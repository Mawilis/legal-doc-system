"""
TITLE:
    WILSY OS Legal Work Completion Authority Service

VERSION:
    v1.0.0-P14-R20R16-WORK-COMPLETION-AUTHORITY

PURPOSE:
    Decide whether one exact acting principal may request completion of one
    exact immutable LegalWorkItem.

AUTHORITY COMPOSITION:
    caller-owned active transaction
    ∩ exact current tenant IAM authorization
    ∩ explicit timezone-aware evaluated_at
    ∩ exact historical work assignment
    ∩ exact tenant / matter / work-item lineage
    ∩ exact acting-principal assignee

TEMPORAL BOUNDARY:
    TenantAuthorizationDecision has no authoritative timestamp. evaluated_at
    is an explicit server-side evaluation instant and is never represented as
    IAM authorized_at.

NON-AUTHORITY:
    This service does not complete or mutate LegalWorkItem, persist completion
    evidence, satisfy dependencies, advance workflow, infer supervision,
    execute AI, create invoices, bill, pay, settle, or grant financial
    authority.

TRANSACTION BOUNDARY:
    The caller supplies and owns one already-active transaction. IAM is
    evaluated inside that same transaction.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, NoReturn

from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_assignment_currentness import (
    LegalWorkAssignmentCurrentnessError,
    resolve_legal_work_assignment_as_of,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)


VERSION = (
    "v1.0.0-P14-R20R16-WORK-COMPLETION-AUTHORITY"
)

COMPLETION_PERMISSION = (
    "legal_operations:work_item:complete"
)

COMPLETION_OPERATION = (
    "legal_work_item_complete"
)


class LegalWorkCompletionAuthorityDeniedError(
    ValueError
):
    """Stable fail-closed completion-admission denial."""

    def __init__(
        self,
        code: str,
    ) -> None:
        self.code = code
        super().__init__(code)


def _fail(
    code: str,
    error: BaseException | None = None,
) -> NoReturn:
    if error is None:
        raise LegalWorkCompletionAuthorityDeniedError(
            code
        )

    raise LegalWorkCompletionAuthorityDeniedError(
        code
    ) from error


def _active_transaction(
    session: Any,
) -> Any:
    """Require one caller-owned transaction before any authority read."""

    marker = (
        getattr(
            session,
            "in_transaction",
            None,
        )
        if session is not None
        else None
    )

    try:
        active = (
            marker()
            if callable(marker)
            else marker
        )
    except (
        AttributeError,
        TypeError,
    ) as error:
        _fail(
            "P14_R20R15_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )

    if active is not True:
        _fail(
            "P14_R20R15_ACTIVE_TRANSACTION_REQUIRED"
        )

    return session


def _moment(
    value: datetime,
) -> datetime:
    """
    Require explicit timezone-aware evaluation time and normalize to UTC.

    This is command-evaluation time, not an IAM authorized_at.
    """

    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            "P14_R20R15_EVALUATED_AT_REQUIRED"
        )

    try:
        return value.astimezone(
            timezone.utc
        )
    except (
        OverflowError,
        ValueError,
    ) as error:
        _fail(
            "P14_R20R15_EVALUATED_AT_REQUIRED",
            error,
        )


def _require_work_scope(
    *,
    tenant_id: str,
    work_item: LegalWorkItem,
) -> None:
    if (
        not isinstance(
            tenant_id,
            str,
        )
        or not tenant_id
        or tenant_id != work_item.tenant_id
    ):
        _fail(
            "P14_R20R15_WORK_SCOPE_MISMATCH"
        )


def _require_completable_work(
    work_item: LegalWorkItem,
) -> None:
    """
    Admission never re-opens terminal work.

    Completion-event persistence and replay remain separate authorities.
    """

    if work_item.status in (
        LegalWorkItemStatus.COMPLETED,
        LegalWorkItemStatus.CANCELLED,
    ):
        _fail(
            "P14_R20R15_WORK_TERMINAL"
        )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalWorkCompletionAuthorityEvidence:
    """
    Immutable evidence that completion admission passed at one explicit instant.

    This evidence is not itself a completion event and does not mutate work.
    """

    tenant_id: str
    case_matter_id: str
    work_item_id: str
    principal_id: str

    work_item_fingerprint: str
    assignment_id: str
    assignment_fingerprint: str

    evaluated_at: datetime

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "tenant_id":
                self.tenant_id,
            "case_matter_id":
                self.case_matter_id,
            "work_item_id":
                self.work_item_id,
            "principal_id":
                self.principal_id,
            "work_item_fingerprint":
                self.work_item_fingerprint,
            "assignment_id":
                self.assignment_id,
            "assignment_fingerprint":
                self.assignment_fingerprint,
            "evaluated_at":
                self.evaluated_at.isoformat(),
        }


def authorize_legal_work_completion(
    *,
    tenant_id: str,
    principal_id: str,
    work_item: LegalWorkItem,
    assignments: tuple[
        LegalWorkAssignment,
        ...,
    ],
    evaluated_at: datetime,
    principal_repository: Any,
    membership_repository: Any,
    role_assignment_repository: Any,
    business_role_repository: Any,
    session: Any,
) -> LegalWorkCompletionAuthorityEvidence:
    """
    Admit completion only for the exact historical assignee with current IAM.

    This function owns no persistence and no transaction lifecycle.
    """

    # Transaction existence dominates all authority reads.
    tx = _active_transaction(
        session
    )

    # Explicit server-owned evaluation instant.
    moment = _moment(
        evaluated_at
    )

    if not isinstance(
        work_item,
        LegalWorkItem,
    ):
        _fail(
            "P14_R20R15_WORK_ITEM_REQUIRED"
        )

    if (
        not isinstance(
            principal_id,
            str,
        )
        or not principal_id
    ):
        _fail(
            "P14_R20R15_PRINCIPAL_REQUIRED"
        )

    _require_work_scope(
        tenant_id=tenant_id,
        work_item=work_item,
    )

    _require_completable_work(
        work_item
    )

    # IAM must be evaluated now, for the exact principal and exact tenant,
    # inside the same caller-owned active transaction.
    decision = authorize_tenant_operation(
        principal_id=principal_id,
        tenant_id=tenant_id,
        permission_id=COMPLETION_PERMISSION,
        operation=COMPLETION_OPERATION,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        role_assignment_repository=role_assignment_repository,
        business_role_repository=business_role_repository,
        session=tx,
    )

    if not (
        decision.authorized is True
        and decision.reason
        is TenantAuthorizationReason.AUTHORIZED
    ):
        _fail(
            "P14_R20R15_IAM_DENIED"
        )

    if not isinstance(
        assignments,
        tuple,
    ):
        _fail(
            "P14_R20R15_ASSIGNMENT_HISTORY_REQUIRED"
        )

    # Historical resolver validates immutable lineage and time.
    try:
        assignment = (
            resolve_legal_work_assignment_as_of(
                assignments,
                evaluated_at=moment,
            )
        )
    except (
        LegalWorkAssignmentCurrentnessError,
        TypeError,
        ValueError,
    ) as error:
        _fail(
            "P14_R20R15_ASSIGNMENT_INVALID",
            error,
        )

    if assignment is None:
        _fail(
            "P14_R20R15_ASSIGNMENT_REQUIRED"
        )

    # Resolver proves internal lineage consistency. The service must still
    # bind that lineage to the exact target work item.
    if assignment.tenant_id != work_item.tenant_id:
        _fail(
            "P14_R20R15_ASSIGNMENT_TENANT_MISMATCH"
        )

    if (
        assignment.case_matter_id
        != work_item.case_matter_id
    ):
        _fail(
            "P14_R20R15_ASSIGNMENT_MATTER_MISMATCH"
        )

    if (
        assignment.work_item_id
        != work_item.work_item_id
    ):
        _fail(
            "P14_R20R15_ASSIGNMENT_WORK_ITEM_MISMATCH"
        )

    if (
        assignment.assignee_principal_id
        != principal_id
    ):
        _fail(
            "P14_R20R15_ASSIGNEE_MISMATCH"
        )

    return LegalWorkCompletionAuthorityEvidence(
        tenant_id=work_item.tenant_id,
        case_matter_id=work_item.case_matter_id,
        work_item_id=work_item.work_item_id,
        principal_id=principal_id,
        work_item_fingerprint=work_item.fingerprint,
        assignment_id=assignment.assignment_id,
        assignment_fingerprint=assignment.fingerprint,
        evaluated_at=moment,
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_work_completion_authority.py
# VERSION: v1.0.0-P14-R20R16-WORK-COMPLETION-AUTHORITY
# COMPLETION PERMISSION: legal_operations:work_item:complete
# COMPLETION OPERATION: legal_work_item_complete
# IAM: exact current authorization inside caller-owned active transaction
# TEMPORAL INPUT: explicit timezone-aware evaluated_at; not IAM authorized_at
# ASSIGNMENT: exact immutable historical assignment
# ASSIGNEE: exact acting principal
# TENANT / MATTER / WORK ITEM: exact immutable lineage
# PERSISTENCE AUTHORITY: NONE
# WORK ITEM MUTATION AUTHORITY: NONE
# OPERATING ROLE AUTHORITY: NONE
# OPERATING CAPABILITY AUTHORITY: NONE
# SUPERVISION AUTHORITY: NONE
# COMPLETION EVENT AUTHORITY: NONE
# DEPENDENCY SATISFACTION AUTHORITY: NONE
# WORKFLOW RELEASE AUTHORITY: NONE
# LEGAL EVENT AUTHORITY: NONE
# AI EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
