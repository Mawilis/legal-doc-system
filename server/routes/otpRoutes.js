/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN OTP ENGINE (SOE)                                                                                                  ║
 * ║ [3FA AUTHENTICATION | TIME-BASED CRYPTOGRAPHY | FORENSIC AUDIT TRAILS]                                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 20.1.0-SINGULARITY-OMEGA | PRODUCTION READY                                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/otpRoutes.js                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Sovereign Security Design & Final Approval                                                    ║
 * ║ • Gemini (AI Engineering) - Cryptographic Handshake & Route Stabilization                                                              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import { protect } from '../middleware/authMiddleware.js';
import {
  generateOTP,
  verifyOTP,
  setupMFA,
  validateMFASetup
} from '../controllers/authController.js'; // 🏛️ Anchored in the Unified Controller

const router = express.Router();

/**
 * @section QUANTUM-SECURE HANDSHAKES
 * @description Dedicated vectors for One-Time Password lifecycle management.
 */

// Generate a new OTP for the authenticated session
router.post('/generate', protect, (req, res, next) => generateOTP(req, res).catch(next));

// Verify the provided OTP to elevate session privileges
router.post('/verify', protect, (req, res, next) => verifyOTP(req, res).catch(next));

/**
 * @section MULTI-FACTOR ENROLLMENT
 * @description Foundational setup for Sovereign Identity hardening.
 */

// Initiate the MFA enrollment (Generates the Secret and QR context)
router.get('/mfa/setup', protect, (req, res, next) => setupMFA(req, res).catch(next));

// Finalize MFA enrollment by validating the first successful handshake
router.post('/mfa/activate', protect, (req, res, next) => validateMFASetup(req, res).catch(next));

export default router;
