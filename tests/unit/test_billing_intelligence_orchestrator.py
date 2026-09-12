"""M12-P3 direct certificate for canonical billing-intelligence composition.

TITLE: Billing Intelligence Orchestrator Certificate
VERSION: v1.0.0-M12-P3
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove tenant source hydration, frozen P1 delegation, and frozen P2
         persistence without transaction or financial-authority ownership.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_billing_intelligence_orchestrator.py
"""
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.saas.billing.billing_intelligence_orchestrator import (
    BillingIntelligenceOrchestrator,
    BillingIntelligenceOrchestratorError,
    parse_as_of,
)
from tools.eos.saas.domain.commercial_receivable import (
    CommercialReceivable,
    ReceivableFamily,
    ReceivableStatus,
)
from tools.eos.saas.domain.commercial_receivable_aging import CommercialReceivableAging
from tools.eos.saas.domain.commercial_receivable_dunning import CommercialReceivableDunning


TENANT = "tenant-m12-p3"
AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)


class Collection:
    def __init__(self, documents: list[dict[str, Any]] | None = None) -> None:
        self.documents = documents or []
        self.sessions: list[Any] = []

    def find(self, query: dict[str, Any], *, session: Any = None) -> list[dict[str, Any]]:
        self.sessions.append(session)
        return [deepcopy(doc) for doc in self.documents if all(doc.get(k) == v for k, v in query.items())]

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> dict[str, Any] | None:
        self.sessions.append(session)
        matches = self.find(query, session=session)
        return matches[0] if matches else None

    def insert_one(self, document: dict[str, Any], *, session: Any = None) -> None:
        self.sessions.append(session)
        self.documents.append(deepcopy(document))


class Session:
    in_transaction = True


def source_collections() -> tuple[Collection, Collection, Collection]:
    receivable = CommercialReceivable(
        tenant_id=TENANT,
        receivable_family=ReceivableFamily.CLIENT,
        receivable_id="r-1",
        source_invoice_id="invoice-1",
        currency="ZAR",
        original_amount_minor=1250,
        adjustment_amount_minor=0,
        outstanding_amount_minor=1250,
        source_invoice_fingerprint="a" * 128,
        status=ReceivableStatus.OPEN,
    )
    aging = CommercialReceivableAging.from_receivable(
        receivable,
        due_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        as_of=AS_OF,
    )
    dunning = CommercialReceivableDunning.from_aging(aging, effective_at=AS_OF)
    return (
        Collection([receivable.to_dict()]),
        Collection([aging.to_dict()]),
        Collection([dunning.to_dict()]),
    )


def orchestrator() -> tuple[BillingIntelligenceOrchestrator, Collection, Collection, Collection, Collection]:
    receivables, aging, dunning = source_collections()
    evidence = Collection()
    return BillingIntelligenceOrchestrator(
        receivable_collection=receivables,
        aging_collection=aging,
        dunning_collection=dunning,
        evidence_collection=evidence,
    ), receivables, aging, dunning, evidence


def test_composes_frozen_p1_and_p2_with_exact_identity() -> None:
    owner, _, _, _, evidence = orchestrator()
    value = owner.collect_and_persist(TENANT, as_of=AS_OF)
    payload = owner.response_payload(value)
    assert payload["tenant_id"] == TENANT
    assert payload["evidence_identity"] == evidence.documents[0]["evidence_identity"]
    assert payload["evidence_fingerprint"] == evidence.documents[0]["evidence_fingerprint"]
    assert payload["unsupported_outputs"]


def test_exact_replay_has_one_durable_evidence_record() -> None:
    owner, _, _, _, evidence = orchestrator()
    first = owner.collect_and_persist(TENANT, as_of=AS_OF)
    second = owner.collect_and_persist(TENANT, as_of=AS_OF)
    assert first == second
    assert len(evidence.documents) == 1


def test_global_tenant_and_naive_snapshot_fail_closed() -> None:
    owner, *_ = orchestrator()
    with pytest.raises(BillingIntelligenceOrchestratorError, match="GLOBAL"):
        owner.collect_and_persist("GLOBAL_ROOT", as_of=AS_OF)
    with pytest.raises(BillingIntelligenceOrchestratorError, match="AS_OF"):
        parse_as_of("2026-09-12T12:00:00")


def test_corrupt_source_rejects_before_persistence() -> None:
    owner, receivables, _, _, evidence = orchestrator()
    receivables.documents[0]["receivable_fingerprint"] = "b" * 128
    with pytest.raises(BillingIntelligenceOrchestratorError, match="RECEIVABLE"):
        owner.collect_and_persist(TENANT, as_of=AS_OF)
    assert evidence.documents == []


def test_session_is_forwarded_and_transaction_lifecycle_is_caller_owned() -> None:
    owner, receivables, aging, dunning, evidence = orchestrator()
    session = Session()
    owner.collect_and_persist(TENANT, as_of=AS_OF, session=session)
    assert receivables.sessions and all(item is session for item in receivables.sessions)
    assert aging.sessions and all(item is session for item in aging.sessions)
    assert dunning.sessions and all(item is session for item in dunning.sessions)
    assert evidence.sessions and all(item is session for item in evidence.sessions)
    assert not hasattr(owner, "start_transaction")
    assert not hasattr(owner, "commit")
    assert not hasattr(owner, "abort")


# ARTIFACT: test_billing_intelligence_orchestrator.py
# VERSION: v1.0.0-M12-P3
# AUTHORITY BOUNDARY: Composition certificate only.
# END OF WILSY OS SOVEREIGN ARTIFACT
