"""WILSY OS canonical product-to-commercial-feature mapping.

TITLE: Product Commercial Feature Mapping Domain
VERSION: v1.0.0-D22B3-PRODUCT-COMMERCIAL-FEATURE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Bind selected D22A tenant-product identities to exact commercial
         subscription feature identities without deciding tenant ownership.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/entitlement/product_commercial_feature.py
COLLABORATION / OWNERSHIP: D22A owns product identity and catalogue integrity;
                            this artifact owns static product-to-feature metadata.
                            SubscriptionRegistry remains subscription authority;
                            D22B1 owns lifecycle and D22B2 owns persistence.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B3-PRODUCT-COMMERCIAL-FEATURE establishes exact Legal
           Operations <-> legal.core and CRM <-> crm.core mappings, explicit
           Billing/HR unmapped failures, catalogue binding and SHA3-512 seals.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Pure immutable global metadata; no tenant, principal,
                             credential, network, filesystem or persistence data.
TENANT BOUNDARY: No tenant identity is accepted, inferred, read or mutated. A
                 mapping never proves that any tenant owns a product.
AUTHORITY BOUNDARY: Static TenantProductId-to-feature identity metadata only;
                    no subscription decision, entitlement issuance/lifecycle,
                    IAM, route, workspace, classification or VAS authority.
FINANCIAL AUTHORITY BOUNDARY: No price, invoice, payment, execution or settlement
                               truth. Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Unknown products, unmapped products, feature drift,
                         duplicate identities, catalogue drift and seal drift
                         reject deterministically without aliases or fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
from typing import Final, cast

from tools.eos.saas.entitlement.product_catalogue import (
    TenantProductCatalogueError,
    TenantProductId,
    get_tenant_product,
)


VERSION: Final[str] = "v1.0.0-D22B3-PRODUCT-COMMERCIAL-FEATURE"
SCHEMA: Final[str] = "WILSY-PRODUCT-COMMERCIAL-FEATURE/V1"
LEGAL_OPERATIONS_COMMERCIAL_FEATURE_ID: Final[str] = "legal.core"
CRM_COMMERCIAL_FEATURE_ID: Final[str] = "crm.core"


class ProductCommercialFeatureMappingError(ValueError):
    """Fail-closed mapping error with a deterministic institutional code."""

    def __init__(self, code: str) -> None:
        """Create one pure-domain failure without tenant or commercial inference."""
        self.code = code
        super().__init__(code)


_FEATURE_BY_PRODUCT: Final[dict[TenantProductId, str]] = {
    TenantProductId.LEGAL_OPERATIONS: LEGAL_OPERATIONS_COMMERCIAL_FEATURE_ID,
    TenantProductId.CRM: CRM_COMMERCIAL_FEATURE_ID,
}


def _digest(payload: dict[str, str]) -> str:
    """Return deterministic SHA3-512 over the exact mapping payload."""
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _mapping_payload(
    product_id: TenantProductId,
    feature_id: str,
    product_catalogue_fingerprint: str,
) -> dict[str, str]:
    """Build the complete canonical payload covered by local integrity."""
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "product_id": product_id.value,
        "feature_id": feature_id,
        "product_catalogue_fingerprint": product_catalogue_fingerprint,
    }


@dataclass(frozen=True, slots=True)
class ProductCommercialFeatureDescriptor:
    """Immutable static mapping bound to exact current D22A catalogue truth.

    The descriptor has no tenant, subscription, entitlement, IAM, route or
    financial mutation semantics. Its presence proves metadata correspondence
    only, never purchase or product access.
    """

    product_id: TenantProductId | str
    feature_id: str
    product_catalogue_fingerprint: str
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate canonical values and derive deterministic mapping integrity."""
        try:
            product_id = TenantProductId(self.product_id)
        except (TypeError, ValueError) as error:
            raise ProductCommercialFeatureMappingError(
                "PRODUCT_COMMERCIAL_FEATURE_UNKNOWN_PRODUCT"
            ) from error

        canonical_feature = _FEATURE_BY_PRODUCT.get(product_id)
        if canonical_feature is None:
            raise ProductCommercialFeatureMappingError(
                "PRODUCT_COMMERCIAL_FEATURE_UNMAPPED"
            )
        if (
            not isinstance(self.feature_id, str)
            or not self.feature_id
            or self.feature_id != canonical_feature
        ):
            raise ProductCommercialFeatureMappingError(
                "PRODUCT_COMMERCIAL_FEATURE_ID_INVALID"
            )

        catalogue = get_tenant_product(product_id)
        if (
            not isinstance(self.product_catalogue_fingerprint, str)
            or not hmac.compare_digest(
                self.product_catalogue_fingerprint,
                catalogue.fingerprint,
            )
        ):
            raise ProductCommercialFeatureMappingError(
                "PRODUCT_COMMERCIAL_FEATURE_CATALOGUE_BINDING_INVALID"
            )

        digest = _digest(
            _mapping_payload(
                product_id,
                self.feature_id,
                self.product_catalogue_fingerprint,
            )
        )
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            raise ProductCommercialFeatureMappingError(
                "PRODUCT_COMMERCIAL_FEATURE_FINGERPRINT_MISMATCH"
            )
        object.__setattr__(self, "product_id", product_id)
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, str]:
        """Return a detached exact mapping document with no authority expansion."""
        payload = _mapping_payload(
            cast(TenantProductId, self.product_id),
            self.feature_id,
            self.product_catalogue_fingerprint,
        )
        payload["fingerprint"] = self.fingerprint
        return payload


def _descriptor(product_id: TenantProductId, feature_id: str) -> ProductCommercialFeatureDescriptor:
    """Construct one mapping directly from canonical D22A evidence."""
    product = get_tenant_product(product_id)
    return ProductCommercialFeatureDescriptor(
        product_id=product.product_id,
        feature_id=feature_id,
        product_catalogue_fingerprint=product.fingerprint,
    )


if len(_FEATURE_BY_PRODUCT) != len(set(_FEATURE_BY_PRODUCT)):
    raise ProductCommercialFeatureMappingError(
        "PRODUCT_COMMERCIAL_FEATURE_DUPLICATE_PRODUCT"
    )
if len(_FEATURE_BY_PRODUCT.values()) != len(set(_FEATURE_BY_PRODUCT.values())):
    raise ProductCommercialFeatureMappingError(
        "PRODUCT_COMMERCIAL_FEATURE_DUPLICATE_FEATURE"
    )

_MAPPINGS: Final[dict[TenantProductId, ProductCommercialFeatureDescriptor]] = {
    product_id: _descriptor(product_id, feature_id)
    for product_id, feature_id in _FEATURE_BY_PRODUCT.items()
}


def get_product_commercial_feature(
    product_id: TenantProductId | str,
) -> ProductCommercialFeatureDescriptor:
    """Return exact static feature metadata for one mapped D22A product.

    Known but unmapped products reject distinctly from unknown product input.
    Returning a descriptor does not establish subscription or entitlement truth.
    """
    try:
        normalized = TenantProductId(product_id)
    except (TypeError, ValueError) as error:
        raise ProductCommercialFeatureMappingError(
            "PRODUCT_COMMERCIAL_FEATURE_UNKNOWN_PRODUCT"
        ) from error
    try:
        get_tenant_product(normalized)
    except TenantProductCatalogueError as error:
        raise ProductCommercialFeatureMappingError(
            "PRODUCT_COMMERCIAL_FEATURE_UNKNOWN_PRODUCT"
        ) from error
    descriptor = _MAPPINGS.get(normalized)
    if descriptor is None:
        raise ProductCommercialFeatureMappingError(
            "PRODUCT_COMMERCIAL_FEATURE_UNMAPPED"
        )
    return descriptor


def list_product_commercial_features() -> tuple[ProductCommercialFeatureDescriptor, ...]:
    """Return mapped descriptors in deterministic D22A product order."""
    return tuple(
        _MAPPINGS[product_id]
        for product_id in TenantProductId
        if product_id in _MAPPINGS
    )


__all__ = [
    "CRM_COMMERCIAL_FEATURE_ID",
    "LEGAL_OPERATIONS_COMMERCIAL_FEATURE_ID",
    "ProductCommercialFeatureDescriptor",
    "ProductCommercialFeatureMappingError",
    "SCHEMA",
    "VERSION",
    "get_product_commercial_feature",
    "list_product_commercial_features",
]

# ARTIFACT: product_commercial_feature.py
# VERSION: v1.0.0-D22B3-PRODUCT-COMMERCIAL-FEATURE
# AUTHORITY BOUNDARY: static D22A product-to-commercial-feature metadata only; no subscription, entitlement, IAM, route or classification authority
# TENANT POSTURE: global mapping facts only; no tenant identity is accepted, inferred or mutated
# FAIL-CLOSED POSTURE: unknown/unmapped products, feature drift, duplicate identities, catalogue drift and fingerprint drift reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
