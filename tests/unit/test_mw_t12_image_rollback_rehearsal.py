"""TITLE: MW-T12 immutable local Docker image rollback certificate.
VERSION: v1.2.0-STRUCTURED-IMAGE-STATE-DENIAL-TEST
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Certify image labels and config hashes, precise three-phase image
         identity, one durable synthetic volume, fail-closed reads and
         mandatory cleanup without invoking Docker or altering live EOS.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_mw_t12_image_rollback_rehearsal.py
COLLABORATION / OWNERSHIP: Existing MW-T12 source archive and synthetic
         fixture contracts, no second tenant/session authority.
CERTIFICATION / UPDATE DATE: 2026-11-24.
CHANGELOG: v1.2.0-STRUCTURED-IMAGE-STATE-DENIAL-TEST
           verifies malformed or missing fixture JSON fails with a safe
           fixed error, removes the owned EOS container and never emits
           an image execution PASS or leaks synthetic actor records.
CHANGELOG: v1.1.0-EXACT-GIT-DOCKER-CONTEXT-PROVENANCE-TEST
           refuses a differing Dockerfile, dependency lock or runtime
           source blob rather than merely trusting a labelled local image;
           fakes exact Git blob reads and runs no Docker process.
CHANGELOG: v1.0.0-DISPOSABLE-IMAGE-ROLLBACK-FAILURE-TESTS covers
           local-only image admission, expected SHA labels/config digest,
           current/historical/current rollout order, single volume, no
           intermediate reseeding, bounded Docker error response,
           preflight failures and cleanup-before-certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Entirely mocked commands and synthetic data.
TENANT BOUNDARY: No MongoDB, Docker daemon, cloud or canonical tenant contacted.
AUTHORITY BOUNDARY: Test certificate only; no release or production authority.
FINANCIAL AUTHORITY BOUNDARY: None.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import re
from types import SimpleNamespace

import pytest

from tools.eos.ops import mw_t12_image_rollback_rehearsal as operator
from tools.eos.ops.mw_t12_local_eos_recovery import MWRecoveryError


CURRENT = "a" * 40
OLDER = "b" * 40
CURRENT_ID = "sha256:" + "c" * 64
OLDER_ID = "sha256:" + "d" * 64


def test_image_provenance_requires_exact_image_id_revision_and_drill(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def docker(*args: str, **kwargs: object) -> str:
        if args[:2] != ("image", "inspect"):
            raise AssertionError("unexpected Docker action")
        if args[-1] != "synthetic:local":
            raise AssertionError("unexpected Docker reference")
        field = args[3]
        if field == "{{.Id}}":
            return CURRENT_ID
        if operator.SOURCE_LABEL in field:
            return CURRENT
        if operator.DRILL_LABEL in field:
            return "synthetic-drill"
        raise AssertionError("unexpected image field")

    monkeypatch.setattr(operator, "_docker", docker)
    assert operator._image_identity(
        "synthetic:local", CURRENT, "synthetic-drill"
    ) == CURRENT_ID
    with pytest.raises(MWRecoveryError, match="IMAGE_SOURCE_ATTESTATION_INVALID"):
        operator._image_identity("synthetic:local", OLDER, "synthetic-drill")
    with pytest.raises(MWRecoveryError, match="IMAGE_SOURCE_ATTESTATION_INVALID"):
        operator._image_identity("synthetic:local", CURRENT, "other-drill")


def test_docker_build_context_must_equal_historical_git_objects(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    source = tmp_path / "stage"
    paths = (
        "Dockerfile.eos", "requirements.txt",
        "tools/eos/api/server.py", "tools/eos/kernel/db.py",
    )
    for relative in paths:
        item = source / relative
        item.parent.mkdir(parents=True, exist_ok=True)
        item.write_bytes(("immutable:" + relative).encode("ascii"))

    def git(args: list[str], **_kwargs: object) -> SimpleNamespace:
        assert args[0:2] == ["git", "show"]
        assert args[2].startswith(CURRENT + ":")
        return SimpleNamespace(
            stdout=("immutable:" + args[2].split(":", 1)[1]).encode("ascii")
        )

    monkeypatch.setattr(subprocess, "run", git)
    operator._verify_context(checkout, source, CURRENT)
    (source / "Dockerfile.eos").write_bytes(b"unverified Dockerfile modification")
    with pytest.raises(MWRecoveryError, match="IMAGE_GIT_CONTEXT_PROVENANCE_MISMATCH"):
        operator._verify_context(checkout, source, CURRENT)


def test_docker_cli_failure_is_redacted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(*_args: object, **_kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(returncode=1, stdout=b"", stderr=b"SECRET=do-not-log")

    monkeypatch.setattr(operator.subprocess, "run", fake_run)
    with pytest.raises(MWRecoveryError) as failure:
        operator._docker("image", "inspect", "private", capture=True)
    assert failure.value.code == "IMAGE_DOCKER_IMAGE_FAILED"
    assert "SECRET" not in failure.value.code


def _mock_rehearsal(
    monkeypatch: pytest.MonkeyPatch,
    events: list[tuple[str, ...]],
    fail_historical: bool = False,
    fail_cleanup: bool = False,
) -> None:
    monkeypatch.setattr(operator, "_admit_rollback_candidate",
                        lambda target: (CURRENT, target))
    monkeypatch.setattr(operator, "_certified_source_revision", lambda: CURRENT)
    monkeypatch.setattr(operator, "_free_port", lambda: 27053)
    monkeypatch.setattr(operator, "_stage_revision", lambda *args: None)
    monkeypatch.setattr(operator, "_verify_context", lambda *args: None)
    monkeypatch.setattr(operator, "_wait_mongo", lambda port: events.append(("primary",)))
    monkeypatch.setattr(operator, "_init_owned_replica",
                        lambda *args: events.append(("replinit",)))
    monkeypatch.setattr(
        operator, "_build_image",
        lambda _stage, tag, sha, _drill: (
            events.append(("build", sha)), CURRENT_ID if sha == CURRENT else OLDER_ID
        )[1],
    )
    monkeypatch.setattr(
        operator, "_image_identity",
        lambda _tag, sha, _drill: CURRENT_ID if sha == CURRENT else OLDER_ID,
    )
    monkeypatch.setattr(Path, "is_file", lambda self: True)
    monkeypatch.setattr(operator, "_fingerprint_fixture",
                        lambda *args: "e" * 64)

    def docker(*args: str, **_kwargs: object) -> str:
        events.append(tuple(args[:3]))
        if args[:2] == ("image", "inspect") and args[2] == operator.MONGO_IMAGE:
            return ""
        if fail_cleanup and args[:2] == ("volume", "rm"):
            raise MWRecoveryError("IMAGE_DOCKER_VOLUME_FAILED")
        return ""

    monkeypatch.setattr(operator, "_docker", docker)

    def fixture(_script: Path, action: str, state: Path,
                env: dict[str, str], _cwd: Path) -> None:
        events.append(("fixture", action))
        if action == "seed":
            state.write_text(json.dumps({
                "database_name": env["BROWSER_CERT_MONGO_DATABASE"],
                "tenant_id": "browser-tenant-synthetic",
            }), encoding="utf-8")

    monkeypatch.setattr(operator, "_run_fixture", fixture)

    def phase(_name: str, _image: str, _network: str, _database: str,
              _secret: str, _state: Path, _fixture: Path,
              _environment: dict[str, str], _baseline: str, revision: str) -> None:
        events.append(("phase", revision))
        if revision == OLDER and fail_historical:
            raise MWRecoveryError("IMAGE_EXACT_HTTP_DENIED")

    monkeypatch.setattr(operator, "_verify_phase", phase)


def test_three_images_one_volume_no_reseed_and_cleanup_before_pass(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    events: list[tuple[str, ...]] = []
    _mock_rehearsal(monkeypatch, events)
    assert operator.rehearse_image(OLDER) == 0
    assert [event[1] for event in events if event[0] == "build"] == [
        CURRENT, OLDER,
    ]
    assert [event[1] for event in events if event[0] == "phase"] == [
        CURRENT, OLDER, CURRENT,
    ]
    assert [event[1] for event in events if event[0] == "fixture"] == [
        "seed", "verify-seed", "cleanup",
    ]
    assert len([event for event in events if event[:2] == ("volume", "create")]) == 1
    assert len([event for event in events if event[:2] == ("volume", "rm")]) == 1
    assert events.index(("fixture", "cleanup")) < events.index(
        next(event for event in events if event[:2] == ("volume", "rm"))
    )
    result = capsys.readouterr().out
    assert "MW_T12_IMAGE_ROLLBACK_READBACK=PASS" in result
    assert "MW_T12_IMAGE_SINGLE_DATA_VOLUME=PASS" in result
    assert "MW_T12_PRODUCTION_IMAGE_ROLLBACK_CERTIFIED=FALSE" in result


def test_historical_http_failure_cleans_ownership_and_never_passes(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    events: list[tuple[str, ...]] = []
    _mock_rehearsal(monkeypatch, events, fail_historical=True)
    assert operator.main(["--rehearse", OLDER]) == 2
    assert ("fixture", "cleanup") in events
    assert any(event[:2] == ("network", "rm") for event in events)
    assert any(event[:2] == ("volume", "rm") for event in events)
    output = capsys.readouterr().out
    assert "MW_T12_IMAGE_REHEARSAL=FAIL_CLOSED" in output
    assert "MW_T12_IMAGE_ROLLBACK_READBACK=PASS" not in output


def test_cleanup_failure_withholds_certification_even_when_phase_passed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    events: list[tuple[str, ...]] = []
    _mock_rehearsal(monkeypatch, events, fail_cleanup=True)
    assert operator.main(["--rehearse", OLDER]) == 2
    output = capsys.readouterr().out
    assert "MW_T12_ERROR=IMAGE_OWNED_VOLUME_CLEANUP_FAILED" in output
    assert "MW_T12_IMAGE_ROLLBACK_READBACK=PASS" not in output


def test_missing_sha_denied_before_any_docker_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(operator, "_docker", lambda *a, **kw: pytest.fail("Docker called"))
    with pytest.raises(MWRecoveryError, match="IMAGE_ROLLBACK_FULL_SHA_REQUIRED"):
        operator.rehearse_image("not-a-full-sha")


def test_corrupt_image_phase_fixture_state_rejects_before_auth_and_cleans(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    state_file = tmp_path / "state.json"
    state_file.write_text("{malformed-synthetic-state", encoding="utf-8")
    calls: list[str] = []
    monkeypatch.setattr(operator, "_free_port", lambda: 19096)
    monkeypatch.setattr(operator, "_image_identity", lambda *args: CURRENT_ID)
    monkeypatch.setattr(operator, "_verify_container_image", lambda *args: None)
    monkeypatch.setattr(operator, "_wait_eos", lambda *args: "http://127.0.0.1:19096")
    monkeypatch.setattr(
        operator, "_authenticate_unchanged",
        lambda *args: pytest.fail("authentication attempted with invalid state"),
    )
    monkeypatch.setattr(
        operator, "_docker",
        lambda *args, **kwargs: calls.append(args[0]),
    )
    with pytest.raises(MWRecoveryError, match="IMAGE_FIXTURE_STATE_UNAVAILABLE"):
        operator._verify_phase(
            "owned-name", "synthetic:local", "owned-network", "synthetic-data",
            "synthetic-secret", state_file, tmp_path / "fixture.py",
            {"MW_T12_IMAGE_DRILL": "owned"}, "f" * 64, CURRENT,
        )
    assert calls == ["run", "rm"]
    assert "MW_T12_IMAGE_VERSION_" not in capsys.readouterr().out


def test_live_image_phase_requires_expected_digest_auth_audit_and_owned_stop(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"database_name": "synthetic-data"}), encoding="utf-8")
    actions: list[str] = []
    monkeypatch.setattr(operator, "_free_port", lambda: 19096)
    monkeypatch.setattr(operator, "_image_identity", lambda *args: CURRENT_ID)
    monkeypatch.setattr(operator, "_verify_container_image",
                        lambda _name, digest: actions.append("image:" + digest))
    monkeypatch.setattr(operator, "_wait_eos", lambda *args: "http://127.0.0.1:19096")
    monkeypatch.setattr(operator, "_authenticate_unchanged",
                        lambda *args: actions.append("auth"))
    monkeypatch.setattr(operator, "_run_fixture",
                        lambda *args: actions.append("verify-seed"))
    monkeypatch.setattr(operator, "_fingerprint_fixture", lambda *args: "f" * 64)
    monkeypatch.setattr(operator, "_docker",
                        lambda *args, **kw: actions.append(args[0]))
    operator._verify_phase(
        "owned-name", "synthetic:local", "owned-network", "synthetic-data",
        "synthetic-secret", state, tmp_path / "fixture.py",
        {"MW_T12_IMAGE_DRILL": "owned"}, "f" * 64, CURRENT,
    )
    assert actions[:4] == ["run", "image:" + CURRENT_ID, "auth", "verify-seed"]
    assert actions[-1] == "rm"
    assert "MW_T12_IMAGE_VERSION_" + CURRENT[:12] + "=PASS" in capsys.readouterr().out


# ARTIFACT: tests/unit/test_mw_t12_image_rollback_rehearsal.py
# VERSION: v1.2.0-STRUCTURED-IMAGE-STATE-DENIAL-TEST
# AUTHORITY BOUNDARY: Synthetic Docker command proof only.
# TENANT POSTURE: No live Docker or production persistence.
# FAIL-CLOSED POSTURE: Failures, wrong provenance and cleanup deny PASS.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
