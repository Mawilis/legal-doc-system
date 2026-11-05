"""Disposable replica-set certification for the System Services case registry."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo import MongoClient
from fastapi.testclient import TestClient

from tools.eos.api import server
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.system_services.support_case import (
    SupportCase,
    SupportCaseCategory,
    SupportCaseEvent,
    SupportCaseScope,
    SupportCaseStatus,
)
from tools.eos.system_services.support_case_service import (
    SupportCaseApplicationService,
    SupportCaseActorContext,
    SupportCaseApplicationError,
)
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.system_services.support_case_registry import (
    CASE_COLLECTION,
    EVENT_COLLECTION,
    SupportCaseConflictError,
    SupportCaseNotFoundError,
    SupportCaseRegistry,
)

URI_ENV = "SYSTEM_SERVICES_CASE_MONGO_URI"
REPLICA_SET = "wilsySystemServicesCaseRS"
NOW = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_case_registry():
    uri = os.environ.get(URI_ENV, "").strip()
    if not uri or ("localhost" not in uri and "127.0.0.1" not in uri):
        pytest.skip(f"{URI_ENV} must point to a disposable loopback MongoDB replica set")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=3000)
    hello = client.admin.command("hello")
    address = client.address
    if address is None or address[0] not in {"localhost", "127.0.0.1"}:
        client.close()
        pytest.skip("System Services certification requires loopback MongoDB")
    if hello.get("setName") != REPLICA_SET or not hello.get("isWritablePrimary"):
        client.close()
        pytest.skip("System Services certification requires its disposable writable replica set")
    database_name = "wilsy_system_services_case_" + uuid.uuid4().hex
    database = client.get_database(
        database_name,
        read_concern=ReadConcern("majority"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    registry = SupportCaseRegistry(
        cases=database[CASE_COLLECTION],
        events=database[EVENT_COLLECTION],
    )
    registry.ensure_indexes()
    try:
        yield client, database, registry
    finally:
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()


def _case(case_id: str, *, scope=SupportCaseScope.SYSTEM, tenant_id=None):
    return SupportCase(
        case_id=case_id,
        scope=scope,
        tenant_id=tenant_id,
        principal_id="principal-synthetic-1",
        category=SupportCaseCategory.ACCOUNT_ACCESS,
        created_at=NOW,
        updated_at=NOW,
    )


def _event(event_id, case_id, key, actor, before, after, action, at):
    return SupportCaseEvent(
        event_id=event_id,
        case_id=case_id,
        actor_principal_id=actor,
        idempotency_key=key,
        from_status=before,
        to_status=after,
        action=action,
        occurred_at=at,
        evidence_reference="evidence-synthetic-1",
    )


def test_real_mongo_create_transition_commit_and_tenant_scope(mongo_case_registry):
    client, database, registry = mongo_case_registry
    case = _case("case-commit-1")
    with client.start_session() as session:
        with session.start_transaction():
            registry.create(
                case,
                _event("event-open-1", case.case_id, "idem-open-1", "actor-1", None, SupportCaseStatus.OPEN, "CASE_CREATED", NOW),
                session=session,
            )
    with client.start_session() as session:
        current = registry.get(case_id=case.case_id, scope=SupportCaseScope.SYSTEM, session=session)
        with session.start_transaction():
            updated = registry.transition(
                current=current,
                next_status=SupportCaseStatus.TRIAGED,
                event=_event("event-triage-1", case.case_id, "idem-triage-1", "actor-1", SupportCaseStatus.OPEN, SupportCaseStatus.TRIAGED, "CASE_TRIAGED", NOW + timedelta(seconds=1)),
                expected_revision=0,
                session=session,
            )
    assert updated.status is SupportCaseStatus.TRIAGED
    assert updated.revision == 1
    queue = registry.list_cases(scope=SupportCaseScope.SYSTEM, statuses=(SupportCaseStatus.TRIAGED,))
    assert tuple(item.case_id for item in queue) == (case.case_id,)
    history = registry.list_events(case_id=case.case_id, scope=SupportCaseScope.SYSTEM)
    assert tuple(item.to_status for item in history) == (SupportCaseStatus.OPEN, SupportCaseStatus.TRIAGED)
    assert database[CASE_COLLECTION].count_documents({"case_id": case.case_id}) == 1
    assert database[EVENT_COLLECTION].count_documents({"case_id": case.case_id}) == 2
    with pytest.raises(SupportCaseNotFoundError):
        registry.get(case_id=case.case_id, scope=SupportCaseScope.TENANT, tenant_id="tenant-other")


def test_real_mongo_transaction_abort_removes_case_and_event(mongo_case_registry):
    client, database, registry = mongo_case_registry
    case = _case("case-abort-1")
    with client.start_session() as session:
        with pytest.raises(RuntimeError, match="ABORT_CERTIFICATE"):
            with session.start_transaction():
                registry.create(
                    case,
                    _event("event-abort-1", case.case_id, "idem-abort-1", "actor-1", None, SupportCaseStatus.OPEN, "CASE_CREATED", NOW),
                    session=session,
                )
                raise RuntimeError("ABORT_CERTIFICATE")
    assert database[CASE_COLLECTION].count_documents({"case_id": case.case_id}) == 0
    assert database[EVENT_COLLECTION].count_documents({"case_id": case.case_id}) == 0


def test_real_mongo_stale_revision_and_event_replay_are_rejected(mongo_case_registry):
    client, database, registry = mongo_case_registry
    case = _case("case-cas-1")
    with client.start_session() as session:
        with session.start_transaction():
            registry.create(
                case,
                _event("event-cas-open", case.case_id, "idem-cas-open", "actor-1", None, SupportCaseStatus.OPEN, "CASE_CREATED", NOW),
                session=session,
            )
    with client.start_session() as session:
        stale = registry.get(case_id=case.case_id, scope=SupportCaseScope.SYSTEM, session=session)
        with session.start_transaction():
            registry.transition(
                current=stale,
                next_status=SupportCaseStatus.TRIAGED,
                event=_event("event-cas-triage", case.case_id, "idem-cas-triage", "actor-1", SupportCaseStatus.OPEN, SupportCaseStatus.TRIAGED, "CASE_TRIAGED", NOW + timedelta(seconds=1)),
                expected_revision=0,
                session=session,
            )
        with session.start_transaction():
            with pytest.raises(SupportCaseConflictError, match="SYSTEM_SERVICES_CASE_CONCURRENT_TRANSITION"):
                registry.transition(
                    current=stale,
                    next_status=SupportCaseStatus.TRIAGED,
                    event=_event("event-cas-replay", case.case_id, "idem-cas-replay", "actor-2", SupportCaseStatus.OPEN, SupportCaseStatus.TRIAGED, "CASE_TRIAGED", NOW + timedelta(seconds=2)),
                    expected_revision=0,
                    session=session,
                )
    assert database[CASE_COLLECTION].count_documents({"case_id": case.case_id}) == 1
    assert database[EVENT_COLLECTION].count_documents({"case_id": case.case_id}) == 2



def test_canonical_eos_startup_registers_case_indexes_and_readiness(monkeypatch):
    client: MongoClient[Any] = MongoClient(
        os.environ[URI_ENV],
        serverSelectionTimeoutMS=3000,
    )
    database_name = "wilsy_system_services_startup_" + uuid.uuid4().hex
    database = client[database_name]
    monkeypatch.setattr(server, "connect_db", lambda: (True, "CERT"))
    monkeypatch.setattr(server, "get_database", lambda: database)
    monkeypatch.setattr(server, "get_client", lambda: client)
    monkeypatch.setattr(server, "disconnect_db", lambda: None)
    monkeypatch.setenv("WILSY_DUNNING_SCHEDULER_ENABLED", "false")
    app = server.WilsyAPIServer(reasoning_provider_binding=None).get_app()

    try:
        with TestClient(app):
            assert app.state.system_services_case_indexes_ready is True
            case_indexes = list(database[CASE_COLLECTION].list_indexes())
            event_indexes = list(database[EVENT_COLLECTION].list_indexes())
            assert any(index.get("name") == "system_service_case_identity_unique" for index in case_indexes)
            assert any(index.get("name") == "system_service_case_scope_status_created" for index in case_indexes)
            assert any(index.get("name") == "system_service_case_event_identity_unique" for index in event_indexes)
            assert any(index.get("name") == "system_service_case_event_idempotency_unique" for index in event_indexes)
            assert any(index.get("name") == "system_service_case_actor_idempotency_unique" for index in event_indexes)
        assert app.state.system_services_case_indexes_ready is False
    finally:
        client.drop_database(database_name)
        client.close()


class _DenySystemAuthorizer:
    def require(self, *, principal_id, permission_id, session):
        raise PermissionError("SYSTEM_IAM_DENIED")


def test_self_service_case_is_principal_bound_and_idempotent(mongo_case_registry):
    client, database, registry = mongo_case_registry
    service = SupportCaseApplicationService(
        registry=registry,
        authorizer=_DenySystemAuthorizer(),
        clock=lambda: NOW,
    )
    actor = SupportCaseActorContext(
        principal_id="principal-self-service",
        scope=SupportCaseScope.TENANT,
        tenant_id="tenant-self",
    )
    with client.start_session() as session:
        with session.start_transaction():
            created = service.create_own_case(
                actor=actor,
                category=SupportCaseCategory.PASSWORD_RECOVERY,
                idempotency_key="self-service-request-001",
                session=session,
            )
    with client.start_session() as session:
        with session.start_transaction():
            replay = service.create_own_case(
                actor=actor,
                category=SupportCaseCategory.PASSWORD_RECOVERY,
                idempotency_key="self-service-request-001",
                session=session,
            )
    assert replay.case_id == created.case_id
    assert database[CASE_COLLECTION].count_documents({"case_id": created.case_id}) == 1
    own = service.list_own_cases(actor=actor)
    assert tuple(item.case_id for item in own) == (created.case_id,)
    other_actor = SupportCaseActorContext(
        principal_id="principal-other",
        scope=SupportCaseScope.TENANT,
        tenant_id="tenant-self",
    )
    assert service.list_own_cases(actor=other_actor) == ()
    with pytest.raises(SupportCaseApplicationError, match="CASE_NOT_OWNED_BY_ACTOR"):
        service.read_own_case_history(actor=other_actor, case_id=created.case_id)


def test_tenant_self_service_cannot_read_system_queue(mongo_case_registry):
    _, _, registry = mongo_case_registry
    service = SupportCaseApplicationService(
        registry=registry,
        authorizer=_DenySystemAuthorizer(),
        clock=lambda: NOW,
    )
    actor = SupportCaseActorContext(
        principal_id="tenant-principal",
        scope=SupportCaseScope.TENANT,
        tenant_id="tenant-a",
    )
    with pytest.raises(SupportCaseApplicationError, match="SYSTEM_SERVICES_SCOPE_REQUIRED"):
        service.list_system_queue(actor=actor)



def test_authenticated_tenant_self_service_http_binds_current_membership_and_principal(
    mongo_case_registry, monkeypatch
):
    """Real-replica-set HTTP proof for tenant/principal binding and fail-closed admission."""
    client, database, registry = mongo_case_registry
    principal_id = "principal-self-service-http"
    tenant_id = "tenant-self-service-http"
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 1),
        collection=database["principal_authorities"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal_id, tenant_id, TenantMembershipStatus.ACTIVE, 1
        ),
        collection=database["tenant_memberships"],
    )

    class MembershipReader:
        def resolve(self, requested_principal, requested_tenant, *, session=None):
            return TenantMembershipRepository.resolve(
                requested_principal,
                requested_tenant,
                collection=database["tenant_memberships"],
                session=session,
            )

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from tools.eos.api.auth_router import get_current_identity
    from tools.eos.api import system_services_router
    from tools.eos.auth.identity import SovereignIdentity

    app = FastAPI()
    app.include_router(system_services_router.router, prefix="/api")
    app.state.system_services_case_indexes_ready = True
    app.state.system_services_case_registry = registry
    app.dependency_overrides[get_current_identity] = lambda: SovereignIdentity(
        identity_id=principal_id,
        tenant_id="untrusted-token-tenant",
        username=None,
        email=None,
        auth_method="CERTIFICATION",
        status=PrincipalStatus.ACTIVE,
        session_reference=None,
    )
    monkeypatch.setattr(system_services_router, "get_client", lambda: client)
    monkeypatch.setattr("tools.eos.kernel.db.get_database", lambda: database)
    monkeypatch.setattr(
        system_services_router,
        "get_tenant_membership_repository",
        lambda: MembershipReader(),
    )

    with TestClient(app) as http:
        denied = http.post(
            "/api/system-services/self-service/cases",
            headers={"X-Tenant-ID": "tenant-forged", "Idempotency-Key": "http-denied-1"},
            json={"category": "PASSWORD_RECOVERY"},
        )
        created = http.post(
            "/api/system-services/self-service/cases",
            headers={"X-Tenant-ID": tenant_id, "Idempotency-Key": "http-create-1"},
            json={"category": "PASSWORD_RECOVERY"},
        )
        listed = http.get(
            "/api/system-services/self-service/cases",
            headers={"X-Tenant-ID": tenant_id},
        )
        detail = http.get(
            f"/api/system-services/self-service/cases/{created.json()['caseId']}",
            headers={"X-Tenant-ID": tenant_id},
        )
        history = http.get(
            f"/api/system-services/self-service/cases/{created.json()['caseId']}/events",
            headers={"X-Tenant-ID": tenant_id},
        )
        forged_body = http.post(
            "/api/system-services/self-service/cases",
            headers={"X-Tenant-ID": tenant_id, "Idempotency-Key": "http-forged-2"},
            json={"category": "PASSWORD_RECOVERY", "principal_id": "victim"},
        )

    assert denied.status_code == 403
    assert created.status_code == 201
    assert listed.status_code == 200 and len(listed.json()) == 1
    assert detail.status_code == 200
    assert history.status_code == 200 and len(history.json()) == 1
    assert forged_body.status_code == 422
    assert database[CASE_COLLECTION].count_documents(
        {"tenant_id": "tenant-forged"}
    ) == 0
    assert database[CASE_COLLECTION].count_documents(
        {"tenant_id": tenant_id, "principal_id": principal_id}
    ) == 1
