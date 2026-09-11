"""WILSY OS M10B1 durable direction-aware execution registry.
TITLE: Financial Movement Execution Registry
VERSION: v1.1.0-M10B1
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Persist and replay Kennel direction-aware execution truth.
EPITOME: Tenant/direction scoped durable evidence with fail-closed corruption checks.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/registry/financial_movement_execution_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS registry owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.1.0-M10B1 normalizes Mongo metadata at the persistence boundary.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Explicit collection only.
TENANT BOUNDARY: Tenant and authority subject scope required.
AUTHORITY BOUNDARY: Persistence only.
FINANCIAL AUTHORITY BOUNDARY: No settlement or paid truth.
TRANSACTION BOUNDARY: Caller-owned session.
FAIL-CLOSED DECLARATION: Divergent replay and corruption reject.
"""
from pymongo import ASCENDING
from ..domain.financial_movement_execution import FinancialMovementExecutionTruth
class FinancialMovementExecutionRegistryError(RuntimeError): pass
class FinancialMovementExecutionRegistry:
 @staticmethod
 def _hydrate(document):
  payload=dict(document)
  payload.pop('_id', None)
  return FinancialMovementExecutionTruth.from_dict(payload)
 @staticmethod
 def ensure_indexes(c): c.create_index([('tenant_id',ASCENDING),('execution_authorization_id',ASCENDING),('direction',ASCENDING),('execution_truth_id',ASCENDING)],unique=True); c.create_index([('tenant_id',ASCENDING),('authority_subject_kind',ASCENDING),('authority_subject_id',ASCENDING),('direction',ASCENDING),('idempotency_key',ASCENDING)],unique=True)
 @staticmethod
 def get_by_idempotency_key(tenant_id,subject_kind,subject_id,direction,key,c,*,session=None):
  d=c.find_one({'tenant_id':tenant_id,'authority_subject_kind':subject_kind,'authority_subject_id':subject_id,'direction':direction.value,'idempotency_key':key},session=session)
  if d is None: return None
  d=dict(d)
  d.pop('idempotency_key', None)
  return FinancialMovementExecutionRegistry._hydrate(d)
 @staticmethod
 def create(truth, key, c, *, session=None):
  existing=FinancialMovementExecutionRegistry.get_by_idempotency_key(truth.tenant_id,truth.authority_subject_kind,truth.authority_subject_id,truth.direction,key,c,session=session)
  if existing is not None:
   if existing.to_dict()!=truth.to_dict(): raise FinancialMovementExecutionRegistryError('M10B_REPLAY_CONFLICT')
   return existing
  c.insert_one({**truth.to_dict(),'idempotency_key':key},session=session); return truth
# ARTIFACT: financial_movement_execution_registry.py
# VERSION: v1.1.0-M10B1
# AUTHORITY BOUNDARY: Kennel persistence only.
# FAIL-CLOSED POSTURE: Corruption and divergence reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
