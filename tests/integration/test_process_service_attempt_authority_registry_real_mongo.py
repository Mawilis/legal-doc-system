"""Host-backed P5B certificate for process-service attempt authority receipts.

TITLE: Wilsy OS Process-Service Attempt Authority Registry Real-Mongo Certificate
VERSION: v1.1.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify the immutable P5B receipt registry against a real, writable
         Mongo replica set: indexes, transaction ownership, durable replay,
         conflicts, tenant isolation, rollback, and strict corruption rejection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_attempt_authority_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Host-backed P5B certificate only. P4B owns allocation
                            evidence, P5A owns attempt-authorization evidence,
                            P5B owns append-only receipt persistence, and this
                            test caller owns every session and transaction.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.1.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY-REAL-MONGO-CERT
           certifies BSON-level allocation-evidence provenance round-trip,
           replay, divergence, and corruption rejection while retaining real
           replica-set indexes, tenant isolation, rollback atomicity, and all
           prior fail-closed boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and opaque evidence;
                             no provider, secret, customer, or external call.
TENANT BOUNDARY: Every registry operation is explicitly tenant-scoped; a
                 foreign tenant is represented only as governed absence.
AUTHORITY BOUNDARY: P5B persistence evidence only. This certificate does not
                    construct or transition ServiceAttempt, create service or
                    return evidence, mutate P2/P4 state, or create a pointer.
TRANSACTION BOUNDARY: The certificate starts, commits, and aborts transactions
                      solely as caller; P5B receives and propagates sessions.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; no invoice, payment, or paid
                              state is represented by legal attempt evidence.
FAIL-CLOSED DECLARATION: Runtime, index, persistence, replay, tenant, race,
                         transaction, and corruption failures remain failures;
                         no hidden runtime skips or fabricated absence are used.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.process_service_attempt_authority import (
    authorize_process_service_attempt,
)
from tools.eos.legal_operations.registry import process_service_attempt_authority_registry as registry
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationReceipt,
)


VERSION = "v1.1.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 8, 0, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128
HEX_E = "e" * 128
HEX_F = "f" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any]]:
    """Yield one verified writable replica-set namespace.

    Only the pre-certification hello/setName/writable-primary checks may report
    runtime unavailability. Once hello succeeds, index and product failures are
    propagated as certificate failures. Cleanup never changes the primary result.
    """
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            client.close()
            pytest.fail(f"host Mongo unavailable during hello: {type(error).__name__}: {error}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            client.close()
            pytest.fail(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            client.close()
            pytest.fail("replica set has no writable primary")

        database = client[f"p5b_attempt_rm_{uuid.uuid4().hex}"]
        collection = database.get_collection(
            registry.RECEIPT_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        registry.ensure_indexes(collection)
        yield client, database, collection
    finally:
        active_error = sys.exc_info()[0] is not None
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _receipt(
    tenant_id: str,
    *,
    authority_id: str = "attempt-authority-1",
    attempt_id: str = "attempt-1",
    allocated_at: datetime = BASE,
    allocation_evidence_reference: str | None = None,
) -> ProcessServiceAllocationReceipt:
    """Build one deterministic valid P4 allocation receipt for P5A."""
    return ProcessServiceAllocationReceipt(
        tenant_id=tenant_id,
        allocation_command_id=f"allocation-command-{authority_id}",
        idempotency_key=f"allocation-idempotency-{authority_id}",
        instruction_id="instruction-1",
        case_matter_id="matter-1",
        document_id=f"document-{authority_id}",
        district_id="district-1",
        sheriff_office_id="office-1",
        deputy_id="deputy-1",
        assignment_decision_id="assignment-1",
        assignment_decision_fingerprint=HEX_A,
        source_instruction_fingerprint=HEX_B,
        source_document_fingerprint=HEX_C,
        source_district_fingerprint=HEX_D,
        source_sheriff_office_fingerprint=HEX_E,
        source_deputy_fingerprint=HEX_F,
        prior_custody_chain_fingerprint=HEX_A,
        prior_custody_head_event_id=f"custody-head-{authority_id}",
        prior_custody_head_fingerprint=HEX_B,
        prior_custody_head_sequence_number=7,
        from_holder_reference="office-1",
        to_holder_reference="deputy-1",
        allocation_custody_event_id=f"custody-allocation-{authority_id}",
        allocation_evidence_reference=(
            allocation_evidence_reference
            if allocation_evidence_reference is not None
            else f"allocation-evidence-{authority_id}"
        ),
        allocated_at=allocated_at,
        allocated_document_fingerprint=HEX_C,
        allocation_custody_event_fingerprint=HEX_D,
        result_custody_chain_fingerprint=HEX_E,
    )


def _current(receipt: ProcessServiceAllocationReceipt) -> ProcessServiceAllocationCurrent:
    """Build the exact P4 current pointer correlated to a receipt."""
    return ProcessServiceAllocationCurrent(
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


def _decision(
    tenant_id: str,
    *,
    authority_id: str = "attempt-authority-1",
    attempt_id: str = "attempt-1",
    allocated_at: datetime = BASE,
    allocation_evidence_reference: str | None = None,
) -> Any:
    """Authorize one exact P5A decision from independently validated P4 evidence."""
    receipt = _receipt(
        tenant_id,
        authority_id=authority_id,
        attempt_id=attempt_id,
        allocated_at=allocated_at,
        **(
            {"allocation_evidence_reference": allocation_evidence_reference}
            if allocation_evidence_reference is not None
            else {}
        ),
    )
    return authorize_process_service_attempt(
        allocation_receipt=receipt,
        allocation_current=_current(receipt),
        attempt_authority_id=authority_id,
        attempt_id=attempt_id,
        authorized_at=allocated_at + timedelta(minutes=2),
    )


def _transaction(client: MongoClient) -> Any:
    """Start one caller-owned snapshot transaction with durable concerns."""
    session = client.start_session()
    session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    return session


def _assert_not_found(call: Any) -> None:
    """Require the exact governed tenant-scoped absence error."""
    with pytest.raises(registry.ProcessServiceAttemptAuthorityRegistryReceiptNotFoundError) as caught:
        call()
    assert caught.value.code == "P5B_ATTEMPT_AUTHORITY_NOT_FOUND"


def _get_authority(collection: Any, tenant_id: str, authority_id: str, session: Any) -> Any:
    """Read one receipt through the public authority-id API."""
    return registry.get_by_attempt_authority_id(
        tenant_id,
        authority_id,
        collection,
        session=session,
    )


def _persist_and_commit(
    client: MongoClient,
    collection: Any,
    decision: Any,
) -> Any:
    """Persist one decision in a caller transaction and commit exactly once."""
    session = _transaction(client)
    try:
        result = registry.persist(decision, collection, session=session)
        session.commit_transaction()
        return result
    finally:
        session.end_session()


def test_real_mongo_p5b_receipt_registry_certificate(
    mongo_context: tuple[MongoClient, Any, Any],
) -> None:
    """Certify P5B durability, replay, conflicts, isolation, rollback, and integrity."""
    client, database, collection = mongo_context

    for forbidden in ("start_transaction", "commit_transaction", "abort_transaction", "_client", "client", "mongo_client"):
        assert not hasattr(registry.ProcessServiceAttemptAuthorityRegistry, forbidden)

    indexes = list(collection.list_indexes())
    expected_indexes = {
        registry.AUTHORITY_INDEX_NAME: [("tenant_id", 1), ("attempt_authority_id", 1)],
        registry.ATTEMPT_INDEX_NAME: [("tenant_id", 1), ("attempt_id", 1)],
        registry.EVIDENCE_INDEX_NAME: [("tenant_id", 1), ("evidence_identity", 1)],
    }
    actual_by_name = {str(index["name"]): index for index in indexes}
    assert set(expected_indexes).issubset(actual_by_name)
    for name, key in expected_indexes.items():
        assert list(actual_by_name[name]["key"].items()) == key
        assert actual_by_name[name].get("unique") is True
    assert not any("current" in str(index["name"]).casefold() for index in indexes)

    tenant_a = "tenant-rm-a"
    tenant_b = "tenant-rm-b"
    original = _decision(tenant_a)

    with client.start_session() as inactive:
        with pytest.raises(registry.ProcessServiceAttemptAuthorityRegistryTransactionRequiredError) as caught:
            registry.persist(original, collection, session=inactive)
        assert caught.value.code == "P5B_ACTIVE_TRANSACTION_REQUIRED"
        with pytest.raises(registry.ProcessServiceAttemptAuthorityRegistryTransactionRequiredError) as read_caught:
            _get_authority(collection, tenant_a, original.attempt_authority_id, inactive)
        assert read_caught.value.code == "P5B_ACTIVE_TRANSACTION_REQUIRED"

    created = _persist_and_commit(client, collection, original)
    assert created.outcome is registry.ProcessServiceAttemptAuthorityPersistenceOutcome.CREATED
    assert created.receipt.allocation_evidence_reference == "allocation-evidence-attempt-authority-1"
    assert collection.count_documents({}) == 1

    read_session = _transaction(client)
    try:
        by_authority = _get_authority(collection, tenant_a, original.attempt_authority_id, read_session)
        by_attempt = registry.get_by_attempt_id(
            tenant_a,
            original.attempt_id,
            collection,
            session=read_session,
        )
        assert by_authority.to_dict() == created.receipt.to_dict()
        assert by_attempt.to_dict() == created.receipt.to_dict()
        assert by_authority.fingerprint == created.receipt.fingerprint
        assert by_authority.evidence_identity == created.receipt.evidence_identity
        assert by_authority.authority_decision_fingerprint == original.fingerprint
        assert by_authority.allocation_evidence_reference == "allocation-evidence-attempt-authority-1"
        read_session.commit_transaction()
    finally:
        read_session.end_session()

    replay = _persist_and_commit(client, collection, original)
    assert replay.outcome is registry.ProcessServiceAttemptAuthorityPersistenceOutcome.IDEMPOTENT_REPLAY
    assert replay.receipt.to_dict() == created.receipt.to_dict()
    assert replay.receipt.allocation_evidence_reference == "allocation-evidence-attempt-authority-1"
    assert collection.count_documents({}) == 1

    provenance_conflict = _decision(
        tenant_a,
        authority_id=original.attempt_authority_id,
        attempt_id=original.attempt_id,
        allocation_evidence_reference="allocation-evidence-divergent",
    )
    provenance_session = _transaction(client)
    try:
        with pytest.raises(registry.ProcessServiceAttemptAuthorityRegistryAuthorityIdentityConflictError) as caught:
            registry.persist(provenance_conflict, collection, session=provenance_session)
        assert caught.value.code == "P5B_ATTEMPT_AUTHORITY_IDENTITY_CONFLICT"
        provenance_session.abort_transaction()
    finally:
        provenance_session.end_session()
    assert collection.count_documents({}) == 1

    authority_conflict = _decision(tenant_a, authority_id=original.attempt_authority_id, attempt_id="attempt-2")
    authority_session = _transaction(client)
    try:
        with pytest.raises(registry.ProcessServiceAttemptAuthorityRegistryAuthorityIdentityConflictError) as caught:
            registry.persist(authority_conflict, collection, session=authority_session)
        assert caught.value.code == "P5B_ATTEMPT_AUTHORITY_IDENTITY_CONFLICT"
        authority_session.abort_transaction()
    finally:
        authority_session.end_session()
    assert collection.count_documents({}) == 1

    attempt_conflict = _decision(tenant_a, authority_id="attempt-authority-2", attempt_id=original.attempt_id)
    attempt_session = _transaction(client)
    try:
        with pytest.raises(registry.ProcessServiceAttemptAuthorityRegistryAttemptIdentityConflictError) as caught:
            registry.persist(attempt_conflict, collection, session=attempt_session)
        assert caught.value.code == "P5B_ATTEMPT_IDENTITY_CONFLICT"
        attempt_session.abort_transaction()
    finally:
        attempt_session.end_session()
    assert collection.count_documents({}) == 1

    tenant_b_decision = _decision(tenant_b, authority_id="attempt-authority-b", attempt_id="attempt-b")
    tenant_b_result = _persist_and_commit(client, collection, tenant_b_decision)
    assert tenant_b_result.receipt.tenant_id == tenant_b
    assert collection.count_documents({}) == 2
    tenant_b_read = _transaction(client)
    try:
        _assert_not_found(
            lambda: _get_authority(collection, tenant_a, tenant_b_decision.attempt_authority_id, tenant_b_read)
        )
        assert _get_authority(collection, tenant_b, tenant_b_decision.attempt_authority_id, tenant_b_read).tenant_id == tenant_b
        tenant_b_read.commit_transaction()
    finally:
        tenant_b_read.end_session()

    rollback_decision = _decision(tenant_a, authority_id="attempt-authority-rollback", attempt_id="attempt-rollback")
    rollback_session = _transaction(client)
    try:
        rollback_result = registry.persist(rollback_decision, collection, session=rollback_session)
        assert rollback_result.outcome is registry.ProcessServiceAttemptAuthorityPersistenceOutcome.CREATED
        assert _get_authority(collection, tenant_a, rollback_decision.attempt_authority_id, rollback_session).to_dict() == rollback_result.receipt.to_dict()
        rollback_session.abort_transaction()
    finally:
        rollback_session.end_session()
    after_rollback = _transaction(client)
    try:
        _assert_not_found(lambda: _get_authority(collection, tenant_a, rollback_decision.attempt_authority_id, after_rollback))
        _assert_not_found(lambda: registry.get_by_attempt_id(tenant_a, rollback_decision.attempt_id, collection, session=after_rollback))
        after_rollback.commit_transaction()
    finally:
        after_rollback.end_session()
    assert collection.count_documents({}) == 2

    pristine = collection.find_one({"tenant_id": tenant_a, "attempt_authority_id": original.attempt_authority_id})
    assert isinstance(pristine, dict)
    corruption_cases = (
        ("receipt_fingerprint", lambda row: row.__setitem__("receipt_fingerprint", "0" * 128)),
        ("evidence_identity", lambda row: row.__setitem__("evidence_identity", "1" * 128)),
        ("authority_decision_fingerprint", lambda row: row.__setitem__("authority_decision_fingerprint", "2" * 128)),
        (
            "payload_mismatch",
            lambda row: row["receipt_payload"].__setitem__("attempt_id", "tampered-attempt"),
        ),
        (
            "source_fingerprint",
            lambda row: row["receipt_payload"].__setitem__("allocation_current_fingerprint", "3" * 128),
        ),
        (
            "provenance_missing",
            lambda row: row["receipt_payload"].pop("allocation_evidence_reference"),
        ),
        (
            "provenance_altered",
            lambda row: row["receipt_payload"].__setitem__("allocation_evidence_reference", "allocation-evidence-corrupt"),
        ),
    )
    for _name, mutate in corruption_cases:
        corrupted = deepcopy(pristine)
        mutate(corrupted)
        collection.replace_one({"_id": pristine["_id"]}, corrupted)
        corruption_session = _transaction(client)
        try:
            with pytest.raises(registry.ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError) as caught:
                _get_authority(collection, tenant_a, original.attempt_authority_id, corruption_session)
            assert caught.value.code.startswith("P5B_")
            corruption_session.abort_transaction()
        finally:
            corruption_session.end_session()
        collection.replace_one({"_id": pristine["_id"]}, pristine)

    restored = _transaction(client)
    try:
        assert _get_authority(collection, tenant_a, original.attempt_authority_id, restored).to_dict() == created.receipt.to_dict()
        restored.commit_transaction()
    finally:
        restored.end_session()

    rows = list(collection.find({}))
    assert len(rows) == 2
    for row in rows:
        assert row["receipt_payload"]["allocation_evidence_reference"].startswith("allocation-evidence-")
        assert not {
            "payment", "settlement", "paid_state", "refund", "invoice", "billing_execution"
        }.intersection(row)
        assert not {
            "payment", "settlement", "paid_state", "refund", "invoice", "billing_execution"
        }.intersection(row.get("receipt_payload", {}))


# ARTIFACT: test_process_service_attempt_authority_registry_real_mongo.py
# VERSION: v1.1.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: P5B immutable receipt persistence evidence only
# TENANT POSTURE: explicit tenant-scoped queries; foreign records are absence
# FAIL-CLOSED POSTURE: runtime and product failures remain certificate failures
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution/settlement
# END OF WILSY OS SOVEREIGN ARTIFACT
