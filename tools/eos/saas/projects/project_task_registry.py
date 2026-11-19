"""TITLE: WILSY OS Enterprise Project Task Transaction Registry
VERSION: v1.2.0-TASK-ACTIVITY-EVENT-READ
AUTHORITY: Python EOS canonical tenant/project task and milestone source truth.
EPITOME: Source-backed tasks, nested subtasks, milestones, dependencies, due
         dates, assignees and audited lifecycle CAS with idempotent command replay.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/projects/project_task_registry.py
COLLABORATION / OWNERSHIP: Projects router admits IAM, participant assignment,
         currentness, project existence and entitlement. EOS owns transactions.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.2.0-TASK-ACTIVITY-EVENT-READ reads bounded immutable lifecycle events in newest revision order with exact-tenant/project/task binding, source validation and privacy-preserving projection. No command or audit mutation.
CHANGELOG: v1.1.0-REVISIONED-PROJECT-TASK-EDITING adds guarded title, description,
due date and assignee editing for active work, durable replay, CAS and
immutable audit without rewriting dependency or completion history.
CHANGELOG: v1.2.0-TASK-ACTIVITY-EVENT-READ establishes an immutable
         project-work aggregate and exact-tenant Mongo transaction registry.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Bounded plain text; no HTML, inferred approval,
         automatic owner privilege or fabricated completion evidence.
TENANT BOUNDARY: Every query binds exact tenant and project; no root fallback.
AUTHORITY BOUNDARY: Domain lifecycle and CAS are not permission grants;
         caller must require independent current IAM/entitlement/participant scope.
TRANSACTION BOUNDARY: Caller-owned MongoDB session and majority transaction.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from hashlib import sha3_512
from hmac import compare_digest
import json
import re
from typing import Any, Final, Literal

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

VERSION: Final[str] = "v1.2.0-TASK-ACTIVITY-EVENT-READ"
SCHEMA: Final[str] = "wilsy.project.task.v1"
COLLECTION: Final[str] = "wilsy_project_tasks"
EVENT_COLLECTION: Final[str] = "wilsy_project_task_events"
_PROJECT = re.compile(r"^prj-[0-9a-f]{48}$")
_TASK = re.compile(r"^ptk-[0-9a-f]{48}$")
_DIGEST = re.compile(r"^[0-9a-f]{128}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_KINDS: Final[frozenset[str]] = frozenset({"TASK", "MILESTONE"})
_STATES: Final[frozenset[str]] = frozenset({
    "TODO", "IN_PROGRESS", "BLOCKED", "DONE", "CANCELLED",
})
_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "TODO": frozenset({"IN_PROGRESS", "BLOCKED", "CANCELLED"}),
    "IN_PROGRESS": frozenset({"BLOCKED", "DONE", "CANCELLED"}),
    "BLOCKED": frozenset({"IN_PROGRESS", "CANCELLED"}),
    "DONE": frozenset(),
    "CANCELLED": frozenset(),
}
_FORBIDDEN_TENANTS = frozenset({
    "MASTER", "GLOBAL_ROOT", "WILSY_ROOT", "WILSY_MASTER",
    "WILSY_GLOBAL_ROOT", "SOVEREIGN_ROOT",
})


class ProjectTaskError(RuntimeError):
    """One safe, stable task-validation or source-integrity error code."""

    def __init__(self, code: str) -> None:
        """Preserve non-sensitive failure classification only."""
        self.code = code
        super().__init__(code)


class ProjectTaskConflict(ProjectTaskError):
    """Task CAS, dependency gate or divergent command replay failure."""


class ProjectTaskNotFound(ProjectTaskError):
    """Exact-tenant task absent, foreign or hidden by source scope."""


def _id(value: object, kind: str) -> str:
    """Validate exact nonempty opaque principal/tenant/record coordinates."""
    if (
        not isinstance(value, str) or not 1 <= len(value) <= 180
        or value != value.strip()
        or any(ord(ch) < 33 for ch in value)
    ):
        raise ProjectTaskError("PROJECT_TASK_" + kind + "_INVALID")
    if kind == "TENANT" and value.upper() in _FORBIDDEN_TENANTS:
        raise ProjectTaskError("PROJECT_TASK_TENANT_INVALID")
    if kind == "PROJECT" and not _PROJECT.fullmatch(value):
        raise ProjectTaskError("PROJECT_TASK_PROJECT_INVALID")
    if kind in {"TASK", "PARENT", "DEPENDENCY"} and not _TASK.fullmatch(value):
        raise ProjectTaskError("PROJECT_TASK_" + kind + "_INVALID")
    return value


def _timestamp(value: object) -> datetime:
    """Accept timezone-aware instants only; normalize immutable UTC snapshots."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ProjectTaskError("PROJECT_TASK_TIMESTAMP_INVALID")
    return value.astimezone(timezone.utc)


def _source_time(value: object) -> datetime:
    """Handle PyMongo UTC-naive BSON reads without admitting naive commands."""
    if not isinstance(value, datetime):
        raise ProjectTaskError("PROJECT_TASK_TIMESTAMP_INVALID")
    return _timestamp(value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value)


def _description(value: object, *, title: bool = False) -> str:
    """Accept bounded plain-text work labels without untrusted control characters."""
    if (
        not isinstance(value, str) or value != value.strip()
        or (title and not value) or len(value) > (180 if title else 5000)
        or any(ord(ch) < 32 and ch not in "\n\t" for ch in value)
        or (title and "\n" in value)
    ):
        raise ProjectTaskError("PROJECT_TASK_TITLE_INVALID" if title else "PROJECT_TASK_DESCRIPTION_INVALID")
    return value


def _due(value: object) -> str | None:
    """Accept ISO calendar dates without assuming a user's time zone."""
    if value is None:
        return None
    if not isinstance(value, str) or not _DATE.fullmatch(value):
        raise ProjectTaskError("PROJECT_TASK_DUE_DATE_INVALID")
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise ProjectTaskError("PROJECT_TASK_DUE_DATE_INVALID") from error
    return value


def _hash(value: dict[str, object]) -> str:
    """Compute deterministic SHA3-512 source-state integrity, not a signature."""
    try:
        serialized = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        )
    except (TypeError, ValueError) as error:
        raise ProjectTaskError("PROJECT_TASK_COMMAND_INVALID") from error
    return sha3_512(serialized.encode("utf-8")).hexdigest()


def task_id_for_command(
    tenant_id: str, project_id: str, actor_principal_id: str, key: str,
) -> str:
    """Derive one stable opaque task ID from exact command origin and replay key."""
    values = [
        _id(tenant_id, "TENANT"), _id(project_id, "PROJECT"),
        _id(actor_principal_id, "ACTOR"),
    ]
    if not isinstance(key, str) or not 1 <= len(key) <= 200 or key != key.strip():
        raise ProjectTaskError("PROJECT_TASK_IDEMPOTENCY_KEY_INVALID")
    return "ptk-" + sha3_512(("\0".join([*values, key])).encode("utf-8")).hexdigest()[:48]


@dataclass(frozen=True, slots=True)
class ProjectTask:
    """Immutable task, nested subtask or milestone owned by one exact project.

    Dependencies are immutable at creation to preclude retroactive cycles.
    A task transition to Done is additionally gated by the registry's current
    predecessor and child facts in the same transaction. Assigned principals
    are facts only; caller must validate current participant identity.
    """

    tenant_id: str
    project_id: str
    task_id: str
    kind: Literal["TASK", "MILESTONE"]
    parent_task_id: str | None
    title: str
    description: str
    status: Literal["TODO", "IN_PROGRESS", "BLOCKED", "DONE", "CANCELLED"]
    assignee_principal_id: str | None
    due_date: str | None
    depends_on: tuple[str, ...]
    created_by_principal_id: str
    updated_by_principal_id: str
    created_at: datetime
    updated_at: datetime
    revision: int = 1
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Revalidate the full state before persistence or hydration."""
        for value, name in (
            (self.tenant_id, "TENANT"),
            (self.project_id, "PROJECT"),
            (self.task_id, "TASK"),
            (self.created_by_principal_id, "CREATOR"),
            (self.updated_by_principal_id, "ACTOR"),
        ):
            _id(value, name)
        if self.kind not in _KINDS or self.status not in _STATES:
            raise ProjectTaskError("PROJECT_TASK_LIFECYCLE_INVALID")
        if self.parent_task_id is not None:
            _id(self.parent_task_id, "PARENT")
            if self.parent_task_id == self.task_id:
                raise ProjectTaskError("PROJECT_TASK_SELF_PARENT_INVALID")
        if self.kind == "MILESTONE" and self.parent_task_id is not None:
            raise ProjectTaskError("PROJECT_TASK_MILESTONE_PARENT_INVALID")
        _description(self.title, title=True)
        _description(self.description)
        if self.assignee_principal_id is not None:
            _id(self.assignee_principal_id, "ASSIGNEE")
        _due(self.due_date)
        if (
            not isinstance(self.depends_on, tuple) or len(self.depends_on) > 25
            or len(set(self.depends_on)) != len(self.depends_on)
        ):
            raise ProjectTaskError("PROJECT_TASK_DEPENDENCIES_INVALID")
        for dependency in self.depends_on:
            _id(dependency, "DEPENDENCY")
            if dependency == self.task_id:
                raise ProjectTaskError("PROJECT_TASK_SELF_DEPENDENCY_INVALID")
        if type(self.revision) is not int or self.revision < 1:
            raise ProjectTaskError("PROJECT_TASK_REVISION_INVALID")
        created, updated = _timestamp(self.created_at), _timestamp(self.updated_at)
        if updated < created:
            raise ProjectTaskError("PROJECT_TASK_TIME_ORDER_INVALID")
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "updated_at", updated)
        checksum = _hash(self._semantic())
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not _DIGEST.fullmatch(self.fingerprint)
            or not compare_digest(self.fingerprint, checksum)
        ):
            raise ProjectTaskError("PROJECT_TASK_FINGERPRINT_INVALID")
        object.__setattr__(self, "fingerprint", checksum)

    def _semantic(self) -> dict[str, object]:
        """Serialize defined immutable business fields in canonical form."""
        return {
            "schema": SCHEMA, "tenant_id": self.tenant_id,
            "project_id": self.project_id, "task_id": self.task_id,
            "kind": self.kind, "parent_task_id": self.parent_task_id,
            "title": self.title, "description": self.description,
            "status": self.status, "assignee_principal_id": self.assignee_principal_id,
            "due_date": self.due_date, "depends_on": list(self.depends_on),
            "created_by_principal_id": self.created_by_principal_id,
            "updated_by_principal_id": self.updated_by_principal_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(), "revision": self.revision,
        }

    def to_dict(self) -> dict[str, object]:
        """Return verified source state for transport and persisted snapshots."""
        return {**self._semantic(), "fingerprint": self.fingerprint}

    @classmethod
    def hydrate(cls, record: dict[str, object]) -> ProjectTask:
        """Reject corrupted/unknown fields before accepting a persisted task."""
        template = {
            "schema", "tenant_id", "project_id", "task_id", "kind", "parent_task_id",
            "title", "description", "status", "assignee_principal_id",
            "due_date", "depends_on", "created_by_principal_id",
            "updated_by_principal_id", "created_at", "updated_at",
            "revision", "fingerprint",
        }
        if not isinstance(record, dict) or set(record) != template or record["schema"] != SCHEMA:
            raise ProjectTaskError("PROJECT_TASK_RECORD_INVALID")
        data = {key: value for key, value in record.items() if key != "schema"}
        if not isinstance(data["depends_on"], (list, tuple)):
            raise ProjectTaskError("PROJECT_TASK_DEPENDENCIES_INVALID")
        data["depends_on"] = tuple(data["depends_on"])
        for key in ("created_at", "updated_at"):
            raw = data[key]
            try:
                data[key] = (
                    _source_time(raw) if isinstance(raw, datetime)
                    else _timestamp(datetime.fromisoformat(raw))
                    if isinstance(raw, str) else _source_time(raw)
                )
            except (ValueError, TypeError) as error:
                raise ProjectTaskError("PROJECT_TASK_TIMESTAMP_INVALID") from error
        try:
            return cls(**data)
        except TypeError as error:
            raise ProjectTaskError("PROJECT_TASK_RECORD_INVALID") from error

    def revise(
        self, *, title: str, description: str, due_date: str | None,
        assignee_principal_id: str | None, actor_principal_id: str,
        expected_revision: int, occurred_at: datetime,
    ) -> ProjectTask:
        """Revise only non-terminal task attributes with exact CAS and source time."""
        _id(actor_principal_id, "ACTOR")
        if type(expected_revision) is not int or expected_revision != self.revision:
            raise ProjectTaskConflict("PROJECT_TASK_REVISION_CONFLICT")
        if self.status in {"DONE", "CANCELLED"}:
            raise ProjectTaskConflict("PROJECT_TASK_TERMINAL_REVISION_DENIED")
        _description(title, title=True)
        _description(description)
        _due(due_date)
        if assignee_principal_id is not None:
            _id(assignee_principal_id, "ASSIGNEE")
        stamp = _timestamp(occurred_at)
        if stamp < self.updated_at:
            raise ProjectTaskError("PROJECT_TASK_TIME_ORDER_INVALID")
        return replace(
            self, title=title, description=description, due_date=due_date,
            assignee_principal_id=assignee_principal_id, revision=self.revision + 1,
            updated_by_principal_id=actor_principal_id, updated_at=stamp,
            fingerprint="",
        )


    def transition(
        self, *, status: str, actor_principal_id: str, expected_revision: int,
        occurred_at: datetime,
    ) -> ProjectTask:
        """Apply a strict task state command with immutable revision and CAS intent."""
        _id(actor_principal_id, "ACTOR")
        if type(expected_revision) is not int or expected_revision != self.revision:
            raise ProjectTaskConflict("PROJECT_TASK_REVISION_CONFLICT")
        if status not in _TRANSITIONS[self.status]:
            raise ProjectTaskConflict("PROJECT_TASK_TRANSITION_DENIED")
        stamp = _timestamp(occurred_at)
        if stamp < self.updated_at:
            raise ProjectTaskError("PROJECT_TASK_TIME_ORDER_INVALID")
        return replace(
            self, status=status, revision=self.revision + 1,
            updated_by_principal_id=actor_principal_id,
            updated_at=stamp, fingerprint="",
        )


class ProjectTaskRegistry:
    """Exact-tenant task persistence with immutable events and dependency gates."""

    def __init__(self, tasks: Any, events: Any) -> None:
        """Use supplied collections; neither create Mongo clients nor IAM."""
        if tasks is None or events is None:
            raise ProjectTaskError("PROJECT_TASK_COLLECTION_REQUIRED")
        self._tasks, self._events = tasks, events

    @staticmethod
    def ensure_indexes(tasks: Any, events: Any) -> None:
        """Create compound indexes before any authenticated Projects route runs."""
        try:
            tasks.create_index(
                [("tenant_id", ASCENDING), ("project_id", ASCENDING),
                 ("task_id", ASCENDING)],
                name="wilsy_project_task_identity_unique", unique=True,
            )
            tasks.create_index(
                [("tenant_id", ASCENDING), ("project_id", ASCENDING),
                 ("created_at", DESCENDING), ("task_id", ASCENDING)],
                name="wilsy_project_task_recent_list",
            )
            tasks.create_index(
                [("tenant_id", ASCENDING), ("project_id", ASCENDING),
                 ("parent_task_id", ASCENDING), ("status", ASCENDING)],
                name="wilsy_project_task_children",
            )
            tasks.create_index(
                [("tenant_id", ASCENDING), ("assignee_principal_id", ASCENDING),
                 ("status", ASCENDING), ("due_date", ASCENDING)],
                name="wilsy_project_task_assignee_attention",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
                name="wilsy_project_task_idempotency_unique", unique=True,
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("project_id", ASCENDING),
                 ("task_id", ASCENDING), ("revision", ASCENDING)],
                name="wilsy_project_task_event_revision_unique", unique=True,
            )
        except PyMongoError as error:
            raise ProjectTaskError("PROJECT_TASK_INDEX_UNAVAILABLE") from error

    def get(
        self, *, tenant_id: str, project_id: str, task_id: str, session: Any,
    ) -> ProjectTask:
        """Read one exact task, concealing unknown/foreign record existence."""
        if session is None:
            raise ProjectTaskError("PROJECT_TASK_SESSION_REQUIRED")
        query = {
            "tenant_id": _id(tenant_id, "TENANT"),
            "project_id": _id(project_id, "PROJECT"),
            "task_id": _id(task_id, "TASK"),
        }
        try:
            row = self._tasks.find_one(query, session=session)
        except PyMongoError as error:
            raise ProjectTaskError("PROJECT_TASK_READ_UNAVAILABLE") from error
        if row is None:
            raise ProjectTaskNotFound("PROJECT_TASK_NOT_FOUND")
        return ProjectTask.hydrate({k: v for k, v in row.items() if k != "_id"})

    def list_event_page(
        self, *, tenant_id: str, project_id: str, task_id: str,
        session: Any, limit: int = 50, offset: int = 0,
    ) -> tuple[tuple[dict[str, object], ...], bool]:
        """Expose only verified task lifecycle evidence, never replay secrets."""
        if session is None or type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or offset < 0:
            raise ProjectTaskError("PROJECT_TASK_EVENT_PAGE_INVALID")
        # Do not allow event existence to disclose a missing exact-task record.
        self.get(tenant_id=tenant_id, project_id=project_id,
                 task_id=task_id, session=session)
        query = {
            "tenant_id": _id(tenant_id, "TENANT"),
            "project_id": _id(project_id, "PROJECT"),
            "task_id": _id(task_id, "TASK"),
        }
        projection = {"_id": 0, "schema": 1, "tenant_id": 1,
                      "project_id": 1, "task_id": 1, "revision": 1,
                      "event_type": 1, "actor_principal_id": 1, "occurred_at": 1}
        try:
            rows = list(self._events.find(query, projection, session=session)
                        .sort([("revision", DESCENDING)]).skip(offset).limit(limit + 1))
        except PyMongoError as error:
            raise ProjectTaskError("PROJECT_TASK_EVENT_READ_UNAVAILABLE") from error
        result: list[dict[str, object]] = []
        for row in rows[:limit]:
            if (row.get("schema") != "wilsy.project.task.event.v1"
                or row.get("tenant_id") != tenant_id
                or row.get("project_id") != project_id
                or row.get("task_id") != task_id
                or type(row.get("revision")) is not int or row["revision"] < 1
                or row.get("event_type") not in {
                    "PROJECT_TASK_CREATED", "PROJECT_TASK_REVISED",
                    "PROJECT_TASK_TRANSITIONED",
                }
                or not isinstance(row.get("actor_principal_id"), str)
                or not row["actor_principal_id"]
                or not isinstance(row.get("occurred_at"), (datetime, str))):
                raise ProjectTaskError("PROJECT_TASK_EVENT_SOURCE_INVALID")
            timestamp = row["occurred_at"]
            if isinstance(timestamp, datetime):
                if timestamp.tzinfo is None:
                    raise ProjectTaskError("PROJECT_TASK_EVENT_SOURCE_INVALID")
                timestamp = timestamp.isoformat()
            else:
                try:
                    parsed = datetime.fromisoformat(timestamp)
                except ValueError as error:
                    raise ProjectTaskError("PROJECT_TASK_EVENT_SOURCE_INVALID") from error
                if parsed.tzinfo is None:
                    raise ProjectTaskError("PROJECT_TASK_EVENT_SOURCE_INVALID")
            result.append({
                "schema": row["schema"], "tenant_id": row["tenant_id"],
                "project_id": row["project_id"], "task_id": row["task_id"],
                "revision": row["revision"], "event_type": row["event_type"],
                "actor_principal_id": row["actor_principal_id"],
                "occurred_at": timestamp,
            })
        return tuple(result), len(rows) > limit

    def list_page(
        self, *, tenant_id: str, project_id: str, session: Any,
        limit: int = 50, offset: int = 0,
    ) -> tuple[tuple[ProjectTask, ...], bool]:
        """Read stable bounded task/milestone pages for an authorized project."""
        if session is None:
            raise ProjectTaskError("PROJECT_TASK_SESSION_REQUIRED")
        if type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or offset < 0:
            raise ProjectTaskError("PROJECT_TASK_PAGE_INVALID")
        query = {"tenant_id": _id(tenant_id, "TENANT"), "project_id": _id(project_id, "PROJECT")}
        try:
            rows = tuple(ProjectTask.hydrate({k: v for k, v in row.items() if k != "_id"})
                for row in self._tasks.find(query, session=session).sort(
                    [("created_at", DESCENDING), ("task_id", ASCENDING)],
                ).skip(offset).limit(limit + 1))
        except PyMongoError as error:
            raise ProjectTaskError("PROJECT_TASK_LIST_UNAVAILABLE") from error
        return rows[:limit], len(rows) > limit

    def _replay(
        self, *, tenant_id: str, key: str, request_digest: str, session: Any,
    ) -> ProjectTask | None:
        """Allow identical replay only after source-authored audit readback."""
        if session is None:
            raise ProjectTaskError("PROJECT_TASK_SESSION_REQUIRED")
        _id(tenant_id, "TENANT")
        if not isinstance(key, str) or not 1 <= len(key) <= 200 or key != key.strip():
            raise ProjectTaskError("PROJECT_TASK_IDEMPOTENCY_KEY_INVALID")
        try:
            event = self._events.find_one({
                "tenant_id": tenant_id, "idempotency_key": key,
            }, session=session)
        except PyMongoError as error:
            raise ProjectTaskError("PROJECT_TASK_REPLAY_UNAVAILABLE") from error
        if event is None:
            return None
        if event.get("request_digest") != request_digest:
            raise ProjectTaskConflict("PROJECT_TASK_DIVERGENT_REPLAY")
        snapshot = event.get("result_snapshot")
        if not isinstance(snapshot, dict):
            raise ProjectTaskError("PROJECT_TASK_EVENT_INVALID")
        task = ProjectTask.hydrate(snapshot)
        if (
            task.tenant_id != tenant_id or task.task_id != event.get("task_id")
            or task.project_id != event.get("project_id")
            or task.fingerprint != event.get("result_fingerprint")
            or task.revision != event.get("revision")
            or event.get("event_type") not in {"PROJECT_TASK_CREATED", "PROJECT_TASK_REVISED", "PROJECT_TASK_TRANSITIONED"}
        ):
            raise ProjectTaskError("PROJECT_TASK_EVENT_INVALID")
        return task

    def _event(
        self, *, task: ProjectTask, key: str, request_digest: str,
        event_type: str, session: Any,
    ) -> None:
        """Persist immutable audit inside the same source transaction."""
        try:
            self._events.insert_one({
                "schema": "wilsy.project.task.event.v1",
                "tenant_id": task.tenant_id, "project_id": task.project_id,
                "task_id": task.task_id, "revision": task.revision,
                "event_type": event_type,
                "actor_principal_id": task.updated_by_principal_id,
                "idempotency_key": key, "request_digest": request_digest,
                "result_fingerprint": task.fingerprint,
                "result_snapshot": task.to_dict(),
                "occurred_at": task.updated_at,
            }, session=session)
        except DuplicateKeyError as error:
            raise ProjectTaskConflict("PROJECT_TASK_EVENT_CONFLICT") from error
        except PyMongoError as error:
            raise ProjectTaskError("PROJECT_TASK_AUDIT_UNAVAILABLE") from error

    def create_or_replay(
        self, *, task: ProjectTask, idempotency_key: str, session: Any,
    ) -> ProjectTask:
        """Create a new task after validating exact-project parent and dependencies."""
        if task.revision != 1 or task.status != "TODO":
            raise ProjectTaskError("PROJECT_TASK_INITIAL_STATE_INVALID")
        if task.task_id != task_id_for_command(
            task.tenant_id, task.project_id,
            task.created_by_principal_id, idempotency_key,
        ):
            raise ProjectTaskError("PROJECT_TASK_IDENTITY_INVALID")
        digest = _hash({"command": "create", **task._semantic(),
                        "created_at": None, "updated_at": None})
        prior = self._replay(
            tenant_id=task.tenant_id, key=idempotency_key,
            request_digest=digest, session=session,
        )
        if prior is not None:
            return prior
        if task.parent_task_id is not None:
            parent = self.get(
                tenant_id=task.tenant_id, project_id=task.project_id,
                task_id=task.parent_task_id, session=session,
            )
            if parent.kind != "TASK" or parent.status in {"DONE", "CANCELLED"}:
                raise ProjectTaskConflict("PROJECT_TASK_PARENT_NOT_ELIGIBLE")
        for identity in task.depends_on:
            dependency = self.get(
                tenant_id=task.tenant_id, project_id=task.project_id,
                task_id=identity, session=session,
            )
            if dependency.status == "CANCELLED":
                raise ProjectTaskConflict("PROJECT_TASK_DEPENDENCY_CANCELLED")
        if session is None:
            raise ProjectTaskError("PROJECT_TASK_SESSION_REQUIRED")
        try:
            self._tasks.insert_one(task.to_dict(), session=session)
        except DuplicateKeyError as error:
            raise ProjectTaskConflict("PROJECT_TASK_ALREADY_EXISTS") from error
        except PyMongoError as error:
            raise ProjectTaskError("PROJECT_TASK_WRITE_UNAVAILABLE") from error
        self._event(
            task=task, key=idempotency_key, request_digest=digest,
            event_type="PROJECT_TASK_CREATED", session=session,
        )
        return task

    def revise_or_replay(
        self, *, tenant_id: str, project_id: str, task_id: str,
        actor_principal_id: str, title: str, description: str,
        due_date: str | None, assignee_principal_id: str | None,
        expected_revision: int, idempotency_key: str,
        occurred_at: datetime, session: Any,
    ) -> ProjectTask:
        """Persist authorized task edits under exact CAS, immutable audit and replay.

        The caller must independently verify a new assignee's ACTIVE exact-project
        CONTRIBUTOR participation and current principal/membership/role.
        """
        actor = _id(actor_principal_id, "ACTOR")
        digest = _hash({
            "command": "revise", "tenant_id": tenant_id,
            "project_id": project_id, "task_id": task_id, "actor": actor,
            "title": title, "description": description, "due_date": due_date,
            "assignee_principal_id": assignee_principal_id,
            "expected_revision": expected_revision,
        })
        prior = self._replay(
            tenant_id=tenant_id, key=idempotency_key,
            request_digest=digest, session=session,
        )
        if prior is not None:
            return prior
        source = self.get(
            tenant_id=tenant_id, project_id=project_id,
            task_id=task_id, session=session,
        )
        revised = source.revise(
            title=title, description=description, due_date=due_date,
            assignee_principal_id=assignee_principal_id,
            actor_principal_id=actor, expected_revision=expected_revision,
            occurred_at=occurred_at,
        )
        try:
            result = self._tasks.update_one({
                "tenant_id": _id(tenant_id, "TENANT"),
                "project_id": _id(project_id, "PROJECT"),
                "task_id": _id(task_id, "TASK"),
                "revision": source.revision, "fingerprint": source.fingerprint,
            }, {"$set": revised.to_dict()}, session=session)
        except PyMongoError as error:
            raise ProjectTaskError("PROJECT_TASK_WRITE_UNAVAILABLE") from error
        if result.matched_count != 1:
            raise ProjectTaskConflict("PROJECT_TASK_REVISION_CONFLICT")
        self._event(
            task=revised, key=idempotency_key, request_digest=digest,
            event_type="PROJECT_TASK_REVISED", session=session,
        )
        return revised


    def transition_or_replay(
        self, *, tenant_id: str, project_id: str, task_id: str,
        actor_principal_id: str, status: str, expected_revision: int,
        idempotency_key: str, occurred_at: datetime, session: Any,
    ) -> ProjectTask:
        """Perform CAS lifecycle transition, blocking completion on live dependencies."""
        actor = _id(actor_principal_id, "ACTOR")
        digest = _hash({
            "command": "transition", "tenant_id": tenant_id,
            "project_id": project_id, "task_id": task_id, "actor": actor,
            "status": status, "expected_revision": expected_revision,
        })
        replay = self._replay(
            tenant_id=tenant_id, key=idempotency_key,
            request_digest=digest, session=session,
        )
        if replay is not None:
            return replay
        source = self.get(
            tenant_id=tenant_id, project_id=project_id,
            task_id=task_id, session=session,
        )
        revised = source.transition(
            status=status, actor_principal_id=actor,
            expected_revision=expected_revision, occurred_at=occurred_at,
        )
        if status == "DONE":
            for identity in source.depends_on:
                preceding = self.get(
                    tenant_id=tenant_id, project_id=project_id,
                    task_id=identity, session=session,
                )
                if preceding.status != "DONE":
                    raise ProjectTaskConflict("PROJECT_TASK_DEPENDENCY_BLOCKED")
            try:
                child = self._tasks.find_one({
                    "tenant_id": _id(tenant_id, "TENANT"),
                    "project_id": _id(project_id, "PROJECT"),
                    "parent_task_id": _id(task_id, "TASK"),
                    "status": {"$nin": ["DONE", "CANCELLED"]},
                }, session=session)
            except PyMongoError as error:
                raise ProjectTaskError("PROJECT_TASK_CHILD_READ_UNAVAILABLE") from error
            if child is not None:
                raise ProjectTaskConflict("PROJECT_TASK_CHILDREN_INCOMPLETE")
        try:
            result = self._tasks.update_one({
                "tenant_id": _id(tenant_id, "TENANT"),
                "project_id": _id(project_id, "PROJECT"),
                "task_id": _id(task_id, "TASK"),
                "revision": source.revision,
                "fingerprint": source.fingerprint,
            }, {"$set": revised.to_dict()}, session=session)
        except PyMongoError as error:
            raise ProjectTaskError("PROJECT_TASK_WRITE_UNAVAILABLE") from error
        if result.matched_count != 1:
            raise ProjectTaskConflict("PROJECT_TASK_REVISION_CONFLICT")
        self._event(
            task=revised, key=idempotency_key, request_digest=digest,
            event_type="PROJECT_TASK_TRANSITIONED", session=session,
        )
        return revised


__all__ = [
    "VERSION", "SCHEMA", "COLLECTION", "EVENT_COLLECTION",
    "ProjectTask", "ProjectTaskRegistry", "ProjectTaskError",
    "ProjectTaskConflict", "ProjectTaskNotFound", "task_id_for_command",
]

# ARTIFACT: project_task_registry.py
# VERSION: v1.2.0-TASK-ACTIVITY-EVENT-READ
# AUTHORITY BOUNDARY: source lifecycle/CAS only; router owns independent IAM
# TENANT POSTURE: exact tenant/project/assignee; no privileged fallback
# FAIL-CLOSED POSTURE: invalid graph, dependency, replay or revision denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
