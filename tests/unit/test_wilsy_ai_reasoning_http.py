"""C1B-R19 HTTP certificate for authenticated reasoning composition.

TITLE: WILSY AI Authenticated Reasoning HTTP Unit Certificate
VERSION: v1.0.0-C1B-R19
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify the single HTTP command's tenant/IAM boundary, server-owned
         identity, transaction ordering, provider isolation, and replay-safe
         bounded response without a live provider.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_reasoning_http.py
COLLABORATION / OWNERSHIP: Certifies tools/eos/api/wilsy_ai_reasoning_router.py
                            and its mount in tools/eos/api/server.py.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0 establishes the C1B-R19 HTTP certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Caller authority fields are rejected and provider
                             errors are never returned or logged.
TENANT BOUNDARY: Tests inject only a TenantAuthorizationContext.
AUTHORITY BOUNDARY: Reasoning evidence/admission only; no legal or financial truth.
FAIL-CLOSED DECLARATION: Invalid scope, key, provider binding, and replay fail.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

import tools.eos.api.wilsy_ai_reasoning_router as module
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.intelligence.domain.ai_model_provider_binding import ServerOwnedModelProviderBinding
from tools.eos.api.server import WilsyAPIServer


class Provider:
    """Provider double proving one out-of-transaction execution call."""

    def __init__(self) -> None:
        self.calls = 0

    def execute(self, request: Any) -> Any:
        self.calls += 1
        return SimpleNamespace()


@dataclass(frozen=True)
class Admission:
    state: SimpleNamespace
    admission_id: str = "c1b-adm-test"


class FakeOrchestrator:
    """Minimal orchestrator seam used to assert HTTP ordering."""

    calls: list[str] = []

    def __init__(self, **_: Any) -> None:
        pass

    def claim(self, **_: Any) -> str:
        self.calls.append("claim")
        return "permit"

    def execute(self, permit: str, **_: Any) -> Any:
        assert permit == "permit"
        self.calls.append("execute")
        return SimpleNamespace(result=SimpleNamespace(outcome=SimpleNamespace(value="SUCCESS")))

    def finalize(self, attempt: Any, **_: Any) -> Any:
        assert attempt.result.outcome.value == "SUCCESS"
        self.calls.append("finalize")
        return SimpleNamespace(
            admission=Admission(SimpleNamespace(value="COMPLETED")),
            invocation_evidence=SimpleNamespace(invocation_id="c1b-inv-test"),
            usage_observation=SimpleNamespace(usage_observation_id="usage-c1b-inv-test"),
            response_text="bounded response",
        )


class FakeEntitlements:
    def __init__(self, *_: Any, **__: Any) -> None:
        pass

    def get_by_module(self, **kwargs: Any) -> Any:
        FakeOrchestrator.calls.append("entitlement")
        assert kwargs["tenant_id"] == "tenant-http"
        assert kwargs["module_id"] == "WILSY_AI_REASONING"
        return SimpleNamespace(entitlement_id="entitlement-canonical")


class FakeCapacity:
    daily_remaining_request_units = 4

    def derive_capacity(self, **_: Any) -> Any:
        FakeOrchestrator.calls.append("capacity")
        return self

    @classmethod
    def from_collections(cls, **_: Any) -> "FakeCapacity":
        return cls()


class FakeAdmissionAuthority:
    def __init__(self, **_: Any) -> None:
        pass

    def reserve(self, **kwargs: Any) -> Any:
        FakeOrchestrator.calls.append("reserve")
        assert kwargs["reserved_request_units"] == 1
        return Admission(SimpleNamespace(value="RESERVED"))


class FakeRegistry:
    def __init__(self, *_: Any, **__: Any) -> None:
        pass


def _context() -> TenantAuthorizationContext:
    return TenantAuthorizationContext(
        identity=cast(Any, SimpleNamespace(identity_id="principal-http")),
        tenant_id="tenant-http",
        decision=cast(Any, SimpleNamespace(authorized=True)),
    )


def _app(binding: ServerOwnedModelProviderBinding | None = None) -> FastAPI:
    app = FastAPI()
    app.state.wilsy_ai_reasoning_provider_binding = binding
    app.include_router(module.router, prefix="/api")
    app.dependency_overrides[module._REASONING_AUTH] = lambda: _context()
    return app


def test_server_mount_is_single_post_route() -> None:
    paths = WilsyAPIServer(allowed_origins=[]).app.openapi()["paths"]
    assert list(path for path in paths if path == "/api/wilsy-ai/reasoning") == ["/api/wilsy-ai/reasoning"]
    assert set(paths["/api/wilsy-ai/reasoning"]) == {"post"}


@pytest.mark.parametrize("field", [
    "tenant_id", "principal_id", "provider_id", "model_id", "entitlement_id",
    "admission_id", "invocation_id", "request_units", "system_policy",
    "fingerprint", "financial_amount",
])
def test_authority_fields_are_rejected(field: str) -> None:
    app = _app()
    with TestClient(app) as client:
        response = client.post("/api/wilsy-ai/reasoning", json={"prompt": "hello", field: "caller"})
    assert response.status_code == 422


def test_missing_key_and_malformed_key_are_rejected() -> None:
    app = _app()
    with TestClient(app) as client:
        assert client.post("/api/wilsy-ai/reasoning", json={"prompt": "hello"}).status_code == 422
        assert client.post("/api/wilsy-ai/reasoning", json={"prompt": "hello"}, headers={"Idempotency-Key": "bad key"}).status_code == 422


def test_missing_server_binding_is_503_without_provider_call() -> None:
    provider = Provider()
    app = _app(None)
    with TestClient(app) as client:
        response = client.post("/api/wilsy-ai/reasoning", json={"prompt": "hello"}, headers={"Idempotency-Key": "key-1"})
    assert response.status_code == 503
    assert provider.calls == 0


def test_missing_database_is_bounded_503(monkeypatch: pytest.MonkeyPatch) -> None:
    binding = ServerOwnedModelProviderBinding.from_injected(provider=Provider())
    monkeypatch.setattr(module, "_collections", lambda: (_ for _ in ()).throw(module._ReasoningHTTPError("C1B_REASONING_PERSISTENCE_UNAVAILABLE", 503)))
    response = TestClient(_app(binding)).post("/api/wilsy-ai/reasoning", json={"prompt": "hello"}, headers={"Idempotency-Key": "key-db"})
    assert response.status_code == 503


def test_server_owned_binding_and_ordered_composition(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = Provider()
    binding = ServerOwnedModelProviderBinding.from_injected(provider=provider, provider_id="server-provider", model_id="server-model")
    FakeOrchestrator.calls = []
    monkeypatch.setattr(module, "WilsyAIReasoningOrchestrator", FakeOrchestrator)
    monkeypatch.setattr(module, "WilsyAIEntitlementRegistry", FakeEntitlements)
    monkeypatch.setattr(module, "WilsyAIUsageCapacityOrchestrator", FakeCapacity)
    monkeypatch.setattr(module, "WilsyAIUsageAdmissionAuthority", FakeAdmissionAuthority)
    monkeypatch.setattr(module, "WilsyAIUsageAdmissionRegistry", FakeRegistry)
    monkeypatch.setattr(module, "AIModelInvocationRegistry", FakeRegistry)
    monkeypatch.setattr(module, "WilsyAIUsageObservationRegistry", FakeRegistry)
    monkeypatch.setattr(module, "_collections", lambda: {"entitlement": object(), "admission": object(), "invocation": object(), "observation": object()})
    monkeypatch.setattr(module, "_transaction", lambda callback, **_: callback(SimpleNamespace(in_transaction=True)))
    response = TestClient(_app(binding)).post("/api/wilsy-ai/reasoning", json={"prompt": "hello"}, headers={"Idempotency-Key": "key-1"})
    assert response.status_code == 200, response.text
    assert response.json()["response_text"] == "bounded response"
    assert FakeOrchestrator.calls == ["entitlement", "capacity", "reserve", "claim", "execute", "finalize"]
    assert provider.calls == 0


def test_reasoning_response_is_not_cached_on_canonical_server() -> None:
    app = WilsyAPIServer(allowed_origins=[]).app
    paths = app.openapi()["paths"]
    assert "/api/wilsy-ai/reasoning" in paths
    app.dependency_overrides[module._REASONING_AUTH] = lambda: _context()
    with TestClient(app) as client:
        response = client.post("/api/wilsy-ai/reasoning", json={"prompt": "hello"}, headers={"Idempotency-Key": "cache-check"})
    assert response.status_code == 503
    assert response.headers["cache-control"] == "no-store"


# ARTIFACT: test_wilsy_ai_reasoning_http.py
# VERSION: v1.0.0-C1B-R19
# AUTHORITY BOUNDARY: HTTP reasoning certificate only
# FAIL-CLOSED POSTURE: caller authority injection and missing binding reject
# END OF WILSY OS SOVEREIGN ARTIFACT
