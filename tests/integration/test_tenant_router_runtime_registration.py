# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN CERTIFICATION ARTIFACT
TENANT ROUTER — CONTROLLED GET + ARCHIVE — CANONICAL RUNTIME CERTIFICATE
===============================================================================

TITLE:
    WILSY OS Tenant Router Controlled Wiring Runtime Certification

FILE:
    tests/integration/test_tenant_router_runtime_registration.py

VERSION:
    v1.1.0-TENANT-ROUTER-CONTROLLED-WIRING-CERT

AUTHORITY:
    Wilsy OS Core Governance.
    Canonical FastAPI runtime certification of selective tenant-router activation.

EPITOME:
    Proves the tenant router remains registered exactly once with the same five
    method/path pairs; collection GET, POST, and PUT remain contained; GET detail
    requires durable tenant:profile:read/profile_read authority; DELETE detail
    requires durable tenant:lifecycle:archive/lifecycle_archive authority; exact
    X-Tenant-ID/path congruence is enforced before persistence; registry
    absence/corruption/outage semantics translate deterministically; and
    transport role/permission projections never replace durable truth.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_router_runtime_registration.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-30

CHANGELOG:
    v1.1.0-TENANT-ROUTER-CONTROLLED-WIRING-CERT
        - Evolves B2A runtime registration proof into B2B selective activation.
        - Preserves exact router registration, OpenAPI surface, application
          metadata, middleware, exception handling, and general API composition.
        - Proves three non-migrated routes remain 503 before persistence.
        - Proves authentication, explicit tenant scope, durable membership/role
          truth, and exact path/header congruence gate GET/archive persistence.
        - Proves GET 200/404/503 and DELETE 204/404/503 mappings.
        - Proves projected roles/permissions cannot substitute durable authority.

    v1.0.0-TENANT-ROUTER-RUNTIME-REGISTRATION-CERT
        - Certified exact B2A router registration while all routes were contained.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Canonical app with deterministic in-memory authority repositories and
    persistence call doubles. No production credentials or tenant data.

TENANT BOUNDARY:
    Activated requests are own-tenant only. Exact authorized X-Tenant-ID must
    equal the path tenant before persistence. Cross-tenant mismatch is denied.

AUTHORITY BOUNDARY:
    Certification evidence only. Durable authorization remains implemented by
    the frozen RequireTenantAuthorization composition; test overrides provide
    deterministic current-truth fixtures, not alternate production authority.

FINANCIAL AUTHORITY BOUNDARY:
    No financial state or execution is touched.
    Kennel EOS remains the exclusive financial execution authority.

CERTIFICATION CLASS:
    INTEGRATION / CANONICAL-ASGI / FAIL-CLOSED

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
===============================================================================
"""

from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any, Iterator, NoReturn

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

import tools.eos.api.tenant_authorization_http as boundary
from tools.eos.api.api_server import (
    VERSION as API_SERVER_VERSION,
    app,
    wilsy_exception_handler,
)
from tools.eos.api.exceptions import WilsyAPIException
from tools.eos.api.middleware import SovereignTelemetryMiddleware
from tools.eos.api.router import router as general_router
from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization
from tools.eos.api.tenant_router import (
    VERSION as TENANT_ROUTER_VERSION,
    tenant_router,
)
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
)
from tools.eos.saas.tenancy.tenant_registry import (
    TenantRegistry,
    TenantRegistryError,
)


# =============================================================================
# CERTIFICATION CONSTANTS
# =============================================================================

VERSION = "v1.1.0-TENANT-ROUTER-CONTROLLED-WIRING-CERT"
EXPECTED_API_SERVER_VERSION = "v1.2.0-TENANT-ROUTER-CONTROLLED-ACTIVATION"
EXPECTED_TENANT_ROUTER_VERSION = "v1.1.0-TENANT-GET-ARCHIVE-AUTHORITY-WIRING"

_PID = "principal-b2b"
_TENANT_A = "tenant-a"
_TENANT_B = "tenant-b"

EXPECTED_TENANT_ROUTES = Counter(
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
# DETERMINISTIC DURABLE-AUTHORITY READERS
# =============================================================================


class _RecordingReader:
    """Resolve deterministic current truth while rejecting unconfigured keys."""

    def __init__(self, values: dict[tuple[str, ...], object] | None = None) -> None:
        self.values = dict(values or {})
        self.read_calls: list[tuple[str, ...]] = []
        self.write_calls = 0

    def resolve(self, *keys: str) -> object:
        """Resolve one exact key using the repository-family not-found contract."""
        key = tuple(keys)
        self.read_calls.append(key)
        if key in self.values:
            return self.values[key]
        if len(key) == 1:
            raise PrincipalAuthorityNotFoundError(
                "PRINCIPAL_AUTHORITY_NOT_FOUND"
            )
        if len(key) == 2:
            raise TenantMembershipNotFoundError(
                "TENANT_MEMBERSHIP_NOT_FOUND"
            )
        raise RoleAssignmentNotFoundError(
            "ROLE_ASSIGNMENT_NOT_FOUND"
        )

    def _write_forbidden(self, *_args: object, **_kwargs: object) -> NoReturn:
        """Fail if authorization attempts persistence mutation."""
        self.write_calls += 1
        raise AssertionError("Authorization reader mutation attempted")

    create = _write_forbidden
    insert = _write_forbidden
    update = _write_forbidden
    replace = _write_forbidden
    replace_one = _write_forbidden
    compare_and_swap = _write_forbidden
    delete = _write_forbidden
    delete_one = _write_forbidden


# =============================================================================
# AUTHORITY FIXTURE BUILDERS
# =============================================================================


def _identity() -> SovereignIdentity:
    """Build an authenticated identity whose projections are never authority."""
    return SovereignIdentity(
        identity_id=_PID,
        tenant_id="wrong-token-tenant",
        username="b2b-user",
        email="b2b@example.test",
        auth_method="test",
        status=PrincipalStatus.ACTIVE,
        roles=["ROOT", "GLOBAL_ROOT", "ENTERPRISE_ADMIN"],
        permissions=["*", "tenant:profile:read", "tenant:lifecycle:archive"],
    )


def _principal() -> PrincipalAuthority:
    """Build active durable principal truth."""
    return PrincipalAuthority(
        _PID,
        PrincipalStatus.ACTIVE,
        0,
    )


def _membership(tenant_id: str) -> TenantMembershipAuthority:
    """Build active durable tenant-membership truth."""
    return TenantMembershipAuthority(
        _PID,
        tenant_id,
        TenantMembershipStatus.ACTIVE,
        0,
    )


def _role(tenant_id: str, role_id: str) -> RoleAssignmentAuthority:
    """Build one active durable role-assignment record."""
    return RoleAssignmentAuthority(
        _PID,
        tenant_id,
        role_id,
        RoleAssignmentStatus.ACTIVE,
        0,
    )


@contextmanager
def _authority_scope(
    tenant_id: str,
    *,
    membership_present: bool = True,
) -> Iterator[tuple[_RecordingReader, _RecordingReader, _RecordingReader]]:
    """Install bounded canonical-app dependency overrides and restore exactly."""
    previous = dict(app.dependency_overrides)

    principal_reader = _RecordingReader(
        {
            (_PID,): _principal(),
        }
    )

    membership_values: dict[tuple[str, ...], object] = {}
    if membership_present:
        membership_values[(_PID, tenant_id)] = _membership(tenant_id)
    membership_reader = _RecordingReader(membership_values)

    role_reader = _RecordingReader(
        {
            (_PID, tenant_id, "tenant_owner"): _role(
                tenant_id,
                "tenant_owner",
            ),
            (_PID, tenant_id, "ENTERPRISE_ADMIN"): _role(
                tenant_id,
                "ENTERPRISE_ADMIN",
            ),
        }
    )

    app.dependency_overrides[boundary.get_current_identity] = _identity
    app.dependency_overrides[
        boundary.get_principal_authority_repository
    ] = lambda: principal_reader
    app.dependency_overrides[
        boundary.get_tenant_membership_repository
    ] = lambda: membership_reader
    app.dependency_overrides[
        boundary.get_role_assignment_repository
    ] = lambda: role_reader

    try:
        yield principal_reader, membership_reader, role_reader
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


# =============================================================================
# ROUTE / OPENAPI INTROSPECTION
# =============================================================================


def _router_method_path_counter() -> Counter[tuple[str, str]]:
    """Return exact method/path pairs owned directly by tenant_router."""
    pairs: Counter[tuple[str, str]] = Counter()
    for route in tenant_router.routes:
        assert isinstance(route, APIRoute)
        for method in route.methods or set():
            pairs[(method, route.path)] += 1
    return pairs


def _included_router_count(target: Any) -> int:
    """Count canonical FastAPI included-router wrappers for one router object."""
    return sum(
        1
        for route in app.routes
        if getattr(route, "original_router", None) is target
    )


def _openapi_tenant_method_path_counter() -> Counter[tuple[str, str]]:
    """Return composed tenant method/path pairs from canonical OpenAPI."""
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


def _route(method: str, path: str) -> APIRoute:
    """Return the unique tenant APIRoute for one method/path."""
    matches = [
        route
        for route in tenant_router.routes
        if isinstance(route, APIRoute)
        and route.path == path
        and method in (route.methods or set())
    ]
    assert len(matches) == 1
    return matches[0]


def _auth_dependencies(route: APIRoute) -> list[RequireTenantAuthorization]:
    """Return RequireTenantAuthorization dependencies attached to a route."""
    return [
        dependant.call
        for dependant in route.dependant.dependencies
        if isinstance(dependant.call, RequireTenantAuthorization)
    ]


# =============================================================================
# RESPONSE FIXTURE
# =============================================================================


def _entity(tenant_id: str = _TENANT_A) -> Any:
    """Build the exact attribute surface consumed by TenantResponse mapping."""
    organization = SimpleNamespace(
        organization_name="Tenant A",
        legal_name="Tenant A Legal",
        tax_id="tax-a",
        contact_email="tenant-a@example.test",
        industry="Legal",
    )
    return SimpleNamespace(
        tenant_id=tenant_id,
        organization=organization,
        alias="tenant-a-alias",
        region="ZA",
        status="ACTIVE",
        subscription_tier="ENTERPRISE",
        compliance_flags={"certified": True},
        created_at="2026-08-30T00:00:00+00:00",
        proof_hash="proof-a",
        verified=True,
    )


# =============================================================================
# REGISTRATION / APPLICATION PRESERVATION
# =============================================================================


def test_versions_lock_b2b_router_into_unchanged_canonical_app() -> None:
    """B2B aligns api_server governance while preserving its composition semantics."""
    assert VERSION == "v1.1.0-TENANT-ROUTER-CONTROLLED-WIRING-CERT"
    assert API_SERVER_VERSION == EXPECTED_API_SERVER_VERSION
    assert TENANT_ROUTER_VERSION == EXPECTED_TENANT_ROUTER_VERSION


def test_tenant_router_still_owns_exactly_five_expected_routes() -> None:
    """No route is added, removed, or alternately mounted by B2B."""
    assert _router_method_path_counter() == EXPECTED_TENANT_ROUTES
    assert len(tenant_router.routes) == 5


def test_tenant_router_is_still_included_exactly_once() -> None:
    """Canonical FastAPI composition contains one tenant and one general router."""
    assert _included_router_count(tenant_router) == 1
    assert _included_router_count(general_router) == 1


def test_composed_openapi_keeps_exact_tenant_surface() -> None:
    """OpenAPI remains exactly the five tenant method/path pairs."""
    tenant_pairs = _openapi_tenant_method_path_counter()
    assert tenant_pairs == EXPECTED_TENANT_ROUTES
    assert sum(tenant_pairs.values()) == 5
    assert all(
        not path.startswith("/api/v1/api/tenants")
        for _, path in tenant_pairs
    )


def test_existing_general_application_composition_is_preserved() -> None:
    """Gateway metadata, middleware, exception handler, and general API remain."""
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


# =============================================================================
# EXACT AUTHORIZATION WIRING
# =============================================================================


def test_runtime_routes_expose_only_exact_get_and_archive_authority_pairs() -> None:
    """Only the two activated detail routes carry tenant authorization dependencies."""
    get_dependencies = _auth_dependencies(
        _route("GET", "/api/tenants/{tenant_id}")
    )
    delete_dependencies = _auth_dependencies(
        _route("DELETE", "/api/tenants/{tenant_id}")
    )

    assert len(get_dependencies) == 1
    assert get_dependencies[0].permission_id == "tenant:profile:read"
    assert get_dependencies[0].operation == "profile_read"

    assert len(delete_dependencies) == 1
    assert delete_dependencies[0].permission_id == "tenant:lifecycle:archive"
    assert delete_dependencies[0].operation == "lifecycle_archive"

    for method, path in (
        ("GET", "/api/tenants"),
        ("POST", "/api/tenants"),
        ("PUT", "/api/tenants/{tenant_id}"),
    ):
        assert _auth_dependencies(_route(method, path)) == []


# =============================================================================
# NON-MIGRATED ROUTE CONTAINMENT
# =============================================================================


def test_non_migrated_routes_remain_503_before_registry_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Collection GET, POST, and PUT still cannot reach any registry method."""
    calls: Counter[str] = Counter()

    for name in ("list", "get", "create", "update", "archive"):

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

    headers = {
        "X-Tenant-ID": _TENANT_A,
        "X-Role": "GLOBAL_ROOT",
        "X-Permissions": "*",
    }

    with TestClient(app) as client:
        for method, path, body in CONTAINED_REQUESTS:
            response = client.request(
                method,
                path,
                headers=headers,
                json=body,
            )
            assert response.status_code == 503
            assert response.json() == {
                "detail": "TENANT_AUTHORITY_UNAVAILABLE"
            }

    assert calls == Counter()


# =============================================================================
# AUTHENTICATION / SCOPE / DURABLE-TRUTH GATES
# =============================================================================


def test_detail_routes_require_authentication_before_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fabricated transport projections cannot activate GET or DELETE."""
    def forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("Registry accessed without authentication")

    monkeypatch.setattr(TenantRegistry, "get", forbidden)
    monkeypatch.setattr(TenantRegistry, "archive", forbidden)

    headers = {
        "X-Tenant-ID": _TENANT_A,
        "X-Role": "ENTERPRISE_ADMIN",
        "X-Permissions": "tenant:profile:read,tenant:lifecycle:archive",
        "Authorization": "Bearer definitely-invalid-token",
    }

    with TestClient(app) as client:
        get_response = client.get(
            f"/api/tenants/{_TENANT_A}",
            headers=headers,
        )
        delete_response = client.delete(
            f"/api/tenants/{_TENANT_A}",
            headers=headers,
        )

    assert get_response.status_code == 401
    assert delete_response.status_code == 401


def test_explicit_tenant_scope_is_required_before_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authenticated callers still require an explicit X-Tenant-ID scope."""
    def forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("Registry accessed without explicit tenant scope")

    monkeypatch.setattr(TenantRegistry, "get", forbidden)
    monkeypatch.setattr(TenantRegistry, "archive", forbidden)

    with _authority_scope(_TENANT_A):
        with TestClient(app) as client:
            get_response = client.get(f"/api/tenants/{_TENANT_A}")
            delete_response = client.delete(f"/api/tenants/{_TENANT_A}")

    assert get_response.status_code == 403
    assert delete_response.status_code == 403


def test_durable_membership_cannot_be_replaced_by_projected_roles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Identity/header role and permission projections cannot replace membership."""
    def forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("Registry accessed without durable membership")

    monkeypatch.setattr(TenantRegistry, "get", forbidden)
    monkeypatch.setattr(TenantRegistry, "archive", forbidden)

    headers = {
        "X-Tenant-ID": _TENANT_A,
        "X-Role": "GLOBAL_ROOT",
        "X-Permissions": "*",
    }

    with _authority_scope(_TENANT_A, membership_present=False):
        with TestClient(app) as client:
            get_response = client.get(
                f"/api/tenants/{_TENANT_A}",
                headers=headers,
            )
            delete_response = client.delete(
                f"/api/tenants/{_TENANT_A}",
                headers=headers,
            )

    assert get_response.status_code == 403
    assert delete_response.status_code == 403


def test_authorized_header_scope_must_equal_path_before_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authorization for tenant-b cannot be used against tenant-a path persistence."""
    calls: Counter[str] = Counter()

    def get_forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        calls["get"] += 1
        raise AssertionError("GET persistence reached after scope mismatch")

    def archive_forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        calls["archive"] += 1
        raise AssertionError("archive persistence reached after scope mismatch")

    monkeypatch.setattr(TenantRegistry, "get", get_forbidden)
    monkeypatch.setattr(TenantRegistry, "archive", archive_forbidden)

    headers = {"X-Tenant-ID": _TENANT_B}

    with _authority_scope(_TENANT_B):
        with TestClient(app) as client:
            get_response = client.get(
                f"/api/tenants/{_TENANT_A}",
                headers=headers,
            )
            delete_response = client.delete(
                f"/api/tenants/{_TENANT_A}",
                headers=headers,
            )

    assert get_response.status_code == 403
    assert get_response.json() == {
        "detail": "TENANT_SCOPE_PATH_MISMATCH"
    }
    assert delete_response.status_code == 403
    assert delete_response.json() == {
        "detail": "TENANT_SCOPE_PATH_MISMATCH"
    }
    assert calls == Counter()


# =============================================================================
# AUTHORIZED GET CONTRACT
# =============================================================================


def test_authorized_get_returns_bounded_tenant_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exact durable authority reaches one registry GET and returns HTTP 200."""
    calls: list[str] = []

    def get_one(tenant_id: str) -> Any:
        calls.append(tenant_id)
        return _entity(tenant_id)

    monkeypatch.setattr(
        TenantRegistry,
        "get",
        staticmethod(get_one),
    )

    with _authority_scope(_TENANT_A) as readers:
        with TestClient(app) as client:
            response = client.get(
                f"/api/tenants/{_TENANT_A}",
                headers={"X-Tenant-ID": _TENANT_A},
            )

    assert response.status_code == 200
    assert response.json() == {
        "tenant_id": _TENANT_A,
        "alias": "tenant-a-alias",
        "name": "Tenant A",
        "legal_name": "Tenant A Legal",
        "tax_id": "tax-a",
        "contact_email": "tenant-a@example.test",
        "industry": "Legal",
        "region": "ZA",
        "sector": None,
        "status": "ACTIVE",
        "subscription_tier": "ENTERPRISE",
        "compliance_flags": {"certified": True},
        "created_at": "2026-08-30T00:00:00+00:00",
        "updated_at": None,
        "proof_hash": "proof-a",
        "verified": True,
    }
    assert calls == [_TENANT_A]
    assert all(reader.write_calls == 0 for reader in readers)


def test_authorized_get_maps_absence_and_registry_failures_exactly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GET distinguishes 404 absence from both explicit 503 registry failures."""
    cases: tuple[
        tuple[object, int, str],
        ...,
    ] = (
        (
            None,
            404,
            "Tenant not found.",
        ),
        (
            TenantRegistryError(
                "TENANT_REGISTRY_GET_INVALID_DOCUMENT"
            ),
            503,
            "TENANT_REGISTRY_GET_INVALID_DOCUMENT",
        ),
        (
            TenantRegistryError(
                "TENANT_REGISTRY_GET_UNAVAILABLE"
            ),
            503,
            "TENANT_REGISTRY_GET_UNAVAILABLE",
        ),
    )

    for outcome, expected_status, expected_detail in cases:
        with monkeypatch.context() as scoped:
            if isinstance(outcome, Exception):

                def get_failure(
                    _tenant_id: str,
                    *,
                    _error: Exception = outcome,
                ) -> NoReturn:
                    raise _error

                scoped.setattr(
                    TenantRegistry,
                    "get",
                    staticmethod(get_failure),
                )
            else:
                scoped.setattr(
                    TenantRegistry,
                    "get",
                    staticmethod(lambda _tenant_id, _outcome=outcome: _outcome),
                )

            with _authority_scope(_TENANT_A):
                with TestClient(app) as client:
                    response = client.get(
                        f"/api/tenants/{_TENANT_A}",
                        headers={"X-Tenant-ID": _TENANT_A},
                    )

        assert response.status_code == expected_status
        assert response.json() == {"detail": expected_detail}


# =============================================================================
# AUTHORIZED ARCHIVE CONTRACT
# =============================================================================


def test_authorized_delete_calls_archive_only_and_returns_204(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DELETE performs only the archive registry operation for exact own tenant."""
    archive_calls: list[str] = []

    def archive_one(tenant_id: str) -> bool:
        archive_calls.append(tenant_id)
        return True

    def get_forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("DELETE route attempted registry GET")

    monkeypatch.setattr(
        TenantRegistry,
        "archive",
        staticmethod(archive_one),
    )
    monkeypatch.setattr(
        TenantRegistry,
        "get",
        staticmethod(get_forbidden),
    )

    with _authority_scope(_TENANT_A) as readers:
        with TestClient(app) as client:
            response = client.delete(
                f"/api/tenants/{_TENANT_A}",
                headers={"X-Tenant-ID": _TENANT_A},
            )

    assert response.status_code == 204
    assert response.content == b""
    assert archive_calls == [_TENANT_A]
    assert all(reader.write_calls == 0 for reader in readers)


def test_authorized_delete_maps_no_change_and_outage_exactly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Archive False remains historical 404; registry outage becomes exact 503."""
    cases: tuple[
        tuple[object, int, str],
        ...,
    ] = (
        (
            False,
            404,
            "Tenant not found or already archived.",
        ),
        (
            TenantRegistryError(
                "TENANT_REGISTRY_ARCHIVE_UNAVAILABLE"
            ),
            503,
            "TENANT_REGISTRY_ARCHIVE_UNAVAILABLE",
        ),
    )

    for outcome, expected_status, expected_detail in cases:
        with monkeypatch.context() as scoped:
            if isinstance(outcome, Exception):

                def archive_failure(
                    _tenant_id: str,
                    *,
                    _error: Exception = outcome,
                ) -> NoReturn:
                    raise _error

                scoped.setattr(
                    TenantRegistry,
                    "archive",
                    staticmethod(archive_failure),
                )
            else:
                scoped.setattr(
                    TenantRegistry,
                    "archive",
                    staticmethod(lambda _tenant_id, _outcome=outcome: _outcome),
                )

            with _authority_scope(_TENANT_A):
                with TestClient(app) as client:
                    response = client.delete(
                        f"/api/tenants/{_TENANT_A}",
                        headers={"X-Tenant-ID": _TENANT_A},
                    )

        assert response.status_code == expected_status
        assert response.json() == {"detail": expected_detail}


# =============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_tenant_router_runtime_registration.py
# VERSION: v1.1.0-TENANT-ROUTER-CONTROLLED-WIRING-CERT
# AUTHORITY BOUNDARY: canonical runtime evidence only; production authority remains frozen durable principal, membership, business-role, permission, and role-assignment composition
# TENANT POSTURE: only exact own-tenant GET/profile_read and DELETE/lifecycle_archive can reach registry; scope/path mismatch denies before persistence; collection GET, POST, and PUT remain contained
# FAIL-CLOSED POSTURE: missing authentication/scope/durable membership denies; absence is 404; invalid persisted GET truth and registry outages are 503; archive no-change is 404
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
