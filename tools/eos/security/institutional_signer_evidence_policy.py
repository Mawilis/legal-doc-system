"""Explicit freshness-policy parameters for institutional signer evidence.

This module validates policy inputs; it does not establish approval authority,
authenticate a policy document, or configure production values. A caller may
use these parameters only after a separately governed policy source has been
authenticated and approved. No defaults are supplied.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from typing import Final, Mapping

EVIDENCE_KINDS: Final[frozenset[str]] = frozenset({
    "IDENTITY_PROOFING",
    "SIGNATORY_MANDATE",
    "INDEPENDENT_APPROVAL",
})


class InstitutionalSignerEvidencePolicyError(RuntimeError):
    """Fail-closed policy validation or evaluation error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _utc_instant(field: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise InstitutionalSignerEvidencePolicyError(
            f"INSTITUTIONAL_SIGNER_POLICY_{field.upper()}_INVALID"
        )
    return value.astimezone(timezone.utc)


def _positive_duration(field: str, value: object, *, allow_zero: bool = False) -> timedelta:
    if type(value) is not timedelta or value < timedelta(0) or (
        not allow_zero and value == timedelta(0)
    ):
        raise InstitutionalSignerEvidencePolicyError(
            f"INSTITUTIONAL_SIGNER_POLICY_{field.upper()}_INVALID"
        )
    return value


@dataclass(frozen=True, slots=True)
class InstitutionalSignerEvidencePolicyParameters:
    """Fully explicit, immutable policy parameters; no operational defaults."""

    policy_reference: str
    policy_revision: str
    effective_at: datetime
    expires_at: datetime
    maximum_evidence_age_by_kind: Mapping[str, timedelta]
    currentness_lease_duration: timedelta
    reconciliation_cadence: timedelta
    clock_skew_tolerance: timedelta

    def __post_init__(self) -> None:
        for field in ("policy_reference", "policy_revision"):
            value = getattr(self, field)
            if type(value) is not str or not value.strip() or len(value) > 256:
                raise InstitutionalSignerEvidencePolicyError(
                    f"INSTITUTIONAL_SIGNER_POLICY_{field.upper()}_INVALID"
                )
        effective_at = _utc_instant("effective_at", self.effective_at)
        expires_at = _utc_instant("expires_at", self.expires_at)
        if expires_at <= effective_at:
            raise InstitutionalSignerEvidencePolicyError(
                "INSTITUTIONAL_SIGNER_POLICY_EFFECTIVE_INTERVAL_INVALID"
            )
        if not isinstance(self.maximum_evidence_age_by_kind, Mapping):
            raise InstitutionalSignerEvidencePolicyError(
                "INSTITUTIONAL_SIGNER_POLICY_EVIDENCE_AGE_MAP_INVALID"
            )
        ages = dict(self.maximum_evidence_age_by_kind)
        if set(ages) != EVIDENCE_KINDS:
            raise InstitutionalSignerEvidencePolicyError(
                "INSTITUTIONAL_SIGNER_POLICY_EVIDENCE_AGE_KINDS_INCOMPLETE"
            )
        for kind, duration in ages.items():
            ages[kind] = _positive_duration(f"{kind.lower()}_maximum_age", duration)
        lease = _positive_duration("currentness_lease_duration", self.currentness_lease_duration)
        cadence = _positive_duration("reconciliation_cadence", self.reconciliation_cadence)
        skew = _positive_duration("clock_skew_tolerance", self.clock_skew_tolerance, allow_zero=True)
        object.__setattr__(self, "effective_at", effective_at)
        object.__setattr__(self, "expires_at", expires_at)
        object.__setattr__(self, "maximum_evidence_age_by_kind", MappingProxyType(ages))
        object.__setattr__(self, "currentness_lease_duration", lease)
        object.__setattr__(self, "reconciliation_cadence", cadence)
        object.__setattr__(self, "clock_skew_tolerance", skew)

    def assert_effective(self, *, evaluated_at: datetime) -> datetime:
        instant = _utc_instant("evaluated_at", evaluated_at)
        if not self.effective_at <= instant < self.expires_at:
            raise InstitutionalSignerEvidencePolicyError(
                "INSTITUTIONAL_SIGNER_POLICY_NOT_EFFECTIVE"
            )
        return instant

    def assert_evidence_fresh(
        self, *, evidence_kind: str, observed_at: datetime, evaluated_at: datetime
    ) -> None:
        instant = self.assert_effective(evaluated_at=evaluated_at)
        maximum_age = self.maximum_evidence_age_by_kind.get(evidence_kind)
        if maximum_age is None:
            raise InstitutionalSignerEvidencePolicyError(
                "INSTITUTIONAL_SIGNER_POLICY_EVIDENCE_KIND_UNSUPPORTED"
            )
        observed = _utc_instant("observed_at", observed_at)
        if observed > instant + self.clock_skew_tolerance:
            raise InstitutionalSignerEvidencePolicyError(
                "INSTITUTIONAL_SIGNER_POLICY_OBSERVATION_FROM_FUTURE"
            )
        if instant - observed > maximum_age:
            raise InstitutionalSignerEvidencePolicyError(
                "INSTITUTIONAL_SIGNER_POLICY_EVIDENCE_TOO_OLD"
            )

    def currentness_lease_until(self, *, checked_at: datetime) -> datetime:
        checked = self.assert_effective(evaluated_at=checked_at)
        lease_until = min(checked + self.currentness_lease_duration, self.expires_at)
        if lease_until <= checked:
            raise InstitutionalSignerEvidencePolicyError(
                "INSTITUTIONAL_SIGNER_POLICY_LEASE_UNAVAILABLE"
            )
        return lease_until

    def next_reconciliation_at(self, *, checked_at: datetime) -> datetime:
        checked = self.assert_effective(evaluated_at=checked_at)
        return min(checked + self.reconciliation_cadence, self.expires_at)


__all__ = [
    "EVIDENCE_KINDS",
    "InstitutionalSignerEvidencePolicyError",
    "InstitutionalSignerEvidencePolicyParameters",
]
