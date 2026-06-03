/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - INSTITUTIONAL EMAIL CONTROLLER [V1.0.0-OMEGA-STRIKE]                                                                        ║
 * ║ [DISTRIBUTION ORCHESTRATION | FORENSIC VALIDATION | INVESTOR TELEMETRY | BIBLICAL WORTH]                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-OMEGA | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                      ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/emailController.js                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated decoupled controller architecture for secure investor-grade delivery. [2026-05-04]   ║
 * ║ • AI Engineering (Gemini) - ARCHITECTED: Engineered the strike controller with deterministic forensic seal verification.               ║
 * ║ • AI Engineering (Gemini) - ENHANCED: Integrated multi-target emailService routing for 10/10 production reliability.                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import emailService from '../services/emailService.js';
import { verifyForensicSeal } from '../utils/forensicSigner.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import loggerRaw from '../utils/logger.js';
const logger = loggerRaw.default || loggerRaw;

/**
 * @function sendInvestorReportStrike
 * @description Orchestrates the forensic validation and distribution of consolidated investor artifacts.
 *
 * @param {Object} req - Sovereign Request Object (containing files and trace metadata).
 * @param {Object} res - Sovereign Response Object.
 */
export const sendInvestorReportStrike = async (req, res) => {
  const { subject, recipients, traceId } = req.body;
  const file = req.files?.file;

  try {
    // 🛡️ PHASE 1: FORENSIC SEAL VERIFICATION
    // Validates that the request DNA matches the Institutional Secret Anchor.
    const isAuthorized = verifyForensicSeal(req.headers, req.body);

    if (!isAuthorized) {
      logger.warn(`[SECURITY-STRIKE] 🚨 Unauthorized mail attempt blocked. Trace: ${traceId || 'VOID'}`);
      return res.status(403).json({
        status: 'FRACTURE',
        message: 'CRYPTOGRAPHIC_SEAL_INVALID',
        audit: 'REJECTED'
      });
    }

    // 🛡️ PHASE 2: ARTIFACT INTEGRITY CHECK
    if (!file || !file.data) {
      throw new Error('INSTITUTIONAL_ARTIFACT_NULL');
    }

    const targetRecipients = JSON.parse(recipients || '[]');
    if (!targetRecipients.length) {
      throw new Error('DISTRIBUTION_TARGETS_MISSING');
    }

    logger.info(`[MAIL-CONTROLLER] 🛰️  Executing Investor Strike | Trace: ${traceId} | Targets: ${targetRecipients.length}`);

    // 🛡️ PHASE 3: SERVICE DISPATCH
    // Hands off the binary buffer to the high-velocity Sovereign Email Service.
    const result = await emailService.sendInvestorReport(
      targetRecipients,
      file.data,
      traceId
    );

    if (!result.success) {
      throw new Error(result.error || 'SERVICE_DISPATCH_FAILURE');
    }

    // 🛡️ PHASE 4: AUDIT LOGGING
    // Finalizes the telemetry loop for the live dashboard feed.
    await broadcastTelemetry('INVESTOR_REPORT_DISPATCHED', {
      traceId,
      status: 'SUCCESS',
      recipients: targetRecipients.length,
      artifactName: file.name
    });

    res.status(200).json({
      status: 'SENT',
      traceId,
      messageId: result.messageId,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error(`💥 [CONTROLLER-FRACTURE] Investor Strike Failed: ${error.message}`);

    // Broadcast the failure to the Risk Sentinel
    await broadcastTelemetry('INVESTOR_REPORT_DISPATCHED', {
      traceId,
      status: 'FAILURE',
      error: error.message
    });

    res.status(500).json({
      status: 'FRACTURE',
      message: 'STRIKE_EXECUTION_FAILED',
      error: error.message
    });
  }
};

export default {
  sendInvestorReportStrike
};
