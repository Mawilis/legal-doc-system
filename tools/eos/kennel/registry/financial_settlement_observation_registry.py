"""WILSY OS — durable settlement-observation evidence registry.

TITLE: Financial Settlement Observation Registry
VERSION: v1.0.1-M11E2D4
AUTHORITY: Kennel EOS / Wilsy OS Core Governance
EPITOME: Persists immutable authenticated settlement observations without settlement authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/registry/financial_settlement_observation_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS settlement-observation persistence owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11E2D4 establishes tenant replay and corruption-first persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: opaque evidence references only.
TENANT BOUNDARY: every identity and query is tenant-scoped.
AUTHORITY BOUNDARY: observation persistence only; no platform settlement evidence.
FINANCIAL AUTHORITY BOUNDARY: no paid state, projection, reconciliation, or closure.
TRANSACTION BOUNDARY: caller-owned session is forwarded unchanged.
FAIL-CLOSED DECLARATION: corruption and divergent replay never overwrite durable evidence.
"""
from __future__ import annotations
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError
from ..domain.financial_settlement_observation import FinancialSettlementObservation, FinancialSettlementObservationError, SettlementObservationStatus
from ..domain.financial_execution_provider_observation import EvidenceStrength, TransportDisposition
from datetime import datetime,timezone

class FinancialSettlementObservationNotFoundError(RuntimeError): pass
class FinancialSettlementObservationPersistedRecordInvalidError(RuntimeError): pass
class FinancialSettlementObservationConflictError(RuntimeError): pass
class FinancialSettlementObservationRegistry:
    @staticmethod
    def ensure_indexes(collection:Collection)->None:
        collection.create_index([('tenant_id',1),('observation_id',1)],unique=True)
        collection.create_index([('tenant_id',1),('provider_name',1),('provider_execution_reference',1),('settlement_reference',1)],unique=True)
    @staticmethod
    def _hydrate(doc):
        try:
            d={k:v for k,v in doc.items() if k not in {"_id","observation_fingerprint"}}; d['status']=SettlementObservationStatus(d['status']); d['evidence_strength']=EvidenceStrength(d['evidence_strength']); d['transport_disposition']=TransportDisposition(d['transport_disposition'])
            for k in ('observed_at','settled_at'):
                if isinstance(d[k],str): d[k]=datetime.fromisoformat(d[k])
                elif d[k].tzinfo is None:d[k]=d[k].replace(tzinfo=timezone.utc)
            value=FinancialSettlementObservation(**d)
            if doc.get('observation_fingerprint')!=value.fingerprint: raise ValueError
            return value
        except Exception as e: raise FinancialSettlementObservationPersistedRecordInvalidError('M11E2D4_SETTLEMENT_OBSERVATION_INVALID') from e
    @staticmethod
    def create(value:FinancialSettlementObservation,collection:Collection,*,session:ClientSession|None=None):
        document={**value.to_dict(),'observation_fingerprint':value.fingerprint}
        try: collection.insert_one(document,session=session); return 'CREATED',value
        except DuplicateKeyError as e:
            existing=collection.find_one({'tenant_id':value.tenant_id,'observation_id':value.observation_id},session=session)
            if existing is not None and FinancialSettlementObservationRegistry._hydrate(existing)==value:return 'IDEMPOTENT_REPLAY',value
            raise FinancialSettlementObservationConflictError('M11E2D4_SETTLEMENT_OBSERVATION_CONFLICT') from e
    @staticmethod
    def get(tenant_id:str,observation_id:str,collection:Collection,*,session:ClientSession|None=None):
        doc=collection.find_one({'tenant_id':tenant_id,'observation_id':observation_id},session=session)
        if doc is None: raise FinancialSettlementObservationNotFoundError('M11E2D4_SETTLEMENT_OBSERVATION_NOT_FOUND')
        return FinancialSettlementObservationRegistry._hydrate(doc)

# ARTIFACT: financial_settlement_observation_registry.py
# VERSION: v1.0.1-M11E2D4
# AUTHORITY BOUNDARY: observation persistence only; no platform settlement.
# TENANT POSTURE: tenant-scoped replay and hydration.
# FAIL-CLOSED POSTURE: corruption and conflict reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
