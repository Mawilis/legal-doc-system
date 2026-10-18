"""
TITLE:
    WILSY OS P14-R20R14 Legal Work Completion Tenant Authorization
    Operation-Permission Binding RED Certificate

VERSION:
    v1.0.0-P14-R20R14-WORK-COMPLETION-TENANT-AUTH-BINDING

AUTHORITY BOUNDARY:
    Exact tenant-authorization operation-to-permission binding only.

    This certificate does not create work assignment, completion-event,
    workflow-transition, dependency, legal-event, AI, billing, payment,
    execution or settlement authority.
"""

from __future__ import annotations

import pytest

import tools.eos.auth.tenant_authorization as ta
from tools.eos.auth.tenant_authority_policy import (
    permission_for_business_role_operation,
)


OPERATION = "legal_work_item_complete"
PERMISSION = "legal_operations:work_item:complete"


def test_completion_tenant_authorization_binding_is_exact_and_unique() -> None:
    assert (
        ta._BINDINGS[
            OPERATION
        ]
        == PERMISSION
    )

    assert (
        list(
            ta._BINDINGS
        ).count(
            OPERATION
        )
        == 1
    )


def test_completion_binding_is_distinct_from_write_and_transition() -> None:
    assert (
        OPERATION
        != "legal_work_item_write"
    )
    assert (
        OPERATION
        != "legal_matter_workflow_transition"
    )

    assert (
        PERMISSION
        != "legal_operations:work_item:write"
    )
    assert (
        PERMISSION
        != "legal_operations:matter_workflow:transition"
    )


@pytest.mark.parametrize(
    ("operation", "permission"),
    (
        (
            "legal_work_item_complete ",
            PERMISSION,
        ),
        (
            " legal_work_item_complete",
            PERMISSION,
        ),
        (
            "LEGAL_WORK_ITEM_COMPLETE",
            PERMISSION,
        ),
        (
            "legal_work_item_*",
            PERMISSION,
        ),
        (
            OPERATION,
            "legal_operations:work_item:write",
        ),
        (
            OPERATION,
            "legal_operations:matter_workflow:transition",
        ),
    ),
)
def test_aliases_and_cross_permission_pairs_do_not_equal_canonical_binding(
    operation: str,
    permission: str,
) -> None:
    assert not (
        operation == OPERATION
        and permission == PERMISSION
    )


def test_policy_helper_does_not_invent_completion_binding_before_r20r14() -> None:
    # This assertion is intentionally RED until the exact R20R14
    # operation-permission binding is installed at its canonical layer.
    assert (
        permission_for_business_role_operation(
            OPERATION
        )
        == PERMISSION
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_completion_tenant_authorization_binding.py
# VERSION: v1.0.0-P14-R20R14-WORK-COMPLETION-TENANT-AUTH-BINDING
# OPERATION: legal_work_item_complete
# PERMISSION: legal_operations:work_item:complete
# BUSINESS ROLE ELIGIBILITY: SEPARATE R20R13
# STATIC ROLE POSSESSION: SEPARATE R20R12
# WORK ASSIGNMENT AUTHORITY: NONE
# COMPLETION COMMAND AUTHORITY: NONE
# LEGAL EVENT AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
