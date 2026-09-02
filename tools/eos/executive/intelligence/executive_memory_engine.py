"""WILSY OS — Executive Memory evidence-bound engine.

TITLE: WILSY Executive Evidence-Bound Memory Engine
VERSION: v1.0.0-WILSY-EXECUTIVE-MEMORY-EVIDENCE
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
PURPOSE: Preserve one validated Executive Explanation as immutable memory provenance without creating evidence, facts, persistence, workflow authority, or execution authority.
EPITOME: Memory remembers only the evidence-bound explanation it is given; it never upgrades memory into truth or authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/executive/intelligence/executive_memory_engine.py
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from tools.eos.executive.intelligence.executive_explanation_engine import (
    ExecutiveExplanationResult,
)


VERSION = "v1.0.0-WILSY-EXECUTIVE-MEMORY-EVIDENCE"

_MEMORY_ID_PREFIX = "MEM-"
_MEMORY_ID_HEX_LENGTH = 16
_STATUS_NO_EVIDENCE = "NO_EVIDENCE"
_STATUS_EVIDENCE_BOUND = "EVIDENCE_BOUND"


class ExecutiveMemoryError(ValueError):
    """Stable fail-closed Executive Memory contract error."""


def _fail(code: str) -> None:
    raise ExecutiveMemoryError(code)


def _validate_recorded_at(recorded_at: object) -> datetime:
    if (
        not isinstance(recorded_at, datetime)
        or recorded_at.tzinfo is None
        or recorded_at.utcoffset() != timedelta(0)
    ):
        _fail("INVALID_RECORDED_AT")
    return recorded_at


def _has_valid_memory_id_shape(memory_id: object) -> bool:
    if not isinstance(memory_id, str):
        return False

    if len(memory_id) != len(_MEMORY_ID_PREFIX) + _MEMORY_ID_HEX_LENGTH:
        return False

    if not memory_id.startswith(_MEMORY_ID_PREFIX):
        return False

    suffix = memory_id[len(_MEMORY_ID_PREFIX) :]
    return all(character in "0123456789abcdef" for character in suffix)


def _frame_text(value: str) -> bytes:
    raw = value.encode("utf-8")
    return len(raw).to_bytes(8, "big") + raw


def _expected_status(
    explanation: ExecutiveExplanationResult,
) -> str:
    if explanation.evidence_references:
        return _STATUS_EVIDENCE_BOUND
    return _STATUS_NO_EVIDENCE


def _validate_explanation(
    explanation: object,
) -> ExecutiveExplanationResult:
    if not isinstance(explanation, ExecutiveExplanationResult):
        _fail("INVALID_EXPLANATION_TYPE")

    if explanation.prediction.planning != explanation.governance.planning:
        _fail("INVALID_EXPLANATION_PROVENANCE")

    if explanation.planning != explanation.prediction.planning:
        _fail("INVALID_EXPLANATION_PROVENANCE")

    if not (
        explanation.evidence_references is explanation.prediction.evidence_references
        and explanation.evidence_references is explanation.governance.evidence_references
    ):
        _fail("EVIDENCE_REFERENCE_MISMATCH")

    if explanation.status != _expected_status(explanation):
        _fail("INVALID_MEMORY_STATUS")

    return explanation


def _memory_id(
    explanation: ExecutiveExplanationResult,
    recorded_at: datetime,
) -> str:
    components = (
        explanation.tenant_id,
        explanation.principal_id,
        explanation.request_id,
        explanation.correlation_id,
        explanation.plan_id,
        explanation.decision_id,
        explanation.target_domain,
        explanation.prediction_id,
        explanation.governance_id,
        explanation.explanation_id,
        recorded_at.isoformat(),
    )

    hasher = hashlib.sha3_512()
    for component in components:
        hasher.update(_frame_text(component))

    return _MEMORY_ID_PREFIX + hasher.hexdigest()[:_MEMORY_ID_HEX_LENGTH]


@dataclass(frozen=True, slots=True)
class ExecutiveMemoryRecord:
    """Immutable evidence-bound Executive Memory envelope."""

    memory_id: str
    recorded_at: datetime
    explanation: ExecutiveExplanationResult
    evidence_references: tuple[object, ...]
    status: str

    def __post_init__(self) -> None:
        if not _has_valid_memory_id_shape(self.memory_id):
            _fail("INVALID_MEMORY_ID")

        recorded_at = _validate_recorded_at(self.recorded_at)
        explanation = _validate_explanation(self.explanation)

        if self.evidence_references is not explanation.evidence_references:
            _fail("EVIDENCE_REFERENCE_MISMATCH")

        expected_status = _expected_status(explanation)
        if self.status != expected_status:
            _fail("INVALID_MEMORY_STATUS")

        if self.memory_id != _memory_id(explanation, recorded_at):
            _fail("INVALID_MEMORY_ID")

    @property
    def planning(self):
        return self.explanation.planning

    @property
    def prediction(self):
        return self.explanation.prediction

    @property
    def governance(self):
        return self.explanation.governance

    @property
    def tenant_id(self) -> str:
        return self.explanation.tenant_id

    @property
    def principal_id(self) -> str:
        return self.explanation.principal_id

    @property
    def request_id(self) -> str:
        return self.explanation.request_id

    @property
    def correlation_id(self) -> str:
        return self.explanation.correlation_id

    @property
    def plan_id(self) -> str:
        return self.explanation.plan_id

    @property
    def decision_id(self) -> str:
        return self.explanation.decision_id

    @property
    def target_domain(self) -> str:
        return self.explanation.target_domain

    @property
    def prediction_id(self) -> str:
        return self.explanation.prediction_id

    @property
    def governance_id(self) -> str:
        return self.explanation.governance_id

    @property
    def explanation_id(self) -> str:
        return self.explanation.explanation_id

    @property
    def evidence_count(self) -> int:
        return len(self.evidence_references)


class ExecutiveMemoryEngine:
    """Stateless builder for immutable evidence-bound memory records."""

    __slots__ = ()

    def build_memory(
        self,
        explanation: ExecutiveExplanationResult,
        *,
        recorded_at: datetime | None = None,
    ) -> ExecutiveMemoryRecord:
        validated_explanation = _validate_explanation(explanation)

        if recorded_at is None:
            resolved_recorded_at = datetime.now(timezone.utc)
        else:
            resolved_recorded_at = _validate_recorded_at(recorded_at)

        return ExecutiveMemoryRecord(
            memory_id=_memory_id(
                validated_explanation,
                resolved_recorded_at,
            ),
            recorded_at=resolved_recorded_at,
            explanation=validated_explanation,
            evidence_references=validated_explanation.evidence_references,
            status=_expected_status(validated_explanation),
        )


executive_memory_engine = ExecutiveMemoryEngine()


__all__ = (
    "VERSION",
    "ExecutiveMemoryError",
    "ExecutiveMemoryRecord",
    "ExecutiveMemoryEngine",
    "executive_memory_engine",
)

# Executive Memory grants no fact, legal, compliance, workflow, payment, or execution authority.
# Kennel EOS remains the exclusive financial execution authority.
# END OF WILSY OS SOVEREIGN PRODUCTION
