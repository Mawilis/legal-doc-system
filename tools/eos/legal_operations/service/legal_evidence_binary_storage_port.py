"""WILSY OS provider-neutral Legal Evidence binary-storage port.

TITLE: Legal Evidence Binary Storage Port
VERSION: v1.2.0-L10A2R-A2-LEGAL-EVIDENCE-BINARY-STORAGE-PORT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Define the fail-closed provider-neutral contract by which bounded
         streamed Legal Evidence bytes may be written, verified, completed,
         inspected and aborted without making any provider canonical business
         truth or requiring whole-object materialization in Python memory.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_binary_storage_port.py
COLLABORATION / OWNERSHIP: L10A1 owns immutable Legal Evidence content identity.
                            L10A2 currently owns legacy Mongo inline-byte
                            persistence and requires later migration. L10A2Q
                            owns commercial-capacity architecture. This artifact
                            owns only the provider-neutral binary-storage seam.
                            Future certified adapters own provider execution.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: v1.2.0-L10A2R-A2 cryptographically binds each provider write
           session and completed object observation to the exact tenant-scoped
           WILSY write intent so identical binary content cannot cause
           cross-intent, cross-document or cross-tenant provider evidence to be
           accepted.
           v1.1.0-L10A2R-A1 removed the pre-stream canonical-content
           fingerprint/reference dependency so WILSY derives exact SHA3-512
           identity only from bytes actually observed during streaming. A
           server-owned ingestion reference begins provisional provider
           storage; canonical LegalEvidenceContent identity is created only
           after verified completion.
           v1.0.0-L10A2R-A established opaque write-session identity,
           immutable write intent, ordered streaming chunk evidence, completed
           object evidence, verified object observations, deterministic
           SHA3-512 streaming identity, exact byte accounting, abort semantics
           and a provider-neutral Protocol with no AWS/S3/GCS/Azure dependency.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No provider credentials, bucket names, URLs,
                             presigned material or caller-controlled storage
                             locators are exposed by this contract. ETag-like
                             provider evidence is opaque and is never treated
                             as WILSY content identity.
TENANT BOUNDARY: Every write and provider observation is bound to one explicit
                 tenant, case matter, process document and server-owned
                 ingestion reference. Canonical content-reference identity is
                 derived only after verified streaming. No pseudo/global tenant
                 exists.
AUTHORITY BOUNDARY: Binary transport/storage evidence only. It grants no Legal
                    lifecycle, custody, Court filing, service, client
                    visibility, IAM, AI, commercial-capacity or retention
                    execution authority.
FINANCIAL AUTHORITY BOUNDARY: No pricing, invoicing, payment, execution or
                               settlement authority. Kennel EOS remains
                               exclusive financial execution authority.
TRANSACTION BOUNDARY: Object-storage operations are outside Mongo transactions.
                      This port creates no false distributed transaction.
                      Higher orchestration must reconcile provider execution
                      with canonical Mongo metadata using explicit evidence.
FAIL-CLOSED DECLARATION: Invalid scope, malformed identities, empty/oversized
                         chunks, non-contiguous chunk sequence, byte-count
                         divergence, SHA3-512 mismatch, provider observation
                         divergence and unknown completion evidence reject.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
import re
from typing import Final, Protocol, runtime_checkable


VERSION: Final[str] = "v1.2.0-L10A2R-A2-LEGAL-EVIDENCE-BINARY-STORAGE-PORT"
SCHEMA: Final[str] = "WILSY-LEGAL-EVIDENCE-BINARY-STORAGE/V1"

# Transport chunk ceiling only. This is deliberately not the commercial
# single-file ceiling and does not limit total object size.
MAX_STREAM_CHUNK_BYTES: Final[int] = 16 * 1024 * 1024

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$"
)
_HEX: Final[frozenset[str]] = frozenset("0123456789abcdef")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalEvidenceBinaryStoragePortError(ValueError):
    """Stable fail-closed binary-storage contract error."""


def _text(name: str, value: object, *, limit: int = 512) -> str:
    """Require one exact bounded non-empty string without coercion."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 32 for character in value)
    ):
        raise LegalEvidenceBinaryStoragePortError(
            f"L10A2R_A_{name.upper()}_INVALID"
        )
    return value


def _identity(name: str, value: object) -> str:
    """Require one bounded opaque identity."""
    normalized = _text(name, value, limit=256)
    if _IDENTITY.fullmatch(normalized) is None:
        raise LegalEvidenceBinaryStoragePortError(
            f"L10A2R_A_{name.upper()}_INVALID"
        )
    return normalized


def _tenant(value: object) -> str:
    """Require one explicit non-pseudo tenant identity."""
    tenant_id = _identity("tenant_id", value)
    if tenant_id.casefold() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceBinaryStoragePortError(
            "L10A2R_A_TENANT_REQUIRED"
        )
    return tenant_id


def _positive_int(name: str, value: object) -> int:
    """Require one strictly positive integer."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise LegalEvidenceBinaryStoragePortError(
            f"L10A2R_A_{name.upper()}_INVALID"
        )
    return value


def _non_negative_int(name: str, value: object) -> int:
    """Require one non-negative integer."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise LegalEvidenceBinaryStoragePortError(
            f"L10A2R_A_{name.upper()}_INVALID"
        )
    return value


def _sha3(name: str, value: object) -> str:
    """Require canonical lowercase SHA3-512 hexadecimal evidence."""
    if (
        not isinstance(value, str)
        or len(value) != 128
        or any(character not in _HEX for character in value)
    ):
        raise LegalEvidenceBinaryStoragePortError(
            f"L10A2R_A_{name.upper()}_INVALID"
        )
    return value


def _write_intent_fingerprint(
    *,
    tenant_id: str,
    case_matter_id: str,
    document_id: str,
    ingestion_reference: str,
    media_type: str,
    original_filename: str,
    admitted_max_content_length: int,
) -> str:
    """Seal exact WILSY write coordinates with deterministic SHA3-512."""
    payload = {
        "schema": SCHEMA,
        "tenant_id": tenant_id,
        "case_matter_id": case_matter_id,
        "document_id": document_id,
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
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalEvidenceBinaryWriteIntent:
    """Immutable WILSY-owned coordinates for one binary object write.

    This intent is provider-neutral. It is not permission, entitlement,
    capacity reservation, lifecycle evidence, retention authority or proof that
    any object has actually been stored.
    """

    tenant_id: str
    case_matter_id: str
    document_id: str
    ingestion_reference: str
    media_type: str
    original_filename: str
    admitted_max_content_length: int
    schema: str = SCHEMA
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        matter = _identity("case_matter_id", self.case_matter_id)
        document = _identity("document_id", self.document_id)
        ingestion_reference = _identity(
            "ingestion_reference",
            self.ingestion_reference,
        )
        media = _text("media_type", self.media_type, limit=128).lower()
        filename = _text("original_filename", self.original_filename, limit=255)
        admitted_max = _positive_int(
            "admitted_max_content_length",
            self.admitted_max_content_length,
        )

        if self.schema != SCHEMA:
            raise LegalEvidenceBinaryStoragePortError(
                "L10A2R_A_SCHEMA_INVALID"
            )

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "case_matter_id", matter)
        object.__setattr__(self, "document_id", document)
        object.__setattr__(
            self,
            "ingestion_reference",
            ingestion_reference,
        )
        object.__setattr__(self, "media_type", media)
        object.__setattr__(self, "original_filename", filename)
        object.__setattr__(
            self,
            "admitted_max_content_length",
            admitted_max,
        )

        digest = _write_intent_fingerprint(
            tenant_id=tenant,
            case_matter_id=matter,
            document_id=document,
            ingestion_reference=ingestion_reference,
            media_type=media,
            original_filename=filename,
            admitted_max_content_length=admitted_max,
        )
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            raise LegalEvidenceBinaryStoragePortError(
                "L10A2R_A_WRITE_INTENT_FINGERPRINT_MISMATCH"
            )
        object.__setattr__(self, "fingerprint", digest)


@dataclass(frozen=True, slots=True)
class LegalEvidenceBinaryWriteSession:
    """Opaque provider write-session evidence returned after begin.

    The session reference is adapter-owned capability material and must never be
    accepted directly from an HTTP caller.
    """

    provider_name: str
    write_session_reference: str
    storage_reference: str
    write_intent_fingerprint: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provider_name",
            _identity("provider_name", self.provider_name),
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
            _text("storage_reference", self.storage_reference, limit=2048),
        )
        object.__setattr__(
            self,
            "write_intent_fingerprint",
            _sha3(
                "write_intent_fingerprint",
                self.write_intent_fingerprint,
            ),
        )


@dataclass(frozen=True, slots=True)
class LegalEvidenceBinaryChunkEvidence:
    """Provider evidence that one ordered stream chunk was accepted."""

    sequence: int
    chunk_length: int
    provider_part_reference: str

    def __post_init__(self) -> None:
        sequence = _non_negative_int("sequence", self.sequence)
        length = _positive_int("chunk_length", self.chunk_length)
        if length > MAX_STREAM_CHUNK_BYTES:
            raise LegalEvidenceBinaryStoragePortError(
                "L10A2R_A_CHUNK_TOO_LARGE"
            )
        reference = _text(
            "provider_part_reference",
            self.provider_part_reference,
            limit=2048,
        )

        object.__setattr__(self, "sequence", sequence)
        object.__setattr__(self, "chunk_length", length)
        object.__setattr__(self, "provider_part_reference", reference)


@dataclass(frozen=True, slots=True)
class LegalEvidenceBinaryObjectEvidence:
    """Opaque provider completion evidence for one stored object version.

    ``provider_integrity_reference`` may be an ETag, checksum reference or
    another provider-native value. It is evidence only and is never substituted
    for WILSY SHA3-512 content identity.
    """

    provider_name: str
    storage_reference: str
    object_version_reference: str
    provider_integrity_reference: str
    write_intent_fingerprint: str
    content_length: int
    content_fingerprint: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provider_name",
            _identity("provider_name", self.provider_name),
        )
        object.__setattr__(
            self,
            "storage_reference",
            _text("storage_reference", self.storage_reference, limit=2048),
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
            _positive_int("content_length", self.content_length),
        )
        object.__setattr__(
            self,
            "content_fingerprint",
            _sha3("content_fingerprint", self.content_fingerprint),
        )

    def proves_stream(
        self,
        *,
        observed_length: int,
        observed_fingerprint: str,
    ) -> bool:
        """Return whether provider completion matches WILSY-observed stream."""
        if (
            isinstance(observed_length, bool)
            or not isinstance(observed_length, int)
            or observed_length <= 0
            or not isinstance(observed_fingerprint, str)
        ):
            return False
        return (
            self.content_length == observed_length
            and hmac.compare_digest(
                self.content_fingerprint,
                observed_fingerprint,
            )
        )


class StreamingSHA3512:
    """Incrementally derive SHA3-512 and exact length without whole-object RAM.

    The accumulator owns no storage or lifecycle authority. It accepts chunks
    once, rejects empty/oversized chunks and becomes immutable after finalize.
    """

    __slots__ = ("_hasher", "_length", "_finalized")

    def __init__(self) -> None:
        self._hasher = hashlib.sha3_512()
        self._length = 0
        self._finalized = False

    @property
    def content_length(self) -> int:
        """Return exact bytes accepted so far."""
        return self._length

    def update(self, chunk: bytes) -> None:
        """Consume one bounded non-empty bytes chunk exactly once."""
        if self._finalized:
            raise LegalEvidenceBinaryStoragePortError(
                "L10A2R_A_STREAM_ALREADY_FINALIZED"
            )
        if not isinstance(chunk, bytes):
            raise LegalEvidenceBinaryStoragePortError(
                "L10A2R_A_STREAM_CHUNK_BYTES_REQUIRED"
            )
        if not chunk:
            raise LegalEvidenceBinaryStoragePortError(
                "L10A2R_A_STREAM_CHUNK_EMPTY"
            )
        if len(chunk) > MAX_STREAM_CHUNK_BYTES:
            raise LegalEvidenceBinaryStoragePortError(
                "L10A2R_A_CHUNK_TOO_LARGE"
            )

        self._hasher.update(chunk)
        self._length += len(chunk)

    def finalize(self) -> tuple[int, str]:
        """Finalize once and return exact byte count plus SHA3-512 identity."""
        if self._finalized:
            raise LegalEvidenceBinaryStoragePortError(
                "L10A2R_A_STREAM_ALREADY_FINALIZED"
            )
        if self._length < 1:
            raise LegalEvidenceBinaryStoragePortError(
                "L10A2R_A_STREAM_EMPTY"
            )

        self._finalized = True
        return self._length, self._hasher.hexdigest()


def validate_completed_binary_object(
    *,
    intent: LegalEvidenceBinaryWriteIntent,
    chunks: tuple[LegalEvidenceBinaryChunkEvidence, ...],
    observed_length: int,
    observed_fingerprint: str,
    completed: LegalEvidenceBinaryObjectEvidence,
) -> None:
    """Fail closed unless stream and provider completion correlate exactly.

    The function deliberately does not infer provider success from an ETag or
    storage locator. WILSY's independently accumulated byte count and SHA3-512
    are authoritative content observations. The byte count must remain within
    the already-admitted maximum and must match completed provider evidence.
    Canonical Legal evidence content identity is created only after this gate.
    """
    if type(intent) is not LegalEvidenceBinaryWriteIntent:
        raise LegalEvidenceBinaryStoragePortError(
            "L10A2R_A_WRITE_INTENT_REQUIRED"
        )
    if type(completed) is not LegalEvidenceBinaryObjectEvidence:
        raise LegalEvidenceBinaryStoragePortError(
            "L10A2R_A_COMPLETION_EVIDENCE_REQUIRED"
        )
    if not isinstance(chunks, tuple) or not chunks:
        raise LegalEvidenceBinaryStoragePortError(
            "L10A2R_A_CHUNK_EVIDENCE_REQUIRED"
        )

    total = 0
    for expected_sequence, chunk in enumerate(chunks):
        if type(chunk) is not LegalEvidenceBinaryChunkEvidence:
            raise LegalEvidenceBinaryStoragePortError(
                "L10A2R_A_CHUNK_EVIDENCE_INVALID"
            )
        if chunk.sequence != expected_sequence:
            raise LegalEvidenceBinaryStoragePortError(
                "L10A2R_A_CHUNK_SEQUENCE_INVALID"
            )
        total += chunk.chunk_length

    length = _positive_int("observed_length", observed_length)
    fingerprint = _sha3("observed_fingerprint", observed_fingerprint)

    if (
        total != length
        or length > intent.admitted_max_content_length
        or not hmac.compare_digest(
            completed.write_intent_fingerprint,
            intent.fingerprint,
        )
        or completed.content_length != length
        or not hmac.compare_digest(
            completed.content_fingerprint,
            fingerprint,
        )
        or not completed.proves_stream(
            observed_length=length,
            observed_fingerprint=fingerprint,
        )
    ):
        raise LegalEvidenceBinaryStoragePortError(
            "L10A2R_A_BINARY_CORRELATION_INVALID"
        )


@runtime_checkable
class LegalEvidenceBinaryStoragePort(Protocol):
    """Provider-neutral execution contract for one Legal Evidence binary write.

    Implementations may use multipart object storage, another certified remote
    binary store or a deterministic test adapter. Provider credentials and
    configuration remain adapter-private.
    """

    def begin(
        self,
        intent: LegalEvidenceBinaryWriteIntent,
    ) -> LegalEvidenceBinaryWriteSession:
        """Begin one provider write for exact server-derived WILSY intent."""
        ...

    def write_chunk(
        self,
        session: LegalEvidenceBinaryWriteSession,
        *,
        sequence: int,
        chunk: bytes,
    ) -> LegalEvidenceBinaryChunkEvidence:
        """Write one ordered bounded chunk and return opaque provider evidence."""
        ...

    def complete(
        self,
        session: LegalEvidenceBinaryWriteSession,
        *,
        chunks: tuple[LegalEvidenceBinaryChunkEvidence, ...],
        content_length: int,
        content_fingerprint: str,
    ) -> LegalEvidenceBinaryObjectEvidence:
        """Complete the provider write and return immutable object evidence."""
        ...

    def inspect(
        self,
        evidence: LegalEvidenceBinaryObjectEvidence,
    ) -> LegalEvidenceBinaryObjectEvidence:
        """Re-read provider object evidence without downloading whole content."""
        ...

    def abort(
        self,
        session: LegalEvidenceBinaryWriteSession,
    ) -> None:
        """Abort one incomplete provider write without claiming object deletion."""
        ...


__all__ = [
    "MAX_STREAM_CHUNK_BYTES",
    "SCHEMA",
    "VERSION",
    "LegalEvidenceBinaryChunkEvidence",
    "LegalEvidenceBinaryObjectEvidence",
    "LegalEvidenceBinaryStoragePort",
    "LegalEvidenceBinaryStoragePortError",
    "LegalEvidenceBinaryWriteIntent",
    "LegalEvidenceBinaryWriteSession",
    "StreamingSHA3512",
    "validate_completed_binary_object",
]

# ARTIFACT: legal_evidence_binary_storage_port.py
# VERSION: v1.2.0-L10A2R-A2-LEGAL-EVIDENCE-BINARY-STORAGE-PORT
# AUTHORITY BOUNDARY: provider-neutral Legal Evidence binary transport/storage evidence only
# TENANT POSTURE: exact tenant/matter/document/ingestion coordinates; canonical content identity follows verified streaming
# FAIL-CLOSED POSTURE: scope/write-intent/chunk/sequence/length/SHA3/provider-evidence divergence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
