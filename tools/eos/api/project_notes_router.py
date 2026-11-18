"""TITLE: WILSY OS Governed Authored Project Notes HTTP Authority
VERSION: v1.0.0-EXACT-PROJECT-NOTE-COMMANDS
AUTHORITY: Existing Python EOS tenant IAM and Projects Registry.
EPITOME: Expose governed authored notes with source-backed listing, creation,
         CAS revision and soft redaction, never substituting notes for approval.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/project_notes_router.py
COLLABORATION / OWNERSHIP: Projects registry proves current project and record
         visibility; ProjectNotesRegistry owns all note state and audit history.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-EXACT-PROJECT-NOTE-COMMANDS binds current tenant and
         author/owner record scope to independently authorized note commands.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Notes are escaped in React, not rendered as HTML;
         no implicit project participation, employee admission or approval.
TENANT BOUNDARY: Authentication, note, project, event and index are exact-tenant.
AUTHORITY BOUNDARY: Creator/current project owner may access these preliminary
         notes; project participation policy must be separately ratified before
         cross-employee note access or mention notifications are enabled.
TRANSACTION BOUNDARY: Reuses Projects' caller-owned Mongo snapshot transaction,
         Projects entitlement checks and atomic notes/event writes.
FINANCIAL AUTHORITY BOUNDARY: No settlement, approval or execution power.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Final

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Response
from pydantic import BaseModel, ConfigDict, Field

from tools.eos.api.projects_router import (
    _transaction, _require_selected_session_tenant, require_projects_indexes_ready,
)
from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization, TenantAuthorizationContext,
)
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.projects.project_registry import ProjectRegistry
from tools.eos.saas.projects.project_notes_registry import (
    COLLECTION, EVENT_COLLECTION,
    ProjectNoteError, ProjectNoteConflict, ProjectNoteNotFound,
    ProjectNotesRegistry,
)


VERSION: Final[str] = "v1.0.0-EXACT-PROJECT-NOTE-COMMANDS"
_READ = RequireTenantAuthorization("project:read", "project_detail")
_UPDATE = RequireTenantAuthorization("project:update", "project_update")


class ProjectNoteCreateRequest(BaseModel):
    """Exact note text only; author and project are server-owned."""

    model_config = ConfigDict(extra="forbid", strict=True)
    body: str = Field(min_length=1, max_length=4000)


class ProjectNoteReviseRequest(BaseModel):
    """Version-guarded note text revision; author remains immutable."""

    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: int = Field(ge=1)
    body: str = Field(min_length=1, max_length=4000)


class ProjectNoteRedactRequest(BaseModel):
    """Soft-redact command retaining the immutable revision event ledger."""

    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: int = Field(ge=1)


def require_project_notes_indexes_ready(request: Any) -> None:
    """Refuse note operations before startup creates source indexes."""
    if getattr(request.app.state, "project_notes_indexes_ready", False) is not True:
        raise HTTPException(status_code=503, detail="PROJECT_NOTES_INDEXES_NOT_READY")


router = APIRouter(
    prefix="/projects", tags=["Project Notes"],
    dependencies=[
        Depends(_require_selected_session_tenant),
        Depends(require_projects_indexes_ready),
        Depends(require_project_notes_indexes_ready),
    ],
)


def _same_scope(
    reader: TenantAuthorizationContext,
    editor: TenantAuthorizationContext,
) -> None:
    """Require independent read/write admission for the same current session."""
    if (
        reader.tenant_id != editor.tenant_id
        or reader.identity.identity_id != editor.identity.identity_id
    ):
        raise HTTPException(status_code=403, detail="PROJECT_NOTE_AUTHORITY_SCOPE_MISMATCH")


def _execute(
    context: TenantAuthorizationContext,
    project_id: str,
    operation: Callable[[ProjectNotesRegistry, Any], dict[str, object]],
    *,
    write: bool = False,
) -> dict[str, object]:
    """Compose project visibility, notes persistence and one transaction."""
    def invoke(projects: ProjectRegistry, session: Any) -> dict[str, object]:
        project = projects.get(
            tenant_id=context.tenant_id, project_id=project_id, session=session,
        )
        actor = context.identity.identity_id
        if actor not in {project.created_by_principal_id, project.owner_principal_id}:
            # Until the independently approved participant registry exists,
            # no tenant-wide project-read role reveals another author's notes.
            raise HTTPException(status_code=403, detail="PROJECT_NOTE_RECORD_SCOPE_REQUIRED")
        database = kernel_db.get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="PROJECT_NOTE_SOURCE_UNAVAILABLE")
        notes = ProjectNotesRegistry(database[COLLECTION], database[EVENT_COLLECTION])
        try:
            return operation(notes, session)
        except ProjectNoteNotFound as error:
            raise HTTPException(status_code=404, detail=error.code) from error
        except ProjectNoteConflict as error:
            raise HTTPException(status_code=409, detail=error.code) from error
        except ProjectNoteError as error:
            if error.code.endswith("_INVALID"):
                raise HTTPException(status_code=422, detail=error.code) from error
            raise HTTPException(status_code=503, detail=error.code) from error
    return _transaction(context, invoke, write=write)


def _result(
    context: TenantAuthorizationContext, project_id: str,
    note: dict[str, object],
) -> dict[str, object]:
    """Wrap committed, bounded note source truth in an exact-scope envelope."""
    return {
        "schema": "WILSY-PROJECT-NOTE-RESULT/V1",
        "tenant_id": context.tenant_id,
        "principal_id": context.identity.identity_id,
        "project_id": project_id,
        "note": note,
        "authority": {"source": "PYTHON_EOS_PROJECT_NOTES", "financial_execution": False},
    }


@router.get("/{project_id}/notes")
def list_project_notes(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Read one exact-authority, exact-project bounded page of note revisions."""
    response.headers["Cache-Control"] = "no-store"
    def read(notes: ProjectNotesRegistry, session: Any) -> dict[str, object]:
        items = notes.list_for_project(
            tenant_id=context.tenant_id, project_id=project_id,
            limit=limit, offset=offset, session=session,
        )
        return {
            "schema": "WILSY-PROJECT-NOTES-LIST/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id,
            "items": list(items),
            "limit": limit, "offset": offset,
        }
    return _execute(context, project_id, read)


@router.post("/{project_id}/notes", status_code=201)
def create_project_note(
    payload: ProjectNoteCreateRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    reader: TenantAuthorizationContext = Depends(_READ),
    editor: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Create an authored note; same-key replay never adds a second note."""
    response.headers["Cache-Control"] = "no-store"
    _same_scope(reader, editor)
    return _execute(editor, project_id, lambda notes, session: _result(
        editor, project_id, notes.create(
            tenant_id=editor.tenant_id, project_id=project_id,
            actor_principal_id=editor.identity.identity_id,
            body=payload.body, idempotency_key=idempotency_key,
            occurred_at=datetime.now(timezone.utc), session=session,
        ),
    ), write=True)


@router.patch("/{project_id}/notes/{note_id}")
def revise_project_note(
    payload: ProjectNoteReviseRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    note_id: str = Path(pattern=r"^pnote-[0-9a-f]{32}$"),
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    reader: TenantAuthorizationContext = Depends(_READ),
    editor: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Revise only the authenticated note author's expected revision."""
    response.headers["Cache-Control"] = "no-store"
    _same_scope(reader, editor)
    return _execute(editor, project_id, lambda notes, session: _result(
        editor, project_id, notes.revise(
            tenant_id=editor.tenant_id, project_id=project_id, note_id=note_id,
            actor_principal_id=editor.identity.identity_id,
            expected_revision=payload.expected_revision, body=payload.body,
            redact=False, idempotency_key=idempotency_key,
            occurred_at=datetime.now(timezone.utc), session=session,
        ),
    ), write=True)


@router.post("/{project_id}/notes/{note_id}/redact")
def redact_project_note(
    payload: ProjectNoteRedactRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    note_id: str = Path(pattern=r"^pnote-[0-9a-f]{32}$"),
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    reader: TenantAuthorizationContext = Depends(_READ),
    editor: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Retain event evidence while removing note body from current projection."""
    response.headers["Cache-Control"] = "no-store"
    _same_scope(reader, editor)
    return _execute(editor, project_id, lambda notes, session: _result(
        editor, project_id, notes.revise(
            tenant_id=editor.tenant_id, project_id=project_id, note_id=note_id,
            actor_principal_id=editor.identity.identity_id,
            expected_revision=payload.expected_revision, body=None,
            redact=True, idempotency_key=idempotency_key,
            occurred_at=datetime.now(timezone.utc), session=session,
        ),
    ), write=True)


__all__ = [
    "VERSION", "ProjectNoteCreateRequest", "ProjectNoteReviseRequest",
    "ProjectNoteRedactRequest", "require_project_notes_indexes_ready",
    "list_project_notes", "create_project_note", "revise_project_note",
    "redact_project_note", "router",
]

# ARTIFACT: project_notes_router.py
# VERSION: v1.0.0-EXACT-PROJECT-NOTE-COMMANDS
# AUTHORITY BOUNDARY: project read/update, author/owner scoped note commands only
# TENANT POSTURE: exact selected tenant, project and versioned-note persistence
# FAIL-CLOSED POSTURE: unverified author, missing project or index, conflict deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
