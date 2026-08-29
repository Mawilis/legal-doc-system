"""Forward-canonical immutable tenant membership authority snapshot.

TITLE: WILSY OS Tenant Membership Authority
VERSION: v1.0.0-WILSY-TENANT-MEMBERSHIP
AUTHORITY: Principal/tenant membership status and revision snapshot only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_membership.py
CERTIFICATION/UPDATE DATE: 2026-08-29
CHANGELOG: v1.0.0 establishes the minimal immutable membership contract.
COMPLIANCE: Framework-free typed value object with no persistence or mutation policy.
SECURITY/PRIVACY POSTURE: Explicit identifiers; no defaults, credentials, or profile data.
TENANT BOUNDARY: Every snapshot is scoped to exactly one explicit tenant_id.
AUTHORITY BOUNDARY: Owns only principal_id, tenant_id, membership status, and revision.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial execution authority.

Epitome:
    The natural membership identity is the ordered pair (principal_id, tenant_id).

Biblical Anchor:
    "And he shall be like a tree planted by the rivers of water..." — Psalm 1:3

Collaboration & Ownership:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    AI Collaborator: Core Systems Engineering Agent
    File Path: tools/eos/auth/tenant_membership.py
"""
from dataclasses import dataclass
from enum import Enum

class TenantMembershipStatus(str, Enum):
    """Current membership lifecycle state, independent of principal status."""
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"

@dataclass(frozen=True, slots=True)
class TenantMembershipAuthority:
    """Immutable tenant-specific membership snapshot without role authority."""
    principal_id: str
    tenant_id: str
    status: TenantMembershipStatus
    revision: int

    def __post_init__(self) -> None:
        """Reject empty, altered, untyped, or negative authority values."""
        for name, value in (("principal_id", self.principal_id), ("tenant_id", self.tenant_id)):
            if not isinstance(value, str) or not value or value != value.strip():
                raise ValueError(f"{name} must be a non-empty trimmed string")
        if not isinstance(self.status, TenantMembershipStatus):
            raise TypeError("status must be a TenantMembershipStatus")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 0:
            raise ValueError("revision must be a non-negative integer")

__all__ = ["TenantMembershipAuthority", "TenantMembershipStatus"]

# ARTIFACT: tenant_membership.py
# VERSION: v1.0.0-WILSY-TENANT-MEMBERSHIP
# AUTHORITY BOUNDARY: principal/tenant membership snapshot only
# TENANT POSTURE: explicit tenant-scoped identity pair; no cross-tenant authority
# FAIL-CLOSED POSTURE: malformed identifiers, status, and revision are rejected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
