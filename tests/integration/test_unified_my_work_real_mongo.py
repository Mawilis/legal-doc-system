"""Replica-set proof for authenticated My Work source aggregation.

The HTTP boundary is exercised with an already-admitted source context while the
owning Operations entitlement, queue registry, snapshot transaction and route
read are backed by an isolated real Mongo replica-set database. IAM decision
semantics are certified separately by the optional-authorization HTTP tests.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
import uuid
from typing import Any, Iterator
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.api import unified_my_work_router as my_work
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
    create_tenant_product_entitlement,
)
from tools.eos.saas.entitlement import tenant_product_entitlement_registry as entitlement_registry
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)
from tools.eos.workspaces.domain.tenant_module_work_item import (
    ModuleWorkKind,
    ModuleWorkPriority,
)

URI = os.getenv("TEST_VENDOR_MONGO_URI")
EXPECTED_REPLICA_SET = parse_qs(urlparse(URI or "").query).get("replicaSet", [None])[0]
TENANT = "WILSYTENANT-4CD2FZ4O"
PRINCIPAL = "my-work-real-mongo-principal"
NOW = datetime(2026, 11, 6, 10, tzinfo=timezone.utc)
FINGERPRINT = "b" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any]]:
    if not URI:
        pytest.skip("TEST_VENDOR_MONGO_URI is not configured")
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"My Work Mongo unavailable before yield: {type(error).__name__}")
        if not EXPECTED_REPLICA_SET or hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong My Work replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("My Work replica set has no writable primary")
        database = client[f"unified_my_work_{uuid.uuid4().hex}"]
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
        yield client, database
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _activate_operations(client: MongoClient[Any], database: Any) -> None:
    entitlement_id = derive_tenant_product_entitlement_id(TENANT, TenantProductId.OPERATIONS)
    pending = create_tenant_product_entitlement(
        tenant_id=TENANT,
        entitlement_id=entitlement_id,
        product_id=TenantProductId.OPERATIONS,
        source_evidence_reference="my-work-operations-entitlement",
        source_evidence_fingerprint=FINGERPRINT,
    )
    history = database.get_collection(entitlement_registry.HISTORY_COLLECTION)
    current = database.get_collection(entitlement_registry.CURRENT_COLLECTION)
    with client.start_session() as session:
        def activate(active: Any) -> None:
            entitlement_registry.create_or_replay(pending, history, current, session=active)
            entitlement_registry.transition(
                tenant_id=TENANT,
                entitlement_id=entitlement_id,
                target_state=TenantProductEntitlementState.ACTIVE,
                expected_revision=0,
                evidence_reference="my-work-operations-active",
                evidence_fingerprint=FINGERPRINT,
                occurred_at=NOW,
                history_collection=history,
                current_collection=current,
                session=active,
            )
        session.with_transaction(activate)


def _context() -> Any:
    return type(
        "AuthorizedSourceContext",
        (),
        {"tenant_id": TENANT, "identity": type("Identity", (), {"identity_id": PRINCIPAL})()},
    )()


def test_authenticated_my_work_http_reads_real_operations_queue_inside_owner_transaction(
    mongo_context,
    monkeypatch: Any,
) -> None:
    client, database = mongo_context
    _activate_operations(client, database)

    module_source = my_work.module_source
    monkeypatch.setattr(module_source, "get_client", lambda: client)
    monkeypatch.setattr(module_source, "get_database", lambda: database)

    product_id, _workspace_key, collection_name, _operation_prefix = module_source._PRODUCTS["operations"]
    service = module_source._service(database, product_id, collection_name)
    with client.start_session() as session:
        created = session.with_transaction(lambda active: service.create(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            title="Prepare verified daily operating report",
            description="Use the current source-of-truth operating figures.",
            kind=ModuleWorkKind.TASK,
            priority=ModuleWorkPriority.HIGH,
            due_at=None,
            source_type=None,
            source_id=None,
            idempotency_key="my-work-real-mongo-operations-1",
            now=NOW,
            session=active,
        ))

    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(my_work.router, prefix="/api")
    identity = SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id="non-authoritative-token-tenant",
        username="my-work-operator",
        email="my-work-operator@example.test",
        roles=["tenant_owner"],
        permissions=[],
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    app.dependency_overrides[my_work.get_current_identity] = lambda: identity
    app.dependency_overrides[my_work._LEGAL_READ] = lambda: None
    app.dependency_overrides[my_work._OPERATIONS_READ] = _context
    app.dependency_overrides[my_work._INTELLIGENCE_READ] = lambda: None
    app.dependency_overrides[my_work._CRM_READ] = lambda: None

    with TestClient(app) as browser:
        response = browser.get("/api/my-work", headers={"X-Tenant-ID": TENANT})

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["sources_included"] == ["OPERATIONS"]
    assert payload["summary"]["active_count"] == 1
    assert payload["items"][0]["work_item_id"] == created.work_item_id
    assert payload["items"][0]["title"] == "Prepare verified daily operating report"
    assert payload["items"][0]["action_authority"] == "SOURCE_SERVICE_ONLY"
    assert payload["authority"]["permits_completion"] is False
