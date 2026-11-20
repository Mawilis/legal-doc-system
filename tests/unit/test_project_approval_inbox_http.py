"""TITLE: WILSY OS Exact-Reviewer Project Approval Inbox Route Certificate
VERSION: v1.0.0-REVOKED-PROJECT-REVIEW-INBOX-DENIAL
AUTHORITY: In-process canonical Projects route and current participation gate.
EPITOME: Prove a named reviewer sees only current contributor project approvals,
         not work in a revoked project or a globally owned project.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_approval_inbox_http.py
COLLABORATION / OWNERSHIP: projects_router, ProjectApprovalRegistry, IAM gates.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.0.0-REVOKED-PROJECT-REVIEW-INBOX-DENIAL covers authorized-only
         candidate filtering before pagination with no role elevation.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers and isolated monkeypatches.
TENANT BOUNDARY: All project/record scope includes authenticated tenant.
AUTHORITY BOUNDARY: Test does not mock true IAM success or create permission.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi import Response

from tools.eos.api import projects_router as routes
from tools.eos.saas.projects.project_approval_registry import ProjectApproval

TENANT = "review-tenant"
PRINCIPAL = "current-reviewer"
LIVE = "prj-" + "a" * 48
REVOKED = "prj-" + "b" * 48
TASK = "ptk-" + "c" * 48
NOW = datetime(2026, 11, 18, 8, 0, tzinfo=timezone.utc)


def _approval(project_id: str, ending: str) -> ProjectApproval:
    """Create a unique, source-valid decision targeted at the same reviewer."""
    return ProjectApproval(
        tenant_id=TENANT, project_id=project_id, task_id=TASK,
        approval_id="par-" + ending * 48,
        requester_principal_id="separate-owner",
        reviewer_principal_id=PRINCIPAL, rationale="Verify completion evidence.",
        status="PENDING", requested_at=NOW,
    )


def test_my_approvals_excludes_revoked_project_before_page_counts(monkeypatch) -> None:
    """A current IAM role alone does not reveal any revoked project review."""
    current = _approval(LIVE, "d")
    former = _approval(REVOKED, "e")
    database = {
        routes.PROJECT_APPROVAL_COLLECTION: object(),
        routes.PROJECT_APPROVAL_EVENT_COLLECTION: object(),
    }
    monkeypatch.setattr(routes.kernel_db, "get_database", lambda: database)
    monkeypatch.setattr(routes, "_transaction", lambda context, read: read(object(), object()))
    monkeypatch.setattr(
        routes.ProjectApprovalRegistry, "pending_for_reviewer",
        lambda self, *, tenant_id, reviewer_principal_id, session: (
            current, former,
        ),
    )
    class Members:
        """Model exact current participant record only for the active project."""
        def get(self, *, tenant_id, project_id, principal_id, session):
            assert (tenant_id, project_id, principal_id) == (TENANT, LIVE, PRINCIPAL)
            return SimpleNamespace(role="CONTRIBUTOR")
    def participant(context, registry, project_id, session):
        if project_id == REVOKED:
            raise routes.ProjectParticipantNotFound("PROJECT_PARTICIPANT_NOT_FOUND")
        assert project_id == LIVE
        return object(), Members()
    monkeypatch.setattr(routes, "_require_current_project_participation", participant)
    task_reads = []
    def source(registry, tenant_id, project_id, session):
        assert (tenant_id, project_id) == (TENANT, LIVE)
        return SimpleNamespace(get=lambda **kw: task_reads.append(kw) or object())
    monkeypatch.setattr(routes, "_project_task_store", source)
    context = SimpleNamespace(
        tenant_id=TENANT,
        identity=SimpleNamespace(identity_id=PRINCIPAL),
        decision=SimpleNamespace(authorization_role="PROJECTS_PARTICIPANT_CONTRIBUTOR"),
    )
    result = routes.list_my_pending_project_approvals(
        response=Response(), context=context, limit=50, offset=0,
    )
    assert result["schema"] == "WILSY-PROJECT-PENDING-APPROVALS/V1"
    assert result["tenant_id"] == TENANT and result["principal_id"] == PRINCIPAL
    assert [item["approval_id"] for item in result["items"]] == [current.approval_id]
    assert result["has_more"] is False
    assert len(task_reads) == 1
    assert task_reads[0]["tenant_id"] == TENANT
    assert task_reads[0]["project_id"] == LIVE


# ARTIFACT: test_project_approval_inbox_http.py
# VERSION: v1.0.0-REVOKED-PROJECT-REVIEW-INBOX-DENIAL
# AUTHORITY BOUNDARY: synthetic HTTP domain check, no live IAM grants
# TENANT POSTURE: current project evidence before display/pagination
# FAIL-CLOSED POSTURE: revoked participant work never enters reviewer inbox
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
