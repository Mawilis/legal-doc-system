"""AWS S3 multipart adapter for sealed candidate evidence write intents.

Provider execution only. KMS encryption is mandatory; Mongo custody metadata
and lifecycle authority remain separate.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import re
from typing import Any, NoReturn
from tempfile import SpooledTemporaryFile

import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError

from tools.eos.saas.hr.candidate_evidence_storage import (
    MAX_CHUNK_BYTES, CandidateEvidenceBinaryObjectEvidence,
    CandidateEvidenceStorageError, CandidateEvidenceWriteIntent,
    CandidateEvidenceWriteSession,
)

PROVIDER_ID = "aws_s3"
MIN_NONFINAL_PART_BYTES = 5 * 1024 * 1024
_BUCKET = re.compile(r"^(?!xn--)(?!.*\.\.)[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")


class CandidateEvidenceS3Error(RuntimeError):
    def __init__(self, code: str, *, uncertain: bool = False) -> None:
        self.code = code
        self.uncertain = uncertain
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None, *, uncertain: bool = False) -> NoReturn:
    error = CandidateEvidenceS3Error(code, uncertain=uncertain)
    if cause is None:
        raise error
    raise error from cause


def _component(value: str) -> str:
    return hashlib.sha3_256(value.encode("utf-8")).hexdigest()


def _storage_key_for_scope(tenant_id: str, candidate_id: str, evidence_id: str,
                           evidence_version_id: str, ingestion_reference: str) -> str:
    return (
        "hr-candidate-evidence/v1/t/" + _component(tenant_id)
        + "/c/" + _component(candidate_id)
        + "/e/" + _component(evidence_id)
        + "/v/" + _component(evidence_version_id)
        + "/i/" + _component(ingestion_reference)
        + "/content"
    )


def _storage_key(intent: CandidateEvidenceWriteIntent) -> str:
    if type(intent) is not CandidateEvidenceWriteIntent:
        _fail("CANDIDATE_EVIDENCE_S3_WRITE_INTENT_REQUIRED")
    return _storage_key_for_scope(
        intent.tenant_id, intent.candidate_id, intent.evidence_id,
        intent.evidence_version_id, intent.ingestion_reference,
    )


@dataclass(frozen=True, slots=True)
class CandidateEvidenceS3Configuration:
    bucket: str
    region: str
    kms_key_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.bucket, str) or _BUCKET.fullmatch(self.bucket) is None:
            raise ValueError("CANDIDATE_EVIDENCE_S3_BUCKET_INVALID")
        if not isinstance(self.region, str) or re.fullmatch(r"^[a-z]{2}(?:-[a-z]+)+-\d+$", self.region) is None:
            raise ValueError("CANDIDATE_EVIDENCE_S3_REGION_INVALID")
        if not isinstance(self.kms_key_id, str) or not self.kms_key_id.strip():
            raise ValueError("CANDIDATE_EVIDENCE_S3_KMS_REQUIRED")


class CandidateEvidenceS3StorageAdapter:
    def __init__(self, config: CandidateEvidenceS3Configuration, *, client: BaseClient | None = None) -> None:
        if type(config) is not CandidateEvidenceS3Configuration:
            raise ValueError("CANDIDATE_EVIDENCE_S3_CONFIGURATION_REQUIRED")
        self._config = config
        self._client = client or boto3.client("s3", region_name=config.region)

    def object_key_for_scope(
        self, *, tenant_id: str, candidate_id: str, evidence_id: str,
        evidence_version_id: str, ingestion_reference: str,
    ) -> str:
        """Derive the opaque provider key for one durable attempt scope."""
        return _storage_key_for_scope(
            tenant_id, candidate_id, evidence_id, evidence_version_id, ingestion_reference,
        )

    def storage_reference_for_scope(
        self, *, tenant_id: str, candidate_id: str, evidence_id: str,
        evidence_version_id: str, ingestion_reference: str,
    ) -> str:
        return _component(self.object_key_for_scope(
            tenant_id=tenant_id, candidate_id=candidate_id, evidence_id=evidence_id,
            evidence_version_id=evidence_version_id, ingestion_reference=ingestion_reference,
        ))

    def begin(self, intent: CandidateEvidenceWriteIntent) -> CandidateEvidenceWriteSession:
        key = _storage_key(intent)
        try:
            response = self._client.create_multipart_upload(
                Bucket=self._config.bucket, Key=key, ContentType=intent.media_type,
                ServerSideEncryption="aws:kms", SSEKMSKeyId=self._config.kms_key_id,
                Metadata={
                    "wilsy-intent-fingerprint": intent.fingerprint,
                    "wilsy-tenant-sha3-256": _component(intent.tenant_id),
                    "wilsy-candidate-sha3-256": _component(intent.candidate_id),
                    "wilsy-evidence-sha3-256": _component(intent.evidence_id),
                    "wilsy-version-sha3-256": _component(intent.evidence_version_id),
                },
            )
            upload_id = response.get("UploadId")
            if not isinstance(upload_id, str) or not upload_id:
                _fail("CANDIDATE_EVIDENCE_S3_UPLOAD_SESSION_INVALID", uncertain=True)
            return CandidateEvidenceWriteSession(
                intent=intent, provider_upload_id=upload_id, provider_object_key=key,
                storage_object_reference=_component(key),
                created_at=datetime.now(timezone.utc),
            )
        except CandidateEvidenceS3Error:
            raise
        except (BotoCoreError, ClientError) as error:
            _fail("CANDIDATE_EVIDENCE_S3_BEGIN_UNAVAILABLE", error)

    def write_chunk(self, session: CandidateEvidenceWriteSession, chunk: bytes) -> int:
        if type(session) is not CandidateEvidenceWriteSession or session.closed:
            _fail("CANDIDATE_EVIDENCE_S3_SESSION_INVALID")
        if not isinstance(chunk, bytes) or not chunk or len(chunk) > MAX_CHUNK_BYTES:
            _fail("CANDIDATE_EVIDENCE_S3_CHUNK_INVALID")
        if session.parts and session.parts[-1]["length"] < MIN_NONFINAL_PART_BYTES:
            _fail("CANDIDATE_EVIDENCE_S3_NONFINAL_PART_TOO_SMALL")
        if session.bytes_written + len(chunk) > session.intent.admitted_max_content_length:
            _fail("CANDIDATE_EVIDENCE_S3_ADMITTED_LENGTH_EXCEEDED")
        if len(session.parts) >= 10_000:
            _fail("CANDIDATE_EVIDENCE_S3_PART_LIMIT_EXCEEDED")
        part_number = len(session.parts) + 1
        try:
            response = self._client.upload_part(
                Bucket=self._config.bucket, Key=session.provider_object_key,
                UploadId=session.provider_upload_id, PartNumber=part_number, Body=chunk,
            )
            etag = response.get("ETag")
            if not isinstance(etag, str) or not etag:
                _fail("CANDIDATE_EVIDENCE_S3_PART_RESPONSE_INVALID", uncertain=True)
            session.parts.append({"PartNumber": part_number, "ETag": etag, "length": len(chunk)})
            session.bytes_written += len(chunk)
            session.hasher.update(chunk)
            return session.bytes_written
        except CandidateEvidenceS3Error:
            raise
        except (BotoCoreError, ClientError) as error:
            _fail("CANDIDATE_EVIDENCE_S3_PART_UNAVAILABLE", error, uncertain=True)

    def complete(self, session: CandidateEvidenceWriteSession) -> CandidateEvidenceBinaryObjectEvidence:
        if type(session) is not CandidateEvidenceWriteSession or session.closed or not session.parts or session.bytes_written <= 0:
            _fail("CANDIDATE_EVIDENCE_S3_SESSION_INVALID")
        try:
            response = self._client.complete_multipart_upload(
                Bucket=self._config.bucket, Key=session.provider_object_key,
                UploadId=session.provider_upload_id,
                MultipartUpload={"Parts": [
                    {"PartNumber": part["PartNumber"], "ETag": part["ETag"]}
                    for part in session.parts
                ]},
            )
            version_id = response.get("VersionId")
            if not isinstance(version_id, str) or not version_id:
                _fail("CANDIDATE_EVIDENCE_S3_VERSION_EVIDENCE_MISSING", uncertain=True)
            digest = session.hasher.hexdigest()
            head = self._client.head_object(
                Bucket=self._config.bucket, Key=session.provider_object_key, VersionId=version_id,
            )
            metadata = head.get("Metadata") or {}
            if (
                head.get("ContentLength") != session.bytes_written
                or metadata.get("wilsy-intent-fingerprint") != session.intent.fingerprint
                or metadata.get("wilsy-tenant-sha3-256") != _component(session.intent.tenant_id)
                or metadata.get("wilsy-candidate-sha3-256") != _component(session.intent.candidate_id)
                or metadata.get("wilsy-evidence-sha3-256") != _component(session.intent.evidence_id)
                or metadata.get("wilsy-version-sha3-256") != _component(session.intent.evidence_version_id)
                or head.get("ServerSideEncryption") != "aws:kms"
                or head.get("SSEKMSKeyId") != self._config.kms_key_id
            ):
                _fail("CANDIDATE_EVIDENCE_S3_OBJECT_OBSERVATION_MISMATCH", uncertain=True)
            session.closed = True
            return CandidateEvidenceBinaryObjectEvidence(
                intent_fingerprint=session.intent.fingerprint,
                storage_object_reference=session.storage_object_reference,
                object_version_reference=version_id,
                provider_integrity_reference=str(head.get("ETag", "")),
                byte_length=session.bytes_written,
                content_digest_sha3_512=digest,
                completed_at=datetime.now(timezone.utc),
            )
        except CandidateEvidenceS3Error:
            raise
        except (BotoCoreError, ClientError) as error:
            _fail("CANDIDATE_EVIDENCE_S3_COMPLETE_UNCERTAIN", error, uncertain=True)

    def inspect(self, intent: CandidateEvidenceWriteIntent, evidence: CandidateEvidenceBinaryObjectEvidence) -> CandidateEvidenceBinaryObjectEvidence:
        if type(intent) is not CandidateEvidenceWriteIntent or type(evidence) is not CandidateEvidenceBinaryObjectEvidence:
            _fail("CANDIDATE_EVIDENCE_S3_INSPECTION_INPUT_INVALID")
        if evidence.intent_fingerprint != intent.fingerprint:
            _fail("CANDIDATE_EVIDENCE_S3_SCOPE_MISMATCH")
        try:
            head = self._client.head_object(
                Bucket=self._config.bucket, Key=_storage_key(intent),
                VersionId=evidence.object_version_reference,
            )
            metadata = head.get("Metadata") or {}
            if (
                head.get("ContentLength") != evidence.byte_length
                or metadata.get("wilsy-intent-fingerprint") != intent.fingerprint
                or metadata.get("wilsy-tenant-sha3-256") != _component(intent.tenant_id)
                or metadata.get("wilsy-candidate-sha3-256") != _component(intent.candidate_id)
                or metadata.get("wilsy-evidence-sha3-256") != _component(intent.evidence_id)
                or metadata.get("wilsy-version-sha3-256") != _component(intent.evidence_version_id)
                or head.get("ServerSideEncryption") != "aws:kms"
                or head.get("SSEKMSKeyId") != self._config.kms_key_id
                or str(head.get("ETag", "")) != evidence.provider_integrity_reference
            ):
                _fail("CANDIDATE_EVIDENCE_S3_INSPECTION_MISMATCH")
            return evidence
        except CandidateEvidenceS3Error:
            raise
        except (BotoCoreError, ClientError) as error:
            _fail("CANDIDATE_EVIDENCE_S3_INSPECTION_UNAVAILABLE", error)

    def list_multipart_uploads(self) -> list[dict[str, Any]]:
        """Enumerate this subsystem's multipart namespace with provider pagination."""
        uploads: list[dict[str, Any]] = []
        key_marker = None
        upload_marker = None
        try:
            while True:
                args: dict[str, Any] = {
                    "Bucket": self._config.bucket,
                    "Prefix": "hr-candidate-evidence/v1/",
                }
                if key_marker is not None:
                    args["KeyMarker"] = key_marker
                if upload_marker is not None:
                    args["UploadIdMarker"] = upload_marker
                response = self._client.list_multipart_uploads(**args)
                for item in response.get("Uploads", []):
                    key, upload_id = item.get("Key"), item.get("UploadId")
                    if isinstance(key, str) and isinstance(upload_id, str):
                        uploads.append({
                            "key": key, "upload_id": upload_id,
                            "initiated_at": item.get("Initiated"),
                        })
                if not response.get("IsTruncated"):
                    return uploads
                key_marker = response.get("NextKeyMarker")
                upload_marker = response.get("NextUploadIdMarker")
                if not key_marker or not upload_marker:
                    _fail("CANDIDATE_EVIDENCE_S3_MULTIPART_PAGINATION_INVALID")
        except CandidateEvidenceS3Error:
            raise
        except (BotoCoreError, ClientError) as error:
            _fail("CANDIDATE_EVIDENCE_S3_MULTIPART_DISCOVERY_UNAVAILABLE", error)

    def list_uploaded_parts(self, *, key: str, upload_id: str) -> list[dict[str, Any]]:
        """Read provider-confirmed part receipts for one exact multipart upload."""
        result: list[dict[str, Any]] = []
        marker = None
        try:
            while True:
                args: dict[str, Any] = {
                    "Bucket": self._config.bucket, "Key": key, "UploadId": upload_id,
                }
                if marker is not None:
                    args["PartNumberMarker"] = marker
                response = self._client.list_parts(**args)
                for item in response.get("Parts", []):
                    result.append({
                        "PartNumber": item["PartNumber"],
                        "ETag": item["ETag"],
                        "length": item["Size"],
                    })
                if not response.get("IsTruncated"):
                    return result
                marker = response.get("NextPartNumberMarker")
                if marker is None:
                    _fail("CANDIDATE_EVIDENCE_S3_PART_PAGINATION_INVALID")
        except CandidateEvidenceS3Error:
            raise
        except (BotoCoreError, ClientError) as error:
            _fail("CANDIDATE_EVIDENCE_S3_PART_DISCOVERY_UNAVAILABLE", error)

    def abort_provider_upload(self, *, key: str, upload_id: str) -> None:
        """Abort a provider upload discovered as an unowned stale orphan."""
        try:
            self._client.abort_multipart_upload(
                Bucket=self._config.bucket, Key=key, UploadId=upload_id,
            )
        except (BotoCoreError, ClientError) as error:
            _fail("CANDIDATE_EVIDENCE_S3_ORPHAN_ABORT_UNCERTAIN", error, uncertain=True)

    def inspect_completed_attempt(
        self, *, tenant_id: str, candidate_id: str, evidence_id: str,
        evidence_version_id: str, ingestion_reference: str,
        intent_fingerprint: str, media_type: str,
    ) -> CandidateEvidenceBinaryObjectEvidence | None:
        """Recover a completed exact-version object after a lost completion response."""
        key = _storage_key_for_scope(
            tenant_id, candidate_id, evidence_id, evidence_version_id, ingestion_reference,
        )
        key_marker = None
        version_marker = None
        try:
            while True:
                args: dict[str, Any] = {"Bucket": self._config.bucket, "Prefix": key}
                if key_marker is not None:
                    args["KeyMarker"] = key_marker
                if version_marker is not None:
                    args["VersionIdMarker"] = version_marker
                response = self._client.list_object_versions(**args)
                for item in response.get("Versions", []):
                    if item.get("Key") != key or not isinstance(item.get("VersionId"), str):
                        continue
                    version_id = item["VersionId"]
                    head = self._client.head_object(
                        Bucket=self._config.bucket, Key=key, VersionId=version_id,
                    )
                    metadata = head.get("Metadata") or {}
                    if (
                        metadata.get("wilsy-intent-fingerprint") != intent_fingerprint
                        or head.get("VersionId") != version_id
                        or (media_type is not None and head.get("ContentType") != media_type)
                        or metadata.get("wilsy-tenant-sha3-256") != _component(tenant_id)
                        or metadata.get("wilsy-candidate-sha3-256") != _component(candidate_id)
                        or metadata.get("wilsy-evidence-sha3-256") != _component(evidence_id)
                        or metadata.get("wilsy-version-sha3-256") != _component(evidence_version_id)
                        or head.get("ServerSideEncryption") != "aws:kms"
                        or head.get("SSEKMSKeyId") != self._config.kms_key_id
                    ):
                        _fail("CANDIDATE_EVIDENCE_S3_RECOVERY_OBSERVATION_MISMATCH")
                    length = head.get("ContentLength")
                    if type(length) is not int or not 1 <= length <= 100 * 1024 * 1024:
                        _fail("CANDIDATE_EVIDENCE_S3_RECOVERY_LENGTH_INVALID")
                    response_object = self._client.get_object(
                        Bucket=self._config.bucket, Key=key, VersionId=version_id,
                    )
                    body = response_object["Body"]
                    hasher = hashlib.sha3_512()
                    observed = 0
                    try:
                        while True:
                            chunk = body.read(8 * 1024 * 1024)
                            if not chunk:
                                break
                            observed += len(chunk)
                            if observed > length:
                                _fail("CANDIDATE_EVIDENCE_S3_RECOVERY_LENGTH_MISMATCH")
                            hasher.update(chunk)
                    finally:
                        body.close()
                    if observed != length:
                        _fail("CANDIDATE_EVIDENCE_S3_RECOVERY_LENGTH_MISMATCH")
                    return CandidateEvidenceBinaryObjectEvidence(
                        intent_fingerprint=intent_fingerprint,
                        storage_object_reference=_component(key),
                        object_version_reference=version_id,
                        provider_integrity_reference=str(head.get("ETag", "")),
                        byte_length=length,
                        content_digest_sha3_512=hasher.hexdigest(),
                        completed_at=item.get("LastModified") or datetime.now(timezone.utc),
                    )
                if not response.get("IsTruncated"):
                    return None
                key_marker = response.get("NextKeyMarker")
                version_marker = response.get("NextVersionIdMarker")
                if not key_marker:
                    _fail("CANDIDATE_EVIDENCE_S3_VERSION_PAGINATION_INVALID")
        except CandidateEvidenceS3Error:
            raise
        except (BotoCoreError, ClientError, KeyError, OSError) as error:
            _fail("CANDIDATE_EVIDENCE_S3_COMPLETED_OBJECT_RECOVERY_UNAVAILABLE", error)

    def read_verified_object(self, metadata: Any):
        """Return a bounded spool only after exact-version integrity verification."""
        key = _storage_key_for_scope(
            metadata.tenant_id, metadata.candidate_id, metadata.evidence_id,
            metadata.evidence_version_id, metadata.ingestion_reference,
        )
        if (
            metadata.storage_provider_id != PROVIDER_ID
            or _component(key) != metadata.storage_object_reference
        ):
            _fail("CANDIDATE_EVIDENCE_S3_READ_SCOPE_MISMATCH")
        spool = SpooledTemporaryFile(max_size=8 * 1024 * 1024, mode="w+b")
        body = None
        try:
            head = self._client.head_object(
                Bucket=self._config.bucket, Key=key,
                VersionId=metadata.object_version_reference,
            )
            observed_metadata = head.get("Metadata") or {}
            if (
                head.get("VersionId") != metadata.object_version_reference
                or head.get("ContentLength") != metadata.byte_length
                or head.get("ContentType") != metadata.media_type
                or str(head.get("ETag", "")) != metadata.provider_integrity_reference
                or observed_metadata.get("wilsy-tenant-sha3-256") != _component(metadata.tenant_id)
                or observed_metadata.get("wilsy-candidate-sha3-256") != _component(metadata.candidate_id)
                or observed_metadata.get("wilsy-evidence-sha3-256") != _component(metadata.evidence_id)
                or observed_metadata.get("wilsy-version-sha3-256") != _component(metadata.evidence_version_id)
                or head.get("ServerSideEncryption") != "aws:kms"
                or head.get("SSEKMSKeyId") != self._config.kms_key_id
            ):
                _fail("CANDIDATE_EVIDENCE_S3_READ_OBSERVATION_MISMATCH")
            if type(metadata.byte_length) is not int or not 1 <= metadata.byte_length <= 100 * 1024 * 1024:
                _fail("CANDIDATE_EVIDENCE_S3_READ_LENGTH_INVALID")
            response = self._client.get_object(
                Bucket=self._config.bucket, Key=key,
                VersionId=metadata.object_version_reference,
            )
            body = response["Body"]
            hasher = hashlib.sha3_512()
            observed = 0
            while True:
                chunk = body.read(8 * 1024 * 1024)
                if not chunk:
                    break
                observed += len(chunk)
                if observed > metadata.byte_length:
                    _fail("CANDIDATE_EVIDENCE_S3_READ_LENGTH_MISMATCH")
                hasher.update(chunk)
                spool.write(chunk)
            if observed != metadata.byte_length or hasher.hexdigest() != metadata.content_digest_sha3_512:
                _fail("CANDIDATE_EVIDENCE_S3_READ_DIGEST_MISMATCH")
            spool.seek(0)
            return spool
        except CandidateEvidenceS3Error:
            spool.close()
            raise
        except (BotoCoreError, ClientError, KeyError, OSError) as error:
            spool.close()
            _fail("CANDIDATE_EVIDENCE_S3_READ_UNAVAILABLE", error)
        finally:
            if body is not None:
                body.close()

    def abort(self, session: CandidateEvidenceWriteSession) -> None:
        if type(session) is not CandidateEvidenceWriteSession or session.closed:
            _fail("CANDIDATE_EVIDENCE_S3_SESSION_INVALID")
        try:
            self._client.abort_multipart_upload(
                Bucket=self._config.bucket, Key=session.provider_object_key,
                UploadId=session.provider_upload_id,
            )
            session.closed = True
        except (BotoCoreError, ClientError) as error:
            _fail("CANDIDATE_EVIDENCE_S3_ABORT_UNCERTAIN", error, uncertain=True)


__all__ = [
    "PROVIDER_ID", "CandidateEvidenceS3Error", "CandidateEvidenceS3Configuration",
    "CandidateEvidenceS3StorageAdapter",
]
