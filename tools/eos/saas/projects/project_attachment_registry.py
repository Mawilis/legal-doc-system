"""TITLE: WILSY OS Governed Project Attachment Manifest Registry
VERSION: v1.0.0-QUARANTINED-TASK-EVIDENCE-MANIFEST
AUTHORITY: Python EOS Projects canonical task-bound file evidence metadata.
EPITOME: Persist a verified content digest, expected size, opaque storage
         receipt, immutable command origin and audit without exposing file
         bytes or promoting unscanned material to approval evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/projects/project_attachment_registry.py
COLLABORATION / OWNERSHIP: Projects router must authorize the exact tenant,
         project and task; verified provider storage/virus-scanning adapters
         own byte evidence and malware verdict. Registry owns immutable metadata.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-QUARANTINED-TASK-EVIDENCE-MANIFEST introduces exact-task,
         replay-safe quarantine manifests. AVAILABLE release is explicitly
         NOT implemented; absence of scanning cannot be interpreted as safe.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: SHA3-512 content identity; no raw bytes, untrusted
         URLs, browser-provided provider receipts, executable preview or download.
TENANT BOUNDARY: Every manifest and command event uses tenant/project/task,
         with deterministic creation ID and no cross-tenant existence leaks.
AUTHORITY BOUNDARY: Storage receipt is observational; it never grants read,
         retention, legal-hold, trust, scanning, signing or approval authority.
TRANSACTION BOUNDARY: Caller owns one MongoDB snapshot/majority transaction.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes finances.
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

VERSION: Final[str] = "v1.0.0-QUARANTINED-TASK-EVIDENCE-MANIFEST"
SCHEMA: Final[str] = "wilsy.project.attachment.v1"
COLLECTION: Final[str] = "wilsy_project_attachments"
EVENT_COLLECTION: Final[str] = "wilsy_project_attachment_events"
MAX_ATTACHMENT_BYTES: Final[int] = 20 * 1024 * 1024
_MEDIA: Final[frozenset[str]] = frozenset({
    "application/pdf", "image/png", "image/jpeg",
})
_PATTERN = {
    "PROJECT": re.compile(r"^prj-[a-f0-9]{48}$"),
    "TASK": re.compile(r"^ptk-[a-f0-9]{48}$"),
    "ATTACHMENT": re.compile(r"^pat-[a-f0-9]{48}$"),
    "DIGEST": re.compile(r"^[a-f0-9]{128}$"),
}
_RESERVED = frozenset({
    "MASTER", "GLOBAL_ROOT", "WILSY_ROOT", "WILSY_MASTER",
    "WILSY_GLOBAL_ROOT", "SOVEREIGN_ROOT", "ROOT", "DEFAULT",
})


class ProjectAttachmentError(RuntimeError):
    """Stable non-disclosing storage manifest error."""

    def __init__(self, code: str) -> None:
        """Report one stable bounded failure code."""
        self.code = code
        super().__init__(code)


class ProjectAttachmentConflict(ProjectAttachmentError):
    """Divergent idempotency replay or colliding immutable source identity."""


class ProjectAttachmentNotFound(ProjectAttachmentError):
    """Exact task-bound source does not exist in caller's authorized scope."""


def _identity(value: object, kind: str, limit: int = 180) -> str:
    """Check bounded opaque coordinates and forbid legacy root fallbacks."""
    if (
        not isinstance(value, str) or not 1 <= len(value) <= limit
        or value != value.strip() or any(ord(char) <= 32 for char in value)
    ):
        raise ProjectAttachmentError("PROJECT_ATTACHMENT_" + kind + "_INVALID")
    if kind == "TENANT" and value.upper() in _RESERVED:
        raise ProjectAttachmentError("PROJECT_ATTACHMENT_TENANT_INVALID")
    pattern = _PATTERN.get(kind)
    if pattern is not None and pattern.fullmatch(value) is None:
        raise ProjectAttachmentError("PROJECT_ATTACHMENT_" + kind + "_INVALID")
    return value


def _text(value: object, kind: str, limit: int) -> str:
    """Validate bounded plain text without path segments or control bytes."""
    if (
        not isinstance(value, str) or not 1 <= len(value) <= limit
        or value != value.strip()
        or any(ord(char) < 32 or char in "/\\" for char in value)
    ):
        raise ProjectAttachmentError("PROJECT_ATTACHMENT_" + kind + "_INVALID")
    return value


def _instant(value: object, *, from_bson: bool = False) -> datetime:
    """Normalize aware timestamps; only BSON hydration may supply naive UTC."""
    if isinstance(value, str) and from_bson:
        try:
            value = datetime.fromisoformat(value)
        except ValueError as error:
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_TIME_INVALID") from error
    if not isinstance(value, datetime):
        raise ProjectAttachmentError("PROJECT_ATTACHMENT_TIME_INVALID")
    if value.tzinfo is None:
        if not from_bson:
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_TIME_INVALID")
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _hash(value: dict[str, object]) -> str:
    """Return semantic SHA3-512, not a signature or scanner attestation."""
    return sha3_512(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


def attachment_id_for_command(
    tenant_id: str, project_id: str, task_id: str,
    uploader_principal_id: str, idempotency_key: str,
) -> str:
    """Bind generated file identity to exact authenticated command origin."""
    components = (
        _identity(tenant_id, "TENANT"),
        _identity(project_id, "PROJECT"),
        _identity(task_id, "TASK"),
        _identity(uploader_principal_id, "UPLOADER"),
        _identity(idempotency_key, "KEY", 200),
    )
    return "pat-" + sha3_512("\0".join(components).encode()).hexdigest()[:48]


@dataclass(frozen=True, slots=True)
class ProjectAttachment:
    """Immutable QUARANTINED file receipt, not usable approval evidence."""

    tenant_id: str
    project_id: str
    task_id: str
    attachment_id: str
    uploader_principal_id: str
    filename: str
    media_type: str
    size_bytes: int
    content_sha3_512: str
    storage_receipt: str
    created_at: datetime
    state: str = "QUARANTINED"
    revision: int = 1
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Reject forged receipts, unsafe media and invented scan readiness."""
        for kind, value in (
            ("TENANT", self.tenant_id), ("PROJECT", self.project_id),
            ("TASK", self.task_id), ("ATTACHMENT", self.attachment_id),
            ("UPLOADER", self.uploader_principal_id),
        ):
            _identity(value, kind)
        _text(self.filename, "FILENAME", 255)
        if (
            self.filename in (".", "..")
            or self.filename.startswith(".")
            or self.media_type not in _MEDIA
            or type(self.size_bytes) is not int
            or not 1 <= self.size_bytes <= MAX_ATTACHMENT_BYTES
        ):
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_CONTENT_INVALID")
        _identity(self.content_sha3_512, "DIGEST")
        _text(self.storage_receipt, "STORAGE_RECEIPT", 200)
        if self.state != "QUARANTINED" or self.revision != 1:
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_UNVERIFIED_RELEASE_DENIED")
        object.__setattr__(self, "created_at", _instant(self.created_at))
        digest = _hash(self._canonical())
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or _PATTERN["DIGEST"].fullmatch(self.fingerprint) is None
            or not compare_digest(self.fingerprint, digest)
        ):
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_FINGERPRINT_INVALID")
        object.__setattr__(self, "fingerprint", digest)

    def _canonical(self) -> dict[str, object]:
        """Serialize complete semantic state with no provider credentials."""
        return {
            "schema": SCHEMA, "tenant_id": self.tenant_id,
            "project_id": self.project_id, "task_id": self.task_id,
            "attachment_id": self.attachment_id,
            "uploader_principal_id": self.uploader_principal_id,
            "filename": self.filename, "media_type": self.media_type,
            "size_bytes": self.size_bytes,
            "content_sha3_512": self.content_sha3_512,
            "storage_receipt": self.storage_receipt,
            "created_at": self.created_at.isoformat(),
            "state": self.state, "revision": self.revision,
        }

    def to_dict(self) -> dict[str, object]:
        """Return a complete source record and integrity digest."""
        return {**self._canonical(), "fingerprint": self.fingerprint}

    @classmethod
    def hydrate(cls, raw: dict[str, object]) -> ProjectAttachment:
        """Fail closed on malformed or foreign persisted source fields."""
        expected = {
            "schema", "tenant_id", "project_id", "task_id", "attachment_id",
            "uploader_principal_id", "filename", "media_type", "size_bytes",
            "content_sha3_512", "storage_receipt", "created_at", "state",
            "revision", "fingerprint",
        }
        if not isinstance(raw, dict) or set(raw) != expected or raw["schema"] != SCHEMA:
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_RECORD_INVALID")
        args = {key: value for key, value in raw.items() if key != "schema"}
        args["created_at"] = _instant(args["created_at"], from_bson=True)
        try:
            return cls(**args)
        except TypeError as error:
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_RECORD_INVALID") from error


class ProjectAttachmentRegistry:
    """Caller-transaction-bound quarantined manifests and immutable events."""

    def __init__(self, attachments: Any, events: Any) -> None:
        """Adopt preconfigured collections; never create sessions or indexes."""
        if attachments is None or events is None:
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_COLLECTIONS_REQUIRED")
        self._attachments = attachments
        self._events = events

    @staticmethod
    def ensure_indexes(attachments: Any, events: Any) -> None:
        """Create scoped uniqueness, task listing and command-event indexes."""
        try:
            attachments.create_index([
                ("tenant_id", ASCENDING), ("project_id", ASCENDING),
                ("task_id", ASCENDING), ("attachment_id", ASCENDING),
            ], unique=True, name="wilsy_project_attachment_identity")
            attachments.create_index([
                ("tenant_id", ASCENDING), ("project_id", ASCENDING),
                ("task_id", ASCENDING), ("created_at", DESCENDING),
                ("attachment_id", ASCENDING),
            ], name="wilsy_project_attachment_task_timeline")
            events.create_index([
                ("tenant_id", ASCENDING), ("actor_principal_id", ASCENDING),
                ("idempotency_key", ASCENDING),
            ], unique=True, name="wilsy_project_attachment_command")
        except PyMongoError as error:
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_INDEX_UNAVAILABLE") from error

    def get(
        self, *, tenant_id: str, project_id: str, task_id: str,
        attachment_id: str, session: Any,
    ) -> ProjectAttachment:
        """Get exact tenant/task manifest; foreign is identical to missing."""
        if session is None:
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_SESSION_REQUIRED")
        query = {
            "tenant_id": _identity(tenant_id, "TENANT"),
            "project_id": _identity(project_id, "PROJECT"),
            "task_id": _identity(task_id, "TASK"),
            "attachment_id": _identity(attachment_id, "ATTACHMENT"),
        }
        try:
            row = self._attachments.find_one(query, session=session)
        except PyMongoError as error:
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_READ_UNAVAILABLE") from error
        if row is None:
            raise ProjectAttachmentNotFound("PROJECT_ATTACHMENT_NOT_FOUND")
        return ProjectAttachment.hydrate({
            key: value for key, value in row.items() if key != "_id"
        })

    def list_page(
        self, *, tenant_id: str, project_id: str, task_id: str,
        session: Any, limit: int = 50, offset: int = 0,
    ) -> tuple[tuple[ProjectAttachment, ...], bool]:
        """List a bounded task evidence timeline without revealing provider data."""
        if session is None:
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_SESSION_REQUIRED")
        if (
            type(limit) is not int or not 1 <= limit <= 100
            or type(offset) is not int or offset < 0
        ):
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_PAGE_INVALID")
        query = {
            "tenant_id": _identity(tenant_id, "TENANT"),
            "project_id": _identity(project_id, "PROJECT"),
            "task_id": _identity(task_id, "TASK"),
        }
        try:
            records = tuple(ProjectAttachment.hydrate({
                key: value for key, value in item.items() if key != "_id"
            }) for item in self._attachments.find(
                query, session=session,
            ).sort([
                ("created_at", DESCENDING), ("attachment_id", ASCENDING),
            ]).skip(offset).limit(limit + 1))
        except PyMongoError as error:
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_READ_UNAVAILABLE") from error
        return records[:limit], len(records) > limit

    def create_or_replay(
        self, *, attachment: ProjectAttachment,
        idempotency_key: str, session: Any,
    ) -> ProjectAttachment:
        """Write a quarantined manifest only after trusted provider verification.

        The caller must verify the provider receipt, streamed digest and exact
        object/version independently before this method is invoked. This
        registry never claims the receipt itself proves the object exists.
        """
        if session is None:
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_SESSION_REQUIRED")
        key = _identity(idempotency_key, "KEY", 200)
        if attachment.attachment_id != attachment_id_for_command(
            attachment.tenant_id, attachment.project_id,
            attachment.task_id, attachment.uploader_principal_id, key,
        ):
            raise ProjectAttachmentConflict("PROJECT_ATTACHMENT_ORIGIN_INVALID")
        command = _hash({
            "command": "REGISTER_QUARANTINE", **{
                k: v for k, v in attachment._canonical().items()
                if k not in ("created_at", "storage_receipt", "attachment_id")
            },
        })
        query = {
            "tenant_id": attachment.tenant_id,
            "actor_principal_id": attachment.uploader_principal_id,
            "idempotency_key": key,
        }
        try:
            event = self._events.find_one(query, session=session)
            if event is not None:
                if event.get("request_fingerprint") != command:
                    raise ProjectAttachmentConflict("PROJECT_ATTACHMENT_DIVERGENT_REPLAY")
                snapshot = event.get("result_snapshot")
                if not isinstance(snapshot, dict):
                    raise ProjectAttachmentError("PROJECT_ATTACHMENT_EVENT_INVALID")
                original = ProjectAttachment.hydrate(snapshot)
                if (
                    event.get("result_fingerprint") != original.fingerprint
                    or event.get("attachment_id") != original.attachment_id
                    or event.get("project_id") != original.project_id
                    or event.get("task_id") != original.task_id
                    or original.attachment_id != attachment.attachment_id
                ):
                    raise ProjectAttachmentError("PROJECT_ATTACHMENT_EVENT_INVALID")
                return original
            self._attachments.insert_one(attachment.to_dict(), session=session)
            self._events.insert_one({
                "schema": "wilsy.project.attachment.event.v1",
                **query, "project_id": attachment.project_id,
                "task_id": attachment.task_id,
                "attachment_id": attachment.attachment_id,
                "request_fingerprint": command,
                "result_fingerprint": attachment.fingerprint,
                "result_snapshot": attachment.to_dict(),
                "event_type": "PROJECT_ATTACHMENT_QUARANTINED",
                "occurred_at": attachment.created_at,
            }, session=session)
        except DuplicateKeyError as error:
            raise ProjectAttachmentConflict("PROJECT_ATTACHMENT_DUPLICATE") from error
        except PyMongoError as error:
            raise ProjectAttachmentError("PROJECT_ATTACHMENT_WRITE_UNAVAILABLE") from error
        return attachment


__all__ = [
    "VERSION", "SCHEMA", "COLLECTION", "EVENT_COLLECTION",
    "MAX_ATTACHMENT_BYTES", "ProjectAttachment", "ProjectAttachmentRegistry",
    "ProjectAttachmentError", "ProjectAttachmentNotFound",
    "ProjectAttachmentConflict", "attachment_id_for_command",
]

# ARTIFACT: project_attachment_registry.py
# VERSION: v1.0.0-QUARANTINED-TASK-EVIDENCE-MANIFEST
# AUTHORITY BOUNDARY: quarantined manifests only; not safe attachment evidence
# TENANT POSTURE: exact tenant/project/task/uploader and durable command origin
# FAIL-CLOSED POSTURE: unscanned, forged, oversized, malformed, foreign denied
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
