import pytest
from fastapi.routing import APIRoute
from fastapi import HTTPException
from types import SimpleNamespace

from tools.eos.api.pos_workspace_router import (
    POSLocationAssignmentRequest, POSSaleCreateRequest, router,
    require_pos_workspace_indexes_ready,
)
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import (
    permission_for_business_role_operation, tenant_role_operation_eligibility, TENANT_ROLES,
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
        ("/pos/locations/{location_id}/sales/{sale_id}/tenders/{evidence_id}/execute", "POST"),
        ("/pos/locations/{location_id}/sales/{sale_id}/refund-intents/{evidence_id}/execute", "POST"),
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
        "pos:movement:authorize": "pos_movement_authorize",
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
    assert "tenant_pos_operator" in TENANT_ROLES
    assert "POS_OPERATOR" in get_roles_granting_permission("pos:sale:create")
    assert tenant_role_operation_eligibility("tenant_pos_operator", "pos_sale_create") == "ELIGIBLE"
    assert tenant_role_operation_eligibility("tenant_pos_operator", "pos_location_assignment_manage") == "DENY"
    assert tenant_role_operation_eligibility("tenant_auditor", "pos_sale_create") == "DENY"
    assert "TENANT_OWNER" in get_roles_granting_permission("pos:financial_execution:authorize")
    assert "POS_OPERATOR" not in get_roles_granting_permission("pos:financial_execution:authorize")
    assert tenant_role_operation_eligibility("tenant_owner", "pos_financial_execution_authorize") == "ELIGIBLE"
    assert tenant_role_operation_eligibility("tenant_pos_operator", "pos_financial_execution_authorize") == "DENY"



def test_pos_workspace_fails_closed_until_canonical_startup_indexes_are_ready():
    unavailable = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(pos_workspace_indexes_ready=False)))
    with pytest.raises(HTTPException) as error:
        require_pos_workspace_indexes_ready(unavailable)
    assert error.value.status_code == 503
    assert error.value.detail == "POS_WORKSPACE_INDEXES_NOT_READY"

    ready = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(pos_workspace_indexes_ready=True)))
    assert require_pos_workspace_indexes_ready(ready) is None
