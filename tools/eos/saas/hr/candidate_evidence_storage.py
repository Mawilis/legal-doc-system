"""Provider-neutral streamed storage contract for candidate and offer evidence."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Protocol, runtime_checkable


SCHEMA = "WILSY-HR-CANDIDATE-EVIDENCE-STORAGE/V1"
MAX_CHUNK_BYTES = 16 * 1024 * 1024
MAX_OBJECT_BYTES = 100 * 1024 * 1024
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")


class CandidateEvidenceStorageError(ValueError):
    pass


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or _ID.fullmatch(value) is None:
        raise CandidateEvidenceStorageError(f"CANDIDATE_EVIDENCE_STORAGE_{name.upper()}_INVALID")
    return value


def _text(name: str, value: object, limit: int = 512) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > limit or any(ord(c) < 32 for c in value):
        raise CandidateEvidenceStorageError(f"CANDIDATE_EVIDENCE_STORAGE_{name.upper()}_INVALID")
    return value


@dataclass(frozen=True, slots=True)
class CandidateEvidenceWriteIntent:
    tenant_id: str
    candidate_id: str
    evidence_id: str
    evidence_version_id: str
    ingestion_reference: str
    media_type: str
    original_filename: str
    admitted_max_content_length: int
    schema: str = SCHEMA
    fingerprint: str = ""

    def __post_init__(self) -> None:
        values = {
            "tenant_id": _identity("tenant_id", self.tenant_id),
            "candidate_id": _identity("candidate_id", self.candidate_id),
            "evidence_id": _identity("evidence_id", self.evidence_id),
            "evidence_version_id": _identity("evidence_version_id", self.evidence_version_id),
            "ingestion_reference": _identity("ingestion_reference", self.ingestion_reference),
            "media_type": _text("media_type", self.media_type, 128).lower(),
            "original_filename": _text("original_filename", self.original_filename, 255),
        }
        if self.tenant_id.casefold() in {"default", "global", "global_root", "root", "master", "*"}:
            raise CandidateEvidenceStorageError("CANDIDATE_EVIDENCE_STORAGE_TENANT_REQUIRED")
        if type(self.admitted_max_content_length) is not int or not 1 <= self.admitted_max_content_length <= MAX_OBJECT_BYTES:
            raise CandidateEvidenceStorageError("CANDIDATE_EVIDENCE_STORAGE_MAX_LENGTH_INVALID")
        if self.schema != SCHEMA:
            raise CandidateEvidenceStorageError("CANDIDATE_EVIDENCE_STORAGE_SCHEMA_INVALID")
        payload = {**values, "admitted_max_content_length": self.admitted_max_content_length, "schema": SCHEMA}
        fingerprint = hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if self.fingerprint and self.fingerprint != fingerprint:
            raise CandidateEvidenceStorageError("CANDIDATE_EVIDENCE_STORAGE_INTENT_FINGERPRINT_MISMATCH")
        for name, value in values.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "fingerprint", fingerprint)


@dataclass(slots=True)
class CandidateEvidenceWriteSession:
    intent: CandidateEvidenceWriteIntent
    provider_upload_id: str
    provider_object_key: str
    storage_object_reference: str
    created_at: datetime
    parts: list[dict[str, Any]] = field(default_factory=list)
    bytes_written: int = 0
    hasher: Any = field(default_factory=hashlib.sha3_512)
    closed: bool = False


@dataclass(frozen=True, slots=True)
class CandidateEvidenceBinaryObjectEvidence:
    intent_fingerprint: str
    storage_object_reference: str
    object_version_reference: str
    provider_integrity_reference: str
    byte_length: int
    content_digest_sha3_512: str
    completed_at: datetime

    def __post_init__(self) -> None:
        for name, value in (
            ("intent_fingerprint", self.intent_fingerprint),
            ("content_digest_sha3_512", self.content_digest_sha3_512),
        ):
            if not isinstance(value, str) or len(value) != 128 or any(c not in "0123456789abcdef" for c in value):
                raise CandidateEvidenceStorageError(f"CANDIDATE_EVIDENCE_STORAGE_{name.upper()}_INVALID")
        for name, value in (
            ("storage_object_reference", self.storage_object_reference),
            ("object_version_reference", self.object_version_reference),
            ("provider_integrity_reference", self.provider_integrity_reference),
        ):
            _text(name, value, 1024)
        if type(self.byte_length) is not int or self.byte_length <= 0:
            raise CandidateEvidenceStorageError("CANDIDATE_EVIDENCE_STORAGE_BYTE_LENGTH_INVALID")
        if not isinstance(self.completed_at, datetime) or self.completed_at.tzinfo is None or self.completed_at.utcoffset() is None:
            raise CandidateEvidenceStorageError("CANDIDATE_EVIDENCE_STORAGE_COMPLETION_TIME_UTC_REQUIRED")
        object.__setattr__(self, "completed_at", self.completed_at.astimezone(timezone.utc))


@runtime_checkable
class CandidateEvidenceBinaryStoragePort(Protocol):
    def begin(self, intent: CandidateEvidenceWriteIntent) -> CandidateEvidenceWriteSession: ...
    def write_chunk(self, session: CandidateEvidenceWriteSession, chunk: bytes) -> int: ...
    def complete(self, session: CandidateEvidenceWriteSession) -> CandidateEvidenceBinaryObjectEvidence: ...
    def inspect(self, intent: CandidateEvidenceWriteIntent, evidence: CandidateEvidenceBinaryObjectEvidence) -> CandidateEvidenceBinaryObjectEvidence: ...
    def abort(self, session: CandidateEvidenceWriteSession) -> None: ...


__all__ = [
    "SCHEMA", "MAX_CHUNK_BYTES", "MAX_OBJECT_BYTES",
    "CandidateEvidenceStorageError", "CandidateEvidenceWriteIntent",
    "CandidateEvidenceWriteSession", "CandidateEvidenceBinaryObjectEvidence",
    "CandidateEvidenceBinaryStoragePort",
]
