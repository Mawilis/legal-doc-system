/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ SUPER-ADMIN CONTROLLER - WILSY OS CITADEL                                 ║
  ║ Dual-Key Governance | Hardware MFA | Vetting Pipeline                    ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/admin/superAdminController.js
 * VERSION: 1.0.0-CITADEL
 * CREATED: 2026-03-02
 */

import { SuperAdmin, SUPER_ADMIN_STATUS, VETTING_STATUS } from '../../models/SuperAdmin.js';
import { AuditLog } from '../../services/audit/auditService.js';
import { Encryption } from '../../utils/cryptoUtils.js';
import { getCurrentTenant, getCurrentUser } from '../../middleware/tenantContext.js';
import { v4 as uuidv4 } from 'uuid';
import crypto from 'crypto';
import logger from '../../utils/logger.js';
import auditLogger from '../../utils/auditLogger.js';
import { emergencyKillSwitch } from '../../middleware/emergencyKillSwitch.js';

// ============================================================================
// VETTING & CREATION (Hardware MFA Required)
// ============================================================================

export const createSuperAdmin = async (req, res, next) => {
  const correlationId = uuidv4();
  const startTime = Date.now();

  try {
    // Step 1: Verify Founder signature
    const { founderSignature, hardwareTokenId, adminData } = req.body;

    if (!founderSignature || !hardwareTokenId) {
      return res.status(403).json({
        error: 'Founder signature and hardware token required',
        code: 'MISSING_FOUNDER_AUTH'
      });
    }

    // Verify founder signature (in production, this would verify against stored founder key)
    const founderVerified = await verifyFounderSignature(founderSignature);
    if (!founderVerified) {
      await auditLogger.log({
        action: 'SUPER_ADMIN_CREATION_FAILED',
        correlationId,
        reason: 'Invalid founder signature'
      });
      return res.status(403).json({ error: 'Invalid founder signature' });
    }

    // Step 2: Check criminal background (simulated - would call actual service)
    const backgroundCheck = await performBackgroundCheck(adminData.identity);

    if (!backgroundCheck.passed) {
      return res.status(400).json({
        error: 'Background check failed',
        details: backgroundCheck.findings
      });
    }

    // Step 3: Store NDA
    const ndaHash = await storeNDA(adminData.identity.email, req.ip, req.get('user-agent'));

    // Step 4: Create Super Admin
    const admin = new SuperAdmin({
      identity: {
        ...adminData.identity,
        biometricHash: crypto.createHash('sha256')
          .update(adminData.identity.email + Date.now())
          .digest('hex')
      },
      vetting: {
        status: VETTING_STATUS.PENDING,
        criminalBackgroundCheck: {
          performedAt: new Date(),
          performedBy: 'founder',
          reportHash: backgroundCheck.reportHash,
          passed: backgroundCheck.passed,
          findings: backgroundCheck.findings
        },
        ndaSigned: {
          signedAt: new Date(),
          documentHash: ndaHash,
          ipAddress: req.ip,
          userAgent: req.get('user-agent')
        }
      },
      hardwareKeys: [{
        keyId: hardwareTokenId,
        publicKey: adminData.hardwarePublicKey,
        attestation: adminData.attestation,
        registeredIp: req.ip
      }],
      geoFencing: adminData.geoFencing || {
        enabled: true,
        allowedCountries: ['ZA']
      },
      audit: {
        createdBy: 'founder',
        createdAt: new Date()
      }
    });

    await admin.save();

    // Add to forensic chain
    admin.addToForensicChain('SUPER_ADMIN_CREATED', {
      createdBy: 'founder',
      hardwareTokenId,
      correlationId
    });
    await admin.save();

    await auditLogger.log({
      action: 'SUPER_ADMIN_CREATED',
      correlationId,
      adminId: admin.adminId,
      duration: Date.now() - startTime
    });

    res.status(201).json({
      success: true,
      adminId: admin.adminId,
      status: admin.status,
      message: 'Super Admin created. Requires secondary approval.',
      nextSteps: [
        'Second founder must approve',
        'Complete hardware registration',
        'Schedule bi-annual review'
      ]
    });

  } catch (error) {
    logger.error('Super Admin creation failed', { correlationId, error: error.message });
    next(error);
  }
};

export const approveSuperAdmin = async (req, res, next) => {
  const correlationId = uuidv4();
  const { adminId } = req.params;
  const { approverSignature, hardwareKeyId } = req.body;

  try {
    const admin = await SuperAdmin.findOne({ adminId });
    if (!admin) {
      return res.status(404).json({ error: 'Super Admin not found' });
    }

    // Verify second founder
    const founderVerified = await verifyFounderSignature(approverSignature, 2);
    if (!founderVerified) {
      return res.status(403).json({ error: 'Invalid approver signature' });
    }

    admin.dualKey.approvedBy.push({
      adminId: 'founder-2',
      approvedAt: new Date(),
      hardwareKeyId,
      signature: approverSignature
    });

    admin.status = SUPER_ADMIN_STATUS.ACTIVE;
    admin.vetting.status = VETTING_STATUS.COMPLETED;
    admin.vetting.vettedBy = 'founder-2';
    admin.vetting.vettingCompletedAt = new Date();

    admin.addToForensicChain('SUPER_ADMIN_APPROVED', {
      approvedBy: 'founder-2',
      correlationId
    });

    await admin.save();

    await auditLogger.log({
      action: 'SUPER_ADMIN_APPROVED',
      correlationId,
      adminId
    });

    res.json({
      success: true,
      status: admin.status,
      message: 'Super Admin fully activated'
    });

  } catch (error) {
    logger.error('Super Admin approval failed', { correlationId, error: error.message });
    next(error);
  }
};

// ============================================================================
// 🚨 EMERGENCY KILL SWITCH
// ============================================================================

export const emergencySuspend = async (req, res, next) => {
  const correlationId = uuidv4();
  const { adminId } = req.params;
  const { reason, founderSignature } = req.body;

  try {
    // Verify founder signature for emergency action
    const founderVerified = await verifyFounderSignature(founderSignature);
    if (!founderVerified) {
      return res.status(403).json({ error: 'Invalid founder signature' });
    }

    const admin = await SuperAdmin.findOneAndUpdate(
      { adminId },
      {
        status: SUPER_ADMIN_STATUS.SUSPENDED,
        killSwitch: {
          triggeredAt: new Date(),
          triggeredBy: getCurrentUser(),
          reason: reason || 'Emergency suspension by founder'
        },
        'sessions.$[].status': 'revoked'
      },
      { new: true }
    );

    if (!admin) {
      return res.status(404).json({ error: 'Super Admin not found' });
    }

    admin.addToForensicChain('EMERGENCY_SUSPEND', {
      triggeredBy: getCurrentUser(),
      reason,
      correlationId
    });
    await admin.save();

    // Trigger global session purge
    await emergencyKillSwitch.purgeAdminSessions(adminId);

    await auditLogger.log({
      action: 'EMERGENCY_SUSPEND',
      correlationId,
      adminId,
      reason
    });

    // Send out-of-band alert to founder
    await sendOutOfBandAlert({
      type: 'EMERGENCY_SUSPEND',
      adminId,
      reason,
      triggeredBy: getCurrentUser()
    });

    res.json({
      success: true,
      message: 'Super Admin suspended. All sessions revoked.',
      killSwitchTriggered: true
    });

  } catch (error) {
    logger.error('Emergency suspend failed', { correlationId, error: error.message });
    next(error);
  }
};

export const restoreSuperAdmin = async (req, res, next) => {
  const correlationId = uuidv4();
  const { adminId } = req.params;
  const { founderSignature, hardwareKeyId } = req.body;

  try {
    // Dual-key restoration required
    const founderVerified = await verifyFounderSignature(founderSignature);
    if (!founderVerified) {
      return res.status(403).json({ error: 'Invalid founder signature' });
    }

    const admin = await SuperAdmin.findOne({ adminId });
    if (!admin) {
      return res.status(404).json({ error: 'Super Admin not found' });
    }

    // Verify hardware key
    const keyValid = admin.verifyHardwareKey(hardwareKeyId, req.body.signature);
    if (!keyValid) {
      return res.status(403).json({ error: 'Hardware key verification failed' });
    }

    admin.status = SUPER_ADMIN_STATUS.ACTIVE;
    admin.killSwitch.restoredAt = new Date();
    admin.killSwitch.restoredBy = getCurrentUser();

    admin.addToForensicChain('SUPER_ADMIN_RESTORED', {
      restoredBy: getCurrentUser(),
      correlationId
    });

    await admin.save();

    await auditLogger.log({
      action: 'SUPER_ADMIN_RESTORED',
      correlationId,
      adminId
    });

    res.json({
      success: true,
      message: 'Super Admin restored',
      status: admin.status
    });

  } catch (error) {
    logger.error('Restore failed', { correlationId, error: error.message });
    next(error);
  }
};

// ============================================================================
// 🕵️ VETTING MANAGEMENT
// ============================================================================

export const initiateVetting = async (req, res, next) => {
  const { adminId } = req.params;

  try {
    const admin = await SuperAdmin.findOne({ adminId });
    if (!admin) {
      return res.status(404).json({ error: 'Super Admin not found' });
    }

    // In production, this would trigger actual third-party vetting services
    const vettingResults = await performThirdPartyVetting(admin.identity);

    admin.vetting.thirdPartyVerification = {
      firm: 'Forensic Security Partners',
      verifiedAt: new Date(),
      certificateHash: vettingResults.certificateHash,
      expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000)
    };

    admin.addToForensicChain('VETTING_COMPLETED', {
      firm: 'Forensic Security Partners',
      verifiedAt: new Date()
    });

    await admin.save();

    res.json({
      success: true,
      vettingCompleted: true,
      expiresAt: admin.vetting.thirdPartyVerification.expiresAt
    });

  } catch (error) {
    next(error);
  }
};

// ============================================================================
// 🛡️ AUDIT & COMPLIANCE
// ============================================================================

export const getAuditTrail = async (req, res, next) => {
  const { adminId } = req.params;

  try {
    const admin = await SuperAdmin.findOne({ adminId })
      .select('+forensicChain +sessions +vetting');

    if (!admin) {
      return res.status(404).json({ error: 'Super Admin not found' });
    }

    res.json({
      adminId: admin.adminId,
      forensicChain: admin.forensicChain,
      vettingHistory: admin.vetting,
      sessionHistory: admin.sessions,
      killSwitchHistory: admin.killSwitch,
      geoFencing: admin.geoFencing,
      timeFencing: admin.timeFencing
    });

  } catch (error) {
    next(error);
  }
};

// ============================================================================
// HELPER FUNCTIONS (In production, these would be actual service calls)
// ============================================================================

async function verifyFounderSignature(signature, founderIndex = 1) {
  // In production: Verify against stored founder public keys
  return signature && signature.length > 10;
}

async function performBackgroundCheck(identity) {
  // In production: Call third-party background check API
  return {
    passed: true,
    reportHash: crypto.createHash('sha256').update(JSON.stringify(identity)).digest('hex'),
    findings: 'No adverse findings'
  };
}

async function storeNDA(email, ip, userAgent) {
  // In production: Store signed NDA in forensic vault
  return crypto.createHash('sha256').update(email + Date.now()).digest('hex');
}

async function performThirdPartyVetting(identity) {
  // In production: Call third-party vetting service
  return {
    certificateHash: crypto.createHash('sha256').update(JSON.stringify(identity)).digest('hex')
  };
}

async function sendOutOfBandAlert(data) {
  // In production: Send via Signal/Telegram API
  console.log('🚨 OOB ALERT:', data);
}

export default {
  createSuperAdmin,
  approveSuperAdmin,
  emergencySuspend,
  restoreSuperAdmin,
  initiateVetting,
  getAuditTrail
};
