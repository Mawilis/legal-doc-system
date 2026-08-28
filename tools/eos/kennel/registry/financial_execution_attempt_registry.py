# -*- coding: utf-8 -*-
"""Wilsy OS durable FinancialExecutionAttempt persistence authority.

VERSION: v1.0.1-KENNEL-FINANCIAL-EXECUTION-ATTEMPT-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Tenant-scoped immutable-at-rest lifecycle attempts with corruption-first CAS transitions.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/registry/financial_execution_attempt_registry.py
COLLABORATION: Wilson Khanyezi (Founder); Codex (AI Engineering)
CHANGELOG: v1.0.1 forward-corrects transaction-error taxonomy: labeled TransientTransactionError and UnknownTransactionCommitResult now propagate unchanged, while unlabeled PyMongo errors remain wrapped; lifecycle, CAS, transaction ownership, and SEND_STARTED orchestration remain unchanged. v1.0.0 established PREPARED creation, strict hydration, replay-safe identity, and caller-owned CAS transitions.
"""
from __future__ import annotations

import hashlib, json
from dataclasses import dataclass
from typing import NoReturn, Optional
from pymongo import ASCENDING, ReturnDocument
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import PyMongoError
from ..domain.financial_execution_lifecycle import FinancialExecutionAttempt, FinancialExecutionAttemptState, FinancialExecutionLifecycleError

VERSION = "v1.0.1-KENNEL-FINANCIAL-EXECUTION-ATTEMPT-REGISTRY"
COLLECTION = "kennel_financial_execution_attempts"

class FinancialExecutionAttemptRegistryError(RuntimeError):
    """Base persistence failure."""


class FinancialExecutionAttemptNotFoundError(FinancialExecutionAttemptRegistryError):
    """Attempt identity is absent."""


class FinancialExecutionAttemptPersistedRecordInvalidError(FinancialExecutionAttemptRegistryError):
    """Durable attempt material failed integrity validation."""


class FinancialExecutionAttemptCreateConflictError(FinancialExecutionAttemptRegistryError):
    """Attempt identity conflicts with immutable material."""


class FinancialExecutionAttemptTransitionConflictError(FinancialExecutionAttemptRegistryError):
    """Attempt CAS or lifecycle transition failed."""

def _raise_mongo(error: PyMongoError, message: str) -> NoReturn:
    """Preserve caller-owned transaction labels; wrap ordinary infrastructure errors."""
    if error.has_error_label("TransientTransactionError") or error.has_error_label("UnknownTransactionCommitResult"):
        raise error
    raise FinancialExecutionAttemptRegistryError(message) from error

@dataclass(frozen=True)
class FinancialExecutionAttemptCreateResult:
    outcome: str
    attempt: FinancialExecutionAttempt

def _target(collection: Optional[Collection]) -> Collection:
    if collection is not None: return collection
    from ...kernel.db import get_database
    db = get_database()
    if db is None: raise FinancialExecutionAttemptRegistryError("FINANCIAL_EXECUTION_ATTEMPT_PERSISTENCE_UNAVAILABLE")
    return db[COLLECTION]

def _fingerprint(attempt: FinancialExecutionAttempt) -> str:
    return hashlib.sha3_512(json.dumps(attempt.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()

def _document(attempt: FinancialExecutionAttempt) -> dict:
    return {**attempt.to_dict(), "attempt_fingerprint": _fingerprint(attempt)}

def _hydrate(document: dict) -> FinancialExecutionAttempt:
    try:
        data = dict(document)
        stored = data.pop("attempt_fingerprint", None)
        data.pop("_id", None)
        for key in ("state",): data[key] = FinancialExecutionAttemptState(data[key])
        for key in ("created_at", "transmission_started_at", "transmitted_at", "provider_accepted_at", "confirmed_at"):
            if isinstance(data.get(key), str):
                from datetime import datetime
                data[key] = datetime.fromisoformat(data[key])
        attempt = FinancialExecutionAttempt(**data)
        if not isinstance(stored, str) or stored != _fingerprint(attempt): raise ValueError
        return attempt
    except (TypeError, ValueError, KeyError, FinancialExecutionLifecycleError) as error:
        raise FinancialExecutionAttemptPersistedRecordInvalidError("FINANCIAL_EXECUTION_ATTEMPT_PERSISTED_RECORD_INVALID") from error

class FinancialExecutionAttemptRegistry:
    """Persists lifecycle attempts; never owns provider transport or final truth."""
    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        try:
            target = _target(collection)
            target.create_index([('tenant_id', ASCENDING), ('execution_attempt_id', ASCENDING)], unique=True, name='tenant_execution_attempt_identity_unique')
            target.create_index([('tenant_id', ASCENDING), ('execution_command_id', ASCENDING)], name='tenant_execution_command_attempts')
            target.create_index([('tenant_id', ASCENDING), ('provider_name', ASCENDING), ('provider_request_reference', ASCENDING)], name='tenant_provider_request_attempts')
            target.create_index([('tenant_id', ASCENDING), ('state', ASCENDING), ('created_at', ASCENDING)], name='tenant_attempt_state_timeline')
        except PyMongoError as error:
            _raise_mongo(error, "FINANCIAL_EXECUTION_ATTEMPT_INDEX_FAILED")

    @staticmethod
    def create(attempt: FinancialExecutionAttempt, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionAttemptCreateResult:
        if not isinstance(attempt, FinancialExecutionAttempt) or attempt.state is not FinancialExecutionAttemptState.PREPARED:
            raise FinancialExecutionAttemptCreateConflictError("FINANCIAL_EXECUTION_ATTEMPT_CREATE_INVALID")
        target = _target(collection)
        try:
            result = target.update_one({'tenant_id': attempt.tenant_id, 'execution_attempt_id': attempt.execution_attempt_id}, {'$setOnInsert': _document(attempt)}, upsert=True, session=session)
            if result.upserted_id is not None:
                return FinancialExecutionAttemptCreateResult("CREATED", attempt)
            existing = target.find_one({'tenant_id': attempt.tenant_id, 'execution_attempt_id': attempt.execution_attempt_id}, session=session)
            if existing is None:
                raise FinancialExecutionAttemptCreateConflictError("FINANCIAL_EXECUTION_ATTEMPT_CREATE_CONFLICT")
            durable = _hydrate(existing)
            if durable == attempt:
                return FinancialExecutionAttemptCreateResult("IDEMPOTENT_REPLAY", durable)
            raise FinancialExecutionAttemptCreateConflictError("FINANCIAL_EXECUTION_ATTEMPT_CREATE_CONFLICT")
        except PyMongoError as error:
            _raise_mongo(error, "FINANCIAL_EXECUTION_ATTEMPT_CREATE_FAILED")

    @staticmethod
    def get(tenant_id: str, execution_attempt_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionAttempt:
        try:
            row = _target(collection).find_one({'tenant_id': str(tenant_id).strip(), 'execution_attempt_id': str(execution_attempt_id).strip()}, session=session)
        except PyMongoError as error:
            _raise_mongo(error, "FINANCIAL_EXECUTION_ATTEMPT_GET_FAILED")
        if row is None: raise FinancialExecutionAttemptNotFoundError("FINANCIAL_EXECUTION_ATTEMPT_NOT_FOUND")
        return _hydrate(row)

    @staticmethod
    def list_for_command(tenant_id: str, execution_command_id: str, limit: int = 100, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> tuple[FinancialExecutionAttempt, ...]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 250: raise FinancialExecutionAttemptRegistryError("limit must be between 1 and 250")
        try:
            rows = _target(collection).find({'tenant_id': str(tenant_id).strip(), 'execution_command_id': str(execution_command_id).strip()}, session=session).sort([('created_at', ASCENDING), ('execution_attempt_id', ASCENDING)]).limit(limit)
            return tuple(_hydrate(row) for row in rows)
        except PyMongoError as error:
            _raise_mongo(error, "FINANCIAL_EXECUTION_ATTEMPT_LIST_FAILED")

    @staticmethod
    def transition(tenant_id: str, execution_attempt_id: str, expected_state: FinancialExecutionAttemptState, expected_fingerprint: str, target_attempt: FinancialExecutionAttempt, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionAttempt:
        if not isinstance(expected_state, FinancialExecutionAttemptState) or not isinstance(target_attempt, FinancialExecutionAttempt): raise FinancialExecutionAttemptTransitionConflictError("FINANCIAL_EXECUTION_ATTEMPT_TRANSITION_INVALID")
        current = FinancialExecutionAttemptRegistry.get(tenant_id, execution_attempt_id, collection, session=session)
        if current.state is not expected_state or _fingerprint(current) != expected_fingerprint: raise FinancialExecutionAttemptTransitionConflictError("FINANCIAL_EXECUTION_ATTEMPT_TRANSITION_CONFLICT")
        try: current.transition_to(target_attempt.state, evidence_reference=target_attempt.latest_provider_evidence_reference, confirmed_at=target_attempt.confirmed_at)
        except FinancialExecutionLifecycleError as error: raise FinancialExecutionAttemptTransitionConflictError("FINANCIAL_EXECUTION_ATTEMPT_TRANSITION_CONFLICT") from error
        try:
            row = _target(collection).find_one_and_replace({'tenant_id': current.tenant_id, 'execution_attempt_id': current.execution_attempt_id, 'attempt_fingerprint': expected_fingerprint}, _document(target_attempt), return_document=ReturnDocument.AFTER, session=session)
        except PyMongoError as error:
            _raise_mongo(error, "FINANCIAL_EXECUTION_ATTEMPT_TRANSITION_FAILED")
        if row is None: raise FinancialExecutionAttemptTransitionConflictError("FINANCIAL_EXECUTION_ATTEMPT_TRANSITION_CONFLICT")
        return _hydrate(row)

# ARTIFACT: financial_execution_attempt_registry.py
# VERSION: v1.0.1-KENNEL-FINANCIAL-EXECUTION-ATTEMPT-REGISTRY
# AUTHORITY BOUNDARY: lifecycle persistence only; no provider, truth, or settlement authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
