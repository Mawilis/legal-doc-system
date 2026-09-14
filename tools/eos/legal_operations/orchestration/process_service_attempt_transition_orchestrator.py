"""Compose one durable field-attempt evidence transition.

TITLE: Wilsy OS Process-Service Attempt Transition Orchestrator
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-ORCHESTRATOR
AUTHORITY: Wilsy OS Core Governance
EPITOME: Read an exact P2 ALLOCATED snapshot, authorize and persist opaque
         field evidence, then append only the P1 ATTEMPTED transition.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/process_service_attempt_transition_orchestrator.py
COLLABORATION / OWNERSHIP: P5D composition only; P1 owns lifecycle, P2 owns
                            immutable snapshots, caller owns Mongo transaction.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-ORCHESTRATOR
           establishes caller-transaction composition for ALLOCATED -> ATTEMPTED.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Tenant scope is an explicit P2 lookup and must equal the
                 hydrated source attempt; no caller claims replace P1 identity.
AUTHORITY BOUNDARY: No terminal service, return, billing, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Active caller transaction, exact P1 type/state,
                         evidence, chronology, and replay-safe persistence are mandatory.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState
from tools.eos.legal_operations.domain.process_service_attempt_transition_authority import authorize_process_service_attempt_transition
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_attempt_transition_registry import ProcessServiceAttemptTransitionRegistry

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-ORCHESTRATOR"


class ProcessServiceAttemptTransitionOrchestratorError(RuntimeError):
    """Stable fail-closed composition error."""

    def __init__(self, code: str) -> None:
        """Create one governed composition error."""
        self.code = code
        super().__init__(code)


def _require_transaction(session: object) -> None:
    marker = getattr(session, "in_transaction", False)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        raise ProcessServiceAttemptTransitionOrchestratorError("P5D_TRANSACTION_REQUIRED") from error
    if active is not True:
        raise ProcessServiceAttemptTransitionOrchestratorError("P5D_TRANSACTION_REQUIRED")


def transition_process_service_attempt(
    *, tenant_id: str, current_evidence_identity: str, lifecycle_collection: Any,
    transition_collection: Any, evidence_reference: str, evidence_fingerprint: str,
    occurred_at: datetime, session: object,
) -> ServiceAttempt:
    """Persist exactly one ALLOCATED -> ATTEMPTED transition in caller transaction.

    P2 hydration is the source of all tenant and P1 identities. The authority
    and registry receive only opaque evidence and the caller's session; neither
    transaction lifecycle nor terminal service/return construction is performed.
    """
    _require_transaction(session)
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ProcessServiceAttemptTransitionOrchestratorError("P5D_TENANT_INVALID")
    current = LegalOperationsLifecycleRegistry.get(tenant_id, current_evidence_identity, lifecycle_collection, session=session)
    if type(current) is not ServiceAttempt or current.state is not ServiceAttemptState.ALLOCATED:
        raise ProcessServiceAttemptTransitionOrchestratorError("P5D_SOURCE_STATE_INVALID")
    decision = authorize_process_service_attempt_transition(
        current_attempt=current,
        evidence_reference=evidence_reference,
        evidence_fingerprint=evidence_fingerprint,
        occurred_at=occurred_at,
    )
    ProcessServiceAttemptTransitionRegistry.persist(decision, transition_collection, session=session)
    attempted = current.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference=evidence_reference,
        evidence_fingerprint=evidence_fingerprint,
        occurred_at=occurred_at,
    )
    persisted = LegalOperationsLifecycleRegistry.create(attempted, lifecycle_collection, session=session)
    if type(persisted) is not ServiceAttempt or persisted.to_dict() != attempted.to_dict() or persisted.fingerprint != attempted.fingerprint:
        raise ProcessServiceAttemptTransitionOrchestratorError("P5D_P2_REPLAY_DIVERGENCE")
    return cast(ServiceAttempt, persisted)


__all__ = ["VERSION", "ProcessServiceAttemptTransitionOrchestratorError", "transition_process_service_attempt"]


# ARTIFACT: process_service_attempt_transition_orchestrator.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-ORCHESTRATOR
# AUTHORITY BOUNDARY: P5D ALLOCATED -> ATTEMPTED composition only.
# TENANT POSTURE: P2-derived source attempt is the sole authority for identities.
# FAIL-CLOSED POSTURE: inactive transactions, invalid evidence, and divergence reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
