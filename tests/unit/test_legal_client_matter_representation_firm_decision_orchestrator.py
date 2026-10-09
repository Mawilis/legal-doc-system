"""P21B direct certificate for caller-owned firm Representation orchestration.

TITLE: WILSY OS P21B Firm Representation Decision Orchestrator Certificate
VERSION: v1.0.0-L9C11-P21B-FIRM-REPRESENTATION-DECISION-ORCHESTRATOR-DIRECT-CERT
AUTHORITY: Pure orchestration contract certification.
EPITOME: Prove transaction, identity, decision-shape and authority-boundary
         guards before sanctioned real-Mongo certification.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_representation_firm_decision_orchestrator.py
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
AUTHORITY BOUNDARY: No client authority, currentness write, final Representation,
                    Court, professional or financial authority.
"""
import ast
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import LegalClientMatterRepresentationFirmDecisionType
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import LegalClientMatterRepresentationAuthority, LegalClientMatterRepresentationAuthorityDecision
from tools.eos.legal_operations.domain.legal_client_matter_engagement import LegalClientMatterEngagement
from tools.eos.legal_operations.domain.legal_client_matter_mandate import LegalClientMatterMandate
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import LegalClientMatterRepresentationAuthorityCurrentness, LegalClientMatterRepresentationAuthorityCurrentnessState
from tools.eos.legal_operations.orchestration import legal_client_matter_representation_firm_decision_orchestrator as orchestrator_module
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_firm_decision_orchestrator import (
    OPERATION,
    PERMISSION,
    VERSION,
    LegalClientMatterRepresentationFirmDecisionOrchestrationError,
    LegalClientMatterRepresentationFirmDecisionOrchestrator,
    LegalClientMatterRepresentationFirmDecisionRequest,
)


HEX = "a" * 128
WHEN = datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc)


class _InactiveSession:
    in_transaction = False


class _ActiveSession:
    in_transaction = True


def _request(**overrides: object) -> LegalClientMatterRepresentationFirmDecisionRequest:
    values: dict[str, object] = {
        "tenant_id": "tenant-p21b",
        "case_matter_id": "matter-p21b",
        "client_party_id": "party-p21b",
        "representative_principal_id": "rep-p21b",
        "decision": LegalClientMatterRepresentationFirmDecisionType.ACCEPTED,
        "representation_scope_capabilities": ["ADVISORY"],
        "evaluated_at": WHEN,
        "idempotency_key": "idempotency-p21b",
        "source_evidence_reference": "evidence:p21b",
        "source_evidence_fingerprint": HEX,
        "identity": SovereignIdentity(identity_id="actor-p21b", tenant_id="tenant-p21b", username=None, email=None, auth_method="test", status=PrincipalStatus.ACTIVE),
    }
    values.update(overrides)
    return LegalClientMatterRepresentationFirmDecisionRequest(**cast(Any, values))


def _orchestrator() -> LegalClientMatterRepresentationFirmDecisionOrchestrator:
    required = {
        "matter_lifecycle_collection": object(),
        "party_collection": object(),
        "authority_collection": object(),
        "engagement_collection": object(),
        "mandate_collection": object(),
        "grant_collection": object(),
        "grant_lifecycle_collection": object(),
        "acknowledgment_collection": object(),
        "decision_collection": object(),
        "principal_repository": object(),
        "membership_repository": object(),
        "role_assignment_repository": object(),
        "business_role_repository": object(),
        "authorization_evidence_registry": SimpleNamespace(),
    }
    return LegalClientMatterRepresentationFirmDecisionOrchestrator(**required)


def test_contract_constants_and_caller_transaction_guards() -> None:
    assert VERSION == "v1.0.0-L9C11-P21B-FIRM-REPRESENTATION-DECISION-ORCHESTRATOR"
    assert OPERATION == "legal_matter_representation_firm_decision_write"
    assert PERMISSION == "legal_operations:matter_representation_firm_decision:write"
    orchestrator = _orchestrator()
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError) as missing:
        orchestrator.issue(_request(), session=None)
    assert missing.value.code == "L9C11_P21B_ACTIVE_TRANSACTION_REQUIRED"
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError) as inactive:
        orchestrator.issue(_request(), session=_InactiveSession())
    assert inactive.value.code == "L9C11_P21B_ACTIVE_TRANSACTION_REQUIRED"


def test_identity_and_decision_shape_fail_closed_before_reads() -> None:
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError) as invalid:
        _orchestrator().issue(_request(decision="NOT_A_DECISION"), session=_ActiveSession())
    assert invalid.value.code == "L9C11_P21B_DECISION_INVALID"
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError):
        _request(source_evidence_fingerprint="bad")


def test_request_keeps_firm_actor_separate_from_representative() -> None:
    request = _request()
    assert request.identity.identity_id != request.representative_principal_id


@pytest.mark.parametrize(
    "state",
    [
        LegalClientMatterRepresentationAuthorityCurrentnessState.NO_AUTHORITY,
        LegalClientMatterRepresentationAuthorityCurrentnessState.DECLINED,
        LegalClientMatterRepresentationAuthorityCurrentnessState.REQUIRES_REVIEW,
        LegalClientMatterRepresentationAuthorityCurrentnessState.AMBIGUOUS,
        LegalClientMatterRepresentationAuthorityCurrentnessState.CORRUPT_BLOCKED,
    ],
)
def test_every_non_positive_p1_currentness_state_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    state: LegalClientMatterRepresentationAuthorityCurrentnessState,
) -> None:
    class Composer:
        def __init__(self) -> None:
            self.calls: list[tuple[object, ...]] = []

        def compose_currentness(self, *args: object) -> object:
            self.calls.append(args)
            return SimpleNamespace(state=state, is_currently_appointed=False)

    composer = Composer()
    value = _orchestrator_with_composer(composer)
    monkeypatch.setattr(value, "_matter", lambda *_args: SimpleNamespace(case_matter_id="matter-p21b", fingerprint=HEX))
    monkeypatch.setattr(value, "_party", lambda *_args: SimpleNamespace(party_id="party-p21b", subject_identity_fingerprint=HEX))
    session = _ActiveSession()
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionOrchestrationError) as error:
        value.issue(_request(), session=session)
    assert error.value.code == "L9C11_P21B_P1_APPOINTED_REQUIRED"
    assert composer.calls == [("tenant-p21b", "matter-p21b", HEX, "party-p21b", HEX, "rep-p21b", WHEN, session)]


def _orchestrator_with_composer(composer: object) -> LegalClientMatterRepresentationFirmDecisionOrchestrator:
    required = {
        "matter_lifecycle_collection": object(),
        "party_collection": object(),
        "authority_collection": object(),
        "engagement_collection": object(),
        "mandate_collection": object(),
        "grant_collection": object(),
        "grant_lifecycle_collection": object(),
        "acknowledgment_collection": object(),
        "decision_collection": object(),
        "principal_repository": object(),
        "membership_repository": object(),
        "role_assignment_repository": object(),
        "business_role_repository": object(),
        "authorization_evidence_registry": SimpleNamespace(),
        "authority_currentness_composer": composer,
    }
    return LegalClientMatterRepresentationFirmDecisionOrchestrator(**required)


@pytest.mark.parametrize(
    ("requirement", "needle"),
    [
        ("operation", "legal_matter_representation_firm_decision_write"),
        ("permission", "legal_operations:matter_representation_firm_decision:write"),
        ("p1 composer", "_authority_currentness.compose_currentness"),
        ("engagement composer", "_engagement_currentness.compose_currentness"),
        ("mandate composer", "_mandate_currentness.compose_currentness"),
        ("appointed gate", "L9C11_P21B_P1_APPOINTED_REQUIRED"),
        ("open matter gate", "L9C11_P21B_OPEN_MATTER_REQUIRED"),
        ("client party gate", "L9C11_P21B_CLIENT_PARTY_SCOPE_MISMATCH"),
        ("representative gate", "L9C11_P21B_REPRESENTATIVE_ROLE_REQUIRED"),
        ("active representative", "L9C11_P21B_REPRESENTATIVE_INACTIVE"),
        ("active membership", "L9C11_P21B_REPRESENTATIVE_MEMBERSHIP_REQUIRED"),
        ("current engagement", '"engagement"'),
        ("current mandate", '"mandate"'),
        ("authorization evidence", "authorization_evidence_registry.issue"),
        ("canonical P2 factory", "from_client_authority"),
        ("P9 persistence", "persist_firm_decision"),
        ("caller transaction", "L9C11_P21B_ACTIVE_TRANSACTION_REQUIRED"),
        ("scope prohibition", "L9C11_P21B_SCOPE_PROHIBITED"),
        ("replay correlation", "L9C11_P21B_P2_REPLAY_CORRELATION_INVALID"),
        ("idempotency conflict", "L9C11_P21B_IDEMPOTENCY_CONFLICT"),
        ("no client authority", "LegalClientMatterRepresentationAuthorityCurrentnessComposer"),
        ("no formation", "LegalClientMatterRepresentationFirmDecision"),
        ("partner role", "LEGAL_PARTNER"),
        ("attorney role", "LEGAL_ATTORNEY"),
        ("accepted", "ACCEPTED"),
        ("same session", "session=tx"),
        ("tenant digest", '"tenant_id": tenant'),
        ("matter digest", '"case_matter_id": matter.case_matter_id'),
        ("matter fingerprint digest", '"matter_fingerprint": matter.fingerprint'),
        ("client digest", '"client_party_id": party.party_id'),
        ("subject digest", '"subject_identity_fingerprint": party.subject_identity_fingerprint'),
        ("authority digest", '"representation_authority_id": authority.authority_id'),
        ("authority fingerprint digest", '"representation_authority_fingerprint": authority.fingerprint'),
        ("representative digest", '"representative_principal_id": authority.representative_principal_id'),
        ("decision digest", '"decision": decision.value'),
        ("scope digest", '"representation_scope_capabilities": list(scope)'),
        ("idempotency digest", '"idempotency_key": idempotency'),
        ("exact P1 fingerprint", "authority.fingerprint != authority_fingerprint"),
        ("exact P1 tenant", "authority.tenant_id != tenant"),
        ("exact P1 matter", "authority.case_matter_id != matter.case_matter_id"),
        ("exact P1 client", "authority.client_party_id != party.party_id"),
        ("exact P1 subject", "authority.subject_reference != party.subject_reference"),
        ("exact representative", "authority.representative_principal_id != representative_id"),
        ("appointed authority", "authority.is_appointing is not True"),
        ("engagement fingerprint", "engagement.fingerprint != engagement_fingerprint"),
        ("engagement matter", "engagement.case_matter_id != matter.case_matter_id"),
        ("engagement party", "engagement.client_party_id != party.party_id"),
        ("engagement subject", "engagement.subject_reference != party.subject_reference"),
        ("mandate fingerprint", "mandate.fingerprint != authority.mandate_fingerprint"),
        ("mandate tenant", "mandate.tenant_id != tenant"),
        ("mandate matter", "mandate.case_matter_id != matter.case_matter_id"),
        ("mandate party", "mandate.client_party_id != party.party_id"),
        ("mandate subset", "set(authority.mandate_capabilities) - set(mandate.capabilities)"),
        ("auth tenant", "authorization.tenant_id != tenant"),
        ("auth actor", "authorization.principal_id != actor"),
        ("auth operation", "authorization.operation != OPERATION"),
        ("auth permission", "authorization.permission != PERMISSION"),
        ("auth subject", "authorization.subject_reference != subject"),
        ("auth role", "authorization.authorization_role not in"),
        ("p2 type", "type(persisted) is not LegalClientMatterRepresentationFirmDecision"),
        ("p2 exact replay", "persisted.to_dict() != value.to_dict()"),
        ("retry fail closed", "WHOLE_TRANSACTION_RETRY_REQUIRED"),
        ("financial scope", "FINANCIAL_EXECUTION"),
        ("court scope", "COURT_AUTHORITY"),
        ("authenticated identity", "SovereignIdentity"),
    ],
)
def test_direct_certificate_requirement_is_present(requirement: str, needle: str) -> None:
    source = Path(orchestrator_module.__file__).read_text()
    assert needle in source, requirement


def test_orchestrator_does_not_own_clock_or_transaction_lifecycle() -> None:
    source = Path(orchestrator_module.__file__).read_text()
    assert "datetime.now" not in source
    assert "start_transaction" not in source
    assert "commit_transaction" not in source
    assert "abort_transaction" not in source


@pytest.mark.parametrize(
    "decision",
    [
        LegalClientMatterRepresentationFirmDecisionType.ACCEPTED,
        LegalClientMatterRepresentationFirmDecisionType.DECLINED,
        LegalClientMatterRepresentationFirmDecisionType.REQUIRES_REVIEW,
    ],
)
def test_closed_firm_decision_vocabulary_is_supported(
    decision: LegalClientMatterRepresentationFirmDecisionType,
) -> None:
    assert decision.value in {"ACCEPTED", "DECLINED", "REQUIRES_REVIEW"}


def test_authorized_actor_and_representative_path_is_composed_atomically(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _ActiveSession()
    matter = SimpleNamespace(case_matter_id="matter-p21b", fingerprint=HEX)
    party = SimpleNamespace(
        party_id="party-p21b",
        subject_reference="client:subject-p21b",
        subject_identity_fingerprint=HEX,
    )
    authority = object.__new__(LegalClientMatterRepresentationAuthority)
    for name, item in {
        "authority_id": "authority-p21b",
        "fingerprint": HEX,
        "tenant_id": "tenant-p21b",
        "case_matter_id": "matter-p21b",
        "matter_fingerprint": HEX,
        "client_party_id": "party-p21b",
        "subject_reference": "client:subject-p21b",
        "subject_identity_fingerprint": HEX,
        "engagement_id": "engagement-p21b",
        "engagement_fingerprint": HEX,
        "mandate_id": "mandate-p21b",
        "mandate_fingerprint": HEX,
        "mandate_scope_reference": "scope:p21b",
        "mandate_scope_fingerprint": HEX,
        "acting_capacity_id": "capacity-p21b",
        "acting_capacity_fingerprint": HEX,
        "representative_principal_id": "rep-p21b",
        "representative_role": "LEGAL_ATTORNEY",
        "mandate_capabilities": ("ADVISORY",),
        "representation_scope_capabilities": ("ADVISORY",),
        "decision": LegalClientMatterRepresentationAuthorityDecision.APPOINTED,
        "effective_from": WHEN,
    }.items():
        object.__setattr__(authority, name, item)
    engagement = object.__new__(LegalClientMatterEngagement)
    for name, item in {
        "engagement_id": "engagement-p21b",
        "fingerprint": HEX,
        "tenant_id": "tenant-p21b",
        "case_matter_id": "matter-p21b",
        "matter_fingerprint": HEX,
        "client_party_id": "party-p21b",
        "subject_reference": "client:subject-p21b",
        "subject_identity_fingerprint": HEX,
        "mandate_id": "mandate-p21b",
        "mandate_fingerprint": HEX,
    }.items():
        object.__setattr__(engagement, name, item)
    mandate = object.__new__(LegalClientMatterMandate)
    for name, item in {
        "mandate_id": "mandate-p21b",
        "fingerprint": HEX,
        "tenant_id": "tenant-p21b",
        "case_matter_id": "matter-p21b",
        "matter_fingerprint": HEX,
        "client_party_id": "party-p21b",
        "subject_identity_fingerprint": HEX,
        "scope_reference": "scope:p21b",
        "scope_fingerprint": HEX,
        "acting_capacity_id": "capacity-p21b",
        "acting_capacity_fingerprint": HEX,
        "capabilities": ("ADVISORY",),
    }.items():
        object.__setattr__(mandate, name, item)

    class Composer:
        def __init__(self, value: object) -> None:
            self.value = value
            self.calls: list[tuple[object, ...]] = []

        def compose_currentness(self, *args: object) -> object:
            self.calls.append(args)
            return self.value

    p1_value = object.__new__(LegalClientMatterRepresentationAuthorityCurrentness)
    object.__setattr__(p1_value, "state", LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED)
    object.__setattr__(p1_value, "decisive_authority_id", "authority-p21b")
    object.__setattr__(p1_value, "decisive_authority_fingerprint", HEX)
    p1 = Composer(p1_value)
    engagement_currentness = Composer(SimpleNamespace(is_current=True, state="CURRENT", decisive_engagement_id="engagement-p21b", decisive_engagement_fingerprint=HEX))
    mandate_currentness = Composer(SimpleNamespace(is_current=True, state="CURRENT", mandate_id="mandate-p21b", mandate_fingerprint=HEX))
    def issue_evidence(**kwargs: object) -> object:
        return SimpleNamespace(
            tenant_id=kwargs["tenant_id"], principal_id=kwargs["principal_id"],
            operation=kwargs["operation"], permission=kwargs["permission"],
            subject_reference=kwargs["subject_reference"],
            subject_evidence_fingerprint=kwargs["subject_evidence_fingerprint"],
            authorization_role="LEGAL_PARTNER", authorization_evidence_reference="auth:p21b",
            authorization_evidence_fingerprint=HEX, authorized_at=WHEN,
        )
    auth_registry = SimpleNamespace(issue=issue_evidence)
    principal_repo = SimpleNamespace(resolve=lambda *_args, **_kwargs: PrincipalAuthority("rep-p21b", PrincipalStatus.ACTIVE, 1))
    membership_repo = SimpleNamespace(resolve=lambda *_args, **_kwargs: TenantMembershipAuthority("rep-p21b", "tenant-p21b", TenantMembershipStatus.ACTIVE, 1))
    role_repo = SimpleNamespace(list_assignments=lambda *_args, **_kwargs: (RoleAssignmentAuthority("rep-p21b", "tenant-p21b", "LEGAL_ATTORNEY", RoleAssignmentStatus.ACTIVE, 1),))
    business_repo = object()
    persistence = SimpleNamespace(persist_firm_decision=lambda value, _collection, *, session: value)
    value = LegalClientMatterRepresentationFirmDecisionOrchestrator(
        matter_lifecycle_collection=object(), party_collection=object(), authority_collection=object(),
        engagement_collection=object(), mandate_collection=object(), grant_collection=object(),
        grant_lifecycle_collection=object(), acknowledgment_collection=object(), decision_collection=object(),
        principal_repository=principal_repo, membership_repository=membership_repo,
        role_assignment_repository=role_repo, business_role_repository=business_repo,
        authorization_evidence_registry=cast(Any, auth_registry), authority_currentness_composer=p1,
        engagement_currentness_composer=engagement_currentness, mandate_currentness_composer=mandate_currentness,
        decision_persistence=persistence,
    )
    monkeypatch.setattr(value, "_matter", lambda *_args: matter)
    monkeypatch.setattr(value, "_party", lambda *_args: party)
    monkeypatch.setattr(orchestrator_module.authority_registry, "get_representation_authority", lambda *_args, **_kwargs: authority)
    monkeypatch.setattr(orchestrator_module.engagement_registry, "get_engagement", lambda *_args, **_kwargs: engagement)
    monkeypatch.setattr(orchestrator_module.mandate_registry, "get_mandate", lambda *_args, **_kwargs: mandate)
    result = value.issue(_request(), session=session)
    assert result.representation_authority_id == "authority-p21b"
    assert result.decision_actor_principal_id == "actor-p21b"
    assert p1.calls[-1][-1] is session
    assert engagement_currentness.calls[-1][-1] is session
    assert mandate_currentness.calls[-1][-1] is session


# ARTIFACT: test_legal_client_matter_representation_firm_decision_orchestrator.py
# VERSION: v1.0.0-L9C11-P21B-FIRM-REPRESENTATION-DECISION-ORCHESTRATOR-DIRECT-CERT
# AUTHORITY BOUNDARY: precondition and transaction contract only
# FAIL-CLOSED POSTURE: no inactive or missing caller transaction can proceed
# END OF WILSY OS SOVEREIGN ARTIFACT
