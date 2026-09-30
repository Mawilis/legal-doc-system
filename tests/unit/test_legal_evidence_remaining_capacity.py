"""Direct certificate for Legal Evidence remaining-capacity derivation.

TITLE: Legal Evidence Remaining Capacity Direct Certificate
VERSION: v1.0.0-L10A2Q-P4-LEGAL-EVIDENCE-REMAINING-CAPACITY-CERT
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Prove immutable P4 remaining-capacity evidence derived only from one exact
    tenant capacity-profile projection, its canonical P1 policy, and one
    complete P3C usage window at the same explicit evaluation instant.

EPITOME:
    P2 TENANT CAPACITY PROFILE
    + P1 CANONICAL CAPACITY POLICY
    + P3C COMPLETE USAGE WINDOW
    -> P4 REMAINING CAPACITY
    != CAPACITY RESERVED
    != STORAGE ADMITTED
    != IAM AUTHORIZED
    != BILLING / PAYMENT / SETTLEMENT

TIME BINDING:
    tenant_profile.evaluated_at MUST equal usage_window.as_of. P4 refuses to
    combine commercial authority and usage evidence evaluated at different
    instants.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.legal_evidence_remaining_capacity import (
    LegalEvidenceRemainingCapacity,
    LegalEvidenceRemainingCapacityError,
    derive_legal_evidence_remaining_capacity,
)
from tools.eos.legal_operations.domain.legal_evidence_usage_window import (
    LegalEvidenceUsageWindow,
)
from tools.eos.saas.billing.legal_evidence_capacity_commercial_policy import (
    get_legal_evidence_capacity_policy,
)
from tools.eos.saas.billing.legal_evidence_capacity_policy_contract import (
    LegalEvidenceCapacityProfile,
)
from tools.eos.saas.billing.legal_evidence_capacity_tenant_profile_resolver import (
    LegalEvidenceCapacityTenantProfile,
)
from tools.eos.saas.domain.tenant_product_entitlement import TenantProductId


AT = datetime(2026, 9, 30, 18, 45, tzinfo=timezone.utc)
SHA = "a" * 128


def _profile(
    *,
    tenant_id: str = "tenant-p4",
    profile: LegalEvidenceCapacityProfile = LegalEvidenceCapacityProfile.STARTER,
    evaluated_at: datetime = AT,
) -> LegalEvidenceCapacityTenantProfile:
    return LegalEvidenceCapacityTenantProfile(
        tenant_id=tenant_id,
        subscription_id="subscription-p4",
        plan_id="plan-p4",
        plan_catalogue_version=7,
        subscription_proof_hash="subscription-proof-p4",
        entitlement_id="entitlement-p4",
        entitlement_revision=3,
        entitlement_fingerprint=SHA,
        product_id=TenantProductId.LEGAL_OPERATIONS,
        profile=profile,
        evaluated_at=evaluated_at,
    )


def _window(
    *,
    tenant_id: str = "tenant-p4",
    document_id: str = "document-p4",
    as_of: datetime = AT,
    storage: int = 100,
    ingress: int = 80,
    versions: int = 4,
) -> LegalEvidenceUsageWindow:
    return LegalEvidenceUsageWindow(
        tenant_id=tenant_id,
        document_id=document_id,
        as_of=as_of,
        monthly_window_start=as_of.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        ),
        monthly_window_end=as_of,
        tenant_observation_count=4,
        monthly_observation_count=2,
        document_observation_count=4,
        tenant_storage_bytes_added=storage,
        monthly_ingress_bytes_added=ingress,
        document_versions_added=versions,
        source_observation_set_fingerprint=SHA,
    )


def _derive(
    *,
    tenant_profile: LegalEvidenceCapacityTenantProfile | None = None,
    usage_window: LegalEvidenceUsageWindow | None = None,
) -> LegalEvidenceRemainingCapacity:
    profile = tenant_profile or _profile()
    window = usage_window or _window()
    policy = get_legal_evidence_capacity_policy(profile.profile)

    return derive_legal_evidence_remaining_capacity(
        tenant_profile=profile,
        policy=policy,
        usage_window=window,
    )


def test_exact_inputs_derive_three_remaining_capacity_dimensions() -> None:
    profile = _profile()
    window = _window()
    policy = get_legal_evidence_capacity_policy(profile.profile)

    result = derive_legal_evidence_remaining_capacity(
        tenant_profile=profile,
        policy=policy,
        usage_window=window,
    )

    assert result.tenant_id == profile.tenant_id
    assert result.document_id == window.document_id
    assert result.evaluated_at == AT

    assert result.tenant_profile_fingerprint == profile.fingerprint
    assert result.capacity_policy_fingerprint == policy.fingerprint
    assert result.usage_window_fingerprint == window.fingerprint

    assert result.tenant_storage_limit_bytes == policy.tenant_storage_limit_bytes
    assert result.tenant_storage_consumed_bytes == window.tenant_storage_bytes_added
    assert result.remaining_storage_bytes == (
        policy.tenant_storage_limit_bytes
        - window.tenant_storage_bytes_added
    )

    assert result.monthly_ingress_limit_bytes == policy.monthly_ingress_limit_bytes
    assert result.monthly_ingress_consumed_bytes == window.monthly_ingress_bytes_added
    assert result.remaining_ingress_bytes == (
        policy.monthly_ingress_limit_bytes
        - window.monthly_ingress_bytes_added
    )

    assert result.max_document_versions == policy.max_document_versions
    assert result.document_versions_consumed == window.document_versions_added
    assert result.remaining_document_versions == (
        policy.max_document_versions
        - window.document_versions_added
    )

    assert result.storage_exhausted is False
    assert result.ingress_exhausted is False
    assert result.versions_exhausted is False


def test_exact_limit_is_exhausted_with_zero_remaining() -> None:
    profile = _profile()
    policy = get_legal_evidence_capacity_policy(profile.profile)

    result = _derive(
        tenant_profile=profile,
        usage_window=_window(
            storage=policy.tenant_storage_limit_bytes,
            ingress=policy.monthly_ingress_limit_bytes,
            versions=policy.max_document_versions,
        ),
    )

    assert result.remaining_storage_bytes == 0
    assert result.remaining_ingress_bytes == 0
    assert result.remaining_document_versions == 0
    assert result.storage_exhausted is True
    assert result.ingress_exhausted is True
    assert result.versions_exhausted is True


def test_over_limit_is_clamped_to_zero_and_remains_exhausted() -> None:
    profile = _profile()
    policy = get_legal_evidence_capacity_policy(profile.profile)

    result = _derive(
        tenant_profile=profile,
        usage_window=_window(
            storage=policy.tenant_storage_limit_bytes + 10,
            ingress=policy.monthly_ingress_limit_bytes + 20,
            versions=policy.max_document_versions + 3,
        ),
    )

    assert result.remaining_storage_bytes == 0
    assert result.remaining_ingress_bytes == 0
    assert result.remaining_document_versions == 0
    assert result.storage_exhausted is True
    assert result.ingress_exhausted is True
    assert result.versions_exhausted is True


def test_zero_usage_preserves_full_capacity() -> None:
    profile = _profile()
    policy = get_legal_evidence_capacity_policy(profile.profile)

    window = LegalEvidenceUsageWindow(
        tenant_id=profile.tenant_id,
        document_id="document-empty",
        as_of=AT,
        monthly_window_start=AT.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        ),
        monthly_window_end=AT,
        tenant_observation_count=0,
        monthly_observation_count=0,
        document_observation_count=0,
        tenant_storage_bytes_added=0,
        monthly_ingress_bytes_added=0,
        document_versions_added=0,
        source_observation_set_fingerprint=SHA,
    )

    result = _derive(
        tenant_profile=profile,
        usage_window=window,
    )

    assert result.remaining_storage_bytes == policy.tenant_storage_limit_bytes
    assert result.remaining_ingress_bytes == policy.monthly_ingress_limit_bytes
    assert result.remaining_document_versions == policy.max_document_versions


def test_cross_tenant_profile_and_usage_window_reject() -> None:
    with pytest.raises(
        LegalEvidenceRemainingCapacityError,
        match="L10A2Q_P4_TENANT_MISMATCH",
    ):
        _derive(
            tenant_profile=_profile(tenant_id="tenant-p4"),
            usage_window=_window(tenant_id="tenant-other"),
        )


def test_policy_profile_mismatch_rejects() -> None:
    tenant_profile = _profile(
        profile=LegalEvidenceCapacityProfile.STARTER,
    )
    wrong_policy = get_legal_evidence_capacity_policy(
        LegalEvidenceCapacityProfile.GROWTH,
    )

    with pytest.raises(
        LegalEvidenceRemainingCapacityError,
        match="L10A2Q_P4_POLICY_PROFILE_MISMATCH",
    ):
        derive_legal_evidence_remaining_capacity(
            tenant_profile=tenant_profile,
            policy=wrong_policy,
            usage_window=_window(),
        )


def test_profile_and_usage_must_share_exact_evaluation_instant() -> None:
    with pytest.raises(
        LegalEvidenceRemainingCapacityError,
        match="L10A2Q_P4_EVALUATION_TIME_MISMATCH",
    ):
        _derive(
            tenant_profile=_profile(evaluated_at=AT),
            usage_window=_window(
                as_of=AT + timedelta(microseconds=1),
            ),
        )


def test_result_is_immutable_and_deterministic() -> None:
    first = _derive()
    second = _derive()

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128
    int(first.fingerprint, 16)

    with pytest.raises(FrozenInstanceError):
        first.remaining_storage_bytes = 0  # type: ignore[misc]


def test_round_trip_preserves_exact_integrity_evidence() -> None:
    result = _derive()

    hydrated = LegalEvidenceRemainingCapacity.from_dict(
        result.to_dict()
    )

    assert hydrated == result
    assert hydrated.fingerprint == result.fingerprint


def test_fingerprint_corruption_rejects() -> None:
    result = _derive()
    payload = result.to_dict()
    payload["fingerprint"] = "0" * 128

    with pytest.raises(
        LegalEvidenceRemainingCapacityError,
        match="L10A2Q_P4_FINGERPRINT_MISMATCH",
    ):
        LegalEvidenceRemainingCapacity.from_dict(payload)


def test_serialized_surface_has_no_reservation_admission_or_financial_authority() -> None:
    keys = set(_derive().to_dict())

    forbidden = {
        "reservation_id",
        "reserved_bytes",
        "reservation_expires_at",
        "admitted",
        "authorized",
        "permission",
        "principal_id",
        "price",
        "amount",
        "currency",
        "invoice",
        "payment",
        "settlement",
        "execution",
        "overage_price",
        "provider",
        "storage_reference",
    }

    assert forbidden.isdisjoint(keys)


def test_caller_cannot_override_derived_remaining_or_exhaustion_fields() -> None:
    result = _derive()

    with pytest.raises(TypeError):
        derive_legal_evidence_remaining_capacity(
            tenant_profile=_profile(),
            policy=get_legal_evidence_capacity_policy(
                LegalEvidenceCapacityProfile.STARTER,
            ),
            usage_window=_window(),
            remaining_storage_bytes=result.remaining_storage_bytes,  # type: ignore[call-arg]
        )


# ARTIFACT: test_legal_evidence_remaining_capacity.py
# VERSION: v1.0.0-L10A2Q-P4-LEGAL-EVIDENCE-REMAINING-CAPACITY-CERT
# AUTHORITY BOUNDARY: immutable remaining-capacity evidence only
# TENANT POSTURE: exact P2/P3C tenant binding
# TIME POSTURE: P2 evaluated_at equals P3C as_of
# RESERVATION POSTURE: no reservation or concurrent admission authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
