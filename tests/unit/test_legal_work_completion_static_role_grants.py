"""
TITLE:
    WILSY OS P14-R20R12 Legal Work Completion Static Authorization-Role
    Grant Certificate

VERSION:
    v1.0.0-P14-R20R12-WORK-COMPLETION-STATIC-GRANTS

AUTHORITY BOUNDARY:
    Static authorization-role permission definitions only. Static possession
    proves neither tenant membership, current role assignment, business-role
    eligibility, work assignment, completion authority nor financial execution.

PRODUCT RULE:
    Partner, Attorney, Paralegal and Secretary may statically possess the exact
    completion permission. Exact completion still requires separately certified
    IAM and exact historical work assignment to the acting principal.
"""

from __future__ import annotations

import pytest

from tools.eos.auth.roles import (
    ROLE_PERMISSIONS_MAP,
    get_roles_granting_permission,
)


PERMISSION = "legal_operations:work_item:complete"

EXPECTED = (
    "LEGAL_ATTORNEY",
    "LEGAL_PARALEGAL",
    "LEGAL_PARTNER",
    "LEGAL_SECRETARY",
)


def test_completion_permission_grant_set_is_exact() -> None:
    assert (
        get_roles_granting_permission(
            PERMISSION
        )
        == EXPECTED
    )


@pytest.mark.parametrize(
    "role",
    EXPECTED,
)
def test_each_daily_legal_work_role_contains_permission_once(
    role: str,
) -> None:
    grants = ROLE_PERMISSIONS_MAP[
        role
    ]

    assert grants.count(
        PERMISSION
    ) == 1


@pytest.mark.parametrize(
    "role",
    (
        "LEGAL_FINANCE",
        "LEGAL_CLIENT",
        "SHERIFF",
        "DEPUTY",
        "AUDITOR",
        "ENTERPRISE_ADMIN",
    ),
)
def test_unrelated_or_nonproductive_roles_do_not_gain_completion(
    role: str,
) -> None:
    assert (
        PERMISSION
        not in ROLE_PERMISSIONS_MAP[
            role
        ]
    )


def test_completion_is_distinct_from_generic_work_item_write() -> None:
    assert (
        PERMISSION
        != "legal_operations:work_item:write"
    )

    assert (
        "legal_operations:work_item:write"
        not in ROLE_PERMISSIONS_MAP[
            "LEGAL_PARALEGAL"
        ]
    )

    assert (
        "legal_operations:work_item:write"
        not in ROLE_PERMISSIONS_MAP[
            "LEGAL_SECRETARY"
        ]
    )

    assert (
        PERMISSION
        in ROLE_PERMISSIONS_MAP[
            "LEGAL_PARALEGAL"
        ]
    )

    assert (
        PERMISSION
        in ROLE_PERMISSIONS_MAP[
            "LEGAL_SECRETARY"
        ]
    )


def test_static_grant_layer_has_no_assignment_or_completion_execution_surface() -> None:
    import tools.eos.auth.roles as module

    assert not hasattr(
        module,
        "assign_work"
    )
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
# ARTIFACT: test_legal_work_completion_static_role_grants.py
# VERSION: v1.0.0-P14-R20R12-WORK-COMPLETION-STATIC-GRANTS
# STATIC AUTHORIZATION ROLES:
#   LEGAL_PARTNER / LEGAL_ATTORNEY / LEGAL_PARALEGAL / LEGAL_SECRETARY
# TENANT MEMBERSHIP AUTHORITY: NONE
# BUSINESS-ROLE ELIGIBILITY AUTHORITY: NONE
# CURRENT ROLE POSSESSION AUTHORITY: NONE
# ASSIGNMENT AUTHORITY: NONE
# COMPLETION COMMAND AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
