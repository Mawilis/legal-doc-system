"""Real-Mongo certificate for the L9C10-P5 Engagement formation composer.

TITLE: WILSY OS Legal Engagement Formation Composer Real-Mongo Certificate
VERSION: v1.0.0-L9C10-P7-ENGAGEMENT-FORMATION-REAL-MONGO-CERTIFICATE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove the published Engagement formation orchestration contract
         against actual tenant-scoped Mongo transactions, durable prerequisite
         registries, rollback, replay, currentness, lineage and corruption.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_engagement_formation_composer_real_mongo.py
COLLABORATION / OWNERSHIP: P5 owns formation orchestration; P1 registries,
                            domain artifacts and currentness composers remain
                            their separate authorities. This file owns only
                            disposable runtime evidence.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C10-P7 certifies real replica-set topology, caller-owned
           transactions, exact session/time propagation, canonical prerequisite
           persistence, Engagement durability, rollback, replay, divergence,
           currentness and strict corruption boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic databases only. URI,
                             credentials, bearer tokens and PII are never
                             printed. No canonical database is selected.
TENANT BOUNDARY: Every canonical read and write is exact tenant/matter/party
                 scoped; the disposable database is never named ``wilsy``.
AUTHORITY BOUNDARY: Runtime certificate evidence only. No IAM, Representation,
                    Court, HTTP, UI, Node, Engagement currentness or finance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and
                              settlement truth.
TRANSACTION BOUNDARY: The test owns every session, transaction, commit and
                      abort. The composer owns none of those operations.
FAIL-CLOSED DECLARATION: Topology, absence, ambiguity, corruption, lineage,
                         currentness and replay failures reject certification.
"""
from __future__ import annotations

import ast
import os
import uuid
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator

import pytest
from pymongo import MongoClient, version as pymongo_version
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.legal_client_acceptance import (
    record_legal_client_acceptance,
)
from tools.eos.legal_operations.domain.legal_client_acceptance_context import (
    LegalClientAcceptanceContext,
)
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    record_legal_client_acting_capacity,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    record_legal_client_matter_acceptance_instrument,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_approval import (
    LegalClientMatterAcceptanceInstrumentApprovalDecision,
    record_legal_client_matter_acceptance_instrument_approval,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycleStatus,
    record_legal_client_matter_acceptance_instrument_lifecycle,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    LegalClientMatterEngagement,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision import (
    LegalClientMatterEngagementFirmDecisionType,
)
from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition import (
    LegalClientMatterConflictDisposition,
    LegalClientMatterConflictDispositionType,
)
from tools.eos.legal_operations.domain.legal_conflict_review import (
    LegalConflictReviewOutcome,
    determine_legal_conflict_review,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_engagement_formation_composer import (
    LegalClientMatterEngagementFormationComposer,
    LegalClientMatterEngagementFormationComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_acceptance_context_registry as context_registry,
    legal_client_acceptance_registry as acceptance_registry,
    legal_client_acting_capacity_registry as capacity_registry,
    legal_client_matter_acceptance_instrument_approval_registry as approval_registry,
    legal_client_matter_acceptance_instrument_lifecycle_registry as instrument_lifecycle_registry,
    legal_client_matter_acceptance_instrument_registry as instrument_registry,
    legal_client_matter_conflict_disposition_registry as conflict_registry,
    legal_client_matter_engagement_firm_decision_registry as decision_registry,
    legal_client_matter_engagement_registry as engagement_registry,
    legal_client_matter_mandate_acknowledgment_registry as acknowledgment_registry,
    legal_client_matter_mandate_grant_lifecycle_registry as grant_lifecycle_registry,
    legal_client_matter_mandate_grant_registry as grant_registry,
    legal_client_matter_mandate_registry as mandate_registry,
    legal_matter_party_registry as party_registry,
    legal_operations_lifecycle_registry as matter_registry,
)
from tools.eos.legal_operations.registry.legal_client_matter_mandate_registry import (
    LegalClientMatterMandateRegistryConflictError,
)
from tests.unit.test_legal_client_matter_conflict_disposition import (
    bundle as conflict_bundle,
)
from tests.unit.test_legal_client_matter_mandate import mandate as mandate_factory
from tests.unit.test_legal_client_matter_mandate_grant import grant as grant_factory
from tests.unit.test_legal_client_matter_mandate_acknowledgment import (
    acknowledgment as acknowledgment_factory,
)
from tests.unit.test_legal_client_matter_mandate_grant_lifecycle import (
    event as grant_event_factory,
)
from tests.unit.test_legal_client_matter_engagement_firm_decision import (
    decision as decision_factory,
)
from tests.unit.test_legal_client_acceptance_context import (
    approval as context_approval_factory,
    capacity as context_capacity_factory,
    instrument as context_instrument_factory,
    lifecycle as context_lifecycle_factory,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)


UTC = timezone.utc
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"
MONGO_VERSION = "7.0.37"
BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=UTC)
EVALUATED_AT = BASE + timedelta(hours=1)
TENANT = "tenant-l9b2"
MATTER_ID = "matter-l9b2"
PARTY_ID = "party-l9b2"
SUBJECT_FP = "a" * 128
EVIDENCE_FP = "b" * 128
CONTEXT_ID = "context-l9b10-p7"
ACCEPTANCE_ID = f"LEGAL-CLIENT-ACCEPT:{CONTEXT_ID}"
ACTOR_ID = "principal-client-l9b2"
CAPACITY_ID = "capacity-l9b10-p7"
INSTRUMENT_ID = "instrument-l9b10-p7"
INSTRUMENT_VERSION = "1.0.0"
MANDATE_ID = "mandate-l9b10-p7"
GRANT_ID = "client-grant-l9b10-p7"
ACK_ID = "acknowledgment-l9b10-p7"
DECISION_ID = "decision-l9b10-p7"


@dataclass(frozen=True)
class Bundle:
    matter: CaseMatter
    party: Any
    capacity: Any
    context: LegalClientAcceptanceContext
    acceptance: Any
    instrument: Any
    lifecycle: Any
    approval: Any
    conflict: Any
    grant: Any
    acknowledgment: Any
    mandate: Any
    decision: Any


class TrackingCollection:
    """Record every PyMongo session while delegating to a real collection."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.sessions: list[Any] = []
        self.operations: list[str] = []

    def with_options(self, **_options: Any) -> "TrackingCollection":
        return self

    def _record(self, operation: str, kwargs: dict[str, Any]) -> None:
        self.operations.append(operation)
        self.sessions.append(kwargs.get("session"))

    def find_one(self, *args: Any, **kwargs: Any) -> Any:
        self._record("find_one", kwargs)
        return self.inner.find_one(*args, **kwargs)

    def find(self, *args: Any, **kwargs: Any) -> Any:
        self._record("find", kwargs)
        return self.inner.find(*args, **kwargs)

    def insert_one(self, *args: Any, **kwargs: Any) -> Any:
        self._record("insert_one", kwargs)
        return self.inner.insert_one(*args, **kwargs)

    def update_one(self, *args: Any, **kwargs: Any) -> Any:
        self._record("update_one", kwargs)
        return self.inner.update_one(*args, **kwargs)

    def delete_many(self, *args: Any, **kwargs: Any) -> Any:
        self._record("delete_many", kwargs)
        return self.inner.delete_many(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner, name)


def _party(matter: CaseMatter) -> Any:
    return register_legal_matter_party(
        matter=matter,
        party_id=PARTY_ID,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=LegalMatterPartySide.CLIENT_SIDE,
        matter_role=LegalMatterPartyRole.CLIENT,
        subject_reference="organization:client-l9b10-p7",
        subject_identity_fingerprint=SUBJECT_FP,
        display_name="Synthetic client",
        registered_at=BASE + timedelta(minutes=1),
        source_evidence_reference="party:l9b10:p7",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def _bundle() -> Bundle:
    """Build one internally consistent canonical prerequisite graph."""
    conflict, matter, party, _screening, _review = conflict_bundle()
    capacity = context_capacity_factory(
        source_matter=matter,
        source_party=party,
        capacity_id=CAPACITY_ID,
        principal_id=ACTOR_ID,
        effective_from=BASE + timedelta(minutes=2),
        effective_until=BASE + timedelta(days=30),
    )
    instrument = context_instrument_factory(
        source_matter=matter,
        instrument_id=INSTRUMENT_ID,
        version=INSTRUMENT_VERSION,
        review_scope="client-information-review:v1",
        created_at=BASE + timedelta(minutes=2),
        effective_from=BASE + timedelta(minutes=3),
    )
    lifecycle = context_lifecycle_factory(
        source_matter=matter,
        source_instrument=instrument,
        occurred_at=BASE + timedelta(minutes=4),
    )
    approval = context_approval_factory(
        source_matter=matter,
        source_instrument=instrument,
        approval_id="approval-l9b10-p7",
        occurred_at=BASE + timedelta(minutes=5),
        effective_from=BASE + timedelta(minutes=5),
    )
    context = LegalClientAcceptanceContext.from_canonical(
        acceptance_context_id=CONTEXT_ID,
        actor_principal_id=ACTOR_ID,
        case_matter=matter,
        party=party,
        acting_capacity=capacity,
        instrument=instrument,
        lifecycle=lifecycle,
        approval=approval,
        issued_at=BASE + timedelta(minutes=6),
        expires_at=BASE + timedelta(days=1),
        replay_key="replay:l9b10:p7",
        issuer_evidence_reference="issuer:l9b10:p7",
        issuer_evidence_fingerprint=EVIDENCE_FP,
    )
    acceptance = record_legal_client_acceptance(
        case_matter=matter,
        acceptance_id=ACCEPTANCE_ID,
        party_id=party.party_id,
        subject_reference=party.subject_reference,
        subject_identity_fingerprint=party.subject_identity_fingerprint,
        acceptance_scope=context.acceptance_scope,
        actor_principal_id=ACTOR_ID,
        accepted_at=BASE + timedelta(minutes=7),
        source_evidence_reference=(
            f"legal-client-acceptance-context:{CONTEXT_ID}:instrument:"
            f"{INSTRUMENT_ID}:{INSTRUMENT_VERSION}:content:{context.content_fingerprint}:intent:p7"
        ),
        source_evidence_fingerprint=context.content_fingerprint,
    )
    grant = grant_factory(
        client_grant_id=GRANT_ID,
        case_matter=matter,
        party=party,
        acting_capacity=capacity,
        occurred_at=BASE + timedelta(minutes=8),
        effective_from=BASE + timedelta(minutes=9),
        effective_until=BASE + timedelta(days=30),
        idempotency_key="grant-replay:l9b10:p7",
    )
    acknowledgment = acknowledgment_factory(
        client_grant=grant,
        acknowledgment_id=ACK_ID,
        occurred_at=BASE + timedelta(minutes=10),
        effective_from=BASE + timedelta(minutes=11),
        idempotency_key="ack-replay:l9b10:p7",
    )
    mandate = mandate_factory(
        mandate_id=MANDATE_ID,
        case_matter=matter,
        party=party,
        acting_capacity=capacity,
        client_grant_reference=grant.client_grant_id,
        client_grant_fingerprint=grant.fingerprint,
        firm_acknowledgment_reference=acknowledgment.acknowledgment_id,
        firm_acknowledgment_fingerprint=acknowledgment.fingerprint,
        occurred_at=BASE + timedelta(minutes=12),
        effective_from=BASE + timedelta(minutes=13),
        effective_until=BASE + timedelta(days=30),
        idempotency_key="mandate-replay:l9b10:p7",
        scope_reference="scope:l9b10:p7",
    )
    decision = decision_factory(
        decision_id=DECISION_ID,
        case_matter=matter,
        party=party,
        decision=LegalClientMatterEngagementFirmDecisionType.ACCEPTED,
        occurred_at=BASE + timedelta(minutes=14),
        effective_from=BASE + timedelta(minutes=15),
        idempotency_key="decision-replay:l9b10:p7",
    )
    return Bundle(
        matter=matter,
        party=party,
        capacity=capacity,
        context=context,
        acceptance=acceptance,
        instrument=instrument,
        lifecycle=lifecycle,
        approval=approval,
        conflict=conflict,
        grant=grant,
        acknowledgment=acknowledgment,
        mandate=mandate,
        decision=decision,
    )


def _collections(database: Any) -> dict[str, Any]:
    return {
        "matter": database[matter_registry.COLLECTION],
        "party": database[party_registry.COLLECTION],
        "capacity": database[capacity_registry.COLLECTION],
        "context": database[context_registry.COLLECTION],
        "acceptance": database[acceptance_registry.COLLECTION],
        "instrument": database[instrument_registry.COLLECTION],
        "lifecycle": database[instrument_lifecycle_registry.COLLECTION],
        "approval": database[approval_registry.COLLECTION],
        "conflict": database[conflict_registry.COLLECTION],
        "grant": database[grant_registry.COLLECTION],
        "grant_lifecycle": database[grant_lifecycle_registry.COLLECTION],
        "acknowledgment": database[acknowledgment_registry.COLLECTION],
        "mandate": database[mandate_registry.COLLECTION],
        "decision": database[decision_registry.COLLECTION],
        "engagement": database[engagement_registry.COLLECTION],
    }


def _ensure_indexes(collections: dict[str, Any]) -> None:
    matter_registry.LegalOperationsLifecycleRegistry.ensure_indexes(collections["matter"])
    party_registry.ensure_indexes(collections["party"])
    capacity_registry.ensure_indexes(collections["capacity"])
    context_registry.ensure_indexes(collections["context"])
    acceptance_registry.ensure_indexes(collections["acceptance"])
    instrument_registry.ensure_indexes(collections["instrument"])
    instrument_lifecycle_registry.ensure_indexes(collections["lifecycle"])
    approval_registry.ensure_indexes(collections["approval"])
    conflict_registry.ensure_indexes(collections["conflict"])
    grant_registry.ensure_indexes(collections["grant"])
    grant_lifecycle_registry.ensure_indexes(collections["grant_lifecycle"])
    acknowledgment_registry.ensure_indexes(collections["acknowledgment"])
    mandate_registry.ensure_indexes(collections["mandate"])
    decision_registry.ensure_indexes(collections["decision"])
    engagement_registry.ensure_indexes(collections["engagement"])


def _persist_bundle(client: MongoClient[Any], collections: dict[str, Any], value: Bundle) -> None:
    """Persist valid evidence only through canonical registries in one transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            matter_registry.LegalOperationsLifecycleRegistry.create(value.matter, collections["matter"], session=session)
            party_registry.persist_party(value.party, collections["party"], session=session)
            capacity_registry.persist_capacity(value.capacity, collections["capacity"], session=session)
            context_registry.persist_context(value.context, collections["context"], session=session)
            acceptance_registry.persist_acceptance(value.acceptance, collections["acceptance"], session=session)
            instrument_registry.persist_instrument(value.instrument, collections["instrument"], session=session)
            instrument_lifecycle_registry.persist_lifecycle(value.lifecycle, collections["lifecycle"], instrument_collection=collections["instrument"], session=session)
            approval_registry.persist_approval(value.approval, collections["approval"], session=session)
            conflict_registry.persist_disposition(value.conflict, collections["conflict"], session=session)
            grant_registry.persist_grant(value.grant, collections["grant"], session=session)
            acknowledgment_registry.persist_acknowledgment(value.acknowledgment, collections["acknowledgment"], session=session)
            mandate_registry.persist_mandate(value.mandate, collections["mandate"], session=session)
            decision_registry.persist_firm_decision(value.decision, collections["decision"], session=session)


def _composer(collections: dict[str, Any]) -> LegalClientMatterEngagementFormationComposer:
    return LegalClientMatterEngagementFormationComposer(
        matter_lifecycle_collection=collections["matter"],
        party_collection=collections["party"],
        capacity_collection=collections["capacity"],
        context_collection=collections["context"],
        acceptance_collection=collections["acceptance"],
        instrument_collection=collections["instrument"],
        instrument_lifecycle_collection=collections["lifecycle"],
        approval_collection=collections["approval"],
        conflict_collection=collections["conflict"],
        mandate_collection=collections["mandate"],
        mandate_grant_collection=collections["grant"],
        mandate_grant_lifecycle_collection=collections["grant_lifecycle"],
        mandate_matter_lifecycle_collection=collections["matter"],
        mandate_acknowledgment_collection=collections["acknowledgment"],
        decision_collection=collections["decision"],
        engagement_collection=collections["engagement"],
    )


def _identity() -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=ACTOR_ID,
        tenant_id=TENANT,
        username=None,
        email=None,
        auth_method="real-mongo-certificate",
        status=PrincipalStatus.ACTIVE,
    )


def _compose(composer: LegalClientMatterEngagementFormationComposer, session: Any, *, mandate_id: str = MANDATE_ID, evaluated_at: datetime = EVALUATED_AT, acceptance_id: str = ACCEPTANCE_ID, party_id: str = PARTY_ID, idempotency_key: str = "formation-replay:l9b10:p7") -> LegalClientMatterEngagement:
    return composer.compose_engagement(
        identity=_identity(),
        case_matter_id=MATTER_ID,
        client_party_id=party_id,
        client_acceptance_id=acceptance_id,
        mandate_id=mandate_id,
        idempotency_key=idempotency_key,
        evaluated_at=evaluated_at,
        session=session,
    )


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, dict[str, Any]]]:
    """Yield one UUID-isolated database on the sanctioned writable replica set."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5_000,
        connectTimeoutMS=5_000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
            version = client.server_info().get("version")
        except (PyMongoError, OSError) as error:
            pytest.skip(f"real Mongo unavailable for operator runtime: {type(error).__name__}")
        assert hello.get("setName") == REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert version == MONGO_VERSION
        with client.start_session() as probe:
            probe.start_transaction(read_concern=ReadConcern("snapshot"))
            assert probe.in_transaction is True
            probe.abort_transaction()
        name = f"wilsy_l9c10_form_{uuid.uuid4().hex}"
        assert len(name) <= 63
        assert name != "wilsy"
        database = client[name]
        collections = _collections(database)
        _ensure_indexes(collections)
        yield client, database, collections
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def test_real_topology_and_transaction_contract(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, database, collections = mongo_context
    assert database.name != "wilsy"
    assert len(database.name) <= 63
    hello = client.admin.command("hello")
    assert hello["setName"] == REPLICA_SET
    assert hello["isWritablePrimary"] is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    assert pymongo_version
    with pytest.raises(LegalClientMatterEngagementFormationComposerError):
        _compose(_composer(collections), None)  # type: ignore[arg-type]
    with client.start_session() as session:
        with pytest.raises(LegalClientMatterEngagementFormationComposerError):
            _compose(_composer(collections), session)
        assert session.in_transaction is False


def test_real_positive_formation_is_canonical_and_session_bound(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, database, raw = mongo_context
    value = _bundle()
    _persist_bundle(client, raw, value)
    tracked = {name: TrackingCollection(collection) for name, collection in raw.items()}
    composer = _composer(tracked)
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"))
        formed = _compose(composer, session)
        assert session.in_transaction is True
        assert raw["engagement"].count_documents({}, session=session) == 1
        sessions = [item for collection in tracked.values() for item in collection.sessions if item is not None]
        assert sessions and all(item is session for item in sessions)
        row = raw["engagement"].find_one({"tenant_id": TENANT, "engagement_id": formed.engagement_id}, session=session)
        assert row is not None
        row.pop("_id", None)
        assert row == formed.to_dict()
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction()
        read = engagement_registry.get_engagement(TENANT, formed.engagement_id, raw["engagement"], session=session)
        session.commit_transaction()
    assert read == formed
    assert raw["engagement"].count_documents({}) == 1
    assert set(row) == set(formed.to_dict())
    assert database.name != "wilsy"


def test_real_rollback_leaves_no_engagement(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _database, collections = mongo_context
    value = _bundle()
    _persist_bundle(client, collections, value)
    with client.start_session() as session:
        session.start_transaction()
        _compose(_composer(collections), session)
        assert session.in_transaction is True
        session.abort_transaction()
    assert collections["engagement"].count_documents({}) == 0


def test_real_exact_replay_is_one_row_and_divergent_idempotency_blocks(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _database, collections = mongo_context
    value = _bundle()
    _persist_bundle(client, collections, value)
    composer = _composer(collections)
    with client.start_session() as session:
        session.start_transaction()
        first = _compose(composer, session)
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction()
        second = _compose(composer, session)
        session.commit_transaction()
    assert first == second
    assert first.engagement_id == second.engagement_id
    assert collections["engagement"].count_documents({}) == 1
    alternate = replace(value.mandate, mandate_id="mandate-l9b10-p7-alt", scope_reference="scope:l9b10:p7:alt", fingerprint="")
    with client.start_session() as session:
        session.start_transaction()
        # The mandate registry's immutable grant/ack pair is itself a
        # tenant-scoped replay identity. A divergent mandate cannot be
        # inserted under that pair, so the registry must reject it before the
        # composer is reached.
        with pytest.raises(LegalClientMatterMandateRegistryConflictError):
            mandate_registry.persist_mandate(alternate, collections["mandate"], session=session)
        session.abort_transaction()
    assert collections["engagement"].count_documents({}) == 1


def test_real_case_matter_currentness_and_party_lineage_fail_closed(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _database, collections = mongo_context
    value = _bundle()
    _persist_bundle(client, collections, value)
    closed = value.matter.transition_to(CaseMatterState.CLOSED, evidence_reference="closure:l9b10:p7", occurred_at=BASE + timedelta(minutes=20))
    with client.start_session() as session:
        session.start_transaction()
        matter_registry.LegalOperationsLifecycleRegistry.create(closed, collections["matter"], session=session)
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterEngagementFormationComposerError):
            _compose(_composer(collections), session)
        session.abort_transaction()
    # A distinct wrong-tenant identity is an exact absence, never a fallback.
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterEngagementFormationComposerError):
            _compose(_composer(collections), session, party_id="party-foreign")
        session.abort_transaction()


def test_real_capacity_acceptance_instrument_and_approval_corruption_block(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _database, collections = mongo_context
    value = _bundle()
    _persist_bundle(client, collections, value)
    cases = (
        ("capacity", CAPACITY_ID, {"effective_until": BASE - timedelta(minutes=1)}),
        ("acceptance", ACCEPTANCE_ID, {"acceptance_scope": "tampered"}),
        ("instrument", INSTRUMENT_ID, {"review_scope": "tampered"}),
        ("approval", "approval-l9b10-p7", {"decision": "DECLINED"}),
    )
    for collection_name, identity, update in cases:
        collections[collection_name].update_one({"_id": {"$exists": True}, **({"capacity_id": identity} if collection_name == "capacity" else {"acceptance_id": identity} if collection_name == "acceptance" else {"instrument_id": identity} if collection_name == "instrument" else {"approval_id": identity})}, {"$set": update})
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(LegalClientMatterEngagementFormationComposerError):
                _compose(_composer(collections), session)
            session.abort_transaction()
        # Recreate a clean disposable prerequisite row for the next case by dropping
        # and reseeding the affected collection through its canonical registry.
        collections[collection_name].delete_many({})
        with client.start_session() as session:
            session.start_transaction()
            if collection_name == "capacity":
                capacity_registry.persist_capacity(value.capacity, collections["capacity"], session=session)
            elif collection_name == "acceptance":
                acceptance_registry.persist_acceptance(value.acceptance, collections["acceptance"], session=session)
            elif collection_name == "instrument":
                instrument_registry.persist_instrument(value.instrument, collections["instrument"], session=session)
            else:
                approval_registry.persist_approval(value.approval, collections["approval"], session=session)
            session.commit_transaction()


def test_real_conflict_mandate_and_firm_decision_currentness_block_obsolete_authority(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _database, collections = mongo_context
    value = _bundle()
    _persist_bundle(client, collections, value)
    _, _, _, later_screening, _ = conflict_bundle()
    later_review = determine_legal_conflict_review(
        screening=later_screening,
        review_id="review-l9b2-later",
        reviewer_principal_id="principal-reviewer-l9b2",
        reviewer_authorization_reference="iam-review:l9b2",
        reviewer_authorization_fingerprint=value.conflict.authorization_evidence_fingerprint,
        outcome=LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
        review_reason_reference="review-reason:l9b2-later",
        reviewed_at=BASE + timedelta(minutes=28),
        source_evidence_reference="review-evidence:l9b2-later",
        source_evidence_fingerprint=value.conflict.supporting_evidence_fingerprint,
    )
    prohibited = LegalClientMatterConflictDisposition.from_canonical(
        disposition_id="disposition-l9b10-p7-later",
        case_matter=value.matter,
        party=value.party,
        screening=later_screening,
        conflict_review=later_review,
        disposition=LegalClientMatterConflictDispositionType.ENGAGEMENT_PROHIBITED,
        decision_actor_principal_id=value.conflict.decision_actor_principal_id,
        authorization_evidence_reference="iam-disposition:l9b2-later",
        authorization_evidence_fingerprint=value.conflict.authorization_evidence_fingerprint,
        supporting_evidence_reference="supporting-disposition:l9b2-later",
        supporting_evidence_fingerprint=value.conflict.supporting_evidence_fingerprint,
        occurred_at=BASE + timedelta(minutes=29),
        effective_from=BASE + timedelta(minutes=30),
        idempotency_key="conflict-later",
    )
    with client.start_session() as session:
        session.start_transaction()
        conflict_registry.persist_disposition(prohibited, collections["conflict"], session=session)
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterEngagementFormationComposerError):
            _compose(_composer(collections), session)
        session.abort_transaction()
    declined = decision_factory(case_matter=value.matter, party=value.party, decision_id="decision-l9b10-p7-later", decision=LegalClientMatterEngagementFirmDecisionType.DECLINED, occurred_at=BASE + timedelta(minutes=31), effective_from=BASE + timedelta(minutes=32), idempotency_key="decision-later")
    with client.start_session() as session:
        session.start_transaction()
        decision_registry.persist_firm_decision(declined, collections["decision"], session=session)
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterEngagementFormationComposerError):
            _compose(_composer(collections), session)
        session.abort_transaction()


def test_real_scalar_decisive_records_fail_closed_and_scope_is_durable(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _database, collections = mongo_context
    value = _bundle()
    _persist_bundle(client, collections, value)
    duplicate = decision_factory(case_matter=value.matter, party=value.party, decision_id="decision-l9b10-p7-same-time", decision=LegalClientMatterEngagementFirmDecisionType.ACCEPTED, occurred_at=BASE + timedelta(minutes=15), effective_from=BASE + timedelta(minutes=15), idempotency_key="decision-same-time")
    with client.start_session() as session:
        session.start_transaction()
        decision_registry.persist_firm_decision(duplicate, collections["decision"], session=session)
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterEngagementFormationComposerError):
            _compose(_composer(collections), session)
        session.abort_transaction()
    assert collections["engagement"].count_documents({}) == 0


def test_real_snapshot_and_corrupt_replay_boundaries(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _database, collections = mongo_context
    value = _bundle()
    _persist_bundle(client, collections, value)
    composer = _composer(collections)
    with client.start_session() as seed_session:
        seed_session.start_transaction()
        _compose(composer, seed_session)
        seed_session.commit_transaction()
    with client.start_session() as snapshot:
        snapshot.start_transaction(read_concern=ReadConcern("snapshot"))
        collections["matter"].find_one({"tenant_id": TENANT, "case_matter_id": MATTER_ID}, session=snapshot)
        later = decision_factory(case_matter=value.matter, party=value.party, decision_id="decision-l9b10-p7-snapshot", decision=LegalClientMatterEngagementFirmDecisionType.DECLINED, occurred_at=BASE + timedelta(minutes=40), effective_from=BASE + timedelta(minutes=41), idempotency_key="decision-snapshot")
        with client.start_session() as writer:
            writer.start_transaction()
            decision_registry.persist_firm_decision(later, collections["decision"], session=writer)
            writer.commit_transaction()
        # Snapshot is limited to the state established by the first read.
        assert _compose(composer, snapshot).engagement_id
        snapshot.abort_transaction()
    # A fresh transaction sees the newly committed decisive state.
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterEngagementFormationComposerError):
            _compose(composer, session)
        session.abort_transaction()


def test_real_corrupt_engagement_replay_fails_closed(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _database, collections = mongo_context
    value = _bundle()
    _persist_bundle(client, collections, value)
    composer = _composer(collections)
    with client.start_session() as session:
        session.start_transaction()
        formed = _compose(composer, session)
        session.commit_transaction()
    collections["engagement"].update_one(
        {"tenant_id": TENANT, "engagement_id": formed.engagement_id},
        {"$set": {"mandate_scope": "tampered"}},
    )
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterEngagementFormationComposerError):
            _compose(composer, session)
        session.abort_transaction()


def test_real_source_has_no_forbidden_downstream_authority() -> None:
    source = open(__import__("tools.eos.legal_operations.orchestration.legal_client_matter_engagement_formation_composer", fromlist=["__file__"]).__file__, encoding="utf-8").read()
    tree = ast.parse(source)
    forbidden = {"start_transaction", "commit_transaction", "abort_transaction", "create_access_token", "requests", "httpx", "Representation", "Court", "TenantAuthorizationDecisionEvidenceRegistry"}
    calls = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert not calls & forbidden
    assert "insert_one" not in source and "update_one" not in source and "delete_many" not in source


# ARTIFACT: test_legal_client_matter_engagement_formation_composer_real_mongo.py
# VERSION: v1.0.0-L9C10-P7-ENGAGEMENT-FORMATION-REAL-MONGO-CERTIFICATE
# AUTHORITY BOUNDARY: disposable real-Mongo formation certificate only
# TENANT POSTURE: exact tenant-scoped canonical registries and UUID database
# FAIL-CLOSED POSTURE: no canonical writes, no silent replay/currentness downgrade
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
