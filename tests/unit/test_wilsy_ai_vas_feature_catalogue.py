"""Direct certificate for the canonical WILSY AI VAS feature catalogue.

TITLE: WILSY AI VAS Commercial Feature Catalogue Direct Certificate
VERSION: v1.0.0-D57A-WILSY-AI-VAS-FEATURE-CATALOGUE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exact closed feature identities, bijective tier correspondence,
         generic-feature rejection, canonical policy compatibility and absence
         of tenant, subscription, entitlement, IAM or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_vas_feature_catalogue.py
COLLABORATION / OWNERSHIP: Direct pure-domain evidence for the D57A catalogue;
                            existing M13-P3 policy remains the tier-value owner.
CERTIFICATION / UPDATE DATE: 2026-10-10
CHANGELOG: v1.0.0-D57A-WILSY-AI-VAS-FEATURE-CATALOGUE-CERT establishes direct
           adversarial certification of the three feature-to-tier mappings.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Pure global metadata assertions; no tenant data.
TENANT BOUNDARY: No tenant identity, subscription ownership or activation fact.
AUTHORITY BOUNDARY: Mapping certification only; no entitlement, IAM, capacity,
                    persistence, provider, billing, payment or execution power.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
from __future__ import annotations

import ast
import inspect
from types import MappingProxyType
from typing import Any, cast

import pytest

from tools.eos.saas.billing import wilsy_ai_vas_feature_catalogue as catalogue
from tools.eos.saas.billing.wilsy_ai_commercial_policy import (
    WilsyAITier,
    get_wilsy_ai_commercial_policy,
)


EXPECTED = {
    catalogue.WilsyAIVASFeatureId.STARTER: WilsyAITier.STARTER,
    catalogue.WilsyAIVASFeatureId.GROWTH: WilsyAITier.GROWTH,
    catalogue.WilsyAIVASFeatureId.INSTITUTIONAL: WilsyAITier.INSTITUTIONAL,
}


@pytest.mark.parametrize(("feature", "tier"), tuple(EXPECTED.items()))
def test_exact_feature_resolves_only_to_exact_tier(
    feature: catalogue.WilsyAIVASFeatureId,
    tier: WilsyAITier,
) -> None:
    """Each exact tier-specific feature resolves to its one canonical tier."""
    assert catalogue.resolve_wilsy_ai_tier_for_feature(feature) is tier
    assert catalogue.resolve_wilsy_ai_tier_for_feature(feature.value) is tier


def test_feature_set_is_closed_distinct_total_and_mapping_is_immutable() -> None:
    """The closed enum is distinct, completely mapped and externally immutable."""
    features = catalogue.list_wilsy_ai_vas_features()
    assert features == tuple(catalogue.WilsyAIVASFeatureId)
    assert set(features) == set(EXPECTED)
    assert len(features) == len({item.value for item in features}) == 3
    assert dict(catalogue.FEATURE_TO_TIER) == EXPECTED
    assert isinstance(catalogue.FEATURE_TO_TIER, MappingProxyType)
    with pytest.raises(TypeError):
        cast(Any, catalogue.FEATURE_TO_TIER)[catalogue.WilsyAIVASFeatureId.STARTER] = (
            WilsyAITier.GROWTH
        )


@pytest.mark.parametrize(
    "value",
    [
        "UNKNOWN",
        "",
        " ",
        " ai.wilsy.starter",
        "ai.wilsy.starter ",
        "AI.WILSY.STARTER",
        None,
        123,
    ],
)
def test_unknown_malformed_and_drifted_feature_fails_closed(value: object) -> None:
    """Unknown, blank, whitespace, case-drifted and non-string values reject."""
    with pytest.raises(catalogue.WilsyAIVASFeatureCatalogueError) as raised:
        catalogue.resolve_wilsy_ai_tier_for_feature(value)  # type: ignore[arg-type]
    assert raised.value.code == "D57A_UNKNOWN_WILSY_AI_VAS_FEATURE"


def test_generic_ai_feature_never_grants_a_tier() -> None:
    """The pre-existing generic availability token is not tier authority."""
    assert catalogue.GENERIC_WILSY_AI_FEATURE_ID == "ai.wilsy"
    assert catalogue.GENERIC_WILSY_AI_FEATURE_ID not in {
        item.value for item in catalogue.WilsyAIVASFeatureId
    }
    with pytest.raises(catalogue.WilsyAIVASFeatureCatalogueError):
        catalogue.resolve_wilsy_ai_tier_for_feature(
            catalogue.GENERIC_WILSY_AI_FEATURE_ID
        )


def test_mapped_tiers_reuse_exact_existing_policy_objects_and_facts() -> None:
    """D57A selects existing policies without altering prices or capacities."""
    expected_facts = {
        WilsyAITier.STARTER: (49_900, 35, 750, 1),
        WilsyAITier.GROWTH: (149_900, 120, 3_000, 3),
        WilsyAITier.INSTITUTIONAL: (549_900, 450, 12_000, 12),
    }
    for feature, expected_tier in EXPECTED.items():
        tier = catalogue.resolve_wilsy_ai_tier_for_feature(feature)
        policy = get_wilsy_ai_commercial_policy(tier)
        assert tier is expected_tier
        assert policy is get_wilsy_ai_commercial_policy(expected_tier)
        assert (
            policy.monthly_price_minor,
            policy.daily_request_limit,
            policy.monthly_automation_limit,
            policy.analyst_seats,
        ) == expected_facts[expected_tier]


def test_source_has_no_base_plan_inference_or_runtime_authority() -> None:
    """The catalogue imports policy tier identity only and has no mutation seam."""
    source = inspect.getsource(catalogue)
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
    forbidden_imports = (
        "subscription",
        "plan_registry",
        "entitlement_registry",
        "tenant_authorization",
        "iam",
        "fastapi",
        "pymongo",
    )
    assert all(
        fragment not in module.casefold()
        for module in imported_modules
        for fragment in forbidden_imports
    )
    assert "PlanTiers" not in source
    assert "tenant_id" not in {
        node.arg for node in ast.walk(tree) if isinstance(node, ast.arg)
    }
    assert not set(catalogue.__all__).intersection(
        {"create", "issue", "activate", "persist", "authorize", "execute"}
    )


# ARTIFACT: test_wilsy_ai_vas_feature_catalogue.py
# VERSION: v1.0.0-D57A-WILSY-AI-VAS-FEATURE-CATALOGUE-CERT
# AUTHORITY BOUNDARY: direct pure feature-to-tier catalogue evidence only; no subscription, entitlement, IAM, persistence or runtime authority
# TENANT POSTURE: global metadata only; no tenant ownership or activation fact
# FAIL-CLOSED POSTURE: exact total mapping required; generic, unknown, malformed and drifted inputs reject without default
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
