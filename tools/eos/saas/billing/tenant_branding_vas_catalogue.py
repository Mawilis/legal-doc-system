"""WILSY OS canonical commercial identity catalogue for Tenant Branding VAS.

TITLE: Tenant Branding VAS Commercial Catalogue
VERSION: v1.0.0-D21C1-TENANT-BRANDING-VAS-CATALOGUE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Own exact, immutable commercial feature identities that map a
         subscription's canonical PlanRegistry feature snapshot to one D21B
         branding tier. This catalogue does not price, charge, grant access,
         approve profiles, select assets, or authorize browser presentation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_branding_vas_catalogue.py
COLLABORATION / OWNERSHIP: PlanRegistry persists canonical plan features;
                            SubscriptionRegistry snapshots them. This module
                            owns only the recognized Branding VAS identities.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-D21C1 establishes exact Professional, Institutional and
           Enterprise feature tokens. Starter remains the platform baseline
           and has no separately paid Branding VAS identity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Pure immutable catalogue; no credentials, assets,
                             payment-provider state or external calls.
TENANT BOUNDARY: Catalogue facts are global; tenant scope is supplied by the
                 canonical subscription evidence consumed elsewhere.
AUTHORITY BOUNDARY: Commercial identity mapping only; no entitlement or IAM.
FINANCIAL AUTHORITY BOUNDARY: No price, charge, payment, settlement or
                               execution truth. Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Unknown and conflicting identities reject when used
                         for eligibility; unrelated plan features are ignored.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Final, Mapping, cast

from tools.eos.saas.billing.tenant_branding_vas_policy import (
    TenantBrandingTier,
)


VERSION: Final[str] = "v1.0.0-D21C1-TENANT-BRANDING-VAS-CATALOGUE"
CATALOGUE_SCHEMA: Final[str] = "WILSY-TENANT-BRANDING-VAS-CATALOGUE/V1"
CATALOGUE_IDENTITY: Final[str] = "WILSY_TENANT_BRANDING_VAS_COMMERCIAL_CATALOGUE"

BRANDING_VAS_PROFESSIONAL_ID: Final[str] = (
    "wilsy.vas.tenant_branding.professional.v1"
)
BRANDING_VAS_INSTITUTIONAL_ID: Final[str] = (
    "wilsy.vas.tenant_branding.institutional.v1"
)
BRANDING_VAS_ENTERPRISE_ID: Final[str] = (
    "wilsy.vas.tenant_branding.enterprise.v1"
)


class TenantBrandingVASCatalogueError(ValueError):
    """Raised when commercial Branding VAS identity evidence is invalid."""


class TenantBrandingVASCommercialTier(str, Enum):
    """Paid Branding VAS tiers; Starter is intentionally not included."""

    PROFESSIONAL = TenantBrandingTier.PROFESSIONAL.value
    INSTITUTIONAL = TenantBrandingTier.INSTITUTIONAL.value
    ENTERPRISE = TenantBrandingTier.ENTERPRISE.value


@dataclass(frozen=True, slots=True)
class TenantBrandingVASCommercialProduct:
    """One exact commercial identity-to-D21B tier mapping."""

    commercial_id: str
    branding_tier: TenantBrandingTier

    def __post_init__(self) -> None:
        """Reject caller-created identity or tier substitutions."""
        expected = _CANONICAL_PRODUCTS.get(self.commercial_id)
        if expected is None or expected is not self.branding_tier:
            raise TenantBrandingVASCatalogueError(
                "D21C1_COMMERCIAL_IDENTITY_INVALID"
            )

    @property
    def catalogue_fingerprint(self) -> str:
        """Return the deterministic catalogue fingerprint for this product."""
        return _catalogue_fingerprint()


_CANONICAL_PRODUCTS: Final[Mapping[str, TenantBrandingTier]] = MappingProxyType(
    {
        BRANDING_VAS_PROFESSIONAL_ID: TenantBrandingTier.PROFESSIONAL,
        BRANDING_VAS_INSTITUTIONAL_ID: TenantBrandingTier.INSTITUTIONAL,
        BRANDING_VAS_ENTERPRISE_ID: TenantBrandingTier.ENTERPRISE,
    }
)


def _catalogue_fingerprint() -> str:
    """Hash exact identity/tier material without price or payment fields."""
    payload = {
        "schema": CATALOGUE_SCHEMA,
        "identity": CATALOGUE_IDENTITY,
        "version": VERSION,
        "products": [
            {"commercial_id": key, "branding_tier": value.value}
            for key, value in sorted(_CANONICAL_PRODUCTS.items())
        ],
    }
    return hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


CATALOGUE_FINGERPRINT: Final[str] = _catalogue_fingerprint()


def recognized_branding_vas_identities(
    features: Iterable[str],
) -> tuple[TenantBrandingVASCommercialProduct, ...]:
    """Return exact recognized identities from canonical plan features.

    Unrelated plan features are harmless. Multiple recognized identities are
    returned in canonical feature order and must be rejected by eligibility.
    No display-name, plan-type, substring or browser value is consulted.
    """
    if isinstance(features, (str, bytes)):
        raise TenantBrandingVASCatalogueError("D21C1_FEATURES_INVALID")
    try:
        values = tuple(features)
    except TypeError as error:
        raise TenantBrandingVASCatalogueError("D21C1_FEATURES_INVALID") from error
    if any(not isinstance(item, str) or not item.strip() for item in values):
        raise TenantBrandingVASCatalogueError("D21C1_FEATURES_INVALID")
    return tuple(
        TenantBrandingVASCommercialProduct(
            commercial_id=item,
            branding_tier=cast(TenantBrandingTier, _CANONICAL_PRODUCTS[item]),
        )
        for item in values
        if item in _CANONICAL_PRODUCTS
    )


def resolve_branding_vas_identity(
    features: Iterable[str],
) -> TenantBrandingVASCommercialProduct | None:
    """Resolve exactly one paid Branding VAS identity or fail closed.

    ``None`` means the subscription has no paid Branding VAS identity; it does
    not mean Starter was commercially purchased.
    """
    identities = recognized_branding_vas_identities(features)
    if len(identities) > 1:
        raise TenantBrandingVASCatalogueError(
            "D21C1_MULTIPLE_BRANDING_IDENTITIES"
        )
    return identities[0] if identities else None


def branding_vas_product(
    commercial_id: str,
) -> TenantBrandingVASCommercialProduct:
    """Return one exact immutable paid Branding VAS product."""
    try:
        tier = _CANONICAL_PRODUCTS[commercial_id]
    except (KeyError, TypeError) as error:
        raise TenantBrandingVASCatalogueError(
            "D21C1_UNKNOWN_COMMERCIAL_IDENTITY"
        ) from error
    return TenantBrandingVASCommercialProduct(commercial_id, tier)


__all__ = [
    "BRANDING_VAS_ENTERPRISE_ID",
    "BRANDING_VAS_INSTITUTIONAL_ID",
    "BRANDING_VAS_PROFESSIONAL_ID",
    "CATALOGUE_FINGERPRINT",
    "CATALOGUE_IDENTITY",
    "CATALOGUE_SCHEMA",
    "TenantBrandingVASCatalogueError",
    "TenantBrandingVASCommercialProduct",
    "TenantBrandingVASCommercialTier",
    "VERSION",
    "branding_vas_product",
    "recognized_branding_vas_identities",
    "resolve_branding_vas_identity",
]

# ARTIFACT: tenant_branding_vas_catalogue.py
# VERSION: v1.0.0-D21C1-TENANT-BRANDING-VAS-CATALOGUE
# AUTHORITY BOUNDARY: exact commercial identity mapping only; no entitlement, IAM or browser authority
# TENANT POSTURE: global catalogue facts; tenant scope comes from SubscriptionEntity
# FAIL-CLOSED POSTURE: unknown/conflicting identities reject; unrelated features remain non-branding
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
