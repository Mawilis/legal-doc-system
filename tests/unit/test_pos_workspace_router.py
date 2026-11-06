import pytest
from fastapi.routing import APIRoute

from tools.eos.api.pos_workspace_router import (
    POSLocationAssignmentRequest, POSSaleCreateRequest, router,
)
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import (
    permission_for_business_role_operation, tenant_role_operation_eligibility,
)


def test_pos_http_surface_contains_location_and_daily_commercial_operations():
    paths = {
        (route.path, method)
        for route in router.routes if isinstance(route, APIRoute)
        for method in route.methods or ()
    }
    expected = {
        ("/pos/locations/{location_id}/assignments", "POST"),
        ("/pos/locations/{location_id}/assignments/{principal_id}/revoke", "POST"),
        ("/pos/locations/{location_id}/sales", "POST"),
        ("/pos/locations/{location_id}/sales/{sale_id}", "GET"),
        ("/pos/locations/{location_id}/sales/{sale_id}/tenders", "POST"),
        ("/pos/locations/{location_id}/sales/{sale_id}/cash-tenders", "POST"),
        ("/pos/locations/{location_id}/sales/{sale_id}/returns", "POST"),
        ("/pos/locations/{location_id}/sales/{sale_id}/refund-intents", "POST"),
    }
    assert expected <= paths


def test_pos_request_contracts_forbid_browser_owned_tenant_and_actor_authority():
    with pytest.raises(ValueError):
        POSLocationAssignmentRequest.model_validate({
            "principal_id": "target-principal", "tenant_id": "browser-tenant",
            "actor_principal_id": "browser-actor",
        })
    with pytest.raises(ValueError):
        POSSaleCreateRequest.model_validate({
            "sale_id": "sale-1", "currency": "ZAR", "lines": [],
            "tenant_id": "browser-tenant", "principal_id": "browser-principal",
            "location_authority": "browser-asserted",
        })


def test_pos_permissions_are_exact_and_location_assignment_is_not_inherited():
    permissions = {
        "pos:location_assignment:manage": "pos_location_assignment_manage",
        "pos:sale:read": "pos_sale_read",
        "pos:sale:create": "pos_sale_create",
        "pos:tender:create": "pos_tender_create",
        "pos:cash:record": "pos_cash_record",
        "pos:return:create": "pos_return_create",
        "pos:refund:create": "pos_refund_create",
    }
    for permission, operation in permissions.items():
        metadata = permission_metadata(permission)
        assert metadata.tenant_membership_required is True
        assert metadata.authorizes_by_itself is False
        assert permission_for_business_role_operation(operation) == permission
    assert "TENANT_OWNER" in get_roles_granting_permission("pos:location_assignment:manage")
    assert "TENANT_ADMIN" not in get_roles_granting_permission("pos:location_assignment:manage")
    assert "TENANT_MANAGER" not in get_roles_granting_permission("pos:location_assignment:manage")
    assert tenant_role_operation_eligibility("tenant_manager", "pos_location_assignment_manage") == "DENY"
    assert tenant_role_operation_eligibility("tenant_manager", "pos_sale_create") == "DENY"
    assert tenant_role_operation_eligibility("tenant_auditor", "pos_sale_read") == "DENY"
    assert tenant_role_operation_eligibility("tenant_auditor", "pos_sale_create") == "DENY"
