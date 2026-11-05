"""Authenticated tenant self-service and SYSTEM support-case API routes.

Tenant self-service derives the principal from EOS ACCESS-token verification,
treats X-Tenant-ID only as a requested scope, and revalidates ACTIVE principal
plus exact ACTIVE membership in the same caller-owned Mongo transaction as
each case or incident read/write. Tenant users can access only their own
records. SYSTEM operations independently re-prove current SYSTEM assignment
and active PLATFORM workforce evidence in the same transaction. Incident
intake is append-only and grants no containment, recovery, or account-action
authority.
"""
from __future__ import annotations

from typing import Annotated, Callable, TypeVar, cast
from datetime import datetime, timezone
from hashlib import sha3_256

from pymongo.client_session import ClientSession

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr

from tools.eos.auth.authentication import get_current_identity
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.system_services.eos_authorizer import (
    SystemServicesAuthorizationError,
    SystemServicesAuthorizationUnavailable,
)
from tools.eos.system_services.support_case import (
    SupportCaseCategory,
    SupportCaseScope,
    SupportCaseStatus,
)
from tools.eos.system_services.support_case_service import (
    SupportCaseActorContext,
    SupportCaseApplicationError,
    SupportCaseApplicationService,
    SystemServicesAuthorizer,
)
from tools.eos.system_services.security_incident import (
    SecurityIncident,
    SecurityIncidentCategory,
    SecurityIncidentEvent,
)
from tools.eos.system_services.security_incident_registry import (
    SecurityIncidentRegistry,
    SecurityIncidentConflictError,
    SecurityIncidentNotFoundError,
)
from tools.eos.system_services.security_incident_assignment import (
    SecurityIncidentAssignment,
)
from tools.eos.system_services.security_incident_assignment_registry import (
    SecurityIncidentAssignmentRegistry,
    IncidentAssignmentConflictError,
    IncidentAssignmentNotFoundError,
)
from tools.eos.system_services.security_incident_escalation_service import (
    SecurityIncidentEscalationService,
    SecurityIncidentEscalationError,
)
from tools.eos.system_services.security_incident_response_decision import (
    SecurityIncidentResponseAction,
    SecurityIncidentResponseDecision,
)
from tools.eos.system_services.security_incident_response_decision_registry import (
    SecurityIncidentResponseDecisionRegistry,
    SecurityIncidentResponseDecisionRegistryError,
    SecurityIncidentResponseDecisionConflictError,
)
from tools.eos.system_services.security_incident_response_decision_service import (
    SecurityIncidentResponseDecisionService,
    SecurityIncidentResponseDecisionServiceError,
)
from tools.eos.system_services.security_incident_response_execution import (
    SecurityIncidentResponseCanonicalExecutor,
    SecurityIncidentResponseExecutionError,
)
from tools.eos.auth.system_permission_assignment import SystemPermissionAssignmentStatus
from tools.eos.auth.system_permission_command_evidence import (
    SystemPermissionCommandEvidence,
    SystemPermissionCommandOperation,
)
from tools.eos.auth.system_permission_assignment_registry import (
    SystemPermissionAssignmentConflictError,
    SystemPermissionAssignmentNotFoundError,
    SystemPermissionAssignmentPersistedInvalidError,
    SystemPermissionAssignmentRegistry as CanonicalSystemPermissionAssignmentRegistry,
)
from tools.eos.auth.system_permission_revocation_command_service import (
    SystemPermissionRevocationCommandError,
)
from tools.eos.saas.auth.password_reset_service import (
    PasswordResetServiceError,
)
from tools.eos.system_services.support_case_registry import (
    SupportCaseConflictError,
    SupportCaseNotFoundError,
    SupportCaseRegistry,
)
from tools.eos.kernel.db import get_client

router = APIRouter(prefix="/system-services", tags=["System Services"])
_Result = TypeVar("_Result")


class CaseTransitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    next_status: SupportCaseStatus
    expected_revision: StrictInt = Field(ge=0)


def _actor(identity: SovereignIdentity) -> SupportCaseActorContext:
    """Discard tenant context: the exact SYSTEM authorization is independently re-proven."""
    if not isinstance(identity.identity_id, str) or not identity.identity_id.strip() or identity.status is not PrincipalStatus.ACTIVE:
        raise HTTPException(status_code=401, detail="Authenticated principal required.")
    return SupportCaseActorContext(
        principal_id=identity.identity_id,
        scope=SupportCaseScope.SYSTEM,
    )


def _runtime(request: Request) -> tuple[SupportCaseRegistry, SystemServicesAuthorizer]:
    if getattr(request.app.state, "system_services_case_indexes_ready", False) is not True:
        raise HTTPException(status_code=503, detail="System Services storage is not ready.")
    registry = getattr(request.app.state, "system_services_case_registry", None)
    authorizer = getattr(request.app.state, "system_services_authorizer", None)
    if type(registry) is not SupportCaseRegistry or not callable(getattr(authorizer, "require", None)):
        raise HTTPException(status_code=503, detail="System Services authority is not configured.")
    return registry, cast(SystemServicesAuthorizer, authorizer)


def _service(request: Request) -> SupportCaseApplicationService:
    registry, authorizer = _runtime(request)
    return SupportCaseApplicationService(registry=registry, authorizer=authorizer)


def _response_runtime(
    request: Request,
) -> tuple[
    SecurityIncidentResponseDecisionRegistry,
    SecurityIncidentResponseDecisionService,
    SecurityIncidentResponseCanonicalExecutor,
    CanonicalSystemPermissionAssignmentRegistry,
]:
    if getattr(request.app.state, "system_services_response_indexes_ready", False) is not True:
        raise HTTPException(status_code=503, detail="System Services response governance is not ready.")
    registry = getattr(request.app.state, "system_services_response_decision_registry", None)
    service = getattr(request.app.state, "system_services_response_decision_service", None)
    executor = getattr(request.app.state, "system_services_response_executor", None)
    assignments = getattr(request.app.state, "system_services_response_permission_assignments", None)
    if (
        type(registry) is not SecurityIncidentResponseDecisionRegistry
        or type(service) is not SecurityIncidentResponseDecisionService
        or type(executor) is not SecurityIncidentResponseCanonicalExecutor
        or type(assignments) is not CanonicalSystemPermissionAssignmentRegistry
    ):
        raise HTTPException(status_code=503, detail="System Services response authority is not configured.")
    return registry, service, executor, assignments


def _run_transaction(callback: Callable[[ClientSession], _Result]) -> _Result:
    client = get_client()
    if client is None:
        raise HTTPException(status_code=503, detail="System Services persistence is unavailable.")
    try:
        with client.start_session() as session:
            with session.start_transaction():
                return callback(session)
    except HTTPException:
        raise
    except SystemServicesAuthorizationError as error:
        raise HTTPException(status_code=403, detail="System Services access denied.") from error
    except SystemServicesAuthorizationUnavailable as error:
        raise HTTPException(status_code=503, detail="System Services authority is unavailable.") from error
    except (
        SupportCaseNotFoundError,
        IncidentAssignmentNotFoundError,
        SecurityIncidentNotFoundError,
        SystemPermissionAssignmentNotFoundError,
    ) as error:
        raise HTTPException(status_code=404, detail="System Services record not found.") from error
    except (
        SupportCaseConflictError, SupportCaseApplicationError,
        SecurityIncidentConflictError, IncidentAssignmentConflictError,
        SecurityIncidentEscalationError,
        SecurityIncidentResponseDecisionRegistryError,
        SecurityIncidentResponseDecisionConflictError,
        SecurityIncidentResponseDecisionServiceError,
        SecurityIncidentResponseExecutionError,
        SystemPermissionAssignmentConflictError,
        SystemPermissionAssignmentPersistedInvalidError,
        SystemPermissionRevocationCommandError,
    ) as error:
        raise HTTPException(status_code=409, detail="Support case operation conflicts with current state.") from error
    except Exception as error:
        # No exception text, Mongo detail, identity, or case content reaches the caller.
        raise HTTPException(status_code=503, detail="System Services operation is unavailable.") from error





class SelfServiceCaseCreateRequest(BaseModel):
    """Strict non-secret account-support intake; actor and tenant are never inputs."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    category: SupportCaseCategory


class _TenantSelfServiceAuthorizer:
    """Deny-only adapter; tenant self-service never invokes SYSTEM authority."""
    def require(self, *, principal_id: str, permission_id: str, session: object | None) -> None:
        raise SystemServicesAuthorizationError("SYSTEM_SCOPE_REQUIRED")


def _tenant_runtime(request: Request) -> SupportCaseRegistry:
    """Resolve only the case store; tenant self-service requires no staff authority."""
    if getattr(request.app.state, "system_services_case_indexes_ready", False) is not True:
        raise HTTPException(status_code=503, detail="System Services storage is not ready.")
    registry = getattr(request.app.state, "system_services_case_registry", None)
    if type(registry) is not SupportCaseRegistry:
        raise HTTPException(status_code=503, detail="System Services storage is not configured.")
    return registry


def _require_current_tenant_actor(
    *,
    identity: SovereignIdentity,
    tenant_id: str,
    session: ClientSession,
) -> SupportCaseActorContext:
    """Re-prove ACTIVE principal and exact ACTIVE membership in the write/read transaction."""
    if identity.status is not PrincipalStatus.ACTIVE:
        raise HTTPException(status_code=401, detail="Authenticated principal required.")
    if not isinstance(tenant_id, str) or not tenant_id or tenant_id != tenant_id.strip():
        raise HTTPException(status_code=403, detail="Tenant membership required.")
    try:
        principal = PrincipalAuthorityRepository().resolve(
            identity.identity_id, session=session
        )
        if principal.status is not PrincipalStatus.ACTIVE:
            raise HTTPException(status_code=401, detail="Authenticated principal required.")
        membership = get_tenant_membership_repository().resolve(
            identity.identity_id, tenant_id, session=session
        )
        if (
            membership.principal_id != identity.identity_id
            or membership.tenant_id != tenant_id
            or membership.status is not TenantMembershipStatus.ACTIVE
        ):
            raise HTTPException(status_code=403, detail="Tenant membership required.")
    except HTTPException:
        raise
    except Exception as error:
        # Absence is denied; repository/infrastructure failures are not converted to grants.
        from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
        from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError
        if isinstance(error, (PrincipalAuthorityNotFoundError, TenantMembershipNotFoundError)):
            raise HTTPException(status_code=403, detail="Tenant membership required.") from error
        raise HTTPException(status_code=503, detail="Tenant authority is unavailable.") from error
    return SupportCaseActorContext(
        principal_id=identity.identity_id,
        scope=SupportCaseScope.TENANT,
        tenant_id=tenant_id,
    )


def _project_tenant_case(case):
    """Expose only the authenticated principal's own non-secret case status."""
    return {
        "caseId": case.case_id,
        "category": case.category.value,
        "status": case.status.value,
        "revision": case.revision,
        "createdAt": case.created_at.isoformat(),
        "updatedAt": case.updated_at.isoformat(),
    }



class SecurityIncidentIntakeRequest(BaseModel):
    """Structured security signal only; free text and secret material are excluded."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    category: SecurityIncidentCategory
    observed_at: datetime


def _incident_runtime(request: Request) -> SecurityIncidentRegistry:
    if getattr(request.app.state, "system_services_incident_indexes_ready", False) is not True:
        raise HTTPException(status_code=503, detail="Security incident intake is not ready.")
    registry = getattr(request.app.state, "system_services_incident_registry", None)
    if type(registry) is not SecurityIncidentRegistry:
        raise HTTPException(status_code=503, detail="Security incident intake is not configured.")
    return registry


def _project_incident(value: SecurityIncident) -> dict[str, object]:
    return {
        "incidentId": value.incident_id,
        "category": value.category.value,
        "status": value.status,
        "revision": value.revision,
        "observedAt": value.observed_at.isoformat(),
        "receivedAt": value.received_at.isoformat(),
    }


@router.post("/self-service/security-incidents", status_code=201)
def report_own_security_incident(
    payload: SecurityIncidentIntakeRequest,
    request: Request,
    tenant_id: Annotated[str, Header(alias="X-Tenant-ID", min_length=1, max_length=256)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=256)],
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Durably report a structured suspected-security event; performs no containment."""
    registry = _incident_runtime(request)
    def record(session):
        actor = _require_current_tenant_actor(identity=identity, tenant_id=tenant_id, session=session)
        if payload.observed_at.tzinfo is None or payload.observed_at.utcoffset() is None:
            raise HTTPException(status_code=422, detail="An aware observation timestamp is required.")
        received_at = datetime.now(timezone.utc)
        fingerprint = sha3_256(
            (tenant_id + "\\0" + actor.principal_id + "\\0" + idempotency_key).encode("utf-8")
        ).hexdigest()
        incident_id = "incident-" + fingerprint
        event_fingerprint = sha3_256(
            (incident_id + "\\0INCIDENT_REPORTED").encode("utf-8")
        ).hexdigest()
        incident = SecurityIncident(
            incident_id=incident_id,
            tenant_id=tenant_id,
            reporter_principal_id=actor.principal_id,
            idempotency_fingerprint=fingerprint,
            category=payload.category,
            observed_at=payload.observed_at,
            received_at=received_at,
        )
        event = SecurityIncidentEvent(
            event_id="incident-event-" + fingerprint,
            incident_id=incident_id,
            tenant_id=tenant_id,
            actor_principal_id=actor.principal_id,
            event_type="INCIDENT_REPORTED",
            occurred_at=received_at,
            fingerprint=event_fingerprint,
        )
        persisted = registry.create_or_replay(incident, event, session=session)
        registry.record_platform_audit(incident=persisted, event=event, session=session)
        return _project_incident(persisted)
    return _run_transaction(record)


@router.get("/self-service/security-incidents")
def list_own_security_incidents(
    request: Request,
    tenant_id: Annotated[str, Header(alias="X-Tenant-ID", min_length=1, max_length=256)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """List only the authenticated reporter's own structured incident receipts."""
    registry = _incident_runtime(request)
    def read(session):
        actor = _require_current_tenant_actor(identity=identity, tenant_id=tenant_id, session=session)
        return [_project_incident(item) for item in registry.list_own(
            tenant_id=tenant_id, principal_id=actor.principal_id,
            session=session, limit=limit,
        )]
    return _run_transaction(read)


@router.post("/self-service/cases", status_code=201)
def create_own_support_case(
    payload: SelfServiceCaseCreateRequest,
    request: Request,
    tenant_id: Annotated[str, Header(alias="X-Tenant-ID", min_length=1, max_length=256)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=256)],
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Create one authenticated user's own tenant-scoped support case."""
    registry = _tenant_runtime(request)
    service = SupportCaseApplicationService(
        registry=registry,
        authorizer=_TenantSelfServiceAuthorizer(),
    )
    return _run_transaction(
        lambda session: _project_tenant_case(
            service.create_own_case(
                actor=_require_current_tenant_actor(
                    identity=identity, tenant_id=tenant_id, session=session
                ),
                category=payload.category,
                idempotency_key=idempotency_key,
                session=session,
            )
        )
    )


@router.get("/self-service/cases")
def list_own_support_cases(
    request: Request,
    tenant_id: Annotated[str, Header(alias="X-Tenant-ID", min_length=1, max_length=256)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """List only cases owned by the authenticated principal in the exact tenant."""
    registry = _tenant_runtime(request)
    service = SupportCaseApplicationService(
        registry=registry,
        authorizer=_TenantSelfServiceAuthorizer(),
    )
    def read(session):
        actor = _require_current_tenant_actor(identity=identity, tenant_id=tenant_id, session=session)
        return [_project_tenant_case(item) for item in service.list_own_cases(
            actor=actor, limit=limit, session=session
        )]
    return _run_transaction(read)


@router.get("/self-service/cases/{case_id}")
def read_own_support_case(
    case_id: str,
    request: Request,
    tenant_id: Annotated[str, Header(alias="X-Tenant-ID", min_length=1, max_length=256)],
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Read only the authenticated principal's own case status."""
    registry = _tenant_runtime(request)
    def read(session):
        actor = _require_current_tenant_actor(identity=identity, tenant_id=tenant_id, session=session)
        case = registry.get(
            case_id=case_id, scope=SupportCaseScope.TENANT,
            tenant_id=tenant_id, session=session,
        )
        if case.principal_id != actor.principal_id:
            raise HTTPException(status_code=404, detail="Support case not found.")
        return _project_tenant_case(case)
    return _run_transaction(read)


@router.get("/self-service/cases/{case_id}/events")
def read_own_support_case_events(
    case_id: str,
    request: Request,
    tenant_id: Annotated[str, Header(alias="X-Tenant-ID", min_length=1, max_length=256)],
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Read append-only history only after principal ownership is proven."""
    registry = _tenant_runtime(request)
    def read(session):
        actor = _require_current_tenant_actor(identity=identity, tenant_id=tenant_id, session=session)
        case = registry.get(
            case_id=case_id, scope=SupportCaseScope.TENANT,
            tenant_id=tenant_id, session=session,
        )
        if case.principal_id != actor.principal_id:
            raise HTTPException(status_code=404, detail="Support case not found.")
        return [event.to_document() for event in registry.list_events(
            case_id=case_id, scope=SupportCaseScope.TENANT,
            tenant_id=tenant_id, session=session,
        )]
    return _run_transaction(read)



class IncidentAssignmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    assigned_to_principal_id: StrictStr = Field(min_length=1, max_length=256)


class IncidentAssignmentDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    expected_revision: StrictInt = Field(ge=0)


def _assignment_runtime(request: Request) -> tuple[SecurityIncidentRegistry, SecurityIncidentAssignmentRegistry]:
    if getattr(request.app.state, "system_services_incident_indexes_ready", False) is not True:
        raise HTTPException(status_code=503, detail="Security incident storage is not ready.")
    if getattr(request.app.state, "system_services_assignment_indexes_ready", False) is not True:
        raise HTTPException(status_code=503, detail="Incident assignment storage is not ready.")
    incidents = getattr(request.app.state, "system_services_incident_registry", None)
    assignments = getattr(request.app.state, "system_services_assignment_registry", None)
    if type(incidents) is not SecurityIncidentRegistry or type(assignments) is not SecurityIncidentAssignmentRegistry:
        raise HTTPException(status_code=503, detail="Incident escalation is not configured.")
    return incidents, assignments


def _project_assignment(value: SecurityIncidentAssignment) -> dict[str, object]:
    return {
        "assignmentId": value.assignment_id,
        "incidentId": value.incident_id,
        "assignedToPrincipalId": value.assigned_to_principal_id,
        "status": value.status.value,
        "revision": value.revision,
        "createdAt": value.created_at.isoformat(),
        "updatedAt": value.updated_at.isoformat(),
    }


@router.get("/security-incidents")
def list_system_security_incidents(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Read sanitized incident queue only with current SYSTEM queue permission."""
    actor = _actor(identity)
    incidents, _ = _assignment_runtime(request)
    _, authorizer = _runtime(request)
    def read(session):
        authorizer.require(
            principal_id=actor.principal_id,
            permission_id="system_services:queue:read",
            session=session,
        )
        return [_project_incident(item) for item in incidents.list_system_queue(
            session=session, limit=limit
        )]
    return _run_transaction(read)


@router.post("/security-incidents/{incident_id}/assign", status_code=201)
def assign_security_incident_responder(
    incident_id: str,
    payload: IncidentAssignmentRequest,
    request: Request,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=256)],
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Assign a separately authorized platform responder with conflict checks."""
    actor = _actor(identity)
    incidents, assignments = _assignment_runtime(request)
    _, authorizer = _runtime(request)
    service = SecurityIncidentEscalationService(
        incidents=incidents, assignments=assignments, authorizer=authorizer,
    )
    return _run_transaction(lambda session: _project_assignment(service.assign(
        actor_principal_id=actor.principal_id,
        assigned_to_principal_id=payload.assigned_to_principal_id,
        incident_id=incident_id,
        idempotency_key=idempotency_key,
        session=session,
    )))



@router.get("/security-incident-assignments/mine")
def list_my_security_incident_assignments(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """List only assignments addressed to the authenticated current responder."""
    actor = _actor(identity)
    incidents, assignments = _assignment_runtime(request)
    _, authorizer = _runtime(request)
    service = SecurityIncidentEscalationService(
        incidents=incidents, assignments=assignments, authorizer=authorizer,
    )
    return _run_transaction(lambda session: [
        _project_assignment(item)
        for item in service.list_my_assignments(
            actor_principal_id=actor.principal_id,
            session=session,
            limit=limit,
        )
    ])



@router.get("/security-incident-assignments/{assignment_id}")
def read_my_security_incident_assignment(
    assignment_id: str,
    request: Request,
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Read only the exact incident assigned to the authenticated responder."""
    actor = _actor(identity)
    incidents, assignments = _assignment_runtime(request)
    _, authorizer = _runtime(request)
    service = SecurityIncidentEscalationService(
        incidents=incidents, assignments=assignments, authorizer=authorizer,
    )
    def read(session):
        assignment, incident = service.read_my_assignment(
            actor_principal_id=actor.principal_id,
            assignment_id=assignment_id,
            session=session,
        )
        return {
            "assignment": _project_assignment(assignment),
            "incident": _project_incident(incident),
        }
    return _run_transaction(read)


@router.post("/security-incident-assignments/{assignment_id}/accept")
def accept_security_incident_assignment(
    assignment_id: str,
    payload: IncidentAssignmentDecisionRequest,
    request: Request,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=256)],
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Allow only the currently assigned, independently authorized responder to accept."""
    actor = _actor(identity)
    incidents, assignments = _assignment_runtime(request)
    _, authorizer = _runtime(request)
    service = SecurityIncidentEscalationService(
        incidents=incidents, assignments=assignments, authorizer=authorizer,
    )
    return _run_transaction(lambda session: _project_assignment(service.accept(
        actor_principal_id=actor.principal_id,
        assignment_id=assignment_id,
        expected_revision=payload.expected_revision,
        idempotency_key=idempotency_key,
        session=session,
    )))


@router.post("/security-incident-assignments/{assignment_id}/decline")
def decline_security_incident_assignment(
    assignment_id: str,
    payload: IncidentAssignmentDecisionRequest,
    request: Request,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=256)],
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Allow only the currently assigned, independently authorized responder to decline."""
    actor = _actor(identity)
    incidents, assignments = _assignment_runtime(request)
    _, authorizer = _runtime(request)
    service = SecurityIncidentEscalationService(
        incidents=incidents, assignments=assignments, authorizer=authorizer,
    )
    return _run_transaction(lambda session: _project_assignment(service.decline(
        actor_principal_id=actor.principal_id,
        assignment_id=assignment_id,
        expected_revision=payload.expected_revision,
        idempotency_key=idempotency_key,
        session=session,
    )))



class SecurityIncidentResponseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    incident_id: StrictStr
    action: SecurityIncidentResponseAction
    target_assignment_id: StrictStr | None = None
    target_permission_id: StrictStr | None = None


class SecurityIncidentResponseApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    approved: StrictBool
    expected_revision: StrictInt = Field(ge=0)
    decision_evidence_reference: StrictStr = Field(min_length=1, max_length=256)


class SecurityIncidentResponseExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    expected_revision: StrictInt = Field(ge=1)


class SecurityIncidentPasswordResetExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    expected_revision: StrictInt = Field(ge=1)
    recovery_token: StrictStr = Field(min_length=1, max_length=4096)
    new_password: StrictStr = Field(min_length=1, max_length=1024)
    context_terms: tuple[StrictStr, ...] | None = None


def _validate_response_idempotency_key(value: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "*" in value
        or any(ord(character) < 33 or ord(character) == 127 for character in value)
    ):
        raise HTTPException(status_code=422, detail="A valid idempotency key is required.")
    return value


def _normalize_bson_utc_datetime(value: datetime) -> datetime:
    """Align event timestamps with MongoDB BSON's millisecond datetime precision."""
    normalized = value.astimezone(timezone.utc)
    return normalized.replace(microsecond=(normalized.microsecond // 1000) * 1000)


def _project_response_decision(value: SecurityIncidentResponseDecision) -> dict[str, object]:
    return {
        "decisionId": value.decision_id,
        "incidentId": value.incident_id,
        "tenantId": value.tenant_id,
        "targetPrincipalId": value.target_principal_id,
        "action": value.action.value,
        "status": value.status.value,
        "revision": value.revision,
        "requestedByPrincipalId": value.requested_by_principal_id,
        "decidedByPrincipalId": value.decided_by_principal_id,
        "decidedAt": value.decided_at.isoformat() if value.decided_at else None,
    }


@router.post("/security-response-decisions", status_code=201)
def request_security_incident_response(
    payload: SecurityIncidentResponseRequest,
    request: Request,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=256)],
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Create an incident-bound proposal; this route never performs containment."""
    actor = _actor(identity)
    idempotency_key = _validate_response_idempotency_key(idempotency_key)
    decision_registry, decision_service, _, permission_assignments = _response_runtime(request)
    incidents, _ = _assignment_runtime(request)

    def create(session):
        incident = incidents.get_by_id(incident_id=payload.incident_id, session=session)
        target_assignment_id = payload.target_assignment_id
        target_permission_id = payload.target_permission_id
        if payload.action is SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION:
            if not target_assignment_id or not target_permission_id:
                raise HTTPException(status_code=422, detail="Exact permission assignment binding is required.")
            history = permission_assignments.get_history(target_assignment_id, session=session)
            if (
                not history
                or history[0].principal_id != incident.reporter_principal_id
                or history[0].permission_id != target_permission_id
                or history[-1].status is not SystemPermissionAssignmentStatus.ACTIVE
            ):
                raise HTTPException(status_code=409, detail="Target permission assignment does not match the incident.")
        elif target_assignment_id is not None or target_permission_id is not None:
            raise HTTPException(status_code=422, detail="Permission assignment binding is not valid for this action.")

        decision_id = "response-" + sha3_256(
            (incident.incident_id + "\\0" + actor.principal_id + "\\0" + idempotency_key).encode("utf-8")
        ).hexdigest()
        existing = decision_registry.find(decision_id, session=session)
        requested_at = (
            existing.requested_at
            if existing is not None
            else _normalize_bson_utc_datetime(datetime.now(timezone.utc))
        )
        decision = SecurityIncidentResponseDecision(
            decision_id=decision_id,
            incident_id=incident.incident_id,
            tenant_id=incident.tenant_id,
            target_principal_id=incident.reporter_principal_id,
            action=payload.action,
            requested_by_principal_id=actor.principal_id,
            requested_at=requested_at,
            request_evidence_reference="security-incident:" + incident.incident_id,
            target_assignment_id=target_assignment_id,
            target_permission_id=target_permission_id,
        )
        persisted = decision_service.request(
            actor_principal_id=actor.principal_id,
            decision=decision,
            session=session,
        )
        return _project_response_decision(persisted)

    return _run_transaction(create)


@router.post("/security-response-decisions/{decision_id}/decision")
def decide_security_incident_response(
    decision_id: str,
    payload: SecurityIncidentResponseApprovalRequest,
    request: Request,
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Approve or reject only through an independently authorized principal."""
    actor = _actor(identity)
    decision_registry, decision_service, _, permission_assignments = _response_runtime(request)
    incidents, _ = _assignment_runtime(request)

    def decide(session):
        current = decision_registry.get(decision_id, session=session)
        if current.action not in {
            SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION,
            SecurityIncidentResponseAction.PASSWORD_RESET,
        }:
            raise HTTPException(status_code=409, detail="This response action is not enabled for canonical execution.")
        incident = incidents.get_by_id(incident_id=current.incident_id, session=session)
        if (
            incident.tenant_id != current.tenant_id
            or incident.reporter_principal_id != current.target_principal_id
        ):
            raise HTTPException(status_code=409, detail="Response decision incident/target binding is invalid.")
        if current.action is SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION:
            if current.target_assignment_id is None or current.target_permission_id is None:
                raise HTTPException(status_code=409, detail="Response decision assignment binding is missing.")
            history = permission_assignments.get_history(current.target_assignment_id, session=session)
            if (
                not history
                or history[0].principal_id != current.target_principal_id
                or history[0].permission_id != current.target_permission_id
            ):
                raise HTTPException(status_code=409, detail="Response decision assignment lineage is invalid.")
            if (
                current.revision == 0
                and payload.approved
                and history[-1].status is not SystemPermissionAssignmentStatus.ACTIVE
            ):
                raise HTTPException(status_code=409, detail="Cannot approve a response for an inactive target assignment.")
        elif current.target_assignment_id is not None or current.target_permission_id is not None:
            raise HTTPException(status_code=409, detail="Password-reset decision cannot bind a permission assignment.")
        decided_at = _normalize_bson_utc_datetime(datetime.now(timezone.utc))
        if current.revision == 1:
            same_outcome = (
                current.status.value == ("APPROVED" if payload.approved else "REJECTED")
                and current.decided_by_principal_id == actor.principal_id
                and current.decision_evidence_reference == payload.decision_evidence_reference
                and payload.expected_revision == 0
            )
            if not same_outcome:
                raise HTTPException(status_code=409, detail="Response decision revision conflict.")
            if not isinstance(current.decided_at, datetime):
                raise HTTPException(status_code=409, detail="Persisted response decision timestamp is invalid.")
            decided_at = current.decided_at
        persisted = decision_service.decide(
            decision_id,
            actor_principal_id=actor.principal_id,
            approved=payload.approved,
            decided_at=decided_at,
            decision_evidence_reference=payload.decision_evidence_reference,
            expected_revision=payload.expected_revision,
            session=session,
        )
        return _project_response_decision(persisted)

    return _run_transaction(decide)


@router.post("/security-response-decisions/{decision_id}/execute/permission-revocation")
def execute_approved_system_permission_revocation(
    decision_id: str,
    payload: SecurityIncidentResponseExecutionRequest,
    request: Request,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=256)],
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Execute one approved revocation through canonical D12 in this caller transaction."""
    actor = _actor(identity)
    idempotency_key = _validate_response_idempotency_key(idempotency_key)
    decision_registry, _, executor, permission_assignments = _response_runtime(request)
    incidents, _ = _assignment_runtime(request)

    def execute(session):
        decision = decision_registry.get(decision_id, session=session)
        incident = incidents.get_by_id(incident_id=decision.incident_id, session=session)
        if (
            incident.tenant_id != decision.tenant_id
            or incident.reporter_principal_id != decision.target_principal_id
        ):
            raise HTTPException(status_code=409, detail="Approved decision no longer matches its incident target.")
        if decision.revision != payload.expected_revision:
            raise HTTPException(status_code=409, detail="Response decision revision conflict.")
        try:
            executor.authorize_execution(
                decision,
                actor_principal_id=actor.principal_id,
                session=session,
            )
        except SecurityIncidentResponseExecutionError as error:
            raise HTTPException(status_code=403, detail="Independent response execution authority required.") from error
        if decision.target_assignment_id is None or decision.target_permission_id is None:
            raise HTTPException(status_code=409, detail="Approved decision has no permission assignment binding.")
        assignment_history = permission_assignments.get_history(
            decision.target_assignment_id,
            session=session,
        )
        if (
            not assignment_history
            or assignment_history[0].principal_id != decision.target_principal_id
            or assignment_history[0].permission_id != decision.target_permission_id
        ):
            raise HTTPException(status_code=409, detail="Approved decision permission assignment correlation is invalid.")
        execution_receipt = decision_registry.find_execution(
            decision=decision,
            actor_principal_id=actor.principal_id,
            idempotency_key=idempotency_key,
            session=session,
        )
        if execution_receipt is not None:
            execution_at = datetime.fromisoformat(execution_receipt["occurred_at"])
        else:
            replay = permission_assignments.find_revocation_replay(
                assignment_id=decision.target_assignment_id,
                idempotency_key=idempotency_key,
                session=session,
            )
            if replay is not None:
                if (
                    replay.principal_id != decision.target_principal_id
                    or replay.permission_id != decision.target_permission_id
                    or replay.revoked_by_principal_id != actor.principal_id
                    or replay.revocation_evidence_reference != (
                        "security-incident-response-decision:" + decision.decision_id
                    )
                    or replay.revoked_at is None
                ):
                    raise HTTPException(status_code=409, detail="Revocation replay does not match the approved decision.")
                execution_at = replay.revoked_at
            else:
                if assignment_history[-1].status is not SystemPermissionAssignmentStatus.ACTIVE:
                    raise HTTPException(status_code=409, detail="Target permission assignment is not active.")
                execution_at = datetime.now(timezone.utc)
        evidence = SystemPermissionCommandEvidence(
            operation=SystemPermissionCommandOperation.REVOKE,
            actor_principal_id=actor.principal_id,
            target_principal_id=decision.target_principal_id,
            permission_id=decision.target_permission_id,
            evidence_reference="security-incident-response-decision:" + decision.decision_id,
            occurred_at=execution_at,
            idempotency_key=idempotency_key,
            assignment_id=decision.target_assignment_id,
        )
        revoked = executor.execute_system_permission_revocation(
            decision,
            evidence=evidence,
            session=session,
        )
        decision_registry.record_execution(
            decision=decision,
            actor_principal_id=actor.principal_id,
            idempotency_key=idempotency_key,
            occurred_at=execution_at,
            result_status=revoked.status.value,
            result_revision=revoked.revision,
            session=session,
        )
        return {
            "decisionId": decision.decision_id,
            "assignmentId": revoked.assignment_id,
            "permissionId": revoked.permission_id,
            "status": revoked.status.value,
            "revision": revoked.revision,
        }

    return _run_transaction(execute)


@router.post("/security-response-decisions/{decision_id}/execute/password-reset")
def execute_approved_password_reset(
    decision_id: str,
    payload: SecurityIncidentPasswordResetExecutionRequest,
    request: Request,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=256)],
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Execute an approved reset only through R10 and atomically record its receipt."""
    actor = _actor(identity)
    idempotency_key = _validate_response_idempotency_key(idempotency_key)
    decision_registry, _, executor, _ = _response_runtime(request)
    incidents, _ = _assignment_runtime(request)

    def resolve_replay(session):
        decision = decision_registry.get(decision_id, session=session)
        if decision.action is not SecurityIncidentResponseAction.PASSWORD_RESET:
            raise HTTPException(status_code=409, detail="Response decision action mismatch.")
        incident = incidents.get_by_id(incident_id=decision.incident_id, session=session)
        if (
            incident.tenant_id != decision.tenant_id
            or incident.reporter_principal_id != decision.target_principal_id
            or decision.target_assignment_id is not None
            or decision.target_permission_id is not None
            or decision.revision != payload.expected_revision
        ):
            raise HTTPException(status_code=409, detail="Approved password-reset decision binding or revision is invalid.")
        try:
            executor.authorize_password_reset_replay(
                decision,
                actor_principal_id=actor.principal_id,
                session=session,
            )
        except SecurityIncidentResponseExecutionError as error:
            raise HTTPException(status_code=403, detail="Independent response execution authority required.") from error
        return decision_registry.find_execution(
            decision=decision,
            actor_principal_id=actor.principal_id,
            idempotency_key=idempotency_key,
            session=session,
        )

    replay = _run_transaction(resolve_replay)
    if replay is not None:
        return {
            "decisionId": decision_id,
            "status": replay["result_status"],
            "credentialRevision": replay["result_revision"],
            "replayed": True,
        }

    # PasswordResetService owns its transaction. The completion callback writes
    # the decision receipt, platform audit, and pending outbox intent on that
    # exact session, so any evidence failure rolls the canonical reset back.
    def persist_receipt(session, tenant_id, principal_id, credential_revision):
        decision_registry.record_execution(
            decision=approved_decision,
            actor_principal_id=actor.principal_id,
            idempotency_key=idempotency_key,
            occurred_at=datetime.now(timezone.utc),
            result_status="PASSWORD_RESET_COMPLETED",
            result_revision=credential_revision,
            session=session,
        )

    approved_decision = _run_transaction(
        lambda session: decision_registry.get(decision_id, session=session)
    )
    try:
        result = executor.execute_password_reset(
            approved_decision,
            actor_principal_id=actor.principal_id,
            recovery_token=payload.recovery_token,
            new_password=payload.new_password,
            context_terms=payload.context_terms,
            transaction_completion=persist_receipt,
        )
    except SystemServicesAuthorizationError as error:
        raise HTTPException(status_code=403, detail="Independent response execution authority required.") from error
    except SystemServicesAuthorizationUnavailable as error:
        raise HTTPException(status_code=503, detail="System Services execution authority is unavailable.") from error
    except SecurityIncidentResponseDecisionConflictError as error:
        # A concurrent request using the same key may have committed first.
        replay = _run_transaction(resolve_replay)
        if replay is not None:
            return {
                "decisionId": decision_id,
                "status": replay["result_status"],
                "credentialRevision": replay["result_revision"],
                "replayed": True,
            }
        raise HTTPException(status_code=409, detail="Canonical password recovery conflicts with current decision state.") from error
    except SecurityIncidentResponseDecisionRegistryError as error:
        raise HTTPException(status_code=503, detail="Password-reset execution evidence is unavailable.") from error
    except (PasswordResetServiceError, SecurityIncidentResponseExecutionError) as error:
        # A concurrent request using the same key may have committed first.
        # Re-resolve only after independently re-authorizing the actor.
        replay = _run_transaction(resolve_replay)
        if replay is not None:
            return {
                "decisionId": decision_id,
                "status": replay["result_status"],
                "credentialRevision": replay["result_revision"],
                "replayed": True,
            }
        raise HTTPException(status_code=409, detail="Canonical password recovery was not completed.") from error
    return {
        "decisionId": decision_id,
        "status": result.status,
        "replayed": False,
    }


@router.get("/workspace-bootstrap")
def system_services_workspace_bootstrap(
    request: Request,
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Project the staff workspace only after the exact EOS queue permission is current."""
    actor = _actor(identity)
    service = _service(request)
    _, authorizer = _runtime(request)

    def project(session: ClientSession):
        cases = service.list_system_queue(actor=actor, limit=100, session=session)
        capabilities = ["system_services:queue:read"]
        for permission_id in (
            "system_services:identity:read",
            "system_services:incident:escalate",
        ):
            try:
                authorizer.require(
                    principal_id=actor.principal_id,
                    permission_id=permission_id,
                    session=session,
                )
                capabilities.append(permission_id)
            except SystemServicesAuthorizationError:
                # Capabilities are exact EOS permission projections, never role-label inference.
                pass
        return {
            "status": "READY",
            "authority": "EOS_SYSTEM_SERVICES",
            "principalId": actor.principal_id,
            "scope": "SYSTEM",
            "capabilities": capabilities,
            "summary": {
                "openCases": sum(case.status is SupportCaseStatus.OPEN for case in cases),
                "securityEscalations": sum(case.status is SupportCaseStatus.ESCALATED_SECURITY_INCIDENT for case in cases),
            },
            "cases": [
                {
                    "caseId": case.case_id,
                    "reference": case.case_id,
                    "category": case.category.value,
                    "status": case.status.value,
                }
                for case in cases
            ],
        }

    return _run_transaction(project)


@router.get("/cases")
def list_system_cases(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    statuses: Annotated[list[SupportCaseStatus] | None, Query()] = None,
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """List the bounded SYSTEM queue after current queue-read authorization."""
    actor = _actor(identity)
    service = _service(request)
    selected = tuple(statuses or ())
    return _run_transaction(
        lambda session: [
            case.to_document()
            for case in service.list_system_queue(
                actor=actor,
                limit=limit,
                statuses=selected,
                session=session,
            )
        ]
    )


@router.get("/cases/{case_id}/events")
def read_system_case_events(
    case_id: str,
    request: Request,
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Read an exact SYSTEM case event history after identity-read authorization."""
    actor = _actor(identity)
    service = _service(request)
    return _run_transaction(
        lambda session: [
            event.to_document()
            for event in service.read_system_case_history(
                actor=actor,
                case_id=case_id,
                session=session,
            )
        ]
    )


@router.post("/cases/{case_id}/transition")
def transition_system_case(
    case_id: str,
    payload: CaseTransitionRequest,
    request: Request,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=256)],
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Perform one permission-gated state transition with revision CAS and replay key."""
    actor = _actor(identity)
    service = _service(request)
    return _run_transaction(
        lambda session: service.transition_system_case(
            actor=actor,
            case_id=case_id,
            next_status=payload.next_status,
            idempotency_key=idempotency_key,
            expected_revision=payload.expected_revision,
            session=session,
        ).to_document()
    )


__all__ = ["router", "CaseTransitionRequest"]
