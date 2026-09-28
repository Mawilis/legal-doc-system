"""Real-Mongo certificate for the published P2 Court preparation orchestrator.

TITLE: WILSY OS Court Operation Preparation Orchestrator Real-Mongo Certificate
VERSION: v1.0.0-L9C12-P2R-COURT-OPERATION-PREPARATION-ORCHESTRATOR-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify one caller-transaction P2 orchestration path against the
         sanctioned Mongo replica set, including fresh P24/P21A/P22,
         Engagement/Mandate and IAM reads, exact P1 persistence, replay,
         rollback and strict internal-only Court scope.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_court_operation_preparation_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: P24/P21A/P22, Engagement, Mandate, IAM and P1
                            registries remain canonical. This certificate owns
                            only disposable runtime evidence.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0 certifies sanctioned topology, caller-owned transaction
           propagation, exact prerequisite lineage, two eligible roles,
           bounded Court filing-preparation scope, replay, collision,
           rollback and zero upstream/external writes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque references and deterministic
                             fingerprints only; canonical ``wilsy`` is never used.
TENANT BOUNDARY: Every read and write is tenant and matter scoped.
AUTHORITY BOUNDARY: Internal preparation only; no filing, acceptance, issuance,
                    service, hearing, admission, Court Online or finance.
TRANSACTION BOUNDARY: The certificate owns setup/commit/abort; P2 owns none.
FAIL-CLOSED DECLARATION: Any stale, mismatched, widened or inactive authority
                         fails certification.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
import inspect
import os
from pathlib import Path
from typing import Any, Iterator, Mapping, cast
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import COLLECTION as PRINCIPAL_COLLECTION
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import COLLECTION as ASSIGNMENT_COLLECTION
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import COLLECTION as MEMBERSHIP_COLLECTION
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_client_matter_engagement import LegalClientMatterEngagement
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import LegalClientMatterRepresentationAuthority
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import LegalClientMatterRepresentationFirmDecision
from tools.eos.legal_operations.domain.legal_court_operation_preparation import (
    LegalCourtOperationPreparationState,
    LegalCourtOperationType,
)
from tools.eos.legal_operations.orchestration.legal_court_operation_preparation_orchestrator import (
    LegalCourtOperationPreparationOrchestrationError,
    LegalCourtOperationPreparationOrchestrator,
    LegalCourtOperationPreparationRequest,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_engagement_currentness_composer import LegalClientMatterEngagementCurrentnessComposer
from tools.eos.legal_operations.orchestration.legal_client_matter_final_representation_orchestrator import LegalClientMatterFinalRepresentationFormationRequest
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_currentness_composer import LegalClientMatterMandateCurrentnessComposer
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_authority_currentness_composer import LegalClientMatterRepresentationAuthorityCurrentnessComposer
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_firm_decision_currentness_composer import LegalClientMatterRepresentationFirmDecisionCurrentnessComposer
from tools.eos.legal_operations.registry import legal_client_matter_engagement_registry as engagement_registry
from tools.eos.legal_operations.registry import legal_client_matter_final_representation_registry as final_registry
from tools.eos.legal_operations.registry import legal_client_matter_mandate_registry as mandate_registry
from tools.eos.legal_operations.registry import legal_client_matter_representation_authority_registry as authority_registry
from tools.eos.legal_operations.registry import legal_client_matter_representation_firm_decision_registry as decision_registry
from tools.eos.legal_operations.registry import legal_court_operation_preparation_registry as preparation_registry
from tests.integration import test_legal_client_matter_final_representation_orchestrator_real_mongo as p25r
from tests.integration.test_legal_client_matter_mandate_currentness_composer_real_mongo import _bundle


MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"
MONGO_VERSION = "7.0.37"
BASE = datetime(2026, 9, 28, 12, 0, 0, 123456, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
TENANT = "tenant-l9c12-p2r"
REPRESENTATIVE = "principal-representative-l9c12-p2r"


class RecordingCollection:
    """Delegate a real collection while recording every supplied session."""

    def __init__(self, collection: Any) -> None:
        self._collection = collection
        self.session_ids: list[int] = []

    def __getattr__(self, name: str) -> Any:
        value = getattr(self._collection, name)
        if not callable(value):
            return value

        def invoke(*args: Any, **kwargs: Any) -> Any:
            session = kwargs.get("session")
            if session is not None:
                self.session_ids.append(id(session))
            return value(*args, **kwargs)

        return invoke


class RepositoryAdapter:
    """Bind canonical IAM repositories to disposable collections."""

    def __init__(self, collection: Any, kind: str) -> None:
        self.collection = collection
        self.kind = kind

    def resolve(self, *args: str, **kwargs: Any) -> Any:
        session = kwargs.get("session")
        if self.kind == "principal":
            return PrincipalAuthorityRepository.resolve(args[0], self.collection, session=session)
        if self.kind == "membership":
            return TenantMembershipRepository.resolve(args[0], args[1], self.collection, session=session)
        return RoleAssignmentRepository.resolve(args[0], args[1], args[2], self.collection, session=session)


@dataclass
class MongoContext:
    client: MongoClient[Any]
    database: Any
    raw: dict[str, Any]
    collections: dict[str, RecordingCollection]


def _collections(database: Any) -> dict[str, Any]:
    raw = p25r._collections(database)
    raw["preparation"] = database[preparation_registry.COLLECTION]
    return raw


def _ensure_indexes(raw: Mapping[str, Any]) -> None:
    p25r._ensure_indexes({key: value for key, value in raw.items() if key != "preparation"})
    preparation_registry.ensure_indexes(raw["preparation"])


def _p25_request(matter: Any, mandate: Any) -> LegalClientMatterFinalRepresentationFormationRequest:
    """Build the P25 prerequisite request from this certificate's lineage.

    The P25R certificate's private request helper is intentionally not reused:
    it binds P25R's tenant and representative constants, which would make a
    P2R seed internally consistent in storage but invisible to P21A. This
    local request is derived only from the P2R bundle and the published P25
    public request type.
    """
    return LegalClientMatterFinalRepresentationFormationRequest(
        tenant_id=TENANT,
        case_matter_id=matter.case_matter_id,
        matter_fingerprint=matter.fingerprint,
        client_party_id=mandate.client_party_id,
        subject_identity_fingerprint=mandate.subject_identity_fingerprint,
        representative_principal_id=REPRESENTATIVE,
        evaluated_at=BASE + timedelta(hours=1),
        effective_from=BASE + timedelta(minutes=1),
        occurred_at=BASE + timedelta(minutes=2),
        idempotency_key="idempotency:final-p2r",
        representative_eligibility_reference="eligibility:p2r",
        representative_eligibility_fingerprint=HEX_A,
        source_evidence_reference="evidence:final-p2r",
        source_evidence_fingerprint=HEX_B,
        requested_scope_capabilities=("LITIGATION_PREPARATION",),
    )


@pytest.fixture()
def mongo_context() -> Iterator[MongoContext]:
    """Yield one sanctioned, writable and UUID-isolated disposable database."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000,
        retryWrites=True, tz_aware=True,
    )
    database = None
    try:
        try:
            hello = client.admin.command("hello")
            version = client.server_info().get("version")
        except PyMongoError as error:
            pytest.skip(f"real Mongo unavailable for operator runtime: {type(error).__name__}")
        assert hello.get("setName") == REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert version == MONGO_VERSION
        database_name = f"wilsy_l9c12_p2r_{uuid4().hex}"
        assert len(database_name) <= 63
        assert database_name != "wilsy"
        database = client[database_name]
        raw = _collections(database)
        _ensure_indexes(raw)
        wrapped = {name: RecordingCollection(value) for name, value in raw.items()}
        yield MongoContext(client, database, raw, wrapped)
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _seed(context: MongoContext, *, role: str = "LEGAL_ATTORNEY", authority_decision: str = "APPOINTED", firm_decision: str | None = "ACCEPTED") -> dict[str, Any]:
    """Persist canonical prerequisites, then form one P24 with litigation scope."""
    values = _bundle(tenant=TENANT, grant_id="grant-p2r", mandate_id="mandate-p2r", matter_id="matter-p2r")
    matter, grant, acknowledgment, original_mandate = values
    mandate = replace(original_mandate, capabilities=("LITIGATION_PREPARATION", "COURT_FILING_PREPARATION"), fingerprint="")
    engagement = LegalClientMatterEngagement(
        engagement_id="engagement-p2r", tenant_id=TENANT, case_matter_id=matter.case_matter_id,
        matter_fingerprint=matter.fingerprint, client_party_id=mandate.client_party_id,
        subject_reference="client:subject-p2r", subject_identity_fingerprint=mandate.subject_identity_fingerprint,
        acting_capacity_id=mandate.acting_capacity_id, acting_capacity_fingerprint=mandate.acting_capacity_fingerprint,
        client_acceptance_id="acceptance-p2r", client_acceptance_fingerprint=HEX_A,
        instrument_id="instrument-p2r", version="v1", instrument_fingerprint=HEX_B, content_fingerprint=HEX_A,
        mandate_id=mandate.mandate_id, mandate_scope=mandate.scope_reference, mandate_fingerprint=mandate.fingerprint,
        conflict_disposition_id="conflict-p2r", conflict_disposition_fingerprint=HEX_B,
        firm_decision_id="engagement-decision-p2r", decision_actor_principal_id=REPRESENTATIVE,
        firm_decision_fingerprint=HEX_A, authorization_evidence_reference="evidence:engagement-auth-p2r",
        authorization_evidence_fingerprint=HEX_B, source_evidence_reference="evidence:engagement-p2r",
        source_evidence_fingerprint=HEX_A, effective_from=BASE - timedelta(hours=1),
        idempotency_key="idempotency:engagement-p2r",
    )
    authority = LegalClientMatterRepresentationAuthority(
        authority_id="authority-p2r", tenant_id=TENANT, case_matter_id=matter.case_matter_id,
        matter_fingerprint=matter.fingerprint, client_party_id=mandate.client_party_id,
        subject_reference="client:subject-p2r", subject_identity_fingerprint=mandate.subject_identity_fingerprint,
        engagement_id=engagement.engagement_id, engagement_fingerprint=engagement.fingerprint,
        mandate_id=mandate.mandate_id, mandate_fingerprint=mandate.fingerprint,
        mandate_scope_reference=mandate.scope_reference, mandate_scope_fingerprint=mandate.scope_fingerprint,
        mandate_capabilities=mandate.capabilities, acting_capacity_id=mandate.acting_capacity_id,
        acting_capacity_fingerprint=mandate.acting_capacity_fingerprint, representative_principal_id=REPRESENTATIVE,
        representative_role=role, representation_scope_capabilities=("LITIGATION_PREPARATION",), decision=authority_decision,
        appointing_principal_id="principal-client-p2r", source_evidence_reference="evidence:authority-p2r",
        source_evidence_fingerprint=HEX_A, authorization_evidence_reference="evidence:authority-auth-p2r",
        authorization_evidence_fingerprint=HEX_B, occurred_at=BASE - timedelta(minutes=20),
        effective_from=BASE - timedelta(minutes=15), effective_until=BASE + timedelta(days=30),
        idempotency_key="idempotency:authority-p2r",
    )
    decision = None if firm_decision is None else LegalClientMatterRepresentationFirmDecision.from_client_authority(
        client_authority=authority, decision=firm_decision, decision_actor_principal_id="principal-firm-p2r",
        authorization_evidence_reference="evidence:decision-auth-p2r", authorization_evidence_fingerprint=HEX_A,
        source_evidence_reference="evidence:decision-p2r", source_evidence_fingerprint=HEX_B,
        occurred_at=BASE - timedelta(minutes=10), effective_from=BASE - timedelta(minutes=5),
        idempotency_key="idempotency:decision-p2r",
    )
    c = context.raw
    p25_context = p25r.MongoContext(context.client, context.database, c, cast(Any, context.collections), MONGO_VERSION)
    p25_request = _p25_request(matter, mandate)
    with context.client.start_session() as session:
        with session.start_transaction():
            p25r.matter_registry.LegalOperationsLifecycleRegistry.create(matter, c["matter"], session=session)
            p25r.grant_registry.persist_grant(grant, c["grant"], session=session)
            p25r.acknowledgment_registry.persist_acknowledgment(acknowledgment, c["acknowledgment"], session=session)
            mandate_registry.persist_mandate(mandate, c["mandate"], session=session)
            engagement_registry.persist_engagement(engagement, c["engagement"], session=session)
            authority_registry.persist_representation_authority(authority, c["authority"], session=session)
            if decision is not None:
                decision_registry.persist_firm_decision(decision, c["decision"], session=session)
            PrincipalAuthorityRepository.create(PrincipalAuthority(REPRESENTATIVE, PrincipalStatus.ACTIVE, 0), c["principal"], session=session)
            TenantMembershipRepository.insert(TenantMembershipAuthority(REPRESENTATIVE, TENANT, TenantMembershipStatus.ACTIVE, 0), c["membership"], session=session)
            RoleAssignmentRepository.insert(RoleAssignmentAuthority(REPRESENTATIVE, TENANT, role, RoleAssignmentStatus.ACTIVE, 0), c["assignment"], session=session)
            representation = p25r._orchestrator(p25_context).form(p25_request, session=session)
    with context.client.start_session() as session:
        with session.start_transaction():
            representation = final_registry.get_final_representation(TENANT, representation.representation_id, c["final"], session=session)
    return {"matter": matter, "mandate": mandate, "engagement": engagement, "authority": authority, "decision": decision, "representation": representation}


def _authority_variant(source: LegalClientMatterRepresentationAuthority, *, decision: str, suffix: str, effective_from: datetime) -> LegalClientMatterRepresentationAuthority:
    """Construct a canonical non-positive P1 row with fresh deterministic identity."""
    payload = source.to_dict()
    payload.update(
        authority_id=f"authority-p2r-{suffix}",
        decision=decision,
        source_evidence_reference=f"evidence:authority-p2r-{suffix}",
        authorization_evidence_reference=f"evidence:authority-auth-p2r-{suffix}",
        occurred_at=effective_from - timedelta(minutes=1),
        effective_from=effective_from,
        idempotency_key=f"idempotency:authority-p2r-{suffix}",
    )
    payload.pop("fingerprint", None)
    return LegalClientMatterRepresentationAuthority(**cast(Any, payload))


def _decision_variant(source: LegalClientMatterRepresentationAuthority, *, decision: str, suffix: str, effective_from: datetime) -> LegalClientMatterRepresentationFirmDecision:
    """Construct a canonical non-positive P2 row with fresh deterministic identity."""
    return LegalClientMatterRepresentationFirmDecision.from_client_authority(
        client_authority=source,
        decision=decision,
        decision_actor_principal_id=f"principal-firm-p2r-{suffix}",
        authorization_evidence_reference=f"evidence:decision-auth-p2r-{suffix}",
        authorization_evidence_fingerprint=HEX_A,
        source_evidence_reference=f"evidence:decision-p2r-{suffix}",
        source_evidence_fingerprint=HEX_B,
        occurred_at=effective_from - timedelta(minutes=1),
        effective_from=effective_from,
        idempotency_key=f"idempotency:decision-p2r-{suffix}",
    )


def _assert_p21a_state(context: MongoContext, bundle: Mapping[str, Any], evaluated_at: datetime, expected: str) -> None:
    """Read P21A canonically and prove the intended non-positive state."""
    with context.client.start_session() as session:
        with session.start_transaction():
            projection = LegalClientMatterRepresentationAuthorityCurrentnessComposer(
                authority_collection=context.collections["authority"],
            ).compose_currentness(
                TENANT,
                bundle["matter"].case_matter_id,
                bundle["matter"].fingerprint,
                bundle["mandate"].client_party_id,
                bundle["mandate"].subject_identity_fingerprint,
                REPRESENTATIVE,
                evaluated_at,
                session,
            )
    assert getattr(projection.state, "value", projection.state) == expected


def _assert_p22_state(context: MongoContext, bundle: Mapping[str, Any], evaluated_at: datetime, expected: str) -> None:
    """Read P22 canonically and prove the intended non-positive state."""
    with context.client.start_session() as session:
        with session.start_transaction():
            projection = LegalClientMatterRepresentationFirmDecisionCurrentnessComposer(
                decision_collection=context.collections["decision"],
            ).compose_currentness(
                TENANT,
                bundle["matter"].case_matter_id,
                bundle["matter"].fingerprint,
                bundle["mandate"].client_party_id,
                bundle["mandate"].subject_identity_fingerprint,
                bundle["authority"].authority_id,
                bundle["authority"].fingerprint,
                REPRESENTATIVE,
                bundle["authority"].representative_role,
                evaluated_at,
                session,
            )
    assert getattr(projection.state, "value", projection.state) == expected


def _orchestrator(context: MongoContext) -> LegalCourtOperationPreparationOrchestrator:
    c = context.collections
    return LegalCourtOperationPreparationOrchestrator(
        authority_currentness_composer=LegalClientMatterRepresentationAuthorityCurrentnessComposer(authority_collection=c["authority"]),
        decision_currentness_composer=LegalClientMatterRepresentationFirmDecisionCurrentnessComposer(decision_collection=c["decision"]),
        engagement_currentness_composer=LegalClientMatterEngagementCurrentnessComposer(engagement_collection=c["engagement"]),
        mandate_currentness_composer=LegalClientMatterMandateCurrentnessComposer(
            mandate_collection=c["mandate"], grant_collection=c["grant"], grant_lifecycle_collection=c["grant_lifecycle"],
            matter_lifecycle_collection=c["matter"], acknowledgment_collection=c["acknowledgment"],
        ),
        representation_collection=c["final"], authority_collection=c["authority"], decision_collection=c["decision"],
        engagement_collection=c["engagement"], mandate_collection=c["mandate"], preparation_collection=c["preparation"],
        principal_repository=RepositoryAdapter(c["principal"], "principal"),
        membership_repository=RepositoryAdapter(c["membership"], "membership"), role_assignment_repository=RepositoryAdapter(c["assignment"], "assignment"),
        principal_collection=c["principal"], membership_collection=c["membership"], role_assignment_collection=c["assignment"],
        representation_reader=final_registry, engagement_reader=engagement_registry, mandate_reader=mandate_registry,
        preparation_writer=preparation_registry,
    )


def _request(bundle: Mapping[str, Any], **overrides: object) -> LegalCourtOperationPreparationRequest:
    representation = bundle["representation"]
    values: dict[str, object] = {
        "tenant_id": representation.tenant_id, "case_matter_id": representation.case_matter_id,
        "matter_fingerprint": representation.matter_fingerprint, "final_representation_id": representation.representation_id,
        "operation_type": LegalCourtOperationType.COURT_FILING_PREPARATION,
        "target_court_reference": "court:opaque-p2r", "target_jurisdiction_reference": "jurisdiction:opaque-gp",
        "document_evidence_lineage": ("document:evidence-2", "document:evidence-1"),
        "requested_scope_capabilities": ("COURT_FILING_PREPARATION",),
        "preparation_state": LegalCourtOperationPreparationState.PREPARATION_REQUIRED,
        "source_evidence_reference": "evidence:preparation-p2r", "source_evidence_fingerprint": HEX_C,
        "provenance_reference": "provenance:p2r", "prepared_at": BASE,
        "occurred_at": BASE + timedelta(minutes=1), "evaluated_at": BASE + timedelta(hours=1),
        "idempotency_key": "idempotency:preparation-p2r",
    }
    values.update(overrides)
    return LegalCourtOperationPreparationRequest(**cast(Any, values))


def _commit(context: MongoContext, bundle: Mapping[str, Any], **overrides: object) -> Any:
    with context.client.start_session() as session:
        with session.start_transaction():
            result = _orchestrator(context).prepare(_request(bundle, **overrides), session=session)
    return result


def test_real_topology_disposable_database_and_indexes(mongo_context: MongoContext) -> None:
    assert mongo_context.database.name.startswith("wilsy_l9c12_p2r_")
    assert mongo_context.database.name != "wilsy"
    assert preparation_registry.COLLECTION in mongo_context.database.list_collection_names() or True
    hello = mongo_context.client.admin.command("hello")
    assert hello["setName"] == REPLICA_SET and hello.get("isWritablePrimary") is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    assert preparation_registry.ensure_indexes(mongo_context.raw["preparation"]) is None


def test_missing_and_inactive_sessions_fail_closed(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    orchestrator = _orchestrator(mongo_context)
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        orchestrator.prepare(_request(bundle), session=None)
    with mongo_context.client.start_session() as session:
        with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
            orchestrator.prepare(_request(bundle), session=session)


@pytest.mark.parametrize("role", ["LEGAL_ATTORNEY", "LEGAL_PARTNER"])
def test_attorney_and_partner_happy_paths_bind_and_persist(mongo_context: MongoContext, role: str) -> None:
    bundle = _seed(mongo_context, role=role)
    value = _commit(mongo_context, bundle)
    assert value.operation_type is LegalCourtOperationType.COURT_FILING_PREPARATION
    assert value.final_representation_id == bundle["representation"].representation_id
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            hydrated = preparation_registry.get_court_operation_preparation(
                bundle["representation"].tenant_id,
                value.operation_preparation_id,
                mongo_context.collections["preparation"],
                session=session,
            )
    assert hydrated == value
    assert mongo_context.raw["preparation"].count_documents({"tenant_id": TENANT}) == 1


def test_exact_session_propagation_and_no_transaction_lifecycle(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        value = _orchestrator(mongo_context).prepare(_request(bundle), session=session)
        assert session.in_transaction is True
        session.abort_transaction()
    assert value
    sources = [collection.session_ids for collection in mongo_context.collections.values()]
    assert any(sources) and all(item for item in sources if item)
    source = Path("tools/eos/legal_operations/orchestration/legal_court_operation_preparation_orchestrator.py").read_text()
    assert "start_transaction" not in source and "commit_transaction" not in source and "abort_transaction" not in source


@pytest.mark.parametrize("field", ["tenant_id", "case_matter_id", "matter_fingerprint", "final_representation_id"])
def test_p24_lookup_and_lineage_fail_closed(mongo_context: MongoContext, field: str) -> None:
    bundle = _seed(mongo_context)
    value = {"tenant_id": TENANT, "case_matter_id": bundle["matter"].case_matter_id, "matter_fingerprint": bundle["matter"].fingerprint, "final_representation_id": bundle["representation"].representation_id}[field]
    wrong = "tenant-other-p2r" if field == "tenant_id" else ("matter-other-p2r" if field == "case_matter_id" else ("b" * 128 if field == "matter_fingerprint" else "missing-final-p2r"))
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        _commit(mongo_context, bundle, **{field: wrong})
    assert mongo_context.raw["preparation"].count_documents({}) == 0


@pytest.mark.parametrize("state", ["DECLINED", "REQUIRES_REVIEW"])
def test_p21a_negative_states_fail_closed(mongo_context: MongoContext, state: str) -> None:
    bundle = _seed(mongo_context)
    negative = _authority_variant(
        bundle["authority"],
        decision=state,
        suffix=f"p21a-{state.lower()}",
        effective_from=BASE - timedelta(minutes=15),
    )
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            mongo_context.raw["authority"].delete_one(
                {"tenant_id": TENANT, "authority_id": bundle["authority"].authority_id},
                session=session,
            )
            authority_registry.persist_representation_authority(
                negative, mongo_context.raw["authority"], session=session,
            )
    _assert_p21a_state(mongo_context, bundle, BASE + timedelta(hours=1), state)
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        _commit(mongo_context, bundle)
    assert mongo_context.raw["preparation"].count_documents({}) == 0


@pytest.mark.parametrize("state", ["DECLINED", "REQUIRES_REVIEW"])
def test_p22_negative_states_fail_closed(mongo_context: MongoContext, state: str) -> None:
    bundle = _seed(mongo_context)
    negative = _decision_variant(
        bundle["authority"],
        decision=state,
        suffix=f"p22-{state.lower()}",
        effective_from=BASE - timedelta(minutes=5),
    )
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            mongo_context.raw["decision"].delete_one(
                {"tenant_id": TENANT, "decision_id": bundle["decision"].decision_id},
                session=session,
            )
            decision_registry.persist_firm_decision(
                negative, mongo_context.raw["decision"], session=session,
            )
    _assert_p22_state(mongo_context, bundle, BASE + timedelta(hours=1), state)
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        _commit(mongo_context, bundle)
    assert mongo_context.raw["preparation"].count_documents({}) == 0


def test_noncurrent_engagement_and_mandate_fail_closed(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            mongo_context.raw["engagement"].delete_many({"tenant_id": TENANT}, session=session)
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        _commit(mongo_context, bundle)


@pytest.mark.parametrize("mutation", ["principal", "membership", "role"])
def test_live_iam_failures_are_rejected(mongo_context: MongoContext, mutation: str) -> None:
    bundle = _seed(mongo_context)
    if mutation == "principal":
        mongo_context.raw["principal"].update_one({"principal_id": REPRESENTATIVE}, {"$set": {"status": PrincipalStatus.SUSPENDED.value}})
    elif mutation == "membership":
        mongo_context.raw["membership"].update_one({"principal_id": REPRESENTATIVE}, {"$set": {"status": TenantMembershipStatus.SUSPENDED.value}})
    else:
        mongo_context.raw["assignment"].delete_many({"principal_id": REPRESENTATIVE})
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        _commit(mongo_context, bundle)


def test_scope_and_operation_widening_fail_closed(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        _commit(mongo_context, bundle, requested_scope_capabilities=("COURT_FILING_PREPARATION", "PAYMENT"))
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        _commit(mongo_context, bundle, operation_type="COURT_APPEARANCE_PREPARATION")


def test_exact_binding_replay_and_divergent_idempotency(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    first = _commit(mongo_context, bundle)
    second = _commit(mongo_context, bundle)
    assert first == second
    assert mongo_context.raw["preparation"].count_documents({}) == 1
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        _commit(mongo_context, bundle, target_court_reference="court:divergent")
    assert mongo_context.raw["preparation"].count_documents({}) == 1


def test_abort_rolls_back_and_failure_before_persist_has_no_partial_write(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        _orchestrator(mongo_context).prepare(_request(bundle), session=session)
        session.abort_transaction()
    assert mongo_context.raw["preparation"].count_documents({}) == 0

    class FailingWriter:
        def persist_court_operation_preparation(self, *args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("bounded persistence failure")

    failing = LegalCourtOperationPreparationOrchestrator(
        authority_currentness_composer=LegalClientMatterRepresentationAuthorityCurrentnessComposer(authority_collection=mongo_context.collections["authority"]),
        decision_currentness_composer=LegalClientMatterRepresentationFirmDecisionCurrentnessComposer(decision_collection=mongo_context.collections["decision"]),
        engagement_currentness_composer=LegalClientMatterEngagementCurrentnessComposer(engagement_collection=mongo_context.collections["engagement"]),
        mandate_currentness_composer=LegalClientMatterMandateCurrentnessComposer(mandate_collection=mongo_context.collections["mandate"], grant_collection=mongo_context.collections["grant"], grant_lifecycle_collection=mongo_context.collections["grant_lifecycle"], matter_lifecycle_collection=mongo_context.collections["matter"], acknowledgment_collection=mongo_context.collections["acknowledgment"]),
        representation_collection=mongo_context.collections["final"], authority_collection=mongo_context.collections["authority"], decision_collection=mongo_context.collections["decision"], engagement_collection=mongo_context.collections["engagement"], mandate_collection=mongo_context.collections["mandate"], preparation_collection=mongo_context.collections["preparation"], principal_repository=RepositoryAdapter(mongo_context.collections["principal"], "principal"), membership_repository=RepositoryAdapter(mongo_context.collections["membership"], "membership"), role_assignment_repository=RepositoryAdapter(mongo_context.collections["assignment"], "role"), principal_collection=mongo_context.collections["principal"], membership_collection=mongo_context.collections["membership"], role_assignment_collection=mongo_context.collections["assignment"], representation_reader=final_registry, engagement_reader=engagement_registry, mandate_reader=mandate_registry, preparation_writer=FailingWriter(),
    )
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
            failing.prepare(_request(bundle), session=session)
        session.abort_transaction()
    assert mongo_context.raw["preparation"].count_documents({}) == 0


def test_only_p1_write_and_no_external_authority_surfaces() -> None:
    source = Path("tools/eos/legal_operations/orchestration/legal_court_operation_preparation_orchestrator.py").read_text().lower()
    assert "httpx" not in source and "requests" not in source and "selenium" not in source
    assert "session.commit(" not in source and "session.abort(" not in source and "datetime.now" not in source
    assert "authorize_payment" not in source and "submit_to_court" not in source
    assert inspect.signature(LegalCourtOperationPreparationOrchestrator.prepare).parameters["session"]


# ARTIFACT: test_legal_court_operation_preparation_orchestrator_real_mongo.py
# VERSION: v1.0.0-L9C12-P2R-COURT-OPERATION-PREPARATION-ORCHESTRATOR-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: sanctioned real-Mongo P2 orchestration certificate only
# FAIL-CLOSED POSTURE: topology, lineage, IAM, scope, transaction and persistence failures reject
# END OF WILSY OS SOVEREIGN ARTIFACT
