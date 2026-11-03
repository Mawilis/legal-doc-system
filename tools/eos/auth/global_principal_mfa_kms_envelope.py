"""Platform KMS envelope encryption for global-principal MFA factors.

AWS KMS is an opt-in deployment adapter, not a default provider. It uses the
ambient AWS workload identity (never static credentials), binds ciphertext to
the principal and credential revision with KMS encryption context, and fails
closed when deployment configuration or KMS access is unavailable.
"""
from __future__ import annotations

import base64
import binascii
import os
import re
from typing import Any, Mapping

from botocore.exceptions import BotoCoreError, ClientError

VERSION = "v1.0.0-GLOBAL-MFA-KMS-ENVELOPE"
ENVELOPE_SCHEMA = "WILSY_GLOBAL_MFA_KMS_V1"
PROVIDER_AWS_KMS = "AWS_KMS"
PURPOSE = "GLOBAL_PRINCIPAL_TOTP"


class GlobalMfaKeyManagementError(RuntimeError):
    """KMS configuration, cryptographic operation, or envelope failure."""


def _identity_context(principal_id: str, credential_revision: int) -> dict[str, str]:
    if (
        not isinstance(principal_id, str)
        or not principal_id
        or principal_id != principal_id.strip()
        or isinstance(credential_revision, bool)
        or not isinstance(credential_revision, int)
        or credential_revision < 0
    ):
        raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_CONTEXT_INVALID")
    return {
        "purpose": PURPOSE,
        "principal_id": principal_id,
        "credential_revision": str(credential_revision),
    }


class AwsKmsGlobalMfaEnvelope:
    """Encrypt/decrypt small MFA secrets directly with AWS KMS.

    The adapter deliberately has no local-key or environment-secret fallback.
    Configure WILSY_GLOBAL_MFA_KMS_PROVIDER=AWS_KMS,
    WILSY_GLOBAL_MFA_KMS_KEY_ID, and optionally AWS_REGION. AWS credentials
    must come from the workload's standard IAM role/credential chain.
    """

    def __init__(self, *, key_id: str, region_name: str | None = None, client: Any = None) -> None:
        if not isinstance(key_id, str) or not key_id.strip():
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_KEY_ID_REQUIRED")
        self.key_id = key_id.strip()
        key_match = re.fullmatch(
            r"arn:[a-z0-9-]+:kms:([a-z0-9-]+):\\d{12}:key/[A-Za-z0-9-]+",
            self.key_id,
        )
        if key_match is None:
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_KEY_ARN_REQUIRED")
        self.region_name = (region_name or os.getenv("AWS_REGION") or "").strip()
        if not self.region_name:
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_REGION_REQUIRED")
        if self.region_name != key_match.group(1):
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_REGION_KEY_MISMATCH")
        if client is None:
            try:
                import boto3
                client = boto3.client("kms", region_name=self.region_name)
            except Exception as error:
                raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_CLIENT_UNAVAILABLE") from error
        self._client = client

    @classmethod
    def from_environment(cls, *, client: Any = None) -> "AwsKmsGlobalMfaEnvelope | None":
        provider = os.getenv("WILSY_GLOBAL_MFA_KMS_PROVIDER", "").strip().upper()
        if not provider:
            return None
        if provider != PROVIDER_AWS_KMS:
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_PROVIDER_UNSUPPORTED")
        key_id = os.getenv("WILSY_GLOBAL_MFA_KMS_KEY_ID", "").strip()
        if not key_id:
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_KEY_ID_REQUIRED")
        return cls(key_id=key_id, region_name=os.getenv("AWS_REGION"), client=client)

    def encrypt_secret(
        self, *, secret: str, principal_id: str, credential_revision: int
    ) -> dict[str, str]:
        if not isinstance(secret, str) or not secret:
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_SECRET_INVALID")
        context = _identity_context(principal_id, credential_revision)
        try:
            result = self._client.encrypt(
                KeyId=self.key_id,
                Plaintext=secret.encode("utf-8"),
                EncryptionContext=context,
            )
            ciphertext = result.get("CiphertextBlob")
            key_id = result.get("KeyId")
            if not isinstance(ciphertext, (bytes, bytearray)) or not ciphertext:
                raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_ENCRYPTION_EMPTY")
            if key_id != self.key_id:
                raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_KEY_ID_MISMATCH")
            return {
                "schema": ENVELOPE_SCHEMA,
                "provider": PROVIDER_AWS_KMS,
                "key_id": self.key_id,
                "ciphertext": base64.b64encode(bytes(ciphertext)).decode("ascii"),
            }
        except GlobalMfaKeyManagementError:
            raise
        except (BotoCoreError, ClientError, Exception) as error:
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_ENCRYPT_FAILED") from error

    def decrypt_secret(
        self, envelope: Mapping[str, Any], *, principal_id: str, credential_revision: int
    ) -> str:
        context = _identity_context(principal_id, credential_revision)
        if (
            not isinstance(envelope, Mapping)
            or envelope.get("schema") != ENVELOPE_SCHEMA
            or envelope.get("provider") != PROVIDER_AWS_KMS
            or envelope.get("key_id") != self.key_id
            or not isinstance(envelope.get("ciphertext"), str)
        ):
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_ENVELOPE_INVALID")
        try:
            ciphertext = base64.b64decode(envelope["ciphertext"], validate=True)
            if not ciphertext:
                raise ValueError("empty ciphertext")
            result = self._client.decrypt(
                CiphertextBlob=ciphertext,
                KeyId=self.key_id,
                EncryptionContext=context,
            )
            plaintext = result.get("Plaintext")
            key_id = result.get("KeyId")
            if key_id != self.key_id:
                raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_KEY_ID_MISMATCH")
            if not isinstance(plaintext, (bytes, bytearray)) or not plaintext:
                raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_DECRYPTION_EMPTY")
            return bytes(plaintext).decode("utf-8")
        except GlobalMfaKeyManagementError:
            raise
        except (BotoCoreError, ClientError, binascii.Error, UnicodeDecodeError, ValueError, Exception) as error:
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_DECRYPT_FAILED") from error


def build_global_mfa_kms_envelope_from_environment(*, client: Any = None) -> AwsKmsGlobalMfaEnvelope | None:
    """Return the explicitly configured KMS adapter, or None when unconfigured."""
    return AwsKmsGlobalMfaEnvelope.from_environment(client=client)


__all__ = [
    "VERSION",
    "ENVELOPE_SCHEMA",
    "PROVIDER_AWS_KMS",
    "GlobalMfaKeyManagementError",
    "AwsKmsGlobalMfaEnvelope",
    "build_global_mfa_kms_envelope_from_environment",
]
