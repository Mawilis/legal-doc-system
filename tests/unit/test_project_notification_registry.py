"""TITLE: WILSY OS Project Mention Inbox Domain Certificate
VERSION: v1.0.0-PROJECT-INBOX-READ-RECEIPT-CERT
AUTHORITY: Synthetic immutable recipient notification source contract tests.
EPITOME: Validate exact recipient source, comment-derived identity,
         fingerprint integrity, unread/read CAS, and absent delivery claims.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_notification_registry.py
COLLABORATION / OWNERSHIP: ProjectNotificationRegistry and Projects router.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-PROJECT-INBOX-READ-RECEIPT-CERT establishes bounded source
         identity, revisioned receipt, retained event and forged-state denial.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identities only.
TENANT BOUNDARY: Exact tenant/project/task and recipient.
AUTHORITY BOUNDARY: In-app evidence only, not transport delivery or approval.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.saas.projects.project_comment_registry import ProjectComment
from tools.eos.saas.projects.project_notification_registry import (
    ProjectNotification, ProjectNotificationError, ProjectNotificationConflict,
    notification_id_for_comment,
)

NOW = datetime(2026, 11, 18, 8, 0, tzinfo=timezone.utc)
PROJECT = "prj-" + "a" * 48
TASK = "ptk-" + "b" * 48
COMMENT = "pcm-" + "c" * 48


def source_comment() -> ProjectComment:
    """Return one source-approved mention comment."""
    return ProjectComment(
        tenant_id="tenant-a", project_id=PROJECT, task_id=TASK,
        comment_id=COMMENT, author_principal_id="author-a",
        body="Action required.", mentions=("recipient-a",), created_at=NOW,
    )


def notification(**changes: object) -> ProjectNotification:
    """Build one legitimate unread notification with explicit opaque recipient."""
    comment = source_comment()
    fields = dict(
        tenant_id=comment.tenant_id, project_id=comment.project_id,
        task_id=comment.task_id, comment_id=comment.comment_id,
        notification_id=notification_id_for_comment(comment, "recipient-a"),
        recipient_principal_id="recipient-a", actor_principal_id="author-a",
        occurred_at=NOW,
    )
    fields.update(changes)
    return ProjectNotification(**fields)


def test_notification_integrity_and_read_cas() -> None:
    """Read receipts are source-owned immutable revisions, not client badges."""
    original = notification()
    assert ProjectNotification.hydrate(original.to_dict()) == original
    assert original.read_at is None and original.revision == 1
    updated = original.mark_read(
        expected_revision=1, instant=NOW + timedelta(minutes=1),
    )
    assert updated.revision == 2
    assert updated.read_at == NOW + timedelta(minutes=1)
    assert original.read_at is None
    assert updated.fingerprint != original.fingerprint
    with pytest.raises(ProjectNotificationConflict, match="REVISION_CONFLICT"):
        original.mark_read(expected_revision=2, instant=NOW)
    with pytest.raises(ProjectNotificationConflict, match="ALREADY_READ"):
        updated.mark_read(
            expected_revision=2, instant=NOW + timedelta(minutes=2),
        )


@pytest.mark.parametrize("changes", [
    {"tenant_id": "MASTER"}, {"tenant_id": "WILSY_ROOT"},
    {"project_id": "foreign"}, {"task_id": "wrong"},
    {"comment_id": "invalid"}, {"recipient_principal_id": ""},
    {"revision": 2}, {"revision": True},
    {"read_at": NOW}, {"occurred_at": NOW.replace(tzinfo=None)},
])
def test_invalid_notification_state_refused(changes: dict[str, object]) -> None:
    """Malformed tenant, recipient, read state and revision are never accepted."""
    with pytest.raises(ProjectNotificationError):
        notification(**changes)


def test_forged_inbox_evidence_denied() -> None:
    """A persisted checksum detects changed state and unknown claims."""
    row = notification().to_dict()
    row["recipient_principal_id"] = "forged-person"
    with pytest.raises(ProjectNotificationError, match="FINGERPRINT_INVALID"):
        ProjectNotification.hydrate(row)
    with pytest.raises(ProjectNotificationError, match="RECORD_INVALID"):
        ProjectNotification.hydrate({**notification().to_dict(), "delivered": True})


def test_notification_identity_requires_real_source_mention() -> None:
    """No arbitrary principal can fabricate inbox evidence from a comment."""
    comment = source_comment()
    assert notification_id_for_comment(comment, "recipient-a") == notification().notification_id
    with pytest.raises(ProjectNotificationError, match="RECIPIENT_INVALID"):
        notification_id_for_comment(comment, "unmentioned-principal")


# ARTIFACT: test_project_notification_registry.py
# VERSION: v1.0.0-PROJECT-INBOX-READ-RECEIPT-CERT
# AUTHORITY BOUNDARY: source notification/receipt only, no delivery
# TENANT POSTURE: exact tenant/project/recipient and source comment
# FAIL-CLOSED POSTURE: false claim, invalid source, stale revision denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
