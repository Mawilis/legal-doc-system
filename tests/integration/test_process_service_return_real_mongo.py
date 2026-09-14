"""Host-backed P5F ReturnOfService certificate.

TITLE: Wilsy OS Process-Service Return Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-RETURN-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: Durable ServiceExecution -> ReturnOfService composition through P1/P2.
TENANT BOUNDARY: UUID-isolated database and explicit tenant predicates.
AUTHORITY BOUNDARY: P1 factories and P2 strict hydration remain sovereign.
TRANSACTION BOUNDARY: This certificate owns sessions only to prove caller ownership;
                      production registries never start, commit, or abort.
FINANCIAL BOUNDARY: Kennel EOS exclusively owns financial execution/settlement.
FAIL-CLOSED: Host availability may skip; product, index, corruption, replay,
             chronology, and transaction failures fail the certificate.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-RETURN-REAL-MONGO-CERT certifies
           durable return generation, provenance, replay, isolation, and abort.
"""
from __future__ import annotations

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

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
    ServiceExecutionOutcome,
)
from tools.eos.legal_operations.orchestration.process_service_return_orchestrator import (
    generate_process_service_return,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)
from tools.eos.legal_operations.registry.process_service_return_registry import (
    ProcessServiceReturnRegistry,
)

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 14, 0, tzinfo=timezone.utc)
TERMINAL_FINGERPRINT = "f" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any]]:
    """Yield majority/journaled collections and clean the isolated database."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000, retryWrites=True)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"MONGO_RUNTIME_UNAVAILABLE: {type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"MONGO_REPLICA_SET_UNAVAILABLE: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("MONGO_WRITABLE_PRIMARY_UNAVAILABLE")
        database = client[f"p5f_return_{uuid.uuid4().hex}"]
        concerns = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
        lifecycle = database.get_collection("legal_lifecycle", **concerns)
        returns = database.get_collection("service_returns", **concerns)
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        ProcessServiceReturnRegistry.ensure_indexes(returns)
        yield client, lifecycle, returns
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


def _tx(client: MongoClient) -> Any:
    """Start one caller-owned transaction with snapshot/majority concerns."""
    session = client.start_session()
    session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
    return session


def _terminal_attempt(tenant: str, suffix: str, state: ServiceAttemptState) -> ServiceAttempt:
    """Build a complete ALLOCATED -> ATTEMPTED -> terminal P1 chain."""
    allocated = ServiceAttempt(
        tenant_id=tenant,
        attempt_id=f"attempt-{suffix}",
        instruction_id=f"instruction-{suffix}",
        document_id=f"document-{suffix}",
        deputy_id=f"deputy-{suffix}",
        allocated_at=BASE,
        allocation_evidence_reference=f"allocation:{suffix}",
    )
    attempted = allocated.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference=f"attempt:{suffix}",
        occurred_at=BASE + timedelta(minutes=1),
    )
    return attempted.transition_to(
        state,
        evidence_reference=f"terminal:{suffix}",
        evidence_fingerprint=TERMINAL_FINGERPRINT,
        occurred_at=BASE + timedelta(minutes=2),
    )


def _seed_execution(client: MongoClient, lifecycle: Any, tenant: str, suffix: str, state: ServiceAttemptState) -> tuple[ServiceAttempt, ServiceExecution, str]:
    """Persist all attempt snapshots and their factory-derived execution."""
    terminal = _terminal_attempt(tenant, suffix, state)
    allocated = ServiceAttempt(
        tenant_id=tenant,
        attempt_id=terminal.attempt_id,
        instruction_id=terminal.instruction_id,
        document_id=terminal.document_id,
        deputy_id=terminal.deputy_id,
        allocated_at=BASE,
        allocation_evidence_reference=f"allocation:{suffix}",
    )
    attempted = allocated.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference=f"attempt:{suffix}", occurred_at=BASE + timedelta(minutes=1))
    session = _tx(client)
    try:
        for snapshot in (allocated, attempted, terminal):
            LegalOperationsLifecycleRegistry.create(snapshot, lifecycle, session=session)
        execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id=f"execution-{suffix}", executed_at=BASE + timedelta(minutes=3))
        LegalOperationsLifecycleRegistry.create(execution, lifecycle, session=session, source_attempt=terminal)
        session.commit_transaction()
    finally:
        session.end_session()
    row = lifecycle.find_one({"tenant_id": tenant, "entity_type": "ServiceExecution", "entity_identity": execution.service_execution_id})
    assert row is not None
    return terminal, execution, row["evidence_identity"]


def test_real_mongo_return_generation_replay_isolation_corruption_and_abort(mongo_context: tuple[MongoClient, Any, Any]) -> None:
    """Prove both outcomes, exact replay, strict corruption, and caller abort."""
    client, lifecycle, returns = mongo_context
    tenant = f"tenant-a-{uuid.uuid4().hex}"
    terminal, execution, execution_identity = _seed_execution(client, lifecycle, tenant, "complete", ServiceAttemptState.COMPLETED)
    session = _tx(client)
    try:
        first = generate_process_service_return(tenant_id=tenant, execution_evidence_identity=execution_identity, lifecycle_collection=lifecycle, return_collection=returns, return_id="return-complete", generated_at=BASE + timedelta(minutes=4), session=session)
        session.commit_transaction()
    finally:
        session.end_session()
    replay_session = _tx(client)
    try:
        replay = generate_process_service_return(tenant_id=tenant, execution_evidence_identity=execution_identity, lifecycle_collection=lifecycle, return_collection=returns, return_id="return-complete", generated_at=BASE + timedelta(minutes=4), session=replay_session)
        replay_session.commit_transaction()
    finally:
        replay_session.end_session()
    assert replay.to_dict() == first.to_dict()
    assert returns.count_documents({"tenant_id": tenant}) == 1
    return_p2_row = lifecycle.find_one({"tenant_id": tenant, "entity_type": "ReturnOfService", "entity_identity": "return-complete"})
    assert return_p2_row is not None
    source_envelope = return_p2_row["source_payload"]
    assert source_envelope["service_execution"]["executed_at"] == execution.executed_at.isoformat()
    assert source_envelope["attempt"]["attempt_id"] == terminal.attempt_id
    with pytest.raises(Exception, match="P5F_REPLAY_CONFLICT"):
        conflict_session = _tx(client)
        try:
            generate_process_service_return(tenant_id=tenant, execution_evidence_identity=execution_identity, lifecycle_collection=lifecycle, return_collection=returns, return_id="return-complete", generated_at=BASE + timedelta(minutes=5), session=conflict_session)
        finally:
            conflict_session.abort_transaction()
            conflict_session.end_session()

    _, noncompleted_execution, noncompleted_identity = _seed_execution(client, lifecycle, tenant, "not-completed", ServiceAttemptState.NOT_COMPLETED)
    session = _tx(client)
    try:
        not_completed = generate_process_service_return(tenant_id=tenant, execution_evidence_identity=noncompleted_identity, lifecycle_collection=lifecycle, return_collection=returns, return_id="return-not-completed", generated_at=BASE + timedelta(minutes=4), session=session)
        session.commit_transaction()
    finally:
        session.end_session()
    assert not_completed.service_outcome is ServiceExecutionOutcome.NOT_COMPLETED
    assert execution.to_dict()["outcome"] == "COMPLETED"
    assert noncompleted_execution.to_dict()["outcome"] == "NOT_COMPLETED"

    with pytest.raises(Exception, match="M2_EVIDENCE_NOT_FOUND"):
        LegalOperationsLifecycleRegistry.get(f"tenant-b-{uuid.uuid4().hex}", execution_identity, lifecycle)

    return_row = returns.find_one({"tenant_id": tenant, "return_id": "return-complete"})
    assert return_row is not None
    pristine = dict(return_row)
    return_row["decision_fingerprint"] = "0" * 128
    returns.replace_one({"tenant_id": tenant, "return_id": "return-complete"}, return_row)
    with pytest.raises(Exception, match="P5F_RECORD_FINGERPRINT_INVALID"):
        ProcessServiceReturnRegistry.get(tenant, pristine["evidence_identity"], returns)
    returns.replace_one({"tenant_id": tenant, "return_id": "return-complete"}, pristine)

    rollback_terminal, rollback_execution, rollback_identity = _seed_execution(client, lifecycle, tenant, "rollback", ServiceAttemptState.COMPLETED)
    before = lifecycle.count_documents({"tenant_id": tenant, "entity_type": "ReturnOfService"})
    rollback = _tx(client)
    try:
        generate_process_service_return(tenant_id=tenant, execution_evidence_identity=rollback_identity, lifecycle_collection=lifecycle, return_collection=returns, return_id="return-rollback", generated_at=BASE + timedelta(minutes=4), session=rollback)
        rollback.abort_transaction()
    finally:
        rollback.end_session()
    assert lifecycle.count_documents({"tenant_id": tenant, "entity_type": "ReturnOfService"}) == before
    assert rollback_terminal.tenant_id == rollback_execution.tenant_id == tenant


# ARTIFACT: test_process_service_return_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-RETURN-REAL-MONGO-CERT
# CERTIFICATION SCOPE: host-backed P5F return authority and durable composition.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
