"""TITLE: WILSY OS Current Role Assignment Authorization.
VERSION: v1.0.0-WILSY-CURRENT-ROLE-AUTHORIZATION
AUTHORITY: Final tenant-scoped role and permission decisions from current governed RoleAssignmentAuthority after authenticated principal and ACTIVE membership admission.
EPITOME: FastAPI authorization dependencies resolve current ACTIVE tenant-scoped assignments and never treat credential projections as possession authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/authorization.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.0-WILSY-CURRENT-ROLE-AUTHORIZATION retires projected-role authorization in favor of current tenant-scoped role assignments.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Denials are bounded; repository, token, tenant, and credential details are never exposed.
TENANT BOUNDARY: Authorization consumes get_current_tenant_identity and never infers or defaults tenant context.
AUTHORITY BOUNDARY: Owns final role and permission authorization decisions only; it does not own credentials, principal lifecycle, membership persistence, role persistence, role definitions, or financial execution.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations
from collections.abc import Sequence
from fastapi import Depends
from tools.eos.api.exceptions import ForbiddenOperationException
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.tenant_access import get_current_tenant_identity
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError, RoleAssignmentPersistedRecordInvalidError, RoleAssignmentRepository, RoleAssignmentRepositoryError
from tools.eos.auth.roles import get_roles_granting_permission

VERSION = "v1.0.0-WILSY-CURRENT-ROLE-AUTHORIZATION"

def get_role_assignment_repository() -> RoleAssignmentRepository:
    """Construct the repository while leaving database and transaction ownership external."""
    return RoleAssignmentRepository()

async def _has_active_assignment(identity: SovereignIdentity, role_id: str, repository: RoleAssignmentRepository) -> bool:
    """Resolve one exact assignment; absence may continue, infrastructure failure denies."""
    try:
        assignment = repository.resolve(identity.identity_id, identity.tenant_id, role_id)
    except RoleAssignmentNotFoundError:
        return False
    except (RoleAssignmentPersistedRecordInvalidError, RoleAssignmentRepositoryError) as error:
        raise ForbiddenOperationException("Authorization authority is unavailable.") from error
    return assignment.status is RoleAssignmentStatus.ACTIVE

class RequireRole:
    """FastAPI dependency requiring a current ACTIVE assignment for an allowed role."""
    def __init__(self, allowed_roles: Sequence[str]):
        self.allowed_roles = tuple(role for role in allowed_roles if isinstance(role, str) and role.strip()) if not isinstance(allowed_roles, (str, bytes)) else ()

    async def __call__(self, identity: SovereignIdentity = Depends(get_current_tenant_identity), repository: RoleAssignmentRepository = Depends(get_role_assignment_repository)) -> SovereignIdentity:
        """Authorize only explicit current assignments in the selected tenant."""
        for role_id in self.allowed_roles:
            if await _has_active_assignment(identity, role_id, repository):
                return identity
        raise ForbiddenOperationException("Required role is not currently authorized.")

class RequirePermission:
    """FastAPI dependency requiring a current assignment whose definition grants a permission."""
    def __init__(self, permission: str):
        self.permission = permission

    async def __call__(self, identity: SovereignIdentity = Depends(get_current_tenant_identity), repository: RoleAssignmentRepository = Depends(get_role_assignment_repository)) -> SovereignIdentity:
        """Authorize exact permission policy plus current ACTIVE assignment."""
        for role_id in get_roles_granting_permission(self.permission):
            if await _has_active_assignment(identity, role_id, repository):
                return identity
        raise ForbiddenOperationException("Required permission is not currently authorized.")

__all__ = ["RequirePermission", "RequireRole", "get_role_assignment_repository"]

# ARTIFACT: authorization.py
# VERSION: v1.0.0-WILSY-CURRENT-ROLE-AUTHORIZATION
# AUTHORITY BOUNDARY: final tenant-scoped role and permission authorization from current governed role assignments only
# TENANT POSTURE: explicit tenant context must already have passed current ACTIVE membership authority; no inference or default
# FAIL-CLOSED POSTURE: absent, revoked, malformed, unavailable, or undefined authorization authority never grants access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
