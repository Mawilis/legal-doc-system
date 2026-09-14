"""Compose canonical P2 ServiceExecution into P1 ReturnOfService.

TITLE: Wilsy OS Process-Service Return Orchestrator
VERSION: v1.0.0-PROCESS-SERVICE-RETURN-ORCHESTRATOR
AUTHORITY: Wilsy OS Core Governance
EPITOME: Hydrate an exact durable ServiceExecution, authorize immutable return
         evidence, invoke the P1 ReturnOfService factory, and persist both facts
         in the caller-owned transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/process_service_return_orchestrator.py
COLLABORATION / OWNERSHIP: P5F composition only; P1 owns return semantics,
                            P2 owns snapshots, caller owns transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-RETURN-ORCHESTRATOR establishes
           durable execution -> return composition for both service outcomes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: P2-derived ServiceExecution and source attempt are sole identity authorities.
AUTHORITY BOUNDARY: ReturnOfService legal fact only; no invoice/payment/settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Active transaction, exact P2 execution, matching source
                         attempt, P1 factory derivation, and replay-safe persistence required.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ReturnOfService, ServiceAttempt, ServiceAttemptState, ServiceExecution
from tools.eos.legal_operations.domain.process_service_return_authority import authorize_process_service_return
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_return_registry import ProcessServiceReturnRegistry

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-RETURN-ORCHESTRATOR"


class ProcessServiceReturnOrchestratorError(RuntimeError):
    """Stable fail-closed return composition error."""

    def __init__(self, code: str) -> None:
        """Create one governed error."""
        self.code = code
        super().__init__(code)


def _active(session: object) -> None:
    marker = getattr(session, "in_transaction", False)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        raise ProcessServiceReturnOrchestratorError("P5F_TRANSACTION_REQUIRED") from error
    if active is not True:
        raise ProcessServiceReturnOrchestratorError("P5F_TRANSACTION_REQUIRED")


def _source_attempt(execution: ServiceExecution, lifecycle_collection: Any, session: object) -> ServiceAttempt:
    """Hydrate the exact terminal attempt corroborating a P2 execution."""
    rows = lifecycle_collection.find({"tenant_id": execution.tenant_id, "entity_type": "ServiceAttempt", "entity_identity": execution.attempt_id}, session=session)
    candidates: list[ServiceAttempt] = []
    for row in rows:
        evidence_identity = row.get("evidence_identity") if isinstance(row, dict) else None
        if not isinstance(evidence_identity, str):
            continue
        try:
            value = LegalOperationsLifecycleRegistry.get(execution.tenant_id, evidence_identity, lifecycle_collection, session=session)
        except Exception:
            continue
        if type(value) is ServiceAttempt:
            candidates.append(cast(ServiceAttempt, value))
    for attempt in candidates:
        if attempt.state not in {ServiceAttemptState.COMPLETED, ServiceAttemptState.NOT_COMPLETED}:
            continue
        try:
            derived = ServiceExecution.from_attempt(attempt=attempt, service_execution_id=execution.service_execution_id, executed_at=execution.executed_at)
        except Exception:
            continue
        if derived.to_dict() == execution.to_dict() and derived.fingerprint == execution.fingerprint:
            return attempt
    raise ProcessServiceReturnOrchestratorError("P5F_SOURCE_ATTEMPT_INVALID")


def generate_process_service_return(*, tenant_id: str, execution_evidence_identity: str, lifecycle_collection: Any, return_collection: Any, return_id: str, generated_at: datetime, session: object) -> ReturnOfService:
    """Generate and persist one P1 ReturnOfService from canonical P2 execution.

    The source execution and corroborating terminal attempt are hydrated from
    P2; caller claims cannot replace their tenant, outcome, or identities. The
    supplied session is used for every read/write and its lifecycle is untouched.
    """
    _active(session)
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ProcessServiceReturnOrchestratorError("P5F_TENANT_INVALID")
    execution = LegalOperationsLifecycleRegistry.get(tenant_id, execution_evidence_identity, lifecycle_collection, session=session)
    if type(execution) is not ServiceExecution:
        raise ProcessServiceReturnOrchestratorError("P5F_SOURCE_EXECUTION_INVALID")
    source_attempt = _source_attempt(cast(ServiceExecution, execution), lifecycle_collection, session)
    decision = authorize_process_service_return(service_execution=cast(ServiceExecution, execution), return_id=return_id, generated_at=generated_at)
    ProcessServiceReturnRegistry.persist(decision, return_collection, session=session)
    result = ReturnOfService.from_service_execution(instruction_id=execution.instruction_id, service_execution=cast(ServiceExecution, execution), return_id=return_id, generated_at=generated_at)
    persisted = LegalOperationsLifecycleRegistry.create(result, lifecycle_collection, session=session, source_attempt=source_attempt, source_execution=cast(ServiceExecution, execution))
    if type(persisted) is not ReturnOfService or persisted.to_dict() != result.to_dict() or persisted.fingerprint != result.fingerprint:
        raise ProcessServiceReturnOrchestratorError("P5F_P2_REPLAY_DIVERGENCE")
    return cast(ReturnOfService, persisted)


__all__ = ["VERSION", "ProcessServiceReturnOrchestratorError", "generate_process_service_return"]


# ARTIFACT: process_service_return_orchestrator.py
# VERSION: v1.0.0-PROCESS-SERVICE-RETURN-ORCHESTRATOR
# AUTHORITY BOUNDARY: canonical ServiceExecution -> ReturnOfService only.
# TENANT POSTURE: identities derive from exact tenant-scoped P2 evidence.
# FAIL-CLOSED POSTURE: invalid source, divergence, chronology, and persistence reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
