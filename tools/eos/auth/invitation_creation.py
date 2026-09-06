"""TITLE: WILSY OS Invitation Creation Authority.
VERSION: v1.0.0-WILSY-F1C2B-A2-R2
AUTHORITY: Ordinary tenant-scoped invitation issuance.
EPITOME: Durable, explicitly delegated, digest-only invitation creation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/invitation_creation.py
COLLABORATION / OWNERSHIP: EOS auth orchestration.
SECURITY / PRIVACY POSTURE: Raw capability is transient and returned separately; only SHA3-512 digest persists.
TENANT BOUNDARY: Every read and write is bound to the requested tenant.
AUTHORITY BOUNDARY: Invitation creation only; no admission or membership mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Caller-owned Mongo transaction.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 establishes A2 ordinary invitation creation authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from dataclasses import dataclass
from typing import Any
from datetime import datetime, timezone
import hashlib, secrets
from pymongo.client_session import ClientSession
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.authorization_role_delegation_policy import evaluate_authorization_role_grant
from tools.eos.auth.invitation import InvitationAuthority, InvitationStatus
from tools.eos.auth.invitation_repository import InvitationRepository
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry
from tools.eos.kernel.db import get_client
from pymongo.collection import Collection

@dataclass(frozen=True, slots=True)
class InvitationCreationResult:
    invitation: InvitationAuthority
    capability: str

class InvitationCreationError(RuntimeError):
    """Fail-closed creation denial without secrets or PII."""

@dataclass(frozen=True, slots=True)
class InvitationCreationComposition:
    """Trusted one-client collection graph for invitation creation."""
    client: Any
    tenant_collection: Collection
    principal_collection: Collection
    membership_collection: Collection
    role_collection: Collection
    invitation_collection: Collection

    def __post_init__(self) -> None:
        """Reject collection graphs that are not owned by the trusted client."""
        for collection in (self.tenant_collection, self.principal_collection,
                           self.membership_collection, self.role_collection,
                           self.invitation_collection):
            owner = getattr(collection, "database", None)
            owner_client = getattr(owner, "client", None)
            if owner_client is not None and owner_client is not self.client:
                raise InvitationCreationError("MIXED_CLIENT_GRAPH")

    def _create_in_transaction(self, *, session: ClientSession,
                               identity: SovereignIdentity, tenant_id: str,
                               recipient_principal_id: str,
                               authorization_role_id: str,
                               expires_at: datetime, invitation_id: str,
                               capability_digest: str,
                               created_at: datetime) -> InvitationAuthority:
        """Execute the canonical authority and insert body in one session."""
        principal = PrincipalAuthorityRepository.get(identity.identity_id, collection=self.principal_collection, session=session)
        if principal.status is not PrincipalStatus.ACTIVE:
            raise InvitationCreationError("INVITER_PRINCIPAL_NOT_ACTIVE")
        if TenantRegistry.get(tenant_id, collection=self.tenant_collection, session=session) is None:
            raise InvitationCreationError("TENANT_NOT_FOUND")
        TenantMembershipRepository.resolve(identity.identity_id, tenant_id, collection=self.membership_collection, session=session)
        assignments = RoleAssignmentRepository.list_assignments(identity.identity_id, tenant_id, collection=self.role_collection, session=session)
        if not any(evaluate_authorization_role_grant(a, tenant_id, authorization_role_id).allowed for a in assignments if a.status is RoleAssignmentStatus.ACTIVE):
            raise InvitationCreationError("GRANT_NOT_PERMITTED")
        recipient = PrincipalAuthorityRepository.get(recipient_principal_id, collection=self.principal_collection, session=session)
        if recipient.status is not PrincipalStatus.ACTIVE:
            raise InvitationCreationError("RECIPIENT_PRINCIPAL_NOT_ACTIVE")
        invitation = InvitationAuthority(invitation_id, tenant_id, recipient_principal_id, identity.identity_id, authorization_role_id, capability_digest, InvitationStatus.ACTIVE, expires_at, 0, created_at)
        InvitationRepository.insert(invitation, collection=self.invitation_collection, session=session)
        return invitation

    def create_invitation(self, *, identity: SovereignIdentity, tenant_id: str, recipient_principal_id: str, authorization_role_id: str, expires_at: datetime) -> InvitationCreationResult:
        if identity.tenant_id != tenant_id: raise InvitationCreationError("INVITATION_CREATION_DENIED")
        now = datetime.now(timezone.utc); invitation_id = f"inv-{secrets.token_hex(32)}"; capability = secrets.token_urlsafe(32); digest = hashlib.sha3_512(capability.encode()).hexdigest(); holder: dict[str, InvitationAuthority] = {}
        with self.client.start_session() as session:
            def callback(current: ClientSession) -> None:
                holder["invitation"] = self._create_in_transaction(session=current, identity=identity, tenant_id=tenant_id, recipient_principal_id=recipient_principal_id, authorization_role_id=authorization_role_id, expires_at=expires_at, invitation_id=invitation_id, capability_digest=digest, created_at=now)
            session.with_transaction(callback)
        return InvitationCreationResult(holder["invitation"], capability)

def create_invitation(*, identity: SovereignIdentity, tenant_id: str, recipient_principal_id: str, authorization_role_id: str, expires_at: datetime) -> InvitationCreationResult:
    """Create one delegated invitation in a caller-owned transaction."""
    client = get_client()
    if client is None: raise InvitationCreationError("PERSISTENCE_FAILURE")
    from tools.eos.kernel.db import get_database
    db = get_database()
    if db is None: raise InvitationCreationError("PERSISTENCE_FAILURE")
    composition = InvitationCreationComposition(client, db["tenants"], db["principal_authorities"], db["tenant_memberships"], db["role_assignments"], db["invitations"])
    return composition.create_invitation(identity=identity, tenant_id=tenant_id, recipient_principal_id=recipient_principal_id, authorization_role_id=authorization_role_id, expires_at=expires_at)

__all__ = ["InvitationCreationComposition", "InvitationCreationError", "InvitationCreationResult", "create_invitation"]
# ARTIFACT: invitation_creation.py
# VERSION: v1.0.0-WILSY-F1C2B-A2-R2
# AUTHORITY BOUNDARY: ordinary invitation issuance only
# TENANT POSTURE: explicit tenant-bound reads and persistence
# FAIL-CLOSED POSTURE: missing, inactive, unauthorized, and persistence failures deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
