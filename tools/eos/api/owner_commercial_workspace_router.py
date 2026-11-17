"""TITLE: WILSY OS CRM Owner Commercial Workspace HTTP Router
VERSION: v1.3.0-CRM-CORE-ADMISSION-ERRORS
AUTHORITY: WILSY OS Python EOS institutional CRM API.
EPITOME: Expose source-owned CRM owner work reads and commands through exact
         tenant authorization, entitlement admission and Mongo transactions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/owner_commercial_workspace_router.py
COLLABORATION / OWNERSHIP: Tenant IAM dependency, CRM owner source service,
         tenant-scoped work registry and Python EOS API gateway.
CERTIFICATION / UPDATE DATE: 2026-11-17
CHANGELOG: v1.3.0-CRM-CORE-ADMISSION-ERRORS maps exact CRM Core
           entitlement absence to 403 and unverifiable CRM Core evidence
           to 503 without using Legal authorization or granting access.
CHANGELOG: v1.2.1-EXPLICIT-FULL-EDIT-REQUEST requires every editable
           task field in an explicit full-revision PATCH; omitted description,
           priority or deadline can no longer silently reset source state.
CHANGELOG: v1.2.0-EXACT-CRM-WORK-EDIT-HTTP adds a dedicated PATCH
           command gated by crm:work_item:update, active entitlement, strict
           request shape, exact actor, idempotency key and source-owned CAS;
           the source edit history is read-only and shares CRM read authority.
           Existing create/complete and denial contracts are unchanged.
CHANGELOG: v1.1.0-AUTHORIZED-CRM-WORK-DETAIL-READ exposes GET /work-items/{work_item_id}
           through existing CRM read permission for active or completed source
           records; absence returns 404 without disclosing foreign tenants.
           Existing create and complete HTTP contracts are preserved.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No new IAM grants, cross-source reads or logs of
                            customer payloads, work content or completion notes.
TENANT BOUNDARY: Every lookup uses authorized context.tenant_id; no wildcard.
AUTHORITY BOUNDARY: CRM source owns records and mutations, no new write route.
TRANSACTION / IDEMPOTENCY BOUNDARY: Existing caller-owned Mongo session with
                                   snapshot read; no new command replay.
FINANCIAL AUTHORITY BOUNDARY: No payments, Kennel EOS exclusively executes.
FAIL-CLOSED POSTURE: Unauthorized context, entitlement outage or invalid
                     source evidence never becomes a verified empty record.
"""
from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization, TenantAuthorizationContext,
)
from tools.eos.crm.domain.owner_commercial_work_item import OwnerWorkKind, OwnerWorkPriority, OwnerWorkItemError
from tools.eos.crm.persistence.owner_commercial_work_registry import (
    COLLECTION, EVENTS_COLLECTION, OwnerCommercialWorkRegistry, OwnerWorkRegistryError, OwnerWorkRegistryConflict, OwnerWorkRegistryNotFound, ensure_indexes,
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

logger = logging.getLogger("WilsyOS.API.OwnerCommercialWorkspace")

_READ = RequireTenantAuthorization("crm:work_item:read", "crm_work_item_read")
_CREATE = RequireTenantAuthorization("crm:work_item:create", "crm_work_item_create")
_COMPLETE = RequireTenantAuthorization("crm:work_item:complete", "crm_work_item_complete")
_UPDATE = RequireTenantAuthorization("crm:work_item:update", "crm_work_item_update")


class OwnerWorkCompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    completion_note: str = Field(min_length=1, max_length=1000)


class OwnerWorkReviseRequest(BaseModel):
    """Only source-owned editable fields and optimistic revision evidence.

    Tenant, actor and assignment are never accepted from the caller. HTTP
    requires separate CRM edit IAM and current entitlement, and the registry
    enforces transactional compare-and-set and idempotent audit.
    """
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=240)
    description: str = Field(max_length=4000)
    priority: Literal["CRITICAL", "HIGH", "NORMAL", "LOW"]
    due_at: datetime | None
    expected_updated_at: datetime


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
        OwnerCommercialWorkRegistry(
            database.get_collection(
                COLLECTION, write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
            database.get_collection(
                EVENTS_COLLECTION, write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
        ),
        subscription_registry_module.subscriptions_collection,
        database.get_collection(HISTORY_COLLECTION),
        database.get_collection(CURRENT_COLLECTION),
    )


def _transaction(callback):
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="OWNER_WORK_DATABASE_UNAVAILABLE")
    try:
        ensure_indexes(database.get_collection(COLLECTION), database.get_collection(EVENTS_COLLECTION))
        with client.start_session() as session:
            return session.with_transaction(
                lambda current: callback(_service(database), current),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except OwnerCommercialWorkspaceError as error:
        code = error.code
        if code in {"OWNER_WORK_CRM_NOT_ENTITLED", "OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE"}:
            raise HTTPException(status_code=403 if code.endswith("NOT_ENTITLED") else 503, detail=code) from error
        raise HTTPException(status_code=503, detail="OWNER_WORK_SERVICE_UNAVAILABLE") from error
    except OwnerWorkRegistryNotFound as error:
        raise HTTPException(status_code=404, detail="OWNER_WORK_NOT_FOUND") from error
    except OwnerWorkRegistryConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except OwnerWorkRegistryError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except OwnerWorkItemError as error:
        raise HTTPException(status_code=422, detail=error.code) from error
    except HTTPException:
        raise
    except Exception as error:
        cause = error.__cause__
        traceback = error.__traceback__
        while traceback is not None and traceback.tb_next is not None:
            traceback = traceback.tb_next
        frame = traceback.tb_frame if traceback is not None else None
        location = (
            f"{frame.f_code.co_filename.rsplit('/', 1)[-1]}:{traceback.tb_lineno}:{frame.f_code.co_name}"
            if frame is not None and traceback is not None else None
        )
        logger.error(
            "OWNER_WORK_TRANSACTION_FAILURE error_type=%s error_code=%s cause_type=%s cause_code=%s attribute_name=%s object_type=%s location=%s",
            type(error).__name__,
            getattr(error, "code", None),
            type(cause).__name__ if cause is not None else None,
            getattr(cause, "code", None) if cause is not None else None,
            getattr(error, "name", None),
            type(getattr(error, "obj", None)).__name__,
            location,
        )
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


@router.get("/work-items/{work_item_id}")
async def read_owner_work_item(
    work_item_id: str,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Read exact tenant-owned persisted CRM work, including completed evidence.

    Existing CRM work-item read authorization and active entitlement are
    required. The source registry returns only same-tenant records. Missing
    and cross-tenant work both resolve to OWNER_WORK_NOT_FOUND without
    disclosing another tenant's record. This endpoint cannot mutate work,
    infer an actor, or assert a source event history not persisted by CRM.
    """
    def read(service: OwnerCommercialWorkspaceService, session: Any):
        item = service.read_work_item(
            tenant_id=context.tenant_id, work_item_id=work_item_id,
            session=session,
        )
        return item.to_dict()
    return _transaction(read)



@router.patch("/work-items/{work_item_id}")
async def revise_owner_work_item(
    work_item_id: str,
    body: OwnerWorkReviseRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Edit only source-owned fields after independent CRM update permission.

    The token-bound actor and tenant are supplied by EOS, not request data.
    Current entitlement is checked inside the transaction. Stale revisions,
    terminal work, changed replay payloads and foreign tenants fail closed;
    a successful source edit and audit event commit atomically.
    """
    def revise(service: OwnerCommercialWorkspaceService, session: Any):
        for instant in (body.expected_updated_at, body.due_at):
            if instant is not None and (instant.tzinfo is None or instant.utcoffset() is None):
                raise HTTPException(status_code=422, detail="WORK_TIMESTAMP_MUST_BE_TIMEZONE_AWARE")
        item = service.revise(
            tenant_id=context.tenant_id, work_item_id=work_item_id,
            actor_principal_id=context.identity.identity_id,
            title=body.title, description=body.description,
            priority=OwnerWorkPriority(body.priority), due_at=body.due_at,
            expected_updated_at=body.expected_updated_at,
            idempotency_key=idempotency_key,
            now=datetime.now(timezone.utc), session=session,
        )
        return item.to_dict()
    return _transaction(revise)


@router.get("/work-items/{work_item_id}/history")
async def read_owner_work_item_history(
    work_item_id: str,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Return only persisted own-tenant CRM edit evidence under current read IAM.

    Legacy records with no edit events have an empty edit history; no
    synthetic history or workforce actor name is supplied. The source
    registry and entitlement service enforce exact tenant reads.
    """
    def history(service: OwnerCommercialWorkspaceService, session: Any):
        return {
            "schema": "WILSY-OWNER-COMMERCIAL-WORK-HISTORY/V1",
            "tenant_id": context.tenant_id,
            "work_item_id": work_item_id,
            "events": list(service.revision_history(
                tenant_id=context.tenant_id, work_item_id=work_item_id,
                session=session,
            )),
        }
    return _transaction(history)


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


__all__ = ["router", "OwnerWorkCreateRequest", "OwnerWorkReviseRequest", "OwnerWorkCompleteRequest", "read_owner_work_item", "read_owner_work_item_history", "revise_owner_work_item"]

# ARTIFACT: tools/eos/api/owner_commercial_workspace_router.py
# VERSION: v1.3.0-CRM-CORE-ADMISSION-ERRORS
# AUTHORITY BOUNDARY: Existing CRM read IAM and owner source entitlement.
# TENANT POSTURE: Authorized tenant only; foreign work is indistinguishable from absent.
# FAIL-CLOSED POSTURE: 401/403/404/503 remain distinct without fabricated evidence.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
