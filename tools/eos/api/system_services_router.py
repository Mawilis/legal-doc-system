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
from tools.eos.system_services.eos_authorizer import (
    SystemServicesAuthorizationError,
    SystemServicesAuthorizationUnavailable,
)
from tools.eos.system_services.support_case import SupportCaseScope, SupportCaseStatus
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
    if not isinstance(identity.identity_id, str) or not identity.identity_id.strip():
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



@router.get("/workspace-bootstrap")
def system_services_workspace_bootstrap(
    request: Request,
    identity: SovereignIdentity = Depends(get_current_identity),
):
    """Project the staff workspace only after the exact EOS queue permission is current."""
    actor = _actor(identity)
    service = _service(request)

    def project(session: ClientSession):
        cases = service.list_system_queue(actor=actor, limit=100, session=session)
        return {
            "status": "READY",
            "authority": "EOS_SYSTEM_SERVICES",
            "principalId": actor.principal_id,
            "scope": "SYSTEM",
            "capabilities": ["system_services:queue:read"],
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
