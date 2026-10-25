from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi import FastAPI
from starlette.requests import Request
import pytest

from tools.eos.api.legal_evidence_provider_readonly_reconciliation_router import (
    _operation_key,
    reconcile_legal_evidence_provider,
    router,
)


def test_operation_key_is_read_from_signed_body_contract() -> None:
    assert _operation_key(b'{"idempotency_key":"reconcile-2026-10-25"}') == "reconcile-2026-10-25"


@pytest.mark.parametrize(
    "body",
    [
        b'{"idempotency_key":"first","idempotency_key":"second"}',
        b'{"idempotency_key":"valid","tenant_id":"caller-selected"}',
        b'{"idempotency_key":""}',
        b'{"idempotency_key":"contains space"}',
        b'{"idempotency_key":"wildcard*"}',
        b'{"idempotency_key":17}',
        b'[]',
        b'not-json',
        b'{"idempotency_key":"\xff"}',
    ],
)
def test_operation_key_rejects_ambiguous_or_invalid_signed_body(body: bytes) -> None:
    with pytest.raises(ValueError):
        _operation_key(body)


def test_reconciliation_readiness_fails_closed_without_verified_composition() -> None:
    from tools.eos.api.legal_evidence_provider_readonly_reconciliation_router import (
        reconciliation_readiness,
    )

    app = FastAPI()
    app.state.legal_evidence_provider_readonly_reconciliation_composition = None
    app.state.legal_evidence_provider_readonly_reconciliation_audit_client = None
    response = asyncio.run(reconciliation_readiness(_request_for_route(app)))
    assert response.status_code == 503
    assert json.loads(response.body) == {
        "success": False,
        "code": "RECONCILIATION_COMPOSITION_UNAVAILABLE",
    }


def test_route_fails_closed_when_deployment_composition_is_not_injected() -> None:
    app = FastAPI()
    app.include_router(router, prefix="/api")
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/legal-operations/evidence-provider/reconciliation",
        "raw_path": b"/api/legal-operations/evidence-provider/reconciliation",
        "query_string": b"",
        "root_path": "",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "app": app,
    }
    request = Request(scope, receive=lambda: None)
    response = asyncio.run(reconcile_legal_evidence_provider(request))
    assert response.status_code == 503
    assert json.loads(response.body) == {
        "success": False,
        "code": "RECONCILIATION_COMPOSITION_UNAVAILABLE",
    }


class _Session:
    def __init__(self) -> None:
        self.in_transaction = False
        self.events: list[str] = []

    def start_transaction(self) -> None:
        self.in_transaction = True
        self.events.append("start")

    def commit_transaction(self) -> None:
        self.events.append("commit")
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.events.append("abort")
        self.in_transaction = False

    def end_session(self) -> None:
        self.events.append("end")


class _Client:
    def __init__(self) -> None:
        self.session = _Session()

    def start_session(self) -> _Session:
        return self.session


class _Composition:
    def __init__(self, *, fail: bool = False) -> None:
        self.business_client = _Client()
        self.fail = fail
        self.calls = []

    def authorize_and_reconcile_idempotently(self, **kwargs):
        self.calls.append(kwargs)
        if self.fail:
            raise RuntimeError("test-only failure")
        return {
            "tenant_id": "tenant-1",
            "coverage_verification_fingerprint": "coverage-fp",
            "completed_observation_count": 2,
        }


def _request_for_route(app: FastAPI) -> Request:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/legal-operations/evidence-provider/reconciliation",
        "raw_path": b"/api/legal-operations/evidence-provider/reconciliation",
        "query_string": b"",
        "root_path": "",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "app": app,
    }
    return Request(scope, receive=lambda: None)


def test_route_commits_only_after_composition_returns(monkeypatch) -> None:
    from tools.eos.api import legal_evidence_provider_readonly_reconciliation_router as module

    app = FastAPI()
    composition = _Composition()
    app.state.legal_evidence_provider_readonly_reconciliation_composition = composition
    envelope = SimpleNamespace(
        request={"service_id": "trusted-service"},
        body=b'{"idempotency_key":"operation-1"}',
        observed_at=datetime(2026, 10, 25, tzinfo=timezone.utc),
    )

    async def extract(_request):
        return envelope

    monkeypatch.setattr(module, "LegalEvidenceProviderReadOnlyReconciliationProductionComposition", _Composition)
    monkeypatch.setattr(module, "extract_signed_workload_request", extract)
    response = asyncio.run(module.reconcile_legal_evidence_provider(_request_for_route(app)))
    assert response.status_code == 200
    assert json.loads(response.body)["data"]["coverage_verification_fingerprint"] == "coverage-fp"
    assert composition.business_client.session.events == ["start", "commit", "end"]


def test_route_aborts_business_transaction_on_composition_failure(monkeypatch) -> None:
    from tools.eos.api import legal_evidence_provider_readonly_reconciliation_router as module

    app = FastAPI()
    composition = _Composition(fail=True)
    app.state.legal_evidence_provider_readonly_reconciliation_composition = composition
    envelope = SimpleNamespace(
        request={"service_id": "trusted-service"},
        body=b'{"idempotency_key":"operation-1"}',
        observed_at=datetime(2026, 10, 25, tzinfo=timezone.utc),
    )

    async def extract(_request):
        return envelope

    monkeypatch.setattr(module, "LegalEvidenceProviderReadOnlyReconciliationProductionComposition", _Composition)
    monkeypatch.setattr(module, "extract_signed_workload_request", extract)
    response = asyncio.run(module.reconcile_legal_evidence_provider(_request_for_route(app)))
    assert response.status_code == 409
    assert composition.business_client.session.events == ["start", "abort", "end"]


def test_route_surfaces_authorization_audit_outage_as_503(monkeypatch) -> None:
    from tools.eos.api import legal_evidence_provider_readonly_reconciliation_router as module
    from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_authorization_gate import (
        LegalEvidenceProviderReadOnlyReconciliationAuthorizationError,
    )

    class _AuditUnavailableComposition(_Composition):
        def authorize_and_reconcile_idempotently(self, **kwargs):
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "AUTHORIZATION_AUDIT_DURABILITY_UNAVAILABLE"
            )

    app = FastAPI()
    composition = _AuditUnavailableComposition()
    app.state.legal_evidence_provider_readonly_reconciliation_composition = composition
    envelope = SimpleNamespace(
        request={"service_id": "trusted-service"},
        body=b'{"idempotency_key":"operation-1"}',
        observed_at=datetime(2026, 10, 25, tzinfo=timezone.utc),
    )

    async def extract(_request):
        return envelope

    monkeypatch.setattr(module, "LegalEvidenceProviderReadOnlyReconciliationProductionComposition", _AuditUnavailableComposition)
    monkeypatch.setattr(module, "extract_signed_workload_request", extract)
    response = asyncio.run(module.reconcile_legal_evidence_provider(_request_for_route(app)))
    assert response.status_code == 503
    assert json.loads(response.body)["code"] == "RECONCILIATION_AUTHORIZATION_AUDIT_UNAVAILABLE"
    assert composition.business_client.session.events == ["start", "abort", "end"]


def test_canonical_eos_server_mounts_exact_reconciliation_path_once() -> None:
    from tools.eos.api.server import app as canonical_app

    from fastapi.routing import APIRoute, _iter_routes_with_context

    routes = []
    for route, context in _iter_routes_with_context(canonical_app.routes):
        if not isinstance(route, APIRoute):
            continue
        path = context.path if context is not None else route.path
        methods = context.methods if context is not None else (route.methods or set())
        if path == "/api/legal-operations/evidence-provider/reconciliation" and "POST" in methods:
            routes.append(route)
    assert len(routes) == 1
    assert routes[0].endpoint.__module__ == (
        "tools.eos.api.legal_evidence_provider_readonly_reconciliation_router"
    )
