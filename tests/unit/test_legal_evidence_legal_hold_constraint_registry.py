"""Direct certificate for the C4D4B durable legal-hold constraint registry.

TITLE: Legal Evidence Legal Hold Constraint Registry Direct Certificate
VERSION: v1.0.0-L10A2R-C4D4B-R4-LEGAL-HOLD-REGISTRY-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Certify append-only exact legal-hold fact replay and bounded immutable
         history without granting current-state, issuance, release, retention,
         orphan, deletion, provider-mutation or transaction-lifecycle authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_evidence_legal_hold_constraint_registry.py
COLLABORATION / OWNERSHIP:
    Test-only certificate for the frozen C4D4B-R3 production registry.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.0 establishes direct certification of collection/index identity,
    caller-owned transactions, exact replay, append-only ACTIVE/RELEASED
    history, tenant isolation, deterministic bounded history, chronology and
    corruption rejection, duplicate-key retry semantics and authority absence.
COMPLIANCE:
    Direct in-process certification only; real Mongo durability remains R5.
SECURITY / PRIVACY POSTURE:
    Synthetic opaque evidence only.
TENANT BOUNDARY:
    All persistence and reads are exact tenant scoped.
AUTHORITY BOUNDARY:
    Tests durable persistence/history semantics only.
FINANCIAL AUTHORITY BOUNDARY:
    No financial authority; Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_evidence_legal_hold_constraint import (
    LegalEvidenceLegalHoldConstraint,
    LegalEvidenceLegalHoldState,
)
from tools.eos.legal_operations.registry.legal_evidence_legal_hold_constraint_registry import (
    COLLECTION,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_HOLD_HISTORY,
    INDEX_TENANT_HOLD_STATE_HISTORY,
    INDEX_TENANT_PROVIDER_OBJECT_HISTORY,
    LegalEvidenceLegalHoldConstraintConflictError,
    LegalEvidenceLegalHoldConstraintNotFoundError,
    LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
    LegalEvidenceLegalHoldConstraintRegistry,
    LegalEvidenceLegalHoldConstraintTransactionRequiredError,
)


BASE = datetime(
    2026,
    10,
    1,
    12,
    0,
    tzinfo=timezone.utc,
)


class _Session:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


class _InsertResult:
    acknowledged = True


def _matches(
    row: dict[str, object],
    query: dict[str, object],
) -> bool:
    return all(
        row.get(key) == value
        for key, value in query.items()
    )


class _Cursor:
    def __init__(
        self,
        rows: list[dict[str, object]],
    ) -> None:
        self._rows = [
            deepcopy(row)
            for row in rows
        ]

    def sort(
        self,
        spec: list[tuple[str, int]],
    ) -> "_Cursor":
        rows = self._rows

        for key, direction in reversed(spec):
            def _sort_key(
                row: dict[str, object],
            ) -> str:
                value = row.get(
                    key
                )

                if not isinstance(
                    value,
                    str,
                ):
                    raise TypeError(
                        "synthetic cursor sort key must be text"
                    )

                return value

            rows.sort(
                key=_sort_key,
                reverse=direction < 0,
            )

        return self

    def limit(
        self,
        limit: int,
    ) -> "_Cursor":
        self._rows = self._rows[:limit]
        return self

    def __iter__(
        self,
    ) -> Any:
        return iter(
            deepcopy(self._rows)
        )


class _Collection:
    def __init__(
        self,
    ) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[
            tuple[
                list[tuple[str, int]],
                bool,
                str,
            ]
        ] = []
        self.raise_duplicate = False

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.indexes.append(
            (
                list(keys),
                unique,
                name,
            )
        )
        return name

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        del session

        for row in self.rows:
            if _matches(
                row,
                query,
            ):
                return deepcopy(
                    row
                )

        return None

    def find(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> _Cursor:
        del session

        return _Cursor(
            [
                row
                for row in self.rows
                if _matches(
                    row,
                    query,
                )
            ]
        )

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object,
    ) -> _InsertResult:
        del session

        if self.raise_duplicate:
            raise DuplicateKeyError(
                "synthetic duplicate"
            )

        self.rows.append(
            deepcopy(
                document
            )
        )

        return _InsertResult()


def _fact(
    *,
    tenant: str = "tenant-alpha",
    hold: str = "hold-alpha",
    provider: str = "s3",
    storage: str = "bucket-alpha",
    version: str = "object-v1",
    state: LegalEvidenceLegalHoldState = (
        LegalEvidenceLegalHoldState.ACTIVE
    ),
    released_at: datetime | None = None,
    imposed_at: datetime = BASE,
    source_reference: str = "source-alpha",
    source_fingerprint: str = "a" * 128,
) -> LegalEvidenceLegalHoldConstraint:
    return LegalEvidenceLegalHoldConstraint(
        tenant_id=tenant,
        provider_name=provider,
        storage_reference=storage,
        object_version_reference=version,
        hold_reference=hold,
        source_evidence_reference=source_reference,
        source_evidence_fingerprint=source_fingerprint,
        imposed_at=imposed_at,
        state=state,
        released_at=released_at,
    )


def test_collection_and_indexes_are_exact_and_have_no_ttl() -> None:
    collection = _Collection()
    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )

    registry.ensure_indexes()

    assert COLLECTION == (
        "legal_evidence_legal_hold_constraints"
    )

    assert collection.indexes == [
        (
            [
                ("tenant_id", 1),
                ("fingerprint", 1),
            ],
            True,
            INDEX_TENANT_FINGERPRINT,
        ),
        (
            [
                ("tenant_id", 1),
                ("hold_reference", 1),
                ("imposed_at", -1),
            ],
            False,
            INDEX_TENANT_HOLD_HISTORY,
        ),
        (
            [
                ("tenant_id", 1),
                ("provider_name", 1),
                ("storage_reference", 1),
                ("object_version_reference", 1),
                ("imposed_at", -1),
            ],
            False,
            INDEX_TENANT_PROVIDER_OBJECT_HISTORY,
        ),
        (
            [
                ("tenant_id", 1),
                ("hold_reference", 1),
                ("state", 1),
                ("imposed_at", -1),
            ],
            False,
            INDEX_TENANT_HOLD_STATE_HISTORY,
        ),
    ]


def test_create_requires_active_caller_transaction() -> None:
    registry = LegalEvidenceLegalHoldConstraintRegistry(
        _Collection()
    )

    with pytest.raises(
        LegalEvidenceLegalHoldConstraintTransactionRequiredError
    ):
        registry.create_or_replay(
            _fact(),
            session=_Session(
                False
            ),
        )


def test_create_and_exact_fingerprint_replay_return_same_fact() -> None:
    collection = _Collection()
    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )
    session = _Session()
    value = _fact()

    created = registry.create_or_replay(
        value,
        session=session,
    )

    replayed = registry.create_or_replay(
        value,
        session=session,
    )

    assert created == value
    assert replayed == value
    assert len(collection.rows) == 1


def test_same_hold_active_and_released_are_append_only_distinct_facts() -> None:
    collection = _Collection()
    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )
    session = _Session()

    active = _fact()

    released = _fact(
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(
            days=7
        ),
    )

    registry.create_or_replay(
        active,
        session=session,
    )

    registry.create_or_replay(
        released,
        session=session,
    )

    assert active.hold_reference == released.hold_reference
    assert active.fingerprint != released.fingerprint
    assert len(collection.rows) == 2

    history = registry.list_hold_history(
        tenant_id=active.tenant_id,
        hold_reference=active.hold_reference,
        session=session,
    )

    assert set(history) == {
        active,
        released,
    }


def test_same_provider_object_allows_multiple_immutable_hold_facts() -> None:
    collection = _Collection()
    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )
    session = _Session()

    first = _fact(
        hold="hold-one",
    )

    second = _fact(
        hold="hold-two",
        source_reference="source-two",
        source_fingerprint="b" * 128,
    )

    registry.create_or_replay(
        first,
        session=session,
    )

    registry.create_or_replay(
        second,
        session=session,
    )

    history = registry.list_provider_object_history(
        tenant_id=first.tenant_id,
        provider_name=first.provider_name,
        storage_reference=first.storage_reference,
        object_version_reference=first.object_version_reference,
        session=session,
    )

    assert set(history) == {
        first,
        second,
    }


def test_history_order_is_deterministic_but_not_current_authority() -> None:
    collection = _Collection()
    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )
    session = _Session()

    older = _fact(
        hold="hold-history",
        imposed_at=BASE,
        source_reference="source-older",
        source_fingerprint="a" * 128,
    )

    newer = _fact(
        hold="hold-history",
        imposed_at=BASE + timedelta(
            days=1
        ),
        source_reference="source-newer",
        source_fingerprint="b" * 128,
    )

    registry.create_or_replay(
        older,
        session=session,
    )

    registry.create_or_replay(
        newer,
        session=session,
    )

    history = registry.list_hold_history(
        tenant_id=older.tenant_id,
        hold_reference=older.hold_reference,
        session=session,
    )

    assert history == (
        newer,
        older,
    )

    assert not hasattr(
        registry,
        "get_current",
    )
    assert not hasattr(
        registry,
        "resolve_current",
    )


def test_get_by_fingerprint_is_tenant_scoped() -> None:
    collection = _Collection()
    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )
    session = _Session()
    value = _fact()

    registry.create_or_replay(
        value,
        session=session,
    )

    assert (
        registry.get_by_fingerprint(
            tenant_id=value.tenant_id,
            fingerprint=value.fingerprint,
            session=session,
        )
        == value
    )

    with pytest.raises(
        LegalEvidenceLegalHoldConstraintNotFoundError
    ):
        registry.get_by_fingerprint(
            tenant_id="tenant-other",
            fingerprint=value.fingerprint,
            session=session,
        )


def test_cross_tenant_same_hold_and_provider_object_are_isolated() -> None:
    collection = _Collection()
    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )
    session = _Session()

    left = _fact(
        tenant="tenant-left",
    )

    right = _fact(
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

    left_history = registry.list_hold_history(
        tenant_id="tenant-left",
        hold_reference=left.hold_reference,
        session=session,
    )

    right_history = registry.list_hold_history(
        tenant_id="tenant-right",
        hold_reference=right.hold_reference,
        session=session,
    )

    assert left_history == (
        left,
    )
    assert right_history == (
        right,
    )


def test_durable_document_uses_state_text_and_aware_iso_chronology() -> None:
    collection = _Collection()
    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )
    session = _Session()

    released = _fact(
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(
            hours=3
        ),
    )

    registry.create_or_replay(
        released,
        session=session,
    )

    row = collection.rows[0]

    assert row["state"] == "RELEASED"
    assert row["imposed_at"] == BASE.isoformat()
    assert row["released_at"] == (
        BASE
        + timedelta(
            hours=3
        )
    ).isoformat()


@pytest.mark.parametrize(
    "field",
    [
        "imposed_at",
        "released_at",
    ],
)
def test_malformed_or_naive_persisted_chronology_rejects(
    field: str,
) -> None:
    collection = _Collection()
    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )
    session = _Session()

    value = _fact(
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(
            days=1
        ),
    )

    registry.create_or_replay(
        value,
        session=session,
    )

    collection.rows[0][field] = (
        "2026-10-01T12:00:00"
    )

    with pytest.raises(
        LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError
    ):
        registry.get_by_fingerprint(
            tenant_id=value.tenant_id,
            fingerprint=value.fingerprint,
            session=session,
        )


def test_corrupt_persisted_record_rejects_without_healing() -> None:
    collection = _Collection()
    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )
    session = _Session()
    value = _fact()

    registry.create_or_replay(
        value,
        session=session,
    )

    before = deepcopy(
        collection.rows[0]
    )

    collection.rows[0][
        "source_evidence_fingerprint"
    ] = "b" * 128

    corrupted = deepcopy(
        collection.rows[0]
    )

    with pytest.raises(
        LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError
    ):
        registry.get_by_fingerprint(
            tenant_id=value.tenant_id,
            fingerprint=value.fingerprint,
            session=session,
        )

    assert collection.rows[0] == corrupted
    assert collection.rows[0] != before


def test_post_construction_tampering_rejects_before_write() -> None:
    collection = _Collection()
    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )

    value = _fact()

    object.__setattr__(
        value,
        "provider_delete_authorized",
        True,
    )

    with pytest.raises(
        LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError
    ):
        registry.create_or_replay(
            value,
            session=_Session(),
        )

    assert collection.rows == []


def test_duplicate_key_requires_whole_transaction_retry() -> None:
    collection = _Collection()
    collection.raise_duplicate = True

    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )

    with pytest.raises(
        LegalEvidenceLegalHoldConstraintConflictError,
        match=(
            "L10A2R_C4D4B_R3_"
            "WHOLE_TRANSACTION_RETRY_REQUIRED"
        ),
    ):
        registry.create_or_replay(
            _fact(),
            session=_Session(),
        )


def test_registry_surface_has_no_later_authority_or_mutators() -> None:
    forbidden = {
        "get_current",
        "resolve_current",
        "set_current",
        "advance",
        "transition",
        "release",
        "activate",
        "update",
        "delete",
        "remove",
        "satisfy_retention",
        "prove_orphan",
        "authorize_delete",
    }

    public = {
        name
        for name in dir(
            LegalEvidenceLegalHoldConstraintRegistry
        )
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(
        public
    )

    assert public == {
        "create_or_replay",
        "ensure_indexes",
        "get_by_fingerprint",
        "list_hold_history",
        "list_provider_object_history",
    }


# ARTIFACT: test_legal_evidence_legal_hold_constraint_registry.py
# VERSION: v1.0.0-L10A2R-C4D4B-R4-LEGAL-HOLD-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct certificate for append-only C4D4B persistence/history
# TENANT POSTURE: tenant isolation and foreign absence are directly certified
# HISTORY POSTURE: same hold/provider object may retain multiple immutable facts
# CURRENT-STATE POSTURE: no latest/current authority is certified or inferred
# TRANSACTION POSTURE: caller-owned active transaction is mandatory
# TTL POSTURE: no TTL persistence behavior is accepted
# DELETION POSTURE: no deletion/provider mutation authority is accepted
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
