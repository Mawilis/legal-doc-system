"""TITLE: WILSY OS Operational Matter Access Issuer Admission.
VERSION: v1.0.0-P47-R95-G23-ISSUER-ADMISSION
AUTHORITY: Transaction-bound prerequisite checking; not grant issuance.
EPITOME: Demand independently authorized Partner identity, canonical
    open matter, and eligible active recipient. Until independently
    certified practitioner-specific confidentiality and ethical-wall
    clearance exists, reject before persistence.
ABSOLUTE CANONICAL PATH:
    tools/eos/legal_operations/service/legal_work_operational_matter_access_issuance.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering / Legal Operations.
CERTIFICATION / UPDATE DATE: 2026-10-21
CHANGELOG:
    2026-10-21 v1.0.0-P47-R95-G23-ISSUER-ADMISSION
    Introduces admission preconditions and explicit clearance blocker.
SECURITY / PRIVACY POSTURE: Exact tenant, no caller-supplied clearance
    or role authority, no personal content or financial operations.
TENANT BOUNDARY: Current IAM, matter and practitioner in same tenant.
AUTHORITY BOUNDARY: Practitioner binding, IAM role and historical GRANTED
    evidence cannot themselves authorize confidential matter access.
TRANSACTION BOUNDARY: Caller owns active session; no commit, retry,
    transaction creation or transaction abort.
FAIL-CLOSED DECLARATION: Any unavailable or contradictory source denies.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Final, NoReturn

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_business_role_authority import (
    BusinessRoleResolution,
    resolve_current_tenant_business_role,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_work_operational_matter_access import (
    LegalWorkMatterAccessError,
    LegalWorkMatterAccessEvent,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_visibility_orchestrator import (
    _case_matter,
)

VERSION: Final[str] = "v1.0.0-P47-R95-G23-ISSUER-ADMISSION"
ISSUE_PERMISSION: Final[str] = "legal_operations:operational_matter_access:issue"
ISSUE_OPERATION: Final[str] = "legal_work_operational_matter_access_issue"
ELIGIBLE_TARGET_ROLES: Final[tuple[tuple[str, str], ...]] = (
    ("tenant_legal_partner", "LEGAL_PARTNER"),
    ("tenant_legal_attorney", "LEGAL_ATTORNEY"),
    ("tenant_legal_paralegal", "LEGAL_PARALEGAL"),
)


class LegalWorkOperationalMatterAccessIssuanceDenied(ValueError):
    """Stable non-authorizing issuer admission denial."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _deny(code: str) -> NoReturn:
    raise LegalWorkOperationalMatterAccessIssuanceDenied(code)


def _transaction(session: Any) -> Any:
    if session is None:
        _deny("P47_R95_ISSUER_ACTIVE_TRANSACTION_REQUIRED")
    try:
        marker = getattr(session, "in_transaction", None)
        active = marker() if callable(marker) else marker
    except Exception:
        _deny("P47_R95_ISSUER_ACTIVE_TRANSACTION_REQUIRED")
    if active is not True:
        _deny("P47_R95_ISSUER_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _issuer(
    *,
    principal_id: str,
    tenant_id: str,
    principal_repository: Any,
    membership_repository: Any,
    business_role_repository: Any,
    role_assignment_repository: Any,
    session: Any,
) -> None:
    try:
        decision = authorize_tenant_operation(
            principal_id=principal_id,
            tenant_id=tenant_id,
            permission_id=ISSUE_PERMISSION,
            operation=ISSUE_OPERATION,
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            business_role_repository=business_role_repository,
            role_assignment_repository=role_assignment_repository,
            session=session,
        )
    except Exception:
        _deny("P47_R95_ISSUER_IAM_UNAVAILABLE")

    if (
        type(decision) is not TenantAuthorizationDecision
        or decision.reason is not TenantAuthorizationReason.AUTHORIZED
        or decision.business_role != "tenant_legal_partner"
        or decision.authorization_role != "LEGAL_PARTNER"
    ):
        _deny("P47_R95_ISSUER_PARTNER_AUTHORITY_REQUIRED")


def _recipient(
    *,
    principal_id: str,
    tenant_id: str,
    principal_repository: Any,
    membership_repository: Any,
    business_role_repository: Any,
    role_assignment_repository: Any,
    session: Any,
) -> None:
    try:
        principal = principal_repository.resolve(principal_id, session=session)
        membership = membership_repository.resolve(
            principal_id, tenant_id, session=session,
        )
        role = resolve_current_tenant_business_role(
            principal_id=principal_id,
            tenant_id=tenant_id,
            repository=business_role_repository,
            session=session,
        )
    except Exception:
        _deny("P47_R95_RECIPIENT_IAM_UNAVAILABLE")

    if (
        getattr(principal, "principal_id", None) != principal_id
        or getattr(principal, "status", None) is not PrincipalStatus.ACTIVE
        or getattr(membership, "principal_id", None) != principal_id
        or getattr(membership, "tenant_id", None) != tenant_id
        or getattr(membership, "status", None)
            is not TenantMembershipStatus.ACTIVE
        or getattr(role, "resolution", None)
            is not BusinessRoleResolution.RESOLVED
    ):
        _deny("P47_R95_RECIPIENT_INACTIVE_OR_WRONG_SCOPE")

    found = [
        authorization_role
        for business_role, authorization_role in ELIGIBLE_TARGET_ROLES
        if getattr(role, "role", None) == business_role
    ]
    if len(found) != 1:
        _deny("P47_R95_RECIPIENT_ROLE_INELIGIBLE")

    try:
        assignment = role_assignment_repository.resolve(
            principal_id, tenant_id, found[0], session=session,
        )
    except Exception:
        _deny("P47_R95_RECIPIENT_ROLE_ASSIGNMENT_UNAVAILABLE")

    if (
        getattr(assignment, "principal_id", None) != principal_id
        or getattr(assignment, "tenant_id", None) != tenant_id
        or getattr(assignment, "status", None)
            is not RoleAssignmentStatus.ACTIVE
    ):
        _deny("P47_R95_RECIPIENT_ROLE_ASSIGNMENT_INVALID")


def issue_operational_matter_access(
    *,
    authenticated_principal_id: str,
    tenant_id: str,
    case_matter_id: str,
    practitioner_principal_id: str,
    event_id: str,
    occurred_at: datetime,
    issuer_authorization_evidence_reference: str,
    reason_reference: str,
    principal_repository: Any,
    membership_repository: Any,
    business_role_repository: Any,
    role_assignment_repository: Any,
    lifecycle_collection: Any,
    access_evidence_collection: Any,
    conflict_disposition_collection: Any,
    registry_collection: Any,
    session: Any,
) -> NoReturn:
    """Validate real upstream prerequisites without issuing a grant.

    Admission remains disabled until a certified current practitioner-specific
    confidentiality/ethical-wall clearance authority can be re-read.
    """
    tx = _transaction(session)

    try:
        candidate = LegalWorkMatterAccessEvent(
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            practitioner_principal_id=practitioner_principal_id,
            event_id=event_id,
            predecessor_event_id=None,
            decision="GRANTED",
            occurred_at=occurred_at,
            issuer_principal_id=authenticated_principal_id,
            issuer_authorization_evidence_reference=(
                issuer_authorization_evidence_reference
            ),
            reason_reference=reason_reference,
        )
    except (LegalWorkMatterAccessError, ValueError, TypeError):
        _deny("P47_R95_ISSUER_REQUEST_INVALID")

    _issuer(
        principal_id=candidate.issuer_principal_id,
        tenant_id=candidate.tenant_id,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=tx,
    )

    try:
        matter = _case_matter(
            tenant_id=candidate.tenant_id,
            case_matter_id=candidate.case_matter_id,
            lifecycle_collection=lifecycle_collection,
            session=tx,
        )
    except Exception:
        _deny("P47_R95_ISSUER_MATTER_UNAVAILABLE")

    if (
        getattr(matter, "tenant_id", None) != candidate.tenant_id
        or getattr(matter, "case_matter_id", None)
            != candidate.case_matter_id
        or getattr(getattr(matter, "state", None), "value", None)
            != "OPEN"
    ):
        _deny("P47_R95_ISSUER_MATTER_NOT_OPEN")

    _recipient(
        principal_id=candidate.practitioner_principal_id,
        tenant_id=candidate.tenant_id,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=tx,
    )

    # No fabricated verification: access evidence and conflict disposition
    # do not independently certify practitioner ethical-wall clearance.
    # The registry is intentionally never called by this candidate.
    _deny("P47_R95_ISSUER_CONFIDENTIALITY_CLEARANCE_UNAVAILABLE")


__all__ = [
    "VERSION",
    "ISSUE_PERMISSION",
    "ISSUE_OPERATION",
    "ELIGIBLE_TARGET_ROLES",
    "LegalWorkOperationalMatterAccessIssuanceDenied",
    "issue_operational_matter_access",
]

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_work_operational_matter_access_issuance.py
# VERSION: v1.0.0-P47-R95-G23-ISSUER-ADMISSION
# HISTORICAL EVIDENCE IS OPERATIONAL AUTHORITY: NO
# PRACTITIONER CONFIDENTIALITY CLEARANCE CERTIFIED: NO
# GRANT WRITES ENABLED: NO
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
