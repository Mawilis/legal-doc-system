"""WILSY OS subscription-backed WILSY AI entitlement composition authority.

TITLE: Subscription-Backed WILSY AI Entitlement Composition Service
VERSION: v1.0.0-D57B-SUBSCRIPTION-WILSY-AI-ENTITLEMENT-COMPOSITION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Derive and persist one canonical WILSY AI reasoning entitlement for
         one tenant from exactly one canonical ACTIVE subscription carrying
         exactly one certified tier-specific WILSY AI VAS feature.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/subscription_wilsy_ai_entitlement_composition_service.py
COLLABORATION / OWNERSHIP: SubscriptionRegistry owns subscription truth; D57A
                            owns feature-to-tier correspondence; P3 owns policy;
                            P4 provisioning and registry own entitlement shape
                            and persistence; the caller owns the transaction.
CERTIFICATION / UPDATE DATE: 2026-10-10
CHANGELOG: v1.0.0-D57B-SUBSCRIPTION-WILSY-AI-ENTITLEMENT-COMPOSITION establishes
           tenant-scoped ACTIVE-subscription resolution, proof verification,
           exact D57A tier derivation, deterministic evidence and durable P4
           create-or-replay composition with bounded failure classification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No secrets, PII, raw persistence diagnostics,
                             pricing, payment or plan internals are exposed.
TENANT BOUNDARY: Every subscription read and entitlement write uses the exact
                 tenant and caller-owned Mongo session; cross-tenant inference
                 and caller-selected subscription identity are impossible.
AUTHORITY BOUNDARY: Positive subscription-to-WILSY-AI entitlement composition
                    only; no plan, subscription, IAM, admission, provider,
                    usage, HTTP, client, or runtime execution authority.
TRANSACTION BOUNDARY: Requires and propagates an active caller-owned session;
                      never starts, commits, aborts or retries a transaction.
FINANCIAL AUTHORITY BOUNDARY: No price, invoice, payment, execution, paid or
                              settlement truth; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing, inactive, ambiguous or corrupt subscription
                         truth; absent/conflicting VAS features; persistence
                         failure; conflict; and divergent replay all reject.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Final, NoReturn

from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.billing.wilsy_ai_commercial_policy import (
    WilsyAITier,
    get_wilsy_ai_commercial_policy,
)
from tools.eos.saas.billing.wilsy_ai_entitlement_provisioning import (
    MODULE_ID,
    WilsyAIReasoningEntitlementProvisioningError,
    provision_wilsy_ai_reasoning_entitlement,
)
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import (
    WilsyAIEntitlementConflictError,
    WilsyAIEntitlementNotFoundError,
    WilsyAIEntitlementRegistry,
    WilsyAIEntitlementRegistryError,
)
from tools.eos.saas.billing.wilsy_ai_vas_feature_catalogue import (
    WilsyAIVASFeatureId,
    resolve_wilsy_ai_tier_for_feature,
)
from tools.eos.saas.domain.subscription import (
    SubscriptionEntity,
    SubscriptionStatus,
    verify_subscription_integrity,
)
from tools.eos.saas.domain.wilsy_ai_entitlement import (
    WilsyAIEntitlement,
    WilsyAIEntitlementState,
)


VERSION: Final[str] = "v1.0.0-D57B-SUBSCRIPTION-WILSY-AI-ENTITLEMENT-COMPOSITION"
ENTITLEMENT_ID_NAMESPACE: Final[str] = "WILSY-AI-SUBSCRIPTION-ENTITLEMENT-ID/V1"
SOURCE_EVIDENCE_SCHEMA: Final[str] = "WILSY-AI-SUBSCRIPTION-SOURCE-EVIDENCE/V1"
CANONICAL_SOURCE_REQUIREMENTS: Final[tuple[str, ...]] = (
    "explicit_authoritative_provisioning",
)
CANONICAL_CAPABILITY_GRANTS: Final[tuple[str, ...]] = (
    "wilsy_ai.reasoning.execute.v1",
)
_SHA3: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")


class SubscriptionWilsyAIEntitlementCompositionError(RuntimeError):
    """Base fail-closed D57B error carrying one stable non-sensitive code."""

    def __init__(self, code: str) -> None:
        """Create one bounded composition failure without leaking internals."""
        self.code = code
        super().__init__(code)


class SubscriptionWilsyAIEntitlementCompositionInputError(
    SubscriptionWilsyAIEntitlementCompositionError
):
    """Caller-owned tenant, replay key, collection or transaction is invalid."""


class SubscriptionWilsyAIEntitlementCompositionCommercialError(
    SubscriptionWilsyAIEntitlementCompositionError
):
    """Canonical subscription truth does not authorize one exact AI tier."""


class SubscriptionWilsyAIEntitlementCompositionPersistenceError(
    SubscriptionWilsyAIEntitlementCompositionError
):
    """A canonical subscription or entitlement persistence seam failed."""


class SubscriptionWilsyAIEntitlementCompositionConflictError(
    SubscriptionWilsyAIEntitlementCompositionError
):
    """Existing entitlement identity conflicts with the derived command."""


class SubscriptionWilsyAIEntitlementCompositionDivergentReplayError(
    SubscriptionWilsyAIEntitlementCompositionConflictError
):
    """One tenant replay key was previously bound to different evidence."""


@dataclass(frozen=True, slots=True)
class SubscriptionWilsyAIEntitlementCompositionResult:
    """Immutable result containing only derived canonical positive truth.

    The result grants no IAM permission, runtime admission, provider action,
    payment execution or settlement fact. Transaction durability remains the
    caller's responsibility until its surrounding transaction commits.
    """

    subscription_id: str
    feature_id: WilsyAIVASFeatureId
    tier: WilsyAITier
    entitlement: WilsyAIEntitlement
    exact_replay: bool


def _raise(
    error_type: type[SubscriptionWilsyAIEntitlementCompositionError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one public bounded error while retaining an internal cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object) -> str:
    """Require exact bounded identity text without coercion or normalization."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 256
    ):
        _raise(
            SubscriptionWilsyAIEntitlementCompositionInputError,
            f"D57B_{name.upper()}_INVALID",
        )
    return value


def _active_transaction(session: Any) -> Any:
    """Require an active caller-owned transaction before authoritative reads."""
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(
            SubscriptionWilsyAIEntitlementCompositionInputError,
            "D57B_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _canonical_json(payload: dict[str, object]) -> bytes:
    """Serialize one deterministic institutional evidence payload."""
    return json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(payload: dict[str, object]) -> str:
    """Return lowercase SHA3-512 evidence for exact semantic coordinates."""
    return hashlib.sha3_512(_canonical_json(payload)).hexdigest()


def derive_subscription_wilsy_ai_entitlement_id(tenant_id: str) -> str:
    """Derive one permanent tenant/module entitlement lineage identifier.

    Subscription, feature, tier, policy, replay key and time are intentionally
    excluded so later commercial change cannot fork the sole tenant/module
    entitlement identity. This derivation creates no entitlement by itself.
    """
    tenant = _text("tenant_id", tenant_id)
    fingerprint = _digest(
        {
            "module_id": MODULE_ID,
            "namespace": ENTITLEMENT_ID_NAMESPACE,
            "tenant_id": tenant,
        }
    )
    return f"wai-{fingerprint}"


def _subscription(
    tenant_id: str,
    collection: Any,
    session: Any,
    registry: type[SubscriptionRegistry],
) -> SubscriptionEntity:
    """Resolve and verify exactly one ACTIVE subscription in tenant scope."""
    try:
        items = registry.list_entities(
            tenant_id,
            collection=collection,
            session=session,
        )
    except Exception as error:
        _raise(
            SubscriptionWilsyAIEntitlementCompositionPersistenceError,
            "D57B_SUBSCRIPTION_UNAVAILABLE",
            error,
        )
    if not items:
        _raise(
            SubscriptionWilsyAIEntitlementCompositionCommercialError,
            "D57B_SUBSCRIPTION_NOT_FOUND",
        )
    active = tuple(item for item in items if item.status is SubscriptionStatus.ACTIVE)
    if not active:
        _raise(
            SubscriptionWilsyAIEntitlementCompositionCommercialError,
            "D57B_ACTIVE_SUBSCRIPTION_NOT_FOUND",
        )
    if len(active) != 1:
        _raise(
            SubscriptionWilsyAIEntitlementCompositionCommercialError,
            "D57B_ACTIVE_SUBSCRIPTION_AMBIGUOUS",
        )
    item = active[0]
    if (
        type(item) is not SubscriptionEntity
        or item.tenant_id != tenant_id
        or not isinstance(item.subscription_id, str)
        or not item.subscription_id
        or item.subscription_id != item.subscription_id.strip()
        or not isinstance(item.plan_id, str)
        or not item.plan_id
        or item.plan_id != item.plan_id.strip()
        or isinstance(item.plan_catalogue_version, bool)
        or not isinstance(item.plan_catalogue_version, int)
        or item.plan_catalogue_version < 1
        or not isinstance(item.proof_hash, str)
        or _SHA3.fullmatch(item.proof_hash.casefold()) is None
        or not verify_subscription_integrity(item)
    ):
        _raise(
            SubscriptionWilsyAIEntitlementCompositionCommercialError,
            "D57B_SUBSCRIPTION_PROOF_INVALID",
        )
    return item


def _feature(subscription: SubscriptionEntity) -> WilsyAIVASFeatureId:
    """Require exactly one D57A feature without aliases or generic matching."""
    matches = tuple(
        feature
        for feature in WilsyAIVASFeatureId
        if feature.value in subscription.plan_features
    )
    if not matches:
        _raise(
            SubscriptionWilsyAIEntitlementCompositionCommercialError,
            "D57B_WILSY_AI_VAS_FEATURE_ABSENT",
        )
    if len(matches) != 1:
        _raise(
            SubscriptionWilsyAIEntitlementCompositionCommercialError,
            "D57B_WILSY_AI_VAS_FEATURE_CONFLICT",
        )
    return matches[0]


def _source_evidence(
    tenant_id: str,
    subscription: SubscriptionEntity,
    feature: WilsyAIVASFeatureId,
    tier: WilsyAITier,
    policy_fingerprint: str,
) -> tuple[str, str]:
    """Bind entitlement source evidence to exact verified commercial truth."""
    payload: dict[str, object] = {
        "feature_id": feature.value,
        "module_id": MODULE_ID,
        "plan_catalogue_version": subscription.plan_catalogue_version,
        "plan_id": subscription.plan_id,
        "policy_fingerprint": policy_fingerprint,
        "schema": SOURCE_EVIDENCE_SCHEMA,
        "subscription_id": subscription.subscription_id,
        "subscription_proof_hash": subscription.proof_hash,
        "tenant_id": tenant_id,
        "tier": tier.value,
    }
    fingerprint = _digest(payload)
    return (
        f"wilsy-ai-subscription:{subscription.subscription_id}:{fingerprint}",
        fingerprint,
    )


def _cause(error: BaseException, expected: type[BaseException]) -> BaseException | None:
    """Find one typed dependency cause in a bounded acyclic error chain."""
    current: BaseException | None = error
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, expected):
            return current
        current = current.__cause__ or current.__context__
    return None


def compose_subscription_wilsy_ai_entitlement(
    *,
    tenant_id: str,
    idempotency_key: str,
    subscription_collection: Any,
    entitlement_collection: Any,
    session: Any,
    subscription_registry: type[SubscriptionRegistry] = SubscriptionRegistry,
    entitlement_registry_type: type[WilsyAIEntitlementRegistry] = (
        WilsyAIEntitlementRegistry
    ),
) -> SubscriptionWilsyAIEntitlementCompositionResult:
    """Derive and persist one canonical WILSY AI entitlement.

    @description Resolves exact ACTIVE subscription truth, verifies its proof,
        derives exactly one D57A feature/tier and invokes the existing P4
        provisioning/registry seam with deterministic server-owned evidence.
    @collaboration SubscriptionRegistry, D57A, P3 policy, P4 provisioning and P4
        persistence remain the respective authorities; the caller owns commit,
        abort and whole-transaction retry.
    @institutional Prevents caller, UI, IAM, plan-name, price or generic-feature
        inference from manufacturing WILSY AI commercial entitlement truth.
    @param tenant_id Exact already-authorized tenant scope.
    @param idempotency_key Exact caller orchestration replay coordinate.
    @param subscription_collection Canonical subscription collection handle.
    @param entitlement_collection Canonical P4 entitlement collection handle.
    @param session Active caller-owned Mongo session and transaction.
    @returns Derived canonical entitlement composition result.
    @raises SubscriptionWilsyAIEntitlementCompositionError on every invalid,
        unavailable, commercially inapplicable, conflicting or divergent path.
    """
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    replay_key = _text("idempotency_key", idempotency_key)
    if subscription_collection is None or entitlement_collection is None:
        _raise(
            SubscriptionWilsyAIEntitlementCompositionInputError,
            "D57B_COLLECTION_REQUIRED",
        )
    subscription = _subscription(
        tenant,
        subscription_collection,
        tx,
        subscription_registry,
    )
    feature = _feature(subscription)
    tier = resolve_wilsy_ai_tier_for_feature(feature)
    policy = get_wilsy_ai_commercial_policy(tier)
    source_reference, source_fingerprint = _source_evidence(
        tenant,
        subscription,
        feature,
        tier,
        policy.policy_fingerprint,
    )
    registry = entitlement_registry_type(entitlement_collection)
    prior = None
    try:
        prior = registry.get_by_module(
            tenant_id=tenant,
            module_id=MODULE_ID,
            session=tx,
        )
    except WilsyAIEntitlementNotFoundError:
        prior = None
    except WilsyAIEntitlementRegistryError as error:
        _raise(
            SubscriptionWilsyAIEntitlementCompositionPersistenceError,
            "D57B_ENTITLEMENT_PERSISTENCE_UNAVAILABLE",
            error,
        )
    except Exception as error:
        _raise(
            SubscriptionWilsyAIEntitlementCompositionPersistenceError,
            "D57B_ENTITLEMENT_PERSISTENCE_FAILED",
            error,
        )
    try:
        entitlement = provision_wilsy_ai_reasoning_entitlement(
            registry=registry,
            tenant_id=tenant,
            entitlement_id=derive_subscription_wilsy_ai_entitlement_id(tenant),
            tier=tier,
            source_evidence_reference=source_reference,
            source_evidence_fingerprint=source_fingerprint,
            idempotency_key=replay_key,
            session=tx,
        )
    except WilsyAIReasoningEntitlementProvisioningError as error:
        conflict = _cause(error, WilsyAIEntitlementConflictError)
        if conflict is not None and "M13P4_DIVERGENT_IDEMPOTENCY" in str(conflict):
            _raise(
                SubscriptionWilsyAIEntitlementCompositionDivergentReplayError,
                "D57B_DIVERGENT_REPLAY",
                error,
            )
        if conflict is not None:
            _raise(
                SubscriptionWilsyAIEntitlementCompositionConflictError,
                "D57B_ENTITLEMENT_PERSISTENCE_CONFLICT",
                error,
            )
        _raise(
            SubscriptionWilsyAIEntitlementCompositionPersistenceError,
            "D57B_ENTITLEMENT_PERSISTENCE_FAILED",
            error,
        )
    if (
        entitlement.tenant_id != tenant
        or entitlement.entitlement_id
        != derive_subscription_wilsy_ai_entitlement_id(tenant)
        or entitlement.module_id != MODULE_ID
        or entitlement.tier is not tier
        or entitlement.policy_fingerprint != policy.policy_fingerprint
        or entitlement.source_requirements != CANONICAL_SOURCE_REQUIREMENTS
        or entitlement.capability_grants != CANONICAL_CAPABILITY_GRANTS
        or entitlement.lifecycle_state is not WilsyAIEntitlementState.PENDING_SOURCE
        or entitlement.source_readiness_evidence_reference != source_reference
        or entitlement.source_readiness_evidence_fingerprint != source_fingerprint
    ):
        _raise(
            SubscriptionWilsyAIEntitlementCompositionPersistenceError,
            "D57B_ENTITLEMENT_RESULT_INVALID",
        )
    return SubscriptionWilsyAIEntitlementCompositionResult(
        subscription_id=subscription.subscription_id,
        feature_id=feature,
        tier=tier,
        entitlement=entitlement,
        exact_replay=prior is not None and prior == entitlement,
    )


__all__ = [
    "CANONICAL_CAPABILITY_GRANTS",
    "CANONICAL_SOURCE_REQUIREMENTS",
    "ENTITLEMENT_ID_NAMESPACE",
    "SOURCE_EVIDENCE_SCHEMA",
    "SubscriptionWilsyAIEntitlementCompositionCommercialError",
    "SubscriptionWilsyAIEntitlementCompositionConflictError",
    "SubscriptionWilsyAIEntitlementCompositionDivergentReplayError",
    "SubscriptionWilsyAIEntitlementCompositionError",
    "SubscriptionWilsyAIEntitlementCompositionInputError",
    "SubscriptionWilsyAIEntitlementCompositionPersistenceError",
    "SubscriptionWilsyAIEntitlementCompositionResult",
    "VERSION",
    "compose_subscription_wilsy_ai_entitlement",
    "derive_subscription_wilsy_ai_entitlement_id",
]

# ARTIFACT: subscription_wilsy_ai_entitlement_composition_service.py
# VERSION: v1.0.0-D57B-SUBSCRIPTION-WILSY-AI-ENTITLEMENT-COMPOSITION
# AUTHORITY BOUNDARY: positive verified subscription-to-WILSY-AI entitlement composition only; no plan, subscription, IAM, admission, provider, route or runtime authority
# TENANT POSTURE: exact tenant scope and caller-owned transaction propagate through every subscription read and entitlement operation
# FAIL-CLOSED POSTURE: unavailable, absent, inactive, ambiguous or corrupt subscription truth; absent/conflicting VAS feature; persistence conflict/failure; divergent replay and invalid result reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
