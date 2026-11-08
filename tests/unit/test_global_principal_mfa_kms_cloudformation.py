# TITLE: WILSY EOS Production Global Principal MFA KMS CloudFormation Contract Test
# VERSION: v1.0.0-PRODUCTION-MFA-KMS-CLOUDFORMATION-CONTRACT
# AUTHORITY: Static production infrastructure safety certification only.
# EPITOME: Verify EKS OIDC trust and exact-role MFA KMS data-plane authority.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_global_principal_mfa_kms_cloudformation.py
# COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
# CERTIFICATION OR UPDATE DATE: 2026-11-08.
# CHANGELOG: v1.0.0 certifies exact EKS OIDC issuer constraints, role-first key creation, and direct KMS policy grants to the exact production EOS role.
# COMPLIANCE: Static test evidence only; does not provision AWS or certify a production hosting target.
# SECURITY / PRIVACY POSTURE: Reads infrastructure source only; no credentials, network, or live AWS resources.
# TENANT BOUNDARY: No tenant data or identity is created or modified.
# AUTHORITY BOUNDARY: Verifies production workload trust and key use only; no runtime authority is granted by the test.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains exclusive.

from __future__ import annotations

import re
from pathlib import Path


TEMPLATE = (
    Path(__file__).resolve().parents[2]
    / "infra"
    / "aws"
    / "global-principal-mfa-kms.yaml"
)


def _template_source() -> str:
    """Read the production MFA KMS CloudFormation source as UTF-8."""
    return TEMPLATE.read_text(encoding="utf-8")


def _oidc_issuer_host_path_pattern() -> str:
    """Return the constrained OIDC issuer host/path pattern from the template."""
    source = _template_source()
    parameter = source.split("  EosEksOidcIssuerHostPath:", 1)[1].split(
        "  EosServiceAccountSubject:", 1
    )[0]
    match = re.search(r"AllowedPattern:\\s*'([^']+)'", parameter)
    assert match is not None, "EKS OIDC issuer host/path must have an explicit constraint"
    return match.group(1)


def test_real_eks_oidc_issuer_identifier_accepts_alphanumeric_provider_id():
    pattern = _oidc_issuer_host_path_pattern()
    actual_eks_issuer = (
        "oidc.eks.af-south-1.amazonaws.com/"
        "id/EXAMPLED539D4633E53DE1B71EXAMPLE"
    )
    assert re.fullmatch(pattern, actual_eks_issuer)


def test_eks_oidc_issuer_host_path_rejects_scheme_and_untrusted_suffixes():
    pattern = _oidc_issuer_host_path_pattern()
    assert re.fullmatch(
        pattern,
        "oidc.eks.af-south-1.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE",
    )
    assert not re.fullmatch(
        pattern,
        "https://oidc.eks.af-south-1.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE",
    )
    assert not re.fullmatch(
        pattern,
        "oidc.eks.af-south-1.amazonaws.com/id/EXAMPLE/attacker",
    )


def test_production_key_policy_grants_data_plane_use_only_to_exact_eos_role():
    source = _template_source()
    key = source.split("  GlobalPrincipalMfaKey:\\n", 1)[1].split(
        "\\n  GlobalPrincipalMfaKeyAlias:", 1
    )[0]
    assert "DependsOn: EosGlobalMfaRuntimeRole" in key
    role_grant = key.split("Sid: DedicatedEosRuntimeMfaEnvelopeUse", 1)[1].split(
        "Sid: DedicatedKeyAdministration", 1
    )[0]
    assert (
        "AWS: !Sub 'arn:${AWS::Partition}:iam::${AWS::AccountId}:role/"
        "wilsy-eos-global-mfa-runtime'"
    ) in role_grant
    assert "kms:Encrypt" in role_grant
    assert "kms:Decrypt" in role_grant
    assert "kms:EncryptionContext:purpose: GLOBAL_PRINCIPAL_TOTP" in role_grant
    assert "kms:*" not in role_grant
    assert "EnableAccountIamDelegation" not in source
    assert "AWS::AccountId}:root" not in source


def test_production_runtime_role_has_exact_oidc_trust_and_no_broader_policy():
    source = _template_source()
    role = source.split("  EosGlobalMfaRuntimeRole:\\n", 1)[1].split(
        "\\nOutputs:", 1
    )[0]
    assert "RoleName: wilsy-eos-global-mfa-runtime" in role
    assert "sts:AssumeRoleWithWebIdentity" in role
    assert "Policies:" not in role
    assert "kms:" not in role


def test_production_eks_stack_has_no_local_development_identity_or_grant():
    source = _template_source()
    assert "LocalDevelopmentPrincipalArn" not in source
    assert "ApprovedLocalDevelopmentMfaEnvelopeUse" not in source


# ARTIFACT: test_global_principal_mfa_kms_cloudformation.py
# VERSION: v1.0.0-PRODUCTION-MFA-KMS-CLOUDFORMATION-CONTRACT
# AUTHORITY BOUNDARY: static production KMS infrastructure assertions only
# TENANT POSTURE: no tenant data or identity is created or modified
# FAIL-CLOSED POSTURE: broadened OIDC or KMS authority fails tests
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
