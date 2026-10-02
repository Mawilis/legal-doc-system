"""WILSY OS — Legal Evidence Provider Cleanup Authorization Registry.

TITLE: Legal Evidence Provider Cleanup Authorization Registry
VERSION: v1.0.0-L10A2R-C4D6E-A2-PROVIDER-CLEANUP-AUTHORIZATION-REGISTRY
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Durably preserve one immutable cleanup-authorization fact per exact provider object version.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_evidence_provider_cleanup_authorization_registry.py
COLLABORATION / OWNERSHIP: Legal Operations / Legal Evidence
CERTIFICATION / UPDATE DATE: 2026-10-02
CHANGELOG:
    v1.0.0 introduces caller-transaction-owned Mongo-style persistence for the
    certified C4D6E-A1 cleanup-authorization evidence contract, with strict
    hydration, exact replay, tenant isolation and immutable unique identities.
COMPLIANCE:
    Fail-closed persistence boundary; deterministic tenant-scoped identities;
    strict domain hydration; no TTL deletion index; no provider execution.
SECURITY / PRIVACY POSTURE:
    Persists opaque tenant/provider/object references and SHA3-512 evidence
    fingerprints only. Corrupt or divergent durable evidence rejects.
TENANT BOUNDARY:
    Every read, replay and durable identity is explicitly tenant scoped.
AUTHORITY BOUNDARY:
    Persistence of cleanup-authorization evidence only. This registry does not
    authorize actors, mutate providers, delete objects, infer execution truth,
    or create settlement/payment authority.
FINANCIAL AUTHORITY BOUNDARY:
    No financial execution authority. Kennel EOS remains exclusive financial
    execution authority.

TRANSACTION CONTRACT:
    Callers own start / commit / abort. Registry operations that read or write
    durable evidence require one already-active caller transaction.

IDEMPOTENCY CONTRACT:
    Exact tenant-scoped authorization identity, fingerprint and provider-object
    identity may replay only the exact same immutable authorization evidence.
    Any divergent collision fails closed.

TTL CONTRACT:
    Cleanup-authorization evidence is immutable authorization evidence.
    This registry creates no TTL deletion index.

FAIL-CLOSED DECLARATION:
    Missing/inactive transaction, malformed domain values, corrupt persisted
    rows, divergent replay, identity collision and invalid collection behavior
    reject without inventing authority.
"""

from __future__ import annotations

from typing import Any, Final

from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_authorization import (
    LegalEvidenceProviderCleanupAuthorization,
    LegalEvidenceProviderCleanupAuthorizationError,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D6E-A2-PROVIDER-CLEANUP-AUTHORIZATION-REGISTRY"
)

COLLECTION: Final[str] = "legal_evidence_provider_cleanup_authorizations"

INDEX_TENANT_AUTHORIZATION_ID: Final[str] = (
    "legal_evidence_cleanup_authorization_tenant_authorization_id_unique"
)
INDEX_TENANT_FINGERPRINT: Final[str] = (
    "legal_evidence_cleanup_authorization_tenant_fingerprint_unique"
)
INDEX_TENANT_PROVIDER_OBJECT: Final[str] = (
    "legal_evidence_cleanup_authorization_tenant_provider_object_unique"
)


class LegalEvidenceProviderCleanupAuthorizationRegistryError(RuntimeError):
    """Base fail-closed durable cleanup-authorization registry error."""


class LegalEvidenceProviderCleanupAuthorizationRegistryTransactionError(
    LegalEvidenceProviderCleanupAuthorizationRegistryError
):
    """Caller did not provide one already-active transaction."""


class LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError(
    LegalEvidenceProviderCleanupAuthorizationRegistryError
):
    """Persisted evidence is corrupt, divergent or identity-inconsistent."""


class LegalEvidenceProviderCleanupAuthorizationRegistryPersistenceError(
    LegalEvidenceProviderCleanupAuthorizationRegistryError
):
    """Mongo-style persistence or collection interaction failed."""


def _active_transaction(
    session: Any,
) -> Any:
    """Require one already-active caller-owned transaction."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise LegalEvidenceProviderCleanupAuthorizationRegistryTransactionError(
            "L10A2R_C4D6E_A2_ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _target(
    collection: Any,
) -> Any:
    """Require one collection-like durable persistence target."""
    if collection is None:
        raise LegalEvidenceProviderCleanupAuthorizationRegistryPersistenceError(
            "L10A2R_C4D6E_A2_COLLECTION_REQUIRED"
        )
    return collection


def _value(
    authorization: LegalEvidenceProviderCleanupAuthorization,
) -> LegalEvidenceProviderCleanupAuthorization:
    """Require the exact certified cleanup-authorization domain type."""
    if type(authorization) is not LegalEvidenceProviderCleanupAuthorization:
        raise LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError(
            "L10A2R_C4D6E_A2_AUTHORIZATION_REQUIRED"
        )
    return authorization


def _document(
    authorization: LegalEvidenceProviderCleanupAuthorization,
) -> dict[str, object]:
    """Return an exact domain-certified durable representation."""
    try:
        document = authorization.to_document()
        hydrated = LegalEvidenceProviderCleanupAuthorization.from_dict(
            dict(document)
        )
    except LegalEvidenceProviderCleanupAuthorizationError as error:
        raise LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError(
            "L10A2R_C4D6E_A2_AUTHORIZATION_INVALID"
        ) from error

    if hydrated != authorization:
        raise LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError(
            "L10A2R_C4D6E_A2_AUTHORIZATION_ROUND_TRIP_INVALID"
        )

    return document


def _hydrate(
    row: object,
) -> LegalEvidenceProviderCleanupAuthorization:
    """Strictly hydrate one Mongo-style row and reject corruption."""
    if not isinstance(row, dict):
        raise LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError(
            "L10A2R_C4D6E_A2_PERSISTED_DOCUMENT_INVALID"
        )

    document = dict(row)
    document.pop("_id", None)

    try:
        return LegalEvidenceProviderCleanupAuthorization.from_dict(
            document
        )
    except (
        LegalEvidenceProviderCleanupAuthorizationError,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        raise LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError(
            "L10A2R_C4D6E_A2_PERSISTED_DOCUMENT_CORRUPT"
        ) from error


def _same(
    left: LegalEvidenceProviderCleanupAuthorization,
    right: LegalEvidenceProviderCleanupAuthorization,
) -> bool:
    """Compare exact immutable domain evidence."""
    return (
        left == right
        and left.fingerprint == right.fingerprint
        and left.to_document() == right.to_document()
    )


def _duplicate_key(error: BaseException) -> bool:
    """Recognize a Mongo duplicate-key race without importing driver authority."""
    return error.__class__.__name__ == "DuplicateKeyError"


class LegalEvidenceProviderCleanupAuthorizationRegistry:
    """Durable immutable cleanup-authorization evidence registry.

    The registry owns no transaction lifecycle. Every durable read/write method
    requires a caller-provided active transaction. Exact replay is permitted
    only when all durable identities resolve to the exact same authorization.

    Tenant boundary:
        Every identity and read contains tenant_id.

    Mutation semantics:
        Append-once immutable authorization evidence only.

    Provider authority:
        None. Persistence does not delete or mutate provider objects.

    Financial authority:
        None. Kennel EOS remains exclusive financial execution authority.
    """

    def __init__(
        self,
        collection: Any,
    ) -> None:
        """Bind one registry instance to one collection-like target."""
        self._collection = _target(collection)

    def ensure_indexes(self) -> None:
        """Create exact durable unique indexes and no TTL index."""
        try:
            self._collection.create_index(
                [
                    ("tenant_id", 1),
                    ("authorization_id", 1),
                ],
                unique=True,
                name=INDEX_TENANT_AUTHORIZATION_ID,
            )
            self._collection.create_index(
                [
                    ("tenant_id", 1),
                    ("fingerprint", 1),
                ],
                unique=True,
                name=INDEX_TENANT_FINGERPRINT,
            )
            self._collection.create_index(
                [
                    ("tenant_id", 1),
                    ("provider_name", 1),
                    ("storage_reference", 1),
                    ("object_version_reference", 1),
                ],
                unique=True,
                name=INDEX_TENANT_PROVIDER_OBJECT,
            )
        except (AttributeError, TypeError, ValueError) as error:
            raise LegalEvidenceProviderCleanupAuthorizationRegistryPersistenceError(
                "L10A2R_C4D6E_A2_INDEX_CREATION_FAILED"
            ) from error

    def _existing(
        self,
        authorization: LegalEvidenceProviderCleanupAuthorization,
        *,
        session: Any,
    ) -> tuple[LegalEvidenceProviderCleanupAuthorization, ...]:
        """Read all durable identities for exact replay reconciliation."""
        queries = (
            {
                "tenant_id": authorization.tenant_id,
                "authorization_id": authorization.authorization_id,
            },
            {
                "tenant_id": authorization.tenant_id,
                "fingerprint": authorization.fingerprint,
            },
            {
                "tenant_id": authorization.tenant_id,
                "provider_name": authorization.provider_name,
                "storage_reference": authorization.storage_reference,
                "object_version_reference":
                    authorization.object_version_reference,
            },
        )

        hydrated: list[LegalEvidenceProviderCleanupAuthorization] = []

        try:
            for query in queries:
                row = self._collection.find_one(
                    query,
                    session=session,
                )
                if row is not None:
                    hydrated.append(_hydrate(row))
        except LegalEvidenceProviderCleanupAuthorizationRegistryError:
            raise
        except (AttributeError, TypeError, ValueError) as error:
            raise LegalEvidenceProviderCleanupAuthorizationRegistryPersistenceError(
                "L10A2R_C4D6E_A2_COLLECTION_INTERFACE_INVALID"
            ) from error

        return tuple(hydrated)

    @staticmethod
    def _resolve_replay(
        requested: LegalEvidenceProviderCleanupAuthorization,
        existing: tuple[LegalEvidenceProviderCleanupAuthorization, ...],
    ) -> LegalEvidenceProviderCleanupAuthorization | None:
        """Return exact replay or fail closed on any divergent identity."""
        if not existing:
            return None

        first = existing[0]

        if not _same(first, requested):
            raise LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError(
                "L10A2R_C4D6E_A2_REPLAY_CONFLICT"
            )

        if any(
            not _same(first, item)
            for item in existing[1:]
        ):
            raise LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError(
                "L10A2R_C4D6E_A2_DURABLE_IDENTITY_CONFLICT"
            )

        return first

    def create_or_replay(
        self,
        authorization: LegalEvidenceProviderCleanupAuthorization,
        *,
        session: Any,
    ) -> LegalEvidenceProviderCleanupAuthorization:
        """Persist once or return exact replay inside caller transaction.

        Same tenant-scoped identities + exact immutable evidence return exact
        replay. Any divergent authorization identity, fingerprint or provider
        object collision fails closed.
        """
        tx = _active_transaction(session)
        requested = _value(authorization)
        document = _document(requested)

        existing = self._existing(
            requested,
            session=tx,
        )
        replay = self._resolve_replay(
            requested,
            existing,
        )
        if replay is not None:
            return replay

        try:
            self._collection.insert_one(
                document,
                session=tx,
            )
        except Exception as error:
            if not _duplicate_key(error):
                raise LegalEvidenceProviderCleanupAuthorizationRegistryPersistenceError(
                    "L10A2R_C4D6E_A2_INSERT_FAILED"
                ) from error

            existing = self._existing(
                requested,
                session=tx,
            )
            replay = self._resolve_replay(
                requested,
                existing,
            )
            if replay is None:
                raise LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError(
                    "L10A2R_C4D6E_A2_DUPLICATE_WITHOUT_REPLAY"
                ) from error
            return replay

        return requested

    def get_by_authorization_id(
        self,
        *,
        tenant_id: str,
        authorization_id: str,
        session: Any,
    ) -> LegalEvidenceProviderCleanupAuthorization | None:
        """Read one exact tenant-scoped authorization identity."""
        tx = _active_transaction(session)

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant_id,
                    "authorization_id": authorization_id,
                },
                session=tx,
            )
        except (AttributeError, TypeError, ValueError) as error:
            raise LegalEvidenceProviderCleanupAuthorizationRegistryPersistenceError(
                "L10A2R_C4D6E_A2_COLLECTION_INTERFACE_INVALID"
            ) from error

        if row is None:
            return None

        value = _hydrate(row)

        if (
            value.tenant_id != tenant_id
            or value.authorization_id != authorization_id
        ):
            raise LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError(
                "L10A2R_C4D6E_A2_LOOKUP_IDENTITY_MISMATCH"
            )

        return value

    def get_by_fingerprint(
        self,
        *,
        tenant_id: str,
        fingerprint: str,
        session: Any,
    ) -> LegalEvidenceProviderCleanupAuthorization | None:
        """Read one exact tenant-scoped authorization fingerprint."""
        tx = _active_transaction(session)

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant_id,
                    "fingerprint": fingerprint,
                },
                session=tx,
            )
        except (AttributeError, TypeError, ValueError) as error:
            raise LegalEvidenceProviderCleanupAuthorizationRegistryPersistenceError(
                "L10A2R_C4D6E_A2_COLLECTION_INTERFACE_INVALID"
            ) from error

        if row is None:
            return None

        value = _hydrate(row)

        if (
            value.tenant_id != tenant_id
            or value.fingerprint != fingerprint
        ):
            raise LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError(
                "L10A2R_C4D6E_A2_LOOKUP_IDENTITY_MISMATCH"
            )

        return value

    def get_by_provider_object(
        self,
        *,
        tenant_id: str,
        provider_name: str,
        storage_reference: str,
        object_version_reference: str,
        session: Any,
    ) -> LegalEvidenceProviderCleanupAuthorization | None:
        """Read one exact tenant/provider/storage/object-version authorization."""
        tx = _active_transaction(session)

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant_id,
                    "provider_name": provider_name,
                    "storage_reference": storage_reference,
                    "object_version_reference":
                        object_version_reference,
                },
                session=tx,
            )
        except (AttributeError, TypeError, ValueError) as error:
            raise LegalEvidenceProviderCleanupAuthorizationRegistryPersistenceError(
                "L10A2R_C4D6E_A2_COLLECTION_INTERFACE_INVALID"
            ) from error

        if row is None:
            return None

        value = _hydrate(row)

        if (
            value.tenant_id != tenant_id
            or value.provider_name != provider_name
            or value.storage_reference != storage_reference
            or value.object_version_reference != object_version_reference
        ):
            raise LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError(
                "L10A2R_C4D6E_A2_LOOKUP_IDENTITY_MISMATCH"
            )

        return value


__all__ = [
    "COLLECTION",
    "INDEX_TENANT_AUTHORIZATION_ID",
    "INDEX_TENANT_FINGERPRINT",
    "INDEX_TENANT_PROVIDER_OBJECT",
    "VERSION",
    "LegalEvidenceProviderCleanupAuthorizationRegistry",
    "LegalEvidenceProviderCleanupAuthorizationRegistryError",
    "LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError",
    "LegalEvidenceProviderCleanupAuthorizationRegistryPersistenceError",
    "LegalEvidenceProviderCleanupAuthorizationRegistryTransactionError",
]


# ARTIFACT: legal_evidence_provider_cleanup_authorization_registry.py
# VERSION: v1.0.0-L10A2R-C4D6E-A2-PROVIDER-CLEANUP-AUTHORIZATION-REGISTRY
# AUTHORITY BOUNDARY: durable immutable cleanup-authorization evidence only
# TENANT POSTURE: all durable identities and lookups are exact tenant scoped
# TRANSACTION POSTURE: caller owns one already-active transaction
# IDEMPOTENCY POSTURE: exact immutable evidence may replay; divergence rejects
# TTL POSTURE: no TTL deletion index
# PROVIDER MUTATION POSTURE: none
# DELETION EXECUTION POSTURE: none
# FAIL-CLOSED POSTURE: corrupt/divergent durable evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
