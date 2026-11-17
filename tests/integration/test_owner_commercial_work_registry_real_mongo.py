"""TITLE: WILSY OS CRM Owner Work Real Mongo Persistence Certificate
VERSION: v1.2.0-CANCELLATION-REAL-MONGO-CERT
AUTHORITY: WILSY OS CRM source persistence certification.
EPITOME: Certify tenant-scoped source commands, idempotent completion,
         independent persisted readback and exact tenant isolation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_owner_commercial_work_registry_real_mongo.py
COLLABORATION / OWNERSHIP: OwnerCommercialWorkRegistry and CRM source domain;
         requires an explicitly configured disposable Mongo replica set.
CERTIFICATION / UPDATE DATE: 2026-11-17
CHANGELOG: v1.2.0-CANCELLATION-REAL-MONGO-CERT verifies durable
           CANCELLED terminal status, source audit, idempotent replay and
           independent readback in an isolated replica-set transaction.
CHANGELOG: v1.1.0-AUDITED-EDIT-REAL-MONGO-CERT proves CRM task
           edit/audit commit atomically under a real replica-set transaction,
           independent source readback, exact replay, stale-version and foreign
           tenant denial. Disposable fixture teardown remains unchanged.
CHANGELOG: v1.0.0-PERSISTED-COMPLETED-WORK-READBACK-CERT proves a completed item
           persists evidence across a new session and remains inaccessible
           under a foreign tenant coordinate. Existing tests are preserved.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Disposable fixture DB only; never production data.
TENANT BOUNDARY: Every record read is tenant-prefixed.
AUTHORITY BOUNDARY: Tests source registry, no IAM grant or HTTP authorization.
TRANSACTION / IDEMPOTENCY BOUNDARY: Caller-owned replica-set sessions and
                                   source compare-and-set receipts.
FINANCIAL AUTHORITY BOUNDARY: No funds; Kennel EOS exclusively executes.
FAIL-CLOSED POSTURE: Missing disposable Mongo is a skip, not pass evidence.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from pymongo import MongoClient

from tools.eos.crm.domain.owner_commercial_work_item import (
    OwnerCommercialWorkItem, OwnerWorkPriority, OwnerWorkStatus,
)
from tools.eos.crm.persistence.owner_commercial_work_registry import (
    COLLECTION, EVENTS_COLLECTION, OwnerCommercialWorkRegistry, OwnerWorkRegistryConflict,
    OwnerWorkRegistryNotFound, ensure_indexes,
)

URI = os.getenv("TEST_VENDOR_MONGO_URI")
pytestmark = pytest.mark.skipif(not URI, reason="TEST_VENDOR_MONGO_URI is not configured")
TENANT = "WILSYTENANT-4CD2FZ4O"
NOW = datetime(2026, 11, 3, 8, tzinfo=timezone.utc)


@pytest.fixture
def registry():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    database_name = "owner_work_cert_" + uuid.uuid4().hex
    collection = client[database_name][COLLECTION]
    events = client[database_name][EVENTS_COLLECTION]
    ensure_indexes(collection, events)
    try:
        yield client, collection, OwnerCommercialWorkRegistry(collection, events)
    finally:
        client.drop_database(database_name)
        client.close()


def make_item(*, tenant=TENANT, title="Prepare client follow-up", due_at=None):
    return OwnerCommercialWorkItem.create(
        tenant_id=tenant, title=title, owner_principal_id="principal-owner",
        priority=OwnerWorkPriority.HIGH, due_at=due_at, now=NOW,
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
        with pytest.raises(OwnerWorkRegistryNotFound):
            store.get(tenant_id="OTHER-TENANT", work_item_id=item.work_item_id, session=session)
        completed = session.with_transaction(lambda active: store.complete(
            tenant_id=TENANT, work_item_id=item.work_item_id,
            completion_note="Follow-up completed", now=NOW, session=active,
        ))
        assert completed.status is OwnerWorkStatus.COMPLETED
        replayed_completion = session.with_transaction(lambda active: store.complete(
            tenant_id=TENANT, work_item_id=item.work_item_id,
            completion_note="Follow-up completed", now=NOW + timedelta(minutes=1),
            session=active,
        ))
        assert replayed_completion == completed
    # Independent Mongo session reads durable source evidence, not a UI cache.
    with client.start_session() as independent:
        persisted = independent.with_transaction(lambda active: store.get(
            tenant_id=TENANT, work_item_id=item.work_item_id, session=active,
        ))
        assert persisted.status is OwnerWorkStatus.COMPLETED
        assert persisted.completed_at == NOW
        assert persisted.completion_note == "Follow-up completed"
        with pytest.raises(OwnerWorkRegistryNotFound):
            independent.with_transaction(lambda active: store.get(
                tenant_id="OTHER-TENANT", work_item_id=item.work_item_id,
                session=active,
            ))



def test_real_mongo_audited_edit_is_durable_idempotent_and_tenant_fenced(registry):
    client, collection, store = registry
    item = make_item(title="Before revision")
    changed_at = NOW + timedelta(minutes=2)
    arguments = dict(
        tenant_id=TENANT, work_item_id=item.work_item_id,
        actor_principal_id="principal-owner",
        title="After revision", description="Verified EOS source update",
        priority=OwnerWorkPriority.CRITICAL,
        due_at=NOW + timedelta(days=2),
        expected_updated_at=NOW, idempotency_key="audited-edit-1",
        now=changed_at,
    )
    with client.start_session() as session:
        session.with_transaction(lambda active: store.create_or_replay(
            item, idempotency_key="create-for-edit", session=active,
        ))
        accepted = session.with_transaction(lambda active: store.revise(
            **arguments, session=active,
        ))
        assert accepted.updated_at == changed_at
        assert session.with_transaction(lambda active: store.revise(
            **arguments, session=active,
        )) == accepted
        with pytest.raises(OwnerWorkRegistryConflict):
            session.with_transaction(lambda active: store.revise(
                **{**arguments, "idempotency_key": "stale-edit"}, session=active,
            ))
        with pytest.raises(OwnerWorkRegistryNotFound):
            session.with_transaction(lambda active: store.revise(
                **{**arguments, "tenant_id": "FOREIGN-TENANT",
                   "idempotency_key": "foreign-edit"}, session=active,
            ))
    with client.start_session() as independent:
        persisted = independent.with_transaction(lambda active: store.get(
            tenant_id=TENANT, work_item_id=item.work_item_id, session=active,
        ))
        history = independent.with_transaction(lambda active: store.revision_history(
            tenant_id=TENANT, work_item_id=item.work_item_id, session=active,
        ))
    assert persisted.title == "After revision"
    assert persisted.priority is OwnerWorkPriority.CRITICAL
    assert persisted.updated_at == changed_at
    assert len(history) == 1
    assert history[0]["actor_principal_id"] == "principal-owner"
    assert history[0]["before"]["title"] == "Before revision"
    assert history[0]["after"]["title"] == "After revision"


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
        with pytest.raises(OwnerWorkRegistryConflict):
            session.with_transaction(lambda active: store.create_or_replay(
                make_item(title="Changed"), idempotency_key="stable", session=active,
            ))
        session.with_transaction(lambda active: store.complete(
            tenant_id=TENANT, work_item_id=item.work_item_id,
            completion_note="Done", now=NOW, session=active,
        ))
        with pytest.raises(OwnerWorkRegistryConflict):
            session.with_transaction(lambda active: store.complete(
                tenant_id=TENANT, work_item_id=item.work_item_id,
                completion_note="Contradictory completion", now=NOW, session=active,
            ))


def test_real_mongo_owner_cancellation_is_atomic_and_visible_after_new_session(registry):
    """A cancellation must commit its source record and audit event together."""
    client, collection, store = registry
    original = make_item(title="Cancel source task")
    with client.start_session() as session:
        session.with_transaction(lambda active: store.create_or_replay(
            original, idempotency_key="cancel-create", session=active,
        ))
        def cancel(active):
            return store.cancel(
                tenant_id=TENANT, work_item_id=original.work_item_id,
                actor_principal_id=original.owner_principal_id,
                reason="Requirements withdrawn",
                expected_updated_at=original.updated_at,
                idempotency_key="cancel-attempt", now=NOW + timedelta(minutes=1),
                session=active,
            )
        committed = session.with_transaction(cancel)
        assert committed.status is OwnerWorkStatus.CANCELLED
        assert session.with_transaction(cancel) == committed
    with client.start_session() as separate:
        def read(active):
            persisted = store.get(
                tenant_id=TENANT, work_item_id=original.work_item_id,
                session=active,
            )
            history = store.revision_history(
                tenant_id=TENANT, work_item_id=original.work_item_id,
                session=active,
            )
            assert persisted.status is OwnerWorkStatus.CANCELLED
            assert len(history) == 1
            assert history[0]["operation"] == "CANCEL"
            assert history[0]["reason"] == "Requirements withdrawn"
            assert history[0]["before"]["status"] == "OPEN"
            assert history[0]["after"]["status"] == "CANCELLED"
            assert store.daily_queue(tenant_id=TENANT, now=NOW, session=active) == ()
        separate.with_transaction(read)


# ARTIFACT: tests/integration/test_owner_commercial_work_registry_real_mongo.py
# VERSION: v1.2.0-CANCELLATION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: Source registry test, no IAM or execution authority.
# TENANT POSTURE: Exact tenant record readback, foreign record not found.
# FAIL-CLOSED POSTURE: Persistence proof requires real disposable replica set.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
