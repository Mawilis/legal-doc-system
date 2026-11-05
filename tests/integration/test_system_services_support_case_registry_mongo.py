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
from tools.eos.auth.current_system_permission_possession import CurrentSystemPermissionPossessionResolver
from tools.eos.auth.system_permission_assignment import SystemPermissionAssignment, SystemPermissionAssignmentStatus
from tools.eos.auth.system_permission_assignment_registry import SystemPermissionAssignmentRegistry
from tools.eos.auth.system_permission_command_evidence import (
    SystemPermissionCommandEvidence,
    SystemPermissionCommandOperation,
)
from tools.eos.auth.system_permission_revocation_command_service import SystemPermissionRevocationCommandService
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.system_services.support_case_registry import (
    CASE_COLLECTION,
    EVENT_COLLECTION,
    SupportCaseConflictError,
    SupportCaseNotFoundError,
    SupportCaseRegistry,
)
from tools.eos.system_services.security_incident_response_decision import (
    SecurityIncidentResponseAction,
    SecurityIncidentResponseDecision,
    SecurityIncidentResponseDecisionStatus,
)
from tools.eos.system_services.security_incident_response_decision_registry import (
    COLLECTION as RESPONSE_DECISION_COLLECTION,
    EVENT_COLLECTION as RESPONSE_DECISION_EVENT_COLLECTION,
    PLATFORM_AUDIT_COLLECTION,
    PLATFORM_OUTBOX_COLLECTION,
    SecurityIncidentResponseDecisionRegistry,
    SecurityIncidentResponseDecisionConflictError,
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
    response_decision_registry = SecurityIncidentResponseDecisionRegistry(
        decisions=database[RESPONSE_DECISION_COLLECTION],
        events=database[RESPONSE_DECISION_EVENT_COLLECTION],
        audit_events=database[PLATFORM_AUDIT_COLLECTION],
        outbox=database[PLATFORM_OUTBOX_COLLECTION],
    )
    response_decision_registry.ensure_indexes()
    try:
        yield client, database, registry, response_decision_registry
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
    client, database, registry, _ = mongo_case_registry
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
    client, database, registry, _ = mongo_case_registry
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
    client, database, registry, _ = mongo_case_registry
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
            assert app.state.system_services_incident_indexes_ready is True
            from tools.eos.system_services.security_incident_registry import (
                COLLECTION as SECURITY_INCIDENT_COLLECTION,
                EVENT_COLLECTION as SECURITY_INCIDENT_EVENT_COLLECTION,
            )
            from tools.eos.system_services.security_incident_assignment_registry import (
                COLLECTION as SECURITY_INCIDENT_ASSIGNMENT_COLLECTION,
                EVENT_COLLECTION as SECURITY_INCIDENT_ASSIGNMENT_EVENT_COLLECTION,
            )
            assignment_indexes = list(database[SECURITY_INCIDENT_ASSIGNMENT_COLLECTION].list_indexes())
            assignment_event_indexes = list(database[SECURITY_INCIDENT_ASSIGNMENT_EVENT_COLLECTION].list_indexes())
            assert any(index.get("name") == "incident_assignment_identity_unique" for index in assignment_indexes)
            assert any(index.get("name") == "incident_assignment_one_owner_unique" for index in assignment_indexes)
            assert any(index.get("name") == "incident_assignment_event_identity_unique" for index in assignment_event_indexes)
            incident_indexes = list(database[SECURITY_INCIDENT_COLLECTION].list_indexes())
            incident_event_indexes = list(database[SECURITY_INCIDENT_EVENT_COLLECTION].list_indexes())
            assert any(index.get("name") == "security_incident_identity_unique" for index in incident_indexes)
            assert any(index.get("name") == "security_incident_reporter_idempotency_unique" for index in incident_indexes)
            assert any(index.get("name") == "security_incident_event_identity_unique" for index in incident_event_indexes)
            assert any(index.get("name") == "security_incident_initial_event_unique" for index in incident_event_indexes)
            case_indexes = list(database[CASE_COLLECTION].list_indexes())
            event_indexes = list(database[EVENT_COLLECTION].list_indexes())
            assert any(index.get("name") == "system_service_case_identity_unique" for index in case_indexes)
            assert any(index.get("name") == "system_service_case_scope_status_created" for index in case_indexes)
            assert any(index.get("name") == "system_service_case_event_identity_unique" for index in event_indexes)
            assert any(index.get("name") == "system_service_case_event_idempotency_unique" for index in event_indexes)
            assert any(index.get("name") == "system_service_case_actor_idempotency_unique" for index in event_indexes)
        assert app.state.system_services_case_indexes_ready is False
        assert app.state.system_services_incident_indexes_ready is False
        assert app.state.system_services_assignment_indexes_ready is False
    finally:
        client.drop_database(database_name)
        client.close()


class _DenySystemAuthorizer:
    def require(self, *, principal_id, permission_id, session):
        raise PermissionError("SYSTEM_IAM_DENIED")


def test_self_service_case_is_principal_bound_and_idempotent(mongo_case_registry):
    client, database, registry, _ = mongo_case_registry
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
    same_principal_other_tenant = SupportCaseActorContext(
        principal_id="principal-self-service",
        scope=SupportCaseScope.TENANT,
        tenant_id="tenant-self-other",
    )
    with client.start_session() as session:
        with session.start_transaction():
            other_tenant_case = service.create_own_case(
                actor=same_principal_other_tenant,
                category=SupportCaseCategory.PASSWORD_RECOVERY,
                idempotency_key="self-service-request-001",
                session=session,
            )
    assert other_tenant_case.case_id != created.case_id
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
    _, _, registry, _ = mongo_case_registry
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
    client, database, registry, _ = mongo_case_registry
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
    other_principal_id = "principal-self-service-http-other"
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(other_principal_id, PrincipalStatus.ACTIVE, 1),
        collection=database["principal_authorities"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            other_principal_id, tenant_id, TenantMembershipStatus.ACTIVE, 1
        ),
        collection=database["tenant_memberships"],
    )
    active_principal = {"id": principal_id}

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
        identity_id=active_principal["id"],
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
        active_principal["id"] = other_principal_id
        cross_principal_detail = http.get(
            f"/api/system-services/self-service/cases/{created.json()['caseId']}",
            headers={"X-Tenant-ID": tenant_id},
        )
        cross_principal_history = http.get(
            f"/api/system-services/self-service/cases/{created.json()['caseId']}/events",
            headers={"X-Tenant-ID": tenant_id},
        )
        active_principal["id"] = principal_id
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
    assert cross_principal_detail.status_code == 404
    assert cross_principal_history.status_code == 404
    assert forged_body.status_code == 422
    assert database[CASE_COLLECTION].count_documents(
        {"tenant_id": "tenant-forged"}
    ) == 0
    assert database[CASE_COLLECTION].count_documents(
        {"tenant_id": tenant_id, "principal_id": principal_id}
    ) == 1



def test_authenticated_security_incident_intake_is_sanitized_append_only_and_idempotent(
    mongo_case_registry, monkeypatch
):
    """Replica-set proof for distinct incident intake, ownership and durable event."""
    client, database, case_registry, _ = mongo_case_registry
    principal_id = "principal-security-incident-http"
    tenant_id = "tenant-security-incident-http"
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
                requested_principal, requested_tenant,
                collection=database["tenant_memberships"], session=session,
            )

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from tools.eos.api.auth_router import get_current_identity
    from tools.eos.api import system_services_router
    from tools.eos.auth.identity import SovereignIdentity
    from tools.eos.system_services.security_incident_registry import (
        COLLECTION, EVENT_COLLECTION, PLATFORM_AUDIT_COLLECTION,
        PLATFORM_OUTBOX_COLLECTION, SecurityIncidentRegistry,
    )

    incident_registry = SecurityIncidentRegistry(
        incidents=database[COLLECTION], events=database[EVENT_COLLECTION]
    )
    incident_registry.ensure_indexes()
    app = FastAPI()
    app.include_router(system_services_router.router, prefix="/api")
    app.state.system_services_case_indexes_ready = True
    app.state.system_services_case_registry = case_registry
    app.state.system_services_incident_indexes_ready = True
    app.state.system_services_incident_registry = incident_registry
    app.dependency_overrides[get_current_identity] = lambda: SovereignIdentity(
        identity_id=principal_id, tenant_id="untrusted-token-tenant",
        username=None, email=None, auth_method="CERTIFICATION",
        status=PrincipalStatus.ACTIVE, session_reference=None,
    )
    monkeypatch.setattr(system_services_router, "get_client", lambda: client)
    monkeypatch.setattr("tools.eos.kernel.db.get_database", lambda: database)
    monkeypatch.setattr(
        system_services_router, "get_tenant_membership_repository",
        lambda: MembershipReader(),
    )

    payload = {
        "category": "SUSPECTED_ACCOUNT_COMPROMISE",
        "observed_at": "2026-11-05T08:00:00+00:00",
    }
    headers = {
        "X-Tenant-ID": tenant_id,
        "Idempotency-Key": "security-incident-intake-001",
    }
    with TestClient(app) as http:
        first = http.post(
            "/api/system-services/self-service/security-incidents",
            headers=headers, json=payload,
        )
        replay = http.post(
            "/api/system-services/self-service/security-incidents",
            headers=headers, json=payload,
        )
        own = http.get(
            "/api/system-services/self-service/security-incidents",
            headers={"X-Tenant-ID": tenant_id},
        )
        secret_attempt = http.post(
            "/api/system-services/self-service/security-incidents",
            headers={**headers, "Idempotency-Key": "security-incident-secret-001"},
            json={**payload, "password": "must-never-be-accepted"},
        )

    assert first.status_code == 201
    assert replay.status_code == 201
    assert first.json()["incidentId"] == replay.json()["incidentId"]
    assert own.status_code == 200 and len(own.json()) == 1
    assert secret_attempt.status_code == 422
    assert database[COLLECTION].count_documents(
        {"tenant_id": tenant_id, "reporter_principal_id": principal_id}
    ) == 1
    assert database[EVENT_COLLECTION].count_documents(
        {"event_type": "INCIDENT_REPORTED"}
    ) == 1
    assert database[PLATFORM_AUDIT_COLLECTION].count_documents({"target_id": first.json()["incidentId"]}) == 1
    assert database[PLATFORM_OUTBOX_COLLECTION].count_documents({"target_id": first.json()["incidentId"], "status": "PENDING"}) == 1
    persisted = database[COLLECTION].find_one({"tenant_id": tenant_id})
    assert persisted is not None
    assert "password" not in persisted and "secret" not in persisted



def test_security_incident_registry_rolls_back_incident_and_event_together(
    mongo_case_registry,
):
    """A failed caller transaction must leave neither incident nor initial event."""
    from datetime import datetime, timezone
    from tools.eos.system_services.security_incident import (
        SecurityIncident, SecurityIncidentCategory, SecurityIncidentEvent,
    )
    from tools.eos.system_services.security_incident_registry import (
        COLLECTION, EVENT_COLLECTION, PLATFORM_AUDIT_COLLECTION,
        PLATFORM_OUTBOX_COLLECTION, SecurityIncidentRegistry,
    )

    client, database, _, _ = mongo_case_registry
    registry = SecurityIncidentRegistry(
        incidents=database[COLLECTION], events=database[EVENT_COLLECTION]
    )
    registry.ensure_indexes()
    now = datetime(2026, 11, 5, 8, tzinfo=timezone.utc)
    incident = SecurityIncident(
        incident_id="incident-atomicity-certificate",
        tenant_id="tenant-atomicity-certificate",
        reporter_principal_id="principal-atomicity-certificate",
        idempotency_fingerprint="a" * 64,
        category=SecurityIncidentCategory.SUSPECTED_ACCOUNT_COMPROMISE,
        observed_at=now,
        received_at=now,
    )
    event = SecurityIncidentEvent(
        event_id="incident-event-atomicity-certificate",
        incident_id=incident.incident_id,
        tenant_id=incident.tenant_id,
        actor_principal_id=incident.reporter_principal_id,
        event_type="INCIDENT_REPORTED",
        occurred_at=now,
        fingerprint="b" * 64,
    )
    with client.start_session() as session:
        with pytest.raises(RuntimeError, match="INCIDENT_ABORT_CERTIFICATE"):
            with session.start_transaction():
                persisted = registry.create_or_replay(incident, event, session=session)
                registry.record_platform_audit(incident=persisted, event=event, session=session)
                raise RuntimeError("INCIDENT_ABORT_CERTIFICATE")
    assert database[COLLECTION].count_documents(
        {"incident_id": incident.incident_id}
    ) == 0
    assert database[EVENT_COLLECTION].count_documents(
        {"incident_id": incident.incident_id}
    ) == 0
    assert database[PLATFORM_AUDIT_COLLECTION].count_documents({"target_id": incident.incident_id}) == 0
    assert database[PLATFORM_OUTBOX_COLLECTION].count_documents({"target_id": incident.incident_id}) == 0



def test_incident_responder_assignment_requires_separate_permissions_and_acceptance(
    mongo_case_registry,
):
    """Replica-set proof for independent assignment, replay and responder-only acceptance."""
    from datetime import datetime, timezone
    from tools.eos.system_services.security_incident import (
        SecurityIncident, SecurityIncidentCategory, SecurityIncidentEvent,
    )
    from tools.eos.system_services.security_incident_registry import (
        COLLECTION as INCIDENTS, EVENT_COLLECTION as INCIDENT_EVENTS,
        SecurityIncidentRegistry,
    )
    from tools.eos.system_services.security_incident_assignment_registry import (
        COLLECTION as ASSIGNMENTS, EVENT_COLLECTION as ASSIGNMENT_EVENTS,
        SecurityIncidentAssignmentRegistry,
    )
    from tools.eos.system_services.security_incident_escalation_service import (
        SecurityIncidentEscalationService,
        SecurityIncidentEscalationError,
    )

    client, database, _, _ = mongo_case_registry
    now = datetime(2026, 11, 5, 8, tzinfo=timezone.utc)
    incidents = SecurityIncidentRegistry(
        incidents=database[INCIDENTS], events=database[INCIDENT_EVENTS]
    )
    assignments = SecurityIncidentAssignmentRegistry(
        assignments=database[ASSIGNMENTS], events=database[ASSIGNMENT_EVENTS]
    )
    incidents.ensure_indexes()
    assignments.ensure_indexes()
    reporter = "incident-reporter-001"
    triage_actor = "incident-triage-001"
    responder = "incident-responder-001"
    incident = SecurityIncident(
        incident_id="incident-assignment-certificate",
        tenant_id="tenant-assignment-certificate",
        reporter_principal_id=reporter,
        idempotency_fingerprint="c" * 64,
        category=SecurityIncidentCategory.SUSPECTED_ACCOUNT_COMPROMISE,
        observed_at=now,
        received_at=now,
    )
    incident_event = SecurityIncidentEvent(
        event_id="incident-event-assignment-certificate",
        incident_id=incident.incident_id,
        tenant_id=incident.tenant_id,
        actor_principal_id=reporter,
        event_type="INCIDENT_REPORTED",
        occurred_at=now,
        fingerprint="d" * 64,
    )
    with client.start_session() as session:
        with session.start_transaction():
            incidents.create_or_replay(incident, incident_event, session=session)

    class CurrentPermissionAuthorizer:
        def __init__(self):
            self.calls = []
        def require(self, *, principal_id, permission_id, session):
            self.calls.append((principal_id, permission_id))
            allowed = {
                (triage_actor, "system_services:case:triage"),
                (triage_actor, "system_services:incident:escalate"),
                (responder, "system_services:incident:escalate"),
            }
            if (principal_id, permission_id) not in allowed:
                raise PermissionError("CURRENT_SYSTEM_PERMISSION_REQUIRED")

    authorizer = CurrentPermissionAuthorizer()
    service = SecurityIncidentEscalationService(
        incidents=incidents, assignments=assignments,
        authorizer=authorizer, clock=lambda: now,
    )
    with client.start_session() as session:
        with session.start_transaction():
            created = service.assign(
                actor_principal_id=triage_actor,
                assigned_to_principal_id=responder,
                incident_id=incident.incident_id,
                idempotency_key="assignment-create-001",
                session=session,
            )
    with client.start_session() as session:
        with session.start_transaction():
            replay = service.assign(
                actor_principal_id=triage_actor,
                assigned_to_principal_id=responder,
                incident_id=incident.incident_id,
                idempotency_key="assignment-create-001",
                session=session,
            )
    assert replay.assignment_id == created.assignment_id
    with client.start_session() as session:
        with session.start_transaction():
            responder_inbox = service.list_my_assignments(
                actor_principal_id=responder, session=session,
            )
    assert tuple(item.assignment_id for item in responder_inbox) == (created.assignment_id,)
    with client.start_session() as session:
        with session.start_transaction():
            assigned_record, assigned_incident = service.read_my_assignment(
                actor_principal_id=responder,
                assignment_id=created.assignment_id,
                session=session,
            )
    assert assigned_record.assignment_id == created.assignment_id
    assert assigned_incident.incident_id == incident.incident_id
    assert authorizer.calls.count((triage_actor, "system_services:case:triage")) == 2
    assert authorizer.calls.count((responder, "system_services:incident:escalate")) == 4

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(SecurityIncidentEscalationError, match="RESPONDER_ONLY"):
                service.accept(
                    actor_principal_id=triage_actor,
                    assignment_id=created.assignment_id,
                    expected_revision=0,
                    idempotency_key="assignment-wrong-actor",
                    session=session,
                )
            session.abort_transaction()

    with client.start_session() as session:
        with session.start_transaction():
            accepted = service.accept(
                actor_principal_id=responder,
                assignment_id=created.assignment_id,
                expected_revision=0,
                idempotency_key="assignment-accept-001",
                session=session,
            )
    assert accepted.status.value == "ACCEPTED"
    assert accepted.revision == 1
    assert database[ASSIGNMENTS].count_documents({"assignment_id": created.assignment_id}) == 1
    assert database[ASSIGNMENT_EVENTS].count_documents({"assignment_id": created.assignment_id}) == 2
    from tools.eos.system_services.security_incident_assignment_registry import (
        PLATFORM_AUDIT_COLLECTION, PLATFORM_OUTBOX_COLLECTION,
    )
    audit_rows = list(database[PLATFORM_AUDIT_COLLECTION].find({"target_id": created.assignment_id}))
    outbox_rows = list(database[PLATFORM_OUTBOX_COLLECTION].find({"target_id": created.assignment_id}))
    assert {row["event_type"] for row in audit_rows} == {
        "INCIDENT_RESPONDER_ASSIGNED", "INCIDENT_ASSIGNMENT_ACCEPTED",
    }
    assert len(outbox_rows) == 2
    assert all(row["status"] == "PENDING" and row["attempts"] == 0 for row in outbox_rows)
    assert {row["event_key"] for row in audit_rows} == {row["event_key"] for row in outbox_rows}


def test_incident_assignment_platform_audit_and_outbox_roll_back_with_business_write(mongo_case_registry):
    """Replica-set proof that business state, immutable audit, and outbox share one transaction."""
    from datetime import datetime, timezone
    from tools.eos.system_services.security_incident_assignment import (
        SecurityIncidentAssignment, SecurityIncidentAssignmentEvent,
        SecurityIncidentAssignmentStatus,
    )
    from tools.eos.system_services.security_incident_assignment_registry import (
        COLLECTION, EVENT_COLLECTION, PLATFORM_AUDIT_COLLECTION,
        PLATFORM_OUTBOX_COLLECTION, SecurityIncidentAssignmentRegistry,
    )

    client, database, _, _ = mongo_case_registry
    registry = SecurityIncidentAssignmentRegistry(
        assignments=database[COLLECTION], events=database[EVENT_COLLECTION],
    )
    registry.ensure_indexes()
    now = datetime(2026, 11, 5, 9, tzinfo=timezone.utc)
    assignment = SecurityIncidentAssignment(
        assignment_id="assignment-audit-rollback-certificate",
        incident_id="incident-audit-rollback-certificate",
        tenant_id="tenant-audit-rollback-certificate",
        reporter_principal_id="reporter-audit-rollback",
        assigned_by_principal_id="triage-audit-rollback",
        assigned_to_principal_id="responder-audit-rollback",
        status=SecurityIncidentAssignmentStatus.PENDING_ACCEPTANCE,
        revision=0, created_at=now, updated_at=now,
        idempotency_fingerprint="e" * 64,
    )
    event = SecurityIncidentAssignmentEvent(
        event_id="assignment-event-audit-rollback-certificate",
        assignment_id=assignment.assignment_id,
        actor_principal_id=assignment.assigned_by_principal_id,
        idempotency_fingerprint="f" * 64,
        from_status=None,
        to_status=SecurityIncidentAssignmentStatus.PENDING_ACCEPTANCE,
        action="INCIDENT_RESPONDER_ASSIGNED",
        occurred_at=now,
    )
    with client.start_session() as session:
        with pytest.raises(RuntimeError, match="SYSTEM_SERVICES_AUDIT_ABORT_CERTIFICATE"):
            with session.start_transaction():
                persisted = registry.create(assignment, event, session=session)
                registry.record_platform_audit(
                    assignment=persisted, event=event, session=session,
                )
                raise RuntimeError("SYSTEM_SERVICES_AUDIT_ABORT_CERTIFICATE")
    for collection in (COLLECTION, EVENT_COLLECTION, PLATFORM_AUDIT_COLLECTION, PLATFORM_OUTBOX_COLLECTION):
        assert database[collection].count_documents({}) == 0



def _response_decision(decision_id: str) -> SecurityIncidentResponseDecision:
    return SecurityIncidentResponseDecision(
        decision_id=decision_id,
        incident_id="incident-response-1",
        tenant_id="tenant-response-1",
        target_principal_id="principal-target-1",
        action=SecurityIncidentResponseAction.PASSWORD_RESET,
        requested_by_principal_id="principal-responder-1",
        requested_at=NOW,
        request_evidence_reference="incident-evidence-response-1",
    )


def test_real_mongo_response_decision_approval_and_audit_are_atomic(mongo_case_registry):
    client, database, _, decision_registry = mongo_case_registry
    request = _response_decision("decision-commit-1")
    with client.start_session() as session:
        with session.start_transaction():
            decision_registry.create(request, session=session)
            approved = decision_registry.decide(
                request.decision_id,
                approved=True,
                decided_by_principal_id="principal-independent-approver",
                decided_at=NOW + timedelta(minutes=1),
                decision_evidence_reference="governance-approval-1",
                expected_revision=0,
                session=session,
            )
    assert approved.status is SecurityIncidentResponseDecisionStatus.APPROVED
    assert approved.revision == 1
    assert database[RESPONSE_DECISION_COLLECTION].count_documents({"decision_id": request.decision_id}) == 1
    assert database[RESPONSE_DECISION_EVENT_COLLECTION].count_documents({"decision_id": request.decision_id}) == 2
    assert database[PLATFORM_AUDIT_COLLECTION].count_documents({"target_id": request.decision_id}) == 2
    assert database[PLATFORM_OUTBOX_COLLECTION].count_documents({"target_id": request.decision_id, "status": "PENDING"}) == 2


def test_real_mongo_response_decision_rejects_stale_and_self_approval(mongo_case_registry):
    client, database, _, decision_registry = mongo_case_registry
    request = _response_decision("decision-cas-1")
    with client.start_session() as session:
        with session.start_transaction():
            decision_registry.create(request, session=session)
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(SecurityIncidentResponseDecisionConflictError, match="INDEPENDENT_DECISION_MAKER_REQUIRED"):
                decision_registry.decide(
                    request.decision_id,
                    approved=True,
                    decided_by_principal_id=request.requested_by_principal_id,
                    decided_at=NOW + timedelta(minutes=1),
                    decision_evidence_reference="self-approval",
                    expected_revision=0,
                    session=session,
                )
    with client.start_session() as session:
        with session.start_transaction():
            decision_registry.decide(
                request.decision_id,
                approved=False,
                decided_by_principal_id="principal-independent-approver",
                decided_at=NOW + timedelta(minutes=1),
                decision_evidence_reference="governance-rejection-1",
                expected_revision=0,
                session=session,
            )
        with session.start_transaction():
            with pytest.raises(SecurityIncidentResponseDecisionConflictError, match="DECISION_REVISION_CONFLICT"):
                decision_registry.decide(
                    request.decision_id,
                    approved=True,
                    decided_by_principal_id="principal-second-approver",
                    decided_at=NOW + timedelta(minutes=2),
                    decision_evidence_reference="late-approval",
                    expected_revision=0,
                    session=session,
                )
    assert database[RESPONSE_DECISION_COLLECTION].find_one({"decision_id": request.decision_id})["status"] == "REJECTED"
    assert database[RESPONSE_DECISION_EVENT_COLLECTION].count_documents({"decision_id": request.decision_id}) == 2


def test_real_mongo_response_decision_rollback_removes_projection_events_and_outbox(mongo_case_registry):
    client, database, _, decision_registry = mongo_case_registry
    request = _response_decision("decision-abort-1")
    with client.start_session() as session:
        with pytest.raises(RuntimeError, match="RESPONSE_DECISION_ABORT"):
            with session.start_transaction():
                decision_registry.create(request, session=session)
                decision_registry.decide(
                    request.decision_id,
                    approved=True,
                    decided_by_principal_id="principal-independent-approver",
                    decided_at=NOW + timedelta(minutes=1),
                    decision_evidence_reference="governance-approval-abort",
                    expected_revision=0,
                    session=session,
                )
                raise RuntimeError("RESPONSE_DECISION_ABORT")
    assert database[RESPONSE_DECISION_COLLECTION].count_documents({"decision_id": request.decision_id}) == 0
    assert database[RESPONSE_DECISION_EVENT_COLLECTION].count_documents({"decision_id": request.decision_id}) == 0
    assert database[PLATFORM_AUDIT_COLLECTION].count_documents({"target_id": request.decision_id}) == 0
    assert database[PLATFORM_OUTBOX_COLLECTION].count_documents({"target_id": request.decision_id}) == 0



def _approved_revocation_decision(decision_id: str) -> SecurityIncidentResponseDecision:
    return SecurityIncidentResponseDecision(
        decision_id=decision_id,
        incident_id="incident-response-execution-1",
        tenant_id="tenant-response-1",
        target_principal_id="principal-target-1",
        action=SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION,
        requested_by_principal_id="principal-independent-requester",
        requested_at=NOW,
        request_evidence_reference="incident-evidence-response-execution-1",
        target_assignment_id="assignment-target-privileged-1",
        target_permission_id="privileged_activation:issue",
    )


def _persist_approved_decision(client: Any, registry: SecurityIncidentResponseDecisionRegistry, decision: SecurityIncidentResponseDecision) -> SecurityIncidentResponseDecision:
    with client.start_session() as session:
        with session.start_transaction():
            registry.create(decision, session=session)
            return registry.decide(
                decision.decision_id,
                approved=True,
                decided_by_principal_id="principal-independent-approver",
                decided_at=NOW + timedelta(minutes=1),
                decision_evidence_reference="independent-approval:" + decision.decision_id,
                expected_revision=0,
                session=session,
            )


def test_real_mongo_canonical_execution_evidence_audit_outbox_and_replay_are_atomic(mongo_case_registry):
    client, database, _, registry = mongo_case_registry
    decision = _approved_revocation_decision("decision-execution-commit")
    approved = _persist_approved_decision(client, registry, decision)
    occurred_at = NOW + timedelta(minutes=2)
    with client.start_session() as session:
        with session.start_transaction():
            recorded = registry.record_execution(
                decision=approved,
                actor_principal_id="principal-independent-executor",
                idempotency_key="canonical-revocation-execution-commit",
                occurred_at=occurred_at,
                result_status="REVOKED",
                result_revision=2,
                session=session,
            )
    with client.start_session() as session:
        with session.start_transaction():
            found = registry.find_execution(
                decision=approved,
                actor_principal_id="principal-independent-executor",
                idempotency_key="canonical-revocation-execution-commit",
                session=session,
            )
            assert found == recorded
            replayed = registry.record_execution(
                decision=approved,
                actor_principal_id="principal-independent-executor",
                idempotency_key="canonical-revocation-execution-commit",
                occurred_at=occurred_at,
                result_status="REVOKED",
                result_revision=2,
                session=session,
            )
            assert replayed == recorded
    event_key = "system-services-response-execution:" + decision.decision_id + ":revision:2"
    event = database[RESPONSE_DECISION_EVENT_COLLECTION].find_one(
        {"decision_id": decision.decision_id, "revision": 2}
    )
    assert event is not None
    assert event["event_type"] == "SECURITY_INCIDENT_RESPONSE_EXECUTED"
    assert event["actor_principal_id"] == "principal-independent-executor"
    assert event["execution_idempotency_fingerprint"]
    assert database[PLATFORM_AUDIT_COLLECTION].count_documents({"event_key": event_key}) == 1
    assert database[PLATFORM_OUTBOX_COLLECTION].count_documents({
        "event_key": event_key, "status": "PENDING", "attempts": 0,
    }) == 1
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(SecurityIncidentResponseDecisionConflictError, match="RESPONSE_EXECUTION_REPLAY_CONFLICT"):
                registry.find_execution(
                    decision=approved,
                    actor_principal_id="principal-independent-executor",
                    idempotency_key="different-execution-key",
                    session=session,
                )


def test_real_mongo_execution_evidence_rollback_preserves_approved_decision(mongo_case_registry):
    client, database, _, registry = mongo_case_registry
    decision = _approved_revocation_decision("decision-execution-abort")
    approved = _persist_approved_decision(client, registry, decision)
    event_key = "system-services-response-execution:" + decision.decision_id + ":revision:2"
    with client.start_session() as session:
        with pytest.raises(RuntimeError, match="RESPONSE_EXECUTION_ABORT"):
            with session.start_transaction():
                registry.record_execution(
                    decision=approved,
                    actor_principal_id="principal-independent-executor",
                    idempotency_key="canonical-revocation-execution-abort",
                    occurred_at=NOW + timedelta(minutes=2),
                    result_status="REVOKED",
                    result_revision=2,
                    session=session,
                )
                raise RuntimeError("RESPONSE_EXECUTION_ABORT")
    persisted = database[RESPONSE_DECISION_COLLECTION].find_one({"decision_id": decision.decision_id})
    assert persisted is not None
    assert persisted["status"] == "APPROVED"
    assert persisted["revision"] == 1
    assert database[RESPONSE_DECISION_EVENT_COLLECTION].count_documents({
        "decision_id": decision.decision_id, "revision": 2,
    }) == 0
    assert database[PLATFORM_AUDIT_COLLECTION].count_documents({"event_key": event_key}) == 0
    assert database[PLATFORM_OUTBOX_COLLECTION].count_documents({"event_key": event_key}) == 0


def test_real_mongo_execution_evidence_rejects_stale_decision_revision(mongo_case_registry):
    client, database, _, registry = mongo_case_registry
    decision = _approved_revocation_decision("decision-execution-stale")
    approved = _persist_approved_decision(client, registry, decision)
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(SecurityIncidentResponseDecisionConflictError, match="RESPONSE_EXECUTION_EVIDENCE_INVALID"):
                registry.record_execution(
                    decision=decision,
                    actor_principal_id="principal-independent-executor",
                    idempotency_key="canonical-revocation-execution-stale",
                    occurred_at=NOW + timedelta(minutes=2),
                    result_status="REVOKED",
                    result_revision=2,
                    session=session,
                )
    assert database[RESPONSE_DECISION_EVENT_COLLECTION].count_documents({
        "decision_id": approved.decision_id, "revision": 2,
    }) == 0


def test_real_mongo_execution_receipt_rejects_non_independent_actor_and_noncanonical_result(mongo_case_registry):
    client, database, _, registry = mongo_case_registry
    decision = _approved_revocation_decision("decision-execution-invalid-actor")
    approved = _persist_approved_decision(client, registry, decision)
    invalid_attempts = (
        ("principal-independent-requester", "REVOKED", 2),
        ("principal-independent-approver", "REVOKED", 2),
        ("principal-target-1", "REVOKED", 2),
        ("principal-independent-executor", "ACTIVE", 2),
        ("principal-independent-executor", "REVOKED", 1),
    )
    for index, (actor, status, revision) in enumerate(invalid_attempts):
        with client.start_session() as session:
            with session.start_transaction():
                with pytest.raises(
                    SecurityIncidentResponseDecisionConflictError,
                    match="RESPONSE_EXECUTION_EVIDENCE_INVALID",
                ):
                    registry.record_execution(
                        decision=approved,
                        actor_principal_id=actor,
                        idempotency_key=f"canonical-revocation-invalid-{index}",
                        occurred_at=NOW + timedelta(minutes=2),
                        result_status=status,
                        result_revision=revision,
                        session=session,
                    )
    assert database[RESPONSE_DECISION_EVENT_COLLECTION].count_documents({
        "decision_id": decision.decision_id, "revision": 2,
    }) == 0


def test_real_mongo_canonical_revocation_and_execution_receipt_rollback_together(mongo_case_registry):
    client, database, _, decision_registry = mongo_case_registry
    target_principal = "principal-response-rollback-target"
    executor_principal = "principal-response-rollback-executor"
    assignment_id = "assignment-response-rollback-target"
    decision_id = "decision-response-canonical-rollback"
    assignment_registry = SystemPermissionAssignmentRegistry(
        database["system_permission_assignments"]
    )
    assignment_registry.ensure_indexes()
    principals = database["principal_authorities"]
    PrincipalAuthorityRepository.ensure_indexes(principals)
    occurred_at = NOW + timedelta(minutes=2)
    decision = SecurityIncidentResponseDecision(
        decision_id=decision_id,
        incident_id="incident-response-canonical-rollback",
        tenant_id="tenant-response-canonical-rollback",
        target_principal_id=target_principal,
        action=SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION,
        requested_by_principal_id="principal-response-rollback-requester",
        requested_at=NOW,
        request_evidence_reference="request-evidence-response-canonical-rollback",
        target_assignment_id=assignment_id,
        target_permission_id="privileged_activation:issue",
    )

    with client.start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(target_principal, PrincipalStatus.ACTIVE, 0),
                principals,
                session=session,
            )
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(executor_principal, PrincipalStatus.ACTIVE, 0),
                principals,
                session=session,
            )
            assignment_registry.create_or_replay(
                SystemPermissionAssignment.assign(
                    assignment_id=assignment_id,
                    principal_id=target_principal,
                    permission_id="privileged_activation:issue",
                    assigned_by_principal_id="independent-iam-issuer",
                    assigned_at=NOW,
                    assignment_evidence_reference="target-assignment-response-rollback",
                ),
                idempotency_key="target-assignment-response-rollback",
                session=session,
            )
            assignment_registry.create_or_replay(
                SystemPermissionAssignment.assign(
                    assignment_id="assignment-response-rollback-executor-revoke",
                    principal_id=executor_principal,
                    permission_id="system_permission_assignment:revoke",
                    assigned_by_principal_id="independent-iam-issuer",
                    assigned_at=NOW,
                    assignment_evidence_reference="executor-revoke-authority-response-rollback",
                ),
                idempotency_key="executor-revoke-authority-response-rollback",
                session=session,
            )
            decision_registry.create(decision, session=session)
            approved = decision_registry.decide(
                decision_id,
                approved=True,
                decided_by_principal_id="principal-response-rollback-approver",
                decided_at=NOW + timedelta(minutes=1),
                decision_evidence_reference="approval-evidence-response-canonical-rollback",
                expected_revision=0,
                session=session,
            )

    possession = CurrentSystemPermissionPossessionResolver(
        principal_collection=principals,
        assignment_registry=assignment_registry,
    )
    revocation = SystemPermissionRevocationCommandService(
        principal_collection=principals,
        possession_resolver=possession,
        assignment_registry=assignment_registry,
    )
    evidence = SystemPermissionCommandEvidence(
        operation=SystemPermissionCommandOperation.REVOKE,
        actor_principal_id=executor_principal,
        target_principal_id=target_principal,
        permission_id="privileged_activation:issue",
        evidence_reference="security-incident-response-decision:" + decision_id,
        occurred_at=occurred_at,
        idempotency_key="execution-response-canonical-rollback",
        assignment_id=assignment_id,
    )
    event_key = "system-services-response-execution:" + decision_id + ":revision:2"

    with client.start_session() as session:
        with pytest.raises(RuntimeError, match="CANONICAL_RESPONSE_EXECUTION_ABORT"):
            with session.start_transaction():
                revoked = revocation.revoke(evidence, session=session)
                assert revoked.status is SystemPermissionAssignmentStatus.REVOKED
                decision_registry.record_execution(
                    decision=approved,
                    actor_principal_id=executor_principal,
                    idempotency_key=evidence.idempotency_key,
                    occurred_at=occurred_at,
                    result_status=revoked.status.value,
                    result_revision=revoked.revision,
                    session=session,
                )
                raise RuntimeError("CANONICAL_RESPONSE_EXECUTION_ABORT")

    history = assignment_registry.get_history(assignment_id)
    assert len(history) == 1
    assert history[0].status is SystemPermissionAssignmentStatus.ACTIVE
    with client.start_session() as session:
        with session.start_transaction():
            persisted_decision = decision_registry.get(decision_id, session=session)
    assert persisted_decision.status is SecurityIncidentResponseDecisionStatus.APPROVED
    assert persisted_decision.revision == 1
    assert database[RESPONSE_DECISION_EVENT_COLLECTION].count_documents({
        "decision_id": decision_id, "revision": 2,
    }) == 0
    assert database[PLATFORM_AUDIT_COLLECTION].count_documents({"event_key": event_key}) == 0
    assert database[PLATFORM_OUTBOX_COLLECTION].count_documents({"event_key": event_key}) == 0
