"""
WILSY OS — P14-R20R23 single-evaluation Legal work-completion
authority provenance composer.

PURPOSE
-------
Compose first-class R20R22 completion-authority evidence from:

    exact historical Legal work assignment
    + one canonical tenant IAM authorization-evidence issuance
    + exact Legal work identity
    + acting principal
    + explicit evaluation instant

The caller owns the active transaction.

This composer does not call authorize_tenant_operation directly.
Canonical IAM evidence issuance owns that one IAM evaluation.

The composer performs no completion-event construction, no completion-event
persistence, no workflow transition, no dependency release, no notification,
no AI execution and no financial execution.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha3_512
import json
from typing import Any, Final, NoReturn, Protocol, cast

from tools.eos.auth.tenant_authorization_decision_evidence import (
    TenantAuthorizationDecisionEvidence,
)
from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_assignment_currentness import (
    LegalWorkAssignmentCurrentnessError,
    resolve_legal_work_assignment_as_of,
)
from tools.eos.legal_operations.domain.legal_work_completion_authority_evidence import (
    LegalWorkCompletionAuthorityEvidence,
    LegalWorkCompletionAuthorityEvidenceError,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)


VERSION: Final[str] = (
    "v1.0.0-P14-R20R23-"
    "SINGLE-EVALUATION-WORK-COMPLETION-AUTHORITY-COMPOSER"
)

COMPLETION_OPERATION: Final[str] = (
    "legal_work_item_complete"
)

COMPLETION_PERMISSION: Final[str] = (
    "legal_operations:work_item:complete"
)

AUTHORIZATION_SUBJECT_PREFIX: Final[str] = (
    "legal-work-completion"
)

_COMPLETION_AUTHORITY_ID_PREFIX: Final[str] = (
    "legal-work-completion-authority:"
)


class LegalWorkCompletionAuthorityCompositionError(
    RuntimeError
):
    """Fail-closed completion-authority composition error."""


class AuthorizationEvidenceIssuer(
    Protocol
):
    def issue(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        operation: str,
        permission: str,
        subject_reference: str,
        subject_evidence_fingerprint: str,
        idempotency_key: str,
        session: Any,
    ) -> TenantAuthorizationDecisionEvidence:
        """Issue or exactly replay canonical tenant IAM evidence."""
        ...


def _fail(
    code: str,
    error: BaseException | None = None,
) -> NoReturn:
    if error is None:
        raise LegalWorkCompletionAuthorityCompositionError(
            code
        )

    raise LegalWorkCompletionAuthorityCompositionError(
        code
    ) from error


def _active_transaction(
    session: object,
) -> object:
    if session is None:
        _fail(
            "P14_R20R23_ACTIVE_TRANSACTION_REQUIRED"
        )

    try:
        marker = getattr(
            session,
            "in_transaction",
        )
    except Exception as error:
        _fail(
            "P14_R20R23_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )

    try:
        active = (
            marker()
            if callable(marker)
            else marker
        )
    except Exception as error:
        _fail(
            "P14_R20R23_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )

    if active is not True:
        _fail(
            "P14_R20R23_ACTIVE_TRANSACTION_REQUIRED"
        )

    return session


def _moment(
    value: object,
) -> datetime:
    if not isinstance(
        value,
        datetime,
    ):
        _fail(
            "P14_R20R23_EVALUATED_AT_INVALID"
        )

    moment = cast(
        datetime,
        value,
    )

    if (
        moment.tzinfo is None
        or moment.utcoffset() is None
    ):
        _fail(
            "P14_R20R23_EVALUATED_AT_INVALID"
        )

    return moment.astimezone(
        timezone.utc
    )


def _canonical_digest(
    value: dict[str, object],
) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode(
        "utf-8"
    )

    return sha3_512(
        raw
    ).hexdigest()


def _subject_reference(
    *,
    tenant_id: str,
    case_matter_id: str,
    work_item_id: str,
) -> str:
    return (
        AUTHORIZATION_SUBJECT_PREFIX
        + ":"
        + tenant_id
        + ":"
        + case_matter_id
        + ":"
        + work_item_id
    )


def _authorization_idempotency_key(
    *,
    tenant_id: str,
    work_item_id: str,
) -> str:
    digest = _canonical_digest(
        {
            "tenant_id":
                tenant_id,
            "work_item_id":
                work_item_id,
        }
    )

    return (
        AUTHORIZATION_SUBJECT_PREFIX
        + ":iam:"
        + digest
    )


def _subject_fingerprint(
    *,
    tenant_id: str,
    case_matter_id: str,
    work_item_id: str,
    work_item_fingerprint: str,
    principal_id: str,
    assignment_id: str,
    assignment_fingerprint: str,
    evaluated_at: datetime,
) -> str:
    return _canonical_digest(
        {
            "tenant_id":
                tenant_id,
            "case_matter_id":
                case_matter_id,
            "work_item_id":
                work_item_id,
            "work_item_fingerprint":
                work_item_fingerprint,
            "principal_id":
                principal_id,
            "assignment_id":
                assignment_id,
            "assignment_fingerprint":
                assignment_fingerprint,
            "evaluated_at":
                evaluated_at.isoformat(),
        }
    )


def _completion_authority_evidence_id(
    *,
    tenant_id: str,
    case_matter_id: str,
    work_item_id: str,
    work_item_fingerprint: str,
    principal_id: str,
    assignment_id: str,
    assignment_fingerprint: str,
    iam_reference: str,
    iam_fingerprint: str,
    evaluated_at: datetime,
) -> str:
    digest = _canonical_digest(
        {
            "tenant_id":
                tenant_id,
            "case_matter_id":
                case_matter_id,
            "work_item_id":
                work_item_id,
            "work_item_fingerprint":
                work_item_fingerprint,
            "principal_id":
                principal_id,
            "assignment_id":
                assignment_id,
            "assignment_fingerprint":
                assignment_fingerprint,
            "iam_authorization_evidence_reference":
                iam_reference,
            "iam_authorization_evidence_fingerprint":
                iam_fingerprint,
            "evaluated_at":
                evaluated_at.isoformat(),
        }
    )

    return (
        _COMPLETION_AUTHORITY_ID_PREFIX
        + digest
    )


def _required_string(
    value: object,
    code: str,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        _fail(
            code
        )

    return cast(
        str,
        value,
    )


def _required_fingerprint(
    value: object,
    code: str,
) -> str:
    text = _required_string(
        value,
        code,
    )

    if (
        len(text) != 128
        or text.lower() != text
    ):
        _fail(
            code
        )

    try:
        int(
            text,
            16,
        )
    except ValueError as error:
        _fail(
            code,
            error,
        )

    return text


def _require_work_scope(
    *,
    tenant_id: str,
    work_item: LegalWorkItem,
) -> None:
    if (
        work_item.tenant_id
        != tenant_id
    ):
        _fail(
            "P14_R20R23_WORK_TENANT_MISMATCH"
        )

    if work_item.status in {
        LegalWorkItemStatus.COMPLETED,
        LegalWorkItemStatus.CANCELLED,
    }:
        _fail(
            "P14_R20R23_WORK_TERMINAL"
        )


def _resolve_assignment(
    *,
    assignments: tuple[
        LegalWorkAssignment,
        ...,
    ],
    work_item: LegalWorkItem,
    principal_id: str,
    evaluated_at: datetime,
) -> LegalWorkAssignment:
    if not isinstance(
        assignments,
        tuple,
    ):
        _fail(
            "P14_R20R23_ASSIGNMENT_HISTORY_REQUIRED"
        )

    try:
        assignment = (
            resolve_legal_work_assignment_as_of(
                assignments,
                evaluated_at=evaluated_at,
            )
        )
    except (
        LegalWorkAssignmentCurrentnessError,
        TypeError,
        ValueError,
    ) as error:
        _fail(
            "P14_R20R23_ASSIGNMENT_INVALID",
            error,
        )

    if assignment is None:
        _fail(
            "P14_R20R23_ASSIGNMENT_REQUIRED"
        )

    if (
        assignment.tenant_id
        != work_item.tenant_id
    ):
        _fail(
            "P14_R20R23_ASSIGNMENT_TENANT_MISMATCH"
        )

    if (
        assignment.case_matter_id
        != work_item.case_matter_id
    ):
        _fail(
            "P14_R20R23_ASSIGNMENT_MATTER_MISMATCH"
        )

    if (
        assignment.work_item_id
        != work_item.work_item_id
    ):
        _fail(
            "P14_R20R23_ASSIGNMENT_WORK_ITEM_MISMATCH"
        )

    if (
        assignment.assignee_principal_id
        != principal_id
    ):
        _fail(
            "P14_R20R23_ASSIGNEE_MISMATCH"
        )

    return assignment


def compose_legal_work_completion_authority_evidence(
    *,
    tenant_id: str,
    principal_id: str,
    work_item: LegalWorkItem,
    assignments: tuple[
        LegalWorkAssignment,
        ...,
    ],
    evaluated_at: datetime,
    authorization_evidence_issuer: AuthorizationEvidenceIssuer,
    session: object,
) -> LegalWorkCompletionAuthorityEvidence:
    """
    Compose one first-class completion-authority evidence value.

    IAM is evaluated exactly once by the canonical evidence issuer.
    The caller owns transaction lifecycle.
    """

    tx = _active_transaction(
        session
    )

    tenant = _required_string(
        tenant_id,
        "P14_R20R23_TENANT_REQUIRED",
    )

    principal = _required_string(
        principal_id,
        "P14_R20R23_PRINCIPAL_REQUIRED",
    )

    if type(
        work_item
    ) is not LegalWorkItem:
        _fail(
            "P14_R20R23_WORK_ITEM_REQUIRED"
        )

    moment = _moment(
        evaluated_at
    )

    _require_work_scope(
        tenant_id=tenant,
        work_item=work_item,
    )

    assignment = _resolve_assignment(
        assignments=assignments,
        work_item=work_item,
        principal_id=principal,
        evaluated_at=moment,
    )

    subject_reference = _subject_reference(
        tenant_id=tenant,
        case_matter_id=work_item.case_matter_id,
        work_item_id=work_item.work_item_id,
    )

    subject_fingerprint = _subject_fingerprint(
        tenant_id=tenant,
        case_matter_id=work_item.case_matter_id,
        work_item_id=work_item.work_item_id,
        work_item_fingerprint=work_item.fingerprint,
        principal_id=principal,
        assignment_id=assignment.assignment_id,
        assignment_fingerprint=assignment.fingerprint,
        evaluated_at=moment,
    )

    idempotency_key = (
        _authorization_idempotency_key(
            tenant_id=tenant,
            work_item_id=work_item.work_item_id,
        )
    )

    try:
        authorization = (
            authorization_evidence_issuer.issue(
                tenant_id=tenant,
                principal_id=principal,
                operation=COMPLETION_OPERATION,
                permission=COMPLETION_PERMISSION,
                subject_reference=subject_reference,
                subject_evidence_fingerprint=subject_fingerprint,
                idempotency_key=idempotency_key,
                session=tx,
            )
        )
    except Exception as error:
        _fail(
            "P14_R20R23_IAM_EVIDENCE_ISSUANCE_FAILED",
            error,
        )

    if type(authorization) is not TenantAuthorizationDecisionEvidence:
        _fail(
            "P14_R20R23_IAM_EVIDENCE_TYPE_INVALID"
        )

    canonical_authorization = cast(
        TenantAuthorizationDecisionEvidence,
        authorization,
    )

    authorization_tenant = canonical_authorization.tenant_id

    authorization_principal = canonical_authorization.principal_id

    authorization_operation = canonical_authorization.operation

    authorization_permission = canonical_authorization.permission

    authorization_subject = canonical_authorization.subject_reference

    authorization_subject_fingerprint = (
        canonical_authorization.subject_evidence_fingerprint
    )

    authorization_reference = (
        canonical_authorization.authorization_evidence_reference
    )

    authorization_fingerprint = (
        canonical_authorization.authorization_evidence_fingerprint
    )

    if authorization_tenant != tenant:
        _fail(
            "P14_R20R23_IAM_TENANT_CORRELATION_INVALID"
        )

    if authorization_principal != principal:
        _fail(
            "P14_R20R23_IAM_PRINCIPAL_CORRELATION_INVALID"
        )

    if (
        authorization_operation
        != COMPLETION_OPERATION
    ):
        _fail(
            "P14_R20R23_IAM_OPERATION_CORRELATION_INVALID"
        )

    if (
        authorization_permission
        != COMPLETION_PERMISSION
    ):
        _fail(
            "P14_R20R23_IAM_PERMISSION_CORRELATION_INVALID"
        )

    if (
        authorization_subject
        != subject_reference
    ):
        _fail(
            "P14_R20R23_IAM_SUBJECT_CORRELATION_INVALID"
        )

    if (
        authorization_subject_fingerprint
        != subject_fingerprint
    ):
        _fail(
            "P14_R20R23_IAM_SUBJECT_FINGERPRINT_CORRELATION_INVALID"
        )

    iam_reference = _required_string(
        authorization_reference,
        "P14_R20R23_IAM_REFERENCE_INVALID",
    )

    iam_fingerprint = _required_fingerprint(
        authorization_fingerprint,
        "P14_R20R23_IAM_FINGERPRINT_INVALID",
    )

    evidence_id = (
        _completion_authority_evidence_id(
            tenant_id=tenant,
            case_matter_id=work_item.case_matter_id,
            work_item_id=work_item.work_item_id,
            work_item_fingerprint=work_item.fingerprint,
            principal_id=principal,
            assignment_id=assignment.assignment_id,
            assignment_fingerprint=assignment.fingerprint,
            iam_reference=iam_reference,
            iam_fingerprint=iam_fingerprint,
            evaluated_at=moment,
        )
    )

    try:
        return LegalWorkCompletionAuthorityEvidence(
            completion_authority_evidence_id=evidence_id,
            tenant_id=tenant,
            case_matter_id=work_item.case_matter_id,
            work_item_id=work_item.work_item_id,
            work_item_fingerprint=work_item.fingerprint,
            principal_id=principal,
            assignment_id=assignment.assignment_id,
            assignment_fingerprint=assignment.fingerprint,
            iam_authorization_evidence_reference=iam_reference,
            iam_authorization_evidence_fingerprint=iam_fingerprint,
            evaluated_at=moment,
        )
    except LegalWorkCompletionAuthorityEvidenceError as error:
        _fail(
            "P14_R20R23_COMPLETION_AUTHORITY_EVIDENCE_INVALID",
            error,
        )


__all__ = [
    "VERSION",
    "COMPLETION_OPERATION",
    "COMPLETION_PERMISSION",
    "AUTHORIZATION_SUBJECT_PREFIX",
    "AuthorizationEvidenceIssuer",
    "LegalWorkCompletionAuthorityCompositionError",
    "compose_legal_work_completion_authority_evidence",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT:
#   legal_work_completion_authority_composer.py
# VERSION:
#   v1.0.0-P14-R20R23-SINGLE-EVALUATION-WORK-COMPLETION-AUTHORITY-COMPOSER
# IAM:
#   exactly one canonical authorization-evidence issuance; no direct IAM call
# TRANSACTION:
#   caller-owned active transaction required and propagated exactly
# ASSIGNMENT:
#   exact historical assignment resolved at explicit evaluated_at
# IDEMPOTENCY:
#   server-derived tenant/work target identity; no caller authority
# OUTPUT:
#   R20R22 first-class immutable completion-authority evidence
# COMPLETION EVENT:
#   NONE
# COMPLETION PERSISTENCE:
#   NONE
# WORKFLOW:
#   NONE
# DEPENDENCY:
#   NONE
# NOTIFICATION:
#   NONE
# AI:
#   NONE
# FINANCIAL:
#   NONE
# =============================================================================
