"""Direct certificate for the WILSY OS password-recovery rate gate.

TITLE: WILSY OS Password Recovery Rate Limit Direct Certificate
VERSION: v1.0.0-R10E27-PASSWORD-RECOVERY-RATE-LIMIT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies deterministic namespaced recovery throttling, durable
         counter behavior, fail-closed persistence, and secret-free bucket
         identity without granting recovery or credential authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_recovery_rate_limit.py
COLLABORATION / OWNERSHIP: Exercises password_recovery_rate_limit.py with an
                           in-memory PyMongo-shaped collection only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E27-PASSWORD-RECOVERY-RATE-LIMIT-CERT introduces direct
           evidence for index shape, fixed-window admission, exact limit
           rejection, namespace isolation, deterministic bucket identity,
           validation, state mismatch rejection, and persistence failure.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic SHA3-512 digests only; no raw email,
                            password, recovery token, or production data.
TENANT BOUNDARY: Tests prove bucket identity includes exact tenant and namespace.
AUTHORITY BOUNDARY: Test evidence only; no recovery, password, session, JWT,
                    MFA, delivery, HTTP, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from pymongo.errors import PyMongoError

from tools.eos.saas.auth.password_recovery_rate_limit import (
    DEFAULT_NAMESPACE,
    PasswordRecoveryRateLimit,
)
from tools.eos.saas.auth.password_recovery_request_service import (
    PasswordRecoveryRequestDependencyError,
    PasswordRecoveryRequestRateLimitedError,
)

TENANT = "WILSY-TENANT-RATE-CERT"
DIGEST = hashlib.sha3_512(b"wilsy@example.com").hexdigest()
OBSERVED = datetime(2026, 9, 22, 18, 0, tzinfo=timezone.utc)


class _FakeCollection:
    """Minimal atomic-counter collection with optional fault/corruption injection."""

    def __init__(self) -> None:
        self.rows: dict[str, dict[str, object]] = {}
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, object]]] = []
        self.fail_indexes = False
        self.fail_write = False
        self.corrupt_next: dict[str, object] | None = None

    def create_index(self, keys, **kwargs):
        if self.fail_indexes:
            raise PyMongoError("index failure")
        self.indexes.append((list(keys), dict(kwargs)))
        return kwargs.get("name")

    def find_one_and_update(self, query, update, *, upsert=False, return_document=None):
        del return_document
        if self.fail_write:
            raise PyMongoError("write failure")
        bucket_id = query["_id"]
        row = self.rows.get(bucket_id)
        if row is None:
            if not upsert:
                return None
            row = {"_id": bucket_id}
            row.update(deepcopy(update.get("$setOnInsert", {})))
            self.rows[bucket_id] = row
        increment = update.get("$inc", {}).get("count", 0)
        row["count"] = row.get("count", 0) + increment
        result = deepcopy(row)
        if self.corrupt_next is not None:
            result.update(self.corrupt_next)
            self.corrupt_next = None
        return result


def _gate(
    collection: _FakeCollection,
    *,
    namespace: str = DEFAULT_NAMESPACE,
    max_requests: int = 5,
    window: timedelta = timedelta(minutes=15),
) -> PasswordRecoveryRateLimit:
    return PasswordRecoveryRateLimit(
        collection,
        namespace=namespace,
        max_requests=max_requests,
        window=window,
    )


def test_indexes_cover_namespace_lookup_and_ttl_cleanup() -> None:
    collection = _FakeCollection()
    _gate(collection).ensure_indexes()

    assert len(collection.indexes) == 2
    lookup_keys, lookup_options = collection.indexes[0]
    ttl_keys, ttl_options = collection.indexes[1]
    assert lookup_keys == [
        ("namespace", 1),
        ("tenant_id", 1),
        ("address_digest", 1),
        ("bucket_start", 1),
    ]
    assert lookup_options == {"unique": False, "name": "password_recovery_rate_lookup"}
    assert ttl_keys == [("expires_at", 1)]
    assert ttl_options == {"expireAfterSeconds": 0, "name": "password_recovery_rate_ttl"}


def test_exact_allowance_then_rate_limit_with_durable_blocked_count() -> None:
    collection = _FakeCollection()
    gate = _gate(collection, max_requests=2)

    gate.require_allowed(tenant_id=TENANT, address_digest=DIGEST, observed_at=OBSERVED)
    gate.require_allowed(
        tenant_id=TENANT,
        address_digest=DIGEST,
        observed_at=OBSERVED + timedelta(seconds=30),
    )

    with pytest.raises(PasswordRecoveryRequestRateLimitedError) as captured:
        gate.require_allowed(
            tenant_id=TENANT,
            address_digest=DIGEST,
            observed_at=OBSERVED + timedelta(minutes=1),
        )

    assert captured.value.code == "RECOVERY_REQUEST_RATE_LIMITED"
    assert len(collection.rows) == 1
    row = next(iter(collection.rows.values()))
    assert row["namespace"] == DEFAULT_NAMESPACE
    assert row["tenant_id"] == TENANT
    assert row["address_digest"] == DIGEST
    assert row["count"] == 3


def test_namespace_and_tenant_have_independent_security_budgets() -> None:
    collection = _FakeCollection()
    reset = _gate(collection, namespace="password-reset", max_requests=1)
    verification = _gate(
        collection,
        namespace="recovery-contact-verification",
        max_requests=1,
    )

    reset.require_allowed(tenant_id=TENANT, address_digest=DIGEST, observed_at=OBSERVED)
    verification.require_allowed(
        tenant_id=TENANT,
        address_digest=DIGEST,
        observed_at=OBSERVED,
    )
    _gate(collection, namespace="password-reset", max_requests=1).require_allowed(
        tenant_id="WILSY-TENANT-OTHER",
        address_digest=DIGEST,
        observed_at=OBSERVED,
    )

    assert len(collection.rows) == 3
    assert {row["namespace"] for row in collection.rows.values()} == {
        "password-reset",
        "recovery-contact-verification",
    }
    assert {row["tenant_id"] for row in collection.rows.values()} == {
        TENANT,
        "WILSY-TENANT-OTHER",
    }


def test_new_fixed_window_resets_admission_without_mutating_prior_bucket() -> None:
    collection = _FakeCollection()
    gate = _gate(collection, max_requests=1, window=timedelta(minutes=15))

    gate.require_allowed(tenant_id=TENANT, address_digest=DIGEST, observed_at=OBSERVED)
    gate.require_allowed(
        tenant_id=TENANT,
        address_digest=DIGEST,
        observed_at=OBSERVED + timedelta(minutes=16),
    )

    assert len(collection.rows) == 2
    assert sorted(row["count"] for row in collection.rows.values()) == [1, 1]


@pytest.mark.parametrize(
    ("kwargs", "code"),
    [
        ({"namespace": ""}, "RECOVERY_RATE_NAMESPACE_INVALID"),
        ({"namespace": " bad"}, "RECOVERY_RATE_NAMESPACE_INVALID"),
        ({"namespace": "bad space"}, "RECOVERY_RATE_NAMESPACE_INVALID"),
        ({"max_requests": 0}, "RECOVERY_RATE_LIMIT_INVALID"),
        ({"max_requests": 101}, "RECOVERY_RATE_LIMIT_INVALID"),
        ({"window": timedelta(seconds=59)}, "RECOVERY_RATE_WINDOW_INVALID"),
        ({"window": timedelta(hours=25)}, "RECOVERY_RATE_WINDOW_INVALID"),
    ],
)
def test_policy_configuration_rejects_invalid_values(kwargs, code) -> None:
    with pytest.raises(PasswordRecoveryRequestDependencyError) as captured:
        PasswordRecoveryRateLimit(_FakeCollection(), **kwargs)
    assert captured.value.code == code


@pytest.mark.parametrize(
    ("tenant_id", "digest", "observed_at", "code"),
    [
        ("", DIGEST, OBSERVED, "RECOVERY_RATE_TENANT_INVALID"),
        (" tenant", DIGEST, OBSERVED, "RECOVERY_RATE_TENANT_INVALID"),
        (TENANT, "0" * 127, OBSERVED, "RECOVERY_RATE_DIGEST_INVALID"),
        (TENANT, "G" * 128, OBSERVED, "RECOVERY_RATE_DIGEST_INVALID"),
        (
            TENANT,
            DIGEST,
            datetime(2026, 9, 22, 18, 0),
            "RECOVERY_RATE_TIME_INVALID",
        ),
    ],
)
def test_request_inputs_fail_closed(tenant_id, digest, observed_at, code) -> None:
    with pytest.raises(PasswordRecoveryRequestDependencyError) as captured:
        _gate(_FakeCollection()).require_allowed(
            tenant_id=tenant_id,
            address_digest=digest,
            observed_at=observed_at,
        )
    assert captured.value.code == code


def test_persisted_state_mismatch_fails_closed() -> None:
    collection = _FakeCollection()
    collection.corrupt_next = {"tenant_id": "OTHER-TENANT"}

    with pytest.raises(PasswordRecoveryRequestDependencyError) as captured:
        _gate(collection).require_allowed(
            tenant_id=TENANT,
            address_digest=DIGEST,
            observed_at=OBSERVED,
        )

    assert captured.value.code == "RECOVERY_RATE_STATE_MISMATCH"


def test_invalid_counter_state_fails_closed() -> None:
    collection = _FakeCollection()
    collection.corrupt_next = {"count": True}

    with pytest.raises(PasswordRecoveryRequestDependencyError) as captured:
        _gate(collection).require_allowed(
            tenant_id=TENANT,
            address_digest=DIGEST,
            observed_at=OBSERVED,
        )

    assert captured.value.code == "RECOVERY_RATE_STATE_INVALID"


def test_index_and_write_failures_do_not_bypass_security_gate() -> None:
    index_collection = _FakeCollection()
    index_collection.fail_indexes = True
    with pytest.raises(PasswordRecoveryRequestDependencyError) as index_error:
        _gate(index_collection).ensure_indexes()
    assert index_error.value.code == "RECOVERY_RATE_INDEX_CREATION_FAILED"

    write_collection = _FakeCollection()
    write_collection.fail_write = True
    with pytest.raises(PasswordRecoveryRequestDependencyError) as write_error:
        _gate(write_collection).require_allowed(
            tenant_id=TENANT,
            address_digest=DIGEST,
            observed_at=OBSERVED,
        )
    assert write_error.value.code == "RECOVERY_RATE_WRITE_FAILED"


def test_bucket_identity_is_secret_free_and_deterministic_for_same_window() -> None:
    collection = _FakeCollection()
    gate = _gate(collection, max_requests=10)

    gate.require_allowed(tenant_id=TENANT, address_digest=DIGEST, observed_at=OBSERVED)
    gate.require_allowed(
        tenant_id=TENANT,
        address_digest=DIGEST,
        observed_at=OBSERVED + timedelta(minutes=5),
    )

    assert len(collection.rows) == 1
    bucket_id = next(iter(collection.rows))
    assert len(bucket_id) == 128
    assert bucket_id == bucket_id.lower()
    assert TENANT not in bucket_id
    assert DIGEST not in bucket_id
    assert next(iter(collection.rows.values()))["count"] == 2


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_password_recovery_rate_limit.py
# VERSION: v1.0.0-R10E27-PASSWORD-RECOVERY-RATE-LIMIT-CERT
# AUTHORITY BOUNDARY: deterministic direct test evidence only
# TENANT POSTURE: namespace + exact tenant/address-digest isolation certified
# FAIL-CLOSED POSTURE: invalid policy, state, and persistence failure reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
