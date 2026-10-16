"""
TITLE: WILSY OS Legal Profile Productive Work Read Service Unit Certificate

VERSION: v1.0.0-PW-P3-RED-DURABLE-PRODUCTIVE-WORK-READ-SERVICE

EPITOME:
    Freeze the read-only service that resolves current durable assignment and
    supervision truth, hydrates corresponding Legal work items, and delegates
    deterministic projection to the already-certified pure composer.

AUTHORITY BOUNDARY:
    Read orchestration only. Operating-role context remains non-authorizing.
    This service creates no IAM, assignment, supervision, work-item, workflow,
    professional, billing, payment, execution or settlement authority.

TRANSACTION:
    Caller supplies one already-active transaction propagated unchanged to
    every durable registry read.

FINANCIAL POSTURE:
    NONE. Kennel EOS exclusively owns financial execution and settlement.
"""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkOperatingContext,
)
from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
)
from tools.eos.legal_operations.domain.legal_work_supervision_binding import (
    LegalSupervisionControlLevel,
    LegalSupervisionScope,
    LegalWorkSupervisionBinding,
)
from tools.eos.legal_operations.service.legal_profile_productive_work_read_service import (
    LegalProductiveWorkReadService,
    LegalProductiveWorkReadServiceError,
    LegalProductiveWorkReadServiceTransactionRequiredError,
)


NOW = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)
TENANT = "tenant-a"
PRINCIPAL = "principal-a"
MATTER = "matter-a"


def _session(active: bool = True) -> object:
    return SimpleNamespace(
        in_transaction=active
    )


def _work(
    work_item_id: str,
    *,
    matter_id: str = MATTER,
) -> LegalWorkItem:
    return LegalWorkItem(
        work_item_id=work_item_id,
        tenant_id=TENANT,
        case_matter_id=matter_id,
        title=f"Work {work_item_id}",
        source_kind="LEGAL_WORKFLOW_STAGE",
        source_reference=f"stage:{work_item_id}",
        source_evidence_fingerprint="a" * 128,
        status="OPEN",
        created_at=NOW,
        due_at=None,
        completion_evidence_reference=None,
        completion_evidence_fingerprint=None,
        completed_at=None,
        cancellation_reason_reference=None,
        cancelled_at=None,
    )


def _assignment(
    assignment_id: str,
    work_item_id: str,
) -> LegalWorkAssignment:
    return LegalWorkAssignment(
        assignment_id=assignment_id,
        tenant_id=TENANT,
        case_matter_id=MATTER,
        work_item_id=work_item_id,
        assignee_principal_id=PRINCIPAL,
        assigned_by_principal_id="principal-assigner",
        assigned_at=NOW,
        assignment_reason_reference="reason:staffing",
        authorization_evidence_reference="authz:assignment",
        supersedes_assignment_id=None,
    )


def _supervision(
    binding_id: str,
    *,
    work_item_id: str | None,
    scope: LegalSupervisionScope,
) -> LegalWorkSupervisionBinding:
    return LegalWorkSupervisionBinding(
        supervision_binding_id=binding_id,
        tenant_id=TENANT,
        case_matter_id=MATTER,
        scope=scope,
        work_item_id=work_item_id,
        supervisee_principal_id="principal-b",
        supervisor_principal_id=PRINCIPAL,
        control_level=(
            LegalSupervisionControlLevel.REVIEW_REQUIRED
        ),
        supervision_plan_reference="plan:review",
        supervision_basis_reference="basis:engagement",
        effective_from=NOW,
        effective_until=None,
        supersedes_supervision_binding_id=None,
    )


def _context(
    role_id: str = "tenant-defined-role",
) -> LegalProductiveWorkOperatingContext:
    return LegalProductiveWorkOperatingContext(
        operating_role_id=role_id,
        operating_role_revision=1,
        display_name="Tenant Defined Role",
        capability_ids=("CAP_MATTER_EXECUTION",),
        office_references=("JOHANNESBURG",),
        practice_references=("DISPUTES",),
        business_unit_references=(),
        jurisdiction_references=("ZA",),
    )


class _OperatingContextHydrator:
    def __init__(
        self,
        values: tuple[
            LegalProductiveWorkOperatingContext,
            ...
        ],
    ) -> None:
        self.values = values
        self.calls: list[
            tuple[
                str,
                str,
                datetime,
                object,
            ]
        ] = []

    def hydrate(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        at: datetime,
        session: object,
    ) -> tuple[
        LegalProductiveWorkOperatingContext,
        ...
    ]:
        self.calls.append(
            (
                tenant_id,
                principal_id,
                at,
                session,
            )
        )
        return self.values


class _AssignmentRegistry:
    def __init__(
        self,
        values: tuple[LegalWorkAssignment, ...],
    ) -> None:
        self.values = values
        self.calls: list[tuple[object, ...]] = []

    def list_current_for_assignee(
        self,
        tenant_id: str,
        principal_id: str,
        *,
        session: object,
    ) -> tuple[LegalWorkAssignment, ...]:
        self.calls.append(
            (
                tenant_id,
                principal_id,
                session,
            )
        )
        return self.values


class _SupervisionRegistry:
    def __init__(
        self,
        values: tuple[LegalWorkSupervisionBinding, ...],
    ) -> None:
        self.values = values
        self.calls: list[tuple[object, ...]] = []

    def list_current_for_supervisor(
        self,
        tenant_id: str,
        supervisor_principal_id: str,
        at: datetime,
        *,
        session: object,
    ) -> tuple[LegalWorkSupervisionBinding, ...]:
        self.calls.append(
            (
                tenant_id,
                supervisor_principal_id,
                at,
                session,
            )
        )
        return self.values


class _WorkItemRegistry:
    def __init__(
        self,
        values: tuple[LegalWorkItem, ...],
    ) -> None:
        self.by_id = {
            item.work_item_id: item
            for item in values
        }
        self.get_calls: list[tuple[object, ...]] = []
        self.matter_calls: list[tuple[object, ...]] = []

    def get_by_id(
        self,
        tenant_id: str,
        work_item_id: str,
        *,
        session: object,
    ) -> LegalWorkItem:
        self.get_calls.append(
            (
                tenant_id,
                work_item_id,
                session,
            )
        )
        return self.by_id[work_item_id]

    def list_matter(
        self,
        tenant_id: str,
        case_matter_id: str,
        *,
        session: object,
    ) -> tuple[LegalWorkItem, ...]:
        self.matter_calls.append(
            (
                tenant_id,
                case_matter_id,
                session,
            )
        )
        return tuple(
            item
            for item in self.by_id.values()
            if item.case_matter_id == case_matter_id
        )


def _service(
    *,
    assignments: tuple[LegalWorkAssignment, ...] = (),
    supervision: tuple[LegalWorkSupervisionBinding, ...] = (),
    work_items: tuple[LegalWorkItem, ...] = (),
    contexts: tuple[
        LegalProductiveWorkOperatingContext,
        ...
    ] | None = None,
):
    assignment_registry = _AssignmentRegistry(assignments)
    supervision_registry = _SupervisionRegistry(supervision)
    work_registry = _WorkItemRegistry(work_items)
    context_hydrator = _OperatingContextHydrator(
        (
            _context(),
        )
        if contexts is None
        else contexts
    )

    service = LegalProductiveWorkReadService(
        work_item_registry=work_registry,
        assignment_registry=assignment_registry,
        supervision_registry=supervision_registry,
        operating_context_hydrator=context_hydrator,
    )

    return (
        service,
        assignment_registry,
        supervision_registry,
        work_registry,
    )


def test_active_caller_transaction_required_before_registry_reads() -> None:
    service, assignment, supervision, work = _service()

    with pytest.raises(
        LegalProductiveWorkReadServiceTransactionRequiredError,
        match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
    ):
        service.project(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            as_of=NOW,
            session=_session(False),
        )

    assert assignment.calls == []
    assert supervision.calls == []
    assert work.get_calls == []
    assert work.matter_calls == []


def test_reads_current_assignment_and_supervision_with_same_session() -> None:
    assigned = _work("work-assigned")
    reviewed = _work("work-reviewed")

    service, assignment, supervision, work = _service(
        assignments=(
            _assignment(
                "assignment-a",
                "work-assigned",
            ),
        ),
        supervision=(
            _supervision(
                "supervision-a",
                work_item_id="work-reviewed",
                scope=LegalSupervisionScope.WORK_ITEM,
            ),
        ),
        work_items=(
            assigned,
            reviewed,
        ),
    )

    session = _session()

    projection = service.project(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        session=session,
    )

    assert assignment.calls == [
        (
            TENANT,
            PRINCIPAL,
            session,
        )
    ]

    assert supervision.calls == [
        (
            TENANT,
            PRINCIPAL,
            NOW,
            session,
        )
    ]

    assert tuple(
        item.work_item_id
        for item in projection.assigned_work_items
    ) == ("work-assigned",)

    assert tuple(
        item.work_item_id
        for item in projection.supervised_work_items
    ) == ("work-reviewed",)


def test_work_item_reads_are_deduplicated_across_assignment_and_supervision() -> None:
    work_item = _work("work-a")

    service, _, _, work = _service(
        assignments=(
            _assignment(
                "assignment-a",
                "work-a",
            ),
        ),
        supervision=(
            _supervision(
                "supervision-a",
                work_item_id="work-a",
                scope=LegalSupervisionScope.WORK_ITEM,
            ),
        ),
        work_items=(work_item,),
    )

    projection = service.project(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        session=_session(),
    )

    assert [
        call[1]
        for call in work.get_calls
    ] == ["work-a"]

    assert tuple(
        item.work_item_id
        for item in projection.assigned_work_items
    ) == ("work-a",)

    # Assignment ownership takes precedence in the pure composer;
    # the same work item must not also appear in supervision.
    assert projection.supervised_work_items == ()


def test_matter_scope_supervision_hydrates_complete_matter_work() -> None:
    first = _work("work-one")
    second = _work("work-two")

    service, _, _, work = _service(
        supervision=(
            _supervision(
                "supervision-matter",
                work_item_id=None,
                scope=LegalSupervisionScope.MATTER,
            ),
        ),
        work_items=(
            first,
            second,
        ),
    )

    session = _session()

    projection = service.project(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        session=session,
    )

    assert work.matter_calls == [
        (
            TENANT,
            MATTER,
            session,
        )
    ]

    assert {
        item.work_item_id
        for item in projection.supervised_work_items
    } == {
        "work-one",
        "work-two",
    }


def test_assignment_work_item_scope_mismatch_fails_closed() -> None:
    mismatched = _work(
        "work-a",
        matter_id="matter-b",
    )

    service, _, _, _ = _service(
        assignments=(
            _assignment(
                "assignment-a",
                "work-a",
            ),
        ),
        work_items=(mismatched,),
    )

    with pytest.raises(
        LegalProductiveWorkReadServiceError,
        match="ASSIGNMENT_WORK_ITEM_SCOPE_MISMATCH",
    ):
        service.project(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            as_of=NOW,
            session=_session(),
        )


def test_work_item_supervision_scope_mismatch_fails_closed() -> None:
    mismatched = _work(
        "work-a",
        matter_id="matter-b",
    )

    service, _, _, _ = _service(
        supervision=(
            _supervision(
                "supervision-a",
                work_item_id="work-a",
                scope=LegalSupervisionScope.WORK_ITEM,
            ),
        ),
        work_items=(mismatched,),
    )

    with pytest.raises(
        LegalProductiveWorkReadServiceError,
        match="SUPERVISION_WORK_ITEM_SCOPE_MISMATCH",
    ):
        service.project(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            as_of=NOW,
            session=_session(),
        )


def test_matter_registry_result_scope_mismatch_fails_closed() -> None:
    foreign_matter = _work(
        "work-foreign",
        matter_id="matter-b",
    )

    class _BadMatterRegistry(_WorkItemRegistry):
        def list_matter(
            self,
            tenant_id: str,
            case_matter_id: str,
            *,
            session: object,
        ) -> tuple[LegalWorkItem, ...]:
            self.matter_calls.append(
                (
                    tenant_id,
                    case_matter_id,
                    session,
                )
            )
            return (
                foreign_matter,
            )

    work_registry = _BadMatterRegistry(
        (foreign_matter,)
    )

    service = LegalProductiveWorkReadService(
        work_item_registry=work_registry,
        assignment_registry=_AssignmentRegistry(()),
        supervision_registry=_SupervisionRegistry(
            (
                _supervision(
                    "supervision-matter",
                    work_item_id=None,
                    scope=LegalSupervisionScope.MATTER,
                ),
            )
        ),
        operating_context_hydrator=_OperatingContextHydrator(
            (
                _context(),
            )
        ),
    )

    with pytest.raises(
        LegalProductiveWorkReadServiceError,
        match="MATTER_WORK_ITEM_SCOPE_MISMATCH",
    ):
        service.project(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            as_of=NOW,
            session=_session(),
        )


def test_custom_role_context_passes_through_without_title_branching() -> None:
    service, _, _, _ = _service(
        contexts=(
            _context(
                "customer-invented-global-specialist-title"
            ),
        )
    )

    projection = service.project(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        session=_session(),
    )

    assert tuple(
        context.operating_role_id
        for context in projection.operating_contexts
    ) == (
        "customer-invented-global-specialist-title",
    )


def test_read_service_exposes_no_mutation_or_financial_authority() -> None:
    service, _, _, _ = _service()

    for forbidden in (
        "assign",
        "supervise",
        "authorize",
        "create",
        "update",
        "delete",
        "pay",
        "invoice",
        "settle",
    ):
        assert not hasattr(
            service,
            forbidden,
        )


# AUTHORITY BOUNDARY:
# read-only durable work composition.
# No IAM, assignment, supervision, workflow or financial execution authority.
