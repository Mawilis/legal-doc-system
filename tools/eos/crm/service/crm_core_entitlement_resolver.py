"""
TITLE: WILSY OS CRM Core Entitlement Resolver
VERSION: v1.0.1-P0-CRM-CORE-ENTITLEMENT-RESOLVER-PROOF-ACTIVATION-EVIDENCE-CONVERGENCE

CHANGELOG:
    - 2026-10-07 v1.0.1-P0-CRM-CORE-ENTITLEMENT-RESOLVER-PROOF-ACTIVATION-EVIDENCE-CONVERGENCE: converges resolver commercial-proof handling with canonical uppercase SubscriptionEntity SHA3-512 proof bytes and derives separate lowercase SHA3-512 activation lifecycle evidence from those exact bytes. The Subscription proof is never normalized or mutated; entitlement-domain lifecycle digest semantics remain unchanged. No send, AI, permission-grant, billing, payment, settlement, or financial-execution authority is introduced.

AUTHORITY:
    Server-derived CRM Core commercial-entitlement resolution.

PURPOSE:
    Resolve whether one already-authorized tenant has exact ``crm.core``
    entitlement from canonical persisted subscription truth.

SOURCE OF TRUTH:
    SubscriptionRegistry.list_entities(
        already-authorized tenant,
        authoritative subscription collection,
        caller-owned session,
    )

FAIL-CLOSED POSTURE:
    - zero ACTIVE subscriptions => no entitlement;
    - more than one ACTIVE subscription => ambiguous commercial authority;
    - exactly one ACTIVE subscription without exact ``crm.core`` => no
      entitlement;
    - plan tier, price, UI state and caller assertions are never entitlement
      authority.

TRANSACTION POSTURE:
    The resolver forwards the exact caller-owned session. It never starts,
    commits, aborts or otherwise owns Mongo transaction lifecycle.

EVIDENCE POSTURE:
    ACTIVE CrmCoreEntitlement evidence is derived from the canonical
    SubscriptionEntity subscription / plan / catalogue / proof coordinates.

EXECUTION BOUNDARY:
    This module grants no mailbox, send, consent, suppression, sequence,
    AI-send, payment, settlement or financial-execution authority.

FINANCIAL AUTHORITY:
    None. Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Final

from tools.eos.crm.domain.crm_core_entitlement import (
    CRM_CORE_FEATURE_ID,
    CrmCoreEntitlement,
    CrmCoreEntitlementState,
)
from tools.eos.saas.billing.subscription_registry import (
    SubscriptionRegistry,
)
from tools.eos.saas.domain.subscription import (
    SubscriptionEntity,
    SubscriptionStatus,
)


CRM_CORE_ENTITLEMENT_RESOLVER_VERSION: Final[str] = (
    "v1.0.1-P0-CRM-CORE-ENTITLEMENT-RESOLVER-PROOF-ACTIVATION-EVIDENCE-CONVERGENCE"
)


class CrmCoreEntitlementResolverError(RuntimeError):
    """Raised when authoritative CRM entitlement cannot be resolved safely."""


def _active_subscription(
    subscriptions: tuple[SubscriptionEntity, ...],
) -> SubscriptionEntity | None:
    """Return exactly one ACTIVE subscription or fail closed."""
    active = tuple(
        subscription
        for subscription in subscriptions
        if subscription.status is SubscriptionStatus.ACTIVE
    )

    if not active:
        return None

    if len(active) != 1:
        raise CrmCoreEntitlementResolverError(
            "CRM_CORE_ENTITLEMENT_SUBSCRIPTION_AMBIGUOUS"
        )

    return active[0]


def _activation_reference(
    subscription: SubscriptionEntity,
) -> str:
    """Bind entitlement activation to canonical subscription truth."""
    return (
        "crm-core-entitlement:"
        + subscription.tenant_id
        + ":"
        + subscription.subscription_id
        + ":"
        + subscription.plan_id
    )


def _pending_entitlement(
    subscription: SubscriptionEntity,
) -> CrmCoreEntitlement:
    """Construct strict PENDING_SOURCE evidence from canonical subscription."""
    if (
        isinstance(subscription.plan_catalogue_version, bool)
        or not isinstance(
            subscription.plan_catalogue_version,
            int,
        )
        or subscription.plan_catalogue_version < 1
    ):
        raise CrmCoreEntitlementResolverError(
            "CRM_CORE_ENTITLEMENT_CATALOGUE_VERSION_INVALID"
        )

    if (
        not isinstance(subscription.proof_hash, str)
        or len(subscription.proof_hash) != 128
        or subscription.proof_hash
        != subscription.proof_hash.upper()
        or any(
            character not in "0123456789ABCDEF"
            for character in subscription.proof_hash
        )
    ):
        raise CrmCoreEntitlementResolverError(
            "CRM_CORE_ENTITLEMENT_SUBSCRIPTION_PROOF_INVALID"
        )

    return CrmCoreEntitlement(
        tenant_id=subscription.tenant_id,
        entitlement_id=(
            "crm.core:"
            + subscription.subscription_id
        ),
        feature_id=CRM_CORE_FEATURE_ID,
        subscription_id=subscription.subscription_id,
        plan_id=subscription.plan_id,
        plan_catalogue_version=(
            subscription.plan_catalogue_version
        ),
        subscription_proof_hash=subscription.proof_hash,
        lifecycle_state=(
            CrmCoreEntitlementState.PENDING_SOURCE
        ),
    )


def resolve_crm_core_entitlement(
    tenant_id: str,
    subscription_collection: Any,
    session: Any,
) -> CrmCoreEntitlement | None:
    """Resolve exact ACTIVE CRM Core entitlement from canonical tenant truth.

    ``tenant_id`` must already be authorized upstream. The caller cannot
    supply subscription identity, plan identity, plan tier or entitlement
    state. All subscription rows are retrieved through the canonical registry
    using the exact caller-owned session.

    ``None`` is a governed denial: either no ACTIVE subscription exists or the
    sole ACTIVE subscription does not carry exact ``crm.core`` in its immutable
    plan-feature snapshot.

    Multiple ACTIVE rows are not resolved heuristically. They are ambiguous
    commercial authority and fail closed.
    """
    subscriptions = SubscriptionRegistry.list_entities(
        tenant_id,
        collection=subscription_collection,
        session=session,
    )

    active = _active_subscription(
        subscriptions
    )

    if active is None:
        return None

    if active.tenant_id != tenant_id:
        raise CrmCoreEntitlementResolverError(
            "CRM_CORE_ENTITLEMENT_TENANT_MISMATCH"
        )

    if CRM_CORE_FEATURE_ID not in active.plan_features:
        return None

    pending = _pending_entitlement(active)

    activation_evidence = hashlib.sha3_512(
        active.proof_hash.encode("ascii")
    ).hexdigest()

    return pending.transition(
        CrmCoreEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference=_activation_reference(active),
        evidence_fingerprint=activation_evidence,
        occurred_at=datetime.now(timezone.utc),
    )


__all__ = (
    "CRM_CORE_ENTITLEMENT_RESOLVER_VERSION",
    "CrmCoreEntitlementResolverError",
    "resolve_crm_core_entitlement",
)


# ARTIFACT: crm_core_entitlement_resolver.py
# VERSION: v1.0.1-P0-CRM-CORE-ENTITLEMENT-RESOLVER-PROOF-ACTIVATION-EVIDENCE-CONVERGENCE
# SOURCE: canonical tenant SubscriptionRegistry.list_entities snapshot
# TRANSACTION: exact caller-owned session forwarding; no lifecycle ownership
# ACTIVE SUBSCRIPTION: exactly one required
# ZERO ACTIVE: deny
# MULTIPLE ACTIVE: fail closed
# FEATURE: exact crm.core from immutable plan_features only
# EVIDENCE: subscription / plan / catalogue / proof coordinates bound
# CALLER SUBSCRIPTION / PLAN / TIER / FEATURE ASSERTION: forbidden
# SEND / MAILBOX / CONSENT / AI-SEND AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
