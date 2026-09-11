"""TITLE: Kennel Financial Execution Truth and Neutral Fact Registry
VERSION: v2.1.0-M11-P5-R2E-R4-R3
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Keep strict historical AP truth persistence separate from neutral execution-fact persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/registry/financial_execution_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS execution-evidence persistence owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v2.1.0-M11-P5-R2E-R4-R3 adds canonical pre-insert exact replay and propagates active-transaction duplicate races for caller-owned whole-transaction retry.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Strict BSON hydration; no raw credentials or provider payloads.
TENANT BOUNDARY: Every identity, attempt lookup, replay, and conflict query includes tenant_id.
AUTHORITY BOUNDARY: Registry persists supplied immutable evidence; it owns no provider or transaction lifecycle.
FINANCIAL AUTHORITY BOUNDARY: Neither registry creates settlement, paid state, or receivable closure.
TRANSACTION BOUNDARY: Caller-owned Mongo sessions propagate unchanged; no transaction starts, commits, aborts, or retries.
FAIL-CLOSED DECLARATION: Unknown/missing fields, corrupt fingerprints, divergent replay, and duplicate races reject.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

from pymongo import ASCENDING
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from ..domain.financial_execution import (
    FinancialExecutionFact,
    FinancialExecutionFactError,
    FinancialExecutionTruth,
    FinancialExecutionTruthError,
)

VERSION = "v2.1.0-M11-P5-R2E-R4-R3"
COLLECTION = "kennel_financial_execution_truth"
FACT_COLLECTION = "kennel_financial_execution_facts"


class FinancialExecutionRegistryError(RuntimeError):
    """Base fail-closed persistence error for historical AP truth."""


class FinancialExecutionNotFoundError(FinancialExecutionRegistryError):
    """Raised when tenant-scoped AP evidence is absent."""


class FinancialExecutionPersistedRecordInvalidError(FinancialExecutionRegistryError):
    """Raised when BSON cannot hydrate historical AP truth."""


class FinancialExecutionIdempotencyKeyReuseError(FinancialExecutionRegistryError):
    """Raised when an AP create key is reused with divergent semantics."""


class FinancialExecutionCreateConflictError(FinancialExecutionRegistryError):
    """Raised when AP duplicate identity is not an exact replay."""


class FinancialExecutionCreateOutcome(StrEnum):
    """Stable AP create outcomes."""

    CREATED = "CREATED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


@dataclass(frozen=True)
class FinancialExecutionCreateResult:
    """Immutable AP create outcome and canonical execution truth."""

    outcome: FinancialExecutionCreateOutcome
    execution_truth: FinancialExecutionTruth


class FinancialExecutionFactRegistryError(RuntimeError):
    """Base fail-closed persistence error for neutral execution facts."""


class FinancialExecutionFactCreateConflictError(FinancialExecutionFactRegistryError):
    """Raised when a fact identity or attempt identity conflicts."""


class FinancialExecutionFactPersistedRecordInvalidError(FinancialExecutionFactRegistryError):
    """Raised when a neutral fact row is incomplete, unknown, or corrupt."""


class FinancialExecutionFactCreateOutcome(StrEnum):
    """Stable neutral-fact create outcomes."""

    CREATED = "CREATED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


@dataclass(frozen=True)
class FinancialExecutionFactCreateResult:
    """Immutable neutral-fact create outcome and canonical fact."""

    outcome: FinancialExecutionFactCreateOutcome
    execution_fact: FinancialExecutionFact


def _collection_or_raise(collection: Optional[Collection], name: str) -> Collection:
    """Resolve an explicitly supplied collection or configured database collection."""
    if collection is not None:
        return collection
    from ...kernel.db import get_database

    database = get_database()
    if database is None:
        raise FinancialExecutionRegistryError(f"{name}_PERSISTENCE_UNAVAILABLE")
    return database[name]


def _fact_collection_or_raise(collection: Optional[Collection]) -> Collection:
    """Resolve neutral facts only; AP rows are never dispatched through this path."""
    if collection is not None:
        return collection
    from ...kernel.db import get_database

    database = get_database()
    if database is None:
        raise FinancialExecutionFactRegistryError("FINANCIAL_EXECUTION_FACT_PERSISTENCE_UNAVAILABLE")
    return database[FACT_COLLECTION]


def _text(value: object, field: str, maximum: int = 256) -> str:
    """Validate bounded tenant-scoped lookup text without normalization."""
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
        raise FinancialExecutionRegistryError(f"invalid {field}")
    return value.strip()


def _fact_text(value: object, field: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
        raise FinancialExecutionFactRegistryError(f"invalid {field}")
    return value.strip()


def _key(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 128 or value != value.strip():
        raise FinancialExecutionRegistryError("invalid idempotency key")
    return value


def _fingerprint(truth: FinancialExecutionTruth, key: str) -> str:
    import hashlib, json
    return hashlib.sha3_512(json.dumps({"execution_truth": truth.evidence_payload(), "create_idempotency_key": key}, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def _validate_persisted_registry_metadata(document: dict) -> tuple[str, str]:
    key = document.get("create_idempotency_key")
    fingerprint = document.get("create_fingerprint")
    if not isinstance(key, str) or key != key.strip() or not key or len(key) > 128 or not isinstance(fingerprint, str) or not __import__("re").fullmatch(r"[0-9a-f]{128}", fingerprint):
        raise FinancialExecutionPersistedRecordInvalidError("FINANCIAL_EXECUTION_PERSISTED_RECORD_INVALID")
    return key, fingerprint


def _hydrate_truth(document: dict) -> FinancialExecutionTruth:
    """Strictly hydrate the frozen AP truth schema."""
    try:
        data = dict(document)
        data.pop("_id", None)
        data.pop("create_idempotency_key", None)
        data.pop("create_fingerprint", None)
        return FinancialExecutionTruth.from_mapping(data)
    except (TypeError, ValueError, KeyError, FinancialExecutionTruthError) as error:
        raise FinancialExecutionPersistedRecordInvalidError("FINANCIAL_EXECUTION_PERSISTED_RECORD_INVALID") from error


def _hydrate_and_validate_truth(document: dict) -> tuple[FinancialExecutionTruth, str, str]:
    """Hydrate AP truth and verify its persisted create-key fingerprint."""
    durable = _hydrate_truth(document)
    key, fingerprint = _validate_persisted_registry_metadata(document)
    if fingerprint != _fingerprint(durable, key):
        raise FinancialExecutionPersistedRecordInvalidError("FINANCIAL_EXECUTION_PERSISTED_RECORD_INVALID")
    return durable, key, fingerprint


def _transaction_is_active(session: Optional[ClientSession]) -> bool:
    """Read transaction state only from the caller-owned ClientSession."""
    return session is not None and session.in_transaction


def _hydrate_fact(document: dict) -> FinancialExecutionFact:
    """Strictly hydrate only the separate neutral execution-fact schema."""
    try:
        data = dict(document)
        data.pop("_id", None)
        return FinancialExecutionFact.from_mapping(data)
    except (TypeError, ValueError, KeyError, FinancialExecutionFactError) as error:
        raise FinancialExecutionFactPersistedRecordInvalidError("FINANCIAL_EXECUTION_FACT_PERSISTED_RECORD_INVALID") from error


class FinancialExecutionTruthRegistry:
    """Persist immutable historical AP execution evidence with caller-owned sessions."""

    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        """Create unchanged tenant-scoped AP truth indexes."""
        target = _collection_or_raise(collection, COLLECTION)
        target.create_index([("tenant_id", ASCENDING), ("execution_truth_id", ASCENDING)], unique=True, name="tenant_execution_truth_identity_unique")
        target.create_index([("tenant_id", ASCENDING), ("payable_id", ASCENDING), ("create_idempotency_key", ASCENDING)], unique=True, name="tenant_payable_execution_create_idempotency_unique")
        target.create_index([("tenant_id", ASCENDING), ("provider", ASCENDING), ("provider_execution_reference", ASCENDING), ("executed_at", ASCENDING), ("execution_truth_id", ASCENDING)], name="tenant_provider_execution_timeline")
        target.create_index([("tenant_id", ASCENDING), ("release_authorization_id", ASCENDING), ("executed_at", ASCENDING), ("execution_truth_id", ASCENDING)], name="tenant_release_authorization_execution_timeline")
        target.create_index([("tenant_id", ASCENDING), ("payable_id", ASCENDING), ("executed_at", ASCENDING), ("execution_truth_id", ASCENDING)], name="tenant_payable_execution_timeline")
        target.create_index([("tenant_id", ASCENDING), ("execution_status", ASCENDING), ("executed_at", ASCENDING), ("execution_truth_id", ASCENDING)], name="tenant_execution_status_timeline")

    @staticmethod
    def create(execution_truth: FinancialExecutionTruth, idempotency_key: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionCreateResult:
        """Insert, exactly replay, or reject divergent historical AP truth."""
        if not isinstance(execution_truth, FinancialExecutionTruth):
            raise FinancialExecutionRegistryError("execution_truth must be FinancialExecutionTruth")
        if not isinstance(idempotency_key, str) or not idempotency_key.strip() or len(idempotency_key.strip()) > 128:
            raise FinancialExecutionRegistryError("invalid idempotency key")
        target = _collection_or_raise(collection, COLLECTION)
        key = idempotency_key.strip()
        key = _key(idempotency_key)
        fingerprint = _fingerprint(execution_truth, key)
        document = {**execution_truth.to_dict(), "create_idempotency_key": key, "create_fingerprint": fingerprint}
        existing_by_key = FinancialExecutionTruthRegistry.get_by_idempotency_key(
            execution_truth.tenant_id,
            execution_truth.payable_id,
            key,
            target,
            session=session,
        )
        if existing_by_key is not None:
            if existing_by_key == execution_truth:
                return FinancialExecutionCreateResult(FinancialExecutionCreateOutcome.IDEMPOTENT_REPLAY, existing_by_key)
            raise FinancialExecutionIdempotencyKeyReuseError("FINANCIAL_EXECUTION_IDEMPOTENCY_KEY_REUSED")
        existing_by_identity = FinancialExecutionTruthRegistry.get(
            execution_truth.tenant_id,
            execution_truth.execution_truth_id,
            target,
            session=session,
        )
        if existing_by_identity is not None:
            identity_row = target.find_one(
                {"tenant_id": execution_truth.tenant_id, "execution_truth_id": execution_truth.execution_truth_id},
                session=session,
            )
            if identity_row is None:
                raise FinancialExecutionCreateConflictError("FINANCIAL_EXECUTION_CREATE_CONFLICT")
            durable, durable_key, durable_fingerprint = _hydrate_and_validate_truth(identity_row)
            if durable == execution_truth and durable_key == key and durable_fingerprint == fingerprint:
                return FinancialExecutionCreateResult(FinancialExecutionCreateOutcome.IDEMPOTENT_REPLAY, durable)
            if durable_key == key:
                raise FinancialExecutionIdempotencyKeyReuseError("FINANCIAL_EXECUTION_IDEMPOTENCY_KEY_REUSED")
            raise FinancialExecutionCreateConflictError("FINANCIAL_EXECUTION_CREATE_CONFLICT")
        try:
            target.insert_one(document, session=session)
            return FinancialExecutionCreateResult(FinancialExecutionCreateOutcome.CREATED, execution_truth)
        except DuplicateKeyError as error:
            if _transaction_is_active(session):
                raise FinancialExecutionCreateConflictError("FINANCIAL_EXECUTION_CREATE_CONFLICT") from error
            key_existing = target.find_one({"tenant_id": execution_truth.tenant_id, "payable_id": execution_truth.payable_id, "create_idempotency_key": key}, session=session)
            if key_existing is not None:
                durable, durable_key, durable_fingerprint = _hydrate_and_validate_truth(key_existing)
                if durable_key == key and durable_fingerprint == fingerprint and durable == execution_truth:
                    return FinancialExecutionCreateResult(FinancialExecutionCreateOutcome.IDEMPOTENT_REPLAY, durable)
                raise FinancialExecutionIdempotencyKeyReuseError("FINANCIAL_EXECUTION_IDEMPOTENCY_KEY_REUSED") from error
            existing = target.find_one({"tenant_id": execution_truth.tenant_id, "execution_truth_id": execution_truth.execution_truth_id}, session=session)
            if existing is not None:
                durable, durable_key, durable_fingerprint = _hydrate_and_validate_truth(existing)
                if durable_key == key and durable_fingerprint == fingerprint and durable == execution_truth:
                    return FinancialExecutionCreateResult(FinancialExecutionCreateOutcome.IDEMPOTENT_REPLAY, durable)
                if durable_key == key:
                    raise FinancialExecutionIdempotencyKeyReuseError("FINANCIAL_EXECUTION_IDEMPOTENCY_KEY_REUSED") from error
                raise FinancialExecutionCreateConflictError("FINANCIAL_EXECUTION_CREATE_CONFLICT") from error
            raise FinancialExecutionCreateConflictError("FINANCIAL_EXECUTION_CREATE_CONFLICT") from error
        except PyMongoError as error:
            raise FinancialExecutionRegistryError("FINANCIAL_EXECUTION_CREATE_FAILED") from error

    @staticmethod
    def get(tenant_id: str, execution_truth_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> Optional[FinancialExecutionTruth]:
        """Return exact tenant-scoped AP truth or absence."""
        row = _collection_or_raise(collection, COLLECTION).find_one({"tenant_id": _text(tenant_id, "tenant_id"), "execution_truth_id": _text(execution_truth_id, "execution_truth_id")}, session=session)
        return None if row is None else _hydrate_and_validate_truth(row)[0]

    @staticmethod
    def list_for_payable(tenant_id: str, payable_id: str, limit: int = 100, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> tuple[FinancialExecutionTruth, ...]:
        """Return bounded AP history by typed payable subject."""
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 250:
            raise FinancialExecutionRegistryError("limit must be between 1 and 250")
        rows = _collection_or_raise(collection, COLLECTION).find({"tenant_id": _text(tenant_id, "tenant_id"), "payable_id": _text(payable_id, "payable_id")}, session=session).sort([("executed_at", ASCENDING), ("execution_truth_id", ASCENDING)]).limit(limit)
        return tuple(_hydrate_truth(row) for row in rows)

    @staticmethod
    def get_by_idempotency_key(tenant_id: str, payable_id: str, idempotency_key: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> Optional[FinancialExecutionTruth]:
        row = _collection_or_raise(collection, COLLECTION).find_one({"tenant_id": _text(tenant_id, "tenant_id"), "payable_id": _text(payable_id, "payable_id"), "create_idempotency_key": _key(idempotency_key)}, session=session)
        return None if row is None else _hydrate_and_validate_truth(row)[0]

    @staticmethod
    def list_for_provider_execution(tenant_id: str, provider: str, provider_execution_reference: str, limit: int = 100, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> tuple[FinancialExecutionTruth, ...]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 250: raise FinancialExecutionRegistryError("limit must be between 1 and 250")
        rows = _collection_or_raise(collection, COLLECTION).find({"tenant_id": _text(tenant_id, "tenant_id"), "provider": _text(provider, "provider"), "provider_execution_reference": _text(provider_execution_reference, "provider_execution_reference")}, session=session).sort([("executed_at", ASCENDING), ("execution_truth_id", ASCENDING)]).limit(limit)
        return tuple(_hydrate_truth(row) for row in rows)

    @staticmethod
    def list_for_release_authorization(tenant_id: str, release_authorization_id: str, limit: int = 100, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> tuple[FinancialExecutionTruth, ...]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 250: raise FinancialExecutionRegistryError("limit must be between 1 and 250")
        rows = _collection_or_raise(collection, COLLECTION).find({"tenant_id": _text(tenant_id, "tenant_id"), "release_authorization_id": _text(release_authorization_id, "release_authorization_id")}, session=session).sort([("executed_at", ASCENDING), ("execution_truth_id", ASCENDING)]).limit(limit)
        return tuple(_hydrate_truth(row) for row in rows)


class FinancialExecutionFactRegistry:
    """Persist strict subject-neutral facts with exactly one fact per tenant/attempt."""

    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        """Create unique fact identity and unique tenant/attempt indexes."""
        target = _fact_collection_or_raise(collection)
        target.create_index([("tenant_id", ASCENDING), ("execution_fact_id", ASCENDING)], unique=True, name="tenant_execution_fact_identity_unique")
        target.create_index([("tenant_id", ASCENDING), ("execution_attempt_id", ASCENDING)], unique=True, name="tenant_execution_fact_attempt_unique")

    @staticmethod
    def create(execution_fact: FinancialExecutionFact, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionFactCreateResult:
        """Create one fact, return exact replay, or reject every divergence."""
        if not isinstance(execution_fact, FinancialExecutionFact):
            raise FinancialExecutionFactRegistryError("execution_fact must be FinancialExecutionFact")
        target = _fact_collection_or_raise(collection)
        document = execution_fact.to_dict()
        try:
            existing_attempt = target.find_one({"tenant_id": execution_fact.tenant_id, "execution_attempt_id": execution_fact.execution_attempt_id}, session=session)
            if existing_attempt is not None:
                durable = _hydrate_fact(existing_attempt)
                if durable == execution_fact:
                    return FinancialExecutionFactCreateResult(FinancialExecutionFactCreateOutcome.IDEMPOTENT_REPLAY, durable)
                raise FinancialExecutionFactCreateConflictError("FINANCIAL_EXECUTION_FACT_ATTEMPT_CONFLICT")
            existing_identity = target.find_one({"tenant_id": execution_fact.tenant_id, "execution_fact_id": execution_fact.execution_fact_id}, session=session)
            if existing_identity is not None:
                durable = _hydrate_fact(existing_identity)
                if durable == execution_fact:
                    return FinancialExecutionFactCreateResult(FinancialExecutionFactCreateOutcome.IDEMPOTENT_REPLAY, durable)
                raise FinancialExecutionFactCreateConflictError("FINANCIAL_EXECUTION_FACT_ID_CONFLICT")
            target.insert_one(document, session=session)
            return FinancialExecutionFactCreateResult(FinancialExecutionFactCreateOutcome.CREATED, execution_fact)
        except DuplicateKeyError as error:
            if _transaction_is_active(session):
                raise FinancialExecutionFactCreateConflictError("FINANCIAL_EXECUTION_FACT_CREATE_CONFLICT") from error
            winner = target.find_one({"tenant_id": execution_fact.tenant_id, "execution_attempt_id": execution_fact.execution_attempt_id}, session=session)
            if winner is not None:
                durable = _hydrate_fact(winner)
                if durable == execution_fact:
                    return FinancialExecutionFactCreateResult(FinancialExecutionFactCreateOutcome.IDEMPOTENT_REPLAY, durable)
            raise FinancialExecutionFactCreateConflictError("FINANCIAL_EXECUTION_FACT_CREATE_CONFLICT") from error
        except FinancialExecutionFactRegistryError:
            raise
        except PyMongoError as error:
            raise FinancialExecutionFactRegistryError("FINANCIAL_EXECUTION_FACT_CREATE_FAILED") from error

    @staticmethod
    def get(tenant_id: str, execution_fact_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> Optional[FinancialExecutionFact]:
        """Return a strict neutral fact by tenant and fact identity."""
        row = _fact_collection_or_raise(collection).find_one({"tenant_id": _fact_text(tenant_id, "tenant_id"), "execution_fact_id": _fact_text(execution_fact_id, "execution_fact_id")}, session=session)
        return None if row is None else _hydrate_fact(row)

    @staticmethod
    def get_by_attempt(tenant_id: str, execution_attempt_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> Optional[FinancialExecutionFact]:
        """Return the sole strict neutral fact for a tenant-scoped attempt."""
        row = _fact_collection_or_raise(collection).find_one({"tenant_id": _fact_text(tenant_id, "tenant_id"), "execution_attempt_id": _fact_text(execution_attempt_id, "execution_attempt_id")}, session=session)
        return None if row is None else _hydrate_fact(row)


# ARTIFACT: financial_execution_registry.py
# VERSION: v2.1.0-M11-P5-R2E-R4-R3
# AUTHORITY BOUNDARY: strict AP and neutral execution-evidence persistence only; no execution or settlement authority.
# TENANT POSTURE: all identities, replays, and conflicts are tenant-scoped.
# FAIL-CLOSED POSTURE: AP and neutral schemas have separate explicit hydration paths.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution truth.
# END OF WILSY OS SOVEREIGN ARTIFACT
