"""Tenant Legal Operating Model direct HTTP boundary certificate.

VERSION: v1.0.0-CX26-R3-CURRENT-OPERATING-MODEL-HTTP-CERT
AUTHORITY: HTTP validation, tenant correlation and transaction composition.
FINANCIAL AUTHORITY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from contextlib import AbstractContextManager
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import tools.eos.api.tenant_legal_operating_model_router as http
from tools.eos.legal_operations.domain.tenant_legal_operating_model import (
    TenantLegalOperatingModelError,
)
from tools.eos.legal_operations.registry.tenant_legal_operating_model_registry import (
    TenantLegalOperatingModelRegistryNotFoundError,
)
from tools.eos.legal_operations.service.tenant_legal_operating_model_service import (
    TenantLegalOperatingModelAuthorizationDeniedError,
    TenantLegalOperatingModelAuthorityUnavailableError,
    TenantLegalOperatingModelRevisionConflictError,
)


TENANT = "tenant-http-operating-model"
PRINCIPAL = "principal-http-operating-model"


class _Value:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def to_dict(self) -> dict[str, object]:
        return dict(self.payload)


class _Session(AbstractContextManager["_Session"]):
    def __init__(self) -> None:
        self.in_transaction = False
        self.started = 0
        self.committed = 0
        self.aborted = 0

    def __enter__(self) -> "_Session":
        return self

    def __exit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> None:
        del exc_type, exc, traceback

    def start_transaction(self) -> None:
        self.started += 1
        self.in_transaction = True

    def commit_transaction(self) -> None:
        assert self.in_transaction
        self.committed += 1
        self.in_transaction = False

    def abort_transaction(self) -> None:
        assert self.in_transaction
        self.aborted += 1
        self.in_transaction = False


class _Client:
    def __init__(self, session: _Session) -> None:
        self.session = session

    def start_session(self) -> _Session:
        return self.session


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(http.router, prefix="/api")

    identity = SimpleNamespace(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
    )

    app.dependency_overrides[
        http.get_current_identity
    ] = lambda: identity

    app.dependency_overrides[
        http.get_principal_authority_repository
    ] = lambda: object()

    app.dependency_overrides[
        http.get_tenant_membership_repository
    ] = lambda: object()

    app.dependency_overrides[
        http.get_role_assignment_repository
    ] = lambda: object()

    app.dependency_overrides[
        http.get_authorization_role_repository
    ] = lambda: object()

    return app


def test_exact_router_surface_is_get_and_post_only() -> None:
    pairs = {
        (
            method,
            str(getattr(route, "path", "")),
        )
        for route in http.router.routes
        for method in (
            getattr(route, "methods", set()) or set()
        )
    }

    assert pairs == {
        ("GET", "/legal/operating-model"),
        ("POST", "/legal/operating-model"),
    }


def test_request_model_rejects_authority_bearing_extras() -> None:
    app = _app()

    with TestClient(app) as client:
        response = client.post(
            "/api/legal/operating-model",
            headers={
                "X-Tenant-ID": TENANT,
                "Idempotency-Key": "command-1",
            },
            json={
                "expected_revision": None,
                "activated_item_ids": [
                    "PERSONA_PARTNER",
                ],
                "tenant_id": "foreign",
                "principal_id": "forged",
                "permission": "forged",
            },
        )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("headers", "expected_status", "expected_code"),
    (
        ({}, 400, "TENANT_SCOPE_REQUIRED"),
        (
            {"X-Tenant-ID": "foreign-tenant"},
            403,
            "TENANT_SCOPE_DENIED",
        ),
    ),
)
def test_tenant_header_is_required_and_exact(
    headers: dict[str, str],
    expected_status: int,
    expected_code: str,
) -> None:
    app = _app()

    with TestClient(app) as client:
        response = client.get(
            "/api/legal/operating-model",
            headers=headers,
        )

    assert response.status_code == expected_status
    assert response.json()["detail"]["error"] == expected_code


def test_missing_idempotency_fails_before_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def forbidden(**_: Any) -> Any:
        nonlocal called
        called = True
        raise AssertionError("service must not execute")

    monkeypatch.setattr(
        http,
        "configure_tenant_legal_operating_model",
        forbidden,
    )

    app = _app()

    with TestClient(app) as client:
        response = client.post(
            "/api/legal/operating-model",
            headers={
                "X-Tenant-ID": TENANT,
            },
            json={
                "expected_revision": None,
                "activated_item_ids": [
                    "PERSONA_PARTNER",
                ],
            },
        )

    assert response.status_code == 400
    assert (
        response.json()["detail"]["error"]
        == "IDEMPOTENCY_KEY_REQUIRED"
    )
    assert called is False


def test_get_forwards_authenticated_identity_and_tenant_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def transaction(callback: Any) -> Any:
        return callback(
            SimpleNamespace(
                in_transaction=True,
            ),
            {
                http.COLLECTION_NAME:
                    object(),
            },
        )

    def service_call(**kwargs: Any) -> _Value:
        captured.update(kwargs)
        return _Value(
            {
                "tenant_id": TENANT,
                "operating_model_id": "model-r1",
                "revision": 1,
            }
        )

    monkeypatch.setattr(
        http,
        "_run_transaction",
        transaction,
    )
    monkeypatch.setattr(
        http,
        "get_current_tenant_legal_operating_model",
        service_call,
    )

    app = _app()

    with TestClient(app) as client:
        response = client.get(
            "/api/legal/operating-model",
            headers={
                "X-Tenant-ID": TENANT,
            },
        )

    assert response.status_code == 200
    assert captured["tenant_id"] == TENANT
    assert captured["principal_id"] == PRINCIPAL
    assert "permission" not in captured
    assert "role" not in captured


def test_post_forwards_bounded_intent_and_server_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def transaction(callback: Any) -> Any:
        return callback(
            SimpleNamespace(
                in_transaction=True,
            ),
            {
                http.COLLECTION_NAME:
                    object(),
            },
        )

    def service_call(**kwargs: Any) -> _Value:
        captured.update(kwargs)
        return _Value(
            {
                "tenant_id": TENANT,
                "operating_model_id": "model-r2",
                "revision": 2,
            }
        )

    monkeypatch.setattr(
        http,
        "_run_transaction",
        transaction,
    )
    monkeypatch.setattr(
        http,
        "configure_tenant_legal_operating_model",
        service_call,
    )

    app = _app()

    with TestClient(app) as client:
        response = client.post(
            "/api/legal/operating-model",
            headers={
                "X-Tenant-ID": TENANT,
                "Idempotency-Key": "command-r2",
            },
            json={
                "expected_revision": 1,
                "activated_item_ids": [
                    "PERSONA_PARTNER",
                ],
            },
        )

    assert response.status_code == 201
    assert captured["tenant_id"] == TENANT
    assert captured["principal_id"] == PRINCIPAL
    assert captured["expected_revision"] == 1
    assert (
        captured["activated_item_ids"]
        == ["PERSONA_PARTNER"]
    )
    assert (
        captured["idempotency_key"]
        == "command-r2"
    )


def test_transaction_commits_before_return(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()

    monkeypatch.setattr(
        http,
        "get_client",
        lambda: _Client(session),
    )
    monkeypatch.setattr(
        http,
        "get_database",
        lambda: {"database": "synthetic"},
    )

    def callback(
        tx: Any,
        database: Any,
    ) -> Any:
        assert tx.in_transaction is True
        return database

    result = http._run_transaction(
        callback
    )

    assert result == {
        "database": "synthetic",
    }
    assert session.started == 1
    assert session.committed == 1
    assert session.aborted == 0
    assert session.in_transaction is False


def test_transaction_aborts_and_translates_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()

    monkeypatch.setattr(
        http,
        "get_client",
        lambda: _Client(session),
    )
    monkeypatch.setattr(
        http,
        "get_database",
        lambda: {"database": "synthetic"},
    )

    def callback(
        tx: Any,
        database: Any,
    ) -> Any:
        del database
        assert tx.in_transaction is True
        raise TenantLegalOperatingModelRevisionConflictError(
            "CX26_R3_EXPECTED_REVISION_CONFLICT"
        )

    with pytest.raises(
        HTTPException,
    ) as error:
        http._run_transaction(
            callback
        )

    assert error.value.status_code == 409
    assert session.started == 1
    assert session.committed == 0
    assert session.aborted == 1
    assert session.in_transaction is False


@pytest.mark.parametrize(
    ("raised", "expected_status"),
    (
        (
            TenantLegalOperatingModelAuthorizationDeniedError(
                "DENIED"
            ),
            403,
        ),
        (
            TenantLegalOperatingModelRegistryNotFoundError(
                "NOT_FOUND"
            ),
            404,
        ),
        (
            TenantLegalOperatingModelRevisionConflictError(
                "CONFLICT"
            ),
            409,
        ),
        (
            TenantLegalOperatingModelError(
                "INVALID"
            ),
            400,
        ),
        (
            TenantLegalOperatingModelAuthorityUnavailableError(
                "OUTAGE"
            ),
            503,
        ),
    ),
)
def test_error_translation_is_bounded(
    raised: Exception,
    expected_status: int,
) -> None:
    translated = http._translate(
        raised
    )

    assert (
        translated.status_code
        == expected_status
    )
    assert isinstance(
        translated.detail,
        dict,
    )
    assert set(
        translated.detail
    ) == {
        "error",
        "message",
    }


def test_missing_persistence_is_bounded_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        http,
        "get_client",
        lambda: None,
    )
    monkeypatch.setattr(
        http,
        "get_database",
        lambda: None,
    )

    with pytest.raises(
        HTTPException,
    ) as error:
        http._run_transaction(
            lambda *_: None
        )

    assert error.value.status_code == 503

    detail: Any = error.value.detail

    assert (
        detail["error"]
        == "OPERATING_MODEL_PERSISTENCE_UNAVAILABLE"
    )


# ARTIFACT: test_tenant_legal_operating_model_http_router.py
# VERSION: v1.0.0-CX26-R3-CURRENT-OPERATING-MODEL-HTTP-CERT
# AUTHORITY BOUNDARY: HTTP validation / transaction composition only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
