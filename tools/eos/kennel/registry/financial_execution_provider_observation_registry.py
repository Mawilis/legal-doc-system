# -*- coding: utf-8 -*-
"""Durable provider-neutral FinancialExecutionProviderObservation authority.

TITLE: Financial Execution Provider Observation Registry
VERSION: v1.0.2-KENNEL-FINANCIAL-EXECUTION-PROVIDER-OBSERVATION-REGISTRY
PURPOSE: Canonical immutable provider-neutral observation persistence authority.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
LAST UPDATED: 2026-08-28
COMPLIANCE: POPIA §19 | GDPR Art. 32 | SOC2 CC7.2
SECURITY / PRIVACY POSTURE: opaque references only; raw payloads and credentials are forbidden.
TENANT BOUNDARY: every identity and query is tenant-scoped.
AUTHORITY: immutable observation persistence only; no attempt, truth, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: no lifecycle, execution, settlement, ledger, or provider transport authority.
CHANGELOG: v1.0.2 corrects transaction-unsafe duplicate-key replay by using immutable transaction-safe upsert resolution; public authority boundaries, caller transaction ownership, and no financial semantic expansion are preserved. v1.0.1 governance-only structural hardening; NO FINANCIAL SEMANTIC CHANGE. v1.0.0 established tenant-scoped corruption-first persistence, replay protection, and caller-owned sessions.
"""
from __future__ import annotations

import hashlib
from typing import Optional, Mapping, Any
from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import PyMongoError
from ..domain.financial_execution_provider_observation import FinancialExecutionProviderObservation, ObservationError

VERSION = "v1.0.2-KENNEL-FINANCIAL-EXECUTION-PROVIDER-OBSERVATION-REGISTRY"
COLLECTION = "kennel_financial_execution_provider_observations"

class FinancialExecutionProviderObservationRegistryError(RuntimeError):
    """Base fail-closed persistence error; no financial truth is inferred."""
class FinancialExecutionProviderObservationNotFoundError(FinancialExecutionProviderObservationRegistryError):
    """Tenant-local absence without cross-tenant disclosure."""
class FinancialExecutionProviderObservationPersistedRecordInvalidError(FinancialExecutionProviderObservationRegistryError):
    """Persisted corruption detected before replay or conflict classification."""
class FinancialExecutionProviderObservationCreateConflictError(FinancialExecutionProviderObservationRegistryError):
    """Immutable identity conflict; divergent material is never overwritten."""

def _target(collection: Optional[Collection]) -> Collection:
    """Resolve an injected collection or configured database without owning transactions."""
    if collection is not None: return collection
    from ...kernel.db import get_database
    db = get_database()
    if db is None: raise FinancialExecutionProviderObservationRegistryError("FINANCIAL_EXECUTION_PROVIDER_OBSERVATION_PERSISTENCE_UNAVAILABLE")
    return db[COLLECTION]

def _hydrate(document: Mapping[str, Any]) -> FinancialExecutionProviderObservation:
    """Reconstruct and validate immutable evidence, normalizing BSON UTC and verifying its fingerprint."""
    try:
        data = dict(document); stored = data.pop("observation_fingerprint", None); data.pop("_id", None)
        from datetime import datetime, timezone
        from ..domain.financial_execution_provider_observation import ObservationStatus, EvidenceStrength, TransportDisposition
        for key, enum_type in (("observation_status", ObservationStatus), ("evidence_strength", EvidenceStrength), ("transport_disposition", TransportDisposition)):
            if isinstance(data.get(key), str): data[key] = enum_type(data[key])
        for key in ("observed_at", "provider_occurred_at"):
            if isinstance(data.get(key), str): data[key] = datetime.fromisoformat(data[key])
            elif isinstance(data.get(key), datetime) and data[key].tzinfo is None: data[key] = data[key].replace(tzinfo=timezone.utc)
        item = FinancialExecutionProviderObservation(**data)
        expected = item.fingerprint
        if not isinstance(stored, str) or stored != expected: raise ValueError
        return item
    except (TypeError, ValueError, KeyError, ObservationError) as error:
        raise FinancialExecutionProviderObservationPersistedRecordInvalidError("FINANCIAL_EXECUTION_PROVIDER_OBSERVATION_PERSISTED_RECORD_INVALID") from error

def _document(item: FinancialExecutionProviderObservation) -> dict[str, Any]:
    """Create the safe deterministic persistence projection with no payloads or secrets."""
    return {**item.to_dict(), "observation_fingerprint": item.fingerprint}

class FinancialExecutionProviderObservationRegistry:
    """Persists immutable observations; never mutates attempts or final truth."""
    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        """Install tenant-scoped observation indexes; provider references remain non-unique."""
        target = _target(collection)
        target.create_index([('tenant_id', ASCENDING), ('observation_id', ASCENDING)], unique=True, name='tenant_observation_identity_unique')
        target.create_index([('tenant_id', ASCENDING), ('execution_attempt_id', ASCENDING), ('observed_at', ASCENDING), ('observation_id', ASCENDING)], name='tenant_attempt_observation_timeline')
        target.create_index([('tenant_id', ASCENDING), ('provider_name', ASCENDING), ('provider_request_reference', ASCENDING)], name='tenant_provider_request_observations')
        target.create_index([('tenant_id', ASCENDING), ('provider_name', ASCENDING), ('provider_execution_reference', ASCENDING)], name='tenant_provider_execution_observations')
        target.create_index([('tenant_id', ASCENDING), ('observation_status', ASCENDING), ('observed_at', ASCENDING)], name='tenant_observation_status_timeline')

    @staticmethod
    def create(observation: FinancialExecutionProviderObservation, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> tuple[str, FinancialExecutionProviderObservation]:
        """Insert immutable evidence, classify exact replay or divergent conflict, and preserve caller session ownership."""
        if not isinstance(observation, FinancialExecutionProviderObservation): raise FinancialExecutionProviderObservationCreateConflictError("FINANCIAL_EXECUTION_PROVIDER_OBSERVATION_CREATE_INVALID")
        target = _target(collection)
        try:
            result = target.update_one(
                {'tenant_id': observation.tenant_id, 'observation_id': observation.observation_id},
                {'$setOnInsert': _document(observation)},
                upsert=True,
                session=session,
            )
            if result.upserted_id is not None: return "CREATED", observation
            existing = target.find_one({'tenant_id': observation.tenant_id, 'observation_id': observation.observation_id}, session=session)
            if existing is None: raise FinancialExecutionProviderObservationCreateConflictError("FINANCIAL_EXECUTION_PROVIDER_OBSERVATION_CREATE_CONFLICT")
            durable = _hydrate(existing)
            if durable == observation: return "IDEMPOTENT_REPLAY", durable
            raise FinancialExecutionProviderObservationCreateConflictError("FINANCIAL_EXECUTION_PROVIDER_OBSERVATION_CREATE_CONFLICT")
        except PyMongoError as error:
            raise FinancialExecutionProviderObservationRegistryError("FINANCIAL_EXECUTION_PROVIDER_OBSERVATION_CREATE_FAILED") from error

    @staticmethod
    def get(tenant_id: str, observation_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionProviderObservation:
        """Read one tenant-scoped observation through corruption-first hydration without disclosure."""
        row = _target(collection).find_one({'tenant_id': str(tenant_id).strip(), 'observation_id': str(observation_id).strip()}, session=session)
        if row is None: raise FinancialExecutionProviderObservationNotFoundError("FINANCIAL_EXECUTION_PROVIDER_OBSERVATION_NOT_FOUND")
        return _hydrate(row)

    @staticmethod
    def list_for_attempt(tenant_id: str, execution_attempt_id: str, limit: int = 250, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> tuple[FinancialExecutionProviderObservation, ...]:
        """List tenant-local observations deterministically for audit; ordering never establishes truth precedence."""
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 250: raise FinancialExecutionProviderObservationRegistryError("limit must be between 1 and 250")
        rows = _target(collection).find({'tenant_id': str(tenant_id).strip(), 'execution_attempt_id': str(execution_attempt_id).strip()}, session=session).sort([('observed_at', ASCENDING), ('observation_id', ASCENDING)]).limit(limit)
        return tuple(_hydrate(row) for row in rows)

# ARTIFACT: financial_execution_provider_observation_registry.py
# VERSION: v1.0.2-KENNEL-FINANCIAL-EXECUTION-PROVIDER-OBSERVATION-REGISTRY
# AUTHORITY BOUNDARY: immutable provider observation persistence; no lifecycle, truth, or settlement authority.
# TENANT POSTURE: all identities and queries are tenant-scoped.
# FAIL-CLOSED POSTURE: corruption, divergent replay, and persistence failures never downgrade integrity.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution truth; this registry owns no truth or settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
