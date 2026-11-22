"""TITLE: WILSY OS Project Work Daily Attention Source Adapter
VERSION: v1.2.0-BATCH-VERIFIED-SOURCE-WORK-PURPOSE
AUTHORITY: Python EOS Projects IAM, record-scoped participation and task registry.
EPITOME: Project tasks enter My Work only with current participant authorization,
         exact tenant and current project participation, inside source transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/project_attention_source.py
COLLABORATION / OWNERSHIP: unified_my_work_router admits independent participant
         read IAM; Projects router owns entitlement, project/participant reads
         and caller-owned majority MongoDB transactions; task registry owns work.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.2.0-BATCH-VERIFIED-SOURCE-WORK-PURPOSE
         reads bounded source/audit evidence after exact participant
         admission in one batched authenticated snapshot, not one query per
         task. Missing classification remains visible, never inferred.
CHANGELOG: v1.1.2-STALE-PURPOSE-UNCLASSIFIED-PROJECTION
         withholds old audited purpose evidence whenever source task revision
         changed, retaining the visible UNCLASSIFIED task without guessing.
CHANGELOG: v1.1.1-STRICT-AUDIENCE-PROJECTION-ENVELOPE
         strips command-only purpose revision before passing verified purpose
         into the strict unified My Work evidence contract.
CHANGELOG: v1.1.0-VERIFIED-PROJECT-WORK-PURPOSE-PROJECTION reads
         audited source and event purpose evidence in the same admitted
         exact-project snapshot; stale task revisions remain UNCLASSIFIED.
         Neither source role nor purpose labels can grant commands.
CHANGELOG: v1.0.0-EXACT-PARTICIPANT-ATTENTION-SOURCE maps delegated and
         blocked project work to the existing source-owned queue contract.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No task bypass via founder/owner status; no global
         directory enumeration, fabricated completions or notification badges.
TENANT BOUNDARY: Every task query, participation and project record is scoped
         by the same authenticated tenant and principal inside one read snapshot.
AUTHORITY BOUNDARY: Read-only projection; task commands remain Projects-owned.
TRANSACTION BOUNDARY: Projects router owns Mongo session, snapshot and retries;
         this adapter never opens a transaction or performs writes.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS is the exclusive executor.
"""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from pymongo.errors import PyMongoError

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.api import projects_router as projects
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.projects.project_work_purpose_registry import (
    COLLECTION as PURPOSE_COLLECTION,
    EVENT_COLLECTION as PURPOSE_EVENT_COLLECTION,
    ProjectWorkPurposeRegistry, WorkPurposeError,
)
from tools.eos.saas.projects.project_task_registry import (
    COLLECTION as TASK_COLLECTION, ProjectTask, ProjectTaskError,
)

VERSION = "v1.2.0-BATCH-VERIFIED-SOURCE-WORK-PURPOSE"
_ACTIVE = frozenset({"TODO", "IN_PROGRESS", "BLOCKED"})
_STATUS = {"TODO": "OPEN", "IN_PROGRESS": "IN_PROGRESS", "BLOCKED": "BLOCKED"}
# Source read is bounded to prevent a single principal's queue from starving EOS.
# Crossing this safety cap is an explicit source outage, never a fabricated
# zero or truncated list. Enterprise paging/streaming is a follow-on milestone.
_MAX_ATTENTION_TASKS = 10000


def read_project_attention(
    *, context: TenantAuthorizationContext, tenant_id: str,
    principal_id: str,
) -> dict[str, Any]:
    """Read exact-assignee projects under independently admitted participant IAM.

    The passed context must represent the same authenticated principal and
    tenant. Each project also requires an ACTIVE exact-project CONTRIBUTOR
    record. Any source/transport failure rejects the entire My Work aggregate.
    This adapter cannot grant owner privileges or complete a task.
    """
    if (
        context.tenant_id != tenant_id
        or context.identity.identity_id != principal_id
        or context.decision.authorization_role not in {
            "PROJECTS_PARTICIPANT_CONTRIBUTOR",
            "PROJECTS_PARTICIPANT_VIEWER",
        }
    ):
        raise HTTPException(status_code=403, detail="PROJECT_ATTENTION_SCOPE_DENIED")

    def read(registry: Any, session: Any) -> dict[str, Any]:
        database = kernel_db.get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="PROJECT_ATTENTION_SOURCE_UNAVAILABLE")
        collection = database[TASK_COLLECTION]
        purposes = ProjectWorkPurposeRegistry(
            database[PURPOSE_COLLECTION], database[PURPOSE_EVENT_COLLECTION],
        )
        query = {
            "tenant_id": tenant_id,
            "assignee_principal_id": principal_id,
            "status": {"$in": sorted(_ACTIVE)},
        }
        rows: list[dict[str, Any]] = []
        verified_tasks: list[ProjectTask] = []
        validated_projects: set[str] = set()
        rejected_projects: set[str] = set()
        try:
            cursor = collection.find(query, session=session).batch_size(100)
            for raw in cursor:
                if len(rows) >= _MAX_ATTENTION_TASKS:
                    raise HTTPException(status_code=503, detail="PROJECT_ATTENTION_CAPACITY_EXCEEDED")
                task = ProjectTask.hydrate({
                    key: value for key, value in raw.items() if key != "_id"
                })
                if (
                    task.tenant_id != tenant_id
                    or task.assignee_principal_id != principal_id
                    or task.status not in _ACTIVE
                ):
                    raise HTTPException(status_code=503, detail="PROJECT_ATTENTION_SOURCE_INVALID")
                if task.project_id in rejected_projects:
                    continue
                if task.project_id not in validated_projects:
                    try:
                        _project, participant_store = projects._require_current_project_participation(
                            context, registry, task.project_id, session,
                        )
                        assignment = participant_store.get(
                            tenant_id=tenant_id, project_id=task.project_id,
                            principal_id=principal_id, session=session,
                        )
                    except projects.ProjectParticipantNotFound:
                        rejected_projects.add(task.project_id)
                        continue
                    except projects.ProjectNotFound:
                        rejected_projects.add(task.project_id)
                        continue
                    if assignment.role != "CONTRIBUTOR":
                        rejected_projects.add(task.project_id)
                        continue
                    validated_projects.add(task.project_id)
                # A date-only deadline has no source timezone or exact instant.
                # Never fabricate UTC 'overdue' truth from a calendar date.
                verified_tasks.append(task)
                rows.append({
                    "tenant_id": tenant_id,
                    "revision": task.revision,
                    "audience_evidence": None,
                    "work_item_id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "status": _STATUS[task.status],
                    "priority": "NORMAL",
                    "kind": task.kind,
                    "due_at": None,
                    "due_date": task.due_date,
                    "project_id": task.project_id,
                    "owner_principal_id": task.assignee_principal_id,
                    "created_by_principal_id": task.created_by_principal_id,
                    "updated_at": task.updated_at.isoformat(),
                })
            evidence_by_id = purposes.current_for_tasks(
                tasks=verified_tasks, session=session,
            )
            for row in rows:
                claim = evidence_by_id[row["work_item_id"]]
                if claim is not None and claim["audience"] != "UNCLASSIFIED":
                    row["audience_evidence"] = {
                        key: value for key, value in claim.items()
                        if key != "purpose_revision"
                    }
        except PyMongoError as error:
            raise HTTPException(
                status_code=503, detail="PROJECT_ATTENTION_SOURCE_UNAVAILABLE",
            ) from error
        except WorkPurposeError as error:
            raise HTTPException(
                status_code=503, detail="PROJECT_ATTENTION_PURPOSE_SOURCE_INVALID",
            ) from error
        except ProjectTaskError as error:
            raise HTTPException(
                status_code=503, detail="PROJECT_ATTENTION_SOURCE_INVALID",
            ) from error
        return {"tenant_id": tenant_id, "items": rows}

    return projects._transaction(context, read)


__all__ = ["VERSION", "read_project_attention"]

# ARTIFACT: project_attention_source.py
# VERSION: v1.2.0-BATCH-VERIFIED-SOURCE-WORK-PURPOSE
# AUTHORITY BOUNDARY: read-only current participant source, no mutations
# TENANT POSTURE: exact assignee, same tenant and active project participation
# FAIL-CLOSED POSTURE: corrupt, stale, oversized or unavailable source denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
