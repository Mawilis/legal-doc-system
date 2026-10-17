"""
P14-R14 immutable Legal work completion-event registry certificate.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_work_completion_event import (
    LegalWorkCompletionEvent,
)
from tools.eos.legal_operations.registry.legal_work_completion_event_registry import (
    COLLECTION_NAME,
    LegalWorkCompletionEventRegistry,
    LegalWorkCompletionEventRegistryConflictError,
    LegalWorkCompletionEventRegistryPersistedRecordInvalidError,
    LegalWorkCompletionEventRegistryTransactionRequiredError,
)


AT = datetime(
    2026,
    10,
    16,
    19,
    0,
    tzinfo=timezone.utc,
)

ACTIVE = SimpleNamespace(
    in_transaction=True
)


def event(
    **overrides: object,
) -> LegalWorkCompletionEvent:
    values: dict[str, object] = {
        "tenant_id": "tenant-law",
        "case_matter_id": "matter-1",
        "work_item_id": "work-1",
        "work_item_fingerprint": "a" * 128,
        "completion_evidence_reference": "evidence:complete:1",
        "completion_evidence_fingerprint": "b" * 128,
        "completed_at": AT,
        "actor_principal_id": "principal-1",
        "authorization_evidence_reference": "iam:decision:1",
        "authorization_evidence_fingerprint": "c" * 128,
    }

    values.update(
        overrides
    )

    return LegalWorkCompletionEvent(
        **values  # type: ignore[arg-type]
    )


class _Cursor:
    def __init__(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        self._rows = rows

    def sort(
        self,
        keys: list[tuple[str, int]],
    ) -> "_Cursor":
        rows = list(
            self._rows
        )

        for name, direction in reversed(
            keys
        ):
            rows.sort(
                key=lambda row: row[name],
                reverse=direction < 0,
            )

        return _Cursor(
            rows
        )

    def __iter__(
        self,
    ):
        return iter(
            self._rows
        )


class _Collection:
    def __init__(self) -> None:
        self.rows: list[
            dict[str, Any]
        ] = []
        self.indexes: list[
            tuple[
                list[tuple[str, int]],
                bool,
                str | None,
                dict[str, Any],
            ]
        ] = []

    def create_index(
        self,
        keys,
        *,
        unique=False,
        name=None,
        **kwargs,
    ):
        self.indexes.append(
            (
                list(keys),
                unique,
                name,
                dict(kwargs),
            )
        )
        return name

    def find_one(
        self,
        query,
        *,
        session,
    ):
        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value
                in query.items()
            ):
                return dict(
                    row
                )

        return None

    def find(
        self,
        query,
        *,
        session,
    ):
        return _Cursor(
            [
                dict(row)
                for row in self.rows
                if all(
                    row.get(key)
                    == value
                    for key, value
                    in query.items()
                )
            ]
        )

    def insert_one(
        self,
        value,
        *,
        session,
    ):
        self.rows.append(
            dict(value)
        )


def setup():
    collection = _Collection()
    registry = (
        LegalWorkCompletionEventRegistry(
            collection
        )
    )
    return registry, collection


def test_collection_name_is_exact() -> None:
    assert (
        COLLECTION_NAME
        == "legal_work_completion_events"
    )


def test_indexes_are_tenant_first_immutable_unique_and_non_ttl() -> None:
    registry, collection = setup()

    registry.ensure_indexes()

    names = {
        name
        for _, _, name, _
        in collection.indexes
    }

    assert {
        "legal_work_completion_event_identity_unique",
        "legal_work_completion_event_fingerprint_unique",
        "legal_work_completion_work_history_unique",
        "legal_work_completion_matter_history",
        "legal_work_completion_actor_history",
    } <= names

    for keys, _, _, kwargs in (
        collection.indexes
    ):
        assert keys[0][0] == "tenant_id"
        assert (
            "expireAfterSeconds"
            not in kwargs
        )


def test_active_caller_transaction_is_required() -> None:
    registry, _ = setup()

    with pytest.raises(
        LegalWorkCompletionEventRegistryTransactionRequiredError
    ):
        registry.create_or_replay(
            event(),
            session=None,
        )


def test_create_and_exact_replay_return_same_truth() -> None:
    registry, collection = setup()
    value = event()

    first = registry.create_or_replay(
        value,
        session=ACTIVE,
    )
    replay = registry.create_or_replay(
        value,
        session=ACTIVE,
    )

    assert first == value
    assert replay == value
    assert len(
        collection.rows
    ) == 1


def test_same_work_cannot_be_rebound_to_divergent_completion_truth() -> None:
    registry, _ = setup()

    registry.create_or_replay(
        event(),
        session=ACTIVE,
    )

    divergent = event(
        completion_evidence_reference=
            "evidence:complete:other"
    )

    with pytest.raises(
        LegalWorkCompletionEventRegistryConflictError
    ):
        registry.create_or_replay(
            divergent,
            session=ACTIVE,
        )


def test_get_by_id_is_exact_and_tenant_scoped() -> None:
    registry, _ = setup()
    value = event()

    registry.create_or_replay(
        value,
        session=ACTIVE,
    )

    assert (
        registry.get_by_id(
            "tenant-law",
            value.completion_event_id,
            session=ACTIVE,
        )
        == value
    )


def test_work_matter_and_actor_history_are_exact() -> None:
    registry, _ = setup()

    first = event()
    second = event(
        tenant_id="tenant-law",
        case_matter_id="matter-2",
        work_item_id="work-2",
        work_item_fingerprint="d" * 128,
        completion_evidence_reference="evidence:complete:2",
        completion_evidence_fingerprint="e" * 128,
        actor_principal_id="principal-2",
        authorization_evidence_reference="iam:decision:2",
        authorization_evidence_fingerprint="f" * 128,
    )
    foreign = event(
        tenant_id="tenant-other"
    )

    for value in (
        first,
        second,
        foreign,
    ):
        registry.create_or_replay(
            value,
            session=ACTIVE,
        )

    assert (
        registry.list_work_history(
            "tenant-law",
            "work-1",
            session=ACTIVE,
        )
        == (
            first,
        )
    )

    assert (
        registry.list_matter_history(
            "tenant-law",
            "matter-2",
            session=ACTIVE,
        )
        == (
            second,
        )
    )

    assert (
        registry.list_actor_history(
            "tenant-law",
            "principal-2",
            session=ACTIVE,
        )
        == (
            second,
        )
    )


def test_persisted_corruption_and_extra_fields_reject() -> None:
    registry, collection = setup()
    value = event()

    registry.create_or_replay(
        value,
        session=ACTIVE,
    )

    collection.rows[0][
        "fingerprint"
    ] = "0" * 128

    with pytest.raises(
        LegalWorkCompletionEventRegistryPersistedRecordInvalidError
    ):
        registry.get_by_id(
            "tenant-law",
            value.completion_event_id,
            session=ACTIVE,
        )

    collection.rows[0] = (
        value.to_dict()
    )
    collection.rows[0][
        "unexpected"
    ] = True

    with pytest.raises(
        LegalWorkCompletionEventRegistryPersistedRecordInvalidError
    ):
        registry.get_by_id(
            "tenant-law",
            value.completion_event_id,
            session=ACTIVE,
        )


def test_registry_exposes_no_mutable_or_authority_surfaces() -> None:
    public = {
        name
        for name in dir(
            LegalWorkCompletionEventRegistry
        )
        if not name.startswith("_")
    }

    forbidden = {
        "update",
        "replace",
        "delete",
        "complete",
        "mark_complete",
        "mark_satisfied",
        "grant",
        "assign",
        "supervise",
        "notify",
    }

    assert public.isdisjoint(
        forbidden
    )


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_work_completion_event_registry.py
# VERSION: v1.0.0-P14-R14-WORK-COMPLETION-EVENT-REGISTRY-UNIT
# APPEND ONLY: YES
# TTL: ABSENT
# MUTABLE CURRENT POINTER: ABSENT
# COMPLETION AUTHORITY: NONE
# DEPENDENCY SATISFACTION AUTHORITY: NONE
# FINANCIAL AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
