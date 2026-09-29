"""Direct certificate for tenant Legal Evidence capacity-profile composition.

TITLE: Tenant Legal Evidence Capacity Profile Resolver Direct Certificate
VERSION: v1.0.0-L10A2Q-P2-TENANT-LEGAL-EVIDENCE-CAPACITY-PROFILE-CERT
AUTHORITY: WILSY OS Core Governance
PURPOSE: Prove exact composition of canonical subscription truth, ACTIVE
         LEGAL_OPERATIONS entitlement evidence and the certified Legal Evidence
         capacity-profile identity resolver.
CERTIFICATION / UPDATE DATE: 2026-09-29

AUTHORITY BOUNDARY:
    Read-only deterministic evidence composition only. No subscription mutation,
    entitlement activation, IAM, storage admission, billing, payment,
    settlement or financial execution authority.

TENANT POSTURE:
    Subscription tenant, requested tenant and entitlement tenant must match
    exactly. Cross-tenant composition rejects.

FAIL-CLOSED POSTURE:
    Invalid subscription integrity, inactive subscription, absent catalogue
    provenance, inactive entitlement, wrong tenant or missing capacity binding
    rejects.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.saas.billing.legal_evidence_capacity_profile_resolver import (
    CAPACITY_FEATURE_STARTER,
)
from tools.eos.saas.billing.legal_evidence_capacity_policy_contract import (
    LegalEvidenceCapacityProfile,
)
from tools.eos.saas.billing.legal_evidence_capacity_tenant_profile_resolver import (
    LegalEvidenceCapacityTenantProfileError,
    derive_legal_evidence_capacity_tenant_profile,
)
from tools.eos.saas.domain.subscription import (
    AuditAction,
    AuditEntry,
    BillingFrequency,
    PlanTiers,
    SubscriptionEntity,
    SubscriptionStatus,
)
from tools.eos.saas.entitlement.product_catalogue import (
    TenantProductId,
)
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlement,
    TenantProductEntitlementState,
    create_tenant_product_entitlement,
)


STAMP = datetime(2026, 9, 29, 20, 0, tzinfo=timezone.utc)
TENANT = "tenant-l10a2q-p2"
SUBSCRIPTION_ID = "WILSYSUB-L10A2QP2"
PLAN_ID = "WILSYPLAN-L10A2QP2"


def _subscription(**changes: Any) -> SubscriptionEntity:
    """Build exact canonical CREATE-proof shape used by SubscriptionRegistry."""
    values: dict[str, Any] = {
        "tenant_id": TENANT,
        "plan_id": PLAN_ID,
        "plan": PlanTiers.PROFESSIONAL,
        "amount": 499.0,
        "currency": "ZAR",
        "billing_frequency": BillingFrequency.MONTHLY,
        "start_date": STAMP,
        "current_period_start": STAMP,
        "current_period_end": datetime(
            2026,
            10,
            29,
            20,
            0,
            tzinfo=timezone.utc,
        ),
        "idempotency_key": "l10a2q-p2-subscription-command",
        "subscription_id": SUBSCRIPTION_ID,
        "plan_name": "Display label is not authority",
        "plan_features": (
            "legal.documents",
            CAPACITY_FEATURE_STARTER,
        ),
        "plan_catalogue_version": 7,
        "status": SubscriptionStatus.ACTIVE,
        "seal_nonce": "l10a2q-p2-seal",
        "tier": PlanTiers.PROFESSIONAL,
    }
    values.update(changes)
    entity = SubscriptionEntity(**values)

    metadata = {
        "source": "subscription_registry",
        "plan_id": entity.plan_id,
        "plan_catalogue_version": entity.plan_catalogue_version,
    }
    proof = entity.generate_proof(
        action="create",
        metadata=metadata,
    )
    audit = AuditEntry(
        action=AuditAction.CREATE,
        timestamp=STAMP,
        user="L10A2Q-P2-CERT",
        new_status=entity.status,
        tier=entity.tier,
        billing_mode=entity.billing_mode,
        metadata=metadata,
        proof_hash=proof,
    )
    payload = entity.to_dict()
    payload.update(
        {
            "proof_hash": proof,
            "merkle_root": "",
            "audit_trail": [audit.to_dict()],
        }
    )
    return SubscriptionEntity.from_dict(payload)


def _entitlement(
    *,
    tenant_id: str = TENANT,
    active: bool = True,
) -> TenantProductEntitlement:
    pending = create_tenant_product_entitlement(
        tenant_id=tenant_id,
        entitlement_id=f"ent-legal-{tenant_id}",
        product_id=TenantProductId.LEGAL_OPERATIONS,
        source_evidence_reference="subscription-entitlement-source",
        source_evidence_fingerprint="a" * 128,
    )
    if not active:
        return pending

    return pending.transition(
        TenantProductEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="legal-product-activation",
        evidence_fingerprint="b" * 128,
        occurred_at=STAMP,
    )


def test_active_subscription_and_legal_entitlement_derive_profile_evidence() -> None:
    subscription = _subscription()
    entitlement = _entitlement()

    result = derive_legal_evidence_capacity_tenant_profile(
        tenant_id=TENANT,
        subscription=subscription,
        entitlement=entitlement,
        evaluated_at=STAMP,
    )

    assert result.tenant_id == TENANT
    assert result.subscription_id == SUBSCRIPTION_ID
    assert result.plan_id == PLAN_ID
    assert result.plan_catalogue_version == 7
    assert result.subscription_proof_hash == subscription.proof_hash
    assert result.entitlement_id == entitlement.entitlement_id
    assert result.entitlement_revision == 1
    assert result.entitlement_fingerprint == entitlement.fingerprint
    assert result.product_id is TenantProductId.LEGAL_OPERATIONS
    assert result.profile is LegalEvidenceCapacityProfile.STARTER
    assert result.evaluated_at == STAMP
    assert len(result.fingerprint) == 128
    int(result.fingerprint, 16)


def test_result_is_immutable() -> None:
    result = derive_legal_evidence_capacity_tenant_profile(
        tenant_id=TENANT,
        subscription=_subscription(),
        entitlement=_entitlement(),
        evaluated_at=STAMP,
    )

    with pytest.raises(FrozenInstanceError):
        result.profile = LegalEvidenceCapacityProfile.GROWTH  # type: ignore[misc]


def test_projection_is_deterministic_for_identical_authority_inputs() -> None:
    subscription = _subscription()
    entitlement = _entitlement()

    first = derive_legal_evidence_capacity_tenant_profile(
        tenant_id=TENANT,
        subscription=subscription,
        entitlement=entitlement,
        evaluated_at=STAMP,
    )
    second = derive_legal_evidence_capacity_tenant_profile(
        tenant_id=TENANT,
        subscription=subscription,
        entitlement=entitlement,
        evaluated_at=STAMP,
    )

    assert first == second
    assert first.fingerprint == second.fingerprint


def test_subscription_tenant_mismatch_fails_closed() -> None:
    with pytest.raises(
        LegalEvidenceCapacityTenantProfileError,
        match="L10A2Q_P2_SUBSCRIPTION_TENANT_MISMATCH",
    ):
        derive_legal_evidence_capacity_tenant_profile(
            tenant_id="tenant-other",
            subscription=_subscription(),
            entitlement=_entitlement(),
            evaluated_at=STAMP,
        )


def test_entitlement_tenant_mismatch_fails_closed() -> None:
    with pytest.raises(
        LegalEvidenceCapacityTenantProfileError,
        match="L10A2Q_P2_ENTITLEMENT_TENANT_MISMATCH",
    ):
        derive_legal_evidence_capacity_tenant_profile(
            tenant_id=TENANT,
            subscription=_subscription(),
            entitlement=_entitlement(
                tenant_id="tenant-other",
            ),
            evaluated_at=STAMP,
        )


def test_non_active_subscription_fails_closed() -> None:
    with pytest.raises(
        LegalEvidenceCapacityTenantProfileError,
        match="L10A2Q_P2_SUBSCRIPTION_ACTIVE_REQUIRED",
    ):
        derive_legal_evidence_capacity_tenant_profile(
            tenant_id=TENANT,
            subscription=_subscription(
                status=SubscriptionStatus.PAUSED,
            ),
            entitlement=_entitlement(),
            evaluated_at=STAMP,
        )


def test_missing_plan_catalogue_provenance_fails_closed() -> None:
    with pytest.raises(
        LegalEvidenceCapacityTenantProfileError,
        match="L10A2Q_P2_PLAN_CATALOGUE_VERSION_REQUIRED",
    ):
        derive_legal_evidence_capacity_tenant_profile(
            tenant_id=TENANT,
            subscription=_subscription(
                plan_catalogue_version=None,
            ),
            entitlement=_entitlement(),
            evaluated_at=STAMP,
        )


def test_pending_legal_product_entitlement_fails_closed() -> None:
    with pytest.raises(
        LegalEvidenceCapacityTenantProfileError,
        match="L10A2Q_P2_LEGAL_ENTITLEMENT_ACTIVE_REQUIRED",
    ):
        derive_legal_evidence_capacity_tenant_profile(
            tenant_id=TENANT,
            subscription=_subscription(),
            entitlement=_entitlement(active=False),
            evaluated_at=STAMP,
        )


def test_missing_explicit_non_founder_capacity_binding_fails_closed() -> None:
    with pytest.raises(
        LegalEvidenceCapacityTenantProfileError,
        match="L10A2Q_P2_PROFILE_BINDING_REQUIRED",
    ):
        derive_legal_evidence_capacity_tenant_profile(
            tenant_id=TENANT,
            subscription=_subscription(
                plan_features=("legal.documents",),
            ),
            entitlement=_entitlement(),
            evaluated_at=STAMP,
        )


def test_evidence_surface_contains_no_price_or_payment_authority() -> None:
    result = derive_legal_evidence_capacity_tenant_profile(
        tenant_id=TENANT,
        subscription=_subscription(),
        entitlement=_entitlement(),
        evaluated_at=STAMP,
    )

    keys = set(result.to_dict())

    assert "price" not in keys
    assert "amount" not in keys
    assert "currency" not in keys
    assert "payment" not in keys
    assert "settlement" not in keys
    assert "invoice" not in keys


# ARTIFACT: test_legal_evidence_capacity_tenant_profile_resolver.py
# VERSION: v1.0.0-L10A2Q-P2-TENANT-LEGAL-EVIDENCE-CAPACITY-PROFILE-CERT
# AUTHORITY BOUNDARY: composition evidence only; no runtime admission authority
# TENANT POSTURE: exact subscription + entitlement tenant binding
# FAIL-CLOSED POSTURE: invalid, inactive, mismatched or unbound authority rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
