# TITLE: WILSY EOS ECS Fargate Production Foundation Contract Tests
# VERSION: v1.0.1-EOS-ECS-PRODUCTION-FOUNDATION-CONTRACT
# AUTHORITY: Static infrastructure safety certification; no provisioning authority.
# EPITOME: Assert the inactive ECS foundation's task/service boundary, immutable image and secret references, role separation, and purpose-scoped production MFA KMS access.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_eos_production_ecs_foundation.py
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; Python EOS and infrastructure governance.
# CERTIFICATION OR UPDATE DATE: 2026-11-09
# CHANGELOG:
#   v1.0.1-EOS-ECS-PRODUCTION-FOUNDATION-CONTRACT adds the mandatory sovereign
#   artifact contract and module-level documentation. Assertions are retained;
#   no runtime or infrastructure behavior is changed.
#   v1.0.0 established static safety assertions for the ECS foundation.
# COMPLIANCE: AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
# SECURITY / PRIVACY POSTURE: Reads repository template text only; no AWS calls, credentials, secrets or live data.
# TENANT BOUNDARY: No tenant, principal, membership, session or database record is accessed or mutated.
# AUTHORITY BOUNDARY: Test-only evidence; cannot provision resources, launch tasks or grant runtime permissions.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains the exclusive financial execution authority.

"""Static contract tests for the deliberately inactive ECS production foundation.

These assertions inspect the checked-in CloudFormation source. They do not
prove AWS resource existence, successful provisioning, effective IAM policy,
task startup, database connectivity, or production readiness.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "infra" / "aws" / "eos-production-ecs-foundation.yaml"


def _source() -> str:
    """Read the repository-owned ECS template without contacting AWS."""
    return TEMPLATE.read_text(encoding="utf-8")


def test_ecs_foundation_defines_only_fargate_cluster_and_task_definition():
    source = _source()
    assert "Type: AWS::ECS::Cluster" in source
    assert "Type: AWS::ECS::TaskDefinition" in source
    assert "RequiresCompatibilities:" in source
    assert "- FARGATE" in source
    assert "Type: AWS::ECS::Service" not in source
    assert "AWS::ECS::Service" not in source
    assert "DesiredCount:" not in source
    assert "RunTask" not in source


def test_task_definition_requires_immutable_ghcr_digest_and_existing_secrets():
    source = _source()
    assert "AllowedPattern: '^ghcr\\.io/" in source
    assert "@sha256:[a-f0-9]{64}" in source
    assert "GhcrCredentialsSecretArn" in source
    assert "MongoDbUriSecretArn" in source
    assert "RepositoryCredentials:" in source
    assert "CredentialsParameter: !Ref GhcrCredentialsSecretArn" in source
    assert "ValueFrom: !Ref MongoDbUriSecretArn" in source


def test_runtime_and_execution_roles_have_separate_authorities():
    source = _source()
    runtime_role = source.split("  EosProductionTaskRole:", 1)[1].split(
        "  EosProductionExecutionRole:", 1
    )[0]
    execution_role = source.split("  EosProductionExecutionRole:", 1)[1].split(
        "  EosProductionMfaKey:", 1
    )[0]
    assert "ecs-tasks.amazonaws.com" in runtime_role
    assert "kms:Encrypt" not in runtime_role
    assert "kms:Decrypt" not in runtime_role
    assert "secretsmanager:" not in runtime_role
    assert "AmazonECSTaskExecutionRolePolicy" in execution_role
    assert "secretsmanager:GetSecretValue" in execution_role
    assert "kms:Encrypt" not in execution_role
    assert "kms:Decrypt" not in execution_role


def test_production_mfa_key_is_separate_and_context_restricted():
    source = _source()
    assert "alias/wilsy/production/global-principal-mfa" in source
    assert "KeyAdministratorRoleArn" in source
    assert "AllowOnlyEosProductionTaskDataPlane" in source
    assert "kms:EncryptionContext:purpose: GLOBAL_PRINCIPAL_TOTP" in source
    key_policy = source.split("  EosProductionMfaKey:", 1)[1].split(
        "  EosProductionMfaKeyAlias:", 1
    )[0]
    assert "AWS: !GetAtt EosProductionTaskRole.Arn" in key_policy
    assert "wilsy-eos-global-mfa-local-development" not in source
    assert "AdministratorAccess" not in source


def test_production_task_definition_enforces_python_eos_and_startup_kms_probe():
    source = _source()
    assert "WILSY_GLOBAL_MFA_KMS_PROVIDER" in source
    assert "AWS_KMS" in source
    assert "WILSY_GLOBAL_MFA_KMS_KEY_ID" in source
    assert "WILSY_GLOBAL_MFA_KMS_REGION" in source
    assert "MONGODB_URI" in source
    assert "9095" in source
    assert "User: '10001'" in source
    assert "ReadonlyRootFilesystem: true" in source
    assert "server.js" not in source.lower()
    assert "NODE_ENV" not in source


def test_production_stack_does_not_invent_networking_or_ingress():
    source = _source()
    assert "AWS::EC2::VPC" not in source
    assert "AWS::ElasticLoadBalancingV2::LoadBalancer" not in source
    assert "AWS::Route53::RecordSet" not in source
    assert "AWS::ECS::Service" not in source
    assert "desired count" in source.lower()
    assert "121014832643" in source
    assert "af-south-1" in source


# ARTIFACT: tests/unit/test_eos_production_ecs_foundation.py
# VERSION: v1.0.1-EOS-ECS-PRODUCTION-FOUNDATION-CONTRACT
# AUTHORITY BOUNDARY: Static template assertions only; no provisioning or task activation.
# TENANT POSTURE: No tenant, identity, session or database records are accessed or mutated.
# FAIL-CLOSED POSTURE: Missing or weakened infrastructure invariants fail the focused test suite.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
