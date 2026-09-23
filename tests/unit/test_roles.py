"""TITLE: WILSY OS Role Definition Policy Unit Contract.
VERSION: v1.17.0-L8-6C-DEPUTY-PERSONAL-QUEUE-IAM-GRANTS-CERT
AUTHORITY: Deterministic unit verification of canonical Python role-definition policy only.
EPITOME: Proves the exact closed role vocabulary, tenant/subscription/plan and
WILSY AI usage-capacity and billing-intelligence evidence read permission grants, deterministic expansion,
reverse lookup, and fail-closed non-bypass behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_roles.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-23.
CHANGELOG:
    2026-09-23 v1.17.0-L8-6C-DEPUTY-PERSONAL-QUEUE-IAM-GRANTS-CERT
    certifies legal_operations:deputy_queue:read is granted only to DEPUTY and
    is absent from SHERIFF and every other authorization role, preserving the
    distinction between personal bound work and tenant-wide sheriff queues.
    2026-09-23 v1.16.0-L8-6A-SHERIFF-QUEUE-READ-IAM-GRANTS-CERT
    certifies legal_operations:queue:read is granted only to SHERIFF and is
    absent from DEPUTY and every other authorization role.
    2026-09-23 v1.15.0-L8-3-LEGAL-OPERATIONS-RECEIPT-IAM-GRANTS-CERT
    certifies that legal_operations:receipt:write is granted only to SHERIFF
    and remains absent from all other authorization roles.
    2026-09-23 v1.14.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-IAM-GRANTS-CERT
    certifies that legal_operations:directory:write is granted only to SHERIFF
    and remains absent from partner, attorney, paralegal, secretary, finance,
    deputy, client, general enterprise, system, and service roles.
    2026-09-17 v1.13.0-C1E-R1 certifies the seven-role legal-advisory
    generate/read grant set and explicit exclusion of all other roles.
    2026-09-15 v1.11.0-L7B-WILSY-AI-LEGAL-TOOL-GRANTS-CERT certifies the
    dedicated gateway grant set and proves it does not manufacture underlying
    legal-operation permissions.
    2026-09-15 v1.10.0-L7A-LEGAL-OPERATIONS-IAM-GRANTS-CERT certifies the
    explicit Legal Operations role grants and least-authority exclusions,
    while preserving reverse lookup and malformed-alias rejection.
    2026-09-13 v1.8.0-M13-P6D-WILSY-AI-CAPACITY-READ-GRANTS-CERT certifies
    the exact own-tenant WILSY AI usage-capacity read grant for
    ENTERPRISE_ADMIN/AUDITOR, its reverse lookup, non-bypass exclusions, and
    malformed alias rejection.
    2026-09-10 v1.7.0-M11-R8-R3B-P8-P3D-P4A-CERT certifies exactly four
    credential-security grants on the existing security-admin role.
    2026-09-09 v1.6.0-M11-R8-R3B-P8-P3B-I2-R3-CERT certifies the bounded
    remediation grant on the existing security-admin role.
    2026-09-09 v1.5.0-M11-R8-R3B-P8-P3A-CERT certifies four dedicated
    inbound merchant-configuration/provider-policy roles and exact grants.
    2026-09-09 v1.4.0-M11-R8-R3B-P6A-CERT certifies the dedicated
    INBOUND_COLLECTION_AUTHORIZATION_ADMIN least-privilege grant.
    2026-09-03 v1.2.0-PLAN-PERMISSION-GRANTS-UNIT-CONTRACT certifies
    plan:read for ENTERPRISE_ADMIN/AUDITOR and plan:manage only for
    ENTERPRISE_ADMIN while retaining subscription grants and preserving
    SOVEREIGN_ARCHITECT/SERVICE_WORKER non-bypass locks.
    2026-08-30 v1.1.0-WILSY-TENANT-PERMISSION-GRANTS-UNIT-CONTRACT
    certified the bounded ENTERPRISE_ADMIN/AUDITOR tenant-permission migration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Pure policy tests with no credentials, principal
data, tenant records, persistence, secrets, or external IO.
TENANT BOUNDARY: Role definitions remain tenant-agnostic policy; current
tenant-scoped possession and WILSY AI capacity reads still require governed
RoleAssignmentAuthority and exact ACTIVE membership.
AUTHORITY BOUNDARY: Unit verification of role identifiers and explicit
permission definitions only; no assignment, authentication, authorization,
lifecycle, or transport authority.
FINANCIAL AUTHORITY BOUNDARY: No tenant/subscription/plan or WILSY AI
capacity-read grant is financial; Kennel EOS remains exclusive.
"""

from __future__ import annotations

from typing import Any, cast

import pytest

from tools.eos.auth.roles import (
    VERSION as POLICY_VERSION,
    ROLE_PERMISSIONS_MAP,
    get_permissions_for_roles,
    get_roles_granting_permission,
)

def test_runtime_version_source_is_canonical() -> None:
    assert POLICY_VERSION == "v1.22.0-L8-6C-DEPUTY-PERSONAL-QUEUE-IAM-GRANTS"

VERSION = "v1.17.0-L8-6C-DEPUTY-PERSONAL-QUEUE-IAM-GRANTS-CERT"

EXPECTED_ROLE_PERMISSIONS: dict[str, list[str]] = {
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
    ],
    "AUDITOR": [
        "kernel:read",
        "artifacts:read",
        "governance:read",
        "audit:read",
        "tenant:profile:read",
        "tenant:membership:read",
        "tenant:role_assignment:read",
    ],
    "SERVICE_WORKER": [
        "artifacts:write",
        "events:publish",
    ],
}

TENANT_PERMISSIONS = {
    "audit:read",
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
    "billing_intelligence:evidence:read",
    "legal_operations:instruction:read",
    "legal_operations:instruction:write",
    "legal_operations:directory:write",
    "legal_operations:receipt:write",
    "legal_operations:queue:read",
    "legal_operations:deputy_queue:read",
    "legal_operations:allocation:read",
    "legal_operations:allocation:write",
    "legal_operations:attempt:read",
    "legal_operations:attempt:write",
    "legal_operations:return:read",
    "legal_operations:billing:read",
    "legal_operations:invoice:read",
    "inbound_collection:authorization:create",
    "inbound_merchant_configuration:register",
    "inbound_merchant_configuration:lifecycle",
    "inbound_merchant_configuration:security",
    "inbound_merchant_configuration:remediate",
    "inbound_provider_policy:author",
    "inbound_provider_policy:activate",
    "inbound_provider_policy:deactivate",
    "inbound_provider_policy:emergency_disable",
    "inbound_provider_credential_security:eligibility_issue",
    "inbound_provider_credential_security:revoke",
    "inbound_provider_credential_security:compromise",
    "inbound_provider_credential_security:rotate",
}


def test_exact_role_vocabulary_and_grant_matrix() -> None:
    """The closed role map grants only the explicitly approved capabilities."""
    assert ROLE_PERMISSIONS_MAP["ENTERPRISE_ADMIN"] == EXPECTED_ROLE_PERMISSIONS["ENTERPRISE_ADMIN"] + ["subscription:read", "subscription:manage", "plan:read", "plan:manage", "wilsy_ai:usage_capacity:read", "billing_intelligence:evidence:read", "platform_billing:release", "tenant:business_role:read", "tenant:business_role:write", "wilsy_ai:reasoning:execute", "wilsy_ai:legal_services:execute"]
    assert ROLE_PERMISSIONS_MAP["AUDITOR"] == EXPECTED_ROLE_PERMISSIONS["AUDITOR"] + ["subscription:read", "plan:read", "wilsy_ai:usage_capacity:read", "billing_intelligence:evidence:read", "tenant:business_role:read"]


def test_legal_role_grants_are_explicit_and_least_authority() -> None:
    """Legal personas receive only the certified legal-operation capabilities."""
    assert ROLE_PERMISSIONS_MAP["LEGAL_PARTNER"] == [
        "legal_operations:instruction:read", "legal_operations:instruction:write",
        "legal_operations:allocation:read", "legal_operations:allocation:write",
        "legal_operations:attempt:read", "legal_operations:return:read",
        "legal_operations:billing:read", "legal_operations:invoice:read",
        "legal_operations:return:write",
        "wilsy_ai:legal_tool:read",
        "wilsy_ai:legal_services:execute",
        "wilsy_ai:legal_advisory:generate", "wilsy_ai:legal_advisory:read",
    ]
    assert ROLE_PERMISSIONS_MAP["LEGAL_FINANCE"] == [
        "legal_operations:billing:read", "legal_operations:invoice:read",
        "wilsy_ai:legal_tool:read",
        "wilsy_ai:legal_services:execute",
        "wilsy_ai:legal_advisory:generate", "wilsy_ai:legal_advisory:read",
    ]
    assert ROLE_PERMISSIONS_MAP["LEGAL_CLIENT"] == ["legal_operations:invoice:read"]
    assert "legal_operations:return:write" in ROLE_PERMISSIONS_MAP["LEGAL_ATTORNEY"]
    assert "legal_operations:return:write" in ROLE_PERMISSIONS_MAP["LEGAL_PARALEGAL"]
    assert "legal_operations:return:write" in ROLE_PERMISSIONS_MAP["LEGAL_SECRETARY"]
    assert "legal_operations:directory:write" in ROLE_PERMISSIONS_MAP["SHERIFF"]
    assert "legal_operations:receipt:write" in ROLE_PERMISSIONS_MAP["SHERIFF"]
    assert "legal_operations:queue:read" in ROLE_PERMISSIONS_MAP["SHERIFF"]
    assert "legal_operations:deputy_queue:read" not in ROLE_PERMISSIONS_MAP["SHERIFF"]
    assert "legal_operations:deputy_queue:read" in ROLE_PERMISSIONS_MAP["DEPUTY"]
    assert "legal_operations:directory:write" not in ROLE_PERMISSIONS_MAP["DEPUTY"]
    assert "legal_operations:receipt:write" not in ROLE_PERMISSIONS_MAP["DEPUTY"]
    assert "legal_operations:queue:read" not in ROLE_PERMISSIONS_MAP["DEPUTY"]
    for role in (
        "LEGAL_PARTNER",
        "LEGAL_ATTORNEY",
        "LEGAL_PARALEGAL",
        "LEGAL_SECRETARY",
        "LEGAL_FINANCE",
        "LEGAL_CLIENT",
        "ENTERPRISE_ADMIN",
        "AUDITOR",
        "SOVEREIGN_ARCHITECT",
        "SERVICE_WORKER",
    ):
        assert "legal_operations:directory:write" not in ROLE_PERMISSIONS_MAP[role]
        assert "legal_operations:receipt:write" not in ROLE_PERMISSIONS_MAP[role]
        assert "legal_operations:queue:read" not in ROLE_PERMISSIONS_MAP[role]
        assert "legal_operations:deputy_queue:read" not in ROLE_PERMISSIONS_MAP[role]
    assert "legal_operations:attempt_outcome:write" in ROLE_PERMISSIONS_MAP["SHERIFF"]
    assert "legal_operations:attempt_outcome:write" in ROLE_PERMISSIONS_MAP["DEPUTY"]
    assert all("financial_execution" not in grants for grants in ROLE_PERMISSIONS_MAP.values())
    assert "wilsy_ai:legal_tool:read" in ROLE_PERMISSIONS_MAP["LEGAL_ATTORNEY"]
    assert "wilsy_ai:legal_tool:read" in ROLE_PERMISSIONS_MAP["LEGAL_PARALEGAL"]
    assert "wilsy_ai:legal_tool:read" in ROLE_PERMISSIONS_MAP["LEGAL_SECRETARY"]
    assert "wilsy_ai:legal_tool:read" in ROLE_PERMISSIONS_MAP["SHERIFF"]
    assert "wilsy_ai:legal_tool:read" in ROLE_PERMISSIONS_MAP["DEPUTY"]
    assert "legal_operations:instruction:read" not in ROLE_PERMISSIONS_MAP["LEGAL_FINANCE"]
    assert "legal_operations:attempt:read" not in ROLE_PERMISSIONS_MAP["LEGAL_FINANCE"]
    assert "legal_operations:return:read" not in ROLE_PERMISSIONS_MAP["LEGAL_FINANCE"]
    assert "legal_operations:billing:read" not in ROLE_PERMISSIONS_MAP["SHERIFF"]
    assert "legal_operations:invoice:read" not in ROLE_PERMISSIONS_MAP["DEPUTY"]
    assert "wilsy_ai:legal_tool:read" not in ROLE_PERMISSIONS_MAP["LEGAL_CLIENT"]
    for role in ("LEGAL_PARTNER", "LEGAL_ATTORNEY", "LEGAL_PARALEGAL", "LEGAL_SECRETARY", "LEGAL_FINANCE", "SHERIFF", "DEPUTY"):
        assert "wilsy_ai:legal_advisory:generate" in ROLE_PERMISSIONS_MAP[role]
        assert "wilsy_ai:legal_advisory:read" in ROLE_PERMISSIONS_MAP[role]
    for role in ("ENTERPRISE_ADMIN", "AUDITOR", "LEGAL_CLIENT", "SOVEREIGN_ARCHITECT", "SERVICE_WORKER"):
        assert "wilsy_ai:legal_advisory:generate" not in ROLE_PERMISSIONS_MAP[role]



def test_permission_expansion_is_explicit_deterministic_and_fail_closed() -> None:
    """Role expansion remains exact, deterministic and non-authoritative."""
    assert get_permissions_for_roles(
        ["ENTERPRISE_ADMIN"]
    ) == sorted(
        ROLE_PERMISSIONS_MAP[
            "ENTERPRISE_ADMIN"
        ]
    )

    assert get_permissions_for_roles(
        ["AUDITOR"]
    ) == sorted(
        ROLE_PERMISSIONS_MAP[
            "AUDITOR"
        ]
    )

    assert get_permissions_for_roles(
        [
            "ENTERPRISE_ADMIN",
            "AUDITOR",
            "ENTERPRISE_ADMIN",
        ]
    ) == sorted(
        set(
            ROLE_PERMISSIONS_MAP[
                "ENTERPRISE_ADMIN"
            ]
        )
        | set(
            ROLE_PERMISSIONS_MAP[
                "AUDITOR"
            ]
        )
    )

    assert get_permissions_for_roles(
        ["UNKNOWN_ROLE"]
    ) == []

    assert get_permissions_for_roles(
        "ENTERPRISE_ADMIN"
    ) == []



@pytest.mark.parametrize(
    ("permission_id", "expected_roles"),
    (
        ("tenant:profile:read", ("AUDITOR", "ENTERPRISE_ADMIN")),
        ("tenant:profile:write", ("ENTERPRISE_ADMIN",)),
        ("tenant:lifecycle:archive", ("ENTERPRISE_ADMIN",)),
        ("tenant:membership:read", ("AUDITOR", "ENTERPRISE_ADMIN")),
        ("tenant:membership:write", ("ENTERPRISE_ADMIN",)),
        ("tenant:role_assignment:read", ("AUDITOR", "ENTERPRISE_ADMIN")),
        ("tenant:role_assignment:write", ("ENTERPRISE_ADMIN",)),
        ("subscription:read", ("AUDITOR", "ENTERPRISE_ADMIN")),
        ("subscription:manage", ("ENTERPRISE_ADMIN",)),
        ("plan:read", ("AUDITOR", "ENTERPRISE_ADMIN")),
        ("plan:manage", ("ENTERPRISE_ADMIN",)),
        ("wilsy_ai:usage_capacity:read", ("AUDITOR", "ENTERPRISE_ADMIN")),
        ("billing_intelligence:evidence:read", ("AUDITOR", "ENTERPRISE_ADMIN")),
        ("legal_operations:directory:write", ("SHERIFF",)),
        ("legal_operations:receipt:write", ("SHERIFF",)),
        ("legal_operations:queue:read", ("SHERIFF",)),
        ("legal_operations:deputy_queue:read", ("DEPUTY",)),
        ("platform_billing:release", ("ENTERPRISE_ADMIN",)),
        ("inbound_collection:authorization:create", ("INBOUND_COLLECTION_AUTHORIZATION_ADMIN",)),
        ("inbound_merchant_configuration:register", ("INBOUND_MERCHANT_CONFIGURATION_ADMIN",)),
        ("inbound_merchant_configuration:lifecycle", ("INBOUND_MERCHANT_CONFIGURATION_ADMIN",)),
        ("inbound_merchant_configuration:security", ("INBOUND_PROVIDER_SECURITY_ADMIN",)),
        ("inbound_merchant_configuration:remediate", ("INBOUND_PROVIDER_SECURITY_ADMIN",)),
        ("inbound_provider_policy:author", ("INBOUND_PROVIDER_POLICY_ADMIN",)),
        ("inbound_provider_policy:activate", ("INBOUND_PROVIDER_POLICY_ACTIVATION_ADMIN",)),
        ("inbound_provider_policy:deactivate", ("INBOUND_PROVIDER_POLICY_ACTIVATION_ADMIN",)),
        ("inbound_provider_policy:emergency_disable", ("INBOUND_PROVIDER_SECURITY_ADMIN",)),
        ("inbound_provider_credential_security:eligibility_issue", ("INBOUND_PROVIDER_SECURITY_ADMIN",)),
        ("inbound_provider_credential_security:revoke", ("INBOUND_PROVIDER_SECURITY_ADMIN",)),
        ("inbound_provider_credential_security:compromise", ("INBOUND_PROVIDER_SECURITY_ADMIN",)),
        ("inbound_provider_credential_security:rotate", ("INBOUND_PROVIDER_SECURITY_ADMIN",)),
    ),
)
def test_tenant_permission_reverse_lookup_is_exact(
    permission_id: str,
    expected_roles: tuple[str, ...],
) -> None:
    """Every tenant commercial permission resolves to its exact approved grants."""
    assert (
        get_roles_granting_permission(
            permission_id
        )
        == expected_roles
    )



@pytest.mark.parametrize(
    "permission_id",
    (
        "admin:all",
        "execution:trigger",
        "tenant:manage",
        "tenant:delete",
        "tenant:*",
        "tenant:all",
        "tenant",
        "admin",
        "unknown:permission",
        "",
        " ",
        "tenant:profile",
        "tenant:profile:read ",
        " tenant:profile:read",
        "subscription:*",
        "subscription",
        "plan:*",
        "plan:all",
        "plan",
        "PLAN:READ",
        " plan:read",
        "plan:read ",
        "wilsy_ai:*",
        "wilsy_ai:usage_capacity:*",
        "WILSY_AI:USAGE_CAPACITY:READ",
        " wilsy_ai:usage_capacity:read",
        "wilsy_ai:usage_capacity:read ",
        "wilsy_ai:usage_capacity:READ",
        "billing_intelligence:*",
        "billing_intelligence:evidence:*",
        "BILLING_INTELLIGENCE:EVIDENCE:READ",
        " billing_intelligence:evidence:read",
        "billing_intelligence:evidence:read ",
        "billing_intelligence:evidence:READ",
        "billing_intelligence:evidence",
    ),
)
def test_forbidden_unknown_partial_and_wildcard_like_permissions_never_grant(
    permission_id: str,
) -> None:
    """Malformed, wildcard-like and unknown values never manufacture grants."""
    assert (
        get_roles_granting_permission(
            permission_id
        )
        == ()
    )



def test_sovereign_architect_and_service_worker_are_not_tenant_bypasses() -> None:
    """The grant migration does not turn system/service roles into tenant authority."""

    sovereign = set(get_permissions_for_roles(["SOVEREIGN_ARCHITECT"]))
    service = set(get_permissions_for_roles(["SERVICE_WORKER"]))
    assert sovereign.isdisjoint(TENANT_PERMISSIONS)
    assert service.isdisjoint(TENANT_PERMISSIONS)
    assert get_permissions_for_roles(["SERVICE_WORKER"]) == [
        "artifacts:write",
        "events:publish",
    ]


def test_wilsy_ai_capacity_read_is_granted_only_to_approved_roles() -> None:
    """The capacity evidence read remains narrowly role-granted."""
    permission = "wilsy_ai:usage_capacity:read"
    assert get_roles_granting_permission(permission) == (
        "AUDITOR",
        "ENTERPRISE_ADMIN",
    )
    for role in ROLE_PERMISSIONS_MAP:
        if role not in {"AUDITOR", "ENTERPRISE_ADMIN"}:
            assert permission not in ROLE_PERMISSIONS_MAP[role]


def test_c1c_legal_services_permission_is_granted_only_to_intended_roles() -> None:
    """C1C entry permission is explicit and does not replace tool IAM."""
    permission = "wilsy_ai:legal_services:execute"
    intended = {"LEGAL_PARTNER", "LEGAL_ATTORNEY", "LEGAL_PARALEGAL", "LEGAL_SECRETARY", "LEGAL_FINANCE", "SHERIFF", "DEPUTY", "ENTERPRISE_ADMIN"}
    assert set(get_roles_granting_permission(permission)) == intended
    for role, grants in ROLE_PERMISSIONS_MAP.items():
        if role not in intended:
            assert permission not in grants


def test_billing_intelligence_evidence_read_is_granted_only_to_approved_roles() -> None:
    """Billing-intelligence evidence read is limited to two static roles."""
    permission = "billing_intelligence:evidence:read"
    assert get_roles_granting_permission(permission) == (
        "AUDITOR",
        "ENTERPRISE_ADMIN",
    )
    assert ROLE_PERMISSIONS_MAP["ENTERPRISE_ADMIN"].count(permission) == 1
    assert ROLE_PERMISSIONS_MAP["AUDITOR"].count(permission) == 1
    for role in ROLE_PERMISSIONS_MAP:
        if role not in {"AUDITOR", "ENTERPRISE_ADMIN"}:
            assert permission not in ROLE_PERMISSIONS_MAP[role]


def test_no_role_has_implicit_wildcard_or_financial_grant() -> None:
    """All role grants remain explicit exact strings and non-financial."""

    for permissions in ROLE_PERMISSIONS_MAP.values():
        assert all("*" not in permission for permission in permissions)
        assert all("financial" not in permission for permission in permissions)
        assert "admin:all" not in permissions
        assert "execution:trigger" not in permissions
        assert "tenant:manage" not in permissions


def test_inbound_collection_role_is_least_privilege() -> None:
    """The dedicated role grants only the provider-neutral request privilege."""
    assert ROLE_PERMISSIONS_MAP["INBOUND_COLLECTION_AUTHORIZATION_ADMIN"] == [
        "inbound_collection:authorization:create",
    ]
    assert get_permissions_for_roles(["INBOUND_COLLECTION_AUTHORIZATION_ADMIN"]) == [
        "inbound_collection:authorization:create",
    ]
    assert "financial_execution" not in " ".join(ROLE_PERMISSIONS_MAP["INBOUND_COLLECTION_AUTHORIZATION_ADMIN"])
    assert "platform_billing:provider_policy:admin" not in ROLE_PERMISSIONS_MAP["INBOUND_COLLECTION_AUTHORIZATION_ADMIN"]
    assert "platform_billing:release" not in ROLE_PERMISSIONS_MAP["INBOUND_COLLECTION_AUTHORIZATION_ADMIN"]
    assert "accounts_payable:provider_policy:admin" not in ROLE_PERMISSIONS_MAP["INBOUND_COLLECTION_AUTHORIZATION_ADMIN"]


def test_inbound_provider_roles_are_narrow_and_separated() -> None:
    assert ROLE_PERMISSIONS_MAP["INBOUND_MERCHANT_CONFIGURATION_ADMIN"] == [
        "inbound_merchant_configuration:register",
        "inbound_merchant_configuration:lifecycle",
    ]
    assert ROLE_PERMISSIONS_MAP["INBOUND_PROVIDER_SECURITY_ADMIN"] == [
        "inbound_merchant_configuration:security",
        "inbound_merchant_configuration:remediate",
        "inbound_provider_policy:emergency_disable",
        "inbound_provider_credential_security:eligibility_issue",
        "inbound_provider_credential_security:revoke",
        "inbound_provider_credential_security:compromise",
        "inbound_provider_credential_security:rotate",
    ]
    assert "inbound_merchant_configuration:register" not in ROLE_PERMISSIONS_MAP["INBOUND_PROVIDER_SECURITY_ADMIN"]
    assert "inbound_merchant_configuration:lifecycle" not in ROLE_PERMISSIONS_MAP["INBOUND_PROVIDER_SECURITY_ADMIN"]
    assert "inbound_provider_policy:author" not in ROLE_PERMISSIONS_MAP["INBOUND_PROVIDER_SECURITY_ADMIN"]
    assert "inbound_provider_policy:activate" not in ROLE_PERMISSIONS_MAP["INBOUND_PROVIDER_SECURITY_ADMIN"]
    assert "secret" not in " ".join(ROLE_PERMISSIONS_MAP["INBOUND_PROVIDER_SECURITY_ADMIN"])
    assert "kms" not in " ".join(ROLE_PERMISSIONS_MAP["INBOUND_PROVIDER_SECURITY_ADMIN"])
    assert ROLE_PERMISSIONS_MAP["INBOUND_PROVIDER_POLICY_ADMIN"] == [
        "inbound_provider_policy:author",
    ]
    assert ROLE_PERMISSIONS_MAP["INBOUND_PROVIDER_POLICY_ACTIVATION_ADMIN"] == [
        "inbound_provider_policy:activate",
        "inbound_provider_policy:deactivate",
    ]
    assert "inbound_provider_policy:activate" not in ROLE_PERMISSIONS_MAP["INBOUND_PROVIDER_POLICY_ADMIN"]
    assert "inbound_provider_policy:emergency_disable" not in ROLE_PERMISSIONS_MAP["INBOUND_PROVIDER_POLICY_ACTIVATION_ADMIN"]


def test_credential_security_grants_are_exactly_security_admin_only() -> None:
    credential_permissions = {
        "inbound_provider_credential_security:eligibility_issue",
        "inbound_provider_credential_security:revoke",
        "inbound_provider_credential_security:compromise",
        "inbound_provider_credential_security:rotate",
    }
    assert set(ROLE_PERMISSIONS_MAP["INBOUND_PROVIDER_SECURITY_ADMIN"]) & credential_permissions == credential_permissions
    for role in (
        "INBOUND_MERCHANT_CONFIGURATION_ADMIN",
        "INBOUND_PROVIDER_POLICY_ADMIN",
        "INBOUND_PROVIDER_POLICY_ACTIVATION_ADMIN",
        "ENTERPRISE_ADMIN",
        "AUDITOR",
    ):
        assert not credential_permissions.intersection(ROLE_PERMISSIONS_MAP[role])


# ARTIFACT: test_roles.py
# VERSION: v1.17.0-L8-6C-DEPUTY-PERSONAL-QUEUE-IAM-GRANTS-CERT
# AUTHORITY BOUNDARY: deterministic unit verification of explicit role-definition policy only
# TENANT POSTURE: directory and other role definitions remain policy; current tenant-scoped possession requires governed RoleAssignmentAuthority
# FAIL-CLOSED POSTURE: unknown, malformed, implicit, wildcard, legacy, and ambiguous inputs never manufacture grants
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT