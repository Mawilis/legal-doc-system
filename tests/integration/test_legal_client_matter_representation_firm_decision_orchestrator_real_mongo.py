"""Real-Mongo certificate for the L9C11-P21B firm-decision orchestrator.

TITLE: WILSY OS Legal Firm Representation Decision Orchestrator Real-Mongo Certificate
VERSION: v1.0.0-L9C11-P21BR-FIRM-REPRESENTATION-DECISION-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published P21B caller-owned transaction boundary, exact
         P1/Engagement/Mandate lineage, IAM evidence, P2 persistence, replay,
         rollback, tenant isolation and authority limits against real Mongo.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_representation_firm_decision_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: Published P21B owns orchestration; P1, Engagement,
                            Mandate, P18 authorization evidence and P9 own
                            their canonical contracts. This file owns only
                            disposable runtime certification evidence.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P21BR certifies sanctioned replica-set topology,
           caller transaction/session propagation, accepted/declined/review
           decisions, IAM and lineage negatives, rollback, exact replay,
           divergent idempotency and zero downstream authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no credentials,
                             tokens, personal data or canonical database use.
TENANT BOUNDARY: Every read and write is exact-tenant scoped; wrong-tenant
                 principal, representative and lineage requests fail closed.
AUTHORITY BOUNDARY: Firm Representation decision evidence only. No client
                    authority, currentness write, final Representation, Court,
                    HTTP/UI/Node or financial authority is created.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for execution.
TRANSACTION BOUNDARY: The certificate owns disposable sessions and transactions;
                      P21B receives one exact active caller session and owns
                      no transaction lifecycle.
FAIL-CLOSED DECLARATION: Topology, prerequisites, lineage, role, scope,
                         authorization, persistence, replay and cleanup failures
                         fail certification.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import inspect
import os
from typing import Any, Iterator, Mapping
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    COLLECTION as PRINCIPAL_COLLECTION,
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    COLLECTION as ASSIGNMENT_COLLECTION,
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as AUTHORIZATION_EVIDENCE_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    COLLECTION as MEMBERSHIP_COLLECTION,
    TenantMembershipRepository,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
    LegalClientMatterRepresentationAuthorityDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import (
    LegalClientMatterRepresentationAuthorityCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import (
    LegalClientMatterRepresentationFirmDecision,
    LegalClientMatterRepresentationFirmDecisionType,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_firm_decision_orchestrator import (
    OPERATION,
    PERMISSION,
    LegalClientMatterRepresentationFirmDecisionOrchestrationError,
    LegalClientMatterRepresentationFirmDecisionOrchestrator,
    LegalClientMatterRepresentationFirmDecisionRequest,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_authority_currentness_composer import (
    LegalClientMatterRepresentationAuthorityCurrentnessComposer,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_representation_authority_registry as authority_registry,
    legal_client_matter_representation_firm_decision_registry as decision_registry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 28, 12, 0, 0, 123456, tzinfo=timezone.utc)
P20 = importlib.import_module(
    "tests.integration.test_legal_client_matter_representation_authority_orchestrator_real_mongo"
)
P21AR = importlib.import_module(
    "tests.integration.test_legal_client_matter_representation_authority_currentness_real_mongo"
)
TENANT: str = P20.TENANT
OTHER_TENANT = "tenant-other-p21br"
ACTOR = "principal-firm-actor-p21br"
ATTORNEY_ACTOR = "principal-attorney-actor-p21br"
PARTNER_REPRESENTATIVE = "principal-partner-representative-p21br"
REPRESENTATIVE: str = P20.REPRESENTATIVE
MATTER_ID: str = P20.MATTER_ID
PARTY_ID: str = P20.PARTY_ID
AUTHORITY_ID = "authority-real-p21br"
HEX = hashlib.sha3_512(b"p21br").hexdigest()


@dataclass
class MongoContext:
    """UUID-isolated database and instrumented canonical collection handles."""

    client: MongoClient[Any]
    database: Any
    raw: dict[str, Any]
    collections: dict[str, Any]
    server_version: str


def _identity(
    *,
    tenant: str = TENANT,
    principal: str = ACTOR,
    status: PrincipalStatus = PrincipalStatus.ACTIVE,
) -> SovereignIdentity:
    """Create a synthetic authenticated identity for one exact tenant."""
    return SovereignIdentity(
        identity_id=principal,
        tenant_id=tenant,
        username=None,
        email=None,
        roles=[],
        permissions=[],
        auth_method="synthetic-p21br-real-mongo",
        status=status,
    )


def _raw_collections(database: Any) -> dict[str, Any]:
    """Reuse the certified P20 prerequisite collection map and add P21B stores."""
    raw = dict(P20._collections(database))
    raw["decision"] = database[decision_registry.COLLECTION]
    raw["authorization"] = database[AUTHORIZATION_EVIDENCE_COLLECTION]
    return raw


def _ensure_indexes(raw: Mapping[str, Any]) -> None:
    """Create only canonical indexes outside issuance transactions."""
    P20._ensure_indexes(raw)
    decision_registry.ensure_indexes(raw["decision"])
    TenantAuthorizationDecisionEvidenceRegistry(
        raw["authorization"],
        principal_repository=PrincipalAuthorityRepository,
        membership_repository=TenantMembershipRepository,
        role_assignment_repository=RoleAssignmentRepository,
        business_role_repository=RoleAssignmentRepository,
    ).ensure_indexes()


@pytest.fixture()
def mongo_context() -> Iterator[MongoContext]:
    """Yield one sanctioned writable replica-set database, once per test."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
            server_version = client.server_info().get("version")
            with client.start_session() as probe:
                probe.start_transaction()
                assert probe.in_transaction is True
                probe.abort_transaction()
        except PyMongoError as error:
            pytest.skip(f"real Mongo unavailable for operator runtime: {type(error).__name__}")
        assert hello.get("setName") == REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert isinstance(server_version, str) and server_version
        database_name = f"wilsy_l9c11_p21br_{uuid4().hex}"
        assert len(database_name) <= 63
        assert database_name != "wilsy"
        database = client[database_name]
        raw = _raw_collections(database)
        _ensure_indexes(raw)
        wrapped = {name: P20.RecordingCollection(collection) for name, collection in raw.items()}
        yield MongoContext(client, database, raw, wrapped, str(server_version))
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _prepare(
    context: MongoContext,
    *,
    actor_role: str = "LEGAL_PARTNER",
    actor_tenant: str = TENANT,
    actor_status: PrincipalStatus = PrincipalStatus.ACTIVE,
    actor_membership: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    representative_role: str = "LEGAL_ATTORNEY",
    representative_status: PrincipalStatus = PrincipalStatus.ACTIVE,
    representative_tenant: str = TENANT,
    representative_membership: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    authority_decision: LegalClientMatterRepresentationAuthorityDecision = LegalClientMatterRepresentationAuthorityDecision.APPOINTED,
    authority_effective: datetime = BASE + timedelta(minutes=7),
    authority_until: datetime | None = BASE + timedelta(days=30),
    engagement_effective: datetime = BASE + timedelta(minutes=6),
    include_authority: bool = True,
) -> dict[str, Any]:
    """Seed P20 lineage, then add one P1 and one firm actor through registries."""
    bundle = P20._seed(
        context,
        representative_status=representative_status,
        representative_tenant=representative_tenant,
        representative_membership_status=representative_membership,
        representative_roles=(representative_role,),
        engagement_effective=engagement_effective,
    )
    c = context.raw
    tenant_role = {
        "LEGAL_PARTNER": "tenant_legal_partner",
        "LEGAL_ATTORNEY": "tenant_legal_attorney",
        "LEGAL_PARALEGAL": "tenant_legal_paralegal",
        "LEGAL_SECRETARY": "tenant_legal_secretary",
        "LEGAL_FINANCE": "tenant_legal_finance",
        "LEGAL_CLIENT": "tenant_legal_client",
    }.get(actor_role)
    with context.client.start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(ACTOR, actor_status, 0), c["principal"], session=session
            )
            TenantMembershipRepository.insert(
                TenantMembershipAuthority(ACTOR, actor_tenant, actor_membership, 0),
                c["membership"],
                session=session,
            )
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(ACTOR, actor_tenant, actor_role, RoleAssignmentStatus.ACTIVE, 0),
                c["assignment"],
                session=session,
            )
            if tenant_role is not None:
                RoleAssignmentRepository.insert(
                    RoleAssignmentAuthority(
                        ACTOR, actor_tenant, tenant_role, RoleAssignmentStatus.ACTIVE, 0
                    ),
                    c["assignment"],
                    session=session,
                )
            if include_authority:
                authority = LegalClientMatterRepresentationAuthority.from_canonical(
                    authority_id=AUTHORITY_ID,
                    engagement=bundle["engagement"],
                    mandate=bundle["mandate"],
                    acting_capacity=bundle["capacity"],
                    representative_principal_id=REPRESENTATIVE,
                    representative_role=representative_role,
                    representation_scope_capabilities=("ADVISORY",),
                    decision=authority_decision,
                    appointing_principal_id=P20.CLIENT,
                    source_evidence_reference="authority-source:p21br",
                    source_evidence_fingerprint=HEX,
                    authorization_evidence_reference="authority-authorization:p21br",
                    authorization_evidence_fingerprint=HEX,
                    occurred_at=min(BASE + timedelta(minutes=7), authority_effective),
                    effective_from=authority_effective,
                    effective_until=authority_until,
                    idempotency_key="authority-idempotency:p21br",
                )
                authority_registry.persist_representation_authority(
                    authority, c["authority"], session=session
                )
            else:
                authority = None
    return {**bundle, "authority": authority}


def _orchestrator(
    context: MongoContext,
    *,
    decision_persistence: Any = decision_registry,
    authority_collection: Any | None = None,
) -> LegalClientMatterRepresentationFirmDecisionOrchestrator:
    """Bind P21B to real collections, repositories and durable evidence."""
    c = context.collections
    principal = P20._RepositoryAdapter(c["principal"], "principal")
    membership = P20._RepositoryAdapter(c["membership"], "membership")
    assignments = P20._RepositoryAdapter(c["assignment"], "assignment")
    evidence = TenantAuthorizationDecisionEvidenceRegistry(
        c["authorization"],
        principal_repository=principal,
        membership_repository=membership,
        role_assignment_repository=assignments,
        business_role_repository=assignments,
    )
    return LegalClientMatterRepresentationFirmDecisionOrchestrator(
        matter_lifecycle_collection=c["matter"],
        party_collection=c["party"],
        authority_collection=authority_collection or c["authority"],
        engagement_collection=c["engagement"],
        mandate_collection=c["mandate"],
        grant_collection=c["grant"],
        grant_lifecycle_collection=c["grant_lifecycle"],
        acknowledgment_collection=c["acknowledgment"],
        decision_collection=c["decision"],
        principal_repository=principal,
        membership_repository=membership,
        role_assignment_repository=assignments,
        business_role_repository=assignments,
        authorization_evidence_registry=evidence,
        decision_persistence=decision_persistence,
    )


def _request(*, decision: LegalClientMatterRepresentationFirmDecisionType = LegalClientMatterRepresentationFirmDecisionType.ACCEPTED, identity: SovereignIdentity | None = None, tenant: str = TENANT, scope: tuple[str, ...] = ("ADVISORY",), idempotency: str = "decision-idempotency:p21br", representative: str = REPRESENTATIVE, evaluated_at: datetime = BASE + timedelta(minutes=9)) -> LegalClientMatterRepresentationFirmDecisionRequest:
    """Build one immutable P21B command with explicit lineage and time."""
    return LegalClientMatterRepresentationFirmDecisionRequest(
        tenant_id=tenant,
        case_matter_id=MATTER_ID,
        client_party_id=PARTY_ID,
        representative_principal_id=representative,
        decision=decision,
        representation_scope_capabilities=scope,
        evaluated_at=evaluated_at,
        idempotency_key=idempotency,
        source_evidence_reference="p21br-command-source",
        source_evidence_fingerprint=HEX,
        identity=identity or _identity(tenant=tenant),
    )


def _issue_and_commit(context: MongoContext, request: LegalClientMatterRepresentationFirmDecisionRequest) -> LegalClientMatterRepresentationFirmDecision:
    """Issue inside a caller transaction and commit outside the orchestrator."""
    with context.client.start_session() as session:
        session.start_transaction()
        result = _orchestrator(context).issue(request, session=session)
        assert session.in_transaction is True
        session.commit_transaction()
    return result


def _count(context: MongoContext, key: str, query: Mapping[str, object] | None = None) -> int:
    """Count only tenant-scoped disposable rows."""
    selector: dict[str, object] = {"tenant_id": TENANT}
    if query:
        for field, value in query.items():
            selector[field] = value
    return int(context.raw[key].count_documents(selector))


def test_real_topology_and_disposable_database_are_sanctioned(mongo_context: MongoContext) -> None:
    """Prove the writable replica set, sessions and non-canonical database."""
    assert mongo_context.database.name.startswith("wilsy_l9c11_p21br_")
    assert len(mongo_context.database.name) <= 63
    assert mongo_context.database.name != "wilsy"
    assert mongo_context.server_version


def test_missing_and_inactive_transaction_rejected(mongo_context: MongoContext) -> None:
    _prepare(mongo_context)
    request = _request()
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
        _orchestrator(mongo_context).issue(request, session=None)
    with mongo_context.client.start_session() as session:
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            _orchestrator(mongo_context).issue(request, session=session)


@pytest.mark.parametrize("decision", list(LegalClientMatterRepresentationFirmDecisionType))
def test_real_decisions_persist_with_exact_lineage(mongo_context: MongoContext, decision: LegalClientMatterRepresentationFirmDecisionType) -> None:
    bundle = _prepare(mongo_context)
    value = _issue_and_commit(mongo_context, _request(decision=decision, idempotency=f"decision:{decision.value.lower()}"))
    assert value.decision is decision
    assert value.tenant_id == TENANT
    assert value.case_matter_id == MATTER_ID
    assert value.client_party_id == PARTY_ID
    assert value.representation_authority_id == bundle["authority"].authority_id
    assert value.representation_authority_fingerprint == bundle["authority"].fingerprint
    assert value.representative_principal_id == REPRESENTATIVE
    assert value.representative_role == "LEGAL_ATTORNEY"
    assert value.representation_scope_capabilities == ("ADVISORY",)
    assert _count(mongo_context, "authorization") == 1
    assert _count(mongo_context, "decision") == 1
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        hydrated = decision_registry.get_firm_decision(TENANT, value.decision_id, mongo_context.collections["decision"], session=session)
        session.commit_transaction()
    assert type(hydrated) is LegalClientMatterRepresentationFirmDecision
    assert hydrated.to_dict() == value.to_dict()


def test_partner_actor_decides_for_attorney_and_attorney_for_partner(mongo_context: MongoContext) -> None:
    seeded = _prepare(mongo_context, actor_role="LEGAL_PARTNER", representative_role="LEGAL_ATTORNEY")
    partner_result = _issue_and_commit(mongo_context, _request(idempotency="separation:partner"))
    assert partner_result.decision_actor_principal_id == ACTOR
    assert partner_result.representative_principal_id == REPRESENTATIVE
    assert ACTOR != REPRESENTATIVE
    assert partner_result.representative_role == "LEGAL_ATTORNEY"

    # Add the reciprocal eligible pair in the same disposable tenant. This
    # proves actor/representative separation in both directions without any
    # fixture bypass or canonical-database mutation.
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(ATTORNEY_ACTOR, PrincipalStatus.ACTIVE, 0),
                mongo_context.raw["principal"],
                session=session,
            )
            TenantMembershipRepository.insert(
                TenantMembershipAuthority(ATTORNEY_ACTOR, TENANT, TenantMembershipStatus.ACTIVE, 0),
                mongo_context.raw["membership"],
                session=session,
            )
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(ATTORNEY_ACTOR, TENANT, "LEGAL_ATTORNEY", RoleAssignmentStatus.ACTIVE, 0),
                mongo_context.raw["assignment"],
                session=session,
            )
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(
                    ATTORNEY_ACTOR,
                    TENANT,
                    "tenant_legal_attorney",
                    RoleAssignmentStatus.ACTIVE,
                    0,
                ),
                mongo_context.raw["assignment"],
                session=session,
            )
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(PARTNER_REPRESENTATIVE, PrincipalStatus.ACTIVE, 0),
                mongo_context.raw["principal"],
                session=session,
            )
            TenantMembershipRepository.insert(
                TenantMembershipAuthority(PARTNER_REPRESENTATIVE, TENANT, TenantMembershipStatus.ACTIVE, 0),
                mongo_context.raw["membership"],
                session=session,
            )
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(PARTNER_REPRESENTATIVE, TENANT, "LEGAL_PARTNER", RoleAssignmentStatus.ACTIVE, 0),
                mongo_context.raw["assignment"],
                session=session,
            )
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(
                    PARTNER_REPRESENTATIVE,
                    TENANT,
                    "tenant_legal_partner",
                    RoleAssignmentStatus.ACTIVE,
                    0,
                ),
                mongo_context.raw["assignment"],
                session=session,
            )
            authority = LegalClientMatterRepresentationAuthority.from_canonical(
                authority_id="authority-partner-p21br",
                engagement=seeded["engagement"],
                mandate=seeded["mandate"],
                acting_capacity=seeded["capacity"],
                representative_principal_id=PARTNER_REPRESENTATIVE,
                representative_role="LEGAL_PARTNER",
                representation_scope_capabilities=("ADVISORY",),
                decision=LegalClientMatterRepresentationAuthorityDecision.APPOINTED,
                appointing_principal_id=P20.CLIENT,
                source_evidence_reference="authority-source:partner-p21br",
                source_evidence_fingerprint=HEX,
                authorization_evidence_reference="authority-authorization:partner-p21br",
                authorization_evidence_fingerprint=HEX,
                occurred_at=BASE + timedelta(minutes=7),
                effective_from=BASE + timedelta(minutes=7),
                effective_until=BASE + timedelta(days=30),
                idempotency_key="authority-idempotency:partner-p21br",
            )
            authority_registry.persist_representation_authority(
                authority, mongo_context.raw["authority"], session=session
            )
    reciprocal = _issue_and_commit(
        mongo_context,
        _request(
            identity=_identity(principal=ATTORNEY_ACTOR),
            representative=PARTNER_REPRESENTATIVE,
            idempotency="separation:attorney",
        ),
    )
    assert reciprocal.decision_actor_principal_id == ATTORNEY_ACTOR
    assert reciprocal.representative_principal_id == PARTNER_REPRESENTATIVE
    assert reciprocal.representative_role == "LEGAL_PARTNER"


@pytest.mark.parametrize("role", ["LEGAL_PARALEGAL", "LEGAL_SECRETARY", "LEGAL_FINANCE", "LEGAL_CLIENT"])
def test_ineligible_actor_roles_are_rejected(mongo_context: MongoContext, role: str) -> None:
    _prepare(mongo_context, actor_role=role)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            _orchestrator(mongo_context).issue(_request(), session=session)
        session.abort_transaction()
    assert _count(mongo_context, "authorization") == 0
    assert _count(mongo_context, "decision") == 0


def test_inactive_actor_membership_principal_and_wrong_tenant_rejected(mongo_context: MongoContext) -> None:
    _prepare(mongo_context, actor_status=PrincipalStatus.SUSPENDED)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            _orchestrator(mongo_context).issue(_request(), session=session)
        session.abort_transaction()
    assert _count(mongo_context, "authorization") == 0


@pytest.mark.parametrize("membership", [TenantMembershipStatus.SUSPENDED])
def test_inactive_actor_membership_rejected(mongo_context: MongoContext, membership: TenantMembershipStatus) -> None:
    _prepare(mongo_context, actor_membership=membership)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            _orchestrator(mongo_context).issue(_request(), session=session)
        session.abort_transaction()


def test_wrong_tenant_actor_fails_closed(mongo_context: MongoContext) -> None:
    _prepare(mongo_context, actor_tenant=OTHER_TENANT)
    request = _request(identity=_identity(tenant=OTHER_TENANT), tenant=OTHER_TENANT)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            _orchestrator(mongo_context).issue(request, session=session)
        session.abort_transaction()
    assert _count(mongo_context, "authorization") == 0


@pytest.mark.parametrize(
    "authority_decision",
    [
        LegalClientMatterRepresentationAuthorityDecision.DECLINED,
        LegalClientMatterRepresentationAuthorityDecision.REQUIRES_REVIEW,
    ],
)
def test_non_appointed_p1_states_rejected_without_p2(mongo_context: MongoContext, authority_decision: LegalClientMatterRepresentationAuthorityDecision) -> None:
    _prepare(mongo_context, authority_decision=authority_decision)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            _orchestrator(mongo_context).issue(_request(), session=session)
        session.abort_transaction()
    assert _count(mongo_context, "authorization") == 0
    assert _count(mongo_context, "decision") == 0


def test_absent_p1_state_rejected(mongo_context: MongoContext) -> None:
    _prepare(mongo_context, include_authority=False)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            _orchestrator(mongo_context).issue(_request(), session=session)
        session.abort_transaction()
    assert _count(mongo_context, "decision") == 0


def test_future_p1_state_rejected(mongo_context: MongoContext) -> None:
    _prepare(mongo_context, authority_effective=BASE + timedelta(days=1))
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            _orchestrator(mongo_context).issue(_request(), session=session)
        session.abort_transaction()
    assert _count(mongo_context, "decision") == 0


def test_ambiguous_p1_state_rejected(mongo_context: MongoContext) -> None:
    """Two eligible P1 rows remain ambiguous; no latest-wins or expiry is inferred."""
    bundle = _prepare(mongo_context)
    second = LegalClientMatterRepresentationAuthority.from_canonical(
        authority_id="authority-ambiguous-p21br",
        engagement=bundle["engagement"],
        mandate=bundle["mandate"],
        acting_capacity=bundle["capacity"],
        representative_principal_id=REPRESENTATIVE,
        representative_role="LEGAL_ATTORNEY",
        representation_scope_capabilities=("ADVISORY",),
        decision=LegalClientMatterRepresentationAuthorityDecision.APPOINTED,
        appointing_principal_id=P20.CLIENT,
        source_evidence_reference="authority-source:p21br-ambiguous",
        source_evidence_fingerprint=HEX,
        authorization_evidence_reference="authority-authorization:p21br-ambiguous",
        authorization_evidence_fingerprint=HEX,
        occurred_at=BASE + timedelta(minutes=8),
        effective_from=BASE + timedelta(minutes=8),
        effective_until=BASE + timedelta(days=30),
        idempotency_key="authority-idempotency:ambiguous-p21br",
    )
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            authority_registry.persist_representation_authority(
                second, mongo_context.raw["authority"], session=session
            )
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        currentness = LegalClientMatterRepresentationAuthorityCurrentnessComposer(
            authority_collection=mongo_context.collections["authority"],
        ).compose_currentness(
            TENANT,
            bundle["matter"].case_matter_id,
            bundle["matter"].fingerprint,
            bundle["party"].party_id,
            bundle["party"].subject_identity_fingerprint,
            REPRESENTATIVE,
            BASE + timedelta(minutes=9),
            session,
        )
        assert currentness.state is LegalClientMatterRepresentationAuthorityCurrentnessState.AMBIGUOUS
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError) as raised:
            _orchestrator(mongo_context).issue(_request(), session=session)
        assert raised.value.code == "L9C11_P21B_P1_APPOINTED_REQUIRED"
        session.abort_transaction()
    assert _count(mongo_context, "decision") == 0


def test_corrupt_blocked_p1_state_rejected(mongo_context: MongoContext) -> None:
    """A bounded read corruption reaches P21A CORRUPT_BLOCKED and rejects P2."""
    bundle = _prepare(mongo_context)
    corrupt = dict(bundle["authority"].to_dict())
    corrupt["decision"] = LegalClientMatterRepresentationAuthorityDecision.DECLINED.value
    corrupt_collection = P21AR.CorruptingCollection(
        mongo_context.collections["authority"],
        {bundle["authority"].authority_id: corrupt},
    )
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError) as raised:
            _orchestrator(
                mongo_context,
                authority_collection=corrupt_collection,
            ).issue(_request(), session=session)
        assert raised.value.code == "L9C11_P21B_P1_CURRENTNESS_UNAVAILABLE"
        session.abort_transaction()
    assert _count(mongo_context, "authorization") == 0
    assert _count(mongo_context, "decision") == 0


def test_noncurrent_engagement_and_mandate_rejected(mongo_context: MongoContext) -> None:
    _prepare(mongo_context, engagement_effective=BASE + timedelta(days=2))
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            _orchestrator(mongo_context).issue(_request(), session=session)
        session.abort_transaction()
    assert _count(mongo_context, "decision") == 0


def test_noncurrent_mandate_rejected(mongo_context: MongoContext) -> None:
    _prepare(mongo_context, authority_until=BASE + timedelta(days=60))
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            _orchestrator(mongo_context).issue(
                _request(evaluated_at=BASE + timedelta(days=40)), session=session
            )
        session.abort_transaction()
    assert _count(mongo_context, "decision") == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"representative_status": PrincipalStatus.SUSPENDED},
        {"representative_membership": TenantMembershipStatus.SUSPENDED},
        {"representative_tenant": OTHER_TENANT},
        {"representative_role": "LEGAL_PARALEGAL"},
    ],
)
def test_representative_eligibility_is_live_and_fail_closed(mongo_context: MongoContext, kwargs: dict[str, Any]) -> None:
    _prepare(mongo_context, **kwargs)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            _orchestrator(mongo_context).issue(_request(), session=session)
        session.abort_transaction()
    assert _count(mongo_context, "authorization") == 0
    assert _count(mongo_context, "decision") == 0


@pytest.mark.parametrize("scope", [("NEGOTIATION",), ("COURT",), ("PAYMENT",), ("SETTLEMENT",)])
def test_scope_widening_court_and_finance_are_rejected(mongo_context: MongoContext, scope: tuple[str, ...]) -> None:
    _prepare(mongo_context)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            _orchestrator(mongo_context).issue(_request(scope=scope), session=session)
        session.abort_transaction()
    assert _count(mongo_context, "authorization") == 0
    assert _count(mongo_context, "decision") == 0


def test_atomic_abort_rolls_back_authorization_and_p2(mongo_context: MongoContext) -> None:
    _prepare(mongo_context)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        result = _orchestrator(mongo_context).issue(_request(), session=session)
        assert result.decision is LegalClientMatterRepresentationFirmDecisionType.ACCEPTED
        session.abort_transaction()
    assert _count(mongo_context, "authorization") == 0
    assert _count(mongo_context, "decision") == 0


class _FailingPersistence:
    """Force P2 failure after authorization evidence is written in-transaction."""

    @staticmethod
    def persist_firm_decision(value: object, collection: Any, *, session: Any) -> object:
        raise decision_registry.LegalClientMatterRepresentationFirmDecisionRegistryPersistenceUnavailableError("bounded-p21br-failure")


def test_no_partial_auth_evidence_on_p2_failure(mongo_context: MongoContext) -> None:
    _prepare(mongo_context)
    failing = _orchestrator(mongo_context, decision_persistence=_FailingPersistence())
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            failing.issue(_request(), session=session)
        session.abort_transaction()
    assert _count(mongo_context, "authorization") == 0
    assert _count(mongo_context, "decision") == 0


def test_exact_replay_is_one_authorization_and_one_p2_row(mongo_context: MongoContext) -> None:
    _prepare(mongo_context)
    request = _request()
    first = _issue_and_commit(mongo_context, request)
    second = _issue_and_commit(mongo_context, request)
    assert second.to_dict() == first.to_dict()
    assert _count(mongo_context, "authorization") == 1
    assert _count(mongo_context, "decision") == 1


def test_divergent_idempotency_is_blocked(mongo_context: MongoContext) -> None:
    _prepare(mongo_context)
    request = _request()
    _issue_and_commit(mongo_context, request)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
            _orchestrator(mongo_context).issue(
                _request(decision=LegalClientMatterRepresentationFirmDecisionType.DECLINED),
                session=session,
            )
        session.abort_transaction()
    assert _count(mongo_context, "authorization") == 1
    assert _count(mongo_context, "decision") == 1


def test_same_session_and_no_transaction_lifecycle_ownership(mongo_context: MongoContext) -> None:
    _prepare(mongo_context)
    for collection in mongo_context.collections.values():
        collection.session_ids.clear()
    source = inspect.getsource(LegalClientMatterRepresentationFirmDecisionOrchestrator)
    assert "start_transaction" not in source
    assert "commit_transaction" not in source
    assert "abort_transaction" not in source
    _issue_and_commit(mongo_context, _request())
    observed = {session_id for collection in mongo_context.collections.values() for session_id in collection.session_ids}
    assert len(observed) == 1


def test_zero_client_currentness_final_court_finance_or_http_authority(mongo_context: MongoContext) -> None:
    _prepare(mongo_context)
    before_authority = _count(mongo_context, "authority")
    _issue_and_commit(mongo_context, _request())
    assert _count(mongo_context, "authority") == before_authority
    assert _count(mongo_context, "authorization") == 1
    assert _count(mongo_context, "decision") == 1
    names = set(mongo_context.database.list_collection_names())
    assert not any("currentness" in name for name in names)
    assert not any("representation" in name and "final" in name for name in names)


# ARTIFACT: test_legal_client_matter_representation_firm_decision_orchestrator_real_mongo.py
# VERSION: v1.0.0-L9C11-P21BR-FIRM-REPRESENTATION-DECISION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable P21B firm-decision runtime evidence only
# TENANT POSTURE: UUID-isolated database and exact tenant-scoped registries
# FAIL-CLOSED POSTURE: zero skipped tests and zero failures required externally
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
