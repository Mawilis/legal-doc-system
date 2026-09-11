"""TITLE: Commercial Statement Snapshot Registry
VERSION: v1.0.0-M7
AUTHORITY: Wilsy OS Core Governance
EPITOME: Explicit tenant-scoped immutable statement snapshots.
ABSOLUTE CANONICAL PATH: tools/eos/saas/billing/commercial_statement_registry.py
COLLABORATION / OWNERSHIP: Python EOS SaaS Billing.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M7 establishes snapshot persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Explicit collection/session only.
TENANT BOUNDARY: Snapshot identity is tenant-scoped by caller.
AUTHORITY BOUNDARY: Persistence only.
FINANCIAL AUTHORITY BOUNDARY: No settlement or execution.
TRANSACTION BOUNDARY: Caller-owned session.
FAIL-CLOSED DECLARATION: Corruption and conflicts reject.
"""
from pymongo.errors import DuplicateKeyError
class CommercialStatementRegistryError(RuntimeError): pass
class CommercialStatementSnapshotRegistry:
 @staticmethod
 def ensure_indexes(c): c.create_index([('tenant_id',1),('snapshot_id',1)],unique=True)
 @staticmethod
 def create(snapshot,collection,*,session=None):
  existing_document = collection.find_one({'tenant_id': snapshot.statement.tenant_id, 'snapshot_id': snapshot.snapshot_id}, session=session)
  if existing_document is not None:
   existing = CommercialStatementSnapshotRegistry.get(snapshot.statement.tenant_id, snapshot.snapshot_id, collection, session=session)
   if existing.to_dict() == snapshot.to_dict(): return existing
   raise CommercialStatementRegistryError('M7_SNAPSHOT_CONFLICT')
  try:
   d=snapshot.to_dict(); d['tenant_id']=snapshot.statement.tenant_id; collection.insert_one(d,session=session); return CommercialStatementSnapshotRegistry.get(snapshot.statement.tenant_id,snapshot.snapshot_id,collection,session=session)
  except DuplicateKeyError:
   if session is not None and getattr(session, 'in_transaction', False):
    raise CommercialStatementRegistryError('M7_SNAPSHOT_RETRY_REQUIRED')
   existing=CommercialStatementSnapshotRegistry.get(snapshot.statement.tenant_id,snapshot.snapshot_id,collection,session=session)
   if existing.to_dict()==snapshot.to_dict(): return existing
   raise CommercialStatementRegistryError('M7_SNAPSHOT_CONFLICT')
 @staticmethod
 def get(tenant_id,snapshot_id,collection,*,session=None):
  d=collection.find_one({'tenant_id':tenant_id,'snapshot_id':snapshot_id},session=session)
  if d is None: raise CommercialStatementRegistryError('M7_SNAPSHOT_NOT_FOUND')
  from ..domain.commercial_statement import CommercialStatementSnapshot
  value=CommercialStatementSnapshot.from_dict(d)
  expected = CommercialStatementSnapshot.from_statement(value.statement, generated_at=value.generated_at, source_evidence_fingerprint=value.source_evidence_fingerprint)
  if expected.snapshot_id != value.snapshot_id or expected.snapshot_fingerprint != d.get('snapshot_fingerprint'): raise CommercialStatementRegistryError('M7_SNAPSHOT_CORRUPT')
  return value
# ARTIFACT: commercial_statement_registry.py
# VERSION: v1.0.0-M7
# END OF WILSY OS SOVEREIGN ARTIFACT
