"""WILSY OS durable Legal Evidence capacity reservation registry.

TITLE: Legal Evidence Capacity Reservation Registry
VERSION: v1.0.0-L10A2Q-P5B-LEGAL-EVIDENCE-CAPACITY-RESERVATION-REGISTRY
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Persist immutable P5A Legal Evidence capacity reservations under exact
    tenant scope with deterministic create/replay semantics, strict hydration,
    durable terminal lifecycle state and atomic ACTIVE-state CAS transitions.

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
    No TTL deletion is used. An ACTIVE row remains durable ACTIVE evidence until
    an explicit lifecycle transition persists EXPIRED. Wall-clock time alone
    never silently releases capacity.

TRANSACTION:
    Every operational read/write requires one caller-owned already-active Mongo
    transaction. The registry never creates, commits, aborts or retries it.

AUTHORITY BOUNDARY:
    Persistence and low-level lifecycle compare-and-set only. P5C owns atomic
    capacity admission/reservation orchestration. P5D owns semantic terminal
    reconciliation evidence and orchestration.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
    LegalEvidenceCapacityReservationError,
    LegalEvidenceCapacityReservationStatus,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2Q-P5B-LEGAL-EVIDENCE-CAPACITY-RESERVATION-REGISTRY"
)

COLLECTION: Final[str] = "legal_evidence_capacity_reservations"

INDEX_TENANT_RESERVATION: Final[str] = (
    "legal_evidence_capacity_reservation_tenant_reservation_unique"
)
INDEX_TENANT_INGESTION_INTENT: Final[str] = (
    "legal_evidence_capacity_reservation_tenant_ingestion_intent_unique"
)
INDEX_TENANT_IDEMPOTENCY: Final[str] = (
    "legal_evidence_capacity_reservation_tenant_idempotency_unique"
)
INDEX_TENANT_STATUS_EXPIRY: Final[str] = (
    "legal_evidence_capacity_reservation_tenant_status_expiry"
)
INDEX_TENANT_DOCUMENT_STATUS: Final[str] = (
    "legal_evidence_capacity_reservation_tenant_document_status"
)

_HEX_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")


class LegalEvidenceCapacityReservationRegistryError(RuntimeError):
    """Base P5B registry error."""


class LegalEvidenceCapacityReservationTransactionRequiredError(
    LegalEvidenceCapacityReservationRegistryError
):
    """Caller did not supply one already-active transaction."""


class LegalEvidenceCapacityReservationConflictError(
    LegalEvidenceCapacityReservationRegistryError
):
    """Durable reservation identity, replay or lifecycle state conflicts."""


class LegalEvidenceCapacityReservationNotFoundError(
    LegalEvidenceCapacityReservationRegistryError
):
    """Exact tenant-scoped reservation was not found."""


class LegalEvidenceCapacityReservationPersistedRecordInvalidError(
    LegalEvidenceCapacityReservationRegistryError
):
    """Persisted durable reservation evidence failed strict hydration."""


class LegalEvidenceCapacityReservationPersistenceError(
    LegalEvidenceCapacityReservationRegistryError
):
    """Mongo persistence or read operation failed."""


def _active_transaction(session: Any) -> Any:
    if session is None or not bool(getattr(session, "in_transaction", False)):
        raise LegalEvidenceCapacityReservationTransactionRequiredError(
            "L10A2Q_P5B_TRANSACTION_REQUIRED"
        )
    return session


def _text(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or value != value.strip()
    ):
        raise LegalEvidenceCapacityReservationRegistryError(
            f"L10A2Q_P5B_{name.upper()}_INVALID"
        )
    return value


def _epoch_microseconds(value: datetime) -> int:
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (
        value.astimezone(timezone.utc) - epoch
    ) // __import__("datetime").timedelta(microseconds=1)


def _creation_command_payload(
    reservation: LegalEvidenceCapacityReservation,
    idempotency_key: str,
) -> dict[str, object]:
    """Return immutable reservation-creation command fields only.

    Lifecycle status and terminal timestamps are deliberately excluded so the
    creation command fingerprint remains stable across durable CAS transitions.
    """

    return {
        "tenant_id": reservation.tenant_id,
        "document_id": reservation.document_id,
        "reservation_id": reservation.reservation_id,
        "ingestion_intent_id": reservation.ingestion_intent_id,
        "remaining_capacity_fingerprint":
            reservation.remaining_capacity_fingerprint,
        "reserved_storage_bytes": reservation.reserved_storage_bytes,
        "reserved_ingress_bytes": reservation.reserved_ingress_bytes,
        "reserved_document_versions": reservation.reserved_document_versions,
        "reserved_at": reservation.to_dict()["reserved_at"],
        "expires_at": reservation.to_dict()["expires_at"],
        "idempotency_key": idempotency_key,
    }


def _command_fingerprint(
    reservation: LegalEvidenceCapacityReservation,
    idempotency_key: str,
) -> str:
    payload = _creation_command_payload(
        reservation,
        idempotency_key,
    )
    return hashlib.sha3_512(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _document(
    reservation: LegalEvidenceCapacityReservation,
    *,
    idempotency_key: str,
) -> dict[str, object]:
    payload = reservation.to_dict()
    payload.update(
        {
            "idempotency_key": idempotency_key,
            "command_fingerprint": _command_fingerprint(
                reservation,
                idempotency_key,
            ),
            "_expires_at_epoch_us": _epoch_microseconds(
                reservation.expires_at
            ),
        }
    )
    return payload


def _hydrate(row: Mapping[str, Any]) -> LegalEvidenceCapacityReservation:
    try:
        raw = dict(row)
        raw.pop("_id", None)

        idempotency_key = raw.pop("idempotency_key")
        command_fingerprint = raw.pop("command_fingerprint")
        expires_epoch = raw.pop("_expires_at_epoch_us")

        if (
            not isinstance(idempotency_key, str)
            or not idempotency_key.strip()
            or idempotency_key != idempotency_key.strip()
            or not isinstance(command_fingerprint, str)
            or _HEX_RE.fullmatch(command_fingerprint) is None
            or isinstance(expires_epoch, bool)
            or not isinstance(expires_epoch, int)
        ):
            raise ValueError("metadata invalid")

        reservation = LegalEvidenceCapacityReservation.from_dict(
            cast(Mapping[str, object], raw)
        )

        if (
            _epoch_microseconds(reservation.expires_at)
            != expires_epoch
        ):
            raise ValueError("expiry metadata invalid")

        expected_command = _command_fingerprint(
            reservation,
            idempotency_key,
        )

        if not hmac.compare_digest(
            command_fingerprint,
            expected_command,
        ):
            raise ValueError("command fingerprint invalid")

        return reservation

    except (
        KeyError,
        TypeError,
        ValueError,
        LegalEvidenceCapacityReservationError,
    ) as error:
        raise LegalEvidenceCapacityReservationPersistedRecordInvalidError(
            "L10A2Q_P5B_PERSISTED_RECORD_INVALID"
        ) from error


def _raise_mongo(
    code: str,
    error: BaseException,
) -> NoReturn:
    raise LegalEvidenceCapacityReservationPersistenceError(code) from error


class LegalEvidenceCapacityReservationRegistry:
    """Durable tenant-scoped reservation persistence and lifecycle CAS."""

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create durable reservation indexes; never create TTL deletion."""
        try:
            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("reservation_id", ASCENDING),
                ],
                unique=True,
                name=INDEX_TENANT_RESERVATION,
            )
            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("ingestion_intent_id", ASCENDING),
                ],
                unique=True,
                name=INDEX_TENANT_INGESTION_INTENT,
            )
            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("idempotency_key", ASCENDING),
                ],
                unique=True,
                name=INDEX_TENANT_IDEMPOTENCY,
            )
            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("status", ASCENDING),
                    ("_expires_at_epoch_us", ASCENDING),
                ],
                unique=False,
                name=INDEX_TENANT_STATUS_EXPIRY,
            )
            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("document_id", ASCENDING),
                    ("status", ASCENDING),
                ],
                unique=False,
                name=INDEX_TENANT_DOCUMENT_STATUS,
            )
        except PyMongoError as error:
            _raise_mongo(
                "L10A2Q_P5B_INDEX_CREATION_FAILED",
                error,
            )

    def create_or_replay(
        self,
        reservation: LegalEvidenceCapacityReservation,
        *,
        idempotency_key: str,
        session: Any,
    ) -> LegalEvidenceCapacityReservation:
        """Persist one ACTIVE reservation or return one exact durable replay."""
        tx = _active_transaction(session)

        if type(reservation) is not LegalEvidenceCapacityReservation:
            raise LegalEvidenceCapacityReservationConflictError(
                "L10A2Q_P5B_RESERVATION_REQUIRED"
            )

        if (
            reservation.status
            is not LegalEvidenceCapacityReservationStatus.ACTIVE
        ):
            raise LegalEvidenceCapacityReservationConflictError(
                "L10A2Q_P5B_CREATE_REQUIRES_ACTIVE"
            )

        key = _text("idempotency_key", idempotency_key)
        command = _command_fingerprint(reservation, key)

        try:
            existing = self._collection.find_one(
                {
                    "tenant_id": reservation.tenant_id,
                    "idempotency_key": key,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo("L10A2Q_P5B_READ_FAILED", error)

        if existing is not None:
            persisted = _hydrate(existing)
            if existing.get("command_fingerprint") != command:
                raise LegalEvidenceCapacityReservationConflictError(
                    "L10A2Q_P5B_DIVERGENT_IDEMPOTENCY"
                )
            return persisted

        try:
            identity = self._collection.find_one(
                {
                    "tenant_id": reservation.tenant_id,
                    "reservation_id": reservation.reservation_id,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo("L10A2Q_P5B_READ_FAILED", error)

        if identity is not None:
            persisted = _hydrate(identity)
            if persisted != reservation:
                raise LegalEvidenceCapacityReservationConflictError(
                    "L10A2Q_P5B_DIVERGENT_RESERVATION_IDENTITY"
                )
            raise LegalEvidenceCapacityReservationConflictError(
                "L10A2Q_P5B_RESERVATION_IDENTITY_REQUIRES_EXACT_REPLAY_KEY"
            )

        try:
            intent = self._collection.find_one(
                {
                    "tenant_id": reservation.tenant_id,
                    "ingestion_intent_id":
                        reservation.ingestion_intent_id,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo("L10A2Q_P5B_READ_FAILED", error)

        if intent is not None:
            persisted = _hydrate(intent)
            if persisted != reservation:
                raise LegalEvidenceCapacityReservationConflictError(
                    "L10A2Q_P5B_DIVERGENT_INGESTION_INTENT"
                )
            raise LegalEvidenceCapacityReservationConflictError(
                "L10A2Q_P5B_INGESTION_INTENT_REQUIRES_EXACT_REPLAY_KEY"
            )

        try:
            self._collection.insert_one(
                _document(
                    reservation,
                    idempotency_key=key,
                ),
                session=tx,
            )
        except DuplicateKeyError as error:
            raise LegalEvidenceCapacityReservationConflictError(
                "L10A2Q_P5B_DUPLICATE_RESERVATION"
            ) from error
        except PyMongoError as error:
            _raise_mongo("L10A2Q_P5B_CREATE_FAILED", error)

        return reservation

    def get(
        self,
        *,
        tenant_id: str,
        reservation_id: str,
        session: Any,
    ) -> LegalEvidenceCapacityReservation:
        """Return one exact tenant reservation or scoped not-found."""
        tx = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)
        identity = _text("reservation_id", reservation_id)

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "reservation_id": identity,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo("L10A2Q_P5B_READ_FAILED", error)

        if row is None:
            raise LegalEvidenceCapacityReservationNotFoundError(
                "L10A2Q_P5B_RESERVATION_NOT_FOUND"
            )

        return _hydrate(row)

    def list_active_reservations(
        self,
        *,
        tenant_id: str,
        session: Any,
        document_id: str | None = None,
    ) -> list[LegalEvidenceCapacityReservation]:
        """Return all durable ACTIVE reservations for exact tenant scope.

        Deliberately performs no wall-clock expiry predicate. An ACTIVE row is
        still outstanding until an explicit durable lifecycle transition says
        otherwise.
        """
        tx = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)

        query: dict[str, object] = {
            "tenant_id": tenant,
            "status":
                LegalEvidenceCapacityReservationStatus.ACTIVE.value,
        }

        if document_id is not None:
            query["document_id"] = _text(
                "document_id",
                document_id,
            )

        try:
            cursor = self._collection.find(
                query,
                session=tx,
            )
            return [
                _hydrate(cast(Mapping[str, Any], row))
                for row in cursor
            ]
        except PyMongoError as error:
            _raise_mongo("L10A2Q_P5B_READ_FAILED", error)

    def _transition(
        self,
        reservation: LegalEvidenceCapacityReservation,
        observed_at: datetime,
        *,
        operation: str,
        successor: LegalEvidenceCapacityReservation,
        session: Any,
    ) -> LegalEvidenceCapacityReservation:
        """Execute one durable ACTIVE-state compare-and-set transition."""
        tx = _active_transaction(session)

        query: dict[str, object] = {
            "tenant_id": reservation.tenant_id,
            "reservation_id": reservation.reservation_id,
            "status":
                LegalEvidenceCapacityReservationStatus.ACTIVE.value,
            "fingerprint": reservation.fingerprint,
        }

        observed_epoch = _epoch_microseconds(
            observed_at.astimezone(timezone.utc)
        )

        if operation == "expire":
            query["_expires_at_epoch_us"] = {
                "$lte": observed_epoch
            }
        else:
            query["_expires_at_epoch_us"] = {
                "$gt": observed_epoch
            }

        successor_payload = successor.to_dict()

        terminal_field = {
            "consume": "consumed_at",
            "release": "released_at",
            "expire": "expired_at",
        }[operation]

        update = {
            "$set": {
                "status": successor_payload["status"],
                terminal_field:
                    successor_payload[terminal_field],
                "fingerprint": successor.fingerprint,
            }
        }

        try:
            row = self._collection.find_one_and_update(
                query,
                update,
                return_document=ReturnDocument.AFTER,
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(
                "L10A2Q_P5B_TRANSITION_FAILED",
                error,
            )

        if row is None:
            try:
                current = self._collection.find_one(
                    {
                        "tenant_id": reservation.tenant_id,
                        "reservation_id":
                            reservation.reservation_id,
                    },
                    session=tx,
                )
            except PyMongoError as error:
                _raise_mongo(
                    "L10A2Q_P5B_TRANSITION_CLASSIFICATION_FAILED",
                    error,
                )

            if current is None:
                raise LegalEvidenceCapacityReservationNotFoundError(
                    "L10A2Q_P5B_RESERVATION_NOT_FOUND"
                )

            _hydrate(current)

            raise LegalEvidenceCapacityReservationConflictError(
                "L10A2Q_P5B_LIFECYCLE_CONFLICT"
            )

        return _hydrate(row)

    def consume(
        self,
        reservation: LegalEvidenceCapacityReservation,
        consumed_at: datetime,
        *,
        session: Any,
    ) -> LegalEvidenceCapacityReservation:
        """Atomically persist ACTIVE -> CONSUMED before expiry."""
        if type(reservation) is not LegalEvidenceCapacityReservation:
            raise LegalEvidenceCapacityReservationConflictError(
                "L10A2Q_P5B_TRANSITION_INVALID"
            )
        try:
            successor = reservation.consume(consumed_at)
        except LegalEvidenceCapacityReservationError as error:
            raise LegalEvidenceCapacityReservationConflictError(
                str(error)
            ) from error

        return self._transition(
            reservation,
            consumed_at,
            operation="consume",
            successor=successor,
            session=session,
        )

    def release(
        self,
        reservation: LegalEvidenceCapacityReservation,
        released_at: datetime,
        *,
        session: Any,
    ) -> LegalEvidenceCapacityReservation:
        """Atomically persist ACTIVE -> RELEASED before expiry."""
        if type(reservation) is not LegalEvidenceCapacityReservation:
            raise LegalEvidenceCapacityReservationConflictError(
                "L10A2Q_P5B_TRANSITION_INVALID"
            )
        try:
            successor = reservation.release(released_at)
        except LegalEvidenceCapacityReservationError as error:
            raise LegalEvidenceCapacityReservationConflictError(
                str(error)
            ) from error

        return self._transition(
            reservation,
            released_at,
            operation="release",
            successor=successor,
            session=session,
        )

    def expire(
        self,
        reservation: LegalEvidenceCapacityReservation,
        expired_at: datetime,
        *,
        session: Any,
    ) -> LegalEvidenceCapacityReservation:
        """Atomically persist ACTIVE -> EXPIRED at or after expiry."""
        if type(reservation) is not LegalEvidenceCapacityReservation:
            raise LegalEvidenceCapacityReservationConflictError(
                "L10A2Q_P5B_TRANSITION_INVALID"
            )
        try:
            successor = reservation.expire(expired_at)
        except LegalEvidenceCapacityReservationError as error:
            raise LegalEvidenceCapacityReservationConflictError(
                str(error)
            ) from error

        return self._transition(
            reservation,
            expired_at,
            operation="expire",
            successor=successor,
            session=session,
        )


__all__ = [
    "COLLECTION",
    "INDEX_TENANT_DOCUMENT_STATUS",
    "INDEX_TENANT_IDEMPOTENCY",
    "INDEX_TENANT_INGESTION_INTENT",
    "INDEX_TENANT_RESERVATION",
    "INDEX_TENANT_STATUS_EXPIRY",
    "VERSION",
    "LegalEvidenceCapacityReservationConflictError",
    "LegalEvidenceCapacityReservationNotFoundError",
    "LegalEvidenceCapacityReservationPersistedRecordInvalidError",
    "LegalEvidenceCapacityReservationPersistenceError",
    "LegalEvidenceCapacityReservationRegistry",
    "LegalEvidenceCapacityReservationRegistryError",
    "LegalEvidenceCapacityReservationTransactionRequiredError",
]


# ARTIFACT: legal_evidence_capacity_reservation_registry.py
# VERSION: v1.0.0-L10A2Q-P5B-LEGAL-EVIDENCE-CAPACITY-RESERVATION-REGISTRY
# AUTHORITY BOUNDARY: durable reservation persistence and lifecycle CAS only
# TENANT POSTURE: every operational read/write is exact-tenant scoped
# EXPIRY POSTURE: no TTL deletion; ACTIVE remains outstanding until durable CAS
# TRANSACTION POSTURE: caller owns one already-active transaction
# RECONCILIATION POSTURE: P5D owns semantic reconciliation evidence/orchestration
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
