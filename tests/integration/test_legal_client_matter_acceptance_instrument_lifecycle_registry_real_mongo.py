"""Isolated real-Mongo certificate for the P2A2 lifecycle registry.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument Lifecycle Registry Real-Mongo Certificate
VERSION: v1.0.0-L9A4-P2A2-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Direct physical certification of append-only lifecycle evidence.
EPITOME: Prove the sanctioned replica set, transactions, indexes, baseline and
         terminal transitions, replay, successor validation, isolation,
         corruption rejection, rollback and competing-consumer safety.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_acceptance_instrument_lifecycle_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Synthetic UUID-isolated database only; canonical
                            shared data and all broader authorities remain out
                            of scope.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2A2-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE-REGISTRY-REAL-MONGO-CERT
           proves physical append-only history, terminal uniqueness, replay,
           transaction rollback, successor verification and isolation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Loopback-only UUID database and synthetic opaque
                             values; no URI, credentials, tokens or PII output.
TENANT BOUNDARY: Every query and mutation is exact tenant/matter/instrument scoped.
AUTHORITY BOUNDARY: Lifecycle persistence only; no approval, acceptance or finance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import hashlib
import os
import uuid

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    LegalClientMatterAcceptanceInstrument,
    record_legal_client_matter_acceptance_instrument,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycle,
    LegalClientMatterAcceptanceInstrumentLifecycleStatus as Status,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry import (
    legal_client_matter_acceptance_instrument_lifecycle_registry as registry,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_acceptance_instrument_registry as instrument_registry,
)


UTC = timezone.utc
NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=UTC)


def _instrument(
    *,
    tenant: str = "tenant-real",
    matter_id: str = "matter-real",
    instrument_id: str = "instrument-real",
    version: str = "1.0.0",
    supersedes: str | None = None,
    content: bytes | None = None,
) -> LegalClientMatterAcceptanceInstrument:
    """Build one synthetic immutable instrument value."""
    content_bytes = content or f"content-{version}".encode()
    matter = CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"REF-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"intake:{matter_id}",
    )
    return record_legal_client_matter_acceptance_instrument(
        case_matter=matter,
        instrument_id=instrument_id,
        version=version,
        instrument_kind="MATTER_REVIEW",
        title="Matter Information Review",
        review_scope=f"Bounded review scope for {instrument_id} {version}.",
        content_reference=f"artifact:{matter_id}/{instrument_id}/{version}",
        content_fingerprint=hashlib.sha3_512(content_bytes).hexdigest(),
        created_at=NOW,
        effective_from=NOW + (timedelta(days=1) if version != "1.0.0" else timedelta(0)),
        approval_evidence_reference=f"approval:{matter_id}/{instrument_id}/{version}",
        approval_evidence_fingerprint=hashlib.sha3_512(f"approval-{version}".encode()).hexdigest(),
        supersedes_version_id=supersedes,
    )


def _lifecycle(
    value: LegalClientMatterAcceptanceInstrument,
    *,
    status: Status = Status.ACTIVE,
    prior_status: Status | None = None,
    occurred_at: datetime = NOW,
    successor: LegalClientMatterAcceptanceInstrument | None = None,
) -> LegalClientMatterAcceptanceInstrumentLifecycle:
    """Build lifecycle evidence for one exact instrument version."""
    return LegalClientMatterAcceptanceInstrumentLifecycle(
        tenant_id=value.tenant_id,
        case_matter_id=value.case_matter_id,
        matter_fingerprint=value.matter_fingerprint,
        instrument_id=value.instrument_id,
        version=value.version,
        instrument_fingerprint=value.fingerprint,
        status=status,
        prior_status=prior_status,
        occurred_at=occurred_at,
        lifecycle_evidence_reference=f"evidence:{value.instrument_id}:{value.version}:{status.value}",
        lifecycle_evidence_fingerprint=hashlib.sha3_512(
            f"evidence-{value.instrument_id}-{value.version}-{status.value}".encode()
        ).hexdigest(),
        superseding_version_id=None if successor is None else successor.version_id,
        superseding_instrument_fingerprint=None if successor is None else successor.fingerprint,
    )


@pytest.fixture()
def mongo_context():
    """Yield one UUID-isolated database and drop only that database."""
    uri = os.environ.get(
        "TEST_VENDOR_MONGO_URI",
        "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
    )
    client = MongoClient(uri, serverSelectionTimeoutMS=5_000)
    database = client[f"wilsy_l9a4_p2a2_lifecycle_{uuid.uuid4().hex}"]
    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or not hello.get("isWritablePrimary"):
            pytest.fail("L9A4_P2A2_REAL_MONGO_TOPOLOGY_INVALID")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("L9A4_P2A2_SESSIONS_UNAVAILABLE")
        lifecycle_collection = database[registry.COLLECTION]
        instrument_collection = database[instrument_registry.COLLECTION]
        registry.ensure_indexes(lifecycle_collection)
        instrument_registry.ensure_indexes(instrument_collection)
        yield client, database, lifecycle_collection, instrument_collection
    finally:
        client.drop_database(database.name)
        client.close()


def _transaction(client: MongoClient, callback):
    """Run one caller-owned transaction; the registry never owns lifecycle."""
    with client.start_session() as session:
        return session.with_transaction(callback)


def _persist_instrument(client: MongoClient, collection: object, value: LegalClientMatterAcceptanceInstrument) -> LegalClientMatterAcceptanceInstrument:
    """Persist a synthetic successor through the certified instrument registry."""
    return _transaction(
        client,
        lambda session: instrument_registry.persist_instrument(value, collection, session=session),
    )


def _persist_lifecycle(client: MongoClient, collection: object, value: LegalClientMatterAcceptanceInstrumentLifecycle, instrument_collection: object | None = None) -> LegalClientMatterAcceptanceInstrumentLifecycle:
    """Persist one lifecycle fact through a caller-owned transaction."""
    return _transaction(
        client,
        lambda session: registry.persist_lifecycle(
            value,
            collection,
            instrument_collection=instrument_collection,
            session=session,
        ),
    )


def test_real_topology_is_writable_replica_set_with_sessions(mongo_context) -> None:
    """Sanctioned loopback topology is a writable transaction-capable replica set."""
    client, _database, _lifecycle_collection, _instrument_collection = mongo_context
    hello = client.admin.command("hello")
    assert hello["setName"] == "wilsyVendorCertRS"
    assert hello["isWritablePrimary"] is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    with client.start_session() as session:
        with session.start_transaction():
            session.abort_transaction()


def test_real_indexes_are_exact_and_non_expiring(mongo_context) -> None:
    """Physical index metadata matches the append-only contract."""
    _client, _database, collection, _instrument_collection = mongo_context
    indexes = collection.index_information()
    assert indexes[registry.IDENTITY_INDEX_NAME]["unique"] is True
    assert indexes[registry.FINGERPRINT_INDEX_NAME]["unique"] is True
    assert indexes[registry.TERMINAL_INDEX_NAME]["unique"] is True
    assert indexes[registry.TERMINAL_INDEX_NAME]["partialFilterExpression"] == {
        "status": {"$in": ["SUPERSEDED", "RETIRED", "WITHDRAWN"]}
    }
    assert indexes[registry.HISTORY_INDEX_NAME].get("unique", False) is False
    assert indexes[registry.STATE_INDEX_NAME].get("unique", False) is False
    assert not any("expireAfterSeconds" in item for item in indexes.values())


def test_real_active_baseline_replay_current_and_microseconds(mongo_context) -> None:
    """ACTIVE is explicit, replay is one row, and UTC precision survives BSON."""
    client, _database, collection, _instrument_collection = mongo_context
    value = _instrument()
    event = _lifecycle(value)
    assert _persist_lifecycle(client, collection, event) == event
    assert _persist_lifecycle(client, collection, event) == event
    assert collection.count_documents({}) == 1
    current = _transaction(
        client,
        lambda session: registry.get_current_lifecycle(
            value.tenant_id,
            value.case_matter_id,
            value.instrument_id,
            value.version,
            collection,
            session=session,
        ),
    )
    assert current == event
    assert current is not None and current.occurred_at.microsecond == 123456


def test_real_terminal_transitions_and_current_state(mongo_context) -> None:
    """SUPERSEDED, RETIRED and WITHDRAWN each resolve as terminal current state."""
    client, _database, collection, instrument_collection = mongo_context
    first = _instrument(instrument_id="instrument-superseded")
    successor = _instrument(instrument_id="instrument-superseded", version="2.0.0", supersedes=first.version_id, content=b"successor")
    retired = _instrument(instrument_id="instrument-retired")
    withdrawn = _instrument(instrument_id="instrument-withdrawn")
    for value in (first, successor, retired, withdrawn):
        _persist_instrument(client, instrument_collection, value)
    _persist_lifecycle(client, collection, _lifecycle(first))
    superseded = _lifecycle(first, status=Status.SUPERSEDED, prior_status=Status.ACTIVE, occurred_at=NOW + timedelta(seconds=1), successor=successor)
    assert _persist_lifecycle(client, collection, superseded, instrument_collection) == superseded
    _persist_lifecycle(client, collection, _lifecycle(retired))
    retired_event = _lifecycle(retired, status=Status.RETIRED, prior_status=Status.ACTIVE)
    _persist_lifecycle(client, collection, retired_event)
    _persist_lifecycle(client, collection, _lifecycle(withdrawn))
    withdrawn_event = _lifecycle(withdrawn, status=Status.WITHDRAWN, prior_status=Status.ACTIVE)
    _persist_lifecycle(client, collection, withdrawn_event)
    for value, expected in ((first, superseded), (retired, retired_event), (withdrawn, withdrawn_event)):
        current = _transaction(client, lambda session, item=value: registry.get_current_lifecycle(item.tenant_id, item.case_matter_id, item.instrument_id, item.version, collection, session=session))
        assert current == expected
    assert instrument_collection.count_documents({}) == 4


def test_real_invalid_transitions_and_cross_scope_absence(mongo_context) -> None:
    """Baseline and terminal rules reject invalid history without cross-scope leakage."""
    client, _database, collection, _instrument_collection = mongo_context
    value = _instrument(instrument_id="instrument-invalid")
    terminal = _lifecycle(value, status=Status.RETIRED, prior_status=Status.ACTIVE)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError):
        _persist_lifecycle(client, collection, terminal)
    _persist_lifecycle(client, collection, _lifecycle(value))
    _persist_lifecycle(client, collection, terminal)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError):
        _persist_lifecycle(client, collection, _lifecycle(value))
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError):
        _persist_lifecycle(client, collection, _lifecycle(value, status=Status.WITHDRAWN, prior_status=Status.ACTIVE))
    assert _transaction(client, lambda session: registry.get_current_lifecycle("tenant-other", value.case_matter_id, value.instrument_id, value.version, collection, session=session)) is None
    assert _transaction(client, lambda session: registry.get_current_lifecycle(value.tenant_id, "matter-other", value.instrument_id, value.version, collection, session=session)) is None


def test_real_abort_leaves_zero_lifecycle_rows(mongo_context) -> None:
    """Caller abort removes an uncommitted baseline without registry cleanup."""
    client, _database, collection, _instrument_collection = mongo_context
    value = _instrument(instrument_id="instrument-abort")
    event = _lifecycle(value)
    with client.start_session() as session:
        session.start_transaction()
        registry.persist_lifecycle(event, collection, session=session)
        session.abort_transaction()
    assert collection.count_documents({"instrument_id": value.instrument_id}) == 0


def test_real_corruption_is_rejected_and_no_other_authority_rows_exist(mongo_context) -> None:
    """A tampered semantic field fails closed and no broader collection is created."""
    client, database, collection, _instrument_collection = mongo_context
    value = _instrument(instrument_id="instrument-corrupt")
    _persist_lifecycle(client, collection, _lifecycle(value))
    collection.update_one({"instrument_id": value.instrument_id}, {"$set": {"status": "RETIRED"}})
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError):
        _transaction(client, lambda session: registry.get_current_lifecycle(value.tenant_id, value.case_matter_id, value.instrument_id, value.version, collection, session=session))
    assert set(database.list_collection_names()) == {registry.COLLECTION, instrument_registry.COLLECTION}
    assert "legal_client_acceptances" not in database.list_collection_names()


def test_real_competing_identical_terminal_consumers_leave_one_row(mongo_context) -> None:
    """Concurrent identical terminal consumers cannot duplicate history."""
    client, _database, collection, _instrument_collection = mongo_context
    value = _instrument(instrument_id="instrument-identical")
    _persist_lifecycle(client, collection, _lifecycle(value))
    terminal = _lifecycle(value, status=Status.RETIRED, prior_status=Status.ACTIVE)

    def consume() -> str:
        try:
            _persist_lifecycle(client, collection, terminal)
            return "committed"
        except Exception:
            return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _item: consume(), (1, 2)))
    assert "committed" in results
    assert collection.count_documents({"instrument_id": value.instrument_id, "status": "RETIRED"}) == 1


def test_real_competing_divergent_terminals_cannot_both_commit(mongo_context) -> None:
    """Concurrent RETIRED/WITHDRAWN consumers yield at most one terminal row."""
    client, _database, collection, _instrument_collection = mongo_context
    value = _instrument(instrument_id="instrument-divergent")
    _persist_lifecycle(client, collection, _lifecycle(value))
    retired = _lifecycle(value, status=Status.RETIRED, prior_status=Status.ACTIVE)
    withdrawn = _lifecycle(value, status=Status.WITHDRAWN, prior_status=Status.ACTIVE)

    def consume(event: LegalClientMatterAcceptanceInstrumentLifecycle) -> str:
        try:
            _persist_lifecycle(client, collection, event)
            return "committed"
        except Exception:
            return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(consume, (retired, withdrawn)))
    assert results.count("committed") <= 1
    assert collection.count_documents({"instrument_id": value.instrument_id, "status": {"$in": ["RETIRED", "WITHDRAWN"]}}) <= 1


# ARTIFACT: test_legal_client_matter_acceptance_instrument_lifecycle_registry_real_mongo.py
# VERSION: v1.0.0-L9A4-P2A2-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated physical lifecycle registry certificate only
# TENANT POSTURE: UUID-isolated database and exact tenant/matter/instrument queries
# FAIL-CLOSED POSTURE: rollback/corruption/race/divergent terminal consumers cannot create dual truth
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
