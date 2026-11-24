"""TITLE: MW-T12 isolated local Python EOS service recovery operator.
VERSION: v1.0.0-ISOLATED-HOST-REPLICA-EOS-RECOVERY
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Own a fresh loopback-only local mongod replica and execute the
         existing authenticated Python EOS restart and durable browser verifier.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_local_eos_recovery.py
COLLABORATION / OWNERSHIP: Python EOS operator; canonical browser certification runner.
CERTIFICATION / UPDATE DATE: 2026-11-24.
CHANGELOG: v1.0.0-ISOLATED-HOST-REPLICA-EOS-RECOVERY replaces unreliable
           Docker Desktop host port forwarding with an operator-owned temporary
           local mongod process and exact synthetic database, without altering
           the existing browser runner, IAM, EOS or production infrastructure.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No production URI, database secrets or raw logs.
TENANT BOUNDARY: Newly generated UUID fixture database and loopback-only replica;
                 canonical wilsy tenant is never selected.
AUTHORITY BOUNDARY: Developer-local synthetic EOS process recovery only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time

from pymongo import MongoClient
from pymongo.errors import PyMongoError

VERSION = "v1.0.0-ISOLATED-HOST-REPLICA-EOS-RECOVERY"
SET_NAME = "wilsyVendorCertRS"
BROWSER_SUITE = "tests/e2e/headquarters-operating-workspace.browser.spec.js"
BROWSER_RUNNER = "tests/e2e/run-browser-cert.mjs"


class MWRecoveryError(RuntimeError):
    """Report a bounded operator-safe code rather than Mongo URI or process logs."""

    def __init__(self, code: str) -> None:
        """Carry only a stable certification failure code."""
        super().__init__(code)
        self.code = code


def _guard() -> tuple[str, str]:
    """Reject production and require both host mongod and Node interpreters.

    This operator never uses a selected process MONGODB_URI; it creates its own
    local synthetic database and explicitly overrides the child process URI.
    """
    if any(
        os.environ.get(key, "").strip().lower() in {"prod", "production"}
        for key in ("ENV", "WILSY_ENV")
    ):
        raise MWRecoveryError("PRODUCTION_ENVIRONMENT_FORBIDDEN")
    binary = shutil.which("mongod")
    if binary is None:
        candidate = Path("/opt/homebrew/bin/mongod")
        if candidate.is_file():
            binary = str(candidate)
    node = shutil.which("node")
    if not binary or not node:
        raise MWRecoveryError("HOST_MONGOD_OR_NODE_UNAVAILABLE")
    if not Path(BROWSER_RUNNER).is_file() or not Path(BROWSER_SUITE).is_file():
        raise MWRecoveryError("CERTIFICATION_RUNNER_NOT_FOUND")
    return binary, node


def _free_port() -> int:
    """Reserve a candidate ephemeral loopback port without touching a listener."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    if not 1024 <= port <= 65535:
        raise MWRecoveryError("LOOPBACK_PORT_UNAVAILABLE")
    return port


def _wait_primary(process: subprocess.Popen[bytes], port: int) -> None:
    """Wait for the owned mongod and initialize only its fresh replica set."""
    connect_uri = f"mongodb://127.0.0.1:{port}/?directConnection=true"
    initiated = False
    deadline = time.monotonic() + 45
    with MongoClient(
        connect_uri, serverSelectionTimeoutMS=1200, connectTimeoutMS=1200,
        socketTimeoutMS=1200,
    ) as client:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise MWRecoveryError("OWNED_MONGO_PROCESS_EXITED")
            try:
                client.admin.command("ping")
                if not initiated:
                    client.admin.command({
                        "replSetInitiate": {
                            "_id": SET_NAME,
                            "members": [{"_id": 0, "host": f"127.0.0.1:{port}"}],
                        }
                    })
                    initiated = True
                hello = client.admin.command("hello")
                if (
                    hello.get("setName") == SET_NAME
                    and hello.get("isWritablePrimary") is True
                ):
                    return
            except PyMongoError:
                if initiated:
                    raise MWRecoveryError("OWNED_REPLICA_INITIATION_OR_PRIMARY_FAILED") from None
            time.sleep(0.4)
    raise MWRecoveryError("OWNED_REPLICA_START_TIMEOUT")


def _stop_owned(process: subprocess.Popen[bytes]) -> None:
    """Terminate only the subprocess created here, denying unverified cleanup."""
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired as error:
                raise MWRecoveryError("OWNED_MONGO_SHUTDOWN_UNVERIFIED") from error
    if process.poll() is None:
        raise MWRecoveryError("OWNED_MONGO_SHUTDOWN_UNVERIFIED")


def run(binary: str, node: str) -> int:
    """Execute real authenticated restart against a new ephemeral local replica.

    Existing runner owns all synthetic principal and tenant fixtures, HTTP
    startup/stop/restart verification, browser tests, and fixture readback.
    This wrapper owns only mongod lifecycle and never stores EOS secrets.
    """
    nonce = secrets.token_hex(12)
    database = "wilsy_l8_8m_r3_mwt12_" + nonce
    port = _free_port()
    with tempfile.TemporaryDirectory(prefix="wilsy-mw-t12-eos-") as temporary:
        directory = Path(temporary)
        dbpath = directory / "mongo"
        dbpath.mkdir(mode=0o700)
        try:
            process = subprocess.Popen(
                [
                    binary, "--dbpath", str(dbpath), "--port", str(port),
                    "--bind_ip", "127.0.0.1", "--replSet", SET_NAME,
                    "--nounixsocket", "--quiet",
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
        except OSError as error:
            raise MWRecoveryError("OWNED_MONGO_LAUNCH_FAILED") from error
        primary_failure: MWRecoveryError | None = None
        exit_code = 2
        try:
            _wait_primary(process, port)
            print("MW_T12_OWNED_REPLICA_PRIMARY=PASS", flush=True)
            environment = os.environ.copy()
            environment.update({
                "BROWSER_CERT_MONGO_URI": (
                    f"mongodb://127.0.0.1:{port}/{database}"
                    f"?replicaSet={SET_NAME}&directConnection=true"
                ),
                "MW_T12_EOS_SERVICE_RECOVERY": "1",
                "ENV": "development",
                "WILSY_ENV": "development",
            })
            # The runner owns synthetic fixture cleanup and controlled EOS restart.
            completed = subprocess.run(
                [node, BROWSER_RUNNER, BROWSER_SUITE],
                env=environment, check=False,
            )
            exit_code = completed.returncode
            if exit_code != 0:
                raise MWRecoveryError("AUTHENTICATED_EOS_RUNNER_FAILED")
            return 0
        except MWRecoveryError as error:
            primary_failure = error
        finally:
            try:
                _stop_owned(process)
                print("MW_T12_OWNED_MONGO_STOPPED=TRUE", flush=True)
            except MWRecoveryError as error:
                raise error from primary_failure
        if primary_failure is not None:
            raise primary_failure
        return exit_code


def main(argv: list[str] | None = None) -> int:
    """Provide explicit read-only tooling check or opt-in isolated run."""
    parser = argparse.ArgumentParser(description="MW-T12 isolated Python EOS recovery")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--run", action="store_true")
    args = parser.parse_args(argv)
    try:
        binary, node = _guard()
        if args.check:
            print("MW_T12_HOST_PREREQUISITES=PASS")
            print("MW_T12_RECOVERY_EXECUTED=FALSE")
            return 0
        result = run(binary, node)
        if result != 0:
            raise MWRecoveryError("AUTHENTICATED_EOS_RUNNER_FAILED")
        print("MW_T12_LOCAL_AUTHENTICATED_EOS_RESTART=RUNNER_PASSED")
        print("MW_T12_FULL_INFRASTRUCTURE_RECOVERY_CERTIFIED=FALSE")
        return 0
    except (MWRecoveryError, KeyboardInterrupt) as error:
        code = error.code if isinstance(error, MWRecoveryError) else "OPERATOR_INTERRUPTED"
        print("MW_T12_STATUS=FAIL_CLOSED")
        print("MW_T12_ERROR=" + code)
        print("MW_T12_FULL_INFRASTRUCTURE_RECOVERY_CERTIFIED=FALSE")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


# ARTIFACT: tools/eos/ops/mw_t12_local_eos_recovery.py
# VERSION: v1.0.0-ISOLATED-HOST-REPLICA-EOS-RECOVERY
# AUTHORITY BOUNDARY: Local synthetic Python EOS test only, no production operations.
# TENANT POSTURE: Random test tenant and local temporary database exclusively.
# FAIL-CLOSED POSTURE: Missing tooling, health, startup, readback, browser or shutdown denies success.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
