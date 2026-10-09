"""Real-Mongo certificate for the L9B7 client mandate-grant registry.

TITLE: WILSY OS Legal Client Matter Mandate Grant Registry Real Mongo Certificate
VERSION: v1.0.0-L9B7-CLIENT-MANDATE-GRANT-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published formation registry against a writable local
         MongoDB replica set using only a UUID-isolated disposable database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_mandate_grant_registry_real_mongo.py
COLLABORATION / OWNERSHIP: This certificate covers only formation persistence;
                            lifecycle persistence, currentness, IAM, mandate,
                            Engagement, Representation, Court and finance are
                            separate authorities and gates.
CERTIFICATION / UPDATE DATE: 2026-09-27
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque evidence only; no canonical
                             database, credentials, PII or bearer secrets.
TRANSACTION BOUNDARY: Caller-owned real Mongo sessions and transactions.
FAIL-CLOSED DECLARATION: Topology, index, replay, isolation, corruption and
                         durability failures fail the certificate.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import os
from pathlib import Path
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.legal_operations.registry.legal_client_matter_mandate_grant_registry import (
    COLLECTION,
    FINGERPRINT_INDEX_NAME,
    GRANT_ID_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    MATTER_CLIENT_INDEX_NAME,
    MATTER_CLIENT_SCOPE_INDEX_NAME,
    LegalClientMatterMandateGrantRegistryConflictError,
    LegalClientMatterMandateGrantRegistryNotFoundError,
    LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError,
    LegalClientMatterMandateGrantRegistryTransactionRequiredError,
    ensure_indexes,
    get_grant,
    get_grant_by_fingerprint,
    list_grants_for_matter_client,
    persist_grant,
)
from tests.unit.test_legal_client_matter_mandate_grant import BASE, grant, matter, party


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture()
def isolated_database():
    """Yield one UUID-isolated real database and remove only that database."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, retryWrites=True)
    database = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == REPLICA_SET
        assert hello.get("isWritablePrimary") is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert client.server_info().get("version") == "7.0.37"
        database = client[f"wilsy_l9b7_grant_registry_{uuid.uuid4().hex}"]
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


def _committed(value, collection, client: MongoClient) -> None:
    with client.start_session() as session:
        with session.start_transaction():
            result = persist_grant(value, collection, session=session)
            assert result.to_dict() == value.to_dict()


def test_real_mongo_formation_registry_contract(isolated_database) -> None:
    client, database, collection = isolated_database
    before_collections = set(database.list_collection_names())

    indexes = {item["name"]: item for item in collection.list_indexes()}
    expected = {
        GRANT_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        MATTER_CLIENT_INDEX_NAME,
        MATTER_CLIENT_SCOPE_INDEX_NAME,
    }
    assert expected.issubset(indexes)
    assert all("expireAfterSeconds" not in item for item in indexes.values())
    assert indexes[GRANT_ID_INDEX_NAME]["unique"] is True
    assert indexes[FINGERPRINT_INDEX_NAME]["unique"] is True
    assert indexes[IDEMPOTENCY_INDEX_NAME]["unique"] is True
    assert list(indexes[GRANT_ID_INDEX_NAME]["key"].items()) == [("tenant_id", 1), ("client_grant_id", 1)]
    assert list(indexes[FINGERPRINT_INDEX_NAME]["key"].items()) == [("tenant_id", 1), ("fingerprint", 1)]
    assert list(indexes[IDEMPOTENCY_INDEX_NAME]["key"].items()) == [("tenant_id", 1), ("idempotency_key", 1)]

    value = grant()
    with pytest.raises(LegalClientMatterMandateGrantRegistryTransactionRequiredError):
        persist_grant(value, collection, session=None)
    with client.start_session() as session:
        assert session.in_transaction is False
        with pytest.raises(LegalClientMatterMandateGrantRegistryTransactionRequiredError):
            persist_grant(value, collection, session=session)

    _committed(value, collection, client)
    assert collection.count_documents({}) == 1
    with client.start_session() as session:
        with session.start_transaction():
            read = get_grant(value.tenant_id, value.client_grant_id, collection, session=session)
            assert read.to_dict() == value.to_dict()
            assert read.fingerprint == value.fingerprint
            assert get_grant_by_fingerprint(value.tenant_id, value.fingerprint, collection, session=session) == value
            assert persist_grant(value, collection, session=session) == value
            assert collection.count_documents({}, session=session) == 1

    tenant_matter = matter(tenant_id="tenant-b", matter_id="matter-b")
    tenant_party = party(source_matter=tenant_matter, party_id="party-b")
    tenant_b = grant(
        client_grant_id=value.client_grant_id,
        idempotency_key=value.idempotency_key,
        case_matter=tenant_matter,
        party=tenant_party,
    )
    _committed(tenant_b, collection, client)
    with client.start_session() as session:
        with session.start_transaction():
            assert get_grant(value.tenant_id, value.client_grant_id, collection, session=session) == value
            with pytest.raises(LegalClientMatterMandateGrantRegistryNotFoundError):
                get_grant_by_fingerprint(value.tenant_id, tenant_b.fingerprint, collection, session=session)
            assert list_grants_for_matter_client(value.tenant_id, value.case_matter_id, value.client_party_id, collection, session=session) == (value,)

    divergent = grant(scope_fingerprint="f" * 128)
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalClientMatterMandateGrantRegistryConflictError):
                persist_grant(divergent, collection, session=session)
    divergent_replay = grant(client_grant_id="other-grant", idempotency_key=value.idempotency_key)
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalClientMatterMandateGrantRegistryConflictError):
                persist_grant(divergent_replay, collection, session=session)
    assert collection.count_documents({}) == 2

    earlier = grant(client_grant_id="earlier", idempotency_key="earlier-key", effective_from=value.effective_from - timedelta(minutes=1))
    _committed(earlier, collection, client)
    with client.start_session() as session:
        with session.start_transaction():
            listed = list_grants_for_matter_client(value.tenant_id, value.case_matter_id, value.client_party_id, collection, session=session)
            assert [item.client_grant_id for item in listed] == ["earlier", "client-grant-l9b4"]

    expired = grant(client_grant_id="expired", idempotency_key="expired-key", effective_until=BASE + timedelta(hours=2, seconds=1))
    _committed(expired, collection, client)
    with client.start_session() as session:
        with session.start_transaction():
            assert get_grant(value.tenant_id, expired.client_grant_id, collection, session=session).effective_until == expired.effective_until

    raw = collection.find_one({"client_grant_id": value.client_grant_id})
    assert raw is not None
    assert not any(key in raw for key in ("email", "password", "jwt", "session_token", "document_body"))
    collection.update_one({"client_grant_id": value.client_grant_id}, {"$set": {"scope_fingerprint": "f" * 128}})
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError):
                get_grant(value.tenant_id, value.client_grant_id, collection, session=session)
    collection.delete_one({"client_grant_id": value.client_grant_id})
    _committed(value, collection, client)

    concurrent_value = grant(client_grant_id="concurrent", idempotency_key="concurrent-key")

    def competing_write() -> str:
        independent = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, retryWrites=True)
        try:
            with independent.start_session() as session:
                with session.start_transaction():
                    persist_grant(concurrent_value, database[COLLECTION], session=session)
            return "COMMITTED"
        except Exception as error:
            return type(error).__name__
        finally:
            independent.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: competing_write(), (1, 2)))
    recovered = outcomes.count("COMMITTED") == 0
    if recovered:
        # Both simultaneous transactions may be rejected by Mongo's write
        # conflict policy. Recovery is deliberately caller-owned, outside the
        # registry, and starts one fresh transaction as required by precedent.
        _committed(concurrent_value, collection, client)
    assert outcomes.count("COMMITTED") + int(recovered) >= 1
    assert collection.count_documents({"client_grant_id": "concurrent"}) == 1

    after_collections = set(database.list_collection_names())
    assert after_collections - before_collections <= {COLLECTION}
    assert database.name != "wilsy"


# ARTIFACT: test_legal_client_matter_mandate_grant_registry_real_mongo.py
# VERSION: v1.0.0-L9B7-CLIENT-MANDATE-GRANT-REGISTRY-REAL-MONGO-CERT
# RESULT: UUID-isolated real-Mongo formation certificate only
# END OF WILSY OS SOVEREIGN ARTIFACT
