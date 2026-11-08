"""Static safety contract for the isolated local-development MFA KMS stack."""
from __future__ import annotations

from pathlib import Path

import yaml


TEMPLATE = (
    Path(__file__).resolve().parents[2]
    / "infra"
    / "aws"
    / "global-principal-mfa-kms-local-development.yaml"
)


def _load_template() -> dict:
    class CfnLoader(yaml.SafeLoader):
        pass

    def _construct_tag(loader, tag_suffix, node):
        if isinstance(node, yaml.ScalarNode):
            value = loader.construct_scalar(node)
        elif isinstance(node, yaml.SequenceNode):
            value = loader.construct_sequence(node)
        else:
            value = loader.construct_mapping(node)
        if tag_suffix == "GetAtt" and isinstance(value, str):
            value = value.split(".", 1)
        key = "Fn::GetAtt" if tag_suffix == "GetAtt" else tag_suffix
        return {key: value}

    CfnLoader.add_multi_constructor("!", _construct_tag)
    return yaml.load(TEMPLATE.read_text(encoding="utf-8"), Loader=CfnLoader)


def test_local_stack_creates_only_dedicated_key_alias_and_assumable_role():
    template = _load_template()
    resources = template["Resources"]
    assert set(resources) == {
        "LocalGlobalPrincipalMfaKey",
        "LocalGlobalPrincipalMfaKeyAlias",
        "LocalGlobalPrincipalMfaRole",
    }
    assert resources["LocalGlobalPrincipalMfaKey"]["Type"] == "AWS::KMS::Key"
    assert resources["LocalGlobalPrincipalMfaKeyAlias"]["Type"] == "AWS::KMS::Alias"
    assert resources["LocalGlobalPrincipalMfaRole"]["Type"] == "AWS::IAM::Role"


def test_local_role_trust_and_kms_permissions_are_narrowly_scoped():
    template = _load_template()
    role = template["Resources"]["LocalGlobalPrincipalMfaRole"]["Properties"]
    trust = role["AssumeRolePolicyDocument"]["Statement"]
    assert trust[0]["Principal"]["AWS"] == {"Ref": "LocalDeveloperPrincipalArn"}
    assert trust[0]["Action"] == "sts:AssumeRole"
    statement = role["Policies"][0]["PolicyDocument"]["Statement"][0]
    assert statement["Action"] == ["kms:Encrypt", "kms:Decrypt"]
    assert statement["Resource"] == {"Fn::GetAtt": ["LocalGlobalPrincipalMfaKey", "Arn"]}
    assert statement["Condition"]["StringEquals"] == {
        "kms:EncryptionContext:purpose": "GLOBAL_PRINCIPAL_TOTP"
    }


def test_local_stack_does_not_create_static_credentials_or_production_identity():
    source = TEMPLATE.read_text(encoding="utf-8")
    template = _load_template()
    resource_types = {item["Type"] for item in template["Resources"].values()}
    assert "AWS::IAM::AccessKey" not in resource_types
    assert "AWS::EKS::Cluster" not in resource_types
    assert "AWS::IAM::OIDCProvider" not in resource_types
    assert "AccessKeyId" not in source
    assert "SecretAccessKey" not in source
    assert "AssumeRoleWithWebIdentity" not in source
    assert "wilsy-eos-global-mfa-runtime" not in source
