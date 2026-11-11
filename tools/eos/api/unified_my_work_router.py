"""TITLE: WILSY OS Authenticated Unified My Work Source Aggregation
VERSION: v1.1.0-NONBLOCKING-SOURCE-READ-TRANSACTIONS
AUTHORITY: WILSY OS Python EOS; canonical source registries own business truth.
EPITOME: Compose only independently authenticated and entitled module work in
         exact tenant scope without blocking FastAPI's event loop on PyMongo.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/unified_my_work_router.py
COLLABORATION / OWNERSHIP: TenantAuthorizationHTTP owns current IAM;
         Legal Operations, CRM and tenant module source services own reads,
         transactions and durable state; projection owns read shape.
CERTIFICATION / UPDATE DATE: 2026-11-11
CHANGELOG: v1.1.0-NONBLOCKING-SOURCE-READ-TRANSACTIONS runs synchronous
           MongoDB source reads and projection in
           FastAPI's request threadpool; source IAM, isolation and fail-closed
           results remain unchanged. v1.0.0 composed independent module work.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No tokens, personal data or work bodies logged.
TENANT BOUNDARY: Exact authenticated principal, tenant and source IAM required.
AUTHORITY BOUNDARY: Read-only aggregator; no work creation, approval or grants.
TRANSACTION / IDEMPOTENCY BOUNDARY: Source-owned independent transactions;
         no cross-source transaction and no new write authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes finances.
FAIL-CLOSED POSTURE: No authorization, malformed source or outage converts
         into a fabricated cleared or successful enterprise queue.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from starlette.concurrency import run_in_threadpool

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
    tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    identity: Any = Depends(get_current_identity),
    legal_context: TenantAuthorizationContext | None = Depends(_LEGAL_READ),
    operations_context: TenantAuthorizationContext | None = Depends(_OPERATIONS_READ),
    intelligence_context: TenantAuthorizationContext | None = Depends(_INTELLIGENCE_READ),
    crm_context: TenantAuthorizationContext | None = Depends(_CRM_READ),
) -> dict[str, Any]:
    """Return only independently authorized work for the current principal/capacity."""

    if not isinstance(tenant_id, str) or not tenant_id or tenant_id != tenant_id.strip():
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

    # A partial source set is valid, but a tenant scope with no independently
    # authorized source is not a workspace. In particular, caller-supplied
    # foreign tenant identifiers must never produce a successful empty view.
    if not any(context is not None for context in contexts):
        raise HTTPException(status_code=403, detail="MY_WORK_NO_AUTHORIZED_SOURCE")

    def compose_source_projection() -> dict[str, Any]:
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

    # Every source transaction uses synchronous PyMongo. Keep its whole read
    # and projection in the bounded request threadpool, never the ASGI loop.
    return await run_in_threadpool(compose_source_projection)


__all__ = ["router", "read_my_work"]


# ARTIFACT: tools/eos/api/unified_my_work_router.py
# VERSION: v1.1.0-NONBLOCKING-SOURCE-READ-TRANSACTIONS
# AUTHORITY BOUNDARY: Authenticated source reads only; no commands.
# TENANT POSTURE: Exact IAM source admission required.
# FAIL-CLOSED POSTURE: Denied or unavailable source never invents clearance.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
