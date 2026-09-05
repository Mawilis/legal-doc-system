"""TITLE: WILSY OS Tenant Business-Role Delegation Certificate.
VERSION: v1.0.0-WILSY-TENANT-BUSINESS-ROLE-DELEGATION-CERT
AUTHORITY: Direct certification of pure delegation policy only.
EPITOME: Verifies deterministic tenant-role delegation and ownership safeguards.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_business_role_delegation_policy.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-05.
CHANGELOG: v1.0.0 establishes the bounded F1C0B certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No secrets, persistence, network, or environment mutation.
TENANT BOUNDARY: Tests exact same-tenant and cross-tenant behavior.
AUTHORITY BOUNDARY: Certificate does not grant or execute authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive financial execution authority.
TRANSACTION BOUNDARY: No transaction or session ownership.
FAIL-CLOSED POSTURE: Assertions require explicit denial evidence.
"""
import pytest
from tools.eos.auth.tenant_business_role_delegation_policy import *
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus

def ev(op, actor='tenant_owner', target_role='tenant_admin', current=None, status=None, ctx=OwnershipTransitionContext.NORMAL, owners=1, same=False):
    return evaluate_business_role_mutation('p1','t1',actor,op,'p1' if same else 'p2','t1',target_role,current,status,TenantMembershipStatus.ACTIVE,owners,ctx)

@pytest.mark.parametrize('op', ['business_role_assign','business_role_change','business_role_revoke'])
def test_normal_non_owner(op):
    r=ev(op,current=None if op=='business_role_assign' else 'tenant_manager',status=None if op=='business_role_assign' else TenantBusinessRoleStatus.ACTIVE)
    assert r.allowed

def test_transfer_owner_assign():
    assert ev('business_role_assign',target_role='tenant_owner',ctx=OwnershipTransitionContext.OWNERSHIP_TRANSFER).allowed

def test_admin_cannot_owner():
    r=ev('business_role_assign',actor='tenant_admin',target_role='tenant_owner',ctx=OwnershipTransitionContext.OWNERSHIP_TRANSFER)
    assert r.denial_code is BusinessRoleMutationDenialCode.TARGET_ROLE_EXCEEDS_CEILING

def test_last_owner_protected():
    r=ev('business_role_revoke',target_role='tenant_owner',current='tenant_owner',status=TenantBusinessRoleStatus.ACTIVE,ctx=OwnershipTransitionContext.OWNERSHIP_TRANSFER)
    assert r.denial_code is BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED

def test_malformed_state_denied():
    r=ev('business_role_assign',status=TenantBusinessRoleStatus.ACTIVE)
    assert r.denial_code is BusinessRoleMutationDenialCode.MALFORMED_INPUT

def test_unknown_operation_denied():
    assert ev('business_role_read').denial_code is BusinessRoleMutationDenialCode.UNKNOWN_OPERATION

@pytest.mark.parametrize('field,value', [('actor_principal_id',' '),('actor_tenant_id',''),('target_principal_id',' '),('target_tenant_id','')])
def test_blank_identity_denied(field,value):
    kwargs={field:value}; base=dict(actor_principal_id='p1',actor_tenant_id='t1',actor_business_role='tenant_owner',operation='business_role_assign',target_principal_id='p2',target_tenant_id='t1',requested_business_role='tenant_admin',current_target_role=None,current_target_role_status=None,target_membership_status=TenantMembershipStatus.ACTIVE,active_owner_count=1,ownership_transition=OwnershipTransitionContext.NORMAL); base.update(kwargs)
    assert evaluate_business_role_mutation(**base).denial_code is BusinessRoleMutationDenialCode.MALFORMED_INPUT

@pytest.mark.parametrize('role', ['tenant_manager','tenant_auditor'])
def test_unauthorized_actor_denied(role):
    assert ev('business_role_assign',actor=role).denial_code is BusinessRoleMutationDenialCode.ACTOR_NOT_ELIGIBLE

@pytest.mark.parametrize('status', [TenantMembershipStatus.SUSPENDED,TenantMembershipStatus.REVOKED])
def test_inactive_membership_denied(status):
    base=ev('business_role_assign'); assert evaluate_business_role_mutation('p1','t1','tenant_owner','business_role_assign','p2','t1','tenant_admin',None,None,status,1,OwnershipTransitionContext.NORMAL).denial_code is BusinessRoleMutationDenialCode.TARGET_MEMBERSHIP_INACTIVE

@pytest.mark.parametrize('op', ['business_role_assign','business_role_change','business_role_revoke'])
def test_cross_tenant_denied(op):
    assert evaluate_business_role_mutation('p1','t1','tenant_owner',op,'p2','t2','tenant_admin',None,None,TenantMembershipStatus.ACTIVE,1,OwnershipTransitionContext.NORMAL).denial_code is BusinessRoleMutationDenialCode.CROSS_TENANT

@pytest.mark.parametrize('role,status', [('tenant_admin',None),(None,TenantBusinessRoleStatus.ACTIVE)])
def test_role_state_pairing_denied(role,status):
    assert ev('business_role_assign',current=role,status=status).denial_code is BusinessRoleMutationDenialCode.MALFORMED_INPUT

def test_reactivation_and_state_guards():
    assert ev('business_role_assign',current='tenant_admin',status=TenantBusinessRoleStatus.REVOKED).allowed
    assert ev('business_role_change',current='tenant_admin',status=TenantBusinessRoleStatus.REVOKED).denial_code is BusinessRoleMutationDenialCode.TARGET_ROLE_STATE_INVALID
    assert ev('business_role_revoke',current=None,status=None).denial_code is BusinessRoleMutationDenialCode.TARGET_ROLE_STATE_INVALID

def test_transfer_change_and_revoke():
    ctx=OwnershipTransitionContext.OWNERSHIP_TRANSFER
    assert ev('business_role_change',target_role='tenant_owner',current='tenant_admin',status=TenantBusinessRoleStatus.ACTIVE,ctx=ctx).allowed
    assert ev('business_role_change',target_role='tenant_admin',current='tenant_owner',status=TenantBusinessRoleStatus.ACTIVE,ctx=ctx,owners=2).allowed
    assert ev('business_role_revoke',target_role='tenant_owner',current='tenant_owner',status=TenantBusinessRoleStatus.ACTIVE,ctx=ctx,owners=2).allowed

def test_boolean_owner_count_rejected():
    r = evaluate_business_role_mutation('p1','t1','tenant_owner','business_role_assign','p2','t1','tenant_admin',None,None,TenantMembershipStatus.ACTIVE,True,OwnershipTransitionContext.NORMAL)
    assert r.denial_code is BusinessRoleMutationDenialCode.MALFORMED_INPUT

@pytest.mark.parametrize('target', ['tenant_manager','tenant_auditor'])
def test_admin_self_change_non_owner_allowed(target):
    assert ev('business_role_change', actor='tenant_admin', target_role=target,
              current='tenant_admin', status=TenantBusinessRoleStatus.ACTIVE,
              same=True).allowed

def test_admin_self_change_same_role_denied():
    assert ev('business_role_change', actor='tenant_admin', target_role='tenant_admin',
              current='tenant_admin', status=TenantBusinessRoleStatus.ACTIVE,
              same=True).denial_code is BusinessRoleMutationDenialCode.SAME_ROLE_MUTATION

def test_admin_self_promotion_denied():
    assert ev('business_role_change', actor='tenant_admin', target_role='tenant_owner',
              current='tenant_admin', status=TenantBusinessRoleStatus.ACTIVE,
              same=True, ctx=OwnershipTransitionContext.OWNERSHIP_TRANSFER,
              owners=2).denial_code is BusinessRoleMutationDenialCode.SELF_PROMOTION_FORBIDDEN

def test_admin_self_revoke_denied():
    assert ev('business_role_revoke', actor='tenant_admin', target_role='tenant_admin',
              current='tenant_admin', status=TenantBusinessRoleStatus.ACTIVE,
              same=True).denial_code is BusinessRoleMutationDenialCode.SELF_REVOCATION_FORBIDDEN

@pytest.mark.parametrize('target', ['tenant_admin','tenant_manager','tenant_auditor'])
def test_owner_self_change_normal_requires_transition(target):
    assert ev('business_role_change', target_role=target, current='tenant_owner',
              status=TenantBusinessRoleStatus.ACTIVE, same=True).denial_code is BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED

@pytest.mark.parametrize('target', ['tenant_admin','tenant_manager','tenant_auditor'])
def test_owner_self_change_transfer_allowed(target):
    assert ev('business_role_change', target_role=target, current='tenant_owner',
              status=TenantBusinessRoleStatus.ACTIVE, same=True,
              ctx=OwnershipTransitionContext.OWNERSHIP_TRANSFER, owners=2).allowed

@pytest.mark.parametrize('owners', [0, 1])
def test_owner_self_change_transfer_last_owner_protected(owners):
    assert ev('business_role_change', target_role='tenant_admin', current='tenant_owner',
              status=TenantBusinessRoleStatus.ACTIVE, same=True,
              ctx=OwnershipTransitionContext.OWNERSHIP_TRANSFER, owners=owners).denial_code is BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED

def test_owner_self_revoke_normal_requires_transition():
    assert ev('business_role_revoke', target_role='tenant_owner', current='tenant_owner',
              status=TenantBusinessRoleStatus.ACTIVE, same=True, owners=2).denial_code is BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED

@pytest.mark.parametrize('owners,expected', [(2, None), (1, BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED)])
def test_owner_self_revoke_transfer_owner_count(owners, expected):
    result = ev('business_role_revoke', target_role='tenant_owner', current='tenant_owner',
                status=TenantBusinessRoleStatus.ACTIVE, same=True,
                ctx=OwnershipTransitionContext.OWNERSHIP_TRANSFER, owners=owners)
    assert result.allowed is (expected is None)
    assert result.denial_code is expected

@pytest.mark.parametrize('count', [-1, False, True])
def test_invalid_owner_counts_fail_closed(count):
    assert ev('business_role_revoke', target_role='tenant_owner', current='tenant_owner',
              status=TenantBusinessRoleStatus.ACTIVE, same=True,
              ctx=OwnershipTransitionContext.OWNERSHIP_TRANSFER, owners=count).denial_code is BusinessRoleMutationDenialCode.MALFORMED_INPUT

def test_decision_constructor_invariants():
    def make(allowed, denial):
        return BusinessRoleMutationDecision(allowed, 'business_role_assign', denial, 'p1', 'p2', 't1', 'tenant_admin', OwnershipTransitionContext.NORMAL)
    assert make(True, None).allowed
    assert make(False, BusinessRoleMutationDenialCode.MALFORMED_INPUT).denial_code is BusinessRoleMutationDenialCode.MALFORMED_INPUT
    with pytest.raises(ValueError):
        make(True, BusinessRoleMutationDenialCode.MALFORMED_INPUT)
    with pytest.raises(ValueError):
        make(False, None)

def _a7a(actor, op, requested, current=None, owners=2):
    return evaluate_business_role_mutation('actor', 'tenant', actor, op, 'target', 'tenant', requested,
        current, TenantBusinessRoleStatus.ACTIVE if current else None,
        TenantMembershipStatus.ACTIVE, owners, OwnershipTransitionContext.NORMAL)

@pytest.mark.parametrize('actor,requested,expected', [
    pytest.param('tenant_owner','tenant_owner',BusinessRoleMutationDenialCode.TARGET_ROLE_EXCEEDS_CEILING,id='NA-01'),
    pytest.param('tenant_owner','tenant_admin',None,id='NA-02'), pytest.param('tenant_owner','tenant_manager',None,id='NA-03'),
    pytest.param('tenant_owner','tenant_auditor',None,id='NA-04'), pytest.param('tenant_admin','tenant_owner',BusinessRoleMutationDenialCode.TARGET_ROLE_EXCEEDS_CEILING,id='NA-05'),
    pytest.param('tenant_admin','tenant_admin',None,id='NA-06'), pytest.param('tenant_admin','tenant_manager',None,id='NA-07'),
    pytest.param('tenant_admin','tenant_auditor',None,id='NA-08'), pytest.param('tenant_manager','tenant_manager',BusinessRoleMutationDenialCode.ACTOR_NOT_ELIGIBLE,id='NA-09'),
    pytest.param('tenant_auditor','tenant_auditor',BusinessRoleMutationDenialCode.ACTOR_NOT_ELIGIBLE,id='NA-10')])
def test_a7a_normal_assign_matrix(actor, requested, expected):
    result = _a7a(actor, 'business_role_assign', requested)
    assert result.allowed is (expected is None); assert result.denial_code is expected

@pytest.mark.parametrize('actor,current,requested,expected', [
    pytest.param('tenant_owner','tenant_admin','tenant_manager',None,id='NC-01'), pytest.param('tenant_owner','tenant_manager','tenant_auditor',None,id='NC-02'),
    pytest.param('tenant_owner','tenant_auditor','tenant_admin',None,id='NC-03'), pytest.param('tenant_admin','tenant_manager','tenant_auditor',None,id='NC-04'),
    pytest.param('tenant_admin','tenant_auditor','tenant_manager',None,id='NC-05'), pytest.param('tenant_owner','tenant_admin','tenant_owner',BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED,id='NC-06'),
    pytest.param('tenant_owner','tenant_owner','tenant_admin',BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED,id='NC-07'), pytest.param('tenant_admin','tenant_owner','tenant_manager',BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED,id='NC-08'),
    pytest.param('tenant_owner','tenant_manager','tenant_manager',BusinessRoleMutationDenialCode.SAME_ROLE_MUTATION,id='NC-09'), pytest.param('tenant_manager','tenant_admin','tenant_manager',BusinessRoleMutationDenialCode.ACTOR_NOT_ELIGIBLE,id='NC-10'),
    pytest.param('tenant_auditor','tenant_admin','tenant_manager',BusinessRoleMutationDenialCode.ACTOR_NOT_ELIGIBLE,id='NC-11')])
def test_a7a_normal_change_matrix(actor, current, requested, expected):
    result = _a7a(actor, 'business_role_change', requested, current)
    assert result.allowed is (expected is None); assert result.denial_code is expected

@pytest.mark.parametrize('actor,current,expected', [
    pytest.param('tenant_owner','tenant_admin',None,id='NR-01'), pytest.param('tenant_owner','tenant_manager',None,id='NR-02'),
    pytest.param('tenant_owner','tenant_auditor',None,id='NR-03'), pytest.param('tenant_admin','tenant_admin',None,id='NR-04'),
    pytest.param('tenant_admin','tenant_manager',None,id='NR-05'), pytest.param('tenant_admin','tenant_auditor',None,id='NR-06'),
    pytest.param('tenant_owner','tenant_owner',BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED,id='NR-07'), pytest.param('tenant_admin','tenant_owner',BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED,id='NR-08'),
    pytest.param('tenant_manager','tenant_admin',BusinessRoleMutationDenialCode.ACTOR_NOT_ELIGIBLE,id='NR-09'), pytest.param('tenant_auditor','tenant_admin',BusinessRoleMutationDenialCode.ACTOR_NOT_ELIGIBLE,id='NR-10')])
def test_a7a_normal_revoke_matrix(actor, current, expected):
    result = _a7a(actor, 'business_role_revoke', current, current)
    assert result.allowed is (expected is None); assert result.denial_code is expected

def _a7b(actor, op, requested, current=None, owners=2):
    return evaluate_business_role_mutation('actor', 'tenant', actor, op, 'target', 'tenant', requested,
        current, TenantBusinessRoleStatus.ACTIVE if current else None,
        TenantMembershipStatus.ACTIVE, owners, OwnershipTransitionContext.OWNERSHIP_TRANSFER)

@pytest.mark.parametrize('actor,requested,expected', [
    pytest.param('tenant_owner','tenant_owner',None,id='TA-01'), pytest.param('tenant_owner','tenant_admin',None,id='TA-02'),
    pytest.param('tenant_owner','tenant_manager',None,id='TA-03'), pytest.param('tenant_owner','tenant_auditor',None,id='TA-04'),
    pytest.param('tenant_admin','tenant_owner',BusinessRoleMutationDenialCode.TARGET_ROLE_EXCEEDS_CEILING,id='TA-05'), pytest.param('tenant_admin','tenant_manager',None,id='TA-06'),
    pytest.param('tenant_manager','tenant_manager',BusinessRoleMutationDenialCode.ACTOR_NOT_ELIGIBLE,id='TA-07'), pytest.param('tenant_auditor','tenant_auditor',BusinessRoleMutationDenialCode.ACTOR_NOT_ELIGIBLE,id='TA-08')])
def test_a7b_transfer_assign_matrix(actor, requested, expected):
    result = _a7b(actor, 'business_role_assign', requested)
    assert result.allowed is (expected is None); assert result.denial_code is expected

@pytest.mark.parametrize('actor,current,requested,owners,expected', [
    pytest.param('tenant_owner','tenant_admin','tenant_owner',1,None,id='TC-01'), pytest.param('tenant_owner','tenant_owner','tenant_admin',2,None,id='TC-02'),
    pytest.param('tenant_owner','tenant_owner','tenant_manager',2,None,id='TC-03'), pytest.param('tenant_owner','tenant_owner','tenant_auditor',2,None,id='TC-04'),
    pytest.param('tenant_owner','tenant_owner','tenant_admin',1,BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED,id='TC-05'), pytest.param('tenant_owner','tenant_owner','tenant_manager',0,BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED,id='TC-06'),
    pytest.param('tenant_admin','tenant_manager','tenant_owner',2,BusinessRoleMutationDenialCode.TARGET_ROLE_EXCEEDS_CEILING,id='TC-07'), pytest.param('tenant_admin','tenant_owner','tenant_manager',2,BusinessRoleMutationDenialCode.TARGET_ROLE_EXCEEDS_CEILING,id='TC-08'),
    pytest.param('tenant_owner','tenant_admin','tenant_manager',2,None,id='TC-09')])
def test_a7b_transfer_change_matrix(actor, current, requested, owners, expected):
    result = _a7b(actor, 'business_role_change', requested, current, owners)
    assert result.allowed is (expected is None); assert result.denial_code is expected

@pytest.mark.parametrize('actor,current,owners,expected', [
    pytest.param('tenant_owner','tenant_owner',2,None,id='TR-01'), pytest.param('tenant_owner','tenant_owner',1,BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED,id='TR-02'),
    pytest.param('tenant_owner','tenant_owner',0,BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED,id='TR-03'), pytest.param('tenant_admin','tenant_owner',2,BusinessRoleMutationDenialCode.TARGET_ROLE_EXCEEDS_CEILING,id='TR-04'),
    pytest.param('tenant_owner','tenant_manager',2,None,id='TR-05'), pytest.param('tenant_admin','tenant_manager',2,None,id='TR-06'),
    pytest.param('tenant_manager','tenant_manager',2,BusinessRoleMutationDenialCode.ACTOR_NOT_ELIGIBLE,id='TR-07'), pytest.param('tenant_auditor','tenant_manager',2,BusinessRoleMutationDenialCode.ACTOR_NOT_ELIGIBLE,id='TR-08')])
def test_a7b_transfer_revoke_matrix(actor, current, owners, expected):
    result = _a7b(actor, 'business_role_revoke', current, current, owners)
    assert result.allowed is (expected is None); assert result.denial_code is expected

def _a7c(op, current, status, requested='tenant_manager', actor='tenant_owner', target='target', owners=2, ctx=OwnershipTransitionContext.NORMAL):
    return evaluate_business_role_mutation('actor', 'tenant', actor, op, target, 'tenant', requested, current, status, TenantMembershipStatus.ACTIVE, owners, ctx)

@pytest.mark.parametrize('current,status,expected', [pytest.param(None,None,None,id='SA-01'), pytest.param('tenant_manager',TenantBusinessRoleStatus.ACTIVE,BusinessRoleMutationDenialCode.TARGET_ROLE_STATE_INVALID,id='SA-02'), pytest.param('tenant_manager',TenantBusinessRoleStatus.REVOKED,None,id='SA-03')])
def test_a7c_assign_role_state_matrix(current,status,expected):
    r=_a7c('business_role_assign',current,status); assert r.allowed is (expected is None); assert r.denial_code is expected

@pytest.mark.parametrize('current,status,expected', [pytest.param(None,None,BusinessRoleMutationDenialCode.TARGET_ROLE_STATE_INVALID,id='SC-01'), pytest.param('tenant_admin',TenantBusinessRoleStatus.ACTIVE,None,id='SC-02'), pytest.param('tenant_admin',TenantBusinessRoleStatus.REVOKED,BusinessRoleMutationDenialCode.TARGET_ROLE_STATE_INVALID,id='SC-03'), pytest.param('tenant_manager',TenantBusinessRoleStatus.ACTIVE,BusinessRoleMutationDenialCode.SAME_ROLE_MUTATION,id='SC-04')])
def test_a7c_change_role_state_matrix(current,status,expected):
    r=_a7c('business_role_change',current,status); assert r.allowed is (expected is None); assert r.denial_code is expected

@pytest.mark.parametrize('current,status,expected', [pytest.param(None,None,BusinessRoleMutationDenialCode.TARGET_ROLE_STATE_INVALID,id='SR-01'), pytest.param('tenant_manager',TenantBusinessRoleStatus.ACTIVE,None,id='SR-02'), pytest.param('tenant_manager',TenantBusinessRoleStatus.REVOKED,BusinessRoleMutationDenialCode.TARGET_ROLE_STATE_INVALID,id='SR-03')])
def test_a7c_revoke_role_state_matrix(current,status,expected):
    r=_a7c('business_role_revoke',current,status); assert r.allowed is (expected is None); assert r.denial_code is expected

@pytest.mark.parametrize('current,status', [pytest.param(None,TenantBusinessRoleStatus.ACTIVE,id='MS-01'), pytest.param(None,TenantBusinessRoleStatus.REVOKED,id='MS-02'), pytest.param('tenant_manager',None,id='MS-03'), pytest.param('unknown',TenantBusinessRoleStatus.ACTIVE,id='MS-04'), pytest.param('tenant_manager','UNKNOWN',id='MS-05')])
def test_a7c_malformed_role_state_matrix(current,status):
    assert _a7c('business_role_change',current,status).denial_code is BusinessRoleMutationDenialCode.MALFORMED_INPUT

@pytest.mark.parametrize('current,status', [pytest.param(None,None,id='MS-06'), pytest.param('tenant_manager',TenantBusinessRoleStatus.ACTIVE,id='MS-07'), pytest.param('tenant_admin',TenantBusinessRoleStatus.REVOKED,id='MS-08')])
def test_a7c_malformed_self_role_state_matrix(current,status):
    assert _a7c('business_role_change',current,status,actor='tenant_admin',target='actor').denial_code is BusinessRoleMutationDenialCode.MALFORMED_INPUT

@pytest.mark.parametrize('owners,expected', [pytest.param(-1,BusinessRoleMutationDenialCode.MALFORMED_INPUT,id='OC-01'), pytest.param(True,BusinessRoleMutationDenialCode.MALFORMED_INPUT,id='OC-02'), pytest.param(False,BusinessRoleMutationDenialCode.MALFORMED_INPUT,id='OC-03'), pytest.param(0,BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED,id='OC-04'), pytest.param(1,BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED,id='OC-05'), pytest.param(2,None,id='OC-06'), pytest.param(3,None,id='OC-07')])
def test_a7c_owner_count_matrix(owners,expected):
    r=_a7c('business_role_revoke','tenant_owner',TenantBusinessRoleStatus.ACTIVE,requested='tenant_owner',owners=owners,ctx=OwnershipTransitionContext.OWNERSHIP_TRANSFER); assert r.allowed is (expected is None); assert r.denial_code is expected

@pytest.mark.parametrize('owners', [pytest.param(0, id='OC-08')])
def test_a7c_owner_count_does_not_block_non_owner_mutation(owners):
    assert _a7c('business_role_change','tenant_admin',TenantBusinessRoleStatus.ACTIVE,owners=owners).allowed

@pytest.mark.parametrize('op,current,status,requested,expected', [
    pytest.param('business_role_assign','tenant_admin',TenantBusinessRoleStatus.ACTIVE,'tenant_admin',BusinessRoleMutationDenialCode.TARGET_ROLE_STATE_INVALID,id='AS-01'),
    pytest.param('business_role_assign',None,None,'tenant_admin',BusinessRoleMutationDenialCode.MALFORMED_INPUT,id='AS-02'),
    pytest.param('business_role_assign','tenant_manager',TenantBusinessRoleStatus.ACTIVE,'tenant_admin',BusinessRoleMutationDenialCode.MALFORMED_INPUT,id='AS-03'),
    pytest.param('business_role_change','tenant_admin',TenantBusinessRoleStatus.ACTIVE,'tenant_manager',None,id='AS-04'),
    pytest.param('business_role_change','tenant_admin',TenantBusinessRoleStatus.ACTIVE,'tenant_auditor',None,id='AS-05'),
    pytest.param('business_role_change','tenant_admin',TenantBusinessRoleStatus.ACTIVE,'tenant_admin',BusinessRoleMutationDenialCode.SAME_ROLE_MUTATION,id='AS-06'),
    pytest.param('business_role_change','tenant_admin',TenantBusinessRoleStatus.ACTIVE,'tenant_owner',BusinessRoleMutationDenialCode.SELF_PROMOTION_FORBIDDEN,id='AS-07'),
    pytest.param('business_role_revoke','tenant_admin',TenantBusinessRoleStatus.ACTIVE,'tenant_admin',BusinessRoleMutationDenialCode.SELF_REVOCATION_FORBIDDEN,id='AS-08')])
def test_a7d_admin_self_mutation_matrix(op,current,status,requested,expected):
    r=_a7c(op,current,status,requested,actor='tenant_admin',target='actor',owners=2); assert r.allowed is (expected is None); assert r.denial_code is expected

@pytest.mark.parametrize('op,ctx,requested,owners,expected', [
    pytest.param('business_role_change',OwnershipTransitionContext.NORMAL,'tenant_admin',2,BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED,id='OS-01'),
    pytest.param('business_role_change',OwnershipTransitionContext.NORMAL,'tenant_manager',2,BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED,id='OS-02'),
    pytest.param('business_role_change',OwnershipTransitionContext.NORMAL,'tenant_auditor',2,BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED,id='OS-03'),
    pytest.param('business_role_change',OwnershipTransitionContext.OWNERSHIP_TRANSFER,'tenant_admin',2,None,id='OS-04'),
    pytest.param('business_role_change',OwnershipTransitionContext.OWNERSHIP_TRANSFER,'tenant_manager',2,None,id='OS-05'),
    pytest.param('business_role_change',OwnershipTransitionContext.OWNERSHIP_TRANSFER,'tenant_auditor',2,None,id='OS-06'),
    pytest.param('business_role_change',OwnershipTransitionContext.OWNERSHIP_TRANSFER,'tenant_admin',1,BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED,id='OS-07'),
    pytest.param('business_role_revoke',OwnershipTransitionContext.NORMAL,'tenant_owner',1,BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED,id='OS-08'),
    pytest.param('business_role_revoke',OwnershipTransitionContext.OWNERSHIP_TRANSFER,'tenant_owner',2,None,id='OS-09'),
    pytest.param('business_role_revoke',OwnershipTransitionContext.OWNERSHIP_TRANSFER,'tenant_owner',1,BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED,id='OS-10')])
def test_a7d_owner_self_mutation_matrix(op,ctx,requested,owners,expected):
    r=_a7c(op,'tenant_owner',TenantBusinessRoleStatus.ACTIVE,requested,actor='tenant_owner',target='actor',owners=owners,ctx=ctx); assert r.allowed is (expected is None); assert r.denial_code is expected

@pytest.mark.parametrize('case,expected', [
    pytest.param('malformed_unknown',BusinessRoleMutationDenialCode.MALFORMED_INPUT,id='DP-01'), pytest.param('unknown_cross',BusinessRoleMutationDenialCode.UNKNOWN_OPERATION,id='DP-02'),
    pytest.param('cross_missing',BusinessRoleMutationDenialCode.CROSS_TENANT,id='DP-03'), pytest.param('cross_inactive',BusinessRoleMutationDenialCode.CROSS_TENANT,id='DP-04'),
    pytest.param('missing_ineligible',BusinessRoleMutationDenialCode.TARGET_NOT_MEMBER,id='DP-05'), pytest.param('inactive_ineligible',BusinessRoleMutationDenialCode.TARGET_MEMBERSHIP_INACTIVE,id='DP-06'),
    pytest.param('ineligible_state',BusinessRoleMutationDenialCode.ACTOR_NOT_ELIGIBLE,id='DP-07'), pytest.param('malformed_later',BusinessRoleMutationDenialCode.MALFORMED_INPUT,id='DP-08'),
    pytest.param('invalid_same',BusinessRoleMutationDenialCode.TARGET_ROLE_STATE_INVALID,id='DP-09'), pytest.param('same_transition',BusinessRoleMutationDenialCode.SAME_ROLE_MUTATION,id='DP-10'),
    pytest.param('admin_self_promote',BusinessRoleMutationDenialCode.SELF_PROMOTION_FORBIDDEN,id='DP-11'), pytest.param('admin_self_revoke',BusinessRoleMutationDenialCode.SELF_REVOCATION_FORBIDDEN,id='DP-12'),
    pytest.param('normal_last',BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED,id='DP-13'), pytest.param('transfer_last',BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED,id='DP-14'), pytest.param('admin_transfer_owner',BusinessRoleMutationDenialCode.TARGET_ROLE_EXCEEDS_CEILING,id='DP-15')])
def test_a7e_denial_precedence_matrix(case, expected):
    kw=dict(actor_principal_id='a',actor_tenant_id='t',actor_business_role='tenant_owner',operation='business_role_assign',target_principal_id='b',target_tenant_id='t',requested_business_role='tenant_admin',current_target_role=None,current_target_role_status=None,target_membership_status=TenantMembershipStatus.ACTIVE,active_owner_count=2,ownership_transition=OwnershipTransitionContext.NORMAL)
    if case=='malformed_unknown': kw.update(actor_principal_id=' ',operation='bad')
    elif case=='unknown_cross': kw.update(operation='bad',target_tenant_id='other')
    elif case=='cross_missing' or case=='cross_inactive': kw.update(target_tenant_id='other',target_membership_status=None if case=='cross_missing' else TenantMembershipStatus.REVOKED)
    elif case=='missing_ineligible' or case=='inactive_ineligible': kw.update(actor_business_role='tenant_manager',target_membership_status=None if case=='missing_ineligible' else TenantMembershipStatus.REVOKED)
    elif case=='ineligible_state': kw.update(actor_business_role='tenant_manager',operation='business_role_change')
    elif case=='malformed_later': kw.update(current_target_role=None,current_target_role_status=TenantBusinessRoleStatus.ACTIVE)
    elif case=='invalid_same': kw.update(current_target_role='tenant_admin',current_target_role_status=TenantBusinessRoleStatus.ACTIVE)
    elif case=='same_transition': kw.update(operation='business_role_change',requested_business_role='tenant_owner',current_target_role='tenant_owner',current_target_role_status=TenantBusinessRoleStatus.ACTIVE)
    elif case=='admin_self_promote': kw.update(actor_principal_id='a',target_principal_id='a',actor_business_role='tenant_admin',operation='business_role_change',requested_business_role='tenant_owner',current_target_role='tenant_admin',current_target_role_status=TenantBusinessRoleStatus.ACTIVE)
    elif case=='admin_self_revoke': kw.update(actor_principal_id='a',target_principal_id='a',actor_business_role='tenant_admin',operation='business_role_revoke',requested_business_role='tenant_admin',current_target_role='tenant_admin',current_target_role_status=TenantBusinessRoleStatus.ACTIVE)
    elif case=='normal_last': kw.update(operation='business_role_revoke',requested_business_role='tenant_owner',current_target_role='tenant_owner',current_target_role_status=TenantBusinessRoleStatus.ACTIVE,active_owner_count=1)
    elif case=='transfer_last': kw.update(operation='business_role_revoke',requested_business_role='tenant_owner',current_target_role='tenant_owner',current_target_role_status=TenantBusinessRoleStatus.ACTIVE,active_owner_count=1,ownership_transition=OwnershipTransitionContext.OWNERSHIP_TRANSFER)
    else: kw.update(actor_business_role='tenant_admin',operation='business_role_change',requested_business_role='tenant_manager',current_target_role='tenant_owner',current_target_role_status=TenantBusinessRoleStatus.ACTIVE,ownership_transition=OwnershipTransitionContext.OWNERSHIP_TRANSFER)
    r=evaluate_business_role_mutation(**kw); assert r.denial_code is expected

@pytest.mark.parametrize('allowed,denial,valid', [pytest.param(True,None,True,id='DC-01'),pytest.param(False,BusinessRoleMutationDenialCode.MALFORMED_INPUT,True,id='DC-02'),pytest.param(True,BusinessRoleMutationDenialCode.MALFORMED_INPUT,False,id='DC-03'),pytest.param(False,None,False,id='DC-04')])
def test_a7e_decision_constructor_matrix(allowed, denial, valid):
    args=(allowed,'business_role_assign',denial,'a','b','t','tenant_admin',OwnershipTransitionContext.NORMAL)
    if valid: assert BusinessRoleMutationDecision(*args).allowed is allowed
    else:
        with pytest.raises(ValueError): BusinessRoleMutationDecision(*args)

# ARTIFACT: test_tenant_business_role_delegation_policy.py
# VERSION: v1.0.0-WILSY-TENANT-BUSINESS-ROLE-DELEGATION-CERT
# AUTHORITY BOUNDARY: direct policy certification only; no authority grant
# TENANT POSTURE: exact tenant binding is asserted
# FAIL-CLOSED POSTURE: malformed and unauthorized inputs must deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
