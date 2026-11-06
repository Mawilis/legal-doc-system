"""Global-principal TOTP verification with revision binding and replay prevention.

This verifier is tenant-neutral and intentionally separate from AuthRegistry.
Factor ciphertext is decrypted only through an injected platform key-management
capability; this module never accepts plaintext persisted secrets or owns keys.
"""
from __future__ import annotations

import hmac
from datetime import datetime, timezone
from typing import Any, Callable

import pyotp
from pymongo import ASCENDING
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from tools.eos.auth.principal_credential_repository import (
    PrincipalCredentialNotFoundError,
    PrincipalCredentialRepository,
    PrincipalCredentialRepositoryError,
)

VERSION = "v1.0.0-GLOBAL-PRINCIPAL-TOTP-VERIFIER"
COLLECTION = "global_principal_mfa_factors"
TOTP_PERIOD_SECONDS = 30
TOTP_DIGITS = 6
TOTP_VALID_WINDOW = 1


class GlobalPrincipalFactorError(RuntimeError):
    """Base fail-closed global MFA factor error."""


class GlobalPrincipalFactorRejected(GlobalPrincipalFactorError):
    """The supplied factor is invalid, stale, inactive, or already used."""


class GlobalPrincipalFactorUnavailable(GlobalPrincipalFactorError):
    """Factor persistence or platform secret decryption is unavailable."""


def _require_transaction(session: ClientSession | Any) -> None:
    marker = getattr(session, "in_transaction", None) if session is not None else None
    active = marker() if callable(marker) else marker
    if active is not True:
        raise GlobalPrincipalFactorRejected("GLOBAL_FACTOR_TRANSACTION_REQUIRED")


def _utc(now: datetime | None) -> datetime:
    instant = now if now is not None else datetime.now(timezone.utc)
    if not isinstance(instant, datetime) or instant.tzinfo is None or instant.utcoffset() is None:
        raise GlobalPrincipalFactorRejected("GLOBAL_FACTOR_TIME_INVALID")
    return instant.astimezone(timezone.utc)


class GlobalPrincipalTotpVerifier:
    """Verify one current global-principal TOTP factor and consume its time-step.

    The caller owns the transaction. A successful verification updates the
    factor's last_accepted_step in that same transaction, so the caller can
    atomically consume the MFA challenge and issue the selected global session.
    The decryptor must be backed by the platform KMS/envelope-encryption service.
    """

    def __init__(
        self,
        *,
        collection: Collection | Any = None,
        credential_repository: Any = None,
        decrypt_secret: Callable[..., str] | None = None,
    ) -> None:
        self._collection = collection
        self._credentials = credential_repository or PrincipalCredentialRepository()
        self._decrypt_secret = decrypt_secret

    @staticmethod
    def ensure_indexes(collection: Collection) -> None:
        collection.create_index(
            [("principal_id", ASCENDING)],
            unique=True,
            name="global_principal_mfa_factor_principal_unique",
        )

    def verify(
        self,
        *,
        principal_id: str,
        credential_revision: int,
        code: str,
        session: ClientSession | Any,
        now: datetime | None = None,
    ) -> bool:
        _require_transaction(session)
        instant = _utc(now)
        if (
            not isinstance(principal_id, str)
            or not principal_id
            or principal_id != principal_id.strip()
            or isinstance(credential_revision, bool)
            or not isinstance(credential_revision, int)
            or credential_revision < 0
        ):
            raise GlobalPrincipalFactorRejected("GLOBAL_FACTOR_IDENTITY_INVALID")
        if not isinstance(code, str) or len(code) != TOTP_DIGITS or not code.isdigit():
            return False
        if self._decrypt_secret is None:
            raise GlobalPrincipalFactorUnavailable("GLOBAL_FACTOR_KEY_SERVICE_UNAVAILABLE")

        try:
            credential = self._credentials.get_by_principal(principal_id, session=session)
        except PrincipalCredentialNotFoundError as error:
            raise GlobalPrincipalFactorRejected("GLOBAL_FACTOR_CREDENTIAL_REQUIRED") from error
        except PrincipalCredentialRepositoryError as error:
            raise GlobalPrincipalFactorUnavailable("GLOBAL_FACTOR_CREDENTIAL_UNAVAILABLE") from error
        if (
            credential.principal_id != principal_id
            or credential.credential_revision != credential_revision
            or credential.mfa_enabled is not True
        ):
            raise GlobalPrincipalFactorRejected("GLOBAL_FACTOR_CREDENTIAL_STALE")

        try:
            collection = self._collection
            if collection is None:
                from tools.eos.kernel.db import get_database
                database = get_database()
                if database is None:
                    raise GlobalPrincipalFactorUnavailable("GLOBAL_FACTOR_PERSISTENCE_UNAVAILABLE")
                collection = database[COLLECTION]
            rows = list(
                collection.find({"principal_id": principal_id}, session=session).limit(2)
            )
        except GlobalPrincipalFactorError:
            raise
        except PyMongoError as error:
            raise GlobalPrincipalFactorUnavailable("GLOBAL_FACTOR_READ_FAILED") from error
        if len(rows) != 1:
            raise GlobalPrincipalFactorRejected("GLOBAL_FACTOR_NOT_ENROLLED_OR_AMBIGUOUS")

        factor = rows[0]
        persisted_revision = factor.get("credential_revision")
        encrypted_secret = factor.get("encrypted_secret")
        if (
            factor.get("principal_id") != principal_id
            or factor.get("status") != "ACTIVE"
            or isinstance(persisted_revision, bool)
            or not isinstance(persisted_revision, int)
            or persisted_revision != credential_revision
            or not isinstance(encrypted_secret, (str, bytes, dict))
            or not encrypted_secret
            or "secret" in factor
        ):
            raise GlobalPrincipalFactorRejected("GLOBAL_FACTOR_ENROLLMENT_STALE")

        try:
            secret = self._decrypt_secret(
                encrypted_secret,
                principal_id=principal_id,
                credential_revision=credential_revision,
            )
            if not isinstance(secret, str) or not secret:
                raise ValueError("decrypted factor secret is invalid")
            totp = pyotp.TOTP(secret, digits=TOTP_DIGITS, interval=TOTP_PERIOD_SECONDS)
            current_step = totp.timecode(instant)
            matching_steps = [
                step
                for step in range(
                    max(0, current_step - TOTP_VALID_WINDOW),
                    current_step + TOTP_VALID_WINDOW + 1,
                )
                if hmac.compare_digest(totp.generate_otp(step), code)
            ]
        except GlobalPrincipalFactorError:
            raise
        except Exception as error:
            raise GlobalPrincipalFactorUnavailable("GLOBAL_FACTOR_DECRYPT_OR_VERIFY_FAILED") from error

        if not matching_steps:
            return False
        accepted_step = max(matching_steps)
        previous_step = factor.get("last_accepted_step")
        if previous_step is not None and (
            isinstance(previous_step, bool)
            or not isinstance(previous_step, int)
            or previous_step < 0
        ):
            raise GlobalPrincipalFactorRejected("GLOBAL_FACTOR_REPLAY_STATE_INVALID")
        replay_filter: dict[str, Any] = {
            "principal_id": principal_id,
            "status": "ACTIVE",
            "credential_revision": credential_revision,
            "last_accepted_step": {"$lt": accepted_step},
        }
        if previous_step is None:
            replay_filter = {
                "principal_id": principal_id,
                "status": "ACTIVE",
                "credential_revision": credential_revision,
                "$or": [
                    {"last_accepted_step": {"$exists": False}},
                    {"last_accepted_step": None},
                    {"last_accepted_step": {"$lt": accepted_step}},
                ],
            }
        try:
            result = collection.update_one(
                replay_filter,
                {"$set": {"last_accepted_step": accepted_step}},
                upsert=False,
                session=session,
            )
        except PyMongoError as error:
            raise GlobalPrincipalFactorUnavailable("GLOBAL_FACTOR_REPLAY_WRITE_FAILED") from error
        if getattr(result, "matched_count", 0) != 1:
            raise GlobalPrincipalFactorRejected("GLOBAL_FACTOR_REPLAYED")
        return True


__all__ = [
    "VERSION",
    "COLLECTION",
    "GlobalPrincipalFactorError",
    "GlobalPrincipalFactorRejected",
    "GlobalPrincipalFactorUnavailable",
    "GlobalPrincipalTotpVerifier",
]
