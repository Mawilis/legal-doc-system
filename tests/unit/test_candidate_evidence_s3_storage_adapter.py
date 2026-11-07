from datetime import datetime, timezone
import hashlib

import pytest

from tools.eos.saas.hr.candidate_evidence_storage import CandidateEvidenceWriteIntent, CandidateEvidenceStorageError
from tools.eos.saas.hr.candidate_evidence_s3_storage_adapter import (
    CandidateEvidenceS3Configuration, CandidateEvidenceS3StorageAdapter,
    CandidateEvidenceS3Error,
)


class FakeS3:
    def __init__(self):
        self.uploads = {}
        self.objects = {}
        self.begin_args = None

    def create_multipart_upload(self, **kwargs):
        self.begin_args = kwargs
        self.uploads["upload-1"] = {"args": kwargs, "parts": {}}
        return {"UploadId": "upload-1"}

    def upload_part(self, **kwargs):
        body = kwargs["Body"]
        etag = hashlib.sha3_256(body).hexdigest()
        self.uploads[kwargs["UploadId"]]["parts"][kwargs["PartNumber"]] = (body, etag)
        return {"ETag": etag}

    def complete_multipart_upload(self, **kwargs):
        upload = self.uploads[kwargs["UploadId"]]
        body = b"".join(upload["parts"][p["PartNumber"]][0] for p in kwargs["MultipartUpload"]["Parts"])
        key = kwargs["Key"]
        version = "version-1"
        self.objects[(key, version)] = {
            "body": body, "metadata": upload["args"]["Metadata"],
            "etag": "opaque-etag", "encryption": upload["args"]["ServerSideEncryption"],
            "kms": upload["args"]["SSEKMSKeyId"],
        }
        return {"VersionId": version}

    def head_object(self, **kwargs):
        obj = self.objects[(kwargs["Key"], kwargs["VersionId"])]
        return {
            "ContentLength": len(obj["body"]), "Metadata": obj["metadata"],
            "ETag": obj["etag"], "ServerSideEncryption": obj["encryption"],
            "SSEKMSKeyId": obj["kms"],
        }

    def abort_multipart_upload(self, **kwargs):
        self.uploads.pop(kwargs["UploadId"], None)


def intent():
    return CandidateEvidenceWriteIntent(
        tenant_id="WILSYTENANT-4CD2FZ4O", candidate_id="CAN-001",
        evidence_id="EVD-001", evidence_version_id="EVDV-001",
        ingestion_reference="ING-001", media_type="application/pdf",
        original_filename="profile.pdf", admitted_max_content_length=1024 * 1024,
    )


def adapter(fake):
    return CandidateEvidenceS3StorageAdapter(
        CandidateEvidenceS3Configuration(
            bucket="wilsy-hr-cert-b005e551fbe35", region="af-south-1",
            kms_key_id="arn:aws:kms:af-south-1:123456789012:key/00000000-0000-0000-0000-000000000000",
        ), client=fake,
    )


def test_candidate_evidence_s3_upload_is_kms_encrypted_and_exact_version_inspected():
    fake = FakeS3()
    store = adapter(fake)
    value = intent()
    session = store.begin(value)
    assert "WILSYTENANT" not in session.provider_object_key
    assert fake.begin_args["ServerSideEncryption"] == "aws:kms"
    assert fake.begin_args["SSEKMSKeyId"].startswith("arn:aws:kms:")
    body = b"%PDF-candidate-evidence"
    assert store.write_chunk(session, body) == len(body)
    evidence = store.complete(session)
    assert evidence.byte_length == len(body)
    assert evidence.content_digest_sha3_512 == hashlib.sha3_512(body).hexdigest()
    assert store.inspect(value, evidence) == evidence


def test_candidate_evidence_s3_rejects_cross_intent_inspection():
    fake = FakeS3()
    store = adapter(fake)
    value = intent()
    session = store.begin(value)
    store.write_chunk(session, b"document")
    evidence = store.complete(session)
    other = CandidateEvidenceWriteIntent(
        tenant_id=value.tenant_id, candidate_id="CAN-OTHER",
        evidence_id=value.evidence_id, evidence_version_id=value.evidence_version_id,
        ingestion_reference=value.ingestion_reference, media_type=value.media_type,
        original_filename=value.original_filename, admitted_max_content_length=1024,
    )
    with pytest.raises(CandidateEvidenceS3Error, match="SCOPE_MISMATCH"):
        store.inspect(other, evidence)


def test_candidate_evidence_s3_requires_kms_configuration_and_aborts_upload():
    with pytest.raises(ValueError, match="KMS_REQUIRED"):
        CandidateEvidenceS3Configuration(bucket="wilsy-hr-cert-b005e551fbe35", region="af-south-1", kms_key_id="")
    fake = FakeS3()
    store = adapter(fake)
    session = store.begin(intent())
    store.abort(session)
    assert session.closed is True
    assert "upload-1" not in fake.uploads


def test_candidate_evidence_write_intent_rejects_pseudo_tenants_and_oversize():
    with pytest.raises(CandidateEvidenceStorageError, match="TENANT_REQUIRED"):
        CandidateEvidenceWriteIntent(
            tenant_id="MASTER", candidate_id="CAN-1", evidence_id="EVD-1",
            evidence_version_id="VER-1", ingestion_reference="ING-1",
            media_type="application/pdf", original_filename="x.pdf",
            admitted_max_content_length=100,
        )
