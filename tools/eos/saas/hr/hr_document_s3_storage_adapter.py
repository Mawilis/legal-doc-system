"""TITLE: WILSY OS HR Document S3 Storage Adapter.
VERSION: v1.0.0-P0-C12F5D-HR-S3-ADAPTER
AUTHORITY: Authority-stateless AWS S3 execution for HR document bytes.
EPITOME: Implements the certified HR binary write and read contracts
using opaque server-derived S3 coordinates, encrypted multipart writes,
exact-version inspection and GET-based readback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/hr/hr_document_s3_storage_adapter.py
CERTIFICATION/UPDATE DATE: 2026-10-04.
CHANGELOG:
2026-10-04 v1.0.0-P0-C12F5D-HR-S3-ADAPTER
establishes the first HR S3 provider execution adapter.
AUTHORITY BOUNDARY: S3 execution only. No IAM, HR business authority,
Mongo/registry mutation, HTTP, payroll, billing or financial execution.
TENANT BOUNDARY: Raw tenant, employee, document and ingestion identifiers
never appear in provider object keys.
TRANSACTION BOUNDARY: S3 remains outside Mongo transactions.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import re
from typing import Any, Final, NoReturn

import boto3
from botocore.client import BaseClient
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
)

from tools.eos.saas.hr.hr_document_read_storage import (
    MAX_READ_CHUNK_BYTES,
    HrDocumentBinaryReadChunk,
    HrDocumentBinaryReadIntent,
    HrDocumentBinaryReadResult,
    HrDocumentBinaryReadSession,
    HrDocumentBinaryReadStoragePortError,
    validate_read_session_for_intent,
)
from tools.eos.saas.hr.hr_document_storage import (
    MAX_STREAM_CHUNK_BYTES,
    HrDocumentBinaryChunkEvidence,
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryStoragePortError,
    HrDocumentBinaryWriteIntent,
    HrDocumentBinaryWriteSession,
    validate_object_evidence_for_intent,
    validate_write_session_for_intent,
)


VERSION: Final[str] = (
    "v1.0.0-P0-C12F5D-HR-S3-ADAPTER"
)

PROVIDER_NAME: Final[str] = "aws_s3"
DEFAULT_REGION: Final[str] = "af-south-1"
MAX_S3_PARTS: Final[int] = 10_000

_BUCKET: Final[re.Pattern[str]] = re.compile(
    r"^(?!xn--)(?!.*\.\.)"
    r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$"
)

_READ_STATE_LIMIT: Final[int] = 256


class HrDocumentS3StorageAdapterError(
    RuntimeError
):
    """Stable non-sensitive HR S3 execution error."""

    def __init__(
        self,
        code: str,
    ) -> None:
        self.code = code
        super().__init__(
            code
        )


def _fail(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = HrDocumentS3StorageAdapterError(
        code
    )

    if cause is None:
        raise error

    raise error from cause


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
            f"P0_C12F5D_{name.upper()}_INVALID"
        )

    return value


def _bucket(
    value: object,
) -> str:
    bucket = _text(
        "bucket",
        value,
        limit=63,
    )

    if _BUCKET.fullmatch(
        bucket
    ) is None:
        _fail(
            "P0_C12F5D_BUCKET_INVALID"
        )

    return bucket


def _region(
    value: object,
) -> str:
    region = _text(
        "region",
        value,
        limit=64,
    )

    if re.fullmatch(
        r"^[a-z]{2}(?:-[a-z]+)+-\d+$",
        region,
    ) is None:
        _fail(
            "P0_C12F5D_REGION_INVALID"
        )

    return region


def _kms(
    value: object | None,
) -> str | None:
    if value is None:
        return None

    return _text(
        "kms_key_id",
        value,
    )


def _component(
    value: str,
) -> str:
    return hashlib.sha3_256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def _storage_key(
    intent: HrDocumentBinaryWriteIntent,
) -> str:
    if (
        type(intent)
        is not HrDocumentBinaryWriteIntent
    ):
        _fail(
            "P0_C12F5D_WRITE_INTENT_REQUIRED"
        )

    return (
        "hr-documents/v1/"
        "t/"
        + _component(
            intent.tenant_id
        )
        + "/e/"
        + _component(
            intent.employee_id
        )
        + "/d/"
        + _component(
            intent.document_id
        )
        + "/v/"
        + _component(
            intent.document_version_id
        )
        + "/i/"
        + _component(
            intent.ingestion_reference
        )
        + "/content"
    )


def _metadata(
    intent: HrDocumentBinaryWriteIntent,
) -> dict[str, str]:
    return {
        "wilsy-intent-sha3-512":
            intent.fingerprint,
        "wilsy-tenant-sha3-256":
            _component(
                intent.tenant_id
            ),
        "wilsy-employee-sha3-256":
            _component(
                intent.employee_id
            ),
        "wilsy-document-sha3-256":
            _component(
                intent.document_id
            ),
        "wilsy-version-sha3-256":
            _component(
                intent.document_version_id
            ),
    }


def _provider_text(
    response: dict[str, Any],
    name: str,
) -> str:
    value = response.get(
        name
    )

    if (
        not isinstance(
            value,
            str,
        )
        or not value
    ):
        _fail(
            "P0_C12F5D_PROVIDER_RESPONSE_INVALID"
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class HrDocumentS3Configuration:
    bucket: str
    region: str = DEFAULT_REGION
    kms_key_id: str | None = None

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "bucket",
            _bucket(
                self.bucket
            ),
        )
        object.__setattr__(
            self,
            "region",
            _region(
                self.region
            ),
        )
        object.__setattr__(
            self,
            "kms_key_id",
            _kms(
                self.kms_key_id
            ),
        )


class HrDocumentS3StorageAdapter:
    """S3 execution for frozen HR write/read contracts."""

    def __init__(
        self,
        config: HrDocumentS3Configuration,
        *,
        client: BaseClient | None = None,
    ) -> None:
        if (
            type(config)
            is not HrDocumentS3Configuration
        ):
            _fail(
                "P0_C12F5D_CONFIG_REQUIRED"
            )

        self._config = config
        self._client = (
            client
            or boto3.client(
                "s3",
                region_name=config.region,
            )
        )


    def _encryption(
        self,
    ) -> dict[str, str]:
        if (
            self._config.kms_key_id
            is not None
        ):
            return {
                "ServerSideEncryption":
                    "aws:kms",
                "SSEKMSKeyId":
                    self._config.kms_key_id,
            }

        return {
            "ServerSideEncryption":
                "AES256"
        }

    def begin(
        self,
        intent: HrDocumentBinaryWriteIntent,
    ) -> HrDocumentBinaryWriteSession:
        if (
            type(intent)
            is not HrDocumentBinaryWriteIntent
        ):
            _fail(
                "P0_C12F5D_WRITE_INTENT_REQUIRED"
            )

        key = _storage_key(
            intent
        )

        try:
            response = (
                self._client
                .create_multipart_upload(
                    Bucket=self._config.bucket,
                    Key=key,
                    ContentType=intent.media_type,
                    Metadata=_metadata(
                        intent
                    ),
                    **self._encryption(),
                )
            )

        except (
            BotoCoreError,
            ClientError,
        ) as error:
            _fail(
                "P0_C12F5D_BEGIN_FAILED",
                error,
            )

        upload_id = _provider_text(
            response,
            "UploadId",
        )

        return HrDocumentBinaryWriteSession(
            provider_name=PROVIDER_NAME,
            write_session_reference=upload_id,
            storage_reference=key,
            write_intent_fingerprint=intent.fingerprint,
        )

    def write_chunk(
        self,
        intent: HrDocumentBinaryWriteIntent,
        session: HrDocumentBinaryWriteSession,
        *,
        sequence: int,
        chunk: bytes,
    ) -> HrDocumentBinaryChunkEvidence:
        try:
            validate_write_session_for_intent(
                intent=intent,
                session=session,
            )
        except HrDocumentBinaryStoragePortError as error:
            _fail(
                "P0_C12F5D_SCOPE_MISMATCH",
                error,
            )

        if (
            session.provider_name
            != PROVIDER_NAME
            or session.storage_reference
            != _storage_key(
                intent
            )
        ):
            _fail(
                "P0_C12F5D_SCOPE_MISMATCH"
            )

        if (
            isinstance(
                sequence,
                bool,
            )
            or not isinstance(
                sequence,
                int,
            )
            or sequence < 0
            or sequence >= MAX_S3_PARTS
        ):
            _fail(
                "P0_C12F5D_SEQUENCE_INVALID"
            )

        if (
            not isinstance(
                chunk,
                bytes,
            )
            or not chunk
            or len(
                chunk
            ) > MAX_STREAM_CHUNK_BYTES
        ):
            _fail(
                "P0_C12F5D_CHUNK_INVALID"
            )

        try:
            response = (
                self._client
                .upload_part(
                    Bucket=self._config.bucket,
                    Key=session.storage_reference,
                    UploadId=session.write_session_reference,
                    PartNumber=sequence + 1,
                    Body=chunk,
                )
            )

        except (
            BotoCoreError,
            ClientError,
        ) as error:
            _fail(
                "P0_C12F5D_UPLOAD_PART_FAILED",
                error,
            )

        etag = _provider_text(
            response,
            "ETag",
        )

        return HrDocumentBinaryChunkEvidence(
            sequence=sequence,
            chunk_length=len(
                chunk
            ),
            provider_part_reference=etag,
        )

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
        try:
            validate_write_session_for_intent(
                intent=intent,
                session=session,
            )
        except HrDocumentBinaryStoragePortError as error:
            _fail(
                "P0_C12F5D_SCOPE_MISMATCH",
                error,
            )

        if (
            session.provider_name
            != PROVIDER_NAME
            or session.storage_reference
            != _storage_key(
                intent
            )
        ):
            _fail(
                "P0_C12F5D_SCOPE_MISMATCH"
            )

        if (
            not chunks
            or any(
                chunk.sequence
                != index
                for index, chunk
                in enumerate(
                    chunks
                )
            )
        ):
            _fail(
                "P0_C12F5D_CHUNK_SEQUENCE_INVALID"
            )

        total = sum(
            chunk.chunk_length
            for chunk in chunks
        )

        if (
            total
            != observed_length
        ):
            _fail(
                "P0_C12F5D_LENGTH_MISMATCH"
            )

        if (
            observed_length
            > intent.admitted_max_content_length
        ):
            _fail(
                "P0_C12F5D_LENGTH_EXCEEDED"
            )

        if (
            not isinstance(
                observed_fingerprint,
                str,
            )
            or len(
                observed_fingerprint
            ) != 128
        ):
            _fail(
                "P0_C12F5D_DIGEST_INVALID"
            )

        try:
            response = (
                self._client
                .complete_multipart_upload(
                    Bucket=self._config.bucket,
                    Key=session.storage_reference,
                    UploadId=session.write_session_reference,
                    MultipartUpload={
                        "Parts": [
                            {
                                "PartNumber":
                                    chunk.sequence
                                    + 1,
                                "ETag":
                                    chunk.provider_part_reference,
                            }
                            for chunk in chunks
                        ]
                    },
                )
            )

        except (
            BotoCoreError,
            ClientError,
        ) as error:
            _fail(
                "P0_C12F5D_COMPLETE_FAILED",
                error,
            )

        version_id = _provider_text(
            response,
            "VersionId",
        )

        etag = _provider_text(
            response,
            "ETag",
        )

        evidence = HrDocumentBinaryObjectEvidence(
            provider_name=PROVIDER_NAME,
            storage_reference=session.storage_reference,
            object_version_reference=version_id,
            provider_integrity_reference=etag,
            write_intent_fingerprint=intent.fingerprint,
            content_length=observed_length,
            content_fingerprint=observed_fingerprint,
        )

        return self.inspect(
            intent,
            evidence,
        )

    def inspect(
        self,
        intent: HrDocumentBinaryWriteIntent,
        evidence: HrDocumentBinaryObjectEvidence,
    ) -> HrDocumentBinaryObjectEvidence:
        try:
            validate_object_evidence_for_intent(
                intent=intent,
                evidence=evidence,
            )
        except HrDocumentBinaryStoragePortError as error:
            _fail(
                "P0_C12F5D_SCOPE_MISMATCH",
                error,
            )

        if (
            evidence.provider_name
            != PROVIDER_NAME
            or evidence.storage_reference
            != _storage_key(
                intent
            )
        ):
            _fail(
                "P0_C12F5D_SCOPE_MISMATCH"
            )

        try:
            response = (
                self._client
                .head_object(
                    Bucket=self._config.bucket,
                    Key=evidence.storage_reference,
                    VersionId=evidence.object_version_reference,
                )
            )

        except (
            BotoCoreError,
            ClientError,
        ) as error:
            _fail(
                "P0_C12F5D_INSPECT_FAILED",
                error,
            )

        version_id = _provider_text(
            response,
            "VersionId",
        )

        etag = _provider_text(
            response,
            "ETag",
        )

        content_length = response.get(
            "ContentLength"
        )

        metadata = response.get(
            "Metadata"
        )

        if (
            version_id
            != evidence.object_version_reference
            or etag
            != evidence.provider_integrity_reference
            or content_length
            != evidence.content_length
            or not isinstance(
                metadata,
                dict,
            )
            or metadata.get(
                "wilsy-intent-sha3-512"
            )
            != intent.fingerprint
        ):
            _fail(
                "P0_C12F5D_PROVIDER_EVIDENCE_MISMATCH"
            )

        return evidence

    def abort(
        self,
        intent: HrDocumentBinaryWriteIntent,
        session: HrDocumentBinaryWriteSession,
    ) -> None:
        try:
            validate_write_session_for_intent(
                intent=intent,
                session=session,
            )
        except HrDocumentBinaryStoragePortError as error:
            _fail(
                "P0_C12F5D_SCOPE_MISMATCH",
                error,
            )

        if (
            session.provider_name
            != PROVIDER_NAME
            or session.storage_reference
            != _storage_key(
                intent
            )
        ):
            _fail(
                "P0_C12F5D_SCOPE_MISMATCH"
            )

        try:
            self._client.abort_multipart_upload(
                Bucket=self._config.bucket,
                Key=session.storage_reference,
                UploadId=session.write_session_reference,
            )

        except (
            BotoCoreError,
            ClientError,
        ) as error:
            _fail(
                "P0_C12F5D_ABORT_FAILED",
                error,
            )

class HrDocumentS3ReadStorageAdapter:
    """Exact S3 execution adapter for the frozen HR binary read port."""

    def __init__(
        self,
        config: HrDocumentS3Configuration,
        *,
        client: BaseClient | None = None,
    ) -> None:
        if type(config) is not HrDocumentS3Configuration:
            _fail(
                "P0_C12F5D_CONFIG_REQUIRED"
            )

        self._config = config
        self._client = (
            client
            or boto3.client(
                "s3",
                region_name=config.region,
            )
        )

        self._read_bodies: dict[
            str,
            Any,
        ] = {}

    def begin(
        self,
        intent: HrDocumentBinaryReadIntent,
    ) -> HrDocumentBinaryReadSession:
        if (
            type(intent)
            is not HrDocumentBinaryReadIntent
            or intent.storage_provider_id
            != PROVIDER_NAME
        ):
            _fail(
                "P0_C12F5D_READ_INTENT_REQUIRED"
            )

        if len(
            self._read_bodies
        ) >= _READ_STATE_LIMIT:
            _fail(
                "P0_C12F5D_READ_STATE_LIMIT"
            )

        try:
            response = self._client.get_object(
                Bucket=self._config.bucket,
                Key=intent.storage_object_reference,
                VersionId=intent.object_version_reference,
            )

        except (
            BotoCoreError,
            ClientError,
        ) as error:
            _fail(
                "P0_C12F5D_READ_BEGIN_FAILED",
                error,
            )

        version_id = _provider_text(
            response,
            "VersionId",
        )

        content_length = response.get(
            "ContentLength"
        )

        body = response.get(
            "Body"
        )

        if (
            version_id
            != intent.object_version_reference
            or content_length
            != intent.expected_byte_length
            or body is None
            or not hasattr(
                body,
                "read",
            )
        ):
            _fail(
                "P0_C12F5D_READ_PROVIDER_EVIDENCE_MISMATCH"
            )

        read_reference = hashlib.sha3_512(
            (
                intent.fingerprint
                + ":"
                + intent.object_version_reference
            ).encode(
                "utf-8"
            )
        ).hexdigest()

        self._read_bodies[
            read_reference
        ] = body

        return HrDocumentBinaryReadSession(
            provider_name=PROVIDER_NAME,
            storage_reference=intent.storage_object_reference,
            object_version_reference=intent.object_version_reference,
            read_reference=read_reference,
            read_intent_fingerprint=intent.fingerprint,
        )

    def read_chunk(
        self,
        intent: HrDocumentBinaryReadIntent,
        session: HrDocumentBinaryReadSession,
        *,
        sequence: int,
        max_bytes: int,
    ) -> HrDocumentBinaryReadChunk:
        try:
            validate_read_session_for_intent(
                intent,
                session,
            )

        except HrDocumentBinaryReadStoragePortError as error:
            _fail(
                "P0_C12F5D_READ_SCOPE_MISMATCH",
                error,
            )

        if (
            session.provider_name
            != PROVIDER_NAME
            or isinstance(
                sequence,
                bool,
            )
            or not isinstance(
                sequence,
                int,
            )
            or sequence < 0
            or isinstance(
                max_bytes,
                bool,
            )
            or not isinstance(
                max_bytes,
                int,
            )
            or max_bytes <= 0
            or max_bytes
            > MAX_READ_CHUNK_BYTES
        ):
            _fail(
                "P0_C12F5D_READ_REQUEST_INVALID"
            )

        body = self._read_bodies.get(
            session.read_reference
        )

        if body is None:
            _fail(
                "P0_C12F5D_READ_SESSION_NOT_ACTIVE"
            )

        try:
            data = body.read(
                max_bytes
            )

        except Exception as error:
            _fail(
                "P0_C12F5D_READ_STREAM_FAILED",
                error,
            )

        if (
            not isinstance(
                data,
                bytes,
            )
            or not data
        ):
            _fail(
                "P0_C12F5D_READ_STREAM_EXHAUSTED"
            )

        return HrDocumentBinaryReadChunk(
            sequence=sequence,
            data=data,
        )

    def complete(
        self,
        intent: HrDocumentBinaryReadIntent,
        session: HrDocumentBinaryReadSession,
        chunks: tuple[
            HrDocumentBinaryReadChunk,
            ...,
        ],
    ) -> HrDocumentBinaryReadResult:
        try:
            validate_read_session_for_intent(
                intent,
                session,
            )

        except HrDocumentBinaryReadStoragePortError as error:
            _fail(
                "P0_C12F5D_READ_SCOPE_MISMATCH",
                error,
            )

        if not chunks:
            _fail(
                "P0_C12F5D_READ_CHUNKS_REQUIRED"
            )

        observed_length = sum(
            chunk.byte_length
            for chunk in chunks
        )

        hasher = hashlib.sha3_512()

        for index, chunk in enumerate(
            chunks
        ):
            if chunk.sequence != index:
                _fail(
                    "P0_C12F5D_READ_CHUNK_SEQUENCE_INVALID"
                )

            hasher.update(
                chunk.data
            )

        observed_digest = (
            hasher.hexdigest()
        )

        if (
            observed_length
            != intent.expected_byte_length
            or not hmac.compare_digest(
                observed_digest,
                intent.expected_sha3_512,
            )
        ):
            _fail(
                "P0_C12F5D_READBACK_INTEGRITY_MISMATCH"
            )

        self._read_bodies.pop(
            session.read_reference,
            None,
        )

        return HrDocumentBinaryReadResult(
            provider_name=PROVIDER_NAME,
            storage_reference=intent.storage_object_reference,
            object_version_reference=intent.object_version_reference,
            read_reference=session.read_reference,
            read_intent_fingerprint=intent.fingerprint,
            content_length=observed_length,
            content_fingerprint=observed_digest,
            chunk_count=len(
                chunks
            ),
        )

    def abort(
        self,
        intent: HrDocumentBinaryReadIntent,
        session: HrDocumentBinaryReadSession,
    ) -> None:
        try:
            validate_read_session_for_intent(
                intent,
                session,
            )

        except HrDocumentBinaryReadStoragePortError as error:
            _fail(
                "P0_C12F5D_READ_SCOPE_MISMATCH",
                error,
            )

        self._read_bodies.pop(
            session.read_reference,
            None,
        )



__all__ = [
    "VERSION",
    "PROVIDER_NAME",
    "DEFAULT_REGION",
    "HrDocumentS3StorageAdapterError",
    "HrDocumentS3Configuration",
    "HrDocumentS3StorageAdapter",
    "HrDocumentS3ReadStorageAdapter",
]


# ARTIFACT: tools/eos/saas/hr/hr_document_s3_storage_adapter.py
# VERSION: v1.0.0-P0-C12F5D-HR-S3-ADAPTER
# PROVIDER: AWS S3 execution only
# OBJECT KEYS: server-derived opaque digests only
# ENCRYPTION: AES256 default, optional AWS KMS
# AUTHORITY BOUNDARY: no IAM, HR business, registry or financial authority
# TRANSACTION BOUNDARY: S3 remains outside Mongo transactions
# END OF WILSY OS SOVEREIGN ARTIFACT
