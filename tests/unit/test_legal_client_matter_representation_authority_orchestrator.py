"""Direct P20 certificate for client Representation-authority orchestration.

TITLE: L9C11-P20 Client Representation Authority Orchestrator Certificate
VERSION: v1.0.0-L9C11-P20-CLIENT-REPRESENTATION-AUTHORITY-ORCHESTRATOR-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove authenticated self-client appointment, exact lineage, role
         selection, caller-session atomicity, replay and authority exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_representation_authority_orchestrator.py
COLLABORATION / OWNERSHIP: P20 direct certificate; P1/P7 and P17/P18 remain
                            immutable predecessor authorities.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0 covers the frozen P15/P16 contract and caller-owned
           transaction, currentness, scope, role and replay boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and SHA3-512 values.
TENANT BOUNDARY: Every fixture is explicitly tenant-scoped.
AUTHORITY BOUNDARY: Client appointment prerequisite only; no final Representation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timezone
import inspect
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_authorization import TenantAuthorizationDecision, TenantAuthorizationReason
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_client_acting_capacity import LegalClientActingCapacity, LegalClientActingCapacityType
from tools.eos.legal_operations.domain.legal_client_matter_representation_authorization_evidence import LegalClientMatterRepresentationAuthorizationEvidence
from tools.eos.legal_operations.domain.legal_client_matter_engagement import LegalClientMatterEngagement
from tools.eos.legal_operations.domain.legal_client_matter_mandate import LegalClientMatterMandate
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter, CaseMatterState
from tools.eos.legal_operations.orchestration import legal_client_matter_representation_authority_orchestrator as orchestrator


TENANT = "tenant-p20"
CLIENT = "principal-client"
ATTORNEY = "principal-attorney"
MATTER_ID = "matter-p20"
PARTY_ID = "party-p20"
MANDATE_ID = "mandate-p20"
ENGAGEMENT_ID = "engagement-p20"
CAPACITY_ID = "capacity-p20"
NOW = datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


class Session:
    in_transaction = True


def _identity(principal: str = CLIENT, status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    return SovereignIdentity(identity_id=principal, tenant_id=TENANT, username=None, email=None, roles=[], permissions=[], auth_method="synthetic", status=status)


def _bare(cls: type[Any], **values: object) -> Any:
    value = object.__new__(cls)
    for key, item in values.items():
        object.__setattr__(value, key, item)
    return value


def _matter(state: CaseMatterState = CaseMatterState.OPEN) -> CaseMatter:
    return CaseMatter(tenant_id=TENANT, case_matter_id=MATTER_ID, matter_reference="matter-p20", opened_at=NOW, evidence_reference="source:matter-p20", state=state)


def _sources() -> dict[str, Any]:
    matter = _matter()
    party = SimpleNamespace(tenant_id=TENANT, case_matter_id=MATTER_ID, matter_fingerprint=matter.fingerprint, party_id=PARTY_ID, subject_reference="client:subject-p20", subject_identity_fingerprint=FP_A, matter_role=SimpleNamespace(value="CLIENT"), party_side=SimpleNamespace(value="CLIENT_SIDE"), fingerprint=FP_B)
    capacity = _bare(LegalClientActingCapacity, tenant_id=TENANT, case_matter_id=MATTER_ID, matter_fingerprint=matter.fingerprint, capacity_id=CAPACITY_ID, principal_id=CLIENT, party_id=PARTY_ID, subject_reference=party.subject_reference, subject_identity_fingerprint=FP_A, capacity_type=LegalClientActingCapacityType.SELF, fingerprint=FP_C)
    engagement = _bare(LegalClientMatterEngagement, tenant_id=TENANT, engagement_id=ENGAGEMENT_ID, case_matter_id=MATTER_ID, matter_fingerprint=matter.fingerprint, client_party_id=PARTY_ID, subject_reference=party.subject_reference, subject_identity_fingerprint=FP_A, acting_capacity_id=CAPACITY_ID, acting_capacity_fingerprint=FP_C, mandate_id=MANDATE_ID, mandate_fingerprint=FP_B, fingerprint=FP_A)
    mandate = _bare(LegalClientMatterMandate, tenant_id=TENANT, mandate_id=MANDATE_ID, case_matter_id=MATTER_ID, matter_fingerprint=matter.fingerprint, client_party_id=PARTY_ID, subject_identity_fingerprint=FP_A, grant_actor_principal_id=CLIENT, acting_capacity_id=CAPACITY_ID, acting_capacity_fingerprint=FP_C, scope_reference="scope:p20", scope_fingerprint=FP_B, capabilities=("ADVISORY", "NEGOTIATION"), fingerprint=FP_B)
    visibility = SimpleNamespace(tenant_id=TENANT, client_principal_id=CLIENT, case_matter_id=MATTER_ID, source_case_matter_fingerprint=matter.fingerprint, binding_identity="visibility:p20", fingerprint=FP_C, status=SimpleNamespace(value="ACTIVE"))
    return {"matter": matter, "party": party, "capacity": capacity, "engagement": engagement, "mandate": mandate, "visibility": visibility}


class Repo:
    def __init__(self) -> None:
        self.calls: list[tuple[tuple[object, ...], Any]] = []

    def resolve(self, *args: object, session: Any = None) -> Any:
        self.calls.append((args, session))
        if len(args) == 1:
            return SimpleNamespace(principal_id=args[0], status=PrincipalStatus.ACTIVE, revision=4)
        if len(args) == 2:
            return SimpleNamespace(principal_id=args[0], tenant_id=args[1], status=TenantMembershipStatus.ACTIVE, revision=5)
        return SimpleNamespace(principal_id=args[0], tenant_id=args[1], role_id=args[2], status=RoleAssignmentStatus.ACTIVE, revision=6)

    def list_assignments(self, principal_id: str, tenant_id: str, *, session: Any = None) -> tuple[Any, ...]:
        self.calls.append(((principal_id, tenant_id, "list"), session))
        if principal_id == ATTORNEY:
            return (SimpleNamespace(principal_id=ATTORNEY, tenant_id=TENANT, role_id="LEGAL_PARTNER", status=RoleAssignmentStatus.ACTIVE, revision=8), SimpleNamespace(principal_id=ATTORNEY, tenant_id=TENANT, role_id="LEGAL_ATTORNEY", status=RoleAssignmentStatus.ACTIVE, revision=7))
        return ()


class Currentness:
    def __init__(self, current: bool = True) -> None:
        self.is_current = current
        self.state = "CURRENT" if current else "AMBIGUOUS"
        self.decisive_engagement_id = ENGAGEMENT_ID if current else None
        self.decisive_engagement_fingerprint = FP_A if current else None
        self.mandate_id = MANDATE_ID if current else None
        self.mandate_fingerprint = FP_B if current else None


class Composer:
    def __init__(self, value: Any) -> None:
        self.value = value
        self.calls: list[Any] = []

    def compose_currentness(self, *args: Any) -> Any:
        self.calls.append(args)
        return self.value


class EvidenceStore:
    def __init__(self) -> None:
        self.values: list[Any] = []
        self.calls: list[Any] = []

    def persist_authorization_evidence(self, value: Any, _collection: Any, *, session: Any) -> Any:
        self.calls.append(session)
        if not self.values:
            self.values.append(value)
        return self.values[0]


class AuthorityStore:
    def __init__(self) -> None:
        self.values: list[Any] = []
        self.calls: list[Any] = []

    def persist_representation_authority(self, value: Any, _collection: Any, *, session: Any) -> Any:
        self.calls.append(session)
        if not self.values:
            self.values.append(value)
        return self.values[0]


@pytest.fixture
def harness(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    sources = _sources()
    repos = Repo()
    evidence_store, authority_store = EvidenceStore(), AuthorityStore()
    engagement_currentness, mandate_currentness = Composer(Currentness()), Composer(Currentness())
    monkeypatch.setattr(orchestrator, "authorize_tenant_operation", lambda **_: TenantAuthorizationDecision(True, TenantAuthorizationReason.AUTHORIZED, "tenant_legal_client", "LEGAL_CLIENT"))
    monkeypatch.setattr(orchestrator.matter_registry.LegalOperationsLifecycleRegistry, "get_entity_history", staticmethod(lambda *_args, **_kwargs: (sources["matter"],)))
    monkeypatch.setattr(orchestrator.party_registry, "list_matter_parties", lambda *_args, **_kwargs: (sources["party"],))
    monkeypatch.setattr(orchestrator.capacity_registry, "list_valid_capacities_at", lambda *_args, **_kwargs: (sources["capacity"],))
    monkeypatch.setattr(orchestrator.visibility_registry.LegalClientMatterVisibilityRegistry, "resolve_current_active", staticmethod(lambda *_args, **_kwargs: sources["visibility"]))
    monkeypatch.setattr(orchestrator.engagement_registry, "get_engagement", lambda *_args, **_kwargs: sources["engagement"])
    monkeypatch.setattr(orchestrator.mandate_registry, "get_mandate", lambda *_args, **_kwargs: sources["mandate"])
    value = orchestrator.LegalClientMatterRepresentationAuthorityOrchestrator(
        matter_lifecycle_collection=object(), visibility_collection=object(), party_collection=object(), capacity_collection=object(), engagement_collection=object(), mandate_collection=object(), grant_collection=object(), grant_lifecycle_collection=object(), acknowledgment_collection=object(), evidence_collection=object(), authority_collection=object(), principal_repository=repos, membership_repository=repos, business_role_repository=repos, role_assignment_repository=repos, engagement_currentness_composer=engagement_currentness, mandate_currentness_composer=mandate_currentness, evidence_persistence=evidence_store, authority_persistence=authority_store,
    )
    return {"orchestrator": value, "repos": repos, "evidence": evidence_store, "authority": authority_store, "engagement_currentness": engagement_currentness, "mandate_currentness": mandate_currentness}


def _request(**overrides: object) -> orchestrator.LegalClientMatterRepresentationAuthorityRequest:
    values: dict[str, object] = dict(tenant_id=TENANT, case_matter_id=MATTER_ID, client_party_id=PARTY_ID, identity=_identity(), representative_principal_id=ATTORNEY, mandate_id=MANDATE_ID, representation_scope_capabilities=("NEGOTIATION", "ADVISORY"), occurred_at=NOW, effective_from=NOW, idempotency_key="idem:p20", source_evidence_reference="evidence:p20", source_evidence_fingerprint=FP_A)
    values.update(overrides)
    return orchestrator.LegalClientMatterRepresentationAuthorityRequest(**cast(Any, values))


def test_version_request_surface_and_transaction_contract() -> None:
    assert orchestrator.VERSION == "v1.0.0-L9C11-P20-CLIENT-REPRESENTATION-AUTHORITY-ORCHESTRATOR"
    assert "representative_role" not in inspect.signature(orchestrator.LegalClientMatterRepresentationAuthorityRequest).parameters


def test_missing_session_rejected(harness: dict[str, Any]) -> None:
    with pytest.raises(orchestrator.LegalClientMatterRepresentationAuthorityOrchestrationError, match="ACTIVE_TRANSACTION_REQUIRED"):
        harness["orchestrator"].issue(_request(), session=None)


def test_success_binds_exact_lineage_role_and_same_session(harness: dict[str, Any]) -> None:
    session = Session()
    value = harness["orchestrator"].issue(_request(), session=session)
    assert value.representative_role == "LEGAL_ATTORNEY"
    assert value.authorization_evidence_reference.startswith("client-representation-authorization:")
    assert value.authorization_evidence_fingerprint == harness["evidence"].values[0].fingerprint
    assert harness["evidence"].calls == [session]
    assert harness["authority"].calls == [session]
    assert all(call[1] is session for call in harness["repos"].calls)
    assert harness["engagement_currentness"].calls[0][-1] is session
    assert harness["mandate_currentness"].calls[0][-1] is session


def test_exact_replay_returns_same_canonical_values(harness: dict[str, Any]) -> None:
    session = Session()
    first = harness["orchestrator"].issue(_request(), session=session)
    second = harness["orchestrator"].issue(_request(), session=session)
    assert second.to_dict() == first.to_dict()


@pytest.mark.parametrize("status", [PrincipalStatus.REVOKED, PrincipalStatus.SUSPENDED])
def test_inactive_identity_rejected(harness: dict[str, Any], status: PrincipalStatus) -> None:
    with pytest.raises(orchestrator.LegalClientMatterRepresentationAuthorityOrchestrationError):
        harness["orchestrator"].issue(_request(identity=_identity(status=status)), session=Session())


def test_wrong_tenant_and_wrong_subject_rejected(harness: dict[str, Any]) -> None:
    with pytest.raises(orchestrator.LegalClientMatterRepresentationAuthorityOrchestrationError):
        harness["orchestrator"].issue(_request(tenant_id="tenant-other"), session=Session())
    with pytest.raises(orchestrator.LegalClientMatterRepresentationAuthorityOrchestrationError):
        harness["orchestrator"].issue(_request(subject_reference="client:other"), session=Session())


@pytest.mark.parametrize("capacity_type", [LegalClientActingCapacityType.AUTHORIZED_AGENT, LegalClientActingCapacityType.REPRESENTATIVE])
def test_non_self_capacity_rejected(harness: dict[str, Any], monkeypatch: pytest.MonkeyPatch, capacity_type: LegalClientActingCapacityType) -> None:
    monkeypatch.setattr(orchestrator.capacity_registry, "list_valid_capacities_at", lambda *_args, **_kwargs: (SimpleNamespace(tenant_id=TENANT, case_matter_id=MATTER_ID, matter_fingerprint=_sources()["matter"].fingerprint, capacity_id=CAPACITY_ID, principal_id=CLIENT, party_id=PARTY_ID, subject_reference="client:subject-p20", subject_identity_fingerprint=FP_A, capacity_type=capacity_type, fingerprint=FP_C),))
    with pytest.raises(orchestrator.LegalClientMatterRepresentationAuthorityOrchestrationError):
        harness["orchestrator"].issue(_request(), session=Session())


def test_non_current_engagement_or_mandate_rejected(harness: dict[str, Any]) -> None:
    harness["engagement_currentness"].value = Currentness(False)
    with pytest.raises(orchestrator.LegalClientMatterRepresentationAuthorityOrchestrationError):
        harness["orchestrator"].issue(_request(), session=Session())
    harness["engagement_currentness"].value = Currentness()
    harness["mandate_currentness"].value = Currentness(False)
    with pytest.raises(orchestrator.LegalClientMatterRepresentationAuthorityOrchestrationError):
        harness["orchestrator"].issue(_request(), session=Session())


def test_scope_is_normalized_and_widening_is_rejected(harness: dict[str, Any]) -> None:
    value = harness["orchestrator"].issue(_request(representation_scope_capabilities=["negotiation", "ADVISORY", "ADVISORY"]), session=Session())
    assert value.representation_scope_capabilities == ("ADVISORY", "NEGOTIATION")
    with pytest.raises(orchestrator.LegalClientMatterRepresentationAuthorityOrchestrationError):
        harness["orchestrator"].issue(_request(representation_scope_capabilities=("TRANSACTIONAL",)), session=Session())
    with pytest.raises(orchestrator.LegalClientMatterRepresentationAuthorityOrchestrationError):
        harness["orchestrator"].issue(_request(representation_scope_capabilities=("COURT_FILING_PREPARATION",)), session=Session())


def test_authority_and_evidence_are_distinct_and_no_downstream_authority(harness: dict[str, Any]) -> None:
    value = harness["orchestrator"].issue(_request(), session=Session())
    evidence = harness["evidence"].values[0]
    assert isinstance(evidence, LegalClientMatterRepresentationAuthorizationEvidence)
    assert value.decision.value == "APPOINTED"
    source = inspect.getsource(orchestrator)
    assert "LegalClientMatterRepresentationFirmDecision" not in source
    assert "datetime.now" not in source
    assert "start_transaction" not in source
    assert ".commit(" not in source
    assert ".abort(" not in source


@pytest.mark.parametrize("scope", [(), ("PAYMENT_EXECUTION",), ("SETTLEMENT",)])
def test_empty_or_financial_scope_rejected(harness: dict[str, Any], scope: tuple[str, ...]) -> None:
    with pytest.raises((ValueError, orchestrator.LegalClientMatterRepresentationAuthorityOrchestrationError)):
        harness["orchestrator"].issue(_request(representation_scope_capabilities=scope), session=Session())


# ARTIFACT: test_legal_client_matter_representation_authority_orchestrator.py
# VERSION: v1.0.0-L9C11-P20-CLIENT-REPRESENTATION-AUTHORITY-ORCHESTRATOR-CERT
# AUTHORITY BOUNDARY: direct P20 certificate only
# TENANT POSTURE: synthetic exact tenant and caller-owned session
# FAIL-CLOSED POSTURE: stale, widened, inactive, divergent and cross-tenant requests reject
# END OF WILSY OS SOVEREIGN ARTIFACT
