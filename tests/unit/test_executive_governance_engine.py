"""WILSY OS direct certificate for evidence-bound executive governance.

TITLE: WILSY Executive Evidence-Bound Governance Engine Direct Certificate
VERSION: v1.0.0-WILSY-EXECUTIVE-GOVERNANCE-CERT
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
EPITOME: Direct adversarial certificate for the frozen evidence-bound Executive Governance production contract.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_executive_governance_engine.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-02
CHANGELOG: Initial direct certificate for v1.0.0-WILSY-EXECUTIVE-GOVERNANCE-EVIDENCE.
COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY: Stable errors and identifiers must not echo caller secrets.
TENANT BOUNDARY: Identity derives only through the validated Governance -> Planning -> Decision -> Reasoning -> Context -> KernelBootstrapRequest chain.
AUTHORITY BOUNDARY: Certificate proves advisory governance-review behavior only and grants no approval, authorization, enforcement, workflow, execution, or financial authority.
EVIDENCE BOUNDARY: NO EVIDENCE = NO FACT; certificate proves Governance creates no evidence and preserves exact Planning evidence references.
REASONING BOUNDARY: Governance accepts no independent reasoning authority; reasoning provenance is inherited only through the validated Planning/Decision chain.
DECISION BOUNDARY: Decision provenance is inherited only through Planning and grants no approval or execution authority.
PLANNING BOUNDARY: ExecutivePlanningResult is the sole upstream Planning/provenance basis and grants no execution authority.
PREDICTION BOUNDARY: Prediction is a sibling advisory surface and is not an authority input to Governance.
GOVERNANCE BOUNDARY: Caller review intent/scopes are inert metadata; no compliance verdict, policy fact, risk fact, signature, attestation, approval, enforcement, or execution is manufactured.
RETRIEVAL BOUNDARY: None.
MODEL BOUNDARY: None.
EXECUTION BOUNDARY: None.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
PRODUCTION UNDER CERTIFICATION: tools/eos/executive/intelligence/executive_governance_engine.py
PRODUCTION VERSION: v1.0.0-WILSY-EXECUTIVE-GOVERNANCE-EVIDENCE
PRODUCTION SHA3-512: d61239592a6f4c9a77432512c0dbcd810039fd532d4b959fb72bf55ea4e929882b4454c8e1b33f5fac8ed40ece7709aebfae1b5390402799cccb9024f8a9cedb
"""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
from hashlib import sha3_512
import inspect
from pathlib import Path
import re
from typing import Any, Callable, cast

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
from tools.eos.executive.intelligence.executive_governance_engine import (
    VERSION,
    ExecutiveGovernanceEngine,
    ExecutiveGovernanceError,
    ExecutiveGovernanceResult,
    executive_governance_engine,
)
import tools.eos.executive.intelligence.executive_governance_engine as governance_prod


STAMP = datetime(2026, 9, 2, 10, 0, tzinfo=timezone.utc)
PRODUCTION_PATH = Path(
    "tools/eos/executive/intelligence/executive_governance_engine.py"
)

EXPECTED_RESULT_FIELDS = (
    "governance_id",
    "reviewed_at",
    "review_intent",
    "review_scopes",
    "planning",
    "evidence_references",
    "status",
)

EXPECTED_ERROR_CODES = {
    "INVALID_GOVERNANCE_ID",
    "INVALID_REVIEWED_AT",
    "INVALID_REVIEW_INTENT",
    "INVALID_REVIEW_SCOPES",
    "INVALID_REVIEW_SCOPE",
    "INVALID_PLANNING_TYPE",
    "INVALID_GOVERNANCE_REFERENCE_TYPE",
    "EVIDENCE_REFERENCE_MISMATCH",
    "INVALID_GOVERNANCE_STATUS",
}


def make_evidence(
    evidence_id: str = "e-a",
    request_id: str = "request-a",
    content: str = "fact",
) -> ExecutiveEvidence:
    return ExecutiveEvidence(
        evidence_id,
        "tenant-a",
        "principal-a",
        request_id,
        "source-a",
        "document",
        "repo://source-a",
        "page:1",
        content,
        sha3_512(content.encode("utf-8")).hexdigest(),
        "receipt-a",
        STAMP,
        None,
    )


def make_planning(
    request_id: str = "request-a",
    evidence_items: tuple[ExecutiveEvidence, ...] = (),
    plan_intent: str = "plan",
    decision_intent: str = "decide",
    target_domain: str = "operations",
) -> ExecutivePlanningResult:
    authority = KernelBootstrapRequest(
        "tenant-a",
        "principal-a",
        request_id,
        "corr-a",
    )
    context = ExecutiveContext(
        authority,
        evidence_items,
        STAMP,
    )
    reasoning = executive_reasoning_engine.evaluate_query(
        "query",
        context,
        evaluated_at=STAMP,
    )
    decision = executive_decision_engine.evaluate_decision(
        decision_intent,
        target_domain,
        reasoning,
        evaluated_at=STAMP,
    )
    return executive_planning_engine.build_plan(
        plan_intent,
        ("step",),
        decision,
        planned_at=STAMP,
    )


def review(
    planning: ExecutivePlanningResult,
    intent: str = "review",
    scopes: tuple[str, ...] = ("scope",),
    reviewed_at: datetime | None = STAMP,
) -> ExecutiveGovernanceResult:
    return executive_governance_engine.build_review(
        intent,
        scopes,
        planning,
        reviewed_at=reviewed_at,
    )


def fails(
    code: str,
    fn: Callable[[], object],
) -> None:
    with pytest.raises(ExecutiveGovernanceError) as caught:
        fn()
    assert str(caught.value) == code


class SecretObject:
    def __init__(self, marker: str) -> None:
        self.marker = marker

    def __str__(self) -> str:
        return self.marker

    def __repr__(self) -> str:
        return f"SecretObject({self.marker})"


def canonical_ast_sha3(source: str) -> str:
    tree = ast.parse(source)

    targets = (
        ast.Module,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.ClassDef,
    )

    def is_docstring_stmt(node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )

    def strip_docstrings(node: ast.AST) -> None:
        if isinstance(node, targets):
            body = getattr(node, "body", None)
            if (
                isinstance(body, list)
                and body
                and is_docstring_stmt(body[0])
            ):
                del body[0]

        for child in ast.iter_child_nodes(node):
            strip_docstrings(child)

    strip_docstrings(tree)
    ast.fix_missing_locations(tree)

    material = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    ).encode("utf-8")

    return sha3_512(material).hexdigest()


def independent_frame(value: str) -> bytes:
    raw = value.encode("utf-8")
    return len(raw).to_bytes(8, "big") + raw


def independent_governance_id(
    planning: ExecutivePlanningResult,
    intent: str,
    scopes: tuple[str, ...],
    stamp: datetime,
) -> str:
    scopes_hasher = sha3_512()
    for scope in scopes:
        scopes_hasher.update(independent_frame(scope))

    final_hasher = sha3_512()
    for component in (
        planning.request_id,
        planning.plan_id,
        planning.decision_id,
        sha3_512(intent.encode("utf-8")).hexdigest(),
        scopes_hasher.hexdigest(),
        stamp.isoformat(),
    ):
        final_hasher.update(independent_frame(component))

    return "GOV-" + final_hasher.hexdigest()[:16]


def test_public_contract_and_no_evidence() -> None:
    planning = make_planning()
    result = review(planning)

    assert VERSION == "v1.0.0-WILSY-EXECUTIVE-GOVERNANCE-EVIDENCE"
    assert issubclass(ExecutiveGovernanceError, ValueError)
    assert isinstance(executive_governance_engine, ExecutiveGovernanceEngine)
    assert type(result) is ExecutiveGovernanceResult

    public_methods = {
        name
        for name, value in ExecutiveGovernanceEngine.__dict__.items()
        if not name.startswith("_") and callable(value)
    }
    assert public_methods == {"build_review"}

    signature = inspect.signature(ExecutiveGovernanceEngine.build_review)
    assert tuple(signature.parameters) == (
        "self",
        "review_intent",
        "review_scopes",
        "planning",
        "reviewed_at",
    )
    assert (
        signature.parameters["reviewed_at"].kind
        is inspect.Parameter.KEYWORD_ONLY
    )

    assert tuple(field.name for field in fields(ExecutiveGovernanceResult)) == (
        EXPECTED_RESULT_FIELDS
    )

    assert result.status == "NO_EVIDENCE"
    assert result.evidence_count == 0
    assert result.evidence_references == ()
    assert result.planning is planning

    assert (
        result.tenant_id,
        result.principal_id,
        result.request_id,
        result.correlation_id,
        result.plan_id,
        result.decision_id,
        result.target_domain,
    ) == (
        planning.tenant_id,
        planning.principal_id,
        planning.request_id,
        planning.correlation_id,
        planning.plan_id,
        planning.decision_id,
        planning.target_domain,
    )

    forbidden_independent_identity = {
        "actor_id",
        "user_id",
        "tenant_id",
        "principal_id",
        "request_id",
        "decision_id",
        "plan_id",
    }
    assert forbidden_independent_identity.isdisjoint(
        set(signature.parameters)
    )
    assert forbidden_independent_identity.isdisjoint(EXPECTED_RESULT_FIELDS)

    for name in (
        "audit_action",
        "get_audit_record",
        "export_governance_state",
    ):
        assert not hasattr(executive_governance_engine, name)


def test_evidence_bound_text_scope_order_duplicates_and_inertness() -> None:
    planning = make_planning(
        evidence_items=(
            make_evidence(),
            make_evidence("e-b", content="second"),
        )
    )
    intent = (
        "  review whether to approve release, authorize workflow, "
        "and transfer payment\t"
    )
    scopes = (
        " policy review ",
        "financial\x1fexecution",
        "duplicate",
        "duplicate",
        "\tvalid scope\t",
    )

    result = review(planning, intent, scopes)

    assert result.status == "EVIDENCE_BOUND"
    assert result.evidence_count == 2
    assert result.evidence_references == planning.evidence_references
    assert result.evidence_references is planning.evidence_references
    assert result.review_intent == intent
    assert result.review_scopes == scopes
    assert result.review_scopes is scopes
    assert result.planning is planning

    for name in (
        "compliance_status",
        "compliant",
        "non_compliant",
        "approved",
        "authorized",
        "risk_exposure",
        "policy_satisfied",
        "regulatory_frameworks",
        "signature",
        "attestation",
        "financial_permission",
        "workflow_permission",
        "execution_permission",
    ):
        assert not hasattr(result, name)


def test_governance_id_shape_determinism_and_all_bindings() -> None:
    planning = make_planning()

    base = review(
        planning,
        "alpha",
        ("beta\x1fgamma",),
        STAMP,
    )
    same = review(
        planning,
        "alpha",
        ("beta\x1fgamma",),
        STAMP,
    )

    assert re.fullmatch(r"GOV-[0-9a-f]{16}", base.governance_id)
    assert base.governance_id == same.governance_id

    split_scopes = review(
        planning,
        "alpha",
        ("beta", "gamma"),
        STAMP,
    )
    reordered = review(
        planning,
        "alpha",
        ("gamma", "beta"),
        STAMP,
    )
    intent_changed = review(
        planning,
        "alpha-changed",
        ("beta\x1fgamma",),
        STAMP,
    )
    timestamp_changed = review(
        planning,
        "alpha",
        ("beta\x1fgamma",),
        STAMP + timedelta(seconds=1),
    )

    assert base.governance_id != split_scopes.governance_id
    assert split_scopes.governance_id != reordered.governance_id
    assert base.governance_id != intent_changed.governance_id
    assert base.governance_id != timestamp_changed.governance_id

    request_changed = review(
        make_planning(request_id="request-b"),
        "alpha",
        ("beta\x1fgamma",),
        STAMP,
    )
    plan_changed = review(
        make_planning(plan_intent="different-plan"),
        "alpha",
        ("beta\x1fgamma",),
        STAMP,
    )
    decision_changed = review(
        make_planning(decision_intent="different-decision"),
        "alpha",
        ("beta\x1fgamma",),
        STAMP,
    )

    assert base.request_id != request_changed.request_id
    assert base.plan_id != plan_changed.plan_id
    assert base.decision_id != decision_changed.decision_id

    assert base.governance_id != request_changed.governance_id
    assert base.governance_id != plan_changed.governance_id
    assert base.governance_id != decision_changed.governance_id

    offset_stamp = STAMP.astimezone(
        timezone(timedelta(hours=2))
    )
    assert offset_stamp == STAMP
    assert offset_stamp.isoformat() != STAMP.isoformat()
    assert (
        review(
            planning,
            "alpha",
            ("beta\x1fgamma",),
            offset_stamp,
        ).governance_id
        != base.governance_id
    )


def test_frame_text_semantics_and_independent_reference_id_oracle() -> None:
    for value in (
        "",
        "a",
        "alpha",
        "request|alpha",
        "βeta",
        "with spaces",
        "\x1f",
        "emoji-🔒",
    ):
        assert governance_prod._frame_text(value) == independent_frame(value)

    planning = make_planning(request_id="request|alpha")
    intent = "α-review"
    scopes = (
        "β",
        "x\x1f",
        "β",
    )
    stamp = datetime(
        2026,
        9,
        2,
        12,
        30,
        tzinfo=timezone(timedelta(hours=2)),
    )

    result = review(
        planning,
        intent,
        scopes,
        stamp,
    )

    expected = independent_governance_id(
        planning,
        intent,
        scopes,
        stamp,
    )

    assert result.governance_id == expected

    scopes_hasher = sha3_512()
    for scope in scopes:
        scopes_hasher.update(independent_frame(scope))

    naive_material = "|".join(
        (
            planning.request_id,
            planning.plan_id,
            planning.decision_id,
            sha3_512(intent.encode("utf-8")).hexdigest(),
            scopes_hasher.hexdigest(),
            stamp.isoformat(),
        )
    ).encode("utf-8")

    naive_id = "GOV-" + sha3_512(naive_material).hexdigest()[:16]

    assert result.governance_id != naive_id


def test_id_ast_scope_and_six_component_framing_flow() -> None:
    tree = ast.parse(PRODUCTION_PATH.read_text(encoding="utf-8"))

    id_functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_id"
    ]
    assert len(id_functions) == 1

    id_function = id_functions[0]
    loops = [
        node
        for node in ast.walk(id_function)
        if isinstance(node, ast.For)
    ]

    scope_loop = next(
        node
        for node in loops
        if isinstance(node.target, ast.Name)
        and node.target.id == "scope"
        and isinstance(node.iter, ast.Name)
        and node.iter.id == "scopes"
    )

    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "update"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Call)
        and isinstance(node.args[0].func, ast.Name)
        and node.args[0].func.id == "_frame_text"
        and len(node.args[0].args) == 1
        and isinstance(node.args[0].args[0], ast.Name)
        and node.args[0].args[0].id == "scope"
        for node in ast.walk(scope_loop)
    )

    component_loop = next(
        node
        for node in loops
        if isinstance(node.iter, ast.Tuple)
        and len(node.iter.elts) == 6
    )

    component_values = [
        ast.unparse(element)
        for element in cast(ast.Tuple, component_loop.iter).elts
    ]

    assert component_values == [
        "planning.request_id",
        "planning.plan_id",
        "planning.decision_id",
        "sha3_512(intent.encode('utf-8')).hexdigest()",
        "scope_hash.hexdigest()",
        "stamp.isoformat()",
    ]

    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "update"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Call)
        and isinstance(node.args[0].func, ast.Name)
        and node.args[0].func.id == "_frame_text"
        and len(node.args[0].args) == 1
        and isinstance(node.args[0].args[0], ast.Name)
        and node.args[0].args[0].id == "component"
        for node in ast.walk(component_loop)
    )


@pytest.mark.parametrize(
    "bad",
    [
        None,
        True,
        False,
        0,
        1.5,
        b"x",
        [],
        {},
        (),
        "",
        " ",
        "\t",
    ],
)
def test_review_intent_complete_fail_closed_matrix(
    bad: object,
) -> None:
    fails(
        "INVALID_REVIEW_INTENT",
        lambda: executive_governance_engine.build_review(
            cast(Any, bad),
            ("scope",),
            make_planning(),
            reviewed_at=STAMP,
        ),
    )


@pytest.mark.parametrize(
    "bad",
    [
        None,
        True,
        False,
        0,
        1.5,
        b"x",
        [],
        {},
        set(),
        "scope",
        (),
    ],
)
def test_review_scopes_collection_complete_fail_closed_matrix(
    bad: object,
) -> None:
    fails(
        "INVALID_REVIEW_SCOPES",
        lambda: executive_governance_engine.build_review(
            "review",
            cast(Any, bad),
            make_planning(),
            reviewed_at=STAMP,
        ),
    )


@pytest.mark.parametrize(
    "bad",
    [
        None,
        True,
        False,
        0,
        1.5,
        b"x",
        [],
        {},
        (),
        set(),
        "",
        " ",
        "\t",
    ],
)
def test_review_scope_element_complete_fail_closed_matrix(
    bad: object,
) -> None:
    fails(
        "INVALID_REVIEW_SCOPE",
        lambda: executive_governance_engine.build_review(
            "review",
            (cast(Any, bad),),
            make_planning(),
            reviewed_at=STAMP,
        ),
    )


@pytest.mark.parametrize(
    "bad",
    [
        None,
        True,
        0,
        {},
        [],
        KernelBootstrapRequest("t", "p", "r", "c"),
    ],
)
def test_planning_type_complete_fail_closed_matrix(
    bad: object,
) -> None:
    fails(
        "INVALID_PLANNING_TYPE",
        lambda: executive_governance_engine.build_review(
            "review",
            ("scope",),
            cast(Any, bad),
            reviewed_at=STAMP,
        ),
    )


@pytest.mark.parametrize(
    "bad",
    [
        "2026",
        b"x",
        7,
        1.5,
        True,
        datetime(2026, 9, 2, 10, 0),
    ],
)
def test_reviewed_at_complete_fail_closed_matrix(
    bad: object,
) -> None:
    fails(
        "INVALID_REVIEWED_AT",
        lambda: executive_governance_engine.build_review(
            "review",
            ("scope",),
            make_planning(),
            reviewed_at=cast(Any, bad),
        ),
    )


def test_timestamp_preservation_and_default_awareness() -> None:
    local_stamp = datetime(
        2026,
        9,
        2,
        12,
        0,
        tzinfo=timezone(timedelta(hours=2)),
    )

    explicit = review(
        make_planning(),
        reviewed_at=local_stamp,
    )

    assert explicit.reviewed_at == local_stamp
    assert explicit.reviewed_at.isoformat() == local_stamp.isoformat()

    automatic = executive_governance_engine.build_review(
        "review",
        ("scope",),
        make_planning(),
    )

    assert automatic.reviewed_at.tzinfo is not None
    assert automatic.reviewed_at.utcoffset() is not None
    assert automatic.reviewed_at.utcoffset() == timedelta(0)


def test_direct_constructor_forged_id_and_status_both_directions() -> None:
    planning = make_planning()
    result = review(planning)

    direct = ExecutiveGovernanceResult(
        result.governance_id,
        result.reviewed_at,
        result.review_intent,
        result.review_scopes,
        result.planning,
        result.evidence_references,
        result.status,
    )
    assert direct == result

    forged = "GOV-" + ("0" * 16)
    fails(
        "INVALID_GOVERNANCE_ID",
        lambda: replace(result, governance_id=forged),
    )

    fails(
        "INVALID_GOVERNANCE_STATUS",
        lambda: replace(result, status="EVIDENCE_BOUND"),
    )

    evidence_bound = review(
        make_planning(
            evidence_items=(make_evidence(),)
        )
    )
    assert evidence_bound.status == "EVIDENCE_BOUND"

    fails(
        "INVALID_GOVERNANCE_STATUS",
        lambda: replace(evidence_bound, status="NO_EVIDENCE"),
    )


@pytest.mark.parametrize(
    "bad",
    [
        None,
        True,
        7,
        b"x",
        "",
        "GOV-",
        "BAD-" + ("0" * 16),
        "GOV-" + ("0" * 15),
        "GOV-" + ("0" * 17),
        "GOV-" + ("A" * 16),
        "GOV-" + ("g" * 16),
    ],
)
def test_direct_governance_id_shape_matrix(
    bad: object,
) -> None:
    result = review(make_planning())

    fails(
        "INVALID_GOVERNANCE_ID",
        lambda: replace(
            result,
            governance_id=cast(Any, bad),
        ),
    )


def test_reference_type_and_provenance_mismatch_matrices() -> None:
    planning = make_planning(
        evidence_items=(
            make_evidence(),
            make_evidence("e-b", content="second"),
        )
    )
    result = review(planning)

    fails(
        "INVALID_GOVERNANCE_REFERENCE_TYPE",
        lambda: replace(
            result,
            evidence_references=cast(
                Any,
                list(result.evidence_references),
            ),
        ),
    )

    fails(
        "INVALID_GOVERNANCE_REFERENCE_TYPE",
        lambda: replace(
            result,
            evidence_references=cast(
                Any,
                (
                    result.evidence_references[0],
                    object(),
                ),
            ),
        ),
    )

    fails(
        "EVIDENCE_REFERENCE_MISMATCH",
        lambda: replace(
            result,
            evidence_references=(
                result.evidence_references[1],
                result.evidence_references[0],
            ),
        ),
    )

    fails(
        "EVIDENCE_REFERENCE_MISMATCH",
        lambda: replace(
            result,
            evidence_references=(),
        ),
    )

    fails(
        "EVIDENCE_REFERENCE_MISMATCH",
        lambda: replace(
            result,
            evidence_references=(
                result.evidence_references[0],
                result.evidence_references[0],
            ),
        ),
    )

    empty_result = review(make_planning())
    fails(
        "EVIDENCE_REFERENCE_MISMATCH",
        lambda: replace(
            empty_result,
            evidence_references=(
                result.evidence_references[0],
            ),
        ),
    )


@pytest.mark.parametrize(
    ("field_name", "replacement"),
    [
        ("evidence_id", "changed-evidence"),
        ("source_id", "changed-source"),
        ("source_type", "changed-type"),
        ("source_locator", "repo://changed"),
        ("citation_locator", "page:99"),
        ("content_sha3_512", "0" * 128),
        ("authorization_receipt_ref", "changed-receipt"),
        (
            "retrieved_at",
            datetime(
                2026,
                9,
                2,
                11,
                0,
                tzinfo=timezone.utc,
            ),
        ),
        ("source_version", "changed-version"),
    ],
)
def test_provenance_field_mismatch_matrix(
    field_name: str,
    replacement: object,
) -> None:
    planning = make_planning(
        evidence_items=(
            make_evidence(),
            make_evidence("e-b", content="second"),
        )
    )
    result = review(planning)

    changed = replace(
        result.evidence_references[0],
        **{field_name: replacement},
    )

    fails(
        "EVIDENCE_REFERENCE_MISMATCH",
        lambda: replace(
            result,
            evidence_references=(
                changed,
                result.evidence_references[1],
            ),
        ),
    )


PRIVACY_CASES: tuple[
    tuple[
        str,
        str,
        Callable[[Any, ExecutiveGovernanceResult], object],
    ],
    ...,
] = (
    (
        "INVALID_GOVERNANCE_ID",
        "PRIVATE-GOVERNANCE-SECRET-ID",
        lambda secret, result: replace(
            result,
            governance_id=secret,
        ),
    ),
    (
        "INVALID_REVIEW_INTENT",
        "PRIVATE-GOVERNANCE-SECRET-INTENT",
        lambda secret, result: executive_governance_engine.build_review(
            secret,
            ("scope",),
            result.planning,
            reviewed_at=STAMP,
        ),
    ),
    (
        "INVALID_REVIEW_SCOPES",
        "PRIVATE-GOVERNANCE-SECRET-SCOPES",
        lambda secret, result: executive_governance_engine.build_review(
            "review",
            secret,
            result.planning,
            reviewed_at=STAMP,
        ),
    ),
    (
        "INVALID_REVIEW_SCOPE",
        "PRIVATE-GOVERNANCE-SECRET-SCOPE",
        lambda secret, result: executive_governance_engine.build_review(
            "review",
            (secret,),
            result.planning,
            reviewed_at=STAMP,
        ),
    ),
    (
        "INVALID_REVIEWED_AT",
        "PRIVATE-GOVERNANCE-SECRET-TIMESTAMP",
        lambda secret, result: executive_governance_engine.build_review(
            "review",
            ("scope",),
            result.planning,
            reviewed_at=secret,
        ),
    ),
    (
        "INVALID_PLANNING_TYPE",
        "PRIVATE-GOVERNANCE-SECRET-PLANNING",
        lambda secret, result: executive_governance_engine.build_review(
            "review",
            ("scope",),
            secret,
            reviewed_at=STAMP,
        ),
    ),
    (
        "INVALID_GOVERNANCE_REFERENCE_TYPE",
        "PRIVATE-GOVERNANCE-SECRET-REFERENCE",
        lambda secret, result: replace(
            result,
            evidence_references=(secret,),
        ),
    ),
    (
        "INVALID_GOVERNANCE_STATUS",
        "PRIVATE-GOVERNANCE-SECRET-STATUS",
        lambda secret, result: replace(
            result,
            status=secret,
        ),
    ),
)


@pytest.mark.parametrize(
    ("code", "marker", "call"),
    PRIVACY_CASES,
)
def test_privacy_non_echo_complete_direct_matrix(
    code: str,
    marker: str,
    call: Callable[[Any, ExecutiveGovernanceResult], object],
) -> None:
    result = review(make_planning())
    secret = SecretObject(marker)

    with pytest.raises(ExecutiveGovernanceError) as caught:
        call(secret, result)

    message = str(caught.value)

    assert message == code
    assert marker not in message
    assert repr(secret) not in message


def test_privacy_non_echo_provenance_mismatch() -> None:
    marker = "PRIVATE-GOVERNANCE-SECRET-PROVENANCE"

    planning = make_planning(
        evidence_items=(make_evidence(),)
    )
    result = review(planning)

    changed = replace(
        result.evidence_references[0],
        source_id=marker,
    )

    with pytest.raises(ExecutiveGovernanceError) as caught:
        replace(
            result,
            evidence_references=(changed,),
        )

    message = str(caught.value)

    assert message == "EVIDENCE_REFERENCE_MISMATCH"
    assert marker not in message


def test_immutability_slots_and_engine_statelessness() -> None:
    before = dict(vars(executive_governance_engine))

    results = [
        review(
            make_planning(request_id=f"request-{suffix}")
        )
        for suffix in ("a", "b", "c")
    ]

    assert len(
        {result.governance_id for result in results}
    ) == 3

    assert dict(vars(executive_governance_engine)) == before

    assert set(ExecutiveGovernanceResult.__slots__) == set(
        EXPECTED_RESULT_FIELDS
    )
    assert not hasattr(results[0], "__dict__")

    for state_name in (
        "_state",
        "_state_lock",
        "_audit_trails",
        "_reviews",
        "_active_reviews",
        "review_history",
        "cache",
        "_cache",
        "history",
        "_history",
        "registry",
        "_registry",
        "_lock",
        "_instance",
    ):
        assert not hasattr(
            executive_governance_engine,
            state_name,
        )

    with pytest.raises(FrozenInstanceError):
        setattr(
            results[0],
            "status",
            "NO_EVIDENCE",
        )

    with pytest.raises(
        (
            FrozenInstanceError,
            AttributeError,
            TypeError,
        )
    ):
        setattr(
            results[0],
            "new_attribute",
            1,
        )


def test_complete_authority_method_and_fact_absence() -> None:
    result = review(
        make_planning(
            evidence_items=(make_evidence(),)
        ),
        "approve release transfer payment",
        (
            "financial authority",
            "workflow approval",
        ),
    )

    forbidden_methods = (
        "audit_action",
        "get_audit_record",
        "export_governance_state",
        "execute",
        "dispatch",
        "approve",
        "authorize",
        "release",
        "pay",
        "transfer",
        "commit",
        "persist",
        "learn",
        "retrieve",
        "fetch",
        "query_model",
        "apply_policy",
        "enforce",
        "sign",
        "attest",
    )

    for name in forbidden_methods:
        assert not hasattr(executive_governance_engine, name)
        assert not hasattr(result, name)

    forbidden_facts = (
        "compliance_status",
        "compliance_result",
        "risk",
        "risk_exposure",
        "policy_satisfaction",
        "regulatory_applicability",
        "regulatory_frameworks",
        "approved",
        "authorized",
        "safe",
        "signature",
        "attestation",
        "certification",
        "financial_permission",
        "workflow_permission",
        "execution_permission",
    )

    for name in forbidden_facts:
        assert not hasattr(result, name)

    assert result.status == "EVIDENCE_BOUND"
    assert result.evidence_references is result.planning.evidence_references


def test_frozen_source_identities_and_canonical_governance_ast() -> None:
    expected = {
        "tools/eos/executive/intelligence/executive_context_engine.py": (
            7044,
            "f02cf9aecb25b34470fc16b6db7f4c7bca285db13874e395856cb9f0b4bee39f5a8223a4c7e019e5d3829030ab8d7a750f8c8429e871ff34c2156a64b1509896",
        ),
        "tests/unit/test_executive_context_engine.py": (
            12043,
            "a02bea87fb0f6b006451c941b00b095bdf3ed2d4212f18af20ddad515de51b955c278d1de11c12518169ee208fab949e3330e5c328ca7ced03de83a8d781df3d",
        ),
        "tools/eos/executive/intelligence/executive_reasoning_engine.py": (
            6919,
            "a04f2dc702f40ee39535fdf3393c1e46e7381bda836791f6be9280724e0d07912c5e1b0684dcfa011bb8e09b104755b754c356942ed378a433ebb5da734adefb",
        ),
        "tests/unit/test_executive_reasoning_engine.py": (
            22574,
            "2c3814ca12f2712faa82421c0af532bcf4c496dce42c0c32450fad06c6510ae2c102efa7443b7113721c5d0978f186e42dfeb93cac8cab27ec9ceac0f4aad655",
        ),
        "tools/eos/executive/intelligence/executive_decision_engine.py": (
            11574,
            "38ce4200c511e3444b18853351405adb9e326027d504269e32738143a30f6890a9c31c31e75d4037f4159f82d1bd64faec47a82336488271e8d5d1c1f936d20f",
        ),
        "tests/unit/test_executive_decision_engine.py": (
            11861,
            "f62143125f3cd23c2f4fead2bd8d6c5bff7080460e95b0f816a3e4909b344742bbacd2c91bffdae236913381e8bc144f14e09723b601e5922450e1b522c83a32",
        ),
        "tools/eos/executive/intelligence/executive_planning_engine.py": (
            7615,
            "41f0f19a3dc9ce4b3ad27c762d8943167d47944fe18cedb87e0bda5a1ba63335f323de01ebc8f244fc8ad84efca422473352abe393ce0a45212f5c0a11aeeff6",
        ),
        "tests/unit/test_executive_planning_engine.py": (
            23882,
            "3073f102f2271e3ba1364496b7d115ae8b2ac709c9aaaf57145be164f7cbe655e0647ce1706a04ce3215a4a6500cdc7f58452d80947cd6f5d9cd69d176e26918",
        ),
        "tools/eos/executive/intelligence/executive_prediction_engine.py": (
            8666,
            "fd65d12d3e2be5127ddd23576396d0a267ccaabb969ab92289820a91fe3ce825a9e44c39ec21db56f54548d1ad56bee12e6e88a14d4ccc2ffaed41ce1ab8cf23",
        ),
        "tests/unit/test_executive_prediction_engine.py": (
            19312,
            "b5963c14d2ff3d94da21d74d6509f7302079485099f8b755af8d1c99db21b7bac3cbb4a6068a7a674187c2aadc253c13d2377c72698e04f14215ba7ff9516939",
        ),
        "tools/eos/executive/intelligence/executive_governance_engine.py": (
            8479,
            "d61239592a6f4c9a77432512c0dbcd810039fd532d4b959fb72bf55ea4e929882b4454c8e1b33f5fac8ed40ece7709aebfae1b5390402799cccb9024f8a9cedb",
        ),
    }

    for artifact_name, (
        expected_bytes,
        expected_sha,
    ) in expected.items():
        raw = Path(artifact_name).read_bytes()
        assert len(raw) == expected_bytes
        assert sha3_512(raw).hexdigest() == expected_sha

    governance_source = PRODUCTION_PATH.read_text(
        encoding="utf-8"
    )
    assert (
        canonical_ast_sha3(governance_source)
        == "2784465284c2d892ae82e65d61b6079e577ae1ab523da5e3dec5553e6f7fba7c855c85f76ae3e0998c4a97076bca0e946fcb241ee8a5fdf5fe2504f194667e9b"
    )


def test_source_semantic_boundary_and_prediction_authority_absence() -> None:
    source = PRODUCTION_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imported_modules: set[str] = set()
    imported_names: set[tuple[str, str]] = set()

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported_modules.add(module)
            for alias in node.names:
                imported_names.add((module, alias.name))

    assert (
        "tools.eos.executive.intelligence.executive_planning_engine",
        "ExecutivePlanningResult",
    ) in imported_names

    assert (
        "tools.eos.executive.intelligence.executive_reasoning_engine",
        "ExecutiveReasoningEvidenceReference",
    ) in imported_names

    assert not any(
        "executive_prediction_engine" in module
        for module in imported_modules
    )

    assert not any(
        name.startswith("ExecutivePrediction")
        for _, name in imported_names
    )

    forbidden_modules = {
        "threading",
        "logging",
        "json",
        "uuid",
        "random",
        "requests",
        "httpx",
        "sqlite3",
        "pymongo",
    }
    assert forbidden_modules.isdisjoint(imported_modules)

    build_functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "build_review"
    ]
    assert len(build_functions) == 1

    build_function = build_functions[0]
    assert tuple(
        argument.arg
        for argument in build_function.args.args
    ) == (
        "self",
        "review_intent",
        "review_scopes",
        "planning",
    )
    assert tuple(
        argument.arg
        for argument in build_function.args.kwonlyargs
    ) == ("reviewed_at",)

    planning_argument = build_function.args.args[-1]
    assert (
        ast.unparse(planning_argument.annotation)
        == "ExecutivePlanningResult"
    )

    status_literals = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and node.value in {
            "NO_EVIDENCE",
            "EVIDENCE_BOUND",
        }
    }
    assert status_literals == {
        "NO_EVIDENCE",
        "EVIDENCE_BOUND",
    }

    error_codes = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and (
            node.value.startswith("INVALID_")
            or node.value == "EVIDENCE_REFERENCE_MISMATCH"
        )
    }
    assert error_codes == EXPECTED_ERROR_CODES

    forbidden_source_tokens = (
        "logging.basicConfig",
        "uuid.uuid4",
        "_audit_trails",
        "_state_lock",
        "audit_action",
        "get_audit_record",
        "export_governance_state",
        '"COMPLIANT"',
        '"NON_COMPLIANT"',
        '"APPROVED"',
        '"AUTHORIZED"',
        "risk_exposure",
        "SIG-OMEGA-",
        "ISO-27001",
        "WilsyOS-ZeroTrust",
        "TODO",
        "FIXME",
        "NotImplemented",
    )

    for token in forbidden_source_tokens:
        assert token not in source


def test_production_sovereign_header_and_physical_end_seal() -> None:
    source = PRODUCTION_PATH.read_text(encoding="utf-8")
    doc = ast.get_docstring(
        ast.parse(source),
        clean=False,
    )

    required_fields = (
        "TITLE",
        "VERSION",
        "AUTHORITY",
        "EPITOME",
        "ABSOLUTE CANONICAL PATH",
        "COLLABORATION / OWNERSHIP",
        "CERTIFICATION/UPDATE DATE",
        "CHANGELOG",
        "COMPLIANCE",
        "SECURITY / PRIVACY",
        "TENANT BOUNDARY",
        "AUTHORITY BOUNDARY",
        "EVIDENCE BOUNDARY",
        "REASONING BOUNDARY",
        "DECISION BOUNDARY",
        "PLANNING BOUNDARY",
        "PREDICTION BOUNDARY",
        "GOVERNANCE BOUNDARY",
        "RETRIEVAL BOUNDARY",
        "MODEL BOUNDARY",
        "EXECUTION BOUNDARY",
        "FINANCIAL AUTHORITY BOUNDARY",
    )

    assert doc is not None

    for field_name in required_fields:
        assert (
            sum(
                line.startswith(field_name + ": ")
                for line in doc.splitlines()
            )
            == 1
        )

    assert (
        "VERSION: v1.0.0-WILSY-EXECUTIVE-GOVERNANCE-EVIDENCE"
        in doc
    )

    terminator = "# END OF " + "WILSY OS SOVEREIGN ARTIFACT"
    assert source.endswith(terminator + "\n")
    assert source.count(terminator) == 1
    assert not source.endswith("\n\n")


def test_certificate_sovereign_header_and_physical_end_seal() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    doc = ast.get_docstring(
        ast.parse(source),
        clean=False,
    )

    required_fields = (
        "TITLE",
        "VERSION",
        "AUTHORITY",
        "EPITOME",
        "ABSOLUTE CANONICAL PATH",
        "COLLABORATION / OWNERSHIP",
        "CERTIFICATION/UPDATE DATE",
        "CHANGELOG",
        "COMPLIANCE",
        "SECURITY / PRIVACY",
        "TENANT BOUNDARY",
        "AUTHORITY BOUNDARY",
        "EVIDENCE BOUNDARY",
        "REASONING BOUNDARY",
        "DECISION BOUNDARY",
        "PLANNING BOUNDARY",
        "PREDICTION BOUNDARY",
        "GOVERNANCE BOUNDARY",
        "RETRIEVAL BOUNDARY",
        "MODEL BOUNDARY",
        "EXECUTION BOUNDARY",
        "FINANCIAL AUTHORITY BOUNDARY",
        "PRODUCTION UNDER CERTIFICATION",
        "PRODUCTION VERSION",
        "PRODUCTION SHA3-512",
    )

    assert doc is not None

    for field_name in required_fields:
        assert (
            sum(
                line.startswith(field_name + ": ")
                for line in doc.splitlines()
            )
            == 1
        )

    assert (
        "VERSION: v1.0.0-WILSY-EXECUTIVE-GOVERNANCE-CERT"
        in doc
    )
    assert (
        "PRODUCTION VERSION: "
        "v1.0.0-WILSY-EXECUTIVE-GOVERNANCE-EVIDENCE"
        in doc
    )

    terminator = (
        "# END OF "
        + "WILSY OS SOVEREIGN CERTIFICATE"
    )

    assert source.endswith(terminator + "\n")
    assert source.count(terminator) == 1
    assert not source.endswith("\n\n")


# ARTIFACT: test_executive_governance_engine.py
# VERSION: v1.0.0-WILSY-EXECUTIVE-GOVERNANCE-CERT
# PRODUCTION UNDER CERTIFICATION: tools/eos/executive/intelligence/executive_governance_engine.py
# PRODUCTION VERSION: v1.0.0-WILSY-EXECUTIVE-GOVERNANCE-EVIDENCE
# PRODUCTION SHA3-512: d61239592a6f4c9a77432512c0dbcd810039fd532d4b959fb72bf55ea4e929882b4454c8e1b33f5fac8ed40ece7709aebfae1b5390402799cccb9024f8a9cedb
# AUTHORITY BOUNDARY: certificate proves advisory governance review only and grants no approval, authorization, enforcement, workflow, execution, or financial authority.
# TENANT POSTURE: tenant and principal identity derive only through Governance -> Planning -> Decision -> Reasoning -> Context -> KernelBootstrapRequest.
# EVIDENCE POSTURE: NO EVIDENCE = NO FACT; Governance creates no evidence and preserves exact Planning evidence references.
# REASONING POSTURE: Governance accepts no independent reasoning authority; reasoning provenance is inherited only through Planning and Decision.
# DECISION POSTURE: Decision provenance is inherited only through Planning and grants no approval or execution authority.
# PLANNING POSTURE: ExecutivePlanningResult is the sole upstream Planning/provenance basis and grants no execution authority.
# PREDICTION POSTURE: Prediction is a sibling advisory surface and is not an authority input to Governance.
# GOVERNANCE POSTURE: caller review metadata is inert; no compliance verdict, policy fact, risk fact, signature, attestation, approval, enforcement, or execution is manufactured.
# FAIL-CLOSED POSTURE: malformed identity, timestamps, review metadata, status, or provenance reject with stable non-echoing errors.
# RETRIEVAL AUTHORITY: NONE
# MODEL AUTHORITY: NONE
# EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN CERTIFICATE
