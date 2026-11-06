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
        if getattr(item, "path", None) == ""
    )
    names = set(endpoint.__annotations__)
    assert "legal_context" in names
    assert "operations_context" in names
    assert "intelligence_context" in names
    assert "crm_context" in names
