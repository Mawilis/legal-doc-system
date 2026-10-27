"""G64 workspace permission vocabulary is not an authorization grant.

VERSION: v1.0.0-G64-WORKSPACE-PERMISSION-VOCABULARY
AUTHORITY: Canonical permission semantics only; no role or runtime authority.
"""
import pytest

from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    canonical_permissions,
    permission_metadata,
)

PERMISSION = "legal_operations:g64_ratification_workspace:write"


def test_g64_workspace_permission_is_exact_own_tenant_and_non_self_authorizing():
    metadata = permission_metadata(PERMISSION)
    assert metadata.permission_id == PERMISSION
    assert metadata.disposition is PermissionDisposition.CANONICAL
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.system_assignment_required is False
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False
    assert metadata.business_capability == (
        "record own-tenant G64 ratification workspace evidence only"
    )


@pytest.mark.parametrize(
    "value",
    (
        "legal_operations:g64_ratification_workspace:write ",
        " legal_operations:g64_ratification_workspace:write",
        "LEGAL_OPERATIONS:G64_RATIFICATION_WORKSPACE:WRITE",
        "legal_operations:g64_ratification_workspace:*",
        "legal_operations:g64_ratification_workspace:ratify",
    ),
)
def test_g64_permission_aliases_and_wildcards_fail_closed(value):
    with pytest.raises(ValueError, match="UNKNOWN_PERMISSION"):
        permission_metadata(value)


def test_g64_permission_is_serialized_once_and_does_not_create_a_grant():
    raw = canonical_permissions()
    token = b'"permission_id":"' + PERMISSION.encode("ascii") + b'"'
    assert raw.count(token) == 1
    metadata = permission_metadata(PERMISSION)
    assert metadata.authorizes_by_itself is False
    assert metadata.tenant_membership_required is True
    assert metadata.financial_execution_capable is False


def test_g64_read_and_write_permissions_are_separate_non_self_authorizing_capabilities():
    read = permission_metadata("legal_operations:g64_ratification_workspace:read")
    write = permission_metadata(PERMISSION)
    assert read.permission_id != write.permission_id
    assert read.tenant_membership_required is True
    assert write.tenant_membership_required is True
    assert read.authorizes_by_itself is False
    assert write.authorizes_by_itself is False
    raw = canonical_permissions()
    assert raw.count(b'"permission_id":"legal_operations:g64_ratification_workspace:read"') == 1
    assert raw.count(b'"permission_id":"legal_operations:g64_ratification_workspace:write"') == 1
