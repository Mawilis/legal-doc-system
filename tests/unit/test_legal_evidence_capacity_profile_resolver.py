"""Direct contract certificate for Legal Evidence capacity-profile resolution.

TITLE: Legal Evidence Capacity Profile Resolver Direct Certificate
VERSION: v1.0.0-L10A2Q-P2-LEGAL-EVIDENCE-CAPACITY-PROFILE-RESOLVER-CERT
AUTHORITY: WILSY OS Core Governance
PURPOSE: Prove that Legal Evidence capacity profiles are derived only from
         explicit canonical commercial-plan evidence, never names, prices,
         tenant identifiers, browser labels or heuristic plan inference.
CERTIFICATION / UPDATE DATE: 2026-09-29
TENANT POSTURE: Profile identity alone grants no tenant authority.
AUTHORITY BOUNDARY: Mapping contract only; no plan mutation, subscription
                    mutation, entitlement activation, IAM, storage, billing,
                    payment, settlement or financial execution authority.
FAIL-CLOSED POSTURE: Missing, conflicting or unknown bindings reject.
"""

from __future__ import annotations

import pytest

from tools.eos.saas.billing.legal_evidence_capacity_policy_contract import (
    LegalEvidenceCapacityProfile,
)
from tools.eos.saas.billing.legal_evidence_capacity_profile_resolver import (
    CAPACITY_FEATURE_GROWTH,
    CAPACITY_FEATURE_INSTITUTIONAL,
    CAPACITY_FEATURE_STARTER,
    LegalEvidenceCapacityProfileResolverError,
    resolve_legal_evidence_capacity_profile_identity,
)
from tools.eos.saas.domain.plan import PlanTiers


def test_explicit_starter_feature_resolves_starter() -> None:
    assert (
        resolve_legal_evidence_capacity_profile_identity(
            plan_tier=PlanTiers.PROFESSIONAL,
            plan_features=(
                "legal.documents",
                CAPACITY_FEATURE_STARTER,
            ),
        )
        is LegalEvidenceCapacityProfile.STARTER
    )


def test_explicit_growth_feature_resolves_growth_without_plan_name_inference() -> None:
    assert (
        resolve_legal_evidence_capacity_profile_identity(
            plan_tier=PlanTiers.PROFESSIONAL,
            plan_features=(
                "crm.core",
                CAPACITY_FEATURE_GROWTH,
            ),
        )
        is LegalEvidenceCapacityProfile.GROWTH
    )


def test_explicit_institutional_feature_resolves_institutional() -> None:
    assert (
        resolve_legal_evidence_capacity_profile_identity(
            plan_tier=PlanTiers.ENTERPRISE,
            plan_features=(
                "legal.documents",
                CAPACITY_FEATURE_INSTITUTIONAL,
            ),
        )
        is LegalEvidenceCapacityProfile.INSTITUTIONAL
    )


def test_founder_enterprise_is_the_only_tier_derived_profile() -> None:
    assert (
        resolve_legal_evidence_capacity_profile_identity(
            plan_tier=PlanTiers.FOUNDER_ENTERPRISE,
            plan_features=("legal.documents",),
        )
        is LegalEvidenceCapacityProfile.FOUNDER_ENTERPRISE
    )


@pytest.mark.parametrize(
    "tier",
    (
        PlanTiers.FREE,
        PlanTiers.PROFESSIONAL,
        PlanTiers.ENTERPRISE,
        PlanTiers.SOVEREIGN,
        PlanTiers.ULTRA,
    ),
)
def test_non_founder_tier_without_explicit_capacity_feature_fails_closed(
    tier: PlanTiers,
) -> None:
    with pytest.raises(
        LegalEvidenceCapacityProfileResolverError,
        match="L10A2Q_P2_PROFILE_BINDING_REQUIRED",
    ):
        resolve_legal_evidence_capacity_profile_identity(
            plan_tier=tier,
            plan_features=("legal.documents",),
        )


def test_conflicting_capacity_features_fail_closed() -> None:
    with pytest.raises(
        LegalEvidenceCapacityProfileResolverError,
        match="L10A2Q_P2_PROFILE_BINDING_CONFLICT",
    ):
        resolve_legal_evidence_capacity_profile_identity(
            plan_tier=PlanTiers.PROFESSIONAL,
            plan_features=(
                CAPACITY_FEATURE_STARTER,
                CAPACITY_FEATURE_GROWTH,
            ),
        )


def test_founder_rejects_non_founder_capacity_override() -> None:
    with pytest.raises(
        LegalEvidenceCapacityProfileResolverError,
        match="L10A2Q_P2_FOUNDER_PROFILE_CONFLICT",
    ):
        resolve_legal_evidence_capacity_profile_identity(
            plan_tier=PlanTiers.FOUNDER_ENTERPRISE,
            plan_features=(CAPACITY_FEATURE_GROWTH,),
        )


def test_duplicate_same_capacity_feature_does_not_create_ambiguity() -> None:
    assert (
        resolve_legal_evidence_capacity_profile_identity(
            plan_tier=PlanTiers.PROFESSIONAL,
            plan_features=(
                CAPACITY_FEATURE_STARTER,
                CAPACITY_FEATURE_STARTER,
            ),
        )
        is LegalEvidenceCapacityProfile.STARTER
    )


@pytest.mark.parametrize(
    "features",
    (
        (),
        ("STARTER",),
        ("growth",),
        ("TENANT_BRANDING_INSTITUTIONAL",),
        ("WILSY_AI_STARTER",),
        ("legal.evidence.capacity.UNKNOWN",),
    ),
)
def test_display_vas_or_lookalike_tokens_never_create_capacity_authority(
    features: tuple[str, ...],
) -> None:
    with pytest.raises(
        LegalEvidenceCapacityProfileResolverError,
        match="L10A2Q_P2_PROFILE_BINDING_REQUIRED",
    ):
        resolve_legal_evidence_capacity_profile_identity(
            plan_tier=PlanTiers.PROFESSIONAL,
            plan_features=features,
        )


def test_mapping_surface_contains_no_price_or_plan_name_inputs() -> None:
    import inspect

    signature = inspect.signature(
        resolve_legal_evidence_capacity_profile_identity
    )

    assert tuple(signature.parameters) == (
        "plan_tier",
        "plan_features",
    )
    assert "price" not in signature.parameters
    assert "amount" not in signature.parameters
    assert "plan_name" not in signature.parameters
    assert "tenant_id" not in signature.parameters


# ARTIFACT: test_legal_evidence_capacity_profile_resolver.py
# VERSION: v1.0.0-L10A2Q-P2-LEGAL-EVIDENCE-CAPACITY-PROFILE-RESOLVER-CERT
# AUTHORITY BOUNDARY: direct profile-binding contract only; no runtime admission
# FAIL-CLOSED POSTURE: implicit, missing, conflicting and lookalike bindings reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
