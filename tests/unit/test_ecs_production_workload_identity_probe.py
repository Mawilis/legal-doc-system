# TITLE: WILSY EOS Production ECS Workload Identity Probe Tests
# VERSION: v1.0.2-ECS-PRODUCTION-MISSING-METADATA-TEST
# AUTHORITY: Unit certification of production ECS identity-verification logic only.
# EPITOME: Prove fail-closed metadata endpoint, task ARN, exact STS role and production boundary validation without contacting AWS.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_ecs_production_workload_identity_probe.py
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; isolated unit certification.
# CERTIFICATION OR UPDATE DATE: 2026-11-09
# CHANGELOG:
#   v1.0.2 corrects the missing-task-metadata negative fixture so it omits
#   the required cluster, family and revision fields.
#   v1.0.1 verifies exact cluster/task-family binding and positive task revision.
#   v1.0.0 establishes deterministic unit coverage for the production ECS
#   workload identity verifier and rejects non-production or alternate roles.
# COMPLIANCE: AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
# SECURITY / PRIVACY POSTURE: Uses synthetic metadata and identity values only; no AWS calls, secrets or credentials.
# TENANT BOUNDARY: No tenant, principal, membership, session or database records are accessed or mutated.
# AUTHORITY BOUNDARY: Test-only verification of identity assertions; no provisioning or runtime activation.
# FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains the exclusive financial execution authority.

"""Unit tests for the ECS production workload identity probe."""

from __future__ import annotations

import pytest

from tools.eos.auth import ecs_production_workload_identity_probe as probe


def test_metadata_url_requires_ecs_task_metadata_v4(monkeypatch):
    monkeypatch.delenv("ECS_CONTAINER_METADATA_URI_V4", raising=False)
    with pytest.raises(RuntimeError, match="ECS_TASK_METADATA_URI_REQUIRED"):
        probe._metadata_url()


@pytest.mark.parametrize(
    "value",
    [
        "https://169.254.170.2/v4/container",
        "http://example.com/v4/container",
        "http://169.254.170.2/v3/container",
        "http://169.254.170.2/v4/container?target=example.com",
        "http://user@169.254.170.2/v4/container",
    ],
)
def test_metadata_url_rejects_non_ecs_or_unsafe_endpoint(monkeypatch, value):
    monkeypatch.setenv("ECS_CONTAINER_METADATA_URI_V4", value)
    with pytest.raises(RuntimeError, match="ECS_TASK_METADATA_URI_INVALID"):
        probe._metadata_url()


def test_metadata_url_returns_task_endpoint(monkeypatch):
    monkeypatch.setenv(
        "ECS_CONTAINER_METADATA_URI_V4",
        "http://169.254.170.2/v4/container-id",
    )
    assert probe._metadata_url() == "http://169.254.170.2/v4/container-id/task"


def test_task_metadata_requires_expected_account_region_and_revision():
    metadata = {
        "TaskARN": (
            "arn:aws:ecs:af-south-1:121014832643:"
            "task/wilsy-eos-production/0123456789abcdef"
        ),
        "Cluster": "wilsy-eos-production",
        "Family": "wilsy-eos-production-api",
        "Revision": 1,
    }
    probe._verify_task_metadata(metadata)


@pytest.mark.parametrize(
    "field,value",
    [("Cluster", "default"), ("Family", "another-task-family"), ("Revision", 0)],
)
def test_task_metadata_rejects_unapproved_cluster_family_or_revision(field, value):
    metadata = {
        "TaskARN": (
            "arn:aws:ecs:af-south-1:121014832643:"
            "task/wilsy-eos-production/0123456789abcdef"
        ),
        "Cluster": "wilsy-eos-production",
        "Family": "wilsy-eos-production-api",
        "Revision": 1,
    }
    metadata[field] = value
    with pytest.raises(
        RuntimeError, match="ECS_PRODUCTION_TASK_DEFINITION_METADATA_REQUIRED"
    ):
        probe._verify_task_metadata(metadata)


@pytest.mark.parametrize(
    "task_arn",
    [
        "arn:aws:ecs:us-east-1:121014832643:task/cluster/task-id",
        "arn:aws:ecs:af-south-1:999999999999:task/cluster/task-id",
        "arn:aws:ecs:af-south-1:121014832643:service/cluster/service",
        "",
    ],
)
def test_task_metadata_rejects_wrong_or_non_task_arn(task_arn):
    with pytest.raises(RuntimeError, match="ECS_PRODUCTION_TASK_ARN_MISMATCH"):
        probe._verify_task_metadata(
            {"TaskARN": task_arn, "Family": "family", "Revision": 1}
        )


def test_task_metadata_requires_task_definition_identity():
    with pytest.raises(
        RuntimeError, match="ECS_PRODUCTION_TASK_DEFINITION_METADATA_REQUIRED"
    ):
        probe._verify_task_metadata(
            {
                "TaskARN": (
                    "arn:aws:ecs:af-south-1:121014832643:"
                    "task/cluster/task-id"
                ),
            }
        )


def test_sts_identity_requires_exact_production_task_role(monkeypatch):
    monkeypatch.setenv(
        "WILSY_ECS_EXPECTED_TASK_ROLE_ARN",
        "arn:aws:iam::121014832643:role/wilsy-eos-production-task-role",
    )
    probe._verify_sts_identity(
        {
            "Account": "121014832643",
            "Arn": (
                "arn:aws:sts::121014832643:assumed-role/"
                "wilsy-eos-production-task-role/0123456789abcdef"
            ),
        }
    )


@pytest.mark.parametrize(
    "arn",
    [
        "arn:aws:sts::121014832643:assumed-role/wilsy-eos-production-execution-role/session",
        "arn:aws:sts::121014832643:assumed-role/wilsy-eos-global-mfa-local-development/session",
        "arn:aws:iam::121014832643:user/wilsy-legal-cert-operator",
        "arn:aws:sts::999999999999:assumed-role/wilsy-eos-production-task-role/session",
    ],
)
def test_sts_identity_rejects_execution_local_admin_and_other_account_roles(
    monkeypatch, arn
):
    monkeypatch.setenv(
        "WILSY_ECS_EXPECTED_TASK_ROLE_ARN",
        "arn:aws:iam::121014832643:role/wilsy-eos-production-task-role",
    )
    with pytest.raises(RuntimeError, match="ECS_PRODUCTION_TASK_ROLE_IDENTITY_REQUIRED"):
        probe._verify_sts_identity({"Account": "121014832643", "Arn": arn})


def test_sts_identity_rejects_unapproved_expected_role_configuration(monkeypatch):
    monkeypatch.setenv(
        "WILSY_ECS_EXPECTED_TASK_ROLE_ARN",
        "arn:aws:iam::121014832643:role/wilsy-eos-production-execution-role",
    )
    with pytest.raises(
        RuntimeError,
        match="ECS_PRODUCTION_EXPECTED_TASK_ROLE_CONFIGURATION_INVALID",
    ):
        probe._verify_sts_identity(
            {
                "Account": "121014832643",
                "Arn": (
                    "arn:aws:sts::121014832643:assumed-role/"
                    "wilsy-eos-production-task-role/session"
                ),
            }
        )


def test_sts_identity_rejects_wrong_account(monkeypatch):
    monkeypatch.setenv(
        "WILSY_ECS_EXPECTED_TASK_ROLE_ARN",
        "arn:aws:iam::121014832643:role/wilsy-eos-production-task-role",
    )
    with pytest.raises(RuntimeError, match="ECS_PRODUCTION_AWS_ACCOUNT_MISMATCH"):
        probe._verify_sts_identity(
            {
                "Account": "999999999999",
                "Arn": (
                    "arn:aws:sts::999999999999:assumed-role/"
                    "wilsy-eos-production-task-role/session"
                ),
            }
        )


# ARTIFACT: tests/unit/test_ecs_production_workload_identity_probe.py
# VERSION: v1.0.2-ECS-PRODUCTION-MISSING-METADATA-TEST
# AUTHORITY BOUNDARY: Synthetic unit tests only; no AWS, task launch or KMS calls.
# TENANT POSTURE: No tenant, principal, membership, session or database data is accessed or changed.
# FAIL-CLOSED POSTURE: Unsafe metadata endpoints and non-production task identities must be rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
