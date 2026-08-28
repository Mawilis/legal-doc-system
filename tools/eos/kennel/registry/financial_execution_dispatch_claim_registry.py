"""Durable immutable registry for dispatch claims.

VERSION: v1.0.1-KENNEL-FINANCIAL-EXECUTION-DISPATCH-CLAIM-REGISTRY
TITLE: Financial Execution Dispatch Claim Registry
PURPOSE: Persist immutable tenant-scoped dispatch claims.
AUTHORITY: Dispatch-claim persistence only; no attempt, transport, provider, truth, or settlement authority.
EPITOME: Identity-keyed immutable claims provide replay-safe recovery evidence.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/registry/financial_execution_dispatch_claim_registry.py
CERTIFICATION DATE: 2026-08-28
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque references and fingerprints only; no credentials.
TENANT BOUNDARY: every identity and list query is tenant-scoped.
TRANSACTION BOUNDARY: caller owns session and transaction lifecycle.
CHANGELOG: v1.0.1 canonicalizes persisted claimed_at to UTC BSON milliseconds, restores trusted naive BSON UTC during hydration, and derives durable fingerprints from canonical persistence material; arbitrary naive business timestamps remain invalid, no CodecOptions precondition is introduced, and domain, transaction, and authority semantics are unchanged. Runtime recertification remains pending. v1.0.0 established immutable dispatch-claim persistence and replay-safe hydration.
"""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from typing import Any, Optional
from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError, PyMongoError
from ..domain.financial_execution_dispatch_claim import FinancialExecutionDispatchClaim, FinancialExecutionAttemptState

VERSION = "v1.0.1-KENNEL-FINANCIAL-EXECUTION-DISPATCH-CLAIM-REGISTRY"
COLLECTION = "kennel_financial_execution_dispatch_claims"

class FinancialExecutionDispatchClaimRegistryError(RuntimeError):
    """Base fail-closed error for claim persistence boundaries."""


class FinancialExecutionDispatchClaimNotFoundError(FinancialExecutionDispatchClaimRegistryError):
    """Raised when a tenant-scoped claim identity is absent."""


class FinancialExecutionDispatchClaimInvalidRecordError(FinancialExecutionDispatchClaimRegistryError):
    """Raised when persisted claim material or fingerprint is corrupt."""


class FinancialExecutionDispatchClaimCreateConflictError(FinancialExecutionDispatchClaimRegistryError):
    """Raised when an immutable claim identity has divergent material."""

def _target(collection: Optional[Collection]) -> Collection:
    if collection is not None: return collection
    from ...kernel.db import get_database
    db = get_database()
    if db is None: raise FinancialExecutionDispatchClaimRegistryError("DISPATCH_CLAIM_PERSISTENCE_UNAVAILABLE")
    return db[COLLECTION]

def _canonical_timestamp(value: datetime) -> datetime:
    """Canonicalize a validated aware instant to UTC BSON milliseconds."""
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise FinancialExecutionDispatchClaimCreateConflictError("claimed_at must be timezone-aware")
    utc_value = value.astimezone(timezone.utc)
    return utc_value.replace(microsecond=(utc_value.microsecond // 1000) * 1000)


def _canonical_claim(claim: FinancialExecutionDispatchClaim) -> FinancialExecutionDispatchClaim:
    """Return an immutable claim using the durable BSON-safe timestamp."""
    return FinancialExecutionDispatchClaim(
        dispatch_claim_id=claim.dispatch_claim_id,
        tenant_id=claim.tenant_id,
        execution_command_id=claim.execution_command_id,
        execution_attempt_id=claim.execution_attempt_id,
        expected_attempt_fingerprint=claim.expected_attempt_fingerprint,
        provider_name=claim.provider_name,
        claimed_at=_canonical_timestamp(claim.claimed_at),
        transport_correlation_id=claim.transport_correlation_id,
        transport_material_fingerprint=claim.transport_material_fingerprint,
        expected_state=claim.expected_state,
        recovery_posture=claim.recovery_posture,
    )


def _material(claim: FinancialExecutionDispatchClaim) -> dict[str, Any]:
    return {"dispatch_claim_id": claim.dispatch_claim_id, "tenant_id": claim.tenant_id, "execution_command_id": claim.execution_command_id, "execution_attempt_id": claim.execution_attempt_id, "expected_attempt_fingerprint": claim.expected_attempt_fingerprint, "provider_name": claim.provider_name, "claimed_at": claim.claimed_at, "transport_correlation_id": claim.transport_correlation_id, "transport_material_fingerprint": claim.transport_material_fingerprint, "expected_state": claim.expected_state.value, "recovery_posture": claim.recovery_posture}

def _fingerprint(claim: FinancialExecutionDispatchClaim) -> str:
    return hashlib.sha3_512(json.dumps({**_material(claim), "claimed_at": claim.claimed_at.isoformat()}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def _document(claim: FinancialExecutionDispatchClaim) -> dict[str, Any]: return {**_material(claim), "claim_fingerprint": _fingerprint(claim)}

def _hydrate(row: dict[str, Any]) -> FinancialExecutionDispatchClaim:
    try:
        data = dict(row)
        stored = data.pop("claim_fingerprint", None)
        data.pop("_id", None)
        data["expected_state"] = FinancialExecutionAttemptState(data["expected_state"])
        if isinstance(data.get("claimed_at"), str):
            data["claimed_at"] = datetime.fromisoformat(data["claimed_at"])
        if isinstance(data.get("claimed_at"), datetime) and data["claimed_at"].tzinfo is None:
            data["claimed_at"] = data["claimed_at"].replace(tzinfo=timezone.utc)
        claim = _canonical_claim(FinancialExecutionDispatchClaim(**data))
        if stored != _fingerprint(claim): raise ValueError("fingerprint")
        return claim
    except (TypeError, ValueError, KeyError) as error:
        raise FinancialExecutionDispatchClaimInvalidRecordError("DISPATCH_CLAIM_PERSISTED_RECORD_INVALID") from error

class FinancialExecutionDispatchClaimRegistry:
    """Persist immutable claims without owning transactions or dispatch."""
    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        target = _target(collection)
        target.create_index([('tenant_id', ASCENDING), ('dispatch_claim_id', ASCENDING)], unique=True, name='tenant_dispatch_claim_identity_unique')
        target.create_index([('tenant_id', ASCENDING), ('execution_attempt_id', ASCENDING), ('claimed_at', ASCENDING), ('dispatch_claim_id', ASCENDING)], name='tenant_dispatch_claim_attempt_timeline')
        target.create_index([('tenant_id', ASCENDING), ('execution_command_id', ASCENDING), ('claimed_at', ASCENDING), ('dispatch_claim_id', ASCENDING)], name='tenant_dispatch_claim_command_timeline')

    @staticmethod
    def create(claim: FinancialExecutionDispatchClaim, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> str:
        if not isinstance(claim, FinancialExecutionDispatchClaim):
            raise FinancialExecutionDispatchClaimCreateConflictError("DISPATCH_CLAIM_CREATE_INVALID")
        durable_claim = _canonical_claim(claim)
        target = _target(collection)
        identity = {'tenant_id': durable_claim.tenant_id, 'dispatch_claim_id': durable_claim.dispatch_claim_id}
        try:
            result = target.update_one(identity, {'$setOnInsert': _document(durable_claim)}, upsert=True, session=session)
            if result.upserted_id is not None: return "CREATED"
            existing = target.find_one(identity, session=session)
            if existing is None: raise FinancialExecutionDispatchClaimCreateConflictError("DISPATCH_CLAIM_CREATE_CONFLICT")
            durable = _hydrate(existing)
            if durable == durable_claim: return "IDEMPOTENT_REPLAY"
            raise FinancialExecutionDispatchClaimCreateConflictError("DISPATCH_CLAIM_CREATE_CONFLICT")
        except DuplicateKeyError as error:
            raise FinancialExecutionDispatchClaimCreateConflictError("DISPATCH_CLAIM_CREATE_CONFLICT") from error
        except PyMongoError as error:
            if error.has_error_label("TransientTransactionError") or error.has_error_label("UnknownTransactionCommitResult"): raise
            raise FinancialExecutionDispatchClaimRegistryError("DISPATCH_CLAIM_CREATE_FAILED") from error

    @staticmethod
    def get(tenant_id: str, dispatch_claim_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionDispatchClaim:
        row = _target(collection).find_one({'tenant_id': str(tenant_id).strip(), 'dispatch_claim_id': str(dispatch_claim_id).strip()}, session=session)
        if row is None: raise FinancialExecutionDispatchClaimNotFoundError("DISPATCH_CLAIM_NOT_FOUND")
        return _hydrate(row)

    @staticmethod
    def list_for_attempt(tenant_id: str, execution_attempt_id: str, collection: Optional[Collection] = None, *, limit: int = 100, session: Optional[ClientSession] = None) -> tuple[FinancialExecutionDispatchClaim, ...]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 250: raise FinancialExecutionDispatchClaimRegistryError("limit must be between 1 and 250")
        rows = _target(collection).find({'tenant_id': str(tenant_id).strip(), 'execution_attempt_id': str(execution_attempt_id).strip()}, session=session).sort([('claimed_at', ASCENDING), ('dispatch_claim_id', ASCENDING)]).limit(limit)
        return tuple(_hydrate(row) for row in rows)

# ARTIFACT: financial_execution_dispatch_claim_registry.py
# VERSION: v1.0.1-KENNEL-FINANCIAL-EXECUTION-DISPATCH-CLAIM-REGISTRY
# AUTHORITY BOUNDARY: immutable claim persistence only; no attempt, transport, provider, truth, or settlement authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
