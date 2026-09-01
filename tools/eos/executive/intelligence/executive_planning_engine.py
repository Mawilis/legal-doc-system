"""WILSY OS evidence-bound executive planning boundary.

TITLE: WILSY Executive Evidence-Bound Planning Engine
VERSION: v1.0.0-WILSY-EXECUTIVE-PLANNING-EVIDENCE
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
EPITOME: Immutable deterministic advisory planning envelope bound solely to a validated ExecutiveDecisionResult; no planning fact, authorization, or execution authority is manufactured.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/executive/intelligence/executive_planning_engine.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.0 replaces the fractured synthetic planner with an immutable deterministic decision-bound evidence planning envelope.
COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY: Stable errors and identifiers never echo caller secrets.
TENANT BOUNDARY: Identity derives only through the supplied ExecutiveDecisionResult chain.
AUTHORITY BOUNDARY: Advisory planning metadata only; no approval, authorization, or execution authority.
EVIDENCE BOUNDARY: NO EVIDENCE = NO FACT; planning preserves only exact decision evidence references and creates no evidence.
REASONING BOUNDARY: Planning consumes no independent reasoning input; reasoning provenance is inherited only through ExecutiveDecisionResult.
DECISION BOUNDARY: ExecutiveDecisionResult is the sole upstream decision/provenance input and grants no approval or execution authority.
PLANNING BOUNDARY: Caller-supplied plan intent and plan steps are inert advisory metadata; the engine generates no plan facts, stages, approvals, workflows, or outcomes.
RETRIEVAL BOUNDARY: None.
MODEL BOUNDARY: None.
EXECUTION BOUNDARY: None; caller planning metadata grants no execution authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
from tools.eos.executive.intelligence.executive_decision_engine import ExecutiveDecisionResult
from tools.eos.executive.intelligence.executive_reasoning_engine import ExecutiveReasoningEvidenceReference
VERSION = "v1.0.0-WILSY-EXECUTIVE-PLANNING-EVIDENCE"
class ExecutivePlanningError(ValueError):
    """Stable fail-closed planning contract error."""
def _aware(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None: raise ExecutivePlanningError("INVALID_PLANNED_AT")
    return value
def _text(value: object, code: str) -> str:
    if not isinstance(value, str) or not value.strip(): raise ExecutivePlanningError(code)
    return value
def _plan_id(intent: str, steps: tuple[str, ...], decision: ExecutiveDecisionResult, planned_at: datetime) -> str:
    hasher = sha3_512(); hasher.update(decision.request_id.encode()); hasher.update(decision.decision_id.encode()); hasher.update(sha3_512(intent.encode()).hexdigest().encode())
    framed = sha3_512()
    for step in steps:
        raw = step.encode(); framed.update(len(raw).to_bytes(8, "big")); framed.update(raw)
    hasher.update(framed.hexdigest().encode()); hasher.update(planned_at.isoformat().encode())
    return "PLAN-" + hasher.hexdigest()[:16]
@dataclass(frozen=True, slots=True)
class ExecutivePlanningResult:
    """Immutable advisory plan envelope bound solely to a decision result."""
    plan_id: str; planned_at: datetime; plan_intent: str; plan_steps: tuple[str, ...]; decision: ExecutiveDecisionResult; evidence_references: tuple[ExecutiveReasoningEvidenceReference, ...]; status: str
    def __post_init__(self) -> None:
        if not isinstance(self.plan_id, str) or len(self.plan_id) != 21 or not self.plan_id.startswith("PLAN-") or any(c not in "0123456789abcdef" for c in self.plan_id[5:]): raise ExecutivePlanningError("INVALID_PLAN_ID")
        _aware(self.planned_at); _text(self.plan_intent, "INVALID_PLAN_INTENT")
        if not isinstance(self.plan_steps, tuple) or not self.plan_steps: raise ExecutivePlanningError("INVALID_PLAN_STEPS")
        if any(not isinstance(s, str) or not s.strip() for s in self.plan_steps): raise ExecutivePlanningError("INVALID_PLAN_STEP")
        if not isinstance(self.decision, ExecutiveDecisionResult): raise ExecutivePlanningError("INVALID_DECISION_TYPE")
        if self.plan_id != _plan_id(self.plan_intent, self.plan_steps, self.decision, self.planned_at): raise ExecutivePlanningError("INVALID_PLAN_ID")
        if not isinstance(self.evidence_references, tuple) or any(not isinstance(r, ExecutiveReasoningEvidenceReference) for r in self.evidence_references): raise ExecutivePlanningError("INVALID_PLAN_REFERENCE_TYPE")
        if self.evidence_references != self.decision.evidence_references: raise ExecutivePlanningError("EVIDENCE_REFERENCE_MISMATCH")
        if self.status != ("NO_EVIDENCE" if self.decision.evidence_count == 0 else "EVIDENCE_BOUND"): raise ExecutivePlanningError("INVALID_PLAN_STATUS")
    tenant_id = property(lambda s: s.decision.tenant_id); principal_id = property(lambda s: s.decision.principal_id); request_id = property(lambda s: s.decision.request_id); correlation_id = property(lambda s: s.decision.correlation_id); decision_id = property(lambda s: s.decision.decision_id); target_domain = property(lambda s: s.decision.target_domain); evidence_count = property(lambda s: s.decision.evidence_count)
class ExecutivePlanningEngine:
    """Stateless builder of caller-supplied advisory plan envelopes."""
    def build_plan(self, plan_intent: str, plan_steps: tuple[str, ...], decision: ExecutiveDecisionResult, *, planned_at: datetime |None = None) -> ExecutivePlanningResult:
        intent = _text(plan_intent, "INVALID_PLAN_INTENT")
        if not isinstance(plan_steps, tuple) or not plan_steps: raise ExecutivePlanningError("INVALID_PLAN_STEPS")
        if any(not isinstance(s, str) or not s.strip() for s in plan_steps): raise ExecutivePlanningError("INVALID_PLAN_STEP")
        if not isinstance(decision, ExecutiveDecisionResult): raise ExecutivePlanningError("INVALID_DECISION_TYPE")
        at = datetime.now(timezone.utc) if planned_at is None else _aware(planned_at)
        return ExecutivePlanningResult(_plan_id(intent, plan_steps, decision, at), at, intent, plan_steps, decision, decision.evidence_references, "NO_EVIDENCE" if decision.evidence_count == 0 else "EVIDENCE_BOUND")
executive_planning_engine = ExecutivePlanningEngine()
# ARTIFACT: executive_planning_engine.py
# VERSION: v1.0.0-WILSY-EXECUTIVE-PLANNING-EVIDENCE
# AUTHORITY BOUNDARY: advisory planning evidence only; no authority grant.
# TENANT POSTURE: identity derives only through ExecutiveDecisionResult/context/bootstrap.
# EVIDENCE POSTURE: NO EVIDENCE = NO FACT; planning preserves only exact decision evidence references and creates no evidence.
# REASONING POSTURE: no independent reasoning input; reasoning provenance is inherited only through the validated decision chain.
# DECISION POSTURE: ExecutiveDecisionResult is the sole upstream decision/provenance basis and provides no approval or execution grant.
# PLANNING POSTURE: caller-supplied planning metadata is advisory and inert; no plan fact, workflow, approval, outcome, or execution is manufactured.
# FAIL-CLOSED POSTURE: malformed identity, timestamps, steps, deterministic IDs, status, or provenance fail closed with stable non-echoing errors.
# RETRIEVAL AUTHORITY: NONE
# MODEL AUTHORITY: NONE
# EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
