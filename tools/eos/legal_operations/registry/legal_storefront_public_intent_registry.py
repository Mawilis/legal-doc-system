"""WILSY OS durable Legal Storefront public-intent registry.

TITLE: Legal Storefront Public Intent Registry
VERSION: v1.0.0-L8-9B-LEGAL-STOREFRONT-PUBLIC-INTENT-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable L8-9A pre-tenant Legal Storefront public intents
         append-only with exact replay, strict corruption rejection,
         caller-owned active Mongo transactions and no invented tenant,
         retention, subscription, Legal lifecycle or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_storefront_public_intent_registry.py
COLLABORATION / OWNERSHIP: L8-9A owns immutable public-intent meaning and
                            SHA3-512 integrity. This registry owns only durable
                            append/replay and exact opaque-intent reads.
                            Identity verification, tenant genesis, retention,
                            deletion, CRM admission, Legal Operations admission,
                            subscription, entitlement and public HTTP remain
                            separate governed owners.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-9B-LEGAL-STOREFRONT-PUBLIC-INTENT-REGISTRY
           establishes the legal_storefront_public_intents collection,
           globally unique server-issued intent identity and exact semantic
           fingerprint, append-only replay, strict hydration, active
           caller-transaction enforcement, duplicate-race retry signaling,
           no email/organization lookup surface and no TTL/delete authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists the bounded L8-9A organization/contact
                             request evidence only. No password, credential,
                             secret, API key, authenticated principal, payment
                             coordinate or provider credential is accepted.
TENANT BOUNDARY: Pre-tenant by definition. No tenant_id is stored, queried,
                 inferred or accepted. Persistence cannot establish tenant
                 scope and this registry exposes no tenant existence oracle.
AUTHORITY BOUNDARY: Append-only public-intent durability and exact opaque-intent
                    reads only. No identity verification, user creation,
                    membership, role, tenant genesis, plan selection,
                    subscription, entitlement, LegalInstruction, CaseMatter,
                    ProcessDocument, billing, payment or settlement authority.
TRANSACTION BOUNDARY: Caller supplies and owns every active Mongo transaction.
                      This registry never starts, commits, aborts, retries or
                      reconciles transactions. Duplicate races require caller
                      abort and fresh whole-transaction retry.
RETENTION BOUNDARY: This registry has no delete, purge, expiry or TTL authority.
                    Durable intent evidence remains until a separately governed
                    retention/privacy authority is certified.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority.
FAIL-CLOSED DECLARATION: Missing transaction, malformed domain value,
                         persisted-shape drift, fingerprint corruption,
                         divergent replay, duplicate race or Mongo failure
                         rejects without repair or authority expansion.
"""

from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_storefront_public_intent import (
    LegalStorefrontPublicIntent,
    LegalStorefrontPublicIntentError,
)


VERSION: Final[str] = (
    "v1.0.0-L8-9B-LEGAL-STOREFRONT-PUBLIC-INTENT-REGISTRY"
)
COLLECTION: Final[str] = "legal_storefront_public_intents"

INDEX_INTENT_ID: Final[str] = (
    "legal_storefront_public_intent_id_unique"
)
INDEX_FINGERPRINT: Final[str] = (
    "legal_storefront_public_intent_fingerprint_unique"
)

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_FINGERPRINT: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")

_REQUIRED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "intent_version",
        "intent_kind",
        "intent_id",
        "organization_name",
        "contact_email",
        "industry",
        "region",
        "submitted_at",
        "fingerprint",
    }
)
_PERSISTED_FIELDS: Final[frozenset[str]] = frozenset(
    set(_REQUIRED_FIELDS) | {"_id"}
)


class LegalStorefrontPublicIntentRegistryError(RuntimeError):
    """Base non-sensitive fail-closed L8-9B registry error.

    This error grants no identity, tenant, Legal Operations, commercial,
    retention, deletion or financial authority.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalStorefrontPublicIntentRegistryConflictError(
    LegalStorefrontPublicIntentRegistryError
):
    """An immutable replay identity collides with divergent intent evidence."""


class LegalStorefrontPublicIntentRegistryTransactionRequiredError(
    LegalStorefrontPublicIntentRegistryError
):
    """Caller failed to supply one active Mongo transaction."""


class LegalStorefrontPublicIntentRegistryRetryTransactionError(
    LegalStorefrontPublicIntentRegistryError
):
    """A duplicate race requires abort and fresh whole-transaction retry."""


class LegalStorefrontPublicIntentRegistryPersistenceError(
    LegalStorefrontPublicIntentRegistryError
):
    """Mongo persistence or read infrastructure failed closed."""


def _fail(code: str) -> NoReturn:
    """Raise one bounded registry validation failure."""
    raise LegalStorefrontPublicIntentRegistryError(code)


def _identity(value: object) -> str:
    """Validate one opaque server-issued public-intent identity."""
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail("L8_9B_INTENT_ID_INVALID")
    return value


def _fingerprint(value: object) -> str:
    """Validate one lowercase SHA3-512 semantic fingerprint."""
    if (
        not isinstance(value, str)
        or _FINGERPRINT.fullmatch(value) is None
    ):
        _fail("L8_9B_FINGERPRINT_INVALID")
    return value


def _active_transaction(session: Any) -> Any:
    """Require one caller-owned active Mongo transaction."""
    if session is None:
        raise LegalStorefrontPublicIntentRegistryTransactionRequiredError(
            "L8_9B_TRANSACTION_REQUIRED"
        )

    active = getattr(session, "in_transaction", False)
    if callable(active):
        active = active()

    if active is not True:
        raise LegalStorefrontPublicIntentRegistryTransactionRequiredError(
            "L8_9B_TRANSACTION_REQUIRED"
        )

    return session


def _target(collection: Any) -> Any:
    """Require an injected Mongo collection without opening infrastructure."""
    if collection is None:
        _fail("L8_9B_COLLECTION_REQUIRED")
    return collection


def _raise_mongo(error: PyMongoError) -> NoReturn:
    """Map Mongo failures to one non-sensitive persistence failure."""
    raise LegalStorefrontPublicIntentRegistryPersistenceError(
        "L8_9B_PERSISTENCE_UNAVAILABLE"
    ) from error


def _hydrate(
    row: Mapping[str, object],
) -> LegalStorefrontPublicIntent:
    """Strictly hydrate one durable L8-9A intent and reject stored drift."""
    try:
        if (
            not isinstance(row, Mapping)
            or not set(row).issubset(_PERSISTED_FIELDS)
            or not _REQUIRED_FIELDS.issubset(row)
        ):
            _fail("L8_9B_CORRUPT_INTENT")

        payload = {
            field: row[field]
            for field in _REQUIRED_FIELDS
        }
        return LegalStorefrontPublicIntent.from_dict(payload)
    except LegalStorefrontPublicIntentRegistryError:
        raise
    except (
        KeyError,
        TypeError,
        ValueError,
        LegalStorefrontPublicIntentError,
    ) as error:
        raise LegalStorefrontPublicIntentRegistryError(
            "L8_9B_CORRUPT_INTENT"
        ) from error


def ensure_indexes(collection: Any) -> None:
    """Create immutable identity indexes and deliberately create no TTL.

    Index creation is an infrastructure/setup operation and does not itself
    persist public intent, authenticate a user, create tenant scope, select a
    commercial plan, or establish any Legal Operations lifecycle fact.
    """
    target = _target(collection)

    try:
        target.create_index(
            [("intent_id", ASCENDING)],
            name=INDEX_INTENT_ID,
            unique=True,
        )
        target.create_index(
            [("fingerprint", ASCENDING)],
            name=INDEX_FINGERPRINT,
            unique=True,
        )
    except PyMongoError as error:
        _raise_mongo(error)


class LegalStorefrontPublicIntentRegistry:
    """Append-only pre-tenant durability for L8-9A public-intent evidence.

    All operational reads/writes require a caller-owned active transaction.
    The registry exposes exact opaque-intent lookup only and intentionally
    exposes no email, organization, industry, region, tenant or public search
    surface. It owns neither retention/deletion nor downstream admission.
    """

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        """Bind one injected collection without creating authority or indexes."""
        self._collection = _target(collection)

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create deterministic L8-9B indexes outside operational transactions."""
        ensure_indexes(collection)

    def create_or_replay(
        self,
        intent: LegalStorefrontPublicIntent,
        *,
        session: Any,
    ) -> LegalStorefrontPublicIntent:
        """Persist one immutable public intent or return its exact replay.

        Exact replay is keyed by the server-issued ``intent_id``. A persisted
        fingerprint collision is also checked before insertion so corrupted or
        impossible duplicate evidence cannot silently create a second row.

        Any divergent identity/fingerprint evidence fails closed. Duplicate-key
        races are surfaced as whole-transaction retry requirements rather than
        being reconciled inside the current transaction.

        This method never creates identity, tenant, subscription, entitlement,
        Legal lifecycle, billing, payment, settlement or retention authority.
        """
        tx = _active_transaction(session)

        if type(intent) is not LegalStorefrontPublicIntent:
            _fail("L8_9B_INTENT_REQUIRED")

        try:
            intent.__post_init__()
        except LegalStorefrontPublicIntentError as error:
            raise LegalStorefrontPublicIntentRegistryError(
                "L8_9B_INTENT_INVALID"
            ) from error

        intent_id = _identity(intent.intent_id)
        fingerprint = _fingerprint(intent.fingerprint)

        try:
            existing = self._collection.find_one(
                {"intent_id": intent_id},
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)

        if existing is not None:
            persisted = _hydrate(existing)
            if persisted != intent:
                raise LegalStorefrontPublicIntentRegistryConflictError(
                    "L8_9B_DIVERGENT_INTENT_IDENTITY"
                )
            return persisted

        try:
            fingerprint_existing = self._collection.find_one(
                {"fingerprint": fingerprint},
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)

        if fingerprint_existing is not None:
            persisted = _hydrate(fingerprint_existing)
            if persisted != intent:
                raise LegalStorefrontPublicIntentRegistryConflictError(
                    "L8_9B_DIVERGENT_FINGERPRINT"
                )
            return persisted

        try:
            self._collection.insert_one(
                intent.to_dict(),
                session=tx,
            )
        except DuplicateKeyError as error:
            raise LegalStorefrontPublicIntentRegistryRetryTransactionError(
                "L8_9B_RETRY_TRANSACTION_REQUIRED"
            ) from error
        except PyMongoError as error:
            _raise_mongo(error)

        return intent

    def get_by_intent_id(
        self,
        *,
        intent_id: str,
        session: Any,
    ) -> LegalStorefrontPublicIntent | None:
        """Return one exact opaque public intent or canonical absence.

        This internal persistence read requires an active caller transaction.
        It exposes no lookup by email, organization, industry, region or tenant
        and creates no public existence oracle or downstream authority.
        """
        tx = _active_transaction(session)
        identity = _identity(intent_id)

        try:
            row = self._collection.find_one(
                {"intent_id": identity},
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)

        if row is None:
            return None

        value = _hydrate(row)
        if value.intent_id != identity:
            _fail("L8_9B_BINDING_MISMATCH")

        return value


__all__ = [
    "COLLECTION",
    "INDEX_FINGERPRINT",
    "INDEX_INTENT_ID",
    "VERSION",
    "LegalStorefrontPublicIntentRegistry",
    "LegalStorefrontPublicIntentRegistryConflictError",
    "LegalStorefrontPublicIntentRegistryError",
    "LegalStorefrontPublicIntentRegistryPersistenceError",
    "LegalStorefrontPublicIntentRegistryRetryTransactionError",
    "LegalStorefrontPublicIntentRegistryTransactionRequiredError",
    "ensure_indexes",
]


# ARTIFACT: legal_storefront_public_intent_registry.py
# VERSION: v1.0.0-L8-9B-LEGAL-STOREFRONT-PUBLIC-INTENT-REGISTRY
# AUTHORITY BOUNDARY: append-only pre-tenant public-intent persistence and exact opaque-intent reads only; no identity, tenant genesis, subscription, entitlement, Legal lifecycle, billing or financial authority
# TENANT POSTURE: pre-tenant by definition; tenant_id is neither stored nor accepted and persistence cannot establish tenant scope
# TRANSACTION POSTURE: caller owns one active transaction; duplicate races require caller abort plus fresh whole-transaction retry
# RETENTION POSTURE: no TTL, delete, purge or expiry authority; retention remains separately governed
# PUBLIC LOOKUP POSTURE: no email, organization, industry, region or tenant lookup/index surface
# FAIL-CLOSED POSTURE: malformed/corrupt/divergent/racy/persistence failure rejects without repair
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
