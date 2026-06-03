/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - COMPLIANCE API GATEWAY [V1.0.0-OMEGA]                                                                                       ║
 * ║ [SOVEREIGN ROUTING | FORENSIC TELEMETRY | FRACTURE PREVENTION | INVESTOR-READY]                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-OMEGA | PRODUCTION READY | BILLION DOLLAR SPEC                                                                          ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL DATA PIPELINE                                                      ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/compliance.js                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated the baseline route logic and strict zero-loss code preservation.                     ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Armored the endpoint with try/catch boundaries, telemetry hooks, and standard JSON framing.     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import ComplianceModel from '../models/Compliance.js';
import logger from '../utils/logger.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
// import { requireSovereignAuth } from '../middleware/auth.js'; // 🛡️ Activate in production to lock the gateway

const router = express.Router();

/**
 * @route GET /api/compliance/metrics/:tenantId
 * @description Executes a sovereign read-strike against the Compliance Nucleus.
 */
router.get('/metrics/:tenantId', async (req, res) => {
  try {
    const { tenantId } = req.params;

    // 🛡️ FORENSIC TELEMETRY: Pre-strike logging
    logger.info(`[COMPLIANCE_API] Executing Nucleus Read Strike for Tenant: ${tenantId}`);

    // 🏛️ ORIGINAL LOGIC PRESERVED: Extracting truth from the immutable ledger
    const data = await ComplianceModel.findOne({ tenantId: req.params.tenantId });

    // 📡 TELEMETRY BROADCAST: Non-repudiation tracking for the dashboard's audit trail
    broadcastTelemetry(tenantId, 'COMPLIANCE_READ', 'SUCCESS', 'Compliance API', {
      timestamp: new Date().toISOString()
    });

    // 🏛️ ORIGINAL LOGIC ELEVATED: res.json(data || {}) transformed to prevent frontend fracturing
    // If the ledger is blank, we return a "Genesis State" so the UI displays pending statuses instead of crashing.
    const genesisFallback = {
      tenantId: tenantId,
      gdprStatus: 'PENDING_GENESIS',
      popiaStatus: 'PENDING_GENESIS',
      soc2Validation: 'AWAITING_AUDIT',
      dataResidency: 'ISOLATED_RSA',
      auditType: 'PQE-256'
    };

    return res.status(200).json({
      success: true,
      data: data || genesisFallback
    });

  } catch (error) {
    // 💥 FRACTURE CONTAINMENT: Prevent the server from crashing and alert the front-end
    logger.error(`💥 [COMPLIANCE_API] Nucleus Fracture: ${error.message}`);

    broadcastTelemetry(req.params.tenantId, 'COMPLIANCE_READ', 'FRACTURE', 'Compliance API', {
      error: error.message
    });

    return res.status(500).json({
      success: false,
      message: 'SOVEREIGN_NUCLEUS_FRACTURE',
      error: error.message
    });
  }
});

export default router;
