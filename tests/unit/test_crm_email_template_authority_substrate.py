"""Test-first certificate for WILSY OS CRM Email Template authority substrate.

TITLE: WILSY OS CRM Email Template Canonical Authority Substrate Certificate
VERSION: v1.0.0-CRM-EMAIL-TEMPLATE-AUTHORITY-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE:
    Freeze canonical tenant authorization vocabulary required before any
    CRM Email Template application service may create, read, revise, archive,
    copy, or widen template sharing.

NEW AUTHORITY:
    crm_email_template_create  -> crm:email_template:create
    crm_email_template_read    -> crm:email_template:read
    crm_email_template_revise  -> crm:email_template:revise
    crm_email_template_archive -> crm:email_template:archive
    crm_email_template_copy    -> crm:email_template:copy
    crm_email_template_share   -> crm:email_template:share

DERIVED AUTHORITY:
    Listing templates consumes read authority.
    Changing template scope consumes share authority.
    No independent list or generic manage permission exists.

BOUNDARIES:
    Permission, business-role eligibility, current assignment, tenant
    membership, record scope, relationship scope, sensitivity policy,
    entitlement, and durable CRM truth remain separate conjuncts.
    No permission authorizes by itself.
    No template authority grants send, mailbox, consent/suppression,
    sequence execution, AI autonomous send, cross-tenant, or financial
    execution capability.
"""

from __future__ import annotations

import pytest

from tools.eos.auth.crm_sales_business_role_catalog import (
    ALL_CRM_SALES_BUSINESS_ROLES,
)
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


CREATE_OPERATION = "crm_email_template_create"
READ_OPERATION = "crm_email_template_read"
REVISE_OPERATION = "crm_email_template_revise"
ARCHIVE_OPERATION = "crm_email_template_archive"
COPY_OPERATION = "crm_email_template_copy"
SHARE_OPERATION = "crm_email_template_share"

CREATE_PERMISSION = "crm:email_template:create"
READ_PERMISSION = "crm:email_template:read"
REVISE_PERMISSION = "crm:email_template:revise"
ARCHIVE_PERMISSION = "crm:email_template:archive"
COPY_PERMISSION = "crm:email_template:copy"
SHARE_PERMISSION = "crm:email_template:share"

OPERATION_PERMISSION_PAIRS = (
    (CREATE_OPERATION, CREATE_PERMISSION),
    (READ_OPERATION, READ_PERMISSION),
    (REVISE_OPERATION, REVISE_PERMISSION),
    (ARCHIVE_OPERATION, ARCHIVE_PERMISSION),
    (COPY_OPERATION, COPY_PERMISSION),
    (SHARE_OPERATION, SHARE_PERMISSION),
)

ALL_PERMISSIONS = tuple(
    permission
    for _, permission in OPERATION_PERMISSION_PAIRS
)

MUTATION_OPERATIONS = (
    CREATE_OPERATION,
    REVISE_OPERATION,
    ARCHIVE_OPERATION,
    COPY_OPERATION,
    SHARE_OPERATION,
)

MUTATION_PERMISSIONS = (
    CREATE_PERMISSION,
    REVISE_PERMISSION,
    ARCHIVE_PERMISSION,
    COPY_PERMISSION,
    SHARE_PERMISSION,
)


def test_template_permissions_are_canonical_tenant_nonfinancial_authority() -> None:
    for permission_id in ALL_PERMISSIONS:
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


def test_template_permissions_have_explicit_business_capabilities() -> None:
    expected = {
        CREATE_PERMISSION: "create CRM email templates",
        READ_PERMISSION: "read CRM email templates",
        REVISE_PERMISSION: "revise CRM email template metadata",
        ARCHIVE_PERMISSION: "archive CRM email templates",
        COPY_PERMISSION: "copy CRM email templates",
        SHARE_PERMISSION: "share CRM email templates",
    }

    for permission_id, capability in expected.items():
        assert (
            permission_metadata(permission_id).business_capability
            == capability
        )


def test_template_authorization_role_grants_are_closed_and_exact() -> None:
    for permission_id in ALL_PERMISSIONS:
        if permission_id == READ_PERMISSION:
            assert get_roles_granting_permission(permission_id) == (
                "AUDITOR",
                "ENTERPRISE_ADMIN",
            )
        else:
            assert get_roles_granting_permission(permission_id) == (
                "ENTERPRISE_ADMIN",
            )

    for permission_id in ALL_PERMISSIONS:
        assert (
            ROLE_PERMISSIONS_MAP["ENTERPRISE_ADMIN"].count(
                permission_id
            )
            == 1
        )

    assert (
        ROLE_PERMISSIONS_MAP["AUDITOR"].count(
            READ_PERMISSION
        )
        == 1
    )

    for permission_id in MUTATION_PERMISSIONS:
        assert permission_id not in ROLE_PERMISSIONS_MAP["AUDITOR"]

    for role_id, grants in ROLE_PERMISSIONS_MAP.items():
        if role_id != "ENTERPRISE_ADMIN":
            for permission_id in MUTATION_PERMISSIONS:
                assert permission_id not in grants

        if role_id not in {"AUDITOR", "ENTERPRISE_ADMIN"}:
            assert READ_PERMISSION not in grants


def test_template_operation_permission_bindings_are_exact() -> None:
    for operation, permission in OPERATION_PERMISSION_PAIRS:
        assert operation in OPERATIONS
        assert (
            permission_for_business_role_operation(operation)
            == permission
        )


@pytest.mark.parametrize(
    ("role", "operation", "expected"),
    [
        ("tenant_owner", CREATE_OPERATION, ELIGIBLE),
        ("tenant_owner", READ_OPERATION, ELIGIBLE),
        ("tenant_owner", REVISE_OPERATION, ELIGIBLE),
        ("tenant_owner", ARCHIVE_OPERATION, ELIGIBLE),
        ("tenant_owner", COPY_OPERATION, ELIGIBLE),
        ("tenant_owner", SHARE_OPERATION, ELIGIBLE),
        ("tenant_admin", CREATE_OPERATION, ELIGIBLE),
        ("tenant_admin", READ_OPERATION, ELIGIBLE),
        ("tenant_admin", REVISE_OPERATION, ELIGIBLE),
        ("tenant_admin", ARCHIVE_OPERATION, ELIGIBLE),
        ("tenant_admin", COPY_OPERATION, ELIGIBLE),
        ("tenant_admin", SHARE_OPERATION, ELIGIBLE),
        ("tenant_manager", CREATE_OPERATION, ELIGIBLE),
        ("tenant_manager", READ_OPERATION, ELIGIBLE),
        ("tenant_manager", REVISE_OPERATION, ELIGIBLE),
        ("tenant_manager", ARCHIVE_OPERATION, ELIGIBLE),
        ("tenant_manager", COPY_OPERATION, ELIGIBLE),
        ("tenant_manager", SHARE_OPERATION, ELIGIBLE),
        ("tenant_auditor", CREATE_OPERATION, DENY),
        ("tenant_auditor", READ_OPERATION, ELIGIBLE),
        ("tenant_auditor", REVISE_OPERATION, DENY),
        ("tenant_auditor", ARCHIVE_OPERATION, DENY),
        ("tenant_auditor", COPY_OPERATION, DENY),
        ("tenant_auditor", SHARE_OPERATION, DENY),
    ],
)
def test_generic_tenant_business_role_eligibility_is_exact(
    role: str,
    operation: str,
    expected: str,
) -> None:
    assert (
        tenant_role_operation_eligibility(
            role,
            operation,
        )
        == expected
    )


@pytest.mark.parametrize(
    "role",
    sorted(ALL_CRM_SALES_BUSINESS_ROLES),
)
def test_crm_sales_business_role_names_do_not_self_authorize(
    role: str,
) -> None:
    for operation, _ in OPERATION_PERMISSION_PAIRS:
        assert (
            tenant_role_operation_eligibility(
                role,
                operation,
            )
            == DENY
        )


def test_listing_uses_read_authority_and_has_no_independent_permission() -> None:
    assert "crm_email_template_list" not in OPERATIONS

    assert (
        permission_for_business_role_operation(
            "crm_email_template_list"
        )
        is None
    )

    with pytest.raises(ValueError):
        permission_metadata(
            "crm:email_template:list"
        )


def test_scope_change_uses_distinct_share_authority() -> None:
    assert SHARE_OPERATION != REVISE_OPERATION
    assert SHARE_PERMISSION != REVISE_PERMISSION

    assert (
        permission_for_business_role_operation(
            SHARE_OPERATION
        )
        == SHARE_PERMISSION
    )

    assert (
        permission_for_business_role_operation(
            REVISE_OPERATION
        )
        == REVISE_PERMISSION
    )

    assert (
        permission_for_business_role_operation(
            SHARE_OPERATION
        )
        != REVISE_PERMISSION
    )


@pytest.mark.parametrize(
    "operation",
    [
        "",
        " ",
        "crm_email_template_create ",
        " crm_email_template_create",
        "crm_email_template_read ",
        " crm_email_template_read",
        "crm_email_template_revise ",
        "crm_email_template_archive ",
        "crm_email_template_copy ",
        "crm_email_template_share ",
        "CRM_EMAIL_TEMPLATE_CREATE",
        "CRM_EMAIL_TEMPLATE_READ",
        "crm_email_template_manage",
        "crm_email_template_send",
        "financial_execution",
        "cross_tenant",
    ],
)
def test_malformed_or_unowned_template_operations_fail_closed(
    operation: str,
) -> None:
    assert (
        tenant_role_operation_eligibility(
            "tenant_owner",
            operation,
        )
        == DENY
    )

    if operation not in {
        "financial_execution",
        "cross_tenant",
    }:
        assert (
            permission_for_business_role_operation(
                operation
            )
            is None
        )


@pytest.mark.parametrize(
    "permission_id",
    [
        "crm:*",
        "crm:email_template:*",
        "crm:email_template:manage",
        "crm:email_template:send",
        "crm:email_template:create ",
        " crm:email_template:create",
        "crm:email_template:read ",
        " crm:email_template:read",
        "crm:email_template:revise ",
        "crm:email_template:archive ",
        "crm:email_template:copy ",
        "crm:email_template:share ",
    ],
)
def test_wildcard_or_malformed_template_permissions_are_not_canonical(
    permission_id: str,
) -> None:
    with pytest.raises(ValueError):
        permission_metadata(permission_id)

    assert get_roles_granting_permission(permission_id) == ()


def test_template_authority_does_not_create_send_or_financial_grants() -> None:
    forbidden_permissions = {
        "crm:email_template:send",
        "crm:mailbox:use",
        "crm:consent:manage",
        "crm:sequence:execute",
        "financial_execution",
    }

    for grants in ROLE_PERMISSIONS_MAP.values():
        assert forbidden_permissions.isdisjoint(grants)

    assert (
        tenant_role_operation_eligibility(
            "tenant_owner",
            "financial_execution",
        )
        == DENY
    )


# =============================================================================
# WILSY OS SOVEREIGN TEST ARTIFACT SEAL
# ARTIFACT: test_crm_email_template_authority_substrate.py
# VERSION: v1.0.0-CRM-EMAIL-TEMPLATE-AUTHORITY-CERT
# AUTHORITY BOUNDARY: CRM Email Template tenant authorization substrate only
# TENANT POSTURE: exact own-tenant canonical permission and business-role policy
# RECORD POSTURE: record/relationship/sensitivity checks remain application-layer conjuncts
# COMMERCIAL POSTURE: tenant entitlement remains separate and is not certified here
# SEND / MAILBOX / CONSENT / SEQUENCE AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
# =============================================================================
