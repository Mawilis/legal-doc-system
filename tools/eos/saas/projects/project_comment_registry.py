"""TITLE: WILSY OS Project Task Comment Authority and Audit Registry
VERSION: v1.1.0-NEWEST-FIRST-INDEXED-COMMENTS
AUTHORITY: Python EOS immutable project-task collaboration source.
EPITOME: One tenant/project/task-bound comment per command, explicit verified
         mentions, deterministic replay, indexed reads and immutable audit.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/projects/project_comment_registry.py
COLLABORATION / OWNERSHIP: Projects router owns authenticated IAM, entitled
         exact-project admission, task existence and current mentioned-member
         validation; this registry owns comments and their immutable event truth.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.1.0-NEWEST-FIRST-INDEXED-COMMENTS indexes
         exact task comments newest-first with deterministic tie-breaking,
         retaining the original index name for existing deployments.
         List pagination now returns the most recent source evidence first.
CHANGELOG: v1.0.0-EXACT-PROJECT-THREADED-COMMENTS establishes task-scoped
         append-only plain-text collaboration with source-backed audit/replay.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Bounded plain text, opaque mention principals,
         no inferred notifications/approval, HTML interpretation or IAM grants.
TENANT BOUNDARY: All read/write/replay/event coordinates include exact tenant,
         project and task scope; reserved alias tenants are refused.
AUTHORITY BOUNDARY: Persisted comments cannot grant permissions, authorize
         approvals, prove delivery, change tasks or create notifications.
TRANSACTION BOUNDARY: Caller-owned MongoDB session and majority transaction;
         index DDL is an EOS startup responsibility, not a request side effect.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes financial actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
from hmac import compare_digest
import json
import re
from typing import Any, Final

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

VERSION: Final[str] = "v1.1.0-NEWEST-FIRST-INDEXED-COMMENTS"
SCHEMA: Final[str] = "wilsy.project.comment.v1"
COLLECTION: Final[str] = "wilsy_project_comments"
EVENT_COLLECTION: Final[str] = "wilsy_project_comment_events"
_PROJECT_ID = re.compile(r"^prj-[a-f0-9]{48}$")
_TASK_ID = re.compile(r"^ptk-[a-f0-9]{48}$")
_COMMENT_ID = re.compile(r"^pcm-[a-f0-9]{48}$")
_DIGEST = re.compile(r"^[a-f0-9]{128}$")
_FORBIDDEN_TENANTS = frozenset({
    "MASTER", "GLOBAL_ROOT", "WILSY_ROOT", "WILSY_MASTER",
    "WILSY_GLOBAL_ROOT", "SOVEREIGN_ROOT",
})


class ProjectCommentError(RuntimeError):
    """Bounded, non-disclosing invalid comment/source error."""

    def __init__(self, code: str) -> None:
        """Carry one stable machine-readable error code."""
        super().__init__(code)
        self.code = code


class ProjectCommentConflict(ProjectCommentError):
    """Divergent idempotency, duplicate origin or comment evidence collision."""


class ProjectCommentNotFound(ProjectCommentError):
    """Foreign, absent and wrong-task comment identities are indistinguishable."""


def _identity(value: object, kind: str, maximum: int = 180) -> str:
    """Require an exact, bounded opaque identity without reserved root aliases."""
    if (
        not isinstance(value, str) or not 1 <= len(value) <= maximum
        or value != value.strip() or any(ord(char) <= 32 for char in value)
    ):
        raise ProjectCommentError("PROJECT_COMMENT_" + kind + "_INVALID")
    if kind == "TENANT" and value.upper() in _FORBIDDEN_TENANTS:
        raise ProjectCommentError("PROJECT_COMMENT_TENANT_INVALID")
    matcher = {"PROJECT": _PROJECT_ID, "TASK": _TASK_ID, "COMMENT": _COMMENT_ID}.get(kind)
    if matcher is not None and matcher.fullmatch(value) is None:
        raise ProjectCommentError("PROJECT_COMMENT_" + kind + "_INVALID")
    return value


def _body(value: object) -> str:
    """Bound descriptive plain text, rejecting empty and invisible controls."""
    if (
        not isinstance(value, str) or not 1 <= len(value) <= 5000
        or value != value.strip()
        or any(ord(char) < 32 and char not in "\n\t" for char in value)
    ):
        raise ProjectCommentError("PROJECT_COMMENT_BODY_INVALID")
    return value


def _time(value: object) -> datetime:
    """Normalize valid timezone-aware authoritative instants to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ProjectCommentError("PROJECT_COMMENT_TIME_INVALID")
    return value.astimezone(timezone.utc)


def _mentions(value: object, author: str) -> tuple[str, ...]:
    """Ensure explicit bounded unique principals, not parsed free-text names."""
    if not isinstance(value, tuple) or len(value) > 10:
        raise ProjectCommentError("PROJECT_COMMENT_MENTIONS_INVALID")
    for mentioned in value:
        _identity(mentioned, "MENTION")
    if len(set(value)) != len(value) or author in value:
        raise ProjectCommentError("PROJECT_COMMENT_MENTIONS_INVALID")
    return value


def _hash(value: dict[str, object]) -> str:
    """Hash canonical semantic evidence; this is not an institutional signature."""
    return sha3_512(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


def comment_id_for_command(
    tenant_id: str, project_id: str, task_id: str,
    author_principal_id: str, idempotency_key: str,
) -> str:
    """Derive stable source identity from exact coordinates and command key."""
    values = [
        _identity(tenant_id, "TENANT"), _identity(project_id, "PROJECT"),
        _identity(task_id, "TASK"), _identity(author_principal_id, "AUTHOR"),
        _identity(idempotency_key, "KEY", 200),
    ]
    return "pcm-" + sha3_512("\0".join(values).encode("utf-8")).hexdigest()[:48]


@dataclass(frozen=True, slots=True)
class ProjectComment:
    """Immutable task-scoped authored comment; never an approval or notification."""

    tenant_id: str
    project_id: str
    task_id: str
    comment_id: str
    author_principal_id: str
    body: str
    mentions: tuple[str, ...]
    created_at: datetime
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate complete source-owned coordinates and checksum on hydrate."""
        for name, value in (
            ("TENANT", self.tenant_id), ("PROJECT", self.project_id),
            ("TASK", self.task_id), ("COMMENT", self.comment_id),
            ("AUTHOR", self.author_principal_id),
        ):
            _identity(value, name)
        _body(self.body)
        _mentions(self.mentions, self.author_principal_id)
        instant = _time(self.created_at)
        object.__setattr__(self, "created_at", instant)
        digest = _hash(self._canonical())
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or _DIGEST.fullmatch(self.fingerprint) is None
            or not compare_digest(self.fingerprint, digest)
        ):
            raise ProjectCommentError("PROJECT_COMMENT_FINGERPRINT_INVALID")
        object.__setattr__(self, "fingerprint", digest)

    def _canonical(self) -> dict[str, object]:
        """Serialize only domain truth, excluding derived fingerprint."""
        return {
            "schema": SCHEMA, "tenant_id": self.tenant_id,
            "project_id": self.project_id, "task_id": self.task_id,
            "comment_id": self.comment_id,
            "author_principal_id": self.author_principal_id,
            "body": self.body, "mentions": list(self.mentions),
            "created_at": self.created_at.isoformat(),
        }

    def to_dict(self) -> dict[str, object]:
        """Return complete canonical source state and integrity fingerprint."""
        return {**self._canonical(), "fingerprint": self.fingerprint}

    @classmethod
    def hydrate(cls, source: dict[str, object]) -> ProjectComment:
        """Reject modified, missing or extra persisted fields."""
        expected = {
            "schema", "tenant_id", "project_id", "task_id", "comment_id",
            "author_principal_id", "body", "mentions", "created_at", "fingerprint",
        }
        if not isinstance(source, dict) or set(source) != expected or source.get("schema") != SCHEMA:
            raise ProjectCommentError("PROJECT_COMMENT_RECORD_INVALID")
        try:
            raw_time = source["created_at"]
            if isinstance(raw_time, str):
                instant = datetime.fromisoformat(raw_time)
            elif isinstance(raw_time, datetime):
                instant = raw_time.replace(tzinfo=timezone.utc) if raw_time.tzinfo is None else raw_time
            else:
                raise ProjectCommentError("PROJECT_COMMENT_TIME_INVALID")
            mentions = source["mentions"]
            if not isinstance(mentions, (tuple, list)):
                raise ProjectCommentError("PROJECT_COMMENT_MENTIONS_INVALID")
            return cls(
                tenant_id=source["tenant_id"], project_id=source["project_id"],
                task_id=source["task_id"], comment_id=source["comment_id"],
                author_principal_id=source["author_principal_id"], body=source["body"],
                mentions=tuple(mentions), created_at=instant,
                fingerprint=source["fingerprint"],
            )
        except (TypeError, ValueError) as error:
            raise ProjectCommentError("PROJECT_COMMENT_RECORD_INVALID") from error


class ProjectCommentRegistry:
    """Append-only project comments with exact-tenant audit and replay semantics.

    The caller must independently authorize current IAM, exact project
    participation, referenced task and each mentioned participant.
    """

    def __init__(self, comments: Any, events: Any) -> None:
        """Adopt supplied Mongo collections without creating a client/session."""
        if comments is None or events is None:
            raise ProjectCommentError("PROJECT_COMMENT_COLLECTIONS_REQUIRED")
        self._comments = comments
        self._events = events

    @staticmethod
    def ensure_indexes(comments: Any, events: Any) -> None:
        """Index exact comment identities, task timeline and immutable replay."""
        try:
            comments.create_index([
                ("tenant_id", ASCENDING), ("project_id", ASCENDING),
                ("task_id", ASCENDING), ("comment_id", ASCENDING),
            ], unique=True, name="wilsy_project_comment_identity_unique")
            comments.create_index([
                ("tenant_id", ASCENDING), ("project_id", ASCENDING),
                ("task_id", ASCENDING), ("created_at", ASCENDING),
                ("comment_id", ASCENDING),
            ], name="wilsy_project_task_comment_timeline")
            comments.create_index([
                ("tenant_id", ASCENDING), ("project_id", ASCENDING),
                ("task_id", ASCENDING), ("created_at", DESCENDING),
                ("comment_id", DESCENDING),
            ], name="wilsy_project_task_comment_recent_v2")
            events.create_index([
                ("tenant_id", ASCENDING), ("idempotency_key", ASCENDING),
            ], unique=True, name="wilsy_project_comment_replay_unique")
        except PyMongoError as error:
            raise ProjectCommentError("PROJECT_COMMENT_INDEX_UNAVAILABLE") from error

    def list_page(
        self, *, tenant_id: str, project_id: str, task_id: str,
        session: Any, offset: int = 0, limit: int = 50,
    ) -> tuple[tuple[ProjectComment, ...], bool]:
        """Return one bounded exact-project and exact-task comment page."""
        if session is None:
            raise ProjectCommentError("PROJECT_COMMENT_SESSION_REQUIRED")
        if (
            type(limit) is not int or not 1 <= limit <= 100
            or type(offset) is not int or offset < 0
        ):
            raise ProjectCommentError("PROJECT_COMMENT_PAGE_INVALID")
        query = {
            "tenant_id": _identity(tenant_id, "TENANT"),
            "project_id": _identity(project_id, "PROJECT"),
            "task_id": _identity(task_id, "TASK"),
        }
        try:
            rows = tuple(ProjectComment.hydrate({
                k: v for k, v in row.items() if k != "_id"
            }) for row in self._comments.find(query, session=session).sort([
                ("created_at", DESCENDING), ("comment_id", DESCENDING),
            ]).skip(offset).limit(limit + 1))
        except PyMongoError as error:
            raise ProjectCommentError("PROJECT_COMMENT_READ_UNAVAILABLE") from error
        return rows[:limit], len(rows) > limit

    def create_or_replay(
        self, *, comment: ProjectComment, actor_principal_id: str,
        idempotency_key: str, session: Any,
    ) -> ProjectComment:
        """Append and audit a comment in one caller-owned MongoDB transaction."""
        if session is None:
            raise ProjectCommentError("PROJECT_COMMENT_SESSION_REQUIRED")
        actor = _identity(actor_principal_id, "ACTOR")
        key = _identity(idempotency_key, "KEY", 200)
        if (
            actor != comment.author_principal_id
            or comment.comment_id != comment_id_for_command(
                comment.tenant_id, comment.project_id, comment.task_id, actor, key,
            )
        ):
            raise ProjectCommentConflict("PROJECT_COMMENT_ORIGIN_INVALID")
        digest = _hash({
            "command": "CREATE", "tenant_id": comment.tenant_id,
            "project_id": comment.project_id, "task_id": comment.task_id,
            "actor": actor, "body": comment.body,
            "mentions": list(comment.mentions),
        })
        try:
            original = self._events.find_one({
                "tenant_id": comment.tenant_id, "idempotency_key": key,
            }, session=session)
        except PyMongoError as error:
            raise ProjectCommentError("PROJECT_COMMENT_REPLAY_UNAVAILABLE") from error
        if original is not None:
            if original.get("request_digest") != digest:
                raise ProjectCommentConflict("PROJECT_COMMENT_DIVERGENT_REPLAY")
            snapshot = original.get("result_snapshot")
            if not isinstance(snapshot, dict):
                raise ProjectCommentError("PROJECT_COMMENT_EVENT_INVALID")
            previous = ProjectComment.hydrate(snapshot)
            if (
                previous.tenant_id != comment.tenant_id
                or previous.project_id != comment.project_id
                or previous.task_id != comment.task_id
                or previous.comment_id != original.get("comment_id")
                or previous.fingerprint != original.get("result_fingerprint")
                or original.get("schema") != "wilsy.project.comment.event.v1"
                or original.get("event_type") != "PROJECT_COMMENT_CREATED"
            ):
                raise ProjectCommentError("PROJECT_COMMENT_EVENT_INVALID")
            return previous
        try:
            self._comments.insert_one(comment.to_dict(), session=session)
            self._events.insert_one({
                "schema": "wilsy.project.comment.event.v1",
                "tenant_id": comment.tenant_id,
                "project_id": comment.project_id,
                "task_id": comment.task_id,
                "comment_id": comment.comment_id,
                "event_type": "PROJECT_COMMENT_CREATED",
                "actor_principal_id": actor,
                "idempotency_key": key,
                "request_digest": digest,
                "result_fingerprint": comment.fingerprint,
                "result_snapshot": comment.to_dict(),
                "occurred_at": comment.created_at,
            }, session=session)
        except DuplicateKeyError as error:
            raise ProjectCommentConflict("PROJECT_COMMENT_CONFLICT") from error
        except PyMongoError as error:
            raise ProjectCommentError("PROJECT_COMMENT_WRITE_UNAVAILABLE") from error
        return comment


__all__ = [
    "SCHEMA", "VERSION", "COLLECTION", "EVENT_COLLECTION",
    "ProjectComment", "ProjectCommentRegistry", "ProjectCommentError",
    "ProjectCommentConflict", "ProjectCommentNotFound", "comment_id_for_command",
]

# ARTIFACT: project_comment_registry.py
# VERSION: v1.1.0-NEWEST-FIRST-INDEXED-COMMENTS
# AUTHORITY BOUNDARY: immutable text/evidence only, no notification or approval
# TENANT POSTURE: all reads, writes and replay bind exact tenant/project/task
# FAIL-CLOSED POSTURE: malformed scope, mentions, tamper and divergent replay deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
