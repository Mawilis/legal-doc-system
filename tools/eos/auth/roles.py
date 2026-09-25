"""TITLE: WILSY OS Role Definition Policy.
VERSION: v1.25.0-L8-8I-CONFLICT-REVIEW-GRANTS
AUTHORITY: Canonical Python role identifiers and explicit permission grants.
EPITOME: Defines current tenant-scoped authorization roles, including
least-privilege subscription/plan-catalogue grants, read-only WILSY AI
usage-capacity and billing-intelligence evidence access, and dedicated inbound
merchant-configuration/provider-policy administration plus least-privilege
field-service outcome/return commands, sheriff-only process-service directory
provisioning, sheriff-only office-receipt authority, and least-privilege
law-firm client-matter visibility provisioning plus one least-privilege
LEGAL_CLIENT projection-read grant without creating tenant-wide matter reads,
deputy possession, service, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/roles.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-23.
CHANGELOG:
    2026-09-25 v1.25.0-L8-8I-CONFLICT-REVIEW-GRANTS grants
    legal_operations:conflict_review:write exactly to LEGAL_PARTNER and
    LEGAL_ATTORNEY for future server-authorized human conflict-review
    determination composition. LEGAL_PARALEGAL, LEGAL_SECRETARY, LEGAL_FINANCE,
    LEGAL_CLIENT, SHERIFF, DEPUTY, ENTERPRISE_ADMIN, AUDITOR, system, service,
    provider and sovereign roles remain excluded. Static role policy still does
    not prove current assignment, ACTIVE tenant membership, eligible business
    role, durable screening evidence, reviewer authorization, conflict finding,
    waiver, ethical wall, recusal, engagement, representation, payment,
    execution or settlement authority.
    2026-09-23 v1.24.0-L8-7D2-CLIENT-MATTER-READ-GRANT grants
    legal_operations:client_matter:read exactly to LEGAL_CLIENT for the future
    explicitly-bound client matter projection. No law-firm, sheriff, deputy,
    finance, enterprise, audit, system, service, or provider role receives the
    grant. Static policy still does not prove current assignment, ACTIVE
    membership, ACTIVE visibility binding, matter scope, HTTP access, service,
    billing, payment, execution, or settlement authority.
    2026-09-23 v1.23.0-L8-7C2-CLIENT-VISIBILITY-WRITE-GRANTS grants
    legal_operations:client_visibility:write only to LEGAL_PARTNER,
    LEGAL_ATTORNEY, and LEGAL_PARALEGAL for future L8-7 grant/revoke
    provisioning. LEGAL_SECRETARY, LEGAL_FINANCE, LEGAL_CLIENT, SHERIFF,
    DEPUTY, ENTERPRISE_ADMIN, AUDITOR, system, service and provider roles remain
    excluded. Static grant policy does not prove current assignment, membership,
    target-client eligibility, CaseMatter visibility, client read, service,
    billing, payment, execution or settlement authority.
    2026-09-23 v1.22.0-L8-6C-DEPUTY-PERSONAL-QUEUE-IAM-GRANTS grants
    legal_operations:deputy_queue:read only to DEPUTY for binding-scoped
    personal active-work projection. SHERIFF retains the distinct tenant-wide
    legal_operations:queue:read permission and receives no deputy-personal
    impersonation capability.
    2026-09-23 v1.21.0-L8-6A-SHERIFF-QUEUE-READ-IAM-GRANTS grants
    legal_operations:queue:read only to SHERIFF for own-tenant certified
    operational-queue projection; DEPUTY and every other role remain excluded.
    2026-09-23 v1.20.0-L8-3-LEGAL-OPERATIONS-RECEIPT-IAM-GRANTS grants
    legal_operations:receipt:write only to SHERIFF; legal-practice, deputy,
    client, enterprise, service, and system roles remain excluded.
    2026-09-23 v1.19.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-IAM-GRANTS grants
    legal_operations:directory:write only to the SHERIFF authorization role;
    partner, attorney, paralegal, secretary, finance, deputy, client, general
    enterprise, service, and system roles remain excluded.
    2026-09-17 v1.18.0-C1E-R1 grants legal-advisory generate/read only to
    the seven approved tenant legal roles.
    2026-09-17 v1.17.0-C1C-R1 grants the dedicated legal-services execution
    permission to the approved legal, sheriff, deputy, and enterprise roles.
    2026-09-16 v1.16.0-C1B-R2 grants reasoning execution only to the
    enterprise administrator role; provider/model authority remains server-owned.
    2026-09-15 v1.15.0-L7B-WILSY-AI-LEGAL-TOOL-GRANTS adds the dedicated
    own-tenant Legal Tool Gateway read grant to seven legal roles; clients
    remain excluded and Kennel financial execution is unchanged.
    2026-09-15 v1.14.0-L7B-LEGAL-OPERATIONS-IAM-GRANTS adds least-privilege
    field-service outcome and return grants to the published legal roles;
    Kennel financial execution stays outside this map.
    2026-09-15 v1.13.0-L7A-LEGAL-OPERATIONS-IAM-GRANTS adds bounded
    legal-practice authorization-role grants; Kennel financial execution stays
    outside this map.
    2026-09-13 v1.12.0-M14-P2-BILLING-INTELLIGENCE-EVIDENCE-READ-GRANTS
    grants the read-only billing-intelligence evidence permission exactly to
    ENTERPRISE_ADMIN and AUDITOR; no assignment, cross-tenant, quota,
    commercial, or financial authority is introduced.
    2026-09-13 v1.11.0-M13-P6D-WILSY-AI-CAPACITY-READ-GRANTS grants the
    read-only WILSY AI usage-capacity evidence permission exactly to
    ENTERPRISE_ADMIN and AUDITOR; no assignment, cross-tenant, quota,
    commercial, or financial authority is introduced.
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
RoleAssignmentAuthority after ACTIVE tenant membership admission; WILSY AI
usage-capacity and billing-intelligence evidence are read-only and remain
own-tenant scoped.
AUTHORITY BOUNDARY: Owns only deterministic role-to-permission policy.
Authentication, membership, role assignment, WILSY AI capacity derivation and
final authorization remain separate authorities.
FINANCIAL AUTHORITY BOUNDARY: Subscription and plan catalogue management and
WILSY AI usage-capacity and billing-intelligence evidence reads are non-financial policy capabilities;
they cannot authorize, release, execute, collect, or settle payment. Kennel EOS
remains exclusive.
"""

from __future__ import annotations

from collections.abc import Iterable


VERSION = "v1.25.0-L8-8I-CONFLICT-REVIEW-GRANTS"


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
        "wilsy_ai:usage_capacity:read",
        "billing_intelligence:evidence:read",
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
        "wilsy_ai:usage_capacity:read",
        "billing_intelligence:evidence:read",
        "tenant:business_role:read",
    ],
    "LEGAL_PARTNER": [
        "legal_operations:instruction:read",
        "legal_operations:instruction:write",
        "legal_operations:client_visibility:write",
        "legal_operations:conflict_review:write",
        "legal_operations:allocation:read",
        "legal_operations:allocation:write",
        "legal_operations:attempt:read",
        "legal_operations:return:read",
        "legal_operations:billing:read",
        "legal_operations:invoice:read",
    ],
    "LEGAL_ATTORNEY": [
        "legal_operations:instruction:read",
        "legal_operations:instruction:write",
        "legal_operations:client_visibility:write",
        "legal_operations:conflict_review:write",
        "legal_operations:allocation:read",
        "legal_operations:allocation:write",
        "legal_operations:attempt:read",
        "legal_operations:return:read",
        "legal_operations:billing:read",
        "legal_operations:invoice:read",
    ],
    "LEGAL_PARALEGAL": [
        "legal_operations:instruction:read",
        "legal_operations:instruction:write",
        "legal_operations:client_visibility:write",
        "legal_operations:allocation:read",
        "legal_operations:allocation:write",
        "legal_operations:attempt:read",
        "legal_operations:return:read",
        "legal_operations:invoice:read",
    ],
    "LEGAL_SECRETARY": [
        "legal_operations:instruction:read",
        "legal_operations:allocation:read",
        "legal_operations:attempt:read",
        "legal_operations:return:read",
        "legal_operations:invoice:read",
    ],
    "LEGAL_FINANCE": [
        "legal_operations:billing:read",
        "legal_operations:invoice:read",
    ],
    "SHERIFF": [
        "legal_operations:directory:write",
        "legal_operations:receipt:write",
        "legal_operations:queue:read",
        "legal_operations:allocation:read",
        "legal_operations:allocation:write",
        "legal_operations:attempt:read",
        "legal_operations:attempt:write",
        "legal_operations:return:read",
    ],
    "DEPUTY": [
        "legal_operations:deputy_queue:read",
        "legal_operations:attempt:read",
        "legal_operations:attempt:write",
        "legal_operations:return:read",
    ],
    "LEGAL_CLIENT": [
        "legal_operations:invoice:read",
        "legal_operations:client_matter:read",
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


for _role_name in ("LEGAL_PARTNER", "LEGAL_ATTORNEY", "LEGAL_PARALEGAL", "LEGAL_SECRETARY", "SHERIFF", "DEPUTY"):
    ROLE_PERMISSIONS_MAP[_role_name].append("legal_operations:return:write")
for _role_name in ("SHERIFF", "DEPUTY"):
    ROLE_PERMISSIONS_MAP[_role_name].append("legal_operations:attempt_outcome:write")
for _role_name in ("LEGAL_PARTNER", "LEGAL_ATTORNEY", "LEGAL_PARALEGAL", "LEGAL_SECRETARY", "LEGAL_FINANCE", "SHERIFF", "DEPUTY"):
    ROLE_PERMISSIONS_MAP[_role_name].append("wilsy_ai:legal_tool:read")
for _role_name in ("ENTERPRISE_ADMIN",):
    ROLE_PERMISSIONS_MAP[_role_name].append("wilsy_ai:reasoning:execute")
for _role_name in ("LEGAL_PARTNER", "LEGAL_ATTORNEY", "LEGAL_PARALEGAL", "LEGAL_SECRETARY", "LEGAL_FINANCE", "SHERIFF", "DEPUTY", "ENTERPRISE_ADMIN"):
    ROLE_PERMISSIONS_MAP[_role_name].append("wilsy_ai:legal_services:execute")
for _role_name in ("LEGAL_PARTNER", "LEGAL_ATTORNEY", "LEGAL_PARALEGAL", "LEGAL_SECRETARY", "LEGAL_FINANCE", "SHERIFF", "DEPUTY"):
    ROLE_PERMISSIONS_MAP[_role_name].extend(("wilsy_ai:legal_advisory:generate", "wilsy_ai:legal_advisory:read"))


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
# VERSION: v1.25.0-L8-8I-CONFLICT-REVIEW-GRANTS
# AUTHORITY BOUNDARY: role identifiers and deterministic permission definitions only; current assignment is separate authority
# TENANT POSTURE: role definitions never establish tenant membership or role possession; conflict-review write is partner/attorney-only policy and client-matter read remains visibility-bound
# FAIL-CLOSED POSTURE: unknown roles and permissions never manufacture grants
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT