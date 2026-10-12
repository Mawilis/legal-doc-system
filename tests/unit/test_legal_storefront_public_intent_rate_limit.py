"""Direct certificate for the Legal Storefront public-intent rate gate.

TITLE: Legal Storefront Public Intent Rate Limit Direct Certificate
VERSION: v1.0.0-L8-9C0-LEGAL-STOREFRONT-PUBLIC-INTENT-RATE-LIMIT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Adversarially certify deterministic pre-tenant rate buckets, opaque
         SHA3-512 subject identity, atomic request counting, stable throttling,
         TTL-only abuse-control retention, corruption rejection and explicit
         absence of tenant, raw-contact or downstream authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_storefront_public_intent_rate_limit.py
COLLABORATION / OWNERSHIP: Certifies L8-9C0 only. L8-9A owns immutable public
                            intent semantics; L8-9B owns durable intent
                            persistence; HTTP request derivation remains a later
                            separately certified owner.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-9C0-LEGAL-STOREFRONT-PUBLIC-INTENT-RATE-LIMIT-CERT
           establishes direct adversarial certification for configuration,
           indexing, deterministic buckets, durable counting, throttling,
           Mongo failures, persisted-state corruption and authority exclusion.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic SHA3-512 request-subject digests only;
                             no live email, IP, credentials or customer data.
TENANT BOUNDARY: Explicitly pre-tenant. tenant_id must not exist in public API,
                 persisted bucket shape or index contract.
AUTHORITY BOUNDARY: Test evidence only; creates no production authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
from typing import Any

import pytest
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError

from tools.eos.legal_operations.service.legal_storefront_public_intent_rate_limit import (
    COLLECTION,
    DEFAULT_MAX_REQUESTS,
    DEFAULT_NAMESPACE,
    DEFAULT_WINDOW,
    INDEX_LOOKUP,
    INDEX_TTL,
    LegalStorefrontPublicIntentRateLimit,
    LegalStorefrontPublicIntentRateLimitDependencyError,
    LegalStorefrontPublicIntentRateLimitError,
    LegalStorefrontPublicIntentRateLimitedError,
    ensure_indexes,
)


BASE = datetime(2026, 10, 12, 12, 0, 0, tzinfo=timezone.utc)
DIGEST = hashlib.sha3_512(b"synthetic-public-subject").hexdigest()


class _Collection:
    def __init__(self) -> None:
        self.indexes: list[
            tuple[list[tuple[str, int]], str, bool, int | None]
        ] = []
        self.rows: dict[str, dict[str, object]] = {}
        self.fail_index = False
        self.fail_write = False
        self.override_row: dict[str, object] | None = None

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        name: str,
        unique: bool = False,
        expireAfterSeconds: int | None = None,
    ) -> str:
        if self.fail_index:
            raise PyMongoError("synthetic-index-failure")
        self.indexes.append(
            (keys, name, unique, expireAfterSeconds)
        )
        return name

    def find_one_and_update(
        self,
        query: dict[str, object],
        update: dict[str, object],
        *,
        upsert: bool,
        return_document: object,
    ) -> dict[str, object]:
        assert upsert is True
        assert return_document is ReturnDocument.AFTER

        if self.fail_write:
            raise PyMongoError("synthetic-write-failure")

        bucket_id = str(query["_id"])
        current = deepcopy(self.rows.get(bucket_id, {}))

        if not current:
            set_on_insert = update["$setOnInsert"]
            assert isinstance(set_on_insert, dict)
            current = {
                "_id": bucket_id,
                **deepcopy(set_on_insert),
            }

        increment = update["$inc"]
        assert isinstance(increment, dict)

        current_count = current.get("count", 0)
        increment_count = increment.get("count")

        assert isinstance(current_count, int)
        assert not isinstance(current_count, bool)
        assert isinstance(increment_count, int)
        assert not isinstance(increment_count, bool)

        current["count"] = current_count + increment_count

        self.rows[bucket_id] = deepcopy(current)

        if self.override_row is not None:
            return deepcopy(self.override_row)

        return deepcopy(current)


def test_collection_and_defaults_are_exact() -> None:
    assert COLLECTION == "legal_storefront_public_intent_rate_limits"
    assert DEFAULT_WINDOW == timedelta(minutes=15)
    assert DEFAULT_MAX_REQUESTS == 5
    assert DEFAULT_NAMESPACE == "legal-storefront-public-intent"


def test_indexes_are_exact_and_ttl_is_ephemeral_only() -> None:
    collection = _Collection()

    ensure_indexes(collection)

    assert collection.indexes == [
        (
            [
                ("namespace", 1),
                ("subject_digest", 1),
                ("bucket_start", 1),
            ],
            INDEX_LOOKUP,
            False,
            None,
        ),
        (
            [("expires_at", 1)],
            INDEX_TTL,
            False,
            0,
        ),
    ]

    indexed_fields = {
        field
        for keys, _, _, _ in collection.indexes
        for field, _ in keys
    }
    assert "tenant_id" not in indexed_fields
    assert "contact_email" not in indexed_fields
    assert "ip_address" not in indexed_fields


def test_first_request_is_allowed_and_persisted_opaquely() -> None:
    collection = _Collection()
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE,
    )

    assert len(collection.rows) == 1
    row = next(iter(collection.rows.values()))

    assert row["namespace"] == DEFAULT_NAMESPACE
    assert row["subject_digest"] == DIGEST
    assert row["count"] == 1
    assert row["bucket_start"] == BASE
    assert row["expires_at"] == (
        BASE + DEFAULT_WINDOW + timedelta(minutes=1)
    )

    forbidden = {
        "tenant_id",
        "email",
        "contact_email",
        "ip",
        "ip_address",
        "principal_id",
        "identity_id",
        "intent_id",
    }
    assert forbidden.isdisjoint(row)


def test_same_subject_same_window_uses_one_bucket() -> None:
    collection = _Collection()
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE,
    )
    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE + timedelta(minutes=1),
    )

    assert len(collection.rows) == 1
    row = next(iter(collection.rows.values()))
    assert row["count"] == 2


def test_new_fixed_window_creates_new_bucket() -> None:
    collection = _Collection()
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE,
    )
    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE + timedelta(minutes=15),
    )

    assert len(collection.rows) == 2


def test_exact_limit_is_allowed_and_next_request_is_rejected() -> None:
    collection = _Collection()
    gate = LegalStorefrontPublicIntentRateLimit(
        collection,
        max_requests=3,
    )

    for offset in range(3):
        gate.require_allowed(
            subject_digest=DIGEST,
            observed_at=BASE + timedelta(seconds=offset),
        )

    with pytest.raises(
        LegalStorefrontPublicIntentRateLimitedError,
        match="L8_9C0_RATE_LIMITED",
    ):
        gate.require_allowed(
            subject_digest=DIGEST,
            observed_at=BASE + timedelta(seconds=4),
        )

    row = next(iter(collection.rows.values()))
    assert row["count"] == 4


def test_blocked_attempts_continue_to_increment_durable_counter() -> None:
    collection = _Collection()
    gate = LegalStorefrontPublicIntentRateLimit(
        collection,
        max_requests=1,
    )

    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE,
    )

    for offset in (1, 2):
        with pytest.raises(
            LegalStorefrontPublicIntentRateLimitedError,
        ):
            gate.require_allowed(
                subject_digest=DIGEST,
                observed_at=BASE + timedelta(seconds=offset),
            )

    row = next(iter(collection.rows.values()))
    assert row["count"] == 3


@pytest.mark.parametrize(
    "bad_digest",
    [
        "",
        "A" * 128,
        "0" * 127,
        "z" * 128,
        None,
    ],
)
def test_invalid_subject_digest_rejects_before_persistence(
    bad_digest: object,
) -> None:
    collection = _Collection()
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRateLimitError,
        match="L8_9C0_SUBJECT_DIGEST_INVALID",
    ):
        gate.require_allowed(
            subject_digest=bad_digest,  # type: ignore[arg-type]
            observed_at=BASE,
        )

    assert collection.rows == {}


def test_naive_time_rejects_before_persistence() -> None:
    collection = _Collection()
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRateLimitError,
        match="L8_9C0_TIME_INVALID",
    ):
        gate.require_allowed(
            subject_digest=DIGEST,
            observed_at=BASE.replace(tzinfo=None),
        )

    assert collection.rows == {}


@pytest.mark.parametrize(
    ("window", "max_requests"),
    [
        (timedelta(seconds=59), 5),
        (timedelta(hours=25), 5),
        (DEFAULT_WINDOW, 0),
        (DEFAULT_WINDOW, 101),
        (DEFAULT_WINDOW, True),
    ],
)
def test_invalid_policy_configuration_fails_closed(
    window: timedelta,
    max_requests: object,
) -> None:
    with pytest.raises(
        LegalStorefrontPublicIntentRateLimitError,
    ):
        LegalStorefrontPublicIntentRateLimit(
            _Collection(),
            window=window,
            max_requests=max_requests,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "namespace",
    [
        "",
        " leading",
        "trailing ",
        "contains space",
        "*" * 65,
    ],
)
def test_invalid_namespace_fails_closed(
    namespace: str,
) -> None:
    with pytest.raises(
        LegalStorefrontPublicIntentRateLimitError,
        match="L8_9C0_NAMESPACE_INVALID",
    ):
        LegalStorefrontPublicIntentRateLimit(
            _Collection(),
            namespace=namespace,
        )


def test_index_failure_maps_to_dependency_error() -> None:
    collection = _Collection()
    collection.fail_index = True

    with pytest.raises(
        LegalStorefrontPublicIntentRateLimitDependencyError,
        match="L8_9C0_INDEX_CREATION_FAILED",
    ):
        ensure_indexes(collection)


def test_write_failure_maps_to_dependency_error() -> None:
    collection = _Collection()
    collection.fail_write = True
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRateLimitDependencyError,
        match="L8_9C0_WRITE_FAILED",
    ):
        gate.require_allowed(
            subject_digest=DIGEST,
            observed_at=BASE,
        )


def test_persisted_namespace_mismatch_rejects() -> None:
    collection = _Collection()
    collection.override_row = {
        "_id": "synthetic",
        "namespace": "other",
        "subject_digest": DIGEST,
        "bucket_start": BASE,
        "expires_at": BASE + DEFAULT_WINDOW,
        "count": 1,
    }
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRateLimitDependencyError,
        match="L8_9C0_STATE_MISMATCH",
    ):
        gate.require_allowed(
            subject_digest=DIGEST,
            observed_at=BASE,
        )


def test_persisted_digest_mismatch_rejects() -> None:
    collection = _Collection()
    collection.override_row = {
        "_id": "synthetic",
        "namespace": DEFAULT_NAMESPACE,
        "subject_digest": "0" * 128,
        "bucket_start": BASE,
        "expires_at": BASE + DEFAULT_WINDOW,
        "count": 1,
    }
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRateLimitDependencyError,
        match="L8_9C0_STATE_MISMATCH",
    ):
        gate.require_allowed(
            subject_digest=DIGEST,
            observed_at=BASE,
        )


def test_persisted_bucket_start_mismatch_rejects() -> None:
    collection = _Collection()
    collection.override_row = {
        "_id": "synthetic",
        "namespace": DEFAULT_NAMESPACE,
        "subject_digest": DIGEST,
        "bucket_start": BASE + timedelta(minutes=15),
        "expires_at": BASE + timedelta(minutes=31),
        "count": 1,
    }
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRateLimitDependencyError,
        match="L8_9C0_STATE_MISMATCH",
    ):
        gate.require_allowed(
            subject_digest=DIGEST,
            observed_at=BASE,
        )


@pytest.mark.parametrize(
    "count",
    [
        None,
        0,
        -1,
        True,
        "1",
    ],
)
def test_invalid_persisted_count_rejects(
    count: object,
) -> None:
    collection = _Collection()
    collection.override_row = {
        "_id": "synthetic",
        "namespace": DEFAULT_NAMESPACE,
        "subject_digest": DIGEST,
        "bucket_start": BASE,
        "expires_at": BASE + DEFAULT_WINDOW,
        "count": count,
    }
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRateLimitDependencyError,
        match="L8_9C0_STATE_INVALID",
    ):
        gate.require_allowed(
            subject_digest=DIGEST,
            observed_at=BASE,
        )


def test_bson_naive_utc_bucket_start_is_accepted() -> None:
    collection = _Collection()
    collection.override_row = {
        "_id": "synthetic",
        "namespace": DEFAULT_NAMESPACE,
        "subject_digest": DIGEST,
        "bucket_start": BASE.replace(tzinfo=None),
        "expires_at": BASE + DEFAULT_WINDOW,
        "count": 1,
    }
    gate = LegalStorefrontPublicIntentRateLimit(collection)

    gate.require_allowed(
        subject_digest=DIGEST,
        observed_at=BASE,
    )


def test_public_api_exposes_only_digest_and_time() -> None:
    signature = inspect.signature(
        LegalStorefrontPublicIntentRateLimit.require_allowed
    )
    assert set(signature.parameters) == {
        "self",
        "subject_digest",
        "observed_at",
    }

    forbidden = {
        "tenant_id",
        "email",
        "contact_email",
        "ip",
        "ip_address",
        "principal_id",
        "identity_id",
        "intent_id",
        "plan",
        "subscription_id",
        "entitlement_id",
    }
    assert forbidden.isdisjoint(signature.parameters)


def test_public_method_surface_has_no_admission_or_identity_authority() -> None:
    public_methods = {
        name
        for name, member in inspect.getmembers(
            LegalStorefrontPublicIntentRateLimit,
            predicate=inspect.isfunction,
        )
        if not name.startswith("_")
    }

    assert public_methods == {
        "ensure_indexes",
        "require_allowed",
    }


# ARTIFACT: test_legal_storefront_public_intent_rate_limit.py
# VERSION: v1.0.0-L8-9C0-LEGAL-STOREFRONT-PUBLIC-INTENT-RATE-LIMIT-CERT
# AUTHORITY BOUNDARY: direct rate-gate certificate only; no production authority
# TENANT POSTURE: pre-tenant; tenant_id is absent from public capability surface
# RETENTION POSTURE: TTL certifies ephemeral rate-bucket cleanup only
# PRIVACY POSTURE: synthetic SHA3-512 subject digests only; no raw email/IP
# FAIL-CLOSED POSTURE: malformed input/configuration, Mongo failure and state corruption reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
