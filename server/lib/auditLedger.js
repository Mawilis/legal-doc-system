/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FORENSIC AUDIT LEDGER BRIDGE [V16.0.0-MARS]                                                                                 ║
 * ║ [CYBERCRIMES ACT COMPLIANT | CRYPTOGRAPHIC VERIFICATION BRIDGE | ATOMIC TRANSACTION SECURED]                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 16.0.0-MARS | PRODUCTION READY | BILLION DOLLAR SPEC                                                                          ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/lib/auditLedger.js                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & ARCHITECTURAL LOG:                                                                                                  ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated an unalterable forensic logging bridge for multi-tenant service interactions.        ║
 * ║ • AI Engineering (Gemini) - FORGED: Unified transaction parsing with Keccak256/SHA-256 integrity tags and structural validation.      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import AuditTrail from '../models/AuditTrail.js';
import { generateEventHash } from '../utils/eventHashGenerator.js';
import logger from '../utils/logger.js';

/**
 * Appends a discrete system or document event into the immutable historical log.
 * Aligned with the South African Cybercrimes Act 19 of 2020 tracking procedures.
 * @param {Object} entryData - The structured metadata describing the action.
 * @param {string} entryData.tenantId - Unique identifier of the calling firm.
 * @param {string} entryData.action - System operation tag (e.g., DOCUMENT_CREATE).
 * @param {string} entryData.resourceType - Affected entity group (e.g., DOCUMENT, CASE).
 * @param {string} entryData.resourceId - Domain identification string.
 * @param {string} entryData.actor - Identifier of the operating user or API key.
 * @param {Object} entryData.details - Non-PII business trace payload.
 * @param {string} [entryData.severity='INFO'] - Incident urgency category.
 * @returns {Promise<string>} Cryptographic hash of the locked log entry.
 */
export async function appendAuditEntry(entryData) {
  const {
    tenantId,
    action,
    resourceType,
    resourceId,
    actor,
    details = {},
    severity = 'INFO'
  } = entryData;

  // 🛡️ Fail-Closed Input Sanity Protocols
  if (!tenantId) throw new Error('FORENSIC_FRACTURE: Cannot append log without a distinct tenantId context.');
  if (!action) throw new Error('FORENSIC_FRACTURE: Action categorization is required to construct entry parameters.');

  const timestamp = new Date();
  const eventId = `AUD-LGR-${timestamp.getTime()}-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;

  try {
    // Construct the deterministic normalization payload
    const logPayload = {
      eventId,
      timestamp: timestamp.toISOString(),
      tenantId,
      actor,
      action,
      resourceType,
      resourceId,
      details: JSON.stringify(details),
      severity
    };

    // Calculate cryptographic integrity seal via master engine
    const cryptographicSeal = generateEventHash(logPayload, { includeTimestamp: false });

    // Instantiation onto permanent collection store
    const record = new AuditTrail({
      eventId,
      eventHash: cryptographicSeal.hash,
      timestamp,
      user: {
        id: actor || 'SYSTEM_DAEMON',
        role: severity === 'ERROR' ? 'SYSTEM_ALERT' : 'OPERATOR',
        tenantId
      },
      action: {
        method: 'INTERNAL_BRIDGE',
        url: `/services/${resourceType.toLowerCase()}/${action.toLowerCase()}`,
        endpoint: resourceType,
        category: mapActionToCategory(action)
      },
      network: {
        ipAddress: '127.0.0.1',
        userAgent: 'Wilsy-OS-Core-Forensic-Bridge'
      },
      result: {
        statusCode: severity === 'ERROR' ? 500 : 200,
        responseTimeMs: 0
      },
      compliance: {
        legalBasis: 'Cybercrimes Act 19 of 2020 (Section 3 Monitoring Logs)',
        jurisdiction: 'ZA',
        retentionPeriodDays: 3650 // 10-Year Archival Matrix Lock
      },
      quantumSignature: {
        hash: cryptographicSeal.hash,
        algorithm: cryptographicSeal.algorithm
      }
    });

    await record.save();
    return cryptographicSeal.hash;

  } catch (error) {
    // Fallback logging matrix to console stdout to avoid black-holing failures
    logger.error(`[AUDIT-LEDGER-CRITICAL] Failed to execute commit phase to database: ${error.message}`);
    throw new Error(`LEDGER_COMMIT_FAILURE: ${error.message}`);
  }
}

/**
 * Internally maps service operations to compliant taxonomy groups
 * @private
 */
function mapActionToCategory(action) {
  if (action.includes('CREATE') || action.includes('MODIFY') || action.includes('UPDATE')) return 'DOC_MODIFY';
  if (action.includes('ACCESS') || action.includes('VIEW') || action.includes('RETRIEVE')) return 'DOC_ACCESS';
  if (action.includes('AUTH') || action.includes('LOGIN')) return 'AUTH';
  if (action.includes('SECURITY') || action.includes('BREACH')) return 'SECURITY';
  return 'SYSTEM';
}

// Default orchestration block export
export default {
  appendAuditEntry
};
