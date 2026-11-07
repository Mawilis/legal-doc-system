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

import tools.eos.auth.authentication as authentication
import tools.eos.auth.tenant_access as tenant_access
import tools.eos.api.tenant_authorization_http as authorization_http
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository, RoleAssignmentNotFoundError
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
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


def _activate_operations(
    client: MongoClient[Any],
    database: Any,
    product_id: TenantProductId = TenantProductId.OPERATIONS,
    tenant_id: str = TENANT,
) -> None:
    entitlement_id = derive_tenant_product_entitlement_id(tenant_id, product_id)
    pending = create_tenant_product_entitlement(
        tenant_id=tenant_id,
        entitlement_id=entitlement_id,
        product_id=product_id,
        source_evidence_reference=f"my-work-{product_id.value.lower()}-entitlement",
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
                evidence_reference=f"my-work-{product_id.value.lower()}-active",
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
    _activate_operations(client, database, TenantProductId.OPERATIONS, tenant_id=tenant_id)
    _activate_operations(client, database, TenantProductId.INTELLIGENCE, tenant_id=tenant_id)

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

    intelligence_product, intelligence_workspace, intelligence_collection, _ = module_source._PRODUCTS["intelligence"]
    intelligence_service = module_source._service(database, intelligence_product, intelligence_collection)
    with client.start_session() as session:
        intelligence_created = session.with_transaction(lambda active: intelligence_service.create(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            title="Validate independent intelligence source queue",
            description="Read from its own registry and entitlement.",
            kind=ModuleWorkKind.TASK,
            priority=ModuleWorkPriority.NORMAL,
            due_at=None,
            source_type=None,
            source_id=None,
            idempotency_key="my-work-real-mongo-intelligence-1",
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
    app.dependency_overrides[my_work._INTELLIGENCE_READ] = _context
    app.dependency_overrides[my_work._CRM_READ] = lambda: None

    with TestClient(app) as browser:
        response = browser.get("/api/my-work", headers={"X-Tenant-ID": TENANT})

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["sources_included"] == ["OPERATIONS", "INTELLIGENCE"]
    assert payload["summary"]["active_count"] == 2
    assert {item["work_item_id"] for item in payload["items"]} == {created.work_item_id, intelligence_created.work_item_id}
    assert {item["source"] for item in payload["items"]} == {"OPERATIONS", "INTELLIGENCE"}
    assert payload["items"][0]["action_authority"] == "SOURCE_SERVICE_ONLY"
    assert payload["authority"]["permits_completion"] is False


class _LivePrincipalReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        return PrincipalAuthorityRepository.get(principal_id, self.collection, session=session)


class _LiveMembershipReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, tenant_id: str, *, session: Any = None) -> Any:
        return TenantMembershipRepository.resolve(principal_id, tenant_id, self.collection, session=session)


class _LiveRoleReader:
    def __init__(self, role_collection: Any, business_collection: Any) -> None:
        self.role_collection = role_collection
        self.business_collection = business_collection

    def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: Any = None) -> Any:
        if role_id in TENANT_ROLES:
            try:
                value = TenantBusinessRoleRepository.resolve(
                    principal_id, tenant_id, self.business_collection, session=session
                )
            except Exception as error:
                from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleNotFoundError
                if isinstance(error, TenantBusinessRoleNotFoundError):
                    raise RoleAssignmentNotFoundError("TENANT_BUSINESS_ROLE_NOT_FOUND") from error
                raise
            if value.business_role != role_id:
                raise RoleAssignmentNotFoundError("TENANT_BUSINESS_ROLE_NOT_FOUND")
            return value
        return RoleAssignmentRepository.resolve(
            principal_id, tenant_id, role_id, self.role_collection, session=session
        )


def _seed_live_owner_iam(database: Any, principal_id: str, tenant_id: str) -> None:
    principal = database["principal_authorities"]
    membership = database["tenant_memberships"]
    business = database["tenant_business_roles"]
    assignments = database["role_assignments"]
    PrincipalAuthorityRepository.ensure_indexes(principal)
    TenantMembershipRepository.ensure_indexes(membership)
    TenantBusinessRoleRepository.ensure_indexes(business)
    RoleAssignmentRepository.ensure_indexes(assignments)
    PrincipalAuthorityRepository.create(PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0), principal)
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(principal_id, tenant_id, TenantMembershipStatus.ACTIVE, 0), membership
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal_id, tenant_id, "tenant_owner", TenantBusinessRoleStatus.ACTIVE, 0, NOW, None
        ), business
    )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(principal_id, tenant_id, "TENANT_OWNER", RoleAssignmentStatus.ACTIVE, 0),
        assignments,
    )


def test_authenticated_my_work_uses_live_mongo_iam_and_rejects_foreign_scope(
    mongo_context, monkeypatch: Any
) -> None:
    client, database = mongo_context
    tenant_id = TENANT + "-live-iam"
    foreign_tenant = TENANT + "-foreign"
    principal_id = PRINCIPAL + "-live-iam"
    _seed_live_owner_iam(database, principal_id, tenant_id)
    _activate_operations(client, database, TenantProductId.OPERATIONS, tenant_id=tenant_id)
    _activate_operations(client, database, TenantProductId.INTELLIGENCE, tenant_id=tenant_id)

    module_source = my_work.module_source
    monkeypatch.setattr(module_source, "get_client", lambda: client)
    monkeypatch.setattr(module_source, "get_database", lambda: database)
    monkeypatch.setattr(my_work.crm_source, "get_client", lambda: client)
    monkeypatch.setattr(my_work.crm_source, "get_database", lambda: database)
    monkeypatch.setattr(
        my_work.crm_source.subscription_registry_module,
        "subscriptions_collection",
        database["subscriptions"],
    )

    for slug in ("operations", "intelligence"):
        product_id, _workspace, collection_name, _prefix = module_source._PRODUCTS[slug]
        service = module_source._service(database, product_id, collection_name)
        with client.start_session() as session:
            session.with_transaction(lambda active, service=service, slug=slug: service.create(
                tenant_id=tenant_id,
                principal_id=principal_id,
                title=f"Live IAM {slug} source task",
                description="Created in its own durable source registry.",
                kind=ModuleWorkKind.TASK,
                priority=ModuleWorkPriority.NORMAL,
                due_at=None,
                source_type=None,
                source_id=None,
                idempotency_key=f"live-iam-{slug}",
                now=NOW,
                session=active,
            ))

    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(my_work.router, prefix="/api")
    identity = SovereignIdentity(
        identity_id=principal_id,
        tenant_id="untrusted-token-tenant",
        username="live-iam-owner",
        email="live-iam-owner@example.test",
        roles=["tenant_owner"],
        permissions=[],
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    app.dependency_overrides[my_work.get_current_identity] = lambda: identity
    app.dependency_overrides[authentication.get_principal_authority_repository] = (
        lambda: _LivePrincipalReader(database["principal_authorities"])
    )
    app.dependency_overrides[tenant_access.get_tenant_membership_repository] = (
        lambda: _LiveMembershipReader(database["tenant_memberships"])
    )
    app.dependency_overrides[authorization_http.get_role_assignment_repository] = (
        lambda: _LiveRoleReader(database["role_assignments"], database["tenant_business_roles"])
    )
    # CRM is admitted by live IAM, then independently denied by its own
    # Legal subscription/entitlement projection in the real Mongo transaction.
    app.dependency_overrides[my_work._CRM_READ] = lambda: _context()

    with TestClient(app) as api:
        admitted = api.get("/api/my-work", headers={"X-Tenant-ID": tenant_id})
        foreign = api.get("/api/my-work", headers={"X-Tenant-ID": foreign_tenant})

    assert admitted.status_code == 200, admitted.text
    payload = admitted.json()
    assert payload["tenant_id"] == tenant_id
    assert payload["sources_included"] == ["OPERATIONS", "INTELLIGENCE"]
    assert payload["summary"]["active_count"] == 2
    assert {row["source"] for row in payload["items"]} == {"OPERATIONS", "INTELLIGENCE"}
    assert foreign.status_code == 403
    assert foreign.json()["detail"] == "MY_WORK_NO_AUTHORIZED_SOURCE"
