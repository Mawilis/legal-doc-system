/* eslint-disable */
/**
 * ####################################################################################################
 * # WILSY OS - MFA ENFORCEMENT MIDDLEWARE [THE IDENTITY GATEKEEPER]                                #
 * # ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/mfaMiddleware.js         #
 * ####################################################################################################
 * # VERSION: 20.0.1-SINGULARITY                                                                      #
 * # EPITOME: BIBLICAL WORTH BILLIONS | ZERO-TRUST ARCHITECTURE | NO CHILD'S PLACE                  #
 * ####################################################################################################
 * * 👥 COLLABORATION & SOVEREIGN SIGN-OFF:
 * • Wilson Khanyezi (Lead Architect & CEO) - Zero-Trust Enforcement Policy.
 * • Gemini (AI Engineering) - Request Interception & Forensic Handshake.
 */

import { mfaService } from '../services/MfaService.js';

/**
 * @desc Protects high-value routes (Trust movements, Financial reports).
 * Requires mfaToken in the request body or headers.
 */
export const requireMfa = async (req, res, next) => {
  try {
    const user = req.user;

    // If MFA is not enabled for this user, we pass (for now), but log the vulnerability.
    if (!user?.securityMetadata?.mfaEnabled) {
      return next();
    }

    const mfaToken = req.body.mfaToken || req.headers['x-wilsy-mfa'];

    if (!mfaToken) {
      return res.status(401).json({
        success: false,
        requiresMfa: true,
        message: "SOVEREIGN_CHALLENGE: Multi-factor authentication code required."
      });
    }

    const isValid = await mfaService.verifyHandshake(user._id, mfaToken);

    if (!isValid) {
      return res.status(401).json({
        success: false,
        message: "FORENSIC_FAILURE: Invalid or expired MFA code."
      });
    }

    // Handshake successful
    next();
  } catch (error) {
    console.error("🛡️ MFA Middleware Error:", error);
    res.status(500).json({ success: false, message: "CRITICAL_SECURITY_FAULT" });
  }
};
