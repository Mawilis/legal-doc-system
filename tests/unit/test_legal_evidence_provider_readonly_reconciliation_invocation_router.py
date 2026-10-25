from __future__ import annotations

import asyncio
import json

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
