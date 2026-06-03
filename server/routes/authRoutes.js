/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN IDENTITY & AUTHENTICATION ROUTES [V47.1.0-MARS]                                                                   ║
 * ║ [PUBLIC GATEWAY | SHARD ALIGNMENT | HS512 HANDSHAKE | BOARDROOM READY]                                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 47.1.0-MARS | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                      ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/authRoutes.js                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated Mars Protocol finality for identity strikes. [2026-05-15]                            ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Explicitly separated Public/Private shards to resolve 403 login fractures. [2026-05-15]         ║
 * ║ • AI Engineering (Gemini) - FORTIFIED: Aligned verify-3fa and refresh trajectories for HS512 consistency. [2026-05-15]                 ║
 * ║ • AI Engineering (DeepSeek) - EPITOMISED: Full JSDoc, added diagnostic route list log. [2026-05-16]                                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import {
  register,
  login,
  getWebAuthnChallenge,
  verifyOTP,
  verify3FA,
  anchorHardwareDevice,
  getMe,
  logout,
  resetPasswordSovereign,
  revokeBiometric,
  verifyForensicChain,
  refresh,
  discoverTenant
} from '../controllers/authController.js';
import { requireSovereignAuth } from '../middleware/auth.middleware.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

const router = express.Router();

// ============================================================================
// 🏛️ 1. PUBLIC IDENTITY GATEWAY (ZERO AUTH REQUIRED)
// ============================================================================

/**
 * 🛰️ SHARD DISCOVERY – allows any client to resolve tenant configuration.
 * Supports both GET and POST for flexibility.
 * @route GET /discover
 * @route POST /discover
 */
router.route('/discover')
  .get(discoverTenant)
  .post(discoverTenant);

/**
 * 🚀 INITIAL IDENTITY STRIKES – registration, login, token refresh, 3FA.
 */
router.post('/register', register);
router.post('/login', login);
router.post('/refresh-token', refresh);
router.post('/verify-3fa', verify3FA);

/**
 * 🚑 PUBLIC RECOVERY AND WEBAUTHN CHALLENGE.
 */
router.post('/recover-account', resetPasswordSovereign);
router.post('/webauthn-challenge', getWebAuthnChallenge);
router.post('/verify-otp', verifyOTP);

// ============================================================================
// 🏛️ 2. PROTECTED SOVEREIGN ROUTES (JWT & HS512 REQUIRED)
// ============================================================================

router.use(requireSovereignAuth);

/**
 * 🧬 IDENTITY & FORENSICS – require authentication.
 */
router.get('/me', getMe);
router.get('/verify-forensic-chain', verifyForensicChain);
router.post('/revoke-biometric', revokeBiometric);
router.post('/anchor-hardware', anchorHardwareDevice);
router.post('/logout', logout);

// Diagnostic: log all routes registered (for debugging)
if (process.env.NODE_ENV !== 'production') {
  const routes = [];
  router.stack.forEach(layer => {
    if (layer.route) {
      routes.push(`${Object.keys(layer.route.methods).join(',')} ${layer.route.path}`);
    }
  });
  console.log('[AUTH-ROUTES] Registered:', routes.join(', '));
}

export default router;
