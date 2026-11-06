"""One-time, revision-bound global-principal TOTP enrollment.

Enrollment is available only when the global credential explicitly has MFA
disabled. An account with MFA enabled but a missing/stale factor is routed to
an independent recovery process; password-only re-enrollment is prohibited.
All persistence transitions participate in the caller's Mongo transaction.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

import pyotp
from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.global_principal_mfa_kms_envelope import GlobalMfaKeyManagementError
from tools.eos.auth.principal_credential_repository import (
    PrincipalCredentialMfaStateConflictError,
    PrincipalCredentialNotFoundError,
    PrincipalCredentialRepository,
    PrincipalCredentialRepositoryError,
)

VERSION = "v1.0.0-GLOBAL-PRINCIPAL-MFA-ENROLLMENT"
CHALLENGE_COLLECTION = "global_principal_mfa_enrollment_challenges"
FACTOR_COLLECTION = "global_principal_mfa_factors"
ENROLLMENT_TTL_SECONDS = 300
MAX_ENROLLMENT_CODE_ATTEMPTS = 5
TOTP_PERIOD_SECONDS = 30
TOTP_DIGITS = 6
TOTP_VALID_WINDOW = 1
PURPOSE = "GLOBAL_MFA_ENROLLMENT"


class GlobalPrincipalMfaEnrollmentError(RuntimeError):
    """Base enrollment lifecycle error."""


class GlobalPrincipalMfaEnrollmentRejected(GlobalPrincipalMfaEnrollmentError):
    """Enrollment challenge or credential state is invalid or stale."""


class GlobalPrincipalMfaEnrollmentUnavailable(GlobalPrincipalMfaEnrollmentError):
    """Required KMS or persistence capability is unavailable."""


class GlobalPrincipalMfaEnrollmentCodeRejected(GlobalPrincipalMfaEnrollmentRejected):
    """Invalid enrollment code; caller must commit the durable attempt counter."""



@dataclass(frozen=True, slots=True)
class GlobalPrincipalMfaEnrollmentReceipt:
    principal_id: str
    credential_revision: int
    expires_at: datetime
    provisioning_uri: str = field(repr=False)
    secret: str = field(repr=False)
    challenge_token: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class GlobalPrincipalMfaEnrollmentCompletion:
    principal_id: str
    credential_revision: int
    enrolled_at: datetime


def _utc(now: datetime | None) -> datetime:
    instant = now if now is not None else datetime.now(timezone.utc)
    if not isinstance(instant, datetime) or instant.tzinfo is None or instant.utcoffset() is None:
        raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_TIME_INVALID")
    return instant.astimezone(timezone.utc)


def _require_transaction(session: Any) -> None:
    marker = getattr(session, "in_transaction", None) if session is not None else None
    active = marker() if callable(marker) else marker
    if active is not True:
        raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_TRANSACTION_REQUIRED")


def _digest(token: str) -> str:
    return hashlib.sha3_512(token.encode("utf-8")).hexdigest()


def _target(collection: Collection | None, name: str) -> Collection:
    if collection is not None:
        return collection
    from tools.eos.kernel.db import get_database
    database = get_database()
    if database is None:
        raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_PERSISTENCE_UNAVAILABLE")
    return database[name]


def _matching_totp_step(secret: str, code: str, now: datetime) -> int | None:
    if not isinstance(code, str) or len(code) != TOTP_DIGITS or not code.isdigit():
        return None
    try:
        totp = pyotp.TOTP(secret, digits=TOTP_DIGITS, interval=TOTP_PERIOD_SECONDS)
        current = totp.timecode(now)
        matches = [
            step
            for step in range(max(0, current - TOTP_VALID_WINDOW), current + TOTP_VALID_WINDOW + 1)
            if hmac.compare_digest(totp.generate_otp(step), code)
        ]
        return max(matches) if matches else None
    except Exception as error:
        raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_FACTOR_INVALID") from error


class GlobalPrincipalMfaEnrollmentService:
    """Issue and confirm first-time MFA enrollment without an MFA-reset bypass."""

    def __init__(
        self,
        *,
        kms: Any,
        challenge_collection: Collection | None = None,
        factor_collection: Collection | None = None,
        legacy_factor_collection: Collection | None = None,
        credential_collection: Collection | None = None,
        credential_repository: Any = None,
    ) -> None:
        self._kms = kms
        self._challenges = challenge_collection
        self._factors = factor_collection
        self._legacy_factors = legacy_factor_collection
        self._credential_collection = credential_collection
        self._credentials = credential_repository or PrincipalCredentialRepository()

    @staticmethod
    def ensure_indexes(challenge_collection: Collection) -> None:
        challenge_collection.create_index(
            [("principal_id", ASCENDING)],
            unique=True,
            name="global_principal_mfa_enrollment_principal_unique",
        )
        challenge_collection.create_index(
            [("challenge_digest", ASCENDING)],
            unique=True,
            name="global_principal_mfa_enrollment_digest_unique",
        )
        challenge_collection.create_index(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=0,
            name="global_principal_mfa_enrollment_expiry_ttl",
        )

    def issue(
        self,
        *,
        principal_id: str,
        credential_revision: int,
        session: Any,
        now: datetime | None = None,
    ) -> GlobalPrincipalMfaEnrollmentReceipt:
        _require_transaction(session)
        instant = _utc(now)
        if not isinstance(principal_id, str) or not principal_id or principal_id != principal_id.strip():
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_PRINCIPAL_INVALID")
        if isinstance(credential_revision, bool) or not isinstance(credential_revision, int) or credential_revision < 0:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_REVISION_INVALID")
        try:
            if self._credential_collection is None:
                credential = self._credentials.get_by_principal(principal_id, session=session)
            else:
                credential = self._credentials.get_by_principal(
                    principal_id, self._credential_collection, session=session
                )
        except PrincipalCredentialNotFoundError as error:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_CREDENTIAL_REQUIRED") from error
        except PrincipalCredentialRepositoryError as error:
            raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_CREDENTIAL_UNAVAILABLE") from error
        if credential.credential_revision != credential_revision:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_CREDENTIAL_STALE")
        if credential.mfa_enabled is not False:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_RECOVERY_REQUIRED")
        legacy_factors = _target(self._legacy_factors, "otp_secrets")
        try:
            legacy_rows = list(
                legacy_factors.find({"user_id": principal_id}, session=session).limit(2)
            )
        except PyMongoError as error:
            raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_LEGACY_FACTOR_READ_FAILED") from error
        if legacy_rows:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_RECOVERY_REQUIRED")

        challenges = _target(self._challenges, CHALLENGE_COLLECTION)
        try:
            challenges.delete_many(
                {"principal_id": principal_id, "expires_at": {"$lte": instant}},
                session=session,
            )
            existing = challenges.find_one({"principal_id": principal_id}, session=session)
        except PyMongoError as error:
            raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_READ_FAILED") from error
        if existing is not None:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_ALREADY_PENDING")

        secret = pyotp.random_base32()
        try:
            envelope = self._kms.encrypt_secret(
                secret=secret,
                principal_id=principal_id,
                credential_revision=credential_revision,
            )
        except GlobalMfaKeyManagementError as error:
            raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_KEY_SERVICE_UNAVAILABLE") from error
        token = secrets.token_urlsafe(48)
        expires_at = instant + timedelta(seconds=ENROLLMENT_TTL_SECONDS)
        document = {
            "purpose": PURPOSE,
            "principal_id": principal_id,
            "credential_revision": credential_revision,
            "challenge_digest": _digest(token),
            "encrypted_secret": envelope,
            "status": "PENDING",
            "attempt_count": 0,
            "created_at": instant,
            "expires_at": expires_at,
        }
        try:
            challenges.insert_one(document, session=session)
        except DuplicateKeyError as error:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_ALREADY_PENDING") from error
        except PyMongoError as error:
            raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_WRITE_FAILED") from error
        provisioning_uri = pyotp.TOTP(secret, digits=TOTP_DIGITS, interval=TOTP_PERIOD_SECONDS).provisioning_uri(
            name=credential.normalized_email,
            issuer_name="WILSY OS",
        )
        return GlobalPrincipalMfaEnrollmentReceipt(
            principal_id=principal_id,
            credential_revision=credential_revision,
            expires_at=expires_at,
            provisioning_uri=provisioning_uri,
            secret=secret,
            challenge_token=token,
        )

    def confirm(
        self,
        *,
        challenge_token: str,
        code: str,
        session: Any,
        now: datetime | None = None,
    ) -> GlobalPrincipalMfaEnrollmentCompletion:
        _require_transaction(session)
        instant = _utc(now)
        if not isinstance(challenge_token, str) or not 40 <= len(challenge_token) <= 128:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_CHALLENGE_INVALID")
        challenges = _target(self._challenges, CHALLENGE_COLLECTION)
        factors = _target(self._factors, FACTOR_COLLECTION)
        try:
            challenge = challenges.find_one(
                {
                    "challenge_digest": _digest(challenge_token),
                    "purpose": PURPOSE,
                    "status": "PENDING",
                    "expires_at": {"$gt": instant},
                },
                session=session,
            )
        except PyMongoError as error:
            raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_READ_FAILED") from error
        if not isinstance(challenge, Mapping):
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_CHALLENGE_INVALID_EXPIRED_OR_CONSUMED")
        attempt_count = challenge.get("attempt_count", 0)
        if isinstance(attempt_count, bool) or not isinstance(attempt_count, int) or not 0 <= attempt_count < MAX_ENROLLMENT_CODE_ATTEMPTS:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_ATTEMPTS_EXHAUSTED")
        principal_id = challenge.get("principal_id")
        credential_revision = challenge.get("credential_revision")
        envelope = challenge.get("encrypted_secret")
        if (
            not isinstance(principal_id, str)
            or not principal_id
            or isinstance(credential_revision, bool)
            or not isinstance(credential_revision, int)
            or credential_revision < 0
            or not isinstance(envelope, Mapping)
        ):
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_CHALLENGE_CORRUPT")
        try:
            if self._credential_collection is None:
                credential = self._credentials.get_by_principal(principal_id, session=session)
            else:
                credential = self._credentials.get_by_principal(
                    principal_id, self._credential_collection, session=session
                )
        except PrincipalCredentialNotFoundError as error:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_CREDENTIAL_REQUIRED") from error
        except PrincipalCredentialRepositoryError as error:
            raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_CREDENTIAL_UNAVAILABLE") from error
        if credential.credential_revision != credential_revision:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_CREDENTIAL_STALE")
        if credential.mfa_enabled is not False:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_RECOVERY_REQUIRED")
        try:
            secret = self._kms.decrypt_secret(
                envelope,
                principal_id=principal_id,
                credential_revision=credential_revision,
            )
        except GlobalMfaKeyManagementError as error:
            raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_KEY_SERVICE_UNAVAILABLE") from error
        if not isinstance(secret, str) or not secret:
            raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_SECRET_UNAVAILABLE")
        accepted_step = _matching_totp_step(secret, code, instant)
        if accepted_step is None:
            update_fields: dict[str, Any] = {"last_failed_at": instant}
            if attempt_count + 1 >= MAX_ENROLLMENT_CODE_ATTEMPTS:
                update_fields.update({"status": "LOCKED", "locked_at": instant})
            try:
                attempted = challenges.update_one(
                    {
                        "_id": challenge.get("_id"),
                        "challenge_digest": _digest(challenge_token),
                        "status": "PENDING",
                        "attempt_count": attempt_count,
                    },
                    {"$inc": {"attempt_count": 1}, "$set": update_fields},
                    upsert=False,
                    session=session,
                )
            except PyMongoError as error:
                raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_ATTEMPT_WRITE_FAILED") from error
            if getattr(attempted, "matched_count", 0) != 1:
                raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_ATTEMPT_STATE_CONFLICT")
            raise GlobalPrincipalMfaEnrollmentCodeRejected("GLOBAL_MFA_ENROLLMENT_CODE_INVALID")

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
        except PrincipalCredentialMfaStateConflictError as error:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_CREDENTIAL_STATE_CONFLICT") from error
        except PrincipalCredentialRepositoryError as error:
            raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_CREDENTIAL_UPDATE_FAILED") from error
        try:
            active_envelope = self._kms.encrypt_secret(
                secret=secret,
                principal_id=principal_id,
                credential_revision=enabled.credential_revision,
            )
            factor_result = factors.update_one(
                {
                    "principal_id": principal_id,
                    "status": {"$ne": "ACTIVE"},
                },
                {
                    "$set": {
                        "principal_id": principal_id,
                        "credential_revision": enabled.credential_revision,
                        "encrypted_secret": active_envelope,
                        "status": "ACTIVE",
                        "last_accepted_step": accepted_step,
                        "enrolled_at": instant,
                    }
                },
                upsert=True,
                session=session,
            )
            if getattr(factor_result, "matched_count", 0) != 1 and getattr(factor_result, "upserted_id", None) is None:
                raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_FACTOR_CONFLICT")
            deleted = challenges.delete_one(
                {
                    "_id": challenge.get("_id"),
                    "challenge_digest": _digest(challenge_token),
                    "status": "PENDING",
                },
                session=session,
            )
            if getattr(deleted, "deleted_count", 0) != 1:
                raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_CHALLENGE_CONSUMPTION_FAILED")
        except GlobalPrincipalMfaEnrollmentError:
            raise
        except DuplicateKeyError as error:
            raise GlobalPrincipalMfaEnrollmentRejected("GLOBAL_MFA_ENROLLMENT_FACTOR_CONFLICT") from error
        except GlobalMfaKeyManagementError as error:
            raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_KEY_SERVICE_UNAVAILABLE") from error
        except PyMongoError as error:
            raise GlobalPrincipalMfaEnrollmentUnavailable("GLOBAL_MFA_ENROLLMENT_PERSISTENCE_FAILED") from error
        return GlobalPrincipalMfaEnrollmentCompletion(
            principal_id=principal_id,
            credential_revision=enabled.credential_revision,
            enrolled_at=instant,
        )


__all__ = [
    "VERSION",
    "CHALLENGE_COLLECTION",
    "FACTOR_COLLECTION",
    "GlobalPrincipalMfaEnrollmentError",
    "GlobalPrincipalMfaEnrollmentRejected",
    "GlobalPrincipalMfaEnrollmentUnavailable",
    "GlobalPrincipalMfaEnrollmentCodeRejected",
    "GlobalPrincipalMfaEnrollmentReceipt",
    "GlobalPrincipalMfaEnrollmentCompletion",
    "GlobalPrincipalMfaEnrollmentService",
]
