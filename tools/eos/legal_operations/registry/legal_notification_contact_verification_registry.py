"""Durable registry for Legal notification-contact verification capabilities.

TITLE: Legal Notification Contact Verification Registry
VERSION: v1.0.0-L8-8H7C-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist, hydrate, exact-replay, tenant-read and atomically transition
         H7A single-use Legal notification-contact verification capabilities
         inside caller-owned active Mongo transactions without storing raw
         contact/token material or creating verified-contact/delivery truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_notification_contact_verification_registry.py
COLLABORATION / OWNERSHIP: H7A owns immutable verification meaning. H7C owns
                           only persistence and atomic lifecycle transitions for
                           that exact H7A value. H7B owns verified Legal contact
                           authority and is intentionally not created here.
                           Callers own Mongo sessions, transactions and retry.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0-L8-8H7C-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-REGISTRY
           establishes Legal-only durable verification persistence with exact
           tenant+verification and tenant+token unique indexes, tenant/principal
           scope reads, strict active-transaction requirements, exact replay,
           duplicate-race whole-transaction retry signalling, deterministic
           hydration, microsecond-safe canonical ISO timestamp persistence and
           CAS consume/revoke/expire transitions. No TTL index is created.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists only H7A digest-only state. Raw email
                            addresses, raw verification capabilities, SMTP
                            credentials, provider identifiers and delivery
                            payloads are prohibited. Persisted corruption fails
                            closed through H7A hydration/fingerprint validation.
TENANT BOUNDARY: Every operational read/write is exact tenant scoped and requires
                 one caller-owned already-active transaction. No global lookup
                 or cross-tenant existence oracle is exposed.
AUTHORITY BOUNDARY: H7A verification persistence/read/transition only. Registry
                    state cannot create H7B verified-contact authority, select
                    recipients, dispatch messages or prove delivery.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority.
TRANSACTION BOUNDARY: Caller owns one already-active Mongo transaction and all
                      whole-transaction retry. This registry never starts,
                      commits, aborts or retries a transaction.
TTL POSTURE: No TTL index. Verification expiry is explicit H7A domain lifecycle
             truth and cannot be replaced by background document deletion.
FAIL-CLOSED DECLARATION: Missing/inactive transaction, malformed selectors,
                         corrupt persisted state, divergent replay, duplicate
                         races, stale CAS sources and persistence failures reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
import hmac
import re
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_notification_contact_verification import (
    LegalNotificationContactChannel,
    LegalNotificationContactVerification,
    LegalNotificationContactVerificationError,
    LegalNotificationContactVerificationStatus,
)


VERSION: Final[str] = (
    "v1.0.0-L8-8H7C-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-REGISTRY"
)
COLLECTION: Final[str] = "legal_notification_contact_verifications"

IDENTITY_INDEX: Final[str] = (
    "legal_notification_contact_verification_identity_unique"
)
TOKEN_INDEX: Final[str] = (
    "legal_notification_contact_verification_token_unique"
)
PRINCIPAL_SCOPE_INDEX: Final[str] = (
    "legal_notification_contact_verification_principal_scope"
)

_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,191}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalNotificationContactVerificationRegistryError(RuntimeError):
    """Base stable H7C persistence-boundary failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalNotificationContactVerificationRegistryTransactionRequiredError(
    LegalNotificationContactVerificationRegistryError
):
    """Caller did not supply one already-active transaction."""


class LegalNotificationContactVerificationRegistryConflictError(
    LegalNotificationContactVerificationRegistryError
):
    """Persisted authority conflicts with the requested exact operation."""


class LegalNotificationContactVerificationRegistryPersistedRecordInvalidError(
    LegalNotificationContactVerificationRegistryError
):
    """Persisted bytes cannot hydrate through the exact H7A domain."""


class LegalNotificationContactVerificationRegistryPersistenceError(
    LegalNotificationContactVerificationRegistryError
):
    """Mongo persistence failed without a safely classifiable race."""


class LegalNotificationContactVerificationRegistryRetryTransactionError(
    LegalNotificationContactVerificationRegistryError
):
    """Caller must abort and retry the complete transaction from fresh reads."""


def _raise(
    error_type: type[LegalNotificationContactVerificationRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable registry error without leaking persistence details."""

    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _require_transaction(session: object) -> object:
    """Require one caller-owned already-active Mongo transaction."""

    if session is None:
        _raise(
            LegalNotificationContactVerificationRegistryTransactionRequiredError,
            "L8_8H7C_ACTIVE_TRANSACTION_REQUIRED",
        )

    try:
        active = getattr(session, "in_transaction", False)
    except Exception as error:
        _raise(
            LegalNotificationContactVerificationRegistryTransactionRequiredError,
            "L8_8H7C_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )

    if active is not True:
        _raise(
            LegalNotificationContactVerificationRegistryTransactionRequiredError,
            "L8_8H7C_ACTIVE_TRANSACTION_REQUIRED",
        )

    return session


def _identifier(name: str, value: object) -> str:
    """Validate one exact registry selector."""

    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTIFIER.fullmatch(value) is None
    ):
        _raise(
            LegalNotificationContactVerificationRegistryError,
            f"L8_8H7C_{name.upper()}_INVALID",
        )
    return value


def _tenant(value: object) -> str:
    """Validate one exact non-global tenant selector."""

    tenant = _identifier("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _raise(
            LegalNotificationContactVerificationRegistryError,
            "L8_8H7C_TENANT_REQUIRED",
        )
    return tenant


def _digest(name: str, value: object) -> str:
    """Validate one lowercase SHA3-512 selector."""

    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _raise(
            LegalNotificationContactVerificationRegistryError,
            f"L8_8H7C_{name.upper()}_INVALID",
        )
    return value


def _channel(value: object) -> LegalNotificationContactChannel:
    """Validate one closed H7A channel selector."""

    try:
        return LegalNotificationContactChannel(value)
    except (TypeError, ValueError) as error:
        _raise(
            LegalNotificationContactVerificationRegistryError,
            "L8_8H7C_CHANNEL_INVALID",
            error,
        )


def _document(
    value: LegalNotificationContactVerification,
) -> dict[str, object]:
    """Build exact microsecond-safe Mongo document from one H7A value.

    H7A's datetime fields are already canonical ISO-8601 UTC strings in
    `to_dict()`. Keeping those strings instead of converting to BSON datetime
    prevents Mongo's millisecond precision from changing the domain payload or
    its deterministic fingerprint.
    """

    if not isinstance(value, LegalNotificationContactVerification):
        _raise(
            LegalNotificationContactVerificationRegistryError,
            "L8_8H7C_VERIFICATION_REQUIRED",
        )

    payload = value.to_dict()

    for field in (
        "issued_at",
        "expires_at",
        "consumed_at",
        "expired_at",
        "revoked_at",
    ):
        stored = payload[field]
        if stored is not None and not isinstance(stored, str):
            _raise(
                LegalNotificationContactVerificationRegistryError,
                "L8_8H7C_TIMESTAMP_SERIALIZATION_INVALID",
            )

    return dict(payload)


def _hydrate(
    row: Mapping[str, object],
) -> LegalNotificationContactVerification:
    """Hydrate exact persisted H7A state and reject storage corruption."""

    if not isinstance(row, Mapping):
        _raise(
            LegalNotificationContactVerificationRegistryPersistedRecordInvalidError,
            "L8_8H7C_PERSISTED_RECORD_INVALID",
        )

    payload = {
        key: value
        for key, value in row.items()
        if key != "_id"
    }

    try:
        return LegalNotificationContactVerification.from_dict(payload)
    except (LegalNotificationContactVerificationError, TypeError, ValueError) as error:
        _raise(
            LegalNotificationContactVerificationRegistryPersistedRecordInvalidError,
            "L8_8H7C_PERSISTED_RECORD_INVALID",
            error,
        )


def _same(
    left: LegalNotificationContactVerification,
    right: LegalNotificationContactVerification,
) -> bool:
    """Compare immutable H7A authority by exact deterministic fingerprint."""

    return hmac.compare_digest(left.fingerprint, right.fingerprint)


class LegalNotificationContactVerificationRegistry:
    """Persist and transition exact H7A verification authority.

    The supplied collection is the only persistence boundary. All operational
    methods require one caller-owned active transaction. `ensure_indexes` is
    intentionally outside transaction ownership and should be invoked during
    controlled application/bootstrap migration.
    """

    def __init__(self, collection: Any) -> None:
        """Bind one explicit Mongo-compatible collection."""

        if collection is None:
            _raise(
                LegalNotificationContactVerificationRegistryError,
                "L8_8H7C_COLLECTION_REQUIRED",
            )
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create the exact governed non-TTL H7C indexes."""

        try:
            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("verification_id", ASCENDING),
                ],
                unique=True,
                name=IDENTITY_INDEX,
            )
            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("token_digest", ASCENDING),
                ],
                unique=True,
                name=TOKEN_INDEX,
            )
            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("principal_id", ASCENDING),
                    ("channel", ASCENDING),
                    ("issued_at", ASCENDING),
                ],
                unique=False,
                name=PRINCIPAL_SCOPE_INDEX,
            )
        except PyMongoError as error:
            _raise(
                LegalNotificationContactVerificationRegistryPersistenceError,
                "L8_8H7C_INDEX_PERSISTENCE_FAILURE",
                error,
            )

    def create(
        self,
        value: LegalNotificationContactVerification,
        *,
        session: object,
    ) -> LegalNotificationContactVerification:
        """Insert one H7A value or return exact same-identity replay.

        A duplicate-key race after the pre-read cannot safely be inspected inside
        the now-aborted Mongo transaction; callers must retry the whole
        transaction from fresh reads.
        """

        tx = _require_transaction(session)

        if not isinstance(value, LegalNotificationContactVerification):
            _raise(
                LegalNotificationContactVerificationRegistryError,
                "L8_8H7C_VERIFICATION_REQUIRED",
            )

        try:
            existing = self._collection.find_one(
                {
                    "tenant_id": value.tenant_id,
                    "verification_id": value.verification_id,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                LegalNotificationContactVerificationRegistryPersistenceError,
                "L8_8H7C_READ_PERSISTENCE_FAILURE",
                error,
            )

        if existing is not None:
            persisted = _hydrate(cast(Mapping[str, object], existing))
            if _same(persisted, value):
                return persisted
            _raise(
                LegalNotificationContactVerificationRegistryConflictError,
                "L8_8H7C_DIVERGENT_REPLAY",
            )

        try:
            self._collection.insert_one(
                _document(value),
                session=tx,
            )
        except DuplicateKeyError as error:
            _raise(
                LegalNotificationContactVerificationRegistryRetryTransactionError,
                "L8_8H7C_DUPLICATE_RACE_RETRY_TRANSACTION",
                error,
            )
        except PyMongoError as error:
            _raise(
                LegalNotificationContactVerificationRegistryPersistenceError,
                "L8_8H7C_WRITE_PERSISTENCE_FAILURE",
                error,
            )

        return value

    def get_by_id(
        self,
        tenant_id: str,
        verification_id: str,
        *,
        session: object,
    ) -> LegalNotificationContactVerification | None:
        """Read one exact tenant-scoped verification identity."""

        tx = _require_transaction(session)
        tenant = _tenant(tenant_id)
        identity = _identifier("verification_id", verification_id)

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "verification_id": identity,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                LegalNotificationContactVerificationRegistryPersistenceError,
                "L8_8H7C_READ_PERSISTENCE_FAILURE",
                error,
            )

        if row is None:
            return None
        return _hydrate(cast(Mapping[str, object], row))

    def get_by_token_digest(
        self,
        tenant_id: str,
        token_digest: str,
        *,
        session: object,
    ) -> LegalNotificationContactVerification | None:
        """Read one exact tenant-scoped verification by token digest."""

        tx = _require_transaction(session)
        tenant = _tenant(tenant_id)
        digest = _digest("token_digest", token_digest)

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "token_digest": digest,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                LegalNotificationContactVerificationRegistryPersistenceError,
                "L8_8H7C_READ_PERSISTENCE_FAILURE",
                error,
            )

        if row is None:
            return None
        return _hydrate(cast(Mapping[str, object], row))

    def list_principal_scope(
        self,
        tenant_id: str,
        principal_id: str,
        channel: LegalNotificationContactChannel | str,
        *,
        session: object,
    ) -> tuple[LegalNotificationContactVerification, ...]:
        """List exact tenant/principal/channel verification history oldest-first."""

        tx = _require_transaction(session)
        tenant = _tenant(tenant_id)
        principal = _identifier("principal_id", principal_id)
        contact_channel = _channel(channel)

        try:
            cursor = self._collection.find(
                {
                    "tenant_id": tenant,
                    "principal_id": principal,
                    "channel": contact_channel.value,
                },
                session=tx,
            ).sort(
                [
                    ("issued_at", ASCENDING),
                    ("verification_id", ASCENDING),
                ]
            )
            rows = tuple(cursor)
        except PyMongoError as error:
            _raise(
                LegalNotificationContactVerificationRegistryPersistenceError,
                "L8_8H7C_READ_PERSISTENCE_FAILURE",
                error,
            )

        return tuple(
            _hydrate(cast(Mapping[str, object], row))
            for row in rows
        )

    def _transition(
        self,
        source: LegalNotificationContactVerification,
        observed_at: datetime,
        *,
        operation: str,
        session: object,
    ) -> LegalNotificationContactVerification:
        """Perform one exact ACTIVE-source atomic H7A lifecycle transition."""

        tx = _require_transaction(session)

        if not isinstance(source, LegalNotificationContactVerification):
            _raise(
                LegalNotificationContactVerificationRegistryError,
                "L8_8H7C_VERIFICATION_REQUIRED",
            )

        if (
            source.status
            is not LegalNotificationContactVerificationStatus.ACTIVE
        ):
            _raise(
                LegalNotificationContactVerificationRegistryConflictError,
                "L8_8H7C_SOURCE_NOT_ACTIVE",
            )

        try:
            if operation == "consume":
                replacement = source.consume(observed_at)
            elif operation == "revoke":
                replacement = source.revoke(observed_at)
            elif operation == "expire":
                replacement = source.expire(observed_at)
            else:
                _raise(
                    LegalNotificationContactVerificationRegistryError,
                    "L8_8H7C_TRANSITION_INVALID",
                )
        except LegalNotificationContactVerificationError as error:
            _raise(
                LegalNotificationContactVerificationRegistryConflictError,
                f"L8_8H7C_{operation.upper()}_REJECTED",
                error,
            )

        selector = {
            "tenant_id": source.tenant_id,
            "verification_id": source.verification_id,
            "fingerprint": source.fingerprint,
            "consumed_at": None,
            "expired_at": None,
            "revoked_at": None,
        }

        try:
            row = self._collection.find_one_and_replace(
                selector,
                _document(replacement),
                return_document=ReturnDocument.AFTER,
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                LegalNotificationContactVerificationRegistryPersistenceError,
                "L8_8H7C_TRANSITION_PERSISTENCE_FAILURE",
                error,
            )

        if row is not None:
            persisted = _hydrate(cast(Mapping[str, object], row))
            if not _same(persisted, replacement):
                _raise(
                    LegalNotificationContactVerificationRegistryPersistedRecordInvalidError,
                    "L8_8H7C_TRANSITION_RESULT_INVALID",
                )
            return persisted

        try:
            current = self._collection.find_one(
                {
                    "tenant_id": source.tenant_id,
                    "verification_id": source.verification_id,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                LegalNotificationContactVerificationRegistryPersistenceError,
                "L8_8H7C_READ_PERSISTENCE_FAILURE",
                error,
            )

        if current is None:
            _raise(
                LegalNotificationContactVerificationRegistryConflictError,
                "L8_8H7C_VERIFICATION_NOT_FOUND",
            )

        persisted = _hydrate(cast(Mapping[str, object], current))

        if _same(persisted, replacement):
            return persisted

        _raise(
            LegalNotificationContactVerificationRegistryConflictError,
            "L8_8H7C_STALE_SOURCE_CONFLICT",
        )

    def consume(
        self,
        source: LegalNotificationContactVerification,
        consumed_at: datetime,
        *,
        session: object,
    ) -> LegalNotificationContactVerification:
        """Atomically consume one exact persisted ACTIVE H7A capability."""

        return self._transition(
            source,
            consumed_at,
            operation="consume",
            session=session,
        )

    def revoke(
        self,
        source: LegalNotificationContactVerification,
        revoked_at: datetime,
        *,
        session: object,
    ) -> LegalNotificationContactVerification:
        """Atomically revoke one exact persisted ACTIVE H7A capability."""

        return self._transition(
            source,
            revoked_at,
            operation="revoke",
            session=session,
        )

    def expire(
        self,
        source: LegalNotificationContactVerification,
        expired_at: datetime,
        *,
        session: object,
    ) -> LegalNotificationContactVerification:
        """Atomically expire one exact persisted ACTIVE H7A capability."""

        return self._transition(
            source,
            expired_at,
            operation="expire",
            session=session,
        )


def ensure_indexes(collection: Any) -> None:
    """Create exact H7C governed indexes on an explicit collection."""

    LegalNotificationContactVerificationRegistry(
        collection
    ).ensure_indexes()


__all__ = [
    "COLLECTION",
    "IDENTITY_INDEX",
    "PRINCIPAL_SCOPE_INDEX",
    "TOKEN_INDEX",
    "VERSION",
    "LegalNotificationContactVerificationRegistry",
    "LegalNotificationContactVerificationRegistryConflictError",
    "LegalNotificationContactVerificationRegistryError",
    "LegalNotificationContactVerificationRegistryPersistedRecordInvalidError",
    "LegalNotificationContactVerificationRegistryPersistenceError",
    "LegalNotificationContactVerificationRegistryRetryTransactionError",
    "LegalNotificationContactVerificationRegistryTransactionRequiredError",
    "ensure_indexes",
]


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_notification_contact_verification_registry.py
# VERSION: v1.0.0-L8-8H7C-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-REGISTRY
# AUTHORITY BOUNDARY: H7A verification persistence/read/CAS lifecycle only; no H7B authority, dispatch, or delivery
# TENANT POSTURE: every operational method is exact tenant scoped inside caller-owned active transaction
# TRANSACTION POSTURE: caller owns transaction and whole-transaction retry; registry never starts/commits/aborts
# TTL POSTURE: no TTL index; explicit H7A expiry lifecycle remains authoritative
# FAIL-CLOSED POSTURE: inactive transaction, corrupt state, divergent replay, race, stale CAS or persistence failure rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
