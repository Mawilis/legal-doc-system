"""Durable registry for canonical WILSY OS recovery-contact authority.

TITLE: WILSY OS Recovery Contact Authority Registry
VERSION: v1.0.0-R10E10-RECOVERY-CONTACT-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persists and atomically transitions one explicit recovery-contact
         authority per tenant/principal/channel active slot without inferring
         verification from login email or account existence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/recovery_contact_registry.py
COLLABORATION / OWNERSHIP: recovery_contact.py owns immutable lifecycle truth;
                           verification services own ceremonies; recovery request
                           orchestration may read VERIFIED contact evidence only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E10-RECOVERY-CONTACT-REGISTRY — Establishes tenant-scoped persistence,
    strict hydration, deterministic indexes, one non-revoked EMAIL contact slot
    per principal, caller-session propagation, exact VERIFIED resolution, and
    revision-bound verify/revoke compare-and-set transitions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Recovery addresses are bounded PII; no password,
                            recovery bearer, credential hash, MFA secret, session,
                            refresh token, JWT, or delivery credential is accepted.
TENANT BOUNDARY: Every lookup and mutation requires exact tenant/principal binding.
AUTHORITY BOUNDARY: Durable recovery-contact evidence only; no verification
                    ceremony, recovery issuance, delivery, login, or password authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Caller owns ClientSession and transaction lifecycle; this
                      registry forwards supplied sessions unchanged.
FAIL-CLOSED POSTURE: Duplicate active slots, corrupt rows, stale revisions,
                     cross-tenant lookups, ambiguous state, and persistence
                     failures never become verified recovery authority.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Final, Mapping, NoReturn

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from .recovery_contact import (
    RecoveryContactAuthority,
    RecoveryContactAuthorityError,
    RecoveryContactChannel,
    RecoveryContactStatus,
    RecoveryContactVerificationMethod,
)


VERSION: Final[str] = "v1.0.0-R10E10-RECOVERY-CONTACT-REGISTRY"
COLLECTION: Final[str] = "recovery_contact_authorities"
_ACTIVE_SLOT_FIELD: Final[str] = "_active_slot"

INDEX_DEFINITIONS: Final[
    tuple[tuple[tuple[tuple[str, int], ...], bool, str], ...]
] = (
    ((("contact_id", ASCENDING),), True, "recovery_contact_identity_unique"),
    (
        (
            ("tenant_id", ASCENDING),
            ("principal_id", ASCENDING),
            (_ACTIVE_SLOT_FIELD, ASCENDING),
        ),
        True,
        "recovery_contact_tenant_principal_active_slot_unique",
    ),
    (
        (
            ("tenant_id", ASCENDING),
            ("principal_id", ASCENDING),
            ("status", ASCENDING),
            ("channel", ASCENDING),
        ),
        False,
        "recovery_contact_tenant_principal_status_channel",
    ),
)


class RecoveryContactRegistryError(RuntimeError):
    """Base code-only persistence failure for recovery-contact authority."""

    def __init__(self, code: str) -> None:
        if not isinstance(code, str) or not code:
            raise TypeError("recovery contact registry code must be non-empty")
        self.code = code
        super().__init__(code)


class RecoveryContactNotFoundError(RecoveryContactRegistryError):
    """Requested contact does not exist within the supplied tenant scope."""


class RecoveryContactAlreadyExistsError(RecoveryContactRegistryError):
    """Insert collided with existing identity or current principal/channel slot."""


class RecoveryContactPersistedRecordInvalidError(RecoveryContactRegistryError):
    """Persisted contact cannot be hydrated through the canonical domain."""


class RecoveryContactLifecycleConflictError(RecoveryContactRegistryError):
    """Atomic contact lifecycle transition lost or observed conflicting state."""


class RecoveryContactPersistenceError(RecoveryContactRegistryError):
    """Mongo persistence failed at the recovery-contact boundary."""


def _target(collection: Any | None) -> Any:
    """Resolve injected collection or canonical Kernel database lazily."""

    if collection is not None:
        return collection
    from tools.eos.kernel import db as kernel_db

    database = kernel_db.get_database()
    if database is None:
        raise RecoveryContactPersistenceError("RECOVERY_CONTACT_DATABASE_UNAVAILABLE")
    return database[COLLECTION]


def _session_kwargs(session: Any | None) -> dict[str, Any]:
    """Forward one caller-owned session exactly; never create a session."""

    return {} if session is None else {"session": session}


def _active_slot(contact: RecoveryContactAuthority) -> str:
    """Return deterministic uniqueness metadata for current vs historical rows."""

    if contact.status is RecoveryContactStatus.REVOKED:
        return f"REVOKED:{contact.contact_id}"
    return contact.channel.value


def _document(contact: RecoveryContactAuthority) -> dict[str, Any]:
    """Persist exact domain serialization plus deterministic uniqueness metadata."""

    payload = contact.to_document()
    payload[_ACTIVE_SLOT_FIELD] = _active_slot(contact)
    return payload


def _hydrate(row: Mapping[str, Any]) -> RecoveryContactAuthority:
    """Hydrate strictly and reject divergent registry-only metadata."""

    try:
        payload = dict(row)
        payload.pop("_id", None)
        active_slot = payload.pop(_ACTIVE_SLOT_FIELD)
        contact = RecoveryContactAuthority.from_document(payload)
        if active_slot != _active_slot(contact):
            raise ValueError("RECOVERY_CONTACT_ACTIVE_SLOT_MISMATCH")
        return contact
    except RecoveryContactPersistedRecordInvalidError:
        raise
    except (KeyError, TypeError, ValueError, RecoveryContactAuthorityError) as error:
        raise RecoveryContactPersistedRecordInvalidError(
            "RECOVERY_CONTACT_PERSISTED_RECORD_INVALID"
        ) from error


def _identity_query(contact: RecoveryContactAuthority) -> dict[str, Any]:
    """Build complete immutable snapshot binding for lifecycle compare-and-set."""

    return {
        "contact_id": contact.contact_id,
        "tenant_id": contact.tenant_id,
        "principal_id": contact.principal_id,
        "channel": contact.channel.value,
        "address": contact.address,
        "status": contact.status.value,
        "revision": contact.revision,
        "created_at": contact.created_at.isoformat(),
        "verified_at": None if contact.verified_at is None else contact.verified_at.isoformat(),
        "verification_method": (
            None if contact.verification_method is None else contact.verification_method.value
        ),
        "revoked_at": None if contact.revoked_at is None else contact.revoked_at.isoformat(),
        _ACTIVE_SLOT_FIELD: _active_slot(contact),
    }


def _transition_failure(
    source: Any,
    contact: RecoveryContactAuthority,
    *,
    session: Any | None,
) -> NoReturn:
    """Classify failed CAS using tenant-scoped identity without leaking other tenants."""

    try:
        row = source.find_one(
            {"tenant_id": contact.tenant_id, "contact_id": contact.contact_id},
            **_session_kwargs(session),
        )
    except PyMongoError as error:
        raise RecoveryContactPersistenceError("RECOVERY_CONTACT_READ_FAILED") from error
    if row is None:
        raise RecoveryContactNotFoundError("RECOVERY_CONTACT_NOT_FOUND")
    persisted = _hydrate(row)
    if (
        persisted.principal_id != contact.principal_id
        or persisted.channel is not contact.channel
        or persisted.address != contact.address
        or persisted.created_at != contact.created_at
    ):
        raise RecoveryContactLifecycleConflictError(
            "RECOVERY_CONTACT_BINDING_CONFLICT"
        )
    if persisted.revision != contact.revision or persisted.status is not contact.status:
        raise RecoveryContactLifecycleConflictError(
            "RECOVERY_CONTACT_STALE_REVISION"
        )
    raise RecoveryContactLifecycleConflictError("RECOVERY_CONTACT_LIFECYCLE_CONFLICT")


class RecoveryContactAuthorityRegistry:
    """Persist and atomically transition explicit recovery-contact evidence.

    The registry never infers verification from users, authentication, MFA,
    membership, invitations, or email delivery. It persists only domain values
    supplied by an owning verification/migration service and exposes VERIFIED
    evidence for downstream recovery issuance.
    """

    def __init__(self, collection: Any | None = None) -> None:
        """Bind a collection dependency without opening Mongo or creating indexes."""

        self._collection = collection

    def _source(self) -> Any:
        """Return injected or canonical collection at operation time."""

        return _target(self._collection)

    def ensure_indexes(self) -> None:
        """Create deterministic uniqueness/query indexes outside transactions."""

        source = self._source()
        try:
            for keys, unique, name in INDEX_DEFINITIONS:
                source.create_index(list(keys), unique=unique, name=name)
        except PyMongoError as error:
            raise RecoveryContactPersistenceError(
                "RECOVERY_CONTACT_INDEX_CREATION_FAILED"
            ) from error

    def create_pending(
        self,
        contact: RecoveryContactAuthority,
        *,
        session: Any | None = None,
    ) -> RecoveryContactAuthority:
        """Insert one PENDING contact into the principal's non-revoked channel slot."""

        if not isinstance(contact, RecoveryContactAuthority):
            raise RecoveryContactRegistryError("RECOVERY_CONTACT_CREATE_INVALID")
        if contact.status is not RecoveryContactStatus.PENDING:
            raise RecoveryContactRegistryError("RECOVERY_CONTACT_CREATE_REQUIRES_PENDING")
        source = self._source()
        try:
            source.insert_one(_document(contact), **_session_kwargs(session))
            return contact
        except DuplicateKeyError as error:
            try:
                identity = source.find_one(
                    {"tenant_id": contact.tenant_id, "contact_id": contact.contact_id},
                    **_session_kwargs(session),
                )
                slot = source.find_one(
                    {
                        "tenant_id": contact.tenant_id,
                        "principal_id": contact.principal_id,
                        _ACTIVE_SLOT_FIELD: contact.channel.value,
                    },
                    **_session_kwargs(session),
                )
            except PyMongoError as read_error:
                raise RecoveryContactPersistenceError(
                    "RECOVERY_CONTACT_DUPLICATE_CLASSIFICATION_FAILED"
                ) from read_error
            if identity is not None:
                raise RecoveryContactAlreadyExistsError(
                    "RECOVERY_CONTACT_ID_DUPLICATE"
                ) from error
            if slot is not None:
                raise RecoveryContactAlreadyExistsError(
                    "RECOVERY_CONTACT_ACTIVE_SLOT_OCCUPIED"
                ) from error
            raise RecoveryContactAlreadyExistsError(
                "RECOVERY_CONTACT_DUPLICATE_CONFLICT"
            ) from error
        except PyMongoError as error:
            raise RecoveryContactPersistenceError(
                "RECOVERY_CONTACT_CREATE_FAILED"
            ) from error

    def get_by_contact_id(
        self,
        *,
        tenant_id: str,
        contact_id: str,
        session: Any | None = None,
    ) -> RecoveryContactAuthority | None:
        """Read one exact tenant/contact identity or return scoped absence."""

        if (
            not isinstance(tenant_id, str)
            or not tenant_id.strip()
            or not isinstance(contact_id, str)
            or not contact_id.strip()
        ):
            raise RecoveryContactNotFoundError("RECOVERY_CONTACT_NOT_FOUND")
        try:
            row = self._source().find_one(
                {"tenant_id": tenant_id, "contact_id": contact_id},
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise RecoveryContactPersistenceError("RECOVERY_CONTACT_READ_FAILED") from error
        return None if row is None else _hydrate(row)

    def get_current_for_principal(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        channel: RecoveryContactChannel = RecoveryContactChannel.EMAIL,
        session: Any | None = None,
    ) -> RecoveryContactAuthority | None:
        """Read the sole non-revoked contact slot for one tenant/principal/channel."""

        if (
            not isinstance(tenant_id, str)
            or not tenant_id.strip()
            or not isinstance(principal_id, str)
            or not principal_id.strip()
            or not isinstance(channel, RecoveryContactChannel)
        ):
            raise RecoveryContactRegistryError("RECOVERY_CONTACT_PRINCIPAL_QUERY_INVALID")
        try:
            rows = list(
                self._source().find(
                    {
                        "tenant_id": tenant_id,
                        "principal_id": principal_id,
                        _ACTIVE_SLOT_FIELD: channel.value,
                    },
                    **_session_kwargs(session),
                ).limit(2)
            )
        except PyMongoError as error:
            raise RecoveryContactPersistenceError("RECOVERY_CONTACT_READ_FAILED") from error
        if not rows:
            return None
        if len(rows) != 1:
            raise RecoveryContactPersistedRecordInvalidError(
                "RECOVERY_CONTACT_ACTIVE_SLOT_AMBIGUOUS"
            )
        contact = _hydrate(rows[0])
        if contact.status not in {RecoveryContactStatus.PENDING, RecoveryContactStatus.VERIFIED}:
            raise RecoveryContactPersistedRecordInvalidError(
                "RECOVERY_CONTACT_ACTIVE_SLOT_STATUS_INVALID"
            )
        return contact

    def resolve_verified_for_principal(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        observed_at: datetime,
        session: Any | None = None,
    ) -> RecoveryContactAuthority | None:
        """Return exact VERIFIED EMAIL evidence or scoped absence.

        PENDING, REVOKED, absent, and stale/corrupt states never become delivery
        authority. The caller may use the returned address as a recovery
        transport destination only after its own principal/lifecycle admission.
        """

        current = self.get_current_for_principal(
            tenant_id=tenant_id,
            principal_id=principal_id,
            channel=RecoveryContactChannel.EMAIL,
            session=session,
        )
        if current is None or current.status is not RecoveryContactStatus.VERIFIED:
            return None
        try:
            return current.require_verified(observed_at=observed_at)
        except RecoveryContactAuthorityError as error:
            raise RecoveryContactPersistedRecordInvalidError(
                "RECOVERY_CONTACT_VERIFIED_EVIDENCE_INVALID"
            ) from error

    def verify(
        self,
        contact: RecoveryContactAuthority,
        *,
        verified_at: datetime,
        method: RecoveryContactVerificationMethod,
        session: Any | None = None,
    ) -> RecoveryContactAuthority:
        """Atomically persist one PENDING -> VERIFIED transition by exact revision."""

        if not isinstance(contact, RecoveryContactAuthority):
            raise RecoveryContactRegistryError("RECOVERY_CONTACT_VERIFY_INVALID")
        try:
            replacement = contact.verify(verified_at=verified_at, method=method)
        except RecoveryContactAuthorityError as error:
            raise RecoveryContactLifecycleConflictError(error.code) from error
        source = self._source()
        try:
            row = source.find_one_and_replace(
                _identity_query(contact),
                _document(replacement),
                return_document=ReturnDocument.AFTER,
                **_session_kwargs(session),
            )
        except DuplicateKeyError as error:
            raise RecoveryContactLifecycleConflictError(
                "RECOVERY_CONTACT_VERIFY_SLOT_CONFLICT"
            ) from error
        except PyMongoError as error:
            raise RecoveryContactPersistenceError(
                "RECOVERY_CONTACT_VERIFY_FAILED"
            ) from error
        if row is None:
            _transition_failure(source, contact, session=session)
        persisted = _hydrate(row)
        if persisted != replacement:
            raise RecoveryContactPersistedRecordInvalidError(
                "RECOVERY_CONTACT_VERIFY_READBACK_MISMATCH"
            )
        return persisted

    def revoke(
        self,
        contact: RecoveryContactAuthority,
        *,
        revoked_at: datetime,
        session: Any | None = None,
    ) -> RecoveryContactAuthority:
        """Atomically persist one PENDING/VERIFIED -> REVOKED transition."""

        if not isinstance(contact, RecoveryContactAuthority):
            raise RecoveryContactRegistryError("RECOVERY_CONTACT_REVOKE_INVALID")
        try:
            replacement = contact.revoke(revoked_at=revoked_at)
        except RecoveryContactAuthorityError as error:
            raise RecoveryContactLifecycleConflictError(error.code) from error
        source = self._source()
        try:
            row = source.find_one_and_replace(
                _identity_query(contact),
                _document(replacement),
                return_document=ReturnDocument.AFTER,
                **_session_kwargs(session),
            )
        except PyMongoError as error:
            raise RecoveryContactPersistenceError(
                "RECOVERY_CONTACT_REVOKE_FAILED"
            ) from error
        if row is None:
            _transition_failure(source, contact, session=session)
        persisted = _hydrate(row)
        if persisted != replacement:
            raise RecoveryContactPersistedRecordInvalidError(
                "RECOVERY_CONTACT_REVOKE_READBACK_MISMATCH"
            )
        return persisted


__all__ = [
    "COLLECTION",
    "INDEX_DEFINITIONS",
    "RecoveryContactAlreadyExistsError",
    "RecoveryContactAuthorityRegistry",
    "RecoveryContactLifecycleConflictError",
    "RecoveryContactNotFoundError",
    "RecoveryContactPersistedRecordInvalidError",
    "RecoveryContactPersistenceError",
    "RecoveryContactRegistryError",
    "VERSION",
]


# ARTIFACT: tools/eos/saas/auth/recovery_contact_registry.py
# VERSION: v1.0.0-R10E10-RECOVERY-CONTACT-REGISTRY
# AUTHORITY BOUNDARY: durable explicit recovery-contact evidence only
# TENANT POSTURE: exact tenant/principal/channel scope with one non-revoked EMAIL slot
# FAIL-CLOSED POSTURE: duplicate, corrupt, stale, ambiguous, and cross-tenant state never verifies recovery contact
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
# END OF WILSY OS SOVEREIGN ARTIFACT
