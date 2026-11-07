import pytest

from tools.eos.auth.permission_namespace import PermissionDisposition, permission_metadata
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP, get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import (
    DENY, ELIGIBLE, OPERATIONS, permission_for_business_role_operation,
    tenant_role_operation_eligibility,
)
from tools.eos.auth.tenant_authorization import _BINDINGS

CASES = (
    ("crm_work_item_read", "crm:work_item:read"),
    ("crm_work_item_create", "crm:work_item:create"),
    ("crm_work_item_complete", "crm:work_item:complete"),
)


@pytest.mark.parametrize(("operation", "permission"), CASES)
def test_owner_work_item_operation_is_exact_canonical_tenant_permission(operation, permission):
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
def test_owner_admin_manager_are_eligible_but_specialized_roles_are_not(operation):
    for role in ("tenant_owner", "tenant_admin", "tenant_manager"):
        assert tenant_role_operation_eligibility(role, operation) == ELIGIBLE
    for role in (
        "tenant_auditor", "tenant_legal_partner", "tenant_legal_attorney",
        "tenant_legal_paralegal", "tenant_legal_secretary", "tenant_legal_finance",
        "tenant_sheriff", "tenant_deputy", "tenant_legal_client",
    ):
        expected = ELIGIBLE if role == "tenant_auditor" and operation == "crm_work_item_read" else DENY
        assert tenant_role_operation_eligibility(role, operation) == expected


def test_static_role_grants_are_narrow_and_nonpossessory():
    assert ROLE_PERMISSIONS_MAP["TENANT_OWNER"] == [
        "subscription:read",
        "crm:work_item:read",
        "crm:work_item:create",
        "crm:work_item:complete",
        "operations:work_item:read",
        "operations:work_item:create",
        "operations:work_item:complete",
        "intelligence:work_item:read",
        "intelligence:work_item:create",
        "intelligence:work_item:complete",
        "tenant:commercial_agreement:read",
        "tenant:commercial_agreement:draft:create",
        "tenant:commercial_agreement:execute",
        "tenant:commercial_agreement:activate",
        "pos:location_assignment:manage",
        "pos:sale:read",
        "pos:sale:create",
        "pos:tender:create",
        "pos:cash:record",
        "pos:return:create",
        "pos:refund:create",
        "pos:payment:authorize",
        "security:institutional_signer:enroll",
        "security:institutional_signer:approve",
        "security:institutional_signer:revoke",
    ]
    assert get_roles_granting_permission("crm:work_item:read") == ("AUDITOR", "ENTERPRISE_ADMIN", "TENANT_OWNER")
    assert get_roles_granting_permission("crm:work_item:create") == ("ENTERPRISE_ADMIN", "TENANT_OWNER")
    assert get_roles_granting_permission("crm:work_item:complete") == ("ENTERPRISE_ADMIN", "TENANT_OWNER")
    for role, grants in ROLE_PERMISSIONS_MAP.items():
        if role not in {"AUDITOR", "ENTERPRISE_ADMIN", "TENANT_OWNER"}:
            assert not any(permission in grants for _, permission in CASES)
