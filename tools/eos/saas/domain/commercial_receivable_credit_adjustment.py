"""WILSY OS M11D1 typed commercial credit adjustment.
TITLE: Commercial Receivable Credit Adjustment
VERSION: v1.0.0-M11D1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable credit-only commercial obligation evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/commercial_receivable_credit_adjustment.py
COLLABORATION / OWNERSHIP: M11D1 Python EOS commercial-adjustment owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11D1 establishes tenant/family/invoice-bound credit truth.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque tenant identifiers; no provider data.
TENANT BOUNDARY: Adjustment is bound to one receivable and invoice.
AUTHORITY BOUNDARY: Commercial obligation adjustment only.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, execution, or Kennel authority.
TRANSACTION BOUNDARY: Pure value object; no persistence.
FAIL-CLOSED DECLARATION: Invalid provenance, amount, schema, or fingerprint rejects.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib, json, re
from .commercial_receivable import ReceivableFamily, CommercialReceivable

class CreditAdjustmentError(ValueError): pass
class CreditBasis(str, Enum): CREDIT_NOTE='CREDIT_NOTE'; COMMERCIAL_CORRECTION='COMMERCIAL_CORRECTION'; SERVICE_CREDIT='SERVICE_CREDIT'
@dataclass(frozen=True, slots=True)
class CommercialReceivableCreditAdjustment:
 tenant_id:str; receivable_family:ReceivableFamily; receivable_id:str; source_invoice_id:str; adjustment_id:str; currency:str; amount_minor:int; basis:CreditBasis; source_receivable_fingerprint:str; effective_at:datetime
 def __post_init__(self):
  if any(not isinstance(getattr(self,n),str) or not getattr(self,n).strip() for n in ('tenant_id','receivable_id','source_invoice_id','adjustment_id')): raise CreditAdjustmentError('M11D1_INVALID_IDENTITY')
  if not isinstance(self.receivable_family,ReceivableFamily) or not re.fullmatch(r'[A-Z]{3}',self.currency): raise CreditAdjustmentError('M11D1_INVALID_PROVENANCE')
  if isinstance(self.amount_minor,bool) or not isinstance(self.amount_minor,int) or self.amount_minor<=0: raise CreditAdjustmentError('M11D1_INVALID_CREDIT_AMOUNT')
  if not isinstance(self.basis,CreditBasis) or not isinstance(self.effective_at,datetime) or self.effective_at.tzinfo is None or not re.fullmatch(r'[0-9a-f]{128}',self.source_receivable_fingerprint): raise CreditAdjustmentError('M11D1_INVALID_EVIDENCE')
 @property
 def adjustment_fingerprint(self): return hashlib.sha3_512(json.dumps(self.to_dict(False),sort_keys=True,separators=(',',':')).encode()).hexdigest()
 def to_dict(self,include_fingerprint=True):
  d={'tenant_id':self.tenant_id,'receivable_family':self.receivable_family.value,'receivable_id':self.receivable_id,'source_invoice_id':self.source_invoice_id,'adjustment_id':self.adjustment_id,'currency':self.currency,'amount_minor':self.amount_minor,'basis':self.basis.value,'source_receivable_fingerprint':self.source_receivable_fingerprint,'effective_at':self.effective_at.astimezone(timezone.utc).isoformat()}
  if include_fingerprint:d['adjustment_fingerprint']=self.adjustment_fingerprint
  return d
 @classmethod
 def from_receivable(cls,receivable:CommercialReceivable,adjustment_id:str,amount_minor:int,basis:CreditBasis,effective_at:datetime): return cls(receivable.tenant_id,receivable.receivable_family,receivable.receivable_id,receivable.source_invoice_id,adjustment_id,receivable.currency,amount_minor,basis,receivable.receivable_fingerprint,effective_at)
 @classmethod
 def from_dict(cls,payload):
  fields={'tenant_id','receivable_family','receivable_id','source_invoice_id','adjustment_id','currency','amount_minor','basis','source_receivable_fingerprint','effective_at','adjustment_fingerprint'}
  if not isinstance(payload,dict) or set(payload)!=fields: raise CreditAdjustmentError('M11D1_INVALID_SCHEMA')
  try: value=cls(payload['tenant_id'],ReceivableFamily(payload['receivable_family']),payload['receivable_id'],payload['source_invoice_id'],payload['adjustment_id'],payload['currency'],payload['amount_minor'],CreditBasis(payload['basis']),payload['source_receivable_fingerprint'],datetime.fromisoformat(payload['effective_at']))
  except Exception as error: raise CreditAdjustmentError('M11D1_INVALID_SCHEMA') from error
  if payload['adjustment_fingerprint']!=value.adjustment_fingerprint: raise CreditAdjustmentError('M11D1_FINGERPRINT_MISMATCH')
  return value

# ARTIFACT: commercial_receivable_credit_adjustment.py
# VERSION: v1.0.0-M11D1
# AUTHORITY BOUNDARY: Commercial adjustment only.
# TENANT POSTURE: Explicit tenant/family/invoice binding.
# FAIL-CLOSED POSTURE: Invalid evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
