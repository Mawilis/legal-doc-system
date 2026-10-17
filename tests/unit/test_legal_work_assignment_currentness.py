"""
WILSY OS — P14-R20R7 Legal Work Assignment Currentness Unit Certificate.

Certifies pure deterministic derivation of the assignee that owned one exact
work item at one explicit historical instant.

This module is evidence/currentness only:
assignment != IAM
assignment != completion authority
assignment != supervision
assignment != matter access
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_assignment_currentness import (
    LegalWorkAssignmentCurrentness,
    LegalWorkAssignmentCurrentnessError,
    resolve_legal_work_assignment_as_of,
)


NOW = datetime(
    2026,
    10,
    17,
    0,
    0,
    tzinfo=timezone.utc,
)

TENANT = "tenant-law"
MATTER = "matter-1"
WORK = "work-1"


def _assignment(
    assignment_id: str,
    principal_id: str,
    assigned_at: datetime,
    *,
    supersedes: str | None = None,
    tenant_id: str = TENANT,
    matter_id: str = MATTER,
    work_item_id: str = WORK,
) -> LegalWorkAssignment:
    return LegalWorkAssignment(
        assignment_id=assignment_id,
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        work_item_id=work_item_id,
        assignee_principal_id=principal_id,
        assigned_by_principal_id="principal-assigner",
        assigned_at=assigned_at,
        assignment_reason_reference="reason:staffing",
        authorization_evidence_reference="authz:assignment",
        supersedes_assignment_id=supersedes,
    )


def _history() -> tuple[LegalWorkAssignment, ...]:
    first = _assignment(
        "assignment-1",
        "principal-a",
        NOW - timedelta(days=3),
    )
    second = _assignment(
        "assignment-2",
        "principal-b",
        NOW - timedelta(days=2),
        supersedes=first.assignment_id,
    )
    third = _assignment(
        "assignment-3",
        "principal-c",
        NOW - timedelta(days=1),
        supersedes=second.assignment_id,
    )
    return (
        first,
        second,
        third,
    )


def test_empty_history_is_unassigned() -> None:
    result = resolve_legal_work_assignment_as_of(
        (),
        evaluated_at=NOW,
    )

    assert result is None


def test_before_first_assignment_is_unassigned() -> None:
    result = resolve_legal_work_assignment_as_of(
        _history(),
        evaluated_at=NOW - timedelta(days=4),
    )

    assert result is None


def test_exact_first_assignment_instant_selects_first() -> None:
    history = _history()

    result = resolve_legal_work_assignment_as_of(
        history,
        evaluated_at=history[0].assigned_at,
    )

    assert result is not None
    assert result.assignment_id == "assignment-1"
    assert result.assignee_principal_id == "principal-a"


def test_between_reassignments_selects_predecessor() -> None:
    history = _history()

    result = resolve_legal_work_assignment_as_of(
        history,
        evaluated_at=(
            history[1].assigned_at
            + timedelta(hours=1)
        ),
    )

    assert result is not None
    assert result.assignment_id == "assignment-2"
    assert result.assignee_principal_id == "principal-b"


def test_exact_reassignment_instant_selects_successor() -> None:
    history = _history()

    result = resolve_legal_work_assignment_as_of(
        history,
        evaluated_at=history[2].assigned_at,
    )

    assert result is not None
    assert result.assignment_id == "assignment-3"
    assert result.assignee_principal_id == "principal-c"


def test_after_latest_selects_latest() -> None:
    result = resolve_legal_work_assignment_as_of(
        _history(),
        evaluated_at=NOW,
    )

    assert result is not None
    assert result.assignment_id == "assignment-3"


def test_projection_records_exact_evaluation_instant() -> None:
    result = LegalWorkAssignmentCurrentness.resolve(
        _history(),
        evaluated_at=NOW,
    )

    assert result.evaluated_at == NOW
    assert result.assignment is not None
    assert result.assignment.assignment_id == "assignment-3"


def test_projection_is_immutable() -> None:
    result = LegalWorkAssignmentCurrentness.resolve(
        _history(),
        evaluated_at=NOW,
    )

    with pytest.raises(
        (FrozenInstanceError, AttributeError),
    ):
        result.evaluated_at = NOW + timedelta(seconds=1)  # type: ignore[misc]


def test_naive_evaluation_time_fails_closed() -> None:
    with pytest.raises(
        LegalWorkAssignmentCurrentnessError,
        match="P14_R20R7_EVALUATED_AT_INVALID",
    ):
        resolve_legal_work_assignment_as_of(
            _history(),
            evaluated_at=datetime(2026, 10, 17),
        )


def test_cross_tenant_lineage_fails_closed() -> None:
    history = list(_history())
    history[1] = _assignment(
        "assignment-2",
        "principal-b",
        NOW - timedelta(days=2),
        supersedes="assignment-1",
        tenant_id="tenant-other",
    )

    with pytest.raises(
        LegalWorkAssignmentCurrentnessError,
        match="P14_R20R7_LINEAGE_SCOPE_MISMATCH",
    ):
        resolve_legal_work_assignment_as_of(
            tuple(history),
            evaluated_at=NOW,
        )


def test_cross_matter_lineage_fails_closed() -> None:
    history = list(_history())
    history[1] = _assignment(
        "assignment-2",
        "principal-b",
        NOW - timedelta(days=2),
        supersedes="assignment-1",
        matter_id="matter-other",
    )

    with pytest.raises(
        LegalWorkAssignmentCurrentnessError,
        match="P14_R20R7_LINEAGE_SCOPE_MISMATCH",
    ):
        resolve_legal_work_assignment_as_of(
            tuple(history),
            evaluated_at=NOW,
        )


def test_cross_work_lineage_fails_closed() -> None:
    history = list(_history())
    history[1] = _assignment(
        "assignment-2",
        "principal-b",
        NOW - timedelta(days=2),
        supersedes="assignment-1",
        work_item_id="work-other",
    )

    with pytest.raises(
        LegalWorkAssignmentCurrentnessError,
        match="P14_R20R7_LINEAGE_SCOPE_MISMATCH",
    ):
        resolve_legal_work_assignment_as_of(
            tuple(history),
            evaluated_at=NOW,
        )


def test_duplicate_assignment_id_fails_closed() -> None:
    first = _assignment(
        "assignment-1",
        "principal-a",
        NOW - timedelta(days=2),
    )
    duplicate = _assignment(
        "assignment-1",
        "principal-b",
        NOW - timedelta(days=1),
    )

    with pytest.raises(
        LegalWorkAssignmentCurrentnessError,
        match="P14_R20R7_DUPLICATE_ASSIGNMENT_ID",
    ):
        resolve_legal_work_assignment_as_of(
            (
                first,
                duplicate,
            ),
            evaluated_at=NOW,
        )


def test_multiple_roots_fail_closed() -> None:
    with pytest.raises(
        LegalWorkAssignmentCurrentnessError,
        match="P14_R20R7_INITIAL_ASSIGNMENT_AMBIGUOUS",
    ):
        resolve_legal_work_assignment_as_of(
            (
                _assignment(
                    "assignment-a",
                    "principal-a",
                    NOW - timedelta(days=2),
                ),
                _assignment(
                    "assignment-b",
                    "principal-b",
                    NOW - timedelta(days=1),
                ),
            ),
            evaluated_at=NOW,
        )


def test_missing_predecessor_fails_closed() -> None:
    root = _assignment(
        "assignment-1",
        "principal-a",
        NOW - timedelta(days=2),
    )
    orphan_successor = _assignment(
        "assignment-2",
        "principal-b",
        NOW - timedelta(days=1),
        supersedes="assignment-missing",
    )

    with pytest.raises(
        LegalWorkAssignmentCurrentnessError,
        match="P14_R20R7_PREDECESSOR_NOT_FOUND",
    ):
        resolve_legal_work_assignment_as_of(
            (
                root,
                orphan_successor,
            ),
            evaluated_at=NOW,
        )


def test_branched_history_fails_closed() -> None:
    first = _assignment(
        "assignment-1",
        "principal-a",
        NOW - timedelta(days=3),
    )

    with pytest.raises(
        LegalWorkAssignmentCurrentnessError,
        match="P14_R20R7_BRANCHED_HISTORY",
    ):
        resolve_legal_work_assignment_as_of(
            (
                first,
                _assignment(
                    "assignment-2",
                    "principal-b",
                    NOW - timedelta(days=2),
                    supersedes=first.assignment_id,
                ),
                _assignment(
                    "assignment-3",
                    "principal-c",
                    NOW - timedelta(days=1),
                    supersedes=first.assignment_id,
                ),
            ),
            evaluated_at=NOW,
        )


def test_non_increasing_successor_time_fails_closed() -> None:
    first = _assignment(
        "assignment-1",
        "principal-a",
        NOW - timedelta(days=1),
    )
    second = _assignment(
        "assignment-2",
        "principal-b",
        first.assigned_at,
        supersedes=first.assignment_id,
    )

    with pytest.raises(
        LegalWorkAssignmentCurrentnessError,
        match="P14_R20R7_ASSIGNED_AT_NOT_INCREASING",
    ):
        resolve_legal_work_assignment_as_of(
            (
                first,
                second,
            ),
            evaluated_at=NOW,
        )


def test_disconnected_history_fails_closed() -> None:
    first = _assignment(
        "assignment-1",
        "principal-a",
        NOW - timedelta(days=3),
    )
    second = _assignment(
        "assignment-2",
        "principal-b",
        NOW - timedelta(days=2),
        supersedes=first.assignment_id,
    )
    disconnected_root = _assignment(
        "assignment-3",
        "principal-c",
        NOW - timedelta(days=1),
    )

    with pytest.raises(
        LegalWorkAssignmentCurrentnessError,
    ):
        resolve_legal_work_assignment_as_of(
            (
                first,
                second,
                disconnected_root,
            ),
            evaluated_at=NOW,
        )


def test_input_order_does_not_change_result() -> None:
    history = _history()

    result = resolve_legal_work_assignment_as_of(
        (
            history[2],
            history[0],
            history[1],
        ),
        evaluated_at=NOW - timedelta(hours=36),
    )

    assert result is not None
    assert result.assignment_id == "assignment-2"


def test_future_successor_is_excluded_not_treated_as_current() -> None:
    first = _assignment(
        "assignment-1",
        "principal-a",
        NOW - timedelta(hours=1),
    )
    future = _assignment(
        "assignment-2",
        "principal-b",
        NOW + timedelta(hours=1),
        supersedes=first.assignment_id,
    )

    result = resolve_legal_work_assignment_as_of(
        (
            first,
            future,
        ),
        evaluated_at=NOW,
    )

    assert result is not None
    assert result.assignment_id == first.assignment_id
    assert result.assignee_principal_id == "principal-a"


def test_no_authority_methods_exist() -> None:
    result = LegalWorkAssignmentCurrentness.resolve(
        _history(),
        evaluated_at=NOW,
    )

    for name in (
        "authorize",
        "complete",
        "assign",
        "reassign",
        "supervise",
        "grant_permission",
        "persist",
        "save",
        "insert",
        "update",
        "delete",
    ):
        assert not hasattr(
            result,
            name,
        )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_assignment_currentness.py
# VERSION: v1.0.0-P14-R20R7-LEGAL-WORK-ASSIGNMENT-CURRENTNESS-UNIT
# PURE HISTORICAL CURRENTNESS: YES
# PERSISTENCE AUTHORITY: NONE
# IAM AUTHORITY: NONE
# COMPLETION AUTHORITY: NONE
# ASSIGNMENT MUTATION AUTHORITY: NONE
# SUPERVISION AUTHORITY: NONE
# FINANCIAL AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
