"""TITLE: WILSY OS Project Task Comment Real MongoDB Certificate
VERSION: v1.0.0-PROJECT-COMMENT-AUDIT-REPLICA-CERT
AUTHORITY: Disposable replica-set-only collaboration persistence evidence.
EPITOME: Certify immutable comment/mention audit, task-scoped read, exactly
         once replay and foreign tenant/project/task nondisclosure.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_project_comments_real_mongo.py
COLLABORATION / OWNERSHIP: Existing disposable Projects CI and comment registry.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-PROJECT-COMMENT-AUDIT-REPLICA-CERT verifies append-only
         comments using caller-owned majority MongoDB transactions and indexes.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identities; no real message delivery.
TENANT BOUNDARY: Explicit tenant/project/task bound on every source read.
AUTHORITY BOUNDARY: These tests never issue project participation or IAM roles.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.saas.projects.project_comment_registry import (
    ProjectComment, ProjectCommentRegistry, ProjectCommentConflict,
    comment_id_for_command,
)


def test_project_comment_create_replay_and_exact_scope() -> None:
    """Test immutable audit + foreign absence with an actual Mongo transaction."""
    uri = os.environ.get("TEST_PROJECTS_ACCOUNTABILITY_MONGO_URI")
    if not uri:
        pytest.skip("Disposable project replica URI not configured")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=4000)
    db = client.get_database("wilsy_project_comment_cert")
    try:
        client.admin.command("ping")
        client.drop_database(db.name)
        comments, events = db["wilsy_project_comments"], db["wilsy_project_comment_events"]
        ProjectCommentRegistry.ensure_indexes(comments, events)
        assert comments.index_information()["wilsy_project_comment_identity_unique"]["unique"]
        assert events.index_information()["wilsy_project_comment_replay_unique"]["unique"]
        registry = ProjectCommentRegistry(comments, events)
        tenant, project, task = "project-comment-tenant", "prj-" + "a" * 48, "ptk-" + "b" * 48
        actor, key = "current-contributor", "comment-1"
        source = ProjectComment(
            tenant_id=tenant, project_id=project, task_id=task,
            comment_id=comment_id_for_command(tenant, project, task, actor, key),
            author_principal_id=actor, body="Review current dependency.",
            mentions=("active-tenant-member",),
            created_at=datetime.now(timezone.utc).replace(microsecond=0),
        )
        def transaction(operation):
            with client.start_session() as session:
                return session.with_transaction(
                    operation, read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
        write = lambda session: registry.create_or_replay(
            comment=source, actor_principal_id=actor, idempotency_key=key,
            session=session,
        )
        created = transaction(write)
        assert transaction(write) == created
        assert comments.count_documents({"tenant_id": tenant}) == 1
        assert events.count_documents({"tenant_id": tenant}) == 1
        values, more = transaction(lambda session: registry.list_page(
            tenant_id=tenant, project_id=project, task_id=task, session=session,
        ))
        assert values == (source,) and more is False
        for scope in (
            {"tenant_id": "foreign-tenant", "project_id": project, "task_id": task},
            {"tenant_id": tenant, "project_id": "prj-" + "c" * 48, "task_id": task},
            {"tenant_id": tenant, "project_id": project, "task_id": "ptk-" + "d" * 48},
        ):
            values, more = transaction(lambda session: registry.list_page(
                **scope, session=session,
            ))
            assert values == () and more is False
        with pytest.raises(ProjectCommentConflict, match="DIVERGENT_REPLAY"):
            transaction(lambda session: registry.create_or_replay(
                comment=ProjectComment(
                    tenant_id=tenant, project_id=project, task_id=task,
                    comment_id=source.comment_id, author_principal_id=actor,
                    body="Different command.", mentions=(),
                    created_at=source.created_at,
                ), actor_principal_id=actor, idempotency_key=key, session=session,
            ))
        assert events.count_documents({"tenant_id": tenant}) == 1
    finally:
        client.drop_database(db.name)
        client.close()


# ARTIFACT: test_project_comments_real_mongo.py
# VERSION: v1.0.0-PROJECT-COMMENT-AUDIT-REPLICA-CERT
# AUTHORITY BOUNDARY: test persistence only, not authenticated route claims
# TENANT POSTURE: exact tenant/project/task with foreign absence
# FAIL-CLOSED POSTURE: divergent replay and foreign project scopes deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
