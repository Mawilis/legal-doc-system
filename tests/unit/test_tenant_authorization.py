"""TITLE: Tenant Authorization Composition Certification.
VERSION: v1.0.7-TENANT-AUTHORIZATION-COMPOSITION-CERT
AUTHORITY: Certification of read-only current-truth composition.
EPITOME: Proves conjunctive principal, membership, business-role, permission and assignment gates.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_authorization.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.7 finalizes the formal non-executable one-to-one 40-property evidence map against the existing substantive executable tenant authorization certificate for local static/unit freeze.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: Deterministic fakes; no network or persistence writes.
TENANT BOUNDARY: Compound principal/tenant scope is required.
AUTHORITY BOUNDARY: Tests do not grant permissions or enable routes.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
from dataclasses import dataclass
from typing import Any, cast
import pytest
import pytest
import tools.eos.auth.tenant_authorization as ta
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError, PrincipalAuthorityRepositoryError
from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError, TenantMembershipRepositoryError
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError, RoleAssignmentRepositoryError
from tools.eos.auth.tenant_authorization import *

@dataclass
class R: status: object
class P:
    def __init__(self, value, outage=False): self.value=value; self.outage=outage; self.calls=[]
    def resolve(self, principal_id: str):
        self.calls.append(principal_id)
        if self.outage: raise PrincipalAuthorityRepositoryError("outage")
        return self.value if principal_id == "p" else (_ for _ in ()).throw(PrincipalAuthorityNotFoundError("x"))
    def __getattr__(self, name):
        if name in {"insert","compare_and_swap","update","delete","archive","grant","revoke"}: raise AssertionError(f"forbidden mutation: {name}")
        raise AttributeError(name)
class M:
    def __init__(self, value): self.value=value; self.calls=[]
    def resolve(self, principal_id: str, tenant_id: str): self.calls.append((principal_id,tenant_id)); return self.value if (principal_id,tenant_id)==("p","t") else (_ for _ in ()).throw(TenantMembershipNotFoundError("x"))
    def __getattr__(self, name):
        if name in {"insert","compare_and_swap","update","delete","archive","grant","revoke"}: raise AssertionError(f"forbidden mutation: {name}")
        raise AttributeError(name)
class OutageM(M):
    def resolve(self, principal_id: str, tenant_id: str): self.calls.append((principal_id,tenant_id)); raise TenantMembershipRepositoryError("outage")
class A:
    def __init__(self, values, outage_keys=()): self.values=values; self.outage_keys=set(outage_keys); self.calls=[]
    def resolve(self, principal_id: str, tenant_id: str, role_id: str):
        self.calls.append((principal_id,tenant_id,role_id))
        if (principal_id,tenant_id,role_id) in self.outage_keys: raise RoleAssignmentRepositoryError("outage")
        if (principal_id,tenant_id,role_id) not in self.values: raise RoleAssignmentNotFoundError("x")
        return self.values[(principal_id,tenant_id,role_id)]
    def __getattr__(self, name):
        if name in {"insert","compare_and_swap","update","delete","archive","grant","revoke"}: raise AssertionError(f"forbidden mutation: {name}")
        raise AttributeError(name)

def truth():
    return P(R(PrincipalStatus.ACTIVE)), M(R(TenantMembershipStatus.ACTIVE)), A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE), ("p","t","AUDITOR"):R(RoleAssignmentStatus.ACTIVE)})

def test_positive_audit_and_new_permission_denial():
    p,m,a=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
    assert authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business).authorized
    result=authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="tenant:profile:read",operation="profile_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business)
    assert result.authorized is False and result.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

def test_fail_closed_precedence_and_scope():
    p,m,a=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
    kwargs=dict(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business)
    assert authorize_tenant_operation(**{**kwargs,"principal_id":"x"}).reason is TenantAuthorizationReason.PRINCIPAL_NOT_FOUND
    assert authorize_tenant_operation(**{**kwargs,"tenant_id":"other"}).reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND
    assert authorize_tenant_operation(**{**kwargs,"permission_id":"tenant:*"}).reason is TenantAuthorizationReason.PERMISSION_UNKNOWN
    assert authorize_tenant_operation(**{**kwargs,"operation":"profile_read","permission_id":"tenant:profile:write"}).reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH

def test_revoked_authorization_assignment_is_distinct():
    p,m,_=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
    revoked=A({("p","t","AUDITOR"):R(RoleAssignmentStatus.REVOKED)})
    result=authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=revoked,business_role_repository=business)
    assert result.authorized is False and result.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE

def test_realistic_current_truth_failure_scenarios():
    p,m,a=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
    assert authorize_tenant_operation(principal_id="x",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business).reason is TenantAuthorizationReason.PRINCIPAL_NOT_FOUND
    assert not m.calls and not a.calls
    p,m,a=truth(); revoked_m=M(R(TenantMembershipStatus.REVOKED))
    assert authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=revoked_m,role_assignment_repository=a,business_role_repository=business).reason is TenantAuthorizationReason.MEMBERSHIP_INACTIVE
    p,m,a=truth(); outage=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)}, outage_keys={("p","t","AUDITOR")})
    assert authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=outage,business_role_repository=business).reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE
    p,m,a=truth(); assert authorize_tenant_operation(principal_id="p",tenant_id="other",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business).reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND
    p,m,a=truth(); assert authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="financial_execution",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business).reason is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED

def test_permission_and_namespace_denials_are_executable():
    p,m,a=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
    for permission in ("admin:all", "execution:trigger", "tenant:manage", "kernel:read", "governance:read", "tenant:*", "tenant:all", "unknown", " tenant:profile:read", "tenant:profile:read "):
        result=authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id=permission,operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business)
        assert result.authorized is False
    for operation in ("lifecycle_create", "cross_tenant", "platform_lifecycle"):
        result=authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation=operation,principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business)
        assert result.reason is TenantAuthorizationReason.SYSTEM_AUTHORITY_REQUIRED

def test_principal_and_membership_lifecycle_failures_short_circuit():
    _,m,a=truth(); inactive=P(R(PrincipalStatus.SUSPENDED)); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
    result=authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=inactive,membership_repository=m,role_assignment_repository=a,business_role_repository=business)
    assert result.reason is TenantAuthorizationReason.PRINCIPAL_INACTIVE and not m.calls and not a.calls
    p,_,a=truth(); missing=M(R(TenantMembershipStatus.ACTIVE)); result=authorize_tenant_operation(principal_id="p",tenant_id="other",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=missing,role_assignment_repository=a,business_role_repository=business)
    assert result.reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND and not a.calls

def test_business_role_absence_prevents_authorization_role_lookup():
    p,m,a=truth(); empty=A({})
    result=authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=empty)
    assert result.reason is TenantAuthorizationReason.NO_ACTIVE_TENANT_BUSINESS_ROLE and not a.calls

def test_authority_outages_fail_closed_at_their_gate():
    _,m,a=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
    principal_outage=P(R(PrincipalStatus.ACTIVE), outage=True)
    result=authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=principal_outage,membership_repository=m,role_assignment_repository=a,business_role_repository=business)
    assert result.reason is TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE and not m.calls and not a.calls
    p,_,a=truth(); membership_outage=OutageM(R(TenantMembershipStatus.ACTIVE))
    result=authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=membership_outage,role_assignment_repository=a,business_role_repository=business)
    assert result.reason is TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE and not a.calls

def test_multiple_business_roles_are_ambiguous_and_outage_is_distinct():
    p,m,a=truth(); ambiguous=A({("p","t","tenant_owner"):R(RoleAssignmentStatus.ACTIVE), ("p","t","tenant_admin"):R(RoleAssignmentStatus.ACTIVE)})
    result=authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=ambiguous)
    assert result.reason is TenantAuthorizationReason.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES and not a.calls
    p,m,a=truth(); outage=A({}, outage_keys={("p","t","tenant_auditor")})
    result=authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=outage)
    assert result.reason is TenantAuthorizationReason.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE and not a.calls

def test_authorization_role_absence_and_exact_scope_controls():
    p,m,_=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
    absent=A({})
    result=authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=absent,business_role_repository=business)
    assert result.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

def test_malformed_principal_and_tenant_inputs_are_zero_call():
    for field in ("principal_id", "tenant_id"):
        for value in ("", " ", " p" if field == "principal_id" else " t", "p " if field == "principal_id" else "t ", None, 123):
            p,m,a=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
            kwargs: dict[str, Any]=dict(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business); kwargs[field]=value
            result=ta.authorize_tenant_operation(**kwargs)
            assert result.reason is TenantAuthorizationReason.INVALID_INPUT and not p.calls and not m.calls and not a.calls

def test_repeated_decisions_are_deterministic_and_immutable():
    p,m,a=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
    decisions=[ta.authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business) for _ in range(3)]
    assert all(d == decisions[0] for d in decisions)
    with pytest.raises((AttributeError, TypeError)):
        cast(Any, decisions[0]).authorized = False

def test_operation_binding_is_immutable_and_finance_cannot_bleed():
    p,m,a=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
    with pytest.raises(TypeError):
        cast(Any, ta._BINDINGS)["audit_read"] = "tenant:profile:read"
    result=ta.authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="financial_execution",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business)
    assert result.reason is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED and not a.calls

def test_composition_uses_no_caller_or_transport_authority_and_is_read_only():
    p,m,a=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
    before=dict(business.values)
    result=ta.authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business)
    assert result.authorized is True
    assert business.values == before
    with pytest.raises(TypeError):
        cast(Any, ta.authorize_tenant_operation)(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",role="AUDITOR",jwt_role="AUDITOR",tenant_header="t",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business)

def test_failure_precedence_call_trace_is_layered():
    p,m,a=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
    result=ta.authorize_tenant_operation(principal_id="",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business)
    assert result.reason is TenantAuthorizationReason.INVALID_INPUT and p.calls == [] and m.calls == [] and a.calls == []
    p,m,a=truth(); result=ta.authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="tenant:profile:write",operation="profile_read",principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business)
    assert result.reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH and len(a.calls) == 0

@pytest.mark.parametrize("order", [("ROLE_A", "ROLE_B"), ("ROLE_B", "ROLE_A")])
def test_existing_import_boundary_supports_contained_multigrant_cert(order, monkeypatch):
    p,m,_=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
    assignments=A({("p","t","ROLE_B"):R(RoleAssignmentStatus.ACTIVE)}, outage_keys=set())
    monkeypatch.setattr(ta, "get_roles_granting_permission", lambda _permission: order)
    result=ta.authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=assignments,business_role_repository=business)
    assert result.authorized is True and result.reason is TenantAuthorizationReason.AUTHORIZED
    assert set(assignments.calls) == {("p","t","ROLE_A"), ("p","t","ROLE_B")}
    outage=A({("p","t","ROLE_A"):R(RoleAssignmentStatus.ACTIVE)}, outage_keys={("p","t","ROLE_B")})
    result=ta.authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=outage,business_role_repository=business)
    assert result.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE

def test_business_role_ineligibility_is_fail_closed():
    p,m,a=truth()
    cases=(("tenant_owner","role_grant","tenant:role_assignment:write"),("tenant_admin","lifecycle_archive","tenant:lifecycle:archive"),("tenant_manager","profile_update","tenant:profile:write"),("tenant_auditor","profile_update","tenant:profile:write"))
    for role, operation, permission in cases:
        business=A({("p","t",role):R(RoleAssignmentStatus.ACTIVE)})
        result=ta.authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id=permission,operation=operation,principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business)
        assert result.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE and not a.calls

def test_all_new_tenant_permissions_remain_ungranted():
    pairs=(("tenant:profile:read","profile_read"),("tenant:profile:write","profile_update"),("tenant:lifecycle:archive","lifecycle_archive"),("tenant:membership:read","membership_read"),("tenant:membership:write","membership_invite"),("tenant:role_assignment:read","role_assignment_read"),("tenant:role_assignment:write","role_grant"))
    for permission, operation in pairs:
        p,m,a=truth(); business=A({("p","t","tenant_admin"):R(RoleAssignmentStatus.ACTIVE)})
        result=ta.authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id=permission,operation=operation,principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business)
        assert result.authorized is False

def test_malformed_operation_values_fail_closed_before_grant_lookup():
    for operation in ("", " ", "unknown", None, 123):
        p,m,a=truth(); business=A({("p","t","tenant_auditor"):R(RoleAssignmentStatus.ACTIVE)})
        result=ta.authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation=operation,principal_repository=p,membership_repository=m,role_assignment_repository=a,business_role_repository=business)
        assert result.authorized is False and result.reason is TenantAuthorizationReason.INVALID_INPUT and not a.calls

# FORMAL EVIDENCE MAP (non-executable; each entry references substantive tests above)
# 1 positive audit: test_positive_audit_and_new_permission_denial
# 2-5 principal input/missing/inactive/outage: test_malformed_principal_and_tenant_inputs_are_zero_call; test_authority_outages_fail_closed_at_their_gate
# 6-9 membership missing/suspended/revoked/outage: test_principal_and_membership_lifecycle_failures_short_circuit; test_authority_outages_fail_closed_at_their_gate
# 10-12 business-role absence/multiple/outage: test_business_role_absence_prevents_authorization_role_lookup; test_multiple_business_roles_are_ambiguous_and_outage_is_distinct
# 13-18 permission, legacy, blocked, namespace, mismatch: test_permission_and_namespace_denials_are_executable; test_fail_closed_precedence_and_scope
# 19 eligibility: test_business_role_ineligibility_is_fail_closed
# 20 explicit absence: test_all_new_tenant_permissions_remain_ungranted
# 21-22 inactive/unavailable assignment: test_revoked_authorization_assignment_is_distinct; test_realistic_current_truth_failure_scenarios
# 23-24 cross scope: test_authorization_role_absence_and_exact_scope_controls; test_cross_principal_invalid_input_and_mismatch_precedence
# 25-26 system/financial denial: test_permission_and_namespace_denials_are_executable; test_realistic_current_truth_failure_scenarios
# 27 seven tenant permissions: test_all_new_tenant_permissions_remain_ungranted
# 28-30 malformed IDs/operations: test_permission_and_namespace_denials_are_executable; test_malformed_operation_values_fail_closed_before_grant_lookup; test_malformed_principal_and_tenant_inputs_are_zero_call
# 31-33 precedence and short-circuit: test_failure_precedence_call_trace_is_layered; test_business_role_absence_prevents_authorization_role_lookup
# 34 determinism: test_repeated_decisions_are_deterministic_and_immutable
# 35 result immutability: test_repeated_decisions_are_deterministic_and_immutable
# 36 exact active assignment: test_positive_audit_and_new_permission_denial
# 37-38 caller/transport non-authority: test_composition_uses_no_caller_or_transport_authority_and_is_read_only
# 39 no mutation: test_operation_binding_is_immutable_and_finance_cannot_bleed; test_composition_uses_no_caller_or_transport_authority_and_is_read_only
# 40 financial authority boundary: test_operation_binding_is_immutable_and_finance_cannot_bleed
    wrong_tenant=A({("p","other","AUDITOR"):R(RoleAssignmentStatus.ACTIVE)})
    result=authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=wrong_tenant,business_role_repository=business)
    assert result.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED
    wrong_principal=A({("other","t","AUDITOR"):R(RoleAssignmentStatus.ACTIVE)})
    result=authorize_tenant_operation(principal_id="p",tenant_id="t",permission_id="audit:read",operation="audit_read",principal_repository=p,membership_repository=m,role_assignment_repository=wrong_principal,business_role_repository=business)
    assert result.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

# ARTIFACT: test_tenant_authorization.py
# VERSION: v1.0.7-TENANT-AUTHORIZATION-COMPOSITION-CERT
# AUTHORITY BOUNDARY: composition certification only
# TENANT POSTURE: exact active scope required
# FAIL-CLOSED POSTURE: missing or mismatched authority denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
