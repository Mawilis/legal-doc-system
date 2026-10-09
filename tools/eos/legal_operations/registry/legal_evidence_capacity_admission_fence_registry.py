"""WILSY OS durable tenant Legal Evidence capacity-admission fence.

TITLE: Legal Evidence Capacity Admission Fence Registry
VERSION: v1.0.0-L10A2Q-P5C-A-LEGAL-EVIDENCE-CAPACITY-ADMISSION-FENCE
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Provide one durable tenant-scoped serialization primitive for capacity
    admission decisions that must not race across independent ingestion
    intents.

EPITOME:
    TENANT CAPACITY DECISION ATTEMPT
    -> TENANT ADMISSION FENCE CAS
    -> SERIALIZED TRANSACTION SNAPSHOT
    != CAPACITY AVAILABLE
    != CAPACITY RESERVED
    != USAGE COMMITTED
    != PROVIDER WRITE
    != AUTHORIZED AVAILABILITY

CONCURRENCY:
    Exactly one fence row exists per tenant. The first acquisition creates
    revision 1. Every later acquisition requires the exact current revision
    and advances it by one through Mongo CAS. Stale and competing acquisitions
    fail closed.

TRANSACTION:
    Operational reads and writes require one caller-owned already-active Mongo
    transaction. This registry never starts, commits, aborts or retries a
    transaction. Index installation is administrative.

EXPIRY:
    Fence evidence has no TTL. Wall-clock passage never removes coordination
    history or silently weakens capacity serialization.

AUTHORITY BOUNDARY:
    Coordination evidence only. This artifact owns no plan, entitlement,
    capacity, usage, reservation, provider, document, IAM, retention, billing,
    payment, settlement or financial execution authority.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError


VERSION: Final[str] = (
    "v1.0.0-L10A2Q-P5C-A-LEGAL-EVIDENCE-CAPACITY-ADMISSION-FENCE"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-EVIDENCE-CAPACITY-ADMISSION-FENCE/V1"
)
COLLECTION: Final[str] = (
    "legal_evidence_capacity_admission_fences"
)
INDEX_TENANT_FENCE: Final[str] = (
    "legal_evidence_capacity_admission_fence_tenant_unique"
)

_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,255}$"
)
_HEX_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)


class LegalEvidenceCapacityAdmissionFenceRegistryError(
    RuntimeError
):
    """Base P5C-A fence persistence error."""


class LegalEvidenceCapacityAdmissionFenceTransactionRequiredError(
    LegalEvidenceCapacityAdmissionFenceRegistryError
):
    """Caller did not provide one already-active transaction."""


class LegalEvidenceCapacityAdmissionFenceConflictError(
    LegalEvidenceCapacityAdmissionFenceRegistryError
):
    """Fence creation or CAS precondition failed."""


class LegalEvidenceCapacityAdmissionFenceNotFoundError(
    LegalEvidenceCapacityAdmissionFenceRegistryError
):
    """Exact tenant-scoped fence does not exist."""


class LegalEvidenceCapacityAdmissionFencePersistedRecordInvalidError(
    LegalEvidenceCapacityAdmissionFenceRegistryError
):
    """Persisted fence failed strict integrity hydration."""


class LegalEvidenceCapacityAdmissionFencePersistenceError(
    LegalEvidenceCapacityAdmissionFenceRegistryError
):
    """Mongo persistence operation failed."""


def _active_transaction(session: Any) -> Any:
    if (
        session is None
        or not bool(
            getattr(session, "in_transaction", False)
        )
    ):
        raise (
            LegalEvidenceCapacityAdmissionFenceTransactionRequiredError(
                "L10A2Q_P5CA_TRANSACTION_REQUIRED"
            )
        )
    return session


def _identity(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or not _IDENTITY_RE.fullmatch(value)
    ):
        raise ValueError(
            f"L10A2Q_P5CA_{name.upper()}_INVALID"
        )
    return value


def _revision(value: object) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        raise ValueError(
            "L10A2Q_P5CA_REVISION_INVALID"
        )
    return value


def _instant(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError(
            f"L10A2Q_P5CA_{name.upper()}_INVALID"
        )
    return value.astimezone(timezone.utc)


def _json_instant(value: datetime) -> str:
    return (
        value.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


@dataclass(frozen=True, slots=True)
class LegalEvidenceCapacityAdmissionFence:
    """Immutable tenant-scoped capacity-admission coordination evidence."""

    tenant_id: str
    revision: int
    advanced_at: datetime
    coordination_reference: str
    schema: str = SCHEMA
    fence_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _identity(
            "tenant_id",
            self.tenant_id,
        )
        revision = _revision(self.revision)
        advanced_at = _instant(
            "advanced_at",
            self.advanced_at,
        )
        coordination_reference = _identity(
            "coordination_reference",
            self.coordination_reference,
        )

        if (
            self.schema != SCHEMA
            or self.fence_version != VERSION
        ):
            raise ValueError(
                "L10A2Q_P5CA_IDENTITY_INVALID"
            )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "revision",
            revision,
        )
        object.__setattr__(
            self,
            "advanced_at",
            advanced_at,
        )
        object.__setattr__(
            self,
            "coordination_reference",
            coordination_reference,
        )

        payload = self._payload()
        digest = hashlib.sha3_512(
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        if self.fingerprint:
            if (
                not isinstance(
                    self.fingerprint,
                    str,
                )
                or not _HEX_RE.fullmatch(
                    self.fingerprint
                )
                or not hmac.compare_digest(
                    self.fingerprint,
                    digest,
                )
            ):
                raise ValueError(
                    "L10A2Q_P5CA_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def _payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "fence_version":
                self.fence_version,
            "tenant_id": self.tenant_id,
            "revision": self.revision,
            "advanced_at":
                _json_instant(
                    self.advanced_at
                ),
            "coordination_reference":
                self.coordination_reference,
        }

    def to_dict(self) -> dict[str, object]:
        """Return one defensive canonical serialized fence value."""
        payload = self._payload()
        payload["fingerprint"] = (
            self.fingerprint
        )
        return payload

    @classmethod
    def from_dict(
        cls,
        value: Mapping[str, object],
    ) -> LegalEvidenceCapacityAdmissionFence:
        """Strictly hydrate one canonical persisted fence."""
        if not isinstance(value, Mapping):
            raise ValueError(
                "L10A2Q_P5CA_SERIALIZED_FENCE_INVALID"
            )

        expected = {
            "schema",
            "fence_version",
            "tenant_id",
            "revision",
            "advanced_at",
            "coordination_reference",
            "fingerprint",
        }

        if set(value) != expected:
            raise ValueError(
                "L10A2Q_P5CA_SERIALIZED_FENCE_INVALID"
            )

        advanced_raw = value["advanced_at"]
        if not isinstance(
            advanced_raw,
            str,
        ):
            raise ValueError(
                "L10A2Q_P5CA_ADVANCED_AT_INVALID"
            )

        try:
            advanced_at = datetime.fromisoformat(
                advanced_raw.replace(
                    "Z",
                    "+00:00",
                )
            )
        except ValueError as error:
            raise ValueError(
                "L10A2Q_P5CA_ADVANCED_AT_INVALID"
            ) from error

        return cls(
            tenant_id=cast(
                str,
                value["tenant_id"],
            ),
            revision=cast(
                int,
                value["revision"],
            ),
            advanced_at=advanced_at,
            coordination_reference=cast(
                str,
                value[
                    "coordination_reference"
                ],
            ),
            schema=cast(
                str,
                value["schema"],
            ),
            fence_version=cast(
                str,
                value["fence_version"],
            ),
            fingerprint=cast(
                str,
                value["fingerprint"],
            ),
        )


def _hydrate(
    raw: Mapping[str, object],
) -> LegalEvidenceCapacityAdmissionFence:
    try:
        payload = {
            key: value
            for key, value in raw.items()
            if key != "_id"
        }
        fence = (
            LegalEvidenceCapacityAdmissionFence.from_dict(
                payload
            )
        )
    except (
        TypeError,
        ValueError,
        KeyError,
    ) as error:
        raise (
            LegalEvidenceCapacityAdmissionFencePersistedRecordInvalidError(
                "L10A2Q_P5CA_PERSISTED_RECORD_INVALID"
            )
        ) from error

    return fence


def _raise_mongo(
    code: str,
    error: PyMongoError,
) -> NoReturn:
    raise (
        LegalEvidenceCapacityAdmissionFencePersistenceError(
            code
        )
    ) from error


class LegalEvidenceCapacityAdmissionFenceRegistry:
    """Durable tenant-only capacity-admission serialization fence."""

    __slots__ = ("_collection",)

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Install exactly one unique tenant fence index; never TTL."""
        try:
            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    )
                ],
                unique=True,
                name=INDEX_TENANT_FENCE,
            )
        except PyMongoError as error:
            _raise_mongo(
                "L10A2Q_P5CA_INDEX_CREATION_FAILED",
                error,
            )

    def get(
        self,
        *,
        tenant_id: str,
        session: Any,
    ) -> LegalEvidenceCapacityAdmissionFence:
        """Return one exact tenant-scoped fence under caller transaction."""
        tx = _active_transaction(
            session
        )
        tenant = _identity(
            "tenant_id",
            tenant_id,
        )

        try:
            row = (
                self._collection.find_one(
                    {
                        "tenant_id": tenant,
                    },
                    session=tx,
                )
            )
        except PyMongoError as error:
            _raise_mongo(
                "L10A2Q_P5CA_READ_FAILED",
                error,
            )

        if row is None:
            raise (
                LegalEvidenceCapacityAdmissionFenceNotFoundError(
                    "L10A2Q_P5CA_FENCE_NOT_FOUND"
                )
            )

        fence = _hydrate(
            cast(
                Mapping[str, object],
                row,
            )
        )

        if fence.tenant_id != tenant:
            raise (
                LegalEvidenceCapacityAdmissionFencePersistedRecordInvalidError(
                    "L10A2Q_P5CA_PERSISTED_RECORD_INVALID"
                )
            )

        return fence

    def advance(
        self,
        *,
        tenant_id: str,
        expected_revision: int | None,
        coordination_reference: str,
        advanced_at: datetime,
        session: Any,
    ) -> LegalEvidenceCapacityAdmissionFence:
        """Create revision 1 or CAS-advance one exact tenant fence."""
        tx = _active_transaction(
            session
        )
        tenant = _identity(
            "tenant_id",
            tenant_id,
        )
        reference = _identity(
            "coordination_reference",
            coordination_reference,
        )
        observed_at = _instant(
            "advanced_at",
            advanced_at,
        )

        if (
            expected_revision is not None
            and (
                isinstance(
                    expected_revision,
                    bool,
                )
                or not isinstance(
                    expected_revision,
                    int,
                )
                or expected_revision < 1
            )
        ):
            raise (
                LegalEvidenceCapacityAdmissionFenceConflictError(
                    "L10A2Q_P5CA_EXPECTED_REVISION_MISMATCH"
                )
            )

        try:
            row = (
                self._collection.find_one(
                    {
                        "tenant_id": tenant,
                    },
                    session=tx,
                )
            )
        except PyMongoError as error:
            _raise_mongo(
                "L10A2Q_P5CA_READ_FAILED",
                error,
            )

        if row is None:
            if expected_revision is not None:
                raise (
                    LegalEvidenceCapacityAdmissionFenceConflictError(
                        "L10A2Q_P5CA_INITIAL_REVISION_EXPECTED_NONE"
                    )
                )

            initial = (
                LegalEvidenceCapacityAdmissionFence(
                    tenant_id=tenant,
                    revision=1,
                    advanced_at=observed_at,
                    coordination_reference=reference,
                )
            )

            try:
                self._collection.insert_one(
                    initial.to_dict(),
                    session=tx,
                )
            except DuplicateKeyError as error:
                raise (
                    LegalEvidenceCapacityAdmissionFenceConflictError(
                        "L10A2Q_P5CA_FENCE_CAS_CONFLICT"
                    )
                ) from error
            except PyMongoError as error:
                _raise_mongo(
                    "L10A2Q_P5CA_CREATE_FAILED",
                    error,
                )

            return initial

        current = _hydrate(
            cast(
                Mapping[str, object],
                row,
            )
        )

        if current.tenant_id != tenant:
            raise (
                LegalEvidenceCapacityAdmissionFencePersistedRecordInvalidError(
                    "L10A2Q_P5CA_PERSISTED_RECORD_INVALID"
                )
            )

        if (
            expected_revision
            != current.revision
        ):
            raise (
                LegalEvidenceCapacityAdmissionFenceConflictError(
                    "L10A2Q_P5CA_EXPECTED_REVISION_MISMATCH"
                )
            )

        successor = (
            LegalEvidenceCapacityAdmissionFence(
                tenant_id=tenant,
                revision=current.revision + 1,
                advanced_at=observed_at,
                coordination_reference=reference,
            )
        )
        successor_payload = (
            successor.to_dict()
        )

        try:
            updated = (
                self._collection.find_one_and_update(
                    {
                        "tenant_id":
                            tenant,
                        "revision":
                            current.revision,
                        "fingerprint":
                            current.fingerprint,
                    },
                    {
                        "$set": {
                            "revision":
                                successor.revision,
                            "advanced_at":
                                successor_payload[
                                    "advanced_at"
                                ],
                            "coordination_reference":
                                successor.coordination_reference,
                            "fingerprint":
                                successor.fingerprint,
                        }
                    },
                    return_document=(
                        ReturnDocument.AFTER
                    ),
                    session=tx,
                )
            )
        except PyMongoError as error:
            _raise_mongo(
                "L10A2Q_P5CA_FENCE_CAS_FAILED",
                error,
            )

        if updated is None:
            try:
                competing = (
                    self._collection.find_one(
                        {
                            "tenant_id":
                                tenant,
                        },
                        session=tx,
                    )
                )
            except PyMongoError as error:
                _raise_mongo(
                    "L10A2Q_P5CA_CAS_CLASSIFICATION_FAILED",
                    error,
                )

            if competing is None:
                raise (
                    LegalEvidenceCapacityAdmissionFenceNotFoundError(
                        "L10A2Q_P5CA_FENCE_NOT_FOUND"
                    )
                )

            _hydrate(
                cast(
                    Mapping[str, object],
                    competing,
                )
            )
            raise (
                LegalEvidenceCapacityAdmissionFenceConflictError(
                    "L10A2Q_P5CA_FENCE_CAS_CONFLICT"
                )
            )

        persisted = _hydrate(
            cast(
                Mapping[str, object],
                updated,
            )
        )

        if (
            persisted.tenant_id != tenant
            or persisted != successor
        ):
            raise (
                LegalEvidenceCapacityAdmissionFencePersistedRecordInvalidError(
                    "L10A2Q_P5CA_PERSISTED_RECORD_INVALID"
                )
            )

        return persisted


__all__ = [
    "COLLECTION",
    "INDEX_TENANT_FENCE",
    "SCHEMA",
    "VERSION",
    "LegalEvidenceCapacityAdmissionFence",
    "LegalEvidenceCapacityAdmissionFenceConflictError",
    "LegalEvidenceCapacityAdmissionFenceNotFoundError",
    "LegalEvidenceCapacityAdmissionFencePersistedRecordInvalidError",
    "LegalEvidenceCapacityAdmissionFencePersistenceError",
    "LegalEvidenceCapacityAdmissionFenceRegistry",
    "LegalEvidenceCapacityAdmissionFenceRegistryError",
    "LegalEvidenceCapacityAdmissionFenceTransactionRequiredError",
]


# ARTIFACT: legal_evidence_capacity_admission_fence_registry.py
# VERSION: v1.0.0-L10A2Q-P5C-A-LEGAL-EVIDENCE-CAPACITY-ADMISSION-FENCE
# AUTHORITY BOUNDARY: tenant capacity admission serialization evidence only
# TENANT POSTURE: exactly one durable coordination fence per tenant
# TRANSACTION POSTURE: caller owns one already-active transaction
# EXPIRY POSTURE: no TTL; coordination evidence is never wall-clock deleted
# RECONCILIATION POSTURE: P5D remains owner of semantic reservation reconciliation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
