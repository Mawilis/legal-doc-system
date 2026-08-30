"""TITLE: WILSY OS Current Role Authorization Unit Contract.
VERSION: v1.0.0-WILSY-CURRENT-ROLE-AUTHORIZATION-UNIT-CONTRACT
AUTHORITY: Deterministic unit verification of current tenant-scoped role-assignment authorization decisions with injected repository outcomes only.
EPITOME: Proves role and permission authorization depends on current ACTIVE RoleAssignmentAuthority rather than projected claims.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authorization.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.0-WILSY-CURRENT-ROLE-AUTHORIZATION-UNIT-CONTRACT establishes unit evidence for exact current-role authorization, projected-claim rejection, repository failure distinction, and bounded denial.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Pure deterministic fixtures only; no credentials, tenant records, Mongo, network, secrets, or external IO.
TENANT BOUNDARY: Tests supply an already membership-admitted identity with an explicit selected tenant; membership persistence is outside this unit contract.
AUTHORITY BOUNDARY: Unit verification of authorization decision semantics only; no authentication, membership persistence, operational endpoint, or financial execution authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""
from __future__ import annotations

import pytest
from typing import Any, cast
from tools.eos.api.exceptions import ForbiddenOperationException
from tools.eos.auth.authorization import RequirePermission, RequireRole, get_role_assignment_repository
from tools.eos.auth.identity import PrincipalStatus, SovereignIdentity
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError, RoleAssignmentPersistedRecordInvalidError, RoleAssignmentRepository, RoleAssignmentRepositoryError

VERSION = "v1.0.0-WILSY-CURRENT-ROLE-AUTHORIZATION-UNIT-CONTRACT"

class StubRepository:
    """Deterministic repository substitute modeling exact assignment outcomes only."""
    def __init__(self, outcomes): self.outcomes = outcomes; self.calls = []
    def resolve(self, principal_id, tenant_id, role_id, collection=None, *, session=None):
        self.calls.append((principal_id, tenant_id, role_id))
        outcome = self.outcomes.get(role_id, "absent")
        if isinstance(outcome, BaseException): raise outcome
        if outcome == "absent": raise RoleAssignmentNotFoundError("internal-marker")
        return outcome

def identity(roles=None, permissions=None):
    """Build an already tenant-admitted identity projection for unit scope."""
    return SovereignIdentity(identity_id="principal-p", tenant_id="tenant-t", username="display", email="display@example.test", roles=roles or [], permissions=permissions or [], auth_method="JWT", status=PrincipalStatus.ACTIVE)

def active(role): return RoleAssignmentAuthority("principal-p", "tenant-t", role, RoleAssignmentStatus.ACTIVE, 0)
def revoked(role): return RoleAssignmentAuthority("principal-p", "tenant-t", role, RoleAssignmentStatus.REVOKED, 1)

@pytest.mark.anyio
async def test_require_role_requires_current_active_assignment():
    """RequireRole allows exact ACTIVE possession and rejects projected sovereign claims."""
    repo = StubRepository({"AUDITOR": active("AUDITOR")})
    result = await RequireRole(["AUDITOR"]).__call__(identity=identity(["SOVEREIGN_ARCHITECT"]), repository=cast(Any, repo))
    assert result is not None and repo.calls == [("principal-p", "tenant-t", "AUDITOR")]
    with pytest.raises(ForbiddenOperationException):
        await RequireRole(["SOVEREIGN_ARCHITECT"]).__call__(identity=identity(["SOVEREIGN_ARCHITECT"]), repository=cast(Any, StubRepository({})))

@pytest.mark.anyio
async def test_require_role_absent_revoked_and_candidates():
    """RequireRole denies absent/revoked assignments and continues explicit candidates."""
    with pytest.raises(ForbiddenOperationException): await RequireRole(["AUDITOR"]).__call__(identity=identity(), repository=cast(Any, StubRepository({})))
    assert await RequireRole(["AUDITOR", "SERVICE_WORKER"]).__call__(identity=identity(), repository=cast(Any, StubRepository({"SERVICE_WORKER": active("SERVICE_WORKER")}))) is not None
    with pytest.raises(ForbiddenOperationException): await RequireRole(["AUDITOR"]).__call__(identity=identity(), repository=cast(Any, StubRepository({"AUDITOR": revoked("AUDITOR")})))

@pytest.mark.anyio
async def test_require_role_repository_failures_stop_without_fallback():
    """Repository corruption or outage denies immediately and never falls through."""
    repo = StubRepository({"AUDITOR": RoleAssignmentRepositoryError("sensitive-internal"), "SERVICE_WORKER": active("SERVICE_WORKER")})
    with pytest.raises(ForbiddenOperationException) as error: await RequireRole(["AUDITOR", "SERVICE_WORKER"]).__call__(identity=identity(), repository=cast(Any, repo))
    assert "sensitive-internal" not in str(error.value) and repo.calls == [("principal-p", "tenant-t", "AUDITOR")]
    repo = StubRepository({"AUDITOR": RoleAssignmentPersistedRecordInvalidError("corrupt"), "SERVICE_WORKER": active("SERVICE_WORKER")})
    with pytest.raises(ForbiddenOperationException): await RequireRole(["AUDITOR", "SERVICE_WORKER"]).__call__(identity=identity(), repository=cast(Any, repo))
    assert repo.calls == [("principal-p", "tenant-t", "AUDITOR")]

@pytest.mark.anyio
async def test_require_permission_uses_definition_and_current_assignment():
    """RequirePermission ignores projected roles/permissions and requires current explicit possession."""
    repo = StubRepository({"AUDITOR": active("AUDITOR")})
    assert await RequirePermission("audit:read").__call__(identity=identity(["SERVICE_WORKER"], ["audit:read"]), repository=cast(Any, repo)) is not None
    with pytest.raises(ForbiddenOperationException): await RequirePermission("audit:read").__call__(identity=identity(["AUDITOR"], ["audit:read"]), repository=cast(Any, StubRepository({})))

@pytest.mark.anyio
async def test_require_permission_candidates_fail_closed_and_admin_all_is_literal():
    """Permission candidates continue only on absence; admin:all remains exact literal policy."""
    repo = StubRepository({"ENTERPRISE_ADMIN": active("ENTERPRISE_ADMIN")})
    with pytest.raises(ForbiddenOperationException):
        await RequirePermission("execution:trigger").__call__(identity=identity(), repository=cast(Any, repo))
    with pytest.raises(ForbiddenOperationException): await RequirePermission("admin:all").__call__(identity=identity(), repository=cast(Any, StubRepository({"SOVEREIGN_ARCHITECT": revoked("SOVEREIGN_ARCHITECT")})))
    with pytest.raises(ForbiddenOperationException):
        await RequirePermission("admin:all").__call__(identity=identity(), repository=cast(Any, StubRepository({"SOVEREIGN_ARCHITECT": active("SOVEREIGN_ARCHITECT")})))
    with pytest.raises(ForbiddenOperationException): await RequirePermission("tenant:delete").__call__(identity=identity(), repository=cast(Any, StubRepository({"SOVEREIGN_ARCHITECT": active("SOVEREIGN_ARCHITECT")})))

@pytest.mark.anyio
async def test_require_permission_unknown_malformed_and_failure_semantics():
    """Unknown/malformed permissions deny without repository access; failures stop evaluation."""
    for permission in ("", " ", "audit", "audit:read:extra", "*"):
        repo = StubRepository({"AUDITOR": active("AUDITOR")})
        with pytest.raises(ForbiddenOperationException): await RequirePermission(permission).__call__(identity=identity(), repository=cast(Any, repo))
        assert repo.calls == []
    repo = StubRepository({"ENTERPRISE_ADMIN": RoleAssignmentRepositoryError("internal") , "SERVICE_WORKER": active("SERVICE_WORKER")})
    with pytest.raises(ForbiddenOperationException): await RequirePermission("execution:trigger").__call__(identity=identity(), repository=cast(Any, repo))
    assert repo.calls == []

def test_role_assignment_provider_is_constructor_boundary():
    """Provider constructs the repository without persistence access."""
    assert isinstance(get_role_assignment_repository(), RoleAssignmentRepository)

# ARTIFACT: test_authorization.py
# VERSION: v1.0.0-WILSY-CURRENT-ROLE-AUTHORIZATION-UNIT-CONTRACT
# AUTHORITY BOUNDARY: deterministic unit verification of current tenant-scoped role and permission authorization only
# TENANT POSTURE: test identity represents an already membership-admitted explicit tenant; membership persistence remains external
# FAIL-CLOSED POSTURE: absent, revoked, malformed, unavailable, undefined, or projected-only authority never grants access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
