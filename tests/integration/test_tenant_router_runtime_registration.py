"""TITLE: WILSY OS Tenant Router Runtime Registration Certification.
VERSION: v1.0.0-TENANT-ROUTER-RUNTIME-REGISTRATION-CERT
AUTHORITY: Runtime certification of canonical FastAPI tenant-router registration and preserved containment.
EPITOME: Proves the frozen five-route tenant surface is registered exactly once in api_server, remains HTTP 503 fail-closed, never reaches TenantRegistry, and cannot be activated by transport projections.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_router_runtime_registration.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.0 establishes FastAPI included-router identity, OpenAPI method/path enumeration, actual HTTP containment, registry non-access, transport non-authority, and existing-router preservation proof for 3K2.8B2A.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Runtime composition proof only; no production tenant data, credentials, persistence mutation, or authority grants are created.
TENANT BOUNDARY: Only the frozen /api/tenants method/path pairs are certified; exact target paths remain contained and no alternate tenant mount is accepted.
AUTHORITY BOUNDARY: Registration evidence only; headers, JWT projections, caller roles, permissions, and application composition never grant tenant authority.
FINANCIAL AUTHORITY BOUNDARY: No financial state or execution is touched. Kennel EOS remains exclusive.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, NoReturn

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from tools.eos.api.api_server import (
    VERSION as API_SERVER_VERSION,
    app,
    wilsy_exception_handler,
)
from tools.eos.api.exceptions import WilsyAPIException
from tools.eos.api.middleware import SovereignTelemetryMiddleware
from tools.eos.api.router import router as general_router
from tools.eos.api.tenant_router import (
    VERSION as TENANT_ROUTER_VERSION,
    tenant_router,
)
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry

VERSION = "v1.0.0-TENANT-ROUTER-RUNTIME-REGISTRATION-CERT"
EXPECTED_API_SERVER_VERSION = "v1.1.0-TENANT-ROUTER-RUNTIME-REGISTRATION"
EXPECTED_TENANT_ROUTER_VERSION = "v1.0.4-TENANT-AUTHORITY-CONTAINMENT"

EXPECTED_TENANT_ROUTES = Counter(
    {
        ("GET", "/api/tenants"): 1,
        ("POST", "/api/tenants"): 1,
        ("GET", "/api/tenants/{tenant_id}"): 1,
        ("PUT", "/api/tenants/{tenant_id}"): 1,
        ("DELETE", "/api/tenants/{tenant_id}"): 1,
    }
)

REQUEST_MATRIX: tuple[tuple[str, str, dict[str, Any] | None], ...] = (
    ("GET", "/api/tenants", None),
    ("POST", "/api/tenants", {"name": "Tenant A"}),
    ("GET", "/api/tenants/tenant-a", None),
    ("PUT", "/api/tenants/tenant-a", {}),
    ("DELETE", "/api/tenants/tenant-a", None),
)


def _router_method_path_counter() -> Counter[tuple[str, str]]:
    """Return method/path pairs owned directly by the frozen tenant APIRouter."""
    pairs: Counter[tuple[str, str]] = Counter()
    for route in tenant_router.routes:
        assert isinstance(route, APIRoute)
        for method in route.methods or ():
            pairs[(method, route.path)] += 1
    return pairs


def _included_router_count(target: Any) -> int:
    """Count canonical FastAPI lazy included-router wrappers for one router object."""
    return sum(
        1
        for route in app.routes
        if getattr(route, "original_router", None) is target
    )


def _openapi_tenant_method_path_counter() -> Counter[tuple[str, str]]:
    """Return composed tenant method/path pairs from canonical generated OpenAPI."""
    pairs: Counter[tuple[str, str]] = Counter()
    schema = app.openapi()
    for path, operations in schema["paths"].items():
        if not path.startswith("/api/tenants"):
            continue
        for method in operations:
            upper = method.upper()
            if upper in {"GET", "POST", "PUT", "DELETE"}:
                pairs[(upper, path)] += 1
    return pairs


def _assert_contained(response: Any) -> None:
    """Assert the frozen runtime containment response exactly."""
    assert response.status_code == 503
    assert response.json() == {"detail": "TENANT_AUTHORITY_UNAVAILABLE"}


def test_versions_lock_registered_app_to_frozen_tenant_router() -> None:
    """The governed app version and frozen contained router version are exact."""
    assert VERSION == "v1.0.0-TENANT-ROUTER-RUNTIME-REGISTRATION-CERT"
    assert API_SERVER_VERSION == EXPECTED_API_SERVER_VERSION
    assert TENANT_ROUTER_VERSION == EXPECTED_TENANT_ROUTER_VERSION


def test_frozen_tenant_router_owns_exactly_five_expected_routes() -> None:
    """The byte-frozen router itself still owns the exact governed method/path surface."""
    assert _router_method_path_counter() == EXPECTED_TENANT_ROUTES
    assert len(tenant_router.routes) == 5


def test_tenant_router_is_included_exactly_once_in_canonical_app() -> None:
    """FastAPI lazy router composition contains exactly one tenant-router wrapper."""
    assert _included_router_count(tenant_router) == 1
    assert _included_router_count(general_router) == 1


def test_composed_openapi_exposes_exact_tenant_surface_without_alternate_mount() -> None:
    """Canonical composed paths are exactly the five tenant routes and no /api/v1 duplicate."""
    tenant_pairs = _openapi_tenant_method_path_counter()

    assert tenant_pairs == EXPECTED_TENANT_ROUTES
    assert sum(tenant_pairs.values()) == 5
    assert all(
        not path.startswith("/api/v1/api/tenants")
        for _, path in tenant_pairs
    )


def test_existing_general_application_composition_is_preserved() -> None:
    """Existing gateway metadata, middleware, exception handling, and /api/v1 surface remain."""
    assert app.title == "Wilsy OS Kernel Gateway API"
    assert (
        app.description
        == "Institutional REST API exposing every Wilsy OS kernel capability for Platform 1.0."
    )
    assert app.version == "1.0.0"
    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"
    assert any(
        getattr(middleware, "cls", None) is SovereignTelemetryMiddleware
        for middleware in app.user_middleware
    )
    assert app.exception_handlers.get(WilsyAPIException) is wilsy_exception_handler

    schema_paths = app.openapi()["paths"]
    assert "/" in schema_paths
    assert "/api/v1/kernel" in schema_paths


def test_all_registered_tenant_routes_remain_503_before_registry_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Actual canonical-app HTTP requests deny before every TenantRegistry method."""
    calls: Counter[str] = Counter()

    for name in ("list", "get", "create", "update", "archive"):

        def forbidden(
            *_args: Any,
            _name: str = name,
            **_kwargs: Any,
        ) -> NoReturn:
            calls[_name] += 1
            raise AssertionError(
                f"TenantRegistry.{_name} accessed before tenant authority"
            )

        monkeypatch.setattr(TenantRegistry, name, forbidden)

    with TestClient(app) as client:
        for method, path, body in REQUEST_MATRIX:
            response = client.request(method, path, json=body)
            _assert_contained(response)

    assert calls == Counter()


def test_transport_projections_cannot_activate_registered_tenant_routes() -> None:
    """Spoofed tenant, JWT, role, and permission projections remain non-authoritative."""
    headers = {
        "X-Tenant-ID": "tenant-a",
        "Authorization": "Bearer fabricated",
        "X-Role": "GLOBAL_ROOT",
        "X-Permissions": "tenant:profile:read",
    }

    with TestClient(app) as client:
        for method, path, body in REQUEST_MATRIX:
            response = client.request(
                method,
                path,
                headers=headers,
                json=body,
            )
            _assert_contained(response)


def test_enterprise_admin_projection_cannot_change_containment_status() -> None:
    """An enterprise-admin caller projection is not tenant authorization authority."""
    with TestClient(app) as client:
        for method, path, body in REQUEST_MATRIX:
            response = client.request(
                method,
                path,
                headers={"X-Role": "ENTERPRISE_ADMIN"},
                json=body,
            )
            assert response.status_code not in {200, 201, 204, 401, 403, 422}
            _assert_contained(response)


# ARTIFACT: test_tenant_router_runtime_registration.py
# VERSION: v1.0.0-TENANT-ROUTER-RUNTIME-REGISTRATION-CERT
# AUTHORITY BOUNDARY: canonical FastAPI registration certification only; no authentication, membership, role, permission, or transport authority
# TENANT POSTURE: the frozen /api/tenants router is included exactly once and exposes exactly five composed method/path pairs while remaining contained
# FAIL-CLOSED POSTURE: actual HTTP requests, including spoofed transport projections, deterministically return 503 TENANT_AUTHORITY_UNAVAILABLE before registry access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
