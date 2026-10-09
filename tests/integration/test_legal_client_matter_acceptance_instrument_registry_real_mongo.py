"""Real-Mongo certificate for the L9A4-P1B2 instrument registry.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument Registry Real-Mongo Certificate
VERSION: v1.0.0-L9A4-P1B2-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Direct physical certification of immutable instrument persistence.
EPITOME: Prove the sanctioned replica-set topology, transactions, indexes,
         replay, supersession, effective selection, isolation, rollback,
         concurrency, UTC precision, corruption rejection and authority scope.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_acceptance_instrument_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Synthetic UUID-isolated Mongo evidence only. No
                            canonical/shared database or client acceptance is
                            touched; this certificate owns no production truth.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P1B2-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-REGISTRY-REAL-MONGO-CERT
           proves physical indexes, transactions, append-only replay,
           supersession and deterministic effective selection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Loopback-only UUID database and synthetic opaque
                             values; no URI, credentials, tokens or PII output.
TENANT BOUNDARY: Every durable read and write is tenant/matter scoped.
AUTHORITY BOUNDARY: Instrument persistence evidence only; no acceptance,
                    engagement, representation, Court or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
import uuid

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    LegalClientMatterAcceptanceInstrument,
    record_legal_client_matter_acceptance_instrument,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry import (
    legal_client_matter_acceptance_instrument_registry as registry,
)


UTC = timezone.utc
NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=UTC)


def _matter(tenant: str = "tenant-real", matter_id: str = "matter-real") -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant, case_matter_id=matter_id,
        matter_reference=f"REF-{matter_id}", opened_at=NOW,
        evidence_reference=f"intake:{matter_id}",
    )


def _instrument(
    *, tenant: str = "tenant-real", matter_id: str = "matter-real",
    instrument_id: str = "instrument-real", version: str = "1.0.0",
    effective_from: datetime = NOW, supersedes: str | None = None,
    content: bytes | None = None,
) -> LegalClientMatterAcceptanceInstrument:
    content_bytes = content or f"content-{version}".encode()
    return record_legal_client_matter_acceptance_instrument(
        case_matter=_matter(tenant, matter_id), instrument_id=instrument_id,
        version=version, instrument_kind="MATTER_REVIEW",
        title="Matter Information Review",
        review_scope=f"Bounded review scope for {instrument_id} {version}.",
        content_reference=f"artifact:{matter_id}/{instrument_id}/{version}",
        content_fingerprint=hashlib.sha3_512(content_bytes).hexdigest(),
        created_at=NOW, effective_from=effective_from,
        approval_evidence_reference=f"approval:{matter_id}/{instrument_id}/{version}",
        approval_evidence_fingerprint=hashlib.sha3_512(f"approval-{version}".encode()).hexdigest(),
        supersedes_version_id=supersedes,
    )


@pytest.fixture()
def mongo_context():
    uri = os.environ.get(
        "TEST_VENDOR_MONGO_URI",
        "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
    )
    client = MongoClient(uri, serverSelectionTimeoutMS=5_000)
    database = client[f"wilsy_l9a4_p1b2_instrument_{uuid.uuid4().hex}"]
    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or not hello.get("isWritablePrimary"):
            pytest.fail("L9A4_P1B2_REAL_MONGO_TOPOLOGY_INVALID")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("L9A4_P1B2_SESSIONS_UNAVAILABLE")
        collection = database[registry.COLLECTION]
        registry.ensure_indexes(collection)
        yield client, database, collection
    finally:
        client.drop_database(database.name)
        client.close()


def _transactional_insert(client: MongoClient, collection: object, value: LegalClientMatterAcceptanceInstrument) -> LegalClientMatterAcceptanceInstrument:
    with client.start_session() as session:
        def callback(active_session):
            return registry.persist_instrument(value, collection, session=active_session)
        return session.with_transaction(callback)


def test_real_topology_is_writable_replica_set_with_transactions(mongo_context) -> None:
    client, _database, _collection = mongo_context
    hello = client.admin.command("hello")
    assert hello["setName"] == "wilsyVendorCertRS"
    assert hello["isWritablePrimary"] is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    with client.start_session() as session:
        with session.start_transaction():
            session.abort_transaction()


def test_real_indexes_are_exact_unique_and_no_ttl(mongo_context) -> None:
    _client, _database, collection = mongo_context
    indexes = collection.index_information()
    assert indexes[registry.IDENTITY_INDEX_NAME]["unique"] is True
    assert indexes[registry.FINGERPRINT_INDEX_NAME]["unique"] is True
    assert indexes[registry.MATTER_INSTRUMENT_INDEX_NAME].get("unique", False) is False
    assert indexes[registry.MATTER_KIND_INDEX_NAME].get("unique", False) is False
    assert indexes[registry.MATTER_EFFECTIVE_INDEX_NAME].get("unique", False) is False
    assert not any("expireAfterSeconds" in item for item in indexes.values())


def test_real_persist_replay_one_row_and_microseconds(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _instrument()
    assert _transactional_insert(client, collection, value) == value
    assert _transactional_insert(client, collection, value) == value
    assert collection.count_documents({}) == 1
    assert collection.find_one({"tenant_id": value.tenant_id})["created_at"].endswith(".123456Z")


def test_real_v2_supersession_and_effective_selection(mongo_context) -> None:
    client, _database, collection = mongo_context
    first = _instrument()
    second = _instrument(version="2.0.0", effective_from=NOW + timedelta(days=1), supersedes=first.version_id)
    future = _instrument(version="3.0.0", effective_from=NOW + timedelta(days=3))
    for value in (first, second, future):
        _transactional_insert(client, collection, value)
    with client.start_session() as session:
        with session.start_transaction():
            assert registry.get_latest_effective_version("tenant-real", "matter-real", "instrument-real", NOW + timedelta(hours=1), collection, session=session) == first
            assert registry.get_latest_effective_version("tenant-real", "matter-real", "instrument-real", NOW + timedelta(days=2), collection, session=session) == second
            assert registry.get_latest_effective_version("tenant-real", "matter-real", "instrument-real", NOW + timedelta(days=2, hours=1), collection, session=session) == second
            session.commit_transaction()
    assert collection.count_documents({}) == 3


def test_real_version_reads_kind_reads_and_cross_scope_isolation(mongo_context) -> None:
    client, _database, collection = mongo_context
    first = _instrument()
    other_matter = _instrument(matter_id="matter-other", instrument_id="instrument-other")
    other_tenant = _instrument(tenant="tenant-other", instrument_id="instrument-other-tenant")
    for value in (first, other_matter, other_tenant):
        _transactional_insert(client, collection, value)
    with client.start_session() as session:
        with session.start_transaction():
            assert registry.get_instrument("tenant-real", "matter-real", "instrument-real", "1.0.0", collection, session=session) == first
            assert len(registry.list_instrument_versions("tenant-real", "matter-real", "instrument-real", collection, session=session)) == 1
            assert len(registry.list_matter_instruments_by_kind("tenant-real", "matter-real", "MATTER_REVIEW", collection, session=session)) == 1
            with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentRegistryNotFoundError):
                registry.get_instrument("tenant-real", "matter-real", "instrument-other-tenant", "1.0.0", collection, session=session)
            session.commit_transaction()


def test_real_divergent_same_version_rejected(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _instrument()
    _transactional_insert(client, collection, value)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentRegistryConflictError):
        _transactional_insert(client, collection, _instrument(content=b"different"))
    assert collection.count_documents({}) == 1


def test_real_abort_leaves_zero_rows(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _instrument()
    with client.start_session() as session:
        session.start_transaction()
        registry.persist_instrument(value, collection, session=session)
        session.abort_transaction()
    assert collection.count_documents({}) == 0


def test_real_competing_identical_consumers_leave_one_row(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _instrument()

    def consume() -> str:
        try:
            _transactional_insert(client, collection, value)
            return "committed"
        except Exception:
            return "race-rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _item: consume(), (1, 2)))
    assert "committed" in results
    assert collection.count_documents({"tenant_id": value.tenant_id}) == 1
    assert _transactional_insert(client, collection, value) == value


def test_real_corruption_is_rejected_and_no_other_authority_rows_exist(mongo_context) -> None:
    client, database, collection = mongo_context
    value = _instrument()
    _transactional_insert(client, collection, value)
    collection.update_one({"tenant_id": value.tenant_id}, {"$set": {"title": "tampered"}})
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError):
                registry.get_instrument("tenant-real", "matter-real", "instrument-real", "1.0.0", collection, session=session)
            session.abort_transaction()
    assert set(database.list_collection_names()) == {registry.COLLECTION}
    assert database[registry.COLLECTION].count_documents({"acceptance_id": {"$exists": True}}) == 0


# ARTIFACT: test_legal_client_matter_acceptance_instrument_registry_real_mongo.py
# VERSION: v1.0.0-L9A4-P1B2-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical immutable instrument persistence/read evidence only
# TENANT POSTURE: UUID-isolated database and exact tenant/matter queries
# FAIL-CLOSED POSTURE: rollback/corruption/conflict/race cannot create divergent truth
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
