"""Durable registry for immutable WILSY OS password-recovery capabilities.

TITLE: WILSY OS Password Recovery Capability Registry
VERSION: v1.1.0-R10E2-ACTIVE-PRINCIPAL-RECOVERY-QUERY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persists and atomically transitions one tenant-scoped,
         digest-only password-recovery capability through the certified
         R10B1 domain contract. This registry owns durable capability truth,
         not password or authentication authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery_registry.py
COLLABORATION / OWNERSHIP: A later recovery service supplies policy-approved
                           R10B1 values and a caller-owned Mongo session;
                           this registry owns only collection persistence,
                           hydration, indexes, and lifecycle CAS.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.1.0-R10E2-ACTIVE-PRINCIPAL-RECOVERY-QUERY adds an exact
           tenant/principal ACTIVE-capability read seam for issuance services;
           it strictly hydrates every matching row, forwards caller sessions,
           and owns no lifecycle transition, issuance policy, token material,
           delivery, credential, or transaction authority.
           v1.0.0-R10B2 establishes the canonical
           password_recovery_capabilities collection contract, deterministic
           uniqueness/query indexes, strict domain hydration, tenant-scoped
           reads, insert-only creation, and caller-session CAS transitions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Raw recovery tokens, passwords, hashes, JWTs,
                            bearer sessions, refresh tokens, MFA secrets,
                            and delivery secrets are never accepted or logged.
TENANT BOUNDARY: Every public lookup and lifecycle mutation requires the
                 exact tenant binding carried by the R10B1 capability; no
                 alias inference or cross-tenant fallback exists.
AUTHORITY BOUNDARY: Durable recovery-capability state only. Password hashing
                    or mutation, token generation, TTL selection, session or
                    refresh revocation, JWT, MFA, delivery, HTTP, rate-limit,
                    membership, and role authority remain outside this file.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: The caller owns ClientSession and transaction lifecycle;
                      this registry never starts, commits, aborts, or retries
                      a transaction.
FAIL-CLOSED POSTURE: Duplicate, absent, corrupt, divergent, stale, expired,
                     revoked, and persistence-failure states are classified
                     as errors rather than inferred as success or absence.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Final, Mapping, NoReturn

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from .password_recovery import (
    PasswordRecoveryCapability,
    PasswordRecoveryCapabilityError,
    PasswordRecoveryCapabilityStatus,
)


VERSION: Final[str] = "v1.1.0-R10E2-ACTIVE-PRINCIPAL-RECOVERY-QUERY"
COLLECTION: Final[str] = "password_recovery_capabilities"
_ISSUED_AT_EPOCH_US: Final[str] = "_issued_at_epoch_us"
_EXPIRES_AT_EPOCH_US: Final[str] = "_expires_at_epoch_us"

# (keys, unique, stable index name). The expiry field is numeric metadata,
# justified because R10B1's ISO serialization permits variable fractional
# precision and therefore is not safe for lexicographic temporal comparison.
INDEX_DEFINITIONS: Final[
    tuple[tuple[tuple[tuple[str, int], ...], bool, str], ...]
] = (
    ((("capability_id", ASCENDING),), True, "password_recovery_capability_identity_unique"),
    ((("token_digest", ASCENDING),), True, "password_recovery_token_digest_unique"),
    (
        (
            ("tenant_id", ASCENDING),
            ("principal_id", ASCENDING),
            ("status", ASCENDING),
            (_EXPIRES_AT_EPOCH_US, ASCENDING),
        ),
        False,
        "password_recovery_tenant_principal_status_expiry",
    ),
)


class PasswordRecoveryCapabilityRegistryError(RuntimeError):
    """Base stable failure for recovery-capability persistence boundaries."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class PasswordRecoveryCapabilityNotFoundError(PasswordRecoveryCapabilityRegistryError):
    """The requested capability is absent within the supplied tenant scope."""


class PasswordRecoveryCapabilityAlreadyExistsError(PasswordRecoveryCapabilityRegistryError):
    """Creation collided with an existing identity or digest and is not replay."""


class PasswordRecoveryCapabilityPersistedRecordInvalidError(PasswordRecoveryCapabilityRegistryError):
    """A matching durable row cannot be hydrated through the R10B1 domain."""


class PasswordRecoveryCapabilityLifecycleConflictError(PasswordRecoveryCapabilityRegistryError):
    """An atomic lifecycle compare-and-set lost or found conflicting state."""


class PasswordRecoveryCapabilityPersistenceError(PasswordRecoveryCapabilityRegistryError):
    """The canonical collection could not complete a requested operation."""


def _target(collection: Any | None) -> Any:
    """Resolve an injected collection or the canonical Kernel database lazily."""

    if collection is not None:
        return collection
    from tools.eos.kernel import db as kernel_db

    database = kernel_db.get_database()
    if database is None:
        raise PasswordRecoveryCapabilityPersistenceError("RECOVERY_DATABASE_UNAVAILABLE")
    return database[COLLECTION]


def _session_kwargs(session: Any | None) -> dict[str, Any]:
    """Forward exactly the caller session when supplied; never create one."""

    return {} if session is None else {"session": session}


def _epoch_microseconds(value: datetime) -> int:
    """Return deterministic UTC epoch microseconds without reading the clock."""

    normalized = value.astimezone(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (normalized - epoch) // timedelta(microseconds=1)


def _document(capability: PasswordRecoveryCapability) -> dict[str, Any]:
    """Persist the exact R10B1 serialization plus query-only time metadata."""

    payload = capability.to_document()
    payload[_ISSUED_AT_EPOCH_US] = _epoch_microseconds(capability.issued_at)
    payload[_EXPIRES_AT_EPOCH_US] = _epoch_microseconds(capability.expires_at)
    return payload


def _hydrate(row: Mapping[str, Any]) -> PasswordRecoveryCapability:
    """Hydrate only through R10B1 and reject missing or divergent metadata."""

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
            raise ValueError("RECOVERY_TIME_METADATA_INVALID")
        capability = PasswordRecoveryCapability.from_document(payload)
        if (
            _epoch_microseconds(capability.issued_at) != issued_epoch
            or _epoch_microseconds(capability.expires_at) != expires_epoch
        ):
            raise ValueError("RECOVERY_TIME_METADATA_MISMATCH")
        return capability
    except PasswordRecoveryCapabilityPersistedRecordInvalidError:
        raise
    except (KeyError, TypeError, ValueError, PasswordRecoveryCapabilityError) as error:
        raise PasswordRecoveryCapabilityPersistedRecordInvalidError(
            "RECOVERY_PERSISTED_RECORD_INVALID"
        ) from error


def _identity_query(capability: PasswordRecoveryCapability) -> dict[str, Any]:
    """Build the complete tenant, principal, digest, and immutable-time binding."""

    return {
        "tenant_id": capability.tenant_id,
        "capability_id": capability.capability_id,
        "principal_id": capability.principal_id,
        "token_digest": capability.token_digest,
        "issued_at": capability.issued_at.isoformat(),
        "expires_at": capability.expires_at.isoformat(),
        "status": PasswordRecoveryCapabilityStatus.ACTIVE.value,
        "consumed_at": None,
        "expired_at": None,
        "revoked_at": None,
        _ISSUED_AT_EPOCH_US: _epoch_microseconds(capability.issued_at),
        _EXPIRES_AT_EPOCH_US: _epoch_microseconds(capability.expires_at),
    }


def _transition_failure(
    source: Any,
    capability: PasswordRecoveryCapability,
    observed_at: datetime,
    *,
    session: Any | None,
    operation: str,
) -> NoReturn:
    """Classify a failed CAS without disclosing cross-tenant state."""

    try:
        current = source.find_one(
            {"tenant_id": capability.tenant_id, "capability_id": capability.capability_id},
            **_session_kwargs(session),
        )
    except PyMongoError as error:
        raise PasswordRecoveryCapabilityPersistenceError("RECOVERY_READ_FAILED") from error
    if current is None:
        raise PasswordRecoveryCapabilityNotFoundError("RECOVERY_CAPABILITY_NOT_FOUND")
    persisted = _hydrate(current)
    if (
        persisted.principal_id != capability.principal_id
        or persisted.token_digest != capability.token_digest
        or persisted.issued_at != capability.issued_at
        or persisted.expires_at != capability.expires_at
    ):
        raise PasswordRecoveryCapabilityLifecycleConflictError(
            "RECOVERY_CAPABILITY_BINDING_CONFLICT"
        )
    if persisted.status is PasswordRecoveryCapabilityStatus.CONSUMED:
        raise PasswordRecoveryCapabilityLifecycleConflictError("RECOVERY_CAPABILITY_CONSUMED")
    if persisted.status is PasswordRecoveryCapabilityStatus.REVOKED:
        raise PasswordRecoveryCapabilityLifecycleConflictError("RECOVERY_CAPABILITY_REVOKED")
    if persisted.status is PasswordRecoveryCapabilityStatus.EXPIRED:
        raise PasswordRecoveryCapabilityLifecycleConflictError("RECOVERY_CAPABILITY_EXPIRED")
    if operation in {"consume", "revoke"} and observed_at >= persisted.expires_at:
        raise PasswordRecoveryCapabilityLifecycleConflictError("RECOVERY_CAPABILITY_EXPIRED")
    if operation == "expire" and observed_at < persisted.expires_at:
        raise PasswordRecoveryCapabilityLifecycleConflictError("RECOVERY_EXPIRY_BOUNDARY_NOT_REACHED")
    raise PasswordRecoveryCapabilityLifecycleConflictError("RECOVERY_LIFECYCLE_CONFLICT")


class PasswordRecoveryCapabilityRegistry:
    """Persist and atomically transition R10B1 recovery capabilities.

    The registry accepts an injected PyMongo collection for composition and
    deterministic certification. If omitted, it resolves the canonical Kernel
    database only when an operation is invoked. Every supplied session is
    forwarded unchanged. No method creates, commits, aborts, or retries a
    transaction, and no method generates or exposes raw token material.
    """

    def __init__(self, collection: Any | None = None) -> None:
        """Bind one collection dependency without opening Mongo or creating indexes."""

        self._collection = collection

    def _source(self) -> Any:
        """Return the configured or canonical collection at operation time."""

        return _target(self._collection)

    def ensure_indexes(self) -> None:
        """Create deterministic identity and query indexes outside transactions.

        Capability and digest uniqueness prevent two durable opaque identities
        from representing different records. The tenant/principal/status/time
        index supports bounded lifecycle queries. No TTL deletion index is
        created because absence must never erase EXPIRED evidence.
        """

        source = self._source()
        try:
            for keys, unique, name in INDEX_DEFINITIONS:
                source.create_index(list(keys), unique=unique, name=name)
        except PyMongoError as error:
            raise PasswordRecoveryCapabilityPersistenceError("RECOVERY_INDEX_CREATION_FAILED") from error

    def create(
        self,
        capability: PasswordRecoveryCapability,
        *,
        session: Any | None = None,
    ) -> PasswordRecoveryCapability:
        """Insert exactly one ACTIVE capability using the domain serializer.

        This is insert-only: duplicate identity or digest is a conflict, never
        an implicit upsert or replay success. The caller owns transaction
        commit/retry and any recovery service policy surrounding issuance.
        """

        if not isinstance(capability, PasswordRecoveryCapability):
            raise PasswordRecoveryCapabilityRegistryError("RECOVERY_CREATE_INVALID")
        if capability.status is not PasswordRecoveryCapabilityStatus.ACTIVE:
            raise PasswordRecoveryCapabilityRegistryError("RECOVERY_CREATE_REQUIRES_ACTIVE")
        source = self._source()
        try:
            source.insert_one(_document(capability), **_session_kwargs(session))
            return capability
        except DuplicateKeyError as error:
            try:
                identity = source.find_one(
                    {"tenant_id": capability.tenant_id, "capability_id": capability.capability_id},
                    **_session_kwargs(session),
                )
                digest = source.find_one(
                    {"tenant_id": capability.tenant_id, "token_digest": capability.token_digest},
                    **_session_kwargs(session),
                )
            except PyMongoError as read_error:
                raise PasswordRecoveryCapabilityPersistenceError("RECOVERY_DUPLICATE_CLASSIFICATION_FAILED") from read_error
            if identity is not None:
                raise PasswordRecoveryCapabilityAlreadyExistsError("RECOVERY_CAPABILITY_ID_DUPLICATE") from error
            if digest is not None:
                raise PasswordRecoveryCapabilityAlreadyExistsError("RECOVERY_TOKEN_DIGEST_DUPLICATE") from error
            raise PasswordRecoveryCapabilityAlreadyExistsError("RECOVERY_DUPLICATE_CONFLICT") from error
        except PyMongoError as error:
            raise PasswordRecoveryCapabilityPersistenceError("RECOVERY_CREATE_FAILED") from error

    def get_by_capability_id(
        self,
        *,
        tenant_id: str,
        capability_id: str,
        session: Any | None = None,
    ) -> PasswordRecoveryCapability | None:
        """Read one exact tenant/capability binding or return scoped absence."""

        if not isinstance(tenant_id, str) or not tenant_id.strip() or not isinstance(capability_id, str) or not capability_id.strip():
            raise PasswordRecoveryCapabilityNotFoundError("RECOVERY_CAPABILITY_NOT_FOUND")
        try:
            row = self._source().find_one(
                {"tenant_id": tenant_id, "capability_id": capability_id},
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise PasswordRecoveryCapabilityPersistenceError("RECOVERY_READ_FAILED") from error
        return None if row is None else _hydrate(row)

    def get_by_token_digest(
        self,
        *,
        tenant_id: str,
        token_digest: str,
        session: Any | None = None,
    ) -> PasswordRecoveryCapability | None:
        """Read one exact tenant/digest binding or return scoped absence.

        The digest is already canonical R10B1 evidence; this method does not
        accept, hash, compare, or disclose raw recovery tokens.
        """

        if not isinstance(tenant_id, str) or not tenant_id.strip() or not isinstance(token_digest, str) or not token_digest.strip():
            raise PasswordRecoveryCapabilityNotFoundError("RECOVERY_CAPABILITY_NOT_FOUND")
        try:
            row = self._source().find_one(
                {"tenant_id": tenant_id, "token_digest": token_digest},
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise PasswordRecoveryCapabilityPersistenceError("RECOVERY_READ_FAILED") from error
        return None if row is None else _hydrate(row)

    def list_active_for_principal(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        session: Any | None = None,
    ) -> tuple[PasswordRecoveryCapability, ...]:
        """Read every ACTIVE capability for one exact tenant/principal pair.

        This bounded persistence seam exists so an issuance orchestrator can
        reconcile earlier recovery windows before creating a replacement.
        Every returned row is hydrated through the immutable recovery domain
        and must retain the requested tenant/principal/status binding. Raw
        recovery token material is never accepted or returned. The optional
        caller session is forwarded unchanged; this method performs no
        transition, issuance, retry, transaction, delivery, or credential work.
        """

        if (
            not isinstance(tenant_id, str)
            or not tenant_id.strip()
            or not isinstance(principal_id, str)
            or not principal_id.strip()
        ):
            raise PasswordRecoveryCapabilityRegistryError("RECOVERY_PRINCIPAL_QUERY_INVALID")
        query = {
            "tenant_id": tenant_id,
            "principal_id": principal_id,
            "status": PasswordRecoveryCapabilityStatus.ACTIVE.value,
        }
        try:
            rows = self._source().find(query, **_session_kwargs(session))
            capabilities = tuple(_hydrate(row) for row in rows)
        except PasswordRecoveryCapabilityPersistedRecordInvalidError:
            raise
        except PyMongoError as error:
            raise PasswordRecoveryCapabilityPersistenceError(
                "RECOVERY_PRINCIPAL_ACTIVE_READ_FAILED"
            ) from error
        for capability in capabilities:
            if (
                capability.tenant_id != tenant_id
                or capability.principal_id != principal_id
                or capability.status is not PasswordRecoveryCapabilityStatus.ACTIVE
            ):
                raise PasswordRecoveryCapabilityPersistedRecordInvalidError(
                    "RECOVERY_PERSISTED_RECORD_INVALID"
                )
        return capabilities
    def _transition(
        self,
        capability: PasswordRecoveryCapability,
        observed_at: datetime,
        *,
        operation: str,
        replacement: PasswordRecoveryCapability,
        session: Any | None,
    ) -> PasswordRecoveryCapability:
        """Execute one atomic ACTIVE-state compare-and-set transition."""

        source = self._source()
        query = _identity_query(capability)
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
        update = {"$set": {"status": replacement_payload["status"], terminal_field: replacement_payload[terminal_field]}}
        try:
            row = source.find_one_and_update(
                query,
                update,
                return_document=ReturnDocument.AFTER,
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise PasswordRecoveryCapabilityPersistenceError("RECOVERY_TRANSITION_FAILED") from error
        if row is None:
            _transition_failure(source, capability, observed_at, session=session, operation=operation)
        return _hydrate(row)

    def consume(
        self,
        capability: PasswordRecoveryCapability,
        consumed_at: datetime,
        *,
        session: Any | None = None,
    ) -> PasswordRecoveryCapability:
        """Atomically consume one ACTIVE capability before immutable expiry."""

        if not isinstance(capability, PasswordRecoveryCapability):
            raise PasswordRecoveryCapabilityRegistryError("RECOVERY_TRANSITION_INVALID")
        try:
            replacement = capability.consume(consumed_at)
        except PasswordRecoveryCapabilityError as error:
            raise PasswordRecoveryCapabilityLifecycleConflictError(error.code) from error
        return self._transition(capability, consumed_at, operation="consume", replacement=replacement, session=session)

    def revoke(
        self,
        capability: PasswordRecoveryCapability,
        revoked_at: datetime,
        *,
        session: Any | None = None,
    ) -> PasswordRecoveryCapability:
        """Atomically revoke one ACTIVE capability before immutable expiry."""

        if not isinstance(capability, PasswordRecoveryCapability):
            raise PasswordRecoveryCapabilityRegistryError("RECOVERY_TRANSITION_INVALID")
        try:
            replacement = capability.revoke(revoked_at)
        except PasswordRecoveryCapabilityError as error:
            raise PasswordRecoveryCapabilityLifecycleConflictError(error.code) from error
        return self._transition(capability, revoked_at, operation="revoke", replacement=replacement, session=session)

    def expire(
        self,
        capability: PasswordRecoveryCapability,
        expired_at: datetime,
        *,
        session: Any | None = None,
    ) -> PasswordRecoveryCapability:
        """Atomically mark one ACTIVE capability EXPIRED at or after expiry."""

        if not isinstance(capability, PasswordRecoveryCapability):
            raise PasswordRecoveryCapabilityRegistryError("RECOVERY_TRANSITION_INVALID")
        try:
            replacement = capability.expire(expired_at)
        except PasswordRecoveryCapabilityError as error:
            raise PasswordRecoveryCapabilityLifecycleConflictError(error.code) from error
        return self._transition(capability, expired_at, operation="expire", replacement=replacement, session=session)


__all__ = [
    "COLLECTION",
    "INDEX_DEFINITIONS",
    "PasswordRecoveryCapabilityAlreadyExistsError",
    "PasswordRecoveryCapabilityLifecycleConflictError",
    "PasswordRecoveryCapabilityNotFoundError",
    "PasswordRecoveryCapabilityPersistedRecordInvalidError",
    "PasswordRecoveryCapabilityPersistenceError",
    "PasswordRecoveryCapabilityRegistry",
    "PasswordRecoveryCapabilityRegistryError",
    "VERSION",
]


# ARTIFACT: password_recovery_registry.py
# VERSION: v1.1.0-R10E2-ACTIVE-PRINCIPAL-RECOVERY-QUERY
# AUTHORITY BOUNDARY: digest-only capability persistence and lifecycle CAS; no credential authority
# TENANT POSTURE: exact tenant-scoped reads and mutations; no cross-tenant fallback
# FAIL-CLOSED POSTURE: duplicate, absent, corrupt, divergent, stale, and persistence states reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
