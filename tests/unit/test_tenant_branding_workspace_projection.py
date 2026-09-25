"""Direct certificate for D21B6 tenant branding workspace composition.

TITLE: Tenant Branding Workspace Projection Direct Certificate
VERSION: v1.0.2-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove safe no-branding absence and exact ACTIVE-entitlement/profile/
         asset composition without raw bytes, URL invention or browser authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_workspace_projection.py
COLLABORATION / OWNERSHIP: Direct deterministic certificate for D21B6 only.
                            D21B2B, D21B4B and D21B5B remain separate sovereign
                            authorities with their own direct/real-Mongo evidence.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.2-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION-CERT aligns the synthetic D21B4B pointer with the repaired
           v1.0.3 registry contract by using the canonical serialized D21B1 tier
           value. This preserves the certificate's exact cross-domain
           correlation purpose and changes no production semantics.
           v1.0.1-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION-CERT attempted to align the fixture while D21B4B still emitted an
           Enum-qualified tier representation; D21B4B v1.0.3 subsequently
           restored canonical tier-value persistence.
           v1.0.0-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION-CERT established adversarial coverage for safe absent branding,
           exact current ACTIVE entitlement correlation, stale/suspended
           rejection, exact logo/favicon resolution, tenant correlation,
           same-session propagation, registry outage/retry taxonomy and
           browser-safe output.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic immutable evidence only; no credentials,
                             external calls or persisted customer data.
TENANT BOUNDARY: Every synthetic authority is exact tenant-bound and foreign
                 correlation is rejected.
AUTHORITY BOUNDARY: D21B6 read-only composition only; no IAM, legal command,
                    upload, entitlement transition or browser authorization.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from typing import Any

import pytest

from tools.eos.auth import tenant_branding_workspace_projection as projection
from tools.eos.saas.billing.tenant_branding_asset_registry import (
    TenantBrandingAssetRegistryConflictError,
    TenantBrandingAssetRegistryRetryRequiredError,
    TenantBrandingResolvedAsset,
)
from tools.eos.saas.billing.tenant_branding_entitlement_registry import (
    TenantBrandingEntitlementRegistryPersistenceUnavailableError,
    TenantBrandingEntitlementRegistryRetryRequiredError,
)
from tools.eos.saas.billing.tenant_branding_profile_registry import (
    TenantBrandingCurrentProfile,
    TenantBrandingCurrentProfilePointer,
    TenantBrandingProfileRegistryCurrentPointerMissingError,
    TenantBrandingProfileRegistryPersistenceUnavailableError,
    TenantBrandingProfileRegistryRetryRequiredError,
)
from tools.eos.saas.billing.tenant_branding_vas_policy import TenantBrandingTier
from tools.eos.saas.domain.tenant_branding_asset import (
    TenantBrandingAssetKind,
    register_tenant_branding_asset,
)
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlement,
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)
from tools.eos.saas.domain.tenant_branding_profile import (
    TenantBrandingProfile,
    approve_tenant_branding_profile,
)
from tools.eos.saas.domain.tenant_branding_profile_selection import (
    TenantBrandingProfileSelection,
    select_tenant_branding_profile,
)


NOW = datetime(2026, 9, 25, 20, 0, tzinfo=timezone.utc)
FP = "a" * 128
LOGO_BYTES = b"\x89PNG\r\n\x1a\nD21B6-logo"
FAVICON_BYTES = b"\x89PNG\r\n\x1a\nD21B6-favicon"


def _active_entitlement(
    tenant_id: str = "tenant-a",
    *,
    source_reference: str = "composition-1",
) -> TenantBrandingEntitlement:
    """Return one exact ACTIVE Institutional D21B2 entitlement."""
    pending = create_tenant_branding_entitlement(
        tenant_id=tenant_id,
        entitlement_id="branding-entitlement-1",
        branding_tier=TenantBrandingTier.INSTITUTIONAL,
        source_evidence_reference=source_reference,
        source_evidence_fingerprint=FP,
    )
    return pending.transition(
        TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
    )


def _resolved_asset(
    tenant_id: str,
    reference: str,
    kind: TenantBrandingAssetKind,
    content: bytes,
) -> TenantBrandingResolvedAsset:
    """Return one exact resolved D21B5B value."""
    asset = register_tenant_branding_asset(
        tenant_id=tenant_id,
        asset_reference=reference,
        asset_kind=kind,
        media_type="image/png",
        content=content,
        source_evidence_reference=f"upload:{kind.value}",
        source_evidence_fingerprint=FP,
        registered_at=NOW,
    )
    return TenantBrandingResolvedAsset(asset=asset, content=content)


def _bundle(
    tenant_id: str = "tenant-a",
) -> tuple[
    TenantBrandingEntitlement,
    TenantBrandingCurrentProfile,
    TenantBrandingResolvedAsset,
    TenantBrandingResolvedAsset,
]:
    """Return mutually correlated D21B2/D21B3/D21B4/D21B5 synthetic truth."""
    entitlement = _active_entitlement(tenant_id)
    logo_reference = f"asset:{tenant_id}:logo:primary"
    favicon_reference = f"asset:{tenant_id}:favicon:primary"
    logo = _resolved_asset(
        tenant_id,
        logo_reference,
        TenantBrandingAssetKind.LOGO,
        LOGO_BYTES,
    )
    favicon = _resolved_asset(
        tenant_id,
        favicon_reference,
        TenantBrandingAssetKind.FAVICON,
        FAVICON_BYTES,
    )
    profile: TenantBrandingProfile = approve_tenant_branding_profile(
        entitlement=entitlement,
        profile_id="profile-primary",
        profile_label="Primary institutional brand",
        source_evidence_reference="profile-submission-1",
        source_evidence_fingerprint=FP,
        approved_at=NOW,
        approval_evidence_reference="profile-approval-1",
        approval_evidence_fingerprint=FP,
        logo_asset_reference=logo_reference,
        logo_asset_fingerprint=logo.asset.content_fingerprint,
        primary_color="#112233",
        secondary_color="#445566",
        accent_color="#AABBCC",
        email_display_name="Acme Legal",
        favicon_asset_reference=favicon_reference,
        favicon_asset_fingerprint=favicon.asset.content_fingerprint,
    )
    selection: TenantBrandingProfileSelection = select_tenant_branding_profile(
        profile=profile,
        current_entitlement=entitlement,
        selection_id="selection-1",
        selection_revision=1,
        selected_at=NOW,
        selection_evidence_reference="selection-evidence-1",
        selection_evidence_fingerprint=FP,
    )
    pointer = TenantBrandingCurrentProfilePointer(
        tenant_id=tenant_id,
        selection_id=selection.selection_id,
        selection_revision=selection.selection_revision,
        selection_fingerprint=selection.fingerprint,
        profile_id=selection.profile_id,
        profile_fingerprint=selection.profile_fingerprint,
        branding_entitlement_id=selection.branding_entitlement_id,
        branding_entitlement_revision=selection.branding_entitlement_revision,
        branding_entitlement_fingerprint=selection.branding_entitlement_fingerprint,
        branding_tier=str(selection.to_dict()["branding_tier"]),
    )
    current = TenantBrandingCurrentProfile(
        pointer=pointer,
        selection=selection,
        profile=profile,
    )
    return entitlement, current, logo, favicon


def _install_happy_authorities(
    monkeypatch: pytest.MonkeyPatch,
    *,
    entitlement: TenantBrandingEntitlement,
    current: TenantBrandingCurrentProfile,
    logo: TenantBrandingResolvedAsset,
    favicon: TenantBrandingResolvedAsset,
    session: object,
) -> list[tuple[str, object]]:
    """Patch exact upstream reads while recording shared-session propagation."""
    calls: list[tuple[str, object]] = []

    def profile_reader(
        tenant_id: str,
        profile_collection: Any,
        selection_collection: Any,
        current_collection: Any,
        *,
        session: object,
    ) -> TenantBrandingCurrentProfile:
        del profile_collection, selection_collection, current_collection
        calls.append(("profile", session))
        assert tenant_id == current.pointer.tenant_id
        return current

    def entitlement_reader(
        tenant_id: str,
        entitlement_id: str,
        history_collection: Any,
        current_collection: Any,
        *,
        session: object,
    ) -> TenantBrandingEntitlement:
        del history_collection, current_collection
        calls.append(("entitlement", session))
        assert tenant_id == entitlement.tenant_id
        assert entitlement_id == entitlement.entitlement_id
        return entitlement

    def asset_reader(
        tenant_id: str,
        asset_reference: str,
        *,
        expected_content_fingerprint: str,
        expected_kind: TenantBrandingAssetKind | str,
        collection: Any,
        session: object,
    ) -> TenantBrandingResolvedAsset:
        del collection
        calls.append((f"asset:{asset_reference}", session))
        assert tenant_id == entitlement.tenant_id
        kind = TenantBrandingAssetKind(expected_kind)
        resolved = logo if kind is TenantBrandingAssetKind.LOGO else favicon
        assert resolved.asset.asset_reference == asset_reference
        assert resolved.asset.content_fingerprint == expected_content_fingerprint
        return resolved

    monkeypatch.setattr(projection, "get_current_branding_profile", profile_reader)
    monkeypatch.setattr(
        projection,
        "get_current_branding_entitlement",
        entitlement_reader,
    )
    monkeypatch.setattr(projection, "resolve_branding_asset", asset_reader)
    return calls


def _invoke(
    *,
    tenant_id: str = "tenant-a",
    session: object,
) -> projection.TenantBrandingWorkspaceProjection | None:
    """Invoke the composer with opaque collection sentinels."""
    return projection.build_tenant_branding_workspace_projection(
        tenant_id=tenant_id,
        entitlement_history_collection=object(),
        entitlement_current_collection=object(),
        profile_collection=object(),
        selection_collection=object(),
        profile_current_collection=object(),
        asset_collection=object(),
        session=session,
    )


def test_exact_current_active_branding_projects_only_bounded_safe_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exact correlated current truth produces the expected browser-safe shape."""
    entitlement, current, logo, favicon = _bundle()
    session = object()
    calls = _install_happy_authorities(
        monkeypatch,
        entitlement=entitlement,
        current=current,
        logo=logo,
        favicon=favicon,
        session=session,
    )

    result = _invoke(session=session)
    assert result is not None
    payload = result.to_dict()

    assert payload["tenantId"] == "tenant-a"
    assert payload["profileId"] == "profile-primary"
    assert payload["selectionRevision"] == 1
    assert payload["entitlementRevision"] == entitlement.lifecycle_revision
    assert payload["brandingTier"] == TenantBrandingTier.INSTITUTIONAL.value
    assert payload["primaryColor"] == "#112233"
    assert payload["emailDisplayName"] == "Acme Legal"
    assert payload["platformTrustMarkRequired"] is True
    assert payload["logo"] == {
        "reference": logo.asset.asset_reference,
        "contentFingerprint": logo.asset.content_fingerprint,
        "mediaType": "image/png",
        "kind": "LOGO",
    }
    assert payload["favicon"] == {
        "reference": favicon.asset.asset_reference,
        "contentFingerprint": favicon.asset.content_fingerprint,
        "mediaType": "image/png",
        "kind": "FAVICON",
    }

    serialized = json.dumps(payload, sort_keys=True)
    assert "data:" not in serialized
    assert "http://" not in serialized
    assert "https://" not in serialized
    assert "base64" not in serialized.lower()
    assert "D21B6-logo" not in serialized
    assert "D21B6-favicon" not in serialized
    assert calls and all(recorded_session is session for _, recorded_session in calls)


def test_missing_current_profile_is_safe_no_branding_absence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A tenant without an explicit current profile receives no tenant branding."""

    def missing(*_: Any, **__: Any) -> Any:
        raise TenantBrandingProfileRegistryCurrentPointerMissingError()

    monkeypatch.setattr(projection, "get_current_branding_profile", missing)
    assert _invoke(session=object()) is None


def test_profile_authority_outage_is_not_silently_defaulted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Infrastructure failure differs from lawful no-branding absence."""

    def unavailable(*_: Any, **__: Any) -> Any:
        raise TenantBrandingProfileRegistryPersistenceUnavailableError()

    monkeypatch.setattr(projection, "get_current_branding_profile", unavailable)
    with pytest.raises(
        projection.TenantBrandingWorkspaceProjectionError
    ) as raised:
        _invoke(session=object())
    assert raised.value.code == "D21B6_PROFILE_AUTHORITY_UNAVAILABLE"


def test_suspended_current_entitlement_rejects_existing_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A once-approved profile cannot render after entitlement suspension."""
    entitlement, current, logo, favicon = _bundle()
    suspended = entitlement.transition(
        TenantBrandingEntitlementState.SUSPENDED,
        expected_revision=entitlement.lifecycle_revision,
        evidence_reference="suspension-1",
        evidence_fingerprint=FP,
        occurred_at=NOW + timedelta(minutes=1),
    )
    session = object()
    _install_happy_authorities(
        monkeypatch,
        entitlement=suspended,
        current=current,
        logo=logo,
        favicon=favicon,
        session=session,
    )

    with pytest.raises(
        projection.TenantBrandingWorkspaceProjectionError
    ) as raised:
        _invoke(session=session)
    assert raised.value.code == "D21B6_ENTITLEMENT_INACTIVE"


def test_different_active_entitlement_evidence_rejects_stale_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ACTIVE alone is insufficient when the current snapshot no longer matches."""
    _, current, logo, favicon = _bundle()
    divergent = _active_entitlement(
        source_reference="different-composition-source"
    )
    session = object()
    _install_happy_authorities(
        monkeypatch,
        entitlement=divergent,
        current=current,
        logo=logo,
        favicon=favicon,
        session=session,
    )

    with pytest.raises(
        projection.TenantBrandingWorkspaceProjectionError
    ) as raised:
        _invoke(session=session)
    assert raised.value.code == "D21B6_ENTITLEMENT_CORRELATION_INVALID"


def test_asset_authority_conflict_rejects_instead_of_projecting_reference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A profile reference is not browser-usable until D21B5B resolves it."""
    entitlement, current, logo, favicon = _bundle()
    session = object()
    _install_happy_authorities(
        monkeypatch,
        entitlement=entitlement,
        current=current,
        logo=logo,
        favicon=favicon,
        session=session,
    )

    def conflicting_asset(*_: Any, **__: Any) -> Any:
        raise TenantBrandingAssetRegistryConflictError()

    monkeypatch.setattr(projection, "resolve_branding_asset", conflicting_asset)
    with pytest.raises(
        projection.TenantBrandingWorkspaceProjectionError
    ) as raised:
        _invoke(session=session)
    assert raised.value.code == "D21B6_ASSET_AUTHORITY_UNAVAILABLE"


def test_foreign_profile_tenant_rejects_before_entitlement_or_asset_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cross-tenant current evidence can never become tenant branding."""
    _, foreign_current, _, _ = _bundle("tenant-b")

    def foreign_reader(*_: Any, **__: Any) -> TenantBrandingCurrentProfile:
        return foreign_current

    monkeypatch.setattr(
        projection,
        "get_current_branding_profile",
        foreign_reader,
    )
    with pytest.raises(
        projection.TenantBrandingWorkspaceProjectionError
    ) as raised:
        _invoke(tenant_id="tenant-a", session=object())
    assert raised.value.code == "D21B6_PROFILE_TENANT_CORRELATION_INVALID"


@pytest.mark.parametrize(
    ("source", "error"),
    (
        (
            "profile",
            TenantBrandingProfileRegistryRetryRequiredError(),
        ),
        (
            "entitlement",
            TenantBrandingEntitlementRegistryRetryRequiredError(),
        ),
        (
            "asset",
            TenantBrandingAssetRegistryRetryRequiredError(),
        ),
    ),
)
def test_whole_transaction_retry_taxonomy_is_preserved(
    monkeypatch: pytest.MonkeyPatch,
    source: str,
    error: Exception,
) -> None:
    """Transient registry races remain distinguishable to the transaction owner."""
    entitlement, current, logo, favicon = _bundle()
    session = object()
    _install_happy_authorities(
        monkeypatch,
        entitlement=entitlement,
        current=current,
        logo=logo,
        favicon=favicon,
        session=session,
    )

    if source == "profile":
        monkeypatch.setattr(
            projection,
            "get_current_branding_profile",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
        )
    elif source == "entitlement":
        monkeypatch.setattr(
            projection,
            "get_current_branding_entitlement",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
        )
    else:
        monkeypatch.setattr(
            projection,
            "resolve_branding_asset",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
        )

    with pytest.raises(
        projection.TenantBrandingWorkspaceProjectionRetryRequiredError
    ) as raised:
        _invoke(session=session)
    assert raised.value.code == "D21B6_WHOLE_TRANSACTION_RETRY_REQUIRED"
    assert raised.value.__cause__ is error


def test_entitlement_authority_outage_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A durable current profile cannot bypass entitlement persistence failure."""
    entitlement, current, logo, favicon = _bundle()
    session = object()
    _install_happy_authorities(
        monkeypatch,
        entitlement=entitlement,
        current=current,
        logo=logo,
        favicon=favicon,
        session=session,
    )

    def unavailable(*_: Any, **__: Any) -> Any:
        raise TenantBrandingEntitlementRegistryPersistenceUnavailableError()

    monkeypatch.setattr(
        projection,
        "get_current_branding_entitlement",
        unavailable,
    )
    with pytest.raises(
        projection.TenantBrandingWorkspaceProjectionError
    ) as raised:
        _invoke(session=session)
    assert raised.value.code == "D21B6_ENTITLEMENT_AUTHORITY_UNAVAILABLE"


def test_invalid_tenant_input_rejects_before_any_authority_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Malformed tenant scope cannot reach durable authorities."""
    called = False

    def reader(*_: Any, **__: Any) -> Any:
        nonlocal called
        called = True
        raise AssertionError("authority must not be called")

    monkeypatch.setattr(projection, "get_current_branding_profile", reader)
    with pytest.raises(
        projection.TenantBrandingWorkspaceProjectionError
    ) as raised:
        _invoke(tenant_id=" tenant-a ", session=object())
    assert raised.value.code == "D21B6_TENANT_ID_INVALID"
    assert called is False


# ARTIFACT: test_tenant_branding_workspace_projection.py
# VERSION: v1.0.2-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION-CERT
# AUTHORITY BOUNDARY: deterministic D21B6 composition evidence only; no persistence, IAM, browser or financial authority
# TENANT POSTURE: exact synthetic tenant correlation with adversarial cross-tenant rejection
# FAIL-CLOSED POSTURE: stale/inactive/outage/asset-conflict/retry conditions never become presentation truth
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
