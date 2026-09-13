"""M14-P5 direct certificate for the canonical billing-intelligence HTTP seam.

VERSION: v1.1.0-M14-P5-BILLING-INTELLIGENCE-EVIDENCE-HTTP-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies exact authorization dependency identity and authorized
         context tenant propagation without creating domain authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_billing_router_intelligence_seam.py
COLLABORATION / OWNERSHIP: Direct HTTP certificate; the orchestrator remains
                            the derivation and persistence owner.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: 2026-09-13 v1.1.0-M14-P5 certifies the billing-intelligence
           permission/operation binding and context-only tenant scope.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
"""
from datetime import datetime, timezone
import importlib
import sys
import types
from typing import Any, Iterator, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.saas.billing.billing_intelligence_engine import derive_billing_intelligence


ROUTER_NAME = "tools.eos.api.billing_router"
REGISTRY_NAME = "tools.eos.saas.billing.billing_registry"


def _authorized_context(tenant_id: str = "tenant-http") -> TenantAuthorizationContext:
    return TenantAuthorizationContext(
        identity=cast(Any, types.SimpleNamespace(identity_id="principal-http")),
        tenant_id=tenant_id,
        decision=cast(Any, types.SimpleNamespace(authorized=True)),
    )


def _evidence() -> Any:
    return derive_billing_intelligence(
        tenant_id="tenant-http",
        as_of=datetime(2026, 9, 12, 12, tzinfo=timezone.utc),
    )


@pytest.fixture()
def router_module() -> Iterator[Any]:
    previous_registry = sys.modules.get(REGISTRY_NAME)
    previous_router = sys.modules.pop(ROUTER_NAME, None)
    stub = types.ModuleType(REGISTRY_NAME)
    setattr(stub, "BillingRegistry", type("BillingRegistry", (), {}))
    setattr(stub, "get_billing_registry", lambda: object())
    setattr(stub, "db", {})
    setattr(stub, "client", object())
    setattr(stub, "platform_invoices_coll", object())
    setattr(stub, "client_invoices_coll", object())
    setattr(stub, "payments_coll", object())
    sys.modules[REGISTRY_NAME] = stub
    try:
        module = importlib.import_module(ROUTER_NAME)
        yield module
    finally:
        sys.modules.pop(ROUTER_NAME, None)
        if previous_router is not None:
            sys.modules[ROUTER_NAME] = previous_router
        if previous_registry is not None:
            sys.modules[REGISTRY_NAME] = previous_registry
        else:
            sys.modules.pop(REGISTRY_NAME, None)


class Database:
    def __init__(self) -> None:
        self.collections: dict[str, object] = {}

    def __getitem__(self, name: str) -> object:
        value = self.collections.setdefault(name, object())
        return value


def test_canonical_endpoint_is_mounted_once_and_delegates(router_module: Any, monkeypatch: Any) -> None:
    module = router_module
    routes = [route for route in module.router.routes if getattr(route, "path", "") == "/billing/intelligence/evidence"]
    assert len(routes) == 1
    calls: list[dict[str, Any]] = []
    database = Database()

    class FakeOrchestrator:
        def __init__(self, **collections: Any) -> None:
            calls.append({"constructor": collections})

        def collect_and_persist(self, tenant_id: str, *, as_of: datetime) -> Any:
            calls.append({"tenant_id": tenant_id, "as_of": as_of})
            return _evidence()

        def response_payload(self, value: Any) -> dict[str, Any]:
            calls.append({"delegated": value})
            return {**value.to_dict(), "evidence_identity": "a" * 128}

    monkeypatch.setattr(module, "BillingIntelligenceOrchestrator", FakeOrchestrator)
    monkeypatch.setattr(module, "_require_db", lambda: database)
    app = FastAPI()
    app.include_router(module.router)
    app.dependency_overrides[module._BILLING_INTELLIGENCE_EVIDENCE_READ_AUTHORIZATION] = (
        lambda: _authorized_context("tenant-http")
    )
    with TestClient(app) as client:
        response = client.get(
            "/billing/intelligence/evidence?as_of=2026-09-12T12:00:00%2B00:00",
        )
    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "tenant-http"
    assert body["unsupported_outputs"]
    assert any("tenant_id" in item for item in calls)
    assert any("delegated" in item for item in calls)


def test_authorized_context_tenant_cannot_be_replaced_by_query_or_header(
    router_module: Any, monkeypatch: Any
) -> None:
    module = router_module
    seen: list[str] = []

    class FakeOrchestrator:
        def __init__(self, **collections: Any) -> None:
            pass

        def collect_and_persist(self, tenant_id: str, *, as_of: datetime) -> Any:
            seen.append(tenant_id)
            return _evidence()

        def response_payload(self, value: Any) -> dict[str, Any]:
            return value.to_dict()

    monkeypatch.setattr(module, "BillingIntelligenceOrchestrator", FakeOrchestrator)
    monkeypatch.setattr(module, "_require_db", lambda: Database())
    app = FastAPI()
    app.include_router(module.router)
    app.dependency_overrides[module._BILLING_INTELLIGENCE_EVIDENCE_READ_AUTHORIZATION] = (
        lambda: _authorized_context("authorized-tenant")
    )
    with TestClient(app) as client:
        response = client.get(
            "/billing/intelligence/evidence?as_of=2026-09-12T12:00:00%2B00:00"
            "&tenant_id=attacker-query",
            headers={"X-Tenant-ID": "attacker-header"},
        )
    assert response.status_code == 200
    assert seen == ["authorized-tenant"]


def test_missing_snapshot_is_fail_closed(router_module: Any) -> None:
    module = router_module
    app = FastAPI()
    app.include_router(module.router)
    app.dependency_overrides[module._BILLING_INTELLIGENCE_EVIDENCE_READ_AUTHORIZATION] = (
        lambda: _authorized_context("tenant-http")
    )
    with TestClient(app) as client:
        response = client.get("/billing/intelligence/evidence")
    assert response.status_code == 422


# ARTIFACT: test_billing_router_intelligence_seam.py
# VERSION: v1.1.0-M14-P5-BILLING-INTELLIGENCE-EVIDENCE-HTTP-CERT
# AUTHORITY BOUNDARY: HTTP composition certificate only.
# TENANT POSTURE: canonical route scope comes only from authorized context.
# FAIL-CLOSED POSTURE: missing authorization or snapshot cannot succeed.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
