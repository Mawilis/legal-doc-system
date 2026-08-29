"""Real-Mongo certification for tenant access enforcement."""
import asyncio, os, uuid
from pymongo import MongoClient
import pytest
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_access import get_current_tenant_identity
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.api.exceptions import UnauthorizedAccessException

@pytest.fixture()
def setup():
    uri=os.getenv("TEST_VENDOR_MONGO_URI")
    if not uri: pytest.fail("TEST_VENDOR_MONGO_URI is required")
    client=MongoClient(uri,serverSelectionTimeoutMS=5000); assert client.admin.command("hello").get("setName")=="wilsyVendorCertRS"
    db=client[f"tenant_access_{uuid.uuid4().hex}"]; c=db["tenant_memberships"]; TenantMembershipRepository.ensure_indexes(c)
    class Repo:
        def resolve(self,p,t): return TenantMembershipRepository.resolve(p,t,c)
    yield Repo(), c
    client.drop_database(db.name); client.close()

def ident(): return SovereignIdentity(identity_id="p",tenant_id="claim",username=None,email=None,auth_method="JWT",status=PrincipalStatus.ACTIVE)
def run(repo, tenant): return asyncio.run(get_current_tenant_identity(tenant, ident(), repo))

def test_current_membership_controls_access_and_revocation(setup):
    repo,c=setup
    TenantMembershipRepository.insert(TenantMembershipAuthority("p","t1",TenantMembershipStatus.ACTIVE,0),c)
    TenantMembershipRepository.insert(TenantMembershipAuthority("p","t2",TenantMembershipStatus.REVOKED,0),c)
    assert run(repo,"t1").tenant_id=="t1"
    with pytest.raises(UnauthorizedAccessException): run(repo,"t2")
    with pytest.raises(UnauthorizedAccessException): run(repo,"missing")
    TenantMembershipRepository.compare_and_swap(TenantMembershipAuthority("p","t1",TenantMembershipStatus.SUSPENDED,1),0,c)
    with pytest.raises(UnauthorizedAccessException): run(repo,"t1")
