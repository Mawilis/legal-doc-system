"""TITLE: WILSY OS Project Execution Domain Certificate
VERSION: v1.0.0-PROJECT-DEPENDENCY-STATE-CERT
AUTHORITY: Synthetic immutable task domain certificate only.
EPITOME: Validate task/subtask/milestone state, dependency syntax, fingerprints,
         revision CAS, terminal states and fail-closed mutation boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_task_registry.py
COLLABORATION / OWNERSHIP: ProjectTaskRegistry and Projects router.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-PROJECT-DEPENDENCY-STATE-CERT establishes source-domain tests.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic project and principal identities only.
TENANT BOUNDARY: No fallback tenant and no unverified record ownership.
AUTHORITY BOUNDARY: No employee assignment, IAM or workflow execution granted.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.saas.projects.project_task_registry import (
    ProjectTask, ProjectTaskError, ProjectTaskConflict, task_id_for_command,
)

NOW = datetime(2026, 11, 18, 10, tzinfo=timezone.utc)
PROJECT = "prj-" + "a" * 48
TASK = "ptk-" + "b" * 48


def task(**values: object) -> ProjectTask:
    """Return an immutable synthetic source task."""
    data = {
        "tenant_id": "tenant-a", "project_id": PROJECT, "task_id": TASK,
        "kind": "TASK", "parent_task_id": None, "title": "Governed work",
        "description": "Source-backed evidence", "status": "TODO",
        "assignee_principal_id": "participant-a", "due_date": "2026-12-01",
        "depends_on": (), "created_by_principal_id": "owner-a",
        "updated_by_principal_id": "owner-a",
        "created_at": NOW, "updated_at": NOW,
    }
    data.update(values)
    return ProjectTask(**data)


def test_task_integrity_and_immutable_transitions() -> None:
    """Transition evidence is source-validated with exact revisions."""
    original = task()
    assert len(original.fingerprint) == 128
    assert ProjectTask.hydrate(original.to_dict()) == original
    in_progress = original.transition(
        status="IN_PROGRESS", actor_principal_id="participant-a",
        expected_revision=1, occurred_at=NOW + timedelta(seconds=1),
    )
    finished = in_progress.transition(
        status="DONE", actor_principal_id="participant-a",
        expected_revision=2, occurred_at=NOW + timedelta(seconds=2),
    )
    assert (original.status, in_progress.status, finished.status) == (
        "TODO", "IN_PROGRESS", "DONE",
    )
    assert finished.revision == 3
    assert len({original.fingerprint, in_progress.fingerprint, finished.fingerprint}) == 3
    with pytest.raises(ProjectTaskConflict, match="TRANSITION_DENIED"):
        finished.transition(
            status="IN_PROGRESS", actor_principal_id="participant-a",
            expected_revision=3, occurred_at=NOW + timedelta(seconds=3),
        )
    with pytest.raises(ProjectTaskConflict, match="REVISION_CONFLICT"):
        original.transition(
            status="BLOCKED", actor_principal_id="participant-a",
            expected_revision=2, occurred_at=NOW + timedelta(seconds=1),
        )


def test_source_mutation_and_false_fingerprint_deny() -> None:
    """Forged completion, foreign fields and invalid fingerprints are rejected."""
    original = task()
    wrong = original.to_dict()
    wrong["status"] = "DONE"
    with pytest.raises(ProjectTaskError, match="FINGERPRINT_INVALID"):
        ProjectTask.hydrate(wrong)
    with pytest.raises(ProjectTaskError, match="RECORD_INVALID"):
        ProjectTask.hydrate({**original.to_dict(), "approved_by": "CEO"})


@pytest.mark.parametrize("changes", [
    {"tenant_id": "MASTER"}, {"tenant_id": "WILSY_ROOT"},
    {"project_id": "not-an-id"}, {"task_id": "wrong"},
    {"title": ""}, {"title": "  trimmed "},
    {"status": "SETTLED"}, {"kind": "FINANCIAL"},
    {"due_date": "2026-02-31"}, {"due_date": "tomorrow"},
    {"revision": 0}, {"revision": True},
    {"depends_on": ("ptk-" + "c" * 48, "ptk-" + "c" * 48)},
    {"depends_on": (TASK,)},
    {"parent_task_id": TASK},
    {"updated_at": NOW - timedelta(minutes=1)},
])
def test_reject_untrusted_project_task_state(changes: dict[str, object]) -> None:
    """Invalid graph, role, dates, state and revision never become source truth."""
    with pytest.raises(ProjectTaskError):
        task(**changes)


def test_milestone_cannot_be_nested_as_a_subtask() -> None:
    """Subtask hierarchy is explicit; milestones stay project-level."""
    with pytest.raises(ProjectTaskError, match="MILESTONE_PARENT_INVALID"):
        task(kind="MILESTONE", parent_task_id="ptk-" + "d" * 48)


def test_task_ids_are_stable_only_for_exact_command_origins() -> None:
    """No global task-ID allocation or cross-tenant idempotency collision."""
    one = task_id_for_command("tenant-a", PROJECT, "owner-a", "key-1")
    assert one.startswith("ptk-") and len(one) == 52
    assert one == task_id_for_command("tenant-a", PROJECT, "owner-a", "key-1")
    assert one != task_id_for_command("tenant-b", PROJECT, "owner-a", "key-1")
    assert one != task_id_for_command("tenant-a", PROJECT, "owner-a", "key-2")


# ARTIFACT: test_project_task_registry.py
# VERSION: v1.0.0-PROJECT-DEPENDENCY-STATE-CERT
# AUTHORITY BOUNDARY: domain-only, no membership/permission or persistence
# TENANT POSTURE: exact synthetic project and principal identifiers
# FAIL-CLOSED POSTURE: forged states, bad parent/dependencies and stale CAS deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
