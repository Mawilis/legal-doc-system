"""TITLE: WILSY OS Project Execution Domain Certificate
VERSION: v1.3.0-COMPLETED-SOURCE-PAGING-CERT
AUTHORITY: Synthetic immutable task domain certificate only.
EPITOME: Validate task/subtask/milestone state, dependency syntax, fingerprints,
         revision CAS, terminal states and fail-closed mutation boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_task_registry.py
COLLABORATION / OWNERSHIP: ProjectTaskRegistry and Projects router.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.3.0-COMPLETED-SOURCE-PAGING-CERT verifies filtered completion pages and exact-revision immutable actor/time, negative spoofing and bounded inputs.
CHANGELOG: v1.2.0-TASK-EVENT-READER-CERT certifies
bounded immutable event reads, strict source scoping, ISO datetime projection,
revision ordering and redaction of replay secrets.
CHANGELOG: v1.1.0-REVISIONED-TASK-EDIT-CERT certifies bounded
revisioned task editing, assignee changes, immutable dependency graph and
terminal editing denial without creating any IAM grant.
CHANGELOG: v1.3.0-COMPLETED-SOURCE-PAGING-CERT establishes source-domain tests.
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


def test_completed_history_filters_before_paging_and_proves_immutable_actor_time() -> None:
    """A completed row is only admitted alongside matching terminal evidence."""
    from tools.eos.saas.projects.project_task_registry import ProjectTaskRegistry

    done = task(
        status="DONE", revision=3, updated_by_principal_id="reviewer-a",
        updated_at=NOW + timedelta(microseconds=123456),
    )
    captured: dict[str, object] = {}

    class Cursor:
        def __init__(self, rows):
            self.rows = rows
        def sort(self, fields):
            captured["sort"] = fields
            return self
        def skip(self, value):
            captured["offset"] = value
            return self
        def limit(self, value):
            captured["limit"] = value
            return self.rows[:value]

    class Tasks:
        def find(self, query, *, session):
            assert session == "verified-session"
            captured["query"] = query
            return Cursor([done.to_dict()])

    class Events:
        def find_one(self, query, projection, *, session):
            captured["event_query"] = query
            assert session == "verified-session"
            assert "idempotency_key" not in projection
            return {
                "schema": "wilsy.project.task.event.v1",
                "actor_principal_id": "reviewer-a",
                "occurred_at": NOW + timedelta(microseconds=123000),
                "result_snapshot": {"status": "DONE"},
            }

    result, more = ProjectTaskRegistry(Tasks(), Events()).list_completed_page(
        tenant_id="tenant-a", project_id=PROJECT,
        session="verified-session", limit=1, offset=0,
        search="Governed", assignee_principal_id="participant-a",
        completion_order="NEWEST",
    )
    assert not more and len(result) == 1
    assert result[0]["completed_by_principal_id"] == "reviewer-a"
    assert result[0]["completed_at"] == done.updated_at.isoformat()
    assert captured["query"] == {
        "tenant_id": "tenant-a", "project_id": PROJECT, "status": "DONE",
        "assignee_principal_id": "participant-a",
        "title": {"$regex": "Governed", "$options": "i"},
    }
    assert captured["event_query"] == {
        "tenant_id": "tenant-a", "project_id": PROJECT,
        "task_id": TASK, "revision": 3,
        "event_type": "PROJECT_TASK_TRANSITIONED",
        "result_fingerprint": done.fingerprint,
    }
    assert captured["offset"] == 0
    assert captured["limit"] == 2


@pytest.mark.parametrize("record", [
    None,
    {"schema": "wilsy.project.task.event.v1", "actor_principal_id": "different",
     "occurred_at": NOW, "result_snapshot": {"status": "DONE"}},
    {"schema": "wilsy.project.task.event.v1", "actor_principal_id": "owner-a",
     "occurred_at": NOW + timedelta(seconds=2), "result_snapshot": {"status": "DONE"}},
    {"schema": "wilsy.project.task.event.v1", "actor_principal_id": "owner-a",
     "occurred_at": NOW, "result_snapshot": {"status": "IN_PROGRESS"}},
])
def test_completed_history_denies_missing_spoofed_or_changed_event(record) -> None:
    from tools.eos.saas.projects.project_task_registry import ProjectTaskRegistry
    done = task(status="DONE", revision=3)

    class Cursor:
        def sort(self, fields):
            return self
        def skip(self, amount):
            return self
        def limit(self, amount):
            return [done.to_dict()]

    class Tasks:
        def find(self, query, *, session):
            return Cursor()

    class Events:
        def find_one(self, query, projection, *, session):
            return record

    with pytest.raises(ProjectTaskError, match="COMPLETION_SOURCE_INVALID"):
        ProjectTaskRegistry(Tasks(), Events()).list_completed_page(
            tenant_id="tenant-a", project_id=PROJECT, session="verified-session",
        )


def test_completed_history_rejects_unbounded_or_unsafe_filter() -> None:
    from tools.eos.saas.projects.project_task_registry import ProjectTaskRegistry
    registry = ProjectTaskRegistry(object(), object())
    with pytest.raises(ProjectTaskError, match="FILTER_INVALID"):
        registry.list_completed_page(
            tenant_id="tenant-a", project_id=PROJECT,
            session="verified-session", search="a" * 121,
        )
    with pytest.raises(ProjectTaskError, match="PAGE_INVALID"):
        registry.list_completed_page(
            tenant_id="tenant-a", project_id=PROJECT,
            session="verified-session", offset=-1,
        )


def test_immutable_event_read_is_scoped_bounded_and_redacted() -> None:
    from tools.eos.saas.projects.project_task_registry import ProjectTaskRegistry

    source = task()
    record = {
        "schema": "wilsy.project.task.event.v1",
        "tenant_id": "tenant-a", "project_id": PROJECT, "task_id": TASK,
        "revision": 2, "event_type": "PROJECT_TASK_TRANSITIONED",
        "actor_principal_id": "owner-a", "occurred_at": NOW,
        "idempotency_key": "secret", "result_snapshot": {"status": "IN_PROGRESS", "private": True},
    }

    class EventCursor:
        def __init__(self):
            self.rows = [record]
        def sort(self, fields):
            assert fields == [("revision", -1)]
            return self
        def skip(self, count):
            assert count == 0
            return self
        def limit(self, count):
            assert count == 2
            return self.rows[:count]

    class Events:
        def find(self, query, projection, *, session):
            assert query == {"tenant_id": "tenant-a",
                             "project_id": PROJECT, "task_id": TASK}
            assert projection["_id"] == 0
            assert "idempotency_key" not in projection
            assert "result_snapshot" not in projection
            assert session == "verified-session"
            return EventCursor()

    class Tasks:
        def find_one(self, query, *, session):
            assert query["task_id"] == TASK
            return source.to_dict()

    registry = ProjectTaskRegistry(Tasks(), Events())
    items, more = registry.list_event_page(
        tenant_id="tenant-a", project_id=PROJECT, task_id=TASK,
        session="verified-session", limit=1, offset=0,
    )
    assert not more and len(items) == 1
    assert items[0]["occurred_at"] == NOW.isoformat()
    assert "idempotency_key" not in items[0]
    assert "result_snapshot" not in items[0]
    assert items[0]["event_type"] == "PROJECT_TASK_TRANSITIONED"
    assert items[0]["status_after"] == "IN_PROGRESS"


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


def test_task_revise_preserves_graph_and_denies_terminal_edits() -> None:
    """Source task changes are CAS-controlled without resetting lifecycle."""
    source = task()
    updated = source.revise(
        title="Updated task", description="New context", due_date=None,
        assignee_principal_id="other-current-participant",
        actor_principal_id="owner-a", expected_revision=1,
        occurred_at=NOW + timedelta(seconds=1),
    )
    assert updated.title == "Updated task"
    assert updated.assignee_principal_id == "other-current-participant"
    assert updated.due_date is None and updated.revision == 2
    assert updated.task_id == source.task_id
    assert updated.depends_on == source.depends_on
    assert updated.parent_task_id == source.parent_task_id
    with pytest.raises(ProjectTaskConflict, match="REVISION_CONFLICT"):
        updated.revise(
            title="Stale", description="", due_date=None,
            assignee_principal_id=None, actor_principal_id="owner-a",
            expected_revision=1, occurred_at=NOW + timedelta(seconds=2),
        )
    active = source.transition(
        status="IN_PROGRESS", actor_principal_id="owner-a",
        expected_revision=1, occurred_at=NOW + timedelta(seconds=1),
    )
    terminal = active.transition(
        status="DONE", actor_principal_id="owner-a",
        expected_revision=2, occurred_at=NOW + timedelta(seconds=2),
    )
    with pytest.raises(ProjectTaskConflict, match="TERMINAL_REVISION_DENIED"):
        terminal.revise(
            title="Rewrite completion", description="", due_date=None,
            assignee_principal_id=None, actor_principal_id="owner-a",
            expected_revision=3, occurred_at=NOW + timedelta(seconds=3),
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
# VERSION: v1.3.0-COMPLETED-SOURCE-PAGING-CERT
# AUTHORITY BOUNDARY: domain-only, no membership/permission or persistence
# TENANT POSTURE: exact synthetic project and principal identifiers
# FAIL-CLOSED POSTURE: forged states, bad parent/dependencies and stale CAS deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
