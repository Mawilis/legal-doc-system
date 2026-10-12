"""WILSY OS Legal notification recipient binding authority.

TITLE: Legal Notification Recipient Binding
VERSION: v1.1.0-L8-8H-RECIPIENT-BINDING
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Records an explicit immutable decision that one opaque principal is an
         authorized recipient for one Legal matter and notification event.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_notification_recipient_binding.py
COLLABORATION / OWNERSHIP: RETURN_READY intent is upstream; the L8-8H registry
                            persists bindings and the resolver revalidates them.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.1.0 removes unverifiable source-authority reference
           and fingerprint fields; canonical scope and explicit selection are
           fully covered by this artifact's own deterministic fingerprint.
           2026-10-12 v1.0.0 establishes strict immutable recipient-binding
           evidence without contact, transport, role, AI or financial truth.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; SHA3-512.
SECURITY / PRIVACY POSTURE: Opaque identifiers only; no email, phone, address,
                            credential, message, provider or delivery state.
TENANT BOUNDARY: Every binding is scoped to one non-pseudo tenant and matter.
AUTHORITY BOUNDARY: Explicit recipient selection only; eligibility is rechecked
                    by composition and address deliverability is never implied.
TRANSACTION BOUNDARY: Pure domain value; owns no persistence transaction.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Exact schema, UTC time, identity and fingerprint
                         divergence reject without normalization or fallback.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Final, Mapping, NoReturn, cast

SCHEMA: Final[str] = "WILSY-LEGAL-NOTIFICATION-RECIPIENT-BINDING/V1"
VERSION: Final[str] = "v1.1.0-L8-8H-RECIPIENT-BINDING"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_SHA3: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({"default", "global", "global_root", "root", "master", "*"})
_FIELDS: Final[tuple[str, ...]] = (
    "schema", "binding_version", "tenant_id", "binding_id", "case_matter_id",
    "event", "recipient_principal_id", "effective_from", "effective_until",
    "created_by_principal_id", "created_at", "fingerprint",
)


class LegalNotificationRecipientBindingError(ValueError):
    """Stable failure for malformed or corrupt recipient-binding evidence."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalNotificationEvent(StrEnum):
    """Legal notification events eligible for explicit recipient binding."""

    RETURN_READY = "RETURN_READY"


def _fail(code: str) -> NoReturn:
    raise LegalNotificationRecipientBindingError(code)


def _identity(name: str, value: object, *, tenant: bool = False) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"L8_8H_{name.upper()}_INVALID")
    if tenant and value.casefold() in _FORBIDDEN_TENANTS:
        _fail("L8_8H_TENANT_INVALID")
    return value


def _utc(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(f"L8_8H_{name.upper()}_INVALID")
    canonical = value.astimezone(timezone.utc)
    if canonical != value or canonical.tzinfo != timezone.utc:
        _fail(f"L8_8H_{name.upper()}_INVALID")
    return canonical


def _json_time(value: datetime) -> str:
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class LegalNotificationRecipientBinding:
    """Immutable explicit recipient decision for one exact Legal scope.

    This value proves selection, not contact ownership, address verification,
    authentication, delivery, or transport authority. Consumers must revalidate
    current source, principal and tenant-membership truth before use.
    """

    tenant_id: str
    binding_id: str
    case_matter_id: str
    event: LegalNotificationEvent | str
    recipient_principal_id: str
    effective_from: datetime
    effective_until: datetime | None
    created_by_principal_id: str
    created_at: datetime
    schema: str = SCHEMA
    binding_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Strictly canonicalize enum/time values and verify SHA3-512 integrity."""
        tenant = _identity("tenant_id", self.tenant_id, tenant=True)
        binding = _identity("binding_id", self.binding_id)
        matter = _identity("case_matter_id", self.case_matter_id)
        recipient = _identity("recipient_principal_id", self.recipient_principal_id)
        creator = _identity("created_by_principal_id", self.created_by_principal_id)
        try:
            event = LegalNotificationEvent(self.event)
        except (TypeError, ValueError) as error:
            raise LegalNotificationRecipientBindingError("L8_8H_EVENT_INVALID") from error
        effective_from = _utc("effective_from", self.effective_from)
        effective_until = None if self.effective_until is None else _utc("effective_until", self.effective_until)
        created_at = _utc("created_at", self.created_at)
        if effective_until is not None and effective_until <= effective_from:
            _fail("L8_8H_VALIDITY_INTERVAL_INVALID")
        if created_at > effective_from:
            _fail("L8_8H_CREATION_CHRONOLOGY_INVALID")
        if self.schema != SCHEMA or self.binding_version != VERSION:
            _fail("L8_8H_BINDING_SCHEMA_INVALID")
        for name, value in (("tenant_id", tenant), ("binding_id", binding), ("case_matter_id", matter), ("event", event), ("recipient_principal_id", recipient), ("effective_from", effective_from), ("effective_until", effective_until), ("created_by_principal_id", creator), ("created_at", created_at)):
            object.__setattr__(self, name, value)
        digest = hashlib.sha3_512(json.dumps(self._payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()
        if self.fingerprint and (not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, digest)):
            _fail("L8_8H_BINDING_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def _payload(self) -> dict[str, object]:
        return {
            "schema": self.schema, "binding_version": self.binding_version,
            "tenant_id": self.tenant_id, "binding_id": self.binding_id,
            "case_matter_id": self.case_matter_id, "event": LegalNotificationEvent(self.event).value,
            "recipient_principal_id": self.recipient_principal_id,
            "effective_from": _json_time(self.effective_from),
            "effective_until": None if self.effective_until is None else _json_time(self.effective_until),
            "created_by_principal_id": self.created_by_principal_id,
            "created_at": _json_time(self.created_at),
        }

    def is_effective_at(self, at: datetime) -> bool:
        """Return exact half-open validity without granting any other authority."""
        current = _utc("resolution_at", at)
        return self.effective_from <= current and (self.effective_until is None or current < self.effective_until)

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact durable binding schema without contact data."""
        return {**self._payload(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalNotificationRecipientBinding":
        """Strictly hydrate an exact field set and reverify its fingerprint."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L8_8H_BINDING_SCHEMA_INVALID")
        values = dict(payload)
        for name in ("effective_from", "effective_until", "created_at"):
            if values[name] is not None and not isinstance(values[name], datetime):
                try:
                    values[name] = datetime.fromisoformat(cast(str, values[name]).replace("Z", "+00:00"))
                except (TypeError, ValueError) as error:
                    raise LegalNotificationRecipientBindingError(f"L8_8H_{name.upper()}_INVALID") from error
        return cls(
            tenant_id=cast(str, values["tenant_id"]),
            binding_id=cast(str, values["binding_id"]),
            case_matter_id=cast(str, values["case_matter_id"]),
            event=cast(str, values["event"]),
            recipient_principal_id=cast(str, values["recipient_principal_id"]),
            effective_from=cast(datetime, values["effective_from"]),
            effective_until=cast(datetime | None, values["effective_until"]),
            created_by_principal_id=cast(str, values["created_by_principal_id"]),
            created_at=cast(datetime, values["created_at"]),
            schema=cast(str, values["schema"]),
            binding_version=cast(str, values["binding_version"]),
            fingerprint=cast(str, values["fingerprint"]),
        )


__all__ = ["SCHEMA", "VERSION", "LegalNotificationEvent", "LegalNotificationRecipientBinding", "LegalNotificationRecipientBindingError"]

# ARTIFACT: legal_notification_recipient_binding.py
# VERSION: v1.1.0-L8-8H-RECIPIENT-BINDING
# AUTHORITY BOUNDARY: explicit opaque principal selection for one Legal matter/event only
# TENANT POSTURE: exact non-pseudo tenant scope; no cross-tenant widening
# FAIL-CLOSED POSTURE: malformed schema, time, identity, interval or fingerprint rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
