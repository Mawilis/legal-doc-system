/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TENANT INVOICE QUERY SERVICE [v1.0.0-LEDGER-EXPLORER]                                                                     ║
 * ║ [PAGINATED LEDGER READS | TENANT ISOLATION | FILTER VALIDATION | PRESENTATION-SAFE PROJECTION]                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME: One auditable invoice read contract for Ledger Explorer and other authenticated financial surfaces.                          ║
 * ║ BIBLICAL ANCHOR: Psalm 1:3 - "And he shall be like a tree planted by the rivers of water..."                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/invoiceService.js                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & OWNERSHIP: Wilson Khanyezi (Founder/Chief Architect) | AI Engineering (Codex) - tenant-safe ledger service.          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import Invoice from '../models/Invoice.js';

/**
 * @function clampInteger
 * @description Parses and bounds a positive integer query parameter.
 * @param {unknown} value - Candidate input.
 * @param {number} fallback - Value used for invalid input.
 * @param {number} maximum - Inclusive upper bound.
 * @returns {number} Bounded integer.
 * @collaboration Prevents a ledger query from becoming an unbounded database read.
 */
function clampInteger(value, fallback, maximum) {
  const parsed = Number.parseInt(String(value ?? ''), 10);
  if (!Number.isFinite(parsed) || parsed < 1) return fallback;
  return Math.min(parsed, maximum);
}

/**
 * @function escapeRegex
 * @description Escapes a search value before constructing a MongoDB regular expression.
 * @param {unknown} value - User-provided search value.
 * @returns {string} Regex-safe text.
 * @collaboration Keeps invoice search expressive without allowing regex injection.
 */
function escapeRegex(value) {
  return String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * @function listInvoicesForTenant
 * @description Fetches a paginated, tenant-isolated ledger slice and its pagination metadata.
 * @param {{tenantId: string, page?: unknown, limit?: unknown, status?: unknown, search?: unknown}} options - Query constraints.
 * @returns {Promise<{items: object[], pagination: {total: number, page: number, limit: number, pages: number}}>} Ledger result.
 * @collaboration Shares one authoritative tenant filter between the controller and future billing surfaces.
 */
export async function listInvoicesForTenant({ tenantId, page = 1, limit = 20, status, search } = {}) {
  if (!tenantId) throw new Error('TENANT_ID_REQUIRED');

  const safePage = clampInteger(page, 1, 100000);
  const safeLimit = clampInteger(limit, 20, 100);
  const filter = {
    tenantId: String(tenantId),
    $or: [{ isCurrent: true }, { isCurrent: { $exists: false } }],
  };

  if (status) filter.status = String(status).trim().toUpperCase();
  if (search && String(search).trim()) {
    const expression = new RegExp(escapeRegex(search).trim(), 'i');
    filter.$and = [{
      $or: [
        { invoiceNumber: expression },
        { clientName: expression },
        { customerName: expression },
        { businessName: expression },
        { clientId: expression },
      ],
    }];
  }

  const [items, total] = await Promise.all([
    Invoice.find(filter)
      .sort({ issueDate: -1, createdAt: -1 })
      .skip((safePage - 1) * safeLimit)
      .limit(safeLimit)
      .select('tenantId invoiceNumber clientName customerName businessName clientId totalAmount status issueDate dueDate description lineItems currency traceId merkleRoot qrVerificationUrl sealHash')
      .lean()
      .exec(),
    Invoice.countDocuments(filter).exec(),
  ]);

  return {
    items,
    pagination: {
      total,
      page: safePage,
      limit: safeLimit,
      pages: Math.ceil(total / safeLimit),
    },
  };
}

export default { listInvoicesForTenant };
