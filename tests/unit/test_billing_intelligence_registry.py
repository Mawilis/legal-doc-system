"""WILSY OS M12-P6 direct certificate for durable billing evidence.

TITLE: Durable Billing Intelligence Evidence Registry Certificate
VERSION: v1.1.0-M12-P6
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify strict P1/P5 evidence persistence, replay, and corruption
         rejection under caller-owned resources.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_billing_intelligence_registry.py
COLLABORATION / OWNERSHIP: Direct registry certificate; P1 owns derivation,
                            P2 owns persistence, and callers own transactions.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.1.0-M12-P6 aligns this direct certificate with the V2 evidence
           contract and recurring-revenue durable schema.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque test tenants only; no secrets or providers.
TENANT BOUNDARY: Every fixture and lookup is tenant-scoped.
AUTHORITY BOUNDARY: Persistence certificate only; no financial execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
FAIL-CLOSED DECLARATION: Schema, provenance, replay, and fingerprint drift reject.
"""
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.saas.billing.billing_intelligence_engine import derive_billing_intelligence
from tools.eos.saas.billing.billing_intelligence_registry import (
    BillingIntelligenceRegistry,
    BillingIntelligenceRegistryError,
)
from tools.eos.saas.domain.commercial_receivable import (
    CommercialReceivable,
    ReceivableFamily,
    ReceivableStatus,
)
from tools.eos.saas.domain.commercial_receivable_aging import CommercialReceivableAging
from tools.eos.saas.domain.commercial_receivable_dunning import CommercialReceivableDunning


TENANT = "tenant-m12"
SOURCE_FP = "a" * 128
AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)


class FakeCollection:
    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []
        self.calls: list[tuple[str, Any]] = []
        self.indexes: list[tuple[Any, Any]] = []

    def create_index(self, keys: Any, **options: Any) -> str:
        self.indexes.append((keys, options))
        return str(options.get("name", "index"))

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> dict[str, Any] | None:
        self.calls.append(("find_one", session))
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                return deepcopy(document)
        return None

    def insert_one(self, document: dict[str, Any], *, session: Any = None) -> None:
        self.calls.append(("insert_one", session))
        self.documents.append(deepcopy(document))


class Session:
    in_transaction = True


def make_receivable(*, amount: int = 1250) -> CommercialReceivable:
    return CommercialReceivable(
        tenant_id=TENANT,
        receivable_family=ReceivableFamily.CLIENT,
        receivable_id="r-1",
        source_invoice_id="invoice-1",
        currency="ZAR",
        original_amount_minor=amount,
        adjustment_amount_minor=0,
        outstanding_amount_minor=amount,
        source_invoice_fingerprint=SOURCE_FP,
        status=ReceivableStatus.OPEN,
    )


def make_value(*, amount: int = 1250):
    receivable = make_receivable(amount=amount)
    aging = CommercialReceivableAging.from_receivable(
        receivable,
        due_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        as_of=AS_OF,
    )
    dunning = CommercialReceivableDunning.from_aging(
        aging,
        effective_at=AS_OF,
    )
    return derive_billing_intelligence(
        tenant_id=TENANT,
        receivables=(receivable,),
        aging=(aging,),
        dunning=(dunning,),
        as_of=AS_OF,
    )


def test_indexes_are_tenant_scoped_and_unique() -> None:
    collection = FakeCollection()
    BillingIntelligenceRegistry.ensure_indexes(collection)
    assert len(collection.indexes) == 2
    assert all(options["unique"] is True for _, options in collection.indexes)
    assert all(keys[0][0] == "tenant_id" for keys, _ in collection.indexes)


def test_create_get_round_trip_preserves_exact_p1_value_and_document() -> None:
    collection = FakeCollection()
    value = make_value()
    created = BillingIntelligenceRegistry.create(value, collection)
    identity = collection.documents[0]["evidence_identity"]
    hydrated = BillingIntelligenceRegistry.get(TENANT, identity, collection)
    assert created == hydrated == value
    assert collection.documents[0]["evidence_fingerprint"] == value.evidence_fingerprint
    assert collection.documents[0]["source_provenance"] == value.to_dict()["source_provenance"]


def test_exact_replay_does_not_create_second_row() -> None:
    collection = FakeCollection()
    value = make_value()
    first = BillingIntelligenceRegistry.create(value, collection)
    second = BillingIntelligenceRegistry.create(value, collection)
    assert first == second == value
    assert len(collection.documents) == 1


def test_same_identity_divergence_fails_closed() -> None:
    collection = FakeCollection()
    value = make_value()
    BillingIntelligenceRegistry.create(value, collection)
    divergent = make_value(amount=1249)
    with pytest.raises(BillingIntelligenceRegistryError, match="REPLAY_CONFLICT|FINGERPRINT"):
        BillingIntelligenceRegistry.create(divergent, collection)


def test_fingerprint_provenance_and_derived_corruption_reject() -> None:
    collection = FakeCollection()
    value = make_value()
    BillingIntelligenceRegistry.create(value, collection)
    identity = collection.documents[0]["evidence_identity"]
    collection.documents[0]["evidence_fingerprint"] = "b" * 128
    with pytest.raises(BillingIntelligenceRegistryError):
        BillingIntelligenceRegistry.get(TENANT, identity, collection)
    collection.documents[0]["evidence_fingerprint"] = value.evidence_fingerprint
    collection.documents[0]["receivable_count"] = 99
    with pytest.raises(BillingIntelligenceRegistryError):
        BillingIntelligenceRegistry.get(TENANT, identity, collection)


def test_provenance_corruption_and_unknown_version_reject() -> None:
    collection = FakeCollection()
    value = make_value()
    BillingIntelligenceRegistry.create(value, collection)
    identity = collection.documents[0]["evidence_identity"]
    collection.documents[0]["source_provenance"][0][2] = "c" * 128
    with pytest.raises(BillingIntelligenceRegistryError):
        BillingIntelligenceRegistry.get(TENANT, identity, collection)
    collection.documents[0]["source_provenance"] = value.to_dict()["source_provenance"]
    collection.documents[0]["evidence_contract"] = "WILSY-BILLING-INTELLIGENCE-EVIDENCE/V3"
    with pytest.raises(BillingIntelligenceRegistryError, match="VERSION"):
        BillingIntelligenceRegistry.get(TENANT, identity, collection)


def test_schema_and_type_corruption_reject() -> None:
    collection = FakeCollection()
    value = make_value()
    BillingIntelligenceRegistry.create(value, collection)
    identity = collection.documents[0]["evidence_identity"]
    collection.documents[0]["unexpected"] = True
    with pytest.raises(BillingIntelligenceRegistryError, match="SCHEMA"):
        BillingIntelligenceRegistry.get(TENANT, identity, collection)


def test_cross_tenant_lookup_fails_closed() -> None:
    collection = FakeCollection()
    BillingIntelligenceRegistry.create(make_value(), collection)
    identity = collection.documents[0]["evidence_identity"]
    with pytest.raises(BillingIntelligenceRegistryError, match="NOT_FOUND"):
        BillingIntelligenceRegistry.get("tenant-other", identity, collection)


def test_session_is_forwarded_and_registry_has_no_transaction_lifecycle() -> None:
    collection = FakeCollection()
    session = Session()
    BillingIntelligenceRegistry.create(make_value(), collection, session=session)
    assert all(call_session is session for _, call_session in collection.calls)
    assert not hasattr(BillingIntelligenceRegistry, "start_transaction")
    assert not hasattr(BillingIntelligenceRegistry, "commit")
    assert not hasattr(BillingIntelligenceRegistry, "abort")


def test_collection_is_injected_and_no_external_client_dependency() -> None:
    collection = FakeCollection()
    BillingIntelligenceRegistry.create(make_value(), collection)
    assert len(collection.documents) == 1
    assert not hasattr(BillingIntelligenceRegistry, "mongo_client")


def test_missing_forbidden_and_unsupported_fields_fail_closed() -> None:
    collection = FakeCollection()
    value = make_value()
    BillingIntelligenceRegistry.create(value, collection)
    identity = collection.documents[0]["evidence_identity"]
    del collection.documents[0]["source_provenance"]
    with pytest.raises(BillingIntelligenceRegistryError, match="SCHEMA"):
        BillingIntelligenceRegistry.get(TENANT, identity, collection)


def test_document_serialization_is_deterministic_and_identity_is_immutable() -> None:
    first, second = make_value(), make_value()
    assert first.to_dict() == second.to_dict()
    first_collection, second_collection = FakeCollection(), FakeCollection()
    BillingIntelligenceRegistry.create(first, first_collection)
    BillingIntelligenceRegistry.create(second, second_collection)
    assert first_collection.documents[0]["evidence_identity"] == second_collection.documents[0]["evidence_identity"]


# ARTIFACT: test_billing_intelligence_registry.py
# VERSION: v1.1.0-M12-P6
# AUTHORITY BOUNDARY: Persistence and strict hydration certificate only.
# TENANT POSTURE: Explicit tenant-scoped fixtures and lookups.
# FAIL-CLOSED POSTURE: Schema, provenance, and replay divergence reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
