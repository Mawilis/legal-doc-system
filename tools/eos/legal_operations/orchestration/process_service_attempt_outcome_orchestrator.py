"""Compose terminal attempt outcome and durable ServiceExecution evidence.

TITLE: Wilsy OS Process-Service Attempt Outcome Orchestrator
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-ORCHESTRATOR
AUTHORITY: Wilsy OS Core Governance
EPITOME: Read an exact P2 ATTEMPTED snapshot, authorize one terminal outcome,
         persist outcome evidence, terminal attempt, and derived ServiceExecution
         in one caller-owned transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/process_service_attempt_outcome_orchestrator.py
COLLABORATION / OWNERSHIP: P5E composition only; P1 owns lifecycle and
                            ServiceExecution factories; P2 owns persistence;
                            caller owns session/transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-ORCHESTRATOR
           establishes atomic terminal outcome -> ServiceExecution composition.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: P2-derived attempt is the sole source of tenant and legal IDs.
AUTHORITY BOUNDARY: ServiceExecution legal truth only; no ReturnOfService or billing.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Active caller transaction, exact ATTEMPTED source,
                         terminal evidence, chronology, and P1 factory derivation required.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState, ServiceExecution
from tools.eos.legal_operations.domain.process_service_attempt_outcome_authority import authorize_process_service_attempt_outcome
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_attempt_outcome_registry import ProcessServiceAttemptOutcomeRegistry

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-ORCHESTRATOR"


class ProcessServiceAttemptOutcomeOrchestratorError(RuntimeError):
    """Stable fail-closed terminal-outcome composition error."""

    def __init__(self, code: str) -> None:
        """Create one governed error."""
        self.code = code
        super().__init__(code)


def _transaction(session: object) -> None:
    marker = getattr(session, "in_transaction", False)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        raise ProcessServiceAttemptOutcomeOrchestratorError("P5E_TRANSACTION_REQUIRED") from error
    if active is not True:
        raise ProcessServiceAttemptOutcomeOrchestratorError("P5E_TRANSACTION_REQUIRED")


def transition_process_service_attempt_outcome(*, tenant_id: str, current_evidence_identity: str, lifecycle_collection: Any, outcome_collection: Any, outcome: ServiceAttemptState, evidence_reference: str, evidence_fingerprint: str, occurred_at: datetime, service_execution_id: str, executed_at: datetime, session: object) -> ServiceExecution:
    """Persist one terminal P1 attempt and its factory-derived ServiceExecution.

    All three durable facts use the supplied active session. This function never
    starts, commits, aborts, or ends caller transactions and never creates a return,
    invoice, payment, settlement, or other financial authority.
    """
    _transaction(session)
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ProcessServiceAttemptOutcomeOrchestratorError("P5E_TENANT_INVALID")
    current = LegalOperationsLifecycleRegistry.get(tenant_id, current_evidence_identity, lifecycle_collection, session=session)
    if type(current) is not ServiceAttempt or current.state is not ServiceAttemptState.ATTEMPTED:
        raise ProcessServiceAttemptOutcomeOrchestratorError("P5E_SOURCE_STATE_INVALID")
    decision = authorize_process_service_attempt_outcome(
        current_attempt=current,
        outcome=outcome,
        evidence_reference=evidence_reference,
        evidence_fingerprint=evidence_fingerprint,
        occurred_at=occurred_at,
        service_execution_id=service_execution_id,
        executed_at=executed_at,
    )
    ProcessServiceAttemptOutcomeRegistry.persist(decision, outcome_collection, session=session)
    terminal = current.transition_to(outcome, evidence_reference=evidence_reference, occurred_at=occurred_at, evidence_fingerprint=evidence_fingerprint)
    persisted_terminal = LegalOperationsLifecycleRegistry.create(terminal, lifecycle_collection, session=session)
    if type(persisted_terminal) is not ServiceAttempt or persisted_terminal.to_dict() != terminal.to_dict() or persisted_terminal.fingerprint != terminal.fingerprint:
        raise ProcessServiceAttemptOutcomeOrchestratorError("P5E_P2_REPLAY_DIVERGENCE")
    execution = ServiceExecution.from_attempt(attempt=cast(ServiceAttempt, persisted_terminal), service_execution_id=service_execution_id, executed_at=executed_at)
    persisted_execution = LegalOperationsLifecycleRegistry.create(execution, lifecycle_collection, session=session, source_attempt=cast(ServiceAttempt, persisted_terminal))
    if type(persisted_execution) is not ServiceExecution or persisted_execution.to_dict() != execution.to_dict() or persisted_execution.fingerprint != execution.fingerprint:
        raise ProcessServiceAttemptOutcomeOrchestratorError("P5E_EXECUTION_REPLAY_DIVERGENCE")
    return cast(ServiceExecution, persisted_execution)


__all__ = ["VERSION", "ProcessServiceAttemptOutcomeOrchestratorError", "transition_process_service_attempt_outcome"]


# ARTIFACT: process_service_attempt_outcome_orchestrator.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-ORCHESTRATOR
# AUTHORITY BOUNDARY: ATTEMPTED -> terminal attempt plus P1-derived ServiceExecution only.
# TENANT POSTURE: all identities derive from one validated P2 attempt.
# FAIL-CLOSED POSTURE: invalid state, evidence, chronology, replay, or persistence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
