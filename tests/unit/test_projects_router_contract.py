"""Certification for the authenticated Python EOS Projects HTTP boundary.

TITLE: WILSY OS Projects Router Contract Certificate
VERSION: v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT
AUTHORITY: Test-only certification of existing EOS Projects route composition.
EPITOME: Pins the HTTP contract, exact IAM operation pairs, session-owned tenant
         binding, internal-role tenant fence, strict payloads and server mount.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_projects_router_contract.py
COLLABORATION / OWNERSHIP: Consumes projects_router.py and server.py; no runtime authority.
CERTIFICATION / UPDATE DATE: 2026-11-17.
CHANGELOG:
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT pins exact owner/participant clean download IAM and
  contributor-only provider scan reconciliation without a safety bypass.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT certifies
  owner-only attachment reads, current participant reads and contributor
  upload commands; no upload, download, scan or financial inherited grant.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT admits named reviewer
  inbox only through independent participant-contribute IAM; the route
  verifies each current exact-project record before revealing pending work.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT locks task approval
  request to owner update and named contributor decision to participant
  contribute; task approval read requires separately admitted context.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT pins exact-project
  co-participant list to the current participant-only read operation.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT pins recipient-only
  notification list/read receipt routes under separate participant IAM and
  exact active project/entitlement checks; no global inbox bypass.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT locks principal-scoped
  /my-projects discovery to explicit current participant IAM, no owner fallback.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT pins four task comment
  read/create routes to owner or current participant IAM and record scope.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT pins owner-authorized task edit
  to project:update / project_update and retains participant scope denial.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT pins exact tenant candidate membership
  choice reads to project owner detail IAM without granting participation.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT pins five new exact-tenant task operations
  to independent owner or participant IAM; no inferred assignee access.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT certifies independent participant IAM pairs
  and exact active project-record scope before detail or notes admission.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT verifies explicit project owner-only participant
  grant/list/revoke routes, active-grantee eligibility and non-inherited IAM.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT pins the four bounded notes endpoints to current
  project read/update permission-operation pairs; no IAM or tenant grant.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT proves customer Projects authority is separately
  assignable without adding inherited founder/admin/manager permissions and
  retains the WILSY-only platform-role fence.
  v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT asserts EOS rejects
  activation before owner/department readback; the UI is not an authority.
  v1.3.2-DEPARTMENT-IDEMPOTENT-AUDIT-CERT verifies exact-scope
  department source writes, immutable command event, identical replay
  and divergent idempotency rejection with no implied IAM grant.
  v1.3.1-TENANT-ASSIGNMENT-CURRENTNESS-CERT checks source-backed\n  assignee currentness, rejects stale department and certifies audited CAS\n  readback without changing the real role/entitlement contract.\n  v1.3.0-TENANT-ACCOUNTABILITY-ROUTE-CERT checks source-backed directory,
  conjunctive department provisioning IAM and isolated assignment commands;
  original project CRUD and Founder gates remain mandatory.
  v1.2.0-DETERMINISTIC-PROJECT-CODE-CERT validates exact
  deterministic project-code derivation and malformed ID denial.
  v1.1.1-FOUNDER-INVITATION-AUTHORITY-CERT pins the eligible
  membership_invite admission gate and independent entitlement issuance pair.
  v1.1.0-FOUNDER-PROJECTS-ADMISSION-CONTRACT adds the explicit Founder\n  admission route IAM pair and fail-closed identity, company and capacity checks.\n  v1.0.1-PROJECTS-HTTP-PAIR-ASSERTIONS — Corrects method-key normalization in
  the exact permission/operation route matrix; certified route behavior is
  unchanged.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Pure in-process checks; no credentials, Mongo
                            connection, tenant records or mutation.
TENANT BOUNDARY: Test identities use non-production values and assert exact
                 authenticated-tenant scope; no persistence is opened.
AUTHORITY BOUNDARY: Certificate asserts transport composition only; it does not
                    claim a live role assignment, entitlement or database write.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import inspect
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Response
from fastapi.routing import APIRoute
from pydantic import ValidationError

from tools.eos.api import projects_router, server
from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization
from tools.eos.auth.roles import get_permissions_for_roles, get_roles_granting_permission
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID


VERSION = "v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT"


def test_customer_projects_owner_role_is_explicit_and_platform_role_remains_fenced() -> None:
    """Grant definitions are non-possessory and never inherited by unrelated roles."""
    grants = ("project:read", "project:create", "project:update", "project:archive")
    assert set(get_permissions_for_roles(["PROJECTS_TENANT_OWNER"])) == set(grants)
    assert set(get_permissions_for_roles(["PROJECTS_PLATFORM_OWNER"])) == set(grants)
    for role in ("TENANT_OWNER", "ENTERPRISE_ADMIN", "AUDITOR", "HR_MANAGER", "POS_OPERATOR"):
        assert not set(get_permissions_for_roles([role])).intersection(grants)
    assert "PROJECTS_TENANT_OWNER" in get_roles_granting_permission("project:read")
    foreign = SimpleNamespace(
        tenant_id="customer-a",
        decision=SimpleNamespace(authorization_role="PROJECTS_PLATFORM_OWNER"),
    )
    with pytest.raises(HTTPException) as denied:
        projects_router._require_project_role_tenant(foreign)
    assert denied.value.status_code == 403
    customer = SimpleNamespace(
        tenant_id="customer-a",
        decision=SimpleNamespace(authorization_role="PROJECTS_TENANT_OWNER"),
    )
    projects_router._require_project_role_tenant(customer)


def test_project_owner_eligibility_requires_current_principal_membership_and_tenant_owner(monkeypatch):
    """No workforce profile, browser role or foreign membership grants eligibility."""
    principal = SimpleNamespace(status=PrincipalStatus.ACTIVE)
    membership = SimpleNamespace(status=TenantMembershipStatus.ACTIVE)
    roles = (SimpleNamespace(status=TenantBusinessRoleStatus.ACTIVE, business_role="tenant_owner"),)
    monkeypatch.setattr(projects_router.PrincipalAuthorityRepository, "get", lambda *_a, **_k: principal)
    monkeypatch.setattr(projects_router.TenantMembershipRepository, "resolve", lambda *_a, **_k: membership)
    monkeypatch.setattr(projects_router.TenantBusinessRoleRepository, "resolve_all", lambda *_a, **_k: roles)
    db = {
        "principal_authorities": object(), "tenant_memberships": object(),
        "tenant_business_roles": object(),
    }
    assert projects_router._project_owner_eligible(db, "tenant-a", "principal-a", object())
    principal.status = PrincipalStatus.SUSPENDED
    assert not projects_router._project_owner_eligible(db, "tenant-a", "principal-a", object())
    principal.status = PrincipalStatus.ACTIVE
    membership.status = TenantMembershipStatus.REVOKED
    assert not projects_router._project_owner_eligible(db, "tenant-a", "principal-a", object())
    membership.status = TenantMembershipStatus.ACTIVE
    roles = (SimpleNamespace(status=TenantBusinessRoleStatus.ACTIVE, business_role="tenant_manager"),)
    assert not projects_router._project_owner_eligible(db, "tenant-a", "principal-a", object())


def test_grantee_currentness_requires_active_principal_membership_and_capacity(monkeypatch):
    """A participant grant never substitutes for current tenant identity."""
    principal = SimpleNamespace(status=PrincipalStatus.ACTIVE)
    membership = SimpleNamespace(status=TenantMembershipStatus.ACTIVE)
    roles = (SimpleNamespace(status=TenantBusinessRoleStatus.ACTIVE, business_role="tenant_manager"),)
    monkeypatch.setattr(projects_router.PrincipalAuthorityRepository, "get", lambda *_a, **_k: principal)
    monkeypatch.setattr(projects_router.TenantMembershipRepository, "resolve", lambda *_a, **_k: membership)
    monkeypatch.setattr(projects_router.TenantBusinessRoleRepository, "resolve_all", lambda *_a, **_k: roles)
    database = {
        "principal_authorities": object(), "tenant_memberships": object(),
        "tenant_business_roles": object(),
    }
    eligible = lambda: projects_router._project_participant_eligible(
        database, "tenant-a", "participant-a", object(),
    )
    assert eligible() is True
    principal.status = PrincipalStatus.SUSPENDED
    assert eligible() is False
    principal.status = PrincipalStatus.ACTIVE
    membership.status = TenantMembershipStatus.REVOKED
    assert eligible() is False
    membership.status = TenantMembershipStatus.ACTIVE
    roles[0].status = TenantBusinessRoleStatus.REVOKED
    assert eligible() is False
    assert projects_router._project_participant_eligible(
        database, "tenant-a", "", object(),
    ) is False


def test_project_participant_record_requires_current_scoped_iam(monkeypatch):
    """A record alone or an IAM role alone never authorizes project details."""
    participant = SimpleNamespace(role="VIEWER")
    project = SimpleNamespace(project_id="prj-" + "c" * 48)
    read_counts = []
    registry = SimpleNamespace(get=lambda **kwargs: read_counts.append(kwargs) or project)
    class Participants:
        def get(self, **kwargs):
            read_counts.append(kwargs)
            if kwargs["project_id"] != project.project_id:
                raise projects_router.ProjectParticipantNotFound("PROJECT_PARTICIPANT_NOT_FOUND")
            return participant
    monkeypatch.setattr(projects_router, "_project_participants", lambda *_args: Participants())
    context = SimpleNamespace(
        tenant_id="tenant-a", identity=SimpleNamespace(identity_id="principal-a"),
        decision=SimpleNamespace(authorization_role="PROJECTS_PARTICIPANT_VIEWER"),
    )
    result, _participants = projects_router._require_current_project_participation(
        context, registry, project.project_id, object(),
    )
    assert result is project
    assert all(row["tenant_id"] == "tenant-a" and row["project_id"] == project.project_id for row in read_counts)
    with pytest.raises(HTTPException) as denied:
        projects_router._require_current_project_participation(
            context, registry, project.project_id, object(), contribute=True,
        )
    assert denied.value.status_code == 403
    context.decision.authorization_role = "PROJECTS_TENANT_OWNER"
    with pytest.raises(HTTPException) as denied:
        projects_router._require_current_project_participation(
            context, registry, project.project_id, object(),
        )
    assert denied.value.status_code == 403
    context.decision.authorization_role = "PROJECTS_PARTICIPANT_CONTRIBUTOR"
    participant.role = "CONTRIBUTOR"
    projects_router._require_current_project_participation(
        context, registry, project.project_id, object(), contribute=True,
    )
    with pytest.raises(projects_router.ProjectParticipantNotFound):
        projects_router._require_current_project_participation(
            context, registry, "prj-" + "d" * 48, object(),
        )


def test_personal_project_task_transition_cannot_operate_on_another_assignee(monkeypatch):
    """Project contributor role is necessary but task-assignee equality is separate."""
    task_id = "ptk-" + "a" * 48
    project_id = "prj-" + "b" * 48
    context = SimpleNamespace(
        tenant_id="tenant-a", identity=SimpleNamespace(identity_id="participant-a"),
        decision=SimpleNamespace(authorization_role="PROJECTS_PARTICIPANT_CONTRIBUTOR"),
    )
    registry = SimpleNamespace(get=lambda **_kwargs: SimpleNamespace(project_id=project_id))
    task = SimpleNamespace(assignee_principal_id="participant-b")
    class Tasks:
        def get(self, **_kwargs):
            return task
        def transition_or_replay(self, **_kwargs):
            pytest.fail("Another person's work must not transition")
    monkeypatch.setattr(projects_router, "_require_current_project_participation", lambda *_a, **_k: (None, None))
    monkeypatch.setattr(projects_router, "_project_task_store", lambda *_a: Tasks())
    monkeypatch.setattr(projects_router, "_transaction", lambda _ctx, callback, **_kwargs: callback(registry, object()))
    with pytest.raises(HTTPException) as denied:
        projects_router.transition_assigned_project_task(
            projects_router.ProjectTaskTransitionRequest(
                expected_revision=1, status="IN_PROGRESS",
            ), Response(), project_id, task_id, "task-key", context,
        )
    assert denied.value.status_code == 403


def test_department_read_requires_exact_tenant_active_record():
    """Unknown, cross-tenant and retired departments never become selectable."""
    class Collection:
        def __init__(self, row):
            self.row = row
        def find_one(self, predicate, session=None):
            assert predicate == {"tenant_id": "tenant-a", "department_id": "dept-" + "a" * 32}
            return self.row if self.row and self.row.get("tenant_id") == predicate["tenant_id"] else None
    identity = "dept-" + "a" * 32
    row = {"tenant_id": "tenant-a", "department_id": identity,
           "name": "Engineering", "status": "ACTIVE", "revision": 1}
    assert projects_router._current_department(
        {"wilsy_tenant_departments": Collection(row)}, "tenant-a", identity, object(),
    )["name"] == "Engineering"
    for invalid in ({**row, "tenant_id": "tenant-b"}, {**row, "status": "RETIRED"}):
        with pytest.raises(HTTPException) as denied:
            projects_router._current_department(
                {"wilsy_tenant_departments": Collection(invalid)}, "tenant-a", identity, object(),
            )
        assert denied.value.status_code == 409


def test_project_activation_rejects_missing_owner_or_department(monkeypatch):
    """The generic lifecycle update cannot bypass governed accountability."""
    project_id = "prj-" + "a" * 48
    context = SimpleNamespace(
        tenant_id="tenant-a", identity=SimpleNamespace(identity_id="principal-a"),
    )
    class Registry:
        def __init__(self, owner, department):
            self.owner = owner
            self.department = department
        def get(self, **kwargs):
            return SimpleNamespace(
                owner_principal_id=self.owner, department_id=self.department,
            )
        def transition(self, **kwargs):
            pytest.fail("activation must not execute without current accountability")
    registry = Registry(None, None)
    monkeypatch.setattr(projects_router, "_transaction", lambda _ctx, callback, **_kw: callback(registry, object()))
    for owner, department in ((None, None), ("principal-owner", None), (None, "dept-" + "b" * 32)):
        registry.owner, registry.department = owner, department
        with pytest.raises(HTTPException) as rejected:
            projects_router.update_project(
                projects_router.ProjectUpdateRequest(
                    expected_revision=2, status=projects_router.ProjectStatus.ACTIVE,
                ), Response(), project_id, "activation-request", context,
            )
        assert rejected.value.status_code == 409
        assert rejected.value.detail == "PROJECT_ACCOUNTABILITY_REQUIRED"


def test_department_provision_persists_audit_and_exact_idempotent_replay(monkeypatch):
    """Department identity and event are exact-tenant, actor-bound and atomic."""
    class Collection:
        def __init__(self):
            self.rows = {}
        def find_one(self, predicate, session=None):
            return next(
                (row for row in self.rows.values()
                 if all(row.get(key) == value for key, value in predicate.items())),
                None,
            )
        def insert_one(self, value, session=None):
            assert value["_id"] not in self.rows
            self.rows[value["_id"]] = dict(value)
    collection = Collection()
    events = Collection()
    database = {
        "wilsy_tenant_departments": collection,
        "wilsy_tenant_department_events": events,
    }
    actor = SimpleNamespace(tenant_id="tenant-a", identity=SimpleNamespace(identity_id="owner-a"))
    other_actor = SimpleNamespace(tenant_id="tenant-a", identity=SimpleNamespace(identity_id="owner-b"))
    other_tenant = SimpleNamespace(tenant_id="tenant-b", identity=SimpleNamespace(identity_id="owner-a"))
    monkeypatch.setattr(projects_router.kernel_db, "get_database", lambda: database)
    session = object()
    monkeypatch.setattr(projects_router, "_transaction", lambda _context, callback, **kwargs: callback(None, session))
    request = projects_router.DepartmentCreateRequest(name="Engineering")
    first = projects_router.provision_project_department(
        request, Response(), "request-1", actor, actor,
    )
    second = projects_router.provision_project_department(
        request, Response(), "request-1", actor, actor,
    )
    assert first == second
    assert len(collection.rows) == len(events.rows) == 1
    assert next(iter(events.rows.values()))["actor_principal_id"] == "owner-a"
    assert first["department"]["name"] == "Engineering"
    assert first["tenant_id"] == "tenant-a"
    with pytest.raises(HTTPException) as different_command:
        projects_router.provision_project_department(
            projects_router.DepartmentCreateRequest(name="Operations"),
            Response(), "request-1", actor, actor,
        )
    assert different_command.value.status_code == 409
    with pytest.raises(HTTPException) as different_actor:
        projects_router.provision_project_department(
            request, Response(), "request-1", other_actor, other_actor,
        )
    assert different_actor.value.status_code == 409
    with pytest.raises(HTTPException) as mixed_scope:
        projects_router.provision_project_department(
            request, Response(), "request-2", actor, other_tenant,
        )
    assert mixed_scope.value.status_code == 403


def test_assignment_command_uses_cas_audit_and_fresh_readback(monkeypatch):
    """Only a verified owner/department pair can advance project revision."""
    project_id = "prj-" + "a" * 48
    department_id = "dept-" + "b" * 32
    context = SimpleNamespace(tenant_id="tenant-a", identity=SimpleNamespace(identity_id="principal-actor"))
    final_project = SimpleNamespace(
        fingerprint="fingerprint", owner_principal_id="principal-owner",
        department_id=department_id, revision=3, status="PLANNED",
        to_dict=lambda: {"project_id": project_id, "tenant_id": "tenant-a"},
    )
    calls = []
    class Registry:
        def update(self, **kwargs):
            calls.append(kwargs)
            return final_project
        def get(self, **kwargs):
            return final_project
        def list_events(self, **kwargs):
            return ({"event_type": "PROJECT_UPDATED"},)
    registry = Registry()
    session = object()
    monkeypatch.setattr(projects_router.kernel_db, "get_database", lambda: {})
    monkeypatch.setattr(projects_router, "_project_owner_eligible", lambda *_args: True)
    monkeypatch.setattr(projects_router, "_current_department", lambda *_args: {"status": "ACTIVE"})
    monkeypatch.setattr(projects_router, "_transaction", lambda _context, callback, **kwargs: callback(registry, session))
    result = projects_router.assign_project_accountability(
        projects_router.ProjectAssignmentRequest(
            expected_revision=2, owner_principal_id="principal-owner",
            department_id=department_id,
        ), Response(), project_id, "request-id", context,
    )
    assert result["project"]["tenant_id"] == "tenant-a"
    assert len(calls) == 1
    assert calls[0]["expected_revision"] == 2
    assert calls[0]["session"] is session
    assert calls[0]["tenant_id"] == "tenant-a"
    assert calls[0]["changes"] == {
        "owner_principal_id": "principal-owner", "department_id": department_id,
    }
    assert result["events"][0]["event_type"] == "PROJECT_UPDATED"


def test_projects_router_exposes_only_the_accepted_lifecycle_contract() -> None:
    """List, summary, detail, create, update and archive paths are exact."""
    routes = {
        (route.path, tuple(sorted(route.methods or ()))): route
        for route in projects_router.router.routes
        if isinstance(route, APIRoute)
    }
    assert set(routes) == {
        ("/projects", ("GET",)),
        ("/projects", ("POST",)),
        ("/projects/summary", ("GET",)),
        ("/projects/assignment-options", ("GET",)),
        ("/projects/departments", ("POST",)),
        ("/projects/{project_id}/assignment", ("PATCH",)),
        ("/projects/founder-projects-admission", ("POST",)),
        ("/projects/my-approvals", ("GET",)),
        ("/projects/{project_id}/tasks/{task_id}/attachments", ("GET",)),
        ("/projects/{project_id}/my-project/tasks/{task_id}/attachments", ("GET",)),
        ("/projects/{project_id}/my-project/tasks/{task_id}/attachments", ("POST",)),
        ("/projects/{project_id}/tasks/{task_id}/attachments/{attachment_id}/download", ("GET",)),
        ("/projects/{project_id}/my-project/tasks/{task_id}/attachments/{attachment_id}/download", ("GET",)),
        ("/projects/{project_id}/my-project/tasks/{task_id}/attachments/{attachment_id}/verify-scan", ("POST",)),
        ("/projects/{project_id}/tasks/{task_id}/approvals", ("GET",)),
        ("/projects/{project_id}/tasks/{task_id}/approvals", ("POST",)),
        ("/projects/{project_id}/my-project/tasks/{task_id}/approvals", ("GET",)),
        ("/projects/{project_id}/my-project/tasks/{task_id}/approvals/{approval_id}/decision", ("POST",)),
        ("/projects/{project_id}/tasks/{task_id}/comments", ("GET",)),
        ("/projects/{project_id}/tasks/{task_id}/comments", ("POST",)),
        ("/projects/{project_id}/my-project/tasks/{task_id}/comments", ("GET",)),
        ("/projects/{project_id}/my-project/tasks/{task_id}/comments", ("POST",)),
        ("/projects/{project_id}/tasks", ("GET",)),
        ("/projects/{project_id}/tasks", ("POST",)),
        ("/projects/{project_id}/tasks/{task_id}", ("PATCH",)),
        ("/projects/{project_id}/tasks/{task_id}/transition", ("POST",)),
        ("/projects/{project_id}/my-project/tasks", ("GET",)),
        ("/projects/{project_id}/my-project/tasks/{task_id}/transition", ("POST",)),
        ("/projects/{project_id}/my-project/participants", ("GET",)),
        ("/projects/{project_id}/my-project/notifications", ("GET",)),
        ("/projects/{project_id}/my-project/notifications/{notification_id}/read", ("POST",)),
        ("/projects/my-projects", ("GET",)),
        ("/projects/{project_id}/my-project", ("GET",)),
        ("/projects/{project_id}/my-project/notes", ("GET",)),
        ("/projects/{project_id}/my-project/notes", ("POST",)),
        ("/projects/{project_id}/participant-options", ("GET",)),
        ("/projects/{project_id}/participants", ("GET",)),
        ("/projects/{project_id}/participants", ("POST",)),
        ("/projects/{project_id}/participants/{participant_principal_id}/revoke", ("POST",)),
        ("/projects/{project_id}/notes", ("GET",)),
        ("/projects/{project_id}/notes", ("POST",)),
        ("/projects/{project_id}/notes/{note_id}", ("PATCH",)),
        ("/projects/{project_id}/notes/{note_id}/archive", ("POST",)),
        ("/projects/{project_id}", ("GET",)),
        ("/projects/{project_id}", ("PATCH",)),
        ("/projects/{project_id}/archive", ("POST",)),
    }
    expected = {
        ("/projects", "GET"): ("project:read", "project_list"),
        ("/projects/summary", "GET"): ("project:read", "project_list"),
        ("/projects/assignment-options", "GET"): ("project:read", "project_list"),
        ("/projects/departments", "POST"): ("tenant:profile:write", "profile_update"),
        ("/projects/{project_id}/assignment", "PATCH"): ("project:update", "project_update"),
        ("/projects/founder-projects-admission", "POST"): ("tenant:membership:write", "membership_invite"),
        ("/projects/my-approvals", "GET"): ("project:participant:contribute", "project_participant_contribute"),
        ("/projects/{project_id}/tasks/{task_id}/attachments", "GET"): ("project:read", "project_detail"),
        ("/projects/{project_id}/my-project/tasks/{task_id}/attachments", "GET"): ("project:participant:read", "project_participant_detail"),
        ("/projects/{project_id}/my-project/tasks/{task_id}/attachments", "POST"): ("project:participant:contribute", "project_participant_contribute"),
        ("/projects/{project_id}/tasks/{task_id}/attachments/{attachment_id}/download", "GET"): ("project:read", "project_detail"),
        ("/projects/{project_id}/my-project/tasks/{task_id}/attachments/{attachment_id}/download", "GET"): ("project:participant:read", "project_participant_detail"),
        ("/projects/{project_id}/my-project/tasks/{task_id}/attachments/{attachment_id}/verify-scan", "POST"): ("project:participant:contribute", "project_participant_contribute"),
        ("/projects/{project_id}/tasks/{task_id}/approvals", "GET"): ("project:read", "project_detail"),
        ("/projects/{project_id}/tasks/{task_id}/approvals", "POST"): ("project:update", "project_update"),
        ("/projects/{project_id}/my-project/tasks/{task_id}/approvals", "GET"): ("project:participant:read", "project_participant_detail"),
        ("/projects/{project_id}/my-project/tasks/{task_id}/approvals/{approval_id}/decision", "POST"): ("project:participant:contribute", "project_participant_contribute"),
        ("/projects/{project_id}/tasks/{task_id}/comments", "GET"): ("project:read", "project_detail"),
        ("/projects/{project_id}/tasks/{task_id}/comments", "POST"): ("project:update", "project_update"),
        ("/projects/{project_id}/my-project/tasks/{task_id}/comments", "GET"): ("project:participant:read", "project_participant_detail"),
        ("/projects/{project_id}/my-project/tasks/{task_id}/comments", "POST"): ("project:participant:contribute", "project_participant_contribute"),
        ("/projects/{project_id}/tasks", "GET"): ("project:read", "project_detail"),
        ("/projects/{project_id}/tasks", "POST"): ("project:update", "project_update"),
        ("/projects/{project_id}/tasks/{task_id}", "PATCH"): ("project:update", "project_update"),
        ("/projects/{project_id}/tasks/{task_id}/transition", "POST"): ("project:update", "project_update"),
        ("/projects/{project_id}/my-project/tasks", "GET"): ("project:participant:read", "project_participant_detail"),
        ("/projects/{project_id}/my-project/tasks/{task_id}/transition", "POST"): ("project:participant:contribute", "project_participant_contribute"),
        ("/projects/{project_id}/my-project/participants", "GET"): ("project:participant:read", "project_participant_detail"),
        ("/projects/{project_id}/my-project/notifications", "GET"): ("project:participant:read", "project_participant_detail"),
        ("/projects/{project_id}/my-project/notifications/{notification_id}/read", "POST"): ("project:participant:read", "project_participant_detail"),
        ("/projects/my-projects", "GET"): ("project:participant:read", "project_participant_detail"),
        ("/projects/{project_id}/my-project", "GET"): ("project:participant:read", "project_participant_detail"),
        ("/projects/{project_id}/my-project/notes", "GET"): ("project:participant:read", "project_participant_detail"),
        ("/projects/{project_id}/my-project/notes", "POST"): ("project:participant:contribute", "project_participant_contribute"),
        ("/projects/{project_id}/participant-options", "GET"): ("project:read", "project_detail"),
        ("/projects/{project_id}/participants", "GET"): ("project:read", "project_detail"),
        ("/projects/{project_id}/participants", "POST"): ("project:update", "project_update"),
        ("/projects/{project_id}/participants/{participant_principal_id}/revoke", "POST"): ("project:update", "project_update"),
        ("/projects/{project_id}/notes", "GET"): ("project:read", "project_detail"),
        ("/projects/{project_id}/notes", "POST"): ("project:update", "project_update"),
        ("/projects/{project_id}/notes/{note_id}", "PATCH"): ("project:update", "project_update"),
        ("/projects/{project_id}/notes/{note_id}/archive", "POST"): ("project:update", "project_update"),
        ("/projects/{project_id}", "GET"): ("project:read", "project_detail"),
        ("/projects", "POST"): ("project:create", "project_create"),
        ("/projects/{project_id}", "PATCH"): ("project:update", "project_update"),
        ("/projects/{project_id}/archive", "POST"): ("project:archive", "project_archive"),
    }
    for (path, methods), route in routes.items():
        method = next(iter(methods))
        dependency = next(
            item.call
            for item in route.dependant.dependencies
            if isinstance(item.call, RequireTenantAuthorization)
        )
        assert (dependency.permission_id, dependency.operation) == expected[(path, method)]
    department_route = routes[("/projects/departments", ("POST",))]
    department_pairs = {
        (dependency.call.permission_id, dependency.call.operation)
        for dependency in department_route.dependant.dependencies
        if isinstance(dependency.call, RequireTenantAuthorization)
    }
    assert department_pairs == {
        ("tenant:profile:write", "profile_update"),
        ("project:create", "project_create"),
    }
    founder_route = routes[("/projects/founder-projects-admission", ("POST",))]
    admission_pairs = {
        (dependency.call.permission_id, dependency.call.operation)
        for dependency in founder_route.dependant.dependencies
        if isinstance(dependency.call, RequireTenantAuthorization)
    }
    assert admission_pairs == {
        ("tenant:membership:write", "membership_invite"),
        ("tenant_product_entitlement:issue", "tenant_product_entitlement_issue"),
    }


def test_selected_session_tenant_must_equal_request_scope() -> None:
    """A forged tenant header cannot select another tenant for Projects."""
    identity = SovereignIdentity(
        identity_id="principal-test",
        tenant_id="tenant-a",
        auth_method="TEST_FIXTURE",
        status=PrincipalStatus.ACTIVE,
        principal_scope="GLOBAL",
        membership_revision=1,
        capacity_revision=1,
    )
    projects_router._require_selected_session_tenant(identity, "tenant-a")
    with pytest.raises(HTTPException) as mismatch:
        projects_router._require_selected_session_tenant(identity, "tenant-b")
    assert mismatch.value.status_code == 403
    assert mismatch.value.detail["error"] == "PROJECT_TENANT_SCOPE_MISMATCH"
    with pytest.raises(HTTPException) as missing:
        projects_router._require_selected_session_tenant(identity, None)
    assert missing.value.status_code == 403


def test_internal_projects_role_is_confined_to_the_canonical_company_tenant() -> None:
    """The internal grant cannot serve as a customer-tenant project role."""
    identity = SovereignIdentity(
        identity_id="principal-test",
        tenant_id=WILSY_COMPANY_TENANT_ID,
        auth_method="TEST_FIXTURE",
        status=PrincipalStatus.ACTIVE,
    )
    allowed_context = projects_router.TenantAuthorizationContext(
        identity,
        WILSY_COMPANY_TENANT_ID,
        TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
            "tenant_owner",
            "PROJECTS_PLATFORM_OWNER",
        ),
    )
    projects_router._require_project_role_tenant(allowed_context)
    foreign_identity = identity.model_copy(update={"tenant_id": "tenant-b"})
    foreign_context = projects_router.TenantAuthorizationContext(
        foreign_identity,
        "tenant-b",
        allowed_context.decision,
    )
    with pytest.raises(HTTPException) as denied:
        projects_router._require_project_role_tenant(foreign_context)
    assert denied.value.status_code == 403
    assert denied.value.detail == "PROJECT_PLATFORM_OWNER_TENANT_DENIED"


def test_founder_projects_admission_denies_wrong_tenant_role_and_actor_before_io() -> None:
    """An IAM-valid request still requires exact canonical Founder ownership."""
    def context(principal: str, tenant: str, business_role: str, auth_role: str):
        identity = SovereignIdentity(
            identity_id=principal, tenant_id=tenant, auth_method="TEST_FIXTURE",
            status=PrincipalStatus.ACTIVE,
        )
        return projects_router.TenantAuthorizationContext(
            identity, tenant,
            TenantAuthorizationDecision(
                True, TenantAuthorizationReason.AUTHORIZED, business_role, auth_role,
            ),
        )

    founder = context("p1", WILSY_COMPANY_TENANT_ID, "tenant_owner", "ENTERPRISE_ADMIN")
    cases = [
        (context("p1", "other-tenant", "tenant_owner", "ENTERPRISE_ADMIN"), founder),
        (founder, context("p2", WILSY_COMPANY_TENANT_ID, "tenant_owner", "ENTERPRISE_ADMIN")),
        (context("p1", WILSY_COMPANY_TENANT_ID, "tenant_admin", "ENTERPRISE_ADMIN"), founder),
        (founder, context("p1", WILSY_COMPANY_TENANT_ID, "tenant_owner", "TENANT_OWNER")),
    ]
    for grant, issuer in cases:
        with pytest.raises(HTTPException) as denial:
            projects_router.admit_founder_projects(grant, issuer)
        assert denial.value.status_code == 403
        assert denial.value.detail == "FOUNDER_PROJECTS_AUTHORITY_REQUIRED"


def test_browser_payload_cannot_supply_authority_or_unverified_ownership() -> None:
    """Creation and update bodies exclude tenant, actor, IDs and owner grants."""
    valid = projects_router.ProjectCreateRequest.model_validate(
        {"name": "Internal delivery", "summary": "Bounded test input"}
    )
    assert valid.name == "Internal delivery"
    for forbidden in (
        "tenant_id",
        "principal_id",
        "created_by_principal_id",
        "project_id",
        "owner_principal_id",
        "department_id",
        "status",
    ):
        with pytest.raises(ValidationError):
            projects_router.ProjectCreateRequest.model_validate(
                {"name": "Internal delivery", forbidden: "forged"}
            )
    with pytest.raises(ValidationError):
        projects_router.ProjectUpdateRequest.model_validate(
            {"expected_revision": 1, "tenant_id": "tenant-b"}
        )


def test_project_code_is_deterministic_tenant_scoped_and_replay_stable() -> None:
    """Omitted human reference derives from the immutable EOS project identity."""
    identity_one = "prj-" + "a" * 48
    identity_two = "prj-" + "a" * 32 + "b" * 16
    assert projects_router._generated_project_code(identity_one) == "PRJ-" + "A" * 16
    assert projects_router._generated_project_code(identity_one) == projects_router._generated_project_code(identity_one)
    assert projects_router._generated_project_code(identity_two) != projects_router._generated_project_code(identity_one)
    with pytest.raises(Exception, match="PROJECT_CODE_SOURCE_INVALID"):
        projects_router._generated_project_code("unsafe")


def test_projects_routes_fail_closed_until_startup_indexes_are_ready() -> None:
    """Metadata indexes gate route readiness without request-time DDL."""
    source = inspect.getsource(projects_router)
    assert "projects_indexes_ready" in source
    assert "ProjectRegistry.ensure_indexes" not in source
    assert projects_router.require_projects_indexes_ready.__doc__


def test_server_mounts_projects_once_and_bootstraps_declared_unique_indexes() -> None:
    """Canonical EOS mounts the router and startup owns its index preparation."""
    source = inspect.getsource(server)
    assert source.count('app.include_router(projects_router, prefix="/api")') == 1
    assert "from .projects_router import router as projects_router" in source
    assert "ProjectRegistry.ensure_indexes(" in source
    assert "PROJECT_COLLECTION" in source
    assert "PROJECT_EVENT_COLLECTION" in source
    assert "app.state.projects_indexes_ready = True" in source
    assert Path("tools/eos/saas/projects/project_registry.py").is_file()


# ARTIFACT: test_projects_router_contract.py
# VERSION: v1.18.0-SCANNED-ATTACHMENT-ROUTE-IAM-CERT
# AUTHORITY BOUNDARY: in-process route contract assertions only; no live role, entitlement, or persistence claim
# TENANT POSTURE: selected session tenant equality is tested with synthetic identities; no tenant records are touched
# FAIL-CLOSED POSTURE: mismatched tenant and foreign internal-role scope must deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
