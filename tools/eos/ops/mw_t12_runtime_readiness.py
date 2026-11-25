"""TITLE: MW-T12 ECS nonproduction runtime readiness and cost admission.
VERSION: v1.0.1-CLOUDFORMATION-SECURITY-GROUP-BINDING
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Inspect two digest-pinned registered Fargate tasks and their exact
         network, storage, identity and cost gates without launching compute.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_runtime_readiness.py
COLLABORATION / OWNERSHIP: Existing AWS MW-T12 ECR preflight, dormant task
         definitions, CloudFormation foundation and ECS read-only admission.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.0.1-CLOUDFORMATION-SECURITY-GROUP-BINDING looks up the
           CloudFormation-owned group ID rather than assuming a group name.
CHANGELOG: v1.0.0-READ-ONLY-RUNTIME-BLOCKERS validates the recorded AWS
           image identities, both task revisions, zero compute, networking,
           persistent storage and independent verification prerequisites.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: AWS CLI read only; no token, URI, secret or task
                           payload printed; no raw error body disclosed.
TENANT BOUNDARY: No real tenant data or EOS business source writes.
AUTHORITY BOUNDARY: Never starts/stops task, service or deploy; no approval,
                    production readiness or rollback result is inferred.
FINANCIAL AUTHORITY BOUNDARY: No paid compute activated; Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
import sys

from tools.eos.ops import mw_t12_ecr_publication as published
from tools.eos.ops import mw_t12_task_definition_admission as registered

VERSION = "v1.0.1-CLOUDFORMATION-SECURITY-GROUP-BINDING"
REVISIONS = (1, 2)
TASK_FAMILY = "wilsy-mwt12-eos-nonproduction"


class ReadinessError(RuntimeError):
    """Bounded, secret-free denial with no cloud state mutation."""


def require(value: bool, code: str) -> None:
    """Deny ambiguous infrastructure, ownership or source evidence."""
    if not value:
        raise ReadinessError(code)


def task(profile: str, revision: int) -> dict:
    """Independently read the precise owned ECS task revision."""
    response = registered.aws(
        profile, "ecs", "describe-task-definition", "--task-definition",
        TASK_FAMILY + ":" + str(revision), "--include", "TAGS",
    )
    definition = response.get("taskDefinition", {})
    require(isinstance(definition, dict)
            and definition.get("revision") == revision
            and definition.get("family") == TASK_FAMILY
            and definition.get("status") == "ACTIVE",
            "EXACT_TASK_REVISION_UNVERIFIED")
    require(any(t.get("key") == "Environment"
                and t.get("value") == "nonproduction"
                for t in response.get("tags", []) if isinstance(t, dict)),
            "TASK_ENVIRONMENT_OWNERSHIP_INVALID")
    return definition


def check(profile: str) -> tuple[str, ...]:
    """Read exact budget, image, task, network and recovery prerequisites.

    Returns stable blocker codes. No AWS mutation, service start, task start,
    database access, secrets readback or production identity is possible.
    """
    head = published.preflight(profile)
    registered.foundation(profile)
    images = registered.images(profile, head)
    tasks = [task(profile, revision) for revision in REVISIONS]
    expected_images = list(images)
    blockers: list[str] = []
    for index, definition in enumerate(tasks):
        require(definition.get("runtimePlatform") == {
            "cpuArchitecture": "X86_64", "operatingSystemFamily": "LINUX",
        }, "TASK_PLATFORM_DRIFT")
        require(definition.get("cpu") == "256"
                and definition.get("memory") == "512",
                "TASK_COMPUTE_PROFILE_DRIFT")
        require(definition.get("networkMode") == "awsvpc"
                and "FARGATE" in definition.get("requiresCompatibilities", []),
                "TASK_NETWORK_COMPATIBILITY_DRIFT")
        containers = definition.get("containerDefinitions", [])
        require(isinstance(containers, list) and len(containers) == 1
                and containers[0].get("image") == expected_images[index],
                "TASK_IMAGE_IDENTITY_DRIFT")
        require(definition.get("executionRoleArn") == registered.ROLE,
                "TASK_EXECUTION_ROLE_DRIFT")
        require(not definition.get("taskRoleArn"), "TASK_ROLE_UNEXPECTED")
        require(not containers[0].get("secrets"), "TASK_SECRETS_UNEXPECTED")
        require(containers[0].get("readonlyRootFilesystem") is True,
                "TASK_ROOT_WRITABLE")
        require(containers[0].get("user") == "10001:10001",
                "TASK_USER_DRIFT")
        mounts = containers[0].get("mountPoints", [])
        volumes = definition.get("volumes", [])
        require(len(mounts) == 4 and len(volumes) == 4,
                "TASK_MOUNT_CONTRACT_DRIFT")
        require(all(v.get("name") in {m.get("sourceVolume") for m in mounts}
                    and not v.get("efsVolumeConfiguration")
                    for v in volumes), "TASK_STORAGE_CONTRACT_DRIFT")
        # These four mounts are deliberately task-local scratch. Their contents
        # DO NOT survive stop/rollback; this cannot prove persistent recovery.
        if "PERSISTENT_RECOVERY_STORAGE_NOT_VERIFIED" not in blockers:
            blockers.append("PERSISTENT_RECOVERY_STORAGE_NOT_VERIFIED")
        if "AUTHENTICATED_DATABASE_SOURCE_NOT_CONFIGURED" not in blockers:
            blockers.append("AUTHENTICATED_DATABASE_SOURCE_NOT_CONFIGURED")
    require(tasks[0].get("revision") < tasks[1].get("revision"),
            "TASK_REVISION_ORDER_INVALID")
    require(tasks[0].get("family") == tasks[1].get("family"),
            "TASK_FAMILY_DRIFT")
    # The only existing security group has no ingress, by foundation design.
    stacks = registered.aws(
        profile, "cloudformation", "describe-stacks",
        "--stack-name", published.STACK,
    ).get("Stacks", [])
    require(isinstance(stacks, list) and len(stacks) == 1,
            "FOUNDATION_STACK_NOT_VERIFIED")
    outputs = stacks[0].get("Outputs", [])
    matched = [x.get("OutputValue") for x in outputs
               if isinstance(x, dict) and x.get("OutputKey") == "ClosedSecurityGroup"]
    require(len(matched) == 1 and isinstance(matched[0], str)
            and matched[0].startswith("sg-"),
            "FOUNDATION_SECURITY_GROUP_OUTPUT_INVALID")
    groups = registered.aws(
        profile, "ec2", "describe-security-groups",
        "--group-ids", matched[0],
    ).get("SecurityGroups", [])
    require(isinstance(groups, list) and len(groups) == 1
            and groups[0].get("GroupId") == matched[0]
            and groups[0].get("VpcId") == "vpc-05a3c2c855c4dde26",
            "EXACT_SECURITY_GROUP_UNVERIFIED")
    require(groups[0].get("IpPermissions") == [],
            "SECURITY_GROUP_UNEXPECTED_INGRESS")
    rules = groups[0].get("IpPermissionsEgress", [])
    require(len(rules) == 1 and rules[0].get("IpProtocol") == "tcp"
            and rules[0].get("FromPort") == 443
            and rules[0].get("ToPort") == 443,
            "SECURITY_GROUP_EGRESS_DRIFT")
    blockers.append("INDEPENDENT_AUTHENTICATED_HTTP_READBACK_UNAVAILABLE")
    # ECR / CloudWatch logs require private endpoints, NAT, or public egress.
    # Nothing here authorizes a publicly exposed application endpoint.
    blockers.append("TASK_EGRESS_TO_ECR_AND_LOGS_NOT_CERTIFIED")
    registered.no_compute(profile)
    return tuple(blockers)


def main(argv: list[str] | None = None) -> int:
    """Report verified registration separately from blocked runtime readiness."""
    parser = argparse.ArgumentParser(description="MW-T12 read-only runtime gate")
    parser.add_argument("--profile", default="wilsy-legal-cert")
    args = parser.parse_args(argv)
    try:
        blockers = check(args.profile)
        print("MW_T12_RUNTIME_METADATA=VERIFIED")
        print("MW_T12_TASK_REVISIONS=1,2")
        print("MW_T12_RUNNING_TASKS=ZERO")
        for code in blockers:
            print("MW_T12_RUNTIME_BLOCKER=" + code)
        print("MW_T12_RUNTIME_RECOVERY_READY=FALSE")
        print("MW_T12_COMPUTE_LAUNCHED=FALSE")
        print("MW_T12_PRODUCTION_AUTHORIZED=FALSE")
        return 2
    except (ReadinessError, registered.AdmissionError,
            published.PublicationError, KeyboardInterrupt) as error:
        code = ("OPERATOR_INTERRUPTED" if isinstance(error, KeyboardInterrupt)
                else str(error))
        print("MW_T12_RUNTIME_GATE=FAIL_CLOSED")
        print("MW_T12_ERROR=" + code)
        print("MW_T12_COMPUTE_LAUNCHED=FALSE")
        print("MW_T12_PRODUCTION_AUTHORIZED=FALSE")
        return 2


if __name__ == "__main__":
    sys.exit(main())

# ARTIFACT: tools/eos/ops/mw_t12_runtime_readiness.py
# VERSION: v1.0.1-CLOUDFORMATION-SECURITY-GROUP-BINDING
# AUTHORITY BOUNDARY: ECS/AWS read-only; no compute or recovery claims.
# TENANT POSTURE: No real tenant, IAM grant, source write or credential.
# FAIL-CLOSED POSTURE: Missing registration or recovery evidence denies.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
