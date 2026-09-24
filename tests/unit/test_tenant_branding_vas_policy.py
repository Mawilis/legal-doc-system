"""Direct certificate for the D21B1 Tenant Branding VAS policy.

TITLE: Tenant Branding VAS Policy Direct Certificate
VERSION: v1.0.0-D21B1-TENANT-BRANDING-VAS-POLICY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove the four approved branding packages, cumulative presentation
         capabilities, permanent WILSY trust mark, custom-code prohibition,
         strict hydration and deterministic SHA3-512 integrity.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_vas_policy.py
COLLABORATION / OWNERSHIP: Evidence-only direct certificate for the D21B1
                            Python EOS branding package policy.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG: v1.0.0-D21B1-TENANT-BRANDING-VAS-POLICY-CERT establishes direct
           evidence for Starter, Professional, Institutional and Enterprise
           policy semantics without tenant entitlement, persistence, pricing
           or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic policy facts only; no tenant data.
TENANT BOUNDARY: No tenant entitlement or tenant identity is created.
AUTHORITY BOUNDARY: Policy-certificate evidence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import re

import pytest

from tools.eos.saas.billing.tenant_branding_vas_policy import (
    PLATFORM_TRUST_MARK_CAPABILITY,
    TenantBrandingTier,
    TenantBrandingVASPolicy,
    TenantBrandingVASPolicyError,
    get_tenant_branding_vas_policy,
    hydrate_tenant_branding_vas_policy,
)


def test_exact_four_tier_branding_ladder() -> None:
    assert [tier.value for tier in TenantBrandingTier] == [
        "TENANT_BRANDING_STARTER",
        "TENANT_BRANDING_PROFESSIONAL",
        "TENANT_BRANDING_INSTITUTIONAL",
        "TENANT_BRANDING_ENTERPRISE",
    ]


def test_starter_is_wilsy_platform_identity_only() -> None:
    starter = get_tenant_branding_vas_policy(TenantBrandingTier.STARTER)
    assert starter.capabilities == (PLATFORM_TRUST_MARK_CAPABILITY,)
    assert not starter.permits("tenant.brand.logo.v1")


def test_professional_adds_logo_colours_and_email_identity_only() -> None:
    policy = get_tenant_branding_vas_policy(TenantBrandingTier.PROFESSIONAL)
    assert policy.capabilities == (
        PLATFORM_TRUST_MARK_CAPABILITY,
        "tenant.brand.logo.v1",
        "tenant.brand.colors.v1",
        "tenant.brand.email_identity.v1",
    )
    assert not policy.permits("tenant.brand.auth_surfaces.v1")
    assert not policy.permits("tenant.brand.custom_domain.v1")


def test_institutional_adds_auth_documents_invitations_and_favicon() -> None:
    policy = get_tenant_branding_vas_policy(TenantBrandingTier.INSTITUTIONAL)
    for capability in (
        "tenant.brand.logo.v1",
        "tenant.brand.colors.v1",
        "tenant.brand.email_identity.v1",
        "tenant.brand.auth_surfaces.v1",
        "tenant.brand.documents.v1",
        "tenant.brand.invitations.v1",
        "tenant.brand.favicon.v1",
    ):
        assert policy.permits(capability)
    assert not policy.permits("tenant.brand.custom_domain.v1")


def test_enterprise_adds_custom_domain_governed_package_and_multiple_profiles() -> None:
    policy = get_tenant_branding_vas_policy(TenantBrandingTier.ENTERPRISE)
    for capability in (
        "tenant.brand.custom_domain.v1",
        "tenant.brand.governed_package.v1",
        "tenant.brand.multiple_profiles.v1",
    ):
        assert policy.permits(capability)
    assert set(
        get_tenant_branding_vas_policy(
            TenantBrandingTier.INSTITUTIONAL
        ).capabilities
    ).issubset(set(policy.capabilities))


@pytest.mark.parametrize("tier", list(TenantBrandingTier))
def test_every_tier_requires_wilsy_trust_mark_and_forbids_custom_code(
    tier: TenantBrandingTier,
) -> None:
    policy = get_tenant_branding_vas_policy(tier)
    assert policy.platform_trust_mark_required is True
    assert policy.custom_code_allowed is False
    assert policy.capabilities[0] == PLATFORM_TRUST_MARK_CAPABILITY
    assert not any(
        capability in policy.capabilities
        for capability in (
            "tenant.brand.custom_css.v1",
            "tenant.brand.custom_js.v1",
            "tenant.brand.custom_html.v1",
        )
    )


def test_unknown_tier_and_caller_policy_override_fail_closed() -> None:
    with pytest.raises(TenantBrandingVASPolicyError, match="D21B1_UNKNOWN_TIER"):
        get_tenant_branding_vas_policy("UNKNOWN")
    professional = get_tenant_branding_vas_policy(
        TenantBrandingTier.PROFESSIONAL
    )
    with pytest.raises(
        TenantBrandingVASPolicyError,
        match="D21B1_CALLER_VALUE_OVERRIDE",
    ):
        replace(
            professional,
            capabilities=professional.capabilities
            + ("tenant.brand.custom_domain.v1",),
            fingerprint="",
        )
    with pytest.raises(
        TenantBrandingVASPolicyError,
        match="D21B1_CUSTOM_CODE_PROHIBITED",
    ):
        replace(
            professional,
            custom_code_allowed=True,
            fingerprint="",
        )


def test_fingerprint_is_deterministic_lowercase_sha3_512() -> None:
    first = get_tenant_branding_vas_policy(TenantBrandingTier.ENTERPRISE)
    second = get_tenant_branding_vas_policy(TenantBrandingTier.ENTERPRISE)
    assert first.fingerprint == second.fingerprint
    assert re.fullmatch(r"[0-9a-f]{128}", first.fingerprint)


def test_strict_round_trip_and_fingerprint_drift_rejection() -> None:
    policy = get_tenant_branding_vas_policy(TenantBrandingTier.INSTITUTIONAL)
    payload = policy.to_dict()
    assert hydrate_tenant_branding_vas_policy(payload) == policy

    with pytest.raises(
        TenantBrandingVASPolicyError,
        match="D21B1_DESCRIPTOR_SCHEMA_INVALID",
    ):
        hydrate_tenant_branding_vas_policy({**payload, "extra": "x"})

    corrupt = dict(payload)
    corrupt["fingerprint"] = "f" * 128
    with pytest.raises(
        TenantBrandingVASPolicyError,
        match="D21B1_FINGERPRINT_MISMATCH",
    ):
        hydrate_tenant_branding_vas_policy(corrupt)


def test_descriptor_is_immutable_and_contains_no_financial_or_authority_truth() -> None:
    policy = get_tenant_branding_vas_policy(TenantBrandingTier.ENTERPRISE)
    with pytest.raises((FrozenInstanceError, AttributeError)):
        policy.label = "Changed"  # type: ignore[misc]

    forbidden = {
        "price",
        "amount",
        "currency",
        "invoice",
        "charge",
        "payment",
        "execution",
        "settlement",
        "subscription_id",
        "tenant_id",
        "principal_id",
        "role",
        "permission",
        "entitled",
        "active",
    }
    assert forbidden.isdisjoint(policy.to_dict())


def test_capability_query_is_exact_and_does_not_normalize_authority() -> None:
    policy = get_tenant_branding_vas_policy(TenantBrandingTier.PROFESSIONAL)
    assert policy.permits("tenant.brand.logo.v1") is True
    assert policy.permits("TENANT.BRAND.LOGO.V1") is False
    with pytest.raises(
        TenantBrandingVASPolicyError,
        match="D21B1_CAPABILITY_INVALID",
    ):
        policy.permits(" tenant.brand.logo.v1")


# ARTIFACT: test_tenant_branding_vas_policy.py
# VERSION: v1.0.0-D21B1-TENANT-BRANDING-VAS-POLICY-CERT
# AUTHORITY BOUNDARY: direct policy evidence only; no tenant entitlement
# TENANT POSTURE: synthetic global policy facts only
# FAIL-CLOSED POSTURE: policy drift and unsupported capability material reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
