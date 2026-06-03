/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN IDENTITY ROUTER [V26.3.0-OMEGA]                                                                                   ║
 * ║ [IDENTITY COMMAND CENTER | BIOMETRIC BRIDGE | FORENSIC EXPORT | CLEARANCE ENFORCEMENT]                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 26.3.0-OMEGA | PRODUCTION READY                                                                                               ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL FINALITY                                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/users.js                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated actionable authority protocols and disruptive investor-grade features.                ║
 * ║ • Gemini (AI Engineering) - Integrated SovereignIdentityService and engineered high-fidelity forensic routing.                         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import { User } from '../models/userModel.js';
import { sovereignIdentityService } from '../services/SovereignIdentityService.js';
import logger from '../utils/logger.js';

const router = express.Router();

/**
 * @route GET /api/users
 * @desc Extracts high-fidelity identities with biometric and clearance telemetry.
 */
router.get('/', async (req, res) => {
  try {
    const tenantContext = req.query.tenant || req.header('X-Tenant-ID');

    if (!tenantContext) {
      return res.status(400).json({ success: false, message: 'TENANT_CONTEXT_MISSING' });
    }

    // Querying the V26.0.0 OMEGA Model
    const dbUsers = await User.find({ tenantId: tenantContext })
      .select('+biometric.biometricAnchor') // Internal validation only, not sent to UI
      .lean();

    const mappedUsers = dbUsers.map(user => ({
      id: user._id,
      firstName: user.firstName,
      lastName: user.lastName,
      email: user.email,
      role: user.role,
      securityClearance: user.securityClearance || 'standard',
      status: user.isActive ? 'active' : 'suspended',
      mfaEnabled: user.securityMetadata?.mfaEnabled || false,
      biometricStatus: user.biometric?.status || 'PENDING',
      lastLogin: user.securityMetadata?.lastLogin || user.createdAt,
      // Sealing the individual row metadata for the UI
      forensicSeal: sovereignIdentityService.generateQuantumSeal(user._id)
    }));

    return res.status(200).json({
      success: true,
      data: {
        users: mappedUsers,
        metadata: { tenant: tenantContext, count: mappedUsers.length }
      }
    });
  } catch (error) {
    logger.error('[ROUTER] 💥 Identity Extraction Failure:', error.message);
    res.status(500).json({ success: false, message: 'INTERNAL_SERVER_ERROR' });
  }
});

/**
 * @route POST /api/users/anchor-biometric
 * @desc "Identities are sealed in human uniqueness."
 */
router.post('/anchor-biometric', async (req, res) => {
  try {
    const { userId, biometricData } = req.body;
    const result = await sovereignIdentityService.anchorBiometric(userId, biometricData);

    // Log the action to the forensic chain via the service
    await sovereignIdentityService.appendForensic(userId, 'BIOMETRIC_ANCHORED', 'SYSTEM_ADMIN', { method: 'FIDO2_SYNC' });

    res.status(200).json(result);
  } catch (error) {
    res.status(403).json({ success: false, message: error.message });
  }
});

/**
 * @route POST /api/users/revoke
 * @desc "Only sovereign clearance executes sovereign actions."
 */
router.post('/revoke', async (req, res) => {
  try {
    const { userId, performerId } = req.body;
    const performer = await User.findById(performerId);

    // Enforcement: Only OMEGA clearance can revoke an identity
    sovereignIdentityService.enforceClearance(performer, 'ADMIN_UNLOCK');

    const target = await User.findByIdAndUpdate(userId, { isActive: false }, { new: true });

    await sovereignIdentityService.appendForensic(userId, 'IDENTITY_REVOKED', performerId, { reason: 'ADMIN_TERMINATION' });

    res.status(200).json({ success: true, message: 'IDENTITY_REVOKED_AND_SEALED' });
  } catch (error) {
    res.status(403).json({ success: false, message: error.message });
  }
});

/**
 * @route GET /api/users/forensic/:userId
 * @desc "Every action sealed in sovereign truth, ready for investor scrutiny."
 */
router.get('/forensic/:userId', async (req, res) => {
  try {
    const report = await sovereignIdentityService.exportForensicReport(req.params.userId);
    res.status(200).json({ success: true, data: report });
  } catch (error) {
    res.status(404).json({ success: false, message: error.message });
  }
});

export default router;
