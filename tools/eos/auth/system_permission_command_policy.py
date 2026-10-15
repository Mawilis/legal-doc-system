"""TITLE: WILSY OS System Permission Command Policy.
VERSION: v1.0.0-D12-COMMAND-POLICY
AUTHORITY: Immutable source-governed bootstrap and ongoing delegation policy.
EPITOME: Prevents bootstrap mismatch, recursion, wildcard, and arbitrary SYSTEM delegation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/system_permission_command_policy.py
COLLABORATION: Bootstrap seed, assignment command, and revocation command services.
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.0.0 freezes two seed mappings and one ongoing delegable permission.
COMPLIANCE / SECURITY: Deterministic immutable policy; no environment or database expansion.
TENANT BOUNDARY: SYSTEM only; tenant permissions are denied.
AUTHORITY BOUNDARY: Policy constrains commands and grants no permission by itself.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from types import MappingProxyType
from typing import Final

VERSION: Final[str] = "v1.0.0-D12-COMMAND-POLICY"
ASSIGN_COMMAND_PERMISSION: Final[str] = "system_permission_assignment:write"
REVOKE_COMMAND_PERMISSION: Final[str] = "system_permission_assignment:revoke"
PRIVILEGED_ACTIVATION_ISSUE_PERMISSION: Final[str] = "privileged_activation:issue"
ASSIGN_BOOTSTRAP_PURPOSE: Final[str] = "SEED_SYSTEM_PERMISSION_ASSIGNMENT_COMMAND_AUTHORITY"
REVOKE_BOOTSTRAP_PURPOSE: Final[str] = "SEED_SYSTEM_PERMISSION_REVOCATION_COMMAND_AUTHORITY"

BOOTSTRAP_PERMISSION_BY_PURPOSE: Final = MappingProxyType({
    ASSIGN_BOOTSTRAP_PURPOSE: ASSIGN_COMMAND_PERMISSION,
    REVOKE_BOOTSTRAP_PURPOSE: REVOKE_COMMAND_PERMISSION,
})
ONGOING_ASSIGNABLE_PERMISSIONS: Final = frozenset({PRIVILEGED_ACTIVATION_ISSUE_PERMISSION})
ONGOING_REVOCABLE_PERMISSIONS: Final = frozenset({PRIVILEGED_ACTIVATION_ISSUE_PERMISSION})


class SystemPermissionCommandPolicyError(ValueError):
    """Fail-closed rejection of material outside the source-governed policy."""


def _exact(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or "*" in value:
        raise SystemPermissionCommandPolicyError(name + "_INVALID")
    return value


def bootstrap_seed_permission(purpose: str) -> str:
    """Return the sole permission seedable by an exact bootstrap purpose."""
    exact = _exact("BOOTSTRAP_PURPOSE", purpose)
    try:
        return BOOTSTRAP_PERMISSION_BY_PURPOSE[exact]
    except KeyError as error:
        raise SystemPermissionCommandPolicyError("BOOTSTRAP_PURPOSE_NOT_ALLOWED") from error


def require_bootstrap_seed(purpose: str, permission_id: str) -> None:
    """Require the exact frozen purpose-to-command-permission mapping."""
    if bootstrap_seed_permission(purpose) != _exact("PERMISSION_ID", permission_id):
        raise SystemPermissionCommandPolicyError("BOOTSTRAP_SEED_PERMISSION_MISMATCH")


def require_ongoing_assignment(permission_id: str) -> None:
    """Allow ongoing assignment of only privileged activation issuance."""
    if _exact("PERMISSION_ID", permission_id) not in ONGOING_ASSIGNABLE_PERMISSIONS:
        raise SystemPermissionCommandPolicyError("PERMISSION_NOT_ASSIGNABLE")


def require_ongoing_revocation(permission_id: str) -> None:
    """Allow ongoing revocation of only privileged activation issuance."""
    if _exact("PERMISSION_ID", permission_id) not in ONGOING_REVOCABLE_PERMISSIONS:
        raise SystemPermissionCommandPolicyError("PERMISSION_NOT_REVOCABLE")


__all__ = ["VERSION", "ASSIGN_COMMAND_PERMISSION", "REVOKE_COMMAND_PERMISSION", "PRIVILEGED_ACTIVATION_ISSUE_PERMISSION", "ASSIGN_BOOTSTRAP_PURPOSE", "REVOKE_BOOTSTRAP_PURPOSE", "BOOTSTRAP_PERMISSION_BY_PURPOSE", "ONGOING_ASSIGNABLE_PERMISSIONS", "ONGOING_REVOCABLE_PERMISSIONS", "SystemPermissionCommandPolicyError", "bootstrap_seed_permission", "require_bootstrap_seed", "require_ongoing_assignment", "require_ongoing_revocation"]
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: system_permission_command_policy.py
# VERSION: v1.0.0-D12-COMMAND-POLICY
# AUTHORITY BOUNDARY: CLOSED COMMAND POLICY ONLY; NO GRANT AUTHORITY
# TENANT POSTURE: SYSTEM ONLY
# FAIL-CLOSED POSTURE: NO RECURSION, WILDCARD, ARBITRARY, OR FINANCIAL AUTHORITY
# FINANCIAL EXECUTION AUTHORITY: KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
