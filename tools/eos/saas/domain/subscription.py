# -*- coding: utf-8 -*-
"""
TITLE:
    WILSY OS — Sovereign Subscription Catalogue Snapshot + Calendar Billing Domain

VERSION:
    v1.3.0-LEGACY-SUBSCRIPTION-MIGRATION

AUTHORITY:
    Wilsy OS Core Governance

PURPOSE:
    Preserve immutable subscription lifecycle truth, bind each current
    commercial plan snapshot to canonical Plan catalogue provenance, and expose
    deterministic calendar-period primitives for sovereign billing orchestration.

EPITOME:
    Subscription evidence may remember canonical catalogue truth and derive
    calendar billing coordinates, but it may never manufacture Plan authority,
    caller-authored proration, payment authority or financial execution truth.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/subscription.py

OWNERSHIP / COLLABORATION:
    Wilson Khanyezi / Wilsy OS Core Engineering.
    PlanEntity remains sovereign commercial catalogue truth.
    PlanRegistry remains canonical catalogue persistence authority.
    SubscriptionRegistry remains subscription persistence authority.
    Subscription HTTP authorization remains outside this domain.

CERTIFICATION / UPDATE DATE:
    2026-09-29

CHANGELOG:
    2026-09-29 v1.3.0-LEGACY-SUBSCRIPTION-MIGRATION
        - Adds an explicit fail-closed migration boundary for sufficiently
          evidenced legacy Node/BillingHUD subscription records.
        - Preserves historical Node proof, merkle and audit material as legacy
          provenance without promoting it to canonical Python proof authority.
        - Preserves SHA3-512-shaped historical Node proof and merkle evidence
          without claiming an independently reproducible relationship between them.
        - Regenerates deterministic canonical Python subscription evidence.
        - Rejects incomplete legacy rows rather than fabricating plan,
          lifecycle, temporal or idempotency truth.
        - Leaves ordinary current-schema hydration separate and unchanged.
        - Adds no payment, entitlement, membership or Kennel authority.

    2026-09-28 v1.2.1-CANONICAL-PROOF-PROVENANCE
        - Adds canonical subscription proof-context validation using the
          persisted latest AuditEntry action and metadata.
        - Keeps merkle validation bound to tenant, proof hash and seal nonce.
        - Does not add payment, membership, entitlement or Kennel authority.

    2026-09-03 v1.2.0-CALENDAR-BILLING-FOUNDATION
        - Adds deterministic timezone-aware calendar billing-period primitives.
        - Anchors billing periods to the first local calendar day of the month.
        - Models monthly, quarterly and annual periods as 1/3/12 calendar months.
        - Derives actual calendar-day denominators, including leap February.
        - Adds calendar-day proration coordinates without calculating money,
          authorizing payment, or widening Kennel execution authority.
        - Retains the legacy fixed-day helper only for existing registry
          compatibility until the separately certified registry-wiring slice.
        - Preserves all v1.1.0 catalogue-provenance semantics and proofs.

    2026-09-03 v1.1.0-CATALOGUE-PROVENANCE
        - Adds explicit optional plan_catalogue_version provenance.
        - Preserves None for legacy subscriptions where catalogue provenance
          was never persisted; no historical catalogue version is fabricated.
        - Deep-freezes the plan-feature snapshot inside SubscriptionEntity.
        - Binds plan name, features and catalogue version into subscription
          SHA3-512 proof material.
        - Removes proof-time wall-clock material so identical canonical
          subscription state produces deterministic proof evidence.
        - Projects catalogue provenance through canonical serialization,
          invoice seed and evidence-package surfaces.
    2026-08-19 v1.0.3-FIXED
        - Historical pre-provenance subscription domain baseline.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001-aligned commercial evidence integrity.

SECURITY / PRIVACY POSTURE:
    Contains subscription commercial/lifecycle evidence only. Catalogue
    provenance is descriptive persisted truth and never authentication,
    membership, permission, entitlement or financial-execution authority.

TENANT BOUNDARY:
    tenant_id is persisted subscription scope. This domain does not establish
    tenant membership or authorize access to another tenant's subscription.

AUTHORITY BOUNDARY:
    Owns immutable subscription value and evidence semantics only. Canonical
    sellable plan values remain owned by PlanEntity / PlanRegistry.

FINANCIAL AUTHORITY BOUNDARY:
    Subscription amount and billing configuration are commercial evidence only.
    APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED.
    Kennel EOS remains the exclusive financial execution authority.

CONSTITUTION:
    NO EVIDENCE = NO FACT.
    Unknown legacy catalogue provenance remains None.
"""

from __future__ import annotations

from calendar import monthrange
import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


VERSION = "v1.3.0-LEGACY-SUBSCRIPTION-MIGRATION"


# ─── Helper ──────────────────────────────────────────────────────────────────

def _canonical_plan_catalogue_version(
    value: Any,
) -> Optional[int]:
    """Validate explicit catalogue provenance without inventing legacy truth."""
    if value is None:
        return None

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(
            "plan_catalogue_version must be an integer or None"
        )

    if value < 1:
        raise ValueError(
            "plan_catalogue_version must be >= 1"
        )

    return value


def _canonical_plan_features(
    value: Any,
) -> Tuple[str, ...]:
    """Freeze one already-derived catalogue feature snapshot."""
    if value is None:
        return ()

    if isinstance(value, str):
        raise TypeError(
            "plan_features must be a sequence of strings"
        )

    try:
        values = tuple(value)
    except TypeError as error:
        raise TypeError(
            "plan_features must be a sequence of strings"
        ) from error

    for item in values:
        if not isinstance(item, str) or not item:
            raise ValueError(
                "plan_features entries must be non-empty strings"
            )

    return values


def parse_datetime(val: Any) -> Optional[datetime]:
    """Parse a datetime from ISO string or return datetime if already one."""
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val)
        except ValueError:
            return None
    return None


def _legacy_subscription_json_value(value: Any) -> Any:
    """Canonicalize observed legacy evidence without manufacturing truth.

    PyMongo returns BSON UTC datetimes as naive ``datetime`` objects unless
    timezone-aware decoding is explicitly enabled. Such already-decoded BSON
    values are normalized to UTC. This rule does not apply to textual
    timestamps.
    """
    if isinstance(value, datetime):
        if value.utcoffset() is None:
            value = value.replace(
                tzinfo=timezone.utc
            )
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): _legacy_subscription_json_value(item)
            for key, item in sorted(
                value.items(),
                key=lambda pair: str(pair[0]),
            )
        }

    if isinstance(value, (list, tuple)):
        return [
            _legacy_subscription_json_value(item)
            for item in value
        ]

    if value is None or isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    return str(value)


def _legacy_subscription_seed(
    data: Dict[str, Any],
    *,
    canonical_tenant_id: str,
    canonical_plan_id: str,
) -> str:
    """Bind fallback identity to complete observed legacy commercial evidence."""
    payload = {
        "canonical_tenant_id": canonical_tenant_id,
        "canonical_plan_id": canonical_plan_id,
        "legacy": _legacy_subscription_json_value(
            {
                key: value
                for key, value in data.items()
                if key != "__v"
            }
        ),
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest().upper()


def _legacy_subscription_datetime(
    data: Dict[str, Any],
    field_name: str,
) -> datetime:
    """Require one historical datetime, preserving MongoDB UTC semantics.

    PyMongo decodes BSON UTC datetimes as naive ``datetime`` values by default.
    Only an already-decoded ``datetime`` receives that UTC normalization.
    Naive textual timestamps remain invalid and are never silently assigned a
    timezone.
    """
    raw = data.get(field_name)
    value = parse_datetime(raw)

    if value is None:
        raise ValueError(
            "legacy subscription evidence incomplete: "
            f"{field_name}"
        )

    if (
        isinstance(raw, datetime)
        and value.utcoffset() is None
    ):
        return value.replace(
            tzinfo=timezone.utc
        )

    return _require_aware_datetime(
        value,
        field_name=field_name,
    )


def _legacy_subscription_sha3(
    value: Any,
    *,
    field_name: str,
) -> str:
    """Require one SHA3-512-shaped historical evidence value."""
    if not isinstance(value, str):
        raise ValueError(
            "legacy subscription evidence incomplete: "
            f"{field_name}"
        )

    candidate = value.strip()

    if len(candidate) != 128:
        raise ValueError(
            "legacy subscription evidence incomplete: "
            f"{field_name}"
        )

    try:
        int(candidate, 16)
    except ValueError as error:
        raise ValueError(
            "legacy subscription evidence incomplete: "
            f"{field_name}"
        ) from error

    return candidate



# ─────────────────────────────────────────────────────────────────────────────
# ENUMS (mirroring Node constants)
# ─────────────────────────────────────────────────────────────────────────────

class SubscriptionStatus(str, Enum):
    """Subscription lifecycle statuses."""
    TRIAL = "trial"
    ACTIVE = "active"
    PAUSED = "paused"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class BillingFrequency(str, Enum):
    """Billing cycle frequencies."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class CollectionMethod(str, Enum):
    """Payment collection methods."""
    CHARGE_AUTOMATICALLY = "charge_automatically"
    SEND_INVOICE = "send_invoice"


class PlanTiers(str, Enum):
    """Plan tier enumeration (as used in Node)."""
    FREE = "FREE"
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"
    SOVEREIGN = "SOVEREIGN"
    ULTRA = "ULTRA"
    FOUNDER_ENTERPRISE = "FOUNDER_ENTERPRISE"


# Alias for compatibility with Subscription.js naming
SubscriptionPlan = PlanTiers


class AuditAction(str, Enum):
    """Audit trail action types."""
    CREATE = "create"
    UPDATE = "update"          # ✅ Added
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    REACTIVATE = "reactivate"
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    CROSS_GRADE = "cross_grade"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    RENEWAL = "renewal"
    EXPIRED = "expired"
    ANOMALY_DETECTED = "anomaly_detected"


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS (mirroring Node helpers)
# ─────────────────────────────────────────────────────────────────────────────

def period_days_for_frequency(frequency: BillingFrequency) -> int:
    """Return the legacy fixed-day compatibility length.

    This helper remains temporarily for existing SubscriptionRegistry callers.
    It is NOT sovereign calendar billing truth and must not be used by new
    calendar-aware code. The registry-wiring slice will retire its production
    use after the calendar foundation is certified.
    """
    if frequency in (BillingFrequency.ANNUAL,):
        return 365
    if frequency == BillingFrequency.QUARTERLY:
        return 90
    return 30


def _require_aware_datetime(
    value: datetime,
    *,
    field_name: str,
) -> datetime:
    """Require one explicit timezone-aware calendar coordinate."""
    if not isinstance(value, datetime):
        raise TypeError(
            f"{field_name} must be a datetime"
        )

    if value.utcoffset() is None:
        raise ValueError(
            f"{field_name} must be timezone-aware"
        )

    return value


def _add_calendar_months(
    month_start: datetime,
    months: int,
) -> datetime:
    """Advance a first-of-month coordinate by whole calendar months."""
    if (
        isinstance(months, bool)
        or not isinstance(months, int)
    ):
        raise TypeError(
            "months must be an integer"
        )

    if months < 1:
        raise ValueError(
            "months must be >= 1"
        )

    absolute_month = (
        month_start.year * 12
        + (month_start.month - 1)
        + months
    )

    year, zero_based_month = divmod(
        absolute_month,
        12,
    )

    return month_start.replace(
        year=year,
        month=zero_based_month + 1,
        day=1,
    )


def calendar_period_bounds(
    reference: datetime,
    frequency: BillingFrequency,
) -> Tuple[datetime, datetime, int]:
    """Resolve deterministic first-of-month calendar period coordinates.

    The returned interval is half-open: ``[period_start, period_end)``.
    Calendar-day counts are derived from local dates rather than elapsed UTC
    seconds, so timezone offset changes cannot silently alter the denominator.
    """
    reference = _require_aware_datetime(
        reference,
        field_name="reference",
    )

    if not isinstance(
        frequency,
        BillingFrequency,
    ):
        raise TypeError(
            "frequency must be a BillingFrequency"
        )

    period_start = reference.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    months = {
        BillingFrequency.MONTHLY: 1,
        BillingFrequency.QUARTERLY: 3,
        BillingFrequency.ANNUAL: 12,
    }[frequency]

    period_end = _add_calendar_months(
        period_start,
        months,
    )

    total_days = (
        period_end.date()
        - period_start.date()
    ).days

    if total_days < 1:
        raise RuntimeError(
            "calendar billing period must contain at least one day"
        )

    if frequency == BillingFrequency.MONTHLY:
        expected_month_days = monthrange(
            period_start.year,
            period_start.month,
        )[1]

        if total_days != expected_month_days:
            raise RuntimeError(
                "monthly calendar denominator mismatch"
            )

    return (
        period_start,
        period_end,
        total_days,
    )


def calendar_proration_coordinate(
    effective_at: datetime,
    frequency: BillingFrequency,
) -> Dict[str, Any]:
    """Return non-monetary calendar-day proration evidence.

    This helper derives period bounds, actual total calendar days, remaining
    calendar days, and their deterministic ratio. It does not calculate price,
    credit, tax, charge, payment, authorization, execution or settlement.
    """
    effective_at = _require_aware_datetime(
        effective_at,
        field_name="effective_at",
    )

    (
        period_start,
        period_end,
        total_days,
    ) = calendar_period_bounds(
        effective_at,
        frequency,
    )

    days_elapsed = (
        effective_at.date()
        - period_start.date()
    ).days

    days_remaining = (
        period_end.date()
        - effective_at.date()
    ).days

    if not (
        0 <= days_elapsed < total_days
    ):
        raise RuntimeError(
            "effective_at falls outside derived calendar period"
        )

    if not (
        1 <= days_remaining <= total_days
    ):
        raise RuntimeError(
            "invalid calendar days_remaining"
        )

    return {
        "period_start": period_start,
        "period_end": period_end,
        "total_days": total_days,
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "proration_factor": (
            days_remaining
            / total_days
        ),
    }


def to_monthly_amount(amount: float, frequency: BillingFrequency) -> float:
    """Normalise amount to monthly equivalent."""
    a = float(amount)
    if frequency == BillingFrequency.ANNUAL:
        return a / 12
    if frequency == BillingFrequency.QUARTERLY:
        return a / 3
    return a


def to_annual_amount(amount: float, frequency: BillingFrequency) -> float:
    """Normalise amount to annual equivalent."""
    a = float(amount)
    if frequency == BillingFrequency.ANNUAL:
        return a
    if frequency == BillingFrequency.QUARTERLY:
        return a * 4
    return a * 12


def generate_proof(
    subscription: Dict[str, Any],
    action: str = "save",
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate a SHA3‑512 proof of a subscription's canonical state.
    Mirrors the Node method generateProof().
    """
    payload = {
        "action": action,
        "subscriptionId": subscription.get("subscription_id", "new"),
        "tenantId": subscription.get("tenant_id", ""),
        "kennelShard": subscription.get("kennel_shard", "EOS_PRIMARY"),
        "plan": subscription.get("plan", ""),
        "planId": subscription.get("plan_id", ""),
        "planName": subscription.get("plan_name"),
        "planFeatures": list(
            _canonical_plan_features(
                subscription.get(
                    "plan_features",
                    (),
                )
            )
        ),
        "planCatalogueVersion": (
            _canonical_plan_catalogue_version(
                subscription.get(
                    "plan_catalogue_version"
                )
            )
        ),
        "planRef": subscription.get("plan_ref"),
        "tier": subscription.get("tier", ""),
        "status": subscription.get("status", SubscriptionStatus.ACTIVE.value),
        "amount": float(subscription.get("amount", 0)),
        "taxAmount": float(subscription.get("tax_amount", 0)),
        "currency": subscription.get("currency", "ZAR"),
        "billingFrequency": subscription.get("billing_frequency", BillingFrequency.MONTHLY.value),
        "billingMode": subscription.get("billing_mode", "PLATFORM"),
        "onboardingRef": subscription.get("onboarding_ref", ""),
        "sector": subscription.get("sector", ""),
        "region": subscription.get("region", ""),
        "complianceFlags": subscription.get("compliance_flags", {}),
        "currentPeriodStart": subscription.get("current_period_start", datetime.now(timezone.utc).isoformat()),
        "currentPeriodEnd": subscription.get("current_period_end", datetime.now(timezone.utc).isoformat()),
        "idempotencyKey": subscription.get("idempotency_key", ""),
        "sealNonce": subscription.get("seal_nonce", uuid.uuid4().hex),
        "metadata": metadata or {},
    }

    # Sort keys for deterministic output
    sorted_payload = {k: payload[k] for k in sorted(payload.keys())}
    data = hashlib.sha3_512()
    data.update(json.dumps(sorted_payload, sort_keys=True).encode("utf-8"))
    return data.hexdigest().upper()


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN ENTITIES (immutable)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AuditEntry:
    """Immutable audit trail entry."""
    action: AuditAction
    timestamp: datetime
    user: str = "SYSTEM"
    reason: Optional[str] = None
    previous_status: Optional[SubscriptionStatus] = None
    new_status: Optional[SubscriptionStatus] = None
    tier: Optional[PlanTiers] = None
    billing_mode: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    proof_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "timestamp": self.timestamp.isoformat(),
            "user": self.user,
            "reason": self.reason,
            "previousStatus": self.previous_status.value if self.previous_status else None,
            "newStatus": self.new_status.value if self.new_status else None,
            "tier": self.tier.value if self.tier else None,
            "billingMode": self.billing_mode,
            "metadata": self.metadata,
            "proofHash": self.proof_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEntry":
        """Deserialise from a dictionary."""
        action = data.get("action")
        if isinstance(action, str):
            action = AuditAction(action.lower())
        elif action is None:
            action = AuditAction.CREATE   # ✅ default if missing
        prev_status = data.get("previousStatus")
        if isinstance(prev_status, str):
            prev_status = SubscriptionStatus(prev_status.lower())
        new_status = data.get("newStatus")
        if isinstance(new_status, str):
            new_status = SubscriptionStatus(new_status.lower())
        tier = data.get("tier")
        if isinstance(tier, str):
            tier = PlanTiers(tier.upper())
        return cls(
            action=action,
            timestamp=parse_datetime(data.get("timestamp", datetime.now(timezone.utc).isoformat())) or datetime.now(timezone.utc),
            user=data.get("user", "SYSTEM"),
            reason=data.get("reason"),
            previous_status=prev_status,
            new_status=new_status,
            tier=tier,
            billing_mode=data.get("billingMode"),
            metadata=data.get("metadata", {}),
            proof_hash=data.get("proofHash", ""),
        )


@dataclass(frozen=True)
class ProrationLogEntry:
    """Proration history entry."""
    action: str
    previous_amount: float
    new_amount: float
    credit_amount: float = 0.0
    charge_amount: float = 0.0
    net_amount: float = 0.0
    proration_factor: float = 0.0
    days_remaining: int = 0
    total_cycle_days: int = 0
    proof_hash: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "previousAmount": self.previous_amount,
            "newAmount": self.new_amount,
            "creditAmount": self.credit_amount,
            "chargeAmount": self.charge_amount,
            "netAmount": self.net_amount,
            "prorationFactor": self.proration_factor,
            "daysRemaining": self.days_remaining,
            "totalCycleDays": self.total_cycle_days,
            "proofHash": self.proof_hash,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProrationLogEntry":
        """Deserialise from a dictionary."""
        return cls(
            action=data.get("action", ""),
            previous_amount=float(data.get("previousAmount", 0)),
            new_amount=float(data.get("newAmount", 0)),
            credit_amount=float(data.get("creditAmount", 0)),
            charge_amount=float(data.get("chargeAmount", 0)),
            net_amount=float(data.get("netAmount", 0)),
            proration_factor=float(data.get("prorationFactor", 0)),
            days_remaining=int(data.get("daysRemaining", 0)),
            total_cycle_days=int(data.get("totalCycleDays", 0)),
            proof_hash=data.get("proofHash", ""),
            timestamp=parse_datetime(data.get("timestamp", datetime.now(timezone.utc).isoformat())) or datetime.now(timezone.utc),
        )


@dataclass(frozen=True)
class SubscriptionEntity:
    """
    Immutable subscription entity – mirrors Node Subscription document.
    Required fields first (no defaults), then optional with defaults.
    """
    # Required fields
    tenant_id: str
    plan_id: str
    plan: PlanTiers
    amount: float
    currency: str
    billing_frequency: BillingFrequency
    start_date: datetime
    current_period_start: datetime
    current_period_end: datetime
    idempotency_key: str

    # Optional fields with defaults
    subscription_id: str = field(default_factory=lambda: f"WILSYSUB-{uuid.uuid4().hex[:8].upper()}")
    kennel_shard: str = "EOS_PRIMARY"
    tenant_ref: Optional[str] = None
    billing_ref: Optional[str] = None
    plan_ref: Optional[str] = None
    plan_name: Optional[str] = None
    plan_features: Tuple[str, ...] = field(default_factory=tuple)
    plan_catalogue_version: Optional[int] = None
    tax_amount: float = 0.0
    collection_method: CollectionMethod = CollectionMethod.CHARGE_AUTOMATICALLY
    trial_end_date: Optional[datetime] = None
    cancel_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    resumed_at: Optional[datetime] = None
    reactivated_at: Optional[datetime] = None
    next_billing_at: Optional[datetime] = None
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    cancel_reason: Optional[str] = None
    pause_reason: Optional[str] = None
    pause_until: Optional[datetime] = None
    payment_method_id: Optional[str] = None
    credit_balance: float = 0.0
    last_invoice_id: Optional[str] = None
    last_platform_invoice_id: Optional[str] = None
    proration_log: List[ProrationLogEntry] = field(default_factory=list)
    seal_nonce: str = field(default_factory=lambda: uuid.uuid4().hex)
    proof_hash: str = ""
    merkle_root: str = ""
    trace_id: Optional[str] = None
    audit_trail: List[AuditEntry] = field(default_factory=list)
    tier: Optional[PlanTiers] = None
    onboarding_ref: Optional[str] = None
    billing_mode: str = "PLATFORM"
    end_date: Optional[datetime] = None
    sector: Optional[str] = None
    region: Optional[str] = None
    compliance_flags: Dict[str, bool] = field(default_factory=lambda: {
        "popia": False,
        "gdpr": False,
        "soc2": False,
        "iso27001": False,
    })
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    legacy_proof_hash: str = ""
    legacy_node_merkle_root: str = ""
    legacy_evidence_status: str = ""
    legacy_audit_trail: Tuple[Dict[str, Any], ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        """Canonicalize immutable catalogue snapshot and subscription evidence."""
        object.__setattr__(
            self,
            "plan_features",
            _canonical_plan_features(
                self.plan_features
            ),
        )

        object.__setattr__(
            self,
            "plan_catalogue_version",
            _canonical_plan_catalogue_version(
                self.plan_catalogue_version
            ),
        )

        legacy_present = bool(
            self.legacy_proof_hash
            or self.legacy_node_merkle_root
            or self.legacy_evidence_status
            or self.legacy_audit_trail
        )

        if legacy_present:
            if self.legacy_evidence_status != (
                "LEGACY_NODE_SUBSCRIPTION_"
                "STRUCTURALLY_CONSISTENT_CONTENT_UNVERIFIED"
            ):
                raise ValueError(
                    "legacy subscription evidence status is invalid"
                )

            _legacy_subscription_sha3(
                self.legacy_proof_hash,
                field_name="legacy_proof_hash",
            )
            _legacy_subscription_sha3(
                self.legacy_node_merkle_root,
                field_name="legacy_node_merkle_root",
            )

        if not self.proof_hash:
            object.__setattr__(
                self,
                "proof_hash",
                self.generate_proof(),
            )

        if not self.merkle_root:
            object.__setattr__(
                self,
                "merkle_root",
                self._compute_merkle_root(),
            )

    def _compute_merkle_root(self) -> str:
        data = f"{self.tenant_id}|{self.proof_hash}|{self.seal_nonce}"
        return hashlib.sha3_512(data.encode("utf-8")).hexdigest().upper()

    def generate_proof(self, action: str = "save", metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate a SHA3‑512 proof of the current state."""
        state = self.to_dict()
        # Convert enums to values
        state["status"] = state["status"].value if isinstance(state["status"], SubscriptionStatus) else state["status"]
        state["billing_frequency"] = state["billing_frequency"].value if isinstance(state["billing_frequency"], BillingFrequency) else state["billing_frequency"]
        state["plan"] = state["plan"].value if isinstance(state["plan"], PlanTiers) else state["plan"]
        state["tier"] = state["tier"].value if isinstance(state["tier"], PlanTiers) else state["tier"]
        # Ensure dates are strings
        for date_field in ["start_date", "current_period_start", "current_period_end", "trial_end_date",
                           "cancel_at", "cancelled_at", "paused_at", "resumed_at", "reactivated_at",
                           "next_billing_at", "end_date"]:
            val = state.get(date_field)
            if val and isinstance(val, datetime):
                state[date_field] = val.isoformat()
        return generate_proof(state, action=action, metadata=metadata)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the subscription to a dictionary (matches Node model)."""
        result = {
            "subscription_id": self.subscription_id,
            "tenant_id": self.tenant_id,
            "kennel_shard": self.kennel_shard,
            "tenant_ref": self.tenant_ref,
            "billing_ref": self.billing_ref,
            "plan": self.plan.value if isinstance(self.plan, PlanTiers) else self.plan,
            "plan_id": self.plan_id,
            "plan_ref": self.plan_ref,
            "plan_name": self.plan_name,
            "plan_features": list(self.plan_features),
            "plan_catalogue_version": self.plan_catalogue_version,
            "billing_frequency": self.billing_frequency.value if isinstance(self.billing_frequency, BillingFrequency) else self.billing_frequency,
            "amount": self.amount,
            "tax_amount": self.tax_amount,
            "currency": self.currency,
            "collection_method": self.collection_method.value if isinstance(self.collection_method, CollectionMethod) else self.collection_method,
            "start_date": self.start_date.isoformat(),
            "trial_end_date": self.trial_end_date.isoformat() if self.trial_end_date else None,
            "current_period_start": self.current_period_start.isoformat(),
            "current_period_end": self.current_period_end.isoformat(),
            "cancel_at": self.cancel_at.isoformat() if self.cancel_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "paused_at": self.paused_at.isoformat() if self.paused_at else None,
            "resumed_at": self.resumed_at.isoformat() if self.resumed_at else None,
            "reactivated_at": self.reactivated_at.isoformat() if self.reactivated_at else None,
            "next_billing_at": self.next_billing_at.isoformat() if self.next_billing_at else None,
            "status": self.status.value if isinstance(self.status, SubscriptionStatus) else self.status,
            "cancel_reason": self.cancel_reason,
            "pause_reason": self.pause_reason,
            "pause_until": self.pause_until.isoformat() if self.pause_until else None,
            "payment_method_id": self.payment_method_id,
            "credit_balance": self.credit_balance,
            "last_invoice_id": self.last_invoice_id,
            "last_platform_invoice_id": self.last_platform_invoice_id,
            "proration_log": [pr.to_dict() for pr in self.proration_log] if self.proration_log else [],
            "idempotency_key": self.idempotency_key,
            "seal_nonce": self.seal_nonce,
            "proof_hash": self.proof_hash,
            "merkle_root": self.merkle_root,
            "trace_id": self.trace_id,
            "audit_trail": [audit.to_dict() for audit in self.audit_trail] if self.audit_trail else [],
            "tier": self.tier.value if isinstance(self.tier, PlanTiers) else self.tier,
            "onboarding_ref": self.onboarding_ref,
            "billing_mode": self.billing_mode,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "sector": self.sector,
            "region": self.region,
            "compliance_flags": self.compliance_flags,
            "metadata": self.metadata,
            "tags": self.tags,
            "legacy_proof_hash": self.legacy_proof_hash,
            "legacy_node_merkle_root": self.legacy_node_merkle_root,
            "legacy_evidence_status": self.legacy_evidence_status,
            "legacy_audit_trail": [
                dict(entry)
                for entry in self.legacy_audit_trail
            ],
        }
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubscriptionEntity":
        """Deserialize from a dictionary (inverse of to_dict)."""
        # Parse enums
        plan_val = data.get("plan", "ENTERPRISE")
        if isinstance(plan_val, str):
            plan_enum = PlanTiers(plan_val.upper())
        else:
            plan_enum = plan_val

        billing_freq_val = data.get("billing_frequency", "monthly")
        if isinstance(billing_freq_val, str):
            billing_freq_enum = BillingFrequency(billing_freq_val.lower())
        else:
            billing_freq_enum = billing_freq_val

        collection_method_val = data.get("collection_method", "charge_automatically")
        if isinstance(collection_method_val, str):
            collection_method_enum = CollectionMethod(collection_method_val.lower())
        else:
            collection_method_enum = collection_method_val

        status_val = data.get("status", "active")
        if isinstance(status_val, str):
            status_enum = SubscriptionStatus(status_val.lower())
        else:
            status_enum = status_val

        tier_val = data.get("tier")
        tier_enum = PlanTiers(tier_val.upper()) if tier_val and isinstance(tier_val, str) else tier_val

        # Parse audit trail and proration log using the inner class from_dict
        audit_entries = [AuditEntry.from_dict(entry) for entry in data.get("audit_trail", [])]
        proration_entries = [ProrationLogEntry.from_dict(entry) for entry in data.get("proration_log", [])]

        return cls(
            tenant_id=data["tenant_id"],
            plan_id=data["plan_id"],
            plan=plan_enum,
            amount=float(data["amount"]),
            currency=data["currency"],
            billing_frequency=billing_freq_enum,
            start_date=parse_datetime(data.get("start_date", datetime.now(timezone.utc).isoformat())) or datetime.now(timezone.utc),
            current_period_start=parse_datetime(data.get("current_period_start", datetime.now(timezone.utc).isoformat())) or datetime.now(timezone.utc),
            current_period_end=parse_datetime(data.get("current_period_end", datetime.now(timezone.utc).isoformat())) or datetime.now(timezone.utc),
            idempotency_key=data["idempotency_key"],
            subscription_id=data.get("subscription_id", f"WILSYSUB-{uuid.uuid4().hex[:8].upper()}"),
            kennel_shard=data.get("kennel_shard", "EOS_PRIMARY"),
            tenant_ref=data.get("tenant_ref"),
            billing_ref=data.get("billing_ref"),
            plan_ref=data.get("plan_ref"),
            plan_name=data.get("plan_name"),
            plan_features=_canonical_plan_features(
                data.get("plan_features", ())
            ),
            plan_catalogue_version=(
                _canonical_plan_catalogue_version(
                    data.get("plan_catalogue_version")
                )
            ),
            tax_amount=float(data.get("tax_amount", 0)),
            collection_method=collection_method_enum,
            trial_end_date=parse_datetime(data.get("trial_end_date")),
            cancel_at=parse_datetime(data.get("cancel_at")),
            cancelled_at=parse_datetime(data.get("cancelled_at")),
            paused_at=parse_datetime(data.get("paused_at")),
            resumed_at=parse_datetime(data.get("resumed_at")),
            reactivated_at=parse_datetime(data.get("reactivated_at")),
            next_billing_at=parse_datetime(data.get("next_billing_at")),
            status=status_enum,
            cancel_reason=data.get("cancel_reason"),
            pause_reason=data.get("pause_reason"),
            pause_until=parse_datetime(data.get("pause_until")),
            payment_method_id=data.get("payment_method_id"),
            credit_balance=float(data.get("credit_balance", 0)),
            last_invoice_id=data.get("last_invoice_id"),
            last_platform_invoice_id=data.get("last_platform_invoice_id"),
            proration_log=proration_entries,
            seal_nonce=data.get("seal_nonce", uuid.uuid4().hex),
            proof_hash=data.get("proof_hash", ""),
            merkle_root=data.get("merkle_root", ""),
            trace_id=data.get("trace_id"),
            audit_trail=audit_entries,
            tier=tier_enum,
            onboarding_ref=data.get("onboarding_ref"),
            billing_mode=data.get("billing_mode", "PLATFORM"),
            end_date=parse_datetime(data.get("end_date")),
            sector=data.get("sector"),
            region=data.get("region"),
            compliance_flags=data.get("compliance_flags", {}),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            legacy_proof_hash=data.get(
                "legacy_proof_hash",
                "",
            ),
            legacy_node_merkle_root=data.get(
                "legacy_node_merkle_root",
                "",
            ),
            legacy_evidence_status=data.get(
                "legacy_evidence_status",
                "",
            ),
            legacy_audit_trail=tuple(
                dict(entry)
                for entry in data.get(
                    "legacy_audit_trail",
                    (),
                )
            ),
        )

    @classmethod
    def migrate_legacy_dict(
        cls,
        data: Dict[str, Any],
        *,
        canonical_tenant_id: str,
        canonical_plan_id: str,
    ) -> "SubscriptionEntity":
        """Project one sufficiently evidenced legacy Node row into current truth.

        Missing commercial, lifecycle, temporal, idempotency or proof evidence
        is rejected. Historical Node proof content remains explicitly
        unverified; only its persisted merkle relationship is authenticated.
        """
        if not isinstance(data, dict):
            raise TypeError(
                "legacy subscription data must be a dictionary"
            )

        if {
            "_registry_schema",
            "_registry_revision",
            "tenant_id",
            "subscription_id",
            "idempotency_key",
            "proof_hash",
            "merkle_root",
            "legacy_evidence_status",
        }.intersection(data):
            raise ValueError(
                "legacy migration accepts only unversioned records"
            )

        required = (
            "tenantId",
            "plan",
            "planId",
            "amount",
            "currency",
            "billingFrequency",
            "status",
            "startDate",
            "currentPeriodStart",
            "currentPeriodEnd",
            "idempotencyKey",
            "sealNonce",
            "proofHash",
            "merkleRoot",
        )
        missing = [
            key
            for key in required
            if data.get(key) is None
            or (
                isinstance(data.get(key), str)
                and not data[key].strip()
            )
        ]
        if missing:
            raise ValueError(
                "legacy subscription evidence incomplete: "
                + ", ".join(missing)
            )

        tenant_id = canonical_tenant_id.strip()
        plan_id = canonical_plan_id.strip()
        if not tenant_id:
            raise ValueError("canonical_tenant_id is required")
        if not plan_id:
            raise ValueError("canonical_plan_id is required")

        legacy_tenant_id = str(data["tenantId"]).strip()
        legacy_plan_id = str(data["planId"]).strip()
        legacy_proof = _legacy_subscription_sha3(
            data["proofHash"],
            field_name="proofHash",
        )
        legacy_merkle = _legacy_subscription_sha3(
            data["merkleRoot"],
            field_name="merkleRoot",
        )
        seal_nonce = str(data["sealNonce"]).strip()

        try:
            plan = PlanTiers(str(data["plan"]).upper())
            frequency = BillingFrequency(
                str(data["billingFrequency"]).lower()
            )
            status = SubscriptionStatus(
                str(data["status"]).lower()
            )
            amount = float(data["amount"])
        except (TypeError, ValueError) as error:
            raise ValueError(
                "legacy subscription evidence incomplete: "
                "commercial coordinate"
            ) from error

        if isinstance(data["amount"], bool):
            raise ValueError(
                "legacy subscription evidence incomplete: amount"
            )

        start_date = _legacy_subscription_datetime(
            data,
            "startDate",
        )
        period_start = _legacy_subscription_datetime(
            data,
            "currentPeriodStart",
        )
        period_end = _legacy_subscription_datetime(
            data,
            "currentPeriodEnd",
        )
        if period_end <= period_start:
            raise ValueError(
                "legacy subscription evidence incomplete: period ordering"
            )

        raw_audit = data.get("auditTrail") or ()
        if not isinstance(raw_audit, (list, tuple)) or not all(
            isinstance(entry, dict)
            for entry in raw_audit
        ):
            raise ValueError(
                "legacy subscription evidence incomplete: auditTrail"
            )

        legacy_audit = tuple(
            _legacy_subscription_json_value(entry)
            for entry in raw_audit
        )

        legacy_status = (
            "LEGACY_NODE_SUBSCRIPTION_"
            "STRUCTURALLY_CONSISTENT_CONTENT_UNVERIFIED"
        )
        seed = _legacy_subscription_seed(
            data,
            canonical_tenant_id=tenant_id,
            canonical_plan_id=plan_id,
        )
        migration_metadata = {
            "legacyEvidenceStatus": legacy_status,
            "legacySourceId": str(data.get("_id", "")),
            "legacyTenantId": legacy_tenant_id,
            "legacyPlanId": legacy_plan_id,
            "legacyProofHash": legacy_proof,
            "legacyNodeMerkleRoot": legacy_merkle,
        }

        provisional = cls(
            tenant_id=tenant_id,
            plan_id=plan_id,
            plan=plan,
            amount=amount,
            currency=str(data["currency"]).strip().upper(),
            billing_frequency=frequency,
            start_date=start_date,
            current_period_start=period_start,
            current_period_end=period_end,
            idempotency_key=str(data["idempotencyKey"]).strip(),
            subscription_id="WILSYSUB-LEGACY-" + seed[:24],
            kennel_shard=str(
                data.get("kennelShard") or "EOS_PRIMARY"
            ).strip(),
            plan_name=(
                str(data["planName"]).strip()
                if data.get("planName") is not None
                else None
            ),
            plan_features=_canonical_plan_features(
                data.get("planFeatures") or ()
            ),
            plan_catalogue_version=None,
            status=status,
            seal_nonce=seal_nonce,
            tier=(
                PlanTiers(str(data["tier"]).upper())
                if data.get("tier")
                else plan
            ),
            billing_mode=str(
                data.get("billingMode") or "PLATFORM"
            ).strip(),
            metadata=dict(data.get("metadata") or {}),
            tags=list(data.get("tags") or []),
            legacy_proof_hash=legacy_proof,
            legacy_node_merkle_root=legacy_merkle,
            legacy_evidence_status=legacy_status,
            legacy_audit_trail=legacy_audit,
        )

        canonical_proof = provisional.generate_proof(
            action=AuditAction.CREATE.value,
            metadata=migration_metadata,
        )
        canonical_merkle = hashlib.sha3_512(
            (
                f"{tenant_id}|"
                f"{canonical_proof}|"
                f"{seal_nonce}"
            ).encode("utf-8")
        ).hexdigest().upper()

        audit_timestamp = start_date
        if raw_audit:
            audit_timestamp = _legacy_subscription_datetime(
                raw_audit[-1],
                "timestamp",
            )

        return cls(
            **{
                **provisional.__dict__,
                "proof_hash": canonical_proof,
                "merkle_root": canonical_merkle,
                "audit_trail": [
                    AuditEntry(
                        action=AuditAction.CREATE,
                        timestamp=audit_timestamp,
                        user="SYSTEM",
                        reason=(
                            "Canonical Python EOS migration projection "
                            "of legacy Node subscription evidence"
                        ),
                        previous_status=None,
                        new_status=status,
                        tier=provisional.tier,
                        billing_mode=provisional.billing_mode,
                        metadata=migration_metadata,
                        proof_hash=canonical_proof,
                    )
                ],
            }
        )



    def to_platform_invoice_seed(self) -> Dict[str, Any]:
        """Generate seed for PlatformInvoice (mirrors Node toPlatformInvoiceSeed)."""
        return {
            "_id": self.subscription_id,
            "tenantId": self.tenant_id,
            "kennelShard": self.kennel_shard,
            "planId": self.plan_id,
            "planCatalogueVersion": self.plan_catalogue_version,
            "planName": self.plan_name or self.plan.value,
            "plan": self.plan.value,
            "planTier": self.plan.value,
            "tier": self.tier.value if self.tier else self.plan.value,
            "billingFrequency": self.billing_frequency.value,
            "planFeatures": list(self.plan_features),
            "amount": self.amount,
            "taxAmount": self.tax_amount,
            "currency": self.currency,
            "collectionMethod": self.collection_method.value,
            "billingMode": self.billing_mode,
            "onboardingRef": self.onboarding_ref,
            "sector": self.sector,
            "region": self.region,
            "complianceFlags": self.compliance_flags,
            "startDate": self.start_date.isoformat(),
            "currentPeriodStart": self.current_period_start.isoformat(),
            "currentPeriodEnd": self.current_period_end.isoformat(),
            "proofHash": self.proof_hash,
            "traceId": self.trace_id,
        }

    def generate_evidence_package(self) -> Dict[str, Any]:
        """Generate evidence package (mirrors Node generateEvidencePackage)."""
        safe_metadata = {k: v for k, v in self.metadata.items() if k not in [
            "pii", "email", "userEmail", "phone", "ipAddress", "fullName", "name", "nationalId", "customerEmail", "customerPhone"
        ]}
        package = {
            "_id": self.subscription_id,
            "tenantId": self.tenant_id,
            "kennelShard": self.kennel_shard,
            "tenantRef": self.tenant_ref,
            "billingRef": self.billing_ref,
            "plan": self.plan.value,
            "planId": self.plan_id,
            "planCatalogueVersion": self.plan_catalogue_version,
            "planRef": self.plan_ref,
            "planName": self.plan_name,
            "planFeatures": list(self.plan_features),
            "tier": self.tier.value if self.tier else None,
            "billingFrequency": self.billing_frequency.value,
            "billingMode": self.billing_mode,
            "onboardingRef": self.onboarding_ref,
            "sector": self.sector,
            "region": self.region,
            "complianceFlags": self.compliance_flags,
            "amount": self.amount,
            "taxAmount": self.tax_amount,
            "currency": self.currency,
            "mrr": to_monthly_amount(self.amount, self.billing_frequency),
            "arr": to_annual_amount(self.amount, self.billing_frequency),
            "billingModeSplit": {
                "platformARR": to_annual_amount(self.amount, self.billing_frequency) if self.billing_mode == "PLATFORM" else 0,
                "clientARR": to_annual_amount(self.amount, self.billing_frequency) if self.billing_mode == "CLIENT" else 0,
                "platformMRR": to_monthly_amount(self.amount, self.billing_frequency) if self.billing_mode == "PLATFORM" else 0,
                "clientMRR": to_monthly_amount(self.amount, self.billing_frequency) if self.billing_mode == "CLIENT" else 0,
            },
            "status": self.status.value,
            "startDate": self.start_date.isoformat(),
            "trialEndDate": self.trial_end_date.isoformat() if self.trial_end_date else None,
            "currentPeriodStart": self.current_period_start.isoformat(),
            "currentPeriodEnd": self.current_period_end.isoformat(),
            "nextBillingAt": self.next_billing_at.isoformat() if self.next_billing_at else None,
            "cancelAt": self.cancel_at.isoformat() if self.cancel_at else None,
            "cancelledAt": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "pausedAt": self.paused_at.isoformat() if self.paused_at else None,
            "resumedAt": self.resumed_at.isoformat() if self.resumed_at else None,
            "reactivatedAt": self.reactivated_at.isoformat() if self.reactivated_at else None,
            "creditBalance": self.credit_balance,
            "lastInvoiceId": self.last_invoice_id,
            "lastPlatformInvoiceId": self.last_platform_invoice_id,
            "idempotencyKey": self.idempotency_key,
            "sealNonce": self.seal_nonce,
            "proofHash": self.proof_hash,
            "merkleRoot": self.merkle_root,
            "traceId": self.trace_id,
            "auditTrail": [audit.to_dict() for audit in self.audit_trail],
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "compliance": {"popia": True, "gdpr": True, "soc2": True, "iso27001": True},
            "metadata": safe_metadata,
        }
        # Compute evidence seal
        raw = json.dumps(package, sort_keys=True)
        package["evidenceSeal"] = hashlib.sha3_512(raw.encode("utf-8")).hexdigest().upper()
        return package


def verify_subscription_integrity(
    subscription: SubscriptionEntity,
) -> bool:
    """Verify canonical subscription proof provenance and merkle integrity.

    A directly constructed value with no audit trail uses the domain's
    deterministic default proof. A persisted Registry value must carry its
    latest operation and proof metadata in the latest ``AuditEntry``; that
    provenance is then replayed exactly before the merkle root is checked.
    This function is pure, tenant-neutral, and grants no entitlement or
    financial authority.
    """
    if type(subscription) is not SubscriptionEntity:
        return False
    try:
        if subscription.audit_trail:
            latest = subscription.audit_trail[-1]
            expected_proof = subscription.generate_proof(
                action=latest.action.value,
                metadata=dict(latest.metadata),
            )
            if not isinstance(latest.proof_hash, str) or not hmac.compare_digest(
                subscription.proof_hash.upper(), latest.proof_hash.upper()
            ):
                return False
        else:
            expected_proof = subscription.generate_proof()
        if not isinstance(subscription.proof_hash, str) or not hmac.compare_digest(
            subscription.proof_hash.upper(), expected_proof.upper()
        ):
            return False
        expected_merkle = subscription._compute_merkle_root()
        return isinstance(subscription.merkle_root, str) and hmac.compare_digest(
            subscription.merkle_root.upper(), expected_merkle.upper()
        )
    except (AttributeError, TypeError, ValueError, KeyError):
        return False


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tools/eos/saas/domain/subscription.py
# VERSION: v1.3.0-LEGACY-SUBSCRIPTION-MIGRATION
# AUTHORITY BOUNDARY: Immutable subscription value, lifecycle and catalogue-
# snapshot evidence only; PlanEntity/PlanRegistry remain canonical plan truth.
# TENANT POSTURE: tenant_id is persisted subscription scope and never establishes
# authentication, membership, role or permission authority.
# FAIL-CLOSED POSTURE: Invalid catalogue-version coordinates, malformed
# catalogue feature snapshots, naive calendar datetimes and invalid calendar
# coordinates are rejected. Unknown legacy provenance remains explicit None.
# Calendar helpers derive evidence only; they grant no caller proration authority.
# Canonical proof verification replays persisted audit provenance and grants no
# entitlement, membership, permission, payment or execution authority.
# FINANCIAL EXECUTION AUTHORITY: NONE — Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
