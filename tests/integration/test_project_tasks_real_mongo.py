"""TITLE: WILSY OS Project Work Execution Real-Mongo Certificate
VERSION: v1.3.0-COMPLETED-HISTORY-MONGO-CERT
AUTHORITY: Synthetic disposable replica-set source certification only.
EPITOME: Test nested work, milestone/dependency index, idempotent task CRUD,
         verified predecessor/child completion gates and exact tenant absence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_project_tasks_real_mongo.py
COLLABORATION / OWNERSHIP: Existing Projects disposable Mongo CI and
         ProjectTaskRegistry; no operator account or active tenant is touched.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.3.0-COMPLETED-HISTORY-MONGO-CERT confirms server-side completed pagination, newest/oldest ordering, source-backed event actor, cross-tenant empty read and filtered title search against disposable majority Mongo transactions.
CHANGELOG: v1.2.0-PREDECESSOR-READBACK-GATE-CERT proves
         blocked completion leaves persisted task, revision and audit
         unchanged; fresh majority readback verifies the predecessor
         transition to Done before the dependent may finish.
CHANGELOG: v1.1.0-PROJECT-TASK-EDIT-REPLAY-REPLICA-CERT certifies
audited task edits, assignee changes, deterministic replay and stale
revision rejection in an isolated disposable replica transaction.
CHANGELOG: v1.3.0-COMPLETED-HISTORY-MONGO-CERT proves source-backed
         dependency, subtask and lifecycle commands in majority transactions.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: All IDs and timestamps synthetic; no provider calls.
TENANT BOUNDARY: Exact tenant and project on each read, event and transition.
AUTHORITY BOUNDARY: Persistence tests only; API IAM verified separately.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.saas.projects.project_task_registry import (
    ProjectTask, ProjectTaskRegistry, ProjectTaskConflict, ProjectTaskNotFound,
    task_id_for_command,
)


def test_disposable_source_project_task_milestone_dependency_lifecycle() -> None:
    """Complete source-backed work requires predecessors and all active children."""
    uri = os.environ.get("TEST_PROJECTS_ACCOUNTABILITY_MONGO_URI")
    if not uri:
        pytest.skip("Disposable MongoDB replica-set URI not configured")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=4000)
    database = client.get_database("wilsy_projects_task_lifecycle_cert")
    try:
        client.admin.command("ping")
        client.drop_database(database.name)
        source = database["wilsy_project_tasks"]
        events = database["wilsy_project_task_events"]
        ProjectTaskRegistry.ensure_indexes(source, events)
        assert source.index_information()["wilsy_project_task_identity_unique"]["unique"]
        assert events.index_information()["wilsy_project_task_idempotency_unique"]["unique"]
        store = ProjectTaskRegistry(source, events)
        tenant, project = "task-tenant-a", "prj-" + "a" * 48
        owner, assignee = "owner-a", "participant-a"
        instant = datetime.now(timezone.utc).replace(microsecond=0)

        def tx(action):
            with client.start_session() as session:
                return session.with_transaction(
                    action, read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )

        def create(key: str, *, name: str, parent: str | None = None,
                   depends: tuple[str, ...] = (), kind: str = "TASK"):
            task_id = task_id_for_command(tenant, project, owner, key)
            record = ProjectTask(
                tenant_id=tenant, project_id=project, task_id=task_id,
                kind=kind, parent_task_id=parent, title=name,
                description="Synthetic source-owned project work", status="TODO",
                assignee_principal_id=assignee, due_date="2026-12-15",
                depends_on=depends, created_by_principal_id=owner,
                updated_by_principal_id=owner,
                created_at=instant, updated_at=instant,
            )
            return tx(lambda session: store.create_or_replay(
                task=record, idempotency_key=key, session=session,
            ))

        parent = create("parent", name="Parent task")
        blocker = create("blocker", name="Predecessor milestone", kind="MILESTONE")
        child = create(
            "child", name="Dependent subtask", parent=parent.task_id,
            depends=(blocker.task_id,),
        )
        assert create("parent", name="Parent task") == parent
        first, more = tx(lambda session: store.list_page(
            tenant_id=tenant, project_id=project, session=session, limit=2,
        ))
        assert len(first) == 2 and more is True
        second, more = tx(lambda session: store.list_page(
            tenant_id=tenant, project_id=project, session=session,
            limit=2, offset=2,
        ))
        assert len(second) == 1 and more is False
        assert len({item.task_id for item in (*first, *second)}) == 3
        with pytest.raises(ProjectTaskNotFound):
            tx(lambda session: store.get(
                tenant_id="foreign-tenant", project_id=project,
                task_id=parent.task_id, session=session,
            ))
        with pytest.raises(ProjectTaskNotFound):
            tx(lambda session: store.get(
                tenant_id=tenant, project_id="prj-" + "b" * 48,
                task_id=child.task_id, session=session,
            ))

        def move(item, status, key, time_offset):
            return tx(lambda session: store.transition_or_replay(
                tenant_id=tenant, project_id=project, task_id=item.task_id,
                actor_principal_id=assignee, status=status,
                expected_revision=item.revision, idempotency_key=key,
                occurred_at=instant + timedelta(seconds=time_offset),
                session=session,
            ))

        root_working = move(parent, "IN_PROGRESS", "parent-start", 1)
        child_working = move(child, "IN_PROGRESS", "child-start", 2)
        with pytest.raises(ProjectTaskConflict, match="CHILDREN_INCOMPLETE"):
            move(root_working, "DONE", "parent-early", 3)
        # A rejected completion must leave both the persisted task and
        # immutable audit unchanged after the transaction aborts.
        events_before_denial = events.count_documents({"tenant_id": tenant})
        with pytest.raises(ProjectTaskConflict, match="DEPENDENCY_BLOCKED"):
            move(child_working, "DONE", "child-early", 3)
        denied_readback = tx(lambda session: (
            store.get(tenant_id=tenant, project_id=project,
                      task_id=child.task_id, session=session),
            store.get(tenant_id=tenant, project_id=project,
                      task_id=blocker.task_id, session=session),
        ))
        assert denied_readback[0].status == "IN_PROGRESS"
        assert denied_readback[0].revision == child_working.revision
        assert denied_readback[0].depends_on == (blocker.task_id,)
        assert denied_readback[1].status == "TODO"
        assert events.count_documents({"tenant_id": tenant}) == events_before_denial
        blocked_working = move(blocker, "IN_PROGRESS", "blocker-start", 3)
        blocked_done = move(blocked_working, "DONE", "blocker-finish", 4)
        assert blocked_done.status == "DONE"
        # Independent current-source majority readback establishes that the
        # same predecessor formerly blocking completion is now actually Done.
        ready_readback = tx(lambda session: (
            store.get(tenant_id=tenant, project_id=project,
                      task_id=child.task_id, session=session),
            store.get(tenant_id=tenant, project_id=project,
                      task_id=blocker.task_id, session=session),
        ))
        assert ready_readback[0].status == "IN_PROGRESS"
        assert ready_readback[0].depends_on == (ready_readback[1].task_id,)
        assert ready_readback[1].status == "DONE"
        assert sum(item.status != "DONE" for item in ready_readback[1:]) == 0
        child_done = move(child_working, "DONE", "child-finish", 5)
        assert child_done.status == "DONE"
        completed_readback = tx(lambda session: store.get(
            tenant_id=tenant, project_id=project,
            task_id=child.task_id, session=session,
        ))
        assert completed_readback == child_done
        assert completed_readback.depends_on == (blocker.task_id,)
        root_done = move(root_working, "DONE", "root-finish", 6)
        assert root_done.status == "DONE"
        assert move(root_working, "DONE", "root-finish", 6) == root_done
        with pytest.raises(ProjectTaskConflict, match="DIVERGENT_REPLAY"):
            tx(lambda session: store.transition_or_replay(
                tenant_id=tenant, project_id=project, task_id=root_working.task_id,
                actor_principal_id=assignee, status="BLOCKED",
                expected_revision=2, idempotency_key="root-finish",
                occurred_at=instant + timedelta(seconds=6), session=session,
            ))
        assert events.count_documents({"tenant_id": tenant}) == 9
        assert source.count_documents({"tenant_id": tenant}) == 3
        assert source.count_documents({"tenant_id": "foreign-tenant"}) == 0
    finally:
        client.drop_database(database.name)
        client.close()


def test_disposable_task_edit_and_reassignment_replay() -> None:
    """Audited task revisions retain original project graph and exact CAS."""
    uri = os.environ.get("TEST_PROJECTS_ACCOUNTABILITY_MONGO_URI")
    if not uri:
        pytest.skip("Disposable MongoDB replica-set URI not configured")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=4000)
    database = client.get_database("wilsy_projects_task_revision_cert")
    try:
        client.admin.command("ping")
        client.drop_database(database.name)
        tasks = database["wilsy_project_tasks"]
        events = database["wilsy_project_task_events"]
        ProjectTaskRegistry.ensure_indexes(tasks, events)
        store = ProjectTaskRegistry(tasks, events)
        tenant, project, owner = "task-edit-tenant", "prj-" + "e" * 48, "owner-a"
        instant = datetime.now(timezone.utc).replace(microsecond=0)
        key = "create-editable-task"
        task_id = task_id_for_command(tenant, project, owner, key)
        initial = ProjectTask(
            tenant_id=tenant, project_id=project, task_id=task_id,
            kind="TASK", parent_task_id=None,
            title="Initial work title", description="First context",
            status="TODO", assignee_principal_id=None, due_date=None,
            depends_on=(), created_by_principal_id=owner,
            updated_by_principal_id=owner,
            created_at=instant, updated_at=instant,
        )
        def tx(work):
            with client.start_session() as session:
                return session.with_transaction(
                    work, read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
        tx(lambda session: store.create_or_replay(
            task=initial, idempotency_key=key, session=session,
        ))
        def edit(session):
            return store.revise_or_replay(
                tenant_id=tenant, project_id=project, task_id=task_id,
                actor_principal_id=owner, title="Revised work",
                description="Governed handoff", due_date="2026-12-30",
                assignee_principal_id="assigned-contributor",
                expected_revision=1, idempotency_key="revise-1",
                occurred_at=instant + timedelta(seconds=1), session=session,
            )
        revised = tx(edit)
        assert tx(edit) == revised
        assert revised.revision == 2
        assert revised.assignee_principal_id == "assigned-contributor"
        assert revised.title == "Revised work"
        assert revised.project_id == project
        with pytest.raises(ProjectTaskConflict, match="DIVERGENT_REPLAY"):
            tx(lambda session: store.revise_or_replay(
                tenant_id=tenant, project_id=project, task_id=task_id,
                actor_principal_id=owner, title="Tampered replay",
                description="Governed handoff", due_date="2026-12-30",
                assignee_principal_id="assigned-contributor",
                expected_revision=1, idempotency_key="revise-1",
                occurred_at=instant + timedelta(seconds=2), session=session,
            ))
        with pytest.raises(ProjectTaskConflict, match="REVISION_CONFLICT"):
            tx(lambda session: store.revise_or_replay(
                tenant_id=tenant, project_id=project, task_id=task_id,
                actor_principal_id=owner, title="Stale edit",
                description="", due_date=None, assignee_principal_id=None,
                expected_revision=1, idempotency_key="stale-1",
                occurred_at=instant + timedelta(seconds=3), session=session,
            ))
        assert events.count_documents({"tenant_id": tenant}) == 2
        assert tasks.count_documents({"tenant_id": tenant, "revision": 2}) == 1
        with client.start_session() as session:
            with pytest.raises(ProjectTaskNotFound):
                store.get(
                    tenant_id="foreign-tenant", project_id=project,
                    task_id=task_id, session=session,
                )
    finally:
        client.drop_database(database.name)
        client.close()



def test_disposable_completed_history_filters_before_pagination_and_binds_event_provenance() -> None:
    """Current DONE history is queried and verified independently in real Mongo."""
    uri = os.environ.get("TEST_PROJECTS_ACCOUNTABILITY_MONGO_URI")
    if not uri:
        pytest.skip("Disposable MongoDB replica-set URI not configured")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=4000)
    database = client.get_database("wilsy_projects_completed_history_cert")
    try:
        client.admin.command("ping")
        client.drop_database(database.name)
        tasks, events = database["wilsy_project_tasks"], database["wilsy_project_task_events"]
        ProjectTaskRegistry.ensure_indexes(tasks, events)
        assert "wilsy_project_task_completed_recent" in tasks.index_information()
        store = ProjectTaskRegistry(tasks, events)
        tenant, project, actor = "completed-cert-tenant", "prj-" + "d" * 48, "source-owner"
        start = datetime.now(timezone.utc).replace(microsecond=123456)

        def tx(action):
            with client.start_session() as session:
                return session.with_transaction(
                    action, read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )

        names = ("Certificate one", "Certificate two", "Still active")
        for index, title in enumerate(names):
            key = "create-completed-" + str(index)
            task_id = task_id_for_command(tenant, project, actor, key)
            created_at = start + timedelta(seconds=index * 10)
            initial = ProjectTask(
                tenant_id=tenant, project_id=project, task_id=task_id,
                kind="TASK", parent_task_id=None, title=title, description="",
                status="TODO", assignee_principal_id="source-contributor",
                due_date=None, depends_on=(), created_by_principal_id=actor,
                updated_by_principal_id=actor, created_at=created_at,
                updated_at=created_at,
            )
            tx(lambda session: store.create_or_replay(
                task=initial, idempotency_key=key, session=session,
            ))
            if index < 2:
                tx(lambda session: store.transition_or_replay(
                    tenant_id=tenant, project_id=project, task_id=task_id,
                    actor_principal_id=actor, status="IN_PROGRESS",
                    expected_revision=1, idempotency_key="start-" + str(index),
                    occurred_at=created_at + timedelta(seconds=1), session=session,
                ))
                tx(lambda session: store.transition_or_replay(
                    tenant_id=tenant, project_id=project, task_id=task_id,
                    actor_principal_id=actor, status="DONE",
                    expected_revision=2, idempotency_key="done-" + str(index),
                    occurred_at=created_at + timedelta(seconds=2), session=session,
                ))

        def read(offset=0, limit=1, search="", order="NEWEST", scope=tenant):
            return tx(lambda session: store.list_completed_page(
                tenant_id=scope, project_id=project, session=session,
                limit=limit, offset=offset, search=search,
                completion_order=order,
            ))

        first, more = read()
        assert more and len(first) == 1
        assert first[0]["title"] == "Certificate two"
        assert first[0]["completed_by_principal_id"] == actor
        second, more = read(offset=1)
        assert not more and second[0]["title"] == "Certificate one"
        oldest, more = read(order="OLDEST")
        assert oldest[0]["title"] == "Certificate one" and more
        searched, more = read(search="two")
        assert len(searched) == 1 and searched[0]["title"] == "Certificate two"
        assert not more
        foreign, more = read(scope="foreign-tenant")
        assert foreign == () and not more
        assert events.count_documents({"tenant_id": tenant, "event_type": "PROJECT_TASK_TRANSITIONED"}) == 4
    finally:
        client.drop_database(database.name)
        client.close()

# ARTIFACT: test_project_tasks_real_mongo.py
# VERSION: v1.3.0-COMPLETED-HISTORY-MONGO-CERT
# AUTHORITY BOUNDARY: synthetic registry proof, not an IAM/employee grant
# TENANT POSTURE: exact tenant/project with cross-scope absence
# FAIL-CLOSED POSTURE: stale state, divergence, child/precedence blockers reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
