"""WILSY OS — Executive Intelligence evidence-bound facade.

TITLE: WILSY Executive Intelligence Evidence-Bound Projection Facade
VERSION: v1.0.0-WILSY-EXECUTIVE-INTELLIGENCE-PROJECTION
AUTHORITY: Wilsy OS Core Governance; Python EOS sovereign intelligence truth
PURPOSE: Project one validated ExecutiveLearningResult into an immutable
evidence-preserving intelligence envelope without manufacturing evidence,
facts, identity, seals, traces, model output, workflow authority, or execution
authority.
EPITOME: The facade is a stateless projection boundary over already-validated
Python EOS intelligence and is never an independent source of truth.
ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tools/eos/executive/intelligence/executive_intelligence_facade.py
CERTIFICATION/UPDATE DATE: 2026-09-03

TENANT BOUNDARY:
Tenant and principal identity derive exclusively from the supplied
ExecutiveLearningResult lineage. Caller headers, defaults, mutable state, or
transport metadata cannot establish or replace identity.

EVIDENCE BOUNDARY:
NO EVIDENCE = NO FACT. The facade preserves the exact evidence-reference tuple
already held by ExecutiveLearningResult and creates no evidence.

LEARNING BOUNDARY:
ExecutiveLearningResult is the sole upstream intelligence input. Learning is
advisory provenance only and grants no fact, model mutation, approval,
authorization, workflow, or execution authority.

STATE BOUNDARY:
Stateless and non-persistent. No cache, registry, trace store, tenant state,
history, network, filesystem, database, or subprocess authority.

CRYPTOGRAPHIC BOUNDARY:
No synthetic forensic seal or verification claim is generated. Existing
upstream provenance remains sovereign.

MODEL / RETRIEVAL BOUNDARY:
None.

WORKFLOW / EXECUTION BOUNDARY:
None. The facade cannot dispatch, approve, authorize, release, pay, transfer,
settle, persist, or execute.

FINANCIAL EXECUTION AUTHORITY:
Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha3_512
from typing import cast

from tools.eos.executive.intelligence.executive_learning_engine import (
    ExecutiveLearningResult,
)


VERSION = "v1.0.0-WILSY-EXECUTIVE-INTELLIGENCE-PROJECTION"

_PROJECTION_PREFIX = "INTEL-"
_PROJECTION_HEX_LENGTH = 16
_STATUS_NO_EVIDENCE = "NO_EVIDENCE"
_STATUS_EVIDENCE_BOUND = "EVIDENCE_BOUND"


class ExecutiveIntelligenceFacadeError(ValueError):
    """Stable fail-closed Executive Intelligence facade contract error."""


def _fail(code: str) -> None:
    raise ExecutiveIntelligenceFacadeError(code)


def _frame_text(value: str) -> bytes:
    raw = value.encode("utf-8")
    return len(raw).to_bytes(8, "big") + raw


def _validate_projected_at(value: object) -> datetime:
    if (
        type(value) is not datetime
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        _fail("INVALID_PROJECTED_AT")

    return cast(datetime, value)


def _validate_learning(value: object) -> ExecutiveLearningResult:
    if type(value) is not ExecutiveLearningResult:
        _fail("INVALID_LEARNING_TYPE")

    learning = cast(
        ExecutiveLearningResult,
        value,
    )

    try:
        ExecutiveLearningResult(
            learning_id=learning.learning_id,
            learned_at=learning.learned_at,
            memory=learning.memory,
            learning_signal=learning.learning_signal,
            adaptation_notes=learning.adaptation_notes,
            evidence_references=learning.evidence_references,
            status=learning.status,
        )
    except (ValueError, TypeError, AttributeError):
        _fail("INVALID_LEARNING_PROVENANCE")

    return learning


def _expected_status(
    learning: ExecutiveLearningResult,
) -> str:
    if learning.evidence_count == 0:
        return _STATUS_NO_EVIDENCE

    return _STATUS_EVIDENCE_BOUND


def _projection_id(
    learning: ExecutiveLearningResult,
    projected_at: datetime,
) -> str:
    hasher = sha3_512()

    for component in (
        learning.tenant_id,
        learning.principal_id,
        learning.request_id,
        learning.correlation_id,
        learning.decision_id,
        learning.plan_id,
        learning.target_domain,
        learning.prediction_id,
        learning.governance_id,
        learning.explanation_id,
        learning.memory_id,
        learning.learning_id,
        projected_at.isoformat(),
    ):
        hasher.update(_frame_text(component))

    return (
        _PROJECTION_PREFIX
        + hasher.hexdigest()[:_PROJECTION_HEX_LENGTH]
    )


def _valid_projection_id(value: object) -> bool:
    if type(value) is not str:
        return False

    if len(value) != (
        len(_PROJECTION_PREFIX)
        + _PROJECTION_HEX_LENGTH
    ):
        return False

    if not value.startswith(_PROJECTION_PREFIX):
        return False

    suffix = value[len(_PROJECTION_PREFIX):]

    return all(
        character in "0123456789abcdef"
        for character in suffix
    )


@dataclass(frozen=True, slots=True)
class ExecutiveIntelligenceProjection:
    """Immutable projection of one validated ExecutiveLearningResult."""

    projection_id: str
    projected_at: datetime
    learning: ExecutiveLearningResult
    evidence_references: tuple[object, ...]
    status: str

    def __post_init__(self) -> None:
        if not _valid_projection_id(
            self.projection_id
        ):
            _fail("INVALID_INTELLIGENCE_ID")

        projected_at = _validate_projected_at(
            self.projected_at
        )

        learning = _validate_learning(
            self.learning
        )

        if type(self.evidence_references) is not tuple:
            _fail(
                "INVALID_INTELLIGENCE_REFERENCE_TYPE"
            )

        if (
            self.evidence_references
            is not learning.evidence_references
        ):
            _fail("EVIDENCE_REFERENCE_MISMATCH")

        if self.status != _expected_status(
            learning
        ):
            _fail("INVALID_INTELLIGENCE_STATUS")

        if self.projection_id != _projection_id(
            learning,
            projected_at,
        ):
            _fail("INVALID_INTELLIGENCE_ID")

    @property
    def memory(self):
        return self.learning.memory

    @property
    def explanation(self):
        return self.learning.explanation

    @property
    def prediction(self):
        return self.learning.prediction

    @property
    def governance(self):
        return self.learning.governance

    @property
    def planning(self):
        return self.learning.planning

    @property
    def tenant_id(self) -> str:
        return self.learning.tenant_id

    @property
    def principal_id(self) -> str:
        return self.learning.principal_id

    @property
    def request_id(self) -> str:
        return self.learning.request_id

    @property
    def correlation_id(self) -> str:
        return self.learning.correlation_id

    @property
    def decision_id(self) -> str:
        return self.learning.decision_id

    @property
    def plan_id(self) -> str:
        return self.learning.plan_id

    @property
    def target_domain(self) -> str:
        return self.learning.target_domain

    @property
    def prediction_id(self) -> str:
        return self.learning.prediction_id

    @property
    def governance_id(self) -> str:
        return self.learning.governance_id

    @property
    def explanation_id(self) -> str:
        return self.learning.explanation_id

    @property
    def memory_id(self) -> str:
        return self.learning.memory_id

    @property
    def learning_id(self) -> str:
        return self.learning.learning_id

    @property
    def learning_signal(self) -> str:
        return self.learning.learning_signal

    @property
    def adaptation_notes(
        self,
    ) -> tuple[str, ...]:
        return self.learning.adaptation_notes

    @property
    def evidence_count(self) -> int:
        return self.learning.evidence_count


class ExecutiveIntelligenceFacade:
    """Stateless projector over validated Python EOS learning provenance."""

    __slots__ = ()

    def project_intelligence(
        self,
        learning: ExecutiveLearningResult,
        *,
        projected_at: datetime | None = None,
    ) -> ExecutiveIntelligenceProjection:
        validated_learning = _validate_learning(
            learning
        )

        resolved_projected_at = (
            datetime.now(timezone.utc)
            if projected_at is None
            else _validate_projected_at(
                projected_at
            )
        )

        return ExecutiveIntelligenceProjection(
            projection_id=_projection_id(
                validated_learning,
                resolved_projected_at,
            ),
            projected_at=resolved_projected_at,
            learning=validated_learning,
            evidence_references=(
                validated_learning.evidence_references
            ),
            status=_expected_status(
                validated_learning
            ),
        )


executive_intelligence_facade = (
    ExecutiveIntelligenceFacade()
)


__all__ = (
    "VERSION",
    "ExecutiveIntelligenceFacadeError",
    "ExecutiveIntelligenceProjection",
    "ExecutiveIntelligenceFacade",
    "executive_intelligence_facade",
)


# AUTHORITY POSTURE:
# Python EOS remains sovereign business/intelligence truth.
#
# TENANT POSTURE:
# No default tenant, header-derived tenant, mutable tenant, or caller override.
#
# EVIDENCE POSTURE:
# NO EVIDENCE = NO FACT. Exact Learning evidence references are preserved.
#
# CRYPTOGRAPHIC POSTURE:
# No synthetic seal generation or verification claim.
#
# MODEL / RETRIEVAL POSTURE:
# None.
#
# WORKFLOW / EXECUTION POSTURE:
# None.
#
# FINANCIAL EXECUTION AUTHORITY:
# Kennel EOS exclusively.
#
# END OF WILSY OS SOVEREIGN PRODUCTION
