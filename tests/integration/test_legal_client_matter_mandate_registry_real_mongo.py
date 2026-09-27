"""Real-Mongo certificate for the immutable client-matter mandate registry.

TITLE: WILSY OS Legal Client Matter Mandate Registry Real-Mongo Certificate
VERSION: v1.0.0-L9B11-CLIENT-MATTER-MANDATE-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the mandate registry against a writable local replica set
         using only UUID-isolated disposable databases and synthetic domain
         evidence. Canonical ``wilsy`` is never selected or mutated.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_mandate_registry_real_mongo.py
COLLABORATION / OWNERSHIP: This certificate covers immutable persistence only;
                            formation composition, currentness, lifecycle,
                            Engagement, Representation, Court, IAM and finance
                            remain separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B11 certifies topology, indexes, transaction ownership,
           durable readback, replay/collision policy, pair uniqueness, history,
           tenant isolation, concurrent writers, corruption and raw-BSON audit.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque evidence only; no URI, secret,
                             bearer token, PII or password is printed.
TENANT BOUNDARY: Every registry read and write carries exact tenant identity.
AUTHORITY BOUNDARY: Disposable mandate collection only; no upstream/downstream
                    collection is read or mutated.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement or release authority;
                              Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Each transaction is created and completed by the test;
                      registry methods never begin, commit, abort or retry.
FAIL-CLOSED DECLARATION: Topology, durability, collision, corruption and
                         isolation failures fail the certificate.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import os
import uuid

import pytest
from pymongo import MongoClient, version as pymongo_version
from pymongo.errors import PyMongoError

import tools.eos.legal_operations.domain.legal_client_matter_mandate as mandate_domain
from tools.eos.legal_operations.registry.legal_client_matter_mandate_registry import (
    COLLECTION,
    FINGERPRINT_INDEX_NAME,
    HISTORY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    MANDATE_ID_INDEX_NAME,
    PAIR_INDEX_NAME,
    LegalClientMatterMandateRegistryConflictError,
    LegalClientMatterMandateRegistryNotFoundError,
    LegalClientMatterMandateRegistryPersistedRecordInvalidError,
    LegalClientMatterMandateRegistryRetryRequiredError,
    LegalClientMatterMandateRegistryTransactionRequiredError,
    ensure_indexes,
    get_mandate,
    get_mandate_by_fingerprint,
    list_mandates_for_matter,
    persist_mandate,
)
from tests.unit.test_legal_client_matter_mandate import mandate, matter, party


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
        database = client[f"wilsy_l9b11_mandate_registry_{uuid.uuid4().hex}"]
        collection = database[COLLECTION]
        ensure_indexes(collection)
        yield client, database, collection
    except PyMongoError as error:
        pytest.fail(f"real Mongo prerequisite/certificate failure: {type(error).__name__}")
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _commit(client: MongoClient, collection: object, value: object) -> object:
    with client.start_session() as session:
        with session.start_transaction():
            return persist_mandate(value, collection, session=session)  # type: ignore[arg-type]


def test_topology_indexes_transaction_and_durable_readback(isolated_database) -> None:
    client, database, collection = isolated_database
    indexes = {item["name"]: item for item in collection.list_indexes()}
    expected = {MANDATE_ID_INDEX_NAME, FINGERPRINT_INDEX_NAME, IDEMPOTENCY_INDEX_NAME, HISTORY_INDEX_NAME, PAIR_INDEX_NAME}
    assert expected.issubset(indexes)
    assert all("expireAfterSeconds" not in item for item in indexes.values())
    assert all(indexes[name].get("unique") is True for name in (MANDATE_ID_INDEX_NAME, FINGERPRINT_INDEX_NAME, IDEMPOTENCY_INDEX_NAME, PAIR_INDEX_NAME))
    assert list(indexes[MANDATE_ID_INDEX_NAME]["key"].items()) == [("tenant_id", 1), ("mandate_id", 1)]
    assert list(indexes[FINGERPRINT_INDEX_NAME]["key"].items()) == [("tenant_id", 1), ("fingerprint", 1)]
    assert list(indexes[IDEMPOTENCY_INDEX_NAME]["key"].items()) == [("tenant_id", 1), ("idempotency_key", 1)]
    assert list(indexes[PAIR_INDEX_NAME]["key"].items()) == [("tenant_id", 1), ("client_grant_fingerprint", 1), ("firm_acknowledgment_fingerprint", 1)]
    value = mandate()
    with pytest.raises(LegalClientMatterMandateRegistryTransactionRequiredError):
        persist_mandate(value, collection, session=None)
    with client.start_session() as session:
        with pytest.raises(LegalClientMatterMandateRegistryTransactionRequiredError):
            persist_mandate(value, collection, session=session)
    assert _commit(client, collection, value).to_dict() == value.to_dict()  # type: ignore[union-attr]
    with client.start_session() as session:
        with session.start_transaction():
            read = get_mandate(value.tenant_id, value.mandate_id, collection, session=session)
            assert read.to_dict() == value.to_dict()
            assert get_mandate_by_fingerprint(value.tenant_id, value.fingerprint, collection, session=session) == value
            assert database[COLLECTION].count_documents({}, session=session) == 1
    assert pymongo_version


def test_real_replay_collisions_and_exact_pair_uniqueness(isolated_database, monkeypatch: pytest.MonkeyPatch) -> None:
    client, _, collection = isolated_database
    value = mandate()
    _commit(client, collection, value)
    with client.start_session() as session:
        with session.start_transaction():
            assert persist_mandate(value, collection, session=session) == value
            assert get_mandate_by_fingerprint(value.tenant_id, value.fingerprint, collection, session=session) == value
    with pytest.raises(LegalClientMatterMandateRegistryConflictError):
        _commit(client, collection, mandate(scope_fingerprint="f" * 128))
    with pytest.raises(LegalClientMatterMandateRegistryConflictError):
        _commit(client, collection, mandate(mandate_id="different-id"))
    with pytest.raises(LegalClientMatterMandateRegistryConflictError):
        _commit(client, collection, mandate(mandate_id="different-id", idempotency_key="different-key"))
    monkeypatch.setattr(mandate_domain, "_digest", lambda _: value.fingerprint)
    fingerprint_collision = mandate(mandate_id="fingerprint-collision-id", idempotency_key="fingerprint-collision-key")
    with pytest.raises(LegalClientMatterMandateRegistryConflictError):
        _commit(client, collection, fingerprint_collision)
    assert collection.count_documents({}) == 1


def test_multiple_history_tenant_isolation_and_raw_bson_audit(isolated_database) -> None:
    client, database, collection = isolated_database
    first = mandate()
    second = mandate(
        mandate_id="mandate-l9b3-successor",
        idempotency_key="mandate-idempotency:successor",
        client_grant_fingerprint="1" * 128,
        firm_acknowledgment_fingerprint="2" * 128,
        effective_from=first.effective_from + timedelta(days=1),
    )
    _commit(client, collection, first)
    _commit(client, collection, second)
    values = None
    with client.start_session() as session:
        with session.start_transaction():
            values = list_mandates_for_matter(first.tenant_id, first.case_matter_id, first.client_party_id, collection, session=session)
    assert values == (first, second)
    other_matter = matter(tenant_id="tenant-l9b3-b", matter_id="matter-l9b3-b")
    other_party = party(source_matter=other_matter, party_id="party-l9b3-b")
    other = mandate(mandate_id=first.mandate_id, idempotency_key="tenant-b-key", case_matter=other_matter, party=other_party)
    _commit(client, collection, other)
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalClientMatterMandateRegistryNotFoundError):
                get_mandate_by_fingerprint(first.tenant_id, other.fingerprint, collection, session=session)
            assert get_mandate(other.tenant_id, other.mandate_id, collection, session=session) == other
    assert database.list_collection_names() == [COLLECTION]
    for row in collection.find({}):
        assert set(row) == set(first.to_dict()) | {"_id"}
        assert not {"current", "currentness", "raw_pii", "document_body", "token", "password"} & set(row)


def test_corruption_is_rejected_and_unrelated_authorities_are_untouched(isolated_database) -> None:
    client, database, collection = isolated_database
    value = mandate()
    _commit(client, collection, value)
    collection.update_one({"mandate_id": value.mandate_id}, {"$set": {"mutable_current": True}})
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalClientMatterMandateRegistryPersistedRecordInvalidError):
                get_mandate(value.tenant_id, value.mandate_id, collection, session=session)
    assert set(database.list_collection_names()) == {COLLECTION}


def test_concurrent_same_identity_creates_one_row(isolated_database) -> None:
    client, _, collection = isolated_database
    value = mandate()

    def writer() -> str:
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    persist_mandate(value, collection, session=session)
            return "COMMITTED"
        except (LegalClientMatterMandateRegistryRetryRequiredError, LegalClientMatterMandateRegistryConflictError):
            return "REJECTED"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: writer(), range(2)))
    assert sorted(results) == ["COMMITTED", "REJECTED"]
    assert collection.count_documents({}) == 1


# ARTIFACT: test_legal_client_matter_mandate_registry_real_mongo.py
# VERSION: v1.0.0-L9B11-CLIENT-MATTER-MANDATE-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable real-Mongo certificate only
# FAIL-CLOSED POSTURE: no canonical database and no unrelated collection writes
# END OF WILSY OS SOVEREIGN ARTIFACT
