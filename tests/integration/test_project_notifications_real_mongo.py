"""TITLE: WILSY OS Project Mention Inbox Real MongoDB Certificate
VERSION: v1.0.0-PROJECT-MENTION-INBOX-ATOMICITY-CERT
AUTHORITY: Disposable MongoDB replica-set source certification only.
EPITOME: Check comment+notification atomic transaction, idempotent recipients,
         exact tenant/project inbox isolation, audited read receipt and replay.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_project_notifications_real_mongo.py
COLLABORATION / OWNERSHIP: ProjectCommentRegistry, ProjectNotificationRegistry
         and existing Projects disposable MongoDB certification infrastructure.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-PROJECT-MENTION-INBOX-ATOMICITY-CERT tests actual
         source-owned mention record and read-receipt persistence.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Test-only synthetic opaque principal IDs.
TENANT BOUNDARY: Every write/read/replay includes exact tenant/project/recipient.
AUTHORITY BOUNDARY: Test validates in-app record, not external transport delivery.
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

from tools.eos.saas.projects.project_comment_registry import (
    ProjectComment, ProjectCommentRegistry, comment_id_for_command,
)
from tools.eos.saas.projects.project_notification_registry import (
    ProjectNotificationRegistry, ProjectNotificationConflict,
    ProjectNotificationNotFound,
)


def test_project_mention_notification_and_receipt_atomically_persist() -> None:
    """Commit one source comment and one recipient inbox signal in one transaction."""
    uri = os.environ.get("TEST_PROJECTS_ACCOUNTABILITY_MONGO_URI")
    if not uri:
        pytest.skip("Disposable project replica URI not configured")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=4000)
    db = client.get_database("wilsy_projects_notifications_cert")
    try:
        client.admin.command("ping")
        client.drop_database(db.name)
        comments, comment_events = db["wilsy_project_comments"], db["wilsy_project_comment_events"]
        inbox, inbox_events = db["wilsy_project_notifications"], db["wilsy_project_notification_events"]
        ProjectCommentRegistry.ensure_indexes(comments, comment_events)
        ProjectNotificationRegistry.ensure_indexes(inbox, inbox_events)
        commentary = ProjectCommentRegistry(comments, comment_events)
        notifications = ProjectNotificationRegistry(inbox, inbox_events)
        tenant, project, task = "notification-tenant", "prj-" + "e" * 48, "ptk-" + "d" * 48
        actor, recipient, key = "current-author", "current-recipient", "comment-1"
        instant = datetime.now(timezone.utc).replace(microsecond=0)
        comment = ProjectComment(
            tenant_id=tenant, project_id=project, task_id=task,
            comment_id=comment_id_for_command(tenant, project, task, actor, key),
            author_principal_id=actor, body="Please review the project blocker.",
            mentions=(recipient,), created_at=instant,
        )
        def tx(action):
            with client.start_session() as session:
                return session.with_transaction(
                    action, read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
        def publish(session):
            stored = commentary.create_or_replay(
                comment=comment, actor_principal_id=actor,
                idempotency_key=key, session=session,
            )
            return notifications.append_for_comment(comment=stored, session=session)
        initial = tx(publish)
        assert len(initial) == 1
        assert tx(publish) == initial
        assert comments.count_documents({"tenant_id": tenant}) == 1
        assert inbox.count_documents({"tenant_id": tenant}) == 1
        assert inbox_events.count_documents({"tenant_id": tenant}) == 1
        notification = initial[0]
        assert notification.read_at is None and notification.revision == 1
        page, more = tx(lambda session: notifications.list_for_recipient(
            tenant_id=tenant, project_id=project,
            recipient_principal_id=recipient, session=session,
        ))
        assert page == initial and more is False
        for coords in (
            {"tenant_id": "foreign", "project_id": project, "recipient_principal_id": recipient},
            {"tenant_id": tenant, "project_id": "prj-" + "c" * 48, "recipient_principal_id": recipient},
            {"tenant_id": tenant, "project_id": project, "recipient_principal_id": "other-person"},
        ):
            page, more = tx(lambda session: notifications.list_for_recipient(
                **coords, session=session,
            ))
            assert page == () and more is False
        def read(session):
            return notifications.mark_read(
                tenant_id=tenant, project_id=project,
                recipient_principal_id=recipient,
                notification_id=notification.notification_id,
                expected_revision=1, idempotency_key="mark-read-1",
                occurred_at=instant + timedelta(seconds=2), session=session,
            )
        readback = tx(read)
        assert readback.revision == 2 and readback.read_at is not None
        assert tx(read) == readback
        assert tx(publish) == (readback,)
        with pytest.raises(ProjectNotificationConflict, match="DIVERGENT_REPLAY"):
            tx(lambda session: notifications.mark_read(
                tenant_id=tenant, project_id=project,
                recipient_principal_id=recipient,
                notification_id=notification.notification_id,
                expected_revision=2, idempotency_key="mark-read-1",
                occurred_at=instant + timedelta(seconds=3), session=session,
            ))
        with pytest.raises(ProjectNotificationNotFound):
            tx(lambda session: notifications.mark_read(
                tenant_id="foreign", project_id=project,
                recipient_principal_id=recipient,
                notification_id=notification.notification_id,
                expected_revision=1, idempotency_key="foreign-read-1",
                occurred_at=instant + timedelta(seconds=3), session=session,
            ))
        assert inbox_events.count_documents({"tenant_id": tenant}) == 2
        assert inbox.count_documents({"tenant_id": tenant, "revision": 2}) == 1
    finally:
        client.drop_database(db.name)
        client.close()


# ARTIFACT: test_project_notifications_real_mongo.py
# VERSION: v1.0.0-PROJECT-MENTION-INBOX-ATOMICITY-CERT
# AUTHORITY BOUNDARY: disposable Mongo transaction, no external delivery
# TENANT POSTURE: only matching tenant/project/recipient rows can be read
# FAIL-CLOSED POSTURE: duplicate, foreign, stale or divergent receipt denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
