from datetime import datetime, timezone

import pytest

from tools.eos.saas.domain.platform_invoice_settlement_allocation import (
    PlatformInvoiceSettlementAllocation,
    PlatformInvoiceSettlementAllocationError,
)


def allocation(**overrides):
    values = dict(
        tenant_id="tenant-a",
        allocation_id="allocation-1",
        observation_id="observation-1",
        observation_fingerprint="a" * 128,
        execution_truth_id="execution-1",
        invoice_id="invoice-1",
        invoice_evidence_fingerprint="b" * 128,
        currency="ZAR",
        amount_minor=4000,
        cumulative_paid_minor=4000,
        outstanding_minor=6000,
        allocation_sequence=1,
        allocated_at=datetime(2026, 11, 5, tzinfo=timezone.utc),
        allocation_status="PARTIAL",
    )
    values.update(overrides)
    return PlatformInvoiceSettlementAllocation(**values)


def test_partial_allocation_is_immutable_and_fingerprinted():
    value = allocation()
    assert value.fingerprint == allocation().fingerprint
    assert value.to_dict()["allocation_fingerprint"] == value.fingerprint
    assert PlatformInvoiceSettlementAllocation.from_dict(value.to_dict()) == value


def test_final_allocation_requires_zero_balance():
    assert allocation(outstanding_minor=0, cumulative_paid_minor=10000, allocation_status="FINAL")
    with pytest.raises(PlatformInvoiceSettlementAllocationError, match="FINALITY"):
        allocation(outstanding_minor=1, cumulative_paid_minor=9999, allocation_status="FINAL")


def test_overpayment_and_invalid_minor_units_rejected():
    with pytest.raises(PlatformInvoiceSettlementAllocationError):
        allocation(amount_minor=0)
    with pytest.raises(PlatformInvoiceSettlementAllocationError):
        allocation(outstanding_minor=-1)


def _orchestration_fixture(monkeypatch, *, paid_minor=0, amount_minor=4000):
    from types import SimpleNamespace
    from unittest.mock import Mock
    from tools.eos.saas.domain.billing import InvoiceStatus
    from tools.eos.kennel.domain.financial_execution import FinancialExecutionStatus
    from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformExecutionStatus
    import tools.eos.saas.billing.platform_invoice_settlement_allocation as module

    now = datetime(2026, 11, 5, tzinfo=timezone.utc)
    observation = SimpleNamespace(
        tenant_id="tenant-a", observation_id="observation-1",
        execution_truth_id="fact-1", provider_name="PAYSHAP",
        provider_execution_reference="provider-ref", currency="ZAR",
        payment_destination_reference="destination-1",
        settled_amount_minor=amount_minor, settled_at=now, fingerprint="a" * 128,
    )
    fact = SimpleNamespace(
        tenant_id="tenant-a", execution_fact_id="fact-1", fingerprint="b" * 128,
        execution_status=FinancialExecutionStatus.EXECUTED, provider="PAYSHAP",
        provider_execution_reference="provider-ref", currency="ZAR",
        payment_destination_reference="destination-1", executed_amount_minor=10000,
    )
    platform_truth = SimpleNamespace(
        execution_status=PlatformExecutionStatus.EXECUTED,
        source_execution_fact_id="fact-1", source_execution_fact_fingerprint="b" * 128,
        provider="PAYSHAP", provider_execution_reference="provider-ref",
        currency="ZAR", payment_destination_reference="destination-1",
        platform_invoice_id="invoice-1", release_authorization_id="release-1",
        release_authorization_fingerprint="d" * 128,
    )
    authorization = SimpleNamespace(
        tenant_id="tenant-a", platform_invoice_id="invoice-1", currency="ZAR",
        authorized_amount_minor=10000, platform_invoice_evidence_fingerprint="c" * 128,
        payment_destination_reference="destination-1",
        release_authorization_fingerprint="d" * 128,
    )
    invoice = SimpleNamespace(
        tenant_id="tenant-a", invoice_id="invoice-1", currency="ZAR",
        status=InvoiceStatus.OPEN, paid_at=None, amount_paid=paid_minor / 100,
        outstanding_amount=(10000 - paid_minor) / 100, release_amount_minor=10000,
        commercial_release_evidence_fingerprint="c" * 128,
    )
    invoice_doc = {
        "tenant_id": "tenant-a", "invoice_id": "invoice-1",
        "amount_paid": paid_minor / 100, "outstanding_amount": (10000 - paid_minor) / 100,
        "status": "open", "currency": "ZAR", "total": 100.0,
        "settlement_allocation_revision": 0 if paid_minor == 0 else 1,
    }
    observations = Mock()
    facts = Mock()
    platform_truths = Mock()
    platform_truths.find.return_value.limit.return_value = [{"execution_truth_id": "platform-truth-1"}]
    invoices = Mock()
    invoices.find_one.return_value = invoice_doc
    invoices.update_one.return_value.matched_count = 1
    allocations = Mock()
    allocations.find_one.return_value = None
    allocations.find.return_value = []
    allocations.count_documents.return_value = 0 if paid_minor == 0 else 1
    audit = Mock()
    audit.find_one.return_value = None
    outbox = Mock()
    outbox.find_one.return_value = None
    monkeypatch.setattr(module.FinancialSettlementObservationRegistry, "get", lambda *a, **k: observation)
    monkeypatch.setattr(module.FinancialExecutionFactRegistry, "get", lambda *a, **k: fact)
    monkeypatch.setattr(module.PlatformBillingFinancialExecutionTruthRegistry, "get", lambda *a, **k: platform_truth)
    monkeypatch.setattr(module.PlatformBillingReleaseAuthorizationRegistry, "get", lambda *a, **k: authorization)
    monkeypatch.setattr(module.PlatformInvoice, "from_dict", lambda doc: invoice)
    monkeypatch.setattr(module, "to_minor_units", lambda value, currency: int(round(value * 100)))
    args = dict(
        tenant_id="tenant-a", observation_id="observation-1",
        observation_collection=observations, execution_truth_collection=facts,
        platform_truth_collection=platform_truths, release_authorization_collection=Mock(),
        platform_invoice_collection=invoices, allocation_collection=allocations,
        audit_collection=audit, outbox_collection=outbox, subscription_collection=None,
        session=Mock(in_transaction=True), allocated_at=now,
    )
    return module, args, invoices, allocations, audit, outbox


def test_partial_allocation_updates_balance_without_marking_invoice_paid(monkeypatch):
    module, args, invoices, allocations, audit, outbox = _orchestration_fixture(monkeypatch)
    result = module.allocate_settlement_observation_to_platform_invoice(**args)
    update = invoices.update_one.call_args.args[1]["$set"]
    assert result["allocation"].allocation_status == "PARTIAL"
    assert update["amount_paid"] == 40.0
    assert update["outstanding_amount"] == 60.0
    assert update["status"] == "open"
    assert update["settlement_state"] == "PARTIALLY_SETTLED"
    assert "paid_at" not in update
    audit.insert_one.assert_called_once()
    outbox.insert_one.assert_called_once()


def test_final_allocation_marks_invoice_paid_only_when_balance_reaches_zero(monkeypatch):
    module, args, invoices, allocations, audit, outbox = _orchestration_fixture(
        monkeypatch, paid_minor=4000, amount_minor=6000
    )
    result = module.allocate_settlement_observation_to_platform_invoice(**args)
    update = invoices.update_one.call_args.args[1]["$set"]
    assert result["allocation"].allocation_status == "FINAL"
    assert update["status"] == "paid"
    assert update["amount_paid"] == 100.0
    assert update["outstanding_amount"] == 0.0
    assert update["settlement_state"] == "SETTLED"
    assert update["paid_at"] == args["allocated_at"]
