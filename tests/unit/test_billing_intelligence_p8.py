"""WILSY OS M12-P8 direct certificate for recurring-revenue growth integration.

TITLE: Canonical Billing Intelligence P8 Growth Integration Certificate
VERSION: v1.0.0-M12-P8
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove explicit prior-evidence lookup, P7 growth composition, strict
          P2 persistence/replay, and unchanged financial authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_billing_intelligence_p8.py
COLLABORATION / OWNERSHIP: Direct certificate for P8 engine, registry, and
                            orchestrator integration; HTTP remains the existing
                            canonical transport seam.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M12-P8 certifies explicit prior identity, deterministic growth,
           strict hydration, replay, corruption rejection, and fail-closed
           financial boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: In-memory opaque fixtures only; no secrets or
                             external clients.
TENANT BOUNDARY: Every lookup and source document carries explicit tenant_id.
AUTHORITY BOUNDARY: Billing intelligence evidence only; no payment execution,
                    settlement, invoice, receivable, or paid-state authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and
                               settlement truth.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.saas.billing.billing_intelligence_engine import (
    BillingIntelligenceError,
    derive_billing_intelligence,
)
from tools.eos.saas.billing.billing_intelligence_orchestrator import (
    BillingIntelligenceOrchestrator,
    BillingIntelligenceOrchestratorError,
)
from tools.eos.saas.billing.billing_intelligence_registry import (
    BillingIntelligenceRegistry,
    BillingIntelligenceRegistryError,
)
from tools.eos.saas.billing.subscription_registry import _create_material, _fingerprint_create_material
from tools.eos.saas.billing.recurring_revenue_policy import derive_recurring_revenue
from tools.eos.saas.domain.subscription import BillingFrequency, PlanTiers, SubscriptionEntity, SubscriptionStatus


TENANT = "tenant-m12-p8"
AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)


class Collection:
    """Minimal injected collection retaining tenant/session semantics."""

    def __init__(self, documents: list[dict[str, Any]] | None = None) -> None:
        self.documents = documents or []
        self.sessions: list[Any] = []

    def find(self, query: dict[str, Any], *, session: Any = None) -> list[dict[str, Any]]:
        self.sessions.append(session)
        return [deepcopy(item) for item in self.documents if all(item.get(key) == value for key, value in query.items())]

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> dict[str, Any] | None:
        self.sessions.append(session)
        for item in self.documents:
            if all(item.get(key) == value for key, value in query.items()):
                return deepcopy(item)
        return None

    def insert_one(self, document: dict[str, Any], *, session: Any = None) -> None:
        self.sessions.append(session)
        self.documents.append(deepcopy(document))

    def create_index(self, *_args: Any, **_kwargs: Any) -> None:
        return None


def _subscription(tenant: str = TENANT, amount: float = 120.0) -> SubscriptionEntity:
    return SubscriptionEntity(
        tenant_id=tenant,
        plan_id="plan-p8",
        plan=PlanTiers.PROFESSIONAL,
        amount=amount,
        currency="ZAR",
        billing_frequency=BillingFrequency.MONTHLY,
        start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        current_period_start=datetime(2026, 9, 1, tzinfo=timezone.utc),
        current_period_end=datetime(2026, 10, 1, tzinfo=timezone.utc),
        idempotency_key=f"idem-{tenant}",
        subscription_id=f"sub-{tenant}",
        status=SubscriptionStatus.ACTIVE,
        plan_catalogue_version=1,
    )


def _owner(tenant: str = TENANT, amount: float = 120.0) -> tuple[BillingIntelligenceOrchestrator, Collection, Collection]:
    value = _subscription(tenant, amount)
    material = _create_material(tenant, {"idempotencyKey": value.idempotency_key})
    document = value.to_dict() | {
        "_registry_schema": "WILSY-SUBSCRIPTION-REGISTRY/V1",
        "_registry_create_material": material,
        "_registry_create_fingerprint": _fingerprint_create_material(material),
        "_registry_revision": 1,
    }
    subscriptions = Collection([document])
    evidence = Collection()
    empty = Collection()
    return BillingIntelligenceOrchestrator(
        receivable_collection=empty,
        aging_collection=empty,
        dunning_collection=empty,
        evidence_collection=evidence,
        subscription_collection=subscriptions,
    ), evidence, subscriptions


def _persisted_prior() -> tuple[BillingIntelligenceOrchestrator, Collection, str]:
    owner, evidence, _subscriptions = _owner(amount=100.0)
    prior = owner.collect_and_persist(TENANT, as_of=AS_OF - timedelta(days=1))
    identity = owner.response_payload(prior)["evidence_identity"]
    assert isinstance(identity, str)
    return owner, evidence, identity


def test_explicit_prior_identity_composes_positive_growth_and_forwards_session() -> None:
    owner, evidence, identity = _persisted_prior()
    value = _subscription(amount=125.0)
    material = _create_material(TENANT, {"idempotencyKey": value.idempotency_key})
    current_subscriptions = Collection([value.to_dict() | {
        "_registry_schema": "WILSY-SUBSCRIPTION-REGISTRY/V1",
        "_registry_create_material": material,
        "_registry_create_fingerprint": _fingerprint_create_material(material),
        "_registry_revision": 1,
    }])
    owner = BillingIntelligenceOrchestrator(
        receivable_collection=Collection(), aging_collection=Collection(), dunning_collection=Collection(),
        evidence_collection=evidence, subscription_collection=current_subscriptions,
    )
    session = object()
    current = owner.collect_and_persist(TENANT, as_of=AS_OF, session=session, prior_evidence_identity=identity)
    assert current.recurring_revenue_growth is not None
    assert current.recurring_revenue_growth.classification.value == "POSITIVE"
    assert current.recurring_revenue_growth.growth_numerator == 2500
    assert current.recurring_revenue_growth.growth_denominator == 10000
    assert current.recurring_revenue is not None
    assert current.recurring_revenue_growth.current_source_fingerprint == current.recurring_revenue.fingerprint
    assert session in evidence.sessions and session in current_subscriptions.sessions


@pytest.mark.parametrize("current_amount, classification", [(75.0, "CONTRACTION"), (100.0, "NO_CHANGE")])
def test_contraction_and_no_change_are_exact(current_amount: float, classification: str) -> None:
    owner, evidence, identity = _persisted_prior()
    value = _subscription(amount=current_amount)
    material = _create_material(TENANT, {"idempotencyKey": value.idempotency_key})
    current_subscriptions = Collection([value.to_dict() | {
        "_registry_schema": "WILSY-SUBSCRIPTION-REGISTRY/V1",
        "_registry_create_material": material,
        "_registry_create_fingerprint": _fingerprint_create_material(material),
        "_registry_revision": 1,
    }])
    owner = BillingIntelligenceOrchestrator(
        receivable_collection=Collection(), aging_collection=Collection(), dunning_collection=Collection(),
        evidence_collection=evidence, subscription_collection=current_subscriptions,
    )
    current = owner.collect_and_persist(TENANT, as_of=AS_OF, prior_evidence_identity=identity)
    assert current.recurring_revenue_growth is not None
    assert current.recurring_revenue_growth.classification.value == classification


def test_no_prior_identity_keeps_growth_absent() -> None:
    owner, _evidence, _subscriptions = _owner()
    current = owner.collect_and_persist(TENANT, as_of=AS_OF)
    assert current.recurring_revenue_growth is None


def test_missing_cross_tenant_and_prior_without_recurring_fail_closed() -> None:
    owner, evidence, _identity = _persisted_prior()
    with pytest.raises(BillingIntelligenceOrchestratorError, match="NOT_FOUND"):
        owner.collect_and_persist(TENANT, as_of=AS_OF, prior_evidence_identity="f" * 128)
    other_owner, other_evidence, other_identity = _persisted_prior()
    assert isinstance(other_identity, str)
    with pytest.raises(BillingIntelligenceOrchestratorError, match="NOT_FOUND"):
        other_owner.collect_and_persist("tenant-other", as_of=AS_OF, prior_evidence_identity=other_identity)
    prior_without_recurring = derive_billing_intelligence(tenant_id=TENANT, as_of=None)
    # A zero-source P1 record is not persistable through the orchestrator, so
    # direct P2 insertion proves the explicit prior-without-recurring rejection.
    BillingIntelligenceRegistry.create(prior_without_recurring, evidence)
    prior_identity = other_owner.response_payload(prior_without_recurring)["evidence_identity"]
    assert isinstance(prior_identity, str)
    with pytest.raises(BillingIntelligenceOrchestratorError, match="PRIOR_RECURRING"):
        owner.collect_and_persist(TENANT, as_of=AS_OF, prior_evidence_identity=prior_identity)


def test_prior_after_or_equal_current_and_no_heuristic_lookup_fail_closed() -> None:
    owner, _evidence, identity = _persisted_prior()
    with pytest.raises(BillingIntelligenceOrchestratorError, match="PRIOR_AS_OF_ORDER"):
        owner.collect_and_persist(TENANT, as_of=AS_OF - timedelta(days=2), prior_evidence_identity=identity)
    current = owner.collect_and_persist(TENANT, as_of=AS_OF)
    assert current.recurring_revenue_growth is None


def test_zero_baseline_undefined_classification() -> None:
    prior = derive_recurring_revenue(tenant_id=TENANT, as_of=AS_OF - timedelta(days=1), subscriptions=(_subscription(amount=0.0),))
    current = derive_recurring_revenue(tenant_id=TENANT, as_of=AS_OF, subscriptions=(_subscription(amount=100.0),))
    from tools.eos.saas.billing.recurring_revenue_growth_policy import derive_recurring_revenue_growth
    growth = derive_recurring_revenue_growth(prior=prior, current=current)
    assert growth.classification.value == "RATE_UNDEFINED_ZERO_BASELINE"
    assert growth.growth_numerator is None and growth.growth_denominator is None


def test_p2_exact_replay_and_corruption_rejection() -> None:
    owner, evidence, identity = _persisted_prior()
    replay = owner.collect_and_persist(TENANT, as_of=AS_OF - timedelta(days=1), prior_evidence_identity=None)
    assert replay.recurring_revenue_growth is None
    hydrated = BillingIntelligenceRegistry.get(TENANT, identity, evidence)
    assert hydrated == owner.collect_and_persist(TENANT, as_of=AS_OF - timedelta(days=1))
    document = evidence.documents[0]
    document["recurring_revenue_growth"] = {"unexpected": True}
    with pytest.raises(BillingIntelligenceRegistryError):
        BillingIntelligenceRegistry.get(TENANT, identity, evidence)


def test_engine_binds_growth_and_rejects_mismatch() -> None:
    from tools.eos.saas.billing.recurring_revenue_growth_policy import derive_recurring_revenue_growth
    prior = derive_recurring_revenue(tenant_id=TENANT, as_of=AS_OF - timedelta(days=1), subscriptions=(_subscription(amount=100.0),))
    current_value = _subscription(amount=125.0)
    current = derive_recurring_revenue(tenant_id=TENANT, as_of=AS_OF, subscriptions=(current_value,))
    growth = derive_recurring_revenue_growth(prior=prior, current=current)
    value = derive_billing_intelligence(tenant_id=TENANT, subscriptions=(current_value,), as_of=AS_OF, recurring_revenue_growth=growth)
    serialized = value.to_dict()["recurring_revenue_growth"]
    assert isinstance(serialized, dict)
    assert serialized["fingerprint"] == growth.fingerprint
    with pytest.raises(BillingIntelligenceError, match="SOURCE_MISMATCH"):
        derive_billing_intelligence(tenant_id=TENANT, subscriptions=(_subscription(amount=120.0),), as_of=AS_OF, recurring_revenue_growth=growth)


# ARTIFACT: test_billing_intelligence_p8.py
# VERSION: v1.0.0-M12-P8
# AUTHORITY BOUNDARY: P8 derived evidence composition only.
# TENANT POSTURE: Explicit tenant-scoped lookups; cross-tenant identities fail closed.
# FAIL-CLOSED POSTURE: Missing, divergent, corrupt, or inferred prior evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
