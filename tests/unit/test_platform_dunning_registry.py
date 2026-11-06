from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.saas.billing.platform_dunning_registry import (
    PlatformDunningRegistry,
    PlatformDunningRegistryError,
    PlatformDunningRevisionConflict,
)


TENANT = "tenant-platform-dunning"
SUBSCRIPTION = "sub-001"
POLICY = "a" * 128
NOW = datetime(2026, 11, 4, 10, tzinfo=timezone.utc)


class UpdateResult:
    def __init__(self, matched_count: int) -> None:
        self.matched_count = matched_count


class FakeCollection:
    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []
        self.indexes: list[tuple[Any, Any]] = []
        self.calls: list[tuple[str, Any]] = []

    def create_index(self, keys: Any, **options: Any) -> str:
        self.indexes.append((keys, options))
        return str(options.get("name", "index"))

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> dict[str, Any] | None:
        self.calls.append(("find_one", session))
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                return deepcopy(document)
        return None

    def insert_one(self, document: dict[str, Any], *, session: Any = None) -> None:
        self.calls.append(("insert_one", session))
        self.documents.append(deepcopy(document))

    def update_one(self, query: dict[str, Any], update: dict[str, Any], *, session: Any = None) -> UpdateResult:
        self.calls.append(("update_one", session))
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                document.update(deepcopy(update["$set"]))
                return UpdateResult(1)
        return UpdateResult(0)


class Session:
    in_transaction = True


def transition(collection: FakeCollection, *, revision: int = 0, state: str = "WARNING",
               invoice_ids: tuple[str, ...] = ("inv-2", "inv-1"), days: int = 14,
               session: Any = None) -> dict[str, Any]:
    return PlatformDunningRegistry.transition(
        tenant_id=TENANT,
        subscription_id=SUBSCRIPTION,
        state=state,
        invoice_ids=invoice_ids,
        days_overdue=days,
        policy_fingerprint=POLICY,
        expected_revision=revision,
        collection=collection,
        session=session,
        evaluated_at=NOW,
    )


def test_indexes_enforce_tenant_subscription_identity() -> None:
    collection = FakeCollection()
    PlatformDunningRegistry.ensure_indexes(collection)
    assert collection.indexes[0][0] == [("tenant_id", 1), ("subscription_id", 1)]
    assert collection.indexes[0][1]["unique"] is True


def test_insert_and_hydrate_revision_one() -> None:
    collection = FakeCollection()
    result = transition(collection)
    assert result["revision"] == 1
    assert result["invoice_ids"] == ["inv-1", "inv-2"]
    assert PlatformDunningRegistry.get(TENANT, SUBSCRIPTION, collection) == result


def test_identical_replay_does_not_advance_revision() -> None:
    collection = FakeCollection()
    first = transition(collection)
    replay = transition(collection, revision=1)
    assert replay == first
    assert len(collection.documents) == 1
    assert collection.documents[0]["revision"] == 1


def test_stale_revision_is_rejected() -> None:
    collection = FakeCollection()
    transition(collection)
    transition(collection, revision=1, state="CRITICAL", days=30)
    with pytest.raises(PlatformDunningRevisionConflict):
        transition(collection, revision=1, state="SUSPENSION_REVIEW", days=45)


def test_revision_guard_advances_exactly_once() -> None:
    collection = FakeCollection()
    transition(collection)
    second = transition(collection, revision=1, state="CRITICAL", days=30)
    assert second["revision"] == 2
    assert collection.documents[0]["revision"] == 2


def test_tenant_is_part_of_projection_identity() -> None:
    collection = FakeCollection()
    transition(collection)
    assert PlatformDunningRegistry.get("another-tenant", SUBSCRIPTION, collection) is None


def test_caller_session_is_forwarded_and_never_owned() -> None:
    collection = FakeCollection()
    session = Session()
    transition(collection, session=session)
    assert collection.calls
    assert all(observed is session for _, observed in collection.calls)
    assert not hasattr(PlatformDunningRegistry, "commit")
    assert not hasattr(PlatformDunningRegistry, "abort")
    assert not hasattr(PlatformDunningRegistry, "start_transaction")


def test_corrupt_projection_fails_closed() -> None:
    collection = FakeCollection()
    transition(collection)
    collection.documents[0]["state"] = "ALTERED"
    with pytest.raises(PlatformDunningRegistryError):
        PlatformDunningRegistry.get(TENANT, SUBSCRIPTION, collection)


def test_invalid_inputs_fail_closed() -> None:
    collection = FakeCollection()
    with pytest.raises(PlatformDunningRegistryError):
        transition(collection, revision=-1)
    with pytest.raises(PlatformDunningRegistryError):
        transition(collection, invoice_ids=())
    with pytest.raises(PlatformDunningRegistryError):
        transition(collection, invoice_ids=("inv-1", "inv-1"))


def test_invoice_order_does_not_change_transition_fingerprint() -> None:
    left, right = FakeCollection(), FakeCollection()
    a = transition(left, invoice_ids=("inv-1", "inv-2"))
    b = transition(right, invoice_ids=("inv-2", "inv-1"))
    assert a["transition_fingerprint"] == b["transition_fingerprint"]


def test_unknown_projection_state_is_rejected():
    collection = FakeCollection()
    with pytest.raises(PlatformDunningRegistryError, match="STATE_INVALID"):
        transition(collection, state="UNKNOWN_STAGE")
