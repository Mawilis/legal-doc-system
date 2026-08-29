"""Unit certification for tenant membership access enforcement."""
import asyncio
import pytest
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_access import get_current_tenant_identity
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.api.exceptions import UnauthorizedAccessException

class Repo:
    def __init__(self, status=None, error=None): self.status, self.error = status, error
    def resolve(self, principal_id, tenant_id):
        if self.error: raise self.error
        from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError
        if self.status is None: raise TenantMembershipNotFoundError("absent")
        return TenantMembershipAuthority(principal_id, tenant_id, self.status, 0)
def identity(status=PrincipalStatus.ACTIVE): return SovereignIdentity(identity_id="p",tenant_id="claim",username=None,email=None,auth_method="JWT",status=status)
def run(i, tenant, repo): return asyncio.run(get_current_tenant_identity(tenant, i, repo))
def test_active_membership_passes_and_context_is_explicit(): assert run(identity(),"tenant-a",Repo(TenantMembershipStatus.ACTIVE)).tenant_id=="tenant-a"
@pytest.mark.parametrize("status",[PrincipalStatus.SUSPENDED,PrincipalStatus.REVOKED])
def test_principal_status_dominates(status):
    with pytest.raises(UnauthorizedAccessException): run(identity(status),"tenant-a",Repo(TenantMembershipStatus.ACTIVE))
@pytest.mark.parametrize("status",[TenantMembershipStatus.SUSPENDED,TenantMembershipStatus.REVOKED,None])
def test_membership_non_active_or_absent_denied(status):
    with pytest.raises(UnauthorizedAccessException): run(identity(),"tenant-a",Repo(status))
def test_missing_or_malformed_tenant_denied():
    for tenant in (None,""," "," tenant-a","tenant-a "):
        with pytest.raises(UnauthorizedAccessException): run(identity(),tenant,Repo(TenantMembershipStatus.ACTIVE))
def test_database_failure_fails_closed():
    from tools.eos.auth.tenant_membership_repository import TenantMembershipRepositoryError
    with pytest.raises(UnauthorizedAccessException): run(identity(),"tenant-a",Repo(error=TenantMembershipRepositoryError("db")))
def test_multi_tenant_and_roles_cannot_override_membership():
    repo=Repo(TenantMembershipStatus.ACTIVE); assert run(identity(),"t1",repo).tenant_id=="t1"
    with pytest.raises(UnauthorizedAccessException): run(identity(),"t2",Repo(TenantMembershipStatus.REVOKED))
