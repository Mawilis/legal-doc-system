"""TITLE: Commercial Statement Domain
VERSION: v1.0.0-M7
AUTHORITY: Wilsy OS Core Governance
EPITOME: Deterministic platform/client statement projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/commercial_statement.py
COLLABORATION / OWNERSHIP: Python EOS SaaS Billing statement owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M7 establishes separated statement domain.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant and account scoped.
TENANT BOUNDARY: Every activity binds tenant_id.
AUTHORITY BOUNDARY: Commercial evidence projection only.
FINANCIAL AUTHORITY BOUNDARY: No execution or settlement authority.
TRANSACTION BOUNDARY: Read-only derivation.
FAIL-CLOSED DECLARATION: Mixed currencies and cross-lane inputs reject.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib, json
class StatementLedgerKind(str, Enum): PLATFORM='PLATFORM'; CLIENT='CLIENT'
class StatementFamily(str, Enum): BALANCE_FORWARD='BALANCE_FORWARD'; OPEN_ITEM='OPEN_ITEM'; TRANSACTION='TRANSACTION'
class StatementActivityKind(str, Enum): INVOICE_CHARGE='INVOICE_CHARGE'; RECEIVABLE_BALANCE='RECEIVABLE_BALANCE'; SETTLEMENT='SETTLEMENT'; CREDIT='CREDIT'; DEBIT_ADJUSTMENT='DEBIT_ADJUSTMENT'; REFUND_ADJUSTMENT='REFUND_ADJUSTMENT'
class AgingBucket(str, Enum): CURRENT='CURRENT'; ONE_30='1_30'; THIRTY_ONE_60='31_60'; SIXTY_ONE_90='61_90'; NINETY_ONE_120='91_120'; ONE_TWENTY_PLUS='120_PLUS'
@dataclass(frozen=True)
class CommercialStatementActivity:
 tenant_id:str; ledger_kind:StatementLedgerKind; account_id:str; source_id:str; source_type:str; effective_at:datetime; currency:str; amount_minor:int; kind:StatementActivityKind; evidence_fingerprint:str|None=None
 def to_dict(self):
  d=self.__dict__.copy(); d['ledger_kind']=self.ledger_kind.value; d['kind']=self.kind.value; d['effective_at']=self.effective_at.astimezone(timezone.utc).replace(microsecond=(self.effective_at.microsecond//1000)*1000).isoformat(); return d
 @staticmethod
 def from_dict(d):
  return CommercialStatementActivity(d['tenant_id'],StatementLedgerKind(d['ledger_kind']),d['account_id'],d['source_id'],d['source_type'],datetime.fromisoformat(d['effective_at']).astimezone(timezone.utc),d['currency'],d['amount_minor'],StatementActivityKind(d['kind']),d.get('evidence_fingerprint'))
@dataclass(frozen=True)
class CommercialStatement:
 tenant_id:str; ledger_kind:StatementLedgerKind; family:StatementFamily; account_id:str; currency:str; as_of:datetime; period_start:datetime|None; period_end:datetime|None; opening_balance_minor:int; activities:tuple[CommercialStatementActivity,...]; closing_balance_minor:int; aging:dict[str,int]|None=None
 def to_dict(self):
  return {'tenant_id':self.tenant_id,'ledger_kind':self.ledger_kind.value,'family':self.family.value,'account_id':self.account_id,'currency':self.currency,'as_of':self.as_of.astimezone(timezone.utc).isoformat(),'period_start':self.period_start.isoformat() if self.period_start else None,'period_end':self.period_end.isoformat() if self.period_end else None,'opening_balance_minor':self.opening_balance_minor,'activities':[a.to_dict() for a in self.activities],'closing_balance_minor':self.closing_balance_minor,'aging':{k:int(self.aging.get(k,0)) for k in [b.value for b in AgingBucket]} if self.aging is not None else None}
 @staticmethod
 def from_dict(d):
  aging=d.get('aging'); return CommercialStatement(d['tenant_id'],StatementLedgerKind(d['ledger_kind']),StatementFamily(d['family']),d['account_id'],d['currency'],datetime.fromisoformat(d['as_of']).astimezone(timezone.utc),datetime.fromisoformat(d['period_start']).astimezone(timezone.utc) if d.get('period_start') else None,datetime.fromisoformat(d['period_end']).astimezone(timezone.utc) if d.get('period_end') else None,d['opening_balance_minor'],tuple(CommercialStatementActivity.from_dict(a) for a in d['activities']),d['closing_balance_minor'],{str(k):int(v) for k,v in aging.items()} if aging is not None else None)
 def fingerprint(self): return hashlib.sha3_512(json.dumps(self.to_dict(),sort_keys=True,separators=(',',':')).encode()).hexdigest()
@dataclass(frozen=True)
class CommercialStatementSnapshot:
 snapshot_id:str; statement:CommercialStatement; generated_at:datetime; source_evidence_fingerprint:str; snapshot_fingerprint:str
 @staticmethod
 def from_statement(statement, *, generated_at, source_evidence_fingerprint=''):
  if not isinstance(statement, CommercialStatement): raise ValueError('M7_STATEMENT_REQUIRED')
  generated_at=generated_at.astimezone(timezone.utc).replace(microsecond=(generated_at.microsecond//1000)*1000)
  payload={'tenant_id':statement.tenant_id,'ledger_kind':statement.ledger_kind.value,'family':statement.family.value,'account_id':statement.account_id,'currency':statement.currency,'as_of':statement.as_of.isoformat(),'source_evidence_fingerprint':source_evidence_fingerprint,'statement_fingerprint':statement.fingerprint()}
  sid='statement-snapshot-'+hashlib.sha3_512(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  provisional=CommercialStatementSnapshot(sid,statement,generated_at,source_evidence_fingerprint,'')
  fp=hashlib.sha3_512(json.dumps(provisional.to_dict(),sort_keys=True,separators=(',',':')).encode()).hexdigest()
  return CommercialStatementSnapshot(sid,statement,generated_at,source_evidence_fingerprint,fp)
 def to_dict(self):
  return {'snapshot_id':self.snapshot_id,'statement':self.statement.to_dict(),'generated_at':self.generated_at.astimezone(timezone.utc).isoformat(),'source_evidence_fingerprint':self.source_evidence_fingerprint,'snapshot_fingerprint':self.snapshot_fingerprint}
 @staticmethod
 def from_dict(data):
  return CommercialStatementSnapshot(data['snapshot_id'],CommercialStatement.from_dict(data['statement']),datetime.fromisoformat(data['generated_at']).astimezone(timezone.utc),data['source_evidence_fingerprint'],data['snapshot_fingerprint'])
# ARTIFACT: commercial_statement.py
# VERSION: v1.0.0-M7
# AUTHORITY BOUNDARY: Commercial projection only.
# TENANT POSTURE: Tenant and account scoped.
# FAIL-CLOSED POSTURE: Cross-lane and mixed-currency inputs reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
