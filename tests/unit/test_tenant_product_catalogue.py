"""Direct certificate for the D22A tenant product catalogue.

TITLE: Tenant Product Catalogue Direct Certificate
VERSION: v1.0.0-D22A-TENANT-PRODUCT-CATALOGUE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exact product identities, VAS separation, deterministic
         descriptor integrity and absence of entitlement/IAM/financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_product_catalogue.py
COLLABORATION / OWNERSHIP: Evidence-only direct certificate for the D22A
                            product catalogue owner.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG: v1.0.0-D22A-TENANT-PRODUCT-CATALOGUE-CERT establishes direct
           evidence for Legal Operations, Billing, CRM and HR product identity
           while excluding WILSY AI, Tenant Branding and Full Enterprise
           wildcard semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic global catalogue facts only.
TENANT BOUNDARY: No tenant entitlement or tenant identity is created.
AUTHORITY BOUNDARY: Product catalogue certificate only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import re

import pytest

from tools.eos.saas.entitlement.product_catalogue import (
    TenantProductCatalogueError,
    TenantProductId,
    get_tenant_product,
    hydrate_tenant_product,
    list_tenant_products,
)


def test_exact_closed_product_catalogue() -> None:
    products = list_tenant_products()
    assert [item.product_id for item in products] == [
        "LEGAL_OPERATIONS",
        "BILLING",
        "CRM",
        "HR",
    ]
    assert len(products) == len(TenantProductId) == 4


def test_legal_operations_descriptor_is_exact_and_non_financial() -> None:
    value = get_tenant_product(TenantProductId.LEGAL_OPERATIONS)
    assert value.label == "Legal Operations"
    assert value.workspace_key == "LEGAL_DASHBOARD"
    assert value.required_products == ()
    assert "legal" in value.description.lower()
    assert "financial execution" not in value.description.lower()


def test_billing_descriptor_preserves_financial_execution_boundary() -> None:
    value = get_tenant_product(TenantProductId.BILLING)
    assert value.workspace_key == "BILLING_HUB"
    assert "no financial execution authority" in value.description.lower()


def test_crm_and_hr_workspace_keys_are_exact() -> None:
    assert get_tenant_product(TenantProductId.CRM).workspace_key == "CRM_DASHBOARD"
    assert get_tenant_product(TenantProductId.HR).workspace_key == "HR_DASHBOARD"


def test_vas_and_bundle_tokens_are_not_products() -> None:
    for token in (
        "WILSY_AI",
        "WILSY_AI_REASONING",
        "TENANT_BRANDING",
        "TENANT_BRANDING_PROFESSIONAL",
        "FULL_ENTERPRISE",
        "ENTERPRISE",
        "*",
    ):
        with pytest.raises(
            TenantProductCatalogueError,
            match="D22A_UNKNOWN_PRODUCT",
        ):
            get_tenant_product(token)


def test_descriptors_are_immutable_and_sha3_512_sealed() -> None:
    value = get_tenant_product(TenantProductId.LEGAL_OPERATIONS)
    with pytest.raises((FrozenInstanceError, AttributeError)):
        value.label = "Changed"  # type: ignore[misc]
    assert re.fullmatch(r"[0-9a-f]{128}", value.fingerprint)


def test_every_descriptor_round_trips_strictly() -> None:
    for value in list_tenant_products():
        assert hydrate_tenant_product(value.to_dict()) == value


def test_unknown_extra_missing_and_corrupt_payloads_fail_closed() -> None:
    payload = get_tenant_product(TenantProductId.CRM).to_dict()

    with pytest.raises(
        TenantProductCatalogueError,
        match="D22A_DESCRIPTOR_SCHEMA_INVALID",
    ):
        hydrate_tenant_product({**payload, "extra": "x"})

    missing = dict(payload)
    missing.pop("label")
    with pytest.raises(
        TenantProductCatalogueError,
        match="D22A_DESCRIPTOR_SCHEMA_INVALID",
    ):
        hydrate_tenant_product(missing)

    corrupt = dict(payload)
    corrupt["fingerprint"] = "f" * 128
    with pytest.raises(
        TenantProductCatalogueError,
        match="D22A_FINGERPRINT_MISMATCH",
    ):
        hydrate_tenant_product(corrupt)


def test_caller_cannot_override_workspace_identity_or_dependencies() -> None:
    legal = get_tenant_product(TenantProductId.LEGAL_OPERATIONS)

    with pytest.raises(
        TenantProductCatalogueError,
        match="D22A_CALLER_VALUE_OVERRIDE",
    ):
        replace(
            legal,
            workspace_key="BILLING_HUB",
            fingerprint="",
        )

    with pytest.raises(
        TenantProductCatalogueError,
        match="D22A_CALLER_VALUE_OVERRIDE",
    ):
        replace(
            legal,
            required_products=(TenantProductId.BILLING,),
            fingerprint="",
        )


def test_descriptor_contains_no_tenant_entitlement_iam_or_commercial_truth() -> None:
    forbidden = {
        "tenant_id",
        "entitlement_id",
        "subscription_id",
        "plan_id",
        "plan",
        "price",
        "amount",
        "currency",
        "principal_id",
        "role",
        "permission",
        "active",
        "enabled",
        "purchased",
        "payment",
        "execution",
        "settlement",
    }
    for value in list_tenant_products():
        assert forbidden.isdisjoint(value.to_dict())


def test_catalogue_has_no_product_dependencies_until_explicitly_certified() -> None:
    assert all(
        item.required_products == ()
        for item in list_tenant_products()
    )


def test_full_enterprise_must_be_future_explicit_composition_not_wildcard() -> None:
    identifiers = {item.product_id for item in list_tenant_products()}
    assert "FULL_ENTERPRISE" not in identifiers
    assert "ALL" not in identifiers
    assert "*" not in identifiers


# ARTIFACT: test_tenant_product_catalogue.py
# VERSION: v1.0.0-D22A-TENANT-PRODUCT-CATALOGUE-CERT
# AUTHORITY BOUNDARY: direct product-catalogue evidence only
# TENANT POSTURE: synthetic global catalogue facts only
# FAIL-CLOSED POSTURE: unknown products, descriptor drift and VAS leakage reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
