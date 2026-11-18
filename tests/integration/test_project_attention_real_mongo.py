"""TITLE: WILSY OS Project Daily Attention Real Mongo Scalability Certificate
VERSION: v1.0.0-ASSIGNED-ATTENTION-OVER-500-REPLICA-CERT
AUTHORITY: Synthetic disposable replica-set source read/authorization proof.
EPITOME: Read all 511 delegated active tasks without silent pagination loss,
         suppress completed and cancelled rows and verify revoked project denial.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_project_attention_real_mongo.py
COLLABORATION / OWNERSHIP: project_attention_source, ProjectTaskRegistry,
         existing Projects accountability disposable MongoDB CI.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-ASSIGNED-ATTENTION-OVER-500-REPLICA-CERT proves
         indexed source read completeness and current project record gating
         under real Mongo snapshot transactions, without creating IAM grants.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic tenant/principal/task records only.
TENANT BOUNDARY: Exact tenant and assignee; no foreign person/tenant disclosure.
AUTHORITY BOUNDARY: IAM and participant repository are safely mocked; full
         authenticated participant HTTP journey is certified separately.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
from types import SimpleNamespace
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api import project_attention_source as attention
from tools.eos.saas.projects.project_task_registry import (
    ProjectTask, ProjectTaskRegistry,
)

TENANT = "attention-scale-tenant"
PROJECT = "prj-" + "d" * 48
PRINCIPAL = "assigned-contributor"
NOW = datetime(2026, 11, 18, 8, 0, tzinfo=timezone.utc)


def _task(index: int, status: str, *, assignee: str = PRINCIPAL, tenant: str = TENANT) -> ProjectTask:
    """Construct one source-valid synthetic immutable project work item."""
    return ProjectTask(
        tenant_id=tenant, project_id=PROJECT,
        task_id="ptk-" + format(index + 1, "048x"),
        kind="TASK", parent_task_id=None,
        title="Execute validated work package " + str(index),
        description="", status=status, assignee_principal_id=assignee,
        due_date=None, depends_on=(),
        created_by_principal_id="project-owner",
        updated_by_principal_id="project-owner",
        created_at=NOW, updated_at=NOW,
    )


def test_complete_511_assigned_project_tasks_and_revocation(monkeypatch: Any) -> None:
    """No silent 500-row truncation or inherited access in a real Mongo source read."""
    uri = os.environ.get("TEST_PROJECTS_ACCOUNTABILITY_MONGO_URI")
    if not uri:
        pytest.skip("Disposable project replica URI not configured")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=4000)
    db = client.get_database("wilsy_project_attention_scale_cert")
    try:
        client.admin.command("ping")
        client.drop_database(db.name)
        source = db["wilsy_project_tasks"]
        events = db["wilsy_project_task_events"]
        ProjectTaskRegistry.ensure_indexes(source, events)
        assert "wilsy_project_task_assignee_attention" in source.index_information()
        records = [_task(index, "BLOCKED" if index % 5 == 0 else "IN_PROGRESS").to_dict()
                   for index in range(511)]
        records.extend([
            _task(511, "DONE").to_dict(),
            _task(512, "CANCELLED").to_dict(),
            _task(513, "BLOCKED", assignee="another-contributor").to_dict(),
            _task(514, "BLOCKED", tenant="foreign-tenant").to_dict(),
        ])
        source.insert_many(records)
        monkeypatch.setattr(attention.kernel_db, "get_database", lambda: db)
        def with_transaction(_context: Any, work: Any) -> Any:
            with client.start_session() as session:
                return session.with_transaction(
                    lambda active: work(object(), active),
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
        monkeypatch.setattr(attention.projects, "_transaction", with_transaction)
        current = {"active": True}
        examined: list[str] = []
        class ParticipantStore:
            """Verify the requested source principal and current assignment."""
            def get(self, *, tenant_id: str, project_id: str,
                    principal_id: str, session: Any) -> Any:
                assert (tenant_id, project_id, principal_id) == (TENANT, PROJECT, PRINCIPAL)
                return SimpleNamespace(role="CONTRIBUTOR")
        def verify(_context: Any, _registry: Any, project_id: str,
                   _session: Any) -> tuple[object, ParticipantStore]:
            examined.append(project_id)
            if not current["active"]:
                raise attention.projects.ProjectParticipantNotFound("NOT_FOUND")
            return object(), ParticipantStore()
        monkeypatch.setattr(attention.projects, "_require_current_project_participation", verify)
        context = SimpleNamespace(
            tenant_id=TENANT,
            identity=SimpleNamespace(identity_id=PRINCIPAL),
            decision=SimpleNamespace(authorization_role="PROJECTS_PARTICIPANT_CONTRIBUTOR"),
        )
        accepted = attention.read_project_attention(
            context=context, tenant_id=TENANT, principal_id=PRINCIPAL,
        )
        assert len(accepted["items"]) == 511
        assert len({row["work_item_id"] for row in accepted["items"]}) == 511
        assert all(row["tenant_id"] == TENANT and row["project_id"] == PROJECT
                   for row in accepted["items"])
        assert all(row["status"] in {"IN_PROGRESS", "BLOCKED"} for row in accepted["items"])
        assert examined == [PROJECT]
        current["active"] = False
        denied = attention.read_project_attention(
            context=context, tenant_id=TENANT, principal_id=PRINCIPAL,
        )
        assert denied == {"tenant_id": TENANT, "items": []}
    finally:
        client.drop_database(db.name)
        client.close()


# ARTIFACT: test_project_attention_real_mongo.py
# VERSION: v1.0.0-ASSIGNED-ATTENTION-OVER-500-REPLICA-CERT
# AUTHORITY BOUNDARY: disposable registry proof, no real IAM/grant
# TENANT POSTURE: exact tenant, principal, project and current participant
# FAIL-CLOSED POSTURE: terminal, foreign, cross-principal and revoked work absent
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
