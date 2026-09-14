"""Host-backed P5C certificate for the process-service attempt handoff.

TITLE: Wilsy OS Process-Service Attempt Orchestrator Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify the durable P5B receipt -> P5C composition -> P1 ALLOCATED
         snapshot -> P2 lifecycle persistence chain against a real writable
         Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_attempt_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: P5B remains the durable attempt-authority source;
                            P1 owns lifecycle semantics; P2 owns lifecycle
                            persistence; this test caller owns all sessions,
                            transactions, and isolated-database cleanup.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR-REAL-MONGO-CERT
           establishes host-backed durability, replay, rollback, corruption,
           tenant isolation, provenance, and transaction-ownership evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic identifiers only; no
                             customer, provider, credential, or PII expansion.
TENANT BOUNDARY: Every P5B and P2 operation is explicitly tenant-scoped;
                 foreign tenant authority is governed absence.
AUTHORITY BOUNDARY: P5C composition only. P5B is the sole durable authority;
                    P5C creates only the initial P1 ALLOCATED snapshot.
TRANSACTION BOUNDARY: The caller starts, commits, aborts, and ends every
                      session. P5C never owns transaction lifecycle or retries.
FINANCIAL AUTHORITY BOUNDARY: No billing, invoice, payment, execution, or
                              settlement authority; Kennel EOS exclusively owns
                              financial execution and settlement.
FAIL-CLOSED DECLARATION: Runtime unavailability, corruption, divergence,
                         persistence failure, and scope mismatch fail rather
                         than becoming fabricated lifecycle success.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import sys
from typing import Any, Iterator, cast
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.legal_operations.orchestration.process_service_attempt_orchestrator as p5c
from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttemptState
from tools.eos.legal_operations.domain.process_service_attempt_authority import (
    authorize_process_service_attempt,
)
from tools.eos.legal_operations.registry import process_service_attempt_authority_registry as p5b
from tools.eos.legal_operations.registry import legal_operations_lifecycle_registry as p2
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)
from tools.eos.legal_operations.registry.process_service_allocation_registry import (  # type: ignore[import-not-found]
    ProcessServiceAllocationCurrent as RegistryAllocationCurrent,
    ProcessServiceAllocationReceipt as RegistryAllocationReceipt,
)


VERSION = "v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR-REAL-MONGO-CERT"
MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 8, 0, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128
HEX_E = "e" * 128
HEX_F = "f" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any, Any]]:
    """Yield one verified writable replica-set database and clean it finally."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000, retryWrites=True)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(f"MONGO_RUNTIME_UNAVAILABLE: {type(error).__name__}: {error}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(f"MONGO_REPLICA_SET_MISMATCH: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("MONGO_WRITABLE_PRIMARY_UNAVAILABLE")
        database = client[f"p5c_attempt_rm_{uuid.uuid4().hex}"]
        concerns = {
            "write_concern": WriteConcern(w="majority", j=True),
            "read_concern": ReadConcern("majority"),
        }
        authority = database.get_collection(p5b.RECEIPT_COLLECTION, **concerns)
        lifecycle = database.get_collection(p2.COLLECTION, **concerns)
        p5b.ProcessServiceAttemptAuthorityRegistry.ensure_indexes(authority)
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        yield client, database, authority, lifecycle
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


def _allocation_receipt(tenant_id: str, authority_id: str, *, attempt_id: str) -> RegistryAllocationReceipt:
    """Build valid synthetic P4 receipt evidence for the setup-only P5A path."""
    return RegistryAllocationReceipt(
        tenant_id=tenant_id,
        allocation_command_id=f"allocation-command-{authority_id}",
        idempotency_key=f"allocation-idempotency-{authority_id}",
        instruction_id="instruction-p5c",
        case_matter_id="matter-p5c",
        document_id=f"document-{attempt_id}",
        district_id="district-p5c",
        sheriff_office_id="office-p5c",
        deputy_id="deputy-p5c",
        assignment_decision_id="assignment-p5c",
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
        from_holder_reference="office-p5c",
        to_holder_reference="deputy-p5c",
        allocation_custody_event_id=f"custody-allocation-{authority_id}",
        allocation_evidence_reference=f"allocation-evidence-{authority_id}",
        allocated_at=BASE,
        allocated_document_fingerprint=HEX_C,
        allocation_custody_event_fingerprint=HEX_D,
        result_custody_chain_fingerprint=HEX_E,
    )


def _allocation_current(receipt: RegistryAllocationReceipt) -> RegistryAllocationCurrent:
    """Correlate the setup P4 current pointer exactly to its receipt."""
    return RegistryAllocationCurrent(
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


def _decision(tenant_id: str, authority_id: str, *, attempt_id: str) -> Any:
    """Create P5B authority only through canonical P4 -> P5A production APIs."""
    receipt = _allocation_receipt(tenant_id, authority_id, attempt_id=attempt_id)
    return authorize_process_service_attempt(
        allocation_receipt=receipt,
        allocation_current=_allocation_current(receipt),
        attempt_authority_id=authority_id,
        attempt_id=attempt_id,
        authorized_at=BASE + timedelta(minutes=2),
    )


def _transaction(client: MongoClient) -> Any:
    """Start one caller-owned snapshot transaction with durable concerns."""
    session = client.start_session()
    session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    return session


def _persist_authority(client: MongoClient, authority: Any, decision: Any) -> Any:
    """Persist setup authority and commit it as the caller, never inside P5C."""
    session = _transaction(client)
    try:
        result = p5b.ProcessServiceAttemptAuthorityRegistry.persist(decision, authority, session=session)
        session.commit_transaction()
        return result
    finally:
        session.end_session()


def _p2_get(client: MongoClient, lifecycle: Any, tenant: str, evidence_identity: str) -> Any:
    """Hydrate one P2 snapshot in a fresh caller-owned read transaction."""
    session = _transaction(client)
    try:
        value = LegalOperationsLifecycleRegistry.get(tenant, evidence_identity, lifecycle, session=session)
        session.commit_transaction()
        return value
    finally:
        session.end_session()


def test_real_mongo_p5c_handoff_certificate(
    mongo_context: tuple[MongoClient, Any, Any, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Certify real P5B authority handoff, durable P2 replay, rollback, and isolation."""
    client, database, authority, lifecycle = mongo_context
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"
    authority_id = f"authority-{uuid.uuid4().hex}"
    attempt_id = f"attempt-{uuid.uuid4().hex}"
    decision = _decision(tenant_a, authority_id, attempt_id=attempt_id)
    seeded = _persist_authority(client, authority, decision)
    assert seeded.receipt.allocation_evidence_reference == f"allocation-evidence-{authority_id}"

    read_session = _transaction(client)
    try:
        durable_receipt = p5b.ProcessServiceAttemptAuthorityRegistry.get_by_attempt_authority_id(
            tenant_a, authority_id, authority, session=read_session
        )
    finally:
        read_session.abort_transaction()
        read_session.end_session()
    assert durable_receipt.to_dict() == seeded.receipt.to_dict()

    observed: list[tuple[str, object]] = []
    original_p5b = p5c.ProcessServiceAttemptAuthorityRegistry.get_by_attempt_authority_id
    original_p2 = p5c.LegalOperationsLifecycleRegistry.create

    def observed_p5b(tenant: str, locator: str, collection: object, *, session: object) -> object:
        observed.append(("p5b", session))
        return original_p5b(tenant, locator, collection, session=session)

    def observed_p2(value: object, collection: object, *, session: object, **kwargs: object) -> object:
        observed.append(("p2", session))
        return original_p2(cast(Any, value), collection, session=session)

    monkeypatch.setattr(p5c.ProcessServiceAttemptAuthorityRegistry, "get_by_attempt_authority_id", staticmethod(observed_p5b))
    monkeypatch.setattr(p5c.LegalOperationsLifecycleRegistry, "create", staticmethod(observed_p2))

    session = _transaction(client)
    try:
        attempt = p5c.orchestrate_process_service_attempt(
            tenant_id=tenant_a,
            attempt_authority_id=authority_id,
            attempt_authority_collection=authority,
            lifecycle_collection=lifecycle,
            session=session,
        )
        assert attempt.state is ServiceAttemptState.ALLOCATED
        assert attempt.transition_history == ()
        assert attempt.tenant_id == durable_receipt.tenant_id
        assert attempt.attempt_id == durable_receipt.attempt_id
        assert attempt.instruction_id == durable_receipt.instruction_id
        assert attempt.document_id == durable_receipt.document_id
        assert attempt.deputy_id == durable_receipt.deputy_id
        assert attempt.allocated_at == durable_receipt.allocated_at
        assert attempt.allocation_evidence_reference == durable_receipt.allocation_evidence_reference
        assert [name for name, _ in observed] == ["p5b", "p2"]
        assert observed[0][1] is session and observed[1][1] is session
        session.commit_transaction()
    finally:
        session.end_session()

    attempt_record = lifecycle.find_one(
        {"tenant_id": tenant_a, "entity_type": "ServiceAttempt", "entity_identity": attempt_id}
    )
    assert attempt_record is not None
    durable_attempt = _p2_get(client, lifecycle, tenant_a, attempt_record["evidence_identity"])
    assert durable_attempt.to_dict() == attempt.to_dict()
    assert durable_attempt.allocation_evidence_reference == durable_receipt.allocation_evidence_reference
    committed_count = lifecycle.count_documents({"tenant_id": tenant_a, "attempt_id": attempt_id})

    replay_session = _transaction(client)
    try:
        replay = p5c.orchestrate_process_service_attempt(
            tenant_id=tenant_a,
            attempt_authority_id=authority_id,
            attempt_authority_collection=authority,
            lifecycle_collection=lifecycle,
            session=replay_session,
        )
        assert replay.to_dict() == attempt.to_dict()
        replay_session.commit_transaction()
    finally:
        replay_session.end_session()
    assert lifecycle.count_documents({"tenant_id": tenant_a, "attempt_id": attempt_id}) == committed_count

    rollback_authority = f"authority-rollback-{uuid.uuid4().hex}"
    rollback_attempt = f"attempt-rollback-{uuid.uuid4().hex}"
    _persist_authority(client, authority, _decision(tenant_a, rollback_authority, attempt_id=rollback_attempt))
    rollback_session = _transaction(client)
    try:
        rolled = p5c.orchestrate_process_service_attempt(
            tenant_id=tenant_a,
            attempt_authority_id=rollback_authority,
            attempt_authority_collection=authority,
            lifecycle_collection=lifecycle,
            session=rollback_session,
        )
        assert rolled.state is ServiceAttemptState.ALLOCATED
        rollback_session.abort_transaction()
    finally:
        rollback_session.end_session()
    assert lifecycle.count_documents({"tenant_id": tenant_a, "attempt_id": rollback_attempt}) == 0
    rollback_read = _transaction(client)
    try:
        assert p5b.ProcessServiceAttemptAuthorityRegistry.get_by_attempt_authority_id(
            tenant_a, rollback_authority, authority, session=rollback_read
        ).attempt_id == rollback_attempt
        rollback_read.abort_transaction()
    finally:
        rollback_read.end_session()

    cross_session = _transaction(client)
    try:
        with pytest.raises(p5b.ProcessServiceAttemptAuthorityRegistryReceiptNotFoundError) as cross_error:
            p5c.orchestrate_process_service_attempt(
                tenant_id=tenant_b,
                attempt_authority_id=authority_id,
                attempt_authority_collection=authority,
                lifecycle_collection=lifecycle,
                session=cross_session,
            )
        assert cross_error.value.code == "P5B_ATTEMPT_AUTHORITY_NOT_FOUND"
        cross_session.abort_transaction()
    finally:
        cross_session.end_session()
    assert lifecycle.count_documents({"tenant_id": tenant_b}) == 0

    corrupt_authority = f"authority-corrupt-{uuid.uuid4().hex}"
    corrupt_attempt = f"attempt-corrupt-{uuid.uuid4().hex}"
    _persist_authority(client, authority, _decision(tenant_a, corrupt_authority, attempt_id=corrupt_attempt))
    pristine = authority.find_one({"tenant_id": tenant_a, "attempt_authority_id": corrupt_authority})
    assert pristine is not None
    authority.update_one(
        {"_id": pristine["_id"]},
        {"$unset": {"receipt_payload.allocation_evidence_reference": ""}},
    )
    corrupt_session = _transaction(client)
    try:
        with pytest.raises(p5b.ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError):
            p5c.orchestrate_process_service_attempt(
                tenant_id=tenant_a,
                attempt_authority_id=corrupt_authority,
                attempt_authority_collection=authority,
                lifecycle_collection=lifecycle,
                session=corrupt_session,
            )
        corrupt_session.abort_transaction()
    finally:
        corrupt_session.end_session()
    assert lifecycle.count_documents({"tenant_id": tenant_a, "attempt_id": corrupt_attempt}) == 0
    authority.replace_one({"_id": pristine["_id"]}, pristine)

    assert not hasattr(p5c, "ProcessServiceAllocationReceipt")
    assert not hasattr(p5c, "authorize_process_service_attempt")
    assert not hasattr(p5c, "ServiceExecution")
    assert not hasattr(p5c, "ReturnOfService")
    assert not any(name in vars(p5c) for name in ("MongoClient", "client", "mongo_client"))


# ARTIFACT: test_process_service_attempt_orchestrator_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: host-backed P5C composition certificate only.
# TENANT POSTURE: isolated synthetic tenants and explicit tenant-scoped reads.
# FAIL-CLOSED POSTURE: unavailable runtime, corruption, divergence, and rollback failures reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
