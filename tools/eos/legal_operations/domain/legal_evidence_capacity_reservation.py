"""WILSY OS immutable Legal Evidence capacity reservation lifecycle.

TITLE: Legal Evidence Capacity Reservation
VERSION: v1.0.0-L10A2Q-P5A-LEGAL-EVIDENCE-CAPACITY-RESERVATION
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Define one immutable tenant/document/ingestion-intent reservation lifecycle
    for the exact capacity dimensions consumed by Legal Evidence accounting.

EPITOME:
    REMAINING CAPACITY
    -> CAPACITY RESERVED
    != STORAGE ADMITTED
    != PROVIDER OBJECT WRITTEN
    != USAGE CONSUMED
    != IAM AUTHORIZED
    != BILLING / PAYMENT / SETTLEMENT

LIFECYCLE:
    ACTIVE may transition exactly once to CONSUMED, RELEASED or EXPIRED.
    Terminal states are durable evidence and are never revived.

EXPIRY:
    consume/release require observed_at < expires_at.
    expire requires observed_at >= expires_at.

AUTHORITY BOUNDARY:
    Pure immutable lifecycle evidence only. Persistence, indexes, CAS,
    concurrency, admission, provider execution, usage mutation and
    reconciliation are owned by later P5 gates.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, Self, cast


VERSION: Final[str] = (
    "v1.0.0-L10A2Q-P5A-LEGAL-EVIDENCE-CAPACITY-RESERVATION"
)
SCHEMA: Final[str] = "WILSY-LEGAL-EVIDENCE-CAPACITY-RESERVATION/V1"

_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,511}$"
)
_SHA3_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "root",
        "*",
        "global_root",
    }
)

_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id",
    "document_id",
    "reservation_id",
    "ingestion_intent_id",
    "remaining_capacity_fingerprint",
    "reserved_storage_bytes",
    "reserved_ingress_bytes",
    "reserved_document_versions",
    "reserved_at",
    "expires_at",
    "status",
    "consumed_at",
    "released_at",
    "expired_at",
    "schema",
    "reservation_version",
    "fingerprint",
)


class LegalEvidenceCapacityReservationError(ValueError):
    """Raised when immutable reservation lifecycle evidence is invalid."""


class LegalEvidenceCapacityReservationStatus(StrEnum):
    """Closed reservation lifecycle vocabulary."""

    ACTIVE = "ACTIVE"
    CONSUMED = "CONSUMED"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"


def _identity(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceCapacityReservationError(
            f"L10A2Q_P5A_{name.upper()}_INVALID"
        )
    return value


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.lower() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceCapacityReservationError(
            "L10A2Q_P5A_TENANT_REQUIRED"
        )
    return tenant


def _utc(name: str, value: object) -> datetime:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError as error:
            raise LegalEvidenceCapacityReservationError(
                f"L10A2Q_P5A_{name.upper()}_INVALID"
            ) from error

    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceCapacityReservationError(
            f"L10A2Q_P5A_{name.upper()}_INVALID"
        )

    return value.astimezone(timezone.utc)


def _optional_utc(
    name: str,
    value: object,
) -> datetime | None:
    if value is None:
        return None
    return _utc(name, value)


def _sha3(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or _SHA3_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceCapacityReservationError(
            f"L10A2Q_P5A_{name.upper()}_INVALID"
        )
    return value


def _positive(name: str, value: object) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        raise LegalEvidenceCapacityReservationError(
            f"L10A2Q_P5A_{name.upper()}_INVALID"
        )
    return value


def _timestamp_text(value: datetime) -> str:
    return (
        value.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return _timestamp_text(value)
    if isinstance(value, StrEnum):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class LegalEvidenceCapacityReservation:
    """Immutable P5A reservation lifecycle evidence."""

    tenant_id: str
    document_id: str
    reservation_id: str
    ingestion_intent_id: str

    remaining_capacity_fingerprint: str

    reserved_storage_bytes: int
    reserved_ingress_bytes: int
    reserved_document_versions: int

    reserved_at: datetime
    expires_at: datetime

    status: LegalEvidenceCapacityReservationStatus = (
        LegalEvidenceCapacityReservationStatus.ACTIVE
    )

    consumed_at: datetime | None = None
    released_at: datetime | None = None
    expired_at: datetime | None = None

    schema: str = SCHEMA
    reservation_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate lifecycle invariants and bind deterministic SHA3-512."""
        tenant = _tenant(self.tenant_id)
        document = _identity("document_id", self.document_id)
        reservation = _identity(
            "reservation_id",
            self.reservation_id,
        )
        intent = _identity(
            "ingestion_intent_id",
            self.ingestion_intent_id,
        )

        remaining_capacity_fingerprint = _sha3(
            "remaining_capacity_fingerprint",
            self.remaining_capacity_fingerprint,
        )

        reserved_storage_bytes = _positive(
            "reserved_storage_bytes",
            self.reserved_storage_bytes,
        )
        reserved_ingress_bytes = _positive(
            "reserved_ingress_bytes",
            self.reserved_ingress_bytes,
        )
        reserved_document_versions = _positive(
            "reserved_document_versions",
            self.reserved_document_versions,
        )

        reserved_at = _utc(
            "reserved_at",
            self.reserved_at,
        )
        expires_at = _utc(
            "expires_at",
            self.expires_at,
        )

        if expires_at <= reserved_at:
            raise LegalEvidenceCapacityReservationError(
                "L10A2Q_P5A_EXPIRY_INVALID"
            )

        if type(self.status) is not LegalEvidenceCapacityReservationStatus:
            raise LegalEvidenceCapacityReservationError(
                "L10A2Q_P5A_STATUS_INVALID"
            )

        consumed_at = _optional_utc(
            "consumed_at",
            self.consumed_at,
        )
        released_at = _optional_utc(
            "released_at",
            self.released_at,
        )
        expired_at = _optional_utc(
            "expired_at",
            self.expired_at,
        )

        terminal_count = sum(
            value is not None
            for value in (
                consumed_at,
                released_at,
                expired_at,
            )
        )

        if self.status is LegalEvidenceCapacityReservationStatus.ACTIVE:
            if terminal_count != 0:
                raise LegalEvidenceCapacityReservationError(
                    "L10A2Q_P5A_ACTIVE_TERMINAL_TIMESTAMP_INVALID"
                )

        elif self.status is LegalEvidenceCapacityReservationStatus.CONSUMED:
            if (
                consumed_at is None
                or terminal_count != 1
                or consumed_at < reserved_at
                or consumed_at >= expires_at
            ):
                raise LegalEvidenceCapacityReservationError(
                    "L10A2Q_P5A_CONSUMED_STATE_INVALID"
                )

        elif self.status is LegalEvidenceCapacityReservationStatus.RELEASED:
            if (
                released_at is None
                or terminal_count != 1
                or released_at < reserved_at
                or released_at >= expires_at
            ):
                raise LegalEvidenceCapacityReservationError(
                    "L10A2Q_P5A_RELEASED_STATE_INVALID"
                )

        elif self.status is LegalEvidenceCapacityReservationStatus.EXPIRED:
            if (
                expired_at is None
                or terminal_count != 1
                or expired_at < expires_at
            ):
                raise LegalEvidenceCapacityReservationError(
                    "L10A2Q_P5A_EXPIRED_STATE_INVALID"
                )

        if (
            self.schema != SCHEMA
            or self.reservation_version != VERSION
        ):
            raise LegalEvidenceCapacityReservationError(
                "L10A2Q_P5A_SCHEMA_INVALID"
            )

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "document_id", document)
        object.__setattr__(self, "reservation_id", reservation)
        object.__setattr__(self, "ingestion_intent_id", intent)
        object.__setattr__(
            self,
            "remaining_capacity_fingerprint",
            remaining_capacity_fingerprint,
        )
        object.__setattr__(
            self,
            "reserved_storage_bytes",
            reserved_storage_bytes,
        )
        object.__setattr__(
            self,
            "reserved_ingress_bytes",
            reserved_ingress_bytes,
        )
        object.__setattr__(
            self,
            "reserved_document_versions",
            reserved_document_versions,
        )
        object.__setattr__(
            self,
            "reserved_at",
            reserved_at,
        )
        object.__setattr__(
            self,
            "expires_at",
            expires_at,
        )
        object.__setattr__(
            self,
            "consumed_at",
            consumed_at,
        )
        object.__setattr__(
            self,
            "released_at",
            released_at,
        )
        object.__setattr__(
            self,
            "expired_at",
            expired_at,
        )

        payload = {
            field: _json_value(getattr(self, field))
            for field in _FIELDS[:-1]
        }

        digest = hashlib.sha3_512(
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        if self.fingerprint:
            if (
                not isinstance(self.fingerprint, str)
                or not hmac.compare_digest(
                    self.fingerprint,
                    digest,
                )
            ):
                raise LegalEvidenceCapacityReservationError(
                    "L10A2Q_P5A_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def _assert_active(self) -> None:
        if self.status is not LegalEvidenceCapacityReservationStatus.ACTIVE:
            raise LegalEvidenceCapacityReservationError(
                "L10A2Q_P5A_TERMINAL_RESERVATION"
            )

    def consume(
        self,
        consumed_at: datetime,
    ) -> Self:
        """Return one immutable CONSUMED successor before expiry."""
        self._assert_active()
        observed = _utc("consumed_at", consumed_at)

        if observed < self.reserved_at:
            raise LegalEvidenceCapacityReservationError(
                "L10A2Q_P5A_CONSUMED_AT_INVALID"
            )

        if observed >= self.expires_at:
            raise LegalEvidenceCapacityReservationError(
                "L10A2Q_P5A_RESERVATION_EXPIRED"
            )

        return replace(
            self,
            status=LegalEvidenceCapacityReservationStatus.CONSUMED,
            consumed_at=observed,
            released_at=None,
            expired_at=None,
            fingerprint="",
        )

    def release(
        self,
        released_at: datetime,
    ) -> Self:
        """Return one immutable RELEASED successor before expiry."""
        self._assert_active()
        observed = _utc("released_at", released_at)

        if observed < self.reserved_at:
            raise LegalEvidenceCapacityReservationError(
                "L10A2Q_P5A_RELEASED_AT_INVALID"
            )

        if observed >= self.expires_at:
            raise LegalEvidenceCapacityReservationError(
                "L10A2Q_P5A_RESERVATION_EXPIRED"
            )

        return replace(
            self,
            status=LegalEvidenceCapacityReservationStatus.RELEASED,
            consumed_at=None,
            released_at=observed,
            expired_at=None,
            fingerprint="",
        )

    def expire(
        self,
        expired_at: datetime,
    ) -> Self:
        """Return one immutable EXPIRED successor at or after expiry."""
        self._assert_active()
        observed = _utc("expired_at", expired_at)

        if observed < self.expires_at:
            raise LegalEvidenceCapacityReservationError(
                "L10A2Q_P5A_EXPIRY_BOUNDARY_NOT_REACHED"
            )

        return replace(
            self,
            status=LegalEvidenceCapacityReservationStatus.EXPIRED,
            consumed_at=None,
            released_at=None,
            expired_at=observed,
            fingerprint="",
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize exact deterministic reservation lifecycle evidence."""
        return {
            field: _json_value(getattr(self, field))
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalEvidenceCapacityReservation":
        """Strictly hydrate exact reservation lifecycle evidence."""
        if (
            not isinstance(payload, Mapping)
            or set(payload) != set(_FIELDS)
        ):
            raise LegalEvidenceCapacityReservationError(
                "L10A2Q_P5A_SCHEMA_INVALID"
            )

        values = dict(payload)
        stored_fingerprint = values.pop("fingerprint")

        try:
            values["status"] = LegalEvidenceCapacityReservationStatus(
                cast(str, values["status"])
            )
        except (TypeError, ValueError) as error:
            raise LegalEvidenceCapacityReservationError(
                "L10A2Q_P5A_STATUS_INVALID"
            ) from error

        for field in (
            "reserved_at",
            "expires_at",
            "consumed_at",
            "released_at",
            "expired_at",
        ):
            raw = values[field]
            if raw is not None:
                values[field] = _utc(field, raw)

        item = cls(
            **cast(
                Any,
                values,
            )
        )

        if (
            not isinstance(stored_fingerprint, str)
            or not hmac.compare_digest(
                stored_fingerprint,
                item.fingerprint,
            )
        ):
            raise LegalEvidenceCapacityReservationError(
                "L10A2Q_P5A_FINGERPRINT_MISMATCH"
            )

        return item


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalEvidenceCapacityReservation",
    "LegalEvidenceCapacityReservationError",
    "LegalEvidenceCapacityReservationStatus",
]


# ARTIFACT: legal_evidence_capacity_reservation.py
# VERSION: v1.0.0-L10A2Q-P5A-LEGAL-EVIDENCE-CAPACITY-RESERVATION
# AUTHORITY BOUNDARY: immutable reservation lifecycle evidence only
# TENANT POSTURE: exact tenant/document/ingestion-intent binding
# EXPIRY POSTURE: terminal evidence retained; no TTL deletion semantics
# CONCURRENCY POSTURE: P5B/P5C own persistence and atomic CAS
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
