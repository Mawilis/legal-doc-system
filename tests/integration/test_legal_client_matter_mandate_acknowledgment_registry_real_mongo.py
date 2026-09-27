"""Real-Mongo certificate for the L9B10 acknowledgment registry.

TITLE: WILSY OS Legal Client Matter Mandate Acknowledgment Registry Real Mongo Certificate
VERSION: v1.0.0-L9B10-FIRM-MANDATE-ACKNOWLEDGMENT-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify append-only acknowledgment evidence against a writable local
         Mongo replica set using only a UUID-isolated disposable database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_mandate_acknowledgment_registry_real_mongo.py
COLLABORATION / OWNERSHIP: This certificate covers persistence, replay,
                            tenant isolation and strict readback only. Grant
                            currentness, IAM, mandate, Engagement, Court and
                            financial authorities remain excluded.
CERTIFICATION / UPDATE DATE: 2026-09-27
SECURITY / PRIVACY POSTURE: Synthetic opaque evidence only; no canonical
                             database, credentials, PII or bearer secrets.
TRANSACTION BOUNDARY: Every registry operation uses a caller-owned session;
                      the registry never controls transaction lifecycle.
FAIL-CLOSED DECLARATION: Topology, index, durability, collision, corruption,
                         concurrency and isolation failures fail the certificate.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import os
from typing import Any
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    ACKNOWLEDGMENT_FIELDS,
    LegalClientMatterMandateAcknowledgment,
)
from tools.eos.legal_operations.registry.legal_client_matter_mandate_acknowledgment_registry import (
    ACKNOWLEDGMENT_ID_INDEX_NAME,
    COLLECTION,
    DECISION_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    HISTORY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    LegalClientMatterMandateAcknowledgmentRegistryConflictError,
    LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError,
    LegalClientMatterMandateAcknowledgmentRegistryRetryRequiredError,
    ensure_indexes,
    get_acknowledgment,
    get_acknowledgment_by_fingerprint,
    list_acknowledgments_for_grant,
    persist_acknowledgment,
)
from tests.unit.test_legal_client_matter_mandate_grant import (
    BASE,
    capacity,
    grant,
    matter,
    party,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture()
def isolated_database():
    """Yield one disposable database and drop only that database afterward."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, retryWrites=True)
    database = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == REPLICA_SET
        assert hello.get("isWritablePrimary") is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert client.server_info().get("version") == "7.0.37"
        database = client[f"wilsy_l9b10_ack_registry_{uuid.uuid4().hex}"]
        collection = database[COLLECTION]
        ensure_indexes(collection)
        yield client, database, collection
    except PyMongoError as error:
        pytest.fail(f"real Mongo prerequisite/certificate failure: {type(error).__name__}")
    finally:
        try:
            if database is not None:
                client.drop_database(database.name)
        finally:
            client.close()


def acknowledgment(
    *,
    decision: str = "ACKNOWLEDGED",
    acknowledgment_id: str = "ack-real-l9b10-1",
    idempotency_key: str = "ack-real-idempotency-l9b10-1",
    effective_offset: int = 0,
    client_grant: Any | None = None,
) -> LegalClientMatterMandateAcknowledgment:
    """Build synthetic exact-grant-bound evidence without PII or secrets."""
    occurred = BASE + timedelta(minutes=effective_offset)
    return LegalClientMatterMandateAcknowledgment.from_client_grant(
        client_grant=client_grant or grant(),
        acknowledgment_id=acknowledgment_id,
        decision=decision,
        decision_actor_principal_id="principal-firm-real-l9b10",
        authorization_evidence_reference="iam-ack-real:l9b10",
        authorization_evidence_fingerprint="d" * 128,
        source_evidence_reference="firm-decision-real:l9b10",
        source_evidence_fingerprint="e" * 128,
        occurred_at=occurred,
        effective_from=occurred,
        idempotency_key=idempotency_key,
    )


def _commit(value: LegalClientMatterMandateAcknowledgment, collection: Any, client: MongoClient) -> None:
    """Persist one value under a fresh caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            assert persist_acknowledgment(value, collection, session=session) == value


def test_real_mongo_acknowledgment_registry_contract(isolated_database) -> None:
    client, database, collection = isolated_database
    indexes = {item["name"]: item for item in collection.list_indexes()}
    assert set(indexes) == {
        "_id_",
        ACKNOWLEDGMENT_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        HISTORY_INDEX_NAME,
        DECISION_INDEX_NAME,
    }
    assert all("expireAfterSeconds" not in item for item in indexes.values())
    assert indexes[ACKNOWLEDGMENT_ID_INDEX_NAME]["unique"] is True
    assert indexes[FINGERPRINT_INDEX_NAME]["unique"] is True
    assert indexes[IDEMPOTENCY_INDEX_NAME]["unique"] is True
    assert list(indexes[ACKNOWLEDGMENT_ID_INDEX_NAME]["key"].items()) == [
        ("tenant_id", 1),
        ("acknowledgment_id", 1),
    ]
    assert list(indexes[FINGERPRINT_INDEX_NAME]["key"].items()) == [
        ("tenant_id", 1),
        ("fingerprint", 1),
    ]
    assert list(indexes[IDEMPOTENCY_INDEX_NAME]["key"].items()) == [
        ("tenant_id", 1),
        ("idempotency_key", 1),
    ]
    assert list(indexes[HISTORY_INDEX_NAME]["key"].items()) == [
        ("tenant_id", 1),
        ("client_grant_id", 1),
        ("client_grant_fingerprint", 1),
        ("effective_from", 1),
        ("occurred_at", 1),
        ("fingerprint", 1),
    ]
    assert list(indexes[DECISION_INDEX_NAME]["key"].items()) == [
        ("tenant_id", 1),
        ("client_grant_id", 1),
        ("client_grant_fingerprint", 1),
        ("effective_from", -1),
        ("decision", 1),
    ]

    with client.start_session() as session:
        with pytest.raises(Exception):
            persist_acknowledgment(acknowledgment(), collection, session=session)

    values = (
        acknowledgment(decision="ACKNOWLEDGED"),
        acknowledgment(decision="DECLINED", acknowledgment_id="ack-real-l9b10-2", idempotency_key="ack-real-idempotency-l9b10-2", effective_offset=1),
        acknowledgment(decision="REQUIRES_REVIEW", acknowledgment_id="ack-real-l9b10-3", idempotency_key="ack-real-idempotency-l9b10-3", effective_offset=2),
    )
    for value in values:
        _commit(value, collection, client)

    with client.start_session() as session:
        with session.start_transaction():
            for value in values:
                assert get_acknowledgment(value.tenant_id, value.acknowledgment_id, collection, session=session) == value
                assert get_acknowledgment_by_fingerprint(value.tenant_id, value.fingerprint, collection, session=session) == value
                assert persist_acknowledgment(value, collection, session=session) == value
            history = list_acknowledgments_for_grant(values[0].tenant_id, values[0].client_grant_id, collection, session=session)
            assert [str(item.decision) for item in history] == ["ACKNOWLEDGED", "DECLINED", "REQUIRES_REVIEW"]
            assert [item.acknowledgment_id for item in history] == [item.acknowledgment_id for item in values]

    assert collection.count_documents({}) == 3
    assert database.name != "wilsy"


def test_real_mongo_tenant_isolation_and_divergent_collisions(isolated_database) -> None:
    client, _, collection = isolated_database
    value = acknowledgment()
    _commit(value, collection, client)
    other_matter = matter(tenant_id="tenant-real-other", matter_id="matter-real-other")
    other_party = party(source_matter=other_matter, party_id="party-real-other")
    other_capacity = capacity(source_matter=other_matter, source_party=other_party)
    other_grant = grant(case_matter=other_matter, party=other_party, acting_capacity=other_capacity)
    other = acknowledgment(client_grant=other_grant, acknowledgment_id=value.acknowledgment_id, idempotency_key=value.idempotency_key)
    _commit(other, collection, client)

    with client.start_session() as session:
        with session.start_transaction():
            assert get_acknowledgment(value.tenant_id, value.acknowledgment_id, collection, session=session) == value
            assert get_acknowledgment(other.tenant_id, other.acknowledgment_id, collection, session=session) == other
            with pytest.raises(LegalClientMatterMandateAcknowledgmentRegistryConflictError):
                persist_acknowledgment(acknowledgment(decision="DECLINED"), collection, session=session)
            with pytest.raises(LegalClientMatterMandateAcknowledgmentRegistryConflictError):
                persist_acknowledgment(acknowledgment(acknowledgment_id="ack-real-other", idempotency_key=value.idempotency_key), collection, session=session)
    assert collection.count_documents({}) == 2


def test_real_mongo_corruption_and_raw_bson_audit(isolated_database) -> None:
    client, database, collection = isolated_database
    value = acknowledgment()
    _commit(value, collection, client)
    collection.update_one(
        {"tenant_id": value.tenant_id, "acknowledgment_id": value.acknowledgment_id},
        {"$set": {"decision": "CORRUPTED"}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError):
                get_acknowledgment(value.tenant_id, value.acknowledgment_id, collection, session=session)
    raw = collection.find_one({"tenant_id": value.tenant_id, "acknowledgment_id": value.acknowledgment_id})
    assert raw is not None
    persisted = set(raw) - {"_id"}
    assert persisted == set(ACKNOWLEDGMENT_FIELDS)
    assert not persisted.intersection({"email", "password", "token", "jwt", "current", "status"})
    assert database.name != "wilsy"


def test_real_mongo_concurrent_same_identity_has_one_semantic_row(isolated_database) -> None:
    client, _, collection = isolated_database
    value = acknowledgment()

    def worker() -> str:
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    result = persist_acknowledgment(value, collection, session=session)
                    return "REPLAY_OR_CREATED" if result == value else "UNEXPECTED"
        except LegalClientMatterMandateAcknowledgmentRegistryRetryRequiredError:
            return "RETRY_REQUIRED"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: worker(), range(2)))
    assert set(outcomes).issubset({"REPLAY_OR_CREATED", "RETRY_REQUIRED"})
    assert collection.count_documents({}) == 1


# ARTIFACT: test_legal_client_matter_mandate_acknowledgment_registry_real_mongo.py
# VERSION: v1.0.0-L9B10-FIRM-MANDATE-ACKNOWLEDGMENT-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable acknowledgment evidence persistence only
# END OF WILSY OS SOVEREIGN ARTIFACT
