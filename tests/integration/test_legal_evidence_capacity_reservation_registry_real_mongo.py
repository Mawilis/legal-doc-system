"""Real-Mongo certificate for Legal Evidence capacity reservation registry.

TITLE: Legal Evidence Capacity Reservation Registry Real-Mongo Certificate
VERSION: v1.0.0-L10A2Q-P5B-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Certify P5B against one explicit loopback disposable Mongo replica set:
    actual index metadata, no TTL deletion, caller-owned transactions, exact
    durable replay, tenant isolation, corruption rejection, rollback, lifecycle
    CAS and competing terminal transitions.

EPITOME:
    P5A IMMUTABLE RESERVATION
    -> P5B DURABLE MONGO RESERVATION
    -> ACTUAL TRANSACTION / CAS EVIDENCE
    != CAPACITY ADMISSION ORCHESTRATION
    != P5D RECONCILIATION AUTHORITY
    != PROVIDER EXECUTION
    != USAGE CONSUMPTION
    != IAM
    != BILLING / PAYMENT / SETTLEMENT

DATABASE SAFETY:
    The certificate requires the explicit loopback wilsyVendorCertRS replica
    set and creates only one UUID-suffixed disposable database. The database is
    dropped after the module. Canonical database "wilsy" is forbidden.

TRANSACTION:
    The caller owns every ClientSession and transaction. The registry never
    starts, commits, aborts or retries transactions.

EXPIRY:
    No TTL index exists. ACTIVE rows remain durable until explicit terminal CAS.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
import os
import threading
import uuid
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
    LegalEvidenceCapacityReservationStatus,
)
from tools.eos.legal_operations.registry.legal_evidence_capacity_reservation_registry import (
    COLLECTION,
    INDEX_TENANT_DOCUMENT_STATUS,
    INDEX_TENANT_IDEMPOTENCY,
    INDEX_TENANT_INGESTION_INTENT,
    INDEX_TENANT_RESERVATION,
    INDEX_TENANT_STATUS_EXPIRY,
    LegalEvidenceCapacityReservationConflictError,
    LegalEvidenceCapacityReservationNotFoundError,
    LegalEvidenceCapacityReservationPersistedRecordInvalidError,
    LegalEvidenceCapacityReservationPersistenceError,
    LegalEvidenceCapacityReservationRegistry,
    LegalEvidenceCapacityReservationTransactionRequiredError,
)


URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)
REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "wilsy_l10a2q_p5b_cert_"

AT = datetime(
    2026,
    9,
    30,
    19,
    30,
    0,
    123456,
    tzinfo=timezone.utc,
)
EXPIRY = AT + timedelta(minutes=15)
SHA = "a" * 128


class MongoContext:
    """Own one isolated disposable certification database."""

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
            write_concern=WriteConcern(w="majority", j=True),
        )
        self.collection = self.database[COLLECTION]
        self.registry = LegalEvidenceCapacityReservationRegistry(
            self.collection
        )


def _reservation(
    *,
    tenant_id: str = "tenant-p5b-real-a",
    document_id: str = "document-p5b-real-a",
    reservation_id: str = "reservation-p5b-real-a",
    ingestion_intent_id: str = "ingestion-p5b-real-a",
    storage: int = 1024,
    ingress: int = 1024,
    versions: int = 1,
) -> LegalEvidenceCapacityReservation:
    return LegalEvidenceCapacityReservation(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id=reservation_id,
        ingestion_intent_id=ingestion_intent_id,
        remaining_capacity_fingerprint=SHA,
        reserved_storage_bytes=storage,
        reserved_ingress_bytes=ingress,
        reserved_document_versions=versions,
        reserved_at=AT,
        expires_at=EXPIRY,
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
            or address[0] not in {"127.0.0.1", "localhost"}
        ):
            raise RuntimeError(
                "P5B_CERT_MONGO_NOT_LOOPBACK"
            )

        if hello.get("setName") != REPLICA_SET:
            raise RuntimeError(
                "P5B_CERT_REPLICA_SET_MISMATCH"
            )

        if hello.get("isWritablePrimary") is not True:
            raise RuntimeError(
                "P5B_CERT_WRITABLE_PRIMARY_REQUIRED"
            )

        database_name = DATABASE_PREFIX + uuid.uuid4().hex

        if (
            database_name == "wilsy"
            or not database_name.startswith(DATABASE_PREFIX)
            or len(database_name) > 63
        ):
            raise RuntimeError(
                "P5B_CERT_DATABASE_GUARD_FAILED"
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
    """Provide one isolated disposable database and delete only that database."""
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


def _index_key(index: Mapping[str, Any]) -> dict[str, Any]:
    return dict(index["key"])


def test_real_indexes_are_exact_unique_and_have_no_ttl(
    mongo_context: MongoContext,
) -> None:
    mongo_context.registry.ensure_indexes()

    indexes = {
        entry["name"]: entry
        for entry in mongo_context.collection.list_indexes()
    }

    assert set(indexes) == {
        "_id_",
        INDEX_TENANT_RESERVATION,
        INDEX_TENANT_INGESTION_INTENT,
        INDEX_TENANT_IDEMPOTENCY,
        INDEX_TENANT_STATUS_EXPIRY,
        INDEX_TENANT_DOCUMENT_STATUS,
    }

    assert _index_key(
        indexes[INDEX_TENANT_RESERVATION]
    ) == {
        "tenant_id": 1,
        "reservation_id": 1,
    }
    assert (
        indexes[INDEX_TENANT_RESERVATION]["unique"]
        is True
    )

    assert _index_key(
        indexes[INDEX_TENANT_INGESTION_INTENT]
    ) == {
        "tenant_id": 1,
        "ingestion_intent_id": 1,
    }
    assert (
        indexes[INDEX_TENANT_INGESTION_INTENT]["unique"]
        is True
    )

    assert _index_key(
        indexes[INDEX_TENANT_IDEMPOTENCY]
    ) == {
        "tenant_id": 1,
        "idempotency_key": 1,
    }
    assert (
        indexes[INDEX_TENANT_IDEMPOTENCY]["unique"]
        is True
    )

    assert _index_key(
        indexes[INDEX_TENANT_STATUS_EXPIRY]
    ) == {
        "tenant_id": 1,
        "status": 1,
        "_expires_at_epoch_us": 1,
    }
    assert (
        indexes[
            INDEX_TENANT_STATUS_EXPIRY
        ].get("unique")
        is not True
    )

    assert _index_key(
        indexes[INDEX_TENANT_DOCUMENT_STATUS]
    ) == {
        "tenant_id": 1,
        "document_id": 1,
        "status": 1,
    }
    assert (
        indexes[
            INDEX_TENANT_DOCUMENT_STATUS
        ].get("unique")
        is not True
    )

    assert not any(
        "expireAfterSeconds" in entry
        for entry in indexes.values()
    )


def test_real_transaction_create_replay_get_and_tenant_isolation(
    mongo_context: MongoContext,
) -> None:
    reservation = _reservation(
        reservation_id="reservation-p5b-real-replay",
        ingestion_intent_id="ingestion-p5b-real-replay",
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        first = mongo_context.registry.create_or_replay(
            reservation,
            idempotency_key="idem-p5b-real-replay",
            session=session,
        )
        second = mongo_context.registry.create_or_replay(
            reservation,
            idempotency_key="idem-p5b-real-replay",
            session=session,
        )
        own = mongo_context.registry.get(
            tenant_id=reservation.tenant_id,
            reservation_id=reservation.reservation_id,
            session=session,
        )

        assert first == reservation
        assert second == reservation
        assert own == reservation

        with pytest.raises(
            LegalEvidenceCapacityReservationNotFoundError,
            match="L10A2Q_P5B_RESERVATION_NOT_FOUND",
        ):
            mongo_context.registry.get(
                tenant_id="tenant-p5b-real-neighbor",
                reservation_id=reservation.reservation_id,
                session=session,
            )

        session.commit_transaction()

    assert mongo_context.collection.count_documents(
        {
            "tenant_id": reservation.tenant_id,
            "reservation_id": reservation.reservation_id,
        }
    ) == 1


def test_real_inactive_transaction_rejects_before_write(
    mongo_context: MongoContext,
) -> None:
    reservation = _reservation(
        reservation_id="reservation-p5b-real-no-tx",
        ingestion_intent_id="ingestion-p5b-real-no-tx",
    )

    with mongo_context.client.start_session() as session:
        with pytest.raises(
            LegalEvidenceCapacityReservationTransactionRequiredError,
            match="L10A2Q_P5B_TRANSACTION_REQUIRED",
        ):
            mongo_context.registry.create_or_replay(
                reservation,
                idempotency_key="idem-p5b-real-no-tx",
                session=session,
            )

    assert mongo_context.collection.count_documents(
        {
            "reservation_id":
                reservation.reservation_id
        }
    ) == 0


def test_real_aborted_transaction_leaves_no_reservation(
    mongo_context: MongoContext,
) -> None:
    reservation = _reservation(
        reservation_id="reservation-p5b-real-abort",
        ingestion_intent_id="ingestion-p5b-real-abort",
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        mongo_context.registry.create_or_replay(
            reservation,
            idempotency_key="idem-p5b-real-abort",
            session=session,
        )

        assert mongo_context.collection.count_documents(
            {
                "reservation_id":
                    reservation.reservation_id
            },
            session=session,
        ) == 1

        session.abort_transaction()

    assert mongo_context.collection.count_documents(
        {
            "reservation_id":
                reservation.reservation_id
        }
    ) == 0


def test_real_divergent_idempotency_identity_and_intent_reject(
    mongo_context: MongoContext,
) -> None:
    first = _reservation(
        reservation_id="reservation-p5b-real-conflict-a",
        ingestion_intent_id="ingestion-p5b-real-conflict-a",
        document_id="document-p5b-real-conflict-a",
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)
        mongo_context.registry.create_or_replay(
            first,
            idempotency_key="idem-p5b-real-conflict",
            session=session,
        )
        session.commit_transaction()

    divergent_idempotency = _reservation(
        reservation_id="reservation-p5b-real-conflict-b",
        ingestion_intent_id="ingestion-p5b-real-conflict-b",
        document_id="document-p5b-real-conflict-b",
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        with pytest.raises(
            LegalEvidenceCapacityReservationConflictError,
            match="L10A2Q_P5B_DIVERGENT_IDEMPOTENCY",
        ):
            mongo_context.registry.create_or_replay(
                divergent_idempotency,
                idempotency_key="idem-p5b-real-conflict",
                session=session,
            )

        session.abort_transaction()

    divergent_identity = _reservation(
        reservation_id=first.reservation_id,
        ingestion_intent_id="ingestion-p5b-real-other-intent",
        document_id="document-p5b-real-other",
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        with pytest.raises(
            LegalEvidenceCapacityReservationConflictError,
            match="L10A2Q_P5B_DIVERGENT_RESERVATION_IDENTITY",
        ):
            mongo_context.registry.create_or_replay(
                divergent_identity,
                idempotency_key="idem-p5b-real-other-identity",
                session=session,
            )

        session.abort_transaction()

    divergent_intent = _reservation(
        reservation_id="reservation-p5b-real-other-id",
        ingestion_intent_id=first.ingestion_intent_id,
        document_id="document-p5b-real-other-intent",
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        with pytest.raises(
            LegalEvidenceCapacityReservationConflictError,
            match="L10A2Q_P5B_DIVERGENT_INGESTION_INTENT",
        ):
            mongo_context.registry.create_or_replay(
                divergent_intent,
                idempotency_key="idem-p5b-real-other-intent",
                session=session,
            )

        session.abort_transaction()


def test_real_corrupt_persisted_reservation_rejects_fail_closed(
    mongo_context: MongoContext,
) -> None:
    reservation = _reservation(
        reservation_id="reservation-p5b-real-corrupt",
        ingestion_intent_id="ingestion-p5b-real-corrupt",
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)
        mongo_context.registry.create_or_replay(
            reservation,
            idempotency_key="idem-p5b-real-corrupt",
            session=session,
        )
        session.commit_transaction()

    mongo_context.collection.update_one(
        {
            "tenant_id": reservation.tenant_id,
            "reservation_id": reservation.reservation_id,
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
            LegalEvidenceCapacityReservationPersistedRecordInvalidError,
            match="L10A2Q_P5B_PERSISTED_RECORD_INVALID",
        ):
            mongo_context.registry.get(
                tenant_id=reservation.tenant_id,
                reservation_id=reservation.reservation_id,
                session=session,
            )

        session.abort_transaction()


@pytest.mark.parametrize(
    ("operation", "offset", "expected_status"),
    [
        ("consume", timedelta(minutes=2), "CONSUMED"),
        ("release", timedelta(minutes=3), "RELEASED"),
        ("expire", timedelta(minutes=15), "EXPIRED"),
    ],
)
def test_real_lifecycle_cas_is_durable_and_replay_fails(
    mongo_context: MongoContext,
    operation: str,
    offset: timedelta,
    expected_status: str,
) -> None:
    reservation = _reservation(
        reservation_id=(
            f"reservation-p5b-real-{operation}"
        ),
        ingestion_intent_id=(
            f"ingestion-p5b-real-{operation}"
        ),
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)
        mongo_context.registry.create_or_replay(
            reservation,
            idempotency_key=f"idem-p5b-real-{operation}",
            session=session,
        )
        session.commit_transaction()

    observed = AT + offset

    with mongo_context.client.start_session() as session:
        _start_transaction(session)
        result = getattr(
            mongo_context.registry,
            operation,
        )(
            reservation,
            observed,
            session=session,
        )
        session.commit_transaction()

    assert result.status.value == expected_status

    persisted = mongo_context.collection.find_one(
        {
            "tenant_id": reservation.tenant_id,
            "reservation_id": reservation.reservation_id,
        }
    )
    assert persisted is not None
    assert persisted["status"] == expected_status
    assert persisted["fingerprint"] == result.fingerprint

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        with pytest.raises(
            LegalEvidenceCapacityReservationConflictError,
        ):
            getattr(
                mongo_context.registry,
                operation,
            )(
                reservation,
                observed,
                session=session,
            )

        session.abort_transaction()


def test_real_active_listing_does_not_implicitly_expire_rows(
    mongo_context: MongoContext,
) -> None:
    reservation = _reservation(
        tenant_id="tenant-p5b-real-active-list",
        reservation_id="reservation-p5b-real-active-list",
        ingestion_intent_id="ingestion-p5b-real-active-list",
        document_id="document-p5b-real-active-list",
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        mongo_context.registry.create_or_replay(
            reservation,
            idempotency_key="idem-p5b-real-active-list",
            session=session,
        )

        tenant_rows = (
            mongo_context.registry.list_active_reservations(
                tenant_id=reservation.tenant_id,
                session=session,
            )
        )
        document_rows = (
            mongo_context.registry.list_active_reservations(
                tenant_id=reservation.tenant_id,
                document_id=reservation.document_id,
                session=session,
            )
        )

        assert reservation in tenant_rows
        assert reservation in document_rows

        session.commit_transaction()


def test_real_exact_creation_replay_after_terminal_transition_returns_current_state(
    mongo_context: MongoContext,
) -> None:
    """Same creation command remains replay-safe after lifecycle advancement."""
    reservation = _reservation(
        reservation_id="reservation-p5b-real-post-terminal-replay",
        ingestion_intent_id="ingestion-p5b-real-post-terminal-replay",
    )
    idem = "idem-p5b-real-post-terminal-replay"

    with mongo_context.client.start_session() as session:
        _start_transaction(session)
        mongo_context.registry.create_or_replay(
            reservation,
            idempotency_key=idem,
            session=session,
        )
        session.commit_transaction()

    consumed_at = AT + timedelta(minutes=4)

    with mongo_context.client.start_session() as session:
        _start_transaction(session)
        consumed = mongo_context.registry.consume(
            reservation,
            consumed_at,
            session=session,
        )
        session.commit_transaction()

    assert (
        consumed.status
        is LegalEvidenceCapacityReservationStatus.CONSUMED
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)

        replay = mongo_context.registry.create_or_replay(
            reservation,
            idempotency_key=idem,
            session=session,
        )

        assert replay == consumed
        session.commit_transaction()

    assert mongo_context.collection.count_documents(
        {
            "tenant_id": reservation.tenant_id,
            "reservation_id": reservation.reservation_id,
        }
    ) == 1


def test_real_competing_terminal_transitions_have_exactly_one_winner(
    mongo_context: MongoContext,
) -> None:
    """Two concurrent terminal attempts cannot both consume one ACTIVE row."""
    reservation = _reservation(
        reservation_id="reservation-p5b-real-race",
        ingestion_intent_id="ingestion-p5b-real-race",
    )

    with mongo_context.client.start_session() as session:
        _start_transaction(session)
        mongo_context.registry.create_or_replay(
            reservation,
            idempotency_key="idem-p5b-real-race",
            session=session,
        )
        session.commit_transaction()

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
                LegalEvidenceCapacityReservationRegistry(
                    collection
                )
            )

            with client.start_session() as session:
                _start_transaction(session)
                barrier.wait(timeout=5)

                try:
                    registry.consume(
                        reservation,
                        AT + timedelta(minutes=5),
                        session=session,
                    )
                    session.commit_transaction()
                    outcome = f"{label}:SUCCESS"

                except (
                    LegalEvidenceCapacityReservationConflictError,
                    LegalEvidenceCapacityReservationPersistenceError,
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
        outcome.endswith(":SUCCESS")
        for outcome in outcomes
    ) == 1
    assert sum(
        outcome.endswith(":FAIL")
        for outcome in outcomes
    ) == 1

    persisted = mongo_context.collection.find_one(
        {
            "tenant_id": reservation.tenant_id,
            "reservation_id": reservation.reservation_id,
        }
    )
    assert persisted is not None
    assert persisted["status"] == "CONSUMED"
    assert mongo_context.collection.count_documents(
        {
            "tenant_id": reservation.tenant_id,
            "reservation_id": reservation.reservation_id,
        }
    ) == 1


# ARTIFACT: test_legal_evidence_capacity_reservation_registry_real_mongo.py
# VERSION: v1.0.0-L10A2Q-P5B-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: actual Mongo durability/index/transaction/CAS evidence only
# DATABASE POSTURE: UUID disposable DB on loopback wilsyVendorCertRS only
# TENANT POSTURE: all registry operations preserve exact tenant scope
# EXPIRY POSTURE: no TTL; ACTIVE state changes only by durable CAS
# TRANSACTION POSTURE: caller owns session/transaction lifecycle
# RECONCILIATION POSTURE: P5D owns semantic reconciliation evidence/orchestration
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
