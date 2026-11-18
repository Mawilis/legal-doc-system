"""TITLE: WILSY OS Encrypted Project Quarantine Upload Adapter Certificate
VERSION: v1.0.0-KMS-VERSIONED-OBJECT-RECONCILIATION-CERT
AUTHORITY: Synthetic S3 byte/signature/hash and provider readback tests.
EPITOME: Fail closed on executable payloads, missing KMS/versioning and
         mismatch in provider receipt; object coords stay opaque.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_attachment_storage.py
COLLABORATION / OWNERSHIP: project_attachment_storage uses boto3 S3 provider.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-KMS-VERSIONED-OBJECT-RECONCILIATION-CERT pins exact
         byte SHA3, encrypted write, version HEAD and opaque S3 coordinates.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Mock storage only; no real S3 credentials.
TENANT BOUNDARY: S3 object keys omit raw tenant/project/task identifiers.
AUTHORITY BOUNDARY: Provider receipt does not grant safe-file availability.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from hashlib import sha3_512
from io import BytesIO

import pytest

from tools.eos.saas.projects import project_attachment_storage as storage

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


# ARTIFACT: test_project_attachment_storage.py
# VERSION: v1.0.0-KMS-VERSIONED-OBJECT-RECONCILIATION-CERT
# AUTHORITY BOUNDARY: simulated provider only; not real malware scan
# TENANT POSTURE: opaque key, no browser-provided coordinates
# FAIL-CLOSED POSTURE: signature, missing KMS/version or provider mismatch
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
