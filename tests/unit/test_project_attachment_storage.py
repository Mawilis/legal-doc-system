"""TITLE: WILSY OS Encrypted Project Quarantine Upload Adapter Certificate
VERSION: v1.1.0-PINNED-GUARDDUTY-CLEARANCE-CERT
AUTHORITY: Synthetic S3 byte/signature/hash and provider readback tests.
EPITOME: Fail closed on executable payloads, missing KMS/versioning and
         mismatch in provider receipt; object coords stay opaque.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_attachment_storage.py
COLLABORATION / OWNERSHIP: project_attachment_storage uses boto3 S3 provider.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.1.0-PINNED-GUARDDUTY-CLEARANCE-CERT certifies pinned policy, exact-version GuardDuty clean tag and fail-closed mismatches through synthetic provider responses.
CHANGELOG: v1.1.0-PINNED-GUARDDUTY-CLEARANCE-CERT pins exact
         byte SHA3, encrypted write, version HEAD and opaque S3 coordinates.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Mock storage only; no real S3 credentials.
TENANT BOUNDARY: S3 object keys omit raw tenant/project/task identifiers.
AUTHORITY BOUNDARY: Provider receipt does not grant safe-file availability.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from hashlib import sha3_512
from datetime import datetime, timezone
import json
from io import BytesIO

import pytest

from tools.eos.saas.projects import project_attachment_storage as storage
from tools.eos.saas.projects.project_attachment_registry import (
    ProjectAttachment, attachment_id_for_command,
)

TENANT = "synthetic-tenant"
PROJECT = "prj-" + "a" * 48
TASK = "ptk-" + "b" * 48
ACTOR = "participant-a"
KEY = "upload-key"
CONTENT = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"


def _write(**changes):
    """Supply one deterministic test-only task upload command."""
    fields = {
        "tenant_id": TENANT, "project_id": PROJECT,
        "task_id": TASK, "uploader_principal_id": ACTOR,
        "idempotency_key": KEY, "media_type": "application/pdf",
        "content_length": len(CONTENT), "stream": BytesIO(CONTENT),
    }
    fields.update(changes)
    return storage.store_quarantined_attachment(**fields)


class FakeS3:
    """Require KMS encryption, no overwrite and exact-version HEAD."""
    def __init__(self, versioning="Enabled", mismatch=False):
        self.versioning = versioning
        self.mismatch = mismatch
        self.key = ""
        self.metadata = {}
        self.content_length = 0
        self.kms = ""

    def get_bucket_versioning(self, Bucket):
        assert Bucket == "synthetic-bucket"
        return {"Status": self.versioning}

    def put_object(self, **values):
        assert values["Bucket"] == "synthetic-bucket"
        self.key = values["Key"]
        assert TENANT not in self.key
        assert PROJECT not in self.key
        assert TASK not in self.key
        assert ACTOR not in self.key
        assert values["IfNoneMatch"] == "*"
        assert values["ServerSideEncryption"] == "aws:kms"
        assert values["SSEKMSKeyId"] == "synthetic-kms-key"
        assert values["ContentType"] == "application/pdf"
        self.content_length = values["ContentLength"]
        self.metadata = values["Metadata"]
        self.kms = values["SSEKMSKeyId"]
        assert values["Body"].read() == CONTENT
        return {"VersionId": "version-one"}

    def head_object(self, **values):
        assert values["Key"] == self.key
        assert values["VersionId"] == "version-one"
        return {
            "VersionId": "version-one",
            "ContentLength": self.content_length + (1 if self.mismatch else 0),
            "Metadata": self.metadata,
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": self.kms,
        }


@pytest.fixture
def configured(monkeypatch):
    """Set isolated test provider configuration without external AWS calls."""
    monkeypatch.setenv("WILSY_PROJECT_ATTACHMENTS_S3_BUCKET", "synthetic-bucket")
    monkeypatch.setenv("WILSY_PROJECT_ATTACHMENTS_AWS_REGION", "af-south-1")
    monkeypatch.setenv("WILSY_PROJECT_ATTACHMENTS_KMS_KEY_ID", "synthetic-kms-key")


def test_verified_immutable_s3_upload_receipt(configured, monkeypatch):
    """Provider HEAD and byte digest must match before receipt can be trusted."""
    fake = FakeS3()
    monkeypatch.setattr(storage.boto3, "client", lambda *a, **k: fake)
    total, digest, receipt = _write()
    assert total == len(CONTENT)
    assert digest == sha3_512(CONTENT).hexdigest()
    assert len(receipt) == 128
    assert not any(value in receipt for value in (TENANT, ACTOR, PROJECT, TASK))
    assert fake.metadata["sha3-512"] == digest


def test_missing_versioning_fails_closed(configured, monkeypatch):
    """Quarantine object cannot be mutable even if ciphertext is encrypted."""
    monkeypatch.setattr(storage.boto3, "client", lambda *a, **k: FakeS3(versioning="Suspended"))
    with pytest.raises(storage.ProjectAttachmentStorageError, match="VERSIONING_REQUIRED"):
        _write()


def test_bad_provider_length_cannot_generate_canonical_receipt(configured, monkeypatch):
    """S3 observation mismatch denies manifest commit."""
    monkeypatch.setattr(storage.boto3, "client", lambda *a, **k: FakeS3(mismatch=True))
    with pytest.raises(storage.ProjectAttachmentStorageError, match="PROVIDER_MISMATCH"):
        _write()


@pytest.mark.parametrize("payload,media", [
    (b"not a pdf", "application/pdf"),
    (b"MZ" + b"A" * 50, "application/pdf"),
    (b"\x89PNG\r\n", "image/png"),
    (b"hello", "text/plain"),
])
def test_mismatched_signatures_and_unsafe_media_rejected(payload, media):
    """A content type declared by the client never supersedes byte identity."""
    with pytest.raises(storage.ProjectAttachmentStorageError, match="CONTENT_INVALID"):
        storage._probe(BytesIO(payload), media, len(payload))



class FakeScanS3(FakeS3):
    """Synthetic GuardDuty policy/tag inspection, never real AWS proof."""

    def __init__(self, *, verdict="NO_THREATS_FOUND", version="version-one"):
        super().__init__()
        self.verdict = verdict
        self.version = version
        self.policy = {"Version": "2012-10-17", "Statement": [
            {"Effect": "Deny", "Action": "s3:PutObjectTagging",
             "Principal": "*", "Resource": "synthetic-scoped-bucket"}
        ]}

    def get_bucket_policy(self, Bucket):
        assert Bucket == "synthetic-bucket"
        return {"Policy": json.dumps(self.policy)}

    def head_object(self, **values):
        assert values["Bucket"] == "synthetic-bucket"
        assert values["Key"] == self.key
        assert values.get("VersionId") in (None, self.version)
        return {
            "VersionId": self.version, "ContentLength": self.content_length,
            "Metadata": self.metadata, "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": self.kms,
        }

    def get_object_tagging(self, **values):
        assert values["VersionId"] == self.version
        assert values["Key"] == self.key
        return {"TagSet": [
            {"Key": "GuardDutyMalwareScanStatus", "Value": self.verdict}
        ]}


def _scan_case(monkeypatch, provider):
    """Persist a quarantine manifest only after an exact synthetic S3 write."""
    monkeypatch.setattr(storage.boto3, "client", lambda *a, **k: provider)
    size, digest, receipt = _write()
    policy_digest = sha3_512(json.dumps(
        provider.policy, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()
    monkeypatch.setenv(
        "WILSY_PROJECT_ATTACHMENTS_BUCKET_POLICY_SHA3_512", policy_digest,
    )
    manifest = ProjectAttachment(
        tenant_id=TENANT, project_id=PROJECT, task_id=TASK,
        attachment_id=attachment_id_for_command(TENANT, PROJECT, TASK, ACTOR, KEY),
        uploader_principal_id=ACTOR, filename="design.pdf",
        media_type="application/pdf", size_bytes=size,
        content_sha3_512=digest, storage_receipt=receipt,
        created_at=datetime(2026, 11, 18, tzinfo=timezone.utc),
    )
    return manifest, policy_digest


def test_guardduty_clean_requires_exact_original_version_and_pinned_policy(
    configured, monkeypatch,
):
    """Only a fresh clean tag on the immutable original may yield scan evidence."""
    provider = FakeScanS3()
    manifest, pin = _scan_case(monkeypatch, provider)
    observed_pin, scan_evidence = storage.verify_guardduty_clean_attachment(manifest)
    assert observed_pin == pin
    assert len(scan_evidence) == 128
    assert scan_evidence != manifest.content_sha3_512


@pytest.mark.parametrize("verdict", [
    "THREATS_FOUND", "UNSUPPORTED", "FAILED", "ACCESS_DENIED",
])
def test_guardduty_nonclean_verdicts_deny_clearance(
    configured, monkeypatch, verdict,
):
    """No attacker-supplied or incomplete scanner outcome becomes clean."""
    provider = FakeScanS3(verdict=verdict)
    manifest, _ = _scan_case(monkeypatch, provider)
    with pytest.raises(storage.ProjectAttachmentStorageError, match="SCAN_UNVERIFIED"):
        storage.verify_guardduty_clean_attachment(manifest)


def test_guardduty_bucket_policy_drift_denies_clearance(configured, monkeypatch):
    """Provider policy change after pinning invalidates scan trust."""
    provider = FakeScanS3()
    manifest, _ = _scan_case(monkeypatch, provider)
    provider.policy = {"Version": "2012-10-17", "Statement": []}
    with pytest.raises(storage.ProjectAttachmentStorageError, match="SCAN_POLICY_DRIFT"):
        storage.verify_guardduty_clean_attachment(manifest)


def test_guardduty_provider_version_drift_denies_clearance(configured, monkeypatch):
    """A different latest object version never inherits an older clean tag."""
    provider = FakeScanS3()
    manifest, _ = _scan_case(monkeypatch, provider)
    provider.version = "version-two"
    with pytest.raises(storage.ProjectAttachmentStorageError, match="VERSION_CHANGED"):
        storage.verify_guardduty_clean_attachment(manifest)


def test_guardduty_missing_security_policy_pin_denies_clearance(configured, monkeypatch):
    """Deployment without an externally reviewed policy pin fails closed."""
    provider = FakeScanS3()
    manifest, _ = _scan_case(monkeypatch, provider)
    monkeypatch.delenv("WILSY_PROJECT_ATTACHMENTS_BUCKET_POLICY_SHA3_512")
    with pytest.raises(storage.ProjectAttachmentStorageError, match="SCAN_POLICY_UNAVAILABLE"):
        storage.verify_guardduty_clean_attachment(manifest)


# ARTIFACT: test_project_attachment_storage.py
# VERSION: v1.1.0-PINNED-GUARDDUTY-CLEARANCE-CERT
# AUTHORITY BOUNDARY: simulated provider only; not real malware scan
# TENANT POSTURE: opaque key, no browser-provided coordinates
# FAIL-CLOSED POSTURE: signature, missing KMS/version or provider mismatch
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
