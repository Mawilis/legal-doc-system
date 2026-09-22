"""Durable registry for WILSY OS verified password-recovery contacts.

TITLE: WILSY OS Verified Recovery Contact Registry
VERSION: v1.1.0-R10E19-SINGLE-ACTIVE-RECOVERY-CONTACT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persists tenant-scoped, digest-only verified recovery-contact authority
         and exposes exact ACTIVE lookup plus atomic revocation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery_contact_registry.py
COLLABORATION / OWNERSHIP: A separately governed verifier/provisioner creates
                           R10E1 contact evidence; the password-recovery request
                           service may read ACTIVE authority. This registry owns
                           persistence only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.1.0-R10E19-SINGLE-ACTIVE-RECOVERY-CONTACT enforces at most one ACTIVE
           recovery contact per tenant/principal/channel and adds exact ACTIVE
           principal lookup so email-change verification can replace prior
           authority atomically without accumulating stale active contacts.
           v1.0.0-R10E2-VERIFIED-RECOVERY-CONTACT-REGISTRY establishes the
           verified_recovery_contacts collection, deterministic identity and
           ACTIVE-address uniqueness indexes, strict R10E1 hydration, exact
           tenant-scoped lookups, insert-only creation, and caller-session CAS
           revocation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Raw recovery addresses, passwords, recovery tokens,
                            JWTs, MFA secrets, and delivery credentials are never
                            accepted or persisted.
TENANT BOUNDARY: Every lookup and lifecycle mutation requires exact tenant scope;
                 cross-tenant absence is indistinguishable from absence.
AUTHORITY BOUNDARY: Durable verified-contact evidence only; no address
                    verification, token issuance, password reset, delivery,
                    HTTP, session, JWT, MFA, or rate-limit authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: Callers own ClientSession and transaction lifecycle; this
                      registry never starts, commits, aborts, or retries one.
FAIL-CLOSED POSTURE: Duplicate ACTIVE contact authority, corrupt persisted state,
                     stale revocation, and database failure are explicit errors.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Final, Mapping, NoReturn

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from .password_recovery_contact import (
    VerifiedRecoveryContact,
    VerifiedRecoveryContactChannel,
    VerifiedRecoveryContactError,
    VerifiedRecoveryContactStatus,
)

VERSION: Final[str] = "v1.1.0-R10E19-SINGLE-ACTIVE-RECOVERY-CONTACT"
COLLECTION: Final[str] = "verified_recovery_contacts"


class VerifiedRecoveryContactRegistryError(RuntimeError):
    """Base stable failure for verified-contact persistence boundaries."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class VerifiedRecoveryContactNotFoundError(VerifiedRecoveryContactRegistryError):
    """The requested contact authority is absent inside the supplied tenant."""


class VerifiedRecoveryContactAlreadyExistsError(VerifiedRecoveryContactRegistryError):
    """Insert-only creation collided with existing contact authority."""


class VerifiedRecoveryContactPersistedRecordInvalidError(VerifiedRecoveryContactRegistryError):
    """Persisted contact evidence cannot hydrate through the R10E1 domain."""


class VerifiedRecoveryContactLifecycleConflictError(VerifiedRecoveryContactRegistryError):
    """Atomic revocation lost to divergent or already-terminal state."""


class VerifiedRecoveryContactPersistenceError(VerifiedRecoveryContactRegistryError):
    """Canonical contact persistence could not complete an operation."""


def _target(collection: Any | None) -> Any:
    """Resolve an injected collection or the canonical Kernel database lazily."""

    if collection is not None:
        return collection
    from tools.eos.kernel import db as kernel_db

    database = kernel_db.get_database()
    if database is None:
        raise VerifiedRecoveryContactPersistenceError("RECOVERY_CONTACT_DATABASE_UNAVAILABLE")
    return database[COLLECTION]


def _session_kwargs(session: Any | None) -> dict[str, Any]:
    """Forward exactly one caller-owned session when supplied."""

    return {} if session is None else {"session": session}


def _hydrate(row: Mapping[str, Any]) -> VerifiedRecoveryContact:
    """Hydrate persisted state only through R10E1 and reject corruption."""

    try:
        payload = dict(row)
        payload.pop("_id", None)
        return VerifiedRecoveryContact.from_document(payload)
    except (TypeError, ValueError, VerifiedRecoveryContactError) as error:
        raise VerifiedRecoveryContactPersistedRecordInvalidError(
            "RECOVERY_CONTACT_PERSISTED_RECORD_INVALID"
        ) from error


def _validate_lookup(tenant_id: object, address_digest: object) -> tuple[str, str]:
    """Validate bounded tenant and digest lookup values without raw addresses."""

    if not isinstance(tenant_id, str) or not tenant_id.strip() or tenant_id != tenant_id.strip():
        raise VerifiedRecoveryContactNotFoundError("RECOVERY_CONTACT_NOT_FOUND")
    if (
        not isinstance(address_digest, str)
        or len(address_digest) != 128
        or address_digest != address_digest.lower()
    ):
        raise VerifiedRecoveryContactNotFoundError("RECOVERY_CONTACT_NOT_FOUND")
    try:
        if len(bytes.fromhex(address_digest)) != 64:
            raise ValueError
    except ValueError as error:
        raise VerifiedRecoveryContactNotFoundError("RECOVERY_CONTACT_NOT_FOUND") from error
    return tenant_id, address_digest


def _revoke_failure(
    source: Any,
    contact: VerifiedRecoveryContact,
    *,
    session: Any | None,
) -> NoReturn:
    """Classify a failed revocation without broadening tenant scope."""

    try:
        current = source.find_one(
            {"tenant_id": contact.tenant_id, "contact_id": contact.contact_id},
            **_session_kwargs(session),
        )
    except PyMongoError as error:
        raise VerifiedRecoveryContactPersistenceError("RECOVERY_CONTACT_READ_FAILED") from error
    if current is None:
        raise VerifiedRecoveryContactNotFoundError("RECOVERY_CONTACT_NOT_FOUND")
    persisted = _hydrate(current)
    if (
        persisted.principal_id != contact.principal_id
        or persisted.channel is not contact.channel
        or persisted.address_digest != contact.address_digest
        or persisted.verified_at != contact.verified_at
    ):
        raise VerifiedRecoveryContactLifecycleConflictError(
            "RECOVERY_CONTACT_BINDING_CONFLICT"
        )
    if persisted.status is VerifiedRecoveryContactStatus.REVOKED:
        raise VerifiedRecoveryContactLifecycleConflictError("RECOVERY_CONTACT_REVOKED")
    raise VerifiedRecoveryContactLifecycleConflictError("RECOVERY_CONTACT_LIFECYCLE_CONFLICT")


class VerifiedRecoveryContactRegistry:
    """Persist and read R10E1 verified recovery-contact authority.

    The registry accepts an injected PyMongo collection for deterministic tests.
    When absent, it resolves the canonical Kernel database lazily. It never
    receives a raw recovery address and never owns verification, delivery,
    authentication, or transaction lifecycle.
    """

    def __init__(self, collection: Any | None = None) -> None:
        """Bind one optional collection dependency without opening Mongo."""

        self._collection = collection

    def _source(self) -> Any:
        """Return the injected or canonical collection at operation time."""

        return _target(self._collection)

    def ensure_indexes(self) -> None:
        """Create stable identity, ACTIVE-address, and principal lookup indexes.

        A partial unique index permits historical REVOKED evidence while proving
        that at most one ACTIVE authority exists for a tenant/channel/digest.
        Index creation occurs outside transactions and never mutates contact
        lifecycle state.
        """

        source = self._source()
        try:
            source.create_index(
                [("contact_id", ASCENDING)],
                unique=True,
                name="verified_recovery_contact_identity_unique",
            )
            source.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("channel", ASCENDING),
                    ("address_digest", ASCENDING),
                ],
                unique=True,
                partialFilterExpression={
                    "status": VerifiedRecoveryContactStatus.ACTIVE.value,
                },
                name="verified_recovery_contact_active_address_unique",
            )
            source.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("principal_id", ASCENDING),
                    ("channel", ASCENDING),
                ],
                unique=True,
                partialFilterExpression={
                    "status": VerifiedRecoveryContactStatus.ACTIVE.value,
                },
                name="verified_recovery_contact_active_principal_unique",
            )
            source.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("principal_id", ASCENDING),
                    ("status", ASCENDING),
                    ("verified_at", ASCENDING),
                ],
                unique=False,
                name="verified_recovery_contact_tenant_principal_status",
            )
        except PyMongoError as error:
            raise VerifiedRecoveryContactPersistenceError(
                "RECOVERY_CONTACT_INDEX_CREATION_FAILED"
            ) from error

    def create(
        self,
        contact: VerifiedRecoveryContact,
        *,
        session: Any | None = None,
    ) -> VerifiedRecoveryContact:
        """Insert exactly one ACTIVE verified-contact authority.

        Creation is insert-only. Duplicate identity or duplicate ACTIVE address
        authority is a conflict, never implicit replay success. The caller owns
        any surrounding verification transaction and must already possess the
        verification evidence represented by R10E1.
        """

        if not isinstance(contact, VerifiedRecoveryContact):
            raise VerifiedRecoveryContactRegistryError("RECOVERY_CONTACT_CREATE_INVALID")
        if contact.status is not VerifiedRecoveryContactStatus.ACTIVE:
            raise VerifiedRecoveryContactRegistryError(
                "RECOVERY_CONTACT_CREATE_REQUIRES_ACTIVE"
            )
        source = self._source()
        try:
            source.insert_one(contact.to_document(), **_session_kwargs(session))
            return contact
        except DuplicateKeyError as error:
            try:
                identity = source.find_one(
                    {"tenant_id": contact.tenant_id, "contact_id": contact.contact_id},
                    **_session_kwargs(session),
                )
                active = source.find_one(
                    {
                        "tenant_id": contact.tenant_id,
                        "channel": contact.channel.value,
                        "address_digest": contact.address_digest,
                        "status": VerifiedRecoveryContactStatus.ACTIVE.value,
                    },
                    **_session_kwargs(session),
                )
            except PyMongoError as read_error:
                raise VerifiedRecoveryContactPersistenceError(
                    "RECOVERY_CONTACT_DUPLICATE_CLASSIFICATION_FAILED"
                ) from read_error
            if identity is not None:
                raise VerifiedRecoveryContactAlreadyExistsError(
                    "RECOVERY_CONTACT_ID_DUPLICATE"
                ) from error
            if active is not None:
                raise VerifiedRecoveryContactAlreadyExistsError(
                    "RECOVERY_CONTACT_ACTIVE_ADDRESS_DUPLICATE"
                ) from error
            raise VerifiedRecoveryContactAlreadyExistsError(
                "RECOVERY_CONTACT_DUPLICATE_CONFLICT"
            ) from error
        except PyMongoError as error:
            raise VerifiedRecoveryContactPersistenceError(
                "RECOVERY_CONTACT_CREATE_FAILED"
            ) from error

    def get_active_by_address_digest(
        self,
        *,
        tenant_id: str,
        channel: VerifiedRecoveryContactChannel,
        address_digest: str,
        session: Any | None = None,
    ) -> VerifiedRecoveryContact | None:
        """Read exact ACTIVE contact authority for one tenant/channel/digest.

        Raw addresses are not accepted here. Absence is tenant-scoped and does
        not reveal whether a matching digest exists under another tenant.
        """

        tenant, digest = _validate_lookup(tenant_id, address_digest)
        if not isinstance(channel, VerifiedRecoveryContactChannel):
            raise VerifiedRecoveryContactNotFoundError("RECOVERY_CONTACT_NOT_FOUND")
        try:
            row = self._source().find_one(
                {
                    "tenant_id": tenant,
                    "channel": channel.value,
                    "address_digest": digest,
                    "status": VerifiedRecoveryContactStatus.ACTIVE.value,
                },
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise VerifiedRecoveryContactPersistenceError(
                "RECOVERY_CONTACT_READ_FAILED"
            ) from error
        if row is None:
            return None
        contact = _hydrate(row)
        if contact.status is not VerifiedRecoveryContactStatus.ACTIVE:
            raise VerifiedRecoveryContactPersistedRecordInvalidError(
                "RECOVERY_CONTACT_STATUS_MISMATCH"
            )
        return contact

    def get_active_by_principal(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        channel: VerifiedRecoveryContactChannel = VerifiedRecoveryContactChannel.EMAIL,
        session: Any | None = None,
    ) -> VerifiedRecoveryContact | None:
        """Read the sole ACTIVE contact authority for one tenant/principal/channel.

        This lookup never accepts an address and therefore cannot infer another
        principal from contact material. The partial unique index guarantees at
        most one ACTIVE result for the binding.
        """

        if (
            not isinstance(tenant_id, str)
            or not tenant_id.strip()
            or tenant_id != tenant_id.strip()
            or not isinstance(principal_id, str)
            or not principal_id.strip()
            or principal_id != principal_id.strip()
            or not isinstance(channel, VerifiedRecoveryContactChannel)
        ):
            raise VerifiedRecoveryContactNotFoundError("RECOVERY_CONTACT_NOT_FOUND")
        try:
            row = self._source().find_one(
                {
                    "tenant_id": tenant_id,
                    "principal_id": principal_id,
                    "channel": channel.value,
                    "status": VerifiedRecoveryContactStatus.ACTIVE.value,
                },
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise VerifiedRecoveryContactPersistenceError(
                "RECOVERY_CONTACT_READ_FAILED"
            ) from error
        return None if row is None else _hydrate(row)

    def revoke(
        self,
        contact: VerifiedRecoveryContact,
        revoked_at: datetime,
        *,
        session: Any | None = None,
    ) -> VerifiedRecoveryContact:
        """Atomically revoke one exact ACTIVE contact authority.

        The caller owns the session/transaction. Revocation cannot alter a user,
        password, recovery capability, session, token, MFA factor, or delivery
        system.
        """

        if not isinstance(contact, VerifiedRecoveryContact):
            raise VerifiedRecoveryContactRegistryError("RECOVERY_CONTACT_REVOKE_INVALID")
        replacement = contact.revoke(revoked_at)
        source = self._source()
        query = {
            "tenant_id": contact.tenant_id,
            "contact_id": contact.contact_id,
            "principal_id": contact.principal_id,
            "channel": contact.channel.value,
            "address_digest": contact.address_digest,
            "verified_at": contact.verified_at.isoformat(),
            "status": VerifiedRecoveryContactStatus.ACTIVE.value,
            "revoked_at": None,
        }
        try:
            row = source.find_one_and_update(
                query,
                {
                    "$set": {
                        "status": replacement.status.value,
                        "revoked_at": replacement.revoked_at.isoformat()
                        if replacement.revoked_at is not None
                        else None,
                    }
                },
                return_document=ReturnDocument.AFTER,
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise VerifiedRecoveryContactPersistenceError(
                "RECOVERY_CONTACT_REVOKE_FAILED"
            ) from error
        if row is None:
            _revoke_failure(source, contact, session=session)
        return _hydrate(row)


__all__ = [
    "COLLECTION",
    "VERSION",
    "VerifiedRecoveryContactAlreadyExistsError",
    "VerifiedRecoveryContactLifecycleConflictError",
    "VerifiedRecoveryContactNotFoundError",
    "VerifiedRecoveryContactPersistedRecordInvalidError",
    "VerifiedRecoveryContactPersistenceError",
    "VerifiedRecoveryContactRegistry",
    "VerifiedRecoveryContactRegistryError",
]


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: password_recovery_contact_registry.py
# VERSION: v1.1.0-R10E19-SINGLE-ACTIVE-RECOVERY-CONTACT
# AUTHORITY BOUNDARY: durable digest-only verified recovery-contact evidence
# TENANT POSTURE: exact tenant scope; ACTIVE lookup never broadens across tenants
# FAIL-CLOSED POSTURE: duplicate, corrupt, stale, and persistence failure rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
