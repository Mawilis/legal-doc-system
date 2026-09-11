"""WILSY OS M11C deterministic commercial-receivable aging projection.
TITLE: Commercial Receivable Aging
VERSION: v1.0.0-M11C
AUTHORITY: Wilsy OS Core Governance
EPITOME: Pure tenant/family-scoped aging derived from receivable and due-date facts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/commercial_receivable_aging.py
COLLABORATION / OWNERSHIP: M11C Python commercial aging owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11C establishes explicit-clock aging buckets.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque tenant-scoped identifiers only.
TENANT BOUNDARY: Receivable identity and fingerprint remain tenant-bound.
AUTHORITY BOUNDARY: Derived commercial projection only.
FINANCIAL AUTHORITY BOUNDARY: No payment, execution, or settlement authority.
TRANSACTION BOUNDARY: Pure value object; no persistence lifecycle.
FAIL-CLOSED DECLARATION: Invalid timestamps, schema, and provenance reject.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib, json
from .commercial_receivable import CommercialReceivable, ReceivableFamily
class AgingBucket(str, Enum): CURRENT='CURRENT'; DAYS_1_30='1_30'; DAYS_31_60='31_60'; DAYS_61_90='61_90'; DAYS_90_PLUS='90_PLUS'
class CommercialReceivableAgingError(ValueError): pass
def _aware(v):
 if not isinstance(v,datetime) or v.tzinfo is None: raise CommercialReceivableAgingError('M11C_INVALID_TIMESTAMP')
 return v.astimezone(timezone.utc)
@dataclass(frozen=True, slots=True)
class CommercialReceivableAging:
 tenant_id:str; receivable_family:ReceivableFamily; receivable_id:str; source_invoice_id:str; currency:str; outstanding_amount_minor:int; due_at:datetime; as_of:datetime; overdue_days:int; bucket:AgingBucket; source_receivable_fingerprint:str
 def __post_init__(self):
  _aware(self.due_at); _aware(self.as_of)
  if self.overdue_days<0: raise CommercialReceivableAgingError('M11C_NEGATIVE_OVERDUE_DAYS')
  if not isinstance(self.bucket,AgingBucket): raise CommercialReceivableAgingError('M11C_INVALID_BUCKET')
  if self.outstanding_amount_minor<0: raise CommercialReceivableAgingError('M11C_INVALID_OUTSTANDING')
 @property
 def aging_fingerprint(self): return hashlib.sha3_512(json.dumps(self.to_dict(False),sort_keys=True,separators=(',',':')).encode()).hexdigest()
 def to_dict(self,include_fingerprint=True):
  d={'tenant_id':self.tenant_id,'receivable_family':self.receivable_family.value,'receivable_id':self.receivable_id,'source_invoice_id':self.source_invoice_id,'currency':self.currency,'outstanding_amount_minor':self.outstanding_amount_minor,'due_at':_aware(self.due_at).isoformat(),'as_of':_aware(self.as_of).isoformat(),'overdue_days':self.overdue_days,'bucket':self.bucket.value,'source_receivable_fingerprint':self.source_receivable_fingerprint}
  if include_fingerprint:d['aging_fingerprint']=self.aging_fingerprint
  return d
 @classmethod
 def from_receivable(cls,receivable:CommercialReceivable,due_at:datetime,as_of:datetime):
  due=_aware(due_at); now=_aware(as_of); overdue=0 if receivable.outstanding_amount_minor == 0 else max(0,(now.date()-due.date()).days) if now.date()>due.date() else 0
  bucket=AgingBucket.CURRENT if receivable.outstanding_amount_minor == 0 or overdue==0 else AgingBucket.DAYS_1_30 if overdue<=30 else AgingBucket.DAYS_31_60 if overdue<=60 else AgingBucket.DAYS_61_90 if overdue<=90 else AgingBucket.DAYS_90_PLUS
  return cls(receivable.tenant_id,receivable.receivable_family,receivable.receivable_id,receivable.source_invoice_id,receivable.currency,receivable.outstanding_amount_minor,due,now,overdue,bucket,receivable.receivable_fingerprint)
 @classmethod
 def from_dict(cls,payload):
  if set(payload)!={'tenant_id','receivable_family','receivable_id','source_invoice_id','currency','outstanding_amount_minor','due_at','as_of','overdue_days','bucket','source_receivable_fingerprint','aging_fingerprint'} or '_id' in payload: raise CommercialReceivableAgingError('M11C_INVALID_SCHEMA')
  try: v=cls(payload['tenant_id'],ReceivableFamily(payload['receivable_family']),payload['receivable_id'],payload['source_invoice_id'],payload['currency'],payload['outstanding_amount_minor'],datetime.fromisoformat(payload['due_at']),datetime.fromisoformat(payload['as_of']),payload['overdue_days'],AgingBucket(payload['bucket']),payload['source_receivable_fingerprint'])
  except Exception as e: raise CommercialReceivableAgingError('M11C_INVALID_SCHEMA') from e
  if payload['aging_fingerprint']!=v.aging_fingerprint: raise CommercialReceivableAgingError('M11C_FINGERPRINT_MISMATCH')
  return v
# ARTIFACT: commercial_receivable_aging.py
# VERSION: v1.0.0-M11C
# AUTHORITY BOUNDARY: Derived commercial projection only.
# TENANT POSTURE: Tenant/family-scoped.
# FAIL-CLOSED POSTURE: Invalid provenance rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
