"""Authenticated HTTP commands for WILSY headcount requisitions.

Transport composes canonical tenant IAM and caller-owned Mongo transactions.
Employment, candidate, offer, principal, membership, capacity, IAM and payroll
authority remain separate systems and are not created by these commands.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization, TenantAuthorizationContext,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.domain.headcount_requisition import (
    HeadcountApproval, HeadcountRequisition, RequisitionDecision, RequisitionError,
)
from tools.eos.saas.hr.headcount_requisition_registry import (
    COLLECTION, EVENT_COLLECTION, HeadcountRequisitionNotFound,
    HeadcountRequisitionRegistry, HeadcountRequisitionRegistryConflict,
    HeadcountRequisitionRegistryError,
)

router = APIRouter(prefix="/hr/headcount-requisitions", tags=["Headcount Requisitions"])

_READ = RequireTenantAuthorization(
    "hr:headcount_requisition:read", "hr_headcount_requisition_read",
)
_CREATE = RequireTenantAuthorization(
    "hr:headcount_requisition:create", "hr_headcount_requisition_create",
)
_DECIDE = RequireTenantAuthorization(
    "hr:headcount_requisition:decide", "hr_headcount_requisition_decide",
)


class RequisitionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    department_id: str = Field(min_length=1, max_length=180)
    position_title: str = Field(min_length=1, max_length=180)
    employment_type: str = Field(min_length=1, max_length=180)
    work_location: str = Field(min_length=1, max_length=180)
    headcount: int = Field(ge=1, le=50, strict=True)
    business_justification: str = Field(min_length=1, max_length=4000)


class RequisitionSubmitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=1, strict=True)


class RequisitionDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=1)
    decision: Literal["APPROVE", "REJECT"]
    reason: str = Field(min_length=1, max_length=2000)


def _registry(database: Any) -> HeadcountRequisitionRegistry:
    current = database.get_collection(
        COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    events = database.get_collection(
        EVENT_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    return HeadcountRequisitionRegistry(current, events)


def _request_fingerprint(
    *, tenant_id: str, requisition_id: str, actor_principal_id: str,
    action: str, idempotency_key: str, payload: dict[str, object],
) -> str:
    command = {
        "tenant_id": tenant_id,
        "requisition_id": requisition_id,
        "actor_principal_id": actor_principal_id,
        "action": action,
        "idempotency_key": idempotency_key,
        "payload": payload,
    }
    raw = json.dumps(command, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


def _transaction(callback):
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="HEADCOUNT_DATABASE_UNAVAILABLE")
    try:
        current = database.get_collection(COLLECTION, write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))
        events = database.get_collection(EVENT_COLLECTION, write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))
        HeadcountRequisitionRegistry.ensure_indexes(current, events)
        with client.start_session() as session:
            return session.with_transaction(
                lambda current: callback(_registry(database), current),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except HeadcountRequisitionNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except HeadcountRequisitionRegistryConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except (HeadcountRequisitionRegistryError, RequisitionError) as error:
        code = getattr(error, "code", str(error))
        raise HTTPException(status_code=422 if isinstance(error, RequisitionError) else 503, detail=code) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="HEADCOUNT_TRANSACTION_UNAVAILABLE") from error


@router.get("")
async def list_headcount_requisitions(
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    values = _transaction(
        lambda registry, session: registry.list_for_tenant(
            tenant_id=context.tenant_id, session=session,
        )
    )
    return {
        "schema": "WILSY-HEADCOUNT-REQUISITIONS/V1",
        "tenant_id": context.tenant_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "items": [value.to_dict() for value in values],
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_headcount_requisition(
    body: RequisitionCreateRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_CREATE),
) -> dict[str, object]:
    now = datetime.now(timezone.utc)
    stable_id = hashlib.sha3_256(
        f"{context.tenant_id}:{idempotency_key}".encode("utf-8")
    ).hexdigest()[:24].upper()
    requisition = HeadcountRequisition(
        tenant_id=context.tenant_id,
        requisition_id=f"REQ-{stable_id}",
        department_id=body.department_id,
        position_title=body.position_title,
        employment_type=body.employment_type,
        work_location=body.work_location,
        headcount=body.headcount,
        business_justification=body.business_justification,
        requested_by_principal_id=context.identity.identity_id,
    )
    value = _transaction(lambda registry, session: registry.create_or_replay(
        requisition, idempotency_key=idempotency_key,
        actor_principal_id=context.identity.identity_id,
        occurred_at=now, session=session,
    ))
    return value.to_dict()


@router.post("/{requisition_id}/submit")
async def submit_headcount_requisition(
    requisition_id: str,
    body: RequisitionSubmitRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_CREATE),
) -> dict[str, object]:
    now = datetime.now(timezone.utc)
    request_fingerprint = _request_fingerprint(
        tenant_id=context.tenant_id, requisition_id=requisition_id,
        actor_principal_id=context.identity.identity_id, action="SUBMITTED",
        idempotency_key=idempotency_key, payload=body.model_dump(),
    )
    def submit(registry: HeadcountRequisitionRegistry, session: Any):
        replay = registry.replay_transition(
            tenant_id=context.tenant_id, idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint, session=session,
        )
        if replay is not None:
            return replay
        current = registry.get(
            tenant_id=context.tenant_id, requisition_id=requisition_id, session=session,
        )
        updated = current.submit(
            actor_principal_id=context.identity.identity_id,
            submitted_at=now, expected_revision=body.expected_revision,
        )
        return registry.transition(
            tenant_id=context.tenant_id, requisition_id=requisition_id,
            expected_revision=body.expected_revision, updated=updated,
            action="SUBMITTED", actor_principal_id=context.identity.identity_id,
            idempotency_key=idempotency_key, request_fingerprint=request_fingerprint,
            occurred_at=now, session=session,
        )
    return _transaction(submit).to_dict()


@router.post("/{requisition_id}/decision")
async def decide_headcount_requisition(
    requisition_id: str,
    body: RequisitionDecisionRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_DECIDE),
) -> dict[str, object]:
    now = datetime.now(timezone.utc)
    request_fingerprint = _request_fingerprint(
        tenant_id=context.tenant_id, requisition_id=requisition_id,
        actor_principal_id=context.identity.identity_id, action=body.decision,
        idempotency_key=idempotency_key, payload=body.model_dump(),
    )
    def decide(registry: HeadcountRequisitionRegistry, session: Any):
        replay = registry.replay_transition(
            tenant_id=context.tenant_id, idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint, session=session,
        )
        if replay is not None:
            return replay
        current = registry.get(
            tenant_id=context.tenant_id, requisition_id=requisition_id, session=session,
        )
        approval = HeadcountApproval(
            decision_id=f"HCA-{uuid.uuid4().hex.upper()}",
            actor_principal_id=context.identity.identity_id,
            decision=RequisitionDecision(body.decision),
            reason=body.reason,
            decided_at=now,
        )
        updated = current.decide(approval, expected_revision=body.expected_revision)
        return registry.transition(
            tenant_id=context.tenant_id, requisition_id=requisition_id,
            expected_revision=body.expected_revision, updated=updated,
            action=body.decision, actor_principal_id=context.identity.identity_id,
            idempotency_key=idempotency_key, request_fingerprint=request_fingerprint,
            occurred_at=now, session=session,
        )
    return _transaction(decide).to_dict()


__all__ = [
    "router", "RequisitionCreateRequest", "RequisitionSubmitRequest",
    "RequisitionDecisionRequest",
]
