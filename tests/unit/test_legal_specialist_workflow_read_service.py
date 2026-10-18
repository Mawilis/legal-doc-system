"""
WILSY OS — Legal Specialist Workflow P1 Read Service RED Contract.

The service is intentionally absent. These tests freeze the smallest
non-authorizing durable read-orchestration boundary required to construct
LegalSpecialistWorkflowContext values for work already admitted by
LegalProductiveWorkProjection.
"""

from __future__ import annotations

from datetime import datetime, timezone
import importlib

import pytest


NOW = datetime(
    2026,
    10,
    18,
    12,
    0,
    tzinfo=timezone.utc,
)


def _subject_module():
    return importlib.import_module(
        "tools.eos.legal_operations.service."
        "legal_specialist_workflow_read_service"
    )


def test_p1_service_module_and_public_contract_exist() -> None:
    module = _subject_module()

    assert hasattr(
        module,
        "LegalSpecialistWorkflowReadService",
    )
    assert hasattr(
        module,
        "LegalSpecialistWorkflowReadServiceError",
    )
    assert hasattr(
        module,
        "LegalSpecialistWorkflowReadServiceTransactionRequiredError",
    )


def test_p1_service_is_read_orchestration_not_authority() -> None:
    module = _subject_module()
    subject_type = module.LegalSpecialistWorkflowReadService

    for name in (
        "create",
        "assign",
        "supervise",
        "complete",
        "transition",
        "authorize",
        "grant",
        "revoke",
        "pay",
        "settle",
    ):
        assert not hasattr(
            subject_type,
            name,
        )


def test_p1_service_requires_caller_owned_active_transaction() -> None:
    module = _subject_module()

    class Reader:
        pass

    subject = module.LegalSpecialistWorkflowReadService(
        work_item_registry=Reader(),
        receipt_registry=Reader(),
        workflow_instance_registry=Reader(),
        workflow_transition_registry=Reader(),
        workflow_stage_registry=Reader(),
        dependency_registry=Reader(),
        completion_registry=Reader(),
        gate_satisfaction_registry=Reader(),
    )

    with pytest.raises(
        module.LegalSpecialistWorkflowReadServiceTransactionRequiredError,
        match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
    ):
        subject.project(
            tenant_id="tenant-a",
            principal_id="principal-a",
            as_of=NOW,
            productive_work=object(),
            session=object(),
        )


def test_p1_service_does_not_treat_work_item_as_workflow_authority() -> None:
    module = _subject_module()

    # Frozen design rule:
    # LegalWorkItem carries no workflow_instance_id, stage_definition_id,
    # receipt_id, or transition_id. Correlation must be proven from durable
    # materialization receipt output and transition history.
    assert (
        module.WORKFLOW_CORRELATION_MODEL
        == (
            "VISIBLE_WORK_ITEM_ID"
            "->MATERIALIZATION_RECEIPT_OUTPUT"
            "->TRANSITION_ID"
            "->WORKFLOW_INSTANCE"
        )
    )


def test_p1_service_exports_no_new_execution_authority() -> None:
    module = _subject_module()

    contract = module.PUBLIC_CONTRACT

    assert contract["authority_ceiling"] == (
        "LegalProductiveWorkProjection"
    )
    assert contract["creates_authority"] is False
    assert contract["caller_owned_transaction"] is True
    assert contract["work_creation_authority"] is False
    assert contract["assignment_authority"] is False
    assert contract["supervision_authority"] is False
    assert contract["completion_authority"] is False
    assert contract["transition_authority"] is False
    assert contract["iam_authority"] is False
    assert contract["financial_authority"] is False


def test_p1_service_has_no_persistence_or_current_pointer_surface() -> None:
    module = _subject_module()

    subject_type = module.LegalSpecialistWorkflowReadService

    for name in (
        "ensure_indexes",
        "create_or_replay",
        "insert",
        "update",
        "replace",
        "delete",
        "set_current",
        "mark_current",
    ):
        assert not hasattr(
            subject_type,
            name,
        )
