"""WILSY OS M11D1 commercial receivable reconciliation projection.
TITLE: Commercial Receivable Settlement-Evidence Reconciliation
VERSION: v1.0.0-M11D1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Deterministic matching projection over receivable, credits, and R3F evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/commercial_receivable_reconciliation.py
COLLABORATION / OWNERSHIP: M11D1 Python EOS reconciliation owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11D1 establishes immutable commercial reconciliation truth.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped evidence references only.
TENANT BOUNDARY: Every source must match the receivable tenant.
AUTHORITY BOUNDARY: Evidence-matching projection only.
FINANCIAL AUTHORITY BOUNDARY: No settlement creation, payment, or execution.
TRANSACTION BOUNDARY: Pure value object; no persistence.
FAIL-CLOSED DECLARATION: Drift, duplicates, excess, schema, and fingerprints reject.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib, json
from .commercial_receivable import CommercialReceivable, ReceivableFamily
from .commercial_receivable_credit_adjustment import CommercialReceivableCreditAdjustment
from .platform_billing_commercial_settlement_projection import PlatformBillingCommercialSettlementProjection
class ReconciliationError(ValueError): pass
@dataclass(frozen=True, slots=True)
class CommercialReceivableReconciliation:
 tenant_id:str; receivable_family:ReceivableFamily; receivable_id:str; source_invoice_id:str; currency:str; original_amount_minor:int; total_credit_minor:int; matched_settlement_minor:int; outstanding_amount_minor:int; source_receivable_fingerprint:str; adjustment_fingerprints:tuple[str,...]; settlement_fingerprints:tuple[str,...]; effective_at:datetime
 def __post_init__(self):
  if self.outstanding_amount_minor<0 or self.total_credit_minor<0 or self.matched_settlement_minor<0 or self.effective_at.tzinfo is None: raise ReconciliationError('M11D1_INVALID_RESULT')
 @property
 def reconciliation_fingerprint(self): return hashlib.sha3_512(json.dumps(self.to_dict(False),sort_keys=True,separators=(',',':')).encode()).hexdigest()
 def to_dict(self,include_fingerprint=True):
  d={'tenant_id':self.tenant_id,'receivable_family':self.receivable_family.value,'receivable_id':self.receivable_id,'source_invoice_id':self.source_invoice_id,'currency':self.currency,'original_amount_minor':self.original_amount_minor,'total_credit_minor':self.total_credit_minor,'matched_settlement_minor':self.matched_settlement_minor,'outstanding_amount_minor':self.outstanding_amount_minor,'source_receivable_fingerprint':self.source_receivable_fingerprint,'adjustment_fingerprints':list(self.adjustment_fingerprints),'settlement_fingerprints':list(self.settlement_fingerprints),'effective_at':self.effective_at.astimezone(timezone.utc).isoformat()}
  if include_fingerprint:d['reconciliation_fingerprint']=self.reconciliation_fingerprint
  return d
 @classmethod
 def from_dict(cls,payload):
  fields={'tenant_id','receivable_family','receivable_id','source_invoice_id','currency','original_amount_minor','total_credit_minor','matched_settlement_minor','outstanding_amount_minor','source_receivable_fingerprint','adjustment_fingerprints','settlement_fingerprints','effective_at','reconciliation_fingerprint'}
  if not isinstance(payload,dict) or set(payload)!=fields: raise ReconciliationError('M11D1_INVALID_SCHEMA')
  try:
   value=cls(payload['tenant_id'],ReceivableFamily(payload['receivable_family']),payload['receivable_id'],payload['source_invoice_id'],payload['currency'],payload['original_amount_minor'],payload['total_credit_minor'],payload['matched_settlement_minor'],payload['outstanding_amount_minor'],payload['source_receivable_fingerprint'],tuple(sorted(payload['adjustment_fingerprints'])),tuple(sorted(payload['settlement_fingerprints'])),datetime.fromisoformat(payload['effective_at']))
  except Exception as error: raise ReconciliationError('M11D1_INVALID_SCHEMA') from error
  if payload['reconciliation_fingerprint']!=value.reconciliation_fingerprint: raise ReconciliationError('M11D1_FINGERPRINT_MISMATCH')
  return value
 @classmethod
 def reconcile(cls,receivable:CommercialReceivable,adjustments=(),settlements=(),effective_at=None):
  adjustments=tuple(adjustments); settlements=tuple(settlements); ids=[a.adjustment_id for a in adjustments]; sids=[s.settlement_evidence_id for s in settlements]
  if len(ids)!=len(set(ids)) or len(sids)!=len(set(sids)): raise ReconciliationError('M11D1_DUPLICATE_EVIDENCE')
  for a in adjustments:
   if (a.tenant_id,a.receivable_family,a.receivable_id,a.source_invoice_id,a.currency,a.source_receivable_fingerprint)!=(receivable.tenant_id,receivable.receivable_family,receivable.receivable_id,receivable.source_invoice_id,receivable.currency,receivable.receivable_fingerprint): raise ReconciliationError('M11D1_PROVENANCE_DRIFT')
  for s in settlements:
   if (s.tenant_id,s.platform_invoice_id,s.currency)!=(receivable.tenant_id,receivable.source_invoice_id,receivable.currency): raise ReconciliationError('M11D1_SETTLEMENT_DRIFT')
  credits=sum(a.amount_minor for a in adjustments); lawful=max(receivable.original_amount_minor-credits,0)
  if credits>receivable.original_amount_minor: raise ReconciliationError('M11D1_OVER_CREDIT')
  matched=sum(s.settled_amount_minor for s in settlements)
  if matched>lawful: raise ReconciliationError('M11D1_OVER_SETTLEMENT')
  if not isinstance(effective_at,datetime) or effective_at.tzinfo is None: raise ReconciliationError('M11D1_INVALID_EFFECTIVE_AT')
  return cls(receivable.tenant_id,receivable.receivable_family,receivable.receivable_id,receivable.source_invoice_id,receivable.currency,receivable.original_amount_minor,credits,matched,lawful-matched,receivable.receivable_fingerprint,tuple(sorted(a.adjustment_fingerprint for a in adjustments)),tuple(sorted(s.projection_fingerprint for s in settlements)),effective_at)

# ARTIFACT: commercial_receivable_reconciliation.py
# VERSION: v1.0.0-M11D1
# AUTHORITY BOUNDARY: Evidence-matching projection only.
# TENANT POSTURE: Tenant/family/invoice firewall.
# FAIL-CLOSED POSTURE: Drift and excess evidence reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
