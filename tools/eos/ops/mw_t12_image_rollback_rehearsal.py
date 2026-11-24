"""TITLE: MW-T12 immutable local Docker image rollback rehearsal.
VERSION: v1.2.0-GIT-CONTEXT-PROVENANCE-AND-RUNTIME-TMPFS
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Certify two provenance-labelled Python EOS Docker image identities
         against one owned persistent MongoDB volume across forward/reverse
         container switching and authenticated source-owned readback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_image_rollback_rehearsal.py
COLLABORATION / OWNERSHIP: Extends the existing MW-T12 Git staging, immutable
         artifact admission, synthetic browser fixture, source read/deny and
         audit snapshot verification. Docker owns only names created here.
CERTIFICATION / UPDATE DATE: 2026-11-24.
CHANGELOG: v1.2.0-GIT-CONTEXT-PROVENANCE-AND-RUNTIME-TMPFS
           verifies immutable Dockerfile, requirements and runtime source
           blobs against Git before each build and enables non-root EOS
           writable paths only as owned ephemeral tmpfs mounts. The local
           Docker image ID and source labels remain independently checked.
CHANGELOG: v1.1.0-REPLICA-STARTUP-AND-IMAGE-OWNERSHIP-GUARDS
           retries owned Mongo replica initialization within a bounded
           deadline rather than racing mongosh startup; rejects any
           failed-owned-process cleanup; keeps EOS container filesystem
           immutable with explicit local tmpfs writable runtime paths.
CHANGELOG: v1.0.0-DISPOSABLE-IMAGE-ROLLBACK-DATA-CONTINUITY builds current
           and historical source archives as separately identified local
           Python EOS images; proves container image ID and source label;
           executes three exact-image deployment phases on the same
           UUID-owned Docker Mongo replica volume; admits only redacted,
           authenticated and immutable source readback; removes owned
           resources after independently verified fixture cleanup.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No production credentials, remote images, registry
         pushes, AWS writes, Docker socket exposure inside containers, or
         untrusted subprocess output. Local synthetic secrets are not logged.
TENANT BOUNDARY: Only UUID synthetic test tenant and localhost-published
         ephemeral Mongo/EOS ports. No existing tenant/Atlas connection.
AUTHORITY BOUNDARY: Local container image-ID rollback drill only, not
         release-registry manifest attestation, ECS task-definition rollback,
         Atlas restore or full infrastructure recovery.
FINANCIAL AUTHORITY BOUNDARY: No cloud spend, payment, or grant authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from tools.eos.ops.mw_t12_local_eos_recovery import (
    MWRecoveryError, SET_NAME, _admit_rollback_candidate,
    _certified_source_revision, _free_port,
)
from tools.eos.ops.mw_t12_versioned_rehearsal import _stage_revision
from tools.eos.ops.mw_t12_same_data_rehearsal import (
    FIXTURE, _authenticate_unchanged, _fingerprint_fixture, _run_fixture,
)

VERSION = "v1.2.0-GIT-CONTEXT-PROVENANCE-AND-RUNTIME-TMPFS"
MONGO_IMAGE = "mongo:7"
SOURCE_LABEL = "wilsy.mwt12.source_sha"
DRILL_LABEL = "wilsy.mwt12.disposable"
IMAGE_ID = re.compile(r"sha256:[0-9a-f]{64}\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")


def _docker(*arguments: str, capture: bool = False, timeout: int = 1800) -> str:
    """Invoke local Docker without a shell, suppressing all raw stderr."""
    try:
        result = subprocess.run(
            ["docker", *arguments], check=False, timeout=timeout,
            stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise MWRecoveryError("IMAGE_DOCKER_COMMAND_UNAVAILABLE") from error
    if result.returncode != 0:
        action = arguments[0].upper().replace("-", "_") if arguments else "UNKNOWN"
        raise MWRecoveryError("IMAGE_DOCKER_" + action + "_FAILED")
    if capture:
        raw = result.stdout or b""
        if len(raw) > 1024:
            raise MWRecoveryError("IMAGE_DOCKER_RESPONSE_OVERSIZED")
        return raw.decode("ascii", errors="replace").strip()
    return ""


def _image_identity(tag: str, revision: str, drill: str) -> str:
    """Require Docker image config SHA and both source-owned labels."""
    image_id = _docker(
        "image", "inspect", "--format", "{{.Id}}", tag, capture=True,
    )
    source = _docker(
        "image", "inspect", "--format",
        '{{index .Config.Labels "' + SOURCE_LABEL + '"}}',
        tag, capture=True,
    )
    owner = _docker(
        "image", "inspect", "--format",
        '{{index .Config.Labels "' + DRILL_LABEL + '"}}',
        tag, capture=True,
    )
    if not IMAGE_ID.fullmatch(image_id) or source != revision or owner != drill:
        raise MWRecoveryError("IMAGE_SOURCE_ATTESTATION_INVALID")
    return image_id


def _verify_context(checkout: Path, source: Path, revision: str) -> None:
    """Correlate the Docker build inputs with immutable Git object blobs."""
    for relative in (
        "Dockerfile.eos", "requirements.txt",
        "tools/eos/api/server.py", "tools/eos/kernel/db.py",
    ):
        path = source / relative
        if not path.is_file() or path.is_symlink():
            raise MWRecoveryError("IMAGE_GIT_CONTEXT_SOURCE_MISSING")
        try:
            result = subprocess.run(
                ["git", "show", revision + ":" + relative],
                cwd=checkout, capture_output=True, check=True, timeout=20,
            )
        except (OSError, subprocess.SubprocessError) as error:
            raise MWRecoveryError("IMAGE_GIT_CONTEXT_PROOF_UNAVAILABLE") from error
        if hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(
            result.stdout
        ).digest():
            raise MWRecoveryError("IMAGE_GIT_CONTEXT_PROVENANCE_MISMATCH")


def _build_image(source: Path, tag: str, revision: str, drill: str) -> str:
    """Build only the Python EOS Dockerfile from a verified Git archive."""
    dockerfile = source / "Dockerfile.eos"
    if not dockerfile.is_file() or dockerfile.is_symlink():
        raise MWRecoveryError("IMAGE_PYTHON_EOS_DOCKERFILE_MISSING")
    _docker(
        "build", "--pull=false", "--file", str(dockerfile),
        "--label", SOURCE_LABEL + "=" + revision,
        "--label", DRILL_LABEL + "=" + drill,
        "--tag", tag, str(source), timeout=3600,
    )
    return _image_identity(tag, revision, drill)


def _init_owned_replica(name: str) -> None:
    """Initialize only the named disposable Mongo container, with bounds."""
    command = (
        'rs.initiate({_id:"' + SET_NAME
        + '",members:[{_id:0,host:"mongo:27017"}]})'
    )
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        try:
            _docker("exec", name, "mongosh", "--quiet", "--eval",
                    command, timeout=8)
            return
        except MWRecoveryError:
            time.sleep(0.5)
    raise MWRecoveryError("IMAGE_MONGO_REPLICA_INIT_UNVERIFIED")


def _local_database_uri(port: int, database: str) -> str:
    """Use localhost for the existing host-side protected fixture."""
    return (
        f"mongodb://127.0.0.1:{port}/{database}"
        f"?replicaSet={SET_NAME}&directConnection=true"
    )


def _wait_mongo(port: int) -> None:
    """Admit only one primary visible through the localhost-published port."""
    from pymongo import MongoClient

    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        try:
            client = MongoClient(
                f"mongodb://127.0.0.1:{port}/admin?directConnection=true",
                serverSelectionTimeoutMS=1500,
            )
            try:
                hello = client.admin.command("hello")
                if hello.get("isWritablePrimary") is True and (
                    hello.get("setName") == SET_NAME
                ):
                    return
            finally:
                client.close()
        except Exception:
            time.sleep(0.35)
    raise MWRecoveryError("IMAGE_MONGO_PRIMARY_UNVERIFIED")


def _wait_eos(name: str, port: int) -> str:
    """Verify container stays running and EOS answers its canonical kernel."""
    base = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        state = _docker(
            "inspect", "--format", "{{.State.Running}}", name, capture=True,
        )
        if state != "true":
            raise MWRecoveryError("IMAGE_EOS_CONTAINER_EXITED")
        try:
            with urlopen(base + "/api/kernel", timeout=2) as response:
                if response.status == 200:
                    return base
        except (OSError, URLError, HTTPError, TimeoutError):
            time.sleep(0.35)
    raise MWRecoveryError("IMAGE_EOS_STARTUP_UNVERIFIED")


def _verify_container_image(name: str, expected: str) -> None:
    """Prove the *executing* container uses the expected immutable image ID."""
    actual = _docker(
        "inspect", "--format", "{{.Image}}", name, capture=True,
    )
    if actual != expected:
        raise MWRecoveryError("IMAGE_EXECUTED_DIGEST_MISMATCH")


def _verify_phase(name: str, image: str, network: str, database: str,
                  jwt_secret: str, state_file: Path, fixture: Path,
                  environment: dict[str, str], baseline: str,
                  revision: str) -> None:
    """Verify exact image, authorization, durable fixture and audit digest."""
    port = _free_port()
    mongo_uri = (
        f"mongodb://mongo:27017/{database}"
        f"?replicaSet={SET_NAME}&directConnection=true"
    )
    args = [
        "--network", network, "--publish", f"127.0.0.1:{port}:9095",
        "--env", "MONGODB_URI=" + mongo_uri,
        "--env", "MONGO_URI=" + mongo_uri,
        "--env", "BROWSER_CERT_MONGO_URI=" + mongo_uri,
        "--env", "WILSY_JWT_SECRET=" + jwt_secret,
        "--env", "WILSY_PLATFORM_WORKFORCE_SCOPE_ID=browser-cert-platform-workforce",
        "--env", "ENV=development", "--env", "WILSY_ENV=development",
        "--env", "WILSY_KENNEL_DB_TLS=0",
        "--read-only",
        "--tmpfs", "/tmp:rw,mode=1777",
        "--tmpfs", "/app/data:rw,mode=1777",
        "--tmpfs", "/app/reports:rw,mode=1777",
        "--tmpfs", "/var/log/wilsy-os:rw,mode=1777",
        image,
    ]
    _docker("run", "-d", "--name", name, *args)
    try:
        _verify_container_image(name, _image_identity(image, revision, environment["MW_T12_IMAGE_DRILL"]))
        base = _wait_eos(name, port)
        state = json.loads(state_file.read_text(encoding="utf-8"))
        if state.get("database_name") != database:
            raise MWRecoveryError("IMAGE_DATABASE_IDENTITY_MISMATCH")
        _authenticate_unchanged(base, state)
        _run_fixture(fixture, "verify-seed", state_file, environment, Path.cwd())
        if _fingerprint_fixture(fixture, state_file, environment, Path.cwd()) != baseline:
            raise MWRecoveryError("IMAGE_IMMUTABLE_AUDIT_CHANGED")
        print("MW_T12_IMAGE_VERSION_" + revision[:12] + "=PASS", flush=True)
    finally:
        _docker("rm", "--force", name)
        print("MW_T12_IMAGE_OWNED_EOS_STOPPED=TRUE", flush=True)


def rehearse_image(target: str) -> int:
    """Run opt-in image switching; never mutate live source or resources."""
    if not SHA.fullmatch(target):
        raise MWRecoveryError("IMAGE_ROLLBACK_FULL_SHA_REQUIRED")
    current, older = _admit_rollback_candidate(target)
    checkout = Path.cwd().resolve()
    fixture = checkout / FIXTURE
    if not fixture.is_file():
        raise MWRecoveryError("IMAGE_EXISTING_FIXTURE_REQUIRED")
    # Never silently download MongoDB or push an EOS image. This is a
    # zero-cloud-cost, local-only, ephemeral rehearsal.
    _docker("version", "--format", "{{.Server.Version}}", capture=True)
    _docker("image", "inspect", MONGO_IMAGE)
    drill = secrets.token_hex(8)
    prefix = "wos-mwt12-" + drill
    network, volume, mongo = prefix + "-net", prefix + "-data", prefix + "-mongo"
    current_tag, old_tag = prefix + "-current:local", prefix + "-old:local"
    tags: list[str] = []
    network_created = volume_created = mongo_created = seeded = False
    complete = False
    with tempfile.TemporaryDirectory(prefix="wilsy-mwt12-image-") as temporary:
        root = Path(temporary)
        state_file = root / "state.json"
        database = "wilsy_l8_8m_r3_mwt12_image_" + drill
        port = _free_port()
        uri = _local_database_uri(port, database)
        env = os.environ.copy()
        for key in (
            "BROWSER_CERT_MONGO_URI", "MONGODB_URI", "MONGO_URI",
            "MONGO_URL", "WILSY_MONGO_URI", "WILSY_MONGODB_URI",
        ):
            env[key] = uri
        jwt = secrets.token_hex(32)
        env.update({
            "BROWSER_CERT_MONGO_DATABASE": database,
            "WILSY_JWT_SECRET": jwt,
            "WILSY_PLATFORM_WORKFORCE_SCOPE_ID": "browser-cert-platform-workforce",
            "MW_T12_IMAGE_DRILL": drill,
            "ENV": "development", "WILSY_ENV": "development",
            "WILSY_KENNEL_DB_TLS": "0",
            "PYTHONPATH": str(checkout),
        })
        try:
            identities = {}
            for label, sha, tag in (
                ("current", current, current_tag), ("historical", older, old_tag),
            ):
                stage = root / (label + "-source")
                stage.mkdir(mode=0o700)
                _stage_revision(sha, checkout, stage)
                _verify_context(checkout, stage, sha)
                tags.append(tag)
                identities[label] = _build_image(stage, tag, sha, drill)
                if _certified_source_revision() != current:
                    raise MWRecoveryError("IMAGE_SOURCE_CHANGED_DURING_BUILD")
            if identities["current"] == identities["historical"]:
                raise MWRecoveryError("IMAGE_DISTINCT_REVISION_ID_REQUIRED")
            print("MW_T12_IMAGE_IMMUTABLE_PROVENANCE=PASS", flush=True)
            _docker("network", "create", network)
            network_created = True
            _docker("volume", "create", "--name", volume)
            volume_created = True
            # The Mongo data volume is created once and never detached or
            # recreated between the three EOS image deployments.
            _docker(
                "run", "-d", "--name", mongo, "--network", network,
                "--network-alias", "mongo",
                "--publish", f"127.0.0.1:{port}:27017",
                "--mount", f"type=volume,source={volume},target=/data/db",
                MONGO_IMAGE, "mongod", "--bind_ip_all", "--replSet", SET_NAME,
                "--quiet",
            )
            mongo_created = True
            _init_owned_replica(mongo)
            _wait_mongo(port)
            seeded = True
            _run_fixture(fixture, "seed", state_file, env, checkout)
            _run_fixture(fixture, "verify-seed", state_file, env, checkout)
            baseline = _fingerprint_fixture(fixture, state_file, env, checkout)
            for label, sha, tag, identity in (
                ("current", current, current_tag, identities["current"]),
                ("historical", older, old_tag, identities["historical"]),
                ("restored", current, current_tag, identities["current"]),
            ):
                _verify_phase(
                    prefix + "-" + label, tag, network, database, jwt,
                    state_file, fixture, env, baseline, sha,
                )
                 if _image_identity(tag, sha, drill) != identity:
                    raise MWRecoveryError("IMAGE_TAG_MUTATED_DURING_DRILL")
                if _certified_source_revision() != current:
                    raise MWRecoveryError("IMAGE_SOURCE_CHANGED_DURING_DRILL")
            complete = True
        finally:
            failure: MWRecoveryError | None = None
            if seeded and mongo_created:
                try:
                    _run_fixture(fixture, "cleanup", state_file, env, checkout)
                    print("MW_T12_IMAGE_FIXTURE_REMOVED=TRUE", flush=True)
                except MWRecoveryError:
                    failure = MWRecoveryError("IMAGE_FIXTURE_CLEANUP_FAILED")
            if mongo_created:
                try:
                    _docker("rm", "--force", mongo)
                except MWRecoveryError:
                    failure = MWRecoveryError("IMAGE_OWNED_MONGO_CLEANUP_FAILED")
            if network_created:
                try:
                    _docker("network", "rm", network)
                except MWRecoveryError:
                    failure = MWRecoveryError("IMAGE_OWNED_NETWORK_CLEANUP_FAILED")
            if volume_created:
                try:
                    _docker("volume", "rm", volume)
                except MWRecoveryError:
                    failure = MWRecoveryError("IMAGE_OWNED_VOLUME_CLEANUP_FAILED")
            for tag in tags:
                try:
                    _docker("image", "rm", tag)
                except MWRecoveryError:
                    failure = MWRecoveryError("IMAGE_OWNED_IMAGE_CLEANUP_FAILED")
            if failure is not None:
                raise failure
    if not complete:
        raise MWRecoveryError("IMAGE_THREE_PHASE_UNVERIFIED")
    print("MW_T12_IMAGE_ROLLBACK_READBACK=PASS", flush=True)
    print("MW_T12_IMAGE_SINGLE_DATA_VOLUME=PASS", flush=True)
    print("MW_T12_IMAGE_IMMUTABLE_AUDIT_EVIDENCE=UNCHANGED", flush=True)
    print("MW_T12_IMAGE_DEPLOYMENT_RESTORED=TRUE", flush=True)
    print("MW_T12_IMAGE_LOCAL_NONPRODUCTION_CERTIFIED=TRUE", flush=True)
    print("MW_T12_PRODUCTION_IMAGE_ROLLBACK_CERTIFIED=FALSE", flush=True)
    print("MW_T12_FULL_INFRASTRUCTURE_RECOVERY_CERTIFIED=FALSE", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Require exact historical commit and fail closed on all Docker errors."""
    parser = argparse.ArgumentParser(
        description="MW-T12 nonproduction immutable Docker image rollback"
    )
    parser.add_argument("--rehearse", required=True, metavar="EXACT_OLDER_SHA")
    args = parser.parse_args(argv)
    try:
        return rehearse_image(args.rehearse)
    except (MWRecoveryError, KeyboardInterrupt) as error:
        code = error.code if isinstance(error, MWRecoveryError) else "OPERATOR_INTERRUPTED"
        print("MW_T12_IMAGE_REHEARSAL=FAIL_CLOSED", flush=True)
        print("MW_T12_ERROR=" + code, flush=True)
        print("MW_T12_PRODUCTION_IMAGE_ROLLBACK_CERTIFIED=FALSE", flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


# ARTIFACT: tools/eos/ops/mw_t12_image_rollback_rehearsal.py
# VERSION: v1.2.0-GIT-CONTEXT-PROVENANCE-AND-RUNTIME-TMPFS
# AUTHORITY BOUNDARY: Local immutable Docker image and synthetic data only.
# TENANT POSTURE: UUID-scoped local fixture, no canonical Founder tenant.
# FAIL-CLOSED POSTURE: Provenance, exact HTTP, audit and cleanup are required.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
