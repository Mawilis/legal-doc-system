"""Certification for the authenticated Python EOS Projects HTTP boundary.

TITLE: WILSY OS Projects Router Contract Certificate
VERSION: v1.37.3-PROJECT-PURPOSE-INDEX-READINESS-CERT
AUTHORITY: Test-only certification of existing EOS Projects route composition.
EPITOME: Pins the HTTP contract, exact IAM operation pairs, session-owned tenant
         binding, internal-role tenant fence, strict payloads and server mount.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_projects_router_contract.py
COLLABORATION / OWNERSHIP: Consumes projects_router.py and server.py; no runtime authority.
CERTIFICATION / UPDATE DATE: 2026-11-17.
CHANGELOG:
  v1.37.3-PROJECT-PURPOSE-INDEX-READINESS-CERT verifies
  bounded purpose source/audit unique indexes are included in the canonical
  Projects startup gate before authenticated source endpoints are admitted.
  v1.37.2-CANONICAL-REQUIRE-IAM-FIELD-CERT uses the
  canonical RequireTenantAuthorization.permission_id/operation contract
  for source classification route assertions.
  v1.37.1-EXACT-PURPOSE-DEPENDENCY-CERT asserts direct existing
  RequireTenantAuthorization permission pairs rather than introspecting
  class implementation details.
  v1.37.0-PROJECT-WORK-PURPOSE-HTTP-IAM-CERT certifies distinct
  project detail GET and project:update POST for exact task purpose, strict
  revision readback and stable idempotency under no-network synthetic data.
  v1.36.0-READ-ONLY-PROJECT-LIST-RETRY-CERT proves exactly one new
  source-authenticated read transaction after PROJECT_LIST_UNAVAILABLE and
  proves 403, other 503 and persistent cursor errors never become success.
  v1.35.0-FOUNDER-CONTRIBUTOR-IAM-READBACK-CERT certifies positive explicitly initiated same-principal, exact-WILSY, current project Contributor admission through digest-only invitation and ACTIVE role assignment readback without direct role writes.
  v1.34.0-FOUNDER-CONTRIBUTOR-ADMISSION-NEGATIVE-CERT enforces canonical company, same actor, tenant-owner capacity, current Enterprise Admin invite authority and separate Projects Platform Owner decision before any role/membership/DB IO.
  v1.33.0-EXPLICIT-FOUNDER-CONTRIBUTOR-IAM-HTTP-CERT pins the new exact-project Founder contributor IAM admission POST to two independent existing IAM admission pairs and no unscoped role-grant path; user initiation and project participation remain separate prerequisites.
  v1.32.0-SEVENTEEN-INDUSTRY-CI-CERT certifies all seventeen
  platform blueprint DAGs through the existing atomic project test suite.
  v1.31.0-WORK-ACTION-CAPABILITY-AUTHORITY-CERT pins an
  exact-project update-authorized read-only capability endpoint and confirms
  zero IAM/grant mutations at this boundary.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT executes the seven-blueprint atomic
  activation/replay regression inside the pre-existing project certification
  suite, without changing the CI workflow or weakening authoritative checks.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT pins exact template catalogue read and atomic activation routes,
  including both required project:create and project:update IAM gates.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT pins the owner and current-participant
  immutable task-event GET routes to separate exact-source detail IAM,
  without permitting writes, inheritance, or cross-project discovery.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT verifies
  valid browser JSON enters the exact strict comment model over the
  FastAPI HTTP parsing boundary, while malformed mention shapes fail 422;
  no database writes or membership authority are exercised.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT admits only bounded JSON string arrays
  as strict task-comment mention tuples; rejects scalar, heterogeneous and
  oversized inputs without broadening participant authority.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT asserts one bounded exact-
  tenant profile lookup for eligible project member names, null-name fallback
  and duplicate identity rejection without creating grant or role authority.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT verifies success and denied summary paths retain unchanged source response and fail-closed HTTP authority while the new phase instrumentation receives exactly one registry read.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT proves owner-filtered registry queries bind tenant and authenticated principal with the preexisting project-read IAM, while participant discovery retains separate explicit-participation IAM.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT certifies exact ISO JSON date and project status values at strict Python-mode FastAPI request admission, preserving unknown/foreign/extra-field denial and isolated status-transition semantics.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT proves approval evidence rechecks exact provider scan/policy and immutable source fingerprints, and refuses policy drift and provider failure without external I/O in Mongo transactions.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT pins exact owner/participant clean download IAM and
  contributor-only provider scan reconciliation without a safety bypass.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT certifies
  owner-only attachment reads, current participant reads and contributor
  upload commands; no upload, download, scan or financial inherited grant.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT admits named reviewer
  inbox only through independent participant-contribute IAM; the route
  verifies each current exact-project record before revealing pending work.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT locks task approval
  request to owner update and named contributor decision to participant
  contribute; task approval read requires separately admitted context.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT pins exact-project
  co-participant list to the current participant-only read operation.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT pins recipient-only
  notification list/read receipt routes under separate participant IAM and
  exact active project/entitlement checks; no global inbox bypass.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT locks principal-scoped
  /my-projects discovery to explicit current participant IAM, no owner fallback.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT pins four task comment
  read/create routes to owner or current participant IAM and record scope.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT pins owner-authorized task edit
  to project:update / project_update and retains participant scope denial.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT pins exact tenant candidate membership
  choice reads to project owner detail IAM without granting participation.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT pins five new exact-tenant task operations
  to independent owner or participant IAM; no inferred assignee access.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT certifies independent participant IAM pairs
  and exact active project-record scope before detail or notes admission.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT verifies explicit project owner-only participant
  grant/list/revoke routes, active-grantee eligibility and non-inherited IAM.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT pins the four bounded notes endpoints to current
  project read/update permission-operation pairs; no IAM or tenant grant.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT proves customer Projects authority is separately
  assignable without adding inherited founder/admin/manager permissions and
  retains the WILSY-only platform-role fence.
  v1.30.0-ATOMIC-TEMPLATE-CI-CERT asserts EOS rejects
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
CHANGELOG: v1.30.0-ATOMIC-TEMPLATE-CI-CERT verifies only matching-tenant verified auth user names are projected, and name collisions fail closed without unauthorized cross-tenant personal disclosure.
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


VERSION = "v1.30.0-ATOMIC-TEMPLATE-CI-CERT"


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


def test_industry_template_activation_certificate_in_projects_ci(monkeypatch) -> None:
    """Include the new atomic blueprint certificate in the canonical CI suite."""
    from pathlib import Path
    from runpy import run_path

    spec = Path(__file__).with_name("test_project_template_activation.py")
    checks = run_path(str(spec))
    checks["test_seventeen_reviewed_industry_blueprints_are_detached_and_topologically_valid"]()
    checks["test_atomic_template_activation_uses_exact_unassigned_records_and_replay"](monkeypatch)
    checks["test_template_activation_denies_unbound_actor_and_stale_revision"]()


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
        ("/projects/templates", ("GET",)),
        ("/projects/templates/{slug}/activate", ("POST",)),
        ("/projects/assignment-options", ("GET",)),
        ("/projects/departments", ("POST",)),
        ("/projects/{project_id}/assignment", ("PATCH",)),
        ("/projects/founder-projects-admission", ("POST",)),
        ("/projects/{project_id}/founder-contributor-iam-admission", ("POST",)),
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
        ("/projects/{project_id}/tasks/{task_id}/events", ("GET",)),
        ("/projects/{project_id}/my-project/tasks/{task_id}/events", ("GET",)),
        ("/projects/{project_id}/tasks/{task_id}/comments", ("GET",)),
        ("/projects/{project_id}/tasks/{task_id}/comments", ("POST",)),
        ("/projects/{project_id}/my-project/tasks/{task_id}/comments", ("GET",)),
        ("/projects/{project_id}/my-project/tasks/{task_id}/comments", ("POST",)),
        ("/projects/{project_id}/task-action-capabilities", ("GET",)),
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
        ("/projects/templates", "GET"): ("project:read", "project_list"),
        ("/projects/templates/{slug}/activate", "POST"): ("project:create", "project_create"),
        ("/projects/assignment-options", "GET"): ("project:read", "project_list"),
        ("/projects/departments", "POST"): ("tenant:profile:write", "profile_update"),
        ("/projects/{project_id}/assignment", "PATCH"): ("project:update", "project_update"),
        ("/projects/founder-projects-admission", "POST"): ("tenant:membership:write", "membership_invite"),
        ("/projects/{project_id}/founder-contributor-iam-admission", "POST"): ("tenant:membership:write", "membership_invite"),
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
        ("/projects/{project_id}/tasks/{task_id}/events", "GET"): ("project:read", "project_detail"),
        ("/projects/{project_id}/my-project/tasks/{task_id}/events", "GET"): ("project:participant:read", "project_participant_detail"),
        ("/projects/{project_id}/tasks/{task_id}/comments", "GET"): ("project:read", "project_detail"),
        ("/projects/{project_id}/tasks/{task_id}/comments", "POST"): ("project:update", "project_update"),
        ("/projects/{project_id}/my-project/tasks/{task_id}/comments", "GET"): ("project:participant:read", "project_participant_detail"),
        ("/projects/{project_id}/my-project/tasks/{task_id}/comments", "POST"): ("project:participant:contribute", "project_participant_contribute"),
        ("/projects/{project_id}/task-action-capabilities", "GET"): ("project:update", "project_update"),
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
    template_activation = routes[("/projects/templates/{slug}/activate", ("POST",))]
    template_pairs = {
        (dependency.call.permission_id, dependency.call.operation)
        for dependency in template_activation.dependant.dependencies
        if isinstance(dependency.call, RequireTenantAuthorization)
    }
    assert template_pairs == {
        ("project:create", "project_create"),
        ("project:update", "project_update"),
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
    contributor_route = routes[("/projects/{project_id}/founder-contributor-iam-admission", ("POST",))]
    contributor_pairs = {
        (dependency.call.permission_id, dependency.call.operation)
        for dependency in contributor_route.dependant.dependencies
        if isinstance(dependency.call, RequireTenantAuthorization)
    }
    assert contributor_pairs == {
        ("tenant:membership:write", "membership_invite"),
        ("project:read", "project_detail"),
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


def test_founder_contributor_self_admission_denies_invalid_authority_before_io() -> None:
    """No body-supplied IAM, role inheritance, tenant alias or other actor."""
    def context(principal: str, tenant: str, business_role: str, authorization_role: str):
        identity = SovereignIdentity(
            identity_id=principal, tenant_id=tenant,
            auth_method="TEST_FIXTURE", status=PrincipalStatus.ACTIVE,
        )
        return projects_router.TenantAuthorizationContext(
            identity, tenant,
            TenantAuthorizationDecision(
                True, TenantAuthorizationReason.AUTHORIZED,
                business_role, authorization_role,
            ),
        )
    actor = context("p1", WILSY_COMPANY_TENANT_ID, "tenant_owner", "ENTERPRISE_ADMIN")
    project = context("p1", WILSY_COMPANY_TENANT_ID, "tenant_owner", "PROJECTS_PLATFORM_OWNER")
    bad = [
        (context("p1", "other-tenant", "tenant_owner", "ENTERPRISE_ADMIN"), project),
        (actor, context("p2", WILSY_COMPANY_TENANT_ID, "tenant_owner", "PROJECTS_PLATFORM_OWNER")),
        (context("p1", WILSY_COMPANY_TENANT_ID, "tenant_admin", "ENTERPRISE_ADMIN"), project),
        (context("p1", WILSY_COMPANY_TENANT_ID, "tenant_owner", "PROJECTS_PLATFORM_OWNER"), project),
        (actor, context("p1", WILSY_COMPANY_TENANT_ID, "tenant_owner", "ENTERPRISE_ADMIN")),
    ]
    for grant, reader in bad:
        with pytest.raises(HTTPException) as denial:
            projects_router.admit_founder_project_contributor_iam(
                Response(), "prj-" + "a" * 48, grant, reader,
            )
        assert denial.value.status_code == 403
        assert denial.value.detail == "PROJECT_CONTRIBUTOR_IAM_ADMISSION_DENIED"


def test_founder_contributor_admission_uses_invitation_and_active_role_readback(monkeypatch: pytest.MonkeyPatch) -> None:
    """A valid command cannot succeed from the participant roster alone."""
    class FakeSession:
        def __enter__(self): return self
        def __exit__(self, *_args): return False
        def start_transaction(self, **_kwargs): return self
    class FakeClient:
        def start_session(self): return FakeSession()
    class FakeDatabase:
        def __getitem__(self, key):
            assert key == "role_assignments"
            return object()
    def context(auth_role: str):
        identity = SovereignIdentity(
            identity_id="founder-fixture", tenant_id=WILSY_COMPANY_TENANT_ID,
            auth_method="TEST_FIXTURE", status=PrincipalStatus.ACTIVE,
        )
        return projects_router.TenantAuthorizationContext(
            identity, WILSY_COMPANY_TENANT_ID,
            TenantAuthorizationDecision(
                True, TenantAuthorizationReason.AUTHORIZED, "tenant_owner", auth_role,
            ),
        )
    active = {"granted": False}
    inspected = []
    def resolve(principal, tenant, role, **kwargs):
        assert (principal, tenant, role) == (
            "founder-fixture", WILSY_COMPANY_TENANT_ID,
            "PROJECTS_PARTICIPANT_CONTRIBUTOR",
        )
        if not active["granted"]:
            raise projects_router.RoleAssignmentNotFoundError("NOT_FOUND")
        return SimpleNamespace(status=SimpleNamespace(value="ACTIVE"))
    def invite(**kwargs):
        assert kwargs["recipient_principal_id"] == "founder-fixture"
        assert kwargs["tenant_id"] == WILSY_COMPANY_TENANT_ID
        assert kwargs["authorization_role_id"] == "PROJECTS_PARTICIPANT_CONTRIBUTOR"
        inspected.append("invited")
        return SimpleNamespace(
            invitation=SimpleNamespace(invitation_id="inv-fixture"),
            capability="synthetic-transient",
        )
    def accept(**kwargs):
        assert kwargs["invitation_id"] == "inv-fixture"
        inspected.append("accepted")
        active["granted"] = True
    def participant_read(_registry, tenant, project, _session):
        assert tenant == WILSY_COMPANY_TENANT_ID
        return SimpleNamespace(get=lambda **kwargs: SimpleNamespace(role="CONTRIBUTOR"))
    def transaction(ctx, callback):
        assert ctx.decision.authorization_role == "PROJECTS_PLATFORM_OWNER"
        return callback(object(), object())
    monkeypatch.setattr(projects_router, "_transaction", transaction)
    monkeypatch.setattr(projects_router, "_project_participants", participant_read)
    monkeypatch.setattr(projects_router.kernel_db, "get_database", lambda: FakeDatabase())
    monkeypatch.setattr(projects_router.kernel_db, "get_client", lambda: FakeClient())
    monkeypatch.setattr(projects_router.RoleAssignmentRepository, "resolve", resolve)
    monkeypatch.setattr(projects_router, "create_invitation", invite)
    monkeypatch.setattr(projects_router, "admit_invited_member", accept)
    result = projects_router.admit_founder_project_contributor_iam(
        Response(), "prj-" + "a" * 48,
        context("ENTERPRISE_ADMIN"), context("PROJECTS_PLATFORM_OWNER"),
    )
    assert inspected == ["invited", "accepted"]
    assert result["authorization_state"] == "ACTIVE"
    assert result["authorization_role"] == "PROJECTS_PARTICIPANT_CONTRIBUTOR"
    assert result["tenant_id"] == WILSY_COMPANY_TENANT_ID
    assert result["principal_id"] == "founder-fixture"
    # An ACTIVE existing assignment is strictly read back without a new invite.
    replay = projects_router.admit_founder_project_contributor_iam(
        Response(), "prj-" + "a" * 48,
        context("ENTERPRISE_ADMIN"), context("PROJECTS_PLATFORM_OWNER"),
    )
    assert replay["authorization_state"] == "ACTIVE"
    assert inspected == ["invited", "accepted"]


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
    assert "ProjectWorkPurposeRegistry.ensure_indexes(" in source
    assert "PROJECT_WORK_PURPOSE_COLLECTION" in source
    assert "PROJECT_WORK_PURPOSE_EVENT_COLLECTION" in source
    assert "PROJECT_COLLECTION" in source
    assert "PROJECT_EVENT_COLLECTION" in source
    assert "app.state.projects_indexes_ready = True" in source
    assert Path("tools/eos/saas/projects/project_registry.py").is_file()



def test_project_approval_evidence_requires_current_provider_and_exact_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A saved scan event cannot replace a current original-version provider check."""
    tenant = "synthetic-tenant"
    project = "prj-" + "a" * 48
    task = "ptk-" + "b" * 48
    attachment = "pat-" + "c" * 48
    manifest = SimpleNamespace(attachment_id=attachment, fingerprint="d" * 128)
    clearance = SimpleNamespace(
        fingerprint="e" * 128,
        policy_sha3_512="a" * 128,
        scan_evidence_sha3_512="b" * 128,
    )
    context = SimpleNamespace(tenant_id=tenant)
    checks = []

    def transaction(authorized, operation):
        assert authorized is context
        return operation(object(), object())

    def source(registry, tenant_id, project_id, task_id, attachment_id, session):
        assert (tenant_id, project_id, task_id, attachment_id) == (
            tenant, project, task, attachment,
        )
        checks.append("source")
        return manifest, clearance

    def provider(original):
        assert original is manifest
        checks.append("provider")
        return "a" * 128, "b" * 128

    monkeypatch.setattr(projects_router, "_transaction", transaction)
    monkeypatch.setattr(projects_router, "_require_cleared_project_attachment", source)
    monkeypatch.setattr(projects_router, "verify_guardduty_clean_attachment", provider)
    result = projects_router._fresh_project_approval_evidence(
        context, project, task, (attachment,), participant=False,
    )
    assert result == {attachment: ("d" * 128, "e" * 128)}
    assert checks == ["source", "provider"]


def test_project_approval_provider_drift_fails_before_decision_commit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A changed scan observation or provider outage cannot authorize a review."""
    context = SimpleNamespace(tenant_id="synthetic-tenant")
    project, task, attachment = (
        "prj-" + "a" * 48, "ptk-" + "b" * 48, "pat-" + "c" * 48,
    )
    manifest = SimpleNamespace(attachment_id=attachment, fingerprint="d" * 128)
    clearance = SimpleNamespace(
        fingerprint="e" * 128, policy_sha3_512="a" * 128,
        scan_evidence_sha3_512="b" * 128,
    )
    monkeypatch.setattr(
        projects_router, "_transaction",
        lambda authorized, operation: operation(object(), object()),
    )
    monkeypatch.setattr(
        projects_router, "_require_cleared_project_attachment",
        lambda *args: (manifest, clearance),
    )
    monkeypatch.setattr(
        projects_router, "verify_guardduty_clean_attachment",
        lambda record: ("f" * 128, "b" * 128),
    )
    with pytest.raises(HTTPException) as drift:
        projects_router._fresh_project_approval_evidence(
            context, project, task, (attachment,), participant=False,
        )
    assert drift.value.status_code == 409
    assert drift.value.detail == "PROJECT_APPROVAL_EVIDENCE_PROVIDER_CHANGED"

    def unavailable(record):
        raise projects_router.ProjectAttachmentStorageError(
            "PROJECT_ATTACHMENT_SCAN_POLICY_UNAVAILABLE",
        )

    monkeypatch.setattr(
        projects_router, "verify_guardduty_clean_attachment", unavailable,
    )
    with pytest.raises(HTTPException) as denied:
        projects_router._fresh_project_approval_evidence(
            context, project, task, (attachment,), participant=False,
        )
    assert denied.value.status_code == 503


def test_project_approval_evidence_refuses_duplicate_or_foreign_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Malformed or duplicate file references never reach provider inspection."""
    context = SimpleNamespace(tenant_id="synthetic-tenant")
    project, task = "prj-" + "a" * 48, "ptk-" + "b" * 48
    attachment = "pat-" + "c" * 48
    for references in ((attachment, attachment), ("pat-foreign",)):
        with pytest.raises(HTTPException) as denied:
            projects_router._fresh_project_approval_evidence(
                context, project, task, references, participant=False,
            )
        assert denied.value.status_code == 422



def test_project_person_names_are_tenant_bound_and_display_only() -> None:
    """The selector's human text never becomes IAM or foreign-tenant identity."""
    class Cursor:
        def __init__(self, records):
            self.records = records

        def limit(self, count):
            assert count == 2
            return self.records[:count]

    class Users:
        def __init__(self, records):
            self.records = records

        def find(self, query, projection, *, session):
            assert session == "source-session"
            assert query["tenantId"] == "tenant-a"
            assert projection["firstName"] == 1
            assert projection["lastName"] == 1
            allowed = {part["user_id"] for part in query["$or"] if "user_id" in part}
            return Cursor([
                record for record in self.records
                if record["tenantId"] == query["tenantId"]
                and record["user_id"] in allowed
            ])

    db = {"users": Users([
        {"tenantId": "tenant-a", "user_id": "owner-a",
         "firstName": "Verified", "lastName": "Owner"},
        {"tenantId": "tenant-b", "user_id": "owner-a",
         "firstName": "Foreign", "lastName": "Private"},
    ])}
    assert projects_router._exact_tenant_project_person_name(
        db, "tenant-a", "owner-a", "source-session",
    ) == {"first_name": "Verified", "last_name": "Owner"}
    assert projects_router._exact_tenant_project_person_name(
        db, "tenant-a", "owner-missing", "source-session",
    ) == {"first_name": None, "last_name": None}
    db["users"].records.append({
        "tenantId": "tenant-a", "user_id": "owner-a",
        "firstName": "Duplicate", "lastName": "Identity",
    })
    with pytest.raises(HTTPException) as denial:
        projects_router._exact_tenant_project_person_name(
            db, "tenant-a", "owner-a", "source-session",
        )
    assert denial.value.status_code == 503
    assert denial.value.detail == "PROJECT_OWNER_PROFILE_COLLISION"


def test_project_participant_page_names_are_bounded_and_tenant_scoped() -> None:
    """Names are display-only and one batched read cannot cross tenant scope."""
    class Cursor:
        def __init__(self, records):
            self.records = records
        def limit(self, count):
            assert count == 5
            return self.records[:count]

    class Users:
        records = [
            {"tenantId": "tenant-a", "user_id": "principal-one",
             "firstName": "Verified", "lastName": "Member"},
        ]
        calls = 0
        def find(self, query, projection, *, session):
            self.calls += 1
            assert session == "source-session"
            assert query["tenantId"] == "tenant-a"
            assert query["$or"][0]["user_id"]["$in"] == [
                "principal-one", "principal-two",
            ]
            assert projection["firstName"] == 1
            return Cursor(self.records)

    users = Users()
    assert projects_router._project_participant_page_names(
        {"users": users}, "tenant-a",
        ["principal-one", "principal-two"], "source-session",
    ) == {
        "principal-one": {"first_name": "Verified", "last_name": "Member"},
    }
    assert users.calls == 1
    users.records = [
        *users.records,
        {"tenantId": "tenant-a", "user_id": "principal-one",
         "firstName": "Collision", "lastName": "Duplicate"},
    ]
    with pytest.raises(HTTPException) as denied:
        projects_router._project_participant_page_names(
            {"users": users}, "tenant-a",
            ["principal-one", "principal-two"], "source-session",
        )
    assert denied.value.status_code == 503
    assert denied.value.detail == "PROJECT_PARTICIPANT_NAMES_COLLISION"


def test_task_comment_json_is_admitted_through_fastapi_http_boundary() -> None:
    """An empty browser mentions array must not cause HTTP 422 admission."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    application = FastAPI()

    @application.post("/api/projects/comment-admission", status_code=201)
    def admit(payload: projects_router.ProjectTaskCommentRequest) -> dict[str, object]:
        return {"accepted": True, "body": payload.body, "mentions": list(payload.mentions)}

    with TestClient(application) as client:
        accepted = client.post("/api/projects/comment-admission", json={
            "body": "**Development progress — 19 November 2026**\\n\\n- Verified source",
            "mentions": [],
        })
        assert accepted.status_code == 201, accepted.text
        assert accepted.json()["mentions"] == []
        assert accepted.json()["body"].startswith("**Development progress")
        invalid = client.post("/api/projects/comment-admission", json={
            "body": "Notes", "mentions": ["member", 123],
        })
        assert invalid.status_code == 422
        extra = client.post("/api/projects/comment-admission", json={
            "body": "Notes", "mentions": [], "timestamp": "forbidden",
        })
        assert extra.status_code == 422


def test_comment_json_mentions_admit_only_bounded_string_arrays() -> None:
    """Browser comment arrays are normalized without weakening strict admission."""
    from pydantic import ValidationError

    cls = projects_router.ProjectTaskCommentRequest
    assert cls.model_validate({"body": "Development progress", "mentions": []}).mentions == ()
    members = ["principal-" + str(i) for i in range(10)]
    assert cls.model_validate({"body": "Update", "mentions": members}).mentions == tuple(members)
    for invalid in ([1], [None], ["ok", 1], ["p"] * 11, "principal", {"id": "p"}):
        with pytest.raises(ValidationError):
            cls.model_validate({"body": "Update", "mentions": invalid})
    with pytest.raises(ValidationError):
        cls.model_validate({"body": "", "mentions": []})


def test_task_create_and_revision_accept_only_canonical_wire_dates() -> None:
    """Calendar JSON dates reach strict EOS admission without coercing invalid input."""
    from datetime import date
    from pydantic import ValidationError

    valid_create = {
        "kind": "MILESTONE", "title": "M01 Headquarters delivery certified",
        "description": "Verified acceptance", "due_date": "2026-11-26",
        "parent_task_id": None, "assignee_principal_id": None,
        "depends_on": [],
    }
    created = projects_router.ProjectTaskCreateRequest.model_validate(valid_create)
    assert created.due_date == date(2026, 11, 26)
    assert created.kind == "MILESTONE"
    assert created.depends_on == ()
    predecessor = "ptk-" + "a" * 48
    with_dependency = projects_router.ProjectTaskCreateRequest.model_validate({
        **valid_create, "depends_on": [predecessor],
    })
    assert with_dependency.depends_on == (predecessor,)
    for malformed in ([123], ["x"] * 26, {"not": "a list"}, "bad"):
        with pytest.raises(ValidationError):
            projects_router.ProjectTaskCreateRequest.model_validate({
                **valid_create, "depends_on": malformed,
            })
    valid_revision = {
        "expected_revision": 1, "title": "Updated milestone",
        "description": "", "due_date": "2026-11-27",
        "assignee_principal_id": None,
    }
    revised = projects_router.ProjectTaskReviseRequest.model_validate(valid_revision)
    assert revised.due_date == date(2026, 11, 27)
    for invalid in ("2026/11/26", "2026-02-30", "2026-11-26T00:00:00",
                    "26-11-2026", "2026-1-2", 20261126, False):
        for model, data in (
            (projects_router.ProjectTaskCreateRequest, valid_create),
            (projects_router.ProjectTaskReviseRequest, valid_revision),
        ):
            with pytest.raises(ValidationError):
                model.model_validate({**data, "due_date": invalid})
    with pytest.raises(ValidationError):
        projects_router.ProjectTaskCreateRequest.model_validate({
            **valid_create, "kind": "FINANCIAL",
        })


def test_canonical_projects_wire_values_keep_strict_validation() -> None:
    """FastAPI receives parsed JSON dicts; browser values must be canonical."""
    from datetime import date
    from tools.eos.saas.domain.project import ProjectStatus

    created = projects_router.ProjectCreateRequest.model_validate({
        "name": "Approved project", "start_date": "2026-11-18",
        "target_date": "2026-11-20",
    })
    assert created.start_date == date(2026, 11, 18)
    assert created.target_date == date(2026, 11, 20)

    revision = projects_router.ProjectUpdateRequest.model_validate({
        "expected_revision": 2, "start_date": "2026-11-18",
        "target_date": "2026-11-20",
    })
    assert revision.start_date == date(2026, 11, 18)
    activated = projects_router.ProjectUpdateRequest.model_validate({
        "expected_revision": 2, "status": "active",
    })
    assert activated.status is ProjectStatus.ACTIVE
    assert activated.model_dump(exclude={"expected_revision"}, exclude_unset=True) == {
        "status": ProjectStatus.ACTIVE,
    }

    for invalid in [
        {"expected_revision": 2, "start_date": "18/11/2026"},
        {"expected_revision": 2, "start_date": "2026-02-30"},
        {"expected_revision": 2, "status": "ACTIVATED"},
        {"expected_revision": "2", "status": "active"},
        {"expected_revision": 2, "status": "active", "timestamp": "untrusted"},
    ]:
        with pytest.raises(ValidationError):
            projects_router.ProjectUpdateRequest.model_validate(invalid)
    with pytest.raises(ValidationError):
        projects_router.ProjectAssignmentRequest.model_validate({
            "expected_revision": 2,
            "owner_principal_id": "eligible-current-owner",
            "department_id": "dept-" + "a" * 32,
            "timestamp": "forbidden-client-injection",
        })


@pytest.mark.parametrize("outcomes,expected_attempts,expected_error", [
    (("PROJECT_LIST_UNAVAILABLE", None), 2, None),
    (("PROJECT_LIST_UNAVAILABLE", "PROJECT_LIST_UNAVAILABLE"), 2, "PROJECT_LIST_UNAVAILABLE"),
    (("PROJECT_DATABASE_UNAVAILABLE", None), 1, "PROJECT_DATABASE_UNAVAILABLE"),
    (("PROJECT_INDEXES_NOT_READY", None), 1, "PROJECT_INDEXES_NOT_READY"),
    (("PROJECTS_ENTITLEMENT_REQUIRED", None), 1, "PROJECTS_ENTITLEMENT_REQUIRED"),
])
def test_project_list_retries_only_exact_transient_source_read(
    monkeypatch, outcomes, expected_attempts, expected_error,
) -> None:
    """One bounded whole-read retry; never retry IAM, index or unrelated faults."""
    calls = []
    context = SimpleNamespace(
        tenant_id="synthetic-tenant",
        identity=SimpleNamespace(identity_id="synthetic-reader"),
    )

    class Registry:
        def list_page_for_tenant(self, **kwargs):
            assert kwargs["tenant_id"] == context.tenant_id
            assert kwargs["session"] == "fresh-transaction"
            return (), False

    def transaction(actual, callback, **kwargs):
        assert actual is context
        assert kwargs == {}
        calls.append(True)
        outcome = outcomes[len(calls) - 1]
        if outcome:
            raise HTTPException(
                status_code=403 if outcome == "PROJECTS_ENTITLEMENT_REQUIRED" else 503,
                detail=outcome,
            )
        return callback(Registry(), "fresh-transaction")

    monkeypatch.setattr(projects_router, "_transaction", transaction)
    args = dict(
        response=Response(), limit=100, offset=0, project_status=None,
        include_archived=False, owned_by_me=False, context=context,
    )
    if expected_error:
        with pytest.raises(HTTPException) as denied:
            projects_router.list_projects(**args)
        assert denied.value.detail == expected_error
    else:
        response = projects_router.list_projects(**args)
        assert response["items"] == []
        assert response["tenant_id"] == context.tenant_id
    assert len(calls) == expected_attempts


def test_source_work_purpose_commands_require_existing_exact_project_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GET/POST retain distinct existing IAM dependencies; no new grant."""
    project = "prj-" + "a" * 48
    task_id = "ptk-" + "b" * 48
    context = SimpleNamespace(
        tenant_id="synthetic-tenant",
        identity=SimpleNamespace(identity_id="synthetic-project-owner"),
    )
    task = SimpleNamespace(task_id=task_id, tenant_id=context.tenant_id,
                           project_id=project, revision=4)
    purpose = {
        "audience": "PLATFORM_BUILD", "purpose_revision": 1,
        "evidence_ref": "project-work-purpose:synthetic",
        "source_revision": 4,
    }
    writes = []

    class Tasks:
        def get(self, **kwargs):
            assert kwargs["tenant_id"] == context.tenant_id
            assert kwargs["project_id"] == project
            assert kwargs["task_id"] == task_id
            return task

    class Purposes:
        def current_for_task(self, **kwargs):
            assert kwargs["task"] is task
            return purpose if writes else None

        def classify(self, **kwargs):
            assert kwargs["task"] is task
            assert kwargs["actor_principal_id"] == context.identity.identity_id
            assert kwargs["expected_task_revision"] == 4
            assert kwargs["expected_purpose_revision"] == 0
            assert kwargs["idempotency_key"] == "synthetic-command-key"
            writes.append(kwargs)

    calls = []
    def transaction(actor, callback, **kwargs):
        assert actor is context
        calls.append(kwargs)
        return callback(object(), "synthetic-current-session")

    monkeypatch.setattr(projects_router, "_project_task_store", lambda *_args: Tasks())
    monkeypatch.setattr(projects_router, "_work_purpose_store", lambda: Purposes())
    monkeypatch.setattr(projects_router, "_transaction", transaction)

    read_before = projects_router.read_project_task_work_purpose(
        response=Response(), project_id=project, task_id=task_id,
        context=context,
    )
    assert read_before["audience"] == "UNCLASSIFIED"
    assert read_before["purpose_revision"] == 0
    assert writes == []
    payload = projects_router.ProjectTaskWorkPurposeRequest(
        audience="PLATFORM_BUILD", reason="Source-authorized platform engineering work.",
        expected_task_revision=4, expected_purpose_revision=0,
    )
    receipt = projects_router.classify_project_task_work_purpose(
        payload=payload, response=Response(), project_id=project,
        task_id=task_id, idempotency_key="synthetic-command-key", context=context,
    )
    assert receipt["audience"] == "PLATFORM_BUILD"
    assert receipt["purpose_revision"] == 1
    assert receipt["evidence_ref"].startswith("project-work-purpose:")
    assert len(writes) == 1
    assert calls == [{}, {"write": True}]
    routes = [route for route in projects_router.router.routes
              if isinstance(route, APIRoute)]
    reads = [route for route in routes if
             route.path == "/projects/{project_id}/tasks/{task_id}/work-purpose"
             and "GET" in route.methods]
    commands = [route for route in routes if
                route.path == "/projects/{project_id}/tasks/{task_id}/work-purpose"
                and "POST" in route.methods]
    assert len(reads) == len(commands) == 1
    assert reads[0].dependant.dependencies != commands[0].dependant.dependencies
    assert projects_router._DETAIL.permission_id == "project:read"
    assert projects_router._UPDATE.permission_id == "project:update"


def test_owner_page_uses_current_authenticated_principal_not_participant_grant(monkeypatch) -> None:
    """Owner responsibility is a project-read filter, never an IAM promotion."""
    identity = SimpleNamespace(identity_id="verified-owner")
    context = SimpleNamespace(tenant_id="tenant-a", identity=identity)
    captured = []
    class Source:
        def list_page_for_tenant(self, **kwargs):
            captured.append(kwargs)
            return (), False
    monkeypatch.setattr(
        projects_router, "_transaction",
        lambda current, callback, **kwargs: callback(Source(), "tx"),
    )
    response = projects_router.list_projects(
        response=Response(), limit=100, offset=0, project_status=None,
        include_archived=False, owned_by_me=True, context=context,
    )
    assert response["items"] == []
    assert response["has_more"] is False
    assert captured == [{
        "tenant_id": "tenant-a", "session": "tx",
        "limit": 100, "offset": 0, "status": None,
        "include_archived": False, "owner_principal_id": "verified-owner",
    }]
    assert projects_router.list_my_assigned_projects.__name__ == "list_my_assigned_projects"
    from fastapi.routing import APIRoute
    routes = [
        route for route in projects_router.router.routes
        if isinstance(route, APIRoute)
    ]
    owner = next(route for route in routes if route.path == "/projects"
                 and "GET" in route.methods)
    participant = next(route for route in routes if route.path == "/projects/my-projects")
    def operation(route):
        dependency = route.dependant.dependencies[0].call
        return getattr(dependency, "permission", None), getattr(dependency, "operation", None)
    assert owner.dependant.dependencies != participant.dependant.dependencies


def test_task_action_capabilities_require_exact_project_update_authority(monkeypatch) -> None:
    """Existing update IAM permits read-only projection; no scope is granted."""
    context = SimpleNamespace(
        tenant_id="tenant-a",
        identity=SimpleNamespace(identity_id="principal-a"),
    )
    project_id = "prj-" + "a" * 48
    reads: list[tuple[str, str, str]] = []

    class Registry:
        def get(self, *, tenant_id, project_id, session):
            reads.append((tenant_id, project_id, session))
            return object()

    monkeypatch.setattr(
        projects_router, "_transaction",
        lambda authorized, callback: callback(Registry(), "exact-session")
        if authorized is context else (_ for _ in ()).throw(AssertionError("scope")),
    )
    response = Response()
    outcome = projects_router.read_project_task_action_capabilities(
        response=response, project_id=project_id, context=context,
    )
    assert outcome == {
        "schema": "WILSY-PROJECT-TASK-ACTION-CAPABILITIES/V1",
        "tenant_id": "tenant-a",
        "principal_id": "principal-a",
        "project_id": project_id,
        "can_start": True,
        "can_complete": True,
        "can_block": True,
        "can_cancel": True,
        "can_assign": True,
        "can_edit": True,
    }
    assert response.headers["cache-control"] == "no-store"
    assert reads == [("tenant-a", project_id, "exact-session")]


def test_projects_summary_phase_metrics_preserve_source_counts_and_denial(monkeypatch) -> None:
    """Instrumentation cannot substitute guessed source counts or change IAM."""
    counts = {
        "total": 1, "active": 1, "planned": 0,
        "on_hold": 0, "done": 0, "cancelled": 0,
    }
    identity = SimpleNamespace(identity_id="principal-a")
    context = SimpleNamespace(tenant_id="tenant-a", identity=identity)
    reads = []
    class Source:
        def summary_for_tenant(self, *, tenant_id, session, phase_timings):
            assert tenant_id == "tenant-a" and session == "transaction-session"
            phase_timings["cursor_first_ms"] = 0.2
            phase_timings["hydrate_ms"] = 0.1
            reads.append(tenant_id)
            return counts

    def transaction(authorized, callback, *, phase_timings):
        assert authorized is context and isinstance(phase_timings, dict)
        return callback(Source(), "transaction-session")

    monkeypatch.setattr(projects_router, "_transaction", transaction)
    response = Response()
    result = projects_router.project_summary(response=response, context=context)
    assert result == {
        "schema": "WILSY-PROJECT-SUMMARY/V1",
        "tenant_id": "tenant-a", "principal_id": "principal-a",
        "counts": counts,
    }
    assert response.headers["cache-control"] == "no-store"
    assert reads == ["tenant-a"]

    def deny(authorized, callback, *, phase_timings):
        assert authorized is context
        raise HTTPException(status_code=403, detail="PROJECTS_ENTITLEMENT_REQUIRED")

    monkeypatch.setattr(projects_router, "_transaction", deny)
    with pytest.raises(HTTPException) as denial:
        projects_router.project_summary(response=Response(), context=context)
    assert denial.value.status_code == 403
    assert denial.value.detail == "PROJECTS_ENTITLEMENT_REQUIRED"




# ARTIFACT: test_projects_router_contract.py
# VERSION: v1.37.3-PROJECT-PURPOSE-INDEX-READINESS-CERT
# AUTHORITY BOUNDARY: in-process route contract assertions only; no live role, entitlement, or persistence claim
# TENANT POSTURE: selected session tenant equality is tested with synthetic identities; no tenant records are touched
# FAIL-CLOSED POSTURE: mismatched tenant and foreign internal-role scope must deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
