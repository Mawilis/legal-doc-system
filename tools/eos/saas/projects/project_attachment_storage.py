"""TITLE: WILSY OS Quarantined Project Attachment S3 Write Adapter
VERSION: v1.2.0-PINNED-SCANNED-VERSION-READBACK
AUTHORITY: Python EOS server-owned binary storage transport, not evidence release.
EPITOME: Bind bounded exact-task bytes to an opaque immutable versioned S3
         object with required KMS, SHA3-512 and provider HEAD readback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/projects/project_attachment_storage.py
COLLABORATION / OWNERSHIP: Projects multipart router admits IAM and validates
         exact task; ProjectAttachmentRegistry owns canonical metadata/audit.
         AWS S3 is an external byte capability, never the Projects truth source.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.2.0-PINNED-SCANNED-VERSION-READBACK permits bounded
         server-only exact-version GET after a fresh independent clean scan
         verification and complete byte SHA3-512 readback; no presigned URLs.
CHANGELOG: v1.2.0-PINNED-SCANNED-VERSION-READBACK verifies
         exact immutable S3 object/version/sha3 and GuardDuty clean tag only
         under a pinned, deployment-governed bucket security policy.
CHANGELOG: v1.2.0-PINNED-SCANNED-VERSION-READBACK stores S3 bytes at
         opaque task-command coordinates with KMS, versioning, checksum and
         exact-version HEAD reconciliation; scanner and download are excluded.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No presigned URLs or provider object coordinates
         leave EOS. No public read, untrusted preview, scanner bypass or delete.
TENANT BOUNDARY: S3 keys are digest-derived from tenant, project, task, source
         uploader and command; raw identities never appear in object keys.
AUTHORITY BOUNDARY: S3 receipt observes encrypted bytes, NOT malware safety,
         approved evidence, electronic signature, retention or availability.
TRANSACTION BOUNDARY: External S3 writes are outside Mongo transactions;
         failed canonical commit leaves inaccessible quarantine to reconcile.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from hashlib import sha3_512
from hmac import compare_digest
import json
import os
from typing import BinaryIO, Final

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from tools.eos.saas.projects.project_attachment_registry import (
    MAX_ATTACHMENT_BYTES, ProjectAttachment, ProjectAttachmentError,
    attachment_id_for_command,
)

VERSION: Final[str] = "v1.2.0-PINNED-SCANNED-VERSION-READBACK"
CHUNK_BYTES: Final[int] = 1024 * 1024


class ProjectAttachmentStorageError(RuntimeError):
    """Non-disclosing S3 capability error without provider coordinates."""

    def __init__(self, code: str) -> None:
        """Carry a bounded stable external-storage failure code."""
        self.code = code
        super().__init__(code)


def _require_config() -> tuple[str, str, str]:
    """Require explicit isolated bucket, AWS region and customer KMS key."""
    bucket = os.getenv("WILSY_PROJECT_ATTACHMENTS_S3_BUCKET", "").strip()
    region = os.getenv("WILSY_PROJECT_ATTACHMENTS_AWS_REGION", "").strip()
    kms = os.getenv("WILSY_PROJECT_ATTACHMENTS_KMS_KEY_ID", "").strip()
    if (
        not 3 <= len(bucket) <= 63
        or not all(char.islower() or char.isdigit() or char in ".-" for char in bucket)
        or not region or len(region) > 48 or not kms or len(kms) > 300
    ):
        raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_STORAGE_NOT_CONFIGURED")
    return bucket, region, kms


def _probe(stream: BinaryIO, media_type: str, limit: int) -> tuple[int, str]:
    """Derive exact SHA3-512 and byte signature without trusting MIME headers."""
    if limit <= 0 or limit > MAX_ATTACHMENT_BYTES:
        raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_SIZE_INVALID")
    digest = sha3_512()
    total = 0
    prefix = b""
    try:
        stream.seek(0)
        while True:
            chunk = stream.read(min(CHUNK_BYTES, limit + 1 - total))
            if not isinstance(chunk, bytes):
                raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_STREAM_INVALID")
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_SIZE_INVALID")
            if len(prefix) < 16:
                prefix += chunk[:16 - len(prefix)]
            digest.update(chunk)
        stream.seek(0)
    except (OSError, ValueError) as error:
        raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_STREAM_UNAVAILABLE") from error
    signatures = {
        "application/pdf": prefix.startswith(b"%PDF-"),
        "image/png": prefix.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/jpeg": prefix.startswith(b"\xff\xd8\xff"),
    }
    if not total or not signatures.get(media_type, False):
        raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_CONTENT_INVALID")
    return total, digest.hexdigest()


def store_quarantined_attachment(
    *, tenant_id: str, project_id: str, task_id: str,
    uploader_principal_id: str, idempotency_key: str,
    media_type: str, content_length: int, stream: BinaryIO,
) -> tuple[int, str, str]:
    """Write one immutable encrypted object; return byte identity and opaque receipt.

    This function never returns a URL, object key, access token or signed
    download. An exact-version HEAD must match length, digest and KMS before
    the caller may persist the QUARANTINED manifest.
    """
    bucket, region, kms = _require_config()
    try:
        attachment_id = attachment_id_for_command(
            tenant_id, project_id, task_id,
            uploader_principal_id, idempotency_key,
        )
    except ProjectAttachmentError as error:
        raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_SCOPE_INVALID") from error
    measured, content_sha3 = _probe(stream, media_type, content_length)
    if measured != content_length:
        raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_LENGTH_MISMATCH")
    opaque = sha3_512("\0".join((
        tenant_id, project_id, task_id, attachment_id,
    )).encode("utf-8")).hexdigest()
    key = "quarantine/v1/" + opaque[:2] + "/" + opaque[2:5] + "/" + opaque
    client = boto3.client("s3", region_name=region)
    metadata = {
        "sha3-512": content_sha3,
        "bytes": str(measured),
        "manifest": attachment_id,
    }
    try:
        versioning = client.get_bucket_versioning(Bucket=bucket)
        if versioning.get("Status") != "Enabled":
            raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_VERSIONING_REQUIRED")
        try:
            result = client.put_object(
                Bucket=bucket, Key=key, Body=stream,
                ContentLength=measured, ContentType=media_type,
                ServerSideEncryption="aws:kms", SSEKMSKeyId=kms,
                Metadata=metadata, IfNoneMatch="*",
            )
            version_id = result.get("VersionId")
        except ClientError as error:
            error_code = str(error.response.get("Error", {}).get("Code", ""))
            if error_code not in ("PreconditionFailed", "412"):
                raise
            # A previous attempt may have written S3 successfully but failed
            # Mongo commit. Never overwrite that object or promote its state.
            head = client.head_object(Bucket=bucket, Key=key)
            version_id = head.get("VersionId")
        if not isinstance(version_id, str) or not version_id or version_id == "null":
            raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_VERSION_UNVERIFIED")
        head = client.head_object(Bucket=bucket, Key=key, VersionId=version_id)
        observed = head.get("Metadata") or {}
        if (
            head.get("VersionId") != version_id
            or head.get("ContentLength") != measured
            or observed.get("sha3-512") != content_sha3
            or observed.get("bytes") != str(measured)
            or observed.get("manifest") != attachment_id
            or head.get("ServerSideEncryption") != "aws:kms"
            or head.get("SSEKMSKeyId") != kms
        ):
            raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_PROVIDER_MISMATCH")
        receipt = sha3_512(("\0".join((
            "aws-s3", region, bucket, key, version_id,
        ))).encode("utf-8")).hexdigest()
        return measured, content_sha3, receipt
    except (BotoCoreError, ClientError) as error:
        raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_PROVIDER_UNAVAILABLE") from error


def verify_guardduty_clean_attachment(
    attachment: ProjectAttachment,
) -> tuple[str, str]:
    """Verify a trusted GuardDuty clean tag for the original immutable object.

    Trust additionally requires a pinned, externally reviewed S3 bucket policy
    which reserves scan-tag writing to the GuardDuty service role. Environment
    configuration is not itself a scan verdict or scanner credential; missing
    policy pin, identity mismatch or unknown tag denies clearance.
    Returns the policy digest and canonical scan observation digest only.
    """
    if attachment.state != "QUARANTINED":
        raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_STATE_INVALID")
    bucket, region, kms = _require_config()
    expected_policy = os.getenv(
        "WILSY_PROJECT_ATTACHMENTS_BUCKET_POLICY_SHA3_512", "",
    ).strip().lower()
    if (
        len(expected_policy) != 128
        or any(char not in "0123456789abcdef" for char in expected_policy)
    ):
        raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_SCAN_POLICY_UNAVAILABLE")
    opaque = sha3_512("\0".join((
        attachment.tenant_id, attachment.project_id,
        attachment.task_id, attachment.attachment_id,
    )).encode("utf-8")).hexdigest()
    key = "quarantine/v1/" + opaque[:2] + "/" + opaque[2:5] + "/" + opaque
    client = boto3.client("s3", region_name=region)
    try:
        raw_policy = client.get_bucket_policy(Bucket=bucket).get("Policy")
        if not isinstance(raw_policy, str):
            raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_SCAN_POLICY_UNAVAILABLE")
        try:
            parsed = json.loads(raw_policy)
        except (ValueError, TypeError) as error:
            raise ProjectAttachmentStorageError(
                "PROJECT_ATTACHMENT_SCAN_POLICY_INVALID",
            ) from error
        current_policy = sha3_512(json.dumps(
            parsed, sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")).hexdigest()
        if not compare_digest(current_policy, expected_policy):
            raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_SCAN_POLICY_DRIFT")
        if client.get_bucket_versioning(Bucket=bucket).get("Status") != "Enabled":
            raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_VERSIONING_REQUIRED")
        observed = client.head_object(Bucket=bucket, Key=key)
        version = observed.get("VersionId")
        if not isinstance(version, str) or not version or version == "null":
            raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_VERSION_UNVERIFIED")
        receipt = sha3_512(("\0".join((
            "aws-s3", region, bucket, key, version,
        ))).encode("utf-8")).hexdigest()
        if not compare_digest(receipt, attachment.storage_receipt):
            raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_VERSION_CHANGED")
        exact = client.head_object(Bucket=bucket, Key=key, VersionId=version)
        metadata = exact.get("Metadata") or {}
        if (
            exact.get("VersionId") != version
            or exact.get("ContentLength") != attachment.size_bytes
            or metadata.get("sha3-512") != attachment.content_sha3_512
            or metadata.get("bytes") != str(attachment.size_bytes)
            or metadata.get("manifest") != attachment.attachment_id
            or exact.get("ServerSideEncryption") != "aws:kms"
            or exact.get("SSEKMSKeyId") != kms
        ):
            raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_PROVIDER_MISMATCH")
        tag_response = client.get_object_tagging(
            Bucket=bucket, Key=key, VersionId=version,
        )
        tags = tag_response.get("TagSet")
        if not isinstance(tags, list) or any(
            not isinstance(tag, dict) for tag in tags
        ):
            raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_SCAN_UNVERIFIED")
        scan = [
            tag.get("Value") for tag in tags
            if tag.get("Key") == "GuardDutyMalwareScanStatus"
        ]
        if len(scan) != 1 or scan[0] != "NO_THREATS_FOUND":
            raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_SCAN_UNVERIFIED")
        scan_evidence_digest = sha3_512(("\0".join((
            attachment.tenant_id, attachment.project_id,
            attachment.task_id, attachment.attachment_id,
            attachment.fingerprint, attachment.storage_receipt,
            current_policy, version, "NO_THREATS_FOUND",
        ))).encode("utf-8")).hexdigest()
        return current_policy, scan_evidence_digest
    except (BotoCoreError, ClientError) as error:
        raise ProjectAttachmentStorageError(
            "PROJECT_ATTACHMENT_SCAN_PROVIDER_UNAVAILABLE",
        ) from error


def read_verified_scanned_attachment(
    attachment: ProjectAttachment,
) -> bytes:
    """Read bounded exact object bytes only after a fresh trusted clean scan.

    Nothing is streamed to an HTTP recipient until full content digest,
    observed version and server-side KMS metadata are independently checked.
    Caller must separately enforce tenant/participant/task/clearance records
    both before and after this provider operation.
    """
    verify_guardduty_clean_attachment(attachment)
    bucket, region, kms = _require_config()
    opaque = sha3_512("\0".join((
        attachment.tenant_id, attachment.project_id,
        attachment.task_id, attachment.attachment_id,
    )).encode("utf-8")).hexdigest()
    key = "quarantine/v1/" + opaque[:2] + "/" + opaque[2:5] + "/" + opaque
    client = boto3.client("s3", region_name=region)
    try:
        observation = client.head_object(Bucket=bucket, Key=key)
        version = observation.get("VersionId")
        if not isinstance(version, str) or not version or version == "null":
            raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_VERSION_UNVERIFIED")
        receipt = sha3_512(("\0".join((
            "aws-s3", region, bucket, key, version,
        ))).encode("utf-8")).hexdigest()
        if not compare_digest(receipt, attachment.storage_receipt):
            raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_VERSION_CHANGED")
        response = client.get_object(Bucket=bucket, Key=key, VersionId=version)
        try:
            if (
                response.get("VersionId") != version
                or response.get("ContentLength") != attachment.size_bytes
                or response.get("ServerSideEncryption") != "aws:kms"
                or response.get("SSEKMSKeyId") != kms
            ):
                raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_PROVIDER_MISMATCH")
            stream = response.get("Body")
            if stream is None:
                raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_BYTES_UNAVAILABLE")
            data = stream.read(MAX_ATTACHMENT_BYTES + 1)
            if (
                not isinstance(data, bytes)
                or len(data) != attachment.size_bytes
                or not compare_digest(
                    sha3_512(data).hexdigest(), attachment.content_sha3_512,
                )
            ):
                raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_BYTES_MISMATCH")
            return data
        finally:
            body = response.get("Body")
            if body is not None:
                body.close()
    except (BotoCoreError, ClientError, OSError) as error:
        raise ProjectAttachmentStorageError("PROJECT_ATTACHMENT_BYTES_UNAVAILABLE") from error


__all__ = [
    "VERSION", "CHUNK_BYTES", "ProjectAttachmentStorageError",
    "store_quarantined_attachment", "verify_guardduty_clean_attachment",
    "read_verified_scanned_attachment",
]

# ARTIFACT: project_attachment_storage.py
# VERSION: v1.2.0-PINNED-SCANNED-VERSION-READBACK
# AUTHORITY BOUNDARY: external immutable encrypted bytes, not scan/release
# TENANT POSTURE: opaque digest-derived coordinates, no raw identifiers in S3
# FAIL-CLOSED POSTURE: missing KMS/version, malformed signature/digest denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
