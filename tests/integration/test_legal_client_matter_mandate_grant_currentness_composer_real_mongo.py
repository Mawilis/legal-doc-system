"""Real-Mongo certificate for the published grant-currentness composer.

TITLE: WILSY OS Legal Client Matter Mandate Grant Currentness Composer Real Mongo Certificate
VERSION: v1.0.0-L9B9-P2-CLIENT-MANDATE-GRANT-CURRENTNESS-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify that one caller-owned Mongo transaction composes exact grant,
         immutable grant-lifecycle, and CaseMatter evidence into a read-only
         currentness projection without persisting currentness or consulting
         downstream legal, IAM, client, court, or financial authorities.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_mandate_grant_currentness_composer_real_mongo.py
COLLABORATION / OWNERSHIP: The published composer owns only transaction-scoped
                            composition; formation/lifecycle registries own
                            immutable evidence; this certificate owns no
                            production semantics.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B9-P2-CLIENT-MANDATE-GRANT-CURRENTNESS-REAL-MONGO-CERT
           certifies topology, caller-session propagation, snapshot behavior,
           every published currentness state, ambiguity, corruption, tenant
           isolation, exact time boundaries, determinism and read-only scope.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no canonical
                             database, credentials, PII, bearer tokens or
                             production secrets are read or printed.
TENANT BOUNDARY: Every formation, lifecycle, and CaseMatter read is exact
                 tenant-scoped; foreign evidence is represented as absence or
                 CORRUPT_BLOCKED, never as a cross-tenant oracle.
AUTHORITY BOUNDARY: Certification of published read-only currentness
                    composition only. No currentness persistence, mandate,
                    acknowledgment, Engagement, Representation, Court, IAM,
                    HTTP, UI, delivery, or financial authority.
TRANSACTION BOUNDARY: The test owns disposable Mongo sessions and transactions;
                      the composer never starts, commits, aborts, or retries.
FAIL-CLOSED DECLARATION: Wrong topology, torn reads, corruption, ambiguity,
                         scope divergence, mutation, or unexpected CURRENT
                         result fails this certificate.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_currentness import (
    LegalClientMatterMandateGrantCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_lifecycle import (
    LegalClientMatterMandateGrantLifecycleEvent,
    LegalClientMatterMandateGrantLifecycleReason,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_grant_currentness_composer import (
    LegalClientMatterMandateGrantCurrentnessComposer,
    LegalClientMatterMandateGrantCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_mandate_grant_lifecycle_registry as lifecycle_registry,
    legal_client_matter_mandate_grant_registry as grant_registry,
    legal_operations_lifecycle_registry as matter_registry,
)
from tests.unit.test_legal_client_matter_mandate_grant import (
    capacity,
    grant,
    matter,
    party,
)
from tests.unit.test_legal_client_matter_mandate_grant_lifecycle import event


VERSION = "v1.0.0-L9B9-P2-CLIENT-MANDATE-GRANT-CURRENTNESS-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"
T = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT_A = "tenant-l9b9-real-a"
TENANT_B = "tenant-l9b9-real-b"


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any, Any, Any]]:
    """Yield one UUID-isolated database and drop only that database."""
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
        database = client[f"wilsy_l9b9_cc_{uuid.uuid4().hex}"]
        grant_collection = database[grant_registry.COLLECTION]
        lifecycle_collection = database[lifecycle_registry.COLLECTION]
        matter_collection = database[matter_registry.COLLECTION]
        grant_registry.ensure_indexes(grant_collection)
        lifecycle_registry.ensure_indexes(lifecycle_collection)
        matter_registry.LegalOperationsLifecycleRegistry.ensure_indexes(matter_collection)
        yield client, database, grant_collection, lifecycle_collection, matter_collection
    except PyMongoError as error:
        pytest.fail(f"real Mongo prerequisite/certificate failure: {type(error).__name__}")
    finally:
        try:
            if database is not None:
                client.drop_database(database.name)
        finally:
            client.close()


def _grant_for(
    tenant: str,
    grant_id: str,
    matter_id: str = "matter-l9b9",
    *,
    effective_until: datetime | None = T + timedelta(days=30),
) -> Any:
    """Build one valid synthetic grant while allowing overlapping opaque IDs."""
    source = matter(tenant_id=tenant, matter_id=matter_id)
    subject = party(source_matter=source, party_id="party-l9b9")
    actor = capacity(source_matter=source, source_party=subject)
    return grant(
        client_grant_id=grant_id,
        case_matter=source,
        party=subject,
        acting_capacity=actor,
        idempotency_key=f"idempotency:{tenant}:{grant_id}",
        effective_until=effective_until,
    )


def _event_for(
    value: Any,
    event_id: str,
    *,
    event_type: LegalClientMatterMandateGrantLifecycleEvent = LegalClientMatterMandateGrantLifecycleEvent.REVOKED,
    effective_from: datetime = T + timedelta(days=1),
    successor: Any | None = None,
) -> Any:
    """Build one grant-bound event using the certified domain factory."""
    return event(
        client_grant=value,
        lifecycle_event_id=event_id,
        idempotency_key=f"idempotency:{event_id}",
        event=event_type,
        effective_from=effective_from,
        occurred_at=effective_from - timedelta(minutes=1),
        successor_grant=successor,
        reason=None if event_type is LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED else LegalClientMatterMandateGrantLifecycleReason.CLIENT_WITHDRAWAL,
        acting_capacity_id=None if event_type is LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED else "capacity-firm-l9b6",
        acting_capacity_fingerprint=None if event_type is LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED else "e" * 128,
    )


def _commit(client: MongoClient, operation: Any) -> None:
    """Run one setup write inside a caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            operation(session)


def _persist_matter(matter_value: CaseMatter, collection: Any, session: Any) -> None:
    matter_registry.LegalOperationsLifecycleRegistry.create(
        matter_value, collection, session=session
    )


def _persist_grant(value: Any, collection: Any, session: Any) -> None:
    grant_registry.persist_grant(value, collection, session=session)


def _persist_event(value: Any, collection: Any, session: Any) -> None:
    lifecycle_registry.persist_event(value, collection, session=session)


def _compose(
    client: MongoClient,
    composer: LegalClientMatterMandateGrantCurrentnessComposer,
    tenant: str,
    grant_id: str,
    at: datetime,
) -> Any:
    """Compose exactly once in a fresh caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            result = composer.compose_currentness(tenant, grant_id, at, session)
            assert session.in_transaction is True
            return result


def test_real_mongo_currentness_composer_contract(mongo_context, monkeypatch) -> None:
    """Certify all published composition states against real Mongo evidence."""
    client, database, grant_collection, lifecycle_collection, matter_collection = mongo_context
    composer = LegalClientMatterMandateGrantCurrentnessComposer(
        grant_collection=grant_collection,
        lifecycle_collection=lifecycle_collection,
        matter_lifecycle_collection=matter_collection,
    )

    matter_reads: list[Any] = []
    read_sessions: list[Any] = []
    original_grant_read = grant_registry.get_grant
    original_lifecycle_read = lifecycle_registry.list_events_for_grant
    original_matter_read = matter_registry.LegalOperationsLifecycleRegistry.get_entity_history

    def spy_grant_read(*args: Any, **kwargs: Any) -> Any:
        read_sessions.append(kwargs["session"])
        return original_grant_read(*args, **kwargs)

    def spy_lifecycle_read(*args: Any, **kwargs: Any) -> Any:
        read_sessions.append(kwargs["session"])
        return original_lifecycle_read(*args, **kwargs)

    def spy_matter_read(*args: Any, **kwargs: Any) -> Any:
        matter_reads.append(args[2])
        read_sessions.append(kwargs["session"])
        return original_matter_read(*args, **kwargs)

    monkeypatch.setattr(grant_registry, "get_grant", spy_grant_read)
    monkeypatch.setattr(lifecycle_registry, "list_events_for_grant", spy_lifecycle_read)
    monkeypatch.setattr(
        matter_registry.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        staticmethod(spy_matter_read),
    )

    with pytest.raises(LegalClientMatterMandateGrantCurrentnessComposerError):
        composer.compose_currentness(TENANT_A, "missing", T, None)
    with client.start_session() as inactive:
        with pytest.raises(LegalClientMatterMandateGrantCurrentnessComposerError):
            composer.compose_currentness(TENANT_A, "missing", T, inactive)
    absent = _compose(client, composer, TENANT_A, "absent", T)
    assert absent.state is LegalClientMatterMandateGrantCurrentnessState.FORMATION_ABSENT
    assert absent.client_grant_fingerprint is None
    assert absent.case_matter_id is None
    assert absent.formation_fingerprint is None

    future = _grant_for(TENANT_A, "future", "matter-future")
    _commit(client, lambda session: _persist_grant(future, grant_collection, session))
    pre_window = _compose(client, composer, TENANT_A, "future", T)
    assert pre_window.state is LegalClientMatterMandateGrantCurrentnessState.NOT_YET_EFFECTIVE
    assert matter_reads == []

    expired_at = T + timedelta(hours=3)
    expired = _grant_for(TENANT_A, "expired", "matter-expired", effective_until=expired_at)
    _commit(client, lambda session: _persist_grant(expired, grant_collection, session))
    expired_result = _compose(client, composer, TENANT_A, "expired", expired_at)
    assert expired_result.state is LegalClientMatterMandateGrantCurrentnessState.EXPIRED
    assert matter_reads == []

    current = _grant_for(TENANT_A, "current", "matter-current")
    current_matter = matter(tenant_id=TENANT_A, matter_id="matter-current")
    _commit(client, lambda session: (_persist_matter(current_matter, matter_collection, session), _persist_grant(current, grant_collection, session)))
    current_result = _compose(client, composer, TENANT_A, "current", T + timedelta(hours=3))
    assert current_result.state is LegalClientMatterMandateGrantCurrentnessState.CURRENT
    assert current_result.client_grant_fingerprint == current.fingerprint
    assert current_result.matter_state_evidence_fingerprint == current_matter.fingerprint
    assert current_result.fingerprint == _compose(client, composer, TENANT_A, "current", T + timedelta(hours=3)).fingerprint

    future_event = _event_for(current, "future-event", effective_from=T + timedelta(days=2))
    _commit(client, lambda session: _persist_event(future_event, lifecycle_collection, session))
    assert _compose(client, composer, TENANT_A, "current", T + timedelta(hours=3)).state is LegalClientMatterMandateGrantCurrentnessState.CURRENT

    revoked = _grant_for(TENANT_A, "revoked", "matter-revoked")
    revoked_matter = matter(tenant_id=TENANT_A, matter_id="matter-revoked")
    revoked_event = _event_for(revoked, "revoked-event", effective_from=T + timedelta(hours=3))
    _commit(client, lambda session: (_persist_matter(revoked_matter, matter_collection, session), _persist_grant(revoked, grant_collection, session), _persist_event(revoked_event, lifecycle_collection, session)))
    revoked_result = _compose(client, composer, TENANT_A, "revoked", T + timedelta(hours=3))
    assert revoked_result.state is LegalClientMatterMandateGrantCurrentnessState.REVOKED
    assert revoked_result.decisive_lifecycle_evidence_fingerprints == (revoked_event.fingerprint,)

    superseded = _grant_for(TENANT_A, "superseded", "matter-superseded")
    successor = _grant_for(TENANT_A, "successor", "matter-superseded")
    superseded_matter = matter(tenant_id=TENANT_A, matter_id="matter-superseded")
    superseded_event = _event_for(
        superseded,
        "superseded-event",
        event_type=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED,
        effective_from=T + timedelta(hours=3),
        successor=successor,
    )
    _commit(client, lambda session: (_persist_matter(superseded_matter, matter_collection, session), _persist_grant(superseded, grant_collection, session), _persist_event(superseded_event, lifecycle_collection, session)))
    superseded_result = _compose(client, composer, TENANT_A, "superseded", T + timedelta(hours=3))
    assert superseded_result.state is LegalClientMatterMandateGrantCurrentnessState.SUPERSEDED
    assert superseded_result.successor_client_grant_id == successor.client_grant_id
    assert superseded_result.successor_client_grant_fingerprint == successor.fingerprint

    equal = _grant_for(TENANT_A, "equal", "matter-equal")
    equal_matter = matter(tenant_id=TENANT_A, matter_id="matter-equal")
    equal_at = T + timedelta(hours=3)
    equal_revoked = _event_for(equal, "equal-revoked", effective_from=equal_at)
    equal_successor = _grant_for(TENANT_A, "equal-successor", "matter-equal")
    equal_superseded = _event_for(equal, "equal-superseded", event_type=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED, effective_from=equal_at, successor=equal_successor)
    _commit(client, lambda session: (_persist_matter(equal_matter, matter_collection, session), _persist_grant(equal, grant_collection, session), _persist_event(equal_revoked, lifecycle_collection, session), _persist_event(equal_superseded, lifecycle_collection, session)))
    equal_result = _compose(client, composer, TENANT_A, "equal", equal_at)
    assert equal_result.state is LegalClientMatterMandateGrantCurrentnessState.AMBIGUOUS
    assert set(equal_result.decisive_lifecycle_evidence_fingerprints) == {equal_revoked.fingerprint, equal_superseded.fingerprint}

    fork = _grant_for(TENANT_A, "fork", "matter-fork")
    fork_matter = matter(tenant_id=TENANT_A, matter_id="matter-fork")
    fork_one = _grant_for(TENANT_A, "fork-one", "matter-fork")
    fork_two = _grant_for(TENANT_A, "fork-two", "matter-fork")
    fork_at = T + timedelta(hours=3)
    fork_event_one = _event_for(fork, "fork-one-event", event_type=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED, effective_from=fork_at, successor=fork_one)
    fork_event_two = _event_for(fork, "fork-two-event", event_type=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED, effective_from=fork_at, successor=fork_two)
    _commit(client, lambda session: (_persist_matter(fork_matter, matter_collection, session), _persist_grant(fork, grant_collection, session), _persist_event(fork_event_one, lifecycle_collection, session), _persist_event(fork_event_two, lifecycle_collection, session)))
    assert _compose(client, composer, TENANT_A, "fork", fork_at).state is LegalClientMatterMandateGrantCurrentnessState.AMBIGUOUS

    closed = _grant_for(TENANT_A, "closed", "matter-closed")
    open_matter = matter(tenant_id=TENANT_A, matter_id="matter-closed")
    closed_matter = open_matter.transition_to(CaseMatterState.CLOSED, evidence_reference="close:l9b9", occurred_at=T + timedelta(hours=3))
    _commit(client, lambda session: (_persist_matter(open_matter, matter_collection, session), _persist_matter(closed_matter, matter_collection, session), _persist_grant(closed, grant_collection, session)))
    closed_result = _compose(client, composer, TENANT_A, "closed", T + timedelta(hours=4))
    assert closed_result.state is LegalClientMatterMandateGrantCurrentnessState.MATTER_CLOSED
    assert closed_result.matter_state_evidence_fingerprint == closed_matter.fingerprint

    missing_matter = _grant_for(TENANT_A, "missing-matter", "matter-missing")
    _commit(client, lambda session: _persist_grant(missing_matter, grant_collection, session))
    missing_result = _compose(client, composer, TENANT_A, "missing-matter", T + timedelta(hours=3))
    assert missing_result.state is LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED

    corrupt = _grant_for(TENANT_A, "corrupt", "matter-corrupt")
    corrupt_matter = matter(tenant_id=TENANT_A, matter_id="matter-corrupt")
    _commit(client, lambda session: (_persist_matter(corrupt_matter, matter_collection, session), _persist_grant(corrupt, grant_collection, session)))
    grant_collection.update_one({"tenant_id": TENANT_A, "client_grant_id": "corrupt"}, {"$set": {"scope_fingerprint": "invalid"}})
    with pytest.raises(LegalClientMatterMandateGrantCurrentnessComposerError):
        _compose(client, composer, TENANT_A, "corrupt", T + timedelta(hours=3))

    lifecycle_corrupt = _grant_for(TENANT_A, "lifecycle-corrupt", "matter-lifecycle-corrupt")
    lifecycle_corrupt_matter = matter(tenant_id=TENANT_A, matter_id="matter-lifecycle-corrupt")
    lifecycle_corrupt_event = _event_for(
        lifecycle_corrupt,
        "lifecycle-corrupt-event",
        effective_from=T + timedelta(hours=3),
    )
    _commit(client, lambda session: (_persist_matter(lifecycle_corrupt_matter, matter_collection, session), _persist_grant(lifecycle_corrupt, grant_collection, session), _persist_event(lifecycle_corrupt_event, lifecycle_collection, session)))
    lifecycle_collection.update_one(
        {"tenant_id": TENANT_A, "lifecycle_event_id": "lifecycle-corrupt-event"},
        {"$set": {"event": "UNKNOWN"}},
    )
    lifecycle_corrupt_result = _compose(
        client, composer, TENANT_A, "lifecycle-corrupt", T + timedelta(hours=3)
    )
    assert lifecycle_corrupt_result.state is LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED

    malformed_matter = _grant_for(TENANT_A, "malformed-matter", "matter-malformed")
    malformed_matter_value = matter(tenant_id=TENANT_A, matter_id="matter-malformed")
    _commit(client, lambda session: (_persist_matter(malformed_matter_value, matter_collection, session), _persist_grant(malformed_matter, grant_collection, session)))
    matter_collection.update_one(
        {"tenant_id": TENANT_A, "entity_type": "CaseMatter", "entity_identity": "matter-malformed"},
        {"$set": {"p1_payload.state": "BROKEN"}},
    )
    malformed_result = _compose(
        client, composer, TENANT_A, "malformed-matter", T + timedelta(hours=3)
    )
    assert malformed_result.state is LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED

    wrong_tenant_grant = _grant_for(TENANT_A, "wrong-tenant-matter", "matter-wrong-tenant")
    wrong_tenant_matter = matter(tenant_id=TENANT_B, matter_id="matter-wrong-tenant")
    _commit(client, lambda session: (_persist_matter(wrong_tenant_matter, matter_collection, session), _persist_grant(wrong_tenant_grant, grant_collection, session)))
    wrong_tenant_result = _compose(
        client, composer, TENANT_A, "wrong-tenant-matter", T + timedelta(hours=3)
    )
    assert wrong_tenant_result.state is LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED

    wrong_id_grant = _grant_for(TENANT_A, "wrong-matter-id", "matter-wrong-id")
    wrong_id_matter = matter(tenant_id=TENANT_A, matter_id="different-matter-id")
    _commit(client, lambda session: (_persist_matter(wrong_id_matter, matter_collection, session), _persist_grant(wrong_id_grant, grant_collection, session)))
    wrong_id_result = _compose(
        client, composer, TENANT_A, "wrong-matter-id", T + timedelta(hours=3)
    )
    assert wrong_id_result.state is LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED

    tenant_b = _grant_for(TENANT_B, "current", "matter-current")
    tenant_b_matter = matter(tenant_id=TENANT_B, matter_id="matter-current")
    _commit(client, lambda session: (_persist_matter(tenant_b_matter, matter_collection, session), _persist_grant(tenant_b, grant_collection, session)))
    foreign = _compose(client, composer, TENANT_A, "current", T + timedelta(hours=3))
    assert foreign.client_grant_fingerprint == current.fingerprint
    assert foreign.client_grant_fingerprint != tenant_b.fingerprint
    assert _compose(client, composer, TENANT_B, "current", T + timedelta(hours=3)).client_grant_fingerprint == tenant_b.fingerprint

    boundary = _grant_for(TENANT_A, "boundary", "matter-boundary")
    boundary_matter = matter(tenant_id=TENANT_A, matter_id="matter-boundary")
    boundary_event = _event_for(boundary, "boundary-event", effective_from=boundary.effective_from + timedelta(hours=1))
    _commit(client, lambda session: (_persist_matter(boundary_matter, matter_collection, session), _persist_grant(boundary, grant_collection, session), _persist_event(boundary_event, lifecycle_collection, session)))
    assert _compose(client, composer, TENANT_A, "boundary", boundary.effective_from).state is LegalClientMatterMandateGrantCurrentnessState.CURRENT
    assert _compose(client, composer, TENANT_A, "boundary", boundary.effective_until).state is LegalClientMatterMandateGrantCurrentnessState.EXPIRED
    assert _compose(client, composer, TENANT_A, "boundary", boundary_event.effective_from).state is LegalClientMatterMandateGrantCurrentnessState.REVOKED

    snapshot = _grant_for(TENANT_A, "snapshot", "matter-snapshot")
    snapshot_matter = matter(tenant_id=TENANT_A, matter_id="matter-snapshot")
    _commit(client, lambda session: (_persist_matter(snapshot_matter, matter_collection, session), _persist_grant(snapshot, grant_collection, session)))
    with client.start_session() as session_a:
        with session_a.start_transaction():
            first = composer.compose_currentness(TENANT_A, "snapshot", T + timedelta(hours=3), session_a)
            closed_snapshot = snapshot_matter.transition_to(CaseMatterState.CLOSED, evidence_reference="snapshot-close", occurred_at=T + timedelta(hours=4))
            _commit(client, lambda session: _persist_matter(closed_snapshot, matter_collection, session))
            second = composer.compose_currentness(TENANT_A, "snapshot", T + timedelta(hours=3), session_a)
            assert first.state is second.state is LegalClientMatterMandateGrantCurrentnessState.CURRENT
        after = _compose(client, composer, TENANT_A, "snapshot", T + timedelta(hours=5))
        assert after.state is LegalClientMatterMandateGrantCurrentnessState.MATTER_CLOSED

    read_sessions.clear()
    with client.start_session() as session:
        with session.start_transaction():
            before_counts = (
                grant_collection.count_documents({}, session=session),
                lifecycle_collection.count_documents({}, session=session),
                matter_collection.count_documents({}, session=session),
            )
            result = composer.compose_currentness(TENANT_A, "current", T + timedelta(hours=3), session)
            assert result.state is LegalClientMatterMandateGrantCurrentnessState.CURRENT
            assert len(read_sessions) == 3
            assert read_sessions[0] is read_sessions[1] is read_sessions[2] is session
            assert before_counts == (
                grant_collection.count_documents({}, session=session),
                lifecycle_collection.count_documents({}, session=session),
                matter_collection.count_documents({}, session=session),
            )

    collections = set(database.list_collection_names())
    assert all("currentness" not in name for name in collections)
    assert database.name != "wilsy"
    assert grant_collection.count_documents({}) > 0
    assert lifecycle_collection.count_documents({}) > 0
    assert matter_collection.count_documents({}) > 0

    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_mandate_grant_currentness_composer.py").read_text()
    assert "commit_transaction" not in source
    assert "abort_transaction" not in source
    assert "insert_one" not in source
    assert "update_one" not in source
    assert "delete_one" not in source


# ARTIFACT: test_legal_client_matter_mandate_grant_currentness_composer_real_mongo.py
# VERSION: v1.0.0-L9B9-P2-CLIENT-MANDATE-GRANT-CURRENTNESS-REAL-MONGO-CERT
# RESULT: UUID-isolated real-Mongo composer certificate only
# END OF WILSY OS SOVEREIGN ARTIFACT
