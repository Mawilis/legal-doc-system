import json

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from tools.eos.security.institutional_pki_provisioning import (
    create_offline_root, issue_intermediate_from_kms_csr,
)
from tools.eos.security.institutional_pki_kms import (
    InstitutionalPKIKMSError,
    create_nonexportable_subordinate_ca_key_and_csr,
)


class FakeKMS:
    def __init__(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
        self.create_calls = []
        self.sign_calls = []

    def create_key(self, **kwargs):
        self.create_calls.append(kwargs)
        return {"KeyMetadata": {
            "Arn": "arn:aws:kms:af-south-1:123456789012:key/00000000-1111-2222-3333-444444444444",
            "KeySpec": "RSA_3072", "KeyUsage": "SIGN_VERIFY",
            "Origin": "AWS_KMS", "KeyState": "Enabled", "MultiRegion": False,
        }}

    def get_public_key(self, **kwargs):
        return {
            "KeySpec": "RSA_3072", "KeyUsage": "SIGN_VERIFY",
            "SigningAlgorithms": ["RSASSA_PSS_SHA_384"],
            "PublicKey": self.private_key.public_key().public_bytes(
                serialization.Encoding.DER,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            ),
        }

    def sign(self, **kwargs):
        self.sign_calls.append(kwargs)
        digest = kwargs["Message"]
        signature = self.private_key.sign(
            digest,
            padding.PSS(mgf=padding.MGF1(hashes.SHA384()), salt_length=48),
            __import__("cryptography").hazmat.primitives.asymmetric.utils.Prehashed(hashes.SHA384()),
        )
        return {"Signature": signature}


def policy():
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "ExplicitSubordinateCASigner",
            "Effect": "Allow",
            "Principal": {"AWS": "arn:aws:iam::123456789012:role/WilsyPkiOperator"},
            "Action": ["kms:Sign", "kms:GetPublicKey", "kms:DescribeKey"],
            "Resource": "*",
        }],
    })


def test_kms_subordinate_key_is_nonexportable_and_csr_is_kms_signed_and_verified():
    kms = FakeKMS()
    result = create_nonexportable_subordinate_ca_key_and_csr(
        kms, region="af-south-1", key_policy_json=policy(),
        common_name="WILSY EOS Intermediate CA",
        organization="Wilsy (Pty) Ltd",
        organizational_unit="Institutional PKI",
        country_code="ZA",
    )
    csr = x509.load_pem_x509_csr(result.csr_pem)
    assert csr.is_signature_valid
    assert csr.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value == result.subject_common_name
    assert result.key_arn.endswith("444444444444")
    assert result.signing_algorithm == "RSASSA_PSS_SHA_384"
    assert len(result.public_key_fingerprint_sha256) == 64
    assert kms.create_calls[0]["Origin"] == "AWS_KMS"
    assert kms.create_calls[0]["KeySpec"] == "RSA_3072"
    assert kms.create_calls[0]["KeyUsage"] == "SIGN_VERIFY"
    assert kms.sign_calls[0]["MessageType"] == "DIGEST"
    assert kms.sign_calls[0]["SigningAlgorithm"] == "RSASSA_PSS_SHA_384"
    assert b"PRIVATE KEY" not in result.csr_pem


def test_kms_subordinate_key_rejects_wildcard_principal_before_key_creation():
    kms = FakeKMS()
    unsafe = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow", "Principal": "*",
            "Action": ["kms:Sign", "kms:GetPublicKey", "kms:DescribeKey"],
            "Resource": "*",
        }],
    })
    try:
        create_nonexportable_subordinate_ca_key_and_csr(
            kms, region="af-south-1", key_policy_json=unsafe,
            common_name="WILSY EOS Intermediate CA",
            organization="Wilsy (Pty) Ltd",
            organizational_unit="Institutional PKI",
            country_code="ZA",
        )
    except InstitutionalPKIKMSError as error:
        assert error.code == "INSTITUTIONAL_KMS_EXPLICIT_PRINCIPAL_REQUIRED"
    else:
        raise AssertionError("Wildcard KMS principal must be rejected")
    assert not kms.create_calls



def test_offline_root_can_issue_kms_csr_without_exporting_subordinate_private_key(tmp_path):
    kms = FakeKMS()
    result = create_nonexportable_subordinate_ca_key_and_csr(
        kms, region="af-south-1", key_policy_json=policy(),
        common_name="WILSY EOS Intermediate CA",
        organization="Wilsy (Pty) Ltd",
        organizational_unit="Institutional PKI",
        country_code="ZA",
    )
    passphrase = b"test-offline-root-passphrase-2026"
    root_key, root_cert, _ = create_offline_root(
        output_directory=tmp_path / "offline-root",
        common_name="WILSY EOS Test Root CA",
        organization="Wilsy (Pty) Ltd",
        passphrase=passphrase,
        crl_distribution_base_url="https://pki.example.test/api/security/pki/crl",
        validity_days=365,
    )
    certificate_path, fingerprint = issue_intermediate_from_kms_csr(
        root_certificate_pem=root_cert,
        root_private_key_pem=root_key,
        root_passphrase=passphrase,
        csr_pem=result.csr_pem,
        output_directory=tmp_path / "issued-intermediate",
        expected_common_name="WILSY EOS Intermediate CA",
        organization="Wilsy (Pty) Ltd",
        crl_distribution_base_url="https://pki.example.test/api/security/pki/crl",
        validity_days=180,
    )
    csr = x509.load_pem_x509_csr(result.csr_pem)
    certificate = x509.load_pem_x509_certificate(certificate_path.read_bytes())
    assert certificate.public_key().public_numbers() == csr.public_key().public_numbers()
    assert certificate.extensions.get_extension_for_class(x509.BasicConstraints).value.path_length == 0
    assert len(fingerprint) == 64
    assert list((tmp_path / "issued-intermediate").glob("*-key.pem")) == []
