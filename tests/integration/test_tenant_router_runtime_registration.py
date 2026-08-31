# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN CERTIFICATION ARTIFACT
TENANT ROUTER — C2 CONTROLLED PROFILE UPDATE — CANONICAL RUNTIME CERTIFICATE
===============================================================================

TITLE:
    WILSY OS Tenant Router C2 Controlled Profile Update Runtime Certification

FILE:
    tests/integration/test_tenant_router_runtime_registration.py

VERSION:
    v1.2.0-TENANT-ROUTER-PROFILE-UPDATE-WIRING-CERT

AUTHORITY:
    Wilsy OS Core Governance.
    Canonical FastAPI runtime certification of C2 tenant-router activation.

EPITOME:
    Proves the canonical app retains the exact five-route tenant surface and
    exactly-one router registration; collection GET and POST remain contained;
    GET, strict PUT, and DELETE require exact frozen authorization pairs; exact
    X-Tenant-ID/path congruence gates persistence; strict PUT uses only
    update_profile; schema widening cannot reach persistence; response sector is
    durable; and 200/403/404/422/503 translations remain deterministic.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_router_runtime_registration.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-31

CHANGELOG:
    v1.2.0-TENANT-ROUTER-PROFILE-UPDATE-WIRING-CERT
        - Evolves B2B runtime certification for controlled profile PUT.
        - Preserves router registration, OpenAPI surface, general application
          composition, GET behavior, archive behavior, and transport non-authority.
        - Proves PUT write authorization, strict field shape, scope congruence,
          update_profile-only persistence, absence, field rejection, empty input,
          registry failure translation, and durable sector response.
        - Preserves collection GET and POST containment.

    v1.1.0-TENANT-ROUTER-CONTROLLED-WIRING-CERT
        - Certified B2B GET/archive activation with PUT still contained.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Canonical app with deterministic in-memory current-truth repositories and
    bounded persistence doubles. Identity/header projections never substitute for
    durable principal, membership, business-role, or permission truth.

TENANT BOUNDARY:
    All activated detail operations are exact own-tenant only. Authorized
    X-Tenant-ID must equal the path tenant before registry access.

AUTHORITY BOUNDARY:
    Certification evidence only. Production authentication and authorization code
    is used as wired; test overrides provide deterministic repository truth and do
    not create alternate authority.

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
    TenantUpdateRequest,
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


VERSION = "v1.2.0-TENANT-ROUTER-PROFILE-UPDATE-WIRING-CERT"
EXPECTED_API_SERVER_VERSION = (
    "v1.3.0-TENANT-PROFILE-UPDATE-CONTROLLED-ACTIVATION"
)
EXPECTED_TENANT_ROUTER_VERSION = (
    "v1.2.0-TENANT-PROFILE-UPDATE-AUTHORITY-WIRING"
)

_PID = "principal-c2"
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


class _RecordingReader:
    """Resolve deterministic current truth while forbidding authority mutation."""

    def __init__(
        self,
        values: dict[tuple[str, ...], object] | None = None,
    ) -> None:
        self.values = dict(values or {})
        self.read_calls: list[tuple[str, ...]] = []
        self.write_calls = 0

    def resolve(self, *keys: str) -> object:
        """Resolve one exact key using repository-family not-found semantics."""
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

    def _write_forbidden(
        self,
        *_args: object,
        **_kwargs: object,
    ) -> NoReturn:
        """Fail if authorization attempts repository mutation."""
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


def _identity() -> SovereignIdentity:
    """Build authenticated identity projections that remain non-authority."""
    return SovereignIdentity(
        identity_id=_PID,
        tenant_id="wrong-token-tenant",
        username="c2-user",
        email="c2@example.test",
        auth_method="test",
        status=PrincipalStatus.ACTIVE,
        roles=["ROOT", "GLOBAL_ROOT", "ENTERPRISE_ADMIN"],
        permissions=[
            "*",
            "tenant:profile:read",
            "tenant:profile:write",
            "tenant:lifecycle:archive",
        ],
    )


def _principal() -> PrincipalAuthority:
    """Build active durable principal truth."""
    return PrincipalAuthority(
        _PID,
        PrincipalStatus.ACTIVE,
        0,
    )


def _membership(tenant_id: str) -> TenantMembershipAuthority:
    """Build active durable membership truth."""
    return TenantMembershipAuthority(
        _PID,
        tenant_id,
        TenantMembershipStatus.ACTIVE,
        0,
    )


def _role(tenant_id: str, role_id: str) -> RoleAssignmentAuthority:
    """Build one active durable role assignment."""
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
) -> Iterator[
    tuple[_RecordingReader, _RecordingReader, _RecordingReader]
]:
    """Install bounded canonical-app authority fixtures and restore exactly."""
    previous = dict(app.dependency_overrides)

    principal_reader = _RecordingReader(
        {(_PID,): _principal()}
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


def _router_method_path_counter() -> Counter[tuple[str, str]]:
    """Return exact method/path pairs owned directly by tenant_router."""
    pairs: Counter[tuple[str, str]] = Counter()
    for route in tenant_router.routes:
        assert isinstance(route, APIRoute)
        for method in route.methods or set():
            pairs[(method, route.path)] += 1
    return pairs


def _included_router_count(target: Any) -> int:
    """Count canonical included-router wrappers for one router object."""
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
    """Return the unique tenant route for one exact pair."""
    matches = [
        route
        for route in tenant_router.routes
        if isinstance(route, APIRoute)
        and route.path == path
        and method in (route.methods or set())
    ]
    assert len(matches) == 1
    return matches[0]


def _auth_dependencies(
    route: APIRoute,
) -> list[RequireTenantAuthorization]:
    """Return governed tenant authorization dependencies attached to a route."""
    return [
        dependant.call
        for dependant in route.dependant.dependencies
        if isinstance(dependant.call, RequireTenantAuthorization)
    ]


def _entity(
    tenant_id: str = _TENANT_A,
    *,
    name: str = "Tenant A",
    sector: str = "RegTech",
) -> Any:
    """Build the exact attribute surface consumed by TenantResponse mapping."""
    organization = SimpleNamespace(
        organization_name=name,
        legal_name=f"{name} Legal",
        tax_id="tax-a",
        contact_email="tenant-a@example.test",
        industry="Legal",
    )
    return SimpleNamespace(
        tenant_id=tenant_id,
        organization=organization,
        alias="tenant-a-alias",
        region="ZA",
        sector=sector,
        status="ACTIVE",
        subscription_tier="ENTERPRISE",
        compliance_flags={"certified": True},
        created_at="2026-08-31T00:00:00+00:00",
        proof_hash="proof-a",
        verified=True,
    )


def test_versions_lock_c2_into_unchanged_canonical_app() -> None:
    """C2 advances governance versions while preserving app composition."""
    assert VERSION == "v1.2.0-TENANT-ROUTER-PROFILE-UPDATE-WIRING-CERT"
    assert API_SERVER_VERSION == EXPECTED_API_SERVER_VERSION
    assert TENANT_ROUTER_VERSION == EXPECTED_TENANT_ROUTER_VERSION


def test_tenant_router_still_owns_exactly_five_expected_routes() -> None:
    """No route is added, removed, or alternately mounted."""
    assert _router_method_path_counter() == EXPECTED_TENANT_ROUTES
    assert len(tenant_router.routes) == 5


def test_tenant_router_is_still_included_exactly_once() -> None:
    """Canonical application contains one tenant and one general router."""
    assert _included_router_count(tenant_router) == 1
    assert _included_router_count(general_router) == 1


def test_composed_openapi_keeps_exact_tenant_surface() -> None:
    """OpenAPI retains exactly the five tenant method/path pairs."""
    tenant_pairs = _openapi_tenant_method_path_counter()
    assert tenant_pairs == EXPECTED_TENANT_ROUTES
    assert sum(tenant_pairs.values()) == 5
    assert all(
        not path.startswith("/api/v1/api/tenants")
        for _, path in tenant_pairs
    )


def test_existing_general_application_composition_is_preserved() -> None:
    """Gateway metadata, middleware, handler, and general API remain intact."""
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


def test_runtime_routes_expose_exact_three_detail_authority_pairs() -> None:
    """GET/PUT/DELETE carry only their canonical frozen permission/operation pairs."""
    expected = {
        "GET": ("tenant:profile:read", "profile_read"),
        "PUT": ("tenant:profile:write", "profile_update"),
        "DELETE": ("tenant:lifecycle:archive", "lifecycle_archive"),
    }
    for method, pair in expected.items():
        dependencies = _auth_dependencies(
            _route(method, "/api/tenants/{tenant_id}")
        )
        assert len(dependencies) == 1
        assert (
            dependencies[0].permission_id,
            dependencies[0].operation,
        ) == pair

    assert _auth_dependencies(_route("GET", "/api/tenants")) == []
    assert _auth_dependencies(_route("POST", "/api/tenants")) == []


def test_runtime_put_schema_is_exact_six_and_extra_forbidden() -> None:
    """Canonical OpenAPI/runtime model cannot represent protected PUT fields."""
    assert set(TenantUpdateRequest.model_fields) == {
        "name",
        "alias",
        "industry",
        "region",
        "sector",
        "legal_name",
    }
    assert TenantUpdateRequest.model_config.get("extra") == "forbid"


def test_collection_routes_remain_503_before_registry_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Collection GET and POST remain contained even with fabricated projections."""
    calls: Counter[str] = Counter()

    for name in (
        "list",
        "get",
        "create",
        "update",
        "update_profile",
        "archive",
    ):
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
        list_response = client.get("/api/tenants", headers=headers)
        create_response = client.post(
            "/api/tenants",
            headers=headers,
            json={"name": "Tenant A"},
        )

    for response in (list_response, create_response):
        assert response.status_code == 503
        assert response.json() == {
            "detail": "TENANT_AUTHORITY_UNAVAILABLE"
        }

    assert calls == Counter()


def test_detail_routes_require_authentication_before_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fabricated transport projections cannot activate GET, PUT, or DELETE."""
    def forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("Registry accessed without authentication")

    monkeypatch.setattr(TenantRegistry, "get", forbidden)
    monkeypatch.setattr(TenantRegistry, "update_profile", forbidden)
    monkeypatch.setattr(TenantRegistry, "archive", forbidden)

    headers = {
        "X-Tenant-ID": _TENANT_A,
        "X-Role": "ENTERPRISE_ADMIN",
        "X-Permissions": "*",
        "Authorization": "Bearer definitely-invalid-token",
    }

    with TestClient(app) as client:
        get_response = client.get(
            f"/api/tenants/{_TENANT_A}",
            headers=headers,
        )
        put_response = client.put(
            f"/api/tenants/{_TENANT_A}",
            headers=headers,
            json={"name": "Tenant Alpha"},
        )
        delete_response = client.delete(
            f"/api/tenants/{_TENANT_A}",
            headers=headers,
        )

    assert get_response.status_code == 401
    assert put_response.status_code == 401
    assert delete_response.status_code == 401


def test_explicit_tenant_scope_is_required_before_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authenticated callers still require explicit X-Tenant-ID."""
    def forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("Registry accessed without tenant scope")

    monkeypatch.setattr(TenantRegistry, "get", forbidden)
    monkeypatch.setattr(TenantRegistry, "update_profile", forbidden)
    monkeypatch.setattr(TenantRegistry, "archive", forbidden)

    with _authority_scope(_TENANT_A):
        with TestClient(app) as client:
            get_response = client.get(f"/api/tenants/{_TENANT_A}")
            put_response = client.put(
                f"/api/tenants/{_TENANT_A}",
                json={"alias": "alpha"},
            )
            delete_response = client.delete(f"/api/tenants/{_TENANT_A}")

    assert get_response.status_code == 403
    assert put_response.status_code == 403
    assert delete_response.status_code == 403


def test_durable_membership_cannot_be_replaced_by_projected_roles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Header/identity projections cannot substitute current membership."""
    def forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("Registry accessed without durable membership")

    monkeypatch.setattr(TenantRegistry, "get", forbidden)
    monkeypatch.setattr(TenantRegistry, "update_profile", forbidden)
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
            put_response = client.put(
                f"/api/tenants/{_TENANT_A}",
                headers=headers,
                json={"alias": "alpha"},
            )
            delete_response = client.delete(
                f"/api/tenants/{_TENANT_A}",
                headers=headers,
            )

    assert get_response.status_code == 403
    assert put_response.status_code == 403
    assert delete_response.status_code == 403


def test_authorized_header_scope_must_equal_path_before_all_detail_persistence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authority for tenant-b cannot target tenant-a through any detail operation."""
    calls: Counter[str] = Counter()

    for name in ("get", "update_profile", "archive"):
        def forbidden(
            *_args: object,
            _name: str = name,
            **_kwargs: object,
        ) -> NoReturn:
            calls[_name] += 1
            raise AssertionError("Persistence reached after scope mismatch")

        monkeypatch.setattr(TenantRegistry, name, forbidden)

    headers = {"X-Tenant-ID": _TENANT_B}

    with _authority_scope(_TENANT_B):
        with TestClient(app) as client:
            get_response = client.get(
                f"/api/tenants/{_TENANT_A}",
                headers=headers,
            )
            put_response = client.put(
                f"/api/tenants/{_TENANT_A}",
                headers=headers,
                json={"alias": "alpha"},
            )
            delete_response = client.delete(
                f"/api/tenants/{_TENANT_A}",
                headers=headers,
            )

    for response in (get_response, put_response, delete_response):
        assert response.status_code == 403
        assert response.json() == {
            "detail": "TENANT_SCOPE_PATH_MISMATCH"
        }

    assert calls == Counter()


def test_authorized_get_returns_durable_sector(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GET remains 200 and now exposes C1 durable sector truth."""
    calls: list[str] = []

    def get_one(tenant_id: str) -> Any:
        calls.append(tenant_id)
        return _entity(tenant_id, sector="LegalTech")

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
    assert response.json()["tenant_id"] == _TENANT_A
    assert response.json()["sector"] == "LegalTech"
    assert calls == [_TENANT_A]
    assert all(reader.write_calls == 0 for reader in readers)


def test_authorized_put_calls_only_strict_profile_persistence_and_returns_sector(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authorized PUT reaches update_profile once and returns HTTP 200."""
    calls: list[tuple[str, dict[str, Any]]] = []

    def update_profile(
        tenant_id: str,
        payload: dict[str, Any],
    ) -> Any:
        calls.append((tenant_id, payload))
        return _entity(
            tenant_id,
            name="Tenant Alpha",
            sector="AI",
        )

    def legacy_forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("Legacy update reached by HTTP PUT")

    monkeypatch.setattr(
        TenantRegistry,
        "update_profile",
        staticmethod(update_profile),
    )
    monkeypatch.setattr(
        TenantRegistry,
        "update",
        staticmethod(legacy_forbidden),
    )

    with _authority_scope(_TENANT_A) as readers:
        with TestClient(app) as client:
            response = client.put(
                f"/api/tenants/{_TENANT_A}",
                headers={"X-Tenant-ID": _TENANT_A},
                json={
                    "name": "Tenant Alpha",
                    "sector": "AI",
                    "alias": None,
                },
            )

    assert response.status_code == 200
    payload = response.json()
    assert payload["tenant_id"] == _TENANT_A
    assert payload["name"] == "Tenant Alpha"
    assert payload["sector"] == "AI"
    assert calls == [
        (
            _TENANT_A,
            {
                "name": "Tenant Alpha",
                "alias": None,
                "sector": "AI",
            },
        )
    ]
    assert all(reader.write_calls == 0 for reader in readers)


def test_put_forbidden_extra_field_is_422_before_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Protected HTTP fields fail schema validation and cannot reach persistence."""
    calls = 0

    def forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        nonlocal calls
        calls += 1
        raise AssertionError("Registry reached by forbidden PUT field")

    monkeypatch.setattr(
        TenantRegistry,
        "update_profile",
        staticmethod(forbidden),
    )

    with _authority_scope(_TENANT_A):
        with TestClient(app) as client:
            response = client.put(
                f"/api/tenants/{_TENANT_A}",
                headers={"X-Tenant-ID": _TENANT_A},
                json={
                    "name": "Tenant Alpha",
                    "status": "ARCHIVED",
                },
            )

    assert response.status_code == 422
    assert calls == 0


def test_put_empty_payload_maps_exact_registry_422(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Empty model reaches strict persistence as {} and returns bounded token."""
    calls: list[dict[str, Any]] = []

    def fail(_tenant_id: str, payload: dict[str, Any]) -> NoReturn:
        calls.append(payload)
        raise TenantRegistryError(
            "TENANT_REGISTRY_PROFILE_UPDATE_EMPTY"
        )

    monkeypatch.setattr(
        TenantRegistry,
        "update_profile",
        staticmethod(fail),
    )

    with _authority_scope(_TENANT_A):
        with TestClient(app) as client:
            response = client.put(
                f"/api/tenants/{_TENANT_A}",
                headers={"X-Tenant-ID": _TENANT_A},
                json={},
            )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "TENANT_REGISTRY_PROFILE_UPDATE_EMPTY"
    }
    assert calls == [{}]


def test_put_genuine_absence_is_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only a genuine missing target maps PUT to HTTP 404."""
    monkeypatch.setattr(
        TenantRegistry,
        "update_profile",
        staticmethod(lambda _tenant_id, _payload: None),
    )

    with _authority_scope(_TENANT_A):
        with TestClient(app) as client:
            response = client.put(
                f"/api/tenants/{_TENANT_A}",
                headers={"X-Tenant-ID": _TENANT_A},
                json={"alias": "alpha"},
            )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Tenant not found."
    }


@pytest.mark.parametrize(
    ("reason", "expected_status"),
    [
        ("TENANT_REGISTRY_PROFILE_UPDATE_INVALID_VALUES", 422),
        ("TENANT_REGISTRY_PROFILE_UPDATE_INVALID_DOCUMENT", 503),
        ("TENANT_REGISTRY_PROFILE_UPDATE_INCONSISTENT_STATE", 503),
        ("TENANT_REGISTRY_PROFILE_UPDATE_UNAVAILABLE", 503),
    ],
)
def test_put_registry_failure_translation_is_bounded(
    monkeypatch: pytest.MonkeyPatch,
    reason: str,
    expected_status: int,
) -> None:
    """Known strict persistence failures retain deterministic HTTP classification."""
    def fail(_tenant_id: str, _payload: dict[str, Any]) -> NoReturn:
        raise TenantRegistryError(reason)

    monkeypatch.setattr(
        TenantRegistry,
        "update_profile",
        staticmethod(fail),
    )

    with _authority_scope(_TENANT_A):
        with TestClient(app) as client:
            response = client.put(
                f"/api/tenants/{_TENANT_A}",
                headers={"X-Tenant-ID": _TENANT_A},
                json={"alias": "alpha"},
            )

    assert response.status_code == expected_status
    assert response.json() == {"detail": reason}


def test_put_unknown_registry_failure_is_generic_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unknown persistence details never leak through the HTTP boundary."""
    def fail(_tenant_id: str, _payload: dict[str, Any]) -> NoReturn:
        raise TenantRegistryError("SECRET_INTERNAL_DETAIL")

    monkeypatch.setattr(
        TenantRegistry,
        "update_profile",
        staticmethod(fail),
    )

    with _authority_scope(_TENANT_A):
        with TestClient(app) as client:
            response = client.put(
                f"/api/tenants/{_TENANT_A}",
                headers={"X-Tenant-ID": _TENANT_A},
                json={"alias": "alpha"},
            )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "TENANT_REGISTRY_UNAVAILABLE"
    }


def test_authorized_get_preserves_absence_and_registry_failure_mapping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """C2 does not regress B2B GET 404/503 semantics."""
    cases: tuple[tuple[object, int, str], ...] = (
        (None, 404, "Tenant not found."),
        (
            TenantRegistryError("TENANT_REGISTRY_GET_INVALID_DOCUMENT"),
            503,
            "TENANT_REGISTRY_GET_INVALID_DOCUMENT",
        ),
        (
            TenantRegistryError("TENANT_REGISTRY_GET_UNAVAILABLE"),
            503,
            "TENANT_REGISTRY_GET_UNAVAILABLE",
        ),
    )

    for outcome, expected_status, expected_detail in cases:
        with monkeypatch.context() as scoped:
            if isinstance(outcome, Exception):
                def fail(
                    _tenant_id: str,
                    *,
                    _error: Exception = outcome,
                ) -> NoReturn:
                    raise _error

                scoped.setattr(
                    TenantRegistry,
                    "get",
                    staticmethod(fail),
                )
            else:
                scoped.setattr(
                    TenantRegistry,
                    "get",
                    staticmethod(
                        lambda _tenant_id, _outcome=outcome: _outcome
                    ),
                )

            with _authority_scope(_TENANT_A):
                with TestClient(app) as client:
                    response = client.get(
                        f"/api/tenants/{_TENANT_A}",
                        headers={"X-Tenant-ID": _TENANT_A},
                    )

            assert response.status_code == expected_status
            assert response.json() == {"detail": expected_detail}


def test_authorized_delete_preserves_soft_archive_http_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """C2 does not regress B2B DELETE 204/404/503 translation."""
    outcomes: tuple[tuple[object, int, str | None], ...] = (
        (True, 204, None),
        (False, 404, "Tenant not found or already archived."),
        (
            TenantRegistryError("TENANT_REGISTRY_ARCHIVE_UNAVAILABLE"),
            503,
            "TENANT_REGISTRY_ARCHIVE_UNAVAILABLE",
        ),
    )

    for outcome, expected_status, expected_detail in outcomes:
        with monkeypatch.context() as scoped:
            if isinstance(outcome, Exception):
                def fail(
                    _tenant_id: str,
                    *,
                    _error: Exception = outcome,
                ) -> NoReturn:
                    raise _error

                scoped.setattr(
                    TenantRegistry,
                    "archive",
                    staticmethod(fail),
                )
            else:
                scoped.setattr(
                    TenantRegistry,
                    "archive",
                    staticmethod(
                        lambda _tenant_id, _outcome=outcome: _outcome
                    ),
                )

            with _authority_scope(_TENANT_A):
                with TestClient(app) as client:
                    response = client.delete(
                        f"/api/tenants/{_TENANT_A}",
                        headers={"X-Tenant-ID": _TENANT_A},
                    )

            assert response.status_code == expected_status
            if expected_detail is not None:
                assert response.json() == {"detail": expected_detail}


# =============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_tenant_router_runtime_registration.py
# VERSION: v1.2.0-TENANT-ROUTER-PROFILE-UPDATE-WIRING-CERT
# AUTHORITY BOUNDARY: canonical-ASGI C2 wiring evidence only; durable authentication, membership, role, permission, authorization, and persistence ownership remain production authorities
# TENANT POSTURE: GET/PUT/DELETE require exact current-truth authorization and X-Tenant-ID/path congruence before persistence; collection GET and POST stay contained
# FAIL-CLOSED POSTURE: protected PUT fields never reach registry; strict update_profile alone is invoked; PUT maps 200/403/404/422/503 deterministically while GET/archive B2B semantics remain preserved
# FINANCIAL EXECUTION AUTHORITY: None. Plan cannot be represented by the PUT model; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
