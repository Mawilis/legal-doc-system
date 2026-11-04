"""Host-backed platform dunning projection certification on disposable Mongo RS."""
from __future__ import annotations

from datetime import datetime, timezone
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Iterator
from urllib.parse import urlparse

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.billing.platform_dunning_evaluator import evaluate_platform_dunning
from tools.eos.saas.billing.platform_dunning_registry import (
    COLLECTION as DUNNING_PROJECTION_COLLECTION,
    PlatformDunningRegistry,
    PlatformDunningRevisionConflict,
)


DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
REPLICA_SET = "wilsyVendorCertRS"
TENANT = "tenant-platform-dunning-real"
SUBSCRIPTION = "sub-platform-dunning-real"
POLICY = "a" * 128
NOW = datetime(2026, 11, 4, 10, tzinfo=timezone.utc)


def _uri() -> str:
    value = os.getenv("TEST_VENDOR_MONGO_URI", DEFAULT_URI)
    parsed = urlparse(value)
    if parsed.scheme != "mongodb" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("PLATFORM_DUNNING_REAL_MONGO_LOOPBACK_REQUIRED")
    return value


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any]]:
    client: MongoClient[Any] = MongoClient(
        _uri(),
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
    )
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != REPLICA_SET or hello.get("isWritablePrimary") is not True:
            pytest.fail("PLATFORM_DUNNING_WRITABLE_REPLICA_SET_REQUIRED")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("PLATFORM_DUNNING_TRANSACTIONS_REQUIRED")
    except Exception as error:
        client.close()
        pytest.fail(f"PLATFORM_DUNNING_MONGO_UNAVAILABLE:{type(error).__name__}")
    database = client[f"wilsy_platform_dunning_{uuid.uuid4().hex}"]
    try:
        yield client, database
    finally:
        client.drop_database(database.name)
        client.close()


def test_real_mongo_unique_identity_revision_replay_and_tenant_isolation(
    mongo_context: tuple[MongoClient[Any], Any],
) -> None:
    client, database = mongo_context
    collection = database.get_collection(
        DUNNING_PROJECTION_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    PlatformDunningRegistry.ensure_indexes(collection)

    first = PlatformDunningRegistry.transition(
        tenant_id=TENANT,
        subscription_id=SUBSCRIPTION,
        state="WARNING",
        invoice_ids=("invoice-b", "invoice-a"),
        days_overdue=7,
        policy_fingerprint=POLICY,
        expected_revision=0,
        collection=collection,
        evaluated_at=NOW,
    )
    assert first["revision"] == 1
    assert PlatformDunningRegistry.get("other-tenant", SUBSCRIPTION, collection) is None

    replay = PlatformDunningRegistry.transition(
        tenant_id=TENANT,
        subscription_id=SUBSCRIPTION,
        state="WARNING",
        invoice_ids=("invoice-a", "invoice-b"),
        days_overdue=7,
        policy_fingerprint=POLICY,
        expected_revision=1,
        collection=collection,
        evaluated_at=NOW,
    )
    assert replay == first
    assert collection.count_documents({"tenant_id": TENANT, "subscription_id": SUBSCRIPTION}) == 1

    second = PlatformDunningRegistry.transition(
        tenant_id=TENANT,
        subscription_id=SUBSCRIPTION,
        state="CRITICAL",
        invoice_ids=("invoice-a", "invoice-b", "invoice-c"),
        days_overdue=10,
        policy_fingerprint=POLICY,
        expected_revision=1,
        collection=collection,
        evaluated_at=NOW,
    )
    assert second["revision"] == 2
    with pytest.raises(PlatformDunningRevisionConflict):
        PlatformDunningRegistry.transition(
            tenant_id=TENANT,
            subscription_id=SUBSCRIPTION,
            state="SUSPENSION_REVIEW",
            invoice_ids=("invoice-a",),
            days_overdue=14,
            policy_fingerprint=POLICY,
            expected_revision=1,
            collection=collection,
            evaluated_at=NOW,
        )

    indexes = {item["name"]: item for item in collection.list_indexes()}
    assert indexes["platform_dunning_tenant_subscription_unique"]["unique"] is True


def test_real_mongo_caller_owned_transaction_rollback(
    mongo_context: tuple[MongoClient[Any], Any],
) -> None:
    client, database = mongo_context
    collection = database.get_collection(
        DUNNING_PROJECTION_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    PlatformDunningRegistry.ensure_indexes(collection)

    with pytest.raises(RuntimeError, match="synthetic abort"):
        with client.start_session() as session:
            with session.start_transaction():
                PlatformDunningRegistry.transition(
                    tenant_id=TENANT,
                    subscription_id=SUBSCRIPTION,
                    state="WARNING",
                    invoice_ids=("invoice-a",),
                    days_overdue=7,
                    policy_fingerprint=POLICY,
                    expected_revision=0,
                    collection=collection,
                    session=session,
                    evaluated_at=NOW,
                )
                assert session.in_transaction
                raise RuntimeError("synthetic abort")

    assert collection.count_documents({"tenant_id": TENANT}) == 0


def test_real_mongo_concurrent_writers_have_one_revision_winner(
    mongo_context: tuple[MongoClient[Any], Any],
) -> None:
    client, database = mongo_context
    collection = database.get_collection(
        DUNNING_PROJECTION_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    PlatformDunningRegistry.ensure_indexes(collection)
    PlatformDunningRegistry.transition(
        tenant_id=TENANT,
        subscription_id=SUBSCRIPTION,
        state="WARNING",
        invoice_ids=("invoice-a",),
        days_overdue=7,
        policy_fingerprint=POLICY,
        expected_revision=0,
        collection=collection,
        evaluated_at=NOW,
    )

    def writer(state: str, invoice_id: str) -> str:
        try:
            value = PlatformDunningRegistry.transition(
                tenant_id=TENANT,
                subscription_id=SUBSCRIPTION,
                state=state,
                invoice_ids=(invoice_id,),
                days_overdue=10 if state == "CRITICAL" else 14,
                policy_fingerprint=POLICY,
                expected_revision=1,
                collection=collection,
                evaluated_at=NOW,
            )
            return f"won:{value['revision']}"
        except PlatformDunningRevisionConflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(
            lambda args: writer(*args),
            [("CRITICAL", "invoice-b"), ("SUSPENSION_REVIEW", "invoice-c")],
        ))
    assert sorted(outcomes) == ["conflict", "won:2"]
    persisted = PlatformDunningRegistry.get(TENANT, SUBSCRIPTION, collection)
    assert persisted is not None and persisted["revision"] == 2


def test_real_mongo_projection_and_audit_share_caller_transaction(
    mongo_context: tuple[MongoClient[Any], Any],
) -> None:
    client, database = mongo_context
    projections = database.get_collection(
        DUNNING_PROJECTION_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    audit = database.get_collection(
        "billing_audit_events",
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    PlatformDunningRegistry.ensure_indexes(projections)
    audit.create_index(
        [("tenant_id", 1), ("event_type", 1), ("subscription_id", 1), ("revision", 1)],
        unique=True,
        partialFilterExpression={"event_type": "DUNNING_PROJECTION_TRANSITION"},
        name="dunning_projection_transition_audit_unique",
    )
    policy = {
        "reminder_day": 3,
        "warning_day": 7,
        "critical_day": 10,
        "suspension_day": 14,
        "collections_day": 21,
        "termination_day": 30,
    }
    invoices = [{
        "tenant_id": TENANT,
        "subscription_id": SUBSCRIPTION,
        "invoice_id": "invoice-atomic",
        "due_at": "2026-10-20T00:00:00+00:00",
        "status": "open",
    }]

    with pytest.raises(RuntimeError, match="synthetic atomic abort"):
        with client.start_session() as session:
            with session.start_transaction():
                result = evaluate_platform_dunning(
                    tenant_id=TENANT,
                    invoices=invoices,
                    policy=policy,
                    projection_collection=projections,
                    now=NOW,
                    session=session,
                )
                transition = result["transitions"][0]
                audit.insert_one({
                    "tenant_id": TENANT,
                    "event_type": "DUNNING_PROJECTION_TRANSITION",
                    "subscription_id": SUBSCRIPTION,
                    "revision": transition["revision"],
                    "proof_hash": transition["transition_fingerprint"],
                }, session=session)
                raise RuntimeError("synthetic atomic abort")

    assert projections.count_documents({"tenant_id": TENANT}) == 0
    assert audit.count_documents({"tenant_id": TENANT}) == 0


def test_settlement_reconciliation_resolves_projection_and_allows_new_cycle(
    mongo_context: tuple[MongoClient[Any], Any],
) -> None:
    client, database = mongo_context
    projections = database.get_collection(
        DUNNING_PROJECTION_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    PlatformDunningRegistry.ensure_indexes(projections)
    PlatformDunningRegistry.transition(
        tenant_id=TENANT,
        subscription_id=SUBSCRIPTION,
        state="WARNING",
        invoice_ids=["invoice-settled"],
        days_overdue=8,
        policy_fingerprint=POLICY,
        expected_revision=0,
        collection=projections,
        evaluated_at=NOW,
    )
    paid_invoice = {
        "tenant_id": TENANT,
        "subscription_id": SUBSCRIPTION,
        "invoice_id": "invoice-settled",
        "due_at": datetime(2026, 10, 1, tzinfo=timezone.utc),
        "status": "paid",
    }
    policy = {
        "reminder_day": 3,
        "warning_day": 7,
        "critical_day": 10,
        "suspension_day": 14,
        "collections_day": 21,
        "termination_day": 30,
    }
    resolved = evaluate_platform_dunning(
        tenant_id=TENANT,
        invoices=[paid_invoice],
        policy=policy,
        projection_collection=projections,
        now=NOW,
    )
    assert resolved["transitions"][0]["state"] == "RESOLVED"
    stored = PlatformDunningRegistry.get(TENANT, SUBSCRIPTION, projections)
    assert stored["state"] == "RESOLVED"
    assert stored["revision"] == 2

    new_invoice = {
        "tenant_id": TENANT,
        "subscription_id": SUBSCRIPTION,
        "invoice_id": "invoice-new-cycle",
        "due_at": datetime(2026, 10, 29, tzinfo=timezone.utc),
        "status": "open",
    }
    reopened = evaluate_platform_dunning(
        tenant_id=TENANT,
        invoices=[paid_invoice, new_invoice],
        policy=policy,
        projection_collection=projections,
        now=NOW,
    )
    assert reopened["transitions"][0]["state"] == "REMINDER"
    assert reopened["transitions"][0]["from_state"] == "RESOLVED"
    assert reopened["transitions"][0]["revision"] == 3
