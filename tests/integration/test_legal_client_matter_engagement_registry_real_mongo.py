"""Real-Mongo certificate for the L9C10-P1 Engagement registry.

TITLE: WILSY OS Legal Client Matter Engagement Registry Real-Mongo Certificate
VERSION: v1.0.0-L9C10-P3-CLIENT-MATTER-ENGAGEMENT-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove physical indexes, caller-owned transactions, BSON durability,
         rollback, replay, collision rejection, tenant isolation, bounded
         history, strict corruption handling and UUID database isolation for
         the immutable Engagement registry.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_engagement_registry_real_mongo.py
COLLABORATION / OWNERSHIP: This certificate owns only synthetic disposable
                            Mongo evidence. It never touches canonical/shared
                            data and does not implement formation.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C10-P3 proves real replica-set transaction behavior,
           exact canonical BSON persistence, strict replay/collision handling,
           tenant-scoped history and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: URI and credentials are never printed. All values
                             are synthetic opaque certificate data.
TENANT BOUNDARY: Every registry operation and history query is exact tenant
                 scoped; the disposable database is UUID isolated.
AUTHORITY BOUNDARY: Engagement persistence evidence only; no prerequisite
                    authority, formation, currentness, Representation, Court
                    or financial authority is read or changed.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
TRANSACTION BOUNDARY: The test owns session lifecycle; the registry owns none.
FAIL-CLOSED DECLARATION: Any topology, transaction, durability, corruption,
                         isolation or cleanup failure fails certification.
"""
from __future__ import annotations

import ast
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    LegalClientMatterEngagement,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_engagement_registry as registry,
)


UTC = timezone.utc
BASE = datetime(2026, 9, 28, 12, 0, 0, 123456, tzinfo=UTC)
HEX = "a" * 128
SUBJECT_HEX = "b" * 128


def _value(
    *,
    tenant: str = "tenant-real-a",
    engagement_id: str = "engagement-real-1",
    idempotency_key: str = "idempotency-real-1",
    matter_id: str = "matter-real",
    matter_fingerprint: str = HEX,
    party_id: str = "party-real",
    subject_fingerprint: str = SUBJECT_HEX,
    offset: int = 0,
) -> LegalClientMatterEngagement:
    """Construct valid synthetic evidence through the published domain API."""
    effective = BASE + timedelta(minutes=offset)
    return LegalClientMatterEngagement(
        engagement_id=engagement_id,
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint,
        client_party_id=party_id,
        subject_reference="client:subject-real",
        subject_identity_fingerprint=subject_fingerprint,
        acting_capacity_id="capacity-real",
        acting_capacity_fingerprint=HEX,
        client_acceptance_id="acceptance-real",
        client_acceptance_fingerprint=HEX,
        instrument_id="instrument-real",
        version="1",
        instrument_fingerprint=HEX,
        content_fingerprint=HEX,
        mandate_id="mandate-real",
        mandate_scope="scope:real",
        mandate_fingerprint=HEX,
        conflict_disposition_id="disposition-real",
        conflict_disposition_fingerprint=HEX,
        firm_decision_id="decision-real",
        decision_actor_principal_id="principal-real",
        firm_decision_fingerprint=HEX,
        authorization_evidence_reference="authorization:real",
        authorization_evidence_fingerprint=HEX,
        source_evidence_reference="source:real",
        source_evidence_fingerprint=HEX,
        effective_from=effective,
        idempotency_key=idempotency_key,
    )


@pytest.fixture()
def mongo_context():
    """Yield a UUID-isolated database on the sanctioned replica set."""
    uri = os.getenv(
        "TEST_VENDOR_MONGO_URI",
        "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
    )
    client = MongoClient(uri, serverSelectionTimeoutMS=5_000, retryWrites=True)
    database = client[f"wilsy_l9c10_eng_{uuid.uuid4().hex}"]
    try:
        try:
            client.admin.command("ping")
            hello = client.admin.command("hello")
            if hello.get("setName") != "wilsyVendorCertRS":
                pytest.fail("L9C10_P3_REPLICA_SET_INVALID")
            if hello.get("isWritablePrimary") is not True:
                pytest.fail("L9C10_P3_WRITABLE_PRIMARY_REQUIRED")
            if hello.get("logicalSessionTimeoutMinutes") is None:
                pytest.fail("L9C10_P3_SESSIONS_REQUIRED")
            server = client.server_info()
            if not isinstance(server.get("version"), str):
                pytest.fail("L9C10_P3_SERVER_VERSION_UNAVAILABLE")
        except Exception:
            pytest.fail("L9C10_P3_MONGO_UNAVAILABLE")
        if len(database.name) > 63:
            pytest.fail("L9C10_P3_DISPOSABLE_DATABASE_NAME_TOO_LONG")
        collection = database[registry.COLLECTION]
        registry.ensure_indexes(collection)
        registry.ensure_indexes(collection)
        yield client, database, collection
    finally:
        client.drop_database(database.name)
        client.close()


def _transactional_insert(
    client: MongoClient[Any],
    collection: Any,
    value: LegalClientMatterEngagement,
) -> LegalClientMatterEngagement:
    """Persist one value while the test owns the active transaction."""
    with client.start_session() as session:
        session.start_transaction()
        try:
            result = registry.persist_engagement(value, collection, session=session)
            session.commit_transaction()
            return result
        except Exception:
            if session.in_transaction:
                session.abort_transaction()
            raise


def test_real_topology_is_writable_replica_set_with_transactions(mongo_context) -> None:
    client, _database, _collection = mongo_context
    hello = client.admin.command("hello")
    assert hello["setName"] == "wilsyVendorCertRS"
    assert hello["isWritablePrimary"] is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    with client.start_session() as session:
        with session.start_transaction():
            assert session.in_transaction is True
        assert session.in_transaction is False


def test_real_indexes_are_exact_unique_non_ttl_and_repeatable(mongo_context) -> None:
    _client, _database, collection = mongo_context
    indexes = collection.index_information()
    assert indexes[registry.ENGAGEMENT_ID_INDEX_NAME]["unique"] is True
    assert indexes[registry.FINGERPRINT_INDEX_NAME]["unique"] is True
    assert indexes[registry.IDEMPOTENCY_INDEX_NAME]["unique"] is True
    history = indexes[registry.HISTORY_INDEX_NAME]
    assert history.get("unique", False) is False
    assert history["key"] == [
        ("tenant_id", 1),
        ("case_matter_id", 1),
        ("matter_fingerprint", 1),
        ("client_party_id", 1),
        ("subject_identity_fingerprint", 1),
        ("effective_from", 1),
        ("fingerprint", 1),
        ("engagement_id", 1),
    ]
    assert not any("expireAfterSeconds" in item for item in indexes.values())
    assert set(indexes) >= {
        registry.ENGAGEMENT_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.IDEMPOTENCY_INDEX_NAME,
        registry.HISTORY_INDEX_NAME,
    }


def test_real_transaction_requirement_and_session_boundary(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _value()
    with pytest.raises(registry.LegalClientMatterEngagementRegistryTransactionRequiredError):
        registry.persist_engagement(value, collection, session=None)
    with client.start_session() as session:
        with pytest.raises(registry.LegalClientMatterEngagementRegistryTransactionRequiredError):
            registry.persist_engagement(value, collection, session=session)
        session.start_transaction()
        registry.persist_engagement(value, collection, session=session)
        assert session.in_transaction is True
        session.abort_transaction()
    assert collection.count_documents({}) == 0


def test_real_insert_bson_commit_durability_and_strict_readback(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _value()
    with client.start_session() as session:
        session.start_transaction()
        result = registry.persist_engagement(value, collection, session=session)
        raw = collection.find_one(
            {"tenant_id": value.tenant_id, "engagement_id": value.engagement_id},
            session=session,
        )
        assert raw is not None
        raw.pop("_id", None)
        assert raw == value.to_dict()
        assert result == value
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction()
        assert registry.get_engagement(value.tenant_id, value.engagement_id, collection, session=session) == value
        session.commit_transaction()
    assert collection.count_documents({}) == 1


def test_real_rollback_isolation(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _value()
    with client.start_session() as session:
        session.start_transaction()
        registry.persist_engagement(value, collection, session=session)
        session.abort_transaction()
    assert collection.count_documents({}) == 0


def test_real_exact_replay_is_one_row(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _value()
    assert _transactional_insert(client, collection, value) == value
    assert _transactional_insert(client, collection, value) == value
    assert collection.count_documents({}) == 1


def test_real_divergent_idempotency_and_id_collisions_fail_closed(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _value()
    _transactional_insert(client, collection, value)
    with pytest.raises(registry.LegalClientMatterEngagementRegistryConflictError):
        _transactional_insert(
            client,
            collection,
            _value(engagement_id="engagement-real-2", idempotency_key=value.idempotency_key),
        )
    with pytest.raises(registry.LegalClientMatterEngagementRegistryConflictError):
        _transactional_insert(
            client,
            collection,
            _value(idempotency_key="idempotency-real-2"),
        )
    assert collection.count_documents({}) == 1


def test_real_fingerprint_replay_and_corruption_fail_closed(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _value()
    _transactional_insert(client, collection, value)
    with client.start_session() as session:
        session.start_transaction()
        assert registry.get_engagement_by_fingerprint(value.tenant_id, value.fingerprint, collection, session=session) == value
        session.commit_transaction()
    collection.update_one(
        {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
        {"$set": {"mandate_scope": "tampered-scope"}},
    )
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientMatterEngagementRegistryPersistedRecordInvalidError):
            registry.get_engagement_by_fingerprint(value.tenant_id, value.fingerprint, collection, session=session)
        session.abort_transaction()
    assert collection.count_documents({}) == 1


def test_real_duplicate_race_leaves_one_canonical_row(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _value()

    def contender(_: int) -> str:
        try:
            _transactional_insert(client, collection, value)
            return "committed"
        except Exception:
            return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(contender, (1, 2)))
    assert "committed" in results
    assert collection.count_documents({"tenant_id": value.tenant_id}) == 1
    assert _transactional_insert(client, collection, value) == value


def test_real_tenant_scoped_id_fingerprint_and_idempotency_reads(mongo_context) -> None:
    client, _database, collection = mongo_context
    first = _value()
    other = _value(tenant="tenant-real-b")
    _transactional_insert(client, collection, first)
    _transactional_insert(client, collection, other)
    with client.start_session() as session:
        session.start_transaction()
        assert registry.get_engagement(first.tenant_id, first.engagement_id, collection, session=session) == first
        assert registry.get_engagement_by_fingerprint(other.tenant_id, other.fingerprint, collection, session=session) == other
        assert registry.get_engagement_by_idempotency_key(other.tenant_id, other.idempotency_key, collection, session=session) == other
        with pytest.raises(registry.LegalClientMatterEngagementRegistryNotFoundError):
            registry.get_engagement("tenant-real-wrong", first.engagement_id, collection, session=session)
        with pytest.raises(registry.LegalClientMatterEngagementRegistryNotFoundError):
            registry.get_engagement_by_fingerprint("tenant-real-wrong", first.fingerprint, collection, session=session)
        with pytest.raises(registry.LegalClientMatterEngagementRegistryNotFoundError):
            registry.get_engagement_by_idempotency_key("tenant-real-wrong", first.idempotency_key, collection, session=session)
        session.commit_transaction()


def test_real_multiple_rows_history_filter_order_and_empty_history(mongo_context) -> None:
    client, _database, collection = mongo_context
    later = _value(engagement_id="engagement-real-2", idempotency_key="idempotency-real-2", offset=2)
    earlier = _value(engagement_id="engagement-real-1", idempotency_key="idempotency-real-1", offset=1)
    neighbors = (
        _value(engagement_id="engagement-real-3", idempotency_key="idempotency-real-3", tenant="tenant-real-b"),
        _value(engagement_id="engagement-real-4", idempotency_key="idempotency-real-4", matter_id="matter-neighbor"),
        _value(engagement_id="engagement-real-5", idempotency_key="idempotency-real-5", matter_fingerprint="c" * 128),
        _value(engagement_id="engagement-real-6", idempotency_key="idempotency-real-6", party_id="party-neighbor"),
        _value(engagement_id="engagement-real-7", idempotency_key="idempotency-real-7", subject_fingerprint="d" * 128),
    )
    for value in (later, *neighbors, earlier):
        _transactional_insert(client, collection, value)
    with client.start_session() as session:
        session.start_transaction()
        history = registry.list_engagements_for_context(
            "tenant-real-a", "matter-real", HEX, "party-real", SUBJECT_HEX,
            collection, session=session,
        )
        assert history == (earlier, later)
        assert registry.list_engagements_for_context(
            "tenant-real-a", "other-matter", HEX, "party-real", SUBJECT_HEX,
            collection, session=session,
        ) == ()
        session.commit_transaction()
    assert collection.count_documents({}) == 7


def test_real_registry_source_has_zero_prerequisite_and_downstream_authority() -> None:
    source_path = Path("tools/eos/legal_operations/registry/legal_client_matter_engagement_registry.py")
    source = source_path.read_text()
    tree = ast.parse(source)
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    imported = " ".join(ast.unparse(node) for node in imports).lower()
    assert "legal_client_matter_engagement" in imported
    for forbidden in (
        "case_matter", "legal_matter_party", "acting_capacity", "client_acceptance",
        "acceptance_instrument", "conflict_currentness", "mandate_currentness",
        "firm_decision_currentness", "authorization", "representation", "court", "http",
    ):
        assert forbidden not in imported
    assert "def persist_engagement" in source
    assert "def list_engagements_for_context" in source
    assert "currentness" in source.lower()
    assert "ttl" in source.lower()


# ARTIFACT: test_legal_client_matter_engagement_registry_real_mongo.py
# VERSION: v1.0.0-L9C10-P3-CLIENT-MATTER-ENGAGEMENT-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical immutable Engagement persistence evidence only
# TENANT POSTURE: UUID-isolated database and exact tenant/lineage queries
# FAIL-CLOSED POSTURE: rollback, corruption, conflict and race cannot create divergent truth
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
