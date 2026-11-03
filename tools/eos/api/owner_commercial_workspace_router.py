"""Tenant-owner Legal commercial operating workspace HTTP surface.

This is a separate owner-commercial projection. It never exposes Legal matters,
client-confidential records, professional work items or practitioner commands.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization, TenantAuthorizationContext,
)
from tools.eos.crm.domain.owner_commercial_work_item import OwnerWorkKind, OwnerWorkPriority, OwnerWorkItemError
from tools.eos.crm.persistence.owner_commercial_work_registry import (
    COLLECTION, OwnerCommercialWorkRegistry, OwnerWorkRegistryError, OwnerWorkRegistryConflict,
)
from tools.eos.crm.service.owner_commercial_workspace_service import (
    OwnerCommercialWorkspaceError, OwnerCommercialWorkspaceService,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION, HISTORY_COLLECTION,
)
import tools.eos.saas.billing.subscription_registry as subscription_registry_module

router = APIRouter(prefix="/crm/owner-workspace", tags=["Owner Commercial Workspace"])

_READ = RequireTenantAuthorization("crm:work_item:read", "crm_work_item_read")
_CREATE = RequireTenantAuthorization("crm:work_item:create", "crm_work_item_create")
_COMPLETE = RequireTenantAuthorization("crm:work_item:complete", "crm_work_item_complete")


class OwnerWorkCompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    completion_note: str = Field(min_length=1, max_length=1000)


class OwnerWorkCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=240)
    description: str = Field(default="", max_length=4000)
    kind: Literal["TASK", "REMINDER", "FOLLOW_UP"] = "TASK"
    priority: Literal["CRITICAL", "HIGH", "NORMAL", "LOW"] = "NORMAL"
    due_at: datetime | None = None
    source_type: str | None = Field(default=None, max_length=80)
    source_id: str | None = Field(default=None, max_length=160)


def _service(database: Any) -> OwnerCommercialWorkspaceService:
    return OwnerCommercialWorkspaceService(
        OwnerCommercialWorkRegistry(database.get_collection(COLLECTION)),
        subscription_registry_module.subscriptions_collection,
        database.get_collection(HISTORY_COLLECTION),
        database.get_collection(CURRENT_COLLECTION),
    )


def _transaction(callback):
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="OWNER_WORK_DATABASE_UNAVAILABLE")
    try:
        with client.start_session() as session:
            return session.with_transaction(lambda current: callback(_service(database), current))
    except OwnerCommercialWorkspaceError as error:
        code = error.code
        if code in {"OWNER_WORK_LEGAL_NOT_ENTITLED", "OWNER_WORK_LEGAL_ENTITLEMENT_UNAVAILABLE"}:
            raise HTTPException(status_code=403 if code.endswith("NOT_ENTITLED") else 503, detail=code) from error
        raise HTTPException(status_code=503, detail="OWNER_WORK_SERVICE_UNAVAILABLE") from error
    except OwnerWorkRegistryConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except OwnerWorkRegistryError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except OwnerWorkItemError as error:
        raise HTTPException(status_code=422, detail=error.code) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="OWNER_WORK_TRANSACTION_UNAVAILABLE") from error


@router.get("")
async def read_owner_workspace(
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Return exact-tenant owner work queue after Legal entitlement admission."""
    def read(service: OwnerCommercialWorkspaceService, session: Any):
        queue = service.daily_queue(
            tenant_id=context.tenant_id, now=datetime.now(timezone.utc), session=session,
        )
        return {
            "schema": "WILSY-OWNER-COMMERCIAL-WORKSPACE/V1",
            "tenant_id": context.tenant_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "items": list(queue),
        }
    return _transaction(read)


@router.post("/work-items", status_code=status.HTTP_201_CREATED)
async def create_owner_work_item(
    body: OwnerWorkCreateRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_CREATE),
) -> dict[str, object]:
    """Persist one explicit owner task/reminder/follow-up under Legal entitlement."""
    def create(service: OwnerCommercialWorkspaceService, session: Any):
        if body.due_at is not None and (body.due_at.tzinfo is None or body.due_at.utcoffset() is None):
            raise HTTPException(status_code=422, detail="DUE_AT_MUST_BE_TIMEZONE_AWARE")
        if (body.source_type is None) != (body.source_id is None):
            raise HTTPException(status_code=422, detail="SOURCE_COORDINATE_INVALID")
        item = service.create(
            tenant_id=context.tenant_id,
            principal_id=context.identity.identity_id,
            title=body.title, description=body.description,
            kind=OwnerWorkKind(body.kind), priority=OwnerWorkPriority(body.priority),
            due_at=body.due_at, source_type=body.source_type, source_id=body.source_id,
            idempotency_key=idempotency_key,
            now=datetime.now(timezone.utc), session=session,
        )
        return item.to_dict()
    return _transaction(create)


@router.post("/work-items/{work_item_id}/complete")
async def complete_owner_work_item(
    work_item_id: str,
    body: OwnerWorkCompleteRequest,
    context: TenantAuthorizationContext = Depends(_COMPLETE),
) -> dict[str, object]:
    """Complete one exact tenant work item with server-owned completion time."""
    def complete(service: OwnerCommercialWorkspaceService, session: Any):
        item = service.complete(
            tenant_id=context.tenant_id, work_item_id=work_item_id,
            completion_note=body.completion_note,
            now=datetime.now(timezone.utc), session=session,
        )
        return item.to_dict()
    return _transaction(complete)


__all__ = ["router", "OwnerWorkCreateRequest", "OwnerWorkCompleteRequest"]
