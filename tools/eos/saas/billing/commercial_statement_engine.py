"""TITLE: Commercial Statement Engine
VERSION: v1.0.0-M7
AUTHORITY: Wilsy OS Core Governance
EPITOME: Separated deterministic platform/client statement derivation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/commercial_statement_engine.py
COLLABORATION / OWNERSHIP: SaaS Billing statement engine.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M7 establishes live statement computation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Explicit tenant/account scope.
TENANT BOUNDARY: Inputs must share tenant_id and account_id.
AUTHORITY BOUNDARY: Invoice/evidence projection only.
FINANCIAL AUTHORITY BOUNDARY: No mutation or payment authority.
TRANSACTION BOUNDARY: Read-only.
FAIL-CLOSED DECLARATION: Cross-lane and mixed-currency data rejects.
"""
from datetime import datetime, timezone
from dataclasses import replace
from ..domain.commercial_statement import AgingBucket, CommercialStatement, CommercialStatementActivity, StatementActivityKind, StatementFamily, StatementLedgerKind
from ..domain.billing import PlatformInvoice, ClientInvoice, InvoiceType
from ..domain.platform_billing_commercial_settlement_projection import PlatformBillingCommercialSettlementProjection
from ..domain.commercial_receivable import CommercialReceivable, ReceivableFamily
from ..domain.commercial_receivable_reconciliation import CommercialReceivableReconciliation
class CommercialStatementError(ValueError): pass
def invoice_activity(invoice, *, tenant_id=None, ledger_kind, account_id, effective_at):
    if tenant_id is not None and (not isinstance(getattr(invoice, 'tenant_id', None), str) or invoice.tenant_id != tenant_id):
        raise CommercialStatementError('M7_STATEMENT_TENANT_MISMATCH')
    if ledger_kind is StatementLedgerKind.PLATFORM and not isinstance(invoice, PlatformInvoice): raise CommercialStatementError('M7_PLATFORM_SOURCE_REQUIRED')
    if ledger_kind is StatementLedgerKind.CLIENT and (not isinstance(invoice, ClientInvoice) or invoice.invoice_type is not InvoiceType.CLIENT): raise CommercialStatementError('M7_CLIENT_SOURCE_REQUIRED')
    if not isinstance(account_id, str) or not account_id.strip(): raise CommercialStatementError('M7_ACCOUNT_INVALID')
    return CommercialStatementActivity(invoice.tenant_id, ledger_kind, account_id, invoice.invoice_id, 'invoice', effective_at, invoice.currency, int(round(invoice.total*100)), StatementActivityKind.INVOICE_CHARGE, getattr(invoice,'commercial_release_evidence_fingerprint',None))
def build_statement(*,tenant_id,ledger_kind, family, account_id, currency, as_of, activities=(), period_start=None, period_end=None, opening_balance_minor=0):
 vals=tuple(a for a in activities if a.tenant_id==tenant_id and a.ledger_kind is ledger_kind and a.account_id==account_id)
 if any(a.currency!=currency for a in vals): raise CommercialStatementError('M7_MIXED_CURRENCY')
 vals=tuple(sorted(vals,key=lambda a:(a.effective_at,a.source_id)))
 selected=tuple(a for a in vals if (period_start is None or a.effective_at>=period_start) and (period_end is None or a.effective_at<=period_end) and a.effective_at<=as_of)
 aging={b.value:0 for b in AgingBucket}
 for a in selected:
  if a.kind is StatementActivityKind.INVOICE_CHARGE:
   days=max(0,(as_of.astimezone().date()-a.effective_at.astimezone().date()).days)
   bucket=AgingBucket.CURRENT if days<=0 else AgingBucket.ONE_30 if days<=30 else AgingBucket.THIRTY_ONE_60 if days<=60 else AgingBucket.SIXTY_ONE_90 if days<=90 else AgingBucket.NINETY_ONE_120 if days<=120 else AgingBucket.ONE_TWENTY_PLUS
   aging[bucket.value]+=a.amount_minor
 return CommercialStatement(tenant_id,ledger_kind,family,account_id,currency,as_of,period_start,period_end,opening_balance_minor,selected,opening_balance_minor+sum(a.amount_minor for a in selected),aging)
def generate_commercial_statement(*, tenant_id, ledger_kind, family, account_id, currency, as_of, invoices=(), settlement_projections=()):
 if as_of.tzinfo is None or as_of.utcoffset() is None: raise CommercialStatementError('M7_AS_OF_INVALID')
 vals=[]
 for invoice in invoices:
  if ledger_kind is StatementLedgerKind.CLIENT and getattr(invoice, 'customer_id', account_id) != account_id: raise CommercialStatementError('M7_CLIENT_ACCOUNT_MISMATCH')
  vals.append(invoice_activity(invoice, tenant_id=tenant_id, ledger_kind=ledger_kind, account_id=account_id, effective_at=getattr(invoice,'issued_at',as_of)))
 for settlement in settlement_projections:
  if ledger_kind is not StatementLedgerKind.PLATFORM or not isinstance(settlement, PlatformBillingCommercialSettlementProjection): raise CommercialStatementError('M7_SETTLEMENT_SOURCE_INVALID')
  if settlement.tenant_id != tenant_id or settlement.currency != currency or settlement.platform_invoice_id not in {i.invoice_id for i in invoices}: raise CommercialStatementError('M7_SETTLEMENT_PROVENANCE_MISMATCH')
  vals.append(CommercialStatementActivity(tenant_id,ledger_kind,account_id,settlement.commercial_settlement_projection_id,'r3f_settlement',settlement.settled_at,currency,-settlement.projected_amount_paid_minor,StatementActivityKind.SETTLEMENT,settlement.projection_fingerprint))
 statement = build_statement(tenant_id=tenant_id,ledger_kind=ledger_kind,family=family,account_id=account_id,currency=currency,as_of=as_of,activities=tuple(vals))
 aging={b.value:0 for b in AgingBucket}
 for invoice in invoices:
  due=getattr(invoice,'due_at',None)
  if due is None or due.tzinfo is None: raise CommercialStatementError('M7_DUE_AT_REQUIRED')
  days=(as_of.astimezone(timezone.utc).date()-due.astimezone(timezone.utc).date()).days
  bucket=AgingBucket.CURRENT if days<=0 else AgingBucket.ONE_30 if days<=30 else AgingBucket.THIRTY_ONE_60 if days<=60 else AgingBucket.SIXTY_ONE_90 if days<=90 else AgingBucket.NINETY_ONE_120 if days<=120 else AgingBucket.ONE_TWENTY_PLUS
  outstanding=max(0,int(round(getattr(invoice,'outstanding_amount',invoice.total)*100)))
  aging[bucket.value]+=outstanding
 return replace(statement, aging=aging)

def generate_receivable_commercial_statement(*, tenant_id, ledger_kind, family, account_id, currency, as_of, receivables=(), reconciliations=(), source_invoices=()):
 """Derive an OPEN_ITEM statement from integer-unit M11 receivable truth only."""
 if as_of.tzinfo is None or family is not StatementFamily.OPEN_ITEM: raise CommercialStatementError('M11E1_SCOPE_INVALID')
 expected=ReceivableFamily.PLATFORM if ledger_kind is StatementLedgerKind.PLATFORM else ReceivableFamily.CLIENT if ledger_kind is StatementLedgerKind.CLIENT else None
 if expected is None: raise CommercialStatementError('M11E1_LEDGER_INVALID')
 invoices={i.invoice_id:i for i in source_invoices}; vals=[]
 for r in sorted(receivables,key=lambda x:(x.tenant_id,x.receivable_family.value,x.receivable_id)):
  if not isinstance(r,CommercialReceivable) or r.tenant_id!=tenant_id or r.receivable_family is not expected or r.currency!=currency: raise CommercialStatementError('M11E1_PROVENANCE_MISMATCH')
  invoice=invoices.get(r.source_invoice_id)
  if invoice is not None and (invoice.tenant_id!=tenant_id or invoice.currency!=currency or (expected is ReceivableFamily.CLIENT and getattr(invoice,'customer_id',None)!=account_id)): raise CommercialStatementError('M11E1_INVOICE_BINDING_MISMATCH')
  recon=next((x for x in reconciliations if isinstance(x,CommercialReceivableReconciliation) and x.receivable_id==r.receivable_id),None)
  amount=r.outstanding_amount_minor if recon is None else recon.outstanding_amount_minor
  if recon is not None and (recon.tenant_id,recon.receivable_family,recon.source_invoice_id,recon.currency,recon.source_receivable_fingerprint)!=(r.tenant_id,r.receivable_family,r.source_invoice_id,r.currency,r.receivable_fingerprint): raise CommercialStatementError('M11E1_RECONCILIATION_MISMATCH')
  vals.append(CommercialStatementActivity(tenant_id,ledger_kind,account_id,r.receivable_id,'commercial_receivable',as_of,currency,amount,StatementActivityKind.RECEIVABLE_BALANCE,recon.reconciliation_fingerprint if recon else r.receivable_fingerprint))
 return build_statement(tenant_id=tenant_id,ledger_kind=ledger_kind,family=family,account_id=account_id,currency=currency,as_of=as_of,activities=tuple(vals))
# ARTIFACT: commercial_statement_engine.py
# VERSION: v1.0.0-M7
# AUTHORITY BOUNDARY: Invoice/evidence projection only.
# TENANT POSTURE: Explicit tenant/account scope.
# FAIL-CLOSED POSTURE: Cross-lane and mixed-currency inputs reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
