"""P12C mounted FastAPI practitioner-binding transport certificate.

Authority: HTTP authentication, bounded request admission and service routing.
Database/service behavior is isolated by controlled test dependencies.
No simulated authorization result is a production authorization grant.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tools.eos.api.errors import register_error_handlers
from tools.eos.api import legal_practitioner_matter_binding_router as api


GRANT = "/api/legal-operations/practitioner-bindings"
REVOKE = GRANT + "/revocations"


def grant_payload():
    """Produce bounded client intent without authority-bearing fields."""
    return {
        "case_matter_id": "matter-A",
        "practitioner_principal_id": "lawyer-A",
        "binding_id": "binding-A",
        "access_evidence_id": "evidence-A",
        "expected_access_evidence_fingerprint": "a" * 128,
    }


def revoke_payload():
    """Produce bounded revocation intent."""
    return {
        "binding_id": "binding-A",
        "evidence_reference": "revocation-A",
    }


@pytest.fixture()
def app():
    """Mount only the actual router and clear all overrides after use."""
    application = FastAPI()
    register_error_handlers(application, debug=False)
    application.include_router(api.router, prefix="/api")
    yield application
    application.dependency_overrides.clear()


@pytest.fixture()
def authorized_app(app):
    """Override IAM only for isolated transport-behavior proofs."""
    app.dependency_overrides[api._PROVISION] = lambda: SimpleNamespace(
        tenant_id="tenant-A",
        identity=SimpleNamespace(identity_id="partner-A"),
    )
    return app


@pytest.mark.parametrize(
    "path,payload",
    [
        (GRANT, grant_payload()),
        (REVOKE, revoke_payload()),
    ],
)
def test_anonymous_request_rejected_by_real_authentication(
    app, monkeypatch, path, payload
):
    """No token must not reach persistence or the provisioning service."""
    def forbidden(*args, **kwargs):
        pytest.fail("UNAUTHENTICATED_REQUEST_REACHED_COMMAND")

    monkeypatch.setattr(api, "_transaction", forbidden)

    with TestClient(app) as client:
        response = client.post(path, json=payload)

    assert response.status_code in (401, 403)


@pytest.mark.parametrize(
    "path,payload",
    [
        (GRANT, grant_payload()),
        (REVOKE, revoke_payload()),
    ],
)
def test_authenticated_context_does_not_allow_extra_authority(
    authorized_app, monkeypatch, path, payload
):
    """Even an admitted test context cannot inject actor or tenant fields."""
    monkeypatch.setattr(
        api,
        "_transaction",
        lambda callback: pytest.fail(
            "INVALID_COMMAND_REACHED_TRANSACTION"
        ),
    )
    payload = {**payload, "tenant_id": "foreign-tenant"}

    with TestClient(authorized_app) as client:
        response = client.post(path, json=payload)

    assert response.status_code == 422


def test_mounted_revoke_forwards_authenticated_context(
    authorized_app, monkeypatch
):
    """A mounted revocation uses only the trusted dependency's identity."""
    observed = {}

    def transaction(callback):
        return callback(None, object())

    def fake_revoke(**kwargs):
        observed.update(kwargs)
        return SimpleNamespace(
            to_dict=lambda: {"status": "REVOKED"}
        )

    monkeypatch.setattr(api, "_transaction", transaction)
    monkeypatch.setattr(
        api, "_collection", lambda database, name: name
    )
    monkeypatch.setattr(api, "revoke_binding", fake_revoke)

    with TestClient(authorized_app) as client:
        response = client.post(REVOKE, json=revoke_payload())

    assert response.status_code == 201
    assert response.json() == {"status": "REVOKED"}
    assert observed["tenant_id"] == "tenant-A"
    assert observed["authenticated_principal_id"] == "partner-A"


def test_mounted_grant_rejects_missing_canonical_evidence(
    authorized_app, monkeypatch
):
    """Missing persisted evidence cannot reach the binding write service."""
    monkeypatch.setattr(
        api, "_transaction", lambda callback: callback(None, object())
    )
    monkeypatch.setattr(
        api, "_collection", lambda database, name: name
    )
    monkeypatch.setattr(api, "get_by_id", lambda **kwargs: None)
    monkeypatch.setattr(
        api,
        "grant_binding",
        lambda **kwargs: pytest.fail(
            "MISSING_EVIDENCE_REACHED_BINDING_SERVICE"
        ),
    )

    with TestClient(authorized_app) as client:
        response = client.post(GRANT, json=grant_payload())

    assert response.status_code == 403


# ARTIFACT: test_legal_practitioner_matter_binding_fastapi.py
# VERSION: v1.0.0-P12C-R4E-MOUNTED-FASTAPI-CERTIFICATE
# AUTHORITY BOUNDARY: test-only HTTP transport and authentication proofs
# TENANT POSTURE: request fields cannot assert tenant authority
# FAIL-CLOSED POSTURE: missing credentials and evidence reject
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
