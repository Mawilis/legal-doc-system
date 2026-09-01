"""WILSY OS direct certificate for evidence-bound executive decisions.

TITLE: WILSY Executive Evidence-Bound Decision Certificate
VERSION: v1.0.0-WILSY-EXECUTIVE-DECISION-CERT
AUTHORITY: Wilsy OS Core Governance; Kennel EOS sovereign truth
EPITOME: Proves decisions preserve explicit reasoning evidence without manufacturing authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_executive_decision_engine.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.0 establishes direct immutable decision-envelope certification.
COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY: Stable errors and identifiers never echo sensitive values.
TENANT BOUNDARY: Identity derives only through reasoning/context/bootstrap.
AUTHORITY BOUNDARY: Advisory evidence envelope; no authorization or execution authority.
EVIDENCE BOUNDARY: NO EVIDENCE = NO FACT; no evidence is retrieved or created.
REASONING BOUNDARY: Frozen ExecutiveReasoningResult is the sole reasoning input.
DECISION BOUNDARY: Decision metadata is non-authoritative caller input.
RETRIEVAL BOUNDARY: None.
MODEL BOUNDARY: None.
EXECUTION BOUNDARY: None.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from hashlib import sha3_512
import re
from typing import Any
import pytest

from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest
from tools.eos.executive.intelligence.executive_context_engine import ExecutiveContext, ExecutiveEvidence
from tools.eos.executive.intelligence.executive_reasoning_engine import ExecutiveReasoningEvidenceReference, executive_reasoning_engine
from tools.eos.executive.intelligence.executive_decision_engine import VERSION, ExecutiveDecisionEngine, ExecutiveDecisionError, ExecutiveDecisionResult, executive_decision_engine

STAMP = datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc)

def request(request_id: str = "request-a") -> KernelBootstrapRequest:
    return KernelBootstrapRequest("tenant-a", "principal-a", request_id, "corr-a")

def evidence(evidence_id: str = "evidence-a", content: str = "fact", source_id: str = "source-a") -> ExecutiveEvidence:
    return ExecutiveEvidence(evidence_id, "tenant-a", "principal-a", "request-a", source_id, "document", f"repo://{source_id}", "page:1", content, sha3_512(content.encode()).hexdigest(), f"receipt-{evidence_id}", STAMP, None)

def context(*items: ExecutiveEvidence, req: KernelBootstrapRequest | None = None) -> ExecutiveContext:
    return ExecutiveContext(req or request(), tuple(items), STAMP)

def reasoning(*items: ExecutiveEvidence, req: KernelBootstrapRequest | None = None):
    return executive_reasoning_engine.evaluate_query("q", context(*items, req=req), evaluated_at=STAMP)

def reference(item: ExecutiveEvidence) -> ExecutiveReasoningEvidenceReference:
    return ExecutiveReasoningEvidenceReference(item.evidence_id, item.source_id, item.source_type, item.source_locator, item.citation_locator, item.content_sha3_512, item.authorization_receipt_ref, item.retrieved_at, item.source_version)

def decision_values(r: Any, **changes: Any) -> dict[str, Any]:
    intent, domain, at = "assess", "operations", STAMP
    material = "\x1f".join((r.request_id, r.evaluation_id, sha3_512(intent.encode()).hexdigest(), sha3_512(domain.encode()).hexdigest(), at.isoformat())).encode()
    values = {"decision_id": "DEC-" + sha3_512(material).hexdigest()[:16], "evaluated_at": at, "decision_intent": intent, "target_domain": domain, "reasoning": r, "evidence_references": r.evidence_references, "status": "NO_EVIDENCE" if r.evidence_count == 0 else "EVIDENCE_BOUND"}
    values.update(changes)
    return values

def error(code: str, fn: Any) -> None:
    with pytest.raises(ExecutiveDecisionError) as caught:
        fn()
    assert str(caught.value) == code

def valid_decision_id(intent: str = "assess", domain: str = "operations", r: Any | None = None, at: datetime = STAMP) -> str:
    r = r or reasoning()
    material = "\x1f".join((r.request_id, r.evaluation_id, sha3_512(intent.encode()).hexdigest(), sha3_512(domain.encode()).hexdigest(), at.isoformat())).encode()
    return "DEC-" + sha3_512(material).hexdigest()[:16]

def test_version_and_valid_empty_decision() -> None:
    assert VERSION == "v1.0.0-WILSY-EXECUTIVE-DECISION-EVIDENCE"
    assert isinstance(executive_decision_engine, ExecutiveDecisionEngine)
    r = reasoning(); result = executive_decision_engine.evaluate_decision("assess", "operations", r, evaluated_at=STAMP)
    assert isinstance(result, ExecutiveDecisionResult)
    assert (result.decision_intent, result.target_domain, result.evaluated_at, result.status, result.evidence_references, result.evidence_count) == ("assess", "operations", STAMP, "NO_EVIDENCE", (), 0)
    assert (result.tenant_id, result.principal_id, result.request_id, result.correlation_id) == ("tenant-a", "principal-a", "request-a", "corr-a")

def test_valid_evidence_and_authority_inheritance() -> None:
    item = evidence(); r = reasoning(item)
    result = executive_decision_engine.evaluate_decision("assess", "operations", r, evaluated_at=STAMP)
    assert result.evidence_references == (reference(item),)
    assert (result.tenant_id, result.principal_id, result.request_id, result.correlation_id, result.evidence_count, result.status) == (r.tenant_id, r.principal_id, r.request_id, r.correlation_id, 1, "EVIDENCE_BOUND")

@pytest.mark.parametrize("bad", [None, 7, True, False, b"x", [], {}, (), "", " ", "\t"])
def test_decision_intent_validation(bad: object) -> None:
    error("INVALID_DECISION_INTENT", lambda: executive_decision_engine.evaluate_decision(bad, "operations", reasoning(), evaluated_at=STAMP))  # type: ignore[arg-type]

@pytest.mark.parametrize("bad", [None, 7, True, b"x", [], {}, (), "", " "])
def test_target_domain_validation(bad: object) -> None:
    error("INVALID_TARGET_DOMAIN", lambda: executive_decision_engine.evaluate_decision("assess", bad, reasoning(), evaluated_at=STAMP))  # type: ignore[arg-type]

@pytest.mark.parametrize("bad", [None, "x", {}, [], (), object(), True, 7])
def test_reasoning_type_validation(bad: object) -> None:
    error("INVALID_REASONING_TYPE", lambda: executive_decision_engine.evaluate_decision("assess", "operations", bad, evaluated_at=STAMP))  # type: ignore[arg-type]

def test_omitted_and_aware_timestamp() -> None:
    assert executive_decision_engine.evaluate_decision("assess", "operations", reasoning()).evaluated_at.tzinfo is not None
    assert executive_decision_engine.evaluate_decision("assess", "operations", reasoning(), evaluated_at=STAMP).evaluated_at == STAMP

@pytest.mark.parametrize("bad", [datetime(2026, 9, 1, 10), "2026-09-01", 7, 1.5, True, object()])
def test_timestamp_validation(bad: object) -> None:
    error("INVALID_EVALUATED_AT", lambda: executive_decision_engine.evaluate_decision("assess", "operations", reasoning(), evaluated_at=bad))  # type: ignore[arg-type]

@pytest.mark.parametrize("bad", ["", "DEC-", "dec-0000000000000000", "DEC-000000000000000G", "DEC-000000000000000A", "DEC-000000000000000", "DEC-00000000000000000", None, 7, True])
def test_direct_decision_id_validation(bad: object) -> None:
    r = reasoning(); error("INVALID_DECISION_ID", lambda: ExecutiveDecisionResult(**decision_values(r, decision_id=bad)))  # type: ignore[arg-type]

def test_direct_cryptographic_id_mismatch() -> None:
    r = reasoning(); error("INVALID_DECISION_ID", lambda: ExecutiveDecisionResult(**decision_values(r, decision_id="DEC-0000000000000000")))

def test_deterministic_id_binding() -> None:
    r = reasoning(); one = executive_decision_engine.evaluate_decision("assess", "operations", r, evaluated_at=STAMP); two = executive_decision_engine.evaluate_decision("assess", "operations", r, evaluated_at=STAMP)
    assert one.decision_id == two.decision_id and re.fullmatch(r"DEC-[0-9a-f]{16}", one.decision_id)
    assert one.decision_id != executive_decision_engine.evaluate_decision("other", "operations", r, evaluated_at=STAMP).decision_id
    assert one.decision_id != executive_decision_engine.evaluate_decision("assess", "financial", r, evaluated_at=STAMP).decision_id
    assert one.decision_id != executive_decision_engine.evaluate_decision("assess", "operations", reasoning(req=request("request-b")), evaluated_at=STAMP).decision_id
    assert one.decision_id != executive_decision_engine.evaluate_decision("assess", "operations", replace(r, evaluation_id="REASON-0123456789abcdee"), evaluated_at=STAMP).decision_id
    assert all(raw not in one.decision_id for raw in ("assess", "operations", r.request_id, r.evaluation_id))

def test_status_and_reference_contracts() -> None:
    r = reasoning(); error("INVALID_DECISION_STATUS", lambda: ExecutiveDecisionResult(**decision_values(r, status="EVIDENCE_BOUND")))
    item = evidence(); rb = reasoning(item); vals = decision_values(rb)
    error("INVALID_DECISION_STATUS", lambda: ExecutiveDecisionResult(**{**vals, "status": "NO_EVIDENCE"}))
    error("INVALID_DECISION_REFERENCE_TYPE", lambda: ExecutiveDecisionResult(**{**decision_values(r), "evidence_references": []}))
    error("INVALID_DECISION_REFERENCE_TYPE", lambda: ExecutiveDecisionResult(**{**decision_values(r), "evidence_references": (object(),)}))

def test_provenance_count_order_and_field_mismatch() -> None:
    a, b = evidence(), evidence("evidence-b", "second", "source-b"); r = reasoning(a, b); ra, rb = reference(a), reference(b); vals = decision_values(r)
    for refs in [(), (ra, rb, ra), (rb, ra), (ra, ra)]: error("EVIDENCE_REFERENCE_MISMATCH", lambda refs=refs: ExecutiveDecisionResult(**{**vals, "evidence_references": refs}))
    for field in ("evidence_id", "source_id", "source_type", "source_locator", "citation_locator", "content_sha3_512", "authorization_receipt_ref", "retrieved_at", "source_version"):
        changed = replace(ra, **{field: datetime(2026, 9, 2, tzinfo=timezone.utc) if field == "retrieved_at" else "other"})
        error("EVIDENCE_REFERENCE_MISMATCH", lambda changed=changed: ExecutiveDecisionResult(**{**vals, "evidence_references": (changed, rb)}))

def test_immutability_statelessness_and_authority() -> None:
    result = executive_decision_engine.evaluate_decision("approve payment", "financial", reasoning(), evaluated_at=STAMP)
    with pytest.raises(FrozenInstanceError): result.status = "EVIDENCE_BOUND"  # type: ignore[misc]
    with pytest.raises(AttributeError): result.extra = 1  # type: ignore[attr-defined]
    for name in ("approve", "authorize", "execute", "dispatch", "release", "pay", "transfer", "get_decision", "export_decision_state", "decision_cache"):
        assert not hasattr(result, name) and not hasattr(executive_decision_engine, name)
    assert not hasattr(executive_decision_engine, "_state")

def test_privacy_error_hygiene() -> None:
    secret = "TENANT_SECRET_QUERY_SECRET_SOURCE_SECRET_RECEIPT_SECRET"
    item = evidence(content=secret, source_id=secret); r = reasoning(item)
    error("INVALID_DECISION_ID", lambda: ExecutiveDecisionResult(**decision_values(r, decision_id="DEC-0000000000000000", decision_intent=secret, target_domain=secret)))

# ARTIFACT: test_executive_decision_engine.py
# VERSION: v1.0.0-WILSY-EXECUTIVE-DECISION-CERT
# AUTHORITY BOUNDARY: direct evidence-bound decision certification only; no authority grant.
# TENANT POSTURE: identity derives only through ExecutiveReasoningResult/context/bootstrap.
# EVIDENCE POSTURE: NO EVIDENCE = NO FACT; validated references only.
# RETRIEVAL AUTHORITY: NONE
# MODEL AUTHORITY: NONE
# EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# FAIL-CLOSED POSTURE: malformed inputs and provenance fail closed.
# END OF WILSY OS SOVEREIGN ARTIFACT
