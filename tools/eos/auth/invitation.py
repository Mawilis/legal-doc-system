"""TITLE: WILSY OS Invitation Authority.
VERSION: v1.0.0-WILSY-F1C2B-A1
AUTHORITY: Immutable invitation provenance and lifecycle value object.
PURPOSE: Define typed invitation persistence truth before admission.
EPITOME: Digest-only, tenant-bound, recipient-bound authority evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/invitation.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering.
SECURITY / PRIVACY POSTURE: Raw bearer capabilities are never accepted or stored.
TENANT BOUNDARY: Explicit tenant identifier on every authority.
AUTHORITY BOUNDARY: Invitation evidence only; no membership or role mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Repository callers own sessions and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 establishes F1C2B-A1 invitation authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import re
from .roles import ROLE_PERMISSIONS_MAP

VERSION = "v1.0.0-WILSY-F1C2B-A1"
def canonicalize_invitation_datetime(value: datetime) -> datetime:
    """Return an aware UTC instant truncated to BSON millisecond precision."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must be UTC-aware")
    utc = value.astimezone(timezone.utc)
    return utc.replace(microsecond=(utc.microsecond // 1000) * 1000)

class InvitationStatus(StrEnum):
    ACTIVE = "ACTIVE"; CONSUMED = "CONSUMED"; REVOKED = "REVOKED"
_DIGEST = re.compile(r"^[0-9a-f]{128}$")

@dataclass(frozen=True, slots=True)
class InvitationAuthority:
    invitation_id: str; tenant_id: str; recipient_principal_id: str
    inviter_principal_id: str; authorization_role_id: str; capability_digest: str
    status: InvitationStatus; expires_at: datetime; revision: int; created_at: datetime; consumed_at: datetime | None = None
    def __post_init__(self) -> None:
        for name, value in (("invitation_id", self.invitation_id), ("tenant_id", self.tenant_id), ("recipient_principal_id", self.recipient_principal_id), ("inviter_principal_id", self.inviter_principal_id), ("authorization_role_id", self.authorization_role_id)):
            if not isinstance(value, str) or not value or value != value.strip(): raise ValueError(f"{name} must be non-empty and trimmed")
        if self.authorization_role_id not in ROLE_PERMISSIONS_MAP: raise ValueError("authorization_role_id must be canonical")
        if not isinstance(self.capability_digest, str) or not _DIGEST.fullmatch(self.capability_digest): raise ValueError("capability_digest must be lowercase SHA3-512 hex")
        if not isinstance(self.status, InvitationStatus): raise TypeError("status must be InvitationStatus")
        if not isinstance(self.revision, int) or isinstance(self.revision, bool) or self.revision < 0: raise ValueError("revision must be non-negative integer")
        object.__setattr__(self, "created_at", canonicalize_invitation_datetime(self.created_at))
        object.__setattr__(self, "expires_at", canonicalize_invitation_datetime(self.expires_at))
        if self.consumed_at is not None: object.__setattr__(self, "consumed_at", canonicalize_invitation_datetime(self.consumed_at))
        if self.expires_at <= self.created_at: raise ValueError("expires_at must be after created_at")
        if self.status is InvitationStatus.ACTIVE and (self.revision != 0 or self.consumed_at is not None): raise ValueError("ACTIVE invariant violated")
        if self.status is InvitationStatus.CONSUMED and (self.revision < 1 or self.consumed_at is None): raise ValueError("CONSUMED invariant violated")
        if self.status is InvitationStatus.REVOKED and self.consumed_at is not None: raise ValueError("REVOKED invariant violated")

__all__ = ["VERSION", "InvitationStatus", "InvitationAuthority", "canonicalize_invitation_datetime"]
# ARTIFACT: invitation.py
# VERSION: v1.0.0-WILSY-F1C2B-A1
# AUTHORITY BOUNDARY: invitation provenance and lifecycle value only
# TENANT POSTURE: explicit tenant and recipient binding
# FAIL-CLOSED POSTURE: malformed and contradictory authority rejected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
