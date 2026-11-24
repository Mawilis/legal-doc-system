"""TITLE: MW-T12 disposable versioned Python EOS execution switch rehearsal.
VERSION: v1.0.1-ROOT-BOUNDED-TRACKED-SYMLINKS
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Prove two immutable executable source revisions can independently
         pass the existing controlled EOS restart and browser certification.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_versioned_rehearsal.py
COLLABORATION / OWNERSHIP: MW-T12 recovery operator owns Mongo and browser
         evidence; existing Python EOS browser runner owns synthetic actors,
         authenticated reads, process stop/restart and cleanup.
CERTIFICATION / UPDATE DATE: 2026-11-24.
CHANGELOG: v1.0.1-ROOT-BOUNDED-TRACKED-SYMLINKS accepts only
           repository-tracked relative symlinks whose normalized targets stay
           inside the private extraction root; absolute, escaping, hardlink
           and special entries still fail closed. The Python data extraction
           filter independently validates every extracted member. No live
           checkout, tenant, authorization or running process is changed.
CHANGELOG: v1.0.0-DISPOSABLE-SOURCE-VERSION-EXECUTION-REHEARSAL
           stages exact historical Git archives outside the live checkout;
           runs separately isolated source-version browser certification at
           current and older revisions, checks stage-blob provenance and
           source-owned screenshot/readback evidence; rejects any incomplete
           lifecycle. Never calls git checkout/reset or changes production.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No credential, user, URI or source content printed;
         diagnostic errors are bounded codes, and temporary files discarded.
TENANT BOUNDARY: Each version uses a separate, loopback-only, UUID synthetic
         database removed by the existing browser runner.
AUTHORITY BOUNDARY: This certifies two disposable executable source revisions,
         NOT continuity of the same persisted database or production rollback.
FINANCIAL AUTHORITY BOUNDARY: No financial authorization or action.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import posixpath
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

from tools.eos.ops.mw_t12_local_eos_recovery import (
    BROWSER_RUNNER,
    BROWSER_SUITE,
    MWRecoveryError,
    ROLLBACK_REQUIRED_PATHS,
    SET_NAME,
    _admit_rollback_candidate,
    _certified_source_revision,
    _free_port,
    _guard,
    _stop_owned,
    _verify_headquarters_evidence,
    _wait_primary,
)

VERSION = "v1.0.1-ROOT-BOUNDED-TRACKED-SYMLINKS"


def _stage_revision(revision: str, checkout: Path, destination: Path) -> None:
    """Stage an immutable Git archive, never a checkout or an active service."""
    archive = destination.parent / (revision + ".tar")
    try:
        with archive.open("wb") as output:
            subprocess.run(
                ["git", "archive", "--format=tar", revision],
                cwd=checkout, stdout=output, stderr=subprocess.DEVNULL,
                check=True, timeout=120,
            )
        with tarfile.open(archive, mode="r:") as source:
            # Git archives may legitimately contain tracked relative
            # symlinks. Admit only links staying inside the owned root;
            # disallow hardlinks, devices and all other special entries.
            # The Python data filter also checks each extracted path and
            # resolved link against the real destination at extraction time.
            members = source.getmembers()
            for member in members:
                name = member.name
                normalized = posixpath.normpath(name)
                if (
                    posixpath.isabs(name)
                    or normalized in {".", ".."}
                    or normalized.startswith("../")
                ):
                    raise MWRecoveryError("VERSION_ARCHIVE_UNSAFE_MEMBER")
                if member.isfile() or member.isdir():
                    continue
                if not member.issym():
                    raise MWRecoveryError("VERSION_ARCHIVE_UNSAFE_MEMBER")
                link = member.linkname
                target = posixpath.normpath(
                    posixpath.join(posixpath.dirname(name), link)
                )
                if (
                    not link
                    or posixpath.isabs(link)
                    or target in {".", ".."}
                    or target.startswith("../")
                ):
                    raise MWRecoveryError("VERSION_ARCHIVE_UNSAFE_MEMBER")
            source.extractall(path=destination, filter="data")
        for required in ROLLBACK_REQUIRED_PATHS:
            item = destination / required
            if not item.is_file() or item.is_symlink():
                raise MWRecoveryError("VERSION_REQUIRED_SOURCE_MISSING")
            historical = subprocess.run(
                ["git", "show", revision + ":" + required],
                cwd=checkout, capture_output=True, check=True, timeout=15,
            )
            if hashlib.sha256(item.read_bytes()).digest() != hashlib.sha256(
                historical.stdout
            ).digest():
                raise MWRecoveryError("VERSION_SOURCE_PROVENANCE_MISMATCH")
    except MWRecoveryError:
        raise
    except (OSError, ValueError, tarfile.TarError, subprocess.SubprocessError) as error:
        raise MWRecoveryError("VERSION_ARCHIVE_STAGING_FAILED") from error
    finally:
        archive.unlink(missing_ok=True)


def _link_local_dependencies(checkout: Path, destination: Path) -> None:
    """Link only installed local build/test dependencies into a private tree."""
    for relative in ("node_modules", "client/node_modules"):
        source = checkout / relative
        target = destination / relative
        if not source.is_dir() or target.exists() or target.is_symlink():
            raise MWRecoveryError("VERSION_LOCAL_DEPENDENCIES_UNAVAILABLE")
        target.symlink_to(source.resolve(), target_is_directory=True)


def _certify_staged_version(binary: str, node: str, revision: str,
                            stage: Path, owner: Path) -> None:
    """Run the existing auth/browser runner against a fresh owned Mongo."""
    database = "wilsy_l8_8m_r3_mwt12_" + revision[:12]
    port = _free_port()
    dbpath = owner / "mongo"
    dbpath.mkdir(mode=0o700)
    evidence = owner / "headquarters-browser-evidence"
    evidence.mkdir(mode=0o700)
    try:
        mongo = subprocess.Popen(
            [binary, "--dbpath", str(dbpath), "--port", str(port),
             "--bind_ip", "127.0.0.1", "--replSet", SET_NAME,
             "--nounixsocket", "--quiet"],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, close_fds=True,
        )
    except OSError as error:
        raise MWRecoveryError("VERSION_OWNED_MONGO_LAUNCH_FAILED") from error
    try:
        _wait_primary(mongo, port)
        uri = (f"mongodb://127.0.0.1:{port}/{database}"
               f"?replicaSet={SET_NAME}&directConnection=true")
        environment = os.environ.copy()
        for key in (
            "BROWSER_CERT_MONGO_URI", "MONGODB_URI", "MONGO_URI",
            "MONGO_URL", "WILSY_MONGO_URI", "WILSY_MONGODB_URI",
        ):
            environment[key] = uri
        environment.update({
            "BROWSER_CERT_PYTHON": sys.executable,
            "PYTHONPATH": str(stage),
            "MW_T12_EOS_SERVICE_RECOVERY": "1",
            "WILSY_HEADQUARTERS_EVIDENCE_DIR": str(evidence),
            "ENV": "development", "WILSY_ENV": "development",
        })
        completed = subprocess.run(
            [node, BROWSER_RUNNER, BROWSER_SUITE],
            cwd=stage, env=environment, check=False,
        )
        if completed.returncode != 0:
            raise MWRecoveryError("VERSION_AUTHENTICATED_BROWSER_FAILED")
        _verify_headquarters_evidence(evidence)
        print("MW_T12_VERSION_" + revision[:12] + "_AUTHENTICATED=PASS", flush=True)
    finally:
        _stop_owned(mongo)
        print("MW_T12_VERSION_OWNED_MONGO_STOPPED=TRUE", flush=True)


def rehearse(target: str) -> int:
    """Execute distinct, disposable old/new source trees in a governed order."""
    binary, node = _guard()
    current, older = _admit_rollback_candidate(target)
    checkout = Path.cwd().resolve()
    if not Path(sys.executable).is_file():
        raise MWRecoveryError("VERSION_PYTHON_INTERPRETER_MISSING")
    with tempfile.TemporaryDirectory(prefix="wilsy-mw-t12-version-switch-") as temp:
        root = Path(temp)
        for label, revision in (("current", current), ("historical", older)):
            stage = root / (label + "-source")
            stage.mkdir(mode=0o700)
            _stage_revision(revision, checkout, stage)
            _link_local_dependencies(checkout, stage)
            # Archive Git objects, not mutable tracked or untracked files.
            # Each version receives fresh isolated Mongo and browser evidence.
            owner = root / (label + "-runtime")
            owner.mkdir(mode=0o700)
            _certify_staged_version(binary, node, revision, stage, owner)
            if _certified_source_revision() != current:
                raise MWRecoveryError("SOURCE_REVISION_CHANGED_DURING_DRILL")
    print("MW_T12_SOURCE_VERSION_SWITCH_EXECUTED=TRUE")
    print("MW_T12_CURRENT_SOURCE=" + current)
    print("MW_T12_HISTORICAL_SOURCE=" + older)
    print("MW_T12_TWO_VERSION_AUTHENTICATED_READBACK=PASS")
    print("MW_T12_SAME_DATA_ROLLBACK_CERTIFIED=FALSE")
    print("MW_T12_VERSIONED_ROLLBACK_CERTIFIED=FALSE")
    print("MW_T12_FULL_INFRASTRUCTURE_RECOVERY_CERTIFIED=FALSE")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Accept only an explicit historical SHA, not an arbitrary remote URI."""
    parser = argparse.ArgumentParser(
        description="MW-T12 isolated two-revision executable source rehearsal"
    )
    parser.add_argument("--rehearse", required=True, metavar="EXACT_OLDER_COMMIT")
    args = parser.parse_args(argv)
    try:
        return rehearse(args.rehearse)
    except (MWRecoveryError, KeyboardInterrupt) as error:
        code = error.code if isinstance(error, MWRecoveryError) else "OPERATOR_INTERRUPTED"
        print("MW_T12_VERSION_SWITCH=FAIL_CLOSED")
        print("MW_T12_ERROR=" + code)
        print("MW_T12_VERSIONED_ROLLBACK_CERTIFIED=FALSE")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


# ARTIFACT: tools/eos/ops/mw_t12_versioned_rehearsal.py
# VERSION: v1.0.1-ROOT-BOUNDED-TRACKED-SYMLINKS
# AUTHORITY BOUNDARY: Two isolated local EOS source versions, no live deployment.
# TENANT POSTURE: Distinct synthetic local fixtures, never canonical wilsy.
# FAIL-CLOSED POSTURE: Missing source, proof, auth, browser, cleanup denies success.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
