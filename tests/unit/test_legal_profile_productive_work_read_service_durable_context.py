"""
TITLE: WILSY OS Productive-Work Read Service Durable CX27 Context Wiring Contract

VERSION: v1.0.0-PW-P8A-RED-DURABLE-CONTEXT-WIRING

EPITOME:
    Freeze the contract that removes caller-supplied operating contexts from
    LegalProductiveWorkReadService and replaces them with the certified durable
    CX27 operating-context hydrator.

SOVEREIGN READ CHAIN:
    caller-owned active transaction
        -> durable CX27 operating-context hydrator
        -> durable current assignments
        -> durable current supervision
        -> durable work items
        -> pure productive-work composer

AUTHORITY BOUNDARY:
    Hydrated operating context remains descriptive metadata only. It does not
    establish IAM, record/client/matter access, assignment, supervision,
    workflow, professional, financial, settlement, or execution authority.
"""

from __future__ import annotations

import inspect
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.legal_operations.service.legal_profile_productive_work_read_service import (
    LegalProductiveWorkReadService,
    LegalProductiveWorkReadServiceTransactionRequiredError,
)


NOW = datetime(
    2026,
    10,
    15,
    18,
    0,
    tzinfo=UTC,
)

TENANT = "tenant-a"
PRINCIPAL = "principal-a"


class _WorkItemRegistry:
    def __init__(self) -> None:
        self.get_calls: list[tuple[object, ...]] = []
        self.matter_calls: list[tuple[object, ...]] = []

    def get_by_id(
        self,
        tenant_id: str,
        work_item_id: str,
        *,
        session: object,
    ) -> Any:
        self.get_calls.append(
            (
                tenant_id,
                work_item_id,
                session,
            )
        )
        raise AssertionError(
            "NO_WORK_ITEM_READ_EXPECTED_FOR_EMPTY_CURRENT_WORK"
        )

    def list_matter(
        self,
        tenant_id: str,
        case_matter_id: str,
        *,
        session: object,
    ) -> tuple[Any, ...]:
        self.matter_calls.append(
            (
                tenant_id,
                case_matter_id,
                session,
            )
        )
        return ()


class _AssignmentRegistry:
    def __init__(self) -> None:
        self.calls: list[
            tuple[str, str, object]
        ] = []

    def list_current_for_assignee(
        self,
        tenant_id: str,
        principal_id: str,
        *,
        session: object,
    ) -> tuple[Any, ...]:
        self.calls.append(
            (
                tenant_id,
                principal_id,
                session,
            )
        )
        return ()


class _SupervisionRegistry:
    def __init__(self) -> None:
        self.calls: list[
            tuple[
                str,
                str,
                datetime,
                object,
            ]
        ] = []

    def list_current_for_supervisor(
        self,
        tenant_id: str,
        supervisor_principal_id: str,
        at: datetime,
        *,
        session: object,
    ) -> tuple[Any, ...]:
        self.calls.append(
            (
                tenant_id,
                supervisor_principal_id,
                at,
                session,
            )
        )
        return ()


class _OperatingContextHydrator:
    def __init__(self) -> None:
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
    ) -> tuple[Any, ...]:
        self.calls.append(
            (
                tenant_id,
                principal_id,
                at,
                session,
            )
        )
        return ()


def _service() -> tuple[
    LegalProductiveWorkReadService,
    _WorkItemRegistry,
    _AssignmentRegistry,
    _SupervisionRegistry,
    _OperatingContextHydrator,
]:
    work_items = _WorkItemRegistry()
    assignments = _AssignmentRegistry()
    supervision = _SupervisionRegistry()
    contexts = _OperatingContextHydrator()

    service = LegalProductiveWorkReadService(
        work_item_registry=work_items,
        assignment_registry=assignments,
        supervision_registry=supervision,
        operating_context_hydrator=contexts,
    )

    return (
        service,
        work_items,
        assignments,
        supervision,
        contexts,
    )


def _session(
    active: bool = True,
) -> object:
    return SimpleNamespace(
        in_transaction=active
    )


def test_constructor_owns_durable_operating_context_hydrator() -> None:
    signature = inspect.signature(
        LegalProductiveWorkReadService.__init__
    )

    assert (
        "operating_context_hydrator"
        in signature.parameters
    )


def test_project_has_no_caller_supplied_operating_contexts_parameter() -> None:
    signature = inspect.signature(
        LegalProductiveWorkReadService.project
    )

    assert (
        "operating_contexts"
        not in signature.parameters
    )


def test_project_hydrates_context_with_exact_scope_and_same_session() -> None:
    (
        service,
        _,
        assignments,
        supervision,
        contexts,
    ) = _service()

    session = _session()

    service.project(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        session=session,
    )

    assert contexts.calls == [
        (
            TENANT,
            PRINCIPAL,
            NOW,
            session,
        )
    ]

    assert assignments.calls == [
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


def test_inactive_transaction_rejects_before_hydrator_or_registry_reads() -> None:
    (
        service,
        _,
        assignments,
        supervision,
        contexts,
    ) = _service()

    with pytest.raises(
        LegalProductiveWorkReadServiceTransactionRequiredError,
    ):
        service.project(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            as_of=NOW,
            session=_session(False),
        )

    assert contexts.calls == []
    assert assignments.calls == []
    assert supervision.calls == []


def test_read_service_exposes_no_authority_or_mutation_surface() -> None:
    (
        service,
        _,
        _,
        _,
        _,
    ) = _service()

    for forbidden in (
        "authorize",
        "grant_permission",
        "grant_access",
        "assign",
        "supervise",
        "create_role",
        "bind_role",
        "pay",
        "invoice",
        "settle",
    ):
        assert not hasattr(
            service,
            forbidden,
        )


# SOVEREIGN SEPARATION:
# durable operating context != IAM
# durable operating context != access authority
# durable operating context != assignment/supervision authority
# read projection != financial or execution authority
