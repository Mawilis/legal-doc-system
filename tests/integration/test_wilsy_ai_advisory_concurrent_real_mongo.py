"""WILSY OS C1E-R1I deterministic concurrent real-Mongo certificate.

TITLE: WILSY AI Legal Advisory Concurrent Supersession Certificate
VERSION: v1.1.2-C1E-R1I
AUTHORITY: Wilsy OS Core Governance
EPITOME: Runs two independent caller transactions through C1D unique
         successor arbitration and proves exactly one durable winner.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_advisory_concurrent_real_mongo.py
COLLABORATION / OWNERSHIP: Certifies C1D registry concurrency; no production
                            or unit source is modified by this certificate.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.1.2-C1E-R1I adds bounded whole-transaction retry for the
           registry's explicit transient-transaction persistence signal;
           unrelated registry failures remain fail-closed.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated records; no provider/model output or secrets.
TENANT BOUNDARY: Every query and unique arbitration key includes tenant_id.
AUTHORITY BOUNDARY: Immutable advisory evidence only; no legal or financial execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Mongo unavailability skips as environment defect;
                         arbitrary exceptions are never classified as a winner.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.intelligence.adapters.legal_operations_advisory_adapter import build_legal_advisory
from tools.eos.intelligence.domain.ai_tool_orchestration import AIToolOrchestration, OrchestrationPhase, orchestration_identity
from tools.eos.intelligence.domain.legal_ai_gateway import GATEWAY_PERMISSION, LegalAIToolInvocationEvidence, TOOL_CONTRACTS
from tools.eos.intelligence.registry.next_best_action_advisory_registry import (
    COLLECTION,
    NextBestActionAdvisoryConflictError,
    NextBestActionAdvisoryRegistry,
    NextBestActionAdvisoryRegistryError,
    ensure_indexes,
)

MONGO_URI = os.getenv("C1E_MONGO_URI", os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"))
REPLICA_SET = os.getenv("C1E_MONGO_REPLICA_SET", "wilsyVendorCertRS")
TENANT = "tenant-c1e-r1b-concurrent"
STAMP = datetime(2026, 9, 17, 8, 0, tzinfo=timezone.utc)


def _result(attempt: str) -> dict[str, object]:
    """Build a bounded legal result projection for fingerprinting."""
    return {"tenant_id": TENANT, "attempt_id": attempt, "state": "ALLOCATED", "evidence_identity": f"evidence-{attempt}"}


def _chain(attempt: str, token: str, stamp: datetime) -> tuple[AIToolOrchestration, LegalAIToolInvocationEvidence, dict[str, object]]:
    """Construct immutable C1C/L7B evidence accepted by the C1D adapter."""
    principal = f"principal-{TENANT}"
    root_id = orchestration_identity(TENANT, principal, f"idempotency-{token}")
    invocation_id, result = f"invocation-{token}", _result(attempt)
    contract = TOOL_CONTRACTS["legal.attempt.read.v1"]
    root = AIToolOrchestration(root_id, TENANT, principal, root_id, OrchestrationPhase.COMPLETED, f"planner-{token}", tool_invocation_id=invocation_id, synthesis_invocation_id=f"synthesis-{token}", tool_identity="legal.attempt.read.v1", resource_identity=attempt, evidence_references=(f"evidence-{token}",), outcome="TOOL_ASSISTED", revision=1, occurred_at=stamp)
    result_fp = hashlib.sha3_512(json.dumps(result, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    invocation = LegalAIToolInvocationEvidence(invocation_id, TENANT, principal, "legal.attempt.read.v1", "v1", GATEWAY_PERMISSION, contract.underlying_permission, contract.capability, "tenant_legal_partner", f"entitlement-{TENANT}", 1, "a" * 128, "STARTER", "b" * 128, f"capacity:{TENANT}", "c" * 128, root_id, "d" * 128, "READ", f"ServiceAttempt:{attempt}", result_fp, stamp)
    return root, invocation, result


@pytest.fixture(scope="module")
def mongo_database() -> Iterator[tuple[MongoClient, Any]]:
    """Yield a writable replica-set database or skip as an environment defect."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000, retryWrites=True)
    try:
        hello = client.admin.command("hello")
    except (PyMongoError, OSError) as error:
        client.close(); pytest.skip(f"ENVIRONMENT_DEFECT: Mongo runtime unavailable ({type(error).__name__})")
    if hello.get("setName") != REPLICA_SET or hello.get("isWritablePrimary", hello.get("ismaster", False)) is not True:
        client.close(); pytest.skip("ENVIRONMENT_DEFECT: writable replica-set primary unavailable")
    database = client[f"c1e_r1b_concurrent_{uuid4().hex}"]
    try:
        yield client, database
    finally:
        client.drop_database(database.name); client.close()


def _error_code(error: BaseException) -> str:
    """Read a non-sensitive registry code from the exception contract."""
    return str(getattr(error, "code", "") or (error.args[0] if error.args else ""))


def _has_transient_transaction_label(error: BaseException) -> bool:
    """Require a causal PyMongo label before permitting whole-transaction retry."""
    cause: BaseException | None = error.__cause__ or error.__context__
    visited: set[int] = set()
    while cause is not None and id(cause) not in visited:
        visited.add(id(cause))
        has_label = getattr(cause, "has_error_label", None)
        if callable(has_label) and bool(has_label("TransientTransactionError")):
            return True
        cause = cause.__cause__ or cause.__context__
    return False


def _is_retryable_registry_error(error: BaseException) -> bool:
    """Classify only the exact persistence code with a proven transient cause."""
    return (
        type(error) is NextBestActionAdvisoryRegistryError
        and _error_code(error) == "C1D_PERSISTENCE_UNAVAILABLE"
        and _has_transient_transaction_label(error)
    )


def test_c1e_r1i_deterministic_two_session_successor_arbitration(mongo_database: tuple[MongoClient, Any]) -> None:
    """Prove one successor wins a deterministic race and one loser is bounded."""
    client, database = mongo_database
    collection = database[COLLECTION]
    ensure_indexes(collection)
    registry = NextBestActionAdvisoryRegistry(collection)
    predecessor_root, predecessor_invocation, predecessor_result = _chain("attempt-predecessor", "predecessor", STAMP)
    predecessor = build_legal_advisory(tenant_id=TENANT, scope_ref="shared-scope", root=predecessor_root, invocation=predecessor_invocation, result=predecessor_result, generated_at=STAMP)
    with client.start_session() as session:
        session.start_transaction(); registry.create_or_replay(predecessor, session=session); session.commit_transaction()
    candidates = []
    for token, hour in (("candidate-a", 9), ("candidate-b", 10)):
        root, invocation, result = _chain(f"attempt-{token}", token, datetime(2026, 9, 17, hour, 0, tzinfo=timezone.utc))
        candidates.append(build_legal_advisory(tenant_id=TENANT, scope_ref="shared-scope", root=root, invocation=invocation, result=result, generated_at=f"2026-09-17T{hour:02d}:00:00Z", supersedes_advisory_id=predecessor.advisory_id))
    barrier = threading.Barrier(2)
    outcomes: list[str] = []
    thread_errors: list[str] = []
    transient_registry_errors = 0
    retry_sessions = 0
    retry_transactions = 0
    lock = threading.Lock()
    winner_committed = threading.Event()

    def contender(candidate: Any) -> None:
        """Use one transaction, then retry the whole transaction only when required."""
        nonlocal transient_registry_errors, retry_sessions, retry_transactions
        session: Any | None = client.start_session()
        outcome: str | None = None

        def record_error(error: BaseException) -> None:
            with lock:
                thread_errors.append(f"{type(error).__name__}:{error}")

        def close_failed_session(active: Any) -> None:
            try:
                active.abort_transaction()
            except BaseException as error:
                record_error(error)
            try:
                active.end_session()
            except BaseException as error:
                record_error(error)

        try:
            session.start_transaction()
            barrier.wait(timeout=10)
            registry.create_or_replay(candidate, session=session)
            session.commit_transaction()
            winner_committed.set()
            outcome = "WIN"
        except NextBestActionAdvisoryConflictError as error:
            try:
                session.abort_transaction()
            except BaseException as abort_error:
                record_error(abort_error)
            outcome = f"BOUNDED_CONFLICT:DIRECT:{type(error).__name__}"
        except NextBestActionAdvisoryRegistryError as error:
            if not _is_retryable_registry_error(error):
                close_failed_session(session)
                session = None
                record_error(error)
            else:
                with lock:
                    transient_registry_errors += 1
                close_failed_session(session)
                session = None
                if not winner_committed.wait(timeout=30):
                    record_error(TimeoutError("winning transaction did not commit before retry"))
                else:
                    retry_session: Any | None = None
                    try:
                        retry_session = client.start_session()
                        with lock:
                            retry_sessions += 1
                        retry_session.start_transaction()
                        with lock:
                            retry_transactions += 1
                        registry.create_or_replay(candidate, session=retry_session)
                        retry_session.commit_transaction()
                        record_error(RuntimeError("transient retry unexpectedly created a second successor"))
                    except NextBestActionAdvisoryConflictError as retry_error:
                        if retry_session is None:
                            record_error(RuntimeError("retry conflict reported without a retry session"))
                        else:
                            try:
                                retry_session.abort_transaction()
                            except BaseException as abort_error:
                                record_error(abort_error)
                        outcome = f"BOUNDED_CONFLICT:RETRY:{type(retry_error).__name__}"
                    except BaseException as retry_error:
                        if retry_session is not None:
                            try:
                                retry_session.abort_transaction()
                            except BaseException as abort_error:
                                record_error(abort_error)
                        record_error(retry_error)
                    finally:
                        if retry_session is not None:
                            try:
                                retry_session.end_session()
                            except BaseException as end_error:
                                record_error(end_error)
        except BaseException as error:
            close_failed_session(session)
            session = None
            record_error(error)
        finally:
            if session is not None:
                try:
                    session.end_session()
                except BaseException as error:
                    record_error(error)
            if outcome is not None:
                with lock:
                    outcomes.append(outcome)

    threads = [threading.Thread(target=contender, args=(candidate,)) for candidate in candidates]
    for thread in threads: thread.start()
    for thread in threads: thread.join(timeout=30)
    assert all(not thread.is_alive() for thread in threads)
    assert not thread_errors
    assert sum(item == "WIN" for item in outcomes) == 1 and sum(item.startswith("BOUNDED_CONFLICT:") for item in outcomes) == 1
    assert transient_registry_errors == retry_sessions == retry_transactions
    with client.start_session() as session:
        predecessor_status = registry.get_status(tenant_id=TENANT, advisory_id=predecessor.advisory_id, session=session)
        assert predecessor_status.disposition == "STALE" and predecessor_status.superseded_by_advisory_id in {candidate.advisory_id for candidate in candidates}
        assert collection.count_documents({"tenant_id": TENANT, "scope_ref": "shared-scope"}, session=session) == 2
    assert not collection.count_documents({"provider": {"$exists": True}}) and not collection.count_documents({"model": {"$exists": True}})
    assert not collection.count_documents({"ServiceExecution": {"$exists": True}}) and not collection.count_documents({"ReturnOfService": {"$exists": True}})


# ARTIFACT: test_wilsy_ai_advisory_concurrent_real_mongo.py
# VERSION: v1.1.2-C1E-R1I
# AUTHORITY BOUNDARY: deterministic concurrency certificate only; no legal or financial authority
# TENANT POSTURE: unique successor arbitration and every query include tenant_id
# FAIL-CLOSED POSTURE: only one committed winner; transient persistence retries
#                      require a new transaction and an explicit durable conflict
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# CERTIFICATION: one deterministic two-session real-Mongo certificate; no sleeps;
#               whole-transaction transient retry is bounded and fail-closed
# END OF WILSY OS SOVEREIGN ARTIFACT
