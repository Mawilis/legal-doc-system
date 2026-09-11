"""WILSY OS M11D2 AR1P orchestration.
TITLE: AR1 Commercial Receivable Closure Orchestration
VERSION: v1.1.0-M11D2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Projects closed receivable from durable R3F evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/platform_billing_commercial_receivable_closure_projection.py
COLLABORATION / OWNERSHIP: SaaS Billing AR1 orchestration owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-AR1 establishes closure orchestration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Explicit tenant-scoped collections.
TENANT BOUNDARY: All reads are tenant-scoped.
AUTHORITY BOUNDARY: Durable R3F projection is authoritative.
FINANCIAL AUTHORITY BOUNDARY: No execution or money movement.
TRANSACTION BOUNDARY: Caller-owned session required.
FAIL-CLOSED DECLARATION: Mismatch and drift abort.
"""
from datetime import datetime, timezone
from ..domain.billing import PlatformInvoice, InvoiceStatus
from .platform_billing_commercial_settlement_projection_registry import PlatformBillingCommercialSettlementProjectionRegistry
from .platform_billing_commercial_receivable_closure_projection_registry import PlatformBillingCommercialReceivableClosureProjectionRegistry as R, PlatformBillingCommercialReceivableClosureProjectionError
from ..domain.platform_billing_commercial_receivable_closure_projection import PlatformBillingCommercialReceivableClosureProjection as P
def _utc(v):
 if v is None:return None
 if v.tzinfo is None:v=v.replace(tzinfo=timezone.utc)
 else:v=v.astimezone(timezone.utc)
 return v.replace(microsecond=(v.microsecond//1000)*1000)
def project_platform_billing_commercial_receivable_closure(tenant_id, commercial_settlement_projection_id, *, commercial_settlement_projection_collection, platform_invoice_collection, closure_projection_collection, session=None, projected_at=None):
 if session is None or not getattr(session,'in_transaction',False): raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_SESSION_REQUIRED')
 s=PlatformBillingCommercialSettlementProjectionRegistry.get(tenant_id,commercial_settlement_projection_id,commercial_settlement_projection_collection,session=session)
 d=platform_invoice_collection.find_one({'tenant_id':tenant_id,'invoice_id':s.platform_invoice_id},session=session)
 if d is None: raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_INVOICE_NOT_FOUND')
 d=dict(d); d['paid_at']=_utc(d.get('paid_at')); i=PlatformInvoice.from_dict(d)
 if not (i.tenant_id==s.tenant_id==tenant_id and i.invoice_id==s.platform_invoice_id and i.currency==s.currency and s.projected_status=='PAID' and s.projected_amount_paid_minor==i.release_amount_minor and s.projected_outstanding_amount_minor==0 and s.platform_invoice_evidence_fingerprint==i.commercial_release_evidence_fingerprint and i.status is InvoiceStatus.PAID and i.amount_paid==i.total and i.outstanding_amount==0 and _utc(i.paid_at)==_utc(s.settled_at)): raise PlatformBillingCommercialReceivableClosureProjectionError('AR1_PROVENANCE_MISMATCH')
 pid=f'platform-receivable-closure-{i.invoice_id}'
 try: return R.get(tenant_id,pid,closure_projection_collection,session=session)
 except PlatformBillingCommercialReceivableClosureProjectionError as e:
  if str(e)!='AR1_PROJECTION_NOT_FOUND': raise
 now=_utc(projected_at or datetime.now(timezone.utc)); assert now is not None; p=P(tenant_id,pid,i.invoice_id,s.platform_invoice_evidence_fingerprint,s.commercial_settlement_projection_id,s.projection_fingerprint,s.settlement_evidence_id,s.release_authorization_id,i.currency,i.release_amount_minor,s.projected_amount_paid_minor,0,s.settled_at,now,'CLOSED'); return R.create(p,closure_projection_collection,session=session)
# ARTIFACT: platform_billing_commercial_receivable_closure_projection.py
# VERSION: v1.1.0-M11D2
# AUTHORITY BOUNDARY: Python EOS commercial projection orchestration only.
# TENANT POSTURE: Explicit tenant-scoped reads.
# FAIL-CLOSED POSTURE: Mismatch and drift abort.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
