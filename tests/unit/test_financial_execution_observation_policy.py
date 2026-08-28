# -*- coding: utf-8 -*-
"""Unit certification for pure provider-observation policy.

VERSION: v1.0.0-KENNEL-FINANCIAL-OBSERVATION-POLICY-UNIT-CERT
CHANGELOG: v1.0.0 certifies identity, transport, evidence, lifecycle, and timestamp gates.
"""
from datetime import datetime, timezone
from typing import Any, cast
import pytest
from tools.eos.kennel.domain.financial_execution_lifecycle import (
    FinancialExecutionAttempt,
    FinancialExecutionAttemptState,
)
from tools.eos.kennel.domain.financial_execution_provider_observation import (
    FinancialExecutionProviderObservation,
    ObservationStatus,
    TransportDisposition,
    EvidenceStrength,
)
from tools.eos.kennel.domain.financial_execution_observation_policy import (
    ObservationPolicyAction,
    evaluate_provider_observation,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def attempt(state=FinancialExecutionAttemptState.PREPARED):
    return FinancialExecutionAttempt("a", "t", "c", "P", state=state)


def observation(status: ObservationStatus = ObservationStatus.PENDING, **kw: Any):
    values = {
        "observation_id": "o",
        "tenant_id": "t",
        "execution_attempt_id": "a",
        "provider_name": "P",
    }
    values.update(kw)
    constructor: Any = FinancialExecutionProviderObservation
    return constructor(
        values.pop("observation_id"),
        values.pop("tenant_id"),
        values.pop("execution_attempt_id"),
        values.pop("provider_name"),
        status,
        NOW,
        **values,
    )


def test_identity_and_purity():
    a = attempt(FinancialExecutionAttemptState.TRANSMITTED)
    o = observation()
    before = a.to_dict()
    d = evaluate_provider_observation(a, o)
    assert d.action is ObservationPolicyAction.ADVANCE and a.to_dict() == before
    assert d == evaluate_provider_observation(a, o)


@pytest.mark.parametrize(
    "field", ["tenant_id", "execution_attempt_id", "provider_name"]
)
def test_identity_mismatch_rejects(field):
    values = {"tenant_id": "x", "execution_attempt_id": "x", "provider_name": "X"}
    assert (
        evaluate_provider_observation(
            attempt(), observation(**cast(Any, {field: values[field]}))
        ).action
        is ObservationPolicyAction.REJECT
    )


@pytest.mark.parametrize(
    "status",
    [
        ObservationStatus.REQUESTED,
        ObservationStatus.UNKNOWN,
        ObservationStatus.CONFLICT,
    ],
)
def test_unsafe_status_reconciles(status):
    assert (
        evaluate_provider_observation(attempt(), observation(status)).action
        is ObservationPolicyAction.RECONCILIATION_REQUIRED
    )


def test_not_sent_noop():
    d = evaluate_provider_observation(
        attempt(),
        observation(
            ObservationStatus.ACCEPTED,
            transport_disposition=TransportDisposition.NOT_SENT,
        ),
    )
    assert d.action is ObservationPolicyAction.NO_OP


def test_send_started_advances():
    d = evaluate_provider_observation(
        attempt(),
        observation(
            ObservationStatus.INITIATED,
            transport_disposition=TransportDisposition.SEND_STARTED,
        ),
    )
    assert d.proposed_state is FinancialExecutionAttemptState.TRANSMISSION_STARTED


def test_sent_acceptance():
    d = evaluate_provider_observation(
        attempt(FinancialExecutionAttemptState.TRANSMITTED),
        observation(
            ObservationStatus.ACCEPTED, transport_disposition=TransportDisposition.SENT
        ),
    )
    assert d.proposed_state is FinancialExecutionAttemptState.ACCEPTED


def test_pending_only():
    d = evaluate_provider_observation(
        attempt(FinancialExecutionAttemptState.ACCEPTED), observation()
    )
    assert d.proposed_state is FinancialExecutionAttemptState.PENDING


@pytest.mark.parametrize(
    "strength", [EvidenceStrength.UNAUTHENTICATED, EvidenceStrength.CORROBORATED]
)
def test_executed_without_timestamp_never_terminal(strength):
    d = evaluate_provider_observation(
        attempt(FinancialExecutionAttemptState.PENDING),
        observation(ObservationStatus.EXECUTED, evidence_strength=strength),
    )
    assert d.proposed_state is not FinancialExecutionAttemptState.CONFIRMED_EXECUTED


def test_authenticated_executed_still_requires_execution_timestamp():
    d = evaluate_provider_observation(
        attempt(FinancialExecutionAttemptState.PENDING),
        observation(
            ObservationStatus.EXECUTED, evidence_strength=EvidenceStrength.AUTHENTICATED
        ),
    )
    assert d.action is ObservationPolicyAction.RECONCILIATION_REQUIRED


def test_authenticated_failed_can_finalize():
    d = evaluate_provider_observation(
        attempt(FinancialExecutionAttemptState.PENDING),
        observation(
            ObservationStatus.FAILED,
            evidence_strength=EvidenceStrength.AUTHENTICATED,
            provider_evidence_reference="e",
        ),
    )
    assert d.proposed_state is FinancialExecutionAttemptState.CONFIRMED_FAILED


def test_failed_has_no_execution_time():
    d = evaluate_provider_observation(
        attempt(FinancialExecutionAttemptState.PENDING),
        observation(
            ObservationStatus.FAILED,
            evidence_strength=EvidenceStrength.AUTHENTICATED,
            provider_evidence_reference="e",
        ),
    )
    assert d.truth_eligible and not d.reconciliation_required


def test_conflicting_and_ambiguous_never_terminal():
    for o in (
        observation(evidence_strength=EvidenceStrength.CONFLICTING),
        observation(transport_disposition=TransportDisposition.AMBIGUOUS),
    ):
        assert (
            evaluate_provider_observation(attempt(), o).action
            is ObservationPolicyAction.AMBIGUOUS
        )


@pytest.mark.parametrize(
    "state",
    [
        FinancialExecutionAttemptState.CONFIRMED_EXECUTED,
        FinancialExecutionAttemptState.CONFIRMED_FAILED,
        FinancialExecutionAttemptState.CANCELLED,
    ],
)
def test_terminal_late_observation_conflicts(state):
    if state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED:
        target = FinancialExecutionAttempt(
            "a", "t", "c", "P", state=state, confirmed_at=NOW
        )
    else:
        target = attempt(state)
    d = evaluate_provider_observation(target, observation())
    assert d.action in {ObservationPolicyAction.CONFLICT, ObservationPolicyAction.NO_OP}


def test_unknown_never_failure_or_execution():
    d = evaluate_provider_observation(attempt(), observation(ObservationStatus.UNKNOWN))
    assert d.proposed_state not in {
        FinancialExecutionAttemptState.CONFIRMED_FAILED,
        FinancialExecutionAttemptState.CONFIRMED_EXECUTED,
    }


def test_cancelled_requires_lifecycle_edge():
    d = evaluate_provider_observation(
        attempt(),
        observation(
            ObservationStatus.CANCELLED,
            evidence_strength=EvidenceStrength.AUTHENTICATED,
        ),
    )
    assert d.action is ObservationPolicyAction.REJECT


def test_accepted_not_executed():
    d = evaluate_provider_observation(
        attempt(FinancialExecutionAttemptState.TRANSMITTED),
        observation(ObservationStatus.ACCEPTED),
    )
    assert d.proposed_state is not FinancialExecutionAttemptState.CONFIRMED_EXECUTED


def test_settled_absent():
    assert "SETTLED" not in {s.value for s in FinancialExecutionAttemptState}


def test_no_truth_or_registry_dependency():
    assert not hasattr(evaluate_provider_observation(attempt(), observation()), "truth")


@pytest.mark.parametrize(
    "status",
    [ObservationStatus.PENDING, ObservationStatus.ACCEPTED, ObservationStatus.FAILED],
)
def test_repeated_semantic_observation_deterministic(status):
    o = observation(
        status,
        evidence_strength=EvidenceStrength.AUTHENTICATED
        if status is ObservationStatus.FAILED
        else EvidenceStrength.UNAUTHENTICATED,
    )
    assert evaluate_provider_observation(attempt(), o) == evaluate_provider_observation(
        attempt(), o
    )


def test_observation_input_unchanged():
    o = observation()
    before = o.to_dict()
    evaluate_provider_observation(attempt(), o)
    assert o.to_dict() == before


def test_illegal_transition_rejects():
    d = evaluate_provider_observation(
        attempt(FinancialExecutionAttemptState.TRANSMISSION_STARTED),
        observation(ObservationStatus.PENDING),
    )
    assert d.action is ObservationPolicyAction.REJECT


def test_provider_occurrence_not_execution_time():
    d = evaluate_provider_observation(
        attempt(FinancialExecutionAttemptState.PENDING),
        observation(
            ObservationStatus.EXECUTED,
            evidence_strength=EvidenceStrength.AUTHENTICATED,
            provider_occurred_at=NOW,
        ),
    )
    assert d.proposed_state is not FinancialExecutionAttemptState.CONFIRMED_EXECUTED


# ARTIFACT: test_financial_execution_observation_policy.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-OBSERVATION-POLICY-UNIT-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
