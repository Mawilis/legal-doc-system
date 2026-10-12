"""Direct unit certificate for Legal Client Acceptance HTTP parity.

TITLE: Wilsy OS Legal Client Acceptance HTTP Router Certificate
VERSION: v1.1.0-LEGAL-CLIENT-ACTIONABLE-INSTRUMENT-READ-HTTP-CERT
AUTHORITY: Wilsy OS Core Governance / authenticated HTTP certification.
EPITOME: Prove the two client-acceptance POST boundaries preserve canonical IAM,
         server-derived legal truth, transaction ownership, idempotency,
         explicit confirmation, and fail-closed HTTP translation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_acceptance_http_router.py
CERTIFICATION / UPDATE DATE: 2026-10-11
TENANT BOUNDARY: Tenant/principal derive only from TenantAuthorizationContext.
AUTHORITY BOUNDARY: HTTP transport only; canonical orchestrators own legal truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Caller authority injection, IAM denial, malformed intent,
                         orchestration rejection, or persistence failure rejects.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Awaitable, Callable

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

import tools.eos.api.legal_client_acceptance_router as http
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)


TENANT = "tenant-http-cert"
PRINCIPAL = "principal-http-cert"


def _authorization_context() -> TenantAuthorizationContext:
    identity = SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username="client",
        email="client@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    decision = TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_legal_client",
        "LEGAL_CLIENT",
    )
    return TenantAuthorizationContext(identity, TENANT, decision)


class _Repo:
    pass


_REPO = _Repo()


def _repo() -> _Repo:
    return _REPO


def _client(
    authorization: (
        Callable[[], TenantAuthorizationContext]
        | Callable[[], Awaitable[TenantAuthorizationContext]]
        | None
    ) = None,
) -> TestClient:
    app = FastAPI()
    app.include_router(http.router)
    app.dependency_overrides[http._WRITE] = (
        authorization or _authorization_context
    )
    app.dependency_overrides[http._PROVISION] = (
        authorization or _authorization_context
    )
    app.dependency_overrides[http._READ] = (
        authorization or _authorization_context
    )
    app.dependency_overrides[http.get_principal_authority_repository] = _repo
    app.dependency_overrides[http.get_tenant_membership_repository] = _repo
    app.dependency_overrides[http.get_role_assignment_repository] = _repo
    return TestClient(app)


@dataclass
class _Value:
    marker: str

    def to_dict(self) -> dict[str, str]:
        return {"marker": self.marker}


class _Database:
    def get_collection(self, name: str) -> str:
        return f"COLLECTION:{name}"


def test_exact_router_and_request_authority_surface() -> None:
    routes = sorted(
        (route.path, tuple(sorted(route.methods or set())))
        for route in http.router.routes
        if isinstance(route, APIRoute)
    )
    assert routes == sorted(
        [
            (
                "/legal-operations/client/"
                "matters/{case_matter_id}/acceptance-instruments",
                ("GET",),
            ),
            (
                "/legal-operations/client/"
                "matters/{case_matter_id}/acceptance-instruments",
                ("POST",),
            ),
            (
                "/legal-operations/client/"
                "acceptance-contexts/{acceptance_context_id}/content",
                ("GET",),
            ),
            (
                "/legal-operations/client/"
                "acceptance-contexts/{acceptance_context_id}/acceptances",
                ("POST",),
            ),
            (
                "/legal-operations/client/"
                "matters/{case_matter_id}/acceptance-contexts",
                ("POST",),
            ),
        ]
    )
    assert set(http.AcceptanceContextCommand.model_fields) == {
        "acceptance_context_id",
        "replay_key",
        "instrument_id",
    }
    assert set(http.AcceptanceCommand.model_fields) == {"confirmed"}
    assert set(http.AcceptanceInstrumentProvisioningCommand.model_fields) == {
        "instrument_id", "version", "instrument_kind", "title", "review_scope",
        "content", "media_type", "effective_from", "approval_evidence_reference",
        "approval_evidence_fingerprint", "supersedes_version_id",
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tenant_id", "attacker"),
        ("principal_id", "attacker"),
        ("party_id", "party-attacker"),
        ("capacity_id", "capacity-attacker"),
        ("acceptance_scope", "everything"),
        ("accepted_at", "2035-01-01T00:00:00Z"),
        ("content_reference", "evil://authority"),
        ("content_fingerprint", "a" * 128),
    ],
)
def test_context_rejects_caller_asserted_authority(
    field: str,
    value: str,
) -> None:
    response = _client().post(
        "/legal-operations/client/matters/matter-1/acceptance-contexts",
        json={
            "acceptance_context_id": "context-1",
            "replay_key": "replay-1",
            "instrument_id": "instrument-1",
            field: value,
        },
    )
    assert response.status_code == 422


def test_acceptance_rejects_caller_asserted_tenant() -> None:
    response = _client().post(
        "/legal-operations/client/acceptance-contexts/context-1/acceptances",
        json={"confirmed": True, "tenant_id": "attacker"},
        headers={"Idempotency-Key": "intent-1"},
    )
    assert response.status_code == 422


def test_actionable_instrument_get_forwards_only_authenticated_matter_scope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        http,
        "_transaction",
        lambda callback: callback(object(), _Database()),
    )

    def project(**kwargs: Any) -> Any:
        captured.update(kwargs)
        return _Value("actionable")

    monkeypatch.setattr(
        http,
        "project_legal_client_acceptance_instruments",
        project,
    )
    response = _client().get(
        "/legal-operations/client/matters/matter-1/acceptance-instruments"
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"marker": "actionable"}}
    assert captured["identity"].tenant_id == TENANT
    assert captured["identity"].identity_id == PRINCIPAL
    assert captured["case_matter_id"] == "matter-1"
    for forbidden in (
        "tenant_id",
        "principal_id",
        "instrument_id",
        "approval_id",
        "content_reference",
    ):
        assert forbidden not in captured


def test_provisioning_rejects_server_owned_fields() -> None:
    body = {
        "instrument_id": "instrument-1", "version": "1.0.0",
        "instrument_kind": "MATTER_REVIEW", "title": "Review",
        "review_scope": "client-information-review:v1", "content": "Terms",
        "media_type": "text/plain", "effective_from": "2030-01-01T00:00:00Z",
        "approval_evidence_reference": "authoring:one",
        "approval_evidence_fingerprint": "a" * 128,
        "tenant_id": "attacker", "content_reference": "evil://locator",
        "lifecycle_status": "ACTIVE",
    }
    response = _client().post(
        "/legal-operations/client/matters/matter-1/acceptance-instruments",
        json=body,
        headers={"Idempotency-Key": "idem-one"},
    )
    assert response.status_code == 422


def test_provisioning_forwards_only_bounded_authoring_intent(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr(http, "_transaction", lambda callback: callback(object(), _Database()))
    monkeypatch.setattr(http, "_authorization_registry", lambda database, **kwargs: object())
    def provision(**kwargs: Any) -> Any:
        captured.update(kwargs)
        item = _Value("durable")
        return SimpleNamespace(content=item, instrument=item, lifecycle=item)
    monkeypatch.setattr(http, "provision_legal_client_matter_acceptance_instrument", provision)
    response = _client().post(
        "/legal-operations/client/matters/matter-1/acceptance-instruments",
        json={"instrument_id": "instrument-1", "version": "1.0.0", "instrument_kind": "MATTER_REVIEW", "title": "Review", "review_scope": "client-information-review:v1", "content": "Terms", "media_type": "text/plain", "effective_from": "2030-01-01T00:00:00Z", "approval_evidence_reference": "authoring:one", "approval_evidence_fingerprint": "a" * 128},
        headers={"Idempotency-Key": "idem-one"},
    )
    assert response.status_code == 201
    assert captured["identity"].tenant_id == TENANT
    assert captured["case_matter_id"] == "matter-1"
    assert captured["content"] == b"Terms"
    assert captured["idempotency_key"] == "idem-one"
    for forbidden in ("tenant_id", "principal_id", "content_reference", "content_fingerprint", "lifecycle_status"):
        assert forbidden not in captured


def test_content_get_delegates_only_authenticated_context_id(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr(http, "_transaction", lambda callback: callback(object(), _Database()))
    def deliver(**kwargs: Any) -> Any:
        captured.update(kwargs)
        return SimpleNamespace(acceptance_context_id="context-1", instrument_id="instrument-1", instrument_version="1.0.0", title="Review", review_scope="Exact terms", media_type="text/plain", content="Terms", content_fingerprint="a" * 128, content_bytes=5)
    monkeypatch.setattr(http, "deliver_legal_client_acceptance_context_content", deliver)
    response = _client().get("/legal-operations/client/acceptance-contexts/context-1/content")
    assert response.status_code == 200
    assert response.text == "Terms"
    assert response.headers["content-type"].startswith("text/plain")
    assert response.headers["x-wilsy-content-fingerprint"] == "a" * 128
    assert captured["identity"].tenant_id == TENANT
    assert captured["acceptance_context_id"] == "context-1"
    for forbidden in ("tenant_id", "principal_id", "content_reference", "content_fingerprint"):
        assert forbidden not in captured


def test_context_forwards_only_canonical_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        http,
        "_transaction",
        lambda callback: callback(object(), _Database()),
    )
    monkeypatch.setattr(
        http,
        "_authorization_registry",
        lambda database, **kwargs: object(),
    )

    def compose(**kwargs: Any) -> _Value:
        captured.update(kwargs)
        return _Value("context")

    monkeypatch.setattr(
        http,
        "compose_legal_client_acceptance_context",
        compose,
    )

    response = _client().post(
        "/legal-operations/client/matters/matter-1/acceptance-contexts",
        json={
            "acceptance_context_id": "context-1",
            "replay_key": "replay-1",
            "instrument_id": "instrument-1",
        },
    )

    assert response.status_code == 201
    assert response.json() == {"data": {"marker": "context"}}
    assert captured["identity"].tenant_id == TENANT
    assert captured["identity"].identity_id == PRINCIPAL
    assert captured["case_matter_id"] == "matter-1"
    assert captured["acceptance_context_id"] == "context-1"
    assert captured["replay_key"] == "replay-1"
    assert captured["instrument_id"] == "instrument-1"

    for forbidden in (
        "tenant_id",
        "principal_id",
        "party_id",
        "capacity_id",
        "accepted_at",
        "acceptance_scope",
        "content_reference",
    ):
        assert forbidden not in captured


def test_acceptance_requires_idempotency_and_explicit_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        http,
        "_transaction",
        lambda callback: callback(object(), _Database()),
    )
    monkeypatch.setattr(
        http,
        "_authorization_registry",
        lambda database, **kwargs: object(),
    )

    def issue(**kwargs: Any) -> _Value:
        if kwargs["confirmed"] is not True:
            raise http.LegalClientAcceptanceOrchestrationError(
                "L9A3_EXPLICIT_CONFIRMATION_REQUIRED"
            )
        return _Value("acceptance")

    monkeypatch.setattr(http, "issue_legal_client_acceptance", issue)

    client = _client()

    missing = client.post(
        "/legal-operations/client/acceptance-contexts/context-1/acceptances",
        json={"confirmed": True},
    )
    assert missing.status_code == 422
    assert (
        missing.json()["detail"]
        == "LEGAL_CLIENT_ACCEPTANCE_IDEMPOTENCY_REQUIRED"
    )

    blank = client.post(
        "/legal-operations/client/acceptance-contexts/context-1/acceptances",
        json={"confirmed": True},
        headers={"Idempotency-Key": "   "},
    )
    assert blank.status_code == 422

    denied = client.post(
        "/legal-operations/client/acceptance-contexts/context-1/acceptances",
        json={"confirmed": False},
        headers={"Idempotency-Key": "intent-false"},
    )
    assert denied.status_code == 422
    assert denied.json()["detail"] == "L9A3_EXPLICIT_CONFIRMATION_REQUIRED"

    accepted = client.post(
        "/legal-operations/client/acceptance-contexts/context-1/acceptances",
        json={"confirmed": True},
        headers={"Idempotency-Key": "intent-1"},
    )
    assert accepted.status_code == 201
    assert accepted.json() == {"data": {"marker": "acceptance"}}


def test_acceptance_forwards_canonical_identity_and_intent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        http,
        "_transaction",
        lambda callback: callback(object(), _Database()),
    )
    monkeypatch.setattr(
        http,
        "_authorization_registry",
        lambda database, **kwargs: object(),
    )

    def issue(**kwargs: Any) -> _Value:
        captured.update(kwargs)
        return _Value("acceptance")

    monkeypatch.setattr(http, "issue_legal_client_acceptance", issue)

    response = _client().post(
        "/legal-operations/client/acceptance-contexts/context-1/acceptances",
        json={"confirmed": True},
        headers={"Idempotency-Key": "intent-1"},
    )
    assert response.status_code == 201
    assert captured["identity"].tenant_id == TENANT
    assert captured["identity"].identity_id == PRINCIPAL
    assert captured["acceptance_context_id"] == "context-1"
    assert captured["confirmed"] is True
    assert captured["idempotency_key"] == "intent-1"

    for forbidden in (
        "tenant_id",
        "principal_id",
        "accepted_at",
        "acceptance_scope",
    ):
        assert forbidden not in captured


@pytest.mark.parametrize(
    ("error", "status_code"),
    [
        (
            http.LegalClientAcceptanceContextOrchestrationRetryRequiredError(
                "L9A4_P2C3_WHOLE_TRANSACTION_RETRY_REQUIRED"
            ),
            409,
        ),
        (
            http.LegalClientAcceptanceOrchestrationError(
                "L9A3_ACCEPTANCE_REPLAY_CONFLICT"
            ),
            409,
        ),
        (
            http.LegalClientAcceptanceOrchestrationError(
                "L9A3_CLIENT_AUTHORIZATION_REQUIRED"
            ),
            403,
        ),
        (
            http.LegalClientAcceptanceOrchestrationError(
                "L9A3_CONTEXT_ACTOR_MISMATCH"
            ),
            403,
        ),
        (
            http.LegalClientAcceptanceOrchestrationError(
                "L9A3_CONTEXT_EXPIRED_OR_NOT_FOUND"
            ),
            404,
        ),
        (
            http.LegalClientAcceptanceOrchestrationError(
                "L9A3_ACCEPTANCE_PERSISTENCE_UNAVAILABLE"
            ),
            503,
        ),
        (
            http.LegalClientAcceptanceOrchestrationError(
                "L9A3_EXPLICIT_CONFIRMATION_REQUIRED"
            ),
            422,
        ),
    ],
)
def test_http_error_translation(
    error: BaseException,
    status_code: int,
) -> None:
    assert http._http_error(error).status_code == status_code


def test_iam_denial_blocks_both_routes() -> None:
    async def denied() -> TenantAuthorizationContext:
        raise HTTPException(
            status_code=403,
            detail="TENANT_AUTHORIZATION_DENIED",
        )

    client = _client(denied)

    context = client.post(
        "/legal-operations/client/matters/matter-1/acceptance-contexts",
        json={
            "acceptance_context_id": "context-1",
            "replay_key": "replay-1",
            "instrument_id": "instrument-1",
        },
    )
    assert context.status_code == 403

    acceptance = client.post(
        "/legal-operations/client/acceptance-contexts/context-1/acceptances",
        json={"confirmed": True},
        headers={"Idempotency-Key": "intent-1"},
    )
    assert acceptance.status_code == 403


# ARTIFACT: test_legal_client_acceptance_http_router.py
# VERSION: v1.1.0-LEGAL-CLIENT-ACTIONABLE-INSTRUMENT-READ-HTTP-CERT
# AUTHORITY BOUNDARY: authenticated transport certification only
# TENANT POSTURE: no caller tenant/principal authority
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
