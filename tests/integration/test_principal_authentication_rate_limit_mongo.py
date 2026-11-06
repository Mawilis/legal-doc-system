"""WILSY OS real-Mongo certification for global principal authentication throttling.

TITLE: Global Principal Authentication Rate Limit Real-Mongo Certificate
VERSION: v1.1.4-GLOBAL-PRINCIPAL-FAILURE-THROTTLE-MONGO-TESTS
AUTHORITY: Certifies durable rate-counter persistence and atomic increments only.
EPITOME: Verifies dual-dimension admission and concurrent Mongo counter behavior
         against the disposable EOS replica set.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_principal_authentication_rate_limit_mongo.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-11-03.
CHANGELOG:
    v1.1.4-GLOBAL-PRINCIPAL-FAILURE-THROTTLE-MONGO-TESTS asserts the renamed
    failure-only persistence dimensions.
    v1.1.3 corrects the concurrent test's source failure-budget argument.
    v1.1.2 corrects the constrained source-budget argument.
    v1.1.1 aligns the email failure-budget constructor argument.
    v1.1.0-GLOBAL-PRINCIPAL-FAILURE-THROTTLE-MONGO-TESTS verifies failure-only
    accounting, successful-email reset and concurrent atomic failed-attempt
    increments against the disposable replica set.
    v1.0.0 adds the initial real-Mongo fixed-window counter tests.
COMPLIANCE: Test artifact for POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic email and documentation-range IP addresses only.
TENANT BOUNDARY: Rate budgets are global and tenant-neutral.
AUTHORITY BOUNDARY: Request-density certification only; no credentials or sessions.
FINANCIAL AUTHORITY BOUNDARY: No financial authority; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import pytest
from pymongo import MongoClient

from tools.eos.auth.principal_authentication_rate_limit import (
    PrincipalAuthenticationRateLimited,
    PrincipalAuthenticationRateLimit,
)


@pytest.fixture()
def mongo_rate_gate():
    """Provide an isolated real-Mongo rate-limit collection."""
    uri = os.getenv("TEST_GLOBAL_PRINCIPAL_MONGO_URI")
    if not uri:
        pytest.fail("TEST_GLOBAL_PRINCIPAL_MONGO_URI is required")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    hello = client.admin.command("hello")
    if hello.get("setName") != "wilsyGlobalPrincipalCertRS":
        pytest.fail("wrong global-principal certification replica set")
    database = client[f"principal_auth_rate_{uuid.uuid4().hex}"]
    collection = database["principal_authentication_rate_limits"]
    gate = PrincipalAuthenticationRateLimit(collection)
    gate.ensure_indexes()
    try:
        yield client, collection, gate
    finally:
        client.drop_database(database.name)
        client.close()


def test_real_mongo_persists_both_tenant_neutral_rate_dimensions(mongo_rate_gate):
    _client, collection, gate = mongo_rate_gate
    gate.record_failure(
        email="owner@example.com",
        source_address="203.0.113.25",
        observed_at=datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc),
    )
    rows = list(collection.find({}))
    assert len(rows) == 2
    assert {row["scope"] for row in rows} == {"EMAIL_FAILURE", "SOURCE_FAILURE"}
    assert all(len(row["subject_digest"]) == 128 for row in rows)
    assert all("owner@example.com" not in repr(row) for row in rows)
    assert all("203.0.113.25" not in repr(row) for row in rows)


def test_real_mongo_enforces_email_budget_across_multiple_source_addresses(mongo_rate_gate):
    _client, _collection, gate = mongo_rate_gate
    constrained = PrincipalAuthenticationRateLimit(
        _collection,
        email_max_failures=1,
        source_max_failures=20,
    )
    observed = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)
    constrained.record_failure(
        email="owner@example.com",
        source_address="203.0.113.25",
        observed_at=observed,
    )
    with pytest.raises(PrincipalAuthenticationRateLimited):
        constrained.require_allowed(
            email="OWNER@example.com",
            source_address="203.0.113.26",
            observed_at=observed,
        )


def test_real_mongo_concurrent_requests_increment_each_bucket_atomically(mongo_rate_gate):
    _client, collection, _gate = mongo_rate_gate
    gate = PrincipalAuthenticationRateLimit(
        collection,
        email_max_failures=100,
        source_max_failures=100,
    )
    observed = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)

    def attempt(_index):
        gate.record_failure(
            email="concurrent@example.com",
            source_address="203.0.113.50",
            observed_at=observed,
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(attempt, range(16)))

    rows = list(collection.find({}))
    assert len(rows) == 2
    assert {row["count"] for row in rows} == {16}


# ARTIFACT: test_principal_authentication_rate_limit_mongo.py
# VERSION: v1.1.4-GLOBAL-PRINCIPAL-FAILURE-THROTTLE-MONGO-TESTS
# AUTHORITY BOUNDARY: real-Mongo request-density persistence certification only
# TENANT POSTURE: tenant-neutral email/source dimensions
# FAIL-CLOSED POSTURE: exhausted budgets and persistence failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
