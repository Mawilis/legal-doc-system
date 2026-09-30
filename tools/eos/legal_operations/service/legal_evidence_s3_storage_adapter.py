"""WILSY OS AWS S3 adapter for streamed Legal Evidence binaries.

TITLE: Legal Evidence S3 Storage Adapter
VERSION: v1.3.0-L10A2R-C4D2R2-S3-INTENT-METADATA-RECOVERY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Implement the certified provider-neutral Legal Evidence binary-storage
         port using AWS S3 multipart operations while preserving exact
         tenant-scoped intent binding, opaque provider evidence and fail-closed
         provider interaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_s3_storage_adapter.py
COLLABORATION / OWNERSHIP: L10A2R-A4-R1 owns provider-neutral storage semantics
                            and tenant/intake scope guards. This adapter owns
                            only S3 capability execution. L10A1 owns canonical
                            Legal Evidence content identity. L10A2Q owns
                            commercial capacity. Retention/legal-hold authority,
                            HTTP, IAM and Mongo reconciliation remain elsewhere.
CERTIFICATION / UPDATE DATE: 2026-09-30
CHANGELOG: v1.3.0-L10A2R-C4D2R2 performs exact-version S3 HEAD
           recovery for every completed object version and emits explicit
           ABSENT/PRESENT canonical WILSY intent-metadata evidence. Provider
           failure, object-version mismatch, length/integrity mismatch and
           malformed metadata fail closed.
           v1.2.0-L10A2R-C4D2 adds read-only tenant-scoped S3 discovery
           for incomplete multipart uploads and completed object versions.
           Discovery validates exact tenant scope, uses opaque tenant prefixes,
           rejects truncated provider enumeration and grants no orphan,
           abort, deletion, retention or availability authority.
           v1.1.0-L10A2R-B2-R1 makes provider object coordinates opaque by
           hashing tenant/matter/document/ingestion identities before they leave
           WILSY, models fail() as NoReturn for exact type narrowing, and rejects
           multipart part-size or total-byte divergence before S3 completion.
           v1.0.0-L10A2R-B2 established S3 multipart begin/upload/complete,
           provider-object inspection and multipart abort with tenant-scoped
           pre-provider guards, server-derived object keys, bounded provider
           errors, encryption-at-rest configuration and provider metadata
           correlation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Credentials are obtained only through the standard
                             AWS SDK provider chain and are never accepted by
                             this adapter API. Caller-supplied bucket names,
                             object keys, upload IDs and provider locators are
                             prohibited. Cross-scope validation occurs before
                             every AWS request.
TENANT BOUNDARY: Object keys are deterministically derived from cryptographic
                 digests of the sealed tenant/matter/document/ingestion
                 coordinates; raw tenant/business identifiers never appear in
                 provider keys. Caller-selected keys are prohibited.
                 Session/evidence substitution rejects before provider access.
AUTHORITY BOUNDARY: S3 transport/storage execution only. S3 does not become
                    canonical Legal lifecycle, Court, IAM, retention, capacity,
                    content-identity, pricing or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive financial
                               execution and settlement authority.
TRANSACTION BOUNDARY: S3 is outside Mongo transactions. This adapter performs
                      no Mongo read/write and does not claim distributed atomicity.
FAIL-CLOSED DECLARATION: Invalid configuration, malformed provider responses,
                         cross-scope sessions/evidence, sequence divergence,
                         oversized chunks, provider metadata mismatch, missing
                         version evidence and AWS failures reject without
                         inventing storage success.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import re
from typing import Any, Final, Mapping, NoReturn

import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError

from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    MAX_STREAM_CHUNK_BYTES,
    LegalEvidenceBinaryChunkEvidence,
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryStoragePortError,
    LegalEvidenceBinaryWriteIntent,
    LegalEvidenceBinaryWriteSession,
    validate_object_evidence_for_intent,
    validate_write_session_for_intent,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceIncompleteWriteSessionObservation,
    LegalEvidenceProviderCleanupDiscoveryError,
    LegalEvidenceProviderDiscoveryScope,
)


VERSION: Final[str] = "v1.3.0-L10A2R-C4D2R2-S3-INTENT-METADATA-RECOVERY"
PROVIDER_NAME: Final[str] = "aws_s3"
DEFAULT_REGION: Final[str] = "af-south-1"
MAX_S3_PARTS: Final[int] = 10_000
S3_MIN_NONFINAL_PART_BYTES: Final[int] = 5 * 1024 * 1024

_BUCKET = re.compile(r"^(?!xn--)(?!.*\.\.)[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")
_KEY_COMPONENT = re.compile(r"^[A-Za-z0-9._:-]+$")


class LegalEvidenceS3StorageAdapterError(RuntimeError):
    """Stable non-sensitive S3 adapter failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalEvidenceS3StorageAdapterError(code)
    if cause is None:
        raise error
    raise error from cause


def _required_text(name: str, value: object, *, limit: int = 2048) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 32 for character in value)
    ):
        _fail(f"L10A2R_B2_{name.upper()}_INVALID")
    return value


def _bucket(value: object) -> str:
    bucket = _required_text("bucket", value, limit=63)
    if _BUCKET.fullmatch(bucket) is None:
        _fail("L10A2R_B2_BUCKET_INVALID")
    return bucket


def _region(value: object) -> str:
    region = _required_text("region", value, limit=64)
    if not re.fullmatch(r"^[a-z]{2}(?:-[a-z]+)+-\d+$", region):
        _fail("L10A2R_B2_REGION_INVALID")
    return region


def _kms_key(value: object | None) -> str | None:
    if value is None:
        return None
    return _required_text("kms_key_id", value, limit=2048)


def _component_digest(name: str, value: str) -> str:
    """Return one provider-safe opaque digest for an already-validated identity."""
    if not value or _KEY_COMPONENT.fullmatch(value) is None:
        _fail(f"L10A2R_B2_{name.upper()}_INVALID")
    return hashlib.sha3_256(value.encode("utf-8")).hexdigest()


def _tenant_discovery_prefix(
    scope: LegalEvidenceProviderDiscoveryScope,
) -> str:
    """Return the exact opaque S3 tenant prefix after sealed-scope validation."""
    if type(scope) is not LegalEvidenceProviderDiscoveryScope:
        _fail("L10A2R_C4D2_DISCOVERY_SCOPE_REQUIRED")

    expected_scope_fingerprint = hashlib.sha3_512(
        scope.tenant_id.encode("utf-8")
    ).hexdigest()

    if not hmac.compare_digest(
        scope.tenant_scope_fingerprint,
        expected_scope_fingerprint,
    ):
        _fail("L10A2R_C4D2_DISCOVERY_SCOPE_MISMATCH")

    tenant = _component_digest(
        "tenant_id",
        scope.tenant_id,
    )

    return f"legal-evidence/v1/t/{tenant}/"


def _observation_time(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            f"L10A2R_C4D2_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _storage_key(intent: LegalEvidenceBinaryWriteIntent) -> str:
    """Derive one opaque server-owned tenant-scoped S3 object key."""
    if type(intent) is not LegalEvidenceBinaryWriteIntent:
        _fail("L10A2R_B2_WRITE_INTENT_REQUIRED")

    tenant = _component_digest("tenant_id", intent.tenant_id)
    matter = _component_digest("case_matter_id", intent.case_matter_id)
    document = _component_digest("document_id", intent.document_id)
    ingestion = _component_digest(
        "ingestion_reference",
        intent.ingestion_reference,
    )

    return (
        f"legal-evidence/v1/t/{tenant}/m/{matter}/"
        f"d/{document}/i/{ingestion}/content"
    )


def _metadata(intent: LegalEvidenceBinaryWriteIntent) -> dict[str, str]:
    """Return provider metadata containing no raw tenant/business identifiers."""
    return {
        "wilsy-intent-sha3-512": intent.fingerprint,
        "wilsy-tenant-sha3-256": hashlib.sha3_256(
            intent.tenant_id.encode("utf-8")
        ).hexdigest(),
    }


def _provider_reference(response: Mapping[str, Any], name: str) -> str:
    value = response.get(name)
    if not isinstance(value, str) or not value:
        _fail("L10A2R_B2_PROVIDER_RESPONSE_INVALID")
    return value


@dataclass(frozen=True, slots=True)
class LegalEvidenceS3Configuration:
    """Immutable adapter-owned S3 configuration."""

    bucket: str
    region: str = DEFAULT_REGION
    kms_key_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "bucket", _bucket(self.bucket))
        object.__setattr__(self, "region", _region(self.region))
        object.__setattr__(self, "kms_key_id", _kms_key(self.kms_key_id))


class LegalEvidenceS3StorageAdapter:
    """AWS S3 implementation of the Legal Evidence binary-storage port.

    The adapter performs no IAM authorization and accepts no caller storage
    coordinates. Every operation validates the exact sealed WILSY write intent
    locally before making an AWS request.
    """

    def __init__(
        self,
        config: LegalEvidenceS3Configuration,
        *,
        client: BaseClient | None = None,
    ) -> None:
        if type(config) is not LegalEvidenceS3Configuration:
            _fail("L10A2R_B2_CONFIG_REQUIRED")

        self._config = config
        self._client = client or boto3.client("s3", region_name=config.region)

    def _encryption(self) -> dict[str, str]:
        if self._config.kms_key_id is not None:
            return {
                "ServerSideEncryption": "aws:kms",
                "SSEKMSKeyId": self._config.kms_key_id,
            }
        return {"ServerSideEncryption": "AES256"}

    def begin(
        self,
        intent: LegalEvidenceBinaryWriteIntent,
    ) -> LegalEvidenceBinaryWriteSession:
        """Create one multipart upload for a server-derived tenant object key."""
        if type(intent) is not LegalEvidenceBinaryWriteIntent:
            _fail("L10A2R_B2_WRITE_INTENT_REQUIRED")

        key = _storage_key(intent)
        try:
            response = self._client.create_multipart_upload(
                Bucket=self._config.bucket,
                Key=key,
                ContentType=intent.media_type,
                Metadata=_metadata(intent),
                **self._encryption(),
            )
        except (BotoCoreError, ClientError) as error:
            _fail("L10A2R_B2_BEGIN_FAILED", error)

        upload_id = _provider_reference(response, "UploadId")

        return LegalEvidenceBinaryWriteSession(
            provider_name=PROVIDER_NAME,
            write_session_reference=upload_id,
            storage_reference=key,
            write_intent_fingerprint=intent.fingerprint,
        )

    def write_chunk(
        self,
        intent: LegalEvidenceBinaryWriteIntent,
        session: LegalEvidenceBinaryWriteSession,
        *,
        sequence: int,
        chunk: bytes,
    ) -> LegalEvidenceBinaryChunkEvidence:
        """Upload one exact ordered chunk after local tenant-scope validation."""
        try:
            validate_write_session_for_intent(intent=intent, session=session)
        except LegalEvidenceBinaryStoragePortError as error:
            _fail("L10A2R_B2_SCOPE_MISMATCH", error)

        if session.provider_name != PROVIDER_NAME:
            _fail("L10A2R_B2_SCOPE_MISMATCH")
        if session.storage_reference != _storage_key(intent):
            _fail("L10A2R_B2_SCOPE_MISMATCH")

        if isinstance(sequence, bool) or not isinstance(sequence, int):
            _fail("L10A2R_B2_SEQUENCE_INVALID")
        if sequence < 0 or sequence >= MAX_S3_PARTS:
            _fail("L10A2R_B2_SEQUENCE_INVALID")
        if (
            not isinstance(chunk, bytes)
            or not chunk
            or len(chunk) > MAX_STREAM_CHUNK_BYTES
        ):
            _fail("L10A2R_B2_CHUNK_INVALID")

        try:
            response = self._client.upload_part(
                Bucket=self._config.bucket,
                Key=session.storage_reference,
                UploadId=session.write_session_reference,
                PartNumber=sequence + 1,
                Body=chunk,
            )
        except (BotoCoreError, ClientError) as error:
            _fail("L10A2R_B2_UPLOAD_PART_FAILED", error)

        etag = _provider_reference(response, "ETag")

        return LegalEvidenceBinaryChunkEvidence(
            sequence=sequence,
            chunk_length=len(chunk),
            provider_part_reference=etag,
        )

    def complete(
        self,
        intent: LegalEvidenceBinaryWriteIntent,
        session: LegalEvidenceBinaryWriteSession,
        *,
        chunks: tuple[LegalEvidenceBinaryChunkEvidence, ...],
        content_length: int,
        content_fingerprint: str,
    ) -> LegalEvidenceBinaryObjectEvidence:
        """Complete one exact multipart upload and verify provider metadata."""
        try:
            validate_write_session_for_intent(intent=intent, session=session)
        except LegalEvidenceBinaryStoragePortError as error:
            _fail("L10A2R_B2_SCOPE_MISMATCH", error)

        if (
            session.provider_name != PROVIDER_NAME
            or session.storage_reference != _storage_key(intent)
        ):
            _fail("L10A2R_B2_SCOPE_MISMATCH")

        if not isinstance(chunks, tuple) or not chunks:
            _fail("L10A2R_B2_CHUNKS_REQUIRED")
        if len(chunks) > MAX_S3_PARTS:
            _fail("L10A2R_B2_TOO_MANY_PARTS")

        parts: list[dict[str, Any]] = []
        observed_total = 0

        for expected, chunk in enumerate(chunks):
            if type(chunk) is not LegalEvidenceBinaryChunkEvidence:
                _fail("L10A2R_B2_CHUNK_EVIDENCE_INVALID")
            if chunk.sequence != expected:
                _fail("L10A2R_B2_SEQUENCE_INVALID")

            is_final = expected == len(chunks) - 1
            if (
                not is_final
                and chunk.chunk_length < S3_MIN_NONFINAL_PART_BYTES
            ):
                _fail("L10A2R_B2_NONFINAL_PART_TOO_SMALL")

            observed_total += chunk.chunk_length

            parts.append(
                {
                    "ETag": chunk.provider_part_reference,
                    "PartNumber": expected + 1,
                }
            )

        if (
            isinstance(content_length, bool)
            or not isinstance(content_length, int)
            or content_length <= 0
            or content_length > intent.admitted_max_content_length
            or observed_total != content_length
        ):
            _fail("L10A2R_B2_CONTENT_LENGTH_INVALID")

        if (
            not isinstance(content_fingerprint, str)
            or len(content_fingerprint) != 128
            or not re.fullmatch(r"[0-9a-f]{128}", content_fingerprint)
        ):
            _fail("L10A2R_B2_CONTENT_FINGERPRINT_INVALID")

        try:
            response = self._client.complete_multipart_upload(
                Bucket=self._config.bucket,
                Key=session.storage_reference,
                UploadId=session.write_session_reference,
                MultipartUpload={"Parts": parts},
            )
        except (BotoCoreError, ClientError) as error:
            _fail("L10A2R_B2_COMPLETE_FAILED", error)

        version_id = _provider_reference(response, "VersionId")
        etag = _provider_reference(response, "ETag")

        evidence = LegalEvidenceBinaryObjectEvidence(
            provider_name=PROVIDER_NAME,
            storage_reference=session.storage_reference,
            object_version_reference=version_id,
            provider_integrity_reference=etag,
            write_intent_fingerprint=intent.fingerprint,
            content_length=content_length,
            content_fingerprint=content_fingerprint,
        )

        return self.inspect(intent, evidence)

    def inspect(
        self,
        intent: LegalEvidenceBinaryWriteIntent,
        evidence: LegalEvidenceBinaryObjectEvidence,
    ) -> LegalEvidenceBinaryObjectEvidence:
        """HEAD one exact object version after local scope validation."""
        try:
            validate_object_evidence_for_intent(
                intent=intent,
                evidence=evidence,
            )
        except LegalEvidenceBinaryStoragePortError as error:
            _fail("L10A2R_B2_SCOPE_MISMATCH", error)

        if (
            evidence.provider_name != PROVIDER_NAME
            or evidence.storage_reference != _storage_key(intent)
        ):
            _fail("L10A2R_B2_SCOPE_MISMATCH")

        try:
            response = self._client.head_object(
                Bucket=self._config.bucket,
                Key=evidence.storage_reference,
                VersionId=evidence.object_version_reference,
            )
        except (BotoCoreError, ClientError) as error:
            _fail("L10A2R_B2_INSPECT_FAILED", error)

        length = response.get("ContentLength")
        metadata = response.get("Metadata")
        etag = response.get("ETag")
        version_id = response.get("VersionId")

        if (
            isinstance(length, bool)
            or not isinstance(length, int)
            or length != evidence.content_length
            or not isinstance(metadata, Mapping)
            or metadata.get("wilsy-intent-sha3-512") != intent.fingerprint
            or not isinstance(etag, str)
            or not etag
            or not isinstance(version_id, str)
            or not version_id
            or version_id != evidence.object_version_reference
        ):
            _fail("L10A2R_B2_PROVIDER_METADATA_MISMATCH")

        return LegalEvidenceBinaryObjectEvidence(
            provider_name=PROVIDER_NAME,
            storage_reference=evidence.storage_reference,
            object_version_reference=version_id,
            provider_integrity_reference=etag,
            write_intent_fingerprint=intent.fingerprint,
            content_length=length,
            content_fingerprint=evidence.content_fingerprint,
        )

    def list_incomplete_write_sessions(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
    ) -> tuple[
        LegalEvidenceIncompleteWriteSessionObservation,
        ...,
    ]:
        """Observe incomplete multipart sessions under one exact tenant prefix."""
        prefix = _tenant_discovery_prefix(
            scope
        )
        observed = _observation_time(
            "observed_at",
            observed_at,
        )

        try:
            response = (
                self._client.list_multipart_uploads(
                    Bucket=self._config.bucket,
                    Prefix=prefix,
                )
            )
        except (
            BotoCoreError,
            ClientError,
        ) as error:
            _fail(
                "L10A2R_C4D2_LIST_MULTIPART_UPLOADS_FAILED",
                error,
            )

        if not isinstance(
            response,
            Mapping,
        ):
            _fail(
                "L10A2R_C4D2_PROVIDER_RESPONSE_INVALID"
            )

        if response.get(
            "IsTruncated"
        ) is True:
            _fail(
                "L10A2R_C4D2_DISCOVERY_TRUNCATED"
            )

        uploads = response.get(
            "Uploads",
            [],
        )

        if not isinstance(
            uploads,
            list,
        ):
            _fail(
                "L10A2R_C4D2_PROVIDER_RESPONSE_INVALID"
            )

        observations: list[
            LegalEvidenceIncompleteWriteSessionObservation
        ] = []

        for row in uploads:
            if not isinstance(
                row,
                Mapping,
            ):
                _fail(
                    "L10A2R_C4D2_PROVIDER_RESPONSE_INVALID"
                )

            key = row.get(
                "Key"
            )
            upload_id = row.get(
                "UploadId"
            )
            initiated = row.get(
                "Initiated"
            )

            if (
                not isinstance(key, str)
                or not key.startswith(prefix)
                or not isinstance(upload_id, str)
                or not upload_id
                or not isinstance(
                    initiated,
                    datetime,
                )
            ):
                _fail(
                    "L10A2R_C4D2_PROVIDER_RESPONSE_INVALID"
                )

            try:
                observation = (
                    LegalEvidenceIncompleteWriteSessionObservation(
                        tenant_id=scope.tenant_id,
                        provider_name=PROVIDER_NAME,
                        storage_reference=key,
                        write_session_reference=upload_id,
                        initiated_at=initiated,
                        observed_at=observed,
                    )
                )
            except LegalEvidenceProviderCleanupDiscoveryError as error:
                _fail(
                    "L10A2R_C4D2_PROVIDER_RESPONSE_INVALID",
                    error,
                )

            observations.append(
                observation
            )

        return tuple(
            sorted(
                observations,
                key=lambda item: (
                    item.initiated_at,
                    item.storage_reference,
                    item.write_session_reference,
                ),
            )
        )

    def list_completed_object_versions(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
    ) -> tuple[
        LegalEvidenceCompletedObjectObservation,
        ...,
    ]:
        """Observe completed S3 object versions under one exact tenant prefix."""
        prefix = _tenant_discovery_prefix(
            scope
        )
        observed = _observation_time(
            "observed_at",
            observed_at,
        )

        try:
            response = (
                self._client.list_object_versions(
                    Bucket=self._config.bucket,
                    Prefix=prefix,
                )
            )
        except (
            BotoCoreError,
            ClientError,
        ) as error:
            _fail(
                "L10A2R_C4D2_LIST_OBJECT_VERSIONS_FAILED",
                error,
            )

        if not isinstance(
            response,
            Mapping,
        ):
            _fail(
                "L10A2R_C4D2_PROVIDER_RESPONSE_INVALID"
            )

        if response.get(
            "IsTruncated"
        ) is True:
            _fail(
                "L10A2R_C4D2_DISCOVERY_TRUNCATED"
            )

        versions = response.get(
            "Versions",
            [],
        )

        if not isinstance(
            versions,
            list,
        ):
            _fail(
                "L10A2R_C4D2_PROVIDER_RESPONSE_INVALID"
            )

        observations: list[
            LegalEvidenceCompletedObjectObservation
        ] = []

        for row in versions:
            if not isinstance(
                row,
                Mapping,
            ):
                _fail(
                    "L10A2R_C4D2_PROVIDER_RESPONSE_INVALID"
                )

            key = row.get(
                "Key"
            )
            version_id = row.get(
                "VersionId"
            )
            etag = row.get(
                "ETag"
            )
            size = row.get(
                "Size"
            )
            modified = row.get(
                "LastModified"
            )

            if (
                not isinstance(key, str)
                or not key.startswith(prefix)
                or not isinstance(version_id, str)
                or not version_id
                or not isinstance(etag, str)
                or not etag
                or isinstance(size, bool)
                or not isinstance(size, int)
                or size <= 0
                or not isinstance(
                    modified,
                    datetime,
                )
            ):
                _fail(
                    "L10A2R_C4D2_PROVIDER_RESPONSE_INVALID"
                )

            try:
                head = self._client.head_object(
                    Bucket=self._config.bucket,
                    Key=key,
                    VersionId=version_id,
                )
            except (
                BotoCoreError,
                ClientError,
            ) as error:
                _fail(
                    "L10A2R_C4D2R2_HEAD_OBJECT_FAILED",
                    error,
                )

            if not isinstance(
                head,
                Mapping,
            ):
                _fail(
                    "L10A2R_C4D2R2_HEAD_RESPONSE_INVALID"
                )

            head_version = head.get(
                "VersionId"
            )
            head_etag = head.get(
                "ETag"
            )
            head_length = head.get(
                "ContentLength"
            )
            metadata = head.get(
                "Metadata"
            )

            if (
                not isinstance(head_version, str)
                or head_version != version_id
                or not isinstance(head_etag, str)
                or head_etag != etag
                or isinstance(head_length, bool)
                or not isinstance(head_length, int)
                or head_length != size
                or not isinstance(metadata, Mapping)
            ):
                _fail(
                    "L10A2R_C4D2R2_HEAD_RESPONSE_MISMATCH"
                )

            raw_intent_fingerprint = metadata.get(
                "wilsy-intent-sha3-512"
            )

            if raw_intent_fingerprint is None:
                metadata_state = (
                    LegalEvidenceCompletedObjectIntentMetadataState.ABSENT
                )
                intent_fingerprint = None
            else:
                metadata_state = (
                    LegalEvidenceCompletedObjectIntentMetadataState.PRESENT
                )
                intent_fingerprint = raw_intent_fingerprint

            try:
                observation = (
                    LegalEvidenceCompletedObjectObservation(
                        tenant_id=scope.tenant_id,
                        provider_name=PROVIDER_NAME,
                        storage_reference=key,
                        object_version_reference=version_id,
                        provider_integrity_reference=etag,
                        content_length=size,
                        last_modified_at=modified,
                        observed_at=observed,
                        write_intent_metadata_state=metadata_state,
                        write_intent_fingerprint=intent_fingerprint,
                    )
                )
            except LegalEvidenceProviderCleanupDiscoveryError as error:
                _fail(
                    "L10A2R_C4D2R2_PROVIDER_METADATA_INVALID",
                    error,
                )

            observations.append(
                observation
            )

        return tuple(
            sorted(
                observations,
                key=lambda item: (
                    item.last_modified_at,
                    item.storage_reference,
                    item.object_version_reference,
                ),
            )
        )

    def abort(
        self,
        intent: LegalEvidenceBinaryWriteIntent,
        session: LegalEvidenceBinaryWriteSession,
    ) -> None:
        """Abort one exact multipart session after local scope validation."""
        try:
            validate_write_session_for_intent(intent=intent, session=session)
        except LegalEvidenceBinaryStoragePortError as error:
            _fail("L10A2R_B2_SCOPE_MISMATCH", error)

        if (
            session.provider_name != PROVIDER_NAME
            or session.storage_reference != _storage_key(intent)
        ):
            _fail("L10A2R_B2_SCOPE_MISMATCH")

        try:
            self._client.abort_multipart_upload(
                Bucket=self._config.bucket,
                Key=session.storage_reference,
                UploadId=session.write_session_reference,
            )
        except (BotoCoreError, ClientError) as error:
            _fail("L10A2R_B2_ABORT_FAILED", error)


__all__ = [
    "DEFAULT_REGION",
    "MAX_S3_PARTS",
    "PROVIDER_NAME",
    "S3_MIN_NONFINAL_PART_BYTES",
    "VERSION",
    "LegalEvidenceS3Configuration",
    "LegalEvidenceS3StorageAdapter",
    "LegalEvidenceS3StorageAdapterError",
]

# ARTIFACT: legal_evidence_s3_storage_adapter.py
# VERSION: v1.3.0-L10A2R-C4D2R2-S3-INTENT-METADATA-RECOVERY
# AUTHORITY BOUNDARY: AWS S3 capability execution only; WILSY retains canonical Legal Evidence truth
# TENANT POSTURE: provider keys contain only opaque coordinate digests; every provider operation locally tenant/intake scope-guarded
# FAIL-CLOSED POSTURE: scope/config/sequence/provider-response/provider-metadata divergence rejects before success
# CLEANUP METADATA POSTURE: exact object-version HEAD yields ABSENT or PRESENT evidence only
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
