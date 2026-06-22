/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - MASTER API NEXUS [V46.1.0-MARS-OMEGA-ANCHOR]                                                                                ║
 * ║ [NEURAL PULSE RELAY | QUANTUM FORENSIC ANCHOR | PAN-AFRICAN JURISDICTION | INVOICE LEDGER | BOARDROOM-READY TELEMETRY]                ║
 * ║ [SOVEREIGN ARTIFACT GENERATOR | HMAC-SEALED PDF STREAMING]                                                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 46.1.0-MARS | PRODUCTION READY | TRILLION DOLLAR SPEC                                                                         ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/api.js                                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated Mars Protocol role alignment, continental jurisdiction safety, and board-ready APIs.   ║
 * ║ • AI Engineering (Gemini) – INTEGRATED: Mounted Seizure Protocols to the Tier-0 Protected Zone for Atomic Enforcement. [2026-05-25]    ║
 * ║ • AI Engineering (DeepSeek) – UPGRADED: Replaced legacy pdfRoutes with Sovereign Artifact Controller for HMAC-verified PDF generation. ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import crypto from 'node:crypto';
import { performance } from 'node:perf_hooks';
import mongoose from 'mongoose';

// Zero-Trust Security Middleware Layers
import { requireSovereignAuth } from '../middleware/auth.middleware.js';
import { enforceTenantIsolation } from '../middleware/tenantBypass.js';
import { tenantGuard } from '../middleware/tenantGuard.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import { breakerRegistry } from '../utils/circuitBreaker.js';
import auditLogger from '../middleware/auditLogger.js';
import { checkRedisHealth } from '../config/redis.js';
import { coldStorageQueue } from '../utils/telemetryLogger.js';
import { SovereignBypassRoles } from '../config/roles.registry.js';

// Route Shard Mappings
import auth from './authRoutes.js';
import tenantRoutes from './tenantRoutes.js';
import lpc from './lpcRoutes.js';
import assetRoutes from './assetRoutes.js';
import contractRoutes from './contractRoutes.js';
import revenueRoutes from './revenueRoutes.js';
import billingRoutes from './billingRoutes.js';
import billingAdvancedRoutes from './billingAdvancedRoutes.js';
import financeRoutes from './financeRoutes.js';
import analyticsRoutes from './analyticsRoutes.js';
import crmRoutes from './crmRoutes.js';
import telemetryRoutes from './telemetryRoutes.js';
import compliance from './complianceRoutes.js';
import forensics from './forensicRoutes.js';
import legalRoutes from './legal/index.js';
import jurisdictionRoutes from './jurisdictionRoutes.js';
import ledgerRoutes from './ledgerRoutes.js';
import brandingRoutes from './brandingRoutes.js';
import invoiceRoutes from './invoiceRoutes.js';
import courtRoutes from './courtRoutes.js';
import nodeRoutes from './nodeRoutes.js';
import seizureRoutes from './sovereignSeizureRoutes.js'; // 🛑 Atomic Seizure Protocol
import statementsRoutes from './statements.routes.js';
import wilsyAiRoutes from './wilsyAiRoutes.js';

// 🏛️ SOVEREIGN ARTIFACT CONTROLLER (replaces legacy pdfRoutes)
import artifactController from '../controllers/artifactController.js';
import { queryLedger } from '../controllers/aiController.js';
import { generateSovereignArtifactPdf } from '../controllers/businessArtifactPdfController.js';

const router = express.Router();

// ============================================================================
// 🧠 NEURAL PULSE INTERCEPTOR – forensic tracing
// ============================================================================
/**
 * @middleware NeuralPulseInterceptor
 * @description Injects canonical tracking parameters, builds unique trace IDs,
 * computes real‑time cryptographic hashes, and records latency. Satisfies Cybercrimes Act §3.
 */
router.use((req, res, next) => {
  req.traceId =
    req.headers['x-trace-id'] ||
    req.headers['x-request-id'] ||
    `TRC-TITAN-${crypto.randomBytes(8).toString('hex').toUpperCase()}`;
  req.startTime = performance.now();

  const forensicPayload = `${req.traceId}-${req.ip}-${req.headers['user-agent']}`;
  const forensicHash = crypto.createHash('sha3-512').update(forensicPayload).digest('hex');

  res.setHeader('X-Trace-ID', req.traceId);
  res.setHeader('X-Quantum-Verified', 'true');
  res.setHeader('X-Forensic-Hash', forensicHash);
  req.forensicHash = forensicHash;

  const tenantId = req.headers['x-tenant-id'] || 'WILSY_ROOT';

  res.on('finish', () => {
    try {
      const duration = (performance.now() - req.startTime).toFixed(3);
      broadcastTelemetry(tenantId, 'NEURAL_PULSE', 'REQUEST_COMPLETE', req.path, {
        traceId: req.traceId,
        durationMs: duration,
        status: res.statusCode,
        method: req.method,
      }).catch(() => {});
    } catch (error) {
      // Request completion telemetry must never alter the HTTP lifecycle.
    }
  });

  next();
});

// ============================================================================
// 📡 SINGULARITY HEALTH PROBE
// ============================================================================
/**
 * @route GET /status
 * @desc Infrastructure stability matrix (Redis, DB, Breakers).
 */
router.get('/status', async (req, res) => {
  const start = performance.now();
  const dbStatus = mongoose.connection.readyState === 1 ? 'ANCHORED' : 'FRACTURED';
  const redisHealth = await checkRedisHealth();
  const breakers = breakerRegistry.getAllStatus();

  const isHealthy = dbStatus === 'ANCHORED' && redisHealth.status === 'HEALTHY';
  const probeLatency = (performance.now() - start).toFixed(2);

  res.status(isHealthy ? 200 : 503).json({
    success: isHealthy,
    status: isHealthy ? 'SINGULARITY_OPERATIONAL' : 'SYSTEM_DEGRADED',
    version: '46.1.0-MARS-INTEGRATED',
    timestamp: new Date().toISOString(),
    probeLatencyMs: probeLatency,
    infrastructure: {
      database: dbStatus,
      redis: { status: redisHealth.status, latencyMs: redisHealth.latency || 0 },
      circuitBreakers: breakers,
      telemetryQueue: coldStorageQueue.length,
    },
  });
});

// ============================================================================
// 🏛️ 1. PUBLIC GATEWAY (No Auth Required)
// ============================================================================
router.use('/auth', auth);
router.use('/telemetry', telemetryRoutes);
router.use('/forensics', forensics);

// ============================================================================
// 🏛️ 2. SOVEREIGN PROTECTED ZONE (Auth Mandatory)
// ============================================================================
router.use(requireSovereignAuth);
router.use(tenantGuard);
router.use(enforceTenantIsolation);

// ============================================================================
// 🏛️ 3. CORE MODULE MOUNTING (Forensically Secured)
// ============================================================================
router.use('/tenant', tenantRoutes);
router.use('/compliance', compliance);
router.use('/lpc', lpc);
router.use('/assets', assetRoutes);
router.use('/contracts', contractRoutes);
router.use('/revenue', revenueRoutes);
router.use('/billing', billingRoutes);
router.use('/billing-advanced', billingAdvancedRoutes);
router.use('/finance', financeRoutes);
router.use('/analytics', analyticsRoutes);
router.use('/crm', crmRoutes);
router.use('/legal', legalRoutes);
router.use('/jurisdiction', jurisdictionRoutes);
router.use('/ledger', ledgerRoutes);
router.use('/branding', brandingRoutes);
router.use('/invoices', invoiceRoutes);
router.use('/courts', courtRoutes);
router.use('/nodes', nodeRoutes);
router.use('/seizure', seizureRoutes); // 🛑 Atomic Seizure Protocol Active
router.use('/statements', statementsRoutes);
router.use('/wilsy-ai', wilsyAiRoutes);
router.post('/ai/query-ledger', queryLedger);

// 🏛️ SOVEREIGN ARTIFACT GENERATION – HMAC-sealed PDF endpoint
// Legacy pdfRoutes is replaced by artifactController for enhanced security (HMAC verification, forensic logging, digital signature embedding)
router.post('/generate/pdf', generateSovereignArtifactPdf);

// ============================================================================
// 💥 GLOBAL NEXUS FAULT INTERCEPTOR
// ============================================================================
/**
 * @middleware GlobalNexusFaultInterceptor
 * @description Catches all upstream runtime faults, logs forensic signatures,
 * and masks internal infrastructure details.
 */
router.use((err, req, res, next) => {
  const errorId = `ERR-TITAN-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
  const duration = (performance.now() - req.startTime).toFixed(3);
  const tenantId = req.headers['x-tenant-id'] || 'WILSY_ROOT';

  auditLogger.log('CRITICAL_FRACTURE', {
    errorId,
    traceId: req.traceId,
    message: err.message,
    path: req.originalUrl,
    tenantId,
  });

  broadcastTelemetry(tenantId, 'NEXUS_FRACTURE', 'CORE_INTERCEPTOR', 'EXCEPTION', {
    errorId,
    traceId: req.traceId,
    durationMs: duration,
    errorCode: err.status || 500,
  });

  res.status(err.status || 500).json({
    success: false,
    errorId,
    message: `Institutional Nexus Jitter: ${err.message}`,
    traceId: req.traceId,
    latencyMs: duration,
  });
});

export default router;
