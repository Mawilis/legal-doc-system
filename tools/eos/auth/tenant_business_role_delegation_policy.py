"""TITLE: WILSY OS Tenant Business-Role Delegation Policy.
VERSION: v1.0.0-WILSY-TENANT-BUSINESS-ROLE-DELEGATION
AUTHORITY: Pure dynamic delegation decision evidence; no authorization or persistence.
EPITOME: Evaluates target-role, membership, lifecycle and ownership invariants.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_business_role_delegation_policy.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-05.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Actor and target must share an exact tenant.
AUTHORITY BOUNDARY: Returns dynamic evidence only; authorization-role checks remain independent.
FINANCIAL AUTHORITY BOUNDARY: No financial or Kennel authority; Kennel EOS is exclusive.
TRANSACTION BOUNDARY: Pure evaluator; caller-owned orchestration supplies committed evidence.
CHANGELOG: v1.0.1 closes self-target and decision-invariant enforcement gaps.
SECURITY / PRIVACY POSTURE: Deterministic fail-closed validation; no persistence, secrets, or network.
FAIL-CLOSED POSTURE: Malformed, unauthorized, cross-tenant, and ownership-breaking requests deny.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .tenant_business_role import TenantBusinessRoleStatus
from .tenant_authority_policy import TENANT_ROLES, tenant_role_operation_eligibility, ELIGIBLE
from .tenant_membership import TenantMembershipStatus

VERSION = "v1.0.0-WILSY-TENANT-BUSINESS-ROLE-DELEGATION"
class OwnershipTransitionContext(str, Enum): NORMAL="NORMAL"; OWNERSHIP_TRANSFER="OWNERSHIP_TRANSFER"
class BusinessRoleMutationDenialCode(str, Enum):
    MALFORMED_INPUT="MALFORMED_INPUT"; UNKNOWN_OPERATION="UNKNOWN_OPERATION"; CROSS_TENANT="CROSS_TENANT"; TARGET_NOT_MEMBER="TARGET_NOT_MEMBER"; TARGET_MEMBERSHIP_INACTIVE="TARGET_MEMBERSHIP_INACTIVE"; ACTOR_NOT_ELIGIBLE="ACTOR_NOT_ELIGIBLE"; TARGET_ROLE_STATE_INVALID="TARGET_ROLE_STATE_INVALID"; SAME_ROLE_MUTATION="SAME_ROLE_MUTATION"; SELF_PROMOTION_FORBIDDEN="SELF_PROMOTION_FORBIDDEN"; SELF_REVOCATION_FORBIDDEN="SELF_REVOCATION_FORBIDDEN"; OWNERSHIP_TRANSITION_REQUIRED="OWNERSHIP_TRANSITION_REQUIRED"; TARGET_ROLE_EXCEEDS_CEILING="TARGET_ROLE_EXCEEDS_CEILING"; LAST_OWNER_PROTECTED="LAST_OWNER_PROTECTED"
@dataclass(frozen=True, slots=True)
class BusinessRoleMutationDecision:
    allowed: bool; operation: str; denial_code: Optional[BusinessRoleMutationDenialCode]; actor_principal_id: str; target_principal_id: str; tenant_id: str; target_role: str; ownership_transition: OwnershipTransitionContext
    def __post_init__(self):
        if self.allowed and self.denial_code is not None: raise ValueError("allowed decisions cannot carry denial_code")
        if not self.allowed and not isinstance(self.denial_code, BusinessRoleMutationDenialCode): raise ValueError("denied decisions require denial_code")

def _deny(op, code, actor, target, tenant, role, ctx): return BusinessRoleMutationDecision(False, op, code, actor, target, tenant, role, ctx)
def evaluate_business_role_mutation(actor_principal_id: object, actor_tenant_id: object, actor_business_role: object, operation: object, target_principal_id: object, target_tenant_id: object, requested_business_role: object, current_target_role: object, current_target_role_status: object, target_membership_status: object, active_owner_count: object, ownership_transition: object) -> BusinessRoleMutationDecision:
    vals=(actor_principal_id,actor_tenant_id,target_principal_id,target_tenant_id)
    if any(not isinstance(v,str) or not v.strip() for v in vals) or not isinstance(actor_business_role,str) or actor_business_role not in TENANT_ROLES or not isinstance(requested_business_role,str) or requested_business_role not in TENANT_ROLES or not isinstance(active_owner_count,int) or isinstance(active_owner_count,bool) or active_owner_count<0 or not isinstance(ownership_transition,OwnershipTransitionContext): return _deny(str(operation),BusinessRoleMutationDenialCode.MALFORMED_INPUT,str(actor_principal_id),str(target_principal_id),str(actor_tenant_id),str(requested_business_role),ownership_transition if isinstance(ownership_transition,OwnershipTransitionContext) else OwnershipTransitionContext.NORMAL)
    assert isinstance(actor_principal_id, str)
    assert isinstance(actor_tenant_id, str)
    assert isinstance(target_principal_id, str)
    assert isinstance(target_tenant_id, str)
    assert isinstance(actor_business_role, str)
    assert isinstance(requested_business_role, str)
    if not isinstance(operation, str):
        return _deny(str(operation), BusinessRoleMutationDenialCode.UNKNOWN_OPERATION, actor_principal_id, target_principal_id, actor_tenant_id, requested_business_role, ownership_transition)
    if operation not in {"business_role_assign","business_role_change","business_role_revoke"}: return _deny(operation,BusinessRoleMutationDenialCode.UNKNOWN_OPERATION,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    if actor_tenant_id != target_tenant_id: return _deny(operation,BusinessRoleMutationDenialCode.CROSS_TENANT,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    if target_membership_status is None: return _deny(operation,BusinessRoleMutationDenialCode.TARGET_NOT_MEMBER,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    if target_membership_status is not TenantMembershipStatus.ACTIVE: return _deny(operation,BusinessRoleMutationDenialCode.TARGET_MEMBERSHIP_INACTIVE,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    if tenant_role_operation_eligibility(actor_business_role,operation) != ELIGIBLE: return _deny(operation,BusinessRoleMutationDenialCode.ACTOR_NOT_ELIGIBLE,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    if (current_target_role is None) != (current_target_role_status is None) or (current_target_role is not None and (not isinstance(current_target_role,str) or current_target_role not in TENANT_ROLES or not isinstance(current_target_role_status,TenantBusinessRoleStatus))): return _deny(operation,BusinessRoleMutationDenialCode.MALFORMED_INPUT,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    if actor_principal_id == target_principal_id and (current_target_role != actor_business_role or current_target_role_status is not TenantBusinessRoleStatus.ACTIVE): return _deny(operation, BusinessRoleMutationDenialCode.MALFORMED_INPUT, actor_principal_id, target_principal_id, actor_tenant_id, requested_business_role, ownership_transition)
    if operation == "business_role_assign" and current_target_role_status is TenantBusinessRoleStatus.ACTIVE: return _deny(operation,BusinessRoleMutationDenialCode.TARGET_ROLE_STATE_INVALID,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    if operation in {"business_role_change","business_role_revoke"} and current_target_role_status is not TenantBusinessRoleStatus.ACTIVE: return _deny(operation,BusinessRoleMutationDenialCode.TARGET_ROLE_STATE_INVALID,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    if operation == "business_role_change" and current_target_role == requested_business_role: return _deny(operation,BusinessRoleMutationDenialCode.SAME_ROLE_MUTATION,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    self_mut = actor_principal_id == target_principal_id
    if self_mut and (current_target_role_status is not TenantBusinessRoleStatus.ACTIVE or current_target_role != actor_business_role): return _deny(operation, BusinessRoleMutationDenialCode.MALFORMED_INPUT, actor_principal_id, target_principal_id, actor_tenant_id, requested_business_role, ownership_transition)
    if self_mut and operation == "business_role_assign": return _deny(operation, BusinessRoleMutationDenialCode.TARGET_ROLE_STATE_INVALID, actor_principal_id, target_principal_id, actor_tenant_id, requested_business_role, ownership_transition)
    if self_mut and operation == "business_role_change" and requested_business_role == "tenant_owner" and actor_business_role != "tenant_owner": return _deny(operation, BusinessRoleMutationDenialCode.SELF_PROMOTION_FORBIDDEN, actor_principal_id, target_principal_id, actor_tenant_id, requested_business_role, ownership_transition)
    if operation == "business_role_assign" and ownership_transition is OwnershipTransitionContext.NORMAL and requested_business_role == "tenant_owner": return _deny(operation, BusinessRoleMutationDenialCode.TARGET_ROLE_EXCEEDS_CEILING, actor_principal_id, target_principal_id, actor_tenant_id, requested_business_role, ownership_transition)
    if operation == "business_role_change" and ownership_transition is OwnershipTransitionContext.NORMAL and (current_target_role == "tenant_owner" or requested_business_role == "tenant_owner"):
        return _deny(operation, BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED, actor_principal_id, target_principal_id, actor_tenant_id, requested_business_role, ownership_transition)
    if operation == "business_role_revoke" and ownership_transition is OwnershipTransitionContext.NORMAL and current_target_role == "tenant_owner":
        return _deny(operation, BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED, actor_principal_id, target_principal_id, actor_tenant_id, requested_business_role, ownership_transition)
    if requested_business_role == "tenant_owner" and actor_business_role != "tenant_owner": return _deny(operation,BusinessRoleMutationDenialCode.TARGET_ROLE_EXCEEDS_CEILING,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    if self_mut and operation == "business_role_revoke":
        if actor_business_role == "tenant_owner" and ownership_transition is OwnershipTransitionContext.OWNERSHIP_TRANSFER and active_owner_count > 1: pass
        else: return _deny(operation,BusinessRoleMutationDenialCode.SELF_REVOCATION_FORBIDDEN if actor_business_role != "tenant_owner" else (BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED if active_owner_count <= 1 else BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED),actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    if current_target_role == "tenant_owner" and actor_business_role != "tenant_owner": return _deny(operation,BusinessRoleMutationDenialCode.TARGET_ROLE_EXCEEDS_CEILING,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    if current_target_role == "tenant_owner" and ownership_transition is OwnershipTransitionContext.NORMAL: return _deny(operation,BusinessRoleMutationDenialCode.OWNERSHIP_TRANSITION_REQUIRED,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    if operation == "business_role_change" and current_target_role == "tenant_owner" and active_owner_count <= 1: return _deny(operation,BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    if operation == "business_role_revoke" and current_target_role == "tenant_owner" and active_owner_count <= 1: return _deny(operation,BusinessRoleMutationDenialCode.LAST_OWNER_PROTECTED,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)
    return BusinessRoleMutationDecision(True,operation,None,actor_principal_id,target_principal_id,actor_tenant_id,requested_business_role,ownership_transition)

__all__=["VERSION","OwnershipTransitionContext","BusinessRoleMutationDenialCode","BusinessRoleMutationDecision","evaluate_business_role_mutation"]
# ARTIFACT: tenant_business_role_delegation_policy.py
# VERSION: v1.0.0-WILSY-TENANT-BUSINESS-ROLE-DELEGATION
# AUTHORITY BOUNDARY: pure delegation evidence only; no authorization or persistence
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
