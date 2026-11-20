"""TITLE: WILSY OS Project Notification and Read Receipt Authority
VERSION: v1.0.0-PROJECT-MENTION-INBOX-CAS
AUTHORITY: Python EOS durable recipient-scoped project notification registry.
EPITOME: Transactional comment-mention notifications, exact recipient inbox,
         unread/read state, deterministic source fingerprints and audit replay.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/projects/project_notification_registry.py
COLLABORATION / OWNERSHIP: Project comment command emits inbox records inside
         its caller-owned Mongo transaction; Projects HTTP owns current
         principal IAM, entitlement, exact project participant and task checks.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-PROJECT-MENTION-INBOX-CAS establishes exact-tenant durable
         in-app notification records with revisioned per-recipient read receipts.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No comment body, email, phone, provider endpoint,
         invented push delivery, or recipient PII beyond opaque principal IDs.
TENANT BOUNDARY: All writes/reads/replay bind exact tenant, project, recipient.
AUTHORITY BOUNDARY: A notification is an in-app work signal, not delivery
         proof, approval, signature, IAM grant or task completion authority.
TRANSACTION BOUNDARY: Caller-owned session and majority MongoDB transaction,
         DDL at startup; CAS/read receipt uses the identical passed session.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS executes all financial actions.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from hashlib import sha3_512
from hmac import compare_digest
import json
import re
from typing import Any, Final

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.projects.project_comment_registry import ProjectComment

VERSION: Final[str] = "v1.0.0-PROJECT-MENTION-INBOX-CAS"
SCHEMA: Final[str] = "wilsy.project.notification.v1"
COLLECTION: Final[str] = "wilsy_project_notifications"
EVENT_COLLECTION: Final[str] = "wilsy_project_notification_events"
_NOTIFICATION_ID = re.compile(r"^pnf-[a-f0-9]{48}$")
_HEX = re.compile(r"^[a-f0-9]{128}$")
_PROJECT = re.compile(r"^prj-[a-f0-9]{48}$")
_TASK = re.compile(r"^ptk-[a-f0-9]{48}$")
_COMMENT = re.compile(r"^pcm-[a-f0-9]{48}$")
_DENIED_TENANT = frozenset({
    "MASTER", "GLOBAL_ROOT", "WILSY_ROOT", "WILSY_MASTER",
    "WILSY_GLOBAL_ROOT", "SOVEREIGN_ROOT",
})


class ProjectNotificationError(RuntimeError):
    """Bounded source-integrity or operational notification error."""

    def __init__(self, code: str) -> None:
        """Return a stable non-disclosing source error code."""
        self.code = code
        super().__init__(code)


class ProjectNotificationConflict(ProjectNotificationError):
    """Stale read receipt, duplicate or divergent source notification evidence."""


class ProjectNotificationNotFound(ProjectNotificationError):
    """Non-disclosing absent or non-recipient notification state."""


def _id(value: object, kind: str) -> str:
    """Validate exact immutable coordinates and deny retired tenant aliases."""
    if (
        not isinstance(value, str) or not 1 <= len(value) <= 180
        or value != value.strip() or any(ord(char) <= 32 for char in value)
    ):
        raise ProjectNotificationError("PROJECT_NOTIFICATION_" + kind + "_INVALID")
    if kind == "TENANT" and value.upper() in _DENIED_TENANT:
        raise ProjectNotificationError("PROJECT_NOTIFICATION_TENANT_INVALID")
    pattern = {
        "PROJECT": _PROJECT, "TASK": _TASK,
        "COMMENT": _COMMENT, "NOTIFICATION": _NOTIFICATION_ID,
    }.get(kind)
    if pattern and pattern.fullmatch(value) is None:
        raise ProjectNotificationError("PROJECT_NOTIFICATION_" + kind + "_INVALID")
    return value


def _time(value: object) -> datetime:
    """Require timezone-aware command instants; normalize to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ProjectNotificationError("PROJECT_NOTIFICATION_TIME_INVALID")
    return value.astimezone(timezone.utc)


def _source_time(value: object) -> datetime:
    """Interpret PyMongo UTC-naive BSON instants without accepting naive input."""
    if not isinstance(value, datetime):
        raise ProjectNotificationError("PROJECT_NOTIFICATION_TIME_INVALID")
    return _time(value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value)


def _digest(value: dict[str, object]) -> str:
    """Calculate canonical SHA3-512 semantic integrity, not a signature."""
    return sha3_512(json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()


def notification_id_for_comment(comment: ProjectComment, recipient: str) -> str:
    """Derive a globally stable in-tenant mention notification coordinate."""
    if not isinstance(comment, ProjectComment):
        raise ProjectNotificationError("PROJECT_NOTIFICATION_COMMENT_INVALID")
    target = _id(recipient, "RECIPIENT")
    if target not in comment.mentions:
        raise ProjectNotificationError("PROJECT_NOTIFICATION_RECIPIENT_INVALID")
    return "pnf-" + sha3_512("\0".join((
        comment.tenant_id, comment.project_id, comment.task_id,
        comment.comment_id, target,
    )).encode("utf-8")).hexdigest()[:48]


@dataclass(frozen=True, slots=True)
class ProjectNotification:
    """Recipient-only immutable source mention fact plus revisioned read state."""

    tenant_id: str
    project_id: str
    task_id: str
    comment_id: str
    notification_id: str
    recipient_principal_id: str
    actor_principal_id: str
    occurred_at: datetime
    read_at: datetime | None = None
    revision: int = 1
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Guard all scope and integrity attributes against forged source state."""
        for kind, value in (
            ("TENANT", self.tenant_id), ("PROJECT", self.project_id),
            ("TASK", self.task_id), ("COMMENT", self.comment_id),
            ("NOTIFICATION", self.notification_id),
            ("RECIPIENT", self.recipient_principal_id),
            ("ACTOR", self.actor_principal_id),
        ):
            _id(value, kind)
        if type(self.revision) is not int or self.revision not in (1, 2):
            raise ProjectNotificationError("PROJECT_NOTIFICATION_REVISION_INVALID")
        stamp = _time(self.occurred_at)
        object.__setattr__(self, "occurred_at", stamp)
        if self.read_at is not None:
            read = _time(self.read_at)
            if self.revision != 2 or read < stamp:
                raise ProjectNotificationError("PROJECT_NOTIFICATION_READ_INVALID")
            object.__setattr__(self, "read_at", read)
        elif self.revision != 1:
            raise ProjectNotificationError("PROJECT_NOTIFICATION_READ_INVALID")
        digest = _digest(self._canonical())
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or _HEX.fullmatch(self.fingerprint) is None
            or not compare_digest(self.fingerprint, digest)
        ):
            raise ProjectNotificationError("PROJECT_NOTIFICATION_FINGERPRINT_INVALID")
        object.__setattr__(self, "fingerprint", digest)

    def _canonical(self) -> dict[str, object]:
        """Represent authoritative notification state without derived checksum."""
        return {
            "schema": SCHEMA, "tenant_id": self.tenant_id,
            "project_id": self.project_id, "task_id": self.task_id,
            "comment_id": self.comment_id, "notification_id": self.notification_id,
            "recipient_principal_id": self.recipient_principal_id,
            "actor_principal_id": self.actor_principal_id,
            "occurred_at": self.occurred_at.isoformat(),
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "revision": self.revision,
        }

    def to_dict(self) -> dict[str, object]:
        """Return source state and SHA3-512 integrity checksum."""
        return {**self._canonical(), "fingerprint": self.fingerprint}

    @classmethod
    def hydrate(cls, row: dict[str, object]) -> ProjectNotification:
        """Verify stored schema and exact fingerprint before readback."""
        fields = {
            "schema", "tenant_id", "project_id", "task_id", "comment_id",
            "notification_id", "recipient_principal_id", "actor_principal_id",
            "occurred_at", "read_at", "revision", "fingerprint",
        }
        if not isinstance(row, dict) or set(row) != fields or row["schema"] != SCHEMA:
            raise ProjectNotificationError("PROJECT_NOTIFICATION_RECORD_INVALID")
        data = {key: value for key, value in row.items() if key != "schema"}
        for field in ("occurred_at", "read_at"):
            value = data[field]
            if value is None and field == "read_at":
                continue
            try:
                data[field] = (
                    _source_time(value) if isinstance(value, datetime)
                    else _time(datetime.fromisoformat(value))
                    if isinstance(value, str) else _source_time(value)
                )
            except (TypeError, ValueError) as error:
                raise ProjectNotificationError("PROJECT_NOTIFICATION_TIME_INVALID") from error
        try:
            return cls(**data)
        except TypeError as error:
            raise ProjectNotificationError("PROJECT_NOTIFICATION_RECORD_INVALID") from error

    def mark_read(self, *, expected_revision: int, instant: datetime) -> ProjectNotification:
        """Transition exactly one unread recipient record to read under CAS."""
        if type(expected_revision) is not int or expected_revision != self.revision:
            raise ProjectNotificationConflict("PROJECT_NOTIFICATION_REVISION_CONFLICT")
        if self.read_at is not None:
            raise ProjectNotificationConflict("PROJECT_NOTIFICATION_ALREADY_READ")
        return replace(self, revision=2, read_at=_time(instant), fingerprint="")


class ProjectNotificationRegistry:
    """Exact recipient in-project notifications with durable read-receipt audit."""

    def __init__(self, notifications: Any, events: Any) -> None:
        """Adopt collections; never create clients, sessions or source records."""
        if notifications is None or events is None:
            raise ProjectNotificationError("PROJECT_NOTIFICATION_COLLECTIONS_REQUIRED")
        self._notifications = notifications
        self._events = events

    @staticmethod
    def ensure_indexes(notifications: Any, events: Any) -> None:
        """Index immutable mention identity, recipient inbox and receipt replay."""
        try:
            notifications.create_index([
                ("tenant_id", ASCENDING), ("notification_id", ASCENDING),
            ], unique=True, name="wilsy_project_notification_identity_unique")
            notifications.create_index([
                ("tenant_id", ASCENDING), ("project_id", ASCENDING),
                ("recipient_principal_id", ASCENDING), ("occurred_at", DESCENDING),
                ("notification_id", ASCENDING),
            ], name="wilsy_project_notification_recipient_inbox")
            events.create_index([
                ("tenant_id", ASCENDING), ("notification_id", ASCENDING),
                ("event_type", ASCENDING),
            ], unique=True, name="wilsy_project_notification_event_type_unique")
            events.create_index([
                ("tenant_id", ASCENDING), ("recipient_principal_id", ASCENDING),
                ("idempotency_key", ASCENDING),
            ], unique=True, partialFilterExpression={"idempotency_key": {"$type": "string"}},
                name="wilsy_project_notification_receipt_replay",
            )
        except PyMongoError as error:
            raise ProjectNotificationError("PROJECT_NOTIFICATION_INDEX_UNAVAILABLE") from error

    def append_for_comment(self, *, comment: ProjectComment, session: Any) -> tuple[ProjectNotification, ...]:
        """Write all mention notifications and issue events in caller's transaction.

        Same comment replay returns exact original notification records. The
        caller must have verified each mentioned principal's current project
        participation before invoking this method.
        """
        if session is None:
            raise ProjectNotificationError("PROJECT_NOTIFICATION_SESSION_REQUIRED")
        result = []
        for recipient in comment.mentions:
            identity = notification_id_for_comment(comment, recipient)
            record = ProjectNotification(
                tenant_id=comment.tenant_id, project_id=comment.project_id,
                task_id=comment.task_id, comment_id=comment.comment_id,
                notification_id=identity, recipient_principal_id=recipient,
                actor_principal_id=comment.author_principal_id,
                occurred_at=comment.created_at,
            )
            try:
                existing = self._notifications.find_one({
                    "tenant_id": comment.tenant_id, "notification_id": identity,
                    "project_id": comment.project_id,
                    "recipient_principal_id": recipient,
                }, session=session)
                if existing is not None:
                    historical = self._events.find_one({
                        "tenant_id": comment.tenant_id, "notification_id": identity,
                        "event_type": "PROJECT_NOTIFICATION_CREATED",
                    }, session=session)
                    if (
                        historical is None
                        or historical.get("comment_fingerprint") != comment.fingerprint
                        or historical.get("source_notification_fingerprint") != record.fingerprint
                    ):
                        raise ProjectNotificationConflict("PROJECT_NOTIFICATION_SOURCE_DIVERGENCE")
                    result.append(ProjectNotification.hydrate({
                        key: value for key, value in existing.items() if key != "_id"
                    }))
                    continue
                self._notifications.insert_one(record.to_dict(), session=session)
                self._events.insert_one({
                    "schema": "wilsy.project.notification.event.v1",
                    "tenant_id": comment.tenant_id,
                    "project_id": comment.project_id, "task_id": comment.task_id,
                    "comment_id": comment.comment_id,
                    "notification_id": identity,
                    "recipient_principal_id": recipient,
                    "event_type": "PROJECT_NOTIFICATION_CREATED",
                    "idempotency_key": None, "revision": 1,
                    "comment_fingerprint": comment.fingerprint,
                    "source_notification_fingerprint": record.fingerprint,
                    "occurred_at": comment.created_at,
                }, session=session)
            except DuplicateKeyError as error:
                raise ProjectNotificationConflict("PROJECT_NOTIFICATION_DUPLICATE") from error
            except PyMongoError as error:
                raise ProjectNotificationError("PROJECT_NOTIFICATION_WRITE_UNAVAILABLE") from error
            result.append(record)
        return tuple(result)

    def list_for_recipient(
        self, *, tenant_id: str, project_id: str, recipient_principal_id: str,
        session: Any, limit: int = 50, offset: int = 0,
    ) -> tuple[tuple[ProjectNotification, ...], bool]:
        """Read only one exact authenticated recipient's in-project inbox."""
        if session is None:
            raise ProjectNotificationError("PROJECT_NOTIFICATION_SESSION_REQUIRED")
        if type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or offset < 0:
            raise ProjectNotificationError("PROJECT_NOTIFICATION_PAGE_INVALID")
        query = {
            "tenant_id": _id(tenant_id, "TENANT"),
            "project_id": _id(project_id, "PROJECT"),
            "recipient_principal_id": _id(recipient_principal_id, "RECIPIENT"),
        }
        try:
            cursor = self._notifications.find(query, session=session).sort([
                ("occurred_at", DESCENDING), ("notification_id", ASCENDING),
            ]).skip(offset).limit(limit + 1)
            values = tuple(ProjectNotification.hydrate({
                key: value for key, value in item.items() if key != "_id"
            }) for item in cursor)
        except PyMongoError as error:
            raise ProjectNotificationError("PROJECT_NOTIFICATION_READ_UNAVAILABLE") from error
        return values[:limit], len(values) > limit

    def mark_read(
        self, *, tenant_id: str, project_id: str, recipient_principal_id: str,
        notification_id: str, expected_revision: int, idempotency_key: str,
        occurred_at: datetime, session: Any,
    ) -> ProjectNotification:
        """Persist recipient-only CAS read receipt and immutable audit event."""
        if session is None:
            raise ProjectNotificationError("PROJECT_NOTIFICATION_SESSION_REQUIRED")
        coords = {
            "tenant_id": _id(tenant_id, "TENANT"),
            "project_id": _id(project_id, "PROJECT"),
            "recipient_principal_id": _id(recipient_principal_id, "RECIPIENT"),
            "notification_id": _id(notification_id, "NOTIFICATION"),
        }
        key = _id(idempotency_key, "KEY")
        digest = _digest({
            "command": "READ", **coords, "expected_revision": expected_revision,
        })
        try:
            replay = self._events.find_one({
                "tenant_id": tenant_id, "recipient_principal_id": recipient_principal_id,
                "idempotency_key": key,
            }, session=session)
            if replay is not None:
                if replay.get("request_digest") != digest or replay.get("event_type") != "PROJECT_NOTIFICATION_READ":
                    raise ProjectNotificationConflict("PROJECT_NOTIFICATION_DIVERGENT_REPLAY")
                snapshot = replay.get("result_snapshot")
                if not isinstance(snapshot, dict):
                    raise ProjectNotificationError("PROJECT_NOTIFICATION_EVENT_INVALID")
                previous = ProjectNotification.hydrate(snapshot)
                if (
                    previous.tenant_id != tenant_id
                    or previous.project_id != project_id
                    or previous.recipient_principal_id != recipient_principal_id
                    or previous.notification_id != notification_id
                    or replay.get("result_fingerprint") != previous.fingerprint
                ):
                    raise ProjectNotificationError("PROJECT_NOTIFICATION_EVENT_INVALID")
                return previous
            row = self._notifications.find_one(coords, session=session)
            if row is None:
                raise ProjectNotificationNotFound("PROJECT_NOTIFICATION_NOT_FOUND")
            current = ProjectNotification.hydrate({
                key: value for key, value in row.items() if key != "_id"
            })
            updated = current.mark_read(
                expected_revision=expected_revision, instant=occurred_at,
            )
            result = self._notifications.update_one({
                **coords, "revision": current.revision,
                "fingerprint": current.fingerprint,
            }, {"$set": updated.to_dict()}, session=session)
            if result.matched_count != 1:
                raise ProjectNotificationConflict("PROJECT_NOTIFICATION_REVISION_CONFLICT")
            self._events.insert_one({
                "schema": "wilsy.project.notification.event.v1",
                **coords, "task_id": updated.task_id,
                "comment_id": updated.comment_id,
                "event_type": "PROJECT_NOTIFICATION_READ",
                "idempotency_key": key, "request_digest": digest,
                "revision": 2, "result_fingerprint": updated.fingerprint,
                "result_snapshot": updated.to_dict(), "occurred_at": updated.read_at,
            }, session=session)
            return updated
        except DuplicateKeyError as error:
            raise ProjectNotificationConflict("PROJECT_NOTIFICATION_RECEIPT_CONFLICT") from error
        except PyMongoError as error:
            raise ProjectNotificationError("PROJECT_NOTIFICATION_WRITE_UNAVAILABLE") from error


__all__ = [
    "VERSION", "SCHEMA", "COLLECTION", "EVENT_COLLECTION",
    "ProjectNotification", "ProjectNotificationRegistry", "ProjectNotificationError",
    "ProjectNotificationConflict", "ProjectNotificationNotFound",
    "notification_id_for_comment",
]

# ARTIFACT: project_notification_registry.py
# VERSION: v1.0.0-PROJECT-MENTION-INBOX-CAS
# AUTHORITY BOUNDARY: in-app notification records only, no transport delivery
# TENANT POSTURE: exact tenant/project/recipient and source comment event
# FAIL-CLOSED POSTURE: missing, foreign, divergent, stale or corrupted deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
