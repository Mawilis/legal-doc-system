"""TITLE: MW-T12 dormant SSM secret-backed ECS task registration contract.
VERSION: v1.2.0-PRIVATE-ECR-AUTH-ISOLATION-CERT
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Certify initial and replay-safe task definition metadata registration
         without launching ECS compute, exposing secrets or accepting drift.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_mw_t12_secure_task_registration.py
COLLABORATION / OWNERSHIP: Existing MW-T12 task definition registrar, ECR
         provenance and guarded ECS readback implementation.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.2.0-PRIVATE-ECR-AUTH-ISOLATION-CERT checks isolated
           ECR login, ephemeral credential disposal and exact fail-closed
           AWS/Crane denial without registry or AWS mutations.
CHANGELOG: v1.1.0-RUNTIME-READINESS-SECURE-REVISION-CERT verifies
           current read-only runtime gate reopens both scoped secret-backed
           revisions, rejects altered image identity and cannot start compute.
CHANGELOG: v1.0.0-EXACT-REVISION-IDEMPOTENCE-REGRESSION adds mocked initial,
           existing, partial, and drift-denial tests for exact dormant SSM
           revisions 3/4; no live AWS or payment authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Mocked AWS and Git sources; no credentials read.
TENANT BOUNDARY: Synthetic-only no tenant records or production URI.
AUTHORITY BOUNDARY: Regression tests cannot deploy or authorize runtime tasks.
FINANCIAL AUTHORITY BOUNDARY: No compute spending; Kennel EOS exclusively.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.eos.ops import mw_t12_task_definition_admission as target
from tools.eos.ops import mw_t12_runtime_readiness as readiness


ARN_PREFIX = (
    "arn:aws:ecs:af-south-1:121014832643:task-definition/"
    "wilsy-mwt12-eos-nonproduction:"
)


def _mock_registration(monkeypatch, initial: int) -> dict:
    """Provide a deterministic AWS/Crane/Git boundary and track mutations."""
    state = {"revision_count": initial, "registrations": [],
             "verified": [], "compute_checks": 0}
    monkeypatch.setattr(target, "secure_plan", lambda profile: None)
    monkeypatch.setattr(target.source, "preflight",
                        lambda profile: "a" * 40)
    monkeypatch.setattr(target.source, "git",
                        lambda *args: "" if args == ("status", "--porcelain")
                        else "a" * 40)
    monkeypatch.setattr(target, "images",
                        lambda profile, head: ("HISTORICAL", "CURRENT"))
    monkeypatch.setattr(target, "no_compute",
                        lambda profile: state.__setitem__(
                            "compute_checks", state["compute_checks"] + 1))
    monkeypatch.setattr(target, "verify",
                        lambda profile, arn, expected: state["verified"].append(
                            (arn, expected["containerDefinitions"][0]["image"],
                             expected["containerDefinitions"][0]["secrets"]))
                        or int(arn.rsplit(":", 1)[-1]))

    def fake_aws(profile, *args):
        if args[:2] == ("ecs", "list-task-definitions"):
            return {"taskDefinitionArns": [
                ARN_PREFIX + str(i)
                for i in range(1, state["revision_count"] + 1)
            ]}
        if args[:2] == ("ecs", "register-task-definition"):
            state["revision_count"] += 1
            state["registrations"].append(state["revision_count"])
            return {"taskDefinition": {
                "taskDefinitionArn": ARN_PREFIX +
                str(state["revision_count"]),
            }}
        raise AssertionError("UNEXPECTED_AWS_OPERATION")

    monkeypatch.setattr(target, "aws", fake_aws)
    return state


def test_initial_secure_registration_reuses_two_dormant_revisions(
    monkeypatch,
) -> None:
    """Only 3/4 are registered, preserving original 1/2 without edits."""
    state = _mock_registration(monkeypatch, 2)
    target.register_secure("wilsy-legal-cert")
    assert state["registrations"] == [3, 4]
    assert state["revision_count"] == 4
    assert state["compute_checks"] >= 3
    assert [entry[0] for entry in state["verified"]] == [
        ARN_PREFIX + str(i) for i in (1, 2, 3, 4)
    ]
    assert state["verified"][0][2] == []
    assert state["verified"][1][2] == []
    assert all(row[2] == [{
        "name": "MONGODB_URI", "valueFrom": target.SSM_PARAMETER_ARN,
    }] for row in state["verified"][2:])


def test_already_registered_replay_never_mutates_metadata(monkeypatch) -> None:
    """Exact 3/4 readback must be idempotent and have no registration."""
    state = _mock_registration(monkeypatch, 4)
    target.register_secure("wilsy-legal-cert")
    assert state["registrations"] == []
    assert len(state["verified"]) == 4
    assert state["compute_checks"] >= 1


def test_partial_revision_three_is_resumed_exactly_once(monkeypatch) -> None:
    """A previously registered 3 is verified and only missing 4 is added."""
    state = _mock_registration(monkeypatch, 3)
    target.register_secure("wilsy-legal-cert")
    assert state["registrations"] == [4]
    assert len(state["verified"]) == 4


@pytest.mark.parametrize("starting_count", [0, 1, 5])
def test_unexpected_revision_inventory_refuses_registration(
    monkeypatch, starting_count: int,
) -> None:
    """Never race an unknown version history or overwrite existing revisions."""
    state = _mock_registration(monkeypatch, starting_count)
    with pytest.raises(target.AdmissionError,
                       match="SECURE_REGISTRATION_EXISTING_REVISIONS_DRIFT"):
        target.register_secure("wilsy-legal-cert")
    assert state["registrations"] == []


def test_registration_spec_preserves_exact_secret_and_no_task_role() -> None:
    """Synthetic SSM ARN alone is the only permitted connection injection."""
    spec = target.secure_definition("digest-pinned-synthetic-test")
    container = spec["containerDefinitions"][0]
    assert spec.get("taskRoleArn") is None
    assert container["readonlyRootFilesystem"] is True
    assert container["user"] == "10001:10001"
    assert container["secrets"] == [{
        "name": "MONGODB_URI",
        "valueFrom": target.SSM_PARAMETER_ARN,
    }]
    assert not any(
        item["name"] == "MONGODB_URI"
        for item in container["environment"]
    )


def test_runtime_gate_reads_both_secure_revisions_without_launch(monkeypatch) -> None:
    """Verify the exact owned SSM revisions before any ECS runtime claim."""
    seen = {"iam": 0, "reads": [], "contract": []}
    monkeypatch.setattr(readiness.registered, "secure_plan",
                        lambda profile: seen.__setitem__("iam", seen["iam"] + 1))
    def read_task(profile, revision):
        seen["reads"].append(revision)
        return {"taskDefinitionArn": ARN_PREFIX + str(revision)}
    monkeypatch.setattr(readiness, "task", read_task)
    def verify(profile, arn, expected):
        seen["contract"].append((arn, expected["containerDefinitions"][0]["image"],
                                  expected["containerDefinitions"][0]["secrets"]))
        return int(arn.rsplit(":", 1)[1])
    monkeypatch.setattr(readiness.registered, "verify", verify)

    readiness.verify_secure_task_revisions("synthetic", ("HISTORICAL", "CURRENT"))
    assert seen["iam"] == 1
    assert seen["reads"] == [3, 4]
    assert [x[0] for x in seen["contract"]] == [
        ARN_PREFIX + "3", ARN_PREFIX + "4"
    ]
    assert [x[1] for x in seen["contract"]] == ["HISTORICAL", "CURRENT"]
    assert all(x[2] == [{
        "name": "MONGODB_URI", "valueFrom": target.SSM_PARAMETER_ARN,
    }] for x in seen["contract"])


def test_runtime_gate_rejects_wrong_secure_revision_identity(monkeypatch) -> None:
    """Do not certify a task ARN not owned by the exact admission family."""
    monkeypatch.setattr(readiness.registered, "secure_plan", lambda profile: None)
    monkeypatch.setattr(readiness, "task", lambda profile, revision: {
        "taskDefinitionArn": ARN_PREFIX + "99",
    })
    monkeypatch.setattr(readiness.registered, "verify",
                        lambda *args: pytest.fail("Unexpected second read"))
    with pytest.raises(readiness.ReadinessError,
                       match="SECURE_TASK_IDENTITY_DRIFT"):
        readiness.verify_secure_task_revisions("synthetic",
                                               ("HISTORICAL", "CURRENT"))


def test_runtime_gate_rejects_secure_secret_or_image_drift(monkeypatch) -> None:
    """Independent task definition readback must certify its whole contract."""
    monkeypatch.setattr(readiness.registered, "secure_plan", lambda profile: None)
    monkeypatch.setattr(readiness, "task", lambda profile, revision: {
        "taskDefinitionArn": ARN_PREFIX + str(revision),
    })
    monkeypatch.setattr(readiness.registered, "verify", lambda *args: 0)
    with pytest.raises(readiness.ReadinessError,
                       match="SECURE_TASK_SPEC_OR_SECRET_DRIFT"):
        readiness.verify_secure_task_revisions("synthetic",
                                               ("HISTORICAL", "CURRENT"))


def test_private_ecr_crane_login_is_ephemeral_and_never_logs_token(monkeypatch) -> None:
    """Private registry reads must isolate credential config and use stdin."""
    secret = b"synthetic-secret-for-regression-only"
    observed = []
    image = target.source.URI + "@sha256:" + "a" * 64
    def fake_run(args, **kwargs):
        observed.append((list(args), dict(kwargs)))
        if args[:3] == ["aws", "ecr", "get-login-password"]:
            return SimpleNamespace(returncode=0, stdout=secret)
        if args[:3] == ["crane", "auth", "login"]:
            assert kwargs.get("input") == secret
            assert "--password-stdin" in args
            assert "--password" not in args
            return SimpleNamespace(returncode=0)
        if args[:2] == ["crane", "config"]:
            return SimpleNamespace(returncode=0, stdout=json.dumps({
                "os": "linux", "architecture": "amd64",
                "config": {"Labels": {"wilsy.mwt12.source_sha": "synthetic"}},
            }).encode())
        pytest.fail("UNEXPECTED_EXTERNAL_COMMAND")
    monkeypatch.setattr(target.subprocess, "run", fake_run)
    data = target.image_config(image, "wilsy-legal-cert")
    assert data["architecture"] == "amd64"
    assert len(observed) == 3
    assert all(x[1]["env"]["DOCKER_CONFIG"] == observed[0][1]["env"]["DOCKER_CONFIG"]
               for x in observed)
    path = Path(observed[0][1]["env"]["DOCKER_CONFIG"])
    assert not path.exists()
    assert all(secret.decode() not in " ".join(x[0]) for x in observed)


@pytest.mark.parametrize("failure_stage,expected_code", [
    ("aws", "ECR_PULL_AUTH_UNAVAILABLE"),
    ("login", "CRANE_ECR_AUTH_UNAVAILABLE"),
    ("config", "IMAGE_CONFIG_UNAVAILABLE"),
])
def test_private_ecr_transport_denials_are_safe_and_do_not_register(
    monkeypatch, failure_stage, expected_code,
) -> None:
    """Never register a task after missing ECR auth or image inspection."""
    calls = []
    def fake_run(args, **kwargs):
        calls.append(list(args))
        if args[0] == "aws":
            return SimpleNamespace(returncode=1 if failure_stage == "aws" else 0,
                                   stdout=b"safe-synthetic-token")
        if args[:3] == ["crane", "auth", "login"]:
            return SimpleNamespace(returncode=1 if failure_stage == "login" else 0)
        if args[:2] == ["crane", "config"]:
            return SimpleNamespace(returncode=1 if failure_stage == "config" else 0,
                                   stdout=b"{}")
        pytest.fail("UNEXPECTED_EXTERNAL_COMMAND")
    monkeypatch.setattr(target.subprocess, "run", fake_run)
    with pytest.raises(target.AdmissionError, match="^" + expected_code + "$"):
        target.image_config(target.source.URI + "@sha256:" + "a" * 64,
                            "wilsy-legal-cert")
    assert not any(args[:2] == ["aws", "ecs"] for args in calls)


# ARTIFACT: tests/unit/test_mw_t12_secure_task_registration.py
# VERSION: v1.2.0-PRIVATE-ECR-AUTH-ISOLATION-CERT
# AUTHORITY BOUNDARY: Mocked ECS metadata registration only; no compute.
# TENANT POSTURE: No live tenant database, role or secret access.
# FAIL-CLOSED POSTURE: Unknown revisions or settings deny registration.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
