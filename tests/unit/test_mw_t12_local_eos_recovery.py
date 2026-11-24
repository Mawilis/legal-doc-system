"""TITLE: MW-T12 isolated Headquarters recovery evidence certificate.
VERSION: v1.2.1-ROLLBACK-COMMIT-VS-BLOB-PROOF-FIX
AUTHORITY: WILSY OS Core Governance; synthetic test-only proof.
EPITOME: Certify the existing local recovery operator checks authenticated
         browser evidence for every Headquarters viewport before success.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_mw_t12_local_eos_recovery.py
COLLABORATION / OWNERSHIP: The MW-T12 operator owns loopback replica lifecycle;
         Playwright owns assertions, network evidence and screen captures.
CERTIFICATION / UPDATE DATE: 2026-11-24.
CHANGELOG: v1.2.1-ROLLBACK-COMMIT-VS-BLOB-PROOF-FIX distinguishes
           the immutable commit-object type query from historical source
           blob queries when inspecting observed read-only Git commands.
           Keeps exact source-file coverage and ancestor-only assertions.
CHANGELOG: v1.2.0-ROLLBACK-CANDIDATE-READONLY-ADMISSION-CERT
           proves strict old-commit ancestry and presence of required
           immutable EOS/browser source files. Denies equal, malformed,
           missing and divergent revisions without invoking git writes.
CHANGELOG: v1.1.0-EXACT-HEAD-REVISION-FAIL-CLOSED-CERT verifies clean
           source revision admission and fail-closed rejection of changed,
           dirty, foreign-root, invalid and unavailable source proof. These
           fixtures never invoke real Git mutations, MongoDB or EOS.
CHANGELOG: v1.0.0-FOUR-VIEWPORT-EVIDENCE-FAIL-CLOSED-TEST adds synthetic
           positive, missing viewport, browser failure, foreign fixture,
           missing authenticated readback and absent screenshot tests.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No real tokens, users, tenants or work records.
TENANT BOUNDARY: Only temporary test fixture artifacts are used.
AUTHORITY BOUNDARY: Tests evidence admission, not production rollback or IAM.
FINANCIAL AUTHORITY BOUNDARY: No financial execution.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.eos.ops.mw_t12_local_eos_recovery import (
    MWRecoveryError,
    _certified_source_revision,
    _admit_rollback_candidate,
    ROLLBACK_REQUIRED_PATHS,
    _verify_headquarters_evidence,
)

VIEWPORTS = ((1440, 900), (1760, 1000), (1024, 900), (390, 844))


def _git_result_mock(monkeypatch: pytest.MonkeyPatch, *,
                     sha: str = "a" * 40, dirty: bool = False,
                     foreign: bool = False, unavailable: bool = False) -> None:
    """Emulate bounded read-only Git responses without modifying a checkout."""
    def read(args: list[str], **kwargs: object) -> SimpleNamespace:
        assert args[0] == "git"
        assert kwargs.get("check") is True
        assert kwargs.get("capture_output") is True
        if unavailable:
            raise subprocess.CalledProcessError(128, args)
        if args[1:] == ["rev-parse", "--show-toplevel"]:
            output = "/unrelated/repository" if foreign else str(Path.cwd())
        elif args[1:] == ["rev-parse", "--verify", "HEAD^{commit}"]:
            output = sha
        elif args[1:] == ["status", "--porcelain=v1", "--untracked-files=no"]:
            output = " M tools/eos/api/server.py" if dirty else ""
        else:
            raise AssertionError("Unexpected Git request")
        return SimpleNamespace(stdout=output + "\n")
    monkeypatch.setattr(subprocess, "run", read)


def test_exact_head_clean_revision_is_admitted(monkeypatch: pytest.MonkeyPatch) -> None:
    _git_result_mock(monkeypatch)
    assert _certified_source_revision() == "a" * 40


@pytest.mark.parametrize("flags,expected", [
    ({"dirty": True}, "SOURCE_TRACKED_WORKTREE_DIRTY"),
    ({"foreign": True}, "SOURCE_REPOSITORY_ROOT_REQUIRED"),
    ({"sha": "not-a-commit"}, "SOURCE_COMMIT_INVALID"),
    ({"unavailable": True}, "SOURCE_REVISION_UNAVAILABLE"),
])
def test_uncertified_source_revision_fails_closed(
    monkeypatch: pytest.MonkeyPatch, flags: dict[str, object], expected: str,
) -> None:
    _git_result_mock(monkeypatch, **flags)
    with pytest.raises(MWRecoveryError, match=expected):
        _certified_source_revision()



def test_versioned_rollback_candidate_is_strict_ancestor_with_required_sources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only immutable Git reads can admit a historical rollback candidate."""
    older = "b" * 40
    current = "a" * 40
    calls = []

    def git(args: list[str], **kwargs: object) -> SimpleNamespace:
        calls.append(args)
        assert args[0] == "git"
        assert kwargs.get("capture_output") is True
        assert kwargs.get("check") is True
        if args[1:] == ["rev-parse", "--show-toplevel"]:
            return SimpleNamespace(stdout=str(Path.cwd()) + "\n")
        if args[1:] == ["rev-parse", "--verify", "HEAD^{commit}"]:
            return SimpleNamespace(stdout=current + "\n")
        if args[1:] == ["status", "--porcelain=v1", "--untracked-files=no"]:
            return SimpleNamespace(stdout="")
        if args[1:] == ["cat-file", "-t", older]:
            return SimpleNamespace(stdout="commit\n")
        if args[1:] == ["merge-base", "--is-ancestor", older, current]:
            return SimpleNamespace(stdout="")
        if args[1:3] == ["cat-file", "-t"] and args[3].startswith(older + ":"):
            return SimpleNamespace(stdout="blob\n")
        raise AssertionError("Unexpected or mutating Git command")

    monkeypatch.setattr(subprocess, "run", git)
    assert _admit_rollback_candidate(older) == (current, older)
    assert ["git", "cat-file", "-t", older] in calls
    asserted = {
        call[3].split(":", 1)[1] for call in calls
        if len(call) == 4
        and call[1:3] == ["cat-file", "-t"]
        and call[3].startswith(older + ":")
    }
    assert asserted == set(ROLLBACK_REQUIRED_PATHS)
    assert all(call[1] in {"rev-parse", "status", "cat-file", "merge-base"} for call in calls)


@pytest.mark.parametrize("target, expected", [
    ("short", "ROLLBACK_TARGET_FULL_SHA_REQUIRED"),
    ("a" * 40, "ROLLBACK_TARGET_MUST_PRECEDE_HEAD"),
])
def test_rollback_target_invalid_or_same_head_denied(
    monkeypatch: pytest.MonkeyPatch, target: str, expected: str,
) -> None:
    _git_result_mock(monkeypatch)
    with pytest.raises(MWRecoveryError, match=expected):
        _admit_rollback_candidate(target)


@pytest.mark.parametrize("scenario, expected", [
    ("noncommit", "ROLLBACK_TARGET_NOT_COMMIT"),
    ("diverged", "ROLLBACK_TARGET_NOT_ANCESTOR"),
    ("missing_source", "ROLLBACK_SOURCE_PROOF_UNAVAILABLE"),
])
def test_rollback_source_or_ancestry_failure_denied(
    monkeypatch: pytest.MonkeyPatch, scenario: str, expected: str,
) -> None:
    older = "b" * 40

    def git(args: list[str], **_kwargs: object) -> SimpleNamespace:
        if args[1:] == ["rev-parse", "--show-toplevel"]:
            return SimpleNamespace(stdout=str(Path.cwd()) + "\n")
        if args[1:] == ["rev-parse", "--verify", "HEAD^{commit}"]:
            return SimpleNamespace(stdout="a" * 40 + "\n")
        if args[1:] == ["status", "--porcelain=v1", "--untracked-files=no"]:
            return SimpleNamespace(stdout="")
        if args[1:] == ["cat-file", "-t", older]:
            return SimpleNamespace(stdout="blob\n" if scenario == "noncommit" else "commit\n")
        if args[1] == "merge-base":
            if scenario == "diverged":
                raise subprocess.CalledProcessError(1, args)
            return SimpleNamespace(stdout="")
        if args[1:3] == ["cat-file", "-t"]:
            if scenario == "missing_source":
                raise subprocess.CalledProcessError(128, args)
            return SimpleNamespace(stdout="blob\n")
        raise AssertionError("Unexpected Git call")

    monkeypatch.setattr(subprocess, "run", git)
    with pytest.raises(MWRecoveryError, match=expected):
        _admit_rollback_candidate(older)


def _evidence(directory: Path) -> None:
    """Create the exact expected synthetic browser-proof surface."""
    for width, height in VIEWPORTS:
        name = f"headquarters-{width}"
        (directory / f"{name}-network.json").write_text(
            json.dumps({
                "viewport": {"width": width, "height": height},
                "fixture": "DISPOSABLE_SYNTHETIC_SESSION",
                "founderMfaAcceptance": False,
                "network": [
                    {"path": "/api/my-work", "method": "GET", "status": 200},
                ],
                "browserErrors": [],
            }),
            encoding="utf-8",
        )
        for suffix in ("", "-ai-companion", "-record", "-readback"):
            (directory / f"{name}{suffix}.png").write_bytes(b"synthetic-test-pixel")


def test_complete_four_viewport_authenticated_evidence_admitted(tmp_path: Path) -> None:
    """Evidence emitted by all four browser widths admits recovery readback."""
    _evidence(tmp_path)
    _verify_headquarters_evidence(tmp_path)


@pytest.mark.parametrize("missing", [
    "headquarters-390-network.json",
    "headquarters-1440-readback.png",
])
def test_missing_browser_evidence_fails_closed(tmp_path: Path, missing: str) -> None:
    """Missing responsive or readback artifacts cannot certify MW-T12."""
    _evidence(tmp_path)
    (tmp_path / missing).unlink()
    with pytest.raises(MWRecoveryError, match="HEADQUARTERS_"):
        _verify_headquarters_evidence(tmp_path)


@pytest.mark.parametrize("field,value", [
    ("browserErrors", ["TypeError"]),
    ("fixture", "CANONICAL_WILSY_TENANT"),
    ("founderMfaAcceptance", True),
    ("network", [{"path": "/api/my-work", "method": "GET", "status": 403}]),
    ("viewport", {"width": 300, "height": 844}),
])
def test_invalid_or_unverified_browser_proof_rejected(
    tmp_path: Path, field: str, value: object,
) -> None:
    """Malformed, unauthorized or mislabelled evidence never passes."""
    _evidence(tmp_path)
    path = tmp_path / "headquarters-390-network.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document[field] = value
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(MWRecoveryError, match="HEADQUARTERS_"):
        _verify_headquarters_evidence(tmp_path)


def test_corrupted_browser_network_record_rejected(tmp_path: Path) -> None:
    """Invalid JSON must fail without inventing a successful readback."""
    _evidence(tmp_path)
    (tmp_path / "headquarters-1024-network.json").write_text(
        "{malformed", encoding="utf-8",
    )
    with pytest.raises(MWRecoveryError, match="HEADQUARTERS_NETWORK_EVIDENCE_INVALID"):
        _verify_headquarters_evidence(tmp_path)


# ARTIFACT: tests/unit/test_mw_t12_local_eos_recovery.py
# VERSION: v1.2.1-ROLLBACK-COMMIT-VS-BLOB-PROOF-FIX
# AUTHORITY BOUNDARY: Disposable test data and read-only certificate.
# TENANT POSTURE: No canonical WILSY database, actor or credentials.
# FAIL-CLOSED POSTURE: Missing or invalid proof denies certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
