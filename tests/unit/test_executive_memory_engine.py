"""WILSY OS — Executive Memory direct certificate.

TITLE: Executive Memory Evidence-Bound Direct Certificate
VERSION: v1.0.0-WILSY-EXECUTIVE-MEMORY-CERT
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
PURPOSE: Certify the frozen Executive Memory production contract directly and adversarially.
EPITOME: Memory preserves one validated Explanation lineage without creating evidence, fact, persistence, workflow, or execution authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_executive_memory_engine.py
CERTIFICATION/UPDATE DATE: 2026-09-02
"""

from __future__ import annotations

import ast
import hashlib
import inspect
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
    VERSION,
    ExecutiveMemoryEngine,
    ExecutiveMemoryError,
    ExecutiveMemoryRecord,
    executive_memory_engine,
)


CERT_VERSION = "v1.0.0-WILSY-EXECUTIVE-MEMORY-CERT"
PRODUCTION_VERSION = "v1.0.0-WILSY-EXECUTIVE-MEMORY-EVIDENCE"
PRODUCTION_PATH = Path(
    "tools/eos/executive/intelligence/executive_memory_engine.py"
)
CERTIFICATE_PATH = Path(
    "tests/unit/test_executive_memory_engine.py"
)

PRODUCTION_BYTES = 7286
PRODUCTION_SHA3_512 = (
    "2a99de910439d8fee86bafab3ea94be2ad671a952f84a959de18fafdf9df1651"
    "afc88490161034b9cdbf5eb9e776b96552a9dc8275a7a9693ea8fa3d0094bca7"
)
PRODUCTION_AST_SHA3_512 = (
    "c09e01c697fb0db94f23bdd6f544192aa902b6c92fafc9d5b568e8652cb60ae6"
    "d9ceb4979394d75c4a726f1897725c1d7acd1b94712396c938287d19e06c938c"
)
PRODUCTION_GIT_BLOB = "d666a467049d5d96f1a21e96b62ef2dc38301ebe"
PRODUCTION_COMMIT = "1062db885603f040977f1a67161ac2f8c4beb544"

STAMP = datetime(
    2026,
    9,
    2,
    21,
    14,
    15,
    926535,
    tzinfo=timezone.utc,
)

EXPECTED_FIELDS = (
    "memory_id",
    "recorded_at",
    "explanation",
    "evidence_references",
    "status",
)

EXPECTED_PROPERTIES = (
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
    "evidence_count",
)

EXPECTED_STABLE_ERRORS = {
    "INVALID_MEMORY_ID",
    "INVALID_RECORDED_AT",
    "INVALID_EXPLANATION_TYPE",
    "INVALID_EXPLANATION_PROVENANCE",
    "EVIDENCE_REFERENCE_MISMATCH",
    "INVALID_MEMORY_STATUS",
}


def _frame_text(value: str) -> bytes:
    raw = value.encode("utf-8")
    return len(raw).to_bytes(8, "big") + raw


def _independent_id(
    explanation: ExecutiveExplanationResult,
    stamp: datetime,
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
        stamp.isoformat(),
    )

    hasher = hashlib.sha3_512()
    for component in components:
        hasher.update(_frame_text(component))
    return "MEM-" + hasher.hexdigest()[:16]


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
    with pytest.raises(ExecutiveMemoryError) as exc_info:
        operation()

    message = str(exc_info.value)
    assert message == code
    assert "PRIVATE_SECRET" not in message
    assert "tenant-secret" not in message
    assert "principal-secret" not in message


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


def test_certificate_version() -> None:
    assert CERT_VERSION == "v1.0.0-WILSY-EXECUTIVE-MEMORY-CERT"


def test_production_version() -> None:
    assert VERSION == PRODUCTION_VERSION


def test_production_identity() -> None:
    raw = PRODUCTION_PATH.read_bytes()

    assert len(raw) == PRODUCTION_BYTES
    assert hashlib.sha3_512(raw).hexdigest() == PRODUCTION_SHA3_512
    assert _canonical_ast_sha(raw) == PRODUCTION_AST_SHA3_512
    assert _git_blob_sha1(raw) == PRODUCTION_GIT_BLOB


def test_certificate_path_is_exact() -> None:
    assert CERTIFICATE_PATH.as_posix() == (
        "tests/unit/test_executive_memory_engine.py"
    )


def test_public_result_fields() -> None:
    assert tuple(
        field.name
        for field in fields(ExecutiveMemoryRecord)
    ) == EXPECTED_FIELDS


def test_public_result_properties() -> None:
    assert tuple(
        name
        for name, value in ExecutiveMemoryRecord.__dict__.items()
        if isinstance(value, property)
    ) == EXPECTED_PROPERTIES


def test_engine_public_surface() -> None:
    assert tuple(
        name
        for name, value in ExecutiveMemoryEngine.__dict__.items()
        if callable(value) and not name.startswith("_")
    ) == ("build_memory",)


def test_build_memory_signature() -> None:
    signature = inspect.signature(ExecutiveMemoryEngine.build_memory)

    assert tuple(signature.parameters) == (
        "self",
        "explanation",
        "recorded_at",
    )
    assert (
        signature.parameters["recorded_at"].kind
        is inspect.Parameter.KEYWORD_ONLY
    )
    assert signature.parameters["recorded_at"].default is None


def test_engine_is_stateless() -> None:
    assert ExecutiveMemoryEngine.__slots__ == ()
    assert not hasattr(executive_memory_engine, "__dict__")

    first = ExecutiveMemoryEngine()
    second = ExecutiveMemoryEngine()

    assert first is not second
    assert first is not executive_memory_engine
    assert second is not executive_memory_engine
    assert not hasattr(first, "__dict__")
    assert not hasattr(second, "__dict__")


def test_no_evidence_memory() -> None:
    explanation = _build_explanation("no-evidence", 0)
    memory = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP,
    )

    assert memory.status == "NO_EVIDENCE"
    assert memory.evidence_count == 0
    assert memory.explanation is explanation
    assert memory.evidence_references is explanation.evidence_references


def test_evidence_bound_memory() -> None:
    explanation = _build_explanation("evidence-bound", 2)
    memory = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP,
    )

    assert memory.status == "EVIDENCE_BOUND"
    assert memory.evidence_count == 2
    assert memory.explanation is explanation
    assert memory.evidence_references is explanation.evidence_references


def test_derived_provenance_binding() -> None:
    explanation = _build_explanation("derived", 1)
    memory = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP,
    )

    assert memory.planning is explanation.planning
    assert memory.prediction is explanation.prediction
    assert memory.governance is explanation.governance
    assert memory.tenant_id == explanation.tenant_id
    assert memory.principal_id == explanation.principal_id
    assert memory.request_id == explanation.request_id
    assert memory.correlation_id == explanation.correlation_id
    assert memory.plan_id == explanation.plan_id
    assert memory.decision_id == explanation.decision_id
    assert memory.target_domain == explanation.target_domain
    assert memory.prediction_id == explanation.prediction_id
    assert memory.governance_id == explanation.governance_id
    assert memory.explanation_id == explanation.explanation_id


def test_independent_memory_id_oracle() -> None:
    explanation = _build_explanation("id-oracle", 2)
    memory = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP,
    )

    assert memory.memory_id == _independent_id(explanation, STAMP)
    assert memory.memory_id.startswith("MEM-")
    assert len(memory.memory_id) == 20
    assert all(
        character in "0123456789abcdef"
        for character in memory.memory_id[4:]
    )


def test_explicit_timestamp_determinism_across_instances() -> None:
    explanation = _build_explanation("deterministic", 1)

    first = ExecutiveMemoryEngine().build_memory(
        explanation,
        recorded_at=STAMP,
    )
    second = ExecutiveMemoryEngine().build_memory(
        explanation,
        recorded_at=STAMP,
    )

    assert first.memory_id == second.memory_id
    assert first == second


def test_timestamp_changes_memory_id() -> None:
    explanation = _build_explanation("timestamp", 1)

    first = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP,
    )
    second = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP + timedelta(microseconds=1),
    )

    assert first.memory_id != second.memory_id


def test_provenance_changes_memory_id() -> None:
    first_explanation = _build_explanation("provenance-a", 1)
    second_explanation = _build_explanation("provenance-b", 1)

    first = executive_memory_engine.build_memory(
        first_explanation,
        recorded_at=STAMP,
    )
    second = executive_memory_engine.build_memory(
        second_explanation,
        recorded_at=STAMP,
    )

    assert first.memory_id != second.memory_id


def test_default_timestamp_is_utc_and_bound_into_id() -> None:
    explanation = _build_explanation("default-time", 1)

    before = datetime.now(timezone.utc)
    memory = executive_memory_engine.build_memory(explanation)
    after = datetime.now(timezone.utc)

    assert before <= memory.recorded_at <= after
    assert memory.recorded_at.tzinfo is not None
    assert memory.recorded_at.utcoffset() == timedelta(0)
    assert memory.memory_id == _independent_id(
        explanation,
        memory.recorded_at,
    )


@pytest.mark.parametrize(
    "invalid_explanation",
    (
        None,
        object(),
        {},
        [],
        (),
        0,
        "PRIVATE_SECRET",
    ),
)
def test_invalid_explanation_type_matrix(
    invalid_explanation: object,
) -> None:
    _expect_error(
        "INVALID_EXPLANATION_TYPE",
        lambda: executive_memory_engine.build_memory(
            invalid_explanation,  # type: ignore[arg-type]
            recorded_at=STAMP,
        ),
    )


@pytest.mark.parametrize(
    "invalid_recorded_at",
    (
        "PRIVATE_SECRET_TIME",
        0,
        object(),
        datetime(2026, 9, 2, 21, 14, 15),
        datetime(
            2026,
            9,
            2,
            23,
            14,
            15,
            tzinfo=timezone(timedelta(hours=2)),
        ),
    ),
)
def test_invalid_recorded_at_matrix(
    invalid_recorded_at: object,
) -> None:
    explanation = _build_explanation("invalid-time", 1)

    _expect_error(
        "INVALID_RECORDED_AT",
        lambda: executive_memory_engine.build_memory(
            explanation,
            recorded_at=invalid_recorded_at,  # type: ignore[arg-type]
        ),
    )


@pytest.mark.parametrize(
    "invalid_memory_id",
    (
        "",
        "MEM-",
        "MEM-0",
        "MEM-" + ("0" * 15),
        "MEM-" + ("0" * 17),
        "mem-" + ("0" * 16),
        "MEM-" + ("G" * 16),
        None,
        123,
    ),
)
def test_invalid_memory_id_matrix(
    invalid_memory_id: object,
) -> None:
    explanation = _build_explanation("invalid-id", 1)

    _expect_error(
        "INVALID_MEMORY_ID",
        lambda: ExecutiveMemoryRecord(
            memory_id=invalid_memory_id,  # type: ignore[arg-type]
            recorded_at=STAMP,
            explanation=explanation,
            evidence_references=explanation.evidence_references,
            status="EVIDENCE_BOUND",
        ),
    )


def test_shape_valid_forged_id_is_rejected() -> None:
    explanation = _build_explanation("forged-id", 1)
    valid = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP,
    )

    forged = "MEM-" + ("0" * 16)
    if forged == valid.memory_id:
        forged = "MEM-" + ("1" * 16)

    _expect_error(
        "INVALID_MEMORY_ID",
        lambda: ExecutiveMemoryRecord(
            memory_id=forged,
            recorded_at=STAMP,
            explanation=explanation,
            evidence_references=explanation.evidence_references,
            status="EVIDENCE_BOUND",
        ),
    )


def test_direct_constructor_accepts_exact_valid_contract() -> None:
    explanation = _build_explanation("direct-valid", 2)
    built = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP,
    )

    direct = ExecutiveMemoryRecord(
        memory_id=built.memory_id,
        recorded_at=STAMP,
        explanation=explanation,
        evidence_references=explanation.evidence_references,
        status="EVIDENCE_BOUND",
    )

    assert direct == built


def test_evidence_identity_mismatch_is_rejected() -> None:
    explanation = _build_explanation("evidence-mismatch", 2)
    valid = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP,
    )

    copied_refs = tuple(list(explanation.evidence_references))
    assert copied_refs is not explanation.evidence_references

    _expect_error(
        "EVIDENCE_REFERENCE_MISMATCH",
        lambda: ExecutiveMemoryRecord(
            memory_id=valid.memory_id,
            recorded_at=STAMP,
            explanation=explanation,
            evidence_references=copied_refs,
            status="EVIDENCE_BOUND",
        ),
    )


def test_direct_status_mismatch_is_rejected() -> None:
    explanation = _build_explanation("status-mismatch", 1)
    valid = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP,
    )

    _expect_error(
        "INVALID_MEMORY_STATUS",
        lambda: ExecutiveMemoryRecord(
            memory_id=valid.memory_id,
            recorded_at=STAMP,
            explanation=explanation,
            evidence_references=explanation.evidence_references,
            status="NO_EVIDENCE",
        ),
    )


def test_corrupted_explanation_status_is_rejected() -> None:
    explanation = _build_explanation("corrupt-status", 1)
    object.__setattr__(
        explanation,
        "status",
        "NO_EVIDENCE",
    )

    _expect_error(
        "INVALID_MEMORY_STATUS",
        lambda: executive_memory_engine.build_memory(
            explanation,
            recorded_at=STAMP,
        ),
    )


def test_corrupted_explanation_evidence_identity_is_rejected() -> None:
    explanation = _build_explanation("corrupt-evidence", 2)

    copied_refs = tuple(list(explanation.evidence_references))
    assert copied_refs is not explanation.evidence_references

    object.__setattr__(
        explanation,
        "evidence_references",
        copied_refs,
    )

    _expect_error(
        "EVIDENCE_REFERENCE_MISMATCH",
        lambda: executive_memory_engine.build_memory(
            explanation,
            recorded_at=STAMP,
        ),
    )


def test_corrupted_explanation_provenance_is_rejected() -> None:
    explanation = _build_explanation("corrupt-provenance", 1)
    different = _build_explanation("different-provenance", 1)

    object.__setattr__(
        explanation.prediction,
        "planning",
        different.planning,
    )

    _expect_error(
        "INVALID_EXPLANATION_PROVENANCE",
        lambda: executive_memory_engine.build_memory(
            explanation,
            recorded_at=STAMP,
        ),
    )


def test_result_is_immutable_and_slotted() -> None:
    explanation = _build_explanation("immutable", 1)
    memory = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP,
    )

    with pytest.raises((FrozenInstanceError, AttributeError)):
        memory.status = "NO_EVIDENCE"  # type: ignore[misc]

    with pytest.raises((FrozenInstanceError, AttributeError)):
        memory.extra = "PRIVATE_SECRET"  # type: ignore[attr-defined]


def test_engine_rejects_dynamic_state() -> None:
    engine = ExecutiveMemoryEngine()

    with pytest.raises(AttributeError):
        engine.state = "PRIVATE_SECRET"  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "forbidden_method",
    (
        "record_memory",
        "query_memories",
        "export_institutional_memory_state",
        "execute",
        "execute_workflow",
        "authorize",
        "approve",
        "sign",
        "pay",
        "transfer",
        "persist",
        "save",
        "store",
    ),
)
def test_legacy_persistence_and_execution_api_absent(
    forbidden_method: str,
) -> None:
    assert not hasattr(
        executive_memory_engine,
        forbidden_method,
    )


def test_stable_error_surface_is_exact() -> None:
    raw = PRODUCTION_PATH.read_bytes()
    tree = ast.parse(raw.decode("utf-8"))

    strings = {
        node.value
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
        )
    }

    observed = {
        value
        for value in strings
        if (
            value.startswith("INVALID_")
            or value == "EVIDENCE_REFERENCE_MISMATCH"
        )
    }

    assert observed == EXPECTED_STABLE_ERRORS


def test_only_explanation_is_executive_upstream() -> None:
    tree = ast.parse(
        PRODUCTION_PATH.read_text(encoding="utf-8")
    )

    executive_imports = []
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue

        module = node.module or ""
        if module.startswith(
            "tools.eos.executive.intelligence."
        ):
            executive_imports.append(
                (
                    module,
                    tuple(
                        alias.name
                        for alias in node.names
                    ),
                )
            )

    assert executive_imports == [
        (
            "tools.eos.executive.intelligence.executive_explanation_engine",
            ("ExecutiveExplanationResult",),
        )
    ]


def test_process_hash_and_stateful_io_surface_absent() -> None:
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
        "redis",
        "pymongo",
        "motor",
    ):
        assert not any(
            module == forbidden
            or module.startswith(forbidden + ".")
            for module in imports
        )

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        call_name = ast.unparse(node.func)
        assert call_name not in {
            "hash",
            "open",
            "eval",
            "exec",
            "compile",
            "__import__",
            "os.system",
        }


def test_authority_boundary_is_explicit_and_non_executing() -> None:
    source = PRODUCTION_PATH.read_text(
        encoding="utf-8"
    ).lower()

    for required in (
        "grants no fact",
        "legal",
        "compliance",
        "workflow",
        "payment",
        "execution authority",
        "kennel eos remains the exclusive financial execution authority",
    ):
        assert required in source

    public_names = (
        tuple(
            name
            for name, value in ExecutiveMemoryEngine.__dict__.items()
            if callable(value) and not name.startswith("_")
        )
        + EXPECTED_PROPERTIES
    )

    for name in public_names:
        lowered = name.lower()
        assert not any(
            term in lowered
            for term in (
                "execute",
                "authorize",
                "approve",
                "payment",
                "transfer",
                "disburse",
                "sign",
                "enforce",
                "persist",
                "save",
                "store",
                "query",
                "export",
            )
        )


def test_physical_end_seal() -> None:
    source = PRODUCTION_PATH.read_text(
        encoding="utf-8"
    )

    assert source.endswith(
        "# END OF WILSY OS SOVEREIGN PRODUCTION\n"
    )


def test_memory_id_does_not_embed_raw_provenance() -> None:
    explanation = _build_explanation("privacy", 1)
    memory = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP,
    )

    for raw_value in (
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
    ):
        assert raw_value not in memory.memory_id


def test_memory_creates_no_new_evidence() -> None:
    explanation = _build_explanation("no-new-evidence", 2)
    memory = executive_memory_engine.build_memory(
        explanation,
        recorded_at=STAMP,
    )

    assert memory.evidence_references is explanation.evidence_references
    assert memory.evidence_count == len(explanation.evidence_references)


# Executive Memory grants no fact, legal, compliance, persistence, workflow, payment, or execution authority.
# Kennel EOS remains the exclusive financial execution authority.
# END OF WILSY OS SOVEREIGN CERTIFICATE
