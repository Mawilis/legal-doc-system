"""WILSY OS — Executive Explanation direct certificate.

TITLE: Executive Explanation Evidence-Bound Direct Certificate
VERSION: v1.0.0-WILSY-EXECUTIVE-EXPLANATION-CERT
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
PURPOSE: Certify the frozen Executive Explanation production contract directly and adversarially.
EPITOME: No evidence = no fact; Prediction and Governance converge only when they preserve one Planning/evidence lineage; Explanation grants no authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_executive_explanation_engine.py
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
    ExecutiveReasoningEvidenceReference,
    executive_reasoning_engine,
)
from tools.eos.executive.intelligence.executive_decision_engine import (
    executive_decision_engine,
)
from tools.eos.executive.intelligence.executive_planning_engine import (
    ExecutivePlanningResult,
    executive_planning_engine,
)
from tools.eos.executive.intelligence.executive_prediction_engine import (
    ExecutivePredictionResult,
    executive_prediction_engine,
)
from tools.eos.executive.intelligence.executive_governance_engine import (
    ExecutiveGovernanceResult,
    executive_governance_engine,
)
from tools.eos.executive.intelligence.executive_explanation_engine import (
    VERSION,
    ExecutiveExplanationEngine,
    ExecutiveExplanationError,
    ExecutiveExplanationResult,
    executive_explanation_engine,
)


CERT_VERSION = "v1.0.0-WILSY-EXECUTIVE-EXPLANATION-CERT"
PRODUCTION_VERSION = "v1.0.0-WILSY-EXECUTIVE-EXPLANATION-EVIDENCE"
PRODUCTION_PATH = Path(
    "tools/eos/executive/intelligence/executive_explanation_engine.py"
)
CERTIFICATE_PATH = Path(
    "tests/unit/test_executive_explanation_engine.py"
)

PRODUCTION_BYTES = 12256
PRODUCTION_SHA3_512 = (
    "10d92718d30ade0aa960217e9111b38f7e80c32ae7bf18126647b99c9b1ad776"
    "62376bc1af80187a91208a9c8aedea7c20e34150d5d0397b6d129986a20ba384"
)
PRODUCTION_AST_SHA3_512 = (
    "db4c7c0d6c507f15706be9074b6cd07207b09e2f47090c5b6cb074595eb66549"
    "b353a79c58d6074c5b20980138acd5cfe2b80994c17f14c2161a5551a5a47f46"
)
PRODUCTION_GIT_BLOB = "7aaf8ab58cef4ecc1ac9a0d636f97c857de886b6"

STAMP = datetime(
    2026,
    9,
    2,
    17,
    45,
    12,
    345678,
    tzinfo=timezone.utc,
)

EXPECTED_FIELDS = (
    "explanation_id",
    "explained_at",
    "explanation_intent",
    "explanation_topics",
    "prediction",
    "governance",
    "evidence_references",
    "status",
)

EXPECTED_PROPERTIES = (
    "planning",
    "tenant_id",
    "principal_id",
    "request_id",
    "correlation_id",
    "plan_id",
    "decision_id",
    "target_domain",
    "prediction_id",
    "governance_id",
    "evidence_count",
)

EXPECTED_STABLE_ERRORS = {
    "INVALID_EXPLANATION_ID",
    "INVALID_EXPLAINED_AT",
    "INVALID_EXPLANATION_INTENT",
    "INVALID_EXPLANATION_TOPICS",
    "INVALID_EXPLANATION_TOPIC",
    "INVALID_PREDICTION_TYPE",
    "INVALID_GOVERNANCE_TYPE",
    "SIBLING_PLANNING_MISMATCH",
    "SIBLING_EVIDENCE_MISMATCH",
    "INVALID_EXPLANATION_REFERENCE_TYPE",
    "EVIDENCE_REFERENCE_MISMATCH",
    "INVALID_EXPLANATION_STATUS",
}


def _frame_text(value: str) -> bytes:
    raw = value.encode("utf-8")
    return len(raw).to_bytes(8, "big") + raw


def _independent_id(
    intent: str,
    topics: tuple[str, ...],
    prediction: ExecutivePredictionResult,
    governance: ExecutiveGovernanceResult,
    stamp: datetime,
) -> str:
    topic_hasher = hashlib.sha3_512()
    for topic in topics:
        topic_hasher.update(_frame_text(topic))

    components = (
        prediction.planning.request_id,
        prediction.planning.plan_id,
        prediction.planning.decision_id,
        prediction.prediction_id,
        governance.governance_id,
        hashlib.sha3_512(intent.encode("utf-8")).hexdigest(),
        topic_hasher.hexdigest(),
        stamp.isoformat(),
    )

    hasher = hashlib.sha3_512()
    for component in components:
        hasher.update(_frame_text(component))
    return "EXPL-" + hasher.hexdigest()[:16]


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


def _git_blob(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def _expect_error(
    code: str,
    operation: Callable[[], object],
    *,
    protected: tuple[str, ...] = (),
) -> None:
    with pytest.raises(ExecutiveExplanationError) as caught:
        operation()

    message = str(caught.value)
    assert message == code
    for secret in protected:
        assert secret not in message


def _build_chain(
    tag: str,
    evidence_count: int,
    *,
    stamp: datetime = STAMP,
) -> dict[str, object]:
    authority = KernelBootstrapRequest(
        tenant_id=f"tenant-{tag}",
        principal_id=f"principal-{tag}",
        request_id=f"request-{tag}",
        correlation_id=f"correlation-{tag}",
    )

    evidence_items: list[ExecutiveEvidence] = []
    for index in range(evidence_count):
        content = f"private-content-{tag}-{index}"
        evidence_items.append(
            ExecutiveEvidence(
                evidence_id=f"evidence-{tag}-{index}",
                tenant_id=authority.tenant_id,
                principal_id=authority.principal_id,
                request_id=authority.request_id,
                source_id=f"source-{tag}-{index}",
                source_type="document",
                source_locator=f"private://source/{tag}/{index}",
                citation_locator=f"citation-{tag}-{index}",
                content=content,
                content_sha3_512=hashlib.sha3_512(
                    content.encode("utf-8")
                ).hexdigest(),
                authorization_receipt_ref=f"receipt-{tag}-{index}",
                retrieved_at=stamp,
                source_version="v1",
            )
        )

    context = ExecutiveContext(
        authority=authority,
        evidence=tuple(evidence_items),
        assembled_at=stamp,
    )
    reasoning = executive_reasoning_engine.evaluate_query(
        f"reasoning-{tag}",
        context,
        evaluated_at=stamp,
    )
    decision = executive_decision_engine.evaluate_decision(
        f"decision-{tag}",
        f"domain-{tag}",
        reasoning,
        evaluated_at=stamp,
    )
    planning = executive_planning_engine.build_plan(
        f"planning-{tag}",
        (
            f"step-{tag}-one",
            f"step-{tag}-one",
            f"step-{tag}-two",
        ),
        decision,
        planned_at=stamp,
    )
    prediction = executive_prediction_engine.build_prediction(
        f"prediction-{tag}",
        (
            f"target-{tag}-one",
            f"target-{tag}-one",
            f"target-{tag}-two",
        ),
        planning,
        predicted_at=stamp,
    )
    governance = executive_governance_engine.build_review(
        f"governance-{tag}",
        (
            f"scope-{tag}-one",
            f"scope-{tag}-one",
            f"scope-{tag}-two",
        ),
        planning,
        reviewed_at=stamp,
    )
    return {
        "authority": authority,
        "evidence": tuple(evidence_items),
        "context": context,
        "reasoning": reasoning,
        "decision": decision,
        "planning": planning,
        "prediction": prediction,
        "governance": governance,
    }


def _build_result(
    chain: dict[str, object],
    *,
    intent: str = "  explain metadata exactly  ",
    topics: tuple[str, ...] = (
        "topic|one",
        "topic-one",
        "topic-one",
        "topic-two",
    ),
    stamp: datetime = STAMP,
) -> ExecutiveExplanationResult:
    prediction = chain["prediction"]
    governance = chain["governance"]
    assert isinstance(prediction, ExecutivePredictionResult)
    assert isinstance(governance, ExecutiveGovernanceResult)
    return executive_explanation_engine.build_explanation(
        intent,
        topics,
        prediction,
        governance,
        explained_at=stamp,
    )


def test_public_contract_and_no_evidence() -> None:
    assert CERT_VERSION == "v1.0.0-WILSY-EXECUTIVE-EXPLANATION-CERT"
    assert VERSION == PRODUCTION_VERSION
    assert tuple(field.name for field in fields(ExecutiveExplanationResult)) == EXPECTED_FIELDS
    assert ExecutiveExplanationResult.__slots__ == EXPECTED_FIELDS
    assert ExecutiveExplanationResult.__match_args__ == EXPECTED_FIELDS
    assert issubclass(ExecutiveExplanationError, ValueError)

    properties = tuple(
        name
        for name, value in ExecutiveExplanationResult.__dict__.items()
        if isinstance(value, property)
    )
    assert properties == EXPECTED_PROPERTIES

    public_methods = tuple(
        name
        for name, value in ExecutiveExplanationEngine.__dict__.items()
        if callable(value) and not name.startswith("_")
    )
    assert public_methods == ("build_explanation",)

    signature = inspect.signature(ExecutiveExplanationEngine.build_explanation)
    assert tuple(signature.parameters) == (
        "self",
        "explanation_intent",
        "explanation_topics",
        "prediction",
        "governance",
        "explained_at",
    )
    assert (
        signature.parameters["explained_at"].kind
        is inspect.Parameter.KEYWORD_ONLY
    )

    chain = _build_chain("zero", 0)
    result = _build_result(chain)
    assert result.status == "NO_EVIDENCE"
    assert result.evidence_references == ()
    assert result.evidence_count == 0


def test_evidence_bound_metadata_order_duplicates_and_inertness() -> None:
    chain = _build_chain("bound", 2)
    intent = "approve payment transfer immediately"
    topics = ("financial", "authorize", "authorize", "release-payment")
    result = _build_result(chain, intent=intent, topics=topics)

    assert result.status == "EVIDENCE_BOUND"
    assert result.explanation_intent == intent
    assert result.explanation_topics == topics
    assert result.explanation_topics is topics
    assert result.evidence_count == 2

    for forbidden in (
        "approval",
        "authorization",
        "payment_permission",
        "financial_authority",
        "execution_permission",
        "workflow_permission",
    ):
        assert not hasattr(result, forbidden)


def test_exact_sibling_and_evidence_object_preservation() -> None:
    chain = _build_chain("identity", 2)
    result = _build_result(chain)
    prediction = chain["prediction"]
    governance = chain["governance"]

    assert isinstance(prediction, ExecutivePredictionResult)
    assert isinstance(governance, ExecutiveGovernanceResult)
    assert result.prediction is prediction
    assert result.governance is governance
    assert result.planning is prediction.planning
    assert prediction.planning == governance.planning
    assert result.evidence_references is prediction.evidence_references
    assert result.evidence_references is governance.evidence_references


def test_derived_provenance_contract() -> None:
    chain = _build_chain("provenance", 2)
    result = _build_result(chain)
    planning = chain["planning"]
    prediction = chain["prediction"]
    governance = chain["governance"]

    assert isinstance(planning, ExecutivePlanningResult)
    assert isinstance(prediction, ExecutivePredictionResult)
    assert isinstance(governance, ExecutiveGovernanceResult)

    assert result.tenant_id == planning.tenant_id
    assert result.principal_id == planning.principal_id
    assert result.request_id == planning.request_id
    assert result.correlation_id == planning.correlation_id
    assert result.plan_id == planning.plan_id
    assert result.decision_id == planning.decision_id
    assert result.target_domain == planning.target_domain
    assert result.prediction_id == prediction.prediction_id
    assert result.governance_id == governance.governance_id
    assert result.evidence_count == planning.evidence_count


def test_explanation_id_shape_determinism_and_independent_oracle() -> None:
    chain = _build_chain("id", 2)
    intent = "  explain|id  "
    topics = ("a", "bc", "a", "bc")
    first = _build_result(chain, intent=intent, topics=topics)
    second = _build_result(chain, intent=intent, topics=topics)

    prediction = chain["prediction"]
    governance = chain["governance"]
    assert isinstance(prediction, ExecutivePredictionResult)
    assert isinstance(governance, ExecutiveGovernanceResult)

    assert first.explanation_id == second.explanation_id
    assert first.explanation_id == _independent_id(
        intent,
        topics,
        prediction,
        governance,
        STAMP,
    )
    assert len(first.explanation_id) == 21
    assert first.explanation_id.startswith("EXPL-")
    assert all(
        character in "0123456789abcdef"
        for character in first.explanation_id[5:]
    )


def test_id_binds_intent_topics_prediction_governance_and_timestamp() -> None:
    chain = _build_chain("bindings", 2)
    base = _build_result(chain)

    changed_intent = _build_result(chain, intent="changed-intent")
    changed_topics = _build_result(chain, topics=("changed-topic",))
    assert changed_intent.explanation_id != base.explanation_id
    assert changed_topics.explanation_id != base.explanation_id

    prediction = chain["prediction"]
    governance = chain["governance"]
    planning = chain["planning"]
    assert isinstance(prediction, ExecutivePredictionResult)
    assert isinstance(governance, ExecutiveGovernanceResult)
    assert isinstance(planning, ExecutivePlanningResult)

    alternate_prediction = executive_prediction_engine.build_prediction(
        "alternate-prediction",
        prediction.prediction_targets,
        planning,
        predicted_at=STAMP,
    )
    alternate_governance = executive_governance_engine.build_review(
        "alternate-governance",
        governance.review_scopes,
        planning,
        reviewed_at=STAMP,
    )

    changed_prediction = executive_explanation_engine.build_explanation(
        base.explanation_intent,
        base.explanation_topics,
        alternate_prediction,
        governance,
        explained_at=STAMP,
    )
    changed_governance = executive_explanation_engine.build_explanation(
        base.explanation_intent,
        base.explanation_topics,
        prediction,
        alternate_governance,
        explained_at=STAMP,
    )
    changed_timestamp = _build_result(
        chain,
        stamp=STAMP + timedelta(seconds=1),
    )

    assert changed_prediction.explanation_id != base.explanation_id
    assert changed_governance.explanation_id != base.explanation_id
    assert changed_timestamp.explanation_id != base.explanation_id


def test_frame_text_semantics_prevent_topic_concatenation_collision() -> None:
    chain = _build_chain("frame", 2)
    left = _build_result(chain, topics=("a", "bc"))
    right = _build_result(chain, topics=("ab", "c"))
    assert left.explanation_id != right.explanation_id

    assert _frame_text("a") + _frame_text("bc") != (
        _frame_text("ab") + _frame_text("c")
    )


def test_timestamp_preservation_representation_binding_and_default_utc() -> None:
    chain = _build_chain("time", 2)
    result = _build_result(chain)
    assert result.explained_at is STAMP

    equivalent_other_offset = STAMP.astimezone(
        timezone(timedelta(hours=2))
    )
    assert equivalent_other_offset == STAMP
    shifted_representation = _build_result(
        chain,
        stamp=equivalent_other_offset,
    )
    assert shifted_representation.explanation_id != result.explanation_id
    assert shifted_representation.explained_at is equivalent_other_offset

    prediction = chain["prediction"]
    governance = chain["governance"]
    assert isinstance(prediction, ExecutivePredictionResult)
    assert isinstance(governance, ExecutiveGovernanceResult)
    defaulted = executive_explanation_engine.build_explanation(
        "default-time",
        ("topic",),
        prediction,
        governance,
    )
    assert defaulted.explained_at.tzinfo is not None
    assert defaulted.explained_at.utcoffset() == timedelta(0)


@pytest.mark.parametrize(
    "bad",
    [None, "", " ", "\t", 0, 1, True, False, [], {}, (), object()],
)
def test_explanation_intent_complete_fail_closed_matrix(bad: object) -> None:
    chain = _build_chain("bad-intent", 2)
    prediction = chain["prediction"]
    governance = chain["governance"]
    assert isinstance(prediction, ExecutivePredictionResult)
    assert isinstance(governance, ExecutiveGovernanceResult)

    _expect_error(
        "INVALID_EXPLANATION_INTENT",
        lambda: executive_explanation_engine.build_explanation(
            bad,  # type: ignore[arg-type]
            ("topic",),
            prediction,
            governance,
            explained_at=STAMP,
        ),
    )


@pytest.mark.parametrize(
    "bad",
    [None, (), [], "topics", {}, set(), 0, 1, True, False, object()],
)
def test_explanation_topics_collection_complete_fail_closed_matrix(
    bad: object,
) -> None:
    chain = _build_chain("bad-topics", 2)
    prediction = chain["prediction"]
    governance = chain["governance"]
    assert isinstance(prediction, ExecutivePredictionResult)
    assert isinstance(governance, ExecutiveGovernanceResult)

    _expect_error(
        "INVALID_EXPLANATION_TOPICS",
        lambda: executive_explanation_engine.build_explanation(
            "intent",
            bad,  # type: ignore[arg-type]
            prediction,
            governance,
            explained_at=STAMP,
        ),
    )


@pytest.mark.parametrize(
    "bad",
    [None, "", " ", "\t", 0, 1, True, False, [], {}, (), object()],
)
def test_explanation_topic_element_complete_fail_closed_matrix(
    bad: object,
) -> None:
    chain = _build_chain("bad-topic", 2)
    prediction = chain["prediction"]
    governance = chain["governance"]
    assert isinstance(prediction, ExecutivePredictionResult)
    assert isinstance(governance, ExecutiveGovernanceResult)

    _expect_error(
        "INVALID_EXPLANATION_TOPIC",
        lambda: executive_explanation_engine.build_explanation(
            "intent",
            ("good-topic", bad),  # type: ignore[arg-type]
            prediction,
            governance,
            explained_at=STAMP,
        ),
    )


@pytest.mark.parametrize(
    "bad_kind",
    ["none", "object", "planning", "governance", "string"],
)
def test_prediction_type_complete_fail_closed_matrix(bad_kind: str) -> None:
    chain = _build_chain("bad-prediction", 2)
    governance = chain["governance"]
    assert isinstance(governance, ExecutiveGovernanceResult)

    bad_values = {
        "none": None,
        "object": object(),
        "planning": chain["planning"],
        "governance": governance,
        "string": "private-prediction-secret",
    }
    _expect_error(
        "INVALID_PREDICTION_TYPE",
        lambda: executive_explanation_engine.build_explanation(
            "intent",
            ("topic",),
            bad_values[bad_kind],  # type: ignore[arg-type]
            governance,
            explained_at=STAMP,
        ),
        protected=("private-prediction-secret",),
    )


@pytest.mark.parametrize(
    "bad_kind",
    ["none", "object", "planning", "prediction", "string"],
)
def test_governance_type_complete_fail_closed_matrix(bad_kind: str) -> None:
    chain = _build_chain("bad-governance", 2)
    prediction = chain["prediction"]
    assert isinstance(prediction, ExecutivePredictionResult)

    bad_values = {
        "none": None,
        "object": object(),
        "planning": chain["planning"],
        "prediction": prediction,
        "string": "private-governance-secret",
    }
    _expect_error(
        "INVALID_GOVERNANCE_TYPE",
        lambda: executive_explanation_engine.build_explanation(
            "intent",
            ("topic",),
            prediction,
            bad_values[bad_kind],  # type: ignore[arg-type]
            explained_at=STAMP,
        ),
        protected=("private-governance-secret",),
    )


@pytest.mark.parametrize(
    "bad",
    [
        datetime(2026, 9, 2, 17, 45, 12),
        "private-timestamp-secret",
        0,
        1,
        True,
        False,
        object(),
    ],
)
def test_explained_at_complete_fail_closed_matrix(bad: object) -> None:
    chain = _build_chain("bad-time", 2)
    prediction = chain["prediction"]
    governance = chain["governance"]
    assert isinstance(prediction, ExecutivePredictionResult)
    assert isinstance(governance, ExecutiveGovernanceResult)

    _expect_error(
        "INVALID_EXPLAINED_AT",
        lambda: executive_explanation_engine.build_explanation(
            "intent",
            ("topic",),
            prediction,
            governance,
            explained_at=bad,  # type: ignore[arg-type]
        ),
        protected=("private-timestamp-secret",),
    )


@pytest.mark.parametrize(
    "bad_id",
    [
        None,
        "",
        "EXPL-",
        "EXPL-0123456789abcde",
        "EXPL-0123456789abcdef0",
        "EXPL-0123456789ABCDEf",
        "EXPL-0123456789abcdeg",
        "PRED-0123456789abcdef",
        0,
        True,
        object(),
    ],
)
def test_direct_explanation_id_shape_matrix(bad_id: object) -> None:
    chain = _build_chain("bad-id", 2)
    result = _build_result(chain)

    _expect_error(
        "INVALID_EXPLANATION_ID",
        lambda: ExecutiveExplanationResult(
            explanation_id=bad_id,  # type: ignore[arg-type]
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent,
            explanation_topics=result.explanation_topics,
            prediction=result.prediction,
            governance=result.governance,
            evidence_references=result.evidence_references,
            status=result.status,
        ),
    )


def test_direct_constructor_forged_id_and_all_binding_changes() -> None:
    chain = _build_chain("forged", 2)
    result = _build_result(chain)
    planning = chain["planning"]
    assert isinstance(planning, ExecutivePlanningResult)

    valid_direct = ExecutiveExplanationResult(
        explanation_id=result.explanation_id,
        explained_at=result.explained_at,
        explanation_intent=result.explanation_intent,
        explanation_topics=result.explanation_topics,
        prediction=result.prediction,
        governance=result.governance,
        evidence_references=result.evidence_references,
        status=result.status,
    )
    assert valid_direct == result

    forged_id = (
        result.explanation_id[:5]
        + ("0" if result.explanation_id[5] != "0" else "1")
        + result.explanation_id[6:]
    )
    _expect_error(
        "INVALID_EXPLANATION_ID",
        lambda: ExecutiveExplanationResult(
            explanation_id=forged_id,
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent,
            explanation_topics=result.explanation_topics,
            prediction=result.prediction,
            governance=result.governance,
            evidence_references=result.evidence_references,
            status=result.status,
        ),
    )

    alternate_prediction = executive_prediction_engine.build_prediction(
        "alternate-forged-prediction",
        result.prediction.prediction_targets,
        planning,
        predicted_at=STAMP,
    )
    alternate_governance = executive_governance_engine.build_review(
        "alternate-forged-governance",
        result.governance.review_scopes,
        planning,
        reviewed_at=STAMP,
    )

    changed_cases = (
        dict(
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent + "x",
            explanation_topics=result.explanation_topics,
            prediction=result.prediction,
            governance=result.governance,
        ),
        dict(
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent,
            explanation_topics=result.explanation_topics + ("changed",),
            prediction=result.prediction,
            governance=result.governance,
        ),
        dict(
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent,
            explanation_topics=result.explanation_topics,
            prediction=alternate_prediction,
            governance=result.governance,
        ),
        dict(
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent,
            explanation_topics=result.explanation_topics,
            prediction=result.prediction,
            governance=alternate_governance,
        ),
        dict(
            explained_at=result.explained_at + timedelta(seconds=1),
            explanation_intent=result.explanation_intent,
            explanation_topics=result.explanation_topics,
            prediction=result.prediction,
            governance=result.governance,
        ),
    )

    for case in changed_cases:
        _expect_error(
            "INVALID_EXPLANATION_ID",
            lambda case=case: ExecutiveExplanationResult(
                explanation_id=result.explanation_id,
                explained_at=case["explained_at"],  # type: ignore[arg-type]
                explanation_intent=case["explanation_intent"],  # type: ignore[arg-type]
                explanation_topics=case["explanation_topics"],  # type: ignore[arg-type]
                prediction=case["prediction"],  # type: ignore[arg-type]
                governance=case["governance"],  # type: ignore[arg-type]
                evidence_references=result.evidence_references,
                status=result.status,
            ),
        )


def test_sibling_planning_mismatch_engine_and_direct_fail_closed() -> None:
    chain = _build_chain("planning-mismatch", 2)
    result = _build_result(chain)
    decision = chain["decision"]

    alternate_plan = executive_planning_engine.build_plan(
        "alternate-plan",
        ("alternate-step",),
        decision,  # type: ignore[arg-type]
        planned_at=STAMP,
    )
    alternate_governance = executive_governance_engine.build_review(
        "alternate-review",
        ("alternate-scope",),
        alternate_plan,
        reviewed_at=STAMP,
    )

    _expect_error(
        "SIBLING_PLANNING_MISMATCH",
        lambda: executive_explanation_engine.build_explanation(
            result.explanation_intent,
            result.explanation_topics,
            result.prediction,
            alternate_governance,
            explained_at=result.explained_at,
        ),
    )
    _expect_error(
        "SIBLING_PLANNING_MISMATCH",
        lambda: ExecutiveExplanationResult(
            explanation_id=result.explanation_id,
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent,
            explanation_topics=result.explanation_topics,
            prediction=result.prediction,
            governance=alternate_governance,
            evidence_references=result.evidence_references,
            status=result.status,
        ),
    )


def test_sibling_evidence_mismatch_engine_and_direct_fail_closed() -> None:
    chain = _build_chain("evidence-mismatch", 2)
    result = _build_result(chain)

    corrupt_governance = executive_governance_engine.build_review(
        "corrupt-governance",
        result.governance.review_scopes,
        result.planning,
        reviewed_at=STAMP,
    )
    object.__setattr__(
        corrupt_governance,
        "evidence_references",
        (),
    )

    _expect_error(
        "SIBLING_EVIDENCE_MISMATCH",
        lambda: executive_explanation_engine.build_explanation(
            result.explanation_intent,
            result.explanation_topics,
            result.prediction,
            corrupt_governance,
            explained_at=result.explained_at,
        ),
    )
    _expect_error(
        "SIBLING_EVIDENCE_MISMATCH",
        lambda: ExecutiveExplanationResult(
            explanation_id=result.explanation_id,
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent,
            explanation_topics=result.explanation_topics,
            prediction=result.prediction,
            governance=corrupt_governance,
            evidence_references=result.evidence_references,
            status=result.status,
        ),
    )


def test_reference_type_and_exact_provenance_mismatch() -> None:
    chain = _build_chain("references", 2)
    result = _build_result(chain)

    _expect_error(
        "INVALID_EXPLANATION_REFERENCE_TYPE",
        lambda: ExecutiveExplanationResult(
            explanation_id=result.explanation_id,
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent,
            explanation_topics=result.explanation_topics,
            prediction=result.prediction,
            governance=result.governance,
            evidence_references=("private-reference-secret",),  # type: ignore[arg-type]
            status=result.status,
        ),
        protected=("private-reference-secret",),
    )

    _expect_error(
        "EVIDENCE_REFERENCE_MISMATCH",
        lambda: ExecutiveExplanationResult(
            explanation_id=result.explanation_id,
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent,
            explanation_topics=result.explanation_topics,
            prediction=result.prediction,
            governance=result.governance,
            evidence_references=(),
            status=result.status,
        ),
    )


def test_status_both_directions_fail_closed() -> None:
    bound = _build_result(_build_chain("status-bound", 2))
    zero = _build_result(_build_chain("status-zero", 0))

    _expect_error(
        "INVALID_EXPLANATION_STATUS",
        lambda: ExecutiveExplanationResult(
            explanation_id=bound.explanation_id,
            explained_at=bound.explained_at,
            explanation_intent=bound.explanation_intent,
            explanation_topics=bound.explanation_topics,
            prediction=bound.prediction,
            governance=bound.governance,
            evidence_references=bound.evidence_references,
            status="NO_EVIDENCE",
        ),
    )
    _expect_error(
        "INVALID_EXPLANATION_STATUS",
        lambda: ExecutiveExplanationResult(
            explanation_id=zero.explanation_id,
            explained_at=zero.explained_at,
            explanation_intent=zero.explanation_intent,
            explanation_topics=zero.explanation_topics,
            prediction=zero.prediction,
            governance=zero.governance,
            evidence_references=zero.evidence_references,
            status="EVIDENCE_BOUND",
        ),
    )


def test_direct_constructor_timestamp_and_metadata_guards() -> None:
    result = _build_result(_build_chain("direct-guards", 2))

    _expect_error(
        "INVALID_EXPLAINED_AT",
        lambda: ExecutiveExplanationResult(
            explanation_id=result.explanation_id,
            explained_at=datetime(2026, 9, 2, 17, 45, 12),
            explanation_intent=result.explanation_intent,
            explanation_topics=result.explanation_topics,
            prediction=result.prediction,
            governance=result.governance,
            evidence_references=result.evidence_references,
            status=result.status,
        ),
    )
    _expect_error(
        "INVALID_EXPLANATION_INTENT",
        lambda: ExecutiveExplanationResult(
            explanation_id=result.explanation_id,
            explained_at=result.explained_at,
            explanation_intent=" ",
            explanation_topics=result.explanation_topics,
            prediction=result.prediction,
            governance=result.governance,
            evidence_references=result.evidence_references,
            status=result.status,
        ),
    )
    _expect_error(
        "INVALID_EXPLANATION_TOPICS",
        lambda: ExecutiveExplanationResult(
            explanation_id=result.explanation_id,
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent,
            explanation_topics=(),
            prediction=result.prediction,
            governance=result.governance,
            evidence_references=result.evidence_references,
            status=result.status,
        ),
    )
    _expect_error(
        "INVALID_EXPLANATION_TOPIC",
        lambda: ExecutiveExplanationResult(
            explanation_id=result.explanation_id,
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent,
            explanation_topics=("good", " "),
            prediction=result.prediction,
            governance=result.governance,
            evidence_references=result.evidence_references,
            status=result.status,
        ),
    )
    _expect_error(
        "INVALID_PREDICTION_TYPE",
        lambda: ExecutiveExplanationResult(
            explanation_id=result.explanation_id,
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent,
            explanation_topics=result.explanation_topics,
            prediction="private-direct-prediction",  # type: ignore[arg-type]
            governance=result.governance,
            evidence_references=result.evidence_references,
            status=result.status,
        ),
        protected=("private-direct-prediction",),
    )
    _expect_error(
        "INVALID_GOVERNANCE_TYPE",
        lambda: ExecutiveExplanationResult(
            explanation_id=result.explanation_id,
            explained_at=result.explained_at,
            explanation_intent=result.explanation_intent,
            explanation_topics=result.explanation_topics,
            prediction=result.prediction,
            governance="private-direct-governance",  # type: ignore[arg-type]
            evidence_references=result.evidence_references,
            status=result.status,
        ),
        protected=("private-direct-governance",),
    )


def test_privacy_non_echo_complete_direct_and_engine_matrix() -> None:
    secret_intent = "PRIVATE-EXPLANATION-INTENT-SECRET"
    secret_topic = "PRIVATE-EXPLANATION-TOPIC-SECRET"
    secret_prediction = "PRIVATE-PREDICTION-SECRET"
    secret_governance = "PRIVATE-GOVERNANCE-SECRET"
    secret_timestamp = "PRIVATE-TIMESTAMP-SECRET"
    secret_reference = "PRIVATE-REFERENCE-SECRET"

    chain = _build_chain("privacy", 2)
    result = _build_result(chain)

    cases = (
        (
            "INVALID_EXPLANATION_INTENT",
            lambda: executive_explanation_engine.build_explanation(
                " ",
                (secret_topic,),
                result.prediction,
                result.governance,
                explained_at=STAMP,
            ),
        ),
        (
            "INVALID_EXPLANATION_TOPIC",
            lambda: executive_explanation_engine.build_explanation(
                secret_intent,
                (" ",),
                result.prediction,
                result.governance,
                explained_at=STAMP,
            ),
        ),
        (
            "INVALID_PREDICTION_TYPE",
            lambda: executive_explanation_engine.build_explanation(
                secret_intent,
                (secret_topic,),
                secret_prediction,  # type: ignore[arg-type]
                result.governance,
                explained_at=STAMP,
            ),
        ),
        (
            "INVALID_GOVERNANCE_TYPE",
            lambda: executive_explanation_engine.build_explanation(
                secret_intent,
                (secret_topic,),
                result.prediction,
                secret_governance,  # type: ignore[arg-type]
                explained_at=STAMP,
            ),
        ),
        (
            "INVALID_EXPLAINED_AT",
            lambda: executive_explanation_engine.build_explanation(
                secret_intent,
                (secret_topic,),
                result.prediction,
                result.governance,
                explained_at=secret_timestamp,  # type: ignore[arg-type]
            ),
        ),
        (
            "INVALID_EXPLANATION_REFERENCE_TYPE",
            lambda: ExecutiveExplanationResult(
                explanation_id=result.explanation_id,
                explained_at=result.explained_at,
                explanation_intent=secret_intent,
                explanation_topics=(secret_topic,),
                prediction=result.prediction,
                governance=result.governance,
                evidence_references=(secret_reference,),  # type: ignore[arg-type]
                status=result.status,
            ),
        ),
    )

    protected = (
        secret_intent,
        secret_topic,
        secret_prediction,
        secret_governance,
        secret_timestamp,
        secret_reference,
    )
    for code, operation in cases:
        _expect_error(code, operation, protected=protected)


def test_immutability_slots_and_engine_statelessness() -> None:
    result = _build_result(_build_chain("immutability", 2))

    with pytest.raises(FrozenInstanceError):
        result.status = "MUTATED"  # type: ignore[misc]

    assert not hasattr(result, "__dict__")
    assert vars(executive_explanation_engine) == {}
    assert ExecutiveExplanationEngine() is not executive_explanation_engine


def test_complete_authority_method_and_fact_absence() -> None:
    result = _build_result(
        _build_chain("authority", 2),
        intent="approve authorize execute payment",
        topics=("approval", "payment", "execution"),
    )

    forbidden_result_surface = (
        "narrative",
        "explanation",
        "cause",
        "causal_chain",
        "confidence",
        "probability",
        "forecast",
        "risk",
        "risk_assessment",
        "compliance",
        "policy",
        "policy_verdict",
        "regulatory_applicability",
        "legal_conclusion",
        "recommendation",
        "approval",
        "authorization",
        "execution_permission",
        "workflow_permission",
        "payment_permission",
        "financial_authority",
    )
    for name in forbidden_result_surface:
        assert not hasattr(result, name)

    forbidden_engine_methods = (
        "explain_query",
        "get_explanation",
        "export_explanation_state",
        "retrieve",
        "persist",
        "approve",
        "authorize",
        "execute",
        "dispatch",
        "release",
        "pay",
        "transfer",
    )
    for name in forbidden_engine_methods:
        assert not hasattr(executive_explanation_engine, name)

    assert result.explanation_intent == "approve authorize execute payment"
    assert result.explanation_topics == ("approval", "payment", "execution")
    assert result.status == "EVIDENCE_BOUND"


def test_stable_error_literal_contract_is_exact() -> None:
    raw = PRODUCTION_PATH.read_bytes()
    tree = ast.parse(raw.decode("utf-8"))
    strings = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    observed = {
        value
        for value in strings
        if (
            value.startswith("INVALID_")
            or value.startswith("SIBLING_")
            or value == "EVIDENCE_REFERENCE_MISMATCH"
        )
    }
    assert observed == EXPECTED_STABLE_ERRORS


def test_frozen_production_source_identities_and_canonical_ast() -> None:
    raw = PRODUCTION_PATH.read_bytes()
    assert len(raw) == PRODUCTION_BYTES
    assert hashlib.sha3_512(raw).hexdigest() == PRODUCTION_SHA3_512
    assert _canonical_ast_sha(raw) == PRODUCTION_AST_SHA3_512
    assert _git_blob(raw) == PRODUCTION_GIT_BLOB


def test_source_semantic_boundary_and_no_independent_upstream_authority() -> None:
    raw = PRODUCTION_PATH.read_bytes()
    source = raw.decode("utf-8")
    tree = ast.parse(source)

    imported_symbols = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    assert "ExecutivePredictionResult" in imported_symbols
    assert "ExecutiveGovernanceResult" in imported_symbols
    assert "ExecutiveReasoningEvidenceReference" in imported_symbols

    for forbidden in (
        "ExecutivePlanningResult",
        "ExecutiveDecisionResult",
        "ExecutiveReasoningResult",
        "ExecutiveContext",
        "ExecutiveEvidence",
        "KernelBootstrapRequest",
    ):
        assert forbidden not in imported_symbols

    defined_functions = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "explain_query" not in defined_functions
    assert "get_explanation" not in defined_functions
    assert "export_explanation_state" not in defined_functions

    for forbidden_state in (
        "_instance",
        "_lock",
        "_state_lock",
        "_explanations",
        "_explanation_store",
    ):
        assert forbidden_state not in source


def test_production_sovereign_header_and_physical_end_seal() -> None:
    source = PRODUCTION_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    header = ast.get_docstring(tree, clean=False)
    assert header is not None

    for required in (
        "VERSION: v1.0.0-WILSY-EXECUTIVE-EXPLANATION-EVIDENCE",
        "NO EVIDENCE = NO FACT",
        "Prediction and Governance must share the same Planning value and exact evidence references",
        "FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.",
    ):
        assert required in header

    assert source.endswith(
        "# END OF WILSY OS SOVEREIGN ARTIFACT\n"
    )


def test_certificate_sovereign_header_and_physical_end_seal() -> None:
    source = CERTIFICATE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    header = ast.get_docstring(tree, clean=False)
    assert header is not None

    assert "VERSION: v1.0.0-WILSY-EXECUTIVE-EXPLANATION-CERT" in header
    assert "No evidence = no fact" in header
    assert "Prediction and Governance converge only when they preserve one Planning/evidence lineage" in header
    assert source.endswith(
        "# END OF WILSY OS SOVEREIGN CERTIFICATE\n"
    )


# ARTIFACT: test_executive_explanation_engine.py
# VERSION: v1.0.0-WILSY-EXECUTIVE-EXPLANATION-CERT
# PRODUCTION SUBJECT: fix(executive): bind explanation to verified prediction and governance
# PRODUCTION COMMIT: 95cb57620028bb8e90df9bf9954af33799b2589f
# PRODUCTION GIT BLOB: 7aaf8ab58cef4ecc1ac9a0d636f97c857de886b6
# AUTHORITY POSTURE: Explanation is advisory evidence metadata only.
# CONVERGENCE POSTURE: Prediction and Governance must preserve one exact Planning/evidence lineage.
# EVIDENCE POSTURE: NO EVIDENCE = NO FACT; certificate rejects manufactured evidence or fact authority.
# EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN CERTIFICATE
