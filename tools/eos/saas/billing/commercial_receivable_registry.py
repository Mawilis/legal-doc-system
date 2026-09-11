"""WILSY OS M11B durable CommercialReceivable registry.
TITLE: Commercial Receivable Registry
VERSION: v1.0.0-M11B
AUTHORITY: Wilsy OS Core Governance
EPITOME: Tenant/family-scoped durable replay and strict persistence hydration.
ABSOLUTE CANONICAL PATH: tools/eos/saas/billing/commercial_receivable_registry.py
COLLABORATION / OWNERSHIP: SaaS persistence infrastructure owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11B establishes durable receivable replay boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Explicit collection; no hidden client or credentials.
TENANT BOUNDARY: Every replay identity binds tenant and family.
AUTHORITY BOUNDARY: Persistence only; domain owns commercial truth.
FINANCIAL AUTHORITY BOUNDARY: No execution, settlement, payment, or dunning.
TRANSACTION BOUNDARY: Caller owns session and transaction lifecycle.
FAIL-CLOSED DECLARATION: Corruption and divergent replay reject deterministically.
"""
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError
from tools.eos.saas.domain.commercial_receivable import CommercialReceivable, CommercialReceivableError

class CommercialReceivableRegistryError(RuntimeError):
    """Raised for missing, corrupt, or conflicting durable receivables."""

class CommercialReceivableRegistry:
    """Persist and hydrate immutable receivables without owning transactions."""
    @staticmethod
    def ensure_indexes(collection):
        collection.create_index([('tenant_id', ASCENDING), ('receivable_family', ASCENDING), ('source_invoice_id', ASCENDING)], unique=True)
    @staticmethod
    def _hydrate(document):
        payload = dict(document); payload.pop('_id', None)
        try: return CommercialReceivable.from_dict(payload)
        except Exception as error: raise CommercialReceivableRegistryError('M11B_RECEIVABLE_CORRUPT') from error
    @staticmethod
    def get(tenant_id, family, source_invoice_id, collection, *, session=None):
        document = collection.find_one({'tenant_id': tenant_id, 'receivable_family': family.value, 'source_invoice_id': source_invoice_id}, session=session)
        if document is None: raise CommercialReceivableRegistryError('M11B_RECEIVABLE_NOT_FOUND')
        return CommercialReceivableRegistry._hydrate(document)
    @staticmethod
    def create(value, collection, *, session=None):
        if not isinstance(value, CommercialReceivable): raise CommercialReceivableRegistryError('M11B_RECEIVABLE_INVALID')
        query={'tenant_id':value.tenant_id,'receivable_family':value.receivable_family.value,'source_invoice_id':value.source_invoice_id}
        existing=collection.find_one(query, session=session)
        if existing is not None:
            current=CommercialReceivableRegistry._hydrate(existing)
            if current != value: raise CommercialReceivableRegistryError('M11B_RECEIVABLE_REPLAY_CONFLICT')
            return current
        try: collection.insert_one(value.to_dict(), session=session)
        except DuplicateKeyError as error: raise CommercialReceivableRegistryError('M11B_RECEIVABLE_REPLAY_CONFLICT') from error
        return value

# ARTIFACT: commercial_receivable_registry.py
# VERSION: v1.0.0-M11B
# AUTHORITY BOUNDARY: Persistence only; no commercial truth inference.
# TENANT POSTURE: Tenant/family/source scoped replay.
# FAIL-CLOSED POSTURE: Corruption and divergent replay reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
