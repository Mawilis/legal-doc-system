"""HTTP certificates for session-bound Deputy P-256 device proof commands.

AUTHORITY: Transport composition only; L8-6H and current IAM remain authoritative.
TENANT: Synthetic exact tenant/principal/session only.
FINANCIAL: No financial authority.
"""
from __future__ import annotations

import base64
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import tools.eos.api.legal_operations_command_router as command_api
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)

TENANT = "tenant-device-http"
PRINCIPAL = "principal-device-http"
DEPUTY = "deputy-device-http"
SESSION = "WILSYSESSION-device-http"


class ActiveSession:
    in_transaction = True


class Database:
    def __init__(self) -> None:
        self.names: list[str] = []

    def get_collection(self, name: str) -> object:
        self.names.append(name)
        return SimpleNamespace(name=name)


def context(*, session_reference: str | None = SESSION) -> TenantAuthorizationContext:
    identity = SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username="deputy",
        email="deputy@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
        session_reference=session_reference,
    )
    decision = TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_deputy",
        "DEPUTY",
    )
    return TenantAuthorizationContext(identity, TENANT, decision)


def app_for(value: TenantAuthorizationContext) -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.dependency_overrides[command_api._ATTEMPT] = lambda: value
    app.include_router(command_api.router, prefix="/api")
    return app


def test_issue_route_uses_server_identity_session_binding_and_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = Database()
    session = ActiveSession()
    calls: list[dict[str, Any]] = []
    challenge = SimpleNamespace(
        to_dict=lambda: {
            "challenge_id": "challenge-http",
            "tenant_id": TENANT,
            "principal_id": PRINCIPAL,
            "deputy_id": DEPUTY,
        }
    )

    monkeypatch.setattr(
        command_api, "_transaction",
        lambda callback: callback(session, database),
    )
    monkeypatch.setattr(
        command_api, "_deputy_device_scope",
        lambda supplied_context, supplied_db, supplied_session: DEPUTY,
    )

    def issue(**kwargs: Any) -> object:
        calls.append(kwargs)
        return challenge

    monkeypatch.setattr(command_api, "issue_deputy_device_challenge", issue)
    public_key = b"synthetic-public-key-der"

    with TestClient(app_for(context())) as client:
        response = client.post(
            "/api/legal-operations/deputy/device-challenges",
            json={"public_key_spki_b64": base64.b64encode(public_key).decode("ascii")},
        )

    assert response.status_code == 200
    assert response.json()["data"]["challenge_id"] == "challenge-http"
    assert len(calls) == 1
    assert calls[0]["tenant_id"] == TENANT
    assert calls[0]["principal_id"] == PRINCIPAL
    assert calls[0]["deputy_id"] == DEPUTY
    assert calls[0]["session_reference"] == SESSION
    assert calls[0]["public_key_spki_der"] == public_key
    assert calls[0]["session"] is session
    assert calls[0]["auth_registry"].__class__ is command_api.AuthRegistry
    assert calls[0]["challenge_collection"].name == "legal_operations_deputy_device_provenance_challenges"
    assert "tenant_id" not in response.json()["data"] or response.json()["data"]["tenant_id"] == TENANT


def test_verify_route_consumes_exact_p1363_signature_under_same_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = Database()
    session = ActiveSession()
    calls: list[dict[str, Any]] = []
    proof = SimpleNamespace(
        to_dict=lambda: {
            "challenge_id": "challenge-http",
            "principal_id": PRINCIPAL,
            "device_id": "device-http",
        }
    )

    monkeypatch.setattr(
        command_api, "_transaction",
        lambda callback: callback(session, database),
    )
    monkeypatch.setattr(
        command_api, "_deputy_device_scope",
        lambda supplied_context, supplied_db, supplied_session: DEPUTY,
    )

    def verify(**kwargs: Any) -> object:
        calls.append(kwargs)
        return proof

    monkeypatch.setattr(command_api, "verify_and_consume_deputy_device_challenge", verify)
    signature = b"S" * 64

    with TestClient(app_for(context())) as client:
        response = client.post(
            "/api/legal-operations/deputy/device-challenges/challenge-http/verify",
            json={"signature_p1363_b64": base64.b64encode(signature).decode("ascii")},
        )

    assert response.status_code == 200
    assert response.json()["data"]["device_id"] == "device-http"
    assert len(calls) == 1
    assert calls[0]["tenant_id"] == TENANT
    assert calls[0]["principal_id"] == PRINCIPAL
    assert calls[0]["deputy_id"] == DEPUTY
    assert calls[0]["session_reference"] == SESSION
    assert calls[0]["challenge_id"] == "challenge-http"
    assert calls[0]["signature_p1363"] == signature
    assert calls[0]["session"] is session


def test_routes_reject_browser_supplied_authority_and_malformed_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with TestClient(app_for(context())) as client:
        extra_authority = client.post(
            "/api/legal-operations/deputy/device-challenges",
            json={
                "public_key_spki_b64": base64.b64encode(b"public-key").decode("ascii"),
                "tenant_id": "attacker-tenant",
            },
        )
        malformed_signature = client.post(
            "/api/legal-operations/deputy/device-challenges/challenge/verify",
            json={"signature_p1363_b64": base64.b64encode(b"short").decode("ascii")},
        )

    assert extra_authority.status_code == 422
    assert malformed_signature.status_code == 422


def test_device_proof_requires_session_reference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        command_api,
        "_bound_deputy",
        lambda *_args, **_kwargs: SimpleNamespace(deputy_id=DEPUTY),
    )
    with pytest.raises(command_api.CommandError) as error:
        command_api._deputy_device_scope(
            context(session_reference=None),
            Database(),
            ActiveSession(),
        )
    assert error.value.code == "DEPUTY_DEVICE_CURRENT_SESSION_REFERENCE_REQUIRED"




def test_location_permission_route_consumes_device_proof_and_creates_short_grant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = Database()
    session = ActiveSession()
    calls: list[dict[str, Any]] = []
    proof = SimpleNamespace(device_id="deputy-device:synthetic")
    grant = SimpleNamespace(
        to_dict=lambda: {
            "tenant_id": TENANT, "attempt_id": "attempt-http",
            "grant_id": "grant-http", "device_id": "deputy-device:synthetic",
            "purpose": "PROCESS_SERVICE_ATTEMPT_FIELD_EVIDENCE",
        },
        fingerprint="a" * 128,
    )
    monkeypatch.setattr(command_api, "_transaction", lambda callback: callback(session, database))
    monkeypatch.setattr(command_api, "_location_attempt_sources", lambda *args: (
        SimpleNamespace(attempt_id="attempt-http"), object(), object()
    ))
    monkeypatch.setattr(command_api, "_deputy_device_scope", lambda *args: DEPUTY)
    monkeypatch.setattr(command_api, "_verify_location_device_proof", lambda **kwargs: proof)

    def issue(**kwargs: Any) -> object:
        calls.append(kwargs)
        return grant

    monkeypatch.setattr(command_api, "issue_process_service_location_permission_grant", issue)
    with TestClient(app_for(context())) as client:
        response = client.post(
            "/api/legal-operations/deputy/attempts/attempt-http/location-permission-grants",
            json={
                "current_evidence_identity": "p2-current-http",
                "grant_id": "grant-http",
                "challenge_id": "challenge-http",
                "signature_p1363_b64": base64.b64encode(b"C" * 64).decode("ascii"),
                "permission_granted": True,
                "permission_notice_version": "P5L-LOCATION-NOTICE-V1",
            },
        )
    assert response.status_code == 200
    assert response.json()["data"]["grant_id"] == "grant-http"
    assert len(calls) == 1
    assert calls[0]["principal_id"] == PRINCIPAL
    assert calls[0]["device_provenance"] is proof
    assert calls[0]["permission_granted"] is True
    assert calls[0]["permission_notice_version"] == "P5L-LOCATION-NOTICE-V1"
    assert calls[0]["session"] is session


def test_location_capture_route_requires_both_challenge_and_gps_signatures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = Database()
    session = ActiveSession()
    calls: list[dict[str, Any]] = []
    proof = SimpleNamespace(device_id="deputy-device:synthetic")
    observation = SimpleNamespace(
        to_dict=lambda: {
            "tenant_id": TENANT, "attempt_id": "attempt-http",
            "observation_id": "observation-http", "latitude": -26.2,
            "longitude": 28.0, "horizontal_accuracy_m": 8.0,
        },
        fingerprint="b" * 128,
    )
    monkeypatch.setattr(command_api, "_transaction", lambda callback: callback(session, database))
    monkeypatch.setattr(command_api, "_location_attempt_sources", lambda *args: (
        SimpleNamespace(attempt_id="attempt-http"), object(), object()
    ))
    monkeypatch.setattr(command_api, "_deputy_device_scope", lambda *args: DEPUTY)
    monkeypatch.setattr(command_api, "_verify_location_device_proof", lambda **kwargs: proof)

    def record(**kwargs: Any) -> object:
        calls.append(kwargs)
        return observation

    monkeypatch.setattr(command_api, "record_process_service_location_observation", record)
    signature = base64.b64encode(b"S" * 64).decode("ascii")
    with TestClient(app_for(context())) as client:
        response = client.post(
            "/api/legal-operations/deputy/attempts/attempt-http/location-evidence",
            json={
                "current_evidence_identity": "p2-current-http",
                "grant_id": "grant-http",
                "observation_id": "observation-http",
                "challenge_id": "challenge-http",
                "signature_p1363_b64": signature,
                "location_signature_p1363_b64": signature,
                "latitude": -26.2,
                "longitude": 28.0,
                "horizontal_accuracy_m": 8.0,
                "captured_at": "2026-11-02T10:00:00.000Z",
            },
        )
    assert response.status_code == 200
    assert response.json()["data"]["observation_id"] == "observation-http"
    assert len(calls) == 1
    assert calls[0]["current_evidence_identity"] == "p2-current-http"
    assert calls[0]["location_signature_p1363"] == b"S" * 64
    assert calls[0]["device_provenance"] is proof
    assert calls[0]["principal_id"] == PRINCIPAL
    assert calls[0]["session"] is session


def test_location_commands_reject_permission_denial_and_extra_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(command_api, "_transaction", lambda callback: pytest.fail("must not open transaction"))
    signature = base64.b64encode(b"S" * 64).decode("ascii")
    with TestClient(app_for(context())) as client:
        denied = client.post(
            "/api/legal-operations/deputy/attempts/attempt-http/location-permission-grants",
            json={
                "current_evidence_identity": "p2-current-http",
                "grant_id": "grant-http",
                "challenge_id": "challenge-http",
                "signature_p1363_b64": signature,
                "permission_granted": False,
                "permission_notice_version": "P5L-LOCATION-NOTICE-V1",
            },
        )
        injected = client.post(
            "/api/legal-operations/deputy/attempts/attempt-http/location-evidence",
            json={
                "current_evidence_identity": "p2-current-http",
                "grant_id": "grant-http",
                "observation_id": "observation-http",
                "challenge_id": "challenge-http",
                "signature_p1363_b64": signature,
                "location_signature_p1363_b64": signature,
                "latitude": -26.2,
                "longitude": 28.0,
                "horizontal_accuracy_m": 8.0,
                "captured_at": "2026-11-02T10:00:00.000Z",
                "tenant_id": "attacker-tenant",
            },
        )
    assert denied.status_code == 403
    assert injected.status_code == 422

# ARTIFACT: test_deputy_device_provenance_http.py
# VERSION: v1.0.0-L8-6H-DEVICE-PROOF-HTTP-CERT
# AUTHORITY BOUNDARY: HTTP composition and server-derived session/deputy scope only.
# FAIL-CLOSED POSTURE: caller authority injection, missing session and malformed proof reject.
# END OF WILSY OS SOVEREIGN ARTIFACT
