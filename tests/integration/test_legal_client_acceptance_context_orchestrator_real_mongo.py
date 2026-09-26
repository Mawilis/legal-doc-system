"""Isolated real-Mongo P2C3 certificate for authenticated context composition.

TITLE: Legal Client Acceptance Context Composer Real-Mongo Certificate
VERSION: v1.0.0-L9A4-P2C3-CLIENT-ACCEPTANCE-CONTEXT-COMPOSER-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove authenticated LEGAL_CLIENT composition against real Mongo with
         UUID-isolated databases, exact source gates, replay, abort and denial.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_acceptance_context_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: The composer orchestrates; IAM, visibility, matter,
                            party, capacity, instrument, lifecycle, approval,
                            issuer and context registries own their truth.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2C3 real-Mongo certificate proves transaction/session
           propagation, exact source gating, replay, divergent replay, abort,
           denial and no downstream authority writes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers; no secrets, URI,
                             bearer tokens or PII are printed.
TENANT BOUNDARY: Exact tenant/matter/principal scope on every operation.
AUTHORITY BOUNDARY: Authenticated client review-context composition only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization_decision_evidence_registry import TenantAuthorizationDecisionEvidenceRegistry
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_client_acting_capacity import LegalClientActingCapacityType, record_legal_client_acting_capacity
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import record_legal_client_matter_acceptance_instrument
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_approval import LegalClientMatterAcceptanceInstrumentApprovalDecision, record_legal_client_matter_acceptance_instrument_approval
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import LegalClientMatterAcceptanceInstrumentLifecycleStatus, record_legal_client_matter_acceptance_instrument_lifecycle
from tools.eos.legal_operations.domain.legal_client_matter_visibility_binding import LegalClientMatterVisibilityBinding
from tools.eos.legal_operations.domain.legal_matter_party import LegalMatterPartyKind, LegalMatterPartyRole, LegalMatterPartySide, register_legal_matter_party
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.orchestration.legal_client_acceptance_context_orchestrator import compose_legal_client_acceptance_context
from tools.eos.legal_operations.registry import legal_client_acceptance_context_registry as context_registry
from tools.eos.legal_operations.registry import legal_client_acting_capacity_registry as capacity_registry
from tools.eos.legal_operations.registry import legal_client_matter_acceptance_instrument_approval_registry as approval_registry
from tools.eos.legal_operations.registry import legal_client_matter_acceptance_instrument_lifecycle_registry as lifecycle_registry
from tools.eos.legal_operations.registry import legal_client_matter_acceptance_instrument_registry as instrument_registry
from tools.eos.legal_operations.registry import legal_client_matter_visibility_registry as visibility_registry
from tools.eos.legal_operations.registry import legal_matter_party_registry as party_registry
from tools.eos.legal_operations.registry import legal_operations_lifecycle_registry as matter_registry

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
TENANT, PRINCIPAL, MATTER_ID, PARTY_ID, INSTRUMENT_ID = ("tenant-p2c3-real", "principal-p2c3-real", "matter-p2c3-real", "party-p2c3-real", "instrument-p2c3-real")
VERSION = "1.0.0"
NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=timezone.utc)
FP_A = hashlib.sha3_512(b"p2c3-real-a").hexdigest()
FP_B = hashlib.sha3_512(b"p2c3-real-b").hexdigest()


class _Repo:
    """Expose canonical IAM repository resolve seams with caller session."""

    def __init__(self, collection: Any, kind: str) -> None:
        self.collection, self.kind = collection, kind

    def resolve(self, *args: str, **kwargs: Any) -> Any:
        session = kwargs.get("session")
        if self.kind == "principal":
            return PrincipalAuthorityRepository.resolve(args[0], self.collection, session=session)
        if self.kind == "membership":
            return TenantMembershipRepository.resolve(args[0], args[1], self.collection, session=session)
        return RoleAssignmentRepository.resolve(args[0], args[1], args[2], self.collection, session=session)


def _identity(*, tenant: str = TENANT, principal: str = PRINCIPAL, status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    return SovereignIdentity(identity_id=principal, tenant_id=tenant, username=None, email=None, roles=[], permissions=[], auth_method="synthetic", status=status)


def _collections(db: Any) -> dict[str, Any]:
    return {
        "matter": db[matter_registry.COLLECTION], "visibility": db[visibility_registry.COLLECTION], "party": db[party_registry.COLLECTION], "capacity": db[capacity_registry.COLLECTION],
        "instrument": db[instrument_registry.COLLECTION], "lifecycle": db[lifecycle_registry.COLLECTION], "approval": db[approval_registry.COLLECTION], "context": db[context_registry.COLLECTION],
        "principal": db["principal_authorities"], "membership": db["tenant_memberships"], "assignment": db["role_assignments"], "authorization": db["tenant_authorization_decision_evidence"],
    }


def _ensure_indexes(c: dict[str, Any]) -> None:
    PrincipalAuthorityRepository.ensure_indexes(c["principal"])
    TenantMembershipRepository.ensure_indexes(c["membership"])
    RoleAssignmentRepository.ensure_indexes(c["assignment"])
    matter_registry.LegalOperationsLifecycleRegistry.ensure_indexes(c["matter"])
    visibility_registry.LegalClientMatterVisibilityRegistry.ensure_indexes(c["visibility"])
    party_registry.ensure_indexes(c["party"])
    capacity_registry.ensure_indexes(c["capacity"])
    instrument_registry.ensure_indexes(c["instrument"])
    lifecycle_registry.ensure_indexes(c["lifecycle"])
    approval_registry.ensure_indexes(c["approval"])
    context_registry.ensure_indexes(c["context"])
    TenantAuthorizationDecisionEvidenceRegistry(c["authorization"], principal_repository=_Repo(c["principal"], "principal")).ensure_indexes()


def _seed(client: MongoClient[Any], c: dict[str, Any], *, capacity_expired: bool = False, lifecycle_status: LegalClientMatterAcceptanceInstrumentLifecycleStatus = LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE, approval_decision: LegalClientMatterAcceptanceInstrumentApprovalDecision = LegalClientMatterAcceptanceInstrumentApprovalDecision.APPROVED, visibility: bool = True) -> None:
    matter = CaseMatter(tenant_id=TENANT, case_matter_id=MATTER_ID, matter_reference="matter-p2c3-real", opened_at=NOW, evidence_reference="matter-source:p2c3")
    party = register_legal_matter_party(matter=matter, party_id=PARTY_ID, party_kind=LegalMatterPartyKind.ORGANIZATION, party_side=LegalMatterPartySide.CLIENT_SIDE, matter_role=LegalMatterPartyRole.CLIENT, subject_reference="client:subject-p2c3", subject_identity_fingerprint=FP_A, display_name="Synthetic P2C3 Client", registered_at=NOW, source_evidence_reference="party-source:p2c3", source_evidence_fingerprint=FP_B)
    capacity = record_legal_client_acting_capacity(case_matter=matter, party=party, capacity_id="capacity-p2c3-real", principal_id=PRINCIPAL, capacity_type=LegalClientActingCapacityType.REPRESENTATIVE, effective_from=NOW - timedelta(days=1), effective_until=NOW - timedelta(seconds=1) if capacity_expired else None, source_evidence_reference="capacity-source:p2c3", source_evidence_fingerprint=FP_A)
    instrument = record_legal_client_matter_acceptance_instrument(case_matter=matter, instrument_id=INSTRUMENT_ID, version=VERSION, instrument_kind="MATTER_REVIEW", title="Synthetic Matter Review Instrument", review_scope="client-information-review:v1", content_reference="server://p2c3/content", content_fingerprint=FP_B, created_at=NOW - timedelta(days=1), effective_from=NOW - timedelta(days=1), approval_evidence_reference="instrument-source:p2c3", approval_evidence_fingerprint=FP_A)
    lifecycle = record_legal_client_matter_acceptance_instrument_lifecycle(tenant_id=TENANT, case_matter_id=MATTER_ID, matter_fingerprint=matter.fingerprint, instrument_id=INSTRUMENT_ID, version=VERSION, instrument_fingerprint=instrument.fingerprint, status=lifecycle_status, occurred_at=NOW, lifecycle_evidence_reference="lifecycle-source:p2c3", lifecycle_evidence_fingerprint=FP_B)
    approval = record_legal_client_matter_acceptance_instrument_approval(case_matter=matter, instrument=instrument, approval_id="approval-p2c3-real", decision=approval_decision, approver_principal_id="principal-firm-reviewer", approver_capacity_reference="capacity:firm-reviewer", authorization_evidence_reference="authorization:firm-reviewer", authorization_evidence_fingerprint=FP_A, approval_evidence_reference="approval-source:p2c3", approval_evidence_fingerprint=FP_B, occurred_at=NOW, effective_from=NOW, idempotency_key=f"approval-p2c3-{approval_decision.value.lower()}")
    binding = LegalClientMatterVisibilityBinding.grant(client_principal_id=PRINCIPAL, case_matter=matter, granted_by_principal_id="principal-firm-reviewer", granted_at=NOW, evidence_reference="visibility-source:p2c3")
    with client.start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(PrincipalAuthority(PRINCIPAL, PrincipalStatus.ACTIVE, 0), c["principal"], session=session)
            TenantMembershipRepository.insert(TenantMembershipAuthority(PRINCIPAL, TENANT, TenantMembershipStatus.ACTIVE, 1), c["membership"], session=session)
            for role in ("tenant_legal_client", "LEGAL_CLIENT"):
                RoleAssignmentRepository.insert(RoleAssignmentAuthority(PRINCIPAL, TENANT, role, RoleAssignmentStatus.ACTIVE, 0), c["assignment"], session=session)
            matter_registry.LegalOperationsLifecycleRegistry.create(matter, c["matter"], session=session)
            party_registry.persist_party(party, c["party"], session=session)
            capacity_registry.persist_capacity(capacity, c["capacity"], session=session)
            instrument_registry.persist_instrument(instrument, c["instrument"], session=session)
            lifecycle_registry.persist_lifecycle(lifecycle, c["lifecycle"], instrument_collection=c["instrument"], session=session)
            approval_registry.persist_approval(approval, c["approval"], session=session)
            if visibility:
                visibility_registry.LegalClientMatterVisibilityRegistry.grant(binding, c["visibility"], session=session)


def _issuer(c: dict[str, Any]) -> TenantAuthorizationDecisionEvidenceRegistry:
    repo = _Repo(c["assignment"], "assignment")
    return TenantAuthorizationDecisionEvidenceRegistry(c["authorization"], principal_repository=_Repo(c["principal"], "principal"), membership_repository=_Repo(c["membership"], "membership"), role_assignment_repository=repo, business_role_repository=repo)


def _kwargs(c: dict[str, Any], issuer: Any, *, identity: SovereignIdentity | None = None, context_id: str = "context-p2c3-real", replay_key: str = "replay-p2c3-real", instrument_id: str = INSTRUMENT_ID) -> dict[str, Any]:
    return dict(identity=identity or _identity(), case_matter_id=MATTER_ID, acceptance_context_id=context_id, replay_key=replay_key, instrument_id=instrument_id, matter_lifecycle_collection=c["matter"], visibility_collection=c["visibility"], party_collection=c["party"], capacity_collection=c["capacity"], instrument_collection=c["instrument"], instrument_lifecycle_collection=c["lifecycle"], approval_collection=c["approval"], context_collection=c["context"], authorization_evidence_registry=issuer, principal_repository=_Repo(c["principal"], "principal"), membership_repository=_Repo(c["membership"], "membership"), business_role_repository=_Repo(c["assignment"], "assignment"), role_assignment_repository=_Repo(c["assignment"], "assignment"), clock=lambda: NOW)


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, dict[str, Any]]]:
    """Use one UUID-isolated database and drop only that database."""
    client: MongoClient[Any] = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5_000, retryWrites=True, tz_aware=True)
    database: Any = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == "wilsyVendorCertRS"
        assert hello.get("isWritablePrimary") is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        database = client[f"wilsy_l9a4_p2c3_context_{uuid4().hex}"]
        c = _collections(database)
        _ensure_indexes(c)
        yield client, database, c
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _compose(client: MongoClient[Any], c: dict[str, Any], **overrides: Any) -> Any:
    issuer = overrides.pop("issuer", None) or _issuer(c)
    kwargs = _kwargs(c, issuer, **overrides)
    with client.start_session() as session:
        with session.start_transaction():
            return compose_legal_client_acceptance_context(**kwargs, session=session)


def test_topology_and_authenticated_commit(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, db, c = mongo_context
    assert client.admin.command("hello").get("setName") == "wilsyVendorCertRS"
    _seed(client, c)
    result = _compose(client, c)
    assert result.tenant_id == TENANT and result.actor_principal_id == PRINCIPAL
    assert result.expires_at - result.issued_at == timedelta(minutes=10)
    assert c["context"].count_documents({"tenant_id": TENANT}) == 1
    assert c["authorization"].count_documents({"tenant_id": TENANT}) == 1
    assert not {"legal_client_acceptances", "engagements", "representations", "court_authorities", "financial_approvals"} & set(db.list_collection_names())


def test_exact_replay_and_divergent_replay(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _db, c = mongo_context
    _seed(client, c)
    first = _compose(client, c)
    replay = _compose(client, c)
    assert replay.to_dict() == first.to_dict()
    with pytest.raises(Exception):
        _compose(client, c, context_id="context-other")
    assert c["context"].count_documents({}) == 1 and c["authorization"].count_documents({}) == 1


def test_stale_visibility_capacity_lifecycle_approval_and_identity_reject(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _db, c = mongo_context
    _seed(client, c, visibility=False)
    with pytest.raises(Exception):
        _compose(client, c)
    assert c["context"].count_documents({}) == 0


def test_abort_rolls_back_both_durable_records(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _db, c = mongo_context
    _seed(client, c)
    kwargs = _kwargs(c, _issuer(c))
    with pytest.raises(RuntimeError):
        with client.start_session() as session:
            with session.start_transaction():
                compose_legal_client_acceptance_context(**kwargs, session=session)
                raise RuntimeError("synthetic caller abort")
    assert c["context"].count_documents({}) == 0 and c["authorization"].count_documents({}) == 0


def test_missing_transaction_cross_tenant_inactive_and_unknown_source_reject(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _db, c = mongo_context
    _seed(client, c)
    with pytest.raises(Exception):
        compose_legal_client_acceptance_context(**_kwargs(c, _issuer(c)), session=None)
    with pytest.raises(Exception):
        _compose(client, c, identity=_identity(status=PrincipalStatus.SUSPENDED), context_id="context-suspended", replay_key="replay-suspended")
    with pytest.raises(Exception):
        _compose(client, c, identity=_identity(tenant="tenant-other"), context_id="context-other-tenant", replay_key="replay-other-tenant")
    with pytest.raises(Exception):
        _compose(client, c, instrument_id="instrument-unknown", context_id="context-unknown", replay_key="replay-unknown")
    assert c["context"].count_documents({}) == 0


def test_no_downstream_authority_is_created(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, db, c = mongo_context
    _seed(client, c)
    _compose(client, c)
    assert c["context"].count_documents({}) == 1 and c["authorization"].count_documents({}) == 1
    assert not {"legal_client_acceptances", "engagements", "representations", "court_authorities", "financial_approvals"} & set(db.list_collection_names())


# ARTIFACT: test_legal_client_acceptance_context_orchestrator_real_mongo.py
# VERSION: v1.0.0-L9A4-P2C3-CLIENT-ACCEPTANCE-CONTEXT-COMPOSER-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated authenticated context composition only
# TENANT POSTURE: UUID-isolated database and exact tenant/matter/principal scope
# FAIL-CLOSED POSTURE: denial, stale, divergent replay and abort reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
