"""
WILSY OS — P14-R8 Runtime Work Dependency Edge Domain Certificate

VERSION: v1.0.0-P14-R8-WORK-DEPENDENCY-EDGE-UNIT-CERT

PURPOSE:
    Freeze the immutable runtime relation between one predecessor work item
    and one successor work item emitted by one exact materialization receipt.

CRITICAL SEPARATIONS:
    dependency edge != dependency satisfaction
    dependency satisfaction != work completion
    edge existence != mutable blocked state

AUTHORITY:
    Evidence of dependency topology only. No completion, satisfaction,
    assignment, supervision, IAM, notification, AI, legal-event or finance
    authority.
"""

from dataclasses import FrozenInstanceError

import pytest

from tools.eos.legal_operations.domain.legal_work_dependency_edge import (
    SCHEMA,
    VERSION,
    LegalWorkDependencyEdge,
    LegalWorkDependencyEdgeError,
)


FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128
FP_D = "d" * 128
FP_E = "e" * 128


def _edge(
    **overrides: object,
) -> LegalWorkDependencyEdge:
    values: dict[str, object] = {
        "tenant_id": "tenant-law",
        "case_matter_id": "matter-1",
        "source_materialization_receipt_id": FP_A,
        "source_materialization_receipt_fingerprint": FP_B,
        "predecessor_work_item_id": "work-a",
        "predecessor_work_item_fingerprint": FP_C,
        "successor_work_item_id": "work-b",
        "successor_work_item_fingerprint": FP_D,
    }

    values.update(
        overrides
    )

    return LegalWorkDependencyEdge(
        **values,  # type: ignore[arg-type]
    )


def test_schema_version_identity_and_immutability_are_exact() -> None:
    value = _edge()

    assert value.schema == SCHEMA
    assert value.edge_version == VERSION
    assert len(value.dependency_edge_id) == 128
    assert len(value.fingerprint) == 128

    with pytest.raises(FrozenInstanceError):
        value.tenant_id = "other"  # type: ignore[misc]


def test_identity_is_deterministic_for_exact_runtime_relation() -> None:
    left = _edge()
    right = _edge()

    assert left == right
    assert (
        left.dependency_edge_id
        == right.dependency_edge_id
    )
    assert left.fingerprint == right.fingerprint


@pytest.mark.parametrize(
    ("field", "value"),
    (
        (
            "source_materialization_receipt_id",
            FP_E,
        ),
        (
            "source_materialization_receipt_fingerprint",
            FP_E,
        ),
        (
            "predecessor_work_item_id",
            "work-other",
        ),
        (
            "predecessor_work_item_fingerprint",
            FP_E,
        ),
        (
            "successor_work_item_id",
            "work-other",
        ),
        (
            "successor_work_item_fingerprint",
            FP_E,
        ),
    ),
)
def test_any_runtime_binding_change_changes_identity(
    field: str,
    value: object,
) -> None:
    original = _edge()
    changed = _edge(
        **{
            field: value,
        }
    )

    assert (
        changed.dependency_edge_id
        != original.dependency_edge_id
    )
    assert (
        changed.fingerprint
        != original.fingerprint
    )


def test_self_dependency_rejects() -> None:
    with pytest.raises(
        LegalWorkDependencyEdgeError,
        match="SELF_DEPENDENCY",
    ):
        _edge(
            successor_work_item_id="work-a",
            successor_work_item_fingerprint=FP_C,
        )


def test_same_work_identity_with_different_fingerprint_rejects() -> None:
    with pytest.raises(
        LegalWorkDependencyEdgeError,
        match="SELF_DEPENDENCY",
    ):
        _edge(
            successor_work_item_id="work-a",
            successor_work_item_fingerprint=FP_D,
        )


@pytest.mark.parametrize(
    "tenant",
    (
        "",
        " tenant-law",
        "tenant-law ",
        "default",
        "global",
        "root",
        "*",
    ),
)
def test_tenant_scope_is_exact_and_pseudo_tenants_reject(
    tenant: str,
) -> None:
    with pytest.raises(
        LegalWorkDependencyEdgeError,
    ):
        _edge(
            tenant_id=tenant,
        )


@pytest.mark.parametrize(
    "field",
    (
        "source_materialization_receipt_id",
        "source_materialization_receipt_fingerprint",
        "predecessor_work_item_fingerprint",
        "successor_work_item_fingerprint",
    ),
)
def test_fingerprint_coordinates_require_lowercase_sha3_512_shape(
    field: str,
) -> None:
    with pytest.raises(
        LegalWorkDependencyEdgeError,
        match="FINGERPRINT",
    ):
        _edge(
            **{
                field: "A" * 128,
            }
        )

    with pytest.raises(
        LegalWorkDependencyEdgeError,
        match="FINGERPRINT",
    ):
        _edge(
            **{
                field: "a" * 127,
            }
        )


def test_round_trip_preserves_exact_truth_and_fingerprint() -> None:
    original = _edge()

    hydrated = LegalWorkDependencyEdge.from_dict(
        original.to_dict()
    )

    assert hydrated == original
    assert (
        hydrated.dependency_edge_id
        == original.dependency_edge_id
    )
    assert (
        hydrated.fingerprint
        == original.fingerprint
    )


def test_hydration_rejects_missing_extra_and_corrupt_truth() -> None:
    raw = _edge().to_dict()

    missing = dict(
        raw
    )
    missing.pop(
        "predecessor_work_item_id"
    )

    with pytest.raises(
        LegalWorkDependencyEdgeError,
    ):
        LegalWorkDependencyEdge.from_dict(
            missing
        )

    extra = dict(
        raw
    )
    extra["blocked"] = True

    with pytest.raises(
        LegalWorkDependencyEdgeError,
    ):
        LegalWorkDependencyEdge.from_dict(
            extra
        )

    corrupt = dict(
        raw
    )
    corrupt["fingerprint"] = FP_E

    with pytest.raises(
        LegalWorkDependencyEdgeError,
        match="FINGERPRINT_MISMATCH",
    ):
        LegalWorkDependencyEdge.from_dict(
            corrupt
        )


def test_domain_contains_no_satisfaction_completion_or_mutable_blocked_state() -> None:
    fields = set(
        _edge().to_dict()
    )

    forbidden = {
        "satisfied",
        "satisfied_at",
        "satisfaction_id",
        "completion_id",
        "completed_at",
        "status",
        "blocked",
        "is_blocked",
        "released",
        "released_at",
    }

    assert fields.isdisjoint(
        forbidden
    )


def test_domain_contains_no_assignment_supervision_iam_ai_notification_or_finance_authority() -> None:
    fields = set(
        _edge().to_dict()
    )

    forbidden = {
        "assignee_principal_id",
        "supervisor_principal_id",
        "authorization_decision_id",
        "permission",
        "role",
        "notification_id",
        "notification_channel",
        "ai_provider",
        "ai_model",
        "invoice_id",
        "payment_id",
        "settlement_id",
    }

    assert fields.isdisjoint(
        forbidden
    )


def test_domain_does_not_claim_global_dag_or_cross_receipt_graph_authority() -> None:
    fields = set(
        _edge().to_dict()
    )

    forbidden = {
        "graph_id",
        "dag_id",
        "topological_order",
        "graph_revision",
        "global_dependency_set",
    }

    assert fields.isdisjoint(
        forbidden
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_dependency_edge.py
# VERSION: v1.0.0-P14-R8-WORK-DEPENDENCY-EDGE-UNIT-CERT
# DEPENDENCY EDGE != DEPENDENCY SATISFACTION
# DEPENDENCY SATISFACTION != WORK COMPLETION
# BLOCKED POSTURE: NOT STORED
# GLOBAL DAG AUTHORITY: NOT CLAIMED
# ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# NOTIFICATION / AI / LEGAL-EVENT AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
