"""
TITLE: WILSY OS Legal Work Assignment Registry Unit Certificate

VERSION: v1.0.0-AS-P1-RED-LEGAL-WORK-ASSIGNMENT-REGISTRY

EPITOME:
    Freeze the durable append-only assignment contract that turns immutable
    LegalWorkAssignment values into deterministic current assignee truth
    without a mutable current pointer.

AUTHORITY BOUNDARY:
    Persistence/currentness only. This registry does not authorize assignment,
    IAM, workflow transition, professional authority, billing, payment,
    execution or settlement.

CURRENTNESS:
    Derived from one strict immutable successor chain per tenant/work item.
    No mutable current pointer.

TRANSACTION:
    Every read/write requires a caller-owned active Mongo transaction.

FINANCIAL POSTURE:
    NONE. Kennel EOS exclusively owns financial execution and settlement.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.registry.legal_work_assignment_registry import (
    ASSIGNEE_INDEX_NAME,
    ASSIGNMENT_IDENTITY_INDEX_NAME,
    COLLECTION_NAME,
    INITIAL_WORK_ITEM_INDEX_NAME,
    PREDECESSOR_INDEX_NAME,
    WORK_ITEM_HISTORY_INDEX_NAME,
    LegalWorkAssignmentRegistry,
    RegistryConflictError,
    RegistryNotFoundError,
    RegistryPersistedRecordInvalidError,
    RegistryTransactionRequiredError,
)


NOW = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)
TENANT = "tenant-a"
MATTER = "matter-a"
WORK = "work-a"


class _Cursor:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = list(rows)

    def sort(self, *args: Any, **kwargs: Any) -> "_Cursor":
        return self

    def __iter__(self):
        return iter(self._rows)


class _Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[object, dict[str, object]]] = []

    def create_index(self, keys: object, **kwargs: object) -> str:
        self.indexes.append((keys, dict(kwargs)))
        return str(kwargs.get("name", ""))

    @staticmethod
    def _matches(
        row: dict[str, object],
        query: dict[str, object],
    ) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        matches = [
            row
            for row in self.rows
            if self._matches(row, query)
        ]
        if not matches:
            return None
        return dict(matches[0])

    def find(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> _Cursor:
        return _Cursor(
            [
                dict(row)
                for row in self.rows
                if self._matches(row, query)
            ]
        )

    def insert_one(
        self,
        value: dict[str, object],
        *,
        session: object,
    ) -> object:
        self.rows.append(dict(value))
        return SimpleNamespace(inserted_id=len(self.rows))


def _session(active: bool = True) -> object:
    return SimpleNamespace(in_transaction=active)


def _assignment(
    assignment_id: str,
    assignee: str,
    *,
    assigned_at: datetime = NOW,
    supersedes: str | None = None,
    tenant_id: str = TENANT,
    matter_id: str = MATTER,
    work_item_id: str = WORK,
) -> LegalWorkAssignment:
    return LegalWorkAssignment(
        assignment_id=assignment_id,
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        work_item_id=work_item_id,
        assignee_principal_id=assignee,
        assigned_by_principal_id="principal-assigner",
        assigned_at=assigned_at,
        assignment_reason_reference="reason:staffing",
        authorization_evidence_reference="authz:assignment",
        supersedes_assignment_id=supersedes,
    )


def test_indexes_freeze_history_currentness_without_ttl() -> None:
    collection = _Collection()
    registry = LegalWorkAssignmentRegistry(collection)

    registry.ensure_indexes()

    names = {
        str(options.get("name"))
        for _, options in collection.indexes
    }

    assert {
        ASSIGNMENT_IDENTITY_INDEX_NAME,
        INITIAL_WORK_ITEM_INDEX_NAME,
        PREDECESSOR_INDEX_NAME,
        WORK_ITEM_HISTORY_INDEX_NAME,
        ASSIGNEE_INDEX_NAME,
    } <= names

    assert all(
        "expireAfterSeconds" not in options
        for _, options in collection.indexes
    )


def test_active_transaction_required_for_reads_and_writes() -> None:
    registry = LegalWorkAssignmentRegistry(_Collection())

    with pytest.raises(
        RegistryTransactionRequiredError,
        match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
    ):
        registry.persist(
            _assignment("assignment-a", "principal-a"),
            session=_session(False),
        )

    with pytest.raises(
        RegistryTransactionRequiredError,
        match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
    ):
        registry.resolve_current(
            TENANT,
            WORK,
            session=_session(False),
        )


def test_first_assignment_persists_and_exact_replay_returns_same_value() -> None:
    collection = _Collection()
    registry = LegalWorkAssignmentRegistry(collection)
    value = _assignment("assignment-a", "principal-a")

    first = registry.persist(
        value,
        session=_session(),
    )
    replay = registry.persist(
        value,
        session=_session(),
    )

    assert first == value
    assert replay == value
    assert len(collection.rows) == 1


def test_same_assignment_identity_divergence_rejected() -> None:
    registry = LegalWorkAssignmentRegistry(_Collection())

    registry.persist(
        _assignment("assignment-a", "principal-a"),
        session=_session(),
    )

    with pytest.raises(
        RegistryConflictError,
        match="DIVERGENT_REPLAY",
    ):
        registry.persist(
            _assignment("assignment-a", "principal-b"),
            session=_session(),
        )


def test_reassignment_requires_exact_current_predecessor() -> None:
    registry = LegalWorkAssignmentRegistry(_Collection())

    first = registry.persist(
        _assignment("assignment-a", "principal-a"),
        session=_session(),
    )

    second = registry.persist(
        _assignment(
            "assignment-b",
            "principal-b",
            assigned_at=NOW + timedelta(minutes=1),
            supersedes=first.assignment_id,
        ),
        session=_session(),
    )

    assert second.supersedes_assignment_id == first.assignment_id

    with pytest.raises(
        RegistryConflictError,
        match="STALE_PREDECESSOR",
    ):
        registry.persist(
            _assignment(
                "assignment-c",
                "principal-c",
                assigned_at=NOW + timedelta(minutes=2),
                supersedes=first.assignment_id,
            ),
            session=_session(),
        )


def test_reassignment_time_must_move_forward() -> None:
    registry = LegalWorkAssignmentRegistry(_Collection())

    first = registry.persist(
        _assignment("assignment-a", "principal-a"),
        session=_session(),
    )

    with pytest.raises(
        RegistryConflictError,
        match="ASSIGNED_AT_NOT_INCREASING",
    ):
        registry.persist(
            _assignment(
                "assignment-b",
                "principal-b",
                assigned_at=NOW,
                supersedes=first.assignment_id,
            ),
            session=_session(),
        )


def test_current_is_derived_from_strict_immutable_leaf() -> None:
    registry = LegalWorkAssignmentRegistry(_Collection())

    first = registry.persist(
        _assignment("assignment-a", "principal-a"),
        session=_session(),
    )

    second = registry.persist(
        _assignment(
            "assignment-b",
            "principal-b",
            assigned_at=NOW + timedelta(minutes=1),
            supersedes=first.assignment_id,
        ),
        session=_session(),
    )

    current = registry.resolve_current(
        TENANT,
        WORK,
        session=_session(),
    )

    assert current is not None
    assert current == second
    assert current.assignee_principal_id == "principal-b"


def test_history_is_complete_ordered_lineage() -> None:
    registry = LegalWorkAssignmentRegistry(_Collection())

    first = registry.persist(
        _assignment("assignment-a", "principal-a"),
        session=_session(),
    )

    second = registry.persist(
        _assignment(
            "assignment-b",
            "principal-b",
            assigned_at=NOW + timedelta(minutes=1),
            supersedes=first.assignment_id,
        ),
        session=_session(),
    )

    history = registry.get_history(
        TENANT,
        WORK,
        session=_session(),
    )

    assert history == (first, second)


def test_assignee_query_returns_only_current_assignments() -> None:
    registry = LegalWorkAssignmentRegistry(_Collection())

    first = registry.persist(
        _assignment("assignment-a", "principal-a"),
        session=_session(),
    )

    registry.persist(
        _assignment(
            "assignment-b",
            "principal-b",
            assigned_at=NOW + timedelta(minutes=1),
            supersedes=first.assignment_id,
        ),
        session=_session(),
    )

    current_a = registry.list_current_for_assignee(
        TENANT,
        "principal-a",
        session=_session(),
    )
    current_b = registry.list_current_for_assignee(
        TENANT,
        "principal-b",
        session=_session(),
    )

    assert current_a == ()
    assert tuple(
        item.assignment_id
        for item in current_b
    ) == ("assignment-b",)


def test_foreign_tenant_is_indistinguishable_from_absence() -> None:
    registry = LegalWorkAssignmentRegistry(_Collection())

    registry.persist(
        _assignment("assignment-a", "principal-a"),
        session=_session(),
    )

    assert (
        registry.resolve_current(
            "tenant-b",
            WORK,
            session=_session(),
        )
        is None
    )

    with pytest.raises(
        RegistryNotFoundError,
        match="HISTORY_NOT_FOUND",
    ):
        registry.get_history(
            "tenant-b",
            WORK,
            session=_session(),
        )


def test_corrupt_branching_history_rejected() -> None:
    collection = _Collection()
    registry = LegalWorkAssignmentRegistry(collection)

    first = _assignment(
        "assignment-a",
        "principal-a",
    )
    second = _assignment(
        "assignment-b",
        "principal-b",
        assigned_at=NOW + timedelta(minutes=1),
        supersedes="assignment-a",
    )
    branch = _assignment(
        "assignment-c",
        "principal-c",
        assigned_at=NOW + timedelta(minutes=2),
        supersedes="assignment-a",
    )

    collection.rows.extend(
        [
            first.to_dict(),
            second.to_dict(),
            branch.to_dict(),
        ]
    )

    with pytest.raises(
        RegistryPersistedRecordInvalidError,
        match="BRANCHED_HISTORY",
    ):
        registry.get_history(
            TENANT,
            WORK,
            session=_session(),
        )


def test_corrupt_cross_matter_lineage_rejected() -> None:
    collection = _Collection()
    registry = LegalWorkAssignmentRegistry(collection)

    first = _assignment(
        "assignment-a",
        "principal-a",
    )
    second = _assignment(
        "assignment-b",
        "principal-b",
        assigned_at=NOW + timedelta(minutes=1),
        supersedes="assignment-a",
        matter_id="matter-b",
    )

    collection.rows.extend(
        [
            first.to_dict(),
            second.to_dict(),
        ]
    )

    with pytest.raises(
        RegistryPersistedRecordInvalidError,
        match="LINEAGE_SCOPE_MISMATCH",
    ):
        registry.get_history(
            TENANT,
            WORK,
            session=_session(),
        )


def test_registry_has_no_mutation_or_financial_authority_surface() -> None:
    registry = LegalWorkAssignmentRegistry(_Collection())

    for forbidden in (
        "update",
        "replace",
        "delete",
        "authorize",
        "pay",
        "settle",
        "invoice",
    ):
        assert not hasattr(registry, forbidden)


# AUTHORITY BOUNDARY:
# append-only Legal work-assignment persistence/currentness only.
# No IAM, workflow-transition, billing, payment or settlement authority.
