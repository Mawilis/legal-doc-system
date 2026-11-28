"""TITLE: MW-T12 read-only ECS Fargate rollback admission.
VERSION: v1.0.0-ECS-NONPRODUCTION-ADMISSION
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Validate nonproduction ownership, immutable image revisions, service
         health, and unchanged storage/authority configuration before recovery.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_ecs_admission.py
COLLABORATION / OWNERSHIP: Builds on MW-T12 local Docker image certificate;
         AWS ECS/STS reads only, no new business truth or deployment commands.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.0.0-ECS-NONPRODUCTION-ADMISSION introduces explicit account,
           cluster, service and historical task ARN admission. Rejects
           production tags, mutable images, drifted task runtime/storage
           authority, non-Fargate or unstable services and missing rollback
           circuit breaker. Emits bounded evidence and no credentials.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Shell-free AWS CLI read commands; response size
         bounded, secrets, AWS outputs and resource IDs never printed.
TENANT BOUNDARY: No tenant or data access; nonproduction resources only.
AUTHORITY BOUNDARY: Admission is read-only, not ECS rollback certification.
FINANCIAL AUTHORITY BOUNDARY: No spending, grants or Kennel execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess

VERSION = "v1.0.0-ECS-NONPRODUCTION-ADMISSION"
ARN = re.compile(r"arn:aws[a-z-]*:ecs:([a-z0-9-]+):(\d{12}):(cluster|service|task-definition)/([^\s]+)\Z")
PIN = re.compile(r"(\d{12})\.dkr\.ecr\.([a-z0-9-]+)\.amazonaws\.com/[^\s@]+@sha256:[0-9a-f]{64}\Z")
REGION = re.compile(r"[a-z]{2}(?:-gov)?-[a-z]+-\d\Z")
NONPROD = frozenset({"nonproduction", "non-production", "staging", "test", "testing", "sandbox"})


class AdmissionError(RuntimeError):
    """Stable non-secret error code at the nonproduction admission boundary."""


def _require(condition: bool, code: str) -> None:
    """Reject missing proofs with bounded error codes, never cloud payloads."""
    if not condition:
        raise AdmissionError(code)


def _aws(parts: list[str], region: str, profile: str | None) -> dict:
    """Read AWS control-plane data; never invoke a mutating API or shell."""
    cmd = ["aws", *parts, "--region", region, "--output", "json", "--no-cli-pager"]
    if profile:
        cmd += ["--profile", profile]
    try:
        result = subprocess.run(cmd, capture_output=True, check=False, timeout=30)
    except (OSError, subprocess.SubprocessError) as error:
        raise AdmissionError("ECS_READ_UNAVAILABLE") from error
    _require(result.returncode == 0, "ECS_READ_DENIED")
    _require(len(result.stdout) <= 1048576, "ECS_READ_OVERSIZED")
    try:
        data = json.loads(result.stdout)
    except (UnicodeError, ValueError) as error:
        raise AdmissionError("ECS_READ_INVALID") from error
    _require(isinstance(data, dict), "ECS_READ_INVALID")
    return data


def _arn(value: str, kind: str, region: str, account: str) -> str:
    """Enforce explicitly selected ARN, resource type, account and region."""
    match = ARN.fullmatch(value)
    _require(match is not None, "ECS_FULL_ARN_REQUIRED")
    assert match is not None
    _require(match.group(1) == region and match.group(2) == account,
             "ECS_ACCOUNT_REGION_MISMATCH")
    _require(match.group(3) == kind, "ECS_RESOURCE_KIND_INVALID")
    return match.group(4)


def _tagged_nonproduction(resource: str, region: str, profile: str | None) -> None:
    """Require one explicit staging/nonproduction environment tag per resource."""
    tags = _aws(["ecs", "list-tags-for-resource", "--resource-arn", resource],
                region, profile).get("tags")
    _require(isinstance(tags, list), "ECS_ENVIRONMENT_TAG_MISSING")
    values = [t["value"].strip().lower() for t in tags if isinstance(t, dict)
              and t.get("key", "").strip().lower()
              in {"environment", "stage", "wilsy:environment"}
              and isinstance(t.get("value"), str)]
    _require(len(values) == 1 and values[0] in NONPROD,
             "ECS_NONPRODUCTION_TAG_REQUIRED")


def _task(reference: str, region: str, account: str,
          profile: str | None) -> dict:
    """Require a live Fargate revision whose only EOS image uses ECR digest."""
    _arn(reference, "task-definition", region, account)
    task = _aws(["ecs", "describe-task-definition", "--task-definition", reference],
                region, profile).get("taskDefinition")
    _require(isinstance(task, dict), "ECS_TASK_MISSING")
    _require(task.get("taskDefinitionArn") == reference
             and task.get("status") == "ACTIVE", "ECS_TASK_INVALID")
    _require(task.get("networkMode") == "awsvpc"
             and "FARGATE" in task.get("requiresCompatibilities", []),
             "ECS_FARGATE_TASK_REQUIRED")
    containers = task.get("containerDefinitions")
    _require(isinstance(containers, list) and len(containers) == 1
             and isinstance(containers[0], dict), "ECS_SINGLE_CONTAINER_REQUIRED")
    image = containers[0].get("image")
    match = PIN.fullmatch(image) if isinstance(image, str) else None
    _require(match is not None, "ECS_IMAGE_DIGEST_REQUIRED")
    assert match is not None
    _require(match.group(1) == account and match.group(2) == region,
             "ECS_REGISTRY_BOUNDARY_INVALID")
    _require(isinstance(task.get("revision"), int) and task["revision"] > 0
             and isinstance(task.get("family"), str), "ECS_TASK_REVISION_INVALID")
    return task


def _contract(task: dict) -> str:
    """Fingerprint unchanged task storage, IAM, secret and runtime semantics.

    Excludes only image identity, task revision and AWS registration metadata;
    EFS volumes, IAM roles, environment, secret references, ports and CPU/memory
    are included. Digest is evidence comparison, not secret confidentiality.
    """
    excluded = {"taskDefinitionArn", "revision", "status", "registeredAt",
                "registeredBy", "deregisteredAt", "requiresAttributes",
                "compatibilities", "tags"}
    spec = {k: v for k, v in task.items() if k not in excluded}
    spec["containerDefinitions"] = [
        {k: v for k, v in c.items() if k != "image"}
        for c in task["containerDefinitions"]
    ]
    raw = json.dumps(spec, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


def admit(cluster: str, service: str, historical: str,
          region: str, account: str, profile: str | None) -> None:
    """Admit only stable nonproduction Fargate with verified older image.

    Does not register revisions, update services, create images, read business
    records or certify recovery time. All readbacks are independent ECS reads.
    """
    _require(REGION.fullmatch(region) is not None, "ECS_REGION_INVALID")
    _require(re.fullmatch(r"\d{12}", account) is not None, "ECS_ACCOUNT_INVALID")
    cluster_name = _arn(cluster, "cluster", region, account)
    service_path = _arn(service, "service", region, account)
    _require(service_path.count("/") == 1
             and service_path.split("/")[0] == cluster_name,
             "ECS_CLUSTER_SERVICE_MISMATCH")
    _arn(historical, "task-definition", region, account)
    caller = _aws(["sts", "get-caller-identity"], region, profile)
    _require(caller.get("Account") == account, "ECS_CALLER_ACCOUNT_MISMATCH")
    _tagged_nonproduction(cluster, region, profile)
    _tagged_nonproduction(service, region, profile)
    result = _aws(["ecs", "describe-services", "--cluster", cluster,
                   "--services", service], region, profile)
    services = result.get("services")
    _require(isinstance(services, list) and len(services) == 1,
             "ECS_SERVICE_MISSING")
    entry = services[0]
    _require(entry.get("serviceArn") == service and entry.get("status") == "ACTIVE",
             "ECS_SERVICE_INVALID")
    _require(entry.get("launchType") == "FARGATE"
             or any(p.get("capacityProvider") == "FARGATE"
                    for p in entry.get("capacityProviderStrategy", [])
                    if isinstance(p, dict)), "ECS_FARGATE_SERVICE_REQUIRED")
    deployment = entry.get("deploymentConfiguration") or {}
    breaker = deployment.get("deploymentCircuitBreaker") or {}
    _require(entry.get("deploymentController", {}).get("type", "ECS") == "ECS"
             and deployment.get("strategy", "ROLLING") == "ROLLING"
             and breaker.get("enable") is True
             and breaker.get("rollback") is True,
             "ECS_ROLLBACK_PROTECTION_REQUIRED")
    desired = entry.get("desiredCount")
    deploys = entry.get("deployments")
    _require(isinstance(desired, int) and desired > 0
             and entry.get("runningCount") == desired
             and entry.get("pendingCount") == 0
             and isinstance(deploys, list) and len(deploys) == 1
             and deploys[0].get("rolloutState") == "COMPLETED",
             "ECS_SERVICE_NOT_STABLE")
    current_arn = entry.get("taskDefinition")
    _require(isinstance(current_arn, str), "ECS_CURRENT_TASK_MISSING")
    current = _task(current_arn, region, account, profile)
    previous = _task(historical, region, account, profile)
    _require(current["family"] == previous["family"]
             and current["revision"] > previous["revision"],
             "ECS_HISTORICAL_REVISION_INVALID")
    _require(current["containerDefinitions"][0]["image"]
             != previous["containerDefinitions"][0]["image"],
             "ECS_IMAGES_NOT_DISTINCT")
    digest = _contract(current)
    _require(digest == _contract(previous), "ECS_STORAGE_AUTHORITY_DRIFT")
    print("MW_T12_ECS_NONPRODUCTION_OWNERSHIP=PASS")
    print("MW_T12_ECS_FARGATE_BASELINE=STABLE")
    print("MW_T12_ECS_TASK_DIGESTS=PINNED")
    print("MW_T12_ECS_TASK_REVISION_ORDER=PASS")
    print("MW_T12_ECS_STORAGE_AUTHORITY_HASH=" + digest)
    print("MW_T12_ECS_ADMISSION=PASS_READ_ONLY")
    print("MW_T12_ECS_ROLLBACK_EXECUTED=FALSE")
    print("MW_T12_ECS_RECOVERY_CERTIFIED=FALSE")


def main(argv: list[str] | None = None) -> int:
    """Require explicit resources, never discover or choose production targets."""
    parser = argparse.ArgumentParser(description="MW-T12 ECS read-only admission")
    parser.add_argument("--cluster-arn", required=True)
    parser.add_argument("--service-arn", required=True)
    parser.add_argument("--historical-task-arn", required=True)
    parser.add_argument("--account-id", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--profile")
    args = parser.parse_args(argv)
    try:
        admit(args.cluster_arn, args.service_arn, args.historical_task_arn,
              args.region, args.account_id, args.profile)
        return 0
    except (AdmissionError, KeyboardInterrupt) as error:
        code = str(error) if isinstance(error, AdmissionError) else "OPERATOR_INTERRUPTED"
        print("MW_T12_ECS_ADMISSION=FAIL_CLOSED")
        print("MW_T12_ERROR=" + code)
        print("MW_T12_ECS_ROLLBACK_EXECUTED=FALSE")
        print("MW_T12_ECS_RECOVERY_CERTIFIED=FALSE")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


# ARTIFACT: tools/eos/ops/mw_t12_ecs_admission.py
# VERSION: v1.0.0-ECS-NONPRODUCTION-ADMISSION
# AUTHORITY BOUNDARY: Read-only Fargate source/digest/storage admission.
# TENANT POSTURE: No tenant or business data touched.
# FAIL-CLOSED POSTURE: Unknown ownership, drift or readiness denies.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
