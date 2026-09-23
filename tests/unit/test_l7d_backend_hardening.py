"""L7D backend boundary certificate.

VERSION: v1.0.0-L7D-BACKEND-HARDENING-CERT
AUTHORITY: Security-boundary evidence only; P1-P6F remain untouched.
TENANT BOUNDARY: No test fixture grants tenant authority.
FAIL-CLOSED POSTURE: Production defaults deny wildcard credentialed CORS,
                       debug/docs exposure, and sensitive response caching.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
"""

from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import tools.eos.api.server as server_module
import tools.eos.api.legal_operations_billing_read_router as billing_read
import tools.eos.api.legal_operations_command_router as command_router
import tools.eos.api.legal_operations_router as legal_read
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth import jwt_provider


def test_production_server_defaults_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    monkeypatch.delenv("WILSY_CORS_ALLOWED_ORIGINS", raising=False)
    monkeypatch.delenv("WILSY_API_DOCS_ENABLED", raising=False)
    instance = server_module.WilsyAPIServer(debug=True)
    assert instance.production_mode is True
    assert instance.debug is False
    assert instance.allowed_origins == []
    assert instance.app.docs_url is None
    assert instance.app.redoc_url is None
    cors = next(item for item in instance.app.user_middleware if getattr(item.cls, "__name__", "") == "CORSMiddleware")
    assert cors.kwargs["allow_credentials"] is False


def test_safe_headers_and_sensitive_cache_policy() -> None:
    client = TestClient(server_module.WilsyAPIServer(allowed_origins=[]).app)
    response = client.get("/api/legal-operations/instructions/missing")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Cache-Control"] == "no-store"


def test_error_handler_redacts_internal_exception() -> None:
    app = FastAPI()
    register_error_handlers(app, debug=False)

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("mongodb://user:password@atlas.example/internal")

    response = TestClient(app, raise_server_exceptions=False).get("/boom")
    assert response.status_code == 500
    body = response.text
    assert "mongodb://" not in body
    assert "atlas.example" not in body
    assert "password" not in body
    assert "Traceback" not in body


def test_jwt_secret_configuration_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WILSY_JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        jwt_provider.create_access_token({"identity_id": "p", "tenant_id": "t"})
    assert jwt_provider.verify_access_token("a.b.c") is None
    monkeypatch.setenv("WILSY_JWT_SECRET", "unit-certificate-secret")
    token = jwt_provider.create_access_token({"identity_id": "p", "tenant_id": "t"})
    decoded = jwt_provider.verify_access_token(token)
    assert isinstance(decoded, dict)
    assert decoded["tenant_id"] == "t"


def test_api_server_production_docs_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    monkeypatch.delenv("WILSY_API_DOCS_ENABLED", raising=False)
    reloaded = importlib.reload(importlib.import_module("tools.eos.api.api_server"))
    assert reloaded.app.docs_url is None
    assert reloaded.app.redoc_url is None


class _TenantScopedEmptyCollection:
    """Synthetic exact-scope empty collection for read-boundary certificates."""

    def __init__(self) -> None:
        self.queries: list[dict[str, object]] = []

    def find_one(self, query: dict[str, object], **_kwargs: object) -> None:
        """Record one exact single-record predicate and return bounded absence."""
        self.queries.append(dict(query))
        return None

    def find(
        self,
        query: dict[str, object],
        **_kwargs: object,
    ) -> tuple[dict[str, object], ...]:
        """Record one exact history predicate and return bounded empty history."""
        self.queries.append(dict(query))
        return ()


def _tenant_context(tenant_id: str = "tenant-a") -> SimpleNamespace:
    return SimpleNamespace(
        tenant_id=tenant_id,
        identity=SimpleNamespace(identity_id="principal-a"),
        decision=SimpleNamespace(business_role="tenant_legal_partner"),
    )


def test_foreign_legal_and_commercial_ids_are_bounded_not_found() -> None:
    app = FastAPI()
    app.include_router(legal_read.router)
    app.include_router(billing_read.router)
    lifecycle = _TenantScopedEmptyCollection()
    app.dependency_overrides[legal_read._INSTRUCTION_READ] = lambda: _tenant_context()
    app.dependency_overrides[legal_read._ATTEMPT_READ] = lambda: _tenant_context()
    app.dependency_overrides[legal_read._RETURN_READ] = lambda: _tenant_context()
    app.dependency_overrides[billing_read._BILLING_READ] = lambda: _tenant_context()
    app.dependency_overrides[billing_read._INVOICE_READ] = lambda: _tenant_context()
    app.dependency_overrides[legal_read.get_lifecycle_collection] = lambda: lifecycle
    app.dependency_overrides[billing_read.get_tariff_collection] = lambda: lifecycle
    app.dependency_overrides[billing_read.get_eligibility_collection] = lambda: lifecycle
    app.dependency_overrides[billing_read.get_invoice_collection] = lambda: lifecycle
    app.dependency_overrides[billing_read.get_issuance_collection] = lambda: lifecycle
    client = TestClient(app)
    paths = (
        "/legal-operations/instructions/tenant-b-identity",
        "/legal-operations/attempts/tenant-b-identity",
        "/legal-operations/executions/tenant-b-identity",
        "/legal-operations/returns/tenant-b-identity",
        "/legal-operations/tariff-assessments/tenant-b-identity",
        "/legal-operations/billing-eligibilities/tenant-b-identity",
        "/legal-operations/invoices/tenant-b-identity",
    )
    for path in paths:
        response = client.get(path)
        assert response.status_code == 404
        assert "tenant-b" not in response.text
    assert all(query.get("tenant_id") == "tenant-a" for query in lifecycle.queries)


@pytest.mark.parametrize(
    "payload",
    [
        {"attempt_authority_id": "ok", "unexpected": "field"},
        {"attempt_authority_id": 7},
        {"attempt_authority_id": None},
    ],
)
def test_hostile_command_payloads_fail_before_sovereign_mutation(payload: dict[str, object]) -> None:
    app = FastAPI()
    app.include_router(command_router.router)
    app.dependency_overrides[command_router._ATTEMPT] = lambda: _tenant_context()
    original_transaction = command_router._transaction
    command_router._transaction = lambda _callback: pytest.fail("malformed command reached persistence")
    try:
        response = TestClient(app).post("/legal-operations/attempts", json=payload)
    finally:
        command_router._transaction = original_transaction
    assert response.status_code == 422
    assert "Traceback" not in response.text
    assert "mongodb" not in response.text.lower()


@pytest.mark.parametrize("identifier", ["x" * 300, "évidence", "null"])
def test_hostile_identifiers_are_bounded(identifier: str) -> None:
    app = FastAPI()
    app.include_router(legal_read.router)
    app.dependency_overrides[legal_read._INSTRUCTION_READ] = lambda: _tenant_context()
    app.dependency_overrides[legal_read.get_lifecycle_collection] = _TenantScopedEmptyCollection
    response = TestClient(app).get(f"/legal-operations/instructions/{identifier}")
    assert response.status_code == 404
    assert "Traceback" not in response.text


# ARTIFACT: test_l7d_backend_hardening.py
# VERSION: v1.0.1-L7D-BACKEND-HARDENING-CERT
# AUTHORITY BOUNDARY: security certificate evidence only.
# TENANT POSTURE: no tenant authority is created.
# FAIL-CLOSED POSTURE: hostile defaults and internal errors are rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT