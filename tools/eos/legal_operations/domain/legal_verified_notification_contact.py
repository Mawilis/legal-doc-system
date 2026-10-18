"""WILSY OS verified Legal notification-contact authority domain.

TITLE: Verified Legal Notification Contact
VERSION: v1.0.0-L8-8H7B-VERIFIED-LEGAL-NOTIFICATION-CONTACT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Represent one immutable tenant/principal/channel/address-digest Legal
         notification-contact authority established only from exact consumed
         H7A verification evidence, without storing raw contact material or
         granting recipient-selection, dispatch, delivery, Court, AI, or
         financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_verified_notification_contact.py
COLLABORATION / OWNERSHIP: H7B owns verified Legal notification-contact
                           authority only. H7A owns email-control verification
                           capability meaning. Upstream Auth owns current
                           principal/email source truth. Recipient binding owns
                           recipient selection. Later orchestration must re-prove
                           current principal/address truth before dispatch.
                           Password-recovery contact authority is purpose-bound
                           and MUST NOT be imported, aliased, or reused here.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0-L8-8H7B-VERIFIED-LEGAL-NOTIFICATION-CONTACT establishes
           immutable ACTIVE/REVOKED Legal notification-contact authority for
           EMAIL only, bound to exact tenant, principal, address digest,
           verification identity/fingerprint, verification-consumed instant,
           verification expiry, verified instant, optional revocation, schema,
           and deterministic SHA3-512 integrity. Raw address/token material,
           transport, dispatch, delivery, recipient selection, Court, AI,
           billing, payment, execution, and settlement authority remain absent.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Durable state is digest-only. Raw email addresses,
                            raw verification tokens, credentials, provider
                            identifiers, message bodies, and delivery outcomes
                            are never represented. Authority is rejected if its
                            H7A provenance is not consumed, internally
                            inconsistent, expired before consumption, or corrupt.
TENANT BOUNDARY: Every contact is bound to one explicit non-global tenant_id and
                 one exact principal_id. No tenant inference or cross-tenant
                 fallback is permitted.
AUTHORITY BOUNDARY: Verified Legal notification-contact authority only.
                    ACTIVE means the exact address digest was proven through one
                    consumed H7A verification for the exact tenant/principal.
                    It does not select a recipient and does not itself authorize
                    dispatch or prove delivery. Address/current-principal drift
                    must be revalidated by later orchestration.
FINANCIAL AUTHORITY BOUNDARY: None. No invoice, payment, release, execution,
                              settlement, or accounting authority. Kennel EOS
                              remains the exclusive financial execution authority.
FAIL-CLOSED DECLARATION: Malformed identity, forbidden tenant, unsupported
                         channel, malformed digest/fingerprint, non-UTC
                         chronology, unconsumed verification provenance,
                         verification chronology contradiction, revocation
                         contradiction, schema drift, and fingerprint mismatch
                         reject.
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

from tools.eos.legal_operations.domain.legal_notification_contact_verification import (
    LegalNotificationContactChannel,
    LegalNotificationContactVerification,
    LegalNotificationContactVerificationStatus,
)


VERSION: Final[str] = "v1.0.0-L8-8H7B-VERIFIED-LEGAL-NOTIFICATION-CONTACT"
SCHEMA: Final[str] = "WILSY-VERIFIED-LEGAL-NOTIFICATION-CONTACT/V1"

_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,191}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class VerifiedLegalNotificationContactError(ValueError):
    """Stable fail-closed pure-domain error for H7B contact authority."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class VerifiedLegalNotificationContactStatus(StrEnum):
    """Closed lifecycle for verified Legal notification-contact authority."""

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "contact_version",
    "tenant_id",
    "contact_id",
    "principal_id",
    "channel",
    "address_digest",
    "verification_id",
    "verification_fingerprint",
    "verification_consumed_at",
    "verification_expires_at",
    "verified_at",
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
        raise VerifiedLegalNotificationContactError(
            f"L8_8H7B_{name.upper()}_INVALID"
        )
    return value


def _tenant(value: object) -> str:
    """Validate one explicit non-global tenant identifier."""

    tenant = _identifier("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        raise VerifiedLegalNotificationContactError(
            "L8_8H7B_TENANT_REQUIRED"
        )
    return tenant


def _digest(name: str, value: object) -> str:
    """Validate one exact lowercase SHA3-512 digest/fingerprint."""

    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        raise VerifiedLegalNotificationContactError(
            f"L8_8H7B_{name.upper()}_INVALID"
        )
    try:
        raw = bytes.fromhex(value)
    except ValueError as error:
        raise VerifiedLegalNotificationContactError(
            f"L8_8H7B_{name.upper()}_INVALID"
        ) from error
    if len(raw) != 64:
        raise VerifiedLegalNotificationContactError(
            f"L8_8H7B_{name.upper()}_INVALID"
        )
    return value


def _utc(name: str, value: object) -> datetime:
    """Require one timezone-aware instant and canonicalize it to UTC."""

    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            raise VerifiedLegalNotificationContactError(
                f"L8_8H7B_{name.upper()}_INVALID"
            ) from error

    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise VerifiedLegalNotificationContactError(
            f"L8_8H7B_{name.upper()}_INVALID"
        )
    return parsed.astimezone(timezone.utc)


def _optional_utc(name: str, value: object) -> datetime | None:
    """Validate one optional lifecycle instant."""

    if value is None:
        return None
    return _utc(name, value)


def _json_value(value: object) -> object:
    """Convert immutable values into deterministic JSON primitives."""

    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(
            timespec="microseconds"
        ).replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class VerifiedLegalNotificationContact:
    """Immutable verified Legal notification-contact authority.

    Transaction ownership:
        None. This pure domain performs no I/O and opens no session.

    Creation authority:
        `from_consumed_verification` requires one exact H7A verification already
        in CONSUMED state. No caller may directly elevate an ACTIVE H7A
        capability into verified-contact authority.

    Dispatch boundary:
        ACTIVE contact authority proves prior control of one address digest only.
        Later dispatch orchestration must independently re-prove current
        principal/address correspondence and recipient selection.
    """

    tenant_id: str
    contact_id: str
    principal_id: str
    channel: LegalNotificationContactChannel | str
    address_digest: str
    verification_id: str
    verification_fingerprint: str
    verification_consumed_at: datetime
    verification_expires_at: datetime
    verified_at: datetime
    revoked_at: datetime | None = None
    schema: str = SCHEMA
    contact_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate provenance, chronology, lifecycle, and deterministic integrity."""

        tenant = _tenant(self.tenant_id)
        contact_id = _identifier("contact_id", self.contact_id)
        principal_id = _identifier("principal_id", self.principal_id)

        try:
            channel = LegalNotificationContactChannel(self.channel)
        except (TypeError, ValueError) as error:
            raise VerifiedLegalNotificationContactError(
                "L8_8H7B_CHANNEL_INVALID"
            ) from error

        address_digest = _digest("address_digest", self.address_digest)
        verification_id = _identifier(
            "verification_id",
            self.verification_id,
        )
        verification_fingerprint = _digest(
            "verification_fingerprint",
            self.verification_fingerprint,
        )
        verification_consumed_at = _utc(
            "verification_consumed_at",
            self.verification_consumed_at,
        )
        verification_expires_at = _utc(
            "verification_expires_at",
            self.verification_expires_at,
        )
        verified_at = _utc("verified_at", self.verified_at)
        revoked_at = _optional_utc("revoked_at", self.revoked_at)

        if self.schema != SCHEMA or self.contact_version != VERSION:
            raise VerifiedLegalNotificationContactError(
                "L8_8H7B_SCHEMA_INVALID"
            )

        if verification_consumed_at >= verification_expires_at:
            raise VerifiedLegalNotificationContactError(
                "L8_8H7B_VERIFICATION_CHRONOLOGY_INVALID"
            )

        if verified_at < verification_consumed_at:
            raise VerifiedLegalNotificationContactError(
                "L8_8H7B_VERIFIED_AT_INVALID"
            )

        if revoked_at is not None and revoked_at < verified_at:
            raise VerifiedLegalNotificationContactError(
                "L8_8H7B_REVOKED_AT_INVALID"
            )

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "contact_id", contact_id)
        object.__setattr__(self, "principal_id", principal_id)
        object.__setattr__(self, "channel", channel)
        object.__setattr__(self, "address_digest", address_digest)
        object.__setattr__(self, "verification_id", verification_id)
        object.__setattr__(
            self,
            "verification_fingerprint",
            verification_fingerprint,
        )
        object.__setattr__(
            self,
            "verification_consumed_at",
            verification_consumed_at,
        )
        object.__setattr__(
            self,
            "verification_expires_at",
            verification_expires_at,
        )
        object.__setattr__(self, "verified_at", verified_at)
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
            raise VerifiedLegalNotificationContactError(
                "L8_8H7B_FINGERPRINT_MISMATCH"
            )

        object.__setattr__(self, "fingerprint", digest)

    @property
    def status(self) -> VerifiedLegalNotificationContactStatus:
        """Return exact lifecycle status without consulting external state."""

        if self.revoked_at is not None:
            return VerifiedLegalNotificationContactStatus.REVOKED
        return VerifiedLegalNotificationContactStatus.ACTIVE

    @classmethod
    def from_consumed_verification(
        cls,
        *,
        contact_id: str,
        verification: LegalNotificationContactVerification,
        verified_at: datetime,
    ) -> "VerifiedLegalNotificationContact":
        """Create ACTIVE authority from one exact consumed H7A verification.

        This is the only certified elevation path in H7B. The source H7A value
        must already be CONSUMED and therefore contain one immutable consumed_at
        instant and one integrity fingerprint covering its tenant, principal,
        channel, address digest, capability identity, and chronology.
        """

        if not isinstance(
            verification,
            LegalNotificationContactVerification,
        ):
            raise VerifiedLegalNotificationContactError(
                "L8_8H7B_VERIFICATION_REQUIRED"
            )

        if (
            verification.status
            is not LegalNotificationContactVerificationStatus.CONSUMED
            or verification.consumed_at is None
        ):
            raise VerifiedLegalNotificationContactError(
                "L8_8H7B_VERIFICATION_NOT_CONSUMED"
            )

        return cls(
            tenant_id=verification.tenant_id,
            contact_id=contact_id,
            principal_id=verification.principal_id,
            channel=verification.channel,
            address_digest=verification.address_digest,
            verification_id=verification.verification_id,
            verification_fingerprint=verification.fingerprint,
            verification_consumed_at=verification.consumed_at,
            verification_expires_at=verification.expires_at,
            verified_at=verified_at,
        )

    def revoke(
        self,
        revoked_at: datetime,
    ) -> "VerifiedLegalNotificationContact":
        """Return immutable REVOKED authority.

        Revocation terminates future Legal notification-contact authority only.
        It does not mutate the principal, recipient binding, H7A verification,
        credential, membership, role, dispatch, delivery, or financial state.
        """

        if self.status is not VerifiedLegalNotificationContactStatus.ACTIVE:
            raise VerifiedLegalNotificationContactError(
                "L8_8H7B_CONTACT_NOT_ACTIVE"
            )

        observed = _utc("revoked_at", revoked_at)
        if observed < self.verified_at:
            raise VerifiedLegalNotificationContactError(
                "L8_8H7B_REVOKED_AT_INVALID"
            )

        return replace(
            self,
            revoked_at=observed,
            fingerprint="",
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize exact digest-only authority state with no raw contact data."""

        return {
            field: _json_value(getattr(self, field))
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "VerifiedLegalNotificationContact":
        """Hydrate exact schema and re-verify deterministic integrity."""

        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise VerifiedLegalNotificationContactError(
                "L8_8H7B_SCHEMA_INVALID"
            )

        values = dict(payload)
        stored = values.pop("fingerprint")
        item = cls(**cast(Any, values))

        if (
            not isinstance(stored, str)
            or not hmac.compare_digest(stored, item.fingerprint)
        ):
            raise VerifiedLegalNotificationContactError(
                "L8_8H7B_FINGERPRINT_MISMATCH"
            )

        return item


__all__ = [
    "SCHEMA",
    "VERSION",
    "VerifiedLegalNotificationContact",
    "VerifiedLegalNotificationContactError",
    "VerifiedLegalNotificationContactStatus",
]


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_verified_notification_contact.py
# VERSION: v1.0.0-L8-8H7B-VERIFIED-LEGAL-NOTIFICATION-CONTACT
# AUTHORITY BOUNDARY: verified Legal notification-contact authority only; no recipient selection, dispatch, or delivery
# TENANT POSTURE: exact tenant/principal/address-digest authority with no cross-tenant inference
# FAIL-CLOSED POSTURE: unconsumed provenance, malformed, contradictory, revoked, or corrupt authority rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
