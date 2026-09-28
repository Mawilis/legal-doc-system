"""Direct certificate for L9C11-P25 final Representation formation.

TITLE: WILSY OS Legal Client Matter Final Representation Orchestrator Certificate
VERSION: v1.0.0-L9C11-P25-FINAL-REPRESENTATION-ORCHESTRATOR-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify caller-transaction formation, exact P21A/P22 and
         Engagement/Mandate revalidation, live IAM checks, deterministic scope
         narrowing and one P24 persistence call without upstream writes.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_final_representation_orchestrator.py
COLLABORATION / OWNERSHIP: P24 and all upstream projections remain canonical;
                            this certificate exercises the P25 seam in memory.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: Fake repositories only; no Mongo, network, clock or IAM mutation.
FAIL-CLOSED DECLARATION: Missing, stale, mismatched or widened authority never forms.
"""
from __future__ import annotations

import inspect
from datetime import timedelta
from pathlib import Path
from typing import Any, cast

import pytest

from tests.unit.test_legal_client_matter_final_representation import (
    BASE,
    HEX,
    _authority_direct,
    _engagement,
    _mandate,
    _mandate_currentness,
)
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_client_matter_engagement_currentness import (
    project_legal_client_matter_engagement_currentness,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import (
    LegalClientMatterRepresentationAuthorityCurrentnessState,
    project_legal_client_matter_representation_authority_currentness,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import (
    LegalClientMatterRepresentationFirmDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision_currentness import (
    LegalClientMatterRepresentationFirmDecisionCurrentnessState,
    project_legal_client_matter_representation_firm_decision_currentness,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_final_representation_orchestrator import (
    ELIGIBLE_REPRESENTATIVE_ROLES,
    VERSION,
    LegalClientMatterFinalRepresentationFormationRequest,
    LegalClientMatterFinalRepresentationOrchestrationError,
    LegalClientMatterFinalRepresentationOrchestrator,
)


SESSION = object()


class Tx:
    in_transaction = True


class Composer:
    def __init__(self, result: object) -> None:
        self.result = result
        self.calls: list[tuple[tuple[object, ...], object]] = []

    def compose_currentness(self, *args: object) -> object:
        self.calls.append((args, args[-1]))
        return self.result


class AuthorityReader:
    def __init__(self, value: object) -> None:
        self.value = value
        self.calls: list[object] = []

    def get_representation_authority(self, *args: object, **kwargs: object) -> object:
        self.calls.append(kwargs.get("session"))
        return self.value


class DecisionReader:
    def __init__(self, value: object) -> None:
        self.value = value
        self.calls: list[object] = []

    def get_firm_decision(self, *args: object, **kwargs: object) -> object:
        self.calls.append(kwargs.get("session"))
        return self.value


class EngagementReader:
    def __init__(self, value: object) -> None:
        self.value = value
        self.calls: list[object] = []

    def get_engagement(self, *args: object, **kwargs: object) -> object:
        self.calls.append(kwargs.get("session"))
        return self.value


class MandateReader:
    def __init__(self, value: object) -> None:
        self.value = value
        self.calls: list[object] = []

    def get_mandate(self, *args: object, **kwargs: object) -> object:
        self.calls.append(kwargs.get("session"))
        return self.value


class Repository:
    def __init__(self, value: object) -> None:
        self.value = value
        self.calls: list[tuple[tuple[object, ...], object]] = []

    def resolve(self, *args: object, session: object = None) -> object:
        self.calls.append((args, session))
        return self.value


class Writer:
    def __init__(self) -> None:
        self.values: list[tuple[Any, object, object]] = []

    def persist_final_representation(self, value: object, collection: object, *, session: object) -> object:
        self.values.append((value, collection, session))
        return value


class DivergentReplayWriter(Writer):
    def persist_final_representation(self, value: object, collection: object, *, session: object) -> object:
        previous = cast(Any, self.values[0][0]) if self.values else None
        if previous is not None and previous.idempotency_key == cast(Any, value).idempotency_key and previous != value:
            raise RuntimeError("L9C11_P24_IDEMPOTENCY_COLLISION")
        return super().persist_final_representation(value, collection, session=session)


def _parts(role: str = "LEGAL_ATTORNEY", authority_scope: tuple[str, ...] = ("ADVISORY", "NEGOTIATION")) -> dict[str, Any]:
    mandate = _mandate()
    engagement = _engagement(mandate)
    authority = _authority_direct(role, authority_scope)
    decision = LegalClientMatterRepresentationFirmDecision.from_client_authority(
        client_authority=authority,
        decision="ACCEPTED",
        decision_actor_principal_id="principal-firm-p24",
        authorization_evidence_reference="evidence:firm-auth-p25",
        authorization_evidence_fingerprint=HEX,
        source_evidence_reference="evidence:firm-decision-p25",
        source_evidence_fingerprint=HEX,
        occurred_at=BASE + timedelta(minutes=5),
        effective_from=BASE + timedelta(minutes=5),
        idempotency_key="idempotency:decision-p25",
    )
    evaluated_at = BASE + timedelta(hours=1)
    p1 = project_legal_client_matter_representation_authority_currentness(
        tenant_id=authority.tenant_id, case_matter_id=authority.case_matter_id,
        matter_fingerprint=authority.matter_fingerprint, client_party_id=authority.client_party_id,
        subject_identity_fingerprint=authority.subject_identity_fingerprint,
        representative_principal_id=authority.representative_principal_id,
        evaluated_at=evaluated_at, authorities=(authority,),
    )
    p2 = project_legal_client_matter_representation_firm_decision_currentness(
        tenant_id=decision.tenant_id, case_matter_id=decision.case_matter_id,
        matter_fingerprint=decision.matter_fingerprint, client_party_id=decision.client_party_id,
        subject_identity_fingerprint=decision.subject_identity_fingerprint,
        representation_authority_id=authority.authority_id,
        representation_authority_fingerprint=authority.fingerprint,
        representative_principal_id=authority.representative_principal_id,
        representative_role=authority.representative_role,
        evaluated_at=evaluated_at, decisions=(decision,),
    )
    engagement_currentness = project_legal_client_matter_engagement_currentness(
        tenant_id=engagement.tenant_id, case_matter_id=engagement.case_matter_id,
        matter_fingerprint=engagement.matter_fingerprint, client_party_id=engagement.client_party_id,
        subject_identity_fingerprint=engagement.subject_identity_fingerprint,
        evaluated_at=evaluated_at, engagements=(engagement,),
    )
    principal = PrincipalAuthority(authority.representative_principal_id, PrincipalStatus.ACTIVE, 1)
    membership = TenantMembershipAuthority(authority.representative_principal_id, authority.tenant_id, TenantMembershipStatus.ACTIVE, 1)
    assignment = RoleAssignmentAuthority(authority.representative_principal_id, authority.tenant_id, role, RoleAssignmentStatus.ACTIVE, 1)
    return {
        "mandate": mandate, "engagement": engagement, "authority": authority, "decision": decision,
        "p1": p1, "p2": p2, "engagement_currentness": engagement_currentness,
        "mandate_currentness": _mandate_currentness(mandate), "principal": principal,
        "membership": membership, "assignment": assignment, "evaluated_at": evaluated_at,
    }


def _request(parts: dict[str, Any], **changes: object) -> LegalClientMatterFinalRepresentationFormationRequest:
    authority = parts["authority"]
    values: dict[str, Any] = {
        "tenant_id": authority.tenant_id, "case_matter_id": authority.case_matter_id,
        "matter_fingerprint": authority.matter_fingerprint, "client_party_id": authority.client_party_id,
        "subject_identity_fingerprint": authority.subject_identity_fingerprint,
        "representative_principal_id": authority.representative_principal_id,
        "evaluated_at": parts["evaluated_at"], "effective_from": BASE + timedelta(minutes=6),
        "occurred_at": BASE + timedelta(minutes=7), "idempotency_key": "idempotency:final-p25",
        "representative_eligibility_reference": "evidence:eligibility-p25",
        "representative_eligibility_fingerprint": HEX, "source_evidence_reference": "evidence:final-p25",
        "source_evidence_fingerprint": HEX, "requested_scope_capabilities": None,
    }
    values.update(changes)
    return LegalClientMatterFinalRepresentationFormationRequest(**values)


def _build(**changes: object) -> tuple[LegalClientMatterFinalRepresentationOrchestrator, dict[str, Any], dict[str, Any]]:
    parts = _parts(cast(str, changes.pop("role", "LEGAL_ATTORNEY")), cast(tuple[str, ...], changes.pop("authority_scope", ("ADVISORY", "NEGOTIATION"))))
    parts.update(changes)
    authority_reader = AuthorityReader(parts["authority"])
    decision_reader = DecisionReader(parts["decision"])
    engagement_reader = EngagementReader(parts["engagement"])
    mandate_reader = MandateReader(parts["mandate"])
    writer = changes.pop("writer_override", None) or Writer()
    principal_repo = Repository(parts["principal"])
    membership_repo = Repository(parts["membership"])
    assignment_repo = Repository(parts["assignment"])
    composers = {
        "p1": Composer(parts["p1"]), "p2": Composer(parts["p2"]),
        "engagement": Composer(parts["engagement_currentness"]), "mandate": Composer(parts["mandate_currentness"]),
    }
    orchestrator = LegalClientMatterFinalRepresentationOrchestrator(
        authority_currentness_composer=composers["p1"], decision_currentness_composer=composers["p2"],
        engagement_currentness_composer=composers["engagement"], mandate_currentness_composer=composers["mandate"],
        authority_collection=object(), decision_collection=object(), engagement_collection=object(),
        mandate_collection=object(), final_representation_collection=object(),
        principal_repository=principal_repo, membership_repository=membership_repo,
        role_assignment_repository=assignment_repo, authority_reader=authority_reader,
        decision_reader=decision_reader, engagement_reader=engagement_reader,
        mandate_reader=mandate_reader, representation_writer=writer,
    )
    return orchestrator, parts, {"composers": composers, "readers": (authority_reader, decision_reader, engagement_reader, mandate_reader), "repos": (principal_repo, membership_repo, assignment_repo), "writer": writer}


def test_version_request_contract_and_authority_fields_are_absent() -> None:
    assert VERSION == "v1.0.0-L9C11-P25-FINAL-REPRESENTATION-ORCHESTRATOR"
    assert ELIGIBLE_REPRESENTATIVE_ROLES == frozenset({"LEGAL_ATTORNEY", "LEGAL_PARTNER"})
    fields = set(LegalClientMatterFinalRepresentationFormationRequest.__dataclass_fields__)
    assert {"representative_role", "representation_scope_capabilities", "decision"}.isdisjoint(fields)


def test_forms_p24_with_exact_session_and_narrowed_scope() -> None:
    orchestrator, parts, doubles = _build()
    result = orchestrator.form(_request(parts, requested_scope_capabilities=("ADVISORY",)), session=Tx())
    assert result.representation_scope_capabilities == ("ADVISORY",)
    assert doubles["writer"].values[0][2].__class__ is Tx
    assert all(call[1].__class__ is Tx for call in doubles["composers"].values() for call in call.calls)
    assert all(item[1].__class__ is Tx for item in doubles["repos"] for item in item.calls)
    assert all(session.__class__ is Tx for reader in doubles["readers"] for session in reader.calls)


@pytest.mark.parametrize("state", [state for state in LegalClientMatterRepresentationAuthorityCurrentnessState if state is not LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED])
def test_non_appointed_p1_is_rejected(state: LegalClientMatterRepresentationAuthorityCurrentnessState) -> None:
    orchestrator, parts, _ = _build()
    object.__setattr__(parts["p1"], "state", state)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError, match="P1_APPOINTED_REQUIRED"):
        orchestrator.form(_request(parts), session=Tx())


@pytest.mark.parametrize("state", [state for state in LegalClientMatterRepresentationFirmDecisionCurrentnessState if state is not LegalClientMatterRepresentationFirmDecisionCurrentnessState.ACCEPTED])
def test_non_accepted_p2_is_rejected(state: LegalClientMatterRepresentationFirmDecisionCurrentnessState) -> None:
    orchestrator, parts, _ = _build()
    object.__setattr__(parts["p2"], "state", state)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError, match="P2_ACCEPTED_REQUIRED"):
        orchestrator.form(_request(parts), session=Tx())


@pytest.mark.parametrize("status", [PrincipalStatus.REVOKED, PrincipalStatus.SUSPENDED])
def test_inactive_principal_is_rejected(status: PrincipalStatus) -> None:
    principal = PrincipalAuthority("principal-representative-p24", status, 2)
    orchestrator, parts, _ = _build(principal=principal)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError, match="PRINCIPAL_INACTIVE"):
        orchestrator.form(_request(parts), session=Tx())


def test_inactive_membership_and_role_assignment_are_rejected() -> None:
    for key, value, expected in (
        ("membership", TenantMembershipAuthority("principal-representative-p24", "tenant-p24", TenantMembershipStatus.SUSPENDED, 2), "MEMBERSHIP_INACTIVE"),
        ("assignment", RoleAssignmentAuthority("principal-representative-p24", "tenant-p24", "LEGAL_ATTORNEY", RoleAssignmentStatus.REVOKED, 2), "ROLE_ASSIGNMENT_INVALID"),
    ):
        orchestrator, parts, _ = _build(**{key: value})
        with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError, match=expected):
            orchestrator.form(_request(parts), session=Tx())


def test_paralegal_role_and_scope_widening_are_rejected() -> None:
    orchestrator, parts, _ = _build(role="PARALEGAL")
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError, match="ROLE_INELIGIBLE"):
        orchestrator.form(_request(parts), session=Tx())
    orchestrator, parts, _ = _build()
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError, match="SCOPE_WIDENING_FORBIDDEN"):
        orchestrator.form(_request(parts, requested_scope_capabilities=("ADVISORY", "LITIGATION_PREPARATION")), session=Tx())


def test_lineage_or_binding_mismatch_is_rejected() -> None:
    orchestrator, parts, _ = _build()
    object.__setattr__(parts["p2"], "representative_role", "LEGAL_PARTNER")
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError, match="P2_LINEAGE_MISMATCH"):
        orchestrator.form(_request(parts), session=Tx())
    orchestrator, parts, _ = _build()
    object.__setattr__(parts["p1"], "decisive_authority_fingerprint", "b" * 128)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError, match="P1_BINDING_MISMATCH"):
        orchestrator.form(_request(parts), session=Tx())


def test_engagement_and_mandate_noncurrent_are_rejected() -> None:
    for key in ("engagement_currentness", "mandate_currentness"):
        orchestrator, parts, _ = _build()
        value = parts[key]
        object.__setattr__(value, "state", "AMBIGUOUS")
        with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError, match=f"{key.split('_')[0].upper()}_CURRENT_REQUIRED"):
            orchestrator.form(_request(parts), session=Tx())


def test_invalid_session_and_chronology_fail_before_write() -> None:
    orchestrator, parts, doubles = _build()
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError, match="ACTIVE_TRANSACTION_REQUIRED"):
        orchestrator.form(_request(parts), session=object())
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError, match="OCCURRED_BEFORE_EFFECTIVE"):
        _request(parts, occurred_at=BASE, effective_from=BASE + timedelta(minutes=8))
    assert doubles["writer"].values == []


def test_partner_role_is_accepted_and_replay_is_deterministic() -> None:
    orchestrator, parts, doubles = _build(role="LEGAL_PARTNER")
    request = _request(parts)
    first = orchestrator.form(request, session=Tx())
    second = orchestrator.form(request, session=Tx())
    assert first == second
    assert first.representative_role == "LEGAL_PARTNER"
    assert len(doubles["writer"].values) == 2


def test_divergent_idempotency_is_left_to_the_immutable_registry_boundary() -> None:
    writer = DivergentReplayWriter()
    orchestrator, parts, _ = _build(writer_override=writer)
    request = _request(parts)
    orchestrator.form(request, session=Tx())
    with pytest.raises(RuntimeError, match="IDEMPOTENCY_COLLISION"):
        orchestrator.form(_request(parts, source_evidence_reference="evidence:divergent-p25"), session=Tx())


def test_no_transaction_lifecycle_or_upstream_write_is_present() -> None:
    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_final_representation_orchestrator.py").read_text()
    tree = inspect.getsource(LegalClientMatterFinalRepresentationOrchestrator.form)
    assert all(token not in tree for token in ("start_transaction", "commit_transaction", "abort_transaction"))
    assert "insert_one" not in source and "update_one" not in source and "delete_one" not in source
    assert "datetime.now" not in source and "utcnow" not in source
    assert "authorization_evidence" not in source.lower()


def test_dependencies_are_required_and_writer_receives_p24_value() -> None:
    parts = _parts()
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError, match="DEPENDENCY_REQUIRED"):
        LegalClientMatterFinalRepresentationOrchestrator(
            authority_currentness_composer=None, decision_currentness_composer=object(),
            engagement_currentness_composer=object(), mandate_currentness_composer=object(),
            authority_collection=object(), decision_collection=object(), engagement_collection=object(),
            mandate_collection=object(), final_representation_collection=object(),
            principal_repository=object(), membership_repository=object(), role_assignment_repository=object(),
        )
    orchestrator, _, doubles = _build()
    result = orchestrator.form(_request(parts), session=Tx())
    assert doubles["writer"].values[0][0] == result


def test_direct_certificate_has_no_placeholder_and_exact_two_file_intent() -> None:
    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_final_representation_orchestrator.py").read_text()
    assert "TODO" not in source and "FIXME" not in source and "pass" not in source
    assert "P24" in source and "P21A" in source and "P22" in source
