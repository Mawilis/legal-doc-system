"""D22C4 direct certificate for Founder perpetual and commercial term policy."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.saas.domain.subscription import (
    BillingFrequency,
    PlanTiers,
    SubscriptionEntity,
    SubscriptionStatus,
)
from tools.eos.saas.billing.subscription_term_policy import (
    SubscriptionTermKind,
    SubscriptionTermPolicyError,
    evaluate_subscription_term,
)


NOW = datetime(2026, 10, 30, 10, 0, tzinfo=timezone.utc)


def _subscription(**changes: object) -> SubscriptionEntity:
    values: dict[str, object] = {
        "tenant_id": "tenant-commercial",
        "plan_id": "plan-commercial",
        "plan": PlanTiers.PROFESSIONAL,
        "amount": 299.0,
        "currency": "ZAR",
        "billing_frequency": BillingFrequency.MONTHLY,
        "start_date": NOW - timedelta(days=90),
        "current_period_start": NOW - timedelta(days=60),
        "current_period_end": NOW + timedelta(days=30),
        "idempotency_key": "term-policy-test",
        "subscription_id": "subscription-commercial",
        "plan_features": ("crm.core",),
        "plan_catalogue_version": 1,
        "status": SubscriptionStatus.ACTIVE,
        "seal_nonce": "term-policy-test-seal",
    }
    values.update(changes)
    return SubscriptionEntity(**values)


def _founder(**changes: object) -> SubscriptionEntity:
    values: dict[str, object] = {
        "tenant_id": "WILSYTENANT-4CD2FZ4O",
        "plan_id": "WILSYPLAN-37B8164F",
        "plan": PlanTiers.FREE,
        "amount": 0.0,
        "currency": "ZAR",
        "billing_frequency": BillingFrequency.MONTHLY,
        "start_date": NOW - timedelta(days=90),
        "current_period_start": NOW - timedelta(days=60),
        "current_period_end": NOW - timedelta(days=29),
        "idempotency_key": "founder-term-policy-test",
        "subscription_id": "WILSYSUB-93455E4E",
        "plan_features": ("tenant.branding",),
        "plan_catalogue_version": 1,
        "status": SubscriptionStatus.ACTIVE,
        "billing_mode": "PLATFORM",
        "seal_nonce": "founder-term-policy-test-seal",
    }
    values.update(changes)
    return SubscriptionEntity(**values)


def test_exact_founder_is_perpetual_after_period_end() -> None:
    result = evaluate_subscription_term(_founder(), evaluated_at=NOW)
    assert result.kind is SubscriptionTermKind.PERPETUAL_PLATFORM_OWNER
    assert result.eligible is True


def test_ordinary_active_commercial_subscription_expires_after_period_end() -> None:
    expired = _subscription(current_period_end=NOW - timedelta(seconds=1))
    result = evaluate_subscription_term(expired, evaluated_at=NOW)
    assert result.kind is SubscriptionTermKind.EXPIRED_BILLING_PERIOD
    assert result.eligible is False


def test_ordinary_active_commercial_subscription_is_eligible_within_period() -> None:
    result = evaluate_subscription_term(_subscription(), evaluated_at=NOW)
    assert result.kind is SubscriptionTermKind.BILLING_PERIOD
    assert result.eligible is True


@pytest.mark.parametrize(
    "changes",
    [
        {"tenant_id": "tenant-other"},
        {"subscription_id": "subscription-forged"},
        {"plan_id": "plan-forged"},
        {"amount": 1.0},
        {"billing_mode": "CLIENT"},
        {"status": SubscriptionStatus.PAUSED},
        {"cancel_at": NOW + timedelta(days=1)},
        {"cancelled_at": NOW - timedelta(days=1)},
        {"paused_at": NOW - timedelta(days=1)},
    ],
)
def test_founder_exception_requires_exact_live_binding_and_lifecycle(
    changes: dict[str, object],
) -> None:
    candidate = _founder(**changes)
    result = evaluate_subscription_term(candidate, evaluated_at=NOW)
    assert result.kind is not SubscriptionTermKind.PERPETUAL_PLATFORM_OWNER
    assert result.eligible is False


def test_client_metadata_and_tags_cannot_forge_founder_exception() -> None:
    ordinary = _subscription(
        current_period_end=NOW - timedelta(seconds=1),
        amount=0.0,
        billing_mode="PLATFORM",
        metadata={"system_owner": True, "perpetual": True},
        tags=["SOVEREIGN_SYSTEM_OWNER", "FOUNDER"],
    )
    result = evaluate_subscription_term(ordinary, evaluated_at=NOW)
    assert result.kind is SubscriptionTermKind.EXPIRED_BILLING_PERIOD
    assert result.eligible is False


def test_corrupt_subscription_proof_fails_closed() -> None:
    corrupted = replace(_founder(), proof_hash="f" * 128)
    with pytest.raises(SubscriptionTermPolicyError, match="INTEGRITY"):
        evaluate_subscription_term(corrupted, evaluated_at=NOW)


def test_naive_evaluation_time_fails_closed() -> None:
    with pytest.raises(SubscriptionTermPolicyError):
        evaluate_subscription_term(_founder(), evaluated_at=NOW.replace(tzinfo=None))


def test_founder_feature_snapshot_is_not_widened_by_term_policy() -> None:
    founder = _founder()
    assert founder.plan_features == ("tenant.branding",)
    result = evaluate_subscription_term(founder, evaluated_at=NOW)
    assert result.eligible is True
    assert founder.plan_features == ("tenant.branding",)


# ARTIFACT: tests/unit/test_subscription_term_policy.py
# VERSION: v1.0.0-D22C4-FOUNDER-PERPETUAL-TERM-POLICY-CERT
# AUTHORITY BOUNDARY: Pure subscription term decision tests; no persistence.
# TENANT POSTURE: Exact Founder tuple and synthetic ordinary tenant.
# FAIL-CLOSED POSTURE: Spoofed coordinates, terminal lifecycle and naive time reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
