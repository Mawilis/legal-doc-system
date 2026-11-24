"""TITLE: WILSY OS Authorization-Role Delegation Policy.
VERSION: v1.3.0-PROJECTS-PLATFORM-OWNER-DELEGATION
AUTHORITY: Explicit GD1 authorization-role grant law.
PURPOSE: Evaluate whether canonical role evidence may grant a target role.
EPITOME: Pure, deterministic, fail-closed tenant-local delegation authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/authorization_role_delegation_policy.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
SECURITY / PRIVACY POSTURE: No persistence, secrets, network, or caller permission trust.
TENANT BOUNDARY: Inviter assignment and target tenant must match exactly; admission-officer, company-document-reader and Projects Platform Owner grants are confined to the canonical WILSY company tenant.
AUTHORITY BOUNDARY: RoleAssignmentAuthority evidence only; no lifecycle mutation.
FINANCIAL AUTHORITY BOUNDARY: No financial or Kennel execution authority.
TRANSACTION BOUNDARY: Pure evaluator; caller owns orchestration and sessions.
CERTIFICATION / UPDATE DATE: 2026-11-14
CHANGELOG:
    2026-11-16 v1.3.0-PROJECTS-PLATFORM-OWNER-DELEGATION permits the existing same-tenant ENTERPRISE_ADMIN delegation path to issue an invitation for the separately assignable Projects Platform Owner role only inside the canonical WILSY company tenant. Invitation acceptance remains required; no direct or automatic assignment occurs.
    2026-11-14 v1.2.0-COMPANY-DOCUMENT-READER-DELEGATION permits only ENTERPRISE_ADMIN to
    delegate COMPANY_DOCUMENT_READER in the canonical WILSY company tenant.
    This pure edge creates no assignment or automatic administrator permission.
    2026-11-12 v1.1.0-PLATFORM-EMPLOYEE-ADMISSION-DELEGATION allows only
    ENTERPRISE_ADMIN to delegate the dedicated employee-admission role, and only
    for the canonical WILSY company tenant. This policy evaluates an assignment
    request but creates no role assignment, membership, or principal.
    v1.0.0 implements explicit governance decision GD1.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from .role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from .roles import ROLE_PERMISSIONS_MAP
from .workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID

VERSION = "v1.3.0-PROJECTS-PLATFORM-OWNER-DELEGATION"
ROLE_GRANT_PERMISSION = "tenant:role_assignment:write"
CANONICAL_AUTHORIZATION_ROLES: Final = frozenset(ROLE_PERMISSIONS_MAP)
PLATFORM_EMPLOYEE_ADMISSION_ROLE: Final[str] = (
    "PLATFORM_EMPLOYEE_ADMISSION_OFFICER"
)
COMPANY_DOCUMENT_READER_ROLE: Final[str] = "COMPANY_DOCUMENT_READER"
PROJECTS_PLATFORM_OWNER_ROLE: Final[str] = "PROJECTS_PLATFORM_OWNER"
_ALLOW_EDGES: Final = frozenset({
    ("ENTERPRISE_ADMIN", "AUDITOR"),
    ("ENTERPRISE_ADMIN", "SERVICE_WORKER"),
    ("ENTERPRISE_ADMIN", PLATFORM_EMPLOYEE_ADMISSION_ROLE),
    ("ENTERPRISE_ADMIN", COMPANY_DOCUMENT_READER_ROLE),
    ("ENTERPRISE_ADMIN", PROJECTS_PLATFORM_OWNER_ROLE),
})
ALLOW_EDGES: Final = frozenset(_ALLOW_EDGES)


class AuthorizationRoleGrantDenialCode(StrEnum):
    MALFORMED_AUTHORITY = "MALFORMED_AUTHORITY"
    TENANT_MISMATCH = "TENANT_MISMATCH"
    INACTIVE_AUTHORITY = "INACTIVE_AUTHORITY"
    UNKNOWN_INVITER_ROLE = "UNKNOWN_INVITER_ROLE"
    UNKNOWN_TARGET_ROLE = "UNKNOWN_TARGET_ROLE"
    MISSING_GRANT_PERMISSION = "MISSING_GRANT_PERMISSION"
    GRANT_NOT_PERMITTED = "GRANT_NOT_PERMITTED"


@dataclass(frozen=True, slots=True)
class AuthorizationRoleGrantDecision:
    allowed: bool
    inviter_role: str
    target_role: str
    target_tenant_id: str
    denial_code: AuthorizationRoleGrantDenialCode | None = None


def _deny(inviter_role: str, target_role: str, tenant: str, code: AuthorizationRoleGrantDenialCode) -> AuthorizationRoleGrantDecision:
    return AuthorizationRoleGrantDecision(False, inviter_role, target_role, tenant, code)


def evaluate_authorization_role_grant(
    inviter_assignment: RoleAssignmentAuthority,
    target_tenant_id: str,
    target_role: str,
) -> AuthorizationRoleGrantDecision:
    """Evaluate a closed grant edge using current trusted assignment evidence.

    Caller must separately prove session, principal, membership, eligible
    granting capacity, target scope, approval and transaction currentness.
    This pure function cannot grant reader, author, publisher or financial power.
    """
    if not isinstance(inviter_assignment, RoleAssignmentAuthority) or not isinstance(target_tenant_id, str) or not target_tenant_id.strip() or not isinstance(target_role, str) or not target_role.strip():
        return _deny("", str(target_role), str(target_tenant_id), AuthorizationRoleGrantDenialCode.MALFORMED_AUTHORITY)
    inviter_role = inviter_assignment.role_id
    if inviter_assignment.tenant_id != target_tenant_id:
        return _deny(inviter_role, target_role, target_tenant_id, AuthorizationRoleGrantDenialCode.TENANT_MISMATCH)
    if inviter_assignment.status is not RoleAssignmentStatus.ACTIVE:
        return _deny(inviter_role, target_role, target_tenant_id, AuthorizationRoleGrantDenialCode.INACTIVE_AUTHORITY)
    if inviter_role not in CANONICAL_AUTHORIZATION_ROLES:
        return _deny(inviter_role, target_role, target_tenant_id, AuthorizationRoleGrantDenialCode.UNKNOWN_INVITER_ROLE)
    if target_role not in CANONICAL_AUTHORIZATION_ROLES:
        return _deny(inviter_role, target_role, target_tenant_id, AuthorizationRoleGrantDenialCode.UNKNOWN_TARGET_ROLE)
    if ROLE_GRANT_PERMISSION not in ROLE_PERMISSIONS_MAP.get(inviter_role, ()):
        return _deny(inviter_role, target_role, target_tenant_id, AuthorizationRoleGrantDenialCode.MISSING_GRANT_PERMISSION)
    if (inviter_role, target_role) not in ALLOW_EDGES:
        return _deny(inviter_role, target_role, target_tenant_id, AuthorizationRoleGrantDenialCode.GRANT_NOT_PERMITTED)
    if (
        target_role in {PLATFORM_EMPLOYEE_ADMISSION_ROLE, COMPANY_DOCUMENT_READER_ROLE, PROJECTS_PLATFORM_OWNER_ROLE}
        and target_tenant_id != WILSY_COMPANY_TENANT_ID
    ):
        return _deny(
            inviter_role,
            target_role,
            target_tenant_id,
            AuthorizationRoleGrantDenialCode.GRANT_NOT_PERMITTED,
        )
    return AuthorizationRoleGrantDecision(True, inviter_role, target_role, target_tenant_id)


__all__ = ["VERSION", "ROLE_GRANT_PERMISSION", "PLATFORM_EMPLOYEE_ADMISSION_ROLE", "COMPANY_DOCUMENT_READER_ROLE", "PROJECTS_PLATFORM_OWNER_ROLE", "CANONICAL_AUTHORIZATION_ROLES", "ALLOW_EDGES", "AuthorizationRoleGrantDenialCode", "AuthorizationRoleGrantDecision", "evaluate_authorization_role_grant"]

# ARTIFACT: authorization_role_delegation_policy.py
# VERSION: v1.3.0-PROJECTS-PLATFORM-OWNER-DELEGATION
# AUTHORITY BOUNDARY: explicit authorization-role delegation evaluation only; this policy creates no assignment
# TENANT POSTURE: exact assignment tenant equality required; platform-only roles are limited to the canonical WILSY company tenant
# FAIL-CLOSED POSTURE: unknown, inactive, malformed, unauthorized, and out-of-scope inputs deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
