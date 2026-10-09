"""WILSY OS durable Legal Evidence original binary write-intent registry.

TITLE: Legal Evidence Binary Write Intent Registry
VERSION: v1.0.0-L10A2R-C4D5C-BINARY-WRITE-INTENT-REGISTRY
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Persist the already-canonical provider-neutral
         LegalEvidenceBinaryWriteIntent before provider execution so later
         reconciliation can distinguish durable original WILSY intent evidence
         from provider observations without manufacturing provider success.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_evidence_binary_write_intent_registry.py
COLLABORATION / OWNERSHIP:
    L10A2R-A owns LegalEvidenceBinaryWriteIntent and its deterministic
    fingerprint. P5B owns capacity reservations and ingestion_intent_id.
    C4D5C owns only immutable durable registration of the canonical intent.
    Fresh ingestion orchestration, provider execution, cleanup discovery,
    orphan proof and deletion remain separate later gates.
CERTIFICATION / UPDATE DATE: 2026-09-30
CHANGELOG:
    v1.0.0-L10A2R-C4D5C establishes transactional immutable intent
    registration, exact tenant+ingestion-reference replay, exact
    tenant+write-intent-fingerprint lookup, strict hydration, corruption
    rejection and zero TTL deletion.
COMPLIANCE:
    Evidence durability only. This registry does not infer legal ownership,
    provider existence, retention satisfaction, hold release, orphan status or
    disposition authority.
SECURITY / PRIVACY POSTURE:
    Provider-neutral durable control-plane evidence. No credentials, provider
    locator, provider object version, raw file bytes or provider mutation.
TENANT BOUNDARY:
    Every operational read/write is exact tenant scoped. Cross-tenant absence
    remains indistinguishable from not-found. Pseudo-global tenants reject.
AUTHORITY BOUNDARY:
    Original binary write-intent durability and exact replay only. Registration
    is not proof that provider begin, upload, completion or metadata commit
    occurred and grants no orphan or deletion authority.
FINANCIAL AUTHORITY BOUNDARY:
    No pricing, invoicing, billing, payment, execution or settlement authority.
    Kennel EOS remains exclusive financial execution authority.
TRANSACTION BOUNDARY:
    Caller owns one already-active Mongo transaction. This registry never
    starts, commits, aborts or retries the transaction.
LEGACY / COVERAGE POSTURE:
    Absence of a C4D5C row is never by itself proof of orphan status. Objects
    predating certified registry coverage remain unresolved until a separately
    certified coverage/migration authority proves otherwise.
TTL POSTURE:
    No TTL index exists. Original write intent is durable audit/reconciliation
    evidence and must not disappear due only to wall-clock passage.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Final, Mapping, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryStoragePortError,
    LegalEvidenceBinaryWriteIntent,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D5C-BINARY-WRITE-INTENT-REGISTRY"
)

COLLECTION: Final[str] = "legal_evidence_binary_write_intents"

INDEX_TENANT_INGESTION: Final[str] = (
    "legal_evidence_binary_write_intents_tenant_ingestion_unique"
)
INDEX_TENANT_FINGERPRINT: Final[str] = (
    "legal_evidence_binary_write_intents_tenant_fingerprint_unique"
)
INDEX_TENANT_DOCUMENT_REGISTERED: Final[str] = (
    "legal_evidence_binary_write_intents_tenant_document_registered"
)

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$"
)
_SHA3_512: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "global_root",
        "root",
        "master",
        "*",
    }
)

_DOCUMENT_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "_id",
        "tenant_id",
        "case_matter_id",
        "document_id",
        "ingestion_reference",
        "media_type",
        "original_filename",
        "admitted_max_content_length",
        "schema",
        "write_intent_fingerprint",
        "registered_at",
        "record_fingerprint",
    }
)


class LegalEvidenceBinaryWriteIntentRegistryError(RuntimeError):
    """Base C4D5C registry error."""


class LegalEvidenceBinaryWriteIntentTransactionRequiredError(
    LegalEvidenceBinaryWriteIntentRegistryError
):
    """Caller did not supply one already-active Mongo transaction."""


class LegalEvidenceBinaryWriteIntentConflictError(
    LegalEvidenceBinaryWriteIntentRegistryError
):
    """Immutable intent identity or replay conflicts with durable evidence."""


class LegalEvidenceBinaryWriteIntentNotFoundError(
    LegalEvidenceBinaryWriteIntentRegistryError
):
    """Exact tenant-scoped durable intent was not found."""


class LegalEvidenceBinaryWriteIntentPersistedRecordInvalidError(
    LegalEvidenceBinaryWriteIntentRegistryError
):
    """Durable row failed strict canonical hydration."""


class LegalEvidenceBinaryWriteIntentPersistenceError(
    LegalEvidenceBinaryWriteIntentRegistryError
):
    """Mongo persistence or read operation failed."""


def _active_transaction(
    session: Any,
) -> Any:
    if session is None or not bool(
        getattr(
            session,
            "in_transaction",
            False,
        )
    ):
        raise LegalEvidenceBinaryWriteIntentTransactionRequiredError(
            "L10A2R_C4D5C_TRANSACTION_REQUIRED"
        )
    return session


def _identity(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or _IDENTITY.fullmatch(value) is None
    ):
        raise LegalEvidenceBinaryWriteIntentRegistryError(
            f"L10A2R_C4D5C_{name.upper()}_INVALID"
        )
    return value


def _tenant(
    value: object,
) -> str:
    tenant = _identity(
        "tenant_id",
        value,
    )

    if tenant.casefold() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceBinaryWriteIntentRegistryError(
            "L10A2R_C4D5C_TENANT_REQUIRED"
        )

    return tenant


def _sha3(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or _SHA3_512.fullmatch(value) is None
    ):
        raise LegalEvidenceBinaryWriteIntentRegistryError(
            f"L10A2R_C4D5C_{name.upper()}_INVALID"
        )
    return value


def _utc(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceBinaryWriteIntentRegistryError(
            f"L10A2R_C4D5C_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _timestamp(
    value: datetime,
) -> str:
    return value.astimezone(
        timezone.utc
    ).isoformat(
        timespec="microseconds"
    ).replace(
        "+00:00",
        "Z",
    )


def _parse_timestamp(
    value: object,
) -> datetime:
    if (
        not isinstance(value, str)
        or not value.endswith("Z")
    ):
        raise ValueError(
            "registered_at invalid"
        )

    parsed = datetime.fromisoformat(
        value[:-1] + "+00:00"
    )

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise ValueError(
            "registered_at invalid"
        )

    return parsed.astimezone(
        timezone.utc
    )


def _record_fingerprint(
    *,
    intent: LegalEvidenceBinaryWriteIntent,
    registered_at: datetime,
) -> str:
    payload = {
        "schema":
            "WILSY-LEGAL-EVIDENCE-BINARY-WRITE-INTENT-REGISTRY/V1",
        "tenant_id":
            intent.tenant_id,
        "case_matter_id":
            intent.case_matter_id,
        "document_id":
            intent.document_id,
        "ingestion_reference":
            intent.ingestion_reference,
        "media_type":
            intent.media_type,
        "original_filename":
            intent.original_filename,
        "admitted_max_content_length":
            intent.admitted_max_content_length,
        "intent_schema":
            intent.schema,
        "write_intent_fingerprint":
            intent.fingerprint,
        "registered_at":
            _timestamp(
                registered_at
            ),
    }

    raw = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        raw
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidenceBinaryWriteIntentRecord:
    """Immutable durable registration of one canonical binary write intent."""

    intent: LegalEvidenceBinaryWriteIntent
    registered_at: datetime
    record_fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        if type(self.intent) is not LegalEvidenceBinaryWriteIntent:
            raise LegalEvidenceBinaryWriteIntentRegistryError(
                "L10A2R_C4D5C_WRITE_INTENT_REQUIRED"
            )

        registered = _utc(
            "registered_at",
            self.registered_at,
        )

        digest = _record_fingerprint(
            intent=self.intent,
            registered_at=registered,
        )

        if self.record_fingerprint and (
            not isinstance(
                self.record_fingerprint,
                str,
            )
            or not hmac.compare_digest(
                self.record_fingerprint,
                digest,
            )
        ):
            raise LegalEvidenceBinaryWriteIntentRegistryError(
                "L10A2R_C4D5C_RECORD_FINGERPRINT_MISMATCH"
            )

        object.__setattr__(
            self,
            "registered_at",
            registered,
        )
        object.__setattr__(
            self,
            "record_fingerprint",
            digest,
        )


def _document(
    record: LegalEvidenceBinaryWriteIntentRecord,
) -> dict[str, object]:
    intent = record.intent

    return {
        "tenant_id":
            intent.tenant_id,
        "case_matter_id":
            intent.case_matter_id,
        "document_id":
            intent.document_id,
        "ingestion_reference":
            intent.ingestion_reference,
        "media_type":
            intent.media_type,
        "original_filename":
            intent.original_filename,
        "admitted_max_content_length":
            intent.admitted_max_content_length,
        "schema":
            intent.schema,
        "write_intent_fingerprint":
            intent.fingerprint,
        "registered_at":
            _timestamp(
                record.registered_at
            ),
        "record_fingerprint":
            record.record_fingerprint,
    }


def _hydrate(
    row: Mapping[str, Any],
) -> LegalEvidenceBinaryWriteIntentRecord:
    try:
        keys = frozenset(
            row.keys()
        )

        if not keys.issubset(
            _DOCUMENT_FIELDS
        ):
            raise ValueError(
                "unexpected fields"
            )

        required = _DOCUMENT_FIELDS - {
            "_id",
        }

        if not required.issubset(
            keys
        ):
            raise ValueError(
                "missing fields"
            )

        intent = LegalEvidenceBinaryWriteIntent(
            tenant_id=cast(
                str,
                row["tenant_id"],
            ),
            case_matter_id=cast(
                str,
                row["case_matter_id"],
            ),
            document_id=cast(
                str,
                row["document_id"],
            ),
            ingestion_reference=cast(
                str,
                row["ingestion_reference"],
            ),
            media_type=cast(
                str,
                row["media_type"],
            ),
            original_filename=cast(
                str,
                row["original_filename"],
            ),
            admitted_max_content_length=cast(
                int,
                row[
                    "admitted_max_content_length"
                ],
            ),
            schema=cast(
                str,
                row["schema"],
            ),
            fingerprint=cast(
                str,
                row[
                    "write_intent_fingerprint"
                ],
            ),
        )

        registered = _parse_timestamp(
            row["registered_at"]
        )

        record = LegalEvidenceBinaryWriteIntentRecord(
            intent=intent,
            registered_at=registered,
            record_fingerprint=cast(
                str,
                row["record_fingerprint"],
            ),
        )

        return record

    except (
        KeyError,
        TypeError,
        ValueError,
        LegalEvidenceBinaryStoragePortError,
        LegalEvidenceBinaryWriteIntentRegistryError,
    ) as error:
        raise (
            LegalEvidenceBinaryWriteIntentPersistedRecordInvalidError(
                "L10A2R_C4D5C_PERSISTED_RECORD_INVALID"
            )
        ) from error


def _raise_mongo(
    code: str,
    error: BaseException,
) -> NoReturn:
    raise LegalEvidenceBinaryWriteIntentPersistenceError(
        code
    ) from error


class LegalEvidenceBinaryWriteIntentRegistry:
    """Persist and retrieve immutable original Legal Evidence write intents."""

    __slots__ = (
        "_collection",
    )

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = collection

    def ensure_indexes(
        self,
    ) -> None:
        """Create exact durable indexes; never create TTL deletion."""

        try:
            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "ingestion_reference",
                        ASCENDING,
                    ),
                ],
                unique=True,
                name=INDEX_TENANT_INGESTION,
            )

            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "write_intent_fingerprint",
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
                        "document_id",
                        ASCENDING,
                    ),
                    (
                        "registered_at",
                        ASCENDING,
                    ),
                ],
                unique=False,
                name=INDEX_TENANT_DOCUMENT_REGISTERED,
            )

        except PyMongoError as error:
            _raise_mongo(
                "L10A2R_C4D5C_INDEX_CREATION_FAILED",
                error,
            )

    def create_or_replay(
        self,
        intent: LegalEvidenceBinaryWriteIntent,
        *,
        registered_at: datetime,
        session: Any,
    ) -> LegalEvidenceBinaryWriteIntentRecord:
        """Persist one immutable intent registration or return exact replay."""

        tx = _active_transaction(
            session
        )

        if type(intent) is not LegalEvidenceBinaryWriteIntent:
            raise LegalEvidenceBinaryWriteIntentConflictError(
                "L10A2R_C4D5C_WRITE_INTENT_REQUIRED"
            )

        record = LegalEvidenceBinaryWriteIntentRecord(
            intent=intent,
            registered_at=registered_at,
        )

        try:
            existing = self._collection.find_one(
                {
                    "tenant_id":
                        intent.tenant_id,
                    "ingestion_reference":
                        intent.ingestion_reference,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(
                "L10A2R_C4D5C_READ_FAILED",
                error,
            )

        if existing is not None:
            persisted = _hydrate(
                cast(
                    Mapping[str, Any],
                    existing,
                )
            )

            if persisted != record:
                raise LegalEvidenceBinaryWriteIntentConflictError(
                    "L10A2R_C4D5C_DIVERGENT_INGESTION_REFERENCE"
                )

            return persisted

        try:
            fingerprint_row = self._collection.find_one(
                {
                    "tenant_id":
                        intent.tenant_id,
                    "write_intent_fingerprint":
                        intent.fingerprint,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(
                "L10A2R_C4D5C_READ_FAILED",
                error,
            )

        if fingerprint_row is not None:
            persisted = _hydrate(
                cast(
                    Mapping[str, Any],
                    fingerprint_row,
                )
            )

            if persisted != record:
                raise LegalEvidenceBinaryWriteIntentConflictError(
                    "L10A2R_C4D5C_DIVERGENT_WRITE_INTENT_FINGERPRINT"
                )

            return persisted

        try:
            self._collection.insert_one(
                _document(
                    record
                ),
                session=tx,
            )
        except DuplicateKeyError as error:
            raise LegalEvidenceBinaryWriteIntentConflictError(
                "L10A2R_C4D5C_DUPLICATE_INTENT"
            ) from error
        except PyMongoError as error:
            _raise_mongo(
                "L10A2R_C4D5C_CREATE_FAILED",
                error,
            )

        return record

    def get_by_ingestion_reference(
        self,
        *,
        tenant_id: str,
        ingestion_reference: str,
        session: Any,
    ) -> LegalEvidenceBinaryWriteIntentRecord:
        """Return exact tenant+ingestion intent registration or scoped not-found."""

        tx = _active_transaction(
            session
        )
        tenant = _tenant(
            tenant_id
        )
        ingestion = _identity(
            "ingestion_reference",
            ingestion_reference,
        )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id":
                        tenant,
                    "ingestion_reference":
                        ingestion,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(
                "L10A2R_C4D5C_READ_FAILED",
                error,
            )

        if row is None:
            raise LegalEvidenceBinaryWriteIntentNotFoundError(
                "L10A2R_C4D5C_WRITE_INTENT_NOT_FOUND"
            )

        return _hydrate(
            cast(
                Mapping[str, Any],
                row,
            )
        )

    def get_by_fingerprint(
        self,
        *,
        tenant_id: str,
        write_intent_fingerprint: str,
        session: Any,
    ) -> LegalEvidenceBinaryWriteIntentRecord:
        """Return exact tenant+canonical-intent-fingerprint registration."""

        tx = _active_transaction(
            session
        )
        tenant = _tenant(
            tenant_id
        )
        fingerprint = _sha3(
            "write_intent_fingerprint",
            write_intent_fingerprint,
        )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id":
                        tenant,
                    "write_intent_fingerprint":
                        fingerprint,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise_mongo(
                "L10A2R_C4D5C_READ_FAILED",
                error,
            )

        if row is None:
            raise LegalEvidenceBinaryWriteIntentNotFoundError(
                "L10A2R_C4D5C_WRITE_INTENT_NOT_FOUND"
            )

        return _hydrate(
            cast(
                Mapping[str, Any],
                row,
            )
        )


__all__ = [
    "COLLECTION",
    "INDEX_TENANT_DOCUMENT_REGISTERED",
    "INDEX_TENANT_FINGERPRINT",
    "INDEX_TENANT_INGESTION",
    "VERSION",
    "LegalEvidenceBinaryWriteIntentConflictError",
    "LegalEvidenceBinaryWriteIntentNotFoundError",
    "LegalEvidenceBinaryWriteIntentPersistedRecordInvalidError",
    "LegalEvidenceBinaryWriteIntentPersistenceError",
    "LegalEvidenceBinaryWriteIntentRecord",
    "LegalEvidenceBinaryWriteIntentRegistry",
    "LegalEvidenceBinaryWriteIntentRegistryError",
    "LegalEvidenceBinaryWriteIntentTransactionRequiredError",
]


# ARTIFACT: legal_evidence_binary_write_intent_registry.py
# VERSION: v1.0.0-L10A2R-C4D5C-BINARY-WRITE-INTENT-REGISTRY
# AUTHORITY BOUNDARY: immutable original binary write-intent durability only
# TENANT POSTURE: exact tenant+ingestion/fingerprint scope; cross-tenant is not-found
# COVERAGE POSTURE: registry absence alone is never orphan proof
# PROVIDER POSTURE: registration does not assert begin/upload/completion/provider success
# TTL POSTURE: no TTL deletion
# FAIL-CLOSED POSTURE: replay divergence, corruption, transaction absence and Mongo failure reject
# DELETION POSTURE: no orphan proof, deletion authorization or provider delete authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
