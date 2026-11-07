"""Non-exportable AWS KMS RSA subordinate-CA key and PKCS#10 CSR provisioning.

The private key is generated inside KMS and is never returned to this process.
The returned CSR is intended for offline approval/signing by the separately
protected institutional root CA. No trust is granted merely by creating a key.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256, sha384
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.x509.oid import NameOID

KEY_SPEC = "RSA_3072"
KEY_USAGE = "SIGN_VERIFY"
SIGNING_ALGORITHM = "RSASSA_PSS_SHA_384"
KEY_TAGS = (
    {"TagKey": "System", "TagValue": "WILSY-EOS"},
    {"TagKey": "Purpose", "TagValue": "Institutional-Subordinate-CA"},
    {"TagKey": "KeyCustody", "TagValue": "NonExportable-KMS"},
)


class InstitutionalPKIKMSError(RuntimeError):
    def __init__(self, code: str, *, key_arn: str | None = None) -> None:
        self.code = code
        self.key_arn = key_arn
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class InstitutionalKMSSubordinateCSR:
    key_arn: str
    region: str
    subject_common_name: str
    public_key_fingerprint_sha256: str
    csr_pem: bytes
    signing_algorithm: str
    created_at: datetime


def _der_length(length: int) -> bytes:
    if length < 0:
        raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_DER_LENGTH_INVALID")
    if length < 128:
        return bytes((length,))
    encoded = length.to_bytes((length.bit_length() + 7) // 8, "big")
    return bytes((0x80 | len(encoded),)) + encoded


def _tlv(tag: int, value: bytes) -> bytes:
    return bytes((tag,)) + _der_length(len(value)) + value


def _sequence(value: bytes) -> bytes:
    return _tlv(0x30, value)


def _integer(value: int) -> bytes:
    if value < 0:
        raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_DER_INTEGER_INVALID")
    encoded = value.to_bytes(max(1, (value.bit_length() + 7) // 8), "big")
    if encoded[0] & 0x80:
        encoded = b"\x00" + encoded
    return _tlv(0x02, encoded)


_OID_SHA384 = bytes.fromhex("0609608648016503040202")
_OID_MGF1 = bytes.fromhex("06092a864886f70d010108")
_OID_RSA_PSS = bytes.fromhex("06092a864886f70d01010a")
_NULL = bytes.fromhex("0500")


def _pss_sha384_algorithm_identifier() -> bytes:
    hash_algorithm = _sequence(_OID_SHA384 + _NULL)
    mask_generation = _sequence(_OID_MGF1 + hash_algorithm)
    parameters = _sequence(
        _tlv(0xA0, hash_algorithm)
        + _tlv(0xA1, mask_generation)
        + _tlv(0xA2, _integer(48))
        + _tlv(0xA3, _integer(1))
    )
    return _sequence(_OID_RSA_PSS + parameters)


def _validate_key_policy(policy: str) -> str:
    if not isinstance(policy, str) or not policy.strip():
        raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_EXPLICIT_KEY_POLICY_REQUIRED")
    try:
        document = json.loads(policy)
    except (TypeError, ValueError) as error:
        raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_KEY_POLICY_INVALID") from error
    if not isinstance(document, dict) or document.get("Version") != "2012-10-17":
        raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_KEY_POLICY_INVALID")
    statements = document.get("Statement")
    if not isinstance(statements, list) or not statements:
        raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_KEY_POLICY_INVALID")
    required_actions = {"kms:Sign", "kms:GetPublicKey", "kms:DescribeKey"}
    allowed_actions: set[str] = set()
    for statement in statements:
        if not isinstance(statement, dict):
            raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_KEY_POLICY_INVALID")
        principal = statement.get("Principal")
        aws_principals = principal.get("AWS") if isinstance(principal, dict) else None
        principals = [aws_principals] if isinstance(aws_principals, str) else aws_principals
        if statement.get("Effect") == "Allow":
            if not isinstance(principals, list) or not principals:
                raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_EXPLICIT_PRINCIPAL_REQUIRED")
            if any(
                not isinstance(value, str)
                or value == "*"
                or not re.fullmatch(r"arn:aws[a-zA-Z-]*:iam::[0-9]{12}:(?:root|role/[A-Za-z0-9+=,.@_/-]+|user/[A-Za-z0-9+=,.@_/-]+)", value)
                for value in principals
            ):
                raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_WILDCARD_OR_INVALID_PRINCIPAL")
            action = statement.get("Action")
            actions = [action] if isinstance(action, str) else action
            if not isinstance(actions, list):
                raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_KEY_POLICY_ACTION_INVALID")
            if "*" in actions or "kms:*" in actions:
                raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_WILDCARD_ACTION_FORBIDDEN")
            allowed_actions.update(value for value in actions if isinstance(value, str))
    if not required_actions.issubset(allowed_actions):
        raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_KEY_POLICY_REQUIRED_ACTIONS_MISSING")
    return json.dumps(document, sort_keys=True, separators=(",", ":"))


def create_nonexportable_subordinate_ca_key_and_csr(
    kms_client: Any,
    *,
    region: str,
    key_policy_json: str,
    common_name: str,
    organization: str,
    organizational_unit: str,
    country_code: str,
) -> InstitutionalKMSSubordinateCSR:
    """Create an RSA-3072 KMS key and a KMS-signed PSS/SHA-384 CSR."""
    if not isinstance(region, str) or not re.fullmatch(r"[a-z]{2}(?:-gov)?-[a-z]+-\d", region):
        raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_REGION_INVALID")
    for value, code, maximum in (
        (common_name, "INSTITUTIONAL_KMS_SUBJECT_CN_INVALID", 128),
        (organization, "INSTITUTIONAL_KMS_SUBJECT_ORG_INVALID", 128),
        (organizational_unit, "INSTITUTIONAL_KMS_SUBJECT_OU_INVALID", 64),
    ):
        if not isinstance(value, str) or not value or value != value.strip() or len(value) > maximum:
            raise InstitutionalPKIKMSError(code)
    if not isinstance(country_code, str) or re.fullmatch(r"[A-Z]{2}", country_code) is None:
        raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_COUNTRY_INVALID")
    policy = _validate_key_policy(key_policy_json)
    created_key_arn: str | None = None
    try:
        created = kms_client.create_key(
            Description="WILSY EOS non-exportable institutional subordinate CA signing key",
            KeySpec=KEY_SPEC,
            KeyUsage=KEY_USAGE,
            Origin="AWS_KMS",
            MultiRegion=False,
            Policy=policy,
            Tags=list(KEY_TAGS),
        )
        metadata = created.get("KeyMetadata") or {}
        key_arn = metadata.get("Arn")
        created_key_arn = key_arn if isinstance(key_arn, str) else None
        if (
            not isinstance(key_arn, str)
            or re.fullmatch(rf"arn:aws(?:-[a-z]+)?:kms:{re.escape(region)}:[0-9]{{12}}:key/[A-Za-z0-9-]+", key_arn) is None
            or metadata.get("KeySpec") != KEY_SPEC
            or metadata.get("KeyUsage") != KEY_USAGE
            or metadata.get("Origin") != "AWS_KMS"
            or metadata.get("KeyState") != "Enabled"
            or metadata.get("MultiRegion") is not False
        ):
            raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_CREATED_KEY_PROFILE_MISMATCH")
        public = kms_client.get_public_key(KeyId=key_arn)
        if (
            public.get("KeySpec") != KEY_SPEC
            or public.get("KeyUsage") != KEY_USAGE
            or SIGNING_ALGORITHM not in public.get("SigningAlgorithms", ())
        ):
            raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_PUBLIC_KEY_PROFILE_MISMATCH")
        public_key_der = public.get("PublicKey")
        if not isinstance(public_key_der, bytes) or not public_key_der:
            raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_PUBLIC_KEY_UNAVAILABLE")
        public_key = serialization.load_der_public_key(public_key_der)
        if not isinstance(public_key, rsa.RSAPublicKey) or public_key.key_size != 3072 or public_key.public_numbers().e != 65537:
            raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_PUBLIC_KEY_STRENGTH_INVALID")
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country_code),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, organizational_unit),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        certification_request_info = _sequence(
            _integer(0)
            + subject.public_bytes()
            + public_key_der
            + _tlv(0xA0, b"")
        )
        digest = sha384(certification_request_info).digest()
        signed = kms_client.sign(
            KeyId=key_arn,
            Message=digest,
            MessageType="DIGEST",
            SigningAlgorithm=SIGNING_ALGORITHM,
        )
        signature = signed.get("Signature")
        if not isinstance(signature, bytes) or not signature:
            raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_CSR_SIGNATURE_UNAVAILABLE")
        public_key.verify(
            signature, digest,
            padding.PSS(mgf=padding.MGF1(hashes.SHA384()), salt_length=48),
            Prehashed(hashes.SHA384()),
        )
        csr_der = _sequence(
            certification_request_info
            + _pss_sha384_algorithm_identifier()
            + _tlv(0x03, b"\x00" + signature)
        )
        csr = x509.load_der_x509_csr(csr_der)
        if not csr.is_signature_valid or csr.subject != subject:
            raise InstitutionalPKIKMSError("INSTITUTIONAL_KMS_CSR_SELF_VERIFICATION_FAILED")
        return InstitutionalKMSSubordinateCSR(
            key_arn=key_arn,
            region=region,
            subject_common_name=common_name,
            public_key_fingerprint_sha256=sha256(public_key_der).hexdigest(),
            csr_pem=csr.public_bytes(serialization.Encoding.PEM),
            signing_algorithm=SIGNING_ALGORITHM,
            created_at=datetime.now(timezone.utc),
        )
    except InstitutionalPKIKMSError as error:
        if created_key_arn and error.key_arn is None:
            raise InstitutionalPKIKMSError(error.code, key_arn=created_key_arn) from error
        raise
    except Exception as error:
        raise InstitutionalPKIKMSError(
            "INSTITUTIONAL_KMS_SUBORDINATE_KEY_PROVISIONING_FAILED",
            key_arn=created_key_arn,
        ) from error


__all__ = [
    "InstitutionalPKIKMSError",
    "InstitutionalKMSSubordinateCSR",
    "create_nonexportable_subordinate_ca_key_and_csr",
]
