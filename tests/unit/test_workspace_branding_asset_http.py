"""Direct certificate for D21B11 authenticated branding asset HTTP delivery.

TITLE: Workspace Branding Asset HTTP Direct Certificate
VERSION: v1.0.0-D21B11-TENANT-BRANDING-ASSET-HTTP-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove bounded session/retry ownership plus authenticated byte transport
         for current tenant logo/favicon without caller tenant/reference authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_workspace_branding_asset_http.py
CERTIFICATION / UPDATE DATE: 2026-09-25
AUTHORITY BOUNDARY: D21B11 HTTP/session orchestration only; D21B10/D21B6/D21B5B
                    own current branding and byte truth.
TENANT BOUNDARY: Route derives tenant only from revalidated workspace authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from tools.eos.api import auth_router
from tools.eos.auth.tenant_branding_workspace_asset_delivery import (
    TenantBrandingWorkspaceAssetDelivery,
    TenantBrandingWorkspaceAssetDeliveryError,
    TenantBrandingWorkspaceAssetNotConfiguredError,
    TenantBrandingWorkspaceAssetRetryRequiredError,
)
from tools.eos.auth.workspace_bootstrap_projection import (
    WorkspaceBootstrapProjectionError,
)
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.domain.tenant_branding_asset import TenantBrandingAssetKind


TENANT = "tenant-d21b11"
PRINCIPAL = "principal-d21b11"
LOGO_BYTES = b"\x89PNG\r\n\x1a\nD21B11-logo"
FAVICON_BYTES = b"\x89PNG\r\n\x1a\nD21B11-favicon"


class _Session:
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
    def __init__(self) -> None:
        self.sessions: list[_Session] = []

    def start_session(self) -> _Session:
        session = _Session()
        self.sessions.append(session)
        return session


class _Database:
    def __init__(self) -> None:
        self.collections: dict[str, object] = {}
        self.requested: list[str] = []

    def __getitem__(self, name: str) -> object:
        self.requested.append(name)
        return self.collections.setdefault(name, object())


def _delivery(kind: TenantBrandingAssetKind) -> TenantBrandingWorkspaceAssetDelivery:
    content = LOGO_BYTES if kind is TenantBrandingAssetKind.LOGO else FAVICON_BYTES
    return TenantBrandingWorkspaceAssetDelivery(
        tenant_id=TENANT,
        asset_reference=f"asset:{TENANT}:{kind.value.lower()}:primary",
        content_fingerprint="a" * 128,
        media_type="image/png",
        kind=kind,
        content=content,
    )


def _install_kernel(monkeypatch: pytest.MonkeyPatch) -> tuple[_Client, _Database]:
    client = _Client()
    database = _Database()
    monkeypatch.setattr(kernel_db, "get_client", lambda: client)
    monkeypatch.setattr(kernel_db, "get_database", lambda: database)
    return client, database


def _expected_collection_names() -> set[str]:
    return {
        auth_router.BRANDING_ENTITLEMENT_HISTORY_COLLECTION,
        auth_router.BRANDING_ENTITLEMENT_CURRENT_COLLECTION,
        auth_router.BRANDING_PROFILE_COLLECTION,
        auth_router.BRANDING_SELECTION_COLLECTION,
        auth_router.BRANDING_PROFILE_CURRENT_COLLECTION,
        auth_router.BRANDING_ASSET_COLLECTION,
    }


def test_asset_helper_uses_exact_collections_one_session_and_read_only_abort(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, database = _install_kernel(monkeypatch)
    calls: list[dict[str, Any]] = []

    def resolve(**kwargs: Any) -> TenantBrandingWorkspaceAssetDelivery:
        calls.append(kwargs)
        session = kwargs["session"]
        assert isinstance(session, _Session)
        assert session.in_transaction is True
        return _delivery(TenantBrandingAssetKind.LOGO)

    monkeypatch.setattr(auth_router, "resolve_current_tenant_branding_asset", resolve)
    result = auth_router._workspace_branding_asset_delivery(
        TENANT,
        TenantBrandingAssetKind.LOGO,
    )

    assert result.content == LOGO_BYTES
    assert len(client.sessions) == 1
    session = client.sessions[0]
    assert session.started == 1
    assert session.aborted == 1
    assert session.ended == 1
    assert session.in_transaction is False
    assert set(database.requested) == _expected_collection_names()
    assert len(database.requested) == 6
    assert calls[0]["tenant_id"] == TENANT
    assert calls[0]["asset_kind"] is TenantBrandingAssetKind.LOGO
    assert calls[0]["session"] is session


def test_asset_helper_retries_only_governed_signal_with_fresh_sessions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _ = _install_kernel(monkeypatch)
    attempts = 0

    def resolve(**kwargs: Any) -> TenantBrandingWorkspaceAssetDelivery:
        nonlocal attempts
        attempts += 1
        assert kwargs["session"] is client.sessions[-1]
        if attempts < 3:
            raise TenantBrandingWorkspaceAssetRetryRequiredError()
        return _delivery(TenantBrandingAssetKind.LOGO)

    monkeypatch.setattr(auth_router, "resolve_current_tenant_branding_asset", resolve)
    result = auth_router._workspace_branding_asset_delivery(
        TENANT,
        TenantBrandingAssetKind.LOGO,
    )
    assert result.content == LOGO_BYTES
    assert attempts == 3
    assert len(client.sessions) == 3
    assert len({id(session) for session in client.sessions}) == 3
    assert all(session.started == 1 for session in client.sessions)
    assert all(session.aborted == 1 for session in client.sessions)
    assert all(session.ended == 1 for session in client.sessions)


def test_asset_helper_retry_exhaustion_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _ = _install_kernel(monkeypatch)
    monkeypatch.setattr(
        auth_router,
        "resolve_current_tenant_branding_asset",
        lambda **_kwargs: (_ for _ in ()).throw(
            TenantBrandingWorkspaceAssetRetryRequiredError()
        ),
    )

    with pytest.raises(TenantBrandingWorkspaceAssetDeliveryError) as raised:
        auth_router._workspace_branding_asset_delivery(
            TENANT,
            TenantBrandingAssetKind.LOGO,
        )
    assert raised.value.code == "D21B11_BRANDING_RETRY_EXHAUSTED"
    assert len(client.sessions) == 3
    assert all(session.aborted == 1 for session in client.sessions)
    assert all(session.ended == 1 for session in client.sessions)


def _http_client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    delivered: TenantBrandingWorkspaceAssetDelivery | None = None,
    delivery_error: Exception | None = None,
    workspace_error: Exception | None = None,
    seen: list[tuple[str, TenantBrandingAssetKind]] | None = None,
) -> TestClient:
    workspace = SimpleNamespace(
        principal_id=PRINCIPAL,
        tenant_id=TENANT,
        business_role="tenant_legal_partner",
        membership_revision=1,
        business_role_revision=1,
        tenant=SimpleNamespace(tenant_id=TENANT),
    )

    if workspace_error is not None:
        monkeypatch.setattr(
            auth_router,
            "build_workspace_bootstrap_projection",
            lambda **_kwargs: (_ for _ in ()).throw(workspace_error),
        )
    else:
        monkeypatch.setattr(
            auth_router,
            "build_workspace_bootstrap_projection",
            lambda **_kwargs: workspace,
        )

    def read(tenant_id: str, kind: TenantBrandingAssetKind) -> TenantBrandingWorkspaceAssetDelivery:
        if seen is not None:
            seen.append((tenant_id, kind))
        if delivery_error is not None:
            raise delivery_error
        assert delivered is not None
        return delivered

    monkeypatch.setattr(auth_router, "_workspace_branding_asset_delivery", read)

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
    return TestClient(app)


@pytest.mark.parametrize(
    ("path_kind", "kind", "content"),
    (
        ("logo", TenantBrandingAssetKind.LOGO, LOGO_BYTES),
        ("favicon", TenantBrandingAssetKind.FAVICON, FAVICON_BYTES),
    ),
)
def test_authenticated_asset_endpoint_returns_exact_bytes_and_security_headers(
    monkeypatch: pytest.MonkeyPatch,
    path_kind: str,
    kind: TenantBrandingAssetKind,
    content: bytes,
) -> None:
    seen: list[tuple[str, TenantBrandingAssetKind]] = []
    response = _http_client(
        monkeypatch,
        delivered=_delivery(kind),
        seen=seen,
    ).get(f"/auth/workspace-branding/{path_kind}")

    assert response.status_code == 200
    assert response.content == content
    assert response.headers["content-type"] == "image/png"
    assert response.headers["cache-control"] == "private, no-store"
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["cross-origin-resource-policy"] == "same-origin"
    assert seen == [(TENANT, kind)]


def test_browser_query_cannot_override_server_tenant_or_asset_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[tuple[str, TenantBrandingAssetKind]] = []
    response = _http_client(
        monkeypatch,
        delivered=_delivery(TenantBrandingAssetKind.LOGO),
        seen=seen,
    ).get(
        "/auth/workspace-branding/logo"
        "?tenant_id=foreign&asset_reference=asset:foreign:logo:x"
        "&content_fingerprint=" + ("f" * 128)
    )
    assert response.status_code == 200
    assert response.content == LOGO_BYTES
    assert seen == [(TENANT, TenantBrandingAssetKind.LOGO)]


def test_invalid_asset_kind_is_bounded_404_without_delivery_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[tuple[str, TenantBrandingAssetKind]] = []
    response = _http_client(
        monkeypatch,
        delivered=_delivery(TenantBrandingAssetKind.LOGO),
        seen=seen,
    ).get("/auth/workspace-branding/script")
    assert response.status_code == 404
    assert response.json() == {"detail": "Workspace branding asset is unavailable."}
    assert seen == []


def test_unconfigured_current_asset_is_bounded_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = TenantBrandingWorkspaceAssetNotConfiguredError()
    response = _http_client(
        monkeypatch,
        delivery_error=error,
    ).get("/auth/workspace-branding/logo")
    assert response.status_code == 404
    assert response.json() == {"detail": "Workspace branding asset is unavailable."}
    assert error.code not in response.text


def test_current_asset_authority_failure_is_redacted_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = TenantBrandingWorkspaceAssetDeliveryError(
        "D21B10_ASSET_AUTHORITY_UNAVAILABLE"
    )
    response = _http_client(
        monkeypatch,
        delivery_error=error,
    ).get("/auth/workspace-branding/logo")
    assert response.status_code == 503
    assert response.json() == {
        "detail": "Workspace branding asset authority is unavailable."
    }
    assert error.code not in response.text


def test_workspace_access_failure_precedes_asset_delivery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = WorkspaceBootstrapProjectionError(
        "WORKSPACE_BOOTSTRAP_MEMBERSHIP_REQUIRED"
    )
    seen: list[tuple[str, TenantBrandingAssetKind]] = []
    response = _http_client(
        monkeypatch,
        workspace_error=error,
        delivered=_delivery(TenantBrandingAssetKind.LOGO),
        seen=seen,
    ).get("/auth/workspace-branding/logo")
    assert response.status_code == 403
    assert response.json() == {"detail": "Workspace access denied."}
    assert seen == []


# ARTIFACT: test_workspace_branding_asset_http.py
# VERSION: v1.0.0-D21B11-TENANT-BRANDING-ASSET-HTTP-CERT
# AUTHORITY BOUNDARY: D21B11 HTTP/session transport evidence only
# TENANT POSTURE: server-revalidated workspace tenant only; query overrides ignored
# FAIL-CLOSED POSTURE: invalid/missing authority releases no bytes; outages are redacted
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
