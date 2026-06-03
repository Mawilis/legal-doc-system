/* eslint-disable */
/**
 * ╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║                         WILSY OS - MFA ADMIN MANAGEMENT [THE HIGH COMMAND]                       ║
 * ║                              IDENTITY CITADEL v20.1.0-SINGULARITY                                ║
 * ║                           ADMIN-LEVEL RECOVERY & AUDIT PROTOCOLS                                 ║
 * ║                                 NO COMPETITION. NO COMPROMISE.                                   ║
 * ╚══════════════════════════════════════════════════════════════════════════════════════════════════╝
 * * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/mfaAdminRoutes.js
 * VERSION: 20.1.0-SINGULARITY-OMEGA
 * EPITOME: BIBLICAL WORTH BILLIONS | CEO-LEVEL AUTHORITY | NO CHILD'S PLACE
 * * * 🛡️ ADMINISTRATIVE GUARD:
 * • Restricted to users with 'super_admin' or 'tenant_owner' roles.
 * • Allows forensic secret rotation for disaster recovery.
 * * * 👥 COLLABORATION & SOVEREIGN SIGN-OFF:
 * • Wilson Khanyezi (Lead Architect & CEO) - Global Governance Policy.
 * • Gemini (AI Engineering) - Admin Route Orchestration.
 */

import express from 'express';
import { adminForceRegenerateMfa } from '../controllers/authController.js';
import { User } from '../models/userModel.js';

const router = express.Router();

// Internal Admin Guard: Only allows the CEO/SuperAdmin to bypass user protections
const restrictToSovereign = (req, res, next) => {
  if (req.user && (req.user.role === 'super_admin' || req.user.role === 'tenant_owner')) {
    return next();
  }
  res.status(403).json({ success: false, message: "AUTHORITY_DENIED: Sovereign Access Required" });
};

/**
 * @route   GET /api/mfa/admin/status/:userId
 * @desc    View the current MFA security posture of a specific user.
 */
router.get('/status/:userId', restrictToSovereign, async (req, res) => {
  try {
    const user = await User.findById(req.params.userId).select('email securityMetadata');
    if (!user) return res.status(404).json({ success: false, message: "USER_NOT_FOUND" });

    res.json({
      success: true,
      user: {
        email: user.email,
        mfaEnabled: user.securityMetadata?.mfaEnabled || false,
        lastLogin: user.securityMetadata?.lastLogin
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

/**
 * @route   POST /api/mfa/admin/regenerate/:userId
 * @desc    [NUCLEAR OPTION] Force reset a user's MFA keys (CEO Use Only).
 */
router.post('/regenerate/:userId', restrictToSovereign, adminForceRegenerateMfa);

export default router;
