"""WILSY OS tests for failure-only global principal authentication throttling.

TITLE: Global Principal Authentication Failure Throttle Unit Certificate
VERSION: v1.1.1-GLOBAL-PRINCIPAL-FAILURE-THROTTLE-TESTS
AUTHORITY: Certifies failed-attempt admission only; grants no authentication authority.
EPITOME: Exercises non-mutating admission checks, failure-only atomic counters,
         success reset, opaque PII-free buckets, UTC windows and TTL indexes.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_principal_authentication_rate_limit.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-11-03.
CHANGELOG:
    v1.1.1-GLOBAL-PRINCIPAL-FAILURE-THROTTLE-TESTS asserts that successful
    authentication clears the email bucket while retaining the source bucket.
    v1.1.0 verifies successful attempts
    do not consume failure budgets and only a successful email identity resets
    its account bucket while source spraying counters remain.
    v1.0.0-GLOBAL-PRINCIPAL-AUTH-RATE-LIMIT-TESTS covered initial dual buckets.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic email and documentation-range IP only.
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

    def find_one(self, query):
        """Read one exact opaque bucket."""
        row = self.documents.get(query["_id"])
        return dict(row) if row is not None else None

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

    def delete_one(self, query):
        """Delete only the exact bucket supplied by the service."""
        self.documents.pop(query["_id"], None)
        return {"deleted_count": 1}


def observed_at(minute=5):
    """Return one fixed UTC instant inside the current test window."""
    return datetime(2026, 11, 3, 12, minute, tzinfo=timezone.utc)


def fail(gate, email="owner@example.com", source="203.0.113.25", at=None):
    """Record one synthetic failed credential attempt."""
    return gate.record_failure(
        email=email,
        source_address=source,
        observed_at=at or observed_at(),
    )


def allow(gate, email="owner@example.com", source="203.0.113.25", at=None):
    """Check admission without consuming a failure attempt."""
    return gate.require_allowed(
        email=email,
        source_address=source,
        observed_at=at or observed_at(),
    )


def test_admission_check_does_not_count_successful_or_unverified_attempts():
    collection = RateLimitCollection()
    gate = PrincipalAuthenticationRateLimit(collection)
    allow(gate)
    assert collection.documents == {}


def test_failure_buckets_persist_only_opaque_email_and_source_digests():
    collection = RateLimitCollection()
    gate = PrincipalAuthenticationRateLimit(collection)
    email = "Owner@Example.com"
    source = "203.0.113.25"
    assert fail(gate, email=email, source=source) == (1, 1)
    persisted = repr(collection.documents)
    assert email not in persisted
    assert source not in persisted
    assert len(collection.documents) == 2
    assert {row["scope"] for row in collection.documents.values()} == {
        "EMAIL_FAILURE",
        "SOURCE_FAILURE",
    }
    assert all(len(row["subject_digest"]) == 128 for row in collection.documents.values())


def test_email_failure_budget_blocks_distributed_guessing_until_window_expiry():
    gate = PrincipalAuthenticationRateLimit(
        RateLimitCollection(),
        email_max_failures=2,
        source_max_failures=10,
    )
    fail(gate, source="203.0.113.25")
    fail(gate, source="203.0.113.26")
    with pytest.raises(PrincipalAuthenticationRateLimited) as blocked:
        allow(gate, source="203.0.113.27")
    assert 1 <= blocked.value.retry_after_seconds <= 900
    allow(gate, source="203.0.113.27", at=observed_at(16))


def test_source_failure_budget_blocks_password_spraying_across_emails():
    gate = PrincipalAuthenticationRateLimit(
        RateLimitCollection(),
        email_max_failures=10,
        source_max_failures=2,
    )
    fail(gate, email="first@example.com")
    fail(gate, email="second@example.com")
    with pytest.raises(PrincipalAuthenticationRateLimited):
        allow(gate, email="third@example.com")


def test_success_resets_only_the_exact_email_bucket_not_source_spray_history():
    gate = PrincipalAuthenticationRateLimit(
        RateLimitCollection(),
        email_max_failures=1,
        source_max_failures=1,
    )
    fail(gate, source="203.0.113.25")
    gate.record_success(email="OWNER@example.com", observed_at=observed_at())
    allow(gate, source="203.0.113.26")
    with pytest.raises(PrincipalAuthenticationRateLimited):
        allow(gate, email="another@example.com", source="203.0.113.25")


@pytest.mark.parametrize("source", ["", " 203.0.113.25", "unknown", "203.0.113.999"])
def test_invalid_or_untrusted_source_address_fails_closed(source):
    collection = RateLimitCollection()
    gate = PrincipalAuthenticationRateLimit(collection)
    with pytest.raises(PrincipalAuthenticationRateLimitUnavailable, match="SOURCE_INVALID"):
        allow(gate, source=source)
    assert collection.documents == {}


def test_invalid_observation_time_and_policy_fail_closed():
    gate = PrincipalAuthenticationRateLimit(RateLimitCollection())
    with pytest.raises(PrincipalAuthenticationRateLimitUnavailable, match="TIME_INVALID"):
        allow(
            gate,
            at=datetime(2026, 11, 3, 12, 5),
        )
    with pytest.raises(PrincipalAuthenticationRateLimitUnavailable, match="LIMIT_INVALID"):
        PrincipalAuthenticationRateLimit(RateLimitCollection(), email_max_failures=0)


def test_index_contract_uses_unique_bucket_identity_and_expiry_ttl():
    collection = RateLimitCollection()
    gate = PrincipalAuthenticationRateLimit(collection)
    gate.ensure_indexes()
    assert collection.indexes[0][1]["unique"] is True
    assert collection.indexes[0][1]["name"] == "principal_auth_rate_scope_subject_window_unique"
    assert collection.indexes[1][1]["expireAfterSeconds"] == 0
    assert collection.indexes[1][1]["name"] == "principal_auth_rate_expiry_ttl"


# ARTIFACT: test_principal_authentication_rate_limit.py
# VERSION: v1.1.1-GLOBAL-PRINCIPAL-FAILURE-THROTTLE-TESTS
# AUTHORITY BOUNDARY: failure-only throttle certification
# TENANT POSTURE: tenant-neutral email and source digest dimensions
# FAIL-CLOSED POSTURE: malformed inputs, corrupt persistence and exhausted budgets reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
