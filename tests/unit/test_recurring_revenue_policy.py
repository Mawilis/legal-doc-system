"""WILSY OS — Direct certificate for canonical recurring-revenue policy.

TITLE: M12-P5 Recurring Revenue Policy Direct Certificate
VERSION: v1.0.0-M12-P5-RECURRING-REVENUE-POLICY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove deterministic tenant-scoped MRR/ARR policy behavior using only
          already-hydrated canonical SubscriptionEntity values.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_recurring_revenue_policy.py
COLLABORATION / OWNERSHIP: Direct certificate for recurring_revenue_policy.py;
                           no persistence, HTTP, provider, or execution owner.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M12-P5 certifies lifecycle, money, currency, provenance,
           determinism, immutability, and fail-closed policy boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Fixtures contain no secrets or external contacts.
TENANT BOUNDARY: Every fixture and assertion uses explicit tenant scope.
AUTHORITY BOUNDARY: Test evidence only; no business, payment, execution, or
                    settlement authority is created by this module.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive execution and
                               settlement authority.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.saas.billing.recurring_revenue_policy import (
    RecurringRevenuePolicyError,
    derive_recurring_revenue,
)
from tools.eos.saas.domain.subscription import (
    BillingFrequency,
    PlanTiers,
    SubscriptionEntity,
    SubscriptionStatus,
)


NOW = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)


def subscription(
    subscription_id: str = "sub-a",
    *,
    tenant_id: str = "tenant-a",
    amount: float = 120.0,
    frequency: BillingFrequency = BillingFrequency.MONTHLY,
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
    start_date: datetime = NOW - timedelta(days=1),
    **kwargs: Any,
) -> SubscriptionEntity:
    return SubscriptionEntity(
        tenant_id=tenant_id,
        plan_id=f"plan-{subscription_id}",
        plan=PlanTiers.BASIC,
        amount=amount,
        currency="ZAR",
        billing_frequency=frequency,
        start_date=start_date,
        current_period_start=NOW.replace(day=1),
        current_period_end=NOW.replace(day=1, month=10),
        idempotency_key=f"idem-{subscription_id}",
        subscription_id=subscription_id,
        status=status,
        **kwargs,
    )


def test_explicit_tenant_required() -> None:
    with pytest.raises(RecurringRevenuePolicyError):
        derive_recurring_revenue(tenant_id="", as_of=NOW, subscriptions=())


def test_explicit_aware_as_of_required() -> None:
    with pytest.raises(RecurringRevenuePolicyError):
        derive_recurring_revenue(tenant_id="tenant-a", as_of=datetime(2026, 9, 12), subscriptions=())


def test_empty_lawful_set_is_deterministic_zero_without_currency_default() -> None:
    first = derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=())
    second = derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=())
    assert (first.mrr_minor, first.arr_minor, first.currency, first.fingerprint) == (0, 0, None, second.fingerprint)


def test_one_monthly_subscription_exact_mrr_arr() -> None:
    result = derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(subscription(amount=120.0),))
    assert (result.mrr_minor, result.arr_minor, result.currency, result.qualifying_subscription_count) == (12000, 144000, "ZAR", 1)


def test_multiple_subscriptions_aggregate() -> None:
    result = derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(subscription("a", amount=100.0), subscription("b", amount=25.0)))
    assert (result.mrr_minor, result.arr_minor) == (12500, 150000)


def test_source_order_invariance() -> None:
    a, b = subscription("a", amount=100.0), subscription("b", amount=25.0)
    assert derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(a, b)).fingerprint == derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(b, a)).fingerprint


def test_duplicate_source_rejected() -> None:
    value = subscription()
    with pytest.raises(RecurringRevenuePolicyError):
        derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(value, value))


def test_mixed_tenant_rejected() -> None:
    with pytest.raises(RecurringRevenuePolicyError):
        derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(subscription(), subscription("b", tenant_id="tenant-b")))


def test_future_and_ended_sources_excluded() -> None:
    future = subscription("future", start_date=NOW + timedelta(days=1))
    ended = subscription("ended", end_date=NOW)
    result = derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(future, ended))
    assert result.qualifying_subscription_count == 0 and result.mrr_minor == 0


def test_future_cancellation_remains_qualifying_until_effective() -> None:
    value = subscription(cancel_at=NOW + timedelta(days=1))
    result = derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(value,))
    assert result.qualifying_subscription_count == 1


@pytest.mark.parametrize(
    ("frequency", "amount", "expected_mrr", "expected_arr"),
    [(BillingFrequency.MONTHLY, 100.0, 10000, 120000), (BillingFrequency.QUARTERLY, 300.0, 10000, 120000), (BillingFrequency.ANNUAL, 1200.0, 10000, 120000)],
)
def test_exact_interval_normalization(frequency: BillingFrequency, amount: float, expected_mrr: int, expected_arr: int) -> None:
    result = derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(subscription(frequency=frequency, amount=amount),))
    assert (result.mrr_minor, result.arr_minor) == (expected_mrr, expected_arr)


def test_mixed_currency_fails_closed() -> None:
    usd = replace(subscription("usd"), currency="USD")
    with pytest.raises(RecurringRevenuePolicyError):
        derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(subscription(), usd))


def test_exact_source_provenance_preserved() -> None:
    source = subscription("source-1")
    result = derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(source,))
    assert result.sources[0].subscription_id == source.subscription_id
    assert result.sources[0].subscription_fingerprint == source.proof_hash.lower()
    assert result.sources[0].plan_id == source.plan_id


def test_material_source_mutation_changes_fingerprint() -> None:
    first = derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(subscription(amount=120.0),))
    second = derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(replace(subscription(), amount=121.0),))
    assert first.fingerprint != second.fingerprint


def test_trial_and_pause_cancel_states_do_not_qualify() -> None:
    trial = subscription("trial", status=SubscriptionStatus.TRIAL, trial_end_date=NOW + timedelta(days=3))
    paused = subscription("paused", status=SubscriptionStatus.PAUSED)
    cancelled = subscription("cancelled", cancel_at=NOW)
    result = derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(trial, paused, cancelled))
    assert result.qualifying_subscription_count == 0


def test_inexact_minor_unit_interval_fails_closed() -> None:
    with pytest.raises(RecurringRevenuePolicyError):
        derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(subscription(frequency=BillingFrequency.QUARTERLY, amount=100.01),))


def test_unsupported_source_and_adjustment_fail_closed() -> None:
    with pytest.raises(RecurringRevenuePolicyError):
        derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(object(),))  # type: ignore[arg-type]
    with pytest.raises(RecurringRevenuePolicyError):
        derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(subscription(credit_balance=1.0),))
    with pytest.raises(RecurringRevenuePolicyError):
        derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(subscription(metadata={"discount": 1}),))


def test_policy_is_immutable_and_has_no_execution_or_persistence_authority() -> None:
    result = derive_recurring_revenue(tenant_id="tenant-a", as_of=NOW, subscriptions=(subscription(),))
    with pytest.raises((AttributeError, TypeError)):
        result.mrr_minor = 1  # type: ignore[misc]
    assert not hasattr(result, "save") and not hasattr(result, "execute") and not hasattr(result, "settle")


# ARTIFACT: test_recurring_revenue_policy.py
# VERSION: v1.0.0-M12-P5-RECURRING-REVENUE-POLICY
# AUTHORITY BOUNDARY: direct verification of deterministic intelligence policy only
# TENANT POSTURE: explicit tenant-scoped fixtures; mixed tenants fail closed
# FAIL-CLOSED POSTURE: assertions require exact money, lifecycle and provenance behavior
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
