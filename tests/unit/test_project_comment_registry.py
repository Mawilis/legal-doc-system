"""TITLE: WILSY OS Project Comment Domain Boundary Certificate
VERSION: v1.1.0-NEWEST-FIRST-COMMENT-PAGINATION-CERT
AUTHORITY: Synthetic immutable comment and mention domain contract tests.
EPITOME: Reject forged authors, checksum modification, retired roots,
         duplicate mentions, foreign project records and malformed comments.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_comment_registry.py
COLLABORATION / OWNERSHIP: ProjectCommentRegistry and Projects task API.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.1.0-NEWEST-FIRST-COMMENT-PAGINATION-CERT pins
         indexed newest-first comments with exact task scope and source-backed
         pagination; neither mutations nor IAM permissions change.
CHANGELOG: v1.0.0-EXACT-PROJECT-COMMENT-DOMAIN-CERT establishes verified
         comment/mention invariants without pretending to send notifications.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque synthetic principal and tenant identifiers.
TENANT BOUNDARY: Explicit tenant/project/task match required for every comment.
AUTHORITY BOUNDARY: No IAM grants or notification approvals are created.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tools.eos.saas.projects.project_comment_registry import (
    ProjectComment, ProjectCommentError, ProjectCommentRegistry, comment_id_for_command,
)

TENANT = "tenant-a"
PROJECT = "prj-" + "a" * 48
TASK = "ptk-" + "b" * 48
AUTHOR = "participant-author"
NOW = datetime(2026, 11, 18, 8, 0, tzinfo=timezone.utc)


def comment(**changes: object) -> ProjectComment:
    """Create one synthetic verified comment with a stable exact origin."""
    values = dict(
        tenant_id=TENANT, project_id=PROJECT, task_id=TASK,
        comment_id=comment_id_for_command(TENANT, PROJECT, TASK, AUTHOR, "create-one"),
        author_principal_id=AUTHOR, body="Please review the milestone.",
        mentions=("member-two",), created_at=NOW,
    )
    values.update(changes)
    return ProjectComment(**values)


def test_comment_pages_are_source_sorted_newest_first() -> None:
    from pymongo import DESCENDING
    older = comment(created_at=NOW)
    newer = comment(
        created_at=NOW.replace(hour=9),
        comment_id=comment_id_for_command(TENANT, PROJECT, TASK, AUTHOR, "create-two"),
    )

    class Cursor:
        def sort(self, spec):
            assert spec == [("created_at", DESCENDING), ("comment_id", DESCENDING)]
            return self
        def skip(self, offset):
            assert offset == 0
            return self
        def limit(self, count):
            assert count == 2
            return [newer.to_dict(), older.to_dict()][:count]

    class Comments:
        def find(self, query, *, session):
            assert query == {
                "tenant_id": TENANT, "project_id": PROJECT, "task_id": TASK,
            }
            assert session == "source-session"
            return Cursor()

    registry = ProjectCommentRegistry(Comments(), object())
    items, more = registry.list_page(
        tenant_id=TENANT, project_id=PROJECT, task_id=TASK,
        session="source-session", offset=0, limit=1,
    )
    assert more
    assert items[0].comment_id == newer.comment_id


def test_comment_canonical_roundtrip_and_tampering_deny() -> None:
    """Every material comment field is checksum-protected and source-owned."""
    original = comment()
    assert ProjectComment.hydrate(original.to_dict()) == original
    assert len(original.fingerprint) == 128
    altered = original.to_dict()
    altered["mentions"] = ["member-three"]
    with pytest.raises(ProjectCommentError, match="FINGERPRINT_INVALID"):
        ProjectComment.hydrate(altered)
    with pytest.raises(ProjectCommentError, match="RECORD_INVALID"):
        ProjectComment.hydrate({**original.to_dict(), "approval": "APPROVED"})


@pytest.mark.parametrize("changes", [
    {"tenant_id": "MASTER"}, {"tenant_id": "WILSY_ROOT"},
    {"project_id": "not-project"}, {"task_id": "not-task"},
    {"comment_id": "wrong"}, {"body": ""}, {"body": "  trim "},
    {"mentions": ("member-two", "member-two")},
    {"mentions": (AUTHOR,)}, {"mentions": ("member-two",) * 11},
    {"created_at": NOW.replace(tzinfo=None)},
])
def test_comment_rejects_false_scope_mentions_or_authority(changes: dict[str, object]) -> None:
    """Impossible source facts and forged authority never become comments."""
    with pytest.raises(ProjectCommentError):
        comment(**changes)


def test_command_identity_separates_tenant_project_task_and_author() -> None:
    """An idempotency key never becomes a global or cross-project identity."""
    first = comment_id_for_command(TENANT, PROJECT, TASK, AUTHOR, "command")
    assert first == comment_id_for_command(TENANT, PROJECT, TASK, AUTHOR, "command")
    assert first != comment_id_for_command("tenant-b", PROJECT, TASK, AUTHOR, "command")
    assert first != comment_id_for_command(
        TENANT, PROJECT, "ptk-" + "c" * 48, AUTHOR, "command",
    )
    assert first != comment_id_for_command(TENANT, PROJECT, TASK, "other", "command")


# ARTIFACT: test_project_comment_registry.py
# VERSION: v1.1.0-NEWEST-FIRST-COMMENT-PAGINATION-CERT
# AUTHORITY BOUNDARY: source validation only, not IAM or message delivery
# TENANT POSTURE: exact tenant/project/task and opaque mention IDs
# FAIL-CLOSED POSTURE: bogus claims, tampered checksum, duplicates and aliases deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
