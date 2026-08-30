"""TITLE: WILSY OS Role Definition Policy.
VERSION: v1.0.1-WILSY-ROLE-DEFINITION-POLICY
AUTHORITY: Canonical Python definition of institutional role identifiers and their permission grants only.
EPITOME: Deterministic code-defined role policy separating role meaning from current principal/tenant role assignment.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/roles.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-29.
CHANGELOG: v1.0.1-WILSY-ROLE-DEFINITION-POLICY removes legacy and ambiguous permission grants fail-closed pending governed semantic normalization.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Contains no credentials, principal profiles, membership records, or runtime secrets; unknown or malformed role inputs fail closed.
TENANT BOUNDARY: Role definitions are tenant-agnostic policy only; current principal/tenant possession requires governed RoleAssignmentAuthority.
AUTHORITY BOUNDARY: Owns role identifiers and explicit role-to-permission policy only. Does not own assignment, lifecycle, membership, credentials, authentication, authorization decisions, or financial execution.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""
from __future__ import annotations
from collections.abc import Iterable

VERSION = "v1.0.1-WILSY-ROLE-DEFINITION-POLICY"

ROLE_PERMISSIONS_MAP: dict[str, list[str]] = {
    "SOVEREIGN_ARCHITECT": ["kernel:read", "kernel:write", "governance:evaluate", "artifacts:read"],
    "ENTERPRISE_ADMIN": ["kernel:read", "governance:evaluate", "artifacts:read"],
    "AUDITOR": ["kernel:read", "artifacts:read", "governance:read", "audit:read"],
    "SERVICE_WORKER": ["artifacts:write", "events:publish"],
}

def get_permissions_for_roles(roles: Iterable[str]) -> list[str]:
    """Expand defined roles into deterministic unique permissions without authorization."""
    if isinstance(roles, (str, bytes)):
        return []
    permissions: set[str] = set()
    for role in roles:
        if isinstance(role, str):
            permissions.update(ROLE_PERMISSIONS_MAP.get(role, ()))
    return sorted(permissions)

def get_roles_granting_permission(permission: str) -> tuple[str, ...]:
    """Return defined roles explicitly granting an exact permission string."""
    if not isinstance(permission, str) or not permission:
        return ()
    return tuple(sorted(role for role, grants in ROLE_PERMISSIONS_MAP.items() if permission in grants))

__all__ = ["ROLE_PERMISSIONS_MAP", "VERSION", "get_permissions_for_roles", "get_roles_granting_permission"]

# ARTIFACT: roles.py
# VERSION: v1.0.1-WILSY-ROLE-DEFINITION-POLICY
# AUTHORITY BOUNDARY: canonical deterministic role identifiers and explicit role-to-permission definitions only
# TENANT POSTURE: role definitions are tenant-agnostic; current tenant-scoped possession requires governed RoleAssignmentAuthority
# FAIL-CLOSED POSTURE: unknown or malformed role inputs never manufacture role or permission authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
