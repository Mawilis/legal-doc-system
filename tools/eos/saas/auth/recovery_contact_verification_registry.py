"""Durable registry for recovery-contact verification challenges.

TITLE: WILSY OS Recovery Contact Verification Registry
VERSION: v1.0.0-R10E13-RECOVERY-CONTACT-VERIFICATION-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persists digest-only verification challenges and atomically transitions
         their lifecycle within exact tenant/principal/contact scope.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/recovery_contact_verification_registry.py
COLLABORATION / OWNERSHIP: recovery_contact_verification.py owns immutable state;
                           enrollment services own token generation/TTL/delivery;
                           this registry owns only collection persistence and CAS.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E13-RECOVERY-CONTACT-VERIFICATION-REGISTRY — Establishes deterministic
    indexes, strict hydration, tenant/digest lookup, active challenge listing,
    insert-only creation, and caller-session consume/expire/revoke CAS transitions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Raw challenge values are never accepted or persisted.
TENANT BOUNDARY: Every read and transition is exact tenant/principal/contact scoped.
AUTHORITY BOUNDARY: Durable challenge evidence only; no contact verification,
                    recovery issuance, password, login, or delivery authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Caller owns ClientSession and transaction lifecycle.
FAIL-CLOSED POSTURE: Duplicate, corrupt, stale, ambiguous, cross-tenant, and
                     persistence-failure states never become verification success.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Final, Mapping, NoReturn

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from .recovery_contact_verification import (
    RecoveryContactVerificationChallenge,
    RecoveryContactVerificationError,
    RecoveryContactVerificationStatus,
)


VERSION: Final[str] = "v1.0.0-R10E13-RECOVERY-CONTACT-VERIFICATION-REGISTRY"
COLLECTION: Final[str] = "recovery_contact_verification_challenges"
_ISSUED_AT_EPOCH_US: Final[str] = "_issued_at_epoch_us"
_EXPIRES_AT_EPOCH_US: Final[str] = "_expires_at_epoch_us"

INDEX_DEFINITIONS: Final[
    tuple[tuple[tuple[tuple[str, int], ...], bool, str], ...]
] = (
    ((("challenge_id", ASCENDING),), True, "recovery_contact_verification_identity_unique"),
    ((("token_digest", ASCENDING),), True, "recovery_contact_verification_digest_unique"),
    (
        (
            ("tenant_id", ASCENDING),
            ("principal_id", ASCENDING),
            ("contact_id", ASCENDING),
            ("status", ASCENDING),
            (_EXPIRES_AT_EPOCH_US, ASCENDING),
        ),
        False,
        "recovery_contact_verification_active_scope",
    ),
)


class RecoveryContactVerificationRegistryError(RuntimeError):
    """Base code-only persistence failure for verification challenges."""

    def __init__(self, code: str) -> None:
        if not isinstance(code, str) or not code:
            raise TypeError("verification registry code must be non-empty")
        self.code = code
        super().__init__(code)


class RecoveryContactVerificationNotFoundError(RecoveryContactVerificationRegistryError):
    """Challenge is absent in the supplied tenant scope."""


class RecoveryContactVerificationAlreadyExistsError(RecoveryContactVerificationRegistryError):
    """Challenge identity or digest collided during insert-only creation."""


class RecoveryContactVerificationPersistedRecordInvalidError(
    RecoveryContactVerificationRegistryError
):
    """Persisted challenge cannot be hydrated through the canonical domain."""


class RecoveryContactVerificationLifecycleConflictError(
    RecoveryContactVerificationRegistryError
):
    """Lifecycle compare-and-set lost or observed conflicting state."""


class RecoveryContactVerificationPersistenceError(RecoveryContactVerificationRegistryError):
    """Mongo operation failed at the challenge persistence boundary."""


def _target(collection: Any | None) -> Any:
    if collection is not None:
        return collection
    from tools.eos.kernel import db as kernel_db

    database = kernel_db.get_database()
    if database is None:
        raise RecoveryContactVerificationPersistenceError(
            "RECOVERY_CONTACT_VERIFICATION_DATABASE_UNAVAILABLE"
        )
    return database[COLLECTION]


def _session_kwargs(session: Any | None) -> dict[str, Any]:
    return {} if session is None else {"session": session}


def _epoch_microseconds(value: datetime) -> int:
    normalized = value.astimezone(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (normalized - epoch) // timedelta(microseconds=1)


def _document(challenge: RecoveryContactVerificationChallenge) -> dict[str, Any]:
    payload = challenge.to_document()
    payload[_ISSUED_AT_EPOCH_US] = _epoch_microseconds(challenge.issued_at)
    payload[_EXPIRES_AT_EPOCH_US] = _epoch_microseconds(challenge.expires_at)
    return payload


def _hydrate(row: Mapping[str, Any]) -> RecoveryContactVerificationChallenge:
    try:
        payload = dict(row)
        payload.pop("_id", None)
        issued_epoch = payload.pop(_ISSUED_AT_EPOCH_US)
        expires_epoch = payload.pop(_EXPIRES_AT_EPOCH_US)
        if (
            isinstance(issued_epoch, bool)
            or not isinstance(issued_epoch, int)
            or isinstance(expires_epoch, bool)
            or not isinstance(expires_epoch, int)
        ):
            raise ValueError("RECOVERY_CONTACT_VERIFICATION_TIME_METADATA_INVALID")
        challenge = RecoveryContactVerificationChallenge.from_document(payload)
        if (
            _epoch_microseconds(challenge.issued_at) != issued_epoch
            or _epoch_microseconds(challenge.expires_at) != expires_epoch
        ):
            raise ValueError("RECOVERY_CONTACT_VERIFICATION_TIME_METADATA_MISMATCH")
        return challenge
    except RecoveryContactVerificationPersistedRecordInvalidError:
        raise
    except (KeyError, TypeError, ValueError, RecoveryContactVerificationError) as error:
        raise RecoveryContactVerificationPersistedRecordInvalidError(
            "RECOVERY_CONTACT_VERIFICATION_PERSISTED_RECORD_INVALID"
        ) from error


def _identity_query(challenge: RecoveryContactVerificationChallenge) -> dict[str, Any]:
    return {
        "challenge_id": challenge.challenge_id,
        "tenant_id": challenge.tenant_id,
        "principal_id": challenge.principal_id,
        "contact_id": challenge.contact_id,
        "address": challenge.address,
        "token_digest": challenge.token_digest,
        "issued_at": challenge.issued_at.isoformat(),
        "expires_at": challenge.expires_at.isoformat(),
        "status": challenge.status.value,
        "consumed_at": None if challenge.consumed_at is None else challenge.consumed_at.isoformat(),
        "expired_at": None if challenge.expired_at is None else challenge.expired_at.isoformat(),
        "revoked_at": None if challenge.revoked_at is None else challenge.revoked_at.isoformat(),
        _ISSUED_AT_EPOCH_US: _epoch_microseconds(challenge.issued_at),
        _EXPIRES_AT_EPOCH_US: _epoch_microseconds(challenge.expires_at),
    }


def _transition_failure(
    source: Any,
    challenge: RecoveryContactVerificationChallenge,
    *,
    session: Any | None,
) -> NoReturn:
    try:
        row = source.find_one(
            {"tenant_id": challenge.tenant_id, "challenge_id": challenge.challenge_id},
            **_session_kwargs(session),
        )
    except PyMongoError as error:
        raise RecoveryContactVerificationPersistenceError(
            "RECOVERY_CONTACT_VERIFICATION_READ_FAILED"
        ) from error
    if row is None:
        raise RecoveryContactVerificationNotFoundError(
            "RECOVERY_CONTACT_VERIFICATION_NOT_FOUND"
        )
    persisted = _hydrate(row)
    if (
        persisted.principal_id != challenge.principal_id
        or persisted.contact_id != challenge.contact_id
        or persisted.address != challenge.address
        or persisted.token_digest != challenge.token_digest
        or persisted.issued_at != challenge.issued_at
        or persisted.expires_at != challenge.expires_at
    ):
        raise RecoveryContactVerificationLifecycleConflictError(
            "RECOVERY_CONTACT_VERIFICATION_BINDING_CONFLICT"
        )
    if persisted.status is RecoveryContactVerificationStatus.CONSUMED:
        raise RecoveryContactVerificationLifecycleConflictError(
            "RECOVERY_CONTACT_VERIFICATION_CONSUMED"
        )
    if persisted.status is RecoveryContactVerificationStatus.EXPIRED:
        raise RecoveryContactVerificationLifecycleConflictError(
            "RECOVERY_CONTACT_VERIFICATION_EXPIRED"
        )
    if persisted.status is RecoveryContactVerificationStatus.REVOKED:
        raise RecoveryContactVerificationLifecycleConflictError(
            "RECOVERY_CONTACT_VERIFICATION_REVOKED"
        )
    raise RecoveryContactVerificationLifecycleConflictError(
        "RECOVERY_CONTACT_VERIFICATION_LIFECYCLE_CONFLICT"
    )


class RecoveryContactVerificationRegistry:
    """Persist and atomically transition digest-only contact-verification challenges."""

    def __init__(self, collection: Any | None = None) -> None:
        self._collection = collection

    def _source(self) -> Any:
        return _target(self._collection)

    def ensure_indexes(self) -> None:
        source = self._source()
        try:
            for keys, unique, name in INDEX_DEFINITIONS:
                source.create_index(list(keys), unique=unique, name=name)
        except PyMongoError as error:
            raise RecoveryContactVerificationPersistenceError(
                "RECOVERY_CONTACT_VERIFICATION_INDEX_CREATION_FAILED"
            ) from error

    def create(
        self,
        challenge: RecoveryContactVerificationChallenge,
        *,
        session: Any | None = None,
    ) -> RecoveryContactVerificationChallenge:
        """Insert exactly one ACTIVE digest-only challenge."""

        if not isinstance(challenge, RecoveryContactVerificationChallenge):
            raise RecoveryContactVerificationRegistryError(
                "RECOVERY_CONTACT_VERIFICATION_CREATE_INVALID"
            )
        if challenge.status is not RecoveryContactVerificationStatus.ACTIVE:
            raise RecoveryContactVerificationRegistryError(
                "RECOVERY_CONTACT_VERIFICATION_CREATE_REQUIRES_ACTIVE"
            )
        source = self._source()
        try:
            source.insert_one(_document(challenge), **_session_kwargs(session))
            return challenge
        except DuplicateKeyError as error:
            try:
                identity = source.find_one(
                    {
                        "tenant_id": challenge.tenant_id,
                        "challenge_id": challenge.challenge_id,
                    },
                    **_session_kwargs(session),
                )
                digest = source.find_one(
                    {
                        "tenant_id": challenge.tenant_id,
                        "token_digest": challenge.token_digest,
                    },
                    **_session_kwargs(session),
                )
            except PyMongoError as read_error:
                raise RecoveryContactVerificationPersistenceError(
                    "RECOVERY_CONTACT_VERIFICATION_DUPLICATE_CLASSIFICATION_FAILED"
                ) from read_error
            if identity is not None:
                raise RecoveryContactVerificationAlreadyExistsError(
                    "RECOVERY_CONTACT_VERIFICATION_ID_DUPLICATE"
                ) from error
            if digest is not None:
                raise RecoveryContactVerificationAlreadyExistsError(
                    "RECOVERY_CONTACT_VERIFICATION_DIGEST_DUPLICATE"
                ) from error
            raise RecoveryContactVerificationAlreadyExistsError(
                "RECOVERY_CONTACT_VERIFICATION_DUPLICATE_CONFLICT"
            ) from error
        except PyMongoError as error:
            raise RecoveryContactVerificationPersistenceError(
                "RECOVERY_CONTACT_VERIFICATION_CREATE_FAILED"
            ) from error

    def get_by_token_digest(
        self,
        *,
        tenant_id: str,
        token_digest: str,
        session: Any | None = None,
    ) -> RecoveryContactVerificationChallenge | None:
        """Read one exact tenant/digest binding without accepting raw token material."""

        if (
            not isinstance(tenant_id, str)
            or not tenant_id.strip()
            or not isinstance(token_digest, str)
            or not token_digest.strip()
        ):
            raise RecoveryContactVerificationNotFoundError(
                "RECOVERY_CONTACT_VERIFICATION_NOT_FOUND"
            )
        try:
            row = self._source().find_one(
                {"tenant_id": tenant_id, "token_digest": token_digest},
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise RecoveryContactVerificationPersistenceError(
                "RECOVERY_CONTACT_VERIFICATION_READ_FAILED"
            ) from error
        return None if row is None else _hydrate(row)

    def list_active_for_contact(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        contact_id: str,
        session: Any | None = None,
    ) -> tuple[RecoveryContactVerificationChallenge, ...]:
        """Read ACTIVE challenges for one exact tenant/principal/contact binding."""

        if any(
            not isinstance(value, str) or not value.strip()
            for value in (tenant_id, principal_id, contact_id)
        ):
            raise RecoveryContactVerificationRegistryError(
                "RECOVERY_CONTACT_VERIFICATION_SCOPE_INVALID"
            )
        try:
            rows = list(
                self._source().find(
                    {
                        "tenant_id": tenant_id,
                        "principal_id": principal_id,
                        "contact_id": contact_id,
                        "status": RecoveryContactVerificationStatus.ACTIVE.value,
                    },
                    **_session_kwargs(session),
                )
            )
        except PyMongoError as error:
            raise RecoveryContactVerificationPersistenceError(
                "RECOVERY_CONTACT_VERIFICATION_READ_FAILED"
            ) from error
        challenges = tuple(_hydrate(row) for row in rows)
        if any(
            item.tenant_id != tenant_id
            or item.principal_id != principal_id
            or item.contact_id != contact_id
            or item.status is not RecoveryContactVerificationStatus.ACTIVE
            for item in challenges
        ):
            raise RecoveryContactVerificationPersistedRecordInvalidError(
                "RECOVERY_CONTACT_VERIFICATION_SCOPE_MISMATCH"
            )
        return challenges

    def consume(
        self,
        challenge: RecoveryContactVerificationChallenge,
        consumed_at: datetime,
        *,
        session: Any | None = None,
    ) -> RecoveryContactVerificationChallenge:
        """Atomically consume one ACTIVE challenge before expiry."""

        try:
            replacement = challenge.consume(consumed_at)
        except RecoveryContactVerificationError as error:
            raise RecoveryContactVerificationLifecycleConflictError(error.code) from error
        return self._replace(challenge, replacement, session=session)

    def expire(
        self,
        challenge: RecoveryContactVerificationChallenge,
        expired_at: datetime,
        *,
        session: Any | None = None,
    ) -> RecoveryContactVerificationChallenge:
        """Atomically expire one ACTIVE challenge at or after its boundary."""

        try:
            replacement = challenge.expire(expired_at)
        except RecoveryContactVerificationError as error:
            raise RecoveryContactVerificationLifecycleConflictError(error.code) from error
        return self._replace(challenge, replacement, session=session)

    def revoke(
        self,
        challenge: RecoveryContactVerificationChallenge,
        revoked_at: datetime,
        *,
        session: Any | None = None,
    ) -> RecoveryContactVerificationChallenge:
        """Atomically revoke one ACTIVE challenge before expiry."""

        try:
            replacement = challenge.revoke(revoked_at)
        except RecoveryContactVerificationError as error:
            raise RecoveryContactVerificationLifecycleConflictError(error.code) from error
        return self._replace(challenge, replacement, session=session)

    def _replace(
        self,
        challenge: RecoveryContactVerificationChallenge,
        replacement: RecoveryContactVerificationChallenge,
        *,
        session: Any | None,
    ) -> RecoveryContactVerificationChallenge:
        source = self._source()
        try:
            row = source.find_one_and_replace(
                _identity_query(challenge),
                _document(replacement),
                return_document=ReturnDocument.AFTER,
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise RecoveryContactVerificationPersistenceError(
                "RECOVERY_CONTACT_VERIFICATION_TRANSITION_FAILED"
            ) from error
        if row is None:
            _transition_failure(source, challenge, session=session)
        persisted = _hydrate(row)
        if persisted != replacement:
            raise RecoveryContactVerificationPersistedRecordInvalidError(
                "RECOVERY_CONTACT_VERIFICATION_READBACK_MISMATCH"
            )
        return persisted


__all__ = [
    "COLLECTION",
    "INDEX_DEFINITIONS",
    "RecoveryContactVerificationAlreadyExistsError",
    "RecoveryContactVerificationLifecycleConflictError",
    "RecoveryContactVerificationNotFoundError",
    "RecoveryContactVerificationPersistedRecordInvalidError",
    "RecoveryContactVerificationPersistenceError",
    "RecoveryContactVerificationRegistry",
    "RecoveryContactVerificationRegistryError",
    "VERSION",
]


# ARTIFACT: tools/eos/saas/auth/recovery_contact_verification_registry.py
# VERSION: v1.0.0-R10E13-RECOVERY-CONTACT-VERIFICATION-REGISTRY
# AUTHORITY BOUNDARY: durable digest-only recovery-contact verification challenge evidence
# TENANT POSTURE: exact tenant/principal/contact scope for every read and transition
# FAIL-CLOSED POSTURE: duplicate, corrupt, stale, replayed, expired, revoked, and cross-tenant state rejects
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
# END OF WILSY OS SOVEREIGN ARTIFACT
