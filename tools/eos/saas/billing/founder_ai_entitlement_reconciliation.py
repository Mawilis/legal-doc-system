"""Exact Founder WILSY AI commercial entitlement reconciliation.

TITLE: WILSY OS Founder AI Entitlement Reconciliation
VERSION: v1.2.1-PLAN-PROOF-BOUND-APPROVAL-INTENT
AUTHORITY: WILSY OS Core Governance; existing subscription and P4 registries.
EPITOME: Enforce exact zero-rated Founder commercial source and activate only an
         explicitly subscribed tier-specific AI feature through existing P4 CAS.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/founder_ai_entitlement_reconciliation.py
COLLABORATION / OWNERSHIP: PlanEntity owns plan state; SubscriptionRegistry owns
                          active subscription proof; D57B derives AI tier and
                          source evidence; P4 owns entitlement lifecycle.
CERTIFICATION / UPDATE DATE: 2026-11-20
CHANGELOG: v1.2.1-PLAN-PROOF-BOUND-APPROVAL-INTENT also binds the
           canonical PlanEntity state proof and integrity-envelope root in the
           nonissuing approval fingerprint to reject stale plan evidence.
           v1.2.0-NONISSUING-SOURCE-BOUND-APPROVAL-INTENT prepares an exact,
           non-issuing SHA3-512 approval intent from canonical Founder plan
           and subscription proofs plus a specifically proposed AI tier;
           signed institutional approval remains external to this intent.
           v1.1.1-CANONICAL-PLAN-REGISTRY-HYDRATION delegates plan
           transport-revision and canonical proof validation to PlanRegistry.
           v1.1.0-EXACT-ACTIVE-ENTITLEMENT-READBACK verifies exact active
           entitlement lineage before accepting an activation replay, so a
           successful retry never issues or activates the module twice.
           v1.0.0-GOVERNED-FOUNDER-AI-RECONCILIATION adds fail-closed exact
           Founder preflight, dry-run, subscription-derived issuance and
           explicit evidence-backed activation within caller-owned transaction.
COMPLIANCE: POPIA s19; GDPR Art32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: No raw source records, secrets, payment information,
                            principal identity or provider payload is exposed.
TENANT BOUNDARY: Exact deployment-controlled Founder binding; unrelated tenants
                 never enter this reconciliation path.
AUTHORITY BOUNDARY: Commercial source check and existing P4 entitlement only;
                    no new principal, permission, plan or subscription grant.
TRANSACTION BOUNDARY: Active caller-owned Mongo session required; this service
                      starts no transaction and never commits, aborts or retries.
FINANCIAL AUTHORITY BOUNDARY: Zero-rated Founder source is verified, not created;
                              Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Absent or divergent features, stale plan snapshot,
                         invalid proof, missing approval evidence and existing
                         incompatible entitlement all reject without fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Final

from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.billing.subscription_wilsy_ai_entitlement_composition_service import (
    _source_evidence,
    compose_subscription_wilsy_ai_entitlement,
    derive_subscription_wilsy_ai_entitlement_id,
)
from tools.eos.saas.billing.subscription_term_policy import (
    SubscriptionTermKind,
    evaluate_subscription_term,
)
from tools.eos.saas.billing.wilsy_ai_entitlement_provisioning import (
    activate_wilsy_ai_reasoning_entitlement,
)
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import (
    WilsyAIEntitlementNotFoundError,
    WilsyAIEntitlementRegistry,
)
from tools.eos.saas.billing.wilsy_ai_vas_feature_catalogue import (
    WilsyAIVASFeatureId,
    resolve_wilsy_ai_tier_for_feature,
)
from tools.eos.saas.billing.wilsy_ai_commercial_policy import get_wilsy_ai_commercial_policy
from tools.eos.saas.domain.plan import PlanEntity
from tools.eos.saas.domain.subscription import SubscriptionStatus, verify_subscription_integrity
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlementState

VERSION: Final[str] = "v1.2.1-PLAN-PROOF-BOUND-APPROVAL-INTENT"
FOUNDER_TENANT_ID: Final[str] = "WILSYTENANT-4CD2FZ4O"
FOUNDER_SUBSCRIPTION_ID: Final[str] = "WILSYSUB-93455E4E"
FOUNDER_PLAN_ID: Final[str] = "WILSYPLAN-37B8164F"
BRANDING_FEATURE: Final[str] = "wilsy.vas.tenant_branding.enterprise.v1"
_SHA3: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")


class FounderAIReconciliationError(RuntimeError):
    """Stable non-sensitive failure at an exact Founder commercial boundary."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True, slots=True)
class FounderAIReconciliationResult:
    """Commercially eligible state; caller still owns durable commit."""

    subscription_id: str
    feature_id: WilsyAIVASFeatureId
    entitlement_id: str | None
    lifecycle: str
    applied: bool


def _require(condition: bool, code: str) -> None:
    """Reject an invalid commercial source without recovery by inference."""
    if not condition:
        raise FounderAIReconciliationError(code)


def _session_required(session: Any) -> None:
    """Require an active caller-owned transaction with no hidden begin/commit."""
    marker = getattr(session, "in_transaction", False)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    _require(active is True, "FOUNDER_AI_ACTIVE_TRANSACTION_REQUIRED")


def _canonical_plan(plan_collection: Any, session: Any) -> PlanEntity:
    """Strictly hydrate the exact Founder plan in the caller's transaction."""
    document = plan_collection.find_one(
        {"tenant_id": FOUNDER_TENANT_ID, "plan_id": FOUNDER_PLAN_ID},
        session=session,
    )
    _require(isinstance(document, dict), "FOUNDER_AI_PLAN_NOT_FOUND")
    assert document is not None
    try:
        # Reuse PlanRegistry's strict transport revision and canonical proof.
        plan = PlanRegistry._hydrate(document).plan
    except (TypeError, ValueError) as error:
        raise FounderAIReconciliationError("FOUNDER_AI_PLAN_PROOF_INVALID") from error
    _require(plan.tenant_id == FOUNDER_TENANT_ID
             and plan.plan_id == FOUNDER_PLAN_ID
             and plan.plan_type.value == "FOUNDER_ENTERPRISE"
             and plan.active is True
             and plan.price == 0, "FOUNDER_AI_PLAN_NOT_ELIGIBLE")
    return plan



@dataclass(frozen=True, slots=True)
class FounderAIApprovalIntent:
    """A source-bound request for independent approval, never an entitlement."""

    feature_id: WilsyAIVASFeatureId
    source_fingerprint: str
    approval_state: str = "NOT_ISSUED"


def prepare_founder_ai_approval_intent(
    *,
    subscription_collection: Any,
    plan_collection: Any,
    session: Any,
    proposed_feature_id: WilsyAIVASFeatureId,
) -> FounderAIApprovalIntent:
    """Produce non-mutating evidence for an independently signed tier decision.

    A request to prepare a Founder commercial amendment is not approval,
    subscription mutation, entitlement issuance or any IAM authority. The
    independently authorized commercial issuer must verify a signed decision
    over this exact source fingerprint and then use the canonical registries.
    """
    _session_required(session)
    _require(type(proposed_feature_id) is WilsyAIVASFeatureId,
             "FOUNDER_AI_EXPLICIT_PROPOSED_TIER_REQUIRED")
    _require(subscription_collection is not None and plan_collection is not None,
             "FOUNDER_AI_SOURCE_COLLECTION_REQUIRED")
    plan = _canonical_plan(plan_collection, session)
    subscriptions = SubscriptionRegistry.list_entities(
        FOUNDER_TENANT_ID, collection=subscription_collection, session=session,
    )
    active = [row for row in subscriptions if row.status is SubscriptionStatus.ACTIVE]
    _require(len(active) == 1, "FOUNDER_AI_ACTIVE_SUBSCRIPTION_CARDINALITY_INVALID")
    subscription = active[0]
    _require(subscription.tenant_id == FOUNDER_TENANT_ID
             and subscription.subscription_id == FOUNDER_SUBSCRIPTION_ID
             and subscription.plan_id == FOUNDER_PLAN_ID
             and subscription.billing_mode == "PLATFORM"
             and subscription.amount == 0
             and verify_subscription_integrity(subscription),
             "FOUNDER_AI_APPROVAL_SOURCE_NOT_ELIGIBLE")
    _require(evaluate_subscription_term(
        subscription, evaluated_at=datetime.now(timezone.utc),
    ).kind is SubscriptionTermKind.PERPETUAL_PLATFORM_OWNER,
             "FOUNDER_AI_APPROVAL_TERM_INVALID")
    _require(plan.catalogue_version == subscription.plan_catalogue_version
             and tuple(plan.features) == tuple(subscription.plan_features)
             and BRANDING_FEATURE in plan.features,
             "FOUNDER_AI_APPROVAL_SOURCE_DIVERGENT")
    existing_tiers = [tier for tier in WilsyAIVASFeatureId
                      if tier.value in plan.features]
    _require(not existing_tiers, "FOUNDER_AI_APPROVAL_TIER_ALREADY_PRESENT")
    proof = getattr(subscription, "proof_hash", None)
    _require(isinstance(proof, str) and _SHA3.fullmatch(proof) is not None,
             "FOUNDER_AI_APPROVAL_SUBSCRIPTION_PROOF_INVALID")
    plan_proof = getattr(plan, "proof_hash", None)
    plan_integrity = getattr(plan, "integrity_root", None)
    _require(isinstance(plan_proof, str)
             and _SHA3.fullmatch(plan_proof) is not None
             and isinstance(plan_integrity, str)
             and _SHA3.fullmatch(plan_integrity) is not None,
             "FOUNDER_AI_APPROVAL_PLAN_PROOF_INVALID")
    proposal = {
        "schema": "WILSY-FOUNDER-AI-FEATURE-APPROVAL-INTENT/V1",
        "tenant_id": FOUNDER_TENANT_ID,
        "subscription_id": FOUNDER_SUBSCRIPTION_ID,
        "plan_id": FOUNDER_PLAN_ID,
        "plan_catalogue_version": plan.catalogue_version,
        "plan_state_proof_hash": plan_proof,
        "plan_integrity_root": plan_integrity,
        "subscription_proof_hash": proof,
        "current_features": sorted(plan.features),
        "proposed_feature_id": proposed_feature_id.value,
        "subscription_amount_minor": 0,
        "authorization": "REQUEST_ONLY_NO_ISSUANCE",
    }
    fingerprint = hashlib.sha3_512(
        json.dumps(proposal, sort_keys=True, ensure_ascii=False,
                   separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()
    return FounderAIApprovalIntent(proposed_feature_id, fingerprint)



def reconcile_founder_ai_entitlement(
    *,
    subscription_collection: Any,
    plan_collection: Any,
    entitlement_collection: Any,
    session: Any,
    idempotency_key: str,
    feature_id: WilsyAIVASFeatureId,
    apply: bool = False,
    activation_evidence_reference: str | None = None,
    activation_evidence_fingerprint: str | None = None,
    occurred_at: datetime | None = None,
) -> FounderAIReconciliationResult:
    """Inspect or issue/activate from independently verified Founder sources.

    The caller must authenticate and authorize the institutional operator
    before invoking this service; this is not an HTTP or self-serve endpoint.
    Applying requires explicit activation evidence and a source subscription
    already containing the exact AI feature. No plan or subscription is edited.
    All writes use D57B and P4, within the caller's active Mongo transaction.
    Caller owns commit, abort and whole-transaction retry if appropriate.
    """
    _session_required(session)
    _require(type(feature_id) is WilsyAIVASFeatureId,
             "FOUNDER_AI_APPROVED_FEATURE_REQUIRED")
    _require(isinstance(idempotency_key, str) and bool(idempotency_key.strip())
             and len(idempotency_key) <= 128,
             "FOUNDER_AI_IDEMPOTENCY_KEY_INVALID")
    _require(all(collection is not None for collection in
                 (subscription_collection, plan_collection, entitlement_collection)),
             "FOUNDER_AI_COLLECTION_REQUIRED")

    plan = _canonical_plan(plan_collection, session)
    subscriptions = SubscriptionRegistry.list_entities(
        FOUNDER_TENANT_ID, collection=subscription_collection, session=session,
    )
    active = [item for item in subscriptions if item.status is SubscriptionStatus.ACTIVE]
    _require(len(active) == 1, "FOUNDER_AI_ACTIVE_SUBSCRIPTION_CARDINALITY_INVALID")
    subscription = active[0]
    _require(subscription.subscription_id == FOUNDER_SUBSCRIPTION_ID
             and subscription.tenant_id == FOUNDER_TENANT_ID
             and subscription.plan_id == FOUNDER_PLAN_ID
             and subscription.tier is not None
             and subscription.tier.value == "FOUNDER_ENTERPRISE"
             and subscription.billing_mode == "PLATFORM"
             and subscription.amount == 0
             and verify_subscription_integrity(subscription),
             "FOUNDER_AI_SUBSCRIPTION_NOT_ELIGIBLE")
    _require(evaluate_subscription_term(
        subscription, evaluated_at=datetime.now(timezone.utc),
    ).kind is SubscriptionTermKind.PERPETUAL_PLATFORM_OWNER,
             "FOUNDER_AI_PERPETUAL_SOURCE_INVALID")
    _require(plan.catalogue_version == subscription.plan_catalogue_version
             and tuple(plan.features) == tuple(subscription.plan_features),
             "FOUNDER_AI_PLAN_SUBSCRIPTION_SNAPSHOT_DIVERGENT")
    features = tuple(plan.features)
    _require(BRANDING_FEATURE in features, "FOUNDER_AI_FOUNDATION_FEATURE_MISSING")
    matches = [item for item in WilsyAIVASFeatureId if item.value in features]
    _require(len(matches) == 1 and matches[0] is feature_id,
             "FOUNDER_AI_EXPLICIT_TIER_FEATURE_REQUIRED")

    registry = WilsyAIEntitlementRegistry(entitlement_collection)
    try:
        existing = registry.get_by_module(
            tenant_id=FOUNDER_TENANT_ID, module_id="WILSY_AI_REASONING", session=session,
        )
    except WilsyAIEntitlementNotFoundError:
        existing = None
    if existing is not None:
        tier = resolve_wilsy_ai_tier_for_feature(feature_id)
        policy = get_wilsy_ai_commercial_policy(tier)
        reference, fingerprint = _source_evidence(
            FOUNDER_TENANT_ID, subscription, feature_id,
            tier, policy.policy_fingerprint,
        )
        _require(existing.tenant_id == FOUNDER_TENANT_ID
                 and existing.entitlement_id == derive_subscription_wilsy_ai_entitlement_id(
                     FOUNDER_TENANT_ID,
                 )
                 and existing.tier is tier
                 and existing.policy_fingerprint == policy.policy_fingerprint
                 and existing.source_readiness_evidence_reference == reference
                 and existing.source_readiness_evidence_fingerprint == fingerprint,
                 "FOUNDER_AI_EXISTING_ENTITLEMENT_SOURCE_DIVERGENT")
        if existing.lifecycle_state is WilsyAIEntitlementState.ACTIVE:
            return FounderAIReconciliationResult(
                FOUNDER_SUBSCRIPTION_ID, feature_id,
                existing.entitlement_id, "ACTIVE", False,
            )
        _require(existing.lifecycle_state is WilsyAIEntitlementState.PENDING_SOURCE,
                 "FOUNDER_AI_EXISTING_ENTITLEMENT_NOT_ACTIVATABLE")
    if not apply:
        return FounderAIReconciliationResult(
            FOUNDER_SUBSCRIPTION_ID, feature_id,
            existing.entitlement_id if existing is not None else None,
            "PENDING_SOURCE" if existing is not None else "ELIGIBLE_NOT_ACTIVATED",
            False,
        )

    _require(isinstance(activation_evidence_reference, str)
             and bool(activation_evidence_reference.strip())
             and len(activation_evidence_reference) <= 256,
             "FOUNDER_AI_ACTIVATION_REFERENCE_REQUIRED")
    _require(isinstance(activation_evidence_fingerprint, str)
             and _SHA3.fullmatch(activation_evidence_fingerprint) is not None,
             "FOUNDER_AI_ACTIVATION_EVIDENCE_INVALID")
    _require(isinstance(occurred_at, datetime)
             and occurred_at.tzinfo is not None
             and occurred_at.utcoffset() is not None,
             "FOUNDER_AI_ACTIVATION_TIME_INVALID")

    composition = compose_subscription_wilsy_ai_entitlement(
        tenant_id=FOUNDER_TENANT_ID,
        idempotency_key=idempotency_key,
        subscription_collection=subscription_collection,
        entitlement_collection=entitlement_collection,
        session=session,
    )
    _require(composition.subscription_id == FOUNDER_SUBSCRIPTION_ID
             and composition.feature_id is feature_id,
             "FOUNDER_AI_COMPOSITION_SOURCE_MISMATCH")
    entitlement = composition.entitlement
    _require(entitlement.lifecycle_state is WilsyAIEntitlementState.PENDING_SOURCE,
             "FOUNDER_AI_ACTIVATION_PRECONDITION_INVALID")
    activated = activate_wilsy_ai_reasoning_entitlement(
        registry=registry,
        entitlement=entitlement,
        activation_evidence_reference=activation_evidence_reference,
        activation_evidence_fingerprint=activation_evidence_fingerprint,
        occurred_at=occurred_at,
        session=session,
    )
    _require(activated.lifecycle_state is WilsyAIEntitlementState.ACTIVE,
             "FOUNDER_AI_ACTIVATION_RESULT_INVALID")
    return FounderAIReconciliationResult(
        FOUNDER_SUBSCRIPTION_ID, feature_id, activated.entitlement_id,
        activated.lifecycle_state.value, True,
    )


__all__ = [
    "VERSION", "FOUNDER_TENANT_ID", "FOUNDER_SUBSCRIPTION_ID", "FOUNDER_PLAN_ID",
    "BRANDING_FEATURE", "FounderAIApprovalIntent",
    "prepare_founder_ai_approval_intent", "FounderAIReconciliationError",
    "FounderAIReconciliationResult", "reconcile_founder_ai_entitlement",
]

# ARTIFACT: founder_ai_entitlement_reconciliation.py
# VERSION: v1.2.1-PLAN-PROOF-BOUND-APPROVAL-INTENT
# AUTHORITY BOUNDARY: source-verified Founder commercial composition and P4 CAS only
# TENANT POSTURE: exact Founder tuple, no aliases or tenant-name default grants
# FAIL-CLOSED POSTURE: active proof and one approved AI tier required before write
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
