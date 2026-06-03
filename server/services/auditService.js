/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN FORENSIC AUDIT SERVICE                                                                                            ║
 * ║ [HMAC-SHA256 CHAINING | COURT-ADMISSIBLE | R50M FRAUD MITIGATION]                                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 16.1.0-SINGULARITY-OMEGA | PRODUCTION READY                                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL GRADE                                                              ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/auditService.js                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Forensic Jurisprudence & Chain of Custody                                                     ║
 * ║ • Gemini (AI Engineering) - Cryptographic Chaining & Persistence Alignment                                                             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import logger from '../utils/logger.js';
import AuditLedger from '../models/AuditLedger.js';
import { getCurrentTenantId, getCurrentUserId, getCurrentRequestId } from '../middleware/tenantContext.js';

class AuditService {
  constructor() {
    this.secret = process.env.AUDIT_SECRET || 'WILSY_OS_CORE_2026_PLATINUM';
  }

  /**
   * @function log
   * @desc Records a cryptographically chained audit entry to the Sovereign Ledger.
   */
  async log(data) {
    const tenantId = getCurrentTenantId();
    const userId = getCurrentUserId();
    const requestId = getCurrentRequestId();

    try {
      // ⛓️ 1. Fetch Latest Entry for Chaining (LPC Rule 35.8 Requirement)
      const lastEntry = await AuditLedger.findOne({ tenantId }).sort({ createdAt: -1 });
      const previousHash = lastEntry ? lastEntry.immutableHash : 'GENESIS_BLOCK';

      // 🔐 2. Generate Forensic HMAC
      const immutableHash = this._generateHash(data, previousHash, tenantId);

      // 🏛️ 3. Persist to Sovereign Ledger
      const auditEntry = await AuditLedger.create({
        tenantId,
        performedBy: userId,
        requestId,
        action: data.action || 'GENERAL_LOG',
        resourceType: data.resourceType || 'SYSTEM',
        resourceId: data.resourceId,
        details: data.details || {},
        previousHash,
        immutableHash,
        ipAddress: data.ipAddress || 'INTERNAL',
        dataResidencyCompliance: 'SA_RESIDENT'
      });

      logger.info(`[AUDIT-LEDGER] 📜 Entry Anchored: ${auditEntry._id} | Hash: ${immutableHash.substring(0, 8)}`);
      return auditEntry;
    } catch (error) {
      logger.error(`[AUDIT-FAULT] 🚨 Failed to anchor forensic trail: ${error.message}`);
      // In a billion-dollar OS, an audit failure should ideally trigger a system freeze (Fail-Closed)
      throw error;
    }
  }

  /**
   * @private
   * @function _generateHash
   */
  _generateHash(data, previousHash, tenantId) {
    const canonicalPayload = JSON.stringify(this._canonicalize({
      data,
      previousHash,
      tenantId
    }));
    return crypto.createHmac('sha256', this.secret).update(canonicalPayload).digest('hex');
  }

  /**
   * @private
   * @function _canonicalize
   * @desc Ensures object key order doesn't break hashes (Deterministic Serializing).
   */
  _canonicalize(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) return obj.map((item) => this._canonicalize(item));
    return Object.keys(obj).sort().reduce((acc, key) => {
      acc[key] = this._canonicalize(obj[key]);
      return acc;
    }, {});
  }
}

export const auditService = new AuditService();
export default auditService;
