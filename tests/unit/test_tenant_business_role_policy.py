"""Sovereign F1C0A static business-role policy certificate."""
import pytest
from tools.eos.auth.tenant_authority_policy import (
    DENY, ELIGIBLE, OPERATIONS, permission_for_business_role_operation,
    tenant_role_operation_eligibility,
)
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import get_roles_granting_permission

OPS = {"business_role_read", "business_role_assign", "business_role_change", "business_role_revoke"}
READ = "tenant:business_role:read"
WRITE = "tenant:business_role:write"

@pytest.mark.parametrize("operation", sorted(OPS))
def test_operations_and_mapping(operation: str) -> None:
    assert operation in OPERATIONS
    assert permission_for_business_role_operation(operation) == (READ if operation == "business_role_read" else WRITE)

def test_forbidden_alias_absent_and_unknown_denied() -> None:
    assert "business_role_manage" not in OPERATIONS
    assert permission_for_business_role_operation("business_role_manage") is None
    assert tenant_role_operation_eligibility("tenant_owner", "business_role_manage") == DENY

@pytest.mark.parametrize("permission", [READ, WRITE])
def test_permission_metadata_is_tenant_scoped_nonfinancial_and_non_authorizing(permission: str) -> None:
    metadata = permission_metadata(permission)
    assert metadata is not None
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.system_assignment_required is True
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False

def test_authorization_role_grants_exact() -> None:
    assert get_roles_granting_permission(READ) == ("AUDITOR", "ENTERPRISE_ADMIN")
    assert get_roles_granting_permission(WRITE) == ("ENTERPRISE_ADMIN",)

@pytest.mark.parametrize("role,operation,expected", [
    ("tenant_owner", "business_role_read", ELIGIBLE), ("tenant_admin", "business_role_read", ELIGIBLE),
    ("tenant_auditor", "business_role_read", ELIGIBLE), ("tenant_manager", "business_role_read", DENY),
    ("tenant_owner", "business_role_assign", ELIGIBLE), ("tenant_admin", "business_role_assign", ELIGIBLE),
    ("tenant_manager", "business_role_assign", DENY), ("tenant_auditor", "business_role_assign", DENY),
    ("tenant_owner", "business_role_change", ELIGIBLE), ("tenant_admin", "business_role_change", ELIGIBLE),
    ("tenant_manager", "business_role_change", DENY), ("tenant_auditor", "business_role_change", DENY),
    ("tenant_owner", "business_role_revoke", ELIGIBLE), ("tenant_admin", "business_role_revoke", ELIGIBLE),
    ("tenant_manager", "business_role_revoke", DENY), ("tenant_auditor", "business_role_revoke", DENY),
])
def test_business_role_eligibility(role: str, operation: str, expected: str) -> None:
    assert tenant_role_operation_eligibility(role, operation) == expected

def test_authorization_role_operations_remain_distinct() -> None:
    assert "role_grant" in OPERATIONS and "role_revoke" in OPERATIONS
    assert permission_for_business_role_operation("role_grant") is None
    assert permission_for_business_role_operation("role_revoke") is None

def test_policy_is_static_and_no_repository_writer() -> None:
    assert all("business_role" not in name for name in ("execute", "dispatch", "persist"))
