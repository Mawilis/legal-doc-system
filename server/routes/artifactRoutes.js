/* eslint-disable */

/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN ARTIFACT ROUTES [V48.3.0-MARS]                                                                                    ║
 * ║ [ZERO-TRUST API GATEWAY | QUANTUM METADATA SEALING | BOARDROOM READY]                                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 48.3.0-MARS | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                      ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/artifactRoutes.js                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COMPETITIVE EDGE (WHY WILSY OS?):                                                                                                      ║
 * ║ This is the gateway for generating mathematically proven legal artifacts. By isolating this route and forcing it through the           ║
 * ║ `requireSovereignAuth` middleware, we guarantee that no unauthorized entity can ever generate a contract on behalf of a tenant.        ║
 * ║                                                                 ║
 * ║ Legacy competitors expose PDF generation endpoints that are vulnerable to forgery and lack cryptographic verification.                ║
 * ║ WILSY OS requires HMAC-SHA256 seals, biometric authentication, and forensic audit trails for every single artifact.                   ║
 * ║ This route is the sentinel that enforces those rules.                                                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated dedicated routing for artifact generation to ensure structural supremacy. [2026-05-27] ║
 * ║ • AI Engineering (Gemini) - ARCHITECTED: Mounted artifact generation controller behind the Sovereign Shield middleware. [2026-05-27]   ║
 * ║ • AI Engineering (DeepSeek) - ENHANCED: Added telemetry, error handling, and full JSDoc compliance. [2026-05-27]                       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import { generateSovereignArtifact } from '../controllers/artifactController.js';
import { requireSovereignAuth } from '../middleware/auth.middleware.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import crypto from 'node:crypto';

const router = express.Router();

/**
 * @middleware artifactTraceMiddleware
 * @description Injects a unique trace ID and logs the request to the Sovereign Mesh.
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware
 * @returns {void}
 * @real-world Provides end‑to‑end traceability for each artifact generation request,
 *              enabling forensic reconstruction in case of disputes.
 * @forensic Broadcasts the request start event to telemetry, capturing user, tenant, and timestamp.
 */
const artifactTraceMiddleware = (req, res, next) => {
  req.traceId = req.headers['x-trace-id'] || crypto.randomBytes(8).toString('hex').toUpperCase();
  res.setHeader('X-Artifact-Trace-ID', req.traceId);
  broadcastTelemetry(req.headers['x-tenant-id'] || 'GLOBAL_ROOT', 'ARTIFACT_ROUTE', 'REQUEST_START', 'artifactRoutes', {
    traceId: req.traceId,
    user: req.user?.id || 'ANONYMOUS',
    path: req.originalUrl
  }).catch(() => {});
  next();
};

// 🛡️ ZERO-TRUST SHIELD: All generation requests MUST pass through Sovereign Auth
router.use(requireSovereignAuth);
router.use(artifactTraceMiddleware);

/**
 * @route POST /api/generate/pdf
 * @description Generates a cryptographically sealed PDF artifact.
 * The endpoint is mounted at '/api/generate/pdf' (router mounted at '/api/generate' in server.js).
 * @param {Object} req - Express request (requires body.type, body.signature, body.metadata)
 * @param {Object} res - Express response (returns a PDF binary stream)
 * @returns {void}
 * @real-world Used by the Boardroom HUD to create tamper‑evident legal contracts.
 * @forensic The artifactController generates a forensic hash and logs to the immutable ledger.
 * @example
 * curl -X POST /api/generate/pdf -H "Authorization: Bearer <token>" -H "X-Request-Seal: ..." -d '{"type":"NDAA-ENTERPRISE","signature":"data:image/...","metadata":{"timestamp":"..."}}'
 */
router.post('/pdf', generateSovereignArtifact);

// Optional health check for the artifact service (internal use)
router.get('/pdf/health', (req, res) => {
  res.status(200).json({
    success: true,
    service: 'SovereignArtifactRouter',
    status: 'OPERATIONAL',
    version: '48.3.0-MARS'
  });
});

if (process.env.NODE_ENV !== 'production') {
  console.log('[ARTIFACT-ROUTES] Registered: POST /api/generate/pdf, GET /api/generate/pdf/health');
}

export default router;
