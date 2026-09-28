"""Direct certificate for the P2 Court operation-preparation orchestrator.

TITLE: WILSY OS Court Operation Preparation Orchestrator Certificate
VERSION: v1.0.0-L9C12-P2-COURT-OPERATION-PREPARATION-ORCHESTRATOR-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify caller-owned transaction propagation, exact P24/P21A/P22,
         Engagement/Mandate and IAM revalidation, bounded Court scope and one
         P1 persistence call without external Court or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_court_operation_preparation_orchestrator.py
TRANSACTION BOUNDARY: In-memory fakes only; no Mongo, network, clock or IAM mutation.
FAIL-CLOSED DECLARATION: Missing, stale, mismatched or widened authority rejects.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tests.unit.test_legal_client_matter_final_representation import _engagement, _mandate_currentness
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_client_matter_engagement_currentness import project_legal_client_matter_engagement_currentness
from tools.eos.legal_operations.domain.legal_client_matter_mandate import LegalClientMatterMandate
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import LegalClientMatterRepresentationAuthority
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import project_legal_client_matter_representation_authority_currentness
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import LegalClientMatterRepresentationFirmDecision
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision_currentness import project_legal_client_matter_representation_firm_decision_currentness
from tools.eos.legal_operations.domain.legal_client_matter_final_representation import LegalClientMatterFinalRepresentation
from tools.eos.legal_operations.domain.legal_court_operation_preparation import LegalCourtOperationPreparationState, LegalCourtOperationType
from tools.eos.legal_operations.orchestration.legal_court_operation_preparation_orchestrator import (
    COURT_SCOPE_DERIVATION_MODEL,
    VERSION,
    LegalCourtOperationPreparationOrchestrationError,
    LegalCourtOperationPreparationOrchestrator,
    LegalCourtOperationPreparationRequest,
)


BASE = datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc)
HEX = "a" * 128
class Tx:
    in_transaction = True


SESSION = Tx()


class Composer:
    def __init__(self, value: object) -> None:
        self.value = value
        self.calls: list[tuple[tuple[object, ...], object]] = []

    def compose_currentness(self, *args: object) -> object:
        self.calls.append((args, args[-1]))
        return self.value


class Reader:
    def __init__(self, value: object) -> None:
        self.value = value
        self.calls: list[object] = []

    def get_final_representation(self, *args: object, **kwargs: object) -> object:
        self.calls.append(kwargs.get("session"))
        return self.value


class EngagementReader(Reader):
    def get_engagement(self, *args: object, **kwargs: object) -> object:
        self.calls.append(kwargs.get("session"))
        return self.value


class MandateReader(Reader):
    def get_mandate(self, *args: object, **kwargs: object) -> object:
        self.calls.append(kwargs.get("session"))
        return self.value


class Repository:
    def __init__(self, value: object) -> None:
        self.value = value
        self.calls: list[tuple[tuple[object, ...], object]] = []

    def resolve(self, *args: object, session: object = None, **kwargs: object) -> object:
        self.calls.append((args, session))
        return self.value


class Writer:
    def __init__(self) -> None:
        self.calls: list[tuple[object, object, object]] = []

    def persist_court_operation_preparation(self, value: object, collection: object, *, session: object) -> object:
        self.calls.append((value, collection, session))
        return value


def _mandate() -> LegalClientMatterMandate:
    return LegalClientMatterMandate(
        mandate_id="mandate-p2", tenant_id="tenant-p2", case_matter_id="matter-p2",
        matter_fingerprint=HEX, client_party_id="party-p2", subject_identity_fingerprint=HEX,
        grant_actor_principal_id="principal-client-p2", acting_capacity_id="capacity-p2",
        acting_capacity_fingerprint=HEX, breadth="LIMITED", scope_reference="scope:p2",
        scope_fingerprint=HEX, capabilities=["ADVISORY", "LITIGATION_PREPARATION", "COURT_FILING_PREPARATION"],
        source_evidence_reference="evidence:mandate-p2", source_evidence_fingerprint=HEX,
        client_grant_reference="grant-p2", client_grant_fingerprint=HEX,
        firm_acknowledgment_reference="ack-p2", firm_acknowledgment_fingerprint=HEX,
        occurred_at=BASE + timedelta(minutes=1), effective_from=BASE + timedelta(minutes=2),
        effective_until=None, idempotency_key="idempotency:mandate-p2",
    )


def _parts() -> dict[str, Any]:
    mandate = _mandate()
    engagement = _engagement(mandate)
    authority = LegalClientMatterRepresentationAuthority(
        authority_id="authority-p2", tenant_id=mandate.tenant_id, case_matter_id=mandate.case_matter_id,
        matter_fingerprint=mandate.matter_fingerprint, client_party_id=mandate.client_party_id,
        subject_reference=engagement.subject_reference, subject_identity_fingerprint=mandate.subject_identity_fingerprint,
        engagement_id=engagement.engagement_id, engagement_fingerprint=engagement.fingerprint,
        mandate_id=mandate.mandate_id, mandate_fingerprint=mandate.fingerprint,
        mandate_scope_reference=mandate.scope_reference, mandate_scope_fingerprint=mandate.scope_fingerprint,
        mandate_capabilities=mandate.capabilities, acting_capacity_id=mandate.acting_capacity_id,
        acting_capacity_fingerprint=mandate.acting_capacity_fingerprint, representative_principal_id="principal-representative-p2",
        representative_role="LEGAL_ATTORNEY", representation_scope_capabilities=("LITIGATION_PREPARATION",),
        decision="APPOINTED", appointing_principal_id="principal-client-p2",
        source_evidence_reference="evidence:authority-p2", source_evidence_fingerprint=HEX,
        authorization_evidence_reference="evidence:authority-auth-p2", authorization_evidence_fingerprint=HEX,
        occurred_at=BASE + timedelta(minutes=4), effective_from=BASE + timedelta(minutes=4),
        effective_until=None, idempotency_key="idempotency:authority-p2",
    )
    decision = LegalClientMatterRepresentationFirmDecision.from_client_authority(
        client_authority=authority, decision="ACCEPTED", decision_actor_principal_id="principal-firm-p2",
        authorization_evidence_reference="evidence:firm-auth-p2", authorization_evidence_fingerprint=HEX,
        source_evidence_reference="evidence:firm-decision-p2", source_evidence_fingerprint=HEX,
        occurred_at=BASE + timedelta(minutes=5), effective_from=BASE + timedelta(minutes=5),
        idempotency_key="idempotency:decision-p2",
    )
    evaluated = BASE + timedelta(hours=1)
    p1 = project_legal_client_matter_representation_authority_currentness(
        tenant_id=authority.tenant_id, case_matter_id=authority.case_matter_id, matter_fingerprint=authority.matter_fingerprint,
        client_party_id=authority.client_party_id, subject_identity_fingerprint=authority.subject_identity_fingerprint,
        representative_principal_id=authority.representative_principal_id, evaluated_at=evaluated, authorities=(authority,),
    )
    p2 = project_legal_client_matter_representation_firm_decision_currentness(
        tenant_id=decision.tenant_id, case_matter_id=decision.case_matter_id, matter_fingerprint=decision.matter_fingerprint,
        client_party_id=decision.client_party_id, subject_identity_fingerprint=decision.subject_identity_fingerprint,
        representation_authority_id=authority.authority_id, representation_authority_fingerprint=authority.fingerprint,
        representative_principal_id=authority.representative_principal_id, representative_role=authority.representative_role,
        evaluated_at=evaluated, decisions=(decision,),
    )
    engagement_currentness = project_legal_client_matter_engagement_currentness(
        tenant_id=engagement.tenant_id, case_matter_id=engagement.case_matter_id, matter_fingerprint=engagement.matter_fingerprint,
        client_party_id=engagement.client_party_id, subject_identity_fingerprint=engagement.subject_identity_fingerprint,
        evaluated_at=evaluated, engagements=(engagement,),
    )
    representation = LegalClientMatterFinalRepresentation.from_canonical(
        authority=authority, authority_currentness=p1, firm_decision=decision, firm_decision_currentness=p2,
        engagement=engagement, engagement_currentness=engagement_currentness, mandate=mandate,
        mandate_currentness=_mandate_currentness(mandate), representation_scope_capabilities=("LITIGATION_PREPARATION",),
        representative_eligibility_reference="evidence:eligibility-p2", representative_eligibility_fingerprint=HEX,
        source_evidence_reference="evidence:representation-p2", source_evidence_fingerprint=HEX,
        effective_from=BASE + timedelta(minutes=6), occurred_at=BASE + timedelta(minutes=7), idempotency_key="idempotency:representation-p2",
    )
    principal = PrincipalAuthority(authority.representative_principal_id, PrincipalStatus.ACTIVE, 1)
    membership = TenantMembershipAuthority(authority.representative_principal_id, authority.tenant_id, TenantMembershipStatus.ACTIVE, 1)
    assignment = RoleAssignmentAuthority(authority.representative_principal_id, authority.tenant_id, authority.representative_role, RoleAssignmentStatus.ACTIVE, 1)
    mandate_currentness = _mandate_currentness(mandate)
    return locals()


def _request(parts: dict[str, Any], **changes: object) -> LegalCourtOperationPreparationRequest:
    values: dict[str, object] = {
        "tenant_id": parts["representation"].tenant_id, "case_matter_id": parts["representation"].case_matter_id,
        "matter_fingerprint": parts["representation"].matter_fingerprint, "final_representation_id": parts["representation"].representation_id,
        "operation_type": LegalCourtOperationType.COURT_FILING_PREPARATION, "target_court_reference": "court:p2",
        "target_jurisdiction_reference": "jurisdiction:p2", "document_evidence_lineage": ("document:p2",),
        "requested_scope_capabilities": ("COURT_FILING_PREPARATION",), "preparation_state": LegalCourtOperationPreparationState.PREPARATION_REQUIRED,
        "source_evidence_reference": "evidence:request-p2", "source_evidence_fingerprint": HEX,
        "provenance_reference": "provenance:p2", "prepared_at": BASE + timedelta(minutes=8),
        "occurred_at": BASE + timedelta(minutes=9), "evaluated_at": parts["evaluated"], "idempotency_key": "idempotency:preparation-p2",
    }
    values.update(changes)
    return LegalCourtOperationPreparationRequest(**cast(Any, values))


def _build(**changes: object) -> tuple[LegalCourtOperationPreparationOrchestrator, dict[str, Any], dict[str, Any]]:
    parts = _parts()
    parts.update(changes)
    writer = Writer()
    readers = {"representation": Reader(parts["representation"]), "engagement": EngagementReader(parts["engagement"]), "mandate": MandateReader(parts["mandate"])}
    repos = {"principal": Repository(parts["principal"]), "membership": Repository(parts["membership"]), "assignment": Repository(parts["assignment"])}
    composers = {"p1": Composer(parts["p1"]), "p2": Composer(parts["p2"]), "engagement": Composer(parts["engagement_currentness"]), "mandate": Composer(parts["mandate_currentness"])}
    orchestrator = LegalCourtOperationPreparationOrchestrator(
        authority_currentness_composer=composers["p1"], decision_currentness_composer=composers["p2"],
        engagement_currentness_composer=composers["engagement"], mandate_currentness_composer=composers["mandate"],
        representation_collection=object(), authority_collection=object(), decision_collection=object(),
        engagement_collection=object(), mandate_collection=object(), principal_repository=repos["principal"],
        preparation_collection=object(),
        membership_repository=repos["membership"], role_assignment_repository=repos["assignment"],
        principal_collection=object(), membership_collection=object(), role_assignment_collection=object(),
        representation_reader=readers["representation"], engagement_reader=readers["engagement"], mandate_reader=readers["mandate"], preparation_writer=writer,
    )
    return orchestrator, parts, {"writer": writer, "readers": readers, "repos": repos, "composers": composers}


def test_version_scope_model_and_request_are_bounded() -> None:
    assert VERSION == "v1.0.0-L9C12-P2-COURT-OPERATION-PREPARATION-ORCHESTRATOR"
    assert "LITIGATION_PREPARATION" in COURT_SCOPE_DERIVATION_MODEL
    assert LegalCourtOperationPreparationRequest.__dataclass_fields__["requested_scope_capabilities"]
    assert LegalCourtOperationPreparationRequest.__dataclass_fields__.get("representative_role") is None


def test_happy_path_persists_one_preparation_and_propagates_session() -> None:
    orchestrator, parts, state = _build()
    result = orchestrator.prepare(_request(parts), session=SESSION)
    assert result.final_representation_id == parts["representation"].representation_id
    assert len(state["writer"].calls) == 1
    assert state["writer"].calls[0][2] is SESSION
    assert all(call[1] is SESSION for composer in state["composers"].values() for call in composer.calls)
    assert all(call is SESSION for reader in state["readers"].values() for call in reader.calls)
    assert all(call[1] is SESSION for repo in state["repos"].values() for call in repo.calls)


@pytest.mark.parametrize("state", ["PREPARATION_REQUIRED", "READY_FOR_EXTERNAL_HANDOFF", "HANDED_OFF_EXTERNALLY", "EXTERNAL_EVIDENCE_PENDING", "EXTERNAL_EVIDENCE_RECORDED", "BLOCKED"])
def test_all_p1_states_are_accepted_as_internal_preparation(state: str) -> None:
    orchestrator, parts, _ = _build()
    result = orchestrator.prepare(_request(parts, preparation_state=state), session=SESSION)
    assert getattr(result.preparation_state, "value", result.preparation_state) == state


@pytest.mark.parametrize("state", ["NO_APPOINTMENT", "DECLINED", "REQUIRES_REVIEW", "AMBIGUOUS", "CORRUPT_BLOCKED", "EXPIRED", "SUPERSEDED"])
def test_non_appointed_p21a_fails_closed(state: str) -> None:
    orchestrator, parts, _ = _build()
    object.__setattr__(parts["p1"], "state", state)
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        orchestrator.prepare(_request(parts), session=SESSION)


@pytest.mark.parametrize("state", ["NO_DECISION", "DECLINED", "REQUIRES_REVIEW", "AMBIGUOUS", "CORRUPT_BLOCKED"])
def test_non_accepted_p22_fails_closed(state: str) -> None:
    orchestrator, parts, _ = _build()
    object.__setattr__(parts["p2"], "state", state)
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        orchestrator.prepare(_request(parts), session=SESSION)


def test_missing_or_inactive_transaction_is_rejected_before_reads() -> None:
    orchestrator, parts, _ = _build()
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        orchestrator.prepare(_request(parts), session=None)
    class Inactive: in_transaction = False
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        orchestrator.prepare(_request(parts), session=Inactive())


@pytest.mark.parametrize("role", ["PARALEGAL", "SECRETARY"])
def test_ineligible_role_fails_closed(role: str) -> None:
    orchestrator, parts, _ = _build()
    object.__setattr__(parts["representation"], "representative_role", role)
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        orchestrator.prepare(_request(parts), session=SESSION)


def test_p24_lineage_scope_and_operation_mismatches_fail_closed() -> None:
    orchestrator, parts, _ = _build()
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        orchestrator.prepare(_request(parts, matter_fingerprint="b" * 128), session=SESSION)
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        _request(parts, requested_scope_capabilities=("COURT_FILING_PREPARATION", "LITIGATION_PREPARATION"))
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        _request(parts, operation_type="COURT_HEARING")


def test_no_external_authority_or_clock_and_exact_public_api() -> None:
    source = Path("tools/eos/legal_operations/orchestration/legal_court_operation_preparation_orchestrator.py").read_text()
    assert "requests" not in source.lower()
    assert "httpx" not in source.lower()
    assert "datetime.now" not in source
    assert "session.commit(" not in source
    assert "session.abort(" not in source
    assert not hasattr(LegalCourtOperationPreparationOrchestrator, "submit_to_court")
    assert not hasattr(LegalCourtOperationPreparationOrchestrator, "authorize_payment")


def test_missing_upstream_currentness_or_iam_fails_closed() -> None:
    orchestrator, parts, _ = _build(engagement_currentness=SimpleNamespace(is_current=False))
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        orchestrator.prepare(_request(parts), session=SESSION)
    orchestrator, parts, _ = _build(principal=PrincipalAuthority("principal-representative-p2", PrincipalStatus.SUSPENDED, 1))
    with pytest.raises(LegalCourtOperationPreparationOrchestrationError):
        orchestrator.prepare(_request(parts), session=SESSION)


def test_artifact_has_sovereign_seal_and_no_placeholder() -> None:
    source = Path("tools/eos/legal_operations/orchestration/legal_court_operation_preparation_orchestrator.py").read_text()
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source
    assert "TODO" not in source and "FIXME" not in source and "pass #" not in source


# ARTIFACT: test_legal_court_operation_preparation_orchestrator.py
# VERSION: v1.0.0-L9C12-P2-COURT-OPERATION-PREPARATION-ORCHESTRATOR-CERT
# AUTHORITY BOUNDARY: direct P2 orchestration certificate only
# FAIL-CLOSED POSTURE: prerequisite, scope, transaction, IAM and side-effect boundaries are asserted
# END OF WILSY OS SOVEREIGN ARTIFACT
