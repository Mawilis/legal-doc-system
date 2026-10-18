"""P14 transition-to-productive-work materializer contract certificate.

VERSION: v1.0.0-P14-P16-MATERIALIZER-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance / Legal Operations
EPITOME: Locks replay-first, server-derived, non-authorizing materialization.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_transition_work_materialization_service.py
CHANGELOG: v1.0.0 initial fail-closed materializer contract.
TENANT BOUNDARY: exact tenant scope on every registry call.
FINANCIAL AUTHORITY: none; Kennel EOS exclusively executes finance.
"""
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from tools.eos.legal_operations.domain.legal_work_materialization_policy import (
    LegalOperationalDueRule,
    LegalWorkMaterializationPolicy,
    LegalWorkMaterializationTemplate,
)
from tools.eos.legal_operations.registry.legal_transition_work_materialization_receipt_registry import (
    LegalTransitionWorkMaterializationReceiptRegistryNotFoundError,
)
from tools.eos.legal_operations.service.legal_transition_work_materialization_service import (
    LegalTransitionWorkMaterializationService,
    LegalTransitionWorkMaterializationServiceError,
)

NOW = datetime(2026, 10, 16, 8, 30, tzinfo=timezone.utc)
FP_A, FP_B, FP_C = "a" * 128, "b" * 128, "c" * 128


class _ReceiptRegistry:
    def __init__(self) -> None:
        self.values = {}

    def get_by_transition_id(
        self,
        tenant_id,
        transition_id,
        *,
        session,
    ):
        key = (
            tenant_id,
            transition_id,
        )
        if key not in self.values:
            raise LegalTransitionWorkMaterializationReceiptRegistryNotFoundError(
                "missing"
            )
        return self.values[key]

    def create_or_replay(
        self,
        value,
        *,
        session,
    ):
        key = (
            value.tenant_id,
            value.transition_id,
        )

        existing = self.values.get(
            key
        )

        if existing is not None:
            if existing == value:
                return existing

            raise AssertionError(
                "fake receipt registry divergent replay"
            )

        self.values[key] = value
        return value



class _DependencyRegistry:
    def __init__(self) -> None:
        self.values = {}

    def create_or_replay(
        self,
        value,
        *,
        session,
    ):
        existing = self.values.get(
            value.dependency_edge_id
        )

        if existing is not None:
            assert existing == value
            return existing

        self.values[
            value.dependency_edge_id
        ] = value

        return value

    def list_by_receipt(
        self,
        tenant_id,
        receipt_id,
        *,
        session,
    ):
        return tuple(
            sorted(
                (
                    value
                    for value
                    in self.values.values()
                    if value.tenant_id
                    == tenant_id
                    and value.source_materialization_receipt_id
                    == receipt_id
                ),
                key=lambda value: (
                    value.predecessor_work_item_id,
                    value.successor_work_item_id,
                    value.dependency_edge_id,
                ),
            )
        )


class _WorkRegistry:
    def __init__(self) -> None: self.values = {}
    def create_or_replay(self, value, *, session): self.values[value.work_item_id] = value; return value
    def get_by_id(self, tenant_id, work_item_id, *, session): return self.values[work_item_id]


def _policy(*, conditions=(), due=LegalOperationalDueRule.NONE, offset=None):
    return LegalWorkMaterializationPolicy(
        tenant_id="tenant-law", policy_id="policy-a", policy_revision=1,
        workflow_definition_id="workflow-a", workflow_definition_fingerprint=FP_B,
        target_stage_definition_id="stage-b", target_stage_fingerprint=FP_C,
        templates=(LegalWorkMaterializationTemplate(
            work_template_id="template-a", title="Prepare filing", due_rule=due,
            due_offset_seconds=offset, dependency_template_ids=(), condition_references=conditions,
        ),),
    )


def _service(policies):
    transition = SimpleNamespace(
        tenant_id="tenant-law",
        transition_id="transition-a",
        case_matter_id="matter-a",
        workflow_instance_id="instance-a",
        workflow_instance_fingerprint="d" * 128,
        workflow_topology_fingerprint="e" * 128,
        target_stage_definition_id="stage-b",
        target_stage_fingerprint=FP_C,
        transitioned_at=NOW,
        fingerprint=FP_A,
    )
    instance = SimpleNamespace(
        tenant_id="tenant-law",
        case_matter_id="matter-a",
        workflow_instance_id="instance-a",
        workflow_definition_id="workflow-a",
        workflow_definition_fingerprint=FP_B,
        workflow_topology_fingerprint="e" * 128,
        fingerprint="d" * 128,
    )
    transition_registry = SimpleNamespace(list_history=lambda *a, **k: (transition,))
    instance_registry = SimpleNamespace(get_by_id=lambda *a, **k: instance)
    policy_registry = SimpleNamespace(
        list_workflow_stage=lambda *a, **k: tuple(policies),
        get_revision=lambda *a, **k: policies[-1],
    )
    return LegalTransitionWorkMaterializationService(
        transition_registry=transition_registry, workflow_instance_registry=instance_registry,
        policy_registry=policy_registry, work_item_registry=_WorkRegistry(),
        receipt_registry=_ReceiptRegistry(),
        dependency_registry=_DependencyRegistry(),
    )


def test_active_transaction_required() -> None:
    with pytest.raises(LegalTransitionWorkMaterializationServiceError, match="ACTIVE_TRANSACTION"):
        _service((_policy(),)).materialize("tenant-law", "instance-a", "transition-a", session=SimpleNamespace(in_transaction=False))


def test_zero_policy_is_explicit_no_work() -> None:
    result = _service(()).materialize("tenant-law", "instance-a", "transition-a", session=SimpleNamespace(in_transaction=True))
    assert result.receipt is None and result.work_items == () and result.no_policy is True


def test_one_policy_creates_deterministic_work_and_exact_replay() -> None:
    service = _service((_policy(),))
    session = SimpleNamespace(in_transaction=True)
    first = service.materialize("tenant-law", "instance-a", "transition-a", session=session)
    replay = service.materialize("tenant-law", "instance-a", "transition-a", session=session)
    assert first.receipt == replay.receipt
    assert first.work_items == replay.work_items
    assert first.replayed is False
    assert replay.replayed is True
    assert len(first.work_items) == 1
    assert first.work_items[0].due_at is None


def test_transition_offset_is_operational_due_only() -> None:
    result = _service((_policy(due=LegalOperationalDueRule.TRANSITION_OFFSET, offset=3600),)).materialize(
        "tenant-law", "instance-a", "transition-a", session=SimpleNamespace(in_transaction=True)
    )
    assert result.work_items[0].due_at == NOW.replace(hour=9, minute=30)


def test_ambiguous_policy_families_and_unresolved_conditions_fail_closed() -> None:
    other = _policy()
    object.__setattr__(other, "policy_id", "policy-b")
    with pytest.raises(LegalTransitionWorkMaterializationServiceError, match="AMBIGUOUS"):
        _service((_policy(), other)).materialize("tenant-law", "instance-a", "transition-a", session=SimpleNamespace(in_transaction=True))
    with pytest.raises(LegalTransitionWorkMaterializationServiceError, match="CONDITION"):
        _service((_policy(conditions=("condition-a",)),)).materialize("tenant-law", "instance-a", "transition-a", session=SimpleNamespace(in_transaction=True))



def _dependent_policy():
    return LegalWorkMaterializationPolicy(
        tenant_id="tenant-law",
        policy_id="policy-a",
        policy_revision=1,
        workflow_definition_id="workflow-a",
        workflow_definition_fingerprint=FP_B,
        target_stage_definition_id="stage-b",
        target_stage_fingerprint=FP_C,
        templates=(
            LegalWorkMaterializationTemplate(
                work_template_id="template-a",
                title="Prepare source",
                due_rule=LegalOperationalDueRule.NONE,
                due_offset_seconds=None,
                dependency_template_ids=(),
                condition_references=(),
            ),
            LegalWorkMaterializationTemplate(
                work_template_id="template-b",
                title="Review source",
                due_rule=LegalOperationalDueRule.NONE,
                due_offset_seconds=None,
                dependency_template_ids=(
                    "template-a",
                ),
                condition_references=(),
            ),
            LegalWorkMaterializationTemplate(
                work_template_id="template-c",
                title="Approve source",
                due_rule=LegalOperationalDueRule.NONE,
                due_offset_seconds=None,
                dependency_template_ids=(
                    "template-a",
                    "template-b",
                ),
                condition_references=(),
            ),
        ),
    )


def test_policy_dependencies_materialize_exact_runtime_edges() -> None:
    service = _service(
        (
            _dependent_policy(),
        )
    )
    session = SimpleNamespace(
        in_transaction=True
    )

    result = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-a",
        session=session,
    )

    assert result.receipt is not None
    assert len(result.work_items) == 3

    edges = service._dependencies.list_by_receipt(
        "tenant-law",
        result.receipt.receipt_id,
        session=session,
    )

    assert len(edges) == 3

    by_title = {
        value.title:
            value
        for value in result.work_items
    }

    actual = {
        (
            edge.predecessor_work_item_id,
            edge.successor_work_item_id,
        )
        for edge in edges
    }

    expected = {
        (
            by_title[
                "Prepare source"
            ].work_item_id,
            by_title[
                "Review source"
            ].work_item_id,
        ),
        (
            by_title[
                "Prepare source"
            ].work_item_id,
            by_title[
                "Approve source"
            ].work_item_id,
        ),
        (
            by_title[
                "Review source"
            ].work_item_id,
            by_title[
                "Approve source"
            ].work_item_id,
        ),
    }

    assert actual == expected

    for edge in edges:
        assert (
            edge.source_materialization_receipt_id
            == result.receipt.receipt_id
        )
        assert (
            edge.source_materialization_receipt_fingerprint
            == result.receipt.fingerprint
        )


def test_dependency_edge_replay_is_exact_and_duplicate_free() -> None:
    service = _service(
        (
            _dependent_policy(),
        )
    )
    session = SimpleNamespace(
        in_transaction=True
    )

    first = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-a",
        session=session,
    )

    replay = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-a",
        session=session,
    )

    assert first.receipt is not None
    assert replay.receipt == first.receipt
    assert replay.work_items == first.work_items
    assert replay.replayed is True

    edges = service._dependencies.list_by_receipt(
        "tenant-law",
        first.receipt.receipt_id,
        session=session,
    )

    assert len(edges) == 3
    assert (
        len(
            service._dependencies.values
        )
        == 3
    )


def test_replay_rejects_missing_receipt_bound_dependency_edge() -> None:
    service = _service(
        (
            _dependent_policy(),
        )
    )
    session = SimpleNamespace(
        in_transaction=True
    )

    first = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-a",
        session=session,
    )

    assert first.receipt is not None

    missing_id = next(
        iter(
            service._dependencies.values
        )
    )

    del service._dependencies.values[
        missing_id
    ]

    with pytest.raises(
        LegalTransitionWorkMaterializationServiceError,
        match="REPLAY_DEPENDENCY_EDGE_MISMATCH",
    ):
        service.materialize(
            "tenant-law",
            "instance-a",
            "transition-a",
            session=session,
        )


def test_replay_rejects_corrupt_receipt_bound_dependency_edge() -> None:
    service = _service(
        (
            _dependent_policy(),
        )
    )
    session = SimpleNamespace(
        in_transaction=True
    )

    first = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-a",
        session=session,
    )

    assert first.receipt is not None

    edge_id = next(
        iter(
            service._dependencies.values
        )
    )

    edge = service._dependencies.values[
        edge_id
    ]

    object.__setattr__(
        edge,
        "successor_work_item_fingerprint",
        "f" * 128,
    )

    with pytest.raises(
        LegalTransitionWorkMaterializationServiceError,
        match="REPLAY_DEPENDENCY_EDGE_MISMATCH",
    ):
        service.materialize(
            "tenant-law",
            "instance-a",
            "transition-a",
            session=session,
        )


def test_zero_dependency_policy_persists_no_runtime_edges() -> None:
    service = _service(
        (
            _policy(),
        )
    )
    session = SimpleNamespace(
        in_transaction=True
    )

    result = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-a",
        session=session,
    )

    assert result.receipt is not None

    assert (
        service._dependencies.list_by_receipt(
            "tenant-law",
            result.receipt.receipt_id,
            session=session,
        )
        == ()
    )


def test_dependency_composition_introduces_no_satisfaction_completion_or_authority() -> None:
    service = _service(
        (
            _dependent_policy(),
        )
    )

    forbidden = {
        "mark_satisfied",
        "mark_complete",
        "complete",
        "release",
        "block",
        "assign",
        "supervise",
        "notify",
    }

    public = {
        name
        for name in dir(
            service._dependencies
        )
        if not name.startswith("_")
    }

    assert public.isdisjoint(
        forbidden
    )


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_transition_work_materialization_service.py
# VERSION: v1.0.0-P14-P16-MATERIALIZER-UNIT-CERT
# AUTHORITY BOUNDARY: materialization contract evidence only
# TENANT POSTURE: exact / fail closed
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT


def test_replay_uses_receipt_locked_policy_revision_not_newer_revision() -> None:
    policy_v1 = _policy()

    service = _service((policy_v1,))
    session = SimpleNamespace(in_transaction=True)

    first = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-a",
        session=session,
    )

    assert first.receipt is not None
    assert first.receipt.policy_revision == 1

    policy_v2 = LegalWorkMaterializationPolicy(
        tenant_id="tenant-law",
        policy_id="policy-a",
        policy_revision=2,
        workflow_definition_id="workflow-a",
        workflow_definition_fingerprint=FP_B,
        target_stage_definition_id="stage-b",
        target_stage_fingerprint=FP_C,
        templates=(
            LegalWorkMaterializationTemplate(
                work_template_id="template-new",
                title="Different future work",
                due_rule=LegalOperationalDueRule.NONE,
                due_offset_seconds=None,
                dependency_template_ids=(),
                condition_references=(),
            ),
        ),
        supersedes_fingerprint=policy_v1.fingerprint,
    )

    service._policies.list_workflow_stage = (  # type: ignore[attr-defined]
        lambda *a, **k: (
            policy_v1,
            policy_v2,
        )
    )

    service._policies.get_revision = (  # type: ignore[attr-defined]
        lambda tenant_id, policy_id, revision, *, session:
            policy_v1
            if revision == 1
            else policy_v2
    )

    replay = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-a",
        session=session,
    )

    assert replay.replayed is True
    assert replay.receipt == first.receipt
    assert replay.receipt is not None
    assert replay.receipt.policy_revision == 1
    assert replay.work_items == first.work_items


def test_replay_rejects_receipt_transition_fingerprint_mismatch() -> None:
    service = _service((_policy(),))
    session = SimpleNamespace(in_transaction=True)

    first = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-a",
        session=session,
    )

    receipt = first.receipt
    assert receipt is not None

    object.__setattr__(
        receipt,
        "transition_fingerprint",
        "f" * 128,
    )

    with pytest.raises(
        LegalTransitionWorkMaterializationServiceError,
        match="REPLAY_RECEIPT_SCOPE_MISMATCH",
    ):
        service.materialize(
            "tenant-law",
            "instance-a",
            "transition-a",
            session=session,
        )


def test_replay_rejects_missing_receipt_bound_work() -> None:
    service = _service((_policy(),))
    session = SimpleNamespace(in_transaction=True)

    first = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-a",
        session=session,
    )

    assert first.receipt is not None

    service._work.values.clear()  # type: ignore[attr-defined]

    with pytest.raises(KeyError):
        service.materialize(
            "tenant-law",
            "instance-a",
            "transition-a",
            session=session,
        )


def test_replay_rejects_receipt_bound_work_fingerprint_mismatch() -> None:
    service = _service((_policy(),))
    session = SimpleNamespace(in_transaction=True)

    first = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-a",
        session=session,
    )

    receipt = first.receipt
    assert receipt is not None

    output = receipt.outputs[0]

    object.__setattr__(
        output,
        "work_item_fingerprint",
        "f" * 128,
    )

    with pytest.raises(
        LegalTransitionWorkMaterializationServiceError,
        match="REPLAY_WORK_MISMATCH",
    ):
        service.materialize(
            "tenant-law",
            "instance-a",
            "transition-a",
            session=session,
        )


def test_transition_instance_fingerprint_mismatch_fails_closed() -> None:
    service = _service((_policy(),))
    session = SimpleNamespace(in_transaction=True)

    history = service._transitions.list_history(  # type: ignore[attr-defined]
        "tenant-law",
        "instance-a",
        session=session,
    )

    transition = history[0]

    object.__setattr__(
        transition,
        "workflow_instance_fingerprint",
        "f" * 128,
    )

    with pytest.raises(
        LegalTransitionWorkMaterializationServiceError,
        match="TRANSITION_SCOPE_MISMATCH",
    ):
        service.materialize(
            "tenant-law",
            "instance-a",
            "transition-a",
            session=session,
        )


def test_transition_topology_fingerprint_mismatch_fails_closed() -> None:
    service = _service((_policy(),))
    session = SimpleNamespace(in_transaction=True)

    history = service._transitions.list_history(  # type: ignore[attr-defined]
        "tenant-law",
        "instance-a",
        session=session,
    )

    transition = history[0]

    object.__setattr__(
        transition,
        "workflow_topology_fingerprint",
        "f" * 128,
    )

    with pytest.raises(
        LegalTransitionWorkMaterializationServiceError,
        match="TRANSITION_SCOPE_MISMATCH",
    ):
        service.materialize(
            "tenant-law",
            "instance-a",
            "transition-a",
            session=session,
        )


def test_multiple_templates_preserve_declared_output_order() -> None:
    policy = LegalWorkMaterializationPolicy(
        tenant_id="tenant-law",
        policy_id="policy-a",
        policy_revision=1,
        workflow_definition_id="workflow-a",
        workflow_definition_fingerprint=FP_B,
        target_stage_definition_id="stage-b",
        target_stage_fingerprint=FP_C,
        templates=(
            LegalWorkMaterializationTemplate(
                work_template_id="template-a",
                title="First",
                due_rule=LegalOperationalDueRule.NONE,
                due_offset_seconds=None,
                dependency_template_ids=(),
                condition_references=(),
            ),
            LegalWorkMaterializationTemplate(
                work_template_id="template-b",
                title="Second",
                due_rule=LegalOperationalDueRule.NONE,
                due_offset_seconds=None,
                dependency_template_ids=(
                    "template-a",
                ),
                condition_references=(),
            ),
        ),
    )

    service = _service((policy,))

    result = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-a",
        session=SimpleNamespace(
            in_transaction=True
        ),
    )

    assert [
        value.title
        for value in result.work_items
    ] == [
        "First",
        "Second",
    ]

    assert result.receipt is not None

    assert [
        output.work_item_id
        for output in result.receipt.outputs
    ] == [
        value.work_item_id
        for value in result.work_items
    ]


def test_stage_reentry_transition_identity_derives_distinct_work_identity() -> None:
    service = _service((_policy(),))
    session = SimpleNamespace(in_transaction=True)

    first = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-a",
        session=session,
    )

    transition_b = SimpleNamespace(
        tenant_id="tenant-law",
        transition_id="transition-b",
        case_matter_id="matter-a",
        workflow_instance_id="instance-a",
        workflow_instance_fingerprint="d" * 128,
        workflow_topology_fingerprint="e" * 128,
        target_stage_definition_id="stage-b",
        target_stage_fingerprint=FP_C,
        transitioned_at=NOW.replace(hour=10),
        fingerprint="f" * 128,
    )

    service._transitions.list_history = (  # type: ignore[attr-defined]
        lambda *a, **k: (
            transition_b,
        )
    )

    second = service.materialize(
        "tenant-law",
        "instance-a",
        "transition-b",
        session=session,
    )

    assert (
        first.work_items[0].work_item_id
        != second.work_items[0].work_item_id
    )

    assert first.receipt is not None
    assert second.receipt is not None

    assert (
        first.receipt.receipt_id
        != second.receipt.receipt_id
    )


def test_materializer_has_no_assignment_supervision_iam_notification_ai_or_finance_dependencies() -> None:
    service = _service((_policy(),))

    state = vars(service)

    forbidden_names = {
        "_assignment",
        "_assignments",
        "_supervision",
        "_supervisions",
        "_iam",
        "_authorization",
        "_notifications",
        "_notification",
        "_ai",
        "_billing",
        "_payments",
        "_settlements",
    }

    assert forbidden_names.isdisjoint(
        state
    )
