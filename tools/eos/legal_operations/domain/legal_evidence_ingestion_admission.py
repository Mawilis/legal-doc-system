"""WILSY OS Legal Evidence pre-provider ingestion admission domain.

TITLE: Legal Evidence Ingestion Admission Domain
VERSION: v1.0.0-L10A2R-C4D5D7-LEGAL-EVIDENCE-INGESTION-ADMISSION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_ingestion_admission.py
COLLABORATION / OWNERSHIP:
    Legal Operations owns this pure pre-provider admission evidence contract.
    ProcessDocument remains the canonical tenant/document/matter source.
    Later capacity, binary-write-intent, provider and commit layers retain
    their separately certified authority boundaries.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.0-L10A2R-C4D5D7 establishes immutable server-issued ingestion
    admission evidence from canonical ProcessDocument scope plus bounded
    pre-provider transport metadata.
COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001-aligned
    integrity and tenant-boundary controls.
SECURITY / PRIVACY POSTURE:
    No provider credentials, storage coordinates, binary content, IAM
    authority or external-system secrets are accepted or emitted. Exact
    canonical ProcessDocument scope is cryptographically bound into the
    admission fingerprint.
TENANT BOUNDARY:
    tenant_id, case_matter_id and document_id are inherited exclusively from
    one exact canonical ProcessDocument. No pseudo/global tenant or
    cross-document substitution is created by this artifact.
AUTHORITY BOUNDARY:
    Immutable pre-provider ingestion-coordinate evidence only. This artifact
    grants no capacity reservation, provider execution, canonical content
    commit, lifecycle, availability, orphan, abort, retention or deletion
    authority.
FINANCIAL AUTHORITY BOUNDARY:
    No pricing, billing, payment, financial execution or settlement authority.
    Kennel EOS remains the exclusive financial execution authority.
PURPOSE:
    Freeze one server-issued Legal Evidence ingestion identity and exact
    pre-provider documentary coordinates from canonical ProcessDocument
    evidence plus bounded transport metadata.

EPITOME:
    CANONICAL PROCESS DOCUMENT
    + BOUNDED TRANSPORT METADATA
    + SERVER-ISSUED INGESTION REFERENCE
    -> IMMUTABLE PRE-PROVIDER ADMISSION EVIDENCE
    != CAPACITY RESERVATION
    != PROVIDER WRITE INTENT
    != PROVIDER EXECUTION
    != CONTENT COMMIT
    != ORPHAN PROOF
    != ABORT AUTHORITY
    != DELETE AUTHORITY

SOURCE AUTHORITY:
    ProcessDocument remains the canonical source of tenant/document/matter
    binding. This artifact does not create, replace or infer matter identity.

INGESTION IDENTITY:
    The ingestion reference is generated inside the factory. No caller may
    supply or override it.

CONTENT METADATA:
    media_type and original_filename are transport metadata frozen before
    provider execution. Their presence here does not prove stored content,
    content identity, legal admissibility or lifecycle state.

CAPACITY BOUNDARY:
    declared_content_length is a bounded pre-provider declaration only. It is
    not commercial-capacity authority and is not admitted_max_content_length.
    Capacity reservation remains separately governed.

TRANSACTION / PROVIDER BOUNDARY:
    Pure domain construction only. No Mongo, provider, S3, HTTP, IAM,
    reconciliation or external I/O occurs here.

FAIL CLOSED:
    Wrong source type, malformed transport metadata, invalid content length,
    invalid time, malformed source fingerprint or reconstruction divergence
    rejects.

"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Final
from uuid import uuid4

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ProcessDocument,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D5D7-LEGAL-EVIDENCE-INGESTION-ADMISSION"
)
SCHEMA: Final[str] = "WILSY-LEGAL-EVIDENCE-INGESTION-ADMISSION/V1"

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$"
)
_HEX: Final[frozenset[str]] = frozenset(
    "0123456789abcdef"
)
_INGESTION_PREFIX: Final[str] = (
    "legal-evidence-ingestion:"
)


class LegalEvidenceIngestionAdmissionError(ValueError):
    """Stable fail-closed ingestion-admission domain error."""


def _text(
    name: str,
    value: object,
    *,
    limit: int,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(
            ord(character) < 32
            for character in value
        )
    ):
        raise LegalEvidenceIngestionAdmissionError(
            f"L10A2R_C4D5D7_{name.upper()}_INVALID"
        )

    return value


def _identity(
    name: str,
    value: object,
) -> str:
    normalized = _text(
        name,
        value,
        limit=256,
    )

    if _IDENTITY.fullmatch(normalized) is None:
        raise LegalEvidenceIngestionAdmissionError(
            f"L10A2R_C4D5D7_{name.upper()}_INVALID"
        )

    return normalized


def _sha3(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 128
        or any(
            character not in _HEX
            for character in value
        )
    ):
        raise LegalEvidenceIngestionAdmissionError(
            f"L10A2R_C4D5D7_{name.upper()}_INVALID"
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
        raise LegalEvidenceIngestionAdmissionError(
            f"L10A2R_C4D5D7_{name.upper()}_INVALID"
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
        raise LegalEvidenceIngestionAdmissionError(
            f"L10A2R_C4D5D7_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _canonical_payload(
    *,
    tenant_id: str,
    case_matter_id: str,
    document_id: str,
    ingestion_reference: str,
    media_type: str,
    original_filename: str,
    declared_content_length: int,
    admitted_at: datetime,
    source_process_document_fingerprint: str,
) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "tenant_id": tenant_id,
        "case_matter_id": case_matter_id,
        "document_id": document_id,
        "ingestion_reference": ingestion_reference,
        "media_type": media_type,
        "original_filename": original_filename,
        "declared_content_length": declared_content_length,
        "admitted_at": admitted_at.isoformat(),
        "source_process_document_fingerprint": (
            source_process_document_fingerprint
        ),
    }


def _fingerprint(
    *,
    tenant_id: str,
    case_matter_id: str,
    document_id: str,
    ingestion_reference: str,
    media_type: str,
    original_filename: str,
    declared_content_length: int,
    admitted_at: datetime,
    source_process_document_fingerprint: str,
) -> str:
    payload = _canonical_payload(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        document_id=document_id,
        ingestion_reference=ingestion_reference,
        media_type=media_type,
        original_filename=original_filename,
        declared_content_length=declared_content_length,
        admitted_at=admitted_at,
        source_process_document_fingerprint=(
            source_process_document_fingerprint
        ),
    )

    raw = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        raw
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
    init=False,
)
class LegalEvidenceIngestionAdmission:
    """Immutable non-authorizing pre-provider ingestion evidence."""

    tenant_id: str
    case_matter_id: str
    document_id: str
    ingestion_reference: str

    media_type: str
    original_filename: str
    declared_content_length: int

    admitted_at: datetime
    source_process_document_fingerprint: str

    schema: str
    admission_version: str
    fingerprint: str

    def __init__(
        self,
        *args: object,
        **kwargs: object,
    ) -> None:
        raise LegalEvidenceIngestionAdmissionError(
            "L10A2R_C4D5D7_FACTORY_REQUIRED"
        )

    @classmethod
    def issue(
        cls,
        *,
        process_document: ProcessDocument,
        media_type: str,
        original_filename: str,
        declared_content_length: int,
        admitted_at: datetime,
    ) -> "LegalEvidenceIngestionAdmission":
        """Issue one server-owned ingestion identity from canonical document."""

        if type(process_document) is not ProcessDocument:
            raise LegalEvidenceIngestionAdmissionError(
                "L10A2R_C4D5D7_PROCESS_DOCUMENT_REQUIRED"
            )

        tenant = _identity(
            "tenant_id",
            process_document.tenant_id,
        )
        matter = _identity(
            "case_matter_id",
            process_document.case_matter_id,
        )
        document = _identity(
            "document_id",
            process_document.document_id,
        )

        source_fingerprint = _sha3(
            "source_process_document_fingerprint",
            process_document.fingerprint,
        )

        media = _text(
            "media_type",
            media_type,
            limit=128,
        ).lower()

        filename = _text(
            "original_filename",
            original_filename,
            limit=255,
        )

        length = _positive_int(
            "declared_content_length",
            declared_content_length,
        )

        observed = _utc(
            "admitted_at",
            admitted_at,
        )

        ingestion_reference = _identity(
            "ingestion_reference",
            _INGESTION_PREFIX + uuid4().hex,
        )

        digest = _fingerprint(
            tenant_id=tenant,
            case_matter_id=matter,
            document_id=document,
            ingestion_reference=ingestion_reference,
            media_type=media,
            original_filename=filename,
            declared_content_length=length,
            admitted_at=observed,
            source_process_document_fingerprint=(
                source_fingerprint
            ),
        )

        value = object.__new__(
            cls
        )

        object.__setattr__(
            value,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            value,
            "case_matter_id",
            matter,
        )
        object.__setattr__(
            value,
            "document_id",
            document,
        )
        object.__setattr__(
            value,
            "ingestion_reference",
            ingestion_reference,
        )
        object.__setattr__(
            value,
            "media_type",
            media,
        )
        object.__setattr__(
            value,
            "original_filename",
            filename,
        )
        object.__setattr__(
            value,
            "declared_content_length",
            length,
        )
        object.__setattr__(
            value,
            "admitted_at",
            observed,
        )
        object.__setattr__(
            value,
            "source_process_document_fingerprint",
            source_fingerprint,
        )
        object.__setattr__(
            value,
            "schema",
            SCHEMA,
        )
        object.__setattr__(
            value,
            "admission_version",
            VERSION,
        )
        object.__setattr__(
            value,
            "fingerprint",
            digest,
        )

        return value

    def verify(self) -> None:
        """Recompute the canonical fingerprint and reject divergence."""

        expected = _fingerprint(
            tenant_id=_identity(
                "tenant_id",
                self.tenant_id,
            ),
            case_matter_id=_identity(
                "case_matter_id",
                self.case_matter_id,
            ),
            document_id=_identity(
                "document_id",
                self.document_id,
            ),
            ingestion_reference=_identity(
                "ingestion_reference",
                self.ingestion_reference,
            ),
            media_type=_text(
                "media_type",
                self.media_type,
                limit=128,
            ).lower(),
            original_filename=_text(
                "original_filename",
                self.original_filename,
                limit=255,
            ),
            declared_content_length=_positive_int(
                "declared_content_length",
                self.declared_content_length,
            ),
            admitted_at=_utc(
                "admitted_at",
                self.admitted_at,
            ),
            source_process_document_fingerprint=_sha3(
                "source_process_document_fingerprint",
                self.source_process_document_fingerprint,
            ),
        )

        if (
            self.schema != SCHEMA
            or self.admission_version != VERSION
            or not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(
                self.fingerprint,
                expected,
            )
        ):
            raise LegalEvidenceIngestionAdmissionError(
                "L10A2R_C4D5D7_ADMISSION_FINGERPRINT_INVALID"
            )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalEvidenceIngestionAdmission",
    "LegalEvidenceIngestionAdmissionError",
]


# ARTIFACT: legal_evidence_ingestion_admission.py
# VERSION: v1.0.0-L10A2R-C4D5D7-LEGAL-EVIDENCE-INGESTION-ADMISSION
# AUTHORITY BOUNDARY: immutable pre-provider ingestion-coordinate evidence only
# TENANT POSTURE: exact canonical ProcessDocument tenant/document/matter scope only
# FAIL-CLOSED POSTURE: malformed source, metadata, length, time or fingerprint rejects
# SOURCE POSTURE: ProcessDocument exclusively supplies tenant/document/matter binding
# IDENTITY POSTURE: ingestion reference is factory-generated and caller cannot override it
# METADATA POSTURE: media type and original filename are bounded pre-provider transport metadata
# CAPACITY POSTURE: declared length grants no reservation or commercial authority
# PROVIDER POSTURE: no provider execution or provider locator authority
# COMMIT POSTURE: no canonical content or metadata commit authority
# ORPHAN POSTURE: no orphan proof
# ABORT POSTURE: no provider-abort authority
# DELETION POSTURE: no provider-delete authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
