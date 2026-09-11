"""WILSY OS R3F-A durable commercial settlement projection registry.
TITLE: Platform Billing Commercial Settlement Projection Registry
VERSION: v1.0.0-R3F-A
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Tenant-scoped immutable projection persistence.
EPITOME: Deterministic replay and conflict protection.
ABSOLUTE CANONICAL PATH: tools/eos/saas/billing/platform_billing_commercial_settlement_projection_registry.py
COLLABORATION / OWNERSHIP: SaaS Billing persistence owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-R3F-A establishes durable projection registry.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Explicit collections; no hidden clients.
TENANT BOUNDARY: Every key includes tenant_id.
AUTHORITY BOUNDARY: Consumes Kennel evidence only.
FINANCIAL AUTHORITY BOUNDARY: No execution or money movement.
TRANSACTION BOUNDARY: Caller session propagates.
FAIL-CLOSED DECLARATION: Corruption and conflicts fail closed.
"""
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from ..domain import platform_billing_commercial_settlement_projection as _m
class PlatformBillingCommercialSettlementProjectionNotFoundError(RuntimeError): pass
class PlatformBillingCommercialSettlementProjectionConflictError(RuntimeError): pass
class PlatformBillingCommercialSettlementProjectionPersistedRecordInvalidError(RuntimeError): pass
class PlatformBillingCommercialSettlementProjectionRegistry:
 @staticmethod
 def ensure_indexes(collection):
  collection.create_index([('tenant_id',1),('commercial_settlement_projection_id',1)],unique=True); collection.create_index([('tenant_id',1),('settlement_evidence_id',1)],unique=True)
 @staticmethod
 def create(value,collection,*,session=None):
  try: collection.insert_one(value.to_dict(),session=session); return value
  except DuplicateKeyError as e:
   d=collection.find_one({'tenant_id':value.tenant_id,'commercial_settlement_projection_id':value.commercial_settlement_projection_id},session=session)
   if d is not None and d.get('projection_fingerprint')==value.projection_fingerprint:return PlatformBillingCommercialSettlementProjectionRegistry._hydrate(d)
   raise PlatformBillingCommercialSettlementProjectionConflictError('R3F_PROJECTION_CONFLICT') from e
 @staticmethod
 def get(tenant_id,projection_id,collection,*,session=None):
  d=collection.find_one({'tenant_id':tenant_id,'commercial_settlement_projection_id':projection_id},session=session)
  if d is None: raise PlatformBillingCommercialSettlementProjectionNotFoundError('R3F_PROJECTION_NOT_FOUND')
  return PlatformBillingCommercialSettlementProjectionRegistry._hydrate(d)
 @staticmethod
 def _hydrate(d):
  try:
   x={k:v for k,v in d.items() if k not in ('_id','projection_fingerprint')}; x['settled_at']=datetime.fromisoformat(x['settled_at']) if isinstance(x['settled_at'],str) else x['settled_at']; x['projected_at']=datetime.fromisoformat(x['projected_at']) if isinstance(x['projected_at'],str) else x['projected_at']; return _m.PlatformBillingCommercialSettlementProjection(**x)
  except Exception as e: raise PlatformBillingCommercialSettlementProjectionPersistedRecordInvalidError('R3F_PROJECTION_INVALID') from e
# ARTIFACT: platform_billing_commercial_settlement_projection_registry.py
# VERSION: v1.0.0-R3F-A
# AUTHORITY BOUNDARY: Projection persistence only.
# FAIL-CLOSED POSTURE: Conflicts and corruption fail closed.
# END OF WILSY OS SOVEREIGN ARTIFACT
