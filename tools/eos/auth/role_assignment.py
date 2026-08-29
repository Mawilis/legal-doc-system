"""Forward-canonical immutable role assignment authority snapshot.

TITLE: WILSY OS Role Assignment Authority
VERSION: v1.0.0-WILSY-ROLE-ASSIGNMENT
AUTHORITY: Current principal/tenant/role assignment status and revision only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/role_assignment.py
CERTIFICATION/UPDATE DATE: 2026-08-29
CHANGELOG: v1.0.0 establishes one immutable assignment per natural authority key.
COMPLIANCE: Framework-free value object; role definitions and permissions remain separate.
SECURITY/PRIVACY POSTURE: Explicit opaque identifiers; no credentials or profile metadata.
TENANT BOUNDARY: Every assignment is scoped to explicit principal_id and tenant_id.
AUTHORITY BOUNDARY: Does not own principal status, membership, role meaning, permissions, or transitions.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial execution authority.

Epitome:
    A single current role binding identified by (principal_id, tenant_id, role_id).

Biblical Anchor:
    "And he shall be like a tree planted by the rivers of water..." — Psalm 1:3

Collaboration & Ownership:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    AI Collaborator: Core Systems Engineering Agent
    File Path: tools/eos/auth/role_assignment.py
"""
from dataclasses import dataclass
from enum import Enum

class RoleAssignmentStatus(str, Enum):
    """Current assignment state; suspension belongs to membership authority."""
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"

@dataclass(frozen=True, slots=True)
class RoleAssignmentAuthority:
    """Immutable tenant-scoped role binding without permission authority."""
    principal_id: str
    tenant_id: str
    role_id: str
    status: RoleAssignmentStatus
    revision: int

    def __post_init__(self) -> None:
        """Reject missing, altered, untyped, or negative assignment values."""
        for name, value in (("principal_id", self.principal_id), ("tenant_id", self.tenant_id), ("role_id", self.role_id)):
            if not isinstance(value, str) or not value or value != value.strip(): raise ValueError(f"{name} must be a non-empty trimmed string")
        if not isinstance(self.status, RoleAssignmentStatus): raise TypeError("status must be a RoleAssignmentStatus")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 0: raise ValueError("revision must be a non-negative integer")

__all__ = ["RoleAssignmentAuthority", "RoleAssignmentStatus"]

# ARTIFACT: role_assignment.py
# VERSION: v1.0.0-WILSY-ROLE-ASSIGNMENT
# AUTHORITY BOUNDARY: current principal/tenant/role binding only
# TENANT POSTURE: explicit three-part tenant-scoped identity
# FAIL-CLOSED POSTURE: malformed identifiers, status, and revision are rejected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
