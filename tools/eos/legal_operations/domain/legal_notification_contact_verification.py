"""WILSY OS Legal notification-contact verification capability domain.

TITLE: Legal Notification Contact Verification
VERSION: v1.0.0-L8-8H7A-LEGAL-NOTIFICATION-CONTACT-VERIFICATION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Represent one immutable single-use Legal notification email-control
         verification capability bound to an exact tenant, principal, channel,
         address digest, token digest, issuance instant, expiry, and terminal
         lifecycle without storing raw contact addresses or granting dispatch.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_notification_contact_verification.py
COLLABORATION / OWNERSHIP: Legal Operations owns Legal notification-contact
                           verification meaning only. Durable principal/email
                           truth remains upstream Auth authority. Recovery-contact
                           authority is purpose-bound and MUST NOT be imported,
                           aliased, or treated as Legal notification authority.
                           Future registry/service layers may persist or consume
                           this value but may not widen its authority.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0-L8-8H7A-LEGAL-NOTIFICATION-CONTACT-VERIFICATION establishes
           the pure immutable single-use Legal notification-contact verification
           capability domain for EMAIL only. The value stores SHA3-512 address
           and token digests rather than raw address/token material; models
           ACTIVE, CONSUMED, EXPIRED, and REVOKED terminal lifecycle; enforces
           strict UTC chronology; supports deterministic integrity hashing and
           exact hydration; and creates no contact authority, recipient
           selection, dispatch, delivery, Court, AI, billing, payment,
           execution, or settlement truth.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Raw email addresses and raw verification tokens are
                            never represented or persisted by this domain.
                            Address and token evidence are lowercase SHA3-512
                            digests only. Terminal lifecycle states are mutually
                            exclusive and fail closed on corruption or replay.
TENANT BOUNDARY: Every verification is bound to one explicit non-global tenant_id
                 and one exact principal_id. This value cannot infer tenant,
                 membership, role, recipient selection, or cross-tenant truth.
AUTHORITY BOUNDARY: Single-use Legal notification email-control verification
                    capability evidence only. Creation does not prove verified
                    Legal contact authority; successful consumption is merely a
                    prerequisite input to a later Legal verified-contact domain.
                    Verification != contact authority != recipient selection
                    != dispatch != delivery.
FINANCIAL AUTHORITY BOUNDARY: None. No invoice, payment, release, execution,
                              settlement, or accounting authority. Kennel EOS
                              remains the exclusive financial execution authority.
FAIL-CLOSED DECLARATION: Malformed identity, forbidden tenant, unsupported
                         channel, malformed digest, non-UTC chronology, expiry
                         contradiction, multiple terminal states, replay, schema
                         drift, and fingerprint mismatch reject.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, Mapping, Self, cast


VERSION: Final[str] = (
    "v1.0.0-L8-8H7A-LEGAL-NOTIFICATION-CONTACT-VERIFICATION"
)
SCHEMA: Final[str] = "WILSY-LEGAL-NOTIFICATION-CONTACT-VERIFICATION/V1"

_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,191}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalNotificationContactVerificationError(ValueError):
    """Stable fail-closed pure-domain error for H7A verification state.

    The code intentionally discloses no raw email address, token, principal
    credentials, tenant membership, role, delivery provider, or secret material.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalNotificationContactChannel(StrEnum):
    """Supported Legal notification contact-verification channels.

    H7A intentionally supports EMAIL only. Adding another channel requires a
    new certified authority contract rather than caller-supplied free text.
    """

    EMAIL = "EMAIL"


class LegalNotificationContactVerificationStatus(StrEnum):
    """Closed lifecycle states for one single-use verification capability."""

    ACTIVE = "ACTIVE"
    CONSUMED = "CONSUMED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "verification_version",
    "tenant_id",
    "verification_id",
    "principal_id",
    "channel",
    "address_digest",
    "token_digest",
    "issued_at",
    "expires_at",
    "consumed_at",
    "expired_at",
    "revoked_at",
    "fingerprint",
)


def _identifier(name: str, value: object) -> str:
    """Validate one bounded opaque identifier without normalizing authority."""

    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTIFIER.fullmatch(value) is None
    ):
        raise LegalNotificationContactVerificationError(
            f"L8_8H7A_{name.upper()}_INVALID"
        )
    return value


def _tenant(value: object) -> str:
    """Validate one explicit non-global tenant identifier."""

    tenant = _identifier("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        raise LegalNotificationContactVerificationError(
            "L8_8H7A_TENANT_REQUIRED"
        )
    return tenant


def _digest(name: str, value: object) -> str:
    """Validate one exact lowercase SHA3-512 digest."""

    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        raise LegalNotificationContactVerificationError(
            f"L8_8H7A_{name.upper()}_INVALID"
        )
    try:
        raw = bytes.fromhex(value)
    except ValueError as error:
        raise LegalNotificationContactVerificationError(
            f"L8_8H7A_{name.upper()}_INVALID"
        ) from error
    if len(raw) != 64:
        raise LegalNotificationContactVerificationError(
            f"L8_8H7A_{name.upper()}_INVALID"
        )
    return value


def _utc(name: str, value: object) -> datetime:
    """Require one timezone-aware instant and canonicalize to UTC."""

    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            raise LegalNotificationContactVerificationError(
                f"L8_8H7A_{name.upper()}_INVALID"
            ) from error

    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise LegalNotificationContactVerificationError(
            f"L8_8H7A_{name.upper()}_INVALID"
        )

    return parsed.astimezone(timezone.utc)


def _optional_utc(name: str, value: object) -> datetime | None:
    """Validate an optional UTC lifecycle instant."""

    if value is None:
        return None
    return _utc(name, value)


def _json_value(value: object) -> object:
    """Convert supported immutable values into deterministic JSON primitives."""

    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(
            timespec="microseconds"
        ).replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class LegalNotificationContactVerification:
    """Immutable single-use Legal notification email-control capability.

    Transaction ownership:
        None. This pure domain performs no I/O and opens no session.

    Idempotency semantics:
        None at this layer. Durable registry/service layers must define replay.

    Authority:
        ACTIVE proves only that a capability exists for one tenant/principal/
        channel/address digest. CONSUMED proves only that a later certified
        completion layer successfully consumed this capability. Neither state
        independently creates durable Legal verified-contact authority.

    Privacy:
        Raw email addresses and raw verification tokens are intentionally absent.
    """

    tenant_id: str
    verification_id: str
    principal_id: str
    channel: LegalNotificationContactChannel | str
    address_digest: str
    token_digest: str
    issued_at: datetime
    expires_at: datetime
    consumed_at: datetime | None = None
    expired_at: datetime | None = None
    revoked_at: datetime | None = None
    schema: str = SCHEMA
    verification_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate immutable capability state and deterministic integrity."""

        tenant = _tenant(self.tenant_id)
        verification_id = _identifier(
            "verification_id",
            self.verification_id,
        )
        principal_id = _identifier("principal_id", self.principal_id)

        try:
            channel = LegalNotificationContactChannel(self.channel)
        except (TypeError, ValueError) as error:
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_CHANNEL_INVALID"
            ) from error

        address_digest = _digest("address_digest", self.address_digest)
        token_digest = _digest("token_digest", self.token_digest)
        issued_at = _utc("issued_at", self.issued_at)
        expires_at = _utc("expires_at", self.expires_at)
        consumed_at = _optional_utc("consumed_at", self.consumed_at)
        expired_at = _optional_utc("expired_at", self.expired_at)
        revoked_at = _optional_utc("revoked_at", self.revoked_at)

        if self.schema != SCHEMA or self.verification_version != VERSION:
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_SCHEMA_INVALID"
            )

        if expires_at <= issued_at:
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_EXPIRY_INVALID"
            )

        terminal = tuple(
            value
            for value in (consumed_at, expired_at, revoked_at)
            if value is not None
        )
        if len(terminal) > 1:
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_TERMINAL_STATE_CONFLICT"
            )

        if consumed_at is not None and not (
            issued_at <= consumed_at < expires_at
        ):
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_CONSUMED_AT_INVALID"
            )

        if revoked_at is not None and not (
            issued_at <= revoked_at < expires_at
        ):
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_REVOKED_AT_INVALID"
            )

        if expired_at is not None and expired_at < expires_at:
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_EXPIRED_AT_INVALID"
            )

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "verification_id", verification_id)
        object.__setattr__(self, "principal_id", principal_id)
        object.__setattr__(self, "channel", channel)
        object.__setattr__(self, "address_digest", address_digest)
        object.__setattr__(self, "token_digest", token_digest)
        object.__setattr__(self, "issued_at", issued_at)
        object.__setattr__(self, "expires_at", expires_at)
        object.__setattr__(self, "consumed_at", consumed_at)
        object.__setattr__(self, "expired_at", expired_at)
        object.__setattr__(self, "revoked_at", revoked_at)

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

        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_FINGERPRINT_MISMATCH"
            )

        object.__setattr__(self, "fingerprint", digest)

    @property
    def status(self) -> LegalNotificationContactVerificationStatus:
        """Return the exact lifecycle status without consulting a clock."""

        if self.consumed_at is not None:
            return LegalNotificationContactVerificationStatus.CONSUMED
        if self.expired_at is not None:
            return LegalNotificationContactVerificationStatus.EXPIRED
        if self.revoked_at is not None:
            return LegalNotificationContactVerificationStatus.REVOKED
        return LegalNotificationContactVerificationStatus.ACTIVE

    @classmethod
    def issue(
        cls,
        *,
        tenant_id: str,
        verification_id: str,
        principal_id: str,
        channel: LegalNotificationContactChannel | str,
        address_digest: str,
        token_digest: str,
        issued_at: datetime,
        expires_at: datetime,
    ) -> "LegalNotificationContactVerification":
        """Create one ACTIVE verification from already-derived digest evidence.

        The caller must already possess certified source facts for tenant,
        principal, address digest, token digest, and chronology. This constructor
        performs no email lookup, no token generation, no persistence, and no
        delivery.
        """

        return cls(
            tenant_id=tenant_id,
            verification_id=verification_id,
            principal_id=principal_id,
            channel=channel,
            address_digest=address_digest,
            token_digest=token_digest,
            issued_at=issued_at,
            expires_at=expires_at,
        )

    def assert_usable_at(self, observed_at: datetime) -> None:
        """Require ACTIVE state and a non-expired capability at one exact instant."""

        observed = _utc("observed_at", observed_at)
        if self.status is not LegalNotificationContactVerificationStatus.ACTIVE:
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_VERIFICATION_NOT_ACTIVE"
            )
        if observed < self.issued_at:
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_VERIFICATION_NOT_YET_VALID"
            )
        if observed >= self.expires_at:
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_VERIFICATION_EXPIRED"
            )

    def consume(
        self,
        consumed_at: datetime,
    ) -> "LegalNotificationContactVerification":
        """Return immutable CONSUMED state after one valid single-use consume."""

        self.assert_usable_at(consumed_at)
        return replace(
            self,
            consumed_at=_utc("consumed_at", consumed_at),
            fingerprint="",
        )

    def revoke(
        self,
        revoked_at: datetime,
    ) -> "LegalNotificationContactVerification":
        """Return immutable REVOKED state before expiry.

        Revocation terminates future verification use. It does not revoke a
        principal, recipient binding, verified contact, delivery, credential,
        membership, role, or any other authority.
        """

        self.assert_usable_at(revoked_at)
        return replace(
            self,
            revoked_at=_utc("revoked_at", revoked_at),
            fingerprint="",
        )

    def expire(
        self,
        observed_at: datetime,
    ) -> "LegalNotificationContactVerification":
        """Return immutable EXPIRED state at or after the declared expiry."""

        observed = _utc("expired_at", observed_at)
        if self.status is not LegalNotificationContactVerificationStatus.ACTIVE:
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_VERIFICATION_NOT_ACTIVE"
            )
        if observed < self.expires_at:
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_EXPIRY_NOT_REACHED"
            )
        return replace(
            self,
            expired_at=observed,
            fingerprint="",
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize exact digest-only capability state with no raw PII/token."""

        return {
            field: _json_value(getattr(self, field))
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalNotificationContactVerification":
        """Hydrate exact schema and re-verify deterministic integrity."""

        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_SCHEMA_INVALID"
            )

        values = dict(payload)
        stored = values.pop("fingerprint")
        item = cls(**cast(Any, values))
        if (
            not isinstance(stored, str)
            or not hmac.compare_digest(stored, item.fingerprint)
        ):
            raise LegalNotificationContactVerificationError(
                "L8_8H7A_FINGERPRINT_MISMATCH"
            )
        return item


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalNotificationContactChannel",
    "LegalNotificationContactVerification",
    "LegalNotificationContactVerificationError",
    "LegalNotificationContactVerificationStatus",
]


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_notification_contact_verification.py
# VERSION: v1.0.0-L8-8H7A-LEGAL-NOTIFICATION-CONTACT-VERIFICATION
# AUTHORITY BOUNDARY: single-use Legal notification email-control verification capability only
# TENANT POSTURE: exact explicit tenant/principal binding; no cross-tenant inference
# FAIL-CLOSED POSTURE: malformed, contradictory, replayed, expired, or corrupt capability state rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
