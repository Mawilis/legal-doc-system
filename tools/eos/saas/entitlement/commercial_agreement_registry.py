"""Durable, revision-guarded tenant commercial agreement registry.

Authority: immutable agreement history and explicit currentness only.
Transaction lifecycle, retries and unknown-commit reconciliation belong to callers.
No product entitlement, IAM, invoice, payment or settlement authority is granted.
"""
from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
import hashlib
import json
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.entitlement.commercial_agreement import (
    CommercialAgreement,
    CommercialAgreementError,
    CommercialAgreementState,
)

VERSION: Final[str] = "v1.0.0-EOS-COMMERCIAL-AGREEMENT-REGISTRY"
HISTORY_SCHEMA: Final[str] = "WILSY-COMMERCIAL-AGREEMENT-HISTORY/V1"
CURRENT_SCHEMA: Final[str] = "WILSY-COMMERCIAL-AGREEMENT-CURRENT/V1"
HISTORY_COLLECTION: Final[str] = "tenant_commercial_agreement_history"
CURRENT_COLLECTION: Final[str] = "tenant_commercial_agreement_current"
HISTORY_REVISION_INDEX_NAME: Final[str] = "commercial_agreement_tenant_revision_unique"
HISTORY_FINGERPRINT_INDEX_NAME: Final[str] = "commercial_agreement_tenant_fingerprint_unique"
CURRENT_IDENTITY_INDEX_NAME: Final[str] = "commercial_agreement_current_tenant_identity_unique"
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")


class CommercialAgreementRegistryError(RuntimeError):
    """Base fail-closed agreement persistence error."""

    def __init__(self, code: str = "COMMERCIAL_AGREEMENT_REGISTRY_ERROR") -> None:
        self.code = code
        super().__init__(code)


class CommercialAgreementRegistryTransactionRequiredError(CommercialAgreementRegistryError):
    pass


class CommercialAgreementRegistryNotFoundError(CommercialAgreementRegistryError):
    pass


class CommercialAgreementRegistryConflictError(CommercialAgreementRegistryError):
    pass


class CommercialAgreementRegistryRetryRequiredError(CommercialAgreementRegistryError):
    pass


class CommercialAgreementRegistryPersistedRecordInvalidError(CommercialAgreementRegistryError):
    pass


class CommercialAgreementRegistryPersistenceUnavailableError(CommercialAgreementRegistryError):
    pass


class CommercialAgreementPersistenceOutcome(StrEnum):
    CREATED = "CREATED"
    TRANSITIONED = "TRANSITIONED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


def _collection(value: Any, label: str) -> Any:
    if value is None:
        raise CommercialAgreementRegistryError(f"{label}_COLLECTION_REQUIRED")
    try:
        return value.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN)
    except AttributeError:
        return value


def _transaction(session: Any) -> Any:
    if session is None:
        raise CommercialAgreementRegistryTransactionRequiredError(
            "COMMERCIAL_AGREEMENT_ACTIVE_TRANSACTION_REQUIRED"
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        raise CommercialAgreementRegistryTransactionRequiredError(
            "COMMERCIAL_AGREEMENT_ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _sha3(value: object) -> str:
    return hashlib.sha3_512(
        json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _pointer(agreement: CommercialAgreement) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema": CURRENT_SCHEMA,
        "version": VERSION,
        "entity_type": "TenantCommercialAgreementCurrent",
        "tenant_id": agreement.tenant_id,
        "agreement_id": agreement.agreement_id,
        "lifecycle_revision": agreement.lifecycle_revision,
        "agreement_fingerprint": agreement.fingerprint,
    }
    payload["pointer_fingerprint"] = _sha3(payload)
    return payload


def _history_record(agreement: CommercialAgreement) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema": HISTORY_SCHEMA,
        "version": VERSION,
        "entity_type": "TenantCommercialAgreementHistory",
        "tenant_id": agreement.tenant_id,
        "agreement_id": agreement.agreement_id,
        "lifecycle_revision": agreement.lifecycle_revision,
        "agreement_fingerprint": agreement.fingerprint,
        "agreement_payload": agreement.to_dict(),
    }
    payload["evidence_identity"] = _sha3({
        "tenant_id": agreement.tenant_id,
        "agreement_id": agreement.agreement_id,
        "lifecycle_revision": agreement.lifecycle_revision,
        "agreement_fingerprint": agreement.fingerprint,
    })
    return payload


def _hydrate_history(row: Mapping[str, Any]) -> CommercialAgreement:
    raw = dict(row)
    raw.pop("_id", None)
    expected = {
        "schema", "version", "entity_type", "tenant_id", "agreement_id",
        "lifecycle_revision", "agreement_fingerprint", "agreement_payload",
        "evidence_identity",
    }
    if set(raw) != expected or raw.get("schema") != HISTORY_SCHEMA or raw.get("version") != VERSION:
        raise CommercialAgreementRegistryPersistedRecordInvalidError(
            "COMMERCIAL_AGREEMENT_HISTORY_SCHEMA_INVALID"
        )
    payload = raw.get("agreement_payload")
    if not isinstance(payload, Mapping):
        raise CommercialAgreementRegistryPersistedRecordInvalidError(
            "COMMERCIAL_AGREEMENT_HISTORY_PAYLOAD_INVALID"
        )
    try:
        agreement = CommercialAgreement(**dict(payload))
    except (CommercialAgreementError, TypeError, ValueError) as error:
        raise CommercialAgreementRegistryPersistedRecordInvalidError(
            "COMMERCIAL_AGREEMENT_HISTORY_HYDRATION_INVALID"
        ) from error
    if (
        agreement.tenant_id != raw.get("tenant_id")
        or agreement.agreement_id != raw.get("agreement_id")
        or agreement.lifecycle_revision != raw.get("lifecycle_revision")
        or agreement.fingerprint != raw.get("agreement_fingerprint")
        or raw.get("evidence_identity") != _history_record(agreement)["evidence_identity"]
    ):
        raise CommercialAgreementRegistryPersistedRecordInvalidError(
            "COMMERCIAL_AGREEMENT_HISTORY_CORRELATION_INVALID"
        )
    return agreement


def _read_one(collection: Any, query: dict[str, object], session: Any) -> Mapping[str, Any] | None:
    try:
        return collection.find_one(query, session=session)
    except PyMongoError as error:
        raise CommercialAgreementRegistryPersistenceUnavailableError(
            "COMMERCIAL_AGREEMENT_MONGO_READ_FAILED"
        ) from error


def _get_revision(
    tenant_id: str, agreement_id: str, revision: int, history: Any, session: Any
) -> CommercialAgreement | None:
    row = _read_one(history, {
        "tenant_id": tenant_id,
        "agreement_id": agreement_id,
        "lifecycle_revision": revision,
    }, session)
    return None if row is None else _hydrate_history(row)


def _get_pointer(tenant_id: str, agreement_id: str, current: Any, session: Any) -> dict[str, Any] | None:
    row = _read_one(current, {"tenant_id": tenant_id, "agreement_id": agreement_id}, session)
    if row is None:
        return None
    raw = dict(row)
    raw.pop("_id", None)
    expected = {
        "schema", "version", "entity_type", "tenant_id", "agreement_id",
        "lifecycle_revision", "agreement_fingerprint", "pointer_fingerprint",
    }
    if set(raw) != expected or raw.get("schema") != CURRENT_SCHEMA or raw.get("version") != VERSION:
        raise CommercialAgreementRegistryPersistedRecordInvalidError(
            "COMMERCIAL_AGREEMENT_CURRENT_SCHEMA_INVALID"
        )
    fingerprint = raw.pop("pointer_fingerprint")
    if fingerprint != _sha3(raw):
        raise CommercialAgreementRegistryPersistedRecordInvalidError(
            "COMMERCIAL_AGREEMENT_CURRENT_FINGERPRINT_INVALID"
        )
    raw["pointer_fingerprint"] = fingerprint
    return raw


def ensure_indexes(history_collection: Any, current_collection: Any) -> None:
    history = _collection(history_collection, "HISTORY")
    current = _collection(current_collection, "CURRENT")
    try:
        history.create_index(
            [("tenant_id", ASCENDING), ("agreement_id", ASCENDING), ("lifecycle_revision", ASCENDING)],
            unique=True, name=HISTORY_REVISION_INDEX_NAME,
        )
        history.create_index(
            [("tenant_id", ASCENDING), ("agreement_fingerprint", ASCENDING)],
            unique=True, name=HISTORY_FINGERPRINT_INDEX_NAME,
        )
        current.create_index(
            [("tenant_id", ASCENDING), ("agreement_id", ASCENDING)],
            unique=True, name=CURRENT_IDENTITY_INDEX_NAME,
        )
    except (AttributeError, PyMongoError) as error:
        raise CommercialAgreementRegistryPersistenceUnavailableError(
            "COMMERCIAL_AGREEMENT_INDEX_INSTALL_FAILED"
        ) from error


def get_revision(
    tenant_id: str, agreement_id: str, lifecycle_revision: int,
    history_collection: Any, *, session: Any,
) -> CommercialAgreement:
    tx = _transaction(session)
    agreement = _get_revision(
        tenant_id, agreement_id, lifecycle_revision,
        _collection(history_collection, "HISTORY"), tx,
    )
    if agreement is None:
        raise CommercialAgreementRegistryNotFoundError(
            "COMMERCIAL_AGREEMENT_REVISION_NOT_FOUND"
        )
    return agreement


def get_current(
    tenant_id: str, agreement_id: str,
    history_collection: Any, current_collection: Any, *, session: Any,
) -> CommercialAgreement:
    tx = _transaction(session)
    history = _collection(history_collection, "HISTORY")
    current = _collection(current_collection, "CURRENT")
    pointer = _get_pointer(tenant_id, agreement_id, current, tx)
    if pointer is None:
        raise CommercialAgreementRegistryNotFoundError(
            "COMMERCIAL_AGREEMENT_CURRENT_NOT_FOUND"
        )
    agreement = _get_revision(
        tenant_id, agreement_id, pointer["lifecycle_revision"], history, tx
    )
    if agreement is None or _pointer(agreement) != pointer:
        raise CommercialAgreementRegistryPersistedRecordInvalidError(
            "COMMERCIAL_AGREEMENT_CURRENT_HISTORY_DIVERGENCE"
        )
    return agreement


def get_history(
    tenant_id: str, agreement_id: str, history_collection: Any, *, session: Any,
) -> tuple[CommercialAgreement, ...]:
    tx = _transaction(session)
    history = _collection(history_collection, "HISTORY")
    try:
        cursor = history.find(
            {"tenant_id": tenant_id, "agreement_id": agreement_id}, session=tx
        ).sort("lifecycle_revision", ASCENDING)
        result = tuple(_hydrate_history(row) for row in cursor)
    except CommercialAgreementRegistryError:
        raise
    except PyMongoError as error:
        raise CommercialAgreementRegistryPersistenceUnavailableError(
            "COMMERCIAL_AGREEMENT_HISTORY_READ_FAILED"
        ) from error
    revisions = tuple(item.lifecycle_revision for item in result)
    if revisions != tuple(sorted(set(revisions))):
        raise CommercialAgreementRegistryPersistedRecordInvalidError(
            "COMMERCIAL_AGREEMENT_HISTORY_ORDER_INVALID"
        )
    return result


def create_or_replay(
    agreement: CommercialAgreement,
    history_collection: Any,
    current_collection: Any,
    *,
    session: Any,
) -> tuple[CommercialAgreementPersistenceOutcome, CommercialAgreement]:
    tx = _transaction(session)
    if type(agreement) is not CommercialAgreement or (
        agreement.lifecycle_revision != 0
        or agreement.lifecycle_state is not CommercialAgreementState.DRAFT
    ):
        raise CommercialAgreementRegistryError(
            "COMMERCIAL_AGREEMENT_INITIAL_DRAFT_REQUIRED"
        )
    history = _collection(history_collection, "HISTORY")
    current = _collection(current_collection, "CURRENT")
    existing = _get_revision(
        agreement.tenant_id, agreement.agreement_id, 0, history, tx
    )
    pointer = _get_pointer(agreement.tenant_id, agreement.agreement_id, current, tx)
    if existing is not None:
        if existing.to_dict() != agreement.to_dict() or pointer != _pointer(existing):
            raise CommercialAgreementRegistryConflictError(
                "COMMERCIAL_AGREEMENT_INITIAL_REPLAY_CONFLICT"
            )
        return CommercialAgreementPersistenceOutcome.IDEMPOTENT_REPLAY, existing
    if pointer is not None:
        raise CommercialAgreementRegistryPersistedRecordInvalidError(
            "COMMERCIAL_AGREEMENT_POINTER_WITHOUT_HISTORY"
        )
    try:
        history.insert_one(_history_record(agreement), session=tx)
        current.insert_one(_pointer(agreement), session=tx)
    except DuplicateKeyError as error:
        raise CommercialAgreementRegistryRetryRequiredError(
            "COMMERCIAL_AGREEMENT_CREATE_RACE_RETRY"
        ) from error
    except PyMongoError as error:
        raise CommercialAgreementRegistryPersistenceUnavailableError(
            "COMMERCIAL_AGREEMENT_CREATE_FAILED"
        ) from error
    persisted = get_current(
        agreement.tenant_id, agreement.agreement_id, history, current, session=tx
    )
    if persisted.to_dict() != agreement.to_dict():
        raise CommercialAgreementRegistryPersistedRecordInvalidError(
            "COMMERCIAL_AGREEMENT_CREATE_READBACK_MISMATCH"
        )
    return CommercialAgreementPersistenceOutcome.CREATED, persisted


def transition(
    *,
    tenant_id: str,
    agreement_id: str,
    target_state: CommercialAgreementState | str,
    expected_revision: int,
    evidence_reference: str,
    evidence_fingerprint: str,
    occurred_at: Any,
    history_collection: Any,
    current_collection: Any,
    session: Any,
) -> tuple[CommercialAgreementPersistenceOutcome, CommercialAgreement]:
    tx = _transaction(session)
    history = _collection(history_collection, "HISTORY")
    current = _collection(current_collection, "CURRENT")
    existing = get_current(tenant_id, agreement_id, history, current, session=tx)
    if existing.lifecycle_revision == expected_revision + 1:
        prior = _get_revision(tenant_id, agreement_id, expected_revision, history, tx)
        if prior is None:
            raise CommercialAgreementRegistryPersistedRecordInvalidError(
                "COMMERCIAL_AGREEMENT_PRIOR_REVISION_MISSING"
            )
        try:
            replay = prior.transition(
                target_state, expected_revision=expected_revision,
                evidence_reference=evidence_reference,
                evidence_fingerprint=evidence_fingerprint, occurred_at=occurred_at,
            )
        except CommercialAgreementError as error:
            raise CommercialAgreementRegistryConflictError(
                "COMMERCIAL_AGREEMENT_TRANSITION_REPLAY_CONFLICT"
            ) from error
        if replay.to_dict() == existing.to_dict():
            return CommercialAgreementPersistenceOutcome.IDEMPOTENT_REPLAY, existing
        raise CommercialAgreementRegistryConflictError(
            "COMMERCIAL_AGREEMENT_TRANSITION_REPLAY_CONFLICT"
        )
    if existing.lifecycle_revision != expected_revision:
        raise CommercialAgreementRegistryConflictError(
            "COMMERCIAL_AGREEMENT_STALE_REVISION"
        )
    try:
        updated = existing.transition(
            target_state, expected_revision=expected_revision,
            evidence_reference=evidence_reference,
            evidence_fingerprint=evidence_fingerprint, occurred_at=occurred_at,
        )
    except CommercialAgreementError as error:
        raise CommercialAgreementRegistryConflictError(
            "COMMERCIAL_AGREEMENT_TRANSITION_INVALID"
        ) from error
    try:
        history.insert_one(_history_record(updated), session=tx)
        result = current.update_one(
            {
                "tenant_id": tenant_id,
                "agreement_id": agreement_id,
                "lifecycle_revision": expected_revision,
                "agreement_fingerprint": existing.fingerprint,
                "pointer_fingerprint": _pointer(existing)["pointer_fingerprint"],
            },
            {"$set": _pointer(updated)},
            session=tx,
        )
        if getattr(result, "matched_count", 0) != 1:
            raise CommercialAgreementRegistryRetryRequiredError(
                "COMMERCIAL_AGREEMENT_CAS_RETRY_REQUIRED"
            )
    except CommercialAgreementRegistryError:
        raise
    except DuplicateKeyError as error:
        raise CommercialAgreementRegistryRetryRequiredError(
            "COMMERCIAL_AGREEMENT_TRANSITION_RACE_RETRY"
        ) from error
    except PyMongoError as error:
        raise CommercialAgreementRegistryPersistenceUnavailableError(
            "COMMERCIAL_AGREEMENT_TRANSITION_FAILED"
        ) from error
    persisted = get_current(tenant_id, agreement_id, history, current, session=tx)
    if persisted.to_dict() != updated.to_dict():
        raise CommercialAgreementRegistryPersistedRecordInvalidError(
            "COMMERCIAL_AGREEMENT_TRANSITION_READBACK_MISMATCH"
        )
    return CommercialAgreementPersistenceOutcome.TRANSITIONED, persisted


class CommercialAgreementRegistry:
    """Static facade; no database client or transaction lifecycle ownership."""
    ensure_indexes = staticmethod(ensure_indexes)
    create_or_replay = staticmethod(create_or_replay)
    get_current = staticmethod(get_current)
    get_revision = staticmethod(get_revision)
    get_history = staticmethod(get_history)
    transition = staticmethod(transition)


__all__ = [
    "CommercialAgreementPersistenceOutcome",
    "CommercialAgreementRegistry",
    "CommercialAgreementRegistryConflictError",
    "CommercialAgreementRegistryError",
    "CommercialAgreementRegistryNotFoundError",
    "CommercialAgreementRegistryPersistedRecordInvalidError",
    "CommercialAgreementRegistryPersistenceUnavailableError",
    "CommercialAgreementRegistryRetryRequiredError",
    "CommercialAgreementRegistryTransactionRequiredError",
    "CURRENT_COLLECTION", "CURRENT_IDENTITY_INDEX_NAME", "CURRENT_SCHEMA",
    "HISTORY_COLLECTION", "HISTORY_FINGERPRINT_INDEX_NAME",
    "HISTORY_REVISION_INDEX_NAME", "HISTORY_SCHEMA", "VERSION",
    "create_or_replay", "ensure_indexes", "get_current", "get_history",
    "get_revision", "transition",
]
