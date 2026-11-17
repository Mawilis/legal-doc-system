"""Certification for the authenticated Python EOS Projects HTTP boundary.

TITLE: WILSY OS Projects Router Contract Certificate
VERSION: v1.3.0-TENANT-ACCOUNTABILITY-ROUTE-CERT
AUTHORITY: Test-only certification of existing EOS Projects route composition.
EPITOME: Pins the HTTP contract, exact IAM operation pairs, session-owned tenant
         binding, internal-role tenant fence, strict payloads and server mount.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_projects_router_contract.py
COLLABORATION / OWNERSHIP: Consumes projects_router.py and server.py; no runtime authority.
CERTIFICATION / UPDATE DATE: 2026-11-17.
CHANGELOG:
  v1.3.0-TENANT-ACCOUNTABILITY-ROUTE-CERT checks source-backed directory,
  conjunctive department provisioning IAM and isolated assignment commands;
  original project CRUD and Founder gates remain mandatory.
  v1.3.0-TENANT-ACCOUNTABILITY-ROUTE-CERT validates exact
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

import pytest
from fastapi import HTTPException
from fastapi.routing import APIRoute
from pydantic import ValidationError

from tools.eos.api import projects_router, server
from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID


VERSION = "v1.3.0-TENANT-ACCOUNTABILITY-ROUTE-CERT"


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
# VERSION: v1.3.0-TENANT-ACCOUNTABILITY-ROUTE-CERT
# AUTHORITY BOUNDARY: in-process route contract assertions only; no live role, entitlement, or persistence claim
# TENANT POSTURE: selected session tenant equality is tested with synthetic identities; no tenant records are touched
# FAIL-CLOSED POSTURE: mismatched tenant and foreign internal-role scope must deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
