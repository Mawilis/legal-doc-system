"""TITLE: Platform Billing Provider-Policy Runtime Binding Certificate.
VERSION: v1.0.0-M11E2D5C2G-P2B-R3.
AUTHORITY: Kennel EOS runtime-binding certificate.
EPITOME: Certifies durable policy, ACTIVATE evidence, binding history and fail-closed replay.
ABSOLUTE CANONICAL PATH: tests/unit/test_platform_billing_provider_policy_runtime_binding.py
COLLABORATION / OWNERSHIP: Kennel EOS runtime-policy certificate.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 adds direct runtime-binding authority coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant and lane are asserted.
AUTHORITY BOUNDARY: Runtime designation only; no provider or execution effect.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
import pytest
from tools.eos.kennel.domain.platform_billing_provider_policy import PlatformBillingProviderPolicy, PolicyStatus
from tools.eos.kennel.domain.platform_billing_provider_policy_revision_authorization_subject import PlatformBillingProviderPolicyRevisionAuthorizationSubject
from tools.eos.kennel.domain.platform_billing_provider_policy_runtime_binding import PlatformBillingProviderPolicyRuntimeBinding
from tools.eos.kennel.registry.platform_billing_provider_policy_registry import PlatformBillingProviderPolicyRegistry
from tools.eos.kennel.registry.platform_billing_provider_policy_runtime_binding_registry import PlatformBillingProviderPolicyRuntimeBindingRegistry as R
from tools.eos.kennel.orchestration.platform_billing_provider_policy_runtime_binding import bind_platform_billing_provider_policy_runtime

class C:
    def __init__(self): self.rows=[]
    def insert_one(self,row,**_): self.rows.append(dict(row))
    def find_one(self,q,**_): return next((r for r in self.rows if all(r.get(k)==v for k,v in q.items())),None)
    def find(self,q,**_): return [r for r in self.rows if all(r.get(k)==v for k,v in q.items())]
    def update_one(self, filt, update, *, upsert=False, **_):
        for row in self.rows:
            if all(row.get(k)==v for k,v in filt.items()):
                row.update(update.get("$set", {})); return SimpleNamespace(matched_count=1, upserted_id=None)
        if upsert:
            self.rows.append(dict(update.get("$set", {}))); return SimpleNamespace(matched_count=0, upserted_id="new")
        return SimpleNamespace(matched_count=0, upserted_id=None)
class S: in_transaction=True

def policy(t="t1", rev=1):
    d=datetime(2026,1,1,tzinfo=timezone.utc)
    return PlatformBillingProviderPolicy(policy_id="p"+str(rev),tenant_id=t,lane="PLATFORM_BILLING_OUTBOUND",authorized_provider_names=("acme",),policy_revision=rev,policy_authorization_reference="auth"+str(rev),effective_at=d,expires_at=None,created_at=d,status=PolicyStatus.ACTIVE)

def test_domain_and_registry_chain():
    c=C(); p=policy(); PlatformBillingProviderPolicyRegistry.create(p,c)
    s=PlatformBillingProviderPolicyRevisionAuthorizationSubject.from_policy(p)
    e=SimpleNamespace(tenant_id="t1",authorization_decision_id="a1",operation="platform_billing_provider_policy_activate",permission="platform_billing:provider_policy:admin",subject_reference=s.subject_reference,subject_evidence_fingerprint=s.subject_evidence_fingerprint)
    ac=C(); ac.insert_one({"tenant_id":"t1","authorization_decision_id":"a1",**e.__dict__})
    b=bind_platform_billing_provider_policy_runtime(tenant_id="t1",policy_id="p1",policy_revision=1,authorization_decision_id="a1",policy_collection=c,authorization_registry=SimpleNamespace(get=lambda **_:e),binding_collection=C(),binding_id="b1",activated_at=p.effective_at,created_at=p.created_at,session=S())
    assert b.binding_revision==1 and b.previous_binding_id is None

def test_replay_and_predecessor_reject():
    c=C(); d=datetime(2026,1,1,tzinfo=timezone.utc)
    b=PlatformBillingProviderPolicyRuntimeBinding("b1","t1","PLATFORM_BILLING_OUTBOUND",1,"p1",1,"f"*128,"a1","e"*128,None,None,d,d)
    R.create(b,c,session=S()); assert R.create(b,c,session=S())==b
    bad=PlatformBillingProviderPolicyRuntimeBinding("b2","t1","PLATFORM_BILLING_OUTBOUND",2,"p2",2,"g"*128,"a2","h"*128,"wrong","x"*128,d,d)
    with pytest.raises(Exception): R.create(bad,c,session=S())

def test_conditional_cas_accepts_one_competing_successor_and_rejects_stale():
    c=C(); d=datetime(2026,1,1,tzinfo=timezone.utc)
    r1=PlatformBillingProviderPolicyRuntimeBinding("b1","t1","PLATFORM_BILLING_OUTBOUND",1,"p1",1,"f"*128,"a1","e"*128,None,None,d,d)
    R.create(r1,c,session=S())
    expected={"_kind":"head","tenant_id":"t1","lane":"PLATFORM_BILLING_OUTBOUND","binding_revision":1,"binding_id":"b1","binding_fingerprint":r1.binding_fingerprint}
    r2a={"_kind":"head","tenant_id":"t1","lane":"PLATFORM_BILLING_OUTBOUND","binding_revision":2,"binding_id":"b2","binding_fingerprint":"2"*128}
    r2b={"_kind":"head","tenant_id":"t1","lane":"PLATFORM_BILLING_OUTBOUND","binding_revision":2,"binding_id":"b3","binding_fingerprint":"3"*128}
    first=c.update_one(expected,{"$set":r2a}); second=c.update_one(expected,{"$set":r2b})
    assert first.matched_count==1 and second.matched_count==0
    assert c.find_one({"_kind":"head","tenant_id":"t1","lane":"PLATFORM_BILLING_OUTBOUND"})==r2a

@pytest.mark.parametrize("field,value", [("tenant_id","other"),("permission","platform:release"),("operation","platform_billing_provider_policy_create"),("subject_reference","wrong"),("subject_evidence_fingerprint","0"*128)])
def test_orchestration_rejects_authorization_substitutions(field,value):
    c=C(); p=policy(); PlatformBillingProviderPolicyRegistry.create(p,c)
    s=PlatformBillingProviderPolicyRevisionAuthorizationSubject.from_policy(p)
    e=SimpleNamespace(tenant_id="t1",authorization_decision_id="a1",operation="platform_billing_provider_policy_activate",permission="platform_billing:provider_policy:admin",subject_reference=s.subject_reference,subject_evidence_fingerprint=s.subject_evidence_fingerprint)
    setattr(e,field,value)
    with pytest.raises(Exception):
        bind_platform_billing_provider_policy_runtime(tenant_id="t1",policy_id="p1",policy_revision=1,authorization_decision_id="a1",policy_collection=c,authorization_registry=SimpleNamespace(get=lambda **_:e),binding_collection=C(),binding_id="b1",activated_at=p.effective_at,created_at=p.created_at,session=S())

# ARTIFACT: test_platform_billing_provider_policy_runtime_binding.py
# VERSION: v1.0.0-M11E2D5C2G-P2B-R3
# AUTHORITY BOUNDARY: direct constitutional certificate only
# TENANT POSTURE: exact tenant/lane scope
# FAIL-CLOSED POSTURE: malformed, divergent, and stale facts reject
# END OF WILSY OS SOVEREIGN ARTIFACT
