"""Fail-closed readiness projection for explicit commercial product bundles.

This is a read-only gate. It never issues entitlements or activates an offer.
A bundle is eligible for bundle activation planning only when every product
has an exact canonical commercial-feature mapping. Missing product authority is
reported explicitly; no feature identifier is inferred from a product label.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from tools.eos.saas.entitlement.commercial_offer_catalogue import (
    CommercialOfferDescriptor,
    CommercialOfferId,
    get_commercial_offer,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.product_commercial_feature import (
    ProductCommercialFeatureMappingError,
    ProductCommercialFeatureDescriptor,
    get_product_commercial_feature,
)

VERSION: Final[str] = "v1.0.0-EOS-COMMERCIAL-BUNDLE-READINESS"


class CommercialBundleReadinessError(RuntimeError):
    """Invalid offer or inconsistent canonical product authority."""


class CommercialBundleReadinessState(StrEnum):
    PRODUCT_MAPPING_COMPLETE = "PRODUCT_MAPPING_COMPLETE"
    BLOCKED_MISSING_PRODUCT_MAPPING = "BLOCKED_MISSING_PRODUCT_MAPPING"


@dataclass(frozen=True, slots=True)
class CommercialBundleProductReadiness:
    product_id: TenantProductId
    ready: bool
    mapping: ProductCommercialFeatureDescriptor | None
    blocker_code: str | None


@dataclass(frozen=True, slots=True)
class CommercialBundleReadiness:
    offer: CommercialOfferDescriptor
    state: CommercialBundleReadinessState
    products: tuple[CommercialBundleProductReadiness, ...]

    @property
    def ready(self) -> bool:
        return self.state is CommercialBundleReadinessState.PRODUCT_MAPPING_COMPLETE

    @property
    def blockers(self) -> tuple[str, ...]:
        return tuple(
            f"{item.product_id.value}:{item.blocker_code}"
            for item in self.products
            if not item.ready
        )


def assess_commercial_bundle_readiness(
    offer_id: CommercialOfferId | str,
) -> CommercialBundleReadiness:
    """Resolve every exact offer product; never infer or partially authorize.

    The returned PRODUCT_MAPPING_COMPLETE means only that mapping metadata exists for every
    offer product. It does not prove purchase, execution, subscription
    eligibility, entitlement currentness, IAM permission or workspace access.
    """
    try:
        offer = get_commercial_offer(offer_id)
    except (TypeError, ValueError) as error:
        raise CommercialBundleReadinessError(
            "COMMERCIAL_BUNDLE_OFFER_UNKNOWN"
        ) from error

    products: list[CommercialBundleProductReadiness] = []
    for product_id in offer.product_ids:
        try:
            mapping = get_product_commercial_feature(product_id)
        except ProductCommercialFeatureMappingError as error:
            if error.code == "PRODUCT_COMMERCIAL_FEATURE_UNMAPPED":
                products.append(
                    CommercialBundleProductReadiness(
                        product_id=product_id,
                        ready=False,
                        mapping=None,
                        blocker_code=error.code,
                    )
                )
                continue
            raise CommercialBundleReadinessError(
                "COMMERCIAL_BUNDLE_PRODUCT_MAPPING_INVALID"
            ) from error
        products.append(
            CommercialBundleProductReadiness(
                product_id=product_id,
                ready=True,
                mapping=mapping,
                blocker_code=None,
            )
        )

    state = (
        CommercialBundleReadinessState.READY_FOR_ATOMIC_ACTIVATION
        if all(item.ready for item in products)
        else CommercialBundleReadinessState.BLOCKED_MISSING_PRODUCT_MAPPING
    )
    return CommercialBundleReadiness(
        offer=offer,
        state=state,
        products=tuple(products),
    )


__all__ = [
    "VERSION",
    "CommercialBundleProductReadiness",
    "CommercialBundleReadiness",
    "CommercialBundleReadinessError",
    "CommercialBundleReadinessState",
    "assess_commercial_bundle_readiness",
]
