"""Direct certificate for D57B subscription-backed WILSY AI composition.

TITLE: Subscription-Backed WILSY AI Entitlement Composition Direct Certificate
VERSION: v1.0.0-D57B-SUBSCRIPTION-WILSY-AI-COMPOSITION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify tenant/session binding, exact ACTIVE subscription proof,
         closed D57A tier derivation, canonical P4 persistence and replay.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_subscription_wilsy_ai_entitlement_composition_service.py
COLLABORATION / OWNERSHIP: Bounded doubles exercise D57B while D57A, P3, P4
                            and SubscriptionRegistry remain separate authorities.
CERTIFICATION / UPDATE DATE: 2026-10-10
CHANGELOG: v1.0.0-D57B-SUBSCRIPTION-WILSY-AI-COMPOSITION-CERT establishes
           positive tiers and adversarial commercial, proof, persistence,
           replay, authority and caller-input certificates.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic in-memory evidence only.
TENANT BOUNDARY: Every fake subscription read and P4 operation records tenant
                 scope and the exact caller transaction object.
AUTHORITY BOUNDARY: Certificate only; no external or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import ast
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import inspect
from pathlib import Path
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.billing.wilsy_ai_commercial_policy import (
    WilsyAITier,
    get_wilsy_ai_commercial_policy,
)
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import (
    WilsyAIEntitlementRegistry,
)
from tools.eos.saas.billing import (
    subscription_wilsy_ai_entitlement_composition_service as service,
)
from tools.eos.saas.domain.subscription import (
    BillingFrequency,
    PlanTiers,
    SubscriptionEntity,
    SubscriptionStatus,
)


NOW = datetime(2026, 10, 10, 10, 0, tzinfo=timezone.utc)


class Session:
    """Minimal caller-owned transaction marker."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class SubscriptionRegistryDouble:
    """Record exact tenant/session reads and return configured entities."""

    items: tuple[SubscriptionEntity, ...] = ()
    calls: list[tuple[str | None, object, object]] = []
    failure: Exception | None = None

    @classmethod
    def list_entities(
        cls,
        tenant_id_header: str | None = None,
        *,
        collection: object = None,
        session: object = None,
    ) -> tuple[SubscriptionEntity, ...]:
        cls.calls.append((tenant_id_header, collection, session))
        if cls.failure is not None:
            raise cls.failure
        return cls.items


class EntitlementCollection:
    """P4-compatible collection double with session and failure evidence."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.sessions: list[object] = []
        self.fail_find = False
        self.fail_insert = False

    def with_options(self, **_: object) -> "EntitlementCollection":
        return self

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, Any] | None:
        self.sessions.append(session)
        if self.fail_find:
            raise PyMongoError("private diagnostic")
        return next(
            (
                row
                for row in self.rows
                if all(row.get(key) == value for key, value in query.items())
            ),
            None,
        )

    def insert_one(self, document: dict[str, Any], *, session: object) -> object:
        self.sessions.append(session)
        if self.fail_insert:
            raise PyMongoError("private diagnostic")
        if any(
            row.get("tenant_id") == document["tenant_id"]
            and row.get("module_id") == document["module_id"]
            for row in self.rows
        ):
            raise DuplicateKeyError("tenant/module unique")
        if any(
            row.get("tenant_id") == document["tenant_id"]
            and row.get("idempotency_key") == document["idempotency_key"]
            for row in self.rows
        ):
            raise DuplicateKeyError("tenant/idempotency unique")
        self.rows.append(dict(document))
        return object()


class UnexpectedReadFailureRegistry(WilsyAIEntitlementRegistry):
    """Inject one non-registry dependency fracture for fail-closed coverage."""

    def get_by_module(self, **_: object) -> Any:
        raise RuntimeError("private unexpected diagnostic")


def subscription(
    *,
    tenant_id: str = "tenant-a",
    subscription_id: str = "subscription-a",
    features: tuple[str, ...] = ("ai.wilsy.starter",),
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
) -> SubscriptionEntity:
    """Construct valid deterministic canonical subscription evidence."""
    return SubscriptionEntity(
        tenant_id=tenant_id,
        plan_id=f"plan-{subscription_id}",
        plan=PlanTiers.PROFESSIONAL,
        amount=100.0,
        currency="ZAR",
        billing_frequency=BillingFrequency.MONTHLY,
        start_date=NOW,
        current_period_start=NOW,
        current_period_end=NOW + timedelta(days=30),
        idempotency_key=f"subscription-key-{subscription_id}",
        subscription_id=subscription_id,
        plan_features=features,
        plan_catalogue_version=1,
        status=status,
        seal_nonce=f"seal-{subscription_id}",
    )


@pytest.fixture(autouse=True)
def reset_subscription_registry() -> None:
    """Reset shared double state before every direct certificate case."""
    SubscriptionRegistryDouble.items = ()
    SubscriptionRegistryDouble.calls = []
    SubscriptionRegistryDouble.failure = None


def invoke(**changes: object) -> service.SubscriptionWilsyAIEntitlementCompositionResult:
    """Invoke D57B with explicit inert dependency surfaces."""
    values: dict[str, Any] = {
        "tenant_id": "tenant-a",
        "idempotency_key": "compose-key-a",
        "subscription_collection": object(),
        "entitlement_collection": EntitlementCollection(),
        "session": Session(),
        "subscription_registry": SubscriptionRegistryDouble,
        "entitlement_registry_type": WilsyAIEntitlementRegistry,
    }
    values.update(changes)
    return service.compose_subscription_wilsy_ai_entitlement(**values)


@pytest.mark.parametrize(
    ("feature", "tier"),
    [
        ("ai.wilsy.starter", WilsyAITier.STARTER),
        ("ai.wilsy.growth", WilsyAITier.GROWTH),
        ("ai.wilsy.institutional", WilsyAITier.INSTITUTIONAL),
    ],
)
def test_exact_subscription_feature_derives_canonical_tier_and_policy(
    feature: str,
    tier: WilsyAITier,
) -> None:
    """Each D57A feature binds exact P3 policy and fixed P4 capability."""
    SubscriptionRegistryDouble.items = (subscription(features=(feature,)),)
    result = invoke()
    policy = get_wilsy_ai_commercial_policy(tier)
    assert result.tier is tier and result.entitlement.tier is tier
    assert result.entitlement.policy_fingerprint == policy.policy_fingerprint
    assert result.entitlement.capability_grants == service.CANONICAL_CAPABILITY_GRANTS
    assert result.entitlement.source_requirements == service.CANONICAL_SOURCE_REQUIREMENTS


@pytest.mark.parametrize(
    "features",
    [
        (),
        ("ai.wilsy",),
        ("ai.wilsy.enterprise",),
        ("AI.WILSY.STARTER",),
        ("ai.wilsy.starter.extra",),
        ("legal.core", "ai.wilsy"),
    ],
)
def test_absent_generic_unknown_and_lookalike_features_write_nothing(
    features: tuple[str, ...],
) -> None:
    """Only exact closed D57A membership can reach entitlement persistence."""
    collection = EntitlementCollection()
    SubscriptionRegistryDouble.items = (subscription(features=features),)
    with pytest.raises(
        service.SubscriptionWilsyAIEntitlementCompositionCommercialError,
        match="D57B_WILSY_AI_VAS_FEATURE_ABSENT",
    ):
        invoke(entitlement_collection=collection)
    assert collection.rows == []


@pytest.mark.parametrize(
    "features",
    [
        ("ai.wilsy.starter", "ai.wilsy.growth"),
        (
            "ai.wilsy.starter",
            "ai.wilsy.growth",
            "ai.wilsy.institutional",
        ),
    ],
)
def test_conflicting_tier_features_fail_before_persistence(
    features: tuple[str, ...],
) -> None:
    """Multiple commercial tier features never select by order or default."""
    collection = EntitlementCollection()
    SubscriptionRegistryDouble.items = (subscription(features=features),)
    with pytest.raises(
        service.SubscriptionWilsyAIEntitlementCompositionCommercialError,
        match="D57B_WILSY_AI_VAS_FEATURE_CONFLICT",
    ):
        invoke(entitlement_collection=collection)
    assert collection.rows == []


@pytest.mark.parametrize(
    ("items", "code"),
    [
        ((), "D57B_SUBSCRIPTION_NOT_FOUND"),
        (
            (subscription(status=SubscriptionStatus.PAUSED),),
            "D57B_ACTIVE_SUBSCRIPTION_NOT_FOUND",
        ),
        (
            (
                subscription(subscription_id="one"),
                subscription(subscription_id="two"),
            ),
            "D57B_ACTIVE_SUBSCRIPTION_AMBIGUOUS",
        ),
    ],
)
def test_subscription_cardinality_and_lifecycle_fail_closed(
    items: tuple[SubscriptionEntity, ...],
    code: str,
) -> None:
    """Absent, inactive and ambiguous subscription truth persist nothing."""
    collection = EntitlementCollection()
    SubscriptionRegistryDouble.items = items
    with pytest.raises(
        service.SubscriptionWilsyAIEntitlementCompositionCommercialError,
        match=code,
    ):
        invoke(entitlement_collection=collection)
    assert collection.rows == []


def test_corrupt_subscription_proof_fails_closed() -> None:
    """Altered canonical proof evidence cannot authorize an entitlement."""
    valid = subscription()
    SubscriptionRegistryDouble.items = (replace(valid, proof_hash="f" * 128),)
    with pytest.raises(
        service.SubscriptionWilsyAIEntitlementCompositionCommercialError,
        match="D57B_SUBSCRIPTION_PROOF_INVALID",
    ):
        invoke()


def test_subscription_read_failure_is_bounded_and_writes_nothing() -> None:
    """Registry outage is not converted into commercial absence or success."""
    collection = EntitlementCollection()
    SubscriptionRegistryDouble.failure = RuntimeError("private diagnostic")
    with pytest.raises(
        service.SubscriptionWilsyAIEntitlementCompositionPersistenceError,
        match="D57B_SUBSCRIPTION_UNAVAILABLE",
    ) as failure:
        invoke(entitlement_collection=collection)
    assert "private diagnostic" not in str(failure.value)
    assert collection.rows == []


@pytest.mark.parametrize("failure_mode", ["find", "insert"])
def test_entitlement_persistence_failure_is_bounded(failure_mode: str) -> None:
    """P4 read and write outages never return synthetic entitlement success."""
    collection = EntitlementCollection()
    collection.fail_find = failure_mode == "find"
    collection.fail_insert = failure_mode == "insert"
    SubscriptionRegistryDouble.items = (subscription(),)
    with pytest.raises(
        service.SubscriptionWilsyAIEntitlementCompositionPersistenceError
    ) as failure:
        invoke(entitlement_collection=collection)
    assert "private diagnostic" not in str(failure.value)
    assert collection.rows == []


def test_unexpected_entitlement_read_failure_is_not_treated_as_absence() -> None:
    """Unknown dependency fractures fail closed before provisioning writes."""
    collection = EntitlementCollection()
    SubscriptionRegistryDouble.items = (subscription(),)
    with pytest.raises(
        service.SubscriptionWilsyAIEntitlementCompositionPersistenceError,
        match="D57B_ENTITLEMENT_PERSISTENCE_FAILED",
    ) as failure:
        invoke(
            entitlement_collection=collection,
            entitlement_registry_type=UnexpectedReadFailureRegistry,
        )
    assert "private unexpected diagnostic" not in str(failure.value)
    assert collection.rows == []


def test_exact_tenant_scope_and_same_session_propagate_everywhere() -> None:
    """One exact caller transaction spans subscription and entitlement seams."""
    collection = EntitlementCollection()
    session = Session()
    subscription_collection = object()
    SubscriptionRegistryDouble.items = (subscription(),)
    result = invoke(
        subscription_collection=subscription_collection,
        entitlement_collection=collection,
        session=session,
    )
    assert result.entitlement.tenant_id == "tenant-a"
    assert SubscriptionRegistryDouble.calls == [
        ("tenant-a", subscription_collection, session)
    ]
    assert collection.sessions and all(item is session for item in collection.sessions)


def test_exact_replay_returns_same_canonical_entitlement_without_duplicate() -> None:
    """Same key and evidence replay the sole tenant/module P4 document."""
    collection = EntitlementCollection()
    SubscriptionRegistryDouble.items = (subscription(),)
    first = invoke(entitlement_collection=collection)
    second = invoke(entitlement_collection=collection)
    assert first.entitlement == second.entitlement
    assert first.exact_replay is False and second.exact_replay is True
    assert len(collection.rows) == 1


def test_divergent_same_key_replay_fails_closed() -> None:
    """One replay key cannot be rebound after canonical subscription drift."""
    collection = EntitlementCollection()
    SubscriptionRegistryDouble.items = (subscription(),)
    invoke(entitlement_collection=collection)
    SubscriptionRegistryDouble.items = (
        subscription(features=("ai.wilsy.growth",)),
    )
    with pytest.raises(
        service.SubscriptionWilsyAIEntitlementCompositionDivergentReplayError,
        match="D57B_DIVERGENT_REPLAY",
    ):
        invoke(entitlement_collection=collection)
    assert len(collection.rows) == 1


def test_different_key_cannot_fork_tenant_module_lineage() -> None:
    """P4 tenant/module uniqueness rejects a second command lineage."""
    collection = EntitlementCollection()
    SubscriptionRegistryDouble.items = (subscription(),)
    invoke(entitlement_collection=collection)
    with pytest.raises(
        service.SubscriptionWilsyAIEntitlementCompositionConflictError,
        match="D57B_ENTITLEMENT_PERSISTENCE_CONFLICT",
    ):
        invoke(entitlement_collection=collection, idempotency_key="different-key")
    assert len(collection.rows) == 1


def test_public_contract_rejects_commercial_authority_injection() -> None:
    """Caller cannot supply tier, features, policy, capability or identities."""
    parameters = inspect.signature(
        service.compose_subscription_wilsy_ai_entitlement
    ).parameters
    forbidden = {
        "tier",
        "policy_fingerprint",
        "capability_grants",
        "plan_features",
        "plan_tier",
        "plan_name",
        "feature_id",
        "module_id",
        "subscription_id",
        "entitlement_id",
        "price",
        "payment",
        "invoice",
        "execution",
        "settlement",
    }
    assert forbidden.isdisjoint(parameters)
    SubscriptionRegistryDouble.items = (subscription(),)
    with pytest.raises(TypeError):
        invoke(tier=WilsyAITier.INSTITUTIONAL)


@pytest.mark.parametrize(
    ("tenant_id", "idempotency_key", "session"),
    [
        ("", "key", Session()),
        (" tenant", "key", Session()),
        ("tenant", "", Session()),
        ("tenant", " key", Session()),
        ("tenant", "key", Session(False)),
        ("tenant", "key", object()),
    ],
)
def test_invalid_scope_replay_key_or_transaction_fails_before_read(
    tenant_id: str,
    idempotency_key: str,
    session: object,
) -> None:
    """Malformed orchestration coordinates never reach canonical registries."""
    with pytest.raises(service.SubscriptionWilsyAIEntitlementCompositionInputError):
        invoke(tenant_id=tenant_id, idempotency_key=idempotency_key, session=session)
    assert SubscriptionRegistryDouble.calls == []


def test_service_does_not_mutate_subscription_or_add_external_authority() -> None:
    """Composition leaves subscription value exact and imports no Node/IAM path."""
    item = subscription()
    before = item.to_dict()
    SubscriptionRegistryDouble.items = (item,)
    invoke()
    assert item.to_dict() == before
    source = Path(service.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not any(
        token in name.casefold()
        for name in imports
        for token in ("node", "iam", "payment", "invoice", "settlement")
    )
    assert not any(
        hasattr(service, name)
        for name in ("mutate_subscription", "grant_permission", "execute_payment")
    )


# ARTIFACT: test_subscription_wilsy_ai_entitlement_composition_service.py
# VERSION: v1.0.0-D57B-SUBSCRIPTION-WILSY-AI-COMPOSITION-CERT
# AUTHORITY BOUNDARY: direct D57B composition evidence only; no external authority
# TENANT POSTURE: exact synthetic tenant and caller-session propagation asserted
# FAIL-CLOSED POSTURE: commercial ambiguity, absence, proof drift, persistence failure, conflict and divergent replay reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
