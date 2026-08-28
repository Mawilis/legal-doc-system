# -*- coding: utf-8 -*-
"""Durable tenant-scoped PayShap provider evidence store.

VERSION: v1.0.0-KENNEL-PAYSHAP-EVIDENCE-STORE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable provider observation persistence; no invoice, execution, or settlement mutation.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/evidence/payshap_evidence_store.py
CHANGELOG: v1.0.0 establishes corruption-first evidence hydration and durable event replay protection.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Optional
import hashlib, json

from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError, PyMongoError

from ..providers.payshap_contract import PayShapEvidenceStore, PayShapProviderEvidence, PayShapStatus

VERSION = "v1.0.0-KENNEL-PAYSHAP-EVIDENCE-STORE"
COLLECTION = "kennel_payshap_provider_evidence"

class PayShapEvidenceStoreError(RuntimeError):
    """Base fail-closed evidence persistence error."""
class PayShapEvidenceCorruptionError(PayShapEvidenceStoreError):
    """Raised when persisted evidence cannot be canonically hydrated."""
class PayShapEvidenceReplayConflictError(PayShapEvidenceStoreError):
    """Raised when an event identity is reused with divergent evidence."""

@dataclass(frozen=True)
class PayShapStoredEvidence:
    evidence_id: str
    tenant_id: str
    provider_name: str
    provider_event_id: str
    provider_reference: str
    provider_status: PayShapStatus
    amount_minor: int
    currency: str
    provider_timestamp: Optional[datetime]
    observed_at: datetime
    payload_fingerprint: str
    signature_fingerprint: str
    evidence_reference: str
    execution_command_id: Optional[str] = None
    destination_reference: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {"evidence_id":self.evidence_id,"tenant_id":self.tenant_id,"provider_name":self.provider_name,"provider_event_id":self.provider_event_id,"provider_reference":self.provider_reference,"provider_status":self.provider_status.value,"amount_minor":self.amount_minor,"currency":self.currency,"provider_timestamp":self.provider_timestamp.isoformat() if self.provider_timestamp else None,"observed_at":self.observed_at.isoformat(),"payload_fingerprint":self.payload_fingerprint,"signature_fingerprint":self.signature_fingerprint,"evidence_reference":self.evidence_reference,"execution_command_id":self.execution_command_id,"destination_reference":self.destination_reference}

class PayShapEvidenceRegistry:
    """Persists immutable PayShap evidence with tenant-scoped event uniqueness."""
    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        target = _target(collection)
        target.create_index([("tenant_id",ASCENDING),("provider_event_id",ASCENDING)],unique=True,name="tenant_payshap_event_unique")
        target.create_index([("tenant_id",ASCENDING),("provider_reference",ASCENDING),("observed_at",ASCENDING)],name="tenant_payshap_reference_timeline")
    @staticmethod
    def store(evidence: Mapping[str, Any], collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> str:
        item = _hydrate(evidence)
        target = _target(collection)
        try:
            target.insert_one(item.to_dict(), session=session); return item.evidence_reference
        except DuplicateKeyError as error:
            existing = target.find_one({"tenant_id":item.tenant_id,"provider_event_id":item.provider_event_id},session=session)
            if existing is None: raise PayShapEvidenceReplayConflictError("PAYSHAP_EVIDENCE_REPLAY_CONFLICT") from error
            durable = _hydrate(existing)
            if durable.payload_fingerprint == item.payload_fingerprint and durable.signature_fingerprint == item.signature_fingerprint:
                return durable.evidence_reference
            raise PayShapEvidenceReplayConflictError("PAYSHAP_EVIDENCE_REPLAY_CONFLICT") from error
        except PyMongoError as error:
            raise PayShapEvidenceStoreError("PAYSHAP_EVIDENCE_STORE_FAILED") from error
    @staticmethod
    def get(tenant_id: str, provider_event_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> PayShapStoredEvidence:
        row=_target(collection).find_one({"tenant_id":tenant_id,"provider_event_id":provider_event_id},session=session)
        if row is None: raise PayShapEvidenceStoreError("PAYSHAP_EVIDENCE_NOT_FOUND")
        return _hydrate(row)

def _target(collection: Optional[Collection]) -> Collection:
    if collection is not None: return collection
    from ...kernel.db import get_database
    db=get_database()
    if db is None: raise PayShapEvidenceStoreError("PAYSHAP_EVIDENCE_PERSISTENCE_UNAVAILABLE")
    return db[COLLECTION]

def _hydrate(value: Mapping[str, Any]) -> PayShapStoredEvidence:
    try:
        d=dict(value); d.pop("_id",None)
        for k in ("provider_timestamp","observed_at"):
            if isinstance(d.get(k),str): d[k]=datetime.fromisoformat(d[k])
        d["provider_status"]=PayShapStatus(d["provider_status"])
        if not isinstance(d.get("amount_minor"),int) or isinstance(d.get("amount_minor"),bool) or d["amount_minor"]<0: raise ValueError
        if not isinstance(d.get("currency"),str) or len(d["currency"])!=3 or d["currency"]!=d["currency"].upper(): raise ValueError
        required=("evidence_id","tenant_id","provider_name","provider_event_id","provider_reference","payload_fingerprint","signature_fingerprint","evidence_reference")
        if any(not isinstance(d.get(k),str) or not d[k].strip() for k in required): raise ValueError
        item=PayShapStoredEvidence(**d)
        if not isinstance(item.payload_fingerprint,str) or len(item.payload_fingerprint)!=128 or any(c not in "0123456789abcdef" for c in item.payload_fingerprint): raise ValueError
        return item
    except (KeyError,TypeError,ValueError) as error:
        raise PayShapEvidenceCorruptionError("PAYSHAP_EVIDENCE_PERSISTED_RECORD_INVALID") from error

# ARTIFACT: payshap_evidence_store.py
# VERSION: v1.0.0-KENNEL-PAYSHAP-EVIDENCE-STORE
# AUTHORITY BOUNDARY: provider observation only; no business projection or settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
