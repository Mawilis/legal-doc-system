"""Real replica-set certification for independent Operations/Intelligence task queues."""
from __future__ import annotations

from datetime import datetime, timezone
import os
import uuid
from typing import Any, Iterator

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState, create_tenant_product_entitlement,
)
from tools.eos.saas.entitlement import tenant_product_entitlement_registry as entitlement_registry
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import derive_tenant_product_entitlement_id
from tools.eos.workspaces.persistence.tenant_module_work_registry import (
    TenantModuleWorkRegistry, ensure_indexes as ensure_work_indexes,
)
from tools.eos.workspaces.service.tenant_module_workspace_service import (
    TenantModuleWorkspaceError, TenantModuleWorkspaceService,
)

URI = os.getenv("TEST_VENDOR_MONGO_URI")
EXPECTED_REPLICA_SET = "tenantModuleCertRS"
NOW = datetime(2026, 11, 6, 10, tzinfo=timezone.utc)
FP = "b" * 128
TENANT = "WILSYTENANT-4CD2FZ4O"


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any, Any]]:
    if not URI:
        pytest.skip("TEST_VENDOR_MONGO_URI is not configured")
    client: MongoClient[Any] = MongoClient(
        URI, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000,
        retryWrites=True, tz_aware=True,
    )
    database = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"module-work Mongo unavailable before yield: {type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("module-work replica set has no writable primary")
        database = client[f"wilsy_tenant_module_work_{uuid.uuid4().hex}"]
        history = database.get_collection(
            entitlement_registry.HISTORY_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        current = database.get_collection(
            entitlement_registry.CURRENT_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        entitlement_registry.ensure_indexes(history, current)
        yield client, database, history, current
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def activate_product(client, tenant_id, product_id, history, current):
    entitlement_id = derive_tenant_product_entitlement_id(tenant_id, product_id)
    pending = create_tenant_product_entitlement(
        tenant_id=tenant_id, entitlement_id=entitlement_id, product_id=product_id,
        source_evidence_reference=f"module-work-source:{product_id.value}",
        source_evidence_fingerprint=FP,
    )
    with client.start_session() as session:
        def activate(active):
            entitlement_registry.create_or_replay(pending, history, current, session=active)
            entitlement_registry.transition(
                tenant_id=tenant_id, entitlement_id=entitlement_id,
                target_state=TenantProductEntitlementState.ACTIVE,
                expected_revision=0, evidence_reference=f"module-work-active:{product_id.value}",
                evidence_fingerprint=FP, occurred_at=NOW,
                history_collection=history, current_collection=current, session=active,
            )
        session.with_transaction(activate)
    return entitlement_id


def build_service(database, product_id, collection_name, history, current):
    collection = database.get_collection(
        collection_name, write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    ensure_work_indexes(collection)
    return TenantModuleWorkspaceService(
        TenantModuleWorkRegistry(collection), product_id, history, current,
    )


def transact(client, callback):
    with client.start_session() as session:
        return session.with_transaction(lambda active: callback(active))


def test_real_replica_set_proves_module_entitlement_and_queue_isolation(mongo_context):
    client, database, history, current = mongo_context
    activate_product(client, TENANT, TenantProductId.OPERATIONS, history, current)
    activate_product(client, TENANT, TenantProductId.INTELLIGENCE, history, current)
    operations = build_service(
        database, TenantProductId.OPERATIONS, "tenant_operations_work_items", history, current,
    )
    intelligence = build_service(
        database, TenantProductId.INTELLIGENCE, "tenant_intelligence_work_items", history, current,
    )
    created = transact(client, lambda session: operations.create(
        tenant_id=TENANT, principal_id="principal-owner", title="Publish weekly operating plan",
        description="", kind=__import__("tools.eos.workspaces.domain.tenant_module_work_item", fromlist=["ModuleWorkKind"]).ModuleWorkKind.TASK,
        priority=__import__("tools.eos.workspaces.domain.tenant_module_work_item", fromlist=["ModuleWorkPriority"]).ModuleWorkPriority.HIGH,
        due_at=None, source_type=None, source_id=None, idempotency_key="operations-task-1",
        now=NOW, session=session,
    ))
    ops_queue = transact(client, lambda session: operations.daily_queue(
        tenant_id=TENANT, now=NOW, session=session,
    ))
    intel_queue = transact(client, lambda session: intelligence.daily_queue(
        tenant_id=TENANT, now=NOW, session=session,
    ))
    assert [item["work_item_id"] for item in ops_queue] == [created.work_item_id]
    assert intel_queue == ()

    completed = transact(client, lambda session: operations.complete(
        tenant_id=TENANT, work_item_id=created.work_item_id,
        completion_note="Weekly operating plan published", now=NOW, session=session,
    ))
    assert completed.status.value == "COMPLETED"
    assert transact(client, lambda session: operations.daily_queue(
        tenant_id=TENANT, now=NOW, session=session,
    )) == ()

    missing = build_service(
        database, TenantProductId.INTELLIGENCE, "tenant_intelligence_work_items",
        history, current,
    )
    with pytest.raises(TenantModuleWorkspaceError, match="MODULE_WORK_PRODUCT_NOT_ENTITLED"):
        transact(client, lambda session: missing.daily_queue(
            tenant_id="OTHER-TENANT", now=NOW, session=session,
        ))
