"""TITLE: WILSY OS Disposable Dock Operating Browser Fixture
VERSION: v1.0.0
AUTHORITY: Test-owned UUID database only; no live IAM or Founder record mutation.
EPITOME: Seed explicit synthetic Projects participation for authenticated Dock certification.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/dock_operating_cert_fixture.py
COLLABORATION / OWNERSHIP: Existing browser runner, canonical EOS app and Projects registries.
CERTIFICATION / UPDATE DATE: 2026-11-25
CHANGELOG: v1.0.0 seeds and independently verifies two real browser task lifecycles and archive records.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic tasks; session credentials remain in runner-owned private state.
TENANT BOUNDARY: UUID-owned database and synthetic tenant only; canonical wilsy is never selected.
AUTHORITY BOUNDARY: Explicit test-only grants confer no production access or Founder acceptance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively; no AI commercial entitlement is seeded.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
from typing import Any

from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from browser_cert_fixture import _owned_database, _uri, RoleAssignmentAuthority, RoleAssignmentStatus, RoleAssignmentRepository
from tools.eos.api import projects_router as projects
from tools.eos.saas.domain.project import Project, ProjectStatus
from tools.eos.saas.domain.tenant_product_entitlement import create_tenant_product_entitlement
from tools.eos.saas.entitlement import tenant_product_entitlement_registry as products
from tools.eos.saas.projects.project_task_registry import ProjectTask, task_id_for_command


def seed(state_path: Path) -> None:
    """Seed only the exact fixture DB, using real registries and majority transactions."""
    state = json.loads(state_path.read_text())
    with MongoClient(_uri(), serverSelectionTimeoutMS=5000, tz_aware=True) as client:
        db = _owned_database(client)
        if db.name != state["database_name"] or state["tenant_id"] == "wilsy":
            raise RuntimeError("DOCK_CERT_DISPOSABLE_SCOPE_REQUIRED")
        tenant = state["tenant_id"]
        person = state["actors"]["commercial_admin"]["principal_id"]
        project_id = "prj-" + "c" * 48
        stamp = datetime.now(timezone.utc)
        now = stamp.replace(microsecond=(stamp.microsecond // 1000) * 1000)
        for registry, source, event in (
            (projects.ProjectRegistry, projects.PROJECT_COLLECTION, projects.PROJECT_EVENT_COLLECTION),
            (projects.ProjectTaskRegistry, projects.PROJECT_TASK_COLLECTION, projects.PROJECT_TASK_EVENT_COLLECTION),
            (projects.ProjectParticipantRegistry, projects.PROJECT_PARTICIPANT_COLLECTION, projects.PROJECT_PARTICIPANT_EVENT_COLLECTION),
        ): registry.ensure_indexes(db[source], db[event])
        registry = projects.ProjectRegistry(db[projects.PROJECT_COLLECTION], db[projects.PROJECT_EVENT_COLLECTION])
        tasks = projects.ProjectTaskRegistry(db[projects.PROJECT_TASK_COLLECTION], db[projects.PROJECT_TASK_EVENT_COLLECTION])
        participants = projects.ProjectParticipantRegistry(db[projects.PROJECT_PARTICIPANT_COLLECTION], db[projects.PROJECT_PARTICIPANT_EVENT_COLLECTION])
        eid = projects.derive_tenant_product_entitlement_id(tenant, projects.TenantProductId.PROJECTS)
        entitlement = create_tenant_product_entitlement(tenant_id=tenant, entitlement_id=eid,
            product_id=projects.TenantProductId.PROJECTS, source_evidence_reference="synthetic-dock-browser",
            source_evidence_fingerprint="d" * 128)
        task_ids = {}
        def write(session: Any) -> None:
            for role in ("PROJECTS_TENANT_OWNER", "PROJECTS_PARTICIPANT_CONTRIBUTOR"):
                RoleAssignmentRepository.insert(RoleAssignmentAuthority(person, tenant, role, RoleAssignmentStatus.ACTIVE, 0), db["role_assignments"], session=session)
            products.create_or_replay(entitlement, db[products.HISTORY_COLLECTION], db[products.CURRENT_COLLECTION], session=session)
            products.transition(tenant_id=tenant, entitlement_id=eid, target_state="ACTIVE", expected_revision=0,
                evidence_reference="synthetic-dock-browser-active", evidence_fingerprint="e" * 128, occurred_at=now,
                history_collection=db[products.HISTORY_COLLECTION], current_collection=db[products.CURRENT_COLLECTION], session=session)
            registry.create_or_replay(project=Project(tenant_id=tenant, project_id=project_id,
                name="Synthetic Dock browser project", code="DOCK-BROWSER", summary=None,
                status=ProjectStatus.ACTIVE, owner_principal_id=person, department_id="synthetic-dock-department",
                start_date=date(2026, 11, 25), target_date=None, source_type="internal", external_source_reference=None,
                created_by_principal_id=person, updated_by_principal_id=person, created_at=now, updated_at=now),
                actor_principal_id=person, idempotency_key="dock-browser-project", occurred_at=now, session=session)
            participants.grant(tenant_id=tenant, project_id=project_id, principal_id=person, role="CONTRIBUTOR",
                actor_principal_id=person, idempotency_key="dock-browser-participant", occurred_at=now, session=session)
            for width in (1440, 390):
                key = "dock-browser-task-" + str(width)
                task_id = task_id_for_command(tenant, project_id, person, key)
                tasks.create_or_replay(task=ProjectTask(tenant_id=tenant, project_id=project_id, task_id=task_id,
                    kind="TASK", parent_task_id=None, title=f"MW-T11 browser alignment {width}",
                    description="Align authorized work, editable deterministic drafting and encrypted continuity.",
                    status="TODO", assignee_principal_id=person, due_date="2026-12-01", depends_on=(),
                    created_by_principal_id=person, updated_by_principal_id=person, created_at=now, updated_at=now),
                    idempotency_key=key, session=session)
                task_ids[str(width)] = task_id
        with client.start_session() as session:
            session.with_transaction(write, read_concern=ReadConcern("snapshot"), write_concern=WriteConcern("majority", j=True))
        state["dock_operating"] = {"project_id": project_id, "task_ids": task_ids, "principal_id": person}
        state_path.write_text(json.dumps(state), encoding="utf-8")
    print("DOCK_CERT_FIXTURE_SEEDED")


def verify(database: Any, state: dict[str, Any]) -> None:
    """Read durable source tasks, immutable receipts and encrypted owner archive only."""
    fixture = state["dock_operating"]
    tenant, person = state["tenant_id"], fixture["principal_id"]
    store = projects.ProjectTaskRegistry(database[projects.PROJECT_TASK_COLLECTION], database[projects.PROJECT_TASK_EVENT_COLLECTION])
    with database.client.start_session() as session:
        for task_id in fixture["task_ids"].values():
            current = store.get(tenant_id=tenant, project_id=fixture["project_id"], task_id=task_id, session=session)
            if current.status != "DONE" or current.revision != 3:
                raise RuntimeError("DOCK_CERT_TASK_LIFECYCLE_UNVERIFIED")
            count = database[projects.PROJECT_TASK_EVENT_COLLECTION].count_documents({
                "tenant_id": tenant, "project_id": fixture["project_id"], "task_id": task_id,
                "event_type": "PROJECT_TASK_TRANSITIONED", "actor_principal_id": person,
            }, session=session)
            if count != 2:
                raise RuntimeError("DOCK_CERT_COMMAND_RECEIPT_UNVERIFIED")
    records = list(database["wilsy_ai_conversation_history_v1"].find({"tenant_id": tenant, "principal_id": person}))
    if len(records) < 2 or any(not isinstance(row.get("ciphertext"), bytes) or "messages" in row for row in records):
        raise RuntimeError("DOCK_CERT_ENCRYPTED_HISTORY_UNVERIFIED")
    if database["wilsy_ai_usage_admissions"].count_documents({"tenant_id": tenant}):
        raise RuntimeError("DOCK_CERT_UNEXPECTED_MODEL_ADMISSION")


def main() -> None:
    """Run fixture seeding only under the existing disposable browser runner."""
    parser = argparse.ArgumentParser(); parser.add_argument("action", choices=("seed",))
    parser.add_argument("--state", required=True, type=Path)
    args = parser.parse_args(); seed(args.state)


if __name__ == "__main__":
    main()

# ARTIFACT: dock_operating_cert_fixture.py
# VERSION: v1.0.0
# AUTHORITY BOUNDARY: disposable synthetic fixture only; verifier is read-only
# TENANT POSTURE: exact UUID-owned database; no canonical Founder mutation
# FAIL-CLOSED POSTURE: missing lifecycle, receipt or encrypted archive denies certification
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
