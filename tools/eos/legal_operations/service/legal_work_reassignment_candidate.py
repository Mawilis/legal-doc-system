"""TITLE: WILSY OS P9 Pure Legal Work Reassignment Candidate Validator.
VERSION: v1.0.0-P9-R59-REASSIGNMENT-CANDIDATE-GREEN
AUTHORITY: Python EOS Legal Operations / structural validation only.
EPITOME:
    Validate one proposed successor against exact immutable Legal work-item
    and predecessor assignment facts without changing or granting authority.
ABSOLUTE CANONICAL PATH:
    tools/eos/legal_operations/service/legal_work_reassignment_candidate.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R59-REASSIGNMENT-CANDIDATE-GREEN
    Introduces a pure, deterministic, fail-closed reassignment candidate
    validator. No repository access, IAM issuance, approval or execution.
TENANT BOUNDARY: Exact existing tenant, matter and work-item identities.
AUTHORITY BOUNDARY:
    Structural acceptance does not establish actor permission, recipient
    membership, professional qualification, confidential matter access,
    supervisory approval or assignment execution authority.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from typing import Final, NoReturn

from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)

VERSION: Final[str] = (
    "v1.0.0-P9-R59-REASSIGNMENT-CANDIDATE-GREEN"
)


class LegalWorkReassignmentCandidateError(ValueError):
    """A bounded structural reassignment preflight failed."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _fail(code: str) -> NoReturn:
    raise LegalWorkReassignmentCandidateError(code)


def validate_legal_work_reassignment_candidate(
    *,
    work_item: LegalWorkItem,
    current_assignment: LegalWorkAssignment,
    successor_assignment: LegalWorkAssignment,
) -> LegalWorkAssignment:
    """Return the unchanged candidate only when structural checks succeed.

    The caller must separately establish current actor IAM, matter access,
    recipient eligibility, any supervisory approval and durable authority
    evidence before invoking the existing assignment persistence registry.
    This function performs no IO and grants none of those authorities.
    """
    if type(work_item) is not LegalWorkItem:
        _fail("P9_R59_WORK_ITEM_INVALID")

    if type(current_assignment) is not LegalWorkAssignment:
        _fail("P9_R59_CURRENT_ASSIGNMENT_INVALID")

    if type(successor_assignment) is not LegalWorkAssignment:
        _fail("P9_R59_SUCCESSOR_ASSIGNMENT_INVALID")

    if work_item.status not in (
        LegalWorkItemStatus.OPEN,
        LegalWorkItemStatus.IN_PROGRESS,
        LegalWorkItemStatus.BLOCKED,
    ):
        _fail("P9_R59_TERMINAL_WORK_REASSIGNMENT_FORBIDDEN")

    scope = (
        work_item.tenant_id,
        work_item.case_matter_id,
        work_item.work_item_id,
    )

    if (
        current_assignment.tenant_id,
        current_assignment.case_matter_id,
        current_assignment.work_item_id,
    ) != scope:
        _fail("P9_R59_CURRENT_ASSIGNMENT_SCOPE_MISMATCH")

    if (
        successor_assignment.tenant_id,
        successor_assignment.case_matter_id,
        successor_assignment.work_item_id,
    ) != scope:
        _fail("P9_R59_SUCCESSOR_ASSIGNMENT_SCOPE_MISMATCH")

    if (
        successor_assignment.supersedes_assignment_id
        != current_assignment.assignment_id
    ):
        _fail("P9_R59_STALE_ASSIGNMENT_PREDECESSOR")

    if successor_assignment.assignment_id == current_assignment.assignment_id:
        _fail("P9_R59_SUCCESSOR_IDENTITY_NOT_DISTINCT")

    if (
        successor_assignment.assignee_principal_id
        == current_assignment.assignee_principal_id
    ):
        _fail("P9_R59_ASSIGNEE_UNCHANGED")

    if successor_assignment.assigned_at <= current_assignment.assigned_at:
        _fail("P9_R59_ASSIGNMENT_TIME_NOT_INCREASING")

    return successor_assignment


__all__ = [
    "VERSION",
    "LegalWorkReassignmentCandidateError",
    "validate_legal_work_reassignment_candidate",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_work_reassignment_candidate.py
# VERSION: v1.0.0-P9-R59-REASSIGNMENT-CANDIDATE-GREEN
# AUTHORITY BOUNDARY: pure structural validation only
# ACTOR / RECIPIENT / MATTER / SUPERVISOR AUTHORITY: NOT GRANTED
# DATABASE / HTTP / ASSIGNMENT MUTATION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
