/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ 🏛️ WILSY OS – SOVEREIGN RUNTIME BOOTSTRAPPER [v5.6.0-R10E17-RECOVERY-CONTACT-VERIFICATION-INTERNAL-MOUNT]                            ║
 * ║ TITLE: Transport-only BFF with separated internal recovery delivery ingress                                                      ║
 * ║ AUTHORITY: Wilsy OS Core Governance; Node transport only                                                                           ║
 * ║ TENANT BOUNDARY: Forward authenticated tenant scope without deriving membership                                                   ║
 * ║ AUTHORITY BOUNDARY: No C1C/C1E/legal/financial authority is interpreted or created                                                ║
 * ║ FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution                                                      ║
 * ║ EPITOME: Production BFF preserving raw proxy order plus dedicated authenticated password-recovery and contact-verification ingress. ║
 * ║          Uses http-proxy-middleware for all Kennel routes, including billing.                                                       ║
 * ║          Raw request streams are forwarded – no body consumption issues.                                                            ║
 * ║ COMPLIANCE: POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: v5.6.0-R10E17-RECOVERY-CONTACT-VERIFICATION-INTERNAL-MOUNT | PRODUCTION READY                                               ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/server.js                                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 CHANGE LOG (v5.6.0-R10E17-RECOVERY-CONTACT-VERIFICATION-INTERNAL-MOUNT):                                                             ║
 * ║   2026-09-22 – Mounted a separately keyed HMAC recovery-contact verification delivery bridge beside password recovery.            ║
 * ║   2026-09-22 – Mounted the HMAC-authenticated internal password-recovery delivery bridge after JSON parsing and outside auth proxy. ║
 * ║   2026-09-17 – Added bounded legal-acceptance status/document/accept transport; Node remains transport-only.                         ║
 * ║   2026-09-17 – Added only the certified C1C legal-services and C1E advisory selective proxies.                                      ║
 * ║   2026-09-17 – Added deterministic application-factory export and direct-execution bootstrap guard.                                 ║
 * ║   2026-08-24 – Preserved raw-stream proxy ordering before body parsers.                                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ CERTIFICATION SEAL: PRODUCTION_READY_v5.6.0-R10E17-RECOVERY-CONTACT-VERIFICATION-INTERNAL-MOUNT                                      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import fileUpload from 'express-fileupload';
import { createServer } from 'node:http';
import mongoose from 'mongoose';
import { generateSovereignArtifactPdf } from './controllers/businessArtifactPdfController.js';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import passwordRecoveryDeliveryRouter from './routes/passwordRecoveryDelivery.js';
import recoveryContactVerificationDeliveryRouter from './routes/recoveryContactVerificationDelivery.js';

// ─── CONSTANTS ──────────────────────────────────────────────────────────────
const KENNEL_TARGET = (
  process.env.KENNEL_URL ||
  process.env.KENNEL_EOS_URL ||
  'http://127.0.0.1:9095'
).replace(/\/$/, '');
const PROXY_LOG_LEVEL = process.env.WILSY_PROXY_DEBUG === '1' ? 'debug' : 'info';
const VERSION = 'v5.6.0-R10E17-RECOVERY-CONTACT-VERIFICATION-INTERNAL-MOUNT';
const BUILD = VERSION;
const BILLING_PROXY_TIMEOUT_MS = Number(process.env.KENNEL_BILLING_TIMEOUT_MS || 60000);
const DEFAULT_PROXY_TIMEOUT_MS = Number(process.env.KENNEL_PROXY_TIMEOUT_MS || 30000);

/**
 * Rebuild Kennel path after Express strips the mount prefix.
 */
function rewriteMountedPath(path, targetPrefix) {
  let pathname = path || '';
  let query = '';
  const qIdx = pathname.indexOf('?');
  if (qIdx >= 0) {
    query = pathname.slice(qIdx);
    pathname = pathname.slice(0, qIdx);
  }
  if (!pathname || pathname === '/') {
    return `${targetPrefix}${query}`;
  }
  const suffix = pathname.startsWith('/') ? pathname : `/${pathname}`;
  return `${targetPrefix}${suffix}${query}`;
}

/**
 * Forward institutional headers to Kennel (dual‑case tenant + idempotency).
 */
function forwardInstitutionalHeaders(proxyReq, req) {
  const h = req.headers || {};
  const tenantId =
    h['x-tenant-id'] ||
    h['x-wilsy-tenant'] ||
    h['x-tenant'] ||
    h['x-wilsy-tenant-id'] ||
    req.tenantId ||
    null;
  if (tenantId) {
    proxyReq.setHeader('X-Tenant-ID', tenantId);
    proxyReq.setHeader('X-Tenant-Id', tenantId);
    proxyReq.setHeader('x-tenant-id', tenantId);
  }
  const idem =
    h['idempotency-key'] || h['x-idempotency-key'] || h['x-wilsy-idempotency-key'] || null;
  if (idem) {
    proxyReq.setHeader('Idempotency-Key', idem);
    proxyReq.setHeader('X-Idempotency-Key', idem);
    proxyReq.setHeader('X-Wilsy-Idempotency-Key', idem);
  }
  if (h.authorization) {
    proxyReq.setHeader('Authorization', h.authorization);
  }
  if (h['x-trace-id']) {
    proxyReq.setHeader('X-Trace-ID', h['x-trace-id']);
  }
  if (h['x-request-id']) {
    proxyReq.setHeader('X-Request-ID', h['x-request-id']);
  }
}

/**
 * Build a proxy middleware for a given mount prefix.
 * Uses http-proxy-middleware – handles raw streams correctly when placed before body parsers.
 */
function buildKennelProxy({ mountPrefix, targetPrefix, timeoutMs }) {
  const timeout = timeoutMs || DEFAULT_PROXY_TIMEOUT_MS;
  return createProxyMiddleware({
    target: KENNEL_TARGET,
    changeOrigin: true,
    logLevel: PROXY_LOG_LEVEL,
    proxyTimeout: timeout,
    timeout,
    connectTimeout: 5000,
    pathRewrite: (path) => {
      const rewritten = rewriteMountedPath(path, targetPrefix);
      if (process.env.WILSY_PROXY_DEBUG === '1') {
        console.log(`[PROXY-REWRITE] mount=${mountPrefix} path=${path} → ${rewritten}`);
      }
      return rewritten;
    },
    on: {
      proxyReq: (proxyReq, req) => {
        forwardInstitutionalHeaders(proxyReq, req);
        // No need to restream – the stream is still raw because proxy runs before body parsers.
        if (process.env.WILSY_PROXY_DEBUG === '1') {
          console.log(`[PROXY] ${req.method} ${req.originalUrl || req.url} → ${KENNEL_TARGET}`);
        }
      },
      error: (err, req, res) => {
        console.error('[PROXY] Kennel unreachable:', err.message);
        if (!res.headersSent) {
          res.status(503).json({
            success: false,
            error: 'Kennel service unavailable',
            message: err.message,
            timestamp: new Date().toISOString(),
          });
        }
      },
    },
  });
}

/**
 * Build a method- and-shape constrained proxy for the certified legal surfaces.
 * The mounted middleware receives the suffix after `mountPrefix`; only the
 * exact C1C collection route or one C1E advisory-id route is forwarded.
 */
function buildSelectiveLegalProxy({ mountPrefix, targetPrefix, allowed }) {
  const proxy = buildKennelProxy({ mountPrefix, targetPrefix });
  return (req, res, next) => {
    if (!allowed(req.method, req.url || '/')) return next();
    return proxy(req, res, next);
  };
}

// ─── EXPRESS APP FACTORY ──────────────────────────────────────────────────

function createApp() {
  const app = express();

  app.set('trust proxy', 1);

  app.use(helmet({ contentSecurityPolicy: false }));
  app.use(cors({ origin: true, credentials: true }));

  // ─── HEALTH ROUTES (GET, no body) ─────────────────────────────────────
  app.get('/ping', (req, res) =>
    res.json({ status: 'PONG', system: 'WILSY OS BFF', version: BUILD })
  );
  app.get('/api/ping', (req, res) =>
    res.json({
      status: 'PONG',
      system: 'WILSY OS BFF',
      version: BUILD,
      kennelAllTheWay: true,
      kennel: KENNEL_TARGET,
    })
  );
  app.get('/api/billing/ping', (req, res) =>
    res.json({
      status: 'PONG',
      surface: 'BILLING_BFF_PROXY',
      version: BUILD,
      kennelAllTheWay: true,
      kennel: KENNEL_TARGET,
      map: '/api/billing/* → /billing/*',
      timestamp: new Date().toISOString(),
    })
  );
  app.get('/health', (req, res) => {
    const dbState = mongoose.connection.readyState;
    const statusMap = { 0: 'DISCONNECTED', 1: 'CONNECTED', 2: 'CONNECTING', 3: 'DISCONNECTING' };
    res.json({
      status: 'OPTIMAL',
      build: BUILD,
      version: BUILD,
      kennelAllTheWay: true,
      database: statusMap[dbState] || 'UNKNOWN',
      kennel: KENNEL_TARGET,
      mounts: {
        billing: '/api/billing + /billing → Kennel /billing',
        tenants: '/api/tenants + /api/business/tenants → Kennel /api/tenants',
        auth: '/api/auth → Kennel /api/auth',
        subscriptions: '/api/subscriptions → Kennel /api/subscriptions',
        employees: '/api/employees → Kennel /api/employees',
        kernel: '/api/kernel → Kennel /api/kernel',
        plans: '/api/plans → Kennel /api/plans',
      },
      timestamp: new Date().toISOString(),
    });
  });
  app.get('/', (req, res) =>
    res.json({
      status: 'OPERATIONAL',
      system: 'WILSY OS BFF',
      version: BUILD,
      kennelAllTheWay: true,
      kennel: KENNEL_TARGET,
    })
  );

  // ─── PROXY TO KENNEL – MUST RUN BEFORE BODY PARSERS ──────────────────
  // This ensures raw request streams are forwarded untouched.
  app.use('/api/auth', buildKennelProxy({ mountPrefix: '/api/auth', targetPrefix: '/api/auth' }));
  app.use(
    '/api/tenants',
    buildKennelProxy({ mountPrefix: '/api/tenants', targetPrefix: '/api/tenants' })
  );
  app.use(
    '/api/business/tenants',
    buildKennelProxy({ mountPrefix: '/api/business/tenants', targetPrefix: '/api/tenants' })
  );
  app.use(
    '/api/employees',
    buildKennelProxy({ mountPrefix: '/api/employees', targetPrefix: '/api/employees' })
  );
  app.use(
    '/api/kernel',
    buildKennelProxy({ mountPrefix: '/api/kernel', targetPrefix: '/api/kernel' })
  );
  app.use(
    '/api/plans',
    buildKennelProxy({ mountPrefix: '/api/plans', targetPrefix: '/api/plans' })
  );
  app.use(
    '/api/subscriptions',
    buildKennelProxy({ mountPrefix: '/api/subscriptions', targetPrefix: '/api/subscriptions' })
  );
  app.use(
    '/api/billing',
    buildKennelProxy({
      mountPrefix: '/api/billing',
      targetPrefix: '/billing',
      timeoutMs: BILLING_PROXY_TIMEOUT_MS,
    })
  );
  app.use(
    '/billing',
    buildKennelProxy({
      mountPrefix: '/billing',
      targetPrefix: '/billing',
      timeoutMs: BILLING_PROXY_TIMEOUT_MS,
    })
  );
  app.use('/auth', buildKennelProxy({ mountPrefix: '/auth', targetPrefix: '/api/auth' }));

  // C1C/C1E transport-only bridge.  These selective mounts deliberately sit
  // before body parsers so POST streams reach Python EOS byte-for-byte.  Node
  // forwards headers and responses but never interprets advisory semantics.
  app.use(
    '/api/wilsy-ai/legal-services',
    buildSelectiveLegalProxy({
      mountPrefix: '/api/wilsy-ai/legal-services',
      targetPrefix: '/api/wilsy-ai/legal-services',
      allowed: (method, suffix) => {
        const pathOnly = String(suffix || '/').split('?', 1)[0];
        return method === 'POST' && (pathOnly === '/' || pathOnly === '');
      },
    })
  );
  app.use(
    '/api/wilsy-ai/legal-next-actions',
    buildSelectiveLegalProxy({
      mountPrefix: '/api/wilsy-ai/legal-next-actions',
      targetPrefix: '/api/wilsy-ai/legal-next-actions',
      allowed: (method, suffix) => {
        const pathOnly = String(suffix || '/').split('?', 1)[0];
        return (
          (method === 'POST' && (pathOnly === '/' || pathOnly === '')) ||
          (method === 'GET' && /^\/[^/]+$/.test(pathOnly))
        );
      },
    })
  );
  app.use(
    '/api/legal-acceptance',
    buildSelectiveLegalProxy({
      mountPrefix: '/api/legal-acceptance',
      targetPrefix: '/api/legal-acceptance',
      allowed: (method, suffix) => {
        const pathOnly = String(suffix || '/').split('?', 1)[0];
        return (
          (method === 'GET' && (pathOnly === '/status' || /^\/documents\/[^/]+$/.test(pathOnly))) ||
          (method === 'POST' && pathOnly === '/accept')
        );
      },
    })
  );

  // ─── BODY PARSERS – AFTER PROXIES ──────────────────────────────────────
  // These will parse bodies for any local routes that need them (currently none).
  app.use(express.json({ limit: '50mb' }));
  app.use(express.urlencoded({ extended: true, limit: '50mb' }));
  app.use(fileUpload({ limits: { fileSize: 50 * 1024 * 1024 }, useTempFiles: false }));

  // Internal recovery transport ingress. These routes are deliberately local
  // to the Node BFF, after JSON parsing and outside the public /api/auth proxy.
  // Each bridge owns only its dedicated HMAC authentication and SMTP delegation;
  // Python EOS retains recovery issuance, recovery-contact verification,
  // lifecycle, credential, principal, and tenant authority.
  app.use('/internal/auth', passwordRecoveryDeliveryRouter);
  app.use('/internal/auth', recoveryContactVerificationDeliveryRouter);

  /**
   * @route POST /api/generate/pdf
   * @description Preserves the tenant-branded, sealed Node PDF renderer while the money surface is proxied to Kennel EOS.
   * @collaboration Keeps binary artifact ownership in the BFF and billing lifecycle ownership in Kennel without routing conflicts.
   */
  app.post('/api/generate/pdf', generateSovereignArtifactPdf);

  // ─── CATCH‑ALL FOR UNPROXIED /api ROUTES ──────────────────────────────
  app.use('/api', (req, res) => {
    res.status(404).json({
      success: false,
      error: 'BFF_ROUTE_NOT_PROXIED',
      message:
        `No selective Kennel proxy for ${req.method} /api${req.url}. ` +
        'Owned prefixes: /api/auth, /api/tenants, /api/business/tenants, /api/employees, /api/kernel, /api/plans, /api/subscriptions, /api/billing → /billing, exact legal-acceptance routes, and exact C1C/C1E legal-advisory routes.',
      path: `/api${req.url}`,
      timestamp: new Date().toISOString(),
    });
  });

  app.use((err, req, res, next) => {
    console.error('[WILSY] BFF Error:', err.message, err.stack);
    res.status(err.statusCode || 500).json({
      success: false,
      error: err.message || 'Internal Server Error',
      timestamp: new Date().toISOString(),
    });
  });

  return app;
}

// ─── RUNTIME BOOTSTRAPPER ─────────────────────────────────────────────────

async function main() {
  console.log(`[WILSY] 🏛️ Sovereign Runtime Bootstrap (v${BUILD})`);

  const app = createApp();
  const httpServer = createServer(app);

  const mongoUri = process.env.MONGODB_URI || process.env.MONGO_URI || '';
  if (mongoUri) {
    console.log('[WILSY] 📡 Connecting to MongoDB...');
    try {
      await mongoose.connect(mongoUri, {
        maxPoolSize: 10,
        serverSelectionTimeoutMS: 5000,
      });
      console.log('[WILSY] ✅ MongoDB connection established.');
    } catch (err) {
      console.warn(`[WILSY] ⚠️ MongoDB connection failed: ${err.message}`);
      console.warn('[WILSY] BFF will continue in proxy‑only mode.');
    }
  } else {
    console.warn('[WILSY] ⚠️ No MongoDB URI provided – /health will report UNKNOWN.');
  }

  const configuredPort = Number(process.env.PORT) || 4000;
  let actualPort = configuredPort;
  let serverStarted = false;

  console.log(`[WILSY] 🔒 Securing TCP Port (starting at ${configuredPort})...`);

  while (!serverStarted) {
    try {
      await new Promise((resolve, reject) => {
        httpServer.once('error', (err) => {
          if (err.code === 'EADDRINUSE') {
            console.warn(`[WILSY] ⚠️ Port ${actualPort} is occupied. Trying ${actualPort + 1}...`);
            actualPort += 1;
            try {
              httpServer.close();
            } catch (_) {
              /* ignore */
            }
            reject(new Error('Port in use'));
          } else {
            reject(err);
          }
        });

        httpServer.listen(actualPort, () => {
          serverStarted = true;
          resolve();
        });
      });
    } catch (err) {
      if (err.message === 'Port in use') continue;
      throw err;
    }
  }

  const dbStatus = mongoose.connection.readyState === 1 ? 'CONNECTED' : 'DEGRADED';
  console.log(`
╔══════════════════════════════════════════════════════════════════════════════════╗
║  ✅ WILSY OS SOVEREIGN RUNTIME                                                  ║
║  ──────────────────────────────────────────────────────────────────────────────── ║
║  Build:     ${BUILD}
║  Database:  ${dbStatus}
║  HTTP:      http://localhost:${actualPort}
║  Health:    http://localhost:${actualPort}/health
║  Proxy:     ${KENNEL_TARGET}
║  Map:       /api/auth|tenants|business/tenants|employees|kernel|plans|subscriptions
║             /api/billing → /billing (http-proxy-middleware, ${BILLING_PROXY_TIMEOUT_MS}ms timeout)
║  Fix:       Proxy middleware order fixed – proxies run BEFORE body parsers.
║  ──────────────────────────────────────────────────────────────────────────────── ║
║  🏛️  Governance: POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
  `);

  const shutdown = async (signal) => {
    console.log(`\n[WILSY] Received ${signal}. Shutting down gracefully...`);
    httpServer.close(async () => {
      try {
        if (mongoose.connection.readyState === 1) {
          await mongoose.connection.close();
        }
      } catch (_) {
        /* ignore */
      }
      console.log('[WILSY] Shutdown complete.');
      process.exit(0);
    });
    setTimeout(() => {
      console.error('[WILSY] Force exit after timeout.');
      process.exit(1);
    }, 10000);
  };

  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);

  process.on('uncaughtException', (err) => {
    console.error('[WILSY] 💥 Uncaught Exception:', err);
  });
  process.on('unhandledRejection', (reason) => {
    console.error('[WILSY] 💥 Unhandled Rejection:', reason);
  });
}

if (process.argv[1] && fileURLToPath(import.meta.url) === resolve(process.argv[1])) {
  main().catch((err) => {
    console.error('[WILSY] ❌ Bootstrap failed:', err);
    process.exit(1);
  });
}

export default createApp;

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏛️ INSTITUTIONAL CERTIFICATION SEAL — WILSY OS RUNTIME BOOTSTRAPPER
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status:          CERTIFIED PRODUCTION ARTIFACT
 * Version:         v5.6.0-R10E17-RECOVERY-CONTACT-VERIFICATION-INTERNAL-MOUNT
 * Fix:             Preserves proxies before body parsers and mounts dedicated authenticated
 *                  password-recovery and recovery-contact-verification delivery bridges after
 *                  JSON parsing. Public auth requests continue to proxy to Python EOS unchanged.
 * Compliance:      POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15
 * Authority boundary: transport only; Python EOS remains sovereign for auth/recovery and C1C/C1E.
 * Tenant posture: institutional headers are forwarded, never invented.
 * Financial execution authority: Kennel EOS exclusively.
 * ═══════════════════════════════════════════════════════════════════════════════
 */
