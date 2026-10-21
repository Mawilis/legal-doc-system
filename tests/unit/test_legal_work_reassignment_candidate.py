"""TITLE: WILSY OS P9 Pure Legal Work Reassignment Candidate RED Certificate.
VERSION: v1.0.0-P9-R58-REASSIGNMENT-CANDIDATE-RED
AUTHORITY: Test-only structural admission contract; no execution authority.
EPITOME: Reject mismatched, terminal, stale, self-directed and ill-timed
    reassignment candidates without granting IAM, matter, recipient,
    professional, supervision, approval or persistence authority.
ABSOLUTE CANONICAL PATH:
    tests/unit/test_legal_work_reassignment_candidate.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R58-REASSIGNMENT-CANDIDATE-RED
    Freezes a pure candidate-only preflight before implementation.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from importlib import import_module
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)

BASE = datetime(2026, 10, 19, 8, tzinfo=timezone.utc)


def _work(**overrides: object) -> LegalWorkItem:
    values: dict[str, Any] = dict(
        work_item_id="work-1",
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        title="Review matter evidence",
        source_kind="MATTER_WORKFLOW",
        source_reference="source-1",
        source_evidence_fingerprint="a" * 128,
        status=LegalWorkItemStatus.OPEN,
        created_at=BASE - timedelta(days=1),
    )
    values.update(overrides)
    return LegalWorkItem(**values)


def _assignment(**overrides: object) -> LegalWorkAssignment:
    values: dict[str, Any] = dict(
        assignment_id="assignment-1",
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        work_item_id="work-1",
        assignee_principal_id="principal-original",
        assigned_by_principal_id="principal-partner",
        assigned_at=BASE,
        assignment_reason_reference="reason-1",
        authorization_evidence_reference="authorization-1",
        supersedes_assignment_id=None,
    )
    values.update(overrides)
    return LegalWorkAssignment(**values)


def _successor(**overrides: object) -> LegalWorkAssignment:
    values: dict[str, Any] = dict(
        assignment_id="assignment-2",
        assignee_principal_id="principal-recipient",
        assigned_at=BASE + timedelta(minutes=1),
        supersedes_assignment_id="assignment-1",
    )
    values.update(overrides)
    return _assignment(**values)


def _validate(
    work_item: LegalWorkItem,
    current_assignment: LegalWorkAssignment,
    successor_assignment: LegalWorkAssignment,
) -> LegalWorkAssignment:
    module = import_module(
        "tools.eos.legal_operations.service."
        "legal_work_reassignment_candidate"
    )
    return module.validate_legal_work_reassignment_candidate(
        work_item=work_item,
        current_assignment=current_assignment,
        successor_assignment=successor_assignment,
    )


@pytest.mark.parametrize(
    "status",
    (
        LegalWorkItemStatus.OPEN,
        LegalWorkItemStatus.IN_PROGRESS,
        LegalWorkItemStatus.BLOCKED,
    ),
)
def test_nonterminal_exact_candidate_is_only_structurally_accepted(
    status: LegalWorkItemStatus,
) -> None:
    successor = _successor()
    assert _validate(_work(status=status), _assignment(), successor) is successor


@pytest.mark.parametrize(
    "status",
    (LegalWorkItemStatus.COMPLETED, LegalWorkItemStatus.CANCELLED),
)
def test_terminal_work_is_never_a_reassignment_candidate(
    status: LegalWorkItemStatus,
) -> None:
    if status is LegalWorkItemStatus.COMPLETED:
        work = _work(
            status=status,
            completion_evidence_reference="completion-1",
            completion_evidence_fingerprint="b" * 128,
            completed_at=BASE,
        )
    else:
        work = _work(
            status=status,
            cancellation_reason_reference="cancellation-1",
            cancelled_at=BASE,
        )
    with pytest.raises(ValueError):
        _validate(work, _assignment(), _successor())


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("tenant_id", "tenant-foreign"),
        ("case_matter_id", "matter-foreign"),
        ("work_item_id", "work-foreign"),
    ),
)
def test_successor_cannot_change_exact_scope(
    field: str, value: str,
) -> None:
    with pytest.raises(ValueError):
        _validate(
            _work(),
            _assignment(),
            _successor(**{field: value}),
        )


def test_predecessor_must_match_exact_current_identity() -> None:
    with pytest.raises(ValueError):
        _validate(
            _work(),
            _assignment(),
            _successor(supersedes_assignment_id="assignment-stale"),
        )


def test_recipient_cannot_be_existing_assignee() -> None:
    with pytest.raises(ValueError):
        _validate(
            _work(),
            _assignment(),
            _successor(assignee_principal_id="principal-original"),
        )


@pytest.mark.parametrize(
    "when",
    (BASE, BASE - timedelta(seconds=1)),
)
def test_successor_effective_time_must_advance(when: datetime) -> None:
    with pytest.raises(ValueError):
        _validate(
            _work(),
            _assignment(),
            _successor(assigned_at=when),
        )


def test_current_assignment_must_match_work_item_scope() -> None:
    with pytest.raises(ValueError):
        _validate(
            _work(),
            _assignment(case_matter_id="matter-foreign"),
            _successor(),
        )


def test_candidate_validation_does_not_issue_or_persist_authority() -> None:
    module = import_module(
        "tools.eos.legal_operations.service."
        "legal_work_reassignment_candidate"
    )
    assert not hasattr(module, "execute_reassignment")
    assert not hasattr(module, "issue_authorization")
    assert not hasattr(module, "persist_reassignment")
    assert not hasattr(module, "approve_reassignment")


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_work_reassignment_candidate.py
# VERSION: v1.0.0-P9-R58-REASSIGNMENT-CANDIDATE-RED
# AUTHORITY BOUNDARY: pure structural candidate validation only
# RECIPIENT / MATTER / SUPERVISOR AUTHORITY: NOT GRANTED
# REASSIGNMENT EXECUTION / PERSISTENCE: NOT CREATED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
