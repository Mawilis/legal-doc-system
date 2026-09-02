"""TITLE: WILSY Executive Evidence-Bound Governance Engine
VERSION: v1.0.0-WILSY-EXECUTIVE-GOVERNANCE-EVIDENCE
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
EPITOME: Immutable deterministic advisory governance-review envelope bound solely to a validated ExecutivePlanningResult; no compliance, policy, risk, approval, authorization, or execution fact is manufactured.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/executive/intelligence/executive_governance_engine.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-02
CHANGELOG: v1.0.0 replaces the synthetic mutable compliance oracle with an immutable deterministic Planning-bound evidence governance-review envelope.
COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY: Stable errors and identifiers never echo caller secrets.
TENANT BOUNDARY: Identity derives only through the supplied ExecutivePlanningResult chain.
AUTHORITY BOUNDARY: Advisory governance-review metadata only; no approval, authorization, policy verdict, enforcement, or execution authority.
EVIDENCE BOUNDARY: NO EVIDENCE = NO FACT; Governance preserves only exact Planning evidence references and creates no evidence.
REASONING BOUNDARY: Governance accepts no independent reasoning input; reasoning provenance is inherited only through the validated Planning/Decision chain.
DECISION BOUNDARY: Decision provenance is inherited only through Planning and grants no approval or execution authority.
PLANNING BOUNDARY: ExecutivePlanningResult is the sole upstream Planning/provenance input and grants no execution authority.
PREDICTION BOUNDARY: ExecutivePredictionResult is not an authority input to Governance; predictive metadata grants no compliance, policy, risk, approval, or execution authority.
GOVERNANCE BOUNDARY: Caller review intent/scopes are inert metadata; no compliance verdict, regulatory applicability, policy satisfaction, risk assessment, signature, approval, enforcement, or execution is manufactured.
RETRIEVAL BOUNDARY: None.
MODEL BOUNDARY: None.
EXECUTION BOUNDARY: None.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
from tools.eos.executive.intelligence.executive_planning_engine import ExecutivePlanningResult
from tools.eos.executive.intelligence.executive_reasoning_engine import ExecutiveReasoningEvidenceReference
VERSION = "v1.0.0-WILSY-EXECUTIVE-GOVERNANCE-EVIDENCE"
class ExecutiveGovernanceError(ValueError):
    """Stable, non-echoing fail-closed governance contract error."""
def _text(value: object, code: str) -> str:
    if not isinstance(value, str) or not value.strip(): raise ExecutiveGovernanceError(code)
    return value
def _aware(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None: raise ExecutiveGovernanceError("INVALID_REVIEWED_AT")
    return value
def _frame_text(value: str) -> bytes:
    raw = value.encode("utf-8"); return len(raw).to_bytes(8, "big") + raw
def _id(intent: str, scopes: tuple[str, ...], planning: ExecutivePlanningResult, stamp: datetime) -> str:
    scope_hash = sha3_512()
    for scope in scopes: scope_hash.update(_frame_text(scope))
    hasher = sha3_512()
    for component in (planning.request_id, planning.plan_id, planning.decision_id, sha3_512(intent.encode("utf-8")).hexdigest(), scope_hash.hexdigest(), stamp.isoformat()): hasher.update(_frame_text(component))
    return "GOV-" + hasher.hexdigest()[:16]
@dataclass(frozen=True, slots=True)
class ExecutiveGovernanceResult:
    """Immutable evidence-binding governance review envelope; never a compliance or execution authority."""
    governance_id: str; reviewed_at: datetime; review_intent: str; review_scopes: tuple[str, ...]; planning: ExecutivePlanningResult; evidence_references: tuple[ExecutiveReasoningEvidenceReference, ...]; status: str
    def __post_init__(self) -> None:
        if not isinstance(self.governance_id, str) or len(self.governance_id) != 20 or not self.governance_id.startswith("GOV-") or any(c not in "0123456789abcdef" for c in self.governance_id[4:]): raise ExecutiveGovernanceError("INVALID_GOVERNANCE_ID")
        _aware(self.reviewed_at); _text(self.review_intent, "INVALID_REVIEW_INTENT")
        if not isinstance(self.review_scopes, tuple) or not self.review_scopes: raise ExecutiveGovernanceError("INVALID_REVIEW_SCOPES")
        if any(not isinstance(s, str) or not s.strip() for s in self.review_scopes): raise ExecutiveGovernanceError("INVALID_REVIEW_SCOPE")
        if not isinstance(self.planning, ExecutivePlanningResult): raise ExecutiveGovernanceError("INVALID_PLANNING_TYPE")
        if not isinstance(self.evidence_references, tuple) or any(not isinstance(r, ExecutiveReasoningEvidenceReference) for r in self.evidence_references): raise ExecutiveGovernanceError("INVALID_GOVERNANCE_REFERENCE_TYPE")
        if self.evidence_references != self.planning.evidence_references: raise ExecutiveGovernanceError("EVIDENCE_REFERENCE_MISMATCH")
        if self.status != ("NO_EVIDENCE" if self.planning.evidence_count == 0 else "EVIDENCE_BOUND"): raise ExecutiveGovernanceError("INVALID_GOVERNANCE_STATUS")
        if self.governance_id != _id(self.review_intent, self.review_scopes, self.planning, self.reviewed_at): raise ExecutiveGovernanceError("INVALID_GOVERNANCE_ID")
    tenant_id = property(lambda s: s.planning.tenant_id); principal_id = property(lambda s: s.planning.principal_id); request_id = property(lambda s: s.planning.request_id); correlation_id = property(lambda s: s.planning.correlation_id); plan_id = property(lambda s: s.planning.plan_id); decision_id = property(lambda s: s.planning.decision_id); target_domain = property(lambda s: s.planning.target_domain); evidence_count = property(lambda s: s.planning.evidence_count)
class ExecutiveGovernanceEngine:
    """Stateless builder of Planning-bound advisory governance envelopes."""
    def build_review(self, review_intent: str, review_scopes: tuple[str, ...], planning: ExecutivePlanningResult, *, reviewed_at: datetime | None = None) -> ExecutiveGovernanceResult:
        intent = _text(review_intent, "INVALID_REVIEW_INTENT")
        if not isinstance(review_scopes, tuple) or not review_scopes: raise ExecutiveGovernanceError("INVALID_REVIEW_SCOPES")
        if any(not isinstance(s, str) or not s.strip() for s in review_scopes): raise ExecutiveGovernanceError("INVALID_REVIEW_SCOPE")
        if not isinstance(planning, ExecutivePlanningResult): raise ExecutiveGovernanceError("INVALID_PLANNING_TYPE")
        stamp = datetime.now(timezone.utc) if reviewed_at is None else _aware(reviewed_at)
        return ExecutiveGovernanceResult(_id(intent, review_scopes, planning, stamp), stamp, intent, review_scopes, planning, planning.evidence_references, "NO_EVIDENCE" if planning.evidence_count == 0 else "EVIDENCE_BOUND")
executive_governance_engine = ExecutiveGovernanceEngine()
# ARTIFACT: executive_governance_engine.py
# VERSION: v1.0.0-WILSY-EXECUTIVE-GOVERNANCE-EVIDENCE
# AUTHORITY BOUNDARY: advisory governance review only; no authority grant.
# TENANT POSTURE: identity derives only through ExecutivePlanningResult/Decision/Reasoning/Context/KernelBootstrapRequest.
# EVIDENCE POSTURE: NO EVIDENCE = NO FACT; governance preserves exact Planning evidence references and creates no evidence.
# REASONING POSTURE: no independent reasoning authority; provenance is inherited through the validated Planning/Decision chain.
# DECISION POSTURE: decision provenance is inherited only through Planning and grants no approval or execution authority.
# PLANNING POSTURE: ExecutivePlanningResult is the sole upstream planning/provenance basis.
# PREDICTION POSTURE: Prediction is not an authority input to Governance and grants no compliance, risk, approval, or execution authority.
# GOVERNANCE POSTURE: caller governance metadata is inert; no compliance verdict, policy fact, risk fact, signature, approval, enforcement, or execution is manufactured.
# FAIL-CLOSED POSTURE: malformed IDs, timestamps, review metadata, status, or provenance reject with stable non-echoing errors.
# RETRIEVAL AUTHORITY: NONE
# MODEL AUTHORITY: NONE
# EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
