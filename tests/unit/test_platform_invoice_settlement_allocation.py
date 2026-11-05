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
