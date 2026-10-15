"""
WILSY OS — Legal Workflow IAM authority substrate certificate.

TITLE: Legal Workflow IAM Authority Substrate
VERSION: v1.0.0-G7G-P0F-LEGAL-WORKFLOW-IAM-AUTHORITY
DATE: 2026-10-15

PURPOSE:
    Freeze the exact permission, operation, business-eligibility, and static
    authorization-role contract required by the first governed Legal workflow
    command plane.

AUTHORITY BOUNDARY:
    Business-role eligibility is non-authorizing. A command proceeds only when
    exact own-tenant ACTIVE membership, exact business eligibility, exact
    static authorization-role assignment, and exact permission binding all
    succeed. Operating-role metadata grants no IAM authority.

FINANCIAL BOUNDARY:
    This certificate grants no billing, payment, release, settlement,
    subscription, or Kennel EOS execution authority.

ASSIGNMENT / SUPERVISION BOUNDARY:
    This certificate creates no work assignment or supervision authority.

NO EVIDENCE = NO FACT.
"""

from __future__ import annotations

import pytest

from tools.eos.auth.permission_namespace import (
    permission_metadata,
)
from tools.eos.auth.roles import (
    ROLE_PERMISSIONS_MAP,
    get_roles_granting_permission,
)
from tools.eos.auth.tenant_authority_policy import (
    DENY,
    ELIGIBLE,
    permission_for_business_role_operation,
    tenant_role_operation_eligibility,
)


CONTRACT = {
    "activation_manage": {
        "operation": "legal_workflow_activation_manage",
        "permission": "legal_operations:workflow_activation:manage",
        "business_roles": {"tenant_admin"},
        "authorization_roles": {"ENTERPRISE_ADMIN"},
    },
    "matter_read": {
        "operation": "legal_matter_workflow_read",
        "permission": "legal_operations:matter_workflow:read",
        "business_roles": {
            "tenant_legal_partner",
            "tenant_legal_attorney",
            "tenant_legal_paralegal",
            "tenant_legal_secretary",
        },
        "authorization_roles": {
            "LEGAL_PARTNER",
            "LEGAL_ATTORNEY",
            "LEGAL_PARALEGAL",
            "LEGAL_SECRETARY",
        },
    },
    "matter_instantiate": {
        "operation": "legal_matter_workflow_instantiate",
        "permission": "legal_operations:matter_workflow:instantiate",
        "business_roles": {
            "tenant_legal_partner",
            "tenant_legal_attorney",
        },
        "authorization_roles": {
            "LEGAL_PARTNER",
            "LEGAL_ATTORNEY",
        },
    },
    "matter_transition": {
        "operation": "legal_matter_workflow_transition",
        "permission": "legal_operations:matter_workflow:transition",
        "business_roles": {
            "tenant_legal_partner",
            "tenant_legal_attorney",
        },
        "authorization_roles": {
            "LEGAL_PARTNER",
            "LEGAL_ATTORNEY",
        },
    },
    "work_item_read": {
        "operation": "legal_work_item_read",
        "permission": "legal_operations:work_item:read",
        "business_roles": {
            "tenant_legal_partner",
            "tenant_legal_attorney",
            "tenant_legal_paralegal",
            "tenant_legal_secretary",
        },
        "authorization_roles": {
            "LEGAL_PARTNER",
            "LEGAL_ATTORNEY",
            "LEGAL_PARALEGAL",
            "LEGAL_SECRETARY",
        },
    },
    "work_item_write": {
        "operation": "legal_work_item_write",
        "permission": "legal_operations:work_item:write",
        "business_roles": {
            "tenant_legal_partner",
            "tenant_legal_attorney",
        },
        "authorization_roles": {
            "LEGAL_PARTNER",
            "LEGAL_ATTORNEY",
        },
    },
}


ALL_TENANT_ROLES = {
    "tenant_owner",
    "tenant_admin",
    "tenant_manager",
    "tenant_auditor",
    "tenant_legal_partner",
    "tenant_legal_attorney",
    "tenant_legal_paralegal",
    "tenant_legal_secretary",
    "tenant_legal_finance",
    "tenant_sheriff",
    "tenant_deputy",
    "tenant_legal_client",
}


def test_exact_operation_permission_bindings() -> None:
    for spec in CONTRACT.values():
        assert (
            permission_for_business_role_operation(
                spec["operation"]
            )
            == spec["permission"]
        )


def test_exact_business_role_eligibility() -> None:
    for spec in CONTRACT.values():
        eligible = {
            role
            for role in ALL_TENANT_ROLES
            if tenant_role_operation_eligibility(
                role,
                spec["operation"],
            )
            == ELIGIBLE
        }
        assert eligible == spec["business_roles"]

        for role in ALL_TENANT_ROLES - spec["business_roles"]:
            assert (
                tenant_role_operation_eligibility(
                    role,
                    spec["operation"],
                )
                == DENY
            )


def test_exact_static_authorization_role_grants() -> None:
    for spec in CONTRACT.values():
        assert (
            set(
                get_roles_granting_permission(
                    spec["permission"]
                )
            )
            == spec["authorization_roles"]
        )

        for role, permissions in ROLE_PERMISSIONS_MAP.items():
            count = permissions.count(spec["permission"])
            if role in spec["authorization_roles"]:
                assert count == 1
            else:
                assert count == 0


def test_permissions_exist_as_exact_namespace_entries() -> None:
    for spec in CONTRACT.values():
        metadata = permission_metadata(
            spec["permission"]
        )
        assert metadata is not None


@pytest.mark.parametrize(
    ("operation", "permission"),
    [
        (
            "legal_workflow_activation_manage ",
            "legal_operations:workflow_activation:manage",
        ),
        (
            " legal_matter_workflow_read",
            "legal_operations:matter_workflow:read",
        ),
        (
            "legal_matter_workflow_*",
            "legal_operations:matter_workflow:transition",
        ),
        (
            "legal_work_item",
            "legal_operations:work_item:read",
        ),
        (
            "legal_work_item_write*",
            "legal_operations:work_item:write",
        ),
    ],
)
def test_alias_wildcard_and_whitespace_operations_fail_closed(
    operation: str,
    permission: str,
) -> None:
    assert (
        permission_for_business_role_operation(operation)
        != permission
    )


def test_tom_permission_does_not_substitute_for_workflow_authority() -> None:
    tom = "legal_operations:operating_model:manage"

    for spec in CONTRACT.values():
        assert spec["permission"] != tom


def test_business_role_eligibility_remains_non_authorizing_metadata() -> None:
    # This test deliberately certifies only the policy half.
    # Tenant authorization still requires ACTIVE membership,
    # authorization-role assignment, and exact permission binding.
    for spec in CONTRACT.values():
        assert spec["business_roles"]
        assert spec["authorization_roles"]


# ARTIFACT: test_legal_workflow_iam_authority_substrate.py
# VERSION: v1.0.0-G7G-P0F-LEGAL-WORKFLOW-IAM-AUTHORITY
# IAM AUTHORITY: exact permission + operation + business eligibility +
# static authorization-role conjunction only
# OPERATING ROLE AUTHORITY: NONE
# ASSIGNMENT AUTHORITY: NONE
# SUPERVISION AUTHORITY: NONE
# FINANCIAL AUTHORITY: NONE
# END OF WILSY OS LEGAL WORKFLOW IAM AUTHORITY SUBSTRATE CERTIFICATE
