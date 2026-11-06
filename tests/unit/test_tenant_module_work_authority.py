import pytest

from tools.eos.auth.permission_namespace import PermissionDisposition, permission_metadata
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP, get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import (
    DENY, ELIGIBLE, OPERATIONS, permission_for_business_role_operation,
    tenant_role_operation_eligibility,
)
from tools.eos.auth.tenant_authorization import _BINDINGS

CASES = (
    ("operations_work_item_read", "operations:work_item:read"),
    ("operations_work_item_create", "operations:work_item:create"),
    ("operations_work_item_complete", "operations:work_item:complete"),
    ("intelligence_work_item_read", "intelligence:work_item:read"),
    ("intelligence_work_item_create", "intelligence:work_item:create"),
    ("intelligence_work_item_complete", "intelligence:work_item:complete"),
)


@pytest.mark.parametrize(("operation", "permission"), CASES)
def test_module_work_operation_has_exact_canonical_tenant_permission(operation, permission):
    assert operation in OPERATIONS
    assert permission_for_business_role_operation(operation) == permission
    assert _BINDINGS[operation] == permission
    metadata = permission_metadata(permission)
    assert metadata.disposition is PermissionDisposition.CANONICAL
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False


@pytest.mark.parametrize("operation", [case[0] for case in CASES])
def test_module_work_business_role_eligibility_is_explicit_and_least_authority(operation):
    for role in ("tenant_owner", "tenant_admin", "tenant_manager"):
        assert tenant_role_operation_eligibility(role, operation) == ELIGIBLE
    if operation.endswith("_read"):
        assert tenant_role_operation_eligibility("tenant_auditor", operation) == ELIGIBLE
    else:
        assert tenant_role_operation_eligibility("tenant_auditor", operation) == DENY
    for role in (
        "tenant_legal_partner", "tenant_legal_attorney", "tenant_legal_paralegal",
        "tenant_legal_secretary", "tenant_legal_finance", "tenant_sheriff",
        "tenant_deputy", "tenant_legal_client",
    ):
        assert tenant_role_operation_eligibility(role, operation) == DENY


def test_module_work_static_grants_are_separate_and_product_scoped():
    for permission in (
        "operations:work_item:read", "operations:work_item:create",
        "operations:work_item:complete", "intelligence:work_item:read",
        "intelligence:work_item:create", "intelligence:work_item:complete",
    ):
        assert "ENTERPRISE_ADMIN" in get_roles_granting_permission(permission)
        assert "TENANT_OWNER" in get_roles_granting_permission(permission)
    assert "AUDITOR" in get_roles_granting_permission("operations:work_item:read")
    assert "AUDITOR" not in get_roles_granting_permission("operations:work_item:create")
    assert "AUDITOR" in get_roles_granting_permission("intelligence:work_item:read")
    assert "AUDITOR" not in get_roles_granting_permission("intelligence:work_item:complete")
    for role in ("LEGAL_PARTNER", "LEGAL_ATTORNEY", "LEGAL_PARALEGAL", "LEGAL_SECRETARY"):
        assert not any(permission in ROLE_PERMISSIONS_MAP[role] for _, permission in CASES)
