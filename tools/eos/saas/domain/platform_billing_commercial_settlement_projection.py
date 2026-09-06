"""WILSY OS R3F-A commercial settlement projection domain.
TITLE: Platform Billing Commercial Settlement Projection
VERSION: v1.0.0-R3F-A
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Immutable commercial consequence derived from Kennel settlement evidence.
EPITOME: Full-liability PAID projection only; no execution or money movement.
ABSOLUTE CANONICAL PATH: tools/eos/saas/domain/platform_billing_commercial_settlement_projection.py
COLLABORATION / OWNERSHIP: SaaS Billing commercial projection owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-R3F-A establishes deterministic projection contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped immutable evidence; no secrets.
TENANT BOUNDARY: All identities are tenant-scoped.
AUTHORITY BOUNDARY: Kennel settlement evidence is authoritative.
FINANCIAL AUTHORITY BOUNDARY: No provider execution or money movement.
TRANSACTION BOUNDARY: Persistence is caller-owned.
FAIL-CLOSED DECLARATION: Invalid provenance or fingerprints are rejected.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib, json, re

class PlatformBillingCommercialSettlementProjectionError(ValueError): pass

@dataclass(frozen=True)
class PlatformBillingCommercialSettlementProjection:
    tenant_id:str; commercial_settlement_projection_id:str; settlement_evidence_id:str; settlement_evidence_fingerprint:str; platform_execution_truth_id:str; execution_request_id:str; execution_command_id:str; release_authorization_id:str; release_authorization_fingerprint:str; platform_invoice_id:str; platform_invoice_evidence_fingerprint:str; settled_amount_minor:int; currency:str; settled_at:datetime; projected_at:datetime; projected_status:str; projected_amount_paid_minor:int; projected_outstanding_amount_minor:int
    def __post_init__(self):
        if any(not isinstance(getattr(self,n),str) or not getattr(self,n).strip() for n in ('tenant_id','commercial_settlement_projection_id','settlement_evidence_id','platform_execution_truth_id','execution_request_id','execution_command_id','release_authorization_id','platform_invoice_id')): raise PlatformBillingCommercialSettlementProjectionError('identity is invalid')
        if any(re.fullmatch(r'[0-9a-f]{128}',getattr(self,n) or '') is None for n in ('settlement_evidence_fingerprint','release_authorization_fingerprint','platform_invoice_evidence_fingerprint')): raise PlatformBillingCommercialSettlementProjectionError('fingerprint is invalid')
        if not isinstance(self.settled_amount_minor,int) or self.settled_amount_minor<=0 or self.projected_amount_paid_minor!=self.settled_amount_minor or self.projected_outstanding_amount_minor!=0: raise PlatformBillingCommercialSettlementProjectionError('amount is invalid')
        if re.fullmatch(r'[A-Z]{3}',self.currency) is None or self.projected_status!='PAID': raise PlatformBillingCommercialSettlementProjectionError('status or currency is invalid')
        if any(not isinstance(getattr(self,n),datetime) or getattr(self,n).tzinfo is None for n in ('settled_at','projected_at')) or self.projected_at<self.settled_at: raise PlatformBillingCommercialSettlementProjectionError('timestamp is invalid')
    @property
    def projection_fingerprint(self)->str:
        return hashlib.sha3_512(json.dumps(self.to_dict(include_fingerprint=False),sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()
    def to_dict(self,include_fingerprint=True):
        d=asdict(self); d['settled_at']=self.settled_at.isoformat(); d['projected_at']=self.projected_at.isoformat()
        if include_fingerprint:d['projection_fingerprint']=self.projection_fingerprint
        return d

# ARTIFACT: platform_billing_commercial_settlement_projection.py
# VERSION: v1.0.0-R3F-A
# AUTHORITY BOUNDARY: Commercial projection only.
# FAIL-CLOSED POSTURE: Invalid evidence fails closed.
# END OF WILSY OS SOVEREIGN ARTIFACT
