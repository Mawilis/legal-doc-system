"""TITLE: WILSY OS Project Note Transaction Registry
VERSION: v1.0.0-AUDITED-EXACT-TENANT-PROJECT-NOTES
AUTHORITY: Python EOS caller-owned MongoDB transaction persistence.
EPITOME: Source-owned note CRUD, immutable note events, bounded list pages,
         deterministic idempotency and author/revision CAS without IAM grants.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/projects/project_note_registry.py
COLLABORATION / OWNERSHIP: ProjectNote domain; Projects router owns current
         project existence, permission/entitlement admission and Mongo session.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-AUDITED-EXACT-TENANT-PROJECT-NOTES adds exact-tenant source
         records and durable event audit without mixing note state into Project.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Whitelisted source fields, no leaked foreign notes,
         stable codes, bounded text/page size and non-executing audit events.
TENANT BOUNDARY: Every persistence query binds tenant_id and project_id;
         no internal/founder/global tenant aliases or cross-tenant fallbacks.
AUTHORITY BOUNDARY: Registry enforces author and optimistic revision only;
         EOS router independently authorizes every read and mutation.
TRANSACTION BOUNDARY: Caller must pass a live session; no registry-created
         Mongo client, transaction, entitlement or permission.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS exclusively.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from hashlib import sha3_512
import json
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.project_note import (
    ProjectNote, ProjectNoteError,
)

VERSION: Final[str] = "v1.0.0-AUDITED-EXACT-TENANT-PROJECT-NOTES"
COLLECTION: Final[str] = "wilsy_project_notes"
EVENT_COLLECTION: Final[str] = "wilsy_project_note_events"
_NOTE_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id", "project_id", "note_id", "author_principal_id",
    "body", "created_at", "updated_at", "revision", "archived_at",
    "schema", "version", "fingerprint",
)
_EVENT_TYPES: Final[frozenset[str]] = frozenset({
    "PROJECT_NOTE_CREATED", "PROJECT_NOTE_REVISED", "PROJECT_NOTE_ARCHIVED",
})


class ProjectNoteRegistryError(RuntimeError):
    """Stable note registry or audit failure without record content."""

    def __init__(self, code: str) -> None:
        """Expose only one bounded error code."""
        self.code = code
        super().__init__(code)


class ProjectNoteConflict(ProjectNoteRegistryError):
    """Idempotency, author, revision or unique identity conflict."""


class ProjectNoteNotFound(ProjectNoteRegistryError):
    """Exact-tenant project note is absent or hidden."""


def _exact(value: object, name: str, maximum: int = 180) -> str:
    """Reject missing, untrimmed or unbounded persistence coordinates."""
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > maximum:
        raise ProjectNoteRegistryError("PROJECT_NOTE_" + name.upper() + "_INVALID")
    return value


def _session(value: object) -> Any:
    """Require caller-provided transaction authority."""
    if value is None:
        raise ProjectNoteRegistryError("PROJECT_NOTE_SESSION_REQUIRED")
    return value


def _hydrate(value: Mapping[str, object]) -> ProjectNote:
    """Hydrate only the canonical note fields and verify SHA3-512 semantics."""
    try:
        return ProjectNote.from_dict({key: value[key] for key in _NOTE_FIELDS})
    except (KeyError, ValueError, TypeError, ProjectNoteError) as error:
        raise ProjectNoteRegistryError("PROJECT_NOTE_RECORD_INVALID") from error


def _fingerprint(payload: Mapping[str, object]) -> str:
    """Build the exact semantic command fingerprint for durable replay."""
    try:
        value = json.dumps(
            dict(payload), ensure_ascii=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ProjectNoteRegistryError("PROJECT_NOTE_COMMAND_INVALID") from error
    return sha3_512(value).hexdigest()


def note_id_for_command(
    tenant_id: str, project_id: str, actor_principal_id: str,
    idempotency_key: str,
) -> str:
    """Derive stable note identity from exact tenant, project, actor and key."""
    coords = [
        _exact(tenant_id, "tenant_id"), _exact(project_id, "project_id"),
        _exact(actor_principal_id, "actor_principal_id"),
        _exact(idempotency_key, "idempotency_key", 200),
    ]
    return "pnt-" + sha3_512("\0".join(coords).encode("utf-8")).hexdigest()[:48]


class ProjectNoteRegistry:
    """Exact-project note persistence, CAS revisions and append-only events.

    The router must verify current Project visibility and independently current
    tenant IAM/entitlement before accessing this registry. A note is never
    authoritative project lifecycle, approval, workflow or financial evidence.
    """

    __slots__ = ("_notes", "_events")

    def __init__(self, notes: Any, events: Any) -> None:
        """Accept explicit database collections without opening resources."""
        if notes is None or events is None:
            raise ProjectNoteRegistryError("PROJECT_NOTE_COLLECTION_REQUIRED")
        self._notes = notes
        self._events = events

    @staticmethod
    def ensure_indexes(notes: Any, events: Any) -> None:
        """Install deterministic tenant/project/idempotency indexes at startup."""
        if notes is None or events is None:
            raise ProjectNoteRegistryError("PROJECT_NOTE_COLLECTION_REQUIRED")
        try:
            notes.create_index(
                [("tenant_id", ASCENDING), ("project_id", ASCENDING), ("note_id", ASCENDING)],
                unique=True, name="wilsy_project_note_identity_unique",
            )
            notes.create_index(
                [("tenant_id", ASCENDING), ("project_id", ASCENDING),
                 ("archived_at", ASCENDING), ("created_at", ASCENDING),
                 ("note_id", ASCENDING)],
                name="wilsy_project_note_visible_page",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
                unique=True, name="wilsy_project_note_idempotency_unique",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("project_id", ASCENDING),
                 ("note_id", ASCENDING), ("revision", ASCENDING)],
                unique=True, name="wilsy_project_note_event_revision_unique",
            )
        except PyMongoError as error:
            raise ProjectNoteRegistryError("PROJECT_NOTE_INDEX_UNAVAILABLE") from error

    def get(
        self, *, tenant_id: str, project_id: str,
        note_id: str, session: Any, include_archived: bool = False,
    ) -> ProjectNote:
        """Return an exact-tenant note or indistinguishable not-found."""
        query: dict[str, object] = {
            "tenant_id": _exact(tenant_id, "tenant_id"),
            "project_id": _exact(project_id, "project_id"),
            "note_id": _exact(note_id, "note_id"),
        }
        if not include_archived:
            query["archived_at"] = None
        try:
            row = self._notes.find_one(query, session=_session(session))
        except PyMongoError as error:
            raise ProjectNoteRegistryError("PROJECT_NOTE_READ_UNAVAILABLE") from error
        if row is None:
            raise ProjectNoteNotFound("PROJECT_NOTE_NOT_FOUND")
        return _hydrate(row)

    def list_for_project(
        self, *, tenant_id: str, project_id: str, session: Any,
        limit: int = 50, offset: int = 0,
    ) -> tuple[tuple[ProjectNote, ...], bool]:
        """Return a bounded verified page and next-page evidence for one project."""
        tenant = _exact(tenant_id, "tenant_id")
        project = _exact(project_id, "project_id")
        if type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or offset < 0:
            raise ProjectNoteRegistryError("PROJECT_NOTE_PAGE_INVALID")
        try:
            cursor = (self._notes.find({
                "tenant_id": tenant, "project_id": project, "archived_at": None,
            }, session=_session(session))
                .sort([("created_at", ASCENDING), ("note_id", ASCENDING)])
                .skip(offset).limit(limit + 1))
            values = tuple(_hydrate(row) for row in cursor)
        except PyMongoError as error:
            raise ProjectNoteRegistryError("PROJECT_NOTE_LIST_UNAVAILABLE") from error
        return values[:limit], len(values) > limit

    def _find_replay(
        self, *, tenant_id: str, idempotency_key: str,
        fingerprint: str, event_type: str, session: Any,
    ) -> ProjectNote | None:
        """Return the immutable original snapshot only for identical replay."""
        tenant = _exact(tenant_id, "tenant_id")
        key = _exact(idempotency_key, "idempotency_key", 200)
        try:
            event = self._events.find_one({
                "tenant_id": tenant, "idempotency_key": key,
            }, session=_session(session))
        except PyMongoError as error:
            raise ProjectNoteRegistryError("PROJECT_NOTE_REPLAY_UNAVAILABLE") from error
        if event is None:
            return None
        if event.get("request_fingerprint") != fingerprint or event.get("event_type") != event_type:
            raise ProjectNoteConflict("PROJECT_NOTE_DIVERGENT_REPLAY")
        snapshot = event.get("result_snapshot")
        if not isinstance(snapshot, Mapping):
            raise ProjectNoteRegistryError("PROJECT_NOTE_EVENT_INVALID")
        note = _hydrate(snapshot)
        if note.tenant_id != tenant or note.note_id != event.get("note_id") or note.project_id != event.get("project_id"):
            raise ProjectNoteRegistryError("PROJECT_NOTE_EVENT_INVALID")
        return note

    def _event(
        self, *, prior: ProjectNote | None, result: ProjectNote,
        event_type: str, idempotency_key: str, request_fingerprint: str,
        actor_principal_id: str, occurred_at: datetime, session: Any,
    ) -> None:
        """Append a source-authored event inside the caller-owned transaction."""
        if event_type not in _EVENT_TYPES:
            raise ProjectNoteRegistryError("PROJECT_NOTE_EVENT_TYPE_INVALID")
        record = {
            "tenant_id": result.tenant_id, "project_id": result.project_id,
            "note_id": result.note_id, "revision": result.revision,
            "event_type": event_type,
            "actor_principal_id": _exact(actor_principal_id, "actor_principal_id"),
            "idempotency_key": _exact(idempotency_key, "idempotency_key", 200),
            "request_fingerprint": request_fingerprint,
            "prior_fingerprint": prior.fingerprint if prior else None,
            "result_fingerprint": result.fingerprint,
            "result_snapshot": result.to_dict(),
            "occurred_at": occurred_at,
            "schema": "wilsy.project.note.event.v1",
        }
        try:
            self._events.insert_one(record, session=_session(session))
        except DuplicateKeyError as error:
            raise ProjectNoteConflict("PROJECT_NOTE_EVENT_CONFLICT") from error
        except PyMongoError as error:
            raise ProjectNoteRegistryError("PROJECT_NOTE_EVENT_WRITE_UNAVAILABLE") from error

    def create_or_replay(
        self, *, note: ProjectNote, actor_principal_id: str,
        idempotency_key: str, occurred_at: datetime, session: Any,
    ) -> ProjectNote:
        """Insert an author-owned note with immutable replay and audit evidence."""
        if not isinstance(note, ProjectNote) or note.revision != 1 or note.archived_at is not None:
            raise ProjectNoteRegistryError("PROJECT_NOTE_CREATE_STATE_INVALID")
        actor = _exact(actor_principal_id, "actor_principal_id")
        if actor != note.author_principal_id or note.note_id != note_id_for_command(
            note.tenant_id, note.project_id, actor, idempotency_key,
        ):
            raise ProjectNoteConflict("PROJECT_NOTE_IDENTITY_INVALID")
        stamp = occurred_at
        fp = _fingerprint({
            "type": "create", "tenant_id": note.tenant_id,
            "project_id": note.project_id, "note_id": note.note_id,
            "actor": actor, "body": note.body,
        })
        replay = self._find_replay(
            tenant_id=note.tenant_id, idempotency_key=idempotency_key,
            fingerprint=fp, event_type="PROJECT_NOTE_CREATED", session=session,
        )
        if replay is not None:
            return replay
        try:
            self._notes.insert_one(note.to_dict(), session=_session(session))
        except DuplicateKeyError as error:
            raise ProjectNoteConflict("PROJECT_NOTE_ALREADY_EXISTS") from error
        except PyMongoError as error:
            raise ProjectNoteRegistryError("PROJECT_NOTE_WRITE_UNAVAILABLE") from error
        self._event(
            prior=None, result=note, event_type="PROJECT_NOTE_CREATED",
            idempotency_key=idempotency_key, request_fingerprint=fp,
            actor_principal_id=actor, occurred_at=stamp, session=session,
        )
        return note

    def revise_or_replay(
        self, *, tenant_id: str, project_id: str, note_id: str,
        actor_principal_id: str, expected_revision: int, body: str,
        idempotency_key: str, occurred_at: datetime, session: Any,
    ) -> ProjectNote:
        """Apply authored note revision under exact CAS and durable replay."""
        tenant = _exact(tenant_id, "tenant_id")
        project = _exact(project_id, "project_id")
        identity = _exact(note_id, "note_id")
        actor = _exact(actor_principal_id, "actor_principal_id")
        fp = _fingerprint({
            "type": "revise", "tenant_id": tenant, "project_id": project,
            "note_id": identity, "actor": actor,
            "expected_revision": expected_revision, "body": body,
        })
        replay = self._find_replay(
            tenant_id=tenant, idempotency_key=idempotency_key,
            fingerprint=fp, event_type="PROJECT_NOTE_REVISED", session=session,
        )
        if replay is not None:
            return replay
        prior = self.get(
            tenant_id=tenant, project_id=project, note_id=identity,
            session=session,
        )
        try:
            revised = prior.revise(
                actor_principal_id=actor, expected_revision=expected_revision,
                body=body, updated_at=occurred_at,
            )
        except ProjectNoteError as error:
            raise ProjectNoteConflict(error.code) from error
        self._apply_revision(prior, revised, session)
        self._event(
            prior=prior, result=revised, event_type="PROJECT_NOTE_REVISED",
            idempotency_key=idempotency_key, request_fingerprint=fp,
            actor_principal_id=actor, occurred_at=occurred_at, session=session,
        )
        return revised

    def archive_or_replay(
        self, *, tenant_id: str, project_id: str, note_id: str,
        actor_principal_id: str, expected_revision: int,
        idempotency_key: str, occurred_at: datetime, session: Any,
    ) -> ProjectNote:
        """Soft archive author-owned text and retain immutable event evidence."""
        tenant = _exact(tenant_id, "tenant_id")
        project = _exact(project_id, "project_id")
        identity = _exact(note_id, "note_id")
        actor = _exact(actor_principal_id, "actor_principal_id")
        fp = _fingerprint({
            "type": "archive", "tenant_id": tenant, "project_id": project,
            "note_id": identity, "actor": actor, "expected_revision": expected_revision,
        })
        replay = self._find_replay(
            tenant_id=tenant, idempotency_key=idempotency_key,
            fingerprint=fp, event_type="PROJECT_NOTE_ARCHIVED", session=session,
        )
        if replay is not None:
            return replay
        prior = self.get(
            tenant_id=tenant, project_id=project, note_id=identity, session=session,
        )
        try:
            archived = prior.archive(
                actor_principal_id=actor, expected_revision=expected_revision,
                archived_at=occurred_at,
            )
        except ProjectNoteError as error:
            raise ProjectNoteConflict(error.code) from error
        self._apply_revision(prior, archived, session)
        self._event(
            prior=prior, result=archived, event_type="PROJECT_NOTE_ARCHIVED",
            idempotency_key=idempotency_key, request_fingerprint=fp,
            actor_principal_id=actor, occurred_at=occurred_at, session=session,
        )
        return archived

    def _apply_revision(
        self, prior: ProjectNote, updated: ProjectNote, session: Any,
    ) -> None:
        """Commit exact current revision or fail rather than silently overwrite."""
        try:
            change = self._notes.update_one({
                "tenant_id": prior.tenant_id, "project_id": prior.project_id,
                "note_id": prior.note_id, "revision": prior.revision,
                "fingerprint": prior.fingerprint, "archived_at": None,
            }, {"$set": updated.to_dict()}, session=_session(session))
        except PyMongoError as error:
            raise ProjectNoteRegistryError("PROJECT_NOTE_WRITE_UNAVAILABLE") from error
        if change.matched_count != 1:
            raise ProjectNoteConflict("PROJECT_NOTE_REVISION_CONFLICT")

    def list_events(
        self, *, tenant_id: str, project_id: str, note_id: str,
        session: Any, limit: int = 100,
    ) -> tuple[dict[str, object], ...]:
        """Return bounded immutable note-event evidence with snapshot validation."""
        tenant = _exact(tenant_id, "tenant_id")
        project = _exact(project_id, "project_id")
        identity = _exact(note_id, "note_id")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ProjectNoteRegistryError("PROJECT_NOTE_EVENT_LIMIT_INVALID")
        try:
            rows = list(self._events.find({
                "tenant_id": tenant, "project_id": project, "note_id": identity,
            }, session=_session(session))
                .sort("revision", ASCENDING).limit(limit + 1))
        except PyMongoError as error:
            raise ProjectNoteRegistryError("PROJECT_NOTE_EVENT_READ_UNAVAILABLE") from error
        if len(rows) > limit:
            raise ProjectNoteRegistryError("PROJECT_NOTE_EVENT_PAGE_BOUND_EXCEEDED")
        output = []
        for row in rows:
            snapshot = row.get("result_snapshot")
            if not isinstance(snapshot, Mapping):
                raise ProjectNoteRegistryError("PROJECT_NOTE_EVENT_INVALID")
            note = _hydrate(snapshot)
            if (
                row.get("tenant_id") != tenant or row.get("project_id") != project
                or row.get("note_id") != identity or row.get("revision") != note.revision
                or row.get("result_fingerprint") != note.fingerprint
                or row.get("event_type") not in _EVENT_TYPES
            ):
                raise ProjectNoteRegistryError("PROJECT_NOTE_EVENT_INVALID")
            output.append({
                "event_type": row["event_type"],
                "revision": note.revision,
                "actor_principal_id": row["actor_principal_id"],
                "occurred_at": (
                    row["occurred_at"].isoformat()
                    if isinstance(row.get("occurred_at"), datetime) else None
                ),
                "result_fingerprint": note.fingerprint,
            })
        return tuple(output)


__all__ = [
    "VERSION", "COLLECTION", "EVENT_COLLECTION", "ProjectNoteRegistry",
    "ProjectNoteRegistryError", "ProjectNoteConflict", "ProjectNoteNotFound",
    "note_id_for_command",
]

# ARTIFACT: project_note_registry.py
# VERSION: v1.0.0-AUDITED-EXACT-TENANT-PROJECT-NOTES
# AUTHORITY BOUNDARY: persistence-only; EOS owns authenticated permission and admission
# TENANT POSTURE: every query binds tenant_id + project_id with no fallback
# FAIL-CLOSED POSTURE: invalid event, author, revision, replay or audit denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
