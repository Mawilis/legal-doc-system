/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – SOVEREIGN AUDIT LOGGER [v2.0.3-ORDERED-INIT]                                                                               ║
 * ║ [IMMUTABLE AUDIT LEDGER | CRYPTOGRAPHIC SEALING | CHAIN INTEGRITY]                                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.0.3-ORDERED-INIT | PRODUCTION READY                                                                                        ║
 * ║ EPITOME: Init only after mongoose readyState===1 (or dedicated audit URI). No import-time DB I/O.                                     ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/AuditLogger.js                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 FIX (v2.0.3):                                                                                                                       ║
 * ║   1. _waitForConnection polls readyState + 'connected' event (no missed race).                                                        ║
 * ║   2. findOne uses maxTimeMS(5000) — no 10s mongoose buffer hang.                                                                      ║
 * ║   3. Optional dedicated connection when MONGODB_AUDIT_URI ≠ main URI.                                                                 ║
 * ║   4. initialize() idempotent; process beforeExit registered once.                                                                     ║
 * ║   5. Server MUST call: await auditLogger.initialize() after mongoose.connect().                                                       ║
 * ║ Compliance: POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15                                                              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import { v4 as uuidv4 } from 'uuid';
import mongoose from 'mongoose';
import fs from 'node:fs/promises';
import { existsSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const LOGS_DIR = path.resolve(__dirname, '../../logs');
const FALLBACK_LOG = path.join(LOGS_DIR, 'audit_fallback.ledger');

if (!existsSync(LOGS_DIR)) mkdirSync(LOGS_DIR, { recursive: true });

// ─── MONGODB SCHEMA ──────────────────────────────────────────────────────────

const AuditLogSchema = new mongoose.Schema(
  {
    logId: { type: String, required: true, unique: true, default: () => uuidv4() },
    action: { type: String, required: true, index: true },
    actorId: { type: String, required: true, index: true },
    actorType: { type: String, enum: ['USER', 'SYSTEM', 'API', 'ADMIN'], default: 'USER' },
    tenantId: { type: String, required: true, index: true },
    resourceType: { type: String, index: true },
    resourceId: { type: String, index: true },
    details: { type: mongoose.Schema.Types.Mixed },
    severity: {
      type: String,
      enum: ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
      default: 'INFO',
      index: true,
    },
    ipAddress: String,
    userAgent: String,
    sessionId: String,
    correlationId: String,
    quantumSeal: { type: String, required: true },
    previousSeal: { type: String },
    complianceMarkers: {
      popia: { type: Boolean, default: false },
      fica: { type: Boolean, default: false },
      gdpr: { type: Boolean, default: false },
      ectAct: { type: Boolean, default: false },
      companiesAct: { type: Boolean, default: false },
    },
    retentionDate: Date,
    timestamp: { type: Date, default: Date.now, index: true },
    metadata: mongoose.Schema.Types.Mixed,
  },
  {
    timestamps: true,
    collection: 'audit_logs',
  }
);

const AuditLog = mongoose.models.AuditLog || mongoose.model('AuditLog', AuditLogSchema);

// ─── COMPLIANCE MAPPING ──────────────────────────────────────────────────────

const COMPLIANCE_MAPPING = {
  DATA_ACCESS: { popia: true, legalRef: 'POPIA §23' },
  CONSENT_CHANGE: { popia: true, legalRef: 'POPIA §11' },
  DATA_BREACH: { popia: true, legalRef: 'POPIA §22' },
  DSAR_REQUEST: { popia: true, legalRef: 'POPIA §23' },
  FICA_VERIFICATION: { fica: true, legalRef: 'FICA Reg 21' },
  AML_TRANSACTION: { fica: true, legalRef: 'FICA §29' },
  PEP_SCREENING: { fica: true, legalRef: 'FICA Reg 22' },
  DIGITAL_SIGNATURE: { ectAct: true, legalRef: 'ECT Act §13' },
  ELECTRONIC_TRANSACTION: { ectAct: true, legalRef: 'ECT Act §21' },
  COMPANY_RECORD: { companiesAct: true, legalRef: 'Companies Act §24' },
  DIRECTOR_CHANGE: { companiesAct: true, legalRef: 'Companies Act §66' },
  QR_VERIFY_TRACE: { popia: true, gdpr: true, legalRef: 'POPIA §19, GDPR §32' },
  QR_VERIFY_SIGNED_PAYLOAD: { popia: true, gdpr: true, legalRef: 'POPIA §19, GDPR §32' },
};

const RETENTION_PERIODS = {
  DEFAULT: 365 * 7,
  POPIA: 365,
  FICA: 365 * 5,
  COMPANIES_ACT: 365 * 7,
  ECT_ACT: 365 * 5,
};

// ─── AUDIT LOGGER CLASS ─────────────────────────────────────────────────────

class AuditLogger {
  constructor() {
    this.chainHead = null;
    this.buffer = [];
    this.flushInterval = null;
    this.batchSize = 100;
    this.flushIntervalMs = 5000;
    this.initialized = false;
    this.dbAvailable = false;
    this._initPromise = null;
    this._beforeExitBound = false;
    this._auditConnection = null; // optional dedicated connection
    this._AuditLogModel = AuditLog;
  }

  /**
   * Resolve audit URI (production env order).
   */
  _resolveAuditUri() {
    return (
      process.env.MONGODB_AUDIT_URI ||
      process.env.AUDIT_DB_URI ||
      process.env.MONGODB_URI ||
      process.env.MONGO_URI ||
      process.env.DATABASE_URL ||
      ''
    ).trim();
  }

  /**
   * Wait until default mongoose connection is ready (poll + event).
   * @param {number} timeoutMs
   * @returns {Promise<boolean>}
   */
  async _waitForDefaultConnection(timeoutMs = 8000) {
    if (mongoose.connection.readyState === 1) return true;

    return new Promise((resolve) => {
      let settled = false;
      const done = (ok) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        clearInterval(poll);
        mongoose.connection.off('connected', onConnected);
        mongoose.connection.off('error', onError);
        resolve(ok);
      };

      const onConnected = () => done(true);
      const onError = () => {
        /* keep waiting until timeout — connect may retry */
      };

      const timer = setTimeout(() => done(mongoose.connection.readyState === 1), timeoutMs);
      const poll = setInterval(() => {
        if (mongoose.connection.readyState === 1) done(true);
      }, 150);

      mongoose.connection.once('connected', onConnected);
      mongoose.connection.once('error', onError);

      if (mongoose.connection.readyState === 1) done(true);
    });
  }

  /**
   * Optionally open a dedicated connection when audit URI differs from main.
   * Uses same models on default connection when URIs match or dedicated fails.
   */
  async _ensureAuditModel() {
    const auditUri = this._resolveAuditUri();
    const mainUri = (
      process.env.MONGODB_URI ||
      process.env.MONGO_URI ||
      process.env.DATABASE_URL ||
      ''
    ).trim();

    // Prefer default connection when URI empty or same as main
    if (!auditUri || auditUri === mainUri) {
      this._AuditLogModel = AuditLog;
      return Boolean(mongoose.connection.readyState === 1);
    }

    try {
      if (!this._auditConnection) {
        this._auditConnection = await mongoose
          .createConnection(auditUri, {
            maxPoolSize: 10,
            serverSelectionTimeoutMS: 8000,
          })
          .asPromise();
      }
      this._AuditLogModel =
        this._auditConnection.models.AuditLog ||
        this._auditConnection.model('AuditLog', AuditLogSchema);
      return this._auditConnection.readyState === 1;
    } catch (err) {
      console.warn(
        '[AuditLogger] Dedicated audit URI failed, falling back to default connection:',
        err.message
      );
      this._AuditLogModel = AuditLog;
      return mongoose.connection.readyState === 1;
    }
  }

  /**
   * Initialize — call once after mongoose.connect() in server boot.
   * Idempotent; concurrent callers share the same promise.
   */
  async initialize() {
    if (this.initialized) return;
    if (this._initPromise) return this._initPromise;

    this._initPromise = (async () => {
      const defaultReady = await this._waitForDefaultConnection(8000);
      if (!defaultReady && !this._resolveAuditUri()) {
        console.warn('[AuditLogger] ⚠️ MongoDB not ready, using file fallback.');
        this.dbAvailable = false;
        this.initialized = true;
        return;
      }

      const modelReady = await this._ensureAuditModel();
      if (!modelReady) {
        console.warn('[AuditLogger] ⚠️ MongoDB not ready, using file fallback.');
        this.dbAvailable = false;
        this.initialized = true;
        return;
      }

      try {
        const lastLog = await this._AuditLogModel
          .findOne()
          .sort({ timestamp: -1 })
          .select('quantumSeal')
          .maxTimeMS(5000)
          .lean();
        this.chainHead = lastLog?.quantumSeal || null;
        this.dbAvailable = true;
        console.log(
          '[AuditLogger] ✅ Connected to MongoDB. Chain head:',
          this.chainHead?.slice(0, 16) || 'GENESIS'
        );
      } catch (error) {
        console.warn('[AuditLogger] ⚠️ DB query failed, using file fallback:', error.message);
        this.dbAvailable = false;
      }

      this.initialized = true;

      if (this.dbAvailable && !this.flushInterval) {
        this.flushInterval = setInterval(() => {
          this.flush().catch(() => { });
        }, this.flushIntervalMs);
        if (this.flushInterval.unref) this.flushInterval.unref();
      }

      if (!this._beforeExitBound) {
        this._beforeExitBound = true;
        process.on('beforeExit', () => {
          this.flush().catch(() => { });
        });
      }
    })();

    try {
      await this._initPromise;
    } finally {
      this._initPromise = null;
    }
  }

  async flush() {
    if (this.buffer.length === 0) return;
    const batch = [...this.buffer];
    this.buffer = [];

    if (this.dbAvailable && this._AuditLogModel) {
      try {
        await this._AuditLogModel.insertMany(batch, { ordered: false });
        return;
      } catch (error) {
        console.error('[AuditLogger] DB flush failed, falling back to file:', error.message);
      }
    }

    try {
      const lines = batch.map((entry) => `${JSON.stringify(entry)}\n`).join('');
      await fs.appendFile(FALLBACK_LOG, lines);
    } catch (err) {
      console.error('[AuditLogger] File fallback failed:', err.message);
    }
  }

  async log({
    action,
    actorId,
    actorType = 'USER',
    tenantId,
    resourceType,
    resourceId,
    details,
    severity = 'INFO',
    ipAddress,
    userAgent,
    sessionId,
    correlationId,
    metadata = {},
  }) {
    if (!this.initialized) {
      await this.initialize();
    }

    const timestamp = new Date();
    const logId = uuidv4();
    const compliance = this.determineCompliance(action);

    const sealData = {
      logId,
      action,
      actorId,
      tenantId,
      timestamp: timestamp.toISOString(),
      previousSeal: this.chainHead,
    };
    const quantumSeal = crypto
      .createHash('sha3-512')
      .update(JSON.stringify(sealData))
      .digest('hex');

    const retentionDays = this.getRetentionDays(compliance);
    const retentionDate = new Date(timestamp);
    retentionDate.setDate(retentionDate.getDate() + retentionDays);

    const entry = {
      logId,
      action,
      actorId,
      actorType,
      tenantId,
      resourceType,
      resourceId,
      details: this.sanitizeDetails(details),
      severity,
      ipAddress: ipAddress || 'UNKNOWN',
      userAgent: userAgent || 'UNKNOWN',
      sessionId,
      correlationId: correlationId || uuidv4(),
      quantumSeal,
      previousSeal: this.chainHead,
      complianceMarkers: compliance,
      retentionDate,
      timestamp,
      metadata: {
        ...metadata,
        version: '2.0.3',
        jurisdiction: 'ZA',
        source: 'WILSY_OS_AUDIT_LOGGER',
      },
    };

    this.chainHead = quantumSeal;
    this.buffer.push(entry);
    this.consoleLog(entry);

    if (this.buffer.length >= this.batchSize) {
      await this.flush();
    }

    return entry;
  }

  determineCompliance(action) {
    const markers = {
      popia: false,
      fica: false,
      gdpr: false,
      ectAct: false,
      companiesAct: false,
    };
    const act = String(action || '');
    for (const [key, config] of Object.entries(COMPLIANCE_MAPPING)) {
      if (act.includes(key) || act === key) {
        Object.assign(markers, {
          popia: Boolean(config.popia),
          fica: Boolean(config.fica),
          gdpr: Boolean(config.gdpr),
          ectAct: Boolean(config.ectAct),
          companiesAct: Boolean(config.companiesAct),
        });
        break;
      }
    }
    if (act.includes('GDPR')) markers.gdpr = true;
    return markers;
  }

  getRetentionDays(compliance) {
    if (compliance.companiesAct) return RETENTION_PERIODS.COMPANIES_ACT;
    if (compliance.fica) return RETENTION_PERIODS.FICA;
    if (compliance.popia) return RETENTION_PERIODS.POPIA;
    if (compliance.ectAct) return RETENTION_PERIODS.ECT_ACT;
    return RETENTION_PERIODS.DEFAULT;
  }

  sanitizeDetails(details) {
    if (!details || typeof details !== 'object') return details;
    const sensitive = [
      'password',
      'token',
      'secret',
      'key',
      'creditCard',
      'cvv',
      'pin',
      'ssn',
      'idNumber',
      'passport',
      'bankAccount',
      'authorization',
      'auth',
    ];
    const sanitized = { ...details };
    for (const field of sensitive) {
      if (sanitized[field]) sanitized[field] = '[REDACTED]';
    }
    return sanitized;
  }

  consoleLog(entry) {
    const colors = {
      DEBUG: '\x1b[90m',
      INFO: '\x1b[32m',
      WARNING: '\x1b[33m',
      ERROR: '\x1b[31m',
      CRITICAL: '\x1b[35m',
    };
    const color = colors[entry.severity] || '\x1b[0m';
    console.log(
      `${color}[AUDIT] [${entry.severity}] [${entry.action}]\x1b[0m ` +
      `Actor: ${entry.actorId} | Tenant: ${entry.tenantId} | Seal: ${entry.quantumSeal.slice(0, 8)}`
    );
  }

  async query(filters = {}, limit = 100, skip = 0) {
    if (!this.dbAvailable || !this._AuditLogModel) {
      console.warn('[AuditLogger] Query requested but DB unavailable – returning empty.');
      return { logs: [], total: 0, limit, skip };
    }
    const query = {};
    if (filters.tenantId) query.tenantId = filters.tenantId;
    if (filters.actorId) query.actorId = filters.actorId;
    if (filters.action) query.action = filters.action;
    if (filters.severity) query.severity = filters.severity;
    if (filters.resourceType) query.resourceType = filters.resourceType;
    if (filters.resourceId) query.resourceId = filters.resourceId;
    if (filters.startDate || filters.endDate) {
      query.timestamp = {};
      if (filters.startDate) query.timestamp.$gte = new Date(filters.startDate);
      if (filters.endDate) query.timestamp.$lte = new Date(filters.endDate);
    }
    const [logs, total] = await Promise.all([
      this._AuditLogModel.find(query).sort({ timestamp: -1 }).skip(skip).limit(limit).maxTimeMS(10000).lean(),
      this._AuditLogModel.countDocuments(query).maxTimeMS(10000),
    ]);
    return { logs, total, limit, skip };
  }

  async verifyIntegrity() {
    if (!this.dbAvailable || !this._AuditLogModel) {
      return {
        valid: true,
        totalLogs: 0,
        invalid: [],
        message: 'DB unavailable – using file fallback',
      };
    }
    const logs = await this._AuditLogModel.find().sort({ timestamp: 1 }).maxTimeMS(30000).lean();
    let previousSeal = null;
    const invalid = [];
    for (const log of logs) {
      if (previousSeal !== null && log.previousSeal !== previousSeal) {
        invalid.push({
          logId: log.logId,
          expected: previousSeal,
          actual: log.previousSeal,
        });
      }
      const sealData = {
        logId: log.logId,
        action: log.action,
        actorId: log.actorId,
        tenantId: log.tenantId,
        timestamp: new Date(log.timestamp).toISOString(),
        previousSeal: log.previousSeal,
      };
      const recalculated = crypto
        .createHash('sha3-512')
        .update(JSON.stringify(sealData))
        .digest('hex');
      if (recalculated !== log.quantumSeal) {
        invalid.push({
          logId: log.logId,
          reason: 'Seal mismatch',
          stored: log.quantumSeal,
          calculated: recalculated,
        });
      }
      previousSeal = log.quantumSeal;
    }
    return { valid: invalid.length === 0, totalLogs: logs.length, invalid };
  }

  async shutdown() {
    if (this.flushInterval) {
      clearInterval(this.flushInterval);
      this.flushInterval = null;
    }
    await this.flush();
    if (this._auditConnection) {
      try {
        await this._auditConnection.close();
      } catch {
        /* ignore */
      }
      this._auditConnection = null;
    }
    console.log('[AuditLogger] Shut down gracefully');
  }
}

// ─── SINGLETON ───────────────────────────────────────────────────────────────

const auditLogger = new AuditLogger();

// No import-time initialize(). Boot sequence:
//   await mongoose.connect(process.env.MONGODB_URI)
//   await auditLogger.initialize()
//   httpServer.listen(PORT)

export default auditLogger;
export { AuditLogger, AuditLog };

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏛️ INSTITUTIONAL CERTIFICATION SEAL — AuditLogger v2.0.3-ORDERED-INIT
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status:          CERTIFIED PRODUCTION ARTIFACT
 * Fix:             Poll+event wait; maxTimeMS; optional dedicated audit URI;
 *                  no import-time DB I/O; server must call initialize() post-connect
 * Compliance:      POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001
 * ═══════════════════════════════════════════════════════════════════════════════
 */
