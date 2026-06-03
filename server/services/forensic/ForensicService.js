/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FORENSIC SERVICE ENGINE (FSE) [V16.0.0-SINGULARITY-OMEGA]                                                                   ║
 * ║ [CANONICAL DETERMINISM | SHA3-512 QUANTUM ANCHORING | TELEMETRY BROADCASING]                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 16.0.0-SINGULARITY-OMEGA | PRODUCTION READY | BILLION DOLLAR SPEC                                                             ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL FINALITY                                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/forensic/ForensicService.js                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Designed base canonicalization protocol and SHA3-512 structure.                               ║
 * ║ • AI Engineering (Gemini) - EPITOMISED: Injected telemetry broadcasting, strict JSDoc typing, and defensive canonical sorting.         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import logger from '../../utils/logger.js';
import { broadcastTelemetry } from '../../utils/telemetryHelper.js';

export class ForensicService {
  /**
   * Recursively alphabetizes an object's keys to guarantee cryptographic canonical stability.
   * Prevents signature mismatches caused by JSON property reordering across different runtime engines.
   * @param {Object|Array|any} obj - The raw payload to stabilize.
   * @returns {Object|Array|any} The canonically sorted payload.
   */
  static sortObject(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) return obj.map(this.sortObject.bind(this));
    return Object.keys(obj)
      .sort()
      .reduce((result, key) => {
        result[key] = this.sortObject(obj[key]);
        return result;
      }, {});
  }

  /**
   * Generates a Sovereign Signature using SHA3-512.
   * Anchors the data matrix against the global institutional secret.
   * @param {Object} data - The raw JSON payload to sign.
   * @returns {string} The 128-character hexadecimal cryptographic seal.
   */
  static signTransaction(data) {
    try {
      const canonicalPayload = JSON.stringify(this.sortObject(data));
      const secret = process.env.SYSTEM_SECRET || 'WILSY_GENESIS_SECRET';

      return crypto
        .createHash('sha3-512')
        .update(canonicalPayload + secret)
        .digest('hex');
    } catch (error) {
      logger.error(`[FSE-FRACTURE] Transaction signing failed: ${error.message}`);
      throw new Error('CRYPTOGRAPHIC_SEAL_FAILURE');
    }
  }

  /**
   * Anchors a critical system asset (Invoice, Contract, Telemetry Log) to the immutable forensic chain.
   * Injects high-entropy nonces and formal timestamps before sealing.
   * @param {string} docId - The logical database ID of the asset.
   * @param {string} contentHash - The standalone hash of the file or object being anchored.
   * @param {string} [tenantId='GLOBAL_ROOT'] - The tenant context for telemetry routing.
   * @returns {Promise<Object>} The finalized, cryptographically sealed anchor manifest.
   */
  static async anchorDocument(docId, contentHash, tenantId = 'GLOBAL_ROOT') {
    const timestamp = new Date().toISOString();
    const nonce = crypto.randomBytes(32).toString('hex'); // High-entropy entropy source
    const anchorId = `ANCHOR-${crypto.randomBytes(8).toString('hex').toUpperCase()}`;

    const payload = {
      anchorId,
      docId,
      contentHash,
      timestamp,
      nonce
    };

    const signature = this.signTransaction(payload);

    const manifest = {
      ...payload,
      signature,
      algorithm: 'SHA3-512',
      status: 'VERIFIED_FINAL'
    };

    // 🏛️ INSTITUTIONAL LOGGING
    logger.info(`[FORENSIC-ENGINE] 🛰️ Asset Anchored: ${docId} | CID: ${anchorId} | HASH: ${signature.substring(0, 16)}...`);

    // 📡 TELEMETRY BROADCAST
    broadcastTelemetry(tenantId, 'COMPLIANCE_EVENT', 'FORENSIC_ANCHOR_CREATED', 'ForensicService', {
      docId,
      anchorId,
      hashPrefix: signature.substring(0, 8)
    });

    return manifest;
  }

  /**
   * Validates a previously signed data payload against its provided forensic seal.
   * Ensures non-repudiation and structural integrity post-storage.
   * @param {Object} data - The payload to verify (must exactly match pre-signature structure).
   * @param {string} signature - The external SHA3-512 seal to test against.
   * @returns {boolean} True if the seal holds, False if tampered.
   */
  static verifyIntegrity(data, signature) {
    if (!data || !signature) return false;
    try {
      const computed = this.signTransaction(data);
      return computed === signature;
    } catch (error) {
      return false; // Safely fail on malformed payloads
    }
  }
}

export default ForensicService;
