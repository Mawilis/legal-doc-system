"""WILSY OS current tenant branding asset delivery composer.

TITLE: Tenant Branding Workspace Asset Delivery
VERSION: v1.0.0-D21B10-TENANT-BRANDING-ASSET-DELIVERY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Return immutable branding bytes only after D21B6 proves the exact
         current tenant branding chain and D21B5B re-resolves the chosen
         logo/favicon under the same caller-owned Mongo transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_branding_workspace_asset_delivery.py
COLLABORATION / OWNERSHIP: D21B6 owns current branding composition; D21B5B owns
                            immutable asset metadata/bytes. D21B10 owns read-only
                            delivery composition only. HTTP transport is a later
                            adapter and callers own transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B10-TENANT-BRANDING-ASSET-DELIVERY establishes exact
           current-logo/current-favicon delivery. It never trusts a browser
           asset reference, URL, path or fingerprint: the requested kind selects
           only the descriptor already proven by D21B6, then D21B5B must
           re-resolve that same tenant/reference/fingerprint/kind before bytes
           are released.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Returns only bounded immutable image bytes already
                             registered by D21B5A/B. No arbitrary file access,
                             public URL, path traversal, base64, HTML/CSS/JS,
                             credentials or browser-supplied asset authority.
TENANT BOUNDARY: Exact input tenant_id is revalidated by D21B6 and D21B5B; the
                 delivered asset tenant must match it exactly.
AUTHORITY BOUNDARY: Read-only current branding asset delivery only. It creates
                    no authentication, membership, IAM, profile selection,
                    entitlement, upload, legal-command or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Every source read uses the same already-active caller
                      transaction. D21B10 never starts, commits, aborts, retries
                      or closes Mongo sessions/transactions.
FAIL-CLOSED DECLARATION: No current branding, no configured requested asset,
                         stale/inactive/corrupt branding, asset mismatch,
                         transaction races or persistence failure never release
                         bytes. Whole-transaction retry taxonomy is preserved.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, NoReturn

from tools.eos.auth.tenant_branding_workspace_projection import (
    TenantBrandingWorkspaceAsset,
    TenantBrandingWorkspaceProjectionError,
    TenantBrandingWorkspaceProjectionRetryRequiredError,
    build_tenant_branding_workspace_projection,
)
from tools.eos.saas.billing.tenant_branding_asset_registry import (
    TenantBrandingAssetRegistryError,
    TenantBrandingAssetRegistryRetryRequiredError,
    TenantBrandingResolvedAsset,
    resolve as resolve_branding_asset,
)
from tools.eos.saas.domain.tenant_branding_asset import TenantBrandingAssetKind


VERSION: Final[str] = "v1.0.0-D21B10-TENANT-BRANDING-ASSET-DELIVERY"


class TenantBrandingWorkspaceAssetDeliveryError(RuntimeError):
    """Base fail-closed D21B10 delivery-composition error."""

    default_code = "D21B10_ASSET_DELIVERY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class TenantBrandingWorkspaceAssetNotConfiguredError(
    TenantBrandingWorkspaceAssetDeliveryError
):
    """The tenant has no current branding or no requested current asset."""

    default_code = "D21B10_ASSET_NOT_CONFIGURED"


class TenantBrandingWorkspaceAssetRetryRequiredError(
    TenantBrandingWorkspaceAssetDeliveryError
):
    """Caller must abort and retry the complete read transaction."""

    default_code = "D21B10_WHOLE_TRANSACTION_RETRY_REQUIRED"


def _raise(
    error_type: type[TenantBrandingWorkspaceAssetDeliveryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


@dataclass(frozen=True, slots=True)
class TenantBrandingWorkspaceAssetDelivery:
    """Exact current immutable asset evidence plus releasable bounded bytes."""

    tenant_id: str
    asset_reference: str
    content_fingerprint: str
    media_type: str
    kind: TenantBrandingAssetKind
    content: bytes

    def __post_init__(self) -> None:
        if (
            not isinstance(self.tenant_id, str)
            or not self.tenant_id
            or self.tenant_id != self.tenant_id.strip()
            or not isinstance(self.asset_reference, str)
            or not self.asset_reference
            or not self.asset_reference.startswith(f"asset:{self.tenant_id}:")
            or not isinstance(self.content_fingerprint, str)
            or len(self.content_fingerprint) != 128
            or any(character not in "0123456789abcdef" for character in self.content_fingerprint)
            or not isinstance(self.media_type, str)
            or not self.media_type
            or type(self.kind) is not TenantBrandingAssetKind
            or not isinstance(self.content, bytes)
            or not self.content
        ):
            _raise(
                TenantBrandingWorkspaceAssetDeliveryError,
                "D21B10_DELIVERY_VALUE_INVALID",
            )


def _descriptor_for_kind(
    branding: Any,
    kind: TenantBrandingAssetKind,
) -> TenantBrandingWorkspaceAsset | None:
    if kind is TenantBrandingAssetKind.LOGO:
        return branding.logo
    if kind is TenantBrandingAssetKind.FAVICON:
        return branding.favicon
    _raise(
        TenantBrandingWorkspaceAssetDeliveryError,
        "D21B10_ASSET_KIND_INVALID",
    )


def resolve_current_tenant_branding_asset(
    *,
    tenant_id: str,
    asset_kind: TenantBrandingAssetKind | str,
    entitlement_history_collection: Any,
    entitlement_current_collection: Any,
    profile_collection: Any,
    selection_collection: Any,
    profile_current_collection: Any,
    asset_collection: Any,
    session: Any,
) -> TenantBrandingWorkspaceAssetDelivery:
    """Return exact current logo/favicon bytes after full currentness proof."""
    if not isinstance(tenant_id, str) or not tenant_id or tenant_id != tenant_id.strip():
        _raise(
            TenantBrandingWorkspaceAssetDeliveryError,
            "D21B10_TENANT_ID_INVALID",
        )
    try:
        kind = TenantBrandingAssetKind(asset_kind)
    except (TypeError, ValueError) as error:
        _raise(
            TenantBrandingWorkspaceAssetDeliveryError,
            "D21B10_ASSET_KIND_INVALID",
            error,
        )

    try:
        branding = build_tenant_branding_workspace_projection(
            tenant_id=tenant_id,
            entitlement_history_collection=entitlement_history_collection,
            entitlement_current_collection=entitlement_current_collection,
            profile_collection=profile_collection,
            selection_collection=selection_collection,
            profile_current_collection=profile_current_collection,
            asset_collection=asset_collection,
            session=session,
        )
    except TenantBrandingWorkspaceProjectionRetryRequiredError as error:
        _raise(
            TenantBrandingWorkspaceAssetRetryRequiredError,
            cause=error,
        )
    except TenantBrandingWorkspaceProjectionError as error:
        _raise(
            TenantBrandingWorkspaceAssetDeliveryError,
            "D21B10_CURRENT_BRANDING_AUTHORITY_UNAVAILABLE",
            error,
        )

    if branding is None:
        _raise(
            TenantBrandingWorkspaceAssetNotConfiguredError,
            "D21B10_BRANDING_NOT_CONFIGURED",
        )

    descriptor = _descriptor_for_kind(branding, kind)
    if descriptor is None:
        _raise(TenantBrandingWorkspaceAssetNotConfiguredError)

    try:
        resolved: TenantBrandingResolvedAsset = resolve_branding_asset(
            tenant_id,
            descriptor.reference,
            expected_content_fingerprint=descriptor.content_fingerprint,
            expected_kind=kind,
            collection=asset_collection,
            session=session,
        )
    except TenantBrandingAssetRegistryRetryRequiredError as error:
        _raise(
            TenantBrandingWorkspaceAssetRetryRequiredError,
            cause=error,
        )
    except TenantBrandingAssetRegistryError as error:
        _raise(
            TenantBrandingWorkspaceAssetDeliveryError,
            "D21B10_ASSET_AUTHORITY_UNAVAILABLE",
            error,
        )

    asset = resolved.asset
    if (
        asset.tenant_id != tenant_id
        or asset.asset_reference != descriptor.reference
        or asset.content_fingerprint != descriptor.content_fingerprint
        or asset.media_type != descriptor.media_type
        or asset.asset_kind is not kind
    ):
        _raise(
            TenantBrandingWorkspaceAssetDeliveryError,
            "D21B10_ASSET_CORRELATION_INVALID",
        )

    return TenantBrandingWorkspaceAssetDelivery(
        tenant_id=tenant_id,
        asset_reference=asset.asset_reference,
        content_fingerprint=asset.content_fingerprint,
        media_type=asset.media_type,
        kind=kind,
        content=resolved.content,
    )


__all__ = [
    "VERSION",
    "TenantBrandingWorkspaceAssetDelivery",
    "TenantBrandingWorkspaceAssetDeliveryError",
    "TenantBrandingWorkspaceAssetNotConfiguredError",
    "TenantBrandingWorkspaceAssetRetryRequiredError",
    "resolve_current_tenant_branding_asset",
]


# ARTIFACT: tenant_branding_workspace_asset_delivery.py
# VERSION: v1.0.0-D21B10-TENANT-BRANDING-ASSET-DELIVERY
# AUTHORITY BOUNDARY: read-only current logo/favicon byte delivery after D21B6 + D21B5B proof
# TENANT POSTURE: exact tenant correlation; no browser-provided asset identity is trusted
# FAIL-CLOSED POSTURE: absent/stale/corrupt/mismatched authority releases no bytes; retry taxonomy preserved
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
