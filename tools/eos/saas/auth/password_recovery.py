"""Immutable password-recovery capability state for the WILSY OS auth domain.

TITLE: WILSY OS Password Recovery Capability Domain
VERSION: v1.0.0-R10B1-PASSWORD-RECOVERY-DOMAIN
AUTHORITY: Wilsy OS Core Governance
EPITOME: Defines the immutable, fail-closed lifecycle value for one opaque
         password-recovery capability without admitting raw token material or
         owning any persistence, credential mutation, or transport authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery.py
COLLABORATION / OWNERSHIP: A future recovery service supplies already-digested
                           capability identity and owns issuance, persistence,
                           token delivery, and transaction orchestration.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10B1 introduces exact tenant/principal binding, SHA3-512
           digest-only state, explicit UTC lifecycle timestamps, immutable
           ACTIVE/CONSUMED/EXPIRED/REVOKED transitions, and strict hydration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Raw recovery tokens never enter, remain in, or
                            leave this domain object. Only a lowercase
                            SHA3-512 digest is admitted. Invalid or
                            contradictory state fails closed.
TENANT BOUNDARY: Exactly one caller-supplied canonical tenant_id is retained;
                 this artifact performs no alias resolution or cross-tenant
                 fallback.
AUTHORITY BOUNDARY: Domain state and deterministic lifecycle validation only;
                    no password, token, session, refresh, JWT, MFA, delivery,
                    HTTP, rate-limit, or database authority is granted.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: No Mongo client, collection, session, transaction,
                      network, environment, or wall-clock ownership exists.
FAIL-CLOSED POSTURE: Invalid identifiers, digests, timestamps, lifecycle
                     transitions, replay attempts, and contradictory terminal
                     fields raise a stable domain error.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, Mapping, Self


VERSION: Final[str] = "v1.0.0-R10B1-PASSWORD-RECOVERY-DOMAIN"
SCHEMA: Final[str] = "WILSY-PASSWORD-RECOVERY-CAPABILITY/V1"
TOKEN_DIGEST_ALGORITHM: Final[str] = "SHA3-512"
TOKEN_DIGEST_ENCODING: Final[str] = "lowercase-hex"
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(r"^[^\s\x00-\x1f\x7f]{1,256}$")
_SHA3_512: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")


class PasswordRecoveryCapabilityError(ValueError):
    """Stable fail-closed error for malformed or contradictory capability state.

    The ``code`` is deterministic and contains no token, password, tenant
    lookup, database, or transport detail. Raising this error grants no
    credential, principal, tenant, session, refresh, JWT, MFA, or financial
    authority. Transaction ownership remains with the caller.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class PasswordRecoveryCapabilityStatus(StrEnum):
    """The complete terminal lifecycle vocabulary for one capability."""

    ACTIVE = "ACTIVE"
    CONSUMED = "CONSUMED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


def _identifier(value: object, code: str) -> str:
    """Require an exact durable identifier without trimming or aliasing it."""

    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise PasswordRecoveryCapabilityError(code)
    return value


def _utc_timestamp(value: object, code: str) -> datetime:
    """Require an aware timestamp and normalize its durable representation to UTC."""

    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise PasswordRecoveryCapabilityError(code)
    try:
        return value.astimezone(timezone.utc)
    except (OverflowError, ValueError) as error:
        raise PasswordRecoveryCapabilityError(code) from error


def _optional_utc_timestamp(value: object, code: str) -> datetime | None:
    """Validate an optional terminal timestamp without reading the wall clock."""

    if value is None:
        return None
    return _utc_timestamp(value, code)


def _digest(value: object, code: str = "TOKEN_DIGEST_INVALID") -> str:
    """Require the canonical lowercase hexadecimal SHA3-512 representation."""

    if not isinstance(value, str) or _SHA3_512.fullmatch(value) is None:
        raise PasswordRecoveryCapabilityError(code)
    return value


def _parse_timestamp(value: object, code: str) -> datetime:
    """Parse one persisted timestamp and defer awareness validation to the domain."""

    if not isinstance(value, str):
        raise PasswordRecoveryCapabilityError(code)
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise PasswordRecoveryCapabilityError(code) from error


@dataclass(frozen=True, slots=True)
class PasswordRecoveryCapability:
    """Immutable state for one exact, digest-only password-recovery capability.

    The value binds one capability, canonical tenant, canonical principal,
    one-way token digest, and explicit lifecycle timestamps. ``issue`` admits
    only an already-computed digest; it never receives or hashes raw token
    material. ``consume``, ``expire``, and ``revoke`` return new values and
    never mutate this instance. A caller-owned service/transaction must decide
    how the returned value is persisted and delivered. Exact replay, missing
    persistence, and cross-tenant resolution are not interpreted here.
    """

    capability_id: str
    tenant_id: str
    principal_id: str
    token_digest: str
    issued_at: datetime
    expires_at: datetime
    status: PasswordRecoveryCapabilityStatus
    consumed_at: datetime | None = None
    expired_at: datetime | None = None
    revoked_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate every immutable field and lifecycle invariant fail-closed."""

        capability_id = _identifier(self.capability_id, "CAPABILITY_ID_INVALID")
        tenant_id = _identifier(self.tenant_id, "TENANT_ID_INVALID")
        principal_id = _identifier(self.principal_id, "PRINCIPAL_ID_INVALID")
        token_digest = _digest(self.token_digest)
        issued_at = _utc_timestamp(self.issued_at, "ISSUED_AT_INVALID")
        expires_at = _utc_timestamp(self.expires_at, "EXPIRES_AT_INVALID")
        if not isinstance(self.status, PasswordRecoveryCapabilityStatus):
            raise PasswordRecoveryCapabilityError("STATUS_INVALID")
        if expires_at <= issued_at:
            raise PasswordRecoveryCapabilityError("EXPIRY_NOT_AFTER_ISSUANCE")

        consumed_at = _optional_utc_timestamp(self.consumed_at, "CONSUMED_AT_INVALID")
        expired_at = _optional_utc_timestamp(self.expired_at, "EXPIRED_AT_INVALID")
        revoked_at = _optional_utc_timestamp(self.revoked_at, "REVOKED_AT_INVALID")
        terminal_values = (consumed_at, expired_at, revoked_at)
        if sum(value is not None for value in terminal_values) > 1:
            raise PasswordRecoveryCapabilityError("MULTIPLE_TERMINAL_TIMESTAMPS")

        for timestamp, code in (
            (consumed_at, "CONSUMED_AT_INVALID"),
            (expired_at, "EXPIRED_AT_INVALID"),
            (revoked_at, "REVOKED_AT_INVALID"),
        ):
            if timestamp is not None and timestamp < issued_at:
                raise PasswordRecoveryCapabilityError(code)

        expected_presence = {
            PasswordRecoveryCapabilityStatus.ACTIVE: (False, False, False),
            PasswordRecoveryCapabilityStatus.CONSUMED: (True, False, False),
            PasswordRecoveryCapabilityStatus.EXPIRED: (False, True, False),
            PasswordRecoveryCapabilityStatus.REVOKED: (False, False, True),
        }[self.status]
        actual_presence = tuple(value is not None for value in terminal_values)
        if actual_presence != expected_presence:
            raise PasswordRecoveryCapabilityError("STATUS_TIMESTAMP_MISMATCH")
        if consumed_at is not None and consumed_at >= expires_at:
            raise PasswordRecoveryCapabilityError("CONSUMED_AT_NOT_BEFORE_EXPIRY")
        if revoked_at is not None and revoked_at >= expires_at:
            raise PasswordRecoveryCapabilityError("REVOKED_AT_NOT_BEFORE_EXPIRY")
        if expired_at is not None and expired_at < expires_at:
            raise PasswordRecoveryCapabilityError("EXPIRED_AT_BEFORE_EXPIRY")

        object.__setattr__(self, "capability_id", capability_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "principal_id", principal_id)
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
        capability_id: str,
        tenant_id: str,
        principal_id: str,
        token_digest: str,
        issued_at: datetime,
        expires_at: datetime,
    ) -> Self:
        """Create ACTIVE state from an already-computed digest.

        This factory does not generate, receive, hash, persist, deliver, or
        authorize a raw token. The caller owns token generation, policy/TTL,
        persistence transaction, rate limiting, and all credential authority.
        """

        return cls(
            capability_id=capability_id,
            tenant_id=tenant_id,
            principal_id=principal_id,
            token_digest=token_digest,
            issued_at=issued_at,
            expires_at=expires_at,
            status=PasswordRecoveryCapabilityStatus.ACTIVE,
        )

    def assert_usable_at(self, observed_at: datetime) -> None:
        """Require ACTIVE, pre-expiry state at an explicit UTC observation time.

        No persistence absence is interpreted as lifecycle truth. Terminal
        states and the expiry boundary fail closed; the caller must handle the
        structured error within its own transaction and response boundary.
        """

        observed = _utc_timestamp(observed_at, "OBSERVED_AT_INVALID")
        if self.status is not PasswordRecoveryCapabilityStatus.ACTIVE:
            raise PasswordRecoveryCapabilityError("CAPABILITY_NOT_ACTIVE")
        if observed < self.issued_at:
            raise PasswordRecoveryCapabilityError("OBSERVED_AT_BEFORE_ISSUANCE")
        if observed >= self.expires_at:
            raise PasswordRecoveryCapabilityError("CAPABILITY_EXPIRED")

    def consume(self, consumed_at: datetime) -> Self:
        """Return one immutable CONSUMED transition before expiry.

        A second consume, terminal-state consume, and expiry-boundary consume
        are rejected as replay or unusable state. This method does not persist
        the transition, mutate a password, revoke sessions, or create JWT/MFA
        or financial authority.
        """

        observed = _utc_timestamp(consumed_at, "CONSUMED_AT_INVALID")
        self.assert_usable_at(observed)
        return replace(
            self,
            status=PasswordRecoveryCapabilityStatus.CONSUMED,
            consumed_at=observed,
        )

    def expire(self, expired_at: datetime) -> Self:
        """Return one immutable EXPIRED transition at or after the boundary."""

        observed = _utc_timestamp(expired_at, "EXPIRED_AT_INVALID")
        if self.status is not PasswordRecoveryCapabilityStatus.ACTIVE:
            raise PasswordRecoveryCapabilityError("CAPABILITY_NOT_ACTIVE")
        if observed < self.expires_at:
            raise PasswordRecoveryCapabilityError("EXPIRY_BOUNDARY_NOT_REACHED")
        return replace(
            self,
            status=PasswordRecoveryCapabilityStatus.EXPIRED,
            expired_at=observed,
        )

    def revoke(self, revoked_at: datetime) -> Self:
        """Return one immutable REVOKED transition while active and pre-expiry."""

        observed = _utc_timestamp(revoked_at, "REVOKED_AT_INVALID")
        self.assert_usable_at(observed)
        return replace(
            self,
            status=PasswordRecoveryCapabilityStatus.REVOKED,
            revoked_at=observed,
        )

    def to_document(self) -> dict[str, Any]:
        """Serialize stable primitive state without any raw-token field."""

        return {
            "schema": SCHEMA,
            "capability_id": self.capability_id,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
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
        """Hydrate exact primitive state; reject unknown or raw-token fields.

        Hydration performs no database lookup and grants no recovery, password,
        session, refresh, JWT, MFA, tenant, principal, or financial authority.
        """

        required = {
            "schema",
            "capability_id",
            "tenant_id",
            "principal_id",
            "token_digest",
            "issued_at",
            "expires_at",
            "status",
            "consumed_at",
            "expired_at",
            "revoked_at",
        }
        if not isinstance(payload, Mapping) or set(payload) != required or payload.get("schema") != SCHEMA:
            raise PasswordRecoveryCapabilityError("PERSISTED_CAPABILITY_SHAPE_INVALID")
        try:
            status = PasswordRecoveryCapabilityStatus(payload["status"])
            consumed_at = None if payload["consumed_at"] is None else _parse_timestamp(payload["consumed_at"], "CONSUMED_AT_INVALID")
            expired_at = None if payload["expired_at"] is None else _parse_timestamp(payload["expired_at"], "EXPIRED_AT_INVALID")
            revoked_at = None if payload["revoked_at"] is None else _parse_timestamp(payload["revoked_at"], "REVOKED_AT_INVALID")
            return cls(
                capability_id=payload["capability_id"],
                tenant_id=payload["tenant_id"],
                principal_id=payload["principal_id"],
                token_digest=payload["token_digest"],
                issued_at=_parse_timestamp(payload["issued_at"], "ISSUED_AT_INVALID"),
                expires_at=_parse_timestamp(payload["expires_at"], "EXPIRES_AT_INVALID"),
                status=status,
                consumed_at=consumed_at,
                expired_at=expired_at,
                revoked_at=revoked_at,
            )
        except PasswordRecoveryCapabilityError:
            raise
        except (KeyError, TypeError, ValueError) as error:
            raise PasswordRecoveryCapabilityError("PERSISTED_CAPABILITY_INVALID") from error


__all__ = [
    "PasswordRecoveryCapability",
    "PasswordRecoveryCapabilityError",
    "PasswordRecoveryCapabilityStatus",
    "SCHEMA",
    "TOKEN_DIGEST_ALGORITHM",
    "TOKEN_DIGEST_ENCODING",
    "VERSION",
]


# ARTIFACT: password_recovery.py
# VERSION: v1.0.0-R10B1-PASSWORD-RECOVERY-DOMAIN
# AUTHORITY BOUNDARY: immutable digest-only lifecycle state; no issuance or persistence authority
# TENANT POSTURE: exact canonical tenant_id and principal_id bindings; no alias or cross-tenant fallback
# FAIL-CLOSED POSTURE: malformed, replayed, expired, revoked, and contradictory state is rejected
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
