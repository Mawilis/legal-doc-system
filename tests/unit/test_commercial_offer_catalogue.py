"""Direct certificate for the explicit commercial-offer catalogue.

The offer catalogue must describe standalone products and explicit bundles
without creating tenant purchases, entitlements, subscriptions, IAM or pricing.
"""
from dataclasses import FrozenInstanceError, replace
import re

import pytest

from tools.eos.saas.entitlement.commercial_offer_catalogue import (
    CommercialModel,
    CommercialOfferCatalogueError,
    CommercialOfferId,
    CommercialOfferKind,
    get_commercial_offer,
    hydrate_commercial_offer,
    list_commercial_offers,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId


def test_catalogue_contains_four_standalone_offers_and_three_explicit_bundles() -> None:
    offers = list_commercial_offers()
    assert len(offers) == 7
    assert sum(item.kind is CommercialOfferKind.STANDALONE for item in offers) == 4
    assert sum(item.kind is CommercialOfferKind.BUNDLE for item in offers) == 3

    standalone = {
        item.product_ids[0]
        for item in offers
        if item.kind is CommercialOfferKind.STANDALONE
    }
    assert standalone == set(TenantProductId)


def test_bundle_composition_is_explicit_and_uses_only_catalogued_products() -> None:
    expected = {
        CommercialOfferId.PROFESSIONAL_SERVICES: (
            TenantProductId.LEGAL_OPERATIONS,
            TenantProductId.CRM,
            TenantProductId.BILLING,
        ),
        CommercialOfferId.BUSINESS_OPERATIONS: (
            TenantProductId.CRM,
            TenantProductId.HR,
            TenantProductId.BILLING,
        ),
        CommercialOfferId.ENTERPRISE_OPERATIONS: (
            TenantProductId.LEGAL_OPERATIONS,
            TenantProductId.BILLING,
            TenantProductId.CRM,
            TenantProductId.HR,
        ),
    }
    for offer_id, product_ids in expected.items():
        offer = get_commercial_offer(offer_id)
        assert offer.kind is CommercialOfferKind.BUNDLE
        assert offer.product_ids == product_ids
        assert len(offer.product_ids) == len(set(offer.product_ids))


def test_offer_composition_does_not_create_wildcard_product() -> None:
    assert "ENTERPRISE_OPERATIONS_BUNDLE" not in {
        item.value for item in TenantProductId
    }
    assert all("*" not in item.to_dict()["product_ids"] for item in list_commercial_offers())


def test_every_offer_models_all_supported_packaging_shapes_as_metadata() -> None:
    expected = set(CommercialModel)
    for offer in list_commercial_offers():
        assert set(offer.commercial_models) == expected


def test_offer_descriptors_are_immutable_and_deterministically_sealed() -> None:
    offer = get_commercial_offer(CommercialOfferId.PROFESSIONAL_SERVICES)
    with pytest.raises((FrozenInstanceError, AttributeError)):
        offer.label = "Changed"  # type: ignore[misc]
    assert re.fullmatch(r"[0-9a-f]{128}", offer.fingerprint)


def test_every_offer_round_trips_through_strict_hydration() -> None:
    for offer in list_commercial_offers():
        assert hydrate_commercial_offer(offer.to_dict()) == offer


def test_unknown_offer_and_product_reject() -> None:
    with pytest.raises(CommercialOfferCatalogueError, match="OFFER_UNKNOWN"):
        get_commercial_offer("ALL_PRODUCTS")
    with pytest.raises(CommercialOfferCatalogueError, match="OFFER_PRODUCTS_INVALID"):
        replace(
            get_commercial_offer(CommercialOfferId.CRM),
            product_ids=("NOT_A_PRODUCT",),
            fingerprint="",
        )


def test_bundle_cannot_be_relabelled_as_standalone_or_redefined() -> None:
    offer = get_commercial_offer(CommercialOfferId.ENTERPRISE_OPERATIONS)
    with pytest.raises(
        CommercialOfferCatalogueError,
        match="OFFER_STANDALONE_CARDINALITY_INVALID",
    ):
        replace(offer, kind=CommercialOfferKind.STANDALONE, fingerprint="")

    with pytest.raises(
        CommercialOfferCatalogueError,
        match="OFFER_CALLER_VALUE_OVERRIDE",
    ):
        replace(offer, product_ids=(TenantProductId.CRM, TenantProductId.HR), fingerprint="")


def test_corrupt_or_non_exact_payloads_fail_closed() -> None:
    payload = get_commercial_offer(CommercialOfferId.BILLING).to_dict()
    with pytest.raises(
        CommercialOfferCatalogueError,
        match="OFFER_DESCRIPTOR_SCHEMA_INVALID",
    ):
        hydrate_commercial_offer({**payload, "tenant_id": "tenant-a"})

    corrupt = dict(payload)
    corrupt["fingerprint"] = "f" * 128
    with pytest.raises(
        CommercialOfferCatalogueError,
        match="OFFER_FINGERPRINT_MISMATCH",
    ):
        hydrate_commercial_offer(corrupt)


def test_offer_metadata_contains_no_purchase_or_authorization_state() -> None:
    forbidden = {
        "tenant_id",
        "principal_id",
        "subscription_id",
        "entitlement_id",
        "plan_id",
        "price",
        "amount",
        "currency",
        "purchased",
        "active",
        "enabled",
        "permission",
        "role",
        "payment",
        "invoice",
        "settlement",
        "execution",
    }
    for offer in list_commercial_offers():
        assert forbidden.isdisjoint(offer.to_dict())


def test_offer_does_not_inherit_product_activation_authority() -> None:
    # Catalogue composition is deliberately separate from D22B entitlement
    # issuance. In particular, bundles cannot be passed as TenantProductIds.
    for offer in list_commercial_offers():
        assert offer.offer_id not in {item.value for item in TenantProductId}
