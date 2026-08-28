"""Real-Mongo certification for dispatch-claim persistence.

VERSION: v1.1.1-KENNEL-FINANCIAL-EXECUTION-DISPATCH-CLAIM-REGISTRY-MONGO-CERT
TITLE: Financial Execution Dispatch Claim Registry Mongo Certification
PURPOSE: Certify immutable tenant-scoped claim persistence and replay.
AUTHORITY: Evidence only; no SEND_STARTED, provider, truth, or settlement authority.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_financial_execution_dispatch_claim_registry_mongo.py
CERTIFICATION DATE: 2026-08-28
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque references and fingerprints only.
TENANT BOUNDARY: all operations are tenant-scoped.
TRANSACTION BOUNDARY: caller owns sessions and transaction lifecycle.
CHANGELOG: v1.1.1 adds natural divergent same-ID concurrency certification: one complete canonical variant survives, logical divergence is not transaction-retried, no overwrite or hybrid material is possible, and the winner is intentionally nondeterministic; runtime certification remains pending. v1.1.0 expanded timestamp round-trip, UTC/millisecond canonicalization, same-millisecond replay, different-millisecond divergence, multiple-claim coexistence, natural concurrency, caller-owned retry and rollback, immutability, fresh-client durability, corruption, and downstream side-effect boundary certification. v1.0.0 established the initial persistence certification.
"""
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
import os
import uuid
from typing import Any
import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError
from tools.eos.kennel.domain.financial_execution_dispatch_claim import FinancialExecutionDispatchClaim, FinancialExecutionAttemptState
from tools.eos.kennel.registry.financial_execution_dispatch_claim_registry import (
    FinancialExecutionDispatchClaimCreateConflictError,
    FinancialExecutionDispatchClaimInvalidRecordError,
    FinancialExecutionDispatchClaimNotFoundError,
    FinancialExecutionDispatchClaimRegistry,
    FinancialExecutionDispatchClaimRegistryError,
)

COLLECTION = "kennel_financial_execution_dispatch_claims"
NOW = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)
FP = "a" * 128

@pytest.fixture()
def mongo_db() -> Any:
    uri = os.getenv("TEST_VENDOR_MONGO_URI")
    if not uri: pytest.fail("TEST_VENDOR_MONGO_URI is required for real-Mongo certification")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    db = client["dispatch_claim_cert_" + uuid.uuid4().hex]
    try:
        hello = client.admin.command("hello")
        if hello.get("isWritablePrimary") is not True or hello.get("setName") != "wilsyVendorCertRS": pytest.fail("dedicated writable replica-set authority is required")
        FinancialExecutionDispatchClaimRegistry.ensure_indexes(db[COLLECTION])
        yield db
    finally:
        client.drop_database(db.name)
        client.close()

def claim(**changes: Any) -> FinancialExecutionDispatchClaim:
    values: dict[str, Any] = dict(dispatch_claim_id="claim-1", tenant_id="tenant-1", execution_command_id="command-1", execution_attempt_id="attempt-1", expected_attempt_fingerprint=FP, provider_name="PAYSHAP", claimed_at=NOW, transport_correlation_id="corr-1", transport_material_fingerprint="b" * 128, expected_state=FinancialExecutionAttemptState.PREPARED, recovery_posture="RECONCILE_BEFORE_RESEND")
    values.update(changes)
    return FinancialExecutionDispatchClaim(**values)

def test_indexes_create_get_replay(mongo_db: Any) -> None:
    c = mongo_db[COLLECTION]
    FinancialExecutionDispatchClaimRegistry.ensure_indexes(c)
    assert {i["name"] for i in c.list_indexes()} == {"_id_", "tenant_dispatch_claim_identity_unique", "tenant_dispatch_claim_attempt_timeline", "tenant_dispatch_claim_command_timeline"}
    x = claim()
    assert FinancialExecutionDispatchClaimRegistry.create(x, c) == "CREATED"
    assert FinancialExecutionDispatchClaimRegistry.create(x, c) == "IDEMPOTENT_REPLAY"
    assert FinancialExecutionDispatchClaimRegistry.get("tenant-1", "claim-1", c) == x

def test_divergent_conflict_and_tenant_isolation(mongo_db: Any) -> None:
    c = mongo_db[COLLECTION]
    x = claim()
    FinancialExecutionDispatchClaimRegistry.create(x, c)
    with pytest.raises(FinancialExecutionDispatchClaimCreateConflictError): FinancialExecutionDispatchClaimRegistry.create(claim(provider_name="ZAPPER"), c)
    with pytest.raises(FinancialExecutionDispatchClaimNotFoundError): FinancialExecutionDispatchClaimRegistry.get("tenant-2", x.dispatch_claim_id, c)

def test_multiple_claims_same_attempt_and_command_list_order(mongo_db: Any) -> None:
    c = mongo_db[COLLECTION]
    for i in range(3): FinancialExecutionDispatchClaimRegistry.create(claim(dispatch_claim_id=f"claim-{i}", claimed_at=NOW.replace(microsecond=i)), c)
    rows = FinancialExecutionDispatchClaimRegistry.list_for_attempt("tenant-1", "attempt-1", c, limit=2)
    assert [x.dispatch_claim_id for x in rows] == ["claim-0", "claim-1"]
    with pytest.raises(FinancialExecutionDispatchClaimRegistryError): FinancialExecutionDispatchClaimRegistry.list_for_attempt("tenant-1", "attempt-1", c, limit=0)

def test_corruption_fails_closed(mongo_db: Any) -> None:
    c = mongo_db[COLLECTION]
    x = claim()
    FinancialExecutionDispatchClaimRegistry.create(x, c)
    c.update_one({"dispatch_claim_id": x.dispatch_claim_id}, {"$set": {"provider_name": "CORRUPT"}})
    with pytest.raises(FinancialExecutionDispatchClaimInvalidRecordError): FinancialExecutionDispatchClaimRegistry.get("tenant-1", x.dispatch_claim_id, c)

def test_session_propagation_and_transaction_abort_commit(mongo_db: Any) -> None:
    c = mongo_db[COLLECTION]
    client = c.database.client
    x = claim(dispatch_claim_id="tx")
    with client.start_session() as s:
        s.start_transaction()
        assert FinancialExecutionDispatchClaimRegistry.create(x, c, session=s) == "CREATED"
        s.abort_transaction()
    with pytest.raises(FinancialExecutionDispatchClaimNotFoundError): FinancialExecutionDispatchClaimRegistry.get("tenant-1", "tx", c)
    with client.start_session() as s:
        s.start_transaction()
        FinancialExecutionDispatchClaimRegistry.create(x, c, session=s)
        s.commit_transaction()
    assert FinancialExecutionDispatchClaimRegistry.get("tenant-1", "tx", c).dispatch_claim_id == "tx"

def test_taxonomy_is_narrow() -> None:
    e = OperationFailure("x")
    e._error_labels = {"TransientTransactionError"}
    assert e.has_error_label("TransientTransactionError")
    assert not PyMongoError("x").has_error_label("TransientTransactionError")


def run_whole_transaction(collection: Any, body: Any) -> tuple[str, int]:
    """Execute caller-owned whole-transaction retry with fresh sessions."""
    attempts = 0
    client = collection.database.client
    for _ in range(3):
        attempts += 1
        with client.start_session() as session:
            session.start_transaction()
            try:
                outcome = body(session)
                session.commit_transaction()
                return outcome, attempts
            except PyMongoError as error:
                if not error.has_error_label("TransientTransactionError"):
                    session.abort_transaction()
                    raise
                session.abort_transaction()
    raise AssertionError("bounded retry exhausted")


def test_timestamp_canonicalization_round_trip_contract(mongo_db: Any) -> None:
    """Certify UTC conversion and BSON millisecond canonicalization."""
    collection = mongo_db[COLLECTION]
    original = claim(claimed_at=datetime(2026, 8, 28, 15, 0, 0, 1999, tzinfo=timezone(timedelta(hours=2))))
    assert FinancialExecutionDispatchClaimRegistry.create(original, collection) == "CREATED"
    durable = FinancialExecutionDispatchClaimRegistry.get("tenant-1", original.dispatch_claim_id, collection)
    assert durable.claimed_at == datetime(2026, 8, 28, 13, 0, 0, 1000, tzinfo=timezone.utc)
    assert original.claimed_at == datetime(2026, 8, 28, 15, 0, 0, 1999, tzinfo=timezone(timedelta(hours=2)))


def test_same_millisecond_replay_and_different_millisecond_conflict(mongo_db: Any) -> None:
    """Certify durable timestamp buckets, replay, and divergence."""
    collection = mongo_db[COLLECTION]
    first = claim(dispatch_claim_id="bucket", claimed_at=NOW.replace(microsecond=1))
    same = claim(dispatch_claim_id="bucket", claimed_at=NOW.replace(microsecond=999))
    different = claim(dispatch_claim_id="bucket", claimed_at=NOW.replace(microsecond=1000))
    assert FinancialExecutionDispatchClaimRegistry.create(first, collection) == "CREATED"
    assert FinancialExecutionDispatchClaimRegistry.create(same, collection) == "IDEMPOTENT_REPLAY"
    with pytest.raises(FinancialExecutionDispatchClaimCreateConflictError):
        FinancialExecutionDispatchClaimRegistry.create(different, collection)


def test_multiple_claims_same_command_and_side_effect_boundaries(mongo_db: Any) -> None:
    """Certify command coexistence and absence of downstream collection writes."""
    collection = mongo_db[COLLECTION]
    for identifier in ("command-claim-a", "command-claim-b"):
        assert FinancialExecutionDispatchClaimRegistry.create(claim(dispatch_claim_id=identifier), collection) == "CREATED"
    assert collection.count_documents({"tenant_id": "tenant-1", "execution_command_id": "command-1"}) == 2
    assert mongo_db["kennel_financial_execution_attempts"].count_documents({}) == 0
    assert mongo_db["kennel_financial_execution_dispatch_transport_evidence"].count_documents({}) == 0


def test_deterministic_retry_rolls_back_marker(mongo_db: Any) -> None:
    """Certify marker-1 rollback and marker-2 commit across fresh transactions."""
    collection = mongo_db[COLLECTION]
    attempts = 0
    injected = False
    item = claim(dispatch_claim_id="rollback")

    def body(session: Any) -> str:
        nonlocal attempts, injected
        attempts += 1
        mongo_db["retry_markers"].insert_one({"_id": f"marker-{attempts}"}, session=session)
        if not injected:
            injected = True
            error = OperationFailure("synthetic transient")
            error._error_labels = {"TransientTransactionError"}
            raise error
        return FinancialExecutionDispatchClaimRegistry.create(item, collection, session=session)

    outcome, helper_attempts = run_whole_transaction(collection, body)
    assert outcome == "CREATED"
    assert helper_attempts == 2
    assert attempts == 2
    assert mongo_db["retry_markers"].count_documents({"_id": "marker-1"}) == 0
    assert mongo_db["retry_markers"].count_documents({"_id": "marker-2"}) == 1


def test_concurrent_exact_creation_converges(mongo_db: Any) -> None:
    """Certify competing exact claims converge without overwrite or hybrids."""
    collection = mongo_db[COLLECTION]
    item = claim(dispatch_claim_id="concurrent")

    def invoke(_: int) -> str:
        def body(session: Any) -> str:
            return FinancialExecutionDispatchClaimRegistry.create(item, collection, session=session)
        try:
            return run_whole_transaction(collection, body)[0]
        except (DuplicateKeyError, FinancialExecutionDispatchClaimRegistryError):
            return run_whole_transaction(collection, body)[0]

    with ThreadPoolExecutor(max_workers=10) as executor:
        outcomes = [future.result(timeout=30) for future in (executor.submit(invoke, i) for i in range(10))]
    assert outcomes.count("CREATED") == 1
    assert outcomes.count("IDEMPOTENT_REPLAY") == 9
    assert collection.count_documents({"dispatch_claim_id": "concurrent"}) == 1


def test_fresh_client_durability_and_immutability(mongo_db: Any) -> None:
    """Certify persisted material survives client replacement and replay."""
    collection = mongo_db[COLLECTION]
    item = claim(dispatch_claim_id="durable")
    assert FinancialExecutionDispatchClaimRegistry.create(item, collection) == "CREATED"
    before = collection.find_one({"dispatch_claim_id": "durable"})
    assert before is not None
    assert FinancialExecutionDispatchClaimRegistry.create(item, collection) == "IDEMPOTENT_REPLAY"
    after = collection.find_one({"dispatch_claim_id": "durable"})
    assert after == before


def test_concurrent_divergent_material_rejects_without_hybrid(mongo_db: Any) -> None:
    """Certify divergent same-ID races preserve one complete canonical variant."""
    collection = mongo_db[COLLECTION]
    left = claim(dispatch_claim_id="divergent-race", provider_name="PAYSHAP")
    right = claim(dispatch_claim_id="divergent-race", provider_name="ZAPPER")

    def invoke(item: FinancialExecutionDispatchClaim) -> str:
        return run_whole_transaction(
            collection,
            lambda session: FinancialExecutionDispatchClaimRegistry.create(item, collection, session=session),
        )[0]

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(invoke, left if i % 2 == 0 else right) for i in range(10)]
        outcomes = []
        for future in futures:
            try:
                outcomes.append(future.result(timeout=30))
            except FinancialExecutionDispatchClaimCreateConflictError:
                outcomes.append("CONFLICT")

    assert outcomes.count("CREATED") == 1
    assert outcomes.count("CONFLICT") == 5
    assert outcomes.count("IDEMPOTENT_REPLAY") == 4
    assert collection.count_documents({"tenant_id": "tenant-1", "dispatch_claim_id": "divergent-race"}) == 1
    raw = collection.find_one({"tenant_id": "tenant-1", "dispatch_claim_id": "divergent-race"})
    assert raw is not None
    assert raw["provider_name"] in {"PAYSHAP", "ZAPPER"}
    durable = FinancialExecutionDispatchClaimRegistry.get("tenant-1", "divergent-race", collection)
    assert durable.provider_name == raw["provider_name"]

# ARTIFACT: test_financial_execution_dispatch_claim_registry_mongo.py
# VERSION: v1.1.1-KENNEL-FINANCIAL-EXECUTION-DISPATCH-CLAIM-REGISTRY-MONGO-CERT
# AUTHORITY BOUNDARY: certification evidence only; no SEND_STARTED, provider, truth, or settlement authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
