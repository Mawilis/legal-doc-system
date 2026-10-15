"""
TITLE: WILSY OS Legal Work Supervision Binding Registry Unit Certificate

VERSION: v1.0.0-SV-P1-RED-LEGAL-WORK-SUPERVISION-BINDING-REGISTRY

EPITOME:
    Freeze append-only durability and effective-currentness semantics for
    immutable LegalWorkSupervisionBinding values.

AUTHORITY BOUNDARY:
    Persistence/currentness only. Supervision is not IAM, assignment,
    professional authority, approval execution, workflow transition,
    billing, payment or settlement authority.

CURRENTNESS:
    Derived from immutable successor chains plus effective dating.
    Multiple independent active supervision chains are permitted.

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

from tools.eos.legal_operations.domain.legal_work_supervision_binding import (
    LegalSupervisionControlLevel,
    LegalSupervisionScope,
    LegalWorkSupervisionBinding,
)
from tools.eos.legal_operations.registry.legal_work_supervision_binding_registry import (
    BINDING_IDENTITY_INDEX_NAME,
    PREDECESSOR_INDEX_NAME,
    SUPERVISEE_INDEX_NAME,
    SUPERVISOR_INDEX_NAME,
    WORK_SCOPE_INDEX_NAME,
    LegalWorkSupervisionBindingRegistry,
    RegistryConflictError,
    RegistryNotFoundError,
    RegistryPersistedRecordInvalidError,
    RegistryTransactionRequiredError,
)


NOW = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)
TENANT = "tenant-a"
MATTER = "matter-a"
WORK = "work-a"
SUPERVISOR = "principal-supervisor"
SUPERVISEE = "principal-supervisee"


class _Cursor:
    def __init__(
        self,
        rows: list[dict[str, object]],
    ) -> None:
        self._rows = list(rows)

    def sort(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> "_Cursor":
        return self

    def __iter__(self):
        return iter(self._rows)


class _Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[
            tuple[object, dict[str, object]]
        ] = []

    def create_index(
        self,
        keys: object,
        **kwargs: object,
    ) -> str:
        self.indexes.append(
            (
                keys,
                dict(kwargs),
            )
        )
        return str(
            kwargs.get("name", "")
        )

    @staticmethod
    def _matches(
        row: dict[str, object],
        query: dict[str, object],
    ) -> bool:
        return all(
            row.get(key) == value
            for key, value in query.items()
        )

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        matches = [
            row
            for row in self.rows
            if self._matches(
                row,
                query,
            )
        ]

        if not matches:
            return None

        return dict(
            matches[0]
        )

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
                if self._matches(
                    row,
                    query,
                )
            ]
        )

    def insert_one(
        self,
        value: dict[str, object],
        *,
        session: object,
    ) -> object:
        self.rows.append(
            dict(value)
        )

        return SimpleNamespace(
            inserted_id=len(self.rows)
        )


def _session(
    active: bool = True,
) -> object:
    return SimpleNamespace(
        in_transaction=active
    )


def _binding(
    binding_id: str,
    *,
    supervisor: str = SUPERVISOR,
    supervisee: str = SUPERVISEE,
    tenant_id: str = TENANT,
    matter_id: str = MATTER,
    scope: LegalSupervisionScope = (
        LegalSupervisionScope.WORK_ITEM
    ),
    work_item_id: str | None = WORK,
    control_level: LegalSupervisionControlLevel = (
        LegalSupervisionControlLevel.REVIEW_REQUIRED
    ),
    effective_from: datetime = NOW,
    effective_until: datetime | None = None,
    supersedes: str | None = None,
) -> LegalWorkSupervisionBinding:
    return LegalWorkSupervisionBinding(
        supervision_binding_id=binding_id,
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        scope=scope,
        work_item_id=work_item_id,
        supervisee_principal_id=supervisee,
        supervisor_principal_id=supervisor,
        control_level=control_level,
        supervision_plan_reference="plan:legal-supervision",
        supervision_basis_reference="basis:engagement",
        effective_from=effective_from,
        effective_until=effective_until,
        supersedes_supervision_binding_id=supersedes,
    )


def test_indexes_are_non_ttl_and_freeze_required_queries() -> None:
    collection = _Collection()

    registry = LegalWorkSupervisionBindingRegistry(
        collection
    )

    registry.ensure_indexes()

    names = {
        str(options.get("name"))
        for _, options in collection.indexes
    }

    assert {
        BINDING_IDENTITY_INDEX_NAME,
        PREDECESSOR_INDEX_NAME,
        SUPERVISOR_INDEX_NAME,
        SUPERVISEE_INDEX_NAME,
        WORK_SCOPE_INDEX_NAME,
    } <= names

    assert all(
        "expireAfterSeconds" not in options
        for _, options in collection.indexes
    )


def test_active_transaction_required_for_read_and_write() -> None:
    registry = LegalWorkSupervisionBindingRegistry(
        _Collection()
    )

    with pytest.raises(
        RegistryTransactionRequiredError,
        match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
    ):
        registry.persist(
            _binding("supervision-a"),
            session=_session(False),
        )

    with pytest.raises(
        RegistryTransactionRequiredError,
        match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
    ):
        registry.list_current_for_supervisor(
            TENANT,
            SUPERVISOR,
            NOW,
            session=_session(False),
        )


def test_initial_binding_and_exact_replay_are_idempotent() -> None:
    collection = _Collection()

    registry = LegalWorkSupervisionBindingRegistry(
        collection
    )

    value = _binding(
        "supervision-a"
    )

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


def test_same_binding_identity_divergence_rejected() -> None:
    registry = LegalWorkSupervisionBindingRegistry(
        _Collection()
    )

    registry.persist(
        _binding(
            "supervision-a",
            control_level=(
                LegalSupervisionControlLevel.OVERSIGHT
            ),
        ),
        session=_session(),
    )

    with pytest.raises(
        RegistryConflictError,
        match="DIVERGENT_REPLAY",
    ):
        registry.persist(
            _binding(
                "supervision-a",
                control_level=(
                    LegalSupervisionControlLevel.REVIEW_REQUIRED
                ),
            ),
            session=_session(),
        )


def test_successor_must_reference_existing_current_leaf() -> None:
    registry = LegalWorkSupervisionBindingRegistry(
        _Collection()
    )

    first = registry.persist(
        _binding(
            "supervision-a",
            control_level=(
                LegalSupervisionControlLevel.OVERSIGHT
            ),
        ),
        session=_session(),
    )

    second = registry.persist(
        _binding(
            "supervision-b",
            control_level=(
                LegalSupervisionControlLevel.REVIEW_REQUIRED
            ),
            effective_from=NOW + timedelta(hours=1),
            supersedes=first.supervision_binding_id,
        ),
        session=_session(),
    )

    assert (
        second.supersedes_supervision_binding_id
        == first.supervision_binding_id
    )

    with pytest.raises(
        RegistryConflictError,
        match="STALE_PREDECESSOR",
    ):
        registry.persist(
            _binding(
                "supervision-c",
                control_level=(
                    LegalSupervisionControlLevel.PRIOR_APPROVAL_REQUIRED
                ),
                effective_from=NOW + timedelta(hours=2),
                supersedes=first.supervision_binding_id,
            ),
            session=_session(),
        )


def test_successor_effective_time_must_move_forward() -> None:
    registry = LegalWorkSupervisionBindingRegistry(
        _Collection()
    )

    first = registry.persist(
        _binding(
            "supervision-a",
        ),
        session=_session(),
    )

    with pytest.raises(
        RegistryConflictError,
        match="EFFECTIVE_FROM_NOT_INCREASING",
    ):
        registry.persist(
            _binding(
                "supervision-b",
                effective_from=NOW,
                supersedes=first.supervision_binding_id,
            ),
            session=_session(),
        )


def test_successor_must_preserve_supervision_relationship_scope() -> None:
    registry = LegalWorkSupervisionBindingRegistry(
        _Collection()
    )

    first = registry.persist(
        _binding(
            "supervision-a",
        ),
        session=_session(),
    )

    with pytest.raises(
        RegistryConflictError,
        match="LINEAGE_SCOPE_MISMATCH",
    ):
        registry.persist(
            _binding(
                "supervision-b",
                supervisee="different-supervisee",
                effective_from=NOW + timedelta(hours=1),
                supersedes=first.supervision_binding_id,
            ),
            session=_session(),
        )


def test_multiple_independent_supervision_chains_may_coexist() -> None:
    registry = LegalWorkSupervisionBindingRegistry(
        _Collection()
    )

    first = registry.persist(
        _binding(
            "supervision-a",
        ),
        session=_session(),
    )

    second = registry.persist(
        _binding(
            "supervision-independent",
            supervisee="principal-other",
            work_item_id="work-b",
        ),
        session=_session(),
    )

    current = registry.list_current_for_supervisor(
        TENANT,
        SUPERVISOR,
        NOW,
        session=_session(),
    )

    assert tuple(
        value.supervision_binding_id
        for value in current
    ) == (
        first.supervision_binding_id,
        second.supervision_binding_id,
    )


def test_currentness_is_derived_from_leaf_and_effective_dates() -> None:
    registry = LegalWorkSupervisionBindingRegistry(
        _Collection()
    )

    first = registry.persist(
        _binding(
            "supervision-a",
            control_level=(
                LegalSupervisionControlLevel.OVERSIGHT
            ),
        ),
        session=_session(),
    )

    future = registry.persist(
        _binding(
            "supervision-b",
            control_level=(
                LegalSupervisionControlLevel.REVIEW_REQUIRED
            ),
            effective_from=NOW + timedelta(hours=1),
            supersedes=first.supervision_binding_id,
        ),
        session=_session(),
    )

    before = registry.list_current_for_supervisee(
        TENANT,
        SUPERVISEE,
        NOW + timedelta(minutes=30),
        session=_session(),
    )

    after = registry.list_current_for_supervisee(
        TENANT,
        SUPERVISEE,
        NOW + timedelta(hours=2),
        session=_session(),
    )

    assert before == (first,)
    assert after == (future,)


def test_expired_leaf_is_not_current() -> None:
    registry = LegalWorkSupervisionBindingRegistry(
        _Collection()
    )

    registry.persist(
        _binding(
            "supervision-expiring",
            effective_until=NOW + timedelta(hours=1),
        ),
        session=_session(),
    )

    assert (
        registry.list_current_for_supervisor(
            TENANT,
            SUPERVISOR,
            NOW + timedelta(minutes=30),
            session=_session(),
        )
    )

    assert (
        registry.list_current_for_supervisor(
            TENANT,
            SUPERVISOR,
            NOW + timedelta(hours=2),
            session=_session(),
        )
        == ()
    )


def test_work_item_scope_query_returns_only_effective_current_bindings() -> None:
    registry = LegalWorkSupervisionBindingRegistry(
        _Collection()
    )

    current = registry.persist(
        _binding(
            "supervision-work-a",
            work_item_id="work-a",
        ),
        session=_session(),
    )

    registry.persist(
        _binding(
            "supervision-work-b",
            work_item_id="work-b",
        ),
        session=_session(),
    )

    result = registry.list_current_for_work_item(
        TENANT,
        MATTER,
        "work-a",
        NOW,
        session=_session(),
    )

    assert result == (current,)


def test_matter_scope_query_returns_only_matter_scoped_bindings() -> None:
    registry = LegalWorkSupervisionBindingRegistry(
        _Collection()
    )

    matter_binding = registry.persist(
        _binding(
            "supervision-matter",
            scope=LegalSupervisionScope.MATTER,
            work_item_id=None,
        ),
        session=_session(),
    )

    registry.persist(
        _binding(
            "supervision-work",
            scope=LegalSupervisionScope.WORK_ITEM,
            work_item_id="work-a",
        ),
        session=_session(),
    )

    result = registry.list_current_for_matter(
        TENANT,
        MATTER,
        NOW,
        session=_session(),
    )

    assert result == (matter_binding,)


def test_foreign_tenant_is_indistinguishable_from_absence() -> None:
    registry = LegalWorkSupervisionBindingRegistry(
        _Collection()
    )

    registry.persist(
        _binding(
            "supervision-a",
        ),
        session=_session(),
    )

    assert (
        registry.list_current_for_supervisor(
            "tenant-b",
            SUPERVISOR,
            NOW,
            session=_session(),
        )
        == ()
    )

    with pytest.raises(
        RegistryNotFoundError,
        match="BINDING_NOT_FOUND",
    ):
        registry.get_by_binding_id(
            "tenant-b",
            "supervision-a",
            session=_session(),
        )


def test_corrupt_branching_history_rejected() -> None:
    collection = _Collection()

    registry = LegalWorkSupervisionBindingRegistry(
        collection
    )

    first = _binding(
        "supervision-a",
    )

    second = _binding(
        "supervision-b",
        effective_from=NOW + timedelta(hours=1),
        supersedes="supervision-a",
    )

    branch = _binding(
        "supervision-c",
        effective_from=NOW + timedelta(hours=2),
        supersedes="supervision-a",
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
        registry.list_current_for_supervisor(
            TENANT,
            SUPERVISOR,
            NOW + timedelta(hours=3),
            session=_session(),
        )


def test_corrupt_cross_scope_successor_rejected() -> None:
    collection = _Collection()

    registry = LegalWorkSupervisionBindingRegistry(
        collection
    )

    first = _binding(
        "supervision-a",
    )

    second = _binding(
        "supervision-b",
        supervisee="different-supervisee",
        effective_from=NOW + timedelta(hours=1),
        supersedes="supervision-a",
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
        registry.list_current_for_supervisor(
            TENANT,
            SUPERVISOR,
            NOW + timedelta(hours=2),
            session=_session(),
        )


def test_registry_exposes_no_iam_assignment_or_financial_authority() -> None:
    registry = LegalWorkSupervisionBindingRegistry(
        _Collection()
    )

    for forbidden in (
        "authorize",
        "assign",
        "update",
        "replace",
        "delete",
        "pay",
        "settle",
        "invoice",
    ):
        assert not hasattr(
            registry,
            forbidden,
        )


# AUTHORITY BOUNDARY:
# append-only supervision persistence/currentness only.
# No IAM, assignment, approval execution or financial execution authority.
