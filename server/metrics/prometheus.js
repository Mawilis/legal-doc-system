/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN PROMETHEUS METRICS REGISTRY [V72.0.0-PRODUCTION]                                                                  ║
 * ║ [TELEMETRY | SCOPE CHECKS | BREACH ESCALATION | COUNCIL DECISIONS | TOKEN LIFECYCLE | RATE LIMIT BACKOFF]                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 72.0.0-PRODUCTION | PRODUCTION READY | TRILLION DOLLAR SPEC                                                                   ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/metrics/prometheus.js                                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated full Prometheus instrumentation for boardroom dashboards.                            ║
 * ║ • AI Engineering (DeepSeek) – ENHANCED: Added token lifecycle, rate limit backoff, and governance ledger metrics; full JSDoc.          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import client from 'prom-client';

// ============================================================================
// 🔥 SOVEREIGN METRICS REGISTRY
// ============================================================================

/**
 * @constant {client.Registry} registry
 * @description The Prometheus registry that holds all sovereign metrics.
 * Used by the `/monitoring/metrics` endpoint to expose data to Grafana.
 */
const registry = new client.Registry();

// Enable default Node.js metrics (event loop lag, memory, GC, etc.)
client.collectDefaultMetrics({ register: registry });

// ============================================================================
// 📊 TELEMETRY METRICS
// ============================================================================

/**
 * @constant {client.Counter} telemetryEvents
 * @description Total number of telemetry events processed (batched or raw).
 * Labels: `status` – 'success', 'failure', 'queued'
 */
export const telemetryEvents = new client.Counter({
  name: 'sovereign_telemetry_events_total',
  help: 'Total processed telemetry events',
  labelNames: ['status'],
  registers: [registry]
});

/**
 * @constant {client.Histogram} telemetryBatchSize
 * @description Size of batched telemetry sends.
 * Labels: none
 */
export const telemetryBatchSize = new client.Histogram({
  name: 'sovereign_telemetry_batch_size',
  help: 'Number of events per telemetry batch',
  buckets: [1, 5, 10, 25, 50, 100],
  registers: [registry]
});

/**
 * @constant {client.Counter} telemetryBackoff
 * @description Count of 429 backoff events in telemetry batching.
 * Labels: `backoffMs` (exponential delay)
 */
export const telemetryBackoff = new client.Counter({
  name: 'sovereign_telemetry_backoff_total',
  help: 'Number of 429 backoff events in telemetry batching',
  labelNames: ['backoffMs'],
  registers: [registry]
});

// ============================================================================
// 🔐 AUTHENTICATION & SCOPE METRICS
// ============================================================================

/**
 * @constant {client.Counter} authScopeChecks
 * @description Total JWT scope validation checks performed.
 * Labels: `scope` – the scope required, `outcome` – 'granted' or 'denied'
 */
export const authScopeChecks = new client.Counter({
  name: 'sovereign_auth_scope_checks_total',
  help: 'Total scope validation checks',
  labelNames: ['scope', 'outcome'],
  registers: [registry]
});

/**
 * @constant {client.Counter} tokenRefreshTotal
 * @description Number of access token refresh attempts.
 * Labels: `outcome` – 'success', 'failure', 'revoked'
 */
export const tokenRefreshTotal = new client.Counter({
  name: 'sovereign_token_refresh_total',
  help: 'Total token refresh attempts',
  labelNames: ['outcome'],
  registers: [registry]
});

/**
 * @constant {client.Counter} tokenRevocationTotal
 * @description Number of refresh token revocations (explicit or due to compromise).
 * Labels: `reason` – 'user_logout', 'suspicious_activity', 'rotation'
 */
export const tokenRevocationTotal = new client.Counter({
  name: 'sovereign_token_revocation_total',
  help: 'Total refresh token revocations',
  labelNames: ['reason'],
  registers: [registry]
});

// ============================================================================
// 🛡️ BREACH & GOVERNANCE METRICS
// ============================================================================

/**
 * @constant {client.Counter} breachEvents
 * @description Total breach escalation events initiated.
 * Labels: `severity` – 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
 */
export const breachEvents = new client.Counter({
  name: 'sovereign_breach_events_total',
  help: 'Total breach escalation events',
  labelNames: ['severity'],
  registers: [registry]
});

/**
 * @constant {client.Counter} councilDecisions
 * @description Total council decisions logged.
 * Labels: `outcome` – 'ACKNOWLEDGED', 'ESCALATED', 'TERMINATED'
 */
export const councilDecisions = new client.Counter({
  name: 'sovereign_council_decisions_total',
  help: 'Total council decisions logged',
  labelNames: ['outcome'],
  registers: [registry]
});

/**
 * @constant {client.Counter} governanceLedgerEntries
 * @description Number of immutable entries added to the governance ledger.
 * Labels: `type` – 'REVOCATION', 'BREACH', 'ESCALATION', 'RESOLUTION'
 */
export const governanceLedgerEntries = new client.Counter({
  name: 'sovereign_governance_ledger_entries_total',
  help: 'Total immutable governance ledger entries',
  labelNames: ['type'],
  registers: [registry]
});

// ============================================================================
// ⚖️ RATE LIMITING & CIRCUIT BREAKER METRICS
// ============================================================================

/**
 * @constant {client.Counter} rateLimitHit
 * @description Number of requests rejected due to rate limiting (429).
 * Labels: `tenantId`, `endpoint`
 */
export const rateLimitHit = new client.Counter({
  name: 'sovereign_rate_limit_hits_total',
  help: 'Total requests rejected by rate limiter',
  labelNames: ['tenantId', 'endpoint'],
  registers: [registry]
});

/**
 * @constant {client.Counter} circuitBreakerState
 * @description Track circuit breaker state changes.
 * Labels: `circuit` – name of the breaker, `state` – 'CLOSED', 'OPEN', 'HALF_OPEN'
 */
export const circuitBreakerState = new client.Gauge({
  name: 'sovereign_circuit_breaker_state',
  help: 'Current state of circuit breakers (0 = CLOSED, 1 = OPEN, 2 = HALF_OPEN)',
  labelNames: ['circuit'],
  registers: [registry]
});

// ============================================================================
// 🚀 METRIC UPDATE HELPERS (for service integration)
// ============================================================================

/**
 * Helper to increment telemetry metrics with batching backoff.
 * @param {string} status - 'success', 'failure', 'queued'
 * @param {number} [batchSize] - optional batch size to record histogram
 */
export function recordTelemetryEvent(status, batchSize = null) {
  telemetryEvents.inc({ status });
  if (batchSize !== null && batchSize > 0) {
    telemetryBatchSize.observe(batchSize);
  }
}

/**
 * Record a token refresh outcome.
 * @param {string} outcome - 'success', 'failure', 'revoked'
 */
export function recordTokenRefresh(outcome) {
  tokenRefreshTotal.inc({ outcome });
}

/**
 * Record a token revocation.
 * @param {string} reason - 'user_logout', 'suspicious_activity', 'rotation'
 */
export function recordTokenRevocation(reason) {
  tokenRevocationTotal.inc({ reason });
}

/**
 * Record a governance ledger entry.
 * @param {string} type - 'REVOCATION', 'BREACH', 'ESCALATION', 'RESOLUTION'
 */
export function recordGovernanceEntry(type) {
  governanceLedgerEntries.inc({ type });
}

/**
 * Record a rate limit hit.
 * @param {string} tenantId - Tenant identifier
 * @param {string} endpoint - Endpoint path
 */
export function recordRateLimitHit(tenantId, endpoint) {
  rateLimitHit.inc({ tenantId, endpoint });
}

/**
 * Update circuit breaker state gauge.
 * @param {string} circuit - Name of circuit breaker
 * @param {string} state - 'CLOSED', 'OPEN', 'HALF_OPEN'
 */
export function updateCircuitBreakerState(circuit, state) {
  const stateMap = { CLOSED: 0, OPEN: 1, HALF_OPEN: 2 };
  const value = stateMap[state] ?? 0;
  circuitBreakerState.set({ circuit }, value);
}

// ============================================================================
// 📤 EXPORTS
// ============================================================================

export default registry;
