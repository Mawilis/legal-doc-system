"""WILSY OS — governed invited-member admission real-Mongo certificate.

TITLE: Six-scenario admission operational certificate
VERSION: v1.0.0-WILSY-F1C2B-A3
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Host-only durable admission certification.
EPITOME: One raw TEST_VENDOR_MONGO_URI client and bounded scenarios.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_invited_member_admission_real_mongo.py
COLLABORATION / OWNERSHIP: EOS auth integration certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 establishes the governed A3 scenario surface.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID fixtures and bounded cleanup only.
TENANT BOUNDARY: Every scenario is isolated by synthetic identifiers.
AUTHORITY BOUNDARY: Evidence only; no new authority is granted by tests.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: Production admission owns the transaction.
FAIL-CLOSED POSTURE: Mongo unavailability is an environment blocker.
"""
import os, uuid, hashlib
from datetime import datetime, timedelta, timezone
import pytest
from pymongo import MongoClient
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.invitation import InvitationAuthority, InvitationStatus
from tools.eos.auth.invitation_repository import InvitationRepository, InvitationNotFoundError
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository, TenantMembershipNotFoundError
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository, RoleAssignmentNotFoundError
from tools.eos.auth.invited_member_admission import InvitedMemberAdmissionComposition, InvitedMemberAdmissionError

URI = os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")

@pytest.fixture
def mongo():
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True)
    try: client.admin.command("ping")
    except Exception: client.close(); pytest.skip("governed Mongo unavailable; host certification required")
    yield client
    client.close()

def _fixture(mongo, conflict=False):
    db=mongo[f"admit_{uuid.uuid4().hex}"]; cols=tuple(db[n] for n in ("tenants","principal_authorities","tenant_memberships","role_assignments","invitations")); tenant=f"t-{uuid.uuid4().hex}"; recipient=f"r-{uuid.uuid4().hex}"; inviter=f"i-{uuid.uuid4().hex}"
    db.tenants.insert_one({"tenant_id":tenant,"name":"cert"}); PrincipalAuthorityRepository.create(PrincipalAuthority(recipient,PrincipalStatus.ACTIVE,0),collection=cols[1]); PrincipalAuthorityRepository.create(PrincipalAuthority(inviter,PrincipalStatus.ACTIVE,0),collection=cols[1])
    if conflict: TenantMembershipRepository.insert(TenantMembershipAuthority(recipient,tenant,TenantMembershipStatus.ACTIVE,0),collection=cols[2])
    cap="cap-"+uuid.uuid4().hex; now=datetime.now(timezone.utc); inv=InvitationAuthority(f"inv-{uuid.uuid4().hex}",tenant,recipient,inviter,"AUDITOR",hashlib.sha3_512(cap.encode()).hexdigest(),InvitationStatus.ACTIVE,now+timedelta(hours=1),0,now); InvitationRepository.insert(inv,collection=cols[4]); comp=InvitedMemberAdmissionComposition(mongo,*cols); return comp,tenant,recipient,inv,cap,cols

def test_rm_admit_1_happy(mongo):
    comp,tenant,recipient,inv,cap,cols=_fixture(mongo); comp.admit(identity=SovereignIdentity(identity_id=recipient,tenant_id=tenant,username=None,email=None,auth_method="certificate",status=PrincipalStatus.ACTIVE),invitation_id=inv.invitation_id,capability=cap); assert cols[2].count_documents({"principal_id":recipient})==1 and cols[3].count_documents({"principal_id":recipient})==1
def test_rm_admit_2_wrong_principal(mongo):
    comp,tenant,recipient,inv,cap,cols=_fixture(mongo)
    with pytest.raises(InvitedMemberAdmissionError): comp.admit(identity=SovereignIdentity(identity_id="wrong",tenant_id=tenant,username=None,email=None,auth_method="certificate",status=PrincipalStatus.ACTIVE),invitation_id=inv.invitation_id,capability=cap)
def test_rm_admit_3_replay(mongo):
    comp,tenant,recipient,inv,cap,cols=_fixture(mongo); ident=SovereignIdentity(identity_id=recipient,tenant_id=tenant,username=None,email=None,auth_method="certificate",status=PrincipalStatus.ACTIVE); comp.admit(identity=ident,invitation_id=inv.invitation_id,capability=cap)
    with pytest.raises(InvitedMemberAdmissionError): comp.admit(identity=ident,invitation_id=inv.invitation_id,capability=cap)
def test_rm_admit_4_invalid_capability(mongo):
    comp,tenant,recipient,inv,cap,cols=_fixture(mongo); ident=SovereignIdentity(identity_id=recipient,tenant_id=tenant,username=None,email=None,auth_method="certificate",status=PrincipalStatus.ACTIVE)
    with pytest.raises(InvitedMemberAdmissionError): comp.admit(identity=ident,invitation_id=inv.invitation_id,capability="bad")
    assert cols[2].count_documents({})==0
def test_rm_admit_5_rollback(mongo):
    comp,tenant,recipient,inv,cap,cols=_fixture(mongo); client=mongo; ident=SovereignIdentity(identity_id=recipient,tenant_id=tenant,username=None,email=None,auth_method="certificate",status=PrincipalStatus.ACTIVE)
    with client.start_session() as s:
        s.start_transaction(); comp._admit_in_transaction(session=s,identity=ident,invitation_id=inv.invitation_id,capability=cap); s.abort_transaction()
    assert cols[2].count_documents({})==0
def test_rm_admit_6_conflict(mongo):
    comp,tenant,recipient,inv,cap,cols=_fixture(mongo,True); ident=SovereignIdentity(identity_id=recipient,tenant_id=tenant,username=None,email=None,auth_method="certificate",status=PrincipalStatus.ACTIVE)
    with pytest.raises(InvitedMemberAdmissionError): comp.admit(identity=ident,invitation_id=inv.invitation_id,capability=cap)

# ARTIFACT: test_invited_member_admission_real_mongo.py
# VERSION: v1.0.0-WILSY-F1C2B-A3
# AUTHORITY BOUNDARY: operational evidence only
# FAIL-CLOSED POSTURE: unavailable Mongo blocks certification
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
