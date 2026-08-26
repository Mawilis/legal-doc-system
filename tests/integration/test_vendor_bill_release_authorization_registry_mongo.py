"""WILSY OS — VENDOR BILL RELEASE AUTHORIZATION REGISTRY REAL-MONGO CERTIFICATION
Version: v1.0.1-VENDOR-BILL-RELEASE-AUTHORIZATION-REGISTRY-MONGO-CERT
Authority: Wilsy OS Core Governance | Classification: Institutional Artifact — Production Certification
EPITOME: Durable tenant-scoped immutable release evidence certification.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_vendor_bill_release_authorization_registry_mongo.py
PRIMARY CONTRACT: vendor_bill_release_authorization_registry.py
ARCHITECTURE LOCK: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
COLLABORATION: Wilson Khanyezi — Founder / Chief Architect; AI Engineering (Codex)
Date: 2026-08-26 | COMPLIANCE: POPIA §19 | GDPR §32 | SOC2 CC7.2
CHANGELOG: 2026-08-26 — v1.0.1 removed duplicated concurrency from session-read certification.
"""

import hashlib
import json
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from datetime import datetime, timezone

import pytest
from pymongo import MongoClient

from tools.eos.saas.billing.vendor_bill_release_authorization_registry import (
    VendorBillReleaseAuthorizationCreateConflictError,
    VendorBillReleaseAuthorizationCreateOutcome,
    VendorBillReleaseAuthorizationIdempotencyKeyReuseError,
    VendorBillReleaseAuthorizationNotFoundError,
    VendorBillReleaseAuthorizationPersistedRecordInvalidError,
    VendorBillReleaseAuthorizationRegistry,
    VendorBillReleaseAuthorizationRegistryError,
)
from tools.eos.saas.domain.vendor_bill_release_authorization import VendorBillReleaseAuthorization


def make_authorization(**overrides: Any) -> VendorBillReleaseAuthorization:
    """Description: build deterministic valid evidence.

    Collaboration: shared fixture for registry certification.
    Institutional: fixed UTC values keep tests reproducible.
    Returns: valid immutable authorization.
    """
    values: dict[str, Any] = {
        "tenant_id": "tenant-a", "release_authorization_id": "release-a",
        "payable_id": "payable-a", "vendor_bill_revision": 1,
        "approval_effective_result_id": "result-a",
        "approval_effective_result_fingerprint": "a" * 128,
        "authorized_amount_minor": 100, "currency": "ZAR",
        "authorized_by_actor_id": "actor-a", "authorization_basis_reference": "basis-a",
        "authorized_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return VendorBillReleaseAuthorization(**values)


@pytest.fixture()
def collection():
    """Provide an isolated real-Mongo collection, failing closed when unavailable."""
    uri = os.environ.get("TEST_VENDOR_MONGO_URI")
    if not uri:
        pytest.skip("TEST_VENDOR_MONGO_URI is required")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    try:
        client.admin.command("hello")
    except Exception as error:
        client.close()
        pytest.fail(f"MongoDB certification environment unavailable: {error}")
    database = client[f"vendor_release_cert_{uuid.uuid4().hex}"]
    target = database["vendor_bill_release_authorizations"]
    yield target
    client.drop_database(database.name)
    client.close()


def test_indexes_and_create_replay(collection) -> None:
    VendorBillReleaseAuthorizationRegistry.ensure_indexes(collection)
    indexes = {index["name"]: index for index in collection.list_indexes()}
    assert indexes["tenant_release_authorization_identity_unique"]["unique"] is True
    assert list(indexes["tenant_release_authorization_identity_unique"]["key"].items()) == [("tenant_id", 1), ("release_authorization_id", 1)]
    assert indexes["tenant_payable_release_idempotency_unique"]["unique"] is True
    authorization = make_authorization()
    created = VendorBillReleaseAuthorizationRegistry.create(authorization, "key-a", collection)
    replay = VendorBillReleaseAuthorizationRegistry.create(authorization, "key-a", collection)
    assert created.outcome is VendorBillReleaseAuthorizationCreateOutcome.CREATED
    assert replay.outcome is VendorBillReleaseAuthorizationCreateOutcome.IDEMPOTENT_REPLAY
    assert collection.count_documents({}) == 1
    raw = collection.find_one({"tenant_id": "tenant-a"})
    assert raw is not None
    assert re.fullmatch(r"[0-9a-f]{128}", raw["create_fingerprint"])


def test_conflicts_isolation_and_fingerprint(collection) -> None:
    VendorBillReleaseAuthorizationRegistry.ensure_indexes(collection)
    original = make_authorization()
    VendorBillReleaseAuthorizationRegistry.create(original, "key-a", collection)
    with pytest.raises(VendorBillReleaseAuthorizationIdempotencyKeyReuseError):
        VendorBillReleaseAuthorizationRegistry.create(make_authorization(authorized_amount_minor=200), "key-a", collection)
    with pytest.raises(VendorBillReleaseAuthorizationCreateConflictError):
        VendorBillReleaseAuthorizationRegistry.create(make_authorization(payable_id="payable-b", authorization_basis_reference="other"), "key-b", collection)
    body = original.to_persistence_dict()
    expected = hashlib.sha3_512(json.dumps({"authorization": body, "idempotency_key": "key-a"}, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
    assert collection.find_one({"tenant_id": "tenant-a"})["create_fingerprint"] == expected
    assert VendorBillReleaseAuthorizationRegistry.get("tenant-a", "release-a", collection) == original
    with pytest.raises(VendorBillReleaseAuthorizationNotFoundError):
        VendorBillReleaseAuthorizationRegistry.get("tenant-b", "release-a", collection)
    other = make_authorization(tenant_id="tenant-b")
    VendorBillReleaseAuthorizationRegistry.create(other, "key-a", collection)
    assert collection.count_documents({}) == 2


def test_corruption_and_not_found(collection) -> None:
    VendorBillReleaseAuthorizationRegistry.ensure_indexes(collection)
    authorization = make_authorization()
    VendorBillReleaseAuthorizationRegistry.create(authorization, "key-a", collection)
    collection.update_one({"tenant_id": "tenant-a"}, {"$set": {"create_fingerprint": "bad"}})
    with pytest.raises(VendorBillReleaseAuthorizationPersistedRecordInvalidError):
        VendorBillReleaseAuthorizationRegistry.get("tenant-a", "release-a", collection)
    with pytest.raises(VendorBillReleaseAuthorizationPersistedRecordInvalidError):
        VendorBillReleaseAuthorizationRegistry.create(authorization, "key-a", collection)
    with pytest.raises(VendorBillReleaseAuthorizationNotFoundError):
        VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key("tenant-a", "payable-a", "missing", collection)


def test_lookup_validation(collection) -> None:
    with pytest.raises(VendorBillReleaseAuthorizationRegistryError, match="tenant_id is invalid"):
        VendorBillReleaseAuthorizationRegistry.get(" ", "release-a", collection)
    with pytest.raises(VendorBillReleaseAuthorizationRegistryError, match="payable_id is invalid"):
        VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key("tenant-a", "x" * 81, "key", collection)


def test_payable_scoped_idempotency_and_metadata_corruption(collection) -> None:
    """Description: idempotency is payable-scoped and metadata is strict.

    Institutional: corrupted persistence is never normalized into authority.
    """
    VendorBillReleaseAuthorizationRegistry.ensure_indexes(collection)
    VendorBillReleaseAuthorizationRegistry.create(make_authorization(), "shared", collection)
    second = make_authorization(payable_id="payable-b", release_authorization_id="release-b")
    assert VendorBillReleaseAuthorizationRegistry.create(second, "shared", collection).outcome is VendorBillReleaseAuthorizationCreateOutcome.CREATED
    isolated = collection.database["isolated"]["vendor_bill_release_authorizations"]
    VendorBillReleaseAuthorizationRegistry.ensure_indexes(isolated)
    VendorBillReleaseAuthorizationRegistry.create(make_authorization(), "key-a", isolated)
    isolated.update_one({"tenant_id": "tenant-a"}, {"$set": {"create_idempotency_key": " key-a "}})
    with pytest.raises(VendorBillReleaseAuthorizationPersistedRecordInvalidError):
        VendorBillReleaseAuthorizationRegistry.get("tenant-a", "release-a", isolated)


def test_concurrent_exact_create_and_release_conflict(collection) -> None:
    """Description: concurrent writers converge on one durable identity.

    Collaboration: certifies retry and unique-index behavior without execution.
    Institutional: no raw duplicate-key error may escape the registry boundary.
    """
    VendorBillReleaseAuthorizationRegistry.ensure_indexes(collection)
    authorization = make_authorization()
    def exact(_: int) -> str:
        try:
            return VendorBillReleaseAuthorizationRegistry.create(authorization, "race", collection).outcome.value
        except Exception as error:
            return type(error).__name__
    with ThreadPoolExecutor(max_workers=16) as workers:
        outcomes = list(workers.map(exact, range(100)))
    assert outcomes.count("CREATED") == 1
    assert outcomes.count("IDEMPOTENT_REPLAY") == 99
    assert collection.count_documents({}) == 1


def test_caller_owned_transaction_abort_removes_release_authorization(collection) -> None:
    """Description: caller abort prevents a transactional insert becoming durable.

    Collaboration: the test owns session lifecycle; the registry only participates.
    Institutional: aborted release evidence cannot become financial authority.
    """
    VendorBillReleaseAuthorizationRegistry.ensure_indexes(collection)
    authorization = make_authorization()
    client = collection.database.client
    with client.start_session() as session:
        session.start_transaction()
        result = VendorBillReleaseAuthorizationRegistry.create(authorization, "abort-key", collection, session=session)
        assert result.outcome is VendorBillReleaseAuthorizationCreateOutcome.CREATED
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": authorization.tenant_id, "release_authorization_id": authorization.release_authorization_id}) == 0
    with pytest.raises(VendorBillReleaseAuthorizationNotFoundError, match="VENDOR_BILL_RELEASE_AUTHORIZATION_NOT_FOUND"):
        VendorBillReleaseAuthorizationRegistry.get(authorization.tenant_id, authorization.release_authorization_id, collection)


def test_caller_owned_transaction_commit_persists_release_authorization(collection) -> None:
    """Description: caller commit makes a registry insert durable.

    Collaboration: orchestration owns commit while the registry receives the session.
    Institutional: persistence composability does not grant execution authority.
    """
    VendorBillReleaseAuthorizationRegistry.ensure_indexes(collection)
    authorization = make_authorization()
    client = collection.database.client
    with client.start_session() as session:
        session.start_transaction()
        VendorBillReleaseAuthorizationRegistry.create(authorization, "commit-key", collection, session=session)
        session.commit_transaction()
    assert VendorBillReleaseAuthorizationRegistry.get(authorization.tenant_id, authorization.release_authorization_id, collection) == authorization
    assert collection.count_documents({"tenant_id": authorization.tenant_id, "release_authorization_id": authorization.release_authorization_id}) == 1


def test_session_aware_release_authorization_reads(collection) -> None:
    """Description: public reads operate inside a caller-owned session.

    Collaboration: session propagation supports future orchestration snapshots.
    Institutional: reads remain tenant and payable scoped without execution behavior.
    """
    VendorBillReleaseAuthorizationRegistry.ensure_indexes(collection)
    authorization = make_authorization()
    VendorBillReleaseAuthorizationRegistry.create(authorization, "session-key", collection)
    client = collection.database.client
    with client.start_session() as session:
        assert VendorBillReleaseAuthorizationRegistry.get(authorization.tenant_id, authorization.release_authorization_id, collection, session=session) == authorization
        assert VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key(authorization.tenant_id, authorization.payable_id, "session-key", collection, session=session) == authorization

# INSTITUTIONAL CERTIFICATION SEAL
# File: test_vendor_bill_release_authorization_registry_mongo.py
# Version: v1.0.1-VENDOR-BILL-RELEASE-AUTHORIZATION-REGISTRY-MONGO-CERT
# Status: SOVEREIGN REAL-MONGO CERTIFICATION — R2B-02
# Runtime posture: PERSISTENCE ONLY / NO KENNEL EXECUTION
# Real-Mongo certification is environment-dependent and not claimed offline.
