"""WILSY OS Legal Operations return-ready notification intent domain.

TITLE: Legal Operations Return-Ready Notification Intent
VERSION: v1.0.0-L8-8E-RETURN-READY-NOTIFICATION-INTENT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Derive one immutable, tenant-scoped notification intent from an exact
         canonical ReturnOfService without selecting a recipient, sending a
         message, mutating Legal lifecycle, or granting financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_return_ready_notification.py
COLLABORATION / OWNERSHIP: P1 owns ReturnOfService truth. This domain owns only
                            the immutable RETURN_READY notification-intent value.
                            Persistence, recipient resolution, dispatch,
                            retry scheduling, transport and delivery evidence
                            remain separate bounded owners.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8E-RETURN-READY-NOTIFICATION-INTENT
           establishes exact ReturnOfService binding, deterministic SHA3-512
           integrity, PENDING intent semantics, strict hydration and an explicit
           no-recipient/no-transport/no-lifecycle-mutation authority boundary.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Stores only opaque Legal identities, source
                             fingerprints and timestamps. No email address,
                             phone number, message body, provider credentials,
                             transport secret, token, document bytes or PII.
TENANT BOUNDARY: tenant_id, instruction_id, document_id and return_id derive
                 only from one validated canonical ReturnOfService; callers
                 cannot assert or widen those identities independently.
AUTHORITY BOUNDARY: Notification intent only. RETURN_READY announces that a
                    canonical ReturnOfService exists; it does not certify
                    service, custody, client receipt, pickup, Court filing,
                    invoice truth, payment, execution or settlement.
TRANSACTION BOUNDARY: Pure immutable construction, deterministic serialization
                      and strict hydration only. No database, session,
                      transaction, retry, network or wall-clock ownership.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority; settlement remains separate.
FAIL-CLOSED DECLARATION: Malformed identities, pseudo tenants, source type,
                         source fingerprint, chronology, schema or fingerprint
                         drift reject without coercion or inferred authority.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Final, Mapping, NoReturn

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ReturnOfService,
    ReturnOfServiceState,
)


VERSION: Final[str] = "v1.0.0-L8-8E-RETURN-READY-NOTIFICATION-INTENT"
SCHEMA: Final[str] = "WILSY-LEGAL-RETURN-READY-NOTIFICATION/V1"

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_SHA3: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalReturnReadyNotificationError(ValueError):
    """Stable fail-closed error for malformed notification intent state."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalReturnReadyNotificationEvent(StrEnum):
    """Closed V1 event vocabulary backed by canonical Legal authority."""

    RETURN_READY = "RETURN_READY"


class LegalReturnReadyNotificationStatus(StrEnum):
    """Intent lifecycle before any recipient/transport owner acts."""

    PENDING = "PENDING"


def _fail(code: str) -> NoReturn:
    raise LegalReturnReadyNotificationError(code)


def _tenant(value: object) -> str:
    value = _identity("tenant_id", value)
    if value.casefold() in _FORBIDDEN_TENANTS:
        _fail("L8_8E_TENANT_INVALID")
    return value


def _identity(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"L8_8E_{name.upper()}_INVALID")
    return value


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(f"L8_8E_{name.upper()}_INVALID")
    return value


def _utc(name: str, value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(f"L8_8E_{name.upper()}_INVALID")
    try:
        return value.astimezone(timezone.utc)
    except (OverflowError, ValueError) as error:
        raise LegalReturnReadyNotificationError(
            f"L8_8E_{name.upper()}_INVALID"
        ) from error


def _parse_timestamp(name: str, value: object) -> datetime:
    if not isinstance(value, str):
        _fail(f"L8_8E_{name.upper()}_INVALID")
    try:
        return _utc(name, datetime.fromisoformat(value))
    except ValueError as error:
        raise LegalReturnReadyNotificationError(
            f"L8_8E_{name.upper()}_INVALID"
        ) from error


def _payload(
    *,
    tenant_id: str,
    notification_id: str,
    instruction_id: str,
    document_id: str,
    return_id: str,
    return_fingerprint: str,
    event: LegalReturnReadyNotificationEvent,
    occurred_at: datetime,
    status: LegalReturnReadyNotificationStatus,
) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "notification_version": VERSION,
        "tenant_id": tenant_id,
        "notification_id": notification_id,
        "instruction_id": instruction_id,
        "document_id": document_id,
        "return_id": return_id,
        "return_fingerprint": return_fingerprint,
        "event": event.value,
        "occurred_at": occurred_at.isoformat(),
        "status": status.value,
    }


def _digest(payload: Mapping[str, object]) -> str:
    raw = json.dumps(
        dict(payload),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalReturnReadyNotification:
    """Immutable intent announcing one canonical generated ReturnOfService.

    The value deliberately contains no recipient, address, phone, channel,
    provider, template, message body or delivery result. Those authorities must
    be resolved later by separately certified owners.
    """

    schema: str
    notification_version: str
    tenant_id: str
    notification_id: str
    instruction_id: str
    document_id: str
    return_id: str
    return_fingerprint: str
    event: LegalReturnReadyNotificationEvent
    occurred_at: datetime
    status: LegalReturnReadyNotificationStatus
    fingerprint: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            _fail("L8_8E_SCHEMA_INVALID")
        if self.notification_version != VERSION:
            _fail("L8_8E_VERSION_INVALID")

        tenant = _tenant(self.tenant_id)
        notification = _identity("notification_id", self.notification_id)
        instruction = _identity("instruction_id", self.instruction_id)
        document = _identity("document_id", self.document_id)
        return_id = _identity("return_id", self.return_id)
        return_fp = _fingerprint("return_fingerprint", self.return_fingerprint)

        if not isinstance(self.event, LegalReturnReadyNotificationEvent):
            _fail("L8_8E_EVENT_INVALID")
        if self.event is not LegalReturnReadyNotificationEvent.RETURN_READY:
            _fail("L8_8E_EVENT_INVALID")
        if not isinstance(self.status, LegalReturnReadyNotificationStatus):
            _fail("L8_8E_STATUS_INVALID")
        if self.status is not LegalReturnReadyNotificationStatus.PENDING:
            _fail("L8_8E_STATUS_INVALID")

        occurred = _utc("occurred_at", self.occurred_at)

        payload = _payload(
            tenant_id=tenant,
            notification_id=notification,
            instruction_id=instruction,
            document_id=document,
            return_id=return_id,
            return_fingerprint=return_fp,
            event=self.event,
            occurred_at=occurred,
            status=self.status,
        )
        expected = _digest(payload)
        fingerprint = _fingerprint("fingerprint", self.fingerprint)
        if not hmac.compare_digest(expected, fingerprint):
            _fail("L8_8E_FINGERPRINT_MISMATCH")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "notification_id", notification)
        object.__setattr__(self, "instruction_id", instruction)
        object.__setattr__(self, "document_id", document)
        object.__setattr__(self, "return_id", return_id)
        object.__setattr__(self, "return_fingerprint", return_fp)
        object.__setattr__(self, "occurred_at", occurred)
        object.__setattr__(self, "fingerprint", fingerprint)

    def to_dict(self) -> dict[str, object]:
        """Return the exact persisted-safe notification-intent mapping."""
        payload = _payload(
            tenant_id=self.tenant_id,
            notification_id=self.notification_id,
            instruction_id=self.instruction_id,
            document_id=self.document_id,
            return_id=self.return_id,
            return_fingerprint=self.return_fingerprint,
            event=self.event,
            occurred_at=self.occurred_at,
            status=self.status,
        )
        payload["fingerprint"] = self.fingerprint
        return payload

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalReturnReadyNotification":
        """Strictly hydrate one complete persisted notification intent."""
        expected_fields = {
            "schema",
            "notification_version",
            "tenant_id",
            "notification_id",
            "instruction_id",
            "document_id",
            "return_id",
            "return_fingerprint",
            "event",
            "occurred_at",
            "status",
            "fingerprint",
        }
        if not isinstance(payload, Mapping) or set(payload) != expected_fields:
            _fail("L8_8E_PAYLOAD_INVALID")
        try:
            event = LegalReturnReadyNotificationEvent(str(payload["event"]))
            status = LegalReturnReadyNotificationStatus(str(payload["status"]))
        except (TypeError, ValueError) as error:
            raise LegalReturnReadyNotificationError(
                "L8_8E_PAYLOAD_INVALID"
            ) from error

        return cls(
            schema=str(payload["schema"]),
            notification_version=str(payload["notification_version"]),
            tenant_id=str(payload["tenant_id"]),
            notification_id=str(payload["notification_id"]),
            instruction_id=str(payload["instruction_id"]),
            document_id=str(payload["document_id"]),
            return_id=str(payload["return_id"]),
            return_fingerprint=str(payload["return_fingerprint"]),
            event=event,
            occurred_at=_parse_timestamp("occurred_at", payload["occurred_at"]),
            status=status,
            fingerprint=str(payload["fingerprint"]),
        )


def create_return_ready_notification(
    *,
    return_of_service: ReturnOfService,
    notification_id: str,
) -> LegalReturnReadyNotification:
    """Derive one PENDING RETURN_READY intent from exact canonical return truth.

    Recipient selection and delivery are intentionally absent. The function
    does not mutate the return, custody, matter, document or any financial state.
    """
    if type(return_of_service) is not ReturnOfService:
        _fail("L8_8E_RETURN_OF_SERVICE_REQUIRED")
    try:
        return_of_service._validate()  # noqa: SLF001 - canonical source validation boundary.
    except Exception as error:
        raise LegalReturnReadyNotificationError(
            "L8_8E_RETURN_OF_SERVICE_INVALID"
        ) from error

    if return_of_service.state is not ReturnOfServiceState.GENERATED:
        _fail("L8_8E_RETURN_NOT_GENERATED")

    tenant = _tenant(return_of_service.tenant_id)
    notification = _identity("notification_id", notification_id)
    instruction = _identity("instruction_id", return_of_service.instruction_id)
    document = _identity("document_id", return_of_service.document_id)
    return_id = _identity("return_id", return_of_service.return_id)
    return_fp = _fingerprint(
        "return_fingerprint",
        return_of_service.fingerprint,
    )
    occurred = _utc("occurred_at", return_of_service.generated_at)
    event = LegalReturnReadyNotificationEvent.RETURN_READY
    status = LegalReturnReadyNotificationStatus.PENDING

    payload = _payload(
        tenant_id=tenant,
        notification_id=notification,
        instruction_id=instruction,
        document_id=document,
        return_id=return_id,
        return_fingerprint=return_fp,
        event=event,
        occurred_at=occurred,
        status=status,
    )

    return LegalReturnReadyNotification(
        schema=SCHEMA,
        notification_version=VERSION,
        tenant_id=tenant,
        notification_id=notification,
        instruction_id=instruction,
        document_id=document,
        return_id=return_id,
        return_fingerprint=return_fp,
        event=event,
        occurred_at=occurred,
        status=status,
        fingerprint=_digest(payload),
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalReturnReadyNotification",
    "LegalReturnReadyNotificationError",
    "LegalReturnReadyNotificationEvent",
    "LegalReturnReadyNotificationStatus",
    "create_return_ready_notification",
]


# ARTIFACT: legal_return_ready_notification.py
# VERSION: v1.0.0-L8-8E-RETURN-READY-NOTIFICATION-INTENT
# AUTHORITY BOUNDARY: immutable RETURN_READY intent only; no recipient resolution, transport, lifecycle mutation, Court, billing or financial authority
# TENANT POSTURE: all durable Legal identities derive from one validated canonical ReturnOfService
# DELIVERY POSTURE: PENDING intent only; no channel, recipient, provider, message body or delivery result exists here
# FAIL-CLOSED POSTURE: source/type/scope/chronology/schema/fingerprint divergence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
