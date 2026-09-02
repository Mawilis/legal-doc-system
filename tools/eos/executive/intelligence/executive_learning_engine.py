"""WILSY OS — Executive Learning evidence-bound engine.

TITLE: WILSY Executive Evidence-Bound Learning Engine
VERSION: v1.0.0-WILSY-EXECUTIVE-LEARNING-EVIDENCE
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
PURPOSE: Bind advisory learning metadata to one validated Executive Memory record without creating evidence, facts, persistence, model mutation, workflow authority, or execution authority.
EPITOME: Learning derives only an immutable advisory envelope from validated Memory provenance; it never mutates Memory, models, truth, workflow, or authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/executive/intelligence/executive_learning_engine.py
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from tools.eos.executive.intelligence.executive_memory_engine import (
    ExecutiveMemoryRecord,
)


VERSION = "v1.0.0-WILSY-EXECUTIVE-LEARNING-EVIDENCE"

_LEARNING_ID_PREFIX = "LEARN-"
_LEARNING_ID_HEX_LENGTH = 16
_STATUS_NO_EVIDENCE = "NO_EVIDENCE"
_STATUS_EVIDENCE_BOUND = "EVIDENCE_BOUND"


class ExecutiveLearningError(ValueError):
    """Stable fail-closed Executive Learning contract error."""


def _fail(code: str) -> None:
    raise ExecutiveLearningError(code)


def _validate_learned_at(learned_at: object) -> datetime:
    if (
        not isinstance(learned_at, datetime)
        or learned_at.tzinfo is None
        or learned_at.utcoffset() != timedelta(0)
    ):
        _fail("INVALID_LEARNED_AT")
    return learned_at


def _has_valid_learning_id_shape(learning_id: object) -> bool:
    if not isinstance(learning_id, str):
        return False

    if len(learning_id) != len(_LEARNING_ID_PREFIX) + _LEARNING_ID_HEX_LENGTH:
        return False

    if not learning_id.startswith(_LEARNING_ID_PREFIX):
        return False

    suffix = learning_id[len(_LEARNING_ID_PREFIX) :]
    return all(character in "0123456789abcdef" for character in suffix)


def _frame_text(value: str) -> bytes:
    raw = value.encode("utf-8")
    return len(raw).to_bytes(8, "big") + raw


def _validate_memory(memory: object) -> ExecutiveMemoryRecord:
    if type(memory) is not ExecutiveMemoryRecord:
        _fail("INVALID_MEMORY_TYPE")

    try:
        ExecutiveMemoryRecord(
            memory_id=memory.memory_id,
            recorded_at=memory.recorded_at,
            explanation=memory.explanation,
            evidence_references=memory.evidence_references,
            status=memory.status,
        )
    except (ValueError, TypeError, AttributeError):
        _fail("INVALID_MEMORY_PROVENANCE")

    return memory


def _validate_learning_signal(learning_signal: object) -> str:
    if not isinstance(learning_signal, str) or learning_signal == "":
        _fail("INVALID_LEARNING_SIGNAL")
    return learning_signal


def _validate_adaptation_notes(
    adaptation_notes: object,
) -> tuple[str, ...]:
    if type(adaptation_notes) is not tuple:
        _fail("INVALID_ADAPTATION_NOTES")

    if not all(
        isinstance(note, str) and note != ""
        for note in adaptation_notes
    ):
        _fail("INVALID_ADAPTATION_NOTES")

    return adaptation_notes


def _expected_status(memory: ExecutiveMemoryRecord) -> str:
    if memory.evidence_references:
        return _STATUS_EVIDENCE_BOUND
    return _STATUS_NO_EVIDENCE


def _learning_id(
    memory: ExecutiveMemoryRecord,
    learning_signal: str,
    adaptation_notes: tuple[str, ...],
    learned_at: datetime,
) -> str:
    fixed_components = (
        memory.tenant_id,
        memory.principal_id,
        memory.request_id,
        memory.correlation_id,
        memory.memory_id,
        memory.explanation_id,
        learning_signal,
    )

    hasher = hashlib.sha3_512()

    for component in fixed_components:
        hasher.update(_frame_text(component))

    hasher.update(len(adaptation_notes).to_bytes(8, "big"))

    for note in adaptation_notes:
        hasher.update(_frame_text(note))

    hasher.update(_frame_text(learned_at.isoformat()))

    return _LEARNING_ID_PREFIX + hasher.hexdigest()[:_LEARNING_ID_HEX_LENGTH]


@dataclass(frozen=True, slots=True)
class ExecutiveLearningResult:
    """Immutable advisory Executive Learning envelope bound to one Memory record."""

    learning_id: str
    learned_at: datetime
    memory: ExecutiveMemoryRecord
    learning_signal: str
    adaptation_notes: tuple[str, ...]
    evidence_references: tuple[object, ...]
    status: str

    def __post_init__(self) -> None:
        if not _has_valid_learning_id_shape(self.learning_id):
            _fail("INVALID_LEARNING_ID")

        learned_at = _validate_learned_at(self.learned_at)
        memory = _validate_memory(self.memory)
        learning_signal = _validate_learning_signal(self.learning_signal)
        adaptation_notes = _validate_adaptation_notes(self.adaptation_notes)

        if self.evidence_references is not memory.evidence_references:
            _fail("EVIDENCE_REFERENCE_MISMATCH")

        expected_status = _expected_status(memory)
        if self.status != expected_status:
            _fail("INVALID_LEARNING_STATUS")

        if self.learning_id != _learning_id(
            memory,
            learning_signal,
            adaptation_notes,
            learned_at,
        ):
            _fail("INVALID_LEARNING_ID")

    @property
    def explanation(self):
        return self.memory.explanation

    @property
    def planning(self):
        return self.memory.planning

    @property
    def prediction(self):
        return self.memory.prediction

    @property
    def governance(self):
        return self.memory.governance

    @property
    def tenant_id(self) -> str:
        return self.memory.tenant_id

    @property
    def principal_id(self) -> str:
        return self.memory.principal_id

    @property
    def request_id(self) -> str:
        return self.memory.request_id

    @property
    def correlation_id(self) -> str:
        return self.memory.correlation_id

    @property
    def plan_id(self) -> str:
        return self.memory.plan_id

    @property
    def decision_id(self) -> str:
        return self.memory.decision_id

    @property
    def target_domain(self) -> str:
        return self.memory.target_domain

    @property
    def prediction_id(self) -> str:
        return self.memory.prediction_id

    @property
    def governance_id(self) -> str:
        return self.memory.governance_id

    @property
    def explanation_id(self) -> str:
        return self.memory.explanation_id

    @property
    def memory_id(self) -> str:
        return self.memory.memory_id

    @property
    def evidence_count(self) -> int:
        return len(self.evidence_references)


class ExecutiveLearningEngine:
    """Stateless builder for immutable advisory learning envelopes."""

    __slots__ = ()

    def build_learning(
        self,
        memory: ExecutiveMemoryRecord,
        learning_signal: str,
        adaptation_notes: tuple[str, ...],
        *,
        learned_at: datetime | None = None,
    ) -> ExecutiveLearningResult:
        validated_memory = _validate_memory(memory)
        validated_signal = _validate_learning_signal(learning_signal)
        validated_notes = _validate_adaptation_notes(adaptation_notes)

        if learned_at is None:
            resolved_learned_at = datetime.now(timezone.utc)
        else:
            resolved_learned_at = _validate_learned_at(learned_at)

        return ExecutiveLearningResult(
            learning_id=_learning_id(
                validated_memory,
                validated_signal,
                validated_notes,
                resolved_learned_at,
            ),
            learned_at=resolved_learned_at,
            memory=validated_memory,
            learning_signal=validated_signal,
            adaptation_notes=validated_notes,
            evidence_references=validated_memory.evidence_references,
            status=_expected_status(validated_memory),
        )


executive_learning_engine = ExecutiveLearningEngine()


__all__ = (
    "VERSION",
    "ExecutiveLearningError",
    "ExecutiveLearningResult",
    "ExecutiveLearningEngine",
    "executive_learning_engine",
)

# Executive Learning grants no fact, evidence, legal, compliance, persistence, model-mutation, workflow, payment, or execution authority.
# Caller-supplied learning signals and adaptation notes remain advisory metadata only.
# Kennel EOS remains the exclusive financial execution authority.
# END OF WILSY OS SOVEREIGN PRODUCTION
