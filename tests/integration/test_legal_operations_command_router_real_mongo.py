"""L7B host-backed live HTTP, IAM, and P4A-to-P5F certificate.

TITLE: Wilsy OS Legal Operations Command API Real-Mongo Certificate
VERSION: v1.4.0-L8-6G-SERVER-OWNED-FIELD-SEQUENCE-RM-CERT
AUTHORITY: Host-backed certificate for authenticated command composition.
EPITOME: Prove actual FastAPI POST dispatch, durable IAM resolution, live P4A
         allocation, canonical P5A/P5B bridging, the P5C-P5F command chain, and
         bound-Deputy P5M->P5D/P5E field command composition.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_command_router_real_mongo.py
COLLABORATION / OWNERSHIP: The certificate owns only fixtures and observations;
                            P1/P2/P4/P5 remain canonical authorities.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.4.0-L8-6G-SERVER-OWNED-FIELD-SEQUENCE-RM-CERT proves live deputy HTTP bodies omit P5M
           sequence lineage while the server derives durable sequence 1 then 2
           and preserves immutable prior-event chaining for the same device.
           2026-09-23 v1.3.0-L8-6E-DEPUTY-FIELD-COMMAND-BRIDGE-RM-CERT adds live tenant_deputy IAM, immutable L8-6B
           binding, P5M journal persistence, server-derived field provenance,
           atomic deputy transition/outcome commands, and same-tenant wrong-deputy denial.
           v1.2.0-L8-1-SPLIT-IAM-COMMAND-CHAIN-RM-CERT migrates the
           certificate fixture to canonical tenant_business_roles plus
           role_assignments and overrides the composed HTTP role reader rather
           than the retired single-store provider seam.
           v1.1.0 proved actual FastAPI POST transport, live
           RequireTenantAuthorization over durable principal/membership/
           business-role/granting-role truth, live P4A allocation, canonical
           P5A/P5B bridge, P5C/P5D/P5E/P5F commands, and rollback/denial safety.
           v1.0.0 established direct command-function host evidence only.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic UUID-scoped identifiers; no secrets,
                            provider calls, or caller-asserted authority claims.
TENANT BOUNDARY: Every durable read and write is explicitly tenant-scoped;
                 foreign scope is denied before legal persistence.
AUTHORITY BOUNDARY: HTTP composes canonical P1/P2/P4/P5 authorities only;
                    the certificate never creates legal, IAM, or financial truth.
TRANSACTION BOUNDARY: The API owns command session/transaction mechanics;
                      P1/P2/P4/P5 orchestrators and registries never do.
FINANCIAL AUTHORITY BOUNDARY: No invoice, payment, settlement, or financial
                              execution is created; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Only pre-yield hello/setName/writable-primary absence
                         may skip. Index, persistence, IAM, transport, lineage,
                         rollback, and product failures fail this certificate.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.legal_operations_command_router as command_api
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    DocumentCustodyEvent,
    DocumentCustodyEventType,
    District,
    Deputy,
    LegalInstruction,
    LegalInstructionState,
    ProcessDocument,
    ProcessDocumentState,
    ServiceAttemptState,
    SheriffOffice,
)
from tools.eos.legal_operations.domain.process_service_attempt_authority import authorize_process_service_attempt
from tools.eos.legal_operations.orchestration.deputy_principal_binding_orchestrator import bind_deputy_principal_identity
from tools.eos.legal_operations.registry import legal_operations_lifecycle_registry as p2
from tools.eos.legal_operations.registry import process_service_attempt_authority_registry as p5b
from tools.eos.legal_operations.registry import process_service_attempt_outcome_registry as p5e
from tools.eos.legal_operations.registry import process_service_attempt_transition_registry as p5d
from tools.eos.legal_operations.registry import process_service_return_registry as p5f
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    COLLECTION as DEPUTY_PRINCIPAL_BINDING_COLLECTION,
    DeputyPrincipalBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_field_evidence_registry import (
    COLLECTION as FIELD_EVIDENCE_COLLECTION,
    ProcessServiceFieldEvidenceRegistry,
)
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ALLOCATION_CURRENT_COLLECTION,
    ALLOCATION_RECEIPT_COLLECTION,
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationRegistry,
    get_current,
    get_receipt_by_idempotency_key,
)


VERSION = "v1.3.0-L8-6E-DEPUTY-FIELD-COMMAND-BRIDGE-RM-CERT"
DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 15, 8, 0, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128


@dataclass(frozen=True)
class _Fixture:
    tenant: str
    principal_id: str
    instruction: LegalInstruction
    document: ProcessDocument
    district: District
    office: SheriffOffice
    deputy: Deputy
    prior_events: tuple[DocumentCustodyEvent, ...]
    expected_current: ProcessServiceAllocationCurrent
    source_identities: dict[str, str]
    command: dict[str, Any]


class _PrincipalReader:
    """Resolve durable principal truth through the canonical repository."""

    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        return PrincipalAuthorityRepository.get(principal_id, self._collection, session=session)


class _MembershipReader:
    """Resolve durable tenant membership truth through the canonical repository."""

    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def resolve(self, principal_id: str, tenant_id: str, *, session: Any = None) -> Any:
        return TenantMembershipRepository.resolve(principal_id, tenant_id, self._collection, session=session)


class _RoleReader:
    """Resolve business and granting roles from their canonical split stores."""

    def __init__(
        self,
        authorization_collection: Any,
        business_collection: Any,
    ) -> None:
        self._authorization_collection = authorization_collection
        self._business_collection = business_collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> Any:
        if role_id in TENANT_ROLES:
            try:
                value = TenantBusinessRoleRepository.resolve(
                    principal_id,
                    tenant_id,
                    self._business_collection,
                    session=session,
                )
            except TenantBusinessRoleNotFoundError as error:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                ) from error
            except TenantBusinessRoleRepositoryError as error:
                raise RoleAssignmentRepositoryError(
                    "TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
                ) from error
            if value.business_role != role_id:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                )
            return value

        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self._authorization_collection,
            session=session,
        )


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield an isolated majority/journaled database after live host gating."""
    client = MongoClient(
        os.getenv("TEST_VENDOR_MONGO_URI", DEFAULT_URI),
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
    )
    database: Any = None
    active_error = False
    cleanup_error: BaseException | None = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"host Mongo unavailable during hello: {type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")
        database = client.get_database(
            f"l7b_live_{uuid4().hex}",
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        collections = {
            "lifecycle": database.get_collection(p2.COLLECTION),
            "allocation_receipts": database.get_collection(ALLOCATION_RECEIPT_COLLECTION),
            "allocation_current": database.get_collection(ALLOCATION_CURRENT_COLLECTION),
            "attempt_authority": database.get_collection(p5b.RECEIPT_COLLECTION),
            "attempt_transition": database.get_collection(p5d.COLLECTION),
            "attempt_outcome": database.get_collection(p5e.COLLECTION),
            "return": database.get_collection(p5f.COLLECTION),
            "principal": database.get_collection("principal_authorities"),
            "membership": database.get_collection("tenant_memberships"),
            "roles": database.get_collection("role_assignments"),
            "business_roles": database.get_collection("tenant_business_roles"),
            "bindings": database.get_collection(DEPUTY_PRINCIPAL_BINDING_COLLECTION),
            "field_evidence": database.get_collection(FIELD_EVIDENCE_COLLECTION),
        }
        LegalOperationsLifecycleRegistry.ensure_indexes(collections["lifecycle"])
        ProcessServiceAllocationRegistry.ensure_indexes(collections["allocation_receipts"], collections["allocation_current"])
        p5b.ProcessServiceAttemptAuthorityRegistry.ensure_indexes(collections["attempt_authority"])
        p5d.ProcessServiceAttemptTransitionRegistry.ensure_indexes(collections["attempt_transition"])
        p5e.ProcessServiceAttemptOutcomeRegistry.ensure_indexes(collections["attempt_outcome"])
        p5f.ProcessServiceReturnRegistry.ensure_indexes(collections["return"])
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        RoleAssignmentRepository.ensure_indexes(collections["roles"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business_roles"])
        DeputyPrincipalBindingRegistry.ensure_indexes(collections["bindings"])
        ProcessServiceFieldEvidenceRegistry.ensure_indexes(collections["field_evidence"])
        yield {"client": client, "database": database, "collections": collections}
    except BaseException:
        active_error = True
        raise
    finally:
        if database is not None:
            try:
                client.drop_database(database.name)
            except BaseException as error:  # pragma: no cover - host cleanup only
                cleanup_error = error
        client.close()
        if cleanup_error is not None and not active_error:
            raise cleanup_error


def _chain_fingerprint(tenant_id: str, document_id: str, events: tuple[DocumentCustodyEvent, ...]) -> str:
    """Mirror the canonical P4A custody-chain digest for fixture currentness."""
    payload = {
        "schema": "WILSY-PROCESS-SERVICE-CUSTODY-CHAIN/V1",
        "tenant_id": tenant_id,
        "document_id": document_id,
        "event_fingerprints": [event.fingerprint for event in events],
    }
    return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _p2_identity(collection: Any, tenant: str, entity_type: str, entity_identity: str) -> str:
    """Resolve one exact P2 evidence identity after canonical persistence."""
    row = collection.find_one({"tenant_id": tenant, "entity_type": entity_type, "entity_identity": entity_identity})
    assert row is not None
    value = row.get("evidence_identity")
    assert isinstance(value, str) and len(value) == 128
    return value


def _seed_fixture(collections: dict[str, Any], *, business_role: str = "tenant_sheriff", grant_role: str = "SHERIFF") -> _Fixture:
    """Persist P1/P2 prerequisites, IAM truth, and the test-only P4 currentness seed."""
    suffix = uuid4().hex
    tenant = f"tenant-l7b-{suffix}"
    principal_id = f"principal-l7b-{suffix}"
    instruction_id, matter_id = f"instruction-{suffix}", f"matter-{suffix}"
    document_id, district_id = f"document-{suffix}", f"district-{suffix}"
    office_id, deputy_id = f"office-{suffix}", f"deputy-{suffix}"
    instruction = LegalInstruction(tenant, instruction_id, matter_id, document_id, BASE, "instruction-registration").transition_to(
        LegalInstructionState.ACCEPTED, evidence_reference="instruction-acceptance", occurred_at=BASE + timedelta(minutes=1)
    )
    document = ProcessDocument(tenant, document_id, matter_id, "summons", BASE, "document-registration").transition_to(
        ProcessDocumentState.RECEIVED, evidence_reference="document-receipt", occurred_at=BASE + timedelta(minutes=1)
    )
    district = District(tenant, district_id, "Central District", "ZA-GP-1", "district-evidence")
    office = SheriffOffice(tenant, office_id, district_id, "Central Office", "office-evidence")
    deputy = Deputy(tenant, deputy_id, office_id, "Deputy One", "badge-1", "deputy-evidence")
    registered = DocumentCustodyEvent(tenant, f"custody-registered-{suffix}", document_id, DocumentCustodyEventType.REGISTERED, BASE, 1, "custody-registration")
    received = DocumentCustodyEvent(tenant, f"custody-received-{suffix}", document_id, DocumentCustodyEventType.RECEIVED_IN_OFFICE, BASE + timedelta(minutes=1), 2, "custody-receipt", "client-holder", office_id)
    prior_events = (registered, received)
    expected_current = ProcessServiceAllocationCurrent(
        tenant_id=tenant, document_id=document_id, process_document_fingerprint=document.fingerprint,
        custody_chain_fingerprint=_chain_fingerprint(tenant, document_id, prior_events), custody_head_event_id=received.custody_event_id,
        custody_head_fingerprint=received.fingerprint, custody_head_sequence_number=2, current_holder_reference=office_id,
        authority_evidence_reference="migration-head", authority_evidence_fingerprint=HEX_A,
    )
    with collections["lifecycle"].database.client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        for value in (instruction, document, district, office, deputy, registered, received):
            LegalOperationsLifecycleRegistry.create(value, collections["lifecycle"], session=session)
        collections["allocation_current"].insert_one(expected_current.to_dict(), session=session)
        PrincipalAuthorityRepository.create(PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0), collections["principal"], session=session)
        TenantMembershipRepository.insert(TenantMembershipAuthority(principal_id, tenant, TenantMembershipStatus.ACTIVE, 0), collections["membership"], session=session)
        TenantBusinessRoleRepository.insert(
            TenantBusinessRoleAuthority(
                principal_id,
                tenant,
                business_role,
                TenantBusinessRoleStatus.ACTIVE,
                0,
                BASE,
                None,
            ),
            collections["business_roles"],
            session=session,
        )
        RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal_id, tenant, grant_role, RoleAssignmentStatus.ACTIVE, 0), collections["roles"], session=session)
        session.commit_transaction()
    source_identities = {
        "instruction": _p2_identity(collections["lifecycle"], tenant, "LegalInstruction", instruction_id),
        "document": _p2_identity(collections["lifecycle"], tenant, "ProcessDocument", document_id),
        "district": _p2_identity(collections["lifecycle"], tenant, "District", district_id),
        "office": _p2_identity(collections["lifecycle"], tenant, "SheriffOffice", office_id),
        "deputy": _p2_identity(collections["lifecycle"], tenant, "Deputy", deputy_id),
    }
    command = {
        "instruction_evidence_identity": source_identities["instruction"], "document_evidence_identity": source_identities["document"],
        "district_evidence_identity": source_identities["district"], "sheriff_office_evidence_identity": source_identities["office"],
        "deputy_evidence_identity": source_identities["deputy"], "assignment_decision_id": f"assignment-{suffix}",
        "assignment_evidence_reference": "assignment-evidence", "decided_at": BASE + timedelta(minutes=2),
        "allocation_command_id": f"allocation-command-{suffix}", "idempotency_key": f"allocation-idempotency-{suffix}",
        "allocation_custody_event_id": f"custody-allocation-{suffix}", "allocation_evidence_reference": "allocation-evidence",
        "allocated_at": BASE + timedelta(minutes=3),
    }
    return _Fixture(tenant, principal_id, instruction, document, district, office, deputy, prior_events, expected_current, source_identities, command)


def _seed_bound_deputy_actor(
    collections: dict[str, Any],
    fixture: _Fixture,
    deputy: Deputy,
) -> str:
    """Persist live deputy IAM plus immutable principal-to-Deputy binding."""
    principal_id = f"principal-deputy-{uuid4().hex}"
    with collections["lifecycle"].database.client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0),
            collections["principal"],
            session=session,
        )
        TenantMembershipRepository.insert(
            TenantMembershipAuthority(
                principal_id,
                fixture.tenant,
                TenantMembershipStatus.ACTIVE,
                0,
            ),
            collections["membership"],
            session=session,
        )
        TenantBusinessRoleRepository.insert(
            TenantBusinessRoleAuthority(
                principal_id,
                fixture.tenant,
                "tenant_deputy",
                TenantBusinessRoleStatus.ACTIVE,
                0,
                BASE,
                None,
            ),
            collections["business_roles"],
            session=session,
        )
        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                principal_id,
                fixture.tenant,
                "DEPUTY",
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            collections["roles"],
            session=session,
        )
        bind_deputy_principal_identity(
            tenant_id=fixture.tenant,
            principal_id=principal_id,
            deputy_id=deputy.deputy_id,
            bound_at=BASE + timedelta(minutes=2),
            evidence_reference=f"binding:{deputy.deputy_id}",
            lifecycle_collection=collections["lifecycle"],
            binding_collection=collections["bindings"],
            principal_collection=collections["principal"],
            membership_collection=collections["membership"],
            business_role_collection=collections["business_roles"],
            role_assignment_collection=collections["roles"],
            session=session,
        )
        session.commit_transaction()
    return principal_id


def _identity_projection(principal_id: str, tenant_id: str) -> SovereignIdentity:
    """Inject authentication identity only; durable authorization is never injected."""
    return SovereignIdentity(identity_id=principal_id, tenant_id=tenant_id, username="operator", email="operator@example.test", auth_method="TEST", status=PrincipalStatus.ACTIVE)


def _app(context: dict[str, Any], fixture: _Fixture, *, principal_id: str | None = None) -> FastAPI:
    """Compose production RequireTenantAuthorization with durable Mongo readers."""
    import tools.eos.api.tenant_authorization_http as authorization_http
    import tools.eos.auth.authentication as authentication
    import tools.eos.auth.tenant_access as tenant_access

    app = FastAPI()
    register_error_handlers(app, debug=False)
    collections = context["collections"]
    app.dependency_overrides[authorization_http.get_current_identity] = lambda: _identity_projection(principal_id or fixture.principal_id, fixture.tenant)
    app.dependency_overrides[authentication.get_principal_authority_repository] = lambda: _PrincipalReader(collections["principal"])
    app.dependency_overrides[tenant_access.get_tenant_membership_repository] = lambda: _MembershipReader(collections["membership"])
    app.dependency_overrides[authorization_http.get_role_assignment_repository] = lambda: _RoleReader(
        collections["roles"],
        collections["business_roles"],
    )
    app.include_router(command_api.router, prefix="/api")
    return app


def _post(context: dict[str, Any], fixture: _Fixture, path: str, payload: dict[str, Any], *, tenant: str | None = None, principal_id: str | None = None) -> Any:
    """Issue one real HTTP POST through FastAPI and production dependencies."""
    body = {key: value.isoformat() if isinstance(value, datetime) else value for key, value in payload.items()}
    with TestClient(_app(context, fixture, principal_id=principal_id)) as client:
        return client.post(path, json=body, headers={"X-Tenant-ID": tenant or fixture.tenant})


def _bridge_actual_p4(context: dict[str, Any], fixture: _Fixture) -> Any:
    """Hydrate actual P4A output and persist the canonical P5A/P5B bridge."""
    collections = context["collections"]
    with context["client"].start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        receipt = get_receipt_by_idempotency_key(fixture.tenant, fixture.document.document_id, fixture.command["idempotency_key"], collections["allocation_receipts"], session=session)
        current = get_current(fixture.tenant, fixture.document.document_id, collections["allocation_current"], session=session)
        assert receipt is not None
        decision = authorize_process_service_attempt(allocation_receipt=receipt, allocation_current=current, attempt_authority_id=f"attempt-authority-{fixture.document.document_id}", attempt_id=f"attempt-{fixture.document.document_id}", authorized_at=BASE + timedelta(minutes=4))
        persisted = p5b.ProcessServiceAttemptAuthorityRegistry.persist(decision, collections["attempt_authority"], session=session)
        session.commit_transaction()
    assert persisted.receipt.allocation_receipt_fingerprint == receipt.fingerprint
    return persisted.receipt


def test_real_mongo_full_http_chain_uses_live_iam_and_actual_p4a(mongo_context: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    """Certify allocation through return using only actual HTTP POST dispatch."""
    monkeypatch.setattr(command_api, "_db_handles", lambda: (mongo_context["client"], mongo_context["database"]))
    fixture = _seed_fixture(mongo_context["collections"])
    allocated = _post(mongo_context, fixture, "/api/legal-operations/allocations", fixture.command)
    assert allocated.status_code == 200, allocated.text
    assert allocated.json()["data"]["state"] == ProcessDocumentState.ALLOCATED_TO_DEPUTY.value
    collections = mongo_context["collections"]
    assert collections["allocation_receipts"].count_documents({"tenant_id": fixture.tenant}) == 1
    assert collections["allocation_current"].find_one({"tenant_id": fixture.tenant, "document_id": fixture.document.document_id})["custody_head_sequence_number"] == 3
    allocated_row = collections["lifecycle"].find_one({"tenant_id": fixture.tenant, "entity_type": "ProcessDocument", "p1_payload.state": "ALLOCATED_TO_DEPUTY"})
    assert allocated_row is not None
    attempt_receipt = _bridge_actual_p4(mongo_context, fixture)
    attempt = _post(mongo_context, fixture, "/api/legal-operations/attempts", {"attempt_authority_id": attempt_receipt.attempt_authority_id})
    assert attempt.status_code == 200, attempt.text
    assert attempt.json()["data"]["state"] == ServiceAttemptState.ALLOCATED.value
    attempt_row = collections["lifecycle"].find_one({"tenant_id": fixture.tenant, "entity_type": "ServiceAttempt", "p1_payload.state": "ALLOCATED"})
    assert attempt_row is not None
    transition = _post(mongo_context, fixture, f"/api/legal-operations/attempts/{attempt_receipt.attempt_id}/transition", {"current_evidence_identity": attempt_row["evidence_identity"], "evidence_reference": "field-observation", "evidence_fingerprint": HEX_B, "occurred_at": BASE + timedelta(minutes=5)})
    assert transition.status_code == 200, transition.text
    attempted_row = collections["lifecycle"].find_one({"tenant_id": fixture.tenant, "entity_type": "ServiceAttempt", "p1_payload.state": "ATTEMPTED"})
    assert attempted_row is not None
    execution_id = f"execution-{attempt_receipt.attempt_id}"
    outcome = _post(mongo_context, fixture, f"/api/legal-operations/attempts/{attempt_receipt.attempt_id}/outcome", {"current_evidence_identity": attempted_row["evidence_identity"], "outcome": ServiceAttemptState.COMPLETED.value, "evidence_reference": "terminal-observation", "evidence_fingerprint": HEX_C, "occurred_at": BASE + timedelta(minutes=6), "service_execution_id": execution_id, "executed_at": BASE + timedelta(minutes=7)})
    assert outcome.status_code == 200, outcome.text
    execution_row = collections["lifecycle"].find_one({"tenant_id": fixture.tenant, "entity_type": "ServiceExecution", "entity_identity": execution_id})
    assert execution_row is not None and execution_row["source_payload"]["attempt"]["state"] == ServiceAttemptState.COMPLETED.value
    returned = _post(mongo_context, fixture, f"/api/legal-operations/executions/{execution_id}/return", {"execution_evidence_identity": execution_row["evidence_identity"], "return_id": f"return-{attempt_receipt.attempt_id}", "generated_at": BASE + timedelta(minutes=8)})
    assert returned.status_code == 200, returned.text
    assert collections["lifecycle"].count_documents({"tenant_id": fixture.tenant, "entity_type": "ProcessDocument"}) == 2
    assert collections["lifecycle"].count_documents({"tenant_id": fixture.tenant, "entity_type": "DocumentCustodyEvent"}) == 3
    assert collections["lifecycle"].count_documents({"tenant_id": fixture.tenant, "entity_type": "ServiceAttempt"}) == 3
    assert collections["lifecycle"].count_documents({"tenant_id": fixture.tenant, "entity_type": "ServiceExecution"}) == 1
    assert collections["lifecycle"].count_documents({"tenant_id": fixture.tenant, "entity_type": "ReturnOfService"}) == 1
    for collection_name in ("lifecycle", "allocation_receipts", "attempt_authority", "attempt_transition", "attempt_outcome", "return"):
        for row in collections[collection_name].find({"tenant_id": fixture.tenant}):
            assert not any(field in row for field in ("payment", "settlement", "paid_state", "refund", "invoice", "billing_execution"))


def test_real_mongo_bound_deputy_field_bridge(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Certify live bound-Deputy P5M->P5D/P5E composition and wrong-deputy denial."""
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (mongo_context["client"], mongo_context["database"]),
    )
    monkeypatch.setattr(
        command_api,
        "_utcnow",
        lambda: BASE + timedelta(minutes=20),
    )
    collections = mongo_context["collections"]
    fixture = _seed_fixture(collections)

    allocated = _post(
        mongo_context,
        fixture,
        "/api/legal-operations/allocations",
        fixture.command,
    )
    assert allocated.status_code == 200, allocated.text
    attempt_receipt = _bridge_actual_p4(mongo_context, fixture)
    created = _post(
        mongo_context,
        fixture,
        "/api/legal-operations/attempts",
        {"attempt_authority_id": attempt_receipt.attempt_authority_id},
    )
    assert created.status_code == 200, created.text

    deputy_principal = _seed_bound_deputy_actor(
        collections,
        fixture,
        fixture.deputy,
    )
    allocated_row = collections["lifecycle"].find_one(
        {
            "tenant_id": fixture.tenant,
            "entity_type": "ServiceAttempt",
            "p1_payload.state": "ALLOCATED",
        }
    )
    assert allocated_row is not None

    transition_payload = {
        "current_evidence_identity": allocated_row["evidence_identity"],
        "device_id": "device-live-1",
        "event_id": "field-event-live-1",
        "occurred_at": BASE + timedelta(minutes=5),
        "observation_reference": "photo:live-attempt",
    }
    transitioned = _post(
        mongo_context,
        fixture,
        f"/api/legal-operations/deputy/attempts/{attempt_receipt.attempt_id}/transition",
        transition_payload,
        principal_id=deputy_principal,
    )
    assert transitioned.status_code == 200, transitioned.text
    transition_body = transitioned.json()
    assert transition_body["data"]["state"] == ServiceAttemptState.ATTEMPTED.value
    field_one = transition_body["field_evidence"]
    assert field_one["event_id"] == "field-event-live-1"
    assert field_one["sequence_number"] == 1
    assert len(field_one["evidence_fingerprint"]) == 128
    assert collections["field_evidence"].count_documents(
        {"tenant_id": fixture.tenant}
    ) == 1

    attempted_row = collections["lifecycle"].find_one(
        {
            "tenant_id": fixture.tenant,
            "entity_type": "ServiceAttempt",
            "p1_payload.state": "ATTEMPTED",
        }
    )
    assert attempted_row is not None
    outcome_payload = {
        "current_evidence_identity": attempted_row["evidence_identity"],
        "device_id": "device-live-1",
        "event_id": "field-event-live-2",
        "occurred_at": BASE + timedelta(minutes=6),
        "observation_reference": "photo:live-terminal",
        "outcome": ServiceAttemptState.COMPLETED.value,
    }
    outcome = _post(
        mongo_context,
        fixture,
        f"/api/legal-operations/deputy/attempts/{attempt_receipt.attempt_id}/outcome",
        outcome_payload,
        principal_id=deputy_principal,
    )
    assert outcome.status_code == 200, outcome.text
    outcome_body = outcome.json()
    assert outcome_body["field_evidence"]["event_id"] == "field-event-live-2"
    assert outcome_body["field_evidence"]["sequence_number"] == 2
    second_durable = collections["field_evidence"].find_one(
        {
            "tenant_id": fixture.tenant,
            "event_id": "field-event-live-2",
        }
    )
    assert second_durable is not None
    assert (
        second_durable["command_payload"]["previous_event_fingerprint"]
        == field_one["evidence_fingerprint"]
    )
    execution_id = outcome_body["data"]["service_execution_id"]
    assert isinstance(execution_id, str) and len(execution_id) == 128
    execution_row = collections["lifecycle"].find_one(
        {
            "tenant_id": fixture.tenant,
            "entity_type": "ServiceExecution",
            "entity_identity": execution_id,
        }
    )
    assert execution_row is not None
    assert execution_row["p1_payload"]["executed_at"] == (
        BASE + timedelta(minutes=6)
    ).isoformat()
    assert collections["field_evidence"].count_documents(
        {"tenant_id": fixture.tenant}
    ) == 2

    other_deputy = Deputy(
        fixture.tenant,
        f"other-deputy-{uuid4().hex}",
        fixture.office.sheriff_office_id,
        "Deputy Two",
        "badge-2",
        "deputy-evidence-2",
    )
    LegalOperationsLifecycleRegistry.create(
        other_deputy,
        collections["lifecycle"],
    )
    other_principal = _seed_bound_deputy_actor(
        collections,
        fixture,
        other_deputy,
    )
    before_journal = collections["field_evidence"].count_documents(
        {"tenant_id": fixture.tenant}
    )
    denied = _post(
        mongo_context,
        fixture,
        f"/api/legal-operations/attempts/{attempt_receipt.attempt_id}/transition",
        {
            "current_evidence_identity": allocated_row["evidence_identity"],
            "evidence_reference": "forbidden-cross-deputy",
            "evidence_fingerprint": HEX_A,
            "occurred_at": BASE + timedelta(minutes=5),
        },
        principal_id=other_principal,
    )
    assert denied.status_code == 404, denied.text
    assert collections["field_evidence"].count_documents(
        {"tenant_id": fixture.tenant}
    ) == before_journal


def test_real_mongo_live_iam_denials_and_p4_rollback(mongo_context: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    """Prove live IAM denials precede legal writes and corrupt P4 rolls back."""
    monkeypatch.setattr(command_api, "_db_handles", lambda: (mongo_context["client"], mongo_context["database"]))
    collections = mongo_context["collections"]
    denial_cases: list[tuple[str, _Fixture, str]] = []
    fixture = _seed_fixture(collections)
    denial_cases.append(("cross-tenant", fixture, f"foreign-{uuid4().hex}"))
    fixture = _seed_fixture(collections)
    RoleAssignmentRepository.compare_and_swap(RoleAssignmentAuthority(fixture.principal_id, fixture.tenant, "SHERIFF", RoleAssignmentStatus.REVOKED, 1), 0, collections["roles"])
    denial_cases.append(("revoked-grant", fixture, fixture.tenant))
    fixture = _seed_fixture(collections)
    PrincipalAuthorityRepository.compare_and_swap(PrincipalAuthority(fixture.principal_id, PrincipalStatus.SUSPENDED, 1), 0, collections["principal"])
    denial_cases.append(("inactive-principal", fixture, fixture.tenant))
    fixture = _seed_fixture(collections)
    TenantMembershipRepository.compare_and_swap(TenantMembershipAuthority(fixture.principal_id, fixture.tenant, TenantMembershipStatus.SUSPENDED, 1), 0, collections["membership"])
    denial_cases.append(("inactive-membership", fixture, fixture.tenant))
    fixture = _seed_fixture(collections, business_role="tenant_legal_client", grant_role="LEGAL_CLIENT")
    denial_cases.append(("client-role", fixture, fixture.tenant))
    fixture = _seed_fixture(collections, business_role="tenant_deputy", grant_role="DEPUTY")
    denial_cases.append(("least-authority-deputy-allocation", fixture, fixture.tenant))
    for label, scenario, request_tenant in denial_cases:
        before = collections["lifecycle"].count_documents({"tenant_id": scenario.tenant})
        response = _post(mongo_context, scenario, "/api/legal-operations/allocations", scenario.command, tenant=request_tenant)
        assert response.status_code == 403, (label, response.text)
        assert collections["lifecycle"].count_documents({"tenant_id": scenario.tenant}) == before

    rollback = _seed_fixture(collections)
    collections["allocation_current"].update_one({"tenant_id": rollback.tenant, "document_id": rollback.document.document_id}, {"$set": {"process_document_fingerprint": HEX_C}})
    before_lifecycle = collections["lifecycle"].count_documents({"tenant_id": rollback.tenant})
    failed = _post(mongo_context, rollback, "/api/legal-operations/allocations", rollback.command)
    assert failed.status_code == 503, failed.text
    assert failed.json()["detail"] == "LEGAL_OPERATIONS_UNAVAILABLE"
    assert collections["lifecycle"].count_documents({"tenant_id": rollback.tenant}) == before_lifecycle
    assert collections["allocation_receipts"].count_documents({"tenant_id": rollback.tenant}) == 0
    assert collections["lifecycle"].count_documents({"tenant_id": rollback.tenant, "p1_payload.state": "ALLOCATED_TO_DEPUTY"}) == 0
    assert collections["lifecycle"].count_documents({"tenant_id": rollback.tenant, "entity_type": "DocumentCustodyEvent", "p1_payload.event_type": "ALLOCATED_TO_DEPUTY"}) == 0


# ARTIFACT: test_legal_operations_command_router_real_mongo.py
# VERSION: v1.4.0-L8-6G-SERVER-OWNED-FIELD-SEQUENCE-RM-CERT
# AUTHORITY BOUNDARY: host-backed actual HTTP/IAM/composition certificate only
# TENANT POSTURE: UUID-isolated database, split durable IAM stores, and explicit tenant predicates
# FAIL-CLOSED POSTURE: only pre-yield host absence may skip
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT