"""Real canonical authorization composer, no mocked positive decision."""
from types import SimpleNamespace
import pytest

from tools.eos.auth.tenant_authorization import (
    authorize_tenant_operation, TenantAuthorizationReason,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepositoryError
from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError, RoleAssignmentRepositoryError,
)

PERM="legal_operations:practitioner_matter_binding:provision"
OP="legal_practitioner_matter_binding_provision"
TENANT="tenant-exact"
ACTOR="partner-exact"

def inactive(enum):
    """Select a real non-ACTIVE enum member; never invent one."""
    options=tuple(item for item in enum if item is not enum.ACTIVE)
    assert options, f"NO_NONACTIVE_CANONICAL_STATUS: {enum.__name__}"
    return options[0]

class Session:
    in_transaction=True

class PrincipalReader:
    def __init__(self,status=PrincipalStatus.ACTIVE,unavailable=False):
        self.status=status
        self.unavailable=unavailable
        self.calls=[]
    def resolve(self,principal_id,*,session=None):
        self.calls.append((principal_id,session))
        if self.unavailable or principal_id!=ACTOR:
            raise PrincipalAuthorityRepositoryError("UNAVAILABLE")
        return SimpleNamespace(status=self.status)

class MembershipReader:
    def __init__(self,status=TenantMembershipStatus.ACTIVE):
        self.status=status
        self.calls=[]
    def resolve(self,principal_id,tenant_id,*,session=None):
        self.calls.append((principal_id,tenant_id,session))
        if (principal_id,tenant_id)!=(ACTOR,TENANT):
            raise TenantMembershipNotFoundError("FOREIGN")
        return SimpleNamespace(status=self.status)

class BusinessRoles:
    def __init__(self,roles=("tenant_legal_partner",),unavailable=False):
        self.roles=roles
        self.unavailable=unavailable
        self.calls=[]
    def resolve(self,principal_id,tenant_id,role_id,*,session=None):
        self.calls.append((principal_id,tenant_id,role_id,session))
        if self.unavailable:
            raise RoleAssignmentRepositoryError("UNAVAILABLE")
        if (principal_id,tenant_id)!=(ACTOR,TENANT) or role_id not in self.roles:
            raise RoleAssignmentNotFoundError("ABSENT")
        return SimpleNamespace(status=TenantBusinessRoleStatus.ACTIVE)

class AuthorizationRoles:
    def __init__(self,status=RoleAssignmentStatus.ACTIVE,unavailable=False):
        self.status=status
        self.unavailable=unavailable
        self.calls=[]
    def resolve(self,principal_id,tenant_id,role_id,*,session=None):
        self.calls.append((principal_id,tenant_id,role_id,session))
        if self.unavailable:
            raise RoleAssignmentRepositoryError("UNAVAILABLE")
        if (principal_id,tenant_id,role_id)!=(ACTOR,TENANT,"LEGAL_PARTNER"):
            raise RoleAssignmentNotFoundError("ABSENT")
        return SimpleNamespace(status=self.status)

def exercise(*,tenant=TENANT,principal=None,membership=None,business=None,
             authorization=None,permission=PERM,operation=OP):
    session=Session()
    pr=principal if principal is not None else PrincipalReader()
    mem=membership if membership is not None else MembershipReader()
    br=business if business is not None else BusinessRoles()
    auth=authorization if authorization is not None else AuthorizationRoles()
    decision=authorize_tenant_operation(
        principal_id=ACTOR,tenant_id=tenant,permission_id=permission,
        operation=operation,principal_repository=pr,
        membership_repository=mem,business_role_repository=br,
        role_assignment_repository=auth,session=session,
    )
    return decision,(pr,mem,br,auth),session

def test_real_positive_partner_current_truth_and_session():
    decision,readers,session=exercise()
    assert decision.authorized is True
    assert decision.reason is TenantAuthorizationReason.AUTHORIZED
    assert decision.business_role=="tenant_legal_partner"
    assert decision.authorization_role=="LEGAL_PARTNER"
    pr,mem,br,auth=readers
    assert pr.calls==[(ACTOR,session)]
    assert mem.calls==[(ACTOR,TENANT,session)]
    assert auth.calls==[(ACTOR,TENANT,"LEGAL_PARTNER",session)]
    assert br.calls and all(c[3] is session for c in br.calls)

@pytest.mark.parametrize("unavailable",[False,True])
def test_principal_inactive_or_unavailable_blocks_downstream(unavailable):
    pr=PrincipalReader(
        status=inactive(PrincipalStatus),unavailable=unavailable
    )
    mem=MembershipReader()
    decision,_,_=exercise(principal=pr,membership=mem)
    assert decision.authorized is False
    assert mem.calls==[]

def test_membership_inactive_blocks_business_role():
    br=BusinessRoles()
    decision,_,_=exercise(
        membership=MembershipReader(inactive(TenantMembershipStatus)),
        business=br,
    )
    assert decision.authorized is False and br.calls==[]

def test_foreign_tenant_denied():
    decision,_,_=exercise(tenant="foreign")
    assert decision.authorized is False
    assert decision.reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND

@pytest.mark.parametrize("roles",[
    (),("tenant_legal_attorney",),
    ("tenant_legal_partner","tenant_legal_attorney"),
])
def test_absent_wrong_or_ambiguous_business_roles(roles):
    auth=AuthorizationRoles()
    decision,_,_=exercise(business=BusinessRoles(roles),authorization=auth)
    assert decision.authorized is False and auth.calls==[]

def test_business_role_outage_denied():
    decision,_,_=exercise(business=BusinessRoles(unavailable=True))
    assert decision.authorized is False

@pytest.mark.parametrize("unavailable",[False,True])
def test_inactive_or_unavailable_grant_denied(unavailable):
    auth=AuthorizationRoles(
        status=inactive(RoleAssignmentStatus),unavailable=unavailable
    )
    decision,_,_=exercise(authorization=auth)
    assert decision.authorized is False

@pytest.mark.parametrize("permission,operation",[
    ("legal_operations:practitioner_matter_access_policy:issue",OP),
    (PERM,"legal_practitioner_matter_access_policy_issue"),
    (PERM,OP+"_override"),
])
def test_mismatched_or_unrecognized_permission_pair_denied(permission,operation):
    decision,_,_=exercise(permission=permission,operation=operation)
    assert decision.authorized is False

def test_business_eligibility_without_active_permission_grant_denied():
    decision,_,_=exercise(
        authorization=AuthorizationRoles(inactive(RoleAssignmentStatus))
    )
    assert decision.business_role=="tenant_legal_partner"
    assert decision.authorized is False

# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P6-R7B-P4-R3B-P1C-R3
# END OF WILSY OS SOVEREIGN ARTIFACT
