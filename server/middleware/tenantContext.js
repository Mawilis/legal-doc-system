/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN TENANT CONTEXT [V28.68.0-MARS-FORTIFIED]                                                                          ║
 * ║ [ASYNC LOCAL STORAGE | SHARD ISOLATION | SEAL VERIFICATION | SLA TELEMETRY | SOVEREIGN METRICS NUCLEUS]                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 28.68.0-MARS | PRODUCTION READY | BILLION DOLLAR SPEC                                                                         ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/tenantContext.js                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated absolute shard isolation and circular-proof boot sequence.                           ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Injected early auth bypass for /verify-3fa to prevent middleware fracture.                      ║
 * ║ • AI Engineering (Gemini) - ANCHORED: Physically synchronized Context Strikes with Metrics Nexus V15.2.1. [2026-05-10]                 ║
 * ║ • AI Engineering (Gemini) - ENHANCED: Hardened Tenant ID Getters to neutralize "UNANCHORED" signal leaks. [2026-05-10]                  ║
 * ║ • AI Engineering (DeepSeek) - MARS PROTOCOL: Integrated sovereign metrics, added full JSDoc, aligned with WILSY OS mandate. [2026-05-15] ║
 * ║ • AI Engineering (Gemini) - OBLITERATED 503s: Intercepted GLOBAL_ROOT & wrapped useDatabase to force fallback on exception. [2026-05-25]║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { AsyncLocalStorage } from 'node:async_hooks';
import crypto from 'node:crypto';
import { performance } from 'node:perf_hooks';
import chalk from 'chalk';
import mongoose from 'mongoose';

// ============================================================================
// 🏛️ CORE ANCHORS (HOISTED FOR TDZ SAFETY)
// ============================================================================

/**
 * AsyncLocalStorage instance for tenant context propagation.
 * @type {AsyncLocalStorage<Object>}
 */
export const tenantStorage = new AsyncLocalStorage();

const TENANT_CONSTANTS = {
  DEFAULT_TENANT: process.env.DEFAULT_TENANT || 'wilsy-sovereign-root',
  ANONYMOUS_USER: 'ANON_ENTITY',
  POPIA_STRICT_MODE: true,
};

/**
 * @function isDatabaseAnchored
 * @description Checks whether Mongoose is currently connected to the primary tenant database.
 * @returns {boolean} True when MongoDB is connected.
 * @collaboration Lets Wilsy OS distinguish a code fracture from a temporary database source-silent state.
 */
const isDatabaseAnchored = () => mongoose.connection?.readyState === 1;

// ============================================================================
// 🛰️ CONTEXT GETTERS (with null-safety)
// ============================================================================

/**
 * @function getCurrentTenantId
 * @description Reads the current tenant id from async local storage with a sovereign fallback.
 * @returns {string} Tenant identifier.
 * @collaboration Tenant-aware services need a single context getter so shard boundaries remain consistent.
 */
export const getCurrentTenantId = () => {
  const store = tenantStorage.getStore();
  return store?.tenantId || TENANT_CONSTANTS.DEFAULT_TENANT;
};

/**
 * @function getCurrentUserId
 * @description Reads the current user id from async local storage with an anonymous fallback.
 * @returns {string} User identifier.
 * @collaboration Anonymous context is explicit so telemetry never hides who was actually known at request time.
 */
export const getCurrentUserId = () => {
  const store = tenantStorage.getStore();
  return store?.userId || TENANT_CONSTANTS.ANONYMOUS_USER;
};

/**
 * @function getCurrentRequestId
 * @description Reads the current request id from async local storage or generates a fallback trace.
 * @returns {string} Request or trace identifier.
 * @collaboration Every request needs a trace anchor even when it begins before tenant context hydration.
 */
export const getCurrentRequestId = () => {
  const store = tenantStorage.getStore();
  return store?.requestId || `UNANCHORED-STRIKE-${Date.now()}`;
};

// ============================================================================
// 🏛️ LATE-BINDING LOGGER ANCHOR
// ============================================================================

import { setContextProvider } from '../utils/logger.js';

setContextProvider(() => ({
  tenantId: getCurrentTenantId(),
  userId: getCurrentUserId(),
  requestId: getCurrentRequestId()
}));

// ============================================================================
// 🏛️ DOWNSTREAM NUCLEUS IMPORTS
// ============================================================================

import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import cryptoCore from '../utils/cryptoCore.js';
import { useDatabase } from '../config/database.js';
// 🛡️ SOVEREIGN METRICS: Legacy metrics (backward compatibility) + sovereign counters
import legacyMetrics from '../utils/metrics.js';
import sovereignMetrics from '../metrics/prometheusMetrics.js';

/**
 * Unified metrics interface that uses sovereign counters where available,
 * falling back to legacy metrics for compatibility.
 */
const metrics = {
  increment: (name, value, labels) => {
    // Try to use sovereign metrics if the counter exists, otherwise legacy
    if (sovereignMetrics[name] && typeof sovereignMetrics[name].inc === 'function') {
      sovereignMetrics[name].inc(labels, value);
    } else if (legacyMetrics.increment) {
      legacyMetrics.increment(name, value, labels);
    }
  },
  recordTiming: (name, duration, labels) => {
    if (legacyMetrics.recordTiming) {
      legacyMetrics.recordTiming(name, duration, labels);
    }
  }
};

// ============================================================================
// 🔐 CRYPTOGRAPHIC CONTEXT SEALING
// ============================================================================

/**
 * @function generateContextSeal
 * @description Generates a SHA3-512 seal for a tenant context payload.
 * @param {string} tenantId - Tenant identifier.
 * @param {string} userId - User identifier.
 * @param {string} traceId - Trace/request identifier.
 * @param {number} timestamp - Unix timestamp in milliseconds.
 * @returns {string} Uppercase hex seal.
 * @collaboration Context seals make tenant routing decisions inspectable and tamper-evident.
 */
const generateContextSeal = (tenantId, userId, traceId, timestamp) => {
  const payload = `${tenantId}:${userId}:${traceId}:${timestamp}`;
  return crypto.createHash('sha3-512').update(payload).digest('hex').toUpperCase();
};

/**
 * @function shouldUseLiveContextFallback
 * @description Identifies lightweight OS routes that must keep serving live process truth even when tenant DB anchoring is degraded.
 * @param {Object} req - Express request object.
 * @returns {boolean} True when the route can safely continue with a degraded tenant context.
 * @collaboration Wilson Khanyezi required telemetry and health surfaces to behave like an operating-system heartbeat, not a fragile database report.
 */
const shouldUseLiveContextFallback = (req) => {
  const path = String(req.originalUrl || req.path || '').toLowerCase();
  const method = String(req.method || 'GET').toUpperCase();

  if ([
    '/api/telemetry',
    '/api/status',
    '/api/v1/sovereign-health',
    '/api/v1/boardroom/health',
    '/api/auth/discover',
    '/api/auth/refresh-token',
    '/api/auth/login',
    '/api/auth/register',
    '/api/wilsy-ai/entitlements'
  ].some(route => path.includes(route))) {
    return true;
  }

  if ([
    '/api/forensics/merkle-auditor/run',
    '/api/forensics/validate-chain'
  ].some(route => path.includes(route))) {
    return true;
  }

  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) return false;

  return [
    '/api/billing/summary',
    '/api/billing/analytics',
    '/api/billing/credit-scores',
    '/api/billing/institutional/summary',
    '/api/billing/status',
    '/api/billing/tax-rates',
    '/api/billing/treasury/status',
    '/api/analytics',
    '/api/finance/kpis',
    '/api/finance/currency',
    '/api/revenue/metrics',
    '/api/revenue/ledger',
    '/api/revenue/trajectory',
    '/api/invoices',
    '/api/compliance/metrics',
    '/api/courts',
    '/api/bank/reconciliation',
    '/api/finance/tax-rates',
    '/api/tax/rates',
    '/api/system/tax-rates',
    '/api/treasury/status',
    '/api/treasury/balances',
    '/api/treasury/policy/matrix',
    '/api/treasury/benchmarks/latest',
    '/api/finance/treasury/status',
    '/api/finance/treasury/balances',
    '/api/finance/treasury/policy/matrix',
    '/api/finance/benchmarks/latest',
    '/api/system/treasury/policy/matrix',
    '/api/system/rates/benchmarks',
    '/api/dunning/recommendations',
    '/api/collections/dunning/recommendations',
    '/api/collections/delinquent-list',
    '/api/forensics/metrics',
    '/api/forensics/verify-chain',
    '/api/forensics/blockchain-verify',
    '/api/forensics/merkle-auditor/status',
    '/api/forensics/merkle-auditor/anchors'
  ].some(route => path.includes(route));
};

/**
 * @function runDegradedTenantContext
 * @description Continues the request with a sealed degraded context when non-mutating OS observability routes cannot attach a DB shard.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @param {Function} next - Express next middleware.
 * @param {Object} context - Trace, tenant and timing context.
 * @returns {void}
 * @collaboration Prevents a single unavailable shard from flooding the founder cockpit with 503 telemetry fractures.
 */
const runDegradedTenantContext = (req, res, next, context) => {
  const tenantId = context.tenantId || TENANT_CONSTANTS.DEFAULT_TENANT;
  const userId = context.userId || TENANT_CONSTANTS.ANONYMOUS_USER;
  const contextSeal = generateContextSeal(tenantId, userId, context.traceId, context.contextTimestamp);

  req.db = null;
  req.tenantId = tenantId;
  req.tenantContextStatus = 'DEGRADED_NO_DB';
  res.setHeader('X-Wilsy-Tenant-ID', tenantId);
  res.setHeader('X-Wilsy-Trace-ID', context.traceId);
  res.setHeader('X-Wilsy-Context-Seal', contextSeal);
  res.setHeader('X-Wilsy-Context-Status', 'DEGRADED_NO_DB');

  return tenantStorage.run({
    tenantId,
    userId,
    requestId: context.traceId,
    contextSeal,
    contextTimestamp: context.contextTimestamp,
    startTime: context.startFetch,
    db: null,
    degraded: true
  }, () => next());
};

/**
 * @function verifyContextSeal
 * @description Verifies a provided context seal against the computed tenant context seal.
 * @param {string} tenantId - Tenant identifier.
 * @param {string} userId - User identifier.
 * @param {string} traceId - Trace/request identifier.
 * @param {number} timestamp - Unix timestamp in milliseconds.
 * @param {string} providedSeal - Seal to verify.
 * @returns {boolean} True when seals match.
 * @collaboration Gives downstream services a reusable proof check before trusting propagated tenant context.
 */
export const verifyContextSeal = (tenantId, userId, traceId, timestamp, providedSeal) => {
  const computedSeal = generateContextSeal(tenantId, userId, traceId, timestamp);
  return computedSeal === providedSeal;
};

// ============================================================================
// 🧬 RUN WITH CONTEXT
// ============================================================================

/**
 * @function runWithContext
 * @description Executes a function within a sealed tenant context.
 * @param {Object} context - Context object with tenantId, userId, requestId and optional db.
 * @param {Function} fn - Async function to execute.
 * @returns {Promise<any>} Result of fn.
 * @collaboration Shared jobs and workers need the same tenant context discipline as HTTP routes.
 */
export const runWithContext = async (context, fn) => {
  const tenantId = context.tenantId || TENANT_CONSTANTS.DEFAULT_TENANT;
  const userId = context.userId || TENANT_CONSTANTS.ANONYMOUS_USER;
  const traceId = context.requestId || context.traceId || `TRC-SYS-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
  const timestamp = Date.now();

  const db = context.db || await useDatabase(tenantId);
  const contextSeal = generateContextSeal(tenantId, userId, traceId, timestamp);

  return tenantStorage.run(
    {
      tenantId,
      userId,
      requestId: traceId,
      contextSeal,
      contextTimestamp: timestamp,
      startTime: performance.now(),
      db,
      ...context,
    },
    fn
  );
};

// ============================================================================
// 🛡️ TENANT CONTEXT MIDDLEWARE
// ============================================================================

/**
 * @function tenantContext
 * @description Express middleware that isolates each request to its tenant database shard and provides degraded read context when DB is unavailable.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @param {Function} next - Express next middleware.
 * @returns {Promise<void>|void} Resolves when the request has been passed to the next middleware.
 * @collaboration This is the operating-system boundary between tenant isolation and productive degraded dashboards during infrastructure recovery.
 */
export const tenantContext = async (req, res, next) => {
  const startFetch = performance.now();
  const contextTimestamp = Date.now();

  if (typeof next !== 'function') {
    console.error(chalk.bgRed('[CONTEXT-PANIC] 🚨 Middleware chain fracture.'));
    return;
  }

  // 🔗 UNIFIED TRACE CORRELATION
  const traceId = req.headers['x-trace-id'] ||
                  req.headers['x-request-id'] ||
                  req.traceId ||
                  `TRC-REQ-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;

  req.traceId = traceId;

  // 🔥 CRITICAL: Early bypass for all authentication routes
  const isAuthRoute =
    req.path.includes('/api/auth/login') ||
    req.path.includes('/api/auth/webauthn-challenge') ||
    req.path.includes('/api/auth/verify3FA') ||
    req.path.includes('/api/auth/verify-3fa') ||
    req.path.includes('/api/auth/register');

  if (isAuthRoute) {
    req.tenantId = TENANT_CONSTANTS.DEFAULT_TENANT;
    try {
      req.db = await useDatabase(TENANT_CONSTANTS.DEFAULT_TENANT);
    } catch (error) {
      console.warn(chalk.yellow(`[SYSTEM] ⚠️ Auth context DB fallback active: ${error.message}`));
      return runDegradedTenantContext(req, res, next, {
        tenantId: TENANT_CONSTANTS.DEFAULT_TENANT,
        userId: TENANT_CONSTANTS.ANONYMOUS_USER,
        traceId,
        contextTimestamp,
        startFetch
      });
    }

    // 📊 LOG AUTH CONTEXT INITIALIZATION (sovereign counter)
    metrics.increment('telemetry_events_total', 1, { tenantId: req.tenantId, eventType: 'AUTH_CONTEXT_INIT' });

    return tenantStorage.run({
      tenantId: req.tenantId,
      userId: TENANT_CONSTANTS.ANONYMOUS_USER,
      requestId: traceId,
      startTime: startFetch,
      db: req.db
    }, () => next());
  }

  // 🏛️ TENANT DISCOVERY
  let incomingTenantId = req.headers['x-tenant-id'] || req.headers['X-Tenant-ID'] ||
                 req.body?.tenantId ||
                 req.query.tenantId;

  // 🔥 MARS PROTOCOL FIX: Intercept unanchored/GLOBAL_ROOT headers immediately
  let tenantId = incomingTenantId;
  if (!tenantId || tenantId === 'undefined' || tenantId === 'null' || tenantId === 'GLOBAL_ROOT') {
    tenantId = TENANT_CONSTANTS.DEFAULT_TENANT;
  }

  const userId = req.user?.id || req.user?._id || TENANT_CONSTANTS.ANONYMOUS_USER;

  if (!isDatabaseAnchored() && shouldUseLiveContextFallback(req)) {
    return runDegradedTenantContext(req, res, next, {
      tenantId,
      userId,
      traceId,
      contextTimestamp,
      startFetch
    });
  }

  try {
    let db;
    try {
      // Wrap useDatabase to prevent a thrown exception from skipping our fallback logic
      db = await useDatabase(tenantId);
    } catch (shardErr) {
      console.warn(chalk.yellow(`[SYSTEM] ⚠️ Shard Exception for ${tenantId}: ${shardErr.message}. Forcing Sovereign Root fallback.`));
      db = null; // Let the fallback handle it
    }

    if (!db) {
      console.warn(chalk.yellow(`[SYSTEM] ⚠️ Shard Link Failed: ${tenantId}. Re-anchoring to Sovereign Root.`));
      req.db = await useDatabase(TENANT_CONSTANTS.DEFAULT_TENANT);
      req.tenantId = TENANT_CONSTANTS.DEFAULT_TENANT;

      // 📊 LOG RECOVERY ROUTING (sovereign counter)
      metrics.increment('telemetry_integrity_failures_total', 1, { tenantId: 'GLOBAL_ROOT', type: 'TENANT_ROUTING_RECOVERY' });

      broadcastTelemetry("GLOBAL_ROOT", "AUDIT_EVENT", "TENANT_RECOVERY_ROUTING", "TenantContext", {
        traceId,
        attemptedTenant: tenantId,
        fallbackTenant: TENANT_CONSTANTS.DEFAULT_TENANT,
        severity: 'ELEVATED'
      });
    } else {
      req.db = db;
      req.tenantId = tenantId;
    }

    // ⚖️ COMPLIANCE OVERLAYS & POPIA REDACTION
    let complianceFlags = { POPIA: 'POPIA_CLEAN', GDPR: 'COMPLIANT' };
    if (TENANT_CONSTANTS.POPIA_STRICT_MODE && req.body && Object.keys(req.body).length > 0) {
      const redacted = cryptoCore.redact ? cryptoCore.redact(req.body) : { data: req.body, metadata: { complianceStatus: 'BYPASSED' } };
      req.body = redacted.data;
      complianceFlags.POPIA = redacted.metadata.complianceStatus;
    }

    const contextSeal = generateContextSeal(req.tenantId, userId, traceId, contextTimestamp);

    // 🔬 SEAL PARITY DIAGNOSTICS
    const clientSeal = req.headers['x-client-seal'];
    if (process.env.NODE_ENV === 'development' && clientSeal && clientSeal !== contextSeal) {
      console.warn(chalk.magenta(`[SEAL-PARITY-WARNING] Mismatch Detected. Client: ${clientSeal} | Engine: ${contextSeal}`));
    }

    // 🛰️ OBSERVABILITY HEADERS
    res.setHeader('X-Wilsy-Tenant-ID', req.tenantId);
    res.setHeader('X-Wilsy-Trace-ID', traceId);
    res.setHeader('X-Wilsy-Context-Seal', contextSeal);

    const store = {
      tenantId: req.tenantId,
      userId,
      requestId: traceId,
      contextSeal,
      contextTimestamp,
      startTime: startFetch,
      db: req.db
    };

    // ⏱️ RECORD CONTEXT INITIALIZATION LATENCY
    const latencyMs = Number((performance.now() - startFetch).toFixed(2));
    metrics.recordTiming('latency_tenant_context_init', latencyMs, { tenantId: req.tenantId });

    // 📡 HIGH-RES SLA TELEMETRY ANCHOR WITH BOARDROOM OVERLAYS
    const breakerState = global.circuitBreakerState || 'CLOSED_OPTIMAL';

    broadcastTelemetry(req.tenantId, "SYSTEM_EVENT", "TENANT_CONTEXT_INIT", "TenantContext", {
      traceId,
      userId,
      route: req.path,
      seal: contextSeal.substring(0, 16),
      latencyMs,
      compliance: complianceFlags,
      boardroomOverlays: {
        breakerState,
        slaStatus: latencyMs < 50 ? 'MET' : 'DEGRADED',
        anomalyIndex: 0
      }
    });

    // 🧊 COLD STORAGE ARCHIVE HOOK
    broadcastTelemetry("GLOBAL_ROOT", "AUDIT_EVENT", "COLD_STORAGE_ARCHIVE", "TenantContext", {
      traceId,
      seal: contextSeal,
      tenantId: req.tenantId,
      timestamp: contextTimestamp
    });

    return tenantStorage.run(store, () => next());

  } catch (error) {
    console.error(chalk.bgRed(`[CONTEXT-FRACTURE] 🚨 ${error.message}`));
    const latencyMs = Number((performance.now() - startFetch).toFixed(2));

    if (shouldUseLiveContextFallback(req)) {
      return runDegradedTenantContext(req, res, next, {
        tenantId: tenantId || TENANT_CONSTANTS.DEFAULT_TENANT,
        userId,
        traceId,
        contextTimestamp,
        startFetch
      });
    }

    // 📊 LOG PANIC FRACTURE (sovereign counter)
    metrics.increment('system_errors_total', 1, { tenantId: 'GLOBAL_ROOT', severity: 'CRITICAL', type: 'CONTEXT_FRACTURE' });

    // 📡 CRITICAL PANIC ESCALATION
    broadcastTelemetry("GLOBAL_ROOT", "SYSTEM_EVENT", "DB_PANIC", "TenantContext", {
      traceId,
      attemptedTenant: incomingTenantId || 'UNKNOWN',
      error: error.message,
      latencyMs,
      severity: 'CRITICAL'
    });

    return res.status(503).json({
      success: false,
      message: "QUANTUM_LINK_RESTORING",
      traceId
    });
  }
};

// ============================================================================
// 📤 ALIASES FOR BACKWARD COMPATIBILITY
// ============================================================================

export const getCurrentTenant = getCurrentTenantId;
export const getCurrentUser = getCurrentUserId;

export default tenantContext;
