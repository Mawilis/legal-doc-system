"""Verified recovery-contact authority for WILSY OS password recovery.

TITLE: WILSY OS Verified Password Recovery Contact Domain
VERSION: v1.0.0-R10E1-VERIFIED-RECOVERY-CONTACT-DOMAIN
AUTHORITY: Wilsy OS Core Governance
EPITOME: Records one immutable, digest-only proof that an exact tenant principal
         has a previously verified recovery contact without storing the contact
         address or granting password-reset, delivery, or authentication authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery_contact.py
COLLABORATION / OWNERSHIP: A governed contact-verification/provisioning service
                           supplies an already-computed address digest; the
                           recovery-request service may consume ACTIVE contact
                           authority but cannot create verification truth.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E1-VERIFIED-RECOVERY-CONTACT-DOMAIN introduces immutable
           tenant/principal/channel/address-digest binding, explicit UTC
           verification/revocation lifecycle, strict hydration, and no raw
           recovery-address persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Recovery addresses are never stored in this domain;
                            only a lowercase SHA3-512 digest is admitted.
TENANT BOUNDARY: Every contact is bound to one exact canonical tenant_id and
                 principal_id; no alias resolution or cross-tenant fallback.
AUTHORITY BOUNDARY: Verified-contact lifecycle evidence only; no token issuance,
                    reset, password, session, JWT, MFA, HTTP, delivery, or
                    rate-limit authority is granted.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
FAIL-CLOSED POSTURE: Invalid identifiers, digests, timestamps, channels, status,
                     and contradictory lifecycle state are rejected.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, Mapping, Self

VERSION: Final[str] = "v1.0.0-R10E1-VERIFIED-RECOVERY-CONTACT-DOMAIN"
SCHEMA: Final[str] = "WILSY-VERIFIED-RECOVERY-CONTACT/V1"
ADDRESS_DIGEST_ALGORITHM: Final[str] = "SHA3-512"
ADDRESS_DIGEST_ENCODING: Final[str] = "lowercase-hex"


class VerifiedRecoveryContactError(ValueError):
    """Stable domain failure for verified recovery-contact state.

    The error code is deterministic and must not contain the address, digest,
    tenant, principal, token, password, session, or other secret material.
    """


class VerifiedRecoveryContactChannel(StrEnum):
    """Supported verified recovery-contact channels.

    EMAIL is the only admitted channel until a separately certified address
    verification authority exists for another delivery mechanism.
    """

    EMAIL = "EMAIL"


class VerifiedRecoveryContactStatus(StrEnum):
    """Durable lifecycle states for one verified recovery-contact authority."""

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


def _identifier(value: object, code: str) -> str:
    """Validate one canonical non-empty identifier without coercion."""

    if not isinstance(value, str):
        raise VerifiedRecoveryContactError(code)
    normalized = value.strip()
    if not normalized or normalized != value or len(normalized) > 256:
        raise VerifiedRecoveryContactError(code)
    if any(ord(character) < 32 or ord(character) == 127 for character in normalized):
        raise VerifiedRecoveryContactError(code)
    return normalized


def _digest(value: object) -> str:
    """Validate one exact lowercase SHA3-512 hex digest."""

    if not isinstance(value, str) or len(value) != 128:
        raise VerifiedRecoveryContactError("ADDRESS_DIGEST_INVALID")
    if value != value.lower():
        raise VerifiedRecoveryContactError("ADDRESS_DIGEST_INVALID")
    try:
        raw = bytes.fromhex(value)
    except ValueError as error:
        raise VerifiedRecoveryContactError("ADDRESS_DIGEST_INVALID") from error
    if len(raw) != 64:
        raise VerifiedRecoveryContactError("ADDRESS_DIGEST_INVALID")
    return value


def _utc_timestamp(value: object, code: str) -> datetime:
    """Require one timezone-aware UTC timestamp."""

    if not isinstance(value, datetime):
        raise VerifiedRecoveryContactError(code)
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise VerifiedRecoveryContactError(code)
    return value


def _optional_utc_timestamp(value: object, code: str) -> datetime | None:
    """Validate one optional UTC timestamp."""

    if value is None:
        return None
    return _utc_timestamp(value, code)


def _parse_timestamp(value: object, code: str) -> datetime:
    """Parse one persisted ISO-8601 timestamp and require UTC."""

    if not isinstance(value, str):
        raise VerifiedRecoveryContactError(code)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise VerifiedRecoveryContactError(code) from error
    return _utc_timestamp(parsed, code)


@dataclass(frozen=True, slots=True)
class VerifiedRecoveryContact:
    """Immutable verified recovery-contact authority.

    This value stores only the digest of a previously verified delivery address.
    Creation of ACTIVE state is therefore not address verification itself: only
    a separately governed verifier/provisioner may supply the digest. Consumers
    may use ACTIVE state as evidence that the exact address digest was verified,
    but they must independently prove the current principal address still hashes
    to the same digest before delivery.

    Transaction ownership: none.
    Idempotency: none; persistence policy belongs to the registry/provisioner.
    Financial boundary: none.
    """

    contact_id: str
    tenant_id: str
    principal_id: str
    channel: VerifiedRecoveryContactChannel
    address_digest: str
    verified_at: datetime
    status: VerifiedRecoveryContactStatus
    revoked_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate complete immutable state and reject contradictions."""

        contact_id = _identifier(self.contact_id, "CONTACT_ID_INVALID")
        tenant_id = _identifier(self.tenant_id, "TENANT_ID_INVALID")
        principal_id = _identifier(self.principal_id, "PRINCIPAL_ID_INVALID")
        if not isinstance(self.channel, VerifiedRecoveryContactChannel):
            raise VerifiedRecoveryContactError("CHANNEL_INVALID")
        address_digest = _digest(self.address_digest)
        verified_at = _utc_timestamp(self.verified_at, "VERIFIED_AT_INVALID")
        if not isinstance(self.status, VerifiedRecoveryContactStatus):
            raise VerifiedRecoveryContactError("STATUS_INVALID")
        revoked_at = _optional_utc_timestamp(self.revoked_at, "REVOKED_AT_INVALID")

        if self.status is VerifiedRecoveryContactStatus.ACTIVE and revoked_at is not None:
            raise VerifiedRecoveryContactError("STATUS_TIMESTAMP_MISMATCH")
        if self.status is VerifiedRecoveryContactStatus.REVOKED:
            if revoked_at is None:
                raise VerifiedRecoveryContactError("STATUS_TIMESTAMP_MISMATCH")
            if revoked_at < verified_at:
                raise VerifiedRecoveryContactError("REVOKED_AT_BEFORE_VERIFIED_AT")

        object.__setattr__(self, "contact_id", contact_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "principal_id", principal_id)
        object.__setattr__(self, "address_digest", address_digest)
        object.__setattr__(self, "verified_at", verified_at)
        object.__setattr__(self, "revoked_at", revoked_at)

    @classmethod
    def issue(
        cls,
        *,
        contact_id: str,
        tenant_id: str,
        principal_id: str,
        channel: VerifiedRecoveryContactChannel,
        address_digest: str,
        verified_at: datetime,
    ) -> Self:
        """Create ACTIVE verified-contact state from prior verification evidence.

        This factory does not receive, normalize, hash, verify, store, or deliver
        a recovery address. The caller must already possess certified verification
        evidence and an already-computed SHA3-512 digest.
        """

        return cls(
            contact_id=contact_id,
            tenant_id=tenant_id,
            principal_id=principal_id,
            channel=channel,
            address_digest=address_digest,
            verified_at=verified_at,
            status=VerifiedRecoveryContactStatus.ACTIVE,
        )

    def require_active(self) -> Self:
        """Return this authority only when it remains ACTIVE."""

        if self.status is not VerifiedRecoveryContactStatus.ACTIVE:
            raise VerifiedRecoveryContactError("CONTACT_NOT_ACTIVE")
        return self

    def revoke(self, revoked_at: datetime) -> Self:
        """Return one immutable REVOKED transition.

        Revocation removes future recovery-address authority but does not mutate
        the principal, password, sessions, tokens, MFA, or any delivery system.
        """

        observed = _utc_timestamp(revoked_at, "REVOKED_AT_INVALID")
        if self.status is not VerifiedRecoveryContactStatus.ACTIVE:
            raise VerifiedRecoveryContactError("CONTACT_NOT_ACTIVE")
        if observed < self.verified_at:
            raise VerifiedRecoveryContactError("REVOKED_AT_BEFORE_VERIFIED_AT")
        return replace(
            self,
            status=VerifiedRecoveryContactStatus.REVOKED,
            revoked_at=observed,
        )

    def to_document(self) -> dict[str, Any]:
        """Serialize stable primitive state without any raw recovery address."""

        return {
            "schema": SCHEMA,
            "contact_id": self.contact_id,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "channel": self.channel.value,
            "address_digest": self.address_digest,
            "verified_at": self.verified_at.isoformat(),
            "status": self.status.value,
            "revoked_at": None if self.revoked_at is None else self.revoked_at.isoformat(),
        }

    @classmethod
    def from_document(cls, payload: Mapping[str, Any]) -> Self:
        """Hydrate exact persisted state and reject unknown/raw-address fields."""

        expected = {
            "schema",
            "contact_id",
            "tenant_id",
            "principal_id",
            "channel",
            "address_digest",
            "verified_at",
            "status",
            "revoked_at",
        }
        if not isinstance(payload, Mapping) or set(payload) != expected:
            raise VerifiedRecoveryContactError("PERSISTED_CONTACT_SHAPE_INVALID")
        if payload["schema"] != SCHEMA:
            raise VerifiedRecoveryContactError("PERSISTED_CONTACT_SCHEMA_INVALID")
        try:
            return cls(
                contact_id=payload["contact_id"],
                tenant_id=payload["tenant_id"],
                principal_id=payload["principal_id"],
                channel=VerifiedRecoveryContactChannel(payload["channel"]),
                address_digest=payload["address_digest"],
                verified_at=_parse_timestamp(payload["verified_at"], "VERIFIED_AT_INVALID"),
                status=VerifiedRecoveryContactStatus(payload["status"]),
                revoked_at=(
                    None
                    if payload["revoked_at"] is None
                    else _parse_timestamp(payload["revoked_at"], "REVOKED_AT_INVALID")
                ),
            )
        except VerifiedRecoveryContactError:
            raise
        except (KeyError, TypeError, ValueError) as error:
            raise VerifiedRecoveryContactError("PERSISTED_CONTACT_INVALID") from error


__all__ = [
    "ADDRESS_DIGEST_ALGORITHM",
    "ADDRESS_DIGEST_ENCODING",
    "SCHEMA",
    "VERSION",
    "VerifiedRecoveryContact",
    "VerifiedRecoveryContactChannel",
    "VerifiedRecoveryContactError",
    "VerifiedRecoveryContactStatus",
]


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: password_recovery_contact.py
# VERSION: v1.0.0-R10E1-VERIFIED-RECOVERY-CONTACT-DOMAIN
# AUTHORITY BOUNDARY: immutable digest-only verified recovery-contact evidence
# TENANT POSTURE: exact tenant/principal binding; no alias or cross-tenant fallback
# FAIL-CLOSED POSTURE: malformed, contradictory, and revoked contact state is rejected
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
