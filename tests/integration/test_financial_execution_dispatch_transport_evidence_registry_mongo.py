"""Real-Mongo certification for internal transport evidence persistence.

VERSION: v1.1.2-KENNEL-FINANCIAL-EXECUTION-DISPATCH-TRANSPORT-EVIDENCE-REGISTRY-MONGO-CERT
TITLE: Dispatch Transport Evidence Registry Mongo Certification
PURPOSE: Certify immutable provider-neutral transport-boundary evidence.
AUTHORITY: Evidence only; no provider observation, execution truth, or settlement.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_financial_execution_dispatch_transport_evidence_registry_mongo.py
CERTIFICATION DATE: 2026-08-28
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque references and fingerprints only.
TENANT BOUNDARY: every query is tenant-scoped.
TRANSACTION BOUNDARY: caller owns sessions and transaction lifecycle.
CHANGELOG: v1.1.2 corrects the v1.1.1 real-Mongo timestamp replay fixture: the candidate now remains in the same BSON millisecond bucket as the existing record. The prior failure was a certification timestamp-case defect; production conflict behavior was correct. Production remains unchanged and complete static/runtime recertification is required. v1.1.1 reconstructed provenance after the prior v1.1.0 reference became indeterminate.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import os
import uuid
from typing import Any
import pytest
from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError
from tools.eos.kennel.domain.financial_execution_dispatch_transport_evidence import (
    FinancialExecutionDispatchTransportEvidence,
    TransportEvidenceDisposition,
)
from tools.eos.kennel.registry.financial_execution_dispatch_transport_evidence_registry import (
    FinancialExecutionDispatchTransportEvidenceCreateConflictError,
    FinancialExecutionDispatchTransportEvidenceInvalidRecordError,
    FinancialExecutionDispatchTransportEvidenceNotFoundError,
    FinancialExecutionDispatchTransportEvidenceRegistry,
    FinancialExecutionDispatchTransportEvidenceRegistryError,
)

COLLECTION = "kennel_financial_execution_dispatch_transport_evidence"
NOW = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)
FP = "a" * 128


def run_whole_transaction(collection: Any, body: Any) -> tuple[Any, int]:
    """Run caller-owned bounded retry with a fresh session per attempt."""
    client = collection.database.client
    for attempt in range(1, 4):
        with client.start_session() as session:
            session.start_transaction()
            try:
                result = body(session)
                session.commit_transaction()
                return result, attempt
            except PyMongoError as error:
                session.abort_transaction()
                if not error.has_error_label("TransientTransactionError"):
                    raise
    raise AssertionError("bounded whole-transaction retry exhausted")


@pytest.fixture()
def mongo_db() -> Any:
    uri = os.getenv("TEST_VENDOR_MONGO_URI")
    if not uri:
        pytest.fail("TEST_VENDOR_MONGO_URI is required for real-Mongo certification")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    database = client["transport_evidence_cert_" + uuid.uuid4().hex]
    try:
        hello = client.admin.command("hello")
        if (
            hello.get("isWritablePrimary") is not True
            or hello.get("setName") != "wilsyVendorCertRS"
        ):
            pytest.fail("dedicated writable replica-set authority is required")
        FinancialExecutionDispatchTransportEvidenceRegistry.ensure_indexes(
            database[COLLECTION]
        )
        yield database
    finally:
        client.drop_database(database.name)
        client.close()


def evidence(**changes: Any) -> FinancialExecutionDispatchTransportEvidence:
    values: dict[str, Any] = dict(
        transport_evidence_id="evidence-1",
        tenant_id="tenant-1",
        execution_command_id="command-1",
        execution_attempt_id="attempt-1",
        dispatch_claim_id="claim-1",
        provider_name="PAYSHAP",
        transport_correlation_id="corr-1",
        transport_material_fingerprint=FP,
        transport_disposition=TransportEvidenceDisposition.SEND_STARTED,
        recorded_at=NOW,
    )
    values.update(changes)
    return FinancialExecutionDispatchTransportEvidence(**values)


def test_indexes_create_get_replay_and_dispositions(mongo_db: Any) -> None:
    collection = mongo_db[COLLECTION]
    assert {item["name"] for item in collection.list_indexes()} == {
        "_id_",
        "tenant_transport_evidence_identity_unique",
        "tenant_transport_evidence_attempt_timeline",
        "tenant_transport_evidence_claim_timeline",
    }
    item = evidence()
    assert (
        FinancialExecutionDispatchTransportEvidenceRegistry.create(item, collection)
        == "CREATED"
    )
    assert (
        FinancialExecutionDispatchTransportEvidenceRegistry.create(item, collection)
        == "IDEMPOTENT_REPLAY"
    )
    assert (
        FinancialExecutionDispatchTransportEvidenceRegistry.get(
            "tenant-1", item.transport_evidence_id, collection
        )
        == item
    )
    for disposition in TransportEvidenceDisposition:
        reference = (
            "response-ref"
            if disposition is TransportEvidenceDisposition.RESPONSE_RECEIVED
            else None
        )
        assert (
            FinancialExecutionDispatchTransportEvidenceRegistry.create(
                evidence(
                    transport_evidence_id=disposition.value,
                    transport_disposition=disposition,
                    response_evidence_reference=reference,
                ),
                collection,
            )
            == "CREATED"
        )


def test_conflict_tenant_isolation_and_lists(mongo_db: Any) -> None:
    collection = mongo_db[COLLECTION]
    item = evidence()
    FinancialExecutionDispatchTransportEvidenceRegistry.create(item, collection)
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceCreateConflictError):
        FinancialExecutionDispatchTransportEvidenceRegistry.create(
            evidence(provider_name="ZAPPER"), collection
        )
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceNotFoundError):
        FinancialExecutionDispatchTransportEvidenceRegistry.get(
            "tenant-2", item.transport_evidence_id, collection
        )
    rows = FinancialExecutionDispatchTransportEvidenceRegistry.list_for_attempt(
        "tenant-1", "attempt-1", collection, limit=1
    )
    assert len(rows) == 1
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceRegistryError):
        FinancialExecutionDispatchTransportEvidenceRegistry.list_for_claim(
            "tenant-1", "claim-1", collection, limit=0
        )


def test_response_reference_contract_and_not_sent_absence(mongo_db: Any) -> None:
    collection = mongo_db[COLLECTION]
    with pytest.raises(ValueError):
        evidence(
            transport_disposition=TransportEvidenceDisposition.SENT,
            response_evidence_reference="ref",
        )
    with pytest.raises(ValueError):
        evidence(transport_disposition=TransportEvidenceDisposition.RESPONSE_RECEIVED)
    with pytest.raises(ValueError):
        evidence(transport_disposition="NOT_SENT")


def test_corruption_and_timestamp_canonicalization(mongo_db: Any) -> None:
    collection = mongo_db[COLLECTION]
    item = evidence(
        recorded_at=datetime(2026, 8, 28, 14, 0, 0, 1999, tzinfo=timezone.utc)
    )
    FinancialExecutionDispatchTransportEvidenceRegistry.create(item, collection)
    durable = FinancialExecutionDispatchTransportEvidenceRegistry.get(
        "tenant-1", item.transport_evidence_id, collection
    )
    assert durable.recorded_at.microsecond == 1000
    collection.update_one(
        {"transport_evidence_id": item.transport_evidence_id},
        {"$set": {"provider_name": "CORRUPT"}},
    )
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceInvalidRecordError):
        FinancialExecutionDispatchTransportEvidenceRegistry.get(
            "tenant-1", item.transport_evidence_id, collection
        )


def test_transaction_abort_commit_and_taxonomy(mongo_db: Any) -> None:
    collection = mongo_db[COLLECTION]
    client = collection.database.client
    item = evidence(transport_evidence_id="tx")
    with client.start_session() as session:
        session.start_transaction()
        assert (
            FinancialExecutionDispatchTransportEvidenceRegistry.create(
                item, collection, session=session
            )
            == "CREATED"
        )
        session.abort_transaction()
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceNotFoundError):
        FinancialExecutionDispatchTransportEvidenceRegistry.get(
            "tenant-1", "tx", collection
        )
    with client.start_session() as session:
        session.start_transaction()
        FinancialExecutionDispatchTransportEvidenceRegistry.create(
            item, collection, session=session
        )
        session.commit_transaction()
    error = OperationFailure("transient")
    error._error_labels = {"TransientTransactionError"}
    assert error.has_error_label("TransientTransactionError")
    assert not PyMongoError("generic").has_error_label("TransientTransactionError")


def test_exact_concurrency_and_side_effect_boundaries(mongo_db: Any) -> None:
    collection = mongo_db[COLLECTION]
    item = evidence(transport_evidence_id="concurrent")

    def create_one(_: int) -> str:
        return FinancialExecutionDispatchTransportEvidenceRegistry.create(
            item, collection
        )

    with ThreadPoolExecutor(max_workers=10) as executor:
        outcomes = [
            future.result(timeout=30)
            for future in (executor.submit(create_one, i) for i in range(10))
        ]
    assert outcomes.count("CREATED") == 1 and outcomes.count("IDEMPOTENT_REPLAY") == 9
    assert collection.count_documents({"transport_evidence_id": "concurrent"}) == 1
    assert mongo_db["kennel_financial_execution_attempts"].count_documents({}) == 0
    assert (
        mongo_db["kennel_financial_execution_dispatch_claims"].count_documents({}) == 0
    )


def test_transaction_taxonomy_and_deterministic_rollback(mongo_db: Any) -> None:
    """Certify narrow taxonomy and rollback after an in-transaction marker write."""
    collection = mongo_db[COLLECTION]
    attempts = 0
    injected = False
    item = evidence(transport_evidence_id="rollback")

    def body(session: Any) -> str:
        nonlocal attempts, injected
        attempts += 1
        mongo_db["transport_retry_markers"].insert_one(
            {"_id": f"marker-{attempts}"}, session=session
        )
        if not injected:
            injected = True
            error = OperationFailure("synthetic transient")
            error._error_labels = {"TransientTransactionError"}
            raise error
        return FinancialExecutionDispatchTransportEvidenceRegistry.create(
            item, collection, session=session
        )

    outcome, transaction_attempts = run_whole_transaction(collection, body)
    assert outcome == "CREATED"
    assert transaction_attempts == 2
    assert attempts == 2
    assert mongo_db["transport_retry_markers"].count_documents({"_id": "marker-1"}) == 0
    assert mongo_db["transport_retry_markers"].count_documents({"_id": "marker-2"}) == 1

    unknown = OperationFailure("unknown commit")
    unknown._error_labels = {"UnknownTransactionCommitResult"}
    assert unknown.has_error_label("UnknownTransactionCommitResult")
    assert not PyMongoError("unlabeled").has_error_label("TransientTransactionError")


def test_transactional_exact_and_divergent_concurrency(mongo_db: Any) -> None:
    """Certify transactional exact convergence and divergent conflict without hybrids."""
    collection = mongo_db[COLLECTION]
    exact = evidence(transport_evidence_id="tx-exact")
    left = evidence(
        transport_evidence_id="tx-divergent",
        transport_disposition=TransportEvidenceDisposition.SEND_STARTED,
    )
    right = evidence(
        transport_evidence_id="tx-divergent",
        transport_disposition=TransportEvidenceDisposition.SENT,
    )

    def invoke(item: FinancialExecutionDispatchTransportEvidence) -> str:
        return run_whole_transaction(
            collection,
            lambda session: FinancialExecutionDispatchTransportEvidenceRegistry.create(
                item, collection, session=session
            ),
        )[0]

    with ThreadPoolExecutor(max_workers=10) as executor:
        exact_outcomes = [
            future.result(timeout=30)
            for future in (executor.submit(invoke, exact) for _ in range(10))
        ]
    assert exact_outcomes.count("CREATED") == 1
    assert exact_outcomes.count("IDEMPOTENT_REPLAY") == 9
    assert collection.count_documents({"transport_evidence_id": "tx-exact"}) == 1

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(invoke, left if i % 2 == 0 else right) for i in range(10)
        ]
        outcomes: list[str] = []
        for future in futures:
            try:
                outcomes.append(future.result(timeout=30))
            except FinancialExecutionDispatchTransportEvidenceCreateConflictError:
                outcomes.append("CONFLICT")
    assert outcomes.count("CREATED") == 1
    assert outcomes.count("CONFLICT") >= 1
    assert collection.count_documents({"transport_evidence_id": "tx-divergent"}) == 1
    raw = collection.find_one({"transport_evidence_id": "tx-divergent"})
    assert raw is not None
    assert raw["transport_disposition"] in {"SEND_STARTED", "SENT"}


def test_raw_immutability_fresh_client_and_timeline_contract(mongo_db: Any) -> None:
    """Certify raw byte stability, fresh-client reload, and independent timelines."""
    collection = mongo_db[COLLECTION]
    item = evidence(transport_evidence_id="durable", recorded_at=NOW)
    assert (
        FinancialExecutionDispatchTransportEvidenceRegistry.create(item, collection)
        == "CREATED"
    )
    before = collection.find_one({"transport_evidence_id": "durable"})
    assert before is not None
    assert (
        FinancialExecutionDispatchTransportEvidenceRegistry.create(item, collection)
        == "IDEMPOTENT_REPLAY"
    )
    assert collection.find_one({"transport_evidence_id": "durable"}) == before
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceCreateConflictError):
        FinancialExecutionDispatchTransportEvidenceRegistry.create(
            evidence(transport_evidence_id="durable", provider_name="OTHER"), collection
        )
    assert collection.find_one({"transport_evidence_id": "durable"}) == before

    uri = os.environ["TEST_VENDOR_MONGO_URI"]
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    try:
        fresh = client[mongo_db.name][COLLECTION]
        assert (
            FinancialExecutionDispatchTransportEvidenceRegistry.get(
                "tenant-1", "durable", fresh
            )
            == item
        )
    finally:
        client.close()

    for i, identifier in enumerate(("timeline-b", "timeline-a")):
        FinancialExecutionDispatchTransportEvidenceRegistry.create(
            evidence(
                transport_evidence_id=identifier,
                execution_attempt_id="many",
                dispatch_claim_id="many",
                recorded_at=NOW.replace(microsecond=i),
            ),
            collection,
        )
    assert [
        row.transport_evidence_id
        for row in FinancialExecutionDispatchTransportEvidenceRegistry.list_for_attempt(
            "tenant-1", "many", collection, limit=250
        )
    ] == ["timeline-a", "timeline-b"]
    assert [
        row.transport_evidence_id
        for row in FinancialExecutionDispatchTransportEvidenceRegistry.list_for_claim(
            "tenant-1", "many", collection, limit=250
        )
    ] == ["timeline-a", "timeline-b"]
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceRegistryError):
        FinancialExecutionDispatchTransportEvidenceRegistry.list_for_attempt(
            "tenant-1", "many", collection, limit=251
        )


def test_full_timestamp_and_corruption_paths(mongo_db: Any) -> None:
    """Certify UTC/BSON canonicalization, millisecond replay, and fail-closed reads/lists."""
    collection = mongo_db[COLLECTION]
    source = datetime(2026, 8, 28, 15, 0, 0, 1999, tzinfo=timezone.utc)
    item = evidence(transport_evidence_id="time", recorded_at=source)
    FinancialExecutionDispatchTransportEvidenceRegistry.create(item, collection)
    assert item.recorded_at == source
    durable = FinancialExecutionDispatchTransportEvidenceRegistry.get(
        "tenant-1", "time", collection
    )
    assert durable.recorded_at == datetime(
        2026, 8, 28, 15, 0, 0, 1000, tzinfo=timezone.utc
    )
    assert (
        FinancialExecutionDispatchTransportEvidenceRegistry.create(
            evidence(
                transport_evidence_id="time",
                recorded_at=datetime(2026, 8, 28, 15, 0, 0, 1001, tzinfo=timezone.utc),
            ),
            collection,
        )
        == "IDEMPOTENT_REPLAY"
    )
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceCreateConflictError):
        FinancialExecutionDispatchTransportEvidenceRegistry.create(
            evidence(
                transport_evidence_id="time",
                recorded_at=datetime(2026, 8, 28, 12, 0, 0, 2000, tzinfo=timezone.utc),
            ),
            collection,
        )
    for field, value in (("recorded_at", "bad"), ("transport_disposition", "BAD")):
        collection.update_one(
            {"transport_evidence_id": "time"}, {"$set": {field: value}}
        )
        with pytest.raises(
            FinancialExecutionDispatchTransportEvidenceInvalidRecordError
        ):
            FinancialExecutionDispatchTransportEvidenceRegistry.get(
                "tenant-1", "time", collection
            )
        collection.update_one(
            {"transport_evidence_id": "time"},
            {
                "$set": {
                    field: durable.recorded_at
                    if field == "recorded_at"
                    else durable.transport_disposition.value
                }
            },
        )


def test_default_bson_hydration_non_utc_and_complete_bounds(mongo_db: Any) -> None:
    """Certify default naive BSON restoration, fixed-offset conversion, and bounds."""
    collection = mongo_db[COLLECTION]
    offset = timezone(timedelta(hours=2))
    incoming = datetime(2026, 8, 28, 15, 0, 0, 1999, tzinfo=offset)
    item = evidence(transport_evidence_id="utc-contract", recorded_at=incoming)
    FinancialExecutionDispatchTransportEvidenceRegistry.create(item, collection)
    raw = collection.find_one({"transport_evidence_id": "utc-contract"})
    assert raw is not None
    assert raw["recorded_at"].tzinfo is None
    loaded = FinancialExecutionDispatchTransportEvidenceRegistry.get(
        "tenant-1", "utc-contract", collection
    )
    assert loaded.recorded_at.tzinfo == timezone.utc
    assert loaded.recorded_at.microsecond == 1000
    assert item.recorded_at == incoming
    for value in (1, 250):
        assert FinancialExecutionDispatchTransportEvidenceRegistry.list_for_attempt(
            "tenant-1", "attempt-1", collection, limit=value
        )
        assert FinancialExecutionDispatchTransportEvidenceRegistry.list_for_claim(
            "tenant-1", "claim-1", collection, limit=value
        )
    for value in (0, 251):
        with pytest.raises(FinancialExecutionDispatchTransportEvidenceRegistryError):
            FinancialExecutionDispatchTransportEvidenceRegistry.list_for_attempt(
                "tenant-1", "attempt-1", collection, limit=value
            )
        with pytest.raises(FinancialExecutionDispatchTransportEvidenceRegistryError):
            FinancialExecutionDispatchTransportEvidenceRegistry.list_for_claim(
                "tenant-1", "claim-1", collection, limit=value
            )


def test_disposition_round_trip_and_cross_tenant_lists(mongo_db: Any) -> None:
    """Persist and rehydrate every valid disposition while proving tenant list isolation."""
    collection = mongo_db[COLLECTION]
    for index, disposition in enumerate(TransportEvidenceDisposition):
        reference = (
            "opaque-response"
            if disposition is TransportEvidenceDisposition.RESPONSE_RECEIVED
            else None
        )
        item = evidence(
            transport_evidence_id=f"roundtrip-{index}",
            transport_disposition=disposition,
            response_evidence_reference=reference,
        )
        assert (
            FinancialExecutionDispatchTransportEvidenceRegistry.create(item, collection)
            == "CREATED"
        )
        loaded = FinancialExecutionDispatchTransportEvidenceRegistry.get(
            "tenant-1", item.transport_evidence_id, collection
        )
        assert loaded.transport_disposition is disposition
        assert loaded.response_evidence_reference == reference
    other = evidence(
        transport_evidence_id="other-tenant",
        tenant_id="tenant-2",
        execution_attempt_id="attempt-1",
        dispatch_claim_id="claim-1",
    )
    FinancialExecutionDispatchTransportEvidenceRegistry.create(other, collection)
    attempt_rows = FinancialExecutionDispatchTransportEvidenceRegistry.list_for_attempt(
        "tenant-1", "attempt-1", collection
    )
    claim_rows = FinancialExecutionDispatchTransportEvidenceRegistry.list_for_claim(
        "tenant-1", "claim-1", collection
    )
    assert all(row.tenant_id == "tenant-1" for row in attempt_rows)
    assert all(row.tenant_id == "tenant-1" for row in claim_rows)


class _FailingCollection:
    """Minimal controlled collection for registry error-taxonomy certification."""

    def __init__(self, error: PyMongoError) -> None:
        self.error = error
        self.database = type(
            "Database",
            (),
            {
                "client": type(
                    "Client", (), {"start_session": lambda _self: _FakeSession()}
                )()
            },
        )()

    def update_one(self, *args: Any, **kwargs: Any) -> Any:
        raise self.error


class _FakeSession:
    """Minimal session implementing caller transaction lifecycle for taxonomy tests."""

    def __enter__(self) -> "_FakeSession":
        return self

    def __exit__(self, *_args: Any) -> None:
        return None

    def start_transaction(self) -> None:
        return None

    def commit_transaction(self) -> None:
        return None

    def abort_transaction(self) -> None:
        return None


def test_registry_error_taxonomy_and_logical_conflict_no_retry() -> None:
    """Certify passthrough labels, unlabeled wrapping, and no logical retry."""
    item = evidence()
    failing_collection: Any = _FailingCollection
    transient = OperationFailure("transient")
    transient._error_labels = {"TransientTransactionError"}
    with pytest.raises(OperationFailure) as transient_error:
        FinancialExecutionDispatchTransportEvidenceRegistry.create(
            item, failing_collection(transient)
        )
    assert transient_error.value is transient
    unknown = OperationFailure("unknown")
    unknown._error_labels = {"UnknownTransactionCommitResult"}
    with pytest.raises(OperationFailure) as unknown_error:
        FinancialExecutionDispatchTransportEvidenceRegistry.create(
            item, failing_collection(unknown)
        )
    assert unknown_error.value is unknown
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceRegistryError):
        FinancialExecutionDispatchTransportEvidenceRegistry.create(
            item, failing_collection(PyMongoError("unlabeled"))
        )

    calls = 0

    def conflict_body(_: Any) -> str:
        nonlocal calls
        calls += 1
        raise FinancialExecutionDispatchTransportEvidenceCreateConflictError("conflict")

    with pytest.raises(FinancialExecutionDispatchTransportEvidenceCreateConflictError):
        run_whole_transaction(_FailingCollection(PyMongoError("unused")), conflict_body)
    assert calls == 1


def test_corruption_first_and_downstream_sentinels(mongo_db: Any) -> None:
    """Certify malformed durable material fails before replay and downstream rows remain unchanged."""
    collection = mongo_db[COLLECTION]
    item = evidence(transport_evidence_id="corrupt-first")
    FinancialExecutionDispatchTransportEvidenceRegistry.create(item, collection)
    collection.update_one(
        {"transport_evidence_id": item.transport_evidence_id},
        {"$unset": {"provider_name": ""}},
    )
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceInvalidRecordError):
        FinancialExecutionDispatchTransportEvidenceRegistry.create(item, collection)
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceInvalidRecordError):
        FinancialExecutionDispatchTransportEvidenceRegistry.list_for_attempt(
            "tenant-1", "attempt-1", collection
        )
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceInvalidRecordError):
        FinancialExecutionDispatchTransportEvidenceRegistry.list_for_claim(
            "tenant-1", "claim-1", collection
        )
    attempt_collection = mongo_db["kennel_financial_execution_attempts"]
    claim_collection = mongo_db["kennel_financial_execution_dispatch_claims"]
    attempt_collection.insert_one(
        {"_id": "sentinel-attempt", "tenant_id": "tenant-1", "state": "DISPATCHABLE"}
    )
    claim_collection.insert_one(
        {"_id": "sentinel-claim", "tenant_id": "tenant-1", "state": "CLAIMED"}
    )
    attempt_before = attempt_collection.find_one({"_id": "sentinel-attempt"})
    claim_before = claim_collection.find_one({"_id": "sentinel-claim"})
    clean = evidence(transport_evidence_id="sentinel-evidence")
    FinancialExecutionDispatchTransportEvidenceRegistry.create(clean, collection)
    assert attempt_collection.find_one({"_id": "sentinel-attempt"}) == attempt_before
    assert claim_collection.find_one({"_id": "sentinel-claim"}) == claim_before
    assert attempt_collection.count_documents({}) == 1
    assert claim_collection.count_documents({}) == 1
    provider_collection = mongo_db["kennel_financial_execution_provider_observations"]
    truth_collection = mongo_db["kennel_financial_execution_truth"]
    provider_before = list(provider_collection.find({}).sort([("_id", 1)]))
    truth_before = list(truth_collection.find({}).sort([("_id", 1)]))
    response = evidence(
        transport_evidence_id="response-boundary",
        transport_disposition=TransportEvidenceDisposition.RESPONSE_RECEIVED,
        response_evidence_reference="opaque",
    )
    FinancialExecutionDispatchTransportEvidenceRegistry.create(response, collection)
    provider_after = list(provider_collection.find({}).sort([("_id", 1)]))
    truth_after = list(truth_collection.find({}).sort([("_id", 1)]))
    assert provider_after == provider_before
    assert truth_after == truth_before


def test_fixed_offset_timestamp_and_corruption_matrix(mongo_db: Any) -> None:
    """Certify fixed-offset conversion, sub-ms truncation, and malformed relationships."""
    collection = mongo_db[COLLECTION]
    offset = timezone(timedelta(hours=2))
    original = datetime(2026, 8, 28, 18, 15, 0, 123456, tzinfo=offset)
    item = evidence(transport_evidence_id="offset", recorded_at=original)
    FinancialExecutionDispatchTransportEvidenceRegistry.create(item, collection)
    loaded = FinancialExecutionDispatchTransportEvidenceRegistry.get(
        "tenant-1", "offset", collection
    )
    assert loaded.recorded_at == datetime(
        2026, 8, 28, 16, 15, 0, 123000, tzinfo=timezone.utc
    )
    assert item.recorded_at == original
    assert item.recorded_at.utcoffset() == timedelta(hours=2)
    assert item.recorded_at.microsecond == 123456

    bad = evidence(transport_evidence_id="bad-disposition")
    FinancialExecutionDispatchTransportEvidenceRegistry.create(bad, collection)
    collection.update_one(
        {"transport_evidence_id": "bad-disposition"},
        {"$set": {"transport_disposition": "NOT_A_REAL_DISPOSITION"}},
    )
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceInvalidRecordError):
        FinancialExecutionDispatchTransportEvidenceRegistry.get(
            "tenant-1", "bad-disposition", collection
        )
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceInvalidRecordError):
        FinancialExecutionDispatchTransportEvidenceRegistry.list_for_attempt(
            "tenant-1", "attempt-1", collection
        )

    response = evidence(
        transport_evidence_id="bad-response",
        transport_disposition=TransportEvidenceDisposition.RESPONSE_RECEIVED,
        response_evidence_reference="opaque",
    )
    FinancialExecutionDispatchTransportEvidenceRegistry.create(response, collection)
    collection.update_one(
        {"transport_evidence_id": "bad-response"},
        {"$unset": {"response_evidence_reference": ""}},
    )
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceInvalidRecordError):
        FinancialExecutionDispatchTransportEvidenceRegistry.get(
            "tenant-1", "bad-response", collection
        )
    ordinary = evidence(transport_evidence_id="bad-reference")
    FinancialExecutionDispatchTransportEvidenceRegistry.create(ordinary, collection)
    collection.update_one(
        {"transport_evidence_id": "bad-reference"},
        {"$set": {"response_evidence_reference": "injected"}},
    )
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceInvalidRecordError):
        FinancialExecutionDispatchTransportEvidenceRegistry.get(
            "tenant-1", "bad-reference", collection
        )


# ARTIFACT: financial_execution_dispatch_transport_evidence_registry_mongo.py
# VERSION: v1.1.2-KENNEL-FINANCIAL-EXECUTION-DISPATCH-TRANSPORT-EVIDENCE-REGISTRY-MONGO-CERT
# AUTHORITY BOUNDARY: certification evidence only; no provider observation, truth, settlement, or ledger authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
