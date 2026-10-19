"""
TITLE: WILSY OS P9 Legal Work Reassignment Dual Binding RED Certificate
VERSION: v1.0.0-P9-R38-REASSIGNMENT-DUAL-BINDING-RED
AUTHORITY: Python EOS canonical tenant authorization composition
EPITOME: Freeze one exact reassignment operation-permission pair in both
    the business-policy permission lookup and authorization binding registry.
ABSOLUTE CANONICAL PATH:
    tests/unit/test_legal_work_reassignment_tenant_authorization_binding.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R38-REASSIGNMENT-DUAL-BINDING-RED
    certifies an exact dual binding and rejects adjacent/alias permissions.
TENANT BOUNDARY: Own-tenant current authority remains separately required.
AUTHORITY BOUNDARY: This test creates no ACTIVE role possession, recipient
    eligibility, matter scope, supervisor approval, command or legal effect.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
"""

from __future__ import annotations

from types import MappingProxyType

import tools.eos.auth.tenant_authorization as ta
from tools.eos.auth.tenant_authority_policy import (
    BUSINESS_ROLE_OPERATION_PERMISSIONS,
    permission_for_business_role_operation,
)

OPERATION = "legal_work_item_reassign"
PERMISSION = "legal_operations:work_item:reassign"


def test_reassignment_dual_binding_is_exact_and_unique() -> None:
    assert BUSINESS_ROLE_OPERATION_PERMISSIONS[OPERATION] == PERMISSION
    assert ta._BINDINGS[OPERATION] == PERMISSION
    assert permission_for_business_role_operation(OPERATION) == PERMISSION
    assert list(BUSINESS_ROLE_OPERATION_PERMISSIONS).count(OPERATION) == 1
    assert list(ta._BINDINGS).count(OPERATION) == 1


def test_reassignment_pair_cannot_be_inferred_from_other_operations() -> None:
    assert OPERATION != "legal_work_item_write"
    assert OPERATION != "legal_work_item_complete"
    assert OPERATION != "legal_matter_workflow_transition"

    assert PERMISSION != "legal_operations:work_item:write"
    assert PERMISSION != "legal_operations:work_item:complete"
    assert PERMISSION != "legal_operations:matter_workflow:transition"

    for operation, permission in (
        ("legal_work_item_reassign ", PERMISSION),
        (" legal_work_item_reassign", PERMISSION),
        ("LEGAL_WORK_ITEM_REASSIGN", PERMISSION),
        ("legal_work_item_*", PERMISSION),
        (OPERATION, "legal_operations:work_item:write"),
        (OPERATION, "legal_operations:work_item:complete"),
        (OPERATION, "legal_operations:matter_workflow:transition"),
    ):
        assert (operation, permission) != (OPERATION, PERMISSION)


def test_binding_registries_remain_immutable_and_non_executing() -> None:
    assert isinstance(BUSINESS_ROLE_OPERATION_PERMISSIONS, MappingProxyType)
    assert isinstance(ta._BINDINGS, MappingProxyType)

    assert (
        BUSINESS_ROLE_OPERATION_PERMISSIONS["legal_work_item_complete"]
        == "legal_operations:work_item:complete"
    )
    assert (
        ta._BINDINGS["legal_work_item_complete"]
        == "legal_operations:work_item:complete"
    )
    assert "financial_execution" not in ta._BINDINGS


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_work_reassignment_tenant_authorization_binding.py
# VERSION: v1.0.0-P9-R38-REASSIGNMENT-DUAL-BINDING-RED
# AUTHORITY BOUNDARY: exact operation-permission pairing only
# BUSINESS ELIGIBILITY AUTHORITY: SEPARATE P9-R33
# STATIC ROLE GRANTS AUTHORITY: SEPARATE P9-R25
# ACTIVE ROLE POSSESSION AUTHORITY: NOT CREATED
# MATTER / RECIPIENT / SUPERVISION AUTHORITY: NOT CREATED
# REASSIGNMENT COMMAND AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
