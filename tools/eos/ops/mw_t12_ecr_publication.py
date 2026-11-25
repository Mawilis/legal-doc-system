"""TITLE: MW-T12 digest-pinned EOS image ECR publication.
VERSION: v1.0.2-SOURCE-KEY-MATERIAL-GUARD
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Stage two exact Git revisions, build the existing Python EOS image
         locally and publish only digest-verifiable nonproduction ECR artifacts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_ecr_publication.py
COLLABORATION / OWNERSHIP: Reuses infra/docker/Dockerfile.eos, its dedicated
         build-context policy, the existing MW-T12 rollback source identities,
         the CloudFormation-owned ECR repository and account budget.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.0.2-SOURCE-KEY-MATERIAL-GUARD rejects plaintext PEM private-key material and
           AWS long-lived access-key identifiers in tracked archive files
           before local Docker build or any ECR image publication.
CHANGELOG: v1.0.1-ACCOUNT-BUDGET-AND-TAG-READBACK enforces account-wide Budgets endpoint,
           verifies existing ECR tags without conflating access-denied with
           absence, and requires known monthly budget notifications.
CHANGELOG: v1.0.0-COST-GATED-ECR-IMAGE-PROVENANCE establishes deterministic
           Git source staging, approved budget admission, no-ECS-write
           publication, verified ECR immutable manifest digests and no secrets.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No AWS keys embedded; login password via stdin;
         no Docker daemon exposure to ECS; no raw subprocess error disclosure.
TENANT BOUNDARY: No tenant records or remote database operations.
AUTHORITY BOUNDARY: ECR publication only; no task definition, service,
         rollout, infrastructure mutation, production or rollback certification.
FINANCIAL AUTHORITY BOUNDARY: Registry storage can incur charges. No payment
         or spending-cap guarantees; Kennel EOS retains financial authority.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import tempfile

VERSION = "v1.0.2-SOURCE-KEY-MATERIAL-GUARD"
ACCOUNT = "121014832643"
REGION = "af-south-1"
REPO = "wilsy/mwt12-eos-nonproduction"
STACK = "wilsy-mwt12-nonproduction-foundation"
BUDGET = "wilsy-mwt12-nonproduction-warning-121014832643"
REGISTRY = ACCOUNT + ".dkr.ecr." + REGION + ".amazonaws.com"
URI = REGISTRY + "/" + REPO
HISTORICAL = "fccd617c80c0d85e3c2a38a2c523ddbe4c65d566"
SHA = re.compile(r"[0-9a-f]{40}\Z")
DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
CONTEXT = ("requirements.txt", "tools", "infra/docker/Dockerfile.eos",
           "infra/docker/Dockerfile.eos.dockerignore")
SOURCE_LABEL = "wilsy.mwt12.source_sha"
DENIED_PARTS = frozenset({".env", ".aws", ".ssh", ".git", "__pycache__",
                         ".venv", "node_modules"})
DENIED_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".jks", ".env", ".sqlite",
                   ".db", ".kdbx", ".asc")


class PublicationError(RuntimeError):
    """Non-secret, bounded ECR publication failure code; no AWS mutation retry."""


def require(ok: bool, code: str) -> None:
    """Fail closed before any further registry writes or runtime action."""
    if not ok:
        raise PublicationError(code)


def run(command: list[str], *, cwd: Path | None = None,
        input_bytes: bytes | None = None, timeout: int = 90,
        capture: bool = True) -> bytes:
    """Run without shell, bounded output, and no accidental credential logs."""
    try:
        p = subprocess.run(command, cwd=cwd, input=input_bytes,
                           stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=timeout,
                           check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise PublicationError("COMMAND_UNAVAILABLE") from exc
    require(p.returncode == 0, "COMMAND_FAILED_" + command[0].upper())
    data = p.stdout or b""
    require(len(data) <= 4194304, "COMMAND_OUTPUT_OVERSIZED")
    return data


def aws(*args: str, profile: str) -> dict:
    """Read only declared AWS authority, never return credentials to stdout."""
    endpoint = "us-east-1" if args[0] == "budgets" else REGION
    result = run(["aws", *args, "--profile", profile, "--region", endpoint,
                  "--output", "json", "--no-cli-pager"])
    try:
        value = json.loads(result)
    except (UnicodeError, ValueError) as exc:
        raise PublicationError("AWS_RESPONSE_INVALID") from exc
    require(isinstance(value, dict), "AWS_RESPONSE_INVALID")
    return value


def git(*args: str) -> str:
    """Read Git source metadata; no working-tree mutation."""
    return run(["git", *args]).decode("ascii").strip()


def preflight(profile: str) -> str:
    """Verify source, account, account-wide budget and dormant ECR authority."""
    require(git("status", "--porcelain") == "", "SOURCE_WORKTREE_DIRTY")
    current = git("rev-parse", "HEAD")
    require(SHA.fullmatch(current) is not None, "SOURCE_SHA_INVALID")
    require(current != HISTORICAL, "SOURCE_REVISIONS_IDENTICAL")
    run(["git", "merge-base", "--is-ancestor", HISTORICAL, current])
    require(aws("sts", "get-caller-identity", profile=profile).get("Account")
            == ACCOUNT, "AWS_ACCOUNT_MISMATCH")
    budget = aws("budgets", "describe-budget", "--account-id", ACCOUNT,
                 "--budget-name", BUDGET, profile=profile).get("Budget", {})
    try:
        cap = Decimal(str(budget["BudgetLimit"]["Amount"]))
        actual = Decimal(str(budget["CalculatedSpend"]["ActualSpend"]["Amount"]))
        forecast = budget.get("CalculatedSpend", {}).get("ForecastedSpend")
        projected = (Decimal(str(forecast["Amount"])) if forecast is not None
                     else None)
    except (KeyError, TypeError, InvalidOperation) as exc:
        raise PublicationError("BUDGET_CURRENT_SPEND_UNVERIFIED") from exc
    require(budget.get("BudgetType") == "COST"
            and budget["BudgetLimit"].get("Unit") == "USD"
            and cap == Decimal("5"), "BUDGET_NOT_APPROVED")
    require(actual >= 0 and actual < Decimal("2")
            and (projected is None or projected < cap),
            "BUDGET_PUBLICATION_HEADROOM_INSUFFICIENT")
    notifications = aws("budgets", "describe-notifications-for-budget",
                        "--account-id", ACCOUNT, "--budget-name", BUDGET,
                        profile=profile).get("Notifications", [])
    expected = {("ACTUAL", Decimal("50")), ("ACTUAL", Decimal("80")),
                ("FORECASTED", Decimal("100"))}
    try:
        present = {(x["NotificationType"], Decimal(str(x["Threshold"])))
                   for x in notifications}
    except (KeyError, TypeError, InvalidOperation) as exc:
        raise PublicationError("BUDGET_NOTIFICATIONS_UNVERIFIED") from exc
    require(present == expected, "BUDGET_NOTIFICATIONS_UNVERIFIED")
    state = aws("cloudformation", "describe-stacks", "--stack-name", STACK,
                profile=profile).get("Stacks", [])
    require(len(state) == 1 and state[0].get("StackStatus")
            in {"CREATE_COMPLETE", "UPDATE_COMPLETE"},
            "FOUNDATION_NOT_VERIFIED")
    repo = aws("ecr", "describe-repositories", "--repository-names", REPO,
               profile=profile).get("repositories", [])
    require(len(repo) == 1 and repo[0].get("repositoryUri") == URI
            and repo[0].get("imageTagMutability") == "IMMUTABLE"
            and repo[0].get("encryptionConfiguration", {}).get("encryptionType")
            == "AES256", "ECR_REPOSITORY_AUTHORITY_INVALID")
    services = aws("ecs", "list-services", "--cluster",
                   "wilsy-mwt12-nonproduction", profile=profile)
    tasks = aws("ecs", "list-tasks", "--cluster",
                "wilsy-mwt12-nonproduction", profile=profile)
    require(services.get("serviceArns") == [] and tasks.get("taskArns") == [],
            "ECS_RUNTIME_NOT_DORMANT")
    return current


def stage_revision(revision: str, directory: Path) -> None:
    """Copy only tracked Git objects; reject symlinks and credential-like paths.

    Git archive excludes untracked local files. The Dockerfile-specific
    deny-by-default context filter remains the canonical layer admission.
    This path-name guard is not a complete secret-content scanner.
    """
    require(SHA.fullmatch(revision) is not None, "SOURCE_SHA_INVALID")
    archive = directory / "source.tar"
    with archive.open("wb") as output:
        try:
            result = subprocess.run(["git", "archive", "--format=tar", revision,
                                     *CONTEXT], stdout=output,
                                    stderr=subprocess.DEVNULL,
                                    check=False, timeout=90)
        except (OSError, subprocess.SubprocessError) as exc:
            raise PublicationError("SOURCE_ARCHIVE_UNAVAILABLE") from exc
    require(result.returncode == 0 and archive.stat().st_size < 268435456,
            "SOURCE_ARCHIVE_INVALID")
    root = directory / "context"
    root.mkdir()
    with tarfile.open(archive, "r:") as stream:
        for entry in stream:
            path = PurePosixPath(entry.name)
            require(not path.is_absolute() and ".." not in path.parts
                    and entry.name != "" and
                    (entry.isdir() or entry.isfile()),
                    "SOURCE_UNSAFE_ARCHIVE_MEMBER")
            require(not (set(path.parts) & DENIED_PARTS)
                    and not path.name.lower().endswith(DENIED_SUFFIXES),
                    "SOURCE_CREDENTIAL_PATH_DENIED")
            destination = root.joinpath(*path.parts)
            if entry.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                require(entry.size <= 16777216, "SOURCE_FILE_OVERSIZED")
                destination.parent.mkdir(parents=True, exist_ok=True)
                content = stream.extractfile(entry)
                require(content is not None, "SOURCE_ARCHIVE_FILE_INVALID")
                data = content.read()
                require(not re.search(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----", data)
                        and not re.search(rb"(?<![A-Z0-9])AKIA[0-9A-Z]{16}(?![A-Z0-9])", data),
                        "SOURCE_PLAINTEXT_SECRET_INDICATOR")
                destination.write_bytes(data)
    archive.unlink()
    dockerfile = root / "infra/docker/Dockerfile.eos"
    policy = root / "infra/docker/Dockerfile.eos.dockerignore"
    require(dockerfile.is_file() and policy.is_file()
            and (root / "requirements.txt").is_file()
            and (root / "tools/eos/api/server.py").is_file(),
            "SOURCE_PYTHON_EOS_INCOMPLETE")
    ignore = policy.read_text(encoding="utf-8")
    require(all(x in ignore.splitlines()
                for x in ("**", "!infra/docker/Dockerfile.eos",
                          "!infra/docker/Dockerfile.eos.dockerignore",
                          "!requirements.txt", "!tools/", "!tools/**")),
            "SOURCE_CONTEXT_ALLOWLIST_MISSING")
    content = dockerfile.read_text(encoding="utf-8")
    require("FROM python:3.12-slim" in content
            and "USER 10001:10001" in content
            and "tools.eos.api.server:app" in content
            and "EXPOSE 9095" in content,
            "SOURCE_RUNTIME_CONTRACT_INVALID")


def image_digest(profile: str, revision: str) -> str:
    """Independently read ECR's immutable manifest digest for exact SHA tag."""
    tag = "sha-" + revision
    details = aws("ecr", "describe-images", "--repository-name", REPO,
                  "--image-ids", "imageTag=" + tag,
                  profile=profile).get("imageDetails", [])
    require(len(details) == 1 and tag in details[0].get("imageTags", []),
            "ECR_IMAGE_READBACK_MISSING")
    digest = details[0].get("imageDigest")
    require(isinstance(digest, str) and DIGEST.fullmatch(digest) is not None,
            "ECR_DIGEST_INVALID")
    return digest


def publish(profile: str, current: str) -> None:
    """Build and publish historical then current immutable EOS image, no ECS writes.

    A partial registry publication is intentionally left for inspection,
    not silently deleted or overwritten.
    """
    historical, latest = HISTORICAL, current
    registry_password = run(["aws", "ecr", "get-login-password",
                             "--profile", profile, "--region", REGION])
    require(0 < len(registry_password) < 4096, "ECR_LOGIN_UNAVAILABLE")
    run(["docker", "login", "--username", "AWS", "--password-stdin",
         REGISTRY], input_bytes=registry_password, timeout=60)
    identities: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="wilsy-mwt12-ecr-") as tmp:
        for revision in (historical, latest):
            preflight_current = git("rev-parse", "HEAD")
            require(preflight_current == current and
                    git("status", "--porcelain") == "",
                    "SOURCE_CHANGED_DURING_PUBLICATION")
            source = Path(tmp) / revision
            source.mkdir()
            stage_revision(revision, source)
            ref = URI + ":sha-" + revision
            # Repository tags are immutable. Existing tags require a separate
            # readback decision rather than a potentially destructive overwrite.
            images = aws("ecr", "list-images", "--repository-name", REPO,
                         "--filter", "tagStatus=TAGGED",
                         profile=profile).get("imageIds", [])
            require(isinstance(images, list), "ECR_TAG_LIST_UNVERIFIED")
            require(not any(x.get("imageTag") == "sha-" + revision
                            for x in images if isinstance(x, dict)),
                    "ECR_TAG_ALREADY_EXISTS_RECONCILE")
            run(["docker", "build", "--pull=false", "--platform", "linux/amd64",
                 "--file", str(source / "context/infra/docker/Dockerfile.eos"),
                 "--label", SOURCE_LABEL + "=" + revision,
                 "--tag", ref, str(source / "context")],
                timeout=3600, capture=False)
            label = run(["docker", "image", "inspect", "--format",
                         '{{index .Config.Labels "' + SOURCE_LABEL + '"}}',
                         ref]).decode().strip()
            require(label == revision, "LOCAL_IMAGE_SOURCE_INVALID")
            run(["docker", "push", ref], timeout=3600, capture=False)
            digest = image_digest(profile, revision)
            identities[revision] = digest
            print("MW_T12_ECR_IMAGE_" + revision[:12] + "=" + URI + "@" + digest,
                  flush=True)
    require(identities[historical] != identities[latest],
            "ECR_IMAGE_REVISIONS_NOT_DISTINCT")
    print("MW_T12_ECR_TWO_IMMUTABLE_REVISIONS=PASS", flush=True)
    print("MW_T12_ECS_SERVICES_CREATED=FALSE", flush=True)
    print("MW_T12_ECS_ROLLBACK_CERTIFIED=FALSE", flush=True)


def main(argv: list[str] | None = None) -> int:
    """Default read-only audit; explicit publish writes ECR only after checks."""
    parser = argparse.ArgumentParser(description="MW-T12 cost-gated ECR publisher")
    parser.add_argument("--profile", default="wilsy-legal-cert")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args(argv)
    try:
        current = preflight(args.profile)
        print("MW_T12_ECR_ADMISSION=PASS", flush=True)
        print("MW_T12_ECR_TARGET_ACCOUNT=" + ACCOUNT, flush=True)
        print("MW_T12_ECR_IMAGE_HISTORICAL=" + HISTORICAL, flush=True)
        print("MW_T12_ECR_IMAGE_CURRENT=" + current, flush=True)
        if args.publish:
            publish(args.profile, current)
        else:
            print("MW_T12_ECR_PUBLISH_EXECUTED=FALSE", flush=True)
        return 0
    except PublicationError as exc:
        print("MW_T12_ECR_GATE=FAIL_CLOSED", flush=True)
        print("MW_T12_ERROR=" + str(exc), flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

# ARTIFACT: tools/eos/ops/mw_t12_ecr_publication.py
# VERSION: v1.0.2-SOURCE-KEY-MATERIAL-GUARD
# AUTHORITY BOUNDARY: Nonproduction ECR images only; no ECS service mutations.
# TENANT POSTURE: No business persistence or operational credentials.
# FAIL-CLOSED POSTURE: Unverified budget, image source or digest denies.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
