"""WILSY OS durable H7D verified Legal notification-contact registry.

TITLE: Verified Legal Notification Contact Registry
VERSION: v1.0.0-L8-8H7D-VERIFIED-LEGAL-NOTIFICATION-CONTACT-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist and revoke exact digest-only H7B Legal notification-contact
         authority under strict tenant isolation, consumed-verification
         provenance uniqueness and caller-owned Mongo transaction semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_verified_notification_contact_registry.py
COLLABORATION / OWNERSHIP: H7B owns verified-contact authority semantics.
                            H7D owns only durable persistence/read/revocation.
                            H7E will own lawful orchestration/elevation.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0-L8-8H7D-VERIFIED-LEGAL-NOTIFICATION-CONTACT-REGISTRY
           establishes exact identity/provenance indexes, one-active-address
           scope, strict hydration, replay, tenant-scoped reads and atomic
           ACTIVE-to-REVOKED compare-and-set persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists only canonical H7B digest-only authority.
                             No raw contact address, verification token,
                             credential or message body is persisted.
TENANT BOUNDARY: Every operational query includes exact tenant_id.
AUTHORITY BOUNDARY: Persistence of already-created H7B authority only. This
                    registry cannot elevate H7A, select recipients, dispatch,
                    deliver, grant IAM/Court authority or create AI truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies and owns every active transaction.
FAIL-CLOSED DECLARATION: Missing transaction, malformed storage, duplicate
                         active authority, divergent replay, stale CAS,
                         races or persistence failure reject.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Final, NoReturn, cast

import hmac
from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_notification_contact_verification import (
    LegalNotificationContactChannel,
)
from tools.eos.legal_operations.domain.legal_verified_notification_contact import (
    VerifiedLegalNotificationContact,
    VerifiedLegalNotificationContactError,
    VerifiedLegalNotificationContactStatus,
)


VERSION: Final[str] = (
    "v1.0.0-L8-8H7D-VERIFIED-LEGAL-NOTIFICATION-CONTACT-REGISTRY"
)
COLLECTION: Final[str] = "legal_verified_notification_contacts"

CONTACT_ID_INDEX: Final[str] = (
    "legal_verified_contact_tenant_contact_unique"
)
VERIFICATION_INDEX: Final[str] = (
    "legal_verified_contact_tenant_verification_unique"
)
ACTIVE_SCOPE_INDEX: Final[str] = (
    "legal_verified_contact_active_address_unique"
)
PRINCIPAL_SCOPE_INDEX: Final[str] = (
    "legal_verified_contact_tenant_principal_history"
)

_PAYLOAD_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "contact_version",
    "tenant_id",
    "contact_id",
    "principal_id",
    "channel",
    "address_digest",
    "verification_id",
    "verification_fingerprint",
    "verification_consumed_at",
    "verification_expires_at",
    "verified_at",
    "revoked_at",
    "fingerprint",
)


class VerifiedLegalNotificationContactRegistryError(RuntimeError):
    """Base fail-closed H7D registry error with one stable code."""

    default_code = "L8_8H7D_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class VerifiedLegalNotificationContactRegistryInputError(
    VerifiedLegalNotificationContactRegistryError
):
    """Malformed H7D input."""

    default_code = "L8_8H7D_INPUT_INVALID"


class VerifiedLegalNotificationContactRegistryTransactionRequiredError(
    VerifiedLegalNotificationContactRegistryError
):
    """Caller failed to provide one already-active transaction."""

    default_code = "L8_8H7D_ACTIVE_TRANSACTION_REQUIRED"


class VerifiedLegalNotificationContactRegistryConflictError(
    VerifiedLegalNotificationContactRegistryError
):
    """Persisted authority conflicts with requested state."""

    default_code = "L8_8H7D_CONTACT_CONFLICT"


class VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError(
    VerifiedLegalNotificationContactRegistryError
):
    """Durable H7B state is corrupt or internally divergent."""

    default_code = "L8_8H7D_PERSISTED_RECORD_INVALID"


class VerifiedLegalNotificationContactRegistryRetryTransactionError(
    VerifiedLegalNotificationContactRegistryError
):
    """Caller must abort and retry the complete transaction."""

    default_code = "L8_8H7D_WHOLE_TRANSACTION_RETRY_REQUIRED"


class VerifiedLegalNotificationContactRegistryPersistenceError(
    VerifiedLegalNotificationContactRegistryError
):
    """Mongo persistence failed."""

    default_code = "L8_8H7D_PERSISTENCE_FAILURE"


def _raise(
    error_type: type[VerifiedLegalNotificationContactRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one bounded H7D error while retaining technical cause."""

    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _require_transaction(session: object) -> object:
    """Require an already-active caller-owned transaction."""

    if session is None:
        _raise(
            VerifiedLegalNotificationContactRegistryTransactionRequiredError
        )

    marker = getattr(session, "in_transaction", None)

    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False

    if active is not True:
        _raise(
            VerifiedLegalNotificationContactRegistryTransactionRequiredError
        )

    return session


def _text(name: str, value: object) -> str:
    """Require one exact non-empty non-coerced identifier."""

    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        _raise(
            VerifiedLegalNotificationContactRegistryInputError,
            f"L8_8H7D_{name.upper()}_INVALID",
        )

    return value


def _digest(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 digest."""

    text = _text(name, value)

    if (
        len(text) != 128
        or any(
            character not in "0123456789abcdef"
            for character in text
        )
    ):
        _raise(
            VerifiedLegalNotificationContactRegistryInputError,
            f"L8_8H7D_{name.upper()}_INVALID",
        )

    return text


def _tenant(value: object) -> str:
    """Require one exact H7B tenant identifier."""

    tenant = _text("tenant_id", value)

    if tenant.lower() in {
        "default",
        "global",
        "global_root",
        "root",
        "master",
    }:
        _raise(
            VerifiedLegalNotificationContactRegistryInputError,
            "L8_8H7D_TENANT_REQUIRED",
        )

    if tenant == "*":
        _raise(
            VerifiedLegalNotificationContactRegistryInputError,
            "L8_8H7D_TENANT_ID_INVALID",
        )

    return tenant


def _channel(
    value: LegalNotificationContactChannel | str,
) -> LegalNotificationContactChannel:
    """Require one exact supported Legal notification-contact channel."""

    try:
        return LegalNotificationContactChannel(value)
    except (TypeError, ValueError) as error:
        _raise(
            VerifiedLegalNotificationContactRegistryInputError,
            "L8_8H7D_CHANNEL_INVALID",
            error,
        )


def _document(
    value: VerifiedLegalNotificationContact,
) -> dict[str, object]:
    """Return exact canonical H7B durable payload."""

    payload = value.to_dict()

    if set(payload) != set(_PAYLOAD_FIELDS):
        _raise(
            VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
            "L8_8H7D_DOMAIN_PAYLOAD_SCHEMA_INVALID",
        )

    return dict(payload)


def _hydrate(
    row: Mapping[str, object],
) -> VerifiedLegalNotificationContact:
    """Hydrate exact H7B state and reject storage corruption."""

    if not isinstance(row, Mapping):
        _raise(
            VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError
        )

    payload = {
        key: value
        for key, value in row.items()
        if key != "_id"
    }

    if set(payload) != set(_PAYLOAD_FIELDS):
        _raise(
            VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
            "L8_8H7D_RECORD_SCHEMA_INVALID",
        )

    try:
        value = VerifiedLegalNotificationContact.from_dict(
            cast(Mapping[str, object], payload)
        )
    except (
        VerifiedLegalNotificationContactError,
        TypeError,
        ValueError,
    ) as error:
        _raise(
            VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
            "L8_8H7D_PERSISTED_RECORD_INVALID",
            error,
        )

    if value.to_dict() != payload:
        _raise(
            VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
            "L8_8H7D_RECORD_CORRELATION_INVALID",
        )

    return value


def _same(
    left: VerifiedLegalNotificationContact,
    right: VerifiedLegalNotificationContact,
) -> bool:
    """Compare exact immutable H7B state by canonical fingerprint."""

    return hmac.compare_digest(
        left.fingerprint,
        right.fingerprint,
    )


class VerifiedLegalNotificationContactRegistry:
    """Persist/read/revoke exact H7B verified-contact authority."""

    def __init__(self, collection: Any) -> None:
        if collection is None:
            _raise(
                VerifiedLegalNotificationContactRegistryInputError,
                "L8_8H7D_COLLECTION_REQUIRED",
            )

        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create exactly the governed non-TTL H7D indexes."""

        try:
            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("contact_id", ASCENDING),
                ],
                unique=True,
                name=CONTACT_ID_INDEX,
            )

            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("verification_fingerprint", ASCENDING),
                ],
                unique=True,
                name=VERIFICATION_INDEX,
            )

            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("principal_id", ASCENDING),
                    ("channel", ASCENDING),
                    ("address_digest", ASCENDING),
                ],
                unique=True,
                partialFilterExpression={"revoked_at": None},
                name=ACTIVE_SCOPE_INDEX,
            )

            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("principal_id", ASCENDING),
                    ("channel", ASCENDING),
                    ("verified_at", ASCENDING),
                ],
                unique=False,
                name=PRINCIPAL_SCOPE_INDEX,
            )

        except PyMongoError as error:
            _raise(
                VerifiedLegalNotificationContactRegistryPersistenceError,
                "L8_8H7D_INDEX_PERSISTENCE_FAILURE",
                error,
            )

    def create(
        self,
        value: VerifiedLegalNotificationContact,
        *,
        session: object,
    ) -> VerifiedLegalNotificationContact:
        """Insert one H7B authority or return exact identity replay."""

        tx = _require_transaction(session)

        if type(value) is not VerifiedLegalNotificationContact:
            _raise(
                VerifiedLegalNotificationContactRegistryInputError,
                "L8_8H7D_CONTACT_REQUIRED",
            )

        try:
            existing = self._collection.find_one(
                {
                    "tenant_id": value.tenant_id,
                    "contact_id": value.contact_id,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                VerifiedLegalNotificationContactRegistryPersistenceError,
                "L8_8H7D_READ_PERSISTENCE_FAILURE",
                error,
            )

        if existing is not None:
            persisted = _hydrate(
                cast(Mapping[str, object], existing)
            )

            if _same(persisted, value):
                return persisted

            _raise(
                VerifiedLegalNotificationContactRegistryConflictError,
                "L8_8H7D_DIVERGENT_REPLAY",
            )

        try:
            provenance = self._collection.find_one(
                {
                    "tenant_id": value.tenant_id,
                    "verification_fingerprint": (
                        value.verification_fingerprint
                    ),
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                VerifiedLegalNotificationContactRegistryPersistenceError,
                "L8_8H7D_READ_PERSISTENCE_FAILURE",
                error,
            )

        if provenance is not None:
            persisted = _hydrate(
                cast(Mapping[str, object], provenance)
            )

            if _same(persisted, value):
                return persisted

            _raise(
                VerifiedLegalNotificationContactRegistryConflictError,
                "L8_8H7D_VERIFICATION_ALREADY_ELEVATED",
            )

        try:
            self._collection.insert_one(
                _document(value),
                session=tx,
            )
        except DuplicateKeyError as error:
            _raise(
                VerifiedLegalNotificationContactRegistryRetryTransactionError,
                "L8_8H7D_DUPLICATE_RACE_RETRY_TRANSACTION",
                error,
            )
        except PyMongoError as error:
            _raise(
                VerifiedLegalNotificationContactRegistryPersistenceError,
                "L8_8H7D_WRITE_PERSISTENCE_FAILURE",
                error,
            )

        return value

    def get_by_id(
        self,
        tenant_id: str,
        contact_id: str,
        *,
        session: object,
    ) -> VerifiedLegalNotificationContact | None:
        """Read one exact tenant-scoped contact identity."""

        tx = _require_transaction(session)
        tenant = _tenant(tenant_id)
        identity = _text("contact_id", contact_id)

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "contact_id": identity,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                VerifiedLegalNotificationContactRegistryPersistenceError,
                "L8_8H7D_READ_PERSISTENCE_FAILURE",
                error,
            )

        if row is None:
            return None

        return _hydrate(
            cast(Mapping[str, object], row)
        )

    def get_by_verification_fingerprint(
        self,
        tenant_id: str,
        verification_fingerprint: str,
        *,
        session: object,
    ) -> VerifiedLegalNotificationContact | None:
        """Read H7B authority by exact consumed-H7A provenance."""

        tx = _require_transaction(session)
        tenant = _tenant(tenant_id)
        fingerprint = _digest(
            "verification_fingerprint",
            verification_fingerprint,
        )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "verification_fingerprint": fingerprint,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                VerifiedLegalNotificationContactRegistryPersistenceError,
                "L8_8H7D_READ_PERSISTENCE_FAILURE",
                error,
            )

        if row is None:
            return None

        return _hydrate(
            cast(Mapping[str, object], row)
        )

    def get_active(
        self,
        tenant_id: str,
        principal_id: str,
        channel: LegalNotificationContactChannel | str,
        address_digest: str,
        *,
        session: object,
    ) -> VerifiedLegalNotificationContact | None:
        """Read one exact ACTIVE tenant/principal/channel/address authority."""

        tx = _require_transaction(session)
        tenant = _tenant(tenant_id)
        principal = _text("principal_id", principal_id)
        contact_channel = _channel(channel)
        digest = _digest("address_digest", address_digest)

        try:
            rows: list[Mapping[str, object]] = [
                cast(Mapping[str, object], row)
                for row in cast(
                    Iterable[object],
                    self._collection.find(
                        {
                            "tenant_id": tenant,
                            "principal_id": principal,
                            "channel": contact_channel.value,
                            "address_digest": digest,
                            "revoked_at": None,
                        },
                        session=tx,
                    ).limit(2),
                )
            ]
        except PyMongoError as error:
            _raise(
                VerifiedLegalNotificationContactRegistryPersistenceError,
                "L8_8H7D_READ_PERSISTENCE_FAILURE",
                error,
            )

        if not rows:
            return None

        if len(rows) > 1:
            _raise(
                VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
                "L8_8H7D_MULTIPLE_ACTIVE_CONTACTS",
            )

        value = _hydrate(
            cast(Mapping[str, object], rows[0])
        )

        if value.status is not VerifiedLegalNotificationContactStatus.ACTIVE:
            _raise(
                VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
                "L8_8H7D_ACTIVE_QUERY_CORRELATION_INVALID",
            )

        return value

    def list_principal_scope(
        self,
        tenant_id: str,
        principal_id: str,
        channel: LegalNotificationContactChannel | str,
        *,
        session: object,
    ) -> tuple[VerifiedLegalNotificationContact, ...]:
        """List exact tenant/principal/channel history oldest-first."""

        tx = _require_transaction(session)
        tenant = _tenant(tenant_id)
        principal = _text("principal_id", principal_id)
        contact_channel = _channel(channel)

        try:
            rows = tuple(
                self._collection.find(
                    {
                        "tenant_id": tenant,
                        "principal_id": principal,
                        "channel": contact_channel.value,
                    },
                    session=tx,
                ).sort(
                    [
                        ("verified_at", ASCENDING),
                        ("contact_id", ASCENDING),
                    ]
                )
            )
        except PyMongoError as error:
            _raise(
                VerifiedLegalNotificationContactRegistryPersistenceError,
                "L8_8H7D_READ_PERSISTENCE_FAILURE",
                error,
            )

        values = tuple(
            _hydrate(cast(Mapping[str, object], row))
            for row in rows
        )

        if any(
            value.tenant_id != tenant
            or value.principal_id != principal
            or value.channel is not contact_channel
            for value in values
        ):
            _raise(
                VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
                "L8_8H7D_PRINCIPAL_QUERY_CORRELATION_INVALID",
            )

        return values

    def revoke(
        self,
        source: VerifiedLegalNotificationContact,
        revoked_at: object,
        *,
        session: object,
    ) -> VerifiedLegalNotificationContact:
        """Atomically persist one exact ACTIVE-to-REVOKED transition."""

        tx = _require_transaction(session)

        if type(source) is not VerifiedLegalNotificationContact:
            _raise(
                VerifiedLegalNotificationContactRegistryInputError,
                "L8_8H7D_CONTACT_REQUIRED",
            )

        if (
            source.status
            is not VerifiedLegalNotificationContactStatus.ACTIVE
        ):
            _raise(
                VerifiedLegalNotificationContactRegistryConflictError,
                "L8_8H7D_SOURCE_NOT_ACTIVE",
            )

        try:
            replacement = source.revoke(
                cast(Any, revoked_at)
            )
        except VerifiedLegalNotificationContactError as error:
            _raise(
                VerifiedLegalNotificationContactRegistryConflictError,
                "L8_8H7D_REVOKE_REJECTED",
                error,
            )

        selector = {
            "tenant_id": source.tenant_id,
            "contact_id": source.contact_id,
            "fingerprint": source.fingerprint,
            "revoked_at": None,
        }

        try:
            row = self._collection.find_one_and_replace(
                selector,
                _document(replacement),
                return_document=ReturnDocument.AFTER,
                session=tx,
            )
        except DuplicateKeyError as error:
            _raise(
                VerifiedLegalNotificationContactRegistryRetryTransactionError,
                "L8_8H7D_REVOKE_RACE_RETRY_TRANSACTION",
                error,
            )
        except PyMongoError as error:
            _raise(
                VerifiedLegalNotificationContactRegistryPersistenceError,
                "L8_8H7D_TRANSITION_PERSISTENCE_FAILURE",
                error,
            )

        if row is not None:
            persisted = _hydrate(
                cast(Mapping[str, object], row)
            )

            if not _same(persisted, replacement):
                _raise(
                    VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
                    "L8_8H7D_TRANSITION_RESULT_INVALID",
                )

            return persisted

        try:
            current = self._collection.find_one(
                {
                    "tenant_id": source.tenant_id,
                    "contact_id": source.contact_id,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                VerifiedLegalNotificationContactRegistryPersistenceError,
                "L8_8H7D_READ_PERSISTENCE_FAILURE",
                error,
            )

        if current is None:
            _raise(
                VerifiedLegalNotificationContactRegistryConflictError,
                "L8_8H7D_CONTACT_NOT_FOUND",
            )

        persisted = _hydrate(
            cast(Mapping[str, object], current)
        )

        if _same(persisted, replacement):
            return persisted

        _raise(
            VerifiedLegalNotificationContactRegistryConflictError,
            "L8_8H7D_STALE_SOURCE_CONFLICT",
        )


__all__ = [
    "ACTIVE_SCOPE_INDEX",
    "COLLECTION",
    "CONTACT_ID_INDEX",
    "PRINCIPAL_SCOPE_INDEX",
    "VERIFICATION_INDEX",
    "VERSION",
    "VerifiedLegalNotificationContactRegistry",
    "VerifiedLegalNotificationContactRegistryConflictError",
    "VerifiedLegalNotificationContactRegistryError",
    "VerifiedLegalNotificationContactRegistryInputError",
    "VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError",
    "VerifiedLegalNotificationContactRegistryPersistenceError",
    "VerifiedLegalNotificationContactRegistryRetryTransactionError",
    "VerifiedLegalNotificationContactRegistryTransactionRequiredError",
]


# ARTIFACT: legal_verified_notification_contact_registry.py
# VERSION: v1.0.0-L8-8H7D-VERIFIED-LEGAL-NOTIFICATION-CONTACT-REGISTRY
# AUTHORITY BOUNDARY: durable H7B verified-contact persistence/read/revocation only
# TENANT POSTURE: exact tenant predicates and caller-owned active transactions
# FAIL-CLOSED POSTURE: corruption/divergence/stale-CAS/race/persistence failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
