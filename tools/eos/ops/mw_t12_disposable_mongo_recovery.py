"""TITLE: MW-T12 disposable MongoDB backup/restore certificate rehearsal.
VERSION: v1.1.0-DISPOSABLE-MONGO-STARTUP-CORRECTION
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Run a real synthetic Mongo dump, fault, restore and readback in a
         newly created network-disabled Docker container; never touch EOS.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_disposable_mongo_recovery.py
COLLABORATION / OWNERSHIP: Python EOS engineering operator / Docker.
CERTIFICATION / UPDATE DATE: 2026-11-24.
CHANGELOG: v1.1.0-DISPOSABLE-MONGO-STARTUP-CORRECTION provisions explicit
           tmpfs ownership for the official Mongo image, removes the immutable
           root filesystem constraint and reports allowlisted container state
           on startup failure without disclosing Docker logs or secrets.
CHANGELOG: v1.0.0-DISPOSABLE-MONGO-RECOVERY adds isolated synthetic recovery
           evidence with fail-closed preflight and mandatory cleanup.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No production URI, secrets, AWS/KMS or host ports.
TENANT BOUNDARY: Random synthetic database/tenant; no existing business data.
AUTHORITY BOUNDARY: Component-level local test, NOT full EOS recovery certification.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from typing import Any

VERSION = "v1.1.0-DISPOSABLE-MONGO-STARTUP-CORRECTION"
IMAGE = "mongo:7"


class RecoveryGateError(RuntimeError):
    """Expose only fixed, non-sensitive error codes to operators."""

    def __init__(self, code: str) -> None:
        """Preserve one bounded failure code without raw Docker stderr."""
        super().__init__(code)
        self.code = code


def docker(*arguments: str, timeout: int = 35) -> str:
    """Run Docker without a shell, sanitizing all failure output."""
    try:
        result = subprocess.run(
            ["docker", *arguments], check=False, capture_output=True,
            text=True, timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RecoveryGateError("DOCKER_EXECUTION_UNAVAILABLE") from error
    if result.returncode:
        raise RecoveryGateError("DOCKER_COMMAND_FAILED")
    return result.stdout.strip()


def mongo(container: str, expression: str) -> str:
    """Evaluate synthetic fixture operations in the owned container only."""
    return docker(
        "exec", container, "mongosh", "--quiet", "--host",
        "127.0.0.1", "--port", "27017", "--eval", expression,
    )


def preflight() -> None:
    """Require an existing Mongo image and local Docker; never pull or deploy."""
    if shutil.which("docker") is None:
        raise RecoveryGateError("DOCKER_BINARY_UNAVAILABLE")
    docker("info", "--format", "{{.ServerVersion}}")
    image_id = docker("image", "inspect", IMAGE, "--format", "{{.Id}}")
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", image_id):
        raise RecoveryGateError("IMAGE_ID_UNVERIFIABLE")


def _startup_failure(container: str) -> RecoveryGateError:
    """Classify an owned disposable container without reading untrusted logs.

    Only Docker's status enum and OOM flag are used; a failed inspection leaves
    the original startup error. This never reports endpoints or user data.
    """
    try:
        status = docker("inspect", container, "--format", "{{.State.Status}}")
        oom = docker("inspect", container, "--format", "{{.State.OOMKilled}}")
    except RecoveryGateError:
        return RecoveryGateError("MONGO_START_UNAVAILABLE")
    if oom == "true":
        return RecoveryGateError("MONGO_CONTAINER_OOM")
    if status in {"exited", "dead", "removing"}:
        return RecoveryGateError("MONGO_CONTAINER_EXITED")
    return RecoveryGateError("MONGO_START_UNAVAILABLE")


def primary(container: str) -> None:
    """Wait for an isolated single-node replica-set primary."""
    for _ in range(45):
        try:
            if mongo(container, "db.adminCommand({ping:1}).ok") == "1":
                break
        except RecoveryGateError:
            pass
        time.sleep(1)
    else:
        raise _startup_failure(container)
    mongo(container, 'rs.initiate({_id:"mwT12",members:[{_id:0,host:"127.0.0.1:27017"}]})')
    for _ in range(45):
        try:
            if mongo(container, "db.hello().isWritablePrimary") == "true":
                return
        except RecoveryGateError:
            pass
        time.sleep(1)
    raise RecoveryGateError("MONGO_PRIMARY_UNAVAILABLE")


def exercise() -> dict[str, Any]:
    """Backup, alter, restore and independently read synthetic Mongo data.

    No EOS deployment, Atlas connection or tenant mutation occurs. The archive,
    replica and fixture are container-local and deleted at the end.
    """
    preflight()
    suffix = secrets.token_hex(8)
    name = "mw-t12-isolated-" + suffix
    dbname = "mw_t12_isolated_" + suffix
    fixture = {
        "tenant_id": "synthetic-" + suffix,
        "task": "MW-T12-SYNTHETIC",
        "revision": 3,
        "comment": "synthetic recovery evidence",
        "state": "BASELINE",
    }
    canonical = json.dumps(fixture, sort_keys=True, separators=(",", ":"))
    fingerprint = hashlib.sha3_512(canonical.encode()).hexdigest()
    started = False
    began = time.monotonic()
    try:
        docker(
            "run", "-d", "--name", name,
            "--label", "wilsy.mw_t12.disposable=true",
            "--network", "none",
            "--tmpfs", "/data/db:rw,size=256m,uid=999,gid=999,mode=0700",
            "--tmpfs", "/data/configdb:rw,size=32m,uid=999,gid=999,mode=0700",
            "--tmpfs", "/tmp:rw,size=128m,mode=1777",
            "--memory", "768m", "--cpus", "1",
            IMAGE, "mongod", "--replSet", "mwT12",
            "--bind_ip", "127.0.0.1",
            timeout=45,
        )
        started = True
        network = docker("inspect", name, "--format", "{{.HostConfig.NetworkMode}}")
        ports = docker("inspect", name, "--format", "{{json .HostConfig.PortBindings}}")
        if network != "none" or ports not in ("null", "{}"):
            raise RecoveryGateError("ISOLATION_UNVERIFIED")
        primary(name)
        mongo(name, f'db.getSiblingDB("{dbname}").evidence.insertOne({canonical})')
        def read() -> dict[str, Any]:
            """Hydrate the independently read fixture; exclude Mongo _id."""
            raw = mongo(name, f'JSON.stringify(db.getSiblingDB("{dbname}").evidence.findOne({{}},{{_id:0}}))')
            try:
                value = json.loads(raw)
            except (ValueError, TypeError) as error:
                raise RecoveryGateError("READBACK_INVALID") from error
            if not isinstance(value, dict):
                raise RecoveryGateError("READBACK_INVALID")
            return value

        if read() != fixture:
            raise RecoveryGateError("BASELINE_MISMATCH")
        docker(
            "exec", name, "mongodump", "--host", "127.0.0.1",
            "--port", "27017", "--db", dbname,
            "--archive=/tmp/mw-t12.archive",
        )
        mongo(name, f'db.getSiblingDB("{dbname}").evidence.updateOne({{}},{{$set:{{state:"ALTERED"}}}})')
        if read().get("state") != "ALTERED":
            raise RecoveryGateError("FAULT_NOT_APPLIED")
        docker(
            "exec", name, "mongorestore", "--host", "127.0.0.1",
            "--port", "27017", "--drop",
            "--archive=/tmp/mw-t12.archive",
        )
        if read() != fixture:
            raise RecoveryGateError("RESTORE_MISMATCH")
        if mongo(name, f'db.getSiblingDB("{dbname}").evidence.countDocuments({{}})') != "1":
            raise RecoveryGateError("RESTORED_COUNT_MISMATCH")
        return {
            "schema": "wilsy.mw-t12.disposable-mongo-rehearsal.v1",
            "version": VERSION,
            "status": "PASS",
            "scope": "SYNTHETIC_MONGO_BACKUP_RESTORE_ONLY",
            "snapshot_sha3_512": fingerprint,
            "observed_elapsed_ms": round((time.monotonic() - began) * 1000),
            "eos_recovery_certified": False,
            "production_release_authorized": False,
        }
    finally:
        # Never target pre-existing containers; name is uniquely generated.
        # A failed Docker run may create a container before exiting.
        try:
            docker("rm", "-f", "-v", name, timeout=30)
        except RecoveryGateError:
            if started:
                raise RecoveryGateError("DISPOSABLE_CLEANUP_UNVERIFIED") from None


def main(argv: list[str] | None = None) -> int:
    """Select read-only preflight or an isolated disposable test, never live EOS."""
    parser = argparse.ArgumentParser(description="MW-T12 isolated recovery rehearsal")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--run-disposable", action="store_true")
    args = parser.parse_args(argv)
    if any(os.getenv(k, "").strip().lower() in {"prod", "production"}
           for k in ("ENV", "WILSY_ENV")):
        print("MW_T12_STATUS=DENIED_PRODUCTION_ENVIRONMENT")
        return 2
    try:
        if args.check:
            preflight()
            print("MW_T12_PREFLIGHT=PASS")
            print("MW_T12_DRILL_EXECUTED=FALSE")
        else:
            print(json.dumps(exercise(), sort_keys=True))
        print("MW_T12_EOS_RECOVERY_CERTIFIED=FALSE")
        return 0
    except RecoveryGateError as error:
        print("MW_T12_STATUS=FAIL_CLOSED")
        print("MW_T12_ERROR=" + error.code)
        print("MW_T12_EOS_RECOVERY_CERTIFIED=FALSE")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


# ARTIFACT: tools/eos/ops/mw_t12_disposable_mongo_recovery.py
# VERSION: v1.1.0-DISPOSABLE-MONGO-STARTUP-CORRECTION
# AUTHORITY BOUNDARY: Disposable Mongo component rehearsal only, not EOS recovery.
# TENANT POSTURE: No canonical or external tenant state is touched.
# FAIL-CLOSED POSTURE: Any Docker, isolation, backup, fault, restore, readback or cleanup failure denies success.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
