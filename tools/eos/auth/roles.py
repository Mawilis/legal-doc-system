"""TITLE: WILSY OS Role Definition Policy.
VERSION: v1.10.0-M11-R8-R3B-P8-P3D-P4A
AUTHORITY: Canonical Python role identifiers and explicit permission grants.
EPITOME: Defines current tenant-scoped authorization roles, including
least-privilege subscription/plan-catalogue grants and dedicated inbound
merchant-configuration/provider-policy administration without creating current
possession authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/roles.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-09.
CHANGELOG:
    2026-09-10 v1.10.0-M11-R8-R3B-P8-P3D-P4A adds exactly four
    credential-security permissions to the existing INBOUND_PROVIDER_SECURITY_ADMIN;
    no new role and no unrelated grant changes.
    2026-09-09 v1.9.0-M11-R8-R3B-P8-P3B-I2-R3 adds only the bounded
    remediation permission to the existing INBOUND_PROVIDER_SECURITY_ADMIN;
    no new role or broader lifecycle authority is introduced.
    2026-09-09 v1.8.0-M11-R8-R3B-P8-P3A adds four dedicated least-privilege
    inbound merchant-configuration/provider-policy administration roles;
    existing roles and grants remain unchanged.
    2026-09-09 v1.7.0-M11-R8-R3B-P6A adds only the dedicated
    INBOUND_COLLECTION_AUTHORIZATION_ADMIN grant for the exact inbound
    collection authorization-request privilege.
    2026-09-04 runtime VERSION is the canonical policy provenance source for
    trusted authorization-evidence capture; no grant semantics changed.
    2026-09-04 v1.4.0-PLATFORM-BILLING-RELEASE-GRANTS grants
    platform_billing:release only to ENTERPRISE_ADMIN.
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


VERSION = "v1.10.0-M11-R8-R3B-P8-P3D-P4A"


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
        "platform_billing:release",
        "tenant:business_role:read",
        "tenant:business_role:write",
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
        "tenant:business_role:read",
    ],
    "SERVICE_WORKER": [
        "artifacts:write",
        "events:publish",
    ],
    "PLATFORM_BILLING_PROVIDER_POLICY_ADMIN": [
        "platform_billing:provider_policy:admin",
    ],
    "ACCOUNTS_PAYABLE_PROVIDER_POLICY_ADMIN": [
        "accounts_payable:provider_policy:admin",
    ],
    "INBOUND_COLLECTION_AUTHORIZATION_ADMIN": [
        "inbound_collection:authorization:create",
    ],
    "INBOUND_MERCHANT_CONFIGURATION_ADMIN": [
        "inbound_merchant_configuration:register",
        "inbound_merchant_configuration:lifecycle",
    ],
    "INBOUND_PROVIDER_SECURITY_ADMIN": [
        "inbound_merchant_configuration:security",
        "inbound_merchant_configuration:remediate",
        "inbound_provider_policy:emergency_disable",
        "inbound_provider_credential_security:eligibility_issue",
        "inbound_provider_credential_security:revoke",
        "inbound_provider_credential_security:compromise",
        "inbound_provider_credential_security:rotate",
    ],
    "INBOUND_PROVIDER_POLICY_ADMIN": [
        "inbound_provider_policy:author",
    ],
    "INBOUND_PROVIDER_POLICY_ACTIVATION_ADMIN": [
        "inbound_provider_policy:activate",
        "inbound_provider_policy:deactivate",
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
# VERSION: v1.10.0-M11-R8-R3B-P8-P3D-P4A
# AUTHORITY BOUNDARY: role identifiers and deterministic permission definitions only; current assignment is separate authority
# TENANT POSTURE: role definitions never establish tenant membership or role possession
# FAIL-CLOSED POSTURE: unknown roles and permissions never manufacture grants
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
