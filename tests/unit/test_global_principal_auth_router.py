from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException
from starlette.requests import Request

from tools.eos.api.global_principal_auth_router import (
    GlobalMfaVerificationRequest,
    logout_global_session,
    router,
    verify_global_mfa,
)


def _request() -> Request:
    app = FastAPI()
    app.state.global_principal_session_indexes_ready = True
    app.state.global_principal_mfa_factor_indexes_ready = True
    app.state.global_principal_totp_verifier = None
    return Request({"type": "http", "app": app, "headers": []})


def test_global_mfa_route_fails_closed_without_kms_factor_verifier() -> None:
    with pytest.raises(HTTPException) as error:
        asyncio.run(verify_global_mfa(
            GlobalMfaVerificationRequest(mfa_challenge="x" * 48, code="123456"),
            _request(),
        ))
    assert error.value.status_code == 503
    assert error.value.detail == "GLOBAL_MFA_KEY_SERVICE_UNAVAILABLE"


def test_global_logout_does_not_revoke_a_legacy_tenant_session() -> None:
    identity = SimpleNamespace(
        identity_id="principal",
        tenant_id="tenant",
        session_reference="WILSYSESSION-legacy",
    )
    with pytest.raises(HTTPException) as error:
        asyncio.run(logout_global_session(identity=identity))
    assert error.value.status_code == 409


def test_global_auth_routes_are_mounted_under_one_explicit_prefix() -> None:
    paths = {getattr(route, "path", None) for route in router.routes}
    assert paths == {
        "/auth/global/login",
        "/auth/global/membership-options",
        "/auth/global/select-membership",
        "/auth/global/verify-mfa",
        "/auth/global/refresh",
        "/auth/global/logout",
    }
