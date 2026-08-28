# -*- coding: utf-8 -*-
"""Wilsy OS pure provider-observation to attempt policy authority.

VERSION: v1.0.0-KENNEL-FINANCIAL-OBSERVATION-POLICY
AUTHORITY: deterministic policy only; persistence and truth remain separate.
EPITOME: Correlates immutable attempt and observation evidence without mutation.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/financial_execution_observation_policy.py
COLLABORATION: Wilson Khanyezi (Founder); Codex (AI Engineering)
DATE: 2026-08-28 | COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque references only; no payloads, credentials, or network.
TENANT / TRUTH BOUNDARY: exact tenant correlation; no execution truth or settlement.
CHANGELOG: v1.0.0 establishes fail-closed transport, evidence, identity, and timestamp policy.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from .financial_execution_lifecycle import (
    FinancialExecutionAttempt,
    FinancialExecutionAttemptState,
    FinancialExecutionLifecycleError,
)
from .financial_execution_provider_observation import (
    FinancialExecutionProviderObservation,
    ObservationStatus,
    TransportDisposition,
    EvidenceStrength,
)

VERSION = "v1.0.0-KENNEL-FINANCIAL-OBSERVATION-POLICY"


class ObservationPolicyAction(StrEnum):
    NO_OP = "NO_OP"
    ADVANCE = "ADVANCE"
    REJECT = "REJECT"
    AMBIGUOUS = "AMBIGUOUS"
    CONFLICT = "CONFLICT"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"


@dataclass(frozen=True)
class FinancialExecutionObservationDecision:
    """Immutable proposal; applying it is owned by a separate transaction authority."""

    action: ObservationPolicyAction
    current_state: FinancialExecutionAttemptState
    proposed_state: FinancialExecutionAttemptState
    reason: str
    reconciliation_required: bool
    truth_eligible: bool
    conflict: bool
    observation_id: str
    attempt_id: str


def evaluate_provider_observation(
    attempt: FinancialExecutionAttempt,
    observation: FinancialExecutionProviderObservation,
) -> FinancialExecutionObservationDecision:
    """Evaluate one correlated observation without clocks, I/O, mutation, or persistence."""
    if not isinstance(attempt, FinancialExecutionAttempt) or not isinstance(
        observation, FinancialExecutionProviderObservation
    ):
        raise TypeError("attempt and observation are required")
    ids_match = (
        attempt.tenant_id == observation.tenant_id
        and attempt.execution_attempt_id == observation.execution_attempt_id
        and attempt.provider_name == observation.provider_name
    )
    if not ids_match:
        return _decision(
            attempt,
            observation,
            ObservationPolicyAction.REJECT,
            attempt.state,
            "IDENTITY_MISMATCH",
            True,
            False,
            True,
        )
    if (
        observation.transport_disposition is TransportDisposition.AMBIGUOUS
        or observation.evidence_strength is EvidenceStrength.CONFLICTING
    ):
        return _decision(
            attempt,
            observation,
            ObservationPolicyAction.AMBIGUOUS,
            FinancialExecutionAttemptState.AMBIGUOUS,
            "EVIDENCE_AMBIGUOUS",
            True,
            False,
            observation.evidence_strength is EvidenceStrength.CONFLICTING,
        )
    if observation.transport_disposition is TransportDisposition.NOT_SENT:
        return _decision(
            attempt,
            observation,
            ObservationPolicyAction.NO_OP,
            attempt.state,
            "NOT_SENT",
            False,
            False,
            False,
        )
    target = _target_state(observation)
    if target is None:
        return _decision(
            attempt,
            observation,
            ObservationPolicyAction.RECONCILIATION_REQUIRED,
            attempt.state,
            "UNKNOWN_OR_UNSAFE_EVIDENCE",
            True,
            False,
            False,
        )
    if observation.observation_status is ObservationStatus.EXECUTED:
        if (
            observation.evidence_strength
            not in {EvidenceStrength.AUTHENTICATED, EvidenceStrength.CORROBORATED}
            or observation.provider_occurred_at is None
        ):
            return _decision(
                attempt,
                observation,
                ObservationPolicyAction.RECONCILIATION_REQUIRED,
                FinancialExecutionAttemptState.AMBIGUOUS,
                "EXECUTION_TIMESTAMP_EVIDENCE_REQUIRED",
                True,
                False,
                False,
            )
    if attempt.is_final:
        if target is attempt.state:
            return _decision(
                attempt,
                observation,
                ObservationPolicyAction.NO_OP,
                attempt.state,
                "TERMINAL_REPLAY",
                False,
                False,
                False,
            )
        return _decision(
            attempt,
            observation,
            ObservationPolicyAction.CONFLICT,
            FinancialExecutionAttemptState.AMBIGUOUS,
            "TERMINAL_CONFLICT",
            True,
            False,
            True,
        )
    try:
        attempt.transition_to(
            target,
            evidence_reference=observation.provider_evidence_reference,
            confirmed_at=observation.provider_occurred_at
            if target is FinancialExecutionAttemptState.CONFIRMED_EXECUTED
            else None,
        )
    except FinancialExecutionLifecycleError:
        return _decision(
            attempt,
            observation,
            ObservationPolicyAction.REJECT,
            attempt.state,
            "ILLEGAL_LIFECYCLE_TRANSITION",
            True,
            False,
            True,
        )
    return _decision(
        attempt,
        observation,
        ObservationPolicyAction.ADVANCE,
        target,
        "LAWFUL_OBSERVATION",
        False,
        target is FinancialExecutionAttemptState.CONFIRMED_FAILED,
        False,
    )


def _target_state(
    observation: FinancialExecutionProviderObservation,
) -> FinancialExecutionAttemptState | None:
    if (
        observation.observation_status is ObservationStatus.INITIATED
        and observation.transport_disposition is TransportDisposition.SEND_STARTED
    ):
        return FinancialExecutionAttemptState.TRANSMISSION_STARTED
    if (
        observation.observation_status is ObservationStatus.ACCEPTED
        and observation.transport_disposition
        in {TransportDisposition.SENT, TransportDisposition.RESPONSE_RECEIVED}
    ):
        return FinancialExecutionAttemptState.ACCEPTED
    if (
        observation.observation_status is ObservationStatus.PENDING
        and observation.transport_disposition is TransportDisposition.RESPONSE_RECEIVED
    ):
        return FinancialExecutionAttemptState.PENDING
    if (
        observation.observation_status is ObservationStatus.FAILED
        and observation.evidence_strength is EvidenceStrength.AUTHENTICATED
    ):
        return FinancialExecutionAttemptState.CONFIRMED_FAILED
    if (
        observation.observation_status is ObservationStatus.CANCELLED
        and observation.evidence_strength is EvidenceStrength.AUTHENTICATED
    ):
        return FinancialExecutionAttemptState.CANCELLED
    return None


def _decision(
    attempt: FinancialExecutionAttempt,
    observation: FinancialExecutionProviderObservation,
    action: ObservationPolicyAction,
    proposed: FinancialExecutionAttemptState,
    reason: str,
    reconcile: bool,
    truth: bool,
    conflict: bool,
) -> FinancialExecutionObservationDecision:
    return FinancialExecutionObservationDecision(
        action,
        attempt.state,
        proposed,
        reason,
        reconcile,
        truth,
        conflict,
        observation.observation_id,
        observation.execution_attempt_id,
    )


# ARTIFACT: financial_execution_observation_policy.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-OBSERVATION-POLICY
# AUTHORITY BOUNDARY: pure proposal only; no persistence, execution truth, or settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
