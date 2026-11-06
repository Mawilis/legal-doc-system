"""Authenticated tenant Operations and Intelligence task/queue HTTP authority.

Each module has separate permission-operation bindings, product entitlement
readback, Mongo collection and API namespace. Browser payloads cannot select a
product, tenant, principal, entitlement or workspace authority.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization, TenantAuthorizationContext
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION, HISTORY_COLLECTION,
)
from tools.eos.workspaces.domain.tenant_module_work_item import (
    ModuleWorkItemError, ModuleWorkKind, ModuleWorkPriority,
)
from tools.eos.workspaces.persistence.tenant_module_work_registry import (
    TenantModuleWorkRegistry, ModuleWorkRegistryError,
    ModuleWorkRegistryConflict, ModuleWorkRegistryNotFound, ensure_indexes,
)
from tools.eos.workspaces.service.tenant_module_workspace_service import (
    TenantModuleWorkspaceError, TenantModuleWorkspaceService,
)

router = APIRouter(prefix="/tenant-modules", tags=["Tenant Module Workspaces"])


class ModuleWorkCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=240)
    description: str = Field(default="", max_length=4000)
    kind: Literal["TASK", "REMINDER", "FOLLOW_UP"] = "TASK"
    priority: Literal["CRITICAL", "HIGH", "NORMAL", "LOW"] = "NORMAL"
    due_at: datetime | None = None
    source_type: str | None = Field(default=None, max_length=80)
    source_id: str | None = Field(default=None, max_length=160)


class ModuleWorkCompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    completion_note: str = Field(min_length=1, max_length=1000)


_PRODUCTS = {
    "operations": (
        TenantProductId.OPERATIONS, "OPERATIONS_DASHBOARD",
        "tenant_operations_work_items", "operations",
    ),
    "intelligence": (
        TenantProductId.INTELLIGENCE, "INTELLIGENCE_DASHBOARD",
        "tenant_intelligence_work_items", "intelligence",
    ),
}


def _service(database: Any, product_id: TenantProductId, collection_name: str) -> TenantModuleWorkspaceService:
    collection = database.get_collection(
        collection_name,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    return TenantModuleWorkspaceService(
        TenantModuleWorkRegistry(collection), product_id,
        database.get_collection(HISTORY_COLLECTION),
        database.get_collection(CURRENT_COLLECTION),
    )


def _transaction(product_id: TenantProductId, collection_name: str, callback):
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="MODULE_WORK_DATABASE_UNAVAILABLE")
    try:
        ensure_indexes(database.get_collection(collection_name))
        with client.start_session() as session:
            return session.with_transaction(
                lambda current: callback(_service(database, product_id, collection_name), current),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except TenantModuleWorkspaceError as error:
        if error.code == "MODULE_WORK_PRODUCT_NOT_ENTITLED":
            raise HTTPException(status_code=403, detail=error.code) from error
        raise HTTPException(status_code=503, detail=error.code) from error
    except ModuleWorkRegistryConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except ModuleWorkRegistryNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except ModuleWorkItemError as error:
        raise HTTPException(status_code=422, detail=error.code) from error
    except ModuleWorkRegistryError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="MODULE_WORK_TRANSACTION_UNAVAILABLE") from error


def _register_module(slug: str, config: tuple, *, read_permission: str, create_permission: str, complete_permission: str) -> None:
    product_id, workspace_key, collection_name, operation_prefix = config
    read_auth = RequireTenantAuthorization(read_permission, f"{operation_prefix}_work_item_read")
    create_auth = RequireTenantAuthorization(create_permission, f"{operation_prefix}_work_item_create")
    complete_auth = RequireTenantAuthorization(complete_permission, f"{operation_prefix}_work_item_complete")

    async def read_workspace(context: TenantAuthorizationContext = Depends(read_auth)):
        def read(service: TenantModuleWorkspaceService, session: Any):
            items = service.daily_queue(
                tenant_id=context.tenant_id, now=datetime.now(timezone.utc), session=session,
            )
            return {
                "schema": "WILSY-TENANT-MODULE-WORKSPACE/V1",
                "tenant_id": context.tenant_id,
                "product_id": product_id.value,
                "workspace_key": workspace_key,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "items": list(items),
            }
        return _transaction(product_id, collection_name, read)

    async def create_work_item(
        body: ModuleWorkCreateRequest,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
        context: TenantAuthorizationContext = Depends(create_auth),
    ):
        def create(service: TenantModuleWorkspaceService, session: Any):
            if body.due_at is not None and (body.due_at.tzinfo is None or body.due_at.utcoffset() is None):
                raise HTTPException(status_code=422, detail="DUE_AT_MUST_BE_TIMEZONE_AWARE")
            if (body.source_type is None) != (body.source_id is None):
                raise HTTPException(status_code=422, detail="SOURCE_COORDINATE_INVALID")
            item = service.create(
                tenant_id=context.tenant_id, principal_id=context.identity.identity_id,
                title=body.title, description=body.description,
                kind=ModuleWorkKind(body.kind), priority=ModuleWorkPriority(body.priority),
                due_at=body.due_at, source_type=body.source_type, source_id=body.source_id,
                idempotency_key=idempotency_key, now=datetime.now(timezone.utc), session=session,
            )
            return item.to_dict()
        return _transaction(product_id, collection_name, create)

    async def complete_work_item(
        work_item_id: str,
        body: ModuleWorkCompleteRequest,
        context: TenantAuthorizationContext = Depends(complete_auth),
    ):
        def complete(service: TenantModuleWorkspaceService, session: Any):
            item = service.complete(
                tenant_id=context.tenant_id, work_item_id=work_item_id,
                completion_note=body.completion_note,
                now=datetime.now(timezone.utc), session=session,
            )
            return item.to_dict()
        return _transaction(product_id, collection_name, complete)

    prefix = f"/{slug}/workspace"
    router.add_api_route(prefix, read_workspace, methods=["GET"], name=f"{slug}_workspace_read")
    router.add_api_route(f"{prefix}/work-items", create_work_item, methods=["POST"],
                         status_code=status.HTTP_201_CREATED, name=f"{slug}_work_item_create")
    router.add_api_route(f"{prefix}/work-items/{{work_item_id}}/complete", complete_work_item,
                         methods=["POST"], name=f"{slug}_work_item_complete")


_register_module(
    "operations", _PRODUCTS["operations"],
    read_permission="operations:work_item:read",
    create_permission="operations:work_item:create",
    complete_permission="operations:work_item:complete",
)
_register_module(
    "intelligence", _PRODUCTS["intelligence"],
    read_permission="intelligence:work_item:read",
    create_permission="intelligence:work_item:create",
    complete_permission="intelligence:work_item:complete",
)

__all__ = ["router", "ModuleWorkCreateRequest", "ModuleWorkCompleteRequest"]
