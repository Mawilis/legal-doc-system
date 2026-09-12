"""WILSY OS — Canonical recurring-revenue growth intelligence policy.

TITLE: Canonical Python Recurring-Revenue Growth Policy
VERSION: v1.0.0-M12-P7-RECURRING-REVENUE-GROWTH-POLICY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Derive an exact, tenant-scoped growth classification from two
          already-certified recurring-revenue evidence snapshots.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/recurring_revenue_growth_policy.py
COLLABORATION / OWNERSHIP: Python EOS owns pure growth derivation and its
                           immutable evidence; P5 owns source MRR evidence;
                           P8 may consume this as derived intelligence.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M12-P7 establishes exact integer growth arithmetic,
           zero-baseline classifications, tenant/currency binding, and a
           deterministic SHA3-512 evidence seal.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No persistence, network, secret, KMS, provider,
                            HTTP, invoice, or external-client access occurs.
TENANT BOUNDARY: Prior and current snapshots must identify one exact tenant.
AUTHORITY BOUNDARY: Derived business-intelligence evidence only; no approval,
                    execution, settlement, paid-state, or receivable truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and
                               settlement; this policy never creates either.
FAIL-CLOSED DECLARATION: Corrupt evidence, unsupported currency, mismatched
                         snapshots, invalid time ordering, and ambiguous
                         zero-baseline rates reject or classify explicitly.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Final

from ..domain.money import SUPPORTED_CURRENCY_EXPONENTS
from .recurring_revenue_policy import (
    EVIDENCE_CONTRACT as RECURRING_REVENUE_EVIDENCE_CONTRACT,
    RecurringRevenueEvidence,
)


VERSION: Final[str] = "v1.0.0-M12-P7-RECURRING-REVENUE-GROWTH-POLICY"
EVIDENCE_CONTRACT: Final[str] = "WILSY-RECURRING-REVENUE-GROWTH-EVIDENCE/V1"
_HEX128 = re.compile(r"^[0-9a-f]{128}$")
_GLOBAL_TENANTS = frozenset({"", "*", "global", "platform", "root", "system"})


class RecurringRevenueGrowthPolicyError(ValueError):
    """Raised when growth cannot be derived from valid certified evidence."""


class GrowthClassification(str, Enum):
    """Closed classifications for exact MRR movement."""

    POSITIVE = "POSITIVE"
    CONTRACTION = "CONTRACTION"
    NO_CHANGE = "NO_CHANGE"
    RATE_UNDEFINED_ZERO_BASELINE = "RATE_UNDEFINED_ZERO_BASELINE"


def _aware_utc(value: object, code: str) -> datetime:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise RecurringRevenueGrowthPolicyError(code)
    return value.astimezone(timezone.utc)


def _snapshot_fingerprint(snapshot: RecurringRevenueEvidence) -> str:
    """Recompute the P5 seal so a forged in-memory snapshot cannot be used."""
    try:
        payload = snapshot.to_dict()
        supplied = payload.pop("fingerprint")
        canonical = json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise RecurringRevenueGrowthPolicyError("M12P7_SOURCE_EVIDENCE_CORRUPT") from exc
    digest = hashlib.sha3_512(canonical).hexdigest()
    if not isinstance(supplied, str) or _HEX128.fullmatch(supplied) is None or supplied != digest:
        raise RecurringRevenueGrowthPolicyError("M12P7_SOURCE_EVIDENCE_CORRUPT")
    return digest


def _validate_snapshot(value: object) -> tuple[RecurringRevenueEvidence, str, datetime]:
    if not isinstance(value, RecurringRevenueEvidence):
        raise RecurringRevenueGrowthPolicyError("M12P7_SOURCE_EVIDENCE_REQUIRED")
    if value.evidence_contract != RECURRING_REVENUE_EVIDENCE_CONTRACT:
        raise RecurringRevenueGrowthPolicyError("M12P7_SOURCE_CONTRACT_UNSUPPORTED")
    fingerprint = _snapshot_fingerprint(value)
    observed = _aware_utc(value.as_of, "M12P7_SOURCE_AS_OF_AWARE_REQUIRED")
    if value.currency is not None and value.currency not in SUPPORTED_CURRENCY_EXPONENTS:
        raise RecurringRevenueGrowthPolicyError("M12P7_SOURCE_CURRENCY_UNSUPPORTED")
    if isinstance(value.mrr_minor, bool) or not isinstance(value.mrr_minor, int) or value.mrr_minor < 0:
        raise RecurringRevenueGrowthPolicyError("M12P7_SOURCE_MRR_INVALID")
    return value, fingerprint, observed


def _canonical_payload(
    *,
    tenant_id: str,
    prior_as_of: datetime,
    current_as_of: datetime,
    currency: str | None,
    prior_source_fingerprint: str,
    current_source_fingerprint: str,
    prior_mrr_minor: int,
    current_mrr_minor: int,
    delta_mrr_minor: int,
    growth_numerator: int | None,
    growth_denominator: int | None,
    classification: GrowthClassification,
) -> dict[str, object]:
    return {
        "evidence_contract": EVIDENCE_CONTRACT,
        "tenant_id": tenant_id,
        "prior_as_of": prior_as_of.isoformat(),
        "current_as_of": current_as_of.isoformat(),
        "currency": currency,
        "prior_source_fingerprint": prior_source_fingerprint,
        "current_source_fingerprint": current_source_fingerprint,
        "prior_mrr_minor": prior_mrr_minor,
        "current_mrr_minor": current_mrr_minor,
        "delta_mrr_minor": delta_mrr_minor,
        "growth_numerator": growth_numerator,
        "growth_denominator": growth_denominator,
        "classification": classification.value,
    }


@dataclass(frozen=True, slots=True)
class RecurringRevenueGrowthEvidence:
    """Immutable exact growth evidence sealed independently from its inputs."""

    tenant_id: str
    prior_as_of: datetime
    current_as_of: datetime
    currency: str | None
    prior_source_fingerprint: str
    current_source_fingerprint: str
    prior_mrr_minor: int
    current_mrr_minor: int
    delta_mrr_minor: int
    growth_numerator: int | None
    growth_denominator: int | None
    classification: GrowthClassification
    evidence_contract: str = EVIDENCE_CONTRACT
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_contract, str) or self.evidence_contract != EVIDENCE_CONTRACT:
            raise RecurringRevenueGrowthPolicyError("M12P7_EVIDENCE_CONTRACT_INVALID")
        if not isinstance(self.tenant_id, str) or not self.tenant_id.strip() or self.tenant_id.casefold() in _GLOBAL_TENANTS:
            raise RecurringRevenueGrowthPolicyError("M12P7_TENANT_INVALID")
        prior = _aware_utc(self.prior_as_of, "M12P7_PRIOR_AS_OF_AWARE_REQUIRED")
        current = _aware_utc(self.current_as_of, "M12P7_CURRENT_AS_OF_AWARE_REQUIRED")
        if current <= prior:
            raise RecurringRevenueGrowthPolicyError("M12P7_AS_OF_ORDER_INVALID")
        if self.currency is not None and self.currency not in SUPPORTED_CURRENCY_EXPONENTS:
            raise RecurringRevenueGrowthPolicyError("M12P7_CURRENCY_UNSUPPORTED")
        for value in (self.prior_mrr_minor, self.current_mrr_minor, self.delta_mrr_minor):
            if isinstance(value, bool) or not isinstance(value, int):
                raise RecurringRevenueGrowthPolicyError("M12P7_MRR_INTEGER_REQUIRED")
        if self.prior_mrr_minor < 0 or self.current_mrr_minor < 0:
            raise RecurringRevenueGrowthPolicyError("M12P7_MRR_NONNEGATIVE_REQUIRED")
        if self.delta_mrr_minor != self.current_mrr_minor - self.prior_mrr_minor:
            raise RecurringRevenueGrowthPolicyError("M12P7_DELTA_MISMATCH")
        if not isinstance(self.classification, GrowthClassification):
            raise RecurringRevenueGrowthPolicyError("M12P7_CLASSIFICATION_INVALID")
        for value in (self.growth_numerator, self.growth_denominator):
            if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
                raise RecurringRevenueGrowthPolicyError("M12P7_RATE_INTEGER_REQUIRED")
        if self.prior_mrr_minor == 0:
            expected = (
                GrowthClassification.NO_CHANGE
                if self.current_mrr_minor == 0
                else GrowthClassification.RATE_UNDEFINED_ZERO_BASELINE
            )
            if self.classification is not expected or self.growth_numerator is not None or self.growth_denominator is not None:
                raise RecurringRevenueGrowthPolicyError("M12P7_ZERO_BASELINE_RATE_INVALID")
        else:
            expected = (
                GrowthClassification.POSITIVE
                if self.delta_mrr_minor > 0
                else GrowthClassification.CONTRACTION
                if self.delta_mrr_minor < 0
                else GrowthClassification.NO_CHANGE
            )
            if self.classification is not expected or self.growth_numerator != self.delta_mrr_minor or self.growth_denominator != self.prior_mrr_minor:
                raise RecurringRevenueGrowthPolicyError("M12P7_RATE_MISMATCH")
        if not isinstance(self.prior_source_fingerprint, str) or _HEX128.fullmatch(self.prior_source_fingerprint) is None:
            raise RecurringRevenueGrowthPolicyError("M12P7_PRIOR_SOURCE_FINGERPRINT_INVALID")
        if not isinstance(self.current_source_fingerprint, str) or _HEX128.fullmatch(self.current_source_fingerprint) is None:
            raise RecurringRevenueGrowthPolicyError("M12P7_CURRENT_SOURCE_FINGERPRINT_INVALID")
        object.__setattr__(self, "prior_as_of", prior)
        object.__setattr__(self, "current_as_of", current)
        payload = _canonical_payload(
            tenant_id=self.tenant_id,
            prior_as_of=prior,
            current_as_of=current,
            currency=self.currency,
            prior_source_fingerprint=self.prior_source_fingerprint,
            current_source_fingerprint=self.current_source_fingerprint,
            prior_mrr_minor=self.prior_mrr_minor,
            current_mrr_minor=self.current_mrr_minor,
            delta_mrr_minor=self.delta_mrr_minor,
            growth_numerator=self.growth_numerator,
            growth_denominator=self.growth_denominator,
            classification=self.classification,
        )
        digest = hashlib.sha3_512(
            json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if self.fingerprint and self.fingerprint != digest:
            raise RecurringRevenueGrowthPolicyError("M12P7_GROWTH_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def growth_fingerprint(self) -> str:
        """Return the deterministic SHA3-512 seal under an explicit name."""
        return self.fingerprint

    def to_dict(self) -> dict[str, object]:
        """Return a detached canonical evidence representation."""
        payload = _canonical_payload(
            tenant_id=self.tenant_id,
            prior_as_of=self.prior_as_of,
            current_as_of=self.current_as_of,
            currency=self.currency,
            prior_source_fingerprint=self.prior_source_fingerprint,
            current_source_fingerprint=self.current_source_fingerprint,
            prior_mrr_minor=self.prior_mrr_minor,
            current_mrr_minor=self.current_mrr_minor,
            delta_mrr_minor=self.delta_mrr_minor,
            growth_numerator=self.growth_numerator,
            growth_denominator=self.growth_denominator,
            classification=self.classification,
        )
        return {**payload, "fingerprint": self.fingerprint}


def derive_recurring_revenue_growth(
    *, prior: RecurringRevenueEvidence, current: RecurringRevenueEvidence
) -> RecurringRevenueGrowthEvidence:
    """Derive exact signed MRR growth from two explicit certified snapshots.

    For a positive prior baseline, ``growth_numerator / growth_denominator`` is
    the exact signed minor-unit ratio ``(current - prior) / prior``. No float,
    percentage conversion, or rounding is performed. A zero baseline is
    classified explicitly and has no rate numerator or denominator.
    """
    prior_snapshot, prior_fingerprint, prior_as_of = _validate_snapshot(prior)
    current_snapshot, current_fingerprint, current_as_of = _validate_snapshot(current)
    if prior_fingerprint == current_fingerprint:
        raise RecurringRevenueGrowthPolicyError("M12P7_SNAPSHOTS_NOT_DISTINCT")
    if prior_snapshot.tenant_id != current_snapshot.tenant_id:
        raise RecurringRevenueGrowthPolicyError("M12P7_TENANT_MISMATCH")
    if current_as_of <= prior_as_of:
        raise RecurringRevenueGrowthPolicyError("M12P7_AS_OF_ORDER_INVALID")
    if prior_snapshot.currency is None or current_snapshot.currency is None:
        raise RecurringRevenueGrowthPolicyError("M12P7_CURRENCY_REQUIRED")
    if prior_snapshot.currency != current_snapshot.currency:
        raise RecurringRevenueGrowthPolicyError("M12P7_CURRENCY_MISMATCH")
    currency = prior_snapshot.currency
    prior_mrr = prior_snapshot.mrr_minor
    current_mrr = current_snapshot.mrr_minor
    delta = current_mrr - prior_mrr
    if prior_mrr == 0:
        if current_mrr == 0:
            classification = GrowthClassification.NO_CHANGE
        else:
            classification = GrowthClassification.RATE_UNDEFINED_ZERO_BASELINE
        numerator = denominator = None
    else:
        numerator, denominator = delta, prior_mrr
        classification = (
            GrowthClassification.POSITIVE if delta > 0 else
            GrowthClassification.CONTRACTION if delta < 0 else
            GrowthClassification.NO_CHANGE
        )
    return RecurringRevenueGrowthEvidence(
        tenant_id=prior_snapshot.tenant_id,
        prior_as_of=prior_as_of,
        current_as_of=current_as_of,
        currency=currency,
        prior_source_fingerprint=prior_fingerprint,
        current_source_fingerprint=current_fingerprint,
        prior_mrr_minor=prior_mrr,
        current_mrr_minor=current_mrr,
        delta_mrr_minor=delta,
        growth_numerator=numerator,
        growth_denominator=denominator,
        classification=classification,
    )


__all__ = [
    "EVIDENCE_CONTRACT",
    "GrowthClassification",
    "RecurringRevenueGrowthEvidence",
    "RecurringRevenueGrowthPolicyError",
    "VERSION",
    "derive_recurring_revenue_growth",
]


# ARTIFACT: recurring_revenue_growth_policy.py
# VERSION: v1.0.0-M12-P7-RECURRING-REVENUE-GROWTH-POLICY
# AUTHORITY BOUNDARY: deterministic derived MRR growth evidence only
# TENANT POSTURE: exact tenant binding; mismatches fail closed
# FAIL-CLOSED POSTURE: corrupt source evidence and undefined rates are explicit
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
