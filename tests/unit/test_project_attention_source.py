"""TITLE: WILSY OS Exact-Participant Project Daily Attention Certificate
VERSION: v1.1.1-BATCH-ATTENTION-PURPOSE-CERT
AUTHORITY: Synthetic authenticated-source isolation and projection tests.
EPITOME: Verify exact principal/tenant queue, current project participation,
         blocked work, revoked visibility and denial of inherited founder IAM.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_attention_source.py
COLLABORATION / OWNERSHIP: project_attention_source, Projects router, My Work.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.1.1-BATCH-ATTENTION-PURPOSE-CERT adjusts synthetic
         collection reads for bounded batch evidence while preserving exact
         participant admission and unclassified visibility.
CHANGELOG: v1.1.0-AUDITED-PURPOSE-SOURCE-ADAPTER-CERT certifies
         missing work-purpose evidence remains visible as UNCLASSIFIED,
         forwards exact source task revision and fails closed on tampering
         while retaining existing participant/tenant scope.
CHANGELOG: v1.0.0-PROJECT-ATTENTION-SOURCE-DENIAL-CERT certifies no cross-
         principal/tenant work, no revoked participant visibility or fake due time.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Pure synthetic identities; no live tenant records.
TENANT BOUNDARY: Work source scopes assignee and every project authorization.
AUTHORITY BOUNDARY: No inherited founder, owner, task mutation or IAM creation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from tools.eos.api import project_attention_source as source
from tools.eos.saas.projects.project_task_registry import ProjectTask

TENANT = "attention-tenant"
PRINCIPAL = "participant-a"
PROJECT = "prj-" + "a" * 48
NOW = datetime(2026, 11, 18, 8, 0, tzinfo=timezone.utc)


class _Cursor:
    """Yield fake Mongo rows through the same batch_size API."""

    def __init__(self, rows):
        self.rows = rows

    def batch_size(self, count):
        assert count == 100
        return iter(self.rows)


class _Collection:
    """Check that every source read contains exact principal and tenant."""

    def __init__(self, rows):
        self.rows = rows

    def find(self, query, session):
        assert session is not None
        assert query["tenant_id"] == TENANT
        assert query["assignee_principal_id"] == PRINCIPAL
        assert set(query["status"]["$in"]) == {"TODO", "IN_PROGRESS", "BLOCKED"}
        return _Cursor(self.rows)


def _task(task_id, status):
    return ProjectTask(
        tenant_id=TENANT, project_id=PROJECT, task_id=task_id,
        kind="TASK", parent_task_id=None,
        title="Action required", description="Verified project work",
        status=status, assignee_principal_id=PRINCIPAL, due_date="2026-11-20",
        depends_on=(), created_by_principal_id="project-owner",
        updated_by_principal_id="project-owner", created_at=NOW, updated_at=NOW,
    )


def _context(role="PROJECTS_PARTICIPANT_CONTRIBUTOR"):
    return SimpleNamespace(
        tenant_id=TENANT, identity=SimpleNamespace(identity_id=PRINCIPAL),
        decision=SimpleNamespace(authorization_role=role),
    )


def _wire(monkeypatch, rows, *, active=True, role="CONTRIBUTOR"):
    class _AbsentPurpose:
        def find(self, query, *, session):
            assert session is not None
            assert query["tenant_id"] == TENANT
            assert set(query["task_id"]["$in"]).issubset({row["task_id"] for row in rows})
            return []
    database = {
        source.TASK_COLLECTION: _Collection(rows),
        source.PURPOSE_COLLECTION: _AbsentPurpose(),
        source.PURPOSE_EVENT_COLLECTION: _AbsentPurpose(),
    }
    monkeypatch.setattr(source.kernel_db, "get_database", lambda: database)
    def run(_context, callback):
        return callback(object(), object())
    monkeypatch.setattr(source.projects, "_transaction", run)
    calls = []
    class Assignments:
        def get(self, *, tenant_id, project_id, principal_id, session):
            assert (tenant_id, project_id, principal_id) == (TENANT, PROJECT, PRINCIPAL)
            return SimpleNamespace(role=role)
    def participation(context, registry, project_id, session):
        calls.append(project_id)
        if not active:
            raise source.projects.ProjectParticipantNotFound("NOT_FOUND")
        return object(), Assignments()
    monkeypatch.setattr(source.projects, "_require_current_project_participation", participation)
    return calls


def test_projects_source_includes_delegated_and_blocked_work(monkeypatch):
    tasks = [
        _task("ptk-" + "b" * 48, "TODO"),
        _task("ptk-" + "c" * 48, "BLOCKED"),
    ]
    calls = _wire(monkeypatch, [task.to_dict() for task in tasks])
    result = source.read_project_attention(
        context=_context(), tenant_id=TENANT, principal_id=PRINCIPAL,
    )
    assert [row["status"] for row in result["items"]] == ["OPEN", "BLOCKED"]
    assert all(row["tenant_id"] == TENANT for row in result["items"])
    assert all(row["project_id"] == PROJECT for row in result["items"])
    assert all(row["due_at"] is None for row in result["items"])
    assert all(row["due_date"] == "2026-11-20" for row in result["items"])
    assert all(row["revision"] == 1 and row["audience_evidence"] is None
               for row in result["items"])
    assert calls == [PROJECT]  # one authorization per distinct project


def test_revoked_or_viewer_project_is_excluded(monkeypatch):
    task = _task("ptk-" + "b" * 48, "BLOCKED")
    for active, role in ((False, "CONTRIBUTOR"), (True, "VIEWER")):
        _wire(monkeypatch, [task.to_dict()], active=active, role=role)
        result = source.read_project_attention(
            context=_context(), tenant_id=TENANT, principal_id=PRINCIPAL,
        )
        assert result == {"tenant_id": TENANT, "items": []}


@pytest.mark.parametrize("scope", [
    {"tenant_id": "foreign-tenant", "principal_id": PRINCIPAL},
    {"tenant_id": TENANT, "principal_id": "another-principal"},
])
def test_foreign_scope_rejected_without_source_read(scope):
    with pytest.raises(HTTPException) as error:
        source.read_project_attention(context=_context(), **scope)
    assert error.value.status_code == 403


def test_founder_owner_role_does_not_inherit_project_participation():
    with pytest.raises(HTTPException) as error:
        source.read_project_attention(
            context=_context(role="PROJECTS_PLATFORM_OWNER"),
            tenant_id=TENANT, principal_id=PRINCIPAL,
        )
    assert error.value.status_code == 403


def test_corrupt_task_source_denies_complete_queue(monkeypatch):
    task = _task("ptk-" + "b" * 48, "BLOCKED")
    altered = task.to_dict()
    altered["title"] = "forged title"
    _wire(monkeypatch, [altered])
    with pytest.raises(HTTPException) as error:
        source.read_project_attention(
            context=_context(), tenant_id=TENANT, principal_id=PRINCIPAL,
        )
    assert error.value.status_code == 503
    assert error.value.detail == "PROJECT_ATTENTION_SOURCE_INVALID"


# ARTIFACT: test_project_attention_source.py
# VERSION: v1.1.1-BATCH-ATTENTION-PURPOSE-CERT
# AUTHORITY BOUNDARY: synthetic source admission, no live tenant IAM
# TENANT POSTURE: exact principal and active-project record mandatory
# FAIL-CLOSED POSTURE: stale, forged, revoked and inherited authority denied
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
