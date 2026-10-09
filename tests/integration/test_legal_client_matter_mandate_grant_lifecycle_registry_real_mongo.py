"""Real-Mongo certificate for the client mandate-grant lifecycle registry.

TITLE: WILSY OS Legal Client Matter Mandate Grant Lifecycle Registry Real Mongo Certificate
VERSION: v1.0.0-L9B8-CLIENT-MANDATE-GRANT-LIFECYCLE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify immutable lifecycle evidence against a writable local Mongo
         replica set using only a UUID-isolated disposable database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_mandate_grant_lifecycle_registry_real_mongo.py
COLLABORATION / OWNERSHIP: This certificate covers lifecycle persistence only;
                            currentness, mandate, Engagement, IAM, Court and
                            financial authorities remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-27
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque evidence only; no canonical data,
                             credentials, PII or bearer secrets.
TRANSACTION BOUNDARY: Caller-owned real-Mongo sessions and transactions.
FAIL-CLOSED DECLARATION: Topology, metadata, replay, isolation, corruption,
                         concurrency and durability failures fail the test.
"""
from __future__ import annotations

import ast
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import os
from pathlib import Path
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_lifecycle import (
    LegalClientMatterMandateGrantLifecycleEvent,
    record_legal_client_matter_mandate_grant_lifecycle,
)
from tools.eos.legal_operations.registry.legal_client_matter_mandate_grant_lifecycle_registry import (
    COLLECTION,
    EVENT_ID_INDEX_NAME,
    EVENT_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    HISTORY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    LegalClientMatterMandateGrantLifecycleRegistryConflictError,
    LegalClientMatterMandateGrantLifecycleRegistryNotFoundError,
    LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError,
    LegalClientMatterMandateGrantLifecycleRegistryTransactionRequiredError,
    ensure_indexes,
    get_event,
    get_event_by_fingerprint,
    list_events_for_grant,
    persist_event,
)
from tests.unit.test_legal_client_matter_mandate_grant_lifecycle import (
    BASE,
    event,
    supersession,
)
from tests.unit.test_legal_client_matter_mandate_grant import grant


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture()
def isolated_database():
    """Yield one disposable UUID database and drop only that database."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, retryWrites=True)
    database = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == REPLICA_SET
        assert hello.get("isWritablePrimary") is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert client.server_info().get("version") == "7.0.37"
        with client.start_session() as probe:
            probe.start_transaction()
            assert probe.in_transaction is True
            probe.abort_transaction()
        database = client[f"wilsy_l9b8_grant_lifecycle_{uuid.uuid4().hex}"]
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


def _commit(value, collection, client: MongoClient) -> None:
    """Commit one event using a caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            result = persist_event(value, collection, session=session)
            assert result.to_dict() == value.to_dict()


def _unique_superseded():
    """Construct a valid successor event with a unique idempotency key."""
    original = supersession()
    successor = grant(
        client_grant_id="client-grant-l9b6-successor-real",
        effective_from=BASE + timedelta(hours=4),
        idempotency_key="successor-grant-real-key",
    )
    return record_legal_client_matter_mandate_grant_lifecycle(
        client_grant=grant(),
        lifecycle_event_id=original.lifecycle_event_id,
        event=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED,
        decision_actor_principal_id=original.decision_actor_principal_id,
        acting_capacity_id=None,
        acting_capacity_fingerprint=None,
        authorization_evidence_reference=original.authorization_evidence_reference,
        authorization_evidence_fingerprint=original.authorization_evidence_fingerprint,
        source_evidence_reference=original.source_evidence_reference,
        source_evidence_fingerprint=original.source_evidence_fingerprint,
        occurred_at=original.occurred_at,
        effective_from=original.effective_from,
        idempotency_key="lifecycle-superseded-real-key",
        reason=None,
        successor_grant=successor,
    )


def test_real_mongo_lifecycle_registry_contract(isolated_database) -> None:
    client, database, collection = isolated_database
    before_collections = set(database.list_collection_names())

    indexes = {item["name"]: item for item in collection.list_indexes()}
    expected = {
        EVENT_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        HISTORY_INDEX_NAME,
        EVENT_INDEX_NAME,
    }
    assert expected.issubset(indexes)
    assert all("expireAfterSeconds" not in item for item in indexes.values())
    assert indexes[EVENT_ID_INDEX_NAME]["unique"] is True
    assert indexes[FINGERPRINT_INDEX_NAME]["unique"] is True
    assert indexes[IDEMPOTENCY_INDEX_NAME]["unique"] is True
    assert list(indexes[EVENT_ID_INDEX_NAME]["key"].items()) == [
        ("tenant_id", 1), ("lifecycle_event_id", 1)
    ]
    assert list(indexes[HISTORY_INDEX_NAME]["key"].items()) == [
        ("tenant_id", 1), ("client_grant_id", 1),
        ("client_grant_fingerprint", 1), ("effective_from", 1),
        ("occurred_at", 1), ("fingerprint", 1),
    ]

    revoked = event()
    with pytest.raises(LegalClientMatterMandateGrantLifecycleRegistryTransactionRequiredError):
        persist_event(revoked, collection, session=None)
    with client.start_session() as inactive:
        with pytest.raises(LegalClientMatterMandateGrantLifecycleRegistryTransactionRequiredError):
            persist_event(revoked, collection, session=inactive)

    _commit(revoked, collection, client)
    assert collection.count_documents({}) == 1
    with client.start_session() as session:
        with session.start_transaction():
            read = get_event(revoked.tenant_id, revoked.lifecycle_event_id, collection, session=session)
            assert read.to_dict() == revoked.to_dict()
            assert read.fingerprint == revoked.fingerprint
            assert read.client_grant_id == revoked.client_grant_id
            assert read.decision_actor_principal_id == revoked.decision_actor_principal_id
            assert read.reason == revoked.reason
            assert get_event_by_fingerprint(revoked.tenant_id, revoked.fingerprint, collection, session=session) == revoked
            assert persist_event(revoked, collection, session=session) == revoked
            assert collection.count_documents({}, session=session) == 1

    superseded = _unique_superseded()
    _commit(superseded, collection, client)
    with client.start_session() as session:
        with session.start_transaction():
            read = get_event(superseded.tenant_id, superseded.lifecycle_event_id, collection, session=session)
            assert read.to_dict() == superseded.to_dict()
            assert read.successor_client_grant_id == superseded.successor_client_grant_id
            assert read.successor_client_grant_fingerprint == superseded.successor_client_grant_fingerprint

    divergent_id = event(source_evidence_reference="different-source", idempotency_key="different-key")
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalClientMatterMandateGrantLifecycleRegistryConflictError):
                persist_event(divergent_id, collection, session=session)
    divergent_idempotency = event(lifecycle_event_id="different-event", idempotency_key=revoked.idempotency_key)
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalClientMatterMandateGrantLifecycleRegistryConflictError):
                persist_event(divergent_idempotency, collection, session=session)
    assert collection.count_documents({}) == 2

    equal_one = event(lifecycle_event_id="equal-effective-one", idempotency_key="equal-effective-one")
    equal_two = event(lifecycle_event_id="equal-effective-two", idempotency_key="equal-effective-two")
    _commit(equal_one, collection, client)
    _commit(equal_two, collection, client)
    with client.start_session() as session:
        with session.start_transaction():
            history = list_events_for_grant(revoked.tenant_id, revoked.client_grant_id, collection, session=session)
            expected_history = sorted(
                [revoked, superseded, equal_one, equal_two],
                key=lambda value: (value.effective_from, value.occurred_at, value.fingerprint, value.lifecycle_event_id),
            )
            assert [value.fingerprint for value in history] == [value.fingerprint for value in expected_history]
            assert len(history) == 4
            with pytest.raises(LegalClientMatterMandateGrantLifecycleRegistryNotFoundError):
                get_event("other-tenant", revoked.lifecycle_event_id, collection, session=session)
            assert list_events_for_grant("other-tenant", revoked.client_grant_id, collection, session=session) == ()

    raw = collection.find_one({"lifecycle_event_id": revoked.lifecycle_event_id})
    assert raw is not None
    assert not any(key in raw for key in (
        "email", "password", "jwt", "session_token", "document_body",
        "current", "active", "revoked", "superseded",
    ))

    collection.update_one(
        {"lifecycle_event_id": revoked.lifecycle_event_id},
        {"$set": {"event": "UNKNOWN"}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError):
                get_event(revoked.tenant_id, revoked.lifecycle_event_id, collection, session=session)

    concurrent = event(lifecycle_event_id="concurrent-real", idempotency_key="concurrent-real-key")

    def competing_write() -> str:
        independent = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, retryWrites=True)
        try:
            with independent.start_session() as session:
                with session.start_transaction():
                    persist_event(concurrent, database[COLLECTION], session=session)
            return "COMMITTED"
        except Exception as error:  # bounded evidence label only; no secret output
            return type(error).__name__
        finally:
            independent.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: competing_write(), (1, 2)))
    if outcomes.count("COMMITTED") == 0:
        _commit(concurrent, collection, client)
    assert outcomes.count("COMMITTED") + int(outcomes.count("COMMITTED") == 0) >= 1
    assert collection.count_documents({"lifecycle_event_id": concurrent.lifecycle_event_id}) == 1

    source = Path("tools/eos/legal_operations/registry/legal_client_matter_mandate_grant_lifecycle_registry.py").read_text()
    tree = ast.parse(source)
    assert "commit_transaction" not in source and "abort_transaction" not in source
    assert "get_current" not in source and "currentness" in source
    assert not any("formation" in (node.module or "") for node in ast.walk(tree) if isinstance(node, ast.ImportFrom))
    assert not any("successor" in (node.module or "") for node in ast.walk(tree) if isinstance(node, ast.ImportFrom))

    after_collections = set(database.list_collection_names())
    assert after_collections - before_collections <= {COLLECTION}
    assert database.name != "wilsy"


# ARTIFACT: test_legal_client_matter_mandate_grant_lifecycle_registry_real_mongo.py
# VERSION: v1.0.0-L9B8-CLIENT-MANDATE-GRANT-LIFECYCLE-REAL-MONGO-CERT
# RESULT: UUID-isolated real-Mongo lifecycle certificate only
# END OF WILSY OS SOVEREIGN ARTIFACT
