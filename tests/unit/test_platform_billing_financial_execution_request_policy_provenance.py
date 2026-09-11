"""TITLE: Platform Execution Request Policy-Provenance Certificate.
VERSION: v1.0.0-M11E2C2G-P3-R5.
AUTHORITY: Wilsy OS Core Governance / Kennel EOS.
EPITOME: Cross-owner request provenance contract certificate.
ABSOLUTE CANONICAL PATH: tests/unit/test_platform_billing_financial_execution_request_policy_provenance.py
COLLABORATION / OWNERSHIP: SaaS request and Kennel runtime-binding owners.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes bounded cross-owner provenance assertions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Request and antecedents remain tenant scoped.
AUTHORITY BOUNDARY: Certificate only; no provider selection or execution.
"""
import inspect
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any
from tools.eos.kennel.domain.platform_billing_provider_policy import PlatformBillingProviderPolicy, PolicyStatus
from tools.eos.kennel.registry.platform_billing_provider_policy_registry import PlatformBillingProviderPolicyRegistry
from tools.eos.kennel.domain.platform_billing_provider_policy_revision_authorization_subject import PlatformBillingProviderPolicyRevisionAuthorizationSubject
from tools.eos.kennel.domain.platform_billing_provider_policy_runtime_binding import PlatformBillingProviderPolicyRuntimeBinding
from tools.eos.kennel.registry.platform_billing_provider_policy_runtime_binding_registry import PlatformBillingProviderPolicyRuntimeBindingRegistry
from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization
from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry
from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import PlatformBillingFinancialExecutionRequestRegistry
from dataclasses import fields, replace
from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest
from tools.eos.saas.billing.platform_billing_financial_execution_request_issuance import issue_platform_billing_financial_execution_request

def test_request_contains_all_immutable_policy_provenance_fields():
    names={field.name for field in fields(PlatformBillingFinancialExecutionRequest)}
    assert {"provider_policy_runtime_binding_id","provider_policy_runtime_binding_fingerprint","provider_policy_id","provider_policy_revision","provider_policy_fingerprint"} <= names

def test_issuance_requires_caller_session_and_resolves_current_binding():
    signature=inspect.signature(issue_platform_billing_financial_execution_request)
    assert "session" in signature.parameters
    source=inspect.getsource(issue_platform_billing_financial_execution_request)
    assert "PlatformBillingProviderPolicyRuntimeBindingRegistry.current" in source
    assert "PlatformBillingProviderPolicyRegistry.get" in source
    assert "start_session" not in source and "start_transaction" not in source

class _C:
    def __init__(self): self.rows=[]
    def with_options(self, **_: Any): return self
    def create_index(self,*_: Any,**__: Any): return "idx"
    def find_one(self,q,**_: Any): return next((r for r in self.rows if all(r.get(k)==v for k,v in q.items())),None)
    def insert_one(self,row,**_: Any): self.rows.append(dict(row))
    def find(self,q,**_: Any): return [r for r in self.rows if all(r.get(k)==v for k,v in q.items())]
    def update_one(self,f,u,*,upsert=False,**_: Any):
        for r in self.rows:
            if all(r.get(k)==v for k,v in f.items()): r.update(u["$set"]); return SimpleNamespace(matched_count=1,upserted_id=None)
        if upsert: self.rows.append(dict(u["$set"])); return SimpleNamespace(matched_count=0,upserted_id="new")
        return SimpleNamespace(matched_count=0,upserted_id=None)
class _S: in_transaction=True
class _DB(dict):
    def __getitem__(self,k): return dict.setdefault(self,k,_C())

def test_canonical_r1_request_a_provenance_chain():
    from tools.eos.saas.billing.platform_billing_financial_execution_request_issuance import issue_platform_billing_financial_execution_request
    db=_DB(); s=_S(); now=datetime(2026,1,1,tzinfo=timezone.utc); policy=PlatformBillingProviderPolicy("p1","t1","PLATFORM_BILLING_OUTBOUND",("acme",),1,"auth",now,None,now,PolicyStatus.ACTIVE)
    PlatformBillingProviderPolicyRegistry.create(policy,db["platform_billing_provider_policies"],session= s)  # type: ignore[arg-type]
    subject=PlatformBillingProviderPolicyRevisionAuthorizationSubject.from_policy(policy)
    evidence=SimpleNamespace(tenant_id="t1",authorization_decision_id="act1",operation="platform_billing_provider_policy_activate",permission="platform_billing:provider_policy:admin",subject_reference=subject.subject_reference,subject_evidence_fingerprint=subject.subject_evidence_fingerprint)
    binding=PlatformBillingProviderPolicyRuntimeBinding("b1","t1",policy.lane,1,"p1",1,policy.policy_fingerprint,"act1",subject.subject_evidence_fingerprint,None,None,now,now)
    PlatformBillingProviderPolicyRuntimeBindingRegistry.create(binding,db["platform_billing_provider_policy_runtime_bindings"],session=s)
    invoice=SimpleNamespace(invoice_id="i1",commercial_release_evidence_fingerprint="a"*128,release_amount_minor=100,currency="ZAR")
    auth=PlatformBillingReleaseAuthorization("t1","rel1","i1","a"*128,"e","b"*128,100,"ZAR","principal","basis","dest","idem",now,now)
    PlatformBillingReleaseAuthorizationRegistry.create(auth,db["platform_billing_release_authorizations"],session=s)  # type: ignore[arg-type]
    request,_=issue_platform_billing_financial_execution_request(None,db,"t1","rel1",execution_request_id="req1",requested_at=now,session=s)  # type: ignore[arg-type]
    readback=PlatformBillingFinancialExecutionRequestRegistry.get("t1","req1",db["platform_billing_financial_execution_requests"],session=s)  # type: ignore[arg-type]
    assert readback.provider_policy_runtime_binding_id=="b1" and readback.provider_policy_id=="p1"
    requests=db["platform_billing_financial_execution_requests"]
    replay,_=PlatformBillingFinancialExecutionRequestRegistry.create(request,requests,session=s)  # type: ignore[arg-type]
    assert replay.fingerprint==request.fingerprint and len(requests.rows)==1
    for field, value in (("provider_policy_runtime_binding_id","b2"),("provider_policy_runtime_binding_fingerprint","d"*128),("provider_policy_id","p2"),("provider_policy_revision",2),("provider_policy_fingerprint","e"*128),("release_authorization_id","rel2")):
        divergent=replace(request,**{field:value})
        try: PlatformBillingFinancialExecutionRequestRegistry.create(divergent,requests,session=s)  # type: ignore[arg-type]
        except Exception: pass
        else: raise AssertionError(f"divergent replay {field} was accepted")
    assert PlatformBillingFinancialExecutionRequestRegistry.get("t1","req1",requests,session=s).provider_policy_id=="p1"  # type: ignore[arg-type]
    canonical_row=dict(requests.rows[0])
    for field, value in (("provider_policy_runtime_binding_id","b2"),("provider_policy_runtime_binding_fingerprint","d"*128),("provider_policy_id","p2"),("provider_policy_revision",2),("provider_policy_fingerprint","e"*128),("release_authorization_id","rel2"),("platform_invoice_id","i2")):
        requests.rows[0]={**canonical_row,field:value}
        try: PlatformBillingFinancialExecutionRequestRegistry.get("t1","req1",requests,session=s)  # type: ignore[arg-type]
        except Exception: pass
        else: raise AssertionError(f"durable corruption {field} was accepted")
    requests.rows[0]={**canonical_row,"unexpected":"x"}
    try: PlatformBillingFinancialExecutionRequestRegistry.get("t1","req1",requests,session=s)  # type: ignore[arg-type]
    except Exception: pass
    else: raise AssertionError("unexpected durable field was accepted")
    requests.rows[0]=canonical_row

def test_r1_to_r2_successor_request_provenance_and_history():
    from tools.eos.saas.billing.platform_billing_financial_execution_request_issuance import issue_platform_billing_financial_execution_request
    db=_DB(); s=_S(); now=datetime(2026,1,1,tzinfo=timezone.utc)
    p1=PlatformBillingProviderPolicy("p1","t1","PLATFORM_BILLING_OUTBOUND",("acme",),1,"auth1",now,None,now,PolicyStatus.ACTIVE); PlatformBillingProviderPolicyRegistry.create(p1,db["platform_billing_provider_policies"],session=s)  # type: ignore[arg-type]
    sub1=PlatformBillingProviderPolicyRevisionAuthorizationSubject.from_policy(p1); e1=SimpleNamespace(tenant_id="t1",authorization_decision_id="a1",operation="platform_billing_provider_policy_activate",permission="platform_billing:provider_policy:admin",subject_reference=sub1.subject_reference,subject_evidence_fingerprint=sub1.subject_evidence_fingerprint)
    b1=PlatformBillingProviderPolicyRuntimeBinding("b1","t1",p1.lane,1,p1.policy_id,1,p1.policy_fingerprint,"a1",sub1.subject_evidence_fingerprint,None,None,now,now); bc=db["platform_billing_provider_policy_runtime_bindings"]; PlatformBillingProviderPolicyRuntimeBindingRegistry.create(b1,bc,session=s)
    rel1=PlatformBillingReleaseAuthorization("t1","rel1","i1","a"*128,"e","b"*128,100,"ZAR","principal","basis","dest","idem1",now,now); PlatformBillingReleaseAuthorizationRegistry.create(rel1,db["platform_billing_release_authorizations"],session=s)  # type: ignore[arg-type]
    a,_=issue_platform_billing_financial_execution_request(None,db,"t1","rel1",execution_request_id="req1",requested_at=now,session=s)  # type: ignore[arg-type]
    p2=PlatformBillingProviderPolicy("p2","t1",p1.lane,("acme",),1,"auth2",now,None,now,PolicyStatus.ACTIVE); PlatformBillingProviderPolicyRegistry.create(p2,db["platform_billing_provider_policies"],session=s)  # type: ignore[arg-type]
    sub2=PlatformBillingProviderPolicyRevisionAuthorizationSubject.from_policy(p2); e2=SimpleNamespace(tenant_id="t1",authorization_decision_id="a2",operation="platform_billing_provider_policy_activate",permission="platform_billing:provider_policy:admin",subject_reference=sub2.subject_reference,subject_evidence_fingerprint=sub2.subject_evidence_fingerprint)
    b2=PlatformBillingProviderPolicyRuntimeBinding("b2","t1",p2.lane,2,p2.policy_id,1,p2.policy_fingerprint,"a2",sub2.subject_evidence_fingerprint,"b1",b1.binding_fingerprint,now,now); PlatformBillingProviderPolicyRuntimeBindingRegistry.create(b2,bc,session=s)
    rel2=PlatformBillingReleaseAuthorization("t1","rel2","i2","a"*128,"e","b"*128,100,"ZAR","principal","basis","dest","idem2",now,now); PlatformBillingReleaseAuthorizationRegistry.create(rel2,db["platform_billing_release_authorizations"],session=s)  # type: ignore[arg-type]
    b,_=issue_platform_billing_financial_execution_request(None,db,"t1","rel2",execution_request_id="req2",requested_at=now,session=s)  # type: ignore[arg-type]
    assert (a.provider_policy_id,a.provider_policy_runtime_binding_id)==("p1","b1") and (b.provider_policy_id,b.provider_policy_runtime_binding_id)==("p2","b2")

def test_no_current_binding_fails_closed(monkeypatch):
    auth=SimpleNamespace(tenant_id="t1", release_authorization_id="rel", platform_invoice_id="i", release_authorization_fingerprint="a"*128, authorized_amount_minor=1, currency="ZAR", payment_destination_reference="opaque", idempotency_key="id", authorized_by_principal_id="p", authorization_basis_reference="b")
    monkeypatch.setattr(PlatformBillingReleaseAuthorizationRegistry, "get", staticmethod(lambda *args, **kwargs: auth))
    db=_DB(); s=_S(); now=datetime(2026,1,1,tzinfo=timezone.utc)
    try: issue_platform_billing_financial_execution_request(None,db,"t1","rel",execution_request_id="req",requested_at=now,session=s)  # type: ignore[arg-type]
    except RuntimeError as exc: assert str(exc) in {"BINDING_HEAD_LOOKUP_FAILED", "CURRENT_RUNTIME_BINDING_REQUIRED"}
    else: raise AssertionError("missing runtime binding was accepted")
    assert not db["platform_billing_financial_execution_requests"].rows

def test_request_registry_rejects_legacy_missing_provenance():
    row={"tenant_id":"t1","execution_request_id":"r","request_fingerprint":"0"*128}
    try: PlatformBillingFinancialExecutionRequestRegistry._hydrate(row)
    except Exception as exc: assert "INVALID" in str(exc)
    else: raise AssertionError("legacy request was hydrated")

def test_request_registry_rejects_durable_fingerprint_corruption():
    now=datetime(2026,1,1,tzinfo=timezone.utc)
    value=PlatformBillingFinancialExecutionRequest("r","t1","rel","i","a"*128,1,"ZAR","opaque","idem","principal","basis",now,"b1","b"*128,"p1",1,"c"*128)
    row={**value.__dict__,"request_fingerprint":"0"*128}
    try: PlatformBillingFinancialExecutionRequestRegistry._hydrate(row)
    except Exception as exc: assert "INVALID" in str(exc)
    else: raise AssertionError("corrupt request fingerprint was accepted")

def test_runtime_antecedent_corruption_fails_closed():
    now=datetime(2026,1,1,tzinfo=timezone.utc)
    p=PlatformBillingProviderPolicy("p1","t1","PLATFORM_BILLING_OUTBOUND",("acme",),1,"auth",now,None,now,PolicyStatus.ACTIVE)
    b=PlatformBillingProviderPolicyRuntimeBinding("b1","t1",p.lane,1,p.policy_id,1,p.policy_fingerprint,"a1","e"*128,None,None,now,now)
    for field, value in (("binding_id","wrong"),("binding_fingerprint","f"*128),("binding_revision",2)):
        c=_C(); history={**b.to_persisted(),"_kind":"binding"}; head={"_kind":"head","tenant_id":"t1","lane":p.lane,"binding_revision":b.binding_revision,"binding_id":b.binding_id,"binding_fingerprint":b.binding_fingerprint}; head[field]=value; c.rows.extend([head,history])
        try: PlatformBillingProviderPolicyRuntimeBindingRegistry.current("t1",p.lane,c,session=_S())
        except Exception: pass
        else: raise AssertionError(f"corrupt head {field} accepted")

def test_runtime_corruption_propagates_through_real_issuance(monkeypatch):
    now=datetime(2026,1,1,tzinfo=timezone.utc)
    auth=PlatformBillingReleaseAuthorization("t1","rel","i","a"*128,"e","b"*128,1,"ZAR","principal","basis","opaque","idem",now,now)
    monkeypatch.setattr(PlatformBillingReleaseAuthorizationRegistry,"get",staticmethod(lambda *a,**k: auth))
    def corrupt(*_a,**_k): raise RuntimeError("BINDING_HEAD_LOOKUP_FAILED")
    monkeypatch.setattr(PlatformBillingProviderPolicyRuntimeBindingRegistry,"current",staticmethod(corrupt))
    db=_DB()
    try: issue_platform_billing_financial_execution_request(None,db,"t1","rel",execution_request_id="corrupt",requested_at=now,session=_S())  # type: ignore[arg-type]
    except RuntimeError as exc: assert str(exc)=="BINDING_HEAD_LOOKUP_FAILED"
    else: raise AssertionError("runtime corruption was swallowed")
    assert not db["platform_billing_financial_execution_requests"].rows

def test_missing_bound_policy_fails_through_real_issuance(monkeypatch):
    now=datetime(2026,1,1,tzinfo=timezone.utc)
    auth=PlatformBillingReleaseAuthorization("t1","rel","i","a"*128,"e","b"*128,1,"ZAR","principal","basis","opaque","idem",now,now)
    binding=SimpleNamespace(binding_id="b1",binding_fingerprint="b"*128,provider_policy_id="p1",provider_policy_revision=1,provider_policy_fingerprint="c"*128)
    monkeypatch.setattr(PlatformBillingReleaseAuthorizationRegistry,"get",staticmethod(lambda *a,**k: auth))
    monkeypatch.setattr(PlatformBillingProviderPolicyRuntimeBindingRegistry,"current",staticmethod(lambda *a,**k: binding))
    monkeypatch.setattr(PlatformBillingProviderPolicyRegistry,"get",staticmethod(lambda *a,**k: None))
    db=_DB()
    try: issue_platform_billing_financial_execution_request(None,db,"t1","rel",execution_request_id="missing-policy",requested_at=now,session=_S())  # type: ignore[arg-type]
    except RuntimeError as exc: assert str(exc)=="BOUND_POLICY_INVALID"
    else: raise AssertionError("missing bound policy was accepted")
    assert not db["platform_billing_financial_execution_requests"].rows

def test_bound_policy_lookup_failure_propagates(monkeypatch):
    now=datetime(2026,1,1,tzinfo=timezone.utc)
    auth=PlatformBillingReleaseAuthorization("t1","rel","i","a"*128,"e","b"*128,1,"ZAR","principal","basis","opaque","idem",now,now)
    binding=SimpleNamespace(binding_id="b1",binding_fingerprint="b"*128,provider_policy_id="p1",provider_policy_revision=1,provider_policy_fingerprint="c"*128)
    monkeypatch.setattr(PlatformBillingReleaseAuthorizationRegistry,"get",staticmethod(lambda *a,**k: auth))
    monkeypatch.setattr(PlatformBillingProviderPolicyRuntimeBindingRegistry,"current",staticmethod(lambda *a,**k: binding))
    def fail(*_a,**_k): raise RuntimeError("POLICY_CORRUPT")
    monkeypatch.setattr(PlatformBillingProviderPolicyRegistry,"get",staticmethod(fail))
    try: issue_platform_billing_financial_execution_request(None,_DB(),"t1","rel",execution_request_id="corrupt-policy",requested_at=now,session=_S())  # type: ignore[arg-type]
    except RuntimeError as exc: assert str(exc)=="POLICY_CORRUPT"
    else: raise AssertionError("policy lookup failure was swallowed")

def test_corrupt_bound_policy_rejects_through_real_issuance(monkeypatch):
    now=datetime(2026,1,1,tzinfo=timezone.utc)
    auth=PlatformBillingReleaseAuthorization("t1","rel","i","a"*128,"e","b"*128,1,"ZAR","principal","basis","opaque","idem",now,now)
    policy=PlatformBillingProviderPolicy("p1","t1","PLATFORM_BILLING_OUTBOUND",("acme",),1,"auth",now,None,now,PolicyStatus.ACTIVE)
    binding=PlatformBillingProviderPolicyRuntimeBinding("b1","t1",policy.lane,1,"p1",1,policy.policy_fingerprint,"a1","e"*128,None,None,now,now)
    monkeypatch.setattr(PlatformBillingReleaseAuthorizationRegistry,"get",staticmethod(lambda *a,**k: auth))
    monkeypatch.setattr(PlatformBillingProviderPolicyRuntimeBindingRegistry,"current",staticmethod(lambda *a,**k: binding))
    corrupt=dict(policy.to_persisted()); corrupt["policy_fingerprint"]="0"*128
    monkeypatch.setattr(PlatformBillingProviderPolicyRegistry,"get",staticmethod(lambda *a,**k: PlatformBillingProviderPolicy(**{**corrupt, "authorized_provider_names":tuple(corrupt["authorized_provider_names"])})))
    try: issue_platform_billing_financial_execution_request(None,_DB(),"t1","rel",execution_request_id="corrupt-policy",requested_at=now,session=_S())  # type: ignore[arg-type]
    except Exception: pass
    else: raise AssertionError("corrupt policy was accepted")

def test_fingerprint_material_corruption_rejects_through_real_registry(monkeypatch):
    now=datetime(2026,1,1,tzinfo=timezone.utc)
    auth=PlatformBillingReleaseAuthorization("t1","rel","i","a"*128,"e","b"*128,1,"ZAR","principal","basis","opaque","idem",now,now)
    policy=PlatformBillingProviderPolicy("p1","t1","PLATFORM_BILLING_OUTBOUND",("acme",),1,"auth",now,None,now,PolicyStatus.ACTIVE)
    binding=PlatformBillingProviderPolicyRuntimeBinding("b1","t1",policy.lane,1,"p1",1,policy.policy_fingerprint,"a1","e"*128,None,None,now,now)
    stored=policy.to_persisted(); stored["authorized_provider_names"]=["other"]
    pc=_C(); pc.rows.append(stored)
    monkeypatch.setattr(PlatformBillingReleaseAuthorizationRegistry,"get",staticmethod(lambda *a,**k: auth))
    monkeypatch.setattr(PlatformBillingProviderPolicyRuntimeBindingRegistry,"current",staticmethod(lambda *a,**k: binding))
    original_get=PlatformBillingProviderPolicyRegistry.get
    monkeypatch.setattr(PlatformBillingProviderPolicyRegistry,"get",staticmethod(lambda tenant, pid, collection, **kw: original_get(tenant,pid,pc,revision=kw.get("revision"),session=kw.get("session"))))
    try: issue_platform_billing_financial_execution_request(None,_DB(),"t1","rel",execution_request_id="material-corruption",requested_at=now,session=_S())  # type: ignore[arg-type]
    except Exception: pass
    else: raise AssertionError("fingerprint-covered material corruption was accepted")

def test_release_authority_is_mandatory_and_fail_closed(monkeypatch):
    now=datetime(2026,1,1,tzinfo=timezone.utc)
    policy=PlatformBillingProviderPolicy("p1","t1","PLATFORM_BILLING_OUTBOUND",("acme",),1,"auth",now,None,now,PolicyStatus.ACTIVE)
    binding=PlatformBillingProviderPolicyRuntimeBinding("b1","t1",policy.lane,1,"p1",1,policy.policy_fingerprint,"a1","e"*128,None,None,now,now)
    monkeypatch.setattr(PlatformBillingReleaseAuthorizationRegistry,"get",staticmethod(lambda *a,**k: (_ for _ in ()).throw(RuntimeError("RELEASE_NOT_FOUND"))))
    monkeypatch.setattr(PlatformBillingProviderPolicyRuntimeBindingRegistry,"current",staticmethod(lambda *a,**k: binding))
    db=_DB()
    try: issue_platform_billing_financial_execution_request(None,db,"t1","missing-release",execution_request_id="no-release",requested_at=now,session=_S())  # type: ignore[arg-type]
    except RuntimeError as exc: assert str(exc)=="RELEASE_NOT_FOUND"
    else: raise AssertionError("missing release authority was accepted")
    assert not db["platform_billing_financial_execution_requests"].rows

def test_corrupt_release_authority_fails_through_real_issuance(monkeypatch):
    now=datetime(2026,1,1,tzinfo=timezone.utc)
    policy=PlatformBillingProviderPolicy("p1","t1","PLATFORM_BILLING_OUTBOUND",("acme",),1,"auth",now,None,now,PolicyStatus.ACTIVE)
    binding=PlatformBillingProviderPolicyRuntimeBinding("b1","t1",policy.lane,1,"p1",1,policy.policy_fingerprint,"a1","e"*128,None,None,now,now)
    monkeypatch.setattr(PlatformBillingReleaseAuthorizationRegistry,"get",staticmethod(lambda *a,**k: (_ for _ in ()).throw(RuntimeError("RELEASE_PERSISTED_RECORD_INVALID"))))
    monkeypatch.setattr(PlatformBillingProviderPolicyRuntimeBindingRegistry,"current",staticmethod(lambda *a,**k: binding))
    try: issue_platform_billing_financial_execution_request(None,_DB(),"t1","rel",execution_request_id="corrupt-release",requested_at=now,session=_S())  # type: ignore[arg-type]
    except RuntimeError as exc: assert str(exc)=="RELEASE_PERSISTED_RECORD_INVALID"
    else: raise AssertionError("corrupt release authority was accepted")

def test_binding_policy_id_mismatch_fails_before_request_persistence(monkeypatch):
    now=datetime(2026,1,1,tzinfo=timezone.utc)
    auth=PlatformBillingReleaseAuthorization("t1","rel","i","a"*128,"e","b"*128,1,"ZAR","principal","basis","opaque","idem",now,now)
    policy=PlatformBillingProviderPolicy("p1","t1","PLATFORM_BILLING_OUTBOUND",("acme",),1,"auth",now,None,now,PolicyStatus.ACTIVE)
    binding=PlatformBillingProviderPolicyRuntimeBinding("b1","t1",policy.lane,1,"other",1,policy.policy_fingerprint,"a1","e"*128,None,None,now,now)
    monkeypatch.setattr(PlatformBillingReleaseAuthorizationRegistry,"get",staticmethod(lambda *a,**k: auth))
    monkeypatch.setattr(PlatformBillingProviderPolicyRuntimeBindingRegistry,"current",staticmethod(lambda *a,**k: binding))
    monkeypatch.setattr(PlatformBillingProviderPolicyRegistry,"get",staticmethod(lambda *a,**k: policy))
    db=_DB()
    try: issue_platform_billing_financial_execution_request(None,db,"t1","rel",execution_request_id="req-id-mismatch",requested_at=now,session=_S())  # type: ignore[arg-type]
    except RuntimeError as exc: assert str(exc)=="BOUND_POLICY_INVALID"
    else: raise AssertionError("policy ID mismatch was accepted")
    assert not db["platform_billing_financial_execution_requests"].rows


# ARTIFACT: test_platform_billing_financial_execution_request_policy_provenance.py
# VERSION: v1.0.0-M11E2C2G-P3-R5
# AUTHORITY BOUNDARY: direct certificate only
# TENANT POSTURE: exact tenant-scoped provenance
# FAIL-CLOSED POSTURE: missing authority is rejected by production boundaries
# END OF WILSY OS SOVEREIGN ARTIFACT
