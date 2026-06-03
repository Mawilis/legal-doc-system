/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN CASE ORCHESTRATOR - OMEGA SINGULARITY                                                                             ║
 * ║ [R23.7T CASE GOVERNANCE | RULE 35 DISCOVERY | FORENSIC INTEGRITY | POPIA §19]                                                          ║
 * ║ VERSION: 15.0.0-SINGULARITY                                                                                                            ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE                                                                                    ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/caseFileController.js                                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import archiver from 'archiver';
import mongoose from 'mongoose';
import CaseFile from '../models/caseFileModel.js';
import SovereignAudit from '../models/SovereignAudit.js';
import auditLogger from '../utils/auditLogger.js';
import cryptoUtils from '../utils/cryptoUtils.js';
import logger from '../utils/logger.js';
import { getCurrentTenant, getCurrentUser, getCurrentRequestId } from '../middleware/tenantContext.js';

/* ---------------------------------------------------------------------------
   1. CASE GOVERNANCE (CRUD & Lifecycle)
   --------------------------------------------------------------------------- */

/**
 * @function createCase
 * @description Opens a new Legal Case File within the firm's sovereign boundary.
 */
export const createCase = async (req, res) => {
  const traceId = getCurrentRequestId();
  const tenantId = getCurrentTenant();
  const userId = getCurrentUser();

  try {
    const newCase = await CaseFile.create({
      ...req.body,
      tenantId,
      createdBy: userId,
      status: 'active',
      forensicHash: cryptoUtils.generateForensicId('CASE-HASH')
    });

    await auditLogger.log({
      action: 'CASE_OPENED',
      category: 'LEGAL',
      resource: newCase._id,
      metadata: { caseNumber: newCase.caseNumber, traceId }
    });

    res.status(201).json({ success: true, data: newCase });
  } catch (error) {
    logger.error(`[CASE-INIT-FAIL] ${error.message}`, { traceId });
    res.status(500).json({ success: false, error: 'Sovereign Case Initialization Fault.' });
  }
};

/**
 * @function getCases
 * @description Retrieves cases scoped strictly to the authenticated Law Firm.
 */
export const getCases = async (req, res) => {
  const tenantId = getCurrentTenant();
  try {
    const { page = 1, limit = 20, status } = req.query;
    const query = { tenantId };
    if (status) query.status = status;

    const [cases, total] = await Promise.all([
      CaseFile.find(query)
        .sort({ updatedAt: -1 })
        .skip((page - 1) * limit)
        .limit(parseInt(limit))
        .populate('createdBy', 'name email'),
      CaseFile.countDocuments(query),
    ]);

    res.json({
      success: true,
      data: cases,
      pagination: { total, page, pages: Math.ceil(total / limit) },
    });
  } catch (error) {
    logger.error(`[CASE-QUERY-FAIL] ${error.message}`);
    res.status(500).json({ success: false, error: 'Sovereign Query Failure.' });
  }
};

/**
 * @function getCaseDetails
 * @description Forensic deep-dive into a single case file.
 */
export const getCaseDetails = async (req, res) => {
  const tenantId = getCurrentTenant();
  try {
    const caseFile = await CaseFile.findOne({
      _id: req.params.id,
      tenantId,
    }).populate('documents');

    if (!caseFile) {
      return res.status(404).json({ error: 'Case File not found or access denied.' });
    }

    await auditLogger.log({
      action: 'CASE_VIEWED',
      category: 'LEGAL',
      resource: caseFile._id,
      severity: 'low',
      metadata: { caseId: caseFile._id },
    });

    res.json({ success: true, data: caseFile });
  } catch (error) {
    logger.error(`[CASE-RETRIEVAL-FAULT] ${error.message}`);
    res.status(500).json({ error: 'Case retrieval fault.' });
  }
};

/* ---------------------------------------------------------------------------
   2. HIGH COURT DISCOVERY (The Billion-Dollar Engine)
   --------------------------------------------------------------------------- */

/**
 * @function generateDiscoveryBundle
 * @description Streams a zipped discovery bundle (Rule 35) for court submission.
 */
export const generateDiscoveryBundle = async (req, res) => {
  const traceId = getCurrentRequestId();
  const tenantId = getCurrentTenant();

  try {
    const caseFile = await CaseFile.findOne({ _id: req.params.id, tenantId });
    if (!caseFile) return res.status(404).json({ error: 'Case not found.' });

    res.attachment(`Discovery_Bundle_${caseFile.caseNumber}.zip`);
    const archive = archiver('zip', { zlib: { level: 9 } });
    archive.pipe(res);

    archive.append(`Sovereign Discovery Index\nCase: ${caseFile.caseNumber}\nTrace: ${traceId}\nGenerated: ${new Date()}`, {
      name: 'INDEX.txt',
    });

    // In production, stream from S3/GridFS here
    if (caseFile.documents && caseFile.documents.length > 0) {
      // archive.file(...) would be used with actual file streams
    }

    await auditLogger.log({
      action: 'DISCOVERY_BUNDLE_EXPORTED',
      category: 'LEGAL',
      resource: caseFile._id,
      severity: 'high',
      metadata: { caseId: caseFile._id, traceId },
    });

    await archive.finalize();
  } catch (error) {
    logger.error(`[DISCOVERY-FAULT] ${error.message}`, { traceId });
    if (!res.headersSent) res.status(500).json({ error: 'Bundle generation failure.' });
  }
};

/* ---------------------------------------------------------------------------
   3. ADVANCED LEGAL ACTIONS
   --------------------------------------------------------------------------- */

/**
 * @function transitionCaseStatus
 * @description Moves a case through the legal lifecycle (Active -> Litigated -> Closed).
 */
export const transitionCaseStatus = async (req, res) => {
  const tenantId = getCurrentTenant();
  const userId = getCurrentUser();
  try {
    const { status, reason } = req.body;
    const caseFile = await CaseFile.findOneAndUpdate(
      { _id: req.params.id, tenantId },
      {
        status,
        $push: {
          timeline: {
            status,
            reason,
            date: new Date(),
            actor: userId,
          },
        },
      },
      { new: true }
    );

    if (!caseFile) return res.status(404).json({ error: 'Case not found.' });

    await auditLogger.log({
      action: 'CASE_STATUS_TRANSITION',
      category: 'LEGAL',
      resource: caseFile._id,
      severity: 'info',
      metadata: { caseId: caseFile._id, newStatus: status },
    });

    res.json({ success: true, data: caseFile });
  } catch (error) {
    logger.error(`[STATUS-TRANSITION-FAIL] ${error.message}`);
    res.status(500).json({ error: 'Status transition failed.' });
  }
};

/**
 * @function archiveCase
 * @description Cold-storage for legal compliance (Must keep for 7 years per Law Society).
 */
export const archiveCase = async (req, res) => {
  const tenantId = getCurrentTenant();
  try {
    const caseFile = await CaseFile.findOneAndUpdate(
      { _id: req.params.id, tenantId },
      { status: 'archived', archivedAt: new Date() },
      { new: true }
    );

    if (!caseFile) return res.status(404).json({ error: 'Case not found.' });

    await auditLogger.log({
      action: 'CASE_ARCHIVED',
      category: 'LEGAL',
      resource: caseFile._id,
      severity: 'medium',
      metadata: { caseId: req.params.id },
    });

    res.json({ success: true, message: 'Case File moved to Cold Storage.' });
  } catch (error) {
    logger.error(`[ARCHIVAL-FAULT] ${error.message}`);
    res.status(500).json({ error: 'Archival fault.' });
  }
};

/**
 * @function deleteCase
 * @description Hard-delete (restricted to SuperAdmins/Owners) for POPIA compliance.
 */
export const deleteCase = async (req, res) => {
  const tenantId = getCurrentTenant();
  const user = getCurrentUser(); // assuming user object available via context
  try {
    // Only allow if user is OWNER or SUPER_ADMIN (role check from context)
    const userRole = user?.role; // adjust based on your context structure
    if (userRole !== 'OWNER' && userRole !== 'SUPER_ADMIN') {
      return res.status(403).json({ error: 'Insufficient clearance to expunge Case Files.' });
    }

    const caseFile = await CaseFile.findOneAndDelete({ _id: req.params.id, tenantId });
    if (!caseFile) return res.status(404).json({ error: 'Case not found.' });

    await auditLogger.log({
      action: 'CASE_EXPUNGED',
      category: 'LEGAL',
      resource: caseFile._id,
      severity: 'critical',
      metadata: { caseNumber: caseFile.caseNumber },
    });

    res.json({ success: true, message: 'Case expunged from Sovereign Ledger.' });
  } catch (error) {
    logger.error(`[EXPUNGEMENT-FAIL] ${error.message}`);
    res.status(500).json({ error: 'Expungement failed.' });
  }
};

// Default export for backward compatibility if needed
export default {
  createCase,
  getCases,
  getCaseDetails,
  generateDiscoveryBundle,
  transitionCaseStatus,
  archiveCase,
  deleteCase,
};
