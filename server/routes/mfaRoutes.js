/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - MFA GATEWAY ROUTES [V15.0.1-HARDENED]                                                                                       ║
 * ║ [IDENTITY ANCHORING | INTEGRITY SHIELDED | OMEGA-LEVEL PROTECTION | FORENSIC TRACING]                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 15.0.1-SINGULARITY-OMEGA | PRODUCTION READY                                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL GRADE                                                              ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/mfaRoutes.js                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated forensic hardening and institutional finality for the MFA Gateway.                   ║
 * ║ • Gemini (AI Engineering) - RECTIFIED: Injected Integrity Shield and Forensic Header Enforcement.                                      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import { setupMfa, verifyMfa } from '../controllers/MfaController.js';
import { protect } from '../middleware/authMiddleware.js';
import { integrityShield } from '../middleware/ProductionHardening.middleware.js'; // 🛡️ Institutional Shield

const router = express.Router();

/**
 * 🛰️ MFA INITIALIZATION (Step 1)
 * Generate TOTP Secret and QR Code for Google Authenticator.
 * * @route   POST /api/mfa/setup
 * @access  Private (Sovereign Authenticated)
 * @security Integrity shield + JWT Protection
 */
router.post('/setup', integrityShield, protect, setupMfa);

/**
 * 🕵️ MFA FINALIZATION (Step 2)
 * Verify TOTP Token and activate permanent Sovereign 3FA state.
 * * @route   POST /api/mfa/verify
 * @access  Private (Sovereign Authenticated)
 * @security Integrity shield + Anti-Replay
 */
router.post('/verify', integrityShield, protect, verifyMfa);

export default router;
