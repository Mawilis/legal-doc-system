"""WILSY OS object-backed canonical Legal Evidence metadata domain.

TITLE: Legal Evidence Object Metadata
VERSION: v1.0.0-L10A2R-C1-LEGAL-EVIDENCE-OBJECT-METADATA
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Bind one canonical LegalEvidenceContent value to one exact provider-neutral
    binary write intent and one exact verified provider object-version evidence
    value without persisting or carrying the raw binary body.

EPITOME:
    CANONICAL LEGAL EVIDENCE CONTENT
    + EXACT BINARY WRITE INTENT
    + VERIFIED PROVIDER OBJECT EVIDENCE
    -> OBJECT-BACKED CANONICAL METADATA
    != RAW-BYTE PERSISTENCE
    != PROVIDER EXECUTION
    != RESERVATION CONSUMPTION
    != USAGE COMMIT
    != AUTHORIZED AVAILABILITY

INTEGRITY:
    WILSY SHA3-512 content identity remains canonical. Provider-native integrity
    is preserved as storage evidence only and never replaces canonical WILSY
    content identity.

CONTROL / OBJECT PLANE:
    The resulting value is suitable for later Mongo control-plane persistence
    but contains no binary body. Provider object/version coordinates are
    evidence only and do not become tenant, Legal lifecycle, IAM, retention,
    Court, billing, payment or settlement authority.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Final

from tools.eos.legal_operations.domain.legal_evidence_content import (
    LegalEvidenceContent,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryStoragePortError,
    LegalEvidenceBinaryWriteIntent,
    validate_object_evidence_for_intent,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C1-LEGAL-EVIDENCE-OBJECT-METADATA"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-EVIDENCE-OBJECT-METADATA/V1"
)

_HEX_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)

_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id",
    "case_matter_id",
    "document_id",
    "content_reference",
    "media_type",
    "original_filename",
    "content_length",
    "content_fingerprint",
    "content_metadata_fingerprint",
    "registered_at",
    "provider_name",
    "storage_reference",
    "object_version_reference",
    "provider_integrity_reference",
    "write_intent_fingerprint",
    "schema",
    "object_metadata_version",
    "fingerprint",
)


class LegalEvidenceObjectMetadataError(ValueError):
    """Stable fail-closed L10A2R-C1 domain error."""


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise LegalEvidenceObjectMetadataError(
            f"L10A2R_C1_{name.upper()}_INVALID"
        )
    return value


def _positive_int(
    name: str,
    value: object,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        raise LegalEvidenceObjectMetadataError(
            f"L10A2R_C1_{name.upper()}_INVALID"
        )
    return value


def _sha3(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or _HEX_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceObjectMetadataError(
            f"L10A2R_C1_{name.upper()}_INVALID"
        )
    return value


def _utc(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceObjectMetadataError(
            f"L10A2R_C1_{name.upper()}_INVALID"
        )
    return value.astimezone(
        timezone.utc
    )


def _fingerprint_payload(
    *,
    tenant_id: str,
    case_matter_id: str,
    document_id: str,
    content_reference: str,
    media_type: str,
    original_filename: str,
    content_length: int,
    content_fingerprint: str,
    content_metadata_fingerprint: str,
    registered_at: datetime,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    provider_integrity_reference: str,
    write_intent_fingerprint: str,
    schema: str,
    object_metadata_version: str,
) -> dict[str, object]:
    return {
        "tenant_id": tenant_id,
        "case_matter_id": case_matter_id,
        "document_id": document_id,
        "content_reference": content_reference,
        "media_type": media_type,
        "original_filename": original_filename,
        "content_length": content_length,
        "content_fingerprint": content_fingerprint,
        "content_metadata_fingerprint": content_metadata_fingerprint,
        "registered_at": registered_at.isoformat(),
        "provider_name": provider_name,
        "storage_reference": storage_reference,
        "object_version_reference": object_version_reference,
        "provider_integrity_reference": provider_integrity_reference,
        "write_intent_fingerprint": write_intent_fingerprint,
        "schema": schema,
        "object_metadata_version": object_metadata_version,
    }


def _fingerprint(
    **values: object,
) -> str:
    raw = json.dumps(
        values,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalEvidenceObjectMetadata:
    """Immutable metadata-only binding between WILSY content and object evidence."""

    tenant_id: str
    case_matter_id: str
    document_id: str
    content_reference: str
    media_type: str
    original_filename: str
    content_length: int
    content_fingerprint: str
    content_metadata_fingerprint: str
    registered_at: datetime
    provider_name: str
    storage_reference: str
    object_version_reference: str
    provider_integrity_reference: str
    write_intent_fingerprint: str
    schema: str = SCHEMA
    object_metadata_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _text(
            "tenant_id",
            self.tenant_id,
        )
        matter = _text(
            "case_matter_id",
            self.case_matter_id,
        )
        document = _text(
            "document_id",
            self.document_id,
        )
        content_reference = _text(
            "content_reference",
            self.content_reference,
        )
        media_type = _text(
            "media_type",
            self.media_type,
        )
        original_filename = _text(
            "original_filename",
            self.original_filename,
        )
        content_length = _positive_int(
            "content_length",
            self.content_length,
        )
        content_fingerprint = _sha3(
            "content_fingerprint",
            self.content_fingerprint,
        )
        content_metadata_fingerprint = _sha3(
            "content_metadata_fingerprint",
            self.content_metadata_fingerprint,
        )
        registered_at = _utc(
            "registered_at",
            self.registered_at,
        )
        provider_name = _text(
            "provider_name",
            self.provider_name,
        )
        storage_reference = _text(
            "storage_reference",
            self.storage_reference,
        )
        object_version_reference = _text(
            "object_version_reference",
            self.object_version_reference,
        )
        provider_integrity_reference = _text(
            "provider_integrity_reference",
            self.provider_integrity_reference,
        )
        write_intent_fingerprint = _sha3(
            "write_intent_fingerprint",
            self.write_intent_fingerprint,
        )

        if self.schema != SCHEMA:
            raise LegalEvidenceObjectMetadataError(
                "L10A2R_C1_SCHEMA_INVALID"
            )

        if self.object_metadata_version != VERSION:
            raise LegalEvidenceObjectMetadataError(
                "L10A2R_C1_VERSION_INVALID"
            )

        payload = _fingerprint_payload(
            tenant_id=tenant,
            case_matter_id=matter,
            document_id=document,
            content_reference=content_reference,
            media_type=media_type,
            original_filename=original_filename,
            content_length=content_length,
            content_fingerprint=content_fingerprint,
            content_metadata_fingerprint=content_metadata_fingerprint,
            registered_at=registered_at,
            provider_name=provider_name,
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            provider_integrity_reference=provider_integrity_reference,
            write_intent_fingerprint=write_intent_fingerprint,
            schema=self.schema,
            object_metadata_version=self.object_metadata_version,
        )

        digest = _fingerprint(
            **payload
        )

        if self.fingerprint:
            if (
                not isinstance(self.fingerprint, str)
                or not hmac.compare_digest(
                    self.fingerprint,
                    digest,
                )
            ):
                raise LegalEvidenceObjectMetadataError(
                    "L10A2R_C1_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "case_matter_id",
            matter,
        )
        object.__setattr__(
            self,
            "document_id",
            document,
        )
        object.__setattr__(
            self,
            "content_reference",
            content_reference,
        )
        object.__setattr__(
            self,
            "media_type",
            media_type,
        )
        object.__setattr__(
            self,
            "original_filename",
            original_filename,
        )
        object.__setattr__(
            self,
            "content_length",
            content_length,
        )
        object.__setattr__(
            self,
            "content_fingerprint",
            content_fingerprint,
        )
        object.__setattr__(
            self,
            "content_metadata_fingerprint",
            content_metadata_fingerprint,
        )
        object.__setattr__(
            self,
            "registered_at",
            registered_at,
        )
        object.__setattr__(
            self,
            "provider_name",
            provider_name,
        )
        object.__setattr__(
            self,
            "storage_reference",
            storage_reference,
        )
        object.__setattr__(
            self,
            "object_version_reference",
            object_version_reference,
        )
        object.__setattr__(
            self,
            "provider_integrity_reference",
            provider_integrity_reference,
        )
        object.__setattr__(
            self,
            "write_intent_fingerprint",
            write_intent_fingerprint,
        )
        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def to_dict(self) -> dict[str, object]:
        """Return a defensive metadata-only canonical serialization."""
        return {
            "tenant_id": self.tenant_id,
            "case_matter_id": self.case_matter_id,
            "document_id": self.document_id,
            "content_reference": self.content_reference,
            "media_type": self.media_type,
            "original_filename": self.original_filename,
            "content_length": self.content_length,
            "content_fingerprint": self.content_fingerprint,
            "content_metadata_fingerprint": self.content_metadata_fingerprint,
            "registered_at": self.registered_at,
            "provider_name": self.provider_name,
            "storage_reference": self.storage_reference,
            "object_version_reference": self.object_version_reference,
            "provider_integrity_reference": self.provider_integrity_reference,
            "write_intent_fingerprint": self.write_intent_fingerprint,
            "schema": self.schema,
            "object_metadata_version": self.object_metadata_version,
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: Mapping[str, object],
    ) -> LegalEvidenceObjectMetadata:
        """Hydrate only the exact frozen C1 serialized surface."""
        if not isinstance(value, Mapping):
            raise LegalEvidenceObjectMetadataError(
                "L10A2R_C1_SERIALIZED_VALUE_INVALID"
            )

        payload = dict(value)

        if set(payload) != set(_FIELDS):
            raise LegalEvidenceObjectMetadataError(
                "L10A2R_C1_SERIALIZED_SCHEMA_INVALID"
            )

        return cls(
            tenant_id=payload["tenant_id"],  # type: ignore[arg-type]
            case_matter_id=payload["case_matter_id"],  # type: ignore[arg-type]
            document_id=payload["document_id"],  # type: ignore[arg-type]
            content_reference=payload["content_reference"],  # type: ignore[arg-type]
            media_type=payload["media_type"],  # type: ignore[arg-type]
            original_filename=payload["original_filename"],  # type: ignore[arg-type]
            content_length=payload["content_length"],  # type: ignore[arg-type]
            content_fingerprint=payload["content_fingerprint"],  # type: ignore[arg-type]
            content_metadata_fingerprint=payload[
                "content_metadata_fingerprint"
            ],  # type: ignore[arg-type]
            registered_at=payload["registered_at"],  # type: ignore[arg-type]
            provider_name=payload["provider_name"],  # type: ignore[arg-type]
            storage_reference=payload["storage_reference"],  # type: ignore[arg-type]
            object_version_reference=payload[
                "object_version_reference"
            ],  # type: ignore[arg-type]
            provider_integrity_reference=payload[
                "provider_integrity_reference"
            ],  # type: ignore[arg-type]
            write_intent_fingerprint=payload[
                "write_intent_fingerprint"
            ],  # type: ignore[arg-type]
            schema=payload["schema"],  # type: ignore[arg-type]
            object_metadata_version=payload[
                "object_metadata_version"
            ],  # type: ignore[arg-type]
            fingerprint=payload["fingerprint"],  # type: ignore[arg-type]
        )


def bind_legal_evidence_object_metadata(
    *,
    content: LegalEvidenceContent,
    intent: LegalEvidenceBinaryWriteIntent,
    object_evidence: LegalEvidenceBinaryObjectEvidence,
) -> LegalEvidenceObjectMetadata:
    """Bind canonical content to exact verified provider object evidence."""
    if type(content) is not LegalEvidenceContent:
        raise LegalEvidenceObjectMetadataError(
            "L10A2R_C1_CONTENT_REQUIRED"
        )

    if type(intent) is not LegalEvidenceBinaryWriteIntent:
        raise LegalEvidenceObjectMetadataError(
            "L10A2R_C1_WRITE_INTENT_REQUIRED"
        )

    if type(object_evidence) is not LegalEvidenceBinaryObjectEvidence:
        raise LegalEvidenceObjectMetadataError(
            "L10A2R_C1_OBJECT_EVIDENCE_REQUIRED"
        )

    if (
        intent.tenant_id != content.tenant_id
        or intent.case_matter_id != content.case_matter_id
        or intent.document_id != content.document_id
    ):
        raise LegalEvidenceObjectMetadataError(
            "L10A2R_C1_INTENT_SCOPE_MISMATCH"
        )

    if (
        intent.media_type != content.media_type
        or intent.original_filename != content.original_filename
    ):
        raise LegalEvidenceObjectMetadataError(
            "L10A2R_C1_INTENT_CONTENT_MISMATCH"
        )

    if content.content_length > intent.admitted_max_content_length:
        raise LegalEvidenceObjectMetadataError(
            "L10A2R_C1_INTENT_CONTENT_MISMATCH"
        )

    try:
        validate_object_evidence_for_intent(
            intent=intent,
            evidence=object_evidence,
        )
    except LegalEvidenceBinaryStoragePortError as error:
        raise LegalEvidenceObjectMetadataError(
            "L10A2R_C1_OBJECT_SCOPE_MISMATCH"
        ) from error

    if not object_evidence.proves_stream(
        observed_length=content.content_length,
        observed_fingerprint=content.content_fingerprint,
    ):
        raise LegalEvidenceObjectMetadataError(
            "L10A2R_C1_OBJECT_CONTENT_MISMATCH"
        )

    return LegalEvidenceObjectMetadata(
        tenant_id=content.tenant_id,
        case_matter_id=content.case_matter_id,
        document_id=content.document_id,
        content_reference=content.content_reference,
        media_type=content.media_type,
        original_filename=content.original_filename,
        content_length=content.content_length,
        content_fingerprint=content.content_fingerprint,
        content_metadata_fingerprint=content.fingerprint,
        registered_at=content.registered_at,
        provider_name=object_evidence.provider_name,
        storage_reference=object_evidence.storage_reference,
        object_version_reference=object_evidence.object_version_reference,
        provider_integrity_reference=(
            object_evidence.provider_integrity_reference
        ),
        write_intent_fingerprint=intent.fingerprint,
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalEvidenceObjectMetadata",
    "LegalEvidenceObjectMetadataError",
    "bind_legal_evidence_object_metadata",
]


# ARTIFACT: legal_evidence_object_metadata.py
# VERSION: v1.0.0-L10A2R-C1-LEGAL-EVIDENCE-OBJECT-METADATA
# AUTHORITY BOUNDARY: canonical metadata/object-evidence binding only
# CONTROL-PLANE POSTURE: serialized surface contains no raw binary body
# OBJECT-PLANE POSTURE: provider evidence remains evidence only
# INTEGRITY POSTURE: WILSY SHA3-512 content identity remains canonical
# AVAILABILITY POSTURE: metadata binding does not authorize availability
# RESERVATION POSTURE: no reservation lifecycle mutation exists here
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
