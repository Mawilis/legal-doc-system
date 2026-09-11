"""WILSY OS M9 canonical POS commercial contract.

TITLE: POS Commercial Domain
VERSION: v1.0.0-M9
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Define canonical M9 POS commercial truth and invariants without electronic financial execution authority.
EPITOME: Immutable tenant/location-scoped cart and sale truth.
ABSOLUTE CANONICAL PATH: tools/eos/saas/domain/pos_commercial.py
COLLABORATION / OWNERSHIP: Python EOS POS commercial owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M9 establishes cart, sale, tender-intent, and return contracts.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant/location scoped; no payment secrets.
TENANT BOUNDARY: Every aggregate binds tenant_id and location_id.
AUTHORITY BOUNDARY: Commercial truth only; Kennel owns electronic execution.
FINANCIAL AUTHORITY BOUNDARY: No paid, settled, provider, or execution fields.
TRANSACTION BOUNDARY: Registry callers own sessions and transactions.
FAIL-CLOSED DECLARATION: Invalid arithmetic, identity, and replay material rejects.
"""
from dataclasses import dataclass
from enum import Enum
import hashlib, json
from datetime import datetime

class POSStatus(str, Enum): DRAFT='DRAFT'; OPEN='OPEN'; COMPLETED_COMMERCIAL='COMPLETED_COMMERCIAL'; VOIDED='VOIDED'
class POSTenderType(str, Enum): CASH='CASH'; CARD='CARD'; BANK='BANK'; WALLET='WALLET'; VOUCHER='VOUCHER'; STORE_CREDIT='STORE_CREDIT'
@dataclass(frozen=True)
class POSTenderIntent:
 tenant_id:str; location_id:str; sale_id:str; tender_type:POSTenderType; requested_amount_minor:int; currency:str; idempotency_key:str
 def __post_init__(self):
  if not isinstance(self.requested_amount_minor,int) or self.requested_amount_minor<=0 or not all((self.tenant_id,self.location_id,self.sale_id,self.idempotency_key,self.currency)): raise ValueError('M9_TENDER_INVALID')
 def to_dict(self): return {**self.__dict__,'tender_type':self.tender_type.value}
@dataclass(frozen=True)
class POSCashTender:
 tenant_id:str; location_id:str; sale_id:str; currency:str; amount_due_minor:int; cash_received_minor:int; operator_id:str; recorded_at:str
 def __post_init__(self):
  if not isinstance(self.amount_due_minor,int) or not isinstance(self.cash_received_minor,int) or self.cash_received_minor<self.amount_due_minor or self.amount_due_minor<=0 or not all((self.tenant_id,self.location_id,self.sale_id,self.currency,self.operator_id,self.recorded_at)): raise ValueError('M9_CASH_INSUFFICIENT')
 @property
 def change_due_minor(self): return self.cash_received_minor-self.amount_due_minor
 def to_dict(self): return {**self.__dict__,'change_due_minor':self.change_due_minor}
@dataclass(frozen=True)
class POSReturnIntent:
 tenant_id:str; location_id:str; return_id:str; original_sale_id:str; sku:str; quantity:int; reason:str; idempotency_key:str
 def __post_init__(self):
  if not isinstance(self.quantity,int) or self.quantity<=0 or not all((self.tenant_id,self.location_id,self.return_id,self.original_sale_id,self.sku,self.reason,self.idempotency_key)): raise ValueError('M9_RETURN_INVALID')
 def to_dict(self): return self.__dict__.copy()
@dataclass(frozen=True)
class POSRefundIntent:
 tenant_id:str; location_id:str; refund_intent_id:str; sale_id:str; amount_minor:int; currency:str; basis:str; idempotency_key:str
 def __post_init__(self):
  if not isinstance(self.amount_minor,int) or self.amount_minor<=0 or not all((self.tenant_id,self.location_id,self.refund_intent_id,self.sale_id,self.basis,self.idempotency_key,self.currency)): raise ValueError('M9_REFUND_INVALID')
 def to_dict(self): return self.__dict__.copy()
@dataclass(frozen=True)
class POSLineItem:
 product_id:str; sku:str; description:str; quantity:int; unit_price_minor:int; discount_minor:int; tax_minor:int; currency:str
 def __post_init__(self):
  if not self.product_id or not self.sku or self.quantity<=0 or self.unit_price_minor<0 or self.discount_minor<0 or self.tax_minor<0 or self.discount_minor>self.quantity*self.unit_price_minor: raise ValueError('M9_LINE_INVALID')
  if not isinstance(self.quantity,int) or not isinstance(self.unit_price_minor,int) or not isinstance(self.discount_minor,int) or not isinstance(self.tax_minor,int): raise ValueError('M9_INTEGER_REQUIRED')
 @property
 def line_total_minor(self): return self.quantity*self.unit_price_minor-self.discount_minor+self.tax_minor
 def to_dict(self): return {'product_id':self.product_id,'sku':self.sku,'description':self.description,'quantity':self.quantity,'unit_price_minor':self.unit_price_minor,'discount_minor':self.discount_minor,'tax_minor':self.tax_minor,'currency':self.currency}
@dataclass(frozen=True)
class POSSale:
 tenant_id:str; location_id:str; sale_id:str; currency:str; lines:tuple[POSLineItem,...]; status:POSStatus=POSStatus.DRAFT; idempotency_key:str=''
 def __post_init__(self):
  if not self.tenant_id or not self.location_id or not self.sale_id or not self.idempotency_key or not self.lines: raise ValueError('M9_IDENTITY_REQUIRED')
  if any(x.currency!=self.currency for x in self.lines): raise ValueError('M9_MIXED_CURRENCY')
 @property
 def total_minor(self): return sum(x.line_total_minor for x in self.lines)
 def to_dict(self): return {'tenant_id':self.tenant_id,'location_id':self.location_id,'sale_id':self.sale_id,'currency':self.currency,'lines':[x.to_dict() for x in self.lines],'status':self.status.value,'idempotency_key':self.idempotency_key,'total_minor':self.total_minor,'fingerprint':self.fingerprint}
 @classmethod
 def from_dict(cls, d):
  lines=tuple(POSLineItem(**x) for x in d['lines'])
  return cls(d['tenant_id'],d['location_id'],d['sale_id'],d['currency'],lines,POSStatus(d['status']),d['idempotency_key'])
 @property
 def fingerprint(self):
  payload={'tenant_id':self.tenant_id,'location_id':self.location_id,'sale_id':self.sale_id,'currency':self.currency,'lines':[x.to_dict() for x in self.lines],'idempotency_key':self.idempotency_key,'total_minor':self.total_minor}
  return hashlib.sha3_512(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
# ARTIFACT: pos_commercial.py
# VERSION: v1.0.0-M9
# AUTHORITY BOUNDARY: Commercial POS truth only.
# FAIL-CLOSED POSTURE: No financial execution or settlement authority.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
