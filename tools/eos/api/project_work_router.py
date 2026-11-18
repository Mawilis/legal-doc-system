"""TITLE: WILSY OS Source-Owned Project Work Command Adapter
VERSION: v1.0.0-EXACT-SOURCE-PROJECT-WORK
AUTHORITY: Python EOS Projects and Operations independently authorize commands.
EPITOME: Create a source-linked Operations task only after exact-tenant Project
         read/update and Operations create admission, preserving the existing
         Operations task ledger and My Work projection instead of duplicating it.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/project_work_router.py
COLLABORATION / OWNERSHIP: Projects registry validates project existence; existing
         TenantModuleWorkspaceService owns Operations task creation and
         entitlement. Existing My Work reads the canonical Operations source.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-EXACT-SOURCE-PROJECT-WORK establishes a single-transaction
         source-coordinate create adapter with exact-tenant/current-principal
         admission, deterministic idempotent replay and committed readback.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No requester-selected tenant, actor, assignee or IAM
         grant. All errors are stable codes without task or tenant disclosure.
TENANT BOUNDARY: Exact selected session tenant plus Projects and Operations
         permissions and independently active product entitlements are mandatory.
AUTHORITY BOUNDARY: A project source link is NOT delegation, assignment, an
         approval or strategy progress. Operations owns task lifecycle.
TRANSACTION BOUNDARY: Projects caller owns one Mongo transaction; the task
         registry receives the same session and makes no nested transaction.
FINANCIAL AUTHORITY BOUNDARY: No financial commands; Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha3_256
from typing import Any, Final, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Response
from pydantic import BaseModel, ConfigDict, Field
from pymongo.errors import PyMongoError

from tools.eos.api.projects_router import (
    _transaction, _require_selected_session_tenant, require_projects_indexes_ready,
)
from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization, TenantAuthorizationContext,
)
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION, HISTORY_COLLECTION,
)
from tools.eos.saas.projects.project_registry import ProjectRegistry
from tools.eos.workspaces.domain.tenant_module_work_item import (
    ModuleWorkItemError, ModuleWorkKind, ModuleWorkPriority,
)
from tools.eos.workspaces.persistence.tenant_module_work_registry import (
    TenantModuleWorkRegistry, ModuleWorkRegistryError, ModuleWorkRegistryConflict,
    ModuleWorkRegistryNotFound,
)
from tools.eos.workspaces.service.tenant_module_workspace_service import (
    TenantModuleWorkspaceError, TenantModuleWorkspaceService,
)


VERSION: Final[str] = "v1.0.0-EXACT-SOURCE-PROJECT-WORK"
PROJECT_SOURCE_TYPE: Final[str] = "PROJECT"
OPERATIONS_COLLECTION: Final[str] = "tenant_operations_work_items"
_PROJECT_READ = RequireTenantAuthorization("project:read", "project_detail")
_PROJECT_UPDATE = RequireTenantAuthorization("project:update", "project_update")
_OPERATIONS_CREATE = RequireTenantAuthorization(
    "operations:work_item:create", "operations_work_item_create",
)


class ProjectWorkCreateRequest(BaseModel):
    """Bounded task intent; no assignee, impersonation or status authority."""

    model_config = ConfigDict(extra="forbid", strict=True)
    title: str = Field(min_length=1, max_length=240)
    description: str = Field(default="", max_length=4000)
    priority: Literal["CRITICAL", "HIGH", "NORMAL", "LOW"] = "NORMAL"
    due_at: datetime | None = None


def require_project_work_indexes_ready(request: Any) -> None:
    """Reject project-work commands before Operations indexes complete startup."""
    if getattr(request.app.state, "project_work_indexes_ready", False) is not True:
        raise HTTPException(status_code=503, detail="PROJECT_WORK_INDEXES_NOT_READY")


router = APIRouter(
    prefix="/projects",
    tags=["Project Work"],
    dependencies=[
        Depends(_require_selected_session_tenant),
        Depends(require_projects_indexes_ready),
        Depends(require_project_work_indexes_ready),
    ],
)


def _operations_service(database: Any) -> tuple[
    TenantModuleWorkspaceService, TenantModuleWorkRegistry,
]:
    """Compose the existing source registry and independently entitled service."""
    work = TenantModuleWorkRegistry(database[OPERATIONS_COLLECTION])
    service = TenantModuleWorkspaceService(
        work, TenantProductId.OPERATIONS,
        database[HISTORY_COLLECTION], database[CURRENT_COLLECTION],
    )
    return service, work


@router.post("/{project_id}/work-items", status_code=201)
def create_project_work_item(
    payload: ProjectWorkCreateRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    project_read: TenantAuthorizationContext = Depends(_PROJECT_READ),
    project_update: TenantAuthorizationContext = Depends(_PROJECT_UPDATE),
    operations_create: TenantAuthorizationContext = Depends(_OPERATIONS_CREATE),
) -> dict[str, object]:
    """Create one project-linked task in the Operations source of truth.

    Three independent current permissions must agree on tenant/principal; both
    product entitlements are independently rechecked in the caller transaction.
    The project may remain Planned; task creation never assigns a project owner
    or department, activates a project, or delegates task ownership.
    """
    response.headers["Cache-Control"] = "no-store"
    principal = project_read.identity.identity_id
    tenant = project_read.tenant_id
    if any(
        context.tenant_id != tenant or context.identity.identity_id != principal
        for context in (project_update, operations_create)
    ):
        raise HTTPException(status_code=403, detail="PROJECT_WORK_AUTHORITY_SCOPE_MISMATCH")
    if idempotency_key != idempotency_key.strip() or not idempotency_key:
        raise HTTPException(status_code=422, detail="PROJECT_WORK_IDEMPOTENCY_KEY_INVALID")
    if payload.due_at is not None and (
        payload.due_at.tzinfo is None or payload.due_at.utcoffset() is None
    ):
        raise HTTPException(status_code=422, detail="PROJECT_WORK_DUE_AT_INVALID")

    def create(projects: ProjectRegistry, session: Any) -> dict[str, object]:
        # The project and the Operations task are observed/committed in the
        # same exact-tenant transaction; failure never leaves a phantom link.
        project = projects.get(tenant_id=tenant, project_id=project_id, session=session)
        database = kernel_db.get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="PROJECT_WORK_SOURCE_UNAVAILABLE")
        service, work_registry = _operations_service(database)
        try:
            # Recheck Operations entitlement even on deterministic replay.
            service._require_product(tenant, session)
            stable_id = "tmw_" + sha3_256(
                (tenant + "\0" + TenantProductId.OPERATIONS.value + "\0" + idempotency_key).encode("utf-8")
            ).hexdigest()[:32]
            due_at = payload.due_at.astimezone(timezone.utc) if payload.due_at else None
            try:
                existing = work_registry.get(
                    tenant_id=tenant, work_item_id=stable_id, session=session,
                )
            except ModuleWorkRegistryNotFound:
                existing = None
            if existing is not None:
                if (
                    existing.source_type != PROJECT_SOURCE_TYPE
                    or existing.source_id != project_id
                    or existing.created_by_principal_id != principal
                    or existing.title != payload.title
                    or existing.description != payload.description
                    or existing.priority is not ModuleWorkPriority(payload.priority)
                    or existing.kind is not ModuleWorkKind.TASK
                    or existing.due_at != due_at
                ):
                    raise HTTPException(status_code=409, detail="PROJECT_WORK_DIVERGENT_REPLAY")
                item = existing
                replayed = True
            else:
                item = service.create(
                    tenant_id=tenant, principal_id=principal, title=payload.title,
                    description=payload.description, kind=ModuleWorkKind.TASK,
                    priority=ModuleWorkPriority(payload.priority), due_at=due_at,
                    source_type=PROJECT_SOURCE_TYPE, source_id=project.project_id,
                    idempotency_key=idempotency_key, now=datetime.now(timezone.utc),
                    session=session,
                )
                replayed = False
            verified = work_registry.get(
                tenant_id=tenant, work_item_id=item.work_item_id, session=session,
            )
            if (
                verified.source_type != PROJECT_SOURCE_TYPE
                or verified.source_id != project.project_id
                or verified.tenant_id != tenant
            ):
                raise HTTPException(status_code=503, detail="PROJECT_WORK_READBACK_INVALID")
        except TenantModuleWorkspaceError as error:
            if error.code == "MODULE_WORK_PRODUCT_NOT_ENTITLED":
                raise HTTPException(status_code=403, detail=error.code) from error
            raise HTTPException(status_code=503, detail=error.code) from error
        except ModuleWorkRegistryConflict as error:
            raise HTTPException(status_code=409, detail=error.code) from error
        except ModuleWorkItemError as error:
            raise HTTPException(status_code=422, detail=error.code) from error
        except ModuleWorkRegistryError as error:
            raise HTTPException(status_code=503, detail=error.code) from error
        except PyMongoError as error:
            raise HTTPException(status_code=503, detail="PROJECT_WORK_SOURCE_UNAVAILABLE") from error
        return {
            "schema": "WILSY-PROJECT-WORK-RESULT/V1",
            "tenant_id": tenant,
            "principal_id": principal,
            "project_id": project.project_id,
            "project_status": project.status.value,
            "work_item": verified.to_dict(),
            "replayed": replayed,
            "authority": {"source": "OPERATIONS_WORK_ITEM", "financial_execution": False},
        }

    return _transaction(project_update, create, write=True)


__all__ = [
    "VERSION", "PROJECT_SOURCE_TYPE", "OPERATIONS_COLLECTION",
    "ProjectWorkCreateRequest", "require_project_work_indexes_ready",
    "create_project_work_item", "router",
]

# ARTIFACT: project_work_router.py
# VERSION: v1.0.0-EXACT-SOURCE-PROJECT-WORK
# AUTHORITY BOUNDARY: independently admitted Project and Operations source commands
# TENANT POSTURE: exact-tenant, exact-principal binding and transactional readback
# FAIL-CLOSED POSTURE: denied/missing entitlement, source conflict, bad replay or outage rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
