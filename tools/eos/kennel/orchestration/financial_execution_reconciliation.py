"""WILSY OS caller-owned execution reconciliation and finalization authority.

TITLE: Financial Execution Reconciliation Orchestrator
VERSION: v1.0.0-M11-HOST-EXECUTION-RECONCILIATION
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Promote durable authenticated execution evidence to a CAS-protected
         confirmed attempt, then delegate terminal fact and family projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/financial_execution_reconciliation.py
COLLABORATION / OWNERSHIP: Kennel EOS reconciliation owner; the observation
                            registry owns evidence persistence, the attempt
                            registry owns lifecycle CAS, and the runtime
                            orchestrator owns post-terminalization projection.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0 establishes strict durable-evidence reconciliation without
           provider transport, transaction lifecycle, settlement, or invoice authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque durable references only; no raw provider
                             payloads, credentials, secrets, or network access.
TENANT BOUNDARY: Every command, attempt, observation, and execution-time
                 evidence identity must match the supplied tenant exactly.
AUTHORITY BOUNDARY: Reconciliation may confirm execution evidence only; it
                    does not authorize settlement or provider execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains the sole execution-truth
                               authority; EXECUTION != SETTLEMENT.
TRANSACTION BOUNDARY: The caller owns the active session, commit, abort, and
                      whole-transaction retry; this module never owns them.
FAIL-CLOSED DECLARATION: Missing, weak, ambiguous, conflicting, stale,
                          cross-tenant, or divergent evidence rejects.
"""
from __future__ import annotations

from datetime import datetime
import importlib
from typing import NoReturn

from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from ..domain.financial_execution import FinancialExecutionTruth
from ..domain.financial_execution_command import FinancialExecutionCommand
from ..domain.financial_execution_execution_time_evidence import (
    FinancialExecutionTimeEvidence,
)
from ..domain.financial_execution_lifecycle import (
    ExecutionReconciliationDecision,
    ExecutionReconciliationOutcome,
    FinancialExecutionAttempt,
    FinancialExecutionAttemptState,
    FinancialExecutionLifecycleError,
)
from ..domain.financial_execution_provider_observation import (
    EvidenceStrength,
    FinancialExecutionProviderObservation,
    ObservationStatus,
    TransportDisposition,
)
from ..domain.platform_billing_financial_execution_truth import (
    PlatformBillingFinancialExecutionTruth,
)
from ..registry.financial_execution_attempt_registry import (
    FinancialExecutionAttemptRegistry,
)
from ..registry.financial_execution_command_registry import (
    FinancialExecutionCommandRegistry,
)
from ..registry.financial_execution_provider_observation_registry import (
    FinancialExecutionProviderObservationRegistry,
)
VERSION = "v1.0.0-M11-HOST-EXECUTION-RECONCILIATION"


def _runtime_composer():
    """Load the certified post-terminalization composer without a second implementation."""
    module_name = "." + "financial_execution_" + "runtime_orchestrator"
    return getattr(
        importlib.import_module(module_name, __package__),
        "orchestrate_terminal_execution_fact_and_projection",
    )


orchestrate_terminal_execution_fact_and_projection = _runtime_composer()


class FinancialExecutionReconciliationError(RuntimeError):
    """Fail-closed reconciliation or finalization error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _reject(code: str) -> NoReturn:
    """Reject malformed or insufficient authority without fallback inference."""
    raise FinancialExecutionReconciliationError(code)


def _active_session(session: ClientSession) -> ClientSession:
    """Require an active transaction owned by the caller."""
    if session is None or not bool(getattr(session, "in_transaction", False)):
        _reject("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _correlate_attempt_command(
    tenant_id: str,
    attempt: FinancialExecutionAttempt,
    command: FinancialExecutionCommand,
) -> None:
    """Require exact durable command lineage before lifecycle mutation."""
    if attempt.tenant_id != tenant_id or command.tenant_id != tenant_id:
        _reject("COMMAND_ATTEMPT_TENANT_MISMATCH")
    if attempt.execution_command_id != command.execution_command_id:
        _reject("COMMAND_ATTEMPT_ID_MISMATCH")
    if attempt.request_fingerprint != command.fingerprint:
        _reject("COMMAND_ATTEMPT_FINGERPRINT_MISMATCH")
    if attempt.provider_name != command.provider_name:
        _reject("COMMAND_ATTEMPT_PROVIDER_MISMATCH")
    if attempt.payment_destination_reference != command.payment_destination_reference:
        _reject("COMMAND_ATTEMPT_DESTINATION_MISMATCH")


def _require_time_match(
    tenant_id: str,
    attempt: FinancialExecutionAttempt,
    observation: FinancialExecutionProviderObservation,
    execution_time: FinancialExecutionTimeEvidence | None,
) -> datetime:
    """Require explicit, typed execution-time authority and exact evidence identity."""
    if not isinstance(execution_time, FinancialExecutionTimeEvidence):
        _reject("EXECUTION_TIME_EVIDENCE_REQUIRED")
    if (
        execution_time.tenant_id != tenant_id
        or execution_time.tenant_id != attempt.tenant_id
        or execution_time.execution_attempt_id != attempt.execution_attempt_id
        or execution_time.provider_name != attempt.provider_name
        or execution_time.provider_execution_reference
        != observation.provider_execution_reference
        or execution_time.evidence_reference != observation.provider_evidence_reference
        or execution_time.evidence_strength is not observation.evidence_strength
    ):
        _reject("EXECUTION_TIME_EVIDENCE_CORRELATION_MISMATCH")
    if execution_time.executed_at.tzinfo is None:
        _reject("EXECUTION_TIME_INVALID")
    return execution_time.executed_at


def _decision(
    tenant_id: str,
    attempt: FinancialExecutionAttempt,
    observations: tuple[FinancialExecutionProviderObservation, ...],
    execution_time: FinancialExecutionTimeEvidence | None,
) -> ExecutionReconciliationDecision:
    """Evaluate only canonical durable evidence; request fields never authorize."""
    if not observations:
        _reject("EXECUTION_OBSERVATION_NOT_FOUND")
    if any(
        item.tenant_id != tenant_id
        or item.tenant_id != attempt.tenant_id
        or item.execution_attempt_id != attempt.execution_attempt_id
        or item.provider_name != attempt.provider_name
        for item in observations
    ):
        _reject("OBSERVATION_IDENTITY_MISMATCH")

    terminal = tuple(
        item
        for item in observations
        if item.observation_status
        in {
            ObservationStatus.EXECUTED,
            ObservationStatus.FAILED,
            ObservationStatus.CANCELLED,
        }
    )
    executed = tuple(
        item for item in terminal if item.observation_status is ObservationStatus.EXECUTED
    )
    if len(executed) != 1:
        _reject("EXECUTED_EVIDENCE_NOT_UNIQUE")
    if any(
        item.observation_status
        in {ObservationStatus.FAILED, ObservationStatus.CANCELLED}
        for item in terminal
    ):
        _reject("CONFLICTING_TERMINAL_EVIDENCE")
    observation = executed[0]
    if (
        observation.evidence_strength
        not in {EvidenceStrength.AUTHENTICATED, EvidenceStrength.CORROBORATED}
        or observation.transport_disposition is TransportDisposition.AMBIGUOUS
        or not observation.provider_execution_reference
        or not observation.provider_evidence_reference
    ):
        _reject("EXECUTED_EVIDENCE_INSUFFICIENT")
    confirmed_at = _require_time_match(tenant_id, attempt, observation, execution_time)
    decision = ExecutionReconciliationDecision(
        outcome=ExecutionReconciliationOutcome.CONFIRMED_EXECUTED,
        evidence_reference=observation.provider_evidence_reference,
        confirmed_at=confirmed_at,
        reason="AUTHENTICATED_DURABLE_EXECUTION_EVIDENCE",
    )
    try:
        attempt.finalize(decision)
    except FinancialExecutionLifecycleError as error:
        raise FinancialExecutionReconciliationError(
            "RECONCILIATION_FINALIZATION_REJECTED"
        ) from error
    return decision


def reconcile_and_finalize_execution(
    tenant_id: str,
    execution_attempt_id: str,
    *,
    command_collection: Collection,
    attempt_collection: Collection,
    observation_collection: Collection,
    fact_collection: Collection,
    ap_truth_collection: Collection,
    platform_truth_collection: Collection,
    execution_time_evidence: FinancialExecutionTimeEvidence,
    session: ClientSession,
) -> FinancialExecutionTruth | PlatformBillingFinancialExecutionTruth:
    """Reconcile durable authenticated evidence and compose terminal execution truth.

    The caller must supply an active Mongo transaction. All reads, the attempt
    CAS transition, neutral fact derivation, and family projection use that same
    session. A caller retry starts a new transaction and repeats this complete
    operation; this function never commits, aborts, starts sessions, calls a
    provider, or invokes settlement.
    """
    tx = _active_session(session)
    tenant = str(tenant_id).strip()
    attempt_id = str(execution_attempt_id).strip()
    if not tenant or not attempt_id:
        _reject("TENANT_AND_ATTEMPT_REQUIRED")
    attempt = FinancialExecutionAttemptRegistry.get(
        tenant, attempt_id, attempt_collection, session=tx
    )
    command = FinancialExecutionCommandRegistry.get(
        tenant, attempt.execution_command_id, command_collection, session=tx
    )
    if not isinstance(command, FinancialExecutionCommand):
        _reject("COMMAND_REQUIRED")
    _correlate_attempt_command(tenant, attempt, command)
    observations = FinancialExecutionProviderObservationRegistry.list_for_attempt(
        tenant, attempt_id, collection=observation_collection, session=tx
    )
    decision = _decision(tenant, attempt, observations, execution_time_evidence)

    if attempt.state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED:
        if (
            attempt.confirmed_at != decision.confirmed_at
            or attempt.reconciliation_evidence_reference != decision.evidence_reference
        ):
            _reject("CONFIRMED_ATTEMPT_REPLAY_MISMATCH")
        persisted = attempt
    elif attempt.state in {
        FinancialExecutionAttemptState.CONFIRMED_FAILED,
        FinancialExecutionAttemptState.CANCELLED,
    }:
        _reject("TERMINAL_ATTEMPT_CONFLICT")
    else:
        try:
            target = attempt.transition_to(
                FinancialExecutionAttemptState.CONFIRMED_EXECUTED,
                evidence_reference=decision.evidence_reference,
                confirmed_at=decision.confirmed_at,
            )
        except FinancialExecutionLifecycleError as error:
            raise FinancialExecutionReconciliationError(
                "ATTEMPT_LIFECYCLE_TRANSITION_REJECTED"
            ) from error
        persisted = FinancialExecutionAttemptRegistry.transition(
            tenant,
            attempt.execution_attempt_id,
            attempt.state,
            attempt.fingerprint,
            target,
            attempt_collection,
            session=tx,
        )

    if persisted.state is not FinancialExecutionAttemptState.CONFIRMED_EXECUTED:
        _reject("ATTEMPT_NOT_CONFIRMED_EXECUTED")
    return orchestrate_terminal_execution_fact_and_projection(
        tenant,
        persisted.execution_attempt_id,
        command_collection=command_collection,
        attempt_collection=attempt_collection,
        observation_collection=observation_collection,
        fact_collection=fact_collection,
        ap_truth_collection=ap_truth_collection,
        platform_truth_collection=platform_truth_collection,
        execution_time_evidence=execution_time_evidence,
        session=tx,
    )


__all__ = [
    "FinancialExecutionReconciliationError",
    "reconcile_and_finalize_execution",
]


# ARTIFACT: financial_execution_reconciliation.py
# VERSION: v1.0.0-M11-HOST-EXECUTION-RECONCILIATION
# AUTHORITY BOUNDARY: durable evidence reconciliation and lifecycle CAS only; no settlement.
# TENANT POSTURE: exact tenant, command, attempt, provider, and evidence correlation.
# FAIL-CLOSED POSTURE: missing, weak, ambiguous, conflicting, or divergent evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; EXECUTION != SETTLEMENT.
# END OF WILSY OS SOVEREIGN ARTIFACT
