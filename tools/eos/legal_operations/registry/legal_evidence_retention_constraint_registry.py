"""WILSY OS — durable Legal Evidence retention-constraint registry.

TITLE: Legal Evidence Retention Constraint Registry
VERSION: v1.0.0-L10A2R-C4D4A-R3-RETENTION-CONSTRAINT-REGISTRY
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Persist and exactly replay one already-valid immutable retention
         constraint for one exact tenant-scoped provider object version.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_evidence_retention_constraint_registry.py
COLLABORATION / OWNERSHIP:
    C4D4A domain owns immutable retention-constraint truth and temporal
    assessment. This registry owns durable exact persistence/replay only.
    Source-authority selection, legal-hold governance, retention satisfaction,
    orphan proof, deletion authorization, provider mutation and reconciliation
    remain separately certified later gates.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.0-L10A2R-C4D4A-R3 establishes exact tenant/provider-object durable
    persistence, strict hydration, immutable replay, active caller-owned
    transaction enforcement, duplicate-race whole-transaction retry and
    zero-TTL posture.

AUTHORITY BOUNDARY
------------------
Persistence is not retention satisfaction or disposition authority.

This registry:
- persists only an already-valid LegalEvidenceRetentionConstraint;
- never selects statutes, contracts, court directions or retention periods;
- never concludes that retention is satisfied;
- never issues, releases or clears a legal hold;
- never proves orphan status;
- never authorizes deletion or provider mutation;
- exposes no update/delete mutator.

Caller owns one already-active Mongo transaction.
The registry never starts, commits, aborts or retries a transaction.
Duplicate-key races require whole-transaction retry by the caller.
No TTL index is permitted.
Financial execution authority remains exclusively with Kennel EOS.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_evidence_retention_constraint import (
    LegalEvidenceRetentionConstraint,
    LegalEvidenceRetentionConstraintError,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D4A-R3-RETENTION-CONSTRAINT-REGISTRY"
)

COLLECTION: Final[str] = (
    "legal_evidence_retention_constraints"
)

INDEX_TENANT_FINGERPRINT: Final[str] = (
    "legal_evidence_retention_tenant_fingerprint_unique"
)

INDEX_TENANT_PROVIDER_OBJECT: Final[str] = (
    "legal_evidence_retention_tenant_provider_object_unique"
)

INDEX_TENANT_SOURCE_EVIDENCE: Final[str] = (
    "legal_evidence_retention_tenant_source_evidence"
)

_PERSISTED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "tenant_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "source_evidence_reference",
        "source_evidence_fingerprint",
        "imposed_at",
        "retain_until",
        "legal_hold_cleared",
        "orphan_proven",
        "provider_delete_authorized",
        "fingerprint",
    }
)


class LegalEvidenceRetentionConstraintRegistryError(
    RuntimeError
):
    """Base durable retention-constraint registry failure."""


class LegalEvidenceRetentionConstraintTransactionRequiredError(
    LegalEvidenceRetentionConstraintRegistryError
):
    """Caller did not provide one already-active Mongo transaction."""


class LegalEvidenceRetentionConstraintConflictError(
    LegalEvidenceRetentionConstraintRegistryError
):
    """Immutable retention identity was reused for divergent evidence."""


class LegalEvidenceRetentionConstraintNotFoundError(
    LegalEvidenceRetentionConstraintRegistryError
):
    """Exact tenant-scoped durable retention constraint was not found."""


class LegalEvidenceRetentionConstraintPersistedRecordInvalidError(
    LegalEvidenceRetentionConstraintRegistryError
):
    """Persisted retention-constraint evidence is malformed or corrupt."""


class LegalEvidenceRetentionConstraintPersistenceError(
    LegalEvidenceRetentionConstraintRegistryError
):
    """Mongo persistence or collection interaction failed."""


def _raise(
    error_type: type[LegalEvidenceRetentionConstraintRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable structured retention-registry error."""

    error = error_type(
        code
    )

    if cause is None:
        raise error

    raise error from cause


def _active_transaction(
    session: Any,
) -> Any:
    """Return caller session only when one active transaction already exists."""

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
            LegalEvidenceRetentionConstraintTransactionRequiredError,
            "L10A2R_C4D4A_R3_ACTIVE_TRANSACTION_REQUIRED",
        )

    return session


def _target(
    collection: Any,
) -> Any:
    """Return one collection-like persistence target or fail closed."""

    if collection is None:
        _raise(
            LegalEvidenceRetentionConstraintPersistenceError,
            "L10A2R_C4D4A_R3_COLLECTION_REQUIRED",
        )

    return collection


def _persisted_utc(
    name: str,
    value: object,
) -> datetime:
    """Hydrate one exact aware persisted ISO-8601 chronology value."""

    if not isinstance(
        value,
        str,
    ):
        _raise(
            LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
            f"L10A2R_C4D4A_R3_PERSISTED_{name.upper()}_INVALID",
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
            LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
            f"L10A2R_C4D4A_R3_PERSISTED_{name.upper()}_INVALID",
            error,
        )

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _raise(
            LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
            f"L10A2R_C4D4A_R3_PERSISTED_{name.upper()}_INVALID",
        )

    return parsed.astimezone(
        timezone.utc
    )


def _validated_value(
    value: object,
) -> LegalEvidenceRetentionConstraint:
    """Reconstruct one exact domain value to detect invalid/tampered input."""

    if type(
        value
    ) is not LegalEvidenceRetentionConstraint:
        _raise(
            LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4A_R3_VALUE_TYPE_INVALID",
        )

    try:
        validated = LegalEvidenceRetentionConstraint(
            tenant_id=value.tenant_id,
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=value.object_version_reference,
            source_evidence_reference=value.source_evidence_reference,
            source_evidence_fingerprint=value.source_evidence_fingerprint,
            imposed_at=value.imposed_at,
            retain_until=value.retain_until,
            legal_hold_cleared=value.legal_hold_cleared,
            orphan_proven=value.orphan_proven,
            provider_delete_authorized=value.provider_delete_authorized,
            fingerprint=value.fingerprint,
        )
    except LegalEvidenceRetentionConstraintError as error:
        _raise(
            LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4A_R3_VALUE_INVALID",
            error,
        )
    except (AttributeError, TypeError, ValueError) as error:
        _raise(
            LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4A_R3_VALUE_INVALID",
            error,
        )

    if validated != value:
        _raise(
            LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4A_R3_VALUE_DIVERGED",
        )

    return validated


def _document(
    value: LegalEvidenceRetentionConstraint,
) -> dict[str, object]:
    """Return one exact durable retention-constraint document."""

    validated = _validated_value(
        value
    )

    return {
        "tenant_id":
            validated.tenant_id,
        "provider_name":
            validated.provider_name,
        "storage_reference":
            validated.storage_reference,
        "object_version_reference":
            validated.object_version_reference,
        "source_evidence_reference":
            validated.source_evidence_reference,
        "source_evidence_fingerprint":
            validated.source_evidence_fingerprint,
        "imposed_at":
            validated.imposed_at.isoformat(),
        "retain_until":
            validated.retain_until.isoformat(),
        "legal_hold_cleared":
            False,
        "orphan_proven":
            False,
        "provider_delete_authorized":
            False,
        "fingerprint":
            validated.fingerprint,
    }


def _hydrate(
    row: object,
) -> LegalEvidenceRetentionConstraint:
    """Hydrate one persisted constraint exactly; never heal corruption."""

    if not isinstance(
        row,
        dict,
    ):
        _raise(
            LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4A_R3_PERSISTED_RECORD_INVALID",
        )

    payload = dict(
        row
    )
    payload.pop(
        "_id",
        None,
    )

    if set(
        payload
    ) != _PERSISTED_FIELDS:
        _raise(
            LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4A_R3_PERSISTED_RECORD_INVALID",
        )

    imposed_at = _persisted_utc(
        "imposed_at",
        payload["imposed_at"],
    )
    retain_until = _persisted_utc(
        "retain_until",
        payload["retain_until"],
    )

    try:
        return LegalEvidenceRetentionConstraint(
            tenant_id=payload["tenant_id"],
            provider_name=payload["provider_name"],
            storage_reference=payload["storage_reference"],
            object_version_reference=payload["object_version_reference"],
            source_evidence_reference=payload["source_evidence_reference"],
            source_evidence_fingerprint=payload[
                "source_evidence_fingerprint"
            ],
            imposed_at=imposed_at,
            retain_until=retain_until,
            legal_hold_cleared=payload["legal_hold_cleared"],
            orphan_proven=payload["orphan_proven"],
            provider_delete_authorized=payload[
                "provider_delete_authorized"
            ],
            fingerprint=payload["fingerprint"],
        )
    except LegalEvidenceRetentionConstraintError as error:
        _raise(
            LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4A_R3_PERSISTED_RECORD_INVALID",
            error,
        )
    except (KeyError, TypeError, ValueError) as error:
        _raise(
            LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4A_R3_PERSISTED_RECORD_INVALID",
            error,
        )


def _same(
    expected: LegalEvidenceRetentionConstraint,
    row: object,
) -> LegalEvidenceRetentionConstraint:
    """Require one durable row to equal one exact immutable constraint."""

    actual = _hydrate(
        row
    )

    if actual != expected:
        _raise(
            LegalEvidenceRetentionConstraintConflictError,
            "L10A2R_C4D4A_R3_IMMUTABLE_REPLAY_DIVERGENCE",
        )

    return actual


class LegalEvidenceRetentionConstraintRegistry:
    """Immutable tenant-scoped durable retention-constraint registry."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        """Bind one registry instance to one collection-like target."""

        self._collection = _target(
            collection
        )

    def ensure_indexes(
        self,
    ) -> None:
        """Create exact durable identities; never create TTL deletion."""

        try:
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

            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "source_evidence_reference",
                        ASCENDING,
                    ),
                ],
                unique=False,
                name=INDEX_TENANT_SOURCE_EVIDENCE,
            )
        except PyMongoError as error:
            _raise(
                LegalEvidenceRetentionConstraintPersistenceError,
                "L10A2R_C4D4A_R3_INDEX_CREATION_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceRetentionConstraintPersistenceError,
                "L10A2R_C4D4A_R3_COLLECTION_INTERFACE_INVALID",
                error,
            )

    def _find_identity_rows(
        self,
        value: LegalEvidenceRetentionConstraint,
        *,
        session: Any,
    ) -> tuple[object | None, object | None]:
        """Read every immutable identity used for replay adjudication."""

        try:
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
                LegalEvidenceRetentionConstraintPersistenceError,
                "L10A2R_C4D4A_R3_READ_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceRetentionConstraintPersistenceError,
                "L10A2R_C4D4A_R3_COLLECTION_INTERFACE_INVALID",
                error,
            )

        return (
            by_fingerprint,
            by_provider_object,
        )

    def create_or_replay(
        self,
        value: LegalEvidenceRetentionConstraint,
        *,
        session: Any,
    ) -> LegalEvidenceRetentionConstraint:
        """Persist once or return one exact immutable retention replay."""

        tx = _active_transaction(
            session
        )

        validated = _validated_value(
            value
        )

        document = _document(
            validated
        )

        rows = self._find_identity_rows(
            validated,
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
                    validated,
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
                    LegalEvidenceRetentionConstraintConflictError,
                    "L10A2R_C4D4A_R3_IDENTITY_ROWS_DIVERGE",
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
                    LegalEvidenceRetentionConstraintPersistenceError,
                    "L10A2R_C4D4A_R3_INSERT_NOT_ACKNOWLEDGED",
                )

        except DuplicateKeyError as error:
            _raise(
                LegalEvidenceRetentionConstraintConflictError,
                "L10A2R_C4D4A_R3_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )
        except LegalEvidenceRetentionConstraintRegistryError:
            raise
        except PyMongoError as error:
            _raise(
                LegalEvidenceRetentionConstraintPersistenceError,
                "L10A2R_C4D4A_R3_INSERT_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceRetentionConstraintPersistenceError,
                "L10A2R_C4D4A_R3_COLLECTION_INTERFACE_INVALID",
                error,
            )

        return validated

    def get_by_fingerprint(
        self,
        *,
        tenant_id: str,
        fingerprint: str,
        session: Any,
    ) -> LegalEvidenceRetentionConstraint:
        """Return one exact tenant+constraint-fingerprint durable fact."""

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
                fingerprint,
                str,
            )
            or not fingerprint
        ):
            _raise(
                LegalEvidenceRetentionConstraintNotFoundError,
                "L10A2R_C4D4A_R3_NOT_FOUND",
            )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id":
                        tenant_id,
                    "fingerprint":
                        fingerprint,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                LegalEvidenceRetentionConstraintPersistenceError,
                "L10A2R_C4D4A_R3_READ_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceRetentionConstraintPersistenceError,
                "L10A2R_C4D4A_R3_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if row is None:
            _raise(
                LegalEvidenceRetentionConstraintNotFoundError,
                "L10A2R_C4D4A_R3_NOT_FOUND",
            )

        value = _hydrate(
            row
        )

        if (
            value.tenant_id != tenant_id
            or value.fingerprint != fingerprint
        ):
            _raise(
                LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
                "L10A2R_C4D4A_R3_PERSISTED_SCOPE_MISMATCH",
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
    ) -> LegalEvidenceRetentionConstraint:
        """Return the exact durable constraint for one provider object."""

        tx = _active_transaction(
            session
        )

        identity = (
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
            for item in identity
        ):
            _raise(
                LegalEvidenceRetentionConstraintNotFoundError,
                "L10A2R_C4D4A_R3_NOT_FOUND",
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
                LegalEvidenceRetentionConstraintPersistenceError,
                "L10A2R_C4D4A_R3_READ_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceRetentionConstraintPersistenceError,
                "L10A2R_C4D4A_R3_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if row is None:
            _raise(
                LegalEvidenceRetentionConstraintNotFoundError,
                "L10A2R_C4D4A_R3_NOT_FOUND",
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
                LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
                "L10A2R_C4D4A_R3_PERSISTED_SCOPE_MISMATCH",
            )

        return value


__all__ = [
    "COLLECTION",
    "INDEX_TENANT_FINGERPRINT",
    "INDEX_TENANT_PROVIDER_OBJECT",
    "INDEX_TENANT_SOURCE_EVIDENCE",
    "VERSION",
    "LegalEvidenceRetentionConstraintConflictError",
    "LegalEvidenceRetentionConstraintNotFoundError",
    "LegalEvidenceRetentionConstraintPersistedRecordInvalidError",
    "LegalEvidenceRetentionConstraintPersistenceError",
    "LegalEvidenceRetentionConstraintRegistry",
    "LegalEvidenceRetentionConstraintRegistryError",
    "LegalEvidenceRetentionConstraintTransactionRequiredError",
]


# ARTIFACT: legal_evidence_retention_constraint_registry.py
# VERSION: v1.0.0-L10A2R-C4D4A-R3-RETENTION-CONSTRAINT-REGISTRY
# AUTHORITY BOUNDARY: durable exact retention-constraint persistence/replay only
# TENANT POSTURE: every durable identity and read is exact tenant scoped
# PROVIDER OBJECT POSTURE: one immutable constraint per exact object version
# SOURCE POSTURE: source evidence is persisted provenance, never selected here
# TRANSACTION POSTURE: caller owns one already-active Mongo transaction
# REPLAY POSTURE: exact immutable replay only; divergence fails closed
# CORRUPTION POSTURE: strict domain reconstruction; no self-healing
# TTL POSTURE: no TTL index or wall-clock deletion
# RETENTION POSTURE: persistence never asserts satisfaction or legal sufficiency
# LEGAL HOLD POSTURE: no issue, release or clearance authority
# ORPHAN POSTURE: no orphan inference or proof authority
# DELETION POSTURE: no update/delete/authorization/provider mutation authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# FAIL-CLOSED POSTURE: transaction absence, divergence, corruption and Mongo failure reject
# END OF WILSY OS SOVEREIGN ARTIFACT
