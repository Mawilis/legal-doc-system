"""Single-use email-control verification authority for recovery enrollment.

TITLE: WILSY OS Recovery Contact Verification Capability Domain
VERSION: v1.0.0-R10E15-RECOVERY-CONTACT-VERIFICATION-DOMAIN
AUTHORITY: Wilsy OS Core Governance
EPITOME: Represents one tenant/principal/address-bound, digest-only capability
         proving possession of a recovery-contact verification link before
         VerifiedRecoveryContact authority may be created.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery_contact_verification.py
COLLABORATION / OWNERSHIP: A verification-request service generates and delivers
                           the raw capability; a completion service consumes this
                           domain state and provisions R10E1 contact authority.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E15-RECOVERY-CONTACT-VERIFICATION-DOMAIN introduces
           tenant/principal/address/token digest binding, explicit UTC expiry,
           immutable ACTIVE/CONSUMED/EXPIRED/REVOKED lifecycle, and strict
           secret-free hydration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Raw verification links and email addresses never
                            enter domain state; only SHA3-512 digests persist.
TENANT BOUNDARY: Exactly one tenant and principal are bound to each capability.
AUTHORITY BOUNDARY: Email-control verification evidence only; no password reset,
                    contact persistence, session, JWT, MFA, HTTP, or delivery
                    authority is granted.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: malformed, replayed, expired, revoked, or contradictory
                     state is rejected.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, Mapping, Self

VERSION: Final[str] = "v1.0.0-R10E15-RECOVERY-CONTACT-VERIFICATION-DOMAIN"
SCHEMA: Final[str] = "WILSY-RECOVERY-CONTACT-VERIFICATION/V1"


class RecoveryContactVerificationError(ValueError):
    """Stable code-only domain failure for recovery-contact verification state."""


class RecoveryContactVerificationStatus(StrEnum):
    """Lifecycle states for one verification capability."""

    ACTIVE = "ACTIVE"
    CONSUMED = "CONSUMED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


def _identifier(value: object, code: str) -> str:
    if not isinstance(value, str):
        raise RecoveryContactVerificationError(code)
    normalized = value.strip()
    if not normalized or normalized != value or len(normalized) > 256:
        raise RecoveryContactVerificationError(code)
    if any(ord(character) < 32 or ord(character) == 127 for character in normalized):
        raise RecoveryContactVerificationError(code)
    return normalized


def _digest(value: object, code: str) -> str:
    if not isinstance(value, str) or len(value) != 128 or value != value.lower():
        raise RecoveryContactVerificationError(code)
    try:
        if len(bytes.fromhex(value)) != 64:
            raise ValueError
    except ValueError as error:
        raise RecoveryContactVerificationError(code) from error
    return value


def _utc(value: object, code: str) -> datetime:
    if not isinstance(value, datetime):
        raise RecoveryContactVerificationError(code)
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise RecoveryContactVerificationError(code)
    return value


def _optional_utc(value: object, code: str) -> datetime | None:
    if value is None:
        return None
    return _utc(value, code)


def _parse(value: object, code: str) -> datetime:
    if not isinstance(value, str):
        raise RecoveryContactVerificationError(code)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise RecoveryContactVerificationError(code) from error
    return _utc(parsed, code)


@dataclass(frozen=True, slots=True)
class RecoveryContactVerification:
    """Immutable single-use verification capability.

    The raw email address and raw capability are deliberately absent. A
    successful consume transition proves possession of the delivered capability
    for the exact tenant/principal/address digest represented here.
    """

    verification_id: str
    tenant_id: str
    principal_id: str
    address_digest: str
    token_digest: str
    issued_at: datetime
    expires_at: datetime
    status: RecoveryContactVerificationStatus
    consumed_at: datetime | None = None
    expired_at: datetime | None = None
    revoked_at: datetime | None = None

    def __post_init__(self) -> None:
        verification_id = _identifier(self.verification_id, "VERIFICATION_ID_INVALID")
        tenant_id = _identifier(self.tenant_id, "TENANT_ID_INVALID")
        principal_id = _identifier(self.principal_id, "PRINCIPAL_ID_INVALID")
        address_digest = _digest(self.address_digest, "ADDRESS_DIGEST_INVALID")
        token_digest = _digest(self.token_digest, "TOKEN_DIGEST_INVALID")
        issued_at = _utc(self.issued_at, "ISSUED_AT_INVALID")
        expires_at = _utc(self.expires_at, "EXPIRES_AT_INVALID")
        if expires_at <= issued_at:
            raise RecoveryContactVerificationError("EXPIRY_NOT_AFTER_ISSUANCE")
        if not isinstance(self.status, RecoveryContactVerificationStatus):
            raise RecoveryContactVerificationError("STATUS_INVALID")

        consumed_at = _optional_utc(self.consumed_at, "CONSUMED_AT_INVALID")
        expired_at = _optional_utc(self.expired_at, "EXPIRED_AT_INVALID")
        revoked_at = _optional_utc(self.revoked_at, "REVOKED_AT_INVALID")
        terminal = (consumed_at, expired_at, revoked_at)
        if sum(value is not None for value in terminal) > 1:
            raise RecoveryContactVerificationError("MULTIPLE_TERMINAL_TIMESTAMPS")

        expected = {
            RecoveryContactVerificationStatus.ACTIVE: (False, False, False),
            RecoveryContactVerificationStatus.CONSUMED: (True, False, False),
            RecoveryContactVerificationStatus.EXPIRED: (False, True, False),
            RecoveryContactVerificationStatus.REVOKED: (False, False, True),
        }[self.status]
        actual = tuple(value is not None for value in terminal)
        if actual != expected:
            raise RecoveryContactVerificationError("STATUS_TIMESTAMP_MISMATCH")

        if consumed_at is not None and not issued_at <= consumed_at < expires_at:
            raise RecoveryContactVerificationError("CONSUMED_AT_INVALID")
        if revoked_at is not None and not issued_at <= revoked_at < expires_at:
            raise RecoveryContactVerificationError("REVOKED_AT_INVALID")
        if expired_at is not None and expired_at < expires_at:
            raise RecoveryContactVerificationError("EXPIRED_AT_BEFORE_EXPIRY")

        object.__setattr__(self, "verification_id", verification_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "principal_id", principal_id)
        object.__setattr__(self, "address_digest", address_digest)
        object.__setattr__(self, "token_digest", token_digest)
        object.__setattr__(self, "issued_at", issued_at)
        object.__setattr__(self, "expires_at", expires_at)
        object.__setattr__(self, "consumed_at", consumed_at)
        object.__setattr__(self, "expired_at", expired_at)
        object.__setattr__(self, "revoked_at", revoked_at)

    @classmethod
    def issue(
        cls,
        *,
        verification_id: str,
        tenant_id: str,
        principal_id: str,
        address_digest: str,
        token_digest: str,
        issued_at: datetime,
        expires_at: datetime,
    ) -> Self:
        """Create one ACTIVE verification capability from precomputed digests."""

        return cls(
            verification_id=verification_id,
            tenant_id=tenant_id,
            principal_id=principal_id,
            address_digest=address_digest,
            token_digest=token_digest,
            issued_at=issued_at,
            expires_at=expires_at,
            status=RecoveryContactVerificationStatus.ACTIVE,
        )

    def assert_usable_at(self, observed_at: datetime) -> None:
        """Require ACTIVE state before expiry."""

        observed = _utc(observed_at, "OBSERVED_AT_INVALID")
        if self.status is not RecoveryContactVerificationStatus.ACTIVE:
            raise RecoveryContactVerificationError("VERIFICATION_NOT_ACTIVE")
        if observed < self.issued_at:
            raise RecoveryContactVerificationError("OBSERVED_AT_BEFORE_ISSUANCE")
        if observed >= self.expires_at:
            raise RecoveryContactVerificationError("VERIFICATION_EXPIRED")

    def consume(self, consumed_at: datetime) -> Self:
        """Return one immutable CONSUMED transition before expiry."""

        self.assert_usable_at(consumed_at)
        return replace(
            self,
            status=RecoveryContactVerificationStatus.CONSUMED,
            consumed_at=consumed_at,
        )

    def revoke(self, revoked_at: datetime) -> Self:
        """Return one immutable REVOKED transition before expiry."""

        self.assert_usable_at(revoked_at)
        return replace(
            self,
            status=RecoveryContactVerificationStatus.REVOKED,
            revoked_at=revoked_at,
        )

    def expire(self, expired_at: datetime) -> Self:
        """Return one immutable EXPIRED transition at/after expiry."""

        observed = _utc(expired_at, "EXPIRED_AT_INVALID")
        if self.status is not RecoveryContactVerificationStatus.ACTIVE:
            raise RecoveryContactVerificationError("VERIFICATION_NOT_ACTIVE")
        if observed < self.expires_at:
            raise RecoveryContactVerificationError("EXPIRY_BOUNDARY_NOT_REACHED")
        return replace(
            self,
            status=RecoveryContactVerificationStatus.EXPIRED,
            expired_at=observed,
        )

    def to_document(self) -> dict[str, Any]:
        """Serialize exact primitive state without raw email/token fields."""

        return {
            "schema": SCHEMA,
            "verification_id": self.verification_id,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "address_digest": self.address_digest,
            "token_digest": self.token_digest,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "status": self.status.value,
            "consumed_at": None if self.consumed_at is None else self.consumed_at.isoformat(),
            "expired_at": None if self.expired_at is None else self.expired_at.isoformat(),
            "revoked_at": None if self.revoked_at is None else self.revoked_at.isoformat(),
        }

    @classmethod
    def from_document(cls, payload: Mapping[str, Any]) -> Self:
        """Hydrate exact persisted verification state and reject extra fields."""

        expected = {
            "schema",
            "verification_id",
            "tenant_id",
            "principal_id",
            "address_digest",
            "token_digest",
            "issued_at",
            "expires_at",
            "status",
            "consumed_at",
            "expired_at",
            "revoked_at",
        }
        if not isinstance(payload, Mapping) or set(payload) != expected:
            raise RecoveryContactVerificationError("PERSISTED_VERIFICATION_SHAPE_INVALID")
        if payload["schema"] != SCHEMA:
            raise RecoveryContactVerificationError("PERSISTED_VERIFICATION_SCHEMA_INVALID")
        try:
            return cls(
                verification_id=payload["verification_id"],
                tenant_id=payload["tenant_id"],
                principal_id=payload["principal_id"],
                address_digest=payload["address_digest"],
                token_digest=payload["token_digest"],
                issued_at=_parse(payload["issued_at"], "ISSUED_AT_INVALID"),
                expires_at=_parse(payload["expires_at"], "EXPIRES_AT_INVALID"),
                status=RecoveryContactVerificationStatus(payload["status"]),
                consumed_at=None if payload["consumed_at"] is None else _parse(payload["consumed_at"], "CONSUMED_AT_INVALID"),
                expired_at=None if payload["expired_at"] is None else _parse(payload["expired_at"], "EXPIRED_AT_INVALID"),
                revoked_at=None if payload["revoked_at"] is None else _parse(payload["revoked_at"], "REVOKED_AT_INVALID"),
            )
        except RecoveryContactVerificationError:
            raise
        except (KeyError, TypeError, ValueError) as error:
            raise RecoveryContactVerificationError("PERSISTED_VERIFICATION_INVALID") from error


__all__ = [
    "RecoveryContactVerification",
    "RecoveryContactVerificationError",
    "RecoveryContactVerificationStatus",
    "SCHEMA",
    "VERSION",
]


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: password_recovery_contact_verification.py
# VERSION: v1.0.0-R10E15-RECOVERY-CONTACT-VERIFICATION-DOMAIN
# AUTHORITY BOUNDARY: single-use digest-only email-control verification evidence
# TENANT POSTURE: exact tenant/principal/address binding
# FAIL-CLOSED POSTURE: malformed, replayed, expired, revoked verification rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
