"""TITLE: WILSY OS Tenant Project Registry
VERSION: v1.4.0-CANONICAL-DATE-ONLY-COMMAND-FINGERPRINT
AUTHORITY: Python EOS durable persistence for canonical tenant Projects.
EPITOME: Persists tenant-scoped Project aggregates and immutable command events
         inside caller-owned Mongo transactions; it contains no authorization
         decisions and never creates a Mongo client or transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/projects/project_registry.py
COLLABORATION / OWNERSHIP: Consumes saas.domain.project; projects_router owns
                           authorization, session and HTTP composition.
CERTIFICATION / UPDATE DATE: 2026-11-17.
CHANGELOG:
  v1.4.0-CANONICAL-DATE-ONLY-COMMAND-FINGERPRINT fingerprints typed date-only project command fields as exact ISO dates, ensuring strict HTTP validation, immutable command replay and project-domain date types agree without a relaxed serializer.
  v1.4.0-CANONICAL-DATE-ONLY-COMMAND-FINGERPRINT — Adds bounded look-ahead paging with verified has-more
  metadata while preserving the existing page-only registry API.
  v1.4.0-CANONICAL-DATE-ONLY-COMMAND-FINGERPRINT — Adds a compound tenant/archive/status/sort index for
  bounded project-list status filtering at enterprise project volumes.
  This is index DDL only: no tenant, role, grant or record is changed.
  v1.4.0-CANONICAL-DATE-ONLY-COMMAND-FINGERPRINT — Streams validated exact-tenant
  project summaries without the former 500-record ceiling, returns bounded
  list pages without rejecting a valid next page, and adds a tenant-oriented
  active-recent listing index. No IAM or project data changes.
  v1.0.3-BSON-UTC-EVENT-READBACK — Normalizes BSON UTC datetimes on
  event readback when PyMongo returns naive values by default, without
  weakening strict input or malformed-event validation.
  v1.0.2-TENANT-PROJECT-REGISTRY — Narrows validated status values before enum
  access to satisfy Pyright's strict union checking.
  v1.0.1-TENANT-PROJECT-REGISTRY — Replaces runtime-derived hydration shape
  with a fixed persistence field contract and tightens status input typing.
  v1.0.0-TENANT-PROJECT-REGISTRY — Adds tenant-scoped CRUD lifecycle,
  idempotent replay, immutable command events, summary and deterministic indexes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Every query includes tenant_id; event evidence is
                            append-only through this API. Errors use stable
                            codes and do not contain record content.
TENANT BOUNDARY: Caller supplies the canonical tenant already established by
                 EOS; the registry rejects malformed scope and never uses
                 MASTER, WILSY_ROOT, or another fallback.
AUTHORITY BOUNDARY: Persistence only. Callers must independently revalidate
                    principal, membership, business capacity and operation IAM.
FINANCIAL AUTHORITY BOUNDARY: Project persistence cannot authorize spending,
                              payment, execution, approval or settlement.

All write methods require a non-null caller-owned Mongo session and must be
executed inside the caller's transaction. Index creation is explicit metadata
DDL and is not hidden inside reads or constructors. Event snapshots preserve
project command evidence; this registry exposes no update or delete operation
for those events.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timezone
import hashlib
import json
from typing import Any, Final, cast

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.project import Project, ProjectError, ProjectStatus


VERSION: Final[str] = "v1.4.0-CANONICAL-DATE-ONLY-COMMAND-FINGERPRINT"
COLLECTION: Final[str] = "wilsy_projects"
EVENT_COLLECTION: Final[str] = "wilsy_project_events"
IDENTITY_INDEX: Final[str] = "wilsy_project_tenant_identity_unique"
CODE_INDEX: Final[str] = "wilsy_project_tenant_code_unique"
EVENT_ID_INDEX: Final[str] = "wilsy_project_event_tenant_identity_unique"
EVENT_REPLAY_INDEX: Final[str] = "wilsy_project_event_tenant_idempotency_unique"
EVENT_REVISION_INDEX: Final[str] = "wilsy_project_event_tenant_project_revision_unique"
_PROJECT_FIELDS: Final[tuple[str, ...]] = (
    "project_id", "tenant_id", "name", "code", "summary", "status",
    "owner_principal_id", "department_id", "start_date", "target_date",
    "source_type", "external_source_reference", "created_by_principal_id",
    "created_at", "updated_by_principal_id", "updated_at", "archived_at",
    "revision", "schema", "version", "fingerprint",
)
_EVENT_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id", "event_id", "project_id", "event_type", "actor_principal_id",
    "revision", "prior_fingerprint", "result_fingerprint", "request_fingerprint",
    "idempotency_key", "occurred_at", "result_snapshot", "schema",
)


class ProjectRegistryError(RuntimeError):
    """Stable project persistence or evidence failure safe for API mapping."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ProjectRegistryConflict(ProjectRegistryError):
    """A project identity, revision, code, or idempotency replay conflicts."""


class ProjectNotFound(ProjectRegistryError):
    """No project exists for the exact tenant and requested project identity."""


def _exact(name: str, value: object, *, maximum: int = 180) -> str:
    """Validate opaque tenant, project, actor and idempotency coordinates."""
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > maximum:
        raise ProjectRegistryError(f"PROJECT_{name.upper()}_INVALID")
    return value


def _session(value: object) -> object:
    """Require the caller's transaction session without opening another one."""
    if value is None:
        raise ProjectRegistryError("PROJECT_TRANSACTION_SESSION_REQUIRED")
    return value


def _occurred_at(value: object) -> datetime:
    """Require an aware command timestamp supplied by the authorized caller."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ProjectRegistryError("PROJECT_COMMAND_TIMESTAMP_INVALID")
    return value


def _date_only_command_value(value: object) -> str:
    """Serialize only an exact date type, not timestamps or arbitrary objects."""
    if type(value) is not date:
        raise TypeError("Unsupported project command value")
    return value.isoformat()


def _canonical_fingerprint(payload: Mapping[str, object]) -> str:
    """Fingerprint deterministic command semantics, including ISO dates, with SHA3-512."""
    try:
        raw = json.dumps(dict(payload), sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, default=_date_only_command_value).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ProjectRegistryError("PROJECT_COMMAND_FINGERPRINT_INVALID") from error
    return hashlib.sha3_512(raw).hexdigest()


def _hydrate(row: Mapping[str, object]) -> Project:
    """Hydrate the exact aggregate fields without deriving schema from sample data."""
    try:
        return Project.from_dict({key: row[key] for key in _PROJECT_FIELDS})
    except (KeyError, TypeError, ValueError, ProjectError) as error:
        raise ProjectRegistryError("PROJECT_PERSISTED_DOCUMENT_INVALID") from error


def _document(value: Project) -> dict[str, object]:
    """Return canonical persisted project semantics without Mongo's internal id."""
    if not isinstance(value, Project):
        raise ProjectRegistryError("PROJECT_AGGREGATE_REQUIRED")
    return value.to_dict()


class ProjectRegistry:
    """Caller-transaction-owned persistence for tenant project aggregates.

    This class never creates indexes implicitly, starts transactions, determines
    tenant identity, validates owner/department eligibility, or authorizes an
    operation. Router callers must perform those checks before invoking it.
    """

    __slots__ = ("_projects", "_events")

    def __init__(self, projects: Any, events: Any) -> None:
        """Bind the canonical project and immutable event collections."""
        if projects is None or events is None:
            raise ProjectRegistryError("PROJECT_COLLECTION_REQUIRED")
        self._projects = projects
        self._events = events

    @staticmethod
    def ensure_indexes(projects: Any, events: Any) -> None:
        """Create deterministic tenant-scoped indexes without replacing indexes."""
        if projects is None or events is None:
            raise ProjectRegistryError("PROJECT_COLLECTION_REQUIRED")
        try:
            projects.create_index([("tenant_id", ASCENDING), ("project_id", ASCENDING)],
                                  unique=True, name=IDENTITY_INDEX)
            projects.create_index([("tenant_id", ASCENDING), ("code", ASCENDING)],
                                  unique=True, name=CODE_INDEX,
                                  partialFilterExpression={"code": {"$type": "string"}})
            projects.create_index([("tenant_id", ASCENDING), ("archived_at", ASCENDING),
                                   ("updated_at", DESCENDING), ("project_id", ASCENDING)],
                                  name="wilsy_project_tenant_active_recent")
            projects.create_index([("tenant_id", ASCENDING), ("archived_at", ASCENDING),
                                   ("status", ASCENDING), ("updated_at", DESCENDING),
                                   ("project_id", ASCENDING)],
                                  name="wilsy_project_tenant_status_recent")
            events.create_index([("tenant_id", ASCENDING), ("event_id", ASCENDING)],
                                unique=True, name=EVENT_ID_INDEX)
            events.create_index([("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
                                unique=True, name=EVENT_REPLAY_INDEX)
            events.create_index([("tenant_id", ASCENDING), ("project_id", ASCENDING),
                                 ("revision", ASCENDING)], unique=True, name=EVENT_REVISION_INDEX)
        except PyMongoError as error:
            raise ProjectRegistryError("PROJECT_INDEX_UNAVAILABLE") from error

    def get(self, *, tenant_id: str, project_id: str, session: Any,
            include_archived: bool = False) -> Project:
        """Read one exact-tenant project; foreign identifiers look absent."""
        tenant = _exact("tenant_id", tenant_id)
        identity = _exact("project_id", project_id)
        query: dict[str, object] = {"tenant_id": tenant, "project_id": identity}
        if include_archived is not True:
            query["archived_at"] = None
        try:
            row = self._projects.find_one(query, session=_session(session))
        except PyMongoError as error:
            raise ProjectRegistryError("PROJECT_READ_UNAVAILABLE") from error
        if row is None:
            raise ProjectNotFound("PROJECT_NOT_FOUND")
        return _hydrate(row)

    def list_for_tenant(self, *, tenant_id: str, session: Any, limit: int = 200,
                        offset: int = 0, status: ProjectStatus | str | None = None,
                        include_archived: bool = False) -> tuple[Project, ...]:
        """Return a backwards-compatible bounded tenant page of project records."""
        page, _has_more = self.list_page_for_tenant(
            tenant_id=tenant_id, session=session, limit=limit, offset=offset,
            status=status, include_archived=include_archived,
        )
        return page

    def list_page_for_tenant(self, *, tenant_id: str, session: Any, limit: int = 200,
                             offset: int = 0, status: ProjectStatus | str | None = None,
                             include_archived: bool = False) -> tuple[tuple[Project, ...], bool]:
        """Return exact-tenant page and verified next-page existence in one snapshot."""
        tenant = _exact("tenant_id", tenant_id)
        if type(limit) is not int or not 1 <= limit <= 500 or type(offset) is not int or offset < 0:
            raise ProjectRegistryError("PROJECT_PAGE_INVALID")
        query: dict[str, object] = {"tenant_id": tenant}
        if include_archived is not True:
            query["archived_at"] = None
        if status is not None:
            try:
                normalized_status = ProjectStatus(status)
                query["status"] = cast(ProjectStatus, normalized_status).value
            except (TypeError, ValueError) as error:
                raise ProjectRegistryError("PROJECT_STATUS_FILTER_INVALID") from error
        try:
            rows = list(self._projects.find(query, session=_session(session))
                        .sort([("updated_at", DESCENDING), ("project_id", ASCENDING)])
                        .skip(offset).limit(limit + 1))
        except PyMongoError as error:
            raise ProjectRegistryError("PROJECT_LIST_UNAVAILABLE") from error
        validated = tuple(_hydrate(row) for row in rows)
        return validated[:limit], len(validated) > limit

    def summary_for_tenant(self, *, tenant_id: str, session: Any) -> dict[str, int]:
        """Derive status counts from fully validated, exact-tenant active records."""
        tenant = _exact("tenant_id", tenant_id)
        counts = {item.value: 0 for item in ProjectStatus}
        total = 0
        try:
            # Stream validated tenant records rather than truncating at 500;
            # no unverified count or foreign-tenant data enters the projection.
            cursor = self._projects.find(
                {"tenant_id": tenant, "archived_at": None},
                session=_session(session),
            )
            for row in cursor:
                value = _hydrate(row)
                counts[cast(ProjectStatus, value.status).value] += 1
                total += 1
        except PyMongoError as error:
            raise ProjectRegistryError("PROJECT_SUMMARY_UNAVAILABLE") from error
        return {
            "total": total, "active": counts[ProjectStatus.ACTIVE.value],
            "planned": counts[ProjectStatus.PLANNED.value],
            "on_hold": counts[ProjectStatus.ON_HOLD.value],
            "done": counts[ProjectStatus.DONE.value],
            "cancelled": counts[ProjectStatus.CANCELLED.value],
        }

    def create_or_replay(self, *, project: Project, actor_principal_id: str,
                         idempotency_key: str, occurred_at: datetime,
                         session: Any) -> Project:
        """Insert one project and immutable creation event or replay exact command."""
        if not isinstance(project, Project):
            raise ProjectRegistryError("PROJECT_AGGREGATE_REQUIRED")
        tenant = _exact("tenant_id", project.tenant_id)
        actor = _exact("actor_principal_id", actor_principal_id)
        key = _exact("idempotency_key", idempotency_key, maximum=200)
        tx = _session(session)
        occurred = _occurred_at(occurred_at)
        if project.created_by_principal_id != actor or project.updated_by_principal_id != actor:
            raise ProjectRegistryConflict("PROJECT_CREATOR_ACTOR_MISMATCH")
        request_fingerprint = _canonical_fingerprint({
            "action": "CREATE", "tenant_id": tenant, "actor_principal_id": actor,
            "idempotency_key": key, "project": project.to_dict(),
        })
        try:
            replay = self._events.find_one({"tenant_id": tenant, "idempotency_key": key}, session=tx)
            if replay is not None:
                if replay.get("request_fingerprint") != request_fingerprint:
                    raise ProjectRegistryConflict("PROJECT_DIVERGENT_REPLAY")
                return _hydrate(replay["result_snapshot"])
            self._projects.insert_one(_document(project), session=tx)
            self._insert_event(project=project, actor=actor, action="CREATED", key=key,
                               request_fingerprint=request_fingerprint, prior=None,
                               occurred_at=occurred, session=tx)
            return project
        except ProjectRegistryConflict:
            raise
        except DuplicateKeyError as error:
            raise ProjectRegistryConflict("PROJECT_IDENTITY_OR_CODE_CONFLICT") from error
        except PyMongoError as error:
            raise ProjectRegistryError("PROJECT_CREATE_UNAVAILABLE") from error

    def update(self, *, tenant_id: str, project_id: str, actor_principal_id: str,
               expected_revision: int, changes: Mapping[str, object],
               idempotency_key: str, occurred_at: datetime, session: Any) -> Project:
        """Update bounded project facts with tenant, revision and replay guards."""
        return self._updated_value(
            tenant_id=tenant_id, project_id=project_id, actor_principal_id=actor_principal_id,
            expected_revision=expected_revision, changes=changes, occurred_at=occurred_at,
            action="UPDATED", idempotency_key=idempotency_key, session=session)

    def transition(self, *, tenant_id: str, project_id: str, actor_principal_id: str,
                   expected_revision: int, resulting_status: ProjectStatus | str,
                   idempotency_key: str, occurred_at: datetime, session: Any) -> Project:
        """Apply one permitted status transition with immutable command evidence."""
        try:
            status_value = ProjectStatus(resulting_status).value
        except (TypeError, ValueError) as error:
            raise ProjectRegistryError("PROJECT_STATUS_INVALID") from error
        return self._updated_value(
            tenant_id=tenant_id, project_id=project_id, actor_principal_id=actor_principal_id,
            expected_revision=expected_revision, changes={"status": status_value},
            occurred_at=occurred_at, action="STATUS_TRANSITION",
            idempotency_key=idempotency_key, session=session)

    def archive(self, *, tenant_id: str, project_id: str, actor_principal_id: str,
                expected_revision: int, idempotency_key: str, occurred_at: datetime,
                session: Any) -> Project:
        """Soft archive a project without deleting its aggregate or command evidence."""
        tenant = _exact("tenant_id", tenant_id)
        identity = _exact("project_id", project_id)
        actor = _exact("actor_principal_id", actor_principal_id)
        key = _exact("idempotency_key", idempotency_key, maximum=200)
        tx = _session(session)
        occurred = _occurred_at(occurred_at)
        fingerprint = _canonical_fingerprint({
            "action": "ARCHIVE", "tenant_id": tenant, "project_id": identity,
            "actor_principal_id": actor, "expected_revision": expected_revision,
            "idempotency_key": key})
        replay = self._find_replay(tenant, key, fingerprint, tx)
        if replay is not None:
            return replay
        current = self.get(tenant_id=tenant, project_id=identity, session=tx)
        try:
            updated = current.archive(actor_principal_id=actor, archived_at=occurred,
                                      expected_revision=expected_revision)
        except ProjectError as error:
            raise ProjectRegistryConflict(error.code) from error
        return self._persist_revision(current, updated, actor, "ARCHIVED", key, fingerprint, occurred, tx)

    def list_events(self, *, tenant_id: str, project_id: str, session: Any,
                    limit: int = 200) -> tuple[dict[str, object], ...]:
        """Read immutable audit events for one exact-tenant project without mutation."""
        tenant = _exact("tenant_id", tenant_id)
        identity = _exact("project_id", project_id)
        if type(limit) is not int or not 1 <= limit <= 500:
            raise ProjectRegistryError("PROJECT_EVENT_LIMIT_INVALID")
        try:
            rows = list(self._events.find({"tenant_id": tenant, "project_id": identity},
                                          session=_session(session))
                        .sort("revision", ASCENDING).limit(limit + 1))
        except PyMongoError as error:
            raise ProjectRegistryError("PROJECT_EVENT_READ_UNAVAILABLE") from error
        if len(rows) > limit:
            raise ProjectRegistryError("PROJECT_EVENT_BOUND_EXCEEDED")
        return tuple(self._public_event(row) for row in rows)

    def _updated_value(self, *, tenant_id: str, project_id: str,
                       actor_principal_id: str, expected_revision: int,
                       changes: Mapping[str, object], occurred_at: datetime,
                       action: str, idempotency_key: str, session: Any) -> Project:
        tenant = _exact("tenant_id", tenant_id)
        identity = _exact("project_id", project_id)
        actor = _exact("actor_principal_id", actor_principal_id)
        key = _exact("idempotency_key", idempotency_key, maximum=200)
        tx = _session(session)
        occurred = _occurred_at(occurred_at)
        command_fields = dict(changes)
        fingerprint = _canonical_fingerprint({
            "action": action, "tenant_id": tenant, "project_id": identity,
            "actor_principal_id": actor, "expected_revision": expected_revision,
            "idempotency_key": key, "changes": command_fields})
        replay = self._find_replay(tenant, key, fingerprint, tx)
        if replay is not None:
            return replay
        current = self.get(tenant_id=tenant, project_id=identity, session=tx)
        try:
            if "status" in command_fields:
                updated = current.transition(
                    actor_principal_id=actor, updated_at=occurred,
                    expected_revision=expected_revision,
                    resulting_status=cast(ProjectStatus | str, command_fields["status"]))
            else:
                updated = current.update(
                    actor_principal_id=actor, updated_at=occurred,
                    expected_revision=expected_revision, changes=command_fields)
        except ProjectError as error:
            raise ProjectRegistryConflict(error.code) from error
        return self._persist_revision(current, updated, actor, action, key, fingerprint, occurred, tx)

    def _find_replay(self, tenant: str, key: str, fingerprint: str,
                     session: object) -> Project | None:
        try:
            row = self._events.find_one({"tenant_id": tenant, "idempotency_key": key}, session=session)
        except PyMongoError as error:
            raise ProjectRegistryError("PROJECT_REPLAY_READ_UNAVAILABLE") from error
        if row is None:
            return None
        if row.get("request_fingerprint") != fingerprint:
            raise ProjectRegistryConflict("PROJECT_DIVERGENT_REPLAY")
        snapshot = row.get("result_snapshot")
        if not isinstance(snapshot, Mapping):
            raise ProjectRegistryError("PROJECT_EVENT_SNAPSHOT_INVALID")
        return _hydrate(snapshot)

    def _persist_revision(self, prior: Project, updated: Project, actor: str,
                          action: str, key: str, request_fingerprint: str,
                          occurred: datetime, session: object) -> Project:
        try:
            result = self._projects.update_one(
                {"tenant_id": prior.tenant_id, "project_id": prior.project_id,
                 "revision": prior.revision, "fingerprint": prior.fingerprint, "archived_at": None},
                {"$set": _document(updated)}, session=session)
            if getattr(result, "matched_count", 0) != 1:
                raise ProjectRegistryConflict("PROJECT_REVISION_CONFLICT")
            self._insert_event(project=updated, actor=actor, action=action, key=key,
                               request_fingerprint=request_fingerprint, prior=prior,
                               occurred_at=occurred, session=session)
            return updated
        except ProjectRegistryConflict:
            raise
        except DuplicateKeyError as error:
            raise ProjectRegistryConflict("PROJECT_IDEMPOTENCY_OR_REVISION_CONFLICT") from error
        except PyMongoError as error:
            raise ProjectRegistryError("PROJECT_UPDATE_UNAVAILABLE") from error

    def _insert_event(self, *, project: Project, actor: str, action: str,
                      key: str, request_fingerprint: str, prior: Project | None,
                      occurred_at: datetime, session: object) -> None:
        event = {
            "tenant_id": project.tenant_id, "event_id": f"project:{request_fingerprint}",
            "project_id": project.project_id, "event_type": f"PROJECT_{action}",
            "actor_principal_id": actor, "revision": project.revision,
            "prior_fingerprint": prior.fingerprint if prior is not None else None,
            "result_fingerprint": project.fingerprint,
            "request_fingerprint": request_fingerprint, "idempotency_key": key,
            "occurred_at": occurred_at, "result_snapshot": project.to_dict(),
            "schema": "wilsy.project.event.v1"}
        try:
            self._events.insert_one(event, session=session)
        except DuplicateKeyError as error:
            raise ProjectRegistryConflict("PROJECT_EVENT_IDENTITY_CONFLICT") from error
        except PyMongoError as error:
            raise ProjectRegistryError("PROJECT_EVENT_PERSISTENCE_UNAVAILABLE") from error

    @staticmethod
    def _public_event(row: Mapping[str, object]) -> dict[str, object]:
        """Project documented audit fields and reject incomplete evidence."""
        if not all(key in row for key in _EVENT_FIELDS):
            raise ProjectRegistryError("PROJECT_EVENT_RECORD_INVALID")
        snapshot = row.get("result_snapshot")
        if not isinstance(snapshot, Mapping):
            raise ProjectRegistryError("PROJECT_EVENT_SNAPSHOT_INVALID")
        _hydrate(snapshot)
        occurred = row.get("occurred_at")
        if not isinstance(occurred, datetime):
            raise ProjectRegistryError("PROJECT_EVENT_TIMESTAMP_INVALID")
        # BSON datetime always represents UTC. PyMongo with tz_aware=False
        # decodes persisted UTC instants as naive datetime values. Normalize
        # ONLY the trusted database read; command input remains strictly aware.
        if occurred.tzinfo is None:
            occurred = occurred.replace(tzinfo=timezone.utc)
        if occurred.utcoffset() is None:
            raise ProjectRegistryError("PROJECT_EVENT_TIMESTAMP_INVALID")
        event = {key: row[key] for key in _EVENT_FIELDS}
        event["occurred_at"] = occurred.astimezone(timezone.utc)
        return event


__all__ = ["VERSION", "COLLECTION", "EVENT_COLLECTION", "ProjectRegistry",
           "ProjectRegistryError", "ProjectRegistryConflict", "ProjectNotFound"]

# ARTIFACT: project_registry.py
# VERSION: v1.4.0-CANONICAL-DATE-ONLY-COMMAND-FINGERPRINT
# AUTHORITY BOUNDARY: tenant-scoped persistence only; EOS authorization is a caller obligation
# TENANT POSTURE: every query and event is scoped by the explicit canonical tenant
# FAIL-CLOSED POSTURE: missing sessions, malformed records, divergent replay, and revision races reject
# FINANCIAL EXECUTION AUTHORITY: no financial execution; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
