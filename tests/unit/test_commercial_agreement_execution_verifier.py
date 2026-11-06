from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

from tools.eos.saas.entitlement.commercial_agreement import (
    CommercialAgreement,
    CommercialRenewalMode,
)
from tools.eos.saas.entitlement.commercial_bundle_activation import (
    VerifiedCommercialAgreementExecutionEvidence,
)
from tools.eos.saas.entitlement.commercial_offer_catalogue import (
    CommercialOfferId,
    get_commercial_offer,
)
from tools.eos.saas.entitlement.commercial_agreement_execution_verifier import (
    CommercialAgreementExecutionVerificationError,
    CommercialAgreementExecutionVerifier,
    StoredCommercialExecutionEvidence,
    TrustedExecutionTimestamp,
    TrustedSigningCertificate,
    VerifiedSignatoryMandate,
    canonical_execution_document,
)

NOW = datetime.now(timezone.utc).replace(microsecond=0)
TENANT = "tenant-execution-verifier"
PRINCIPAL = "principal-execution-verifier"


def _agreement() -> CommercialAgreement:
    offer = get_commercial_offer(CommercialOfferId.ENTERPRISE_OPERATIONS)
    return CommercialAgreement(
        tenant_id=TENANT,
        agreement_id="agreement-execution-verifier",
        offer_id=offer.offer_id,
        offer_fingerprint=offer.fingerprint,
        contract_reference="contract-execution-verifier",
        contract_version="2026-11-06",
        counterparty_legal_name="Verifier Test Counterparty (Pty) Ltd",
        effective_at=NOW - timedelta(days=1),
        expires_at=NOW + timedelta(days=365),
        renewal_mode=CommercialRenewalMode.MANUAL,
        notice_days=30,
        termination_terms_reference="terms-execution-verifier",
    )


class _EvidenceStore:
    def __init__(self, evidence):
        self.evidence = evidence

    def load(self, tenant_id, agreement_id, evidence_reference):
        assert (tenant_id, agreement_id, evidence_reference) == (
            self.evidence.tenant_id,
            self.evidence.agreement_id,
            self.evidence.evidence_reference,
        )
        return self.evidence


class _TrustResolver:
    def __init__(self, certificate_pem, certificate_fingerprint, *, chain_valid=True, revocation="GOOD"):
        self.result = TrustedSigningCertificate(
            certificate_pem=certificate_pem,
            certificate_fingerprint=certificate_fingerprint,
            trust_anchor_reference="trust-anchor:commercial-signing",
            trust_anchor_fingerprint="a" * 128,
            chain_valid=chain_valid,
            revocation_status=revocation,
        )

    def resolve(self, **_kwargs):
        return self.result


class _MandateResolver:
    def __init__(self, *, active=True):
        self.active = active

    def resolve(self, **kwargs):
        return VerifiedSignatoryMandate(
            tenant_id=kwargs["tenant_id"],
            agreement_id=kwargs["agreement_id"],
            principal_id=kwargs["principal_id"],
            authority_reference="board-mandate:commercial-signing",
            authority_fingerprint="b" * 128,
            active=self.active,
        )


class _TimestampVerifier:
    def verify(self, **_kwargs):
        return TrustedExecutionTimestamp(
            signed_at=NOW,
            evidence_reference="trusted-timestamp:commercial-signing",
            evidence_fingerprint="c" * 128,
        )


def _harness(*, chain_valid=True, revocation="GOOD", mandate_active=True, tamper=False):
    agreement = _agreement()
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, PRINCIPAL),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "WILSY OS Test Trust"),
    ])
    certificate = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(NOW - timedelta(days=2))
        .not_valid_after(NOW + timedelta(days=365))
        .add_extension(
            x509.KeyUsage(
                digital_signature=True, content_commitment=True,
                key_encipherment=False, data_encipherment=False,
                key_agreement=False, key_cert_sign=False, crl_sign=False,
                encipher_only=None, decipher_only=None,
            ),
            critical=True,
        )
        .sign(private_key, hashes.SHA256())
    )
    certificate_pem = certificate.public_bytes(serialization.Encoding.PEM)
    certificate_fp = certificate.fingerprint(hashes.SHA256()).hex()
    document = canonical_execution_document(agreement)
    signature = private_key.sign(document, padding.PKCS1v15(), hashes.SHA256())
    if tamper:
        document += b" "
    evidence = StoredCommercialExecutionEvidence(
        tenant_id=TENANT,
        agreement_id=agreement.agreement_id,
        evidence_reference="evidence:commercial-signature:001",
        contract_reference=agreement.contract_reference,
        contract_version=agreement.contract_version,
        offer_fingerprint=agreement.offer_fingerprint,
        signed_document=document,
        signature=signature,
        signature_algorithm="RSA-PKCS1v15-SHA256",
        signing_certificate_fingerprint=certificate_fp,
        signatory_principal_id=PRINCIPAL,
        timestamp_token=b"trusted-timestamp-token",
    )
    verifier = CommercialAgreementExecutionVerifier(
        evidence_store=_EvidenceStore(evidence),
        certificate_trust=_TrustResolver(
            certificate_pem, certificate_fp,
            chain_valid=chain_valid, revocation=revocation,
        ),
        mandate_resolver=_MandateResolver(active=mandate_active),
        timestamp_verifier=_TimestampVerifier(),
        verifier_id="wilsy-commercial-execution-verifier-v1",
    )
    return agreement, verifier


def test_verifier_cryptographically_verifies_exact_document_and_authority():
    agreement, verifier = _harness()
    result = verifier.verify(
        agreement=agreement,
        evidence_reference="evidence:commercial-signature:001",
    )
    assert type(result) is VerifiedCommercialAgreementExecutionEvidence
    assert result.tenant_id == TENANT
    assert result.agreement_id == agreement.agreement_id
    assert result.signatory_principal_id == PRINCIPAL
    assert result.signatory_authority_reference == "board-mandate:commercial-signing"
    assert result.verifier_id == "wilsy-commercial-execution-verifier-v1"
    assert result.verified_at >= result.signed_at
    assert len(result.execution_evidence_fingerprint) == 128
    assert len(result.verification_receipt_fingerprint) == 128


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"chain_valid": False}, "COMMERCIAL_EXECUTION_CERTIFICATE_UNTRUSTED"),
        ({"revocation": "REVOKED"}, "COMMERCIAL_EXECUTION_CERTIFICATE_UNTRUSTED"),
        ({"mandate_active": False}, "COMMERCIAL_EXECUTION_SIGNATORY_NOT_AUTHORIZED"),
        ({"tamper": True}, "COMMERCIAL_EXECUTION_DOCUMENT_BINDING_INVALID"),
    ],
)
def test_verifier_fails_closed_for_untrusted_or_divergent_evidence(kwargs, expected):
    agreement, verifier = _harness(**kwargs)
    with pytest.raises(CommercialAgreementExecutionVerificationError) as error:
        verifier.verify(
            agreement=agreement,
            evidence_reference="evidence:commercial-signature:001",
        )
    assert error.value.code == expected
