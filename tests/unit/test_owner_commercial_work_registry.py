from datetime import datetime, timezone
from dataclasses import replace

import pytest

from tools.eos.crm.domain.owner_commercial_work_item import (
    OwnerCommercialWorkItem, OwnerWorkStatus,
)
from tools.eos.crm.persistence.owner_commercial_work_registry import (
    OwnerCommercialWorkRegistry, OwnerWorkRegistryConflict,
    OwnerWorkRegistryNotFound, OwnerWorkRegistryError, ensure_indexes,
)

NOW = datetime(2026, 11, 3, 8, tzinfo=timezone.utc)
TENANT = "WILSYTENANT-4CD2FZ4O"


class Cursor(list):
    def sort(self, *_args, **_kwargs):
        return self

    def limit(self, _value):
        return self


class Collection:
    def __init__(self):
        self.rows = []
        self.indexes = []

    def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))

    def find_one(self, query, session=None):
        assert session is not None
        return next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)

    def insert_one(self, document, session=None):
        assert session is not None
        self.rows.append(dict(document))

    def find(self, query, session=None):
        assert session is not None
        return Cursor(row for row in self.rows if all(row.get(k) == v for k, v in query.items()))

    def update_one(self, query, update, session=None):
        assert session is not None
        row = next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)
        if row is None:
            return type("Result", (), {"matched_count": 0})()
        row.update(update["$set"])
        return type("Result", (), {"matched_count": 1})()


def make_item(tenant=TENANT):
    return OwnerCommercialWorkItem.create(
        tenant_id=tenant, title="Prepare client follow-up",
        owner_principal_id="principal-1", now=NOW,
    )


def test_registry_requires_collection_and_caller_session():
    with pytest.raises(OwnerWorkRegistryError):
        OwnerCommercialWorkRegistry(None)
    registry = OwnerCommercialWorkRegistry(Collection())
    with pytest.raises(OwnerWorkRegistryError, match="SESSION_REQUIRED"):
        registry.create_or_replay(make_item(), idempotency_key="cmd-1", session=None)


def test_create_replay_is_exact_and_divergent_reuse_denies():
    registry = OwnerCommercialWorkRegistry(Collection())
    item = make_item()
    assert registry.create_or_replay(item, idempotency_key="cmd-1", session=object()) == item
    assert registry.create_or_replay(item, idempotency_key="cmd-1", session=object()) == item
    changed = make_item()
    changed = replace(changed, title="Different command")
    with pytest.raises(OwnerWorkRegistryConflict):
        registry.create_or_replay(changed, idempotency_key="cmd-1", session=object())


def test_get_and_list_are_exact_tenant_scoped():
    registry = OwnerCommercialWorkRegistry(Collection())
    item = make_item()
    registry.create_or_replay(item, idempotency_key="cmd-1", session=object())
    assert registry.get(tenant_id=TENANT, work_item_id=item.work_item_id, session=object()) == item
    with pytest.raises(OwnerWorkRegistryNotFound):
        registry.get(tenant_id="OTHER-TENANT", work_item_id=item.work_item_id, session=object())
    assert registry.list_for_tenant(tenant_id="OTHER-TENANT", session=object()) == ()


def test_daily_queue_projection_is_tenant_scoped():
    registry = OwnerCommercialWorkRegistry(Collection())
    item = make_item()
    registry.create_or_replay(item, idempotency_key="cmd-1", session=object())
    queue = registry.daily_queue(tenant_id=TENANT, now=NOW, session=object())
    assert len(queue) == 1
    assert queue[0]["work_item_id"] == item.work_item_id


def test_index_set_is_tenant_first_and_has_no_ttl():
    collection = Collection()
    ensure_indexes(collection)
    assert len(collection.indexes) == 3
    assert all(keys[0][0] == "tenant_id" for keys, _ in collection.indexes)
    assert all(kwargs.get("expireAfterSeconds") is None for _, kwargs in collection.indexes)


def test_terminal_work_item_not_in_daily_queue():
    registry = OwnerCommercialWorkRegistry(Collection())
    item = make_item()
    completed = replace(
        item, status=OwnerWorkStatus.COMPLETED,
        completed_at=NOW, updated_at=NOW,
    )
    # Completed records are excluded from actionable queue even when hydrated
    # from a source snapshot; registry creation remains an immutable insert.
    from tools.eos.crm.domain.owner_commercial_work_item import build_daily_queue
    assert build_daily_queue([completed], tenant_id=TENANT, now=NOW) == ()


def test_completion_is_tenant_scoped_compare_and_set_and_exact_replay():
    registry = OwnerCommercialWorkRegistry(Collection())
    item = make_item()
    registry.create_or_replay(item, idempotency_key="cmd-1", session=object())
    completed = registry.complete(
        tenant_id=TENANT, work_item_id=item.work_item_id,
        completion_note="Confirmed completed", now=NOW, session=object(),
    )
    assert completed.status is OwnerWorkStatus.COMPLETED
    assert registry.complete(
        tenant_id=TENANT, work_item_id=item.work_item_id,
        completion_note="Confirmed completed", now=NOW, session=object(),
    ) == completed
    with pytest.raises(OwnerWorkRegistryConflict):
        registry.complete(
            tenant_id=TENANT, work_item_id=item.work_item_id,
            completion_note="Different evidence", now=NOW, session=object(),
        )
    with pytest.raises(OwnerWorkRegistryNotFound):
        registry.complete(
            tenant_id="OTHER-TENANT", work_item_id=item.work_item_id,
            completion_note="Confirmed completed", now=NOW, session=object(),
        )
