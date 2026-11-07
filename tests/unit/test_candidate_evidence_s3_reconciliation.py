from datetime import datetime, timezone
from io import BytesIO
import hashlib

from tools.eos.saas.hr.candidate_evidence_s3_storage_adapter import (
    CandidateEvidenceS3Configuration,
    CandidateEvidenceS3StorageAdapter,
)


NOW = datetime(2026, 11, 7, 20, 0, tzinfo=timezone.utc)
PAYLOAD = b"verified recovery bytes"


def component(value):
    return hashlib.sha3_256(value.encode("utf-8")).hexdigest()


class FakeS3:
    def __init__(self):
        self.multipart_calls = []
        self.list_version_calls = []

    def list_multipart_uploads(self, **kwargs):
        self.multipart_calls.append(kwargs)
        if len(self.multipart_calls) == 1:
            return {
                "Uploads": [{"Key": "key-one", "UploadId": "upload-one", "Initiated": NOW}],
                "IsTruncated": True,
                "NextKeyMarker": "key-one",
                "NextUploadIdMarker": "upload-one",
            }
        return {
            "Uploads": [{"Key": "key-two", "UploadId": "upload-two", "Initiated": NOW}],
            "IsTruncated": False,
        }

    def list_object_versions(self, **kwargs):
        self.list_version_calls.append(kwargs)
        return {
            "Versions": [{
                "Key": self.key, "VersionId": "version-opaque", "LastModified": NOW,
            }],
            "IsTruncated": False,
        }

    def head_object(self, **kwargs):
        return {
            "ContentLength": len(PAYLOAD),
            "ContentType": "application/pdf",
            "Metadata": {
                "wilsy-intent-fingerprint": self.intent_fingerprint,
                "wilsy-tenant-sha3-256": component("tenant-1"),
                "wilsy-candidate-sha3-256": component("candidate-1"),
                "wilsy-evidence-sha3-256": component("evidence-1"),
                "wilsy-version-sha3-256": component("version-1"),
            },
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": self.kms_key_id,
            "ETag": '"provider-etag"',
        }

    def get_object(self, **kwargs):
        return {"Body": BytesIO(PAYLOAD)}


def adapter(client):
    config = CandidateEvidenceS3Configuration(
        bucket="candidate-evidence-bucket",
        region="af-south-1",
        kms_key_id="arn:aws:kms:af-south-1:123456789012:key/12345678-1234-1234-1234-123456789012",
    )
    return CandidateEvidenceS3StorageAdapter(config, client=client)


def test_lists_all_provider_multipart_pages():
    client = FakeS3()
    result = adapter(client).list_multipart_uploads()
    assert [item["upload_id"] for item in result] == ["upload-one", "upload-two"]
    assert len(client.multipart_calls) == 2
    assert client.multipart_calls[0]["Prefix"] == "hr-candidate-evidence/v1/"
    assert client.multipart_calls[1]["KeyMarker"] == "key-one"


def test_recovers_completed_version_only_after_scope_kms_and_digest_readback():
    client = FakeS3()
    storage = adapter(client)
    client.kms_key_id = storage._config.kms_key_id
    client.key = storage.object_key_for_scope(
        tenant_id="tenant-1", candidate_id="candidate-1",
        evidence_id="evidence-1", evidence_version_id="version-1",
        ingestion_reference="ingestion-1",
    )
    client.intent_fingerprint = hashlib.sha3_512(b"intent").hexdigest()
    evidence = storage.inspect_completed_attempt(
        tenant_id="tenant-1", candidate_id="candidate-1",
        evidence_id="evidence-1", evidence_version_id="version-1",
        ingestion_reference="ingestion-1",
        intent_fingerprint=client.intent_fingerprint,
        media_type="application/pdf",
    )
    assert evidence is not None
    assert evidence.object_version_reference == "version-opaque"
    assert evidence.byte_length == len(PAYLOAD)
    assert evidence.content_digest_sha3_512 == hashlib.sha3_512(PAYLOAD).hexdigest()
    assert evidence.provider_integrity_reference == '"provider-etag"'
