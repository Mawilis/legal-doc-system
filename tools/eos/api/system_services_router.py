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
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

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
    except (SupportCaseNotFoundError, IncidentAssignmentNotFoundError, SecurityIncidentNotFoundError) as error:
        raise HTTPException(status_code=404, detail="System Services record not found.") from error
    except (
        SupportCaseConflictError, SupportCaseApplicationError,
        SecurityIncidentConflictError, IncidentAssignmentConflictError,
        SecurityIncidentEscalationError,
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
        return _project_incident(registry.create_or_replay(incident, event, session=session))
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
        authorizer=cast(SystemServicesAuthorizer, object()),
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
        try:
            authorizer.require(
                principal_id=actor.principal_id,
                permission_id="system_services:identity:read",
                session=session,
            )
            capabilities.append("system_services:identity:read")
        except SystemServicesAuthorizationError:
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
