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

def test_actual_practice_route_calls_guard_before_response():
    path = Path(router.__file__)
    tree = ast.parse(path.read_text())
    endpoint = next(
        n for n in tree.body
        if isinstance(n, ast.AsyncFunctionDef)
        and n.name == "get_legal_practice_workspace_projection"
    )
    calls = [
        n for n in ast.walk(endpoint)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "_require_workspace_disclosure_clearance"
    ]
    assert len(calls) == 1
    guard_line = calls[0].lineno
    responses = [
        n for n in ast.walk(endpoint)
        if isinstance(n, ast.Return)
        and isinstance(n.value, ast.Dict)
        and any(
            isinstance(k, ast.Constant) and k.value == "matters"
            for k in n.value.keys
        )
    ]
    assert len(responses) == 1
    assert guard_line < responses[0].lineno

def test_other_independent_routes_remain_declared():
    assert callable(router.get_legal_productive_work_projection)
    assert callable(router.get_legal_practice_workspace_projection)
