"""Pure eligibility policy for asynchronous financial execution terminalization.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TERMINALIZATION
TITLE: Financial Execution Terminalization Eligibility
PURPOSE: Decide whether canonical attempt evidence may be mapped to final truth.
AUTHORITY: Pure domain policy; no persistence, transaction ownership, or transport.
EPITOME: Correlates immutable attempt, observations, and explicit execution time.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/financial_execution_terminalization.py
CERTIFICATION DATE: 2026-08-28
CHANGELOG: v1.0.0 establishes provider-neutral fail-closed terminalization eligibility.
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque references only; no credentials or provider payloads.
TENANT BOUNDARY: all evidence must match the canonical attempt tenant and identity.
FINANCIAL AUTHORITY BOUNDARY: does not create truth, settle, ledger, or execute.
TIME BOUNDARY: provider occurrence and observation time never substitute for executed_at.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .financial_execution_execution_time_evidence import FinancialExecutionTimeEvidence
from .financial_execution_lifecycle import (
    FinancialExecutionAttempt,
    FinancialExecutionAttemptState,
)
from .financial_execution_provider_observation import (
    EvidenceStrength,
    FinancialExecutionProviderObservation,
    ObservationStatus,
    TransportDisposition,
)
from .financial_execution import FinancialExecutionStatus

VERSION = "v1.0.0-KENNEL-FINANCIAL-EXECUTION-TERMINALIZATION"


class FinancialExecutionTerminalizationError(ValueError):
    """Fail-closed error for malformed terminalization inputs."""


class TerminalizationDecision(StrEnum):
    """Closed outcomes of the pure terminalization eligibility policy."""

    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"
    ELIGIBLE_FAILED = "ELIGIBLE_FAILED"
    ELIGIBLE_EXECUTED = "ELIGIBLE_EXECUTED"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class FinancialExecutionTerminalizationDecision:
    """Immutable mapping material for a future truth-writing bridge."""

    decision: TerminalizationDecision
    status: FinancialExecutionStatus | None
    executed_at: datetime | None
    evidence_references: tuple[str, ...]
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.decision, TerminalizationDecision) or not isinstance(self.reason, str) or not self.reason.strip():
            raise FinancialExecutionTerminalizationError("invalid terminalization decision")
        if self.decision is TerminalizationDecision.ELIGIBLE_FAILED:
            if self.status is not FinancialExecutionStatus.FAILED or self.executed_at is not None:
                raise FinancialExecutionTerminalizationError("failed mapping is invalid")
        if self.decision is TerminalizationDecision.ELIGIBLE_EXECUTED:
            if self.status is not FinancialExecutionStatus.EXECUTED or self.executed_at is None or self.executed_at.tzinfo is None:
                raise FinancialExecutionTerminalizationError("executed mapping is invalid")

    @property
    def fingerprint(self) -> str:
        """Return deterministic audit material for this decision only."""
        payload = {"decision": self.decision.value, "status": self.status.value if self.status else None, "executed_at": self.executed_at.isoformat() if self.executed_at else None, "evidence_references": self.evidence_references, "reason": self.reason}
        return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def evaluate_terminalization(
    attempt: FinancialExecutionAttempt,
    observations: tuple[FinancialExecutionProviderObservation, ...],
    execution_time: FinancialExecutionTimeEvidence | None = None,
) -> FinancialExecutionTerminalizationDecision:
    """Evaluate canonical evidence without creating or persisting financial truth."""
    if not isinstance(attempt, FinancialExecutionAttempt) or not isinstance(observations, tuple):
        raise FinancialExecutionTerminalizationError("invalid terminalization inputs")
    if any(not isinstance(item, FinancialExecutionProviderObservation) for item in observations):
        raise FinancialExecutionTerminalizationError("observations must be canonical objects")
    if execution_time is not None and not isinstance(execution_time, FinancialExecutionTimeEvidence):
        raise FinancialExecutionTerminalizationError("execution-time evidence is invalid")
    ordered = tuple(sorted(observations, key=lambda item: item.fingerprint))
    for item in ordered:
        if item.tenant_id != attempt.tenant_id or item.execution_attempt_id != attempt.execution_attempt_id or item.provider_name != attempt.provider_name:
            return _decision(TerminalizationDecision.CONFLICT, "evidence_identity_mismatch", ordered)
    terminal = tuple(item for item in ordered if item.observation_status in {ObservationStatus.EXECUTED, ObservationStatus.FAILED})
    statuses = {item.observation_status for item in terminal}
    if len(statuses) > 1 or any(item.evidence_strength in {EvidenceStrength.UNAUTHENTICATED, EvidenceStrength.CONFLICTING} or item.transport_disposition is TransportDisposition.AMBIGUOUS for item in terminal):
        return _decision(TerminalizationDecision.CONFLICT, "terminal_evidence_conflict", terminal)
    if attempt.state is FinancialExecutionAttemptState.CONFIRMED_FAILED:
        if len(terminal) == 1 and terminal[0].observation_status is ObservationStatus.FAILED and terminal[0].evidence_strength in {EvidenceStrength.AUTHENTICATED, EvidenceStrength.CORROBORATED}:
            return _decision(TerminalizationDecision.ELIGIBLE_FAILED, "authoritative_failure", terminal, FinancialExecutionStatus.FAILED)
        return _decision(TerminalizationDecision.RECONCILIATION_REQUIRED, "failure_evidence_insufficient", terminal)
    if attempt.state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED:
        if len(terminal) != 1 or terminal[0].observation_status is not ObservationStatus.EXECUTED or terminal[0].evidence_strength not in {EvidenceStrength.AUTHENTICATED, EvidenceStrength.CORROBORATED}:
            return _decision(TerminalizationDecision.RECONCILIATION_REQUIRED, "execution_evidence_insufficient", terminal)
        if execution_time is None:
            return _decision(TerminalizationDecision.RECONCILIATION_REQUIRED, "explicit_execution_time_required", terminal)
        item = terminal[0]
        if (execution_time.tenant_id != attempt.tenant_id or execution_time.execution_attempt_id != attempt.execution_attempt_id or execution_time.provider_name != attempt.provider_name or item.provider_execution_reference != execution_time.provider_execution_reference):
            return _decision(TerminalizationDecision.CONFLICT, "execution_time_identity_mismatch", terminal)
        return _decision(TerminalizationDecision.ELIGIBLE_EXECUTED, "explicit_execution_time_authority", terminal, FinancialExecutionStatus.EXECUTED, execution_time.executed_at)
    return _decision(TerminalizationDecision.NOT_ELIGIBLE, "attempt_not_terminal", terminal)


def _decision(decision: TerminalizationDecision, reason: str, observations: tuple[FinancialExecutionProviderObservation, ...], status: FinancialExecutionStatus | None = None, executed_at: datetime | None = None) -> FinancialExecutionTerminalizationDecision:
    """Build an immutable decision from deterministically ordered evidence."""
    return FinancialExecutionTerminalizationDecision(decision, status, executed_at, tuple(item.provider_evidence_reference or item.observation_id for item in observations), reason)


# ARTIFACT: financial_execution_terminalization.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TERMINALIZATION
# AUTHORITY BOUNDARY: eligibility only; no persistence, execution truth, or settlement.
# TENANT POSTURE: canonical attempt and evidence identities are fail-closed correlated.
# FAIL-CLOSED POSTURE: ambiguity, conflict, and missing authority cannot finalize.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution truth.
# END OF WILSY OS SOVEREIGN ARTIFACT
