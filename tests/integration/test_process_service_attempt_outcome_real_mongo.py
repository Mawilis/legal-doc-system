"""Host-backed P5E certificate for terminal outcome and ServiceExecution facts.

TITLE: Wilsy OS Process-Service Attempt Outcome Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Verify durable ATTEMPTED -> COMPLETED/NOT_COMPLETED composition through
         P1 and P2 using one caller-owned Mongo transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_attempt_outcome_real_mongo.py
TENANT BOUNDARY: UUID-isolated tenant/database; foreign reads disclose absence only.
AUTHORITY BOUNDARY: P1 owns lifecycle and ServiceExecution factories; P5E composes
                     terminal evidence only and never creates ReturnOfService.
TRANSACTION BOUNDARY: The certificate owns session/transaction start, commit, abort,
                      and cleanup; production registries do not.
FINANCIAL AUTHORITY BOUNDARY: ServiceExecution is legal-process truth; Kennel EOS
                              exclusively owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Runtime, persistence, corruption, replay, and scope failures
                         fail; only unavailable host infrastructure is skipped.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-REAL-MONGO-CERT
           certifies terminal outcomes, execution derivation, replay, isolation,
           and rollback safety.
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

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState, ServiceExecutionOutcome
from tools.eos.legal_operations.orchestration.process_service_attempt_outcome_orchestrator import transition_process_service_attempt_outcome
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_attempt_outcome_registry import ProcessServiceAttemptOutcomeRegistry

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 13, 0, tzinfo=timezone.utc)
EVIDENCE_HASH = "d" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any]]:
    """Yield majority/journaled collections and always clean the UUID database."""
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
        database = client[f"p5e_outcome_{uuid.uuid4().hex}"]
        concerns = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
        lifecycle = database.get_collection("legal_lifecycle", **concerns)
        outcomes = database.get_collection("attempt_outcomes", **concerns)
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        ProcessServiceAttemptOutcomeRegistry.ensure_indexes(outcomes)
        yield client, lifecycle, outcomes
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


def _attempt(tenant: str, suffix: str) -> ServiceAttempt:
    """Build an immutable P1 ALLOCATED -> ATTEMPTED source chain."""
    allocated = ServiceAttempt(tenant_id=tenant, attempt_id=f"attempt-{suffix}", instruction_id=f"instruction-{suffix}", document_id=f"document-{suffix}", deputy_id=f"deputy-{suffix}", allocated_at=BASE, allocation_evidence_reference=f"p5b:allocation-{suffix}")
    return allocated.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference=f"field:attempt-{suffix}", occurred_at=BASE + timedelta(minutes=1))


def _seed_attempt(client: MongoClient, lifecycle: Any, attempt: ServiceAttempt) -> str:
    """Persist one source attempt and return its exact P2 evidence identity."""
    session = _tx(client)
    try:
        LegalOperationsLifecycleRegistry.create(attempt, lifecycle, session=session)
        session.commit_transaction()
    finally:
        session.end_session()
    row = lifecycle.find_one({"tenant_id": attempt.tenant_id, "entity_type": "ServiceAttempt", "entity_identity": attempt.attempt_id})
    assert row is not None
    return row["evidence_identity"]


def test_real_mongo_terminal_outcomes_execution_replay_isolation_and_rollback(mongo_context: tuple[MongoClient, Any, Any]) -> None:
    """Certify both terminal outcomes, derived execution, replay, scope, and abort safety."""
    client, lifecycle, outcomes = mongo_context
    tenant = f"tenant-a-{uuid.uuid4().hex}"
    completed_source = _attempt(tenant, "completed")
    noncompleted_source = _attempt(tenant, "noncompleted")
    completed_identity = _seed_attempt(client, lifecycle, completed_source)
    noncompleted_identity = _seed_attempt(client, lifecycle, noncompleted_source)

    session = _tx(client)
    try:
        completed_execution = transition_process_service_attempt_outcome(tenant_id=tenant, current_evidence_identity=completed_identity, lifecycle_collection=lifecycle, outcome_collection=outcomes, outcome=ServiceAttemptState.COMPLETED, evidence_reference="field:service-completed", evidence_fingerprint=EVIDENCE_HASH, occurred_at=BASE + timedelta(minutes=2), service_execution_id="execution-completed", executed_at=BASE + timedelta(minutes=3), session=session)
        assert completed_execution.outcome is ServiceExecutionOutcome.COMPLETED
        session.commit_transaction()
    finally:
        session.end_session()

    replay_session = _tx(client)
    try:
        replay = transition_process_service_attempt_outcome(tenant_id=tenant, current_evidence_identity=completed_identity, lifecycle_collection=lifecycle, outcome_collection=outcomes, outcome=ServiceAttemptState.COMPLETED, evidence_reference="field:service-completed", evidence_fingerprint=EVIDENCE_HASH, occurred_at=BASE + timedelta(minutes=2), service_execution_id="execution-completed", executed_at=BASE + timedelta(minutes=3), session=replay_session)
        assert replay.to_dict() == completed_execution.to_dict()
        replay_session.commit_transaction()
    finally:
        replay_session.end_session()

    session = _tx(client)
    try:
        noncompleted_execution = transition_process_service_attempt_outcome(tenant_id=tenant, current_evidence_identity=noncompleted_identity, lifecycle_collection=lifecycle, outcome_collection=outcomes, outcome=ServiceAttemptState.NOT_COMPLETED, evidence_reference="field:service-not-completed", evidence_fingerprint=EVIDENCE_HASH, occurred_at=BASE + timedelta(minutes=2), service_execution_id="execution-not-completed", executed_at=BASE + timedelta(minutes=3), session=session)
        assert noncompleted_execution.outcome is ServiceExecutionOutcome.NOT_COMPLETED
        session.commit_transaction()
    finally:
        session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant, "entity_type": "ServiceExecution"}) == 2
    assert outcomes.count_documents({"tenant_id": tenant}) == 2
    assert lifecycle.count_documents({"tenant_id": tenant, "entity_type": "ReturnOfService"}) == 0
    with pytest.raises(Exception, match="M2_EVIDENCE_NOT_FOUND"):
        LegalOperationsLifecycleRegistry.get(f"tenant-b-{uuid.uuid4().hex}", completed_identity, lifecycle)

    rollback_source = _attempt(tenant, "rollback")
    rollback_identity = _seed_attempt(client, lifecycle, rollback_source)
    before_lifecycle = lifecycle.count_documents({"tenant_id": tenant})
    before_outcomes = outcomes.count_documents({"tenant_id": tenant})
    rollback_session = _tx(client)
    try:
        transition_process_service_attempt_outcome(tenant_id=tenant, current_evidence_identity=rollback_identity, lifecycle_collection=lifecycle, outcome_collection=outcomes, outcome=ServiceAttemptState.COMPLETED, evidence_reference="field:rollback", evidence_fingerprint=EVIDENCE_HASH, occurred_at=BASE + timedelta(minutes=2), service_execution_id="execution-rollback", executed_at=BASE + timedelta(minutes=3), session=rollback_session)
        rollback_session.abort_transaction()
    finally:
        rollback_session.end_session()
    assert lifecycle.count_documents({"tenant_id": tenant}) == before_lifecycle
    assert outcomes.count_documents({"tenant_id": tenant}) == before_outcomes


# ARTIFACT: test_process_service_attempt_outcome_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-REAL-MONGO-CERT
# CERTIFICATION SCOPE: host-backed terminal outcome and ServiceExecution facts only.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
