"""TITLE: MW-T12 single-database rollback source continuity certificate.
VERSION: v1.1.0-EXACT-HTTP-SOURCE-RECORD-CONTINUITY-CERT
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Certify one disposable Mongo dataset, three exact source versions,
         independent durable readback and fail-closed audit evidence checks.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_mw_t12_same_data_rehearsal.py
COLLABORATION / OWNERSHIP: Existing fixture owns exact-tenant source records;
         current/older staged code must not create new database consumers.
CERTIFICATION / UPDATE DATE: 2026-11-24.
CHANGELOG: v1.1.0-EXACT-HTTP-SOURCE-RECORD-CONTINUITY-CERT
           verifies HTTP results carry the same explicitly seeded
           incident and assignment IDs and reject foreign/missing evidence;
           adds a bounded parser rejection for oversized responses.
CHANGELOG: v1.0.0-SAME-DATA-SOURCE-CONTINUITY-TEST validates one seed,
           current-to-older-to-restored exact revision order, unchanged
           database identity, record fingerprint rejection, expected HTTP
           permission boundaries, owned process stop and cleanup-before-PASS.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic actors, no real credentials or URIs.
TENANT BOUNDARY: All test state is UUID-scoped and read-only or mocked.
AUTHORITY BOUNDARY: No production artifact, migration or deployment change.
FINANCIAL AUTHORITY BOUNDARY: No financial execution.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from tools.eos.ops import mw_t12_same_data_rehearsal as operator
from tools.eos.ops.mw_t12_local_eos_recovery import MWRecoveryError

CURRENT = "a" * 40
OLDER = "b" * 40


def _actor_fixture(database: str) -> dict[str, object]:
    return {
        "tenant_id": "browser-tenant-test",
        "database_name": database,
        "system_incident_id": "synthetic-incident-id",
        "system_assignment_id": "synthetic-assignment-id",
        "actors": {
            "partner": {"access_token": "synthetic-partner"},
            "tenant_owner": {"access_token": "synthetic-owner"},
        },
        "system_actors": {
            "system_responder": {"access_token": "synthetic-responder"},
            "system_triage": {"access_token": "synthetic-triage"},
        },
    }


def test_three_versions_share_one_seed_and_cleanup_after_evidence(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(operator, "_guard", lambda: ("/fake/mongod", "/fake/node"))
    monkeypatch.setattr(operator, "_admit_rollback_candidate",
                        lambda sha: (CURRENT, sha))
    monkeypatch.setattr(operator, "_certified_source_revision", lambda: CURRENT)
    monkeypatch.setattr(operator, "_free_port", lambda: 27058)
    monkeypatch.setattr(operator, "_wait_primary", lambda *args: None)
    monkeypatch.setattr(operator, "_stage_revision", lambda *args: None)
    monkeypatch.setattr(operator, "_link_local_dependencies", lambda *args: None)
    monkeypatch.setattr(operator, "_fingerprint_fixture",
                        lambda *args: "d" * 64)
    monkeypatch.setattr(Path, "is_file", lambda self: True)
    fake_mongo = SimpleNamespace(poll=lambda: None)
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: fake_mongo)
    stopped = []
    monkeypatch.setattr(operator, "_stop_owned", lambda p: stopped.append(p))
    phases = []
    actions = []

    def fixture(_path, action, state, env, _cwd):
        actions.append(action)
        if action == "seed":
            Path(state).write_text(
                json.dumps(_actor_fixture(env["BROWSER_CERT_MONGO_DATABASE"])),
                encoding="utf-8",
            )

    def version(_stage, env, state, _fixture, revision, fingerprint):
        phases.append((revision, env["BROWSER_CERT_MONGO_URI"], fingerprint))
        assert Path(state).is_file()
        assert actions.count("seed") == 1
        assert "cleanup" not in actions

    monkeypatch.setattr(operator, "_run_fixture", fixture)
    monkeypatch.setattr(operator, "_certify_running_version", version)
    assert operator.rehearse_same_data(OLDER) == 0
    assert [step[0] for step in phases] == [CURRENT, OLDER, CURRENT]
    assert len({step[1] for step in phases}) == 1
    assert all(step[2] == "d" * 64 for step in phases)
    assert actions == ["seed", "verify", "cleanup"]
    assert stopped == [fake_mongo]
    output = capsys.readouterr().out
    assert "MW_T12_SAME_DATA_THREE_PHASE_READBACK=PASS" in output
    assert "MW_T12_SAME_DATA_IMMUTABLE_AUDIT_EVIDENCE=UNCHANGED" in output
    assert "MW_T12_VERSIONED_ROLLBACK_CERTIFIED=FALSE" in output


def test_source_failure_always_stops_mongo_and_never_emits_pass(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(operator, "_guard", lambda: ("/fake/mongod", "/fake/node"))
    monkeypatch.setattr(operator, "_admit_rollback_candidate",
                        lambda target: (CURRENT, target))
    monkeypatch.setattr(operator, "_free_port", lambda: 27058)
    monkeypatch.setattr(operator, "_wait_primary", lambda *args: None)
    monkeypatch.setattr(operator, "_fingerprint_fixture",
                        lambda *args: "d" * 64)
    monkeypatch.setattr(Path, "is_file", lambda self: True)
    process = SimpleNamespace(poll=lambda: None)
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: process)
    monkeypatch.setattr(operator, "_stop_owned", lambda p: None)
    monkeypatch.setattr(operator, "_run_fixture", lambda *args: None)
    monkeypatch.setattr(operator, "_stage_revision",
                        lambda *args: (_ for _ in ()).throw(
                            MWRecoveryError("SAME_DATA_TEST_SOURCE_MISSING")
                        ))
    assert operator.main(["--rehearse", OLDER]) == 2
    output = capsys.readouterr().out
    assert "MW_T12_SAME_DATA_THREE_PHASE_READBACK=PASS" not in output
    assert "MW_T12_ERROR=SAME_DATA_TEST_SOURCE_MISSING" in output


def test_unchanged_authority_requires_all_exact_http_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence = _actor_fixture("wilsy_l8_8m_r3_mwt12_continuity_test")
    observed = []

    def read(base, route, token, scope=None):
        observed.append((route, token, scope))
        if route == "/api/legal-operations/productive-work" and token == "synthetic-owner":
            return 403
        if route.endswith("mine") and token == "synthetic-triage":
            return 403
        return 200

    monkeypatch.setattr(operator, "_read_authorized", read)
    def records(_base, route, _token):
        return [{"incidentId": evidence["system_incident_id"]}] if (
            route.endswith("security-incidents")
        ) else [{"assignmentId": evidence["system_assignment_id"]}]
    monkeypatch.setattr(operator, "_read_records", records)
    operator._authenticate_unchanged("http://127.0.0.1:19095", evidence)
    assert len(observed) == 7
    assert all(scope == evidence["tenant_id"] for route, _, scope in observed[:3])
    monkeypatch.setattr(operator, "_read_records", lambda *args: [])
    with pytest.raises(MWRecoveryError, match="SAME_DATA_SOURCE_RECORD_ID_MISMATCH"):
        operator._authenticate_unchanged("http://127.0.0.1:19095", evidence)
    monkeypatch.setattr(operator, "_read_authorized", lambda *args: 200)
    with pytest.raises(MWRecoveryError, match="SAME_DATA_AUTHORIZATION_READBACK_FAILED"):
        operator._authenticate_unchanged("http://127.0.0.1:19095", evidence)


def test_different_database_or_actor_state_is_denied() -> None:
    fixture = _actor_fixture("wilsy_l8_8m_r3_mwt12_continuity_test")
    fixture["tenant_id"] = "wilsy"
    with pytest.raises(MWRecoveryError, match="SAME_DATA_FIXTURE_SCOPE_INVALID"):
        operator._authenticate_unchanged("http://127.0.0.1:19095", fixture)


def test_fingerprint_requires_bounded_sha3_digest(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        subprocess, "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stdout=b"0123456789abcdef" * 4,
        ),
    )
    assert operator._fingerprint_fixture(
        tmp_path / "fixture.py", tmp_path / "state.json", {}, tmp_path
    ) == "0123456789abcdef" * 4
    monkeypatch.setattr(
        subprocess, "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stdout=b"secret-invalid-digest",
        ),
    )
    with pytest.raises(MWRecoveryError, match="SAME_DATA_AUDIT_FINGERPRINT_INVALID"):
        operator._fingerprint_fixture(
            tmp_path / "fixture.py", tmp_path / "state.json", {}, tmp_path,
        )


def test_mutated_audit_records_fail_before_version_pass(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    stage = tmp_path / "source"
    stage.mkdir()
    state_file = tmp_path / "state.json"
    state_file.write_text(json.dumps(_actor_fixture("synthetic-db")), encoding="utf-8")
    process = SimpleNamespace(poll=lambda: None)
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(operator, "_free_port", lambda: 19095)
    monkeypatch.setattr(operator, "_health", lambda *args: None)
    monkeypatch.setattr(operator, "_authenticate_unchanged", lambda *args: None)
    monkeypatch.setattr(operator, "_run_fixture", lambda *args: None)
    monkeypatch.setattr(operator, "_fingerprint_fixture", lambda *args: "f" * 64)
    stopped = []
    monkeypatch.setattr(operator, "_stop_owned", lambda p: stopped.append(p))
    with pytest.raises(MWRecoveryError, match="SAME_DATA_AUDIT_EVIDENCE_MUTATED"):
        operator._certify_running_version(
            stage, {"BROWSER_CERT_MONGO_DATABASE": "synthetic-db"},
            state_file, tmp_path / "fixture.py", CURRENT, "d" * 64,
        )
    assert stopped == [process]
    assert "MW_T12_SAME_DATA_VERSION_" not in capsys.readouterr().out


# ARTIFACT: tests/unit/test_mw_t12_same_data_rehearsal.py
# VERSION: v1.1.0-EXACT-HTTP-SOURCE-RECORD-CONTINUITY-CERT
# AUTHORITY BOUNDARY: Synthetic local source-version continuity only.
# TENANT POSTURE: No external database or production actor.
# FAIL-CLOSED POSTURE: Missing or mutated source evidence denies success.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
