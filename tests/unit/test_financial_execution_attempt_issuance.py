"""Unit certification for canonical command-to-PREPARED-attempt issuance.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-ATTEMPT-ISSUANCE-UNIT-CERT
AUTHORITY: pure preparation evidence; no persistence or provider authority.
"""
from datetime import datetime, timezone

import pytest

from tools.eos.kennel.domain.financial_execution_command import FinancialExecutionCommand
from tools.eos.kennel.domain.financial_execution_lifecycle import FinancialExecutionAttemptState
from tools.eos.kennel.orchestration.financial_execution_attempt_issuance import (
    FinancialExecutionAttemptIssuance,
    issue_financial_execution_attempt,
)

NOW = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)


def command() -> FinancialExecutionCommand:
    return FinancialExecutionCommand("tenant-1", "payable-1", "release-1", "command-1", "idem-1", 1000, "ZAR", "destination-ref", NOW, "PAYSHAP", "metadata-ref")


def issuance(**changes: object) -> FinancialExecutionAttemptIssuance:
    values: dict[str, object] = {"execution_attempt_id": "attempt-1", "provider_name": "PAYSHAP", "created_at": NOW, "destination_fingerprint": "a" * 128, "request_evidence_reference": "request-evidence"}
    values.update(changes)
    return FinancialExecutionAttemptIssuance(**values)  # type: ignore[arg-type]


def test_constructs_prepared_attempt_with_command_lineage() -> None:
    attempt = issue_financial_execution_attempt(command(), issuance())
    assert attempt.state is FinancialExecutionAttemptState.PREPARED
    assert attempt.tenant_id == command().tenant_id
    assert attempt.execution_command_id == command().execution_command_id
    assert attempt.payment_destination_reference == command().payment_destination_reference
    assert attempt.request_fingerprint == command().fingerprint
    assert attempt.execution_attempt_id != attempt.execution_command_id


def test_provider_mismatch_and_identity_collision_fail_closed() -> None:
    with pytest.raises(ValueError):
        issue_financial_execution_attempt(command(), issuance(provider_name="ZAPPER"))
    with pytest.raises(ValueError):
        issue_financial_execution_attempt(command(), issuance(execution_attempt_id="command-1"))


def test_attempt_is_immutable_and_has_no_transport_evidence() -> None:
    attempt = issue_financial_execution_attempt(command(), issuance())
    with pytest.raises(AttributeError):
        attempt.state = FinancialExecutionAttemptState.TRANSMITTED  # type: ignore[misc]
    assert attempt.provider_request_reference is None
    assert attempt.provider_accepted_at is None
    assert attempt.transmitted_at is None


def test_invalid_inputs_are_rejected_without_side_effects() -> None:
    with pytest.raises(TypeError):
        issue_financial_execution_attempt(object(), issuance())  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        issue_financial_execution_attempt(command(), object())  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        issue_financial_execution_attempt(command(), issuance(created_at=datetime(2026, 8, 28, 12, 0)))


# ARTIFACT: test_financial_execution_attempt_issuance.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-ATTEMPT-ISSUANCE-UNIT-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
