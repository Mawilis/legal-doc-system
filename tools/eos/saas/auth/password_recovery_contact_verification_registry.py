"""Durable registry for WILSY OS recovery-contact verification capabilities.

TITLE: WILSY OS Recovery Contact Verification Registry
VERSION: v1.0.0-R10E16-RECOVERY-CONTACT-VERIFICATION-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persists and atomically transitions one tenant/principal/address-bound,
         digest-only email-control verification capability through R10E15.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery_contact_verification_registry.py
COLLABORATION / OWNERSHIP: Verification-request and completion services supply
                           R10E15 values and caller-owned sessions. This registry
                           owns persistence, hydration, indexes, and lifecycle CAS.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E16-RECOVERY-CONTACT-VERIFICATION-REGISTRY establishes the
           recovery_contact_verifications collection, deterministic identity and
           token-digest uniqueness, tenant/principal/status/expiry indexing,
           strict hydration, exact digest lookup, insert-only creation, and
           caller-session consume/revoke/expire transitions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Raw email addresses and raw verification tokens are
                            never accepted, logged, or persisted.
TENANT BOUNDARY: Every lookup and lifecycle transition is bound to exact tenant
                 evidence carried by the R10E15 capability.
AUTHORITY BOUNDARY: Durable email-control verification evidence only; no contact
                    authority creation, password reset, delivery, session, JWT,
                    MFA, or HTTP authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: The caller owns ClientSession and transaction lifecycle;
                      this registry never starts, commits, aborts, or retries one.
FAIL-CLOSED POSTURE: Duplicate, absent, corrupt, replayed, expired, revoked, and
                     divergent persisted state is rejected explicitly.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Final, Mapping, NoReturn

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from .password_recovery_contact_verification import (
    RecoveryContactVerification,
    RecoveryContactVerificationError,
    RecoveryContactVerificationStatus,
)

VERSION: Final[str] = "v1.0.0-R10E16-RECOVERY-CONTACT-VERIFICATION-REGISTRY"
COLLECTION: Final[str] = "recovery_contact_verifications"
_ISSUED_AT_EPOCH_US: Final[str] = "_issued_at_epoch_us"
_EXPIRES_AT_EPOCH_US: Final[str] = "_expires_at_epoch_us"

INDEX_DEFINITIONS: Final[
    tuple[tuple[tuple[tuple[str, int], ...], bool, str], ...]
] = (
    ((("verification_id", ASCENDING),), True, "recovery_contact_verification_identity_unique"),
    ((("token_digest", ASCENDING),), True, "recovery_contact_verification_token_unique"),
    (
        (
            ("tenant_id", ASCENDING),
            ("principal_id", ASCENDING),
            ("status", ASCENDING),
            (_EXPIRES_AT_EPOCH_US, ASCENDING),
        ),
        False,
        "recovery_contact_verification_tenant_principal_status_expiry",
    ),
)


class RecoveryContactVerificationRegistryError(RuntimeError):
    """Base stable failure for verification persistence boundaries."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class RecoveryContactVerificationNotFoundError(RecoveryContactVerificationRegistryError):
    """The requested verification is absent inside the supplied tenant scope."""


class RecoveryContactVerificationAlreadyExistsError(RecoveryContactVerificationRegistryError):
    """Insert-only creation collided with an existing identity or token digest."""


class RecoveryContactVerificationPersistedRecordInvalidError(
    RecoveryContactVerificationRegistryError
):
    """Persisted verification evidence cannot hydrate through R10E15."""


class RecoveryContactVerificationLifecycleConflictError(
    RecoveryContactVerificationRegistryError
):
    """Atomic lifecycle compare-and-set found replay, expiry, or divergence."""


class RecoveryContactVerificationPersistenceError(RecoveryContactVerificationRegistryError):
    """Canonical verification persistence could not complete an operation."""


def _target(collection: Any | None) -> Any:
    """Resolve injected collection or canonical Kernel database lazily."""

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
    """Forward exactly one caller-owned session when supplied."""

    return {} if session is None else {"session": session}


def _epoch_microseconds(value: datetime) -> int:
    """Return deterministic UTC epoch microseconds without reading the clock."""

    normalized = value.astimezone(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (normalized - epoch) // timedelta(microseconds=1)


def _document(verification: RecoveryContactVerification) -> dict[str, Any]:
    """Persist exact R10E15 serialization plus query-only time metadata."""

    payload = verification.to_document()
    payload[_ISSUED_AT_EPOCH_US] = _epoch_microseconds(verification.issued_at)
    payload[_EXPIRES_AT_EPOCH_US] = _epoch_microseconds(verification.expires_at)
    return payload


def _hydrate(row: Mapping[str, Any]) -> RecoveryContactVerification:
    """Hydrate only through R10E15 and reject divergent metadata."""

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
        verification = RecoveryContactVerification.from_document(payload)
        if (
            _epoch_microseconds(verification.issued_at) != issued_epoch
            or _epoch_microseconds(verification.expires_at) != expires_epoch
        ):
            raise ValueError("RECOVERY_CONTACT_VERIFICATION_TIME_METADATA_MISMATCH")
        return verification
    except RecoveryContactVerificationPersistedRecordInvalidError:
        raise
    except (KeyError, TypeError, ValueError, RecoveryContactVerificationError) as error:
        raise RecoveryContactVerificationPersistedRecordInvalidError(
            "RECOVERY_CONTACT_VERIFICATION_PERSISTED_RECORD_INVALID"
        ) from error


def _identity_query(
    verification: RecoveryContactVerification,
) -> dict[str, Any]:
    """Build exact ACTIVE verification binding for lifecycle CAS."""

    return {
        "tenant_id": verification.tenant_id,
        "verification_id": verification.verification_id,
        "principal_id": verification.principal_id,
        "address_digest": verification.address_digest,
        "token_digest": verification.token_digest,
        "issued_at": verification.issued_at.isoformat(),
        "expires_at": verification.expires_at.isoformat(),
        "status": RecoveryContactVerificationStatus.ACTIVE.value,
        "consumed_at": None,
        "expired_at": None,
        "revoked_at": None,
        _ISSUED_AT_EPOCH_US: _epoch_microseconds(verification.issued_at),
        _EXPIRES_AT_EPOCH_US: _epoch_microseconds(verification.expires_at),
    }


def _transition_failure(
    source: Any,
    verification: RecoveryContactVerification,
    observed_at: datetime,
    *,
    session: Any | None,
    operation: str,
) -> NoReturn:
    """Classify failed lifecycle CAS without broadening tenant scope."""

    try:
        current = source.find_one(
            {
                "tenant_id": verification.tenant_id,
                "verification_id": verification.verification_id,
            },
            **_session_kwargs(session),
        )
    except PyMongoError as error:
        raise RecoveryContactVerificationPersistenceError(
            "RECOVERY_CONTACT_VERIFICATION_READ_FAILED"
        ) from error

    if current is None:
        raise RecoveryContactVerificationNotFoundError(
            "RECOVERY_CONTACT_VERIFICATION_NOT_FOUND"
        )

    persisted = _hydrate(current)
    if (
        persisted.principal_id != verification.principal_id
        or persisted.address_digest != verification.address_digest
        or persisted.token_digest != verification.token_digest
        or persisted.issued_at != verification.issued_at
        or persisted.expires_at != verification.expires_at
    ):
        raise RecoveryContactVerificationLifecycleConflictError(
            "RECOVERY_CONTACT_VERIFICATION_BINDING_CONFLICT"
        )

    if persisted.status is RecoveryContactVerificationStatus.CONSUMED:
        raise RecoveryContactVerificationLifecycleConflictError(
            "RECOVERY_CONTACT_VERIFICATION_CONSUMED"
        )
    if persisted.status is RecoveryContactVerificationStatus.REVOKED:
        raise RecoveryContactVerificationLifecycleConflictError(
            "RECOVERY_CONTACT_VERIFICATION_REVOKED"
        )
    if persisted.status is RecoveryContactVerificationStatus.EXPIRED:
        raise RecoveryContactVerificationLifecycleConflictError(
            "RECOVERY_CONTACT_VERIFICATION_EXPIRED"
        )
    if operation in {"consume", "revoke"} and observed_at >= persisted.expires_at:
        raise RecoveryContactVerificationLifecycleConflictError(
            "RECOVERY_CONTACT_VERIFICATION_EXPIRED"
        )
    if operation == "expire" and observed_at < persisted.expires_at:
        raise RecoveryContactVerificationLifecycleConflictError(
            "RECOVERY_CONTACT_VERIFICATION_EXPIRY_BOUNDARY_NOT_REACHED"
        )
    raise RecoveryContactVerificationLifecycleConflictError(
        "RECOVERY_CONTACT_VERIFICATION_LIFECYCLE_CONFLICT"
    )


class RecoveryContactVerificationRegistry:
    """Persist and atomically transition R10E15 verification capabilities."""

    def __init__(self, collection: Any | None = None) -> None:
        """Bind one optional collection dependency without opening Mongo."""

        self._collection = collection

    def _source(self) -> Any:
        """Return injected or canonical collection at operation time."""

        return _target(self._collection)

    def ensure_indexes(self) -> None:
        """Create stable uniqueness/query indexes outside transactions."""

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
        verification: RecoveryContactVerification,
        *,
        session: Any | None = None,
    ) -> RecoveryContactVerification:
        """Insert exactly one ACTIVE verification capability."""

        if not isinstance(verification, RecoveryContactVerification):
            raise RecoveryContactVerificationRegistryError(
                "RECOVERY_CONTACT_VERIFICATION_CREATE_INVALID"
            )
        if verification.status is not RecoveryContactVerificationStatus.ACTIVE:
            raise RecoveryContactVerificationRegistryError(
                "RECOVERY_CONTACT_VERIFICATION_CREATE_REQUIRES_ACTIVE"
            )

        source = self._source()
        try:
            source.insert_one(_document(verification), **_session_kwargs(session))
            return verification
        except DuplicateKeyError as error:
            try:
                identity = source.find_one(
                    {
                        "tenant_id": verification.tenant_id,
                        "verification_id": verification.verification_id,
                    },
                    **_session_kwargs(session),
                )
                digest = source.find_one(
                    {
                        "tenant_id": verification.tenant_id,
                        "token_digest": verification.token_digest,
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
                    "RECOVERY_CONTACT_VERIFICATION_TOKEN_DUPLICATE"
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
    ) -> RecoveryContactVerification | None:
        """Read one exact tenant/token-digest verification binding."""

        if (
            not isinstance(tenant_id, str)
            or not tenant_id.strip()
            or tenant_id != tenant_id.strip()
            or not isinstance(token_digest, str)
            or len(token_digest) != 128
            or token_digest != token_digest.lower()
        ):
            raise RecoveryContactVerificationNotFoundError(
                "RECOVERY_CONTACT_VERIFICATION_NOT_FOUND"
            )
        try:
            if len(bytes.fromhex(token_digest)) != 64:
                raise ValueError
        except ValueError as error:
            raise RecoveryContactVerificationNotFoundError(
                "RECOVERY_CONTACT_VERIFICATION_NOT_FOUND"
            ) from error

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

    def _transition(
        self,
        verification: RecoveryContactVerification,
        observed_at: datetime,
        *,
        operation: str,
        replacement: RecoveryContactVerification,
        session: Any | None,
    ) -> RecoveryContactVerification:
        """Execute one exact ACTIVE lifecycle compare-and-set."""

        source = self._source()
        query = _identity_query(verification)
        observed_epoch = _epoch_microseconds(observed_at.astimezone(timezone.utc))
        if operation == "expire":
            query[_EXPIRES_AT_EPOCH_US] = {"$lte": observed_epoch}
        else:
            query[_EXPIRES_AT_EPOCH_US] = {"$gt": observed_epoch}

        replacement_payload = replacement.to_document()
        terminal_field = {
            "consume": "consumed_at",
            "revoke": "revoked_at",
            "expire": "expired_at",
        }[operation]
        try:
            row = source.find_one_and_update(
                query,
                {
                    "$set": {
                        "status": replacement_payload["status"],
                        terminal_field: replacement_payload[terminal_field],
                    }
                },
                return_document=ReturnDocument.AFTER,
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise RecoveryContactVerificationPersistenceError(
                "RECOVERY_CONTACT_VERIFICATION_TRANSITION_FAILED"
            ) from error

        if row is None:
            _transition_failure(
                source,
                verification,
                observed_at,
                session=session,
                operation=operation,
            )
        return _hydrate(row)

    def consume(
        self,
        verification: RecoveryContactVerification,
        consumed_at: datetime,
        *,
        session: Any | None = None,
    ) -> RecoveryContactVerification:
        """Atomically consume one ACTIVE verification before expiry."""

        if not isinstance(verification, RecoveryContactVerification):
            raise RecoveryContactVerificationRegistryError(
                "RECOVERY_CONTACT_VERIFICATION_CONSUME_INVALID"
            )
        return self._transition(
            verification,
            consumed_at,
            operation="consume",
            replacement=verification.consume(consumed_at),
            session=session,
        )

    def revoke(
        self,
        verification: RecoveryContactVerification,
        revoked_at: datetime,
        *,
        session: Any | None = None,
    ) -> RecoveryContactVerification:
        """Atomically revoke one ACTIVE verification before expiry."""

        if not isinstance(verification, RecoveryContactVerification):
            raise RecoveryContactVerificationRegistryError(
                "RECOVERY_CONTACT_VERIFICATION_REVOKE_INVALID"
            )
        return self._transition(
            verification,
            revoked_at,
            operation="revoke",
            replacement=verification.revoke(revoked_at),
            session=session,
        )

    def expire(
        self,
        verification: RecoveryContactVerification,
        expired_at: datetime,
        *,
        session: Any | None = None,
    ) -> RecoveryContactVerification:
        """Atomically expire one ACTIVE verification at/after expiry."""

        if not isinstance(verification, RecoveryContactVerification):
            raise RecoveryContactVerificationRegistryError(
                "RECOVERY_CONTACT_VERIFICATION_EXPIRE_INVALID"
            )
        return self._transition(
            verification,
            expired_at,
            operation="expire",
            replacement=verification.expire(expired_at),
            session=session,
        )


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


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: password_recovery_contact_verification_registry.py
# VERSION: v1.0.0-R10E16-RECOVERY-CONTACT-VERIFICATION-REGISTRY
# AUTHORITY BOUNDARY: durable digest-only email-control verification evidence
# TENANT POSTURE: exact tenant/principal/token binding; no cross-tenant fallback
# FAIL-CLOSED POSTURE: duplicate, replayed, expired, revoked, corrupt state rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
