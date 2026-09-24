"""Direct certificate for D21B4A tenant branding profile selection facts.

TITLE: Tenant Branding Profile Selection Direct Certificate
VERSION: v1.0.0-D21B4A-TENANT-BRANDING-PROFILE-SELECTION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove selection-time ACTIVE-entitlement/profile correlation, revision
         lineage, integrity and historical-only authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_profile_selection.py
COLLABORATION / OWNERSHIP: Direct certificate for D21B4A immutable selection
                            facts; D21B4B will own persistence/current-pointer
                            CAS and runtime projection remains later.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B4A-TENANT-BRANDING-PROFILE-SELECTION-CERT establishes
           direct evidence for initial/subsequent selection lineage, exact
           D21B3 profile and current ACTIVE D21B2 correlation, cross-tenant/
           stale-provenance rejection, SHA3-512 integrity and strict exclusion
           of raw branding, IAM/browser, commercial and financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic tenant/profile/evidence references only.
TENANT BOUNDARY: Every composition remains exact-tenant and cross-tenant silent.
AUTHORITY BOUNDARY: Historical selection evidence only; no durable currentness,
                    browser presentation, asset resolution or IAM.
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
    approve_tenant_branding_profile,
)
from tools.eos.saas.domain.tenant_branding_profile_selection import (
    TenantBrandingProfileSelection,
    TenantBrandingProfileSelectionError,
    select_tenant_branding_profile,
)


NOW = datetime(2026, 9, 25, 13, 0, tzinfo=timezone.utc)
FP = "a" * 128
ASSET_FP = "b" * 128


def active_entitlement(
    *,
    tenant_id: str = "tenant-a",
    entitlement_id: str = "branding-ent-a",
    tier: TenantBrandingTier = TenantBrandingTier.PROFESSIONAL,
) -> TenantBrandingEntitlement:
    """Return one exact ACTIVE D21B2 entitlement."""
    pending = create_tenant_branding_entitlement(
        tenant_id=tenant_id,
        entitlement_id=entitlement_id,
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


def approved_profile(
    entitlement: TenantBrandingEntitlement | None = None,
    *,
    profile_id: str = "profile-primary",
) -> TenantBrandingProfile:
    """Return one valid D21B3 approved profile."""
    current = entitlement or active_entitlement()
    return approve_tenant_branding_profile(
        entitlement=current,
        profile_id=profile_id,
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


def initial_selection(
    *,
    entitlement: TenantBrandingEntitlement | None = None,
    profile: TenantBrandingProfile | None = None,
) -> TenantBrandingProfileSelection:
    """Return one valid revision-1 selection fact."""
    current = entitlement or active_entitlement()
    approved = profile or approved_profile(current)
    return select_tenant_branding_profile(
        profile=approved,
        current_entitlement=current,
        selection_id="selection-1",
        selection_revision=1,
        selected_at=NOW,
        selection_evidence_reference="selection-evidence-1",
        selection_evidence_fingerprint=FP,
    )


def test_initial_selection_binds_exact_profile_and_active_entitlement() -> None:
    """Revision one proves exact profile/current-entitlement selection-time truth."""
    current = active_entitlement()
    approved = approved_profile(current)
    value = initial_selection(entitlement=current, profile=approved)
    assert value.tenant_id == "tenant-a"
    assert value.selection_revision == 1
    assert value.profile_id == approved.profile_id
    assert value.profile_fingerprint == approved.fingerprint
    assert value.branding_entitlement_id == current.entitlement_id
    assert value.branding_entitlement_revision == current.lifecycle_revision
    assert value.branding_entitlement_fingerprint == current.fingerprint
    assert value.branding_tier is TenantBrandingTier.PROFESSIONAL
    assert value.prior_selection_id is None
    assert value.prior_selection_fingerprint is None


def test_second_selection_requires_exact_prior_lineage() -> None:
    """Revision two binds exact prior selection identity and fingerprint."""
    current = active_entitlement()
    first = initial_selection(entitlement=current)
    second_profile = approved_profile(current, profile_id="profile-secondary")
    second = select_tenant_branding_profile(
        profile=second_profile,
        current_entitlement=current,
        selection_id="selection-2",
        selection_revision=2,
        selected_at=NOW,
        selection_evidence_reference="selection-evidence-2",
        selection_evidence_fingerprint=FP,
        prior_selection=first,
    )
    assert second.selection_revision == 2
    assert second.prior_selection_id == first.selection_id
    assert second.prior_selection_fingerprint == first.fingerprint


def test_non_initial_revision_without_prior_selection_fails_closed() -> None:
    """A later revision can never invent a missing lineage antecedent."""
    current = active_entitlement()
    with pytest.raises(
        TenantBrandingProfileSelectionError,
        match="D21B4A_PRIOR_SELECTION_REQUIRED",
    ):
        select_tenant_branding_profile(
            profile=approved_profile(current),
            current_entitlement=current,
            selection_id="selection-2",
            selection_revision=2,
            selected_at=NOW,
            selection_evidence_reference="selection-evidence-2",
            selection_evidence_fingerprint=FP,
        )


def test_prior_selection_revision_and_tenant_must_match() -> None:
    """Prior selection must be the exact previous revision for the same tenant."""
    current = active_entitlement()
    first = initial_selection(entitlement=current)
    second_profile = approved_profile(current, profile_id="profile-secondary")

    with pytest.raises(
        TenantBrandingProfileSelectionError,
        match="D21B4A_PRIOR_SELECTION_MISMATCH",
    ):
        select_tenant_branding_profile(
            profile=second_profile,
            current_entitlement=current,
            selection_id="selection-3",
            selection_revision=3,
            selected_at=NOW,
            selection_evidence_reference="selection-evidence-3",
            selection_evidence_fingerprint=FP,
            prior_selection=first,
        )

    other_entitlement = active_entitlement(
        tenant_id="tenant-b",
        entitlement_id="branding-ent-b",
    )
    other_profile = approve_tenant_branding_profile(
        entitlement=other_entitlement,
        profile_id="profile-b",
        profile_label="Tenant B",
        source_evidence_reference="submission-b",
        source_evidence_fingerprint=FP,
        approved_at=NOW,
        approval_evidence_reference="approval-b",
        approval_evidence_fingerprint=FP,
        logo_asset_reference="asset:tenant-b:logo:primary",
        logo_asset_fingerprint=ASSET_FP,
        primary_color="#112233",
        secondary_color="#445566",
        accent_color="#AABBCC",
        email_display_name="Tenant B",
    )
    other_first = initial_selection(
        entitlement=other_entitlement,
        profile=other_profile,
    )
    with pytest.raises(
        TenantBrandingProfileSelectionError,
        match="D21B4A_PRIOR_SELECTION_MISMATCH",
    ):
        select_tenant_branding_profile(
            profile=second_profile,
            current_entitlement=current,
            selection_id="selection-2",
            selection_revision=2,
            selected_at=NOW,
            selection_evidence_reference="selection-evidence-2",
            selection_evidence_fingerprint=FP,
            prior_selection=other_first,
        )


@pytest.mark.parametrize(
    "state",
    [
        TenantBrandingEntitlementState.PENDING_SOURCE,
        TenantBrandingEntitlementState.SUSPENDED,
        TenantBrandingEntitlementState.REVOKED,
    ],
)
def test_non_active_current_entitlement_fails_closed(
    state: TenantBrandingEntitlementState,
) -> None:
    """Selection requires a currently read ACTIVE D21B2 snapshot."""
    pending = create_tenant_branding_entitlement(
        tenant_id="tenant-a",
        entitlement_id="branding-ent-a",
        branding_tier=TenantBrandingTier.PROFESSIONAL,
        source_evidence_reference="composition-1",
        source_evidence_fingerprint=FP,
    )
    approved = approved_profile(active_entitlement())
    if state is TenantBrandingEntitlementState.PENDING_SOURCE:
        current = pending
    else:
        active = pending.transition(
            TenantBrandingEntitlementState.ACTIVE,
            expected_revision=0,
            evidence_reference="activate-1",
            evidence_fingerprint=FP,
            occurred_at=NOW,
        )
        current = active.transition(
            state,
            expected_revision=1,
            evidence_reference=f"{state.value.lower()}-1",
            evidence_fingerprint=FP,
            occurred_at=NOW,
        )
    with pytest.raises(
        TenantBrandingProfileSelectionError,
        match="D21B4A_ACTIVE_ENTITLEMENT_REQUIRED",
    ):
        select_tenant_branding_profile(
            profile=approved,
            current_entitlement=current,
            selection_id="selection-x",
            selection_revision=1,
            selected_at=NOW,
            selection_evidence_reference="selection-evidence-x",
            selection_evidence_fingerprint=FP,
        )


def test_profile_must_match_exact_current_entitlement_snapshot() -> None:
    """Same-tenant but different entitlement evidence cannot be substituted."""
    profile_entitlement = active_entitlement(
        entitlement_id="branding-ent-original",
    )
    approved = approved_profile(profile_entitlement)
    different = active_entitlement(
        entitlement_id="branding-ent-different",
    )
    with pytest.raises(
        TenantBrandingProfileSelectionError,
        match="D21B4A_PROFILE_ENTITLEMENT_MISMATCH",
    ):
        select_tenant_branding_profile(
            profile=approved,
            current_entitlement=different,
            selection_id="selection-x",
            selection_revision=1,
            selected_at=NOW,
            selection_evidence_reference="selection-evidence-x",
            selection_evidence_fingerprint=FP,
        )


def test_selection_schema_carries_no_raw_brand_material() -> None:
    """Selection facts carry only authority identities and fingerprints."""
    payload = initial_selection().to_dict()
    forbidden = {
        "logo_asset_reference",
        "logo_asset_fingerprint",
        "primary_color",
        "secondary_color",
        "accent_color",
        "email_display_name",
        "favicon_asset_reference",
        "favicon_asset_fingerprint",
        "logo_url",
        "logo_path",
        "logo_base64",
        "asset_bytes",
    }
    assert forbidden.isdisjoint(payload)


def test_selection_does_not_claim_currentness_or_runtime_authorization() -> None:
    """Historical selection has no browser/IAM/current-pointer authority fields."""
    payload = initial_selection().to_dict()
    forbidden = {
        "is_current",
        "current_profile",
        "workspace_access",
        "principal_id",
        "role",
        "permission",
        "browser_authorized",
        "asset_resolved",
        "render_url",
    }
    assert forbidden.isdisjoint(payload)


def test_revision_and_prior_lineage_shape_fail_closed() -> None:
    """Revision values and prior evidence must have exact legal shape."""
    base = initial_selection()
    with pytest.raises(
        TenantBrandingProfileSelectionError,
        match="D21B4A_SELECTION_REVISION_INVALID",
    ):
        replace(base, selection_revision=0, fingerprint="")

    with pytest.raises(
        TenantBrandingProfileSelectionError,
        match="D21B4A_INITIAL_LINEAGE_INVALID",
    ):
        replace(
            base,
            prior_selection_id="prior",
            prior_selection_fingerprint=FP,
            fingerprint="",
        )

    with pytest.raises(TenantBrandingProfileSelectionError):
        replace(
            base,
            selection_revision=2,
            prior_selection_id="prior",
            prior_selection_fingerprint="not-a-digest",
            fingerprint="",
        )


def test_time_and_selection_evidence_are_mandatory() -> None:
    """Selection facts require aware time plus exact opaque evidence."""
    base = initial_selection()
    with pytest.raises(TenantBrandingProfileSelectionError):
        replace(
            base,
            selected_at=datetime(2026, 9, 25, 13, 0),
            fingerprint="",
        )
    with pytest.raises(TenantBrandingProfileSelectionError):
        replace(base, selection_evidence_reference="", fingerprint="")
    with pytest.raises(TenantBrandingProfileSelectionError):
        replace(
            base,
            selection_evidence_fingerprint="not-a-digest",
            fingerprint="",
        )


def test_fingerprint_is_deterministic_lowercase_sha3_512_and_mutation_sensitive() -> None:
    """Selection semantics are sealed deterministically."""
    first = initial_selection()
    second = initial_selection()
    assert first.fingerprint == second.fingerprint
    assert re.fullmatch(r"[0-9a-f]{128}", first.fingerprint)
    changed = replace(
        first,
        selection_evidence_reference="selection-evidence-other",
        fingerprint="",
    )
    assert changed.fingerprint != first.fingerprint


def test_strict_round_trip_and_corruption_fail_closed() -> None:
    """Hydration accepts exact schema and rejects missing/extra/corrupt material."""
    value = initial_selection()
    payload = value.to_dict()
    assert TenantBrandingProfileSelection.from_dict(payload) == value

    with pytest.raises(
        TenantBrandingProfileSelectionError,
        match="D21B4A_SCHEMA_INVALID",
    ):
        TenantBrandingProfileSelection.from_dict({**payload, "extra": "x"})

    missing = dict(payload)
    missing.pop("profile_id")
    with pytest.raises(
        TenantBrandingProfileSelectionError,
        match="D21B4A_SCHEMA_INVALID",
    ):
        TenantBrandingProfileSelection.from_dict(missing)

    corrupt = dict(payload)
    corrupt["fingerprint"] = "f" * 128
    with pytest.raises(
        TenantBrandingProfileSelectionError,
        match="D21B4A_FINGERPRINT_MISMATCH",
    ):
        TenantBrandingProfileSelection.from_dict(corrupt)


def test_immutability_and_financial_authority_firewall() -> None:
    """Selection facts are immutable and contain no commercial/execution truth."""
    value = initial_selection()
    with pytest.raises((FrozenInstanceError, AttributeError)):
        value.tenant_id = "tenant-b"  # type: ignore[misc]

    forbidden = {
        "plan_id",
        "subscription_id",
        "price",
        "amount",
        "currency",
        "bank_details",
        "tax_id",
        "invoice",
        "payment",
        "execution",
        "settlement",
    }
    assert forbidden.isdisjoint(value.to_dict())


def test_no_runtime_side_effect_imports() -> None:
    """Pure selection domain import must not load provider/network SDK authority."""
    import sys

    assert "requests" not in sys.modules
    assert "boto3" not in sys.modules


# ARTIFACT: test_tenant_branding_profile_selection.py
# VERSION: v1.0.0-D21B4A-TENANT-BRANDING-PROFILE-SELECTION-CERT
# AUTHORITY BOUNDARY: direct historical selection evidence only; no durable currentness, browser, asset resolution or IAM
# TENANT POSTURE: synthetic exact tenant/profile/current-ACTIVE-entitlement composition only
# FAIL-CLOSED POSTURE: inactive/mismatched entitlement, invalid lineage, malformed evidence, schema drift and corruption reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
