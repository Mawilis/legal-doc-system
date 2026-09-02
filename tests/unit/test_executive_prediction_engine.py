"""TITLE: WILSY Executive Evidence-Bound Prediction Engine Direct Certificate
VERSION: v1.0.0-WILSY-EXECUTIVE-PREDICTION-CERT
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
EPITOME: Direct adversarial certificate for the frozen evidence-bound Executive Prediction production contract.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_executive_prediction_engine.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-02
CHANGELOG: Initial direct certificate for v1.0.0-WILSY-EXECUTIVE-PREDICTION-EVIDENCE.
COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY: Stable errors and identifiers must not echo caller secrets.
TENANT BOUNDARY: Identity derives only through the validated Prediction -> Planning -> Decision -> Reasoning -> Context -> KernelBootstrapRequest chain.
AUTHORITY BOUNDARY: Certificate proves advisory prediction behavior only and grants no authority.
EVIDENCE BOUNDARY: NO EVIDENCE = NO FACT; certificate proves Prediction creates no evidence and preserves exact Planning evidence references.
REASONING BOUNDARY: Prediction accepts no independent reasoning authority; reasoning provenance is inherited only through the validated Planning/Decision chain.
DECISION BOUNDARY: Decision provenance is inherited only through Planning and grants no approval or execution authority.
PLANNING BOUNDARY: ExecutivePlanningResult is the sole upstream Planning/provenance basis and grants no execution authority.
PREDICTION BOUNDARY: Caller-supplied predictive metadata is advisory and inert; no forecast, probability, confidence, risk, trend, outcome, accuracy claim, workflow, approval, or execution is manufactured.
RETRIEVAL BOUNDARY: None.
MODEL BOUNDARY: None.
EXECUTION BOUNDARY: None.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
PRODUCTION UNDER CERTIFICATION: tools/eos/executive/intelligence/executive_prediction_engine.py
PRODUCTION VERSION: v1.0.0-WILSY-EXECUTIVE-PREDICTION-EVIDENCE
PRODUCTION SHA3-512: fd65d12d3e2be5127ddd23576396d0a267ccaabb969ab92289820a91fe3ce825a9e44c39ec21db56f54548d1ad56bee12e6e88a14d4ccc2ffaed41ce1ab8cf23
"""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone, timedelta
from hashlib import sha3_512
from pathlib import Path
import ast
from typing import cast
import pytest
from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest
from tools.eos.executive.intelligence.executive_context_engine import ExecutiveContext, ExecutiveEvidence
from tools.eos.executive.intelligence.executive_reasoning_engine import executive_reasoning_engine
from tools.eos.executive.intelligence.executive_decision_engine import executive_decision_engine
from tools.eos.executive.intelligence.executive_planning_engine import executive_planning_engine
from tools.eos.executive.intelligence.executive_prediction_engine import *
STAMP=datetime(2026,9,2,10,tzinfo=timezone.utc)
def planning(request="request-a", evidence=(), intent="plan"):
    a=KernelBootstrapRequest("tenant-a","principal-a",request,"corr-a"); c=ExecutiveContext(a,tuple(evidence),STAMP); r=executive_reasoning_engine.evaluate_query("query",c,evaluated_at=STAMP); d=executive_decision_engine.evaluate_decision("decide","operations",r,evaluated_at=STAMP); return executive_planning_engine.build_plan(intent,("step",),d,planned_at=STAMP)
def evidence(eid="e-a",request="request-a",content="fact"):
    return ExecutiveEvidence(eid,"tenant-a","principal-a",request,"source-a","document","repo://a","page:1",content,sha3_512(content.encode()).hexdigest(),"receipt-a",STAMP,None)
def pred(p,intent="predict",targets=("target",),at=STAMP): return executive_prediction_engine.build_prediction(intent,targets,p,predicted_at=at)
def fails(code,fn):
    with pytest.raises(ExecutivePredictionError) as e: fn()
    assert str(e.value)==code
class SecretObject:
    def __init__(self, marker): self.marker=marker
    def __str__(self): return self.marker
    def __repr__(self): return f"SecretObject({self.marker})"
def test_public_and_no_evidence():
    p=planning(); r=pred(p); assert VERSION=="v1.0.0-WILSY-EXECUTIVE-PREDICTION-EVIDENCE" and issubclass(ExecutivePredictionError,ValueError); assert isinstance(executive_prediction_engine,ExecutivePredictionEngine); assert {n for n,v in ExecutivePredictionEngine.__dict__.items() if not n.startswith('_') and callable(v)}=={'build_prediction'}; assert type(r) is ExecutivePredictionResult and r.status=="NO_EVIDENCE" and r.evidence_count==0 and r.evidence_references==()
    for n in ("generate_prediction","get_prediction","export_prediction_state","execute","dispatch","approve","authorize","release","pay","transfer","commit","persist","learn","retrieve","fetch","query_model","predict_with_model"): assert not hasattr(executive_prediction_engine,n) and not hasattr(r,n)
def test_evidence_bound_and_text():
    p=planning(evidence=(evidence(),evidence("e-b",content="second"))); intent="  forecast whether to approve release and transfer payment\t"; targets=(" expected payment outcome ","financial\x1ftransfer risk","\tvalid target\t"); r=pred(p,intent,targets); assert r.status=="EVIDENCE_BOUND" and r.evidence_count==2 and r.evidence_references==p.evidence_references and r.prediction_intent==intent and r.prediction_targets==targets
def test_ids_and_collisions():
    p=planning(); a=pred(p,"alpha",("beta\x1fgamma",)); b=pred(p,"alpha",("beta","gamma")); c=pred(p,"alpha\x1fbeta",("gamma",)); assert a.prediction_id!=b.prediction_id and c.prediction_id!=b.prediction_id
    assert a.prediction_id==pred(p,"alpha",("beta\x1fgamma",)).prediction_id and a.prediction_id.startswith("PRED-") and len(a.prediction_id)==21
    assert pred(planning("request|alpha")).request_id=="request|alpha" and pred(planning("request|alpha")).prediction_id!=pred(planning("request|beta")).prediction_id
    assert pred(planning(),"x",("target",),STAMP).prediction_id!=pred(planning(),"y",("target",),STAMP).prediction_id
    assert pred(planning(),"x",("a","b"),STAMP).prediction_id!=pred(planning(),"x",("b","a"),STAMP).prediction_id
def test_direct_constructor_and_status():
    p=planning(); r=pred(p); direct=ExecutivePredictionResult(r.prediction_id,r.predicted_at,r.prediction_intent,r.prediction_targets,r.planning,r.evidence_references,r.status); assert direct==r
    forged="PRED-"+"0"*16; fails("INVALID_PREDICTION_ID",lambda: replace(r,prediction_id=forged))
    fails("INVALID_PREDICTION_STATUS",lambda: ExecutivePredictionResult(r.prediction_id,r.predicted_at,r.prediction_intent,r.prediction_targets,r.planning,r.evidence_references,"EVIDENCE_BOUND"))
    e=planning(evidence=(evidence(),)); q=pred(e); fails("INVALID_PREDICTION_STATUS",lambda: ExecutivePredictionResult(q.prediction_id,q.predicted_at,q.prediction_intent,q.prediction_targets,q.planning,q.evidence_references,"NO_EVIDENCE"))
@pytest.mark.parametrize("bad",[None,True,False,0,1.5,b"x",[],{},(),"", " ","\t"])
def test_intent_matrix(bad): fails("INVALID_PREDICTION_INTENT",lambda: executive_prediction_engine.build_prediction(bad,("x",),planning(),predicted_at=STAMP))
@pytest.mark.parametrize("bad",[None,True,False,0,1.5,b"x",[],{},set(),"x",()])
def test_target_collection_matrix(bad): fails("INVALID_PREDICTION_TARGETS",lambda: executive_prediction_engine.build_prediction("x",bad,planning(),predicted_at=STAMP))
@pytest.mark.parametrize("bad",[None,True,False,0,1.5,b"x",[],{},(),set(),""," ","\t"])
def test_target_element_matrix(bad): fails("INVALID_PREDICTION_TARGET",lambda: executive_prediction_engine.build_prediction("x",(bad,),planning(),predicted_at=STAMP))
@pytest.mark.parametrize("bad",[None,True,0,{},[],KernelBootstrapRequest("t","p","r","c")])
def test_planning_type_matrix(bad): fails("INVALID_PLANNING_TYPE",lambda: executive_prediction_engine.build_prediction("x",("y",),bad,predicted_at=STAMP))
@pytest.mark.parametrize("bad",["2026",b"x",7,1.5,True,datetime(2026,1,1)])
def test_timestamp_matrix(bad): fails("INVALID_PREDICTED_AT",lambda: executive_prediction_engine.build_prediction("x",("y",),planning(),predicted_at=bad))
def test_timestamp_and_provenance():
    local=datetime(2026,9,2,tzinfo=timezone(timedelta(hours=2))); r=pred(planning(),at=local); assert r.predicted_at==local; auto=executive_prediction_engine.build_prediction("x",("y",),planning()); assert auto.predicted_at.tzinfo is not None and auto.predicted_at.utcoffset() is not None
    p=planning(evidence=(evidence(),evidence("e-b",content="second"))); r=pred(p); fails("INVALID_PREDICTION_REFERENCE_TYPE",lambda: replace(r,evidence_references=list(r.evidence_references))); fails("INVALID_PREDICTION_REFERENCE_TYPE",lambda: replace(r,evidence_references=(r.evidence_references[0],object()))); fails("EVIDENCE_REFERENCE_MISMATCH",lambda: replace(r,evidence_references=(r.evidence_references[1],r.evidence_references[0]))); fails("EVIDENCE_REFERENCE_MISMATCH",lambda: replace(r,evidence_references=()))
@pytest.mark.parametrize("field,value",[("evidence_id","x"),("source_id","x"),("source_type","x"),("source_locator","x"),("citation_locator","x"),("content_sha3_512","0"*128),("authorization_receipt_ref","x"),("retrieved_at",datetime(2026,9,2,11,tzinfo=timezone.utc)),("source_version","x")])
def test_provenance_fields(field,value):
    p=planning(evidence=(evidence(),evidence("e-b",content="second"))); r=pred(p); refs=(replace(r.evidence_references[0],**{field:value}),r.evidence_references[1]); fails("EVIDENCE_REFERENCE_MISMATCH",lambda: replace(r,evidence_references=refs))
@pytest.mark.parametrize("code,marker,call",[("INVALID_PREDICTION_ID","PRIVATE-PREDICTION-SECRET-ID",lambda s,r: ExecutivePredictionResult(s,r.predicted_at,r.prediction_intent,r.prediction_targets,r.planning,r.evidence_references,r.status)),("INVALID_PREDICTION_INTENT","PRIVATE-PREDICTION-SECRET-INTENT",lambda s,r: executive_prediction_engine.build_prediction(s,("x",),r.planning,predicted_at=STAMP)),("INVALID_PREDICTION_TARGETS","PRIVATE-PREDICTION-SECRET-TARGETS",lambda s,r: executive_prediction_engine.build_prediction("x",s,r.planning,predicted_at=STAMP)),("INVALID_PREDICTION_TARGET","PRIVATE-PREDICTION-SECRET-TARGET",lambda s,r: executive_prediction_engine.build_prediction("x",(s,),r.planning,predicted_at=STAMP)),("INVALID_PREDICTED_AT","PRIVATE-PREDICTION-SECRET-TIMESTAMP",lambda s,r: executive_prediction_engine.build_prediction("x",("x",),r.planning,predicted_at=s)),("INVALID_PLANNING_TYPE","PRIVATE-PREDICTION-SECRET-PLANNING",lambda s,r: executive_prediction_engine.build_prediction("x",("x",),s,predicted_at=STAMP)),("INVALID_PREDICTION_REFERENCE_TYPE","PRIVATE-PREDICTION-SECRET-REFERENCES",lambda s,r: replace(r,evidence_references=(s,))), ("INVALID_PREDICTION_STATUS","PRIVATE-PREDICTION-SECRET-STATUS",lambda s,r: ExecutivePredictionResult(r.prediction_id,r.predicted_at,r.prediction_intent,r.prediction_targets,r.planning,r.evidence_references,s))])
def test_privacy_non_echo_matrix(code,marker,call):
    r=pred(planning()); secret=SecretObject(marker)
    with pytest.raises(ExecutivePredictionError) as caught: call(secret,r)
    assert str(caught.value)==code and marker not in str(caught.value) and repr(secret) not in str(caught.value)
def test_immutability_slots_statelessness_authority():
    before=dict(vars(executive_prediction_engine)); plans=[pred(planning(f"r-{x}")) for x in "abc"]; assert len({x.prediction_id for x in plans})==3 and dict(vars(executive_prediction_engine))==before
    for n in ("_state","_state_lock","_predictions","_active_predictions","prediction_history","cache","_cache","history","_history","registry","_registry","_lock","_instance"): assert not hasattr(executive_prediction_engine,n)
    with pytest.raises(FrozenInstanceError): plans[0].status="NO_EVIDENCE"  # type: ignore[misc]
    with pytest.raises((AttributeError,TypeError)): plans[0].new_attr=1  # type: ignore[attr-defined]
def test_identity_and_source_boundary():
    expected={"tools/eos/executive/intelligence/executive_prediction_engine.py":(8666,"fd65d12d3e2be5127ddd23576396d0a267ccaabb969ab92289820a91fe3ce825a9e44c39ec21db56f54548d1ad56bee12e6e88a14d4ccc2ffaed41ce1ab8cf23"),"tools/eos/executive/intelligence/executive_planning_engine.py":(7615,"41f0f19a3dc9ce4b3ad27c762d8943167d47944fe18cedb87e0bda5a1ba63335f323de01ebc8f244fc8ad84efca422473352abe393ce0a45212f5c0a11aeeff6")}
    expected.update({"tools/eos/executive/intelligence/executive_decision_engine.py":(11574,"38ce4200c511e3444b18853351405adb9e326027d504269e32738143a30f6890a9c31c31e75d4037f4159f82d1bd64faec47a82336488271e8d5d1c1f936d20f"),"tools/eos/executive/intelligence/executive_reasoning_engine.py":(6919,"a04f2dc702f40ee39535fdf3393c1e46e7381bda836791f6be9280724e0d07912c5e1b0684dcfa011bb8e09b104755b754c356942ed378a433ebb5da734adefb"),"tools/eos/executive/intelligence/executive_context_engine.py":(7044,"f02cf9aecb25b34470fc16b6db7f4c7bca285db13874e395856cb9f0b4bee39f5a8223a4c7e019e5d3829030ab8d7a750f8c8429e871ff34c2156a64b1509896"),"tests/unit/test_executive_planning_engine.py":(23882,"3073f102f2271e3ba1364496b7d115ae8b2ac709c9aaaf57145be164f7cbe655e0647ce1706a04ce3215a4a6500cdc7f58452d80947cd6f5d9cd69d176e26918"),"tests/unit/test_executive_decision_engine.py":(11861,"f62143125f3cd23c2f4fead2bd8d6c5bff7080460e95b0f816a3e4909b344742bbacd2c91bffdae236913381e8bc144f14e09723b601e5922450e1b522c83a32"),"tests/unit/test_executive_reasoning_engine.py":(22574,"2c3814ca12f2712faa82421c0af532bcf4c496dce42c0c32450fad06c6510ae2c102efa7443b7113721c5d0978f186e42dfeb93cac8cab27ec9ceac0f4aad655"),"tests/unit/test_executive_context_engine.py":(12043,"a02bea87fb0f6b006451c941b00b095bdf3ed2d4212f18af20ddad515de51b955c278d1de11c12518169ee208fab949e3330e5c328ca7ced03de83a8d781df3d")})
    for n,(size,digest) in expected.items():
        b=Path(n).read_bytes(); assert (len(b),sha3_512(b).hexdigest())==(size,digest)
    source=Path("tools/eos/executive/intelligence/executive_prediction_engine.py").read_text(); assert "|\".join" not in source and all(x not in source for x in ("threading","logging.basicConfig","uuid","random","_predictions","generate_prediction","get_prediction","export_prediction_state","+18.4% YoY","98.2%","VERIFIED_ACCURATE","TODO","FIXME","NotImplemented"))
    assert Path(__file__).read_text().rstrip().endswith("# END OF "+"WILSY OS SOVEREIGN CERTIFICATE")
def test_frame_text_semantics_and_oracle():
    import tools.eos.executive.intelligence.executive_prediction_engine as prod
    for value in ("", "a", "alpha", "request|alpha", "βeta", "with spaces", "\x1f", "emoji-🔒"):
        raw=value.encode(); frame=prod._frame_text(value)
        assert frame==len(raw).to_bytes(8,"big")+raw and len(frame)==8+len(raw)
    p=planning("request|alpha"); r=pred(p,"α",("β","x\x1f"),datetime(2026,9,2,tzinfo=timezone(timedelta(hours=2))))
    h=sha3_512()
    def f(v): raw=v.encode(); return len(raw).to_bytes(8,"big")+raw
    th=sha3_512();
    for t in r.prediction_targets: th.update(f(t))
    for v in (p.request_id,p.plan_id,p.decision_id,sha3_512("α".encode()).hexdigest(),th.hexdigest(),r.predicted_at.isoformat()): h.update(f(v))
    assert r.prediction_id=="PRED-"+h.hexdigest()[:16]
    bad=sha3_512("|".join((p.request_id,p.plan_id,p.decision_id,sha3_512("α".encode()).hexdigest(),th.hexdigest(),r.predicted_at.isoformat())).encode()).hexdigest()[:16]
    assert r.prediction_id!="PRED-"+bad
def test_id_ast_component_framing_flow():
    tree=ast.parse(Path("tools/eos/executive/intelligence/executive_prediction_engine.py").read_text()); funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_id"]; assert len(funcs)==1
    loops=[n for n in ast.walk(funcs[0]) if isinstance(n,ast.For)]; assert loops
    loop=next(n for n in loops if isinstance(n.iter,ast.Tuple) and len(n.iter.elts)==6); values=[ast.dump(x,include_attributes=False) for x in cast(ast.Tuple, loop.iter).elts]
    expected=["Attribute(value=Name(id='planning', ctx=Load()), attr='request_id', ctx=Load())","Attribute(value=Name(id='planning', ctx=Load()), attr='plan_id', ctx=Load())","Attribute(value=Name(id='planning', ctx=Load()), attr='decision_id', ctx=Load())","Name(id='intent_digest', ctx=Load())","Name(id='target_digest', ctx=Load())","Call(func=Attribute(value=Name(id='stamp', ctx=Load()), attr='isoformat', ctx=Load()))"]
    assert values==expected
    assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="update" and n.args and isinstance(n.args[0],ast.Call) and isinstance(n.args[0].func,ast.Name) and n.args[0].func.id=="_frame_text" for n in ast.walk(funcs[0]))
    source=Path(__file__).read_text(); doc=ast.get_docstring(ast.parse(source),clean=False)
    fields=("TITLE","VERSION","AUTHORITY","EPITOME","ABSOLUTE CANONICAL PATH","COLLABORATION / OWNERSHIP","CERTIFICATION/UPDATE DATE","CHANGELOG","COMPLIANCE","SECURITY / PRIVACY","TENANT BOUNDARY","AUTHORITY BOUNDARY","EVIDENCE BOUNDARY","REASONING BOUNDARY","DECISION BOUNDARY","PLANNING BOUNDARY","PREDICTION BOUNDARY","RETRIEVAL BOUNDARY","MODEL BOUNDARY","EXECUTION BOUNDARY","FINANCIAL AUTHORITY BOUNDARY","PRODUCTION UNDER CERTIFICATION","PRODUCTION VERSION","PRODUCTION SHA3-512")
    assert doc is not None and len(fields)==24
    for field in fields: assert sum(line.startswith(field+": ") for line in doc.splitlines())==1
    terminator="# END OF "+"WILSY OS SOVEREIGN CERTIFICATE"; assert source.endswith(terminator+"\n") and source.count(terminator)==1 and not source.endswith("\n\n")
# ARTIFACT: test_executive_prediction_engine.py
# VERSION: v1.0.0-WILSY-EXECUTIVE-PREDICTION-CERT
# PRODUCTION UNDER CERTIFICATION: tools/eos/executive/intelligence/executive_prediction_engine.py
# PRODUCTION VERSION: v1.0.0-WILSY-EXECUTIVE-PREDICTION-EVIDENCE
# PRODUCTION SHA3-512: fd65d12d3e2be5127ddd23576396d0a267ccaabb969ab92289820a91fe3ce825a9e44c39ec21db56f54548d1ad56bee12e6e88a14d4ccc2ffaed41ce1ab8cf23
# AUTHORITY BOUNDARY: certificate proves advisory prediction behavior only and grants no authority.
# TENANT POSTURE: tenant and principal identity must derive only through the validated Prediction -> Planning -> Decision -> Reasoning -> Context -> KernelBootstrapRequest chain.
# EVIDENCE POSTURE: NO EVIDENCE = NO FACT; certificate proves Prediction creates no evidence and preserves exact Planning evidence references.
# REASONING POSTURE: Prediction accepts no independent reasoning authority; reasoning provenance is inherited only through the validated Planning/Decision chain.
# DECISION POSTURE: decision provenance is inherited only through Planning and grants no approval or execution authority.
# PLANNING POSTURE: ExecutivePlanningResult is the sole upstream Planning/provenance basis and grants no execution authority.
# PREDICTION POSTURE: caller-supplied predictive metadata is advisory and inert; no forecast, probability, confidence, risk, trend, outcome, accuracy claim, workflow, approval, or execution is manufactured.
# FAIL-CLOSED POSTURE: malformed identities, timestamps, targets, deterministic IDs, status, or provenance must reject with stable non-echoing errors.
# RETRIEVAL AUTHORITY: NONE
# MODEL AUTHORITY: NONE
# EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN CERTIFICATE
