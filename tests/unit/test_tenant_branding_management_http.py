"""Direct certificate for the L10-P2C7 tenant-branding management HTTP boundary.

TITLE: Tenant Branding Management HTTP Direct Certificate
VERSION: v1.1.0-L10-P2C7-D21B-BRANDING-MANAGEMENT-HTTP-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves authenticated tenant-derived routing, strict browser-safe
         projections, deterministic evidence helpers and bounded HTTP errors.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_management_http.py
COLLABORATION / OWNERSHIP: Direct Python EOS certificate; real-Mongo follow-up
                            remains separate because this gate introduces a new
                            multi-registry HTTP transaction composition.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: v1.1.0-L10-P2C7-D21B-BRANDING-MANAGEMENT-HTTP-CERT adds governed
           upload validation, D21B5B transaction composition and profile asset
           descriptor correlation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No credentials, raw bytes, public URLs or caller
                             tenant claims become authority.
TENANT BOUNDARY: Exact authenticated identity tenant only.
AUTHORITY BOUNDARY: HTTP composition; D21B registries remain canonical.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from typing import cast

import pytest
from fastapi import HTTPException, UploadFile
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from starlette.requests import Request

from tools.eos.api import tenant_branding_router as router
from tools.eos.saas.billing.tenant_branding_vas_policy import TenantBrandingTier


class CodedError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _request(payload: object) -> Request:
    body = json.dumps(payload).encode()
    consumed = False

    async def receive() -> dict[str, object]:
        nonlocal consumed
        if consumed:
            return {"type": "http.request", "body": b"", "more_body": False}
        consumed = True
        return {"type": "http.request", "body": body, "more_body": False}

    return Request({"type": "http", "method": "POST", "path": "/api/tenant-branding/profiles", "headers": []}, receive)


@pytest.mark.parametrize("value", range(10))
def test_digest_is_deterministic(value: int) -> None:
    payload = {"tenant": "tenant-a", "profile": value, "fields": ["label", "colour"]}
    assert router._digest(payload) == router._digest({"fields": payload["fields"], "profile": value, "tenant": "tenant-a"})
    assert len(router._digest(payload)) == 128


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("D21B2B_NOT_FOUND", 404),
        ("D21B4B_CURRENT_POINTER_MISSING", 404),
        ("D21B5B_ASSET_NOT_FOUND", 404),
        ("D21B4B_PROFILE_CONFLICT", 409),
        ("D21B4B_RETRY_REQUIRED", 409),
        ("D21B4B_CURRENT_POINTER_CONFLICT", 409),
        ("D21B2B_INPUT_INVALID", 422),
        ("D21B3_PROFILE_REQUIRED", 422),
        ("D21B4A_ACTIVE_ENTITLEMENT_REQUIRED", 422),
        ("D21B5A_MEDIA_INVALID", 422),
        ("BRANDING_PERSISTENCE_UNAVAILABLE", 503),
        ("D21B2B_PERSISTENCE_UNAVAILABLE", 503),
        ("UNKNOWN_FAILURE", 503),
        ("D21B2B_SINGLE_CURRENT_ENTITLEMENT_REQUIRED", 409),
        ("D21B4B_CURRENT_HISTORY_MISSING", 404),
    ],
)
def test_error_mapping_is_bounded(code: str, expected: int) -> None:
    assert router._map_error(CodedError(code)).status_code == expected


@pytest.mark.parametrize("payload", [{"profile_label": "A"}, {"profile_label": "B", "timestamp": "transport"}, {"primary_color": "#fff"}, {}, {"email_display_name": "Legal"}])
def test_allowlist_accepts_only_declared_presentation_fields(payload: dict[str, str]) -> None:
    result = asyncio.run(router._json_allowlist(_request(payload), {"profile_label", "primary_color", "email_display_name"}))
    assert result == {key: value for key, value in payload.items() if key != "timestamp"}


@pytest.mark.parametrize("field", ["tenant_id", "entitlement_id", "source_evidence_fingerprint", "approval_evidence_fingerprint", "raw_bytes"])
def test_allowlist_rejects_authority_or_raw_fields(field: str) -> None:
    with pytest.raises(Exception):
        asyncio.run(router._json_allowlist(_request({field: "forbidden"}), {"profile_label"}))


@pytest.mark.parametrize("value", range(5))
def test_browser_projection_excludes_durable_authority_fields(value: int) -> None:
    entitlement = SimpleNamespace(entitlement_id=f"ent-{value}", branding_tier="PRO", lifecycle_state="ACTIVE", lifecycle_revision=value, fingerprint="a" * 128)
    profile = SimpleNamespace(profile_id=f"profile-{value}", profile_label="Legal", fingerprint="b" * 128, branding_entitlement=entitlement, primary_color="#111", secondary_color=None, accent_color="#222", email_display_name=None, logo_asset_reference=None, logo_asset_fingerprint=None, favicon_asset_reference=None, favicon_asset_fingerprint=None)
    current = SimpleNamespace(profile=profile, pointer=SimpleNamespace(selection_id="sel", selection_revision=1))
    projection = router._profile_projection(current, entitlement)
    assert projection["entitlement"]["entitlementId"] == entitlement.entitlement_id
    assert "sourceEvidenceFingerprint" not in json.dumps(projection)
    assert "tenant_id" not in json.dumps(projection)
    assert "raw_bytes" not in json.dumps(projection)


def test_routes_are_authenticated_and_bounded() -> None:
    paths = {getattr(route, "path", None) for route in router.router.routes}
    assert paths == {"/tenant-branding", "/tenant-branding/profiles", "/tenant-branding/profiles/{profile_id}/select", "/tenant-branding/assets/{kind}"}
    assert router._READ_PERMISSION == "tenant_branding:read"
    assert router._PROFILE_PERMISSION == "tenant_branding:profile:manage"


def _authorized_identity() -> SovereignIdentity:
    return SovereignIdentity(
        identity_id="principal-http",
        tenant_id="tenant-http",
        username="operator",
        email="operator@example.test",
        auth_method="test",
        status=PrincipalStatus.ACTIVE,
    )


def test_mutation_authorization_returns_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    identity = _authorized_identity()
    monkeypatch.setattr(
        router,
        "authorize_tenant_operation",
        lambda **_: TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
        ),
    )
    result = asyncio.run(
        router.BrandingAuthorization("tenant_branding:profile:manage", "manage")(
            identity=identity,
            principal_repository=object(),
            membership_repository=object(),
            business_role_repository=object(),
            role_assignment_repository=object(),
        )
    )
    assert result is identity


def test_capability_authorization_returns_boolean_true(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        router,
        "authorize_tenant_operation",
        lambda **_: TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
        ),
    )
    result = asyncio.run(
        router.BrandingAuthorization("tenant_branding:profile:manage", "manage", allow_denied=True)(
            identity=_authorized_identity(),
            principal_repository=object(),
            membership_repository=object(),
            business_role_repository=object(),
            role_assignment_repository=object(),
        )
    )
    assert result is True


def test_capability_authorization_returns_boolean_false_when_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        router,
        "authorize_tenant_operation",
        lambda **_: TenantAuthorizationDecision(
            False,
            TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE,
        ),
    )
    result = asyncio.run(
        router.BrandingAuthorization("tenant_branding:profile:manage", "manage", allow_denied=True)(
            identity=_authorized_identity(),
            principal_repository=object(),
            membership_repository=object(),
            business_role_repository=object(),
            role_assignment_repository=object(),
        )
    )
    assert result is False


def test_capability_authority_unavailable_remains_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        router,
        "authorize_tenant_operation",
        lambda **_: TenantAuthorizationDecision(
            False,
            TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE,
        ),
    )
    with pytest.raises(Exception) as exc_info:
        asyncio.run(
            router.BrandingAuthorization("tenant_branding:profile:manage", "manage", allow_denied=True)(
                identity=_authorized_identity(),
                principal_repository=object(),
                membership_repository=object(),
                business_role_repository=object(),
                role_assignment_repository=object(),
            )
        )
    assert getattr(exc_info.value, "status_code", None) == 503


def test_projection_capability_values_are_booleans_and_never_identity() -> None:
    entitlement = SimpleNamespace(
        entitlement_id="ent-http",
        branding_tier="PRO",
        lifecycle_state="ACTIVE",
        lifecycle_revision=1,
        fingerprint="a" * 128,
    )
    projection = router._profile_projection(
        None,
        entitlement,
        can_manage_profile=True,
        can_manage_assets=False,
    )
    capabilities = projection["capabilities"]
    assert capabilities == {
        "canRead": True,
        "canManageProfile": True,
        "canManageAsset": False,
        "canManageAssets": False,
        "trustMarkRequired": True,
    }
    assert all(isinstance(value, bool) for value in capabilities.values())
    serialized = json.dumps(capabilities)
    for forbidden in ("identity_id", "email", "tenant_id", "roles", "permissions"):
        assert forbidden not in serialized


class _Upload:
    def __init__(self, content: bytes, content_type: str | None) -> None:
        self.content_type = content_type
        self._content = content

    async def read(self, _limit: int) -> bytes:
        return self._content


def test_asset_capability_is_closed_and_tier_specific() -> None:
    assert router._asset_capability(router.TenantBrandingAssetKind.LOGO) == "tenant.brand.logo.v1"
    assert router._asset_capability(router.TenantBrandingAssetKind.FAVICON) == "tenant.brand.favicon.v1"


def test_profile_asset_descriptor_resolves_server_side_with_exact_context(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}
    resolved = SimpleNamespace(asset=SimpleNamespace(asset_reference="asset:tenant-http:logo:1", content_fingerprint="b" * 128))
    monkeypatch.setattr(router, "_collection", lambda *_args: "asset-collection")

    def resolve(tenant_id: str, reference: str, *, expected_content_fingerprint: str, expected_kind: object, collection: object, session: object) -> object:
        captured.update(
            tenant_id=tenant_id,
            reference=reference,
            fingerprint=expected_content_fingerprint,
            kind=expected_kind,
            collection=collection,
            session=session,
        )
        return resolved

    monkeypatch.setattr(router.asset_registry, "resolve", resolve)
    result = router._resolve_profile_asset(
        payload={"logo_asset_reference": "asset:tenant-http:logo:1", "logo_asset_fingerprint": "b" * 128},
        reference_key="logo_asset_reference",
        fingerprint_key="logo_asset_fingerprint",
        kind=router.TenantBrandingAssetKind.LOGO,
        tenant_id="tenant-http",
        database=object(),
        session="active-session",
    )
    assert result is resolved
    assert captured == {
        "tenant_id": "tenant-http",
        "reference": "asset:tenant-http:logo:1",
        "fingerprint": "b" * 128,
        "kind": router.TenantBrandingAssetKind.LOGO,
        "collection": "asset-collection",
        "session": "active-session",
    }


def test_profile_asset_descriptor_requires_reference_and_fingerprint_pair() -> None:
    with pytest.raises(HTTPException) as raised:
        router._resolve_profile_asset(
            payload={"logo_asset_reference": "asset:tenant-http:logo:1"},
            reference_key="logo_asset_reference",
            fingerprint_key="logo_asset_fingerprint",
            kind=router.TenantBrandingAssetKind.LOGO,
            tenant_id="tenant-http",
            database=object(),
            session="active-session",
        )
    assert raised.value.status_code == 422


def test_upload_generates_server_descriptor_and_uses_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}
    entitlement = SimpleNamespace(branding_tier=TenantBrandingTier.PROFESSIONAL)
    asset = SimpleNamespace(
        asset_reference="asset:tenant-http:logo:server",
        content_fingerprint="a" * 128,
        media_type="image/png",
        asset_kind=router.TenantBrandingAssetKind.LOGO,
        content_length=8,
    )
    resolved = SimpleNamespace(asset=asset)
    monkeypatch.setattr(router, "_current_entitlement", lambda *_args, **_kwargs: entitlement)
    monkeypatch.setattr(router, "_collection", lambda *_args, **_kwargs: object())

    def persist(asset_value: object, content: bytes, _collection: object, *, session: object) -> object:
        captured.update(asset=asset_value, content=content, session=session)
        return resolved

    monkeypatch.setattr(router.asset_registry, "create_or_replay", persist)
    monkeypatch.setattr(router, "register_tenant_branding_asset", lambda **kwargs: kwargs)
    monkeypatch.setattr(router, "_transaction", lambda callback: callback("active-session", object()))
    response = asyncio.run(
        router.upload_tenant_branding_asset(
            "logo",
            cast(UploadFile, _Upload(b"png-data", "image/png")),
            _authorized_identity(),
        )
    )
    assert response.status_code == 201
    body = json.loads(bytes(response.body))
    assert body["data"] == {
        "reference": "asset:tenant-http:logo:server",
        "contentFingerprint": "a" * 128,
        "mediaType": "image/png",
        "kind": "LOGO",
        "contentLength": 8,
    }
    assert captured["session"] == "active-session"
    assert captured["content"] == b"png-data"


@pytest.mark.parametrize("kind", ["svg", "unknown"])
def test_upload_rejects_closed_kind_or_unsafe_media(kind: str) -> None:
    media = "image/svg+xml" if kind == "svg" else "image/png"
    with pytest.raises(Exception) as raised:
        asyncio.run(
            router.upload_tenant_branding_asset(
                kind,
                cast(UploadFile, _Upload(b"bytes", media)),
                _authorized_identity(),
            )
        )
    assert getattr(raised.value, "status_code", None) == 422


@pytest.mark.parametrize("content", [b"", b"x" * (router.MAX_ASSET_BYTES + 1)])
def test_upload_rejects_empty_or_oversize_content(content: bytes) -> None:
    with pytest.raises(Exception) as raised:
        asyncio.run(
            router.upload_tenant_branding_asset(
                "logo",
                cast(UploadFile, _Upload(content, "image/png")),
                _authorized_identity(),
            )
        )
    assert getattr(raised.value, "status_code", None) == 422


def test_upload_rejects_non_entitled_favicon_before_registry_write(monkeypatch: pytest.MonkeyPatch) -> None:
    entitlement = SimpleNamespace(branding_tier=TenantBrandingTier.PROFESSIONAL)
    monkeypatch.setattr(router, "_current_entitlement", lambda *_args, **_kwargs: entitlement)
    monkeypatch.setattr(router, "_transaction", lambda callback: callback("active-session", object()))
    called = False

    def forbidden(*_args: object, **_kwargs: object) -> object:
        nonlocal called
        called = True
        return None

    monkeypatch.setattr(router.asset_registry, "create_or_replay", forbidden)
    with pytest.raises(Exception) as raised:
        asyncio.run(
            router.upload_tenant_branding_asset(
                "favicon",
                cast(UploadFile, _Upload(b"png-data", "image/png")),
                _authorized_identity(),
            )
        )
    assert getattr(raised.value, "status_code", None) == 422
    assert called is False


# ARTIFACT: test_tenant_branding_management_http.py
# VERSION: v1.1.0-L10-P2C7-D21B-BRANDING-MANAGEMENT-HTTP-CERT
# AUTHORITY BOUNDARY: focused HTTP composition certificate only
# TENANT POSTURE: authenticated server-derived tenant scope
# FAIL-CLOSED POSTURE: browser authority fields are rejected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
