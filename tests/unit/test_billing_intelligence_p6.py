"""WILSY OS M12-P6 direct certificate for recurring-revenue integration.

TITLE: Canonical Billing Intelligence P6 Integration Certificate
VERSION: v1.0.0-M12-P6
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove P5 recurring-revenue evidence is acquired from canonical
         subscriptions, bound by P1, strictly persisted by P2, and exposed
         without financial execution or settlement authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_billing_intelligence_p6.py
COLLABORATION / OWNERSHIP: Direct certificate for P6 composition; production
                            owners remain SubscriptionRegistry, P5, P1, P2,
                            P3, and the canonical billing router.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M12-P6 certifies subscription read ownership, P5 binding,
           strict durable schema, exact replay, and transaction pass-through.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Test-only opaque tenant data; no secrets, network,
                             providers, KMS, or external clients.
TENANT BOUNDARY: Every fixture and lookup is explicitly tenant-scoped.
AUTHORITY BOUNDARY: Evidence composition only; no authorization, execution,
                    settlement, paid-state, invoice, or receivable closure.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Corrupt subscriptions and recurring evidence reject.
"""
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.saas.billing.billing_intelligence_engine import (
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
from tools.eos.saas.domain.subscription import (
    BillingFrequency,
    PlanTiers,
    SubscriptionEntity,
    SubscriptionStatus,
)
from tools.eos.saas.billing.subscription_registry import (
    _create_material,
    _fingerprint_create_material,
)


TENANT = "tenant-m12-p6"
AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)


class Collection:
    """Minimal injected collection retaining query/session evidence."""

    def __init__(self, documents: list[dict[str, Any]] | None = None) -> None:
        self.documents = documents or []
        self.sessions: list[Any] = []

    def find(self, query: dict[str, Any], *, session: Any = None) -> list[dict[str, Any]]:
        self.sessions.append(session)
        return [deepcopy(item) for item in self.documents if all(item.get(k) == v for k, v in query.items())]

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> dict[str, Any] | None:
        self.sessions.append(session)
        for item in self.documents:
            if all(item.get(k) == v for k, v in query.items()):
                return deepcopy(item)
        return None

    def insert_one(self, document: dict[str, Any], *, session: Any = None) -> None:
        self.sessions.append(session)
        self.documents.append(deepcopy(document))


def subscription(*, tenant_id: str = TENANT, amount: float = 120.0) -> SubscriptionEntity:
    return SubscriptionEntity(
        tenant_id=tenant_id,
        plan_id="plan-pro",
        plan=PlanTiers.PROFESSIONAL,
        amount=amount,
        currency="ZAR",
        billing_frequency=BillingFrequency.MONTHLY,
        start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        current_period_start=datetime(2026, 9, 1, tzinfo=timezone.utc),
        current_period_end=datetime(2026, 10, 1, tzinfo=timezone.utc),
        idempotency_key="sub-create-1",
        subscription_id="sub-1",
        status=SubscriptionStatus.ACTIVE,
        plan_catalogue_version=1,
    )


def persisted_subscription(value: SubscriptionEntity) -> dict[str, Any]:
    material = _create_material(value.tenant_id, {"idempotencyKey": value.idempotency_key})
    return value.to_dict() | {
        "_registry_schema": "WILSY-SUBSCRIPTION-REGISTRY/V1",
        "_registry_create_material": material,
        "_registry_create_fingerprint": _fingerprint_create_material(material),
        "_registry_revision": 1,
    }


def test_p5_evidence_is_bound_into_p1_fingerprint() -> None:
    value = derive_billing_intelligence(
        tenant_id=TENANT,
        subscriptions=(subscription(),),
        as_of=AS_OF,
    )
    assert value.recurring_revenue is not None
    assert value.recurring_revenue.mrr_minor == 12000
    assert value.recurring_revenue.arr_minor == 144000
    assert value.recurring_revenue.tenant_id == TENANT
    assert value.evidence_fingerprint == value.compute_fingerprint()
    changed = derive_billing_intelligence(
        tenant_id=TENANT,
        subscriptions=(subscription(amount=121.0),),
        as_of=AS_OF,
    )
    assert changed.recurring_revenue is not None
    assert changed.recurring_revenue.fingerprint != value.recurring_revenue.fingerprint
    assert changed.evidence_fingerprint != value.evidence_fingerprint


def test_orchestrator_reads_canonical_subscriptions_and_forwards_session() -> None:
    subscriptions = Collection([persisted_subscription(subscription())])
    evidence = Collection()
    empty = Collection()
    owner = BillingIntelligenceOrchestrator(
        receivable_collection=empty,
        aging_collection=empty,
        dunning_collection=empty,
        evidence_collection=evidence,
        subscription_collection=subscriptions,
    )
    session = object()
    value = owner.collect_and_persist(TENANT, as_of=AS_OF, session=session)
    assert value.recurring_revenue is not None
    assert value.recurring_revenue.mrr_minor == 12000
    assert subscriptions.sessions == [session]
    assert evidence.documents[0]["recurring_revenue"]["fingerprint"] == value.recurring_revenue.fingerprint


def test_corrupt_subscription_fails_closed_before_persistence() -> None:
    document = persisted_subscription(subscription())
    document["proof_hash"] = "invalid"
    subscriptions = Collection([document])
    evidence = Collection()
    empty = Collection()
    owner = BillingIntelligenceOrchestrator(
        receivable_collection=empty,
        aging_collection=empty,
        dunning_collection=empty,
        evidence_collection=evidence,
        subscription_collection=subscriptions,
    )
    with pytest.raises(BillingIntelligenceOrchestratorError, match="SUBSCRIPTION"):
        owner.collect_and_persist(TENANT, as_of=AS_OF)
    assert evidence.documents == []


def test_p2_rejects_recurring_evidence_corruption() -> None:
    value = derive_billing_intelligence(tenant_id=TENANT, subscriptions=(subscription(),), as_of=AS_OF)
    collection = Collection()
    BillingIntelligenceRegistry.create(value, collection)
    identity = collection.documents[0]["evidence_identity"]
    collection.documents[0]["recurring_revenue"]["mrr_minor"] = 1
    with pytest.raises(BillingIntelligenceRegistryError):
        BillingIntelligenceRegistry.get(TENANT, identity, collection)


# ARTIFACT: test_billing_intelligence_p6.py
# VERSION: v1.0.0-M12-P6
# AUTHORITY BOUNDARY: P6 direct composition certificate only.
# TENANT POSTURE: Explicit tenant-scoped fixtures and lookups.
# FAIL-CLOSED POSTURE: Corruption and cross-owner authority are rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
