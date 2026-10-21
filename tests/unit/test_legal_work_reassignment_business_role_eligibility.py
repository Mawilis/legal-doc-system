"""
TITLE: WILSY OS P9 Legal Work Reassignment Business Eligibility RED Certificate
VERSION: v1.1.0-P9-R39-REASSIGNMENT-BINDING-TRANSITION
AUTHORITY: Wilsy OS Core Engineering / Python EOS business policy
EPITOME: Freeze exact Partner/Attorney-only reassignment business eligibility.
ABSOLUTE CANONICAL PATH:
    tests/unit/test_legal_work_reassignment_business_role_eligibility.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.1.0-P9-R39-REASSIGNMENT-BINDING-TRANSITION
    transitions the P9-R30 eligibility-only assertion to the exact
    reassignment permission lookup contract. Eligibility, lookup and
    static grants remain non-authorizing without current membership,
    ACTIVE role assignment, exact matter/recipient scope, supervisor
    requirements and separately governed command execution.
    2026-10-19 v1.0.0-P9-R30-REASSIGNMENT-BUSINESS-ELIGIBILITY-RED
    freezes a new own-tenant reassignment operation and all-other-role denial.
COMPLIANCE: Test-first closed-operation and tenant-business-role policy.
SECURITY / PRIVACY POSTURE:
    Business eligibility does not establish identity, membership or permission.
TENANT BOUNDARY: Exact current own-tenant checks remain separately mandatory.
AUTHORITY BOUNDARY:
    No ACTIVE authorization-role possession, assignment, target membership,
    matter scope, operation-permission binding, execution or legal effect.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""

from __future__ import annotations

from tools.eos.auth.tenant_authority_policy import (
    BUSINESS_ROLE_OPERATION_PERMISSIONS,
    DENY,
    ELIGIBLE,
    ELIGIBILITY,
    OPERATIONS,
    TENANT_ROLES,
    tenant_role_operation_eligibility,
)

OPERATION = "legal_work_item_reassign"
ALLOWED_ROLES = frozenset({
    "tenant_legal_partner",
    "tenant_legal_attorney",
})


def test_reassignment_operation_is_recognized_with_exact_business_eligibility() -> None:
    assert OPERATION in OPERATIONS
    assert len(OPERATIONS) == 127
    assert len(TENANT_ROLES) == 119

    eligible = {
        role for role in TENANT_ROLES
        if tenant_role_operation_eligibility(role, OPERATION) == ELIGIBLE
    }
    assert eligible == ALLOWED_ROLES

    for role in TENANT_ROLES:
        assert tenant_role_operation_eligibility(role, OPERATION) == (
            ELIGIBLE if role in ALLOWED_ROLES else DENY
        )


def test_unrelated_roles_and_operation_aliases_remain_denied() -> None:
    assert len(ELIGIBILITY) == 51

    for role in (
        "tenant_legal_paralegal",
        "tenant_legal_secretary",
        "tenant_legal_finance",
        "tenant_legal_client",
        "tenant_owner",
        "tenant_admin",
        "tenant_manager",
        "tenant_auditor",
        "tenant_sheriff",
        "tenant_deputy",
    ):
        assert role in TENANT_ROLES
        assert tenant_role_operation_eligibility(role, OPERATION) == DENY

    for variant in (
        "legal_work_item_reassign ",
        " legal_work_item_reassign",
        "LEGAL_WORK_ITEM_REASSIGN",
        "legal_work_item_*",
        "legal_work_item_reassigned",
        "legal_work_item_complete",
    ):
        if variant == "legal_work_item_complete":
            assert variant != OPERATION
        else:
            assert tenant_role_operation_eligibility(
                "tenant_legal_partner", variant
            ) == DENY


def test_eligibility_binding_is_exact_but_not_execution_authority() -> None:
    assert BUSINESS_ROLE_OPERATION_PERMISSIONS[OPERATION] == (
        "legal_operations:work_item:reassign"
    )
    assert list(BUSINESS_ROLE_OPERATION_PERMISSIONS).count(OPERATION) == 1
    assert "financial_execution" not in BUSINESS_ROLE_OPERATION_PERMISSIONS
    assert "legal_work_item_complete" in OPERATIONS
    assert "legal_work_item_write" in OPERATIONS
    assert tenant_role_operation_eligibility(
        "tenant_legal_paralegal", "legal_work_item_complete"
    ) == ELIGIBLE
    assert tenant_role_operation_eligibility(
        "tenant_legal_secretary", "legal_work_item_complete"
    ) == ELIGIBLE


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_work_reassignment_business_role_eligibility.py
# VERSION: v1.1.0-P9-R39-REASSIGNMENT-BINDING-TRANSITION
# AUTHORITY BOUNDARY: business eligibility only, non-authorizing
# TENANT POSTURE: exact current membership separately required
# FAIL-CLOSED POSTURE: all unauthorized roles and aliases denied
# OPERATION-PERMISSION BINDING AUTHORITY: NONE
# REASSIGNMENT COMMAND AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
