/* eslint-disable */

/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                                                                                        ║
 * ║   ██╗    ██╗██╗██╗     ███████╗██╗   ██╗    ██████╗ ███████╗     ██████╗ ███████╗                                               ║
 * ║   ██║    ██║██║██║     ██╔════╝╚██╗ ██╔╝    ██╔══██╗██╔════╝    ██╔═══██╗██╔════╝                                               ║
 * ║   ██║ █╗ ██║██║██║     ███████╗ ╚████╔╝     ██████╔╝█████╗      ██║   ██║███████╗                                               ║
 * ║   ██║███╗██║██║██║     ╚════██║  ╚██╔╝      ██╔══██╗██╔══╝      ██║   ██║╚════██║                                               ║
 * ║   ╚███╔███╔╝██║███████╗███████║   ██║       ██████╔╝███████╗    ╚██████╔╝███████║                                               ║
 * ║    ╚══╝╚══╝ ╚═╝╚══════╝╚══════╝   ╚═╝       ╚═════╝ ╚══════╝     ╚═════╝ ╚══════╝                                               ║
 * ║                                                                                                                                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * 🏛️ WILSY OS - CORE APPLICATION NUCLEUS [V72.0.0-PRODUCTION]
 * [LATENCY SNIPER | CIRCUIT BREAKER | BINARY STRIKE AUDIT | BOARDROOM KPIS | SOVEREIGN MONITORING]
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 72.0.0-PRODUCTION | PRODUCTION READY | TRILLION DOLLAR SPEC                                                                   ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/app.js                                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated production‑ready middleware stack without temporary debuggers.                       ║
 * ║ • AI Engineering (DeepSeek) – FINAL: Cleaned app.js; added full JSDoc; integrityShield handles forensic mismatch logging internally.   ║
 * ║ • AI Engineering (DeepSeek) – ENHANCED: Mounted sovereignRoutes (TelemetryMesh + Regulator ETL) under /monitoring.                     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import { generateSovereignArtifactPdf } from './controllers/businessArtifactPdfController.js';

import helmet from 'helmet';
import morgan from 'morgan';
import chalk from 'chalk';
import rateLimit from 'express-rate-limit';
import mongoose from 'mongoose';
import os from 'os';

// 🏛️ SOVEREIGN IMPORTS
import { tenantContext } from './middleware/tenantContext.js';
import { integrityShield } from './middleware/ProductionHardening.middleware.js';

import metrics from './utils/metrics.js';
import routes from './routes/api.js';
import forensicRoutes from './routes/forensicRoutes.js';
import sovereignRoutes from './routes/sovereignRoutes.js'; // 🆕 Sovereign monitoring & regulator API
import auditLogger from './utils/auditLogger.js';
import { broadcastTelemetry, getTelemetryState } from './utils/telemetryHelper.js';
import { breakerRegistry } from './utils/circuitBreaker.js';
import { checkRedisHealth } from './config/redis.js';

const app = express();

// ============================================================================
// 🔥 SOVEREIGN CORS FORTRESS - EARLY & SECURE
// ============================================================================

/**
 * @middleware corsMiddleware
 * @description Configures Cross-Origin Resource Sharing (CORS) for the sovereign dashboard.
 * Allows only trusted localhost origins, and exposes custom forensic headers.
 * @param {Object} req - Express request
 * @param {Object} res - Express response
 * @param {Function} next - Express next middleware
 */
/**
 * @function corsMiddleware
 * @description Applies Wilsy OS CORS policy for browser, proxy, and local development API traffic.
 * @collaboration Supports frontend Vite proxy, auth routes, telemetry routes, and protected backend services.
 */
const corsMiddleware = (req, res, next) => {
  const origin = req.headers.origin;
  const allowedOrigins = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3001',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
  ];

  if (allowedOrigins.includes(origin)) {
    res.header('Access-Control-Allow-Origin', origin);
  } else {
    res.header('Access-Control-Allow-Origin', 'http://localhost:3000');
  }

  res.header('Access-Control-Allow-Credentials', 'true');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH');
  res.header(
    'Access-Control-Allow-Headers',
    'Origin, X-Requested-With, Content-Type, Accept, Authorization, X-Tenant-ID, x-tenant-id, X-Tenant-Id, x-tenant-id, X-Request-ID, x-request-id, X-Trace-ID, x-trace-id, X-Correlation-ID, x-correlation-id, X-Forensic-Timestamp, x-forensic-timestamp, X-Cryptographic-Nonce, x-cryptographic-nonce, X-Request-Seal, x-request-seal, X-Request-Proof, x-request-proof, X-Artifact-Type, x-artifact-type, X-Wilsy-Tenant-ID, x-wilsy-tenant-id, X-Wilsy-Artifact-Type, x-wilsy-artifact-type, X-Binary-Strike, x-binary-strike, X-Quantum-Verified, x-quantum-verified, X-Wilsy-Account-Client, x-wilsy-account-client, X-Wilsy-Account-Command, x-wilsy-account-command, X-Wilsy-Client, x-wilsy-client'
  );
  res.header(
    'Access-Control-Expose-Headers',
    'X-Institutional-Latency, X-Forensic-Trace, X-Artifact-Seal, X-Request-Proof, X-Wilsy-Trace-ID, X-Wilsy-Merkle-Root, X-Wilsy-Tenant-ID, X-Wilsy-Artifact-Type'
  );
  res.header('Access-Control-Max-Age', '86400');

  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
};

app.use(corsMiddleware);

/**
 * @route POST /api/generate/pdf
 * @description Scoped DB-free branded artifact ingress mounted immediately after CORS.
 * @returns {Promise<void>} Streams a branded Wilsy OS artifact PDF.
 * @collaboration Bypasses heavy tenant/global middleware for artifact export while preserving JWT and proof verification inside the controller.
 */
app.post('/api/generate/pdf', express.json({ limit: '10mb' }), generateSovereignArtifactPdf);

// ============================================================================
// 🛡️ PUBLIC HEALTH PROBES (BYPASS AUTH & RATE LIMITING)
// ============================================================================

/**
 * @route GET /api/status
 * @description Simple health check endpoint for load balancers.
 * @returns {Object} { status: "OK", timestamp }
 */
app.get('/api/status', (req, res) => {
  res.status(200).json({ status: 'OK', timestamp: new Date().toISOString() });
});

/**
 * @route POST /api/telemetry/pulse
 * @description Accepts telemetry pings without requiring authentication.
 * @returns {Object} { status: "ACCEPTED" }
 */
app.post('/api/telemetry/pulse', (req, res) => {
  res.status(202).json({ status: 'ACCEPTED' });
});

// ============================================================================
// ⚡ LATENCY SNIPER & BINARY STRIKE AUDIT
// ============================================================================

/**
 * @middleware latencySniper
 * @description Measures request duration, injects latency headers, and records SLA metrics.
 * Logs a warning if response time exceeds 500ms.
 */
/**
 * @function latencySniper
 * @description Measures request latency and surfaces slow-strike warnings without changing response semantics.
 * @collaboration Supports observability, SLA telemetry, and backend route performance for Wilsy OS.
 */
const latencySniper = (req, res, next) => {
  const start = process.hrtime();
  const tenantId = req.headers['x-tenant-id'] || 'GLOBAL_ROOT';

  // Skip health probes to reduce noise
  if (
    req.originalUrl.includes('/telemetry/pulse') ||
    req.originalUrl === '/api/status' ||
    req.originalUrl.includes('/api/source-registry/health') ||
    req.originalUrl.includes('/api/source-registry/status')
  )
    return next();

  const originalEnd = res.end;
  res.end = function (chunk, encoding, callback) {
    if (!res.headersSent) {
      const diff = process.hrtime(start);
      const timeInMs = Number((diff[0] * 1e3 + diff[1] * 1e-6).toFixed(3));

      res.setHeader('X-Institutional-Latency', `${timeInMs}ms`);
      res.setHeader('X-Forensic-Trace', req.headers['x-trace-id'] || 'SYSTEM_ROOT');

      metrics.recordTiming('latency_request_latency', timeInMs, {
        tenantId,
        method: req.method,
        endpoint: req.originalUrl,
        threshold: 500,
      });

      if (timeInMs > 500) {
        console.warn(
          chalk.yellow(
            `[SLA-WARNING] Slow Strike Detected: ${req.method} ${req.originalUrl} - ${timeInMs}ms`
          )
        );
      }
    }
    originalEnd.call(this, chunk, encoding, callback);
  };
  next();
};

app.use(latencySniper);

// ============================================================================
// 🔒 INSTITUTIONAL RATE LIMITING
// ============================================================================

/**
 * @const sovereignLimiter
 * @description Rate limiter that applies to all /api endpoints.
 * Limits each tenant/IP to 2000 requests per 15 minutes.
 */
const sovereignLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 2000,
  keyGenerator: (req) => req.headers['x-tenant-id'] || req.ip,
  handler: (req, res) =>
    res.status(429).json({ success: false, message: 'Institutional Threshold Reached.' }),
});
app.use('/api/', sovereignLimiter);

// ============================================================================
// 🛡️ SECURITY HARDENING & CONTEXT
// ============================================================================

app.use(helmet({ contentSecurityPolicy: false }));
app.use(express.json({ limit: '100mb' }));
app.use(express.urlencoded({ extended: true, limit: '100mb' }));

if (process.env.NODE_ENV === 'development') app.use(morgan('dev'));

// 🏛️ Tenant context (injects tenantId into req)
app.use(tenantContext);

// 🛡️ Integrity Shield – validates cryptographic seals and rejects tampered requests.
// On failure, it logs the expected vs received seal (production forensic logging).
app.use(integrityShield);

// ============================================================================
// 🚀 BOARDROOM HEALTH CHECK (SLA DASHBOARD)
// ============================================================================

/**
 * @route GET /api/v1/sovereign-health
 * @description Returns detailed system health including Redis, circuit breakers, and KPIs.
 * Used by the Boardroom HUD to display institutional health.
 */
app.get('/api/v1/sovereign-health', async (req, res) => {
  try {
    const breakers = breakerRegistry ? breakerRegistry.getAllStatus() : {};
    const redisHealth = checkRedisHealth
      ? await checkRedisHealth()
      : { status: 'OFFLINE', latency: 0 };
    const snapshot = metrics.getSnapshot ? metrics.getSnapshot() : { metrics: { performance: {} } };
    const telemetryState = getTelemetryState ? getTelemetryState() : { queueLength: 0 };

    res.status(200).json({
      status: 'OPTIMAL',
      uptime: process.uptime(),
      timestamp: new Date().toISOString(),
      version: '72.0.0-PRODUCTION',
      boardroom: {
        redisStatus: redisHealth.status || 'UNKNOWN',
        redisLatencyMs: redisHealth.latency || 0,
        activeBreakers: Object.keys(breakers).length,
        coldStorageQueueSize: telemetryState.queueLength || 0,
        kpi: {
          slaScore: snapshot.metrics?.performance?.latency_request_latency?.p95 || 0,
          riskIndex: snapshot.metrics?.performance?.latency_request_latency?.p99 || 0,
        },
      },
    });
  } catch (err) {
    res.status(500).json({ status: 'FRACTURED', error: err.message });
  }
});

/**
 * @function isWilsyPublicForensicGatewayPath
 * @description Detects forensic Merkle gateway endpoints that are intentionally public in development/showroom mode.
 * @collaboration Prevents auth-debug noise on approved read/showroom proof endpoints while preserving real auth enforcement elsewhere.
 */
const isWilsyPublicForensicGatewayPath = (req = {}) => {
  const url = String(req.originalUrl || req.url || '').toLowerCase();
  const method = String(req.method || 'GET').toUpperCase();

  const publicReadPaths = [
    '/api/forensics/verify-chain',
    '/api/forensics/merkle-auditor/status',
    '/api/forensics/merkle-auditor/anchors',
  ];

  if (
    ['GET', 'HEAD', 'OPTIONS'].includes(method) &&
    publicReadPaths.some((path) => url.startsWith(path))
  ) {
    return true;
  }

  return method === 'POST' && url.startsWith('/api/forensics/merkle-auditor/run');
};

// ============================================================================
// 🔍 FORENSIC DEBUG MIDDLEWARE (Auth-only, no payload dump – production friendly)
// ============================================================================

/**
 * @middleware ForensicAuthLogger
 * @description Logs missing or malformed Authorization headers for all /api endpoints.
 * This is a lightweight, production‑safe logger that does not alter request processing.
 */
app.use((req, res, next) => {
  if (req.originalUrl.includes('/api/')) {
    const publicTelemetryPaths = [
      '/api/telemetry/event',
      '/api/telemetry/pulse',
      '/api/telemetry/error',
      '/api/auth/discover',
      '/api/auth/login',
      '/api/auth/verify-3fa',
      '/api/auth/register',
      '/api/auth/refresh-token',
      '/api/auth/me',
    ];
    if (
      publicTelemetryPaths.some((path) => req.originalUrl.startsWith(path)) ||
      isWilsyPublicForensicGatewayPath(req)
    ) {
      return next();
    }

    const auth = req.headers['authorization'];
    const tenant = req.headers['x-tenant-id'];

    if (!auth || auth === 'Bearer null' || auth === 'Bearer undefined') {
      console.log(chalk.red.bold(`[FORENSIC-AUTH] 🚨 Missing/Invalid Auth on ${req.originalUrl}`));
      console.log(chalk.yellow(`  Auth: ${auth} | Tenant: ${tenant}`));
    }
  }
  next();
});

// ============================================================================
// 🚀 MASTER ROUTE DISPATCH
// ============================================================================
app.use('/api', routes);
app.use('/api/forensics', forensicRoutes);

// 🆕 SOVEREIGN MONITORING ROUTER (TelemetryMesh + Regulator ETL)
// Mounted under /monitoring to avoid conflicts with existing /api routes.
// Exposes:
//   GET /monitoring/metrics          – Prometheus metrics (authenticated)
//   GET /monitoring/api/regulator/bundles – Regulator audit bundles (authenticated + scoped)
app.use('/monitoring', sovereignRoutes);

// ============================================================================
// 🏛️ INSTITUTIONAL GLOBAL ERROR INTERCEPTOR
// ============================================================================

/**
 * @middleware globalErrorHandler
 * @description Catches any unhandled errors, broadcasts telemetry, and returns a structured
 * forensic error response. Prevents stack traces from leaking to the client.
 */
app.use(async (err, req, res, next) => {
  const traceId = req.headers['x-trace-id'] || 'SYSTEM_FRACTURE';
  const tenantId = req.headers['x-tenant-id'] || 'GLOBAL_ROOT';

  metrics.increment('system_errors_total', 1, { tenantId, severity: 'HIGH' });

  broadcastTelemetry(tenantId, 'SYSTEM_EVENT', 'GATEWAY_ERROR', 'AppCore', {
    traceId,
    error: err.message,
  });

  if (!res.headersSent) {
    res.status(err.status || 500).json({
      success: false,
      message: 'Institutional Finality Breach.',
      forensics: { traceId, timestamp: new Date().toISOString(), shard: tenantId },
    });
  }
});

export default app;
