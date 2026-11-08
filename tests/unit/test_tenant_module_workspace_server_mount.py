# TITLE: WILSY EOS Tenant Module Workspace API and Transport Contract Tests
# VERSION: v1.0.1-EOS-TENANT-MODULE-WORKSPACE-PYTHON-TRANSPORT
# AUTHORITY: Static and in-process Python EOS route/transport certification only.
# EPITOME: Verify authenticated Operations and Intelligence workspace routes, tenant-authority input rejection, canonical Python EOS mounting, direct frontend development proxying, distinct module persistence, and permission-operation separation.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_module_workspace_server_mount.py
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; Python EOS owns tenant module workspace API and durable work authority.
# CERTIFICATION OR UPDATE DATE: 2026-11-09
# CHANGELOG:
#   v1.0.1-EOS-TENANT-MODULE-WORKSPACE-PYTHON-TRANSPORT replaces the retired
#   Node BFF source assertion with verification of the canonical Python EOS
#   router mount and Vite's direct /api/tenant-modules proxy to port 9095.
#   This preserves the transport boundary and removes a stale test dependency;
#   no application runtime behavior or authorization contract is changed.
#   v1.0.0 established route, request, module and permission contract tests.
# COMPLIANCE: AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
# SECURITY / PRIVACY POSTURE: Tests use source/config inspection and in-process route metadata; no credentials or live tenant records.
# TENANT BOUNDARY: Request models reject browser-supplied tenant, product and principal authority; no tenant data is mutated.
# AUTHORITY BOUNDARY: Tests verify authenticated EOS-owned routes and frontend transport only; browser/Vite code grants no business authority.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains the exclusive financial execution authority.

"""Contract tests for canonical Python EOS tenant-module workspace transport.

The retired Node BFF is intentionally absent. The browser development proxy
forwards the canonical API path directly to Python EOS; it is not a backend or
an authority boundary.
"""

import inspect
from pathlib import Path

import pytest
from pydantic import ValidationError

from tools.eos.api import server
from tools.eos.api.tenant_module_workspace_router import (
    ModuleWorkCompleteRequest,
    ModuleWorkCreateRequest,
    _PRODUCTS,
    router,
)
from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization


def test_operations_and_intelligence_workspace_routes_are_distinct_and_mounted_once():
    """Both modules expose distinct authenticated routes mounted once by EOS."""
    routes = {
        (route.path, tuple(sorted(route.methods or ()))): route
        for route in router.routes
    }
    expected = {
        ("/tenant-modules/operations/workspace", ("GET",)),
        ("/tenant-modules/operations/workspace/work-items", ("POST",)),
        (
            "/tenant-modules/operations/workspace/work-items/{work_item_id}/complete",
            ("POST",),
        ),
        ("/tenant-modules/intelligence/workspace", ("GET",)),
        ("/tenant-modules/intelligence/workspace/work-items", ("POST",)),
        (
            "/tenant-modules/intelligence/workspace/work-items/{work_item_id}/complete",
            ("POST",),
        ),
    }
    assert set(routes) == expected
    for route in routes.values():
        dependencies = route.dependant.dependencies
        assert len(dependencies) == 1
        assert isinstance(dependencies[0].call, RequireTenantAuthorization)

    source = inspect.getsource(server)
    assert (
        source.count(
            'app.include_router(tenant_module_workspace_router, prefix="/api")'
        )
        == 1
    )
    assert (
        "from .tenant_module_workspace_router import "
        "router as tenant_module_workspace_router"
    ) in source


def test_browser_commands_cannot_author_tenant_product_principal_or_source_authority():
    """Browser payloads cannot supply server-owned tenant or principal context."""
    with pytest.raises(ValidationError):
        ModuleWorkCreateRequest.model_validate(
            {"title": "Prepare operations plan", "tenant_id": "FORGED-TENANT"}
        )
    with pytest.raises(ValidationError):
        ModuleWorkCreateRequest.model_validate(
            {"title": "Prepare operations plan", "product_id": "INTELLIGENCE"}
        )
    with pytest.raises(ValidationError):
        ModuleWorkCreateRequest.model_validate(
            {
                "title": "Prepare operations plan",
                "created_by_principal_id": "FORGED-PRINCIPAL",
            }
        )
    with pytest.raises(ValidationError):
        ModuleWorkCompleteRequest.model_validate(
            {
                "completion_note": "Done",
                "tenant_id": "FORGED-TENANT",
                "product_id": "OPERATIONS",
            }
        )


def test_module_workspace_transport_targets_python_eos_through_dev_proxy():
    """Vite forwards the API path directly to the canonical Python EOS server."""
    eos_source = inspect.getsource(server)
    vite = Path("client/vite.config.js").read_text(encoding="utf-8")

    assert (
        eos_source.count(
            'app.include_router(tenant_module_workspace_router, prefix="/api")'
        )
        == 1
    )
    proxy_start = vite.index("      '/api/tenant-modules': {")
    proxy_end = vite.index("      },", proxy_start)
    proxy_block = vite[proxy_start:proxy_end]

    assert "target: 'http://localhost:9095'" in proxy_block
    assert "changeOrigin: true" in proxy_block
    assert "rewrite:" not in proxy_block


def test_module_products_have_distinct_workspace_keys_and_persistence_collections():
    """Operations and Intelligence retain separate product and persistence scopes."""
    operations = _PRODUCTS["operations"]
    intelligence = _PRODUCTS["intelligence"]
    assert operations[0].value == "OPERATIONS"
    assert intelligence[0].value == "INTELLIGENCE"
    assert operations[1] == "OPERATIONS_DASHBOARD"
    assert intelligence[1] == "INTELLIGENCE_DASHBOARD"
    assert operations[2] == "tenant_operations_work_items"
    assert intelligence[2] == "tenant_intelligence_work_items"
    assert operations[2] != intelligence[2]


def test_each_module_command_has_separate_permission_operation_pair():
    """Every module route uses its own exact permission and operation identity."""
    routes = {route.path: route for route in router.routes}
    cases = {
        "/tenant-modules/operations/workspace": (
            "operations:work_item:read",
            "operations_work_item_read",
        ),
        "/tenant-modules/operations/workspace/work-items": (
            "operations:work_item:create",
            "operations_work_item_create",
        ),
        "/tenant-modules/operations/workspace/work-items/{work_item_id}/complete": (
            "operations:work_item:complete",
            "operations_work_item_complete",
        ),
        "/tenant-modules/intelligence/workspace": (
            "intelligence:work_item:read",
            "intelligence_work_item_read",
        ),
        "/tenant-modules/intelligence/workspace/work-items": (
            "intelligence:work_item:create",
            "intelligence_work_item_create",
        ),
        "/tenant-modules/intelligence/workspace/work-items/{work_item_id}/complete": (
            "intelligence:work_item:complete",
            "intelligence_work_item_complete",
        ),
    }
    for path, expected in cases.items():
        dependency = routes[path].dependant.dependencies[0].call
        assert (dependency.permission_id, dependency.operation) == expected


# ARTIFACT: tests/unit/test_tenant_module_workspace_server_mount.py
# VERSION: v1.0.1-EOS-TENANT-MODULE-WORKSPACE-PYTHON-TRANSPORT
# AUTHORITY BOUNDARY: In-process API and frontend development transport tests only.
# TENANT POSTURE: Forged tenant/principal inputs are rejected; no tenant records are mutated.
# FAIL-CLOSED POSTURE: Missing EOS route mounts, invalid request boundaries or proxy drift fail the focused suite.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
