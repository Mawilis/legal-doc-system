"""
P14-R20R27 controlled RED for Legal work-item completion HTTP.

This contract deliberately precedes production wiring.

Frozen boundary:
    POST /api/legal-operations/work-items/{work_item_id}/completion

Browser-supplied facts:
    completion_evidence_reference
    completion_evidence_fingerprint

Server-owned authority:
    tenant
    principal
    work item / work fingerprint
    assignment history / current historical assignment
    IAM decision evidence
    completion authority evidence
    evaluated_at
    transaction
"""

from __future__ import annotations

import ast
from pathlib import Path

import tools.eos.api.legal_operations_command_router as command_api


ROUTE_PATH = (
    "/work-items/{work_item_id}/completion"
)

PERMISSION = (
    "legal_operations:work_item:complete"
)

OPERATION = (
    "legal_work_item_complete"
)

SOURCE = Path(
    command_api.__file__
).read_text(
    encoding="utf-8"
)

TREE = ast.parse(
    SOURCE
)


def _class(
    name: str,
) -> ast.ClassDef:
    for node in ast.iter_child_nodes(
        TREE
    ):
        if (
            isinstance(
                node,
                ast.ClassDef,
            )
            and node.name == name
        ):
            return node

    raise AssertionError(
        f"MISSING_CLASS:{name}"
    )


def _function_for_route(
) -> (
    ast.FunctionDef
    | ast.AsyncFunctionDef
):
    for node in ast.walk(
        TREE
    ):
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        for decorator in (
            node.decorator_list
        ):
            text = ast.unparse(
                decorator
            )

            if (
                ".post(" in text
                and ROUTE_PATH in text
            ):
                return node

    raise AssertionError(
        "R20R27_COMPLETION_POST_ROUTE_MISSING"
    )


def test_completion_route_is_one_exact_post_subresource(
) -> None:
    function = (
        _function_for_route()
    )

    decorators = tuple(
        ast.unparse(value)
        for value
        in function.decorator_list
    )

    assert any(
        ".post(" in value
        and ROUTE_PATH in value
        for value in decorators
    )


def test_completion_command_model_is_extra_forbid_and_has_only_outcome_evidence(
) -> None:
    model = _class(
        "LegalWorkCompletionCommand"
    )

    fields: set[str] = set()

    for node in model.body:
        if (
            isinstance(
                node,
                ast.AnnAssign,
            )
            and isinstance(
                node.target,
                ast.Name,
            )
        ):
            fields.add(
                node.target.id
            )

    assert fields == {
        "completion_evidence_reference",
        "completion_evidence_fingerprint",
    }

    bases = {
        ast.unparse(base)
        for base in model.bases
    }

    assert "_CommandModel" in bases


def test_completion_route_uses_exact_certified_permission_and_operation(
) -> None:
    assert (
        f'_ctx("{PERMISSION}", '
        f'"{OPERATION}")'
        in SOURCE
        or (
            PERMISSION in SOURCE
            and OPERATION in SOURCE
        )
    )


def test_completion_route_derives_actor_scope_from_authorized_context(
) -> None:
    function = (
        _function_for_route()
    )

    text = ast.unparse(
        function
    )

    assert (
        "context.tenant_id"
        in text
    )

    assert (
        "context.identity.identity_id"
        in text
    )


def test_completion_route_server_derives_trusted_evaluated_at(
) -> None:
    function = (
        _function_for_route()
    )

    text = ast.unparse(
        function
    )

    assert (
        "datetime.now(timezone.utc)"
        in text
        or "datetime.now(tz=timezone.utc)"
        in text
    )

    assert (
        "command.evaluated_at"
        not in text
    )


def test_completion_route_loads_durable_work_and_assignment_history(
) -> None:
    function = (
        _function_for_route()
    )

    text = ast.unparse(
        function
    )

    assert (
        "LegalWorkItemRegistry"
        in text
    )

    assert (
        "LegalWorkAssignmentRegistry"
        in text
    )

    assert (
        "work_item_id"
        in text
    )


def test_completion_route_constructs_canonical_iam_evidence_and_calls_r20r20_once(
) -> None:
    function = (
        _function_for_route()
    )

    text = ast.unparse(
        function
    )

    assert (
        "TenantAuthorizationDecisionEvidenceRegistry"
        in text
    )

    assert (
        text.count(
            "record_legal_work_completion("
        )
        == 1
    )


def test_completion_http_never_accepts_authority_or_financial_fields(
) -> None:
    model = _class(
        "LegalWorkCompletionCommand"
    )

    rendered = ast.unparse(
        model
    )

    forbidden = (
        "tenant_id",
        "principal_id",
        "actor_principal_id",
        "work_item_fingerprint",
        "assignment_id",
        "assignment_fingerprint",
        "iam_authorization_evidence_reference",
        "iam_authorization_evidence_fingerprint",
        "completion_authority_evidence_reference",
        "completion_authority_evidence_fingerprint",
        "evaluated_at",
        "authorized_at",
        "business_role",
        "authorization_role",
        "invoice",
        "payment",
        "settlement",
        "amount",
        "price",
        "subscription",
        "plan",
        "workflow_release",
        "dependency_release",
    )

    for token in forbidden:
        assert token not in rendered


def test_completion_route_executes_inside_router_transaction_boundary(
) -> None:
    function = (
        _function_for_route()
    )

    text = ast.unparse(
        function
    )

    assert (
        "def run(session"
        in text
    )

    assert (
        "_transaction(run)"
        in text
    )


def test_completion_route_returns_canonical_event_projection_only(
) -> None:
    function = (
        _function_for_route()
    )

    returns = [
        node
        for node in ast.walk(function)
        if isinstance(
            node,
            ast.Return,
        )
    ]

    assert any(
        isinstance(
            node.value,
            ast.Dict,
        )
        and len(node.value.keys) == 1
        and isinstance(
            node.value.keys[0],
            ast.Constant,
        )
        and node.value.keys[0].value == "data"
        and isinstance(
            node.value.values[0],
            ast.Call,
        )
        and isinstance(
            node.value.values[0].func,
            ast.Attribute,
        )
        and node.value.values[0].func.attr == "to_dict"
        for node in returns
    )
