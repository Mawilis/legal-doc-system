"""
TITLE: WILSY OS Subscription Term Decision Policy
VERSION: v1.0.0-D22C4-FOUNDER-PERPETUAL-TERM-POLICY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Distinguish the exact platform Founder subscription from ordinary
         commercial billing-period subscriptions without widening plan features.
ABSOLUTE CANONICAL PATH: tools/eos/saas/billing/subscription_term_policy.py
COLLABORATION / OWNERSHIP: SubscriptionEntity owns persisted subscription truth;
                           this policy classifies its term only.
CERTIFICATION / UPDATE DATE: 2026-10-30
CHANGELOG: v1.0.0 introduces an exact server-controlled Founder binding and
           finite billing-period enforcement for every other subscription.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No caller metadata, role, tenant config, price,
                            or billing-mode flag independently grants Founder.
TENANT BOUNDARY: Founder exception is bound to one exact tenant, subscription,
                 and plan tuple; all other tenants use ordinary terms.
AUTHORITY BOUNDARY: Term classification only; no IAM, entitlement issuance,
                    subscription mutation, payment, or G77 authority.
FINANCIAL AUTHORITY BOUNDARY: No payment or execution authority; Kennel EOS
                              remains exclusive financial execution authority.
FAIL-CLOSED POSTURE: Malformed or naive timestamps reject; terminal and
                     paused/cancel-scheduled Founder subscriptions do not
                     receive the perpetual exception.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from tools.eos.saas.domain.subscription import (
    SubscriptionEntity,
    SubscriptionStatus,
)


VERSION = "v1.0.0-D22C4-FOUNDER-PERPETUAL-TERM-POLICY"

# This is a deployment-controlled platform designation, not a user- or
# tenant-supplied claim. The exact tuple prevents role, metadata, plan-name,
# zero-price, or PLATFORM-mode spoofing from creating perpetual status.
_PLATFORM_FOUNDER_BINDING = (
    "WILSYTENANT-4CD2FZ4O",
    "WILSYSUB-93455E4E",
    "WILSYPLAN-37B8164F",
)


class SubscriptionTermKind(str, Enum):
    """Canonical subscription term classes; classification grants no access."""

    PERPETUAL_PLATFORM_OWNER = "PERPETUAL_PLATFORM_OWNER"
    BILLING_PERIOD = "BILLING_PERIOD"
    EXPIRED_BILLING_PERIOD = "EXPIRED_BILLING_PERIOD"


@dataclass(frozen=True, slots=True)
class SubscriptionTermDecision:
    """Immutable term decision derived from canonical subscription evidence."""

    kind: SubscriptionTermKind
    eligible: bool
    evaluated_at: datetime


class SubscriptionTermPolicyError(ValueError):
    """Raised when subscription term evidence is malformed or unverifiable."""


def _aware_utc(value: datetime, field: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise SubscriptionTermPolicyError(
            f"SUBSCRIPTION_TERM_{field.upper()}_MUST_BE_TIMEZONE_AWARE"
        )
    return value.astimezone(timezone.utc)


def evaluate_subscription_term(
    subscription: SubscriptionEntity,
    *,
    evaluated_at: datetime,
) -> SubscriptionTermDecision:
    """Classify the term of one canonical subscription.

    The perpetual exception applies only to the exact source-controlled
    platform Founder tenant/subscription/plan tuple, while the subscription
    remains ACTIVE, zero-rated, PLATFORM-billed, and not paused, cancelled,
    or scheduled for cancellation. Its ordinary period end is not an expiry
    boundary. Every other subscription is eligible only strictly before its
    timezone-aware current_period_end.

    This function does not authenticate a principal, establish tenant
    ownership, issue an entitlement, or mutate subscription evidence.
    """
    if type(subscription) is not SubscriptionEntity:
        raise SubscriptionTermPolicyError("SUBSCRIPTION_TERM_ENTITY_REQUIRED")

    now = _aware_utc(evaluated_at, "EVALUATED_AT")
    status = subscription.status
    if status is not SubscriptionStatus.ACTIVE:
        return SubscriptionTermDecision(
            SubscriptionTermKind.EXPIRED_BILLING_PERIOD,
            False,
            now,
        )

    founder_coordinates = (
        subscription.tenant_id,
        subscription.subscription_id,
        subscription.plan_id,
    )
    founder_is_exact = (
        founder_coordinates == _PLATFORM_FOUNDER_BINDING
        and subscription.amount == 0
        and subscription.billing_mode == "PLATFORM"
        and subscription.cancelled_at is None
        and subscription.cancel_at is None
        and subscription.paused_at is None
    )
    if founder_is_exact:
        return SubscriptionTermDecision(
            SubscriptionTermKind.PERPETUAL_PLATFORM_OWNER,
            True,
            now,
        )

    period_end = _aware_utc(
        subscription.current_period_end,
        "CURRENT_PERIOD_END",
    )
    if period_end > now:
        return SubscriptionTermDecision(
            SubscriptionTermKind.BILLING_PERIOD,
            True,
            now,
        )
    return SubscriptionTermDecision(
        SubscriptionTermKind.EXPIRED_BILLING_PERIOD,
        False,
        now,
    )


__all__ = [
    "SubscriptionTermDecision",
    "SubscriptionTermKind",
    "SubscriptionTermPolicyError",
    "VERSION",
    "evaluate_subscription_term",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tools/eos/saas/billing/subscription_term_policy.py
# VERSION: v1.0.0-D22C4-FOUNDER-PERPETUAL-TERM-POLICY
# AUTHORITY BOUNDARY: Subscription term classification only; no entitlement,
# IAM, subscription mutation, billing execution, or confidentiality authority.
# TENANT POSTURE: Exact tenant/subscription/plan Founder binding; ordinary
# subscriptions retain finite billing-period semantics.
# FAIL-CLOSED POSTURE: Invalid entities, terminal states and malformed times
# reject; caller-controlled claims cannot create the Founder exception.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
