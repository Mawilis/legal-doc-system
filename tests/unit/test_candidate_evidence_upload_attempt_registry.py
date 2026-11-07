from datetime import datetime, timezone, timedelta

import pytest

from tools.eos.saas.hr.candidate_evidence_upload_attempt_registry import (
    CandidateEvidenceUploadAttempt,
    UploadAttemptConflict,
    UploadAttemptStatus,
)

NOW = datetime(2026, 11, 7, 18, 0, tzinfo=timezone.utc)
HEX = "a" * 128


def attempt():
    return CandidateEvidenceUploadAttempt(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        upload_attempt_id="UPL-001",
        candidate_id="CAN-001",
        evidence_id="EVD-001",
        evidence_version_id="VER-001",
        ingestion_reference="ING-001",
        intent_fingerprint=HEX,
        provider_id="AWS_S3_KMS",
        provider_upload_id="multipart-opaque-id",
        provider_object_reference="opaque-object-ref",
        status=UploadAttemptStatus.INITIATED,
        revision=1,
        created_at=NOW,
        updated_at=NOW,
        offer_id="OFFER-001",
    )


def test_upload_attempt_progress_is_revision_guarded_and_auditable():
    initial = attempt()
    progressed = initial.advance(
        status=UploadAttemptStatus.PARTS_UPLOADED,
        expected_revision=1,
        occurred_at=NOW + timedelta(minutes=1),
        parts=({"PartNumber": 1, "ETag": '"part-1"', "length": 8 * 1024 * 1024},),
        byte_length=8 * 1024 * 1024,
    )
    assert progressed.revision == 2
    assert progressed.parts[0]["PartNumber"] == 1
    assert progressed.fingerprint != initial.fingerprint


def test_uncertain_completion_can_be_reconciled_but_not_assumed_success():
    uncertain = attempt().advance(
        status=UploadAttemptStatus.COMPLETION_UNCERTAIN,
        expected_revision=1,
        occurred_at=NOW + timedelta(minutes=1),
        failure_code="S3_COMPLETE_RESPONSE_LOST",
    )
    assert uncertain.status is UploadAttemptStatus.COMPLETION_UNCERTAIN
    verified = uncertain.advance(
        status=UploadAttemptStatus.PROVIDER_VERIFIED,
        expected_revision=2,
        occurred_at=NOW + timedelta(minutes=2),
        object_version_reference="s3-version-opaque",
        content_digest_sha3_512="b" * 128,
        provider_integrity_reference='"verified-etag"',
        byte_length=1234,
    )
    assert verified.status is UploadAttemptStatus.PROVIDER_VERIFIED
    assert verified.object_version_reference == "s3-version-opaque"


def test_custody_registration_only_follows_provider_verification():
    with pytest.raises(UploadAttemptConflict, match="UPLOAD_ATTEMPT_TRANSITION_CONFLICT"):
        attempt().advance(
            status=UploadAttemptStatus.CUSTODY_REGISTERED,
            expected_revision=1,
            occurred_at=NOW + timedelta(minutes=1),
        )


def test_stale_revision_and_terminal_state_are_rejected():
    aborted = attempt().advance(
        status=UploadAttemptStatus.ABORTED,
        expected_revision=1,
        occurred_at=NOW + timedelta(minutes=1),
    )
    with pytest.raises(UploadAttemptConflict):
        aborted.advance(
            status=UploadAttemptStatus.PROVIDER_VERIFIED,
            expected_revision=2,
            occurred_at=NOW + timedelta(minutes=2),
        )
    with pytest.raises(UploadAttemptConflict):
        attempt().advance(
            status=UploadAttemptStatus.PARTS_UPLOADED,
            expected_revision=0,
            occurred_at=NOW + timedelta(minutes=1),
        )


def test_attempt_scope_and_fingerprint_are_immutable():
    value = attempt()
    with pytest.raises(ValueError, match="UPLOAD_ATTEMPT_FINGERPRINT_MISMATCH"):
        CandidateEvidenceUploadAttempt(
            tenant_id=value.tenant_id, upload_attempt_id=value.upload_attempt_id,
            candidate_id=value.candidate_id, evidence_id=value.evidence_id,
            evidence_version_id=value.evidence_version_id, ingestion_reference=value.ingestion_reference,
            intent_fingerprint=value.intent_fingerprint, provider_id=value.provider_id,
            provider_upload_id=value.provider_upload_id, provider_object_reference=value.provider_object_reference,
            status=value.status, revision=value.revision, created_at=value.created_at,
            updated_at=value.updated_at, offer_id=value.offer_id, fingerprint="f" * 128,
        )
