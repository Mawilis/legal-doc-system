"""WILSY OS durable immutable Legal Evidence usage-observation registry.

TITLE: Legal Evidence Usage Observation Registry
VERSION: v1.0.0-L10A2Q-P3B-LEGAL-EVIDENCE-USAGE-OBSERVATION-REGISTRY
AUTHORITY: WILSY OS Core Governance
PURPOSE:
    Persist immutable P3A Legal Evidence usage observations append-only with
    exact tenant scope, caller-owned transaction propagation, deterministic
    idempotency and strict corruption detection.

EPITOME:
    USAGE OBSERVATION DERIVED
    != USAGE OBSERVATION DURABLY RECORDED
    != REMAINING CAPACITY
    != CAPACITY RESERVED
    != STORAGE ADMISSION

COLLABORATION / OWNERSHIP:
    L10A2Q-P3A owns immutable Legal Evidence usage-observation truth.
    This artifact owns append-only durability of those observations only.
    L10A2Q-P4 owns remaining-capacity derivation.
    L10A2Q-P5 owns reservation, expiry, concurrency and reconciliation.

CERTIFICATION / UPDATE DATE: 2026-09-30

TENANT BOUNDARY:
    Observation identity, idempotency and reads are always tenant scoped.
    Cross-tenant absence is indistinguishable from not-found.

TRANSACTION POSTURE:
    Caller owns the Mongo session and active transaction. This registry never
    starts, commits, aborts or retries a transaction on the caller's behalf.

AUTHORITY BOUNDARY:
    Append-only raw usage-observation durability only. Persistence grants no
    entitlement, quota, remaining-capacity, reservation, admission, billing,
    payment, settlement, execution, deletion, retention or legal-hold authority.

FAIL-CLOSED DECLARATION:
    Missing transaction, malformed inputs, unknown persisted fields, observation
    fingerprint drift, command-fingerprint drift, divergent replay, identity
    collision and Mongo failures reject.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Final, Mapping, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_evidence_usage_observation import (
    LegalEvidenceUsageObservation,
    LegalEvidenceUsageObservationError,
)
from tools.eos.legal_operations.domain.legal_evidence_usage_window import (
    LegalEvidenceUsageWindow,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2Q-P3B-LEGAL-EVIDENCE-USAGE-OBSERVATION-REGISTRY"
)

COLLECTION: Final[str] = "legal_evidence_usage_observations"

INDEX_TENANT_OBSERVATION: Final[str] = (
    "legal_evidence_usage_tenant_observation_unique"
)
INDEX_TENANT_IDEMPOTENCY: Final[str] = (
    "legal_evidence_usage_tenant_idempotency_unique"
)
INDEX_TENANT_OCCURRED: Final[str] = (
    "legal_evidence_usage_tenant_occurred"
)
INDEX_TENANT_DOCUMENT_OCCURRED: Final[str] = (
    "legal_evidence_usage_tenant_document_occurred"
)

_HEX_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")

_OBSERVATION_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id",
    "usage_observation_id",
    "case_matter_id",
    "document_id",
    "content_reference",
    "content_fingerprint",
    "content_evidence_fingerprint",
    "storage_bytes_added",
    "monthly_ingress_bytes",
    "document_versions_added",
    "occurred_at",
    "schema",
    "observation_version",
    "fingerprint",
)

_ALLOWED_PERSISTED_FIELDS: Final[frozenset[str]] = frozenset(
    (
        *_OBSERVATION_FIELDS,
        "idempotency_key",
        "command_fingerprint",
        "_id",
    )
)


class LegalEvidenceUsageObservationRegistryError(RuntimeError):
    """Base error for durable Legal Evidence usage-observation persistence."""


class LegalEvidenceUsageObservationConflictError(
    LegalEvidenceUsageObservationRegistryError
):
    """Immutable observation/idempotency identity conflicts."""


class LegalEvidenceUsageObservationNotFoundError(
    LegalEvidenceUsageObservationRegistryError
):
    """No exact tenant-scoped usage observation exists."""


class LegalEvidenceUsageObservationTransactionRequiredError(
    LegalEvidenceUsageObservationRegistryError
):
    """Caller did not supply one active transaction."""


def _raise_mongo(error: PyMongoError) -> NoReturn:
    raise LegalEvidenceUsageObservationRegistryError(
        "L10A2Q_P3B_PERSISTENCE_UNAVAILABLE"
    ) from error


def _text(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or not value
        or len(value) > 512
    ):
        raise LegalEvidenceUsageObservationRegistryError(
            f"L10A2Q_P3B_{name.upper()}_INVALID"
        )
    return value


def _active_transaction(session: Any) -> Any:
    if session is None:
        raise LegalEvidenceUsageObservationTransactionRequiredError(
            "L10A2Q_P3B_TRANSACTION_REQUIRED"
        )

    active = getattr(session, "in_transaction", False)
    if callable(active):
        active = active()

    if active is not True:
        raise LegalEvidenceUsageObservationTransactionRequiredError(
            "L10A2Q_P3B_TRANSACTION_REQUIRED"
        )

    return session


def _target(collection: Any) -> Any:
    if collection is None:
        raise LegalEvidenceUsageObservationRegistryError(
            "L10A2Q_P3B_COLLECTION_REQUIRED"
        )
    return collection


def _p3c_as_of(value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceUsageObservationRegistryError(
            "L10A2Q_P3C_B_AS_OF_INVALID"
        )
    return value.astimezone(timezone.utc)


def _p3c_source_set_fingerprint(
    observations: tuple[LegalEvidenceUsageObservation, ...],
) -> str:
    payload = [
        {
            "usage_observation_id": item.usage_observation_id,
            "fingerprint": item.fingerprint,
        }
        for item in observations
    ]
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


def _command_fingerprint(
    observation: LegalEvidenceUsageObservation,
    idempotency_key: str,
) -> str:
    payload = {
        "tenant_id": observation.tenant_id,
        "idempotency_key": idempotency_key,
        "observation": observation.to_dict(),
    }
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


def _hydrate(
    row: Mapping[str, object],
) -> LegalEvidenceUsageObservation:
    try:
        if (
            not isinstance(row, Mapping)
            or not set(row).issubset(_ALLOWED_PERSISTED_FIELDS)
        ):
            raise LegalEvidenceUsageObservationRegistryError(
                "L10A2Q_P3B_CORRUPT_OBSERVATION"
            )

        if not set(_OBSERVATION_FIELDS).issubset(row):
            raise LegalEvidenceUsageObservationRegistryError(
                "L10A2Q_P3B_CORRUPT_OBSERVATION"
            )

        idempotency_key = row.get("idempotency_key")
        command_fingerprint = row.get("command_fingerprint")

        if (
            not isinstance(idempotency_key, str)
            or not idempotency_key.strip()
            or not isinstance(command_fingerprint, str)
            or _HEX_RE.fullmatch(command_fingerprint) is None
        ):
            raise LegalEvidenceUsageObservationRegistryError(
                "L10A2Q_P3B_CORRUPT_OBSERVATION"
            )

        payload = {
            field: row[field]
            for field in _OBSERVATION_FIELDS
        }

        observation = LegalEvidenceUsageObservation.from_dict(payload)

        expected = _command_fingerprint(
            observation,
            idempotency_key,
        )

        if not hmac.compare_digest(
            command_fingerprint,
            expected,
        ):
            raise LegalEvidenceUsageObservationRegistryError(
                "L10A2Q_P3B_CORRUPT_OBSERVATION"
            )

        return observation

    except (
        KeyError,
        TypeError,
        LegalEvidenceUsageObservationError,
    ) as error:
        raise LegalEvidenceUsageObservationRegistryError(
            "L10A2Q_P3B_CORRUPT_OBSERVATION"
        ) from error


def ensure_indexes(collection: Any) -> None:
    """Create the closed durable identity/read index surface."""
    target = _target(collection)

    try:
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("usage_observation_id", ASCENDING),
            ],
            name=INDEX_TENANT_OBSERVATION,
            unique=True,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("idempotency_key", ASCENDING),
            ],
            name=INDEX_TENANT_IDEMPOTENCY,
            unique=True,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("occurred_at", ASCENDING),
            ],
            name=INDEX_TENANT_OCCURRED,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("document_id", ASCENDING),
                ("occurred_at", ASCENDING),
            ],
            name=INDEX_TENANT_DOCUMENT_OCCURRED,
        )
    except PyMongoError as error:
        _raise_mongo(error)


class LegalEvidenceUsageObservationRegistry:
    """Append-only caller-transaction Legal Evidence usage registry."""

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        self._collection = _target(collection)

    def create_or_replay(
        self,
        observation: LegalEvidenceUsageObservation,
        *,
        idempotency_key: str,
        session: Any,
    ) -> LegalEvidenceUsageObservation:
        """Append exactly once or return one exact durable replay."""
        tx = _active_transaction(session)

        if type(observation) is not LegalEvidenceUsageObservation:
            raise LegalEvidenceUsageObservationRegistryError(
                "L10A2Q_P3B_OBSERVATION_REQUIRED"
            )

        key = _text("idempotency_key", idempotency_key)
        command = _command_fingerprint(observation, key)

        try:
            existing = self._collection.find_one(
                {
                    "tenant_id": observation.tenant_id,
                    "idempotency_key": key,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)

        if existing is not None:
            persisted = _hydrate(existing)
            if (
                persisted != observation
                or existing.get("command_fingerprint") != command
            ):
                raise LegalEvidenceUsageObservationConflictError(
                    "L10A2Q_P3B_DIVERGENT_IDEMPOTENCY"
                )
            return persisted

        try:
            identity = self._collection.find_one(
                {
                    "tenant_id": observation.tenant_id,
                    "usage_observation_id":
                        observation.usage_observation_id,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)

        if identity is not None:
            raise LegalEvidenceUsageObservationConflictError(
                "L10A2Q_P3B_DIVERGENT_OBSERVATION_IDENTITY"
            )

        document = observation.to_dict()
        document.update(
            {
                "idempotency_key": key,
                "command_fingerprint": command,
            }
        )

        try:
            self._collection.insert_one(
                document,
                session=tx,
            )
        except DuplicateKeyError as error:
            raise LegalEvidenceUsageObservationConflictError(
                "L10A2Q_P3B_DUPLICATE_OBSERVATION"
            ) from error
        except PyMongoError as error:
            _raise_mongo(error)

        return observation

    def get_complete_window_for_p4(
        self,
        *,
        tenant_id: str,
        document_id: str,
        as_of: datetime,
        session: Any,
    ) -> LegalEvidenceUsageWindow:
        """Return one exhaustive tenant/document P3C usage snapshot.

        Every persisted row for the requested tenant is strictly hydrated
        before temporal accounting. This deliberately avoids Mongo timestamp
        predicates that could hide malformed persisted evidence and falsely
        prove a complete usage window.
        """
        tx = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)
        document = _text("document_id", document_id)
        as_of_utc = _p3c_as_of(as_of)

        try:
            rows = self._collection.find(
                {
                    "tenant_id": tenant,
                },
                session=tx,
            )
            hydrated = tuple(
                _hydrate(row)
                for row in rows
            )
        except PyMongoError as error:
            _raise_mongo(error)

        for observation in hydrated:
            if observation.tenant_id != tenant:
                raise LegalEvidenceUsageObservationRegistryError(
                    "L10A2Q_P3B_CORRUPT_OBSERVATION"
                )

        ordered = tuple(
            sorted(
                hydrated,
                key=lambda item: (
                    item.occurred_at,
                    item.usage_observation_id,
                ),
            )
        )

        bounded = tuple(
            item
            for item in ordered
            if item.occurred_at <= as_of_utc
        )

        month_start = as_of_utc.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        monthly = tuple(
            item
            for item in bounded
            if month_start <= item.occurred_at <= as_of_utc
        )

        document_observations = tuple(
            item
            for item in bounded
            if item.document_id == document
        )

        return LegalEvidenceUsageWindow(
            tenant_id=tenant,
            document_id=document,
            as_of=as_of_utc,
            monthly_window_start=month_start,
            monthly_window_end=as_of_utc,
            tenant_observation_count=len(bounded),
            monthly_observation_count=len(monthly),
            document_observation_count=len(document_observations),
            tenant_storage_bytes_added=sum(
                item.storage_bytes_added
                for item in bounded
            ),
            monthly_ingress_bytes_added=sum(
                item.monthly_ingress_bytes
                for item in monthly
            ),
            document_versions_added=sum(
                item.document_versions_added
                for item in document_observations
            ),
            source_observation_set_fingerprint=(
                _p3c_source_set_fingerprint(bounded)
            ),
        )

    def get(
        self,
        *,
        tenant_id: str,
        usage_observation_id: str,
        session: Any,
    ) -> LegalEvidenceUsageObservation:
        """Return one exact tenant-scoped strictly hydrated observation."""
        tx = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)
        observation_id = _text(
            "usage_observation_id",
            usage_observation_id,
        )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "usage_observation_id": observation_id,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(error)

        if row is None:
            raise LegalEvidenceUsageObservationNotFoundError(
                "L10A2Q_P3B_OBSERVATION_NOT_FOUND"
            )

        observation = _hydrate(row)

        if (
            observation.tenant_id != tenant
            or observation.usage_observation_id != observation_id
        ):
            raise LegalEvidenceUsageObservationRegistryError(
                "L10A2Q_P3B_CORRUPT_OBSERVATION"
            )

        return observation


__all__ = [
    "COLLECTION",
    "INDEX_TENANT_DOCUMENT_OCCURRED",
    "INDEX_TENANT_IDEMPOTENCY",
    "INDEX_TENANT_OBSERVATION",
    "INDEX_TENANT_OCCURRED",
    "VERSION",
    "LegalEvidenceUsageObservationConflictError",
    "LegalEvidenceUsageObservationNotFoundError",
    "LegalEvidenceUsageObservationRegistry",
    "LegalEvidenceUsageObservationRegistryError",
    "LegalEvidenceUsageObservationTransactionRequiredError",
    "ensure_indexes",
]


# ARTIFACT: legal_evidence_usage_observation_registry.py
# VERSION: v1.0.0-L10A2Q-P3B-LEGAL-EVIDENCE-USAGE-OBSERVATION-REGISTRY
# AUTHORITY BOUNDARY: append-only raw Legal Evidence usage durability only
# TENANT POSTURE: exact tenant-scoped observation/idempotency/read identity
# TRANSACTION POSTURE: caller owns one active transaction
# FAIL-CLOSED POSTURE: corruption/divergence/collision/persistence failure rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
