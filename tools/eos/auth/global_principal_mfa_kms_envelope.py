"""Platform KMS envelope encryption for global-principal MFA factors.

AWS KMS is an opt-in deployment adapter, not a default provider. It uses the
ambient AWS workload identity (never static credentials), binds ciphertext to
the principal and credential revision with KMS encryption context, and fails
closed when deployment configuration or KMS access is unavailable.
"""
from __future__ import annotations

import base64
import hmac
import secrets
import os
import re
from typing import Any, Mapping


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
    WILSY_GLOBAL_MFA_KMS_KEY_ID, AWS_REGION and optional WILSY_GLOBAL_MFA_KMS_DECRYPT_KEY_IDS for staged key rotation. AWS credentials
    must come from the workload's standard IAM role/credential chain.
    """

    def __init__(self, *, key_id: str, region_name: str | None = None, decrypt_key_ids: list[str] | None = None, client: Any = None) -> None:
        if not isinstance(key_id, str) or not key_id.strip():
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_KEY_ID_REQUIRED")
        self.key_id = key_id.strip()
        key_match = re.fullmatch(
            r"arn:([a-z0-9-]+):kms:([a-z0-9-]+):(\d{12}):key/[A-Za-z0-9-]+",
            self.key_id,
        )
        if key_match is None:
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_KEY_ARN_REQUIRED")
        self.region_name = (region_name or "").strip()
        if not self.region_name:
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_REGION_REQUIRED")
        if self.region_name != key_match.group(2):
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_REGION_KEY_MISMATCH")
        configured_decrypt_ids = decrypt_key_ids or []
        if not isinstance(configured_decrypt_ids, list):
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_DECRYPT_KEYRING_INVALID")
        self.decrypt_key_ids = {self.key_id}
        for decrypt_key_id in configured_decrypt_ids:
            if not isinstance(decrypt_key_id, str):
                raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_DECRYPT_KEYRING_INVALID")
            candidate = decrypt_key_id.strip()
            candidate_match = re.fullmatch(
                r"arn:([a-z0-9-]+):kms:([a-z0-9-]+):(\d{12}):key/[A-Za-z0-9-]+",
                candidate,
            )
            if candidate_match is None or candidate_match.groups() != key_match.groups():
                raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_DECRYPT_KEYRING_INVALID")
            self.decrypt_key_ids.add(candidate)
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
        decrypt_key_ids = [
            item.strip()
            for item in os.getenv("WILSY_GLOBAL_MFA_KMS_DECRYPT_KEY_IDS", "").split(",")
            if item.strip()
        ]
        region_name = (
            os.getenv("WILSY_GLOBAL_MFA_KMS_REGION", "").strip()
            or os.getenv("AWS_REGION", "").strip()
            or os.getenv("AWS_DEFAULT_REGION", "").strip()
        )
        if not region_name:
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_REGION_REQUIRED")
        return cls(
            key_id=key_id,
            region_name=region_name,
            decrypt_key_ids=decrypt_key_ids,
            client=client,
        )

    def validate_access(self) -> None:
        """Prove the configured workload identity can round-trip a synthetic KMS envelope."""
        probe_secret = secrets.token_urlsafe(32)
        probe_principal = f"WILSY_KMS_STARTUP_PROBE:{secrets.token_hex(16)}"
        envelope = self.encrypt_secret(
            secret=probe_secret,
            principal_id=probe_principal,
            credential_revision=0,
        )
        recovered = self.decrypt_secret(
            envelope,
            principal_id=probe_principal,
            credential_revision=0,
        )
        if not isinstance(recovered, str) or not hmac.compare_digest(recovered, probe_secret):
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_STARTUP_PROBE_FAILED")

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
        except Exception as error:
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_ENCRYPT_FAILED") from error

    def decrypt_secret(
        self, envelope: Mapping[str, Any], *, principal_id: str, credential_revision: int
    ) -> str:
        context = _identity_context(principal_id, credential_revision)
        if (
            not isinstance(envelope, Mapping)
            or envelope.get("schema") != ENVELOPE_SCHEMA
            or envelope.get("provider") != PROVIDER_AWS_KMS
            or envelope.get("key_id") not in self.decrypt_key_ids
            or not isinstance(envelope.get("ciphertext"), str)
        ):
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_ENVELOPE_INVALID")
        try:
            ciphertext = base64.b64decode(envelope["ciphertext"], validate=True)
            if not ciphertext:
                raise ValueError("empty ciphertext")
            result = self._client.decrypt(
                CiphertextBlob=ciphertext,
                KeyId=envelope["key_id"],
                EncryptionContext=context,
            )
            plaintext = result.get("Plaintext")
            key_id = result.get("KeyId")
            if key_id != envelope["key_id"]:
                raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_KEY_ID_MISMATCH")
            if not isinstance(plaintext, (bytes, bytearray)) or not plaintext:
                raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_DECRYPTION_EMPTY")
            return bytes(plaintext).decode("utf-8")
        except GlobalMfaKeyManagementError:
            raise
        except Exception as error:
            raise GlobalMfaKeyManagementError("GLOBAL_MFA_KMS_DECRYPT_FAILED") from error


def build_global_mfa_kms_envelope_from_environment(*, client: Any = None) -> AwsKmsGlobalMfaEnvelope | None:
    """Return the configured KMS adapter, or None when provider is absent.

    Region resolution is deterministic: EOS-specific region, AWS_REGION,
    then AWS_DEFAULT_REGION. A configured provider without a region fails closed.
    """
    return AwsKmsGlobalMfaEnvelope.from_environment(client=client)


__all__ = [
    "VERSION",
    "ENVELOPE_SCHEMA",
    "PROVIDER_AWS_KMS",
    "GlobalMfaKeyManagementError",
    "AwsKmsGlobalMfaEnvelope",
    "build_global_mfa_kms_envelope_from_environment",
]
