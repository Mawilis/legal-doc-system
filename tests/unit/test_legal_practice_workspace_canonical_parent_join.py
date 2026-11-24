"""TITLE: Legal Practice Workspace Matter-Lineage Certificate.
VERSION: v1.0.0-G79-R15R2-MATTER-LINEAGE-CERT
AUTHORITY: Canonical parent-lineage validation and fail-closed route posture.
EPITOME: Certifies six-entity matter relationships and proves the currently
         mounted workspace route denies disclosure before reading those entities.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_practice_workspace_canonical_parent_join.py
COLLABORATION / OWNERSHIP: Exercises the canonical matter-lineage service and
                           Legal Operations workspace router.
CERTIFICATION / UPDATE DATE: 2026-11-11
CHANGELOG: v1.0.0-G79-R15R2-MATTER-LINEAGE-CERT preserves pure parent-lineage
           corruption checks and matches the mounted workspace route's current
           fail-closed confidentiality boundary before legal matter reads.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic matter IDs only; no protected matter data.
TENANT BOUNDARY: Runtime route admission remains exact-tenant scoped.
AUTHORITY BOUNDARY: Lineage validation creates no disclosure or matter authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
import ast
from copy import deepcopy
from pathlib import Path
import pytest

from tools.eos.legal_operations.service import (
    legal_practice_workspace_matter_lineage as lineage,
)
from tools.eos.api import legal_operations_router as router

KEYS = ("matters", "instructions", "documents",
        "attempts", "executions", "returns")

def graph():
    return {
        "matters": [
            {"case_matter_id": "A"},
            {"case_matter_id": "B"},
        ],
        "instructions": [
            {"instruction_id": "iA", "case_matter_id": "A", "document_id": "dA"},
            {"instruction_id": "iB", "case_matter_id": "B", "document_id": "dB"},
        ],
        "documents": [
            {"document_id": "dA", "case_matter_id": "A"},
            {"document_id": "dB", "case_matter_id": "B"},
        ],
        "attempts": [
            {"attempt_id": "aA", "instruction_id": "iA", "document_id": "dA"},
        ],
        "executions": [
            {"service_execution_id": "eA", "attempt_id": "aA",
             "instruction_id": "iA", "document_id": "dA"},
        ],
        "returns": [
            {"return_id": "rA", "service_execution_id": "eA",
             "attempt_id": "aA", "instruction_id": "iA",
             "document_id": "dA"},
        ],
    }

def resolve(g):
    return lineage.resolve_workspace_canonical_parents(**g)

def test_full_graph_has_correct_matter_for_every_row():
    assert resolve(graph()) == {
        "matters": ("A", "B"),
        "instructions": ("A", "B"),
        "documents": ("A", "B"),
        "attempts": ("A",),
        "executions": ("A",),
        "returns": ("A",),
    }

def test_empty_graph_discloses_nothing():
    assert resolve({key: [] for key in KEYS}) == {
        key: () for key in KEYS
    }

def test_two_independent_valid_matters_are_not_corruption():
    g = graph()
    g["attempts"].append({
        "attempt_id": "aB", "instruction_id": "iB", "document_id": "dB"
    })
    assert resolve(g)["attempts"] == ("A", "B")

@pytest.mark.parametrize("group,field,value", [
    ("instructions", "case_matter_id", "B"),
    ("instructions", "document_id", "dB"),
    ("documents", "case_matter_id", "NONEXISTENT"),
    ("attempts", "instruction_id", "iB"),
    ("attempts", "document_id", "dB"),
    ("attempts", "document_id", "missing"),
    ("executions", "attempt_id", "missing"),
    ("executions", "instruction_id", "iB"),
    ("executions", "document_id", "dB"),
    ("returns", "service_execution_id", "missing"),
    ("returns", "attempt_id", "missing"),
    ("returns", "instruction_id", "iB"),
    ("returns", "document_id", "dB"),
])
def test_broken_relationship_denied(group, field, value):
    g = graph()
    g[group][0][field] = value
    with pytest.raises(lineage.MatterLineageError):
        resolve(g)

@pytest.mark.parametrize("group,id_field", [
    ("matters", "case_matter_id"),
    ("instructions", "instruction_id"),
    ("documents", "document_id"),
    ("attempts", "attempt_id"),
    ("executions", "service_execution_id"),
    ("returns", "return_id"),
])
def test_duplicate_identity_denied(group, id_field):
    g = graph()
    g[group].append(deepcopy(g[group][0]))
    with pytest.raises(lineage.MatterLineageError):
        resolve(g)

@pytest.mark.parametrize("group,field", [
    ("matters", "case_matter_id"),
    ("instructions", "case_matter_id"),
    ("instructions", "document_id"),
    ("documents", "case_matter_id"),
    ("attempts", "instruction_id"),
    ("executions", "attempt_id"),
    ("returns", "service_execution_id"),
])
def test_missing_parent_denied(group, field):
    g = graph()
    del g[group][0][field]
    with pytest.raises(lineage.MatterLineageError):
        resolve(g)

def test_no_positive_legal_authority_issued():
    for name in ("issue_clearance", "grant_access",
                 "authorize_practitioner"):
        assert not hasattr(lineage, name)

def test_practice_route_denies_before_matter_lineage_reads():
    tree = ast.parse(Path(router.__file__).read_text())
    endpoint = next(
        n for n in tree.body
        if isinstance(n, ast.AsyncFunctionDef)
        and n.name == "get_legal_practice_workspace_projection"
    )
    calls = []
    denial_details = []
    for node in ast.walk(endpoint):
        if not isinstance(node, ast.Call):
            continue
        name = (
            node.func.id
            if isinstance(node.func, ast.Name)
            else node.func.attr
            if isinstance(node.func, ast.Attribute)
            else ""
        )
        calls.append(name)
        if name == "HTTPException":
            for keyword in node.keywords:
                if keyword.arg == "detail" and isinstance(keyword.value, ast.Constant):
                    denial_details.append(keyword.value.value)
    assert "LEGAL_OPERATIONS_WORKSPACE_CONFIDENTIALITY_AUTHORITY_UNAVAILABLE" in denial_details
    assert "resolve_workspace_canonical_parents" not in calls
    assert "_require_workspace_disclosure_clearance" not in calls


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practice_workspace_canonical_parent_join.py
# VERSION: v1.0.0-G79-R15R2-MATTER-LINEAGE-CERT
# AUTHORITY BOUNDARY: lineage validation and disclosure-denial tests only
# TENANT POSTURE: route must preserve exact authorized tenant scope
# FAIL-CLOSED POSTURE: unavailable confidentiality authority denies before matter reads
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
