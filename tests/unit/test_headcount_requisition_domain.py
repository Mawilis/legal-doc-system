from datetime import datetime, timezone

import pytest

from tools.eos.saas.domain.headcount_requisition import (
    HeadcountApproval,
    HeadcountRequisition,
    RequisitionDecision,
    RequisitionError,
    RequisitionStatus,
)


def requisition(**changes):
    values = {
        "tenant_id": "WILSYTENANT-4CD2FZ4O",
        "requisition_id": "REQ-WIL-0001",
        "department_id": "ENGINEERING",
        "position_title": "Senior Platform Engineer",
        "employment_type": "PERMANENT",
        "work_location": "HYBRID",
        "headcount": 1,
        "business_justification": "Approved roadmap capacity for platform reliability.",
        "requested_by_principal_id": "principal-requester",
    }
    values.update(changes)
    return HeadcountRequisition(**values)


def approval(actor="principal-approver", decision=RequisitionDecision.APPROVE):
    return HeadcountApproval(
        decision_id="DECISION-0001",
        actor_principal_id=actor,
        decision=decision,
        reason="Independent headcount review completed.",
        decided_at=datetime(2026, 11, 7, tzinfo=timezone.utc),
    )


def submit(value=None):
    return (value or requisition()).submit(
        actor_principal_id="principal-requester",
        submitted_at=datetime(2026, 11, 7, tzinfo=timezone.utc),
        expected_revision=1,
    )


def test_requisition_must_be_submitted_before_approval():
    with pytest.raises(RequisitionError, match="ONLY_SUBMITTED"):
        requisition().decide(approval(), expected_revision=1)


def test_maker_cannot_approve_own_headcount_request():
    with pytest.raises(RequisitionError, match="MAKER_CHECKER"):
        submit().decide(approval(actor="principal-requester"), expected_revision=2)


def test_independent_approval_advances_revision_and_preserves_scope():
    approved = submit().decide(approval(), expected_revision=2)
    assert approved.status is RequisitionStatus.APPROVED
    assert approved.revision == 3
    assert approved.tenant_id == "WILSYTENANT-4CD2FZ4O"
    assert approved.requested_by_principal_id == "principal-requester"
    assert approved.approval.actor_principal_id == "principal-approver"


def test_rejection_is_a_distinct_terminal_decision():
    rejected = submit().decide(
        approval(decision=RequisitionDecision.REJECT),
        expected_revision=2,
    )
    assert rejected.status is RequisitionStatus.REJECTED
    with pytest.raises(RequisitionError, match="ONLY_SUBMITTED"):
        rejected.decide(approval(), expected_revision=3)


def test_stale_revision_cannot_overwrite_requisition():
    with pytest.raises(RequisitionError, match="REVISION_CONFLICT"):
        submit().decide(approval(), expected_revision=1)


def test_submitter_must_be_the_requisition_requester():
    with pytest.raises(RequisitionError, match="SUBMISSION_ACTOR_MISMATCH"):
        requisition().submit(
            actor_principal_id="different-principal",
            submitted_at=datetime(2026, 11, 7, tzinfo=timezone.utc),
            expected_revision=1,
        )


def test_approver_must_differ_from_requester_and_submitter():
    submitted = submit()
    with pytest.raises(RequisitionError, match="MAKER_CHECKER"):
        submitted.decide(approval(actor="principal-requester"), expected_revision=2)


@pytest.mark.parametrize("headcount", [0, -1, 51, True, 1.5])
def test_headcount_is_bounded_and_rejects_boolean(headcount):
    with pytest.raises(RequisitionError, match="HEADCOUNT"):
        requisition(headcount=headcount)


def test_decision_evidence_is_required_for_approved_record():
    with pytest.raises(RequisitionError, match="DECISION_EVIDENCE"):
        requisition(
            status=RequisitionStatus.APPROVED,
            submitted_by_principal_id="principal-requester",
            submitted_at=datetime(2026, 11, 7, tzinfo=timezone.utc),
        )


def test_requisition_round_trips_through_strict_persistence_shape():
    value = submit().decide(approval(), expected_revision=2)
    restored = HeadcountRequisition.from_dict(value.to_dict())
    assert restored.to_dict() == value.to_dict()


def test_fingerprint_detects_tampering():
    value = requisition()
    with pytest.raises(RequisitionError, match="FINGERPRINT_MISMATCH"):
        requisition(business_justification="Tampered", fingerprint=value.fingerprint)
