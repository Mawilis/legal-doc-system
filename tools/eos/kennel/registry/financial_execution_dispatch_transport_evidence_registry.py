"""Durable append-only registry for internal transport evidence.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-DISPATCH-TRANSPORT-EVIDENCE-REGISTRY
TITLE: Financial Execution Dispatch Transport Evidence Registry
PURPOSE: Persist immutable tenant-scoped transport-boundary events.
AUTHORITY: Internal transport evidence only; no provider, attempt, truth, or settlement authority.
EPITOME: Append-only evidence records preserve send-boundary facts without inferring delivery or settlement.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/registry/financial_execution_dispatch_transport_evidence_registry.py
CERTIFICATION DATE: 2026-08-28
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque references and fingerprints only; no payloads or credentials.
TENANT BOUNDARY: every identity and timeline query is tenant-scoped.
FINANCIAL AUTHORITY BOUNDARY: no provider outcome, execution truth, settlement, or ledger authority.
TRANSACTION BOUNDARY: caller owns sessions and transaction lifecycle.
CHANGELOG: v1.0.0 establishes immutable evidence persistence, UTC/millisecond timestamp canonicalization, and corruption-first hydration; runtime certification pending.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Optional
from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import PyMongoError
from ..domain.financial_execution_dispatch_transport_evidence import FinancialExecutionDispatchTransportEvidence, TransportEvidenceDisposition, FinancialExecutionDispatchTransportEvidenceError

VERSION = "v1.0.0-KENNEL-FINANCIAL-EXECUTION-DISPATCH-TRANSPORT-EVIDENCE-REGISTRY"
COLLECTION = "kennel_financial_execution_dispatch_transport_evidence"

class FinancialExecutionDispatchTransportEvidenceRegistryError(RuntimeError):
    """Base fail-closed persistence error."""
class FinancialExecutionDispatchTransportEvidenceNotFoundError(FinancialExecutionDispatchTransportEvidenceRegistryError):
    """Tenant-scoped evidence identity was not found."""
class FinancialExecutionDispatchTransportEvidenceInvalidRecordError(FinancialExecutionDispatchTransportEvidenceRegistryError):
    """Persisted evidence material or fingerprint is corrupt."""
class FinancialExecutionDispatchTransportEvidenceCreateConflictError(FinancialExecutionDispatchTransportEvidenceRegistryError):
    """Immutable evidence identity has divergent material."""

def _target(collection: Optional[Collection]) -> Collection:
    """Resolve an injected collection without owning database transactions."""
    if collection is not None:
        return collection
    from ...kernel.db import get_database
    database = get_database()
    if database is None:
        raise FinancialExecutionDispatchTransportEvidenceRegistryError("TRANSPORT_EVIDENCE_PERSISTENCE_UNAVAILABLE")
    return database[COLLECTION]

def _canonical_timestamp(value: datetime) -> datetime:
    """Convert an aware instant to UTC BSON millisecond precision."""
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise FinancialExecutionDispatchTransportEvidenceCreateConflictError("recorded_at must be timezone-aware")
    utc_value = value.astimezone(timezone.utc)
    return utc_value.replace(microsecond=(utc_value.microsecond // 1000) * 1000)

def _canonical(evidence: FinancialExecutionDispatchTransportEvidence) -> FinancialExecutionDispatchTransportEvidence:
    """Return a new immutable evidence value with canonical persistence time."""
    return FinancialExecutionDispatchTransportEvidence(**{**evidence.__dict__, "recorded_at": _canonical_timestamp(evidence.recorded_at)})

def _material(evidence: FinancialExecutionDispatchTransportEvidence) -> dict[str, Any]:
    """Build the canonical BSON-safe material projection."""
    return {**evidence.canonical_payload(), "recorded_at": evidence.recorded_at}

def _fingerprint(evidence: FinancialExecutionDispatchTransportEvidence) -> str:
    """Fingerprint canonical durable evidence material."""
    material = {**_material(evidence), "recorded_at": evidence.recorded_at.isoformat()}
    return hashlib.sha3_512(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def _document(evidence: FinancialExecutionDispatchTransportEvidence) -> dict[str, Any]:
    """Build immutable evidence storage material."""
    return {**_material(evidence), "transport_evidence_fingerprint": _fingerprint(evidence)}

def _hydrate(row: dict[str, Any]) -> FinancialExecutionDispatchTransportEvidence:
    """Restore trusted BSON UTC representation and validate corruption-first."""
    try:
        data = dict(row)
        stored = data.pop("transport_evidence_fingerprint", None)
        data.pop("_id", None)
        data["transport_disposition"] = TransportEvidenceDisposition(data["transport_disposition"])
        value = data.get("recorded_at")
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if isinstance(value, datetime) and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        data["recorded_at"] = value
        evidence = _canonical(FinancialExecutionDispatchTransportEvidence(**data))
        if stored != _fingerprint(evidence):
            raise ValueError("fingerprint mismatch")
        return evidence
    except (TypeError, ValueError, KeyError, FinancialExecutionDispatchTransportEvidenceError) as error:
        raise FinancialExecutionDispatchTransportEvidenceInvalidRecordError("TRANSPORT_EVIDENCE_PERSISTED_RECORD_INVALID") from error

class FinancialExecutionDispatchTransportEvidenceRegistry:
    """Persist append-only transport evidence without provider or lifecycle authority."""
    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        """Install the unique identity and tenant-scoped timeline indexes."""
        target = _target(collection)
        target.create_index([('tenant_id', ASCENDING), ('transport_evidence_id', ASCENDING)], unique=True, name='tenant_transport_evidence_identity_unique')
        target.create_index([('tenant_id', ASCENDING), ('execution_attempt_id', ASCENDING), ('recorded_at', ASCENDING), ('transport_evidence_id', ASCENDING)], name='tenant_transport_evidence_attempt_timeline')
        target.create_index([('tenant_id', ASCENDING), ('dispatch_claim_id', ASCENDING), ('recorded_at', ASCENDING), ('transport_evidence_id', ASCENDING)], name='tenant_transport_evidence_claim_timeline')

    @staticmethod
    def create(evidence: FinancialExecutionDispatchTransportEvidence, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> str:
        """Create immutable evidence or classify exact replay/divergent conflict."""
        if not isinstance(evidence, FinancialExecutionDispatchTransportEvidence):
            raise FinancialExecutionDispatchTransportEvidenceCreateConflictError("TRANSPORT_EVIDENCE_CREATE_INVALID")
        durable = _canonical(evidence)
        target = _target(collection)
        identity = {'tenant_id': durable.tenant_id, 'transport_evidence_id': durable.transport_evidence_id}
        try:
            result = target.update_one(identity, {'$setOnInsert': _document(durable)}, upsert=True, session=session)
            if result.upserted_id is not None:
                return "CREATED"
            existing = target.find_one(identity, session=session)
            if existing is None:
                raise FinancialExecutionDispatchTransportEvidenceCreateConflictError("TRANSPORT_EVIDENCE_CREATE_CONFLICT")
            if _hydrate(existing) == durable:
                return "IDEMPOTENT_REPLAY"
            raise FinancialExecutionDispatchTransportEvidenceCreateConflictError("TRANSPORT_EVIDENCE_CREATE_CONFLICT")
        except PyMongoError as error:
            if error.has_error_label("TransientTransactionError") or error.has_error_label("UnknownTransactionCommitResult"):
                raise
            raise FinancialExecutionDispatchTransportEvidenceRegistryError("TRANSPORT_EVIDENCE_CREATE_FAILED") from error

    @staticmethod
    def get(tenant_id: str, transport_evidence_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionDispatchTransportEvidence:
        """Read one tenant-scoped evidence event through corruption-first hydration."""
        row = _target(collection).find_one({'tenant_id': str(tenant_id).strip(), 'transport_evidence_id': str(transport_evidence_id).strip()}, session=session)
        if row is None:
            raise FinancialExecutionDispatchTransportEvidenceNotFoundError("TRANSPORT_EVIDENCE_NOT_FOUND")
        return _hydrate(row)

    @staticmethod
    def _list(query: dict[str, str], collection: Optional[Collection], limit: int, session: Optional[ClientSession]) -> tuple[FinancialExecutionDispatchTransportEvidence, ...]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 250:
            raise FinancialExecutionDispatchTransportEvidenceRegistryError("limit must be between 1 and 250")
        rows = _target(collection).find(query, session=session).sort([('recorded_at', ASCENDING), ('transport_evidence_id', ASCENDING)]).limit(limit)
        return tuple(_hydrate(row) for row in rows)

    @staticmethod
    def list_for_attempt(tenant_id: str, execution_attempt_id: str, collection: Optional[Collection] = None, *, limit: int = 250, session: Optional[ClientSession] = None) -> tuple[FinancialExecutionDispatchTransportEvidence, ...]:
        """List tenant-local evidence by attempt in deterministic order."""
        return FinancialExecutionDispatchTransportEvidenceRegistry._list({'tenant_id': str(tenant_id).strip(), 'execution_attempt_id': str(execution_attempt_id).strip()}, collection, limit, session)

    @staticmethod
    def list_for_claim(tenant_id: str, dispatch_claim_id: str, collection: Optional[Collection] = None, *, limit: int = 250, session: Optional[ClientSession] = None) -> tuple[FinancialExecutionDispatchTransportEvidence, ...]:
        """List tenant-local evidence by dispatch claim in deterministic order."""
        return FinancialExecutionDispatchTransportEvidenceRegistry._list({'tenant_id': str(tenant_id).strip(), 'dispatch_claim_id': str(dispatch_claim_id).strip()}, collection, limit, session)

# ARTIFACT: financial_execution_dispatch_transport_evidence_registry.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-DISPATCH-TRANSPORT-EVIDENCE-REGISTRY
# AUTHORITY BOUNDARY: immutable internal transport evidence only; no provider, truth, settlement, or ledger authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
