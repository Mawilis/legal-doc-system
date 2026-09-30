"""WILSY OS durable Legal Evidence commit-uncertainty registry.

TITLE: Legal Evidence Commit Uncertainty Registry
VERSION: v1.0.0-L10A2R-C4B-COMMIT-UNCERTAINTY-REGISTRY
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Persist immutable C4A LegalEvidenceCommitUncertainty values in the Mongo
    control plane so verified provider-object / unproven-C3-outcome evidence
    survives process restart and is discoverable for later reconciliation.

EPITOME:
    C4A COMMIT UNCERTAINTY
    -> DURABLE MONGO CONTROL-PLANE EVIDENCE
    != ORPHAN PROVEN
    != C3 COMMIT FAILED
    != RECONCILIATION PERFORMED
    != RESERVATION RELEASED
    != PROVIDER OBJECT DELETED
    != AUTHORIZED AVAILABILITY

COLLABORATION / OWNERSHIP:
    C4A owns immutable commit-uncertainty evidence.
    C4B owns only durable append-once persistence, exact replay, corruption
    detection and tenant-scoped discovery.
    Later C4 reconciliation services determine actual metadata/reservation
    state and execute only separately certified reconciliation actions.
    Provider execution remains owned by the certified storage adapter.
    Retention/legal-hold/deletion authority remains separately certified.

TRANSACTION POSTURE:
    Every operational read/write requires one already-active caller-owned Mongo
    transaction. This registry never starts, commits, aborts or retries it.

TENANT BOUNDARY:
    Every operational read/write begins with exact tenant scope. Cross-tenant
    absence is indistinguishable from not-found.

IDENTITY:
    One tenant may bind one uncertainty_id exactly once.
    One tenant may bind one ingestion_intent_id to exactly one uncertainty.
    One tenant may bind one provider object version coordinate to exactly one
    uncertainty.

TTL:
    No TTL index exists. Commit uncertainty is reconciliation/audit evidence and
    must not disappear merely because wall-clock time elapsed.

FAIL-CLOSED DECLARATION:
    Missing transactions, malformed scope, unknown/missing persisted fields,
    fingerprint corruption, divergent immutable replay, ingestion/provider
    identity collisions, duplicate-key races and Mongo failures reject.

AUTHORITY BOUNDARY:
    Immutable uncertainty durability only. No provider IO, reconciliation,
    reservation transition, usage mutation, deletion, retention/legal-hold
    decision, availability publication, IAM, billing, payment or settlement.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_commit_uncertainty import (
    LegalEvidenceCommitUncertainty,
    LegalEvidenceCommitUncertaintyError,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4B-COMMIT-UNCERTAINTY-REGISTRY"
)

COLLECTION: Final[str] = (
    "legal_evidence_commit_uncertainties"
)

UNCERTAINTY_INDEX_NAME: Final[str] = (
    "legal_evidence_commit_uncertainty_tenant_identity_unique"
)

INGESTION_INDEX_NAME: Final[str] = (
    "legal_evidence_commit_uncertainty_tenant_ingestion_unique"
)

PROVIDER_OBJECT_INDEX_NAME: Final[str] = (
    "legal_evidence_commit_uncertainty_tenant_provider_object_unique"
)

DETECTED_INDEX_NAME: Final[str] = (
    "legal_evidence_commit_uncertainty_tenant_detected"
)

MAX_TENANT_UNCERTAINTIES: Final[int] = 500

WRITE_CONCERN: Final[WriteConcern] = WriteConcern(
    w="majority",
    j=True,
)

READ_CONCERN: Final[ReadConcern] = ReadConcern(
    "majority"
)

_UNCERTAINTY_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "uncertainty_id",
        "tenant_id",
        "case_matter_id",
        "document_id",
        "ingestion_intent_id",
        "reservation_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "provider_integrity_reference",
        "write_intent_fingerprint",
        "content_length",
        "content_fingerprint",
        "source_evidence_reference",
        "source_evidence_fingerprint",
        "detected_at",
        "schema",
        "uncertainty_version",
        "fingerprint",
    }
)


class LegalEvidenceCommitUncertaintyRegistryError(
    RuntimeError
):
    """Base fail-closed C4B registry error."""

    default_code = (
        "L10A2R_C4B_REGISTRY_ERROR"
    )

    def __init__(
        self,
        code: str | None = None,
    ) -> None:
        self.code = (
            code
            or self.default_code
        )
        super().__init__(
            self.code
        )


class LegalEvidenceCommitUncertaintyRegistryInputError(
    LegalEvidenceCommitUncertaintyRegistryError
):
    """Malformed input or unsupported collection surface."""

    default_code = (
        "L10A2R_C4B_INPUT_INVALID"
    )


class LegalEvidenceCommitUncertaintyRegistryTransactionRequiredError(
    LegalEvidenceCommitUncertaintyRegistryError
):
    """Caller did not provide one active transaction."""

    default_code = (
        "L10A2R_C4B_TRANSACTION_REQUIRED"
    )


class LegalEvidenceCommitUncertaintyRegistryNotFoundError(
    LegalEvidenceCommitUncertaintyRegistryError
):
    """No exact tenant-scoped uncertainty exists."""

    default_code = (
        "L10A2R_C4B_UNCERTAINTY_NOT_FOUND"
    )


class LegalEvidenceCommitUncertaintyRegistryConflictError(
    LegalEvidenceCommitUncertaintyRegistryError
):
    """Immutable uncertainty identity conflicts."""

    default_code = (
        "L10A2R_C4B_UNCERTAINTY_CONFLICT"
    )


class LegalEvidenceCommitUncertaintyRegistryRetryRequiredError(
    LegalEvidenceCommitUncertaintyRegistryError
):
    """Caller must abort and retry the complete transaction."""

    default_code = (
        "L10A2R_C4B_WHOLE_TRANSACTION_RETRY_REQUIRED"
    )


class LegalEvidenceCommitUncertaintyRegistryPersistenceUnavailableError(
    LegalEvidenceCommitUncertaintyRegistryError
):
    """Mongo persistence/read failed safely."""

    default_code = (
        "L10A2R_C4B_PERSISTENCE_UNAVAILABLE"
    )


def _raise(
    error_type: type[
        LegalEvidenceCommitUncertaintyRegistryError
    ],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(
        code
    )

    if cause is None:
        raise error

    raise error from cause


def _raise_mongo(
    error: PyMongoError,
) -> NoReturn:
    if error.has_error_label(
        "TransientTransactionError"
    ):
        _raise(
            LegalEvidenceCommitUncertaintyRegistryRetryRequiredError,
            cause=error,
        )

    _raise(
        LegalEvidenceCommitUncertaintyRegistryPersistenceUnavailableError,
        cause=error,
    )


def _target(
    collection: Any,
) -> Any:
    if collection is None:
        _raise(
            LegalEvidenceCommitUncertaintyRegistryInputError,
            "L10A2R_C4B_COLLECTION_REQUIRED",
        )

    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
            codec_options=CodecOptions(
                tz_aware=True,
                tzinfo=timezone.utc,
            ),
        )
    except AttributeError:
        return collection


def _active_transaction(
    session: Any,
) -> Any:
    if session is None:
        _raise(
            LegalEvidenceCommitUncertaintyRegistryTransactionRequiredError,
            "L10A2R_C4B_TRANSACTION_REQUIRED",
        )

    marker = getattr(
        session,
        "in_transaction",
        None,
    )

    try:
        active = (
            marker()
            if callable(marker)
            else marker
        )
    except (
        AttributeError,
        TypeError,
    ):
        active = False

    if active is not True:
        _raise(
            LegalEvidenceCommitUncertaintyRegistryTransactionRequiredError,
            "L10A2R_C4B_TRANSACTION_REQUIRED",
        )

    return session


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
        or len(value) > 2048
    ):
        _raise(
            LegalEvidenceCommitUncertaintyRegistryInputError,
            f"L10A2R_C4B_{name.upper()}_INVALID",
        )

    return value


def _serialize(
    value: LegalEvidenceCommitUncertainty,
) -> dict[str, object]:
    """Encode C4A exactly while preserving microsecond timestamp identity."""
    if type(value) is not LegalEvidenceCommitUncertainty:
        _raise(
            LegalEvidenceCommitUncertaintyRegistryInputError,
            "L10A2R_C4B_UNCERTAINTY_REQUIRED",
        )

    document = value.to_dict()

    document["detected_at"] = (
        value.detected_at.isoformat()
    )

    if (
        set(document)
        != _UNCERTAINTY_FIELDS
    ):
        _raise(
            LegalEvidenceCommitUncertaintyRegistryError,
            "L10A2R_C4B_CORRUPT_UNCERTAINTY",
        )

    if any(
        isinstance(
            item,
            (
                bytes,
                bytearray,
            ),
        )
        for item in document.values()
    ):
        _raise(
            LegalEvidenceCommitUncertaintyRegistryError,
            "L10A2R_C4B_RAW_BYTES_FORBIDDEN",
        )

    return document


def _hydrate(
    row: Mapping[str, Any],
) -> LegalEvidenceCommitUncertainty:
    """Strictly hydrate exactly one immutable C4A persisted row."""
    try:
        if not isinstance(
            row,
            Mapping,
        ):
            _raise(
                LegalEvidenceCommitUncertaintyRegistryError,
                "L10A2R_C4B_CORRUPT_UNCERTAINTY",
            )

        persisted = dict(
            row
        )

        persisted.pop(
            "_id",
            None,
        )

        if (
            set(persisted)
            != _UNCERTAINTY_FIELDS
        ):
            _raise(
                LegalEvidenceCommitUncertaintyRegistryError,
                "L10A2R_C4B_CORRUPT_UNCERTAINTY",
            )

        detected_at = persisted.get(
            "detected_at"
        )

        if not isinstance(
            detected_at,
            str,
        ):
            _raise(
                LegalEvidenceCommitUncertaintyRegistryError,
                "L10A2R_C4B_CORRUPT_UNCERTAINTY",
            )

        try:
            parsed_detected_at = (
                datetime.fromisoformat(
                    detected_at
                )
            )
        except ValueError as error:
            _raise(
                LegalEvidenceCommitUncertaintyRegistryError,
                "L10A2R_C4B_CORRUPT_UNCERTAINTY",
                error,
            )

        if (
            parsed_detected_at.tzinfo
            is None
            or parsed_detected_at.utcoffset()
            is None
            or parsed_detected_at.astimezone(
                timezone.utc
            ).isoformat()
            != detected_at
        ):
            _raise(
                LegalEvidenceCommitUncertaintyRegistryError,
                "L10A2R_C4B_CORRUPT_UNCERTAINTY",
            )

        domain_payload = dict(
            persisted
        )

        domain_payload[
            "detected_at"
        ] = parsed_detected_at

        value = (
            LegalEvidenceCommitUncertainty.from_dict(
                cast(
                    Mapping[
                        str,
                        object,
                    ],
                    domain_payload,
                )
            )
        )

        if (
            _serialize(value)
            != persisted
        ):
            _raise(
                LegalEvidenceCommitUncertaintyRegistryError,
                "L10A2R_C4B_CORRUPT_UNCERTAINTY",
            )

        return value

    except LegalEvidenceCommitUncertaintyRegistryError:
        raise
    except (
        KeyError,
        TypeError,
        ValueError,
        LegalEvidenceCommitUncertaintyError,
    ) as error:
        _raise(
            LegalEvidenceCommitUncertaintyRegistryError,
            "L10A2R_C4B_CORRUPT_UNCERTAINTY",
            error,
        )


def ensure_indexes(
    collection: Any,
) -> None:
    """Create the closed C4B durable identity/read index surface."""
    target = _target(
        collection
    )

    try:
        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "uncertainty_id",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=UNCERTAINTY_INDEX_NAME,
        )

        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "ingestion_intent_id",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=INGESTION_INDEX_NAME,
        )

        target.create_index(
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
            name=PROVIDER_OBJECT_INDEX_NAME,
        )

        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "detected_at",
                    DESCENDING,
                ),
                (
                    "uncertainty_id",
                    ASCENDING,
                ),
            ],
            unique=False,
            name=DETECTED_INDEX_NAME,
        )

    except PyMongoError as error:
        _raise_mongo(
            error
        )
    except AttributeError as error:
        _raise(
            LegalEvidenceCommitUncertaintyRegistryInputError,
            "L10A2R_C4B_COLLECTION_INTERFACE_INVALID",
            error,
        )


class LegalEvidenceCommitUncertaintyRegistry:
    """Append-once durable C4A commit-uncertainty registry."""

    __slots__ = (
        "_collection",
    )

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
        """Create exact C4B indexes without TTL."""
        ensure_indexes(
            self._collection
        )

    def create_or_replay(
        self,
        value: LegalEvidenceCommitUncertainty,
        *,
        session: Any,
    ) -> LegalEvidenceCommitUncertainty:
        """Persist once or return one exact immutable uncertainty replay."""
        tx = _active_transaction(
            session
        )

        if type(value) is not LegalEvidenceCommitUncertainty:
            _raise(
                LegalEvidenceCommitUncertaintyRegistryInputError,
                "L10A2R_C4B_UNCERTAINTY_REQUIRED",
            )

        try:
            existing = self._collection.find_one(
                {
                    "tenant_id":
                        value.tenant_id,
                    "uncertainty_id":
                        value.uncertainty_id,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(
                error
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceCommitUncertaintyRegistryInputError,
                "L10A2R_C4B_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if existing is not None:
            persisted = _hydrate(
                cast(
                    Mapping[
                        str,
                        Any,
                    ],
                    existing,
                )
            )

            if persisted != value:
                _raise(
                    LegalEvidenceCommitUncertaintyRegistryConflictError,
                    "L10A2R_C4B_DIVERGENT_UNCERTAINTY_IDENTITY",
                )

            return persisted

        try:
            ingestion = self._collection.find_one(
                {
                    "tenant_id":
                        value.tenant_id,
                    "ingestion_intent_id":
                        value.ingestion_intent_id,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(
                error
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceCommitUncertaintyRegistryInputError,
                "L10A2R_C4B_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if ingestion is not None:
            persisted_ingestion = _hydrate(
                cast(
                    Mapping[
                        str,
                        Any,
                    ],
                    ingestion,
                )
            )

            if persisted_ingestion != value:
                _raise(
                    LegalEvidenceCommitUncertaintyRegistryConflictError,
                    "L10A2R_C4B_DIVERGENT_INGESTION_IDENTITY",
                )

            return persisted_ingestion

        try:
            provider_object = (
                self._collection.find_one(
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
                    session=tx,
                )
            )
        except PyMongoError as error:
            _raise_mongo(
                error
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceCommitUncertaintyRegistryInputError,
                "L10A2R_C4B_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if provider_object is not None:
            persisted_provider = _hydrate(
                cast(
                    Mapping[
                        str,
                        Any,
                    ],
                    provider_object,
                )
            )

            if persisted_provider != value:
                _raise(
                    LegalEvidenceCommitUncertaintyRegistryConflictError,
                    "L10A2R_C4B_DIVERGENT_PROVIDER_OBJECT_IDENTITY",
                )

            return persisted_provider

        document = _serialize(
            value
        )

        try:
            self._collection.insert_one(
                document,
                session=tx,
            )
        except DuplicateKeyError as error:
            _raise(
                LegalEvidenceCommitUncertaintyRegistryRetryRequiredError,
                cause=error,
            )
        except PyMongoError as error:
            _raise_mongo(
                error
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceCommitUncertaintyRegistryInputError,
                "L10A2R_C4B_COLLECTION_INTERFACE_INVALID",
                error,
            )

        return value

    def get(
        self,
        *,
        tenant_id: str,
        uncertainty_id: str,
        session: Any,
    ) -> LegalEvidenceCommitUncertainty:
        """Return one exact tenant-scoped strictly hydrated uncertainty."""
        tx = _active_transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )

        uncertainty = _text(
            "uncertainty_id",
            uncertainty_id,
        )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id":
                        tenant,
                    "uncertainty_id":
                        uncertainty,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(
                error
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceCommitUncertaintyRegistryInputError,
                "L10A2R_C4B_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if row is None:
            _raise(
                LegalEvidenceCommitUncertaintyRegistryNotFoundError,
                "L10A2R_C4B_UNCERTAINTY_NOT_FOUND",
            )

        value = _hydrate(
            cast(
                Mapping[
                    str,
                    Any,
                ],
                row,
            )
        )

        if (
            value.tenant_id
            != tenant
            or value.uncertainty_id
            != uncertainty
        ):
            _raise(
                LegalEvidenceCommitUncertaintyRegistryError,
                "L10A2R_C4B_CORRUPT_UNCERTAINTY",
            )

        return value

    def list_tenant_uncertainties(
        self,
        *,
        tenant_id: str,
        session: Any,
    ) -> tuple[
        LegalEvidenceCommitUncertainty,
        ...,
    ]:
        """Return bounded deterministic unresolved-evidence rows for one tenant.

        C4B does not claim these values remain unresolved in business truth.
        They are durable uncertainty evidence only; later reconciliation owns
        determination of actual current state.
        """
        tx = _active_transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )

        try:
            cursor = self._collection.find(
                {
                    "tenant_id":
                        tenant,
                },
                session=tx,
            )

            if hasattr(
                cursor,
                "limit",
            ):
                cursor = cursor.limit(
                    MAX_TENANT_UNCERTAINTIES
                    + 1
                )

            rows = tuple(
                cast(
                    Mapping[
                        str,
                        Any,
                    ],
                    row,
                )
                for row in cursor
            )

        except PyMongoError as error:
            _raise_mongo(
                error
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceCommitUncertaintyRegistryInputError,
                "L10A2R_C4B_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if (
            len(rows)
            > MAX_TENANT_UNCERTAINTIES
        ):
            _raise(
                LegalEvidenceCommitUncertaintyRegistryError,
                "L10A2R_C4B_TENANT_UNCERTAINTY_LIMIT_EXCEEDED",
            )

        hydrated = tuple(
            _hydrate(
                row
            )
            for row in rows
        )

        for value in hydrated:
            if (
                value.tenant_id
                != tenant
            ):
                _raise(
                    LegalEvidenceCommitUncertaintyRegistryError,
                    "L10A2R_C4B_CORRUPT_UNCERTAINTY",
                )

        return tuple(
            sorted(
                hydrated,
                key=lambda item: (
                    item.detected_at,
                    item.uncertainty_id,
                ),
                reverse=True,
            )
        )


__all__ = [
    "COLLECTION",
    "DETECTED_INDEX_NAME",
    "INGESTION_INDEX_NAME",
    "MAX_TENANT_UNCERTAINTIES",
    "PROVIDER_OBJECT_INDEX_NAME",
    "READ_CONCERN",
    "UNCERTAINTY_INDEX_NAME",
    "VERSION",
    "WRITE_CONCERN",
    "LegalEvidenceCommitUncertaintyRegistry",
    "LegalEvidenceCommitUncertaintyRegistryConflictError",
    "LegalEvidenceCommitUncertaintyRegistryError",
    "LegalEvidenceCommitUncertaintyRegistryInputError",
    "LegalEvidenceCommitUncertaintyRegistryNotFoundError",
    "LegalEvidenceCommitUncertaintyRegistryPersistenceUnavailableError",
    "LegalEvidenceCommitUncertaintyRegistryRetryRequiredError",
    "LegalEvidenceCommitUncertaintyRegistryTransactionRequiredError",
    "ensure_indexes",
]


# ARTIFACT: legal_evidence_commit_uncertainty_registry.py
# VERSION: v1.0.0-L10A2R-C4B-COMMIT-UNCERTAINTY-REGISTRY
# AUTHORITY BOUNDARY: immutable commit-uncertainty durability only
# TENANT POSTURE: exact tenant-scoped create/replay/read/list identity
# INGESTION POSTURE: one tenant ingestion binds one uncertainty identity
# PROVIDER POSTURE: one provider object version binds one uncertainty; no IO
# TRANSACTION POSTURE: caller owns one already-active transaction
# REPLAY POSTURE: exact replay only; divergence fails closed
# TTL POSTURE: no TTL; uncertainty evidence is not wall-clock deleted
# RECONCILIATION POSTURE: persistence does not determine reconciliation outcome
# DELETION POSTURE: no provider-object deletion authority
# AVAILABILITY POSTURE: no availability authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
