"""Certification for the authenticated Python EOS Projects HTTP boundary.

TITLE: WILSY OS Projects Router Contract Certificate
VERSION: v1.5.0-EXACT-NOTE-RECORD-ACCESS-CERT
AUTHORITY: Test-only certification of existing EOS Projects route composition.
EPITOME: Pins the HTTP contract, exact IAM operation pairs, session-owned tenant
         binding, internal-role tenant fence, strict payloads and server mount.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_projects_router_contract.py
COLLABORATION / OWNERSHIP: Consumes projects_router.py and server.py; no runtime authority.
CERTIFICATION / UPDATE DATE: 2026-11-17.
CHANGELOG:
  v1.5.0-EXACT-NOTE-RECORD-ACCESS-CERT proves note read/update route
  permission separation, record-scope denial before source reads, no
  browser-authored actors and explicit startup note index admission.
  v1.4.0-SOURCE-PROJECT-WORK-AUTH-CERT verifies conjunctive Projects and
  Operations route IAM, exact tenant/principal, source-owned task creation,
  transactional task readback, idempotent replay and startup index admission.
  v1.3.3-PROJECT-ACTIVATION-ACCOUNTABILITY-CERT asserts EOS rejects
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

from tools.eos.api import projects_router, project_work_router, project_notes_router, server
from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID


VERSION = "v1.5.0-EXACT-NOTE-RECORD-ACCESS-CERT"


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



def test_project_work_requires_three_independent_permissions_and_startup_indexes() -> None:
    """Project work is a source adapter, never an inherited Founder task grant."""
    routes = [route for route in project_work_router.router.routes
              if isinstance(route, APIRoute)]
    assert [(route.path, route.methods) for route in routes] == [
        ("/projects/{project_id}/work-items", {"POST"}),
    ]
    pairs = {
        (item.call.permission_id, item.call.operation)
        for item in routes[0].dependant.dependencies
        if isinstance(item.call, RequireTenantAuthorization)
    }
    assert pairs == {
        ("project:read", "project_detail"),
        ("project:update", "project_update"),
        ("operations:work_item:create", "operations_work_item_create"),
    }
    with pytest.raises(ValidationError):
        project_work_router.ProjectWorkCreateRequest.model_validate(
            {"title": "Task", "assignee_principal_id": "invented-employee"}
        )
    with pytest.raises(HTTPException) as unavailable:
        project_work_router.require_project_work_indexes_ready(
            SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(
                project_work_indexes_ready=False,
            )))
        )
    assert unavailable.value.status_code == 503
    assert "ensure_project_work_indexes(" in inspect.getsource(server)
    assert inspect.getsource(server).count(
        'app.include_router(project_work_router, prefix="/api")'
    ) == 1


def test_project_work_create_uses_same_source_session_and_readback(monkeypatch) -> None:
    """A Planned project can originate work without assignment or activation."""
    project_id = "prj-" + "a" * 48
    scope = SimpleNamespace(
        tenant_id="tenant-a", identity=SimpleNamespace(identity_id="principal-a"),
    )
    transaction_session = object()
    project = SimpleNamespace(project_id=project_id, status=projects_router.ProjectStatus.PLANNED)

    class Projects:
        def get(self, **kwargs):
            assert kwargs == {
                "tenant_id": "tenant-a", "project_id": project_id,
                "session": transaction_session,
            }
            return project

    created = []
    class SourceWork:
        def get(self, **kwargs):
            assert kwargs["session"] is transaction_session
            assert kwargs["tenant_id"] == "tenant-a"
            if not created:
                raise project_work_router.ModuleWorkRegistryNotFound("MODULE_WORK_NOT_FOUND")
            return created[0]

    class SourceService:
        def _require_product(self, tenant_id, session):
            assert tenant_id == "tenant-a" and session is transaction_session
        def create(self, **kwargs):
            assert kwargs["tenant_id"] == "tenant-a"
            assert kwargs["principal_id"] == "principal-a"
            assert kwargs["source_type"] == "PROJECT"
            assert kwargs["source_id"] == project_id
            assert kwargs["session"] is transaction_session
            assert kwargs["kind"] is project_work_router.ModuleWorkKind.TASK
            value = SimpleNamespace(
                source_type="PROJECT", source_id=project_id, tenant_id="tenant-a",
                created_by_principal_id="principal-a", title="Build implementation",
                description="Verified instructions",
                priority=project_work_router.ModuleWorkPriority.NORMAL,
                kind=project_work_router.ModuleWorkKind.TASK,
                due_at=None, work_item_id="tmw_" + "b" * 32,
            )
            value.to_dict = lambda: {
                "work_item_id": value.work_item_id, "tenant_id": value.tenant_id,
                "source_type": "PROJECT", "source_id": project_id,
                "title": value.title,
            }
            created.append(value)
            return value

    monkeypatch.setattr(
        project_work_router, "_transaction",
        lambda context, callback, **kw: callback(Projects(), transaction_session),
    )
    monkeypatch.setattr(project_work_router.kernel_db, "get_database", lambda: {})
    monkeypatch.setattr(
        project_work_router, "_operations_service",
        lambda _db: (SourceService(), SourceWork()),
    )
    body = project_work_router.ProjectWorkCreateRequest(
        title="Build implementation", description="Verified instructions",
    )
    result = project_work_router.create_project_work_item(
        body, Response(), project_id, "stable-key", scope, scope, scope,
    )
    assert result["schema"] == "WILSY-PROJECT-WORK-RESULT/V1"
    assert result["work_item"]["source_id"] == project_id
    assert result["project_status"] == "planned"
    assert not result["replayed"]
    again = project_work_router.create_project_work_item(
        body, Response(), project_id, "stable-key", scope, scope, scope,
    )
    assert again["replayed"]
    assert len(created) == 1


def test_project_work_rejects_foreign_session_authority_before_io(monkeypatch) -> None:
    """A user with one tenant's rights cannot combine another tenant's grants."""
    scope = SimpleNamespace(
        tenant_id="tenant-a", identity=SimpleNamespace(identity_id="principal-a"),
    )
    foreign = SimpleNamespace(
        tenant_id="tenant-b", identity=SimpleNamespace(identity_id="principal-a"),
    )
    monkeypatch.setattr(
        project_work_router, "_transaction",
        lambda *_a, **_k: pytest.fail("no transaction permitted"),
    )
    with pytest.raises(HTTPException) as denial:
        project_work_router.create_project_work_item(
            project_work_router.ProjectWorkCreateRequest(title="No foreign task"),
            Response(), "prj-" + "a" * 48, "stable-key", scope, scope, foreign,
        )
    assert denial.value.status_code == 403




def test_project_notes_api_requires_current_project_read_and_write() -> None:
    """Notes never imply company-wide discussion access from module admission."""
    routes = {
        (route.path, next(iter(route.methods))): route
        for route in project_notes_router.router.routes
        if isinstance(route, APIRoute)
    }
    assert set(routes) == {
        ("/projects/{project_id}/notes", "GET"),
        ("/projects/{project_id}/notes", "POST"),
        ("/projects/{project_id}/notes/{note_id}", "PATCH"),
        ("/projects/{project_id}/notes/{note_id}/redact", "POST"),
    }
    for (path, method), route in routes.items():
        pairs = {
            (item.call.permission_id, item.call.operation)
            for item in route.dependant.dependencies
            if isinstance(item.call, RequireTenantAuthorization)
        }
        required = {("project:read", "project_detail")}
        if method != "GET":
            required.add(("project:update", "project_update"))
        assert pairs == required
    with pytest.raises(ValidationError):
        project_notes_router.ProjectNoteCreateRequest.model_validate(
            {"body": "Untrusted owner", "author_principal_id": "fake-author"}
        )
    assert "ProjectNotesRegistry.ensure_indexes(" in inspect.getsource(server)
    assert inspect.getsource(server).count(
        'app.include_router(project_notes_router, prefix="/api")'
    ) == 1


def test_project_notes_reject_nonparticipant_record_reader_before_source_io(monkeypatch):
    """An independently admitted tenant role is not a project-note grant."""
    project_id = "prj-" + "a" * 48
    context = SimpleNamespace(
        tenant_id="tenant-a", identity=SimpleNamespace(identity_id="other-member"),
    )
    class ProjectSource:
        def get(self, **kwargs):
            assert kwargs["tenant_id"] == "tenant-a"
            assert kwargs["project_id"] == project_id
            return SimpleNamespace(
                created_by_principal_id="original-author",
                owner_principal_id=None,
            )
    monkeypatch.setattr(
        project_notes_router, "_transaction",
        lambda _ctx, callback, **kwargs: callback(ProjectSource(), object()),
    )
    monkeypatch.setattr(
        project_notes_router.kernel_db, "get_database",
        lambda: pytest.fail("a nonparticipant cannot inspect notes database"),
    )
    with pytest.raises(HTTPException) as denied:
        project_notes_router.list_project_notes(
            Response(), project_id, 50, 0, context,
        )
    assert denied.value.status_code == 403
    assert denied.value.detail == "PROJECT_NOTE_RECORD_SCOPE_REQUIRED"



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
# VERSION: v1.5.0-EXACT-NOTE-RECORD-ACCESS-CERT
# AUTHORITY BOUNDARY: in-process route contract assertions only; no live role, entitlement, or persistence claim
# TENANT POSTURE: selected session tenant equality is tested with synthetic identities; no tenant records are touched
# FAIL-CLOSED POSTURE: mismatched tenant and foreign internal-role scope must deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
