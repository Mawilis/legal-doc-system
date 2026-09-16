"""Wilsy OS M13-P6A canonical WILSY AI usage-capacity derivation.

TITLE: WILSY AI Usage Capacity Derivation
VERSION: v1.1.0-M13-P6A
AUTHORITY: Wilsy OS Core Governance
EPITOME: Derive tenant-scoped daily request and calendar-month automation
         capacity from explicit P5A/P5B evidence without creating new truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/wilsy_ai_usage_capacity.py
COLLABORATION / OWNERSHIP: P3 owns commercial limits; P4 owns active
                            entitlement lifecycle; P5A/P5B own raw observed
                            evidence; P6A owns this pure derivation only.
                            Kennel EOS exclusively owns financial execution and
                            settlement.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: v1.1.0-M13-P6A binds capacity to canonical P6B complete-window
           evidence and derives legitimate zero consumption from an empty
           authoritative window.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Pure in-memory derivation; no persistence,
                             network, secrets, providers, or clients.
TENANT BOUNDARY: Every observation must match the explicit entitlement tenant.
AUTHORITY BOUNDARY: Capacity derivation only; no access grant, billing,
                    invoice, payment, execution, settlement, or ROI authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
FAIL-CLOSED DECLARATION: Missing complete-window evidence, inactive/stale
                         entitlements, mismatches, invalid windows, and
                         malformed facts reject.
COMPLETENESS POSTURE: P6B complete-window evidence is mandatory; an empty
                      complete window is proven absence, not a usage event.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
from typing import Any, Final, cast

from tools.eos.saas.billing.wilsy_ai_commercial_policy import get_wilsy_ai_commercial_policy
from tools.eos.saas.domain.wilsy_ai_entitlement import (
    WilsyAIEntitlement,
    WilsyAIEntitlementError,
    WilsyAIEntitlementState,
)
from tools.eos.saas.domain.wilsy_ai_usage_window import (
    WilsyAIUsageWindowEvidence,
    WilsyAIUsageWindowEvidenceError,
)

VERSION: Final[str] = "v1.1.0-M13-P6A"
SCHEMA: Final[str] = "WILSY-AI-USAGE-CAPACITY/V2"
_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id", "entitlement_id", "module_id", "entitlement_revision",
    "entitlement_fingerprint", "as_of", "daily_window_start",
    "daily_window_end", "monthly_window_start", "monthly_window_end",
    "daily_request_limit", "monthly_automation_limit",
    "daily_consumed_request_units", "monthly_consumed_automation_actions",
    "daily_remaining_request_units", "monthly_remaining_automation_actions",
    "daily_exhausted", "monthly_exhausted", "observation_fingerprints",
    "usage_window_fingerprint", "schema", "capacity_version", "fingerprint",
)
_HEX = frozenset("0123456789abcdef")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "root", "*", "global_root"})


class WilsyAIUsageCapacityError(ValueError):
    """Raised when capacity derivation cannot be proven from canonical evidence."""


def _aware(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise WilsyAIUsageCapacityError("M13P6A_AS_OF_INVALID")
    return value.astimezone(timezone.utc)


def _next_month(start: datetime) -> datetime:
    if start.month == 12:
        return start.replace(year=start.year + 1, month=1, day=1)
    return start.replace(month=start.month + 1, day=1)


def _digest(value: object, code: str) -> str:
    if not isinstance(value, str) or len(value) != 128 or not value or not set(value) <= _HEX:
        raise WilsyAIUsageCapacityError(code)
    return value


def _nonnegative(value: object, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise WilsyAIUsageCapacityError(code)
    return value


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class WilsyAIUsageCapacity:
    """Immutable evidence of observed consumption and remaining capacity."""

    tenant_id: str
    entitlement_id: str
    module_id: str
    entitlement_revision: int
    entitlement_fingerprint: str
    as_of: datetime
    daily_window_start: datetime
    daily_window_end: datetime
    monthly_window_start: datetime
    monthly_window_end: datetime
    daily_request_limit: int
    monthly_automation_limit: int
    daily_consumed_request_units: int
    monthly_consumed_automation_actions: int
    daily_remaining_request_units: int
    monthly_remaining_automation_actions: int
    daily_exhausted: bool
    monthly_exhausted: bool
    observation_fingerprints: tuple[str, ...]
    usage_window_fingerprint: str
    schema: str = SCHEMA
    capacity_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.capacity_version != VERSION:
            raise WilsyAIUsageCapacityError("M13P6A_IDENTITY_INVALID")
        as_of = _aware(self.as_of)
        windows = {
            field: _aware(getattr(self, field))
            for field in ("daily_window_start", "daily_window_end", "monthly_window_start", "monthly_window_end")
        }
        expected_daily_start = as_of.replace(hour=0, minute=0, second=0, microsecond=0)
        expected_daily_end = expected_daily_start + timedelta(days=1)
        expected_monthly_start = expected_daily_start.replace(day=1)
        expected_monthly_end = _next_month(expected_monthly_start)
        if (
            windows["daily_window_start"] != expected_daily_start
            or windows["daily_window_end"] != expected_daily_end
            or windows["monthly_window_start"] != expected_monthly_start
            or windows["monthly_window_end"] != expected_monthly_end
        ):
            raise WilsyAIUsageCapacityError("M13P6A_WINDOW_INVALID")
        for field in ("tenant_id", "entitlement_id", "module_id"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value or value != value.strip():
                raise WilsyAIUsageCapacityError("M13P6A_IDENTITY_INVALID")
            if field == "tenant_id" and value.lower() in _FORBIDDEN_TENANTS:
                raise WilsyAIUsageCapacityError("M13P6A_TENANT_REQUIRED")
        _nonnegative(self.entitlement_revision, "M13P6A_REVISION_INVALID")
        _digest(self.entitlement_fingerprint, "M13P6A_FINGERPRINT_INVALID")
        _digest(self.usage_window_fingerprint, "M13P6A_WINDOW_FINGERPRINT_INVALID")
        for field in ("daily_request_limit", "monthly_automation_limit"):
            if _nonnegative(getattr(self, field), "M13P6A_LIMIT_INVALID") <= 0:
                raise WilsyAIUsageCapacityError("M13P6A_LIMIT_INVALID")
        for field in ("daily_consumed_request_units", "monthly_consumed_automation_actions", "daily_remaining_request_units", "monthly_remaining_automation_actions"):
            _nonnegative(getattr(self, field), "M13P6A_CONSUMPTION_INVALID")
        if self.daily_remaining_request_units != max(0, self.daily_request_limit - self.daily_consumed_request_units) or self.monthly_remaining_automation_actions != max(0, self.monthly_automation_limit - self.monthly_consumed_automation_actions):
            raise WilsyAIUsageCapacityError("M13P6A_REMAINING_INVALID")
        if not isinstance(self.daily_exhausted, bool) or not isinstance(self.monthly_exhausted, bool):
            raise WilsyAIUsageCapacityError("M13P6A_STATUS_INVALID")
        if self.daily_exhausted != (self.daily_consumed_request_units >= self.daily_request_limit) or self.monthly_exhausted != (self.monthly_consumed_automation_actions >= self.monthly_automation_limit):
            raise WilsyAIUsageCapacityError("M13P6A_STATUS_INVALID")
        if not isinstance(self.observation_fingerprints, tuple) or any(
            _digest(item, "M13P6A_OBSERVATION_FINGERPRINT_INVALID") != item
            for item in self.observation_fingerprints
        ):
            raise WilsyAIUsageCapacityError("M13P6A_OBSERVATION_FINGERPRINT_INVALID")
        if len(set(self.observation_fingerprints)) != len(self.observation_fingerprints):
            raise WilsyAIUsageCapacityError("M13P6A_OBSERVATION_FINGERPRINT_INVALID")
        object.__setattr__(self, "as_of", as_of)
        for field, value in windows.items():
            object.__setattr__(self, field, value)
        payload = {_field: _json_value(getattr(self, _field)) for _field in _FIELDS[:-1]}
        digest = hashlib.sha3_512(json.dumps(payload, ensure_ascii=False, sort_keys=False, separators=(",", ":")).encode("utf-8")).hexdigest()
        if self.fingerprint and (not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, digest)):
            raise WilsyAIUsageCapacityError("M13P6A_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Return deterministic capacity evidence without financial fields."""
        return {_field: _json_value(getattr(self, _field)) for _field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "WilsyAIUsageCapacity":
        """Hydrate exact capacity evidence and verify its deterministic digest."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise WilsyAIUsageCapacityError("M13P6A_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        for field in ("as_of", "daily_window_start", "daily_window_end", "monthly_window_start", "monthly_window_end"):
            value = values.get(field)
            if isinstance(value, str):
                try:
                    values[field] = datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError as error:
                    raise WilsyAIUsageCapacityError("M13P6A_AS_OF_INVALID") from error
        if isinstance(values.get("observation_fingerprints"), list):
            values["observation_fingerprints"] = tuple(cast(list[str], values["observation_fingerprints"]))
        item = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, item.fingerprint):
            raise WilsyAIUsageCapacityError("M13P6A_FINGERPRINT_MISMATCH")
        return item


def derive_wilsy_ai_usage_capacity(*, entitlement: WilsyAIEntitlement, usage_window: WilsyAIUsageWindowEvidence, as_of: datetime) -> WilsyAIUsageCapacity:
    """Derive capacity from one canonical, complete P6B usage window.

    A naked iterable of observations is deliberately unsupported: P6B must
    prove that an empty result is exhaustive before P6A may derive zero use.
    """
    if not isinstance(entitlement, WilsyAIEntitlement):
        raise WilsyAIUsageCapacityError("M13P6A_ENTITLEMENT_INVALID")
    try:
        verified_entitlement = WilsyAIEntitlement.from_dict(entitlement.to_dict())
    except WilsyAIEntitlementError as error:
        if "POLICY_BINDING" in str(error):
            raise WilsyAIUsageCapacityError("M13P6A_POLICY_BINDING_INVALID") from error
        raise WilsyAIUsageCapacityError("M13P6A_ENTITLEMENT_INVALID") from error
    if verified_entitlement.lifecycle_state is not WilsyAIEntitlementState.ACTIVE:
        raise WilsyAIUsageCapacityError("M13P6A_ENTITLEMENT_NOT_ACTIVE")
    as_of_utc = _aware(as_of)
    if verified_entitlement.activated_at is None:
        raise WilsyAIUsageCapacityError("M13P6A_ACTIVATION_EVIDENCE_REQUIRED")
    if verified_entitlement.activated_at.tzinfo is None or verified_entitlement.activated_at.utcoffset() is None:
        raise WilsyAIUsageCapacityError("M13P6A_ACTIVATION_EVIDENCE_REQUIRED")
    activated_at = verified_entitlement.activated_at.astimezone(timezone.utc)
    if as_of_utc < activated_at:
        raise WilsyAIUsageCapacityError("M13P6A_AS_OF_BEFORE_ACTIVATION")
    policy = get_wilsy_ai_commercial_policy(verified_entitlement.tier)
    if verified_entitlement.policy_fingerprint != policy.policy_fingerprint:
        raise WilsyAIUsageCapacityError("M13P6A_POLICY_BINDING_INVALID")
    if not isinstance(usage_window, WilsyAIUsageWindowEvidence):
        raise WilsyAIUsageCapacityError("M13P6A_COMPLETE_WINDOW_REQUIRED")
    try:
        window = WilsyAIUsageWindowEvidence.from_dict(usage_window.to_dict())
    except WilsyAIUsageWindowEvidenceError as error:
        raise WilsyAIUsageCapacityError("M13P6A_WINDOW_INVALID") from error
    if (
        window.tenant_id != verified_entitlement.tenant_id
        or window.entitlement_id != verified_entitlement.entitlement_id
        or window.module_id != verified_entitlement.module_id
        or window.entitlement_revision != verified_entitlement.lifecycle_revision
        or window.entitlement_fingerprint != verified_entitlement.fingerprint
        or window.as_of != as_of_utc
    ):
        raise WilsyAIUsageCapacityError("M13P6A_WINDOW_BINDING_MISMATCH")
    if window.as_of < activated_at:
        raise WilsyAIUsageCapacityError("M13P6A_AS_OF_BEFORE_ACTIVATION")
    daily_start = as_of_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    daily_end = daily_start + timedelta(days=1)
    monthly_start = daily_start.replace(day=1)
    monthly_end = _next_month(monthly_start)
    for item in window.observations:
        if item.occurred_at < activated_at:
            raise WilsyAIUsageCapacityError("M13P6A_PRE_ACTIVATION_EVIDENCE")
        if item.occurred_at > as_of_utc:
            raise WilsyAIUsageCapacityError("M13P6A_FUTURE_EVIDENCE")
        if item.occurred_at < monthly_start or item.occurred_at >= monthly_end:
            raise WilsyAIUsageCapacityError("M13P6A_EVIDENCE_OUTSIDE_MONTH")
    bounded_evidence = window.observations
    daily = tuple(item for item in bounded_evidence if daily_start <= item.occurred_at <= as_of_utc)
    monthly = tuple(item for item in bounded_evidence if monthly_start <= item.occurred_at <= as_of_utc)
    daily_consumed = sum(item.request_units for item in daily)
    monthly_consumed = sum(item.automation_actions for item in monthly)
    daily_limit = policy.daily_request_limit
    monthly_limit = policy.monthly_automation_limit
    return WilsyAIUsageCapacity(
        tenant_id=verified_entitlement.tenant_id, entitlement_id=verified_entitlement.entitlement_id, module_id=verified_entitlement.module_id,
        entitlement_revision=verified_entitlement.lifecycle_revision, entitlement_fingerprint=verified_entitlement.fingerprint,
        as_of=as_of_utc, daily_window_start=daily_start, daily_window_end=daily_end,
        monthly_window_start=monthly_start, monthly_window_end=monthly_end,
        daily_request_limit=daily_limit, monthly_automation_limit=monthly_limit,
        daily_consumed_request_units=daily_consumed, monthly_consumed_automation_actions=monthly_consumed,
        daily_remaining_request_units=max(0, daily_limit - daily_consumed), monthly_remaining_automation_actions=max(0, monthly_limit - monthly_consumed),
        daily_exhausted=daily_consumed >= daily_limit, monthly_exhausted=monthly_consumed >= monthly_limit,
        observation_fingerprints=window.observation_fingerprints,
        usage_window_fingerprint=window.fingerprint,
    )


__all__ = ["SCHEMA", "VERSION", "WilsyAIUsageCapacity", "WilsyAIUsageCapacityError", "derive_wilsy_ai_usage_capacity"]

# ARTIFACT: wilsy_ai_usage_capacity.py
# VERSION: v1.1.0-M13-P6A
# AUTHORITY BOUNDARY: observed capacity derivation only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
