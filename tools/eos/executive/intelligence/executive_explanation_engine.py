"""TITLE: WILSY Executive Evidence-Bound Explanation Engine
VERSION: v1.0.0-WILSY-EXECUTIVE-EXPLANATION-EVIDENCE
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
EPITOME: Immutable deterministic advisory explanation envelope converging validated ExecutivePredictionResult and ExecutiveGovernanceResult siblings that share one Planning/evidence lineage; no causal, confidence, compliance, policy, risk, approval, authorization, legal, truth, or execution fact is manufactured.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/executive/intelligence/executive_explanation_engine.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-02
CHANGELOG: v1.0.0 replaces the synthetic mutable causal oracle with an immutable deterministic Prediction/Governance sibling-convergence evidence envelope.
COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY: Stable errors and deterministic identifiers never echo caller secrets.
TENANT BOUNDARY: Identity derives only through the shared Planning -> Decision -> Context -> KernelBootstrapRequest lineage carried by the supplied Prediction and Governance siblings.
AUTHORITY BOUNDARY: Advisory explanatory metadata only; no approval, authorization, policy verdict, enforcement, workflow, or execution authority.
EVIDENCE BOUNDARY: NO EVIDENCE = NO FACT; Explanation preserves only exact evidence references already shared by Prediction and Governance and creates no evidence.
REASONING BOUNDARY: Explanation accepts no independent reasoning input; reasoning provenance is inherited only through the validated shared Planning/Decision lineage.
DECISION BOUNDARY: Decision provenance is inherited only through the shared Planning lineage and grants no approval or execution authority.
PLANNING BOUNDARY: Explanation accepts no independent Planning input; Prediction and Governance must carry the same validated Planning provenance.
PREDICTION BOUNDARY: ExecutivePredictionResult is an advisory sibling input only; predictive metadata grants no forecast fact, probability, confidence, risk, outcome, accuracy, approval, or execution authority.
GOVERNANCE BOUNDARY: ExecutiveGovernanceResult is an advisory sibling input only; governance metadata grants no compliance, policy, regulatory, risk, approval, enforcement, or execution authority.
CONVERGENCE BOUNDARY: Prediction and Governance must share the same Planning value and exact evidence references; divergent sibling provenance fails closed and is never reconciled.
EXPLANATION BOUNDARY: Caller-supplied explanation intent and topics are inert metadata; the engine generates no narrative, causal claim, factual conclusion, confidence, truth claim, legal conclusion, recommendation, approval, or execution permission.
RETRIEVAL BOUNDARY: None.
MODEL BOUNDARY: None.
EXECUTION BOUNDARY: None; explanatory metadata grants no execution authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512

from tools.eos.executive.intelligence.executive_governance_engine import (
    ExecutiveGovernanceResult,
)
from tools.eos.executive.intelligence.executive_prediction_engine import (
    ExecutivePredictionResult,
)
from tools.eos.executive.intelligence.executive_reasoning_engine import (
    ExecutiveReasoningEvidenceReference,
)

VERSION = "v1.0.0-WILSY-EXECUTIVE-EXPLANATION-EVIDENCE"


class ExecutiveExplanationError(ValueError):
    """Stable, non-echoing fail-closed explanation contract error."""


def _text(value: object, code: str) -> str:
    if type(value) is not str or not value.strip():
        raise ExecutiveExplanationError(code)
    return value


def _aware(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise ExecutiveExplanationError("INVALID_EXPLAINED_AT")
    return value


def _frame_text(value: str) -> bytes:
    raw = value.encode("utf-8")
    return len(raw).to_bytes(8, "big") + raw


def _digest(values: tuple[str, ...]) -> str:
    hasher = sha3_512()
    for value in values:
        hasher.update(_frame_text(value))
    return hasher.hexdigest()


def _siblings(
    prediction: object,
    governance: object,
) -> tuple[ExecutivePredictionResult, ExecutiveGovernanceResult]:
    if type(prediction) is not ExecutivePredictionResult:
        raise ExecutiveExplanationError("INVALID_PREDICTION_TYPE")
    if type(governance) is not ExecutiveGovernanceResult:
        raise ExecutiveExplanationError("INVALID_GOVERNANCE_TYPE")
    if prediction.planning != governance.planning:
        raise ExecutiveExplanationError("SIBLING_PLANNING_MISMATCH")
    if prediction.evidence_references != governance.evidence_references:
        raise ExecutiveExplanationError("SIBLING_EVIDENCE_MISMATCH")
    return prediction, governance


def _id(
    intent: str,
    topics: tuple[str, ...],
    prediction: ExecutivePredictionResult,
    governance: ExecutiveGovernanceResult,
    stamp: datetime,
) -> str:
    planning = prediction.planning
    intent_digest = sha3_512(intent.encode("utf-8")).hexdigest()
    topic_digest = _digest(topics)
    hasher = sha3_512()
    for component in (
        planning.request_id,
        planning.plan_id,
        planning.decision_id,
        prediction.prediction_id,
        governance.governance_id,
        intent_digest,
        topic_digest,
        stamp.isoformat(),
    ):
        hasher.update(_frame_text(component))
    return "EXPL-" + hasher.hexdigest()[:16]


@dataclass(frozen=True, slots=True)
class ExecutiveExplanationResult:
    """Immutable sibling-convergence envelope preserving shared evidence provenance only."""

    explanation_id: str
    explained_at: datetime
    explanation_intent: str
    explanation_topics: tuple[str, ...]
    prediction: ExecutivePredictionResult
    governance: ExecutiveGovernanceResult
    evidence_references: tuple[ExecutiveReasoningEvidenceReference, ...]
    status: str

    def __post_init__(self) -> None:
        if (
            type(self.explanation_id) is not str
            or len(self.explanation_id) != 21
            or not self.explanation_id.startswith("EXPL-")
            or any(
                char not in "0123456789abcdef"
                for char in self.explanation_id[5:]
            )
        ):
            raise ExecutiveExplanationError("INVALID_EXPLANATION_ID")
        _aware(self.explained_at)
        _text(self.explanation_intent, "INVALID_EXPLANATION_INTENT")
        if type(self.explanation_topics) is not tuple or not self.explanation_topics:
            raise ExecutiveExplanationError("INVALID_EXPLANATION_TOPICS")
        for topic in self.explanation_topics:
            _text(topic, "INVALID_EXPLANATION_TOPIC")

        prediction, governance = _siblings(self.prediction, self.governance)

        if type(self.evidence_references) is not tuple or any(
            type(reference) is not ExecutiveReasoningEvidenceReference
            for reference in self.evidence_references
        ):
            raise ExecutiveExplanationError("INVALID_EXPLANATION_REFERENCE_TYPE")
        if (
            self.evidence_references != prediction.evidence_references
            or self.evidence_references != governance.evidence_references
        ):
            raise ExecutiveExplanationError("EVIDENCE_REFERENCE_MISMATCH")

        expected_status = (
            "NO_EVIDENCE"
            if prediction.planning.evidence_count == 0
            else "EVIDENCE_BOUND"
        )
        if self.status != expected_status:
            raise ExecutiveExplanationError("INVALID_EXPLANATION_STATUS")

        if self.explanation_id != _id(
            self.explanation_intent,
            self.explanation_topics,
            prediction,
            governance,
            self.explained_at,
        ):
            raise ExecutiveExplanationError("INVALID_EXPLANATION_ID")

    planning = property(lambda self: self.prediction.planning)
    tenant_id = property(lambda self: self.planning.tenant_id)
    principal_id = property(lambda self: self.planning.principal_id)
    request_id = property(lambda self: self.planning.request_id)
    correlation_id = property(lambda self: self.planning.correlation_id)
    plan_id = property(lambda self: self.planning.plan_id)
    decision_id = property(lambda self: self.planning.decision_id)
    target_domain = property(lambda self: self.planning.target_domain)
    prediction_id = property(lambda self: self.prediction.prediction_id)
    governance_id = property(lambda self: self.governance.governance_id)
    evidence_count = property(lambda self: self.planning.evidence_count)


class ExecutiveExplanationEngine:
    """Stateless builder for deterministic evidence-preserving sibling convergence."""

    def build_explanation(
        self,
        explanation_intent: str,
        explanation_topics: tuple[str, ...],
        prediction: ExecutivePredictionResult,
        governance: ExecutiveGovernanceResult,
        *,
        explained_at: datetime | None = None,
    ) -> ExecutiveExplanationResult:
        intent = _text(
            explanation_intent,
            "INVALID_EXPLANATION_INTENT",
        )
        if type(explanation_topics) is not tuple or not explanation_topics:
            raise ExecutiveExplanationError("INVALID_EXPLANATION_TOPICS")
        for topic in explanation_topics:
            _text(topic, "INVALID_EXPLANATION_TOPIC")

        prediction, governance = _siblings(prediction, governance)

        stamp = (
            datetime.now(timezone.utc)
            if explained_at is None
            else _aware(explained_at)
        )
        status = (
            "NO_EVIDENCE"
            if prediction.planning.evidence_count == 0
            else "EVIDENCE_BOUND"
        )

        return ExecutiveExplanationResult(
            _id(
                intent,
                explanation_topics,
                prediction,
                governance,
                stamp,
            ),
            stamp,
            intent,
            explanation_topics,
            prediction,
            governance,
            prediction.evidence_references,
            status,
        )


executive_explanation_engine = ExecutiveExplanationEngine()

# ARTIFACT: executive_explanation_engine.py
# VERSION: v1.0.0-WILSY-EXECUTIVE-EXPLANATION-EVIDENCE
# AUTHORITY BOUNDARY: advisory explanation evidence only; no authority grant.
# TENANT POSTURE: identity derives only through the shared Planning/Decision/Reasoning/Context/KernelBootstrapRequest lineage.
# EVIDENCE POSTURE: NO EVIDENCE = NO FACT; explanation preserves exact sibling evidence references and creates no evidence.
# REASONING POSTURE: no independent reasoning authority; provenance is inherited through the validated shared Planning/Decision chain.
# DECISION POSTURE: decision provenance is inherited only through the shared Planning lineage and grants no approval or execution authority.
# PLANNING POSTURE: no independent Planning input; Prediction and Governance must share the same validated Planning provenance.
# PREDICTION POSTURE: Prediction is an advisory sibling input only and grants no forecast fact, confidence, risk, outcome, approval, or execution authority.
# GOVERNANCE POSTURE: Governance is an advisory sibling input only and grants no compliance, policy, regulatory, risk, approval, enforcement, or execution authority.
# CONVERGENCE POSTURE: divergent Prediction/Governance Planning or evidence provenance fails closed and is never reconciled.
# EXPLANATION POSTURE: caller explanation metadata is inert; no narrative, causal claim, fact, confidence, truth, legal conclusion, recommendation, approval, or execution is manufactured.
# FAIL-CLOSED POSTURE: malformed IDs, timestamps, metadata, sibling types, sibling provenance, evidence references, status, or deterministic identity reject with stable non-echoing errors.
# RETRIEVAL AUTHORITY: NONE
# MODEL AUTHORITY: NONE
# EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
