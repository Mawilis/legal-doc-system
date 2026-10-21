"""
TITLE: WILSY OS P9 Legal Work Reassignment Permission RED Certificate
VERSION: v1.0.0-P9-R16-REASSIGNMENT-PERMISSION-RED
AUTHORITY: Wilsy OS Core Governance / Python EOS IAM
EPITOME: Freeze exact reassignment permission semantics before production mutation.
ABSOLUTE CANONICAL PATH: tests/unit/test_legal_work_reassignment_permission_namespace.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG: 2026-10-19 v1.0.0-P9-R16-REASSIGNMENT-PERMISSION-RED
    establishes the test-first permission vocabulary contract.
COMPLIANCE: Exact, fail-closed, test-first permission validation.
SECURITY / PRIVACY POSTURE: Reject aliases, wildcard and implicit authority.
TENANT BOUNDARY: Exact own-tenant membership required.
AUTHORITY BOUNDARY: Vocabulary alone grants no assignment, supervision,
    role possession, operation binding, HTTP or reassignment authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

import pytest

from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    canonical_permissions,
    permission_metadata,
)

PERMISSION = "legal_operations:work_item:reassign"


def test_reassignment_permission_is_exact_canonical_tenant_vocabulary() -> None:
    metadata = permission_metadata(PERMISSION)
    assert metadata.permission_id == PERMISSION
    assert metadata.disposition is PermissionDisposition.CANONICAL
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.business_capability == (
        "request bounded own-tenant Legal work-item reassignment admission"
    )
    assert metadata.tenant_membership_required is True
    assert metadata.system_assignment_required is False
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False
    assert PERMISSION != "legal_operations:work_item:write"
    assert PERMISSION != "legal_operations:work_item:complete"

    token = ('"permission_id":"' + PERMISSION + '"').encode("ascii")
    serialized = canonical_permissions()
    assert isinstance(serialized, bytes)
    assert serialized.count(token) == 1

    forbidden = {
        "authorization_role",
        "business_role",
        "role_grant",
        "role_assignment",
        "assignee_principal_id",
        "supervisor_principal_id",
        "assignment_authorized",
        "reassignment_executed",
        "completion_event_id",
        "payment_id",
        "settlement_id",
    }
    assert forbidden.isdisjoint(metadata.__dataclass_fields__)


@pytest.mark.parametrize(
    "variant",
    (
        "legal_operations:work_item:reassign ",
        " legal_operations:work_item:reassign",
        "LEGAL_OPERATIONS:WORK_ITEM:REASSIGN",
        "legal_operations:work_item:*",
        "work_item:reassign",
        "legal_operations:work_item:reassigned",
    ),
)
def test_reassignment_permission_aliases_fail_closed(variant: str) -> None:
    with pytest.raises(ValueError, match="UNKNOWN_PERMISSION"):
        permission_metadata(variant)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_work_reassignment_permission_namespace.py
# VERSION: v1.0.0-P9-R16-REASSIGNMENT-PERMISSION-RED
# AUTHORITY BOUNDARY: permission test only
# TENANT POSTURE: membership required, no cross-tenant grant
# FAIL-CLOSED POSTURE: reject unknown and malformed permissions
# REASSIGNMENT COMMAND AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
