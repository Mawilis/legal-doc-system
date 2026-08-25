/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – BILLING UTILITIES [v1.0.0-PHASE5-PLAN-CATALOG]                                                                           ║
 * ║ [IDEMPOTENCY | CANONICAL STRINGIFICATION | SHARED BILLING HELPERS]                                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME: Shared utilities for billing operations – idempotency keys, stable JSON stringification, and common helpers.                ║
 * ║           Used by subscriptionController and other billing modules.                                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/billingUtils.js                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                               ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated idempotency and stable hashing.                                                          ║
 * ║ • AI Engineering (v1.0.0) – Created utilities.                                                                                      ║
 * ║ • Compliance: POPIA §19, GDPR §32, SOC2 §CC7.2, ISO 27001                                                                           ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

/**
 * Creates a unique idempotency key for billing operations.
 * @param {string} tenantId - Tenant identifier.
 * @returns {string} Idempotency key.
 */
export const createBillingIdempotencyKey = (tenantId = 'GLOBAL_ROOT') => {
  const entropy = globalThis.crypto?.randomUUID
    ? globalThis.crypto.randomUUID().slice(0, 12)
    : `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
  return `WILSY-BILL-${String(tenantId || 'GLOBAL_ROOT').toUpperCase()}-${entropy.toUpperCase()}`;
};

/**
 * Stable JSON stringification with sorted keys (deterministic).
 * @param {*} value - Any value to stringify.
 * @returns {string} Stable JSON string.
 */
export const stableBillingStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) {
    return `[${value.map(item => stableBillingStringify(item)).join(',')}]`;
  }
  const keys = Object.keys(value).sort();
  const pairs = keys.map(key => `${JSON.stringify(key)}:${stableBillingStringify(value[key])}`);
  return `{${pairs.join(',')}}`;
};

// ═══════════════════════════════════════════════════════════════════════════════
// INSTITUTIONAL CERTIFICATION SEAL – BILLING UTILITIES
// Status:          PRODUCTION READY
// Version:         v1.0.0-PHASE5-PLAN-CATALOG
// Compliance:      POPIA §19, GDPR §32, SOC2 §CC7.2, ISO 27001
// ═══════════════════════════════════════════════════════════════════════════════
