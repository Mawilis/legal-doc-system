"""WILSY OS — authenticated settlement-observation ingestion boundary.

TITLE: Authenticated Settlement Observation Ingestion
VERSION: v1.0.0-M11E2D4
AUTHORITY: Kennel EOS / Wilsy OS Core Governance
EPITOME: Correlates authenticated clearing evidence to durable execution truth and persists observation only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/authenticated_settlement_observation_ingestion.py
COLLABORATION / OWNERSHIP: Kennel EOS settlement-ingestion owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11E2D4 establishes fail-closed settlement observation ingestion.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: typed opaque provider references; no raw payloads.
TENANT BOUNDARY: external evidence and durable execution truth must share tenant.
AUTHORITY BOUNDARY: observation evidence only; no settlement truth or projection.
FINANCIAL AUTHORITY BOUNDARY: no provider call, paid state, reconciliation, or closure.
TRANSACTION BOUNDARY: caller-owned active session forwarded to registries.
FAIL-CLOSED DECLARATION: missing, weak, ambiguous, divergent, or corrupt evidence rejects.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from ..domain.financial_execution import FinancialExecutionStatus
from ..domain.financial_execution_provider_observation import EvidenceStrength, TransportDisposition
from ..domain.financial_settlement_observation import FinancialSettlementObservation, SettlementObservationStatus
from ..registry.financial_execution_registry import FinancialExecutionFactRegistry
from ..registry.financial_settlement_observation_registry import FinancialSettlementObservationRegistry
class AuthenticatedSettlementObservationIngestionError(ValueError): pass
@dataclass(frozen=True)
class AuthenticatedSettlementTransportEvidence:
    tenant_id:str; provider_name:str; provider_execution_reference:str; settlement_reference:str; provider_settlement_evidence_reference:str; settled_amount_minor:int; currency:str; payment_destination_reference:str; observed_at:datetime; settled_at:datetime; evidence_strength:EvidenceStrength; transport_disposition:TransportDisposition
def ingest_authenticated_settlement_observation(tenant_id:str,evidence:AuthenticatedSettlementTransportEvidence,*,execution_truth_id:str,execution_truth_collection:Collection,observation_collection:Collection,session:ClientSession):
    if session is None or not bool(getattr(session,'in_transaction',False)): raise AuthenticatedSettlementObservationIngestionError('M11E2D4_ACTIVE_SESSION_REQUIRED')
    if not isinstance(evidence,AuthenticatedSettlementTransportEvidence) or evidence.tenant_id!=tenant_id: raise AuthenticatedSettlementObservationIngestionError('M11E2D4_TENANT_MISMATCH')
    if evidence.evidence_strength not in {EvidenceStrength.AUTHENTICATED,EvidenceStrength.CORROBORATED} or evidence.transport_disposition is TransportDisposition.AMBIGUOUS: raise AuthenticatedSettlementObservationIngestionError('M11E2D4_EVIDENCE_INVALID')
    truth=FinancialExecutionFactRegistry.get(tenant_id,execution_truth_id,execution_truth_collection,session=session)
    if truth is None or truth.execution_status is not FinancialExecutionStatus.EXECUTED or (truth.provider,truth.provider_execution_reference,truth.currency,truth.payment_destination_reference)!=(evidence.provider_name,evidence.provider_execution_reference,evidence.currency,evidence.payment_destination_reference) or evidence.settled_amount_minor>truth.executed_amount_minor: raise AuthenticatedSettlementObservationIngestionError('M11E2D4_EXECUTION_CORRELATION_MISMATCH')
    value=FinancialSettlementObservation(tenant_id,f'settlement-observation-{execution_truth_id}-{evidence.settlement_reference}',evidence.provider_name,execution_truth_id,evidence.provider_execution_reference,evidence.settlement_reference,evidence.provider_settlement_evidence_reference,SettlementObservationStatus.SETTLED,evidence.settled_amount_minor,evidence.currency,evidence.payment_destination_reference,evidence.observed_at,evidence.settled_at,evidence.evidence_strength,evidence.transport_disposition)
    return FinancialSettlementObservationRegistry.create(value,observation_collection,session=session)

# ARTIFACT: authenticated_settlement_observation_ingestion.py
# VERSION: v1.0.0-M11E2D4
# AUTHORITY BOUNDARY: authenticated settlement observation only; no platform evidence.
# TENANT POSTURE: execution-correlated and tenant-scoped.
# FAIL-CLOSED POSTURE: weak, ambiguous, or divergent evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
