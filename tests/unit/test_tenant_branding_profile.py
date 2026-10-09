"""Direct certificate for the D21B3 approved tenant branding profile domain.

TITLE: Tenant Branding Profile Direct Certificate
VERSION: v1.0.0-D21B3-TENANT-BRANDING-PROFILE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove ACTIVE D21B2 binding, D21B1 capability gates, opaque asset
         evidence, profile integrity and legacy/financial authority firewalls.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_profile.py
COLLABORATION / OWNERSHIP: Evidence-only direct certificate for D21B3 profile
                            authority; persistence/current selection and asset
                            resolution remain deliberately outside this scope.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B3-TENANT-BRANDING-PROFILE-CERT establishes direct
           evidence for exact ACTIVE entitlement binding, tier-gated logo/
           colours/email-display/favicon material, mandatory WILSY trust mark,
           opaque asset-reference discipline, strict approval/source evidence,
           deterministic SHA3-512 integrity and exclusion of legacy banking,
           tax/legal-identity, raw-location, IAM/browser and financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic profile/evidence/asset references only.
TENANT BOUNDARY: Every profile is bound to one exact synthetic tenant and one
                 embedded ACTIVE D21B2 entitlement snapshot.
AUTHORITY BOUNDARY: Direct approved-profile evidence only; no persistence,
                    current selection, asset resolution, browser or IAM.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
import re
from typing import Any, cast

import pytest

from tools.eos.saas.billing.tenant_branding_vas_policy import TenantBrandingTier
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlement,
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)
from tools.eos.saas.domain.tenant_branding_profile import (
    TenantBrandingProfile,
    TenantBrandingProfileError,
    approve_tenant_branding_profile,
)


NOW = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)
FP = "a" * 128
ASSET_FP = "b" * 128


def active_entitlement(
    tier: TenantBrandingTier = TenantBrandingTier.PROFESSIONAL,
) -> TenantBrandingEntitlement:
    """Return one exact ACTIVE D21B2 synthetic entitlement."""
    pending = create_tenant_branding_entitlement(
        tenant_id="tenant-a",
        entitlement_id=f"branding-ent-{tier.value.lower()}",
        branding_tier=tier,
        source_evidence_reference="composition-1",
        source_evidence_fingerprint=FP,
    )
    return pending.transition(
        TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activate-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
    )


def profile(
    *,
    entitlement: TenantBrandingEntitlement | None = None,
    **changes: object,
) -> TenantBrandingProfile:
    """Return one valid approved Professional profile with optional changes."""
    entitlement = entitlement or active_entitlement()
    values: dict[str, object] = {
        "tenant_id": entitlement.tenant_id,
        "profile_id": "profile-primary",
        "profile_label": "Primary tenant brand",
        "branding_entitlement": entitlement,
        "source_evidence_reference": "brand-submission-1",
        "source_evidence_fingerprint": FP,
        "approved_at": NOW,
        "approval_evidence_reference": "brand-approval-1",
        "approval_evidence_fingerprint": FP,
        "logo_asset_reference": "asset:tenant-a:logo:primary",
        "logo_asset_fingerprint": ASSET_FP,
        "primary_color": "#112233",
        "secondary_color": "#445566",
        "accent_color": "#AABBCC",
        "email_display_name": "Acme Legal",
    }
    values.update(changes)
    return TenantBrandingProfile(**cast(Any, values))


def test_professional_profile_binds_active_entitlement_and_exact_brand_material() -> None:
    """Professional tier admits logo, colours and email display identity."""
    entitlement = active_entitlement(TenantBrandingTier.PROFESSIONAL)
    value = approve_tenant_branding_profile(
        entitlement=entitlement,
        profile_id="profile-primary",
        profile_label="Primary tenant brand",
        source_evidence_reference="submission-1",
        source_evidence_fingerprint=FP,
        approved_at=NOW,
        approval_evidence_reference="approval-1",
        approval_evidence_fingerprint=FP,
        logo_asset_reference="asset:tenant-a:logo:primary",
        logo_asset_fingerprint=ASSET_FP,
        primary_color="#112233",
        secondary_color="#445566",
        accent_color="#AABBCC",
        email_display_name="Acme Legal",
    )
    assert value.tenant_id == entitlement.tenant_id
    assert value.branding_entitlement == entitlement
    assert value.platform_trust_mark_required is True
    assert value.logo_asset_reference == "asset:tenant-a:logo:primary"
    assert value.email_display_name == "Acme Legal"


@pytest.mark.parametrize(
    ("field", "value", "error_code"),
    [
        (
            "logo_asset_reference",
            "asset:tenant-a:logo:primary",
            "D21B3_LOGO_NOT_ENTITLED",
        ),
        ("primary_color", "#112233", "D21B3_COLORS_NOT_ENTITLED"),
        (
            "email_display_name",
            "Acme Legal",
            "D21B3_EMAIL_IDENTITY_NOT_ENTITLED",
        ),
    ],
)
def test_starter_rejects_tenant_specific_brand_material(
    field: str,
    value: str,
    error_code: str,
) -> None:
    """Starter preserves platform-only branding and rejects tenant material."""
    changes: dict[str, object] = {
        "logo_asset_reference": None,
        "logo_asset_fingerprint": None,
        "primary_color": None,
        "secondary_color": None,
        "accent_color": None,
        "email_display_name": None,
    }
    changes[field] = value
    if field == "logo_asset_reference":
        changes["logo_asset_fingerprint"] = ASSET_FP
    with pytest.raises(TenantBrandingProfileError, match=error_code):
        profile(
            entitlement=active_entitlement(TenantBrandingTier.STARTER),
            **changes,
        )


def test_professional_rejects_favicon_but_institutional_and_enterprise_permit_it() -> None:
    """Favicon material begins only at the D21B1 Institutional tier."""
    with pytest.raises(
        TenantBrandingProfileError,
        match="D21B3_FAVICON_NOT_ENTITLED",
    ):
        profile(
            favicon_asset_reference="asset:tenant-a:favicon:primary",
            favicon_asset_fingerprint=ASSET_FP,
        )

    for tier in (
        TenantBrandingTier.INSTITUTIONAL,
        TenantBrandingTier.ENTERPRISE,
    ):
        value = profile(
            entitlement=active_entitlement(tier),
            favicon_asset_reference="asset:tenant-a:favicon:primary",
            favicon_asset_fingerprint=ASSET_FP,
        )
        assert value.favicon_asset_reference == "asset:tenant-a:favicon:primary"


@pytest.mark.parametrize(
    "state",
    [
        TenantBrandingEntitlementState.PENDING_SOURCE,
        TenantBrandingEntitlementState.SUSPENDED,
        TenantBrandingEntitlementState.REVOKED,
    ],
)
def test_non_active_entitlement_snapshots_fail_closed(
    state: TenantBrandingEntitlementState,
) -> None:
    """Only an exact ACTIVE D21B2 snapshot may underpin profile approval."""
    pending = create_tenant_branding_entitlement(
        tenant_id="tenant-a",
        entitlement_id="branding-ent-a",
        branding_tier=TenantBrandingTier.PROFESSIONAL,
        source_evidence_reference="composition-1",
        source_evidence_fingerprint=FP,
    )
    if state is TenantBrandingEntitlementState.PENDING_SOURCE:
        entitlement = pending
    else:
        active = pending.transition(
            TenantBrandingEntitlementState.ACTIVE,
            expected_revision=0,
            evidence_reference="activate-1",
            evidence_fingerprint=FP,
            occurred_at=NOW,
        )
        entitlement = active.transition(
            state,
            expected_revision=1,
            evidence_reference=f"{state.value.lower()}-1",
            evidence_fingerprint=FP,
            occurred_at=NOW,
        )
    with pytest.raises(
        TenantBrandingProfileError,
        match="D21B3_ACTIVE_ENTITLEMENT_REQUIRED",
    ):
        profile(entitlement=entitlement)


def test_profile_tenant_must_match_embedded_entitlement_exactly() -> None:
    """Caller cannot bind another tenant to an entitlement snapshot."""
    with pytest.raises(
        TenantBrandingProfileError,
        match="D21B3_TENANT_MISMATCH",
    ):
        profile(tenant_id="tenant-b")


@pytest.mark.parametrize(
    "reference",
    [
        "https://example.com/logo.png",
        "http://example.com/logo.png",
        "/tmp/logo.png",
        "../logo.png",
        "data:image/png;base64,AAAA",
        "file:logo",
    ],
)
def test_raw_logo_locations_and_non_asset_references_fail_closed(
    reference: str,
) -> None:
    """Profiles admit only opaque asset: references, never direct locations."""
    with pytest.raises(
        TenantBrandingProfileError,
        match="D21B3_INVALID_LOGO_ASSET_REFERENCE",
    ):
        profile(logo_asset_reference=reference)


def test_asset_reference_and_fingerprint_are_atomic() -> None:
    """Asset reference and SHA3-512-shaped evidence must appear together."""
    with pytest.raises(TenantBrandingProfileError):
        profile(logo_asset_reference=None, logo_asset_fingerprint=ASSET_FP)
    with pytest.raises(TenantBrandingProfileError):
        profile(
            logo_asset_reference="asset:tenant-a:logo:primary",
            logo_asset_fingerprint=None,
        )


@pytest.mark.parametrize(
    "color",
    ["#abc", "#abcdef", "#ABCDEG", "112233", "#11223344", ""],
)
def test_colours_require_canonical_uppercase_six_digit_hex(color: str) -> None:
    """Profile colours are exact canonical values; no browser normalization."""
    with pytest.raises(
        TenantBrandingProfileError,
        match="D21B3_INVALID_PRIMARY_COLOR",
    ):
        profile(primary_color=color)


def test_email_display_identity_is_exact_text_not_an_address_authority() -> None:
    """Email display label is bounded text and no sending address is stored."""
    value = profile(email_display_name="Acme Legal")
    assert value.email_display_name == "Acme Legal"
    assert "email_from" not in value.to_dict()
    assert "email_address" not in value.to_dict()

    with pytest.raises(TenantBrandingProfileError):
        profile(email_display_name=" Acme Legal ")


def test_platform_trust_mark_cannot_be_removed() -> None:
    """Every approved tenant profile preserves visible WILSY platform trust."""
    with pytest.raises(
        TenantBrandingProfileError,
        match="D21B3_TRUST_MARK_REQUIRED",
    ):
        profile(platform_trust_mark_required=False)


def test_source_approval_evidence_and_timezone_are_mandatory() -> None:
    """Profile approval requires exact source evidence and aware approval time."""
    with pytest.raises(TenantBrandingProfileError):
        profile(source_evidence_reference="")
    with pytest.raises(TenantBrandingProfileError):
        profile(approval_evidence_fingerprint="not-a-digest")
    with pytest.raises(TenantBrandingProfileError):
        profile(approved_at=datetime(2026, 9, 25, 12, 0))


def test_fingerprint_is_deterministic_lowercase_sha3_512_and_mutation_sensitive() -> None:
    """Approved profile semantic material is sealed deterministically."""
    first = profile()
    second = profile()
    assert first.fingerprint == second.fingerprint
    assert re.fullmatch(r"[0-9a-f]{128}", first.fingerprint)
    changed = replace(
        first,
        profile_label="Alternate tenant brand",
        fingerprint="",
    )
    assert changed.fingerprint != first.fingerprint


def test_strict_round_trip_and_corruption_fail_closed() -> None:
    """Only exact schema plus intact embedded entitlement/profile seals hydrate."""
    value = profile()
    payload = value.to_dict()
    assert TenantBrandingProfile.from_dict(payload) == value

    with pytest.raises(
        TenantBrandingProfileError,
        match="D21B3_SCHEMA_INVALID",
    ):
        TenantBrandingProfile.from_dict({**payload, "extra": "x"})

    missing = dict(payload)
    missing.pop("profile_id")
    with pytest.raises(
        TenantBrandingProfileError,
        match="D21B3_SCHEMA_INVALID",
    ):
        TenantBrandingProfile.from_dict(missing)

    corrupt_profile = dict(payload)
    corrupt_profile["fingerprint"] = "f" * 128
    with pytest.raises(
        TenantBrandingProfileError,
        match="D21B3_FINGERPRINT_MISMATCH",
    ):
        TenantBrandingProfile.from_dict(corrupt_profile)

    corrupt_entitlement = dict(payload)
    entitlement_payload = cast(
        dict[str, object],
        dict(cast(dict[str, object], corrupt_entitlement["branding_entitlement"])),
    )
    entitlement_payload["fingerprint"] = "f" * 128
    corrupt_entitlement["branding_entitlement"] = entitlement_payload
    with pytest.raises(
        TenantBrandingProfileError,
        match="D21B3_ENTITLEMENT_INVALID",
    ):
        TenantBrandingProfile.from_dict(corrupt_entitlement)


def test_immutability_and_authority_firewalls() -> None:
    """Approved profile is immutable and excludes legacy/commercial authority."""
    value = profile()
    with pytest.raises((FrozenInstanceError, AttributeError)):
        value.profile_id = "other"  # type: ignore[misc]

    forbidden = {
        "logo_url",
        "logo_path",
        "logo_base64",
        "address",
        "vat_number",
        "registration_number",
        "bank_details",
        "account_number",
        "iban",
        "swift",
        "mission",
        "footer",
        "headers",
        "custom_css",
        "custom_js",
        "custom_html",
        "custom_domain",
        "principal_id",
        "role",
        "permission",
        "workspace_access",
        "plan_id",
        "subscription_id",
        "price",
        "amount",
        "currency",
        "invoice",
        "payment",
        "execution",
        "settlement",
    }
    assert forbidden.isdisjoint(value.to_dict())


def test_no_runtime_side_effect_imports() -> None:
    """Pure profile domain import must not load network/provider SDK authority."""
    import sys

    assert "requests" not in sys.modules
    assert "boto3" not in sys.modules


# ARTIFACT: test_tenant_branding_profile.py
# VERSION: v1.0.0-D21B3-TENANT-BRANDING-PROFILE-CERT
# AUTHORITY BOUNDARY: direct approved-profile evidence only; no persistence/current selection, asset resolution, browser or IAM
# TENANT POSTURE: synthetic exact tenant/ACTIVE-D21B2 bindings only
# FAIL-CLOSED POSTURE: inactive entitlement, capability mismatch, raw asset location, malformed evidence and corruption reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
