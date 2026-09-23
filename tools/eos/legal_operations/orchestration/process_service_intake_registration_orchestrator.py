"""Canonical initial-intake registration for Legal Operations process service.

TITLE: WILSY OS Process Service Intake Registration Orchestrator
VERSION: v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION
AUTHORITY: Wilsy OS Legal Operations initial case/instruction/document registration composition.
EPITOME: Register or exactly replay one tenant-scoped initial CaseMatter,
         LegalInstruction, ProcessDocument, and first REGISTERED custody fact
         inside one caller-owned active transaction without collapsing
         registration into acceptance, receipt, allocation, service, billing,
         payment, or settlement authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/process_service_intake_registration_orchestrator.py
COLLABORATION / OWNERSHIP: P1 owns lifecycle and custody value semantics; P2
                            owns immutable persistence and strict hydration;
                            L8-0 owns deterministic history validation; L8-2
                            owns only the initial intake registration bundle.
                            HTTP/IAM admission remains a separate boundary.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION
           establishes transaction-required initial CaseMatter ->
           LegalInstruction -> ProcessDocument registration with the first
           DocumentCustodyEvent.REGISTERED fact, complete-history preflight,
           exact replay, partial-registration rejection, chronology binding,
           and no acceptance/receipt/service/financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Accepts explicit tenant-scoped opaque legal intake
                             identities, references, document type, and
                             timestamps only. It accepts no credentials, JWT
                             claims, provider secrets, payment data, browser
                             tenant authority, service outcome, or settlement data.
TENANT BOUNDARY: Every history lookup and write binds the exact P1-validated
                 tenant_id. The four intake facts must share that tenant and
                 exact matter/document lineage; no foreign fallback is allowed.
AUTHORITY BOUNDARY: Initial registration only. REGISTERED instruction is not
                    ACCEPTED; REGISTERED document/custody is not RECEIVED;
                    registration creates no allocation, attempt, service,
                    return, invoice, IAM, payment, execution, or settlement truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; intake registration has no
                              financial-execution or settlement semantics.
TRANSACTION BOUNDARY: The caller must supply one already-active transaction
                      session and must abort it on any raised failure. This
                      module never starts, commits, aborts, or retries a
                      transaction. P2 receives the same session for every
                      history read and persistence write.
FAIL-CLOSED DECLARATION: Missing transaction, malformed P1 input, invalid
                         chronology, partial prior registration, corrupt or
                         divergent history, same-identity/different-registration
                         evidence, and persistence divergence reject without
                         healing, fallback, or invented lifecycle truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    LegalOperationsCurrentProjectionError,
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    DocumentCustodyEvent,
    DocumentCustodyEventType,
    LegalInstruction,
    LegalOperationsLifecycleError,
    ProcessDocument,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)


VERSION: Final[str] = "v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION"

_IntakeValue = CaseMatter | LegalInstruction | ProcessDocument | DocumentCustodyEvent


class ProcessServiceIntakeRegistrationDisposition(StrEnum):
    """Durable bundle outcome without adding downstream lifecycle authority."""

    CREATED = "CREATED"
    REPLAYED = "REPLAYED"


class ProcessServiceIntakeRegistrationError(RuntimeError):
    """Stable fail-closed L8-2 initial registration failure.

    The exception grants no tenant, IAM, acceptance, receipt, custody transfer,
    allocation, attempt, service, return, invoice, payment, execution, or
    settlement authority.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ProcessServiceIntakeTransactionRequiredError(
    ProcessServiceIntakeRegistrationError
):
    """Caller did not provide one already-active transaction session."""


@dataclass(frozen=True, slots=True)
class ProcessServiceIntakeRegistrationResult:
    """Immutable evidence result for one initial intake create or exact replay.

    The four values are exact canonical P1 registration facts. A replay may be
    returned even if stateful entities later advanced, provided complete durable
    history is non-divergent and contains the exact original registration
    snapshot. The result itself creates no later lifecycle or financial authority.
    """

    case_matter: CaseMatter
    instruction: LegalInstruction
    document: ProcessDocument
    custody_event: DocumentCustodyEvent
    disposition: ProcessServiceIntakeRegistrationDisposition

    def __post_init__(self) -> None:
        """Revalidate result lineage and registration-only semantics."""
        if self.instruction.tenant_id != self.case_matter.tenant_id:
            _fail("L8_2_RESULT_TENANT_MISMATCH")
        if self.document.tenant_id != self.case_matter.tenant_id:
            _fail("L8_2_RESULT_TENANT_MISMATCH")
        if self.custody_event.tenant_id != self.case_matter.tenant_id:
            _fail("L8_2_RESULT_TENANT_MISMATCH")
        if self.instruction.case_matter_id != self.case_matter.case_matter_id:
            _fail("L8_2_RESULT_MATTER_LINEAGE_MISMATCH")
        if self.document.case_matter_id != self.case_matter.case_matter_id:
            _fail("L8_2_RESULT_MATTER_LINEAGE_MISMATCH")
        if self.instruction.document_id != self.document.document_id:
            _fail("L8_2_RESULT_DOCUMENT_LINEAGE_MISMATCH")
        if self.custody_event.document_id != self.document.document_id:
            _fail("L8_2_RESULT_DOCUMENT_LINEAGE_MISMATCH")
        if self.custody_event.event_type is not DocumentCustodyEventType.REGISTERED:
            _fail("L8_2_RESULT_CUSTODY_NOT_REGISTERED")
        if self.custody_event.sequence_number != 1:
            _fail("L8_2_RESULT_CUSTODY_SEQUENCE_INVALID")
        if not isinstance(
            self.disposition,
            ProcessServiceIntakeRegistrationDisposition,
        ):
            _fail("L8_2_RESULT_DISPOSITION_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize bounded registration evidence without downstream authority."""
        return {
            "disposition": self.disposition.value,
            "case_matter": self.case_matter.to_dict(),
            "instruction": self.instruction.to_dict(),
            "document": self.document.to_dict(),
            "custody_event": self.custody_event.to_dict(),
        }


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable intake failure while retaining the technical cause."""
    error = ProcessServiceIntakeRegistrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _active_transaction(session: object) -> object:
    """Require one already-active caller-owned transaction before any read."""
    if session is None:
        raise ProcessServiceIntakeTransactionRequiredError(
            "L8_2_ACTIVE_TRANSACTION_REQUIRED"
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        raise ProcessServiceIntakeTransactionRequiredError(
            "L8_2_ACTIVE_TRANSACTION_REQUIRED"
        ) from error
    if active is not True:
        raise ProcessServiceIntakeTransactionRequiredError(
            "L8_2_ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _construct_case_matter(
    tenant_id: str,
    case_matter_id: str,
    matter_reference: str,
    opened_at: Any,
    evidence_reference: str,
) -> CaseMatter:
    """Construct one initial OPEN CaseMatter and normalize P1 validation failures."""
    try:
        return CaseMatter(
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            matter_reference=matter_reference,
            opened_at=opened_at,
            evidence_reference=evidence_reference,
        )
    except LegalOperationsLifecycleError as error:
        _fail("L8_2_REGISTRATION_VALUE_INVALID", error)


def _construct_document(
    tenant_id: str,
    document_id: str,
    case_matter_id: str,
    document_type: str,
    registered_at: Any,
    registration_evidence_reference: str,
) -> ProcessDocument:
    """Construct one initial REGISTERED ProcessDocument."""
    try:
        return ProcessDocument(
            tenant_id=tenant_id,
            document_id=document_id,
            case_matter_id=case_matter_id,
            document_type=document_type,
            registered_at=registered_at,
            registration_evidence_reference=registration_evidence_reference,
        )
    except LegalOperationsLifecycleError as error:
        _fail("L8_2_REGISTRATION_VALUE_INVALID", error)


def _construct_instruction(
    tenant_id: str,
    instruction_id: str,
    case_matter_id: str,
    document_id: str,
    registered_at: Any,
    evidence_reference: str,
) -> LegalInstruction:
    """Construct one initial REGISTERED LegalInstruction."""
    try:
        return LegalInstruction(
            tenant_id=tenant_id,
            instruction_id=instruction_id,
            case_matter_id=case_matter_id,
            document_id=document_id,
            registered_at=registered_at,
            evidence_reference=evidence_reference,
        )
    except LegalOperationsLifecycleError as error:
        _fail("L8_2_REGISTRATION_VALUE_INVALID", error)


def _construct_registered_custody(
    tenant_id: str,
    custody_event_id: str,
    document_id: str,
    occurred_at: Any,
    evidence_reference: str,
) -> DocumentCustodyEvent:
    """Construct the required sequence-one REGISTERED custody fact."""
    try:
        return DocumentCustodyEvent(
            tenant_id=tenant_id,
            custody_event_id=custody_event_id,
            document_id=document_id,
            event_type=DocumentCustodyEventType.REGISTERED,
            occurred_at=occurred_at,
            sequence_number=1,
            evidence_reference=evidence_reference,
        )
    except LegalOperationsLifecycleError as error:
        _fail("L8_2_REGISTRATION_VALUE_INVALID", error)


def _identity(value: _IntakeValue) -> str:
    """Return the exact P1 identity used by P2 history scope."""
    if isinstance(value, CaseMatter):
        return value.case_matter_id
    if isinstance(value, LegalInstruction):
        return value.instruction_id
    if isinstance(value, ProcessDocument):
        return value.document_id
    if isinstance(value, DocumentCustodyEvent):
        return value.custody_event_id
    _fail("L8_2_REGISTRATION_VALUE_INVALID")


def _existing_exact_registration(
    proposed: _IntakeValue,
    *,
    lifecycle_collection: Any,
    session: object,
) -> _IntakeValue | None:
    """Return the exact original registration fact after full-history validation.

    Any non-empty history is first passed through L8-0 so forks, static payload
    drift, and immutable-fact divergence fail closed. Stateful entities may have
    advanced after the original registration; replay remains valid only when the
    exact proposed initial snapshot is still present in complete P2 history.
    """
    entity_type = type(proposed)
    history = LegalOperationsLifecycleRegistry.get_entity_history(
        proposed.tenant_id,
        entity_type.__name__,
        _identity(proposed),
        lifecycle_collection,
        session=session,
    )
    if not history:
        return None
    try:
        resolve_current_lifecycle_snapshot(
            history,
            expected_type=entity_type,
        )
    except LegalOperationsCurrentProjectionError as error:
        _fail("L8_2_REGISTRATION_HISTORY_DIVERGENT", error)

    exact = tuple(
        value
        for value in history
        if type(value) is entity_type
        and getattr(value, "fingerprint", None) == proposed.fingerprint
    )
    if len(exact) != 1:
        _fail("L8_2_REGISTRATION_IDENTITY_DIVERGENCE")
    return cast(_IntakeValue, exact[0])


def _persist_exact(
    proposed: _IntakeValue,
    *,
    lifecycle_collection: Any,
    session: object,
) -> _IntakeValue:
    """Persist one exact P1 registration value and verify P2 returned it."""
    persisted = LegalOperationsLifecycleRegistry.create(
        proposed,
        lifecycle_collection,
        session=session,
    )
    if type(persisted) is not type(proposed):
        _fail("L8_2_REGISTRATION_PERSISTED_TYPE_INVALID")
    if persisted.fingerprint != proposed.fingerprint:
        _fail("L8_2_REGISTRATION_PERSISTED_DIVERGENCE")
    return cast(_IntakeValue, persisted)


def register_process_service_intake(
    *,
    tenant_id: str,
    case_matter_id: str,
    matter_reference: str,
    case_opened_at: Any,
    matter_evidence_reference: str,
    instruction_id: str,
    instruction_registered_at: Any,
    instruction_evidence_reference: str,
    document_id: str,
    document_type: str,
    document_registered_at: Any,
    document_registration_evidence_reference: str,
    registration_custody_event_id: str,
    lifecycle_collection: Any,
    session: object,
) -> ProcessServiceIntakeRegistrationResult:
    """Create or exactly replay one complete initial process-service intake.

    Chronology is explicit: the case/matter opens no later than the instruction,
    the instruction is registered no later than the process document, and the
    first custody event occurs exactly at document registration. The custody
    event reuses the document registration evidence reference so registration
    creates one coherent evidence basis without pretending that office receipt
    has occurred.

    Before any write, complete P2 history for all four identities is validated.
    Either all four exact registration facts already exist and REPLAYED is
    returned, or none exist and all four are persisted under the caller-owned
    transaction. Any mixed presence is a partial registration and rejects
    without healing. The caller must abort its transaction on failure.
    """
    active_session = _active_transaction(session)

    case_matter = _construct_case_matter(
        tenant_id,
        case_matter_id,
        matter_reference,
        case_opened_at,
        matter_evidence_reference,
    )
    instruction = _construct_instruction(
        tenant_id,
        instruction_id,
        case_matter_id,
        document_id,
        instruction_registered_at,
        instruction_evidence_reference,
    )
    document = _construct_document(
        tenant_id,
        document_id,
        case_matter_id,
        document_type,
        document_registered_at,
        document_registration_evidence_reference,
    )
    custody_event = _construct_registered_custody(
        tenant_id,
        registration_custody_event_id,
        document_id,
        document_registered_at,
        document_registration_evidence_reference,
    )

    if case_matter.opened_at > instruction.registered_at:
        _fail("L8_2_REGISTRATION_CHRONOLOGY_INVALID")
    if instruction.registered_at > document.registered_at:
        _fail("L8_2_REGISTRATION_CHRONOLOGY_INVALID")
    if custody_event.occurred_at != document.registered_at:
        _fail("L8_2_REGISTRATION_CHRONOLOGY_INVALID")

    proposed: tuple[_IntakeValue, ...] = (
        case_matter,
        instruction,
        document,
        custody_event,
    )
    existing = tuple(
        _existing_exact_registration(
            value,
            lifecycle_collection=lifecycle_collection,
            session=active_session,
        )
        for value in proposed
    )

    present = tuple(value is not None for value in existing)
    if any(present) and not all(present):
        _fail("L8_2_PARTIAL_REGISTRATION")

    if all(present):
        replay_case = existing[0]
        replay_instruction = existing[1]
        replay_document = existing[2]
        replay_custody = existing[3]
        if not isinstance(replay_case, CaseMatter):
            _fail("L8_2_REGISTRATION_PERSISTED_TYPE_INVALID")
        if not isinstance(replay_instruction, LegalInstruction):
            _fail("L8_2_REGISTRATION_PERSISTED_TYPE_INVALID")
        if not isinstance(replay_document, ProcessDocument):
            _fail("L8_2_REGISTRATION_PERSISTED_TYPE_INVALID")
        if not isinstance(replay_custody, DocumentCustodyEvent):
            _fail("L8_2_REGISTRATION_PERSISTED_TYPE_INVALID")
        return ProcessServiceIntakeRegistrationResult(
            case_matter=replay_case,
            instruction=replay_instruction,
            document=replay_document,
            custody_event=replay_custody,
            disposition=ProcessServiceIntakeRegistrationDisposition.REPLAYED,
        )

    persisted_case = _persist_exact(
        case_matter,
        lifecycle_collection=lifecycle_collection,
        session=active_session,
    )
    persisted_instruction = _persist_exact(
        instruction,
        lifecycle_collection=lifecycle_collection,
        session=active_session,
    )
    persisted_document = _persist_exact(
        document,
        lifecycle_collection=lifecycle_collection,
        session=active_session,
    )
    persisted_custody = _persist_exact(
        custody_event,
        lifecycle_collection=lifecycle_collection,
        session=active_session,
    )

    if not isinstance(persisted_case, CaseMatter):
        _fail("L8_2_REGISTRATION_PERSISTED_TYPE_INVALID")
    if not isinstance(persisted_instruction, LegalInstruction):
        _fail("L8_2_REGISTRATION_PERSISTED_TYPE_INVALID")
    if not isinstance(persisted_document, ProcessDocument):
        _fail("L8_2_REGISTRATION_PERSISTED_TYPE_INVALID")
    if not isinstance(persisted_custody, DocumentCustodyEvent):
        _fail("L8_2_REGISTRATION_PERSISTED_TYPE_INVALID")

    return ProcessServiceIntakeRegistrationResult(
        case_matter=persisted_case,
        instruction=persisted_instruction,
        document=persisted_document,
        custody_event=persisted_custody,
        disposition=ProcessServiceIntakeRegistrationDisposition.CREATED,
    )


__all__ = [
    "VERSION",
    "ProcessServiceIntakeRegistrationDisposition",
    "ProcessServiceIntakeRegistrationError",
    "ProcessServiceIntakeRegistrationResult",
    "ProcessServiceIntakeTransactionRequiredError",
    "register_process_service_intake",
]


# ARTIFACT: process_service_intake_registration_orchestrator.py
# VERSION: v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION
# AUTHORITY BOUNDARY: initial case/instruction/document/custody registration composition only
# TENANT POSTURE: exact tenant history and writes; exact matter/document lineage required
# FAIL-CLOSED POSTURE: inactive transaction, malformed chronology, partial state, corruption, and divergence reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
