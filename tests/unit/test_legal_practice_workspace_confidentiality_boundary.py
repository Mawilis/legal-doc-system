"""G79-R5: populated legal workspace must not leak without wall clearance."""
import ast
from pathlib import Path

import pytest
from fastapi import HTTPException

from tools.eos.api import legal_operations_router as router

ENTITY_KEYS = (
    "matters", "instructions", "documents",
    "attempts", "executions", "returns",
)

def _payload(active=None):
    rows = {key: [] for key in ENTITY_KEYS}
    if active is not None:
        rows[active] = [{
            "case_matter_id": "RESTRICTED-MATTER",
            "title": "CONFIDENTIAL-MATTER",
            "evidence_identity": "SECRET-LOCATOR",
        }]
    return rows

@pytest.mark.parametrize("entity", ENTITY_KEYS)
def test_any_uncleared_workspace_record_is_denied(entity):
    with pytest.raises(HTTPException) as exc:
        router._require_workspace_disclosure_clearance(**_payload(entity))
    assert exc.value.status_code == 503
    detail = str(exc.value.detail)
    assert detail == "LEGAL_OPERATIONS_WORKSPACE_MATTER_CLEARANCE_UNAVAILABLE"
    for secret in ("RESTRICTED-MATTER", "CONFIDENTIAL-MATTER", "SECRET-LOCATOR"):
        assert secret not in detail

def test_empty_workspace_has_no_matter_disclosure():
    assert router._require_workspace_disclosure_clearance(
        **_payload()
    ) is None

def test_actual_practice_route_denies_before_lifecycle_reads():
    """Unratified confidentiality authority blocks disclosure before row reads."""
    tree = ast.parse(Path(router.__file__).read_text())
    endpoint = next(
        n for n in tree.body
        if isinstance(n, ast.AsyncFunctionDef)
        and n.name == "get_legal_practice_workspace_projection"
    )
    run = next(
        n for n in ast.walk(endpoint)
        if isinstance(n, ast.FunctionDef) and n.name == "run"
    )

    product_calls = [
        n for n in ast.walk(run)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "resolve_legal_product_availability"
    ]
    assert len(product_calls) == 1

    containment_raises = [
        n for n in ast.walk(run)
        if isinstance(n, ast.Raise)
        and isinstance(n.exc, ast.Call)
        and isinstance(n.exc.func, ast.Name)
        and n.exc.func.id == "HTTPException"
        and any(
            keyword.arg == "detail"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value
            == "LEGAL_OPERATIONS_WORKSPACE_CONFIDENTIALITY_AUTHORITY_UNAVAILABLE"
            for keyword in n.exc.keywords
        )
    ]
    assert len(containment_raises) == 1
    assert product_calls[0].lineno < containment_raises[0].lineno

    # This route must not collect lifecycle rows and only then deny disclosure.
    assert not any(
        isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "_workspace_rows"
        for n in ast.walk(run)
    )
    assert not any(
        isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == "get_collection"
        and any(
            isinstance(arg, ast.Name)
            and arg.id == "LIFECYCLE_COLLECTION"
            for arg in n.args
        )
        for n in ast.walk(run)
    )

def test_other_independent_routes_remain_declared():
    assert callable(router.get_legal_productive_work_projection)
    assert callable(router.get_legal_practice_workspace_projection)
