"""WILSY OS — Canonical recurring-revenue intelligence policy.

TITLE: Canonical Python MRR / ARR Policy Owner
VERSION: v1.0.0-M12-P5-RECURRING-REVENUE-POLICY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Derive deterministic, tenant-scoped recurring-revenue evidence from
          already-hydrated canonical SubscriptionEntity obligations.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/recurring_revenue_policy.py
COLLABORATION / OWNERSHIP: Python EOS owns policy and evidence semantics;
                           SubscriptionRegistry owns durable subscriptions;
                           PlanEntity/PlanRegistry own catalogue truth.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M12-P5 establishes an immutable pure MRR/ARR policy owner;
           P6 may wire this owner into BillingIntelligenceEngine.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No persistence, network, secret, KMS, provider,
                            payment, or client access occurs here.
TENANT BOUNDARY: Every source is explicitly bound to one non-global tenant.
AUTHORITY BOUNDARY: Business-intelligence evidence only; no authorization,
                    execution, settlement, paid-state, or receivable truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and
                               settlement; this policy never creates either.
FAIL-CLOSED DECLARATION: Ambiguous lifecycle, money, currency, provenance,
                         interval, duplicate, or unsupported adjustments reject.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Final, Iterable

from ..domain.money import MoneyPrecisionError, to_minor_units
from ..domain.subscription import BillingFrequency, SubscriptionEntity, SubscriptionStatus


VERSION: Final[str] = "v1.0.0-M12-P5-RECURRING-REVENUE-POLICY"
EVIDENCE_CONTRACT: Final[str] = "WILSY-RECURRING-REVENUE-EVIDENCE/V1"
_HEX128 = re.compile(r"^[0-9a-fA-F]{128}$")
_GLOBAL_TENANTS = frozenset({"", "*", "global", "platform", "root", "system"})
_SUPPORTED_FREQUENCIES = frozenset(
    {BillingFrequency.MONTHLY, BillingFrequency.QUARTERLY, BillingFrequency.ANNUAL}
)
_UNSUPPORTED_METADATA_KEYS = frozenset(
    {"discount", "discounts", "credit", "credits", "quantity", "seats", "units", "usage", "outcome", "hybrid", "proration"}
)


class RecurringRevenuePolicyError(ValueError):
    """Raised when recurring-revenue evidence cannot be proven exactly."""


def _tenant(value: object) -> str:
    if not isinstance(value, str):
        raise RecurringRevenuePolicyError("M12P5_TENANT_REQUIRED")
    value = value.strip()
    if not value or value.casefold() in _GLOBAL_TENANTS:
        raise RecurringRevenuePolicyError("M12P5_TENANT_INVALID")
    return value


def _as_of(value: object) -> datetime:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise RecurringRevenuePolicyError("M12P5_AS_OF_AWARE_REQUIRED")
    return value.astimezone(timezone.utc)


def _source_fingerprint(source: SubscriptionEntity) -> str:
    proof = source.proof_hash
    if not isinstance(proof, str) or _HEX128.fullmatch(proof) is None:
        raise RecurringRevenuePolicyError("M12P5_SOURCE_PROOF_INVALID")
    return proof.lower()


def _money_minor(source: SubscriptionEntity) -> int:
    try:
        value = to_minor_units(source.amount, source.currency)
    except (MoneyPrecisionError, TypeError, ValueError) as exc:
        raise RecurringRevenuePolicyError("M12P5_SOURCE_MONEY_INVALID") from exc
    if isinstance(source.amount, float) and not math.isfinite(source.amount):
        raise RecurringRevenuePolicyError("M12P5_SOURCE_MONEY_INVALID")
    return value


def _interval_amounts(amount_minor: int, frequency: BillingFrequency) -> tuple[int, int]:
    """Return exact MRR/ARR; no fractional minor unit or calendar approximation."""
    if frequency not in _SUPPORTED_FREQUENCIES:
        raise RecurringRevenuePolicyError("M12P5_INTERVAL_UNSUPPORTED")
    if frequency is BillingFrequency.MONTHLY:
        return amount_minor, amount_minor * 12
    divisor, multiplier = (3, 4) if frequency is BillingFrequency.QUARTERLY else (12, 1)
    if amount_minor % divisor:
        raise RecurringRevenuePolicyError("M12P5_INTERVAL_NOT_EXACT_IN_MINOR_UNITS")
    return amount_minor // divisor, amount_minor * multiplier


@dataclass(frozen=True, slots=True)
class RecurringRevenueSource:
    """Immutable provenance for one qualifying subscription obligation."""

    subscription_id: str
    subscription_fingerprint: str
    plan_id: str
    plan_catalogue_version: int | None
    amount_minor: int
    billing_frequency: str

    def __post_init__(self) -> None:
        if not isinstance(self.subscription_id, str) or not self.subscription_id.strip():
            raise RecurringRevenuePolicyError("M12P5_SOURCE_ID_INVALID")
        if _HEX128.fullmatch(self.subscription_fingerprint) is None:
            raise RecurringRevenuePolicyError("M12P5_SOURCE_PROOF_INVALID")
        if not isinstance(self.plan_id, str) or not self.plan_id.strip():
            raise RecurringRevenuePolicyError("M12P5_PLAN_ID_INVALID")
        if isinstance(self.amount_minor, bool) or not isinstance(self.amount_minor, int) or self.amount_minor < 0:
            raise RecurringRevenuePolicyError("M12P5_SOURCE_MONEY_INVALID")
        if self.plan_catalogue_version is not None and (
            isinstance(self.plan_catalogue_version, bool)
            or not isinstance(self.plan_catalogue_version, int)
            or self.plan_catalogue_version < 1
        ):
            raise RecurringRevenuePolicyError("M12P5_PLAN_VERSION_INVALID")

    def to_payload(self) -> dict[str, object]:
        return {
            "subscription_id": self.subscription_id,
            "subscription_fingerprint": self.subscription_fingerprint.lower(),
            "plan_id": self.plan_id,
            "plan_catalogue_version": self.plan_catalogue_version,
            "amount_minor": self.amount_minor,
            "billing_frequency": self.billing_frequency,
        }


@dataclass(frozen=True, slots=True)
class RecurringRevenueEvidence:
    """Immutable tenant/snapshot MRR and ARR evidence with deterministic seal."""

    tenant_id: str
    as_of: datetime
    currency: str | None
    qualifying_subscription_count: int
    mrr_minor: int
    arr_minor: int
    sources: tuple[RecurringRevenueSource, ...] = field(default_factory=tuple)
    evidence_contract: str = EVIDENCE_CONTRACT
    fingerprint: str = field(default="", compare=True)

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        observed = _as_of(self.as_of)
        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "as_of", observed)
        if self.currency is not None and (not isinstance(self.currency, str) or not re.fullmatch(r"[A-Z]{3}", self.currency)):
            raise RecurringRevenuePolicyError("M12P5_CURRENCY_INVALID")
        if any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in (self.qualifying_subscription_count, self.mrr_minor, self.arr_minor)):
            raise RecurringRevenuePolicyError("M12P5_EVIDENCE_TOTAL_INVALID")
        ordered = tuple(self.sources)
        if ordered != tuple(sorted(ordered, key=lambda item: item.subscription_id)):
            raise RecurringRevenuePolicyError("M12P5_SOURCE_ORDER_INVALID")
        object.__setattr__(self, "sources", ordered)
        payload = self._payload()
        digest = hashlib.sha3_512(
            json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if self.fingerprint and self.fingerprint != digest:
            raise RecurringRevenuePolicyError("M12P5_EVIDENCE_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def _payload(self) -> dict[str, object]:
        return {
            "evidence_contract": self.evidence_contract,
            "tenant_id": self.tenant_id,
            "as_of": self.as_of.isoformat(),
            "currency": self.currency,
            "qualifying_subscription_count": self.qualifying_subscription_count,
            "mrr_minor": self.mrr_minor,
            "arr_minor": self.arr_minor,
            "sources": [item.to_payload() for item in self.sources],
        }

    def to_dict(self) -> dict[str, object]:
        """Return a detached canonical evidence representation."""
        return {**self._payload(), "fingerprint": self.fingerprint}


def derive_recurring_revenue(
    *, tenant_id: str, as_of: datetime, subscriptions: Iterable[SubscriptionEntity]
) -> RecurringRevenueEvidence:
    """Derive exact MRR/ARR from canonical subscription obligations at ``as_of``.

    Active obligations qualify only after start and before effective end or
    cancellation. Trial/paused/past-due/cancelled/expired states are excluded;
    unsupported credits, proration, non-subscription sources and inexact minor
    unit normalization fail closed. Inputs are never persisted or mutated.
    """
    tenant = _tenant(tenant_id)
    observed = _as_of(as_of)
    values = tuple(subscriptions)
    seen: set[str] = set()
    qualifying: list[RecurringRevenueSource] = []
    currency: str | None = None
    mrr = 0
    arr = 0
    for source in values:
        if not isinstance(source, SubscriptionEntity):
            raise RecurringRevenuePolicyError("M12P5_SOURCE_TYPE_UNSUPPORTED")
        if source.tenant_id != tenant:
            raise RecurringRevenuePolicyError("M12P5_MIXED_TENANT")
        if source.subscription_id in seen:
            raise RecurringRevenuePolicyError("M12P5_DUPLICATE_SOURCE")
        seen.add(source.subscription_id)
        if source.credit_balance != 0 or source.proration_log:
            raise RecurringRevenuePolicyError("M12P5_ADJUSTMENT_UNSUPPORTED")
        if any(str(key).casefold() in _UNSUPPORTED_METADATA_KEYS for key in source.metadata):
            raise RecurringRevenuePolicyError("M12P5_ADJUSTMENT_UNSUPPORTED")
        if source.start_date > observed or (source.end_date is not None and source.end_date <= observed):
            continue
        if source.cancel_at is not None and source.cancel_at <= observed:
            continue
        if source.trial_end_date is not None and observed < source.trial_end_date:
            continue
        if source.status is not SubscriptionStatus.ACTIVE:
            continue
        amount_minor = _money_minor(source)
        source_currency = source.currency
        if currency is None:
            currency = source_currency
        elif source_currency != currency:
            raise RecurringRevenuePolicyError("M12P5_MIXED_CURRENCY")
        source_mrr, source_arr = _interval_amounts(amount_minor, source.billing_frequency)
        mrr += source_mrr
        arr += source_arr
        qualifying.append(
            RecurringRevenueSource(
                subscription_id=source.subscription_id,
                subscription_fingerprint=_source_fingerprint(source),
                plan_id=source.plan_id,
                plan_catalogue_version=source.plan_catalogue_version,
                amount_minor=amount_minor,
                billing_frequency=source.billing_frequency.value,
            )
        )
    ordered = tuple(sorted(qualifying, key=lambda item: item.subscription_id))
    return RecurringRevenueEvidence(
        tenant_id=tenant,
        as_of=observed,
        currency=currency,
        qualifying_subscription_count=len(ordered),
        mrr_minor=mrr,
        arr_minor=arr,
        sources=ordered,
    )


__all__ = [
    "EVIDENCE_CONTRACT",
    "RecurringRevenueEvidence",
    "RecurringRevenuePolicyError",
    "RecurringRevenueSource",
    "VERSION",
    "derive_recurring_revenue",
]


# ARTIFACT: recurring_revenue_policy.py
# VERSION: v1.0.0-M12-P5-RECURRING-REVENUE-POLICY
# AUTHORITY BOUNDARY: deterministic MRR/ARR intelligence evidence only
# TENANT POSTURE: explicit non-global tenant scope; mixed tenants fail closed
# FAIL-CLOSED POSTURE: unsupported adjustments, currencies, intervals and provenance reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
