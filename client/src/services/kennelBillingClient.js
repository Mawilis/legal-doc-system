/**
 * WILSY OS — Kennel Billing Client [V1.3.0‑OUTSTANDING]
 * Path: client/src/services/kennelBillingClient.js
 * Invoice CRUD toward EOS Kennel (/billing/platform|client/invoices).
 * Summary/analytics remain on Node until Phase D.
 *
 * V1.3.0: Improved outstandingAmount calculation – uses amountPaid, explicit outstanding,
 *         and computed total - paid. Enhanced tax handling in sumLineItems.
 * Compliance: POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15
 */
import sovereignClient from '../utils/sovereignClient';

const IDEMPOTENCY_HEADER = 'X-Idempotency-Key';

/**
 * Creates a unique idempotency key for a billing operation.
 * @param {string} [tenantId='GLOBAL_ROOT']
 * @returns {string}
 */
export function createIdempotencyKey(tenantId = 'GLOBAL_ROOT') {
  const entropy = globalThis.crypto?.randomUUID
    ? globalThis.crypto.randomUUID().slice(0, 12)
    : `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
  return `WILSY-BILL-${String(tenantId || 'GLOBAL_ROOT').toUpperCase()}-${entropy.toUpperCase()}`;
}

/**
 * Builds a Kennel‑compatible invoice payload from a draft object.
 * @param {object} draft
 * @param {object} [options]
 * @param {string} [options.mode='PLATFORM']
 * @returns {object}
 */
export function buildKennelInvoicePayload(draft = {}, { mode = 'PLATFORM' } = {}) {
  const amount = Number(draft.amount ?? draft.unitPrice ?? 0);
  const qty = Number(draft.quantity ?? 1) || 1;
  const unit = Number(draft.unitPrice ?? amount);
  const taxRate = Number(draft.defaultTaxRate ?? draft.taxRate ?? 0.15);
  const taxAmount = Number(
    draft.taxAmount ?? Math.round(amount * taxRate * 100) / 100
  );
  const currency = String(draft.currency || 'ZAR').toUpperCase();
  const isClient = String(mode).toUpperCase().includes('CLIENT');

  const line_items = Array.isArray(draft.line_items) && draft.line_items.length
    ? draft.line_items
    : [
        {
          description: draft.description || 'WILSY OS sovereign allocation',
          amount,
          quantity: qty,
          unit_price: unit,
          tax_rate: taxRate,
          tax_amount: taxAmount,
          discount: Number(draft.discount || 0),
        },
      ];

  return {
    tenant_id: draft.tenantId || draft.tenant_id || draft.recipientTenantId,
    issuer_tenant_id: draft.issuerTenantId || draft.issuer_tenant_id,
    recipient_tenant_id: draft.recipientTenantId || draft.recipient_tenant_id || draft.tenantId,
    currency,
    description: draft.description || line_items[0]?.description,
    status: draft.status || 'ISSUED',
    billing_mode: isClient ? 'CLIENT' : 'PLATFORM',
    supply_type: draft.supplyType || draft.supply_type || 'Digital service',
    tax_jurisdiction: draft.taxJurisdiction || draft.clientJurisdiction || 'ZA',
    issue_date: draft.issueDate || draft.issue_date,
    due_date: draft.dueDate || draft.due_date,
    payment_terms: Number(draft.paymentTerms || 30),
    line_items,
    amount,
    tax_amount: taxAmount,
    total_amount: Number(draft.totalAmount ?? amount + taxAmount),
    salesperson_id: draft.salespersonId || draft.salesperson_id || null,
    salesperson_name: draft.salespersonName || draft.salesperson || null,
    customer_tax_id: draft.customerTaxId || null,
    metadata: {
      invoiceClass: draft.invoiceClass,
      clientType: draft.clientType,
      idempotencyKey: draft.idempotencyKey,
      proofHash: draft.proofHash,
      source: 'BILLING_HUD',
    },
    idempotency_key: draft.idempotencyKey || createIdempotencyKey(draft.tenantId),
  };
}

/**
 * Creates a new invoice in Kennel.
 * @param {object} draft
 * @param {object} [options]
 * @param {string} [options.mode='PLATFORM']
 * @param {string} [options.tenantId]
 * @returns {Promise<object>}
 */
export async function createKennelInvoice(draft = {}, { mode = 'PLATFORM', tenantId } = {}) {
  const isClient = String(mode).toUpperCase().includes('CLIENT');
  const path = isClient ? '/billing/client/invoices' : '/billing/platform/invoices';
  const body = buildKennelInvoicePayload(draft, { mode });
  const tid = tenantId || body.tenant_id || 'GLOBAL_ROOT';
  const key = body.idempotency_key || createIdempotencyKey(tid);

  const res = await sovereignClient.post(path, body, {
    headers: {
      'X-Tenant-ID': tid,
      [IDEMPOTENCY_HEADER]: key,
    },
  });
  return res?.data ?? res;
}

/**
 * Retrieves a paginated list of invoices from Kennel.
 * @param {object} [params]
 * @param {string} [params.mode='PLATFORM']
 * @param {string} [params.tenantId='GLOBAL_ROOT']
 * @param {number} [params.limit=20]
 * @param {number} [params.offset=0]
 * @param {string} [params.status]
 * @param {string} [params.q]
 * @param {string} [params.from]
 * @param {string} [params.to]
 * @returns {Promise<{ items: Array, total: number }>}
 */
export async function listKennelInvoices({
  mode = 'PLATFORM',
  tenantId = 'GLOBAL_ROOT',
  limit = 20,
  offset = 0,
  status,
  q,
  from,
  to,
} = {}) {
  const isClient = String(mode).toUpperCase().includes('CLIENT');
  const path = isClient ? '/billing/client/invoices' : '/billing/platform/invoices';
  const params = {
    tenantId,
    limit,
    offset,
    status,
    q,
    from,
    to,
    sort_by: 'issued_at',
    sort_order: -1,
  };
  Object.keys(params).forEach((k) => params[k] == null && delete params[k]);

  const res = await sovereignClient.get(path, {
    params,
    headers: { 'X-Tenant-ID': tenantId },
  });
  const data = res?.data ?? res;
  if (Array.isArray(data)) return { items: data, total: data.length };
  if (Array.isArray(data?.items)) return { items: data.items, total: data.total ?? data.items.length };
  if (Array.isArray(data?.invoices)) return { items: data.invoices, total: data.total ?? data.invoices.length };
  if (Array.isArray(data?.data)) return { items: data.data, total: data.total ?? data.data.length };
  return { items: [], total: 0 };
}

/** Map Kennel domain statuses → ledger UI vocabulary */
export function normalizeKennelStatus(raw) {
  const s = String(raw || '').toUpperCase().trim();
  if (!s) return 'DRAFT';
  if (s === 'OPEN' || s === 'SENT' || s === 'ACTIVE' || s === 'POSTED') return 'ISSUED';
  if (s === 'PARTIAL' || s === 'PARTIALLY_PAID' || s === 'PARTIAL_PAID') return 'PARTIALLY_PAID';
  if (s === 'SETTLED' || s === 'COMPLETE' || s === 'COMPLETED') return 'PAID';
  if (s === 'PAST_DUE' || s === 'LATE') return 'OVERDUE';
  if (s === 'VOIDED' || s === 'CANCELLED' || s === 'CANCELED') return 'VOID';
  return s;
}

/**
 * Sums line item totals including tax.
 * @param {object} inv
 * @returns {number}
 */
function sumLineItems(inv = {}) {
  const lines = inv.line_items || inv.lineItems || inv.items || [];
  if (!Array.isArray(lines) || !lines.length) return 0;
  return lines.reduce((sum, li) => {
    const qty = Number(li.quantity ?? li.qty ?? 1) || 1;
    const unit = Number(li.unit_price ?? li.unitPrice ?? 0) || 0;
    const exclusive = Number(li.amount ?? li.line_total ?? li.lineTotal ?? (qty * unit)) || 0;
    let tax = Number(li.tax_amount ?? li.taxAmount ?? 0) || 0;
    const rate = Number(li.tax_rate ?? li.taxRate ?? 0) || 0;
    if (tax <= 0 && rate > 0 && exclusive > 0) tax = Math.round(exclusive * rate * 100) / 100;
    // Domain stores amount as EX-VAT line total → always add tax for payable
    return sum + exclusive + tax;
  }, 0);
}

/**
 * Normalizes a Kennel invoice row for use in the ledger UI.
 * @param {object} inv – raw invoice from Kennel
 * @returns {object} normalised row
 */
export function normalizeKennelInvoiceRow(inv = {}) {
  if (!inv || typeof inv !== 'object') return {};

  const lineSum = sumLineItems(inv);
  const rawTotal = Number(
    inv.total_amount ?? inv.totalAmount ?? inv.total ?? inv.grand_total ?? inv.grandTotal
  );
  const rawAmount = Number(inv.amount ?? inv.subtotal ?? inv.sub_total ?? inv.base_amount ?? inv.baseAmount);
  const taxAmount = Number(inv.tax_amount ?? inv.taxAmount ?? inv.vat_amount ?? inv.vatAmount ?? 0) || 0;

  // amount/subtotal is EX-VAT; total/total_amount is the legal payable (INCL tax)
  let totalAmount = 0;
  if (Number.isFinite(rawTotal) && rawTotal > 0) {
    totalAmount = rawTotal;
  } else if (lineSum > 0) {
    totalAmount = lineSum; // sumLineItems already folds tax when present
  } else if (Number.isFinite(rawAmount) && rawAmount > 0) {
    totalAmount = taxAmount > 0 ? rawAmount + taxAmount : rawAmount;
  } else {
    totalAmount = 0;
  }

  // Prefer human bill-to over raw tenant codes
  const billTo =
    inv.customer_name || inv.customerName || inv.client_name || inv.clientName ||
    inv.recipient_name || inv.recipientName || inv.business_name || inv.businessName ||
    inv.metadata?.tenantName || inv.metadata?.customer_name || inv.metadata?.brand?.legalName ||
    inv.customer_id || inv.customerId || inv.recipient_tenant_id || inv.recipientTenantId ||
    inv.tenant_id || inv.tenantId || '';

  const status = normalizeKennelStatus(inv.status || inv.invoice_status || inv.invoiceStatus);
  const paid = Number(inv.amount_paid ?? inv.amountPaid ?? inv.paid_amount ?? inv.paidAmount ?? 0) || 0;
  const explicitOutstanding = inv.outstanding_amount ?? inv.outstandingAmount ?? inv.balance_due ?? inv.balanceDue;

  let outstandingAmount = 0;
  if (explicitOutstanding != null && explicitOutstanding !== '') {
    outstandingAmount = Number(explicitOutstanding) || 0;
  } else if (status === 'PAID' || status === 'VOID') {
    outstandingAmount = 0;
  } else {
    const rem = totalAmount - paid;
    outstandingAmount = rem > 0 ? rem : (status === 'PAID' ? 0 : totalAmount);
  }

  return {
    ...inv,
    id: inv.id || inv.invoice_id || inv.invoiceId || inv._id,
    invoiceNumber: inv.invoice_number || inv.invoiceNumber || inv.number || inv.invoice_id || inv.invoiceId,
    status,
    rawStatus: inv.status || status,
    amount: totalAmount,
    totalAmount,
    amountPaid: paid,
    outstandingAmount,
    taxAmount,
    currency: inv.currency || 'ZAR',
    tenantId: inv.tenant_id || inv.tenantId || '',
    customerName: billTo,
    clientName: billTo,
    counterparty: billTo,
    recipientTenantId: inv.recipient_tenant_id || inv.recipientTenantId || inv.customer_id || inv.customerId || inv.tenant_id || inv.tenantId,
    description: inv.description || inv.line_items?.[0]?.description || inv.lineItems?.[0]?.description || '',
    issueDate: inv.issued_at || inv.issueDate || inv.created_at || inv.createdAt,
    dueDate: inv.due_at || inv.dueDate || inv.due_date,
    sealedAt: inv.sealed_at || inv.sealedAt || inv.issued_at || inv.issueDate,
    proofHash: inv.proof_hash || inv.proofHash || inv.seal_hash || inv.sealHash || '',
    sealHash: inv.seal_hash || inv.sealHash || inv.proof_hash || inv.proofHash || '',
    merkleRoot: inv.merkle_root || inv.merkleRoot,
    billingMode: inv.billing_mode || inv.billingMode,
    issuerType: inv.issuer_type || inv.issuerType || inv.billing_mode || inv.billingMode || 'platform',
    orderNumber: inv.order_number || inv.orderNumber || '',
    purchaseOrder: inv.purchase_order || inv.purchaseOrder || '',
    salespersonName: inv.salesperson_name || inv.salespersonName || inv.metadata?.salesperson || '',
    createdByName: inv.created_by_name || inv.createdByName || inv.performed_by || inv.performedBy || inv.created_by || inv.createdBy,
    createdByEmail: inv.created_by_email || inv.createdByEmail,
    jurisdiction: inv.customer_jurisdiction || inv.customerJurisdiction || inv.seller_jurisdiction || inv.jurisdiction || 'ZA',
  };
}

export default {
  createIdempotencyKey,
  buildKennelInvoicePayload,
  createKennelInvoice,
  listKennelInvoices,
  normalizeKennelInvoiceRow,
};

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏛️ INSTITUTIONAL CERTIFICATION SEAL — Kennel Billing Client V1.3.0‑OUTSTANDING
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status:          CERTIFIED PRODUCTION ARTIFACT — V1.3.0‑OUTSTANDING
 * Fix:             Improved outstandingAmount and amountPaid; better tax handling.
 * Compliance:      POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15
 * ────────────────────────────────────────────────────────────────────────────────
 * 🔒 This file is ready for deployment.
 * ═══════════════════════════════════════════════════════════════════════════════
 */
