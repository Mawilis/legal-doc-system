from __future__ import annotations

import base64
from types import SimpleNamespace

import pytest

from tools.eos.auth.global_principal_mfa_kms_envelope import (
    ENVELOPE_SCHEMA,
    GlobalMfaKeyManagementError,
    AwsKmsGlobalMfaEnvelope,
    build_global_mfa_kms_envelope_from_environment,
)


class _KmsClient:
    def __init__(self) -> None:
        self.encrypt_calls = []
        self.decrypt_calls = []

    def encrypt(self, **kwargs):
        self.encrypt_calls.append(kwargs)
        return {"CiphertextBlob": b"ciphertext", "KeyId": "arn:aws:kms:af-south-1:123456789012:key/test"}

    def decrypt(self, **kwargs):
        self.decrypt_calls.append(kwargs)
        return {
            "Plaintext": b"JBSWY3DPEHPK3PXP",
            "KeyId": "arn:aws:kms:af-south-1:123456789012:key/test",
        }


KEY = "arn:aws:kms:af-south-1:123456789012:key/test"


def test_encrypt_and_decrypt_bind_ciphertext_to_principal_and_credential_epoch():
    client = _KmsClient()
    adapter = AwsKmsGlobalMfaEnvelope(key_id=KEY, region_name="af-south-1", client=client)
    envelope = adapter.encrypt_secret(
        secret="JBSWY3DPEHPK3PXP",
        principal_id="principal-1",
        credential_revision=9,
    )
    assert envelope == {
        "schema": ENVELOPE_SCHEMA,
        "provider": "AWS_KMS",
        "key_id": KEY,
        "ciphertext": base64.b64encode(b"ciphertext").decode("ascii"),
    }
    assert client.encrypt_calls[0]["EncryptionContext"] == {
        "purpose": "GLOBAL_PRINCIPAL_TOTP",
        "principal_id": "principal-1",
        "credential_revision": "9",
    }
    assert adapter.decrypt_secret(
        envelope, principal_id="principal-1", credential_revision=9
    ) == "JBSWY3DPEHPK3PXP"
    assert client.decrypt_calls[0]["EncryptionContext"] == client.encrypt_calls[0]["EncryptionContext"]


def test_ciphertext_cannot_be_decrypted_for_another_principal_or_revision():
    client = _KmsClient()
    adapter = AwsKmsGlobalMfaEnvelope(key_id=KEY, region_name="af-south-1", client=client)
    envelope = adapter.encrypt_secret(
        secret="secret", principal_id="principal-1", credential_revision=9
    )
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_DECRYPT_FAILED"):
        adapter.decrypt_secret(envelope, principal_id="principal-2", credential_revision=9)
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_DECRYPT_FAILED"):
        adapter.decrypt_secret(envelope, principal_id="principal-1", credential_revision=10)


def test_envelope_key_substitution_is_rejected_before_kms_call():
    client = _KmsClient()
    adapter = AwsKmsGlobalMfaEnvelope(key_id=KEY, region_name="af-south-1", client=client)
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_ENVELOPE_INVALID"):
        adapter.decrypt_secret(
            {"schema": ENVELOPE_SCHEMA, "provider": "AWS_KMS", "key_id": "other", "ciphertext": "YQ=="},
            principal_id="principal-1",
            credential_revision=1,
        )
    assert client.decrypt_calls == []


def test_environment_factory_is_disabled_without_explicit_provider(monkeypatch):
    monkeypatch.delenv("WILSY_GLOBAL_MFA_KMS_PROVIDER", raising=False)
    monkeypatch.delenv("WILSY_GLOBAL_MFA_KMS_KEY_ID", raising=False)
    assert build_global_mfa_kms_envelope_from_environment(client=object()) is None


def test_environment_factory_requires_key_id_and_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("WILSY_GLOBAL_MFA_KMS_PROVIDER", "AWS_KMS")
    monkeypatch.delenv("WILSY_GLOBAL_MFA_KMS_KEY_ID", raising=False)
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_KEY_ID_REQUIRED"):
        build_global_mfa_kms_envelope_from_environment(client=object())
    monkeypatch.setenv("WILSY_GLOBAL_MFA_KMS_PROVIDER", "LOCAL")
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_PROVIDER_UNSUPPORTED"):
        build_global_mfa_kms_envelope_from_environment(client=object())


def test_invalid_identity_context_is_rejected():
    client = _KmsClient()
    adapter = AwsKmsGlobalMfaEnvelope(key_id=KEY, region_name="af-south-1", client=client)
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_CONTEXT_INVALID"):
        adapter.encrypt_secret(secret="secret", principal_id=" ", credential_revision=1)
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_CONTEXT_INVALID"):
        adapter.encrypt_secret(secret="secret", principal_id="principal-1", credential_revision=True)
