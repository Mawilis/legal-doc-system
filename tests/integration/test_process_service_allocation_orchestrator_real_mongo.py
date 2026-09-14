"""Host-backed P4A process-service allocation composition certificate.

TITLE: Wilsy OS Process Service Allocation Orchestrator Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify real Mongo transactional composition of P1 lifecycle evidence,
         P2 immutable snapshots, P4B allocation receipts/currentness, and the
         P4A caller-owned transaction boundary without creating service or
         financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_allocation_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: Direct host-backed P4A certificate. P1 owns legal
                            lifecycle/custody evidence, P2 owns immutable
                            evidence persistence, P3 owns assignment authority,
                            P4B owns receipt/current persistence, and P4A
                            owns composition only. The caller owns Mongo
                            sessions and transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR-REAL-MONGO-CERT
           certifies real index topology, committed creation, replay, abort
           atomicity, durable-current preflight, non-healing partial states,
           tenant isolation, and P4B error preservation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every fixture, query, identity, pointer, and replay is
                 explicitly tenant-scoped; foreign evidence is absent.
AUTHORITY BOUNDARY: Host-backed P4A composition evidence only. A
                    TEST_FIXTURE_ONLY_CURRENTNESS_SEED is test setup, never
                    production bootstrap or authority derivation. No service
                    attempt, execution, return, IAM, or transport authority.
FINANCIAL AUTHORITY BOUNDARY: Allocation evidence is not invoicing, payment,
                              execution, or settlement; Kennel EOS exclusively
                              owns financial execution and settlement.
TRANSACTION BOUNDARY: The certificate starts, commits, and aborts caller
                      sessions around P4A. P4A/P2/P4B never own transactions
                      or a Mongo client.
FAIL-CLOSED DECLARATION: Runtime availability is skipped only before the
                         certificate yield when hello/setName/writable-primary
                         checks fail. Index, persistence, corruption, replay,
                         CAS, or product failures after yield fail the test.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
import sys
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    Deputy,
    District,
    DocumentCustodyEvent,
    DocumentCustodyEventType,
    LegalInstruction,
    LegalInstructionState,
    ProcessDocument,
    ProcessDocumentState,
    SheriffOffice,
)
from tools.eos.legal_operations.domain.process_service_assignment_authority import (
    authorize_process_service_assignment,
)
from tools.eos.legal_operations.orchestration.process_service_allocation_orchestrator import (
    ProcessServiceAllocationOrchestratorInputError,
    ProcessServiceAllocationOrchestratorPartialReplayError,
    orchestrate_process_service_allocation,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
)
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ALLOCATION_CURRENT_COLLECTION,
    ALLOCATION_RECEIPT_COLLECTION,
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationPersistenceOutcome,
    ProcessServiceAllocationRegistry,
    ProcessServiceAllocationRegistryReceiptPointerCorrelationError,
)


VERSION = "v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR-REAL-MONGO-CERT"
DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 9, 0, tzinfo=timezone.utc)
HEX_A = "a" * 128


def _chain_fingerprint(tenant_id: str, document_id: str, events: tuple[DocumentCustodyEvent, ...]) -> str:
    """Mirror the P4A canonical custody-chain digest for fixture currentness."""
    payload = {
        "schema": "WILSY-PROCESS-SERVICE-CUSTODY-CHAIN/V1",
        "tenant_id": tenant_id,
        "document_id": document_id,
        "event_fingerprints": [event.fingerprint for event in events],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha3_512(encoded).hexdigest()


def _p2_identity(value: ProcessDocument | DocumentCustodyEvent) -> str:
    """Derive the exact P2 identity formula used by the frozen P4A module."""
    identity_name = "document_id" if type(value) is ProcessDocument else "custody_event_id"
    payload = {
        "tenant_id": value.tenant_id,
        "entity_type": type(value).__name__,
        "entity_identity": getattr(value, identity_name),
        "p1_fingerprint": value.fingerprint,
        "source_fingerprint": None,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha3_512(encoded).hexdigest()


def _without_mongo_id(document: Any) -> dict[str, Any]:
    """Return one durable document without Mongo's transport-only ``_id``."""
    result = dict(document)
    result.pop("_id", None)
    return result


@dataclass(frozen=True)
class _Fixture:
    tenant: str
    instruction: LegalInstruction
    document: ProcessDocument
    district: District
    office: SheriffOffice
    deputy: Deputy
    decision: Any
    prior_events: tuple[DocumentCustodyEvent, ...]
    expected_current: ProcessServiceAllocationCurrent
    values: dict[str, Any]


def _fixture(tenant: str, suffix: str) -> _Fixture:
    """Build deterministic, production-validated pre-allocation evidence."""
    instruction_id = f"instruction-{suffix}"
    matter_id = f"matter-{suffix}"
    document_id = f"document-{suffix}"
    district_id = f"district-{suffix}"
    office_id = f"office-{suffix}"
    deputy_id = f"deputy-{suffix}"
    instruction = LegalInstruction(
        tenant, instruction_id, matter_id, document_id, BASE, "instruction-registration"
    ).transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="instruction-acceptance",
        occurred_at=BASE + timedelta(minutes=1),
    )
    document = ProcessDocument(
        tenant, document_id, matter_id, "summons", BASE, "document-registration"
    ).transition_to(
        ProcessDocumentState.RECEIVED,
        evidence_reference="document-receipt",
        occurred_at=BASE + timedelta(minutes=1),
    )
    district = District(tenant, district_id, "Central District", "ZA-GP-1", "district-evidence")
    office = SheriffOffice(tenant, office_id, district_id, "Central Office", "office-evidence")
    deputy = Deputy(tenant, deputy_id, office_id, "Deputy One", "badge-1", "deputy-evidence")
    decision = authorize_process_service_assignment(
        instruction=instruction,
        document=document,
        district=district,
        sheriff_office=office,
        deputy=deputy,
        assignment_decision_id=f"assignment-{suffix}",
        assignment_evidence_reference="assignment-evidence",
        decided_at=BASE + timedelta(minutes=2),
    )
    registered = DocumentCustodyEvent(
        tenant, f"custody-registered-{suffix}", document_id,
        DocumentCustodyEventType.REGISTERED, BASE, 1, "custody-registration",
    )
    received = DocumentCustodyEvent(
        tenant, f"custody-received-{suffix}", document_id,
        DocumentCustodyEventType.RECEIVED_IN_OFFICE, BASE + timedelta(minutes=1), 2,
        "custody-receipt", "client-holder", office_id,
    )
    prior_events = (registered, received)
    expected_current = ProcessServiceAllocationCurrent(
        tenant_id=tenant,
        document_id=document_id,
        process_document_fingerprint=document.fingerprint,
        custody_chain_fingerprint=_chain_fingerprint(tenant, document_id, prior_events),
        custody_head_event_id=received.custody_event_id,
        custody_head_fingerprint=received.fingerprint,
        custody_head_sequence_number=2,
        current_holder_reference=office_id,
        authority_evidence_reference="migration-head",
        authority_evidence_fingerprint=HEX_A,
    )
    values: dict[str, Any] = {
        "instruction": instruction,
        "document": document,
        "district": district,
        "sheriff_office": office,
        "deputy": deputy,
        "assignment_decision": decision,
        "prior_custody_events": prior_events,
        "expected_prior_current": expected_current,
        "allocation_command_id": f"allocation-command-{suffix}",
        "idempotency_key": f"allocation-idempotency-{suffix}",
        "allocation_custody_event_id": f"custody-allocation-{suffix}",
        "allocation_evidence_reference": "allocation-evidence",
        "allocated_at": BASE + timedelta(minutes=3),
    }
    return _Fixture(tenant, instruction, document, district, office, deputy, decision, prior_events, expected_current, values)


def _invoke(fixture: _Fixture, lifecycle: Any, receipts: Any, current: Any, session: Any) -> Any:
    """Invoke P4A with only canonical fixture values and the caller session."""
    values = dict(fixture.values)
    values.update(
        lifecycle_collection=lifecycle,
        allocation_receipt_collection=receipts,
        allocation_current_collection=current,
        session=session,
    )
    return orchestrate_process_service_allocation(**values)


def _seed_base(client: MongoClient, db: Any, fixture: _Fixture) -> tuple[Any, Any, Any]:
    """Persist P1 base snapshots and the TEST_FIXTURE_ONLY_CURRENTNESS_SEED."""
    lifecycle = db[LIFECYCLE_COLLECTION]
    receipts = db[ALLOCATION_RECEIPT_COLLECTION]
    current = db[ALLOCATION_CURRENT_COLLECTION]
    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        LegalOperationsLifecycleRegistry.create(fixture.instruction, lifecycle, session=session)
        LegalOperationsLifecycleRegistry.create(fixture.document, lifecycle, session=session)
        current.insert_one(fixture.expected_current.to_dict(), session=session)
        session.commit_transaction()
    return lifecycle, receipts, current


@pytest.fixture
def mongo_runtime():
    """Yield a verified writable replica set; only pre-yield availability skips."""
    uri = os.getenv("TEST_VENDOR_MONGO_URI", DEFAULT_URI)
    client = MongoClient(uri, serverSelectionTimeoutMS=2000, connectTimeoutMS=2000, retryWrites=True)
    try:
        hello = client.admin.command("hello")
    except PyMongoError as error:
        client.close()
        pytest.skip(f"NOT CERTIFIED: hello unavailable: {error.__class__.__name__}")
    if hello.get("setName") != EXPECTED_REPLICA_SET:
        client.close()
        pytest.skip("NOT CERTIFIED: wrong replica set")
    if hello.get("isWritablePrimary") is not True:
        client.close()
        pytest.skip("NOT CERTIFIED: no writable primary")
    database_name = f"legal_p4a_{uuid4().hex}"
    db = client.get_database(
        database_name,
        read_concern=ReadConcern("majority"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    try:
        yield client, db
    finally:
        cleanup_error: BaseException | None = None
        try:
            client.drop_database(database_name)
        except BaseException as error:  # pragma: no cover - host cleanup only
            cleanup_error = error
        finally:
            client.close()
        if cleanup_error is not None and sys.exc_info()[0] is None:
            raise cleanup_error


def test_real_mongo_p4a_composition(mongo_runtime: tuple[MongoClient, Any]) -> None:
    """Certify P4A creation, replay, abort, CAS preflight, partial state, and isolation."""
    client, db = mongo_runtime
    lifecycle = db[LIFECYCLE_COLLECTION]
    receipts = db[ALLOCATION_RECEIPT_COLLECTION]
    current = db[ALLOCATION_CURRENT_COLLECTION]
    LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
    ProcessServiceAllocationRegistry.ensure_indexes(receipts, current)

    index_docs = list(lifecycle.list_indexes())
    p2_history = next(item for item in index_docs if item["name"] == "legal_operations_tenant_entity_history")
    p2_identity = next(item for item in index_docs if item["name"] == "legal_operations_tenant_evidence_unique")
    assert p2_history["key"] == {"tenant_id": 1, "entity_type": 1, "entity_identity": 1}
    assert p2_history.get("unique") is not True
    assert p2_identity["key"] == {"tenant_id": 1, "evidence_identity": 1}
    assert p2_identity["unique"] is True
    receipt_indexes = {item["name"]: item for item in receipts.list_indexes()}
    assert receipt_indexes["process_service_allocation_tenant_command_unique"]["key"] == {"tenant_id": 1, "allocation_command_id": 1}
    assert receipt_indexes["process_service_allocation_tenant_command_unique"]["unique"] is True
    assert receipt_indexes["process_service_allocation_tenant_document_idempotency_unique"]["key"] == {"tenant_id": 1, "document_id": 1, "idempotency_key": 1}
    assert receipt_indexes["process_service_allocation_tenant_document_idempotency_unique"]["unique"] is True
    assert receipt_indexes["process_service_allocation_tenant_event_unique"]["key"] == {"tenant_id": 1, "allocation_custody_event_id": 1}
    assert receipt_indexes["process_service_allocation_tenant_event_unique"]["unique"] is True
    current_indexes = {item["name"]: item for item in current.list_indexes()}
    assert current_indexes["process_service_allocation_current_tenant_document_unique"]["key"] == {"tenant_id": 1, "document_id": 1}
    assert current_indexes["process_service_allocation_current_tenant_document_unique"]["unique"] is True

    fixture = _fixture("tenant-p4a-committed", "committed")
    lifecycle, receipts, current = _seed_base(client, db, fixture)
    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        result = _invoke(fixture, lifecycle, receipts, current, session)
        assert result.persistence_result.outcome is ProcessServiceAllocationPersistenceOutcome.CREATED
        assert result.allocated_document.state is ProcessDocumentState.ALLOCATED_TO_DEPUTY
        assert result.allocation_custody_event.event_type is DocumentCustodyEventType.ALLOCATED_TO_DEPUTY
        assert result.allocation_custody_event.from_holder_reference == fixture.office.sheriff_office_id
        assert result.allocation_custody_event.to_holder_reference == fixture.deputy.deputy_id
        assert result.allocation_custody_event.sequence_number == 3
        assert lifecycle.count_documents({"tenant_id": fixture.tenant, "entity_type": "ProcessDocument"}, session=session) == 2
        assert lifecycle.count_documents({"tenant_id": fixture.tenant, "entity_type": "DocumentCustodyEvent"}, session=session) == 1
        assert receipts.count_documents({"tenant_id": fixture.tenant}, session=session) == 1
        assert current.count_documents({"tenant_id": fixture.tenant, "document_id": fixture.document.document_id}, session=session) == 1
        session.commit_transaction()
    allocated_identity = _p2_identity(result.allocated_document)
    event_identity = _p2_identity(result.allocation_custody_event)
    assert lifecycle.count_documents({"tenant_id": fixture.tenant, "p1_fingerprint": result.allocated_document.fingerprint}) == 1
    assert LegalOperationsLifecycleRegistry.get(fixture.tenant, allocated_identity, lifecycle).to_dict() == result.allocated_document.to_dict()
    assert LegalOperationsLifecycleRegistry.get(fixture.tenant, event_identity, lifecycle).to_dict() == result.allocation_custody_event.to_dict()
    assert receipts.count_documents({"tenant_id": fixture.tenant}) == 1
    assert current.count_documents({"tenant_id": fixture.tenant, "document_id": fixture.document.document_id}) == 1
    stored_current = current.find_one({"tenant_id": fixture.tenant, "document_id": fixture.document.document_id})
    assert stored_current is not None
    stored_current_without_id = dict(stored_current)
    stored_current_without_id.pop("_id", None)
    assert stored_current_without_id == result.persistence_result.current.to_dict()
    source_record = receipts.find_one({"tenant_id": fixture.tenant})
    assert source_record is not None
    assert source_record["receipt_payload"]["source_instruction_fingerprint"] == fixture.instruction.fingerprint
    assert source_record["receipt_payload"]["source_document_fingerprint"] == fixture.document.fingerprint

    with client.start_session() as replay_session:
        replay_session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        replay = _invoke(fixture, lifecycle, receipts, current, replay_session)
        assert replay.persistence_result.outcome is ProcessServiceAllocationPersistenceOutcome.IDEMPOTENT_REPLAY
        replay_session.commit_transaction()
    assert receipts.count_documents({"tenant_id": fixture.tenant}) == 1
    assert current.count_documents({"tenant_id": fixture.tenant, "document_id": fixture.document.document_id}) == 1

    abort_fixture = _fixture("tenant-p4a-abort", "abort")
    lifecycle, receipts, current = _seed_base(client, db, abort_fixture)
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        _invoke(abort_fixture, lifecycle, receipts, current, session)
        assert receipts.count_documents({"tenant_id": abort_fixture.tenant, "idempotency_key": abort_fixture.values["idempotency_key"]}, session=session) == 1
        session.abort_transaction()
    assert receipts.count_documents({"tenant_id": abort_fixture.tenant, "document_id": abort_fixture.document.document_id, "idempotency_key": abort_fixture.values["idempotency_key"]}) == 0
    assert lifecycle.count_documents({"tenant_id": abort_fixture.tenant, "entity_type": "ProcessDocument", "entity_identity": abort_fixture.document.document_id}) == 1
    assert lifecycle.count_documents({"tenant_id": abort_fixture.tenant, "entity_type": "DocumentCustodyEvent", "entity_identity": abort_fixture.values["allocation_custody_event_id"]}) == 0
    assert current.find_one({"tenant_id": abort_fixture.tenant, "document_id": abort_fixture.document.document_id})
    assert _without_mongo_id(current.find_one({"tenant_id": abort_fixture.tenant, "document_id": abort_fixture.document.document_id})) == abort_fixture.expected_current.to_dict()

    mismatch = _fixture("tenant-p4a-current-mismatch", "current-mismatch")
    lifecycle, receipts, current = _seed_base(client, db, mismatch)
    current.update_one(
        {"tenant_id": mismatch.tenant, "document_id": mismatch.document.document_id},
        {"$set": {"authority_evidence_reference": "different-current"}},
    )
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        with pytest.raises(ProcessServiceAllocationOrchestratorInputError, match="P4A_EXPECTED_CURRENT_DURABLE_MISMATCH"):
            _invoke(mismatch, lifecycle, receipts, current, session)
        session.abort_transaction()
    assert receipts.count_documents({"tenant_id": mismatch.tenant, "document_id": mismatch.document.document_id, "idempotency_key": mismatch.values["idempotency_key"]}) == 0
    assert lifecycle.count_documents({"tenant_id": mismatch.tenant, "entity_type": "DocumentCustodyEvent", "entity_identity": mismatch.values["allocation_custody_event_id"]}) == 0
    assert lifecycle.count_documents({"tenant_id": mismatch.tenant, "entity_type": "ProcessDocument", "entity_identity": mismatch.document.document_id}) == 1
    mismatched_current = current.find_one({"tenant_id": mismatch.tenant, "document_id": mismatch.document.document_id})
    assert mismatched_current is not None
    assert _without_mongo_id(mismatched_current) == {**mismatch.expected_current.to_dict(), "authority_evidence_reference": "different-current"}

    partial = _fixture("tenant-p4a-partial-document", "partial-document")
    lifecycle, receipts, current = _seed_base(client, db, partial)
    allocated = partial.document.transition_to(
        ProcessDocumentState.ALLOCATED_TO_DEPUTY,
        evidence_reference="allocation-evidence",
        occurred_at=BASE + timedelta(minutes=3),
    )
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        LegalOperationsLifecycleRegistry.create(allocated, lifecycle, session=session)
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        with pytest.raises(ProcessServiceAllocationOrchestratorPartialReplayError, match="P4A_PARTIAL_REPLAY"):
            _invoke(partial, lifecycle, receipts, current, session)
        session.abort_transaction()
    assert receipts.count_documents({"tenant_id": partial.tenant, "document_id": partial.document.document_id, "idempotency_key": partial.values["idempotency_key"]}) == 0
    assert lifecycle.count_documents({"tenant_id": partial.tenant, "entity_type": "ProcessDocument", "entity_identity": partial.document.document_id}) == 2
    assert lifecycle.count_documents({"tenant_id": partial.tenant, "entity_type": "DocumentCustodyEvent", "entity_identity": partial.values["allocation_custody_event_id"]}) == 0
    assert _without_mongo_id(current.find_one({"tenant_id": partial.tenant, "document_id": partial.document.document_id})) == partial.expected_current.to_dict()

    partial_event = _fixture("tenant-p4a-partial-event", "partial-event")
    lifecycle, receipts, current = _seed_base(client, db, partial_event)
    allocated_event = DocumentCustodyEvent(
        partial_event.tenant,
        partial_event.values["allocation_custody_event_id"],
        partial_event.document.document_id,
        DocumentCustodyEventType.ALLOCATED_TO_DEPUTY,
        BASE + timedelta(minutes=3),
        3,
        "allocation-evidence",
        partial_event.office.sheriff_office_id,
        partial_event.deputy.deputy_id,
    )
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        LegalOperationsLifecycleRegistry.create(allocated_event, lifecycle, session=session)
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        with pytest.raises(ProcessServiceAllocationOrchestratorPartialReplayError, match="P4A_PARTIAL_REPLAY"):
            _invoke(partial_event, lifecycle, receipts, current, session)
        session.abort_transaction()
    assert receipts.count_documents({"tenant_id": partial_event.tenant, "document_id": partial_event.document.document_id, "idempotency_key": partial_event.values["idempotency_key"]}) == 0
    assert lifecycle.count_documents({"tenant_id": partial_event.tenant, "entity_type": "ProcessDocument", "entity_identity": partial_event.document.document_id}) == 1
    assert lifecycle.count_documents({"tenant_id": partial_event.tenant, "entity_type": "DocumentCustodyEvent", "entity_identity": partial_event.values["allocation_custody_event_id"]}) == 1
    assert _without_mongo_id(current.find_one({"tenant_id": partial_event.tenant, "document_id": partial_event.document.document_id})) == partial_event.expected_current.to_dict()

    receipt_partial = _fixture("tenant-p4a-partial-receipt", "partial-receipt")
    lifecycle, receipts, current = _seed_base(client, db, receipt_partial)
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        created_partial = _invoke(receipt_partial, lifecycle, receipts, current, session)
        session.commit_transaction()
    lifecycle.delete_one({"tenant_id": receipt_partial.tenant, "p1_fingerprint": created_partial.allocated_document.fingerprint})
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        with pytest.raises(ProcessServiceAllocationOrchestratorPartialReplayError, match="P4A_PARTIAL_REPLAY"):
            _invoke(receipt_partial, lifecycle, receipts, current, session)
        session.abort_transaction()
    assert lifecycle.count_documents({"tenant_id": receipt_partial.tenant, "entity_type": "ProcessDocument", "entity_identity": receipt_partial.document.document_id, "p1_fingerprint": created_partial.allocated_document.fingerprint}) == 0
    assert receipts.count_documents({"tenant_id": receipt_partial.tenant, "document_id": receipt_partial.document.document_id, "idempotency_key": receipt_partial.values["idempotency_key"]}) == 1
    assert _without_mongo_id(current.find_one({"tenant_id": receipt_partial.tenant, "document_id": receipt_partial.document.document_id})) == created_partial.persistence_result.current.to_dict()

    tenant_a = _fixture("tenant-p4a-a", "isolation")
    lifecycle, receipts, current = _seed_base(client, db, tenant_a)
    with pytest.raises(LegalOperationsLifecycleRegistryError, match="M2_EVIDENCE_NOT_FOUND"):
        LegalOperationsLifecycleRegistry.get("tenant-p4a-b", _p2_identity(tenant_a.document), lifecycle)
    assert lifecycle.count_documents({"tenant_id": tenant_a.tenant}) == 2

    corrupt = _fixture("tenant-p4a-p4b-corrupt", "p4b-corrupt")
    lifecycle, receipts, current = _seed_base(client, db, corrupt)
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        _invoke(corrupt, lifecycle, receipts, current, session)
        session.commit_transaction()
    current.update_one(
        {"tenant_id": corrupt.tenant, "document_id": corrupt.document.document_id},
        {"$set": {"authority_evidence_reference": "corrupt-current"}},
    )
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        with pytest.raises(ProcessServiceAllocationRegistryReceiptPointerCorrelationError):
            _invoke(corrupt, lifecycle, receipts, current, session)
        session.abort_transaction()
    source_record = receipts.find_one({"tenant_id": fixture.tenant})
    assert source_record is not None
    assert "payment" not in source_record and "settlement" not in source_record
    assert "invoice" not in source_record and "billing_execution" not in source_record


# ARTIFACT: test_process_service_allocation_orchestrator_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-ORCHESTRATOR-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: host-backed P4A composition certificate only.
# TENANT POSTURE: explicit tenant-scoped real Mongo fixtures and lookups.
# FAIL-CLOSED POSTURE: post-yield product/runtime failures fail the certificate.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution/settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
