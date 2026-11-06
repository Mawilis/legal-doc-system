from __future__ import annotations

import pytest

from tools.eos.saas.entitlement.commercial_bundle_readiness import (
    CommercialBundleReadinessError,
    CommercialBundleReadinessState,
    assess_commercial_bundle_readiness,
)
from tools.eos.saas.entitlement.commercial_offer_catalogue import CommercialOfferId
from tools.eos.saas.entitlement.product_catalogue import TenantProductId


@pytest.mark.parametrize(
    ("offer_id", "expected_products", "blocked_products"),
    [
        (
            CommercialOfferId.PROFESSIONAL_SERVICES,
            ("LEGAL_OPERATIONS", "CRM", "BILLING"),
            ("BILLING",),
        ),
        (
            CommercialOfferId.BUSINESS_OPERATIONS,
            ("CRM", "HR", "BILLING"),
            ("HR", "BILLING"),
        ),
        (
            CommercialOfferId.ENTERPRISE_OPERATIONS,
            ("LEGAL_OPERATIONS", "BILLING", "CRM", "HR"),
            ("BILLING", "HR"),
        ),
    ],
)
def test_every_catalogued_bundle_fails_closed_until_all_product_authorities_exist(
    offer_id: CommercialOfferId,
    expected_products: tuple[str, ...],
    blocked_products: tuple[str, ...],
) -> None:
    """A single unmapped product blocks the entire explicit offer composition."""
    result = assess_commercial_bundle_readiness(offer_id)
    assert tuple(item.product_id.value for item in result.products) == expected_products
    assert result.state is CommercialBundleReadinessState.BLOCKED_MISSING_PRODUCT_AUTHORITY
    assert result.ready is False
    assert tuple(item.product_id.value for item in result.products if not item.ready) == blocked_products
    assert all(item.mapping is None for item in result.products if not item.ready)


@pytest.mark.parametrize(
    ("offer_id", "product_id"),
    [
        (CommercialOfferId.LEGAL_OPERATIONS, TenantProductId.LEGAL_OPERATIONS),
        (CommercialOfferId.CRM, TenantProductId.CRM),
    ],
)
def test_standalone_offer_is_ready_only_at_mapping_metadata_layer(
    offer_id: CommercialOfferId,
    product_id: TenantProductId,
) -> None:
    """Known Legal/CRM mappings are present without claiming entitlement."""
    result = assess_commercial_bundle_readiness(offer_id)
    assert result.state is CommercialBundleReadinessState.READY_FOR_ATOMIC_ACTIVATION
    assert result.ready is True
    assert len(result.products) == 1
    assert result.products[0].product_id is product_id
    assert result.products[0].mapping is not None
    assert result.products[0].blocker_code is None


@pytest.mark.parametrize("offer_id", ["UNKNOWN", None, object()])
def test_unknown_offer_rejects_without_fallback(offer_id: object) -> None:
    with pytest.raises(CommercialBundleReadinessError) as raised:
        assess_commercial_bundle_readiness(offer_id)  # type: ignore[arg-type]
    assert raised.value.args == ("COMMERCIAL_BUNDLE_OFFER_UNKNOWN",)


def test_readiness_source_has_no_persistence_or_activation_authority() -> None:
    import inspect

    source = inspect.getsource(assess_commercial_bundle_readiness)
    assert "insert_one" not in source
    assert "update_one" not in source
    assert "activate" not in source.casefold()
    assert "session" not in source.casefold()
