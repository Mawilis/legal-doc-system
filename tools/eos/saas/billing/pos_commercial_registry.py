"""WILSY OS M9 durable POS sale registry.
TITLE: POS Commercial Registry
VERSION: v1.0.0-M9
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Persist and hydrate tenant/location-scoped M9 POS evidence with fail-closed replay and corruption behavior.
EPITOME: Tenant-scoped immutable sale persistence and replay.
ABSOLUTE CANONICAL PATH: tools/eos/saas/billing/pos_commercial_registry.py
COLLABORATION / OWNERSHIP: Python EOS POS registry owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M9 establishes explicit collection replay semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Explicit collection/session only.
TENANT BOUNDARY: All access binds tenant_id, location_id, sale_id.
AUTHORITY BOUNDARY: Persistence only.
FINANCIAL AUTHORITY BOUNDARY: No execution or settlement.
TRANSACTION BOUNDARY: Caller owns session and transaction.
FAIL-CLOSED DECLARATION: Divergent replay and corruption reject.
"""
from pymongo.errors import DuplicateKeyError
from ..domain.pos_commercial import POSLineItem, POSSale, POSStatus
class POSRegistryError(RuntimeError): pass
class POSSaleRegistry:
 @staticmethod
 def ensure_indexes(c): c.create_index([('tenant_id',1),('location_id',1),('sale_id',1)],unique=True); c.create_index([('tenant_id',1),('idempotency_key',1)],unique=True)
 @staticmethod
 def create(sale, collection, *, session=None):
  existing=collection.find_one({'tenant_id':sale.tenant_id,'location_id':sale.location_id,'sale_id':sale.sale_id},session=session)
  if existing is not None:
   if existing.get('fingerprint')==sale.fingerprint: return POSSaleRegistry.from_dict(existing)
   raise POSRegistryError('M9_SALE_REPLAY_CONFLICT')
  try: collection.insert_one(sale.to_dict(),session=session)
  except DuplicateKeyError: raise POSRegistryError('M9_SALE_RETRY_REQUIRED')
  return POSSaleRegistry.get(sale.tenant_id,sale.location_id,sale.sale_id,collection,session=session)
 @staticmethod
 def get(tenant_id, location_id, sale_id, collection, *, session=None):
  d=collection.find_one({'tenant_id':tenant_id,'location_id':location_id,'sale_id':sale_id},session=session)
  if d is None: raise POSRegistryError('M9_SALE_NOT_FOUND')
  if d.get('fingerprint') != POSSaleRegistry.from_dict(d).fingerprint: raise POSRegistryError('M9_SALE_CORRUPT')
  return POSSaleRegistry.from_dict(d)
 @staticmethod
 def from_dict(d):
  lines=tuple(POSLineItem(**x) for x in d['lines']); return POSSale(d['tenant_id'],d['location_id'],d['sale_id'],d['currency'],lines,POSStatus(d['status']),d['idempotency_key'])
# ARTIFACT: pos_commercial_registry.py
# VERSION: v1.0.0-M9
# AUTHORITY BOUNDARY: Persistence only.
# FAIL-CLOSED POSTURE: Replay conflicts reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
