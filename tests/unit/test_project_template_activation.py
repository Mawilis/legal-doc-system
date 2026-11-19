"""TITLE: WILSY OS Industry Project Template Activation Certificate
VERSION: v1.2.0-SEVENTEEN-TEMPLATE-DAG-CERT
AUTHORITY: Synthetic EOS project/task transaction boundary only.
EPITOME: Validate seventeen industry DAGs, materialisation IDs, safe unassigned
         records, stable replay and exact admission without real Mongo writes.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_template_activation.py
COLLABORATION / OWNERSHIP: Projects router and immutable project/task registries.
CERTIFICATION / UPDATE DATE: 2026-11-19
CHANGELOG: v1.2.0-SEVENTEEN-TEMPLATE-DAG-CERT verifies 17 source-validated industry
         blueprints with immutable DAGs and no automatic staff authority.
CHANGELOG: v1.1.0-IMMUTABLE-TEMPLATE-REPLAY-CERT verifies replay
         reads the original immutable creation snapshot rather than
         reissuing a timestamp-sensitive create or duplicating task evidence.
CHANGELOG: v1.0.0-ATOMIC-BLUEPRINT-AUTHORITY-CERT pins seven validated
         platform blueprints and an exact-context, atomic source readback loop.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic actor, tenant, transaction and date.
TENANT BOUNDARY: Exact caller tenant only; no cross-tenant or root fallbacks.
AUTHORITY BOUNDARY: Route demands independent create and update IAM; synthetic
         mock tests do not replace authenticated HTTP authorization tests.
FINANCIAL AUTHORITY BOUNDARY: No financial mutations or approvals.
"""
from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import HTTPException, Response
import pytest

from tools.eos.api import projects_router
from tools.eos.saas.projects.project_template_catalogue import (
    get_blueprint, list_blueprints,
)


def test_seventeen_reviewed_industry_blueprints_are_detached_and_topologically_valid() -> None:
    entries = list_blueprints()
    assert len(entries) == 17
    assert {entry["industry"] for entry in entries} == {
        "Legal", "Construction", "Football", "Imports", "Software",
        "Healthcare", "General business",
    }
    for entry in entries:
        assert entry["revision"] == 1
        assert len(entry["steps"]) >= 4
        assert any(step["kind"] == "MILESTONE" for step in entry["steps"])
        seen = set()
        for step in entry["steps"]:
            assert set(step["depends_on"]).issubset(seen)
            assert step["role"] and step["acceptance"]
            seen.add(step["id"])
        assert get_blueprint(entry["slug"]) == entry
        entry["steps"][0]["title"] = "Tampered"
        assert get_blueprint(entry["slug"])["steps"][0]["title"] != "Tampered"


def test_atomic_template_activation_uses_exact_unassigned_records_and_replay(monkeypatch) -> None:
    context = SimpleNamespace(
        tenant_id="tenant-cert", identity=SimpleNamespace(identity_id="actor-cert"),
    )
    seen = {}
    committed_projects = {}
    committed_tasks = {}
    committed_events = {}

    class Projects:
        def list_events(self, *, tenant_id, project_id, session):
            assert tenant_id == "tenant-cert" and session == "tx"
            return tuple([committed_events[project_id]] if project_id in committed_events else [])

        def create_or_replay(self, *, project, actor_principal_id, idempotency_key,
                             occurred_at, session):
            assert session == "tx" and actor_principal_id == "actor-cert"
            assert project.tenant_id == "tenant-cert"
            assert project.owner_principal_id is None
            assert project.department_id is None
            assert project.status.value == "planned"
            assert idempotency_key.startswith("template-project:")
            assert project.project_id not in committed_projects, "replay must use original evidence"
            committed_projects[project.project_id] = project
            committed_events[project.project_id] = {
                "event_type": "PROJECT_CREATED",
                "idempotency_key": idempotency_key,
                "actor_principal_id": actor_principal_id,
                "result_snapshot": project.to_dict(),
            }
            return project

        def get(self, *, tenant_id, project_id, session):
            assert tenant_id == "tenant-cert" and session == "tx"
            return committed_projects[project_id]

    class Tasks:
        def create_or_replay(self, *, task, idempotency_key, session):
            assert session == "tx"
            assert task.assignee_principal_id is None
            assert task.status == "TODO"
            assert task.tenant_id == "tenant-cert"
            assert idempotency_key.startswith("template-step:")
            return committed_tasks.setdefault(task.task_id, task)

        def get(self, *, tenant_id, project_id, task_id, session):
            assert tenant_id == "tenant-cert" and session == "tx"
            result = committed_tasks[task_id]
            assert result.project_id == project_id
            return result

    project_registry = Projects()
    monkeypatch.setattr(projects_router, "_transaction",
                        lambda context, callback, write=False: callback(project_registry, "tx"))
    monkeypatch.setattr(projects_router, "_project_task_store",
                        lambda registry, tenant, project, session: Tasks())
    payload = projects_router.ProjectTemplateActivationRequest.model_validate({
        "name": "Litigation operations", "start_date": "2026-11-19",
        "template_revision": 1,
    })
    activate = lambda: projects_router.activate_project_template(
        payload=payload, response=Response(), slug="legal-litigation",
        idempotency_key="approved-once", context=context, update_context=context,
    )
    first = activate()
    second = activate()
    assert first["schema"] == "WILSY-PROJECT-TEMPLATE-ACTIVATION/V1"
    assert first["project"]["project_id"] == second["project"]["project_id"]
    assert len(first["items"]) == len(get_blueprint("legal-litigation")["steps"])
    assert len(committed_tasks) == len(first["items"])
    assert first["authority"] == {
        "financial_execution": False, "auto_assignments": False, "iam_grants": False,
    }
    assert any(row["kind"] == "MILESTONE" and row["depends_on"] for row in first["items"])
    assert all(row["revision"] == 1 for row in first["items"])
    assert first["project"]["target_date"] == "2027-01-03"


def test_template_activation_denies_unbound_actor_and_stale_revision() -> None:
    context = SimpleNamespace(tenant_id="tenant-a",
                              identity=SimpleNamespace(identity_id="actor-a"))
    foreign = SimpleNamespace(tenant_id="tenant-b",
                              identity=SimpleNamespace(identity_id="actor-a"))
    payload = projects_router.ProjectTemplateActivationRequest(
        name="Safe project", template_revision=1, start_date=date(2026, 11, 19),
    )
    with pytest.raises(HTTPException) as denied:
        projects_router.activate_project_template(
            payload=payload, response=Response(), slug="legal-litigation",
            idempotency_key="one", context=context, update_context=foreign,
        )
    assert denied.value.status_code == 403

    with pytest.raises(HTTPException) as stale:
        projects_router.activate_project_template(
            payload=payload.model_copy(update={"template_revision": 2}),
            response=Response(), slug="legal-litigation", idempotency_key="one",
            context=context, update_context=context,
        )
    assert stale.value.status_code == 409


# ARTIFACT: test_project_template_activation.py
# VERSION: v1.2.0-SEVENTEEN-TEMPLATE-DAG-CERT
# AUTHORITY BOUNDARY: synthetic tests only; authenticated IAM remains in EOS
# TENANT POSTURE: exact tenant actor and project records
# FAIL-CLOSED POSTURE: malformed data, stale revision and scope mismatches deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS only
# END OF WILSY OS SOVEREIGN ARTIFACT
