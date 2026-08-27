"""Wilsy OS Kennel EOS immutable financial execution truth registry.

VERSION: v1.0.3-KENNEL-FINANCIAL-EXECUTION-TRUTH-REGISTRY-CORRUPTION-FIRST-RECONCILIATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Tenant-scoped append-only persistence; no transaction ownership or settlement.
CHANGELOG: v1.0.3 corrects duplicate-key reconciliation by enforcing durable domain hydration first, registry metadata validation second, corruption checks before replay/reuse, separate execution identity collision handling, and unresolved duplicate conflict classification.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError, PyMongoError

from ..domain.financial_execution import FinancialExecutionTruth, FinancialExecutionTruthError

VERSION = "v1.0.3-KENNEL-FINANCIAL-EXECUTION-TRUTH-REGISTRY-CORRUPTION-FIRST-RECONCILIATION"
COLLECTION = "kennel_financial_execution_truth"


class FinancialExecutionRegistryError(RuntimeError):
    """Base fail-closed persistence error."""


class FinancialExecutionNotFoundError(FinancialExecutionRegistryError):
    """Raised when tenant-scoped evidence is absent."""


class FinancialExecutionPersistedRecordInvalidError(FinancialExecutionRegistryError):
    """Raised when BSON cannot hydrate the immutable domain contract."""


class FinancialExecutionIdempotencyKeyReuseError(FinancialExecutionRegistryError):
    """Raised when a create key is reused with divergent semantics."""


class FinancialExecutionCreateConflictError(FinancialExecutionRegistryError):
    """Raised when duplicate identity is not an exact replay."""


class FinancialExecutionCreateOutcome(StrEnum):
    CREATED = "CREATED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


@dataclass(frozen=True)
class FinancialExecutionCreateResult:
    """Immutable create outcome and canonical execution truth."""

    outcome: FinancialExecutionCreateOutcome
    execution_truth: FinancialExecutionTruth


def _collection_or_raise(collection: Optional[Collection]) -> Collection:
    if collection is None:
        from ...kernel.db import get_database
        database = get_database()
        if database is None:
            raise FinancialExecutionRegistryError("FINANCIAL_EXECUTION_PERSISTENCE_UNAVAILABLE")
        collection = database[COLLECTION]
    return collection


def _fingerprint(truth: FinancialExecutionTruth, key: str) -> str:
    payload = {"execution_truth": truth.evidence_payload(), "create_idempotency_key": key}
    return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()

def _key(value: str) -> str:
    key = value.strip() if isinstance(value, str) else ""
    if not key or len(key) > 128:
        raise FinancialExecutionRegistryError("invalid idempotency key")
    return key

def _validate_persisted_registry_metadata(document: dict) -> tuple[str, str]:
    key = document.get("create_idempotency_key")
    fingerprint = document.get("create_fingerprint")
    if not isinstance(key, str) or not key.strip() or len(key.strip()) > 128 or key != key.strip() or not isinstance(fingerprint, str) or len(fingerprint) != 128 or any(ch not in "0123456789abcdef" for ch in fingerprint):
        raise FinancialExecutionPersistedRecordInvalidError("FINANCIAL_EXECUTION_PERSISTED_RECORD_INVALID")
    return key, fingerprint

def _text(value: object, field: str, max_length: int = 256) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > max_length:
        raise FinancialExecutionRegistryError(f"invalid {field}")
    return value.strip()


def _hydrate(document: dict) -> FinancialExecutionTruth:
    try:
        data = dict(document)
        data.pop("_id", None); data.pop("create_idempotency_key", None); data.pop("create_fingerprint", None)
        return FinancialExecutionTruth.from_mapping(data)
    except (TypeError, ValueError, FinancialExecutionTruthError) as error:
        raise FinancialExecutionPersistedRecordInvalidError("FINANCIAL_EXECUTION_PERSISTED_RECORD_INVALID") from error


class FinancialExecutionTruthRegistry:
    """Persists immutable execution evidence with caller-owned session support."""

    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        target = _collection_or_raise(collection)
        target.create_index([("tenant_id", ASCENDING), ("execution_truth_id", ASCENDING)], unique=True, name="tenant_execution_truth_identity_unique")
        target.create_index([("tenant_id", ASCENDING), ("payable_id", ASCENDING), ("create_idempotency_key", ASCENDING)], unique=True, name="tenant_payable_execution_create_idempotency_unique")
        target.create_index([("tenant_id", ASCENDING), ("provider", ASCENDING), ("provider_execution_reference", ASCENDING), ("executed_at", ASCENDING), ("execution_truth_id", ASCENDING)], name="tenant_provider_execution_timeline")
        target.create_index([("tenant_id", ASCENDING), ("release_authorization_id", ASCENDING), ("executed_at", ASCENDING), ("execution_truth_id", ASCENDING)], name="tenant_release_authorization_execution_timeline")
        target.create_index([("tenant_id", ASCENDING), ("payable_id", ASCENDING), ("executed_at", ASCENDING), ("execution_truth_id", ASCENDING)], name="tenant_payable_execution_timeline")
        target.create_index([("tenant_id", ASCENDING), ("execution_status", ASCENDING), ("executed_at", ASCENDING), ("execution_truth_id", ASCENDING)], name="tenant_execution_status_timeline")

    @staticmethod
    def create(execution_truth: FinancialExecutionTruth, idempotency_key: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionCreateResult:
        if not isinstance(execution_truth, FinancialExecutionTruth):
            raise FinancialExecutionRegistryError("execution_truth must be FinancialExecutionTruth")
        key = _key(idempotency_key)
        target = _collection_or_raise(collection); fingerprint = _fingerprint(execution_truth, key)
        document = {**execution_truth.to_dict(), "create_idempotency_key": key, "create_fingerprint": fingerprint}
        try:
            target.insert_one(document, session=session)
            return FinancialExecutionCreateResult(FinancialExecutionCreateOutcome.CREATED, execution_truth)
        except DuplicateKeyError as error:
            existing = target.find_one({"tenant_id": execution_truth.tenant_id, "payable_id": execution_truth.payable_id, "create_idempotency_key": key}, session=session)
            if existing is not None:
                durable_truth = _hydrate(existing)
                durable_key, durable_fingerprint = _validate_persisted_registry_metadata(existing)
                if durable_key != key:
                    raise FinancialExecutionPersistedRecordInvalidError("FINANCIAL_EXECUTION_PERSISTED_RECORD_INVALID") from error
                if durable_fingerprint != fingerprint:
                    raise FinancialExecutionIdempotencyKeyReuseError("FINANCIAL_EXECUTION_IDEMPOTENCY_KEY_REUSED") from error
                return FinancialExecutionCreateResult(FinancialExecutionCreateOutcome.IDEMPOTENT_REPLAY, durable_truth)
            identity_existing = target.find_one({"tenant_id": execution_truth.tenant_id, "execution_truth_id": execution_truth.execution_truth_id}, session=session)
            if identity_existing is not None:
                _hydrate(identity_existing)
                _validate_persisted_registry_metadata(identity_existing)
                raise FinancialExecutionCreateConflictError("FINANCIAL_EXECUTION_CREATE_CONFLICT") from error
            raise FinancialExecutionCreateConflictError("FINANCIAL_EXECUTION_CREATE_CONFLICT") from error
        except PyMongoError as error:
            raise FinancialExecutionRegistryError("FINANCIAL_EXECUTION_CREATE_FAILED") from error

    @staticmethod
    def get(tenant_id: str, execution_truth_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> Optional[FinancialExecutionTruth]:
        document = _collection_or_raise(collection).find_one({"tenant_id": _text(tenant_id, "tenant_id"), "execution_truth_id": _text(execution_truth_id, "execution_truth_id")}, session=session)
        return None if document is None else _hydrate(document)

    @staticmethod
    def _list(query: dict, limit: int, collection: Optional[Collection], session: Optional[ClientSession]) -> tuple[FinancialExecutionTruth, ...]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 250:
            raise FinancialExecutionRegistryError("limit must be between 1 and 250")
        return tuple(_hydrate(row) for row in _collection_or_raise(collection).find(query, session=session).sort([("executed_at", ASCENDING), ("execution_truth_id", ASCENDING)]).limit(limit))

    @staticmethod
    def list_for_payable(tenant_id: str, payable_id: str, limit: int = 100, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> tuple[FinancialExecutionTruth, ...]:
        return FinancialExecutionTruthRegistry._list({"tenant_id": _text(tenant_id, "tenant_id"), "payable_id": _text(payable_id, "payable_id")}, limit, collection, session)

    @staticmethod
    def get_by_idempotency_key(tenant_id: str, payable_id: str, idempotency_key: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> Optional[FinancialExecutionTruth]:
        key = _key(idempotency_key)
        document = _collection_or_raise(collection).find_one({"tenant_id": _text(tenant_id, "tenant_id"), "payable_id": _text(payable_id, "payable_id"), "create_idempotency_key": key}, session=session)
        return None if document is None else _hydrate(document)

    @staticmethod
    def list_for_provider_execution(tenant_id: str, provider: str, provider_execution_reference: str, limit: int = 100, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> tuple[FinancialExecutionTruth, ...]:
        return FinancialExecutionTruthRegistry._list({"tenant_id": _text(tenant_id, "tenant_id"), "provider": _text(provider, "provider"), "provider_execution_reference": _text(provider_execution_reference, "provider_execution_reference")}, limit, collection, session)

    @staticmethod
    def list_for_release_authorization(tenant_id: str, release_authorization_id: str, limit: int = 100, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> tuple[FinancialExecutionTruth, ...]:
        return FinancialExecutionTruthRegistry._list({"tenant_id": _text(tenant_id, "tenant_id"), "release_authorization_id": _text(release_authorization_id, "release_authorization_id")}, limit, collection, session)


# ARTIFACT: financial_execution_registry.py
# VERSION: v1.0.3-KENNEL-FINANCIAL-EXECUTION-TRUTH-REGISTRY-CORRUPTION-FIRST-RECONCILIATION
# AUTHORITY BOUNDARY: Kennel EOS owns execution truth; registry owns persistence only.
# END OF WILSY OS SOVEREIGN ARTIFACT
