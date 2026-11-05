"""Real replica-set certificate for immutable settlement allocations."""
from datetime import datetime, timezone
import os
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.saas.domain.platform_invoice_settlement_allocation import PlatformInvoiceSettlementAllocation
from tools.eos.saas.billing.platform_invoice_settlement_allocation_registry import (
    PlatformInvoiceSettlementAllocationConflict,
    PlatformInvoiceSettlementAllocationRegistry,
)

URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"


@pytest.fixture()
def mongo_allocation_collection():
    assert os.environ.get("TEST_VENDOR_MONGO_URI") == URI
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    assert client.admin.command("hello").get("isWritablePrimary") is True
    db = client[f"invoice_allocation_{uuid4().hex}"]
    collection = db["allocations"]
    PlatformInvoiceSettlementAllocationRegistry.ensure_indexes(collection)
    try:
        yield client, collection
    finally:
        client.drop_database(db.name)
        client.close()


def value(tenant_id="tenant-a", observation_id="obs-1", amount=4000):
    return PlatformInvoiceSettlementAllocation(
        tenant_id=tenant_id,
        allocation_id=f"allocation-{observation_id}",
        observation_id=observation_id,
        observation_fingerprint="a" * 128,
        execution_truth_id="execution-1",
        invoice_id="invoice-1",
        invoice_evidence_fingerprint="b" * 128,
        currency="ZAR",
        amount_minor=amount,
        cumulative_paid_minor=amount,
        outstanding_minor=10000 - amount,
        allocation_sequence=1,
        allocated_at=datetime(2026, 11, 5, tzinfo=timezone.utc),
        allocation_status="PARTIAL",
    )


def test_durable_exact_replay_and_divergent_replay_rejection(mongo_allocation_collection):
    client, collection = mongo_allocation_collection
    first = value()
    with client.start_session() as session:
        with session.start_transaction():
            PlatformInvoiceSettlementAllocationRegistry.create(first, collection, session=session)
    with client.start_session() as session:
        with session.start_transaction():
            replay = PlatformInvoiceSettlementAllocationRegistry.create(first, collection, session=session)
            assert replay.fingerprint == first.fingerprint
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(PlatformInvoiceSettlementAllocationConflict):
                PlatformInvoiceSettlementAllocationRegistry.create(
                    value(amount=5000), collection, session=session
                )
    assert collection.count_documents({"tenant_id": "tenant-a"}) == 1


def test_allocation_abort_rolls_back_and_tenant_identity_isolated(mongo_allocation_collection):
    client, collection = mongo_allocation_collection
    with client.start_session() as session:
        with pytest.raises(RuntimeError, match="abort"):
            with session.start_transaction():
                PlatformInvoiceSettlementAllocationRegistry.create(value(), collection, session=session)
                raise RuntimeError("abort")
    assert collection.count_documents({"tenant_id": "tenant-a"}) == 0
    with client.start_session() as session:
        with session.start_transaction():
            PlatformInvoiceSettlementAllocationRegistry.create(value("tenant-a"), collection, session=session)
    with client.start_session() as session:
        with session.start_transaction():
            PlatformInvoiceSettlementAllocationRegistry.create(value("tenant-b"), collection, session=session)
    assert collection.count_documents({"observation_id": "obs-1"}) == 2


def _real_invoice_orchestration_fixture(monkeypatch, db):
    from types import SimpleNamespace
    from tools.eos.kennel.domain.financial_execution import FinancialExecutionStatus
    from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformExecutionStatus
    from tools.eos.saas.domain.billing import InvoiceStatus
    import tools.eos.saas.billing.platform_invoice_settlement_allocation as module

    tenant_id = "tenant-e2e"
    invoice_id = "invoice-e2e"
    fact_id = "fact-e2e"
    execution_reference = "uetr-e2e-unique"
    destination = "destination-e2e"
    release_fingerprint = "d" * 128
    commercial_fingerprint = "c" * 128
    now = datetime(2026, 11, 5, 8, 0, tzinfo=timezone.utc)

    observations = {}
    facts = {}
    platform_truths = {}
    def ensure_execution(observation_id, amount_minor):
        local_fact_id = f"fact-{observation_id}"
        local_reference = f"uetr-{observation_id}"
        fact = SimpleNamespace(
            tenant_id=tenant_id, execution_fact_id=local_fact_id, fingerprint=(observation_id[-1] * 128),
            execution_status=FinancialExecutionStatus.EXECUTED, provider="ELECTRUM",
            provider_execution_reference=local_reference, currency="ZAR",
            payment_destination_reference=destination, executed_amount_minor=amount_minor,
        )
        truth = SimpleNamespace(
            tenant_id=tenant_id, execution_truth_id=f"platform-truth-{local_fact_id}",
            execution_status=PlatformExecutionStatus.EXECUTED,
            source_execution_fact_id=local_fact_id, source_execution_fact_fingerprint=fact.fingerprint,
            provider="ELECTRUM", provider_execution_reference=local_reference,
            currency="ZAR", payment_destination_reference=destination,
            executed_amount_minor=amount_minor, platform_invoice_id=invoice_id,
            release_authorization_id="release-e2e",
            release_authorization_fingerprint=release_fingerprint,
        )
        facts[local_fact_id] = fact
        platform_truths[truth.execution_truth_id] = truth
        db["platform_truth"].insert_one({
            "tenant_id": tenant_id,
            "source_execution_fact_id": local_fact_id,
            "execution_truth_id": truth.execution_truth_id,
            "provider_execution_reference": local_reference,
        })
        return local_fact_id, local_reference
    authorization = SimpleNamespace(
        tenant_id=tenant_id, platform_invoice_id=invoice_id, currency="ZAR",
        authorized_amount_minor=10000,
        platform_invoice_evidence_fingerprint=commercial_fingerprint,
        payment_destination_reference=destination,
        release_authorization_fingerprint=release_fingerprint,
    )

    def invoice_model(doc):
        return SimpleNamespace(
            tenant_id=tenant_id, invoice_id=invoice_id, currency=doc["currency"],
            status=InvoiceStatus(doc["status"]), paid_at=doc.get("paid_at"),
            amount_paid=doc.get("amount_paid", 0.0),
            outstanding_amount=doc.get("outstanding_amount", 100.0),
            release_amount_minor=10000,
            commercial_release_evidence_fingerprint=commercial_fingerprint,
        )

    monkeypatch.setattr(module.FinancialSettlementObservationRegistry, "get",
                        lambda tenant, observation_id, collection, session=None: observations[observation_id])
    monkeypatch.setattr(module.FinancialExecutionFactRegistry, "get",
                        lambda tenant, execution_truth_id, collection, session=None: facts[execution_truth_id])
    monkeypatch.setattr(module.PlatformBillingFinancialExecutionTruthRegistry, "get",
                        lambda tenant, execution_truth_id, collection, session=None: platform_truths[execution_truth_id])
    monkeypatch.setattr(module.PlatformBillingReleaseAuthorizationRegistry, "get",
                        lambda *args, **kwargs: authorization)
    monkeypatch.setattr(module, "PlatformInvoice", SimpleNamespace(from_dict=invoice_model))

    invoices = db["invoices"]
    allocations = db["allocations"]
    audit = db["audit"]
    outbox = db["outbox"]
    module.ensure_platform_invoice_settlement_allocation_indexes(allocations, audit, outbox)
    invoices.insert_one({
        "tenant_id": tenant_id, "invoice_id": invoice_id, "currency": "ZAR",
        "status": "open", "amount_paid": 0.0, "outstanding_amount": 100.0,
        "total": 100.0, "release_amount_minor": 10000,
        "commercial_release_evidence_fingerprint": commercial_fingerprint,
        "settlement_allocation_revision": 0,
    })

    def add_observation(observation_id, amount_minor, offset_seconds):
        local_fact_id, local_reference = ensure_execution(observation_id, amount_minor)
        observation = SimpleNamespace(
            tenant_id=tenant_id, observation_id=observation_id,
            execution_truth_id=local_fact_id, provider_name="ELECTRUM",
            provider_execution_reference=local_reference,
            settlement_reference=f"settlement-{observation_id}",
            provider_settlement_evidence_reference=f"message-{observation_id}",
            currency="ZAR", payment_destination_reference=destination,
            settled_amount_minor=amount_minor, settled_at=now,
            observed_at=now, fingerprint=(str(offset_seconds % 10) * 128),
        )
        observations[observation_id] = observation
        return observation

    args = {
        "tenant_id": tenant_id,
        "observation_collection": db["observations"],
        "execution_truth_collection": db["execution_facts"],
        "platform_truth_collection": db["platform_truth"],
        "release_authorization_collection": db["release_authorizations"],
        "platform_invoice_collection": invoices,
        "allocation_collection": allocations,
        "audit_collection": audit,
        "outbox_collection": outbox,
        "subscription_collection": None,
        "allocated_at": now,
    }
    return module, args, add_observation, invoices, allocations, audit, outbox


def test_real_invoice_projection_partial_then_final_and_exact_replay(mongo_allocation_collection, monkeypatch):
    client, _, = mongo_allocation_collection
    db = client[f"invoice_allocation_e2e_{uuid4().hex}"]
    module, args, add_observation, invoices, allocations, audit, outbox = _real_invoice_orchestration_fixture(monkeypatch, db)
    try:
        add_observation("obs-partial", 4000, 1)
        with client.start_session() as session:
            with session.start_transaction():
                first = module.allocate_settlement_observation_to_platform_invoice(
                    "tenant-e2e", "obs-partial", **{**args, "session": session}
                )
        invoice = invoices.find_one({"tenant_id": "tenant-e2e", "invoice_id": "invoice-e2e"})
        assert first["allocation"].allocation_status == "PARTIAL"
        assert invoice["amount_paid"] == 40.0
        assert invoice["outstanding_amount"] == 60.0
        assert invoice["status"] == "open"
        assert invoice["settlement_state"] == "PARTIALLY_SETTLED"
        assert "paid_at" not in invoice

        with client.start_session() as session:
            with session.start_transaction():
                replay = module.allocate_settlement_observation_to_platform_invoice(
                    "tenant-e2e", "obs-partial", **{**args, "session": session}
                )
        assert replay["replayed"] is True
        assert allocations.count_documents({}) == 1

        add_observation("obs-final", 6000, 2)
        with client.start_session() as session:
            with session.start_transaction():
                final = module.allocate_settlement_observation_to_platform_invoice(
                    "tenant-e2e", "obs-final", **{**args, "session": session}
                )
        invoice = invoices.find_one({"tenant_id": "tenant-e2e", "invoice_id": "invoice-e2e"})
        assert final["allocation"].allocation_status == "FINAL"
        assert invoice["amount_paid"] == 100.0
        assert invoice["outstanding_amount"] == 0.0
        assert invoice["status"] == "paid"
        assert invoice["settlement_state"] == "SETTLED"
        assert invoice["paid_at"] is not None
        assert allocations.count_documents({}) == 2
        assert audit.count_documents({}) == 2
        assert outbox.count_documents({}) == 2
    finally:
        client.drop_database(db.name)


def test_real_invoice_allocation_interrupted_transaction_rolls_back_every_projection(mongo_allocation_collection, monkeypatch):
    client, _ = mongo_allocation_collection
    db = client[f"invoice_allocation_abort_{uuid4().hex}"]
    module, args, add_observation, invoices, allocations, audit, outbox = _real_invoice_orchestration_fixture(monkeypatch, db)
    try:
        add_observation("obs-abort", 4000, 3)
        with client.start_session() as session:
            with pytest.raises(RuntimeError, match="simulated interruption"):
                with session.start_transaction():
                    module.allocate_settlement_observation_to_platform_invoice(
                        "tenant-e2e", "obs-abort", **{**args, "session": session}
                    )
                    raise RuntimeError("simulated interruption")
        invoice = invoices.find_one({"tenant_id": "tenant-e2e", "invoice_id": "invoice-e2e"})
        assert invoice["amount_paid"] == 0.0
        assert invoice["outstanding_amount"] == 100.0
        assert invoice["status"] == "open"
        assert allocations.count_documents({}) == 0
        assert audit.count_documents({}) == 0
        assert outbox.count_documents({}) == 0
    finally:
        client.drop_database(db.name)
