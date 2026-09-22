/**
 * WILSY OS — NODE AUTH TRANSPORT ROUTES
 * TITLE: Node Authentication Transport Router
 * VERSION: v47.0.0-R10E65-RETIRE-NODE-RECOVERY-ROUTE
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Binds the retained Node authentication transport endpoints while
 *          explicitly excluding password-recovery/reset authority now owned
 *          by canonical Python EOS recovery services.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/authRoutes.js
 * COLLABORATION / OWNERSHIP: Node controllers remain transport/orchestration
 *                            surfaces for legacy auth paths; Python EOS
 *                            tools/eos/api/auth_router.py owns canonical
 *                            password recovery and reset HTTP authority.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG: v47.0.0-R10E65-RETIRE-NODE-RECOVERY-ROUTE — Removes the public
 *            /reset-password-sovereign route and its controller binding after
 *            R10E64 certified the Python recovery request, verified-contact,
 *            delivery, reset-completion, ASGI, real-Mongo, and client flow.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: This router accepts no password-recovery token,
 *                             recovery email, reset password, or recovery
 *                             capability material.
 * TENANT BOUNDARY: Route binding creates no tenant truth; downstream canonical
 *                  authorities remain responsible for tenant admission.
 * AUTHORITY BOUNDARY: Node transport/orchestration only. Password recovery,
 *                     recovery-contact verification, reset capability issuance,
 *                     and password-reset mutation belong exclusively to Python EOS.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive
 *                               financial execution and settlement authority.
 * FAIL-CLOSED POSTURE: No Node password-recovery/reset route is exposed by
 *                      this router; canonical recovery requests must traverse
 *                      the Python EOS auth API.
 */

import express from 'express';
import {
  discoverTenant,
  register,
  login,
  refresh,
  getWebAuthnChallenge,
  verify3FA,
  getMe,
  logout,
  anchorHardwareDevice,
  revokeBiometric,
  verifyForensicChain,
  verifyOTP,
  setupMFA,
  validateMFASetup,
} from '../controllers/authController.js';
import { protectSovereign } from '../middleware/authMiddleware.js';

const router = express.Router();

/**
 * Discover the tenant transport context before authentication.
 * This route grants no tenant membership or password-recovery authority.
 */
router.post('/discover', discoverTenant);
router.get('/discover', discoverTenant);

/**
 * Forward legacy registration transport to its existing controller.
 * This binding does not grant password-recovery/reset authority.
 */
router.post('/register', register);

/**
 * Forward legacy primary-credential login transport.
 * Password recovery is intentionally absent from this Node router.
 */
router.post('/login', login);

/**
 * Forward retained MFA verification transport.
 * These routes do not issue password-recovery capabilities.
 */
router.post('/verify-3fa', verify3FA);
router.post('/verify-otp', verifyOTP);

/**
 * Forward retained refresh transport.
 * Recovery/reset capability issuance is not available through this route.
 */
router.post('/refresh', refresh);

/**
 * Forward retained WebAuthn challenge transport.
 */
router.post('/webauthn-challenge', getWebAuthnChallenge);

/**
 * Project the current authenticated identity through the existing guard.
 */
router.get('/me', protectSovereign, getMe);

/**
 * Forward authenticated logout transport.
 */
router.post('/logout', protectSovereign, logout);

/**
 * Forward authenticated hardware-anchor transport.
 */
router.post('/anchor-hardware', protectSovereign, anchorHardwareDevice);

/**
 * Forward authenticated biometric revocation transport.
 */
router.post('/revoke-biometric', protectSovereign, revokeBiometric);

/**
 * Forward authenticated forensic-chain verification transport.
 */
router.get('/verify-forensic-chain', protectSovereign, verifyForensicChain);

/**
 * Forward retained MFA setup/validation transport.
 */
router.post('/setup-mfa', protectSovereign, setupMFA);
router.post('/validate-mfa-setup', validateMFASetup);

export default router;

/**
 * ARTIFACT: server/routes/authRoutes.js
 * VERSION: v47.0.0-R10E65-RETIRE-NODE-RECOVERY-ROUTE
 * AUTHORITY BOUNDARY: Node auth transport/orchestration only; no recovery/reset authority
 * TENANT POSTURE: route binding creates no tenant truth or cross-tenant fallback
 * FAIL-CLOSED POSTURE: legacy Node password-recovery/reset route is absent
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
