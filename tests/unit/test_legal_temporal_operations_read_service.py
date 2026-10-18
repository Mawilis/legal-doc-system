"""
P4-P1 Legal Temporal Operations read-service certificate.

TITLE:
    WILSY OS Legal Temporal Operations Read Service Certificate

AUTHORITY:
    Read-only orchestration over already-visible Productive Work matters.

ABSOLUTE BOUNDARY:
    - Productive Work remains the visibility ceiling.
    - The service creates no matter visibility.
    - The service performs no tenant-wide deadline scan.
    - Each distinct visible matter is read exactly once.
    - The caller owns the active transaction.
    - The exact caller session is reused for every deadline read.
    - Deadline persistence/service failures fail closed.
    - Final scope admission remains owned by the pure P4-P0 composer.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_matter_deadline import (
    LegalMatterDeadline,
)
from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkProjection,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)
from tools.eos.legal_operations.service.legal_temporal_operations_read_service import (
    LegalTemporalOperationsReadService,
    LegalTemporalOperationsReadServiceError,
    LegalTemporalOperationsReadServiceTransactionRequiredError,
)


NOW = datetime(
    2026,
    10,
    18,
    15,
    0,
    tzinfo=timezone.utc,
)


class _Session:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.active = active

    def in_transaction(self) -> bool:
        return self.active


class _DeadlineReader:
    def __init__(
        self,
        values: dict[
            str,
            tuple[LegalMatterDeadline, ...],
        ],
        *,
        failure: Exception | None = None,
    ) -> None:
        self.values = values
        self.failure = failure
        self.calls: list[
            tuple[str, str, object, object]
        ] = []

    def list_matter_deadlines(
        self,
        *,
        tenant_id: str,
        case_matter_id: str,
        deadline_collection: object,
        session: object,
    ) -> tuple[LegalMatterDeadline, ...]:
        self.calls.append(
            (
                tenant_id,
                case_matter_id,
                deadline_collection,
                session,
            )
        )

        if self.failure is not None:
            raise self.failure

        return self.values.get(
            case_matter_id,
            (),
        )


def _work(
    identity: str,
    matter: str,
) -> LegalWorkItem:
    return LegalWorkItem(
        work_item_id=identity,
        tenant_id="tenant-a",
        case_matter_id=matter,
        title=identity,
        source_kind="LEGAL_WORKFLOW_STAGE",
        source_reference=f"stage:{identity}",
        source_evidence_fingerprint="1" * 128,
        status=LegalWorkItemStatus.OPEN,
        created_at=NOW,
        due_at=None,
    )


def _productive(
    *,
    assigned: tuple[LegalWorkItem, ...] = (),
    supervised: tuple[LegalWorkItem, ...] = (),
) -> LegalProductiveWorkProjection:
    return LegalProductiveWorkProjection(
        tenant_id="tenant-a",
        principal_id="principal-a",
        as_of=NOW,
        operating_contexts=(),
        capability_ids=(),
        assigned_work_items=assigned,
        supervised_work_items=supervised,
        overdue_work_items=(),
        due_soon_work_items=(),
    )


def _deadline(
    identity: str,
    matter: str,
    *,
    days: int,
) -> LegalMatterDeadline:
    return LegalMatterDeadline(
        tenant_id="tenant-a",
        case_matter_id=matter,
        deadline_id=identity,
        deadline_kind="FILING",
        title=identity,
        due_at=NOW + timedelta(days=days),
        source_type="COURT_ORDER",
        source_reference=f"evidence:{identity}",
        source_evidence_fingerprint="2" * 128,
        jurisdiction_reference="jurisdiction:za-high-court",
        created_at=NOW,
    )


def _service(
    reader: _DeadlineReader,
    collection: object,
) -> LegalTemporalOperationsReadService:
    return LegalTemporalOperationsReadService(
        deadline_collection=collection,
        deadline_reader=reader,
    )


def test_requires_caller_owned_active_transaction_before_any_read():
    collection = object()
    reader = _DeadlineReader(
        {
            "matter-a": (
                _deadline(
                    "deadline-a",
                    "matter-a",
                    days=1,
                ),
            )
        }
    )

    service = _service(
        reader,
        collection,
    )

    with pytest.raises(
        LegalTemporalOperationsReadServiceTransactionRequiredError,
        match="TEMPORAL_READ_TRANSACTION_REQUIRED",
    ):
        service.project(
            productive_work=_productive(
                assigned=(
                    _work(
                        "work-a",
                        "matter-a",
                    ),
                )
            ),
            session=_Session(False),
        )

    assert reader.calls == []


def test_reads_each_distinct_visible_matter_once_in_sorted_order_same_session():
    collection = object()
    session = _Session()

    reader = _DeadlineReader(
        {
            "matter-a": (
                _deadline(
                    "deadline-a",
                    "matter-a",
                    days=3,
                ),
            ),
            "matter-b": (
                _deadline(
                    "deadline-b",
                    "matter-b",
                    days=1,
                ),
            ),
        }
    )

    service = _service(
        reader,
        collection,
    )

    projection = service.project(
        productive_work=_productive(
            assigned=(
                _work(
                    "work-b",
                    "matter-b",
                ),
                _work(
                    "work-a1",
                    "matter-a",
                ),
                _work(
                    "work-a2",
                    "matter-a",
                ),
            ),
        ),
        session=session,
    )

    assert reader.calls == [
        (
            "tenant-a",
            "matter-a",
            collection,
            session,
        ),
        (
            "tenant-a",
            "matter-b",
            collection,
            session,
        ),
    ]

    assert projection.visible_matter_ids == (
        "matter-a",
        "matter-b",
    )

    assert [
        row.deadline_id
        for row in projection.rows
    ] == [
        "deadline-b",
        "deadline-a",
    ]


def test_supervised_productive_work_is_already_visible_and_admitted():
    collection = object()
    session = _Session()

    reader = _DeadlineReader(
        {
            "matter-supervised": (
                _deadline(
                    "deadline-supervised",
                    "matter-supervised",
                    days=1,
                ),
            )
        }
    )

    projection = _service(
        reader,
        collection,
    ).project(
        productive_work=_productive(
            supervised=(
                _work(
                    "work-supervised",
                    "matter-supervised",
                ),
            ),
        ),
        session=session,
    )

    assert projection.visible_matter_ids == (
        "matter-supervised",
    )

    assert (
        projection.rows[0].deadline_id
        == "deadline-supervised"
    )


def test_empty_productive_work_performs_zero_deadline_reads():
    collection = object()
    session = _Session()
    reader = _DeadlineReader({})

    projection = _service(
        reader,
        collection,
    ).project(
        productive_work=_productive(),
        session=session,
    )

    assert reader.calls == []
    assert projection.visible_matter_ids == ()
    assert projection.rows == ()


def test_deadline_reader_failure_fails_closed():
    collection = object()
    session = _Session()

    reader = _DeadlineReader(
        {},
        failure=RuntimeError(
            "deadline store unavailable"
        ),
    )

    with pytest.raises(
        LegalTemporalOperationsReadServiceError,
        match="TEMPORAL_DEADLINE_READ_FAILED",
    ):
        _service(
            reader,
            collection,
        ).project(
            productive_work=_productive(
                assigned=(
                    _work(
                        "work-a",
                        "matter-a",
                    ),
                )
            ),
            session=session,
        )


def test_reader_cannot_expand_visibility_with_foreign_matter_deadline():
    collection = object()
    session = _Session()

    reader = _DeadlineReader(
        {
            "matter-visible": (
                _deadline(
                    "deadline-visible",
                    "matter-visible",
                    days=1,
                ),
                _deadline(
                    "deadline-secret",
                    "matter-secret",
                    days=2,
                ),
            )
        }
    )

    with pytest.raises(
        LegalTemporalOperationsReadServiceError,
        match="TEMPORAL_PROJECTION_FAILED",
    ):
        _service(
            reader,
            collection,
        ).project(
            productive_work=_productive(
                assigned=(
                    _work(
                        "work-visible",
                        "matter-visible",
                    ),
                )
            ),
            session=session,
        )


def test_read_service_exposes_no_write_or_authority_methods():
    public = {
        name
        for name in dir(
            LegalTemporalOperationsReadService
        )
        if not name.startswith("_")
    }

    assert public == {
        "project",
    }


# AUTHORITY BOUNDARY:
# Read-only composition.
# No IAM, assignment, supervision, visibility grant,
# deadline persistence, legal-period calculation,
# court/hearing, AI, billing, payment or settlement authority.
