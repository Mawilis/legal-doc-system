"""TITLE: WILSY OS Project Reviewer Approval Real MongoDB Certificate
VERSION: v1.1.0-PENDING-REVIEWER-INBOX-REPLICA-CERT
AUTHORITY: Disposable replica-set decision CAS, replay, audit and isolation.
EPITOME: Owner request -> named contributor decision, exact replay, durable
         audit, foreign review absence and independent task status retention.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_project_approvals_real_mongo.py
COLLABORATION / OWNERSHIP: ProjectApprovalRegistry; Projects disposable CI.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.1.0-PENDING-REVIEWER-INBOX-REPLICA-CERT verifies the
         exact tenant/reviewer indexed queue includes PENDING and removes
         terminal decisions without deleting immutable audit records.
CHANGELOG: v1.1.0-PENDING-REVIEWER-INBOX-REPLICA-CERT verifies
         immutable approval and reviewer source under real Mongo transactions.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic data in disposable isolated Mongo.
TENANT BOUNDARY: Exact tenant, task, reviewer and event scope.
AUTHORITY BOUNDARY: Does not grant permissions or mutate financial/task states.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS only.
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

from tools.eos.saas.projects.project_approval_registry import (
    ProjectApproval, ProjectApprovalRegistry,
    ProjectApprovalConflict, ProjectApprovalNotFound,
    approval_id_for_request,
)


def test_project_approval_exact_review_and_replay_in_replica_set() -> None:
    """Prove one decision and immutable audit under actual snapshot/majority CAS."""
    uri = os.environ.get("TEST_PROJECTS_ACCOUNTABILITY_MONGO_URI")
    if not uri:
        pytest.skip("Disposable Projects replica not configured")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=4000)
    db = client.get_database("wilsy_projects_review_cert")
    try:
        client.admin.command("ping")
        client.drop_database(db.name)
        store = ProjectApprovalRegistry(
            db["wilsy_project_approvals"], db["wilsy_project_approval_events"],
        )
        ProjectApprovalRegistry.ensure_indexes(
            db["wilsy_project_approvals"], db["wilsy_project_approval_events"],
        )
        assert db["wilsy_project_approvals"].index_information()["wilsy_project_approval_identity_unique"]["unique"]
        assert "wilsy_project_approval_principal_inbox" in db["wilsy_project_approvals"].index_information()
        tenant, project, task = "approval-tenant", "prj-" + "a" * 48, "ptk-" + "b" * 48
        requester, reviewer = "project-owner", "reviewer-a"
        now = datetime.now(timezone.utc).replace(microsecond=0)
        key = "request-1"
        source = ProjectApproval(
            tenant_id=tenant, project_id=project, task_id=task,
            approval_id=approval_id_for_request(tenant, project, task, requester, key),
            requester_principal_id=requester, reviewer_principal_id=reviewer,
            rationale="Review acceptance evidence.", status="PENDING",
            requested_at=now,
        )
        def tx(action):
            with client.start_session() as session:
                return session.with_transaction(
                    action, read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
        def request(session):
            return store.create_or_replay(
                approval=source, idempotency_key=key, session=session,
            )
        created = tx(request)
        assert tx(request) == created
        assert created.status == "PENDING" and created.revision == 1
        pending = tx(lambda session: store.pending_for_reviewer(
            tenant_id=tenant, reviewer_principal_id=reviewer, session=session,
        ))
        assert pending == (created,)
        foreign_pending = tx(lambda session: store.pending_for_reviewer(
            tenant_id="foreign", reviewer_principal_id=reviewer, session=session,
        ))
        assert foreign_pending == ()
        other_pending = tx(lambda session: store.pending_for_reviewer(
            tenant_id=tenant, reviewer_principal_id="intruder", session=session,
        ))
        assert other_pending == ()
        def decide(session):
            return store.decide_or_replay(
                tenant_id=tenant, project_id=project, task_id=task,
                approval_id=created.approval_id, reviewer_principal_id=reviewer,
                decision="APPROVED", rationale="Source verified.",
                expected_revision=1, occurred_at=now + timedelta(seconds=1),
                idempotency_key="review-1", session=session,
            )
        result = tx(decide)
        assert result.status == "APPROVED" and result.revision == 2
        assert tx(decide) == result
        after = tx(lambda session: store.pending_for_reviewer(
            tenant_id=tenant, reviewer_principal_id=reviewer, session=session,
        ))
        assert after == ()
        assert tx(request) == created
        page, more = tx(lambda session: store.list_page(
            tenant_id=tenant, project_id=project, task_id=task, session=session,
        ))
        assert page == (result,) and more is False
        for coords in (
            ("foreign", project, task),
            (tenant, "prj-" + "c" * 48, task),
            (tenant, project, "ptk-" + "d" * 48),
        ):
            page, more = tx(lambda session: store.list_page(
                tenant_id=coords[0], project_id=coords[1],
                task_id=coords[2], session=session,
            ))
            assert page == () and more is False
        with pytest.raises(ProjectApprovalNotFound):
            tx(lambda session: store.get(
                tenant_id="foreign", project_id=project, task_id=task,
                approval_id=created.approval_id, session=session,
            ))
        with pytest.raises(ProjectApprovalNotFound):
            tx(lambda session: store.decide_or_replay(
                tenant_id=tenant, project_id=project, task_id=task,
                approval_id=created.approval_id,
                reviewer_principal_id="intruder", decision="REJECTED",
                rationale="Wrong reviewer.", expected_revision=1,
                occurred_at=now + timedelta(seconds=2),
                idempotency_key="intrusion-1", session=session,
            ))
        with pytest.raises(ProjectApprovalConflict, match="REVISION_CONFLICT"):
            tx(lambda session: store.decide_or_replay(
                tenant_id=tenant, project_id=project, task_id=task,
                approval_id=created.approval_id, reviewer_principal_id=reviewer,
                decision="REJECTED", rationale="Changed after acceptance.",
                expected_revision=1, occurred_at=now + timedelta(seconds=2),
                idempotency_key="new-review-1", session=session,
            ))
        with pytest.raises(ProjectApprovalConflict, match="DIVERGENT_REPLAY"):
            tx(lambda session: store.decide_or_replay(
                tenant_id=tenant, project_id=project, task_id=task,
                approval_id=created.approval_id, reviewer_principal_id=reviewer,
                decision="REJECTED", rationale="Different result.",
                expected_revision=1, occurred_at=now + timedelta(seconds=3),
                idempotency_key="review-1", session=session,
            ))
        assert db["wilsy_project_approvals"].count_documents({"tenant_id": tenant}) == 1
        assert db["wilsy_project_approval_events"].count_documents({"tenant_id": tenant}) == 2
    finally:
        client.drop_database(db.name)
        client.close()


# ARTIFACT: test_project_approvals_real_mongo.py
# VERSION: v1.1.0-PENDING-REVIEWER-INBOX-REPLICA-CERT
# AUTHORITY BOUNDARY: disposable source persistence proof, not IAM or signature
# TENANT POSTURE: foreign tenant, task and reviewer nondisclosure
# FAIL-CLOSED POSTURE: divergent replay, nonreviewer and stale revision deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS only
# END OF WILSY OS SOVEREIGN ARTIFACT
