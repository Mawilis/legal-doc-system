"""WILSY OS Legal Operations command boundary.

TITLE: Legal Operations Command API
VERSION: v1.2.0-L8-2-LEGAL-OPERATIONS-INTAKE-COMMAND-API
AUTHORITY: HTTP command composition only; P1/P2/L8-1/L8-2/P4/P5 remain canonical authorities.
EPITOME: Translate authenticated tenant-scoped intake, directory, and
         field-service commands into one canonical orchestrator inside one
         API-owned Mongo transaction, without accepting browser-supplied tenant
         authority or collapsing registration into receipt/allocation/service truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/legal_operations_command_router.py
COLLABORATION / OWNERSHIP: API composition owns transport and transaction
                           mechanics; domain/registry/orchestrator modules own
                           lifecycle, evidence, and persistence truth.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: v1.2.0-L8-2-LEGAL-OPERATIONS-INTAKE-COMMAND-API adds one
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
                            directory facts, locators, and observations; tenant
                            authority comes only from durable authorization and
                            canonical domain/orchestrator layers own lifecycle,
                            lineage, fingerprints, and outcome truth.
TENANT BOUNDARY: X-Tenant-ID from RequireTenantAuthorization is the only
                 request scope; every Mongo query includes that tenant.
AUTHORITY BOUNDARY: This module composes authenticated command transport and
                    transaction mechanics only; exactly one canonical intake,
                    directory, or field-service orchestrator is called per command.
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

from datetime import datetime
from enum import StrEnum
from typing import Any, Callable, Final, TypeVar, cast

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization, TenantAuthorizationContext
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
from tools.eos.legal_operations.orchestration.process_service_attempt_orchestrator import orchestrate_process_service_attempt
from tools.eos.legal_operations.orchestration.process_service_attempt_outcome_orchestrator import transition_process_service_attempt_outcome
from tools.eos.legal_operations.orchestration.process_service_attempt_transition_orchestrator import transition_process_service_attempt
from tools.eos.legal_operations.orchestration.process_service_return_orchestrator import generate_process_service_return
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import COLLECTION as LIFECYCLE_COLLECTION, LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ALLOCATION_CURRENT_COLLECTION,
    ALLOCATION_RECEIPT_COLLECTION,
    ProcessServiceAllocationRegistry,
)
from tools.eos.legal_operations.registry.process_service_attempt_authority_registry import RECEIPT_COLLECTION as ATTEMPT_AUTHORITY_COLLECTION
from tools.eos.legal_operations.registry.process_service_attempt_outcome_registry import COLLECTION as OUTCOME_COLLECTION
from tools.eos.legal_operations.registry.process_service_attempt_transition_registry import COLLECTION as TRANSITION_COLLECTION
from tools.eos.legal_operations.registry.process_service_return_registry import COLLECTION as RETURN_COLLECTION


VERSION: Final[str] = "v1.2.0-L8-2-LEGAL-OPERATIONS-INTAKE-COMMAND-API"
router = APIRouter(prefix="/legal-operations", tags=["Legal Operations Commands"])
_T = TypeVar("_T")


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


def _prior_custody(collection: Any, tenant: str, document_id: str, session: Any) -> tuple[Any, ...]:
    """Hydrate the complete received custody prefix; never infer latest state."""
    rows = collection.find(
        {"tenant_id": tenant, "entity_type": "DocumentCustodyEvent", "p1_payload.document_id": document_id},
        session=session,
    )
    events: list[Any] = []
    for row in rows:
        identity = row.get("evidence_identity") if isinstance(row, dict) else None
        if not isinstance(identity, str):
            raise CommandError("LEGAL_OPERATIONS_CUSTODY_EVIDENCE_INVALID")
        events.append(LegalOperationsLifecycleRegistry.get(tenant, identity, collection, session=session))
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
    if code in {"M2_RETRY_TRANSACTION_REQUIRED", "P4_WHOLE_TRANSACTION_RETRY_REQUIRED", "P5B_RETRY_REQUIRED"}:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="LEGAL_OPERATIONS_RETRY_REQUIRED")
    if code.endswith("NOT_FOUND") or code in {"P5B_RECEIPT_NOT_FOUND", "P4_RECEIPT_NOT_FOUND", "P4_CURRENT_POINTER_MISSING"}:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LEGAL_OPERATION_NOT_FOUND")
    if "TRANSACTION_REQUIRED" in code or "PERSISTENCE_UNAVAILABLE" in code or "COMMAND_FAILED" in code:
        return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LEGAL_OPERATIONS_UNAVAILABLE")
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="LEGAL_OPERATIONS_COMMAND_INVALID")


def _ctx(permission: str, operation: str) -> RequireTenantAuthorization:
    return RequireTenantAuthorization(permission, operation)


_INTAKE = _ctx("legal_operations:instruction:write", "legal_instruction_write")
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
# VERSION: v1.2.0-L8-2-LEGAL-OPERATIONS-INTAKE-COMMAND-API
# AUTHORITY BOUNDARY: authenticated intake/directory/field-service command composition; P1/P2/L8-1/L8-2/P4/P5 remain canonical
# TENANT POSTURE: explicit authorized tenant scope on every source and write
# FAIL-CLOSED POSTURE: malformed, unauthorized, divergent, and ambiguous commands reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns financial execution and settlement
# END OF WILSY OS SOVEREIGN ARTIFACT