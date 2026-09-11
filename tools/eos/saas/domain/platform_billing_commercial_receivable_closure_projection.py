"""WILSY OS M11D2 platform commercial receivable closure projection.
TITLE: Platform Billing Commercial Receivable Closure Projection
VERSION: v1.1.0-M11D2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable PLATFORM-only closure derived from R3F settlement evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/platform_billing_commercial_receivable_closure_projection.py
COLLABORATION / OWNERSHIP: AR1P/M11D2 SaaS billing domain owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.1.0-M11D2 adds strict construction, hydration, and fingerprint validation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped immutable evidence.
TENANT BOUNDARY: Every projection is tenant-bound.
AUTHORITY BOUNDARY: Settlement-derived commercial projection only.
FINANCIAL AUTHORITY BOUNDARY: Kennel owns execution and settlement evidence.
TRANSACTION BOUNDARY: Pure value object; persistence is caller-owned.
FAIL-CLOSED DECLARATION: Invalid provenance, schema, and fingerprints reject.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib, json, re
class PlatformBillingCommercialReceivableClosureProjectionError(ValueError): pass
@dataclass(frozen=True, slots=True)
class PlatformBillingCommercialReceivableClosureProjection:
 tenant_id:str; commercial_receivable_closure_projection_id:str; platform_invoice_id:str; platform_invoice_evidence_fingerprint:str; commercial_settlement_projection_id:str; commercial_settlement_projection_fingerprint:str; settlement_evidence_id:str; release_authorization_id:str; currency:str; original_receivable_amount_minor:int; closed_receivable_amount_minor:int; remaining_receivable_amount_minor:int; closed_at:datetime; projected_at:datetime; receivable_status:str
 def __post_init__(self):
  if any(not isinstance(getattr(self,n),str) or not getattr(self,n).strip() for n in ('tenant_id','commercial_receivable_closure_projection_id','platform_invoice_id','commercial_settlement_projection_id','settlement_evidence_id','release_authorization_id')): raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_INVALID_IDENTITY')
  if not re.fullmatch(r'[A-Z]{3}',self.currency) or self.receivable_status!='CLOSED': raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_INVALID_STATUS_OR_CURRENCY')
  for n in ('original_receivable_amount_minor','closed_receivable_amount_minor','remaining_receivable_amount_minor'):
   v=getattr(self,n)
   if isinstance(v,bool) or not isinstance(v,int) or v<0: raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_INVALID_AMOUNT')
  if self.remaining_receivable_amount_minor!=0 or self.closed_receivable_amount_minor!=self.original_receivable_amount_minor: raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_NOT_CLOSED')
  if any(not isinstance(getattr(self,n),str) or not re.fullmatch(r'[0-9a-f]{128}',getattr(self,n)) for n in ('platform_invoice_evidence_fingerprint','commercial_settlement_projection_fingerprint')): raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_INVALID_FINGERPRINT')
  if any(not isinstance(getattr(self,n),datetime) or getattr(self,n).tzinfo is None for n in ('closed_at','projected_at')): raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_INVALID_TIMESTAMP')
 @property
 def projection_fingerprint(self): return hashlib.sha3_512(json.dumps(self.to_dict(False),sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()
 def to_dict(self,include_fingerprint=True):
  d=asdict(self); d['closed_at']=self.closed_at.astimezone(timezone.utc).isoformat(); d['projected_at']=self.projected_at.astimezone(timezone.utc).isoformat()
  if include_fingerprint:d['projection_fingerprint']=self.projection_fingerprint
  return d
 @classmethod
 def from_dict(cls,payload):
  fields=set(cls.__dataclass_fields__)|{'projection_fingerprint'}
  if not isinstance(payload,dict) or set(payload)!=fields: raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_INVALID_SCHEMA')
  try:
   data={k:payload[k] for k in cls.__dataclass_fields__}; data['closed_at']=datetime.fromisoformat(payload['closed_at']); data['projected_at']=datetime.fromisoformat(payload['projected_at']); value=cls(**data)
  except Exception as error: raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_INVALID_SCHEMA') from error
  if payload['projection_fingerprint']!=value.projection_fingerprint: raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_FINGERPRINT_MISMATCH')
  return value
# ARTIFACT: platform_billing_commercial_receivable_closure_projection.py
# VERSION: v1.1.0-M11D2
# AUTHORITY BOUNDARY: Settlement-derived commercial projection only.
# TENANT POSTURE: Explicit PLATFORM tenant scope.
# FAIL-CLOSED POSTURE: Invalid evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
