"""WILSY OS — Executive Intelligence Facade direct certificate.

TITLE: Executive Intelligence Evidence-Bound Projection Direct Certificate
VERSION: v1.0.0-WILSY-EXECUTIVE-INTELLIGENCE-PROJECTION-CERT
AUTHORITY: Wilsy OS Core Governance; Python EOS sovereign intelligence truth
PURPOSE: Directly and adversarially certify the Executive Intelligence facade.
EPITOME: The facade projects only validated ExecutiveLearningResult provenance;
it creates no evidence, identity, synthetic verification, workflow authority,
model authority, or execution authority.
CERTIFICATION/UPDATE DATE: 2026-09-03
"""

from __future__ import annotations

import hashlib
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

import pytest

from tools.eos.kernel.domain.kernel_bootstrap_request import (
    KernelBootstrapRequest,
)
from tools.eos.executive.intelligence.executive_context_engine import (
    ExecutiveContext,
    ExecutiveEvidence,
)
from tools.eos.executive.intelligence.executive_reasoning_engine import (
    executive_reasoning_engine,
)
from tools.eos.executive.intelligence.executive_decision_engine import (
    executive_decision_engine,
)
from tools.eos.executive.intelligence.executive_planning_engine import (
    executive_planning_engine,
)
from tools.eos.executive.intelligence.executive_prediction_engine import (
    executive_prediction_engine,
)
from tools.eos.executive.intelligence.executive_governance_engine import (
    executive_governance_engine,
)
from tools.eos.executive.intelligence.executive_explanation_engine import (
    executive_explanation_engine,
)
from tools.eos.executive.intelligence.executive_memory_engine import (
    executive_memory_engine,
)
from tools.eos.executive.intelligence.executive_learning_engine import (
    ExecutiveLearningResult,
    executive_learning_engine,
)
from tools.eos.executive.intelligence.executive_intelligence_facade import (
    VERSION,
    ExecutiveIntelligenceFacade,
    ExecutiveIntelligenceFacadeError,
    ExecutiveIntelligenceProjection,
    executive_intelligence_facade,
)


PRODUCTION_PATH = Path(
    "tools/eos/executive/intelligence/"
    "executive_intelligence_facade.py"
)

PRODUCTION_BYTES = 9945

PRODUCTION_SHA3_512 = (
    "521d790b3782ad2e8ceebced3f3ba47d5cc0d613d92aa2b9989d0e51e5b2151"
    "15d6a6cd0f5c82f6611ebbad6aacc1b328d3b028f308b5687b179c9510ea540ce"
)

STAMP = datetime(
    2026,
    9,
    3,
    0,
    0,
    0,
    tzinfo=timezone.utc,
)


def _evidence(
    evidence_id: str = "evidence-a",
    *,
    content: str = "verified source fact",
) -> ExecutiveEvidence:
    return ExecutiveEvidence(
        evidence_id,
        "tenant-a",
        "principal-a",
        "request-a",
        "source-a",
        "document",
        "repo://source-a",
        "page:1",
        content,
        hashlib.sha3_512(
            content.encode("utf-8")
        ).hexdigest(),
        "receipt-a",
        STAMP,
        None,
    )


def _learning(
    evidence: tuple[ExecutiveEvidence, ...] = (),
    *,
    request_id: str = "request-a",
) -> ExecutiveLearningResult:
    request = KernelBootstrapRequest(
        "tenant-a",
        "principal-a",
        request_id,
        "correlation-a",
    )

    context = ExecutiveContext(
        request,
        evidence,
        STAMP,
    )

    reasoning = executive_reasoning_engine.evaluate_query(
        "evaluate evidence",
        context,
        evaluated_at=STAMP,
    )

    decision = executive_decision_engine.evaluate_decision(
        "consider options",
        "operations",
        reasoning,
        evaluated_at=STAMP,
    )

    planning = executive_planning_engine.build_plan(
        "plan advisory work",
        ("review",),
        decision,
        planned_at=STAMP,
    )

    prediction = executive_prediction_engine.build_prediction(
        "consider possible outcomes",
        ("target",),
        planning,
        predicted_at=STAMP,
    )

    governance = executive_governance_engine.build_review(
        "review governance metadata",
        ("scope",),
        planning,
        reviewed_at=STAMP,
    )

    explanation = executive_explanation_engine.build_explanation(
        "explain evidence lineage",
        ("lineage",),
        prediction,
        governance,
        explained_at=STAMP,
    )

    memory = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP,
    )

    return executive_learning_engine.build_learning(
        memory,
        "advisory learning signal",
        ("preserve evidence lineage",),
        learned_at=STAMP,
    )


def _projection(
    learning: ExecutiveLearningResult,
    *,
    at: datetime = STAMP,
) -> ExecutiveIntelligenceProjection:
    return executive_intelligence_facade.project_intelligence(
        learning,
        projected_at=at,
    )


def _fails(
    code: str,
    operation: Callable[[], object],
) -> None:
    with pytest.raises(
        ExecutiveIntelligenceFacadeError
    ) as caught:
        operation()

    assert str(caught.value) == code


def test_production_identity() -> None:
    raw = PRODUCTION_PATH.read_bytes()

    assert len(raw) == PRODUCTION_BYTES
    assert (
        hashlib.sha3_512(raw).hexdigest()
        == PRODUCTION_SHA3_512
    )

    assert (
        VERSION
        == "v1.0.0-WILSY-EXECUTIVE-INTELLIGENCE-PROJECTION"
    )


def test_public_surface_is_projection_only() -> None:
    assert isinstance(
        executive_intelligence_facade,
        ExecutiveIntelligenceFacade,
    )

    public_methods = {
        name
        for name, value
        in ExecutiveIntelligenceFacade.__dict__.items()
        if not name.startswith("_")
        and callable(value)
    }

    assert public_methods == {
        "project_intelligence",
    }

    for forbidden in (
        "set_trace_id",
        "get_trace_id",
        "seal_intelligence_response",
        "verify_sealed_response",
        "health_check",
        "execute",
        "dispatch",
        "approve",
        "authorize",
        "release",
        "pay",
        "transfer",
        "settle",
        "persist",
        "retrieve",
        "fetch",
        "query_model",
        "predict_with_model",
    ):
        assert not hasattr(
            executive_intelligence_facade,
            forbidden,
        )


def test_no_evidence_no_fact_projection() -> None:
    learning = _learning()
    projection = _projection(learning)

    assert projection.status == "NO_EVIDENCE"
    assert projection.evidence_count == 0
    assert projection.evidence_references == ()
    assert (
        projection.evidence_references
        is learning.evidence_references
    )


def test_evidence_bound_exact_reference_identity() -> None:
    learning = _learning(
        (
            _evidence(),
            _evidence(
                "evidence-b",
                content="second verified fact",
            ),
        )
    )

    projection = _projection(learning)

    assert projection.status == "EVIDENCE_BOUND"
    assert projection.evidence_count == 2
    assert (
        projection.evidence_references
        is learning.evidence_references
    )


def test_full_identity_lineage_is_inherited() -> None:
    learning = _learning()
    projection = _projection(learning)

    assert projection.learning is learning
    assert projection.memory is learning.memory
    assert projection.explanation is learning.explanation
    assert projection.prediction is learning.prediction
    assert projection.governance is learning.governance
    assert projection.planning is learning.planning

    assert projection.tenant_id == learning.tenant_id
    assert projection.principal_id == learning.principal_id
    assert projection.request_id == learning.request_id
    assert projection.correlation_id == learning.correlation_id
    assert projection.decision_id == learning.decision_id
    assert projection.plan_id == learning.plan_id
    assert projection.target_domain == learning.target_domain

    assert projection.prediction_id == learning.prediction_id
    assert projection.governance_id == learning.governance_id
    assert projection.explanation_id == learning.explanation_id
    assert projection.memory_id == learning.memory_id
    assert projection.learning_id == learning.learning_id

    assert projection.learning_signal == learning.learning_signal
    assert projection.adaptation_notes == learning.adaptation_notes


def test_projection_id_is_deterministic_and_lineage_bound() -> None:
    first_learning = _learning(
        request_id="request-a"
    )
    second_learning = _learning(
        request_id="request-b"
    )

    first = _projection(first_learning)
    repeat = _projection(first_learning)
    second = _projection(second_learning)

    assert first.projection_id == repeat.projection_id
    assert first.projection_id != second.projection_id

    later = _projection(
        first_learning,
        at=STAMP + timedelta(seconds=1),
    )

    assert first.projection_id != later.projection_id


@pytest.mark.parametrize(
    "bad",
    [
        None,
        True,
        False,
        0,
        1.5,
        b"x",
        "learning",
        (),
        [],
        {},
        object(),
    ],
)
def test_learning_type_fails_closed(
    bad: object,
) -> None:
    _fails(
        "INVALID_LEARNING_TYPE",
        lambda: executive_intelligence_facade.project_intelligence(
            bad,  # type: ignore[arg-type]
            projected_at=STAMP,
        ),
    )


@pytest.mark.parametrize(
    "bad",
    [
        True,
        False,
        0,
        1.5,
        "2026-09-03",
        b"x",
        datetime(2026, 9, 3),
        object(),
    ],
)
def test_projected_at_fails_closed(
    bad: object,
) -> None:
    _fails(
        "INVALID_PROJECTED_AT",
        lambda: executive_intelligence_facade.project_intelligence(
            _learning(),
            projected_at=bad,  # type: ignore[arg-type]
        ),
    )


def test_projected_at_none_resolves_aware_utc() -> None:
    projection = (
        executive_intelligence_facade.project_intelligence(
            _learning(),
            projected_at=None,
        )
    )

    assert isinstance(
        projection.projected_at,
        datetime,
    )
    assert projection.projected_at.tzinfo is not None
    assert projection.projected_at.utcoffset() == timedelta(0)


def test_non_utc_projected_at_fails_closed() -> None:
    non_utc = datetime(
        2026,
        9,
        3,
        tzinfo=timezone(
            timedelta(hours=2)
        ),
    )

    _fails(
        "INVALID_PROJECTED_AT",
        lambda: _projection(
            _learning(),
            at=non_utc,
        ),
    )


def test_direct_constructor_rejects_forgery() -> None:
    learning = _learning()
    projection = _projection(learning)

    forged_id = "INTEL-" + ("0" * 16)

    _fails(
        "INVALID_INTELLIGENCE_ID",
        lambda: replace(
            projection,
            projection_id=forged_id,
        ),
    )

    _fails(
        "INVALID_INTELLIGENCE_STATUS",
        lambda: replace(
            projection,
            status="EVIDENCE_BOUND",
        ),
    )

    _fails(
        "INVALID_INTELLIGENCE_REFERENCE_TYPE",
        lambda: ExecutiveIntelligenceProjection(
            projection.projection_id,
            projection.projected_at,
            projection.learning,
            [],  # type: ignore[arg-type]
            projection.status,
        ),
    )


def test_reference_copy_or_substitution_fails_closed() -> None:
    learning = _learning(
        (
            _evidence(),
        )
    )
    projection = _projection(learning)

    copied = tuple(
        list(projection.evidence_references)
    )

    assert copied == projection.evidence_references

    # Force a distinct tuple object even for one item.
    copied = tuple(
        [*projection.evidence_references, object()]
    )[:-1]

    assert copied == projection.evidence_references
    assert copied is not projection.evidence_references

    _fails(
        "EVIDENCE_REFERENCE_MISMATCH",
        lambda: replace(
            projection,
            evidence_references=copied,
        ),
    )


def test_immutability_slots_and_statelessness() -> None:
    learning = _learning()
    projection = _projection(learning)

    with pytest.raises(FrozenInstanceError):
        projection.status = "NO_EVIDENCE"  # type: ignore[misc]

    with pytest.raises((AttributeError, TypeError)):
        projection.extra = "x"  # type: ignore[attr-defined]

    for forbidden_state in (
        "__dict__",
        "_tenant_id",
        "tenant_id",
        "_trace_id",
        "_state",
        "_cache",
        "cache",
        "_history",
        "history",
        "_registry",
        "registry",
        "_lock",
        "_instance",
    ):
        assert not hasattr(
            executive_intelligence_facade,
            forbidden_state,
        )


def test_upstream_learning_provenance_is_revalidated() -> None:
    learning = _learning(
        (
            _evidence(),
        )
    )

    forged = object.__new__(
        ExecutiveLearningResult
    )

    object.__setattr__(
        forged,
        "learning_id",
        learning.learning_id,
    )
    object.__setattr__(
        forged,
        "learned_at",
        learning.learned_at,
    )
    object.__setattr__(
        forged,
        "memory",
        learning.memory,
    )
    object.__setattr__(
        forged,
        "learning_signal",
        learning.learning_signal,
    )
    object.__setattr__(
        forged,
        "adaptation_notes",
        learning.adaptation_notes,
    )
    object.__setattr__(
        forged,
        "evidence_references",
        (),
    )
    object.__setattr__(
        forged,
        "status",
        learning.status,
    )

    _fails(
        "INVALID_LEARNING_PROVENANCE",
        lambda: executive_intelligence_facade.project_intelligence(
            forged,
            projected_at=STAMP,
        ),
    )


def test_errors_are_stable_and_non_echoing() -> None:
    class Private:
        def __str__(self) -> str:
            return "PRIVATE_SECRET"

        def __repr__(self) -> str:
            return "PRIVATE_SECRET"

    secret = Private()

    with pytest.raises(
        ExecutiveIntelligenceFacadeError
    ) as caught:
        executive_intelligence_facade.project_intelligence(
            secret,  # type: ignore[arg-type]
            projected_at=STAMP,
        )

    message = str(caught.value)

    assert message == "INVALID_LEARNING_TYPE"
    assert "PRIVATE_SECRET" not in message
