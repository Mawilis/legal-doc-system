"""WILSY OS Kennel platform execution truth; distinct from AP payable truth.
TITLE: Platform Billing Financial Execution Truth
VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
AUTHORITY: Kennel EOS / Wilsy OS Core Governance
EPITOME: Immutable platform execution evidence with no payable provenance.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/domain/platform_billing_financial_execution_truth.py
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations
import hashlib, json, re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

class PlatformBillingFinancialExecutionTruthError(ValueError): """Fail-closed validation error."""
class PlatformExecutionStatus(StrEnum): SUBMITTED="SUBMITTED"; ACCEPTED="ACCEPTED"; EXECUTED="EXECUTED"; FAILED="FAILED"

@dataclass(frozen=True)
class PlatformBillingFinancialExecutionTruth:
    tenant_id: str; execution_truth_id: str; platform_invoice_id: str; execution_request_id: str; execution_command_id: str; release_authorization_id: str; provider: str; provider_execution_reference: str; execution_status: PlatformExecutionStatus; executed_amount_minor: int; currency: str; executed_at: datetime|None; payment_destination_reference: str; provider_evidence_reference: str; execution_command_fingerprint: str; execution_evidence_fingerprint: str; created_at: datetime
    def __post_init__(self)->None:
        for n in ('tenant_id','platform_invoice_id','execution_request_id','execution_command_id','release_authorization_id','provider','provider_execution_reference','payment_destination_reference','provider_evidence_reference'):
            if not isinstance(getattr(self,n),str) or not getattr(self,n).strip(): raise PlatformBillingFinancialExecutionTruthError(f'{n} is invalid')
        if not isinstance(self.execution_status,PlatformExecutionStatus): raise PlatformBillingFinancialExecutionTruthError('execution_status is invalid')
        if not isinstance(self.executed_amount_minor,int) or isinstance(self.executed_amount_minor,bool) or self.executed_amount_minor<=0: raise PlatformBillingFinancialExecutionTruthError('amount is invalid')
        if not isinstance(self.currency,str) or re.fullmatch(r'[A-Z]{3}',self.currency) is None: raise PlatformBillingFinancialExecutionTruthError('currency is invalid')
        for n in ('created_at',):
            if not isinstance(getattr(self,n),datetime) or getattr(self,n).tzinfo is None: raise PlatformBillingFinancialExecutionTruthError('timestamp is invalid')
        if self.execution_status is PlatformExecutionStatus.EXECUTED and (not isinstance(self.executed_at,datetime) or self.executed_at.tzinfo is None): raise PlatformBillingFinancialExecutionTruthError('EXECUTED requires executed_at')
        if self.execution_status is not PlatformExecutionStatus.EXECUTED and self.executed_at is not None: raise PlatformBillingFinancialExecutionTruthError('non-EXECUTED cannot carry executed_at')
        if any(re.fullmatch(r'[0-9a-f]{128}',x) is None for x in (self.execution_command_fingerprint,self.execution_evidence_fingerprint)): raise PlatformBillingFinancialExecutionTruthError('fingerprint is invalid')
    @classmethod
    def from_command(cls, command, *, provider:str, provider_execution_reference:str, execution_status:PlatformExecutionStatus, executed_at:datetime|None, provider_evidence_reference:str, created_at:datetime)->'PlatformBillingFinancialExecutionTruth':
        from .platform_billing_financial_execution_command import PlatformBillingFinancialExecutionCommand
        if not isinstance(command,PlatformBillingFinancialExecutionCommand): raise PlatformBillingFinancialExecutionTruthError('command is invalid')
        return cls(command.tenant_id,f'platform-truth-{command.execution_request_id}',command.platform_invoice_id,command.execution_request_id,command.execution_command_id,command.release_authorization_id,provider,provider_execution_reference,execution_status,command.amount_minor,command.currency,executed_at,command.payment_destination_reference,provider_evidence_reference,command.fingerprint,hashlib.sha3_512(f'{command.fingerprint}:{provider}:{provider_execution_reference}:{execution_status.value}'.encode()).hexdigest(),created_at)
    def to_dict(self): return {k:(v.value if isinstance(v,StrEnum) else v.isoformat() if isinstance(v,datetime) else v) for k,v in self.__dict__.items()}
    @property
    def fingerprint(self): return hashlib.sha3_512(json.dumps(self.to_dict(),sort_keys=True,separators=(',',':')).encode()).hexdigest()

# ARTIFACT: platform_billing_financial_execution_truth.py
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY BOUNDARY: Platform Kennel execution evidence only; no settlement.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
# WILSY OS SOVEREIGN ARTIFACT STRUCTURE
# TITLE: R3F0 Platform Billing Financial Execution Truth and Settlement Evidence
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY: Wilsy OS Core Governance / Kennel EOS
# PURPOSE: Durable, tenant-scoped platform execution and settlement evidence.
# EPITOME: Canonical platform financial truth without provider execution or money movement.
# ABSOLUTE CANONICAL PATH: tools/eos/kennel/domain/platform_billing_financial_execution_truth.py
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

# ARTIFACT: tools/eos/kennel/domain/platform_billing_financial_execution_truth.py
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY BOUNDARY: Certification evidence only.
# TENANT POSTURE: Tenant-scoped synthetic fixtures.
# FAIL-CLOSED POSTURE: Failures are surfaced; no skips.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
