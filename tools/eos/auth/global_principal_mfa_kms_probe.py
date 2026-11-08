"""Verify the local EOS AWS role and Global Principal MFA KMS round trip.

Run with AWS_PROFILE set to the dedicated assumed-role profile. This command
never prints credentials, plaintext, ciphertext, TOTP material, or key policy.
"""
from __future__ import annotations

import sys

from tools.eos.auth.global_principal_mfa_kms_envelope import (
    GlobalMfaKeyManagementError,
    build_global_mfa_kms_envelope_from_environment,
)


EXPECTED_ROLE_NAME = "wilsy-eos-global-mfa-local-development"


def main() -> int:
    try:
        import boto3

        identity = boto3.client("sts").get_caller_identity()
        arn = identity.get("Arn", "")
        if f":assumed-role/{EXPECTED_ROLE_NAME}/" not in arn:
            raise RuntimeError("LOCAL_EOS_MFA_ROLE_IDENTITY_REQUIRED")
        envelope = build_global_mfa_kms_envelope_from_environment()
        if envelope is None:
            raise RuntimeError("GLOBAL_MFA_KMS_PROVIDER_REQUIRED")
        envelope.validate_access()
    except Exception as error:
        print(
            f"LOCAL_EOS_MFA_KMS_PROBE=FAILED ({type(error).__name__})",
            file=sys.stderr,
        )
        return 1

    print("LOCAL_EOS_MFA_ROLE=VERIFIED")
    print("LOCAL_EOS_MFA_KMS_ENCRYPT_DECRYPT=PASSED")
    print("LOCAL_EOS_MFA_KMS_STARTUP_PROBE=PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
