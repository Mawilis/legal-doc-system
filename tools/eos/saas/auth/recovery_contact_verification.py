"""Immutable verification challenge state for recovery-contact enrollment.

TITLE: WILSY OS Recovery Contact Verification Challenge
VERSION: v1.0.0-R10E12-RECOVERY-CONTACT-VERIFICATION-DOMAIN
AUTHORITY: Wilsy OS Core Governance
EPITOME: Represents one digest-only, tenant/principal/contact-bound email
         possession challenge without persisting raw verification bearer material.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/recovery_contact_verification.py
COLLABORATION / OWNERSHIP: An enrollment service generates raw challenge values
                           and TTL policy; a registry persists this immutable
                           state; successful consumption may authorize the
                           separate recovery-contact VERIFIED transition.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E12-RECOVERY-CONTACT-VERIFICATION-DOMAIN — Establishes exact
    tenant/principal/contact/address binding, SHA3-512 digest-only challenge
    evidence, ACTIVE/CONSUMED/EXPIRED/REVOKED lifecycle, strict hydration, and
    immutable terminal transitions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Raw challenge values never enter durable domain state.
TENANT BOUNDARY: Every challenge binds one exact tenant_id, principal_id, and contact_id.
AUTHORITY BOUNDARY: Email-possession challenge lifecycle only; no recovery,
                    password, login, MFA, session, membership, role, or delivery authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Pure immutable domain object with no I/O.
FAIL-CLOSED POSTURE: Malformed digests, identities, addresses, timestamps,
                     contradictory lifecycle state, and replayed transitions reject.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, Mapping, Self


VERSION: Final[str] = "v1.0.0-R10E12-RECOVERY-CONTACT-VERIFICATION-DOMAIN"
SCHEMA: Final[str] = "WILSY-RECOVERY-CONTACT-VERIFICATION/V1"
TOKEN_DIGEST_LENGTH: Final[int] = 128


class RecoveryContactVerificationError(ValueError):
    """Stable code-only challenge-domain failure."""

    def __init__(self, code: str) -> None:
        if not isinstance(code, str) or not code:
            raise TypeError("verification error code must be non-empty")
        self.code = code
        super().__init__(code)

    def __repr__(self) -> str:
        return f"RecoveryContactVerificationError(code={self.code!r})"


class RecoveryContactVerificationStatus(StrEnum):
    """Lifecycle states for one verification challenge."""

    ACTIVE = "ACTIVE"
    CONSUMED = "CONSUMED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


def _identifier(value: object, code: str) -> str:
    if not isinstance(value, str):
        raise RecoveryContactVerificationError(code)
    candidate = value.strip()
    if (
        not candidate
        or candidate != value
        or len(candidate) > 256
        or any(ord(character) < 32 or ord(character) == 127 for character in candidate)
    ):
        raise RecoveryContactVerificationError(code)
    return candidate


def _email(value: object) -> str:
    if not isinstance(value, str):
        raise RecoveryContactVerificationError("RECOVERY_CONTACT_VERIFICATION_ADDRESS_INVALID")
    candidate = value.strip().lower()
    if (
        not candidate
        or len(candidate) > 320
        or candidate.count("@") != 1
        or any(character.isspace() for character in candidate)
    ):
        raise RecoveryContactVerificationError("RECOVERY_CONTACT_VERIFICATION_ADDRESS_INVALID")
    local, domain = candidate.split("@", 1)
    if not local or not domain:
        raise RecoveryContactVerificationError("RECOVERY_CONTACT_VERIFICATION_ADDRESS_INVALID")
    return candidate


def _digest(value: object) -> str:
    if not isinstance(value, str) or len(value) != TOKEN_DIGEST_LENGTH:
        raise RecoveryContactVerificationError("RECOVERY_CONTACT_VERIFICATION_DIGEST_INVALID")
    if value.lower() != value or any(character not in "0123456789abcdef" for character in value):
        raise RecoveryContactVerificationError("RECOVERY_CONTACT_VERIFICATION_DIGEST_INVALID")
    return value


def _utc(value: object, code: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise RecoveryContactVerificationError(code)
    return value.astimezone(timezone.utc)


def _optional_utc(value: object, code: str) -> datetime | None:
    if value is None:
        return None
    return _utc(value, code)


@dataclass(frozen=True, slots=True)
class RecoveryContactVerificationChallenge:
    """Immutable digest-only email-possession challenge for one recovery contact."""

    challenge_id: str
    tenant_id: str
    principal_id: str
    contact_id: str
    address: str
    token_digest: str
    issued_at: datetime
    expires_at: datetime
    status: RecoveryContactVerificationStatus
    consumed_at: datetime | None = None
    expired_at: datetime | None = None
    revoked_at: datetime | None = None

    def __post_init__(self) -> None:
        challenge_id = _identifier(
            self.challenge_id, "RECOVERY_CONTACT_VERIFICATION_ID_INVALID"
        )
        tenant_id = _identifier(
            self.tenant_id, "RECOVERY_CONTACT_VERIFICATION_TENANT_INVALID"
        )
        principal_id = _identifier(
            self.principal_id, "RECOVERY_CONTACT_VERIFICATION_PRINCIPAL_INVALID"
        )
        contact_id = _identifier(
            self.contact_id, "RECOVERY_CONTACT_VERIFICATION_CONTACT_INVALID"
        )
        address = _email(self.address)
        token_digest = _digest(self.token_digest)
        issued_at = _utc(
            self.issued_at, "RECOVERY_CONTACT_VERIFICATION_ISSUED_AT_INVALID"
        )
        expires_at = _utc(
            self.expires_at, "RECOVERY_CONTACT_VERIFICATION_EXPIRES_AT_INVALID"
        )
        consumed_at = _optional_utc(
            self.consumed_at, "RECOVERY_CONTACT_VERIFICATION_CONSUMED_AT_INVALID"
        )
        expired_at = _optional_utc(
            self.expired_at, "RECOVERY_CONTACT_VERIFICATION_EXPIRED_AT_INVALID"
        )
        revoked_at = _optional_utc(
            self.revoked_at, "RECOVERY_CONTACT_VERIFICATION_REVOKED_AT_INVALID"
        )
        if not isinstance(self.status, RecoveryContactVerificationStatus):
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_STATUS_INVALID"
            )
        if expires_at <= issued_at:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_EXPIRY_INVALID"
            )
        terminal = [value is not None for value in (consumed_at, expired_at, revoked_at)]
        if sum(terminal) > 1:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_MULTIPLE_TERMINAL_TIMESTAMPS"
            )
        for value, code in (
            (consumed_at, "RECOVERY_CONTACT_VERIFICATION_CONSUMED_BEFORE_ISSUED"),
            (expired_at, "RECOVERY_CONTACT_VERIFICATION_EXPIRED_BEFORE_ISSUED"),
            (revoked_at, "RECOVERY_CONTACT_VERIFICATION_REVOKED_BEFORE_ISSUED"),
        ):
            if value is not None and value < issued_at:
                raise RecoveryContactVerificationError(code)

        expected = {
            RecoveryContactVerificationStatus.ACTIVE: (False, False, False),
            RecoveryContactVerificationStatus.CONSUMED: (True, False, False),
            RecoveryContactVerificationStatus.EXPIRED: (False, True, False),
            RecoveryContactVerificationStatus.REVOKED: (False, False, True),
        }[self.status]
        if tuple(terminal) != expected:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_STATUS_TIMESTAMP_MISMATCH"
            )
        if consumed_at is not None and consumed_at >= expires_at:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_CONSUMED_AFTER_EXPIRY"
            )
        if revoked_at is not None and revoked_at >= expires_at:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_REVOKED_AFTER_EXPIRY"
            )
        if expired_at is not None and expired_at < expires_at:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_EXPIRED_BEFORE_BOUNDARY"
            )

        object.__setattr__(self, "challenge_id", challenge_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "principal_id", principal_id)
        object.__setattr__(self, "contact_id", contact_id)
        object.__setattr__(self, "address", address)
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
        challenge_id: str,
        tenant_id: str,
        principal_id: str,
        contact_id: str,
        address: str,
        token_digest: str,
        issued_at: datetime,
        expires_at: datetime,
    ) -> Self:
        """Create ACTIVE challenge state from an already-computed digest."""

        return cls(
            challenge_id=challenge_id,
            tenant_id=tenant_id,
            principal_id=principal_id,
            contact_id=contact_id,
            address=address,
            token_digest=token_digest,
            issued_at=issued_at,
            expires_at=expires_at,
            status=RecoveryContactVerificationStatus.ACTIVE,
        )

    def consume(self, consumed_at: datetime) -> Self:
        """Return the sole ACTIVE -> CONSUMED transition before expiry."""

        observed = _utc(
            consumed_at, "RECOVERY_CONTACT_VERIFICATION_CONSUMED_AT_INVALID"
        )
        if self.status is not RecoveryContactVerificationStatus.ACTIVE:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_NOT_ACTIVE"
            )
        if observed < self.issued_at:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_OBSERVED_BEFORE_ISSUED"
            )
        if observed >= self.expires_at:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_EXPIRED"
            )
        return replace(
            self,
            status=RecoveryContactVerificationStatus.CONSUMED,
            consumed_at=observed,
        )

    def expire(self, expired_at: datetime) -> Self:
        """Return ACTIVE -> EXPIRED at or after the expiry boundary."""

        observed = _utc(
            expired_at, "RECOVERY_CONTACT_VERIFICATION_EXPIRED_AT_INVALID"
        )
        if self.status is not RecoveryContactVerificationStatus.ACTIVE:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_NOT_ACTIVE"
            )
        if observed < self.expires_at:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_EXPIRY_BOUNDARY_NOT_REACHED"
            )
        return replace(
            self,
            status=RecoveryContactVerificationStatus.EXPIRED,
            expired_at=observed,
        )

    def revoke(self, revoked_at: datetime) -> Self:
        """Return ACTIVE -> REVOKED before expiry."""

        observed = _utc(
            revoked_at, "RECOVERY_CONTACT_VERIFICATION_REVOKED_AT_INVALID"
        )
        if self.status is not RecoveryContactVerificationStatus.ACTIVE:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_NOT_ACTIVE"
            )
        if observed < self.issued_at:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_OBSERVED_BEFORE_ISSUED"
            )
        if observed >= self.expires_at:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_EXPIRED"
            )
        return replace(
            self,
            status=RecoveryContactVerificationStatus.REVOKED,
            revoked_at=observed,
        )

    def to_document(self) -> dict[str, Any]:
        """Serialize stable primitive state without any raw challenge field."""

        return {
            "schema": SCHEMA,
            "challenge_id": self.challenge_id,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "contact_id": self.contact_id,
            "address": self.address,
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
        """Hydrate exact challenge state and reject raw-token or unknown fields."""

        expected = {
            "schema",
            "challenge_id",
            "tenant_id",
            "principal_id",
            "contact_id",
            "address",
            "token_digest",
            "issued_at",
            "expires_at",
            "status",
            "consumed_at",
            "expired_at",
            "revoked_at",
        }
        if not isinstance(payload, Mapping) or set(payload) != expected or payload.get("schema") != SCHEMA:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_DOCUMENT_SHAPE_INVALID"
            )
        try:
            return cls(
                challenge_id=payload["challenge_id"],
                tenant_id=payload["tenant_id"],
                principal_id=payload["principal_id"],
                contact_id=payload["contact_id"],
                address=payload["address"],
                token_digest=payload["token_digest"],
                issued_at=datetime.fromisoformat(payload["issued_at"]),
                expires_at=datetime.fromisoformat(payload["expires_at"]),
                status=RecoveryContactVerificationStatus(payload["status"]),
                consumed_at=(
                    None
                    if payload["consumed_at"] is None
                    else datetime.fromisoformat(payload["consumed_at"])
                ),
                expired_at=(
                    None
                    if payload["expired_at"] is None
                    else datetime.fromisoformat(payload["expired_at"])
                ),
                revoked_at=(
                    None
                    if payload["revoked_at"] is None
                    else datetime.fromisoformat(payload["revoked_at"])
                ),
            )
        except RecoveryContactVerificationError:
            raise
        except (KeyError, TypeError, ValueError) as error:
            raise RecoveryContactVerificationError(
                "RECOVERY_CONTACT_VERIFICATION_DOCUMENT_INVALID"
            ) from error


__all__ = [
    "RecoveryContactVerificationChallenge",
    "RecoveryContactVerificationError",
    "RecoveryContactVerificationStatus",
    "SCHEMA",
    "TOKEN_DIGEST_LENGTH",
    "VERSION",
]


# ARTIFACT: tools/eos/saas/auth/recovery_contact_verification.py
# VERSION: v1.0.0-R10E12-RECOVERY-CONTACT-VERIFICATION-DOMAIN
# AUTHORITY BOUNDARY: immutable digest-only recovery-contact verification challenge state
# TENANT POSTURE: exact tenant/principal/contact/address binding; no cross-tenant fallback
# FAIL-CLOSED POSTURE: malformed, replayed, expired, revoked, and contradictory challenges reject
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
# END OF WILSY OS SOVEREIGN ARTIFACT
