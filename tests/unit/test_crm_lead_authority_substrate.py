"""Test-first certificate for canonical WILSY OS CRM Lead authority substrate.

TITLE: WILSY OS CRM Lead Canonical Authority Substrate Certificate
VERSION: v1.0.0-CRM-P9B-LEAD-AUTHORITY-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE:
    Freeze the new canonical tenant authorization substrate required before
    CrmLeadCommandService may execute create or read commands.

NEW AUTHORITY:
    crm_lead_create -> crm:lead:create
    crm_lead_read   -> crm:lead:read

BUSINESS-ROLE ELIGIBILITY:
    tenant_owner   -> create + read
    tenant_admin   -> create + read
    tenant_manager -> create + read
    tenant_auditor -> read only

AUTHORIZATION-ROLE GRANTS:
    crm:lead:create -> ENTERPRISE_ADMIN
    crm:lead:read   -> AUDITOR + ENTERPRISE_ADMIN

BOUNDARIES:
    Permission, business-role eligibility, subscription entitlement and durable
    CRM truth remain separate authorities. No permission authorizes by itself.
    No CRM Lead authority grants cross-tenant or financial execution capability.
"""

from __future__ import annotations

import pytest

from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    permission_metadata,
)
from tools.eos.auth.roles import (
    ROLE_PERMISSIONS_MAP,
    get_roles_granting_permission,
)
from tools.eos.auth.tenant_authority_policy import (
    DENY,
    ELIGIBLE,
    OPERATIONS,
    permission_for_business_role_operation,
    tenant_role_operation_eligibility,
)


CREATE_OPERATION = "crm_lead_create"
READ_OPERATION = "crm_lead_read"

CREATE_PERMISSION = "crm:lead:create"
READ_PERMISSION = "crm:lead:read"


def test_crm_lead_permissions_are_canonical_tenant_nonfinancial_authority() -> None:
    for permission_id in (CREATE_PERMISSION, READ_PERMISSION):
        metadata = permission_metadata(permission_id)

        assert metadata.permission_id == permission_id
        assert metadata.namespace == "TENANT"
        assert metadata.scope_kind == "TENANT"
        assert metadata.tenant_membership_required is True
        assert metadata.system_assignment_required is False
        assert metadata.cross_tenant_capable is False
        assert metadata.financial_execution_capable is False
        assert metadata.authorizes_by_itself is False
        assert metadata.disposition is PermissionDisposition.CANONICAL


def test_crm_lead_permissions_have_explicit_business_capabilities() -> None:
    create_metadata = permission_metadata(CREATE_PERMISSION)
    read_metadata = permission_metadata(READ_PERMISSION)

    assert create_metadata.business_capability == "create CRM leads"
    assert read_metadata.business_capability == "read CRM leads"


def test_crm_lead_authorization_role_grants_follow_existing_tenant_precedent() -> None:
    assert get_roles_granting_permission(CREATE_PERMISSION) == (
        "ENTERPRISE_ADMIN",
    )

    assert get_roles_granting_permission(READ_PERMISSION) == (
        "AUDITOR",
        "ENTERPRISE_ADMIN",
    )

    assert ROLE_PERMISSIONS_MAP["ENTERPRISE_ADMIN"].count(
        CREATE_PERMISSION
    ) == 1
    assert ROLE_PERMISSIONS_MAP["ENTERPRISE_ADMIN"].count(
        READ_PERMISSION
    ) == 1
    assert ROLE_PERMISSIONS_MAP["AUDITOR"].count(READ_PERMISSION) == 1

    for role_id, grants in ROLE_PERMISSIONS_MAP.items():
        if role_id != "ENTERPRISE_ADMIN":
            assert CREATE_PERMISSION not in grants

        if role_id not in {"AUDITOR", "ENTERPRISE_ADMIN"}:
            assert READ_PERMISSION not in grants


def test_crm_lead_operations_are_closed_canonical_policy_vocabulary() -> None:
    assert CREATE_OPERATION in OPERATIONS
    assert READ_OPERATION in OPERATIONS

    assert (
        permission_for_business_role_operation(CREATE_OPERATION)
        == CREATE_PERMISSION
    )
    assert (
        permission_for_business_role_operation(READ_OPERATION)
        == READ_PERMISSION
    )


@pytest.mark.parametrize(
    ("role", "operation", "expected"),
    [
        ("tenant_owner", CREATE_OPERATION, ELIGIBLE),
        ("tenant_owner", READ_OPERATION, ELIGIBLE),
        ("tenant_admin", CREATE_OPERATION, ELIGIBLE),
        ("tenant_admin", READ_OPERATION, ELIGIBLE),
        ("tenant_manager", CREATE_OPERATION, ELIGIBLE),
        ("tenant_manager", READ_OPERATION, ELIGIBLE),
        ("tenant_auditor", CREATE_OPERATION, DENY),
        ("tenant_auditor", READ_OPERATION, ELIGIBLE),
    ],
)
def test_generic_tenant_business_role_eligibility_is_exact(
    role: str,
    operation: str,
    expected: str,
) -> None:
    assert tenant_role_operation_eligibility(role, operation) == expected


@pytest.mark.parametrize(
    "role",
    [
        "tenant_legal_partner",
        "tenant_legal_attorney",
        "tenant_legal_paralegal",
        "tenant_legal_secretary",
        "tenant_legal_finance",
        "tenant_sheriff",
        "tenant_deputy",
        "tenant_legal_client",
    ],
)
def test_existing_specialized_non_crm_roles_do_not_gain_crm_authority(
    role: str,
) -> None:
    assert tenant_role_operation_eligibility(role, CREATE_OPERATION) == DENY
    assert tenant_role_operation_eligibility(role, READ_OPERATION) == DENY


@pytest.mark.parametrize(
    "operation",
    [
        "",
        " ",
        "crm_lead_create ",
        " crm_lead_create",
        "crm_lead_read ",
        " crm_lead_read",
        "CRM_LEAD_CREATE",
        "CRM_LEAD_READ",
        "crm_lead_write",
        "financial_execution",
        "cross_tenant",
    ],
)
def test_malformed_or_unowned_crm_operations_fail_closed(
    operation: str,
) -> None:
    if operation in {"financial_execution", "cross_tenant"}:
        assert tenant_role_operation_eligibility(
            "tenant_owner",
            operation,
        ) == DENY
    else:
        assert tenant_role_operation_eligibility(
            "tenant_owner",
            operation,
        ) == DENY
        assert permission_for_business_role_operation(operation) is None


@pytest.mark.parametrize(
    "permission_id",
    [
        "crm:*",
        "crm:lead:*",
        "crm:lead:manage",
        "crm:lead:create ",
        " crm:lead:create",
        "crm:lead:read ",
        " crm:lead:read",
    ],
)
def test_wildcard_or_malformed_crm_permissions_are_not_canonical(
    permission_id: str,
) -> None:
    with pytest.raises(ValueError):
        permission_metadata(permission_id)

    assert get_roles_granting_permission(permission_id) == ()


def test_crm_authority_does_not_create_financial_execution_grants() -> None:
    assert "financial_execution" not in ROLE_PERMISSIONS_MAP[
        "ENTERPRISE_ADMIN"
    ]
    assert "financial_execution" not in ROLE_PERMISSIONS_MAP["AUDITOR"]

    assert tenant_role_operation_eligibility(
        "tenant_owner",
        "financial_execution",
    ) == DENY


# =============================================================================
# WILSY OS SOVEREIGN TEST ARTIFACT SEAL
# ARTIFACT: test_crm_lead_authority_substrate.py
# VERSION: v1.0.0-CRM-P9B-LEAD-AUTHORITY-CERT
# AUTHORITY BOUNDARY: CRM Lead create/read authorization substrate only
# TENANT POSTURE: exact own-tenant permission and business-role policy
# COMMERCIAL POSTURE: entitlement remains separate and is not certified here
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
# =============================================================================
