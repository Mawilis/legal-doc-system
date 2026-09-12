"""M12-P3 direct certificate for the canonical Python HTTP seam."""
from datetime import datetime, timezone
import importlib
import sys
import types
from typing import Any, Iterator

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from tools.eos.saas.billing.billing_intelligence_engine import derive_billing_intelligence


ROUTER_NAME = "tools.eos.api.billing_router"
REGISTRY_NAME = "tools.eos.saas.billing.billing_registry"


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
    app.dependency_overrides[module.get_tenant_id] = lambda: "tenant-http"
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


@pytest.mark.parametrize("tenant", ["GLOBAL_ROOT", "MASTER", "SOVEREIGN_ROOT", ""])
def test_global_or_blank_tenant_is_rejected(router_module: Any, monkeypatch: Any, tenant: str) -> None:
    module = router_module
    monkeypatch.setattr(module, "_require_db", lambda: Database())
    app = FastAPI()
    app.include_router(module.router)
    app.dependency_overrides[module.get_tenant_id] = lambda: tenant
    with TestClient(app) as client:
        response = client.get(
            "/billing/intelligence/evidence?as_of=2026-09-12T12:00:00%2B00:00",
        )
    assert response.status_code == 400


def test_missing_snapshot_is_fail_closed(router_module: Any) -> None:
    module = router_module
    app = FastAPI()
    app.include_router(module.router)
    app.dependency_overrides[module.get_tenant_id] = lambda: "tenant-http"
    with TestClient(app) as client:
        response = client.get("/billing/intelligence/evidence")
    assert response.status_code == 422


# ARTIFACT: test_billing_router_intelligence_seam.py
# VERSION: v1.0.0-M12-P3
# AUTHORITY BOUNDARY: HTTP composition certificate only.
# END OF WILSY OS SOVEREIGN ARTIFACT
