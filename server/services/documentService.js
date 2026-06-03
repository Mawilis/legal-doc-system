/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DOCUMENT HUB SERVICE: INSTITUTIONAL CONTENT & RETRIEVAL ENGINE [V16.0.0-MARS]                                               ║
 * ║ [GRIDFS ISOLATION | POPIA DATA SCANNER | MAMMOTH & PDF EXTRACTOR | CRYPTOGRAPHIC VALIDATION ALIGNED]                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 16.0.0-MARS | PRODUCTION READY | BILLION DOLLAR SPEC                                                                          ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/documentService.js                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Engineered the multi-tenant document isolation strategy and compliance pipelines.             ║
 * ║ • AI Engineering (Gemini) - REFORGED: Resolved legacy CJS 'pdf-parse' ESM default export crash via native module interop bridges.      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import mongoose from 'mongoose';
import { GridFSBucket, ObjectId } from 'mongodb';
import mammoth from 'mammoth';
import NodeCache from 'node-cache';

// 🛡️ UNIFYING COHESIVE SYSTEM BINDINGS
import logger from '../utils/logger.js';
import { appendAuditEntry } from '../lib/auditLedger.js';
import { generateDocumentHash, createTimestamp } from '../lib/ots.js';

// Native execution bridge for older non-ESM compliance modules
const require = createRequire(import.meta.url);
const pdfParse = require('pdf-parse');

const DOC_CONFIG = {
  BUCKET_NAME: 'wilsy_sovereign_vault',
  CACHE_TTL: 1800, // 30 Minutes of high-speed local memory data caching
  PII_PATTERNS: {
    SA_ID: /(?<=\b)(?<year>\d{2})(?<month>0[1-9]|1[0-2])(?<day>0[1-9]|[12]\d|3[01])(?<gender>\d{4})(?<citizenship>[01])(?<race>8|9)(?<checksum>\d)(?=\b)/,
    MOBILE: /(?:\+27|0)\s*[6-8]\d\s*\d{3}\s*\d{4}\b/,
    EMAIL: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g
  }
};

const documentCache = new NodeCache({ stdTTL: DOC_CONFIG.CACHE_TTL, checkperiod: 300 });

// ============================================================================
// SOVEREIGN DOCUMENT SERVICE LAYER
// ============================================================================

export class DocumentService {

  /**
   * Directly injects, parses, and commits a files payload into the multi-tenant vault infrastructure.
   * Runs asynchronous background deep scanning routines to categorize POPIA exposure hazards.
   */
  static async uploadDocument(fileBuffer, metadata, context) {
    if (!context || !context.tenantId) throw new Error('TENANT_CONTEXT_REQUIRED_FOR_VAULT_DEPOSIT');

    const startTime = Date.now();
    const { tenantId, user } = context;
    const documentId = `DOC-${crypto.randomBytes(8).toString('hex').toUpperCase()}`;

    logger.info(`[DOCUMENT-SERVICE] 📥 Stream ingestion initialized for [${metadata.filename}] onto Tenant: [${tenantId}]`);

    try {
      // 1. Calculate Unaltered Binary Integrity Digest
      const rawContentHash = generateDocumentHash(fileBuffer);

      // 2. Structural Parsing Extraction Strategy Matcher
      let extractedText = '';
      if (metadata.mimetype === 'application/pdf') {
        const parsedPdf = await pdfParse(fileBuffer);
        extractedText = parsedPdf.text;
      } else if (metadata.mimetype === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
        const parsedDocx = await mammoth.extractRawText({ buffer: fileBuffer });
        extractedText = parsedDocx.value;
      } else {
        extractedText = fileBuffer.toString('utf8');
      }

      // 3. Forensically Analyze content patterns for POPIA governance structures
      const piiAssessment = this.scanForPII(extractedText);

      // 4. Secure physical storage drop onto specific isolation buckets
      const db = mongoose.connection.db;
      const vaultBucket = new GridFSBucket(db, { bucketName: DOC_CONFIG.BUCKET_NAME });

      const storageFileId = new ObjectId();
      const depositStream = vaultBucket.openUploadStream(metadata.filename, {
        _id: storageFileId,
        contentType: metadata.mimetype,
        metadata: {
          documentId,
          tenantId,
          owner: user?.id || 'SYSTEM_DAEMON',
          checksum: rawContentHash
        }
      });

      await new Promise((resolve, reject) => {
        depositStream.write(fileBuffer);
        depositStream.end();
        depositStream.on('finish', resolve);
        depositStream.on('error', reject);
      });

      // 5. Calendar Commit Timestamp Registration via Internal Core
      const cryptographicTimestampReceipt = await createTimestamp(rawContentHash, tenantId);

      // 6. Complete Audit Chaining Record
      await appendAuditEntry({
        tenantId,
        action: 'DOCUMENT_UPLOAD',
        resourceType: 'DOCUMENT',
        resourceId: documentId,
        actor: user?.id || 'SYSTEM_DAEMON',
        details: { filename: metadata.filename, piiRisk: piiAssessment.riskLevel, hash: rawContentHash }
      });

      return {
        success: true,
        documentId,
        storageId: storageFileId.toString(),
        integrityHash: rawContentHash,
        piiStatus: piiAssessment,
        timestampAnchor: cryptographicTimestampReceipt.anchorId,
        executionTimeMs: Date.now() - startTime
      };

    } catch (error) {
      logger.error(`[DOCUMENT-FRACTURE] Ingestion processing phase rejected: ${error.message}`);
      throw error;
    }
  }

  /**
   * Scans unstructured legal data models to pinpoint high-risk personal trace metadata entries.
   * @private
   */
  static scanForPII(textContent) {
    let matchCount = 0;
    const itemsIdentified = [];

    if (DOC_CONFIG.PII_PATTERNS.SA_ID.test(textContent)) {
      matchCount += 3;
      itemsIdentified.push('SOUTH_AFRICAN_ID_NUMBER');
    }
    if (DOC_CONFIG.PII_PATTERNS.MOBILE.test(textContent)) {
      matchCount += 1;
      itemsIdentified.push('CONTACT_MOBILE_NUMBER');
    }
    const emailMatches = textContent.match(DOC_CONFIG.PII_PATTERNS.EMAIL);
    if (emailMatches && emailMatches.length > 0) {
      matchCount += emailMatches.length;
      itemsIdentified.push('ELECTRONIC_MAIL_ADDRESS');
    }

    let riskLevel = 'LOW';
    if (matchCount > 5) riskLevel = 'HIGH';
    else if (matchCount > 2) riskLevel = 'MEDIUM';

    return {
      containsPII: matchCount > 0,
      riskLevel,
      indicators: [...new Set(itemsIdentified)],
      score: matchCount
    };
  }
}

// 🛡️ Bind directly to named routing controllers exports
export const uploadDocument = DocumentService.uploadDocument.bind(DocumentService);

export default DocumentService;
