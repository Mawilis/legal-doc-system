# TITLE: WILSY EOS ECS Fargate Production Foundation Contract Tests
# VERSION: v1.0.3-EOS-ECS-IDENTITY-VERIFIER-CONTRACT
# AUTHORITY: Static infrastructure safety certification; no provisioning authority.
# EPITOME: Assert the inactive ECS foundation's service boundary, immutable image and secret references, role separation, purpose-scoped MFA KMS access, and non-root writable task-volume contract.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_eos_production_ecs_foundation.py
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; Python EOS and infrastructure governance.
# CERTIFICATION OR UPDATE DATE: 2026-11-09
# CHANGELOG:
#   v1.0.3 adds assertions that the task definition injects the exact expected
#   task-role ARN used by the production ECS metadata/STS/KMS verifier.
#   v1.0.2-EOS-ECS-WRITABLE-TASK-VOLUMES asserts that the published Python EOS
#   image prepares UID/GID 10001-owned task-volume mount points and that ECS
#   mounts task-scoped /tmp while retaining a read-only root filesystem.
#   v1.0.1 added the sovereign artifact contract and module documentation.
#   v1.0.0 established static safety assertions for the ECS foundation.
# COMPLIANCE: AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
# SECURITY / PRIVACY POSTURE: Reads repository template and Dockerfile text only; no AWS calls, credentials, secrets or live data.
# TENANT BOUNDARY: No tenant, principal, membership, session or database record is accessed or mutated.
# AUTHORITY BOUNDARY: Test-only evidence; cannot provision resources, launch tasks or grant runtime permissions.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains the exclusive financial execution authority.

"""Static contract tests for the deliberately inactive ECS production foundation.

These assertions inspect checked-in CloudFormation and image-build source. They
do not prove AWS resource existence, successful provisioning, effective IAM
policy, task startup, database connectivity, or production readiness.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "infra" / "aws" / "eos-production-ecs-foundation.yaml"
IMAGE_DOCKERFILE = ROOT / "infra" / "docker" / "Dockerfile.eos"


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
    assert "WILSY_ECS_EXPECTED_TASK_ROLE_ARN" in source
    assert "Value: !GetAtt EosProductionTaskRole.Arn" in source
    assert "MONGODB_URI" in source
    assert "9095" in source
    assert "User: '10001'" in source
    assert "ReadonlyRootFilesystem: true" in source
    assert "server.js" not in source.lower()
    assert "NODE_ENV" not in source


def test_non_root_image_and_task_volumes_have_writable_owned_mount_points():
    source = _source()
    image = IMAGE_DOCKERFILE.read_text(encoding="utf-8")
    assert "USER 10001:10001" in image
    assert "mkdir -p /app/data /app/reports /var/log/wilsy-os /tmp" in image
    assert (
        "chown -R 10001:10001 /app/data /app/reports /var/log/wilsy-os /tmp"
        in image
    )
    assert "chmod 1777 /tmp" in image
    assert "- Name: eos-tmp" in source
    assert "SourceVolume: eos-tmp" in source
    assert "ContainerPath: /tmp" in source
    assert "ReadonlyRootFilesystem: true" in source


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
# VERSION: v1.0.3-EOS-ECS-IDENTITY-VERIFIER-CONTRACT
# AUTHORITY BOUNDARY: Static template and image-build assertions only; no provisioning or task activation.
# TENANT POSTURE: No tenant, identity, session or database records are accessed or mutated.
# FAIL-CLOSED POSTURE: Missing or weakened infrastructure and image-volume invariants fail the focused test suite.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
