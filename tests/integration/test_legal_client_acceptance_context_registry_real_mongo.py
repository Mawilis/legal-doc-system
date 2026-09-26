"""Isolated real-Mongo P2C2 certificate for context durability.

TITLE: Legal Client Acceptance Context Registry Real-Mongo Certificate
VERSION: v1.0.0-L9A4-P2C2-CLIENT-ACCEPTANCE-CONTEXT-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove physical append-only context durability, exact replay and
         collision protection, temporal reads, tenant isolation, strict
         hydration, rollback and competing-writer safety.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_acceptance_context_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Synthetic UUID-isolated database only; canonical
                            context composition, acceptance, IAM and finance
                            remain outside this certificate.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2C2-CLIENT-ACCEPTANCE-CONTEXT-REGISTRY-REAL-MONGO-CERT
           proves transactions, exact indexes, replay/collision behavior,
           temporal validity, scope reads, rollback and concurrency.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Loopback-only UUID database and synthetic opaque
                             values; no URI, credentials, tokens or PII output.
TENANT BOUNDARY: Every read/write is exact tenant scoped.
AUTHORITY BOUNDARY: Context evidence persistence/read only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import hashlib
import os
from typing import Any
import uuid

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.domain.legal_client_acceptance_context import (
    LegalClientAcceptanceContext,
)
from tools.eos.legal_operations.registry import (
    legal_client_acceptance_context_registry as registry,
)


UTC = timezone.utc
NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=UTC)


def _fp(seed: str) -> str:
    return hashlib.sha3_512(seed.encode()).hexdigest()


def _context(
    *,
    tenant: str = "tenant-real",
    context_id: str = "context-real-1",
    actor: str = "principal-real-1",
    matter: str = "matter-real-1",
    party: str = "party-real-1",
    replay: str = "replay-real-1",
    issued: datetime = NOW,
    expires: datetime = NOW + timedelta(hours=1),
) -> LegalClientAcceptanceContext:
    """Build synthetic opaque P2C1 evidence only."""
    return LegalClientAcceptanceContext(
        schema="WILSY-LEGAL-CLIENT-ACCEPTANCE-CONTEXT/V1",
        context_version="v1.0.0-L9A4-P2C1-CLIENT-ACCEPTANCE-CONTEXT",
        acceptance_context_id=context_id,
        tenant_id=tenant,
        actor_principal_id=actor,
        case_matter_id=matter,
        matter_reference=f"REF-{matter}",
        matter_fingerprint=_fp(f"matter:{matter}"),
        party_id=party,
        subject_reference=f"client:{party}",
        subject_identity_fingerprint=_fp(f"subject:{party}"),
        capacity_id=f"capacity:{party}",
        capacity_type="REPRESENTATIVE",
        capacity_fingerprint=_fp(f"capacity:{party}"),
        capacity_effective_from=issued - timedelta(days=1),
        capacity_effective_until=None,
        instrument_id="terms",
        instrument_version="1.0.0",
        instrument_fingerprint=_fp("instrument"),
        content_fingerprint=_fp("content"),
        content_reference=f"server://content/{matter}",
        title="Matter Review Terms",
        review_scope="client-information-review:v1",
        instrument_effective_from=issued - timedelta(days=1),
        lifecycle_status="ACTIVE",
        lifecycle_fingerprint=_fp("lifecycle"),
        lifecycle_evidence_fingerprint=_fp("lifecycle-evidence"),
        approval_id="approval-real-1",
        approval_decision="APPROVED",
        approval_fingerprint=_fp("approval"),
        approval_effective_from=issued - timedelta(days=1),
        issuer_evidence_reference="issuer-evidence:1",
        issuer_evidence_fingerprint=_fp("issuer-evidence"),
        issued_at=issued,
        expires_at=expires,
        replay_key=replay,
    )


@pytest.fixture()
def mongo_context():
    """Use one UUID-isolated database and drop only that database."""
    uri = os.environ.get(
        "TEST_VENDOR_MONGO_URI",
        "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
    )
    client = MongoClient(uri, serverSelectionTimeoutMS=5_000)
    database = client[f"wilsy_l9a4_p2c2_context_{uuid.uuid4().hex}"]
    connected = False
    try:
        client.admin.command("ping")
        connected = True
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or not hello.get("isWritablePrimary"):
            pytest.fail("L9A4_P2C2_REAL_MONGO_TOPOLOGY_INVALID")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("L9A4_P2C2_SESSIONS_UNAVAILABLE")
        collection = database[registry.COLLECTION]
        registry.ensure_indexes(collection)
        yield client, database, collection
    finally:
        if connected:
            client.drop_database(database.name)
        client.close()


def _tx(client: MongoClient, callback):
    """Run one caller-owned transaction; the registry owns no lifecycle."""
    with client.start_session() as session:
        return session.with_transaction(callback)


def _persist(client: MongoClient, collection: Any, value: LegalClientAcceptanceContext):
    return _tx(client, lambda session: registry.persist_context(value, collection, session=session))


def _count(client: MongoClient, collection: Any, query: dict[str, object] | None = None) -> int:
    with client.start_session() as session:
        with session.start_transaction():
            return collection.count_documents(query or {}, session=session)


def test_topology_is_writable_replica_set_with_sessions(mongo_context) -> None:
    client, _database, _collection = mongo_context
    hello = client.admin.command("hello")
    assert hello["setName"] == "wilsyVendorCertRS"
    assert hello["isWritablePrimary"] is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None


def test_physical_indexes_are_exact_and_non_expiring(mongo_context) -> None:
    _client, _database, collection = mongo_context
    indexes = collection.index_information()
    assert set(indexes) >= {
        "_id_",
        registry.CONTEXT_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.REPLAY_KEY_INDEX_NAME,
        registry.ACTOR_ISSUED_INDEX_NAME,
        registry.MATTER_ISSUED_INDEX_NAME,
        registry.MATTER_PARTY_ISSUED_INDEX_NAME,
        registry.EXPIRES_INDEX_NAME,
        registry.ACTOR_EXPIRES_INDEX_NAME,
    }
    for name in (registry.CONTEXT_ID_INDEX_NAME, registry.FINGERPRINT_INDEX_NAME, registry.REPLAY_KEY_INDEX_NAME):
        assert indexes[name]["unique"] is True
    assert all("expireAfterSeconds" not in item for item in indexes.values())


def test_persist_replay_is_one_durable_row_and_preserves_microseconds(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _context()
    assert _persist(client, collection, value) == value
    assert _persist(client, collection, value) == value
    assert _count(client, collection) == 1
    read = _tx(client, lambda session: registry.get_context(value.tenant_id, value.acceptance_context_id, collection, session=session))
    assert read.issued_at == NOW and read.issued_at.microsecond == 123456


def test_context_id_and_replay_key_collisions_reject(mongo_context) -> None:
    client, _database, collection = mongo_context
    first = _context()
    _persist(client, collection, first)
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryConflictError):
        _persist(client, collection, _context(context_id=first.acceptance_context_id, replay="replay-real-2", actor="principal-real-2"))
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryConflictError):
        _persist(client, collection, _context(context_id="context-real-2", replay=first.replay_key, actor="principal-real-2"))


def test_cross_tenant_identity_isolation_and_scoped_reads(mongo_context) -> None:
    client, _database, collection = mongo_context
    first, other = _context(), _context(tenant="tenant-other")
    _persist(client, collection, first)
    _persist(client, collection, other)
    assert _count(client, collection) == 2
    assert _tx(client, lambda session: registry.list_contexts_for_actor("tenant-real", first.actor_principal_id, collection, session=session)) == (first,)
    assert _tx(client, lambda session: registry.list_contexts_for_matter("tenant-real", first.case_matter_id, collection, session=session)) == (first,)
    assert _tx(client, lambda session: registry.list_contexts_for_party("tenant-real", first.case_matter_id, first.party_id, collection, session=session)) == (first,)
    assert _tx(client, lambda session: registry.get_context("tenant-other", other.acceptance_context_id, collection, session=session)) == other
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryNotFoundError):
        _tx(client, lambda session: registry.get_context("tenant-unrelated", first.acceptance_context_id, collection, session=session))


def test_temporal_validity_expiry_and_future_are_read_only(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _context()
    _persist(client, collection, value)
    assert _tx(client, lambda session: registry.get_valid_context(value.tenant_id, value.acceptance_context_id, NOW, collection, session=session)) == value
    assert _tx(client, lambda session: registry.get_valid_context(value.tenant_id, value.acceptance_context_id, value.expires_at, collection, session=session)) is None
    future = _context(context_id="context-future", replay="replay-future", issued=NOW + timedelta(days=1), expires=NOW + timedelta(days=2))
    _persist(client, collection, future)
    assert _tx(client, lambda session: registry.get_valid_context(future.tenant_id, future.acceptance_context_id, NOW, collection, session=session)) is None
    assert _count(client, collection) == 2


def test_corrupt_row_is_rejected_without_repair(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _context()
    _persist(client, collection, value)
    with client.start_session() as session:
        with session.start_transaction():
            collection.update_one({"tenant_id": value.tenant_id, "acceptance_context_id": value.acceptance_context_id}, {"$set": {"title": "tampered"}}, session=session)
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryPersistedRecordInvalidError):
        _tx(client, lambda session: registry.get_context(value.tenant_id, value.acceptance_context_id, collection, session=session))


def test_caller_abort_rolls_back_zero_rows(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _context()
    with pytest.raises(RuntimeError):
        def abort(session):
            registry.persist_context(value, collection, session=session)
            raise RuntimeError("synthetic caller abort")
        _tx(client, abort)
    assert _count(client, collection) == 0


def test_competing_identical_writers_leave_one_row(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _context()

    def attempt(_: int) -> str:
        try:
            _persist(client, collection, value)
            return "committed"
        except registry.LegalClientAcceptanceContextRegistryError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, [1, 2]))
    assert "committed" in results
    assert _count(client, collection) == 1


def test_no_other_authority_collection_is_written(mongo_context) -> None:
    client, database, collection = mongo_context
    _persist(client, collection, _context())
    names = set(database.list_collection_names())
    assert names == {registry.COLLECTION}
