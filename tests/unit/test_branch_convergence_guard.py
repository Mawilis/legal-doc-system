"""Direct certificate for the branch-convergence governance guard.

TITLE: WILSY OS Branch Convergence Guard Direct Certificate
VERSION: v1.0.0-R1D-B0F-REPOSITORY-CONVERGENCE-R1-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Independently exercises parity decisions and dirty-work accountability
         without GitHub, MongoDB, network, staging, or repository mutation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_branch_convergence_guard.py
COLLABORATION / OWNERSHIP: Tests the executable governance artifact only.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.0.0-R1 certifies parity, governed-PR pending, divergence, and
           preserved/new/lost/mutated dirty-work states.
COMPLIANCE: POPIA section 19; GDPR Article 32; audit evidence.
SECURITY / PRIVACY POSTURE: Uses deterministic fakes; no secrets or contents.
TENANT BOUNDARY: None; repository governance only.
AUTHORITY BOUNDARY: Certificate evidence only; no merge or Git mutation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.eos.governance import branch_convergence_guard as guard


def _evidence(status: str, *, open_pr: str = "NONE") -> guard.ParityEvidence:
    return guard.ParityEvidence("a", "a", "a", "m", "a", 0, 0, open_pr, status)


def test_parity_passes_only_when_operating_equals_main(monkeypatch) -> None:
    monkeypatch.setattr(guard, "_ref", lambda ref: "a" if ref != "origin/main" else "m")
    monkeypatch.setattr(guard, "_counts", lambda local, main: (0, 0, "a"))
    evidence = guard.parity_evidence()
    assert evidence.status == "PASS"


def test_ahead_requires_exact_open_governed_pr(monkeypatch) -> None:
    monkeypatch.setattr(guard, "_ref", lambda ref: "a" if ref != "origin/main" else "m")
    monkeypatch.setattr(guard, "_counts", lambda local, main: (2, 0, "m"))
    monkeypatch.setattr(guard, "_open_pr", lambda branch, base: "NONE")
    assert guard.parity_evidence().status == "FAIL"
    monkeypatch.setattr(guard, "_open_pr", lambda branch, base: "88")
    evidence = guard.parity_evidence()
    assert evidence.status == "PENDING"
    assert evidence.open_pr == "88"


def test_behind_and_diverged_fail(monkeypatch) -> None:
    monkeypatch.setattr(guard, "_ref", lambda ref: "a" if ref != "origin/main" else "m")
    monkeypatch.setattr(guard, "_open_pr", lambda branch, base: "88")
    monkeypatch.setattr(guard, "_counts", lambda local, main: (0, 1, "m"))
    assert guard.parity_evidence().status == "FAIL"
    monkeypatch.setattr(guard, "_counts", lambda local, main: (1, 1, "m") )
    assert guard.parity_evidence().status == "FAIL"


def test_tracking_mismatch_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        guard,
        "_ref",
        lambda ref: {"HEAD": "a", "origin/fg108o4b-knowledge-operating-room": "b", "origin/main": "m"}[ref],
    )
    monkeypatch.setattr(guard, "_counts", lambda local, main: (0, 0, "m"))
    assert guard.parity_evidence().status == "FAIL"


def test_dirty_accountability_detects_new_lost_and_mutated(tmp_path: Path, monkeypatch) -> None:
    files = {"preserved.txt": b"stable", "mutated.txt": b"before"}
    monkeypatch.setattr(
        guard,
        "_status",
        lambda: {
            "preserved.txt": {"state": "MODIFIED", "sha3_512": hashlib.sha3_512(files["preserved.txt"]).hexdigest()},
            "mutated.txt": {"state": "MODIFIED", "sha3_512": hashlib.sha3_512(b"after").hexdigest()},
            "new.txt": {"state": "UNTRACKED", "sha3_512": hashlib.sha3_512(b"new").hexdigest()},
        },
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "version": 1,
                "preserved": {
                    "preserved.txt": {"state": "MODIFIED", "sha3_512": hashlib.sha3_512(files["preserved.txt"]).hexdigest()},
                    "lost.txt": {"state": "UNTRACKED", "sha3_512": hashlib.sha3_512(b"lost").hexdigest()},
                    "mutated.txt": {"state": "MODIFIED", "sha3_512": hashlib.sha3_512(files["mutated.txt"]).hexdigest()},
                },
                "campaign": {},
            }
        ),
        encoding="utf-8",
    )
    result = guard.accountability_evidence(manifest)
    assert result["NEW_UNACCOUNTED_DIRTY_PATH"] == ["new.txt"]
    assert result["LOST_PRESERVED_DIRTY_PATH"] == ["lost.txt"]
    assert result["UNEXPECTED_MUTATION_OF_PRESERVED_PATH"] == ["mutated.txt"]
    assert result["DIRTY_WORK_ACCOUNTABILITY_STATUS"] == "FAIL"


def test_clean_preserved_manifest_passes(tmp_path: Path, monkeypatch) -> None:
    digest = hashlib.sha3_512(b"stable").hexdigest()
    monkeypatch.setattr(guard, "_status", lambda: {"stable.txt": {"state": "MODIFIED", "sha3_512": digest}})
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"version": 1, "preserved": {"stable.txt": {"state": "MODIFIED", "sha3_512": digest}}, "campaign": {}}), encoding="utf-8")
    result = guard.accountability_evidence(manifest)
    assert result["DIRTY_WORK_ACCOUNTABILITY_STATUS"] == "PASS"


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: branch convergence guard direct certificate
# VERSION: v1.0.0-R1D-B0F-REPOSITORY-CONVERGENCE-R1-CERT
# AUTHORITY BOUNDARY: direct governance evidence only
# TENANT POSTURE: repository-level; no tenant data
# FAIL-CLOSED POSTURE: negative parity and dirty-work cases are asserted
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
