"""Proof-based migration of an existing legacy TOTP factor into global MFA.

Migration requires the exact global principal ID to match exactly one legacy
otp_secrets.user_id row, an ACTIVE principal, current global credentials with
MFA already enabled, and a valid code from that existing factor. It never
generates or resets a legacy factor and never treats password-only proof as
sufficient. The legacy row is retained for compatibility until legacy auth
cutover is independently certified.
"""
from __future__ import annotations

import hmac
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pyotp
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.global_principal_mfa_kms_envelope import GlobalMfaKeyManagementError
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_credential_repository import (
    PrincipalCredentialNotFoundError,
    PrincipalCredentialRepository,
    PrincipalCredentialRepositoryError,
)

VERSION = "v1.0.0-GLOBAL-MFA-LEGACY-FACTOR-MIGRATION"
LEGACY_FACTOR_COLLECTION = "otp_secrets"
GLOBAL_FACTOR_COLLECTION = "global_principal_mfa_factors"
TOTP_PERIOD_SECONDS = 30
TOTP_DIGITS = 6
TOTP_VALID_WINDOW = 1


class GlobalPrincipalMfaLegacyMigrationError(RuntimeError):
    """Base fail-closed legacy factor migration error."""


class GlobalPrincipalMfaLegacyMigrationRejected(GlobalPrincipalMfaLegacyMigrationError):
    """Legacy factor proof or exact principal mapping was invalid."""


class GlobalPrincipalMfaLegacyMigrationCodeRejected(GlobalPrincipalMfaLegacyMigrationRejected):
    """Invalid legacy TOTP code; caller should record the auth failure."""


class GlobalPrincipalMfaLegacyMigrationUnavailable(GlobalPrincipalMfaLegacyMigrationError):
    """Required KMS or persistence capability is unavailable."""


@dataclass(frozen=True, slots=True)
class GlobalPrincipalMfaLegacyMigrationReceipt:
    principal_id: str
    credential_revision: int
    migrated_at: datetime


def _utc(now: datetime | None) -> datetime:
    instant = now if now is not None else datetime.now(timezone.utc)
    if not isinstance(instant, datetime) or instant.tzinfo is None or instant.utcoffset() is None:
        raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_TIME_INVALID")
    return instant.astimezone(timezone.utc)


def _require_transaction(session: Any) -> None:
    marker = getattr(session, "in_transaction", None) if session is not None else None
    active = marker() if callable(marker) else marker
    if active is not True:
        raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_TRANSACTION_REQUIRED")


class GlobalPrincipalMfaLegacyMigrationService:
    """Move only an already-enrolled, actively proven legacy factor into KMS."""

    def __init__(
        self,
        *,
        kms: Any,
        legacy_factor_collection: Collection | None = None,
        factor_collection: Collection | None = None,
        credential_collection: Collection | None = None,
        credential_repository: Any = None,
        principal_repository: Any = None,
    ) -> None:
        self._kms = kms
        self._legacy = legacy_factor_collection
        self._factors = factor_collection
        self._credential_collection = credential_collection
        self._credentials = credential_repository or PrincipalCredentialRepository()
        self._principals = principal_repository or PrincipalAuthorityRepository()

    @staticmethod
    def _target(collection: Collection | None, name: str) -> Collection:
        if collection is not None:
            return collection
        from tools.eos.kernel.db import get_database
        database = get_database()
        if database is None:
            raise GlobalPrincipalMfaLegacyMigrationUnavailable("GLOBAL_MFA_MIGRATION_PERSISTENCE_UNAVAILABLE")
        return database[name]

    def migrate(
        self,
        *,
        principal_id: str,
        credential_revision: int,
        code: str,
        session: Any,
        now: datetime | None = None,
    ) -> GlobalPrincipalMfaLegacyMigrationReceipt:
        _require_transaction(session)
        instant = _utc(now)
        if not isinstance(principal_id, str) or not principal_id or principal_id != principal_id.strip():
            raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_PRINCIPAL_INVALID")
        if isinstance(credential_revision, bool) or not isinstance(credential_revision, int) or credential_revision < 0:
            raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_REVISION_INVALID")
        try:
            if self._credential_collection is None:
                credential = self._credentials.get_by_principal(principal_id, session=session)
            else:
                credential = self._credentials.get_by_principal(
                    principal_id, self._credential_collection, session=session
                )
        except PrincipalCredentialNotFoundError as error:
            raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_CREDENTIAL_REQUIRED") from error
        except PrincipalCredentialRepositoryError as error:
            raise GlobalPrincipalMfaLegacyMigrationUnavailable("GLOBAL_MFA_MIGRATION_CREDENTIAL_UNAVAILABLE") from error
        if credential.credential_revision != credential_revision:
            raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_CREDENTIAL_STALE")
        if credential.mfa_enabled not in (True, False):
            raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_MFA_STATE_INVALID")

        try:
            principal = self._principals.get(principal_id, session=session)
        except PrincipalAuthorityNotFoundError as error:
            raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_PRINCIPAL_AUTHORITY_MISSING") from error
        except PrincipalAuthorityRepositoryError as error:
            raise GlobalPrincipalMfaLegacyMigrationUnavailable("GLOBAL_MFA_MIGRATION_PRINCIPAL_AUTHORITY_UNAVAILABLE") from error
        if getattr(principal, "principal_id", None) != principal_id or getattr(principal, "status", None) is not PrincipalStatus.ACTIVE:
            raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_PRINCIPAL_NOT_ACTIVE")

        legacy = self._target(self._legacy, LEGACY_FACTOR_COLLECTION)
        factors = self._target(self._factors, GLOBAL_FACTOR_COLLECTION)
        try:
            rows = list(legacy.find({"user_id": principal_id}, session=session).limit(2))
        except PyMongoError as error:
            raise GlobalPrincipalMfaLegacyMigrationUnavailable("GLOBAL_MFA_MIGRATION_LEGACY_READ_FAILED") from error
        if len(rows) != 1:
            raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_LEGACY_FACTOR_NOT_UNIQUE")
        legacy_row = rows[0]
        secret = legacy_row.get("secret")
        if (
            legacy_row.get("user_id") != principal_id
            or not isinstance(secret, str)
            or not secret
            or "encrypted_secret" in legacy_row
        ):
            raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_LEGACY_FACTOR_INVALID")
        if not isinstance(code, str) or len(code) != TOTP_DIGITS or not code.isdigit():
            raise GlobalPrincipalMfaLegacyMigrationCodeRejected("GLOBAL_MFA_MIGRATION_CODE_INVALID")
        try:
            totp = pyotp.TOTP(secret, digits=TOTP_DIGITS, interval=TOTP_PERIOD_SECONDS)
            current_step = totp.timecode(instant)
            matching_steps = [
                step
                for step in range(max(0, current_step - TOTP_VALID_WINDOW), current_step + TOTP_VALID_WINDOW + 1)
                if hmac.compare_digest(totp.generate_otp(step), code)
            ]
        except Exception as error:
            raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_LEGACY_FACTOR_INVALID") from error
        if not matching_steps:
            raise GlobalPrincipalMfaLegacyMigrationCodeRejected("GLOBAL_MFA_MIGRATION_CODE_INVALID")
        accepted_step = max(matching_steps)

        target_revision = credential_revision
        if credential.mfa_enabled is False:
            try:
                if self._credential_collection is None:
                    enabled = self._credentials.enable_mfa(
                        principal_id, credential_revision, session=session
                    )
                else:
                    enabled = self._credentials.enable_mfa(
                        principal_id,
                        credential_revision,
                        self._credential_collection,
                        session=session,
                    )
                target_revision = enabled.credential_revision
            except PrincipalCredentialRepositoryError as error:
                raise GlobalPrincipalMfaLegacyMigrationRejected(
                    "GLOBAL_MFA_MIGRATION_CREDENTIAL_STATE_CONFLICT"
                ) from error

        try:
            envelope = self._kms.encrypt_secret(
                secret=secret,
                principal_id=principal_id,
                credential_revision=target_revision,
            )
            result = factors.update_one(
                {
                    "principal_id": principal_id,
                    "$or": [
                        {"status": {"$ne": "ACTIVE"}},
                        {"credential_revision": {"$ne": target_revision}},
                    ],
                },
                {
                    "$set": {
                        "principal_id": principal_id,
                        "credential_revision": target_revision,
                        "encrypted_secret": envelope,
                        "status": "ACTIVE",
                        "last_accepted_step": accepted_step,
                        "enrolled_at": instant,
                        "migration_source": "LEGACY_OTP_SECRET_PROOF",
                    }
                },
                upsert=True,
                session=session,
            )
            if getattr(result, "matched_count", 0) != 1 and getattr(result, "upserted_id", None) is None:
                raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_FACTOR_CONFLICT")
        except GlobalPrincipalMfaLegacyMigrationRejected:
            raise
        except DuplicateKeyError as error:
            raise GlobalPrincipalMfaLegacyMigrationRejected("GLOBAL_MFA_MIGRATION_FACTOR_ALREADY_CURRENT") from error
        except GlobalMfaKeyManagementError as error:
            raise GlobalPrincipalMfaLegacyMigrationUnavailable("GLOBAL_MFA_MIGRATION_KEY_SERVICE_UNAVAILABLE") from error
        except PyMongoError as error:
            raise GlobalPrincipalMfaLegacyMigrationUnavailable("GLOBAL_MFA_MIGRATION_FACTOR_WRITE_FAILED") from error
        return GlobalPrincipalMfaLegacyMigrationReceipt(
            principal_id=principal_id,
            credential_revision=target_revision,
            migrated_at=instant,
        )


__all__ = [
    "VERSION",
    "LEGACY_FACTOR_COLLECTION",
    "GLOBAL_FACTOR_COLLECTION",
    "GlobalPrincipalMfaLegacyMigrationError",
    "GlobalPrincipalMfaLegacyMigrationRejected",
    "GlobalPrincipalMfaLegacyMigrationCodeRejected",
    "GlobalPrincipalMfaLegacyMigrationUnavailable",
    "GlobalPrincipalMfaLegacyMigrationReceipt",
    "GlobalPrincipalMfaLegacyMigrationService",
]
