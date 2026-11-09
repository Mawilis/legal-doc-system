"""WILSY EOS local-development Global Principal MFA KMS identity probe.

TITLE: WILSY EOS Local Global Principal MFA KMS Probe
VERSION: v1.0.0-LOCAL-EOS-MFA-KMS-PROBE
AUTHORITY: Local-development infrastructure verification only.
EPITOME: Verify the dedicated assumed role and execute the production EOS KMS
         envelope adapter's synthetic encrypt/decrypt validation without
         persisting or disclosing authentication material.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/global_principal_mfa_kms_probe.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
CERTIFICATION OR UPDATE DATE: 2026-11-08.
CHANGELOG: v1.0.0 establishes an account-pinned, role-pinned local KMS probe
           using the canonical EOS envelope adapter.
COMPLIANCE: Operator-invoked verification; no AWS resources are provisioned.
SECURITY / PRIVACY POSTURE: Uses ambient assumed-role credentials; emits no
                            credentials, key material, TOTP material,
                            plaintext, ciphertext, or database content.
TENANT BOUNDARY: Synthetic probe principal only; no tenant identity or data.
AUTHORITY BOUNDARY: No IAM, membership, MFA enrollment, session, or workspace
                    authority is issued or changed.
FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS
                              remains exclusive.

Run with AWS_PROFILE set to the dedicated assumed-role profile. The probe
never prints credentials, plaintext, ciphertext, TOTP material, or key policy.
"""
from __future__ import annotations

import sys

from tools.eos.auth.global_principal_mfa_kms_envelope import (
    build_global_mfa_kms_envelope_from_environment,
)


EXPECTED_ACCOUNT_ID = "121014832643"
EXPECTED_ROLE_NAME = "wilsy-eos-global-mfa-local-development"


def main() -> int:
    """Verify the pinned local AWS role and the canonical EOS KMS envelope.

    Authority: local infrastructure verification only; this function does not
    provision resources, enroll MFA, create sessions, or mutate tenant data.
    Inputs: AWS credentials from the configured assumed-role profile and the
    explicit EOS KMS environment configuration.
    Output: zero only after account, role, and synthetic KMS round-trip checks;
    otherwise one with only the exception class disclosed.
    Fail-closed: identity mismatch, missing configuration, or KMS failure
    returns nonzero and never falls back to a local encryption key.
    """
    try:
        import boto3

        identity = boto3.client("sts").get_caller_identity()
        arn = identity.get("Arn", "")
        if identity.get("Account") != EXPECTED_ACCOUNT_ID:
            raise RuntimeError("LOCAL_EOS_MFA_AWS_ACCOUNT_MISMATCH")
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


# ARTIFACT: global_principal_mfa_kms_probe.py
# VERSION: v1.0.0-LOCAL-EOS-MFA-KMS-PROBE
# AUTHORITY BOUNDARY: local-development AWS identity and KMS capability probe only
# TENANT POSTURE: synthetic probe principal; no tenant data or identity mutation
# FAIL-CLOSED POSTURE: any account, role, configuration, or KMS failure exits nonzero
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
