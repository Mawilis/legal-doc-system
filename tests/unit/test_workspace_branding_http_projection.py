"""Direct certificate for D21B7 workspace-branding HTTP projection.

TITLE: Workspace Branding HTTP Projection Direct Certificate
VERSION: v1.0.0-D21B7-TENANT-BRANDING-WORKSPACE-HTTP-PROJECTION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove authenticated workspace-bootstrap transports only D21B6 branding
         truth and owns a bounded fresh-session read-transaction/retry boundary.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_workspace_branding_http_projection.py
COLLABORATION / OWNERSHIP: D21B6 owns current-branding composition; auth_router
                            owns only HTTP/session orchestration and response
                            projection. This certificate grants no branding truth.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B7-TENANT-BRANDING-WORKSPACE-HTTP-PROJECTION-CERT
           establishes exact collection wiring, same-session propagation,
           read-only abort/end lifecycle, fresh-session retry and exhaustion,
           explicit null absence, configured transport, and bounded 503 evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic projection metadata only; no asset bytes,
                             secrets, network providers or durable customer data.
TENANT BOUNDARY: The router forwards only the already-revalidated workspace
                 tenant_id into D21B6 and cannot accept browser tenant branding.
AUTHORITY BOUNDARY: HTTP projection and transaction ownership only; no IAM,
                    entitlement, profile, asset-upload, legal or financial truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from tools.eos.api import auth_router
from tools.eos.auth.tenant_branding_workspace_projection import (
    TenantBrandingWorkspaceProjectionError,
    TenantBrandingWorkspaceProjectionRetryRequiredError,
)
from tools.eos.kernel import db as kernel_db


TENANT = "tenant-d21b7"
PRINCIPAL = "principal-d21b7"


def _branding_payload() -> dict[str, object]:
    """Return one browser-safe synthetic D21B6 transport payload."""
    return {
        "tenantId": TENANT,
        "profileId": "profile-primary",
        "profileFingerprint": "a" * 128,
        "selectionId": "selection-1",
        "selectionRevision": 1,
        "entitlementId": "branding-entitlement-1",
        "entitlementRevision": 1,
        "entitlementFingerprint": "b" * 128,
        "brandingTier": "TENANT_BRANDING_INSTITUTIONAL",
        "profileLabel": "Primary brand",
        "primaryColor": "#112233",
        "secondaryColor": "#445566",
        "accentColor": "#AABBCC",
        "emailDisplayName": "Acme Legal",
        "platformTrustMarkRequired": True,
        "logo": {
            "reference": f"asset:{TENANT}:logo:primary",
            "contentFingerprint": "c" * 128,
            "mediaType": "image/png",
            "kind": "LOGO",
        },
        "favicon": {
            "reference": f"asset:{TENANT}:favicon:primary",
            "contentFingerprint": "d" * 128,
            "mediaType": "image/png",
            "kind": "FAVICON",
        },
    }


class _Session:
    """Minimal caller-owned transaction fixture with lifecycle evidence."""

    def __init__(self) -> None:
        self.in_transaction = False
        self.started = 0
        self.aborted = 0
        self.ended = 0

    def start_transaction(self) -> None:
        self.started += 1
        self.in_transaction = True

    def abort_transaction(self) -> None:
        self.aborted += 1
        self.in_transaction = False

    def end_session(self) -> None:
        self.ended += 1


class _Client:
    """Create one fresh synthetic session per transaction attempt."""

    def __init__(self) -> None:
        self.sessions: list[_Session] = []

    def start_session(self) -> _Session:
        session = _Session()
        self.sessions.append(session)
        return session


class _Database:
    """Return stable collection sentinels and record exact requested names."""

    def __init__(self) -> None:
        self.collections: dict[str, object] = {}
        self.requested: list[str] = []

    def __getitem__(self, name: str) -> object:
        self.requested.append(name)
        return self.collections.setdefault(name, object())


class _BrandingProjection:
    """Synthetic D21B6 result exposing only the public serialization seam."""

    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def to_dict(self) -> dict[str, object]:
        return dict(self.payload)


def _install_kernel(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[_Client, _Database]:
    """Bind D21B7 dynamic kernel lookups to deterministic fixtures."""
    client = _Client()
    database = _Database()
    monkeypatch.setattr(kernel_db, "get_client", lambda: client)
    monkeypatch.setattr(kernel_db, "get_database", lambda: database)
    return client, database


def _expected_collection_names() -> set[str]:
    """Return the exact six canonical D21B6 collection dependencies."""
    return {
        auth_router.BRANDING_ENTITLEMENT_HISTORY_COLLECTION,
        auth_router.BRANDING_ENTITLEMENT_CURRENT_COLLECTION,
        auth_router.BRANDING_PROFILE_COLLECTION,
        auth_router.BRANDING_SELECTION_COLLECTION,
        auth_router.BRANDING_PROFILE_CURRENT_COLLECTION,
        auth_router.BRANDING_ASSET_COLLECTION,
    }


def test_branding_helper_uses_exact_collections_one_session_and_read_only_abort(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One successful composition uses one fresh active session and persists zero."""
    client, database = _install_kernel(monkeypatch)
    payload = _branding_payload()
    calls: list[dict[str, Any]] = []

    def build(**kwargs: Any) -> _BrandingProjection:
        calls.append(kwargs)
        session = kwargs["session"]
        assert isinstance(session, _Session)
        assert session.in_transaction is True
        return _BrandingProjection(payload)

    monkeypatch.setattr(
        auth_router,
        "build_tenant_branding_workspace_projection",
        build,
    )

    result = auth_router._workspace_branding_projection(TENANT)

    assert result == payload
    assert len(client.sessions) == 1
    session = client.sessions[0]
    assert session.started == 1
    assert session.aborted == 1
    assert session.ended == 1
    assert session.in_transaction is False
    assert set(database.requested) == _expected_collection_names()
    assert len(database.requested) == 6
    assert calls[0]["tenant_id"] == TENANT
    assert calls[0]["session"] is session


def test_branding_helper_retries_only_governed_signal_with_fresh_sessions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two governed retries restart the complete read and third attempt succeeds."""
    client, _ = _install_kernel(monkeypatch)
    attempts = 0

    def build(**kwargs: Any) -> _BrandingProjection:
        nonlocal attempts
        attempts += 1
        assert kwargs["session"] is client.sessions[-1]
        if attempts < 3:
            raise TenantBrandingWorkspaceProjectionRetryRequiredError()
        return _BrandingProjection(_branding_payload())

    monkeypatch.setattr(
        auth_router,
        "build_tenant_branding_workspace_projection",
        build,
    )

    assert auth_router._workspace_branding_projection(TENANT) == _branding_payload()
    assert attempts == 3
    assert len(client.sessions) == 3
    assert len({id(session) for session in client.sessions}) == 3
    assert all(session.started == 1 for session in client.sessions)
    assert all(session.aborted == 1 for session in client.sessions)
    assert all(session.ended == 1 for session in client.sessions)


def test_branding_helper_retry_exhaustion_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Three governed retry signals never become null/no-branding authority."""
    client, _ = _install_kernel(monkeypatch)

    def retry(**_kwargs: Any) -> Any:
        raise TenantBrandingWorkspaceProjectionRetryRequiredError()

    monkeypatch.setattr(
        auth_router,
        "build_tenant_branding_workspace_projection",
        retry,
    )

    with pytest.raises(TenantBrandingWorkspaceProjectionError) as raised:
        auth_router._workspace_branding_projection(TENANT)

    assert raised.value.code == "D21B7_BRANDING_RETRY_EXHAUSTED"
    assert len(client.sessions) == 3
    assert all(session.aborted == 1 for session in client.sessions)
    assert all(session.ended == 1 for session in client.sessions)


def _http_client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    branding: dict[str, object] | None = None,
    branding_error: Exception | None = None,
) -> TestClient:
    """Return a bounded FastAPI client with non-branding authorities frozen."""
    projection = SimpleNamespace(
        principal_id=PRINCIPAL,
        email="principal@example.com",
        tenant_id=TENANT,
        business_role="tenant_legal_partner",
        membership_revision=7,
        business_role_revision=11,
        tenant=SimpleNamespace(
            tenant_id=TENANT,
            alias="acme-legal",
            region="ZA",
            sector="Law",
            status=SimpleNamespace(value="ACTIVE"),
            organization=SimpleNamespace(
                organization_name="Acme Legal",
                legal_name="Acme Legal Inc.",
                industry="Legal Services",
            ),
        ),
    )
    monkeypatch.setattr(
        auth_router,
        "build_workspace_bootstrap_projection",
        lambda **_kwargs: projection,
    )
    monkeypatch.setattr(
        auth_router,
        "_workspace_legal_presentation_permissions",
        lambda **_kwargs: (),
    )
    monkeypatch.setattr(
        auth_router,
        "_workspace_principal_profile",
        lambda _projection: ("Canonical", "Principal"),
    )

    if branding_error is not None:
        def branding_reader(_tenant_id: str) -> Any:
            raise branding_error
    else:
        def branding_reader(_tenant_id: str) -> dict[str, object] | None:
            assert _tenant_id == TENANT
            return branding

    monkeypatch.setattr(
        auth_router,
        "_workspace_branding_projection",
        branding_reader,
    )

    app = FastAPI()
    app.include_router(auth_router.router)
    identity = SimpleNamespace(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        email="principal@example.com",
        roles=(),
        permissions=(),
    )
    app.dependency_overrides[auth_router.get_current_identity] = lambda: identity
    app.dependency_overrides[
        auth_router.get_principal_authority_repository
    ] = lambda: object()
    app.dependency_overrides[
        auth_router.get_tenant_membership_repository
    ] = lambda: object()
    app.dependency_overrides[
        auth_router.get_tenant_authority_role_repository
    ] = lambda: object()
    return TestClient(app)


def test_workspace_bootstrap_transports_exact_server_branding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Configured D21B6 output is transported exactly without added authority."""
    payload = _branding_payload()
    response = _http_client(monkeypatch, branding=payload).get(
        "/auth/workspace-bootstrap"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "READY"
    assert body["workspace"]["tenantId"] == TENANT
    assert body["workspace"]["branding"] == payload
    serialized = response.text
    assert "asset_bytes" not in serialized
    assert "content_bytes" not in serialized
    assert "data:" not in serialized
    assert "http://" not in serialized
    assert "https://" not in serialized


def test_workspace_bootstrap_projects_lawful_no_branding_as_explicit_null(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No D21B4B current pointer is explicit null, not legacy/browser fallback."""
    response = _http_client(monkeypatch, branding=None).get(
        "/auth/workspace-bootstrap"
    )
    assert response.status_code == 200
    body = response.json()
    assert "branding" in body["workspace"]
    assert body["workspace"]["branding"] is None


def test_workspace_branding_authority_failure_is_bounded_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Configured-branding corruption/outage cannot be disguised as null."""
    error = TenantBrandingWorkspaceProjectionError(
        "D21B6_ASSET_AUTHORITY_UNAVAILABLE"
    )
    response = _http_client(
        monkeypatch,
        branding_error=error,
    ).get("/auth/workspace-bootstrap")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Workspace branding authority is unavailable."
    }
    assert "D21B6_ASSET_AUTHORITY_UNAVAILABLE" not in response.text


# ARTIFACT: test_workspace_branding_http_projection.py
# VERSION: v1.0.0-D21B7-TENANT-BRANDING-WORKSPACE-HTTP-PROJECTION-CERT
# AUTHORITY BOUNDARY: D21B7 HTTP/session orchestration evidence only; no branding, IAM, legal or financial authority
# TENANT POSTURE: exact server-revalidated tenant forwarded to D21B6; no browser tenant-brand authority
# FAIL-CLOSED POSTURE: configured-branding errors and retry exhaustion are never converted to lawful absence
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
