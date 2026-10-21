"""G79-R12: fail-closed matter lineage for workspace projections."""

import pytest

from tools.eos.legal_operations.service.legal_practice_workspace_matter_lineage import (
    MatterLineageError,
    require_matter_lineage,
    require_uniform_matter_lineage,
)

@pytest.mark.parametrize(
    "entity_type",
    (
        "CaseMatter",
        "LegalInstruction",
        "ProcessDocument",
        "ServiceAttempt",
        "ServiceExecution",
        "ReturnOfService",
    ),
)
def test_each_supported_entity_needs_exact_matter_lineage(entity_type):
    row = {"case_matter_id": "matter-001"}
    assert require_matter_lineage(
        entity_type=entity_type,
        row=row,
    ) == "matter-001"

@pytest.mark.parametrize(
    "invalid",
    ("", " ", None, 123, True, [], {}, " matter-001 "),
)
def test_invalid_matter_reference_denied(invalid):
    with pytest.raises(MatterLineageError):
        require_matter_lineage(
            entity_type="ProcessDocument",
            row={"case_matter_id": invalid},
        )

def test_missing_link_is_denied():
    with pytest.raises(MatterLineageError):
        require_matter_lineage(
            entity_type="ProcessDocument",
            row={"document_id": "document-001"},
        )

def test_unsupported_type_denied():
    with pytest.raises(MatterLineageError):
        require_matter_lineage(
            entity_type="UnregisteredEntity",
            row={"case_matter_id": "matter-001"},
        )

def test_conflicting_matter_references_denied():
    with pytest.raises(MatterLineageError):
        require_matter_lineage(
            entity_type="ProcessDocument",
            row={
                "case_matter_id": "matter-001",
                "matter_id": "matter-002",
            },
        )

def test_matching_references_are_unambiguous():
    assert require_matter_lineage(
        entity_type="ProcessDocument",
        row={
            "case_matter_id": "matter-001",
            "matter_id": "matter-001",
        },
    ) == "matter-001"

def test_cross_matter_join_denied():
    with pytest.raises(MatterLineageError):
        require_uniform_matter_lineage(
            entity_type="ProcessDocument",
            rows=(
                {"case_matter_id": "matter-001"},
                {"case_matter_id": "matter-002"},
            ),
        )

def test_uniform_matter_join():
    assert require_uniform_matter_lineage(
        entity_type="ServiceAttempt",
        rows=(
            {"case_matter_id": "matter-001"},
            {"case_matter_id": "matter-001"},
        ),
    ) == "matter-001"

def test_empty_group_requires_no_matter():
    assert require_uniform_matter_lineage(
        entity_type="ServiceAttempt",
        rows=(),
    ) is None

def test_no_positive_authority_is_exposed():
    from tools.eos.legal_operations.service import (
        legal_practice_workspace_matter_lineage as module
    )
    assert not hasattr(module, "grant_access")
    assert not hasattr(module, "authorize_practitioner")
    assert not hasattr(module, "issue_clearance")
