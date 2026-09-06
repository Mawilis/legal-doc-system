"""TITLE: Platform Billing Financial Settlement Evidence
VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
AUTHORITY: Kennel EOS / Wilsy OS Core Governance
EPITOME: Immutable full-settlement evidence derived from platform execution truth.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/domain/platform_billing_financial_settlement_evidence.py
"""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
from datetime import datetime
from .platform_billing_financial_execution_truth import PlatformBillingFinancialExecutionTruth, PlatformExecutionStatus
class PlatformBillingFinancialSettlementEvidenceError(ValueError): """Fail-closed validation error."""
@dataclass(frozen=True)
class PlatformBillingFinancialSettlementEvidence:
 tenant_id:str; settlement_evidence_id:str; platform_execution_truth_id:str; platform_invoice_id:str; execution_request_id:str; execution_command_id:str; release_authorization_id:str; settled_amount_minor:int; currency:str; settlement_reference:str; provider_settlement_evidence_reference:str; settled_at:datetime; created_at:datetime
 def __post_init__(self):
  for n in ('tenant_id','settlement_evidence_id','platform_execution_truth_id','platform_invoice_id','execution_request_id','execution_command_id','release_authorization_id','settlement_reference','provider_settlement_evidence_reference'):
   if not isinstance(getattr(self,n),str) or not getattr(self,n).strip(): raise PlatformBillingFinancialSettlementEvidenceError(f'{n} is invalid')
  if not isinstance(self.settled_amount_minor,int) or self.settled_amount_minor<=0: raise PlatformBillingFinancialSettlementEvidenceError('amount is invalid')
  if not isinstance(self.currency,str) or len(self.currency)!=3 or not self.currency.isupper(): raise PlatformBillingFinancialSettlementEvidenceError('currency is invalid')
  if any(not isinstance(getattr(self,n),datetime) or getattr(self,n).tzinfo is None for n in ('settled_at','created_at')): raise PlatformBillingFinancialSettlementEvidenceError('timestamp is invalid')
 @classmethod
 def from_execution_truth(cls,truth:PlatformBillingFinancialExecutionTruth,settlement_reference:str,provider_settlement_evidence_reference:str,settled_at:datetime,created_at:datetime):
  if truth.execution_status is not PlatformExecutionStatus.EXECUTED: raise PlatformBillingFinancialSettlementEvidenceError('EXECUTED truth required')
  return cls(truth.tenant_id,f'platform-settlement-{truth.execution_request_id}',f'platform-truth-{truth.execution_request_id}',truth.platform_invoice_id,truth.execution_request_id,truth.execution_command_id,truth.release_authorization_id,truth.executed_amount_minor,truth.currency,settlement_reference,provider_settlement_evidence_reference,settled_at,created_at)
 def to_dict(self): return {k:(v.isoformat() if isinstance(v,datetime) else v) for k,v in self.__dict__.items()}
 @property
 def fingerprint(self): return hashlib.sha3_512(json.dumps(self.to_dict(),sort_keys=True,separators=(',',':')).encode()).hexdigest()
# ARTIFACT: platform_billing_financial_settlement_evidence.py
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY BOUNDARY: Kennel evidence only; no commercial projection.
# END OF WILSY OS SOVEREIGN ARTIFACT
# WILSY OS SOVEREIGN ARTIFACT STRUCTURE
# TITLE: R3F0 Platform Billing Financial Execution Truth and Settlement Evidence
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY: Wilsy OS Core Governance / Kennel EOS
# PURPOSE: Durable, tenant-scoped platform execution and settlement evidence.
# EPITOME: Canonical platform financial truth without provider execution or money movement.
# ABSOLUTE CANONICAL PATH: tools/eos/kennel/domain/platform_billing_financial_settlement_evidence.py
# COLLABORATION / OWNERSHIP: Kennel EOS platform financial domain; R3F0 certificates.
# CERTIFICATION / UPDATE DATE: 2026-09-06; structural remediation.
# CHANGELOG: v1.1.0-R3F0-STRUCTURAL-REMEDIATION complete sovereign metadata alignment.
# COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
# SECURITY / PRIVACY POSTURE: Tenant isolation; UUID synthetic tests; no raw secrets.
# TENANT BOUNDARY: Every read, write, replay, and certificate assertion is tenant-scoped.
# AUTHORITY BOUNDARY: Kennel EOS is exclusive financial execution authority.
# FINANCIAL AUTHORITY BOUNDARY: Evidence only; no provider call, settlement inference, or paid state.
# TRANSACTION BOUNDARY: Caller-owned Mongo session propagates through durable operations.
# FAIL-CLOSED DECLARATION: Invalid authority, provenance, persistence, or hydration fails closed.
# BEGIN SOVEREIGN HEADER SEAL
# END SOVEREIGN HEADER SEAL

# ARTIFACT: tools/eos/kennel/domain/platform_billing_financial_settlement_evidence.py
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY BOUNDARY: Certification evidence only.
# TENANT POSTURE: Tenant-scoped synthetic fixtures.
# FAIL-CLOSED POSTURE: Failures are surfaced; no skips.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
