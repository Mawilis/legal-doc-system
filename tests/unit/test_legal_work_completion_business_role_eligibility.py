"""
TITLE:
    WILSY OS P14-R20R13 Legal Work Completion Business-Role
    Eligibility Certificate

VERSION:
    v1.0.0-P14-R20R13-WORK-COMPLETION-BUSINESS-ROLE-ELIGIBILITY

AUTHORITY BOUNDARY:
    Business-role eligibility only. Eligibility is non-authorizing and does not
    establish tenant membership, permission possession, current role assignment,
    work assignment, completion authority, workflow progression, legal-event
    truth, billing, payment, execution or settlement authority.
"""

from __future__ import annotations

import pytest

from tools.eos.auth.tenant_authority_policy import (
    DENY,
    ELIGIBLE,
    OPERATIONS,
    TENANT_ROLES,
    tenant_role_operation_eligibility,
)


OPERATION = "legal_work_item_complete"

EXPECTED = (
    "tenant_legal_attorney",
    "tenant_legal_paralegal",
    "tenant_legal_partner",
    "tenant_legal_secretary",
)


def test_completion_operation_is_canonical_business_operation() -> None:
    assert OPERATION in OPERATIONS


def test_completion_business_role_eligibility_is_exactly_daily_legal_work_roles() -> None:
    eligible = tuple(
        sorted(
            role
            for role in TENANT_ROLES
            if tenant_role_operation_eligibility(
                role,
                OPERATION,
            )
            == ELIGIBLE
        )
    )

    assert eligible == EXPECTED


@pytest.mark.parametrize(
    "role",
    EXPECTED,
)
def test_each_daily_legal_work_role_is_eligible(
    role: str,
) -> None:
    assert (
        tenant_role_operation_eligibility(
            role,
            OPERATION,
        )
        == ELIGIBLE
    )


@pytest.mark.parametrize(
    "role",
    (
        "tenant_legal_finance",
        "tenant_legal_client",
        "tenant_sheriff",
        "tenant_deputy",
        "tenant_owner",
        "tenant_admin",
        "tenant_manager",
        "tenant_auditor",
    ),
)
def test_unrelated_business_roles_remain_ineligible(
    role: str,
) -> None:
    assert (
        tenant_role_operation_eligibility(
            role,
            OPERATION,
        )
        == DENY
    )


@pytest.mark.parametrize(
    "operation",
    (
        "legal_work_item_complete ",
        " legal_work_item_complete",
        "LEGAL_WORK_ITEM_COMPLETE",
        "legal_work_item_*",
        "legal_work_item_completion",
    ),
)
def test_alias_case_whitespace_and_cross_operation_fail_closed(
    operation: str,
) -> None:
    for role in EXPECTED:
        assert (
            tenant_role_operation_eligibility(
                role,
                operation,
            )
            == DENY
        )


def test_completion_operation_is_distinct_from_generic_work_item_write() -> None:
    assert (
        OPERATION
        != "legal_work_item_write"
    )


def test_eligibility_does_not_expose_completion_execution() -> None:
    import tools.eos.auth.tenant_authority_policy as module

    assert not hasattr(
        module,
        "complete_work"
    )

    assert not hasattr(
        module,
        "authorize_completion"
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_completion_business_role_eligibility.py
# VERSION: v1.0.0-P14-R20R13-WORK-COMPLETION-BUSINESS-ROLE-ELIGIBILITY
# OPERATION: legal_work_item_complete
# ELIGIBLE: PARTNER / ATTORNEY / PARALEGAL / SECRETARY
# PERMISSION POSSESSION AUTHORITY: NONE
# CURRENT ROLE ASSIGNMENT AUTHORITY: NONE
# WORK ASSIGNMENT AUTHORITY: NONE
# COMPLETION COMMAND AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
