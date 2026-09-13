"""WILSY OS M13-P3 canonical WILSY AI commercial-policy authority.

TITLE: WILSY AI Commercial Policy
VERSION: v1.0.0-M13-P3
AUTHORITY: Wilsy OS Core Governance
EPITOME: Own the immutable, provider-neutral commercial policy for the three
         WILSY AI VAS products without granting entitlement or financial power.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/wilsy_ai_commercial_policy.py
COLLABORATION / OWNERSHIP: Python EOS canonical policy owner; PlanRegistry owns
                            base subscription catalogue, WilsyAIVASAccess is a
                            downstream projection, and Kennel EOS owns financial
                            execution and settlement.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M13-P3 migrates the certified Node WILSY AI tier inputs into
           exact integer-ZAR-minor immutable descriptors with deterministic
           SHA3-512 evidence and strict fail-closed hydration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Pure in-process policy data only; no credentials,
                             network, provider, KMS, Mongo, or external client.
TENANT BOUNDARY: Policy descriptors are provider-neutral catalogue facts; they
                 do not grant tenant entitlement or activation.
AUTHORITY BOUNDARY: Commercial policy description and integrity evidence only;
                    no entitlement, metering, persistence, invoicing, charging,
                    payment, settlement, or autonomous-action authorization.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and
                               settlement truth; PlanRegistry owns base plans.
FAIL-CLOSED DECLARATION: Unknown tiers, altered canonical values, malformed
                         payloads, unsupported currency, and fingerprint drift
                         reject deterministically.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Final, cast


VERSION: Final[str] = "v1.0.0-M13-P3"
POLICY_SCHEMA: Final[str] = "WILSY-AI-COMMERCIAL-POLICY/V1"
POLICY_IDENTITY: Final[str] = "WILSY_AI_COMMERCIAL_POLICY"
SUPPORTED_CURRENCY: Final[str] = "ZAR"
_FINGERPRINT = "fingerprint"


class WilsyAICommercialPolicyError(ValueError):
    """Raised when a WILSY AI commercial-policy descriptor is invalid."""


class WilsyAITier(str, Enum):
    """The closed set of WILSY AI commercial VAS products."""

    STARTER = "WILSY_AI_STARTER"
    GROWTH = "WILSY_AI_GROWTH"
    INSTITUTIONAL = "WILSY_AI_INSTITUTIONAL"


# These are the exact production Node policy inputs. Monetary values are
# converted once into integer ZAR minor units; no binary float enters the
# canonical descriptor or its digest.
_CANONICAL_INPUTS: Final[dict[WilsyAITier, dict[str, object]]] = {
    WilsyAITier.STARTER: {
        "label": "Wilsy AI Starter",
        "currency": "ZAR",
        "monthly_price_minor": 49_900,
        "setup_price_minor": 0,
        "daily_request_limit": 35,
        "monthly_automation_limit": 750,
        "analyst_seats": 1,
        "max_autonomous_actions_per_day": 5,
        "approval_threshold_minor": 250_000,
        "overage_price_per_request_minor": 300,
        "value_promise": "Daily admin reduction, inbox triage, customer follow-ups and document capture.",
    },
    WilsyAITier.GROWTH: {
        "label": "Wilsy AI Growth",
        "currency": "ZAR",
        "monthly_price_minor": 149_900,
        "setup_price_minor": 75_000,
        "daily_request_limit": 120,
        "monthly_automation_limit": 3_000,
        "analyst_seats": 3,
        "max_autonomous_actions_per_day": 25,
        "approval_threshold_minor": 1_000_000,
        "overage_price_per_request_minor": 200,
        "value_promise": "Owner-grade cash, margin, stock and customer-work automation with controlled execution.",
    },
    WilsyAITier.INSTITUTIONAL: {
        "label": "Wilsy AI Institutional",
        "currency": "ZAR",
        "monthly_price_minor": 549_900,
        "setup_price_minor": 250_000,
        "daily_request_limit": 450,
        "monthly_automation_limit": 12_000,
        "analyst_seats": 12,
        "max_autonomous_actions_per_day": 100,
        "approval_threshold_minor": 5_000_000,
        "overage_price_per_request_minor": 100,
        "value_promise": "Executive command automation, compliance evidence, industry playbooks and audit exports.",
    },
}

_SERIALIZED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "policy_identity",
        "policy_version",
        "tier",
        "label",
        "currency",
        "monthly_price_minor",
        "setup_price_minor",
        "daily_request_limit",
        "monthly_automation_limit",
        "analyst_seats",
        "max_autonomous_actions_per_day",
        "approval_threshold_minor",
        "overage_price_per_request_minor",
        "value_promise",
        _FINGERPRINT,
    }
)


def _canonical_payload(
    *,
    tier: WilsyAITier,
    label: str,
    currency: str,
    monthly_price_minor: int,
    setup_price_minor: int,
    daily_request_limit: int,
    monthly_automation_limit: int,
    analyst_seats: int,
    max_autonomous_actions_per_day: int,
    approval_threshold_minor: int,
    overage_price_per_request_minor: int,
    value_promise: str,
) -> dict[str, object]:
    """Return the complete semantic payload, excluding its derived digest."""
    return {
        "schema": POLICY_SCHEMA,
        "policy_identity": POLICY_IDENTITY,
        "policy_version": VERSION,
        "tier": tier.value,
        "label": label,
        "currency": currency,
        "monthly_price_minor": monthly_price_minor,
        "setup_price_minor": setup_price_minor,
        "daily_request_limit": daily_request_limit,
        "monthly_automation_limit": monthly_automation_limit,
        "analyst_seats": analyst_seats,
        "max_autonomous_actions_per_day": max_autonomous_actions_per_day,
        "approval_threshold_minor": approval_threshold_minor,
        "overage_price_per_request_minor": overage_price_per_request_minor,
        "value_promise": value_promise,
    }


def _digest(payload: Mapping[str, object]) -> str:
    """Compute lowercase SHA3-512 over deterministic UTF-8 JSON bytes."""
    encoded = json.dumps(
        dict(payload),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _text(value: object, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WilsyAICommercialPolicyError(code)
    return value


def _money(value: object, code: str, *, allow_zero: bool) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise WilsyAICommercialPolicyError(code)
    if value < 0 or (value == 0 and not allow_zero):
        raise WilsyAICommercialPolicyError(code)
    return value


def _capacity(value: object, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise WilsyAICommercialPolicyError(code)
    return value


@dataclass(frozen=True, slots=True)
class WilsyAICommercialPolicy:
    """Immutable canonical commercial policy and deterministic evidence seal."""

    tier: WilsyAITier | str
    label: str
    currency: str
    monthly_price_minor: int
    setup_price_minor: int
    daily_request_limit: int
    monthly_automation_limit: int
    analyst_seats: int
    max_autonomous_actions_per_day: int
    approval_threshold_minor: int
    overage_price_per_request_minor: int
    value_promise: str
    schema: str = POLICY_SCHEMA
    policy_identity: str = POLICY_IDENTITY
    policy_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate canonical values and derive the descriptor fingerprint."""
        try:
            tier = WilsyAITier(self.tier)
        except (TypeError, ValueError) as error:
            raise WilsyAICommercialPolicyError("M13P3_UNKNOWN_TIER") from error
        canonical = _CANONICAL_INPUTS[tier]
        if self.schema != POLICY_SCHEMA or self.policy_identity != POLICY_IDENTITY or self.policy_version != VERSION:
            raise WilsyAICommercialPolicyError("M13P3_POLICY_IDENTITY_INVALID")
        if self.currency != SUPPORTED_CURRENCY:
            raise WilsyAICommercialPolicyError("M13P3_CURRENCY_UNSUPPORTED")
        _text(self.label, "M13P3_LABEL_INVALID")
        _text(self.value_promise, "M13P3_VALUE_PROMISE_INVALID")
        _money(self.monthly_price_minor, "M13P3_MONTHLY_PRICE_INVALID", allow_zero=False)
        _money(self.setup_price_minor, "M13P3_SETUP_PRICE_INVALID", allow_zero=True)
        _money(self.approval_threshold_minor, "M13P3_APPROVAL_THRESHOLD_INVALID", allow_zero=False)
        _money(self.overage_price_per_request_minor, "M13P3_OVERAGE_PRICE_INVALID", allow_zero=False)
        _capacity(self.daily_request_limit, "M13P3_DAILY_LIMIT_INVALID")
        _capacity(self.monthly_automation_limit, "M13P3_MONTHLY_AUTOMATION_INVALID")
        _capacity(self.analyst_seats, "M13P3_ANALYST_SEATS_INVALID")
        _capacity(self.max_autonomous_actions_per_day, "M13P3_AUTONOMOUS_LIMIT_INVALID")
        for field, expected in canonical.items():
            if getattr(self, field) != expected:
                raise WilsyAICommercialPolicyError("M13P3_CALLER_VALUE_OVERRIDE")
        payload = _canonical_payload(
            tier=tier,
            label=self.label,
            currency=self.currency,
            monthly_price_minor=self.monthly_price_minor,
            setup_price_minor=self.setup_price_minor,
            daily_request_limit=self.daily_request_limit,
            monthly_automation_limit=self.monthly_automation_limit,
            analyst_seats=self.analyst_seats,
            max_autonomous_actions_per_day=self.max_autonomous_actions_per_day,
            approval_threshold_minor=self.approval_threshold_minor,
            overage_price_per_request_minor=self.overage_price_per_request_minor,
            value_promise=self.value_promise,
        )
        digest = _digest(payload)
        if self.fingerprint and self.fingerprint != digest:
            raise WilsyAICommercialPolicyError("M13P3_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "tier", tier)
        object.__setattr__(self, "fingerprint", digest)

    @property
    def policy_fingerprint(self) -> str:
        """Return the deterministic SHA3-512 policy evidence fingerprint."""
        return self.fingerprint

    def to_dict(self) -> dict[str, object]:
        """Return a detached strict descriptor suitable for evidence transport."""
        payload = _canonical_payload(
            tier=WilsyAITier(self.tier),
            label=self.label,
            currency=self.currency,
            monthly_price_minor=self.monthly_price_minor,
            setup_price_minor=self.setup_price_minor,
            daily_request_limit=self.daily_request_limit,
            monthly_automation_limit=self.monthly_automation_limit,
            analyst_seats=self.analyst_seats,
            max_autonomous_actions_per_day=self.max_autonomous_actions_per_day,
            approval_threshold_minor=self.approval_threshold_minor,
            overage_price_per_request_minor=self.overage_price_per_request_minor,
            value_promise=self.value_promise,
        )
        payload[_FINGERPRINT] = self.fingerprint
        return payload


def get_wilsy_ai_commercial_policy(tier: WilsyAITier | str) -> WilsyAICommercialPolicy:
    """Return the exact immutable policy for one known WILSY AI tier.

    Unknown tiers fail closed; there is no default-tier or latest-policy
    selection. The returned descriptor cannot be caller-overridden.
    """
    try:
        normalized = WilsyAITier(tier)
    except (TypeError, ValueError) as error:
        raise WilsyAICommercialPolicyError("M13P3_UNKNOWN_TIER") from error
    return _POLICIES[normalized]


def hydrate_wilsy_ai_commercial_policy(payload: Mapping[str, object]) -> WilsyAICommercialPolicy:
    """Strictly hydrate one descriptor and recompute its canonical fingerprint."""
    if not isinstance(payload, Mapping) or set(payload) != _SERIALIZED_FIELDS:
        raise WilsyAICommercialPolicyError("M13P3_DESCRIPTOR_SCHEMA_INVALID")
    raw: Mapping[str, Any] = payload
    try:
        return WilsyAICommercialPolicy(
            tier=raw["tier"],
            label=raw["label"],
            currency=raw["currency"],
            monthly_price_minor=raw["monthly_price_minor"],
            setup_price_minor=raw["setup_price_minor"],
            daily_request_limit=raw["daily_request_limit"],
            monthly_automation_limit=raw["monthly_automation_limit"],
            analyst_seats=raw["analyst_seats"],
            max_autonomous_actions_per_day=raw["max_autonomous_actions_per_day"],
            approval_threshold_minor=raw["approval_threshold_minor"],
            overage_price_per_request_minor=raw["overage_price_per_request_minor"],
            value_promise=raw["value_promise"],
            schema=raw["schema"],
            policy_identity=raw["policy_identity"],
            policy_version=raw["policy_version"],
            fingerprint=raw[_FINGERPRINT],
        )
    except (KeyError, TypeError, ValueError) as error:
        if isinstance(error, WilsyAICommercialPolicyError):
            raise
        raise WilsyAICommercialPolicyError("M13P3_DESCRIPTOR_INVALID") from error


_POLICIES: Mapping[WilsyAITier, WilsyAICommercialPolicy] = MappingProxyType(
    {
        tier: WilsyAICommercialPolicy(tier=tier, **cast(dict[str, Any], values))
        for tier, values in _CANONICAL_INPUTS.items()
    }
)

POLICIES: Final[Mapping[WilsyAITier, WilsyAICommercialPolicy]] = _POLICIES


__all__ = [
    "POLICIES",
    "POLICY_IDENTITY",
    "POLICY_SCHEMA",
    "SUPPORTED_CURRENCY",
    "VERSION",
    "WilsyAICommercialPolicy",
    "WilsyAICommercialPolicyError",
    "WilsyAITier",
    "get_wilsy_ai_commercial_policy",
    "hydrate_wilsy_ai_commercial_policy",
]


# ARTIFACT: wilsy_ai_commercial_policy.py
# VERSION: v1.0.0-M13-P3
# AUTHORITY BOUNDARY: Canonical WILSY AI commercial policy and integrity only.
# TENANT POSTURE: Provider-neutral catalogue facts; no entitlement grant.
# FAIL-CLOSED POSTURE: Unknown, altered, malformed, or unsupported descriptors reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
