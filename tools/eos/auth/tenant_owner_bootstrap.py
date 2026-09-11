"""WILSY OS tenant-owner bootstrap orchestrator.

TITLE: Tenant-owner bootstrap
VERSION: v1.0.2-WILSY-TENANT-OWNER-BOOTSTRAP
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Atomically create tenant-local owner authority for an authenticated provisioner.
EPITOME: Four-write, caller-owned Mongo transaction; global principal is a precondition.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_owner_bootstrap.py
COLLABORATION / OWNERSHIP: EOS auth orchestration owns transaction; repositories remain participants.
SECURITY / PRIVACY POSTURE: Deployment-rooted authority, fixed roles, fail-closed conflicts.
TENANT BOUNDARY: Target tenant is explicit and all local authorities bind the authenticated principal.
AUTHORITY BOUNDARY: Tenant genesis only; no general administration or delegation.
FINANCIAL BOUNDARY: No financial or Kennel execution authority.
TRANSACTION BOUNDARY: Exactly four writes, one caller-owned session.
CERTIFICATION / UPDATE DATE: 2026-09-05
CHANGELOG: v1.0.2-WILSY-TENANT-OWNER-BOOTSTRAP — certify create-command adapter metadata alignment.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pymongo.client_session import ClientSession

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.pretenant_bootstrap_authority import verify_pretenant_bootstrap_authority
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository, PrincipalAuthorityNotFoundError
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository, TenantMembershipAlreadyExistsError, TenantMembershipNotFoundError
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository, RoleAssignmentAlreadyExistsError, RoleAssignmentNotFoundError
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository, TenantBusinessRoleAlreadyExistsError, TenantBusinessRoleNotFoundError
from tools.eos.saas.domain.tenant import TenantEntity
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry
from tools.eos.kernel.db import get_client

TENANT_OWNER_BOOTSTRAP_VERSION = "v1.0.2-WILSY-TENANT-OWNER-BOOTSTRAP"

def _tenant_registry_create_payload(tenant: TenantEntity) -> dict[str, object]:
    """Freeze a registry create command from the tenant domain value."""
    organization = tenant.organization.to_dict()
    return {
        "tenant_id": tenant.tenant_id,
        "name": organization["organization_name"],
        "organization_name": organization["organization_name"],
        "industry": organization["industry"],
        "plan": organization["plan"],
        "legal_name": organization["legal_name"],
        "tax_id": organization["tax_id"],
        "contact_email": organization["contact_email"],
        "regions": list(organization["regions"]),
        "status": tenant.status,
        "created_at": tenant.created_at,
        "checksum": tenant.checksum,
        "alias": tenant.alias,
        "region": tenant.region,
        "compliance_flags": tenant.compliance_flags,
        "verified": tenant.verified,
    }

class TenantOwnerBootstrapDenialCode(str, Enum):
    PRINCIPAL_NOT_FOUND = "PRINCIPAL_NOT_FOUND"
    PRINCIPAL_NOT_ACTIVE = "PRINCIPAL_NOT_ACTIVE"
    TENANT_ALREADY_EXISTS = "TENANT_ALREADY_EXISTS"
    MEMBERSHIP_ALREADY_EXISTS = "MEMBERSHIP_ALREADY_EXISTS"
    AUTHORIZATION_ROLE_ALREADY_EXISTS = "AUTHORIZATION_ROLE_ALREADY_EXISTS"
    BUSINESS_ROLE_ALREADY_EXISTS = "BUSINESS_ROLE_ALREADY_EXISTS"
    PERSISTENCE_FAILURE = "PERSISTENCE_FAILURE"
    INTERNAL_INVARIANT_FRACTURE = "INTERNAL_INVARIANT_FRACTURE"

class TenantOwnerBootstrapError(RuntimeError):
    """Bounded orchestration denial without sensitive persistence details."""
    def __init__(self, code: TenantOwnerBootstrapDenialCode) -> None:
        self.code = code
        super().__init__(code.value)

@dataclass(frozen=True, slots=True)
class TenantOwnerBootstrapResult:
    tenant: TenantEntity
    membership: TenantMembershipAuthority
    authorization_role: RoleAssignmentAuthority
    business_role: TenantBusinessRoleAuthority

def bootstrap_tenant_owner(*, identity: SovereignIdentity, tenant: TenantEntity) -> TenantOwnerBootstrapResult:
    """Atomically bootstrap one tenant for the authenticated provisioner."""
    verify_pretenant_bootstrap_authority(identity)
    try:
        authority = PrincipalAuthorityRepository.get(identity.identity_id)
    except PrincipalAuthorityNotFoundError as exc:
        raise TenantOwnerBootstrapError(TenantOwnerBootstrapDenialCode.PRINCIPAL_NOT_FOUND) from exc
    if authority.status is not PrincipalStatus.ACTIVE:
        raise TenantOwnerBootstrapError(TenantOwnerBootstrapDenialCode.PRINCIPAL_NOT_ACTIVE)
    principal_id, tenant_id = authority.principal_id, tenant.tenant_id
    membership = TenantMembershipAuthority(principal_id, tenant_id, TenantMembershipStatus.ACTIVE, 0)
    assignment = RoleAssignmentAuthority(principal_id, tenant_id, "ENTERPRISE_ADMIN", RoleAssignmentStatus.ACTIVE, 0)
    now = datetime.now(timezone.utc)
    business = TenantBusinessRoleAuthority(principal_id, tenant_id, "tenant_owner", TenantBusinessRoleStatus.ACTIVE, 0, now, None)
    tenant_create_payload = _tenant_registry_create_payload(tenant)
    client = get_client()
    if client is None:
        raise TenantOwnerBootstrapError(TenantOwnerBootstrapDenialCode.PERSISTENCE_FAILURE)
    try:
        with client.start_session() as session:
            def callback(current_session: ClientSession) -> None:
                try:
                    current = PrincipalAuthorityRepository.get(principal_id, session=current_session)
                except PrincipalAuthorityNotFoundError as exc:
                    raise TenantOwnerBootstrapError(TenantOwnerBootstrapDenialCode.PRINCIPAL_NOT_FOUND) from exc
                if current is None:
                    raise TenantOwnerBootstrapError(TenantOwnerBootstrapDenialCode.PRINCIPAL_NOT_FOUND)
                if current.status is not PrincipalStatus.ACTIVE:
                    raise TenantOwnerBootstrapError(TenantOwnerBootstrapDenialCode.PRINCIPAL_NOT_ACTIVE)
                if TenantRegistry.get(tenant_id, session=current_session) is not None:
                    raise TenantOwnerBootstrapError(TenantOwnerBootstrapDenialCode.TENANT_ALREADY_EXISTS)
                checks = (
                    (lambda: TenantMembershipRepository.resolve(principal_id, tenant_id, session=current_session), TenantMembershipNotFoundError, TenantOwnerBootstrapDenialCode.MEMBERSHIP_ALREADY_EXISTS),
                    (lambda: RoleAssignmentRepository.resolve(principal_id, tenant_id, "ENTERPRISE_ADMIN", session=current_session), RoleAssignmentNotFoundError, TenantOwnerBootstrapDenialCode.AUTHORIZATION_ROLE_ALREADY_EXISTS),
                    (lambda: TenantBusinessRoleRepository.resolve(principal_id, tenant_id, session=current_session), TenantBusinessRoleNotFoundError, TenantOwnerBootstrapDenialCode.BUSINESS_ROLE_ALREADY_EXISTS),
                )
                for check, missing, code in checks:
                    try: check()
                    except missing: continue
                    raise TenantOwnerBootstrapError(code)
                if not TenantRegistry.create(tenant_create_payload, session=current_session).get("success"):
                    raise TenantOwnerBootstrapError(TenantOwnerBootstrapDenialCode.PERSISTENCE_FAILURE)
                TenantMembershipRepository.insert(membership, session=current_session)
                RoleAssignmentRepository.insert(assignment, session=current_session)
                TenantBusinessRoleRepository.insert(business, session=current_session)
            session.with_transaction(callback)
    except TenantOwnerBootstrapError:
        raise
    except (TenantMembershipAlreadyExistsError, RoleAssignmentAlreadyExistsError, TenantBusinessRoleAlreadyExistsError) as exc:
        raise TenantOwnerBootstrapError(TenantOwnerBootstrapDenialCode.PERSISTENCE_FAILURE) from exc
    except Exception as exc:
        raise TenantOwnerBootstrapError(TenantOwnerBootstrapDenialCode.PERSISTENCE_FAILURE) from exc
    return TenantOwnerBootstrapResult(tenant, membership, assignment, business)

__all__ = ["TENANT_OWNER_BOOTSTRAP_VERSION", "TenantOwnerBootstrapDenialCode", "TenantOwnerBootstrapError", "TenantOwnerBootstrapResult", "bootstrap_tenant_owner"]

# ARTIFACT: tenant_owner_bootstrap.py
# VERSION: v1.0.2-WILSY-TENANT-OWNER-BOOTSTRAP
# AUTHORITY BOUNDARY: tenant-owner genesis only; no general administration.
# TENANT POSTURE: explicit target tenant and authenticated principal.
# FAIL-CLOSED POSTURE: authority, precondition, conflict, and transaction failures deny.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
