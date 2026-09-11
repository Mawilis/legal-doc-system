"""WILSY OS M9 POS commercial orchestration.
TITLE: POS Commercial Orchestration
VERSION: v1.0.0-M9
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Orchestrate M9 POS commercial operations while preserving the Kennel financial execution boundary.
EPITOME: Validated sale construction without electronic execution.
ABSOLUTE CANONICAL PATH: tools/eos/saas/billing/pos_commercial_orchestration.py
COLLABORATION / OWNERSHIP: Python EOS POS orchestration owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M9 establishes finalize-sale boundary.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No provider credentials or payment state.
TENANT BOUNDARY: Sale construction requires tenant/location identity.
AUTHORITY BOUNDARY: Commercial sale only.
FINANCIAL AUTHORITY BOUNDARY: Electronic execution belongs to Kennel EOS/M10.
TRANSACTION BOUNDARY: Caller supplies collection/session.
FAIL-CLOSED DECLARATION: Caller-paid and settled fields are rejected.
"""
from .pos_commercial_registry import POSSaleRegistry
from ..domain.pos_commercial import (POSSale, POSStatus, POSTenderIntent, POSTenderType, POSCashTender, POSReturnIntent, POSRefundIntent)
def finalize_sale(sale, collection, *, session=None):
 if sale.status not in (POSStatus.DRAFT, POSStatus.OPEN): raise ValueError('M9_SALE_FINALIZATION_INVALID')
 finalized=POSSale(sale.tenant_id,sale.location_id,sale.sale_id,sale.currency,sale.lines,POSStatus.COMPLETED_COMMERCIAL,sale.idempotency_key)
 return POSSaleRegistry.create(finalized,collection,session=session)

def create_tender_intent(sale: POSSale, tender_type: POSTenderType, requested_amount_minor: int, idempotency_key: str) -> POSTenderIntent:
 """Create commercial tender intent; it is never execution or settlement truth."""
 if sale.status is not POSStatus.COMPLETED_COMMERCIAL: raise ValueError('M9_TENDER_SALE_NOT_FINAL')
 if requested_amount_minor != sale.total_minor: raise ValueError('M9_TENDER_AMOUNT_MISMATCH')
 return POSTenderIntent(sale.tenant_id,sale.location_id,sale.sale_id,tender_type,requested_amount_minor,sale.currency,idempotency_key)

def record_cash_tender(sale: POSSale, cash_received_minor: int, operator_id: str, recorded_at: str) -> POSCashTender:
 """Record bounded cash evidence without asserting paid or settled state."""
 if sale.status is not POSStatus.COMPLETED_COMMERCIAL: raise ValueError('M9_CASH_SALE_NOT_FINAL')
 return POSCashTender(sale.tenant_id,sale.location_id,sale.sale_id,sale.currency,sale.total_minor,cash_received_minor,operator_id,recorded_at)

def create_return(sale: POSSale, sku: str, quantity: int, reason: str, return_id: str, idempotency_key: str, prior_returns=()):
 """Create tenant-bound return intent and enforce cumulative quantity."""
 line=next((x for x in sale.lines if x.sku==sku),None)
 if line is None or quantity + sum(x.quantity for x in prior_returns if x.sku==sku) > line.quantity: raise ValueError('M9_RETURN_EXCEEDS_SALE')
 return POSReturnIntent(sale.tenant_id,sale.location_id,return_id,sale.sale_id,sku,quantity,reason,idempotency_key)

def create_refund_intent(sale: POSSale, amount_minor: int, basis: str, refund_intent_id: str, idempotency_key: str):
 """Create bounded commercial refund intent; no provider or paid truth."""
 if amount_minor <= 0 or amount_minor > sale.total_minor: raise ValueError('M9_REFUND_EXCEEDS_SALE')
 return POSRefundIntent(sale.tenant_id,sale.location_id,refund_intent_id,sale.sale_id,amount_minor,sale.currency,basis,idempotency_key)
# ARTIFACT: pos_commercial_orchestration.py
# VERSION: v1.0.0-M9
# AUTHORITY BOUNDARY: Commercial orchestration only.
# FAIL-CLOSED POSTURE: No paid or settled state.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
