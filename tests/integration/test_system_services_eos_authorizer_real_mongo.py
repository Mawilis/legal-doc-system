"""Real-Mongo certificate for the composed System Services EOS authorizer."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.auth.current_system_permission_possession import CurrentSystemPermissionPossessionResolver
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.system_permission_assignment import SystemPermissionAssignment
from tools.eos.auth.system_permission_assignment_registry import SystemPermissionAssignmentRegistry
from tools.eos.system_services.eos_authorizer import (
    SystemServicesAuthorizationError,
    SystemServicesEosAuthorizer,
)
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)
from tools.eos.workforce.registry import workforce_relationship_registry as workforce_registry

URI = os.getenv(
    "SYSTEM_SERVICES_CASE_MONGO_URI",
    "mongodb://127.0.0.1:27017/?replicaSet=wilsySystemServicesCaseRS",
)
REPLICA_SET = "wilsySystemServicesCaseRS"
PERMISSION = "system_services:queue:read"
PRINCIPAL = "system-services-staff-001"
PLATFORM_SCOPE = "platform-workforce-cert"
AT = datetime(2026, 11, 3, 12, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000, retryWrites=True)
    hello = client.admin.command("hello")
    assert hello.get("setName") == REPLICA_SET
    assert hello.get("isWritablePrimary") is True
    database_name = "wilsy_system_services_iam_" + uuid4().hex[:16]
    database = client[database_name]
    principal_collection = database["principal_authorities"]
    assignment_collection = database["system_permission_assignments"]
    workforce_collection = database[workforce_registry.COLLECTION_NAME]
    assignment_registry = SystemPermissionAssignmentRegistry(assignment_collection)
    assignment_registry.ensure_indexes()
    workforce_registry.ensure_indexes(workforce_collection)
    possession = CurrentSystemPermissionPossessionResolver(
        principal_collection=principal_collection,
        assignment_registry=assignment_registry,
    )
    authorizer = SystemServicesEosAuthorizer(
        possession_resolver=possession,
        workforce_collection=workforce_collection,
        platform_scope_id=PLATFORM_SCOPE,
        clock=lambda: AT + timedelta(hours=2),
    )
    try:
        yield {
            "client": client,
            "database": database,
            "principal_collection": principal_collection,
            "assignment_collection": assignment_collection,
            "workforce_collection": workforce_collection,
            "assignment_registry": assignment_registry,
            "authorizer": authorizer,
        }
    finally:
        client.drop_database(database_name)
        client.close()


def principal() -> PrincipalAuthority:
    return PrincipalAuthority(PRINCIPAL, PrincipalStatus.ACTIVE, 1)


def assignment() -> SystemPermissionAssignment:
    return SystemPermissionAssignment.assign(
        assignment_id="system-services-assignment-001",
        principal_id=PRINCIPAL,
        permission_id=PERMISSION,
        assigned_by_principal_id="independent-iam-issuer",
        assigned_at=AT,
        assignment_evidence_reference="approved-assignment-evidence-001",
    )


def workforce(status=WorkforceRelationshipStatus.ACTIVE, previous=None, revision=1):
    return WorkforceRelationship(
        relationship_id="system-services-workforce-001",
        revision=revision,
        scope_kind=WorkforceScopeKind.PLATFORM,
        scope_id=PLATFORM_SCOPE,
        principal_id=PRINCIPAL,
        relationship_type=WorkforceRelationshipType.EMPLOYEE,
        status=status,
        effective_from=AT - timedelta(days=10),
        effective_until=None,
        status_effective_at=AT + timedelta(hours=revision - 1),
        reason_reference=f"workforce-evidence-{revision}",
        supersedes_fingerprint=None if previous is None else previous.fingerprint,
    )


def seed_authority(context):
    with context["client"].start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(
                principal(),
                collection=context["principal_collection"],
                session=session,
            )
            context["assignment_registry"].create_or_replay(
                assignment(),
                idempotency_key="system-services-assignment-create",
                session=session,
            )
            workforce_registry.persist_revision(
                workforce(),
                collection=context["workforce_collection"],
                session=session,
            )


def test_real_mongo_active_principal_assignment_and_platform_workforce_allow(mongo_context):
    seed_authority(mongo_context)
    with mongo_context["client"].start_session() as session:
        with session.start_transaction():
            assert mongo_context["authorizer"].require(
                principal_id=PRINCIPAL,
                permission_id=PERMISSION,
                session=session,
            ) is None
            session.abort_transaction()


def test_real_mongo_suspended_platform_workforce_denies(mongo_context):
    seed_authority(mongo_context)
    active = workforce()
    suspended = workforce(
        status=WorkforceRelationshipStatus.SUSPENDED,
        previous=active,
        revision=2,
    )
    with mongo_context["client"].start_session() as session:
        with session.start_transaction():
            workforce_registry.persist_revision(
                suspended,
                collection=mongo_context["workforce_collection"],
                session=session,
            )
    with mongo_context["client"].start_session() as session:
        with session.start_transaction():
            with pytest.raises(SystemServicesAuthorizationError, match="ACTIVE_PLATFORM_WORKFORCE_REQUIRED"):
                mongo_context["authorizer"].require(
                    principal_id=PRINCIPAL,
                    permission_id=PERMISSION,
                    session=session,
                )
            session.abort_transaction()


def test_real_mongo_tenant_workforce_cannot_satisfy_system_authority(mongo_context):
    with mongo_context["client"].start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(
                principal(),
                collection=mongo_context["principal_collection"],
                session=session,
            )
            mongo_context["assignment_registry"].create_or_replay(
                assignment(),
                idempotency_key="system-services-assignment-create",
                session=session,
            )
            tenant_relation = WorkforceRelationship(
                relationship_id="tenant-workforce-only",
                revision=1,
                scope_kind=WorkforceScopeKind.TENANT,
                scope_id=PLATFORM_SCOPE,
                principal_id=PRINCIPAL,
                relationship_type=WorkforceRelationshipType.EMPLOYEE,
                status=WorkforceRelationshipStatus.ACTIVE,
                effective_from=AT - timedelta(days=1),
                effective_until=None,
                status_effective_at=AT - timedelta(days=1),
                reason_reference="tenant-workforce-evidence",
                supersedes_fingerprint=None,
            )
            workforce_registry.persist_revision(
                tenant_relation,
                collection=mongo_context["workforce_collection"],
                session=session,
            )
    with mongo_context["client"].start_session() as session:
        with session.start_transaction():
            with pytest.raises(SystemServicesAuthorizationError, match="ACTIVE_PLATFORM_WORKFORCE_REQUIRED"):
                mongo_context["authorizer"].require(
                    principal_id=PRINCIPAL,
                    permission_id=PERMISSION,
                    session=session,
                )
            session.abort_transaction()


def test_real_mongo_revoked_system_assignment_denies(mongo_context):
    seed_authority(mongo_context)
    active = assignment()
    revoked = active.revoke(
        revoked_by_principal_id="independent-iam-revoker",
        revoked_at=AT + timedelta(minutes=1),
        revocation_evidence_reference="approved-revocation-evidence",
    )
    with mongo_context["client"].start_session() as session:
        with session.start_transaction():
            mongo_context["assignment_registry"].revoke_or_replay(
                revoked,
                revocation_idempotency_key="system-services-assignment-revoke",
                session=session,
            )
    with mongo_context["client"].start_session() as session:
        with session.start_transaction():
            with pytest.raises(SystemServicesAuthorizationError, match="CURRENT_SYSTEM_PERMISSION_REQUIRED"):
                mongo_context["authorizer"].require(
                    principal_id=PRINCIPAL,
                    permission_id=PERMISSION,
                    session=session,
                )
            session.abort_transaction()


def test_real_mongo_system_services_queue_http_uses_current_eos_authority(mongo_context, monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from tools.eos.api.auth_router import get_current_identity
    from tools.eos.api.system_services_router import router
    from tools.eos.auth.identity import SovereignIdentity
    from tools.eos.system_services.support_case_registry import (
        CASE_COLLECTION, EVENT_COLLECTION, SupportCaseRegistry,
    )
    from tools.eos.system_services.security_incident import (
        SecurityIncident, SecurityIncidentCategory, SecurityIncidentEvent,
    )
    from tools.eos.system_services.security_incident_registry import (
        COLLECTION as INCIDENT_COLLECTION,
        EVENT_COLLECTION as INCIDENT_EVENT_COLLECTION,
        SecurityIncidentRegistry,
    )
    from tools.eos.system_services.security_incident_assignment_registry import (
        COLLECTION as ASSIGNMENT_COLLECTION,
        EVENT_COLLECTION as ASSIGNMENT_EVENT_COLLECTION,
        SecurityIncidentAssignmentRegistry,
    )

    seed_authority(mongo_context)
    registry = SupportCaseRegistry(
        cases=mongo_context["database"][CASE_COLLECTION],
        events=mongo_context["database"][EVENT_COLLECTION],
    )
    registry.ensure_indexes()
    incident_registry = SecurityIncidentRegistry(
        incidents=mongo_context["database"][INCIDENT_COLLECTION],
        events=mongo_context["database"][INCIDENT_EVENT_COLLECTION],
    )
    incident_registry.ensure_indexes()
    assignment_registry = SecurityIncidentAssignmentRegistry(
        assignments=mongo_context["database"][ASSIGNMENT_COLLECTION],
        events=mongo_context["database"][ASSIGNMENT_EVENT_COLLECTION],
    )
    assignment_registry.ensure_indexes()
    incident_at = AT
    incident = SecurityIncident(
        incident_id="system-queue-incident-001",
        tenant_id="tenant-incident-001",
        reporter_principal_id="tenant-reporter-001",
        idempotency_fingerprint="e" * 64,
        category=SecurityIncidentCategory.SUSPECTED_ACCOUNT_COMPROMISE,
        observed_at=incident_at,
        received_at=incident_at,
    )
    incident_event = SecurityIncidentEvent(
        event_id="system-queue-incident-event-001",
        incident_id=incident.incident_id,
        tenant_id=incident.tenant_id,
        actor_principal_id=incident.reporter_principal_id,
        event_type="INCIDENT_REPORTED",
        occurred_at=incident_at,
        fingerprint="f" * 64,
    )
    with mongo_context["client"].start_session() as session:
        with session.start_transaction():
            incident_registry.create_or_replay(incident, incident_event, session=session)
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.state.system_services_case_indexes_ready = True
    app.state.system_services_case_registry = registry
    app.state.system_services_incident_indexes_ready = True
    app.state.system_services_incident_registry = incident_registry
    app.state.system_services_assignment_indexes_ready = True
    app.state.system_services_assignment_registry = assignment_registry
    app.state.system_services_authorizer = mongo_context["authorizer"]
    app.dependency_overrides[get_current_identity] = lambda: SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id="ignored-context",
        username=None,
        email=None,
        auth_method="CERTIFICATION",
        status=PrincipalStatus.ACTIVE,
        session_reference=None,
    )
    monkeypatch.setattr(
        "tools.eos.api.system_services_router.get_client",
        lambda: mongo_context["client"],
    )
    with TestClient(app) as http:
        response = http.get("/api/system-services/cases")
        workspace = http.get("/api/system-services/workspace-bootstrap")
        incident_queue = http.get("/api/system-services/security-incidents")
        responder_inbox_denied = http.get("/api/system-services/security-incident-assignments/mine")
    assert incident_queue.status_code == 200
    assert incident_queue.json()[0]["incidentId"] == incident.incident_id
    assert responder_inbox_denied.status_code == 403
    assert response.status_code == 200
    assert response.json() == []
    assert workspace.status_code == 200
    assert workspace.json()["status"] == "READY"
    assert workspace.json()["authority"] == "EOS_SYSTEM_SERVICES"
    assert workspace.json()["principalId"] == PRINCIPAL
    assert workspace.json()["capabilities"] == ["system_services:queue:read"]



def test_real_mongo_incident_assignment_permissions_require_current_platform_workforce(mongo_context):
    """Exact triage and incident-escalation permissions each require current workforce."""
    from tools.eos.auth.system_permission_assignment import SystemPermissionAssignment

    triage_principal = "system-services-triage-incident-001"
    responder_principal = "system-services-incident-responder-001"
    triage_permission = "system_services:case:triage"
    responder_permission = "system_services:incident:escalate"

    def relation(principal_id: str, relation_id: str) -> WorkforceRelationship:
        return WorkforceRelationship(
            relationship_id=relation_id,
            revision=1,
            scope_kind=WorkforceScopeKind.PLATFORM,
            scope_id=PLATFORM_SCOPE,
            principal_id=principal_id,
            relationship_type=WorkforceRelationshipType.EMPLOYEE,
            status=WorkforceRelationshipStatus.ACTIVE,
            effective_from=AT - timedelta(days=10),
            effective_until=None,
            status_effective_at=AT,
            reason_reference=f"workforce-evidence-{relation_id}",
            supersedes_fingerprint=None,
        )

    with mongo_context["client"].start_session() as session:
        with session.start_transaction():
            for principal_id, permission_id, assignment_id in (
                (triage_principal, triage_permission, "incident-triage-permission-assignment"),
                (responder_principal, responder_permission, "incident-responder-permission-assignment"),
            ):
                PrincipalAuthorityRepository.create(
                    PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 1),
                    collection=mongo_context["principal_collection"],
                    session=session,
                )
                mongo_context["assignment_registry"].create_or_replay(
                    SystemPermissionAssignment.assign(
                        assignment_id=assignment_id,
                        principal_id=principal_id,
                        permission_id=permission_id,
                        assigned_by_principal_id="independent-system-iam-issuer",
                        assigned_at=AT,
                        assignment_evidence_reference=f"approved-{assignment_id}",
                    ),
                    idempotency_key=f"idem-{assignment_id}",
                    session=session,
                )
                workforce_registry.persist_revision(
                    relation(principal_id, f"workforce-{assignment_id}"),
                    collection=mongo_context["workforce_collection"],
                    session=session,
                )

    with mongo_context["client"].start_session() as session:
        with session.start_transaction():
            mongo_context["authorizer"].require(
                principal_id=triage_principal,
                permission_id=triage_permission,
                session=session,
            )
            mongo_context["authorizer"].require(
                principal_id=responder_principal,
                permission_id=responder_permission,
                session=session,
            )
            with pytest.raises(SystemServicesAuthorizationError):
                mongo_context["authorizer"].require(
                    principal_id=triage_principal,
                    permission_id=responder_permission,
                    session=session,
                )
            session.abort_transaction()
