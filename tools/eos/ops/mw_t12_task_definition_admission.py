"""TITLE: MW-T12 digest-pinned dormant ECS task-definition admission.
VERSION: v1.0.0-DORMANT-IMAGE-ADMISSION
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Verify immutable ECR provenance and optionally register two dormant,
         equivalent nonproduction Fargate task definitions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_task_definition_admission.py
COLLABORATION / OWNERSHIP: Reuses MW-T12 ECR budget/ownership preflight,
         existing CloudFormation resources, and later read-only ECS admission.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.0.0-DORMANT-IMAGE-ADMISSION binds exact source/image digests,
           verifies dormant cluster, role, logs and account budget, and requires
           --register for task-definition-only metadata mutation/readback.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No task role, credentials, secret refs, public
                           ingress, live tenancy, database or production change.
TENANT BOUNDARY: No real tenant data and no EOS source write.
AUTHORITY BOUNDARY: ECS task-definition metadata only; no service or task
                    activation, storage continuity or rollback certification.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

from tools.eos.ops import mw_t12_ecr_publication as source

VERSION = "v1.0.0-DORMANT-IMAGE-ADMISSION"
FAMILY = "wilsy-mwt12-eos-nonproduction"
CLUSTER = "wilsy-mwt12-nonproduction"
LOG_GROUP = "/wilsy/mwt12/nonproduction/eos"
ROLE = ("arn:aws:iam::" + source.ACCOUNT
        + ":role/wilsy-mwt12-eos-execution-nonproduction")
IMAGE_CURRENT_SOURCE = "439ec07776c44723936da68bbc01d907a8708eb7"
DIGEST_HISTORICAL = "sha256:184aaacac23aedfa75024ab47954f8c182965c83c83cc73a6f84e36264b47dc4"
DIGEST_CURRENT = "sha256:c9a55bcdc14e145dd40a0515db6b054e38bb2fd696502259b9af7d16f8ae021b"


class AdmissionError(RuntimeError):
    """A bounded non-secret denial code for the nonproduction admission gate."""


def require(condition: bool, code: str) -> None:
    """Fail closed when provenance, isolation or infrastructure is unverifiable."""
    if not condition:
        raise AdmissionError(code)


def aws(profile: str, *parts: str) -> dict:
    """Call an explicit AWS CLI operation without logging credentials or responses."""
    try:
        result = subprocess.run(
            ["aws", *parts, "--profile", profile, "--region", source.REGION,
             "--output", "json", "--no-cli-pager"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=60,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise AdmissionError("AWS_COMMAND_UNAVAILABLE") from exc
    require(result.returncode == 0 and len(result.stdout) <= 2097152,
            "AWS_OPERATION_DENIED_OR_OVERSIZED")
    try:
        value = json.loads(result.stdout)
    except (UnicodeError, ValueError) as exc:
        raise AdmissionError("AWS_RESPONSE_INVALID") from exc
    require(isinstance(value, dict), "AWS_RESPONSE_INVALID")
    return value


def no_compute(profile: str) -> None:
    """Require no services and no running or pending tasks in owned cluster."""
    require(aws(profile, "ecs", "list-services", "--cluster", CLUSTER).get(
        "serviceArns") == [], "ECS_SERVICES_PRESENT")
    for status in ("RUNNING", "PENDING"):
        require(aws(profile, "ecs", "list-tasks", "--cluster", CLUSTER,
                    "--desired-status", status).get("taskArns") == [],
                "ECS_TASKS_PRESENT")


def image_config(image: str) -> dict:
    """Read the exact manifest's runtime config via Mac-host Crane transport."""
    env = os.environ.copy()
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
                "http_proxy", "https_proxy", "all_proxy"):
        env.pop(key, None)
    try:
        result = subprocess.run(
            ["crane", "config", image], env=env, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, timeout=60, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise AdmissionError("CRANE_UNAVAILABLE") from exc
    require(result.returncode == 0 and len(result.stdout) <= 1048576,
            "IMAGE_CONFIG_UNAVAILABLE")
    try:
        value = json.loads(result.stdout)
    except (UnicodeError, ValueError) as exc:
        raise AdmissionError("IMAGE_CONFIG_INVALID") from exc
    require(isinstance(value, dict), "IMAGE_CONFIG_INVALID")
    return value


def images(profile: str, head: str) -> tuple[str, str]:
    """Verify two independent exact ECR digests and original Git provenance.

    The admission-code commit is newer than the certified runtime image;
    source identity MUST remain the image's original full SHA, not Git HEAD.
    """
    source.run(["git", "merge-base", "--is-ancestor",
                IMAGE_CURRENT_SOURCE, head],
               failure_code="PUBLISHED_IMAGE_SOURCE_NOT_ANCESTOR")
    refs = []
    for revision, expected in (
        (source.HISTORICAL, DIGEST_HISTORICAL),
        (IMAGE_CURRENT_SOURCE, DIGEST_CURRENT),
    ):
        require(source.image_digest(profile, revision) == expected,
                "IMAGE_DIGEST_DRIFT")
        image = source.URI + "@" + expected
        config = image_config(image)
        require(config.get("os") == "linux"
                and config.get("architecture") == "amd64",
                "IMAGE_PLATFORM_INVALID")
        labels = config.get("config", {}).get("Labels", {})
        require(isinstance(labels, dict)
                and labels.get(source.SOURCE_LABEL) == revision,
                "IMAGE_SOURCE_LABEL_INVALID")
        refs.append(image)
    require(refs[0] != refs[1], "IMAGES_IDENTICAL")
    return refs[0], refs[1]


def foundation(profile: str) -> None:
    """Verify exact regional role/log group and entirely dormant cluster."""
    group = aws(profile, "logs", "describe-log-groups",
                "--log-group-name-prefix", LOG_GROUP).get("logGroups", [])
    require(any(isinstance(g, dict) and g.get("logGroupName") == LOG_GROUP
                for g in group), "LOG_GROUP_MISSING")
    role = aws(profile, "iam", "get-role", "--role-name",
               "wilsy-mwt12-eos-execution-nonproduction").get("Role", {})
    require(role.get("Arn") == ROLE, "EXECUTION_ROLE_MISMATCH")
    clusters = aws(profile, "ecs", "describe-clusters", "--clusters",
                   CLUSTER, "--include", "TAGS").get("clusters", [])
    require(len(clusters) == 1 and clusters[0].get("clusterName") == CLUSTER
            and clusters[0].get("status") == "ACTIVE"
            and clusters[0].get("runningTasksCount") == 0
            and clusters[0].get("pendingTasksCount") == 0
            and clusters[0].get("activeServicesCount") == 0,
            "CLUSTER_NOT_DORMANT")
    require(any(t.get("key") == "Environment" and
                t.get("value") == "nonproduction"
                for t in clusters[0].get("tags", [])
                if isinstance(t, dict)), "CLUSTER_OWNERSHIP_INVALID")
    no_compute(profile)


def definition(image: str) -> dict:
    """Create a zero-secrets task spec with scratch-only, nonpersistent mounts.

    This task definition intentionally grants NO task IAM identity. Database
    persistence and authenticated runtime are separate, still-blocked gates.
    """
    mounts = (("app-data", "/app/data"), ("app-reports", "/app/reports"),
              ("app-logs", "/var/log/wilsy-os"), ("tmp", "/tmp"))
    return {
        "family": FAMILY,
        "executionRoleArn": ROLE,
        "networkMode": "awsvpc",
        "requiresCompatibilities": ["FARGATE"],
        "runtimePlatform": {"cpuArchitecture": "X86_64",
                            "operatingSystemFamily": "LINUX"},
        "cpu": "256", "memory": "512",
        "volumes": [{"name": name} for name, _ in mounts],
        "containerDefinitions": [{
            "name": "python-eos", "image": image, "essential": True,
            "readonlyRootFilesystem": True, "user": "10001:10001",
            "portMappings": [{"containerPort": 9095, "protocol": "tcp"}],
            "mountPoints": [{"sourceVolume": name, "containerPath": target,
                             "readOnly": False} for name, target in mounts],
            "environment": [{"name": "WILSY_ENV", "value": "nonproduction"}],
            "secrets": [],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {"awslogs-group": LOG_GROUP,
                            "awslogs-region": source.REGION,
                            "awslogs-stream-prefix": "mw-t12-eos"},
            },
            "healthCheck": {
                "command": ["CMD-SHELL",
                    "python -c 'import urllib.request; r=urllib.request.urlopen(\"http://127.0.0.1:9095/\",timeout=3); raise SystemExit(0 if r.status==200 else 1)'"],
                "interval": 30, "timeout": 5, "retries": 3,
                "startPeriod": 20,
            },
        }],
        "tags": [{"key": "Environment", "value": "nonproduction"},
                 {"key": "Project", "value": "MW-T12"}],
    }


def verify(profile: str, arn: str, expected: dict) -> int:
    """Independently reopen exact registered revision and inspect safety fields."""
    response = aws(profile, "ecs", "describe-task-definition",
                   "--task-definition", arn, "--include", "TAGS")
    task = response.get("taskDefinition", {})
    require(task.get("taskDefinitionArn") == arn
            and task.get("status") == "ACTIVE"
            and not task.get("taskRoleArn"), "TASK_IDENTITY_OR_STATUS_DRIFT")
    for key in ("family", "executionRoleArn", "networkMode", "runtimePlatform",
                "cpu", "memory"):
        require(task.get(key) == expected[key], "TASK_RUNTIME_DRIFT")
    require("FARGATE" in task.get("requiresCompatibilities", []),
            "TASK_COMPATIBILITY_DRIFT")
    actual = task.get("containerDefinitions", [])
    require(isinstance(actual, list) and len(actual) == 1,
            "TASK_CONTAINER_COUNT_DRIFT")
    wanted = expected["containerDefinitions"][0]
    for key in ("name", "image", "essential", "readonlyRootFilesystem",
                "user", "portMappings", "mountPoints", "environment",
                "logConfiguration", "healthCheck"):
        require(actual[0].get(key) == wanted[key],
                "TASK_CONTAINER_CONTRACT_DRIFT")
    require(not actual[0].get("secrets"), "TASK_SECRETS_UNEXPECTED")
    volumes = task.get("volumes", [])
    require([v.get("name") for v in volumes]
            == [v["name"] for v in expected["volumes"]]
            and all(not v.get("efsVolumeConfiguration")
                    and not v.get("dockerVolumeConfiguration")
                    and not v.get("host") for v in volumes),
            "TASK_STORAGE_DRIFT")
    tags = response.get("tags", [])
    require(all(tag in tags for tag in expected["tags"]),
            "TASK_TAG_DRIFT")
    revision = task.get("revision")
    require(type(revision) is int and revision > 0,
            "TASK_REVISION_INVALID")
    return revision


def run(profile: str, register: bool) -> None:
    """Read-only admission by default; explicit registration creates no compute."""
    head = source.preflight(profile)
    foundation(profile)
    historical, current = images(profile, head)
    print("MW_T12_TASK_DEFINITION_PREFLIGHT=PASS", flush=True)
    print("MW_T12_TWO_IMMUTABLE_IMAGES=VERIFIED", flush=True)
    print("MW_T12_FARGATE_COMPUTE=ZERO", flush=True)
    registered = aws(profile, "ecs", "list-task-definitions",
                     "--family-prefix", FAMILY, "--status", "ACTIVE").get(
                         "taskDefinitionArns")
    require(isinstance(registered, list), "TASK_LIST_INVALID")
    if not register:
        print("MW_T12_REGISTRATION_EXECUTED=FALSE", flush=True)
        print("MW_T12_ACTIVE_TASK_REVISIONS=" + str(len(registered)), flush=True)
        return
    require(registered == [], "EXISTING_REVISIONS_REQUIRE_RECONCILIATION")
    for label, image in (("HISTORICAL", historical), ("CURRENT", current)):
        require(source.git("status", "--porcelain") == ""
                and source.git("rev-parse", "HEAD") == head,
                "GIT_SOURCE_CHANGED")
        no_compute(profile)
        spec = definition(image)
        with tempfile.TemporaryDirectory(prefix="wilsy-mwt12-task-") as tmp:
            file = Path(tmp) / "task.json"
            file.write_text(json.dumps(spec, sort_keys=True), encoding="utf-8")
            result = aws(profile, "ecs", "register-task-definition",
                         "--cli-input-json", "file://" + str(file))
        task = result.get("taskDefinition", {})
        arn = task.get("taskDefinitionArn")
        require(isinstance(arn, str) and arn.startswith(
            "arn:aws:ecs:" + source.REGION + ":" + source.ACCOUNT
            + ":task-definition/" + FAMILY + ":"),
            "TASK_REGISTRATION_RESPONSE_INVALID")
        revision = verify(profile, arn, spec)
        print("MW_T12_" + label + "_TASK_ARN=" + arn, flush=True)
        print("MW_T12_" + label + "_TASK_REVISION="
              + str(revision), flush=True)
    no_compute(profile)
    print("MW_T12_REGISTERED_REVISIONS=2", flush=True)
    print("MW_T12_FARGATE_COMPUTE=ZERO", flush=True)
    print("MW_T12_ROLLBACK_CERTIFIED=FALSE", flush=True)


def main(argv: list[str] | None = None) -> int:
    """Expose explicitly opted-in ECS metadata registration only."""
    parser = argparse.ArgumentParser(description="MW-T12 dormant ECS admission")
    parser.add_argument("--profile", default="wilsy-legal-cert")
    parser.add_argument("--register", action="store_true")
    args = parser.parse_args(argv)
    try:
        run(args.profile, args.register)
        return 0
    except (AdmissionError, source.PublicationError, KeyboardInterrupt) as exc:
        code = str(exc) if not isinstance(exc, KeyboardInterrupt) else "INTERRUPTED"
        print("MW_T12_TASK_ADMISSION=FAIL_CLOSED", flush=True)
        print("MW_T12_ERROR=" + code, flush=True)
        print("MW_T12_ROLLBACK_CERTIFIED=FALSE", flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

# ARTIFACT: tools/eos/ops/mw_t12_task_definition_admission.py
# VERSION: v1.0.0-DORMANT-IMAGE-ADMISSION
# AUTHORITY BOUNDARY: Exact owned ECS task metadata; no running services/tasks.
# TENANT POSTURE: No business records or tenant runtime authorized.
# FAIL-CLOSED POSTURE: Unknown image, budget, task identity or compute denies.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
