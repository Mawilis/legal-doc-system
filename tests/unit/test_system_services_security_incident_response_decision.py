from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.system_services.security_incident_response_decision import (
    SecurityIncidentResponseAction,
    SecurityIncidentResponseDecision,
    SecurityIncidentResponseDecisionError,
    SecurityIncidentResponseDecisionStatus,
)


NOW = datetime(2026, 11, 5, 10, 0, tzinfo=timezone.utc)


def pending() -> SecurityIncidentResponseDecision:
    return SecurityIncidentResponseDecision(
        decision_id="decision-1",
        incident_id="incident-1",
        tenant_id="tenant-1",
        target_principal_id="principal-target",
        action=SecurityIncidentResponseAction.PASSWORD_RESET,
        requested_by_principal_id="principal-responder",
        requested_at=NOW,
        request_evidence_reference="incident-evidence-1",
    )


def test_request_is_pending_and_contains_no_execution_authority() -> None:
    value = pending()
    assert value.status is SecurityIncidentResponseDecisionStatus.PENDING
    assert value.revision == 0
    assert value.decided_by_principal_id is None
    assert not hasattr(value, "password")
    assert not hasattr(value, "recovery_token")
    assert not hasattr(value, "session_token")
    assert not hasattr(value, "execute")


def test_independent_approval_creates_terminal_decision_only() -> None:
    approved = pending().decide(
        approved=True,
        decided_by_principal_id="principal-independent-approver",
        decided_at=NOW + timedelta(minutes=2),
        decision_evidence_reference="governance-approval-2026-11-05",
        expected_revision=0,
    )
    assert approved.status is SecurityIncidentResponseDecisionStatus.APPROVED
    assert approved.revision == 1
    assert approved.decided_by_principal_id == "principal-independent-approver"
    assert approved.action is SecurityIncidentResponseAction.PASSWORD_RESET
    assert not hasattr(approved, "execute")


def test_independent_rejection_is_also_terminal() -> None:
    rejected = pending().decide(
        approved=False,
        decided_by_principal_id="principal-independent-approver",
        decided_at=NOW + timedelta(minutes=1),
        decision_evidence_reference="governance-rejection-2026-11-05",
        expected_revision=0,
    )
    assert rejected.status is SecurityIncidentResponseDecisionStatus.REJECTED
    assert rejected.revision == 1


def test_requester_cannot_approve_or_reject_own_request() -> None:
    with pytest.raises(
        SecurityIncidentResponseDecisionError,
        match="INDEPENDENT_DECISION_MAKER_REQUIRED",
    ):
        pending().decide(
            approved=True,
            decided_by_principal_id="principal-responder",
            decided_at=NOW + timedelta(minutes=1),
            decision_evidence_reference="self-approval",
            expected_revision=0,
        )


def test_stale_revision_and_second_decision_are_rejected() -> None:
    value = pending()
    with pytest.raises(SecurityIncidentResponseDecisionError, match="DECISION_REVISION_CONFLICT"):
        value.decide(
            approved=True,
            decided_by_principal_id="principal-approver",
            decided_at=NOW + timedelta(minutes=1),
            decision_evidence_reference="approval-1",
            expected_revision=1,
        )
    approved = value.decide(
        approved=True,
        decided_by_principal_id="principal-approver",
        decided_at=NOW + timedelta(minutes=1),
        decision_evidence_reference="approval-1",
        expected_revision=0,
    )
    with pytest.raises(SecurityIncidentResponseDecisionError, match="DECISION_REVISION_CONFLICT"):
        approved.decide(
            approved=False,
            decided_by_principal_id="principal-second-approver",
            decided_at=NOW + timedelta(minutes=2),
            decision_evidence_reference="reversal",
            expected_revision=1,
        )


def test_decision_cannot_precede_request_or_lack_governance_evidence() -> None:
    with pytest.raises(SecurityIncidentResponseDecisionError, match="DECISION_PRECEDES_REQUEST"):
        pending().decide(
            approved=True,
            decided_by_principal_id="principal-approver",
            decided_at=NOW - timedelta(seconds=1),
            decision_evidence_reference="approval-1",
            expected_revision=0,
        )
    with pytest.raises(SecurityIncidentResponseDecisionError, match="DECISION_EVIDENCE_REFERENCE_INVALID"):
        pending().decide(
            approved=True,
            decided_by_principal_id="principal-approver",
            decided_at=NOW + timedelta(minutes=1),
            decision_evidence_reference="",
            expected_revision=0,
        )


def test_system_permission_revocation_is_recorded_as_a_separate_canonical_action() -> None:
    value = SecurityIncidentResponseDecision(
        decision_id="decision-2",
        incident_id="incident-2",
        tenant_id="tenant-2",
        target_principal_id="principal-2",
        action=SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION,
        requested_by_principal_id="responder-2",
        requested_at=NOW,
        request_evidence_reference="incident-evidence-2",
    )
    assert value.action is SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION
