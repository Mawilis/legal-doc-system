"""Host-backed P4B certificate for process-service allocation persistence.

TITLE: Wilsy OS Process Service Allocation Registry Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify real Mongo index topology, durable immutable allocation
         receipts, explicit current-pointer CAS, replay, rollback, event
         identity uniqueness, and tenant isolation for P4B.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_allocation_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Host-backed P4B certificate only; P1 owns legal
                            lifecycle evidence, P2 owns immutable persistence,
                            P3 owns assignment authority, and the test caller
                            owns every Mongo transaction boundary.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ALLOCATION-REGISTRY-REAL-MONGO-CERT
           certifies real replica-set indexes, commit/replay durability,
           rollback atomicity, strict event identity, and stale-CAS rejection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and identifiers;
                             no provider, secret, customer, or external call.
TENANT BOUNDARY: Every Mongo query and write is explicitly tenant/document
                 scoped; foreign evidence is represented only as absence.
AUTHORITY BOUNDARY: P4B persistence/currentness evidence only. Fixture pointer
                    seeding is test setup, never production bootstrap authority.
TRANSACTION BOUNDARY: The certificate starts, commits, and aborts transactions;
                      the registry must only receive and propagate sessions.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; no invoice, payment, or paid
                              state is represented by legal allocation evidence.
FAIL-CLOSED DECLARATION: Wrong replica set, unavailable persistence, strict
                         corruption, replay divergence, races, and stale
                         currentness fail closed; runtime skips are pre-yield
                         environment skips only.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.registry import process_service_allocation_registry as registry


VERSION = "v1.0.0-PROCESS-SERVICE-ALLOCATION-REGISTRY-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 9, 0, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128
HEX_E = "e" * 128
HEX_F = "f" * 128
HEX_0 = "0" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[Any, Any, Any, Any]]:
    """Yield an isolated writable replica-set database or pre-yield skip.

    Once ``hello`` proves the required writable replica set, index or product
    failures propagate as test failures. Cleanup never converts those failures
    into skips.
    """
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"host Mongo unavailable during hello: {type(error).__name__}: {error}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")

        database = client[f"p4b_alloc_rm_{uuid.uuid4().hex}"]
        receipt_collection = database.get_collection(
            registry.RECEIPT_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        current_collection = database.get_collection(
            registry.CURRENT_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        registry.ensure_indexes(receipt_collection, current_collection)
        yield client, database, receipt_collection, current_collection
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _receipt(
    tenant_id: str,
    *,
    document_id: str = "document-1",
    allocation_command_id: str = "allocation-command-1",
    idempotency_key: str = "idempotency-1",
    allocation_custody_event_id: str = "custody-event-1",
    source_document_fingerprint: str = HEX_C,
    prior_custody_chain_fingerprint: str = HEX_0,
    prior_custody_head_event_id: str = "custody-head-1",
    prior_custody_head_fingerprint: str = HEX_A,
    prior_custody_head_sequence_number: int = 7,
    from_holder_reference: str = "office-holder-1",
    allocated_at: datetime = BASE,
) -> registry.ProcessServiceAllocationReceipt:
    """Build one deterministic valid P4A receipt for the isolated database."""
    return registry.ProcessServiceAllocationReceipt(
        tenant_id=tenant_id,
        allocation_command_id=allocation_command_id,
        idempotency_key=idempotency_key,
        instruction_id="instruction-1",
        case_matter_id="matter-1",
        document_id=document_id,
        district_id="district-1",
        sheriff_office_id="office-1",
        deputy_id="deputy-1",
        assignment_decision_id="assignment-1",
        assignment_decision_fingerprint=HEX_A,
        source_instruction_fingerprint=HEX_B,
        source_document_fingerprint=source_document_fingerprint,
        source_district_fingerprint=HEX_D,
        source_sheriff_office_fingerprint=HEX_E,
        source_deputy_fingerprint=HEX_F,
        prior_custody_chain_fingerprint=prior_custody_chain_fingerprint,
        prior_custody_head_event_id=prior_custody_head_event_id,
        prior_custody_head_fingerprint=prior_custody_head_fingerprint,
        prior_custody_head_sequence_number=prior_custody_head_sequence_number,
        from_holder_reference=from_holder_reference,
        to_holder_reference="deputy-holder-1",
        allocation_custody_event_id=allocation_custody_event_id,
        allocation_evidence_reference="allocation-evidence-1",
        allocated_at=allocated_at,
        allocated_document_fingerprint=HEX_B,
        allocation_custody_event_fingerprint=HEX_C,
        result_custody_chain_fingerprint=HEX_D,
    )


def _prior(receipt: registry.ProcessServiceAllocationReceipt) -> registry.ProcessServiceAllocationCurrent:
    """Build the explicit current pointer that exactly precedes a receipt."""
    return registry.ProcessServiceAllocationCurrent(
        tenant_id=receipt.tenant_id,
        document_id=receipt.document_id,
        process_document_fingerprint=receipt.source_document_fingerprint,
        custody_chain_fingerprint=receipt.prior_custody_chain_fingerprint,
        custody_head_event_id=receipt.prior_custody_head_event_id,
        custody_head_fingerprint=receipt.prior_custody_head_fingerprint,
        custody_head_sequence_number=receipt.prior_custody_head_sequence_number,
        current_holder_reference=receipt.from_holder_reference,
        authority_evidence_reference="migration-head-1",
        authority_evidence_fingerprint=HEX_E,
    )


def _next(receipt: registry.ProcessServiceAllocationReceipt) -> registry.ProcessServiceAllocationCurrent:
    """Derive the expected post-allocation pointer for assertions."""
    return registry.ProcessServiceAllocationCurrent(
        tenant_id=receipt.tenant_id,
        document_id=receipt.document_id,
        process_document_fingerprint=receipt.allocated_document_fingerprint,
        custody_chain_fingerprint=receipt.result_custody_chain_fingerprint,
        custody_head_event_id=receipt.allocation_custody_event_id,
        custody_head_fingerprint=receipt.allocation_custody_event_fingerprint,
        custody_head_sequence_number=receipt.prior_custody_head_sequence_number + 1,
        current_holder_reference=receipt.to_holder_reference,
        authority_evidence_reference=receipt.allocation_command_id,
        authority_evidence_fingerprint=receipt.fingerprint,
    )


def _seed_current(
    current_collection: Any,
    pointer: registry.ProcessServiceAllocationCurrent,
) -> None:
    """Seed test-only currentness; P4B has no production bootstrap API."""
    current_collection.insert_one(pointer.to_dict())


def _raw_receipt(collection: Any, receipt: registry.ProcessServiceAllocationReceipt) -> dict[str, Any]:
    """Read one durable receipt record for explicit raw evidence assertions."""
    row = collection.find_one(
        {
            "tenant_id": receipt.tenant_id,
            "document_id": receipt.document_id,
            "idempotency_key": receipt.idempotency_key,
        }
    )
    assert isinstance(row, dict)
    return row


def _raw_current_payload(collection: Any, tenant_id: str, document_id: str) -> dict[str, Any]:
    """Read one durable current pointer without Mongo's transport-only ``_id``."""
    row = collection.find_one({"tenant_id": tenant_id, "document_id": document_id})
    assert isinstance(row, dict)
    payload = dict(row)
    payload.pop("_id", None)
    return payload


def _persist_and_commit(
    client: Any,
    receipt: registry.ProcessServiceAllocationReceipt,
    prior: registry.ProcessServiceAllocationCurrent,
    receipt_collection: Any,
    current_collection: Any,
) -> registry.ProcessServiceAllocationPersistenceResult:
    """Persist one receipt while the test caller owns the transaction."""
    with client.start_session() as session:
        session.start_transaction()
        result = registry.persist_receipt_and_advance_current(
            receipt,
            prior,
            receipt_collection,
            current_collection,
            session=session,
        )
        session.commit_transaction()
        return result


def test_real_indexes_and_committed_create_replay(mongo_context: Any) -> None:
    """Certify exact indexes, committed creation, and durable replay."""
    client, _, receipts, current = mongo_context
    registry.ensure_indexes(receipts, current)
    receipt_indexes = {
        item["name"]: item for item in receipts.list_indexes() if item["name"] != "_id_"
    }
    assert set(receipt_indexes) == {
        registry.RECEIPT_COMMAND_INDEX_NAME,
        registry.RECEIPT_IDEMPOTENCY_INDEX_NAME,
        registry.RECEIPT_EVENT_INDEX_NAME,
    }
    assert dict(receipt_indexes[registry.RECEIPT_COMMAND_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "allocation_command_id": 1,
    }
    assert dict(receipt_indexes[registry.RECEIPT_IDEMPOTENCY_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "document_id": 1,
        "idempotency_key": 1,
    }
    assert dict(receipt_indexes[registry.RECEIPT_EVENT_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "allocation_custody_event_id": 1,
    }
    assert all(item["unique"] is True for item in receipt_indexes.values())
    current_indexes = {item["name"]: item for item in current.list_indexes() if item["name"] != "_id_"}
    assert set(current_indexes) == {registry.CURRENT_STREAM_INDEX_NAME}
    assert dict(current_indexes[registry.CURRENT_STREAM_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "document_id": 1,
    }
    assert current_indexes[registry.CURRENT_STREAM_INDEX_NAME]["unique"] is True

    tenant = f"tenant-{uuid.uuid4().hex}"
    receipt = _receipt(tenant)
    prior = _prior(receipt)
    _seed_current(current, prior)
    created = _persist_and_commit(client, receipt, prior, receipts, current)
    assert created.outcome is registry.ProcessServiceAllocationPersistenceOutcome.CREATED
    raw = _raw_receipt(receipts, receipt)
    assert raw["allocation_custody_event_id"] == receipt.allocation_custody_event_id
    assert raw["allocation_custody_event_id"] == raw["receipt_payload"]["allocation_custody_event_id"]
    assert raw["allocation_command_id"] == receipt.allocation_command_id
    assert raw["idempotency_key"] == receipt.idempotency_key
    assert receipts.count_documents({"tenant_id": tenant}) == 1
    assert current.count_documents({"tenant_id": tenant, "document_id": receipt.document_id}) == 1
    assert created.current.to_dict() == _next(receipt).to_dict()

    with client.start_session() as session:
        session.start_transaction()
        replay = registry.persist_receipt_and_advance_current(
            receipt, prior, receipts, current, session=session
        )
        assert replay.outcome is registry.ProcessServiceAllocationPersistenceOutcome.IDEMPOTENT_REPLAY
        assert replay.receipt.to_dict() == receipt.to_dict()
        assert replay.current.to_dict() == _next(receipt).to_dict()
        session.commit_transaction()
    assert receipts.count_documents({"tenant_id": tenant}) == 1
    assert current.count_documents({"tenant_id": tenant, "document_id": receipt.document_id}) == 1


def test_real_event_index_and_semantic_conflict(mongo_context: Any) -> None:
    """Certify top-level event uniqueness and public semantic conflict."""
    client, _, receipts, current = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    first = _receipt(tenant)
    first_prior = _prior(first)
    _seed_current(current, first_prior)
    _persist_and_commit(client, first, first_prior, receipts, current)

    raw = deepcopy(_raw_receipt(receipts, first))
    raw.pop("_id", None)
    raw["document_id"] = "collision-document"
    raw["allocation_command_id"] = "collision-command"
    raw["idempotency_key"] = "collision-idempotency"
    raw["evidence_identity"] = HEX_F
    with pytest.raises(DuplicateKeyError):
        receipts.insert_one(raw)

    second = _receipt(
        tenant,
        document_id="document-2",
        allocation_command_id="allocation-command-2",
        idempotency_key="idempotency-2",
        allocation_custody_event_id=first.allocation_custody_event_id,
    )
    second_prior = _prior(second)
    _seed_current(current, second_prior)
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.ProcessServiceAllocationRegistryCustodyEventConflictError) as raised:
            registry.persist_receipt_and_advance_current(
                second, second_prior, receipts, current, session=session
            )
        assert raised.value.code == "P4_ALLOCATION_CUSTODY_EVENT_IDENTITY_CONFLICT"
        session.abort_transaction()
    assert receipts.count_documents({"tenant_id": tenant, "document_id": "document-2"}) == 0
    assert _raw_current_payload(current, tenant, "document-2") == second_prior.to_dict()


def test_real_abort_atomicity_and_stale_prior_rejection(mongo_context: Any) -> None:
    """Certify caller abort rollback, commit durability, and stale CAS."""
    client, _, receipts, current = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    first = _receipt(tenant)
    prior = _prior(first)
    _seed_current(current, prior)
    with client.start_session() as session:
        session.start_transaction()
        result = registry.persist_receipt_and_advance_current(
            first, prior, receipts, current, session=session
        )
        assert result.outcome is registry.ProcessServiceAllocationPersistenceOutcome.CREATED
        assert receipts.count_documents({"tenant_id": tenant}, session=session) == 1
        assert current.count_documents({"tenant_id": tenant, "document_id": first.document_id}, session=session) == 1
        session.abort_transaction()
    assert receipts.count_documents({"tenant_id": tenant}) == 0
    assert _raw_current_payload(current, tenant, first.document_id) == prior.to_dict()

    _persist_and_commit(client, first, prior, receipts, current)
    next_prior = _next(first)
    second = _receipt(
        tenant,
        source_document_fingerprint=first.allocated_document_fingerprint,
        prior_custody_chain_fingerprint=first.result_custody_chain_fingerprint,
        prior_custody_head_event_id=first.allocation_custody_event_id,
        prior_custody_head_fingerprint=first.allocation_custody_event_fingerprint,
        prior_custody_head_sequence_number=next_prior.custody_head_sequence_number,
        from_holder_reference=first.to_holder_reference,
        allocation_command_id="allocation-command-2",
        idempotency_key="idempotency-2",
        allocation_custody_event_id="custody-event-2",
        allocated_at=BASE + timedelta(minutes=1),
    )
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.ProcessServiceAllocationRegistryCurrentPointerConflictError):
            registry.persist_receipt_and_advance_current(
                second, prior, receipts, current, session=session
            )
        session.abort_transaction()
    assert receipts.count_documents({"tenant_id": tenant}) == 1
    assert _raw_current_payload(current, tenant, first.document_id) == next_prior.to_dict()


def test_real_absent_pointer_tenant_isolation_and_corruption(mongo_context: Any) -> None:
    """Certify no bootstrap, tenant-scoped absence, and durable corruption gates."""
    client, _, receipts, current = mongo_context
    empty_tenant = f"tenant-empty-{uuid.uuid4().hex}"
    empty = _receipt(empty_tenant, document_id="empty-document")
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.ProcessServiceAllocationRegistryCurrentPointerMissingError):
            registry.persist_receipt_and_advance_current(
                empty, _prior(empty), receipts, current, session=session
            )
        session.abort_transaction()
    assert receipts.count_documents({"tenant_id": empty_tenant}) == 0
    assert current.count_documents({"tenant_id": empty_tenant}) == 0

    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"
    receipt_a = _receipt(tenant_a, document_id="shared-document", allocation_custody_event_id="shared-event")
    receipt_b = _receipt(
        tenant_b,
        document_id="shared-document",
        allocation_command_id="allocation-command-b",
        idempotency_key="idempotency-b",
        allocation_custody_event_id="shared-event",
    )
    prior_a = _prior(receipt_a)
    prior_b = _prior(receipt_b)
    _seed_current(current, prior_a)
    _seed_current(current, prior_b)
    _persist_and_commit(client, receipt_a, prior_a, receipts, current)
    _persist_and_commit(client, receipt_b, prior_b, receipts, current)
    assert current.find_one({"tenant_id": tenant_a, "document_id": "shared-document"})["tenant_id"] == tenant_a
    with client.start_session() as session:
        session.start_transaction()
        assert registry.get_receipt_by_idempotency_key(
            tenant_b, "shared-document", receipt_a.idempotency_key, receipts, session=session
        ) is None
        session.commit_transaction()

    original = deepcopy(_raw_receipt(receipts, receipt_a))
    for path, replacement in (
        ("receipt_payload.fingerprint", HEX_0),
        ("evidence_identity", HEX_F),
        ("version", "unsupported-version"),
        ("allocation_custody_event_id", "different-event"),
    ):
        receipts.update_one({"_id": original["_id"]}, {"$set": {path: replacement}})
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(registry.ProcessServiceAllocationRegistryPersistedRecordInvalidError):
                registry.get_receipt_by_idempotency_key(
                    tenant_a, receipt_a.document_id, receipt_a.idempotency_key, receipts, session=session
                )
            session.abort_transaction()
        receipts.replace_one({"_id": original["_id"]}, original)


# ARTIFACT: test_process_service_allocation_registry_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real Mongo P4B persistence/currentness certification only.
# TENANT POSTURE: explicit tenant/document scope; cross-tenant existence is not disclosed.
# FAIL-CLOSED POSTURE: runtime, schema, replay, event identity, CAS, and transaction failures reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns financial execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
