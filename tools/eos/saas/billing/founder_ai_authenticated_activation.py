"""Authenticated Founder Institutional AI commercial activation.

TITLE: WILSY Founder Institutional AI Authenticated Activation
VERSION: v1.0.1-CANONICAL-INSTITUTIONAL-TIER-READBACK
AUTHORITY: Existing plan:manage AND subscription:manage IAM; canonical P4.
EPITOME: Execute canonical staged commercial amendment, zero-rated subscription
         snapshot, D57B/P4 ACTIVE issuance, and durable source readback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/founder_ai_authenticated_activation.py
COLLABORATION / OWNERSHIP: SubscriptionRouter authenticates both permissions;
  PlanRegistry owns plan CAS and audit; SubscriptionRegistry owns commercial
  snapshot/audit; D57B/P4 own AI entitlement lifecycle; EOS Mongo owns transport.
CERTIFICATION / UPDATE DATE: 2026-11-20
CHANGELOG: v1.0.1-CANONICAL-INSTITUTIONAL-TIER-READBACK matches
  the canonical WilsyAITier.INSTITUTIONAL ACTIVE source readback rather than
  an unrelated display string.
  v1.0.0-EXACT-FOUNDER-AUTHENTICATED-INSTITUTIONAL-ACTIVATION
  adds a permission-scoped, exact Founder, staged, recoverable issuance command.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: No browser-supplied plan, tenant, tier or evidence
  facts; activation proof binds authenticated issuer, durable commercial source
  proofs, the fixed Founder mandate and idempotency key; no secrets are logged.
TENANT BOUNDARY: Exact deployed Founder tuple only; no aliases or name fallbacks.
AUTHORITY BOUNDARY: Requires two independently admitted current IAM permissions;
  no identity, role, entitlement or arbitrary-source self-grant.
TRANSACTION BOUNDARY: PlanRegistry owns its atomic CAS, and subscription and P4
  each run in a separate caller-owned Mongo transaction. Recoverable staged
  commits are verified and never claimed rolled back as a single transaction.
FINANCIAL AUTHORITY BOUNDARY: Every source price/amount must remain zero;
  money and payment execution remain Kennel EOS exclusive.
FAIL-CLOSED DECLARATION: Cross-tenant actor, unverified proof, divergent source,
  unexpected AI tier, stale commercial state or missing P4 readback denies.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Final

from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.billing.founder_ai_entitlement_reconciliation import (
    BRANDING_FEATURE,
    FOUNDER_MANDATED_AI_FEATURE,
    FOUNDER_PLAN_ID,
    FOUNDER_SUBSCRIPTION_ID,
    FOUNDER_TENANT_ID,
    _canonical_plan,
    reconcile_founder_ai_entitlement,
)
from tools.eos.saas.billing.subscription_term_policy import (
    SubscriptionTermKind, evaluate_subscription_term,
)
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import WilsyAIEntitlementRegistry
from tools.eos.saas.billing.wilsy_ai_commercial_policy import WilsyAITier
from tools.eos.saas.billing.wilsy_ai_vas_feature_catalogue import WilsyAIVASFeatureId
from tools.eos.saas.domain.subscription import SubscriptionStatus, verify_subscription_integrity
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlementState

VERSION: Final[str] = "v1.0.1-CANONICAL-INSTITUTIONAL-TIER-READBACK"
_MANDATE_REF: Final[str] = "founder-institutional-ai-commercial-decision-20261120"
_IDEMPOTENCY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9:_-]{16,128}$")


class FounderAIAuthenticatedActivationError(RuntimeError):
    """One bounded error code; no raw exception or source record leaks."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise FounderAIAuthenticatedActivationError(code)


def _sources(database: Any, client: Any, at: datetime) -> tuple[Any, Any]:
    """Rehydrate current authenticated Founder commercial truth in a new txn."""
    with client.start_session() as session:
        with session.start_transaction():
            plan = _canonical_plan(database["plans"], session)
            subscriptions = SubscriptionRegistry.list_entities(
                FOUNDER_TENANT_ID, collection=database["subscriptions"], session=session,
            )
            current = [s for s in subscriptions if s.status is SubscriptionStatus.ACTIVE]
            _require(len(current) == 1, "FOUNDER_AI_SUBSCRIPTION_CARDINALITY_INVALID")
            subscription = current[0]
            _require(
                subscription.tenant_id == FOUNDER_TENANT_ID
                and subscription.subscription_id == FOUNDER_SUBSCRIPTION_ID
                and subscription.plan_id == FOUNDER_PLAN_ID
                and subscription.tier is not None
                and subscription.tier.value == "FOUNDER_ENTERPRISE"
                and subscription.billing_mode == "PLATFORM"
                and subscription.amount == 0
                and verify_subscription_integrity(subscription)
                and evaluate_subscription_term(
                    subscription, evaluated_at=at,
                ).kind is SubscriptionTermKind.PERPETUAL_PLATFORM_OWNER,
                "FOUNDER_AI_SUBSCRIPTION_SOURCE_INVALID",
            )
            _require(
                plan.tenant_id == FOUNDER_TENANT_ID
                and plan.plan_id == FOUNDER_PLAN_ID
                and plan.price == 0
                and plan.active is True
                and plan.plan_type.value == "FOUNDER_ENTERPRISE"
                and BRANDING_FEATURE in plan.features,
                "FOUNDER_AI_PLAN_SOURCE_INVALID",
            )
            competing = [
                feature for feature in WilsyAIVASFeatureId
                if feature is not FOUNDER_MANDATED_AI_FEATURE
                and (
                    feature.value in plan.features
                    or feature.value in subscription.plan_features
                )
            ]
            _require(not competing, "FOUNDER_AI_COMPETING_TIER_REJECTED")
            return plan, subscription


def activate_authenticated_founder_institutional_ai(
    *, tenant_id: str, principal_id: str, idempotency_key: str,
) -> dict[str, Any]:
    """Run after HTTP requires BOTH current plan and subscription permissions.

    This function deliberately has no public HTTP or permission acquisition
    capability. Its only router caller must enforce both IAM dependencies and
    pass their identical membership-admitted identity and tenant. It never
    upgrades another tenant, alters price, or accepts a client-selected tier.
    Retries re-read each stage and resume only the missing canonical stage.
    """
    _require(tenant_id == FOUNDER_TENANT_ID, "FOUNDER_AI_TENANT_NOT_AUTHORIZED")
    _require(
        isinstance(principal_id, str) and bool(principal_id.strip())
        and len(principal_id) <= 128 and principal_id == principal_id.strip(),
        "FOUNDER_AI_AUTHENTICATED_PRINCIPAL_REQUIRED",
    )
    _require(
        isinstance(idempotency_key, str)
        and _IDEMPOTENCY.fullmatch(idempotency_key) is not None,
        "FOUNDER_AI_IDEMPOTENCY_KEY_INVALID",
    )
    client, database = get_client(), get_database()
    _require(client is not None and database is not None,
             "FOUNDER_AI_CANONICAL_MONGO_UNAVAILABLE")
    now = datetime.now(timezone.utc)
    plan, subscription = _sources(database, client, now)

    if FOUNDER_MANDATED_AI_FEATURE.value not in plan.features:
        # A pre-existing subscription must still match the exact old plan
        # before an auditable plan amendment may begin.
        _require(
            tuple(plan.features) == tuple(subscription.plan_features)
            and plan.catalogue_version == subscription.plan_catalogue_version,
            "FOUNDER_AI_PLAN_SOURCE_DIVERGENT",
        )
        evolved = PlanRegistry.update(
            FOUNDER_PLAN_ID, {
                "features": sorted(set(plan.features) | {FOUNDER_MANDATED_AI_FEATURE.value}),
                "user": principal_id,
            }, tenant_id=FOUNDER_TENANT_ID, exact_tenant=True,
        )
        _require(evolved.get("success") is True, "FOUNDER_AI_PLAN_CAS_FAILED")
        plan, subscription = _sources(database, client, now)

    _require(
        FOUNDER_MANDATED_AI_FEATURE.value in plan.features,
        "FOUNDER_AI_PLAN_FEATURE_NOT_VERIFIED",
    )
    if (
        tuple(subscription.plan_features) != tuple(plan.features)
        or subscription.plan_catalogue_version != plan.catalogue_version
    ):
        # Only the exact one-feature, one-version pending step is admissible.
        _require(
            tuple(sorted(subscription.plan_features))
            == tuple(sorted(
                feature for feature in plan.features
                if feature != FOUNDER_MANDATED_AI_FEATURE.value
            ))
            and plan.catalogue_version == subscription.plan_catalogue_version + 1,
            "FOUNDER_AI_SUBSCRIPTION_SOURCE_DIVERGENT",
        )
        with client.start_session() as session:
            with session.start_transaction():
                result = SubscriptionRegistry.upgrade(
                    FOUNDER_SUBSCRIPTION_ID, FOUNDER_TENANT_ID,
                    {"newPlanId": FOUNDER_PLAN_ID},
                    collection=database["subscriptions"], session=session,
                )
                _require(result.get("success") is True,
                         "FOUNDER_AI_SUBSCRIPTION_SNAPSHOT_FAILED")
                new_sub = result["subscription"]
                _require(
                    new_sub.amount == 0
                    and tuple(new_sub.plan_features) == tuple(plan.features)
                    and new_sub.plan_catalogue_version == plan.catalogue_version,
                    "FOUNDER_AI_SUBSCRIPTION_NEW_SOURCE_INVALID",
                )
        plan, subscription = _sources(database, client, now)

    _require(
        tuple(plan.features) == tuple(subscription.plan_features)
        and plan.catalogue_version == subscription.plan_catalogue_version
        and subscription.amount == 0,
        "FOUNDER_AI_COMMERCIAL_READBACK_INVALID",
    )

    evidence = {
        "kind": "FOUNDER_INSTITUTIONAL_AI_AUTHENTICATED_ACTIVATION/V1",
        "mandate": _MANDATE_REF,
        "tenant_id": FOUNDER_TENANT_ID,
        "subscription_id": FOUNDER_SUBSCRIPTION_ID,
        "plan_id": FOUNDER_PLAN_ID,
        "feature_id": FOUNDER_MANDATED_AI_FEATURE.value,
        "principal_id": principal_id,
        "idempotency_key": idempotency_key,
        "plan_proof": plan.proof_hash,
        "subscription_proof": subscription.proof_hash,
        "zero_rated": True,
    }
    fingerprint = hashlib.sha3_512(
        json.dumps(evidence, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=True, allow_nan=False).encode("utf-8"),
    ).hexdigest()
    with client.start_session() as session:
        with session.start_transaction():
            result = reconcile_founder_ai_entitlement(
                subscription_collection=database["subscriptions"],
                plan_collection=database["plans"],
                entitlement_collection=database["wilsy_ai_entitlements"],
                session=session, idempotency_key=idempotency_key,
                feature_id=FOUNDER_MANDATED_AI_FEATURE, apply=True,
                activation_evidence_reference=_MANDATE_REF,
                activation_evidence_fingerprint=fingerprint,
                occurred_at=datetime.now(timezone.utc),
            )
    with client.start_session() as session:
        readback = WilsyAIEntitlementRegistry(
            database["wilsy_ai_entitlements"],
        ).get_by_module(
            tenant_id=FOUNDER_TENANT_ID,
            module_id="WILSY_AI_REASONING", session=session,
        )
    _require(
        result.lifecycle == "ACTIVE"
        and readback.lifecycle_state is WilsyAIEntitlementState.ACTIVE
        and readback.tenant_id == FOUNDER_TENANT_ID
        and readback.entitlement_id == result.entitlement_id
        and readback.tier is WilsyAITier.INSTITUTIONAL,
        "FOUNDER_AI_ACTIVE_ENTITLEMENT_READBACK_FAILED",
    )
    return {
        "tenant_id": FOUNDER_TENANT_ID,
        "subscription_id": FOUNDER_SUBSCRIPTION_ID,
        "feature_id": FOUNDER_MANDATED_AI_FEATURE.value,
        "entitlement_id": readback.entitlement_id,
        "entitlement_state": "ACTIVE",
        "zero_rated_subscription": True,
        "source_verified": True,
        "activated_this_request": result.applied,
    }


__all__ = [
    "VERSION", "FounderAIAuthenticatedActivationError",
    "activate_authenticated_founder_institutional_ai",
]

# ARTIFACT: founder_ai_authenticated_activation.py
# VERSION: v1.0.1-CANONICAL-INSTITUTIONAL-TIER-READBACK
# AUTHORITY BOUNDARY: dual IAM required at router; canonical registries only
# TENANT POSTURE: exact Founder tuple, never aliased
# FAIL-CLOSED POSTURE: stage CAS, proof and ACTIVE readback are mandatory
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
