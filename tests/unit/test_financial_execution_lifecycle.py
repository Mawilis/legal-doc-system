"""WILSY OS Kennel EOS lifecycle contract certification.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-LIFECYCLE-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Unit certification for immutable asynchronous execution attempts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution_lifecycle.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
CHANGELOG: v1.0.0 certifies validation, transitions, reconciliation gates, and confidentiality boundaries.
COMPLIANCE: POPIA §19 | GDPR Art. 32 | SOC2 CC7.2
FINANCIAL AUTHORITY: Kennel EOS exclusively owns execution truth; execution is not settlement.
"""
from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.kennel.domain.financial_execution_lifecycle import (
    ExecutionReconciliationDecision,
    ExecutionReconciliationOutcome,
    FinancialExecutionAttempt,
    FinancialExecutionAttemptState,
    FinancialExecutionFinalization,
    FinancialExecutionLifecycleError,
)


NOW = datetime(2026, 8, 28, 12, tzinfo=timezone.utc)


def attempt(**changes: object) -> FinancialExecutionAttempt:
    values: dict[str, Any] = {
        "execution_attempt_id": "attempt-1",
        "tenant_id": "tenant-1",
        "execution_command_id": "command-1",
        "provider_name": "PAYSHAP",
        "created_at": NOW,
    }
    values.update(changes)
    return FinancialExecutionAttempt(**values)


def decision(outcome: ExecutionReconciliationOutcome, **changes: object) -> ExecutionReconciliationDecision:
    values: dict[str, Any] = {"outcome": outcome, "evidence_reference": "evidence-1"}
    values.update(changes)
    return ExecutionReconciliationDecision(**values)


def test_prepared_attempt_is_retryable_and_not_final() -> None:
    value = attempt()
    assert value.state is FinancialExecutionAttemptState.PREPARED
    assert value.may_retry is True
    assert value.is_final is False


@pytest.mark.parametrize("state", list(FinancialExecutionAttemptState))
def test_state_serialization_is_safe_and_deterministic(state: FinancialExecutionAttemptState) -> None:
    value = attempt(state=state, confirmed_at=NOW if state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED else None)
    assert value.to_dict()["state"] == state.value
    assert len(value.fingerprint) == 128
    assert value.fingerprint == value.fingerprint.lower()


@pytest.mark.parametrize("state", [FinancialExecutionAttemptState.TRANSMISSION_STARTED, FinancialExecutionAttemptState.TRANSMITTED, FinancialExecutionAttemptState.AMBIGUOUS, FinancialExecutionAttemptState.CONFIRMED_FAILED])
def test_prepared_transitions(state: FinancialExecutionAttemptState) -> None:
    value = attempt().transition_to(state, evidence_reference="provider-evidence" if state is FinancialExecutionAttemptState.CONFIRMED_FAILED else None)
    assert value.state is state
    assert value is not attempt()


def test_monotonic_pending_to_execution_requires_evidence_and_timestamp() -> None:
    pending = attempt(state=FinancialExecutionAttemptState.PENDING).transition_to(FinancialExecutionAttemptState.CONFIRMED_EXECUTED, evidence_reference="evidence-2", confirmed_at=NOW)
    assert pending.is_final is True
    assert pending.may_retry is False


def test_ambiguous_delivery_is_not_retryable() -> None:
    value = attempt(state=FinancialExecutionAttemptState.AMBIGUOUS)
    assert value.may_retry is False
    assert value.is_final is False


@pytest.mark.parametrize("state", [FinancialExecutionAttemptState.PREPARED, FinancialExecutionAttemptState.TRANSMITTED, FinancialExecutionAttemptState.PENDING, FinancialExecutionAttemptState.AMBIGUOUS])
def test_final_transition_requires_evidence(state: FinancialExecutionAttemptState) -> None:
    with pytest.raises(FinancialExecutionLifecycleError):
        attempt(state=state).transition_to(FinancialExecutionAttemptState.CONFIRMED_FAILED)


def test_illegal_reversal_is_rejected() -> None:
    value = attempt(state=FinancialExecutionAttemptState.TRANSMITTED)
    with pytest.raises(FinancialExecutionLifecycleError):
        value.transition_to(FinancialExecutionAttemptState.PREPARED)


def test_same_state_replay_is_idempotent() -> None:
    value = attempt(state=FinancialExecutionAttemptState.PENDING, latest_provider_evidence_reference="evidence-1")
    assert value.transition_to(FinancialExecutionAttemptState.PENDING) is value
    with pytest.raises(FinancialExecutionLifecycleError):
        value.transition_to(FinancialExecutionAttemptState.PENDING, evidence_reference="different")


@pytest.mark.parametrize("outcome", [ExecutionReconciliationOutcome.UNKNOWN, ExecutionReconciliationOutcome.STILL_PENDING, ExecutionReconciliationOutcome.CONFLICT])
def test_nonfinal_reconciliation_cannot_finalize(outcome: ExecutionReconciliationOutcome) -> None:
    with pytest.raises(FinancialExecutionLifecycleError):
        attempt().finalize(decision(outcome))


def test_confirmed_failure_finalizes_without_execution_timestamp() -> None:
    result = attempt().finalize(decision(ExecutionReconciliationOutcome.CONFIRMED_FAILED))
    assert isinstance(result, FinancialExecutionFinalization)
    assert result.outcome is ExecutionReconciliationOutcome.CONFIRMED_FAILED
    assert result.confirmed_at is None


def test_confirmed_execution_requires_reliable_timestamp() -> None:
    with pytest.raises(FinancialExecutionLifecycleError):
        attempt().finalize(decision(ExecutionReconciliationOutcome.CONFIRMED_EXECUTED))
    result = attempt().finalize(decision(ExecutionReconciliationOutcome.CONFIRMED_EXECUTED, confirmed_at=NOW))
    assert result.confirmed_at == NOW


@pytest.mark.parametrize("field", ["execution_attempt_id", "tenant_id", "execution_command_id", "provider_name"])
def test_identity_fields_are_required(field: str) -> None:
    with pytest.raises(FinancialExecutionLifecycleError):
        attempt(**{field: ""})


def test_attempt_and_command_identity_must_differ() -> None:
    with pytest.raises(FinancialExecutionLifecycleError):
        attempt(execution_command_id="attempt-1")


def test_sensitive_or_settlement_fields_are_not_in_serialized_surface() -> None:
    value = attempt()
    serialized = value.to_dict()
    assert not {"bank_account", "card_number", "credentials", "paid", "settled", "settlement_id"}.intersection(serialized)
    assert "payment_destination_reference" in serialized


@pytest.mark.parametrize("outcome", list(ExecutionReconciliationOutcome))
def test_decision_outcomes_are_closed_vocabulary(outcome: ExecutionReconciliationOutcome) -> None:
    value = decision(outcome)
    assert value.outcome is outcome


def test_decision_requires_evidence_reference() -> None:
    with pytest.raises(FinancialExecutionLifecycleError):
        ExecutionReconciliationDecision(ExecutionReconciliationOutcome.UNKNOWN, "")


def test_naive_confirmation_time_is_rejected() -> None:
    with pytest.raises(FinancialExecutionLifecycleError):
        decision(ExecutionReconciliationOutcome.CONFIRMED_EXECUTED, confirmed_at=datetime(2026, 8, 28))


def test_finalization_preserves_tenant_and_command_binding() -> None:
    result = attempt().finalize(decision(ExecutionReconciliationOutcome.CONFIRMED_FAILED))
    assert (result.tenant_id, result.execution_command_id) == ("tenant-1", "command-1")


# ARTIFACT: test_financial_execution_lifecycle.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-LIFECYCLE-UNIT-CERT
# AUTHORITY BOUNDARY: tests certify attempt evidence and finalization gates only.
# TENANT POSTURE: tenant and command identities remain immutable and explicit.
# FAIL-CLOSED POSTURE: ambiguous outcomes cannot finalize and malformed input is rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; execution is not settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
