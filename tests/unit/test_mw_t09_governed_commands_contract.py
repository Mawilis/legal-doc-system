"""TITLE: WILSY OS MW-T09 Governed Command HTTP Boundary Certificate
VERSION: v1.0.2-MW-T09-SOURCE-COMMAND-BOUNDARY-CERT
AUTHORITY: Synthetic read-only inspection of the canonical Python EOS Projects router.
EPITOME: Certifies existing create/revise/transition/approval/decision route declarations,
         current IAM, CAS, idempotent registry delegation and read-only receipt authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_mw_t09_governed_commands_contract.py
COLLABORATION / OWNERSHIP: MW-T09 Foundation programme; Projects API/router/registry boundaries.
CERTIFICATION / UPDATE DATE: 2026-11-26.
CHANGELOG: v1.0.2-MW-T09-SOURCE-COMMAND-BOUNDARY-CERT uses the exact TENANT BOUNDARY label required by repository_integrity_guard.\nCHANGELOG: v1.0.1-MW-T09-SOURCE-COMMAND-BOUNDARY-CERT asserts the canonical actual financial fence strings rather than a synthesized phrase.\nCHANGELOG: v1.0.0-MW-T09-SOURCE-COMMAND-BOUNDARY-CERT adds explicit source contract assertions;
           authenticated HTTP, real Mongo and actor-denial tests are separate existing certificates.
COMPLIANCE: POPIA section 19; GDPR Article 32; WILSY institutional source governance.
SECURITY / PRIVACY POSTURE: Static AST inspection; no tokens, identities, external requests or database.
TENANT BOUNDARY: Exact-tenant scope must be admitted by canonical EOS authorization.
AUTHORITY BOUNDARY: Tests inspect explicit dependent IAM and deny authority inferred from task state.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively; Projects cannot authorize financial execution.

MW-T09 source-owned command wiring: static HTTP boundary regression certificate.
This is NOT live authenticated HTTP, MongoDB durability, or release certification.
END OF WILSY OS SOVEREIGN ARTIFACT
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROUTER = Path(__file__).resolve().parents[2] / "tools/eos/api/projects_router.py"
TREE = ast.parse(ROUTER.read_text(encoding="utf-8"), filename=str(ROUTER))
FUNCTIONS = {
    node.name: node
    for node in TREE.body
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
}
MODELS = {
    node.name: node
    for node in TREE.body
    if isinstance(node, ast.ClassDef)
}


def body_of(name: str) -> str:
    assert name in FUNCTIONS, f"Missing canonical EOS route: {name}"
    return ast.get_source_segment(ROUTER.read_text(encoding="utf-8"), FUNCTIONS[name]) or ""


def uses_authority(name: str, authority: str) -> None:
    node = FUNCTIONS[name]
    defaults = list(node.args.defaults) + [
        value for value in node.args.kw_defaults if value is not None
    ]
    assert any(
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Name)
        and value.func.id == "Depends"
        and value.args
        and isinstance(value.args[0], ast.Name)
        and value.args[0].id == authority
        for value in defaults
    ), f"{name} must independently admit {authority}"


def route_of(name: str, method: str, suffix: str) -> None:
    node = FUNCTIONS[name]
    assert any(
        isinstance(decorator, ast.Call)
        and isinstance(decorator.func, ast.Attribute)
        and decorator.func.attr == method
        and decorator.args
        and isinstance(decorator.args[0], ast.Constant)
        and decorator.args[0].value == suffix
        for decorator in node.decorator_list
    ), f"{name} missing {method.upper()} {suffix}"


@pytest.mark.parametrize(("name", "method", "suffix", "authority"), [
    ("create_project_task", "post", "/{project_id}/tasks", "_UPDATE"),
    ("revise_project_task", "patch", "/{project_id}/tasks/{task_id}", "_UPDATE"),
    ("transition_project_task", "post", "/{project_id}/tasks/{task_id}/transition", "_UPDATE"),
    ("transition_assigned_project_task", "post", "/{project_id}/my-project/tasks/{task_id}/transition", "_PARTICIPANT_CONTRIBUTE"),
    ("request_project_task_approval", "post", "/{project_id}/tasks/{task_id}/approvals", "_UPDATE"),
    ("decide_project_task_approval", "post", "/{project_id}/my-project/tasks/{task_id}/approvals/{approval_id}/decision", "_PARTICIPANT_CONTRIBUTE"),
])
def test_each_mutation_uses_canonical_route_and_iam(name, method, suffix, authority):
    route_of(name, method, suffix)
    uses_authority(name, authority)
    source = body_of(name)
    assert '_note_idempotency_key(idempotency_key)' in source
    assert 'write=True' in source


@pytest.mark.parametrize(("name", "command"), [
    ("create_project_task", "tasks.create_or_replay("),
    ("revise_project_task", "tasks.revise_or_replay("),
    ("transition_project_task", "tasks.transition_or_replay("),
    ("transition_assigned_project_task", "tasks.transition_or_replay("),
    ("request_project_task_approval", "store.create_or_replay("),
    ("decide_project_task_approval", "store.decide_or_replay("),
])
def test_mutations_delegate_to_durable_idempotent_source(name, command):
    source = body_of(name)
    assert command in source
    assert "idempotency_key=key" in source
    assert "session=session" in source


@pytest.mark.parametrize("name", [
    "revise_project_task", "transition_project_task",
    "transition_assigned_project_task", "decide_project_task_approval",
])
def test_mutations_retain_expected_revision_cas(name):
    assert "expected_revision=payload.expected_revision" in body_of(name)


def test_assignment_and_creation_recheck_current_project_participation():
    for name in ("create_project_task", "revise_project_task"):
        source = body_of(name)
        assert "_project_participant_eligible(" in source
        assert "participants.get(" in source
        assert 'assignment.role != "CONTRIBUTOR"' in source
        assert "context.tenant_id" in source


def test_personal_transition_cannot_touch_unassigned_or_other_user_task():
    source = body_of("transition_assigned_project_task")
    assert "_require_current_project_participation(" in source
    assert "contribute=True" in source
    assert "task.assignee_principal_id != context.identity.identity_id" in source
    assert "PROJECT_TASK_ASSIGNEE_SCOPE_REQUIRED" in source


def test_approval_request_disallows_self_review_and_requires_eligible_reviewer():
    source = body_of("request_project_task_approval")
    for required in (
        "PROJECT_APPROVAL_SELF_REVIEW_DENIED",
        "_project_participant_eligible(",
        'reviewer.role != "CONTRIBUTOR"',
        "_fresh_project_approval_evidence(",
        "_require_cleared_project_attachment(",
        "PROJECT_APPROVAL_EVIDENCE_CHANGED",
    ):
        assert required in source


def test_approval_decision_is_reviewer_scoped_cas_and_evidence_current():
    source = body_of("decide_project_task_approval")
    for required in (
        "_require_current_project_participation(",
        "current_approval.reviewer_principal_id != context.identity.identity_id",
        "PROJECT_APPROVAL_SOURCE_CHANGED",
        "PROJECT_APPROVAL_EVIDENCE_CHANGED",
        "expected_revision=payload.expected_revision",
        "store.decide_or_replay(",
    ):
        assert required in source


@pytest.mark.parametrize(("name", "authority"), [
    ("read_owner_task_transition_receipt", "_UPDATE"),
    ("read_participant_task_transition_receipt", "_PARTICIPANT_CONTRIBUTE"),
])
def test_transition_receipts_require_current_iam_without_reissuing_write(name, authority):
    uses_authority(name, authority)
    source = body_of(name)
    assert "_read_task_transition_receipt(" in source
    assert "write=True" not in source


def test_exact_receipt_binds_actor_revision_target_and_replay_key():
    source = body_of("_read_task_transition_receipt")
    for required in (
        "actor_principal_id=context.identity.identity_id",
        "expected_revision=expected_revision",
        "status=target_status",
        "idempotency_key=key",
        "store.read_transition_receipt(",
        "PROJECT_TASK_COMMAND_NOT_YET_VERIFIED",
    ):
        assert required in source


def test_mutation_models_require_revision_and_constrained_terminal_decision():
    revise = MODELS["ProjectTaskReviseRequest"]
    transition = MODELS["ProjectTaskTransitionRequest"]
    decision = MODELS["ProjectApprovalDecisionRequest"]
    for cls in (revise, transition, decision):
        fields = [
            field.target.id
            for field in cls.body
            if isinstance(field, ast.AnnAssign)
            and isinstance(field.target, ast.Name)
        ]
        assert "expected_revision" in fields
    decision_source = ast.get_source_segment(ROUTER.read_text(encoding="utf-8"), decision) or ""
    assert 'Literal["APPROVED", "REJECTED"]' in decision_source


def test_no_financial_execution_authority_is_issued_by_project_commands():
    source = ROUTER.read_text(encoding="utf-8")
    assert 'FINANCIAL AUTHORITY BOUNDARY: Projects cannot authorize spend' in source
    assert 'Kennel EOS remains exclusive' in source
    assert 'FINANCIAL EXECUTION AUTHORITY: none' in source
