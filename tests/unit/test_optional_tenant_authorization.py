"""Certificates for source-local optional authorization in unified My Work."""

from __future__ import annotations

import asyncio

import pytest

from tools.eos.api import tenant_authorization_http as boundary
from tools.eos.api.exceptions import ForbiddenOperationException, WilsyAPIException


def _args():
    return (object(), object(), "tenant-a", object(), object(), object())


def test_optional_authorization_omits_only_a_canonical_source_denial(monkeypatch):
    dependency = boundary.OptionalTenantAuthorization("crm:work_item:read", "crm_work_item_read")

    async def denied(*_args):
        raise ForbiddenOperationException("denied")

    monkeypatch.setattr(dependency, "_required", denied)
    assert asyncio.run(dependency(*_args())) is None


def test_optional_authorization_preserves_authorized_source_context(monkeypatch):
    dependency = boundary.OptionalTenantAuthorization("operations:work_item:read", "operations_work_item_read")
    expected = object()

    async def admitted(*_args):
        return expected

    monkeypatch.setattr(dependency, "_required", admitted)
    assert asyncio.run(dependency(*_args())) is expected


@pytest.mark.parametrize(
    "failure",
    [
        WilsyAPIException("authority unavailable", status_code=503),
        RuntimeError("unexpected dependency failure"),
    ],
)
def test_optional_authorization_never_converts_dependency_outage_to_empty_source(monkeypatch, failure):
    dependency = boundary.OptionalTenantAuthorization("intelligence:work_item:read", "intelligence_work_item_read")

    async def unavailable(*_args):
        raise failure

    monkeypatch.setattr(dependency, "_required", unavailable)
    with pytest.raises(type(failure)):
        asyncio.run(dependency(*_args()))


def test_optional_authorization_declares_no_permission_or_persistence_authority():
    dependency = boundary.OptionalTenantAuthorization("legal_operations:productive_work:read", "legal_productive_work_read")
    assert dependency._required.permission_id == "legal_operations:productive_work:read"
    assert dependency._required.operation == "legal_productive_work_read"



def test_fastapi_optional_dependency_maps_only_permission_denial_to_source_omission(monkeypatch):
    from fastapi import Depends, FastAPI
    from fastapi.testclient import TestClient
    from tools.eos.api.errors import register_error_handlers
    from tools.eos.auth.identity import SovereignIdentity
    from tools.eos.auth.principal_status import PrincipalStatus
    from tools.eos.auth.tenant_authorization import (
        TenantAuthorizationDecision,
        TenantAuthorizationReason,
    )

    app = FastAPI()
    register_error_handlers(app, debug=False)
    identity = SovereignIdentity(
        identity_id="principal-a",
        tenant_id="untrusted-token-tenant",
        username="source-reader",
        email="source-reader@example.test",
        roles=["tenant_owner"],
        permissions=[],
        auth_method="test",
        status=PrincipalStatus.ACTIVE,
    )
    app.dependency_overrides[boundary.get_current_identity] = lambda: identity
    app.dependency_overrides[boundary.get_principal_authority_repository] = object
    app.dependency_overrides[boundary.get_tenant_membership_repository] = object
    app.dependency_overrides[boundary.get_role_assignment_repository] = object

    dependency = boundary.OptionalTenantAuthorization("operations:work_item:read", "operations_work_item_read")

    @app.get("/optional")
    async def optional(context=Depends(dependency)):
        return {"admitted": context is not None}

    monkeypatch.setattr(
        boundary,
        "authorize_tenant_operation",
        lambda **_kwargs: TenantAuthorizationDecision(
            False, TenantAuthorizationReason.PERMISSION_NOT_GRANTED
        ),
    )
    with TestClient(app) as client:
        denied = client.get("/optional", headers={"X-Tenant-ID": "tenant-a"})
    assert denied.status_code == 200
    assert denied.json() == {"admitted": False}


def test_fastapi_optional_dependency_preserves_iam_authority_outage(monkeypatch):
    from fastapi import Depends, FastAPI
    from fastapi.testclient import TestClient
    from tools.eos.api.errors import register_error_handlers
    from tools.eos.auth.identity import SovereignIdentity
    from tools.eos.auth.principal_status import PrincipalStatus
    from tools.eos.auth.tenant_authorization import (
        TenantAuthorizationDecision,
        TenantAuthorizationReason,
    )

    app = FastAPI()
    register_error_handlers(app, debug=False)
    identity = SovereignIdentity(
        identity_id="principal-a",
        tenant_id="untrusted-token-tenant",
        username="source-reader",
        email="source-reader@example.test",
        roles=["tenant_owner"],
        permissions=[],
        auth_method="test",
        status=PrincipalStatus.ACTIVE,
    )
    app.dependency_overrides[boundary.get_current_identity] = lambda: identity
    app.dependency_overrides[boundary.get_principal_authority_repository] = object
    app.dependency_overrides[boundary.get_tenant_membership_repository] = object
    app.dependency_overrides[boundary.get_role_assignment_repository] = object

    dependency = boundary.OptionalTenantAuthorization("operations:work_item:read", "operations_work_item_read")

    @app.get("/optional")
    async def optional(context=Depends(dependency)):
        return {"admitted": context is not None}

    monkeypatch.setattr(
        boundary,
        "authorize_tenant_operation",
        lambda **_kwargs: TenantAuthorizationDecision(
            False, TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE
        ),
    )
    with TestClient(app) as client:
        unavailable = client.get("/optional", headers={"X-Tenant-ID": "tenant-a"})
    assert unavailable.status_code == 503
