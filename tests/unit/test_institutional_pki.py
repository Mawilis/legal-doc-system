from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID, ObjectIdentifier

from tools.eos.security.institutional_pki import (
    InstitutionalPKIError,
    InstitutionalPKISettings,
    InstitutionalPKIVerifier,
)
from tools.eos.api.institutional_pki_router import router as institutional_pki_router
from tools.eos.security.institutional_pki_provisioning import assemble_crl_bundle
from tools.eos.security.institutional_pki_provisioning import create_offline_root, issue_crl, issue_intermediate

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


def _fixture(tmp_path: Path, *, revoked_leaf=False, stale_crl=False, eku=SIGNING_EKU, critical_extension=False):
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
    if critical_extension:
        leaf_builder = leaf_builder.add_extension(
            x509.UnrecognizedExtension(ObjectIdentifier("1.2.3.4.5"), b"\\x05\\x00"),
            critical=True,
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
    return verifier, leaf, intermediate, leaf_key


def test_verifies_exact_chain_and_fresh_crls(tmp_path):
    verifier, leaf, intermediate, leaf_key = _fixture(tmp_path)
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
    verifier, leaf, intermediate, _ = _fixture(tmp_path, revoked_leaf=True)
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
    verifier, leaf, intermediate, _ = _fixture(tmp_path, eku=ExtendedKeyUsageOID.CLIENT_AUTH.dotted_string)
    with pytest.raises(InstitutionalPKIError, match="SIGNING_EKU_MISMATCH"):
        verifier.verify(
            leaf_pem=leaf.public_bytes(__import__("cryptography").hazmat.primitives.serialization.Encoding.PEM),
            intermediate_pems=[intermediate.public_bytes(__import__("cryptography").hazmat.primitives.serialization.Encoding.PEM)],
            verified_at=NOW,
        )


def test_rejects_untrusted_root_pin_set(tmp_path):
    verifier, _, _, _ = _fixture(tmp_path)
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
    verifier, _, _, _ = _fixture(tmp_path)
    issuer_reference = sha256(verifier._anchors[0].subject.public_bytes()).hexdigest()
    app = FastAPI()
    app.include_router(institutional_pki_router, prefix="/api")
    app.state.institutional_pki_verifier = verifier
    app.state.institutional_pki_ready = True
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



def test_verifies_detached_institutional_document_signature(tmp_path):
    verifier, leaf, intermediate, leaf_key = _fixture(tmp_path)
    payload = b"canonical WILSY signed-offer verification payload"
    signature = leaf_key.sign(
        payload,
        padding.PSS(mgf=padding.MGF1(hashes.SHA384()), salt_length=hashes.SHA384().digest_size),
        hashes.SHA384(),
    )
    result = verifier.verify_signed_payload(
        leaf_pem=leaf.public_bytes(serialization.Encoding.PEM),
        intermediate_pems=[intermediate.public_bytes(serialization.Encoding.PEM)],
        signed_payload=payload,
        signature=signature,
        verified_at=NOW,
    )
    assert result.signature_algorithm == "RSA-PSS-SHA384"
    assert result.payload_digest_sha3_512
    assert result.certificate_verification.chain_depth == 2


def test_rejects_tampered_institutional_document_signature(tmp_path):
    verifier, leaf, intermediate, leaf_key = _fixture(tmp_path)
    payload = b"canonical WILSY signed-offer verification payload"
    signature = leaf_key.sign(
        payload,
        padding.PSS(mgf=padding.MGF1(hashes.SHA384()), salt_length=hashes.SHA384().digest_size),
        hashes.SHA384(),
    )
    with pytest.raises(InstitutionalPKIError, match="DOCUMENT_SIGNATURE_INVALID"):
        verifier.verify_signed_payload(
            leaf_pem=leaf.public_bytes(serialization.Encoding.PEM),
            intermediate_pems=[intermediate.public_bytes(serialization.Encoding.PEM)],
            signed_payload=payload + b"tampered",
            signature=signature,
            verified_at=NOW,
        )



def test_crl_refresh_requires_and_invokes_durable_currentness_binding(tmp_path):
    verifier, _, _, _ = _fixture(tmp_path)
    observations = []
    verified_bundles = []
    verifier.bind_crl_currentness_recorder(lambda value: observations.append(dict(value)))
    verifier.bind_crl_revocation_recorder(lambda value: verified_bundles.append(tuple(value)))
    verifier.refresh_crls()
    assert len(observations) == 1
    assert len(observations[0]) == 2
    assert all(number == 1 for number, _ in observations[0].values())
    assert len(verified_bundles) == 1
    assert len(verified_bundles[0]) == 2
    assert all(crl.get_revoked_certificate_by_serial_number(0xABCDEF) is None for crl in verified_bundles[0])



def test_assembles_complete_multi_issuer_crl_bundle_atomically(tmp_path):
    verifier, _, _, _ = _fixture(tmp_path)
    crl_paths = []
    for index, crl in enumerate(verifier.refresh_crls()):
        path = tmp_path / f"issuer-{index}.crl.pem"
        path.write_bytes(crl.public_bytes(serialization.Encoding.PEM))
        crl_paths.append(path)
    output = tmp_path / "deployment" / "crl-bundle.pem"
    bundle_path, fingerprint = assemble_crl_bundle(
        crl_paths=crl_paths,
        output_path=output,
    )
    assert bundle_path == output
    assert len(fingerprint) == 64
    assert bundle_path.read_bytes().count(b"-----BEGIN X509 CRL-----") == 2


def test_crl_bundle_assembly_rejects_duplicate_issuer(tmp_path):
    verifier, _, _, _ = _fixture(tmp_path)
    path = tmp_path / "root.crl.pem"
    path.write_bytes(verifier._crls[0].public_bytes(serialization.Encoding.PEM))
    with pytest.raises(InstitutionalPKIError, match="BUNDLE_DUPLICATE_ISSUER"):
        assemble_crl_bundle(crl_paths=[path, path], output_path=tmp_path / "bundle.pem")



def test_offline_ca_ceremony_creates_encrypted_root_intermediate_and_signed_crl(tmp_path):
    passphrase = b"unit-test-offline-ca-passphrase-2026"
    crl_base = "https://pki.example.test/api/security/pki/crl"
    root_key_path, root_cert_path, root_fingerprint = create_offline_root(
        output_directory=tmp_path / "offline-root",
        common_name="WILSY EOS Test Root CA",
        organization="WILSY EOS",
        passphrase=passphrase,
        crl_distribution_base_url=crl_base,
        validity_days=365,
    )
    assert len(root_fingerprint) == 64
    assert root_key_path.stat().st_mode & 0o777 == 0o600
    assert root_key_path.parent.stat().st_mode & 0o777 == 0o700
    root = x509.load_pem_x509_certificate(root_cert_path.read_bytes())
    root_key = serialization.load_pem_private_key(root_key_path.read_bytes(), password=passphrase)
    root_dp = root.extensions.get_extension_for_class(x509.CRLDistributionPoints).value
    assert root_dp[0].full_name[0].value.startswith(crl_base + "/")

    intermediate_key_path, intermediate_cert_path, intermediate_fingerprint = issue_intermediate(
        root_certificate_pem=root_cert_path,
        root_private_key_pem=root_key_path,
        root_passphrase=passphrase,
        output_directory=tmp_path / "intermediate",
        common_name="WILSY EOS Test Signing CA",
        organization="WILSY EOS",
        crl_distribution_base_url=crl_base,
        validity_days=365,
    )
    assert len(intermediate_fingerprint) == 64
    intermediate = x509.load_pem_x509_certificate(intermediate_cert_path.read_bytes())
    intermediate_key = serialization.load_pem_private_key(
        intermediate_key_path.read_bytes(), password=passphrase,
    )
    assert intermediate.issuer == root.subject
    assert intermediate.extensions.get_extension_for_class(x509.BasicConstraints).value.path_length == 0
    assert intermediate.extensions.get_extension_for_class(x509.CRLDistributionPoints).value[0].full_name[0].value.startswith(
        crl_base + "/" + sha256(root.subject.public_bytes()).hexdigest()
    )

    crl_path, crl_fingerprint = issue_crl(
        issuer_certificate_pem=intermediate_cert_path,
        issuer_private_key_pem=intermediate_key_path,
        issuer_passphrase=passphrase,
        output_path=tmp_path / "crls" / "intermediate.crl.pem",
        crl_number=1,
    )
    assert len(crl_fingerprint) == 64
    crl = x509.load_pem_x509_crl(crl_path.read_bytes())
    assert crl.issuer == intermediate.subject
    assert crl.extensions.get_extension_for_class(x509.CRLNumber).value.crl_number == 1



def test_rejects_unhandled_critical_certificate_extension(tmp_path):
    verifier, leaf, intermediate, _ = _fixture(tmp_path, critical_extension=True)
    with pytest.raises(InstitutionalPKIError, match="UNHANDLED_CRITICAL_CERTIFICATE_EXTENSION"):
        verifier.verify(
            leaf_pem=leaf.public_bytes(serialization.Encoding.PEM),
            intermediate_pems=[intermediate.public_bytes(serialization.Encoding.PEM)],
            verified_at=NOW,
        )
