"""WILSY OS governed A2 real-Mongo certificate.

TITLE: Five-scenario operational invitation authority certificate
VERSION: v1.0.1-WILSY-F1C2B-A2C6
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Exercise canonical invitation creation against durable Mongo.
EPITOME: One raw client, explicit collections, real transaction boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_invitation_creation_real_mongo.py
COLLABORATION / OWNERSHIP: EOS auth integration certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.1 replaces scaffold scenarios with canonical composition calls.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID fixtures; raw capabilities never persist.
TENANT BOUNDARY: Every fixture is scenario-unique and tenant-scoped.
AUTHORITY BOUNDARY: Evidence only; A0P remains the grant evaluator.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Caller-owned Mongo sessions are preserved.
FAIL-CLOSED POSTURE: Missing Mongo is an environment blocker, never a pass.
"""
from datetime import datetime, timedelta, timezone
import hashlib, os, uuid
import pytest
from pymongo import MongoClient
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.invitation_creation import InvitationCreationComposition
from tools.eos.auth.invitation_repository import InvitationRepository, InvitationNotFoundError
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository

URI = os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")

@pytest.fixture
def graph():
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True)
    try: client.admin.command("ping")
    except Exception: client.close(); pytest.skip("governed real Mongo unavailable")
    db = client[f"invitation_creation_cert_{uuid.uuid4().hex}"]
    cols = tuple(db[n] for n in ("tenants", "principal_authorities", "tenant_memberships", "role_assignments", "invitations"))
    yield client, cols
    client.close()

def _setup(graph, second_role=None):
    client, cols = graph; tenants, principals, memberships, roles, invitations = cols
    tenant_id=f"cert-tenant-{uuid.uuid4().hex}"; inviter=f"cert-inviter-{uuid.uuid4().hex}"; recipient=f"cert-recipient-{uuid.uuid4().hex}"
    tenants.insert_one({"tenant_id": tenant_id, "name": "A2 Certificate"})
    PrincipalAuthorityRepository.create(PrincipalAuthority(inviter, PrincipalStatus.ACTIVE, 0), collection=principals)
    PrincipalAuthorityRepository.create(PrincipalAuthority(recipient, PrincipalStatus.ACTIVE, 0), collection=principals)
    TenantMembershipRepository.insert(TenantMembershipAuthority(inviter, tenant_id, TenantMembershipStatus.ACTIVE, 0), collection=memberships)
    for role in ("ENTERPRISE_ADMIN", second_role) if second_role else ("ENTERPRISE_ADMIN",): RoleAssignmentRepository.insert(RoleAssignmentAuthority(inviter, tenant_id, role, RoleAssignmentStatus.ACTIVE, 0), collection=roles)
    return InvitationCreationComposition(client, *cols), SovereignIdentity(identity_id=inviter, tenant_id=tenant_id, username=None, email=None, auth_method="certificate", status=PrincipalStatus.ACTIVE), tenant_id, inviter, recipient, invitations

def _call(graph, target):
    comp, identity, tenant_id, _, recipient, invitations = _setup(graph)
    result=comp.create_invitation(identity=identity, tenant_id=tenant_id, recipient_principal_id=recipient, authorization_role_id=target, expires_at=datetime.now(timezone.utc)+timedelta(hours=1))
    durable=InvitationRepository.get(result.invitation.invitation_id, collection=invitations)
    assert durable.authorization_role_id==target and durable.capability_digest==hashlib.sha3_512(result.capability.encode()).hexdigest()
    raw=invitations.find_one({"invitation_id":durable.invitation_id}); assert "recipient_email" not in raw and result.capability not in str(raw)
    return durable

def test_rm_a2_1_enterprise_admin_to_auditor(graph): assert _call(graph,"AUDITOR").status.value=="ACTIVE"
def test_rm_a2_2_enterprise_admin_to_service_worker(graph): assert _call(graph,"SERVICE_WORKER").status.value=="ACTIVE"
def test_rm_a2_3_escalation_denied(graph):
    comp, identity, tenant_id, _, recipient, invitations=_setup(graph)
    with pytest.raises(Exception): comp.create_invitation(identity=identity, tenant_id=tenant_id, recipient_principal_id=recipient, authorization_role_id="SOVEREIGN_ARCHITECT", expires_at=datetime.now(timezone.utc)+timedelta(hours=1))
    assert invitations.count_documents({"tenant_id":tenant_id})==0
def test_rm_a2_4_multi_role_any_active_allow(graph):
    comp, identity, tenant_id, inviter, recipient, invitations=_setup(graph,"AUDITOR")
    assert len(RoleAssignmentRepository.list_assignments(inviter,tenant_id,collection=invitations.database["role_assignments"]))==2
    result=comp.create_invitation(identity=identity,tenant_id=tenant_id,recipient_principal_id=recipient,authorization_role_id="AUDITOR",expires_at=datetime.now(timezone.utc)+timedelta(hours=1))
    assert InvitationRepository.get(result.invitation.invitation_id,collection=invitations).authorization_role_id=="AUDITOR"
def test_rm_a2_5_transaction_rollback(graph):
    client, cols=graph; comp, identity, tenant_id, _, recipient, invitations=_setup(graph); now=datetime.now(timezone.utc); iid=f"abort-{uuid.uuid4().hex}"; digest=hashlib.sha3_512(b"abort").hexdigest()
    with client.start_session() as session:
        session.start_transaction(); comp._create_in_transaction(session=session,identity=identity,tenant_id=tenant_id,recipient_principal_id=recipient,authorization_role_id="AUDITOR",expires_at=now+timedelta(hours=1),invitation_id=iid,capability_digest=digest,created_at=now); session.abort_transaction()
    with pytest.raises(InvitationNotFoundError): InvitationRepository.get(iid,collection=invitations)

# ARTIFACT: test_invitation_creation_real_mongo.py
# VERSION: v1.0.1-WILSY-F1C2B-A2C6
# AUTHORITY BOUNDARY: operational evidence only; no authority grant.
# FAIL-CLOSED POSTURE: unavailable Mongo is an environment blocker.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
