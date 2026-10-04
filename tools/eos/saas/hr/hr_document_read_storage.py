"""TITLE: WILSY OS HR Document Binary Read Storage Port.
VERSION: v1.0.0-P0-C12F5C-HR-DOCUMENT-READ-PORT
AUTHORITY: Authority-stateless provider-neutral binary retrieval contract.
EPITOME: Binds exact tenant, employee, document, immutable version and
provider coordinates to bounded ordered binary reads with independently
recomputed byte length and SHA3-512 content integrity.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/hr/hr_document_read_storage.py
CERTIFICATION/UPDATE DATE: 2026-10-04.
CHANGELOG:
2026-10-04 v1.0.0-P0-C12F5C-HR-DOCUMENT-READ-PORT
establishes the first sovereign HR binary read contract.
AUTHORITY BOUNDARY: Provider execution contract only. No IAM, business
authorization, registry mutation, HTTP, payroll, billing or financial authority.
WRITE BOUNDARY: The certified write port remains unchanged and independent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import hmac
import json
import re
from typing import Final, Protocol, cast, runtime_checkable


VERSION: Final[str] = (
    "v1.0.0-P0-C12F5C-HR-DOCUMENT-READ-PORT"
)

HR_DOCUMENT_BINARY_READ_SCHEMA: Final[str] = (
    "WILSY-HR-DOCUMENT-BINARY-READ/V1"
)

MAX_READ_CHUNK_BYTES: Final[int] = (
    16 * 1024 * 1024
)

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$"
)

_HEX: Final[frozenset[str]] = frozenset(
    "0123456789abcdef"
)

_PSEUDO_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "*",
        "global",
        "global_root",
        "master",
        "root",
    }
)


class HrDocumentBinaryReadStoragePortError(
    RuntimeError
):
    """Stable fail-closed HR binary read-contract error."""


def _fail(
    code: str,
) -> None:
    raise HrDocumentBinaryReadStoragePortError(
        code
    )


def _identity(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
        or _IDENTITY.fullmatch(
            value
        ) is None
    ):
        _fail(
            f"P0_C12F5C_{name.upper()}_INVALID"
        )

    return cast(
        str,
        value,
    )


def _tenant(
    value: object,
) -> str:
    tenant = _identity(
        "tenant_id",
        value,
    )

    if tenant.casefold() in _PSEUDO_TENANTS:
        _fail(
            "P0_C12F5C_TENANT_ID_INVALID"
        )

    return tenant


def _text(
    name: str,
    value: object,
    *,
    limit: int = 2048,
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
        _fail(
            f"P0_C12F5C_{name.upper()}_INVALID"
        )

    return cast(
        str,
        value,
    )


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
        _fail(
            f"P0_C12F5C_{name.upper()}_INVALID"
        )

    return cast(
        int,
        value,
    )


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
        _fail(
            f"P0_C12F5C_{name.upper()}_INVALID"
        )

    return cast(
        int,
        value,
    )


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
        _fail(
            f"P0_C12F5C_{name.upper()}_INVALID"
        )

    return cast(
        str,
        value,
    )


def _intent_fingerprint(
    *,
    tenant_id: str,
    employee_id: str,
    document_id: str,
    document_version_id: str,
    storage_provider_id: str,
    storage_object_reference: str,
    object_version_reference: str,
    expected_byte_length: int,
    expected_sha3_512: str,
) -> str:
    payload = {
        "schema":
            HR_DOCUMENT_BINARY_READ_SCHEMA,
        "tenant_id":
            tenant_id,
        "employee_id":
            employee_id,
        "document_id":
            document_id,
        "document_version_id":
            document_version_id,
        "storage_provider_id":
            storage_provider_id,
        "storage_object_reference":
            storage_object_reference,
        "object_version_reference":
            object_version_reference,
        "expected_byte_length":
            expected_byte_length,
        "expected_sha3_512":
            expected_sha3_512,
    }

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
)
class HrDocumentBinaryReadIntent:
    tenant_id: str
    employee_id: str
    document_id: str
    document_version_id: str
    storage_provider_id: str
    storage_object_reference: str
    object_version_reference: str
    expected_byte_length: int
    expected_sha3_512: str
    schema: str = (
        HR_DOCUMENT_BINARY_READ_SCHEMA
    )
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        if (
            self.schema
            != HR_DOCUMENT_BINARY_READ_SCHEMA
        ):
            _fail(
                "P0_C12F5C_SCHEMA_INVALID"
            )

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

        provider = _identity(
            "storage_provider_id",
            self.storage_provider_id,
        )

        object_ref = _text(
            "storage_object_reference",
            self.storage_object_reference,
        )

        object_version = _text(
            "object_version_reference",
            self.object_version_reference,
        )

        length = _positive_int(
            "expected_byte_length",
            self.expected_byte_length,
        )

        digest = _sha3(
            "expected_sha3_512",
            self.expected_sha3_512,
        )

        calculated = _intent_fingerprint(
            tenant_id=tenant,
            employee_id=employee,
            document_id=document,
            document_version_id=version,
            storage_provider_id=provider,
            storage_object_reference=object_ref,
            object_version_reference=object_version,
            expected_byte_length=length,
            expected_sha3_512=digest,
        )

        if (
            self.fingerprint
            and not hmac.compare_digest(
                self.fingerprint,
                calculated,
            )
        ):
            _fail(
                "P0_C12F5C_INTENT_FINGERPRINT_MISMATCH"
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
            "storage_provider_id",
            provider,
        )
        object.__setattr__(
            self,
            "storage_object_reference",
            object_ref,
        )
        object.__setattr__(
            self,
            "object_version_reference",
            object_version,
        )
        object.__setattr__(
            self,
            "expected_byte_length",
            length,
        )
        object.__setattr__(
            self,
            "expected_sha3_512",
            digest,
        )
        object.__setattr__(
            self,
            "fingerprint",
            calculated,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class HrDocumentBinaryReadSession:
    provider_name: str
    storage_reference: str
    object_version_reference: str
    read_reference: str
    read_intent_fingerprint: str

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
            ),
        )
        object.__setattr__(
            self,
            "object_version_reference",
            _text(
                "object_version_reference",
                self.object_version_reference,
            ),
        )
        object.__setattr__(
            self,
            "read_reference",
            _text(
                "read_reference",
                self.read_reference,
            ),
        )
        object.__setattr__(
            self,
            "read_intent_fingerprint",
            _sha3(
                "read_intent_fingerprint",
                self.read_intent_fingerprint,
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class HrDocumentBinaryReadChunk:
    sequence: int
    data: bytes
    byte_length: int = field(
        init=False
    )
    chunk_sha3_512: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
        sequence = _non_negative_int(
            "sequence",
            self.sequence,
        )

        if (
            not isinstance(
                self.data,
                bytes,
            )
            or not self.data
            or len(
                self.data
            ) > MAX_READ_CHUNK_BYTES
        ):
            _fail(
                "P0_C12F5C_READ_CHUNK_INVALID"
            )

        object.__setattr__(
            self,
            "sequence",
            sequence,
        )

        object.__setattr__(
            self,
            "byte_length",
            len(
                self.data
            ),
        )

        object.__setattr__(
            self,
            "chunk_sha3_512",
            hashlib.sha3_512(
                self.data
            ).hexdigest(),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class HrDocumentBinaryReadResult:
    provider_name: str
    storage_reference: str
    object_version_reference: str
    read_reference: str
    read_intent_fingerprint: str
    content_length: int
    content_fingerprint: str
    chunk_count: int

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
            ),
        )
        object.__setattr__(
            self,
            "object_version_reference",
            _text(
                "object_version_reference",
                self.object_version_reference,
            ),
        )
        object.__setattr__(
            self,
            "read_reference",
            _text(
                "read_reference",
                self.read_reference,
            ),
        )
        object.__setattr__(
            self,
            "read_intent_fingerprint",
            _sha3(
                "read_intent_fingerprint",
                self.read_intent_fingerprint,
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
        object.__setattr__(
            self,
            "chunk_count",
            _positive_int(
                "chunk_count",
                self.chunk_count,
            ),
        )


class StreamingReadSHA3512:
    __slots__ = (
        "_digest",
        "_length",
        "_finalized",
    )

    def __init__(
        self,
    ) -> None:
        self._digest = hashlib.sha3_512()
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
            _fail(
                "P0_C12F5C_READ_STREAM_FINALIZED"
            )

        if (
            not isinstance(
                chunk,
                bytes,
            )
            or not chunk
            or len(
                chunk
            ) > MAX_READ_CHUNK_BYTES
        ):
            _fail(
                "P0_C12F5C_READ_STREAM_CHUNK_INVALID"
            )

        self._digest.update(
            chunk
        )

        self._length += len(
            chunk
        )

    def finalize(
        self,
    ) -> tuple[int, str]:
        if self._finalized:
            _fail(
                "P0_C12F5C_READ_STREAM_ALREADY_FINALIZED"
            )

        self._finalized = True

        return (
            self._length,
            self._digest.hexdigest(),
        )


def validate_read_session_for_intent(
    intent: HrDocumentBinaryReadIntent,
    session: HrDocumentBinaryReadSession,
) -> None:
    if (
        type(intent)
        is not HrDocumentBinaryReadIntent
        or type(session)
        is not HrDocumentBinaryReadSession
    ):
        _fail(
            "P0_C12F5C_READ_SESSION_INVALID"
        )

    if not (
        hmac.compare_digest(
            intent.fingerprint,
            session.read_intent_fingerprint,
        )
        and intent.storage_provider_id
        == session.provider_name
        and intent.storage_object_reference
        == session.storage_reference
        and intent.object_version_reference
        == session.object_version_reference
    ):
        _fail(
            "P0_C12F5C_READ_SESSION_SCOPE_MISMATCH"
        )


def validate_read_chunk_sequence(
    chunks: tuple[
        HrDocumentBinaryReadChunk,
        ...,
    ],
) -> tuple[
    HrDocumentBinaryReadChunk,
    ...,
]:
    if (
        not isinstance(
            chunks,
            tuple,
        )
        or not chunks
    ):
        _fail(
            "P0_C12F5C_READ_CHUNKS_INVALID"
        )

    for expected, chunk in enumerate(
        chunks
    ):
        if (
            type(chunk)
            is not HrDocumentBinaryReadChunk
            or chunk.sequence != expected
        ):
            _fail(
                "P0_C12F5C_READ_CHUNK_SEQUENCE_INVALID"
            )

    return chunks


def validate_read_result_for_intent(
    intent: HrDocumentBinaryReadIntent,
    result: HrDocumentBinaryReadResult,
    chunks: tuple[
        HrDocumentBinaryReadChunk,
        ...,
    ],
) -> None:
    if (
        type(intent)
        is not HrDocumentBinaryReadIntent
        or type(result)
        is not HrDocumentBinaryReadResult
    ):
        _fail(
            "P0_C12F5C_READ_RESULT_INVALID"
        )

    ordered = validate_read_chunk_sequence(
        chunks
    )

    if not (
        hmac.compare_digest(
            intent.fingerprint,
            result.read_intent_fingerprint,
        )
        and intent.storage_provider_id
        == result.provider_name
        and intent.storage_object_reference
        == result.storage_reference
        and intent.object_version_reference
        == result.object_version_reference
    ):
        _fail(
            "P0_C12F5C_READ_RESULT_SCOPE_MISMATCH"
        )

    if result.chunk_count != len(
        ordered
    ):
        _fail(
            "P0_C12F5C_READ_CHUNK_COUNT_MISMATCH"
        )

    stream = StreamingReadSHA3512()

    for chunk in ordered:
        stream.update(
            chunk.data
        )

    observed_length, observed_digest = stream.finalize()

    if (
        observed_length
        != intent.expected_byte_length
        or result.content_length
        != intent.expected_byte_length
        or result.content_length
        != observed_length
    ):
        _fail(
            "P0_C12F5C_READBACK_LENGTH_MISMATCH"
        )

    if not (
        hmac.compare_digest(
            observed_digest,
            intent.expected_sha3_512,
        )
        and hmac.compare_digest(
            result.content_fingerprint,
            intent.expected_sha3_512,
        )
        and hmac.compare_digest(
            result.content_fingerprint,
            observed_digest,
        )
    ):
        _fail(
            "P0_C12F5C_READBACK_DIGEST_MISMATCH"
        )


@runtime_checkable
class HrDocumentBinaryReadStoragePort(
    Protocol
):
    def begin(
        self,
        intent: HrDocumentBinaryReadIntent,
    ) -> HrDocumentBinaryReadSession:
        ...

    def read_chunk(
        self,
        intent: HrDocumentBinaryReadIntent,
        session: HrDocumentBinaryReadSession,
        *,
        sequence: int,
        max_bytes: int,
    ) -> HrDocumentBinaryReadChunk:
        ...

    def complete(
        self,
        intent: HrDocumentBinaryReadIntent,
        session: HrDocumentBinaryReadSession,
        chunks: tuple[
            HrDocumentBinaryReadChunk,
            ...,
        ],
    ) -> HrDocumentBinaryReadResult:
        ...

    def abort(
        self,
        intent: HrDocumentBinaryReadIntent,
        session: HrDocumentBinaryReadSession,
    ) -> None:
        ...


__all__ = [
    "VERSION",
    "HR_DOCUMENT_BINARY_READ_SCHEMA",
    "MAX_READ_CHUNK_BYTES",
    "HrDocumentBinaryReadStoragePortError",
    "HrDocumentBinaryReadIntent",
    "HrDocumentBinaryReadSession",
    "HrDocumentBinaryReadChunk",
    "HrDocumentBinaryReadResult",
    "StreamingReadSHA3512",
    "validate_read_session_for_intent",
    "validate_read_chunk_sequence",
    "validate_read_result_for_intent",
    "HrDocumentBinaryReadStoragePort",
]


# ARTIFACT: tools/eos/saas/hr/hr_document_read_storage.py
# VERSION: v1.0.0-P0-C12F5C-HR-DOCUMENT-READ-PORT
# AUTHORITY BOUNDARY: authority-stateless binary retrieval contract only
# READBACK BOUNDARY: exact length + incremental SHA3-512 re-verification
# PROVIDER BOUNDARY: provider-neutral; no boto/S3 execution here
# WRITE BOUNDARY: frozen HR write port unchanged
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
