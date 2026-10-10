"""WILSY OS canonical WILSY AI VAS commercial-feature catalogue.

TITLE: WILSY AI VAS Commercial Feature Catalogue
VERSION: v1.0.0-D57A-WILSY-AI-VAS-FEATURE-CATALOGUE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Define the closed tenant-neutral subscription feature identities that
         correspond exactly to the existing canonical WILSY AI commercial tiers
         without granting subscription ownership, entitlement, IAM, or execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/wilsy_ai_vas_feature_catalogue.py
COLLABORATION / OWNERSHIP: This catalogue owns only tier-specific WILSY AI VAS
                            commercial feature identity and correspondence;
                            SubscriptionRegistry owns tenant subscription truth,
                            WILSY AI policy owns tier value/capacity facts, and
                            entitlement authorities remain separate consumers.
CERTIFICATION / UPDATE DATE: 2026-10-10
CHANGELOG: v1.0.0-D57A-WILSY-AI-VAS-FEATURE-CATALOGUE establishes explicit
           ai.wilsy.starter, ai.wilsy.growth and ai.wilsy.institutional feature
           identities mapped bijectively to the three existing policy tiers.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Pure immutable in-process metadata; no tenant,
                             principal, credential, network, filesystem,
                             database, provider, or runtime input.
TENANT BOUNDARY: Global commercial-feature facts only. A feature identity does
                 not prove that any tenant has an ACTIVE subscription or an
                 entitlement to use WILSY AI.
AUTHORITY BOUNDARY: Exact feature-to-tier metadata only. No base-product,
                    subscription, plan, entitlement, IAM, admission, capacity,
                    provider, autonomous-action, or runtime execution authority.
FINANCIAL AUTHORITY BOUNDARY: No price mutation, invoice, charge, payment,
                              execution, paid, or settlement truth. Kennel EOS
                              remains the exclusive financial execution authority.
FAIL-CLOSED DECLARATION: Unknown, generic, malformed, case-drifted, whitespace-
                         drifted, or non-string features reject without default,
                         alias, base-plan inference, or STARTER fallback.
"""
from __future__ import annotations

from enum import Enum
from types import MappingProxyType
from typing import Final, Mapping

from tools.eos.saas.billing.wilsy_ai_commercial_policy import WilsyAITier


VERSION: Final[str] = "v1.0.0-D57A-WILSY-AI-VAS-FEATURE-CATALOGUE"
GENERIC_WILSY_AI_FEATURE_ID: Final[str] = "ai.wilsy"


class WilsyAIVASFeatureCatalogueError(ValueError):
    """Fail-closed feature-catalogue error with a stable institutional code.

    This error expresses invalid global metadata input only. It carries no
    tenant absence, subscription decision, entitlement, or financial meaning.
    """

    def __init__(self, code: str) -> None:
        """Create one deterministic pure-domain catalogue failure."""
        self.code = code
        super().__init__(code)


class WilsyAIVASFeatureId(str, Enum):
    """Closed tier-specific subscription features for the WILSY AI VAS.

    Enum membership describes commercial vocabulary only. It never proves
    that a plan contains the feature or that a tenant owns an entitlement.
    """

    STARTER = "ai.wilsy.starter"
    GROWTH = "ai.wilsy.growth"
    INSTITUTIONAL = "ai.wilsy.institutional"


FEATURE_TO_TIER: Final[Mapping[WilsyAIVASFeatureId, WilsyAITier]] = (
    MappingProxyType(
        {
            WilsyAIVASFeatureId.STARTER: WilsyAITier.STARTER,
            WilsyAIVASFeatureId.GROWTH: WilsyAITier.GROWTH,
            WilsyAIVASFeatureId.INSTITUTIONAL: WilsyAITier.INSTITUTIONAL,
        }
    )
)

if set(FEATURE_TO_TIER) != set(WilsyAIVASFeatureId):
    raise WilsyAIVASFeatureCatalogueError("D57A_FEATURE_MAPPING_INCOMPLETE")
if len(set(FEATURE_TO_TIER.values())) != len(FEATURE_TO_TIER):
    raise WilsyAIVASFeatureCatalogueError("D57A_TIER_MAPPING_NOT_BIJECTIVE")


def resolve_wilsy_ai_tier_for_feature(
    feature_id: WilsyAIVASFeatureId | str,
) -> WilsyAITier:
    """Resolve one exact tier-specific VAS feature to its canonical AI tier.

    @description Accepts only one exact closed D57A feature identity and returns
        its existing canonical WILSY AI policy tier without aliases or defaults.
    @collaboration Future subscription composition may call this only after it
        has independently established exact ACTIVE subscription feature truth.
    @institutional Separates commercial vocabulary from tenant ownership,
        entitlement issuance, IAM authority, capacity, and financial execution.
    @param feature_id Exact tier-specific commercial feature identity.
    @returns The corresponding existing canonical ``WilsyAITier``.
    @raises WilsyAIVASFeatureCatalogueError for unknown, generic, malformed,
        whitespace-drifted, case-drifted, or non-string input.
    """
    try:
        feature = WilsyAIVASFeatureId(feature_id)
    except (TypeError, ValueError) as error:
        raise WilsyAIVASFeatureCatalogueError(
            "D57A_UNKNOWN_WILSY_AI_VAS_FEATURE"
        ) from error
    return FEATURE_TO_TIER[feature]


def list_wilsy_ai_vas_features() -> tuple[WilsyAIVASFeatureId, ...]:
    """Return the complete closed feature set in stable tier order.

    The returned immutable tuple is global catalogue metadata and creates no
    tenant subscription, entitlement, IAM, persistence, or financial truth.
    """
    return tuple(WilsyAIVASFeatureId)


__all__ = [
    "FEATURE_TO_TIER",
    "GENERIC_WILSY_AI_FEATURE_ID",
    "VERSION",
    "WilsyAIVASFeatureCatalogueError",
    "WilsyAIVASFeatureId",
    "list_wilsy_ai_vas_features",
    "resolve_wilsy_ai_tier_for_feature",
]

# ARTIFACT: wilsy_ai_vas_feature_catalogue.py
# VERSION: v1.0.0-D57A-WILSY-AI-VAS-FEATURE-CATALOGUE
# AUTHORITY BOUNDARY: exact global WILSY AI VAS feature-to-tier metadata only; no subscription, entitlement, IAM, admission, capacity, provider, or runtime authority
# TENANT POSTURE: tenant-neutral catalogue facts; feature identity never proves tenant ownership or activation
# FAIL-CLOSED POSTURE: unknown, generic, malformed, case/whitespace-drifted and non-string feature input rejects without alias, default or base-plan inference
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
