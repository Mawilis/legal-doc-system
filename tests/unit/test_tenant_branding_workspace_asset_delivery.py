"""Direct certificate for D21B10 current branding asset delivery.

TITLE: Tenant Branding Workspace Asset Delivery Direct Certificate
VERSION: v1.0.0-D21B10-TENANT-BRANDING-ASSET-DELIVERY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove that current branding bytes are releasable only after D21B6
         currentness proof and exact D21B5B re-resolution, with no caller asset
         identity authority and preserved whole-transaction retry semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_workspace_asset_delivery.py
CERTIFICATION / UPDATE DATE: 2026-09-25
AUTHORITY BOUNDARY: D21B10 read-only delivery composition only.
TENANT BOUNDARY: Synthetic evidence is exact tenant-bound; foreign/mismatched
                 asset evidence is rejected.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

import inspect
from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.auth import tenant_branding_workspace_asset_delivery as delivery
from tools.eos.auth.tenant_branding_workspace_projection import (
    TenantBrandingWorkspaceAsset,
    TenantBrandingWorkspaceProjection,
    TenantBrandingWorkspaceProjectionError,
    TenantBrandingWorkspaceProjectionRetryRequiredError,
)
from tools.eos.saas.billing.tenant_branding_asset_registry import (
    TenantBrandingAssetRegistryConflictError,
    TenantBrandingAssetRegistryRetryRequiredError,
    TenantBrandingResolvedAsset,
)
from tools.eos.saas.domain.tenant_branding_asset import (
    TenantBrandingAssetKind,
    register_tenant_branding_asset,
)


TENANT = "tenant-a"
NOW = datetime(2026, 9, 25, 22, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
LOGO_BYTES = b"\x89PNG\r\n\x1a\nD21B10-logo"
FAVICON_BYTES = b"\x89PNG\r\n\x1a\nD21B10-favicon"


def _resolved(
    kind: TenantBrandingAssetKind,
    content: bytes,
) -> TenantBrandingResolvedAsset:
    reference = f"asset:{TENANT}:{kind.value.lower()}:primary"
    asset = register_tenant_branding_asset(
        tenant_id=TENANT,
        asset_reference=reference,
        asset_kind=kind,
        media_type="image/png",
        content=content,
        source_evidence_reference=f"upload:{kind.value}",
        source_evidence_fingerprint=FP_A,
        registered_at=NOW,
    )
    return TenantBrandingResolvedAsset(asset=asset, content=content)


def _projection(
    *,
    logo: TenantBrandingResolvedAsset | None = None,
    favicon: TenantBrandingResolvedAsset | None = None,
) -> TenantBrandingWorkspaceProjection:
    logo_descriptor = (
        None
        if logo is None
        else TenantBrandingWorkspaceAsset(
            reference=logo.asset.asset_reference,
            content_fingerprint=logo.asset.content_fingerprint,
            media_type=logo.asset.media_type,
            kind=TenantBrandingAssetKind.LOGO.value,
        )
    )
    favicon_descriptor = (
        None
        if favicon is None
        else TenantBrandingWorkspaceAsset(
            reference=favicon.asset.asset_reference,
            content_fingerprint=favicon.asset.content_fingerprint,
            media_type=favicon.asset.media_type,
            kind=TenantBrandingAssetKind.FAVICON.value,
        )
    )
    return TenantBrandingWorkspaceProjection(
        tenant_id=TENANT,
        profile_id="profile-1",
        profile_fingerprint=FP_A,
        selection_id="selection-1",
        selection_revision=1,
        entitlement_id="entitlement-1",
        entitlement_revision=1,
        entitlement_fingerprint=FP_B,
        branding_tier="TENANT_BRANDING_INSTITUTIONAL",
        profile_label="Institutional brand",
        primary_color="#112233",
        secondary_color="#445566",
        accent_color="#AABBCC",
        email_display_name="Acme Legal",
        platform_trust_mark_required=True,
        logo=logo_descriptor,
        favicon=favicon_descriptor,
    )


def _invoke(
    *,
    asset_kind: TenantBrandingAssetKind | str = TenantBrandingAssetKind.LOGO,
    tenant_id: str = TENANT,
    session: object,
) -> delivery.TenantBrandingWorkspaceAssetDelivery:
    return delivery.resolve_current_tenant_branding_asset(
        tenant_id=tenant_id,
        asset_kind=asset_kind,
        entitlement_history_collection=object(),
        entitlement_current_collection=object(),
        profile_collection=object(),
        selection_collection=object(),
        profile_current_collection=object(),
        asset_collection=object(),
        session=session,
    )


@pytest.mark.parametrize(
    ("kind", "content"),
    (
        (TenantBrandingAssetKind.LOGO, LOGO_BYTES),
        (TenantBrandingAssetKind.FAVICON, FAVICON_BYTES),
    ),
)
def test_exact_current_asset_kind_releases_only_reresolved_bytes(
    monkeypatch: pytest.MonkeyPatch,
    kind: TenantBrandingAssetKind,
    content: bytes,
) -> None:
    """Logo/favicon bytes are returned only from exact D21B6 -> D21B5B chain."""
    logo = _resolved(TenantBrandingAssetKind.LOGO, LOGO_BYTES)
    favicon = _resolved(TenantBrandingAssetKind.FAVICON, FAVICON_BYTES)
    current = _projection(logo=logo, favicon=favicon)
    chosen = logo if kind is TenantBrandingAssetKind.LOGO else favicon
    session = object()
    calls: list[tuple[str, object]] = []

    def project(**kwargs: Any) -> TenantBrandingWorkspaceProjection:
        calls.append(("projection", kwargs["session"]))
        assert kwargs["tenant_id"] == TENANT
        return current

    def resolve(
        tenant_id: str,
        asset_reference: str,
        *,
        expected_content_fingerprint: str,
        expected_kind: TenantBrandingAssetKind | str,
        collection: Any,
        session: object,
    ) -> TenantBrandingResolvedAsset:
        del collection
        calls.append(("asset", session))
        assert tenant_id == TENANT
        assert asset_reference == chosen.asset.asset_reference
        assert expected_content_fingerprint == chosen.asset.content_fingerprint
        assert TenantBrandingAssetKind(expected_kind) is kind
        return chosen

    monkeypatch.setattr(delivery, "build_tenant_branding_workspace_projection", project)
    monkeypatch.setattr(delivery, "resolve_branding_asset", resolve)

    result = _invoke(asset_kind=kind, session=session)
    assert result.tenant_id == TENANT
    assert result.asset_reference == chosen.asset.asset_reference
    assert result.content_fingerprint == chosen.asset.content_fingerprint
    assert result.media_type == "image/png"
    assert result.kind is kind
    assert result.content == content
    assert calls == [("projection", session), ("asset", session)]


def test_no_current_branding_is_not_configured_and_releases_no_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Lawful D21B6 no-branding absence never falls back to legacy assets."""
    asset_called = False

    def project(**_: Any) -> None:
        return None

    def resolve(*_: Any, **__: Any) -> Any:
        nonlocal asset_called
        asset_called = True
        raise AssertionError("asset authority must not be reached")

    monkeypatch.setattr(delivery, "build_tenant_branding_workspace_projection", project)
    monkeypatch.setattr(delivery, "resolve_branding_asset", resolve)

    with pytest.raises(delivery.TenantBrandingWorkspaceAssetNotConfiguredError) as raised:
        _invoke(session=object())
    assert raised.value.code == "D21B10_BRANDING_NOT_CONFIGURED"
    assert asset_called is False


def test_requested_kind_missing_from_current_profile_is_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A profile without a favicon cannot release some other asset as fallback."""
    logo = _resolved(TenantBrandingAssetKind.LOGO, LOGO_BYTES)
    monkeypatch.setattr(
        delivery,
        "build_tenant_branding_workspace_projection",
        lambda **_: _projection(logo=logo, favicon=None),
    )
    monkeypatch.setattr(
        delivery,
        "resolve_branding_asset",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("asset resolver must not run")
        ),
    )

    with pytest.raises(delivery.TenantBrandingWorkspaceAssetNotConfiguredError) as raised:
        _invoke(asset_kind=TenantBrandingAssetKind.FAVICON, session=object())
    assert raised.value.code == "D21B10_ASSET_NOT_CONFIGURED"


def test_current_branding_authority_failure_releases_no_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """D21B6 corruption/outage remains a delivery failure, not absence."""

    error = TenantBrandingWorkspaceProjectionError("D21B6_ENTITLEMENT_INACTIVE")
    monkeypatch.setattr(
        delivery,
        "build_tenant_branding_workspace_projection",
        lambda **_: (_ for _ in ()).throw(error),
    )

    with pytest.raises(delivery.TenantBrandingWorkspaceAssetDeliveryError) as raised:
        _invoke(session=object())
    assert raised.value.code == "D21B10_CURRENT_BRANDING_AUTHORITY_UNAVAILABLE"
    assert raised.value.__cause__ is error


@pytest.mark.parametrize("source", ("projection", "asset"))
def test_whole_transaction_retry_taxonomy_is_preserved(
    monkeypatch: pytest.MonkeyPatch,
    source: str,
) -> None:
    """Transient D21B6/D21B5B races remain visible to the transaction owner."""
    logo = _resolved(TenantBrandingAssetKind.LOGO, LOGO_BYTES)
    if source == "projection":
        error: Exception = TenantBrandingWorkspaceProjectionRetryRequiredError()
        monkeypatch.setattr(
            delivery,
            "build_tenant_branding_workspace_projection",
            lambda **_: (_ for _ in ()).throw(error),
        )
    else:
        error = TenantBrandingAssetRegistryRetryRequiredError()
        monkeypatch.setattr(
            delivery,
            "build_tenant_branding_workspace_projection",
            lambda **_: _projection(logo=logo),
        )
        monkeypatch.setattr(
            delivery,
            "resolve_branding_asset",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
        )

    with pytest.raises(delivery.TenantBrandingWorkspaceAssetRetryRequiredError) as raised:
        _invoke(session=object())
    assert raised.value.code == "D21B10_WHOLE_TRANSACTION_RETRY_REQUIRED"
    assert raised.value.__cause__ is error


def test_asset_authority_failure_releases_no_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """D21B5B resolution conflicts cannot be converted into image responses."""
    logo = _resolved(TenantBrandingAssetKind.LOGO, LOGO_BYTES)
    error = TenantBrandingAssetRegistryConflictError()
    monkeypatch.setattr(
        delivery,
        "build_tenant_branding_workspace_projection",
        lambda **_: _projection(logo=logo),
    )
    monkeypatch.setattr(
        delivery,
        "resolve_branding_asset",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
    )

    with pytest.raises(delivery.TenantBrandingWorkspaceAssetDeliveryError) as raised:
        _invoke(session=object())
    assert raised.value.code == "D21B10_ASSET_AUTHORITY_UNAVAILABLE"
    assert raised.value.__cause__ is error


def test_reresolved_asset_must_still_match_d21b6_descriptor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Even a D21B5B return value cannot drift from the current D21B6 descriptor."""
    logo = _resolved(TenantBrandingAssetKind.LOGO, LOGO_BYTES)
    divergent = register_tenant_branding_asset(
        tenant_id=TENANT,
        asset_reference=logo.asset.asset_reference,
        asset_kind=TenantBrandingAssetKind.LOGO,
        media_type="image/webp",
        content=LOGO_BYTES,
        source_evidence_reference="different-upload",
        source_evidence_fingerprint=FP_A,
        registered_at=NOW,
    )
    monkeypatch.setattr(
        delivery,
        "build_tenant_branding_workspace_projection",
        lambda **_: _projection(logo=logo),
    )
    monkeypatch.setattr(
        delivery,
        "resolve_branding_asset",
        lambda *_args, **_kwargs: TenantBrandingResolvedAsset(
            asset=divergent,
            content=LOGO_BYTES,
        ),
    )

    with pytest.raises(delivery.TenantBrandingWorkspaceAssetDeliveryError) as raised:
        _invoke(session=object())
    assert raised.value.code == "D21B10_ASSET_CORRELATION_INVALID"


@pytest.mark.parametrize(
    ("tenant_id", "kind", "code"),
    (
        (" tenant-a", TenantBrandingAssetKind.LOGO, "D21B10_TENANT_ID_INVALID"),
        (TENANT, "SCRIPT", "D21B10_ASSET_KIND_INVALID"),
    ),
)
def test_invalid_scope_or_kind_rejects_before_current_authority_read(
    monkeypatch: pytest.MonkeyPatch,
    tenant_id: str,
    kind: str | TenantBrandingAssetKind,
    code: str,
) -> None:
    """Malformed scope/kind cannot reach current branding authorities."""
    called = False

    def project(**_: Any) -> Any:
        nonlocal called
        called = True
        return None

    monkeypatch.setattr(delivery, "build_tenant_branding_workspace_projection", project)
    with pytest.raises(delivery.TenantBrandingWorkspaceAssetDeliveryError) as raised:
        _invoke(tenant_id=tenant_id, asset_kind=kind, session=object())
    assert raised.value.code == code
    assert called is False


def test_public_delivery_api_accepts_kind_not_browser_asset_identity() -> None:
    """Callers cannot assert a reference, fingerprint, URL or path."""
    signature = inspect.signature(delivery.resolve_current_tenant_branding_asset)
    parameters = set(signature.parameters)
    assert "asset_kind" in parameters
    assert "tenant_id" in parameters
    assert "asset_reference" not in parameters
    assert "content_fingerprint" not in parameters
    assert "url" not in parameters
    assert "path" not in parameters


# ARTIFACT: test_tenant_branding_workspace_asset_delivery.py
# VERSION: v1.0.0-D21B10-TENANT-BRANDING-ASSET-DELIVERY-CERT
# AUTHORITY BOUNDARY: deterministic D21B10 delivery-composition evidence only
# TENANT POSTURE: exact tenant current branding only; caller cannot assert asset identity
# FAIL-CLOSED POSTURE: absence/outage/retry/mismatch releases no bytes
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
