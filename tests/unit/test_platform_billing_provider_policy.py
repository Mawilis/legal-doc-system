"""TITLE: Platform Billing Provider Policy Certificate.
VERSION: v1.0.0-M11E2D5C2F-R2.
AUTHORITY: Kennel EOS policy evidence certificate.
EPITOME: Proves immutable tenant-scoped outbound policy and issuance.
ABSOLUTE CANONICAL PATH: tests/unit/test_platform_billing_provider_policy.py
COLLABORATION / OWNERSHIP: Kennel EOS policy owners.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 adds direct domain, registry and issuance coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant scope is asserted.
AUTHORITY BOUNDARY: Eligibility only; no routing or execution.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
import pytest
from typing import Any, cast
from tools.eos.kennel.domain.platform_billing_provider_policy import PlatformBillingProviderPolicy, PlatformBillingProviderPolicyError, PolicyStatus
from tools.eos.kennel.registry.platform_billing_provider_policy_registry import PlatformBillingProviderPolicyRegistry
from tools.eos.kennel.orchestration.platform_billing_provider_policy_issuance import issue_platform_billing_provider_policy, PlatformBillingProviderPolicyIssuanceError
from tools.eos.kennel.domain.platform_billing_provider_policy_revision_authorization_subject import PlatformBillingProviderPolicyRevisionAuthorizationSubject
from tools.eos.auth.tenant_authorization import authorize_tenant_operation
from tools.eos.auth.tenant_authorization_decision_evidence_registry import TenantAuthorizationDecisionEvidenceRegistry
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError

class Collection:
    def __init__(self): self.rows=[]
    def insert_one(self,row,**_): self.rows.append(dict(row))
    def find_one(self,q,**_): return next((r for r in self.rows if all(r.get(k)==v for k,v in q.items())),None)
class Session: in_transaction=True
def make(**overrides):
    t=datetime(2026,1,1,tzinfo=timezone.utc)
    values=dict(policy_id="p1",tenant_id="t1",lane="PLATFORM_BILLING_OUTBOUND",authorized_provider_names=("acme",),policy_revision=1,policy_authorization_reference="e1",effective_at=t,expires_at=None,created_at=t,status=PolicyStatus.ACTIVE)
    values.update(overrides); return PlatformBillingProviderPolicy(**cast(dict[str, Any], values))
def test_domain_determinism_and_invariants():
    p=make(); assert p.policy_fingerprint==make().policy_fingerprint; assert make(authorized_provider_names=("other",)).policy_fingerprint!=p.policy_fingerprint
    for bad in ({"tenant_id":""},{"lane":"CLIENT"},{"authorized_provider_names":()},{"authorized_provider_names":("x","x")},{"policy_revision":0}):
        with pytest.raises(PlatformBillingProviderPolicyError): make(**bad)
def test_registry_roundtrip_and_corruption_rejects():
    c=Collection(); p=make(); PlatformBillingProviderPolicyRegistry.create(p,c); assert PlatformBillingProviderPolicyRegistry.get("t1","p1",c)==p
    c.rows[0]["policy_fingerprint"]="0"*128
    with pytest.raises(Exception): PlatformBillingProviderPolicyRegistry.get("t1","p1",c)
def test_authorized_issuance_and_evidence_binding():
    e=SimpleNamespace(tenant_id="t1",permission="platform_billing:provider_policy:admin",operation="platform_billing_provider_policy_create",subject_reference="s",subject_evidence_fingerprint="f",authorization_decision_id="e1")
    c=Collection(); p=issue_platform_billing_provider_policy(authorization_evidence=e,tenant_id="t1",provider_names=("acme",),subject_reference="s",subject_fingerprint="f",collection=c,policy_id="p1",effective_at=datetime(2026,1,1,tzinfo=timezone.utc),created_at=datetime(2026,1,1,tzinfo=timezone.utc),session=Session()); assert PlatformBillingProviderPolicyRegistry.get("t1","p1",c)==p
    with pytest.raises(PlatformBillingProviderPolicyIssuanceError): issue_platform_billing_provider_policy(authorization_evidence=SimpleNamespace(**{**e.__dict__,"operation":"platform_billing_provider_policy_revise"}),tenant_id="t1",provider_names=("acme",),subject_reference="s",subject_fingerprint="f",collection=Collection(),policy_id="p2",effective_at=p.effective_at,created_at=p.created_at,session=Session())

def test_revision_authorization_subject_binds_exact_policy_facts():
    subject=PlatformBillingProviderPolicyRevisionAuthorizationSubject.from_policy(make())
    assert subject.subject_reference == "platform-policy-revision:t1:p1:1"
    assert subject.subject_evidence_fingerprint == PlatformBillingProviderPolicyRevisionAuthorizationSubject.from_policy(make()).subject_evidence_fingerprint
    assert subject.subject_evidence_fingerprint != PlatformBillingProviderPolicyRevisionAuthorizationSubject.from_policy(make(policy_revision=2)).subject_evidence_fingerprint

def test_real_activate_authorization_to_durable_evidence(monkeypatch):
    class P:
        def resolve(self, *_args, **_kwargs): return SimpleNamespace(status=PrincipalStatus.ACTIVE)
    class M:
        def resolve(self, *_args, **_kwargs): return SimpleNamespace(status=TenantMembershipStatus.ACTIVE, revision=1)
    class R:
        def __init__(self, role): self.role=role
        def resolve(self, _p, _t, role_id, **_kwargs):
            if role_id != self.role: raise RoleAssignmentNotFoundError("missing")
            return SimpleNamespace(status=RoleAssignmentStatus.ACTIVE, revision=1)
    p=make(); s=PlatformBillingProviderPolicyRevisionAuthorizationSubject.from_policy(p)
    decision=authorize_tenant_operation(principal_id="p",tenant_id="t1",permission_id="platform_billing:provider_policy:admin",operation="platform_billing_provider_policy_activate",principal_repository=P(),membership_repository=M(),role_assignment_repository=R("PLATFORM_BILLING_PROVIDER_POLICY_ADMIN"),business_role_repository=R("tenant_platform_billing_provider_policy_admin"))
    assert decision.authorized
    evidence=TenantAuthorizationDecisionEvidenceRegistry(cast(Any,Collection()),principal_repository=P(),membership_repository=M(),role_assignment_repository=R("PLATFORM_BILLING_PROVIDER_POLICY_ADMIN"),business_role_repository=R("tenant_platform_billing_provider_policy_admin"))
    row=evidence.issue(tenant_id="t1",principal_id="p",operation="platform_billing_provider_policy_activate",permission="platform_billing:provider_policy:admin",subject_reference=s.subject_reference,subject_evidence_fingerprint=s.subject_evidence_fingerprint,idempotency_key="activate-1",session=cast(Any,Session()))
    readback=evidence.get(tenant_id="t1",authorization_decision_id=row.authorization_decision_id,session=cast(Any,Session()))
    assert readback == row and readback.subject_reference == s.subject_reference and readback.subject_evidence_fingerprint == s.subject_evidence_fingerprint
    altered_fingerprint=PlatformBillingProviderPolicyRevisionAuthorizationSubject("t1","p1",1,"0"*128)
    altered_tenant=PlatformBillingProviderPolicyRevisionAuthorizationSubject("t2","p1",1,p.policy_fingerprint)
    assert altered_fingerprint.subject_evidence_fingerprint != s.subject_evidence_fingerprint
    assert altered_tenant.subject_reference != s.subject_reference and altered_tenant.subject_evidence_fingerprint != s.subject_evidence_fingerprint

# ARTIFACT: test_platform_billing_provider_policy.py
# VERSION: v1.0.0-M11E2D5C2F-R2
# AUTHORITY BOUNDARY: policy certificate only
# TENANT POSTURE: exact tenant scope
# FAIL-CLOSED POSTURE: malformed facts reject
# END OF WILSY OS SOVEREIGN ARTIFACT
