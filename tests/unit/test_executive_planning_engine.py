"""WILSY OS direct certificate for evidence-bound executive planning.

TITLE: WILSY Executive Evidence-Bound Planning Engine Direct Certificate
VERSION: v1.0.0-WILSY-EXECUTIVE-PLANNING-CERT
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
EPITOME: Direct adversarial certificate for the frozen evidence-bound Executive Planning production contract.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_executive_planning_engine.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: Initial direct certificate for v1.0.0-WILSY-EXECUTIVE-PLANNING-EVIDENCE.
COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY: Stable errors and identifiers do not echo caller secrets.
TENANT BOUNDARY: Identity derives only through ExecutiveDecisionResult.
AUTHORITY BOUNDARY: Advisory planning only; no approval, authorization, or execution.
EVIDENCE BOUNDARY: NO EVIDENCE = NO FACT; planning creates no evidence.
REASONING BOUNDARY: Provenance is inherited through the validated decision chain.
DECISION BOUNDARY: Decision is the sole upstream input and grants no authority.
PLANNING BOUNDARY: Caller text is inert metadata; no workflow or outcome is generated.
RETRIEVAL BOUNDARY: None.
MODEL BOUNDARY: None.
EXECUTION BOUNDARY: None.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
PRODUCTION UNDER CERTIFICATION: tools/eos/executive/intelligence/executive_planning_engine.py
PRODUCTION VERSION: v1.0.0-WILSY-EXECUTIVE-PLANNING-EVIDENCE
PRODUCTION SHA3-512: 41f0f19a3dc9ce4b3ad27c762d8943167d47944fe18cedb87e0bda5a1ba63335f323de01ebc8f244fc8ad84efca422473352abe393ce0a45212f5c0a11aeeff6
"""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone, timedelta
from hashlib import sha3_512
import re
from typing import Any, cast
import pytest
from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest
from tools.eos.executive.intelligence.executive_context_engine import ExecutiveContext, ExecutiveEvidence
from tools.eos.executive.intelligence.executive_reasoning_engine import executive_reasoning_engine, ExecutiveReasoningEvidenceReference
from tools.eos.executive.intelligence.executive_decision_engine import ExecutiveDecisionResult, executive_decision_engine
from tools.eos.executive.intelligence.executive_planning_engine import VERSION, ExecutivePlanningEngine, ExecutivePlanningError, ExecutivePlanningResult, executive_planning_engine
STAMP = datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc)
def chain(request_id: str = "request-a", *items: ExecutiveEvidence):
    auth = KernelBootstrapRequest("tenant-a", "principal-a", request_id, "corr-a")
    ctx = ExecutiveContext(auth, tuple(items), STAMP)
    return executive_reasoning_engine.evaluate_query("q", ctx, evaluated_at=STAMP)
def ev(eid: str = "e-a", content: str = "fact") -> ExecutiveEvidence:
    return ExecutiveEvidence(eid, "tenant-a", "principal-a", "request-a", "source-a", "document", "repo://source-a", "page:1", content, sha3_512(content.encode()).hexdigest(), "receipt-a", STAMP, None)
def make_decision(r: Any, intent: str = "assess", domain: str = "operations"):
    return executive_decision_engine.evaluate_decision(intent, domain, r, evaluated_at=STAMP)
def err(code: str, fn: Any) -> None:
    with pytest.raises(ExecutivePlanningError) as caught: fn()
    assert str(caught.value) == code
def test_public_contract_and_empty_path() -> None:
    assert VERSION == "v1.0.0-WILSY-EXECUTIVE-PLANNING-EVIDENCE"; assert issubclass(ExecutivePlanningError, ValueError); assert isinstance(executive_planning_engine, ExecutivePlanningEngine)
    public = {name for name, value in ExecutivePlanningEngine.__dict__.items() if not name.startswith("_") and callable(value)}
    assert public == {"build_plan"}
    assert not hasattr(executive_planning_engine, "generate_enterprise_plan") and not hasattr(executive_planning_engine, "get_plan_state")
    result = executive_planning_engine.build_plan("assess", ("observe",), make_decision(chain()), planned_at=STAMP)
    assert isinstance(result, ExecutivePlanningResult); assert (result.tenant_id,result.principal_id,result.request_id,result.correlation_id,result.decision_id,result.target_domain,result.evidence_count,result.evidence_references,result.status)==("tenant-a","principal-a","request-a","corr-a",result.decision_id,"operations",0,(),"NO_EVIDENCE")
def test_evidence_bound_and_preservation() -> None:
    a,b=ev(),ev("e-b","second"); d=make_decision(chain("request-a",a,b)); p=executive_planning_engine.build_plan("  assess  ",(" step ","financial"),d,planned_at=STAMP)
    assert p.status=="EVIDENCE_BOUND" and p.evidence_count==2 and p.evidence_references==d.evidence_references and p.plan_intent=="  assess  " and p.plan_steps==(" step ","financial")
    assert (p.tenant_id,p.principal_id,p.request_id,p.correlation_id,p.decision_id,p.target_domain)==(d.tenant_id,d.principal_id,d.request_id,d.correlation_id,d.decision_id,d.target_domain)

def test_caller_plan_text_and_delimiters_preserved_exactly() -> None:
    intent = "  assess  "
    steps = ("  step one  ", "beta\x1fgamma", "\tvalid\t")
    result = executive_planning_engine.build_plan(intent, steps, make_decision(chain()), planned_at=STAMP)
    assert result.plan_intent == intent
    assert result.plan_steps == steps
def test_plan_id_shape_determinism_and_binding() -> None:
    d=make_decision(chain()); base=executive_planning_engine.build_plan("a",("b","c"),d,planned_at=STAMP); same=executive_planning_engine.build_plan("a",("b","c"),d,planned_at=STAMP)
    assert re.fullmatch(r"PLAN-[0-9a-f]{16}",base.plan_id) and base.plan_id==same.plan_id
    assert base.plan_id!=executive_planning_engine.build_plan("x",("b","c"),d,planned_at=STAMP).plan_id
    assert base.plan_id!=executive_planning_engine.build_plan("a",("x","c"),d,planned_at=STAMP).plan_id
    assert base.plan_id!=executive_planning_engine.build_plan("a",("c","b"),d,planned_at=STAMP).plan_id
    assert base.plan_id!=executive_planning_engine.build_plan("a",("b","c"),d,planned_at=datetime(2026,9,1,11,tzinfo=timezone.utc)).plan_id
    other=make_decision(chain(),"different"); assert base.plan_id!=executive_planning_engine.build_plan("a",("b","c"),other,planned_at=STAMP).plan_id
    request_changed=make_decision(chain("request-b")); assert base.request_id != request_changed.request_id
def test_delimiter_collision_and_request_binding() -> None:
    d=make_decision(chain()); a=executive_planning_engine.build_plan("alpha",("beta\x1fgamma",),d,planned_at=STAMP); b=executive_planning_engine.build_plan("alpha",("beta","gamma"),d,planned_at=STAMP); c=executive_planning_engine.build_plan("alpha\x1fbeta",("gamma",),d,planned_at=STAMP)
    assert a.plan_id!=b.plan_id and c.plan_id!=b.plan_id
@pytest.mark.parametrize("bad",[None,7,True,b"x",[],{},(),""," "])
def test_plan_intent_fail_closed(bad: object)->None: err("INVALID_PLAN_INTENT",lambda: executive_planning_engine.build_plan(bad,("x",),make_decision(chain()),planned_at=STAMP)) # type: ignore[arg-type]
@pytest.mark.parametrize("bad",[None,7,True,b"x",[],{},()," "])
def test_steps_fail_closed(bad: object)->None: err("INVALID_PLAN_STEPS" if not isinstance(bad,tuple) else "INVALID_PLAN_STEPS",lambda: executive_planning_engine.build_plan("x",bad,make_decision(chain()),planned_at=STAMP)) # type: ignore[arg-type]
def test_step_element_validation():
    d=make_decision(chain()); err("INVALID_PLAN_STEPS",lambda: executive_planning_engine.build_plan("x",(),d,planned_at=STAMP)); err("INVALID_PLAN_STEP",lambda: executive_planning_engine.build_plan("x",(" ",),d,planned_at=STAMP)); err("INVALID_PLAN_STEP",lambda: executive_planning_engine.build_plan("x",(7,),d,planned_at=STAMP)) # type: ignore[arg-type]
@pytest.mark.parametrize("bad",["2026",7,1.5,True,datetime(2026,9,1,10)])
def test_planned_at_validation(bad: object)->None: err("INVALID_PLANNED_AT",lambda: executive_planning_engine.build_plan("x",("y",),make_decision(chain()),planned_at=bad)) # type: ignore[arg-type]
def test_direct_constructor_and_provenance_fail_closed():
    d=make_decision(chain()); p=executive_planning_engine.build_plan("x",("y",),d,planned_at=STAMP); err("INVALID_PLAN_ID",lambda: ExecutivePlanningResult("PLAN-0000000000000000",STAMP,"x",("y",),d,(),"NO_EVIDENCE")); err("INVALID_DECISION_TYPE",lambda: ExecutivePlanningResult(p.plan_id,STAMP,"x",("y",),None,(),"NO_EVIDENCE")) # type: ignore[arg-type]
    with pytest.raises(FrozenInstanceError): p.status="EVIDENCE_BOUND" # type: ignore[misc]
def test_authority_and_privacy_boundaries():
    p=executive_planning_engine.build_plan("approve payment",("release",),make_decision(chain(),"transfer","financial"),planned_at=STAMP)
    for name in ("approve","authorize","execute","dispatch","release","pay","transfer","get_plan_state"): assert not hasattr(p,name) and not hasattr(executive_planning_engine,name)
    secret="PRIVATE-PLAN-SECRET"
    d = make_decision(chain())
    with pytest.raises(ExecutivePlanningError) as caught:
        ExecutivePlanningResult("PLAN-0000000000000000", STAMP, secret, ("step",), d, d.evidence_references, "NO_EVIDENCE")
    assert str(caught.value) != secret and secret not in str(caught.value)

def test_request_binding_builds_two_complete_plans():
    a = make_decision(chain("request-a")); b = make_decision(chain("request-b"))
    pa = executive_planning_engine.build_plan("x", ("y",), a, planned_at=STAMP); pb = executive_planning_engine.build_plan("x", ("y",), b, planned_at=STAMP)
    assert pa.request_id != pb.request_id and pa.plan_id != pb.plan_id

def test_decision_binding_asserts_distinct_decisions_and_plans():
    da = make_decision(chain(), "a"); db = make_decision(chain(), "b")
    assert da.decision_id != db.decision_id
    pa = executive_planning_engine.build_plan("x", ("y",), da, planned_at=STAMP); pb = executive_planning_engine.build_plan("x", ("y",), db, planned_at=STAMP)
    assert pa.plan_id != pb.plan_id

@pytest.mark.parametrize("bad", [None, True, False, 0, 1.5, "", " ", "PLAN-", "BAD-0000000000000000", "plan-0000000000000000", "PLAN-000000000000000G", "PLAN-000000000000000", "PLAN-00000000000000000", "PLAN-0000000000000000x"])
def test_direct_plan_id_matrix(bad: object):
    d = make_decision(chain()); p = executive_planning_engine.build_plan("x", ("y",), d, planned_at=STAMP)
    err("INVALID_PLAN_ID", lambda: ExecutivePlanningResult(bad, p.planned_at, p.plan_intent, p.plan_steps, d, p.evidence_references, p.status))  # type: ignore[arg-type]

@pytest.mark.parametrize("bad", [None, True, 1, 1.5, b"x", [], {}, (), set(), "", " ", "\t", "\n"])
def test_direct_step_element_matrix(bad: object):
    err("INVALID_PLAN_STEP", lambda: executive_planning_engine.build_plan("x", (bad,), make_decision(chain()), planned_at=STAMP))  # type: ignore[arg-type]

def test_provenance_structure_two_reference_cases():
    a,b=ev(),ev("e-b","second"); d=make_decision(chain("request-a",a,b)); ra,rb=d.evidence_references; p=executive_planning_engine.build_plan("x",("y",),d,planned_at=STAMP)
    for refs in [(), (ra,), (ra,rb,ra), (ra,ra), (rb,ra)]: err("EVIDENCE_REFERENCE_MISMATCH", lambda refs=refs: ExecutivePlanningResult(p.plan_id,p.planned_at,p.plan_intent,p.plan_steps,d,refs,p.status))

def test_frozen_identity_and_source_boundary():
    from pathlib import Path
    files = {
        "tools/eos/executive/intelligence/executive_planning_engine.py": (7615, "41f0f19a3dc9ce4b3ad27c762d8943167d47944fe18cedb87e0bda5a1ba63335f323de01ebc8f244fc8ad84efca422473352abe393ce0a45212f5c0a11aeeff6"),
        "tools/eos/executive/intelligence/executive_decision_engine.py": (11574, "38ce4200c511e3444b18853351405adb9e326027d504269e32738143a30f6890a9c31c31e75d4037f4159f82d1bd64faec47a82336488271e8d5d1c1f936d20f"),
        "tools/eos/executive/intelligence/executive_reasoning_engine.py": (6919, "a04f2dc702f40ee39535fdf3393c1e46e7381bda836791f6be9280724e0d07912c5e1b0684dcfa011bb8e09b104755b754c356942ed378a433ebb5da734adefb"),
        "tools/eos/executive/intelligence/executive_context_engine.py": (7044, "f02cf9aecb25b34470fc16b6db7f4c7bca285db13874e395856cb9f0b4bee39f5a8223a4c7e019e5d3829030ab8d7a750f8c8429e871ff34c2156a64b1509896"),
        "tests/unit/test_executive_decision_engine.py": (11861, "f62143125f3cd23c2f4fead2bd8d6c5bff7080460e95b0f816a3e4909b344742bbacd2c91bffdae236913381e8bc144f14e09723b601e5922450e1b522c83a32"),
    }
    for name, (size, digest) in files.items():
        raw = Path(name).read_bytes(); assert (len(raw), sha3_512(raw).hexdigest()) == (size, digest)
    source = Path("tools/eos/executive/intelligence/executive_planning_engine.py").read_text()
    assert not any(token in source for token in ("threading", "uuid", "random", "PLAN_GENERATED", "_active_plans", "generate_enterprise_plan", "get_plan_state", "TODO", "FIXME", "NotImplemented"))

def test_request_and_decision_ids_bind_plans_explicitly():
    a = make_decision(chain("request-a")); b = make_decision(chain("request-b"))
    pa = executive_planning_engine.build_plan("x", ("y",), a, planned_at=STAMP); pb = executive_planning_engine.build_plan("x", ("y",), b, planned_at=STAMP)
    assert pa.request_id != pb.request_id and pa.plan_id != pb.plan_id
    da = make_decision(chain(), "a"); db = make_decision(chain(), "b")
    assert da.decision_id != db.decision_id
    assert executive_planning_engine.build_plan("x", ("y",), da, planned_at=STAMP).plan_id != executive_planning_engine.build_plan("x", ("y",), db, planned_at=STAMP).plan_id

def test_direct_valid_constructors_and_slots():
    empty = make_decision(chain()); plan = executive_planning_engine.build_plan("x", ("y",), empty, planned_at=STAMP)
    direct = ExecutivePlanningResult(plan.plan_id, plan.planned_at, plan.plan_intent, plan.plan_steps, plan.decision, plan.evidence_references, plan.status)
    assert direct == plan and not hasattr(direct, "__dict__")
    item = ev(); bound = make_decision(chain("request-a", item)); bp = executive_planning_engine.build_plan("x", ("y",), bound, planned_at=STAMP)
    direct_bound = ExecutivePlanningResult(bp.plan_id, bp.planned_at, bp.plan_intent, bp.plan_steps, bp.decision, bp.evidence_references, bp.status)
    assert direct_bound.plan_id == bp.plan_id
    assert direct_bound.planned_at == bp.planned_at
    assert direct_bound.plan_intent == bp.plan_intent
    assert direct_bound.plan_steps == bp.plan_steps
    assert direct_bound.decision is bp.decision
    assert direct_bound.evidence_references == bp.evidence_references
    assert direct_bound.evidence_count == 1
    assert (direct_bound.tenant_id, direct_bound.principal_id, direct_bound.request_id, direct_bound.correlation_id, direct_bound.decision_id, direct_bound.target_domain, direct_bound.status) == ("tenant-a", "principal-a", "request-a", "corr-a", bp.decision_id, "operations", "EVIDENCE_BOUND")

@pytest.mark.parametrize("bad", [None, True, False, 0, 1.5, "", " ", "PLAN-", "BAD-0000000000000000", "plan-0000000000000000", "PLAN-000000000000000G", "PLAN-ABCDEFABCDEFABCD", "PLAN-000000000000000", "PLAN-00000000000000000", "PLAN-0000000000000000x"])
def test_complete_plan_id_matrix(bad: object):
    d = make_decision(chain()); p = executive_planning_engine.build_plan("x", ("y",), d, planned_at=STAMP)
    err("INVALID_PLAN_ID", lambda: ExecutivePlanningResult(bad, p.planned_at, p.plan_intent, p.plan_steps, d, p.evidence_references, p.status))  # type: ignore[arg-type]

@pytest.mark.parametrize("bad", [None, [], ["step"], "step", b"step", {"step"}, {"step": 1}, 7, 1.5, True, False, ()])
def test_complete_steps_collection_matrix(bad: object):
    err("INVALID_PLAN_STEPS", lambda: executive_planning_engine.build_plan("x", bad, make_decision(chain()), planned_at=STAMP))  # type: ignore[arg-type]

@pytest.mark.parametrize("bad", [None, "decision", b"decision", [], (), {}, set(), 7, 1.5, True, False, object()])
def test_complete_decision_type_matrix(bad: object):
    err("INVALID_DECISION_TYPE", lambda: executive_planning_engine.build_plan("x", ("y",), bad, planned_at=STAMP))  # type: ignore[arg-type]

def test_timestamp_matrix_and_state_surface():
    utc = executive_planning_engine.build_plan("x", ("y",), make_decision(chain()), planned_at=STAMP)
    assert utc.planned_at == STAMP and utc.planned_at.utcoffset() == timedelta(0)
    non_utc_stamp = datetime(2026, 9, 1, tzinfo=timezone(timedelta(hours=2)))
    result = executive_planning_engine.build_plan("x", ("y",), make_decision(chain()), planned_at=non_utc_stamp)
    assert result.planned_at.utcoffset() == timedelta(hours=2)
    automatic = executive_planning_engine.build_plan("x", ("y",), make_decision(chain()))
    assert automatic.planned_at.tzinfo is not None and automatic.planned_at.utcoffset() is not None
    for name in ("_state", "_state_lock", "_active_plans", "cache", "_cache", "history", "_history", "registry", "_registry", "_lock", "_instance"):
        assert not hasattr(executive_planning_engine, name)

def test_engine_remains_stateless_before_and_after_multiple_builds():
    forbidden = ("_state", "_state_lock", "_active_plans", "cache", "_cache", "history", "_history", "registry", "_registry", "_lock", "_instance")
    before = dict(vars(executive_planning_engine))
    for name in forbidden:
        assert not hasattr(executive_planning_engine, name)
    plans = [
        executive_planning_engine.build_plan(f"intent-{suffix}", ("step",), make_decision(chain(f"request-{suffix}")), planned_at=STAMP)
        for suffix in ("a", "b", "c")
    ]
    assert len({plan.plan_id for plan in plans}) == 3
    after = dict(vars(executive_planning_engine))
    assert after == before
    for name in forbidden:
        assert not hasattr(executive_planning_engine, name)
    assert not any(value is plans[0] or value in plans for value in after.values())
    assert not any(isinstance(value, (dict, list, tuple, set)) and any("PLAN-" in str(item) for item in value) for value in after.values())

def test_status_matrix_rejects_both_evidence_mismatches():
    no_evidence = executive_planning_engine.build_plan("x", ("y",), make_decision(chain()), planned_at=STAMP)
    assert no_evidence.status == "NO_EVIDENCE"
    err("INVALID_PLAN_STATUS", lambda: ExecutivePlanningResult(no_evidence.plan_id, no_evidence.planned_at, no_evidence.plan_intent, no_evidence.plan_steps, no_evidence.decision, no_evidence.evidence_references, "EVIDENCE_BOUND"))
    evidence = ev()
    evidence_bound = executive_planning_engine.build_plan("x", ("y",), make_decision(chain("request-a", evidence)), planned_at=STAMP)
    assert evidence_bound.status == "EVIDENCE_BOUND"
    err("INVALID_PLAN_STATUS", lambda: ExecutivePlanningResult(evidence_bound.plan_id, evidence_bound.planned_at, evidence_bound.plan_intent, evidence_bound.plan_steps, evidence_bound.decision, evidence_bound.evidence_references, "NO_EVIDENCE"))

@pytest.mark.parametrize("field,replacement", [
    ("evidence_id", "e-mut"), ("source_id", "source-mut"), ("source_type", "api"),
    ("source_locator", "repo://mut"), ("citation_locator", "page:9"),
    ("content_sha3_512", "0" * 128), ("authorization_receipt_ref", "receipt-mut"),
    ("retrieved_at", datetime(2026, 9, 1, tzinfo=timezone.utc)), ("source_version", "v2"),
])
def test_provenance_field_matrix(field: str, replacement: object):
    a, b = ev(), ev("e-b", "second")
    decision = make_decision(chain("request-a", a, b))
    plan = executive_planning_engine.build_plan("x", ("y",), decision, planned_at=STAMP)
    mutated = replace(plan.evidence_references[0], **{field: replacement})
    refs = (mutated, plan.evidence_references[1])
    err("EVIDENCE_REFERENCE_MISMATCH", lambda: ExecutivePlanningResult(plan.plan_id, plan.planned_at, plan.plan_intent, plan.plan_steps, decision, refs, plan.status))

def test_reference_type_matrix_list_and_wrong_element():
    item = ev(); decision = make_decision(chain("request-a", item)); plan = executive_planning_engine.build_plan("x", ("y",), decision, planned_at=STAMP)
    err("INVALID_PLAN_REFERENCE_TYPE", lambda: ExecutivePlanningResult(plan.plan_id, plan.planned_at, plan.plan_intent, plan.plan_steps, decision, cast(Any, list(plan.evidence_references)), plan.status))
    err("INVALID_PLAN_REFERENCE_TYPE", lambda: ExecutivePlanningResult(plan.plan_id, plan.planned_at, plan.plan_intent, plan.plan_steps, decision, cast(Any, (plan.evidence_references[0], object())), plan.status))

def test_authority_method_absence_complete():
    result = executive_planning_engine.build_plan("x", ("y",), make_decision(chain()), planned_at=STAMP)
    for name in ("execute", "dispatch", "approve", "authorize", "release", "pay", "transfer", "commit", "persist", "learn", "get_plan_state", "generate_enterprise_plan"):
        assert not hasattr(executive_planning_engine, name)
        assert not hasattr(result, name)

class SecretObject:
    def __str__(self) -> str: return "WILSY-SECRET-PLANNING-SENTINEL"
    def __repr__(self) -> str: return "WILSY-SECRET-PLANNING-SENTINEL"

@pytest.mark.parametrize("code,call", [
    ("INVALID_PLAN_INTENT", lambda: executive_planning_engine.build_plan(cast(Any, SecretObject()), ("x",), make_decision(chain()), planned_at=STAMP)),
    ("INVALID_DECISION_TYPE", lambda: executive_planning_engine.build_plan("x", ("y",), cast(Any, SecretObject()), planned_at=STAMP)),
    ("INVALID_PLANNED_AT", lambda: executive_planning_engine.build_plan("x", ("y",), make_decision(chain()), planned_at=cast(Any, SecretObject()))),
    ("INVALID_PLAN_STEP", lambda: executive_planning_engine.build_plan("x", cast(Any, (SecretObject(),)), make_decision(chain()), planned_at=STAMP)),
])
def test_privacy_non_echo(code: str, call: Any):
    with pytest.raises(ExecutivePlanningError) as caught: call()
    assert str(caught.value) == code
    assert "WILSY-SECRET-PLANNING-SENTINEL" not in str(caught.value)

def test_source_boundary_is_synthetic_free():
    from pathlib import Path
    source = Path(__file__).parents[2] / "tools/eos/executive/intelligence/executive_planning_engine.py"
    text = source.read_text()
    for token in ("threading", "uuid", "random", "PLAN_GENERATED", "projected_domains_affected", "_active_plans", "generate_enterprise_plan", "get_plan_state", "TODO", "FIXME", "NotImplemented"):
        assert token not in text
# ARTIFACT: test_executive_planning_engine.py
# VERSION: v1.0.0-WILSY-EXECUTIVE-PLANNING-CERT
# PRODUCTION UNDER CERTIFICATION: tools/eos/executive/intelligence/executive_planning_engine.py
# PRODUCTION VERSION: v1.0.0-WILSY-EXECUTIVE-PLANNING-EVIDENCE
# PRODUCTION SHA3-512: 41f0f19a3dc9ce4b3ad27c762d8943167d47944fe18cedb87e0bda5a1ba63335f323de01ebc8f244fc8ad84efca422473352abe393ce0a45212f5c0a11aeeff6
# AUTHORITY BOUNDARY: certificate proves advisory planning behavior only and grants no authority.
# TENANT POSTURE: tenant and principal identity must derive only through the validated Decision -> Reasoning -> Context -> KernelBootstrapRequest chain.
# EVIDENCE POSTURE: NO EVIDENCE = NO FACT; certificate proves Planning creates no evidence and preserves exact decision evidence references.
# REASONING POSTURE: Planning accepts no independent reasoning authority; reasoning provenance is inherited only through the validated decision chain.
# DECISION POSTURE: ExecutiveDecisionResult is the sole upstream decision/provenance basis and grants no approval or execution authority.
# PLANNING POSTURE: caller-supplied planning metadata is advisory and inert; no workflow, approval, outcome, or execution is manufactured.
# FAIL-CLOSED POSTURE: malformed identities, timestamps, steps, status, deterministic IDs, or provenance must reject with stable non-echoing errors.
# RETRIEVAL AUTHORITY: NONE
# MODEL AUTHORITY: NONE
# EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN CERTIFICATE
