"""WILSY OS direct certificate for evidence-bound executive reasoning.

TITLE: WILSY Executive Evidence-Bound Reasoning Certificate
VERSION: v1.0.2-WILSY-EXECUTIVE-REASONING-CERT
AUTHORITY: Wilsy OS Core Governance; Kennel EOS sovereign truth
EPITOME: Proves reasoning accepts only explicit ExecutiveContext evidence and never manufactures facts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_executive_reasoning_engine.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.2 closes second independent-review gaps in direct matrices, malformed IDs, reference shape/order, ID content non-materiality, privacy construction, and authority assertions.
COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY: Identifiers and errors exclude raw query/evidence and authority values.
TENANT BOUNDARY: KernelBootstrapRequest inside ExecutiveContext is the sole authority envelope.
AUTHORITY BOUNDARY: No authentication, authorization, retrieval, model, execution, or financial authority.
EVIDENCE BOUNDARY: References copy explicit provenance only; NO EVIDENCE = NO FACT.
RETRIEVAL BOUNDARY: No retrieval or private-evidence selection occurs.
MODEL BOUNDARY: No model is invoked or represented.
EXECUTION BOUNDARY: Results cannot dispatch, approve, release, pay, or execute.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive financial execution authority.
"""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from hashlib import sha3_512
import re
from typing import Any
import pytest

from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest
from tools.eos.executive.intelligence.executive_context_engine import ExecutiveContext, ExecutiveEvidence
from tools.eos.executive.intelligence.executive_reasoning_engine import (
    VERSION, ExecutiveReasoningEngine, ExecutiveReasoningError,
    ExecutiveReasoningEvidenceReference, ExecutiveReasoningResult,
    executive_reasoning_engine,
)

TEST_VERSION = "v1.0.2-WILSY-EXECUTIVE-REASONING-CERT"
UTC = timezone.utc
STAMP = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)

def req() -> KernelBootstrapRequest:
    return KernelBootstrapRequest("tenant-a", "principal-a", "request-a", "corr-a")

def ev(evidence_id: str = "evidence-a", source_id: str = "source-a", content: str = "explicit fact", source_version: str | None = None) -> ExecutiveEvidence:
    return ExecutiveEvidence(evidence_id, "tenant-a", "principal-a", "request-a", source_id, "document", f"repo://document/{source_id}", "page:1", content, sha3_512(content.encode()).hexdigest(), f"receipt-{evidence_id}", STAMP, source_version)

def ctx(*items: ExecutiveEvidence) -> ExecutiveContext:
    return ExecutiveContext(req(), tuple(items), STAMP)

def code(expected: str, fn: Any) -> None:
    with pytest.raises(ExecutiveReasoningError, match=f"^{expected}$"):
        fn()

def direct_kwargs() -> dict[str, Any]:
    item = ev()
    ref = ExecutiveReasoningEvidenceReference(item.evidence_id, item.source_id, item.source_type, item.source_locator, item.citation_locator, item.content_sha3_512, item.authorization_receipt_ref, item.retrieved_at, item.source_version)
    return {"evaluation_id": "REASON-0123456789abcdef", "evaluated_at": STAMP, "query_intent": "q", "context": ctx(item), "evidence_references": (ref,), "status": "EVIDENCE_BOUND"}

def test_version_exports_and_empty_contract() -> None:
    assert TEST_VERSION == "v1.0.2-WILSY-EXECUTIVE-REASONING-CERT"
    assert VERSION == "v1.0.1-WILSY-EXECUTIVE-REASONING-EVIDENCE"
    assert isinstance(executive_reasoning_engine, ExecutiveReasoningEngine)
    result = executive_reasoning_engine.evaluate_query("What is available?", ctx(), evaluated_at=STAMP)
    assert isinstance(result, ExecutiveReasoningResult)
    assert (result.status, result.evidence_references, result.evidence_count) == ("NO_EVIDENCE", (), 0)
    assert (result.tenant_id, result.principal_id, result.request_id, result.correlation_id) == ("tenant-a", "principal-a", "request-a", "corr-a")
    assert result.evaluated_at == STAMP
    assert result.query_intent == "What is available?"
    for name in ("confidence_score", "confidence", "risk_assessment", "risk_level", "impact_score", "impact_level", "recommendation", "decision", "answer", "conclusion", "legal_conclusion", "cognitive_path", "model_name", "model_output"):
        assert not hasattr(result, name)

def test_evidence_bound_provenance_and_order() -> None:
    a, b = ev(), ev("evidence-b", "source-b", "second fact", "v2")
    result = executive_reasoning_engine.evaluate_query("Assess", ctx(a, b), evaluated_at=STAMP)
    assert result.status == "EVIDENCE_BOUND"
    assert [r.evidence_id for r in result.evidence_references] == ["evidence-a", "evidence-b"]
    ref = result.evidence_references[1]
    assert (ref.source_id, ref.source_type, ref.source_locator, ref.citation_locator, ref.content_sha3_512, ref.authorization_receipt_ref, ref.retrieved_at, ref.source_version) == (b.source_id, b.source_type, b.source_locator, b.citation_locator, b.content_sha3_512, b.authorization_receipt_ref, b.retrieved_at, "v2")
    assert result.evidence_references[0].source_version is None

@pytest.mark.parametrize("bad", ["", "   ", None, b"x", True, 7, object()])
def test_query_validation(bad: object) -> None:
    code("INVALID_QUERY_INTENT", lambda: executive_reasoning_engine.evaluate_query(bad, ctx()))  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", ["\t", "\n", "\t\n", bytearray(b"x"), [], {}, ()])
def test_query_validation_additional_types_and_whitespace(bad: object) -> None:
    code("INVALID_QUERY_INTENT", lambda: executive_reasoning_engine.evaluate_query(bad, ctx()))  # type: ignore[arg-type]


def test_query_preserves_nonblank_surrounding_whitespace() -> None:
    query = "  assess evidence  "
    assert executive_reasoning_engine.evaluate_query(query, ctx(), evaluated_at=STAMP).query_intent == query

def test_engine_omitted_timestamp_is_aware() -> None:
    result = executive_reasoning_engine.evaluate_query("q", ctx(), evaluated_at=None)
    assert result.evaluated_at.tzinfo is not None and result.evaluated_at.utcoffset() is not None

@pytest.mark.parametrize("bad", [{}, None, [], object()])
def test_context_validation(bad: object) -> None:
    code("INVALID_CONTEXT_TYPE", lambda: executive_reasoning_engine.evaluate_query("q", bad))  # type: ignore[arg-type]

@pytest.mark.parametrize("bad", [datetime(2026, 1, 1), "2026-01-01"])
def test_timestamp_validation(bad: object) -> None:
    code("INVALID_EVALUATED_AT", lambda: executive_reasoning_engine.evaluate_query("q", ctx(), evaluated_at=bad))  # type: ignore[arg-type]

def test_result_direct_invariants_and_immutability() -> None:
    result = executive_reasoning_engine.evaluate_query("q", ctx(ev()), evaluated_at=STAMP)
    with pytest.raises(FrozenInstanceError): result.status = "NO_EVIDENCE"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError): result.evidence_references = ()  # type: ignore[misc]
    with pytest.raises(AttributeError): result.extra = 1  # type: ignore[attr-defined]
    ref = next(iter(result.evidence_references))
    with pytest.raises(FrozenInstanceError): ref.source_id = "x"  # type: ignore[misc]
    code("INVALID_REASONING_REFERENCE_TYPE", lambda: ExecutiveReasoningResult(result.evaluation_id, STAMP, "q", result.context, list(result.evidence_references), result.status))  # type: ignore[arg-type]
    code("EVIDENCE_REFERENCE_MISMATCH", lambda: ExecutiveReasoningResult(result.evaluation_id, STAMP, "q", result.context, (replace(ref, source_id="other"),), result.status))
    code("INVALID_REASONING_STATUS", lambda: ExecutiveReasoningResult(result.evaluation_id, STAMP, "q", result.context, result.evidence_references, "SUCCESS"))


def test_direct_evidence_bound_result_and_no_evidence_result() -> None:
    item = ev()
    context = ctx(item)
    reference = ExecutiveReasoningEvidenceReference(item.evidence_id, item.source_id, item.source_type, item.source_locator, item.citation_locator, item.content_sha3_512, item.authorization_receipt_ref, item.retrieved_at, item.source_version)
    bound = ExecutiveReasoningResult("REASON-0123456789abcdef", STAMP, "q", context, (reference,), "EVIDENCE_BOUND")
    assert (bound.evaluation_id, bound.evaluated_at, bound.query_intent, bound.context, bound.evidence_references, bound.status) == ("REASON-0123456789abcdef", STAMP, "q", context, (reference,), "EVIDENCE_BOUND")
    assert (bound.tenant_id, bound.principal_id, bound.request_id, bound.correlation_id, bound.evidence_count) == ("tenant-a", "principal-a", "request-a", "corr-a", 1)
    empty = ExecutiveReasoningResult("REASON-0123456789abcdef", STAMP, "q", ctx(), (), "NO_EVIDENCE")
    assert (empty.tenant_id, empty.principal_id, empty.request_id, empty.correlation_id, empty.status, empty.evidence_references, empty.evidence_count, empty.query_intent, empty.evaluated_at) == ("tenant-a", "principal-a", "request-a", "corr-a", "NO_EVIDENCE", (), 0, "q", STAMP)

@pytest.mark.parametrize("field", ["evaluation_id", "evaluated_at", "query_intent", "context", "evidence_references", "status"])
def test_direct_constructor_preserves_every_field(field: str) -> None:
    item = ev(); context = ctx(item)
    reference = ExecutiveReasoningEvidenceReference(item.evidence_id, item.source_id, item.source_type, item.source_locator, item.citation_locator, item.content_sha3_512, item.authorization_receipt_ref, item.retrieved_at, item.source_version)
    values = {"evaluation_id": "REASON-0123456789abcdef", "evaluated_at": STAMP, "query_intent": "q", "context": context, "evidence_references": (reference,), "status": "EVIDENCE_BOUND"}
    assert getattr(ExecutiveReasoningResult(**values), field) == values[field]

@pytest.mark.parametrize("bad", ["", " ", "   ", "\t", "\n", "\t\n", None, 7, True, False, b"x", bytearray(b"x"), object(), [], {}, ()])
def test_direct_query_matrix(bad: object) -> None:
    values = direct_kwargs(); values["query_intent"] = bad
    with pytest.raises(ExecutiveReasoningError) as caught:
        ExecutiveReasoningResult(**values)  # type: ignore[arg-type]
    assert str(caught.value) == "INVALID_QUERY_INTENT"

@pytest.mark.parametrize("bad", [None, {}, [], (), "tenant-a", 7, True, object()])
def test_direct_context_matrix(bad: object) -> None:
    values = direct_kwargs(); values["context"] = bad
    with pytest.raises(ExecutiveReasoningError) as caught:
        ExecutiveReasoningResult(**values)  # type: ignore[arg-type]
    assert str(caught.value) == "INVALID_CONTEXT_TYPE"

@pytest.mark.parametrize("bad", [datetime(2026, 9, 1, 10), None, "2026-09-01T10:00:00Z", 7, 1.5, True, object()])
def test_direct_timestamp_matrix(bad: object) -> None:
    values = direct_kwargs(); values["evaluated_at"] = bad
    with pytest.raises(ExecutiveReasoningError) as caught:
        ExecutiveReasoningResult(**values)  # type: ignore[arg-type]
    assert str(caught.value) == "INVALID_EVALUATED_AT"

@pytest.mark.parametrize("bad", ["", " ", "REASON-", "REASON-0123456789abcde", "reason-0123456789abcdef", "REASON-0123456789ABCDEf", "REASON-0123456789abcdeg", "OTHER-0123456789abcdef", None, 7, True, b"x"])
def test_direct_evaluation_id_matrix(bad: object) -> None:
    code("INVALID_EVALUATION_ID", lambda: ExecutiveReasoningResult(bad, STAMP, "q", ctx(), (), "NO_EVIDENCE"))  # type: ignore[arg-type]

@pytest.mark.parametrize("bad", ["REASON-0123456789abcdef0", "REASON-0123456789ABCDEF"])
def test_canonical_direct_id_rejections(bad: str) -> None:
    code("INVALID_EVALUATION_ID", lambda: ExecutiveReasoningResult(bad, STAMP, "q", ctx(), (), "NO_EVIDENCE"))

@pytest.mark.parametrize("bad", [None, 7, True, False, b"x", bytearray(b"x"), object(), [], {}, (), ""])
def test_engine_query_matrix(bad: object) -> None:
    code("INVALID_QUERY_INTENT", lambda: executive_reasoning_engine.evaluate_query(bad, ctx(), evaluated_at=STAMP))  # type: ignore[arg-type]

@pytest.mark.parametrize("bad", [datetime(2026, 9, 1), datetime(2026, 9, 1, tzinfo=UTC).replace(tzinfo=None), "2026-09-01", 7])
def test_engine_timestamp_matrix(bad: object) -> None:
    code("INVALID_EVALUATED_AT", lambda: executive_reasoning_engine.evaluate_query("q", ctx(), evaluated_at=bad))  # type: ignore[arg-type]

def test_reference_shape_status_and_order_fail_closed() -> None:
    item = ev(); context = ctx(item)
    ref = ExecutiveReasoningEvidenceReference(item.evidence_id, item.source_id, item.source_type, item.source_locator, item.citation_locator, item.content_sha3_512, item.authorization_receipt_ref, item.retrieved_at, item.source_version)
    base = ("REASON-0123456789abcdef", STAMP, "q", context)
    code("INVALID_REASONING_REFERENCE_TYPE", lambda: ExecutiveReasoningResult(*base, [ref], "EVIDENCE_BOUND"))  # type: ignore[arg-type]
    code("INVALID_REASONING_STATUS", lambda: ExecutiveReasoningResult(*base, (ref,), "NO_EVIDENCE"))
    code("EVIDENCE_REFERENCE_MISMATCH", lambda: ExecutiveReasoningResult(*base, (), "EVIDENCE_BOUND"))
    code("EVIDENCE_REFERENCE_MISMATCH", lambda: ExecutiveReasoningResult(*base, (ref, ref), "EVIDENCE_BOUND"))

@pytest.mark.parametrize("kind", ["generator", "set", "object", "evidence"])
def test_reference_type_matrix(kind: str) -> None:
    item = ev(); context = ctx(item)
    ref = ExecutiveReasoningEvidenceReference(item.evidence_id, item.source_id, item.source_type, item.source_locator, item.citation_locator, item.content_sha3_512, item.authorization_receipt_ref, item.retrieved_at, item.source_version)
    refs: object = {"generator": iter((ref,)), "set": {ref}, "object": (object(),), "evidence": (item,)}[kind]
    code("INVALID_REASONING_REFERENCE_TYPE", lambda: ExecutiveReasoningResult("REASON-0123456789abcdef", STAMP, "q", context, refs, "EVIDENCE_BOUND"))  # type: ignore[arg-type]

@pytest.mark.parametrize("field", ["evidence_id", "source_id", "source_type", "source_locator", "citation_locator", "content_sha3_512", "authorization_receipt_ref", "retrieved_at", "source_version"])
def test_each_provenance_field_mismatch_is_rejected(field: str) -> None:
    item = ev(); context = ctx(item)
    ref = ExecutiveReasoningEvidenceReference(item.evidence_id, item.source_id, item.source_type, item.source_locator, item.citation_locator, item.content_sha3_512, item.authorization_receipt_ref, item.retrieved_at, item.source_version)
    changed = replace(ref, **{field: ("other" if field != "retrieved_at" else datetime(2026, 9, 2, tzinfo=UTC))})
    code("EVIDENCE_REFERENCE_MISMATCH", lambda: ExecutiveReasoningResult("REASON-0123456789abcdef", STAMP, "q", context, (changed,), "EVIDENCE_BOUND"))


@pytest.mark.parametrize("bad", ["", " ", "REASON-", "OTHER-0123456789abcdef", "REASON-0123456789ABCDE", "REASON-0123456789abcdeg", None, 7, True, b"x"])
def test_direct_evaluation_id_validation(bad: object) -> None:
    result = executive_reasoning_engine.evaluate_query("q", ctx(), evaluated_at=STAMP)
    code("INVALID_EVALUATION_ID", lambda: ExecutiveReasoningResult(bad, STAMP, "q", result.context, (), "NO_EVIDENCE"))  # type: ignore[arg-type]


def test_evaluation_id_changes_for_timestamp_and_request() -> None:
    first = executive_reasoning_engine.evaluate_query("q", ctx(), evaluated_at=STAMP)
    later = executive_reasoning_engine.evaluate_query("q", ctx(), evaluated_at=datetime(2026, 9, 1, 10, 1, tzinfo=UTC))
    other_request = KernelBootstrapRequest("tenant-a", "principal-a", "request-b", "corr-a")
    other_context = ExecutiveContext(other_request, (), STAMP)
    changed = executive_reasoning_engine.evaluate_query("q", other_context, evaluated_at=STAMP)
    assert first.evaluation_id != later.evaluation_id
    assert first.evaluation_id != changed.evaluation_id
    assert re.fullmatch(r"REASON-[0-9a-f]{16}", first.evaluation_id)

def test_deterministic_ids_and_state_isolation() -> None:
    a, b = ev(), ev("evidence-b", "source-b", "second")
    one = executive_reasoning_engine.evaluate_query("q", ctx(a, b), evaluated_at=STAMP)
    two = executive_reasoning_engine.evaluate_query("q", ctx(a, b), evaluated_at=STAMP)
    assert one.evaluation_id == two.evaluation_id
    assert one.evaluation_id.startswith("REASON-") and len(one.evaluation_id) == 23
    assert one.evaluation_id != executive_reasoning_engine.evaluate_query("other", ctx(a, b), evaluated_at=STAMP).evaluation_id
    assert one.evaluation_id != executive_reasoning_engine.evaluate_query("q", ctx(b, a), evaluated_at=STAMP).evaluation_id
    assert not hasattr(executive_reasoning_engine, "_reasoning_cache")
    assert not hasattr(executive_reasoning_engine, "export_reasoning_state")

def test_evaluation_id_changes_when_evidence_identity_changes() -> None:
    first = executive_reasoning_engine.evaluate_query("q", ctx(ev("evidence-a")), evaluated_at=STAMP)
    changed = executive_reasoning_engine.evaluate_query("q", ctx(ev("evidence-b")), evaluated_at=STAMP)
    assert first.evaluation_id != changed.evaluation_id

def test_evaluation_id_excludes_evidence_content() -> None:
    first = ev("evidence-a", content="first")
    second = ev("evidence-a", content="second")
    assert first.content_sha3_512 != second.content_sha3_512
    assert executive_reasoning_engine.evaluate_query("q", ctx(first), evaluated_at=STAMP).evaluation_id == executive_reasoning_engine.evaluate_query("q", ctx(second), evaluated_at=STAMP).evaluation_id

def test_two_evidence_order_and_duplicate_references_fail_closed() -> None:
    a, b = ev("evidence-a"), ev("evidence-b", "source-b", "second")
    rb = ExecutiveReasoningEvidenceReference(b.evidence_id, b.source_id, b.source_type, b.source_locator, b.citation_locator, b.content_sha3_512, b.authorization_receipt_ref, b.retrieved_at, b.source_version)
    ra = ExecutiveReasoningEvidenceReference(a.evidence_id, a.source_id, a.source_type, a.source_locator, a.citation_locator, a.content_sha3_512, a.authorization_receipt_ref, a.retrieved_at, a.source_version)
    base = ("REASON-0123456789abcdef", STAMP, "q", ctx(a, b))
    code("EVIDENCE_REFERENCE_MISMATCH", lambda: ExecutiveReasoningResult(*base, (rb, ra), "EVIDENCE_BOUND"))
    code("EVIDENCE_REFERENCE_MISMATCH", lambda: ExecutiveReasoningResult(*base, (ra, ra), "EVIDENCE_BOUND"))

def test_state_and_legacy_domain_context_are_absent() -> None:
    assert not hasattr(executive_reasoning_engine, "_state_lock")
    with pytest.raises(TypeError):
        executive_reasoning_engine.evaluate_query("q", ctx(), evaluated_at=STAMP, domain_context={})  # type: ignore[call-arg]

@pytest.mark.parametrize("status", ["SUCCESS", "FAILED", "CANCELLED", None, "NO_EVIDENCE "])
def test_invalid_status_values_fail_closed(status: object) -> None:
    code("INVALID_REASONING_STATUS", lambda: ExecutiveReasoningResult("REASON-0123456789abcdef", STAMP, "q", ctx(), (), status))  # type: ignore[arg-type]

def test_no_authority_expansion_or_content_leakage() -> None:
    secret = "DISTINCTIVE-PRIVATE-MARKER"
    result = executive_reasoning_engine.evaluate_query("q", ctx(ev(content=secret)), evaluated_at=STAMP)
    with pytest.raises(ExecutiveReasoningError) as caught:
        ExecutiveReasoningResult(result.evaluation_id, STAMP, "q", result.context, (replace(result.evidence_references[0], source_id="bad"),), result.status)
    assert str(caught.value) == "EVIDENCE_REFERENCE_MISMATCH" and secret not in str(caught.value)
    for name in ("execute", "dispatch", "approve", "authorize", "release", "pay", "transfer"):
        assert not hasattr(result, name)

@pytest.mark.parametrize("secret", ["QUERY-SECRET", "CONTENT-SECRET", "tenant-secret", "principal-secret", "request-secret", "repo://secret", "receipt-secret"])
def test_privacy_errors_never_echo_sensitive_markers(secret: str) -> None:
    item = ev(content=secret, source_id=secret)
    result = executive_reasoning_engine.evaluate_query("q", ctx(item), evaluated_at=STAMP)
    with pytest.raises(ExecutiveReasoningError) as caught:
        ExecutiveReasoningResult(result.evaluation_id, STAMP, "q", result.context, (replace(result.evidence_references[0], source_id="mismatch"),), result.status)
    assert secret not in str(caught.value)

@pytest.mark.parametrize("field", ["tenant_id", "principal_id", "request_id"])
def test_identity_privacy_on_context_error(field: str) -> None:
    secret = field.upper() + "_SECRET"
    values = {"tenant_id": "tenant-a", "principal_id": "principal-a", "request_id": "request-a", "correlation_id": "corr-a"}
    values[field] = secret
    bad_context = ExecutiveContext(KernelBootstrapRequest(**values), (), STAMP)
    with pytest.raises(ExecutiveReasoningError) as caught:
        ExecutiveReasoningResult("REASON-0123456789abcdef", STAMP, "q", bad_context, [], "NO_EVIDENCE")  # type: ignore[arg-type]
    assert str(caught.value) == "INVALID_REASONING_REFERENCE_TYPE" and secret not in str(caught.value)

def test_query_locator_receipt_and_malformed_id_privacy() -> None:
    query_secret = "QUERY_SECRET"
    item = ev(source_id="LOCATOR_SECRET"); item = replace(item, source_locator="LOCATOR_SECRET", authorization_receipt_ref="RECEIPT_SECRET")
    result = executive_reasoning_engine.evaluate_query(query_secret, ctx(item), evaluated_at=STAMP)
    with pytest.raises(ExecutiveReasoningError) as query_error:
        ExecutiveReasoningResult(result.evaluation_id, STAMP, query_secret, result.context, (replace(result.evidence_references[0], source_id="bad"),), result.status)
    assert str(query_error.value) == "EVIDENCE_REFERENCE_MISMATCH" and query_secret not in str(query_error.value)
    with pytest.raises(ExecutiveReasoningError) as mismatch:
        ExecutiveReasoningResult("REASON-0123456789abcdef0", STAMP, "q", result.context, result.evidence_references, result.status)
    assert str(mismatch.value) == "INVALID_EVALUATION_ID" and all(s not in str(mismatch.value) for s in ("LOCATOR_SECRET", "RECEIPT_SECRET"))

# ARTIFACT: test_executive_reasoning_engine.py
# VERSION: v1.0.2-WILSY-EXECUTIVE-REASONING-CERT
# AUTHORITY BOUNDARY: direct evidence-bound reasoning certification only; no authority grant.
# TENANT POSTURE: authority derives only from ExecutiveContext/KernelBootstrapRequest.
# EVIDENCE POSTURE: NO EVIDENCE = NO FACT; references preserve validated provenance only.
# FAIL-CLOSED POSTURE: malformed query/context/result/reference contracts are rejected.
# RETRIEVAL AUTHORITY: NONE
# MODEL AUTHORITY: NONE
# EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
