/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN PROMETHEUS TELEMETRY [V28.1.0-MARS]                                                                               ║
 * ║ [REAL-TIME REVENUE SENSORS | LATENCY TRACKING | FRACTURE DETECTION | BOARDROOM METRICS]                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 28.1.0-MARS | PRODUCTION READY | BILLION DOLLAR SPEC                                                                          ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/metrics/prometheusMetrics.js                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero-blind-spot financial telemetry for global scale. [2026-05-15]                   ║
 * ║ • AI Engineering (Gemini) - ARCHITECTED: Custom revenue and fracture counters wired for Quota Guard injection. [2026-05-15]            ║
 * ║ • AI Engineering (DeepSeek) - MARS PROTOCOL: Full JSDoc documentation, metric descriptions, export documentation. [2026-05-15]         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import promClient from 'prom-client';

// ============================================================================
// 🧠 GLOBAL REGISTRY & DEFAULT SENSORS
// ============================================================================

/**
 * Prometheus registry – holds all metrics.
 * @type {promClient.Registry}
 */
const register = new promClient.Registry();

/**
 * Enable default Node.js metrics (CPU, memory, event loop lag).
 * All default metrics are prefixed with 'wilsy_os_' to avoid collisions.
 */
promClient.collectDefaultMetrics({
  register,
  prefix: 'wilsy_os_'
});

// ============================================================================
// 💰 FINANCIAL & QUOTA GUARD SENSORS (Custom Counters)
// ============================================================================

/**
 * Counter for successful revenue-generating API strikes.
 * Incremented when a usage record is successfully written to MongoDB and Redis.
 *
 * @type {promClient.Counter}
 * @labelNames {tenantId, type, status} - tenant identifier, strike type (e.g., AI_STRIKE), success/failure
 */
const revenueStrikes = new promClient.Counter({
  name: 'wilsy_revenue_strikes_total',
  help: 'Total number of successful revenue-generating API strikes',
  labelNames: ['tenantId', 'type', 'status'],
  registers: [register]
});

/**
 * Counter for API strikes rejected due to suspended billing or quota limits.
 * Incremented when a tenant is frozen (402 Payment Required).
 *
 * @type {promClient.Counter}
 * @labelNames {tenantId, reason} - tenant identifier, rejection reason (e.g., SUSPENDED)
 */
const quotaRejections = new promClient.Counter({
  name: 'wilsy_quota_rejections_total',
  help: 'Total number of API strikes rejected due to suspended billing or quota limits',
  labelNames: ['tenantId', 'reason'],
  registers: [register]
});

/**
 * Counter for duplicate API strikes intercepted by the Idempotency Shield.
 * Incremented when a request with an already‑used x-idempotency-key is received.
 *
 * @type {promClient.Counter}
 * @labelNames {tenantId} - tenant identifier
 */
const idempotentRejections = new promClient.Counter({
  name: 'wilsy_idempotent_rejections_total',
  help: 'Total number of duplicate API strikes intercepted by the Idempotency Shield',
  labelNames: ['tenantId'],
  registers: [register]
});

/**
 * Counter for CRITICAL failures writing to the MongoDB Sovereign Ledger.
 * Incremented when UsageRecord.create() fails after circuit breaker retries.
 * Each increment represents potential revenue loss – immediate alert threshold.
 *
 * @type {promClient.Counter}
 * @labelNames {tenantId} - tenant identifier
 */
const ledgerFailures = new promClient.Counter({
  name: 'wilsy_ledger_failures_total',
  help: 'CRITICAL: Total number of failed writes to the MongoDB Sovereign Ledger',
  labelNames: ['tenantId'],
  registers: [register]
});

// ============================================================================
// 🚀 EXPORT NUCLEUS
// ============================================================================

/**
 * Get all metrics data in Prometheus exposition format.
 * Used by the /metrics endpoint to feed Grafana/Datadog.
 *
 * @async
 * @returns {Promise<string>} Metrics data as a string
 */
export const getMetricsData = async () => {
  return await register.metrics();
};

/**
 * Get the Content-Type header for Prometheus metrics.
 * Should be set as 'text/plain; charset=utf-8' in the /metrics response.
 *
 * @returns {string} Content-Type string
 */
export const getMetricsContentType = () => {
  return register.contentType;
};

/**
 * Default export – all custom counters and the registry.
 * Used by quotaGuard.js and other controllers to increment metrics.
 *
 * @example
 * import metrics from '../metrics/prometheusMetrics.js';
 * metrics.revenueStrikes.inc({ tenantId, type: 'AI_STRIKE', status: 'success' });
 */
export default {
  revenueStrikes,
  quotaRejections,
  idempotentRejections,
  ledgerFailures,
  register
};
