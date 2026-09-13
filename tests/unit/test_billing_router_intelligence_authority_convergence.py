"""WILSY OS M14-P5 Python billing-intelligence authority certificate.

TITLE: Python Billing Intelligence Authority-Convergence Certificate
VERSION: v1.1.0-M14-P5-BILLING-INTELLIGENCE-EVIDENCE-HTTP-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove legacy summary/analytics compatibility remains fail closed
         while the canonical evidence endpoint uses exact authorization-bound
         tenant scope and delegated intelligence derivation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_billing_router_intelligence_authority_convergence.py
COLLABORATION / OWNERSHIP: Direct source and HTTP certificate for billing_router.py;
                            no production authority is created by this test.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: 2026-09-13 v1.1.0-M14-P5 certifies the exact billing-intelligence
           authorization dependency, context-only tenant scope, and preserved
           legacy compatibility firewall.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic tenant identifiers only; no secrets,
                             external clients, providers, or financial execution.
TENANT BOUNDARY: The canonical evidence route uses TenantAuthorizationContext;
                 legacy routes retain explicit X-Tenant-ID compatibility scope.
AUTHORITY BOUNDARY: Test certificate only; Kennel EOS remains execution authority.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, paid-state, or receivable
                              closure truth is created.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path
import sys
import types
from typing import Any, Iterator

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest


ROUTER_MODULE = "tools.eos.api.billing_router"
REGISTRY_MODULE = "tools.eos.saas.billing.billing_registry"
ROUTER_PATH = Path("tools/eos/api/billing_router.py")
FORBIDDEN_FORMULA_NAMES = {
    "arr",
    "mrr",
    "churn_rate",
    "ltv",
    "cac",
    "forecast",
    "growth_rate",
    "arpu",
    "credit_score",
    "anomaly_score",
}


@pytest.fixture()
def router_module() -> Iterator[Any]:
    """Import the router with persistence dependencies replaced by inert seams."""
    previous_registry = sys.modules.get(REGISTRY_MODULE)
    previous_router = sys.modules.pop(ROUTER_MODULE, None)
    stub = types.ModuleType(REGISTRY_MODULE)
    setattr(stub, "BillingRegistry", type("BillingRegistry", (), {}))
    setattr(stub, "get_billing_registry", lambda: object())
    setattr(stub, "db", {})
    setattr(stub, "client", object())
    setattr(stub, "platform_invoices_coll", object())
    setattr(stub, "client_invoices_coll", object())
    setattr(stub, "payments_coll", object())
    sys.modules[REGISTRY_MODULE] = stub
    try:
        yield importlib.import_module(ROUTER_MODULE)
    finally:
        sys.modules.pop(ROUTER_MODULE, None)
        if previous_router is not None:
            sys.modules[ROUTER_MODULE] = previous_router
        if previous_registry is not None:
            sys.modules[REGISTRY_MODULE] = previous_registry
        else:
            sys.modules.pop(REGISTRY_MODULE, None)


def _app(module: Any) -> FastAPI:
    app = FastAPI()
    app.include_router(module.router)
    app.dependency_overrides[module.get_tenant_id] = lambda: "tenant-p4"
    return app


@pytest.mark.parametrize("path", ["/billing/summary", "/billing/analytics"])
def test_legacy_routes_fail_closed_without_synthetic_intelligence(
    router_module: Any,
    path: str,
) -> None:
    """Legacy callers receive an explicit canonical redirect, never zeros."""
    with TestClient(_app(router_module)) as client:
        response = client.get(path)
    assert response.status_code == 410
    detail = response.json()["detail"]
    assert detail["code"] == "BILLING_LEGACY_INTELLIGENCE_UNAVAILABLE"
    assert detail["canonical_endpoint"] == "/billing/intelligence/evidence"
    assert set(detail["unsupported_outputs"]) >= FORBIDDEN_FORMULA_NAMES
    assert not any(key in detail for key in FORBIDDEN_FORMULA_NAMES)


def test_legacy_routes_require_explicit_tenant(router_module: Any) -> None:
    """Compatibility boundaries retain the existing X-Tenant-Id dependency."""
    app = FastAPI()
    app.include_router(router_module.router)
    with TestClient(app) as client:
        assert client.get("/billing/summary").status_code == 422
        assert client.get("/billing/analytics").status_code == 422


def test_legacy_route_functions_contain_no_formula_identifiers() -> None:
    """AST proof prevents easy reintroduction of router-owned intelligence."""
    tree = ast.parse(ROUTER_PATH.read_text(encoding="utf-8"))
    targets = {
        "get_billing_summary",
        "get_billing_analytics",
    }
    functions = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in targets
    }
    assert set(functions) == targets
    for node in functions.values():
        names = {
            child.id
            for child in ast.walk(node)
            if isinstance(child, ast.Name)
        }
        assert names.isdisjoint(FORBIDDEN_FORMULA_NAMES)
        assert not any(
            isinstance(child, (ast.For, ast.While, ast.comprehension))
            for child in ast.walk(node)
        )


def test_legacy_response_models_removed(router_module: Any) -> None:
    """Obsolete numeric response models cannot force fabricated values."""
    assert not hasattr(router_module, "BillingSummaryResponse")
    assert not hasattr(router_module, "BillingAnalyticsResponse")


def test_canonical_endpoint_remains_single_delegated_route(router_module: Any) -> None:
    """Canonical route remains mounted once and delegates to the orchestrator."""
    routes = [
        route
        for route in router_module.router.routes
        if getattr(route, "path", "") == "/billing/intelligence/evidence"
    ]
    assert len(routes) == 1
    source = ROUTER_PATH.read_text(encoding="utf-8")
    endpoint_source = source[source.index('def get_billing_intelligence_evidence'):]
    assert "BillingIntelligenceOrchestrator(" in endpoint_source
    assert "collect_and_persist(" in endpoint_source
    assert "parse_as_of(" in endpoint_source


def test_m14_canonical_route_uses_exact_authorization_dependency(router_module: Any) -> None:
    """The route is mounted once and binds the canonical permission/operation object."""

    module = router_module
    routes = [
        route
        for route in module.router.routes
        if getattr(route, "path", "") == "/billing/intelligence/evidence"
    ]
    assert len(routes) == 1
    route = routes[0]
    assert len(route.dependant.dependencies) == 1
    dependency = route.dependant.dependencies[0]
    assert dependency.call is module._BILLING_INTELLIGENCE_EVIDENCE_READ_AUTHORIZATION
    assert dependency.call.permission_id == "billing_intelligence:evidence:read"
    assert dependency.call.operation == "billing_intelligence_evidence_read"
    assert "tenant_id" not in inspect.signature(route.endpoint).parameters
    assert "authorization" in inspect.signature(route.endpoint).parameters


def test_m14_canonical_route_has_no_legacy_tenant_dependency(router_module: Any) -> None:
    """Only summary/analytics retain get_tenant_id; canonical evidence does not."""

    module = router_module
    source = ROUTER_PATH.read_text(encoding="utf-8")
    start = source.index("async def get_billing_intelligence_evidence")
    end = source.index("@router.get", start + 1)
    canonical_source = source[start:end]
    assert "get_tenant_id" not in canonical_source
    assert "authorization.tenant_id" in canonical_source


def test_m14_canonical_route_cannot_succeed_without_authorization(
    router_module: Any,
) -> None:
    """The production dependency remains mandatory when not overridden."""

    app = FastAPI()
    app.include_router(router_module.router)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(
            "/billing/intelligence/evidence?as_of=2026-09-12T12:00:00%2B00:00"
        )
    assert response.status_code != 200


def test_no_unsupported_formula_source_survives(router_module: Any) -> None:
    """The router source has no legacy formula assignments or calculations."""
    source = ROUTER_PATH.read_text(encoding="utf-8")
    forbidden_fragments = (
        "arr = mrr * 12",
        "churn_rate =",
        "forecast = mrr",
        "growth_rate =",
        "ltv =",
        "cac =",
        "monthly_mrr =",
    )
    assert all(fragment not in source for fragment in forbidden_fragments)


# ARTIFACT: test_billing_router_intelligence_authority_convergence.py
# VERSION: v1.1.0-M14-P5-BILLING-INTELLIGENCE-EVIDENCE-HTTP-CERT
# AUTHORITY BOUNDARY: Direct HTTP/source authority-convergence certificate only.
# TENANT POSTURE: canonical evidence scope is authorized-context only.
# FAIL-CLOSED POSTURE: absent authorization and legacy unsupported routes deny.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
