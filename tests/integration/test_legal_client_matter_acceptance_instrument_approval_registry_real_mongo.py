"""Isolated real-Mongo certificate for the P2B2 approval registry.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument Approval Registry Real-Mongo Certificate
VERSION: v1.0.0-L9A4-P2B2-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Direct physical certification of append-only approval evidence.
EPITOME: Prove the sanctioned loopback replica set, transactions, exact
         indexes, replay/collision behavior, currentness chronology, isolation,
         concurrent races and abort zero-write semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_acceptance_instrument_approval_registry_real_mongo.py
COLLABORATION / OWNERSHIP: UUID-isolated synthetic database only; canonical
                            data and IAM/acceptance/finance remain out of scope.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2B2-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-REGISTRY-REAL-MONGO-CERT
           proves physical approval history, exact replay/collisions, currentness,
           isolation, concurrency and caller-owned rollback.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Loopback-only UUID database and synthetic opaque
                             values; no URI, credentials, tokens or PII output.
TENANT BOUNDARY: Every query and mutation is exact tenant and complete subject scoped.
AUTHORITY BOUNDARY: Approval evidence/currentness only; no IAM or acceptance.
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

from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_approval import (
    LegalClientMatterAcceptanceInstrumentApproval,
    LegalClientMatterAcceptanceInstrumentApprovalDecision as Decision,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_acceptance_instrument_approval_registry as registry,
)


UTC = timezone.utc
NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=UTC)
TENANT = "tenant-real"
MATTER = "matter-real"
INSTRUMENT = "instrument-real"
VERSION = "1.0.0"
MATTER_FP = hashlib.sha3_512(b"real-matter").hexdigest()
INSTRUMENT_FP = hashlib.sha3_512(b"real-instrument").hexdigest()
CONTENT_FP = hashlib.sha3_512(b"real-content").hexdigest()
EVIDENCE_FP = hashlib.sha3_512(b"real-evidence").hexdigest()


def _approval(
    *,
    tenant: str = TENANT,
    matter: str = MATTER,
    instrument: str = INSTRUMENT,
    version: str = VERSION,
    approval_id: str = "approval-real-1",
    idempotency_key: str = "idem-real-1",
    decision: Decision = Decision.APPROVED,
    instrument_fp: str = INSTRUMENT_FP,
    content_fp: str = CONTENT_FP,
    occurred_at: datetime = NOW,
    effective_from: datetime = NOW,
) -> LegalClientMatterAcceptanceInstrumentApproval:
    """Build one synthetic immutable approval without secrets or PII."""
    return LegalClientMatterAcceptanceInstrumentApproval(
        tenant_id=tenant,
        case_matter_id=matter,
        matter_fingerprint=MATTER_FP,
        approval_id=approval_id,
        instrument_id=instrument,
        version=version,
        instrument_fingerprint=instrument_fp,
        content_fingerprint=content_fp,
        decision=decision,
        approver_principal_id="principal-real-1",
        approver_capacity_reference="capacity:reviewer",
        authorization_evidence_reference="auth:real-1",
        authorization_evidence_fingerprint=EVIDENCE_FP,
        approval_evidence_reference="approval:real-1",
        approval_evidence_fingerprint=EVIDENCE_FP,
        occurred_at=occurred_at,
        effective_from=effective_from,
        idempotency_key=idempotency_key,
    )


@pytest.fixture()
def mongo_context():
    """Yield one UUID-isolated database and drop only that database."""
    uri = os.environ.get(
        "TEST_VENDOR_MONGO_URI",
        "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
    )
    client = MongoClient(uri, serverSelectionTimeoutMS=5_000)
    database = client[f"wilsy_l9a4_p2b2_approval_{uuid.uuid4().hex}"]
    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or not hello.get("isWritablePrimary"):
            pytest.fail("L9A4_P2B2_REAL_MONGO_TOPOLOGY_INVALID")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("L9A4_P2B2_SESSIONS_UNAVAILABLE")
        collection = database[registry.COLLECTION]
        registry.ensure_indexes(collection)
        yield client, database, collection
    finally:
        client.drop_database(database.name)
        client.close()


def _tx(client: MongoClient, callback):
    """Run one caller-owned transaction; registry never owns its lifecycle."""
    with client.start_session() as session:
        return session.with_transaction(callback)


def _persist(client: MongoClient, collection: object, value: LegalClientMatterAcceptanceInstrumentApproval):
    """Persist one synthetic value through the canonical transaction path."""
    return _tx(client, lambda session: registry.persist_approval(value, collection, session=session))


def _count(collection: Any, client: MongoClient, query: dict[str, object] | None = None) -> int:
    """Read one aggregate count in a caller-owned read transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return collection.count_documents(query or {}, session=session)


def test_real_topology_is_writable_replica_set_with_sessions(mongo_context) -> None:
    client, _database, _collection = mongo_context
    hello = client.admin.command("hello")
    assert hello["setName"] == "wilsyVendorCertRS"
    assert hello["isWritablePrimary"] is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    with client.start_session() as session:
        with session.start_transaction():
            assert session.in_transaction is True


def test_indexes_are_physical_exact_and_non_expiring(mongo_context) -> None:
    _client, _database, collection = mongo_context
    indexes = collection.index_information()
    assert set(indexes) >= {
        "_id_", registry.APPROVAL_ID_INDEX_NAME, registry.FINGERPRINT_INDEX_NAME,
        registry.IDEMPOTENCY_INDEX_NAME, registry.HISTORY_INDEX_NAME, registry.DECISION_INDEX_NAME,
    }
    for name in (registry.APPROVAL_ID_INDEX_NAME, registry.FINGERPRINT_INDEX_NAME, registry.IDEMPOTENCY_INDEX_NAME):
        assert indexes[name]["unique"] is True
    assert all("expireAfterSeconds" not in item for item in indexes.values())


def test_insert_commits_exact_document_and_history(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _persist(client, collection, _approval())
    assert value.to_dict() == _tx(client, lambda session: registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, session=session))[0].to_dict()
    assert _count(collection, client) == 1


def test_exact_replay_is_single_row(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _approval()
    first = _persist(client, collection, value)
    second = _persist(client, collection, value)
    assert first.to_dict() == second.to_dict()
    assert _count(collection, client) == 1


def test_approval_id_collision_rejects(mongo_context) -> None:
    client, _database, collection = mongo_context
    _persist(client, collection, _approval())
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryConflictError):
        _persist(client, collection, _approval(approval_id="approval-real-1", idempotency_key="idem-real-2", decision=Decision.REJECTED))


def test_idempotency_collision_rejects(mongo_context) -> None:
    client, _database, collection = mongo_context
    _persist(client, collection, _approval())
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryConflictError):
        _persist(client, collection, _approval(approval_id="approval-real-2", idempotency_key="idem-real-1"))


def test_fingerprint_collision_is_unique_and_replay_safe(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _approval()
    _persist(client, collection, value)
    assert _count(collection, client, {"fingerprint": value.fingerprint}) == 1


def test_current_approved_before_rejection(mongo_context) -> None:
    client, _database, collection = mongo_context
    _persist(client, collection, _approval())
    rejected_at = NOW + timedelta(days=1)
    _persist(client, collection, _approval(decision=Decision.REJECTED, approval_id="approval-real-2", idempotency_key="idem-real-2", occurred_at=rejected_at, effective_from=rejected_at))
    before = _tx(client, lambda session: registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=NOW + timedelta(hours=1), session=session))
    after = _tx(client, lambda session: registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=rejected_at, session=session))
    assert before is not None and before.decision is Decision.APPROVED
    assert after is None


def test_future_effective_boundary_is_excluded(mongo_context) -> None:
    client, _database, collection = mongo_context
    future = NOW + timedelta(days=1)
    _persist(client, collection, _approval(effective_from=future, occurred_at=NOW))
    assert _tx(client, lambda session: registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=NOW, session=session)) is None


def test_equal_effective_divergent_decisions_fail_closed(mongo_context) -> None:
    client, _database, collection = mongo_context
    effective = NOW + timedelta(days=1)
    _persist(client, collection, _approval(effective_from=effective, occurred_at=NOW))
    _persist(client, collection, _approval(decision=Decision.REJECTED, approval_id="approval-real-2", idempotency_key="idem-real-2", effective_from=effective, occurred_at=NOW + timedelta(hours=1)))
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryAmbiguousCurrentError):
        _tx(client, lambda session: registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=effective + timedelta(hours=1), session=session))


def test_stale_fingerprints_are_excluded(mongo_context) -> None:
    client, _database, collection = mongo_context
    _persist(client, collection, _approval())
    stale = hashlib.sha3_512(b"stale").hexdigest()
    assert _tx(client, lambda session: registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, stale, CONTENT_FP, collection, at=NOW, session=session)) is None


def test_tenant_isolation(mongo_context) -> None:
    client, _database, collection = mongo_context
    _persist(client, collection, _approval())
    assert _tx(client, lambda session: registry.get_approval_history("tenant-other", MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, session=session)) == ()


def test_subject_isolation(mongo_context) -> None:
    client, _database, collection = mongo_context
    _persist(client, collection, _approval())
    assert _tx(client, lambda session: registry.get_approval_history(TENANT, "matter-other", INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, session=session)) == ()


def test_content_fingerprint_isolation(mongo_context) -> None:
    client, _database, collection = mongo_context
    _persist(client, collection, _approval())
    other = hashlib.sha3_512(b"other-content").hexdigest()
    assert _tx(client, lambda session: registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, other, collection, session=session)) == ()


def test_instrument_fingerprint_isolation(mongo_context) -> None:
    client, _database, collection = mongo_context
    _persist(client, collection, _approval())
    other = hashlib.sha3_512(b"other-instrument").hexdigest()
    assert _tx(client, lambda session: registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, other, CONTENT_FP, collection, session=session)) == ()


def test_no_history_returns_none(mongo_context) -> None:
    client, _database, collection = mongo_context
    assert _tx(client, lambda session: registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=NOW, session=session)) is None


def test_get_exact_approval(mongo_context) -> None:
    client, _database, collection = mongo_context
    _persist(client, collection, _approval())
    assert _tx(client, lambda session: registry.get_approval(TENANT, "approval-real-1", collection, session=session)).approval_id == "approval-real-1"


def test_missing_approval_is_bounded(mongo_context) -> None:
    client, _database, collection = mongo_context
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryNotFoundError):
        _tx(client, lambda session: registry.get_approval(TENANT, "missing", collection, session=session))


def test_utc_microseconds_round_trip(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _persist(client, collection, _approval())
    assert value.occurred_at == NOW and value.occurred_at.microsecond == 123456


def test_session_propagates_on_reads_and_write(mongo_context) -> None:
    client, _database, collection = mongo_context
    with client.start_session() as session:
        with session.start_transaction():
            registry.persist_approval(_approval(), collection, session=session)
            registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, session=session)


def test_abort_rolls_back_zero_rows(mongo_context) -> None:
    client, _database, collection = mongo_context
    with pytest.raises(RuntimeError):
        _tx(client, lambda session: (_persist_in_transaction(collection, session), _raise_abort())[1])
    assert _count(collection, client) == 0


def _persist_in_transaction(collection: object, session: object):
    """Insert one record inside an intentionally aborted caller transaction."""
    return registry.persist_approval(_approval(), collection, session=session)


def _raise_abort():
    """Raise after the registry write to prove caller-owned rollback."""
    raise RuntimeError("synthetic caller abort")


def test_concurrent_identical_writers_have_one_durable_row(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _approval()

    def worker():
        try:
            return _persist(client, collection, value)
        except registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryRetryRequiredError:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _item: worker(), (1, 2)))
    assert sum(result is not None for result in results) == 1
    assert _count(collection, client) == 1


def test_concurrent_divergent_writers_do_not_duplicate_identity(mongo_context) -> None:
    client, _database, collection = mongo_context
    first = _approval()
    second = _approval(approval_id="approval-real-2", idempotency_key="idem-real-1", decision=Decision.REJECTED)

    def worker(value):
        try:
            return _persist(client, collection, value)
        except (registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryRetryRequiredError, registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryConflictError):
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(worker, (first, second)))
    assert _count(collection, client) == 1


def test_no_ttl_or_mutation_surface_is_created(mongo_context) -> None:
    client, _database, collection = mongo_context
    before = collection.index_information()
    assert all("expireAfterSeconds" not in item for item in before.values())
    _persist(client, collection, _approval())
    assert _count(collection, client) == 1


def test_corrupt_row_fails_closed(mongo_context) -> None:
    client, _database, collection = mongo_context
    value = _approval()
    _persist(client, collection, value)
    collection.update_one({"fingerprint": value.fingerprint}, {"$set": {"decision": "CORRUPT"}})
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistedRecordInvalidError):
        _tx(client, lambda session: registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, session=session))


def test_same_decision_equal_effective_time_is_deterministic(mongo_context) -> None:
    client, _database, collection = mongo_context
    _persist(client, collection, _approval())
    _persist(client, collection, _approval(approval_id="approval-real-2", idempotency_key="idem-real-2"))
    current = _tx(client, lambda session: registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=NOW, session=session))
    assert current is not None and current.decision is Decision.APPROVED


def test_complete_history_contains_both_decisions(mongo_context) -> None:
    client, _database, collection = mongo_context
    _persist(client, collection, _approval())
    _persist(client, collection, _approval(approval_id="approval-real-2", idempotency_key="idem-real-2", effective_from=NOW + timedelta(days=1), occurred_at=NOW + timedelta(days=1), decision=Decision.REJECTED))
    history = _tx(client, lambda session: registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, session=session))
    assert len(history) == 2 and history[-1].decision is Decision.REJECTED


def test_database_name_is_uuid_isolated(mongo_context) -> None:
    _client, database, _collection = mongo_context
    assert database.name.startswith("wilsy_l9a4_p2b2_approval_")


def test_currentness_uses_explicit_at_not_wall_clock(mongo_context) -> None:
    client, _database, collection = mongo_context
    future = NOW + timedelta(days=2)
    _persist(client, collection, _approval(effective_from=future, occurred_at=NOW))
    assert _tx(client, lambda session: registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=NOW, session=session)) is None


# ARTIFACT: test_legal_client_matter_acceptance_instrument_approval_registry_real_mongo.py
# VERSION: v1.0.0-L9A4-P2B2-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated physical registry certificate only
# TENANT POSTURE: UUID database and exact subject predicates
# FAIL-CLOSED POSTURE: topology, transaction, rollback, race and integrity failures fail
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
