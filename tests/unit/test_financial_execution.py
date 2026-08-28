from datetime import datetime, timezone

import pytest

from tools.eos.kennel.domain.financial_execution import (
    FinancialExecutionStatus,
    FinancialExecutionTruth,
    FinancialExecutionTruthError,
)


def truth(status: FinancialExecutionStatus, executed_at: datetime | None = None) -> FinancialExecutionTruth:
    now = datetime(2026, 1, 2, tzinfo=timezone.utc)
    return FinancialExecutionTruth(
        "truth-1", "tenant-1", "payable-1", "release-1", "PAYSHAP", "provider-1", status,
        100, "ZAR", executed_at, "destination-1", "evidence-1", "a" * 128, "b" * 128, now,
    )


def test_executed_requires_aware_timestamp_and_is_deterministic() -> None:
    at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    item = truth(FinancialExecutionStatus.EXECUTED, at)
    assert item.to_dict()["executed_at"] == at.isoformat()
    assert item.evidence_fingerprint == item.evidence_fingerprint


@pytest.mark.parametrize("status", [FinancialExecutionStatus.SUBMITTED, FinancialExecutionStatus.ACCEPTED, FinancialExecutionStatus.FAILED])
def test_non_executed_statuses_omit_execution_timestamp(status: FinancialExecutionStatus) -> None:
    item = truth(status)
    assert item.executed_at is None
    assert "executed_at" in item.to_dict()
    assert item.to_dict()["executed_at"] is None


def test_invalid_timestamp_combinations_rejected() -> None:
    with pytest.raises(FinancialExecutionTruthError):
        truth(FinancialExecutionStatus.EXECUTED)
    with pytest.raises(FinancialExecutionTruthError):
        truth(FinancialExecutionStatus.EXECUTED, datetime(2026, 1, 1))
    with pytest.raises(FinancialExecutionTruthError):
        truth(FinancialExecutionStatus.FAILED, datetime(2026, 1, 1, tzinfo=timezone.utc))


def test_round_trip_executed_and_failed() -> None:
    executed = truth(FinancialExecutionStatus.EXECUTED, datetime(2026, 1, 1, tzinfo=timezone.utc))
    failed = truth(FinancialExecutionStatus.FAILED)
    assert FinancialExecutionTruth.from_mapping(executed.to_dict()) == executed
    assert FinancialExecutionTruth.from_mapping(failed.to_dict()) == failed


def test_material_truth_changes_fingerprint_and_no_settlement_status() -> None:
    executed = truth(FinancialExecutionStatus.EXECUTED, datetime(2026, 1, 1, tzinfo=timezone.utc))
    failed = truth(FinancialExecutionStatus.FAILED)
    assert executed.evidence_fingerprint != failed.evidence_fingerprint
    assert {status.value for status in FinancialExecutionStatus} == {"SUBMITTED", "ACCEPTED", "EXECUTED", "FAILED"}
