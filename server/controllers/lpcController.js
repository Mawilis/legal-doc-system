/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - LPC REGULATORY CONTROLLER - OMEGA SINGULARITY                                                                               ║
 * ║ [FIDUCIARY ORCHESTRATION | SHA3-512 RECURSIVE VALIDATION | R10B+ AUDITABLE]                                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 15.2.0-SINGULARITY-OMEGA | PRODUCTION READY                                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | 100-YEAR AUDIT TRAIL | NO CHILD'S PLACE                                                           ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * * 🏛️ ARCHITECT: Wilson Khanyezi – 10th Generation Sovereign Architect
 */

import { lpcService } from '../services/lpcService.js';
import cryptoUtils from '../utils/cryptoUtils.js';

/**
 * @function nativeAsync
 * @desc Sovereign wrapper for zero-dependency promise handling.
 */
const nativeAsync = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

/**
 * @desc Atomic Trust Summary retrieval with Master Integrity Seal verification.
 */
export const getTrustAccountSummary = nativeAsync(async (req, res) => {
  const tenantId = req.user.tenantId;
  const summary = await lpcService.initializeTrustAccount(tenantId); // Ensures account exists or returns current

  res.status(200).json({
    success: true,
    masterIntegritySeal: summary.masterIntegritySeal,
    data: {
      accountNumber: summary.accountNumber,
      balance: summary.currentBalance,
      lastTransaction: summary.lastTransactionAt
    }
  });
});

/**
 * @desc Process Fiduciary Transaction with SHA3-512 Recursive Chaining.
 */
export const processTrustTransaction = nativeAsync(async (req, res) => {
  const tenantId = req.user.tenantId;
  const userId = req.user._id;
  const requestId = req.id || cryptoUtils.generateForensicId('LPC-TX');

  const result = await lpcService.recordTransaction(tenantId, {
    ...req.body,
    initiatedBy: userId,
    forensicId: requestId
  });

  res.status(201).json({
    success: true,
    transactionId: result.transactionId,
    forensicHash: result.forensicHash,
    forensicTrace: requestId
  });
});

/**
 * @desc Submit CPD Activity for Forensic Verification.
 */
export const submitCPDActivity = nativeAsync(async (req, res) => {
  const tenantId = req.user.tenantId;
  const cpd = await lpcService.recordTransaction(tenantId, {
    ...req.body,
    type: 'FEE_EARNED', // CPD activities often link to forensic fee recognition
    description: `CPD_ACTIVITY: ${req.body.activityName}`
  });

  res.status(201).json({
    success: true,
    activityId: cpd.transactionId,
    forensicHash: cpd.forensicHash
  });
});

/**
 * @desc Generate LPC Forensic Export for 100-Year Audit.
 */
export const generateLPCForensicExport = nativeAsync(async (req, res) => {
  const tenantId = req.user.tenantId;
  const archiveData = await lpcService.getFinancialSnapshot(tenantId); // Re-using engine for export logic

  res.status(200).json({
    success: true,
    timestamp: new Date(),
    data: archiveData,
    message: 'Forensic archive generated for Sovereign Audit.'
  });
});

export default {
  getTrustAccountSummary,
  processTrustTransaction,
  submitCPDActivity,
  generateLPCForensicExport
};
