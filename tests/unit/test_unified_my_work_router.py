from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from tools.eos.api import unified_my_work_router as route


def _context(tenant="tenant-a", principal="principal-a"):
    return SimpleNamespace(
        tenant_id=tenant,
        identity=SimpleNamespace(identity_id=principal),
    )


def _identity(principal="principal-a"):
    return SimpleNamespace(identity_id=principal)


def test_route_omits_denied_sources_and_reads_only_independently_admitted_sources(monkeypatch):
    calls = []

    def read_module(slug, *, tenant_id):
        calls.append((slug, tenant_id))
        return {
            "tenant_id": tenant_id,
            "items": [{
                "work_item_id": f"{slug}-1",
                "title": f"{slug} work",
                "status": "OPEN",
                "priority": "HIGH",
            }],
        }

    monkeypatch.setattr(route, "_read_module", read_module)
    monkeypatch.setattr(route, "_read_legal", lambda **_kwargs: pytest.fail("denied Legal source read"))
    monkeypatch.setattr(route, "_read_crm", lambda **_kwargs: pytest.fail("denied CRM source read"))

    result = asyncio.run(route.read_my_work(
        tenant_id="tenant-a",
        identity=_identity(),
        legal_context=None,
        operations_context=_context(),
        intelligence_context=None,
        crm_context=None,
    ))

    assert calls == [("operations", "tenant-a")]
    assert result["sources_included"] == ["OPERATIONS"]
    assert result["summary"]["active_count"] == 1
    assert result["summary"]["source_counts"] == {"OPERATIONS": 1}
    assert result["items"][0]["source"] == "OPERATIONS"
    assert result["authority"]["permits_source_commands"] is False


def test_route_fails_closed_when_an_authorized_source_reader_is_unavailable(monkeypatch):
    def unavailable(*_args, **_kwargs):
        raise HTTPException(status_code=503, detail="SOURCE_UNAVAILABLE")

    monkeypatch.setattr(route, "_read_module", unavailable)
    with pytest.raises(HTTPException) as error:
        asyncio.run(route.read_my_work(
            tenant_id="tenant-a",
            identity=_identity(),
            legal_context=None,
            operations_context=_context(),
            intelligence_context=None,
            crm_context=None,
        ))
    assert error.value.status_code == 503


def test_route_rejects_context_from_a_different_tenant_or_principal():
    with pytest.raises(HTTPException) as error:
        asyncio.run(route.read_my_work(
            tenant_id="tenant-a",
            identity=_identity(),
            legal_context=None,
            operations_context=_context(tenant="tenant-b"),
            intelligence_context=None,
            crm_context=None,
        ))
    assert error.value.status_code == 503
    assert error.value.detail == "MY_WORK_AUTHORIZATION_CONTEXT_INCONSISTENT"


def test_route_registers_four_independent_optional_iam_dependencies():
    endpoint = next(
        item.endpoint for item in route.router.routes
        if getattr(item, "name", None) == "read_my_work"
    )
    names = set(endpoint.__annotations__)
    assert "legal_context" in names
    assert "operations_context" in names
    assert "intelligence_context" in names
    assert "crm_context" in names



def test_route_rejects_whitespace_tenant_scope_before_source_reads():
    with pytest.raises(HTTPException) as error:
        asyncio.run(route.read_my_work(
            tenant_id=" tenant-a ",
            identity=_identity(),
            legal_context=None,
            operations_context=None,
            intelligence_context=None,
            crm_context=None,
        ))
    assert error.value.status_code == 403
    assert error.value.detail == "TENANT_SCOPE_REQUIRED"


def test_route_rejects_tenant_scope_when_no_source_is_authorized():
    with pytest.raises(HTTPException) as error:
        asyncio.run(route.read_my_work(
            tenant_id="foreign-tenant",
            identity=_identity(),
            legal_context=None,
            operations_context=None,
            intelligence_context=None,
            crm_context=None,
        ))
    assert error.value.status_code == 403
    assert error.value.detail == "MY_WORK_NO_AUTHORIZED_SOURCE"


def test_http_route_does_not_return_empty_success_for_unjoined_foreign_tenant():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from tools.eos.api.errors import register_error_handlers

    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(route.router, prefix="/api")
    app.dependency_overrides[route.get_current_identity] = _identity
    app.dependency_overrides[route._LEGAL_READ] = lambda: None
    app.dependency_overrides[route._OPERATIONS_READ] = lambda: None
    app.dependency_overrides[route._INTELLIGENCE_READ] = lambda: None
    app.dependency_overrides[route._CRM_READ] = lambda: None

    with TestClient(app) as client:
        response = client.get(
            "/api/my-work",
            headers={"X-Tenant-ID": "foreign-tenant"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "MY_WORK_NO_AUTHORIZED_SOURCE"



def test_http_route_omits_denied_source_and_returns_only_authorized_projection(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from tools.eos.api.errors import register_error_handlers

    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(route.router, prefix="/api")
    app.dependency_overrides[route.get_current_identity] = _identity
    app.dependency_overrides[route._LEGAL_READ] = lambda: None
    app.dependency_overrides[route._OPERATIONS_READ] = lambda: _context()
    app.dependency_overrides[route._INTELLIGENCE_READ] = lambda: None
    app.dependency_overrides[route._CRM_READ] = lambda: None
    monkeypatch.setattr(
        route,
        "_read_module",
        lambda slug, *, tenant_id: {
            "tenant_id": tenant_id,
            "items": [{
                "work_item_id": "http-ops-1",
                "title": "HTTP operations task",
                "status": "OPEN",
                "priority": "NORMAL",
            }],
        },
    )

    with TestClient(app) as client:
        response = client.get("/api/my-work", headers={"X-Tenant-ID": "tenant-a"})

    assert response.status_code == 200
    body = response.json()
    assert body["sources_included"] == ["OPERATIONS"]
    assert [item["title"] for item in body["items"]] == ["HTTP operations task"]


def test_http_route_does_not_turn_authorized_source_outage_into_empty_success(monkeypatch):
    from fastapi import FastAPI, HTTPException
    from fastapi.testclient import TestClient
    from tools.eos.api.errors import register_error_handlers

    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(route.router, prefix="/api")
    app.dependency_overrides[route.get_current_identity] = _identity
    app.dependency_overrides[route._LEGAL_READ] = lambda: None
    app.dependency_overrides[route._OPERATIONS_READ] = lambda: _context()
    app.dependency_overrides[route._INTELLIGENCE_READ] = lambda: None
    app.dependency_overrides[route._CRM_READ] = lambda: None

    def unavailable(*_args, **_kwargs):
        raise HTTPException(status_code=503, detail="SOURCE_UNAVAILABLE")

    monkeypatch.setattr(route, "_read_module", unavailable)
    with TestClient(app) as client:
        response = client.get("/api/my-work", headers={"X-Tenant-ID": "tenant-a"})

    assert response.status_code == 503



def test_module_product_entitlement_denial_omits_only_that_source(monkeypatch):
    def not_entitled(*_args, **_kwargs):
        raise HTTPException(status_code=403, detail="MODULE_WORK_PRODUCT_NOT_ENTITLED")

    monkeypatch.setattr(route.module_source, "_transaction", not_entitled)
    assert route._read_module("operations", tenant_id="tenant-a") is None


def test_crm_legal_entitlement_denial_omits_only_crm_source(monkeypatch):
    def not_entitled(*_args, **_kwargs):
        raise HTTPException(status_code=403, detail="OWNER_WORK_LEGAL_NOT_ENTITLED")

    monkeypatch.setattr(route.crm_source, "_transaction", not_entitled)
    assert route._read_crm(tenant_id="tenant-a") is None


def test_unknown_source_forbidden_and_source_outage_are_not_silently_omitted(monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise HTTPException(status_code=403, detail="UNCLASSIFIED_SOURCE_DENIAL")

    monkeypatch.setattr(route.module_source, "_transaction", forbidden)
    with pytest.raises(HTTPException) as error:
        route._read_module("operations", tenant_id="tenant-a")
    assert error.value.detail == "UNCLASSIFIED_SOURCE_DENIAL"
