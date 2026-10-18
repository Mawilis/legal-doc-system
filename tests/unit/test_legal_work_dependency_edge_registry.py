"""
WILSY OS — P14-R9 Work Dependency Edge Registry Unit Certificate

VERSION: v1.0.0-P14-R9-WORK-DEPENDENCY-EDGE-REGISTRY-UNIT

PURPOSE:
    Certify immutable tenant-scoped persistence of runtime work dependency
    edges without introducing satisfaction, completion, mutable blocked state,
    assignment, supervision, IAM, notification, AI or financial authority.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_work_dependency_edge import (
    LegalWorkDependencyEdge,
)
from tools.eos.legal_operations.registry.legal_work_dependency_edge_registry import (
    COLLECTION_NAME,
    LegalWorkDependencyEdgeRegistry,
    LegalWorkDependencyEdgeRegistryConflictError,
    LegalWorkDependencyEdgeRegistryNotFoundError,
    LegalWorkDependencyEdgeRegistryPersistedRecordInvalidError,
    LegalWorkDependencyEdgeRegistryTransactionRequiredError,
)


FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128
FP_D = "d" * 128
FP_E = "e" * 128


class _Result:
    inserted_id = "fake"


class _Session:
    in_transaction = True


class _NoTransaction:
    in_transaction = False


class _Cursor:
    def __init__(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        self._rows = rows

    def __iter__(
        self,
    ):
        return iter(
            self._rows
        )

    def sort(
        self,
        keys: Any,
    ) -> "_Cursor":
        result = list(
            self._rows
        )

        for name, direction in reversed(
            keys
        ):
            result.sort(
                key=lambda row: row[name],
                reverse=direction < 0,
            )

        return _Cursor(
            result
        )



class _Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[tuple[Any, bool, str]] = []

    def create_index(
        self,
        keys: Any,
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.indexes.append(
            (
                tuple(keys),
                unique,
                name,
            )
        )
        return name

    def find_one(
        self,
        query: dict[str, Any],
        *,
        session: object,
    ) -> dict[str, Any] | None:
        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value in query.items()
            ):
                return deepcopy(row)

        return None

    def insert_one(
        self,
        value: dict[str, Any],
        *,
        session: object,
    ) -> _Result:
        row = deepcopy(value)
        row["_id"] = f"id-{len(self.rows) + 1}"
        self.rows.append(row)
        return _Result()

    def find(
        self,
        query: dict[str, Any],
        *,
        session: object,
    ) -> _Cursor:
        return _Cursor(
            [
                deepcopy(row)
                for row in self.rows
                if all(
                    row.get(key) == value
                    for key, value in query.items()
                )
            ]
        )


def _edge(
    *,
    tenant: str = "tenant-law",
    matter: str = "matter-1",
    receipt_id: str = FP_A,
    receipt_fingerprint: str = FP_B,
    predecessor_id: str = "work-a",
    predecessor_fingerprint: str = FP_C,
    successor_id: str = "work-b",
    successor_fingerprint: str = FP_D,
) -> LegalWorkDependencyEdge:
    return LegalWorkDependencyEdge(
        tenant_id=tenant,
        case_matter_id=matter,
        source_materialization_receipt_id=receipt_id,
        source_materialization_receipt_fingerprint=receipt_fingerprint,
        predecessor_work_item_id=predecessor_id,
        predecessor_work_item_fingerprint=predecessor_fingerprint,
        successor_work_item_id=successor_id,
        successor_work_item_fingerprint=successor_fingerprint,
    )


def test_collection_name_is_exact() -> None:
    assert COLLECTION_NAME == "legal_work_dependency_edges"


def test_indexes_are_tenant_first_immutable_unique_and_non_ttl() -> None:
    collection = _Collection()
    registry = LegalWorkDependencyEdgeRegistry(
        collection
    )

    registry.ensure_indexes()

    by_name = {
        name: (keys, unique)
        for keys, unique, name in collection.indexes
    }

    assert by_name[
        "legal_work_dependency_edge_identity_unique"
    ] == (
        (
            ("tenant_id", 1),
            ("dependency_edge_id", 1),
        ),
        True,
    )

    assert by_name[
        "legal_work_dependency_edge_relation_unique"
    ] == (
        (
            ("tenant_id", 1),
            ("source_materialization_receipt_id", 1),
            ("predecessor_work_item_id", 1),
            ("successor_work_item_id", 1),
        ),
        True,
    )

    assert by_name[
        "legal_work_dependency_edge_fingerprint_unique"
    ] == (
        (
            ("tenant_id", 1),
            ("fingerprint", 1),
        ),
        True,
    )

    assert all(
        "ttl" not in name.casefold()
        for name in by_name
    )


def test_active_caller_transaction_is_required() -> None:
    registry = LegalWorkDependencyEdgeRegistry(
        _Collection()
    )

    with pytest.raises(
        LegalWorkDependencyEdgeRegistryTransactionRequiredError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            _edge(),
            session=_NoTransaction(),
        )


def test_create_and_exact_replay_return_same_truth() -> None:
    collection = _Collection()
    registry = LegalWorkDependencyEdgeRegistry(
        collection
    )
    session = _Session()

    value = _edge()

    first = registry.create_or_replay(
        value,
        session=session,
    )
    replay = registry.create_or_replay(
        value,
        session=session,
    )

    assert first == value
    assert replay == value
    assert len(collection.rows) == 1


def test_same_runtime_relation_cannot_be_rebound_to_new_fingerprint_truth() -> None:
    collection = _Collection()
    registry = LegalWorkDependencyEdgeRegistry(
        collection
    )
    session = _Session()

    original = _edge()

    registry.create_or_replay(
        original,
        session=session,
    )

    divergent = _edge(
        predecessor_fingerprint=FP_E,
    )

    with pytest.raises(
        LegalWorkDependencyEdgeRegistryConflictError,
        match="DIVERGENT_RELATION_REPLAY",
    ):
        registry.create_or_replay(
            divergent,
            session=session,
        )

    assert len(collection.rows) == 1


def test_get_by_id_is_exact_and_tenant_scoped() -> None:
    collection = _Collection()
    registry = LegalWorkDependencyEdgeRegistry(
        collection
    )
    session = _Session()
    value = _edge()

    registry.create_or_replay(
        value,
        session=session,
    )

    assert registry.get_by_id(
        "tenant-law",
        value.dependency_edge_id,
        session=session,
    ) == value

    with pytest.raises(
        LegalWorkDependencyEdgeRegistryNotFoundError,
    ):
        registry.get_by_id(
            "tenant-other",
            value.dependency_edge_id,
            session=session,
        )


def test_receipt_predecessor_and_successor_queries_are_exact() -> None:
    collection = _Collection()
    registry = LegalWorkDependencyEdgeRegistry(
        collection
    )
    session = _Session()

    first = _edge(
        predecessor_id="work-a",
        successor_id="work-b",
    )
    second = _edge(
        predecessor_id="work-b",
        predecessor_fingerprint=FP_D,
        successor_id="work-c",
        successor_fingerprint=FP_E,
    )

    for value in (
        first,
        second,
    ):
        registry.create_or_replay(
            value,
            session=session,
        )

    assert registry.list_by_receipt(
        "tenant-law",
        FP_A,
        session=session,
    ) == (
        first,
        second,
    )

    assert registry.list_predecessors(
        "tenant-law",
        "work-c",
        session=session,
    ) == (
        second,
    )

    assert registry.list_successors(
        "tenant-law",
        "work-a",
        session=session,
    ) == (
        first,
    )


def test_cross_tenant_same_relation_is_isolated() -> None:
    collection = _Collection()
    registry = LegalWorkDependencyEdgeRegistry(
        collection
    )
    session = _Session()

    left = _edge(
        tenant="tenant-left",
    )
    right = _edge(
        tenant="tenant-right",
    )

    registry.create_or_replay(
        left,
        session=session,
    )
    registry.create_or_replay(
        right,
        session=session,
    )

    assert registry.list_by_receipt(
        "tenant-left",
        FP_A,
        session=session,
    ) == (
        left,
    )

    assert registry.list_by_receipt(
        "tenant-right",
        FP_A,
        session=session,
    ) == (
        right,
    )


def test_persisted_corruption_and_extra_field_reject_strictly() -> None:
    collection = _Collection()
    registry = LegalWorkDependencyEdgeRegistry(
        collection
    )
    session = _Session()

    value = _edge()

    registry.create_or_replay(
        value,
        session=session,
    )

    pristine = deepcopy(
        collection.rows[0]
    )

    collection.rows[0][
        "fingerprint"
    ] = FP_E

    with pytest.raises(
        LegalWorkDependencyEdgeRegistryPersistedRecordInvalidError,
    ):
        registry.get_by_id(
            value.tenant_id,
            value.dependency_edge_id,
            session=session,
        )

    collection.rows[0] = deepcopy(
        pristine
    )
    collection.rows[0][
        "blocked"
    ] = True

    with pytest.raises(
        LegalWorkDependencyEdgeRegistryPersistedRecordInvalidError,
    ):
        registry.get_by_id(
            value.tenant_id,
            value.dependency_edge_id,
            session=session,
        )


def test_registry_exposes_no_mutable_or_authority_surfaces() -> None:
    forbidden = {
        "update",
        "replace",
        "delete",
        "set_current",
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
            LegalWorkDependencyEdgeRegistry
        )
        if not name.startswith("_")
    }

    assert public.isdisjoint(
        forbidden
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_dependency_edge_registry.py
# VERSION: v1.0.0-P14-R9-WORK-DEPENDENCY-EDGE-REGISTRY-UNIT
# IMMUTABLE EDGE DURABILITY: REQUIRED
# EXACT REPLAY: REQUIRED
# SAME RELATION DIVERGENCE: FAIL CLOSED
# TENANT ISOLATION: REQUIRED
# TTL: FORBIDDEN
# MUTABLE CURRENT POINTER: FORBIDDEN
# SATISFACTION / COMPLETION AUTHORITY: NONE
# ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# NOTIFICATION / AI / FINANCIAL AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
