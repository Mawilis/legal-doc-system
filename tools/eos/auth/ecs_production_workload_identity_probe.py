# TITLE: WILSY EOS Production ECS Workload Identity Probe
# VERSION: v1.0.1-ECS-PRODUCTION-CLUSTER-PIN
# AUTHORITY: Python EOS infrastructure verification; no IAM, factor or session authority.
# EPITOME: Independently verify the actual ECS task metadata identity, STS task-role identity, production account/region and task-local MFA KMS encrypt/decrypt capability.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/ecs_production_workload_identity_probe.py
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; production platform identity remains AWS ECS.
# CERTIFICATION OR UPDATE DATE: 2026-11-09
# CHANGELOG:
#   v1.0.1 pins metadata verification to the approved ECS cluster and task
#   family and requires a positive task-definition revision.
#   v1.0.0 establishes a fail-closed ECS metadata, STS role and production KMS
#   workload probe. It is an operator-invoked verifier and does not provision,
#   launch, enroll, authenticate or mutate business records.
# COMPLIANCE: AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
# SECURITY / PRIVACY POSTURE: Uses ECS task metadata and ambient short-lived credentials; emits no credentials, secret values, ciphertext or factor material.
# TENANT BOUNDARY: Synthetic KMS probe identity only; no tenant or principal records are read or mutated.
# AUTHORITY BOUNDARY: Verifies an existing task identity and cryptographic permission only; grants no IAM, MFA, membership, session or workspace authority.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains exclusive.
# FAIL-CLOSED DECLARATION: Missing ECS metadata, unexpected metadata host, account, region, task role, task ARN, key configuration or KMS access exits nonzero.

"""Verify the actual AWS ECS production task identity and MFA KMS capability.

Run only inside a controlled ECS task after separately approved provisioning
and task launch. The verifier requires ECS_CONTAINER_METADATA_URI_V4, compares
the actual STS assumed-role identity with the exact expected IAM task-role ARN,
checks the task ARN's account and region, and performs the canonical synthetic
KMS encrypt/decrypt round trip. It never accepts an administrator, execution,
local-development or developer identity as a substitute.
"""
from __future__ import annotations

import json
import os
import re
import sys
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener

from tools.eos.auth.global_principal_mfa_kms_envelope import (
    build_global_mfa_kms_envelope_from_environment,
)

EXPECTED_ACCOUNT_ID = "121014832643"
EXPECTED_REGION = "af-south-1"
EXPECTED_ROLE_NAME = "wilsy-eos-production-task-role"
EXPECTED_CLUSTER_NAME = "wilsy-eos-production"
EXPECTED_TASK_FAMILY = "wilsy-eos-production-api"
_METADATA_HOST = "169.254.170.2"


def _metadata_url() -> str:
    """Return the ECS task metadata URL after strict endpoint validation."""
    value = os.getenv("ECS_CONTAINER_METADATA_URI_V4", "").strip()
    if not value:
        raise RuntimeError("ECS_TASK_METADATA_URI_REQUIRED")
    parsed = urlsplit(value)
    if (
        parsed.scheme != "http"
        or parsed.hostname != _METADATA_HOST
        or parsed.port not in (None, 80)
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or not re.fullmatch(r"/v4/[A-Za-z0-9._-]+/?", parsed.path)
    ):
        raise RuntimeError("ECS_TASK_METADATA_URI_INVALID")
    return value.rstrip("/") + "/task"


def _read_task_metadata() -> dict[str, object]:
    """Read the task-scoped metadata endpoint without using ambient proxies."""
    request = Request(_metadata_url(), headers={"Accept": "application/json"})
    try:
        with build_opener(ProxyHandler({})).open(request, timeout=3) as response:
            if response.status != 200:
                raise RuntimeError("ECS_TASK_METADATA_HTTP_STATUS_INVALID")
            payload = json.loads(response.read(65536).decode("utf-8"))
    except (URLError, TimeoutError, UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError("ECS_TASK_METADATA_UNAVAILABLE") from error
    if not isinstance(payload, dict):
        raise RuntimeError("ECS_TASK_METADATA_INVALID")
    return payload


def _verify_task_metadata(metadata: dict[str, object]) -> None:
    """Require the task ARN to belong to the approved production account/region."""
    task_arn = metadata.get("TaskARN")
    expected_prefix = (
        f"arn:aws:ecs:{EXPECTED_REGION}:{EXPECTED_ACCOUNT_ID}:task/"
    )
    if not isinstance(task_arn, str) or not task_arn.startswith(expected_prefix):
        raise RuntimeError("ECS_PRODUCTION_TASK_ARN_MISMATCH")
    revision = metadata.get("Revision")
    if (
        metadata.get("Cluster") != EXPECTED_CLUSTER_NAME
        or metadata.get("Family") != EXPECTED_TASK_FAMILY
        or isinstance(revision, bool)
        or not (isinstance(revision, int) and revision > 0)
        and not (isinstance(revision, str) and revision.isdigit() and int(revision) > 0)
    ):
        raise RuntimeError("ECS_PRODUCTION_TASK_DEFINITION_METADATA_REQUIRED")


def _verify_sts_identity(identity: dict[str, object]) -> None:
    """Require the exact production task role, not merely the AWS account."""
    expected_role_arn = os.getenv("WILSY_ECS_EXPECTED_TASK_ROLE_ARN", "").strip()
    expected = (
        f"arn:aws:iam::{EXPECTED_ACCOUNT_ID}:role/{EXPECTED_ROLE_NAME}"
    )
    if expected_role_arn != expected:
        raise RuntimeError("ECS_PRODUCTION_EXPECTED_TASK_ROLE_CONFIGURATION_INVALID")
    arn = identity.get("Arn")
    if identity.get("Account") != EXPECTED_ACCOUNT_ID:
        raise RuntimeError("ECS_PRODUCTION_AWS_ACCOUNT_MISMATCH")
    if not isinstance(arn, str) or not re.fullmatch(
        rf"arn:aws:sts::{EXPECTED_ACCOUNT_ID}:assumed-role/"
        rf"{re.escape(EXPECTED_ROLE_NAME)}/[A-Za-z0-9+=,.@_-]+",
        arn,
    ):
        raise RuntimeError("ECS_PRODUCTION_TASK_ROLE_IDENTITY_REQUIRED")


def main() -> int:
    """Verify ECS task metadata, STS role and task-local KMS round trip."""
    try:
        if os.getenv("AWS_REGION", "").strip() != EXPECTED_REGION:
            raise RuntimeError("ECS_PRODUCTION_AWS_REGION_MISMATCH")
        metadata = _read_task_metadata()
        _verify_task_metadata(metadata)

        import boto3

        identity = boto3.client("sts", region_name=EXPECTED_REGION).get_caller_identity()
        _verify_sts_identity(identity)

        envelope = build_global_mfa_kms_envelope_from_environment()
        if envelope is None:
            raise RuntimeError("GLOBAL_MFA_KMS_PROVIDER_REQUIRED")
        if envelope.region_name != EXPECTED_REGION:
            raise RuntimeError("ECS_PRODUCTION_KMS_REGION_MISMATCH")
        key_match = re.fullmatch(
            r"arn:aws:kms:af-south-1:121014832643:key/[A-Za-z0-9-]+",
            envelope.key_id,
        )
        if key_match is None:
            raise RuntimeError("ECS_PRODUCTION_KMS_KEY_ARN_MISMATCH")
        envelope.validate_access()
    except Exception as error:
        print(
            f"ECS_PRODUCTION_WORKLOAD_IDENTITY=FAILED ({type(error).__name__})",
            file=sys.stderr,
        )
        return 1

    print("ECS_PRODUCTION_TASK_METADATA=VERIFIED")
    print("ECS_PRODUCTION_TASK_ROLE=VERIFIED")
    print("ECS_PRODUCTION_KMS_ENCRYPT_DECRYPT=PASSED")
    print("ECS_PRODUCTION_WORKLOAD_IDENTITY=VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# ARTIFACT: tools/eos/auth/ecs_production_workload_identity_probe.py
# VERSION: v1.0.1-ECS-PRODUCTION-CLUSTER-PIN
# AUTHORITY BOUNDARY: Verifies existing ECS task metadata, STS role and KMS capability only.
# TENANT POSTURE: Synthetic KMS probe only; no tenant, principal, membership or session records are changed.
# FAIL-CLOSED POSTURE: Missing or mismatched task metadata, account, region, task role or KMS capability exits nonzero.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
