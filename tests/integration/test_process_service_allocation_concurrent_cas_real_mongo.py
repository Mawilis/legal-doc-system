"""Deterministic host-backed P4C concurrent-CAS certificate.

TITLE: Wilsy OS Process Service Allocation Concurrent CAS Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-CONCURRENT-CAS-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify that two legitimate P4A callers observing one exact durable
         pre-allocation pointer cannot both commit divergent allocations.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_allocation_concurrent_cas_real_mongo.py
COLLABORATION / OWNERSHIP: Direct P4C concurrency certificate. P1 owns
                            lifecycle/custody evidence, P2 owns immutable
                            persistence, P3 owns assignment evidence, P4B owns
                            receipt/current CAS, and P4A owns composition only.
                            Each worker owns its Mongo session/transaction.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ALLOCATION-CONCURRENT-CAS-REAL-MONGO-CERT
           adds deterministic barrier-controlled competing allocation proof
           with winner durability and loser rollback assertions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: One UUID-isolated race tenant/document stream is used; every
                 P2/P4B query is explicitly tenant and identity scoped.
AUTHORITY BOUNDARY: Test-only concurrency evidence for frozen P4A/P4B CAS;
                    no production authority, service execution, return, IAM,
                    transport, or lifecycle derivation is introduced.
FINANCIAL AUTHORITY BOUNDARY: Allocation is not invoice, payment, execution,
                              or settlement truth; Kennel EOS exclusively owns
                              financial execution and settlement.
TRANSACTION BOUNDARY: Two independent worker sessions start/commit/abort their
                      own transactions. P4A and P4B never own transaction
                      lifecycle or a Mongo client.
FAIL-CLOSED DECLARATION: Only pre-yield hello/setName/writable-primary
                         availability may skip. Race, persistence, assertion,
                         or product failures after yield fail the certificate.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
import sys
import threading
from typing import Any
from unittest.mock import patch
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
from tools.eos.legal_operations.orchestration import process_service_allocation_orchestrator as p4a
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
)
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ALLOCATION_CURRENT_COLLECTION,
    ALLOCATION_RECEIPT_COLLECTION,
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationPersistenceOutcome,
    ProcessServiceAllocationRegistry,
    ProcessServiceAllocationRegistryPersistenceUnavailableError,
    ProcessServiceAllocationRegistryRetryRequiredError,
)


VERSION = "v1.0.0-PROCESS-SERVICE-ALLOCATION-CONCURRENT-CAS-REAL-MONGO-CERT"
DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 9, 0, tzinfo=timezone.utc)
HEX_A = "a" * 128
_TRANSACTION_RACE_LABELS = frozenset({"TransientTransactionError"})


def _sha3(value: object) -> str:
    """Return the repository's deterministic compact-JSON SHA3-512 digest."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha3_512(encoded).hexdigest()


def _chain_fingerprint(tenant_id: str, document_id: str, events: tuple[DocumentCustodyEvent, ...]) -> str:
    """Derive the frozen P4A custody-chain fingerprint."""
    return _sha3(
        {
            "schema": "WILSY-PROCESS-SERVICE-CUSTODY-CHAIN/V1",
            "tenant_id": tenant_id,
            "document_id": document_id,
            "event_fingerprints": [event.fingerprint for event in events],
        }
    )


def _p2_identity(value: object) -> str:
    """Derive one exact P2 identity without importing private production helpers."""
    names = {
        "LegalInstruction": "instruction_id",
        "ProcessDocument": "document_id",
        "DocumentCustodyEvent": "custody_event_id",
    }
    entity_type = type(value).__name__
    identity_name = names[entity_type]
    return _sha3(
        {
            "tenant_id": getattr(value, "tenant_id"),
            "entity_type": entity_type,
            "entity_identity": getattr(value, identity_name),
            "p1_fingerprint": getattr(value, "fingerprint"),
            "source_fingerprint": None,
        }
    )


@dataclass(frozen=True)
class _Common:
    tenant: str
    instruction: LegalInstruction
    document: ProcessDocument
    district: District
    office: SheriffOffice
    prior_events: tuple[DocumentCustodyEvent, ...]
    expected_current: ProcessServiceAllocationCurrent


@dataclass(frozen=True)
class _Command:
    common: _Common
    deputy: Deputy
    decision: Any
    allocation_command_id: str
    idempotency_key: str
    allocation_custody_event_id: str
    allocation_evidence_reference: str
    allocated_at: datetime


@dataclass(frozen=True)
class _WorkerOutcome:
    worker: str
    status: str
    result: Any = None
    error: BaseException | None = None
    labels: tuple[str, ...] = ()


def _classify_race_loser(error: BaseException) -> tuple[str, str | None, tuple[str, ...]]:
    """Accept only an evidenced transactional/write-conflict loser outcome."""
    if isinstance(error, ProcessServiceAllocationRegistryRetryRequiredError):
        if str(error) != "P4_WHOLE_TRANSACTION_RETRY_REQUIRED":
            raise AssertionError(f"unexpected retry-required code: {error}")
        return ("P4_WHOLE_TRANSACTION_RETRY_REQUIRED", str(error), ())

    chain: list[BaseException] = []
    current: BaseException | None = error
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        chain.append(current)
        current = current.__cause__ or current.__context__

    if isinstance(error, ProcessServiceAllocationRegistryPersistenceUnavailableError):
        for cause in chain[1:]:
            if isinstance(cause, PyMongoError):
                labels = tuple(sorted(getattr(cause, "_error_labels", ())))
                if _TRANSACTION_RACE_LABELS.intersection(labels):
                    code = getattr(cause, "code", None)
                    return ("P4_PERSISTENCE_UNAVAILABLE_TRANSACTION_CONFLICT", str(code) if code is not None else None, labels)
        raise AssertionError("persistence-unavailable loser lacks a transactional PyMongo cause")

    if isinstance(error, PyMongoError):
        labels = tuple(sorted(getattr(error, "_error_labels", ())))
        if _TRANSACTION_RACE_LABELS.intersection(labels):
            code = getattr(error, "code", None)
            return ("PYMONGO_TRANSACTION_RACE", str(code) if code is not None else None, labels)
        raise AssertionError("raw PyMongo loser lacks a transactional race label")

    raise AssertionError(f"unsupported race loser type: {type(error).__name__}")


def _common(tenant: str, suffix: str) -> _Common:
    """Build one exact accepted/received pre-allocation source stream."""
    instruction_id = f"instruction-{suffix}"
    matter_id = f"matter-{suffix}"
    document_id = f"document-{suffix}"
    district_id = f"district-{suffix}"
    office_id = f"office-{suffix}"
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
    current = ProcessServiceAllocationCurrent(
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
    return _Common(tenant, instruction, document, district, office, prior_events, current)


def _command(common: _Common, worker: str) -> _Command:
    """Build one independently authorized deputy command."""
    deputy = Deputy(
        common.tenant,
        f"deputy-{worker}",
        common.office.sheriff_office_id,
        f"Deputy {worker}",
        f"badge-{worker}",
        f"deputy-evidence-{worker}",
    )
    decision = authorize_process_service_assignment(
        instruction=common.instruction,
        document=common.document,
        district=common.district,
        sheriff_office=common.office,
        deputy=deputy,
        assignment_decision_id=f"assignment-{worker}",
        assignment_evidence_reference=f"assignment-evidence-{worker}",
        decided_at=BASE + timedelta(minutes=2),
    )
    return _Command(
        common=common,
        deputy=deputy,
        decision=decision,
        allocation_command_id=f"allocation-command-{worker}",
        idempotency_key=f"allocation-idempotency-{worker}",
        allocation_custody_event_id=f"custody-allocation-{worker}",
        allocation_evidence_reference=f"allocation-evidence-{worker}",
        allocated_at=BASE + timedelta(minutes=3),
    )


def _expected_results(command: _Command) -> tuple[ProcessDocument, DocumentCustodyEvent]:
    """Derive the exact two P2 result values independently for winner/loser checks."""
    allocated_document = command.common.document.transition_to(
        ProcessDocumentState.ALLOCATED_TO_DEPUTY,
        evidence_reference=command.allocation_evidence_reference,
        occurred_at=command.allocated_at,
    )
    event = DocumentCustodyEvent(
        command.common.tenant,
        command.allocation_custody_event_id,
        command.common.document.document_id,
        DocumentCustodyEventType.ALLOCATED_TO_DEPUTY,
        command.allocated_at,
        3,
        command.allocation_evidence_reference,
        command.common.office.sheriff_office_id,
        command.deputy.deputy_id,
    )
    return allocated_document, event


def _seed(client: MongoClient, db: Any, common: _Common) -> tuple[Any, Any, Any]:
    """Persist source P1 snapshots and TEST-FIXTURE-ONLY currentness."""
    lifecycle = db[LIFECYCLE_COLLECTION]
    receipts = db[ALLOCATION_RECEIPT_COLLECTION]
    current = db[ALLOCATION_CURRENT_COLLECTION]
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        LegalOperationsLifecycleRegistry.create(common.instruction, lifecycle, session=session)
        LegalOperationsLifecycleRegistry.create(common.document, lifecycle, session=session)
        current.insert_one(common.expected_current.to_dict(), session=session)
        session.commit_transaction()
    return lifecycle, receipts, current


@pytest.fixture
def mongo_runtime():
    """Yield one verified writable replica set; only pre-yield availability skips."""
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
    database_name = f"legal_p4c_{uuid4().hex}"
    db = client.get_database(database_name, read_concern=ReadConcern("majority"), write_concern=WriteConcern(w="majority", j=True))
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


def test_two_legitimate_p4a_allocations_have_one_cas_winner(mongo_runtime: tuple[MongoClient, Any]) -> None:
    """Synchronize two real transactions after the same current-pointer read."""
    client, db = mongo_runtime
    tenant = f"tenant-p4c-{uuid4().hex[:12]}"
    common = _common(tenant, "race")
    command_a = _command(common, "a")
    command_b = _command(common, "b")
    lifecycle, receipts, current = _seed(client, db, common)
    LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
    ProcessServiceAllocationRegistry.ensure_indexes(receipts, current)

    barrier = threading.Barrier(2)
    thread_state = threading.local()
    observed: dict[str, dict[str, object]] = {}
    observed_lock = threading.Lock()
    original_get_current = ProcessServiceAllocationRegistry.get_current

    def synchronized_get_current(tenant_id: str, document_id: str, collection: Any, *, session: Any) -> Any:
        """Call the real P4B read, then synchronize only the two race workers."""
        pointer = original_get_current(tenant_id, document_id, collection, session=session)
        worker = getattr(thread_state, "worker", None)
        if worker is not None and not getattr(thread_state, "barrier_done", False):
            with observed_lock:
                observed[worker] = pointer.to_dict()
            barrier.wait(timeout=30)
            thread_state.barrier_done = True
        return pointer

    def run_worker(worker: str, command: _Command) -> _WorkerOutcome:
        """Run one caller-owned transaction with no retry or lifecycle takeover."""
        thread_state.worker = worker
        thread_state.barrier_done = False
        with client.start_session() as session:
            session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
            try:
                values = {
                    "instruction": command.common.instruction,
                    "document": command.common.document,
                    "district": command.common.district,
                    "sheriff_office": command.common.office,
                    "deputy": command.deputy,
                    "assignment_decision": command.decision,
                    "prior_custody_events": command.common.prior_events,
                    "expected_prior_current": command.common.expected_current,
                    "allocation_command_id": command.allocation_command_id,
                    "idempotency_key": command.idempotency_key,
                    "allocation_custody_event_id": command.allocation_custody_event_id,
                    "allocation_evidence_reference": command.allocation_evidence_reference,
                    "allocated_at": command.allocated_at,
                    "lifecycle_collection": lifecycle,
                    "allocation_receipt_collection": receipts,
                    "allocation_current_collection": current,
                    "session": session,
                }
                result = p4a.orchestrate_process_service_allocation(**values)
                session.commit_transaction()
                if result.persistence_result.outcome is not ProcessServiceAllocationPersistenceOutcome.CREATED:
                    raise AssertionError("a competing command unexpectedly replayed")
                return _WorkerOutcome(worker, "COMMITTED", result=result)
            except BaseException as error:
                if session.in_transaction:
                    session.abort_transaction()
                labels = tuple(getattr(error, "_error_labels", ()))
                return _WorkerOutcome(worker, "REJECTED", error=error, labels=labels)

    with patch.object(ProcessServiceAllocationRegistry, "get_current", staticmethod(synchronized_get_current)):
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(run_worker, "a", command_a), executor.submit(run_worker, "b", command_b)]
            outcomes = [future.result() for future in futures]

    assert set(observed) == {"a", "b"}
    assert observed["a"] == observed["b"] == common.expected_current.to_dict()
    assert sorted(outcome.status for outcome in outcomes) == ["COMMITTED", "REJECTED"]
    winner = next(outcome for outcome in outcomes if outcome.status == "COMMITTED")
    loser = next(outcome for outcome in outcomes if outcome.status == "REJECTED")
    assert loser.error is not None
    loser_classification, loser_code, loser_labels = _classify_race_loser(loser.error)
    assert loser_classification in {
        "P4_WHOLE_TRANSACTION_RETRY_REQUIRED",
        "P4_PERSISTENCE_UNAVAILABLE_TRANSACTION_CONFLICT",
        "PYMONGO_TRANSACTION_RACE",
    }
    winner_command = command_a if winner.worker == "a" else command_b
    loser_command = command_b if winner.worker == "a" else command_a
    winner_document, winner_event = _expected_results(winner_command)
    loser_document, loser_event = _expected_results(loser_command)

    winner_receipts = list(receipts.find({"tenant_id": tenant, "allocation_command_id": {"$in": [command_a.allocation_command_id, command_b.allocation_command_id]}}))
    assert len(winner_receipts) == 1
    winner_receipt = winner_receipts[0]
    assert winner_receipt["allocation_command_id"] == winner_command.allocation_command_id
    assert winner_receipt["idempotency_key"] == winner_command.idempotency_key
    durable_current = current.find_one({"tenant_id": tenant, "document_id": common.document.document_id})
    assert durable_current is not None
    durable_current_without_id = dict(durable_current)
    durable_current_without_id.pop("_id", None)
    assert winner.result is not None
    assert durable_current_without_id == winner.result.persistence_result.current.to_dict()
    assert durable_current_without_id["current_holder_reference"] == winner_command.deputy.deputy_id
    assert durable_current_without_id["authority_evidence_reference"] == winner_command.allocation_command_id
    assert durable_current_without_id["authority_evidence_fingerprint"] == winner_receipt["receipt_fingerprint"]
    assert lifecycle.count_documents({"tenant_id": tenant, "evidence_identity": _p2_identity(winner_document)}) == 1
    assert lifecycle.count_documents({"tenant_id": tenant, "evidence_identity": _p2_identity(winner_event)}) == 1
    assert lifecycle.count_documents({"tenant_id": tenant, "evidence_identity": _p2_identity(loser_document)}) == 0
    assert lifecycle.count_documents({"tenant_id": tenant, "evidence_identity": _p2_identity(loser_event)}) == 0
    assert receipts.count_documents({"tenant_id": tenant, "allocation_command_id": loser_command.allocation_command_id}) == 0
    assert receipts.count_documents({"tenant_id": tenant, "idempotency_key": loser_command.idempotency_key}) == 0
    assert lifecycle.count_documents({"tenant_id": tenant, "evidence_identity": _p2_identity(common.instruction)}) == 1
    assert lifecycle.count_documents({"tenant_id": tenant, "evidence_identity": _p2_identity(common.document)}) == 1
    assert lifecycle.count_documents({"tenant_id": tenant, "entity_type": "ProcessDocument", "entity_identity": common.document.document_id}) == 2
    assert current.count_documents({"tenant_id": tenant, "document_id": common.document.document_id}) == 1
    assert loser_code is None or isinstance(loser_code, str)
    assert all(isinstance(label, str) for label in loser_labels)


# ARTIFACT: test_process_service_allocation_concurrent_cas_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-CONCURRENT-CAS-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: deterministic P4C race certificate only.
# TENANT POSTURE: one UUID-isolated explicit race tenant.
# FAIL-CLOSED POSTURE: only pre-yield runtime availability may skip.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution/settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
