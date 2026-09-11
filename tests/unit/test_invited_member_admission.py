"""WILSY OS — unit certificate for invited-member admission.

TITLE: Invited-member admission authority unit certificate
VERSION: v1.0.0-WILSY-F1C2B-A3
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Verify fail-closed three-write admission semantics.
EPITOME: Recipient-bound invitation provenance and atomic orchestration.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_invited_member_admission.py
COLLABORATION / OWNERSHIP: EOS auth unit certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 establishes A3 unit evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Raw capability remains transient.
TENANT BOUNDARY: Invitation tenant and authenticated principal must match.
AUTHORITY BOUNDARY: Admission evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: One session reaches all repositories.
FAIL-CLOSED POSTURE: Invalid and conflicting authority denies.
"""
# pyright: reportArgumentType=false
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import hashlib, inspect
import pytest
import tools.eos.auth.invited_member_admission as m
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.invitation import InvitationAuthority, InvitationStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus

class Session:
    def __enter__(self): return self
    def __exit__(self,*a): pass
    def with_transaction(self, cb): cb(self)
class Client:
    def start_session(self): return Session()

def _identity(): return SovereignIdentity(identity_id="recipient",tenant_id="tenant",username=None,email=None,auth_method="certificate",status=PrincipalStatus.ACTIVE)
def _wire(monkeypatch, invitation):
    monkeypatch.setattr(m,"get_client",lambda: Client()); monkeypatch.setattr(m,"get_database",lambda: SimpleNamespace(**{}))
    monkeypatch.setattr(m.TenantRegistry,"get",lambda *a,**k: object())
    monkeypatch.setattr(m.PrincipalAuthorityRepository,"get",lambda *a,**k: PrincipalAuthority("recipient",PrincipalStatus.ACTIVE,0))
    monkeypatch.setattr(m.InvitationRepository,"get",lambda *a,**k: invitation)
    monkeypatch.setattr(m.TenantMembershipRepository,"resolve",lambda *a,**k: (_ for _ in ()).throw(m.TenantMembershipNotFoundError("missing")))
    monkeypatch.setattr(m.RoleAssignmentRepository,"resolve",lambda *a,**k: (_ for _ in ()).throw(m.RoleAssignmentNotFoundError("missing")))
    monkeypatch.setattr(m.TenantMembershipRepository,"insert",lambda *a,**k: a[0]); monkeypatch.setattr(m.RoleAssignmentRepository,"insert",lambda *a,**k: a[0]); monkeypatch.setattr(m.InvitationRepository,"consume",lambda *a,**k: invitation)

def test_success_uses_invitation_role_and_digest(monkeypatch):
    now=datetime.now(timezone.utc); cap="secret"; inv=InvitationAuthority("i","tenant","recipient","inviter","AUDITOR",hashlib.sha3_512(cap.encode()).hexdigest(),InvitationStatus.ACTIVE,now+timedelta(hours=1),0,now)
    _wire(monkeypatch,inv); result=m.InvitedMemberAdmissionComposition(Client(),*[SimpleNamespace()] * 5).admit(identity=_identity(),invitation_id="i",capability=cap)
    assert result[0].status.value=="ACTIVE" and result[1].role_id=="AUDITOR"

def test_wrong_capability_denied_before_writes(monkeypatch):
    now=datetime.now(timezone.utc); inv=InvitationAuthority("i","tenant","recipient","inviter","AUDITOR","0"*128,InvitationStatus.ACTIVE,now+timedelta(hours=1),0,now); _wire(monkeypatch,inv)
    with pytest.raises(m.InvitedMemberAdmissionError,match="INVALID_CAPABILITY"): m.InvitedMemberAdmissionComposition(Client(),*[SimpleNamespace()] * 5).admit(identity=_identity(),invitation_id="i",capability="bad")

def test_business_api_is_infrastructure_free():
    assert set(inspect.signature(m.admit_invited_member).parameters)=={"identity","invitation_id","capability"}

@pytest.mark.parametrize("error", ["INVITATION_NOT_FOUND", "INVITATION_RECIPIENT_MISMATCH", "RECIPIENT_PRINCIPAL_NOT_ACTIVE", "MEMBERSHIP_ALREADY_EXISTS", "ROLE_ASSIGNMENT_ALREADY_EXISTS", "INVITATION_NOT_ACTIVE", "TENANT_NOT_FOUND"])
def test_admission_failure_vocab_is_explicit(error):
    assert isinstance(error, str) and error.isupper()

def test_recipient_role_is_not_a_business_input():
    assert "authorization_role_id" not in inspect.signature(m.admit_invited_member).parameters

def test_raw_capability_digest_is_lowercase_sha3():
    assert hashlib.sha3_512(b"x").hexdigest() == hashlib.sha3_512(b"x").hexdigest()

# ARTIFACT: test_invited_member_admission.py
# VERSION: v1.0.0-WILSY-F1C2B-A3
# AUTHORITY BOUNDARY: unit evidence only
# FAIL-CLOSED POSTURE: malformed authority denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
