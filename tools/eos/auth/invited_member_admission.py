"""WILSY OS invited-member admission authority.

TITLE: Canonical invited-member admission
VERSION: v1.0.0-WILSY-F1C2B-A3
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Atomically admit an invitation recipient into one tenant.
EPITOME: Consume invitation, create membership, and create its role together.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/invited_member_admission.py
COLLABORATION / OWNERSHIP: EOS auth orchestration.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 establishes governed three-write admission.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Raw capability is transient and never persisted.
TENANT BOUNDARY: Invitation tenant and authenticated principal are exact.
AUTHORITY BOUNDARY: Admission only; invitation creation remains A2.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: One bound client session owns all reads and writes.
FAIL-CLOSED POSTURE: Invalid, replayed, conflicting, or inactive authority denies.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import hashlib
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from tools.eos.kernel.db import get_client, get_database
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository, TenantMembershipNotFoundError
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository, RoleAssignmentNotFoundError
from tools.eos.auth.invitation_repository import InvitationRepository, InvitationNotFoundError, InvitationRepositoryError
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry

class InvitedMemberAdmissionError(RuntimeError): pass

@dataclass(frozen=True, slots=True)
class InvitedMemberAdmissionComposition:
    client: Any; tenant_collection: Collection; principal_collection: Collection; membership_collection: Collection; role_collection: Collection; invitation_collection: Collection
    def __post_init__(self):
        for c in (self.tenant_collection,self.principal_collection,self.membership_collection,self.role_collection,self.invitation_collection):
            owner=getattr(getattr(c,"database",None),"client",None)
            if owner is not None and owner is not self.client: raise InvitedMemberAdmissionError("MIXED_CLIENT_GRAPH")
    def _admit_in_transaction(self, *, session: ClientSession, identity: SovereignIdentity, invitation_id: str, capability: str) -> tuple[TenantMembershipAuthority, RoleAssignmentAuthority]:
        digest=hashlib.sha3_512(capability.encode()).hexdigest()
        try: invitation=InvitationRepository.get(invitation_id, collection=self.invitation_collection, session=session)
        except InvitationNotFoundError as e: raise InvitedMemberAdmissionError("INVITATION_NOT_FOUND") from e
        if invitation.capability_digest != digest: raise InvitedMemberAdmissionError("INVALID_CAPABILITY")
        now=datetime.now(timezone.utc)
        if invitation.status.value != "ACTIVE" or invitation.expires_at <= now: raise InvitedMemberAdmissionError("INVITATION_NOT_ACTIVE")
        if invitation.tenant_id != identity.tenant_id or invitation.recipient_principal_id != identity.identity_id: raise InvitedMemberAdmissionError("INVITATION_RECIPIENT_MISMATCH")
        if TenantRegistry.get(invitation.tenant_id, collection=self.tenant_collection, session=session) is None: raise InvitedMemberAdmissionError("TENANT_NOT_FOUND")
        principal=PrincipalAuthorityRepository.get(identity.identity_id, collection=self.principal_collection, session=session)
        if principal.status is not PrincipalStatus.ACTIVE: raise InvitedMemberAdmissionError("RECIPIENT_PRINCIPAL_NOT_ACTIVE")
        try: TenantMembershipRepository.resolve(identity.identity_id, invitation.tenant_id, collection=self.membership_collection, session=session); raise InvitedMemberAdmissionError("MEMBERSHIP_ALREADY_EXISTS")
        except TenantMembershipNotFoundError: pass
        try: RoleAssignmentRepository.resolve(identity.identity_id, invitation.tenant_id, invitation.authorization_role_id, collection=self.role_collection, session=session); raise InvitedMemberAdmissionError("ROLE_ASSIGNMENT_ALREADY_EXISTS")
        except RoleAssignmentNotFoundError: pass
        membership=TenantMembershipAuthority(identity.identity_id, invitation.tenant_id, TenantMembershipStatus.ACTIVE, 0)
        role=RoleAssignmentAuthority(identity.identity_id, invitation.tenant_id, invitation.authorization_role_id, RoleAssignmentStatus.ACTIVE, 0)
        TenantMembershipRepository.insert(membership, collection=self.membership_collection, session=session)
        RoleAssignmentRepository.insert(role, collection=self.role_collection, session=session)
        try: InvitationRepository.consume(invitation.invitation_id, digest, invitation.revision, now, collection=self.invitation_collection, session=session)
        except InvitationRepositoryError as e: raise InvitedMemberAdmissionError("INVITATION_CONSUME_FAILED") from e
        return membership, role
    def admit(self, *, identity: SovereignIdentity, invitation_id: str, capability: str) -> tuple[TenantMembershipAuthority, RoleAssignmentAuthority]:
        if not identity.tenant_id or not invitation_id or not capability: raise InvitedMemberAdmissionError("MALFORMED_ADMISSION")
        with self.client.start_session() as session:
            holder={}
            def callback(current): holder["result"]=self._admit_in_transaction(session=current, identity=identity, invitation_id=invitation_id, capability=capability)
            session.with_transaction(callback)
        return holder["result"]

def admit_invited_member(*, identity: SovereignIdentity, invitation_id: str, capability: str) -> tuple[TenantMembershipAuthority, RoleAssignmentAuthority]:
    client=get_client(); db=get_database()
    if client is None or db is None: raise InvitedMemberAdmissionError("PERSISTENCE_FAILURE")
    return InvitedMemberAdmissionComposition(client,db["tenants"],db["principal_authorities"],db["tenant_memberships"],db["role_assignments"],db["invitations"]).admit(identity=identity, invitation_id=invitation_id, capability=capability)

# ARTIFACT: invited_member_admission.py
# VERSION: v1.0.0-WILSY-F1C2B-A3
# AUTHORITY BOUNDARY: three-write invitation admission only
# FAIL-CLOSED POSTURE: invalid and conflicting authority denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
