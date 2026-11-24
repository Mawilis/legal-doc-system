"""TITLE: MW-T12 versioned source executable rehearsal failure-path certificate.
VERSION: v1.0.1-OWNED-RUNTIME-DIRECTORY-FIX
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Validate isolated source provenance, non-mutating version switching,
         authenticated readback and mandatory temporary resource cleanup.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_mw_t12_versioned_rehearsal.py
COLLABORATION / OWNERSHIP: Existing MW-T12 recovery owns Mongo lifecycle,
         browser verifier owns synthetic actors, HTTP and durable readback.
CERTIFICATION / UPDATE DATE: 2026-11-24.
CHANGELOG: v1.0.1-OWNED-RUNTIME-DIRECTORY-FIX creates the
           same owner-scoped runtime directory the real rehearsal creates
           before invoking the unit-isolated Mongo/browser runner.
CHANGELOG: v1.0.0-ISOLATED-TWO-VERSION-RECOVERY-TEST checks version order,
           post-switch fail-closed behavior, immutable archive source proof,
           dependency-only staging, authenticated runner failure and owned
           process shutdown, all without a real EOS or MongoDB listener.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic source text and Git results only.
TENANT BOUNDARY: Temporary files and fake processes; no canonical tenant.
AUTHORITY BOUNDARY: Does not certify same-data rollback or release.
FINANCIAL AUTHORITY BOUNDARY: No financial execution.
"""
from __future__ import annotations

import io
from pathlib import Path
import subprocess
import tarfile
from types import SimpleNamespace

import pytest

from tools.eos.ops import mw_t12_versioned_rehearsal as operator
from tools.eos.ops.mw_t12_local_eos_recovery import MWRecoveryError


CURRENT = "a" * 40
OLDER = "b" * 40


def _isolated_admission(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(operator, "_guard", lambda: ("/fake/mongod", "/fake/node"))
    monkeypatch.setattr(operator, "_admit_rollback_candidate", lambda target: (CURRENT, target))
    monkeypatch.setattr(operator, "_certified_source_revision", lambda: CURRENT)
    monkeypatch.setattr(operator, "_link_local_dependencies", lambda *args: None)


def test_versioned_rehearsal_orders_current_then_historical_and_preserves_checkout(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    _isolated_admission(monkeypatch)
    stages = []
    runs = []

    def stage(sha: str, checkout: Path, destination: Path) -> None:
        assert checkout == Path.cwd().resolve()
        assert destination.is_dir()
        stages.append(sha)

    def authenticate(_binary: str, _node: str, sha: str, _stage: Path, owner: Path) -> None:
        assert owner.is_dir()
        runs.append(sha)

    monkeypatch.setattr(operator, "_stage_revision", stage)
    monkeypatch.setattr(operator, "_certify_staged_version", authenticate)
    assert operator.rehearse(OLDER) == 0
    assert stages == [CURRENT, OLDER]
    assert runs == [CURRENT, OLDER]
    output = capsys.readouterr().out
    assert "MW_T12_SOURCE_VERSION_SWITCH_EXECUTED=TRUE" in output
    assert "MW_T12_TWO_VERSION_AUTHENTICATED_READBACK=PASS" in output
    assert "MW_T12_SAME_DATA_ROLLBACK_CERTIFIED=FALSE" in output


def test_historical_failure_never_certifies_rollback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    _isolated_admission(monkeypatch)
    monkeypatch.setattr(operator, "_stage_revision", lambda *args: None)

    def verify(_binary: str, _node: str, sha: str, _stage: Path, _owner: Path) -> None:
        if sha == OLDER:
            raise MWRecoveryError("VERSION_AUTHENTICATED_BROWSER_FAILED")

    monkeypatch.setattr(operator, "_certify_staged_version", verify)
    assert operator.main(["--rehearse", OLDER]) == 2
    output = capsys.readouterr().out
    assert "MW_T12_ERROR=VERSION_AUTHENTICATED_BROWSER_FAILED" in output
    assert "MW_T12_VERSIONED_ROLLBACK_CERTIFIED=FALSE" in output
    assert "MW_T12_SOURCE_VERSION_SWITCH_EXECUTED=TRUE" not in output


def test_source_change_after_first_version_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _isolated_admission(monkeypatch)
    monkeypatch.setattr(operator, "_stage_revision", lambda *args: None)
    monkeypatch.setattr(operator, "_certify_staged_version", lambda *args: None)
    monkeypatch.setattr(operator, "_certified_source_revision", lambda: OLDER)
    with pytest.raises(MWRecoveryError, match="SOURCE_REVISION_CHANGED_DURING_DRILL"):
        operator.rehearse(OLDER)


def test_missing_local_dependencies_denies_execution(tmp_path: Path) -> None:
    checkout = tmp_path / "checkout"
    stage = tmp_path / "stage"
    checkout.mkdir()
    stage.mkdir()
    with pytest.raises(MWRecoveryError, match="VERSION_LOCAL_DEPENDENCIES_UNAVAILABLE"):
        operator._link_local_dependencies(checkout, stage)


def test_staged_dependencies_link_existing_local_packages_only(tmp_path: Path) -> None:
    checkout = tmp_path / "checkout"
    stage = tmp_path / "stage"
    for root in (checkout, stage):
        (root / "client").mkdir(parents=True)
    for name in ("node_modules", "client/node_modules"):
        (checkout / name).mkdir()
    operator._link_local_dependencies(checkout, stage)
    for name in ("node_modules", "client/node_modules"):
        assert (stage / name).is_symlink()
        assert (stage / name).resolve() == (checkout / name).resolve()


def test_archive_refuses_untrusted_links(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    archive_path = tmp_path / (OLDER + ".tar")

    def fake_git(args: list[str], **kwargs: object) -> SimpleNamespace:
        assert args[:3] == ["git", "archive", "--format=tar"]
        with tarfile.open(fileobj=kwargs["stdout"], mode="w") as tar:
            member = tarfile.TarInfo("unsafe-link")
            member.type = tarfile.SYMTYPE
            member.linkname = "/etc/passwd"
            tar.addfile(member)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_git)
    stage = tmp_path / "source"
    stage.mkdir()
    with pytest.raises(MWRecoveryError, match="VERSION_ARCHIVE_UNSAFE_MEMBER"):
        operator._stage_revision(OLDER, tmp_path, stage)
    assert not archive_path.exists()
    assert not (stage / "unsafe-link").exists()


def test_archive_blob_provenance_is_required(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    content = b"immutable-check"
    files = operator.ROLLBACK_REQUIRED_PATHS

    def fake_git(args: list[str], **kwargs: object) -> SimpleNamespace:
        if args[1] == "archive":
            with tarfile.open(fileobj=kwargs["stdout"], mode="w") as tar:
                for file in files:
                    member = tarfile.TarInfo(file)
                    member.size = len(content)
                    tar.addfile(member, io.BytesIO(content))
            return SimpleNamespace(returncode=0)
        assert args[1] == "show"
        return SimpleNamespace(stdout=b"different-source")
    monkeypatch.setattr(subprocess, "run", fake_git)
    stage = tmp_path / "source"
    stage.mkdir()
    with pytest.raises(MWRecoveryError, match="VERSION_SOURCE_PROVENANCE_MISMATCH"):
        operator._stage_revision(OLDER, tmp_path, stage)


def test_authenticated_runner_failure_stops_only_owned_mongo(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    stopped = []
    fake_mongo = SimpleNamespace(pid=101)
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: fake_mongo)
    monkeypatch.setattr(operator, "_free_port", lambda: 27051)
    monkeypatch.setattr(operator, "_wait_primary", lambda *args: None)
    monkeypatch.setattr(operator, "_stop_owned", lambda process: stopped.append(process))

    def failed_runner(args: list[str], **kwargs: object) -> SimpleNamespace:
        assert args[1:] == [operator.BROWSER_RUNNER, operator.BROWSER_SUITE]
        assert kwargs["cwd"] == tmp_path
        assert kwargs["env"]["MONGODB_URI"].startswith("mongodb://127.0.0.1:")
        assert kwargs["env"]["PYTHONPATH"] == str(tmp_path)
        return SimpleNamespace(returncode=1)

    monkeypatch.setattr(subprocess, "run", failed_runner)
    owner = tmp_path / "owned"
    owner.mkdir()
    with pytest.raises(MWRecoveryError, match="VERSION_AUTHENTICATED_BROWSER_FAILED"):
        operator._certify_staged_version("/fake/mongod", "/fake/node", OLDER, tmp_path, owner)
    assert stopped == [fake_mongo]


# ARTIFACT: tests/unit/test_mw_t12_versioned_rehearsal.py
# VERSION: v1.0.1-OWNED-RUNTIME-DIRECTORY-FIX
# AUTHORITY BOUNDARY: Synthetic failure-path tests, no live system mutation.
# TENANT POSTURE: No canonical or authenticated production principal.
# FAIL-CLOSED POSTURE: Historical proof or auth failure denies certificate.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
