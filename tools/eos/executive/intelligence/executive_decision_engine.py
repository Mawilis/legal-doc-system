"""WILSY OS evidence-bound executive decision boundary.

TITLE: WILSY Executive Evidence-Bound Decision Engine
VERSION: v1.0.0-WILSY-EXECUTIVE-DECISION-EVIDENCE
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
EPITOME: Deterministic evidence-bound decision-basis envelope; no decision facts or authority are manufactured.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/executive/intelligence/executive_decision_engine.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.0 retires synthetic executive impacts, mutable decision state, random identifiers, fabricated evidence, and authoritative recommendation semantics in favor of immutable ExecutiveReasoningResult-bound provenance.
COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY: Stable identifiers and errors disclose no raw decision text, evidence content, tenant/principal authority values, source locators, or authorization receipt values.
TENANT BOUNDARY: Tenant, principal, request, and correlation identity derive only through ExecutiveReasoningResult -> ExecutiveContext -> KernelBootstrapRequest.
AUTHORITY BOUNDARY: No authentication, authorization, recommendation, approval, retrieval, model, execution, or financial authority.
EVIDENCE BOUNDARY: Decision results preserve only provenance already validated by ExecutiveReasoningResult; NO EVIDENCE = NO FACT.
REASONING BOUNDARY: ExecutiveReasoningResult is the sole reasoning input and supplies evidence provenance without granting decision or execution authority.
RETRIEVAL BOUNDARY: No retrieval, evidence selection, network access, database access, or filesystem mutation occurs.
MODEL BOUNDARY: No model is invoked and no model conclusion is represented.
EXECUTION BOUNDARY: Decision results are advisory provenance envelopes only and cannot dispatch, approve, release, pay, transfer, or execute.
FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512

from tools.eos.executive.intelligence.executive_reasoning_engine import (
    ExecutiveReasoningEvidenceReference,
    ExecutiveReasoningResult,
)


VERSION = "v1.0.0-WILSY-EXECUTIVE-DECISION-EVIDENCE"


class ExecutiveDecisionError(ValueError):
    """Stable fail-closed executive decision contract error."""


def _aware(value: object) -> datetime:
    """Return an aware datetime or fail closed without echoing the value."""
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ExecutiveDecisionError("INVALID_EVALUATED_AT")
    return value


def _nonblank_string(value: object, error_code: str) -> str:
    """Require an actual nonblank string while preserving valid caller text."""
    if not isinstance(value, str) or not value.strip():
        raise ExecutiveDecisionError(error_code)
    return value


def _validate_decision_id(value: object) -> str:
    """Require the canonical DEC-[0-9a-f]{16} identifier."""
    if (
        not isinstance(value, str)
        or len(value) != 20
        or not value.startswith("DEC-")
        or any(char not in "0123456789abcdef" for char in value[4:])
    ):
        raise ExecutiveDecisionError("INVALID_DECISION_ID")
    return value


def _decision_id(
    decision_intent: str,
    target_domain: str,
    reasoning: ExecutiveReasoningResult,
    evaluated_at: datetime,
) -> str:
    """Derive a deterministic non-reversible decision identifier."""
    decision_hash = sha3_512(decision_intent.encode("utf-8")).hexdigest()
    domain_hash = sha3_512(target_domain.encode("utf-8")).hexdigest()
    material = "\x1f".join(
        (
            reasoning.request_id,
            reasoning.evaluation_id,
            decision_hash,
            domain_hash,
            evaluated_at.isoformat(),
        )
    ).encode("utf-8")
    return f"DEC-{sha3_512(material).hexdigest()[:16]}"


@dataclass(frozen=True, slots=True)
class ExecutiveDecisionResult:
    """Immutable evidence-bound decision-basis envelope without decision authority.

    Authority:
        Derives tenant/principal/request/correlation identity only from the
        supplied ExecutiveReasoningResult.

    Evidence:
        Preserves the reasoning result's validated evidence references exactly.
        It performs no retrieval and manufactures no evidence or conclusions.

    Mutation:
        Frozen and slot-bound. It owns no mutable persistence or execution state.

    Financial boundary:
        Carries no payment, transfer, approval, release, or other financial
        execution authority. Kennel EOS remains the exclusive executor.
    """

    decision_id: str
    evaluated_at: datetime
    decision_intent: str
    target_domain: str
    reasoning: ExecutiveReasoningResult
    evidence_references: tuple[ExecutiveReasoningEvidenceReference, ...]
    status: str

    def __post_init__(self) -> None:
        """Revalidate every public construction path fail closed."""
        _validate_decision_id(self.decision_id)
        _aware(self.evaluated_at)
        _nonblank_string(self.decision_intent, "INVALID_DECISION_INTENT")
        _nonblank_string(self.target_domain, "INVALID_TARGET_DOMAIN")

        if not isinstance(self.reasoning, ExecutiveReasoningResult):
            raise ExecutiveDecisionError("INVALID_REASONING_TYPE")

        expected_decision_id = _decision_id(
            self.decision_intent,
            self.target_domain,
            self.reasoning,
            self.evaluated_at,
        )
        if self.decision_id != expected_decision_id:
            raise ExecutiveDecisionError("INVALID_DECISION_ID")

        if not isinstance(self.evidence_references, tuple):
            raise ExecutiveDecisionError("INVALID_DECISION_REFERENCE_TYPE")

        if any(
            not isinstance(reference, ExecutiveReasoningEvidenceReference)
            for reference in self.evidence_references
        ):
            raise ExecutiveDecisionError("INVALID_DECISION_REFERENCE_TYPE")

        expected_status = (
            "NO_EVIDENCE"
            if self.reasoning.evidence_count == 0
            else "EVIDENCE_BOUND"
        )
        if self.status != expected_status:
            raise ExecutiveDecisionError("INVALID_DECISION_STATUS")

        if self.evidence_references != self.reasoning.evidence_references:
            raise ExecutiveDecisionError("EVIDENCE_REFERENCE_MISMATCH")

    @property
    def tenant_id(self) -> str:
        """Validated tenant identity inherited from the reasoning authority chain."""
        return self.reasoning.tenant_id

    @property
    def principal_id(self) -> str:
        """Validated principal identity inherited from the reasoning authority chain."""
        return self.reasoning.principal_id

    @property
    def request_id(self) -> str:
        """Validated request identity inherited from the reasoning authority chain."""
        return self.reasoning.request_id

    @property
    def correlation_id(self) -> str | None:
        """Optional correlation identity inherited without inference."""
        return self.reasoning.correlation_id

    @property
    def evidence_count(self) -> int:
        """Validated evidence count inherited from ExecutiveReasoningResult."""
        return self.reasoning.evidence_count


class ExecutiveDecisionEngine:
    """Stateless builder for ExecutiveReasoningResult-bound decision envelopes.

    The engine evaluates no business, legal, financial, operational, governance,
    or risk conclusion. It only binds caller-supplied decision metadata to a
    previously validated reasoning provenance envelope.

    It has no retrieval, model, persistence, approval, execution, or financial
    authority.
    """

    def evaluate_decision(
        self,
        decision_intent: str,
        target_domain: str,
        reasoning: ExecutiveReasoningResult,
        *,
        evaluated_at: datetime | None = None,
    ) -> ExecutiveDecisionResult:
        """Build one immutable evidence-bound decision-basis result.

        Args:
            decision_intent:
                Caller-supplied nonblank decision text. Text is metadata only;
                words such as approve, release, payment, or transfer grant no
                execution authority.
            target_domain:
                Caller-supplied nonblank domain label. A value such as
                ``financial`` grants no financial authority.
            reasoning:
                A validated ExecutiveReasoningResult. No second tenant,
                principal, request, evidence, or authority envelope is accepted.
            evaluated_at:
                Optional aware timestamp. When omitted, current aware UTC is used.

        Returns:
            An immutable ExecutiveDecisionResult preserving the reasoning
            provenance references exactly and in order.

        Raises:
            ExecutiveDecisionError:
                On malformed decision text, target domain, reasoning type,
                timestamp, result identifier, status, or provenance references.

        Idempotency:
            Identical explicit inputs, including ``evaluated_at``, produce the
            same deterministic decision identifier.

        Mutation:
            None. No state, persistence, network, database, filesystem,
            execution, or financial side effect occurs.
        """
        decision_text = _nonblank_string(
            decision_intent,
            "INVALID_DECISION_INTENT",
        )
        domain_text = _nonblank_string(
            target_domain,
            "INVALID_TARGET_DOMAIN",
        )

        if not isinstance(reasoning, ExecutiveReasoningResult):
            raise ExecutiveDecisionError("INVALID_REASONING_TYPE")

        timestamp = (
            datetime.now(timezone.utc)
            if evaluated_at is None
            else _aware(evaluated_at)
        )

        references = reasoning.evidence_references
        status = (
            "NO_EVIDENCE"
            if reasoning.evidence_count == 0
            else "EVIDENCE_BOUND"
        )

        return ExecutiveDecisionResult(
            decision_id=_decision_id(
                decision_text,
                domain_text,
                reasoning,
                timestamp,
            ),
            evaluated_at=timestamp,
            decision_intent=decision_text,
            target_domain=domain_text,
            reasoning=reasoning,
            evidence_references=references,
            status=status,
        )


executive_decision_engine = ExecutiveDecisionEngine()


# ARTIFACT: executive_decision_engine.py
# VERSION: v1.0.0-WILSY-EXECUTIVE-DECISION-EVIDENCE
# AUTHORITY BOUNDARY: evidence-bound decision basis only; no authority grant.
# TENANT POSTURE: authority derives only through ExecutiveReasoningResult/ExecutiveContext/KernelBootstrapRequest.
# EVIDENCE POSTURE: NO EVIDENCE = NO FACT; supplied reasoning provenance is preserved only.
# REASONING POSTURE: decision consumes validated reasoning provenance and manufactures no conclusions.
# FAIL-CLOSED POSTURE: malformed inputs and provenance mismatches are rejected.
# RETRIEVAL AUTHORITY: NONE
# MODEL AUTHORITY: NONE
# EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
