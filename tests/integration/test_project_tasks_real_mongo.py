"""TITLE: WILSY OS Project Work Execution Real-Mongo Certificate
VERSION: v1.0.0-PROJECT-TASK-REPLICA-LIFECYCLE-CERT
AUTHORITY: Synthetic disposable replica-set source certification only.
EPITOME: Test nested work, milestone/dependency index, idempotent task CRUD,
         verified predecessor/child completion gates and exact tenant absence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_project_tasks_real_mongo.py
COLLABORATION / OWNERSHIP: Existing Projects disposable Mongo CI and
         ProjectTaskRegistry; no operator account or active tenant is touched.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-PROJECT-TASK-REPLICA-LIFECYCLE-CERT proves source-backed
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
        with pytest.raises(ProjectTaskConflict, match="DEPENDENCY_BLOCKED"):
            move(child_working, "DONE", "child-early", 3)
        blocked_working = move(blocker, "IN_PROGRESS", "blocker-start", 3)
        blocked_done = move(blocked_working, "DONE", "blocker-finish", 4)
        assert blocked_done.status == "DONE"
        child_done = move(child_working, "DONE", "child-finish", 5)
        assert child_done.status == "DONE"
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


# ARTIFACT: test_project_tasks_real_mongo.py
# VERSION: v1.0.0-PROJECT-TASK-REPLICA-LIFECYCLE-CERT
# AUTHORITY BOUNDARY: synthetic registry proof, not an IAM/employee grant
# TENANT POSTURE: exact tenant/project with cross-scope absence
# FAIL-CLOSED POSTURE: stale state, divergence, child/precedence blockers reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
