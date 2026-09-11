"""TITLE: Platform Billing Provider Routing Certificate.
VERSION: v1.1.0-M11E2D5C2G-P5-R2C.
AUTHORITY: Kennel EOS / Wilsy OS Core Governance.
EPITOME: Direct certificate for historical-policy provider selection.
ABSOLUTE CANONICAL PATH: tests/unit/test_platform_billing_provider_routing_decision.py
COLLABORATION / OWNERSHIP: Kennel routing owners.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.1.0-M11E2D5C2G-P5-R2C adds request-level cardinality, lookup, replay, and race certificates.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic tenant-scoped fixtures; no credentials or provider transport data.
TENANT BOUNDARY: Exact tenant request/policy routing.
AUTHORITY BOUNDARY: Certificate only; no execution.
FINANCIAL AUTHORITY BOUNDARY: Tests do not issue commands, attempts, execution truth, or settlement.
"""
# pyright: reportArgumentType=false
from tools.eos.kennel.domain.platform_billing_provider_routing_decision import PlatformBillingProviderRoutingDecision
from tools.eos.kennel.registry.platform_billing_provider_routing_decision_registry import PlatformBillingProviderRoutingDecisionRegistry
from datetime import datetime, timezone
from types import SimpleNamespace
from pymongo.errors import DuplicateKeyError
class C:
    def __init__(self): self.rows=[]; self.index_calls=[]; self.find_calls=[]; self.find_one_calls=[]
    def with_options(self, **_): return self
    def create_index(self, keys, **kwargs): self.index_calls.append((keys, kwargs)); return "idx"
    def find_one(self,q,**kwargs): self.find_one_calls.append((q, kwargs)); return next((r for r in self.rows if all(r.get(k)==v for k,v in q.items())),None)
    def find(self,q,**kwargs):
        self.find_calls.append((q, kwargs))
        rows=[r for r in self.rows if all(r.get(k)==v for k,v in q.items())]
        class Cursor:
            def __init__(self, values): self.values=values
            def limit(self, amount): return Cursor(self.values[:amount])
            def __iter__(self): return iter(self.values)
        return Cursor(rows)
    def insert_one(self,r,**_): self.rows.append(dict(r))
    def update_one(self,f,u,*,upsert=False,**_):
        for r in self.rows:
            if all(r.get(k)==v for k,v in f.items()): r.update(u["$set"]); return SimpleNamespace(matched_count=1,upserted_id=None)
        if upsert: self.rows.append(dict(u["$set"])); return SimpleNamespace(matched_count=0,upserted_id="new")
        return SimpleNamespace(matched_count=0,upserted_id=None)
def test_routing_decision_identity_and_replay():
    c=C(); now=datetime(2026,1,1,tzinfo=timezone.utc); d=PlatformBillingProviderRoutingDecision("t1","rd1","req1","a"*128,"p1",1,"b"*128,"acme",now)
    _, replay=PlatformBillingProviderRoutingDecisionRegistry.create(d,c,session=object()); assert replay is False
    _, replay=PlatformBillingProviderRoutingDecisionRegistry.create(d,c,session=object()); assert replay is True
    assert PlatformBillingProviderRoutingDecisionRegistry.get("t1","rd1",c,session=object())==d
def test_corrupt_routing_decision_rejects():
    c=C(); now=datetime(2026,1,1,tzinfo=timezone.utc); d=PlatformBillingProviderRoutingDecision("t1","rd1","req1","a"*128,"p1",1,"b"*128,"acme",now); row=d.to_persisted(); row["selected_provider"]="evil"; c.rows.append(row)
    try: PlatformBillingProviderRoutingDecisionRegistry.get("t1","rd1",c,session=object())
    except RuntimeError as exc: assert str(exc)=="ROUTING_DECISION_PERSISTED_RECORD_INVALID"
    else: raise AssertionError("corrupt routing decision accepted")

def test_routing_requires_active_caller_transaction():
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    try: route_platform_billing_request("t1","req1","rd1",{},session=object())
    except RuntimeError as exc: assert str(exc)=="ACTIVE_TRANSACTION_REQUIRED"
    else: raise AssertionError("inactive transaction was accepted")

def test_routing_uses_request_historical_policy_and_tenant_scope(monkeypatch):
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest
    request=PlatformBillingFinancialExecutionRequest("req1","t1","rel","inv","a"*128,1,"ZAR","opaque","idem","principal","basis",datetime(2026,1,1,tzinfo=timezone.utc),"b1","b"*128,"p1",1,"c"*128)
    policy=SimpleNamespace(policy_id="p1",policy_revision=1,policy_fingerprint="c"*128,authorized_provider_names=("acme",))
    db={"platform_billing_financial_execution_requests":C(),"platform_billing_provider_policies":C(),"platform_billing_provider_routing_decisions":C()}
    db["platform_billing_financial_execution_requests"].rows.append({**request.__dict__,"request_fingerprint":request.fingerprint})
    monkeypatch.setattr("tools.eos.saas.billing.platform_billing_financial_execution_request_registry.PlatformBillingFinancialExecutionRequestRegistry.get",staticmethod(lambda *a,**k: request))
    monkeypatch.setattr("tools.eos.kennel.registry.platform_billing_provider_policy_registry.PlatformBillingProviderPolicyRegistry.get",staticmethod(lambda *a,**k: policy))
    decision,_=route_platform_billing_request("t1","req1","rd1",db,session=SimpleNamespace(in_transaction=True))
    assert decision.source_provider_policy_id=="p1" and decision.selected_provider=="acme"

def _decision(**changes):
    base=dict(tenant_id="t1",routing_decision_id="rd1",source_execution_request_id="req1",
              source_execution_request_fingerprint="a"*128,source_provider_policy_id="p1",
              source_provider_policy_revision=1,source_provider_policy_fingerprint="b"*128,
              selected_provider="acme",decided_at=datetime(2026,1,1,tzinfo=timezone.utc))
    base.update(changes); return PlatformBillingProviderRoutingDecision(**base)

def test_full_divergent_replay_matrix_is_fail_closed():
    c=C(); original=_decision(); PlatformBillingProviderRoutingDecisionRegistry.create(original,c,session=object())
    for field,value in (("selected_provider","other"),("source_execution_request_id","req2"),
                        ("source_execution_request_fingerprint","c"*128),("source_provider_policy_id","p2"),
                        ("source_provider_policy_revision",2),("source_provider_policy_fingerprint","d"*128)):
        try: PlatformBillingProviderRoutingDecisionRegistry.create(_decision(**{field:value}),c,session=object())
        except RuntimeError as exc: assert str(exc)=="ROUTING_DECISION_REPLAY_CONFLICT"
        else: raise AssertionError(field+" replay was accepted")
    assert len(c.rows)==1 and PlatformBillingProviderRoutingDecisionRegistry.get("t1","rd1",c,session=object())==original

def test_full_durable_corruption_matrix_is_fail_closed():
    fields=("selected_provider","source_execution_request_id","source_execution_request_fingerprint",
            "source_provider_policy_id","source_provider_policy_revision","source_provider_policy_fingerprint",
            "routing_decision_fingerprint")
    for field in fields:
        c=C(); row=_decision().to_persisted(); row[field] = ("corrupt" if field != "source_provider_policy_revision" else 99); c.rows.append(row)
        try: PlatformBillingProviderRoutingDecisionRegistry.get("t1","rd1",c,session=object())
        except RuntimeError as exc: assert str(exc)=="ROUTING_DECISION_PERSISTED_RECORD_INVALID"
        else: raise AssertionError(field+" corruption was normalized")

def test_routing_is_tenant_isolated_and_has_no_provider_execution(monkeypatch):
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest
    request=PlatformBillingFinancialExecutionRequest("req1","t1","rel","inv","a"*128,1,"ZAR","opaque","idem","principal","basis",datetime(2026,1,1,tzinfo=timezone.utc),"b1","b"*128,"p1",1,"c"*128)
    policy=SimpleNamespace(policy_id="p1",policy_revision=1,policy_fingerprint="c"*128,authorized_provider_names=("acme",))
    monkeypatch.setattr("tools.eos.saas.billing.platform_billing_financial_execution_request_registry.PlatformBillingFinancialExecutionRequestRegistry.get",staticmethod(lambda tenant,*a,**k: request if tenant=="t1" else None))
    monkeypatch.setattr("tools.eos.kennel.registry.platform_billing_provider_policy_registry.PlatformBillingProviderPolicyRegistry.get",staticmethod(lambda *a,**k: policy))
    db={"platform_billing_financial_execution_requests":C(),"platform_billing_provider_policies":C(),"platform_billing_provider_routing_decisions":C()}
    calls=[]; monkeypatch.setattr("tools.eos.kennel.orchestration.platform_billing_provider_routing.PlatformBillingProviderRoutingDecisionRegistry.create",staticmethod(lambda value,*a,**k: (calls.append(value),False)[1]))
    route_platform_billing_request("t1","req1","rd1",db,session=SimpleNamespace(in_transaction=True))
    assert len(calls)==1 and calls[0].selected_provider=="acme"
    assert PlatformBillingProviderRoutingDecisionRegistry.get("t2","rd1",db["platform_billing_provider_routing_decisions"],session=object()) is None

def test_request_source_unique_index_is_added_and_identity_is_preserved():
    c=C(); PlatformBillingProviderRoutingDecisionRegistry.ensure_indexes(c)
    assert len(c.index_calls)==2
    assert c.index_calls[0][0]==[("tenant_id",1),("routing_decision_id",1)]
    assert c.index_calls[0][1]["unique"] is True
    assert c.index_calls[1][0]==[("tenant_id",1),("source_execution_request_id",1)]
    assert c.index_calls[1][1]["unique"] is True

def test_get_by_request_is_exact_and_session_scoped():
    c=C(); value=_decision(); c.rows.append(value.to_persisted()); session=object()
    result=PlatformBillingProviderRoutingDecisionRegistry.get_by_request("t1","req1",c,session=session)
    assert result==value
    assert c.find_calls[-1][0]=={"tenant_id":"t1","source_execution_request_id":"req1"}
    assert c.find_calls[-1][1]["session"] is session

def test_get_by_request_zero_rows_is_canonical_absence():
    c=C(); assert PlatformBillingProviderRoutingDecisionRegistry.get_by_request("t1","missing",c,session=object()) is None

def test_get_by_request_does_not_cross_tenants():
    c=C(); c.rows.append(_decision().to_persisted())
    assert PlatformBillingProviderRoutingDecisionRegistry.get_by_request("t2","req1",c,session=object()) is None

def test_get_by_request_multiple_rows_rejects_without_selection():
    c=C(); c.rows.extend([_decision().to_persisted(),_decision(routing_decision_id="rd2").to_persisted()])
    try: PlatformBillingProviderRoutingDecisionRegistry.get_by_request("t1","req1",c,session=object())
    except RuntimeError as exc: assert str(exc)=="MULTIPLE_ROUTING_DECISIONS_FOR_REQUEST"
    else: raise AssertionError("multiple request decisions were selected")

def test_get_by_request_uses_canonical_strict_hydration():
    c=C(); row=_decision().to_persisted(); row["unknown"]="reject"; c.rows.append(row)
    try: PlatformBillingProviderRoutingDecisionRegistry.get_by_request("t1","req1",c,session=object())
    except RuntimeError as exc: assert str(exc)=="ROUTING_DECISION_PERSISTED_RECORD_INVALID"
    else: raise AssertionError("unknown persisted field was accepted")

def test_get_by_request_missing_required_field_rejects():
    c=C(); row=_decision().to_persisted(); row.pop("selected_provider"); c.rows.append(row)
    try: PlatformBillingProviderRoutingDecisionRegistry.get_by_request("t1","req1",c,session=object())
    except RuntimeError as exc: assert str(exc)=="ROUTING_DECISION_PERSISTED_RECORD_INVALID"
    else: raise AssertionError("missing persisted field was accepted")

def test_existing_request_decision_precedes_policy_lookup_and_persistence(monkeypatch):
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest
    request=PlatformBillingFinancialExecutionRequest("req1","t1","rel","inv","a"*128,1,"ZAR","opaque","idem","principal","basis",datetime(2026,1,1,tzinfo=timezone.utc),"b1","b"*128,"p1",1,"c"*128)
    c=C(); decision=_decision(source_execution_request_fingerprint=request.fingerprint,source_provider_policy_fingerprint=request.provider_policy_fingerprint); c.rows.append(decision.to_persisted())
    db={"platform_billing_financial_execution_requests":C(),"platform_billing_provider_policies":C(),"platform_billing_provider_routing_decisions":c}
    monkeypatch.setattr("tools.eos.saas.billing.platform_billing_financial_execution_request_registry.PlatformBillingFinancialExecutionRequestRegistry.get",staticmethod(lambda *a,**k: request))
    def fail_policy(*a,**k): raise AssertionError("policy was resolved on replay")
    monkeypatch.setattr("tools.eos.kennel.registry.platform_billing_provider_policy_registry.PlatformBillingProviderPolicyRegistry.get",staticmethod(fail_policy))
    result,replay=route_platform_billing_request("t1","req1","different-routing-id",db,session=SimpleNamespace(in_transaction=True))
    assert result==decision and replay is True and len(c.rows)==1

def test_existing_request_decision_correlation_matrix_rejects(monkeypatch):
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest
    request=PlatformBillingFinancialExecutionRequest("req1","t1","rel","inv","a"*128,1,"ZAR","opaque","idem","principal","basis",datetime(2026,1,1,tzinfo=timezone.utc),"b1","b"*128,"p1",1,"c"*128)
    for field,value in (("source_execution_request_fingerprint","d"*128),("source_provider_policy_id","p2"),("source_provider_policy_revision",2),("source_provider_policy_fingerprint","e"*128)):
        changes={"source_execution_request_fingerprint":request.fingerprint,"source_provider_policy_fingerprint":request.provider_policy_fingerprint}; changes[field]=value
        c=C(); c.rows.append(_decision(**changes).to_persisted()); db={"platform_billing_financial_execution_requests":C(),"platform_billing_provider_policies":C(),"platform_billing_provider_routing_decisions":c}
        db["platform_billing_financial_execution_requests"].rows.append({**request.__dict__,"request_fingerprint":request.fingerprint})
        monkeypatch.setattr("tools.eos.saas.billing.platform_billing_financial_execution_request_registry.PlatformBillingFinancialExecutionRequestRegistry.get",staticmethod(lambda *a,**k: request))
        try: route_platform_billing_request("t1","req1","rd-new",db,session=SimpleNamespace(in_transaction=True))
        except RuntimeError as exc: assert str(exc)=="ROUTING_DECISION_REQUEST_CORRELATION_INVALID"
        else: raise AssertionError(field+" mismatch was accepted")

def test_existing_decision_survives_later_policy_change(monkeypatch):
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest
    request=PlatformBillingFinancialExecutionRequest("req1","t1","rel","inv","a"*128,1,"ZAR","opaque","idem","principal","basis",datetime(2026,1,1,tzinfo=timezone.utc),"b1","b"*128,"p1",1,"c"*128)
    decision=_decision(source_execution_request_fingerprint=request.fingerprint,source_provider_policy_fingerprint=request.provider_policy_fingerprint); c=C(); c.rows.append(decision.to_persisted()); db={"platform_billing_financial_execution_requests":C(),"platform_billing_provider_policies":C(),"platform_billing_provider_routing_decisions":c}
    monkeypatch.setattr("tools.eos.saas.billing.platform_billing_financial_execution_request_registry.PlatformBillingFinancialExecutionRequestRegistry.get",staticmethod(lambda *a,**k: request))
    monkeypatch.setattr("tools.eos.kennel.registry.platform_billing_provider_policy_registry.PlatformBillingProviderPolicyRegistry.get",staticmethod(lambda *a,**k: SimpleNamespace(policy_fingerprint="d"*128)))
    result,_=route_platform_billing_request("t1","req1","rd-later",db,session=SimpleNamespace(in_transaction=True)); assert result==decision

def test_different_routing_id_after_existing_request_cannot_create_second(monkeypatch):
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest
    request=PlatformBillingFinancialExecutionRequest("req1","t1","rel","inv","a"*128,1,"ZAR","opaque","idem","principal","basis",datetime(2026,1,1,tzinfo=timezone.utc),"b1","b"*128,"p1",1,"c"*128)
    c=C(); c.rows.append(_decision(source_execution_request_fingerprint=request.fingerprint,source_provider_policy_fingerprint=request.provider_policy_fingerprint).to_persisted()); db={"platform_billing_financial_execution_requests":C(),"platform_billing_provider_policies":C(),"platform_billing_provider_routing_decisions":c}; monkeypatch.setattr("tools.eos.saas.billing.platform_billing_financial_execution_request_registry.PlatformBillingFinancialExecutionRequestRegistry.get",staticmethod(lambda *a,**k: request))
    result,replay=route_platform_billing_request("t1","req1","rd2",db,session=SimpleNamespace(in_transaction=True)); assert replay and len(c.rows)==1 and result.routing_decision_id=="rd1"

def test_source_request_conflict_is_not_failover():
    c=C(); first=_decision(); PlatformBillingProviderRoutingDecisionRegistry.create(first,c,session=object())
    with_conflict=_decision(routing_decision_id="rd2",selected_provider="stripe")
    try: PlatformBillingProviderRoutingDecisionRegistry.create(with_conflict,c,session=object())
    except RuntimeError as exc: assert str(exc)=="ROUTING_DECISION_SOURCE_REQUEST_CONFLICT"
    else: raise AssertionError("source conflict became failover")
    assert len(c.rows)==1

def test_same_source_request_same_tenant_different_routing_id_replays_only_exact_value():
    c=C(); first=_decision(); PlatformBillingProviderRoutingDecisionRegistry.create(first,c,session=object())
    try: PlatformBillingProviderRoutingDecisionRegistry.create(_decision(routing_decision_id="rd2"),c,session=object())
    except RuntimeError as exc: assert str(exc)=="ROUTING_DECISION_SOURCE_REQUEST_CONFLICT"
    else: raise AssertionError("different routing identity was treated as replay")

def test_same_request_id_different_tenants_is_independent():
    c=C(); a=_decision(); b=_decision(tenant_id="t2"); assert PlatformBillingProviderRoutingDecisionRegistry.create(a,c,session=object())[1] is False; assert PlatformBillingProviderRoutingDecisionRegistry.create(b,c,session=object())[1] is False; assert len(c.rows)==2

def test_duplicate_key_source_race_returns_exact_winner():
    from pymongo.errors import DuplicateKeyError
    class Race(C):
        def __init__(self): super().__init__(); self.first=True
        def insert_one(self,r,**kwargs):
            if self.first:
                self.first=False; self.rows.append(dict(r)); raise DuplicateKeyError("source race")
            super().insert_one(r,**kwargs)
    c=Race(); value=_decision(); result,replay=PlatformBillingProviderRoutingDecisionRegistry.create(value,c,session=object()); assert result==value and replay is True and len(c.rows)==1

def test_duplicate_key_source_race_rejects_divergent_winner():
    from pymongo.errors import DuplicateKeyError
    class Race(C):
        def insert_one(self,r,**kwargs): self.rows.append(_decision(selected_provider="winner").to_persisted()); raise DuplicateKeyError("source race")
    c=Race()
    try: PlatformBillingProviderRoutingDecisionRegistry.create(_decision(),c,session=object())
    except RuntimeError as exc: assert str(exc)=="ROUTING_DECISION_SOURCE_REQUEST_CONFLICT"
    else: raise AssertionError("divergent race winner accepted")
    assert len(c.rows)==1

def test_registry_never_selects_provider_or_generates_routing_id():
    import inspect
    source=inspect.getsource(PlatformBillingProviderRoutingDecisionRegistry)
    assert "authorized_provider_names" not in source and "datetime.now" not in source

def test_p4_surface_has_no_generic_command_or_attempt_authority():
    import inspect
    from tools.eos.kennel.orchestration import platform_billing_provider_routing as routing
    source=inspect.getsource(routing)
    assert "FinancialExecutionCommandRegistry" not in source and "issue_financial_execution_attempt" not in source

def test_p4_surface_has_no_ap_or_client_invoice_authority():
    import inspect
    from tools.eos.kennel.orchestration import platform_billing_provider_routing as routing
    source=inspect.getsource(routing)
    assert "AccountsPayable" not in source and "ClientInvoice" not in source and "payable_id" not in source

def test_platform_specific_command_is_not_consumed_by_p4():
    import inspect
    from tools.eos.kennel.orchestration import platform_billing_provider_routing as routing
    assert "PlatformBillingFinancialExecutionCommand" not in inspect.getsource(routing)

def test_routing_id_argument_is_preserved_and_not_derived():
    import inspect
    from tools.eos.kennel.orchestration import platform_billing_provider_routing as routing
    source=inspect.getsource(routing.route_platform_billing_request)
    assert "routing_decision_id" in inspect.signature(routing.route_platform_billing_request).parameters and "platform-command-" not in source and "hashlib" not in source

def test_request_source_lookup_does_not_select_first_or_latest():
    import inspect
    source=inspect.getsource(PlatformBillingProviderRoutingDecisionRegistry.get_by_request)
    assert ".sort(" not in source and "latest" not in source.lower() and "first" not in source.lower()

def test_p4_does_not_mutate_generic_registry_or_platform_specific_command():
    import inspect
    from tools.eos.kennel.registry import platform_billing_provider_routing_decision_registry as registry
    assert "FinancialExecutionCommandRegistry" not in inspect.getsource(registry)

def test_production_backed_historical_chain_routes_a_and_b_without_execution():
    from tools.eos.saas.billing.platform_billing_financial_execution_request_issuance import issue_platform_billing_financial_execution_request
    from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry
    from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization
    from tools.eos.kennel.domain.platform_billing_provider_policy import PlatformBillingProviderPolicy, PolicyStatus
    from tools.eos.kennel.domain.platform_billing_provider_policy_runtime_binding import PlatformBillingProviderPolicyRuntimeBinding
    from tools.eos.kennel.registry.platform_billing_provider_policy_registry import PlatformBillingProviderPolicyRegistry
    from tools.eos.kennel.registry.platform_billing_provider_policy_runtime_binding_registry import PlatformBillingProviderPolicyRuntimeBindingRegistry
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    now=datetime(2026,1,1,tzinfo=timezone.utc); db={k:C() for k in ("platform_billing_provider_policies","platform_billing_provider_policy_runtime_bindings","platform_billing_release_authorizations","platform_billing_financial_execution_requests","platform_billing_provider_routing_decisions")}; session=SimpleNamespace(in_transaction=True)
    p1=PlatformBillingProviderPolicy("p1","t1","PLATFORM_BILLING_OUTBOUND",("acme",),1,"auth1",now,None,now,PolicyStatus.ACTIVE); PlatformBillingProviderPolicyRegistry.create(p1,db["platform_billing_provider_policies"],session=session)
    r1=PlatformBillingProviderPolicyRuntimeBinding("r1","t1",p1.lane,1,p1.policy_id,1,p1.policy_fingerprint,"act1","e"*128,None,None,now,now); PlatformBillingProviderPolicyRuntimeBindingRegistry.create(r1,db["platform_billing_provider_policy_runtime_bindings"],session=session)
    a1=PlatformBillingReleaseAuthorization("t1","rel1","inv1","a"*128,"e","b"*128,100,"ZAR","principal","basis","opaque","idem1",now,now); PlatformBillingReleaseAuthorizationRegistry.create(a1,db["platform_billing_release_authorizations"],session=session)
    req_a,_=issue_platform_billing_financial_execution_request(None,db,"t1","rel1",execution_request_id="req-a",requested_at=now,session=session)
    p2=PlatformBillingProviderPolicy("p2","t1",p1.lane,("stripe",),2,"auth2",now,None,now,PolicyStatus.ACTIVE); PlatformBillingProviderPolicyRegistry.create(p2,db["platform_billing_provider_policies"],session=session)
    r2=PlatformBillingProviderPolicyRuntimeBinding("r2","t1",p2.lane,2,p2.policy_id,2,p2.policy_fingerprint,"act2","f"*128,r1.binding_id,r1.binding_fingerprint,now,now); PlatformBillingProviderPolicyRuntimeBindingRegistry.create(r2,db["platform_billing_provider_policy_runtime_bindings"],session=session)
    current = PlatformBillingProviderPolicyRuntimeBindingRegistry.current("t1",p2.lane,db["platform_billing_provider_policy_runtime_bindings"],session=session)
    assert current is not None and current.binding_id=="r2"
    a2=PlatformBillingReleaseAuthorization("t1","rel2","inv2","a"*128,"e","b"*128,100,"ZAR","principal","basis","opaque","idem2",now,now); PlatformBillingReleaseAuthorizationRegistry.create(a2,db["platform_billing_release_authorizations"],session=session)
    req_b,_=issue_platform_billing_financial_execution_request(None,db,"t1","rel2",execution_request_id="req-b",requested_at=now,session=session)
    decision_a,_=route_platform_billing_request("t1",req_a.execution_request_id,"rd-a",db,session=session); decision_b,_=route_platform_billing_request("t1",req_b.execution_request_id,"rd-b",db,session=session)
    assert (decision_a.source_provider_policy_id,decision_a.selected_provider)==("p1","acme")
    assert (decision_b.source_provider_policy_id,decision_b.selected_provider)==("p2","stripe")
    assert PlatformBillingProviderRoutingDecisionRegistry.get("t1","rd-a",db["platform_billing_provider_routing_decisions"],session=session)==decision_a
    assert PlatformBillingProviderRoutingDecisionRegistry.get("t1","rd-b",db["platform_billing_provider_routing_decisions"],session=session)==decision_b
    assert not db.get("platform_financial_execution_commands",C()).rows and not db.get("financial_execution_attempts",C()).rows

def test_registry_get_uses_exact_tenant_and_routing_identity():
    c=C(); c.rows.append(_decision().to_persisted()); session=object()
    assert PlatformBillingProviderRoutingDecisionRegistry.get("t1","rd1",c,session=session) is not None
    assert c.find_one_calls[-1][0]=={"tenant_id":"t1","routing_decision_id":"rd1"}
    assert c.find_one_calls[-1][1]["session"] is session

def test_registry_get_does_not_cross_tenant():
    c=C(); c.rows.append(_decision().to_persisted())
    assert PlatformBillingProviderRoutingDecisionRegistry.get("t2","rd1",c,session=object()) is None

def test_registry_create_rejects_non_domain_value():
    try: PlatformBillingProviderRoutingDecisionRegistry.create(object(),C(),session=object())
    except RuntimeError as exc: assert str(exc)=="ROUTING_DECISION_CREATE_INVALID"
    else: raise AssertionError("non-domain routing value accepted")

def test_registry_create_wraps_non_duplicate_persistence_failure():
    class Broken(C):
        def insert_one(self,r,**kwargs): raise OSError("storage unavailable")
    try: PlatformBillingProviderRoutingDecisionRegistry.create(_decision(),Broken(),session=object())
    except RuntimeError as exc: assert str(exc)=="ROUTING_DECISION_PERSISTENCE_FAILED"
    else: raise AssertionError("storage failure was swallowed")

def test_registry_get_by_request_fallback_find_one_is_exact():
    class FindOneOnly:
        def __init__(self,row): self.row=row; self.calls=[]
        def find_one(self,q,**kwargs): self.calls.append((q,kwargs)); return self.row
    collection=FindOneOnly(_decision().to_persisted()); session=object()
    assert PlatformBillingProviderRoutingDecisionRegistry.get_by_request("t1","req1",collection,session=session) is not None
    assert collection.calls[0][0]=={"tenant_id":"t1","source_execution_request_id":"req1"}

def test_registry_get_by_request_wraps_backend_failure():
    class Broken:
        def find(self,q,**kwargs): raise OSError("lookup unavailable")
    try: PlatformBillingProviderRoutingDecisionRegistry.get_by_request("t1","req1",Broken(),session=object())
    except RuntimeError as exc: assert str(exc)=="ROUTING_DECISION_REQUEST_LOOKUP_FAILED"
    else: raise AssertionError("lookup failure was swallowed")

def test_registry_request_lookup_rejects_routing_fingerprint_corruption():
    c=C(); row=_decision().to_persisted(); row["routing_decision_fingerprint"]="f"*128; c.rows.append(row)
    try: PlatformBillingProviderRoutingDecisionRegistry.get_by_request("t1","req1",c,session=object())
    except RuntimeError as exc: assert str(exc)=="ROUTING_DECISION_PERSISTED_RECORD_INVALID"
    else: raise AssertionError("fingerprint corruption accepted")

def test_route_rejects_missing_request_before_policy_lookup(monkeypatch):
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import PlatformBillingFinancialExecutionRequestRegistry
    monkeypatch.setattr(PlatformBillingFinancialExecutionRequestRegistry,"get",staticmethod(lambda *a,**k: (_ for _ in ()).throw(RuntimeError("REQUEST_MISSING"))))
    try: route_platform_billing_request("t1","missing","rd1",{"platform_billing_financial_execution_requests":C(),"platform_billing_provider_routing_decisions":C()},session=SimpleNamespace(in_transaction=True))
    except RuntimeError as exc: assert str(exc)=="REQUEST_MISSING"
    else: raise AssertionError("missing request was accepted")

def test_route_rejects_policy_fingerprint_mismatch(monkeypatch):
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest
    request=PlatformBillingFinancialExecutionRequest("req1","t1","rel","inv","a"*128,1,"ZAR","opaque","idem","principal","basis",datetime(2026,1,1,tzinfo=timezone.utc),"b1","b"*128,"p1",1,"c"*128)
    monkeypatch.setattr("tools.eos.saas.billing.platform_billing_financial_execution_request_registry.PlatformBillingFinancialExecutionRequestRegistry.get",staticmethod(lambda *a,**k: request))
    monkeypatch.setattr("tools.eos.kennel.registry.platform_billing_provider_policy_registry.PlatformBillingProviderPolicyRegistry.get",staticmethod(lambda *a,**k: SimpleNamespace(policy_id="p1",policy_revision=1,policy_fingerprint="d"*128,authorized_provider_names=("acme",))))
    db={"platform_billing_financial_execution_requests":C(),"platform_billing_provider_policies":C(),"platform_billing_provider_routing_decisions":C()}
    try: route_platform_billing_request("t1","req1","rd1",db,session=SimpleNamespace(in_transaction=True))
    except RuntimeError as exc: assert str(exc)=="ROUTING_BOUND_POLICY_INVALID"
    else: raise AssertionError("mismatched policy fingerprint accepted")

def test_route_rejects_ambiguous_policy(monkeypatch):
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest
    request=PlatformBillingFinancialExecutionRequest("req1","t1","rel","inv","a"*128,1,"ZAR","opaque","idem","principal","basis",datetime(2026,1,1,tzinfo=timezone.utc),"b1","b"*128,"p1",1,"c"*128)
    monkeypatch.setattr("tools.eos.saas.billing.platform_billing_financial_execution_request_registry.PlatformBillingFinancialExecutionRequestRegistry.get",staticmethod(lambda *a,**k: request))
    monkeypatch.setattr("tools.eos.kennel.registry.platform_billing_provider_policy_registry.PlatformBillingProviderPolicyRegistry.get",staticmethod(lambda *a,**k: SimpleNamespace(policy_id="p1",policy_revision=1,policy_fingerprint="c"*128,authorized_provider_names=("acme","stripe"))))
    db={"platform_billing_financial_execution_requests":C(),"platform_billing_provider_policies":C(),"platform_billing_provider_routing_decisions":C()}
    try: route_platform_billing_request("t1","req1","rd1",db,session=SimpleNamespace(in_transaction=True))
    except RuntimeError as exc: assert str(exc)=="ROUTING_PROVIDER_AMBIGUOUS"
    else: raise AssertionError("ambiguous policy selected a provider")

def test_route_active_transaction_requires_true_boolean():
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    try: route_platform_billing_request("t1","req1","rd1",{},session=SimpleNamespace(in_transaction=1))
    except RuntimeError as exc: assert str(exc)=="ACTIVE_TRANSACTION_REQUIRED"
    else: raise AssertionError("truthy non-boolean transaction accepted")

def test_route_existing_decision_ignores_caller_routing_id(monkeypatch):
    from tools.eos.kennel.orchestration.platform_billing_provider_routing import route_platform_billing_request
    from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest
    request=PlatformBillingFinancialExecutionRequest("req1","t1","rel","inv","a"*128,1,"ZAR","opaque","idem","principal","basis",datetime(2026,1,1,tzinfo=timezone.utc),"b1","b"*128,"p1",1,"c"*128)
    decision=_decision(source_execution_request_fingerprint=request.fingerprint,source_provider_policy_fingerprint=request.provider_policy_fingerprint); c=C(); c.rows.append(decision.to_persisted())
    monkeypatch.setattr("tools.eos.saas.billing.platform_billing_financial_execution_request_registry.PlatformBillingFinancialExecutionRequestRegistry.get",staticmethod(lambda *a,**k: request))
    db={"platform_billing_financial_execution_requests":C(),"platform_billing_provider_routing_decisions":c}
    result,replay=route_platform_billing_request("t1","req1","caller-id-is-ignored",db,session=SimpleNamespace(in_transaction=True))
    assert replay is True and result.routing_decision_id=="rd1"

def test_request_level_index_name_is_stable():
    c=C(); PlatformBillingProviderRoutingDecisionRegistry.ensure_indexes(c)
    assert c.index_calls[1][1]["name"]=="tenant_source_execution_request_unique"

def test_registry_rejects_multiple_rows_even_when_first_is_valid():
    c=C(); c.rows.extend([_decision().to_persisted(),_decision(routing_decision_id="rd2").to_persisted()])
    try: PlatformBillingProviderRoutingDecisionRegistry.get_by_request("t1","req1",c,session=object())
    except RuntimeError as exc: assert str(exc)=="MULTIPLE_ROUTING_DECISIONS_FOR_REQUEST"
    else: raise AssertionError("first row was selected from ambiguous request cardinality")

def test_p4_orchestration_has_no_current_policy_resolution():
    import inspect
    from tools.eos.kennel.orchestration import platform_billing_provider_routing as routing
    source=inspect.getsource(routing.route_platform_billing_request).lower()
    assert "current(" not in source and "latest" not in source and "highest" not in source

# ARTIFACT: test_platform_billing_provider_routing_decision.py
# VERSION: v1.1.0-M11E2D5C2G-P5-R2C
# AUTHORITY BOUNDARY: direct routing certificate only
# FAIL-CLOSED POSTURE: corruption and replay conflicts reject
# END OF WILSY OS SOVEREIGN ARTIFACT
