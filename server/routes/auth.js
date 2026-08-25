/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Sovereign Authentication Gateway (Telemetry · Audit · Anomalies)
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           server/routes/auth.js
 * Version:        v46.0.2-NO-FALLBACK
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Removed hardcoded fallback user – now returns 401 if
 *                 authentication fails. All data comes from the database.
 * Classification: Production Artifact – Institutional Contract
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) — Mandated removal of fake data.
 *   - AI Engineering — v46.0.2: Removed hardcoded fallback in verify-token.
 *
 * Change Log:
 *   2026-08-18 v46.0.2-NO-FALLBACK — Removed hardcoded user fallback.
 *   2026-08-18 v46.0.1-STATIC-IMPORT — Static imports.
 *
 * Certification Seal: PRODUCTION_READY_v46.0.2-NO-FALLBACK
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import express from 'express';
import crypto from 'node:crypto';
import { discoverTenantShard } from '../controllers/tenantDiscoveryController.js';
import {
  login,
  generateOTP,
  verifyOTP,
  getMe,
  setupMFA,
  validateMFASetup,
  logout,
  adminForceRegenerateMfa,
  verify3FA,
  refresh
} from '../controllers/authController.js';
import { registerTenant } from '../controllers/onboardingController.js';
import { protect, admin, requireSovereignAuth, forensicAuditMiddleware } from '../middleware/auth.js';
import { useSovereignMesh } from '../utils/sovereignMesh.js';
import { useSovereignData } from '../utils/sovereignData.js';
import loggerRaw from '../utils/logger.js';
import promMetrics from '../metrics/prometheusMetrics.js';

const logger = loggerRaw.default || loggerRaw;
const router = express.Router();
const mesh = useSovereignMesh();

// ─── Helpers ────────────────────────────────────────────────────────────

function generateAuthProof(payload) {
  const sorted = JSON.stringify(payload, Object.keys(payload).sort());
  return crypto.createHash('sha3-512').update(sorted).digest('hex').toUpperCase();
}

function detectAuthAnomalies(req) {
  const anomalies = [];
  const headers = req.headers || {};
  const body = req.body || {};

  if (!headers['x-tenant-id'] && !headers['x-wilsy-tenant-id']) {
    anomalies.push('MISSING_TENANT_ID');
  }
  if (body.password && body.password.length < 12) {
    anomalies.push('WEAK_PASSWORD');
  }
  const email = body.adminEmail || body.email || '';
  if (email && /@(gmail|yahoo|hotmail|outlook|aol|protonmail|mail|yandex|icloud)\.com$/i.test(email)) {
    anomalies.push('CONSUMER_EMAIL_DOMAIN');
  }
  if (req.headers['x-forwarded-for'] && req.headers['x-forwarded-for'].split(',').length > 3) {
    anomalies.push('SUSPICIOUS_PROXY_CHAIN');
  }
  return anomalies;
}

function withAuthTelemetry(handler, routeName, eventType) {
  return async (req, res, next) => {
    const start = process.hrtime.bigint();
    const tenantId = req.headers['x-tenant-id'] || req.headers['x-wilsy-tenant-id'] || 'GLOBAL_ROOT';
    const tier = req.headers['x-wilsy-tier'] || 'default';

    try {
      const originalJson = res.json;
      res.json = function(data) {
        if (res.statusCode >= 200 && res.statusCode < 300 && data && typeof data === 'object') {
          if (!data.proofHash) {
            const proofPayload = {
              tenantId,
              tier,
              route: req.originalUrl || req.url,
              method: req.method,
              event: eventType,
              status: res.statusCode,
              timestamp: new Date().toISOString()
            };
            data.proofHash = generateAuthProof(proofPayload);
          }
          if (!data.anomalies) {
            data.anomalies = detectAuthAnomalies(req);
          }
          if (!data.compliance && eventType === 'register') {
            data.compliance = data.compliance || { popia: false, gdpr: false, soc2: false };
          }
        }
        originalJson.call(this, data);
      };

      await handler(req, res, next);

      const latencyMs = Number(process.hrtime.bigint() - start) / 1e6;
      if (promMetrics?.authLatency) {
        promMetrics.authLatency.observe({ route: routeName, tier }, latencyMs);
      }
      if (eventType === 'login' && promMetrics?.authLogins) {
        promMetrics.authLogins.inc({ tenantId, tier });
      } else if (eventType === 'register' && promMetrics?.authOnboardings) {
        promMetrics.authOnboardings.inc({ tier });
      }
    } catch (error) {
      if (promMetrics?.authFailures) {
        promMetrics.authFailures.inc({ tenantId, tier, reason: error.code || error.message || 'UNKNOWN' });
      }
      logger.error(`[AUTH_GATEWAY] ${routeName} failed: ${error.message}`);
      next(error);
    }
  };
}

// ====================== PUBLIC IDENTITY ROUTES ======================

router.route('/discover')
  .get(discoverTenantShard)
  .post(discoverTenantShard);

router.post('/register', withAuthTelemetry(registerTenant, '/register', 'register'));

router.post('/login', withAuthTelemetry(login, '/login', 'login'));

router.post('/sovereign-login', withAuthTelemetry(login, '/sovereign-login', 'login'));

router.post('/refresh', withAuthTelemetry(refresh, '/refresh', 'refresh'));

router.post('/otp/generate', withAuthTelemetry(generateOTP, '/otp/generate', 'otp'));

router.post('/otp/verify', withAuthTelemetry(verifyOTP, '/otp/verify', 'otp'));

router.post('/verify-3fa', withAuthTelemetry(verify3FA, '/verify-3fa', '3fa'));

// ====================== PROTECTED SOVEREIGN ROUTES ======================

/**
 * @route   GET/POST /api/auth/verify-token
 * @desc    Verifies sovereign authentication tokens.
 * @access  Protected (JWT + seal required)
 */
const verifyTokenHandler = async (req, res) => {
  try {
    // If protect middleware didn't attach req.user, authentication failed.
    if (!req.user) {
      return res.status(401).json({
        success: false,
        status: 'UNAUTHORIZED',
        error: 'AUTHENTICATION_REQUIRED',
        message: 'Valid JWT token required.'
      });
    }

    const authHeader = req.headers.authorization || req.headers['x-access-token'];
    const token = authHeader && authHeader.startsWith('Bearer ') 
      ? authHeader.split(' ')[1] 
      : (authHeader || req.body?.token);

    return res.status(200).json({
      success: true,
      status: 'VERIFIED',
      user: req.user, // Always from database
      token: token || null
    });
  } catch (error) {
    logger.error(`💥 [AUTH_VERIFY] Token Verification Fracture: ${error.message}`);
    return res.status(500).json({
      success: false,
      status: 'FRACTURE',
      error: 'TOKEN_VERIFICATION_FAILED'
    });
  }
};

router.get('/verify-token', protect, forensicAuditMiddleware, verifyTokenHandler);
router.post('/verify-token', protect, forensicAuditMiddleware, verifyTokenHandler);

router.use(requireSovereignAuth);

router.get('/me', protect, forensicAuditMiddleware, getMe);

router.post('/mfa/setup', protect, forensicAuditMiddleware, setupMFA);

router.get('/me/mfa/validate', protect, forensicAuditMiddleware, validateMFASetup);

router.post('/logout', protect, forensicAuditMiddleware, logout);

router.post('/admin/mfa-reset', protect, admin, forensicAuditMiddleware, adminForceRegenerateMfa);

export default router;
