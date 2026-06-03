/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TRUST ACCOUNT CONTROLLER [V33.65.0-OMEGA-FIDUCIARY]                                                                         ║
 * ║ [LPC RULE 54 COMPLIANT | R10B+ ATOMIC FINALITY | FORENSIC AUDITABLE | TRACE-AWARE]                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 33.65.0-OMEGA | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                    ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/TrustAccountController.js                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated R10B+ atomic finality and courtroom-ready fiduciary forensics. [2026-05-04]           ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Aligned Trace-ID logic with V33.45.0 Master API Nexus and V33.37 Telemetry.                     ║
 * ║ • AI Engineering (Gemini) - ENHANCED: Hardened the Forensic Echo strike for sub-ms boardroom visibility.                               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { performance } from 'node:perf_hooks';
import { lpcService } from '../services/lpcService.js';
import { TrustAccount } from '../models/TrustAccount.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import logger from '../utils/logger.js';

/**
 * ⚛️ SOVEREIGN WRAPPER
 * Orchestrates zero-dependency promise handling for institutional-grade reliability.
 */
const nativeAsync = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

class TrustAccountController {
  /**
   * ⚖️ HANDLE TRANSACTION
   * Processes biblical fiduciary movements anchored to LPC Rule 54 and Citadel Trace-IDs.
   */
  handleTransaction = nativeAsync(async (req, res) => {
    const startTime = performance.now();
    // RECTIFIED: Prioritizing the institutional Trace-ID from the V33 Master Nexus
    const traceId = req.traceId || req.headers['x-trace-id'] || `TRC-TRUST-${Date.now()}`;

    // 🛡️ CITADEL CONTEXT
    const tenantId = req.user.tenantId;
    const userId = req.user.id || req.user._id;

    try {
      // Execute the Fiduciary Movement via the LPC Service Layer
      const result = await lpcService.recordTransaction(tenantId, {
        ...req.body,
        initiatedBy: userId,
        forensicId: traceId
      });

      const duration = (performance.now() - startTime).toFixed(2);

      // 📡 FORENSIC ECHO: Fiduciary movement pulse
      await broadcastTelemetry(tenantId, 'FIDUCIARY_STRIKE_SUCCESS', userId, 'TRUST_TX_COMMITTED', {
        amount: req.body.amount,
        traceId,
        latencyMs: duration
      });

      logger.info(`[LPC-FIDUCIARY] ⚖️ Transaction Anchored | Trace: ${traceId} | ${duration}ms`);

      res.status(201).json({
        success: true,
        data: result,
        traceId,
        metrics: { latencyMs: duration }
      });
    } catch (err) {
      logger.error(`[LPC-FAULT] 🚨 ${traceId} - ${err.message}`);

      await broadcastTelemetry(tenantId, 'FIDUCIARY_STRIKE_FAILURE', userId, 'TRUST_TX_ABORTED', {
        error: err.message,
        traceId
      });

      res.status(400).json({
        success: false,
        error: err.message,
        traceId
      });
    }
  });

  /**
   * 📜 GET LEDGER
   * Retrieves the immutable institutional ledger anchored to the Sovereign Nucleus.
   */
  getLedger = nativeAsync(async (req, res) => {
    const traceId = req.traceId || req.headers['x-trace-id'] || `TRC-LEDGER-${Date.now()}`;
    const tenantId = req.user.tenantId;

    const account = await TrustAccount.findOne({ tenantId })
      .populate('transactions.entityId', 'name email');

    if (!account) {
      return res.status(404).json({
        success: false,
        error: 'LEDGER_NOT_FOUND',
        message: 'No fiduciary anchor found for this institutional shard.',
        traceId
      });
    }

    res.status(200).json({
      success: true,
      data: {
        balance: account.currentBalance,
        currency: account.currency || 'ZAR',
        lastUpdated: account.updatedAt,
        transactions: account.transactions
      },
      traceId
    });
  });
}

export const trustAccountController = new TrustAccountController();
export default trustAccountController;
