"""WILSY OS R3F-B atomic commercial settlement projection.
TITLE: Platform Billing Commercial Settlement Projection Orchestration
VERSION: v1.1.0-R3F-B
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Project canonical Kennel settlement evidence into PlatformInvoice state.
EPITOME: Explicit collections, provenance gates, CAS invoice mutation.
ABSOLUTE CANONICAL PATH: tools/eos/saas/billing/platform_billing_commercial_settlement_projection.py
COLLABORATION / OWNERSHIP: SaaS Billing commercial projection owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-R3F-B adds atomic projection orchestration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped explicit collection graph.
TENANT BOUNDARY: All reads and writes bind tenant_id.
AUTHORITY BOUNDARY: Durable Kennel settlement evidence only.
FINANCIAL AUTHORITY BOUNDARY: No provider execution or money movement.
TRANSACTION BOUNDARY: Caller-owned session required for atomic writes.
FAIL-CLOSED DECLARATION: Any provenance or CAS mismatch aborts.
"""
from datetime import datetime, timezone
from pymongo.collection import Collection
from ..domain.billing import PlatformInvoice, InvoiceStatus
from ..domain.platform_billing_commercial_settlement_projection import PlatformBillingCommercialSettlementProjection
from .platform_billing_commercial_settlement_projection_registry import PlatformBillingCommercialSettlementProjectionRegistry, PlatformBillingCommercialSettlementProjectionNotFoundError
from .platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry
from tools.eos.kennel.registry.platform_billing_financial_settlement_evidence_registry import PlatformBillingFinancialSettlementEvidenceRegistry

class PlatformBillingCommercialSettlementProjectionError(RuntimeError): pass

def _canonical_utc_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.replace(microsecond=(value.microsecond // 1000) * 1000)

def _mongo_timestamp(value: datetime) -> datetime:
    """Return UTC-aware millisecond precision suitable for BSON persistence."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise PlatformBillingCommercialSettlementProjectionError('R3F_TIMESTAMP_INVALID')
    value = value.astimezone(timezone.utc)
    return value.replace(microsecond=(value.microsecond // 1000) * 1000)

def project_platform_billing_commercial_settlement(tenant_id:str,settlement_evidence_id:str,*,settlement_collection:Collection,release_authorization_collection:Collection,platform_invoice_collection:Collection,commercial_projection_collection:Collection,session=None,projected_at:datetime|None=None):
    if session is None or not getattr(session, 'in_transaction', False): raise PlatformBillingCommercialSettlementProjectionError('R3F_SESSION_REQUIRED')
    settlement=PlatformBillingFinancialSettlementEvidenceRegistry.get(tenant_id,settlement_evidence_id,settlement_collection,session=session)
    authorization=PlatformBillingReleaseAuthorizationRegistry.get(tenant_id,settlement.release_authorization_id,release_authorization_collection,session=session)
    doc=platform_invoice_collection.find_one({'tenant_id':tenant_id,'invoice_id':settlement.platform_invoice_id},session=session)
    if doc is None: raise PlatformBillingCommercialSettlementProjectionError('R3F_INVOICE_NOT_FOUND')
    hydrated_doc = dict(doc)
    hydrated_doc['paid_at'] = _canonical_utc_datetime(hydrated_doc.get('paid_at'))
    invoice=PlatformInvoice.from_dict(hydrated_doc)
    if not (settlement.tenant_id==authorization.tenant_id==invoice.tenant_id==tenant_id and settlement.platform_invoice_id==authorization.platform_invoice_id==invoice.invoice_id and settlement.currency==authorization.currency==invoice.currency and settlement.settled_amount_minor==authorization.authorized_amount_minor==invoice.release_amount_minor and authorization.platform_invoice_evidence_fingerprint==invoice.commercial_release_evidence_fingerprint): raise PlatformBillingCommercialSettlementProjectionError('R3F_PROVENANCE_MISMATCH')
    projection_id = f'platform-commercial-settlement-{settlement_evidence_id}'
    try:
        existing = PlatformBillingCommercialSettlementProjectionRegistry.get(tenant_id, projection_id, commercial_projection_collection, session=session)
    except PlatformBillingCommercialSettlementProjectionNotFoundError:
        existing = None
    now = _mongo_timestamp(existing.projected_at if existing is not None else (projected_at or datetime.now(timezone.utc)))
    projection=PlatformBillingCommercialSettlementProjection(tenant_id,projection_id,settlement_evidence_id,settlement.fingerprint,settlement.platform_execution_truth_id,settlement.execution_request_id,settlement.execution_command_id,authorization.release_authorization_id,authorization.release_authorization_fingerprint,invoice.invoice_id,authorization.platform_invoice_evidence_fingerprint,settlement.settled_amount_minor,settlement.currency,settlement.settled_at,now,'PAID',settlement.settled_amount_minor,0)
    if existing is not None:
        if existing.to_dict(include_fingerprint=False) != projection.to_dict(include_fingerprint=False): raise PlatformBillingCommercialSettlementProjectionError('R3F_REPLAY_PROJECTION_MISMATCH')
        canonical_invoice_paid_at = _canonical_utc_datetime(invoice.paid_at)
        canonical_settlement_settled_at = _canonical_utc_datetime(settlement.settled_at)
        if invoice.status is not InvoiceStatus.PAID or canonical_invoice_paid_at != canonical_settlement_settled_at or invoice.amount_paid != invoice.total or invoice.outstanding_amount != 0: raise PlatformBillingCommercialSettlementProjectionError('R3F_REPLAY_INVOICE_MISMATCH')
        return existing
    if invoice.status is InvoiceStatus.PAID or invoice.paid_at is not None or invoice.amount_paid>0: raise PlatformBillingCommercialSettlementProjectionError('R3F_ARBITRARY_PAID_STATE')
    PlatformBillingCommercialSettlementProjectionRegistry.create(projection,commercial_projection_collection,session=session)
    cas={'tenant_id':tenant_id,'invoice_id':invoice.invoice_id,'status':{'$ne':'PAID'},'amount_paid':invoice.amount_paid,'outstanding_amount':invoice.outstanding_amount,'paid_at':doc.get('paid_at')}
    for field in ('release_amount_minor','currency','amount','tax_amount','tax_type','line_items','issued_at','due_at','payment_terms_days','collection_method','billing_mode','seller_jurisdiction','customer_jurisdiction','subscription_id','plan_id','order_number','purchase_order'):
        if field in doc: cas[field]=doc[field]
    result=platform_invoice_collection.update_one(cas,{'$set':{'status':'PAID','amount_paid':invoice.total,'amountPaid':invoice.total,'outstanding_amount':0,'outstandingAmount':0,'paid_at':settlement.settled_at,'paidAt':settlement.settled_at}},session=session)
    if result.matched_count!=1: raise PlatformBillingCommercialSettlementProjectionError('R3F_INVOICE_CAS_FAILED')
    return projection

# ARTIFACT: platform_billing_commercial_settlement_projection.py
# VERSION: v1.1.0-R3F-B
# END OF WILSY OS SOVEREIGN ARTIFACT
