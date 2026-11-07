from datetime import datetime, timedelta, timezone
from dataclasses import replace

import pytest

from tools.eos.saas.domain.candidate_evidence import (
    CandidateEvidenceError, CandidateEvidenceKind, CandidateEvidenceObjectMetadata,
)

NOW = datetime(2026, 11, 7, 12, tzinfo=timezone.utc)


def evidence(kind=CandidateEvidenceKind.CANDIDATE_PROFILE, offer_id=None):
    return CandidateEvidenceObjectMetadata(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        candidate_id="CAN-001",
        evidence_id="EVD-001",
        evidence_version_id="EVDV-001",
        evidence_kind=kind,
        media_type="application/pdf",
        original_filename="candidate-profile.pdf",
        byte_length=2048,
        content_digest_sha3_512="a" * 128,
        storage_provider_id="aws_s3",
        storage_object_reference="opaque-object-reference-001",
        object_version_reference="opaque-version-reference-001",
        provider_integrity_reference="opaque-provider-integrity-001",
        ingestion_reference="ING-001",
        created_at=NOW,
        created_by_principal_id="principal-hr-1",
        offer_id=offer_id,
        retention_until=NOW + timedelta(days=365),
    )


def test_candidate_profile_metadata_is_immutable_and_round_trips_without_binary_bytes():
    value = evidence()
    hydrated = CandidateEvidenceObjectMetadata.from_dict(value.to_dict())
    assert hydrated == value
    assert "content_bytes" not in value.to_dict()
    assert "candidate_name" not in value.to_dict()
    assert len(value.fingerprint) == 128


def test_signed_offer_evidence_requires_exact_offer_scope():
    with pytest.raises(CandidateEvidenceError, match="SIGNED_OFFER_REQUIRES_OFFER"):
        evidence(CandidateEvidenceKind.SIGNED_OFFER)
    value = evidence(CandidateEvidenceKind.SIGNED_OFFER, "OFFER-001")
    assert value.offer_id == "OFFER-001"


def test_profile_evidence_cannot_be_mislabelled_as_offer_evidence():
    with pytest.raises(CandidateEvidenceError, match="PROFILE_OFFER_SCOPE_FORBIDDEN"):
        evidence(CandidateEvidenceKind.CANDIDATE_PROFILE, "OFFER-001")


def test_retention_cannot_precede_custody_creation():
    with pytest.raises(CandidateEvidenceError, match="RETENTION_INVALID"):
        replace(evidence(), retention_until=NOW - timedelta(days=1))


def test_metadata_fingerprint_detects_tampering():
    value = evidence()
    payload = value.to_dict()
    payload["storage_object_reference"] = "tampered-object-reference"
    with pytest.raises(CandidateEvidenceError, match="FINGERPRINT_MISMATCH"):
        CandidateEvidenceObjectMetadata.from_dict(payload)
