"""WILSY OS — durable Legal Evidence provider-object disownership registry.

TITLE: Legal Evidence Provider Object Disownership Registry
VERSION: v1.0.0-L10A2R-C4D6D-A2-DISOWNERSHIP-REGISTRY
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Persist one immutable, explicitly evidenced disownership decision for
         one exact tenant-scoped provider object version.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_evidence_provider_object_disownership_registry.py
COLLABORATION / OWNERSHIP:
    C4D6D-A1 owns the immutable disownership domain fact and fingerprint.
    C4D6D-A2 owns only durable exact persistence and replay of that fact.
    Authorized issuance, orphan proof, preservation composition, deletion
    authorization and provider deletion remain separate later gates.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.0-L10A2R-C4D6D-A2 establishes one tenant-scoped immutable row per
    provider object version, exact replay, strict hydration, corruption
    rejection, active caller-owned transaction enforcement and zero TTL.

AUTHORITY BOUNDARY
------------------
Persistence is not issuance and does not prove orphan status.

This registry:
- never infers disownership from absence;
- never creates provider-object ownership facts;
- never proves orphan status;
- never authorizes retention disposition, legal-hold release, abort or delete;
- never mutates provider storage;
- exposes no update/delete authority.

Caller owns one already-active Mongo transaction.
No TTL index is permitted.
Financial execution authority remains exclusively with Kennel EOS.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_evidence_provider_object_disownership import (
    LegalEvidenceProviderObjectDisownership,
    LegalEvidenceProviderObjectDisownershipError,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D6D-A2-DISOWNERSHIP-REGISTRY"
)

COLLECTION: Final[str] = (
    "legal_evidence_provider_object_disownerships"
)

INDEX_TENANT_REFERENCE: Final[str] = (
    "legal_evidence_disownership_tenant_reference_unique"
)

INDEX_TENANT_FINGERPRINT: Final[str] = (
    "legal_evidence_disownership_tenant_fingerprint_unique"
)

INDEX_TENANT_PROVIDER_OBJECT: Final[str] = (
    "legal_evidence_disownership_tenant_provider_object_unique"
)


class LegalEvidenceProviderObjectDisownershipRegistryError(
    RuntimeError
):
    """Base durable disownership registry failure."""


class LegalEvidenceProviderObjectDisownershipTransactionRequiredError(
    LegalEvidenceProviderObjectDisownershipRegistryError
):
    """Caller did not provide one active Mongo transaction."""


class LegalEvidenceProviderObjectDisownershipConflictError(
    LegalEvidenceProviderObjectDisownershipRegistryError
):
    """Immutable identity was reused for divergent durable evidence."""


class LegalEvidenceProviderObjectDisownershipNotFoundError(
    LegalEvidenceProviderObjectDisownershipRegistryError
):
    """Exact tenant-scoped durable disownership fact was not found."""


class LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError(
    LegalEvidenceProviderObjectDisownershipRegistryError
):
    """Persisted durable disownership evidence is corrupt or divergent."""


class LegalEvidenceProviderObjectDisownershipPersistenceError(
    LegalEvidenceProviderObjectDisownershipRegistryError
):
    """Mongo persistence failed without producing a trusted result."""


def _raise(
    error_type: type[LegalEvidenceProviderObjectDisownershipRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(
        code
    )

    if cause is None:
        raise error

    raise error from cause


def _active_transaction(
    session: Any,
) -> Any:
    if (
        session is None
        or getattr(
            session,
            "in_transaction",
            False,
        )
        is not True
    ):
        _raise(
            LegalEvidenceProviderObjectDisownershipTransactionRequiredError,
            "L10A2R_C4D6D_A2_ACTIVE_TRANSACTION_REQUIRED",
        )

    return session


def _target(
    collection: Any,
) -> Any:
    if collection is None:
        _raise(
            LegalEvidenceProviderObjectDisownershipPersistenceError,
            "L10A2R_C4D6D_A2_COLLECTION_REQUIRED",
        )

    return collection


def _document(
    value: LegalEvidenceProviderObjectDisownership,
) -> dict[str, object]:
    if type(
        value
    ) is not LegalEvidenceProviderObjectDisownership:
        _raise(
            LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError,
            "L10A2R_C4D6D_A2_VALUE_TYPE_INVALID",
        )

    document = value.to_dict()

    # Revalidation detects post-construction mutation before persistence.
    try:
        value.__post_init__()
    except LegalEvidenceProviderObjectDisownershipError as error:
        _raise(
            LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError,
            "L10A2R_C4D6D_A2_VALUE_INVALID",
            error,
        )

    # Persist chronology as canonical ISO-8601 text rather than BSON datetime.
    # Default PyMongo BSON decoding returns naïve datetime values unless every
    # caller configures tz_aware=True. Durable registry correctness must not
    # depend on an external client codec option.
    document["decided_at"] = value.decided_at.isoformat()

    return document


def _persisted_decided_at(
    value: object,
) -> datetime:
    if not isinstance(
        value,
        str,
    ):
        _raise(
            LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError,
            "L10A2R_C4D6D_A2_PERSISTED_DECIDED_AT_INVALID",
        )

    try:
        parsed = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )
    except ValueError as error:
        _raise(
            LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError,
            "L10A2R_C4D6D_A2_PERSISTED_DECIDED_AT_INVALID",
            error,
        )

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _raise(
            LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError,
            "L10A2R_C4D6D_A2_PERSISTED_DECIDED_AT_INVALID",
        )

    return parsed.astimezone(
        timezone.utc
    )


def _hydrate(
    row: object,
) -> LegalEvidenceProviderObjectDisownership:
    if not isinstance(
        row,
        dict,
    ):
        _raise(
            LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError,
            "L10A2R_C4D6D_A2_PERSISTED_RECORD_INVALID",
        )

    payload = dict(
        row
    )
    payload.pop(
        "_id",
        None,
    )

    if "decided_at" not in payload:
        _raise(
            LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError,
            "L10A2R_C4D6D_A2_PERSISTED_RECORD_INVALID",
        )

    payload["decided_at"] = _persisted_decided_at(
        payload["decided_at"]
    )

    try:
        return LegalEvidenceProviderObjectDisownership.from_dict(
            payload
        )
    except LegalEvidenceProviderObjectDisownershipError as error:
        _raise(
            LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError,
            "L10A2R_C4D6D_A2_PERSISTED_RECORD_INVALID",
            error,
        )


def _same(
    expected: LegalEvidenceProviderObjectDisownership,
    row: object,
) -> LegalEvidenceProviderObjectDisownership:
    actual = _hydrate(
        row
    )

    if actual != expected:
        _raise(
            LegalEvidenceProviderObjectDisownershipConflictError,
            "L10A2R_C4D6D_A2_IMMUTABLE_REPLAY_DIVERGENCE",
        )

    return actual


class LegalEvidenceProviderObjectDisownershipRegistry:
    """Immutable tenant-scoped durable disownership evidence registry."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = _target(
            collection
        )

    def ensure_indexes(
        self,
    ) -> None:
        """Create exact immutable identities; never create TTL deletion."""

        try:
            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "disownership_reference",
                        ASCENDING,
                    ),
                ],
                unique=True,
                name=INDEX_TENANT_REFERENCE,
            )

            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "fingerprint",
                        ASCENDING,
                    ),
                ],
                unique=True,
                name=INDEX_TENANT_FINGERPRINT,
            )

            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "provider_name",
                        ASCENDING,
                    ),
                    (
                        "storage_reference",
                        ASCENDING,
                    ),
                    (
                        "object_version_reference",
                        ASCENDING,
                    ),
                ],
                unique=True,
                name=INDEX_TENANT_PROVIDER_OBJECT,
            )
        except PyMongoError as error:
            _raise(
                LegalEvidenceProviderObjectDisownershipPersistenceError,
                "L10A2R_C4D6D_A2_INDEX_CREATION_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceProviderObjectDisownershipPersistenceError,
                "L10A2R_C4D6D_A2_COLLECTION_INTERFACE_INVALID",
                error,
            )

    def _find_identity_rows(
        self,
        value: LegalEvidenceProviderObjectDisownership,
        *,
        session: Any,
    ) -> tuple[object | None, object | None, object | None]:
        try:
            by_reference = self._collection.find_one(
                {
                    "tenant_id":
                        value.tenant_id,
                    "disownership_reference":
                        value.disownership_reference,
                },
                session=session,
            )

            by_fingerprint = self._collection.find_one(
                {
                    "tenant_id":
                        value.tenant_id,
                    "fingerprint":
                        value.fingerprint,
                },
                session=session,
            )

            by_provider_object = self._collection.find_one(
                {
                    "tenant_id":
                        value.tenant_id,
                    "provider_name":
                        value.provider_name,
                    "storage_reference":
                        value.storage_reference,
                    "object_version_reference":
                        value.object_version_reference,
                },
                session=session,
            )
        except PyMongoError as error:
            _raise(
                LegalEvidenceProviderObjectDisownershipPersistenceError,
                "L10A2R_C4D6D_A2_READ_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceProviderObjectDisownershipPersistenceError,
                "L10A2R_C4D6D_A2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        return (
            by_reference,
            by_fingerprint,
            by_provider_object,
        )

    def create_or_replay(
        self,
        value: LegalEvidenceProviderObjectDisownership,
        *,
        session: Any,
    ) -> LegalEvidenceProviderObjectDisownership:
        """Persist once or return one exact immutable replay."""

        tx = _active_transaction(
            session
        )
        document = _document(
            value
        )

        rows = self._find_identity_rows(
            value,
            session=tx,
        )

        present = tuple(
            row
            for row in rows
            if row is not None
        )

        if present:
            hydrated = tuple(
                _same(
                    value,
                    row,
                )
                for row in present
            )

            first = hydrated[0]

            if any(
                item != first
                for item in hydrated[1:]
            ):
                _raise(
                    LegalEvidenceProviderObjectDisownershipConflictError,
                    "L10A2R_C4D6D_A2_IDENTITY_ROWS_DIVERGE",
                )

            return first

        try:
            result = self._collection.insert_one(
                document,
                session=tx,
            )

            if getattr(
                result,
                "acknowledged",
                False,
            ) is not True:
                _raise(
                    LegalEvidenceProviderObjectDisownershipPersistenceError,
                    "L10A2R_C4D6D_A2_INSERT_NOT_ACKNOWLEDGED",
                )
        except DuplicateKeyError as error:
            # A duplicate-key write race leaves transaction recovery to the
            # caller. Do not attempt same-transaction replay reads here.
            # Caller must abort and retry the whole transaction, at which
            # point the ordinary pre-insert identity reads can prove exact
            # replay or reject divergence.
            _raise(
                LegalEvidenceProviderObjectDisownershipConflictError,
                "L10A2R_C4D6D_A2_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )
        except LegalEvidenceProviderObjectDisownershipRegistryError:
            raise
        except PyMongoError as error:
            _raise(
                LegalEvidenceProviderObjectDisownershipPersistenceError,
                "L10A2R_C4D6D_A2_INSERT_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceProviderObjectDisownershipPersistenceError,
                "L10A2R_C4D6D_A2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        return value

    def get_by_reference(
        self,
        *,
        tenant_id: str,
        disownership_reference: str,
        session: Any,
    ) -> LegalEvidenceProviderObjectDisownership:
        """Return exact tenant+disownership-reference durable evidence."""

        tx = _active_transaction(
            session
        )

        if (
            not isinstance(
                tenant_id,
                str,
            )
            or not tenant_id
            or not isinstance(
                disownership_reference,
                str,
            )
            or not disownership_reference
        ):
            _raise(
                LegalEvidenceProviderObjectDisownershipNotFoundError,
                "L10A2R_C4D6D_A2_NOT_FOUND",
            )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id":
                        tenant_id,
                    "disownership_reference":
                        disownership_reference,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                LegalEvidenceProviderObjectDisownershipPersistenceError,
                "L10A2R_C4D6D_A2_READ_FAILED",
                error,
            )

        if row is None:
            _raise(
                LegalEvidenceProviderObjectDisownershipNotFoundError,
                "L10A2R_C4D6D_A2_NOT_FOUND",
            )

        value = _hydrate(
            row
        )

        if (
            value.tenant_id != tenant_id
            or value.disownership_reference
            != disownership_reference
        ):
            _raise(
                LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError,
                "L10A2R_C4D6D_A2_PERSISTED_SCOPE_MISMATCH",
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
    ) -> LegalEvidenceProviderObjectDisownership:
        """Return one exact tenant-scoped provider-object disownership fact."""

        tx = _active_transaction(
            session
        )

        fields = (
            tenant_id,
            provider_name,
            storage_reference,
            object_version_reference,
        )

        if any(
            not isinstance(
                item,
                str,
            )
            or not item
            for item in fields
        ):
            _raise(
                LegalEvidenceProviderObjectDisownershipNotFoundError,
                "L10A2R_C4D6D_A2_NOT_FOUND",
            )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id":
                        tenant_id,
                    "provider_name":
                        provider_name,
                    "storage_reference":
                        storage_reference,
                    "object_version_reference":
                        object_version_reference,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                LegalEvidenceProviderObjectDisownershipPersistenceError,
                "L10A2R_C4D6D_A2_READ_FAILED",
                error,
            )

        if row is None:
            _raise(
                LegalEvidenceProviderObjectDisownershipNotFoundError,
                "L10A2R_C4D6D_A2_NOT_FOUND",
            )

        value = _hydrate(
            row
        )

        if (
            value.tenant_id != tenant_id
            or value.provider_name != provider_name
            or value.storage_reference != storage_reference
            or value.object_version_reference
            != object_version_reference
        ):
            _raise(
                LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError,
                "L10A2R_C4D6D_A2_PERSISTED_SCOPE_MISMATCH",
            )

        return value


__all__ = [
    "COLLECTION",
    "INDEX_TENANT_FINGERPRINT",
    "INDEX_TENANT_PROVIDER_OBJECT",
    "INDEX_TENANT_REFERENCE",
    "VERSION",
    "LegalEvidenceProviderObjectDisownershipConflictError",
    "LegalEvidenceProviderObjectDisownershipNotFoundError",
    "LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError",
    "LegalEvidenceProviderObjectDisownershipPersistenceError",
    "LegalEvidenceProviderObjectDisownershipRegistry",
    "LegalEvidenceProviderObjectDisownershipRegistryError",
    "LegalEvidenceProviderObjectDisownershipTransactionRequiredError",
]


# ARTIFACT: legal_evidence_provider_object_disownership_registry.py
# VERSION: v1.0.0-L10A2R-C4D6D-A2-DISOWNERSHIP-REGISTRY
# AUTHORITY BOUNDARY: durable exact disownership persistence/replay only
# TENANT POSTURE: all identities and reads are exact tenant scoped
# PROVIDER OBJECT POSTURE: one immutable decision per exact provider object version
# TRANSACTION POSTURE: caller owns one already-active Mongo transaction
# REPLAY POSTURE: exact immutable replay only; divergence fails closed
# CORRUPTION POSTURE: strict domain hydration; no self-healing
# TTL POSTURE: no TTL index or wall-clock deletion
# ORPHAN POSTURE: persistence is not orphan proof
# DELETION POSTURE: no delete authorization or provider mutation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
