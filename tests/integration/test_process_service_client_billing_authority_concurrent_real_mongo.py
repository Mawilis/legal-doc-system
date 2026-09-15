"""Deterministic P6D immutable binding writer-race certificate.

TITLE: Wilsy OS Process-Service Client Billing Authority Concurrent Certificate
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-BILLING-AUTHORITY-CONCURRENT-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
TENANT BOUNDARY: Competing writes share one explicit tenant and binding identity.
TRANSACTION BOUNDARY: Two caller-owned sessions/transactions; registry owns none.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns execution and settlement.
FAIL-CLOSED: Ambiguous transaction outcomes are failures, never accepted losers.
CERTIFICATION / UPDATE DATE: 2026-09-15
"""
from datetime import datetime, timezone
from dataclasses import replace
import os
from threading import Barrier, Thread
from uuid import uuid4

import pytest
from typing import Any
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.billing.process_service_client_billing_authority import InstructionBillingBinding
from tools.eos.saas.billing.process_service_client_billing_registry import ProcessServiceClientBillingRegistry, ProcessServiceClientBillingRegistryError

URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"


class _InsertBoundary:
    """Coordinate only the real Mongo insert boundary; no result/error fabrication."""

    def __init__(self, collection: Any, barrier: Barrier) -> None:
        self._collection = collection
        self._barrier = barrier

    def insert_one(self, *args: Any, **kwargs: Any) -> Any:
        self._barrier.wait(timeout=10)
        return self._collection.insert_one(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._collection, name)


@pytest.fixture()
def mongo() -> Any:
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=2000)
        hello = client.admin.command("hello")
    except Exception as error:
        pytest.skip(f"Mongo hello unavailable: {error}")
    if hello.get("setName") != REPLICA_SET:
        client.close(); pytest.skip("wrong replica set")
    if not hello.get("isWritablePrimary", hello.get("ismaster", False)):
        client.close(); pytest.skip("no writable primary")
    database = client.get_database(f"p6dc_{uuid4().hex}", read_concern=ReadConcern("majority"), write_concern=WriteConcern("majority", j=True))
    try:
        yield client, database
    finally:
        try: client.drop_database(database.name)
        finally: client.close()


def test_two_caller_transactions_yield_one_winner_and_one_retry_loser(mongo: tuple[Any, Any]) -> None:
    client, database = mongo
    collection = database.get_collection("bindings")
    ProcessServiceClientBillingRegistry.ensure_indexes(database.get_collection("profiles"), collection)
    binding = InstructionBillingBinding("tenant-a", "binding-race", "instruction-race", "profile-1", "profile-v1", datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc), "race-evidence")
    barrier = Barrier(2); outcomes: list[str] = []; raw_errors: list[str] = []; diagnostics: list[dict[str, Any]] = []; aborted_loser = False

    def worker() -> None:
        nonlocal aborted_loser
        with client.start_session() as session:
            session.start_transaction()
            try:
                ProcessServiceClientBillingRegistry.create_binding(binding, _InsertBoundary(collection, barrier), session=session)
                session.commit_transaction(); outcomes.append("WINNER")
            except Exception as error:
                try:
                    session.abort_transaction()
                    aborted_loser = True
                except Exception: pass
                code = getattr(error, "code", "")
                raw_errors.append(type(error).__name__)
                cause: Any = error.__cause__
                details = getattr(cause, "details", {})
                labels = tuple(label for label in ("TransientTransactionError", "UnknownTransactionCommitResult") if hasattr(cause, "has_error_label") and cause.has_error_label(label))
                diagnostics.append({"exception_type": type(error).__name__, "raw_cause_type": type(cause).__name__ if cause is not None else "NONE", "raw_mongo_code": details.get("code") if isinstance(details, dict) else None, "mongo_labels": labels})
                outcomes.append("RETRY_REQUIRED" if code == "P6D_RETRY_TRANSACTION_REQUIRED" else "OTHER")

    workers = [Thread(target=worker), Thread(target=worker)]
    for thread in workers: thread.start()
    for thread in workers: thread.join(timeout=30)
    assert sorted(outcomes) == ["RETRY_REQUIRED", "WINNER"], (outcomes, raw_errors)
    assert len(diagnostics) == 1 and diagnostics[0]["raw_cause_type"] == "OperationFailure"
    assert diagnostics[0]["raw_mongo_code"] == 112
    assert "TransientTransactionError" in diagnostics[0]["mongo_labels"]
    assert "UnknownTransactionCommitResult" not in diagnostics[0]["mongo_labels"]
    assert aborted_loser is True
    print(f"LOSER_DIAGNOSTICS={diagnostics[0]}")
    assert collection.count_documents({"tenant_id": "tenant-a", "entity_identity": "binding-race"}) == 1
    assert raw_errors
    replay = ProcessServiceClientBillingRegistry.create_binding(binding, collection)
    assert replay.to_dict() == binding.to_dict()
    assert collection.count_documents({"tenant_id": "tenant-a", "entity_identity": "binding-race"}) == 1
    with pytest.raises(ProcessServiceClientBillingRegistryError, match="P6D_REPLAY_CONFLICT"):
        ProcessServiceClientBillingRegistry.create_binding(replace(binding, evidence_reference="divergent"), collection)
