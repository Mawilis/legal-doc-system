"""TITLE: WILSY OS Project Attachment Malware Clearance Evidence Registry
VERSION: v1.0.0-PINNED-SCAN-EVIDENCE-CLEARANCE
AUTHORITY: Python EOS Projects exact-task malware scan observation ledger.
EPITOME: Persist one immutable, source-bound clean scanner observation after
         server-verified GuardDuty object/version/tag and pinned bucket policy.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/projects/project_attachment_clearance_registry.py
COLLABORATION / OWNERSHIP: Projects router owns current participant IAM and
         exact task/manifest gate; storage adapter verifies S3/GuardDuty;
         clearance registry owns internal audited observation truth.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-PINNED-SCAN-EVIDENCE-CLEARANCE binds independent scan result
         to immutable manifest SHA3-512 and policy pin with durable replay.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Scan status is observed, not a legal authenticity
         guarantee, electronic signature or proof against later advisories.
TENANT BOUNDARY: Every receipt, lookup and replay binds tenant/project/task.
AUTHORITY BOUNDARY: Not a download, signature, task completion or finance grant.
TRANSACTION BOUNDARY: Caller owns majority snapshot and source reauthorization.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
from hmac import compare_digest
import json
import re
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

VERSION: Final[str] = "v1.0.0-PINNED-SCAN-EVIDENCE-CLEARANCE"
SCHEMA: Final[str] = "wilsy.project.attachment.clearance.v1"
COLLECTION: Final[str] = "wilsy_project_attachment_clearances"
EVENT_COLLECTION: Final[str] = "wilsy_project_attachment_clearance_events"
_PATTERN = {
    "PROJECT": re.compile(r"^prj-[a-f0-9]{48}$"),
    "TASK": re.compile(r"^ptk-[a-f0-9]{48}$"),
    "ATTACHMENT": re.compile(r"^pat-[a-f0-9]{48}$"),
    "DIGEST": re.compile(r"^[a-f0-9]{128}$"),
}
_RESERVED = frozenset({
    "ROOT", "DEFAULT", "MASTER", "GLOBAL_ROOT",
    "WILSY_ROOT", "WILSY_MASTER", "WILSY_GLOBAL_ROOT",
})


class ProjectAttachmentClearanceError(RuntimeError):
    """Stable non-disclosing scanner evidence persistence error."""

    def __init__(self, code: str) -> None:
        """Expose a bounded source failure code without provider details."""
        self.code = code
        super().__init__(code)


class ProjectAttachmentClearanceNotFound(ProjectAttachmentClearanceError):
    """Missing or foreign scan evidence is indistinguishable."""


class ProjectAttachmentClearanceConflict(ProjectAttachmentClearanceError):
    """Distinct scan evidence cannot silently replace original clearance."""


def _identity(value: object, kind: str, limit: int = 180) -> str:
    """Validate bounded opaque tenant, task and SHA3-512 coordinates."""
    if (
        not isinstance(value, str) or not 1 <= len(value) <= limit
        or value != value.strip() or any(ord(char) <= 32 for char in value)
    ):
        raise ProjectAttachmentClearanceError(
            "PROJECT_ATTACHMENT_CLEARANCE_" + kind + "_INVALID",
        )
    if kind == "TENANT" and value.upper() in _RESERVED:
        raise ProjectAttachmentClearanceError("PROJECT_ATTACHMENT_CLEARANCE_TENANT_INVALID")
    pattern = _PATTERN.get(kind)
    if pattern is not None and pattern.fullmatch(value) is None:
        raise ProjectAttachmentClearanceError(
            "PROJECT_ATTACHMENT_CLEARANCE_" + kind + "_INVALID",
        )
    return value


def _time(value: object, *, bson: bool = False) -> datetime:
    """Normalize an EOS observation instant, not a scanner-issued timestamp."""
    if isinstance(value, str) and bson:
        try:
            value = datetime.fromisoformat(value)
        except ValueError as error:
            raise ProjectAttachmentClearanceError("PROJECT_ATTACHMENT_CLEARANCE_TIME_INVALID") from error
    if not isinstance(value, datetime):
        raise ProjectAttachmentClearanceError("PROJECT_ATTACHMENT_CLEARANCE_TIME_INVALID")
    if value.tzinfo is None:
        if not bson:
            raise ProjectAttachmentClearanceError("PROJECT_ATTACHMENT_CLEARANCE_TIME_INVALID")
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _hash(data: dict[str, object]) -> str:
    """Fingerprint semantic scanner observation; not a digital signature."""
    return sha3_512(json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ProjectAttachmentClearance:
    """Immutable GuardDuty clean observation bound to exact original file."""

    tenant_id: str
    project_id: str
    task_id: str
    attachment_id: str
    attachment_fingerprint: str
    policy_sha3_512: str
    scan_evidence_sha3_512: str
    observed_by_principal_id: str
    observed_at: datetime
    scan_status: str = "NO_THREATS_FOUND"
    revision: int = 1
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Never construct clearance from an unverified or ambiguous status."""
        for kind, value in (
            ("TENANT", self.tenant_id), ("PROJECT", self.project_id),
            ("TASK", self.task_id), ("ATTACHMENT", self.attachment_id),
            ("DIGEST", self.attachment_fingerprint),
            ("DIGEST", self.policy_sha3_512),
            ("DIGEST", self.scan_evidence_sha3_512),
            ("OBSERVER", self.observed_by_principal_id),
        ):
            _identity(value, kind)
        if self.scan_status != "NO_THREATS_FOUND" or self.revision != 1:
            raise ProjectAttachmentClearanceError("PROJECT_ATTACHMENT_CLEARANCE_NOT_CLEAN")
        object.__setattr__(self, "observed_at", _time(self.observed_at))
        digest = _hash(self._canonical())
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or _PATTERN["DIGEST"].fullmatch(self.fingerprint) is None
            or not compare_digest(self.fingerprint, digest)
        ):
            raise ProjectAttachmentClearanceError("PROJECT_ATTACHMENT_CLEARANCE_FINGERPRINT_INVALID")
        object.__setattr__(self, "fingerprint", digest)

    def _canonical(self) -> dict[str, object]:
        """Encode immutable scan evidence with no storage/provider location."""
        return {
            "schema": SCHEMA, "tenant_id": self.tenant_id,
            "project_id": self.project_id, "task_id": self.task_id,
            "attachment_id": self.attachment_id,
            "attachment_fingerprint": self.attachment_fingerprint,
            "policy_sha3_512": self.policy_sha3_512,
            "scan_evidence_sha3_512": self.scan_evidence_sha3_512,
            "observed_by_principal_id": self.observed_by_principal_id,
            "observed_at": self.observed_at.isoformat(),
            "scan_status": self.scan_status, "revision": self.revision,
        }

    def to_dict(self) -> dict[str, object]:
        """Return complete canonical scan observation for an authorized caller."""
        return {**self._canonical(), "fingerprint": self.fingerprint}

    @classmethod
    def hydrate(cls, row: dict[str, object]) -> ProjectAttachmentClearance:
        """Verify strict persisted fields, timestamp and semantic digest."""
        required = {
            "schema", "tenant_id", "project_id", "task_id", "attachment_id",
            "attachment_fingerprint", "policy_sha3_512",
            "scan_evidence_sha3_512", "observed_by_principal_id",
            "observed_at", "scan_status", "revision", "fingerprint",
        }
        if not isinstance(row, dict) or set(row) != required or row["schema"] != SCHEMA:
            raise ProjectAttachmentClearanceError("PROJECT_ATTACHMENT_CLEARANCE_RECORD_INVALID")
        values = {key: value for key, value in row.items() if key != "schema"}
        values["observed_at"] = _time(values["observed_at"], bson=True)
        try:
            return cls(**values)
        except TypeError as error:
            raise ProjectAttachmentClearanceError(
                "PROJECT_ATTACHMENT_CLEARANCE_RECORD_INVALID",
            ) from error


class ProjectAttachmentClearanceRegistry:
    """Persist once-only scanner observations and immutable command evidence."""

    def __init__(self, current: Any, events: Any) -> None:
        """Adopt indexes/sessions from EOS caller; do not create authority."""
        if current is None or events is None:
            raise ProjectAttachmentClearanceError("PROJECT_ATTACHMENT_CLEARANCE_COLLECTIONS_REQUIRED")
        self._current = current
        self._events = events

    @staticmethod
    def ensure_indexes(current: Any, events: Any) -> None:
        """Require one cleared exact-task attachment and durable replay origin."""
        try:
            current.create_index([
                ("tenant_id", ASCENDING), ("project_id", ASCENDING),
                ("task_id", ASCENDING), ("attachment_id", ASCENDING),
            ], unique=True, name="wilsy_project_attachment_clearance_unique")
            events.create_index([
                ("tenant_id", ASCENDING), ("actor_principal_id", ASCENDING),
                ("idempotency_key", ASCENDING),
            ], unique=True, name="wilsy_project_attachment_clearance_replay")
        except PyMongoError as error:
            raise ProjectAttachmentClearanceError(
                "PROJECT_ATTACHMENT_CLEARANCE_INDEX_UNAVAILABLE",
            ) from error

    def get(
        self, *, tenant_id: str, project_id: str, task_id: str,
        attachment_id: str, session: Any,
    ) -> ProjectAttachmentClearance:
        """Return exact task clearance; absent and foreign records are identical."""
        if session is None:
            raise ProjectAttachmentClearanceError("PROJECT_ATTACHMENT_CLEARANCE_SESSION_REQUIRED")
        query = {
            "tenant_id": _identity(tenant_id, "TENANT"),
            "project_id": _identity(project_id, "PROJECT"),
            "task_id": _identity(task_id, "TASK"),
            "attachment_id": _identity(attachment_id, "ATTACHMENT"),
        }
        try:
            row = self._current.find_one(query, session=session)
        except PyMongoError as error:
            raise ProjectAttachmentClearanceError(
                "PROJECT_ATTACHMENT_CLEARANCE_SOURCE_UNAVAILABLE",
            ) from error
        if row is None:
            raise ProjectAttachmentClearanceNotFound("PROJECT_ATTACHMENT_CLEARANCE_NOT_FOUND")
        return ProjectAttachmentClearance.hydrate({
            key: value for key, value in row.items() if key != "_id"
        })

    def record_or_replay(
        self, *, clearance: ProjectAttachmentClearance,
        idempotency_key: str, session: Any,
    ) -> ProjectAttachmentClearance:
        """Record external clean observation once; caller verifies S3 tag first."""
        if session is None:
            raise ProjectAttachmentClearanceError("PROJECT_ATTACHMENT_CLEARANCE_SESSION_REQUIRED")
        key = _identity(idempotency_key, "KEY", 200)
        command_digest = _hash({
            key: value for key, value in clearance._canonical().items()
            if key != "observed_at"
        })
        query = {
            "tenant_id": clearance.tenant_id,
            "actor_principal_id": clearance.observed_by_principal_id,
            "idempotency_key": key,
        }
        try:
            event = self._events.find_one(query, session=session)
            if event is not None:
                if event.get("request_fingerprint") != command_digest:
                    raise ProjectAttachmentClearanceConflict(
                        "PROJECT_ATTACHMENT_CLEARANCE_DIVERGENT_REPLAY",
                    )
                snapshot = event.get("result_snapshot")
                if not isinstance(snapshot, dict):
                    raise ProjectAttachmentClearanceError(
                        "PROJECT_ATTACHMENT_CLEARANCE_EVENT_INVALID",
                    )
                original = ProjectAttachmentClearance.hydrate(snapshot)
                if (
                    event.get("result_fingerprint") != original.fingerprint
                    or event.get("attachment_id") != original.attachment_id
                    or original.attachment_id != clearance.attachment_id
                ):
                    raise ProjectAttachmentClearanceError(
                        "PROJECT_ATTACHMENT_CLEARANCE_EVENT_INVALID",
                    )
                return original
            self._current.insert_one(clearance.to_dict(), session=session)
            self._events.insert_one({
                "schema": "wilsy.project.attachment.clearance.event.v1",
                **query, "project_id": clearance.project_id,
                "task_id": clearance.task_id,
                "attachment_id": clearance.attachment_id,
                "request_fingerprint": command_digest,
                "result_fingerprint": clearance.fingerprint,
                "result_snapshot": clearance.to_dict(),
                "event_type": "PROJECT_ATTACHMENT_SCAN_CLEAN_OBSERVED",
                "occurred_at": clearance.observed_at,
            }, session=session)
        except DuplicateKeyError as error:
            raise ProjectAttachmentClearanceConflict(
                "PROJECT_ATTACHMENT_CLEARANCE_DUPLICATE",
            ) from error
        except PyMongoError as error:
            raise ProjectAttachmentClearanceError(
                "PROJECT_ATTACHMENT_CLEARANCE_WRITE_UNAVAILABLE",
            ) from error
        return clearance


__all__ = [
    "VERSION", "SCHEMA", "COLLECTION", "EVENT_COLLECTION",
    "ProjectAttachmentClearance", "ProjectAttachmentClearanceRegistry",
    "ProjectAttachmentClearanceError", "ProjectAttachmentClearanceConflict",
    "ProjectAttachmentClearanceNotFound",
]

# ARTIFACT: project_attachment_clearance_registry.py
# VERSION: v1.0.0-PINNED-SCAN-EVIDENCE-CLEARANCE
# AUTHORITY BOUNDARY: immutable observed clean tag, not signature/finance
# TENANT POSTURE: exact task/attachment and SHA3 object evidence scope
# FAIL-CLOSED POSTURE: unknown, untrusted, foreign, tampered, nonclean deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
