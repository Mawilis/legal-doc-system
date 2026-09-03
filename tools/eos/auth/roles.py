"""TITLE: WILSY OS Role Definition Policy.
VERSION: v1.3.0-PLAN-PERMISSION-GRANTS
AUTHORITY: Canonical Python role identifiers and explicit permission grants.
EPITOME: Extends current tenant-scoped authorization roles with least-privilege
subscription and plan-catalogue read/manage grants without creating current
possession authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/roles.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-03.
CHANGELOG:
    2026-09-03 v1.3.0-PLAN-PERMISSION-GRANTS grants plan:read to
    ENTERPRISE_ADMIN and AUDITOR, plan:manage only to ENTERPRISE_ADMIN,
    and grants neither capability to SERVICE_WORKER or SOVEREIGN_ARCHITECT.
    v1.2.0-SUBSCRIPTION-PERMISSION-GRANTS grants subscription:read to
    ENTERPRISE_ADMIN and AUDITOR, subscription:manage only to
    ENTERPRISE_ADMIN, and grants neither capability to SERVICE_WORKER or
    SOVEREIGN_ARCHITECT.
    v1.1.0-WILSY-TENANT-PERMISSION-GRANTS migrated the canonical tenant
    profile, membership and role-assignment permissions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Contains no credentials, principal records,
memberships or runtime secrets. A role definition never proves possession.
TENANT BOUNDARY: Current principal/tenant possession requires governed
RoleAssignmentAuthority after ACTIVE tenant membership admission.
AUTHORITY BOUNDARY: Owns only deterministic role-to-permission policy.
Authentication, membership, role assignment and final authorization remain
separate authorities.
FINANCIAL AUTHORITY BOUNDARY: Subscription and plan catalogue management are
commercial lifecycle policy only and cannot authorize, release, execute,
collect, or settle payment. Kennel EOS remains exclusive.
"""

from __future__ import annotations

from collections.abc import Iterable


VERSION = "v1.3.0-PLAN-PERMISSION-GRANTS"


ROLE_PERMISSIONS_MAP: dict[str, list[str]] = {
    "SOVEREIGN_ARCHITECT": [
        "kernel:read",
        "kernel:write",
        "governance:evaluate",
        "artifacts:read",
    ],
    "ENTERPRISE_ADMIN": [
        "kernel:read",
        "governance:evaluate",
        "artifacts:read",
        "tenant:profile:read",
        "tenant:profile:write",
        "tenant:lifecycle:archive",
        "tenant:membership:read",
        "tenant:membership:write",
        "tenant:role_assignment:read",
        "tenant:role_assignment:write",
        "subscription:read",
        "subscription:manage",
        "plan:read",
        "plan:manage",
    ],
    "AUDITOR": [
        "kernel:read",
        "artifacts:read",
        "governance:read",
        "audit:read",
        "tenant:profile:read",
        "tenant:membership:read",
        "tenant:role_assignment:read",
        "subscription:read",
        "plan:read",
    ],
    "SERVICE_WORKER": [
        "artifacts:write",
        "events:publish",
    ],
}


def get_permissions_for_roles(
    roles: Iterable[str],
) -> list[str]:
    """Expand defined roles deterministically without proving possession."""
    if isinstance(roles, (str, bytes)):
        return []

    permissions: set[str] = set()

    for role in roles:
        if isinstance(role, str):
            permissions.update(
                ROLE_PERMISSIONS_MAP.get(
                    role,
                    (),
                )
            )

    return sorted(permissions)


def get_roles_granting_permission(
    permission: str,
) -> tuple[str, ...]:
    """Return roles whose static definition grants one exact permission."""
    if (
        not isinstance(permission, str)
        or not permission
    ):
        return ()

    return tuple(
        sorted(
            role
            for role, grants
            in ROLE_PERMISSIONS_MAP.items()
            if permission in grants
        )
    )


__all__ = [
    "ROLE_PERMISSIONS_MAP",
    "VERSION",
    "get_permissions_for_roles",
    "get_roles_granting_permission",
]

# ARTIFACT: tools/eos/auth/roles.py
# VERSION: v1.3.0-PLAN-PERMISSION-GRANTS
# AUTHORITY BOUNDARY: role identifiers and deterministic permission definitions only; current assignment is separate authority
# TENANT POSTURE: role definitions never establish tenant membership or role possession
# FAIL-CLOSED POSTURE: unknown roles and permissions never manufacture grants
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
