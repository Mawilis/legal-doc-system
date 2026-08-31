# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN CERTIFICATION ARTIFACT
TENANT ROUTER — C2 CONTROLLED PROFILE UPDATE — UNIT CERTIFICATE
===============================================================================

TITLE:
    WILSY OS Tenant Router C2 Controlled Profile Update Unit Certification

FILE:
    tests/unit/test_tenant_router_fail_closed.py

VERSION:
    v1.2.0-TENANT-PROFILE-UPDATE-AUTHORITY-CERT

AUTHORITY:
    Wilsy OS Core Governance.
    Deterministic certification of exact route ownership, containment, authority
    bindings, six-field PUT schema, scope congruence, persistence invocation, and
    failure translation.

EPITOME:
    Evolves the B2B selective-containment certificate without weakening its GET,
    DELETE, collection-list, or POST assertions. Proves PUT is now the third
    activated detail operation, bound only to tenant:profile:write/profile_update,
    invokes only update_profile after exact scope binding, rejects field widening,
    maps strict registry failures deterministically, and serializes durable sector.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_router_fail_closed.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-31

CHANGELOG:
    v1.2.0-TENANT-PROFILE-UPDATE-AUTHORITY-CERT
        - Activates deterministic certification for PUT profile mutation.
        - Preserves exact five-route ownership.
        - Preserves collection GET and POST containment before persistence.
        - Preserves exact GET and DELETE authorization bindings.
        - Adds exact PUT write authorization binding and six-field schema proof.
        - Proves legacy TenantRegistry.update cannot be reached by PUT.
        - Proves scope mismatch, absence, input errors, service failures, and
          durable sector response mapping.
        - Uses genuine Request objects for direct route calls so bounded Pyright
          certification proves the same runtime signatures exercised by FastAPI.

    v1.1.0-TENANT-SELECTIVE-AUTHORITY-CONTAINMENT-CERT
        - Certified B2B GET/archive activation while GET collection, POST, and PUT
          remained contained.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    Test-local ASGI/direct-call persistence doubles only. No production tenant
    data, credentials, network access, or durable authority mutation.

TENANT BOUNDARY:
    Activated detail dependencies use exact own-tenant vocabulary. Scope mismatch
    is proved to deny before profile persistence.

AUTHORITY BOUNDARY:
    Evidence only. No authentication, authorization, assignment, membership,
    permission, or persistence authority is created by this certificate.

FINANCIAL AUTHORITY BOUNDARY:
    Proves PUT cannot represent or invoke plan mutation.
    Kennel EOS remains the exclusive financial execution authority.

CERTIFICATION CLASS:
    UNIT / DETERMINISTIC / FAIL-CLOSED

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
===============================================================================
"""

from __future__ import annotations

import asyncio
from collections import Counter
from types import SimpleNamespace
from typing import Any, NoReturn

import pytest
from fastapi import HTTPException, Request
from fastapi.routing import APIRoute
from pydantic import ValidationError

import tools.eos.api.tenant_router as router_module
from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization
from tools.eos.api.tenant_router import (
    TenantUpdateRequest,
    VERSION as TENANT_ROUTER_VERSION,
    tenant_router,
)
from tools.eos.saas.tenancy.tenant_registry import (
    TenantRegistry,
    TenantRegistryError,
)


VERSION = "v1.2.0-TENANT-PROFILE-UPDATE-AUTHORITY-CERT"
EXPECTED_ROUTER_VERSION = "v1.2.0-TENANT-PROFILE-UPDATE-AUTHORITY-WIRING"

EXPECTED_ROUTES = Counter(
    {
        ("GET", "/api/tenants"): 1,
        ("POST", "/api/tenants"): 1,
        ("GET", "/api/tenants/{tenant_id}"): 1,
        ("PUT", "/api/tenants/{tenant_id}"): 1,
        ("DELETE", "/api/tenants/{tenant_id}"): 1,
    }
)

EXPECTED_UPDATE_FIELDS = {
    "name",
    "alias",
    "industry",
    "region",
    "sector",
    "legal_name",
}


def _route(method: str, path: str) -> APIRoute:
    """Return the unique tenant APIRoute for one exact method/path."""
    matches = [
        route
        for route in tenant_router.routes
        if isinstance(route, APIRoute)
        and route.path == path
        and method in (route.methods or set())
    ]
    assert len(matches) == 1
    return matches[0]


def _tenant_authorization_dependencies(
    route: APIRoute,
) -> list[RequireTenantAuthorization]:
    """Return only governed tenant-authorization dependencies on a route."""
    return [
        dependant.call
        for dependant in route.dependant.dependencies
        if isinstance(dependant.call, RequireTenantAuthorization)
    ]


def _route_counter() -> Counter[tuple[str, str]]:
    """Return exact method/path ownership for tenant_router."""
    result: Counter[tuple[str, str]] = Counter()
    for route in tenant_router.routes:
        assert isinstance(route, APIRoute)
        for method in route.methods or set():
            result[(method, route.path)] += 1
    return result


def _entity(tenant_id: str = "tenant-a", *, sector: str = "RegTech") -> Any:
    """Build the exact response-mapper attribute surface."""
    return SimpleNamespace(
        tenant_id=tenant_id,
        organization=SimpleNamespace(
            organization_name="Tenant A",
            legal_name="Tenant A Legal",
            tax_id="tax-a",
            contact_email="tenant-a@example.test",
            industry="Legal",
        ),
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


def _authorization(tenant_id: str) -> Any:
    """Build minimal already-authorized context for direct route invocation."""
    return SimpleNamespace(tenant_id=tenant_id)


def _request() -> Request:
    """Build one minimal genuine HTTP Request for direct route invocation."""
    scope: dict[str, Any] = {
        "type": "http",
        "http_version": "1.1",
        "method": "PUT",
        "scheme": "http",
        "path": "/api/tenants/tenant-a",
        "raw_path": b"/api/tenants/tenant-a",
        "query_string": b"",
        "headers": [],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
        "root_path": "",
    }
    return Request(scope)


def test_version_and_exact_five_route_surface() -> None:
    """C2 keeps the exact five-route API surface."""
    assert VERSION == "v1.2.0-TENANT-PROFILE-UPDATE-AUTHORITY-CERT"
    assert TENANT_ROUTER_VERSION == EXPECTED_ROUTER_VERSION
    assert _route_counter() == EXPECTED_ROUTES
    assert len(tenant_router.routes) == 5


def test_get_detail_has_exact_profile_read_authorization_dependency() -> None:
    """GET keeps exactly tenant:profile:read/profile_read."""
    dependencies = _tenant_authorization_dependencies(
        _route("GET", "/api/tenants/{tenant_id}")
    )
    assert len(dependencies) == 1
    assert dependencies[0].permission_id == "tenant:profile:read"
    assert dependencies[0].operation == "profile_read"


def test_put_detail_has_exact_profile_write_authorization_dependency() -> None:
    """PUT is activated only through tenant:profile:write/profile_update."""
    dependencies = _tenant_authorization_dependencies(
        _route("PUT", "/api/tenants/{tenant_id}")
    )
    assert len(dependencies) == 1
    assert dependencies[0].permission_id == "tenant:profile:write"
    assert dependencies[0].operation == "profile_update"


def test_delete_detail_has_exact_lifecycle_archive_authorization_dependency() -> None:
    """DELETE keeps exactly tenant:lifecycle:archive/lifecycle_archive."""
    dependencies = _tenant_authorization_dependencies(
        _route("DELETE", "/api/tenants/{tenant_id}")
    )
    assert len(dependencies) == 1
    assert dependencies[0].permission_id == "tenant:lifecycle:archive"
    assert dependencies[0].operation == "lifecycle_archive"


def test_collection_get_and_post_remain_without_tenant_authorization_dependency() -> None:
    """Non-migrated collection routes remain contained and unactivated."""
    for method, path in (
        ("GET", "/api/tenants"),
        ("POST", "/api/tenants"),
    ):
        assert _tenant_authorization_dependencies(_route(method, path)) == []


def test_update_request_exposes_exact_six_fields_and_forbids_extra() -> None:
    """HTTP profile input cannot represent protected business fields."""
    assert set(TenantUpdateRequest.model_fields) == EXPECTED_UPDATE_FIELDS
    assert TenantUpdateRequest.model_config.get("extra") == "forbid"

    for forbidden in (
        "tenant_id",
        "tax_id",
        "contact_email",
        "plan",
        "status",
        "checksum",
        "proof_hash",
        "verified",
        "compliance_flags",
        "created_at",
        "updated_at",
    ):
        with pytest.raises(ValidationError):
            TenantUpdateRequest.model_validate({forbidden: "forbidden"})


def test_update_request_exclude_unset_preserves_explicit_null() -> None:
    """Omission and explicit-null remain distinct for optional profile fields."""
    empty = TenantUpdateRequest()
    explicit = TenantUpdateRequest(alias=None, sector=None)

    assert empty.model_dump(exclude_unset=True) == {}
    assert explicit.model_dump(exclude_unset=True) == {
        "alias": None,
        "sector": None,
    }


def test_response_mapper_uses_durable_sector_truth() -> None:
    """C2 maps response sector from the durable top-level entity field."""
    response = router_module._entity_to_response(
        _entity(sector="Legal Technology")
    )
    assert response.sector == "Legal Technology"


def test_collection_routes_deny_before_registry_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GET collection and POST remain exact 503 before every registry method."""
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
            raise AssertionError(f"TenantRegistry.{_name} reached")

        monkeypatch.setattr(TenantRegistry, name, forbidden)

    with pytest.raises(HTTPException) as list_error:
        asyncio.run(
            router_module.list_tenants(
                request=_request(),
                search=None,
                skip=0,
                limit=20,
            )
        )
    assert list_error.value.status_code == 503
    assert list_error.value.detail == "TENANT_AUTHORITY_UNAVAILABLE"

    with pytest.raises(HTTPException) as post_error:
        asyncio.run(
            router_module.create_tenant(
                payload=router_module.TenantCreateRequest(name="Tenant A"),
                request=_request(),
            )
        )
    assert post_error.value.status_code == 503
    assert post_error.value.detail == "TENANT_AUTHORITY_UNAVAILABLE"
    assert calls == Counter()


def test_put_scope_mismatch_denies_before_all_registry_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authority for tenant-b cannot mutate tenant-a path truth."""
    calls: Counter[str] = Counter()

    for name in ("update_profile", "update"):
        def forbidden(
            *_args: object,
            _name: str = name,
            **_kwargs: object,
        ) -> NoReturn:
            calls[_name] += 1
            raise AssertionError("Persistence reached after scope mismatch")

        monkeypatch.setattr(TenantRegistry, name, forbidden)

    with pytest.raises(HTTPException) as raised:
        asyncio.run(
            router_module.update_tenant(
                tenant_id="tenant-a",
                payload=TenantUpdateRequest(name="Tenant Alpha"),
                request=_request(),
                authorization=_authorization("tenant-b"),
            )
        )

    assert raised.value.status_code == 403
    assert raised.value.detail == "TENANT_SCOPE_PATH_MISMATCH"
    assert calls == Counter()


def test_put_invokes_only_update_profile_with_exclude_unset_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authorized PUT reaches strict persistence exactly once and never legacy update."""
    calls: list[tuple[str, dict[str, Any]]] = []

    def update_profile(
        tenant_id: str,
        payload: dict[str, Any],
    ) -> Any:
        calls.append((tenant_id, payload))
        return _entity(tenant_id, sector="AI")

    def legacy_forbidden(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("Legacy TenantRegistry.update reached by PUT")

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

    response = asyncio.run(
        router_module.update_tenant(
            tenant_id="tenant-a",
            payload=TenantUpdateRequest(
                name="Tenant Alpha",
                sector="AI",
                alias=None,
            ),
            request=_request(),
            authorization=_authorization("tenant-a"),
        )
    )

    assert response.tenant_id == "tenant-a"
    assert response.sector == "AI"
    assert calls == [
        (
            "tenant-a",
            {
                "name": "Tenant Alpha",
                "alias": None,
                "sector": "AI",
            },
        )
    ]


def test_put_genuine_absence_maps_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Strict persistence None maps only to bounded target absence."""
    monkeypatch.setattr(
        TenantRegistry,
        "update_profile",
        staticmethod(lambda _tenant_id, _payload: None),
    )

    with pytest.raises(HTTPException) as raised:
        asyncio.run(
            router_module.update_tenant(
                tenant_id="tenant-a",
                payload=TenantUpdateRequest(alias="alpha"),
                request=_request(),
                authorization=_authorization("tenant-a"),
            )
        )

    assert raised.value.status_code == 404
    assert raised.value.detail == "Tenant not found."


@pytest.mark.parametrize(
    "reason",
    [
        "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_TENANT_ID",
        "TENANT_REGISTRY_PROFILE_UPDATE_EMPTY",
        "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_FIELDS",
        "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_VALUES",
    ],
)
def test_put_profile_input_failures_map_exact_422(
    monkeypatch: pytest.MonkeyPatch,
    reason: str,
) -> None:
    """Strict persistence caller-input failures remain bounded HTTP 422."""
    def fail(_tenant_id: str, _payload: dict[str, Any]) -> NoReturn:
        raise TenantRegistryError(reason)

    monkeypatch.setattr(
        TenantRegistry,
        "update_profile",
        staticmethod(fail),
    )

    with pytest.raises(HTTPException) as raised:
        asyncio.run(
            router_module.update_tenant(
                tenant_id="tenant-a",
                payload=TenantUpdateRequest(alias="alpha"),
                request=_request(),
                authorization=_authorization("tenant-a"),
            )
        )

    assert raised.value.status_code == 422
    assert raised.value.detail == reason


@pytest.mark.parametrize(
    "reason",
    [
        "TENANT_REGISTRY_PROFILE_UPDATE_INVALID_DOCUMENT",
        "TENANT_REGISTRY_PROFILE_UPDATE_INCONSISTENT_STATE",
        "TENANT_REGISTRY_PROFILE_UPDATE_UNAVAILABLE",
    ],
)
def test_put_profile_service_failures_map_exact_503(
    monkeypatch: pytest.MonkeyPatch,
    reason: str,
) -> None:
    """Persisted-truth/consistency/outage failures stay operationally distinct."""
    def fail(_tenant_id: str, _payload: dict[str, Any]) -> NoReturn:
        raise TenantRegistryError(reason)

    monkeypatch.setattr(
        TenantRegistry,
        "update_profile",
        staticmethod(fail),
    )

    with pytest.raises(HTTPException) as raised:
        asyncio.run(
            router_module.update_tenant(
                tenant_id="tenant-a",
                payload=TenantUpdateRequest(alias="alpha"),
                request=_request(),
                authorization=_authorization("tenant-a"),
            )
        )

    assert raised.value.status_code == 503
    assert raised.value.detail == reason


def test_put_unknown_registry_failure_is_generic_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unknown future registry errors never escape as raw HTTP 500."""
    def fail(_tenant_id: str, _payload: dict[str, Any]) -> NoReturn:
        raise TenantRegistryError("SECRET_INTERNAL_DETAIL")

    monkeypatch.setattr(
        TenantRegistry,
        "update_profile",
        staticmethod(fail),
    )

    with pytest.raises(HTTPException) as raised:
        asyncio.run(
            router_module.update_tenant(
                tenant_id="tenant-a",
                payload=TenantUpdateRequest(alias="alpha"),
                request=_request(),
                authorization=_authorization("tenant-a"),
            )
        )

    assert raised.value.status_code == 503
    assert raised.value.detail == "TENANT_REGISTRY_UNAVAILABLE"


def test_empty_put_payload_reaches_strict_empty_contract_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Empty HTTP model becomes {} and strict persistence owns its bounded rejection."""
    observed: list[dict[str, Any]] = []

    def fail(_tenant_id: str, payload: dict[str, Any]) -> NoReturn:
        observed.append(payload)
        raise TenantRegistryError("TENANT_REGISTRY_PROFILE_UPDATE_EMPTY")

    monkeypatch.setattr(
        TenantRegistry,
        "update_profile",
        staticmethod(fail),
    )

    with pytest.raises(HTTPException) as raised:
        asyncio.run(
            router_module.update_tenant(
                tenant_id="tenant-a",
                payload=TenantUpdateRequest(),
                request=_request(),
                authorization=_authorization("tenant-a"),
            )
        )

    assert observed == [{}]
    assert raised.value.status_code == 422
    assert raised.value.detail == "TENANT_REGISTRY_PROFILE_UPDATE_EMPTY"


# =============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_tenant_router_fail_closed.py
# VERSION: v1.2.0-TENANT-PROFILE-UPDATE-AUTHORITY-CERT
# AUTHORITY BOUNDARY: deterministic C2 router-schema/wiring evidence only; no authentication, membership, role, permission, authorization, persistence, or financial authority
# TENANT POSTURE: GET/PUT/DELETE detail routes each carry one exact governed dependency; PUT scope mismatch denies before strict persistence; collection GET and POST remain contained
# FAIL-CLOSED POSTURE: PUT field widening is schema-rejected; strict update_profile alone is invoked; absence=404, caller mutation errors=422, persisted-truth/outage/unknown failures=503
# FINANCIAL EXECUTION AUTHORITY: None. Plan is absent from TenantUpdateRequest and cannot be mutated through PUT.
# END OF WILSY OS SOVEREIGN ARTIFACT
