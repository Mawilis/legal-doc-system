"""WILSY OS tests for durable tenant-neutral global authentication throttling.

TITLE: Global Principal Authentication Rate Limit Unit Certificate
VERSION: v1.0.0-GLOBAL-PRINCIPAL-AUTH-RATE-LIMIT-TESTS
AUTHORITY: Certifies request-density admission only; grants no authentication authority.
EPITOME: Exercises opaque email/source buckets, atomic counters, bounded budgets,
         source-address validation, UTC windows and startup-only index declarations.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_principal_authentication_rate_limit.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-11-03.
CHANGELOG:
    v1.0.0-GLOBAL-PRINCIPAL-AUTH-RATE-LIMIT-TESTS adds deterministic unit
    coverage for both global rate dimensions, no raw PII persistence,
    rejection semantics, source validation and index topology.
COMPLIANCE: Test artifact for POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic email and address only; no raw PII persisted.
TENANT BOUNDARY: Global rate dimensions are tenant-neutral.
AUTHORITY BOUNDARY: Tests throttling only; no credential or session authority.
FINANCIAL AUTHORITY BOUNDARY: No financial authority; Kennel EOS remains exclusive.
"""

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.auth.principal_authentication_rate_limit import (
    PrincipalAuthenticationRateLimited,
    PrincipalAuthenticationRateLimit,
    PrincipalAuthenticationRateLimitUnavailable,
)


class RateLimitCollection:
    """Minimal atomic collection double for deterministic fixed-window tests."""

    def __init__(self):
        self.documents = {}
        self.indexes = []

    def create_index(self, keys, **options):
        """Record the exact index declaration."""
        self.indexes.append((keys, options))
        return options.get("name", "test-index")

    def find_one_and_update(
        self,
        query,
        update,
        *,
        upsert=False,
        return_document=None,
    ):
        """Apply one atomic insert-if-absent and increment operation."""
        bucket_id = query["_id"]
        row = self.documents.get(bucket_id)
        if row is None:
            if not upsert:
                return None
            row = dict(update.get("$setOnInsert", {}))
        row["count"] = row.get("count", 0) + update["$inc"]["count"]
        self.documents[bucket_id] = dict(row)
        return dict(row)


def observed_at(minute=5):
    """Return one fixed UTC instant inside the current test window."""
    return datetime(2026, 11, 3, 12, minute, tzinfo=timezone.utc)


def test_global_rate_gate_persists_only_opaque_email_and_source_digests():
    collection = RateLimitCollection()
    gate = PrincipalAuthenticationRateLimit(collection)
    email = "Owner@Example.com"
    source = "203.0.113.25"
    gate.require_allowed(email=email, source_address=source, observed_at=observed_at())
    persisted = repr(collection.documents)
    assert email not in persisted
    assert source not in persisted
    assert len(collection.documents) == 2
    assert {row["scope"] for row in collection.documents.values()} == {"EMAIL", "SOURCE"}
    assert all(len(row["subject_digest"]) == 128 for row in collection.documents.values())


def test_email_budget_rejects_distributed_guessing_against_one_principal():
    gate = PrincipalAuthenticationRateLimit(
        RateLimitCollection(),
        email_max_requests=1,
        source_max_requests=10,
    )
    gate.require_allowed(
        email="owner@example.com",
        source_address="203.0.113.25",
        observed_at=observed_at(),
    )
    with pytest.raises(PrincipalAuthenticationRateLimited, match="RATE_LIMITED"):
        gate.require_allowed(
            email="OWNER@example.com",
            source_address="203.0.113.26",
            observed_at=observed_at(),
        )


def test_source_budget_rejects_one_peer_spraying_multiple_emails():
    gate = PrincipalAuthenticationRateLimit(
        RateLimitCollection(),
        email_max_requests=10,
        source_max_requests=1,
    )
    gate.require_allowed(
        email="first@example.com",
        source_address="203.0.113.25",
        observed_at=observed_at(),
    )
    with pytest.raises(PrincipalAuthenticationRateLimited, match="RATE_LIMITED"):
        gate.require_allowed(
            email="second@example.com",
            source_address="203.0.113.25",
            observed_at=observed_at(),
        )


@pytest.mark.parametrize("source", ["", " 203.0.113.25", "unknown", "203.0.113.999"])
def test_invalid_or_untrusted_source_address_fails_closed(source):
    collection = RateLimitCollection()
    gate = PrincipalAuthenticationRateLimit(collection)
    with pytest.raises(PrincipalAuthenticationRateLimitUnavailable, match="SOURCE_INVALID"):
        gate.require_allowed(
            email="owner@example.com",
            source_address=source,
            observed_at=observed_at(),
        )
    assert collection.documents == {}


def test_rate_window_is_deterministic_and_resets_only_at_next_window():
    gate = PrincipalAuthenticationRateLimit(
        RateLimitCollection(),
        email_max_requests=1,
        source_max_requests=10,
        window=timedelta(minutes=15),
    )
    gate.require_allowed(
        email="owner@example.com",
        source_address="203.0.113.25",
        observed_at=observed_at(5),
    )
    gate.require_allowed(
        email="owner@example.com",
        source_address="203.0.113.25",
        observed_at=observed_at(16),
    )


def test_invalid_observation_time_and_policy_fail_closed():
    gate = PrincipalAuthenticationRateLimit(RateLimitCollection())
    with pytest.raises(PrincipalAuthenticationRateLimitUnavailable, match="TIME_INVALID"):
        gate.require_allowed(
            email="owner@example.com",
            source_address="203.0.113.25",
            observed_at=datetime(2026, 11, 3, 12, 5),
        )
    with pytest.raises(PrincipalAuthenticationRateLimitUnavailable, match="LIMIT_INVALID"):
        PrincipalAuthenticationRateLimit(RateLimitCollection(), email_max_requests=0)


def test_index_contract_uses_unique_bucket_identity_and_expiry_ttl():
    collection = RateLimitCollection()
    gate = PrincipalAuthenticationRateLimit(collection)
    gate.ensure_indexes()
    assert collection.indexes[0][1]["unique"] is True
    assert collection.indexes[0][1]["name"] == "principal_auth_rate_scope_subject_window_unique"
    assert collection.indexes[1][1]["expireAfterSeconds"] == 0
    assert collection.indexes[1][1]["name"] == "principal_auth_rate_expiry_ttl"


# ARTIFACT: test_principal_authentication_rate_limit.py
# VERSION: v1.0.0-GLOBAL-PRINCIPAL-AUTH-RATE-LIMIT-TESTS
# AUTHORITY BOUNDARY: rate-limit behavior certification only
# TENANT POSTURE: tenant-neutral email and source digest dimensions
# FAIL-CLOSED POSTURE: malformed inputs, corrupt persistence and exhausted budgets reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
