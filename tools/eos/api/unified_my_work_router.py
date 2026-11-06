"""Authenticated My Work aggregation over independently authorized EOS sources.

Each source is admitted by its own canonical permission-operation pair and is
read through its owning module's existing service and transaction boundary.
A source denial omits only that source; any authorization or persistence outage
fails the request. This router owns no work-item persistence or commands.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException

from tools.eos.api.tenant_authorization_http import (
    OptionalTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.auth.authentication import get_current_identity
from tools.eos.workspaces.service.unified_my_work_projection import (
    UnifiedMyWorkProjectionError,
    build_unified_my_work,
)

from tools.eos.api import legal_operations_router as legal_source
from tools.eos.api import owner_commercial_workspace_router as crm_source
from tools.eos.api import tenant_module_workspace_router as module_source

router = APIRouter(prefix="/my-work", tags=["My Work"])

_LEGAL_READ = OptionalTenantAuthorization(
    "legal_operations:productive_work:read", "legal_productive_work_read"
)
_OPERATIONS_READ = OptionalTenantAuthorization(
    "operations:work_item:read", "operations_work_item_read"
)
_INTELLIGENCE_READ = OptionalTenantAuthorization(
    "intelligence:work_item:read", "intelligence_work_item_read"
)
_CRM_READ = OptionalTenantAuthorization("crm:work_item:read", "crm_work_item_read")


def _assert_context(
    context: TenantAuthorizationContext | None,
    *,
    tenant_id: str,
    principal_id: str,
) -> None:
    if context is not None and (
        context.tenant_id != tenant_id
        or context.identity.identity_id != principal_id
    ):
        raise HTTPException(status_code=503, detail="MY_WORK_AUTHORIZATION_CONTEXT_INCONSISTENT")


def _read_legal(*, tenant_id: str, principal_id: str) -> dict[str, Any]:
    def read(session: Any, database: Any) -> Any:
        return legal_source._productive_work_service(database).project(
            tenant_id=tenant_id,
            principal_id=principal_id,
            as_of=datetime.now(timezone.utc),
            session=session,
        )

    projection = legal_source._productive_work_projection_transaction(read)
    payload = legal_source._productive_work_payload(projection)
    return {
        "tenant_id": tenant_id,
        "assigned_work_items": payload["assigned_work_items"],
        "supervised_work_items": payload["supervised_work_items"],
    }


def _read_module(slug: str, *, tenant_id: str) -> dict[str, Any] | None:
    product_id, workspace_key, collection_name, _operation_prefix = (
        module_source._PRODUCTS[slug]
    )

    def read(service: Any, session: Any) -> dict[str, Any]:
        readback = service.read_workspace(
            tenant_id=tenant_id,
            now=datetime.now(timezone.utc),
            session=session,
        )
        return {
            "tenant_id": tenant_id,
            "product_id": product_id.value,
            "workspace_key": workspace_key,
            **readback,
            "items": list(readback["items"]),
        }

    try:
        return module_source._transaction(product_id, collection_name, read)
    except HTTPException as error:
        if error.status_code == 403 and error.detail == "MODULE_WORK_PRODUCT_NOT_ENTITLED":
            return None
        raise


def _read_crm(*, tenant_id: str) -> dict[str, Any] | None:
    def read(service: Any, session: Any) -> dict[str, Any]:
        queue = service.daily_queue(
            tenant_id=tenant_id,
            now=datetime.now(timezone.utc),
            session=session,
        )
        return {"tenant_id": tenant_id, "items": list(queue)}

    try:
        return crm_source._transaction(read)
    except HTTPException as error:
        if error.status_code == 403 and error.detail == "OWNER_WORK_LEGAL_NOT_ENTITLED":
            return None
        raise


@router.get("")
async def read_my_work(
    tenant_id: str = Header(alias="X-Tenant-ID", min_length=1),
    identity: Any = Depends(get_current_identity),
    legal_context: TenantAuthorizationContext | None = Depends(_LEGAL_READ),
    operations_context: TenantAuthorizationContext | None = Depends(_OPERATIONS_READ),
    intelligence_context: TenantAuthorizationContext | None = Depends(_INTELLIGENCE_READ),
    crm_context: TenantAuthorizationContext | None = Depends(_CRM_READ),
) -> dict[str, Any]:
    """Return only independently authorized work for the current principal/capacity."""

    if not tenant_id or tenant_id != tenant_id.strip():
        raise HTTPException(status_code=403, detail="TENANT_SCOPE_REQUIRED")

    principal_id = identity.identity_id
    contexts = (
        legal_context,
        operations_context,
        intelligence_context,
        crm_context,
    )
    for context in contexts:
        _assert_context(context, tenant_id=tenant_id, principal_id=principal_id)

    # None means a canonical 403 for that source only. A 503 or any unexpected
    # authorization failure is raised by the dependency and never becomes empty.
    legal = (
        _read_legal(tenant_id=tenant_id, principal_id=principal_id)
        if legal_context is not None else None
    )
    operations = (
        _read_module("operations", tenant_id=tenant_id)
        if operations_context is not None else None
    )
    intelligence = (
        _read_module("intelligence", tenant_id=tenant_id)
        if intelligence_context is not None else None
    )
    crm = _read_crm(tenant_id=tenant_id) if crm_context is not None else None

    try:
        result = build_unified_my_work(
            tenant_id=tenant_id,
            principal_id=principal_id,
            now=datetime.now(timezone.utc),
            legal=legal,
            operations=operations,
            intelligence=intelligence,
            crm=crm,
        )
    except UnifiedMyWorkProjectionError as error:
        raise HTTPException(
            status_code=503,
            detail="MY_WORK_SOURCE_PROJECTION_INVALID",
        ) from error

    result["sources_included"] = [
        source for source, payload in (
            ("LEGAL", legal),
            ("OPERATIONS", operations),
            ("INTELLIGENCE", intelligence),
            ("CRM", crm),
        ) if payload is not None
    ]
    result["authority"]["permits_source_commands"] = False
    result["authority"]["source_read_transactions"] = "INDEPENDENT_OWNER_BOUNDARIES"
    return result


__all__ = ["router", "read_my_work"]
