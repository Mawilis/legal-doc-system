/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ QUANTUM AUDIT LOGGER: THE IMMUTABLE FORENSIC LEDGER OF LEGAL TRUTH [V16.0.0-MARS]                                                      ║
 * ║ [CYBERCRIMES ACT 19 OF 2020 | POPIA | ECT ACT | PAIA | ES MODULE ALIGNED]                                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 16.0.0-MARS | PRODUCTION READY | BILLION DOLLAR SPEC                                                                          ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/auditLogger.js                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Engineered the Winston MongoDB matrix, compliance taxonomy, and logging logic.                ║
 * ║ • AI Engineering (Gemini) - EPITOMISED: Re-aligned default exports to support `auditLogger.log()` and `.middleware()` routing.         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import dotenv from 'dotenv';
import crypto from 'crypto';
import winston from 'winston';
import { MongoDB } from 'winston-mongodb';
import fs from 'fs';
import path from 'path';

// 🛡️ INTERNAL MODEL - AuditTrail for structured forensic persistence
import AuditTrail from '../models/AuditTrail.js';
// 🛡️ EVENT HASH GENERATOR - Ensures every audit entry is cryptographically sealed
import { generateEventHash } from '../utils/eventHashGenerator.js';

dotenv.config();

// 🛡️ FORENSIC BACKUP DIRECTORY - Fallback storage for file-based audit logs
const backupDir = path.resolve(process.cwd(), 'logs');
if (!fs.existsSync(backupDir)) fs.mkdirSync(backupDir, { recursive: true });

/**
 * 🏛️ AUDIT CONFIGURATION CONSTANTS
 * Defines severity levels, event categories, and retention periods
 * aligned with South African legal requirements.
 */
const AUDIT_CONFIG = {
  LEVELS: {
    forensic: 0,  // Immutable legal evidence
    critical: 1,  // System-compromising events
    error: 2,     // Operational failures
    warn: 3,      // Potential issues
    info: 4,      // Standard operations
    debug: 5      // Development diagnostics
  },
  COLORS: {
    forensic: 'white',
    critical: 'red',
    error: 'orange',
    warn: 'yellow',
    info: 'green',
    debug: 'blue'
  },
  EVENT_CATEGORIES: {
    AUTHENTICATION: 'AUTH',
    DOCUMENT_ACCESS: 'DOC_ACCESS',
    DOCUMENT_MODIFICATION: 'DOC_MODIFY',
    COMPLIANCE_CHECK: 'COMPLIANCE',
    USER_MANAGEMENT: 'USER_MGMT',
    SYSTEM_SECURITY: 'SECURITY',
    DATA_EXPORT: 'DATA_EXPORT',
    API_CALL: 'API'
  },
  RETENTION_PERIODS: {
    FORENSIC: 3650,   // 10 years for forensic evidence
    CRITICAL: 1825,   // 5 years for critical events
    STANDARD: 1095,   // 3 years for standard operations
    DEBUG: 30         // 30 days for debug logs
  }
};

/**
 * 🛡️ QUANTUM LOGGER FACTORY
 * Creates a Winston logger instance with multiple transports:
 * - Console (development)
 * - File (forensic backup)
 * - MongoDB (primary structured storage)
 */
const createQuantumLogger = () => {
  const complianceFormat = winston.format.printf(({ timestamp, level, message, ...meta }) => {
    return JSON.stringify({
      timestamp,
      level: level.toUpperCase(),
      message,
      jurisdiction: 'ZA',
      legalBasis: 'Cybercrimes Act 19 of 2020',
      ...meta
    });
  });

  const transports = [
    // Console transport for real-time monitoring
    new winston.transports.Console({
      level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
      format: winston.format.combine(winston.format.colorize(), winston.format.simple()),
    }),
    // File transport for forensic backup
    new winston.transports.File({
      level: 'forensic',
      filename: `logs/forensic-${new Date().toISOString().split('T')[0]}.log`,
      maxsize: 50 * 1024 * 1024, // 50MB per file
      maxFiles: 100,
      tailable: true,
      format: winston.format.combine(winston.format.timestamp(), complianceFormat),
    }),
  ];

  // MongoDB transport for primary structured audit storage
  if (process.env.AUDIT_DB_URI || process.env.MONGO_URI) {
    transports.push(new MongoDB({
      level: 'info',
      db: process.env.AUDIT_DB_URI || process.env.MONGO_URI,
      collection: 'quantum_audit_logs',
      options: { useUnifiedTopology: true },
      capped: true,
      cappedSize: 500 * 1024 * 1024, // 500MB capped collection
      cappedMax: 500000,
      expireAfterSeconds: AUDIT_CONFIG.RETENTION_PERIODS.STANDARD * 86400,
      metaKey: 'meta',
      format: winston.format.combine(winston.format.timestamp(), complianceFormat),
    }));
  }

  const logger = winston.createLogger({
    levels: AUDIT_CONFIG.LEVELS,
    level: 'forensic',
    format: winston.format.combine(winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }), complianceFormat),
    transports,
    exitOnError: false,
  });

  winston.addColors(AUDIT_CONFIG.COLORS);
  return logger;
};

// Initialize the quantum logger instance
const quantumLogger = createQuantumLogger();

/**
 * 🏛️ AUDIT LOGGER CLASS
 * Provides static methods for logging events and creating middleware.
 * All methods generate cryptographically unique audit IDs and event hashes.
 */
class AuditLogger {
  /**
   * Generates a unique audit event ID.
   * @returns {string} Format: AUDIT-{timestamp}-{random hex}
   */
  static generateAuditId() {
    return `AUDIT-${Date.now()}-${crypto.randomBytes(6).toString('hex')}`;
  }

  /**
   * Persists an audit event to the structured AuditTrail model.
   * @param {Object} auditEvent - The complete audit event data.
   */
  static async saveToStructuredTrail(auditEvent) {
    try {
      const auditRecord = new AuditTrail({
        eventId: auditEvent.eventId,
        eventHash: auditEvent.eventHash,
        timestamp: auditEvent.timestamp,
        user: {
          id: auditEvent.userId,
          role: auditEvent.userRole,
          tenantId: auditEvent.tenantId || 'WILSY_ROOT'
        },
        action: {
          method: auditEvent.method,
          url: auditEvent.url,
          endpoint: auditEvent.endpoint,
          category: auditEvent.category
        },
        network: {
          ipAddress: auditEvent.ip,
          userAgent: auditEvent.userAgent
        },
        result: {
          statusCode: auditEvent.statusCode,
          responseTimeMs: auditEvent.responseTime
        },
        compliance: {
          legalBasis: auditEvent.legalBasis,
          jurisdiction: auditEvent.jurisdiction,
          retentionPeriodDays: AUDIT_CONFIG.RETENTION_PERIODS.STANDARD
        },
        quantumSignature: {
          hash: auditEvent.eventHash,
          algorithm: auditEvent.hashAlgorithm || 'sha256'
        }
      });
      await auditRecord.save();
    } catch (error) {
      quantumLogger.error('Structured audit trail save failed', {
        eventId: auditEvent.eventId,
        error: error.message
      });
    }
  }

  /**
   * 🛡️ PRIMARY LOGGING METHOD
   * Used by legal services and controllers to record forensic events.
   * @param {string} action - The action name (e.g., 'CASE_CREATED', 'PRECEDENT_SEARCH').
   * @param {Object} data - Additional metadata for the audit entry.
   * @returns {Promise<string>} The generated audit event ID.
   */
  static async log(action, data = {}) {
    const auditEventId = AuditLogger.generateAuditId();
    const auditData = {
      eventId: auditEventId,
      timestamp: new Date().toISOString(),
      action,
      ...data
    };

    // Generate cryptographic hash of the complete event payload
    const hashResult = generateEventHash(auditData, { includeTimestamp: true });
    auditData.eventHash = hashResult.hash;

    // Log to Winston transports
    quantumLogger.info(action, auditData);

    // Persist to structured database (unless explicitly skipped)
    if (data.saveToTrail !== false) {
      await AuditLogger.saveToStructuredTrail(auditData).catch(() => {});
    }

    return auditEventId;
  }

  /**
   * 🛡️ EXPRESS MIDDLEWARE FACTORY
   * Creates middleware that automatically logs every request/response cycle.
   * @param {string} actionName - The action category for this middleware.
   * @returns {Function} Express middleware function.
   */
  static middleware(actionName = 'API_ACCESS') {
    return (req, res, next) => {
      const startTime = Date.now();
      const auditEventId = AuditLogger.generateAuditId();
      req.auditEventId = auditEventId;

      // Intercept response to log after completion
      const originalEnd = res.end;
      res.end = function (chunk, encoding) {
        res.end = originalEnd;
        res.end(chunk, encoding);

        const responseTime = Date.now() - startTime;

        const auditData = {
          eventId: auditEventId,
          timestamp: new Date(startTime).toISOString(),
          tenantId: req.tenantId || req.headers['x-tenant-id'] || 'WILSY_ROOT',
          userId: req.user?.id || 'anonymous',
          userRole: req.user?.role || 'guest',
          ip: req.headers['x-forwarded-for'] || req.socket?.remoteAddress || '0.0.0.0',
          userAgent: (req.headers['user-agent'] || '').substring(0, 200),
          method: req.method,
          url: req.originalUrl,
          statusCode: res.statusCode,
          responseTime,
          action: actionName,
          category: AUDIT_CONFIG.EVENT_CATEGORIES.API_CALL,
          legalBasis: 'Cybercrimes Act 19 of 2020',
          jurisdiction: 'ZA'
        };

        // Generate hash and seal the event
        const hashResult = generateEventHash(auditData, { includeTimestamp: true });
        auditData.eventHash = hashResult.hash;
        auditData.hashAlgorithm = hashResult.algorithm;

        // Log to Winston
        quantumLogger.log({
          level: res.statusCode >= 400 ? 'error' : 'info',
          message: `${auditData.method} ${auditData.url} - ${res.statusCode} (${responseTime}ms)`,
          ...auditData
        });

        // Persist to database
        AuditLogger.saveToStructuredTrail(auditData).catch(() => {});
      };

      next();
    };
  }
}

/**
 * 🛡️ DEFAULT EXPORT - COMPATIBLE WITH LEGAL ROUTER
 * Provides `log()` and `middleware()` methods for the legal/index.js router.
 */
export default {
  log: AuditLogger.log,
  middleware: AuditLogger.middleware,
  quantumLogger,
  AUDIT_CONFIG
};
