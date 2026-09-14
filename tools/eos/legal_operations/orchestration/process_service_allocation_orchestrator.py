"""Canonical P4A orchestration for process-service allocation evidence.

TITLE: Wilsy OS Process Service Allocation Orchestrator
VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR
AUTHORITY: Wilsy OS Core Governance
EPITOME: Compose already-certified Legal Operations lifecycle snapshots,
         assignment authority, custody evidence, P2 persistence, and P4B
         receipt/current CAS without creating service or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/process_service_allocation_orchestrator.py
COLLABORATION / OWNERSHIP: P4A orchestration owner; P1 remains lifecycle and
                            custody authority, P2 remains durable lifecycle
                            evidence persistence, P3 remains assignment
                            authority, and P4B remains allocation receipt and
                            current-pointer persistence. The caller owns the
                            Mongo session and transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR composes
           exact P1/P3 evidence with non-healing P2 replay checks and P4B
           receipt/current CAS under one caller-owned transaction.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque tenant and evidence references only; no
                             network, provider, secret, credential, or PII
                             expansion occurs during orchestration.
TENANT BOUNDARY: All supplied P1/P3 values, P2 identities, P4B lookups, and
                 derived custody evidence must share one explicit tenant and
                 document scope; cross-tenant composition fails closed.
AUTHORITY BOUNDARY: P4A composition only. This module does not authorize
                    assignment, mutate P1 values, bootstrap currentness,
                    create service attempts/executions/returns, or provide IAM
                    or transport authority.
FINANCIAL AUTHORITY BOUNDARY: Allocation evidence is not invoicing, payment,
                              execution, or settlement; Kennel EOS exclusively
                              owns financial execution and settlement.
TRANSACTION BOUNDARY: An already-active caller-owned Mongo transaction is
                      required before any persistence read/write. This module
                      never starts, commits, aborts, retries, or stores a
                      Mongo client.
FAIL-CLOSED DECLARATION: Invalid source evidence, identity, lineage,
                         chronology, custody history, replay provenance,
                         partial state, persistence, and transaction inputs
                         reject through stable P4A errors.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    Deputy,
    District,
    DocumentCustodyEvent,
    DocumentCustodyEventType,
    LegalInstruction,
    LegalInstructionState,
    LegalOperationsLifecycleError,
    ProcessDocument,
    ProcessDocumentState,
    SheriffOffice,
    validate_custody_event_chain,
)
from tools.eos.legal_operations.domain.process_service_assignment_authority import (
    ProcessServiceAssignmentDecision,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
)
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationPersistenceResult,
    ProcessServiceAllocationReceipt,
    ProcessServiceAllocationRegistry,
)


VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR"
CUSTODY_CHAIN_SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-CUSTODY-CHAIN/V1"
_SHA3 = re.compile(r"^[0-9a-f]{128}$")


class ProcessServiceAllocationOrchestratorError(RuntimeError):
    """Stable fail-closed P4A composition error.

    The error represents no transaction lifecycle action and no allocation,
    service, invoice, payment, execution, or settlement authority. Mongo
    persistence errors from P2/P4B are deliberately allowed to retain their
    upstream governed error types and codes.
    """

    default_code: str = "P4A_ORCHESTRATION_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class ProcessServiceAllocationOrchestratorInputError(ProcessServiceAllocationOrchestratorError):
    """Explicit P4A input, identity, source, lineage, or chronology failure."""

    default_code: str = "P4A_INPUT_INVALID"


class ProcessServiceAllocationOrchestratorTransactionRequiredError(ProcessServiceAllocationOrchestratorError):
    """Caller did not provide an already-active transaction session."""

    default_code: str = "P4A_ACTIVE_TRANSACTION_REQUIRED"


class ProcessServiceAllocationOrchestratorPartialReplayError(ProcessServiceAllocationOrchestratorError):
    """P2/P4B evidence was partially present or diverged and cannot be healed."""

    default_code: str = "P4A_PARTIAL_REPLAY"


@dataclass(frozen=True, slots=True)
class ProcessServiceAllocationOrchestrationResult:
    """Immutable P4A result containing derived evidence and exact P4B outcome.

    ``allocated_document``, ``allocation_custody_event``, and
    ``result_custody_chain`` are derived from validated P1 inputs. The
    ``persistence_result`` is the exact caller-transaction-scoped P4B result.
    No field represents a service attempt, execution, return, billing, payment,
    or settlement fact.
    """

    allocated_document: ProcessDocument
    allocation_custody_event: DocumentCustodyEvent
    result_custody_chain: tuple[DocumentCustodyEvent, ...]
    persistence_result: ProcessServiceAllocationPersistenceResult

    def __post_init__(self) -> None:
        if type(self.allocated_document) is not ProcessDocument:
            _fail("P4A_RESULT_DOCUMENT_INVALID")
        if type(self.allocation_custody_event) is not DocumentCustodyEvent:
            _fail("P4A_RESULT_EVENT_INVALID")
        if not isinstance(self.result_custody_chain, tuple) or not self.result_custody_chain:
            _fail("P4A_RESULT_CHAIN_INVALID")
        if any(type(event) is not DocumentCustodyEvent for event in self.result_custody_chain):
            _fail("P4A_RESULT_CHAIN_INVALID")
        if type(self.persistence_result) is not ProcessServiceAllocationPersistenceResult:
            _fail("P4A_RESULT_PERSISTENCE_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize only canonical P1/P4B evidence, without new authority."""
        return {
            "allocated_document": self.allocated_document.to_dict(),
            "allocation_custody_event": self.allocation_custody_event.to_dict(),
            "result_custody_chain": [event.to_dict() for event in self.result_custody_chain],
            "persistence_result": self.persistence_result.to_dict(),
        }


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable P4A error while retaining a technical cause."""
    error = ProcessServiceAllocationOrchestratorError(code)
    if cause is None:
        raise error
    raise error from cause


def _fail_input(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable P4A input error."""
    error = ProcessServiceAllocationOrchestratorInputError(code)
    if cause is None:
        raise error
    raise error from cause


def _fail_partial(code: str = "P4A_PARTIAL_REPLAY") -> NoReturn:
    """Raise the non-healing partial-replay failure."""
    raise ProcessServiceAllocationOrchestratorPartialReplayError(code)


def _active_transaction(session: object) -> object:
    """Require an already-active caller session before any database access."""
    if session is None:
        raise ProcessServiceAllocationOrchestratorTransactionRequiredError()
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        raise ProcessServiceAllocationOrchestratorTransactionRequiredError() from error
    if active is not True:
        raise ProcessServiceAllocationOrchestratorTransactionRequiredError()
    return session


def _validate_p1(value: object, expected: type[object], code: str) -> None:
    """Revalidate an exact canonical P1 runtime value and its evidence."""
    if type(value) is not expected:
        _fail_input(code)
    try:
        cast(Any, value).__post_init__()
    except Exception as error:
        _fail_input(code, error)


def _validate_assignment(value: object) -> ProcessServiceAssignmentDecision:
    """Revalidate the exact P3 proof-bearing assignment decision."""
    if type(value) is not ProcessServiceAssignmentDecision:
        _fail_input("P4A_ASSIGNMENT_DECISION_INVALID")
    try:
        cast(ProcessServiceAssignmentDecision, value).__post_init__()
    except Exception as error:
        _fail_input("P4A_ASSIGNMENT_DECISION_INVALID", error)
    return cast(ProcessServiceAssignmentDecision, value)


def _utc(name: str, value: object) -> datetime:
    """Require an explicit aware UTC timestamp for allocation evidence."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        _fail_input(f"P4A_{name.upper()}_INVALID")
    return value


def _text(name: str, value: object) -> str:
    """Require explicit non-empty evidence text without inventing defaults."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail_input(f"P4A_{name.upper()}_INVALID")
    return value


def _identity(name: str, value: object) -> str:
    """Require one canonical opaque identity."""
    if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", value) is None:
        _fail_input(f"P4A_{name.upper()}_INVALID")
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 fingerprint."""
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail_input(f"P4A_{name.upper()}_INVALID")
    return value


def _sha3(value: object) -> str:
    """Hash deterministic JSON using the P2 canonical convention."""
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _p2_identity(value: ProcessDocument | DocumentCustodyEvent) -> str:
    """Derive the public P2 evidence identity without importing P2 internals."""
    entity_type = type(value).__name__
    identity_name = "document_id" if entity_type == "ProcessDocument" else "custody_event_id"
    return _sha3(
        {
            "tenant_id": value.tenant_id,
            "entity_type": entity_type,
            "entity_identity": getattr(value, identity_name),
            "p1_fingerprint": value.fingerprint,
            "source_fingerprint": None,
        }
    )


def _transition_at(document: ProcessDocument, state: ProcessDocumentState) -> datetime:
    """Return the unique transition timestamp proving one document state."""
    matches = tuple(event for event in document.transition_history if event.resulting_state is state)
    if len(matches) != 1:
        _fail_input("P4A_DOCUMENT_TRANSITION_EVIDENCE_MISSING")
    return matches[0].occurred_at


def _custody_chain_fingerprint(
    tenant_id: str,
    document_id: str,
    events: tuple[DocumentCustodyEvent, ...],
) -> str:
    """Derive the first explicit P4A custody-chain digest contract."""
    return _sha3(
        {
            "schema": CUSTODY_CHAIN_SCHEMA,
            "tenant_id": tenant_id,
            "document_id": document_id,
            "event_fingerprints": [event.fingerprint for event in events],
        }
    )


def _p2_get(
    tenant_id: str,
    evidence_identity: str,
    lifecycle_collection: Any,
    session: object,
) -> object | None:
    """Read one P2 identity, distinguishing only its exact absence code."""
    try:
        return LegalOperationsLifecycleRegistry.get(
            tenant_id,
            evidence_identity,
            lifecycle_collection,
            session=session,
        )
    except LegalOperationsLifecycleRegistryError as error:
        if str(error) == "M2_EVIDENCE_NOT_FOUND":
            return None
        raise


def _require_exact_result(
    value: object | None,
    expected: ProcessDocument | DocumentCustodyEvent,
) -> ProcessDocument | DocumentCustodyEvent:
    """Require an existing P2 result to equal the newly derived value exactly."""
    if type(value) is not type(expected) or value is None:
        _fail_partial()
    candidate = cast(ProcessDocument | DocumentCustodyEvent, value)
    if candidate.to_dict() != expected.to_dict() or candidate.fingerprint != expected.fingerprint:
        _fail_partial()
    return candidate


def orchestrate_process_service_allocation(
    *,
    instruction: LegalInstruction,
    document: ProcessDocument,
    district: District,
    sheriff_office: SheriffOffice,
    deputy: Deputy,
    assignment_decision: ProcessServiceAssignmentDecision,
    prior_custody_events: Iterable[DocumentCustodyEvent],
    expected_prior_current: ProcessServiceAllocationCurrent,
    allocation_command_id: str,
    idempotency_key: str,
    allocation_custody_event_id: str,
    allocation_evidence_reference: str,
    allocated_at: datetime,
    lifecycle_collection: Any,
    allocation_receipt_collection: Any,
    allocation_current_collection: Any,
    session: object,
) -> ProcessServiceAllocationOrchestrationResult:
    """Compose one allocation receipt/current advancement under caller control.

    The first operation requires an active caller transaction. Exact P1/P3
    sources and the complete prior custody chain are revalidated, one
    allocation transition/event are derived, P2 partial-replay conditions are
    checked without healing, and P4B persists the receipt/current CAS. This
    function never starts, commits, aborts, retries, or owns a Mongo session.
    """
    tx = _active_transaction(session)

    _validate_p1(instruction, LegalInstruction, "P4A_INSTRUCTION_INVALID")
    _validate_p1(document, ProcessDocument, "P4A_DOCUMENT_INVALID")
    _validate_p1(district, District, "P4A_DISTRICT_INVALID")
    _validate_p1(sheriff_office, SheriffOffice, "P4A_SHERIFF_OFFICE_INVALID")
    _validate_p1(deputy, Deputy, "P4A_DEPUTY_INVALID")
    decision = _validate_assignment(assignment_decision)
    if type(expected_prior_current) is not ProcessServiceAllocationCurrent:
        _fail_input("P4A_EXPECTED_CURRENT_INVALID")
    try:
        expected_prior_current.__post_init__()
    except Exception as error:
        _fail_input("P4A_EXPECTED_CURRENT_INVALID", error)

    tenant = instruction.tenant_id
    if any(value.tenant_id != tenant for value in (document, district, sheriff_office, deputy, decision)):
        _fail_input("P4A_TENANT_MISMATCH")
    if instruction.state is not LegalInstructionState.ACCEPTED:
        _fail_input("P4A_INSTRUCTION_NOT_ACCEPTED")
    if document.state is not ProcessDocumentState.RECEIVED:
        _fail_input("P4A_DOCUMENT_NOT_RECEIVED")
    if instruction.document_id != document.document_id or instruction.case_matter_id != document.case_matter_id:
        _fail_input("P4A_INSTRUCTION_DOCUMENT_MISMATCH")
    if sheriff_office.district_id != district.district_id:
        _fail_input("P4A_DISTRICT_OFFICE_LINEAGE_MISMATCH")
    if deputy.sheriff_office_id != sheriff_office.sheriff_office_id:
        _fail_input("P4A_OFFICE_DEPUTY_LINEAGE_MISMATCH")
    decision_bindings = (
        (decision.instruction_id, instruction.instruction_id),
        (decision.case_matter_id, instruction.case_matter_id),
        (decision.document_id, document.document_id),
        (decision.district_id, district.district_id),
        (decision.sheriff_office_id, sheriff_office.sheriff_office_id),
        (decision.deputy_id, deputy.deputy_id),
        (decision.instruction_fingerprint, instruction.fingerprint),
        (decision.document_fingerprint, document.fingerprint),
        (decision.district_fingerprint, district.fingerprint),
        (decision.sheriff_office_fingerprint, sheriff_office.fingerprint),
        (decision.deputy_fingerprint, deputy.fingerprint),
    )
    if any(actual != expected for actual, expected in decision_bindings):
        _fail_input("P4A_ASSIGNMENT_SOURCE_BINDING_INVALID")

    try:
        prior_chain = validate_custody_event_chain(tuple(prior_custody_events))
    except (LegalOperationsLifecycleError, TypeError) as error:
        _fail_input("P4A_PRIOR_CUSTODY_CHAIN_INVALID", error)
    if any(event.tenant_id != tenant or event.document_id != document.document_id for event in prior_chain):
        _fail_input("P4A_PRIOR_CUSTODY_SCOPE_INVALID")
    prior_head = prior_chain[-1]
    if prior_head.event_type is not DocumentCustodyEventType.RECEIVED_IN_OFFICE:
        _fail_input("P4A_PRIOR_CUSTODY_HEAD_INVALID")
    if prior_head.to_holder_reference != sheriff_office.sheriff_office_id:
        _fail_input("P4A_PRIOR_CUSTODY_HEAD_INVALID")
    if (
        expected_prior_current.tenant_id != tenant
        or expected_prior_current.document_id != document.document_id
        or expected_prior_current.process_document_fingerprint != document.fingerprint
        or expected_prior_current.custody_head_event_id != prior_head.custody_event_id
        or expected_prior_current.custody_head_fingerprint != prior_head.fingerprint
        or expected_prior_current.custody_head_sequence_number != prior_head.sequence_number
        or expected_prior_current.current_holder_reference != prior_head.to_holder_reference
    ):
        _fail_input("P4A_EXPECTED_CURRENT_CORRELATION_INVALID")
    prior_chain_fingerprint = _custody_chain_fingerprint(tenant, document.document_id, prior_chain)
    if expected_prior_current.custody_chain_fingerprint != prior_chain_fingerprint:
        _fail_input("P4A_PRIOR_CUSTODY_FINGERPRINT_INVALID")

    allocation_time = _utc("allocated_at", allocated_at)
    received_at = _transition_at(document, ProcessDocumentState.RECEIVED)
    if allocation_time < instruction.registered_at or allocation_time < document.registered_at:
        _fail_input("P4A_ALLOCATION_CHRONOLOGY_INVALID")
    if allocation_time < received_at or allocation_time < decision.decided_at or allocation_time < prior_head.occurred_at:
        _fail_input("P4A_ALLOCATION_CHRONOLOGY_INVALID")
    allocation_command = _identity("allocation_command_id", allocation_command_id)
    idempotency = _text("idempotency_key", idempotency_key)
    custody_event_id = _identity("allocation_custody_event_id", allocation_custody_event_id)
    allocation_reference = _text("allocation_evidence_reference", allocation_evidence_reference)

    existing_receipt = ProcessServiceAllocationRegistry.get_receipt_by_idempotency_key(
        tenant,
        document.document_id,
        idempotency,
        allocation_receipt_collection,
        session=tx,
    )

    try:
        allocated_document = document.transition_to(
            ProcessDocumentState.ALLOCATED_TO_DEPUTY,
            evidence_reference=allocation_reference,
            occurred_at=allocation_time,
        )
        allocation_event = DocumentCustodyEvent(
            tenant_id=tenant,
            custody_event_id=custody_event_id,
            document_id=document.document_id,
            event_type=DocumentCustodyEventType.ALLOCATED_TO_DEPUTY,
            occurred_at=allocation_time,
            sequence_number=prior_head.sequence_number + 1,
            evidence_reference=allocation_reference,
            from_holder_reference=prior_head.to_holder_reference,
            to_holder_reference=deputy.deputy_id,
        )
        result_chain = validate_custody_event_chain((*prior_chain, allocation_event))
    except (LegalOperationsLifecycleError, TypeError) as error:
        _fail_input("P4A_DERIVED_EVIDENCE_INVALID", error)
    result_chain_fingerprint = _custody_chain_fingerprint(tenant, document.document_id, result_chain)
    if not result_chain_fingerprint:
        _fail_input("P4A_RESULT_CUSTODY_FINGERPRINT_INVALID")

    receipt = ProcessServiceAllocationReceipt(
        tenant_id=tenant,
        allocation_command_id=allocation_command,
        idempotency_key=idempotency,
        instruction_id=instruction.instruction_id,
        case_matter_id=instruction.case_matter_id,
        document_id=document.document_id,
        district_id=district.district_id,
        sheriff_office_id=sheriff_office.sheriff_office_id,
        deputy_id=deputy.deputy_id,
        assignment_decision_id=decision.assignment_decision_id,
        assignment_decision_fingerprint=decision.fingerprint,
        source_instruction_fingerprint=instruction.fingerprint,
        source_document_fingerprint=document.fingerprint,
        source_district_fingerprint=district.fingerprint,
        source_sheriff_office_fingerprint=sheriff_office.fingerprint,
        source_deputy_fingerprint=deputy.fingerprint,
        prior_custody_chain_fingerprint=prior_chain_fingerprint,
        prior_custody_head_event_id=prior_head.custody_event_id,
        prior_custody_head_fingerprint=prior_head.fingerprint,
        prior_custody_head_sequence_number=prior_head.sequence_number,
        from_holder_reference=cast(str, prior_head.to_holder_reference),
        to_holder_reference=deputy.deputy_id,
        allocation_custody_event_id=allocation_event.custody_event_id,
        allocation_evidence_reference=allocation_reference,
        allocated_at=allocation_time,
        allocated_document_fingerprint=allocated_document.fingerprint,
        allocation_custody_event_fingerprint=allocation_event.fingerprint,
        result_custody_chain_fingerprint=result_chain_fingerprint,
    )
    expected_document_identity = _p2_identity(allocated_document)
    expected_event_identity = _p2_identity(allocation_event)

    if existing_receipt is not None:
        if existing_receipt.to_dict() != receipt.to_dict() or existing_receipt.fingerprint != receipt.fingerprint:
            _fail_partial("P4A_REPLAY_RECEIPT_DIVERGENCE")
        persisted_document = _require_exact_result(
            _p2_get(tenant, expected_document_identity, lifecycle_collection, tx), allocated_document
        )
        persisted_event = _require_exact_result(
            _p2_get(tenant, expected_event_identity, lifecycle_collection, tx), allocation_event
        )
    else:
        existing_document = _p2_get(tenant, expected_document_identity, lifecycle_collection, tx)
        existing_event = _p2_get(tenant, expected_event_identity, lifecycle_collection, tx)
        if existing_document is not None or existing_event is not None:
            _fail_partial()
        durable_prior = ProcessServiceAllocationRegistry.get_current(
            tenant,
            document.document_id,
            allocation_current_collection,
            session=tx,
        )
        if durable_prior.to_dict() != expected_prior_current.to_dict():
            _fail_input("P4A_EXPECTED_CURRENT_DURABLE_MISMATCH")
        persisted_document = LegalOperationsLifecycleRegistry.create(
            allocated_document,
            lifecycle_collection,
            session=tx,
        )
        persisted_event = LegalOperationsLifecycleRegistry.create(
            allocation_event,
            lifecycle_collection,
            session=tx,
        )
        if type(persisted_document) is not ProcessDocument or persisted_document.to_dict() != allocated_document.to_dict():
            _fail_partial("P4A_P2_DOCUMENT_DIVERGENCE")
        if type(persisted_event) is not DocumentCustodyEvent or persisted_event.to_dict() != allocation_event.to_dict():
            _fail_partial("P4A_P2_EVENT_DIVERGENCE")

    persistence_result = ProcessServiceAllocationRegistry.persist_receipt_and_advance_current(
        receipt,
        expected_prior_current,
        allocation_receipt_collection,
        allocation_current_collection,
        session=tx,
    )
    return ProcessServiceAllocationOrchestrationResult(
        allocated_document=cast(ProcessDocument, persisted_document),
        allocation_custody_event=cast(DocumentCustodyEvent, persisted_event),
        result_custody_chain=result_chain,
        persistence_result=persistence_result,
    )


__all__ = [
    "CUSTODY_CHAIN_SCHEMA",
    "ProcessServiceAllocationOrchestrationResult",
    "ProcessServiceAllocationOrchestratorError",
    "ProcessServiceAllocationOrchestratorInputError",
    "ProcessServiceAllocationOrchestratorPartialReplayError",
    "ProcessServiceAllocationOrchestratorTransactionRequiredError",
    "VERSION",
    "orchestrate_process_service_allocation",
]


# ARTIFACT: process_service_allocation_orchestrator.py
# VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR
# AUTHORITY BOUNDARY: P4A composition only; no service or financial execution authority.
# TENANT POSTURE: exact tenant and document scope across all P1/P2/P3/P4B evidence.
# FAIL-CLOSED POSTURE: active caller transaction, source integrity, chronology, replay, and CAS are mandatory.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns financial execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
