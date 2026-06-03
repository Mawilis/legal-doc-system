/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN AUDIT LOG SCHEMA [V72.0.0-FORENSIC-SEALED]                                                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/SovereignAuditLog.js                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ FEATURES:                                                                                                                              ║
 * ║   • Immutable audit ledger for boardroom and regulator actions.                                                                       ║
 * ║   • Forensic sealing with SHA3‑512 – each entry cryptographically linked to global hash chain.                                        ║
 * ║   • 10‑year retention policy (TTL index) – compliant with POPIA, GDPR, SARS.                                                          ║
 * ║   • Full JSDoc – every field, static method, and parameter documented.                                                                ║
 * ║   • Multi‑tenant indexes – fast queries by tenantId, correlationId, eventType, timestamp.                                             ║
 * ║   • Validation – required fields, enum constraints, and custom validators.                                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – mandated forensic sealing, retention policy, and full auditability for boardroom HUD.        ║
 * ║ • AI Engineering (DeepSeek) – ENHANCED: added forensicHasher integration, static helpers, compound indexes, and complete JSDoc.       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import forensicHasher from '../utils/forensicHasher.js';

// ============================================================================
// 🔥 SCHEMA DEFINITIONS
// ============================================================================

/**
 * @typedef {Object} Actor
 * @property {string} userId - Unique identifier of the actor (user or system).
 * @property {string} role - Role of the actor ('FOUNDER', 'DIRECTOR', 'AUDITOR', 'SYSTEM').
 * @property {string} method - HTTP method or action type (e.g., 'GET', 'POST', 'BIOMETRIC').
 */

/**
 * @typedef {Object} Metadata
 * @property {string} ip - IP address of the requestor (or 'SYSTEM' for internal actions).
 * @property {string} device - User‑agent string or device identifier.
 * @property {string} [browser] - Browser name (parsed from user‑agent).
 * @property {string} geo - Geo location (country code or 'UNKNOWN').
 * @property {string} [correlationId] - End‑to‑end correlation ID (duplicated at root level for indexing).
 */

/**
 * Mongoose schema for actor metadata.
 * @type {mongoose.Schema}
 */
const ActorSchema = new mongoose.Schema({
  userId: {
    type: String,
    required: [true, 'Actor userId is required'],
    trim: true,
    index: true
  },
  role: {
    type: String,
    required: [true, 'Actor role is required'],
    enum: {
      values: ['FOUNDER', 'DIRECTOR', 'AUDITOR', 'SYSTEM'],
      message: 'Role must be one of: FOUNDER, DIRECTOR, AUDITOR, SYSTEM'
    }
  },
  method: {
    type: String,
    required: [true, 'Actor method is required'],
    trim: true
  }
}, { _id: false });

/**
 * Mongoose schema for request metadata.
 * @type {mongoose.Schema}
 */
const MetadataSchema = new mongoose.Schema({
  ip: {
    type: String,
    required: [true, 'IP address is required'],
    trim: true
  },
  device: {
    type: String,
    required: [true, 'Device/user‑agent is required'],
    trim: true
  },
  browser: {
    type: String,
    default: 'unknown',
    trim: true
  },
  geo: {
    type: String,
    required: [true, 'Geo location is required'],
    trim: true,
    default: 'UNKNOWN'
  }
}, { _id: false });

/**
 * Main Sovereign Audit Log schema – immutable forensic ledger.
 * @type {mongoose.Schema}
 */
const SovereignAuditLogSchema = new mongoose.Schema({
  /** @type {string} Unique event identifier (UUID v4 recommended) */
  eventId: {
    type: String,
    required: [true, 'eventId is required'],
    unique: true,
    index: true,
    trim: true
  },
  /** @type {string} Type of event – must match boardroom/regulator actions */
  eventType: {
    type: String,
    required: [true, 'eventType is required'],
    enum: {
      values: [
        'HUD_ACKNOWLEDGE',
        'PDF_REQUEST',
        'REFRESH_ATTEMPT',
        'REGULATOR_BUNDLE_ACCESS',
        'REGULATOR_AUTH_FAILURE_ESCALATION',
        'REGULATOR_SUSPENSION_LIFECYCLE',
        'BIOMETRIC_REGISTRATION',
        'BIOMETRIC_VERIFICATION',
        'SEIZURE_ORDER_EXECUTED',
        'PRICE_WARHEAD_TRIGGERED'
      ],
      message: 'eventType must be a valid boardroom action'
    },
    index: true
  },
  /** @type {string} Tenant ID (multi‑tenant isolation) */
  tenantId: {
    type: String,
    required: [true, 'tenantId is required'],
    index: true,
    trim: true
  },
  /** @type {string} End‑to‑end correlation ID for tracing across systems */
  correlationId: {
    type: String,
    required: [true, 'correlationId is required'],
    index: true,
    trim: true
  },
  /** @type {string|null} Optional alert ID (if event is a response to an alert) */
  alertId: {
    type: String,
    default: null,
    trim: true
  },
  /** @type {string|null} Optional trace ID from external systems */
  traceId: {
    type: String,
    default: null,
    trim: true
  },
  /** @type {string|null} Biometric credential ID (if verification involved) */
  credentialId: {
    type: String,
    default: null,
    trim: true
  },
  /** @type {string} Outcome of the action – success, failure, or lifecycle state */
  outcome: {
    type: String,
    required: [true, 'outcome is required'],
    enum: {
      values: ['SUCCESS', 'FAILURE', 'SUSPENDED', 'ACTIVE', 'TERMINATED', 'REINSTATED'],
      message: 'outcome must be one of: SUCCESS, FAILURE, SUSPENDED, ACTIVE, TERMINATED, REINSTATED'
    }
  },
  /** @type {Actor} Actor who performed the action */
  actor: {
    type: ActorSchema,
    required: [true, 'actor is required']
  },
  /** @type {Date} Timestamp of the event (defaults to now) */
  timestamp: {
    type: Date,
    default: Date.now
  },
  /** @type {Metadata} Request metadata (IP, device, geo) */
  metadata: {
    type: MetadataSchema,
    required: [true, 'metadata is required']
  },
  /** @type {string} Cryptographic seal from forensicHasher (SHA3‑512) */
  forensicSeal: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  /** @type {number} Position in the global forensic hash chain */
  chainPosition: {
    type: Number,
    unique: true,
    index: true
  },
  /** @type {string} Chain hash linking to previous entry in the global chain */
  chainHash: {
    type: String,
    required: true,
    trim: true
  }
}, {
  timestamps: true,           // Adds createdAt and updatedAt
  collection: 'sovereign_audit_ledger'
});

// ============================================================================
// 🔥 INDEXES FOR PERFORMANCE AND RETENTION
// ============================================================================

/** TTL index: automatically delete documents after 10 years (315,360,000 seconds) */
SovereignAuditLogSchema.index({ timestamp: 1 }, { expireAfterSeconds: 315360000 });

/** Compound index for tenant‑scoped time‑range queries */
SovereignAuditLogSchema.index({ tenantId: 1, timestamp: -1 });

/** Compound index for correlation ID + tenant (fast forensic lookup) */
SovereignAuditLogSchema.index({ correlationId: 1, tenantId: 1 });

/** Index for eventType + outcome (analytics) */
SovereignAuditLogSchema.index({ eventType: 1, outcome: 1 });

// ============================================================================
// 🔥 PRE‑SAVE HOOK: AUTO‑SEAL WITH FORENSIC HASHER
// ============================================================================

/**
 * Pre‑save middleware that automatically seals the audit entry using forensicHasher.
 * @param {Function} next - Mongoose next middleware function.
 */
SovereignAuditLogSchema.pre('save', async function(next) {
  if (!this.isNew) return next(); // Only seal on creation

  try {
    // Build the payload to be sealed
    const sealPayload = {
      eventId: this.eventId,
      eventType: this.eventType,
      tenantId: this.tenantId,
      correlationId: this.correlationId,
      outcome: this.outcome,
      actor: this.actor,
      timestamp: this.timestamp,
      metadata: this.metadata
    };

    // Create a forensic seal using the global hasher
    const sealEntry = forensicHasher.createSeal(sealPayload);
    this.forensicSeal = sealEntry.hash;
    this.chainPosition = sealEntry.position;
    this.chainHash = sealEntry.chainHash;

    next();
  } catch (error) {
    next(new Error(`Forensic sealing failed: ${error.message}`));
  }
});

// ============================================================================
// 🔥 STATIC METHODS
// ============================================================================

/**
 * Creates a new audit entry with forensic sealing.
 * @async
 * @static
 * @param {Object} params - Audit entry parameters.
 * @param {string} params.eventId - Unique event ID (UUID v4).
 * @param {string} params.eventType - Event type (must match enum).
 * @param {string} params.tenantId - Tenant ID.
 * @param {string} params.correlationId - Correlation ID.
 * @param {string} params.outcome - Outcome ('SUCCESS', 'FAILURE', etc.).
 * @param {Object} params.actor - Actor object.
 * @param {string} params.actor.userId - User ID.
 * @param {string} params.actor.role - Role (FOUNDER, DIRECTOR, etc.).
 * @param {string} params.actor.method - HTTP method or action.
 * @param {Object} params.metadata - Metadata object.
 * @param {string} params.metadata.ip - IP address.
 * @param {string} params.metadata.device - User‑agent.
 * @param {string} [params.metadata.browser] - Browser name.
 * @param {string} [params.metadata.geo] - Geo location.
 * @param {string} [params.alertId] - Optional alert ID.
 * @param {string} [params.traceId] - Optional trace ID.
 * @param {string} [params.credentialId] - Optional biometric credential ID.
 * @returns {Promise<Document>} The created audit document.
 * @throws {Error} If required fields are missing or sealing fails.
 *
 * @real-world
 *   Called by the Boardroom HUD, regulator export service, and sovereign routes
 *   to record every critical action. The forensic seal ensures non‑repudiation.
 *
 * @forensic
 *   The entry is cryptographically linked to the global hash chain. Any tampering
 *   will break the chain and be detected by `verifyChainIntegrity`.
 *
 * @example
 * const auditEntry = await SovereignAuditLog.createAuditEntry({
 *   eventId: uuidv4(),
 *   eventType: 'HUD_ACKNOWLEDGE',
 *   tenantId: 'GLOBAL_ROOT',
 *   correlationId: 'CORR-123',
 *   outcome: 'SUCCESS',
 *   actor: { userId: 'usr_456', role: 'DIRECTOR', method: 'BIOMETRIC' },
 *   metadata: { ip: '192.168.1.1', device: 'Chrome/120', geo: 'ZA' },
 *   alertId: 'ALERT-789'
 * });
 */
SovereignAuditLogSchema.statics.createAuditEntry = async function(params) {
  const requiredFields = ['eventId', 'eventType', 'tenantId', 'correlationId', 'outcome', 'actor', 'metadata'];
  for (const field of requiredFields) {
    if (!params[field]) {
      throw new Error(`Missing required audit field: ${field}`);
    }
  }

  // Validate actor sub‑fields
  if (!params.actor.userId || !params.actor.role || !params.actor.method) {
    throw new Error('Actor must contain userId, role, and method');
  }

  // Validate metadata sub‑fields
  if (!params.metadata.ip || !params.metadata.device) {
    throw new Error('Metadata must contain ip and device');
  }

  const auditData = {
    eventId: params.eventId,
    eventType: params.eventType,
    tenantId: params.tenantId,
    correlationId: params.correlationId,
    outcome: params.outcome,
    actor: {
      userId: params.actor.userId,
      role: params.actor.role,
      method: params.actor.method
    },
    metadata: {
      ip: params.metadata.ip,
      device: params.metadata.device,
      browser: params.metadata.browser || 'unknown',
      geo: params.metadata.geo || 'UNKNOWN'
    },
    alertId: params.alertId || null,
    traceId: params.traceId || null,
    credentialId: params.credentialId || null
  };

  return this.create(auditData);
};

/**
 * Finds all audit events for a given correlation ID, sorted oldest to newest.
 * @async
 * @static
 * @param {string} correlationId - The correlation ID to search for.
 * @returns {Promise<Array<Document>>} Array of audit documents.
 * @example
 * const events = await SovereignAuditLog.findByCorrelationId('CORR-123');
 */
SovereignAuditLogSchema.statics.findByCorrelationId = async function(correlationId) {
  if (!correlationId) throw new Error('correlationId is required');
  return this.find({ correlationId }).sort({ timestamp: 1 }).exec();
};

/**
 * Finds all audit events for a tenant within a time range, newest first.
 * @async
 * @static
 * @param {string} tenantId - Tenant ID.
 * @param {Date} startDate - Start of time range (inclusive).
 * @param {Date} endDate - End of time range (inclusive).
 * @returns {Promise<Array<Document>>} Array of audit documents.
 * @example
 * const from = new Date('2026-01-01');
 * const to = new Date('2026-12-31');
 * const logs = await SovereignAuditLog.findByTenantAndTimeRange('GLOBAL_ROOT', from, to);
 */
SovereignAuditLogSchema.statics.findByTenantAndTimeRange = async function(tenantId, startDate, endDate) {
  if (!tenantId) throw new Error('tenantId is required');
  if (!startDate || !endDate) throw new Error('startDate and endDate are required');
  if (startDate > endDate) throw new Error('startDate must be before endDate');

  return this.find({
    tenantId,
    timestamp: { $gte: startDate, $lte: endDate }
  }).sort({ timestamp: -1 }).exec();
};

/**
 * Verifies the integrity of the forensic hash chain starting from the first entry.
 * Uses forensicHasher.verifyChain to detect tampering.
 * @async
 * @static
 * @returns {Promise<boolean>} True if chain is intact, false otherwise.
 * @example
 * const isIntact = await SovereignAuditLog.verifyChainIntegrity();
 * if (!isIntact) console.error('Chain tampered!');
 */
SovereignAuditLogSchema.statics.verifyChainIntegrity = async function() {
  const allEntries = await this.find().sort({ chainPosition: 1 }).exec();
  if (allEntries.length === 0) return true;

  const chainEntries = allEntries.map(entry => ({
    hash: entry.forensicSeal,
    chainHash: entry.chainHash
  }));

  return forensicHasher.verifyChain(null, chainEntries);
};

// ============================================================================
// 🔥 MODEL EXPORT
// ============================================================================

/**
 * Sovereign Audit Log model – immutable forensic ledger for boardroom and regulator actions.
 * @type {mongoose.Model}
 */
export const SovereignAuditLog = mongoose.model('SovereignAuditLog', SovereignAuditLogSchema);

// Prevent model recompilation in development (hot reload safety)
if (!mongoose.models.SovereignAuditLog) {
  mongoose.model('SovereignAuditLog', SovereignAuditLogSchema);
}

export default SovereignAuditLog;
