import inspect
from pathlib import Path

import pytest
from pydantic import ValidationError

from tools.eos.api import server
from tools.eos.api.tenant_module_workspace_router import ModuleWorkCompleteRequest, ModuleWorkCreateRequest, router
from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization


def test_operations_and_intelligence_workspace_routes_are_distinct_and_mounted_once():
    routes = { (route.path, tuple(sorted(route.methods or ()))): route for route in router.routes }
    expected = {
        ("/tenant-modules/operations/workspace", ("GET",)),
        ("/tenant-modules/operations/workspace/work-items", ("POST",)),
        ("/tenant-modules/operations/workspace/work-items/{work_item_id}/complete", ("POST",)),
        ("/tenant-modules/intelligence/workspace", ("GET",)),
        ("/tenant-modules/intelligence/workspace/work-items", ("POST",)),
        ("/tenant-modules/intelligence/workspace/work-items/{work_item_id}/complete", ("POST",)),
    }
    assert set(routes) == expected
    for key, route in routes.items():
        dependencies = route.dependant.dependencies
        assert len(dependencies) == 1
        assert isinstance(dependencies[0].call, RequireTenantAuthorization)
    source = inspect.getsource(server)
    assert source.count("app.include_router(tenant_module_workspace_router, prefix=\"/api\")") == 1
    assert "from .tenant_module_workspace_router import router as tenant_module_workspace_router" in source


def test_browser_commands_cannot_author_tenant_product_principal_or_source_authority():
    with pytest.raises(ValidationError):
        ModuleWorkCreateRequest.model_validate({
            "title": "Prepare operations plan",
            "tenant_id": "FORGED-TENANT",
        })
    with pytest.raises(ValidationError):
        ModuleWorkCreateRequest.model_validate({
            "title": "Prepare operations plan",
            "product_id": "INTELLIGENCE",
        })
    with pytest.raises(ValidationError):
        ModuleWorkCreateRequest.model_validate({
            "title": "Prepare operations plan",
            "created_by_principal_id": "FORGED-PRINCIPAL",
        })
    with pytest.raises(ValidationError):
        ModuleWorkCompleteRequest.model_validate({
            "completion_note": "Done",
            "tenant_id": "FORGED-TENANT",
            "product_id": "OPERATIONS",
        })


def test_module_workspace_transport_is_bounded_through_bff_and_dev_proxy():
    bff = Path("server/server.js").read_text(encoding="utf-8")
    vite = Path("client/vite.config.js").read_text(encoding="utf-8")
    assert "'/api/tenant-modules'" in bff
    assert "operations|intelligence" in bff
    assert "'/api/tenant-modules': {" in vite


def test_each_module_command_has_separate_permission_operation_pair():
    routes = {route.path: route for route in router.routes}
    cases = {
        "/tenant-modules/operations/workspace": ("operations:work_item:read", "operations_work_item_read"),
        "/tenant-modules/operations/workspace/work-items": ("operations:work_item:create", "operations_work_item_create"),
        "/tenant-modules/operations/workspace/work-items/{work_item_id}/complete": ("operations:work_item:complete", "operations_work_item_complete"),
        "/tenant-modules/intelligence/workspace": ("intelligence:work_item:read", "intelligence_work_item_read"),
        "/tenant-modules/intelligence/workspace/work-items": ("intelligence:work_item:create", "intelligence_work_item_create"),
        "/tenant-modules/intelligence/workspace/work-items/{work_item_id}/complete": ("intelligence:work_item:complete", "intelligence_work_item_complete"),
    }
    for path, expected in cases.items():
        dependency = routes[path].dependant.dependencies[0].call
        assert (dependency.permission_id, dependency.operation) == expected
