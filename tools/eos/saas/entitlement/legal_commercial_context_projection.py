"""WILSY OS server-owned Legal Operations commercial-context projection.

TITLE:
    WILSY OS Legal Operations Commercial Context Projection

VERSION:
    v1.0.1-SOVEREIGN-LEGAL-COMMERCIAL-CONTEXT

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Conjoin exact current Legal Operations tenant-product availability with
    canonical active subscription commercial evidence while preserving strict
    separation from IAM, Legal command authority, payment execution and
    settlement authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/entitlement/legal_commercial_context_projection.py

COLLABORATION / OWNERSHIP:
    Wilsy OS Core Engineering.
    D22B5 owns current Legal product-availability projection.
    SubscriptionRegistry owns canonical subscription persistence/hydration.
    SubscriptionEntity owns immutable subscription commercial evidence.
    This artifact owns only the bounded descriptive conjunction.

CERTIFICATION / UPDATE DATE:
    2026-10-16

CHANGELOG:
    v1.0.1-SOVEREIGN-LEGAL-COMMERCIAL-CONTEXT
        - Aligns the artifact with AGENTS.md sovereign production-file contract.
        - Preserves the already-certified runtime projection semantics.
        - Adds complete governance, tenant, authority, financial and fail-closed
          declarations plus the mandatory sovereign end seal.

    v1.0.0-LEGAL-COMMERCIAL-CONTEXT
        - Established exact Legal entitlement/subscription conjunction.
        - Added server-derived monthly-equivalent commercial evidence.
        - Rejected ambiguous, mismatched and cross-tenant commercial truth.

COMPLIANCE:
    POPIA section 19 technical controls.
    GDPR Article 32 technical controls.
    SOC 2 CC7.2-aligned technical controls.
    ISO 27001-aligned security controls.
    No independent legal-compliance claim is created by this artifact.

SECURITY / PRIVACY POSTURE:
    Projects bounded tenant-commercial evidence only. It does not expose
    credentials, payment destinations, settlement data or unrelated tenant
    commercial truth. Invalid, ambiguous or corrupted authority fails closed.

TENANT BOUNDARY:
    tenant_id is exact upstream-authorized scope. Subscription hydration and
    Legal product availability remain tenant-scoped. Cross-tenant evidence
    never becomes lawful absence or compatible commercial truth.

AUTHORITY BOUNDARY:
    Descriptive commercial projection only. Product availability, plan,
    subscription and price evidence do not grant principal permissions,
    business roles, Legal lifecycle mutation, workspace admission or command
    authority.

FINANCIAL AUTHORITY BOUNDARY:
    monthly_equivalent_amount is descriptive normalized commercial evidence
    only. APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED.
    Kennel EOS remains the exclusive financial execution authority.

TRANSACTION BOUNDARY:
    The caller owns the active transaction/session lifecycle. This artifact
    propagates the supplied session unchanged and never starts, commits,
    aborts or retries a transaction.

FAIL-CLOSED POSTURE:
    Invalid tenant/commercial state, dependency failure, multiple active Legal
    subscriptions, entitlement/subscription disagreement, foreign tenant
    evidence or malformed canonical values reject. Lawful absence is projected
    only where both Legal product entitlement and active Legal subscription are
    absent.

CONSTITUTION:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
    DISCOVER -> MAP -> WIRE -> CLEAN -> CERTIFY -> OBSERVE -> INTELLIGENCE
    -> EVOLVE.
    NO EVIDENCE = NO FACT.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Final, NoReturn

from tools.eos.saas.billing.subscription_registry import (
    SubscriptionRegistry,
    SubscriptionRegistryError,
)
from tools.eos.saas.domain.subscription import (
    BillingFrequency,
    PlanTiers,
    SubscriptionEntity,
    SubscriptionStatus,
    to_monthly_amount,
)
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
)
from tools.eos.saas.entitlement.legal_product_availability_projection import (
    LegalProductAvailabilityProjectionError,
    resolve_legal_product_availability,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId


VERSION: Final[str] = "v1.0.1-SOVEREIGN-LEGAL-COMMERCIAL-CONTEXT"
LEGAL_FEATURE: Final[str] = "legal.core"


class LegalCommercialContextProjectionError(RuntimeError):
    """Stable fail-closed commercial-context projection error."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True, slots=True)
class LegalCommercialContextProjection:
    """Immutable Legal product + subscription commercial description."""

    tenant_id: str
    product_id: TenantProductId
    workspace_key: str
    entitlement_id: str
    entitlement_state: TenantProductEntitlementState | None
    product_available: bool
    subscription_id: str | None
    subscription_status: SubscriptionStatus | None
    plan_id: str | None
    plan_tier: PlanTiers | None
    plan_name: str | None
    plan_features: tuple[str, ...]
    plan_catalogue_version: int | None
    amount: float | None
    currency: str | None
    billing_frequency: BillingFrequency | None
    monthly_equivalent_amount: float | None
    current_period_end: datetime | None


def _raise(
    code: str,
    message: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = LegalCommercialContextProjectionError(code, message)
    if cause is None:
        raise error
    raise error from cause


def _active_legal_subscriptions(
    values: tuple[SubscriptionEntity, ...],
) -> tuple[SubscriptionEntity, ...]:
    """Return exact ACTIVE subscriptions whose canonical snapshot includes Legal."""
    return tuple(
        value
        for value in values
        if (
            isinstance(value, SubscriptionEntity)
            and value.status is SubscriptionStatus.ACTIVE
            and LEGAL_FEATURE in value.plan_features
        )
    )


def resolve_legal_commercial_context(
    tenant_id: str,
    subscription_collection: Any,
    entitlement_history_collection: Any,
    entitlement_current_collection: Any,
    *,
    session: Any,
) -> LegalCommercialContextProjection:
    """Resolve one fail-closed Legal commercial context for an exact tenant."""
    try:
        availability = resolve_legal_product_availability(
            tenant_id,
            entitlement_history_collection,
            entitlement_current_collection,
            session=session,
        )
    except LegalProductAvailabilityProjectionError as error:
        _raise(
            "LEGAL_COMMERCIAL_PRODUCT_AUTHORITY_UNAVAILABLE",
            "Legal product availability could not be established",
            error,
        )

    try:
        subscriptions = SubscriptionRegistry.list_entities(
            tenant_id,
            collection=subscription_collection,
            session=session,
        )
    except SubscriptionRegistryError as error:
        _raise(
            "LEGAL_COMMERCIAL_SUBSCRIPTION_AUTHORITY_UNAVAILABLE",
            "canonical tenant subscription truth could not be established",
            error,
        )

    active_legal = _active_legal_subscriptions(subscriptions)

    if len(active_legal) > 1:
        _raise(
            "LEGAL_COMMERCIAL_ACTIVE_SUBSCRIPTION_AMBIGUOUS",
            "multiple ACTIVE subscriptions contain the Legal commercial feature",
        )

    if availability.available is True and len(active_legal) != 1:
        _raise(
            "LEGAL_COMMERCIAL_ENTITLEMENT_WITHOUT_ACTIVE_SUBSCRIPTION",
            "ACTIVE Legal entitlement lacks one matching ACTIVE subscription",
        )

    if availability.available is not True and active_legal:
        _raise(
            "LEGAL_COMMERCIAL_ACTIVE_SUBSCRIPTION_WITHOUT_ENTITLEMENT",
            "ACTIVE Legal subscription disagrees with current product entitlement",
        )

    if not active_legal:
        return LegalCommercialContextProjection(
            tenant_id=availability.tenant_id,
            product_id=availability.product_id,
            workspace_key=availability.workspace_key,
            entitlement_id=availability.entitlement_id,
            entitlement_state=availability.lifecycle_state,
            product_available=False,
            subscription_id=None,
            subscription_status=None,
            plan_id=None,
            plan_tier=None,
            plan_name=None,
            plan_features=(),
            plan_catalogue_version=None,
            amount=None,
            currency=None,
            billing_frequency=None,
            monthly_equivalent_amount=None,
            current_period_end=None,
        )

    subscription = active_legal[0]

    if subscription.tenant_id != availability.tenant_id:
        _raise(
            "LEGAL_COMMERCIAL_SUBSCRIPTION_TENANT_MISMATCH",
            "hydrated subscription tenant does not match product authority",
        )

    if not subscription.plan_id or subscription.plan_id != subscription.plan_id.strip():
        _raise(
            "LEGAL_COMMERCIAL_PLAN_ID_INVALID",
            "canonical subscription plan identity is invalid",
        )

    if type(subscription.plan) is not PlanTiers:
        _raise(
            "LEGAL_COMMERCIAL_PLAN_TIER_INVALID",
            "canonical subscription plan tier is invalid",
        )

    if type(subscription.billing_frequency) is not BillingFrequency:
        _raise(
            "LEGAL_COMMERCIAL_BILLING_FREQUENCY_INVALID",
            "canonical subscription billing frequency is invalid",
        )

    if not isinstance(subscription.currency, str) or not subscription.currency:
        _raise(
            "LEGAL_COMMERCIAL_CURRENCY_INVALID",
            "canonical subscription currency is invalid",
        )

    try:
        monthly_amount = to_monthly_amount(
            subscription.amount,
            subscription.billing_frequency,
        )
    except (TypeError, ValueError, OverflowError) as error:
        _raise(
            "LEGAL_COMMERCIAL_MONTHLY_EQUIVALENT_INVALID",
            "monthly-equivalent commercial evidence could not be derived",
            error,
        )

    return LegalCommercialContextProjection(
        tenant_id=availability.tenant_id,
        product_id=availability.product_id,
        workspace_key=availability.workspace_key,
        entitlement_id=availability.entitlement_id,
        entitlement_state=availability.lifecycle_state,
        product_available=True,
        subscription_id=subscription.subscription_id,
        subscription_status=subscription.status,
        plan_id=subscription.plan_id,
        plan_tier=subscription.plan,
        plan_name=subscription.plan_name,
        plan_features=tuple(subscription.plan_features),
        plan_catalogue_version=subscription.plan_catalogue_version,
        amount=subscription.amount,
        currency=subscription.currency,
        billing_frequency=subscription.billing_frequency,
        monthly_equivalent_amount=monthly_amount,
        current_period_end=subscription.current_period_end,
    )


__all__ = [
    "LEGAL_FEATURE",
    "LegalCommercialContextProjection",
    "LegalCommercialContextProjectionError",
    "VERSION",
    "resolve_legal_commercial_context",
]

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_commercial_context_projection.py
# VERSION: v1.0.1-SOVEREIGN-LEGAL-COMMERCIAL-CONTEXT
# AUTHORITY BOUNDARY: descriptive Legal commercial context only; no IAM, Legal command, payment execution or settlement authority
# TENANT POSTURE: exact tenant-scoped entitlement and canonical subscription evidence only
# FAIL-CLOSED POSTURE: ambiguity, mismatch, corruption and dependency failure reject; no synthetic commercial truth
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
