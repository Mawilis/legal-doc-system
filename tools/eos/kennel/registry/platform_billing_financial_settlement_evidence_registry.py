"""TITLE: Platform Billing Financial Settlement Evidence Registry
VERSION: v1.1.1-R3F0-IDEMPOTENT-REPLAY
AUTHORITY: Kennel EOS / Wilsy OS Core Governance
EPITOME: Tenant-scoped immutable settlement evidence persistence.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/registry/platform_billing_financial_settlement_evidence_registry.py
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError
from ..domain.platform_billing_financial_settlement_evidence import PlatformBillingFinancialSettlementEvidence,PlatformBillingFinancialSettlementEvidenceError
class PlatformBillingFinancialSettlementEvidenceNotFoundError(RuntimeError): pass
class PlatformBillingFinancialSettlementEvidencePersistedRecordInvalidError(RuntimeError): pass
class PlatformBillingFinancialSettlementEvidenceConflictError(RuntimeError): pass
def _hydrate(d):
 try:
  x={k:v for k,v in d.items() if k!='_id'}
  for k in ('settled_at','created_at'):
   if isinstance(x.get(k),str): x[k]=datetime.fromisoformat(x[k])
  return PlatformBillingFinancialSettlementEvidence(**x)
 except (TypeError,ValueError,PlatformBillingFinancialSettlementEvidenceError) as e: raise PlatformBillingFinancialSettlementEvidencePersistedRecordInvalidError('PLATFORM_SETTLEMENT_EVIDENCE_PERSISTED_RECORD_INVALID') from e
class PlatformBillingFinancialSettlementEvidenceRegistry:
 @staticmethod
 def ensure_indexes(collection:Collection): collection.create_index([('tenant_id',1),('settlement_evidence_id',1)],unique=True); collection.create_index([('tenant_id',1),('platform_execution_truth_id',1)],unique=True)
 @staticmethod
 def create(value,collection:Collection,*,session:Optional[ClientSession]=None):
  d=collection.find_one({'tenant_id':value.tenant_id,'platform_execution_truth_id':value.platform_execution_truth_id},session=session)
  if d is not None:
   hydrated=_hydrate(d)
   if hydrated==value:return hydrated
   raise PlatformBillingFinancialSettlementEvidenceConflictError('PLATFORM_SETTLEMENT_EVIDENCE_CREATE_CONFLICT')
  try:
   collection.insert_one(value.to_dict(),session=session); return value
  except DuplicateKeyError as e:
   raise PlatformBillingFinancialSettlementEvidenceConflictError('PLATFORM_SETTLEMENT_EVIDENCE_CREATE_CONFLICT') from e
 @staticmethod
 def get(tenant_id:str,settlement_evidence_id:str,collection:Collection,*,session:Optional[ClientSession]=None):
  d=collection.find_one({'tenant_id':tenant_id,'settlement_evidence_id':settlement_evidence_id},session=session)
  if d is None: raise PlatformBillingFinancialSettlementEvidenceNotFoundError('PLATFORM_SETTLEMENT_EVIDENCE_NOT_FOUND')
  return _hydrate(d)
# ARTIFACT: platform_billing_financial_settlement_evidence_registry.py
# VERSION: v1.1.1-R3F0-IDEMPOTENT-REPLAY
# AUTHORITY BOUNDARY: Persistence only; no paid state.
# END OF WILSY OS SOVEREIGN ARTIFACT
# WILSY OS SOVEREIGN ARTIFACT STRUCTURE
# TITLE: R3F0 Platform Billing Financial Execution Truth and Settlement Evidence
# VERSION: v1.1.1-R3F0-IDEMPOTENT-REPLAY
# AUTHORITY: Wilsy OS Core Governance / Kennel EOS
# PURPOSE: Durable, tenant-scoped platform execution and settlement evidence.
# EPITOME: Canonical platform financial truth without provider execution or money movement.
# ABSOLUTE CANONICAL PATH: tools/eos/kennel/registry/platform_billing_financial_settlement_evidence_registry.py
# COLLABORATION / OWNERSHIP: Kennel EOS platform financial domain; R3F0 certificates.
# CERTIFICATION / UPDATE DATE: 2026-09-11; idempotent replay repair.
# CHANGELOG: v1.1.1-R3F0-IDEMPOTENT-REPLAY preflights durable replay before insert and fails closed on duplicate races.
# COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
# SECURITY / PRIVACY POSTURE: Tenant isolation; UUID synthetic tests; no raw secrets.
# TENANT BOUNDARY: Every read, write, replay, and certificate assertion is tenant-scoped.
# AUTHORITY BOUNDARY: Kennel EOS is exclusive financial execution authority.
# FINANCIAL AUTHORITY BOUNDARY: Evidence only; no provider call, settlement inference, or paid state.
# TRANSACTION BOUNDARY: Caller-owned Mongo session propagates through durable operations.
# FAIL-CLOSED DECLARATION: Invalid authority, provenance, persistence, or hydration fails closed.
# BEGIN SOVEREIGN HEADER SEAL
# END SOVEREIGN HEADER SEAL

# ARTIFACT: tools/eos/kennel/registry/platform_billing_financial_settlement_evidence_registry.py
# VERSION: v1.1.1-R3F0-IDEMPOTENT-REPLAY
# AUTHORITY BOUNDARY: Certification evidence only.
# TENANT POSTURE: Tenant-scoped synthetic fixtures.
# FAIL-CLOSED POSTURE: Failures are surfaced; no skips.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
