"""WILSY OS pure authorization-role revocation-edge policy.

TITLE: Authorization Role Revocation Policy
VERSION: v1.0.0-P1-R3A-PURE-AUTHORIZATION-ROLE-REVOCATION-POLICY
AUTHORITY: Wilsy OS Core Governance / Sovereign IAM Design
EPITOME: Decide whether one already-trusted, already-current authorization-role
         revocation edge is structurally permitted by the frozen normal graph.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/authorization_role_revocation_policy.py
COLLABORATION / OWNERSHIP: P1-R3A owns pure edge policy; a later command layer
                            must independently prove actor authorization and own
                            persistence, evidence, and transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.0.0-P1-R3A freezes ENTERPRISE_ADMIN revocation of ACTIVE AUDITOR
           and SERVICE_WORKER assignments as the only normal allowed edges,
           with categorical enterprise-root and system-root target protection.
COMPLIANCE: NIST privileged-access lifecycle principles; POPIA section 19;
            GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Exact closed graph, strict identity validation,
                             same-tenant enforcement, and fail-closed denials.
TENANT BOUNDARY: Actor and target tenant identifiers must be exact and equal.
AUTHORITY BOUNDARY: Pure revocation-edge policy only. It does not prove actor
                    authorization, grant permissions, mutate role assignments,
                    persist evidence, own transaction lifecycle, implement root
                    rotation, implement privileged activation, or implement
                    break glass.
FINANCIAL AUTHORITY BOUNDARY: No financial authority; Kennel EOS exclusively
                              owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Malformed input, unknown operations or roles,
                         cross-tenant requests, inactive targets, non-admin
                         actors, root targets, and every non-allowlisted edge deny.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from tools.eos.auth.role_assignment import RoleAssignmentStatus


VERSION: Final[str] = "v1.0.0-P1-R3A-PURE-AUTHORIZATION-ROLE-REVOCATION-POLICY"
ROLE_REVOKE_OPERATION: Final[str] = "role_revoke"
ENTERPRISE_ADMIN: Final[str] = "ENTERPRISE_ADMIN"
SOVEREIGN_ARCHITECT: Final[str] = "SOVEREIGN_ARCHITECT"
AUDITOR: Final[str] = "AUDITOR"
SERVICE_WORKER: Final[str] = "SERVICE_WORKER"

_KNOWN_ROLES: Final[frozenset[str]] = frozenset(
    {ENTERPRISE_ADMIN, SOVEREIGN_ARCHITECT, AUDITOR, SERVICE_WORKER}
)
_NORMAL_REVOCATION_EDGES: Final[frozenset[tuple[str, str]]] = frozenset(
    {
        (ENTERPRISE_ADMIN, AUDITOR),
        (ENTERPRISE_ADMIN, SERVICE_WORKER),
    }
)


class AuthorizationRoleRevocationDenialCode(StrEnum):
    """Closed, non-secret reasons why a normal revocation edge is denied."""

    MALFORMED_INPUT = "MALFORMED_INPUT"
    UNKNOWN_OPERATION = "UNKNOWN_OPERATION"
    CROSS_TENANT = "CROSS_TENANT"
    TARGET_ASSIGNMENT_NOT_ACTIVE = "TARGET_ASSIGNMENT_NOT_ACTIVE"
    ACTOR_ROLE_NOT_AUTHORIZED = "ACTOR_ROLE_NOT_AUTHORIZED"
    TARGET_ROLE_NOT_REVOCABLE = "TARGET_ROLE_NOT_REVOCABLE"
    ROOT_LIFECYCLE_REQUIRED = "ROOT_LIFECYCLE_REQUIRED"
    SYSTEM_ROOT_NOT_TENANT_DELEGATION = "SYSTEM_ROOT_NOT_TENANT_DELEGATION"


@dataclass(frozen=True, slots=True)
class AuthorizationRoleRevocationDecision:
    """Immutable pure decision suitable for later command-certificate input.

    The value records only supplied structural facts and the policy result. It
    creates no durable evidence, authorization, assignment mutation, or
    financial authority.
    """

    allowed: bool
    denial_code: AuthorizationRoleRevocationDenialCode | None
    operation: object
    actor_principal_id: object
    actor_tenant_id: object
    actor_authorization_role: object
    target_principal_id: object
    target_tenant_id: object
    target_authorization_role: object
    target_assignment_status: object


def _decision(
    *,
    allowed: bool,
    denial_code: AuthorizationRoleRevocationDenialCode | None,
    operation: object,
    actor_principal_id: object,
    actor_tenant_id: object,
    actor_authorization_role: object,
    target_principal_id: object,
    target_tenant_id: object,
    target_authorization_role: object,
    target_assignment_status: object,
) -> AuthorizationRoleRevocationDecision:
    """Construct one immutable decision without coercing untrusted facts."""
    return AuthorizationRoleRevocationDecision(
        allowed=allowed,
        denial_code=denial_code,
        operation=operation,
        actor_principal_id=actor_principal_id,
        actor_tenant_id=actor_tenant_id,
        actor_authorization_role=actor_authorization_role,
        target_principal_id=target_principal_id,
        target_tenant_id=target_tenant_id,
        target_authorization_role=target_authorization_role,
        target_assignment_status=target_assignment_status,
    )


def evaluate_authorization_role_revocation(
    *,
    operation: object,
    actor_principal_id: object,
    actor_tenant_id: object,
    actor_authorization_role: object,
    target_principal_id: object,
    target_tenant_id: object,
    target_authorization_role: object,
    target_assignment_status: object,
) -> AuthorizationRoleRevocationDecision:
    """Evaluate one exact normal authorization-role revocation edge.

    All input facts must already be trusted and current. This pure function does
    not prove principal, membership, business-role, permission, or actor-role
    currentness. It performs no I/O or mutation. Ordinary revocation always
    denies ENTERPRISE_ADMIN and SOVEREIGN_ARCHITECT targets because root
    rotation, recovery, privileged activation, and break glass are separate
    constitutional lifecycles.
    """
    values = (
        operation,
        actor_principal_id,
        actor_tenant_id,
        actor_authorization_role,
        target_principal_id,
        target_tenant_id,
        target_authorization_role,
    )
    malformed = any(
        not isinstance(value, str) or not value or value != value.strip()
        for value in values
    ) or not isinstance(target_assignment_status, RoleAssignmentStatus)

    facts = {
        "operation": operation,
        "actor_principal_id": actor_principal_id,
        "actor_tenant_id": actor_tenant_id,
        "actor_authorization_role": actor_authorization_role,
        "target_principal_id": target_principal_id,
        "target_tenant_id": target_tenant_id,
        "target_authorization_role": target_authorization_role,
        "target_assignment_status": target_assignment_status,
    }

    if malformed:
        return _decision(allowed=False, denial_code=AuthorizationRoleRevocationDenialCode.MALFORMED_INPUT, **facts)
    if operation != ROLE_REVOKE_OPERATION:
        return _decision(allowed=False, denial_code=AuthorizationRoleRevocationDenialCode.UNKNOWN_OPERATION, **facts)
    if actor_tenant_id != target_tenant_id:
        return _decision(allowed=False, denial_code=AuthorizationRoleRevocationDenialCode.CROSS_TENANT, **facts)
    if target_assignment_status is not RoleAssignmentStatus.ACTIVE:
        return _decision(allowed=False, denial_code=AuthorizationRoleRevocationDenialCode.TARGET_ASSIGNMENT_NOT_ACTIVE, **facts)
    if target_authorization_role == ENTERPRISE_ADMIN:
        return _decision(allowed=False, denial_code=AuthorizationRoleRevocationDenialCode.ROOT_LIFECYCLE_REQUIRED, **facts)
    if target_authorization_role == SOVEREIGN_ARCHITECT:
        return _decision(allowed=False, denial_code=AuthorizationRoleRevocationDenialCode.SYSTEM_ROOT_NOT_TENANT_DELEGATION, **facts)
    if actor_authorization_role not in _KNOWN_ROLES or actor_authorization_role != ENTERPRISE_ADMIN:
        return _decision(allowed=False, denial_code=AuthorizationRoleRevocationDenialCode.ACTOR_ROLE_NOT_AUTHORIZED, **facts)
    if target_authorization_role not in _KNOWN_ROLES or target_authorization_role not in {AUDITOR, SERVICE_WORKER}:
        return _decision(allowed=False, denial_code=AuthorizationRoleRevocationDenialCode.TARGET_ROLE_NOT_REVOCABLE, **facts)
    if (actor_authorization_role, target_authorization_role) not in _NORMAL_REVOCATION_EDGES:
        return _decision(allowed=False, denial_code=AuthorizationRoleRevocationDenialCode.TARGET_ROLE_NOT_REVOCABLE, **facts)
    return _decision(allowed=True, denial_code=None, **facts)


__all__ = [
    "VERSION",
    "ROLE_REVOKE_OPERATION",
    "AuthorizationRoleRevocationDenialCode",
    "AuthorizationRoleRevocationDecision",
    "evaluate_authorization_role_revocation",
]

# ARTIFACT: authorization_role_revocation_policy.py
# VERSION: v1.0.0-P1-R3A-PURE-AUTHORIZATION-ROLE-REVOCATION-POLICY
# AUTHORITY BOUNDARY: pure revocation-edge policy only; no actor authorization, mutation, evidence, transaction, root rotation, activation, or break glass
# TENANT POSTURE: exact same-tenant structural facts are mandatory; every cross-tenant edge denies
# FAIL-CLOSED POSTURE: only ENTERPRISE_ADMIN to ACTIVE AUDITOR or SERVICE_WORKER is allowed; all other edges deny
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
