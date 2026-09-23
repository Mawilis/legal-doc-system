"""WILSY OS Legal Operations command boundary.

TITLE: Legal Operations Command API
VERSION: v1.6.0-L8-6G-SERVER-OWNED-FIELD-SEQUENCE
AUTHORITY: HTTP command composition only; P1/P2/L8-1/L8-2/L8-3/L8-6B/P4/P5 remain canonical authorities.
EPITOME: Translate authenticated tenant-scoped intake, acceptance/receipt,
         directory, deputy-principal identity-binding, and field-service
         commands into bounded canonical orchestrator composition inside one
         API-owned Mongo transaction without accepting browser-supplied tenant authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/legal_operations_command_router.py
COLLABORATION / OWNERSHIP: API composition owns transport and transaction
                           mechanics; domain/registry/orchestrator modules own
                           lifecycle, evidence, and persistence truth.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.6.0-L8-6G-SERVER-OWNED-FIELD-SEQUENCE
           removes browser ownership of P5M sequence_number and previous-event
           fingerprint for bound-Deputy field commands. The server now recovers
           exact event replay inputs or derives the next immutable sequence from
           the certified tenant/attempt/device journal head inside the same
           transaction before P5M -> P5D/P5E composition.
           2026-09-23 v1.5.0-L8-6E-DEPUTY-FIELD-COMMAND-BRIDGE
           adds bound-Deputy field transition/outcome composition: authenticated
           principal-to-Deputy scope is re-resolved inside the command transaction,
           browser observation facts are canonicalized into server-derived SHA3-512
           field evidence, P5M sync/replay is atomic with P5D/P5E, and terminal
           ServiceExecution identity is server-derived. Existing sheriff command
           compatibility remains; tenant_deputy use of legacy transition/outcome
           routes is additionally binding-scoped.
           2026-09-23 v1.4.1-L8-6B-DEPUTY-PRINCIPAL-BINDING-COMMAND-API aligns the sovereign authority/header
           declarations with the already-authored L8-6B identity-binding
           composition; runtime route, IAM, transaction, and error semantics
           are unchanged.
           2026-09-23 v1.4.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-COMMAND-API adds one sheriff-only
           directory command for immutable principal-to-canonical-Deputy
           identity binding. The request cannot supply tenant authority; L8-6B
           independently proves target principal, membership, tenant_deputy
           business role, DEPUTY assignment, and canonical Deputy evidence
           inside the same API-owned transaction before the binding write.
           v1.3.0-L8-3-LEGAL-OPERATIONS-RECEIPT-COMMAND-API adds one
           sheriff-only legal_operations:receipt:write command that composes
           canonical L8-3 instruction acceptance plus physical office receipt
           inside the API-owned transaction. It also routes allocation custody
           reads through the canonical P2 custody-history API instead of
           depending on P2 durable record shape.
           v1.2.1-L8-2-LEGAL-OPERATIONS-INTAKE-COMMAND-API replaces the
           deprecated Starlette 422 status alias with HTTP 422 Unprocessable
           Content while preserving the exact fail-closed command projection.
           v1.2.0-L8-2-LEGAL-OPERATIONS-INTAKE-COMMAND-API added one
           legal_operations:instruction:write-authorized own-tenant intake
           registration command. The body cannot supply tenant_id; L8-2 creates
           or exactly replays CaseMatter, LegalInstruction, ProcessDocument,
           and REGISTERED custody inside the same API-owned transaction while
           registration remains distinct from acceptance and office receipt.
           v1.1.1-L8-1-LEGAL-OPERATIONS-DIRECTORY-COMMAND-API preserved
           structured L8-1 directory provisioning failures across the API-owned
           transaction boundary so bounded parent absence remains HTTP 404
           instead of being collapsed into generic command-unavailable 503.
           v1.1.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-COMMAND-API added three
           sheriff-authorized own-tenant directory provisioning commands for
           District, SheriffOffice, and Deputy. Tenant scope comes only from
           RequireTenantAuthorization; the request cannot supply tenant_id;
           L8-1 performs canonical parent/history validation inside the same
           API-owned transaction.
           v1.0.0-L7B-LEGAL-OPERATIONS-COMMAND-API established authenticated
           allocation, attempt creation/transition, terminal-outcome, and
           return command boundaries using evidence locators only.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Request bodies contain bounded intake facts,
                            acceptance/receipt evidence, directory facts, locators, and observations; tenant
                            authority comes only from durable authorization and
                            canonical domain/orchestrator layers own lifecycle,
                            lineage, fingerprints, and outcome truth.
TENANT BOUNDARY: X-Tenant-ID from RequireTenantAuthorization is the only
                 request scope; every Mongo query includes that tenant.
AUTHORITY BOUNDARY: This module composes authenticated command transport and
                    transaction mechanics only. Ordinary commands dispatch one
                    canonical orchestrator; L8-6E/L8-6G deputy field commands
                    compose only the certified P5M -> P5D/P5E chain in one
                    transaction with sequence lineage derived server-side.
TRANSACTION BOUNDARY: The API acquires the configured client, starts one
                      session/transaction, invokes one orchestrator, commits
                      only after success, aborts on failure, and ends the session.
FINANCIAL AUTHORITY BOUNDARY: No invoice, payment, settlement, or financial
                              execution authority; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing authority, malformed locators, unavailable
                         persistence, divergent evidence, and ambiguous commit
                         outcomes return bounded errors without fabricated success.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
from typing import Any, Callable, Final, TypeVar, cast

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization, TenantAuthorizationContext
from tools.eos.auth.principal_authority_repository import (
    COLLECTION as PRINCIPAL_AUTHORITY_COLLECTION,
)
from tools.eos.auth.role_assignment_repository import (
    COLLECTION as ROLE_ASSIGNMENT_COLLECTION,
)
from tools.eos.auth.tenant_business_role_repository import (
    COLLECTION as TENANT_BUSINESS_ROLE_COLLECTION,
)
from tools.eos.auth.tenant_membership_repository import (
    COLLECTION as TENANT_MEMBERSHIP_COLLECTION,
)
from tools.eos.legal_operations.domain.process_service_field_evidence_authority import ProcessServiceFieldEvidenceAuthorityError
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    District,
    Deputy,
    LegalInstruction,
    ProcessDocument,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
    SheriffOffice,
)
from tools.eos.legal_operations.domain.process_service_assignment_authority import authorize_process_service_assignment
from tools.eos.legal_operations.orchestration.deputy_principal_binding_orchestrator import (
    DeputyPrincipalBindingOrchestrationError,
    bind_deputy_principal_identity,
)
from tools.eos.legal_operations.orchestration.process_service_allocation_orchestrator import orchestrate_process_service_allocation
from tools.eos.legal_operations.orchestration.process_service_directory_provisioning_orchestrator import (
    ProcessServiceDirectoryProvisioningError,
    provision_deputy,
    provision_district,
    provision_sheriff_office,
)
from tools.eos.legal_operations.orchestration.process_service_intake_registration_orchestrator import (
    ProcessServiceIntakeRegistrationError,
    register_process_service_intake,
)
from tools.eos.legal_operations.orchestration.process_service_acceptance_receipt_orchestrator import (
    ProcessServiceAcceptanceReceiptError,
    accept_instruction_and_receive_document,
)
from tools.eos.legal_operations.orchestration.process_service_attempt_orchestrator import orchestrate_process_service_attempt
from tools.eos.legal_operations.orchestration.process_service_field_evidence_orchestrator import (
    ProcessServiceFieldEvidenceOrchestratorError,
    sync_offline_field_evidence,
)
from tools.eos.legal_operations.orchestration.process_service_attempt_outcome_orchestrator import transition_process_service_attempt_outcome
from tools.eos.legal_operations.orchestration.process_service_attempt_transition_orchestrator import transition_process_service_attempt
from tools.eos.legal_operations.orchestration.process_service_return_orchestrator import generate_process_service_return
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    COLLECTION as DEPUTY_PRINCIPAL_BINDING_COLLECTION,
    DeputyPrincipalBindingRegistry,
    DeputyPrincipalBindingRegistryError,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import COLLECTION as LIFECYCLE_COLLECTION, LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ALLOCATION_CURRENT_COLLECTION,
    ALLOCATION_RECEIPT_COLLECTION,
    ProcessServiceAllocationRegistry,
)
from tools.eos.legal_operations.registry.process_service_attempt_authority_registry import RECEIPT_COLLECTION as ATTEMPT_AUTHORITY_COLLECTION
from tools.eos.legal_operations.registry.process_service_attempt_outcome_registry import COLLECTION as OUTCOME_COLLECTION
from tools.eos.legal_operations.registry.process_service_attempt_transition_registry import COLLECTION as TRANSITION_COLLECTION
from tools.eos.legal_operations.registry.process_service_field_evidence_registry import (
    COLLECTION as FIELD_EVIDENCE_COLLECTION,
    ProcessServiceFieldEvidenceRegistry,
    ProcessServiceFieldEvidenceRegistryError,
)
from tools.eos.legal_operations.registry.process_service_return_registry import COLLECTION as RETURN_COLLECTION


VERSION: Final[str] = "v1.6.0-L8-6G-SERVER-OWNED-FIELD-SEQUENCE"
router = APIRouter(prefix="/legal-operations", tags=["Legal Operations Commands"])
_T = TypeVar("_T")
_DEPUTY_BUSINESS_ROLE: Final[str] = "tenant_deputy"
_FIELD_OBSERVATION_SCHEMA: Final[str] = "WILSY-LEGAL-OPERATIONS-DEPUTY-FIELD-OBSERVATION/V1"
_FIELD_RECEIPT_SCHEMA: Final[str] = "WILSY-LEGAL-OPERATIONS-DEPUTY-FIELD-RECEIPT-ID/V1"
_FIELD_EXECUTION_SCHEMA: Final[str] = "WILSY-LEGAL-OPERATIONS-DEPUTY-SERVICE-EXECUTION-ID/V1"


class _CommandModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class IntakeRegistrationCommand(_CommandModel):
    """Bounded initial Legal Operations intake facts; tenant is server-derived.

    The model carries opaque matter/instruction/document identities, timestamps,
    document type, and evidence references only. It cannot supply tenant_id,
    acceptance, receipt, allocation, service, return, invoice, payment,
    execution, or settlement authority.
    """

    case_matter_id: str = Field(min_length=1)
    matter_reference: str = Field(min_length=1)
    case_opened_at: datetime
    matter_evidence_reference: str = Field(min_length=1)
    instruction_id: str = Field(min_length=1)
    instruction_registered_at: datetime
    instruction_evidence_reference: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    document_type: str = Field(min_length=1)
    document_registered_at: datetime
    document_registration_evidence_reference: str = Field(min_length=1)
    registration_custody_event_id: str = Field(min_length=1)


class AcceptanceReceiptCommand(_CommandModel):
    """Bounded L8-3 acceptance/office-receipt evidence; tenant is server-derived.

    The body may identify the instruction, document, canonical SheriffOffice,
    explicit acceptance/receipt timestamps, evidence references, and the
    sequence-two custody event identity. It cannot supply tenant authority,
    allocation, service, return, invoice, payment, execution, or settlement truth.
    """

    instruction_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    sheriff_office_id: str = Field(min_length=1)
    accepted_at: datetime
    acceptance_evidence_reference: str = Field(min_length=1)
    received_at: datetime
    receipt_evidence_reference: str = Field(min_length=1)
    receipt_custody_event_id: str = Field(min_length=1)


class DistrictProvisioningCommand(_CommandModel):
    """Bounded District facts; tenant authority is always server-derived."""

    district_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    jurisdiction_code: str = Field(min_length=1)
    evidence_reference: str = Field(min_length=1)


class SheriffOfficeProvisioningCommand(_CommandModel):
    """Bounded SheriffOffice facts under one canonical District identity."""

    sheriff_office_id: str = Field(min_length=1)
    district_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    evidence_reference: str = Field(min_length=1)


class DeputyProvisioningCommand(_CommandModel):
    """Bounded Deputy facts under one canonical SheriffOffice identity."""

    deputy_id: str = Field(min_length=1)
    sheriff_office_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    badge_reference: str = Field(min_length=1)
    evidence_reference: str = Field(min_length=1)


class DeputyPrincipalBindingCommand(_CommandModel):
    """Bounded sheriff-issued L8-6B identity-link request; tenant is server-derived.

    The command may identify the target principal and canonical Deputy plus the
    binding timestamp/reference. It cannot grant membership, roles, queue
    access, service authority, client identity, AI authority, or financial truth.
    """

    principal_id: str = Field(min_length=1)
    deputy_id: str = Field(min_length=1)
    bound_at: datetime
    evidence_reference: str = Field(min_length=1, max_length=512)


class AllocationCommand(_CommandModel):
    """Tenant-scoped P4A locators and operator observations only.

    P1/P3 identity, state, lineage, custody, and fingerprints are rehydrated
    or derived by the canonical allocation orchestrator; this model grants no
    lifecycle or financial authority and rejects extra fields.
    """

    instruction_evidence_identity: str = Field(min_length=1)
    document_evidence_identity: str = Field(min_length=1)
    district_evidence_identity: str = Field(min_length=1)
    sheriff_office_evidence_identity: str = Field(min_length=1)
    deputy_evidence_identity: str = Field(min_length=1)
    assignment_decision_id: str = Field(min_length=1)
    assignment_evidence_reference: str = Field(min_length=1)
    decided_at: datetime
    allocation_command_id: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)
    allocation_custody_event_id: str = Field(min_length=1)
    allocation_evidence_reference: str = Field(min_length=1)
    allocated_at: datetime


class AttemptCommand(_CommandModel):
    """Opaque P5B authority locator for creating an initial ALLOCATED attempt."""

    attempt_authority_id: str = Field(min_length=1)


class AttemptTransitionCommand(_CommandModel):
    """Opaque P2 snapshot locator plus field-evidence observation for P5D."""

    current_evidence_identity: str = Field(min_length=1)
    evidence_reference: str = Field(min_length=1)
    evidence_fingerprint: str = Field(min_length=128, max_length=128)
    occurred_at: datetime


class OutcomeCommand(_CommandModel):
    """Terminal outcome observation passed to P5E; execution is factory-derived."""

    current_evidence_identity: str = Field(min_length=1)
    outcome: ServiceAttemptState
    evidence_reference: str = Field(min_length=1)
    evidence_fingerprint: str = Field(min_length=128, max_length=128)
    occurred_at: datetime
    service_execution_id: str = Field(min_length=1)
    executed_at: datetime


class DeputyFieldObservationCommand(_CommandModel):
    """Bounded bound-Deputy observation; sequence lineage is server-derived."""

    current_evidence_identity: str = Field(min_length=1)
    device_id: str = Field(min_length=1, max_length=128)
    event_id: str = Field(min_length=1, max_length=128)
    occurred_at: datetime
    observation_reference: str = Field(min_length=1, max_length=512)


class DeputyFieldTransitionCommand(DeputyFieldObservationCommand):
    """Bounded ALLOCATED -> ATTEMPTED deputy observation."""


class DeputyFieldOutcomeCommand(DeputyFieldObservationCommand):
    """Bounded terminal deputy observation; P1 execution identity/time are server-owned."""

    outcome: ServiceAttemptState


class ReturnCommand(_CommandModel):
    """Opaque ServiceExecution locator and return observation passed to P5F."""

    execution_evidence_identity: str = Field(min_length=1)
    return_id: str = Field(min_length=1)
    generated_at: datetime


class CommandError(RuntimeError):
    """Bounded tenant-command failure with a stable code and hidden cause.

    The exception carries no legal, persistence, transaction, or financial
    authority; callers receive only the mapped HTTP projection.
    """

    def __init__(self, code: str, cause: BaseException | None = None) -> None:
        self.code = code
        super().__init__(code)
        if cause is not None:
            self.__cause__ = cause


def _collection(database: Any, name: str) -> Any:
    if database is None:
        raise CommandError("LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE")
    return database.get_collection(name)


def _db_handles() -> tuple[Any, Any]:
    """Resolve the configured Kernel client/database only when a command runs."""
    from tools.eos.kernel.db import get_client, get_database

    return get_client(), get_database()


def _source(collection: Any, tenant: str, identity: str, expected: type[_T], session: Any) -> _T:
    value = LegalOperationsLifecycleRegistry.get(tenant, identity, collection, session=session)
    if type(value) is not expected:
        raise CommandError("LEGAL_OPERATIONS_SOURCE_TYPE_INVALID")
    return cast(_T, value)


def _digest(payload: object) -> str:
    """Return deterministic lowercase SHA3-512 for server-owned field composition."""
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _utcnow() -> datetime:
    """Return one timezone-aware server acceptance timestamp."""
    return datetime.now(timezone.utc)


def _bound_deputy(
    context: TenantAuthorizationContext,
    database: Any,
    session: Any,
    *,
    required: bool,
) -> Any | None:
    """Resolve immutable deputy binding after current IAM; never grant authority."""
    if context.decision.business_role != _DEPUTY_BUSINESS_ROLE:
        if required:
            raise CommandError("LEGAL_OPERATIONS_DEPUTY_COMMAND_REQUIRED")
        return None
    return DeputyPrincipalBindingRegistry.resolve_by_principal(
        context.tenant_id,
        context.identity.identity_id,
        _collection(database, DEPUTY_PRINCIPAL_BINDING_COLLECTION),
        session=session,
    )


def _enforce_deputy_attempt_scope(
    context: TenantAuthorizationContext,
    current: ServiceAttempt,
    database: Any,
    session: Any,
    *,
    required: bool,
) -> Any | None:
    """Require exact bound-deputy ownership when the actor is or must be a deputy."""
    binding = _bound_deputy(context, database, session, required=required)
    if binding is None:
        return None
    if current.deputy_id != binding.deputy_id:
        raise CommandError("LEGAL_OPERATION_NOT_FOUND")
    return binding


def _field_observation_provenance(
    *,
    context: TenantAuthorizationContext,
    current: ServiceAttempt,
    command_kind: str,
    current_evidence_identity: str,
    device_id: str,
    event_id: str,
    sequence_number: int,
    occurred_at: datetime,
    observation_reference: str,
    previous_event_fingerprint: str | None,
    outcome: ServiceAttemptState | None = None,
) -> tuple[str, str]:
    """Canonicalize one browser observation into server-owned opaque provenance."""
    payload = {
        "schema": _FIELD_OBSERVATION_SCHEMA,
        "tenant_id": context.tenant_id,
        "principal_id": context.identity.identity_id,
        "deputy_id": current.deputy_id,
        "attempt_id": current.attempt_id,
        "source_attempt_fingerprint": current.fingerprint,
        "current_evidence_identity": current_evidence_identity,
        "command_kind": command_kind,
        "device_id": device_id,
        "event_id": event_id,
        "sequence_number": sequence_number,
        "occurred_at": occurred_at.isoformat(),
        "observation_reference": observation_reference,
        "previous_event_fingerprint": previous_event_fingerprint,
        "outcome": outcome.value if outcome is not None else None,
    }
    return observation_reference, _digest(payload)


def _field_receipt_id(tenant_id: str, event_id: str) -> str:
    """Derive one stable server-owned P5M receipt locator for an immutable event."""
    return _digest(
        {
            "schema": _FIELD_RECEIPT_SCHEMA,
            "tenant_id": tenant_id,
            "event_id": event_id,
        }
    )


def _field_service_execution_id(
    *,
    tenant_id: str,
    attempt_id: str,
    evidence_identity: str,
    outcome: ServiceAttemptState,
) -> str:
    """Derive one stable P1 execution locator from accepted terminal field evidence."""
    return _digest(
        {
            "schema": _FIELD_EXECUTION_SCHEMA,
            "tenant_id": tenant_id,
            "attempt_id": attempt_id,
            "field_evidence_identity": evidence_identity,
            "outcome": outcome.value,
        }
    )


def _sync_bound_deputy_field_evidence(
    *,
    context: TenantAuthorizationContext,
    current: ServiceAttempt,
    command: DeputyFieldObservationCommand,
    command_kind: str,
    outcome: ServiceAttemptState | None,
    database: Any,
    session: Any,
) -> Any:
    """Synchronize one observation with server-owned P5M sequence lineage."""
    journal = _collection(database, FIELD_EVIDENCE_COLLECTION)
    try:
        replay_command, replay_receipt = (
            ProcessServiceFieldEvidenceRegistry.resolve_command_receipt_by_event(
                context.tenant_id,
                command.event_id,
                journal,
                session=session,
            )
        )
    except ProcessServiceFieldEvidenceRegistryError as error:
        if error.code != "P5M_EVIDENCE_NOT_FOUND":
            raise
        head = ProcessServiceFieldEvidenceRegistry.resolve_latest_for_attempt_device(
            context.tenant_id,
            current.attempt_id,
            command.device_id,
            journal,
            session=session,
        )
        sequence_number = 1 if head is None else head.sequence_number + 1
        previous_event_fingerprint = (
            None if head is None else head.evidence_fingerprint
        )
        receipt_id = _field_receipt_id(context.tenant_id, command.event_id)
        accepted_at = _utcnow()
    else:
        if (
            replay_command.attempt_id != current.attempt_id
            or replay_command.device_id != command.device_id
            or replay_command.occurred_at != command.occurred_at
            or replay_command.evidence_reference != command.observation_reference
        ):
            raise ProcessServiceFieldEvidenceRegistryError("P5M_REPLAY_CONFLICT")
        sequence_number = replay_command.sequence_number
        previous_event_fingerprint = replay_command.previous_event_fingerprint
        receipt_id = replay_receipt.receipt_id
        accepted_at = replay_receipt.accepted_at

    evidence_reference, evidence_fingerprint = _field_observation_provenance(
        context=context,
        current=current,
        command_kind=command_kind,
        current_evidence_identity=command.current_evidence_identity,
        device_id=command.device_id,
        event_id=command.event_id,
        sequence_number=sequence_number,
        occurred_at=command.occurred_at,
        observation_reference=command.observation_reference,
        previous_event_fingerprint=previous_event_fingerprint,
        outcome=outcome,
    )
    if "replay_command" in locals() and (
        replay_command.evidence_reference != evidence_reference
        or replay_command.evidence_fingerprint != evidence_fingerprint
        or replay_command.previous_event_fingerprint != previous_event_fingerprint
        or replay_command.sequence_number != sequence_number
    ):
        raise ProcessServiceFieldEvidenceRegistryError("P5M_REPLAY_CONFLICT")

    return sync_offline_field_evidence(
        tenant_id=context.tenant_id,
        attempt_evidence_identity=command.current_evidence_identity,
        device_id=command.device_id,
        event_id=command.event_id,
        sequence_number=sequence_number,
        occurred_at=command.occurred_at,
        evidence_reference=evidence_reference,
        evidence_fingerprint=evidence_fingerprint,
        previous_event_fingerprint=previous_event_fingerprint,
        receipt_id=receipt_id,
        accepted_at=accepted_at,
        lifecycle_collection=_collection(database, LIFECYCLE_COLLECTION),
        allocation_receipt_collection=_collection(database, ALLOCATION_RECEIPT_COLLECTION),
        allocation_current_collection=_collection(database, ALLOCATION_CURRENT_COLLECTION),
        journal_collection=journal,
        session=session,
    )


def _prior_custody(collection: Any, tenant: str, document_id: str, session: Any) -> tuple[Any, ...]:
    """Return canonical P2-hydrated custody history for allocation composition."""
    events = list(
        LegalOperationsLifecycleRegistry.get_document_custody_history(
            tenant,
            document_id,
            collection,
            session=session,
        )
    )
    events.sort(key=lambda event: event.sequence_number)
    return tuple(events)


def _transaction(callback: Callable[[Any, Any], _T]) -> _T:
    """Run one command in one API-owned session/transaction."""
    client, database = _db_handles()
    if client is None or database is None:
        raise CommandError("LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE")
    try:
        with client.start_session() as session:
            session.start_transaction()
            try:
                result = callback(session, database)
                session.commit_transaction()
                return result
            except Exception:
                if bool(getattr(session, "in_transaction", False)):
                    session.abort_transaction()
                raise
    except (
        CommandError,
        ProcessServiceDirectoryProvisioningError,
        ProcessServiceIntakeRegistrationError,
        ProcessServiceAcceptanceReceiptError,
        DeputyPrincipalBindingOrchestrationError,
        DeputyPrincipalBindingRegistryError,
        ProcessServiceFieldEvidenceAuthorityError,
        ProcessServiceFieldEvidenceOrchestratorError,
        ProcessServiceFieldEvidenceRegistryError,
    ):
        raise
    except Exception as error:
        raise CommandError("LEGAL_OPERATIONS_COMMAND_FAILED", error) from error


def _http_error(error: BaseException) -> HTTPException:
    if isinstance(error, CommandError):
        code = error.code
    else:
        code = getattr(error, "code", "LEGAL_OPERATIONS_COMMAND_FAILED")
    if not isinstance(code, str):
        code = "LEGAL_OPERATIONS_COMMAND_FAILED"
    if code in {"M2_RETRY_TRANSACTION_REQUIRED", "P4_WHOLE_TRANSACTION_RETRY_REQUIRED", "P5B_RETRY_REQUIRED", "P5M_RETRY_TRANSACTION_REQUIRED"}:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="LEGAL_OPERATIONS_RETRY_REQUIRED")
    if code == "P5M_REPLAY_CONFLICT":
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="LEGAL_OPERATIONS_FIELD_EVIDENCE_CONFLICT")
    if code == "L8_6B_BINDING_CONFLICT":
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="LEGAL_OPERATIONS_DEPUTY_BINDING_CONFLICT")
    if code in {"L8_6B_BINDING_NOT_FOUND", "LEGAL_OPERATIONS_DEPUTY_COMMAND_REQUIRED"}:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="DEPUTY_IDENTITY_BINDING_REQUIRED")
    if code.endswith("NOT_FOUND") or code in {"P5B_RECEIPT_NOT_FOUND", "P4_RECEIPT_NOT_FOUND", "P4_CURRENT_POINTER_MISSING"}:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LEGAL_OPERATION_NOT_FOUND")
    if "TRANSACTION_REQUIRED" in code or "PERSISTENCE_UNAVAILABLE" in code or "PERSISTED_RECORD_INVALID" in code or "COMMAND_FAILED" in code:
        return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LEGAL_OPERATIONS_UNAVAILABLE")
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="LEGAL_OPERATIONS_COMMAND_INVALID")


def _ctx(permission: str, operation: str) -> RequireTenantAuthorization:
    return RequireTenantAuthorization(permission, operation)


_INTAKE = _ctx("legal_operations:instruction:write", "legal_instruction_write")
_RECEIPT = _ctx("legal_operations:receipt:write", "legal_receipt_write")
_DIRECTORY = _ctx("legal_operations:directory:write", "legal_directory_write")
_ALLOCATE = _ctx("legal_operations:allocation:write", "legal_allocation_write")
_ATTEMPT = _ctx("legal_operations:attempt:write", "legal_attempt_write")
_OUTCOME = _ctx("legal_operations:attempt_outcome:write", "legal_attempt_outcome_write")
_RETURN = _ctx("legal_operations:return:write", "legal_return_write")


@router.post("/intake/registrations")
async def register_process_service_intake_command(
    command: IntakeRegistrationCommand,
    context: TenantAuthorizationContext = Depends(_INTAKE),
) -> dict[str, Any]:
    """Register or exactly replay one own-tenant initial process-service intake.

    Tenant scope is derived exclusively from the authorization context. The API
    owns the transaction; L8-2 owns registration composition and preserves the
    distinction between registration, acceptance, receipt, allocation, service,
    and all financial states.
    """

    def run(session: Any, db: Any) -> Any:
        return register_process_service_intake(
            tenant_id=context.tenant_id,
            case_matter_id=command.case_matter_id,
            matter_reference=command.matter_reference,
            case_opened_at=command.case_opened_at,
            matter_evidence_reference=command.matter_evidence_reference,
            instruction_id=command.instruction_id,
            instruction_registered_at=command.instruction_registered_at,
            instruction_evidence_reference=command.instruction_evidence_reference,
            document_id=command.document_id,
            document_type=command.document_type,
            document_registered_at=command.document_registered_at,
            document_registration_evidence_reference=(
                command.document_registration_evidence_reference
            ),
            registration_custody_event_id=command.registration_custody_event_id,
            lifecycle_collection=_collection(db, LIFECYCLE_COLLECTION),
            session=session,
        )

    try:
        result = _transaction(run)
    except Exception as error:
        raise _http_error(error) from error
    return result.to_dict()


@router.post("/intake/acceptance-receipts")
async def accept_and_receive_process_service_command(
    command: AcceptanceReceiptCommand,
    context: TenantAuthorizationContext = Depends(_RECEIPT),
) -> dict[str, Any]:
    """Accept one instruction and record linked physical sheriff-office receipt.

    Tenant scope comes only from the authorization context. L8-3 rehydrates
    canonical instruction/document/office/custody truth, derives ACCEPTED,
    RECEIVED, and RECEIVED_IN_OFFICE facts, and rejects partial/divergent
    evidence without creating allocation, service, or financial authority.
    """

    def run(session: Any, db: Any) -> Any:
        return accept_instruction_and_receive_document(
            tenant_id=context.tenant_id,
            instruction_id=command.instruction_id,
            document_id=command.document_id,
            sheriff_office_id=command.sheriff_office_id,
            accepted_at=command.accepted_at,
            acceptance_evidence_reference=command.acceptance_evidence_reference,
            received_at=command.received_at,
            receipt_evidence_reference=command.receipt_evidence_reference,
            receipt_custody_event_id=command.receipt_custody_event_id,
            lifecycle_collection=_collection(db, LIFECYCLE_COLLECTION),
            session=session,
        )

    try:
        result = _transaction(run)
    except Exception as error:
        raise _http_error(error) from error
    return result.to_dict()


@router.post("/directory/districts")
async def provision_district_command(
    command: DistrictProvisioningCommand,
    context: TenantAuthorizationContext = Depends(_DIRECTORY),
) -> dict[str, Any]:
    """Provision or exactly replay one own-tenant canonical District."""

    def run(session: Any, db: Any) -> Any:
        return provision_district(
            tenant_id=context.tenant_id,
            district_id=command.district_id,
            name=command.name,
            jurisdiction_code=command.jurisdiction_code,
            evidence_reference=command.evidence_reference,
            lifecycle_collection=_collection(db, LIFECYCLE_COLLECTION),
            session=session,
        )

    try:
        result = _transaction(run)
    except Exception as error:
        raise _http_error(error) from error
    return result.to_dict()


@router.post("/directory/sheriff-offices")
async def provision_sheriff_office_command(
    command: SheriffOfficeProvisioningCommand,
    context: TenantAuthorizationContext = Depends(_DIRECTORY),
) -> dict[str, Any]:
    """Provision or exactly replay one own-tenant SheriffOffice under P1/P2 truth."""

    def run(session: Any, db: Any) -> Any:
        return provision_sheriff_office(
            tenant_id=context.tenant_id,
            sheriff_office_id=command.sheriff_office_id,
            district_id=command.district_id,
            name=command.name,
            evidence_reference=command.evidence_reference,
            lifecycle_collection=_collection(db, LIFECYCLE_COLLECTION),
            session=session,
        )

    try:
        result = _transaction(run)
    except Exception as error:
        raise _http_error(error) from error
    return result.to_dict()


@router.post("/directory/deputies")
async def provision_deputy_command(
    command: DeputyProvisioningCommand,
    context: TenantAuthorizationContext = Depends(_DIRECTORY),
) -> dict[str, Any]:
    """Provision or exactly replay one own-tenant Deputy under canonical office lineage."""

    def run(session: Any, db: Any) -> Any:
        return provision_deputy(
            tenant_id=context.tenant_id,
            deputy_id=command.deputy_id,
            sheriff_office_id=command.sheriff_office_id,
            display_name=command.display_name,
            badge_reference=command.badge_reference,
            evidence_reference=command.evidence_reference,
            lifecycle_collection=_collection(db, LIFECYCLE_COLLECTION),
            session=session,
        )

    try:
        result = _transaction(run)
    except Exception as error:
        raise _http_error(error) from error
    return result.to_dict()


@router.post("/directory/deputy-principal-bindings")
async def bind_deputy_principal_command(
    command: DeputyPrincipalBindingCommand,
    context: TenantAuthorizationContext = Depends(_DIRECTORY),
) -> dict[str, object]:
    """Bind one active deputy principal to one canonical Deputy identity.

    Actor admission uses the existing sheriff-only directory authority. Tenant
    scope comes only from the authorized context. L8-6B independently proves
    the target principal's current ACTIVE principal/membership truth,
    tenant_deputy business role, DEPUTY authorization assignment, and exact
    canonical Deputy evidence under the same API-owned transaction before the
    immutable one-to-one binding is persisted or exactly replayed.

    Binding creation grants no queue, attempt, service, return, billing,
    payment, AI, execution, or settlement authority.
    """

    def run(session: Any, db: Any) -> Any:
        return bind_deputy_principal_identity(
            tenant_id=context.tenant_id,
            principal_id=command.principal_id,
            deputy_id=command.deputy_id,
            bound_at=command.bound_at,
            evidence_reference=command.evidence_reference,
            lifecycle_collection=_collection(db, LIFECYCLE_COLLECTION),
            binding_collection=_collection(
                db,
                DEPUTY_PRINCIPAL_BINDING_COLLECTION,
            ),
            principal_collection=_collection(db, PRINCIPAL_AUTHORITY_COLLECTION),
            membership_collection=_collection(db, TENANT_MEMBERSHIP_COLLECTION),
            business_role_collection=_collection(
                db,
                TENANT_BUSINESS_ROLE_COLLECTION,
            ),
            role_assignment_collection=_collection(
                db,
                ROLE_ASSIGNMENT_COLLECTION,
            ),
            session=session,
        )

    try:
        value = _transaction(run)
    except Exception as error:
        raise _http_error(error) from error
    return value.to_dict()


@router.post("/allocations")
async def allocate_process_service(command: AllocationCommand, context: TenantAuthorizationContext = Depends(_ALLOCATE)) -> dict[str, Any]:
    """Authorize and execute exactly one P4A allocation command."""
    def run(session: Any, db: Any) -> Any:
        lifecycle = _collection(db, LIFECYCLE_COLLECTION)
        instruction = _source(lifecycle, context.tenant_id, command.instruction_evidence_identity, LegalInstruction, session)
        document = _source(lifecycle, context.tenant_id, command.document_evidence_identity, ProcessDocument, session)
        district = _source(lifecycle, context.tenant_id, command.district_evidence_identity, District, session)
        office = _source(lifecycle, context.tenant_id, command.sheriff_office_evidence_identity, SheriffOffice, session)
        deputy = _source(lifecycle, context.tenant_id, command.deputy_evidence_identity, Deputy, session)
        assignment = authorize_process_service_assignment(instruction=instruction, document=document, district=district, sheriff_office=office, deputy=deputy, assignment_decision_id=command.assignment_decision_id, assignment_evidence_reference=command.assignment_evidence_reference, decided_at=command.decided_at)
        current = ProcessServiceAllocationRegistry.get_current(context.tenant_id, document.document_id, _collection(db, ALLOCATION_CURRENT_COLLECTION), session=session)
        result = orchestrate_process_service_allocation(instruction=instruction, document=document, district=district, sheriff_office=office, deputy=deputy, assignment_decision=assignment, prior_custody_events=_prior_custody(lifecycle, context.tenant_id, document.document_id, session), expected_prior_current=current, allocation_command_id=command.allocation_command_id, idempotency_key=command.idempotency_key, allocation_custody_event_id=command.allocation_custody_event_id, allocation_evidence_reference=command.allocation_evidence_reference, allocated_at=command.allocated_at, lifecycle_collection=lifecycle, allocation_receipt_collection=_collection(db, ALLOCATION_RECEIPT_COLLECTION), allocation_current_collection=_collection(db, ALLOCATION_CURRENT_COLLECTION), session=session)
        return result.allocated_document
    try:
        value = _transaction(run)
    except Exception as error:
        raise _http_error(error) from error
    return {"data": value.to_dict()}


@router.post("/attempts")
async def create_process_service_attempt(command: AttemptCommand, context: TenantAuthorizationContext = Depends(_ATTEMPT)) -> dict[str, Any]:
    """Create only the initial P1 ALLOCATED attempt through P5C."""
    def run(session: Any, db: Any) -> Any:
        return orchestrate_process_service_attempt(
            tenant_id=context.tenant_id,
            attempt_authority_id=command.attempt_authority_id,
            attempt_authority_collection=_collection(db, ATTEMPT_AUTHORITY_COLLECTION),
            lifecycle_collection=_collection(db, LIFECYCLE_COLLECTION),
            session=session,
        )
    try:
        value = _transaction(run)
    except Exception as error:
        raise _http_error(error) from error
    return {"data": value.to_dict()}


@router.post("/attempts/{attempt_id}/transition")
async def transition_process_service_attempt_command(attempt_id: str, command: AttemptTransitionCommand, context: TenantAuthorizationContext = Depends(_ATTEMPT)) -> dict[str, Any]:
    """Persist one P5D ALLOCATED -> ATTEMPTED transition."""
    if not attempt_id.strip():
        raise HTTPException(status_code=422, detail="LEGAL_OPERATIONS_COMMAND_INVALID")
    def run(session: Any, db: Any) -> Any:
        lifecycle = _collection(db, LIFECYCLE_COLLECTION)
        current = _source(lifecycle, context.tenant_id, command.current_evidence_identity, ServiceAttempt, session)
        if current.attempt_id != attempt_id:
            raise CommandError("LEGAL_OPERATION_NOT_FOUND")
        _enforce_deputy_attempt_scope(
            context,
            current,
            db,
            session,
            required=False,
        )
        return transition_process_service_attempt(
            tenant_id=context.tenant_id,
            current_evidence_identity=command.current_evidence_identity,
            lifecycle_collection=lifecycle,
            transition_collection=_collection(db, TRANSITION_COLLECTION),
            evidence_reference=command.evidence_reference,
            evidence_fingerprint=command.evidence_fingerprint,
            occurred_at=command.occurred_at,
            session=session,
        )
    try:
        value = _transaction(run)
    except Exception as error:
        raise _http_error(error) from error
    return {"data": value.to_dict()}


@router.post("/attempts/{attempt_id}/outcome")
async def record_process_service_outcome_command(attempt_id: str, command: OutcomeCommand, context: TenantAuthorizationContext = Depends(_OUTCOME)) -> dict[str, Any]:
    """Persist one P5E terminal outcome and derive ServiceExecution."""
    if command.outcome not in {ServiceAttemptState.COMPLETED, ServiceAttemptState.NOT_COMPLETED}:
        raise HTTPException(status_code=422, detail="LEGAL_OPERATIONS_TERMINAL_OUTCOME_REQUIRED")
    def run(session: Any, db: Any) -> Any:
        lifecycle = _collection(db, LIFECYCLE_COLLECTION)
        current = _source(lifecycle, context.tenant_id, command.current_evidence_identity, ServiceAttempt, session)
        if current.attempt_id != attempt_id:
            raise CommandError("LEGAL_OPERATION_NOT_FOUND")
        _enforce_deputy_attempt_scope(
            context,
            current,
            db,
            session,
            required=False,
        )
        return transition_process_service_attempt_outcome(
            tenant_id=context.tenant_id,
            current_evidence_identity=command.current_evidence_identity,
            lifecycle_collection=lifecycle,
            outcome_collection=_collection(db, OUTCOME_COLLECTION),
            outcome=command.outcome,
            evidence_reference=command.evidence_reference,
            evidence_fingerprint=command.evidence_fingerprint,
            occurred_at=command.occurred_at,
            service_execution_id=command.service_execution_id,
            executed_at=command.executed_at,
            session=session,
        )
    try:
        value = _transaction(run)
    except Exception as error:
        raise _http_error(error) from error
    return {"data": value.to_dict()}


@router.post("/deputy/attempts/{attempt_id}/transition")
async def transition_bound_deputy_field_attempt_command(
    attempt_id: str,
    command: DeputyFieldTransitionCommand,
    context: TenantAuthorizationContext = Depends(_ATTEMPT),
) -> dict[str, Any]:
    """Atomically journal one bound-Deputy field observation and persist ATTEMPTED."""
    if not attempt_id.strip():
        raise HTTPException(status_code=422, detail="LEGAL_OPERATIONS_COMMAND_INVALID")

    def run(session: Any, db: Any) -> tuple[Any, Any]:
        lifecycle = _collection(db, LIFECYCLE_COLLECTION)
        current = _source(
            lifecycle,
            context.tenant_id,
            command.current_evidence_identity,
            ServiceAttempt,
            session,
        )
        if current.attempt_id != attempt_id:
            raise CommandError("LEGAL_OPERATION_NOT_FOUND")
        _enforce_deputy_attempt_scope(
            context,
            current,
            db,
            session,
            required=True,
        )
        receipt = _sync_bound_deputy_field_evidence(
            context=context,
            current=current,
            command=command,
            command_kind="TRANSITION_TO_ATTEMPTED",
            outcome=None,
            database=db,
            session=session,
        )
        attempted = transition_process_service_attempt(
            tenant_id=context.tenant_id,
            current_evidence_identity=command.current_evidence_identity,
            lifecycle_collection=lifecycle,
            transition_collection=_collection(db, TRANSITION_COLLECTION),
            evidence_reference=receipt.evidence_reference,
            evidence_fingerprint=receipt.evidence_fingerprint,
            occurred_at=command.occurred_at,
            session=session,
        )
        return attempted, receipt

    try:
        value, receipt = _transaction(run)
    except Exception as error:
        raise _http_error(error) from error
    return {"data": value.to_dict(), "field_evidence": receipt.to_dict()}


@router.post("/deputy/attempts/{attempt_id}/outcome")
async def record_bound_deputy_field_outcome_command(
    attempt_id: str,
    command: DeputyFieldOutcomeCommand,
    context: TenantAuthorizationContext = Depends(_OUTCOME),
) -> dict[str, Any]:
    """Atomically journal one bound-Deputy terminal observation and derive P1 execution."""
    if command.outcome not in {
        ServiceAttemptState.COMPLETED,
        ServiceAttemptState.NOT_COMPLETED,
    }:
        raise HTTPException(
            status_code=422,
            detail="LEGAL_OPERATIONS_TERMINAL_OUTCOME_REQUIRED",
        )

    def run(session: Any, db: Any) -> tuple[Any, Any]:
        lifecycle = _collection(db, LIFECYCLE_COLLECTION)
        current = _source(
            lifecycle,
            context.tenant_id,
            command.current_evidence_identity,
            ServiceAttempt,
            session,
        )
        if current.attempt_id != attempt_id:
            raise CommandError("LEGAL_OPERATION_NOT_FOUND")
        _enforce_deputy_attempt_scope(
            context,
            current,
            db,
            session,
            required=True,
        )
        receipt = _sync_bound_deputy_field_evidence(
            context=context,
            current=current,
            command=command,
            command_kind=f"RECORD_{command.outcome.value}_OUTCOME",
            outcome=command.outcome,
            database=db,
            session=session,
        )
        execution_id = _field_service_execution_id(
            tenant_id=context.tenant_id,
            attempt_id=current.attempt_id,
            evidence_identity=receipt.evidence_identity,
            outcome=command.outcome,
        )
        execution = transition_process_service_attempt_outcome(
            tenant_id=context.tenant_id,
            current_evidence_identity=command.current_evidence_identity,
            lifecycle_collection=lifecycle,
            outcome_collection=_collection(db, OUTCOME_COLLECTION),
            outcome=command.outcome,
            evidence_reference=receipt.evidence_reference,
            evidence_fingerprint=receipt.evidence_fingerprint,
            occurred_at=command.occurred_at,
            service_execution_id=execution_id,
            executed_at=command.occurred_at,
            session=session,
        )
        return execution, receipt

    try:
        value, receipt = _transaction(run)
    except Exception as error:
        raise _http_error(error) from error
    return {"data": value.to_dict(), "field_evidence": receipt.to_dict()}


@router.post("/executions/{execution_id}/return")
async def generate_return_of_service_command(execution_id: str, command: ReturnCommand, context: TenantAuthorizationContext = Depends(_RETURN)) -> dict[str, Any]:
    """Generate one P5F ReturnOfService from canonical ServiceExecution."""
    def run(session: Any, db: Any) -> Any:
        lifecycle = _collection(db, LIFECYCLE_COLLECTION)
        execution = _source(lifecycle, context.tenant_id, command.execution_evidence_identity, ServiceExecution, session)
        if execution.service_execution_id != execution_id:
            raise CommandError("LEGAL_OPERATION_NOT_FOUND")
        return generate_process_service_return(
            tenant_id=context.tenant_id,
            execution_evidence_identity=command.execution_evidence_identity,
            lifecycle_collection=lifecycle,
            return_collection=_collection(db, RETURN_COLLECTION),
            return_id=command.return_id,
            generated_at=command.generated_at,
            session=session,
        )
    try:
        value = _transaction(run)
    except Exception as error:
        raise _http_error(error) from error
    return {"data": value.to_dict()}


__all__ = ["VERSION", "router", "CommandError"]

# ARTIFACT: legal_operations_command_router.py
# VERSION: v1.6.0-L8-6G-SERVER-OWNED-FIELD-SEQUENCE
# AUTHORITY BOUNDARY: authenticated intake/receipt/directory/deputy-binding/field-service composition; bound-Deputy field commands canonicalize transport observations while P1/P2/L8-1/L8-2/L8-3/L8-6B/P4/P5 remain canonical
# TENANT POSTURE: explicit authorized tenant scope on every source and write
# FAIL-CLOSED POSTURE: malformed, unauthorized, divergent, and ambiguous commands reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns financial execution and settlement
# END OF WILSY OS SOVEREIGN ARTIFACT