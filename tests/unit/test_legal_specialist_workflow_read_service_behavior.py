"""
WILSY OS — Legal Specialist Workflow P1 Behavioral Certificate.

Certifies read-only orchestration semantics:
- productive-work visibility remains absolute;
- work->receipt->transition->instance correlation is explicit;
- no receipt creates no workflow context;
- ambiguous receipt correlation fails closed;
- predecessor blocking derives only from canonical completion currentness;
- ambiguous/corrupt completion evidence fails closed;
- unsatisfied gates derive from configured gates minus positive satisfaction;
- caller-owned session propagates unchanged through every durable read.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, cast

import pytest

import tools.eos.legal_operations.service.legal_specialist_workflow_read_service as subject_module
from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkProjection,
)
from tools.eos.legal_operations.domain.legal_work_completion_currentness import (
    LegalWorkCompletionCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)


NOW = datetime(
    2026,
    10,
    18,
    12,
    30,
    tzinfo=timezone.utc,
)

SESSION = SimpleNamespace(
    in_transaction=True,
)


def _work(
    work_item_id: str,
    *,
    matter: str = "matter-1",
    source_fp: str = "a" * 128,
) -> LegalWorkItem:
    return LegalWorkItem(
        work_item_id=work_item_id,
        tenant_id="tenant-a",
        case_matter_id=matter,
        title=work_item_id,
        source_kind="TEST",
        source_reference=f"source:{work_item_id}",
        source_evidence_fingerprint=source_fp,
        status=LegalWorkItemStatus.OPEN,
        created_at=NOW,
    )


def _productive(
    work: LegalWorkItem,
) -> LegalProductiveWorkProjection:
    return LegalProductiveWorkProjection(
        tenant_id="tenant-a",
        principal_id="principal-a",
        as_of=NOW,
        operating_contexts=(),
        capability_ids=(),
        assigned_work_items=(work,),
        supervised_work_items=(),
        overdue_work_items=(),
        due_soon_work_items=(),
    )


class Calls:
    def __init__(self) -> None:
        self.sessions: list[object] = []

    def seen(
        self,
        session: object,
    ) -> None:
        self.sessions.append(session)


def _fixture(
    *,
    visible: LegalWorkItem,
    predecessor: LegalWorkItem | None = None,
    receipts: tuple[object, ...] | None = None,
    configured_gates: tuple[str, ...] = (
        "gate-a",
        "gate-b",
    ),
    satisfied_gates: tuple[str, ...] = (
        "gate-a",
    ),
    completion_state: LegalWorkCompletionCurrentnessState = (
        LegalWorkCompletionCurrentnessState.NOT_COMPLETED
    ),
):
    calls = Calls()

    predecessor = predecessor or _work(
        "work-predecessor",
        source_fp="b" * 128,
    )

    output = SimpleNamespace(
        work_item_id=visible.work_item_id,
        work_item_fingerprint=visible.fingerprint,
    )

    default_receipt = SimpleNamespace(
        tenant_id="tenant-a",
        case_matter_id=visible.case_matter_id,
        transition_id="transition-1",
        transition_fingerprint="c" * 128,
        workflow_definition_id="workflow-1",
        target_stage_definition_id="stage-review",
        outputs=(output,),
        receipt_id="d" * 128,
    )

    receipt_values = (
        (default_receipt,)
        if receipts is None
        else receipts
    )

    instance = SimpleNamespace(
        tenant_id="tenant-a",
        case_matter_id=visible.case_matter_id,
        workflow_instance_id="instance-1",
        workflow_definition_id="workflow-1",
        workflow_definition_fingerprint="e" * 128,
        workflow_topology_fingerprint="f" * 128,
        fingerprint="1" * 128,
    )

    transition = SimpleNamespace(
        transition_id="transition-1",
        fingerprint="c" * 128,
        workflow_instance_id="instance-1",
    )

    currentness = SimpleNamespace(
        tenant_id="tenant-a",
        case_matter_id=visible.case_matter_id,
        workflow_instance_id="instance-1",
        workflow_instance_fingerprint="1" * 128,
        workflow_topology_fingerprint="f" * 128,
        current_stage_definition_id="stage-review",
    )

    stage = SimpleNamespace(
        workflow_definition_id="workflow-1",
        stage_definition_id="stage-review",
        completion_gate_references=configured_gates,
    )

    satisfactions = tuple(
        SimpleNamespace(
            tenant_id="tenant-a",
            workflow_instance_id="instance-1",
            source_stage_definition_id="stage-review",
            gate_reference=gate,
        )
        for gate in satisfied_gates
    )

    edge = SimpleNamespace(
        tenant_id="tenant-a",
        case_matter_id=visible.case_matter_id,
        successor_work_item_id=visible.work_item_id,
        successor_work_item_fingerprint=visible.fingerprint,
        predecessor_work_item_id=predecessor.work_item_id,
        predecessor_work_item_fingerprint=predecessor.fingerprint,
    )

    class WorkItems:
        def get_by_id(
            self,
            tenant_id,
            work_item_id,
            *,
            session,
        ):
            calls.seen(session)
            assert tenant_id == "tenant-a"
            assert work_item_id == predecessor.work_item_id
            return predecessor

    class Receipts:
        def list_matter(
            self,
            tenant_id,
            case_matter_id,
            *,
            session,
        ):
            calls.seen(session)
            assert tenant_id == "tenant-a"
            assert case_matter_id == visible.case_matter_id
            return receipt_values

    class Instances:
        def list_matter_instances(
            self,
            tenant_id,
            case_matter_id,
            *,
            session,
        ):
            calls.seen(session)
            return (instance,)

    class Transitions:
        def list_history(
            self,
            tenant_id,
            workflow_instance_id,
            *,
            session,
        ):
            calls.seen(session)
            return (transition,)

        def derive_currentness(
            self,
            currentness_id,
            workflow_instance,
            *,
            session,
        ):
            calls.seen(session)
            assert len(currentness_id) == 128
            assert workflow_instance is instance
            return currentness

    class Stages:
        def get_by_definition_stage(
            self,
            workflow_definition_fingerprint,
            stage_definition_id,
            *,
            session,
        ):
            calls.seen(session)
            assert workflow_definition_fingerprint == "e" * 128
            assert stage_definition_id == "stage-review"
            return stage

    class Dependencies:
        def list_predecessors(
            self,
            tenant_id,
            successor_work_item_id,
            *,
            session,
        ):
            calls.seen(session)
            return (edge,)

    class Completions:
        def list_work_history(
            self,
            tenant_id,
            work_item_id,
            *,
            session,
        ):
            calls.seen(session)
            return ()

    class Gates:
        def list_workflow_stage(
            self,
            tenant_id,
            workflow_instance_id,
            source_stage_definition_id,
            *,
            session,
        ):
            calls.seen(session)
            return satisfactions

    service = (
        subject_module.LegalSpecialistWorkflowReadService(
            work_item_registry=cast(Any, WorkItems()),
            receipt_registry=cast(Any, Receipts()),
            workflow_instance_registry=cast(Any, Instances()),
            workflow_transition_registry=cast(Any, Transitions()),
            workflow_stage_registry=cast(Any, Stages()),
            dependency_registry=cast(Any, Dependencies()),
            completion_registry=cast(Any, Completions()),
            gate_satisfaction_registry=cast(Any, Gates()),
        )
    )

    fake_currentness = SimpleNamespace(
        state=completion_state,
    )

    return (
        service,
        calls,
        fake_currentness,
        default_receipt,
    )


def test_happy_path_composes_dependency_gate_and_materialization_context(
    monkeypatch,
) -> None:
    visible = _work(
        "work-visible",
    )

    (
        service,
        calls,
        fake_currentness,
        receipt,
    ) = _fixture(
        visible=visible,
    )

    monkeypatch.setattr(
        subject_module,
        "project_legal_work_completion_currentness",
        lambda **kwargs: fake_currentness,
    )

    result = service.project(
        tenant_id="tenant-a",
        principal_id="principal-a",
        as_of=NOW,
        productive_work=_productive(
            visible
        ),
        session=SESSION,
    )

    assert len(result.rows) == 1

    row = result.rows[0]

    assert row.work_item_id == "work-visible"
    assert row.workflow_instance_id == "instance-1"
    assert row.stage_definition_id == "stage-review"

    assert row.blocking_dependency_work_item_ids == (
        "work-predecessor",
    )

    assert row.unsatisfied_gate_references == (
        "gate-b",
    )

    assert row.materialization_transition_id == (
        "transition-1"
    )

    assert row.materialization_receipt_id == (
        receipt.receipt_id
    )

    assert row.readiness == (
        "BLOCKED_DEPENDENCY_AND_GATE"
    )

    assert calls.sessions
    assert all(
        session is SESSION
        for session in calls.sessions
    )


def test_completed_predecessor_and_fully_satisfied_gates_are_actionable(
    monkeypatch,
) -> None:
    visible = _work(
        "work-visible",
    )

    (
        service,
        _calls,
        fake_currentness,
        _receipt,
    ) = _fixture(
        visible=visible,
        configured_gates=("gate-a",),
        satisfied_gates=("gate-a",),
        completion_state=(
            LegalWorkCompletionCurrentnessState.COMPLETED
        ),
    )

    monkeypatch.setattr(
        subject_module,
        "project_legal_work_completion_currentness",
        lambda **kwargs: fake_currentness,
    )

    result = service.project(
        tenant_id="tenant-a",
        principal_id="principal-a",
        as_of=NOW,
        productive_work=_productive(
            visible
        ),
        session=SESSION,
    )

    row = result.rows[0]

    assert row.blocking_dependency_work_item_ids == ()
    assert row.unsatisfied_gate_references == ()
    assert row.readiness == "ACTIONABLE"


def test_visible_work_without_materialization_receipt_is_not_manufactured_into_workflow_row(
    monkeypatch,
) -> None:
    visible = _work(
        "work-visible",
    )

    (
        service,
        _calls,
        fake_currentness,
        _receipt,
    ) = _fixture(
        visible=visible,
        receipts=(),
    )

    monkeypatch.setattr(
        subject_module,
        "project_legal_work_completion_currentness",
        lambda **kwargs: fake_currentness,
    )

    result = service.project(
        tenant_id="tenant-a",
        principal_id="principal-a",
        as_of=NOW,
        productive_work=_productive(
            visible
        ),
        session=SESSION,
    )

    assert result.rows == ()


def test_multiple_receipts_for_one_visible_work_fail_closed(
    monkeypatch,
) -> None:
    visible = _work(
        "work-visible",
    )

    (
        _service,
        _calls,
        fake_currentness,
        receipt,
    ) = _fixture(
        visible=visible,
    )

    duplicate_receipt = SimpleNamespace(
        **receipt.__dict__,
    )

    (
        service,
        _calls2,
        _fake2,
        _default2,
    ) = _fixture(
        visible=visible,
        receipts=(
            receipt,
            duplicate_receipt,
        ),
    )

    monkeypatch.setattr(
        subject_module,
        "project_legal_work_completion_currentness",
        lambda **kwargs: fake_currentness,
    )

    with pytest.raises(
        subject_module.LegalSpecialistWorkflowReadServiceError,
        match="WORK_MATERIALIZATION_AMBIGUOUS",
    ):
        service.project(
            tenant_id="tenant-a",
            principal_id="principal-a",
            as_of=NOW,
            productive_work=_productive(
                visible
            ),
            session=SESSION,
        )


@pytest.mark.parametrize(
    "state",
    (
        LegalWorkCompletionCurrentnessState.AMBIGUOUS,
        LegalWorkCompletionCurrentnessState.CORRUPT_BLOCKED,
    ),
)
def test_nondecisive_predecessor_completion_fails_closed(
    monkeypatch,
    state,
) -> None:
    visible = _work(
        "work-visible",
    )

    (
        service,
        _calls,
        fake_currentness,
        _receipt,
    ) = _fixture(
        visible=visible,
        completion_state=state,
    )

    monkeypatch.setattr(
        subject_module,
        "project_legal_work_completion_currentness",
        lambda **kwargs: fake_currentness,
    )

    with pytest.raises(
        subject_module.LegalSpecialistWorkflowReadServiceError,
        match="PREDECESSOR_COMPLETION_NOT_DECISIVE",
    ):
        service.project(
            tenant_id="tenant-a",
            principal_id="principal-a",
            as_of=NOW,
            productive_work=_productive(
                visible
            ),
            session=SESSION,
        )


def test_gate_scope_drift_fails_closed(
    monkeypatch,
) -> None:
    visible = _work(
        "work-visible",
    )

    (
        service,
        _calls,
        fake_currentness,
        _receipt,
    ) = _fixture(
        visible=visible,
    )

    class BadGates:
        def list_workflow_stage(
            self,
            tenant_id,
            workflow_instance_id,
            source_stage_definition_id,
            *,
            session,
        ):
            return (
                SimpleNamespace(
                    tenant_id="tenant-other",
                    workflow_instance_id="instance-1",
                    source_stage_definition_id="stage-review",
                    gate_reference="gate-a",
                ),
            )

    service._gates = cast(Any, BadGates())

    monkeypatch.setattr(
        subject_module,
        "project_legal_work_completion_currentness",
        lambda **kwargs: fake_currentness,
    )

    with pytest.raises(
        subject_module.LegalSpecialistWorkflowReadServiceError,
        match="GATE_SCOPE_MISMATCH",
    ):
        service.project(
            tenant_id="tenant-a",
            principal_id="principal-a",
            as_of=NOW,
            productive_work=_productive(
                visible
            ),
            session=SESSION,
        )
