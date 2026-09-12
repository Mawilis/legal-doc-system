"""WILSY OS — Direct certificate for recurring-revenue growth policy.

TITLE: M12-P7 Recurring-Revenue Growth Policy Direct Certificate
VERSION: v1.0.0-M12-P7-RECURRING-REVENUE-GROWTH-POLICY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exact integer growth classifications from two immutable P5
          recurring-revenue evidence snapshots.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_recurring_revenue_growth_policy.py
COLLABORATION / OWNERSHIP: Direct certificate for recurring_revenue_growth_policy.py;
                           no persistence, HTTP, provider, invoice, or execution owner.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M12-P7 certifies growth arithmetic, zero-baseline policy,
           source integrity, tenant/currency binding, and immutable output.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Fixtures contain no secrets and contact no systems.
TENANT BOUNDARY: Every fixture uses an explicit non-global tenant.
AUTHORITY BOUNDARY: Test evidence only; no authorization, execution, settlement,
                    paid-state, invoice, or receivable authority is created.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive execution and
                               settlement authority.
"""
from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.saas.billing.recurring_revenue_growth_policy import (
    GrowthClassification,
    RecurringRevenueGrowthEvidence,
    RecurringRevenueGrowthPolicyError,
    derive_recurring_revenue_growth,
)
from tools.eos.saas.billing.recurring_revenue_policy import RecurringRevenueEvidence, derive_recurring_revenue
from tools.eos.saas.domain.subscription import BillingFrequency, PlanTiers, SubscriptionEntity, SubscriptionStatus


BASE = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)


def _subscription(*, tenant_id: str = "tenant-growth", amount: float = 100.0, currency: str = "ZAR", subscription_id: str = "sub-growth") -> SubscriptionEntity:
    return SubscriptionEntity(
        tenant_id=tenant_id,
        plan_id=f"plan-{subscription_id}",
        plan=PlanTiers.BASIC,
        amount=amount,
        currency=currency,
        billing_frequency=BillingFrequency.MONTHLY,
        start_date=BASE - timedelta(days=1),
        current_period_start=BASE,
        current_period_end=BASE + timedelta(days=30),
        idempotency_key=f"idem-{subscription_id}",
        subscription_id=subscription_id,
        status=SubscriptionStatus.ACTIVE,
    )


def _snapshot(*, as_of: datetime, amount: float | None, tenant_id: str = "tenant-growth", currency: str = "ZAR"):
    if amount is None:
        return RecurringRevenueEvidence(
            tenant_id=tenant_id,
            as_of=as_of,
            currency=currency,
            qualifying_subscription_count=0,
            mrr_minor=0,
            arr_minor=0,
            sources=(),
        )
    subscriptions = (_subscription(tenant_id=tenant_id, amount=amount, currency=currency),)
    return derive_recurring_revenue(tenant_id=tenant_id, as_of=as_of, subscriptions=subscriptions)


def test_positive_growth_uses_exact_signed_minor_unit_ratio() -> None:
    result = derive_recurring_revenue_growth(prior=_snapshot(as_of=BASE, amount=100.0), current=_snapshot(as_of=BASE + timedelta(days=1), amount=125.0))
    assert (result.classification, result.delta_mrr_minor, result.growth_numerator, result.growth_denominator) == (GrowthClassification.POSITIVE, 2500, 2500, 10000)


def test_contraction_is_negative_without_rounding() -> None:
    result = derive_recurring_revenue_growth(prior=_snapshot(as_of=BASE, amount=125.0), current=_snapshot(as_of=BASE + timedelta(days=1), amount=100.0))
    assert (result.classification, result.delta_mrr_minor, result.growth_numerator, result.growth_denominator) == (GrowthClassification.CONTRACTION, -2500, -2500, 12500)


def test_no_change_has_zero_exact_numerator() -> None:
    result = derive_recurring_revenue_growth(prior=_snapshot(as_of=BASE, amount=100.0), current=_snapshot(as_of=BASE + timedelta(days=1), amount=100.0))
    assert (result.classification, result.delta_mrr_minor, result.growth_numerator, result.growth_denominator) == (GrowthClassification.NO_CHANGE, 0, 0, 10000)


def test_zero_to_zero_has_no_rate() -> None:
    result = derive_recurring_revenue_growth(prior=_snapshot(as_of=BASE, amount=None), current=_snapshot(as_of=BASE + timedelta(days=1), amount=None))
    assert (result.classification, result.currency, result.growth_numerator, result.growth_denominator) == (GrowthClassification.NO_CHANGE, "ZAR", None, None)


def test_zero_to_positive_is_explicitly_undefined_rate() -> None:
    result = derive_recurring_revenue_growth(prior=_snapshot(as_of=BASE, amount=None), current=_snapshot(as_of=BASE + timedelta(days=1), amount=100.0))
    assert (result.classification, result.currency, result.growth_numerator, result.growth_denominator) == (GrowthClassification.RATE_UNDEFINED_ZERO_BASELINE, "ZAR", None, None)


def test_tenant_mismatch_rejects() -> None:
    with pytest.raises(RecurringRevenueGrowthPolicyError, match="TENANT_MISMATCH"):
        derive_recurring_revenue_growth(prior=_snapshot(as_of=BASE, amount=100.0), current=_snapshot(as_of=BASE + timedelta(days=1), amount=125.0, tenant_id="tenant-other"))


def test_currency_mismatch_rejects() -> None:
    with pytest.raises(RecurringRevenueGrowthPolicyError, match="CURRENCY_MISMATCH"):
        derive_recurring_revenue_growth(prior=_snapshot(as_of=BASE, amount=100.0, currency="ZAR"), current=_snapshot(as_of=BASE + timedelta(days=1), amount=125.0, currency="USD"))


def test_missing_currency_rejects_even_for_zero_baseline() -> None:
    missing = derive_recurring_revenue(tenant_id="tenant-growth", as_of=BASE, subscriptions=())
    with pytest.raises(RecurringRevenueGrowthPolicyError, match="CURRENCY_REQUIRED"):
        derive_recurring_revenue_growth(prior=missing, current=_snapshot(as_of=BASE + timedelta(days=1), amount=None))


def test_reversed_and_same_snapshots_reject() -> None:
    with pytest.raises(RecurringRevenueGrowthPolicyError, match="AS_OF_ORDER_INVALID"):
        derive_recurring_revenue_growth(prior=_snapshot(as_of=BASE + timedelta(days=1), amount=100.0), current=_snapshot(as_of=BASE, amount=125.0))
    with pytest.raises(RecurringRevenueGrowthPolicyError, match="AS_OF_ORDER_INVALID"):
        derive_recurring_revenue_growth(prior=_snapshot(as_of=BASE, amount=100.0), current=_snapshot(as_of=BASE, amount=125.0))


def test_identical_snapshot_fingerprint_rejects_even_when_reused() -> None:
    snapshot = _snapshot(as_of=BASE, amount=100.0)
    with pytest.raises(RecurringRevenueGrowthPolicyError, match="SNAPSHOTS_NOT_DISTINCT"):
        derive_recurring_revenue_growth(prior=snapshot, current=snapshot)


def test_corrupt_source_fingerprint_rejects() -> None:
    corrupt = _snapshot(as_of=BASE, amount=100.0)
    object.__setattr__(corrupt, "fingerprint", "0" * 128)
    with pytest.raises(RecurringRevenueGrowthPolicyError, match="SOURCE_EVIDENCE_CORRUPT"):
        derive_recurring_revenue_growth(prior=corrupt, current=_snapshot(as_of=BASE + timedelta(days=1), amount=125.0))


def test_source_mutation_changes_source_and_growth_fingerprints() -> None:
    first = derive_recurring_revenue_growth(prior=_snapshot(as_of=BASE, amount=100.0), current=_snapshot(as_of=BASE + timedelta(days=1), amount=125.0))
    second = derive_recurring_revenue_growth(prior=_snapshot(as_of=BASE, amount=101.0), current=_snapshot(as_of=BASE + timedelta(days=1), amount=125.0))
    assert first.prior_source_fingerprint != second.prior_source_fingerprint
    assert first.fingerprint != second.fingerprint


def test_output_is_immutable_detached_and_deterministic() -> None:
    prior, current = _snapshot(as_of=BASE, amount=100.0), _snapshot(as_of=BASE + timedelta(days=1), amount=125.0)
    first = derive_recurring_revenue_growth(prior=prior, current=current)
    second = derive_recurring_revenue_growth(prior=prior, current=current)
    assert first == second and first.fingerprint == first.growth_fingerprint
    detached = first.to_dict()
    detached["delta_mrr_minor"] = 0
    assert first.delta_mrr_minor == 2500
    with pytest.raises(FrozenInstanceError):
        first.delta_mrr_minor = 0  # type: ignore[misc]


def test_invalid_aware_source_and_contract_fail_closed() -> None:
    corrupt = _snapshot(as_of=BASE, amount=100.0)
    object.__setattr__(corrupt, "as_of", datetime(2026, 9, 1, 12))
    with pytest.raises(RecurringRevenueGrowthPolicyError, match="SOURCE_EVIDENCE_CORRUPT"):
        derive_recurring_revenue_growth(prior=corrupt, current=_snapshot(as_of=BASE + timedelta(days=1), amount=125.0))


def test_growth_output_rejects_invalid_contract_and_rate_shape() -> None:
    with pytest.raises(RecurringRevenueGrowthPolicyError, match="EVIDENCE_CONTRACT_INVALID"):
        RecurringRevenueGrowthEvidence(
            tenant_id="tenant-growth",
            prior_as_of=BASE,
            current_as_of=BASE + timedelta(days=1),
            currency="ZAR",
            prior_source_fingerprint="0" * 128,
            current_source_fingerprint="1" * 128,
            prior_mrr_minor=0,
            current_mrr_minor=0,
            delta_mrr_minor=0,
            growth_numerator=None,
            growth_denominator=None,
            classification=GrowthClassification.NO_CHANGE,
            evidence_contract="wrong",
        )


def test_no_persistence_http_or_financial_execution_authority() -> None:
    source = inspect.getsource(derive_recurring_revenue_growth)
    module = inspect.getsource(__import__("tools.eos.saas.billing.recurring_revenue_growth_policy", fromlist=["*"]))
    assert all(token not in module for token in ("pymongo", "MongoClient", "requests", "httpx", "fastapi"))
    assert all(token not in source for token in ("save", "execute", "settle", "invoice", "receivable"))


# ARTIFACT: test_recurring_revenue_growth_policy.py
# VERSION: v1.0.0-M12-P7-RECURRING-REVENUE-GROWTH-POLICY
# AUTHORITY BOUNDARY: direct verification of derived intelligence only
# TENANT POSTURE: explicit tenant-scoped fixtures; mismatch rejects
# FAIL-CLOSED POSTURE: exact arithmetic, source seals, and closed classifications
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
