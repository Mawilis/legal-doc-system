from datetime import datetime, timezone

import pytest

from tools.eos.security.institutional_signer_source_adapters import (
    InstitutionalSignerSourceAdapterError,
    InstitutionalSignerSourceEvidence,
    InstitutionalSignerSourceLookup,
    UnavailableInstitutionalSignerSourceAdapterSet,
)
from tools.eos.security.institutional_signer_evidence_verifier import TENANT_ID


NOW = datetime(2026, 11, 8, tzinfo=timezone.utc)


def lookup(**overrides):
    values = {
        "tenant_id": TENANT_ID,
        "evidence_kind": "IDENTITY_PROOFING",
        "evidence_reference": "evidence://identity/record-1",
        "subject_principal_id": "PRINCIPAL-1",
        "certificate_fingerprint_sha256": "a" * 64,
        "evaluated_at": NOW,
    }
    values.update(overrides)
    return InstitutionalSignerSourceLookup(**values)


def test_lookup_is_exactly_tenant_principal_certificate_and_time_bound():
    request = lookup()
    assert request.tenant_id == TENANT_ID
    assert request.subject_principal_id == "PRINCIPAL-1"
    assert request.certificate_fingerprint_sha256 == "a" * 64


@pytest.mark.parametrize("tenant", ["*", "global", "OTHER-TENANT"])
def test_lookup_rejects_cross_tenant_scope(tenant):
    with pytest.raises(InstitutionalSignerSourceAdapterError) as error:
        lookup(tenant_id=tenant)
    assert error.value.code == "INSTITUTIONAL_SIGNER_SOURCE_TENANT_SCOPE_INVALID"


def test_lookup_rejects_unknown_evidence_kind_and_bad_fingerprint():
    with pytest.raises(InstitutionalSignerSourceAdapterError):
        lookup(evidence_kind="IAM_ROLE_GRANT")
    with pytest.raises(InstitutionalSignerSourceAdapterError):
        lookup(certificate_fingerprint_sha256="not-a-fingerprint")


def test_lookup_rejects_naive_evaluation_time():
    with pytest.raises(InstitutionalSignerSourceAdapterError) as error:
        lookup(evaluated_at=datetime(2026, 11, 8))
    assert error.value.code == "INSTITUTIONAL_SIGNER_SOURCE_EVALUATED_AT_INVALID"


def test_source_envelope_requires_authenticated_response_reference_and_validity():
    response = InstitutionalSignerSourceEvidence(
        evidence_kind="IDENTITY_PROOFING",
        evidence_reference="evidence://identity/record-1",
        tenant_id=TENANT_ID,
        source_system_id="DHA-NPR-VERIFICATION",
        source_record_id="record-1",
        source_revision="revision-7",
        subject_principal_id="PRINCIPAL-1",
        certificate_fingerprint_sha256="a" * 64,
        evidence_fingerprint_sha256="b" * 64,
        status="ACTIVE",
        valid_from=NOW,
        valid_until=datetime(2027, 1, 1, tzinfo=timezone.utc),
        revoked=False,
        observed_at=NOW,
        response_signature_reference="signature://response/123",
    )
    assert response.source_revision == "revision-7"
    assert response.response_signature_reference.startswith("signature://")


def test_source_envelope_rejects_invalid_validity_interval():
    with pytest.raises(InstitutionalSignerSourceAdapterError) as error:
        InstitutionalSignerSourceEvidence(
            evidence_kind="IDENTITY_PROOFING",
            evidence_reference="evidence://identity/record-1",
            tenant_id=TENANT_ID,
            source_system_id="DHA-NPR-VERIFICATION",
            source_record_id="record-1",
            source_revision="revision-7",
            subject_principal_id="PRINCIPAL-1",
            certificate_fingerprint_sha256="a" * 64,
            evidence_fingerprint_sha256="b" * 64,
            status="ACTIVE",
            valid_from=NOW,
            valid_until=NOW,
            revoked=False,
            observed_at=NOW,
            response_signature_reference="signature://response/123",
        )
    assert error.value.code == "INSTITUTIONAL_SIGNER_SOURCE_VALIDITY_INTERVAL_INVALID"


@pytest.mark.parametrize(
    "method,kind",
    [
        ("read_identity_proofing", "IDENTITY_PROOFING"),
        ("read_signatory_mandate", "SIGNATORY_MANDATE"),
        ("read_independent_approval", "INDEPENDENT_APPROVAL"),
    ],
)
def test_unavailable_source_adapter_set_denies_all_authorities(method, kind):
    with pytest.raises(InstitutionalSignerSourceAdapterError) as error:
        getattr(UnavailableInstitutionalSignerSourceAdapterSet(), method)(
            lookup=lookup()
        )
    assert error.value.code == f"INSTITUTIONAL_SIGNER_SOURCE_{kind}_AUTHORITY_UNAVAILABLE"
