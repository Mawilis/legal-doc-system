from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID, ObjectIdentifier

from tools.eos.security.institutional_pki import (
    InstitutionalPKIError,
    InstitutionalPKISettings,
    InstitutionalPKIVerifier,
)
from tools.eos.api.institutional_pki_router import router as institutional_pki_router

NOW = datetime.now(timezone.utc)
SIGNING_EKU = "1.3.6.1.4.1.55555.1.1"


def _name(value: str) -> x509.Name:
    return x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "WILSY EOS TEST PKI"),
        x509.NameAttribute(NameOID.COMMON_NAME, value),
    ])


def _ca_certificate(subject, issuer, public_key, signer, serial, path_length, not_after):
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(serial)
        .not_valid_before(NOW - timedelta(days=2))
        .not_valid_after(not_after)
        .add_extension(x509.BasicConstraints(ca=True, path_length=path_length), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=False, content_commitment=False, key_encipherment=False,
            data_encipherment=False, key_agreement=False, key_cert_sign=True,
            crl_sign=True, encipher_only=False, decipher_only=False,
        ), critical=True)
    )
    return builder.sign(signer, hashes.SHA256())


def _crl(issuer, signer, revoked_serials=(), *, last_update=NOW - timedelta(minutes=1), next_update=NOW + timedelta(hours=12)):
    builder = (
        x509.CertificateRevocationListBuilder()
        .issuer_name(issuer)
        .last_update(last_update)
        .next_update(next_update)
        .add_extension(x509.CRLNumber(1), critical=False)
    )
    for serial in revoked_serials:
        builder = builder.add_revoked_certificate(
            x509.RevokedCertificateBuilder()
            .serial_number(serial)
            .revocation_date(NOW - timedelta(minutes=5))
            .build()
        )
    return builder.sign(signer, hashes.SHA256())


def _fixture(tmp_path: Path, *, revoked_leaf=False, stale_crl=False, eku=SIGNING_EKU):
    root_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    intermediate_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    leaf_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    root = _ca_certificate(
        _name("WILSY EOS Test Root"), _name("WILSY EOS Test Root"),
        root_key.public_key(), root_key, 100, 1, NOW + timedelta(days=3650),
    )
    intermediate = _ca_certificate(
        _name("WILSY EOS Test Intermediate"), root.subject,
        intermediate_key.public_key(), root_key, 200, 0, NOW + timedelta(days=1000),
    )
    leaf_builder = (
        x509.CertificateBuilder()
        .subject_name(_name("WILSY EOS Test Signer"))
        .issuer_name(intermediate.subject)
        .public_key(leaf_key.public_key())
        .serial_number(300)
        .not_valid_before(NOW - timedelta(days=1))
        .not_valid_after(NOW + timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True, content_commitment=True, key_encipherment=False,
            data_encipherment=False, key_agreement=False, key_cert_sign=False,
            crl_sign=False, encipher_only=False, decipher_only=False,
        ), critical=True)
        .add_extension(x509.ExtendedKeyUsage([ObjectIdentifier(eku)]), critical=False)
    )
    leaf = leaf_builder.sign(intermediate_key, hashes.SHA256())
    crl_last = NOW - timedelta(days=2) if stale_crl else NOW - timedelta(minutes=1)
    crl_next = NOW - timedelta(days=1) if stale_crl else NOW + timedelta(hours=12)
    root_crl = _crl(root.subject, root_key, (), last_update=crl_last, next_update=crl_next)
    intermediate_crl = _crl(
        intermediate.subject, intermediate_key,
        [leaf.serial_number] if revoked_leaf else (),
        last_update=crl_last, next_update=crl_next,
    )
    anchor_path = tmp_path / "anchors.pem"
    issuer_path = tmp_path / "issuers.pem"
    crl_path = tmp_path / "crls.pem"
    anchor_path.write_bytes(root.public_bytes(serialization.Encoding.PEM))
    issuer_path.write_bytes(intermediate.public_bytes(serialization.Encoding.PEM))
    crl_path.write_bytes(
        root_crl.public_bytes(serialization.Encoding.PEM)
        + intermediate_crl.public_bytes(serialization.Encoding.PEM)
    )
    settings = InstitutionalPKISettings(
        trust_anchors_pem=anchor_path,
        issuer_certificates_pem=issuer_path,
        crl_bundle_pem=crl_path,
        trusted_root_sha256=frozenset({root.fingerprint(hashes.SHA256()).hex()}),
        required_eku_oid=SIGNING_EKU,
    )
    verifier = InstitutionalPKIVerifier(
        anchors=[root], crls=[root_crl, intermediate_crl], settings=settings,
        issuer_certificates=[intermediate],
    )
    return verifier, leaf, intermediate


def test_verifies_exact_chain_and_fresh_crls(tmp_path):
    verifier, leaf, intermediate = _fixture(tmp_path)
    result = verifier.verify(
        leaf_pem=leaf.public_bytes(serialization.Encoding.PEM),
        intermediate_pems=[intermediate.public_bytes(serialization.Encoding.PEM)],
        verified_at=NOW,
    )
    assert result.chain_depth == 2
    assert result.serial_number_hex == "12c"
    assert len(result.revocation_sources) == 2
    assert len(result.verification_fingerprint) == 64


def test_rejects_revoked_signer_certificate(tmp_path):
    verifier, leaf, intermediate = _fixture(tmp_path, revoked_leaf=True)
    with pytest.raises(InstitutionalPKIError, match="CERTIFICATE_REVOKED"):
        verifier.verify(
            leaf_pem=leaf.public_bytes(__import__("cryptography").hazmat.primitives.serialization.Encoding.PEM),
            intermediate_pems=[intermediate.public_bytes(__import__("cryptography").hazmat.primitives.serialization.Encoding.PEM)],
            verified_at=NOW,
        )


def test_rejects_stale_crl_even_when_signature_is_valid(tmp_path):
    with pytest.raises(InstitutionalPKIError, match="CRL_NOT_CURRENT"):
        _fixture(tmp_path, stale_crl=True)


def test_rejects_wrong_signing_eku(tmp_path):
    verifier, leaf, intermediate = _fixture(tmp_path, eku=ExtendedKeyUsageOID.CLIENT_AUTH.dotted_string)
    with pytest.raises(InstitutionalPKIError, match="SIGNING_EKU_MISMATCH"):
        verifier.verify(
            leaf_pem=leaf.public_bytes(__import__("cryptography").hazmat.primitives.serialization.Encoding.PEM),
            intermediate_pems=[intermediate.public_bytes(__import__("cryptography").hazmat.primitives.serialization.Encoding.PEM)],
            verified_at=NOW,
        )


def test_rejects_untrusted_root_pin_set(tmp_path):
    verifier, _, _ = _fixture(tmp_path)
    wrong = InstitutionalPKISettings(
        trust_anchors_pem=tmp_path / "anchors.pem",
        issuer_certificates_pem=tmp_path / "issuers.pem",
        crl_bundle_pem=tmp_path / "crls.pem",
        trusted_root_sha256=frozenset({"0" * 64}),
        required_eku_oid=SIGNING_EKU,
    )
    with pytest.raises(InstitutionalPKIError, match="ROOT_PIN_SET_MISMATCH"):
        InstitutionalPKIVerifier(
            anchors=verifier._anchors, crls=verifier._crls, settings=wrong,
        )


def test_environment_composition_fails_closed_without_explicit_trust_material(monkeypatch):
    for key in (
        "WILSY_EOS_PKI_TRUST_ANCHORS_PEM",
        "WILSY_EOS_PKI_ISSUER_CERTIFICATES_PEM",
        "WILSY_EOS_PKI_CRL_BUNDLE_PEM",
        "WILSY_EOS_PKI_TRUSTED_ROOT_SHA256",
        "WILSY_EOS_PKI_REQUIRED_SIGNING_EKU_OID",
    ):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(InstitutionalPKIError, match="RUNTIME_CONFIGURATION_INCOMPLETE"):
        InstitutionalPKIVerifier.from_environment()



def test_public_crl_distribution_route_serves_only_the_loaded_issuer_crl(tmp_path):
    verifier, _, _ = _fixture(tmp_path)
    issuer_reference = sha256(verifier._anchors[0].subject.public_bytes()).hexdigest()
    app = FastAPI()
    app.include_router(institutional_pki_router, prefix="/api")
    app.state.institutional_pki_verifier = verifier
    with TestClient(app) as client:
        response = client.get(f"/api/security/pki/crl/{issuer_reference}")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pkix-crl")
    assert response.headers["cache-control"] == "public, max-age=300, must-revalidate"
    parsed_crl = x509.load_der_x509_crl(response.content)
    assert parsed_crl.issuer == verifier._anchors[0].subject


def test_public_crl_distribution_route_fails_closed_without_runtime():
    app = FastAPI()
    app.include_router(institutional_pki_router, prefix="/api")
    with TestClient(app) as client:
        response = client.get("/api/security/pki/crl/" + "0" * 64)
    assert response.status_code == 503
