"""TITLE: WILSY OS Tenant Project Notes and Revision Evidence Registry
VERSION: v1.0.1-IMMUTABLE-NOTE-EVENT-HYDRATION
AUTHORITY: Python EOS tenant-scoped project collaboration persistence.
EPITOME: Store source-owned project notes with author ownership, bounded pages,
         compare-and-set revisions, immutable event snapshots and replay guards.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/projects/project_notes_registry.py
COLLABORATION / OWNERSHIP: Projects router proves project access/record visibility;
         this registry owns note persistence only and receives caller Mongo sessions.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.1-IMMUTABLE-NOTE-EVENT-HYDRATION supports ISO UTC
         timestamps from immutable event snapshots as well as trusted BSON UTC
         readbacks, retaining command-time timezone strictness.
         v1.0.0-AUTHORED-PROJECT-NOTES establishes exact-tenant authored
         note create, bounded list, revision update and soft-redaction events.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Notes never establish task assignment, decisions,
         approvals, IAM permissions or document custody. No raw PII in logs.
TENANT BOUNDARY: Every lookup, CAS, idempotency event and index binds tenant_id.
AUTHORITY BOUNDARY: Caller must independently authorize project read/update and
         record visibility; author-only update/redaction is enforced here.
TRANSACTION BOUNDARY: Caller creates Mongo snapshot/majority transaction and
         supplies its session; registry never starts a transaction or creates DDL.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha3_256, sha3_512
import hmac
import json
from typing import Any, Final, Mapping

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError


VERSION: Final[str] = "v1.0.1-IMMUTABLE-NOTE-EVENT-HYDRATION"
COLLECTION: Final[str] = "wilsy_project_notes"
EVENT_COLLECTION: Final[str] = "wilsy_project_note_events"
_FIELDS: Final[frozenset[str]] = frozenset({
    "tenant_id", "project_id", "note_id", "created_by_principal_id",
    "body", "revision", "created_at", "updated_at", "redacted_at",
    "fingerprint",
})


class ProjectNoteError(RuntimeError):
    """Stable project-note validation, persistence or integrity failure."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class ProjectNoteConflict(ProjectNoteError):
    """Conflicting revision, replay or author identity."""


class ProjectNoteNotFound(ProjectNoteError):
    """Missing or foreign-tenant note, without disclosing another tenant."""


def _text(value: object, name: str, maximum: int = 180) -> str:
    """Reject missing, unbounded, controls and whitespace-ambiguous identifiers."""
    if (
        not isinstance(value, str) or not value or len(value) > maximum
        or value != value.strip()
        or any(ord(ch) < 32 for ch in value)
    ):
        raise ProjectNoteError("PROJECT_NOTE_" + name + "_INVALID")
    return value


def _body(value: object) -> str:
    """Allow bounded multiline note content without trusting HTML markup."""
    if (
        not isinstance(value, str) or not value.strip() or len(value) > 4000
        or value != value.strip()
        or any(ord(ch) < 32 and ch not in "\n\t" for ch in value)
    ):
        raise ProjectNoteError("PROJECT_NOTE_BODY_INVALID")
    return value


def _session(value: object) -> object:
    """Reject attempts to write or read without the caller-owned session."""
    if value is None:
        raise ProjectNoteError("PROJECT_NOTE_SESSION_REQUIRED")
    return value


def _instant(value: object) -> datetime:
    """Normalize Mongo UTC readback while requiring aware command instants."""
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as error:
            raise ProjectNoteError("PROJECT_NOTE_TIMESTAMP_INVALID") from error
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ProjectNoteError("PROJECT_NOTE_TIMESTAMP_INVALID")
        value = parsed
    if not isinstance(value, datetime):
        raise ProjectNoteError("PROJECT_NOTE_TIMESTAMP_INVALID")
    if value.tzinfo is None:
        # BSON datetime from a trusted PyMongo collection represents UTC.
        value = value.replace(tzinfo=timezone.utc)
    if value.utcoffset() is None:
        raise ProjectNoteError("PROJECT_NOTE_TIMESTAMP_INVALID")
    return value.astimezone(timezone.utc)


def _command_instant(value: object) -> datetime:
    """Require explicitly timezone-aware caller instants for write commands."""
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None or value.utcoffset() is None
    ):
        raise ProjectNoteError("PROJECT_NOTE_TIMESTAMP_INVALID")
    return value.astimezone(timezone.utc)


def _digest(material: Mapping[str, object]) -> str:
    """Fingerprint canonical request/record fields, not an authorization claim."""
    return sha3_512(
        json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _semantic(record: Mapping[str, object]) -> dict[str, object]:
    """Canonical UTC semantic representation of one note revision."""
    return {
        "tenant_id": record["tenant_id"],
        "project_id": record["project_id"],
        "note_id": record["note_id"],
        "created_by_principal_id": record["created_by_principal_id"],
        "body": record["body"],
        "revision": record["revision"],
        "created_at": _instant(record["created_at"]).isoformat(),
        "updated_at": _instant(record["updated_at"]).isoformat(),
        "redacted_at": _instant(record["redacted_at"]).isoformat() if record["redacted_at"] else None,
    }


def _hydrate(row: Mapping[str, object]) -> dict[str, object]:
    """Fail closed on malformed or fingerprint-mismatched persisted records."""
    if not isinstance(row, Mapping) or set(row) - {"_id"} != _FIELDS:
        raise ProjectNoteError("PROJECT_NOTE_RECORD_INVALID")
    for field in ("tenant_id", "project_id", "note_id", "created_by_principal_id"):
        _text(row[field], field.upper())
    if not isinstance(row["revision"], int) or row["revision"] < 1:
        raise ProjectNoteError("PROJECT_NOTE_REVISION_INVALID")
    if row["redacted_at"] is None:
        _body(row["body"])
    elif row["body"] != "":
        raise ProjectNoteError("PROJECT_NOTE_REDACTION_INVALID")
    semantic = _semantic(row)
    fingerprint = row["fingerprint"]
    if not isinstance(fingerprint, str) or not hmac.compare_digest(
        fingerprint, _digest(semantic),
    ):
        raise ProjectNoteError("PROJECT_NOTE_FINGERPRINT_MISMATCH")
    return {**semantic, "fingerprint": fingerprint}


class ProjectNotesRegistry:
    """Own exact-tenant authored note state and immutable command events."""

    __slots__ = ("_notes", "_events")

    def __init__(self, notes: Any, events: Any) -> None:
        """Bind injected Mongo collections without making any database changes."""
        if notes is None or events is None:
            raise ProjectNoteError("PROJECT_NOTE_COLLECTION_REQUIRED")
        self._notes, self._events = notes, events

    @staticmethod
    def ensure_indexes(notes: Any, events: Any) -> None:
        """Prepare deterministic tenant/source identities before HTTP admission."""
        if notes is None or events is None:
            raise ProjectNoteError("PROJECT_NOTE_COLLECTION_REQUIRED")
        try:
            notes.create_index(
                [("tenant_id", ASCENDING), ("project_id", ASCENDING),
                 ("note_id", ASCENDING)],
                unique=True, name="wilsy_project_note_identity_unique",
            )
            notes.create_index(
                [("tenant_id", ASCENDING), ("project_id", ASCENDING),
                 ("created_at", DESCENDING), ("note_id", ASCENDING)],
                name="wilsy_project_note_recent",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
                unique=True, name="wilsy_project_note_event_replay_unique",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("project_id", ASCENDING),
                 ("note_id", ASCENDING), ("revision", ASCENDING)],
                unique=True, name="wilsy_project_note_revision_unique",
            )
        except PyMongoError as error:
            raise ProjectNoteError("PROJECT_NOTE_INDEX_UNAVAILABLE") from error

    def get(self, *, tenant_id: str, project_id: str, note_id: str,
            session: Any) -> dict[str, object]:
        """Return one verified note, making foreign scope indistinguishable."""
        query = {
            "tenant_id": _text(tenant_id, "TENANT_ID"),
            "project_id": _text(project_id, "PROJECT_ID"),
            "note_id": _text(note_id, "NOTE_ID"),
        }
        try:
            row = self._notes.find_one(query, session=_session(session))
        except PyMongoError as error:
            raise ProjectNoteError("PROJECT_NOTE_READ_UNAVAILABLE") from error
        if row is None:
            raise ProjectNoteNotFound("PROJECT_NOTE_NOT_FOUND")
        return _hydrate(row)

    def list_for_project(
        self, *, tenant_id: str, project_id: str,
        session: Any, limit: int = 50, offset: int = 0,
    ) -> tuple[dict[str, object], ...]:
        """Return a bounded and integrity-validated tenant/project note page."""
        tenant, project = _text(tenant_id, "TENANT_ID"), _text(project_id, "PROJECT_ID")
        if (
            type(limit) is not int or not 1 <= limit <= 100
            or type(offset) is not int or offset < 0
        ):
            raise ProjectNoteError("PROJECT_NOTE_PAGE_INVALID")
        try:
            cursor = self._notes.find(
                {"tenant_id": tenant, "project_id": project},
                session=_session(session),
            ).sort([("created_at", DESCENDING), ("note_id", ASCENDING)])
            rows = list(cursor.skip(offset).limit(limit))
        except PyMongoError as error:
            raise ProjectNoteError("PROJECT_NOTE_LIST_UNAVAILABLE") from error
        return tuple(_hydrate(row) for row in rows)

    def _replay(
        self, *, tenant_id: str, idempotency_key: str,
        fingerprint: str, session: Any,
    ) -> dict[str, object] | None:
        """Return immutable matching outcome; reject divergent command reuse."""
        try:
            event = self._events.find_one(
                {"tenant_id": tenant_id, "idempotency_key": idempotency_key},
                session=session,
            )
        except PyMongoError as error:
            raise ProjectNoteError("PROJECT_NOTE_EVENT_READ_UNAVAILABLE") from error
        if event is None:
            return None
        if event.get("request_fingerprint") != fingerprint:
            raise ProjectNoteConflict("PROJECT_NOTE_DIVERGENT_REPLAY")
        snapshot = event.get("result_snapshot")
        if not isinstance(snapshot, Mapping):
            raise ProjectNoteError("PROJECT_NOTE_EVENT_CORRUPT")
        return _hydrate(snapshot)

    def _event(
        self, *, tenant_id: str, project_id: str, note_id: str,
        actor: str, kind: str, key: str, fingerprint: str,
        result: Mapping[str, object], instant: datetime, session: Any,
    ) -> None:
        """Append a bounded replay and immutable note-revision event."""
        try:
            self._events.insert_one({
                "_id": tenant_id + ":" + key,
                "tenant_id": tenant_id, "project_id": project_id,
                "note_id": note_id, "event_type": kind,
                "revision": result["revision"], "actor_principal_id": actor,
                "idempotency_key": key,
                "request_fingerprint": fingerprint,
                "result_fingerprint": result["fingerprint"],
                "result_snapshot": dict(result), "occurred_at": instant,
            }, session=session)
        except DuplicateKeyError as error:
            raise ProjectNoteConflict("PROJECT_NOTE_EVENT_CONFLICT") from error
        except PyMongoError as error:
            raise ProjectNoteError("PROJECT_NOTE_EVENT_UNAVAILABLE") from error

    def create(
        self, *, tenant_id: str, project_id: str, actor_principal_id: str,
        body: str, idempotency_key: str, occurred_at: datetime,
        session: Any,
    ) -> dict[str, object]:
        """Create one authored note with deterministic identity and exact replay."""
        tenant = _text(tenant_id, "TENANT_ID")
        project = _text(project_id, "PROJECT_ID")
        actor = _text(actor_principal_id, "ACTOR")
        text = _body(body)
        key = _text(idempotency_key, "IDEMPOTENCY_KEY", maximum=160)
        tx = _session(session)
        now = _command_instant(occurred_at)
        fingerprint = _digest({
            "action": "CREATE", "tenant_id": tenant,
            "project_id": project, "actor": actor, "body": text,
            "key": key,
        })
        prior = self._replay(
            tenant_id=tenant, idempotency_key=key, fingerprint=fingerprint,
            session=tx,
        )
        if prior is not None:
            return prior
        note_id = "pnote-" + sha3_256(
            (tenant + "\0" + project + "\0" + actor + "\0" + key).encode("utf-8")
        ).hexdigest()[:32]
        record: dict[str, object] = {
            "tenant_id": tenant, "project_id": project,
            "note_id": note_id, "created_by_principal_id": actor,
            "body": text, "revision": 1, "created_at": now,
            "updated_at": now, "redacted_at": None,
        }
        record["fingerprint"] = _digest(_semantic(record))
        try:
            self._notes.insert_one({
                "_id": tenant + ":" + note_id, **record,
            }, session=tx)
        except DuplicateKeyError as error:
            raise ProjectNoteConflict("PROJECT_NOTE_IDENTITY_CONFLICT") from error
        except PyMongoError as error:
            raise ProjectNoteError("PROJECT_NOTE_CREATE_UNAVAILABLE") from error
        result = _hydrate(record)
        self._event(
            tenant_id=tenant, project_id=project, note_id=note_id,
            actor=actor, kind="PROJECT_NOTE_CREATED", key=key,
            fingerprint=fingerprint, result=result, instant=now, session=tx,
        )
        return result

    def revise(
        self, *, tenant_id: str, project_id: str, note_id: str,
        actor_principal_id: str, expected_revision: int,
        body: str | None, redact: bool, idempotency_key: str,
        occurred_at: datetime, session: Any,
    ) -> dict[str, object]:
        """CAS-revise or redact only the note author's current revision."""
        tenant = _text(tenant_id, "TENANT_ID")
        project = _text(project_id, "PROJECT_ID")
        identity = _text(note_id, "NOTE_ID")
        actor = _text(actor_principal_id, "ACTOR")
        key = _text(idempotency_key, "IDEMPOTENCY_KEY", maximum=160)
        tx = _session(session)
        now = _command_instant(occurred_at)
        if type(expected_revision) is not int or expected_revision < 1:
            raise ProjectNoteError("PROJECT_NOTE_REVISION_INVALID")
        if type(redact) is not bool or (redact and body is not None) or (not redact and body is None):
            raise ProjectNoteError("PROJECT_NOTE_COMMAND_INVALID")
        proposed = "" if redact else _body(body)
        fingerprint = _digest({
            "action": "REDACT" if redact else "REVISE",
            "tenant_id": tenant, "project_id": project, "note_id": identity,
            "actor": actor, "expected_revision": expected_revision,
            "body": proposed, "key": key,
        })
        prior = self._replay(
            tenant_id=tenant, idempotency_key=key, fingerprint=fingerprint,
            session=tx,
        )
        if prior is not None:
            return prior
        current = self.get(
            tenant_id=tenant, project_id=project, note_id=identity, session=tx,
        )
        if current["created_by_principal_id"] != actor:
            raise ProjectNoteConflict("PROJECT_NOTE_AUTHOR_REQUIRED")
        if current["redacted_at"] is not None:
            raise ProjectNoteConflict("PROJECT_NOTE_ALREADY_REDACTED")
        if current["revision"] != expected_revision:
            raise ProjectNoteConflict("PROJECT_NOTE_REVISION_CONFLICT")
        old_time = datetime.fromisoformat(str(current["updated_at"]))
        if now < old_time:
            raise ProjectNoteConflict("PROJECT_NOTE_TIMESTAMP_CONFLICT")
        updated: dict[str, object] = {
            **current,
            "body": proposed,
            "revision": expected_revision + 1,
            "updated_at": now,
            "redacted_at": now if redact else None,
        }
        updated["fingerprint"] = _digest(_semantic(updated))
        try:
            outcome = self._notes.update_one(
                {"tenant_id": tenant, "project_id": project,
                 "note_id": identity, "revision": expected_revision,
                 "redacted_at": None},
                {"$set": {
                    "body": updated["body"], "revision": updated["revision"],
                    "updated_at": updated["updated_at"],
                    "redacted_at": updated["redacted_at"],
                    "fingerprint": updated["fingerprint"],
                }},
                session=tx,
            )
        except PyMongoError as error:
            raise ProjectNoteError("PROJECT_NOTE_UPDATE_UNAVAILABLE") from error
        if getattr(outcome, "matched_count", 0) != 1:
            raise ProjectNoteConflict("PROJECT_NOTE_CONCURRENT_REVISION")
        result = _hydrate(updated)
        self._event(
            tenant_id=tenant, project_id=project, note_id=identity,
            actor=actor, kind="PROJECT_NOTE_REDACTED" if redact else "PROJECT_NOTE_REVISED",
            key=key, fingerprint=fingerprint, result=result,
            instant=now, session=tx,
        )
        return result


__all__ = [
    "VERSION", "COLLECTION", "EVENT_COLLECTION", "ProjectNotesRegistry",
    "ProjectNoteError", "ProjectNoteConflict", "ProjectNoteNotFound",
]

# ARTIFACT: project_notes_registry.py
# VERSION: v1.0.1-IMMUTABLE-NOTE-EVENT-HYDRATION
# AUTHORITY BOUNDARY: persistence-only, caller-owned session and author-only edits
# TENANT POSTURE: exact tenant and project filters for reads, writes, replay and events
# FAIL-CLOSED POSTURE: corruption, foreign scope, replay conflict and stale revisions deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
