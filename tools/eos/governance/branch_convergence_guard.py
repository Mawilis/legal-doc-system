"""WILSY OS branch-parity and dirty-work accountability guard.

TITLE: WILSY OS Branch Convergence and Dirty-Work Accountability Guard
VERSION: v1.0.0-R1D-B0F-REPOSITORY-CONVERGENCE-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Emits an evidence-bounded parity decision for the operating branch
         and verifies that every surviving dirty path is explicitly preserved
         or assigned to a named campaign. An empty index is never treated as
         proof of convergence or dirty-work accountability.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/branch_convergence_guard.py
COLLABORATION / OWNERSHIP: Git owns commit identity; GitHub owns governed PR
                           state; campaign owners own the signed dirty-work
                           manifest. This guard owns no repository mutation.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.0.1-R1D-B0F-REPOSITORY-CONVERGENCE-R1 establishes explicit
           local/tracking/remote/main parity, governed-PR pending state, and
           NUL-safe dirty-work accountability with SHA3-512 preservation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; audit evidence.
SECURITY / PRIVACY POSTURE: Only repository paths, commit IDs, and digests are
                            emitted; no file contents or credentials are read
                            into output. GitHub lookup is bounded and optional.
TENANT BOUNDARY: None; this is repository governance, not tenant authority.
AUTHORITY BOUNDARY: Evidence and closure classification only; no merge, push,
                    commit, staging, reset, restore, checkout, or clean power.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Ref mismatches, divergent history, missing governed PR,
                     malformed manifests, new paths, lost paths, and digest
                     changes fail closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OPERATING_BRANCH = "fg108o4b-knowledge-operating-room"
DEFAULT_REMOTE = "origin"
MANIFEST_VERSION = 1


class GuardFailure(RuntimeError):
    """Structured fail-closed governance failure."""


def _git(*args: str) -> str:
    """Run one read-only Git query at the canonical repository root."""

    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), *args],
            stderr=subprocess.PIPE,
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise GuardFailure("git evidence query failed") from error


def _sha3(path: Path) -> str:
    """Return the deterministic SHA3-512 digest of one tracked file."""

    if not path.is_file():
        raise GuardFailure(f"accountability path is not a file: {path}")
    return hashlib.sha3_512(path.read_bytes()).hexdigest()


def _status() -> dict[str, dict[str, str]]:
    """Capture NUL-safe status records and their current content digests."""

    raw = subprocess.check_output(
        ["git", "-C", str(ROOT), "status", "--porcelain=v1", "-z", "-uall"],
        stderr=subprocess.PIPE,
    )
    records = raw.decode("utf-8", errors="strict").split("\0")
    result: dict[str, dict[str, str]] = {}
    for record in records:
        if not record:
            continue
        if len(record) < 4:
            raise GuardFailure("malformed NUL-safe Git status record")
        code = record[:2]
        path = record[3:]
        if code[0] in {"R", "C"}:
            raise GuardFailure("rename/copy status requires explicit adjudication")
        state = "UNTRACKED" if code == "??" else "MODIFIED"
        result[path] = {"state": state, "sha3_512": _sha3(ROOT / path)}
    return result


@dataclass(frozen=True)
class ParityEvidence:
    """Immutable local/tracking/remote parity evidence."""

    local: str
    tracking: str
    remote_operating: str
    remote_main: str
    merge_base: str
    ahead: int
    behind: int
    open_pr: str
    status: str


def _ref(ref: str) -> str:
    return _git("rev-parse", ref)


def _upstream_ref() -> str:
    """Resolve the configured upstream ref independently from remote naming."""

    return _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")


def _counts(local: str, remote_main: str) -> tuple[int, int, str]:
    try:
        merge_base = _git("merge-base", local, remote_main)
        counts = _git("rev-list", "--left-right", "--count", f"{local}...{remote_main}")
        ahead_text, behind_text = counts.split()
        return int(ahead_text), int(behind_text), merge_base
    except (ValueError, GuardFailure) as error:
        raise GuardFailure("unable to calculate branch parity") from error


def _open_pr(branch: str, base: str) -> str:
    """Find an exact open operating-to-main PR without treating local parity as enough."""

    try:
        payload = subprocess.check_output(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                os.getenv("WILSY_REPOSITORY", "Mawilis/legal-doc-system"),
                "--head",
                branch,
                "--base",
                base,
                "--state",
                "open",
                "--json",
                "number,headRefName,baseRefName",
            ],
            stderr=subprocess.PIPE,
            text=True,
        )
        rows = json.loads(payload)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError):
        return "NONE"
    for row in rows:
        if row.get("headRefName") == branch and row.get("baseRefName") == base:
            return str(row["number"])
    return "NONE"


def parity_evidence(
    operating_branch: str = DEFAULT_OPERATING_BRANCH,
    remote: str = DEFAULT_REMOTE,
    base_branch: str = "main",
) -> ParityEvidence:
    """Collect and adjudicate all branch identities without changing Git state."""

    local = _ref("HEAD")
    tracking_ref = _upstream_ref()
    tracking = _ref(tracking_ref)
    remote_operating = _ref(f"{remote}/{operating_branch}")
    remote_main = _ref(f"{remote}/{base_branch}")
    ahead, behind, merge_base = _counts(local, remote_main)
    open_pr = "NONE"
    if ahead or behind or local != tracking or tracking != remote_operating:
        open_pr = _open_pr(operating_branch, base_branch)
    identities_equal = local == tracking == remote_operating
    if identities_equal and ahead == 0 and behind == 0:
        status = "PASS"
    elif identities_equal and ahead > 0 and behind == 0 and open_pr != "NONE":
        status = "PENDING"
    else:
        status = "FAIL"
    return ParityEvidence(
        local,
        tracking,
        remote_operating,
        remote_main,
        merge_base,
        ahead,
        behind,
        open_pr,
        status,
    )


def _manifest(path: Path) -> dict[str, dict[str, str]]:
    """Load a preserved/campaign manifest and return its explicit path set."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("version") != MANIFEST_VERSION:
            raise GuardFailure("unsupported accountability manifest version")
        merged: dict[str, dict[str, str]] = {}
        for section in ("preserved", "campaign"):
            values = payload.get(section, {})
            if not isinstance(values, Mapping):
                raise GuardFailure(f"manifest section is not an object: {section}")
            for item, evidence in values.items():
                if not isinstance(item, str) or not isinstance(evidence, Mapping):
                    raise GuardFailure("malformed accountability manifest entry")
                state = evidence.get("state")
                digest = evidence.get("sha3_512")
                if state not in {"MODIFIED", "UNTRACKED"} or not isinstance(digest, str):
                    raise GuardFailure("manifest entry lacks bounded state/digest")
                if len(digest) != 128 or any(ch not in "0123456789abcdef" for ch in digest):
                    raise GuardFailure("manifest digest is not lowercase SHA3-512")
                merged[item] = {"state": state, "sha3_512": digest}
        return merged
    except (OSError, json.JSONDecodeError) as error:
        raise GuardFailure("accountability manifest cannot be read") from error


def accountability_evidence(manifest_path: Path) -> dict[str, Any]:
    """Compare current dirty work with an explicit preserved/campaign manifest."""

    expected = _manifest(manifest_path)
    current = _status()
    new = sorted(set(current) - set(expected))
    lost = sorted(set(expected) - set(current))
    mutated = sorted(
        path
        for path in set(current) & set(expected)
        if current[path] != expected[path]
    )
    status = "PASS" if not new and not lost and not mutated else "FAIL"
    return {
        "NEW_UNACCOUNTED_DIRTY_PATH": new,
        "LOST_PRESERVED_DIRTY_PATH": lost,
        "UNEXPECTED_MUTATION_OF_PRESERVED_PATH": mutated,
        "DIRTY_WORK_ACCOUNTABILITY_STATUS": status,
    }


def capture_manifest(path: Path) -> None:
    """Write an explicit, reviewable baseline for currently dirty work."""

    records = _status()
    payload = {"version": MANIFEST_VERSION, "preserved": records, "campaign": {}}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _print_parity(evidence: ParityEvidence) -> None:
    for key, value in (
        ("LOCAL_HEAD", evidence.local),
        ("TRACKING_HEAD", evidence.tracking),
        ("REMOTE_OPERATING_HEAD", evidence.remote_operating),
        ("REMOTE_MAIN_HEAD", evidence.remote_main),
        ("MERGE_BASE", evidence.merge_base),
        ("AHEAD_MAIN", evidence.ahead),
        ("BEHIND_MAIN", evidence.behind),
        ("OPEN_CONVERGENCE_PR", evidence.open_pr),
        ("BRANCH_CONVERGENCE_STATUS", evidence.status),
    ):
        print(f"{key}={value}")


def main(argv: Sequence[str] | None = None) -> int:
    """Run parity and optional dirty-work checks; no Git mutation is possible."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operating-branch", default=DEFAULT_OPERATING_BRANCH)
    parser.add_argument("--remote", default=DEFAULT_REMOTE)
    parser.add_argument("--base-branch", default="main")
    parser.add_argument("--dirty-manifest", type=Path)
    parser.add_argument("--capture-manifest", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.capture_manifest:
            capture_manifest(args.capture_manifest)
            print(f"ACCOUNTABILITY_MANIFEST={args.capture_manifest}")
        evidence = parity_evidence(args.operating_branch, args.remote, args.base_branch)
        _print_parity(evidence)
        status = evidence.status
        if args.dirty_manifest:
            dirty = accountability_evidence(args.dirty_manifest)
            for key in (
                "NEW_UNACCOUNTED_DIRTY_PATH",
                "LOST_PRESERVED_DIRTY_PATH",
                "UNEXPECTED_MUTATION_OF_PRESERVED_PATH",
            ):
                print(f"{key}={json.dumps(dirty[key], separators=(',', ':'))}")
            print(f"DIRTY_WORK_ACCOUNTABILITY_STATUS={dirty['DIRTY_WORK_ACCOUNTABILITY_STATUS']}")
            if dirty["DIRTY_WORK_ACCOUNTABILITY_STATUS"] == "FAIL":
                status = "FAIL"
        return 0 if status in {"PASS", "PENDING"} else 1
    except GuardFailure as error:
        print(f"BRANCH_CONVERGENCE_STATUS=FAIL")
        print(f"GUARD_ERROR={error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: branch parity and dirty-work accountability guard
# VERSION: v1.0.1-R1D-B0F-REPOSITORY-CONVERGENCE-R1
# AUTHORITY BOUNDARY: evidence classification only; no Git mutation authority
# TENANT POSTURE: repository-level; no tenant data
# FAIL-CLOSED POSTURE: mismatches and unaccounted dirty work deny closure
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
