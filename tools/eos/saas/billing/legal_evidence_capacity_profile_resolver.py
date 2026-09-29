"""WILSY OS Legal Evidence capacity-profile commercial binding resolver.

TITLE: Legal Evidence Capacity Profile Resolver
VERSION: v1.0.0-L10A2Q-P2-LEGAL-EVIDENCE-CAPACITY-PROFILE-RESOLVER
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Resolve one Legal Evidence capacity profile only from explicit,
         canonical PlanRegistry-derived commercial-plan evidence.

EPITOME:
    Non-Founder plans require an exact Legal Evidence capacity feature binding.
    Generic SaaS plan tiers, plan names, prices, tenant identifiers, browser
    labels, VAS tiers and heuristic fallbacks never create Legal Evidence
    capacity authority.

    FOUNDER_ENTERPRISE is the sole tier-derived exception because the canonical
    PlanRegistry/SubscriptionRegistry contract already carries that governed
    plan classification. This resolver does not establish or alter its price.

COLLABORATION / OWNERSHIP:
    PlanRegistry owns canonical plan catalogue truth.
    SubscriptionRegistry owns tenant subscription truth and its plan snapshot.
    TenantProductEntitlement owns tenant/product entitlement lifecycle evidence.
    L10A2Q-P1 owns Legal Evidence capacity-profile vocabulary and limits.
    This artifact owns only deterministic profile-identity binding.

CERTIFICATION / UPDATE DATE: 2026-09-29

SECURITY / PRIVACY POSTURE:
    No tenant data, credentials, content bytes, payment data or provider secrets
    are consumed.

TENANT BOUNDARY:
    This pure mapping function receives no tenant identifier and therefore
    cannot establish tenant authority. Tenant scope must be proven upstream.

AUTHORITY BOUNDARY:
    Mapping only. No plan mutation, subscription mutation, entitlement
    activation, IAM, storage admission, billing, payment, settlement or
    financial execution authority.

FINANCIAL AUTHORITY BOUNDARY:
    No price or amount is consumed. FOUNDER_ENTERPRISE profile resolution does
    not mutate or establish Founder pricing. Kennel EOS remains exclusive
    financial execution authority.

FAIL-CLOSED DECLARATION:
    Missing, malformed, conflicting or unknown profile bindings reject.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Final

from tools.eos.saas.billing.legal_evidence_capacity_policy_contract import (
    LegalEvidenceCapacityProfile,
)
from tools.eos.saas.domain.plan import PlanTiers


VERSION: Final[str] = (
    "v1.0.0-L10A2Q-P2-LEGAL-EVIDENCE-CAPACITY-PROFILE-RESOLVER"
)

CAPACITY_FEATURE_STARTER: Final[str] = "legal.evidence.capacity.STARTER"
CAPACITY_FEATURE_GROWTH: Final[str] = "legal.evidence.capacity.GROWTH"
CAPACITY_FEATURE_INSTITUTIONAL: Final[str] = (
    "legal.evidence.capacity.INSTITUTIONAL"
)

_EXPLICIT_PROFILE_FEATURES: Final[
    dict[str, LegalEvidenceCapacityProfile]
] = {
    CAPACITY_FEATURE_STARTER: LegalEvidenceCapacityProfile.STARTER,
    CAPACITY_FEATURE_GROWTH: LegalEvidenceCapacityProfile.GROWTH,
    CAPACITY_FEATURE_INSTITUTIONAL:
        LegalEvidenceCapacityProfile.INSTITUTIONAL,
}


class LegalEvidenceCapacityProfileResolverError(ValueError):
    """Raised when canonical plan evidence cannot resolve one profile safely."""


def _canonical_plan_tier(value: PlanTiers | str) -> PlanTiers:
    """Require one known canonical SaaS plan-tier identity."""
    try:
        return PlanTiers(value)
    except (TypeError, ValueError) as error:
        raise LegalEvidenceCapacityProfileResolverError(
            "L10A2Q_P2_PLAN_TIER_INVALID"
        ) from error


def _canonical_features(value: Iterable[str]) -> tuple[str, ...]:
    """Require an explicit finite sequence of exact feature strings."""
    if isinstance(value, (str, bytes)):
        raise LegalEvidenceCapacityProfileResolverError(
            "L10A2Q_P2_PLAN_FEATURES_INVALID"
        )

    try:
        features = tuple(value)
    except TypeError as error:
        raise LegalEvidenceCapacityProfileResolverError(
            "L10A2Q_P2_PLAN_FEATURES_INVALID"
        ) from error

    for feature in features:
        if (
            not isinstance(feature, str)
            or not feature
            or feature != feature.strip()
        ):
            raise LegalEvidenceCapacityProfileResolverError(
                "L10A2Q_P2_PLAN_FEATURE_INVALID"
            )

    return features


def resolve_legal_evidence_capacity_profile_identity(
    *,
    plan_tier: PlanTiers | str,
    plan_features: Iterable[str],
) -> LegalEvidenceCapacityProfile:
    """Resolve exactly one Legal Evidence capacity-profile identity.

    ``plan_tier`` and ``plan_features`` must originate from canonical
    PlanRegistry-derived subscription evidence before this function is called.

    For non-Founder plans, one exact Legal Evidence capacity feature is
    mandatory. Generic SaaS plan tiers intentionally do not imply STARTER,
    GROWTH or INSTITUTIONAL.

    ``FOUNDER_ENTERPRISE`` is the sole tier-derived profile. Any conflicting
    non-Founder Legal Evidence capacity feature on a Founder plan rejects.

    This function does not inspect tenant identity, plan name, price, billing
    amount, subscription status, entitlement state, IAM or storage state.
    Those authorities remain upstream or downstream of this pure mapping seam.
    """
    tier = _canonical_plan_tier(plan_tier)
    features = _canonical_features(plan_features)

    bound_profiles = {
        _EXPLICIT_PROFILE_FEATURES[feature]
        for feature in features
        if feature in _EXPLICIT_PROFILE_FEATURES
    }

    if tier is PlanTiers.FOUNDER_ENTERPRISE:
        if bound_profiles:
            raise LegalEvidenceCapacityProfileResolverError(
                "L10A2Q_P2_FOUNDER_PROFILE_CONFLICT"
            )
        return LegalEvidenceCapacityProfile.FOUNDER_ENTERPRISE

    if not bound_profiles:
        raise LegalEvidenceCapacityProfileResolverError(
            "L10A2Q_P2_PROFILE_BINDING_REQUIRED"
        )

    if len(bound_profiles) != 1:
        raise LegalEvidenceCapacityProfileResolverError(
            "L10A2Q_P2_PROFILE_BINDING_CONFLICT"
        )

    return next(iter(bound_profiles))


__all__ = [
    "CAPACITY_FEATURE_GROWTH",
    "CAPACITY_FEATURE_INSTITUTIONAL",
    "CAPACITY_FEATURE_STARTER",
    "LegalEvidenceCapacityProfileResolverError",
    "VERSION",
    "resolve_legal_evidence_capacity_profile_identity",
]


# ARTIFACT: legal_evidence_capacity_profile_resolver.py
# VERSION: v1.0.0-L10A2Q-P2-LEGAL-EVIDENCE-CAPACITY-PROFILE-RESOLVER
# AUTHORITY BOUNDARY: deterministic profile binding only; no admission authority
# TENANT POSTURE: no tenant identity accepted; tenant authority must exist upstream
# FAIL-CLOSED POSTURE: missing, malformed, conflicting or unknown bindings reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
