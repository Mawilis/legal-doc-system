"""Direct certificate for the Legal Evidence capacity reservation registry.

TITLE: Legal Evidence Capacity Reservation Registry Direct Certificate
VERSION: v1.0.0-L10A2Q-P5B-LEGAL-EVIDENCE-CAPACITY-RESERVATION-REGISTRY-CERT
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Certify the durable tenant-scoped Mongo registry contract for immutable P5A
    capacity reservations: exact create/replay, strict hydration, active
    transaction ownership, durable terminal CAS and active-reservation reads.

EPITOME:
    P5A IMMUTABLE RESERVATION
    -> P5B DURABLE TENANT REGISTRY
    -> ATOMIC LIFECYCLE CAS
    != CAPACITY ADMISSION ORCHESTRATION
    != RECONCILIATION AUTHORITY
    != STORAGE PROVIDER EXECUTION
    != USAGE CONSUMPTION
    != IAM
    != BILLING / PAYMENT / SETTLEMENT

EXPIRY:
    Wall-clock expiry does not delete a row and does not silently make an
    ACTIVE reservation disappear. Explicit P5B EXPIRED CAS preserves durable
    evidence; P5D later owns reconciliation semantics.

TRANSACTION:
    Operational writes and reads require one caller-owned already-active Mongo
    transaction. The registry never creates, commits, aborts or retries it.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Any
from unittest.mock import MagicMock

import pytest

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
    LegalEvidenceCapacityReservationRegistry,
    LegalEvidenceCapacityReservationTransactionRequiredError,
)


AT = datetime(2026, 9, 30, 19, 30, tzinfo=timezone.utc)
EXPIRY = AT + timedelta(minutes=15)
SHA = "a" * 128


class Session:
    """Minimal direct-certificate session marker."""

    def __init__(self, in_transaction: bool) -> None:
        self.in_transaction = in_transaction


def _reservation(
    *,
    tenant_id: str = "tenant-p5b",
    document_id: str = "document-p5b",
    reservation_id: str = "reservation-p5b",
    ingestion_intent_id: str = "ingestion-p5b",
) -> LegalEvidenceCapacityReservation:
    return LegalEvidenceCapacityReservation(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id=reservation_id,
        ingestion_intent_id=ingestion_intent_id,
        remaining_capacity_fingerprint=SHA,
        reserved_storage_bytes=1024,
        reserved_ingress_bytes=1024,
        reserved_document_versions=1,
        reserved_at=AT,
        expires_at=EXPIRY,
    )


def _stored(
    reservation: LegalEvidenceCapacityReservation,
    *,
    idempotency_key: str = "idem-p5b",
) -> dict[str, object]:
    serialized = reservation.to_dict()

    command_payload = {
        "tenant_id": reservation.tenant_id,
        "document_id": reservation.document_id,
        "reservation_id": reservation.reservation_id,
        "ingestion_intent_id": reservation.ingestion_intent_id,
        "remaining_capacity_fingerprint":
            reservation.remaining_capacity_fingerprint,
        "reserved_storage_bytes": reservation.reserved_storage_bytes,
        "reserved_ingress_bytes": reservation.reserved_ingress_bytes,
        "reserved_document_versions": reservation.reserved_document_versions,
        "reserved_at": serialized["reserved_at"],
        "expires_at": serialized["expires_at"],
        "idempotency_key": idempotency_key,
    }

    command_fingerprint = hashlib.sha3_512(
        json.dumps(
            command_payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    payload = dict(serialized)
    payload.update(
        {
            "_id": "mongo-id",
            "idempotency_key": idempotency_key,
            "command_fingerprint": command_fingerprint,
            "_expires_at_epoch_us": int(
                reservation.expires_at.timestamp() * 1_000_000
            ),
        }
    )
    return payload


def test_collection_and_index_names_are_closed_contract() -> None:
    assert COLLECTION == "legal_evidence_capacity_reservations"
    assert INDEX_TENANT_RESERVATION
    assert INDEX_TENANT_INGESTION_INTENT
    assert INDEX_TENANT_IDEMPOTENCY
    assert INDEX_TENANT_STATUS_EXPIRY
    assert INDEX_TENANT_DOCUMENT_STATUS


def test_indexes_are_exact_tenant_scoped_and_have_no_ttl() -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)

    registry.ensure_indexes()

    calls = collection.create_index.call_args_list
    assert len(calls) == 5

    normalized = [
        {
            "keys": tuple(call.args[0]),
            "unique": call.kwargs.get("unique", False),
            "name": call.kwargs["name"],
            "ttl": call.kwargs.get("expireAfterSeconds"),
        }
        for call in calls
    ]

    assert {
        (entry["keys"], entry["unique"], entry["name"])
        for entry in normalized
    } == {
        (
            (("tenant_id", 1), ("reservation_id", 1)),
            True,
            INDEX_TENANT_RESERVATION,
        ),
        (
            (("tenant_id", 1), ("ingestion_intent_id", 1)),
            True,
            INDEX_TENANT_INGESTION_INTENT,
        ),
        (
            (("tenant_id", 1), ("idempotency_key", 1)),
            True,
            INDEX_TENANT_IDEMPOTENCY,
        ),
        (
            (("tenant_id", 1), ("status", 1), ("_expires_at_epoch_us", 1)),
            False,
            INDEX_TENANT_STATUS_EXPIRY,
        ),
        (
            (("tenant_id", 1), ("document_id", 1), ("status", 1)),
            False,
            INDEX_TENANT_DOCUMENT_STATUS,
        ),
    }

    assert all(entry["ttl"] is None for entry in normalized)


@pytest.mark.parametrize("session", [None, Session(False)])
def test_create_requires_caller_owned_active_transaction_before_database_call(
    session: Any,
) -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)

    with pytest.raises(
        LegalEvidenceCapacityReservationTransactionRequiredError,
        match="L10A2Q_P5B_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            _reservation(),
            idempotency_key="idem-p5b-no-tx",
            session=session,
        )

    collection.find_one.assert_not_called()
    collection.insert_one.assert_not_called()


def test_create_or_replay_inserts_exact_active_reservation() -> None:
    collection = MagicMock()
    collection.find_one.return_value = None
    registry = LegalEvidenceCapacityReservationRegistry(collection)
    reservation = _reservation()

    result = registry.create_or_replay(
        reservation,
        idempotency_key="idem-p5b-create",
        session=Session(True),
    )

    assert result == reservation
    collection.insert_one.assert_called_once()

    document = collection.insert_one.call_args.args[0]
    assert document["tenant_id"] == reservation.tenant_id
    assert document["document_id"] == reservation.document_id
    assert document["reservation_id"] == reservation.reservation_id
    assert document["ingestion_intent_id"] == reservation.ingestion_intent_id
    assert document["status"] == "ACTIVE"
    assert document["idempotency_key"] == "idem-p5b-create"
    assert len(document["command_fingerprint"]) == 128
    assert isinstance(document["_expires_at_epoch_us"], int)

    assert "expireAfterSeconds" not in document
    assert "admitted" not in document
    assert "usage_observation_id" not in document


def test_create_rejects_non_active_initial_reservation() -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)
    terminal = _reservation().consume(AT + timedelta(minutes=1))

    with pytest.raises(
        LegalEvidenceCapacityReservationConflictError,
        match="L10A2Q_P5B_CREATE_REQUIRES_ACTIVE",
    ):
        registry.create_or_replay(
            terminal,
            idempotency_key="idem-p5b-terminal",
            session=Session(True),
        )

    collection.find_one.assert_not_called()
    collection.insert_one.assert_not_called()


def test_exact_idempotent_replay_returns_existing_reservation() -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)
    reservation = _reservation()

    # The registry computes the command fingerprint before the lookup. Reuse
    # the exact inserted row produced by one first call.
    collection.find_one.return_value = None
    first = registry.create_or_replay(
        reservation,
        idempotency_key="idem-p5b-replay",
        session=Session(True),
    )
    inserted = dict(collection.insert_one.call_args.args[0])

    collection.reset_mock()
    collection.find_one.return_value = inserted

    second = registry.create_or_replay(
        reservation,
        idempotency_key="idem-p5b-replay",
        session=Session(True),
    )

    assert first == reservation
    assert second == reservation
    collection.insert_one.assert_not_called()


def test_exact_creation_replay_after_terminal_transition_returns_current_state() -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)
    reservation = _reservation()
    idempotency_key = "idem-p5b-post-terminal"

    collection.find_one.return_value = None
    registry.create_or_replay(
        reservation,
        idempotency_key=idempotency_key,
        session=Session(True),
    )
    inserted = dict(collection.insert_one.call_args.args[0])

    consumed = reservation.consume(
        AT + timedelta(minutes=2)
    )
    terminal_row = _stored(
        consumed,
        idempotency_key=idempotency_key,
    )
    terminal_row["command_fingerprint"] = inserted[
        "command_fingerprint"
    ]

    collection.reset_mock()
    collection.find_one.return_value = terminal_row

    replay = registry.create_or_replay(
        reservation,
        idempotency_key=idempotency_key,
        session=Session(True),
    )

    assert replay == consumed
    assert (
        replay.status
        is LegalEvidenceCapacityReservationStatus.CONSUMED
    )
    collection.insert_one.assert_not_called()


def test_divergent_idempotency_replay_rejects() -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)

    first = _reservation(document_id="document-p5b-a")
    second = _reservation(
        document_id="document-p5b-b",
        reservation_id="reservation-p5b-b",
        ingestion_intent_id="ingestion-p5b-b",
    )

    collection.find_one.return_value = None
    registry.create_or_replay(
        first,
        idempotency_key="idem-p5b-divergent",
        session=Session(True),
    )
    inserted = dict(collection.insert_one.call_args.args[0])

    collection.reset_mock()
    collection.find_one.return_value = inserted

    with pytest.raises(
        LegalEvidenceCapacityReservationConflictError,
        match="L10A2Q_P5B_DIVERGENT_IDEMPOTENCY",
    ):
        registry.create_or_replay(
            second,
            idempotency_key="idem-p5b-divergent",
            session=Session(True),
        )

    collection.insert_one.assert_not_called()


def test_same_reservation_identity_with_different_command_rejects() -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)

    existing = _reservation()
    row = _stored(existing)

    def find_one(query: dict[str, object], **_: object) -> object:
        if query.get("idempotency_key") == "idem-p5b-new":
            return None
        if query.get("reservation_id") == existing.reservation_id:
            return row
        return None

    collection.find_one.side_effect = find_one

    divergent = _reservation(
        document_id="document-p5b-other",
    )

    with pytest.raises(
        LegalEvidenceCapacityReservationConflictError,
        match="L10A2Q_P5B_DIVERGENT_RESERVATION_IDENTITY",
    ):
        registry.create_or_replay(
            divergent,
            idempotency_key="idem-p5b-new",
            session=Session(True),
        )

    collection.insert_one.assert_not_called()


def test_same_ingestion_intent_cannot_acquire_divergent_second_reservation() -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)

    existing = _reservation()
    row = _stored(existing)

    def find_one(query: dict[str, object], **_: object) -> object:
        if query.get("idempotency_key") == "idem-p5b-new-intent":
            return None
        if query.get("reservation_id") == "reservation-p5b-second":
            return None
        if query.get("ingestion_intent_id") == existing.ingestion_intent_id:
            return row
        return None

    collection.find_one.side_effect = find_one

    divergent = _reservation(
        reservation_id="reservation-p5b-second",
    )

    with pytest.raises(
        LegalEvidenceCapacityReservationConflictError,
        match="L10A2Q_P5B_DIVERGENT_INGESTION_INTENT",
    ):
        registry.create_or_replay(
            divergent,
            idempotency_key="idem-p5b-new-intent",
            session=Session(True),
        )

    collection.insert_one.assert_not_called()


def test_get_is_exact_tenant_scoped_and_cross_tenant_absence_is_not_disclosure() -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)
    reservation = _reservation()

    collection.find_one.return_value = _stored(reservation)

    own = registry.get(
        tenant_id=reservation.tenant_id,
        reservation_id=reservation.reservation_id,
        session=Session(True),
    )

    assert own == reservation
    assert collection.find_one.call_args.args[0] == {
        "tenant_id": reservation.tenant_id,
        "reservation_id": reservation.reservation_id,
    }

    collection.find_one.return_value = None

    with pytest.raises(
        LegalEvidenceCapacityReservationNotFoundError,
        match="L10A2Q_P5B_RESERVATION_NOT_FOUND",
    ):
        registry.get(
            tenant_id="tenant-p5b-neighbor",
            reservation_id=reservation.reservation_id,
            session=Session(True),
        )


def test_corrupt_persisted_row_rejects_without_repair() -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)
    reservation = _reservation()

    corrupt = _stored(reservation)
    corrupt["fingerprint"] = "0" * 128
    collection.find_one.return_value = corrupt

    with pytest.raises(
        LegalEvidenceCapacityReservationPersistedRecordInvalidError,
        match="L10A2Q_P5B_PERSISTED_RECORD_INVALID",
    ):
        registry.get(
            tenant_id=reservation.tenant_id,
            reservation_id=reservation.reservation_id,
            session=Session(True),
        )


def test_active_reads_do_not_silently_drop_wall_clock_expired_active_rows() -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)

    active = _reservation()
    row = _stored(active)

    cursor = MagicMock()
    cursor.__iter__.return_value = iter([row])
    collection.find.return_value = cursor

    values = registry.list_active_reservations(
        tenant_id=active.tenant_id,
        session=Session(True),
    )

    assert values == [active]

    query = collection.find.call_args.args[0]
    assert query == {
        "tenant_id": active.tenant_id,
        "status": "ACTIVE",
    }
    assert "_expires_at_epoch_us" not in query
    assert "expires_at" not in query


def test_document_scoped_active_read_retains_exact_tenant_document_binding() -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)

    active = _reservation()
    cursor = MagicMock()
    cursor.__iter__.return_value = iter([_stored(active)])
    collection.find.return_value = cursor

    values = registry.list_active_reservations(
        tenant_id=active.tenant_id,
        document_id=active.document_id,
        session=Session(True),
    )

    assert values == [active]
    assert collection.find.call_args.args[0] == {
        "tenant_id": active.tenant_id,
        "document_id": active.document_id,
        "status": "ACTIVE",
    }


@pytest.mark.parametrize(
    ("operation", "offset", "expected_status"),
    [
        ("consume", timedelta(minutes=2), "CONSUMED"),
        ("release", timedelta(minutes=3), "RELEASED"),
        ("expire", timedelta(minutes=15), "EXPIRED"),
    ],
)
def test_lifecycle_transition_uses_atomic_active_state_cas(
    operation: str,
    offset: timedelta,
    expected_status: str,
) -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)
    active = _reservation()
    observed = AT + offset

    if operation == "consume":
        successor = active.consume(observed)
    elif operation == "release":
        successor = active.release(observed)
    else:
        successor = active.expire(observed)

    row = _stored(
        successor,
        idempotency_key="idem-p5b-transition",
    )
    collection.find_one_and_update.return_value = row

    result = getattr(registry, operation)(
        active,
        observed,
        session=Session(True),
    )

    assert result == successor

    query = collection.find_one_and_update.call_args.args[0]
    assert query["tenant_id"] == active.tenant_id
    assert query["reservation_id"] == active.reservation_id
    assert query["status"] == "ACTIVE"
    assert query["fingerprint"] == active.fingerprint

    if operation == "expire":
        assert query["_expires_at_epoch_us"] == {
            "$lte": int(observed.timestamp() * 1_000_000)
        }
    else:
        assert query["_expires_at_epoch_us"] == {
            "$gt": int(observed.timestamp() * 1_000_000)
        }

    update = collection.find_one_and_update.call_args.args[1]
    assert update["$set"]["status"] == expected_status
    assert update["$set"]["fingerprint"] == successor.fingerprint


def test_lifecycle_cas_loss_fails_closed() -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityReservationRegistry(collection)
    active = _reservation()

    collection.find_one_and_update.return_value = None
    collection.find_one.return_value = _stored(
        active.consume(AT + timedelta(minutes=1))
    )

    with pytest.raises(
        LegalEvidenceCapacityReservationConflictError,
        match="L10A2Q_P5B_LIFECYCLE_CONFLICT",
    ):
        registry.consume(
            active,
            AT + timedelta(minutes=2),
            session=Session(True),
        )


def test_registry_surface_has_no_admission_provider_usage_or_financial_authority() -> None:
    forbidden = {
        "admit",
        "authorize",
        "write_provider_object",
        "persist_usage",
        "invoice",
        "payment",
        "settlement",
        "execute_payment",
    }

    public = {
        name
        for name in dir(LegalEvidenceCapacityReservationRegistry)
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(public)


# ARTIFACT: test_legal_evidence_capacity_reservation_registry.py
# VERSION: v1.0.0-L10A2Q-P5B-LEGAL-EVIDENCE-CAPACITY-RESERVATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: durable reservation persistence and lifecycle CAS only
# TENANT POSTURE: every operational read/write is exact-tenant scoped
# EXPIRY POSTURE: no TTL deletion; ACTIVE remains outstanding until durable transition
# TRANSACTION POSTURE: caller owns one already-active transaction
# RECONCILIATION POSTURE: P5D owns semantic reconciliation evidence/orchestration
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
