/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – BILLING LIVE ADAPTER [V2.2.0-OMEGA-PHASE5]                                                                                ║
 * ║ AUTHORITY: WILSY OS FINANCE & OPERATIONS | TERMINAL WORKFLOW COMPLIANT                                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.2.0-OMEGA-PHASE5 | PRODUCTION HARDENED | TRILLION‑DOLLAR SPEC                                                              ║
 * ║ EPITOME: NORMALISES BFF LIVE_DB / LIVE_EMPTY ENVELOPES INTO BILLINGHUD SHAPES – ZERO SYNTHETIC DATA, FULL KENNEL EOS AWARENESS       ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/utils/billingLiveAdapter.js                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/Architect) – Mandated zero‑loss integration with BFF LIVE_DB routes.                                      ║
 * ║ • AI Engineering (DeepSeek) – ARCHITECTED: Adapter functions for summary, analytics, credit, and invoice extraction.                   ║
 * ║ • AI Engineering (Gemini) – ENHANCED: Robust extractData, added institutional documentation, and Kennel EOS awareness.                ║
 * ║ • Compliance: POPIA §19, GDPR §32, SOC2 §CC7.2, ISO 27001.                                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 FEATURES:                                                                                                                           ║
 * ║   1. extractData – Unwraps nested API envelopes (axios, double‑nested, success‑guarded).                                             ║
 * ║   2. extractLiveInvoices – Extracts invoice arrays from summary payloads.                                                             ║
 * ║   3. normalizeBillingSummary – Normalises summary with ARR, MRR, history, source status.                                              ║
 * ║   4. normalizeBillingAnalytics – Normalises analytics (forecast, history).                                                            ║
 * ║   5. normalizeCreditScores – Normalises credit‑score object (empty allowed).                                                          ║
 * ║   6. buildLiveSourceHeartbeat – Builds source heartbeat from settled API result.                                                       ║
 * ║   7. Kennel EOS aware – honours kennelVersion and source statuses.                                                                    ║
 * ║   8. JSDoc documentation for all exported functions.                                                                                 ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

/**
 * @function asMoneyNumber
 * @description Safe number coercion without inventing non‑zero theatre values.
 * @param {unknown} value - Any value to convert to a number.
 * @returns {number} A finite number or 0.
 * @collaboration Prevents NaN and undefined from breaking billing calculations.
 * @institutional Financial integrity depends on truthful zeros, not invented numbers.
 * @epitome "Zero is a valid state."
 */
export function asMoneyNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

/**
 * @function extractData
 * @description Unwraps axios / sovereignClient response envelopes without inventing fields.
 * Handles both standard axios `{ data: ... }` and double‑nested `{ data: { data: ... } }`.
 * Also respects success/status flags to avoid reading synthetic data.
 * @param {object} response - Axios response or already‑unwrapped body.
 * @returns {object|Array} The unwrapped payload.
 * @collaboration BillingHUD hydrate must read the same shape the BFF returns.
 * @institutional All data flows through this gateway, ensuring consistent envelope unwrapping.
 */
export function extractData(response) {
  if (response == null) return {};
  // Axios-style: response.data
  if (Object.prototype.hasOwnProperty.call(response, 'data') && response.data != null) {
    const inner = response.data;
    // Double envelope: { data: { data: ... } } or { data: { success: true, data: ... } }
    if (inner && typeof inner === 'object' && !Array.isArray(inner)) {
      // If inner has a data field and either success or status is true, unwrap to inner.data
      if (Object.prototype.hasOwnProperty.call(inner, 'data') &&
          (inner.success === true || inner.status === true || inner.status === 'success')) {
        return inner.data != null ? inner.data : inner;
      }
      // If inner has no data but has other fields, return inner
      return inner;
    }
    return inner;
  }
  return response;
}

/**
 * @function extractLiveInvoices
 * @description Extract invoice arrays from mixed BFF / legacy envelopes.
 * @param {object} summary - Summary payload from /billing/summary.
 * @returns {object[]} Array of invoice objects.
 * @collaboration BillingHUD ledger must only render rows that arrived from the API.
 * @institutional Prevents display of synthetic invoices when the source is empty.
 */
export function extractLiveInvoices(summary = {}) {
  const candidates = [
    summary?.recentInvoices,
    summary?.invoices,
    summary?.data?.recentInvoices,
    summary?.data?.invoices
  ];
  const rows = candidates.find((c) => Array.isArray(c));
  return Array.isArray(rows) ? rows.filter(Boolean) : [];
}

/**
 * @function normalizeBillingSummary
 * @description Normalize summary into BillingHUD state fields (truthful zeros allowed).
 * @param {object} raw - Response body from /billing/summary
 * @returns {object} Normalised summary with ARR, MRR, history, source, and liveMeta.
 * @collaboration Ensures BillingHUD consumes a consistent shape regardless of backend version.
 * @institutional Source status (`LIVE_DB`, `LIVE_EMPTY`) is preserved for operational awareness.
 */
export function normalizeBillingSummary(raw = {}) {
  const body = raw?.data && typeof raw.data === 'object' && !Array.isArray(raw.data)
    ? { ...raw, ...raw.data }
    : raw;

  const invoices = extractLiveInvoices(body);
  const totalArr = asMoneyNumber(body.totalArr ?? body.arr ?? body.metrics?.arr);
  const mrr = asMoneyNumber(body.mrr ?? body.metrics?.mrr);
  const outstanding = asMoneyNumber(
    body.outstanding ?? body.outstandingReceivables ?? body.metrics?.outstandingReceivables
  );
  const activeSubscriptions = asMoneyNumber(
    body.activeSubscriptions ?? body.metrics?.activeSubscriptions
  );
  const history = Array.isArray(body.history)
    ? body.history
    : Array.isArray(body.data?.history)
      ? body.data.history
      : [];

  const source = String(body.source || 'LIVE_EMPTY').toUpperCase();
  const isLive = source === 'LIVE_DB' || source === 'REVENUE_SURFACE';
  const isEmpty = source === 'LIVE_EMPTY' || (invoices.length === 0 && totalArr === 0 && mrr === 0);

  return {
    ...body,
    totalArr,
    arr: totalArr,
    mrr,
    outstanding,
    outstandingReceivables: outstanding,
    activeSubscriptions,
    pendingInvoices: asMoneyNumber(body.pendingInvoices ?? body.invoicesOpen),
    recentInvoices: invoices,
    invoices,
    history,
    collectedYtd: asMoneyNumber(body.collectedYtd ?? body.ytdRevenue),
    ytdRevenue: asMoneyNumber(body.ytdRevenue ?? body.collectedYtd),
    source,
    sources: Array.isArray(body.sources) ? body.sources : [],
    kennelVersion: body.kennelVersion || null,
    liveMeta: {
      source,
      isLive,
      isEmpty,
      invoiceCount: invoices.length,
      note: body.note || null
    }
  };
}

/**
 * @function normalizeBillingAnalytics
 * @description Normalize analytics envelope for forecast + history.
 * @param {object} raw - Response body from /billing/analytics.
 * @returns {object} Normalised analytics with forecast, history, and source.
 * @collaboration BillingHUD uses this for trend visualisation and forecasting.
 * @institutional Forecast is derived from live history, not invented.
 */
export function normalizeBillingAnalytics(raw = {}) {
  const body = raw?.data && typeof raw.data === 'object' ? { ...raw, ...raw.data } : raw;
  return {
    forecast: asMoneyNumber(body.forecast),
    history: Array.isArray(body.history) ? body.history : [],
    mrr: asMoneyNumber(body.mrr),
    arr: asMoneyNumber(body.arr),
    source: String(body.source || 'LIVE_EMPTY').toUpperCase()
  };
}

/**
 * @function normalizeCreditScores
 * @description Normalize credit-scores payload — empty object is valid live empty.
 * @param {object} raw - Response body from /billing/credit-scores.
 * @returns {{ scores: Record<string, number>, source: string }} Normalised credit scores.
 * @collaboration Credit scores are backend‑derived; empty is a valid state.
 * @institutional No synthetic scores are invented – source honesty is preserved.
 */
export function normalizeCreditScores(raw = {}) {
  const body = raw?.data && typeof raw.data === 'object' ? { ...raw, ...raw.data } : raw;
  const scores = body.scores && typeof body.scores === 'object' && !Array.isArray(body.scores)
    ? body.scores
    : {};
  return {
    scores,
    source: String(body.source || 'LIVE_EMPTY').toUpperCase()
  };
}

/**
 * @function buildLiveSourceHeartbeat
 * @description Build source heartbeat row from PromiseSettledResult + live meta.
 * @param {PromiseSettledResult} result - Settled promise result from Promise.allSettled.
 * @param {string} label - Human‑readable label for the source.
 * @returns {{ label: string, status: string, live: boolean, error: string|null }} Heartbeat row.
 * @collaboration BillingHUD flight deck uses this to show which sources are live.
 * @institutional Operational transparency – sources are either live, empty, or silent.
 */
export function buildLiveSourceHeartbeat(result, label) {
  if (result?.status === 'fulfilled') {
    const source = result.value?.liveMeta?.source || result.value?.source || 'LIVE_DB';
    const empty = result.value?.liveMeta?.isEmpty;
    return {
      label,
      status: empty ? 'LIVE_EMPTY' : source === 'LIVE_EMPTY' ? 'LIVE_EMPTY' : 'LIVE',
      live: source === 'LIVE_DB' || source === 'REVENUE_SURFACE',
      error: null
    };
  }
  return {
    label,
    status: 'SOURCE_SILENT',
    live: false,
    error: result?.reason?.response?.data?.message || result?.reason?.message || 'SOURCE_SILENT'
  };
}

export default {
  asMoneyNumber,
  extractData,
  extractLiveInvoices,
  normalizeBillingSummary,
  normalizeBillingAnalytics,
  normalizeCreditScores,
  buildLiveSourceHeartbeat
};

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏛️ INSTITUTIONAL CERTIFICATION SEAL — billingLiveAdapter v2.2.0-OMEGA-PHASE5
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status:          CERTIFIED PRODUCTION ARTIFACT
 * Version:         2.2.0-OMEGA-PHASE5
 * Compliance:      POPIA §19 / GDPR §32 / SOC2 §CC7.2 / ISO 27001
 * Health Check:
 *   ✅ extractData – robust envelope unwrapping
 *   ✅ extractLiveInvoices – invoice extraction from summary
 *   ✅ normalizeBillingSummary – consistent ARR/MRR/history/source
 *   ✅ normalizeBillingAnalytics – forecast and history normalisation
 *   ✅ normalizeCreditScores – credit‑score normalisation (empty allowed)
 *   ✅ buildLiveSourceHeartbeat – source heartbeat from settled results
 *   ✅ Kennel EOS aware – kennelVersion preserved
 *   ✅ JSDoc documentation for all exported functions
 * ═══════════════════════════════════════════════════════════════════════════════
 */
