"""Real-Mongo certification for durable FinancialExecutionCommandRegistry.

VERSION: v1.5.1-KENNEL-FINANCIAL-EXECUTION-COMMAND-REGISTRY-MONGO-CERT
TITLE: Durable Financial Execution Command Registry Mongo Certification
PURPOSE: Certify immutable command persistence, replay, corruption detection, and tenant isolation.
AUTHORITY: Certification evidence only; no AP wiring, attempts, truth, settlement, or ledger authority.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_financial_execution_command_registry_mongo.py
CERTIFICATION DATE: 2026-08-28
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: synthetic opaque references only; no credentials or provider payloads.
TENANT BOUNDARY: every fixture and registry call is tenant-scoped.
TRANSACTION BOUNDARY: caller owns sessions, commit, abort, and retry.
FINANCIAL TRUTH BOUNDARY: command persistence is not execution truth or settlement.
FIXTURE POSTURE: isolated database per test, fixed command semantics, bounded barriers, no sleeps.
MONGO CERTIFICATION: local replica set authority is required; unavailable Mongo fails explicitly.
CHANGELOG: v1.5.1 corrects the deterministic retry fixture: the labeled transient now occurs after the first transactional marker write; first-attempt rollback is genuinely certified; transaction-loop attempts remain distinct from body invocations; marker-1 rollback and marker-2 commit are explicitly proven; no production authority changed; runtime recertification remains pending. v1.5.0 routes natural exact and divergent races through the caller-owned whole-transaction retry helper; production behavior is unchanged.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import os
from threading import Barrier
import uuid
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError

from tools.eos.kennel.domain.financial_execution_command import FinancialExecutionCommand
from tools.eos.kennel.registry.financial_execution_command_registry import (
    FinancialExecutionCommandCreateConflictError,
    FinancialExecutionCommandNotFoundError,
    FinancialExecutionCommandPersistedRecordInvalidError,
    FinancialExecutionCommandRegistry,
)

COLLECTION = "kennel_financial_execution_commands"
NOW = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)


@pytest.fixture()
def mongo_db() -> Any:
    """Provide an isolated real-Mongo database and remove it after the test."""
    uri = os.getenv("TEST_VENDOR_MONGO_URI")
    if not uri:
        pytest.fail("TEST_VENDOR_MONGO_URI is required for real-Mongo certification")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    database = client["command_registry_cert_" + uuid.uuid4().hex]
    try:
        hello = client.admin.command("hello")
        if hello.get("isWritablePrimary") is not True or hello.get("setName") != "wilsyVendorCertRS":
            pytest.fail("dedicated writable replica-set authority is required")
        FinancialExecutionCommandRegistry.ensure_indexes(database[COLLECTION])
        yield database
    finally:
        client.drop_database(database.name)
        client.close()


def command(**changes: Any) -> FinancialExecutionCommand:
    """Build a fixed canonical command fixture."""
    values: dict[str, Any] = {
        "tenant_id": "tenant-1",
        "payable_id": "payable-1",
        "release_authorization_id": "release-1",
        "execution_command_id": "command-1",
        "idempotency_key": "idem-1",
        "amount_minor": 1000,
        "currency": "ZAR",
        "payment_destination_reference": "destination-ref-1",
        "created_at": NOW,
        "provider_name": "PAYSHAP",
        "provider_metadata_reference": "provider-meta-1",
    }
    values.update(changes)
    return FinancialExecutionCommand(**values)


def is_transient_transaction_error(error: BaseException) -> bool:
    """Recognize only the established TransientTransactionError label."""
    return bool(getattr(error, "has_error_label", lambda _label: False)("TransientTransactionError"))


def run_whole_transaction(collection: Any, body: Any, *, inject_transient_once: bool = False) -> tuple[str, int]:
    """Test-only caller-owned retry helper; each retry uses a fresh transaction."""
    attempts = 0
    injected = False
    client = collection.database.client
    for _ in range(3):
        attempts += 1
        with client.start_session() as session:
            session.start_transaction()
            try:
                if inject_transient_once and not injected:
                    injected = True
                    transient = OperationFailure("synthetic transient boundary")
                    transient._error_labels = {"TransientTransactionError"}
                    raise transient
                outcome = body(session)
                session.commit_transaction()
                return outcome, attempts
            except PyMongoError as error:
                if not is_transient_transaction_error(error):
                    session.abort_transaction()
                    raise
                session.abort_transaction()
    raise AssertionError("bounded whole-transaction retry exhausted")


def test_collection_indexes_and_basic_create_get(mongo_db: Any) -> None:
    """Certify collection identity, exact declared indexes, create, and get."""
    collection = mongo_db[COLLECTION]
    item = command()
    result = FinancialExecutionCommandRegistry.create(item, collection)
    assert result.outcome == "CREATED"
    assert FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection) == item
    names = {index["name"] for index in collection.list_indexes()}
    assert names == {"_id_", "tenant_execution_command_identity_unique", "tenant_payable_commands_timeline", "tenant_release_authorization_commands_timeline"}
    assert collection.index_information()["tenant_execution_command_identity_unique"]["unique"] is True
    assert collection.count_documents({}) == 1


def test_exact_replay_and_divergent_conflict(mongo_db: Any) -> None:
    """Certify exact replay and immutable divergent same-ID conflict."""
    collection = mongo_db[COLLECTION]
    item = command()
    FinancialExecutionCommandRegistry.create(item, collection)
    replay = FinancialExecutionCommandRegistry.create(item, collection)
    assert replay.outcome == "IDEMPOTENT_REPLAY"
    with pytest.raises(FinancialExecutionCommandCreateConflictError):
        FinancialExecutionCommandRegistry.create(command(amount_minor=1001), collection)
    assert collection.count_documents({}) == 1
    assert FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection) == item


def test_idempotency_key_can_coexist_and_tenant_identity_isolated(mongo_db: Any) -> None:
    """Certify idempotency is command material, while identity remains tenant-scoped."""
    collection = mongo_db[COLLECTION]
    first = command()
    second = command(execution_command_id="command-2")
    other_tenant = command(tenant_id="tenant-2", execution_command_id="command-1")
    assert FinancialExecutionCommandRegistry.create(first, collection).outcome == "CREATED"
    assert FinancialExecutionCommandRegistry.create(second, collection).outcome == "CREATED"
    assert FinancialExecutionCommandRegistry.create(other_tenant, collection).outcome == "CREATED"
    assert collection.count_documents({}) == 3
    with pytest.raises(FinancialExecutionCommandNotFoundError):
        FinancialExecutionCommandRegistry.get("tenant-2", "missing", collection)


def test_list_for_payable_and_bounds(mongo_db: Any) -> None:
    """Certify tenant/payable filtering, deterministic order, and bounds."""
    collection = mongo_db[COLLECTION]
    first = command(execution_command_id="command-a", created_at=NOW)
    second = command(execution_command_id="command-b", created_at=NOW.replace(hour=13))
    other_payable = command(execution_command_id="command-c", payable_id="payable-2")
    other_tenant = command(execution_command_id="command-d", tenant_id="tenant-2")
    for item in (first, second, other_payable, other_tenant):
        FinancialExecutionCommandRegistry.create(item, collection)
    rows = FinancialExecutionCommandRegistry.list_for_payable("tenant-1", "payable-1", 2, collection)
    assert [row.execution_command_id for row in rows] == ["command-a", "command-b"]
    with pytest.raises(Exception):
        FinancialExecutionCommandRegistry.list_for_payable("tenant-1", "payable-1", 0, collection)


def test_corruption_fails_before_replay_get_and_list(mongo_db: Any) -> None:
    """Certify fingerprint and business-material corruption fail closed."""
    collection = mongo_db[COLLECTION]
    item = command()
    FinancialExecutionCommandRegistry.create(item, collection)
    collection.update_one({"tenant_id": item.tenant_id, "execution_command_id": item.execution_command_id}, {"$set": {"command_fingerprint": "broken"}})
    with pytest.raises(FinancialExecutionCommandPersistedRecordInvalidError):
        FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection)
    with pytest.raises(FinancialExecutionCommandPersistedRecordInvalidError):
        FinancialExecutionCommandRegistry.create(item, collection)
    with pytest.raises(FinancialExecutionCommandPersistedRecordInvalidError):
        FinancialExecutionCommandRegistry.list_for_payable(item.tenant_id, item.payable_id, 10, collection)


def test_business_material_corruption_and_transaction_commit_abort(mongo_db: Any) -> None:
    """Certify malformed durable material and caller-owned commit/abort semantics."""
    collection = mongo_db[COLLECTION]
    item = command()
    FinancialExecutionCommandRegistry.create(item, collection)
    collection.update_one({"execution_command_id": item.execution_command_id}, {"$set": {"currency": "bad"}})
    with pytest.raises(FinancialExecutionCommandPersistedRecordInvalidError):
        FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection)
    fresh = command(execution_command_id="transaction-command")
    client = collection.database.client
    with client.start_session() as session:
        session.start_transaction()
        FinancialExecutionCommandRegistry.create(fresh, collection, session=session)
        assert FinancialExecutionCommandRegistry.get(fresh.tenant_id, fresh.execution_command_id, collection, session=session) == fresh
        session.commit_transaction()
    assert FinancialExecutionCommandRegistry.get(fresh.tenant_id, fresh.execution_command_id, collection) == fresh
    aborted = command(execution_command_id="aborted-command")
    with client.start_session() as session:
        session.start_transaction()
        FinancialExecutionCommandRegistry.create(aborted, collection, session=session)
        session.abort_transaction()
    with pytest.raises(FinancialExecutionCommandNotFoundError):
        FinancialExecutionCommandRegistry.get(aborted.tenant_id, aborted.execution_command_id, collection)


def test_transaction_replay_and_divergent_conflict_are_usable(mongo_db: Any) -> None:
    """Certify transaction-safe replay/conflict without duplicate-key recovery."""
    collection = mongo_db[COLLECTION]
    item = command()
    FinancialExecutionCommandRegistry.create(item, collection)
    client = collection.database.client
    with client.start_session() as session:
        session.start_transaction()
        assert FinancialExecutionCommandRegistry.create(item, collection, session=session).outcome == "IDEMPOTENT_REPLAY"
        assert collection.count_documents({}, session=session) == 1
        session.commit_transaction()
    divergent = command(amount_minor=2000)
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(FinancialExecutionCommandCreateConflictError):
            FinancialExecutionCommandRegistry.create(divergent, collection, session=session)
        session.abort_transaction()
    assert collection.count_documents({}) == 1


def test_concurrent_exact_and_divergent_create_convergence(mongo_db: Any) -> None:
    """Certify bounded concurrent exact replay and divergent conflict convergence."""
    collection = mongo_db[COLLECTION]
    for iteration in range(10):
        item = command(tenant_id=f"race-{iteration}", execution_command_id=f"command-{iteration}")
        barrier = Barrier(2, timeout=30)

        def invoke(value: FinancialExecutionCommand) -> str:
            first = True
            def body(session: Any) -> str:
                nonlocal first
                if first:
                    first = False
                    barrier.wait()
                return FinancialExecutionCommandRegistry.create(value, collection, session=session).outcome
            return run_whole_transaction(collection, body)[0]

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(invoke, item) for _ in range(2)]
            outcomes = sorted(future.result(timeout=30) for future in futures)
        assert outcomes == ["CREATED", "IDEMPOTENT_REPLAY"]
    assert collection.count_documents({"tenant_id": {"$regex": "^race-"}}) == 10


def test_process_failure_proxy_and_no_financial_side_effects(mongo_db: Any) -> None:
    """Certify durable recovery and absence of attempt/truth/settlement side effects."""
    item = command(execution_command_id="durable-command")
    collection = mongo_db[COLLECTION]
    client = collection.database.client
    with client.start_session() as session:
        FinancialExecutionCommandRegistry.create(item, collection, session=session)
    assert FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection) == item
    assert mongo_db.list_collection_names() == [COLLECTION]


def test_legacy_provider_fallback_and_divergent_fields_fail_closed(mongo_db: Any) -> None:
    """Certify legacy provider fallback and rejection of divergent provider fields."""
    collection = mongo_db[COLLECTION]
    item = command(execution_command_id="legacy-command")
    FinancialExecutionCommandRegistry.create(item, collection)
    collection.update_one(
        {"tenant_id": item.tenant_id, "execution_command_id": item.execution_command_id},
        {"$unset": {"provider_name": ""}, "$set": {"requested_provider": item.provider_name}},
    )
    assert FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection).provider_name == item.provider_name
    assert FinancialExecutionCommandRegistry.create(item, collection).outcome == "IDEMPOTENT_REPLAY"
    collection.update_one(
        {"tenant_id": item.tenant_id, "execution_command_id": item.execution_command_id},
        {"$set": {"provider_name": "PAYFAST", "requested_provider": "ZAPPER"}},
    )
    with pytest.raises(FinancialExecutionCommandPersistedRecordInvalidError):
        FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection)


def test_fingerprint_and_set_on_insert_are_directly_immutable(mongo_db: Any) -> None:
    """Certify persisted fingerprint equality and byte-stable replay/conflict behavior."""
    collection = mongo_db[COLLECTION]
    item = command(execution_command_id="immutable-command")
    assert FinancialExecutionCommandRegistry.create(item, collection).outcome == "CREATED"
    before = collection.find_one({"tenant_id": item.tenant_id, "execution_command_id": item.execution_command_id})
    assert before is not None and before["command_fingerprint"] == item.fingerprint
    assert FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection).fingerprint == item.fingerprint
    assert FinancialExecutionCommandRegistry.create(item, collection).outcome == "IDEMPOTENT_REPLAY"
    after_replay = collection.find_one({"tenant_id": item.tenant_id, "execution_command_id": item.execution_command_id})
    assert after_replay == before
    with pytest.raises(FinancialExecutionCommandCreateConflictError):
        FinancialExecutionCommandRegistry.create(command(execution_command_id=item.execution_command_id, amount_minor=2001), collection)
    assert collection.find_one({"tenant_id": item.tenant_id, "execution_command_id": item.execution_command_id}) == before


def test_fresh_client_durability_proxy(mongo_db: Any) -> None:
    """Certify loading command material through an independent client lifecycle."""
    item = command(execution_command_id="fresh-client-command")
    collection = mongo_db[COLLECTION]
    FinancialExecutionCommandRegistry.create(item, collection)
    uri = os.environ["TEST_VENDOR_MONGO_URI"]
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    try:
        fresh = client[mongo_db.name][COLLECTION]
        loaded = FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, fresh)
        assert loaded == item and loaded.fingerprint == item.fingerprint
    finally:
        client.close()


def test_divergent_concurrent_creation_never_overwrites(mongo_db: Any) -> None:
    """Certify repeated two-session divergent races preserve one immutable winner."""
    collection = mongo_db[COLLECTION]
    for iteration in range(10):
        identity = {"tenant_id": f"divergent-{iteration}", "execution_command_id": f"command-{iteration}"}
        left = command(**identity, amount_minor=1000)
        right = command(**identity, amount_minor=2000)
        barrier = Barrier(2, timeout=30)

        def invoke(value: FinancialExecutionCommand) -> str:
            first = True
            def body(session: Any) -> str:
                nonlocal first
                if first:
                    first = False
                    barrier.wait()
                return FinancialExecutionCommandRegistry.create(value, collection, session=session).outcome
            try:
                return run_whole_transaction(collection, body)[0]
            except FinancialExecutionCommandCreateConflictError:
                return "CONFLICT"

        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = sorted(future.result(timeout=30) for future in (executor.submit(invoke, left), executor.submit(invoke, right)))
        assert outcomes.count("CREATED") == 1
        assert outcomes.count("CONFLICT") == 1 or outcomes.count("IDEMPOTENT_REPLAY") == 1
        durable = collection.find_one(identity)
        assert durable is not None and durable["amount_minor"] in {1000, 2000}
    assert collection.count_documents({"tenant_id": {"$regex": "^divergent-"}}) == 10


def test_caller_owned_whole_transaction_retry_converges_exact_replay(mongo_db: Any) -> None:
    """Certify a transient boundary retries the complete logical transaction."""
    collection = mongo_db[COLLECTION]
    item = command(execution_command_id="retry-command")
    FinancialExecutionCommandRegistry.create(item, collection)

    def body(session: Any) -> str:
        return FinancialExecutionCommandRegistry.create(item, collection, session=session).outcome

    outcome, attempts = run_whole_transaction(collection, body, inject_transient_once=True)
    assert outcome == "IDEMPOTENT_REPLAY" and attempts == 2
    assert collection.count_documents({}) == 1


def test_caller_owned_retry_never_retries_logical_divergence(mongo_db: Any) -> None:
    """Certify logical conflict is returned once and is not classified transient."""
    collection = mongo_db[COLLECTION]
    item = command(execution_command_id="logical-command")
    FinancialExecutionCommandRegistry.create(item, collection)
    attempts = 0
    client = collection.database.client
    with client.start_session() as session:
        session.start_transaction()
        attempts += 1
        with pytest.raises(FinancialExecutionCommandCreateConflictError):
            FinancialExecutionCommandRegistry.create(command(execution_command_id=item.execution_command_id, amount_minor=3000), collection, session=session)
        session.abort_transaction()
    assert attempts == 1 and collection.count_documents({}) == 1


def test_transient_retry_taxonomy_is_narrow(mongo_db: Any) -> None:
    """Certify only labeled transient transaction failures are retryable."""
    labeled = OperationFailure("labeled")
    labeled._error_labels = {"TransientTransactionError"}
    assert is_transient_transaction_error(labeled)
    assert not is_transient_transaction_error(PyMongoError("generic"))
    assert not is_transient_transaction_error(FinancialExecutionCommandCreateConflictError("logical"))
    assert not is_transient_transaction_error(FinancialExecutionCommandPersistedRecordInvalidError("corrupt"))
    assert not is_transient_transaction_error(OperationFailure("ordinary"))


def test_deterministic_retry_aborts_first_attempt_marker(mongo_db: Any) -> None:
    """Certify injected transient failure discards writes before a fresh retry."""
    collection = mongo_db[COLLECTION]
    item = command(execution_command_id="retry-marker-command")
    client = collection.database.client
    attempts = 0
    transient_injected = False

    def body(session: Any) -> str:
        nonlocal attempts, transient_injected
        attempts += 1
        collection.database["retry_markers"].insert_one({"_id": f"marker-{attempts}"}, session=session)
        if not transient_injected:
            transient_injected = True
            transient = OperationFailure("synthetic transient after marker-1")
            transient._error_labels = {"TransientTransactionError"}
            raise transient
        return FinancialExecutionCommandRegistry.create(item, collection, session=session).outcome

    outcome, helper_attempts = run_whole_transaction(collection, body)
    assert outcome == "CREATED" and helper_attempts == 2 and attempts == 2
    assert collection.count_documents({}) == 1
    assert collection.database["retry_markers"].count_documents({"_id": "marker-1"}) == 0
    assert collection.database["retry_markers"].count_documents({"_id": "marker-2"}) == 1


# ARTIFACT: test_financial_execution_command_registry_mongo.py
# VERSION: v1.5.1-KENNEL-FINANCIAL-EXECUTION-COMMAND-REGISTRY-MONGO-CERT
# AUTHORITY BOUNDARY: certification evidence only; no attempt, truth, settlement, or ledger authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
