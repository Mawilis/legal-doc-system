"""Real-Mongo certification for tenant tenant module work persistence."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from pymongo import MongoClient

from tools.eos.workspaces.domain.tenant_module_work_item import (
    TenantModuleWorkItem, ModuleWorkPriority, ModuleWorkStatus,
)
from tools.eos.workspaces.persistence.tenant_module_work_registry import (
    COLLECTION, TenantModuleWorkRegistry, ModuleWorkRegistryConflict,
    ModuleWorkRegistryNotFound, ensure_indexes,
)

URI = os.getenv("TEST_VENDOR_MONGO_URI")
pytestmark = pytest.mark.skipif(not URI, reason="TEST_VENDOR_MONGO_URI is not configured")
TENANT = "WILSYTENANT-4CD2FZ4O"
NOW = datetime(2026, 11, 3, 8, tzinfo=timezone.utc)


@pytest.fixture
def registry():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    database_name = "module_work_cert_" + uuid.uuid4().hex
    collection = client[database_name][COLLECTION]
    ensure_indexes(collection)
    try:
        yield client, collection, TenantModuleWorkRegistry(collection)
    finally:
        client.drop_database(database_name)
        client.close()


def make_item(*, tenant=TENANT, title="Prepare client follow-up", due_at=None):
    return TenantModuleWorkItem.create(
        tenant_id=tenant, title=title, created_by_principal_id="principal-owner",
        priority=ModuleWorkPriority.HIGH, due_at=due_at, now=NOW,
    )


def test_real_mongo_create_replay_tenant_isolation_and_completion(registry):
    client, collection, store = registry
    item = make_item(due_at=NOW + timedelta(hours=2))
    with client.start_session() as session:
        session.with_transaction(lambda active: store.create_or_replay(
            item, idempotency_key="create-1", session=active,
        ))
        replay = session.with_transaction(lambda active: store.create_or_replay(
            make_item(due_at=NOW + timedelta(hours=2)),
            idempotency_key="create-1", session=active,
        ))
        assert replay.work_item_id == item.work_item_id
        with pytest.raises(ModuleWorkRegistryNotFound):
            store.get(tenant_id="OTHER-TENANT", work_item_id=item.work_item_id, session=session)
        completed = session.with_transaction(lambda active: store.complete(
            tenant_id=TENANT, work_item_id=item.work_item_id,
            completion_note="Follow-up completed", now=NOW, session=active,
        ))
        assert completed.status is ModuleWorkStatus.COMPLETED
        replayed_completion = session.with_transaction(lambda active: store.complete(
            tenant_id=TENANT, work_item_id=item.work_item_id,
            completion_note="Follow-up completed", now=NOW + timedelta(minutes=1),
            session=active,
        ))
        assert replayed_completion == completed


def test_real_mongo_queue_orders_overdue_and_today_and_is_tenant_scoped(registry):
    client, collection, store = registry
    overdue = make_item(title="Overdue", due_at=NOW - timedelta(days=1))
    today = make_item(title="Today", due_at=NOW + timedelta(hours=2))
    foreign = make_item(tenant="FOREIGN-TENANT", title="Foreign", due_at=NOW)
    with client.start_session() as session:
        def write(active):
            store.create_or_replay(overdue, idempotency_key="overdue", session=active)
            store.create_or_replay(today, idempotency_key="today", session=active)
            store.create_or_replay(foreign, idempotency_key="foreign", session=active)
        session.with_transaction(write)
        queue = session.with_transaction(lambda active: store.daily_queue(
            tenant_id=TENANT, now=NOW, session=active,
        ))
    assert [row["title"] for row in queue] == ["Overdue", "Today"]
    assert queue[0]["is_overdue"] is True
    assert queue[1]["is_due_today"] is True


def test_real_mongo_divergent_replay_and_terminal_completion_fail_closed(registry):
    client, collection, store = registry
    item = make_item()
    with client.start_session() as session:
        session.with_transaction(lambda active: store.create_or_replay(
            item, idempotency_key="stable", session=active,
        ))
        with pytest.raises(ModuleWorkRegistryConflict):
            session.with_transaction(lambda active: store.create_or_replay(
                make_item(title="Changed"), idempotency_key="stable", session=active,
            ))
        session.with_transaction(lambda active: store.complete(
            tenant_id=TENANT, work_item_id=item.work_item_id,
            completion_note="Done", now=NOW, session=active,
        ))
        with pytest.raises(ModuleWorkRegistryConflict):
            session.with_transaction(lambda active: store.complete(
                tenant_id=TENANT, work_item_id=item.work_item_id,
                completion_note="Contradictory completion", now=NOW, session=active,
            ))
