"""Isolated real-Mongo certification for G64 workspace and review registries.

Requires TEST_G64_MONGO_URI to point at a disposable replica set created by CI.
Never defaults to application or production database configuration.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.legal_operations.domain.g64_ratification_workspace_evidence import (
    G64RatificationWorkspaceRecord,
    G64RecordState,
    new_pending_decisions,
)
from tools.eos.legal_operations.registry.g64_ratification_review_registry import (
    COLLECTION as REVIEW_COLLECTION,
    G64ReviewRegistryError,
    append_review_event,
    ensure_indexes as ensure_review_indexes,
    list_review_events,
)
from tools.eos.legal_operations.registry.g64_ratification_workspace_registry import (
    COLLECTION as WORKSPACE_COLLECTION,
    G64RegistryCorruptRecordError,
    append_record,
    ensure_indexes as ensure_workspace_indexes,
    read_record,
)

MONGO_URI = os.environ.get("TEST_G64_MONGO_URI", "").strip()
pytestmark = pytest.mark.skipif(not MONGO_URI, reason="TEST_G64_MONGO_URI is required for isolated real-Mongo certification")


@pytest.fixture()
def isolated_database():
    if not MONGO_URI:
        pytest.skip("TEST_G64_MONGO_URI is required")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5_000, connectTimeoutMS=5_000)
    client.admin.command("ping")
    database_name = "g64_workspace_cert_" + uuid.uuid4().hex
    database = client[database_name]
    try:
        yield client, database
    finally:
        client.drop_database(database_name)
        client.close()


def _record() -> G64RatificationWorkspaceRecord:
    return G64RatificationWorkspaceRecord(
        record_id="g64-" + uuid.uuid4().hex + uuid.uuid4().hex[:8],
        institution_id="institution-test-label-unverified",
        ratifier_principal_id="principal-test-attester",
        contract_version="v1.0.0-P47-R95-G62-DRAFT",
        contract_sha3_512_fingerprint="a" * 128,
        created_at=datetime.now(timezone.utc).replace(microsecond=0),
        state=G64RecordState.DRAFT,
        decisions=new_pending_decisions(),
    )


def test_real_mongo_workspace_registry_transaction_and_integrity(isolated_database):
    client, database = isolated_database
    collection = database[WORKSPACE_COLLECTION]
    ensure_workspace_indexes(collection)
    record = _record()
    with client.start_session() as session:
        with session.start_transaction():
            append_record(
                tenant_id="tenant-test-001", record=record,
                collection=collection, session=session,
            )
    with client.start_session() as session:
        with session.start_transaction():
            stored = read_record(
                tenant_id="tenant-test-001", institution_id=record.institution_id,
                record_id=record.record_id, collection=collection, session=session,
            )
            assert stored["payload"]["permits_operational_access"] is False
            assert stored["payload"]["evidence_sha3_512"] == record.evidence_fingerprint()
    collection.update_one(
        {"tenant_id": "tenant-test-001", "institution_id": record.institution_id, "record_id": record.record_id},
        {"$set": {"payload.ratifier_principal_id": "principal-tampered"}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(G64RegistryCorruptRecordError):
                read_record(
                    tenant_id="tenant-test-001", institution_id=record.institution_id,
                    record_id=record.record_id, collection=collection, session=session,
                )


def test_real_mongo_review_registry_transaction_digest_and_separation_evidence(isolated_database):
    client, database = isolated_database
    collection = database[REVIEW_COLLECTION]
    ensure_review_indexes(collection)
    record_id = "g64-" + uuid.uuid4().hex + uuid.uuid4().hex[:8]
    event_id = "verification-" + uuid.uuid4().hex[:32]
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    payload = {
        "event_id": event_id,
        "event_type": "INDEPENDENT_VERIFICATION",
        "tenant_id": "tenant-test-002",
        "institution_id": "institution-test-label-unverified",
        "record_id": record_id,
        "verifier_principal_id": "principal-independent-verifier",
        "outcome": "FAIL",
        "findings": [{"check": "RATIFIER_AUTHORITY", "passed": False}],
        "created_at": now,
        "authority_effect": "NONE",
        "ratification_complete": False,
        "permits_operational_access": False,
    }
    with client.start_session() as session:
        with session.start_transaction():
            append_review_event(
                tenant_id="tenant-test-002", institution_id="institution-test-label-unverified",
                record_id=record_id, event_id=event_id, payload=payload,
                collection=collection, session=session,
            )
    with client.start_session() as session:
        with session.start_transaction():
            rows = list_review_events(
                tenant_id="tenant-test-002", institution_id="institution-test-label-unverified",
                record_id=record_id, collection=collection, session=session,
            )
            assert len(rows) == 1
            assert rows[0]["payload"]["verifier_principal_id"] == "principal-independent-verifier"
            assert rows[0]["payload"]["permits_operational_access"] is False
    collection.update_one(
        {"tenant_id": "tenant-test-002", "institution_id": "institution-test-label-unverified", "record_id": record_id, "event_id": event_id},
        {"$set": {"payload.verifier_principal_id": "principal-tampered"}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(G64ReviewRegistryError, match="G64_REVIEW_PERSISTED_EVENT_INVALID"):
                list_review_events(
                    tenant_id="tenant-test-002", institution_id="institution-test-label-unverified",
                    record_id=record_id, collection=collection, session=session,
                )
