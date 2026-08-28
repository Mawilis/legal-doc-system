"""Unit certification for pure asynchronous terminalization eligibility.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TERMINALIZATION-UNIT-CERT
TITLE: Financial Execution Terminalization Unit Certification
PURPOSE: Prove closed, correlated, immutable terminalization decisions.
AUTHORITY: Test evidence only; no persistence, transport, or settlement authority.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution_terminalization.py
CERTIFICATION DATE: 2026-08-28
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: fixed opaque references; no credentials or payloads.
TENANT BOUNDARY: deterministic fixtures use one explicit tenant per scenario.
FINANCIAL TRUTH BOUNDARY: tests prove policy does not create truth or settlement.
TRANSACTION BOUNDARY: no Mongo, sessions, transactions, clocks, or I/O.
FIXTURE POSTURE: fixed identities, references, timestamps, and lifecycle states.
CHANGELOG: v1.0.0 certifies the pure terminalization eligibility contract.
"""
from datetime import datetime, timezone
from typing import Any, cast

import pytest

from tools.eos.kennel.domain.financial_execution import FinancialExecutionStatus
from tools.eos.kennel.domain.financial_execution_execution_time_evidence import FinancialExecutionTimeEvidence, ExecutionTimeAuthorityKind
from tools.eos.kennel.domain.financial_execution_lifecycle import FinancialExecutionAttempt, FinancialExecutionAttemptState
from tools.eos.kennel.domain.financial_execution_provider_observation import EvidenceStrength, FinancialExecutionProviderObservation, ObservationStatus, TransportDisposition
from tools.eos.kennel.domain.financial_execution_terminalization import FinancialExecutionTerminalizationError, TerminalizationDecision, evaluate_terminalization

NOW = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)


def attempt(state: FinancialExecutionAttemptState) -> FinancialExecutionAttempt:
    """Build a fixed canonical attempt fixture."""
    return FinancialExecutionAttempt(
        execution_attempt_id="attempt-1",
        tenant_id="tenant-1",
        execution_command_id="command-1",
        provider_name="PAYSHAP",
        state=state,
        confirmed_at=NOW if state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED else None,
    )


def observation(status: ObservationStatus, *, strength: EvidenceStrength = EvidenceStrength.AUTHENTICATED, transport: TransportDisposition = TransportDisposition.RESPONSE_RECEIVED, execution_reference: str | None = "provider-execution-1", occurrence: datetime | None = None, observation_id: str = "observation-1") -> FinancialExecutionProviderObservation:
    """Build a fixed correlated provider observation fixture."""
    return FinancialExecutionProviderObservation(
        observation_id=observation_id,
        tenant_id="tenant-1",
        execution_attempt_id="attempt-1",
        provider_name="PAYSHAP",
        observation_status=status,
        observed_at=NOW,
        provider_execution_reference=execution_reference,
        provider_evidence_reference=f"evidence-{observation_id}",
        provider_occurred_at=occurrence,
        evidence_strength=strength,
        transport_disposition=transport,
    )


def execution_time(**changes: Any) -> FinancialExecutionTimeEvidence:
    """Build fixed explicit execution-time authority evidence."""
    values: dict[str, object] = {
        "tenant_id": "tenant-1",
        "execution_attempt_id": "attempt-1",
        "provider_name": "PAYSHAP",
        "provider_execution_reference": "provider-execution-1",
        "evidence_reference": "signed-receipt-1",
        "executed_at": NOW,
        "authority_kind": ExecutionTimeAuthorityKind.SIGNED_EXECUTION_RECEIPT,
        "evidence_strength": EvidenceStrength.AUTHENTICATED,
    }
    values.update(changes)
    return FinancialExecutionTimeEvidence(**cast(dict[str, Any], values))


@pytest.mark.parametrize("state", [FinancialExecutionAttemptState.PREPARED, FinancialExecutionAttemptState.TRANSMISSION_STARTED, FinancialExecutionAttemptState.TRANSMITTED, FinancialExecutionAttemptState.ACCEPTED, FinancialExecutionAttemptState.PENDING, FinancialExecutionAttemptState.AMBIGUOUS, FinancialExecutionAttemptState.CANCELLED])
def test_nonterminal_states_are_not_eligible(state: FinancialExecutionAttemptState) -> None:
    """Prove nonterminal and cancelled states cannot create final truth."""
    result = evaluate_terminalization(attempt(state), (observation(ObservationStatus.ACCEPTED),))
    assert result.decision is TerminalizationDecision.NOT_ELIGIBLE
    assert result.status is None


def test_confirmed_failed_requires_authoritative_non_ambiguous_evidence() -> None:
    """Prove confirmed failure maps only to FAILED with no execution time."""
    result = evaluate_terminalization(attempt(FinancialExecutionAttemptState.CONFIRMED_FAILED), (observation(ObservationStatus.FAILED, execution_reference=None),))
    assert result.decision is TerminalizationDecision.ELIGIBLE_FAILED
    assert result.status is FinancialExecutionStatus.FAILED
    assert result.executed_at is None


@pytest.mark.parametrize("kwargs, expected", [
    ({"strength": EvidenceStrength.UNAUTHENTICATED}, TerminalizationDecision.CONFLICT),
    ({"strength": EvidenceStrength.CONFLICTING}, TerminalizationDecision.CONFLICT),
    ({"transport": TransportDisposition.AMBIGUOUS}, TerminalizationDecision.CONFLICT),
])
def test_confirmed_failed_weak_or_ambiguous_evidence_fails_closed(kwargs: dict[str, Any], expected: TerminalizationDecision) -> None:
    """Prove weak, conflicting, and ambiguous failure evidence cannot finalize."""
    result = evaluate_terminalization(attempt(FinancialExecutionAttemptState.CONFIRMED_FAILED), (observation(ObservationStatus.FAILED, execution_reference=None, **kwargs),))
    assert result.decision is expected
    assert result.executed_at is None


def test_confirmed_executed_requires_explicit_time_authority() -> None:
    """Prove provider occurrence and observed timestamps are insufficient."""
    item = observation(ObservationStatus.EXECUTED, occurrence=NOW)
    result = evaluate_terminalization(attempt(FinancialExecutionAttemptState.CONFIRMED_EXECUTED), (item,))
    assert result.decision is TerminalizationDecision.RECONCILIATION_REQUIRED
    assert result.status is None


def test_confirmed_executed_uses_explicit_time_authority() -> None:
    """Prove lawful execution maps the explicit aware timestamp exactly."""
    result = evaluate_terminalization(attempt(FinancialExecutionAttemptState.CONFIRMED_EXECUTED), (observation(ObservationStatus.EXECUTED),), execution_time())
    assert result.decision is TerminalizationDecision.ELIGIBLE_EXECUTED
    assert result.status is FinancialExecutionStatus.EXECUTED
    assert result.executed_at == NOW


@pytest.mark.parametrize("changes", [{"tenant_id": "tenant-2"}, {"execution_attempt_id": "attempt-2"}, {"provider_name": "OTHER"}, {"provider_execution_reference": "other-reference"}])
def test_identity_correlation_mismatch_is_conflict(changes: dict[str, object]) -> None:
    """Prove observation and execution-time identities cannot cross boundaries."""
    item = observation(ObservationStatus.EXECUTED)
    if "tenant_id" in changes or "execution_attempt_id" in changes or "provider_name" in changes:
        item = FinancialExecutionProviderObservation(**cast(dict[str, Any], {**item.__dict__, **changes}))
        result = evaluate_terminalization(attempt(FinancialExecutionAttemptState.CONFIRMED_EXECUTED), (item,), execution_time())
    else:
        result = evaluate_terminalization(attempt(FinancialExecutionAttemptState.CONFIRMED_EXECUTED), (item,), execution_time(**changes))
    assert result.decision is TerminalizationDecision.CONFLICT


def test_conflicting_terminal_evidence_and_unknown_are_not_final() -> None:
    """Prove contradictory terminal evidence and UNKNOWN never become truth."""
    conflict = evaluate_terminalization(attempt(FinancialExecutionAttemptState.CONFIRMED_EXECUTED), (observation(ObservationStatus.EXECUTED), observation(ObservationStatus.FAILED, execution_reference=None, observation_id="observation-2")), execution_time())
    unknown = evaluate_terminalization(attempt(FinancialExecutionAttemptState.CONFIRMED_FAILED), (observation(ObservationStatus.UNKNOWN, execution_reference=None),))
    assert conflict.decision is TerminalizationDecision.CONFLICT
    assert unknown.decision is TerminalizationDecision.RECONCILIATION_REQUIRED


def test_arrival_order_and_fingerprint_are_deterministic() -> None:
    """Prove evidence ordering cannot own truth or audit identity."""
    first = observation(ObservationStatus.EXECUTED, observation_id="observation-a")
    second = observation(ObservationStatus.ACCEPTED, execution_reference=None, observation_id="observation-b")
    left = evaluate_terminalization(attempt(FinancialExecutionAttemptState.CONFIRMED_EXECUTED), (first, second), execution_time())
    right = evaluate_terminalization(attempt(FinancialExecutionAttemptState.CONFIRMED_EXECUTED), (second, first), execution_time())
    assert left.decision is right.decision is TerminalizationDecision.ELIGIBLE_EXECUTED
    assert left.fingerprint == right.fingerprint
    assert len(left.fingerprint) == 128
    assert all(character in "0123456789abcdef" for character in left.fingerprint)


def test_empty_and_malformed_inputs_fail_closed() -> None:
    """Prove absent evidence is not fabricated and malformed shapes raise domain errors."""
    empty = evaluate_terminalization(attempt(FinancialExecutionAttemptState.CONFIRMED_FAILED), ())
    assert empty.decision is TerminalizationDecision.RECONCILIATION_REQUIRED
    with pytest.raises(FinancialExecutionTerminalizationError):
        evaluate_terminalization(object(), ())  # type: ignore[arg-type]
    with pytest.raises(FinancialExecutionTerminalizationError):
        evaluate_terminalization(attempt(FinancialExecutionAttemptState.PREPARED), [])  # type: ignore[arg-type]


def test_decision_is_immutable_and_policy_has_no_truth_or_settlement_surface() -> None:
    """Prove value immutability and the intentionally narrow public policy surface."""
    result = evaluate_terminalization(attempt(FinancialExecutionAttemptState.CONFIRMED_FAILED), (observation(ObservationStatus.FAILED, execution_reference=None),))
    with pytest.raises(AttributeError):
        result.reason = "changed"  # type: ignore[misc]
    assert not hasattr(result, "settle")
    assert not hasattr(result, "create")
    assert "SETTLED" not in result.fingerprint


# ARTIFACT: test_financial_execution_terminalization.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TERMINALIZATION-UNIT-CERT
# AUTHORITY BOUNDARY: certification evidence only; no persistence or execution authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
