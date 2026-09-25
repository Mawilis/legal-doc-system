"""WILSY OS tenant branding workspace projection composer.

TITLE: Tenant Branding Workspace Projection
VERSION: v1.0.1-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Compose one bounded browser-safe tenant-branding projection only after
         exact durable current-profile correlation, current ACTIVE entitlement
         revalidation and immutable asset-byte resolution under one caller-owned
         Mongo transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_branding_workspace_projection.py
COLLABORATION / OWNERSHIP: D21B2B owns durable branding-entitlement currentness;
                            D21B4B owns durable profile/selection currentness;
                            D21B5B owns immutable asset bytes/resolution. This
                            artifact owns read-only runtime composition only and
                            creates no new entitlement, selection or asset truth.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.1-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION preserves explicit whole-transaction retry taxonomy from
           D21B2B/D21B4B/D21B5B so the caller can abort and restart the complete
           read transaction rather than misclassifying a transient race/outage as
           ordinary presentation denial.
           v1.0.0-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION established the fail-closed runtime chain current profile ->
           exact current ACTIVE entitlement -> exact immutable logo/favicon
           resolution -> bounded browser-safe projection. Absence of a current
           profile yields no tenant branding; once currentness exists, any stale
           entitlement, corruption, missing/mismatched asset or persistence
           failure rejects.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Projects only approved presentation metadata and
                             opaque asset descriptors. Raw bytes, URLs, paths,
                             base64, credentials, HTML/CSS/JS and legacy
                             bank/tax/legal-identity material are excluded.
TENANT BOUNDARY: Input tenant_id must exactly equal current pointer, selection,
                 profile, entitlement and every resolved asset tenant identity.
AUTHORITY BOUNDARY: Read-only tenant-brand presentation composition only. A
                    projection grants no authentication, membership, IAM,
                    workspace admission, legal-command or asset-upload authority.
FINANCIAL AUTHORITY BOUNDARY: No price, bank, tax, invoice, charge, payment,
                               execution or settlement truth. Kennel EOS remains
                               the exclusive financial execution authority.
TRANSACTION BOUNDARY: All registry reads receive the same already-active
                      caller-owned Mongo session. This artifact never starts,
                      commits, aborts, retries or closes transactions.
FAIL-CLOSED DECLARATION: Existing current branding must correlate exactly across
                         D21B2B/D21B4B/D21B5B. Missing current branding alone is
                         a safe absence; all corruption, stale entitlement,
                         asset mismatch and infrastructure failures reject.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, NoReturn

from tools.eos.saas.billing.tenant_branding_asset_registry import (
    TenantBrandingAssetRegistryError,
    TenantBrandingAssetRegistryRetryRequiredError,
    TenantBrandingResolvedAsset,
    resolve as resolve_branding_asset,
)
from tools.eos.saas.billing.tenant_branding_entitlement_registry import (
    TenantBrandingEntitlementRegistryError,
    TenantBrandingEntitlementRegistryRetryRequiredError,
    get_current as get_current_branding_entitlement,
)
from tools.eos.saas.billing.tenant_branding_profile_registry import (
    TenantBrandingCurrentProfile,
    TenantBrandingProfileRegistryCurrentPointerMissingError,
    TenantBrandingProfileRegistryError,
    TenantBrandingProfileRegistryRetryRequiredError,
    get_current as get_current_branding_profile,
)
from tools.eos.saas.domain.tenant_branding_asset import TenantBrandingAssetKind
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlement,
    TenantBrandingEntitlementState,
)


VERSION: Final[str] = "v1.0.1-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION"


class TenantBrandingWorkspaceProjectionError(RuntimeError):
    """Fail-closed D21B6 runtime branding composition error with stable code."""

    default_code = "D21B6_BRANDING_PROJECTION_ERROR"

    def __init__(self, code: str | None = None) -> None:
        """Create one bounded composition failure without leaking durable state."""
        self.code = code or self.default_code
        super().__init__(self.code)


class TenantBrandingWorkspaceProjectionRetryRequiredError(
    TenantBrandingWorkspaceProjectionError
):
    """Caller must abort and restart the complete branding read transaction."""

    default_code = "D21B6_WHOLE_TRANSACTION_RETRY_REQUIRED"


def _raise_retry(cause: BaseException) -> NoReturn:
    """Preserve governed whole-transaction retry semantics across composition."""
    raise TenantBrandingWorkspaceProjectionRetryRequiredError() from cause


def _raise(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable projection error while preserving the technical cause."""
    error = TenantBrandingWorkspaceProjectionError(code)
    if cause is None:
        raise error
    raise error from cause


@dataclass(frozen=True, slots=True)
class TenantBrandingWorkspaceAsset:
    """Browser-safe descriptor for one already-resolved immutable branding asset."""

    reference: str
    content_fingerprint: str
    media_type: str
    kind: str

    def to_dict(self) -> dict[str, str]:
        """Serialize opaque asset evidence without bytes or a fabricated URL."""
        return {
            "reference": self.reference,
            "contentFingerprint": self.content_fingerprint,
            "mediaType": self.media_type,
            "kind": self.kind,
        }


@dataclass(frozen=True, slots=True)
class TenantBrandingWorkspaceProjection:
    """Bounded tenant branding presentation proven current at read time."""

    tenant_id: str
    profile_id: str
    profile_fingerprint: str
    selection_id: str
    selection_revision: int
    entitlement_id: str
    entitlement_revision: int
    entitlement_fingerprint: str
    branding_tier: str
    profile_label: str
    primary_color: str | None
    secondary_color: str | None
    accent_color: str | None
    email_display_name: str | None
    platform_trust_mark_required: bool
    logo: TenantBrandingWorkspaceAsset | None
    favicon: TenantBrandingWorkspaceAsset | None

    def to_dict(self) -> dict[str, object]:
        """Serialize only browser-safe presentation/provenance fields."""
        return {
            "tenantId": self.tenant_id,
            "profileId": self.profile_id,
            "profileFingerprint": self.profile_fingerprint,
            "selectionId": self.selection_id,
            "selectionRevision": self.selection_revision,
            "entitlementId": self.entitlement_id,
            "entitlementRevision": self.entitlement_revision,
            "entitlementFingerprint": self.entitlement_fingerprint,
            "brandingTier": self.branding_tier,
            "profileLabel": self.profile_label,
            "primaryColor": self.primary_color,
            "secondaryColor": self.secondary_color,
            "accentColor": self.accent_color,
            "emailDisplayName": self.email_display_name,
            "platformTrustMarkRequired": self.platform_trust_mark_required,
            "logo": None if self.logo is None else self.logo.to_dict(),
            "favicon": None if self.favicon is None else self.favicon.to_dict(),
        }


def _asset_descriptor(
    *,
    tenant_id: str,
    expected_reference: str,
    expected_content_fingerprint: str,
    expected_kind: TenantBrandingAssetKind,
    resolved: TenantBrandingResolvedAsset,
) -> TenantBrandingWorkspaceAsset:
    """Correlate one D21B5B result to exact profile-supplied asset evidence."""
    asset = resolved.asset
    if (
        asset.tenant_id != tenant_id
        or asset.asset_reference != expected_reference
        or asset.content_fingerprint != expected_content_fingerprint
        or asset.asset_kind is not expected_kind
    ):
        _raise("D21B6_ASSET_CORRELATION_INVALID")
    return TenantBrandingWorkspaceAsset(
        reference=asset.asset_reference,
        content_fingerprint=asset.content_fingerprint,
        media_type=asset.media_type,
        kind=expected_kind.value,
    )


def _resolve_optional_asset(
    *,
    tenant_id: str,
    reference: str | None,
    content_fingerprint: str | None,
    kind: TenantBrandingAssetKind,
    asset_collection: Any,
    session: Any,
) -> TenantBrandingWorkspaceAsset | None:
    """Resolve one optional profile asset; partial evidence always rejects."""
    if reference is None and content_fingerprint is None:
        return None
    if reference is None or content_fingerprint is None:
        _raise("D21B6_PROFILE_ASSET_EVIDENCE_INVALID")
    try:
        resolved = resolve_branding_asset(
            tenant_id,
            reference,
            expected_content_fingerprint=content_fingerprint,
            expected_kind=kind,
            collection=asset_collection,
            session=session,
        )
    except TenantBrandingAssetRegistryRetryRequiredError as error:
        _raise_retry(error)
    except TenantBrandingAssetRegistryError as error:
        _raise("D21B6_ASSET_AUTHORITY_UNAVAILABLE", error)
    return _asset_descriptor(
        tenant_id=tenant_id,
        expected_reference=reference,
        expected_content_fingerprint=content_fingerprint,
        expected_kind=kind,
        resolved=resolved,
    )


def build_tenant_branding_workspace_projection(
    *,
    tenant_id: str,
    entitlement_history_collection: Any,
    entitlement_current_collection: Any,
    profile_collection: Any,
    selection_collection: Any,
    profile_current_collection: Any,
    asset_collection: Any,
    session: Any,
) -> TenantBrandingWorkspaceProjection | None:
    """Compose current tenant branding from sovereign durable authorities only.

    A tenant with no explicit D21B4B current-profile pointer has no tenant
    branding projection and safely falls back to WILSY platform presentation.
    If a pointer exists, the exact D21B2B entitlement must still be ACTIVE and
    identical to the profile/selection entitlement snapshot, and every referenced
    asset must resolve through D21B5B with exact content fingerprint and kind.

    The caller owns the already-active transaction and must abort/retry the whole
    transaction when any underlying registry signals a transaction retry.
    """
    if not isinstance(tenant_id, str) or not tenant_id or tenant_id != tenant_id.strip():
        _raise("D21B6_TENANT_ID_INVALID")

    try:
        current: TenantBrandingCurrentProfile = get_current_branding_profile(
            tenant_id,
            profile_collection,
            selection_collection,
            profile_current_collection,
            session=session,
        )
    except TenantBrandingProfileRegistryCurrentPointerMissingError:
        return None
    except TenantBrandingProfileRegistryRetryRequiredError as error:
        _raise_retry(error)
    except TenantBrandingProfileRegistryError as error:
        _raise("D21B6_PROFILE_AUTHORITY_UNAVAILABLE", error)

    if (
        current.pointer.tenant_id != tenant_id
        or current.selection.tenant_id != tenant_id
        or current.profile.tenant_id != tenant_id
    ):
        _raise("D21B6_PROFILE_TENANT_CORRELATION_INVALID")

    entitlement_id = current.pointer.branding_entitlement_id
    try:
        entitlement = get_current_branding_entitlement(
            tenant_id,
            entitlement_id,
            entitlement_history_collection,
            entitlement_current_collection,
            session=session,
        )
    except TenantBrandingEntitlementRegistryRetryRequiredError as error:
        _raise_retry(error)
    except TenantBrandingEntitlementRegistryError as error:
        _raise("D21B6_ENTITLEMENT_AUTHORITY_UNAVAILABLE", error)

    if type(entitlement) is not TenantBrandingEntitlement:
        _raise("D21B6_ENTITLEMENT_AUTHORITY_INVALID")
    if entitlement.tenant_id != tenant_id or entitlement.entitlement_id != entitlement_id:
        _raise("D21B6_ENTITLEMENT_TENANT_CORRELATION_INVALID")
    if entitlement.lifecycle_state is not TenantBrandingEntitlementState.ACTIVE:
        _raise("D21B6_ENTITLEMENT_INACTIVE")

    embedded = current.profile.branding_entitlement
    if type(embedded) is not TenantBrandingEntitlement:
        _raise("D21B6_PROFILE_ENTITLEMENT_INVALID")

    entitlement_payload = entitlement.to_dict()
    pointer_tier = current.pointer.branding_tier
    entitlement_tier = entitlement_payload.get("branding_tier")
    if (
        embedded.to_dict() != entitlement_payload
        or current.pointer.branding_entitlement_revision
        != entitlement.lifecycle_revision
        or current.pointer.branding_entitlement_fingerprint
        != entitlement.fingerprint
        or current.selection.branding_entitlement_id != entitlement.entitlement_id
        or current.selection.branding_entitlement_revision
        != entitlement.lifecycle_revision
        or current.selection.branding_entitlement_fingerprint
        != entitlement.fingerprint
        or pointer_tier != entitlement_tier
    ):
        _raise("D21B6_ENTITLEMENT_CORRELATION_INVALID")

    logo = _resolve_optional_asset(
        tenant_id=tenant_id,
        reference=current.profile.logo_asset_reference,
        content_fingerprint=current.profile.logo_asset_fingerprint,
        kind=TenantBrandingAssetKind.LOGO,
        asset_collection=asset_collection,
        session=session,
    )
    favicon = _resolve_optional_asset(
        tenant_id=tenant_id,
        reference=current.profile.favicon_asset_reference,
        content_fingerprint=current.profile.favicon_asset_fingerprint,
        kind=TenantBrandingAssetKind.FAVICON,
        asset_collection=asset_collection,
        session=session,
    )

    if current.profile.platform_trust_mark_required is not True:
        _raise("D21B6_PLATFORM_TRUST_MARK_REQUIRED")

    return TenantBrandingWorkspaceProjection(
        tenant_id=tenant_id,
        profile_id=current.profile.profile_id,
        profile_fingerprint=current.profile.fingerprint,
        selection_id=current.selection.selection_id,
        selection_revision=current.selection.selection_revision,
        entitlement_id=entitlement.entitlement_id,
        entitlement_revision=entitlement.lifecycle_revision,
        entitlement_fingerprint=entitlement.fingerprint,
        branding_tier=str(entitlement_tier),
        profile_label=current.profile.profile_label,
        primary_color=current.profile.primary_color,
        secondary_color=current.profile.secondary_color,
        accent_color=current.profile.accent_color,
        email_display_name=current.profile.email_display_name,
        platform_trust_mark_required=True,
        logo=logo,
        favicon=favicon,
    )


__all__ = [
    "VERSION",
    "TenantBrandingWorkspaceAsset",
    "TenantBrandingWorkspaceProjection",
    "TenantBrandingWorkspaceProjectionError",
    "TenantBrandingWorkspaceProjectionRetryRequiredError",
    "build_tenant_branding_workspace_projection",
]


# ARTIFACT: tenant_branding_workspace_projection.py
# VERSION: v1.0.1-D21B6-TENANT-BRANDING-WORKSPACE-PROJECTION
# AUTHORITY BOUNDARY: read-only current branding composition only; no auth, IAM, upload, legal-command or financial authority
# TENANT POSTURE: exact tenant correlation across current profile, selection, entitlement and resolved assets
# FAIL-CLOSED POSTURE: safe absence only when no current profile exists; all existing-current drift, corruption, staleness, asset mismatch and outages reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
