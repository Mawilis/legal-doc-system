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
    ("offer_id", "expected_products"),
    [
        (CommercialOfferId.PROFESSIONAL_SERVICES, ("LEGAL_OPERATIONS", "CRM", "BILLING")),
        (CommercialOfferId.BUSINESS_OPERATIONS, ("CRM", "HR", "BILLING")),
        (CommercialOfferId.ENTERPRISE_OPERATIONS, ("LEGAL_OPERATIONS", "BILLING", "CRM", "HR")),
    ],
)
def test_every_catalogued_bundle_has_exact_mapping_for_each_product(
    offer_id: CommercialOfferId, expected_products: tuple[str, ...],
) -> None:
    """All bundle products map explicitly; this does not prove entitlement or access."""
    result = assess_commercial_bundle_readiness(offer_id)
    assert tuple(item.product_id.value for item in result.products) == expected_products
    assert result.state is CommercialBundleReadinessState.PRODUCT_MAPPING_COMPLETE
    assert result.ready is True
    assert result.blockers == ()
    assert all(item.mapping is not None for item in result.products)


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
    assert result.state is CommercialBundleReadinessState.PRODUCT_MAPPING_COMPLETE
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
    assert "issue_tenant_product_entitlement" not in source
    assert "transition(" not in source
    assert "session" not in source.casefold()
