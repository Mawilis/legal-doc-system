"""Direct certificate for the D22B3 product commercial feature mapping.

TITLE: Product Commercial Feature Mapping Direct Certificate
VERSION: v1.0.0-D22B3-PRODUCT-COMMERCIAL-FEATURE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exact immutable product/feature mappings, D22A catalogue binding,
         deterministic integrity, uniqueness and absence of runtime authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_product_commercial_feature.py
COLLABORATION / OWNERSHIP: Direct pure-domain certificate for D22B3 metadata;
                            D22A remains product authority and later composition
                            must obtain authoritative subscription truth.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B3-PRODUCT-COMMERCIAL-FEATURE-CERT establishes adversarial
           evidence for exact Legal/CRM mappings, unmapped/unknown failures,
           immutability, uniqueness, catalogue binding and authority absence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Pure synthetic assertions; no tenant or credentials.
TENANT BOUNDARY: No tenant identity or tenant commercial decision is exercised.
AUTHORITY BOUNDARY: Mapping-domain certification only; no subscription,
                    entitlement, IAM, route, classification or VAS authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
import hashlib
import inspect
import json

import pytest

from tools.eos.saas.entitlement import product_commercial_feature as mapping
from tools.eos.saas.entitlement.product_catalogue import (
    TenantProductId,
    get_tenant_product,
)


def test_exact_legal_and_crm_mappings_bind_d22a() -> None:
    """Legal and CRM map exactly and carry their current D22A fingerprints."""
    legal = mapping.get_product_commercial_feature(TenantProductId.LEGAL_OPERATIONS)
    crm = mapping.get_product_commercial_feature(TenantProductId.CRM)
    assert legal.feature_id == "legal.core"
    assert crm.feature_id == "crm.core"
    assert legal.product_catalogue_fingerprint == get_tenant_product(
        TenantProductId.LEGAL_OPERATIONS
    ).fingerprint
    assert crm.product_catalogue_fingerprint == get_tenant_product(
        TenantProductId.CRM
    ).fingerprint


@pytest.mark.parametrize("product_id", [TenantProductId.BILLING, TenantProductId.HR])
def test_known_unmapped_products_fail_closed(product_id: TenantProductId) -> None:
    """Billing and HR remain explicitly unmapped without invented identities."""
    with pytest.raises(mapping.ProductCommercialFeatureMappingError) as raised:
        mapping.get_product_commercial_feature(product_id)
    assert raised.value.code == "PRODUCT_COMMERCIAL_FEATURE_UNMAPPED"


def test_unknown_product_fails_distinctly() -> None:
    """Unknown input cannot collapse into the known-but-unmapped state."""
    with pytest.raises(mapping.ProductCommercialFeatureMappingError) as raised:
        mapping.get_product_commercial_feature("UNKNOWN_PRODUCT")
    assert raised.value.code == "PRODUCT_COMMERCIAL_FEATURE_UNKNOWN_PRODUCT"


@pytest.mark.parametrize(
    "feature_id",
    [
        "LEGAL.CORE",
        "legal.core ",
        " legal.core",
        "legal.operations",
        "LEGAL_OPERATIONS",
        "legal.evidence.capacity.STARTER",
        "legal.evidence.capacity.GROWTH",
        "legal.evidence.capacity.INSTITUTIONAL",
    ],
)
def test_legal_feature_is_exact_without_aliases(feature_id: str) -> None:
    """Case, whitespace, operational identity and capacity aliases all reject."""
    product = get_tenant_product(TenantProductId.LEGAL_OPERATIONS)
    with pytest.raises(mapping.ProductCommercialFeatureMappingError) as raised:
        mapping.ProductCommercialFeatureDescriptor(
            product_id=product.product_id,
            feature_id=feature_id,
            product_catalogue_fingerprint=product.fingerprint,
        )
    assert raised.value.code == "PRODUCT_COMMERCIAL_FEATURE_ID_INVALID"


def test_product_identity_is_distinct_from_commercial_feature_identity() -> None:
    """D22A enum identities are never treated as subscription feature strings."""
    crm = mapping.get_product_commercial_feature(TenantProductId.CRM)
    assert isinstance(crm.product_id, TenantProductId)
    assert crm.product_id.value == "CRM"
    assert crm.feature_id == "crm.core"
    assert crm.product_id.value != crm.feature_id


def test_mapping_fingerprint_is_deterministic_and_covers_catalogue_binding() -> None:
    """The exact D22A fingerprint participates in deterministic SHA3-512."""
    item = mapping.get_product_commercial_feature(TenantProductId.LEGAL_OPERATIONS)
    payload = item.to_dict()
    fingerprint = payload.pop("fingerprint")
    expected = hashlib.sha3_512(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    assert fingerprint == expected == item.fingerprint
    changed = dict(payload)
    changed["product_catalogue_fingerprint"] = "f" * 128
    assert hashlib.sha3_512(
        json.dumps(changed, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest() != item.fingerprint


def test_catalogue_drift_and_stored_fingerprint_drift_reject() -> None:
    """Neither catalogue binding nor the local seal can silently drift."""
    product = get_tenant_product(TenantProductId.CRM)
    with pytest.raises(mapping.ProductCommercialFeatureMappingError) as catalogue:
        mapping.ProductCommercialFeatureDescriptor(
            product_id=product.product_id,
            feature_id="crm.core",
            product_catalogue_fingerprint="f" * 128,
        )
    assert catalogue.value.code == "PRODUCT_COMMERCIAL_FEATURE_CATALOGUE_BINDING_INVALID"
    with pytest.raises(mapping.ProductCommercialFeatureMappingError) as seal:
        mapping.ProductCommercialFeatureDescriptor(
            product_id=product.product_id,
            feature_id="crm.core",
            product_catalogue_fingerprint=product.fingerprint,
            fingerprint="f" * 128,
        )
    assert seal.value.code == "PRODUCT_COMMERCIAL_FEATURE_FINGERPRINT_MISMATCH"


def test_mapping_is_immutable_and_listing_is_exact_deterministic_unique() -> None:
    """Listing exposes only Legal then CRM with bijective identities."""
    first = mapping.list_product_commercial_features()
    second = mapping.list_product_commercial_features()
    assert first == second
    assert tuple(item.product_id for item in first) == (
        TenantProductId.LEGAL_OPERATIONS,
        TenantProductId.CRM,
    )
    assert tuple(item.feature_id for item in first) == ("legal.core", "crm.core")
    assert len({item.product_id for item in first}) == len(first)
    assert len({item.feature_id for item in first}) == len(first)
    with pytest.raises(FrozenInstanceError):
        first[0].feature_id = "legal.operations"  # type: ignore[misc]


def test_source_has_no_runtime_authority_dependencies_or_mutation_surface() -> None:
    """Freeze the pure seam against persistence, tenant and transport expansion."""
    source = inspect.getsource(mapping)
    tree = ast.parse(source)
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    forbidden_import_fragments = (
        "subscription",
        "plan_registry",
        "tenant_product_entitlement",
        "business_classification",
        "iam",
        "router",
        "fastapi",
        "pymongo",
    )
    assert all(
        fragment not in module.casefold()
        for module in imported_modules
        for fragment in forbidden_import_fragments
    )
    assert "tenant_id" not in {
        node.arg for node in ast.walk(tree) if isinstance(node, ast.arg)
    }
    public = set(mapping.__all__)
    assert not public.intersection(
        {"create", "issue", "activate", "persist", "authorize", "execute"}
    )


# ARTIFACT: test_product_commercial_feature.py
# VERSION: v1.0.0-D22B3-PRODUCT-COMMERCIAL-FEATURE-CERT
# AUTHORITY BOUNDARY: direct pure mapping evidence only; no subscription, entitlement, IAM, route or classification authority
# TENANT POSTURE: no tenant identity or tenant commercial decision
# FAIL-CLOSED POSTURE: exact mappings, catalogue binding, uniqueness and authority absence are mandatory
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
