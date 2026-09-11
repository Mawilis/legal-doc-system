"""WILSY OS M10B1 direction-aware Kennel execution domain.
TITLE: Financial Movement Execution
VERSION: v1.0.0-M10B1
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Define immutable COLLECTION/DISBURSEMENT execution intent and truth.
EPITOME: Kennel-owned provider execution evidence without settlement authority.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/domain/financial_movement_execution.py
COLLABORATION / OWNERSHIP: Kennel EOS financial execution owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M10B1 establishes direction-aware execution contracts.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references only; raw credentials rejected.
TENANT BOUNDARY: Every execution binds tenant and authority subject.
AUTHORITY BOUNDARY: Kennel execution only; no settlement or paid truth.
FINANCIAL AUTHORITY BOUNDARY: Execution is distinct from settlement.
TRANSACTION BOUNDARY: Caller owns sessions and transactions.
FAIL-CLOSED DECLARATION: Invalid direction, provenance, fingerprints, and replay reject.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib, json, re
from typing import Any
from .financial_execution import FinancialExecutionStatus
class FinancialMovementDirection(StrEnum): COLLECTION='COLLECTION'; DISBURSEMENT='DISBURSEMENT'
class FinancialMovementExecutionError(ValueError): pass
_HEX=r'[0-9a-f]{128}'; _SENSITIVE=re.compile(r'(card_number|pan|cvv|bank_account|account_number|branch_code|credentials|password|secret|api_key|access_token|refresh_token)',re.I)
def _fp(v:Any)->str: return hashlib.sha3_512(json.dumps(v,sort_keys=True,separators=(',',':'),default=lambda x:x.isoformat() if isinstance(x,datetime) else x.value if isinstance(x,StrEnum) else str(x)).encode()).hexdigest()
@dataclass(frozen=True)
class FinancialMovementExecutionCommand:
 tenant_id:str; execution_authorization_id:str; execution_authorization_fingerprint:str; authority_subject_kind:str; authority_subject_id:str; authority_subject_fingerprint:str; direction:FinancialMovementDirection; execution_command_id:str; idempotency_key:str; amount_minor:int; currency:str; payment_instrument_reference:str; requested_provider:str|None=None; provider_metadata_reference:str|None=None
 def __post_init__(self):
  if not all(isinstance(getattr(self,n),str) and getattr(self,n).strip() for n in ('tenant_id','execution_authorization_id','authority_subject_kind','authority_subject_id','execution_command_id','idempotency_key','payment_instrument_reference')) or _SENSITIVE.search(self.payment_instrument_reference): raise FinancialMovementExecutionError('M10B_COMMAND_IDENTITY_INVALID')
  if not isinstance(self.amount_minor,int) or isinstance(self.amount_minor,bool) or self.amount_minor<=0 or re.fullmatch(r'[A-Z]{3}',self.currency) is None: raise FinancialMovementExecutionError('M10B_COMMAND_MONEY_INVALID')
  if not isinstance(self.direction,FinancialMovementDirection) or re.fullmatch(_HEX,self.execution_authorization_fingerprint) is None or re.fullmatch(_HEX,self.authority_subject_fingerprint) is None: raise FinancialMovementExecutionError('M10B_COMMAND_PROVENANCE_INVALID')
 @property
 def fingerprint(self): return _fp(self.__dict__)
@dataclass(frozen=True)
class FinancialMovementExecutionTruth:
 execution_truth_id:str; tenant_id:str; execution_authorization_id:str; authority_subject_kind:str; authority_subject_id:str; direction:FinancialMovementDirection; provider:str; provider_execution_reference:str; execution_status:FinancialExecutionStatus; executed_amount_minor:int; currency:str; executed_at:datetime|None; payment_instrument_reference:str; provider_evidence_reference:str; execution_command_fingerprint:str; execution_evidence_fingerprint:str; created_at:datetime
 def __post_init__(self):
  if not isinstance(self.direction,FinancialMovementDirection) or not isinstance(self.execution_status,FinancialExecutionStatus) or not isinstance(self.executed_amount_minor,int) or isinstance(self.executed_amount_minor,bool) or self.executed_amount_minor<=0 or re.fullmatch(r'[A-Z]{3}',self.currency) is None or re.fullmatch(_HEX,self.execution_command_fingerprint) is None or re.fullmatch(_HEX,self.execution_evidence_fingerprint) is None: raise FinancialMovementExecutionError('M10B_TRUTH_INVALID')
 def to_dict(self): return {**self.__dict__,'direction':self.direction.value,'execution_status':self.execution_status.value,'executed_at':self.executed_at.isoformat() if self.executed_at else None,'created_at':self.created_at.isoformat()}
 @classmethod
 def from_dict(cls,d):
  x=dict(d); x['direction']=FinancialMovementDirection(x['direction']); x['execution_status']=FinancialExecutionStatus(x['execution_status']); x['executed_at']=datetime.fromisoformat(x['executed_at']) if x.get('executed_at') else None; x['created_at']=datetime.fromisoformat(x['created_at']); return cls(**x)
# ARTIFACT: financial_movement_execution.py
# VERSION: v1.0.0-M10B1
# AUTHORITY BOUNDARY: Kennel EOS execution evidence.
# FAIL-CLOSED POSTURE: Invalid command/truth rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
