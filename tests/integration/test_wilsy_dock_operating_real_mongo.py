"""TITLE: WILSY OS Dock Vertical Operating Source Certificate
VERSION: v1.0.0
AUTHORITY: Disposable MongoDB integration evidence; injected IAM is explicitly synthetic.
EPITOME: Prove source lifecycle, receipts, encrypted continuity and quarantined plan manifests.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_dock_operating_real_mongo.py
COLLABORATION / OWNERSHIP: Canonical Projects, Dock HTTP and encrypted EOS archive.
CERTIFICATION / UPDATE DATE: 2026-11-25
CHANGELOG: v1.0.0 certifies the nonproduction vertical source journey and denial cases.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID disposable database, synthetic identities, local fake object store.
TENANT BOUNDARY: Exact source tenant/principal; no Founder or production records.
AUTHORITY BOUNDARY: Real Mongo transactions; IAM and external S3 capability are injected test seams.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively; no paid provider calls.
"""
from __future__ import annotations

import base64
from datetime import date, datetime, timezone
from hashlib import sha3_512
import os
from types import SimpleNamespace
from typing import Any, cast
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
import pytest

from tools.eos.api import projects_router as projects
from tools.eos.api import wilsy_ai_reasoning_router as dock
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.saas.domain.project import Project, ProjectStatus
from tools.eos.saas.domain.tenant_product_entitlement import create_tenant_product_entitlement
from tools.eos.saas.entitlement import tenant_product_entitlement_registry as products
from tools.eos.saas.projects.project_task_registry import ProjectTask, task_id_for_command


@pytest.fixture()
def journey(monkeypatch: pytest.MonkeyPatch):
    """Own a disposable database; preserve production transactions and source indexes."""
    uri = os.environ.get("TEST_DOCK_MONGO_URI")
    if not uri:
        pytest.skip("Explicit disposable Dock Mongo URI not configured")
    if not uri.startswith("mongodb://127.0.0.1:"):
        pytest.fail("Dock integration requires an explicit disposable loopback replica")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=3000)
    assert client.admin.command("hello").get("isWritablePrimary") is True
    db = client.get_database("wilsy_dock_cert_" + uuid4().hex,
        read_concern=ReadConcern("majority"), write_concern=WriteConcern("majority", j=True))
    tenant, person, project = "dock-tenant", "dock-person", "prj-" + "a" * 48
    now = datetime.now(timezone.utc)
    owner = TenantAuthorizationContext(tenant_id=tenant,
        identity=cast(Any, SimpleNamespace(identity_id=person, tenant_id=tenant)),
        decision=cast(Any, SimpleNamespace(authorized=True, business_role="tenant_owner", authorization_role="PROJECTS_TENANT_OWNER")))
    contributor = TenantAuthorizationContext(tenant_id=tenant, identity=owner.identity,
        decision=cast(Any, SimpleNamespace(authorized=True, business_role="tenant_owner", authorization_role="PROJECTS_PARTICIPANT_CONTRIBUTOR")))
    monkeypatch.setattr(projects.kernel_db, "get_client", lambda: client)
    monkeypatch.setattr(projects.kernel_db, "get_database", lambda: db)
    monkeypatch.setattr(dock, "_database", lambda: db)
    monkeypatch.setattr(dock, "_HISTORY_INDEXES_READY", False)
    monkeypatch.setenv("WILSY_AI_HISTORY_KEY_B64", base64.b64encode(b"K" * 32).decode())
    def start_session():
        session = client.start_session(); session.start_transaction(); return session
    monkeypatch.setattr(dock, "_start_session", start_session)
    for registry, source, event in (
        (projects.ProjectRegistry, projects.PROJECT_COLLECTION, projects.PROJECT_EVENT_COLLECTION),
        (projects.ProjectTaskRegistry, projects.PROJECT_TASK_COLLECTION, projects.PROJECT_TASK_EVENT_COLLECTION),
        (projects.ProjectParticipantRegistry, projects.PROJECT_PARTICIPANT_COLLECTION, projects.PROJECT_PARTICIPANT_EVENT_COLLECTION),
        (projects.ProjectAttachmentRegistry, projects.PROJECT_ATTACHMENT_COLLECTION, projects.PROJECT_ATTACHMENT_EVENT_COLLECTION),
    ): registry.ensure_indexes(db[source], db[event])
    products.ensure_indexes(db[products.HISTORY_COLLECTION], db[products.CURRENT_COLLECTION])
    def tx(callback):
        with client.start_session() as session:
            return session.with_transaction(callback, read_concern=ReadConcern("snapshot"), write_concern=WriteConcern("majority", j=True))
    registry = projects.ProjectRegistry(db[projects.PROJECT_COLLECTION], db[projects.PROJECT_EVENT_COLLECTION])
    entitlement_id = projects.derive_tenant_product_entitlement_id(tenant, projects.TenantProductId.PROJECTS)
    entitlement = create_tenant_product_entitlement(tenant_id=tenant, entitlement_id=entitlement_id,
        product_id=projects.TenantProductId.PROJECTS, source_evidence_reference="synthetic", source_evidence_fingerprint="c" * 128)
    def seed(session):
        products.create_or_replay(entitlement, db[products.HISTORY_COLLECTION], db[products.CURRENT_COLLECTION], session=session)
        products.transition(tenant_id=tenant, entitlement_id=entitlement_id, target_state="ACTIVE", expected_revision=0,
            evidence_reference="synthetic-active", evidence_fingerprint="d" * 128, occurred_at=now,
            history_collection=db[products.HISTORY_COLLECTION], current_collection=db[products.CURRENT_COLLECTION], session=session)
        registry.create_or_replay(project=Project(tenant_id=tenant, project_id=project, name="Synthetic Dock project", code="DOCK-CERT",
            summary=None, status=ProjectStatus.PLANNED, owner_principal_id=None, department_id=None,
            start_date=date(2026, 11, 25), target_date=None, source_type="internal", external_source_reference=None,
            created_by_principal_id=person, updated_by_principal_id=person, created_at=now, updated_at=now),
            actor_principal_id=person, idempotency_key="seed-project", occurred_at=now, session=session)
    tx(seed)
    store = projects.ProjectTaskRegistry(db[projects.PROJECT_TASK_COLLECTION], db[projects.PROJECT_TASK_EVENT_COLLECTION])
    def create(key, dependencies=()):
        task = ProjectTask(tenant_id=tenant, project_id=project, task_id=task_id_for_command(tenant, project, person, key),
            kind="TASK", parent_task_id=None, title="MW-T11 synthetic alignment", description="Review source-owned work and evidence.",
            status="TODO", assignee_principal_id=person, due_date="2026-12-01", depends_on=dependencies,
            created_by_principal_id=person, updated_by_principal_id=person, created_at=now, updated_at=now)
        return tx(lambda session: store.create_or_replay(task=task, idempotency_key=key, session=session))
    predecessor = create("predecessor"); task = create("work", (predecessor.task_id,))
    # The production participant check is tested separately with real IAM. This
    # narrow seam establishes a synthetic current contributor, not a new grant.
    monkeypatch.setattr(projects, "_require_current_project_participation", lambda *args, **kwargs: (None, None))
    app = FastAPI(); app.include_router(dock.router, prefix="/api"); app.include_router(projects.router, prefix="/api")
    app.state.projects_indexes_ready = True
    app.dependency_overrides[projects.get_current_identity] = lambda: owner.identity
    app.dependency_overrides[dock._REASONING_AUTH] = lambda: owner
    app.dependency_overrides[dock.get_reasoning_project_authority] = lambda: owner
    app.dependency_overrides[dock.get_dock_command_authorities] = lambda: {"update": owner, "contribute": contributor}
    app.dependency_overrides[projects._UPDATE] = lambda: owner
    app.dependency_overrides[projects._DETAIL] = lambda: owner
    app.dependency_overrides[projects._PARTICIPANT_CONTRIBUTE] = lambda: contributor
    app.dependency_overrides[projects._PARTICIPANT_DETAIL] = lambda: contributor
    provider_calls = []
    def quarantine(**kwargs):
        content = kwargs["stream"].read(); provider_calls.append(content)
        assert content.startswith(b"%PDF")
        return len(content), sha3_512(content).hexdigest(), "synthetic-quarantine-receipt"
    monkeypatch.setattr(projects, "store_quarantined_attachment", quarantine)
    try:
        with TestClient(app, headers={"X-Tenant-ID": tenant}) as http:
            yield SimpleNamespace(http=http, app=app, db=db, tx=tx, store=store, task=task,
                predecessor=predecessor, tenant=tenant, person=person, project=project, calls=provider_calls)
    finally:
        client.drop_database(db.name); client.close()


def test_dock_lifecycle_artifact_and_encrypted_reopen(journey) -> None:
    """Independently verify task commands, PDF manifest and encrypted task continuity."""
    j = journey; http = j.http
    args = dict(workspace="PROJECTS", project_id=j.project, task_id=j.task.task_id)
    read = http.get("/api/wilsy-ai/dock/context", params=args)
    assert read.status_code == 200, read.text
    assert read.headers["cache-control"] == "no-store"
    initial = read.json(); actions = initial["components"][1]["actions"]
    assert len(actions) == 4 and actions[-1]["kind"] == "START_TASK"
    base = f"/api/projects/{j.project}/tasks/{j.task.task_id}"
    command = dict(expected_revision=1, status="IN_PROGRESS"); headers = {"Idempotency-Key": "dock-start"}
    assert http.post(base + "/transition", json=command, headers=headers).status_code == 200
    receipt = http.get(base + "/transition-receipt", params=dict(expected_revision=1, target_status="IN_PROGRESS"), headers=headers)
    assert receipt.status_code == 200 and receipt.json()["task"]["revision"] == 2
    assert http.post(base + "/transition", json=command, headers=headers).json() == receipt.json()
    assert http.post(base + "/transition", json={**command, "status": "BLOCKED"}, headers=headers).status_code == 409
    reread = http.get("/api/wilsy-ai/dock/context", params=args).json()
    assert reread["source"]["revision"] == 2
    assert "COMPLETE_TASK" not in [action["kind"] for action in reread["components"][1]["actions"]]
    assert reread["components"][0]["blockers"] == ["A recorded predecessor is not complete."]
    assert http.post(base + "/transition", json=dict(expected_revision=2, status="DONE"), headers={"Idempotency-Key": "early-complete"}).status_code == 409
    assert http.get("/api/wilsy-ai/dock/context", params={**args, "task_revision": 1}).status_code == 409
    assert http.get(base + "/transition-receipt", params=dict(expected_revision=2, target_status="DONE"), headers={"Idempotency-Key": "unseen"}).status_code == 404
    content = b"%PDF-1.4\nSynthetic edited alignment plan\n%%EOF"
    uploaded = http.post(f"/api/projects/{j.project}/my-project/tasks/{j.task.task_id}/attachments",
        files={"file": ("alignment-plan-r2.pdf", content, "application/pdf")}, headers={"Idempotency-Key": "dock-pdf"})
    assert uploaded.status_code == 201, uploaded.text
    attachment_id = uploaded.json()["attachment"]["attachment_id"]
    manifests = http.get(base + "/attachments").json()["items"]
    assert manifests[0]["attachment_id"] == attachment_id
    assert manifests[0]["content_sha3_512"] == sha3_512(content).hexdigest()
    assert manifests[0]["state"] == "QUARANTINED" and "storage_receipt" not in manifests[0]
    thread = "session-" + str(uuid4())
    payload = dict(expected_revision=0, title="MW-T11 alignment", workspace="Projects",
        work_locator=args, messages=[dict(role="assistant", content="Plan attached; quarantine recorded.", timestamp=datetime.now(timezone.utc).isoformat())])
    saved = http.put("/api/wilsy-ai/history/" + thread, json=payload)
    assert saved.status_code == 200, saved.text
    recovered = http.get("/api/wilsy-ai/history/" + thread).json()["threads"][0]
    assert recovered["workLocator"]["task_id"] == j.task.task_id
    assert recovered["messages"][0]["content"] == payload["messages"][0]["content"]
    row = j.db[dock._HISTORY_COLLECTION].find_one({"thread_id": thread})
    assert "MW-T11" not in str(row) and "Plan attached" not in str(row)
    assert isinstance(row["ciphertext"], bytes)
    assert http.put("/api/wilsy-ai/history/" + thread, json=payload).status_code == 409
    assert http.delete("/api/wilsy-ai/history/" + thread, params={"expected_revision": 1}).status_code == 200
    assert http.get("/api/wilsy-ai/history/" + thread).status_code == 404
    assert len(j.calls) == 1
    assert j.db["wilsy_ai_usage_admissions"].count_documents({}) == 0


def test_completion_eligibility_and_foreign_receipt_isolation(journey) -> None:
    """Canonical predecessor completion changes eligibility; foreign lookups disclose no receipt."""
    j = journey
    for item, key in ((j.predecessor, "pre"), (j.task, "main")):
        base = f"/api/projects/{j.project}/tasks/{item.task_id}"
        j.http.post(base + "/transition", json=dict(expected_revision=1, status="IN_PROGRESS"), headers={"Idempotency-Key": key + "-start"}).raise_for_status()
        j.http.post(base + "/transition", json=dict(expected_revision=2, status="DONE"), headers={"Idempotency-Key": key + "-done"}).raise_for_status()
    current = j.tx(lambda session: j.store.get(tenant_id=j.tenant, project_id=j.project, task_id=j.task.task_id, session=session))
    assert current.status == "DONE" and current.revision == 3
    j.app.dependency_overrides[dock.get_reasoning_project_authority] = lambda: TenantAuthorizationContext(
        tenant_id="foreign", identity=cast(Any, SimpleNamespace(identity_id=j.person)), decision=cast(Any, SimpleNamespace(authorized=True, business_role="tenant_owner")))
    response = j.http.get("/api/wilsy-ai/dock/context", params=dict(workspace="PROJECTS", project_id=j.project, task_id=j.task.task_id))
    assert response.status_code == 403


# ARTIFACT: test_wilsy_dock_operating_real_mongo.py
# VERSION: v1.0.0
# AUTHORITY BOUNDARY: disposable source persistence; synthetic IAM and object transport
# TENANT POSTURE: exact scoped source and encrypted owner readback
# FAIL-CLOSED POSTURE: stale revisions, divergent keys and completion blockers denied
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT

