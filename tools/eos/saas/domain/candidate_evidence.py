"""Immutable metadata for tenant-scoped candidate and offer evidence objects.

This domain stores no candidate PII or binary bytes. Provider execution and
cryptographic signature verification are separate authorities.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import re
from typing import Any, Mapping


SCHEMA = "WILSY-HR-CANDIDATE-EVIDENCE/V1"
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")
_HEX = frozenset("0123456789abcdef")


class CandidateEvidenceError(ValueError):
    pass


class CandidateEvidenceKind(str, Enum):
    CANDIDATE_PROFILE = "CANDIDATE_PROFILE"
    SIGNED_OFFER = "SIGNED_OFFER"


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or _ID.fullmatch(value) is None:
        raise CandidateEvidenceError(f"CANDIDATE_EVIDENCE_{name.upper()}_INVALID")
    return value


def _text(name: str, value: object, limit: int = 512) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > limit or any(ord(c) < 32 for c in value):
        raise CandidateEvidenceError(f"CANDIDATE_EVIDENCE_{name.upper()}_INVALID")
    return value


def _digest(name: str, value: object) -> str:
    if not isinstance(value, str) or len(value) != 128 or any(c not in _HEX for c in value):
        raise CandidateEvidenceError(f"CANDIDATE_EVIDENCE_{name.upper()}_INVALID")
    return value


def _utc(name: str, value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise CandidateEvidenceError(f"CANDIDATE_EVIDENCE_{name.upper()}_UTC_REQUIRED")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class CandidateEvidenceObjectMetadata:
    tenant_id: str
    candidate_id: str
    evidence_id: str
    evidence_version_id: str
    evidence_kind: CandidateEvidenceKind
    media_type: str
    original_filename: str
    byte_length: int
    content_digest_sha3_512: str
    storage_provider_id: str
    storage_object_reference: str
    object_version_reference: str
    provider_integrity_reference: str
    ingestion_reference: str
    created_at: datetime
    created_by_principal_id: str
    offer_id: str | None = None
    retention_until: datetime | None = None
    legal_hold: bool = False
    signature_verification_reference: str | None = None
    schema: str = SCHEMA
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _identity("tenant_id", self.tenant_id)
        candidate = _identity("candidate_id", self.candidate_id)
        evidence = _identity("evidence_id", self.evidence_id)
        version = _identity("evidence_version_id", self.evidence_version_id)
        if type(self.evidence_kind) is not CandidateEvidenceKind:
            raise CandidateEvidenceError("CANDIDATE_EVIDENCE_KIND_INVALID")
        media = _text("media_type", self.media_type, 128).lower()
        filename = _text("original_filename", self.original_filename, 255)
        if type(self.byte_length) is not int or self.byte_length <= 0:
            raise CandidateEvidenceError("CANDIDATE_EVIDENCE_BYTE_LENGTH_INVALID")
        digest = _digest("content_digest_sha3_512", self.content_digest_sha3_512)
        provider = _identity("storage_provider_id", self.storage_provider_id)
        storage_ref = _text("storage_object_reference", self.storage_object_reference, 1024)
        object_version = _text("object_version_reference", self.object_version_reference, 512)
        integrity = _text("provider_integrity_reference", self.provider_integrity_reference, 512)
        ingestion = _identity("ingestion_reference", self.ingestion_reference)
        actor = _identity("created_by_principal_id", self.created_by_principal_id)
        offer = None if self.offer_id is None else _identity("offer_id", self.offer_id)
        if self.evidence_kind is CandidateEvidenceKind.SIGNED_OFFER and offer is None:
            raise CandidateEvidenceError("CANDIDATE_EVIDENCE_SIGNED_OFFER_REQUIRES_OFFER")
        if self.evidence_kind is CandidateEvidenceKind.CANDIDATE_PROFILE and offer is not None:
            raise CandidateEvidenceError("CANDIDATE_EVIDENCE_PROFILE_OFFER_SCOPE_FORBIDDEN")
        if type(self.legal_hold) is not bool:
            raise CandidateEvidenceError("CANDIDATE_EVIDENCE_LEGAL_HOLD_INVALID")
        signature_ref = None if self.signature_verification_reference is None else _text("signature_verification_reference", self.signature_verification_reference, 512)
        created = _utc("created_at", self.created_at)
        retention = None if self.retention_until is None else _utc("retention_until", self.retention_until)
        if retention is not None and retention < created:
            raise CandidateEvidenceError("CANDIDATE_EVIDENCE_RETENTION_INVALID")
        if self.schema != SCHEMA:
            raise CandidateEvidenceError("CANDIDATE_EVIDENCE_SCHEMA_INVALID")
        values = {
            "tenant_id": tenant, "candidate_id": candidate, "evidence_id": evidence,
            "evidence_version_id": version, "evidence_kind": self.evidence_kind.value,
            "media_type": media, "original_filename": filename, "byte_length": self.byte_length,
            "content_digest_sha3_512": digest, "storage_provider_id": provider,
            "storage_object_reference": storage_ref, "object_version_reference": object_version,
            "provider_integrity_reference": integrity, "ingestion_reference": ingestion,
            "created_at": created.isoformat(), "created_by_principal_id": actor,
            "offer_id": offer, "retention_until": retention.isoformat() if retention else None,
            "legal_hold": self.legal_hold, "signature_verification_reference": signature_ref,
            "schema": SCHEMA,
        }
        fingerprint = hashlib.sha3_512(json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        if self.fingerprint and self.fingerprint != fingerprint:
            raise CandidateEvidenceError("CANDIDATE_EVIDENCE_FINGERPRINT_MISMATCH")
        for name, value in (
            ("tenant_id", tenant), ("candidate_id", candidate), ("evidence_id", evidence),
            ("evidence_version_id", version), ("media_type", media), ("original_filename", filename),
            ("content_digest_sha3_512", digest), ("storage_provider_id", provider),
            ("storage_object_reference", storage_ref), ("object_version_reference", object_version),
            ("provider_integrity_reference", integrity), ("ingestion_reference", ingestion),
            ("created_by_principal_id", actor), ("offer_id", offer), ("created_at", created),
            ("retention_until", retention), ("signature_verification_reference", signature_ref),
            ("fingerprint", fingerprint),
        ):
            object.__setattr__(self, name, value)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id, "candidate_id": self.candidate_id,
            "evidence_id": self.evidence_id, "evidence_version_id": self.evidence_version_id,
            "evidence_kind": self.evidence_kind.value, "media_type": self.media_type,
            "original_filename": self.original_filename, "byte_length": self.byte_length,
            "content_digest_sha3_512": self.content_digest_sha3_512,
            "storage_provider_id": self.storage_provider_id,
            "storage_object_reference": self.storage_object_reference,
            "object_version_reference": self.object_version_reference,
            "provider_integrity_reference": self.provider_integrity_reference,
            "ingestion_reference": self.ingestion_reference, "created_at": self.created_at.isoformat(),
            "created_by_principal_id": self.created_by_principal_id, "offer_id": self.offer_id,
            "retention_until": self.retention_until.isoformat() if self.retention_until else None,
            "legal_hold": self.legal_hold, "signature_verification_reference": self.signature_verification_reference,
            "schema": self.schema, "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "CandidateEvidenceObjectMetadata":
        expected = {
            "tenant_id", "candidate_id", "evidence_id", "evidence_version_id", "evidence_kind",
            "media_type", "original_filename", "byte_length", "content_digest_sha3_512",
            "storage_provider_id", "storage_object_reference", "object_version_reference",
            "provider_integrity_reference", "ingestion_reference", "created_at",
            "created_by_principal_id", "offer_id", "retention_until", "legal_hold",
            "signature_verification_reference", "schema", "fingerprint",
        }
        if not isinstance(value, Mapping) or set(value) != expected:
            raise CandidateEvidenceError("CANDIDATE_EVIDENCE_FIELDS_INVALID")
        return cls(
            tenant_id=value["tenant_id"], candidate_id=value["candidate_id"],
            evidence_id=value["evidence_id"], evidence_version_id=value["evidence_version_id"],
            evidence_kind=CandidateEvidenceKind(value["evidence_kind"]), media_type=value["media_type"],
            original_filename=value["original_filename"], byte_length=value["byte_length"],
            content_digest_sha3_512=value["content_digest_sha3_512"],
            storage_provider_id=value["storage_provider_id"], storage_object_reference=value["storage_object_reference"],
            object_version_reference=value["object_version_reference"], provider_integrity_reference=value["provider_integrity_reference"],
            ingestion_reference=value["ingestion_reference"], created_at=datetime.fromisoformat(value["created_at"]),
            created_by_principal_id=value["created_by_principal_id"], offer_id=value["offer_id"],
            retention_until=datetime.fromisoformat(value["retention_until"]) if value["retention_until"] else None,
            legal_hold=value["legal_hold"], signature_verification_reference=value["signature_verification_reference"],
            schema=value["schema"], fingerprint=value["fingerprint"],
        )
