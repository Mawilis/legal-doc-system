"""TITLE: WILSY OS Authorization-Role Delegation Policy.
VERSION: v1.0.0-WILSY-A0P-GD1
AUTHORITY: Explicit GD1 authorization-role grant law.
PURPOSE: Evaluate whether canonical role evidence may grant a target role.
EPITOME: Pure, deterministic, fail-closed tenant-local delegation authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/authorization_role_delegation_policy.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
SECURITY / PRIVACY POSTURE: No persistence, secrets, network, or caller permission trust.
TENANT BOUNDARY: Inviter assignment and target tenant must match exactly.
AUTHORITY BOUNDARY: RoleAssignmentAuthority evidence only; no lifecycle mutation.
FINANCIAL AUTHORITY BOUNDARY: No financial or Kennel execution authority.
TRANSACTION BOUNDARY: Pure evaluator; caller owns orchestration and sessions.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 implements explicit governance decision GD1.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from .role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from .roles import ROLE_PERMISSIONS_MAP

VERSION = "v1.0.0-WILSY-A0P-GD1"
ROLE_GRANT_PERMISSION = "tenant:role_assignment:write"
CANONICAL_AUTHORIZATION_ROLES: Final = frozenset(ROLE_PERMISSIONS_MAP)
_ALLOW_EDGES: Final = frozenset({("ENTERPRISE_ADMIN", "AUDITOR"), ("ENTERPRISE_ADMIN", "SERVICE_WORKER")})
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
    """Evaluate one canonical role assignment against explicit GD1 law."""
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
    return AuthorizationRoleGrantDecision(True, inviter_role, target_role, target_tenant_id)


__all__ = ["VERSION", "ROLE_GRANT_PERMISSION", "CANONICAL_AUTHORIZATION_ROLES", "ALLOW_EDGES", "AuthorizationRoleGrantDenialCode", "AuthorizationRoleGrantDecision", "evaluate_authorization_role_grant"]

# ARTIFACT: authorization_role_delegation_policy.py
# VERSION: v1.0.0-WILSY-A0P-GD1
# AUTHORITY BOUNDARY: explicit authorization-role delegation evaluation only
# TENANT POSTURE: exact assignment tenant equality required
# FAIL-CLOSED POSTURE: unknown, inactive, malformed, and unauthorized inputs deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
