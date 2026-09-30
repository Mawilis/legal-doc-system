"""Real-Mongo certificate for the Legal Evidence capacity admission fence.

TITLE: Legal Evidence Capacity Admission Fence Registry Real-Mongo Certificate
VERSION: v1.0.0-L10A2Q-P5C-A-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Certify the P5C-A tenant-only capacity-admission serialization primitive
    against an actual disposable loopback Mongo replica set.

EPITOME:
    COMPETING TENANT ADMISSION ATTEMPTS
    -> ONE DURABLE TENANT FENCE
    -> REVISION CAS
    -> AT MOST ONE WINNER PER EXPECTED REVISION
    != CAPACITY RESERVED
    != USAGE COMMITTED
    != PROVIDER WRITE
    != AUTHORIZED AVAILABILITY

TRANSACTION:
    Every operational read/write uses a caller-owned active transaction.
    The registry never starts, commits, aborts or retries transactions.

CONCURRENCY:
    Competing first creation and competing revision advancement are exercised
    against real Mongo. A losing transaction must fail closed and never appear
    as a second successful fence acquisition.

DATABASE SAFETY:
    Only an explicit loopback wilsyVendorCertRS connection is accepted. One
    UUID-suffixed disposable database is created and dropped. Canonical "wilsy"
    is forbidden.

AUTHORITY BOUNDARY:
    Coordination evidence only. No capacity, usage, reservation, provider,
    document, IAM, retention, billing, payment, settlement or execution truth.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import threading
import uuid
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.registry.legal_evidence_capacity_admission_fence_registry import (
    COLLECTION,
    INDEX_TENANT_FENCE,
    LegalEvidenceCapacityAdmissionFenceConflictError,
    LegalEvidenceCapacityAdmissionFenceNotFoundError,
    LegalEvidenceCapacityAdmissionFencePersistedRecordInvalidError,
    LegalEvidenceCapacityAdmissionFencePersistenceError,
    LegalEvidenceCapacityAdmissionFenceRegistry,
    LegalEvidenceCapacityAdmissionFenceTransactionRequiredError,
)


URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)
REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "wilsy_l10a2q_p5ca_cert_"

AT = datetime(
    2026,
    9,
    30,
    6,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)


class MongoContext:
    """Own one isolated disposable P5C-A certification database."""

    def __init__(
        self,
        client: MongoClient[Any],
        database_name: str,
    ) -> None:
        self.client = client
        self.database_name = database_name
        self.database = client.get_database(
            database_name,
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
        )
        self.collection = self.database[COLLECTION]
        self.registry = LegalEvidenceCapacityAdmissionFenceRegistry(
            self.collection
        )


def _fresh_context() -> MongoContext:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        socketTimeoutMS=3000,
        retryWrites=True,
    )

    try:
        hello = client.admin.command("hello")
        address = client.address

        if (
            address is None
            or address[0] not in {
                "127.0.0.1",
                "localhost",
            }
        ):
            raise RuntimeError(
                "P5CA_CERT_MONGO_NOT_LOOPBACK"
            )

        if hello.get("setName") != REPLICA_SET:
            raise RuntimeError(
                "P5CA_CERT_REPLICA_SET_MISMATCH"
            )

        if hello.get("isWritablePrimary") is not True:
            raise RuntimeError(
                "P5CA_CERT_WRITABLE_PRIMARY_REQUIRED"
            )

        database_name = (
            DATABASE_PREFIX
            + uuid.uuid4().hex
        )

        if (
            database_name == "wilsy"
            or not database_name.startswith(
                DATABASE_PREFIX
            )
            or len(database_name) > 63
        ):
            raise RuntimeError(
                "P5CA_CERT_DATABASE_GUARD_FAILED"
            )

        context = MongoContext(
            client,
            database_name,
        )
        context.registry.ensure_indexes()
        return context

    except BaseException:
        client.close()
        raise


@pytest.fixture(scope="module")
def mongo_context() -> Any:
    """Yield one UUID-isolated database and remove only that database."""
    context = _fresh_context()

    try:
        yield context
    finally:
        context.client.drop_database(
            context.database_name
        )
        assert (
            context.database_name
            not in context.client.list_database_names()
        )
        context.client.close()


def _start_transaction(session: Any) -> None:
    session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(
            w="majority",
            j=True,
        ),
    )


def test_real_index_is_exact_unique_tenant_and_has_no_ttl(
    mongo_context: MongoContext,
) -> None:
    mongo_context.registry.ensure_indexes()

    indexes = {
        entry["name"]: entry
        for entry in mongo_context.collection.list_indexes()
    }

    assert set(indexes) == {
        "_id_",
        INDEX_TENANT_FENCE,
    }

    fence_index = indexes[
        INDEX_TENANT_FENCE
    ]

    assert dict(
        fence_index["key"]
    ) == {
        "tenant_id": 1,
    }
    assert fence_index["unique"] is True
    assert "expireAfterSeconds" not in fence_index


def test_real_inactive_transaction_rejects_before_database_call(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5ca-real-no-tx"

    with mongo_context.client.start_session() as session:
        with pytest.raises(
            LegalEvidenceCapacityAdmissionFenceTransactionRequiredError,
            match="L10A2Q_P5CA_TRANSACTION_REQUIRED",
        ):
            mongo_context.registry.advance(
                tenant_id=tenant,
                expected_revision=None,
                coordination_reference="reservation-p5ca-no-tx",
                advanced_at=AT,
                session=session,
            )

    assert mongo_context.collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0


def test_real_first_advance_creates_revision_one_and_get_is_tenant_scoped(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5ca-real-create"

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        created = mongo_context.registry.advance(
            tenant_id=tenant,
            expected_revision=None,
            coordination_reference="reservation-p5ca-create",
            advanced_at=AT,
            session=session,
        )

        loaded = mongo_context.registry.get(
            tenant_id=tenant,
            session=session,
        )

        assert created.revision == 1
        assert loaded == created

        with pytest.raises(
            LegalEvidenceCapacityAdmissionFenceNotFoundError,
            match="L10A2Q_P5CA_FENCE_NOT_FOUND",
        ):
            mongo_context.registry.get(
                tenant_id="tenant-p5ca-real-neighbor",
                session=session,
            )

        session.commit_transaction()

    persisted = mongo_context.collection.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert persisted is not None
    assert persisted["revision"] == 1
    assert (
        persisted["coordination_reference"]
        == "reservation-p5ca-create"
    )


def test_real_aborted_initial_advance_leaves_no_fence(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5ca-real-abort"

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        mongo_context.registry.advance(
            tenant_id=tenant,
            expected_revision=None,
            coordination_reference="reservation-p5ca-abort",
            advanced_at=AT,
            session=session,
        )

        assert mongo_context.collection.count_documents(
            {
                "tenant_id": tenant,
            },
            session=session,
        ) == 1

        session.abort_transaction()

    assert mongo_context.collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0


def test_real_existing_fence_advances_exactly_one_revision(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5ca-real-advance"

    with mongo_context.client.start_session() as session:
        _start_transaction(session)
        initial = mongo_context.registry.advance(
            tenant_id=tenant,
            expected_revision=None,
            coordination_reference="reservation-p5ca-advance-a",
            advanced_at=AT,
            session=session,
        )
        session.commit_transaction()

    with mongo_context.client.start_session() as session:
        _start_transaction(session)
        successor = mongo_context.registry.advance(
            tenant_id=tenant,
            expected_revision=initial.revision,
            coordination_reference="reservation-p5ca-advance-b",
            advanced_at=AT + timedelta(seconds=1),
            session=session,
        )
        session.commit_transaction()

    assert successor.revision == 2

    persisted = mongo_context.collection.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert persisted is not None
    assert persisted["revision"] == 2
    assert (
        persisted["fingerprint"]
        == successor.fingerprint
    )


def test_real_stale_revision_rejects_without_mutation(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5ca-real-stale"

    with mongo_context.client.start_session() as session:
        _start_transaction(session)
        initial = mongo_context.registry.advance(
            tenant_id=tenant,
            expected_revision=None,
            coordination_reference="reservation-p5ca-stale-a",
            advanced_at=AT,
            session=session,
        )
        session.commit_transaction()

    with mongo_context.client.start_session() as session:
        _start_transaction(session)
        current = mongo_context.registry.advance(
            tenant_id=tenant,
            expected_revision=initial.revision,
            coordination_reference="reservation-p5ca-stale-b",
            advanced_at=AT + timedelta(seconds=1),
            session=session,
        )
        session.commit_transaction()

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        with pytest.raises(
            LegalEvidenceCapacityAdmissionFenceConflictError,
            match="L10A2Q_P5CA_EXPECTED_REVISION_MISMATCH",
        ):
            mongo_context.registry.advance(
                tenant_id=tenant,
                expected_revision=1,
                coordination_reference="reservation-p5ca-stale-c",
                advanced_at=AT + timedelta(seconds=2),
                session=session,
            )

        session.abort_transaction()

    persisted = mongo_context.collection.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert persisted is not None
    assert persisted["revision"] == current.revision
    assert (
        persisted["fingerprint"]
        == current.fingerprint
    )


def test_real_corrupt_persisted_fence_rejects_fail_closed(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5ca-real-corrupt"

    with mongo_context.client.start_session() as session:
        _start_transaction(session)
        mongo_context.registry.advance(
            tenant_id=tenant,
            expected_revision=None,
            coordination_reference="reservation-p5ca-corrupt",
            advanced_at=AT,
            session=session,
        )
        session.commit_transaction()

    mongo_context.collection.update_one(
        {
            "tenant_id": tenant,
        },
        {
            "$set": {
                "fingerprint": "0" * 128,
            }
        },
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        with pytest.raises(
            LegalEvidenceCapacityAdmissionFencePersistedRecordInvalidError,
            match="L10A2Q_P5CA_PERSISTED_RECORD_INVALID",
        ):
            mongo_context.registry.get(
                tenant_id=tenant,
                session=session,
            )

        session.abort_transaction()


def test_real_competing_first_acquisition_has_exactly_one_committed_winner(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5ca-real-first-race"
    barrier = threading.Barrier(2)
    outcomes: list[str] = []
    lock = threading.Lock()

    def contender(label: str) -> None:
        client: MongoClient[Any] = MongoClient(
            URI,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=3000,
            retryWrites=True,
        )

        try:
            collection = client.get_database(
                mongo_context.database_name,
                read_concern=ReadConcern("majority"),
                write_concern=WriteConcern(
                    w="majority",
                    j=True,
                ),
            )[COLLECTION]
            registry = (
                LegalEvidenceCapacityAdmissionFenceRegistry(
                    collection
                )
            )

            with client.start_session() as session:
                _start_transaction(session)
                barrier.wait(timeout=5)

                try:
                    result = registry.advance(
                        tenant_id=tenant,
                        expected_revision=None,
                        coordination_reference=(
                            f"reservation-first-{label}"
                        ),
                        advanced_at=AT,
                        session=session,
                    )
                    session.commit_transaction()
                    outcome = (
                        f"{label}:SUCCESS:{result.revision}"
                    )

                except (
                    LegalEvidenceCapacityAdmissionFenceConflictError,
                    LegalEvidenceCapacityAdmissionFencePersistenceError,
                ):
                    if session.in_transaction:
                        session.abort_transaction()
                    outcome = f"{label}:FAIL"

                with lock:
                    outcomes.append(outcome)

        finally:
            client.close()

    threads = [
        threading.Thread(
            target=contender,
            args=("A",),
        ),
        threading.Thread(
            target=contender,
            args=("B",),
        ),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(timeout=10)
        assert not thread.is_alive()

    assert len(outcomes) == 2
    assert sum(
        ":SUCCESS:1" in outcome
        for outcome in outcomes
    ) == 1
    assert sum(
        outcome.endswith(":FAIL")
        for outcome in outcomes
    ) == 1

    assert mongo_context.collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    persisted = mongo_context.collection.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert persisted is not None
    assert persisted["revision"] == 1


def test_real_competing_same_revision_cas_has_exactly_one_committed_winner(
    mongo_context: MongoContext,
) -> None:
    tenant = "tenant-p5ca-real-cas-race"

    with mongo_context.client.start_session() as session:
        _start_transaction(session)
        initial = mongo_context.registry.advance(
            tenant_id=tenant,
            expected_revision=None,
            coordination_reference="reservation-cas-seed",
            advanced_at=AT,
            session=session,
        )
        session.commit_transaction()

    assert initial.revision == 1

    barrier = threading.Barrier(2)
    outcomes: list[str] = []
    lock = threading.Lock()

    def contender(label: str) -> None:
        client: MongoClient[Any] = MongoClient(
            URI,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=3000,
            retryWrites=True,
        )

        try:
            collection = client.get_database(
                mongo_context.database_name,
                read_concern=ReadConcern("majority"),
                write_concern=WriteConcern(
                    w="majority",
                    j=True,
                ),
            )[COLLECTION]
            registry = (
                LegalEvidenceCapacityAdmissionFenceRegistry(
                    collection
                )
            )

            with client.start_session() as session:
                _start_transaction(session)
                barrier.wait(timeout=5)

                try:
                    result = registry.advance(
                        tenant_id=tenant,
                        expected_revision=1,
                        coordination_reference=(
                            f"reservation-cas-{label}"
                        ),
                        advanced_at=(
                            AT + timedelta(seconds=1)
                        ),
                        session=session,
                    )
                    session.commit_transaction()
                    outcome = (
                        f"{label}:SUCCESS:{result.revision}"
                    )

                except (
                    LegalEvidenceCapacityAdmissionFenceConflictError,
                    LegalEvidenceCapacityAdmissionFencePersistenceError,
                ):
                    if session.in_transaction:
                        session.abort_transaction()
                    outcome = f"{label}:FAIL"

                with lock:
                    outcomes.append(outcome)

        finally:
            client.close()

    threads = [
        threading.Thread(
            target=contender,
            args=("A",),
        ),
        threading.Thread(
            target=contender,
            args=("B",),
        ),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(timeout=10)
        assert not thread.is_alive()

    assert len(outcomes) == 2
    assert sum(
        ":SUCCESS:2" in outcome
        for outcome in outcomes
    ) == 1
    assert sum(
        outcome.endswith(":FAIL")
        for outcome in outcomes
    ) == 1

    persisted = mongo_context.collection.find_one(
        {
            "tenant_id": tenant,
        }
    )
    assert persisted is not None
    assert persisted["revision"] == 2
    assert mongo_context.collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1


# ARTIFACT: test_legal_evidence_capacity_admission_fence_registry_real_mongo.py
# VERSION: v1.0.0-L10A2Q-P5C-A-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: actual Mongo tenant admission serialization evidence only
# TENANT POSTURE: exactly one durable coordination fence per tenant
# TRANSACTION POSTURE: caller owns every session and transaction
# CONCURRENCY POSTURE: competing first-create and stale-revision CAS fail closed
# EXPIRY POSTURE: no TTL; wall clock never releases the serialization fence
# RECONCILIATION POSTURE: P5D remains owner of semantic reservation reconciliation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
