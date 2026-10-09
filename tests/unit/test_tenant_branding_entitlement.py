"""Direct certificate for the D21B2 tenant branding entitlement domain.

TITLE: Tenant Branding Entitlement Direct Certificate
VERSION: v1.0.0-D21B2-TENANT-BRANDING-ENTITLEMENT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exact D21B1 policy binding, tenant isolation, source-evidence
         requirements, lifecycle integrity and brand-profile/authority firewalls.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_entitlement.py
COLLABORATION / OWNERSHIP: Evidence-only direct certificate for the D21B2
                            tenant branding entitlement domain.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B2-TENANT-BRANDING-ENTITLEMENT-CERT establishes direct
           evidence for exact four-tier D21B1 binding, pending/active/suspended/
           revoked lifecycle semantics, strict evidence/integrity handling and
           separation from brand-profile assets, IAM, subscription/commercial
           pricing, browser presentation and financial execution.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic tenant/evidence identifiers only; no brand
                             assets, credentials, URLs, provider or browser data.
TENANT BOUNDARY: Cross-tenant or pseudo-tenant authority is never inferred.
AUTHORITY BOUNDARY: Direct domain evidence only; no persistence, brand-profile
                    approval, browser presentation, IAM or workspace admission.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
import re
from typing import Any, cast

import pytest

from tools.eos.saas.billing.tenant_branding_vas_policy import (
    TenantBrandingTier,
    get_tenant_branding_vas_policy,
)
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlement,
    TenantBrandingEntitlementError,
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)


NOW = datetime(2026, 9, 25, 10, 0, tzinfo=timezone.utc)
FP = "a" * 128


def entitlement(**changes: object) -> TenantBrandingEntitlement:
    """Return one valid pending synthetic entitlement with optional changes."""
    policy = get_tenant_branding_vas_policy(TenantBrandingTier.PROFESSIONAL)
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "entitlement_id": "branding-ent-a",
        "branding_tier": TenantBrandingTier.PROFESSIONAL,
        "policy_fingerprint": policy.policy_fingerprint,
        "lifecycle_state": TenantBrandingEntitlementState.PENDING_SOURCE,
        "source_evidence_reference": "tenant-composition-1",
        "source_evidence_fingerprint": FP,
    }
    values.update(changes)
    return TenantBrandingEntitlement(**cast(Any, values))


def test_factory_binds_exact_d21b1_policy_fingerprint_and_stays_pending() -> None:
    """Factory binds D21B1 evidence but never activates by construction."""
    value = create_tenant_branding_entitlement(
        tenant_id="tenant-a",
        entitlement_id="branding-ent-enterprise",
        branding_tier=TenantBrandingTier.ENTERPRISE,
        source_evidence_reference="composition-1",
        source_evidence_fingerprint=FP,
    )
    policy = get_tenant_branding_vas_policy(TenantBrandingTier.ENTERPRISE)
    assert value.branding_tier is TenantBrandingTier.ENTERPRISE
    assert value.policy_fingerprint == policy.policy_fingerprint
    assert value.lifecycle_state is TenantBrandingEntitlementState.PENDING_SOURCE
    assert value.activated_at is None


@pytest.mark.parametrize("tier", list(TenantBrandingTier))
def test_every_d21b1_tier_can_be_bound_exactly(tier: TenantBrandingTier) -> None:
    """Every canonical package is independently bindable without tier inference."""
    policy = get_tenant_branding_vas_policy(tier)
    value = create_tenant_branding_entitlement(
        tenant_id="tenant-a",
        entitlement_id=f"branding-{tier.value.lower()}",
        branding_tier=tier,
        source_evidence_reference="composition-1",
        source_evidence_fingerprint=FP,
    )
    assert value.branding_tier is tier
    assert value.policy_fingerprint == policy.policy_fingerprint


def test_entitlement_existence_does_not_approve_branding_or_activation() -> None:
    """Pending existence is not active branding and carries no approved assets."""
    value = entitlement()
    assert value.lifecycle_state is TenantBrandingEntitlementState.PENDING_SOURCE
    assert value.activated_at is None
    assert value.activation_evidence_reference is None
    serialized = value.to_dict()
    forbidden = {
        "logo",
        "logo_url",
        "primary_color",
        "secondary_color",
        "accent_color",
        "email_identity",
        "favicon",
        "login_branding",
        "document_branding",
        "custom_domain",
        "profile_id",
        "brand_profile",
    }
    assert forbidden.isdisjoint(serialized)


def test_policy_fingerprint_drift_and_unknown_tier_fail_closed() -> None:
    """Caller tier/policy drift never establishes a branding entitlement."""
    with pytest.raises(
        TenantBrandingEntitlementError,
        match="D21B2_POLICY_BINDING_INVALID",
    ):
        entitlement(policy_fingerprint="b" * 128)

    with pytest.raises(
        TenantBrandingEntitlementError,
        match="D21B2_ENUM_INVALID",
    ):
        entitlement(branding_tier="TENANT_BRANDING_UNKNOWN")


@pytest.mark.parametrize("tenant_id", ["", "default", "global", "root", "*"])
def test_missing_or_pseudo_tenant_fails_closed(tenant_id: str) -> None:
    """Pseudo-tenants cannot receive branding-package authority."""
    with pytest.raises(TenantBrandingEntitlementError):
        entitlement(tenant_id=tenant_id)


def test_source_evidence_reference_and_fingerprint_are_mandatory() -> None:
    """Creation requires one exact opaque source reference plus SHA3-512 shape."""
    with pytest.raises(TenantBrandingEntitlementError):
        entitlement(source_evidence_reference="")
    with pytest.raises(TenantBrandingEntitlementError):
        entitlement(source_evidence_fingerprint="not-a-digest")


def test_active_suspended_and_revoked_shapes_require_exact_evidence() -> None:
    """Each non-pending state requires its exact lifecycle evidence."""
    active = entitlement(
        lifecycle_state=TenantBrandingEntitlementState.ACTIVE,
        activated_at=NOW,
        activation_evidence_reference="activate-1",
        activation_evidence_fingerprint=FP,
    )
    assert active.lifecycle_state is TenantBrandingEntitlementState.ACTIVE

    suspended = entitlement(
        lifecycle_state=TenantBrandingEntitlementState.SUSPENDED,
        activated_at=NOW,
        activation_evidence_reference="activate-1",
        activation_evidence_fingerprint=FP,
        suspended_at=NOW,
        suspension_evidence_reference="suspend-1",
        suspension_evidence_fingerprint=FP,
    )
    assert suspended.lifecycle_state is TenantBrandingEntitlementState.SUSPENDED

    revoked = entitlement(
        lifecycle_state=TenantBrandingEntitlementState.REVOKED,
        activated_at=NOW,
        activation_evidence_reference="activate-1",
        activation_evidence_fingerprint=FP,
        revoked_at=NOW,
        revocation_evidence_reference="revoke-1",
        revocation_evidence_fingerprint=FP,
    )
    assert revoked.lifecycle_state is TenantBrandingEntitlementState.REVOKED


def test_invalid_lifecycle_shape_pair_and_chronology_fail_closed() -> None:
    """Partial evidence, impossible state shape and backwards time all reject."""
    with pytest.raises(
        TenantBrandingEntitlementError,
        match="D21B2_ACTIVE_SHAPE_INVALID",
    ):
        entitlement(lifecycle_state=TenantBrandingEntitlementState.ACTIVE)

    with pytest.raises(TenantBrandingEntitlementError):
        entitlement(
            activation_evidence_reference="activation-without-fingerprint",
        )

    with pytest.raises(
        TenantBrandingEntitlementError,
        match="D21B2_CHRONOLOGY_INVALID",
    ):
        entitlement(
            lifecycle_state=TenantBrandingEntitlementState.SUSPENDED,
            activated_at=NOW,
            activation_evidence_reference="activate-1",
            activation_evidence_fingerprint=FP,
            suspended_at=NOW.replace(year=2025),
            suspension_evidence_reference="suspend-1",
            suspension_evidence_fingerprint=FP,
        )


def test_revisioned_transitions_are_closed_and_evidence_backed() -> None:
    """Legal transitions increment revision; stale and terminal transitions reject."""
    pending = entitlement()
    active = pending.transition(
        TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activate-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
    )
    assert active.lifecycle_revision == 1
    assert active.activation_evidence_reference == "activate-1"

    suspended = active.transition(
        TenantBrandingEntitlementState.SUSPENDED,
        expected_revision=1,
        evidence_reference="suspend-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
    )
    assert suspended.lifecycle_revision == 2

    with pytest.raises(
        TenantBrandingEntitlementError,
        match="D21B2_STALE_REVISION",
    ):
        pending.transition(
            TenantBrandingEntitlementState.ACTIVE,
            expected_revision=99,
            evidence_reference="activate-x",
            evidence_fingerprint=FP,
            occurred_at=NOW,
        )

    with pytest.raises(
        TenantBrandingEntitlementError,
        match="D21B2_ILLEGAL_TRANSITION",
    ):
        suspended.transition(
            TenantBrandingEntitlementState.ACTIVE,
            expected_revision=2,
            evidence_reference="resume-x",
            evidence_fingerprint=FP,
            occurred_at=NOW,
        )


def test_revoked_is_terminal() -> None:
    """Revoked branding entitlement cannot be reactivated under V1."""
    active = entitlement().transition(
        TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activate-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
    )
    revoked = active.transition(
        TenantBrandingEntitlementState.REVOKED,
        expected_revision=1,
        evidence_reference="revoke-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
    )
    with pytest.raises(
        TenantBrandingEntitlementError,
        match="D21B2_ILLEGAL_TRANSITION",
    ):
        revoked.transition(
            TenantBrandingEntitlementState.ACTIVE,
            expected_revision=2,
            evidence_reference="reactivate-x",
            evidence_fingerprint=FP,
            occurred_at=NOW,
        )


def test_transition_chronology_is_strict() -> None:
    """A later lifecycle event cannot predate activation."""
    active = entitlement().transition(
        TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activate-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
    )
    with pytest.raises(
        TenantBrandingEntitlementError,
        match="D21B2_CHRONOLOGY_INVALID",
    ):
        active.transition(
            TenantBrandingEntitlementState.SUSPENDED,
            expected_revision=1,
            evidence_reference="suspend-1",
            evidence_fingerprint=FP,
            occurred_at=NOW.replace(year=2025),
        )


def test_fingerprint_is_deterministic_lowercase_sha3_512_and_mutation_sensitive() -> None:
    """Semantic changes alter the deterministic lowercase SHA3-512 seal."""
    first = entitlement()
    second = entitlement()
    assert first.fingerprint == second.fingerprint
    assert re.fullmatch(r"[0-9a-f]{128}", first.fingerprint)
    assert replace(
        first,
        tenant_id="tenant-b",
        fingerprint="",
    ).fingerprint != first.fingerprint


def test_strict_round_trip_unknown_missing_and_corrupt_payloads_fail_closed() -> None:
    """Hydration accepts only the exact schema and exact stored fingerprint."""
    value = entitlement()
    payload = value.to_dict()
    assert TenantBrandingEntitlement.from_dict(payload) == value

    with pytest.raises(
        TenantBrandingEntitlementError,
        match="D21B2_SCHEMA_INVALID",
    ):
        TenantBrandingEntitlement.from_dict({**payload, "extra": "x"})

    missing = dict(payload)
    missing.pop("branding_tier")
    with pytest.raises(
        TenantBrandingEntitlementError,
        match="D21B2_SCHEMA_INVALID",
    ):
        TenantBrandingEntitlement.from_dict(missing)

    corrupt = dict(payload)
    corrupt["fingerprint"] = "f" * 128
    with pytest.raises(
        TenantBrandingEntitlementError,
        match="D21B2_FINGERPRINT_MISMATCH",
    ):
        TenantBrandingEntitlement.from_dict(corrupt)


def test_immutability_and_authority_firewalls() -> None:
    """Entitlement evidence cannot mutate or acquire unrelated authorities."""
    value = entitlement()
    with pytest.raises((FrozenInstanceError, AttributeError)):
        value.tenant_id = "tenant-b"  # type: ignore[misc]

    forbidden = {
        "plan",
        "plan_id",
        "subscription_id",
        "price",
        "amount",
        "currency",
        "principal_id",
        "role",
        "permission",
        "workspace_access",
        "logo",
        "logo_url",
        "colors",
        "email_identity",
        "favicon",
        "custom_domain",
        "brand_profile",
        "invoice",
        "payment",
        "execution",
        "settlement",
    }
    assert forbidden.isdisjoint(value.to_dict())


def test_no_runtime_side_effect_imports() -> None:
    """Pure domain import must not load network/provider SDK authority."""
    import sys

    assert "requests" not in sys.modules
    assert "boto3" not in sys.modules


# ARTIFACT: test_tenant_branding_entitlement.py
# VERSION: v1.0.0-D21B2-TENANT-BRANDING-ENTITLEMENT-CERT
# AUTHORITY BOUNDARY: direct entitlement-domain evidence only; no persistence, brand-profile approval or IAM
# TENANT POSTURE: synthetic exact tenant/D21B1-tier bindings only
# FAIL-CLOSED POSTURE: policy drift, malformed evidence, stale revisions, corruption and illegal transitions reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
