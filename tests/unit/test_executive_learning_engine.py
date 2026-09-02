"""WILSY OS — Executive Learning direct certificate.

TITLE: Executive Learning Evidence-Bound Direct Certificate
VERSION: v1.0.0-WILSY-EXECUTIVE-LEARNING-CERT
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
PURPOSE: Certify the frozen Executive Learning production contract directly and adversarially.
EPITOME: Learning binds advisory metadata to one validated Memory lineage without creating evidence, persistence, model mutation, workflow authority, or execution authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_executive_learning_engine.py
CERTIFICATION/UPDATE DATE: 2026-09-02
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import os
import subprocess
import sys
from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

import pytest

from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest
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
    ExecutiveExplanationResult,
    executive_explanation_engine,
)
from tools.eos.executive.intelligence.executive_memory_engine import (
    ExecutiveMemoryEngine,
    ExecutiveMemoryRecord,
)
from tools.eos.executive.intelligence.executive_learning_engine import (
    VERSION,
    ExecutiveLearningEngine,
    ExecutiveLearningError,
    ExecutiveLearningResult,
    executive_learning_engine,
)


CERT_VERSION = "v1.0.0-WILSY-EXECUTIVE-LEARNING-CERT"
PRODUCTION_VERSION = "v1.0.0-WILSY-EXECUTIVE-LEARNING-EVIDENCE"
PRODUCTION_PATH = Path(
    "tools/eos/executive/intelligence/executive_learning_engine.py"
)
CERTIFICATE_PATH = Path(
    "tests/unit/test_executive_learning_engine.py"
)

PRODUCTION_BYTES = 8592
PRODUCTION_SHA3_512 = (
    "9627e097c972d6de7b92a50aad01e4cea89d05936953f912493e29b9fa5e7df7"
    "2fe5199a0206d330a47772fbfd0a0b9769a79ee0739d5965dcd1d489de372b8e"
)
PRODUCTION_AST_SHA3_512 = (
    "3274f4f1e5fc0617b9eba91c07dbea0b5b0f22b95309166bbb2d899225dc933a"
    "47f78f8867bcddbe73857b1586ffbb97a65bb4ce36ca2b620071bab6ef11a72d"
)
PRODUCTION_GIT_BLOB = "e9d0edca22b9cc39caa065e8e1b050f3e1347b68"
PRODUCTION_COMMIT = "183a59bf8c68df2dcfbf3e3d77cce33ff8741b30"

STAMP = datetime(
    2026,
    9,
    2,
    22,
    31,
    47,
    314159,
    tzinfo=timezone.utc,
)

EXPECTED_FIELDS = (
    "learning_id",
    "learned_at",
    "memory",
    "learning_signal",
    "adaptation_notes",
    "evidence_references",
    "status",
)

EXPECTED_PROPERTIES = (
    "explanation",
    "planning",
    "prediction",
    "governance",
    "tenant_id",
    "principal_id",
    "request_id",
    "correlation_id",
    "plan_id",
    "decision_id",
    "target_domain",
    "prediction_id",
    "governance_id",
    "explanation_id",
    "memory_id",
    "evidence_count",
)

EXPECTED_STABLE_ERRORS = {
    "INVALID_LEARNING_ID",
    "INVALID_LEARNED_AT",
    "INVALID_MEMORY_TYPE",
    "INVALID_MEMORY_PROVENANCE",
    "EVIDENCE_REFERENCE_MISMATCH",
    "INVALID_LEARNING_SIGNAL",
    "INVALID_ADAPTATION_NOTES",
    "INVALID_LEARNING_STATUS",
}


def _frame_text(value: str) -> bytes:
    raw = value.encode("utf-8")
    return len(raw).to_bytes(8, "big") + raw


def _independent_id(
    memory: ExecutiveMemoryRecord,
    learning_signal: str,
    adaptation_notes: tuple[str, ...],
    stamp: datetime,
) -> str:
    hasher = hashlib.sha3_512()

    for component in (
        memory.tenant_id,
        memory.principal_id,
        memory.request_id,
        memory.correlation_id,
        memory.memory_id,
        memory.explanation_id,
        learning_signal,
    ):
        hasher.update(_frame_text(component))

    hasher.update(len(adaptation_notes).to_bytes(8, "big"))

    for note in adaptation_notes:
        hasher.update(_frame_text(note))

    hasher.update(_frame_text(stamp.isoformat()))
    return "LEARN-" + hasher.hexdigest()[:16]


def _canonical_ast_sha(raw: bytes) -> str:
    tree = ast.parse(raw.decode("utf-8"))
    targets = (
        ast.Module,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.ClassDef,
    )

    def is_doc(node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )

    def strip(node: ast.AST) -> None:
        if isinstance(node, targets):
            body = getattr(node, "body", None)
            if isinstance(body, list) and body and is_doc(body[0]):
                del body[0]

        for child in ast.iter_child_nodes(node):
            strip(child)

    strip(tree)
    ast.fix_missing_locations(tree)
    material = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    ).encode("utf-8")
    return hashlib.sha3_512(material).hexdigest()


def _git_blob_sha1(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def _expect_error(
    code: str,
    operation: Callable[[], object],
) -> None:
    with pytest.raises(ExecutiveLearningError) as exc_info:
        operation()

    message = str(exc_info.value)
    assert message == code
    assert "PRIVATE_SECRET" not in message
    assert "tenant-secret" not in message
    assert "principal-secret" not in message
    assert "ADVISORY_PRIVATE" not in message


def _build_explanation(
    tag: str,
    evidence_count: int,
) -> ExecutiveExplanationResult:
    authority = KernelBootstrapRequest(
        tenant_id=f"tenant-{tag}",
        principal_id=f"principal-{tag}",
        request_id=f"request-{tag}",
        correlation_id=f"correlation-{tag}",
    )

    evidence = []
    for index in range(evidence_count):
        content = f"PRIVATE_SECRET_{tag}_{index}"
        evidence.append(
            ExecutiveEvidence(
                evidence_id=f"evidence-{tag}-{index}",
                tenant_id=authority.tenant_id,
                principal_id=authority.principal_id,
                request_id=authority.request_id,
                source_id=f"source-{tag}-{index}",
                source_type="document",
                source_locator=f"private://{tag}/{index}",
                citation_locator=f"citation-{tag}-{index}",
                content=content,
                content_sha3_512=hashlib.sha3_512(
                    content.encode("utf-8")
                ).hexdigest(),
                authorization_receipt_ref=f"receipt-{tag}-{index}",
                retrieved_at=STAMP,
                source_version="v1",
            )
        )

    context = ExecutiveContext(
        authority=authority,
        evidence=tuple(evidence),
        assembled_at=STAMP,
    )
    reasoning = executive_reasoning_engine.evaluate_query(
        f"reasoning-{tag}",
        context,
        evaluated_at=STAMP,
    )
    decision = executive_decision_engine.evaluate_decision(
        f"decision-{tag}",
        f"domain-{tag}",
        reasoning,
        evaluated_at=STAMP,
    )
    planning = executive_planning_engine.build_plan(
        f"planning-{tag}",
        (
            f"step-{tag}-one",
            f"step-{tag}-two",
        ),
        decision,
        planned_at=STAMP,
    )
    prediction = executive_prediction_engine.build_prediction(
        f"prediction-{tag}",
        (f"target-{tag}",),
        planning,
        predicted_at=STAMP,
    )
    governance = executive_governance_engine.build_review(
        f"governance-{tag}",
        (f"scope-{tag}",),
        planning,
        reviewed_at=STAMP,
    )
    return executive_explanation_engine.build_explanation(
        f"explanation-{tag}",
        (f"topic-{tag}",),
        prediction,
        governance,
        explained_at=STAMP,
    )


def _build_memory(
    tag: str,
    evidence_count: int,
) -> tuple[ExecutiveExplanationResult, ExecutiveMemoryRecord]:
    explanation = _build_explanation(tag, evidence_count)
    memory = ExecutiveMemoryEngine().build_memory(
        explanation,
        recorded_at=STAMP,
    )
    return explanation, memory


def test_certificate_version() -> None:
    assert CERT_VERSION == "v1.0.0-WILSY-EXECUTIVE-LEARNING-CERT"


def test_production_version() -> None:
    assert VERSION == PRODUCTION_VERSION


def test_production_identity() -> None:
    raw = PRODUCTION_PATH.read_bytes()

    assert len(raw) == PRODUCTION_BYTES
    assert hashlib.sha3_512(raw).hexdigest() == PRODUCTION_SHA3_512
    assert _canonical_ast_sha(raw) == PRODUCTION_AST_SHA3_512
    assert _git_blob_sha1(raw) == PRODUCTION_GIT_BLOB


def test_production_commit_is_frozen() -> None:
    assert PRODUCTION_COMMIT == "183a59bf8c68df2dcfbf3e3d77cce33ff8741b30"


def test_certificate_path_is_exact() -> None:
    assert CERTIFICATE_PATH.as_posix() == (
        "tests/unit/test_executive_learning_engine.py"
    )


def test_public_result_fields() -> None:
    assert tuple(
        field.name
        for field in fields(ExecutiveLearningResult)
    ) == EXPECTED_FIELDS


def test_public_result_properties() -> None:
    assert tuple(
        name
        for name, value in ExecutiveLearningResult.__dict__.items()
        if isinstance(value, property)
    ) == EXPECTED_PROPERTIES


def test_result_dataclass_is_frozen_and_slotted() -> None:
    _, memory = _build_memory("result-slots", 0)
    result = executive_learning_engine.build_learning(
        memory,
        "result-slots-signal",
        (),
        learned_at=STAMP,
    )

    assert ExecutiveLearningResult.__dataclass_params__.frozen is True
    assert "__slots__" in ExecutiveLearningResult.__dict__
    assert not hasattr(result, "__dict__")


def test_engine_public_surface() -> None:
    assert tuple(
        name
        for name, value in ExecutiveLearningEngine.__dict__.items()
        if callable(value) and not name.startswith("_")
    ) == ("build_learning",)


def test_build_learning_signature() -> None:
    signature = inspect.signature(ExecutiveLearningEngine.build_learning)

    assert tuple(signature.parameters) == (
        "self",
        "memory",
        "learning_signal",
        "adaptation_notes",
        "learned_at",
    )
    assert (
        signature.parameters["learned_at"].kind
        is inspect.Parameter.KEYWORD_ONLY
    )
    assert signature.parameters["learned_at"].default is None


def test_engine_is_stateless_and_non_singleton() -> None:
    assert ExecutiveLearningEngine.__slots__ == ()
    assert not hasattr(executive_learning_engine, "__dict__")

    first = ExecutiveLearningEngine()
    second = ExecutiveLearningEngine()

    assert first is not second
    assert first is not executive_learning_engine
    assert second is not executive_learning_engine
    assert not hasattr(first, "__dict__")
    assert not hasattr(second, "__dict__")


def test_no_evidence_learning() -> None:
    explanation, memory = _build_memory("no-evidence", 0)
    notes: tuple[str, ...] = ()

    learning = executive_learning_engine.build_learning(
        memory,
        "advisory-no-evidence",
        notes,
        learned_at=STAMP,
    )

    assert learning.status == "NO_EVIDENCE"
    assert learning.evidence_count == 0
    assert learning.memory is memory
    assert learning.explanation is explanation
    assert learning.evidence_references is memory.evidence_references
    assert learning.learning_signal == "advisory-no-evidence"
    assert learning.adaptation_notes is notes


def test_evidence_bound_learning() -> None:
    explanation, memory = _build_memory("evidence-bound", 2)
    notes = (
        "advisory-evidence-one",
        "advisory-evidence-two",
    )

    learning = executive_learning_engine.build_learning(
        memory,
        "advisory-evidence",
        notes,
        learned_at=STAMP,
    )

    assert learning.status == "EVIDENCE_BOUND"
    assert learning.evidence_count == 2
    assert learning.memory is memory
    assert learning.explanation is explanation
    assert learning.evidence_references is memory.evidence_references
    assert learning.learning_signal == "advisory-evidence"
    assert learning.adaptation_notes is notes


def test_derived_provenance_binding() -> None:
    explanation, memory = _build_memory("derived", 1)

    learning = executive_learning_engine.build_learning(
        memory,
        "derived-signal",
        ("derived-note",),
        learned_at=STAMP,
    )

    assert learning.explanation is explanation
    assert learning.planning is memory.planning
    assert learning.prediction is memory.prediction
    assert learning.governance is memory.governance
    assert learning.tenant_id == memory.tenant_id
    assert learning.principal_id == memory.principal_id
    assert learning.request_id == memory.request_id
    assert learning.correlation_id == memory.correlation_id
    assert learning.plan_id == memory.plan_id
    assert learning.decision_id == memory.decision_id
    assert learning.target_domain == memory.target_domain
    assert learning.prediction_id == memory.prediction_id
    assert learning.governance_id == memory.governance_id
    assert learning.explanation_id == memory.explanation_id
    assert learning.memory_id == memory.memory_id


def test_learning_signal_and_notes_are_exact_advisory_bindings() -> None:
    _, memory = _build_memory("advisory-bindings", 1)
    signal = "  advisory signal remains exact  "
    notes = (
        " first note exact ",
        "second-note",
    )

    learning = executive_learning_engine.build_learning(
        memory,
        signal,
        notes,
        learned_at=STAMP,
    )

    assert learning.learning_signal == signal
    assert learning.adaptation_notes is notes


def test_independent_learning_id_oracle() -> None:
    _, memory = _build_memory("id-oracle", 2)
    signal = "ADVISORY_PRIVATE_SIGNAL"
    notes = (
        "ADVISORY_PRIVATE_NOTE_ONE",
        "ADVISORY_PRIVATE_NOTE_TWO",
    )

    learning = executive_learning_engine.build_learning(
        memory,
        signal,
        notes,
        learned_at=STAMP,
    )

    assert learning.learning_id == _independent_id(
        memory,
        signal,
        notes,
        STAMP,
    )
    assert learning.learning_id.startswith("LEARN-")
    assert len(learning.learning_id) == 22
    assert all(
        character in "0123456789abcdef"
        for character in learning.learning_id[6:]
    )
    assert "ADVISORY_PRIVATE" not in learning.learning_id
    assert "PRIVATE_SECRET" not in learning.learning_id


def test_explicit_timestamp_determinism_across_instances() -> None:
    _, memory = _build_memory("deterministic", 1)
    notes = ("deterministic-note",)

    first = ExecutiveLearningEngine().build_learning(
        memory,
        "deterministic-signal",
        notes,
        learned_at=STAMP,
    )
    second = ExecutiveLearningEngine().build_learning(
        memory,
        "deterministic-signal",
        notes,
        learned_at=STAMP,
    )

    assert first == second
    assert first.learning_id == second.learning_id


def test_timestamp_changes_learning_id() -> None:
    _, memory = _build_memory("timestamp", 1)

    first = executive_learning_engine.build_learning(
        memory,
        "timestamp-signal",
        (),
        learned_at=STAMP,
    )
    second = executive_learning_engine.build_learning(
        memory,
        "timestamp-signal",
        (),
        learned_at=STAMP + timedelta(microseconds=1),
    )

    assert first.learning_id != second.learning_id


def test_signal_changes_learning_id() -> None:
    _, memory = _build_memory("signal-change", 1)

    first = executive_learning_engine.build_learning(
        memory,
        "signal-one",
        (),
        learned_at=STAMP,
    )
    second = executive_learning_engine.build_learning(
        memory,
        "signal-two",
        (),
        learned_at=STAMP,
    )

    assert first.learning_id != second.learning_id


def test_notes_content_changes_learning_id() -> None:
    _, memory = _build_memory("notes-content", 1)

    first = executive_learning_engine.build_learning(
        memory,
        "notes-signal",
        ("one", "two"),
        learned_at=STAMP,
    )
    second = executive_learning_engine.build_learning(
        memory,
        "notes-signal",
        ("one", "three"),
        learned_at=STAMP,
    )

    assert first.learning_id != second.learning_id


def test_notes_order_changes_learning_id() -> None:
    _, memory = _build_memory("notes-order", 1)

    first = executive_learning_engine.build_learning(
        memory,
        "notes-order-signal",
        ("one", "two"),
        learned_at=STAMP,
    )
    second = executive_learning_engine.build_learning(
        memory,
        "notes-order-signal",
        ("two", "one"),
        learned_at=STAMP,
    )

    assert first.learning_id != second.learning_id


def test_notes_count_changes_learning_id() -> None:
    _, memory = _build_memory("notes-count", 1)

    first = executive_learning_engine.build_learning(
        memory,
        "notes-count-signal",
        (),
        learned_at=STAMP,
    )
    second = executive_learning_engine.build_learning(
        memory,
        "notes-count-signal",
        ("note",),
        learned_at=STAMP,
    )

    assert first.learning_id != second.learning_id


def test_signal_is_not_normalized() -> None:
    _, memory = _build_memory("signal-space", 0)

    learning = executive_learning_engine.build_learning(
        memory,
        " ",
        (),
        learned_at=STAMP,
    )

    assert learning.learning_signal == " "
    assert learning.learning_id == _independent_id(
        memory,
        " ",
        (),
        STAMP,
    )


def test_default_timestamp_is_utc_and_bound_into_id() -> None:
    _, memory = _build_memory("default-time", 1)

    before = datetime.now(timezone.utc)
    learning = executive_learning_engine.build_learning(
        memory,
        "default-time-signal",
        (),
    )
    after = datetime.now(timezone.utc)

    assert before <= learning.learned_at <= after
    assert learning.learned_at.tzinfo is not None
    assert learning.learned_at.utcoffset() == timedelta(0)
    assert learning.learning_id == _independent_id(
        memory,
        "default-time-signal",
        (),
        learning.learned_at,
    )


@pytest.mark.parametrize(
    "invalid_memory",
    (
        None,
        object(),
        {},
        [],
        (),
        0,
        "PRIVATE_SECRET_MEMORY",
    ),
)
def test_invalid_memory_type_matrix(
    invalid_memory: object,
) -> None:
    _expect_error(
        "INVALID_MEMORY_TYPE",
        lambda: executive_learning_engine.build_learning(
            invalid_memory,  # type: ignore[arg-type]
            "signal",
            (),
            learned_at=STAMP,
        ),
    )


def test_adaptation_notes_tuple_subclass_is_rejected() -> None:
    _, memory = _build_memory("notes-subclass", 1)

    class NotesSubclass(tuple):
        pass

    notes = NotesSubclass(("note",))

    _expect_error(
        "INVALID_ADAPTATION_NOTES",
        lambda: executive_learning_engine.build_learning(
            memory,
            "signal",
            notes,  # type: ignore[arg-type]
            learned_at=STAMP,
        ),
    )


def test_memory_subclass_is_rejected_by_exact_type_boundary() -> None:
    _, memory = _build_memory("memory-subclass", 1)

    class MemorySubclass(ExecutiveMemoryRecord):
        pass

    subclass = MemorySubclass(
        memory_id=memory.memory_id,
        recorded_at=memory.recorded_at,
        explanation=memory.explanation,
        evidence_references=memory.evidence_references,
        status=memory.status,
    )

    _expect_error(
        "INVALID_MEMORY_TYPE",
        lambda: executive_learning_engine.build_learning(
            subclass,
            "signal",
            (),
            learned_at=STAMP,
        ),
    )


@pytest.mark.parametrize(
    "invalid_learned_at",
    (
        "PRIVATE_SECRET_TIME",
        0,
        object(),
        datetime(2026, 9, 2, 22, 31, 47),
        datetime(
            2026,
            9,
            2,
            22,
            31,
            47,
            tzinfo=timezone(timedelta(hours=2)),
        ),
    ),
)
def test_invalid_learned_at_matrix(
    invalid_learned_at: object,
) -> None:
    _, memory = _build_memory("invalid-time", 1)

    _expect_error(
        "INVALID_LEARNED_AT",
        lambda: executive_learning_engine.build_learning(
            memory,
            "signal",
            (),
            learned_at=invalid_learned_at,  # type: ignore[arg-type]
        ),
    )


@pytest.mark.parametrize(
    "invalid_signal",
    (
        None,
        "",
        0,
        object(),
        (),
    ),
)
def test_invalid_learning_signal_matrix(
    invalid_signal: object,
) -> None:
    _, memory = _build_memory("invalid-signal", 1)

    _expect_error(
        "INVALID_LEARNING_SIGNAL",
        lambda: executive_learning_engine.build_learning(
            memory,
            invalid_signal,  # type: ignore[arg-type]
            (),
            learned_at=STAMP,
        ),
    )


@pytest.mark.parametrize(
    "invalid_notes",
    (
        None,
        [],
        {},
        "",
        ("",),
        ("valid", 1),
        ("valid", None),
    ),
)
def test_invalid_adaptation_notes_matrix(
    invalid_notes: object,
) -> None:
    _, memory = _build_memory("invalid-notes", 1)

    _expect_error(
        "INVALID_ADAPTATION_NOTES",
        lambda: executive_learning_engine.build_learning(
            memory,
            "signal",
            invalid_notes,  # type: ignore[arg-type]
            learned_at=STAMP,
        ),
    )


@pytest.mark.parametrize(
    "invalid_learning_id",
    (
        "",
        "LEARN-",
        "LEARN-0",
        "LEARN-000000000000000",
        "LEARN-00000000000000000",
        "learn-0000000000000000",
        "LEARN-GGGGGGGGGGGGGGGG",
        None,
        123,
    ),
)
def test_invalid_learning_id_matrix(
    invalid_learning_id: object,
) -> None:
    _, memory = _build_memory("invalid-id", 1)

    _expect_error(
        "INVALID_LEARNING_ID",
        lambda: ExecutiveLearningResult(
            learning_id=invalid_learning_id,  # type: ignore[arg-type]
            learned_at=STAMP,
            memory=memory,
            learning_signal="signal",
            adaptation_notes=(),
            evidence_references=memory.evidence_references,
            status="EVIDENCE_BOUND",
        ),
    )


def test_direct_constructor_accepts_exact_contract() -> None:
    _, memory = _build_memory("direct", 1)
    signal = "direct-signal"
    notes: tuple[str, ...] = ()
    learning_id = _independent_id(
        memory,
        signal,
        notes,
        STAMP,
    )

    result = ExecutiveLearningResult(
        learning_id=learning_id,
        learned_at=STAMP,
        memory=memory,
        learning_signal=signal,
        adaptation_notes=notes,
        evidence_references=memory.evidence_references,
        status="EVIDENCE_BOUND",
    )

    assert result.learning_id == learning_id
    assert result.memory is memory


def test_shape_valid_forged_learning_id_is_rejected() -> None:
    _, memory = _build_memory("forged-id", 1)
    signal = "forged-signal"
    notes: tuple[str, ...] = ()

    valid_id = _independent_id(
        memory,
        signal,
        notes,
        STAMP,
    )
    forged_id = "LEARN-0000000000000000"
    if forged_id == valid_id:
        forged_id = "LEARN-ffffffffffffffff"

    _expect_error(
        "INVALID_LEARNING_ID",
        lambda: ExecutiveLearningResult(
            learning_id=forged_id,
            learned_at=STAMP,
            memory=memory,
            learning_signal=signal,
            adaptation_notes=notes,
            evidence_references=memory.evidence_references,
            status="EVIDENCE_BOUND",
        ),
    )


def test_evidence_tuple_identity_mismatch_is_rejected() -> None:
    _, memory = _build_memory("evidence-mismatch", 2)
    signal = "evidence-mismatch-signal"
    notes: tuple[str, ...] = ()
    copied_evidence = tuple(
        [
            *memory.evidence_references,
        ]
    )

    assert copied_evidence is not memory.evidence_references

    _expect_error(
        "EVIDENCE_REFERENCE_MISMATCH",
        lambda: ExecutiveLearningResult(
            learning_id=_independent_id(
                memory,
                signal,
                notes,
                STAMP,
            ),
            learned_at=STAMP,
            memory=memory,
            learning_signal=signal,
            adaptation_notes=notes,
            evidence_references=copied_evidence,
            status="EVIDENCE_BOUND",
        ),
    )


def test_status_mismatch_is_rejected() -> None:
    _, memory = _build_memory("status-mismatch", 1)
    signal = "status-mismatch-signal"
    notes: tuple[str, ...] = ()

    _expect_error(
        "INVALID_LEARNING_STATUS",
        lambda: ExecutiveLearningResult(
            learning_id=_independent_id(
                memory,
                signal,
                notes,
                STAMP,
            ),
            learned_at=STAMP,
            memory=memory,
            learning_signal=signal,
            adaptation_notes=notes,
            evidence_references=memory.evidence_references,
            status="NO_EVIDENCE",
        ),
    )


def test_corrupted_memory_id_is_rejected() -> None:
    _, memory = _build_memory("corrupt-memory-id", 1)

    object.__setattr__(
        memory,
        "memory_id",
        "MEM-0000000000000000",
    )

    _expect_error(
        "INVALID_MEMORY_PROVENANCE",
        lambda: executive_learning_engine.build_learning(
            memory,
            "signal",
            (),
            learned_at=STAMP,
        ),
    )


def test_corrupted_memory_status_is_rejected() -> None:
    _, memory = _build_memory("corrupt-memory-status", 1)

    object.__setattr__(
        memory,
        "status",
        "NO_EVIDENCE",
    )

    _expect_error(
        "INVALID_MEMORY_PROVENANCE",
        lambda: executive_learning_engine.build_learning(
            memory,
            "signal",
            (),
            learned_at=STAMP,
        ),
    )


def test_corrupted_memory_evidence_identity_is_rejected() -> None:
    _, memory = _build_memory("corrupt-memory-evidence", 2)
    copied_evidence = tuple(
        [
            *memory.evidence_references,
        ]
    )

    assert copied_evidence is not memory.evidence_references

    object.__setattr__(
        memory,
        "evidence_references",
        copied_evidence,
    )

    _expect_error(
        "INVALID_MEMORY_PROVENANCE",
        lambda: executive_learning_engine.build_learning(
            memory,
            "signal",
            (),
            learned_at=STAMP,
        ),
    )


def test_corrupted_memory_explanation_lineage_is_rejected() -> None:
    _, memory = _build_memory("corrupt-memory-provenance", 1)
    other_explanation = _build_explanation(
        "other-provenance",
        1,
    )

    object.__setattr__(
        memory,
        "explanation",
        other_explanation,
    )

    _expect_error(
        "INVALID_MEMORY_PROVENANCE",
        lambda: executive_learning_engine.build_learning(
            memory,
            "signal",
            (),
            learned_at=STAMP,
        ),
    )


def test_result_is_immutable() -> None:
    _, memory = _build_memory("immutable-result", 1)

    learning = executive_learning_engine.build_learning(
        memory,
        "immutable-signal",
        (),
        learned_at=STAMP,
    )

    with pytest.raises(FrozenInstanceError):
        learning.status = "NO_EVIDENCE"  # type: ignore[misc]


def test_engine_rejects_dynamic_state() -> None:
    engine = ExecutiveLearningEngine()

    with pytest.raises(AttributeError):
        engine.dynamic_state = {}  # type: ignore[attr-defined]


def test_legacy_and_authority_apis_are_absent() -> None:
    for name in (
        "process_feedback",
        "get_learning_record",
        "export_learning_state",
        "execute",
        "execute_workflow",
        "authorize",
        "approve",
        "pay",
        "payment",
        "transfer",
        "persist",
        "save",
        "store",
        "query",
        "export",
    ):
        assert not hasattr(
            ExecutiveLearningEngine,
            name,
        )


def test_production_source_has_only_memory_executive_upstream() -> None:
    source = PRODUCTION_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    executive_imports = []

    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue

        if (
            node.module
            and node.module.startswith(
                "tools.eos.executive.intelligence."
            )
        ):
            executive_imports.append(
                (
                    node.module,
                    tuple(
                        alias.name
                        for alias in node.names
                    ),
                )
            )

    assert executive_imports == [
        (
            "tools.eos.executive.intelligence.executive_memory_engine",
            ("ExecutiveMemoryRecord",),
        )
    ]


def test_production_source_revalidates_memory_public_contract() -> None:
    source = PRODUCTION_PATH.read_text(encoding="utf-8")

    for fragment in (
        "type(memory) is not ExecutiveMemoryRecord",
        "ExecutiveMemoryRecord(",
        "memory_id=memory.memory_id",
        "recorded_at=memory.recorded_at",
        "explanation=memory.explanation",
        "evidence_references=memory.evidence_references",
        "status=memory.status",
        '_fail("INVALID_MEMORY_PROVENANCE")',
    ):
        assert fragment in source


def test_production_source_learning_id_framing_contract() -> None:
    source = PRODUCTION_PATH.read_text(encoding="utf-8")

    for fragment in (
        "memory.tenant_id",
        "memory.principal_id",
        "memory.request_id",
        "memory.correlation_id",
        "memory.memory_id",
        "memory.explanation_id",
        "learning_signal",
        'len(adaptation_notes).to_bytes(8, "big")',
        "_frame_text(note)",
        "_frame_text(learned_at.isoformat())",
        "hashlib.sha3_512()",
    ):
        assert fragment in source


def test_production_source_forbidden_state_and_io_surfaces_absent() -> None:
    source = PRODUCTION_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")

    for forbidden in (
        "threading",
        "logging",
        "json",
        "uuid",
        "random",
        "os",
        "pathlib",
        "sqlite3",
        "subprocess",
        "socket",
        "requests",
        "httpx",
        "urllib",
        "redis",
        "pymongo",
        "motor",
    ):
        assert not any(
            module == forbidden
            or module.startswith(
                forbidden + "."
            )
            for module in imports
        )

    calls = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        try:
            calls.add(ast.unparse(node.func))
        except Exception:
            pass

    for forbidden_call in (
        "hash",
        "open",
        "eval",
        "exec",
        "compile",
        "__import__",
        "logging.basicConfig",
    ):
        assert forbidden_call not in calls

    for forbidden_token in (
        "_instance",
        "_lock",
        "_state_lock",
        "_learning_records",
        "model_weight_adjustment",
        "cognitive_adaptability_score",
        "ADAPTATION_COMMITTED",
    ):
        assert forbidden_token not in source


def test_production_source_authority_boundary_is_explicit() -> None:
    source = PRODUCTION_PATH.read_text(encoding="utf-8").lower()

    for phrase in (
        "grants no fact, evidence",
        "persistence",
        "model-mutation",
        "workflow",
        "payment",
        "execution authority",
        "advisory metadata only",
        "kennel eos remains the exclusive financial execution authority",
    ):
        assert phrase in source


def test_production_source_stable_error_surface() -> None:
    source = PRODUCTION_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    observed = {
        node.value
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and (
                node.value.startswith("INVALID_")
                or node.value
                == "EVIDENCE_REFERENCE_MISMATCH"
            )
        )
    }

    assert observed == EXPECTED_STABLE_ERRORS


def test_production_module_all_is_exact() -> None:
    source = PRODUCTION_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    module_all = None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue

        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "__all__"
        ):
            module_all = ast.literal_eval(node.value)

    assert module_all == (
        "VERSION",
        "ExecutiveLearningError",
        "ExecutiveLearningResult",
        "ExecutiveLearningEngine",
        "executive_learning_engine",
    )


def test_production_physical_end_seal() -> None:
    source = PRODUCTION_PATH.read_text(encoding="utf-8")

    assert source.endswith(
        "# END OF WILSY OS SOVEREIGN PRODUCTION\n"
    )


def test_certificate_physical_end_seal() -> None:
    source = Path(__file__).read_text(encoding="utf-8")

    assert source.endswith(
        "# END OF WILSY OS SOVEREIGN CERTIFICATE\n"
    )


def test_cross_process_learning_id_determinism() -> None:
    certificate_file = str(Path(__file__).resolve())
    script = f"""
import importlib.util
from pathlib import Path
import sys

certificate = Path({certificate_file!r})

spec = importlib.util.spec_from_file_location(
    "_wilsy_learning_cert_cross_process",
    certificate,
)

if spec is None or spec.loader is None:
    raise SystemExit("certificate load failed")

module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

_, memory = module._build_memory(
    "cross-process",
    2,
)

learning = (
    module.ExecutiveLearningEngine()
    .build_learning(
        memory,
        "cross-process-signal",
        (
            "cross-process-note-one",
            "cross-process-note-two",
        ),
        learned_at=module.STAMP,
    )
)

print(learning.learning_id)
"""

    observed = []
    for seed in ("1", "271828", "9973"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = seed
        env["PYTHONPATH"] = str(Path.cwd())

        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                script,
            ],
            cwd=Path.cwd(),
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

        lines = completed.stdout.strip().splitlines()
        assert lines
        observed.append(lines[-1])

    assert len(set(observed)) == 1
    assert observed[0].startswith("LEARN-")
    assert len(observed[0]) == 22


# Executive Learning certificate grants no fact, evidence, persistence, model-mutation, workflow, payment, or execution authority.
# The certificate preserves the frozen Executive Memory upstream and tests advisory Learning only.
# Kennel EOS remains the exclusive financial execution authority.
# END OF WILSY OS SOVEREIGN CERTIFICATE
