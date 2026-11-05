"""Authenticated SYSTEM-scoped support-case API routes.

Principal identity comes from EOS ACCESS-token verification. Tenant claims,
browser roles, request actor IDs and request permission lists are never used
for SYSTEM authorization; each operation re-proves current SYSTEM assignment
and active PLATFORM workforce evidence in the same Mongo transaction as the
case read/write.
"""
from __future__ import annotations

from typing import Annotated, Callable, TypeVar, cast

from pymongo.client_session import ClientSession

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, StrictInt

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
    except SupportCaseNotFoundError as error:
        raise HTTPException(status_code=404, detail="Support case not found.") from error
    except (SupportCaseConflictError, SupportCaseApplicationError) as error:
        raise HTTPException(status_code=409, detail="Support case operation conflicts with current state.") from error
    except Exception as error:
        # No exception text, Mongo detail, identity, or case content reaches the caller.
        raise HTTPException(status_code=503, detail="System Services operation is unavailable.") from error





class SelfServiceCaseCreateRequest(BaseModel):
    """Strict non-secret account-support intake; actor and tenant are never inputs."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    category: SupportCaseCategory


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
        authorizer=cast(SystemServicesAuthorizer, object()),
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
