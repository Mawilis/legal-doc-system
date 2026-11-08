# TITLE: WILSY EOS Local Global Principal MFA KMS CloudFormation Contract Test
# VERSION: v1.0.3-LOCAL-MFA-KMS-CLOUDFORMATION-CONTRACT
# AUTHORITY: Static infrastructure safety certification only.
# EPITOME: Verify the isolated local-development MFA KMS stack without undeclared parser dependencies.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_global_principal_mfa_kms_local_development_cloudformation.py
# COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
# CERTIFICATION OR UPDATE DATE: 2026-11-08.
# CHANGELOG: v1.0.3 verifies exact-role key-policy access without account-wide IAM delegation; v1.0.2 limits resource discovery to Resources and aligns the seal; v1.0.1 scopes resource discovery; v1.0.0 establishes standard-library-only structural checks.
# COMPLIANCE: Test evidence only; does not provision AWS resources or grant runtime authority.
# SECURITY / PRIVACY POSTURE: Reads infrastructure source; uses no credentials, secrets, network, or live AWS resources.
# TENANT BOUNDARY: No tenant data or tenant authority is created or modified.
# AUTHORITY BOUNDARY: Static verification only; no IAM, KMS, EOS, or MongoDB authority.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains exclusive.

from __future__ import annotations

import re
from pathlib import Path


TEMPLATE = (
    Path(__file__).resolve().parents[2]
    / "infra"
    / "aws"
    / "global-principal-mfa-kms-local-development.yaml"
)


def _template_source() -> str:
    """Read the reviewed local-development CloudFormation source as UTF-8."""
    return TEMPLATE.read_text(encoding="utf-8")


def _resource_block(source: str, logical_id: str) -> str:
    """Return one top-level CloudFormation resource block without parsing YAML."""
    lines = source.splitlines()
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if line == f"  {logical_id}:"
        ),
        None,
    )
    assert start is not None, f"Missing CloudFormation resource: {logical_id}"

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if re.fullmatch(r"  [A-Za-z][A-Za-z0-9]*:", lines[index]):
            end = index
            break
    return "\n".join(lines[start:end])


def test_local_stack_declares_only_the_dedicated_key_alias_and_role():
    source = _template_source()
    resources_section = source.split("\nResources:\n", 1)[1].split(
        "\nOutputs:\n", 1
    )[0]
    resources = re.findall(
        r"^  ([A-Za-z][A-Za-z0-9]*):\n    Type: (AWS::[A-Za-z0-9:]+)$",
        resources_section,
        flags=re.MULTILINE,
    )
    assert dict(resources) == {
        "LocalGlobalPrincipalMfaKey": "AWS::KMS::Key",
        "LocalGlobalPrincipalMfaKeyAlias": "AWS::KMS::Alias",
        "LocalGlobalPrincipalMfaRole": "AWS::IAM::Role",
    }


def test_local_role_trust_is_limited_to_the_exact_developer_principal():
    role = _resource_block(_template_source(), "LocalGlobalPrincipalMfaRole")
    assert (
        "Principal:\n"
        "              AWS: !Ref LocalDeveloperPrincipalArn"
    ) in role
    assert "Action: sts:AssumeRole" in role
    assert role.count("Action: sts:AssumeRole") == 1
    assert "sts:AssumeRoleWithWebIdentity" not in role


def test_local_role_can_only_encrypt_and_decrypt_with_the_dedicated_key():
    role = _resource_block(_template_source(), "LocalGlobalPrincipalMfaRole")
    assert (
        "Action:\n"
        "                  - kms:Encrypt\n"
        "                  - kms:Decrypt\n"
        "                Resource: !GetAtt LocalGlobalPrincipalMfaKey.Arn\n"
        "                Condition:\n"
        "                  StringEquals:\n"
        "                    kms:EncryptionContext:purpose: GLOBAL_PRINCIPAL_TOTP"
    ) in role
    assert "kms:*" not in role
    assert "kms:GenerateDataKey" not in role
    assert "kms:CreateGrant" not in role


def test_key_has_rotation_and_delayed_deletion_and_exact_local_alias():
    source = _template_source()
    key = _resource_block(source, "LocalGlobalPrincipalMfaKey")
    alias = _resource_block(source, "LocalGlobalPrincipalMfaKeyAlias")
    assert "EnableKeyRotation: true" in key
    assert "PendingWindowInDays: 30" in key
    assert "KeySpec: SYMMETRIC_DEFAULT" in key
    assert "KeyUsage: ENCRYPT_DECRYPT" in key
    assert "AliasName: alias/wilsy/local-development/global-principal-mfa" in alias
    assert "TargetKeyId: !Ref LocalGlobalPrincipalMfaKey" in alias


def test_key_policy_grants_data_plane_use_only_to_the_exact_local_role():
    source = _template_source()
    key = _resource_block(source, "LocalGlobalPrincipalMfaKey")
    role_grant = key.split("Sid: DedicatedLocalRoleMfaEnvelopeUse", 1)[1].split(
        "Sid: DedicatedLocalKeyAdministration", 1
    )[0]
    assert (
        "AWS: !Sub 'arn:${AWS::Partition}:iam::${AWS::AccountId}:role/"
        "wilsy-eos-global-mfa-local-development'"
    ) in role_grant
    assert "kms:Encrypt" in role_grant
    assert "kms:Decrypt" in role_grant
    assert "kms:EncryptionContext:purpose: GLOBAL_PRINCIPAL_TOTP" in role_grant
    assert "kms:*" not in role_grant
    assert "EnableAccountIamDelegation" not in source
    assert "AWS::AccountId}:root" not in source


def test_key_administration_is_separate_from_local_runtime_use():
    key = _resource_block(_template_source(), "LocalGlobalPrincipalMfaKey")
    assert "AWS: !Ref KeyAdministratorPrincipalArn" in key
    administration = key.split("Sid: DedicatedLocalKeyAdministration", 1)[1]
    assert "kms:Encrypt" not in administration
    assert "kms:Decrypt" not in administration
    assert "kms:ScheduleKeyDeletion" in administration


def test_local_stack_rejects_non_user_principals_and_creates_no_static_credentials():
    source = _template_source()
    assert (
        "AllowedPattern: '^arn:[a-z0-9-]+:iam::[0-9]{12}:user/.+$'"
        in source
    )
    assert "AWS::IAM::AccessKey" not in source
    assert "AccessKeyId" not in source
    assert "SecretAccessKey" not in source
    assert "AWS::EKS::Cluster" not in source
    assert "AWS::IAM::OIDCProvider" not in source
    assert "AssumeRoleWithWebIdentity" not in source
    assert "wilsy-eos-global-mfa-runtime" not in source


# ARTIFACT: test_global_principal_mfa_kms_local_development_cloudformation.py
# VERSION: v1.0.3-LOCAL-MFA-KMS-CLOUDFORMATION-CONTRACT
# AUTHORITY BOUNDARY: static infrastructure safety assertions only
# TENANT POSTURE: no tenant data or authority is created or modified
# FAIL-CLOSED POSTURE: missing or broadened infrastructure controls fail tests
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
