"""TITLE: Platform Billing Financial Execution Truth Registry
VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
AUTHORITY: Kennel EOS / Wilsy OS Core Governance
EPITOME: Durable tenant-scoped platform execution evidence.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/registry/platform_billing_financial_execution_truth_registry.py
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError
from ..domain.platform_billing_financial_execution_truth import PlatformBillingFinancialExecutionTruth, PlatformBillingFinancialExecutionTruthError, PlatformExecutionStatus

class PlatformBillingFinancialExecutionTruthNotFoundError(RuntimeError): pass
class PlatformBillingFinancialExecutionTruthPersistedRecordInvalidError(RuntimeError): pass
class PlatformBillingFinancialExecutionTruthConflictError(RuntimeError): pass

def _hydrate(doc: dict) -> PlatformBillingFinancialExecutionTruth:
    try:
        d={k:v for k,v in doc.items() if k!='_id'}
        if isinstance(d.get('execution_status'),str): d['execution_status']=PlatformExecutionStatus(d['execution_status'])
        for k in ('executed_at','created_at'):
            if isinstance(d.get(k),str): d[k]=datetime.fromisoformat(d[k])
        return PlatformBillingFinancialExecutionTruth(**d)
    except (TypeError,ValueError,PlatformBillingFinancialExecutionTruthError) as e: raise PlatformBillingFinancialExecutionTruthPersistedRecordInvalidError('PLATFORM_EXECUTION_TRUTH_PERSISTED_RECORD_INVALID') from e

class PlatformBillingFinancialExecutionTruthRegistry:
    @staticmethod
    def ensure_indexes(collection: Collection)->None:
        collection.create_index([('tenant_id',1),('execution_truth_id',1)],unique=True)
        collection.create_index([('tenant_id',1),('execution_request_id',1)],unique=True)
    @staticmethod
    def create(value: PlatformBillingFinancialExecutionTruth, collection: Collection, *, session: Optional[ClientSession]=None)->PlatformBillingFinancialExecutionTruth:
        document={'execution_truth_id':f'platform-truth-{value.execution_request_id}',**value.to_dict()}
        try: collection.insert_one(document,session=session); return value
        except DuplicateKeyError as e:
            existing=collection.find_one({'tenant_id':value.tenant_id,'execution_request_id':value.execution_request_id},session=session)
            if existing is not None and _hydrate(existing)==value:return _hydrate(existing)
            raise PlatformBillingFinancialExecutionTruthConflictError('PLATFORM_EXECUTION_TRUTH_CREATE_CONFLICT') from e
    @staticmethod
    def get(tenant_id:str, execution_truth_id:str, collection:Collection, *, session:Optional[ClientSession]=None)->PlatformBillingFinancialExecutionTruth:
        doc=collection.find_one({'tenant_id':tenant_id,'execution_truth_id':execution_truth_id},session=session)
        if doc is None: raise PlatformBillingFinancialExecutionTruthNotFoundError('PLATFORM_EXECUTION_TRUTH_NOT_FOUND')
        return _hydrate(doc)

# ARTIFACT: platform_billing_financial_execution_truth_registry.py
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY BOUNDARY: Persistence only; no settlement or commercial projection.
# END OF WILSY OS SOVEREIGN ARTIFACT
# WILSY OS SOVEREIGN ARTIFACT STRUCTURE
# TITLE: R3F0 Platform Billing Financial Execution Truth and Settlement Evidence
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY: Wilsy OS Core Governance / Kennel EOS
# PURPOSE: Durable, tenant-scoped platform execution and settlement evidence.
# EPITOME: Canonical platform financial truth without provider execution or money movement.
# ABSOLUTE CANONICAL PATH: tools/eos/kennel/registry/platform_billing_financial_execution_truth_registry.py
# COLLABORATION / OWNERSHIP: Kennel EOS platform financial domain; R3F0 certificates.
# CERTIFICATION / UPDATE DATE: 2026-09-06; structural remediation.
# CHANGELOG: v1.1.0-R3F0-STRUCTURAL-REMEDIATION complete sovereign metadata alignment.
# COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
# SECURITY / PRIVACY POSTURE: Tenant isolation; UUID synthetic tests; no raw secrets.
# TENANT BOUNDARY: Every read, write, replay, and certificate assertion is tenant-scoped.
# AUTHORITY BOUNDARY: Kennel EOS is exclusive financial execution authority.
# FINANCIAL AUTHORITY BOUNDARY: Evidence only; no provider call, settlement inference, or paid state.
# TRANSACTION BOUNDARY: Caller-owned Mongo session propagates through durable operations.
# FAIL-CLOSED DECLARATION: Invalid authority, provenance, persistence, or hydration fails closed.
# BEGIN SOVEREIGN HEADER SEAL
# END SOVEREIGN HEADER SEAL

# ARTIFACT: tools/eos/kennel/registry/platform_billing_financial_execution_truth_registry.py
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY BOUNDARY: Certification evidence only.
# TENANT POSTURE: Tenant-scoped synthetic fixtures.
# FAIL-CLOSED POSTURE: Failures are surfaced; no skips.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
