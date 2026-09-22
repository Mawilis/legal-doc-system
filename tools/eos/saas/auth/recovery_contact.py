"""Canonical recovery-contact authority for WILSY OS account recovery.

TITLE: WILSY OS Recovery Contact Authority
VERSION: v1.0.0-R10E9-RECOVERY-CONTACT-AUTHORITY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Represents one explicit, tenant/principal-bound recovery address whose
         verification lifecycle is independent from login-email existence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/recovery_contact.py
COLLABORATION / OWNERSHIP: A verification service may transition PENDING contact
                           evidence; a registry persists immutable snapshots;
                           password recovery may consume VERIFIED evidence only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E9-RECOVERY-CONTACT-AUTHORITY — Establishes explicit EMAIL recovery
    contact identity, PENDING/VERIFIED/REVOKED lifecycle, revisioned immutable
    transitions, verification-method evidence, strict hydration, and fail-closed
    eligibility without granting token, password, session, or delivery authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Recovery addresses are bounded personal information;
                            no password, bearer token, credential hash, MFA secret,
                            session, refresh token, or provider credential exists here.
TENANT BOUNDARY: Every contact binds exactly one canonical tenant_id and principal_id.
AUTHORITY BOUNDARY: Recovery-contact lifecycle evidence only; verification ceremony,
                    persistence, delivery, recovery issuance, and credential mutation
                    remain separate authorities.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Pure immutable domain object; no database or transaction access.
FAIL-CLOSED POSTURE: Malformed identifiers, unsupported channels, invalid addresses,
                     contradictory lifecycle timestamps, unknown verification methods,
                     stale revisions, and non-VERIFIED recovery use are rejected.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Final, Mapping, Self


VERSION: Final[str] = "v1.0.0-R10E9-RECOVERY-CONTACT-AUTHORITY"
SCHEMA: Final[str] = "WILSY-RECOVERY-CONTACT-AUTHORITY/V1"
MAX_IDENTIFIER_LENGTH: Final[int] = 256
MAX_EMAIL_LENGTH: Final[int] = 320


class RecoveryContactAuthorityError(ValueError):
    """Stable domain failure without retaining recovery-address or identity values."""

    def __init__(self, code: str) -> None:
        if not isinstance(code, str) or not code:
            raise TypeError("recovery contact error code must be a non-empty string")
        self.code = code
        super().__init__(code)

    def __repr__(self) -> str:
        return f"RecoveryContactAuthorityError(code={self.code!r})"


class RecoveryContactChannel(StrEnum):
    """Supported recovery delivery channels; EMAIL is the only admitted V1 channel."""

    EMAIL = "EMAIL"


class RecoveryContactStatus(StrEnum):
    """Lifecycle states for one explicit recovery contact."""

    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REVOKED = "REVOKED"


class RecoveryContactVerificationMethod(StrEnum):
    """Evidence source used to establish VERIFIED recovery-contact authority."""

    EMAIL_CHALLENGE = "EMAIL_CHALLENGE"
    LEGACY_EMAIL_VERIFIED_MIGRATION = "LEGACY_EMAIL_VERIFIED_MIGRATION"


def _identifier(value: object, code: str) -> str:
    if not isinstance(value, str):
        raise RecoveryContactAuthorityError(code)
    candidate = value.strip()
    if (
        not candidate
        or candidate != value
        or len(candidate) > MAX_IDENTIFIER_LENGTH
        or any(ord(character) < 32 or ord(character) == 127 for character in candidate)
    ):
        raise RecoveryContactAuthorityError(code)
    return candidate


def _email_address(value: object) -> str:
    if not isinstance(value, str):
        raise RecoveryContactAuthorityError("RECOVERY_CONTACT_ADDRESS_INVALID")
    candidate = value.strip().lower()
    if (
        not candidate
        or len(candidate) > MAX_EMAIL_LENGTH
        or candidate.count("@") != 1
        or any(character.isspace() for character in candidate)
        or any(ord(character) < 32 or ord(character) == 127 for character in candidate)
    ):
        raise RecoveryContactAuthorityError("RECOVERY_CONTACT_ADDRESS_INVALID")
    local, domain = candidate.split("@", 1)
    if not local or not domain or local.startswith(".") or local.endswith(".") or domain.startswith(".") or domain.endswith("."):
        raise RecoveryContactAuthorityError("RECOVERY_CONTACT_ADDRESS_INVALID")
    return candidate


def _utc_timestamp(value: object, code: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise RecoveryContactAuthorityError(code)
    return value.astimezone(timezone.utc)


def _optional_utc_timestamp(value: object, code: str) -> datetime | None:
    if value is None:
        return None
    return _utc_timestamp(value, code)


def _revision(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RecoveryContactAuthorityError("RECOVERY_CONTACT_REVISION_INVALID")
    return value


@dataclass(frozen=True, slots=True)
class RecoveryContactAuthority:
    """Immutable authority snapshot for one explicitly verified recovery contact.

    This value never infers verification from a user row, MFA registration,
    invitation, tenant membership, or account existence. Verification is an
    explicit lifecycle transition carrying a bounded verification-method value.
    """

    contact_id: str
    tenant_id: str
    principal_id: str
    channel: RecoveryContactChannel
    address: str
    status: RecoveryContactStatus
    revision: int
    created_at: datetime
    verified_at: datetime | None = None
    verification_method: RecoveryContactVerificationMethod | None = None
    revoked_at: datetime | None = None

    def __post_init__(self) -> None:
        contact_id = _identifier(self.contact_id, "RECOVERY_CONTACT_ID_INVALID")
        tenant_id = _identifier(self.tenant_id, "RECOVERY_CONTACT_TENANT_INVALID")
        principal_id = _identifier(self.principal_id, "RECOVERY_CONTACT_PRINCIPAL_INVALID")
        if not isinstance(self.channel, RecoveryContactChannel):
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_CHANNEL_INVALID")
        if self.channel is not RecoveryContactChannel.EMAIL:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_CHANNEL_UNSUPPORTED")
        address = _email_address(self.address)
        if not isinstance(self.status, RecoveryContactStatus):
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_STATUS_INVALID")
        revision = _revision(self.revision)
        created_at = _utc_timestamp(self.created_at, "RECOVERY_CONTACT_CREATED_AT_INVALID")
        verified_at = _optional_utc_timestamp(
            self.verified_at, "RECOVERY_CONTACT_VERIFIED_AT_INVALID"
        )
        revoked_at = _optional_utc_timestamp(
            self.revoked_at, "RECOVERY_CONTACT_REVOKED_AT_INVALID"
        )
        method = self.verification_method
        if method is not None and not isinstance(method, RecoveryContactVerificationMethod):
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_VERIFICATION_METHOD_INVALID")

        if verified_at is not None and verified_at < created_at:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_VERIFIED_BEFORE_CREATED")
        if revoked_at is not None and revoked_at < created_at:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_REVOKED_BEFORE_CREATED")
        if verified_at is not None and revoked_at is not None and revoked_at < verified_at:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_REVOKED_BEFORE_VERIFIED")

        if self.status is RecoveryContactStatus.PENDING:
            if verified_at is not None or method is not None or revoked_at is not None or revision != 0:
                raise RecoveryContactAuthorityError("RECOVERY_CONTACT_PENDING_STATE_INVALID")
        elif self.status is RecoveryContactStatus.VERIFIED:
            if verified_at is None or method is None or revoked_at is not None or revision < 1:
                raise RecoveryContactAuthorityError("RECOVERY_CONTACT_VERIFIED_STATE_INVALID")
        elif self.status is RecoveryContactStatus.REVOKED:
            if revoked_at is None or revision < 1:
                raise RecoveryContactAuthorityError("RECOVERY_CONTACT_REVOKED_STATE_INVALID")
            if (verified_at is None) != (method is None):
                raise RecoveryContactAuthorityError("RECOVERY_CONTACT_VERIFICATION_EVIDENCE_INVALID")

        object.__setattr__(self, "contact_id", contact_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "principal_id", principal_id)
        object.__setattr__(self, "address", address)
        object.__setattr__(self, "revision", revision)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "verified_at", verified_at)
        object.__setattr__(self, "revoked_at", revoked_at)

    @classmethod
    def pending(
        cls,
        *,
        contact_id: str,
        tenant_id: str,
        principal_id: str,
        address: str,
        created_at: datetime,
    ) -> Self:
        """Create PENDING email recovery-contact evidence with no verification authority."""

        return cls(
            contact_id=contact_id,
            tenant_id=tenant_id,
            principal_id=principal_id,
            channel=RecoveryContactChannel.EMAIL,
            address=address,
            status=RecoveryContactStatus.PENDING,
            revision=0,
            created_at=created_at,
        )

    def verify(
        self,
        *,
        verified_at: datetime,
        method: RecoveryContactVerificationMethod,
    ) -> Self:
        """Return the sole PENDING -> VERIFIED transition.

        The caller must already own and prove the verification ceremony. This
        method validates lifecycle consistency only and creates no delivery,
        token, login, membership, or credential authority.
        """

        observed = _utc_timestamp(verified_at, "RECOVERY_CONTACT_VERIFIED_AT_INVALID")
        if self.status is not RecoveryContactStatus.PENDING:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_NOT_PENDING")
        if not isinstance(method, RecoveryContactVerificationMethod):
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_VERIFICATION_METHOD_INVALID")
        if observed < self.created_at:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_VERIFIED_BEFORE_CREATED")
        return replace(
            self,
            status=RecoveryContactStatus.VERIFIED,
            revision=self.revision + 1,
            verified_at=observed,
            verification_method=method,
        )

    def revoke(self, *, revoked_at: datetime) -> Self:
        """Return one terminal REVOKED transition from PENDING or VERIFIED."""

        observed = _utc_timestamp(revoked_at, "RECOVERY_CONTACT_REVOKED_AT_INVALID")
        if self.status is RecoveryContactStatus.REVOKED:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_ALREADY_REVOKED")
        lower_bound = self.verified_at or self.created_at
        if observed < lower_bound:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_REVOKED_BEFORE_CURRENT_STATE")
        return replace(
            self,
            status=RecoveryContactStatus.REVOKED,
            revision=self.revision + 1,
            revoked_at=observed,
        )

    def require_verified(self, *, observed_at: datetime) -> Self:
        """Return self only when current contact authority is explicitly VERIFIED."""

        observed = _utc_timestamp(observed_at, "RECOVERY_CONTACT_OBSERVED_AT_INVALID")
        if observed < self.created_at:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_OBSERVED_BEFORE_CREATED")
        if self.status is not RecoveryContactStatus.VERIFIED:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_NOT_VERIFIED")
        if self.verified_at is None or self.verification_method is None:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_VERIFICATION_EVIDENCE_INVALID")
        if observed < self.verified_at:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_OBSERVED_BEFORE_VERIFICATION")
        return self

    def to_document(self) -> dict[str, Any]:
        """Serialize stable primitive state for tenant-scoped durable persistence."""

        return {
            "schema": SCHEMA,
            "contact_id": self.contact_id,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "channel": self.channel.value,
            "address": self.address,
            "status": self.status.value,
            "revision": self.revision,
            "created_at": self.created_at.isoformat(),
            "verified_at": None if self.verified_at is None else self.verified_at.isoformat(),
            "verification_method": (
                None if self.verification_method is None else self.verification_method.value
            ),
            "revoked_at": None if self.revoked_at is None else self.revoked_at.isoformat(),
        }

    @classmethod
    def from_document(cls, payload: Mapping[str, Any]) -> Self:
        """Hydrate exact persisted state while rejecting unknown or missing fields."""

        expected = {
            "schema",
            "contact_id",
            "tenant_id",
            "principal_id",
            "channel",
            "address",
            "status",
            "revision",
            "created_at",
            "verified_at",
            "verification_method",
            "revoked_at",
        }
        if not isinstance(payload, Mapping) or set(payload) != expected or payload.get("schema") != SCHEMA:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_DOCUMENT_SHAPE_INVALID")
        try:
            verified_at = payload["verified_at"]
            revoked_at = payload["revoked_at"]
            verification_method = payload["verification_method"]
            return cls(
                contact_id=payload["contact_id"],
                tenant_id=payload["tenant_id"],
                principal_id=payload["principal_id"],
                channel=RecoveryContactChannel(payload["channel"]),
                address=payload["address"],
                status=RecoveryContactStatus(payload["status"]),
                revision=payload["revision"],
                created_at=datetime.fromisoformat(payload["created_at"]),
                verified_at=None if verified_at is None else datetime.fromisoformat(verified_at),
                verification_method=(
                    None
                    if verification_method is None
                    else RecoveryContactVerificationMethod(verification_method)
                ),
                revoked_at=None if revoked_at is None else datetime.fromisoformat(revoked_at),
            )
        except RecoveryContactAuthorityError:
            raise
        except (KeyError, TypeError, ValueError) as error:
            raise RecoveryContactAuthorityError("RECOVERY_CONTACT_DOCUMENT_INVALID") from error


__all__ = [
    "MAX_EMAIL_LENGTH",
    "RecoveryContactAuthority",
    "RecoveryContactAuthorityError",
    "RecoveryContactChannel",
    "RecoveryContactStatus",
    "RecoveryContactVerificationMethod",
    "SCHEMA",
    "VERSION",
]


# ARTIFACT: tools/eos/saas/auth/recovery_contact.py
# VERSION: v1.0.0-R10E9-RECOVERY-CONTACT-AUTHORITY
# AUTHORITY BOUNDARY: immutable recovery-contact lifecycle evidence only
# TENANT POSTURE: exact tenant_id/principal_id binding; no alias or cross-tenant fallback
# FAIL-CLOSED POSTURE: only explicitly VERIFIED non-revoked contact evidence is recovery-eligible
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
# END OF WILSY OS SOVEREIGN ARTIFACT
