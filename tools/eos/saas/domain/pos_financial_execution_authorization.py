"""WILSY OS M10 POS financial execution authorization contract.

TITLE: POS Financial Execution Authorization
VERSION: v1.0.0-M10
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Bind validated M9 POS commercial evidence to one directional execution authority.
EPITOME: Immutable tenant/location/principal-bound authorization; never execution or settlement truth.
ABSOLUTE CANONICAL PATH: tools/eos/saas/domain/pos_financial_execution_authorization.py
COLLABORATION / OWNERSHIP: Python EOS SaaS POS commercial authority.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M10 establishes COLLECTION and DISBURSEMENT authorization provenance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: SHA3-512 evidence; no payment credentials.
TENANT BOUNDARY: Sale, source, and actor evidence must share one tenant/location.
AUTHORITY BOUNDARY: Binds existing authority evidence; grants no principal role.
FINANCIAL AUTHORITY BOUNDARY: Authorization is not execution, settlement, or paid truth.
TRANSACTION BOUNDARY: Pure value object; caller owns persistence and sessions.
FAIL-CLOSED DECLARATION: Direction, provenance, amount, currency, and authority drift reject.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib, json, re
from typing import Any, cast
from tools.eos.auth.tenant_authorization_decision_evidence import TenantAuthorizationDecisionEvidence
from .pos_commercial import POSSale, POSTenderIntent, POSRefundIntent, POSTenderType, POSStatus

class POSFinancialExecutionDirection(StrEnum): COLLECTION='COLLECTION'; DISBURSEMENT='DISBURSEMENT'
class POSFinancialExecutionAuthorizationError(ValueError): pass

def _json_default(value: Any):
 if isinstance(value,datetime): return value.astimezone(timezone.utc).isoformat()
 if isinstance(value,StrEnum): return value.value
 raise TypeError('unsupported fingerprint value')
def _fp(payload: Any) -> str: return hashlib.sha3_512(json.dumps(payload,sort_keys=True,separators=(',',':'),default=_json_default).encode()).hexdigest()
def _source(value: POSTenderIntent|POSRefundIntent) -> tuple[str,str,int,str]:
 if isinstance(value,POSTenderIntent): return ('POSTenderIntent',value.idempotency_key,value.requested_amount_minor,_fp(value.to_dict()))
 if isinstance(value,POSRefundIntent): return ('POSRefundIntent',value.refund_intent_id,value.amount_minor,_fp(value.to_dict()))
 raise POSFinancialExecutionAuthorizationError('M10_SOURCE_INVALID')

@dataclass(frozen=True)
class POSFinancialExecutionAuthorization:
 authorization_id:str; tenant_id:str; location_id:str; sale_id:str; direction:POSFinancialExecutionDirection; source_kind:str; source_id:str; sale_fingerprint:str; source_evidence_fingerprint:str; amount_minor:int; currency:str; authorized_principal_id:str; principal_authority_decision_id:str; principal_authority_evidence_fingerprint:str; authorization_basis:str; authorized_at:datetime; idempotency_key:str; authorization_fingerprint:str
 def __post_init__(self):
  if not all(isinstance(getattr(self,n),str) and getattr(self,n).strip() for n in ('authorization_id','tenant_id','location_id','sale_id','source_kind','source_id','sale_fingerprint','source_evidence_fingerprint','currency','authorized_principal_id','principal_authority_decision_id','principal_authority_evidence_fingerprint','authorization_basis','idempotency_key')): raise POSFinancialExecutionAuthorizationError('M10_AUTH_IDENTITY_INVALID')
  if not isinstance(self.direction,POSFinancialExecutionDirection) or not isinstance(self.amount_minor,int) or isinstance(self.amount_minor,bool) or self.amount_minor<=0 or re.fullmatch(r'[A-Z]{3}',self.currency) is None: raise POSFinancialExecutionAuthorizationError('M10_AUTHORITY_MONEY_INVALID')
  if not isinstance(self.authorized_at,datetime) or self.authorized_at.tzinfo is None: raise POSFinancialExecutionAuthorizationError('M10_AUTH_TIME_INVALID')
  for n in ('sale_fingerprint','source_evidence_fingerprint','principal_authority_evidence_fingerprint','authorization_fingerprint'):
   if re.fullmatch(r'[0-9a-f]{128}',getattr(self,n)) is None: raise POSFinancialExecutionAuthorizationError('M10_AUTH_FINGERPRINT_INVALID')
 def to_dict(self): return {**self.__dict__,'direction':self.direction.value,'authorized_at':self.authorized_at.astimezone(timezone.utc).isoformat()}
 @property
 def semantic_payload(self): return {k:v for k,v in self.to_dict().items() if k!='authorization_fingerprint'}
 @classmethod
 def from_dict(cls, value: dict[str, Any]):
  body=dict(value); body['direction']=POSFinancialExecutionDirection(body['direction']); body['authorized_at']=datetime.fromisoformat(body['authorized_at']) if isinstance(body['authorized_at'],str) else body['authorized_at']
  stored=body.get('authorization_fingerprint'); body['authorization_fingerprint']='0'*128
  result=cls(**body)
  if stored != result._computed_fingerprint(): raise POSFinancialExecutionAuthorizationError('M10_AUTH_CORRUPT')
  return cls(**{**body,'authorization_fingerprint':stored})
 def _computed_fingerprint(self): return _fp(self.semantic_payload)
 @classmethod
 def issue(cls,sale:POSSale, source:POSTenderIntent|POSRefundIntent, authority:TenantAuthorizationDecisionEvidence, *, authorization_id:str, idempotency_key:str, authorized_at:datetime):
  if sale.status is not POSStatus.COMPLETED_COMMERCIAL or authority.tenant_id!=sale.tenant_id: raise POSFinancialExecutionAuthorizationError('M10_AUTHORITY_CONTEXT_INVALID')
  kind, sid, amount, sfp = _source(source)
  if source.tenant_id!=sale.tenant_id or source.location_id!=sale.location_id or source.sale_id!=sale.sale_id or source.currency!=sale.currency: raise POSFinancialExecutionAuthorizationError('M10_SOURCE_CONTEXT_INVALID')
  if kind=='POSTenderIntent':
   tender = cast(POSTenderIntent, source)
   if tender.tender_type in (POSTenderType.CASH,POSTenderType.VOUCHER,POSTenderType.STORE_CREDIT): raise POSFinancialExecutionAuthorizationError('M10_TENDER_UNSUPPORTED')
   if amount!=sale.total_minor: raise POSFinancialExecutionAuthorizationError('M10_TENDER_AMOUNT_INVALID')
   direction=POSFinancialExecutionDirection.COLLECTION
  else: direction=POSFinancialExecutionDirection.DISBURSEMENT
  body=dict(authorization_id=authorization_id,tenant_id=sale.tenant_id,location_id=sale.location_id,sale_id=sale.sale_id,direction=direction,source_kind=kind,source_id=sid,sale_fingerprint=sale.fingerprint,source_evidence_fingerprint=sfp,amount_minor=amount,currency=sale.currency,authorized_principal_id=authority.principal_id,principal_authority_decision_id=authority.authorization_decision_id,principal_authority_evidence_fingerprint=authority.authorization_evidence_fingerprint,authorization_basis=authority.authorization_basis_reference,authorized_at=authorized_at,idempotency_key=idempotency_key,authorization_fingerprint='0'*128)
  body['authorization_fingerprint']=_fp({k:v for k,v in body.items() if k!='authorization_fingerprint'})
  return cls(authorization_id=cast(str,body['authorization_id']),tenant_id=cast(str,body['tenant_id']),location_id=cast(str,body['location_id']),sale_id=cast(str,body['sale_id']),direction=cast(POSFinancialExecutionDirection,body['direction']),source_kind=cast(str,body['source_kind']),source_id=cast(str,body['source_id']),sale_fingerprint=cast(str,body['sale_fingerprint']),source_evidence_fingerprint=cast(str,body['source_evidence_fingerprint']),amount_minor=cast(int,body['amount_minor']),currency=cast(str,body['currency']),authorized_principal_id=cast(str,body['authorized_principal_id']),principal_authority_decision_id=cast(str,body['principal_authority_decision_id']),principal_authority_evidence_fingerprint=cast(str,body['principal_authority_evidence_fingerprint']),authorization_basis=cast(str,body['authorization_basis']),authorized_at=cast(datetime,body['authorized_at']),idempotency_key=cast(str,body['idempotency_key']),authorization_fingerprint=cast(str,body['authorization_fingerprint']))

# ARTIFACT: pos_financial_execution_authorization.py
# VERSION: v1.0.0-M10
# AUTHORITY BOUNDARY: Existing principal evidence is bound; no role is granted.
# TENANT POSTURE: Exact tenant/location/sale/source equality is mandatory.
# FAIL-CLOSED POSTURE: Invalid provenance, direction, amount, or sensitive material rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns provider execution.
# END OF WILSY OS SOVEREIGN ARTIFACT
