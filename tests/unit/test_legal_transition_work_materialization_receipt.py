"""
WILSY OS — Transition Work Materialization Receipt Domain Certificate

VERSION:
    v1.0.0-P14-P12A-TRANSITION-WORK-MATERIALIZATION-RECEIPT-RED-CERT

PURPOSE:
    Freeze immutable replay provenance binding one exact persisted workflow
    transition to one exact selected work-materialization policy revision and
    the exact deterministic work outputs produced from that selection.

AUTHORITY:
    Historical composition evidence only.

    The receipt does not:
    - create work;
    - assign or supervise principals;
    - grant IAM or professional authority;
    - calculate jurisdictional legal deadlines;
    - deliver notifications;
    - invoke AI;
    - execute billing, payment, settlement or finance.

REPLAY GUARANTEE:
    Later policy revisions must never reinterpret an existing transition.

COMPETITIVE POSTURE:
    Preserve stage-triggered automation with immutable historical provenance,
    deterministic replay and stage-reentry separation.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.legal_transition_work_materialization_receipt import (
    SCHEMA,
    VERSION,
    LegalTransitionWorkMaterializationOutput,
    LegalTransitionWorkMaterializationReceipt,
    LegalTransitionWorkMaterializationReceiptError,
)


NOW = datetime(
    2026,
    10,
    16,
    12,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)

FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128
FP_D = "d" * 128
FP_E = "e" * 128


def _output(
    *,
    work_item_id: str = "work-item-a",
    work_item_fingerprint: str = FP_D,
) -> LegalTransitionWorkMaterializationOutput:
    return LegalTransitionWorkMaterializationOutput(
        work_item_id=work_item_id,
        work_item_fingerprint=work_item_fingerprint,
    )


def _receipt(
    *,
    tenant_id: str = "tenant-law",
    case_matter_id: str = "matter-1",
    transition_id: str = "transition-1",
    transition_fingerprint: str = FP_A,
    workflow_definition_id: str = "workflow-litigation",
    target_stage_definition_id: str = "stage-filing",
    policy_id: str = "policy-filing",
    policy_revision: int = 1,
    policy_fingerprint: str = FP_B,
    outputs: tuple[LegalTransitionWorkMaterializationOutput, ...] | None = None,
    materialized_at: datetime = NOW,
) -> LegalTransitionWorkMaterializationReceipt:
    return LegalTransitionWorkMaterializationReceipt(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        transition_id=transition_id,
        transition_fingerprint=transition_fingerprint,
        workflow_definition_id=workflow_definition_id,
        target_stage_definition_id=target_stage_definition_id,
        policy_id=policy_id,
        policy_revision=policy_revision,
        policy_fingerprint=policy_fingerprint,
        outputs=outputs or (_output(),),
        materialized_at=materialized_at,
    )


def test_identity_schema_version_and_immutability_are_exact() -> None:
    value = _receipt()

    assert VERSION == (
        "v1.0.0-P14-P12-"
        "TRANSITION-WORK-MATERIALIZATION-RECEIPT"
    )
    assert SCHEMA == (
        "WILSY-LEGAL-TRANSITION-WORK-MATERIALIZATION-RECEIPT/V1"
    )

    assert value.tenant_id == "tenant-law"
    assert value.case_matter_id == "matter-1"
    assert value.transition_id == "transition-1"
    assert value.policy_revision == 1
    assert len(value.receipt_id) == 128
    assert len(value.fingerprint) == 128

    with pytest.raises(FrozenInstanceError):
        value.policy_revision = 2  # type: ignore[misc]


def test_receipt_identity_is_deterministic_from_bound_inputs() -> None:
    left = _receipt()
    right = _receipt()

    assert left.receipt_id == right.receipt_id
    assert left.fingerprint == right.fingerprint


def test_transition_identity_change_changes_receipt_identity() -> None:
    baseline = _receipt()
    changed = _receipt(
        transition_id="transition-2",
        transition_fingerprint=FP_C,
    )

    assert baseline.receipt_id != changed.receipt_id
    assert baseline.fingerprint != changed.fingerprint


def test_policy_revision_change_changes_receipt_identity() -> None:
    baseline = _receipt()
    changed = _receipt(
        policy_revision=2,
        policy_fingerprint=FP_C,
    )

    assert baseline.receipt_id != changed.receipt_id
    assert baseline.fingerprint != changed.fingerprint


def test_stage_reentry_new_transition_creates_distinct_receipt() -> None:
    first_entry = _receipt(
        transition_id="transition-entry-1",
        transition_fingerprint=FP_A,
    )
    second_entry = _receipt(
        transition_id="transition-entry-2",
        transition_fingerprint=FP_C,
    )

    assert first_entry.receipt_id != second_entry.receipt_id


def test_outputs_are_ordered_immutable_work_bindings() -> None:
    value = _receipt(
        outputs=(
            _output(
                work_item_id="work-a",
                work_item_fingerprint=FP_D,
            ),
            _output(
                work_item_id="work-b",
                work_item_fingerprint=FP_E,
            ),
        )
    )

    assert tuple(
        item.work_item_id
        for item in value.outputs
    ) == (
        "work-a",
        "work-b",
    )


def test_duplicate_work_item_identity_rejects() -> None:
    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptError,
        match="DUPLICATE",
    ):
        _receipt(
            outputs=(
                _output(
                    work_item_id="work-a",
                    work_item_fingerprint=FP_D,
                ),
                _output(
                    work_item_id="work-a",
                    work_item_fingerprint=FP_E,
                ),
            )
        )


@pytest.mark.parametrize(
    "tenant_id",
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
    tenant_id: str,
) -> None:
    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptError,
    ):
        _receipt(
            tenant_id=tenant_id,
        )


def test_policy_revision_must_be_positive_integer_not_boolean() -> None:
    for revision in (
        0,
        -1,
        True,
        False,
        1.5,
        "1",
    ):
        with pytest.raises(
            LegalTransitionWorkMaterializationReceiptError,
        ):
            _receipt(
                policy_revision=revision,  # type: ignore[arg-type]
            )


@pytest.mark.parametrize(
    "field,value",
    (
        ("transition_fingerprint", "A" * 128),
        ("transition_fingerprint", "a" * 127),
        ("policy_fingerprint", "B" * 128),
        ("policy_fingerprint", "b" * 127),
    ),
)
def test_input_fingerprints_require_lowercase_sha3_512(
    field: str,
    value: str,
) -> None:
    kwargs = {
        field: value,
    }

    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptError,
    ):
        _receipt(
            **kwargs,  # type: ignore[arg-type]
        )


def test_output_fingerprint_requires_lowercase_sha3_512() -> None:
    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptError,
    ):
        _output(
            work_item_fingerprint="D" * 128,
        )


def test_materialized_at_requires_timezone_aware_timestamp() -> None:
    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptError,
        match="MATERIALIZED_AT",
    ):
        _receipt(
            materialized_at=datetime(
                2026,
                10,
                16,
                12,
                0,
                0,
            )
        )


def test_round_trip_preserves_exact_receipt_and_fingerprint() -> None:
    original = _receipt(
        outputs=(
            _output(
                work_item_id="work-a",
                work_item_fingerprint=FP_D,
            ),
            _output(
                work_item_id="work-b",
                work_item_fingerprint=FP_E,
            ),
        )
    )

    restored = LegalTransitionWorkMaterializationReceipt.from_dict(
        original.to_dict()
    )

    assert restored == original
    assert restored.receipt_id == original.receipt_id
    assert restored.fingerprint == original.fingerprint


def test_hydration_rejects_missing_extra_or_corrupt_truth() -> None:
    payload = _receipt().to_dict()

    missing = dict(payload)
    missing.pop("policy_id")

    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptError,
        match="SCHEMA",
    ):
        LegalTransitionWorkMaterializationReceipt.from_dict(
            missing
        )

    extra = dict(payload)
    extra["unexpected"] = True

    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptError,
        match="SCHEMA",
    ):
        LegalTransitionWorkMaterializationReceipt.from_dict(
            extra
        )

    corrupt = dict(payload)
    corrupt["fingerprint"] = "0" * 128

    with pytest.raises(
        LegalTransitionWorkMaterializationReceiptError,
        match="FINGERPRINT",
    ):
        LegalTransitionWorkMaterializationReceipt.from_dict(
            corrupt
        )


def test_receipt_contains_no_policy_selection_authority_input() -> None:
    payload = _receipt().to_dict()

    forbidden = {
        "requested_policy_id",
        "browser_policy_id",
        "client_policy_fingerprint",
        "policy_selector",
        "policy_override",
    }

    assert forbidden.isdisjoint(payload)


def test_receipt_contains_no_assignment_supervision_or_iam_authority() -> None:
    payload = _receipt().to_dict()

    forbidden = {
        "assignee_principal_id",
        "assigned_by_principal_id",
        "supervisor_principal_id",
        "supervisee_principal_id",
        "permission",
        "permissions",
        "authorization_decision",
    }

    assert forbidden.isdisjoint(payload)


def test_receipt_contains_no_legal_deadline_notification_ai_or_financial_authority() -> None:
    payload = _receipt().to_dict()

    forbidden = {
        "legal_deadline_id",
        "jurisdiction_reference",
        "notification_recipient",
        "notification_channel",
        "ai_provider",
        "ai_model",
        "tool_invocation",
        "payment_state",
        "settlement_state",
        "billing_authority",
    }

    assert forbidden.isdisjoint(payload)


def test_competitive_replay_contract_is_explicit() -> None:
    """
    Same immutable inputs and outputs yield the same receipt. New transition
    identity or selected policy revision yields a distinct receipt.

    This prevents mutable task-rule reinterpretation of historical workflow
    transitions while preserving stage-reentry automation.
    """
    first = _receipt()

    replay = _receipt()

    newer_policy = _receipt(
        policy_revision=2,
        policy_fingerprint=FP_C,
    )

    reentry = _receipt(
        transition_id="transition-2",
        transition_fingerprint=FP_C,
    )

    assert replay == first
    assert replay.receipt_id == first.receipt_id
    assert newer_policy.receipt_id != first.receipt_id
    assert reentry.receipt_id != first.receipt_id


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_transition_work_materialization_receipt.py
# VERSION: v1.0.0-P14-P12A-TRANSITION-WORK-MATERIALIZATION-RECEIPT-RED-CERT
# AUTHORITY BOUNDARY: immutable composition-evidence contract only
# HISTORICAL POLICY REINTERPRETATION: FORBIDDEN
# STAGE REENTRY: distinct transition receipt required
# ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# LEGAL-DEADLINE / NOTIFICATION / AI AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
