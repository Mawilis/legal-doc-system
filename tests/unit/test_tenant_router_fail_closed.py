"""Sovereign route-level proof for temporary tenant authority containment."""

import asyncio
import json

from fastapi import FastAPI

from tools.eos.api.tenant_router import tenant_router
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry


def test_all_tenant_routes_deny_before_registry_access(monkeypatch):
    calls = {name: 0 for name in ("list", "get", "create", "update", "archive")}

    for name in calls:
        def forbidden(*_args, _name=name, **_kwargs):
            calls[_name] += 1
            raise AssertionError("TenantRegistry accessed before tenant authority")

        monkeypatch.setattr(TenantRegistry, name, forbidden)

    app = FastAPI()
    app.include_router(tenant_router)
    requests = [
        ("get", "/api/tenants"),
        ("post", "/api/tenants", {"name": "x"}),
        ("get", "/api/tenants/tenant-a"),
        ("put", "/api/tenants/tenant-a", {"name": "x"}),
        ("delete", "/api/tenants/tenant-a"),
    ]
    for method, path, *body in requests:
        for headers in ({}, {"X-Tenant-ID": "GLOBAL_ROOT"}, {"X-Tenant-ID": "tenant-b"}):
            status_code, payload = asyncio.run(_request(app, method, path, headers, body[0] if body else None))
            assert status_code == 503
            assert payload["detail"] == "TENANT_AUTHORITY_UNAVAILABLE"
            assert not 200 <= status_code < 300
    assert calls == {name: 0 for name in calls}


async def _request(app, method, path, headers, body):
    """Execute the actual FastAPI router through its ASGI boundary."""
    captured = {"status": 500, "body": b""}
    raw_body = json.dumps(body).encode() if body is not None else b""
    header_items = [(key.lower().encode(), value.encode()) for key, value in headers.items()]
    if body is not None:
        header_items.append((b"content-type", b"application/json"))
    messages = [{"type": "http.request", "body": raw_body, "more_body": False}]

    async def receive():
        return messages.pop(0)

    async def send(message):
        if message["type"] == "http.response.start":
            captured["status"] = message["status"]
        elif message["type"] == "http.response.body":
            captured["body"] += message.get("body", b"")

    scope = {"type": "http", "method": method.upper(), "path": path, "query_string": b"", "headers": header_items, "scheme": "http", "server": ("test", 80), "client": ("test", 1), "root_path": "", "http_version": "1.1", "asgi": {"version": "3.0", "spec_version": "2.0"}}
    await app(scope, receive, send)
    return captured["status"], json.loads(captured["body"])


# ARTIFACT: test_tenant_router_fail_closed.py
# VERSION: v1.0.0-TENANT-AUTHORITY-CONTAINMENT-CERT
# AUTHORITY BOUNDARY: certifies deny-before-registry behavior of the Python tenant router
# TENANT POSTURE: headers, roles, and target IDs cannot authorize contained routes
# FAIL-CLOSED POSTURE: every route returns bounded HTTP 503 before persistence access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
