/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ QUANTUM AUDIT LOGGER: THE IMMUTABLE FORENSIC LEDGER OF LEGAL TRUTH [V16.1.0-ATLAS-URI]                                               ║
 * ║ [CYBERCRIMES ACT 19 OF 2020 | POPIA | ECT ACT | PAIA | ES MODULE ALIGNED]                                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 16.1.0-ATLAS-URI | PRODUCTION READY                                                                                          ║
 * ║ EPITOME: Resolves Mongo URI from MONGODB_AUDIT_URI → AUDIT_DB_URI → MONGODB_URI → MONGO_URI.                                          ║
 * ║           Winston-MongoDB transport is optional and non-fatal; HTTP listen is never blocked.                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/auditLogger.js                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 FIX (v16.1.0):                                                                                                                      ║
 * ║   1. Prefer MONGODB_AUDIT_URI / MONGODB_URI (server/.env production keys).                                                             ║
 * ║   2. Drop deprecated useUnifiedTopology (Mongo driver 4+).                                                                            ║
 * ║   3. Guard Mongo transport construction — log warning, continue with console+file.                                                    ║
 * ║   4. Preserve API: quantumLogger, AuditLogger class, middleware(), default export.                                                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import dotenv from 'dotenv';
import crypto from 'crypto';
import winston from 'winston';
import { MongoDB } from 'winston-mongodb';
import fs from 'fs';
import path from 'path';
import AuditTrail from '../models/AuditTrail.js';
import { generateEventHash } from '../utils/eventHashGenerator.js';

dotenv.config();

const backupDir = path.resolve(process.cwd(), 'logs');
if (!fs.existsSync(backupDir)) fs.mkdirSync(backupDir, { recursive: true });

/**
 * Resolve audit Mongo URI in production order.
 * Does not invent credentials — uses only env already present on the host.
 */
function resolveAuditDbUri() {
  return (
    process.env.MONGODB_AUDIT_URI ||
    process.env.AUDIT_DB_URI ||
    process.env.MONGODB_URI ||
    process.env.MONGO_URI ||
    process.env.DATABASE_URL ||
    ''
  ).trim();
}

const AUDIT_CONFIG = {
  LEVELS: {
    forensic: 0,
    critical: 1,
    error: 2,
    warn: 3,
    info: 4,
    debug: 5,
  },
  COLORS: {
    forensic: 'white',
    critical: 'red',
    error: 'orange',
    warn: 'yellow',
    info: 'green',
    debug: 'blue',
  },
  EVENT_CATEGORIES: {
    AUTHENTICATION: 'AUTH',
    DOCUMENT_ACCESS: 'DOC_ACCESS',
    DOCUMENT_MODIFICATION: 'DOC_MODIFY',
    COMPLIANCE_CHECK: 'COMPLIANCE',
    USER_MANAGEMENT: 'USER_MGMT',
    SYSTEM_SECURITY: 'SECURITY',
    DATA_EXPORT: 'DATA_EXPORT',
    API_CALL: 'API',
  },
  RETENTION_PERIODS: {
    FORENSIC: 3650,
    CRITICAL: 1825,
    STANDARD: 1095,
    DEBUG: 30,
  },
};

/**
 * Creates Winston logger with console + file always; Mongo when URI is valid.
 * Mongo transport failures must not prevent process listen.
 */
const createQuantumLogger = () => {
  const complianceFormat = winston.format.printf(({ timestamp, level, message, ...meta }) => {
    return JSON.stringify({
      timestamp,
      level: level.toUpperCase(),
      message,
      jurisdiction: 'ZA',
      legalBasis: 'Cybercrimes Act 19 of 2020',
      ...meta,
    });
  });

  const transports = [
    new winston.transports.Console({
      level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
      format: winston.format.combine(winston.format.colorize(), winston.format.simple()),
    }),
    new winston.transports.File({
      level: 'forensic',
      filename: `logs/forensic-${new Date().toISOString().split('T')[0]}.log`,
      maxsize: 50 * 1024 * 1024,
      maxFiles: 100,
      tailable: true,
      format: winston.format.combine(winston.format.timestamp(), complianceFormat),
    }),
  ];

  const auditDbUri = resolveAuditDbUri();
  if (auditDbUri) {
    try {
      transports.push(
        new MongoDB({
          level: 'info',
          db: auditDbUri,
          collection: 'quantum_audit_logs',
          // driver 4+: no useUnifiedTopology
          capped: true,
          cappedSize: 500 * 1024 * 1024,
          cappedMax: 500000,
          expireAfterSeconds: AUDIT_CONFIG.RETENTION_PERIODS.STANDARD * 86400,
          metaKey: 'meta',
          format: winston.format.combine(winston.format.timestamp(), complianceFormat),
        })
      );
    } catch (err) {
      // eslint-disable-next-line no-console
      console.warn(
        `[AuditLogger] Winston-MongoDB transport not attached: ${err?.message || err}. Console+file remain active.`
      );
    }
  } else {
    // eslint-disable-next-line no-console
    console.warn(
      '[AuditLogger] No MONGODB_AUDIT_URI / MONGODB_URI / MONGO_URI — Mongo audit transport skipped.'
    );
  }

  const logger = winston.createLogger({
    levels: AUDIT_CONFIG.LEVELS,
    level: 'forensic',
    format: winston.format.combine(
      winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
      complianceFormat
    ),
    transports,
    exitOnError: false,
  });

  winston.addColors(AUDIT_CONFIG.COLORS);
  return logger;
};

const quantumLogger = createQuantumLogger();

class AuditLogger {
  static generateAuditId() {
    return `AUDIT-${Date.now()}-${crypto.randomBytes(6).toString('hex')}`;
  }

  static async saveToStructuredTrail(auditEvent) {
    try {
      const auditRecord = new AuditTrail({
        eventId: auditEvent.eventId,
        eventHash: auditEvent.eventHash,
        timestamp: auditEvent.timestamp,
        user: {
          id: auditEvent.userId,
          role: auditEvent.userRole,
          tenantId: auditEvent.tenantId || 'WILSY_ROOT',
        },
        action: {
          method: auditEvent.method,
          url: auditEvent.url,
          endpoint: auditEvent.endpoint,
          category: auditEvent.category,
        },
        network: {
          ipAddress: auditEvent.ip,
          userAgent: auditEvent.userAgent,
        },
        metadata: auditEvent.metadata || {},
        severity: auditEvent.severity || 'info',
      });
      await auditRecord.save();
      return auditRecord;
    } catch (err) {
      quantumLogger.error('Failed to persist structured AuditTrail', {
        error: err?.message,
        eventId: auditEvent?.eventId,
      });
      return null;
    }
  }

  static async log(event = {}) {
    const eventId = event.eventId || AuditLogger.generateAuditId();
    const timestamp = event.timestamp || new Date().toISOString();
    const payload = {
      eventId,
      timestamp,
      message: event.message || event.action || 'AUDIT_EVENT',
      level: event.level || 'info',
      userId: event.userId || 'SYSTEM',
      userRole: event.userRole || 'SYSTEM',
      tenantId: event.tenantId || 'GLOBAL_ROOT',
      method: event.method,
      url: event.url,
      endpoint: event.endpoint,
      category: event.category || AUDIT_CONFIG.EVENT_CATEGORIES.API_CALL,
      ip: event.ip,
      userAgent: event.userAgent,
      metadata: event.metadata || {},
      severity: event.severity || 'info',
    };

    try {
      payload.eventHash = generateEventHash
        ? generateEventHash(payload)
        : crypto.createHash('sha256').update(JSON.stringify(payload)).digest('hex');
    } catch {
      payload.eventHash = crypto.createHash('sha256').update(String(eventId)).digest('hex');
    }

    const level = String(payload.level).toLowerCase();
    if (typeof quantumLogger[level] === 'function') {
      quantumLogger[level](payload.message, payload);
    } else {
      quantumLogger.info(payload.message, payload);
    }

    // Non-blocking structured trail
    setImmediate(() => {
      AuditLogger.saveToStructuredTrail(payload).catch(() => { });
    });

    return payload;
  }

  /**
   * Express middleware — records request/response audit envelope.
   */
  static middleware() {
    return (req, res, next) => {
      const start = Date.now();
      const eventId = AuditLogger.generateAuditId();
      res.on('finish', () => {
        AuditLogger.log({
          eventId,
          message: `${req.method} ${req.originalUrl || req.url}`,
          level: res.statusCode >= 500 ? 'error' : res.statusCode >= 400 ? 'warn' : 'info',
          userId: req.user?.id || req.user?._id || 'ANONYMOUS',
          userRole: req.user?.role || 'ANONYMOUS',
          tenantId:
            req.headers['x-tenant-id'] ||
            req.tenantId ||
            req.user?.tenantId ||
            'GLOBAL_ROOT',
          method: req.method,
          url: req.originalUrl || req.url,
          endpoint: req.route?.path || req.path,
          category: AUDIT_CONFIG.EVENT_CATEGORIES.API_CALL,
          ip: req.ip || req.headers['x-forwarded-for'],
          userAgent: req.headers['user-agent'],
          metadata: {
            statusCode: res.statusCode,
            durationMs: Date.now() - start,
          },
        }).catch(() => { });
      });
      next();
    };
  }
}

export { quantumLogger, AuditLogger, AUDIT_CONFIG, createQuantumLogger, resolveAuditDbUri };
export default AuditLogger;

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — middleware/auditLogger.js V16.1.0-ATLAS-URI
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status:     PRODUCTION
 * Fix:        URI resolution order; no useUnifiedTopology; Mongo transport non-fatal
 * Compliance: POPIA §19 · GDPR §32 · Cybercrimes Act 19 of 2020
 * ═══════════════════════════════════════════════════════════════════════════════
 */
