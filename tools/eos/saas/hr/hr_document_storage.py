"""TITLE: WILSY OS HR Document Binary Storage Port.
VERSION: v1.0.0-P0-C12F2A-HR-DOCUMENT-BINARY-STORAGE-PORT
AUTHORITY: Provider-neutral binary transport/storage evidence for HR documents.
EPITOME: Defines immutable HR binary write scope, bounded streaming
SHA3-512 identity, exact byte accounting, opaque provider session and
completion evidence, and provider-neutral lifecycle operations without
granting HR IAM, employment, payroll, billing or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/hr/hr_document_storage.py
CERTIFICATION/UPDATE DATE: 2026-10-04.
CHANGELOG:
2026-10-04 v1.0.0-P0-C12F2A-HR-DOCUMENT-BINARY-STORAGE-PORT
establishes the HR-specific authority-stateless binary storage seam.
SECURITY / PRIVACY POSTURE: No provider credentials, URLs, presigned
material, IAM grants or caller-created business authority are exposed.
TENANT BOUNDARY: Every provider session/object observation is sealed to
exact tenant, employee, document, document-version and ingestion scope.
AUTHORITY BOUNDARY: Storage evidence only. Tenant/employee coordinates
are scope data and never constitute authorization.
FINANCIAL AUTHORITY BOUNDARY: No pricing, billing, payment execution or
settlement authority. Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Provider object operations are outside MongoDB
transactions; higher orchestration must reconcile byte and metadata truth.
FAIL-CLOSED DECLARATION: malformed scope, pseudo tenants, forged
fingerprints, invalid chunks, non-contiguous sequence, byte-count
divergence and SHA3-512 divergence reject.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
import re
from typing import Final, Protocol, runtime_checkable


VERSION: Final[str] = (
    "v1.0.0-P0-C12F2A-HR-DOCUMENT-BINARY-STORAGE-PORT"
)

HR_DOCUMENT_BINARY_STORAGE_SCHEMA: Final[str] = (
    "WILSY-HR-DOCUMENT-BINARY-STORAGE/V1"
)

MAX_STREAM_CHUNK_BYTES: Final[int] = (
    16 * 1024 * 1024
)

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$"
)

_HEX: Final[frozenset[str]] = frozenset(
    "0123456789abcdef"
)

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({
    "default",
    "global",
    "global_root",
    "root",
    "master",
    "*",
})


class HrDocumentBinaryStoragePortError(ValueError):
    """Stable fail-closed HR binary-storage contract error."""


def _text(
    name: str,
    value: object,
    *,
    limit: int = 512,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(
            ord(character) < 32
            for character in value
        )
    ):
        raise HrDocumentBinaryStoragePortError(
            f"P0_C12F2A_{name.upper()}_INVALID"
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

    if _IDENTITY.fullmatch(
        normalized
    ) is None:
        raise HrDocumentBinaryStoragePortError(
            f"P0_C12F2A_{name.upper()}_INVALID"
        )

    return normalized


def _tenant(
    value: object,
) -> str:
    tenant_id = _identity(
        "tenant_id",
        value,
    )

    if (
        tenant_id.casefold()
        in _FORBIDDEN_TENANTS
    ):
        raise HrDocumentBinaryStoragePortError(
            "P0_C12F2A_TENANT_REQUIRED"
        )

    return tenant_id


def _positive_int(
    name: str,
    value: object,
) -> int:
    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
        or value <= 0
    ):
        raise HrDocumentBinaryStoragePortError(
            f"P0_C12F2A_{name.upper()}_INVALID"
        )

    return value


def _non_negative_int(
    name: str,
    value: object,
) -> int:
    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
        or value < 0
    ):
        raise HrDocumentBinaryStoragePortError(
            f"P0_C12F2A_{name.upper()}_INVALID"
        )

    return value


def _sha3(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or len(value) != 128
        or any(
            character not in _HEX
            for character in value
        )
    ):
        raise HrDocumentBinaryStoragePortError(
            f"P0_C12F2A_{name.upper()}_INVALID"
        )

    return value


def _intent_fingerprint(
    *,
    tenant_id: str,
    employee_id: str,
    document_id: str,
    document_version_id: str,
    ingestion_reference: str,
    media_type: str,
    original_filename: str,
    admitted_max_content_length: int,
) -> str:
    payload = {
        "schema": HR_DOCUMENT_BINARY_STORAGE_SCHEMA,
        "tenant_id": tenant_id,
        "employee_id": employee_id,
        "document_id": document_id,
        "document_version_id": document_version_id,
        "ingestion_reference": ingestion_reference,
        "media_type": media_type,
        "original_filename": original_filename,
        "admitted_max_content_length": admitted_max_content_length,
    }

    raw = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        raw
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class HrDocumentBinaryWriteIntent:
    """Immutable provider-neutral coordinates for one HR byte write."""

    tenant_id: str
    employee_id: str
    document_id: str
    document_version_id: str
    ingestion_reference: str
    media_type: str
    original_filename: str
    admitted_max_content_length: int
    schema: str = HR_DOCUMENT_BINARY_STORAGE_SCHEMA
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        tenant = _tenant(
            self.tenant_id
        )

        employee = _identity(
            "employee_id",
            self.employee_id,
        )

        document = _identity(
            "document_id",
            self.document_id,
        )

        version = _identity(
            "document_version_id",
            self.document_version_id,
        )

        ingestion = _identity(
            "ingestion_reference",
            self.ingestion_reference,
        )

        media = _text(
            "media_type",
            self.media_type,
            limit=128,
        ).lower()

        filename = _text(
            "original_filename",
            self.original_filename,
            limit=255,
        )

        admitted = _positive_int(
            "admitted_max_content_length",
            self.admitted_max_content_length,
        )

        if (
            self.schema
            != HR_DOCUMENT_BINARY_STORAGE_SCHEMA
        ):
            raise HrDocumentBinaryStoragePortError(
                "P0_C12F2A_SCHEMA_INVALID"
            )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "employee_id",
            employee,
        )
        object.__setattr__(
            self,
            "document_id",
            document,
        )
        object.__setattr__(
            self,
            "document_version_id",
            version,
        )
        object.__setattr__(
            self,
            "ingestion_reference",
            ingestion,
        )
        object.__setattr__(
            self,
            "media_type",
            media,
        )
        object.__setattr__(
            self,
            "original_filename",
            filename,
        )
        object.__setattr__(
            self,
            "admitted_max_content_length",
            admitted,
        )

        digest = _intent_fingerprint(
            tenant_id=tenant,
            employee_id=employee,
            document_id=document,
            document_version_id=version,
            ingestion_reference=ingestion,
            media_type=media,
            original_filename=filename,
            admitted_max_content_length=admitted,
        )

        if (
            self.fingerprint
            and (
                not isinstance(
                    self.fingerprint,
                    str,
                )
                or not hmac.compare_digest(
                    self.fingerprint,
                    digest,
                )
            )
        ):
            raise HrDocumentBinaryStoragePortError(
                "P0_C12F2A_WRITE_INTENT_FINGERPRINT_MISMATCH"
            )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class HrDocumentBinaryWriteSession:
    """Opaque provider session evidence."""

    provider_name: str
    write_session_reference: str
    storage_reference: str
    write_intent_fingerprint: str

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "provider_name",
            _identity(
                "provider_name",
                self.provider_name,
            ),
        )

        object.__setattr__(
            self,
            "write_session_reference",
            _text(
                "write_session_reference",
                self.write_session_reference,
                limit=1024,
            ),
        )

        object.__setattr__(
            self,
            "storage_reference",
            _text(
                "storage_reference",
                self.storage_reference,
                limit=2048,
            ),
        )

        object.__setattr__(
            self,
            "write_intent_fingerprint",
            _sha3(
                "write_intent_fingerprint",
                self.write_intent_fingerprint,
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class HrDocumentBinaryChunkEvidence:
    """Opaque provider acceptance evidence for one ordered chunk."""

    sequence: int
    chunk_length: int
    provider_part_reference: str

    def __post_init__(
        self,
    ) -> None:
        sequence = _non_negative_int(
            "sequence",
            self.sequence,
        )

        length = _positive_int(
            "chunk_length",
            self.chunk_length,
        )

        if (
            length
            > MAX_STREAM_CHUNK_BYTES
        ):
            raise HrDocumentBinaryStoragePortError(
                "P0_C12F2A_CHUNK_TOO_LARGE"
            )

        reference = _text(
            "provider_part_reference",
            self.provider_part_reference,
            limit=2048,
        )

        object.__setattr__(
            self,
            "sequence",
            sequence,
        )
        object.__setattr__(
            self,
            "chunk_length",
            length,
        )
        object.__setattr__(
            self,
            "provider_part_reference",
            reference,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class HrDocumentBinaryObjectEvidence:
    """Opaque completed-object evidence plus WILSY content identity."""

    provider_name: str
    storage_reference: str
    object_version_reference: str
    provider_integrity_reference: str
    write_intent_fingerprint: str
    content_length: int
    content_fingerprint: str

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "provider_name",
            _identity(
                "provider_name",
                self.provider_name,
            ),
        )

        object.__setattr__(
            self,
            "storage_reference",
            _text(
                "storage_reference",
                self.storage_reference,
                limit=2048,
            ),
        )

        object.__setattr__(
            self,
            "object_version_reference",
            _text(
                "object_version_reference",
                self.object_version_reference,
                limit=2048,
            ),
        )

        object.__setattr__(
            self,
            "provider_integrity_reference",
            _text(
                "provider_integrity_reference",
                self.provider_integrity_reference,
                limit=2048,
            ),
        )

        object.__setattr__(
            self,
            "write_intent_fingerprint",
            _sha3(
                "write_intent_fingerprint",
                self.write_intent_fingerprint,
            ),
        )

        object.__setattr__(
            self,
            "content_length",
            _positive_int(
                "content_length",
                self.content_length,
            ),
        )

        object.__setattr__(
            self,
            "content_fingerprint",
            _sha3(
                "content_fingerprint",
                self.content_fingerprint,
            ),
        )

    def proves_stream(
        self,
        *,
        observed_length: int,
        observed_fingerprint: str,
    ) -> bool:
        if (
            isinstance(
                observed_length,
                bool,
            )
            or not isinstance(
                observed_length,
                int,
            )
            or observed_length <= 0
            or not isinstance(
                observed_fingerprint,
                str,
            )
        ):
            return False

        return (
            self.content_length
            == observed_length
            and hmac.compare_digest(
                self.content_fingerprint,
                observed_fingerprint,
            )
        )


class StreamingSHA3512:
    """Incremental immutable SHA3-512 and exact-byte accumulator."""

    __slots__ = (
        "_hasher",
        "_length",
        "_finalized",
    )

    def __init__(
        self,
    ) -> None:
        self._hasher = hashlib.sha3_512()
        self._length = 0
        self._finalized = False

    @property
    def content_length(
        self,
    ) -> int:
        return self._length

    def update(
        self,
        chunk: bytes,
    ) -> None:
        if self._finalized:
            raise HrDocumentBinaryStoragePortError(
                "P0_C12F2A_STREAM_ALREADY_FINALIZED"
            )

        if not isinstance(
            chunk,
            bytes,
        ):
            raise HrDocumentBinaryStoragePortError(
                "P0_C12F2A_STREAM_CHUNK_BYTES_REQUIRED"
            )

        if not chunk:
            raise HrDocumentBinaryStoragePortError(
                "P0_C12F2A_STREAM_CHUNK_EMPTY"
            )

        if (
            len(chunk)
            > MAX_STREAM_CHUNK_BYTES
        ):
            raise HrDocumentBinaryStoragePortError(
                "P0_C12F2A_CHUNK_TOO_LARGE"
            )

        self._hasher.update(
            chunk
        )

        self._length += len(
            chunk
        )

    def finalize(
        self,
    ) -> tuple[int, str]:
        if self._finalized:
            raise HrDocumentBinaryStoragePortError(
                "P0_C12F2A_STREAM_ALREADY_FINALIZED"
            )

        if self._length < 1:
            raise HrDocumentBinaryStoragePortError(
                "P0_C12F2A_STREAM_EMPTY"
            )

        self._finalized = True

        return (
            self._length,
            self._hasher.hexdigest(),
        )


def validate_write_session_for_intent(
    *,
    intent: HrDocumentBinaryWriteIntent,
    session: HrDocumentBinaryWriteSession,
) -> None:
    if (
        type(intent)
        is not HrDocumentBinaryWriteIntent
        or type(session)
        is not HrDocumentBinaryWriteSession
    ):
        raise HrDocumentBinaryStoragePortError(
            "P0_C12F2A_SCOPE_MISMATCH"
        )

    if not hmac.compare_digest(
        session.write_intent_fingerprint,
        intent.fingerprint,
    ):
        raise HrDocumentBinaryStoragePortError(
            "P0_C12F2A_SCOPE_MISMATCH"
        )


def validate_object_evidence_for_intent(
    *,
    intent: HrDocumentBinaryWriteIntent,
    evidence: HrDocumentBinaryObjectEvidence,
) -> None:
    if (
        type(intent)
        is not HrDocumentBinaryWriteIntent
        or type(evidence)
        is not HrDocumentBinaryObjectEvidence
    ):
        raise HrDocumentBinaryStoragePortError(
            "P0_C12F2A_SCOPE_MISMATCH"
        )

    if not hmac.compare_digest(
        evidence.write_intent_fingerprint,
        intent.fingerprint,
    ):
        raise HrDocumentBinaryStoragePortError(
            "P0_C12F2A_SCOPE_MISMATCH"
        )


def validate_completed_binary_object(
    *,
    intent: HrDocumentBinaryWriteIntent,
    chunks: tuple[
        HrDocumentBinaryChunkEvidence,
        ...,
    ],
    evidence: HrDocumentBinaryObjectEvidence,
    observed_length: int,
    observed_fingerprint: str,
) -> None:
    validate_object_evidence_for_intent(
        intent=intent,
        evidence=evidence,
    )

    if not chunks:
        raise HrDocumentBinaryStoragePortError(
            "P0_C12F2A_CHUNK_EVIDENCE_REQUIRED"
        )

    expected_sequence = 0
    total = 0

    for chunk in chunks:
        if (
            type(chunk)
            is not HrDocumentBinaryChunkEvidence
            or chunk.sequence
            != expected_sequence
        ):
            raise HrDocumentBinaryStoragePortError(
                "P0_C12F2A_CHUNK_SEQUENCE_INVALID"
            )

        total += chunk.chunk_length
        expected_sequence += 1

    if (
        total
        != observed_length
    ):
        raise HrDocumentBinaryStoragePortError(
            "P0_C12F2A_BYTE_COUNT_MISMATCH"
        )

    normalized_fingerprint = _sha3(
        "observed_fingerprint",
        observed_fingerprint,
    )

    if not evidence.proves_stream(
        observed_length=observed_length,
        observed_fingerprint=normalized_fingerprint,
    ):
        raise HrDocumentBinaryStoragePortError(
            "P0_C12F2A_CONTENT_FINGERPRINT_MISMATCH"
        )

    if (
        observed_length
        > intent.admitted_max_content_length
    ):
        raise HrDocumentBinaryStoragePortError(
            "P0_C12F2A_ADMITTED_CONTENT_LENGTH_EXCEEDED"
        )


@runtime_checkable
class HrDocumentBinaryStoragePort(
    Protocol
):
    """Authority-stateless provider-neutral HR binary operations."""

    def begin(
        self,
        intent: HrDocumentBinaryWriteIntent,
    ) -> HrDocumentBinaryWriteSession:
        ...

    def write_chunk(
        self,
        intent: HrDocumentBinaryWriteIntent,
        session: HrDocumentBinaryWriteSession,
        *,
        sequence: int,
        chunk: bytes,
    ) -> HrDocumentBinaryChunkEvidence:
        ...

    def complete(
        self,
        intent: HrDocumentBinaryWriteIntent,
        session: HrDocumentBinaryWriteSession,
        chunks: tuple[
            HrDocumentBinaryChunkEvidence,
            ...,
        ],
        *,
        observed_length: int,
        observed_fingerprint: str,
    ) -> HrDocumentBinaryObjectEvidence:
        ...

    def inspect(
        self,
        intent: HrDocumentBinaryWriteIntent,
        evidence: HrDocumentBinaryObjectEvidence,
    ) -> HrDocumentBinaryObjectEvidence:
        ...

    def abort(
        self,
        intent: HrDocumentBinaryWriteIntent,
        session: HrDocumentBinaryWriteSession,
    ) -> None:
        ...


__all__ = [
    "VERSION",
    "HR_DOCUMENT_BINARY_STORAGE_SCHEMA",
    "MAX_STREAM_CHUNK_BYTES",
    "HrDocumentBinaryStoragePortError",
    "HrDocumentBinaryWriteIntent",
    "HrDocumentBinaryWriteSession",
    "HrDocumentBinaryChunkEvidence",
    "HrDocumentBinaryObjectEvidence",
    "StreamingSHA3512",
    "validate_write_session_for_intent",
    "validate_object_evidence_for_intent",
    "validate_completed_binary_object",
    "HrDocumentBinaryStoragePort",
]


# ARTIFACT: tools/eos/saas/hr/hr_document_storage.py
# VERSION: v1.0.0-P0-C12F2A-HR-DOCUMENT-BINARY-STORAGE-PORT
# AUTHORITY BOUNDARY: provider-neutral binary storage evidence only
# TENANT POSTURE: tenant/employee/document/version scope is sealed but confers no IAM authority
# FAIL-CLOSED POSTURE: malformed, forged, non-contiguous, oversized and divergent evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
