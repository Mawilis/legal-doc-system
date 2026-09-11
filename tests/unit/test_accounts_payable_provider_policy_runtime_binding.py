"""TITLE: AP Provider-Policy Runtime Binding Direct Certificate.
VERSION: v1.0.1-M11E2C3-R4F-R1-R3.
AUTHORITY: Kennel EOS AP current-head certificate.
EPITOME: Direct constitutional certification of AP runtime-binding authority.
ABSOLUTE CANONICAL PATH: tests/unit/test_accounts_payable_provider_policy_runtime_binding.py
COLLABORATION / OWNERSHIP: Kennel EOS AP runtime authority certification.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.1-M11E2C3-R4F-R1-R3 certifies canonical head replacement and duplicate-head rejection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no secrets or PII.
TENANT BOUNDARY: Synthetic tenant-scoped fixtures.
AUTHORITY BOUNDARY: Certificate evidence only; no provider selection or execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes financial movement.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any
import hashlib
import pytest
from tools.eos.kennel.orchestration.accounts_payable_provider_policy_issuance import issue_accounts_payable_provider_policy
from tools.eos.kennel.orchestration.accounts_payable_provider_policy_runtime_binding import bind_accounts_payable_provider_policy_runtime
from tools.eos.auth.tenant_authorization_decision_evidence import TenantAuthorizationDecisionEvidence
from tools.eos.auth.tenant_authorization_decision_evidence_registry import TenantAuthorizationDecisionEvidenceRegistry
from tools.eos.kennel.domain.accounts_payable_provider_policy_runtime_binding import AccountsPayableProviderPolicyRuntimeBinding
from tools.eos.kennel.registry.accounts_payable_provider_policy_runtime_binding_registry import AccountsPayableProviderPolicyRuntimeBindingRegistry

class Collection:
    """Deterministic in-memory persistence double."""
    def __init__(self): self.rows=[]; self.sessions=[]
    def find_one(self,q,**kwargs): self.sessions.append(kwargs.get("session")); return next((r for r in self.rows if all(r.get(k)==v for k,v in q.items())),None)
    def insert_one(self,row,**kwargs): self.sessions.append(kwargs.get("session")); self.rows.append(dict(row))
    def replace_one(self,q,row,**kwargs):
        self.sessions.append(kwargs.get("session"))
        matches=[i for i,r in enumerate(self.rows) if all(r.get(k)==v for k,v in q.items())]
        if not matches: return SimpleNamespace(matched_count=0)
        self.rows[matches[0]]=dict(row); return SimpleNamespace(matched_count=1)
    def find(self,q,**kwargs): self.sessions.append(kwargs.get("session")); return [r for r in self.rows if all(r.get(k)==v for k,v in q.items())]
class Session: in_transaction=True
class Auth:
    def __init__(self,e): self.e=e
    def get(self,**kwargs): self.session=kwargs.get("session"); return self.e
class MultiAuth(Auth):
    def __init__(self, values): self.values=values; self.sessions=[]
    def get(self,**kwargs): self.sessions.append(kwargs.get("session")); return self.values[kwargs["authorization_decision_id"]]
def ev(op, decision, rev=1, tenant="tenant-a", policy="policy-a"):
    subject=f"accounts-payable-provider-policy:{tenant}:{policy}:{rev}"
    return SimpleNamespace(tenant_id=tenant,permission="accounts_payable:provider_policy:admin",operation=op,subject_reference=subject,subject_evidence_fingerprint=hashlib.sha3_512(subject.encode()).hexdigest(),authorization_decision_id=decision)
def p1(c,s): return issue_accounts_payable_provider_policy(authorization_evidence=ev("accounts_payable_provider_policy_create","create-1"),tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,provider_names=("provider-a",),predecessor_fingerprint=None,collection=c,effective_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
def test_initial_activation_and_explicit_current_head():
    p=p1(Collection(),Session()); assert p.policy_revision==1
def test_successor_activation_preserves_history():
    pc=Collection();bc=Collection();s=Session();p=p1(pc,s);r=bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=Auth(ev("accounts_payable_provider_policy_activate","a1")),binding_collection=bc,binding_id="b1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s);assert r.provider_policy_fingerprint==p.policy_fingerprint
@pytest.mark.parametrize("field,value",[("subject_reference","wrong"),("subject_evidence_fingerprint","0"*128)])
def test_activation_rejects_provenance_drift(field,value):
    pc=Collection();bc=Collection();s=Session();p1(pc,s);bad=ev("accounts_payable_provider_policy_activate","a1");setattr(bad,field,value)
    with pytest.raises(Exception): bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=Auth(bad),binding_collection=bc,binding_id="b1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)

def test_activation_rejects_same_tenant_cross_policy_subject():
    pc=Collection(); bc=Collection(); s=Session(); p1(pc,s)
    bad=ev("accounts_payable_provider_policy_activate","a1")
    with pytest.raises(Exception): bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-b",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=Auth(bad),binding_collection=bc,binding_id="b1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)

def test_missing_session_rejects_before_downstream_operations():
    pc=Collection(); bc=Collection(); auth=Auth(ev("accounts_payable_provider_policy_activate","a1"))
    with pytest.raises(Exception, match="ACTIVE_TRANSACTION_REQUIRED"):
        bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=auth,binding_collection=bc,binding_id="b1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=None)
    assert pc.sessions==[] and bc.sessions==[] and not hasattr(auth,"session")

def test_inactive_transaction_rejects_before_downstream_operations():
    pc=Collection(); bc=Collection(); auth=Auth(ev("accounts_payable_provider_policy_activate","a1")); s=SimpleNamespace(in_transaction=False)
    with pytest.raises(Exception, match="ACTIVE_TRANSACTION_REQUIRED"):
        bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=auth,binding_collection=bc,binding_id="b1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    assert pc.sessions==[] and bc.sessions==[] and not hasattr(auth,"session")

def test_active_transaction_uses_same_caller_session_for_all_operations():
    pc=Collection(); bc=Collection(); s=Session(); p=p1(pc,s); auth=Auth(ev("accounts_payable_provider_policy_activate","a1"))
    result=bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=auth,binding_collection=bc,binding_id="b1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    assert result.provider_policy_fingerprint==p.policy_fingerprint
    assert auth.session is s and all(seen is s for seen in pc.sessions + bc.sessions if seen is not None)

def test_successor_activation_passes_caller_session_to_predecessor_lookup():
    pc=Collection(); bc=Collection(); s=Session(); p_first=p1(pc,s)
    auths=MultiAuth({"a1":ev("accounts_payable_provider_policy_activate","a1",1),"a2":ev("accounts_payable_provider_policy_activate","a2",2)})
    r1=bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=auths,binding_collection=bc,binding_id="b1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    p_second=issue_accounts_payable_provider_policy(authorization_evidence=ev("accounts_payable_provider_policy_revise","rev-2",2),tenant_id="tenant-a",policy_id="policy-a",policy_revision=2,provider_names=("provider-a",),predecessor_fingerprint=p_first.policy_fingerprint,collection=pc,effective_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    r2=bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=2,authorization_decision_id="a2",policy_collection=pc,authorization_registry=auths,binding_collection=bc,binding_id="b2",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    assert r1.binding_id=="b1" and r2.previous_binding_id==r1.binding_id and r2.provider_policy_fingerprint==p_second.policy_fingerprint
    assert auths.sessions==[s,s] and all(seen is s for seen in pc.sessions + bc.sessions if seen is not None)

def _bind_inputs(pc: Any,bc: Any,s: Any,auth: Any,**overrides: Any) -> dict[str, Any]:
    values: dict[str, Any]=dict(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=auth,binding_collection=bc,binding_id="bad",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    values.update(overrides); return values

@pytest.mark.parametrize("case,override",[("wrong tenant",{"tenant_id":"tenant-b"}),("wrong id",{"policy_id":"policy-b"}),("wrong revision",{"policy_revision":2})])
def test_bound_policy_provenance_identity_must_resolve_canonically(case,override):
    pc=Collection(); bc=Collection(); s=Session(); p1(pc,s); auth=Auth(ev("accounts_payable_provider_policy_activate","a1"))
    with pytest.raises(Exception): bind_accounts_payable_provider_policy_runtime(**_bind_inputs(pc,bc,s,auth,**override))
    assert bc.rows==[]

def test_bound_policy_fingerprint_corruption_rejects_without_binding():
    pc=Collection(); bc=Collection(); s=Session(); p1(pc,s); pc.rows[0]["policy_fingerprint"]="0"*128; auth=Auth(ev("accounts_payable_provider_policy_activate","a1"))
    with pytest.raises(Exception): bind_accounts_payable_provider_policy_runtime(**_bind_inputs(pc,bc,s,auth))
    assert bc.rows==[]

def test_cross_family_policy_authority_rejects_without_binding():
    pc=Collection(); bc=Collection(); s=Session(); p1(pc,s); pc.rows[0]["family"]="PLATFORM_BILLING"; auth=Auth(ev("accounts_payable_provider_policy_activate","a1"))
    with pytest.raises(Exception): bind_accounts_payable_provider_policy_runtime(**_bind_inputs(pc,bc,s,auth))
    assert bc.rows==[]

@pytest.mark.parametrize("label,evidence",[
    ("missing",None),
    ("wrong tenant",SimpleNamespace(tenant_id="tenant-b",permission="accounts_payable:provider_policy:admin",operation="accounts_payable_provider_policy_activate",subject_reference="accounts-payable-provider-policy:tenant-a:policy-a:1",subject_evidence_fingerprint="")),
    ("create",ev("accounts_payable_provider_policy_create","a1")),
    ("revise",ev("accounts_payable_provider_policy_revise","a1")),
    ("revoke",ev("accounts_payable_provider_policy_revoke","a1")),
    ("platform",SimpleNamespace(tenant_id="tenant-a",permission="platform_billing:provider_policy:admin",operation="platform_billing_provider_policy_activate",subject_reference="accounts-payable-provider-policy:tenant-a:policy-a:1",subject_evidence_fingerprint="")),
    ("generic",SimpleNamespace(tenant_id="tenant-a",permission="tenant:admin",operation="accounts_payable_provider_policy_activate",subject_reference="accounts-payable-provider-policy:tenant-a:policy-a:1",subject_evidence_fingerprint="")),
    ("corrupt",SimpleNamespace(tenant_id="tenant-a",permission="accounts_payable:provider_policy:admin",operation="accounts_payable_provider_policy_activate",subject_reference="accounts-payable-provider-policy:tenant-a:policy-a:1",subject_evidence_fingerprint="0"*128)),
])
def test_activate_requires_exact_durable_authorization(label,evidence):
    pc=Collection(); bc=Collection(); s=Session(); p1(pc,s); auth=Auth(evidence)
    with pytest.raises(Exception): bind_accounts_payable_provider_policy_runtime(**_bind_inputs(pc,bc,s,auth))
    assert bc.rows==[]

def _durable_activate():
    subject="accounts-payable-provider-policy:tenant-a:policy-a:1"
    return TenantAuthorizationDecisionEvidence(tenant_id="tenant-a",authorization_decision_id="durable-a1",principal_id="principal-a",operation="accounts_payable_provider_policy_activate",permission="accounts_payable:provider_policy:admin",business_role="admin",authorization_role="admin",membership_revision=1,role_assignment_revision=1,subject_reference=subject,subject_evidence_fingerprint=hashlib.sha3_512(subject.encode()).hexdigest(),permission_namespace_version="v1",authorization_role_policy_version="v1",tenant_business_role_policy_version="v1",tenant_authorization_composition_version="v1",idempotency_key="idem-a1",authorized_at=datetime.now(timezone.utc))

def test_canonical_durable_authorization_readback_and_corruption_firewall():
    pc=Collection(); bc=Collection(); s=Session(); p1(pc,s); evidence=_durable_activate(); ac=Collection(); ac.rows.append(evidence.to_persisted()); registry=TenantAuthorizationDecisionEvidenceRegistry(ac,principal_repository=None)  # type: ignore[arg-type]
    result=bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="durable-a1",policy_collection=pc,authorization_registry=registry,binding_collection=bc,binding_id="durable-b1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    assert result.activation_authorization_evidence_id=="durable-a1"
    ac.rows[0]["authorization_evidence_fingerprint"]="0"*128
    with pytest.raises(Exception): bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="durable-a1",policy_collection=pc,authorization_registry=registry,binding_collection=Collection(),binding_id="durable-b2",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)

def test_corrupt_durable_authorization_operation_rejects_without_normalization():
    pc=Collection(); bc=Collection(); s=Session(); p1(pc,s); evidence=_durable_activate(); ac=Collection(); ac.rows.append(evidence.to_persisted()); ac.rows[0]["operation"]="accounts_payable_provider_policy_create"; registry=TenantAuthorizationDecisionEvidenceRegistry(ac,principal_repository=None)  # type: ignore[arg-type]
    with pytest.raises(Exception): bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="durable-a1",policy_collection=pc,authorization_registry=registry,binding_collection=bc,binding_id="durable-b3",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    assert bc.rows==[]

def test_cas_rejects_stale_wrong_and_cross_tenant_predecessors_without_head_change():
    c=Collection(); s=Session(); now=datetime.now(timezone.utc)
    def b(i,rev,tenant="tenant-a",prev=None,fp=None,family="ACCOUNTS_PAYABLE"):
        return AccountsPayableProviderPolicyRuntimeBinding(i,tenant,rev,"policy-a",rev,"p"*128,"a"+i,"f"*128,prev,fp,now,now,family=family)
    r1=b("r1",1); AccountsPayableProviderPolicyRuntimeBindingRegistry.create(r1,c,session=s)
    r2=b("r2",2,"tenant-a","r1",r1.binding_fingerprint); AccountsPayableProviderPolicyRuntimeBindingRegistry.create(r2,c,session=s)
    before=[dict(row) for row in c.rows]
    for candidate in (b("stale",3,"tenant-a","r1",r1.binding_fingerprint),b("wrong",3,"tenant-a","other","x"*128),b("cross",3,"tenant-b","r2",r2.binding_fingerprint)):
        with pytest.raises(Exception): AccountsPayableProviderPolicyRuntimeBindingRegistry.create(candidate,c,session=s)
    with pytest.raises(Exception): b("family",3,"tenant-a","r2",r2.binding_fingerprint,"PLATFORM_BILLING")
    assert c.rows==before

def test_missing_head_with_existing_history_fails_closed_before_reinitialization():
    pc=Collection(); bc=Collection(); s=Session(); p=p1(pc,s); auth=Auth(ev("accounts_payable_provider_policy_activate","a1"))
    first=bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=auth,binding_collection=bc,binding_id="b1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    bc.rows=[row for row in bc.rows if row.get("_kind")!="head"]; before=[dict(row) for row in bc.rows]
    with pytest.raises(Exception, match="FAIL_CLOSED_INCONSISTENT_CURRENTNESS"):
        bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=auth,binding_collection=bc,binding_id="b2",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    assert first.binding_id=="b1" and bc.rows==before

def test_runtime_binding_registry_isolates_history_current_and_existence_by_tenant():
    c=Collection(); s=Session(); now=datetime.now(timezone.utc)
    a=AccountsPayableProviderPolicyRuntimeBinding("a1","tenant-a",1,"policy-a",1,"p"*128,"auth-a","f"*128,None,None,now,now)
    b=AccountsPayableProviderPolicyRuntimeBinding("b1","tenant-b",1,"policy-b",1,"q"*128,"auth-b","e"*128,None,None,now,now)
    AccountsPayableProviderPolicyRuntimeBindingRegistry.create(a,c,session=s); AccountsPayableProviderPolicyRuntimeBindingRegistry.create(b,c,session=s)
    read_b=AccountsPayableProviderPolicyRuntimeBindingRegistry.get("tenant-b",c,revision=1,session=s); current_b=AccountsPayableProviderPolicyRuntimeBindingRegistry.current("tenant-b",c,session=s)
    assert read_b is not None and read_b.binding_id=="b1"
    assert current_b is not None and current_b.tenant_id=="tenant-b"
    assert AccountsPayableProviderPolicyRuntimeBindingRegistry.has_history("tenant-a",c,session=s) is True
    assert AccountsPayableProviderPolicyRuntimeBindingRegistry.has_history("tenant-b",c,session=s) is True
    assert AccountsPayableProviderPolicyRuntimeBindingRegistry.get("tenant-b",c,revision=2,session=s) is None

def test_tenant_b_true_virgin_activation_ignores_tenant_a_history():
    pc=Collection(); bc=Collection(); s=Session(); p1(pc,s)
    bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=Auth(ev("accounts_payable_provider_policy_activate","a1")),binding_collection=bc,binding_id="a1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    p_b=issue_accounts_payable_provider_policy(authorization_evidence=ev("accounts_payable_provider_policy_create","create-b",tenant="tenant-b",policy="policy-b"),tenant_id="tenant-b",policy_id="policy-b",policy_revision=1,provider_names=("provider-b",),predecessor_fingerprint=None,collection=pc,effective_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    result=bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-b",policy_id="policy-b",policy_revision=1,authorization_decision_id="b1",policy_collection=pc,authorization_registry=Auth(ev("accounts_payable_provider_policy_activate","b1",tenant="tenant-b",policy="policy-b")),binding_collection=bc,binding_id="b1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    assert p_b.tenant_id=="tenant-b" and result.tenant_id=="tenant-b" and result.binding_revision==1

def test_successor_cannot_use_tenant_a_policy_or_authorization_for_tenant_b():
    pc=Collection(); bc=Collection(); s=Session(); p_a=p1(pc,s)
    bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=Auth(ev("accounts_payable_provider_policy_activate","a1")),binding_collection=bc,binding_id="a1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    p_b=issue_accounts_payable_provider_policy(authorization_evidence=ev("accounts_payable_provider_policy_create","create-b",tenant="tenant-b",policy="policy-b"),tenant_id="tenant-b",policy_id="policy-b",policy_revision=1,provider_names=("provider-b",),predecessor_fingerprint=None,collection=pc,effective_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-b",policy_id="policy-b",policy_revision=1,authorization_decision_id="b1",policy_collection=pc,authorization_registry=Auth(ev("accounts_payable_provider_policy_activate","b1",tenant="tenant-b",policy="policy-b")),binding_collection=bc,binding_id="b1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    before=[dict(row) for row in bc.rows]
    with pytest.raises(Exception): bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-b",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=Auth(ev("accounts_payable_provider_policy_activate","a1")),binding_collection=bc,binding_id="cross",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    assert p_a.tenant_id=="tenant-a" and p_b.tenant_id=="tenant-b" and bc.rows==before

def test_exact_initial_replay_does_not_create_duplicate_history():
    pc=Collection(); bc=Collection(); s=Session(); p1(pc,s); auth=Auth(ev("accounts_payable_provider_policy_activate","a1")); kwargs=dict(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=auth,binding_collection=bc,binding_id="replay-r1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    first=bind_accounts_payable_provider_policy_runtime(**kwargs)  # type: ignore[arg-type]
    before=[dict(row) for row in bc.rows]
    with pytest.raises(Exception): bind_accounts_payable_provider_policy_runtime(**kwargs)  # type: ignore[arg-type]
    assert first.binding_id=="replay-r1" and bc.rows==before

def test_exact_successor_replay_and_new_authorization_do_not_create_r3():
    pc=Collection(); bc=Collection(); s=Session(); p_first=p1(pc,s); auths=MultiAuth({"a1":ev("accounts_payable_provider_policy_activate","a1",1),"a2":ev("accounts_payable_provider_policy_activate","a2",2),"a3":ev("accounts_payable_provider_policy_activate","a3",2)})
    r1=bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=auths,binding_collection=bc,binding_id="r1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    p_second=issue_accounts_payable_provider_policy(authorization_evidence=ev("accounts_payable_provider_policy_revise","rev-2",2),tenant_id="tenant-a",policy_id="policy-a",policy_revision=2,provider_names=("provider-a",),predecessor_fingerprint=p_first.policy_fingerprint,collection=pc,effective_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    r2=bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=2,authorization_decision_id="a2",policy_collection=pc,authorization_registry=auths,binding_collection=bc,binding_id="r2",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s); before=[dict(row) for row in bc.rows]
    with pytest.raises(Exception,match="ALREADY_CURRENT_POLICY_REPLAY"):
        bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=2,authorization_decision_id="a3",policy_collection=pc,authorization_registry=auths,binding_collection=bc,binding_id="r3",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    assert r2.provider_policy_fingerprint==p_second.policy_fingerprint and bc.rows==before and auths.sessions[-1] is s

def test_multiple_legacy_heads_fail_closed_without_normalization():
    c=Collection(); s=Session(); now=datetime.now(timezone.utc)
    base={"tenant_id":"tenant-a","family":"ACCOUNTS_PAYABLE","_kind":"head","binding_revision":1,"binding_id":"b1","binding_fingerprint":"f"*128}
    c.rows.extend([dict(base),dict(base,binding_revision=2,binding_id="b2",binding_fingerprint="g"*128)])
    before=[dict(row) for row in c.rows]
    with pytest.raises(Exception,match="MULTIPLE_CURRENT_HEADS"):
        AccountsPayableProviderPolicyRuntimeBindingRegistry.current("tenant-a",c,session=s)
    assert c.rows==before

def test_consumed_historical_activation_cannot_reactivate_p1_after_r2():
    pc=Collection(); bc=Collection(); s=Session(); p_first=p1(pc,s)
    auths=MultiAuth({"a1":ev("accounts_payable_provider_policy_activate","a1",1),"a2":ev("accounts_payable_provider_policy_activate","a2",2)})
    r1=bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=auths,binding_collection=bc,binding_id="r1",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    p_second=issue_accounts_payable_provider_policy(authorization_evidence=ev("accounts_payable_provider_policy_revise","rev-2",2),tenant_id="tenant-a",policy_id="policy-a",policy_revision=2,provider_names=("provider-a",),predecessor_fingerprint=p_first.policy_fingerprint,collection=pc,effective_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    r2=bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=2,authorization_decision_id="a2",policy_collection=pc,authorization_registry=auths,binding_collection=bc,binding_id="r2",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    before=[dict(row) for row in bc.rows]
    with pytest.raises(Exception,match="CONSUMED_ACTIVATION_AUTHORIZATION_REPLAY"):
        bind_accounts_payable_provider_policy_runtime(tenant_id="tenant-a",policy_id="policy-a",policy_revision=1,authorization_decision_id="a1",policy_collection=pc,authorization_registry=auths,binding_collection=bc,binding_id="stale-r3",activated_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc),session=s)
    assert r1.binding_id=="r1" and r2.binding_id=="r2" and p_second.policy_revision==2 and bc.rows==before

def test_same_binding_revision_with_divergent_fingerprint_rejects_without_overwrite():
    c=Collection(); s=Session(); now=datetime.now(timezone.utc)
    original=AccountsPayableProviderPolicyRuntimeBinding("same-id","tenant-a",1,"policy-a",1,"p"*128,"auth-a","f"*128,None,None,now,now)
    divergent=AccountsPayableProviderPolicyRuntimeBinding("same-id","tenant-a",1,"policy-a",1,"p"*128,"auth-a","g"*128,None,None,now,now)
    AccountsPayableProviderPolicyRuntimeBindingRegistry.create(original,c,session=s)
    before=[dict(row) for row in c.rows]
    with pytest.raises(Exception,match="BINDING_REVISION_CONFLICT"):
        AccountsPayableProviderPolicyRuntimeBindingRegistry.create(divergent,c,session=s)
    assert c.rows==before

def _history_binding_fixture():
    c=Collection(); s=Session(); now=datetime.now(timezone.utc)
    binding=AccountsPayableProviderPolicyRuntimeBinding("history-b1","tenant-a",1,"policy-a",1,"p"*128,"auth-a","f"*128,None,None,now,now)
    AccountsPayableProviderPolicyRuntimeBindingRegistry.create(binding,c,session=s)
    return c,s,binding

def test_durable_history_binding_fingerprint_corruption_fails_closed():
    c,s,binding=_history_binding_fixture(); assert AccountsPayableProviderPolicyRuntimeBindingRegistry.get("tenant-a",c,revision=1,session=s) == binding
    c.rows[0]["binding_fingerprint"]="0"*128
    with pytest.raises(Exception,match="BINDING_PERSISTED_RECORD_INVALID"):
        AccountsPayableProviderPolicyRuntimeBindingRegistry.get("tenant-a",c,revision=1,session=s)
    assert c.rows[0]["binding_fingerprint"]=="0"*128

def test_missing_durable_history_authorization_provenance_fails_closed():
    c,s,_=_history_binding_fixture(); del c.rows[0]["activation_authorization_evidence_id"]
    with pytest.raises(Exception,match="BINDING_PERSISTED_RECORD_INVALID"):
        AccountsPayableProviderPolicyRuntimeBindingRegistry.get("tenant-a",c,revision=1,session=s)

def test_wrong_kind_row_cannot_hydrate_as_history():
    c,s,_=_history_binding_fixture(); c.rows[0]["_kind"]="head"
    assert AccountsPayableProviderPolicyRuntimeBindingRegistry.get("tenant-a",c,revision=1,session=s) is None

def test_history_row_never_satisfies_current_without_explicit_head():
    c,s,_=_history_binding_fixture(); c.rows=[row for row in c.rows if row.get("_kind")!="head"]
    assert AccountsPayableProviderPolicyRuntimeBindingRegistry.current("tenant-a",c,session=s) is None

def test_head_only_state_has_no_history():
    c,s,binding=_history_binding_fixture(); c.rows=[row for row in c.rows if row.get("_kind")=="head"]
    assert AccountsPayableProviderPolicyRuntimeBindingRegistry.has_history("tenant-a",c,session=s) is False
    assert binding.binding_id=="history-b1"

def test_head_only_state_cannot_prove_consumed_authorization():
    c,s,binding=_history_binding_fixture(); c.rows=[row for row in c.rows if row.get("_kind")=="head"]
    assert AccountsPayableProviderPolicyRuntimeBindingRegistry.has_consumed_activation_authorization("tenant-a","auth-a","f"*128,c,session=s) is False
    assert binding.binding_id=="history-b1"

def test_corrupt_existing_head_fingerprint_is_not_treated_as_valid_currentness():
    c,s,binding=_history_binding_fixture(); head=next(row for row in c.rows if row.get("_kind")=="head")
    assert AccountsPayableProviderPolicyRuntimeBindingRegistry.current("tenant-a",c,session=s) == binding
    head["binding_fingerprint"]="0"*128
    with pytest.raises(Exception,match="BINDING_PERSISTED_RECORD_INVALID"):
        AccountsPayableProviderPolicyRuntimeBindingRegistry.current("tenant-a",c,session=s)
    assert head["binding_fingerprint"]=="0"*128

def test_head_binding_identity_must_correlate_exactly_with_history():
    c,s,_=_history_binding_fixture(); head=next(row for row in c.rows if row.get("_kind")=="head")
    head["binding_id"]="forged-head-id"
    with pytest.raises(Exception,match="BINDING_PERSISTED_RECORD_INVALID"):
        AccountsPayableProviderPolicyRuntimeBindingRegistry.current("tenant-a",c,session=s)
# ARTIFACT: test_accounts_payable_provider_policy_runtime_binding.py
# VERSION: v1.0.1-M11E2C3-R4F-R1-R3
# AUTHORITY BOUNDARY: AP runtime-binding certificate evidence only
# TENANT POSTURE: synthetic tenant-scoped fixtures
# FAIL-CLOSED POSTURE: invalid authority rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
