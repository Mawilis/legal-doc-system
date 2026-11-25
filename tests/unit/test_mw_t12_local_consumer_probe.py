"""TITLE: MW-T12 local Mongo consumer classification and privacy certificate.
VERSION: v1.0.0-LOCAL-SECRET-FREE-CLASSIFICATION-TESTS
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Verify no credential emission, exact Atlas target classification,
         loopback/other handling and no inference of running EOS secret.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_mw_t12_local_consumer_probe.py
COLLABORATION / OWNERSHIP: Existing MW-T12 read-only local listener/URI probe.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.0.0-LOCAL-SECRET-FREE-CLASSIFICATION-TESTS adds synthetic
           regression for missing, malformed and explicitly scoped URI cases;
           verifies listener inspection cannot reveal environment/argv.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic credentials only, no real URI.
TENANT BOUNDARY: No external database connections or data reads.
AUTHORITY BOUNDARY: Test does not attest running process MongoDB target.
FINANCIAL AUTHORITY BOUNDARY: No paid resource activation.
"""
from __future__ import annotations

import pytest

from tools.eos.ops import mw_t12_local_consumer_probe as probe


def test_atlas_srv_target_redacts_credentials_and_identity(capsys, monkeypatch):
    """Only identified shared target classification and digest are returned."""
    token = "synthetic-credential-never-log"
    uri = ("mongodb+srv://synthetic:" + token
           + "@legal-doc-test.xmlpwmq.mongodb.net/synthetic_db?retryWrites=true")
    info = probe.classify_uri(uri)
    assert info["target"] == "MW_T12_SHARED_TEST_ATLAS"
    assert info["transport"] == "SRV_TLS"
    monkeypatch.setenv("MONGODB_URI", uri)
    monkeypatch.setattr(probe, "local_listener_pids", lambda: [12345])
    probe.run()
    output = capsys.readouterr().out
    assert token not in output
    assert "synthetic_db" not in output
    assert "synthetic" not in output
    assert "12345" not in output
    assert "MW_T12_LIVE_EOS_RESOLVED_TARGET=NOT_VERIFIED" in output
    assert "MW_T12_ATLAS_WILDCARD_RETIREMENT=BLOCKED" in output


def test_atlas_shard_set_classified_independent_of_host_order():
    """Exact three-node Mongo URI classifies the existing shared test cluster."""
    raw = (
        "mongodb://synthetic:pw@" + ",".join(
            host + ":27017" for host in sorted(probe.ATLAS_SHARDS, reverse=True)
        ) + "/synthetic_db?tls=true"
    )
    result = probe.classify_uri(raw)
    assert result["target"] == "MW_T12_SHARED_TEST_ATLAS"
    assert result["host_count"] == "3"


def test_loopback_not_misidentified_as_atlas():
    """Local replica-set is not an Atlas network consumer proof."""
    result = probe.classify_uri("mongodb://127.0.0.1:27017/wilsy-os-dev")
    assert result["target"] == "LOOPBACK_MONGODB"


def test_other_atlas_target_remains_unverified():
    """A different SRV cluster cannot inherit source ownership."""
    result = probe.classify_uri("mongodb+srv://different.example.net/other")
    assert result["target"] == "OTHER_OR_UNVERIFIED"


@pytest.mark.parametrize("uri", [
    "", "not-a-uri", "mongodb+srv://two.example.com,three.example.com/db",
    "mongodb://localhost:99999/db", "mongodb://example.com:-1/db",
    "mongodb://example.com:abc/db", "mongodb://example.com/db\nLEAK",
])
def test_malformed_or_missing_uri_denied_without_content(uri: str):
    """Never echo the invalid original URI."""
    with pytest.raises(probe.ProbeDenied):
        probe.classify_uri(uri)


def test_listener_pid_query_uses_no_process_environment_or_argv(monkeypatch):
    """The local OS process probe is limited to lsof's PID-only selection."""
    invocations = []

    def fake_run(cmd, **kwargs):
        invocations.append(cmd)
        return type("Result", (), {
            "returncode": 0,
            "stdout": b"100\n100\n202\n",
        })()

    monkeypatch.setattr(probe.subprocess, "run", fake_run)
    assert probe.local_listener_pids() == [100, 202]
    assert invocations == [[
        "lsof", "-nP", "-tiTCP:9095", "-sTCP:LISTEN",
    ]]


def test_empty_shell_environment_is_not_treated_as_live_eos_denial(
    monkeypatch, capsys,
):
    """Unknown shell environment is evidence gap, not source downtime."""
    monkeypatch.delenv("MONGODB_URI", raising=False)
    monkeypatch.setattr(probe, "local_listener_pids", lambda: [])
    probe.run()
    output = capsys.readouterr().out
    assert "MW_T12_LOCAL_EOS_9095_LISTENER=ABSENT" in output
    assert "MW_T12_SHELL_MONGODB_URI_CLASSIFICATION=SHELL_MONGODB_URI_NOT_PRESENT" in output
    assert "MW_T12_LIVE_EOS_RESOLVED_TARGET=NOT_VERIFIED" in output


# ARTIFACT: tests/unit/test_mw_t12_local_consumer_probe.py
# VERSION: v1.0.0-LOCAL-SECRET-FREE-CLASSIFICATION-TESTS
# AUTHORITY BOUNDARY: Mocked local evidence read only; no cloud changes.
# TENANT POSTURE: Synthetic fixtures only.
# FAIL-CLOSED POSTURE: Shell target never certifies a live EOS process.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
