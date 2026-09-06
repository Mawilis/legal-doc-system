"""WILSY OS M10 durable POS execution-authorization registry.

TITLE: POS Financial Execution Authorization Registry
VERSION: v1.0.0-M10
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Persist and replay tenant-scoped POS execution authorizations.
EPITOME: Explicit-collection durability with corruption and divergence rejection.
ABSOLUTE CANONICAL PATH: tools/eos/saas/billing/pos_financial_execution_authorization_registry.py
COLLABORATION / OWNERSHIP: Python EOS SaaS authorization persistence owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M10 establishes explicit collection replay and hydration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No hidden database/client; opaque evidence only.
TENANT BOUNDARY: Every lookup binds tenant and authorization identity.
AUTHORITY BOUNDARY: Persistence only; no authority is inferred.
FINANCIAL AUTHORITY BOUNDARY: Authorization is not execution or settlement.
TRANSACTION BOUNDARY: Caller owns session and transaction lifecycle.
FAIL-CLOSED DECLARATION: Divergent replay and corrupt fingerprints reject.
"""
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError
from tools.eos.saas.domain import pos_financial_execution_authorization as domain

class POSFinancialExecutionAuthorizationRegistryError(RuntimeError): pass
class POSFinancialExecutionAuthorizationRegistry:
 @staticmethod
 def ensure_indexes(collection):
  collection.create_index([('tenant_id',ASCENDING),('authorization_id',ASCENDING)],unique=True)
  collection.create_index([('tenant_id',ASCENDING),('direction',ASCENDING),('source_id',ASCENDING),('idempotency_key',ASCENDING)],unique=True)
 @staticmethod
 def get(tenant_id, authorization_id, collection, *, session=None):
  doc=collection.find_one({'tenant_id':tenant_id,'authorization_id':authorization_id},session=session)
  if doc is None: raise POSFinancialExecutionAuthorizationRegistryError('M10_AUTH_NOT_FOUND')
  try:
   payload=dict(doc)
   payload.pop('_id', None)
   return domain.POSFinancialExecutionAuthorization.from_dict(payload)
  except Exception as error: raise POSFinancialExecutionAuthorizationRegistryError('M10_AUTH_CORRUPT') from error
 @staticmethod
 def create(value, collection, *, session=None):
  if not isinstance(value,domain.POSFinancialExecutionAuthorization): raise POSFinancialExecutionAuthorizationRegistryError('M10_AUTH_INVALID')
  existing=collection.find_one({'tenant_id':value.tenant_id,'authorization_id':value.authorization_id},session=session)
  if existing is not None:
   current=POSFinancialExecutionAuthorizationRegistry.get(value.tenant_id,value.authorization_id,collection,session=session)
   if current.to_dict()!=value.to_dict(): raise POSFinancialExecutionAuthorizationRegistryError('M10_AUTH_REPLAY_CONFLICT')
   return current
  try: collection.insert_one(value.to_dict(),session=session)
  except DuplicateKeyError as error: raise POSFinancialExecutionAuthorizationRegistryError('M10_AUTH_REPLAY_CONFLICT') from error
  return value
# ARTIFACT: pos_financial_execution_authorization_registry.py
# VERSION: v1.0.0-M10
# AUTHORITY BOUNDARY: Persistence only; issuance owns policy.
# TENANT POSTURE: Tenant-scoped identity and replay.
# FAIL-CLOSED POSTURE: Corruption and divergent replay reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
