"""TITLE: Platform Billing Financial Execution Truth Registry
VERSION: v1.2.0-M11-P5-R2E-R4-R3
AUTHORITY: Kennel EOS / Wilsy OS Core Governance
EPITOME: Durable tenant-scoped platform execution evidence.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/registry/platform_billing_financial_execution_truth_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS platform financial execution-evidence persistence owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.2.0-M11-P5-R2E-R4-R3 adds canonical pre-insert exact replay and caller-owned active-transaction duplicate-race propagation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Strict BSON hydration; opaque synthetic references only.
TENANT BOUNDARY: Every lookup and conflict query includes tenant_id.
AUTHORITY BOUNDARY: Persistence of canonical Platform execution evidence only.
FINANCIAL AUTHORITY BOUNDARY: No provider selection, settlement, paid state, or receivable closure.
TRANSACTION BOUNDARY: Caller-owned Mongo sessions propagate unchanged; no transaction lifecycle ownership.
FAIL-CLOSED DECLARATION: Unknown, missing, corrupt, divergent, and duplicate-race records reject.
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

def _transaction_is_active(session: Optional[ClientSession]) -> bool:
    """Read transaction state only from the caller-owned ClientSession."""
    return session is not None and session.in_transaction

class PlatformBillingFinancialExecutionTruthRegistry:
    @staticmethod
    def ensure_indexes(collection: Collection)->None:
        collection.create_index([('tenant_id',1),('execution_truth_id',1)],unique=True)
        collection.create_index([('tenant_id',1),('execution_request_id',1)],unique=True)
    @staticmethod
    def create(value: PlatformBillingFinancialExecutionTruth, collection: Collection, *, session: Optional[ClientSession]=None)->PlatformBillingFinancialExecutionTruth:
        document={'execution_truth_id':f'platform-truth-{value.execution_request_id}',**value.to_dict()}
        try:
            existing = PlatformBillingFinancialExecutionTruthRegistry.get(
                value.tenant_id, value.execution_truth_id, collection, session=session
            )
        except PlatformBillingFinancialExecutionTruthNotFoundError:
            existing = None
        if existing is not None:
            if existing == value and existing.fingerprint == value.fingerprint:
                return existing
            raise PlatformBillingFinancialExecutionTruthConflictError('PLATFORM_EXECUTION_TRUTH_CREATE_CONFLICT')
        try: collection.insert_one(document,session=session); return value
        except DuplicateKeyError as e:
            if _transaction_is_active(session):
                raise PlatformBillingFinancialExecutionTruthConflictError('PLATFORM_EXECUTION_TRUTH_CREATE_CONFLICT') from e
            existing=collection.find_one({'tenant_id':value.tenant_id,'execution_request_id':value.execution_request_id},session=session)
            if existing is not None:
                durable = _hydrate(existing)
                if durable == value and durable.fingerprint == value.fingerprint:return durable
            raise PlatformBillingFinancialExecutionTruthConflictError('PLATFORM_EXECUTION_TRUTH_CREATE_CONFLICT') from e
    @staticmethod
    def get(tenant_id:str, execution_truth_id:str, collection:Collection, *, session:Optional[ClientSession]=None)->PlatformBillingFinancialExecutionTruth:
        doc=collection.find_one({'tenant_id':tenant_id,'execution_truth_id':execution_truth_id},session=session)
        if doc is None: raise PlatformBillingFinancialExecutionTruthNotFoundError('PLATFORM_EXECUTION_TRUTH_NOT_FOUND')
        return _hydrate(doc)

# ARTIFACT: platform_billing_financial_execution_truth_registry.py
# VERSION: v1.2.0-M11-P5-R2E-R4-R3
# AUTHORITY BOUNDARY: Caller-session persistence of canonical Platform execution evidence only.
# TENANT POSTURE: Every lookup, replay, and conflict is tenant-scoped.
# FAIL-CLOSED POSTURE: Corrupt, divergent, and active-transaction duplicate races reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no settlement or paid-state authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
