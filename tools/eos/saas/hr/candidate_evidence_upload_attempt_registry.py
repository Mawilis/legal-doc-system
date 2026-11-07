"""Durable, revision-guarded upload-attempt state for HR evidence ingestion.

This registry records provider multipart progress and uncertainty. It never
claims that an object is authoritative; custody metadata is registered only
after provider inspection and a separate caller-owned transaction.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import re
from typing import Any, Mapping

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

COLLECTION = "wilsy_hr_candidate_evidence_upload_attempts"
EVENT_COLLECTION = "wilsy_hr_candidate_evidence_upload_attempt_events"
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")


class UploadAttemptError(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class UploadAttemptConflict(UploadAttemptError):
    pass


class UploadAttemptStatus(str, Enum):
    INITIATING = "INITIATING"
    INITIATED = "INITIATED"
    PARTS_UPLOADED = "PARTS_UPLOADED"
    COMPLETION_UNCERTAIN = "COMPLETION_UNCERTAIN"
    PROVIDER_VERIFIED = "PROVIDER_VERIFIED"
    CUSTODY_REGISTERED = "CUSTODY_REGISTERED"
    ABORTED = "ABORTED"
    ORPHANED = "ORPHANED"


_ALLOWED = {
    UploadAttemptStatus.INITIATING: {UploadAttemptStatus.INITIATED, UploadAttemptStatus.ORPHANED},
    UploadAttemptStatus.INITIATED: {UploadAttemptStatus.PARTS_UPLOADED, UploadAttemptStatus.COMPLETION_UNCERTAIN, UploadAttemptStatus.ABORTED, UploadAttemptStatus.ORPHANED},
    UploadAttemptStatus.PARTS_UPLOADED: {UploadAttemptStatus.PARTS_UPLOADED, UploadAttemptStatus.COMPLETION_UNCERTAIN, UploadAttemptStatus.PROVIDER_VERIFIED, UploadAttemptStatus.ABORTED},
    UploadAttemptStatus.COMPLETION_UNCERTAIN: {UploadAttemptStatus.PROVIDER_VERIFIED, UploadAttemptStatus.ABORTED, UploadAttemptStatus.ORPHANED},
    UploadAttemptStatus.PROVIDER_VERIFIED: {UploadAttemptStatus.CUSTODY_REGISTERED, UploadAttemptStatus.ORPHANED},
    UploadAttemptStatus.CUSTODY_REGISTERED: set(),
    UploadAttemptStatus.ABORTED: set(),
    UploadAttemptStatus.ORPHANED: set(),
}


def _id(value: object, code: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or _ID.fullmatch(value) is None:
        raise UploadAttemptError(code)
    return value


def _provider_token(value: object) -> str:
    # AWS multipart UploadId values are opaque provider tokens, not WILSY
    # identifiers. Preserve the exact token for recovery while rejecting
    # whitespace/control characters and unbounded provider responses.
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 2048
        or any(ord(character) < 33 or ord(character) > 126 for character in value)
    ):
        raise UploadAttemptError("UPLOAD_ATTEMPT_PROVIDER_UPLOAD_INVALID")
    return value


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise UploadAttemptError("UPLOAD_ATTEMPT_UTC_REQUIRED")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class CandidateEvidenceUploadAttempt:
    tenant_id: str
    upload_attempt_id: str
    candidate_id: str
    evidence_id: str
    evidence_version_id: str
    ingestion_reference: str
    intent_fingerprint: str
    provider_id: str
    provider_upload_id: str | None
    provider_object_reference: str | None
    status: UploadAttemptStatus
    revision: int
    created_at: datetime
    updated_at: datetime
    offer_id: str | None = None
    actor_principal_id: str | None = None
    evidence_kind: str | None = None
    media_type: str | None = None
    original_filename: str | None = None
    admitted_max_content_length: int | None = None
    parts: tuple[Mapping[str, Any], ...] = ()
    byte_length: int = 0
    object_version_reference: str | None = None
    content_digest_sha3_512: str | None = None
    provider_integrity_reference: str | None = None
    failure_code: str | None = None
    fingerprint: str = ""

    def __post_init__(self):
        for field, code in (
            (self.tenant_id, "UPLOAD_ATTEMPT_TENANT_INVALID"),
            (self.upload_attempt_id, "UPLOAD_ATTEMPT_ID_INVALID"),
            (self.candidate_id, "UPLOAD_ATTEMPT_CANDIDATE_INVALID"),
            (self.evidence_id, "UPLOAD_ATTEMPT_EVIDENCE_INVALID"),
            (self.evidence_version_id, "UPLOAD_ATTEMPT_VERSION_INVALID"),
            (self.ingestion_reference, "UPLOAD_ATTEMPT_INGESTION_INVALID"),
            (self.provider_id, "UPLOAD_ATTEMPT_PROVIDER_INVALID"),
        ):
            _id(field, code)
        provider_absent = self.provider_upload_id is None and self.provider_object_reference is None
        if self.status is UploadAttemptStatus.INITIATING or (
            self.status is UploadAttemptStatus.ORPHANED and provider_absent
        ):
            if not provider_absent:
                raise UploadAttemptError("UPLOAD_ATTEMPT_PROVIDER_MUST_BE_PENDING")
        else:
            _provider_token(self.provider_upload_id)
            if not isinstance(self.provider_object_reference, str) or not self.provider_object_reference.strip():
                raise UploadAttemptError("UPLOAD_ATTEMPT_PROVIDER_OBJECT_INVALID")
        if self.offer_id is not None:
            _id(self.offer_id, "UPLOAD_ATTEMPT_OFFER_INVALID")
        if self.actor_principal_id is not None:
            _id(self.actor_principal_id, "UPLOAD_ATTEMPT_ACTOR_INVALID")
        if self.evidence_kind is not None and self.evidence_kind not in {"CANDIDATE_PROFILE", "SIGNED_OFFER"}:
            raise UploadAttemptError("UPLOAD_ATTEMPT_EVIDENCE_KIND_INVALID")
        for name, value, maximum in (
            ("media_type", self.media_type, 128),
            ("original_filename", self.original_filename, 255),
        ):
            if value is not None and (
                not isinstance(value, str) or not value or value != value.strip()
                or len(value) > maximum or any(ord(c) < 32 for c in value)
            ):
                raise UploadAttemptError(f"UPLOAD_ATTEMPT_{name.upper()}_INVALID")
        if self.admitted_max_content_length is not None and (
            type(self.admitted_max_content_length) is not int
            or not 1 <= self.admitted_max_content_length <= 100 * 1024 * 1024
        ):
            raise UploadAttemptError("UPLOAD_ATTEMPT_MAX_LENGTH_INVALID")
        for value in (self.intent_fingerprint, self.content_digest_sha3_512):
            if value is not None and (not isinstance(value, str) or len(value) != 128 or any(c not in "0123456789abcdef" for c in value)):
                raise UploadAttemptError("UPLOAD_ATTEMPT_DIGEST_INVALID")
        if type(self.status) is not UploadAttemptStatus or type(self.revision) is not int or self.revision < 1:
            raise UploadAttemptError("UPLOAD_ATTEMPT_STATE_INVALID")
        if type(self.byte_length) is not int or self.byte_length < 0:
            raise UploadAttemptError("UPLOAD_ATTEMPT_LENGTH_INVALID")
        created, updated = _utc(self.created_at), _utc(self.updated_at)
        if updated < created:
            raise UploadAttemptError("UPLOAD_ATTEMPT_CHRONOLOGY_INVALID")
        parts = tuple(dict(p) for p in self.parts)
        if len(parts) > 10000:
            raise UploadAttemptError("UPLOAD_ATTEMPT_PART_LIMIT")
        payload = {
            "tenant_id": self.tenant_id, "upload_attempt_id": self.upload_attempt_id,
            "candidate_id": self.candidate_id, "evidence_id": self.evidence_id,
            "evidence_version_id": self.evidence_version_id, "ingestion_reference": self.ingestion_reference,
            "intent_fingerprint": self.intent_fingerprint, "provider_id": self.provider_id,
            "provider_upload_id": self.provider_upload_id, "provider_object_reference": self.provider_object_reference,
            "status": self.status.value, "revision": self.revision, "created_at": created.isoformat(),
            "updated_at": updated.isoformat(), "offer_id": self.offer_id, "parts": parts,
            "byte_length": self.byte_length, "object_version_reference": self.object_version_reference,
            "content_digest_sha3_512": self.content_digest_sha3_512,
            "provider_integrity_reference": self.provider_integrity_reference, "failure_code": self.failure_code,
        }
        recovery_context = {
            "actor_principal_id": self.actor_principal_id,
            "evidence_kind": self.evidence_kind,
            "media_type": self.media_type,
            "original_filename": self.original_filename,
            "admitted_max_content_length": self.admitted_max_content_length,
        }
        if any(value is not None for value in recovery_context.values()):
            payload.update(recovery_context)
        fp = hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
        if self.fingerprint and self.fingerprint != fp:
            raise UploadAttemptError("UPLOAD_ATTEMPT_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "updated_at", updated)
        object.__setattr__(self, "parts", parts)
        object.__setattr__(self, "fingerprint", fp)

    def advance(self, *, status: UploadAttemptStatus, expected_revision: int, occurred_at: datetime,
                parts: tuple[Mapping[str, Any], ...] | None = None, byte_length: int | None = None,
                object_version_reference: str | None = None, content_digest_sha3_512: str | None = None,
                provider_integrity_reference: str | None = None, failure_code: str | None = None,
                provider_upload_id: str | None = None, provider_object_reference: str | None = None):
        if expected_revision != self.revision or status not in _ALLOWED[self.status]:
            raise UploadAttemptConflict("UPLOAD_ATTEMPT_TRANSITION_CONFLICT")
        return CandidateEvidenceUploadAttempt(
            tenant_id=self.tenant_id, upload_attempt_id=self.upload_attempt_id,
            candidate_id=self.candidate_id, evidence_id=self.evidence_id,
            evidence_version_id=self.evidence_version_id, ingestion_reference=self.ingestion_reference,
            intent_fingerprint=self.intent_fingerprint, provider_id=self.provider_id,
            provider_upload_id=provider_upload_id if provider_upload_id is not None else self.provider_upload_id,
            provider_object_reference=provider_object_reference if provider_object_reference is not None else self.provider_object_reference,
            status=status, revision=self.revision + 1, created_at=self.created_at,
            updated_at=_utc(occurred_at), offer_id=self.offer_id,
            actor_principal_id=self.actor_principal_id,
            evidence_kind=self.evidence_kind, media_type=self.media_type,
            original_filename=self.original_filename,
            admitted_max_content_length=self.admitted_max_content_length,
            parts=self.parts if parts is None else parts,
            byte_length=self.byte_length if byte_length is None else byte_length,
            object_version_reference=object_version_reference or self.object_version_reference,
            content_digest_sha3_512=content_digest_sha3_512 or self.content_digest_sha3_512,
            provider_integrity_reference=provider_integrity_reference or self.provider_integrity_reference,
            failure_code=failure_code,
        )

    def to_dict(self):
        return {
            "tenant_id": self.tenant_id, "upload_attempt_id": self.upload_attempt_id,
            "candidate_id": self.candidate_id, "evidence_id": self.evidence_id,
            "evidence_version_id": self.evidence_version_id, "ingestion_reference": self.ingestion_reference,
            "intent_fingerprint": self.intent_fingerprint, "provider_id": self.provider_id,
            "provider_upload_id": self.provider_upload_id, "provider_object_reference": self.provider_object_reference,
            "status": self.status.value, "revision": self.revision, "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(), "offer_id": self.offer_id,
            "actor_principal_id": self.actor_principal_id, "evidence_kind": self.evidence_kind,
            "media_type": self.media_type, "original_filename": self.original_filename,
            "admitted_max_content_length": self.admitted_max_content_length,
            "parts": list(self.parts), "byte_length": self.byte_length,
            "object_version_reference": self.object_version_reference,
            "content_digest_sha3_512": self.content_digest_sha3_512,
            "provider_integrity_reference": self.provider_integrity_reference,
            "failure_code": self.failure_code, "fingerprint": self.fingerprint,
        }


class CandidateEvidenceUploadAttemptRegistry:
    def __init__(self, attempts: Any, events: Any):
        if attempts is None or events is None:
            raise UploadAttemptError("UPLOAD_ATTEMPT_COLLECTION_REQUIRED")
        self._attempts, self._events = attempts, events

    @staticmethod
    def ensure_indexes(attempts: Any, events: Any):
        try:
            attempts.create_index([("tenant_id", ASCENDING), ("upload_attempt_id", ASCENDING)], unique=True, name="uq_hr_evidence_upload_attempt")
            attempts.create_index([("tenant_id", ASCENDING), ("status", ASCENDING), ("updated_at", ASCENDING)], name="ix_hr_evidence_upload_reconciliation")
            attempts.create_index(
                [
                    ("tenant_id", ASCENDING), ("candidate_id", ASCENDING),
                    ("evidence_id", ASCENDING), ("evidence_version_id", ASCENDING),
                ],
                unique=True,
                partialFilterExpression={"status": {"$in": [
                    UploadAttemptStatus.INITIATING.value,
                    UploadAttemptStatus.INITIATED.value,
                    UploadAttemptStatus.PARTS_UPLOADED.value,
                    UploadAttemptStatus.COMPLETION_UNCERTAIN.value,
                    UploadAttemptStatus.PROVIDER_VERIFIED.value,
                ]}},
                name="uq_hr_evidence_upload_active_scope",
            )
            events.create_index([("tenant_id", ASCENDING), ("upload_attempt_id", ASCENDING), ("revision", ASCENDING)], unique=True, name="uq_hr_evidence_upload_attempt_event")
        except PyMongoError as error:
            raise UploadAttemptError("UPLOAD_ATTEMPT_INDEX_UNAVAILABLE") from error

    def create(self, value: CandidateEvidenceUploadAttempt, *, session: object):
        if session is None:
            raise UploadAttemptError("UPLOAD_ATTEMPT_TRANSACTION_REQUIRED")
        try:
            self._attempts.insert_one(value.to_dict(), session=session)
            self._events.insert_one({"tenant_id": value.tenant_id, "upload_attempt_id": value.upload_attempt_id,
                "revision": value.revision, "action": value.status.value,
                "fingerprint": value.fingerprint, "snapshot": value.to_dict()}, session=session)
            return value
        except DuplicateKeyError as error:
            raise UploadAttemptConflict("UPLOAD_ATTEMPT_ALREADY_EXISTS") from error
        except PyMongoError as error:
            raise UploadAttemptError("UPLOAD_ATTEMPT_CREATE_UNAVAILABLE") from error

    def transition(self, current: CandidateEvidenceUploadAttempt, updated: CandidateEvidenceUploadAttempt,
                   *, expected_revision: int, actor_principal_id: str, session: object):
        if session is None:
            raise UploadAttemptError("UPLOAD_ATTEMPT_TRANSACTION_REQUIRED")
        if (current.tenant_id != updated.tenant_id or current.upload_attempt_id != updated.upload_attempt_id
            or updated.revision != expected_revision + 1 or current.revision != expected_revision):
            raise UploadAttemptConflict("UPLOAD_ATTEMPT_REVISION_CONFLICT")
        _id(actor_principal_id, "UPLOAD_ATTEMPT_ACTOR_INVALID")
        try:
            result = self._attempts.update_one(
                {"tenant_id": current.tenant_id, "upload_attempt_id": current.upload_attempt_id,
                 "revision": expected_revision, "fingerprint": current.fingerprint},
                {"$set": updated.to_dict()}, session=session,
            )
            if result.matched_count != 1:
                raise UploadAttemptConflict("UPLOAD_ATTEMPT_REVISION_CONFLICT")
            self._events.insert_one({"tenant_id": updated.tenant_id, "upload_attempt_id": updated.upload_attempt_id,
                "revision": updated.revision, "actor_principal_id": actor_principal_id,
                "action": updated.status.value, "fingerprint": updated.fingerprint,
                "snapshot": updated.to_dict()}, session=session)
            return updated
        except UploadAttemptConflict:
            raise
        except DuplicateKeyError as error:
            raise UploadAttemptConflict("UPLOAD_ATTEMPT_EVENT_CONFLICT") from error
        except PyMongoError as error:
            raise UploadAttemptError("UPLOAD_ATTEMPT_TRANSITION_UNAVAILABLE") from error

    def list_reconcilable(self, *, session: object, limit: int = 500):
        if session is None:
            raise UploadAttemptError("UPLOAD_ATTEMPT_TRANSACTION_REQUIRED")
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise UploadAttemptError("UPLOAD_ATTEMPT_LIMIT_INVALID")
        statuses = [
            UploadAttemptStatus.INITIATING.value,
            UploadAttemptStatus.INITIATED.value,
            UploadAttemptStatus.PARTS_UPLOADED.value,
            UploadAttemptStatus.COMPLETION_UNCERTAIN.value,
            UploadAttemptStatus.PROVIDER_VERIFIED.value,
        ]
        try:
            rows = list(
                self._attempts.find({"status": {"$in": statuses}}, session=session)
                .sort("updated_at", ASCENDING).limit(limit)
            )
        except PyMongoError as error:
            raise UploadAttemptError("UPLOAD_ATTEMPT_RECONCILIATION_READ_UNAVAILABLE") from error
        result = []
        for row in rows:
            row.pop("_id", None)
            row.pop("fingerprint", None)
            row["created_at"] = row["created_at"] if isinstance(row["created_at"], str) else row["created_at"].isoformat()
            row["updated_at"] = row["updated_at"] if isinstance(row["updated_at"], str) else row["updated_at"].isoformat()
            row["status"] = UploadAttemptStatus(row["status"])
            result.append(CandidateEvidenceUploadAttempt(**row))
        return tuple(result)

    def get(self, *, tenant_id: str, upload_attempt_id: str, session: object):
        if session is None:
            raise UploadAttemptError("UPLOAD_ATTEMPT_TRANSACTION_REQUIRED")
        scope = {"tenant_id": _id(tenant_id, "UPLOAD_ATTEMPT_TENANT_INVALID"),
                 "upload_attempt_id": _id(upload_attempt_id, "UPLOAD_ATTEMPT_ID_INVALID")}
        try:
            row = self._attempts.find_one(scope, session=session)
        except PyMongoError as error:
            raise UploadAttemptError("UPLOAD_ATTEMPT_READ_UNAVAILABLE") from error
        if row is None:
            raise UploadAttemptError("UPLOAD_ATTEMPT_NOT_FOUND")
        row.pop("_id", None)
        row.pop("fingerprint", None)
        row["created_at"] = row["created_at"] if isinstance(row["created_at"], str) else row["created_at"].isoformat()
        row["updated_at"] = row["updated_at"] if isinstance(row["updated_at"], str) else row["updated_at"].isoformat()
        row["status"] = UploadAttemptStatus(row["status"])
        return CandidateEvidenceUploadAttempt(**row)
