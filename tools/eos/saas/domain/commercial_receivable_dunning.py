"""WILSY OS M11C deterministic commercial dunning workflow projection.
TITLE: Commercial Receivable Dunning
VERSION: v1.0.0-M11C
AUTHORITY: Wilsy OS Core Governance
EPITOME: Non-executing collection-workflow truth derived from aging evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/commercial_receivable_dunning.py
COLLABORATION / OWNERSHIP: M11C Python dunning owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11C establishes deterministic eligible/reminder/escalated workflow.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No outbound message or provider data.
TENANT BOUNDARY: Aging tenant/family identity is preserved.
AUTHORITY BOUNDARY: Commercial workflow projection only.
FINANCIAL AUTHORITY BOUNDARY: No payment, execution, settlement, or balance mutation.
TRANSACTION BOUNDARY: Pure value object; no persistence lifecycle.
FAIL-CLOSED DECLARATION: Invalid aging provenance and workflow state reject.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib, json
from .commercial_receivable_aging import CommercialReceivableAging
class DunningStage(str,Enum): NONE='NONE'; ELIGIBLE='ELIGIBLE'; REMINDER='REMINDER'; ESCALATED='ESCALATED'
@dataclass(frozen=True,slots=True)
class CommercialReceivableDunning:
 tenant_id:str; receivable_family:str; receivable_id:str; aging_fingerprint:str; outstanding_amount_minor:int; stage:DunningStage; effective_at:datetime
 def __post_init__(self):
  if self.effective_at.tzinfo is None or self.outstanding_amount_minor<0 or not isinstance(self.stage,DunningStage): raise ValueError('M11C_INVALID_DUNNING')
 @property
 def dunning_fingerprint(self): return hashlib.sha3_512(json.dumps(self.to_dict(False),sort_keys=True,separators=(',',':')).encode()).hexdigest()
 def to_dict(self,include_fingerprint=True):
  d={'tenant_id':self.tenant_id,'receivable_family':self.receivable_family,'receivable_id':self.receivable_id,'aging_fingerprint':self.aging_fingerprint,'outstanding_amount_minor':self.outstanding_amount_minor,'stage':self.stage.value,'effective_at':self.effective_at.astimezone(timezone.utc).isoformat()}
  if include_fingerprint:d['dunning_fingerprint']=self.dunning_fingerprint
  return d
 @classmethod
 def from_aging(cls,aging,effective_at,stage=None):
  chosen=stage or (DunningStage.ELIGIBLE if aging.outstanding_amount_minor>0 and aging.overdue_days>0 else DunningStage.NONE)
  return cls(aging.tenant_id,aging.receivable_family.value,aging.receivable_id,aging.aging_fingerprint,aging.outstanding_amount_minor,chosen,effective_at)
# ARTIFACT: commercial_receivable_dunning.py
# VERSION: v1.0.0-M11C
# AUTHORITY BOUNDARY: Commercial workflow only.
# TENANT POSTURE: Aging tenant/family preserved.
# FAIL-CLOSED POSTURE: Invalid workflow evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
