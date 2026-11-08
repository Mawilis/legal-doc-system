# TITLE: WILSY EOS Global Principal MFA KMS Envelope Contract Tests
# VERSION: v1.0.1-GLOBAL-MFA-KMS-ENVELOPE-CONTRACT
# AUTHORITY: Static cryptographic adapter certification only; no live KMS or identity authority.
# EPITOME: Verify principal/revision-bound AWS KMS envelopes, synthetic startup access validation, key rotation constraints, explicit region selection and fail-closed error behavior.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_global_principal_mfa_kms_envelope.py
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; Python EOS Global Principal MFA.
# CERTIFICATION OR UPDATE DATE: 2026-11-09
# CHANGELOG:
#   v1.0.1-GLOBAL-MFA-KMS-ENVELOPE-CONTRACT adds the mandatory sovereign
#   artifact header, module documentation and end seal. Test assertions and
#   runtime behavior are unchanged.
#   v1.0.0 established the KMS envelope, context, region, rotation and denial tests.
# COMPLIANCE: AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
# SECURITY / PRIVACY POSTURE: Uses synthetic in-memory KMS client fixtures only; no real factor secrets, AWS credentials or KMS calls.
# TENANT BOUNDARY: Synthetic principal identifiers only; no tenant or membership records are created or mutated.
# AUTHORITY BOUNDARY: Test-only evidence; cannot enroll factors, issue sessions or grant KMS permissions.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains the exclusive financial execution authority.

"""Contract tests for the Python EOS Global Principal MFA KMS envelope adapter.

All cryptographic calls are handled by a deterministic in-memory client. These
tests do not contact AWS or certify a production workload identity.
"""

from __future__ import annotations

import base64
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
        self.last_plaintext = b"JBSWY3DPEHPK3PXP"
        self.last_context = {
            "purpose": "GLOBAL_PRINCIPAL_TOTP",
            "principal_id": "principal-1",
            "credential_revision": "9",
        }

    def encrypt(self, **kwargs):
        self.encrypt_calls.append(kwargs)
        self.last_plaintext = kwargs["Plaintext"]
        self.last_context = kwargs["EncryptionContext"]
        return {"CiphertextBlob": b"ciphertext", "KeyId": "arn:aws:kms:af-south-1:123456789012:key/test"}

    def decrypt(self, **kwargs):
        self.decrypt_calls.append(kwargs)
        if kwargs["EncryptionContext"] != self.last_context:
            raise ValueError("encryption context mismatch")
        return {
            "Plaintext": self.last_plaintext,
            "KeyId": kwargs["KeyId"],
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


def test_startup_access_validation_round_trips_ephemeral_probe_without_persistence():
    client = _KmsClient()
    adapter = AwsKmsGlobalMfaEnvelope(key_id=KEY, region_name="af-south-1", client=client)
    adapter.validate_access()
    assert len(client.encrypt_calls) == 1
    assert len(client.decrypt_calls) == 1
    context = client.encrypt_calls[0]["EncryptionContext"]
    assert context["purpose"] == "GLOBAL_PRINCIPAL_TOTP"
    assert context["principal_id"].startswith("WILSY_KMS_STARTUP_PROBE:")
    assert context["credential_revision"] == "0"


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


OLD_KEY = "arn:aws:kms:af-south-1:123456789012:key/previous"


def test_decrypt_supports_explicitly_allowlisted_previous_key_during_rotation():
    client = _KmsClient()
    adapter = AwsKmsGlobalMfaEnvelope(
        key_id=KEY,
        region_name="af-south-1",
        decrypt_key_ids=[OLD_KEY],
        client=client,
    )
    envelope = {
        "schema": ENVELOPE_SCHEMA,
        "provider": "AWS_KMS",
        "key_id": OLD_KEY,
        "ciphertext": base64.b64encode(b"old-ciphertext").decode("ascii"),
    }
    assert adapter.decrypt_secret(
        envelope, principal_id="principal-1", credential_revision=9
    ) == "JBSWY3DPEHPK3PXP"
    assert client.decrypt_calls[0]["KeyId"] == OLD_KEY


def test_rotation_keyring_rejects_key_from_another_region():
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_DECRYPT_KEYRING_INVALID"):
        AwsKmsGlobalMfaEnvelope(
            key_id=KEY,
            region_name="af-south-1",
            decrypt_key_ids=["arn:aws:kms:eu-west-1:123456789012:key/other"],
            client=_KmsClient(),
        )
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_DECRYPT_KEYRING_INVALID"):
        AwsKmsGlobalMfaEnvelope(
            key_id=KEY,
            region_name="af-south-1",
            decrypt_key_ids=["arn:aws:kms:af-south-1:999999999999:key/other"],
            client=_KmsClient(),
        )


def test_kms_adapter_requires_full_key_arn_and_matching_explicit_region():
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_KEY_ARN_REQUIRED"):
        AwsKmsGlobalMfaEnvelope(key_id="alias/wilsy-mfa", region_name="af-south-1", client=_KmsClient())
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_REGION_REQUIRED"):
        AwsKmsGlobalMfaEnvelope(key_id=KEY, client=_KmsClient())
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_REGION_KEY_MISMATCH"):
        AwsKmsGlobalMfaEnvelope(key_id=KEY, region_name="eu-west-1", client=_KmsClient())


def test_environment_factory_requires_and_uses_explicit_aws_region(monkeypatch):
    monkeypatch.setenv("WILSY_GLOBAL_MFA_KMS_PROVIDER", "AWS_KMS")
    monkeypatch.setenv("WILSY_GLOBAL_MFA_KMS_KEY_ID", KEY)
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
    monkeypatch.delenv("WILSY_GLOBAL_MFA_KMS_REGION", raising=False)
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_REGION_REQUIRED"):
        build_global_mfa_kms_envelope_from_environment(client=_KmsClient())

    monkeypatch.setenv("AWS_REGION", "af-south-1")
    adapter = build_global_mfa_kms_envelope_from_environment(client=_KmsClient())
    assert adapter is not None
    assert adapter.region_name == "af-south-1"


def test_invalid_identity_context_is_rejected():
    client = _KmsClient()
    adapter = AwsKmsGlobalMfaEnvelope(key_id=KEY, region_name="af-south-1", client=client)
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_CONTEXT_INVALID"):
        adapter.encrypt_secret(secret="secret", principal_id=" ", credential_revision=1)
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_CONTEXT_INVALID"):
        adapter.encrypt_secret(secret="secret", principal_id="principal-1", credential_revision=True)


def test_kms_access_denied_on_encrypt_fails_closed():
    client = _KmsClient()

    def denied_encrypt(**kwargs):
        raise RuntimeError("AccessDeniedException: kms:Encrypt is not authorized")

    client.encrypt = denied_encrypt
    adapter = AwsKmsGlobalMfaEnvelope(key_id=KEY, region_name="af-south-1", client=client)
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_ENCRYPT_FAILED"):
        adapter.encrypt_secret(secret="secret", principal_id="principal-1", credential_revision=1)


def test_kms_access_denied_on_decrypt_fails_closed():
    client = _KmsClient()
    adapter = AwsKmsGlobalMfaEnvelope(key_id=KEY, region_name="af-south-1", client=client)
    envelope = adapter.encrypt_secret(
        secret="secret", principal_id="principal-1", credential_revision=1
    )

    def denied_decrypt(**kwargs):
        raise RuntimeError("AccessDeniedException: kms:Decrypt is not authorized")

    client.decrypt = denied_decrypt
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_DECRYPT_FAILED"):
        adapter.decrypt_secret(envelope, principal_id="principal-1", credential_revision=1)


def test_startup_probe_fails_when_kms_returns_different_plaintext():
    client = _KmsClient()
    original_decrypt = client.decrypt

    def altered_decrypt(**kwargs):
        result = original_decrypt(**kwargs)
        return {**result, "Plaintext": b"not-the-probe-secret"}

    client.decrypt = altered_decrypt
    adapter = AwsKmsGlobalMfaEnvelope(key_id=KEY, region_name="af-south-1", client=client)
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_STARTUP_PROBE_FAILED"):
        adapter.validate_access()


def test_kms_encrypt_rejects_response_from_unexpected_key():
    client = _KmsClient()

    def wrong_key_encrypt(**kwargs):
        return {"CiphertextBlob": b"ciphertext", "KeyId": OLD_KEY}

    client.encrypt = wrong_key_encrypt
    adapter = AwsKmsGlobalMfaEnvelope(key_id=KEY, region_name="af-south-1", client=client)
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_KEY_ID_MISMATCH"):
        adapter.encrypt_secret(secret="secret", principal_id="principal-1", credential_revision=1)


def test_environment_factory_prefers_explicit_eos_region(monkeypatch):
    monkeypatch.setenv("WILSY_GLOBAL_MFA_KMS_PROVIDER", "AWS_KMS")
    monkeypatch.setenv("WILSY_GLOBAL_MFA_KMS_KEY_ID", KEY)
    monkeypatch.setenv("WILSY_GLOBAL_MFA_KMS_REGION", "af-south-1")
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    adapter = build_global_mfa_kms_envelope_from_environment(client=_KmsClient())
    assert adapter is not None
    assert adapter.region_name == "af-south-1"


def test_environment_factory_falls_back_to_aws_default_region(monkeypatch):
    monkeypatch.setenv("WILSY_GLOBAL_MFA_KMS_PROVIDER", "AWS_KMS")
    monkeypatch.setenv("WILSY_GLOBAL_MFA_KMS_KEY_ID", KEY)
    monkeypatch.delenv("WILSY_GLOBAL_MFA_KMS_REGION", raising=False)
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "af-south-1")
    adapter = build_global_mfa_kms_envelope_from_environment(client=_KmsClient())
    assert adapter is not None
    assert adapter.region_name == "af-south-1"


def test_environment_factory_rejects_region_mismatch_before_kms_client_use(monkeypatch):
    monkeypatch.setenv("WILSY_GLOBAL_MFA_KMS_PROVIDER", "AWS_KMS")
    monkeypatch.setenv("WILSY_GLOBAL_MFA_KMS_KEY_ID", KEY)
    monkeypatch.setenv("WILSY_GLOBAL_MFA_KMS_REGION", "eu-west-1")
    with pytest.raises(GlobalMfaKeyManagementError, match="GLOBAL_MFA_KMS_REGION_KEY_MISMATCH"):
        build_global_mfa_kms_envelope_from_environment(client=_KmsClient())


# ARTIFACT: tests/unit/test_global_principal_mfa_kms_envelope.py
# VERSION: v1.0.1-GLOBAL-MFA-KMS-ENVELOPE-CONTRACT
# AUTHORITY BOUNDARY: Static adapter contract tests only; no live KMS or factor authority.
# TENANT POSTURE: Synthetic principal context only; no tenant or membership state is changed.
# FAIL-CLOSED POSTURE: Key, region, context, envelope and provider regressions fail the focused suite.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
