"""Compose canonical P2 attempts with immutable offline field evidence.

TITLE: Wilsy OS Process-Service Offline Field-Evidence Sync Orchestrator
VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-ORCHESTRATOR
AUTHORITY: Wilsy OS Core Governance
EPITOME: Validate one device observation against canonical P1/P2 attempt
         context and persist an immutable sync receipt in a caller transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/process_service_field_evidence_orchestrator.py
COLLABORATION / OWNERSHIP: P5 evidence composition only; P1 owns lifecycle,
                            P2 owns lifecycle persistence, and callers own
                            Mongo session/transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-ORCHESTRATOR
           establishes caller-transactional observation synchronization.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Attempt tenant and all identities derive from exact P2 data.
AUTHORITY BOUNDARY: Sync acceptance only; no attempt/service/return transition.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
TRANSACTION BOUNDARY: A caller-owned active session is mandatory and is passed
                      to every P2 and P5 persistence operation.
FAIL-CLOSED DECLARATION: Missing, stale, cross-tenant, malformed, or divergent
                         context rejects without fabricating legal truth.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt
from tools.eos.legal_operations.domain.process_service_field_evidence_authority import (
    OfflineFieldEvidenceSyncReceipt,
    _issue_sync_receipt,
    create_offline_field_evidence_command,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_allocation_registry import ProcessServiceAllocationRegistry, _hydrate_receipt
from tools.eos.legal_operations.registry.process_service_field_evidence_registry import ProcessServiceFieldEvidenceRegistry

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-ORCHESTRATOR"


class ProcessServiceFieldEvidenceOrchestratorError(RuntimeError):
    """Stable fail-closed orchestration error without lifecycle authority."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise ProcessServiceFieldEvidenceOrchestratorError(code)


def sync_offline_field_evidence(
    *,
    tenant_id: str,
    attempt_evidence_identity: str,
    device_id: str,
    event_id: str,
    sequence_number: int,
    occurred_at: datetime,
    evidence_reference: str,
    evidence_fingerprint: str,
    previous_event_fingerprint: str | None = None,
    receipt_id: str,
    accepted_at: datetime,
    lifecycle_collection: Any,
    allocation_receipt_collection: Any,
    allocation_current_collection: Any,
    journal_collection: Any,
    session: Any,
) -> OfflineFieldEvidenceSyncReceipt:
    """Accept one observation against an exact canonical P2 ``ServiceAttempt``.

    The supplied tenant and evidence identity are used only to locate the
    canonical attempt; all authority-bearing identities are then derived from
    that hydrated attempt.  The caller's active transaction owns atomicity,
    commit, abort, and whole-transaction retry.  This function never mutates
    the P1 attempt and never creates service, return, invoice, or payment truth.
    """
    if session is None or not bool(getattr(session, "in_transaction", False)):
        _fail("P5M_ACTIVE_TRANSACTION_REQUIRED")
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        _fail("P5M_INVALID_TENANT")
    try:
        attempt = LegalOperationsLifecycleRegistry.get(tenant_id, attempt_evidence_identity, lifecycle_collection, session=session)
    except Exception as error:
        if isinstance(error, ProcessServiceFieldEvidenceOrchestratorError):
            raise
        raise ProcessServiceFieldEvidenceOrchestratorError("P5M_CANONICAL_ATTEMPT_UNAVAILABLE") from error
    if type(attempt) is not ServiceAttempt:
        _fail("P5M_CANONICAL_ATTEMPT_REQUIRED")
    try:
        allocation_document = allocation_receipt_collection.find_one(
            {"tenant_id": attempt.tenant_id, "receipt_payload.allocation_evidence_reference": attempt.allocation_evidence_reference},
            session=session,
        )
        if allocation_document is None:
            for candidate in allocation_receipt_collection.find({"tenant_id": attempt.tenant_id}, session=session):
                hydrated_candidate = _hydrate_receipt(candidate)
                if hydrated_candidate.allocation_evidence_reference == attempt.allocation_evidence_reference:
                    allocation_document = candidate
                    break
        if allocation_document is None:
            _fail("P5M_ALLOCATION_NOT_FOUND")
        allocation_receipt = _hydrate_receipt(allocation_document)
        allocation_current = ProcessServiceAllocationRegistry.get_current(
            attempt.tenant_id, attempt.document_id, allocation_current_collection, session=session
        )
    except ProcessServiceFieldEvidenceOrchestratorError:
        raise
    except Exception as error:
        raise ProcessServiceFieldEvidenceOrchestratorError("P5M_ALLOCATION_UNAVAILABLE") from error
    command = create_offline_field_evidence_command(
        attempt=attempt,
        allocation_receipt=allocation_receipt,
        allocation_current=allocation_current,
        device_id=device_id,
        event_id=event_id,
        sequence_number=sequence_number,
        occurred_at=occurred_at,
        evidence_reference=evidence_reference,
        evidence_fingerprint=evidence_fingerprint,
        previous_event_fingerprint=previous_event_fingerprint,
    )
    receipt = _issue_sync_receipt(command=command, receipt_id=receipt_id, accepted_at=accepted_at)
    persisted = ProcessServiceFieldEvidenceRegistry.persist(command, receipt, journal_collection, session=session)
    if persisted.to_dict() != receipt.to_dict() or persisted.fingerprint != receipt.fingerprint:
        _fail("P5M_REPLAY_CONFLICT")
    return persisted


__all__ = ["VERSION", "ProcessServiceFieldEvidenceOrchestratorError", "sync_offline_field_evidence"]


# ARTIFACT: process_service_field_evidence_orchestrator.py
# VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-ORCHESTRATOR
# AUTHORITY BOUNDARY: canonical-context evidence synchronization only.
# TENANT POSTURE: tenant and legal identities derive from P2 ServiceAttempt.
# FAIL-CLOSED POSTURE: no active caller transaction or canonical attempt means rejection.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
