"""Host-backed certificate for durable P5D field-attempt transitions.

TITLE: Wilsy OS Process-Service Attempt Transition Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Verify one caller-owned Mongo transaction persists an immutable
         P1 ALLOCATED -> ATTEMPTED evidence snapshot through P2 and P5D.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_attempt_transition_real_mongo.py
TENANT BOUNDARY: UUID-isolated tenants and database; foreign lookups are absent.
AUTHORITY BOUNDARY: P1 lifecycle and P2 persistence remain canonical; P5D never
                     creates completion, execution, return, or financial truth.
TRANSACTION BOUNDARY: This certificate starts, commits, aborts, and ends sessions.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Runtime and product failures fail; only unavailable
                         host infrastructure is skipped.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-REAL-MONGO-CERT
           certifies durable field evidence, replay, isolation, and rollback.
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

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState
from tools.eos.legal_operations.orchestration.process_service_attempt_transition_orchestrator import transition_process_service_attempt
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_attempt_transition_registry import ProcessServiceAttemptTransitionRegistry

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 11, 0, tzinfo=timezone.utc)
EVIDENCE_HASH = "b" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any]]:
    """Yield verified writable collections and always close/drop safely."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500, retryWrites=True)
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
        database = client[f"p5d_transition_{uuid.uuid4().hex}"]
        concerns = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
        lifecycle = database.get_collection("legal_lifecycle", **concerns)
        transitions = database.get_collection("attempt_transitions", **concerns)
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        ProcessServiceAttemptTransitionRegistry.ensure_indexes(transitions)
        yield client, lifecycle, transitions
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


def _session(client: MongoClient) -> Any:
    """Start one caller-owned transaction with durable concerns."""
    session = client.start_session()
    session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
    return session


def test_real_mongo_allocated_to_attempted_replay_isolation_and_rollback(mongo_context: tuple[MongoClient, Any, Any]) -> None:
    """Persist one transition, replay it exactly, reject foreign scope, and rollback a second write."""
    client, lifecycle, transitions = mongo_context
    tenant = f"tenant-a-{uuid.uuid4().hex}"
    source = ServiceAttempt(
        tenant_id=tenant,
        attempt_id=f"attempt-{uuid.uuid4().hex}",
        instruction_id="instruction-real",
        document_id="document-real",
        deputy_id="deputy-real",
        allocated_at=BASE,
        allocation_evidence_reference="p5b:allocation-real",
    )
    create_session = _session(client)
    try:
        LegalOperationsLifecycleRegistry.create(source, lifecycle, session=create_session)
        create_session.commit_transaction()
    finally:
        create_session.end_session()
    source_identity = lifecycle.find_one({"tenant_id": tenant, "entity_type": "ServiceAttempt"})["evidence_identity"]
    transition_session = _session(client)
    try:
        result = transition_process_service_attempt(
            tenant_id=tenant,
            current_evidence_identity=source_identity,
            lifecycle_collection=lifecycle,
            transition_collection=transitions,
            evidence_reference="field:real-observation",
            evidence_fingerprint=EVIDENCE_HASH,
            occurred_at=BASE + timedelta(minutes=1),
            session=transition_session,
        )
        assert result.state is ServiceAttemptState.ATTEMPTED
        transition_session.commit_transaction()
    finally:
        transition_session.end_session()
    replay_session = _session(client)
    try:
        replay = transition_process_service_attempt(
            tenant_id=tenant,
            current_evidence_identity=source_identity,
            lifecycle_collection=lifecycle,
            transition_collection=transitions,
            evidence_reference="field:real-observation",
            evidence_fingerprint=EVIDENCE_HASH,
            occurred_at=BASE + timedelta(minutes=1),
            session=replay_session,
        )
        assert replay.to_dict() == result.to_dict()
        replay_session.commit_transaction()
    finally:
        replay_session.end_session()
    assert lifecycle.count_documents({"tenant_id": tenant}) == 2
    assert transitions.count_documents({"tenant_id": tenant}) == 1
    rollback_source = ServiceAttempt(
        tenant_id=tenant,
        attempt_id=f"attempt-{uuid.uuid4().hex}",
        instruction_id="instruction-real",
        document_id="document-rollback",
        deputy_id="deputy-real",
        allocated_at=BASE,
        allocation_evidence_reference="p5b:allocation-rollback",
    )
    rollback_session = _session(client)
    try:
        LegalOperationsLifecycleRegistry.create(rollback_source, lifecycle, session=rollback_session)
        rollback_identity = lifecycle.find_one(
            {
                "tenant_id": tenant,
                "entity_type": "ServiceAttempt",
                "entity_identity": rollback_source.attempt_id,
            },
            session=rollback_session,
        )["evidence_identity"]
        transition_process_service_attempt(
            tenant_id=tenant,
            current_evidence_identity=rollback_identity,
            lifecycle_collection=lifecycle,
            transition_collection=transitions,
            evidence_reference="field:rollback-observation",
            evidence_fingerprint=EVIDENCE_HASH,
            occurred_at=BASE + timedelta(minutes=1),
            session=rollback_session,
        )
        rollback_session.abort_transaction()
    finally:
        rollback_session.end_session()
    assert lifecycle.count_documents({"tenant_id": tenant}) == 2
    assert transitions.count_documents({"tenant_id": tenant}) == 1
    foreign = f"tenant-b-{uuid.uuid4().hex}"
    with pytest.raises(Exception, match="M2_EVIDENCE_NOT_FOUND"):
        LegalOperationsLifecycleRegistry.get(foreign, source_identity, lifecycle)


# ARTIFACT: test_process_service_attempt_transition_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-REAL-MONGO-CERT
# CERTIFICATION SCOPE: host-backed P5D durability; no completion or financial truth.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
