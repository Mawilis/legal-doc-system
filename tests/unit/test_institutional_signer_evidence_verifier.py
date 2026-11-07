from datetime import datetime, timezone

import pytest

from tools.eos.security.institutional_signer_evidence_verifier import (
    InstitutionalSignerEvidenceVerificationError,
    InstitutionalSignerEvidenceVerificationRequest,
    UnavailableInstitutionalSignerEvidenceVerifier,
    VerifiedInstitutionalSignerEvidence,
    TENANT_ID,
)


def test_request_binds_exact_tenant_certificate_principal_and_reference():
    request = InstitutionalSignerEvidenceVerificationRequest(
        tenant_id=TENANT_ID,
        certificate_fingerprint_sha256="a" * 64,
        subject_principal_id="PRINCIPAL-1",
        evidence_reference="evidence://identity/123",
        evidence_kind="IDENTITY_PROOFING",
        evaluated_at=datetime(2026, 11, 7, tzinfo=timezone.utc),
    )
    assert request.tenant_id == TENANT_ID
    assert request.certificate_fingerprint_sha256 == "a" * 64


@pytest.mark.parametrize("tenant", ["other-tenant", "global", "*"])
def test_request_rejects_noncanonical_tenant(tenant):
    with pytest.raises(InstitutionalSignerEvidenceVerificationError) as error:
        InstitutionalSignerEvidenceVerificationRequest(
            tenant_id=tenant,
            certificate_fingerprint_sha256="a" * 64,
            subject_principal_id="PRINCIPAL-1",
            evidence_reference="evidence://identity/123",
            evidence_kind="IDENTITY_PROOFING",
            evaluated_at=datetime(2026, 11, 7, tzinfo=timezone.utc),
        )
    assert error.value.code == "INSTITUTIONAL_SIGNER_TENANT_SCOPE_INVALID"


def test_request_rejects_malformed_certificate_fingerprint():
    with pytest.raises(InstitutionalSignerEvidenceVerificationError) as error:
        InstitutionalSignerEvidenceVerificationRequest(
            tenant_id=TENANT_ID,
            certificate_fingerprint_sha256="not-a-fingerprint",
            subject_principal_id="PRINCIPAL-1",
            evidence_reference="evidence://identity/123",
            evidence_kind="IDENTITY_PROOFING",
            evaluated_at=datetime(2026, 11, 7, tzinfo=timezone.utc),
        )
    assert error.value.code == "INSTITUTIONAL_SIGNER_CERTIFICATE_FINGERPRINT_INVALID"


def test_success_result_cannot_be_forged_by_callers():
    with pytest.raises(InstitutionalSignerEvidenceVerificationError) as error:
        VerifiedInstitutionalSignerEvidence()
    assert error.value.code == "INSTITUTIONAL_SIGNER_EVIDENCE_AUTHORITY_UNAVAILABLE"


@pytest.mark.parametrize("method,kwargs", [
    ("verify_enrollment", {
        "tenant_id": TENANT_ID,
        "certificate_fingerprint_sha256": "a" * 64,
        "subject_principal_id": "PRINCIPAL-1",
        "identity_proofing_reference": "evidence://identity/123",
        "signatory_mandate_reference": "evidence://mandate/456",
        "evaluated_at": datetime(2026, 11, 7, tzinfo=timezone.utc),
        "session": object(),
    }),
    ("verify_approval", {
        "tenant_id": TENANT_ID,
        "certificate_fingerprint_sha256": "a" * 64,
        "enrollment_requester_principal_id": "PRINCIPAL-1",
        "reviewer_principal_id": "PRINCIPAL-2",
        "approval_attestation_reference": "evidence://approval/789",
        "evaluated_at": datetime(2026, 11, 7, tzinfo=timezone.utc),
        "session": object(),
    }),
])
def test_unavailable_authoritative_adapter_fails_closed(method, kwargs):
    verifier = UnavailableInstitutionalSignerEvidenceVerifier()
    with pytest.raises(InstitutionalSignerEvidenceVerificationError) as error:
        getattr(verifier, method)(**kwargs)
    assert error.value.code == "INSTITUTIONAL_SIGNER_EVIDENCE_AUTHORITY_UNAVAILABLE"
