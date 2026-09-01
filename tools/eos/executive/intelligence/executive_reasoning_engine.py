"""WILSY OS evidence-bound executive reasoning boundary.

TITLE: WILSY Executive Evidence-Bound Reasoning Engine
VERSION: v1.0.1-WILSY-EXECUTIVE-REASONING-EVIDENCE
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
EPITOME: Deterministic provenance envelope; no semantic conclusions are manufactured.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/executive/intelligence/executive_reasoning_engine.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.1 closes the direct-constructor evaluation-ID format gap by enforcing the canonical lowercase hexadecimal identifier format.
COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY: Raw query, evidence, and authority references never appear in IDs or errors.
TENANT BOUNDARY: Authority derives solely from KernelBootstrapRequest embedded in ExecutiveContext.
AUTHORITY BOUNDARY: No authentication, authorization, retrieval, recommendation, approval, or execution authority.
RETRIEVAL BOUNDARY: No retrieval or private-evidence selection.
MODEL BOUNDARY: No model invocation or manufactured model conclusion.
EXECUTION BOUNDARY: Output is advisory evidence metadata only.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive financial execution authority.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
from tools.eos.executive.intelligence.executive_context_engine import ExecutiveContext

VERSION = "v1.0.1-WILSY-EXECUTIVE-REASONING-EVIDENCE"

class ExecutiveReasoningError(ValueError):
    """Stable fail-closed executive reasoning contract error."""

def _aware(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ExecutiveReasoningError("INVALID_EVALUATED_AT")
    return value

@dataclass(frozen=True, slots=True)
class ExecutiveReasoningEvidenceReference:
    """Immutable provenance metadata copied from valid ExecutiveEvidence."""
    evidence_id: str
    source_id: str
    source_type: str
    source_locator: str
    citation_locator: str
    content_sha3_512: str
    authorization_receipt_ref: str
    retrieved_at: datetime
    source_version: str | None

def _validate_result(result: "ExecutiveReasoningResult") -> None:
    if (not isinstance(result.evaluation_id, str) or len(result.evaluation_id) != 23 or
            not result.evaluation_id.startswith("REASON-") or
            any(char not in "0123456789abcdef" for char in result.evaluation_id[7:])):
        raise ExecutiveReasoningError("INVALID_EVALUATION_ID")
    _aware(result.evaluated_at)
    if not isinstance(result.query_intent, str) or not result.query_intent.strip():
        raise ExecutiveReasoningError("INVALID_QUERY_INTENT")
    if not isinstance(result.context, ExecutiveContext):
        raise ExecutiveReasoningError("INVALID_CONTEXT_TYPE")
    if not isinstance(result.evidence_references, tuple):
        raise ExecutiveReasoningError("INVALID_REASONING_REFERENCE_TYPE")
    expected = result.context.evidence
    if result.status not in {"NO_EVIDENCE", "EVIDENCE_BOUND"} or (result.status == "NO_EVIDENCE") != (not expected):
        raise ExecutiveReasoningError("INVALID_REASONING_STATUS")
    if len(result.evidence_references) != len(expected):
        raise ExecutiveReasoningError("EVIDENCE_REFERENCE_MISMATCH")
    fields = ("evidence_id", "source_id", "source_type", "source_locator", "citation_locator", "content_sha3_512", "authorization_receipt_ref", "retrieved_at", "source_version")
    for source, reference in zip(expected, result.evidence_references):
        if not isinstance(reference, ExecutiveReasoningEvidenceReference):
            raise ExecutiveReasoningError("INVALID_REASONING_REFERENCE_TYPE")
        if any(getattr(source, field) != getattr(reference, field) for field in fields):
            raise ExecutiveReasoningError("EVIDENCE_REFERENCE_MISMATCH")

@dataclass(frozen=True, slots=True)
class ExecutiveReasoningResult:
    """Immutable evidence envelope without semantic conclusions or authority."""
    evaluation_id: str
    evaluated_at: datetime
    query_intent: str
    context: ExecutiveContext
    evidence_references: tuple[ExecutiveReasoningEvidenceReference, ...]
    status: str
    def __post_init__(self) -> None:
        _validate_result(self)
    @property
    def tenant_id(self) -> str:
        return self.context.tenant_id
    @property
    def principal_id(self) -> str:
        return self.context.principal_id
    @property
    def request_id(self) -> str:
        return self.context.request_id
    @property
    def correlation_id(self) -> str | None:
        return self.context.correlation_id
    @property
    def evidence_count(self) -> int:
        return self.context.evidence_count

class ExecutiveReasoningEngine:
    """Stateless builder for an ExecutiveContext-bound evidence envelope."""
    def evaluate_query(self, query_intent: str, context: ExecutiveContext, *, evaluated_at: datetime | None = None) -> ExecutiveReasoningResult:
        if not isinstance(query_intent, str) or not query_intent.strip():
            raise ExecutiveReasoningError("INVALID_QUERY_INTENT")
        if not isinstance(context, ExecutiveContext):
            raise ExecutiveReasoningError("INVALID_CONTEXT_TYPE")
        timestamp = datetime.now(timezone.utc) if evaluated_at is None else _aware(evaluated_at)
        query_hash = sha3_512(query_intent.encode("utf-8")).hexdigest()
        material = "|".join((context.request_id, query_hash, *(item.evidence_id for item in context.evidence), timestamp.isoformat())).encode("utf-8")
        evaluation_id = f"REASON-{sha3_512(material).hexdigest()[:16]}"
        references = tuple(ExecutiveReasoningEvidenceReference(item.evidence_id, item.source_id, item.source_type, item.source_locator, item.citation_locator, item.content_sha3_512, item.authorization_receipt_ref, item.retrieved_at, item.source_version) for item in context.evidence)
        return ExecutiveReasoningResult(evaluation_id, timestamp, query_intent, context, references, "EVIDENCE_BOUND" if references else "NO_EVIDENCE")

executive_reasoning_engine = ExecutiveReasoningEngine()

# ARTIFACT: executive_reasoning_engine.py
# VERSION: v1.0.1-WILSY-EXECUTIVE-REASONING-EVIDENCE
# AUTHORITY BOUNDARY: evidence envelope only; no authority grant.
# TENANT POSTURE: ExecutiveContext-bound; no implicit identity or tenant fallback.
# EVIDENCE POSTURE: provenance references preserve explicit metadata only.
# FAIL-CLOSED POSTURE: invalid inputs and mismatched references are rejected.
# RETRIEVAL AUTHORITY: NONE
# MODEL AUTHORITY: NONE
# EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
