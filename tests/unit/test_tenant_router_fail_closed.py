# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN CERTIFICATION ARTIFACT
TENANT ROUTER — SELECTIVE CONTAINMENT + AUTHORITY BINDINGS — UNIT CERTIFICATE
===============================================================================

TITLE:
    WILSY OS Tenant Router Selective Containment Unit Certification

FILE:
    tests/unit/test_tenant_router_fail_closed.py

VERSION:
    v1.1.0-TENANT-SELECTIVE-AUTHORITY-CONTAINMENT-CERT

AUTHORITY:
    Wilsy OS Core Governance.
    Deterministic unit certification of tenant-router route ownership,
    selective containment, and exact authorization dependency bindings.

EPITOME:
    Proves the tenant router still owns exactly five routes; collection GET,
    POST create, and PUT mutation remain 503-contained before registry access;
    GET detail is bound only to tenant:profile:read + profile_read; DELETE detail
    is bound only to tenant:lifecycle:archive + lifecycle_archive; and contained
    routes have no authorization dependency that could accidentally activate
    persistence.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_router_fail_closed.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-30

CHANGELOG:
    v1.1.0-TENANT-SELECTIVE-AUTHORITY-CONTAINMENT-CERT
        - Evolves the B2A all-route containment certificate for B2B.
        - Locks exact GET and DELETE authorization dependencies.
        - Preserves fail-closed collection GET, POST, and PUT behavior.
        - Proves contained routes cannot access any TenantRegistry method.

    v1.0.0-TENANT-AUTHORITY-CONTAINMENT-CERT
        - Certified all five tenant routes as contained before B2B activation.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Test-local ASGI requests and deterministic persistence tripwires only.
    No production data, credentials, durable authority mutation, or network
    access.

TENANT BOUNDARY:
    Activated detail-route dependencies are exact own-tenant vocabulary.
    Non-migrated routes remain unavailable independent of supplied headers.

AUTHORITY BOUNDARY:
    Evidence only. The certificate does not authenticate, authorize, assign
    roles, establish membership, mutate persistence, or grant financial authority.

FINANCIAL AUTHORITY BOUNDARY:
    No financial state or execution is touched.
    Kennel EOS remains the exclusive financial execution authority.

CERTIFICATION CLASS:
    UNIT / DETERMINISTIC / FAIL-CLOSED

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
===============================================================================
"""

from __future__ import annotations

import json
from collections import Counter
from typing import Any, NoReturn

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.types import Message, Scope

from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization
from tools.eos.api.tenant_router import VERSION as TENANT_ROUTER_VERSION
from tools.eos.api.tenant_router import tenant_router
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry


# =============================================================================
# CERTIFICATION CONSTANTS
# =============================================================================

VERSION = "v1.1.0-TENANT-SELECTIVE-AUTHORITY-CONTAINMENT-CERT"
EXPECTED_ROUTER_VERSION = "v1.1.0-TENANT-GET-ARCHIVE-AUTHORITY-WIRING"

EXPECTED_ROUTES = Counter(
    {
        ("GET", "/api/tenants"): 1,
        ("POST", "/api/tenants"): 1,
        ("GET", "/api/tenants/{tenant_id}"): 1,
        ("PUT", "/api/tenants/{tenant_id}"): 1,
        ("DELETE", "/api/tenants/{tenant_id}"): 1,
    }
)

CONTAINED_REQUESTS: tuple[
    tuple[str, str, dict[str, Any] | None],
    ...,
] = (
    ("GET", "/api/tenants", None),
    ("POST", "/api/tenants", {"name": "Tenant A"}),
    ("PUT", "/api/tenants/tenant-a", {"name": "Tenant A"}),
)


# =============================================================================
# ROUTE / DEPENDENCY INTROSPECTION
# =============================================================================


def _route(method: str, path: str) -> APIRoute:
    """Return the unique tenant APIRoute for one exact method/path pair."""
    matches = [
        route
        for route in tenant_router.routes
        if isinstance(route, APIRoute)
        and route.path == path
        and method in (route.methods or set())
    ]
    assert len(matches) == 1
    return matches[0]


def _tenant_authorization_dependencies(route: APIRoute) -> list[RequireTenantAuthorization]:
    """Return only RequireTenantAuthorization dependencies attached to a route."""
    dependencies: list[RequireTenantAuthorization] = []
    for dependant in route.dependant.dependencies:
        call = dependant.call
        if isinstance(call, RequireTenantAuthorization):
            dependencies.append(call)
    return dependencies


def _route_counter() -> Counter[tuple[str, str]]:
    """Return exact method/path ownership for the tenant APIRouter."""
    result: Counter[tuple[str, str]] = Counter()
    for route in tenant_router.routes:
        assert isinstance(route, APIRoute)
        for method in route.methods or set():
            result[(method, route.path)] += 1
    return result


# =============================================================================
# VERSION / ROUTE SURFACE CERTIFICATION
# =============================================================================


def test_version_and_exact_five_route_surface() -> None:
    """B2B keeps the exact five-path HTTP surface while changing only semantics."""
    assert VERSION == "v1.1.0-TENANT-SELECTIVE-AUTHORITY-CONTAINMENT-CERT"
    assert TENANT_ROUTER_VERSION == EXPECTED_ROUTER_VERSION
    assert _route_counter() == EXPECTED_ROUTES
    assert len(tenant_router.routes) == 5


# =============================================================================
# EXACT AUTHORIZATION BINDING CERTIFICATION
# =============================================================================


def test_get_detail_has_exact_profile_read_authorization_dependency() -> None:
    """GET detail is wired only to the canonical profile-read pair."""
    dependencies = _tenant_authorization_dependencies(
        _route("GET", "/api/tenants/{tenant_id}")
    )
    assert len(dependencies) == 1
    dependency = dependencies[0]
    assert dependency.permission_id == "tenant:profile:read"
    assert dependency.operation == "profile_read"


def test_delete_detail_has_exact_lifecycle_archive_authorization_dependency() -> None:
    """DELETE detail is wired only to the canonical archive pair."""
    dependencies = _tenant_authorization_dependencies(
        _route("DELETE", "/api/tenants/{tenant_id}")
    )
    assert len(dependencies) == 1
    dependency = dependencies[0]
    assert dependency.permission_id == "tenant:lifecycle:archive"
    assert dependency.operation == "lifecycle_archive"


def test_non_migrated_routes_have_no_tenant_authorization_dependency() -> None:
    """Collection GET, POST, and PUT cannot accidentally activate via auth wiring."""
    for method, path in (
        ("GET", "/api/tenants"),
        ("POST", "/api/tenants"),
        ("PUT", "/api/tenants/{tenant_id}"),
    ):
        assert _tenant_authorization_dependencies(_route(method, path)) == []


# =============================================================================
# SELECTIVE CONTAINMENT RUNTIME CERTIFICATION
# =============================================================================


def test_non_migrated_routes_deny_before_all_registry_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """All three non-migrated routes remain exact 503 before persistence."""
    calls = {
        name: 0
        for name in ("list", "get", "create", "update", "archive")
    }

    for name in calls:

        def forbidden(
            *_args: object,
            _name: str = name,
            **_kwargs: object,
        ) -> NoReturn:
            calls[_name] += 1
            raise AssertionError(
                f"TenantRegistry.{_name} accessed by contained route"
            )

        monkeypatch.setattr(TenantRegistry, name, forbidden)

    app = FastAPI()
    app.include_router(tenant_router)

    for method, path, body in CONTAINED_REQUESTS:
        for headers in (
            {},
            {"X-Tenant-ID": "tenant-a"},
            {
                "X-Tenant-ID": "GLOBAL_ROOT",
                "X-Role": "ENTERPRISE_ADMIN",
                "X-Permissions": "*",
            },
        ):
            status_code, payload = _run_request(
                app,
                method,
                path,
                headers,
                body,
            )
            assert status_code == 503
            assert payload == {"detail": "TENANT_AUTHORITY_UNAVAILABLE"}

    assert calls == {
        name: 0
        for name in ("list", "get", "create", "update", "archive")
    }


# =============================================================================
# TEST-LOCAL ASGI DRIVER
# =============================================================================


def _run_request(
    app: FastAPI,
    method: str,
    path: str,
    headers: dict[str, str],
    body: dict[str, Any] | None,
) -> tuple[int, dict[str, Any]]:
    """Execute one actual ASGI request without external network access."""
    import asyncio

    return asyncio.run(
        _request(
            app,
            method,
            path,
            headers,
            body,
        )
    )


async def _request(
    app: FastAPI,
    method: str,
    path: str,
    headers: dict[str, str],
    body: dict[str, Any] | None,
) -> tuple[int, dict[str, Any]]:
    """Drive one FastAPI request through the ASGI boundary."""
    captured: dict[str, Any] = {
        "status": 500,
        "body": b"",
    }
    raw_body = (
        json.dumps(body).encode("utf-8")
        if body is not None
        else b""
    )
    header_items = [
        (key.lower().encode("utf-8"), value.encode("utf-8"))
        for key, value in headers.items()
    ]
    if body is not None:
        header_items.append((b"content-type", b"application/json"))

    messages: list[Message] = [
        {
            "type": "http.request",
            "body": raw_body,
            "more_body": False,
        }
    ]

    async def receive() -> Message:
        return messages.pop(0)

    async def send(message: Message) -> None:
        if message["type"] == "http.response.start":
            captured["status"] = message["status"]
        elif message["type"] == "http.response.body":
            captured["body"] += message.get("body", b"")

    scope: Scope = {
        "type": "http",
        "method": method,
        "path": path,
        "query_string": b"",
        "headers": header_items,
        "scheme": "http",
        "server": ("test", 80),
        "client": ("test", 1),
        "root_path": "",
        "http_version": "1.1",
        "asgi": {
            "version": "3.0",
            "spec_version": "2.0",
        },
    }

    await app(scope, receive, send)

    payload = (
        json.loads(captured["body"])
        if captured["body"]
        else {}
    )
    return int(captured["status"]), payload


# =============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_tenant_router_fail_closed.py
# VERSION: v1.1.0-TENANT-SELECTIVE-AUTHORITY-CONTAINMENT-CERT
# AUTHORITY BOUNDARY: unit evidence for exact route dependencies and containment only; no authentication, membership, role, permission, persistence, or financial authority
# TENANT POSTURE: GET detail binds profile_read; DELETE detail binds lifecycle_archive; global list, create, and PUT remain unavailable independent of transport projections
# FAIL-CLOSED POSTURE: non-migrated routes return exact 503 TENANT_AUTHORITY_UNAVAILABLE before any TenantRegistry method; activated-route authority dependencies are exact and singular
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
