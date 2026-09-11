"""WILSY OS M11D2 persistence-only registry.
TITLE: AR1 Commercial Receivable Closure Registry
VERSION: v1.1.0-M11D2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Durable tenant-scoped immutable closure persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/platform_billing_commercial_receivable_closure_projection_registry.py
COLLABORATION / OWNERSHIP: SaaS Billing AR1 registry owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-AR1 establishes explicit collection registry.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Explicit collection/session only.
TENANT BOUNDARY: Every lookup includes tenant_id.
AUTHORITY BOUNDARY: Persistence only.
FINANCIAL AUTHORITY BOUNDARY: No execution or settlement.
TRANSACTION BOUNDARY: Caller-owned session.
FAIL-CLOSED DECLARATION: Corruption and conflicts fail closed.
"""
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from ..domain.platform_billing_commercial_receivable_closure_projection import PlatformBillingCommercialReceivableClosureProjection as P
class PlatformBillingCommercialReceivableClosureProjectionError(RuntimeError): pass
class PlatformBillingCommercialReceivableClosureProjectionRegistry:
 @staticmethod
 def ensure_indexes(c): c.create_index([('tenant_id',1),('commercial_receivable_closure_projection_id',1)],unique=True); c.create_index([('tenant_id',1),('platform_invoice_id',1)],unique=True)
 @staticmethod
 def create(v,c,*,session=None):
  try: c.insert_one(v.to_dict(),session=session); return v
  except DuplicateKeyError as e:
   d=c.find_one({'tenant_id':v.tenant_id,'commercial_receivable_closure_projection_id':v.commercial_receivable_closure_projection_id},session=session)
   if d and d.get('projection_fingerprint')==v.projection_fingerprint:return PlatformBillingCommercialReceivableClosureProjectionRegistry._hydrate(d)
   raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_PROJECTION_CONFLICT') from e
 @staticmethod
 def get(t,i,c,*,session=None):
  d=c.find_one({'tenant_id':t,'commercial_receivable_closure_projection_id':i},session=session)
  if d is None: raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_PROJECTION_NOT_FOUND')
  return PlatformBillingCommercialReceivableClosureProjectionRegistry._hydrate(d)
 @staticmethod
 def _hydrate(d):
  try:
   x=dict(d); x.pop('_id',None); return P.from_dict(x)
  except Exception as e: raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_PROJECTION_INVALID') from e
# ARTIFACT: platform_billing_commercial_receivable_closure_projection_registry.py
# VERSION: v1.1.0-M11D2
# AUTHORITY BOUNDARY: Persistence only.
# TENANT POSTURE: Tenant/PLATFORM scoped persistence.
# FAIL-CLOSED POSTURE: Corruption and conflicts reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
