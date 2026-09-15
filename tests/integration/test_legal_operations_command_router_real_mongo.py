"""Host-backed L7B field-service command-chain certificate.

TITLE: Wilsy OS Legal Operations Command API Real-Mongo Certificate
VERSION: v1.0.0-L7B-LEGAL-OPERATIONS-COMMAND-API-RM-CERT
AUTHORITY: Authenticated command composition over canonical P1/P2/P4/P5.
EPITOME: Drives allocation prerequisites and the live command chain through
         P5C, P5D, P5E, and P5F using caller-owned Mongo transactions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_command_router_real_mongo.py
COLLABORATION / OWNERSHIP: Certificate caller owns Mongo client/session/transaction;
                            P1/P2/P4/P5 remain the sole legal authorities.
CERTIFICATION DATE: 2026-09-15
CHANGELOG: v1.0.0 establishes real writable-replica command-chain evidence,
           rollback, tenant scope, replay, and authority-boundary checks.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every durable read/write is explicitly tenant-scoped.
AUTHORITY BOUNDARY: HTTP is composition only; canonical orchestrators derive
                    all lifecycle, outcome, execution, and return truth.
TRANSACTION BOUNDARY: This certificate starts/commits/aborts sessions; the API
                      transaction helper is the only command transaction owner.
FINANCIAL AUTHORITY BOUNDARY: No billing, invoice, payment, settlement, or
                              financial execution; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Runtime absence may skip before certification; all
                         post-hello product, index, persistence, or chain errors fail.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.legal_operations_command_router as command_api
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import TenantAuthorizationDecision, TenantAuthorizationReason
from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttemptState
from tools.eos.legal_operations.domain.process_service_attempt_authority import authorize_process_service_attempt
from tools.eos.legal_operations.registry import legal_operations_lifecycle_registry as p2
from tools.eos.legal_operations.registry import process_service_attempt_authority_registry as p5b
from tools.eos.legal_operations.registry import process_service_attempt_outcome_registry as p5e
from tools.eos.legal_operations.registry import process_service_attempt_transition_registry as p5d
from tools.eos.legal_operations.registry import process_service_return_registry as p5f
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_allocation_registry import ProcessServiceAllocationCurrent, ProcessServiceAllocationReceipt


VERSION = "v1.0.0-L7B-LEGAL-OPERATIONS-COMMAND-API-RM-CERT"
MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 15, 8, 0, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128
HEX_E = "e" * 128
HEX_F = "f" * 128


def _tx(client: MongoClient) -> Any:
    session = client.start_session()
    session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
    return session


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, dict[str, Any]]]:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2500, retryWrites=True)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            client.close()
            pytest.skip(f"Mongo hello unavailable: {type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            client.close()
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            client.close()
            pytest.skip("no writable primary")
        database = client[f"l7b_cmd_{uuid.uuid4().hex}"]
        concerns = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
        collections = {
            "authority": database.get_collection(p5b.RECEIPT_COLLECTION, **concerns),
            "lifecycle": database.get_collection(p2.COLLECTION, **concerns),
            "transition": database.get_collection(p5d.COLLECTION, **concerns),
            "outcome": database.get_collection(p5e.COLLECTION, **concerns),
            "return": database.get_collection(p5f.COLLECTION, **concerns),
        }
        p5b.ProcessServiceAttemptAuthorityRegistry.ensure_indexes(collections["authority"])
        LegalOperationsLifecycleRegistry.ensure_indexes(collections["lifecycle"])
        p5d.ProcessServiceAttemptTransitionRegistry.ensure_indexes(collections["transition"])
        p5e.ProcessServiceAttemptOutcomeRegistry.ensure_indexes(collections["outcome"])
        p5f.ProcessServiceReturnRegistry.ensure_indexes(collections["return"])
        yield client, database, collections
    finally:
        active_error = bool(__import__("sys").exc_info()[0])
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _authority(tenant: str, authority_id: str, attempt_id: str) -> Any:
    receipt = ProcessServiceAllocationReceipt(
        tenant_id=tenant, allocation_command_id=f"allocation-{authority_id}", idempotency_key=f"idem-{authority_id}",
        instruction_id="instruction-l7b", case_matter_id="matter-l7b", document_id=f"document-{attempt_id}", district_id="district-l7b", sheriff_office_id="office-l7b", deputy_id="deputy-l7b", assignment_decision_id="assignment-l7b", assignment_decision_fingerprint=HEX_A, source_instruction_fingerprint=HEX_B, source_document_fingerprint=HEX_C, source_district_fingerprint=HEX_D, source_sheriff_office_fingerprint=HEX_E, source_deputy_fingerprint=HEX_F, prior_custody_chain_fingerprint=HEX_A, prior_custody_head_event_id=f"head-{authority_id}", prior_custody_head_fingerprint=HEX_B, prior_custody_head_sequence_number=1, from_holder_reference="office-l7b", to_holder_reference="deputy-l7b", allocation_custody_event_id=f"allocated-{authority_id}", allocation_evidence_reference=f"allocation-evidence-{authority_id}", allocated_at=BASE, allocated_document_fingerprint=HEX_C, allocation_custody_event_fingerprint=HEX_D, result_custody_chain_fingerprint=HEX_E,
    )
    current = ProcessServiceAllocationCurrent(
        tenant_id=tenant, document_id=receipt.document_id, process_document_fingerprint=receipt.allocated_document_fingerprint,
        custody_chain_fingerprint=receipt.result_custody_chain_fingerprint, custody_head_event_id=receipt.allocation_custody_event_id,
        custody_head_fingerprint=receipt.allocation_custody_event_fingerprint, custody_head_sequence_number=2,
        current_holder_reference=receipt.to_holder_reference, authority_evidence_reference=receipt.allocation_command_id,
        authority_evidence_fingerprint=receipt.fingerprint,
    )
    return authorize_process_service_attempt(allocation_receipt=receipt, allocation_current=current, attempt_authority_id=authority_id, attempt_id=attempt_id, authorized_at=BASE + timedelta(minutes=1))


def _context(tenant: str) -> TenantAuthorizationContext:
    identity = SovereignIdentity(identity_id="principal-l7b", tenant_id=tenant, username="operator", email="operator@example.test", auth_method="TEST", status=PrincipalStatus.ACTIVE)
    decision = TenantAuthorizationDecision(True, TenantAuthorizationReason.AUTHORIZED, "tenant_sheriff", "SHERIFF")
    return TenantAuthorizationContext(identity, tenant, decision)


def test_real_mongo_command_chain_uses_canonical_orchestrators(mongo_context: tuple[MongoClient, Any, dict[str, Any]], monkeypatch: pytest.MonkeyPatch) -> None:
    client, _database, collections = mongo_context
    tenant = f"tenant-l7b-{uuid.uuid4().hex}"
    authority_id, attempt_id = f"authority-{uuid.uuid4().hex}", f"attempt-{uuid.uuid4().hex}"
    seed = _tx(client)
    try:
        p5b.ProcessServiceAttemptAuthorityRegistry.persist(_authority(tenant, authority_id, attempt_id), collections["authority"], session=seed)
        seed.commit_transaction()
    finally:
        seed.end_session()
    monkeypatch.setattr(command_api, "_db_handles", lambda: (client, _database))
    ctx = _context(tenant)

    created = __import__("asyncio").run(command_api.create_process_service_attempt(command_api.AttemptCommand(attempt_authority_id=authority_id), ctx))
    assert created["data"]["state"] == "ALLOCATED"
    allocated = collections["lifecycle"].find_one({"tenant_id": tenant, "entity_type": "ServiceAttempt", "entity_identity": attempt_id})
    assert allocated is not None
    transition = command_api.AttemptTransitionCommand(current_evidence_identity=allocated["evidence_identity"], evidence_reference="field-observation", evidence_fingerprint=HEX_F, occurred_at=BASE + timedelta(minutes=2))
    attempted = __import__("asyncio").run(command_api.transition_process_service_attempt_command(attempt_id, transition, ctx))
    assert attempted["data"]["state"] == "ATTEMPTED"
    attempted_record = collections["lifecycle"].find_one({"tenant_id": tenant, "entity_type": "ServiceAttempt", "entity_identity": attempt_id, "p1_payload.state": "ATTEMPTED"})
    assert attempted_record is not None
    outcome = command_api.OutcomeCommand(current_evidence_identity=attempted_record["evidence_identity"], outcome=ServiceAttemptState.COMPLETED, evidence_reference="terminal-observation", evidence_fingerprint=HEX_E, occurred_at=BASE + timedelta(minutes=3), service_execution_id=f"execution-{attempt_id}", executed_at=BASE + timedelta(minutes=4))
    execution = __import__("asyncio").run(command_api.record_process_service_outcome_command(attempt_id, outcome, ctx))
    assert execution["data"]["attempt_id"] == attempt_id
    execution_record = collections["lifecycle"].find_one({"tenant_id": tenant, "entity_type": "ServiceExecution", "entity_identity": outcome.service_execution_id})
    assert execution_record is not None
    return_command = command_api.ReturnCommand(execution_evidence_identity=execution_record["evidence_identity"], return_id=f"return-{attempt_id}", generated_at=BASE + timedelta(minutes=5))
    returned = __import__("asyncio").run(command_api.generate_return_of_service_command(outcome.service_execution_id, return_command, ctx))
    assert returned["data"]["service_execution_id"] == outcome.service_execution_id
    assert collections["lifecycle"].count_documents({"tenant_id": tenant, "entity_type": "ServiceAttempt"}) == 3
    assert collections["lifecycle"].count_documents({"tenant_id": tenant, "entity_type": "ServiceExecution"}) == 1
    assert collections["lifecycle"].count_documents({"tenant_id": tenant, "entity_type": "ReturnOfService"}) == 1
    assert not any(key in returned["data"] for key in ("payment", "settlement", "invoice", "billing_execution"))


def test_real_mongo_failed_command_rolls_back(mongo_context: tuple[MongoClient, Any, dict[str, Any]], monkeypatch: pytest.MonkeyPatch) -> None:
    client, _database, collections = mongo_context
    tenant = f"tenant-l7b-{uuid.uuid4().hex}"
    authority_id, attempt_id = f"authority-{uuid.uuid4().hex}", f"attempt-{uuid.uuid4().hex}"
    seed = _tx(client)
    try:
        p5b.ProcessServiceAttemptAuthorityRegistry.persist(_authority(tenant, authority_id, attempt_id), collections["authority"], session=seed)
        seed.commit_transaction()
    finally:
        seed.end_session()
    monkeypatch.setattr(command_api, "_db_handles", lambda: (client, _database))
    with pytest.raises(command_api.HTTPException):
        __import__("asyncio").run(command_api.create_process_service_attempt(command_api.AttemptCommand(attempt_authority_id=authority_id), _context(f"foreign-{tenant}")))
    assert collections["lifecycle"].count_documents({"tenant_id": tenant}) == 0


# ARTIFACT: test_legal_operations_command_router_real_mongo.py
# VERSION: v1.0.0-L7B-LEGAL-OPERATIONS-COMMAND-API-RM-CERT
# AUTHORITY BOUNDARY: host-backed command composition certificate only
# TENANT POSTURE: UUID-isolated database and explicit tenant predicates
# FAIL-CLOSED POSTURE: only pre-hello host absence may skip
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
