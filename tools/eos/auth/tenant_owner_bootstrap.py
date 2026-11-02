"""WILSY OS tenant-owner bootstrap fail-closed authority boundary.

TITLE: Tenant-owner bootstrap
VERSION: v1.0.3-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK
AUTHORITY: Wilsy OS Core Governance
EPITOME: Preserve the pretenant deployment gate while denying owner issuance
         until an independent legal-entity ownership verifier is configured.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_owner_bootstrap.py
COLLABORATION / OWNERSHIP: EOS auth orchestration; Principal, tenant,
                           membership, role and business-role repositories
                           remain canonical persistence owners.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG: 2026-11-02 v1.0.3-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK preserves deployment-rooted pretenant verification and denies tenant genesis because no independent legal-entity ownership evidence authority is configured.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No ownership is inferred from login, email, JWT
                            claims, a requested tenant id, or provisioner status.
TENANT BOUNDARY: No tenant, membership, authorization role, or business role is
                 created while the ownership verifier is unavailable.
AUTHORITY BOUNDARY: Deployment authority may request genesis; it cannot prove
                    legal-entity ownership or authorize owner issuance.
FINANCIAL AUTHORITY BOUNDARY: No financial or Kennel execution authority.
FAIL-CLOSED POSTURE: Every authorized bootstrap request denies with the stable
                     OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE code.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.pretenant_bootstrap_authority import (
    verify_pretenant_bootstrap_authority,
)
from tools.eos.auth.role_assignment import RoleAssignmentAuthority
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority
from tools.eos.auth.tenant_membership import TenantMembershipAuthority
from tools.eos.saas.domain.tenant import TenantEntity


TENANT_OWNER_BOOTSTRAP_VERSION = (
    "v1.0.3-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK"
)


class TenantOwnerBootstrapDenialCode(str, Enum):
    """Stable tenant-owner bootstrap denial vocabulary.

    The ownership-evidence denial is the only outcome after successful
    pretenant authentication until a canonical independent verifier exists.
    Other values remain for compatibility with callers that classify historical
    bootstrap failures.
    """

    PRINCIPAL_NOT_FOUND = "PRINCIPAL_NOT_FOUND"
    PRINCIPAL_NOT_ACTIVE = "PRINCIPAL_NOT_ACTIVE"
    TENANT_ALREADY_EXISTS = "TENANT_ALREADY_EXISTS"
    MEMBERSHIP_ALREADY_EXISTS = "MEMBERSHIP_ALREADY_EXISTS"
    AUTHORIZATION_ROLE_ALREADY_EXISTS = "AUTHORIZATION_ROLE_ALREADY_EXISTS"
    BUSINESS_ROLE_ALREADY_EXISTS = "BUSINESS_ROLE_ALREADY_EXISTS"
    PERSISTENCE_FAILURE = "PERSISTENCE_FAILURE"
    INTERNAL_INVARIANT_FRACTURE = "INTERNAL_INVARIANT_FRACTURE"
    OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE = (
        "OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE"
    )


class TenantOwnerBootstrapError(RuntimeError):
    """Bounded bootstrap denial without exposing identity or persistence data."""

    def __init__(self, code: TenantOwnerBootstrapDenialCode) -> None:
        self.code = code
        super().__init__(code.value)


@dataclass(frozen=True, slots=True)
class TenantOwnerBootstrapResult:
    """Historical success shape retained for import compatibility.

    The fail-closed bootstrap command does not produce this value until
    independently verified legal-entity ownership can authorize genesis.
    """

    tenant: TenantEntity
    membership: TenantMembershipAuthority
    authorization_role: RoleAssignmentAuthority
    business_role: TenantBusinessRoleAuthority


def bootstrap_tenant_owner(
    *,
    identity: SovereignIdentity,
    tenant: TenantEntity,
) -> TenantOwnerBootstrapResult:
    """Deny tenant-owner genesis until independent ownership verification exists.

    Deployment-rooted pretenant authority establishes only that the caller may
    request provisioning. It does not establish that the caller represents or
    owns the requested legal entity. This boundary intentionally performs no
    principal lookup, transaction, tenant write, membership write, IAM role
    write, or business-role write. A future complete path must supply and verify
    issuer-rooted legal-entity evidence bound to the exact tenant and principal.

    Args:
        identity: Authenticated platform identity subject to the existing
            deployment-controlled pretenant provisioner allowlist.
        tenant: Requested tenant value; its contents are not treated as proof.

    Raises:
        PretenantBootstrapAuthorityError: If deployment-rooted request authority
            is absent, malformed, or outside its configured allowlist.
        TenantOwnerBootstrapError: Always after successful pretenant verification
            while the independent ownership verifier is unavailable.
    """
    verify_pretenant_bootstrap_authority(identity)
    raise TenantOwnerBootstrapError(
        TenantOwnerBootstrapDenialCode.OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE
    )


__all__ = [
    "TENANT_OWNER_BOOTSTRAP_VERSION",
    "TenantOwnerBootstrapDenialCode",
    "TenantOwnerBootstrapError",
    "TenantOwnerBootstrapResult",
    "bootstrap_tenant_owner",
]

# ARTIFACT: tenant_owner_bootstrap.py
# VERSION: v1.0.3-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK
# AUTHORITY BOUNDARY: deployment provisioning cannot grant tenant ownership
# TENANT POSTURE: no tenant or tenant-local authority is created
# FAIL-CLOSED POSTURE: independent legal-entity ownership verifier unavailable
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
