"""TITLE: MW-T12 dormant SSM secret-backed ECS task registration contract.
VERSION: v1.0.0-EXACT-REVISION-IDEMPOTENCE-REGRESSION
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Certify initial and replay-safe task definition metadata registration
         without launching ECS compute, exposing secrets or accepting drift.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_mw_t12_secure_task_registration.py
COLLABORATION / OWNERSHIP: Existing MW-T12 task definition registrar, ECR
         provenance and guarded ECS readback implementation.
CERTIFICATION / UPDATE DATE: 2026-11-25.
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

import pytest

from tools.eos.ops import mw_t12_task_definition_admission as target


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


# ARTIFACT: tests/unit/test_mw_t12_secure_task_registration.py
# VERSION: v1.0.0-EXACT-REVISION-IDEMPOTENCE-REGRESSION
# AUTHORITY BOUNDARY: Mocked ECS metadata registration only; no compute.
# TENANT POSTURE: No live tenant database, role or secret access.
# FAIL-CLOSED POSTURE: Unknown revisions or settings deny registration.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
