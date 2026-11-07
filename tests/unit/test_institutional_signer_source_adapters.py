from datetime import datetime, timezone
import base64
from dataclasses import replace

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import pytest

from tools.eos.security.institutional_signer_source_adapters import (
    InstitutionalSignerSourceAdapterError,
    InstitutionalSignerSourceEvidence,
    InstitutionalSignerSourceLookup,
    UnavailableInstitutionalSignerSourceAdapterSet,
    Ed25519InstitutionalSignerSourceResponseAuthenticator,
    AuthenticatedInstitutionalSignerSourceAdapterSet,
    _canonical_source_response_payload,
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
        response_signing_key_id="dha-response-key-2026",
        response_signature_base64=base64.b64encode(b"0" * 64).decode("ascii"),
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
            response_signing_key_id="dha-response-key-2026",
            response_signature_base64=base64.b64encode(b"0" * 64).decode("ascii"),
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



class _FakeAdapter:
    source_system_id = "DHA-NPR-VERIFICATION"
    supported_evidence_kind = "IDENTITY_PROOFING"

    def __init__(self, response):
        self.response = response

    def read_evidence(self, *, lookup):
        return self.response


class _FakeAuthenticator:
    def __init__(self):
        self.calls = []

    def authenticate_response(self, *, expected_source_system_id, lookup, response):
        self.calls.append((expected_source_system_id, lookup, response))


def source_response(**overrides):
    values = {
        "evidence_kind": "IDENTITY_PROOFING",
        "evidence_reference": "evidence://identity/record-1",
        "tenant_id": TENANT_ID,
        "source_system_id": "DHA-NPR-VERIFICATION",
        "source_record_id": "record-1",
        "source_revision": "revision-7",
        "subject_principal_id": "PRINCIPAL-1",
        "certificate_fingerprint_sha256": "a" * 64,
        "evidence_fingerprint_sha256": "b" * 64,
        "status": "ACTIVE",
        "valid_from": NOW,
        "valid_until": datetime(2027, 1, 1, tzinfo=timezone.utc),
        "revoked": False,
        "observed_at": NOW,
        "response_signature_reference": "signature://response/123",
        "response_signing_key_id": "dha-response-key-2026",
        "response_signature_base64": base64.b64encode(b"0" * 64).decode("ascii"),
    }
    values.update(overrides)
    return InstitutionalSignerSourceEvidence(**values)


def test_authenticated_read_verifies_source_and_exact_scope():
    from tools.eos.security.institutional_signer_source_adapters import read_authenticated_source_evidence
    request = lookup()
    response = source_response()
    authenticator = _FakeAuthenticator()
    result = read_authenticated_source_evidence(
        adapter=_FakeAdapter(response), authenticator=authenticator, lookup=request
    )
    assert result is response
    assert authenticator.calls == [("DHA-NPR-VERIFICATION", request, response)]


def test_authenticated_read_rejects_scope_mismatch_after_source_authentication():
    from tools.eos.security.institutional_signer_source_adapters import read_authenticated_source_evidence
    request = lookup()
    response = source_response(subject_principal_id="PRINCIPAL-OTHER")
    with pytest.raises(InstitutionalSignerSourceAdapterError) as error:
        read_authenticated_source_evidence(
            adapter=_FakeAdapter(response), authenticator=_FakeAuthenticator(), lookup=request
        )
    assert error.value.code == "INSTITUTIONAL_SIGNER_SOURCE_SUBJECT_PRINCIPAL_ID_MISMATCH"


def test_authenticated_read_preserves_negative_source_state_for_reconciliation():
    from tools.eos.security.institutional_signer_source_adapters import read_authenticated_source_evidence
    response = source_response(status="REVOKED", revoked=True)
    result = read_authenticated_source_evidence(
        adapter=_FakeAdapter(response), authenticator=_FakeAuthenticator(), lookup=lookup()
    )
    assert result.status == "REVOKED"
    assert result.revoked is True


def test_authenticated_read_rejects_adapter_kind_mismatch_before_provider_io():
    from tools.eos.security.institutional_signer_source_adapters import read_authenticated_source_evidence
    adapter = _FakeAdapter(source_response())
    adapter.supported_evidence_kind = "SIGNATORY_MANDATE"
    with pytest.raises(InstitutionalSignerSourceAdapterError) as error:
        read_authenticated_source_evidence(
            adapter=adapter, authenticator=_FakeAuthenticator(), lookup=lookup()
        )
    assert error.value.code == "INSTITUTIONAL_SIGNER_SOURCE_ADAPTER_EVIDENCE_KIND_MISMATCH"


def _signed_source_response(private_key=None, **overrides):
    private_key = private_key or Ed25519PrivateKey.generate()
    response = source_response(**overrides)
    signature = private_key.sign(_canonical_source_response_payload(response))
    response = replace(response, response_signature_base64=base64.b64encode(signature).decode("ascii"))
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return response, public_key


def test_ed25519_authenticator_accepts_signature_from_pinned_source_key():
    response, public_key = _signed_source_response()
    authenticator = Ed25519InstitutionalSignerSourceResponseAuthenticator({
        ("DHA-NPR-VERIFICATION", "dha-response-key-2026"): public_key
    })
    authenticator.authenticate_response(
        expected_source_system_id="DHA-NPR-VERIFICATION", lookup=lookup(), response=response
    )


def test_ed25519_authenticator_rejects_tampered_source_revision():
    response, public_key = _signed_source_response()
    authenticator = Ed25519InstitutionalSignerSourceResponseAuthenticator({
        ("DHA-NPR-VERIFICATION", "dha-response-key-2026"): public_key
    })
    tampered = replace(response, source_revision="revision-8")
    with pytest.raises(InstitutionalSignerSourceAdapterError) as error:
        authenticator.authenticate_response(
            expected_source_system_id="DHA-NPR-VERIFICATION", lookup=lookup(), response=tampered
        )
    assert error.value.code == "INSTITUTIONAL_SIGNER_SOURCE_RESPONSE_SIGNATURE_INVALID"


def test_ed25519_authenticator_rejects_key_reuse_for_another_source():
    response, public_key = _signed_source_response()
    authenticator = Ed25519InstitutionalSignerSourceResponseAuthenticator({
        ("UNRELATED-SOURCE", "dha-response-key-2026"): public_key
    })
    with pytest.raises(InstitutionalSignerSourceAdapterError) as error:
        authenticator.authenticate_response(
            expected_source_system_id="DHA-NPR-VERIFICATION", lookup=lookup(), response=response
        )
    assert error.value.code == "INSTITUTIONAL_SIGNER_SOURCE_SIGNING_KEY_UNTRUSTED"


def test_ed25519_authenticator_rejects_empty_trust_configuration():
    response, _ = _signed_source_response()
    authenticator = Ed25519InstitutionalSignerSourceResponseAuthenticator({})
    with pytest.raises(InstitutionalSignerSourceAdapterError) as error:
        authenticator.authenticate_response(
            expected_source_system_id="DHA-NPR-VERIFICATION", lookup=lookup(), response=response
        )
    assert error.value.code == "INSTITUTIONAL_SIGNER_SOURCE_SIGNING_KEY_UNTRUSTED"


def test_authenticated_adapter_set_keeps_three_governance_channels_separate():
    authenticator = _FakeAuthenticator()
    identity = _FakeAdapter(source_response())
    mandate = _FakeAdapter(source_response(evidence_kind="SIGNATORY_MANDATE"))
    approval = _FakeAdapter(source_response(evidence_kind="INDEPENDENT_APPROVAL"))
    mandate.supported_evidence_kind = "SIGNATORY_MANDATE"
    approval.supported_evidence_kind = "INDEPENDENT_APPROVAL"
    sources = AuthenticatedInstitutionalSignerSourceAdapterSet(
        identity_proofing=identity,
        signatory_mandate=mandate,
        independent_approval=approval,
        authenticator=authenticator,
    )
    assert sources.read_identity_proofing(lookup=lookup()).evidence_kind == "IDENTITY_PROOFING"
    assert sources.read_signatory_mandate(lookup=lookup(evidence_kind="SIGNATORY_MANDATE")).evidence_kind == "SIGNATORY_MANDATE"
    assert sources.read_independent_approval(lookup=lookup(evidence_kind="INDEPENDENT_APPROVAL")).evidence_kind == "INDEPENDENT_APPROVAL"
    assert len(authenticator.calls) == 3


def test_authenticated_adapter_set_rejects_reusing_one_adapter_for_all_authorities():
    adapter = _FakeAdapter(source_response())
    with pytest.raises(InstitutionalSignerSourceAdapterError) as error:
        AuthenticatedInstitutionalSignerSourceAdapterSet(
            identity_proofing=adapter,
            signatory_mandate=adapter,
            independent_approval=adapter,
            authenticator=_FakeAuthenticator(),
        )
    assert error.value.code == "INSTITUTIONAL_SIGNER_SOURCE_ADAPTERS_MUST_BE_DISTINCT"
