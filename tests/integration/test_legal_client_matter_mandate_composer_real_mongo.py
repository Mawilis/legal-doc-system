"""Real-Mongo certificate for client-matter mandate formation composition.

TITLE: WILSY OS Legal Client Matter Mandate Formation Composer Real-Mongo Certificate
VERSION: v1.0.0-L9B11-P2-RM-CLIENT-MATTER-MANDATE-FORMATION-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published mandate composer against real grant,
         lifecycle, acknowledgment and mandate registries inside UUID-isolated
         Mongo transactions. This certificate creates no currentness,
         lifecycle, Engagement, Representation, Court, IAM or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_mandate_composer_real_mongo.py
COLLABORATION / OWNERSHIP: Published registries own durable evidence and the
                            mandate domain owns immutable serialization. This
                            certificate owns only disposable test evidence.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B11-P2-RM certifies topology, caller-owned transactions,
           exact-session propagation, formation gating, lineage, replay,
           pair uniqueness, historical append-only formation, snapshots,
           concurrency, tenant isolation, corruption, BSON and no-TTL posture.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no URI,
                             credentials, bearer tokens, PII or canonical data
                             are printed or selected.
TENANT BOUNDARY: Every setup, read and formation operation is exact-tenant
                 scoped; overlapping opaque IDs are deliberately exercised.
AUTHORITY BOUNDARY: Real persistence certification for mandate formation only;
                    no downstream legal, IAM, HTTP, UI, Node or finance path.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: The test owns every session and transaction; the
                      composer and registries never own transaction lifecycle.
FAIL-CLOSED DECLARATION: Runtime, state, lineage, snapshot, corruption,
                         collision, isolation or mutation drift fails tests.
"""
from __future__ import annotations

import ast
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from typing import Any, Callable, Iterator
import uuid

import pytest
from pymongo import MongoClient, version as pymongo_version
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern

from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    LegalClientMatterMandateAcknowledgment,
    LegalClientMatterMandateAcknowledgmentDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_lifecycle import (
    LegalClientMatterMandateGrantLifecycleEvent,
    LegalClientMatterMandateGrantLifecycleReason,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_composer import (
    LegalClientMatterMandateComposer,
    LegalClientMatterMandateComposerError,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_grant_currentness_composer import (
    LegalClientMatterMandateGrantCurrentnessComposer,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_acknowledgment_currentness_composer import (
    LegalClientMatterMandateAcknowledgmentCurrentnessComposer,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_mandate_acknowledgment_registry as acknowledgment_registry,
    legal_client_matter_mandate_grant_lifecycle_registry as grant_lifecycle_registry,
    legal_client_matter_mandate_grant_registry as grant_registry,
    legal_client_matter_mandate_registry as mandate_registry,
    legal_operations_lifecycle_registry as matter_registry,
)
from tests.unit.test_legal_client_matter_mandate_grant import (
    capacity as capacity_factory,
    grant as grant_factory,
    matter as matter_factory,
    party as party_factory,
)
from tests.unit.test_legal_client_matter_mandate_grant_lifecycle import (
    event as lifecycle_event_factory,
)


VERSION = "v1.0.0-L9B11-P2-RM-CLIENT-MATTER-MANDATE-FORMATION-COMPOSER"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"
MONGO_VERSION = "7.0.37"
BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT_A = "tenant-l9b11-rm-a"
TENANT_B = "tenant-l9b11-rm-b"
FORBIDDEN_BSON_FIELDS = frozenset(
    {
        "password",
        "passwordHash",
        "jwt",
        "session_token",
        "refresh_token",
        "document_body",
        "raw_pii",
        "current",
        "currentness",
        "payment",
        "settlement",
        "financial_execution",
    }
)


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, dict[str, Any]]]:
    """Yield one fresh database and drop only that database afterward."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == REPLICA_SET
        assert hello.get("isWritablePrimary") is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert client.server_info().get("version") == MONGO_VERSION
        with client.start_session() as probe:
            probe.start_transaction(read_concern=ReadConcern("snapshot"))
            assert probe.in_transaction is True
            probe.abort_transaction()
        database_name = f"wilsy_l9b11_p2_mandate_cmp_{uuid.uuid4().hex}"
        assert len(database_name) <= 63
        database = client[database_name]
        collections = {
            "grant": database[grant_registry.COLLECTION],
            "grant_lifecycle": database[grant_lifecycle_registry.COLLECTION],
            "matter": database[matter_registry.COLLECTION],
            "ack": database[acknowledgment_registry.COLLECTION],
            "mandate": database[mandate_registry.COLLECTION],
        }
        grant_registry.ensure_indexes(collections["grant"])
        grant_lifecycle_registry.ensure_indexes(collections["grant_lifecycle"])
        matter_registry.LegalOperationsLifecycleRegistry.ensure_indexes(collections["matter"])
        acknowledgment_registry.ensure_indexes(collections["ack"])
        mandate_registry.ensure_indexes(collections["mandate"])
        yield client, database, collections
    except PyMongoError as error:
        pytest.fail(f"real Mongo prerequisite/certificate failure: {type(error).__name__}")
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _bundle(
    tenant: str,
    grant_id: str,
    *,
    matter_id: str = "matter-l9b11",
    grant_effective: datetime = BASE + timedelta(hours=1),
    grant_until: datetime | None = BASE + timedelta(days=30),
    acknowledgment_id: str = "ack-l9b11",
    decision: LegalClientMatterMandateAcknowledgmentDecision | None = LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED,
    acknowledgment_effective: datetime = BASE + timedelta(hours=4),
) -> tuple[CaseMatter, Any, LegalClientMatterMandateAcknowledgment | None]:
    """Build synthetic canonical matter, grant and optional acknowledgment."""
    source_matter = matter_factory(tenant_id=tenant, matter_id=matter_id)
    source_party = party_factory(source_matter=source_matter, party_id=f"party-{tenant}")
    source_capacity = capacity_factory(
        source_matter=source_matter,
        source_party=source_party,
        principal_id=f"principal-{tenant}",
    )
    source_grant = grant_factory(
        client_grant_id=grant_id,
        case_matter=source_matter,
        party=source_party,
        acting_capacity=source_capacity,
        effective_from=grant_effective,
        effective_until=grant_until,
        idempotency_key=f"grant:{tenant}:{grant_id}",
    )
    if decision is None:
        return source_matter, source_grant, None
    acknowledgment = LegalClientMatterMandateAcknowledgment.from_client_grant(
        client_grant=source_grant,
        acknowledgment_id=acknowledgment_id,
        decision=decision,
        decision_actor_principal_id=f"firm-principal-{tenant}",
        authorization_evidence_reference=f"firm-authorization:{tenant}",
        authorization_evidence_fingerprint="e" * 128,
        source_evidence_reference=f"firm-review:{tenant}",
        source_evidence_fingerprint="f" * 128,
        occurred_at=acknowledgment_effective - timedelta(minutes=1),
        effective_from=acknowledgment_effective,
        idempotency_key=f"ack:{tenant}:{acknowledgment_id}",
    )
    return source_matter, source_grant, acknowledgment


def _persist_bundle(
    client: MongoClient[Any],
    collections: dict[str, Any],
    bundle: tuple[CaseMatter, Any, LegalClientMatterMandateAcknowledgment | None],
    *,
    extra_matters: tuple[CaseMatter, ...] = (),
    events: tuple[Any, ...] = (),
    acknowledgments: tuple[LegalClientMatterMandateAcknowledgment, ...] = (),
) -> None:
    """Persist setup evidence through every published registry."""
    source_matter, source_grant, source_acknowledgment = bundle
    values = tuple(
        item
        for item in (source_acknowledgment, *acknowledgments)
        if item is not None
    )
    with client.start_session() as session:
        with session.start_transaction():
            matter_registry.LegalOperationsLifecycleRegistry.create(
                source_matter, collections["matter"], session=session
            )
            for matter_value in extra_matters:
                matter_registry.LegalOperationsLifecycleRegistry.create(
                    matter_value, collections["matter"], session=session
                )
            grant_registry.persist_grant(source_grant, collections["grant"], session=session)
            for event in events:
                grant_lifecycle_registry.persist_event(
                    event, collections["grant_lifecycle"], session=session
                )
            for acknowledgment in values:
                acknowledgment_registry.persist_acknowledgment(
                    acknowledgment, collections["ack"], session=session
                )


def _composer(collections: dict[str, Any]) -> LegalClientMatterMandateComposer:
    """Bind the published composer to disposable real collections."""
    return LegalClientMatterMandateComposer(
        grant_collection=collections["grant"],
        grant_lifecycle_collection=collections["grant_lifecycle"],
        matter_lifecycle_collection=collections["matter"],
        acknowledgment_collection=collections["ack"],
        mandate_collection=collections["mandate"],
    )


def _compose(
    client: MongoClient[Any],
    collections: dict[str, Any],
    tenant: str,
    grant_id: str,
    idempotency_key: str,
    *,
    read_concern: ReadConcern | None = None,
) -> Any:
    """Invoke one formation in a fresh caller-owned transaction."""
    composer = _composer(collections)
    with client.start_session() as session:
        session.start_transaction(read_concern=read_concern) if read_concern else session.start_transaction()
        try:
            value = composer.compose_mandate(
                tenant_id=tenant,
                client_grant_id=grant_id,
                idempotency_key=idempotency_key,
                session=session,
            )
            assert session.in_transaction is True
            session.commit_transaction()
            return value
        except BaseException:
            if session.in_transaction:
                session.abort_transaction()
            raise


def _event_for(
    source_grant: Any,
    event_id: str,
    *,
    event_type: LegalClientMatterMandateGrantLifecycleEvent,
    effective_from: datetime,
    successor_grant: Any | None = None,
) -> Any:
    """Build exact lifecycle evidence through its canonical factory."""
    superseded = event_type is LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED
    return lifecycle_event_factory(
        client_grant=source_grant,
        lifecycle_event_id=event_id,
        event=event_type,
        decision_actor_principal_id="firm-principal-l9b11",
        authorization_evidence_reference=f"lifecycle-authorization:{event_id}",
        authorization_evidence_fingerprint="a" * 128,
        source_evidence_reference=f"lifecycle-source:{event_id}",
        source_evidence_fingerprint="b" * 128,
        occurred_at=effective_from - timedelta(minutes=1),
        effective_from=effective_from,
        idempotency_key=f"lifecycle:{event_id}",
        reason=None if superseded else LegalClientMatterMandateGrantLifecycleReason.CLIENT_WITHDRAWAL,
        acting_capacity_id=None if superseded else "firm-capacity-l9b11",
        acting_capacity_fingerprint=None if superseded else "c" * 128,
        successor_grant=successor_grant,
    )


def _instrument(monkeypatch: pytest.MonkeyPatch, calls: list[tuple[str, int]]) -> None:
    """Record real registry/currentness session identity without replacing them."""
    original_grant_get = grant_registry.get_grant
    original_ack_list = acknowledgment_registry.list_acknowledgments_for_grant
    original_grant_currentness = LegalClientMatterMandateGrantCurrentnessComposer.compose_currentness
    original_ack_currentness = LegalClientMatterMandateAcknowledgmentCurrentnessComposer.compose_currentness
    original_mandate_persist = mandate_registry.persist_mandate

    def grant_get(*args: Any, **kwargs: Any) -> Any:
        calls.append(("grant", id(kwargs["session"])))
        return original_grant_get(*args, **kwargs)

    def ack_list(*args: Any, **kwargs: Any) -> Any:
        calls.append(("ack_history", id(kwargs["session"])))
        return original_ack_list(*args, **kwargs)

    def grant_currentness(self: Any, *args: Any, **kwargs: Any) -> Any:
        calls.append(("grant_currentness", id(args[-1] if args else kwargs["session"])))
        return original_grant_currentness(self, *args, **kwargs)

    def ack_currentness(self: Any, *args: Any, **kwargs: Any) -> Any:
        calls.append(("ack_currentness", id(args[-1] if args else kwargs["session"])))
        return original_ack_currentness(self, *args, **kwargs)

    def mandate_persist(*args: Any, **kwargs: Any) -> Any:
        calls.append(("mandate_persist", id(kwargs["session"])))
        return original_mandate_persist(*args, **kwargs)

    monkeypatch.setattr(grant_registry, "get_grant", grant_get)
    monkeypatch.setattr(acknowledgment_registry, "list_acknowledgments_for_grant", ack_list)
    monkeypatch.setattr(LegalClientMatterMandateGrantCurrentnessComposer, "compose_currentness", grant_currentness)
    monkeypatch.setattr(LegalClientMatterMandateAcknowledgmentCurrentnessComposer, "compose_currentness", ack_currentness)
    monkeypatch.setattr(mandate_registry, "persist_mandate", mandate_persist)


def _assert_blocked(
    client: MongoClient[Any],
    collections: dict[str, Any],
    tenant: str,
    grant_id: str,
    key: str,
) -> None:
    """Require fail-closed composition and no mandate write."""
    with pytest.raises(LegalClientMatterMandateComposerError):
        _compose(client, collections, tenant, grant_id, key)
    assert collections["mandate"].count_documents({}) == 0


def test_real_mongo_topology_and_caller_transaction_boundary(mongo_context) -> None:
    """The fixture proves topology; the composer proves caller ownership."""
    client, _database, collections = mongo_context
    bundle = _bundle(TENANT_A, "grant-boundary")
    _persist_bundle(client, collections, bundle)
    composer = _composer(collections)
    with pytest.raises(LegalClientMatterMandateComposerError):
        composer.compose_mandate(
            tenant_id=TENANT_A,
            client_grant_id="grant-boundary",
            idempotency_key="no-session",
            session=None,
        )
    with client.start_session() as session:
        with pytest.raises(LegalClientMatterMandateComposerError):
            composer.compose_mandate(
                tenant_id=TENANT_A,
                client_grant_id="grant-boundary",
                idempotency_key="inactive",
                session=session,
            )


def test_real_mongo_valid_formation_session_lineage_scope_and_write_audit(
    mongo_context, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A valid chain writes exactly one mandate and preserves one session."""
    client, database, collections = mongo_context
    bundle = _bundle(TENANT_A, "grant-valid")
    assert bundle[2] is not None
    _persist_bundle(client, collections, bundle)
    calls: list[tuple[str, int]] = []
    _instrument(monkeypatch, calls)
    before = {name: collection.count_documents({}) for name, collection in collections.items()}
    value = _compose(client, collections, TENANT_A, "grant-valid", "mandate-key-valid")
    assert value.tenant_id == TENANT_A
    assert value.client_grant_reference == bundle[1].client_grant_id
    assert value.client_grant_fingerprint == bundle[1].fingerprint
    assert value.firm_acknowledgment_reference == bundle[2].acknowledgment_id
    assert value.firm_acknowledgment_fingerprint == bundle[2].fingerprint
    assert value.case_matter_id == bundle[1].case_matter_id
    assert value.client_party_id == bundle[1].client_party_id
    assert value.subject_identity_fingerprint == bundle[1].subject_identity_fingerprint
    assert value.scope_reference == bundle[1].scope_reference
    assert value.scope_fingerprint == bundle[1].scope_fingerprint
    assert value.capabilities == bundle[1].capabilities
    assert value.occurred_at == bundle[2].effective_from
    assert value.effective_from == bundle[2].effective_from
    after = {name: collection.count_documents({}) for name, collection in collections.items()}
    assert after["mandate"] == before["mandate"] + 1
    for name in ("grant", "grant_lifecycle", "matter", "ack"):
        assert after[name] == before[name]
    labels = {label for label, _session_id in calls}
    assert {"grant", "ack_history", "grant_currentness", "ack_currentness", "mandate_persist"} <= labels
    assert len({session_id for _label, session_id in calls}) == 1
    assert set(database.list_collection_names()) == {collection.name for collection in collections.values()}


@pytest.mark.parametrize(
    "decision",
    [
        LegalClientMatterMandateAcknowledgmentDecision.DECLINED,
        LegalClientMatterMandateAcknowledgmentDecision.REQUIRES_REVIEW,
    ],
)
def test_real_mongo_non_acknowledged_decisions_block(
    mongo_context, decision: LegalClientMatterMandateAcknowledgmentDecision
) -> None:
    """Declined and review decisions cannot form a mandate."""
    client, _database, collections = mongo_context
    _persist_bundle(client, collections, _bundle(TENANT_A, f"grant-{decision.value.lower()}", decision=decision))
    _assert_blocked(client, collections, TENANT_A, f"grant-{decision.value.lower()}", f"key-{decision.value.lower()}")


def test_real_mongo_no_decision_and_ambiguous_acknowledgment_block(mongo_context) -> None:
    """Absent history is NO_DECISION and equal-time conflicting decisions are ambiguous."""
    client, _database, collections = mongo_context
    no_decision = _bundle(TENANT_A, "grant-no-decision", decision=None)
    _persist_bundle(client, collections, no_decision)
    _assert_blocked(client, collections, TENANT_A, "grant-no-decision", "key-no-decision")

    ambiguous = _bundle(TENANT_A, "grant-ambiguous", acknowledgment_id="ack-ambiguous-a")
    second = LegalClientMatterMandateAcknowledgment.from_client_grant(
        client_grant=ambiguous[1],
        acknowledgment_id="ack-ambiguous-b",
        decision=LegalClientMatterMandateAcknowledgmentDecision.DECLINED,
        decision_actor_principal_id="firm-principal-ambiguous",
        authorization_evidence_reference="firm-authorization:ambiguous",
        authorization_evidence_fingerprint="1" * 128,
        source_evidence_reference="firm-review:ambiguous",
        source_evidence_fingerprint="2" * 128,
        occurred_at=BASE + timedelta(hours=3),
        effective_from=BASE + timedelta(hours=4),
        idempotency_key="ack:ambiguous:b",
    )
    _persist_bundle(client, collections, ambiguous, acknowledgments=(second,))
    _assert_blocked(client, collections, TENANT_A, "grant-ambiguous", "key-ambiguous")


@pytest.mark.parametrize("state", [
    "NOT_YET_EFFECTIVE", "EXPIRED", "REVOKED", "SUPERSEDED", "MATTER_CLOSED", "AMBIGUOUS",
])
def test_real_mongo_grant_currentness_states_block(mongo_context, state: str) -> None:
    """Every non-CURRENT grant state blocks mandate formation."""
    client, _database, collections = mongo_context
    grant_id = f"grant-{state.lower()}"
    if state == "NOT_YET_EFFECTIVE":
        bundle = _bundle(TENANT_A, grant_id, grant_effective=BASE + timedelta(hours=10))
        _persist_bundle(client, collections, bundle)
    elif state == "EXPIRED":
        bundle = _bundle(TENANT_A, grant_id, grant_until=BASE + timedelta(hours=3))
        _persist_bundle(client, collections, bundle)
    elif state == "MATTER_CLOSED":
        bundle = _bundle(TENANT_A, grant_id)
        closed = bundle[0].transition_to(CaseMatterState.CLOSED, evidence_reference="matter:closed", occurred_at=BASE + timedelta(hours=3))
        _persist_bundle(client, collections, bundle, extra_matters=(closed,))
    else:
        bundle = _bundle(TENANT_A, grant_id)
        events: list[Any] = []
        successor = None
        if state in {"SUPERSEDED", "AMBIGUOUS"}:
            successor = _bundle(TENANT_A, f"{grant_id}-successor")[1]
            events.append(_event_for(bundle[1], f"{grant_id}-superseded", event_type=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED, effective_from=BASE + timedelta(hours=3), successor_grant=successor))
        if state in {"REVOKED", "AMBIGUOUS"}:
            events.append(_event_for(bundle[1], f"{grant_id}-revoked", event_type=LegalClientMatterMandateGrantLifecycleEvent.REVOKED, effective_from=BASE + timedelta(hours=3)))
        _persist_bundle(client, collections, bundle, events=tuple(events))
    _assert_blocked(client, collections, TENANT_A, grant_id, f"key-{state.lower()}")


def test_real_mongo_corrupt_grant_ack_and_mandate_replay_fail_closed(mongo_context) -> None:
    """Strict hydration rejects corrupt upstream and existing mandate BSON."""
    client, _database, collections = mongo_context
    grant_bundle = _bundle(
        TENANT_A,
        "grant-corrupt-grant",
        acknowledgment_id="ack-corrupt-grant",
    )
    _persist_bundle(client, collections, grant_bundle)
    collections["grant"].update_one({"client_grant_id": "grant-corrupt-grant"}, {"$set": {"scope_fingerprint": "0" * 128}})
    _assert_blocked(client, collections, TENANT_A, "grant-corrupt-grant", "key-corrupt-grant")

    ack_bundle = _bundle(
        TENANT_A,
        "grant-corrupt-ack",
        acknowledgment_id="ack-corrupt-ack",
    )
    assert ack_bundle[2] is not None
    _persist_bundle(client, collections, ack_bundle)
    collections["ack"].update_one({"acknowledgment_id": ack_bundle[2].acknowledgment_id}, {"$set": {"decision": "CORRUPT_BLOCKED"}})
    _assert_blocked(client, collections, TENANT_A, "grant-corrupt-ack", "key-corrupt-ack")

    valid = _bundle(
        TENANT_A,
        "grant-corrupt-mandate",
        acknowledgment_id="ack-corrupt-mandate",
    )
    _persist_bundle(client, collections, valid)
    value = _compose(client, collections, TENANT_A, "grant-corrupt-mandate", "key-corrupt-mandate")
    collections["mandate"].update_one({"mandate_id": value.mandate_id}, {"$set": {"fingerprint": "0" * 128}})
    with pytest.raises(LegalClientMatterMandateComposerError):
        _compose(client, collections, TENANT_A, "grant-corrupt-mandate", "key-corrupt-mandate")


def test_real_mongo_replay_pair_uniqueness_and_historical_append_only(mongo_context) -> None:
    """Replay is exact, pair uniqueness is enforced, and history remains append-only."""
    client, _database, collections = mongo_context
    bundle = _bundle(TENANT_A, "grant-history")
    _persist_bundle(client, collections, bundle)
    first = _compose(client, collections, TENANT_A, "grant-history", "same-key")
    replay = _compose(client, collections, TENANT_A, "grant-history", "same-key")
    assert replay.to_dict() == first.to_dict()
    with pytest.raises(LegalClientMatterMandateComposerError):
        _compose(client, collections, TENANT_A, "grant-history", "different-key")
    successor_ack = LegalClientMatterMandateAcknowledgment.from_client_grant(
        client_grant=bundle[1],
        acknowledgment_id="ack-history-successor",
        decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED,
        decision_actor_principal_id="firm-principal-history",
        authorization_evidence_reference="firm-authorization:history-2",
        authorization_evidence_fingerprint="3" * 128,
        source_evidence_reference="firm-review:history-2",
        source_evidence_fingerprint="4" * 128,
        occurred_at=BASE + timedelta(hours=4, minutes=1),
        effective_from=BASE + timedelta(hours=5),
        idempotency_key="ack:history:successor",
    )
    _persist_bundle(client, collections, bundle, acknowledgments=(successor_ack,))
    with pytest.raises(LegalClientMatterMandateComposerError):
        _compose(client, collections, TENANT_A, "grant-history", "same-key")
    second = _compose(client, collections, TENANT_A, "grant-history", "history-key-2")
    assert second.firm_acknowledgment_fingerprint == successor_ack.fingerprint
    assert collections["mandate"].count_documents({"tenant_id": TENANT_A}) == 2
    assert collections["mandate"].count_documents({"mandate_id": first.mandate_id}) == 1


def test_real_mongo_snapshot_tenant_isolation_and_no_forbidden_authority(mongo_context) -> None:
    """Snapshot reads remain coherent and foreign tenant evidence is absent."""
    client, database, collections = mongo_context
    bundle_a = _bundle(TENANT_A, "overlap-grant", matter_id="overlap-matter")
    bundle_b = _bundle(TENANT_B, "overlap-grant", matter_id="overlap-matter")
    _persist_bundle(client, collections, bundle_a)
    _persist_bundle(client, collections, bundle_b)
    with client.start_session() as session_a:
        session_a.start_transaction(read_concern=ReadConcern("snapshot"))
        assert collections["grant"].count_documents({}, session=session_a) == 2
        revoke = _event_for(bundle_a[1], "snapshot-revoke", event_type=LegalClientMatterMandateGrantLifecycleEvent.REVOKED, effective_from=BASE + timedelta(hours=5))
        with client.start_session() as session_b:
            with session_b.start_transaction():
                grant_lifecycle_registry.persist_event(revoke, collections["grant_lifecycle"], session=session_b)
        result = _composer(collections).compose_mandate(tenant_id=TENANT_A, client_grant_id="overlap-grant", idempotency_key="snapshot-key", session=session_a)
        assert result.tenant_id == TENANT_A
        session_a.commit_transaction()
    with pytest.raises(LegalClientMatterMandateComposerError):
        _compose(client, collections, TENANT_A, "overlap-grant", "post-revoke-key")
    with pytest.raises(LegalClientMatterMandateComposerError):
        _compose(client, collections, TENANT_A, "tenant-b-only", "foreign-key")
    assert not database[mandate_registry.COLLECTION].find_one({"tenant_id": TENANT_A, "client_grant_id": "foreign"})


def test_real_mongo_concurrent_same_request_creates_one_semantic_row(mongo_context) -> None:
    """Independent caller transactions cannot create a semantic duplicate."""
    client, _database, collections = mongo_context
    bundle = _bundle(TENANT_A, "grant-concurrent")
    _persist_bundle(client, collections, bundle)

    def attempt(_: int) -> str:
        try:
            _compose(client, collections, TENANT_A, "grant-concurrent", "concurrent-key")
            return "COMMITTED"
        except LegalClientMatterMandateComposerError:
            return "REJECTED"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(attempt, (1, 2)))
    assert outcomes.count("COMMITTED") == 1
    assert collections["mandate"].count_documents({"tenant_id": TENANT_A}) == 1


def test_real_mongo_raw_bson_append_only_no_ttl_and_static_authority_audit(mongo_context) -> None:
    """Persisted BSON is bounded and the composer has no forbidden authority."""
    client, database, collections = mongo_context
    bundle = _bundle(TENANT_A, "grant-audit")
    _persist_bundle(client, collections, bundle)
    value = _compose(client, collections, TENANT_A, "grant-audit", "audit-key")
    row = collections["mandate"].find_one({"mandate_id": value.mandate_id})
    assert row is not None
    assert set(row) == set(value.to_dict()) | {"_id"}
    assert not FORBIDDEN_BSON_FIELDS & set(row)
    assert not any("expireAfterSeconds" in index for index in collections["mandate"].list_indexes())
    assert "legal_client_matter_mandate_currentness" not in database.list_collection_names()
    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_mandate_composer.py").read_text()
    tree = ast.parse(source)
    imported = {
        alias.name.lower()
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    assert not any(token in imported for token in {"iam", "conflict", "engagement", "representation", "court"})
    assert "datetime.now" not in source
    assert ".insert_one(" not in source
    assert ".update_one(" not in source
    assert ".delete_many(" not in source
    assert pymongo_version


def test_certificate_scope_and_sovereign_markers() -> None:
    """The certificate remains one real-Mongo file with no production edits."""
    source = Path(__file__).read_text()
    assert "VERSION: v1.0.0-L9B11-P2-RM-CLIENT-MATTER-MANDATE-FORMATION-COMPOSER" in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source
    assert "MONGO_URI" in source and "wilsy_l9b11_p2_mandate_cmp_" in source
    assert "LegalClientMatterMandateComposer" in source


# ARTIFACT: test_legal_client_matter_mandate_composer_real_mongo.py
# VERSION: v1.0.0-L9B11-P2-RM-CLIENT-MATTER-MANDATE-FORMATION-COMPOSER
# AUTHORITY BOUNDARY: disposable real-Mongo formation certificate only
# TENANT POSTURE: UUID-isolated exact-tenant evidence; canonical wilsy excluded
# FAIL-CLOSED POSTURE: runtime, transaction, lineage, replay and BSON drift fails
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
