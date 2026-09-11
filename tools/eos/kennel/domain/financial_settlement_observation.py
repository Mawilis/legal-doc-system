"""WILSY OS — authenticated provider settlement observation contract.

TITLE: Financial Settlement Observation
VERSION: v1.0.0-M11E2D4
AUTHORITY: Kennel EOS / Wilsy OS Core Governance
EPITOME: Immutable authenticated clearing evidence, distinct from settlement truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/financial_settlement_observation.py
COLLABORATION / OWNERSHIP: Kennel EOS settlement-observation owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11E2D4 establishes tenant-scoped settlement observation evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: opaque references only; no provider payloads or credentials.
TENANT BOUNDARY: tenant and execution identity are immutable and required.
AUTHORITY BOUNDARY: authenticated observation only; no platform settlement evidence.
FINANCIAL AUTHORITY BOUNDARY: no paid state, closure, reconciliation, or provider execution.
TRANSACTION BOUNDARY: pure value object; persistence is registry-owned.
FAIL-CLOSED DECLARATION: weak, ambiguous, mismatched, or malformed evidence rejects.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import hashlib,json,re
from .financial_execution_provider_observation import EvidenceStrength, TransportDisposition

class FinancialSettlementObservationError(ValueError):
    """Fail-closed settlement observation validation error."""
class SettlementObservationStatus(StrEnum):
    SETTLED="SETTLED"
    CLEARED="CLEARED"

@dataclass(frozen=True)
class FinancialSettlementObservation:
    tenant_id:str; observation_id:str; provider_name:str; execution_truth_id:str; provider_execution_reference:str; settlement_reference:str; provider_settlement_evidence_reference:str; status:SettlementObservationStatus; settled_amount_minor:int; currency:str; payment_destination_reference:str; observed_at:datetime; settled_at:datetime; evidence_strength:EvidenceStrength; transport_disposition:TransportDisposition
    def __post_init__(self):
        for n in ('tenant_id','observation_id','provider_name','execution_truth_id','provider_execution_reference','settlement_reference','provider_settlement_evidence_reference','payment_destination_reference'):
            if not isinstance(getattr(self,n),str) or not getattr(self,n).strip(): raise FinancialSettlementObservationError(f'{n} is invalid')
        if not isinstance(self.status,SettlementObservationStatus) or self.status is not SettlementObservationStatus.SETTLED: raise FinancialSettlementObservationError('settlement status is invalid')
        if not isinstance(self.evidence_strength,EvidenceStrength) or self.evidence_strength not in {EvidenceStrength.AUTHENTICATED,EvidenceStrength.CORROBORATED}: raise FinancialSettlementObservationError('evidence strength is insufficient')
        if self.transport_disposition is TransportDisposition.AMBIGUOUS: raise FinancialSettlementObservationError('transport is ambiguous')
        if not isinstance(self.settled_amount_minor,int) or isinstance(self.settled_amount_minor,bool) or self.settled_amount_minor<=0: raise FinancialSettlementObservationError('amount is invalid')
        if not isinstance(self.currency,str) or re.fullmatch(r'[A-Z]{3}',self.currency) is None: raise FinancialSettlementObservationError('currency is invalid')
        if any(not isinstance(getattr(self,n),datetime) or getattr(self,n).tzinfo is None for n in ('observed_at','settled_at')): raise FinancialSettlementObservationError('timestamps are invalid')
    def to_dict(self): return {k:(v.value if isinstance(v,StrEnum) else v.isoformat() if isinstance(v,datetime) else v) for k,v in self.__dict__.items()}
    @property
    def fingerprint(self): return hashlib.sha3_512(json.dumps(self.to_dict(),sort_keys=True,separators=(',',':')).encode()).hexdigest()

# ARTIFACT: financial_settlement_observation.py
# VERSION: v1.0.0-M11E2D4
# AUTHORITY BOUNDARY: authenticated observation only; no settlement truth.
# TENANT POSTURE: execution-correlated and tenant-scoped.
# FAIL-CLOSED POSTURE: weak, ambiguous, divergent, or corrupt evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
