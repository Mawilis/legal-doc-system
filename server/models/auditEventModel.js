
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - AUDIT EVENT MODEL v1.0                                         ║
 * ║ [Production Grade | POPIA §19-22 | Forensic Event Trail]                 ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 * 
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/auditEventModel.js
 * VERSION: 1.0.0
 * CREATED: 2026-02-24
 * 
 * INVESTOR VALUE PROPOSITION:
 * • Complete audit trail of all system events for regulatory compliance
 * • POPIA §19-22 security safeguards and breach notification
 * • ECT Act §15 data message integrity verification
 * • Companies Act §28 records retention enforcement
 * • LPC Rule 17.3 attorney audit trail compliance
 * • LPC Rule 21.1 trust account traceability
 * 
 * DEPENDENCIES:
 * • mongoose ^8.2.4 - MongoDB ODM
 * • crypto (built-in) - SHA256 hashing
 * 
 * INTEGRATION MAP:
 * {
 *   "consumers": [
 *     "utils/auditLogger.js",
 *     "middleware/auditMiddleware.js",
 *     "services/complianceService.js",
 *     "controllers/auditController.js",
 *     "workers/auditWorker.js"
 *   ],
 *   "providers": [
 *     "./plugins/auditPlugin.js",
 *     "../utils/auditUtils.js"
 *   ]
 * }
 */

import mongoose from 'mongoose';
import crypto from 'crypto';

/**
 * Event Categories Enum
 */
const EVENT_CATEGORIES = {
  // Authentication Events
  AUTH: 'authentication',
  LOGIN: 'login',
  LOGOUT: 'logout',
  PASSWORD_CHANGE: 'password_change',
  MFA: 'multi_factor_auth',
  
  // Authorization Events
  AUTHORIZATION: 'authorization',
  PERMISSION_CHANGE: 'permission_change',
  ROLE_CHANGE: 'role_change',
  
  // Data Events
  DATA_ACCESS: 'data_access',
  DATA_CREATE: 'data_create',
  DATA_UPDATE: 'data_update',
  DATA_DELETE: 'data_delete',
  DATA_EXPORT: 'data_export',
  DATA_IMPORT: 'data_import',
  
  // Compliance Events
  COMPLIANCE_CHECK: 'compliance_check',
  CONSENT_CHANGE: 'consent_change',
  POPIA_BREACH: 'popia_breach',
  REGULATORY_REPORT: 'regulatory_report',
  
  // Security Events
  SECURITY_ALERT: 'security_alert',
  THREAT_DETECTED: 'threat_detected',
  INCIDENT_REPORT: 'incident_report',
  
  // System Events
  SYSTEM_STARTUP: 'system_startup',
  SYSTEM_SHUTDOWN: 'system_shutdown',
  CONFIG_CHANGE: 'config_change',
  BACKUP: 'backup',
  RESTORE: 'restore',
  
  // Tenant Events
  TENANT_CREATE: 'tenant_create',
  TENANT_UPDATE: 'tenant_update',
  TENANT_DELETE: 'tenant_delete',
  TENANT_CONFIG: 'tenant_config',
  
  // User Events
  USER_CREATE: 'user_create',
  USER_UPDATE: 'user_update',
  USER_DELETE: 'user_delete',
  USER_SUSPEND: 'user_suspend',
  USER_ACTIVATE: 'user_activate',
  
  // Document Events
  DOCUMENT_UPLOAD: 'document_upload',
  DOCUMENT_DOWNLOAD: 'document_download',
  DOCUMENT_SHARE: 'document_share',
  DOCUMENT_SIGN: 'document_sign',
  DOCUMENT_VERIFY: 'document_verify',
  
  // Financial Events
  PAYMENT: 'payment',
  INVOICE: 'invoice',
  TRUST_ACCOUNT: 'trust_account',
  TAX_CALCULATION: 'tax_calculation',
  
  // Legal Events
  CASE_CREATE: 'case_create',
  CASE_UPDATE: 'case_update',
  PRECEDENT_ANALYSIS: 'precedent_analysis',
  LEGAL_RESEARCH: 'legal_research'
};

/**
 * Event Severity Levels
 */
const EVENT_SEVERITY = {
  DEBUG: 'debug',
  INFO: 'info',
  NOTICE: 'notice',
  WARNING: 'warning',
  ERROR: 'error',
  CRITICAL: 'critical',
  ALERT: 'alert',
  EMERGENCY: 'emergency'
};

/**
 * Event Status
 */
const EVENT_STATUS = {
  SUCCESS: 'success',
  FAILURE: 'failure',
  PENDING: 'pending',
  PROCESSING: 'processing',
  CANCELLED: 'cancelled'
};

/**
 * Audit Event Schema
 * Tracks all significant system events for compliance
 */
const auditEventSchema = new mongoose.Schema({
  /**
   * Core Fields
   */
  eventId: {
    type: String,
    required: true,
    unique: true,
    index: true,
    default: () => `evt-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`
  },

  timestamp: {
    type: Date,
    default: Date.now,
    required: true,
    index: true,
    immutable: true
  },

  eventCategory: {
    type: String,
    required: true,
    enum: Object.values(EVENT_CATEGORIES),
    index: true
  },

  eventType: {
    type: String,
    required: true,
    index: true
  },

  severity: {
    type: String,
    required: true,
    enum: Object.values(EVENT_SEVERITY),
    default: EVENT_SEVERITY.INFO,
    index: true
  },

  status: {
    type: String,
    required: true,
    enum: Object.values(EVENT_STATUS),
    default: EVENT_STATUS.SUCCESS,
    index: true
  },

  /**
   * Identity & Context
   */
  tenantId: {
    type: String,
    required: true,
    index: true,
    validate: {
      validator: (v) => /^[a-zA-Z0-9_-]{8,64}$/.test(v),
      message: 'tenantId must be 8-64 alphanumeric characters'
    }
  },

  userId: {
    type: String,
    index: true,
    sparse: true
  },

  sessionId: {
    type: String,
    index: true,
    sparse: true
  },

  requestId: {
    type: String,
    required: true,
    index: true,
    validate: {
      validator: (v) => /^[a-f0-9]{16,32}$/i.test(v),
      message: 'requestId must be a valid hexadecimal string'
    }
  },

  correlationId: {
    type: String,
    index: true,
    sparse: true
  },

  /**
   * Source Information
   */
  source: {
    ipAddress: {
      type: String,
      validate: {
        validator: (v) => !v || /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$|^([a-f0-9:]+)$/i.test(v),
        message: 'Invalid IP address format'
      }
    },
    userAgent: {
      type: String,
      maxlength: 500
    },
    referer: String,
    endpoint: String,
    method: {
      type: String,
      enum: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
    },
    platform: String,
    browser: String,
    device: String
  },

  /**
   * Target Information
   */
  target: {
    type: {
      type: String,
      enum: ['user', 'tenant', 'document', 'case', 'payment', 'config', 'system']
    },
    id: String,
    name: String,
    version: Number,
    previousState: mongoose.Schema.Types.Mixed
  },

  /**
   * Event Data
   */
  data: {
    input: mongoose.Schema.Types.Mixed,
    output: mongoose.Schema.Types.Mixed,
    changes: [{
      field: String,
      oldValue: mongoose.Schema.Types.Mixed,
      newValue: mongoose.Schema.Types.Mixed
    }],
    metadata: mongoose.Schema.Types.Mixed
  },

  /**
   * PII Redaction Tracking
   */
  piiFields: [{
    field: String,
    redacted: Boolean,
    category: {
      type: String,
      enum: ['personal', 'financial', 'biometric', 'health', 'criminal']
    }
  }],

  containsPII: {
    type: Boolean,
    default: false
  },

  redactionApplied: {
    type: Boolean,
    default: false
  },

  /**
   * Performance Metrics
   */
  performance: {
    duration: Number, // milliseconds
    memoryUsed: Number, // bytes
    cpuTime: Number, // milliseconds
    databaseQueries: Number,
    apiCalls: Number
  },

  /**
   * Compliance Tracking
   */
  compliance: {
    frameworks: [{
      name: {
        type: String,
        enum: ['POPIA', 'ECT', 'COMPANIES_ACT', 'FICA', 'LPC', 'GDPR']
      },
      sections: [String],
      requirements: [String],
      verified: Boolean,
      verifiedAt: Date
    }],
    
    retentionCategory: {
      type: String,
      enum: [
        'audit_trail',
        'financial_record',
        'legal_document',
        'user_data',
        'system_log',
        'compliance_report'
      ],
      required: true
    },

    legalHold: {
      active: { type: Boolean, default: false },
      reason: String,
      initiatedBy: String,
      initiatedAt: Date,
      expiresAt: Date
    }
  },

  /**
   * Data Retention (POPIA §14, Companies Act §28)
   */
  retention: {
    policy: {
      type: String,
      enum: {
        values: [
          'companies_act_10_years',
          'popia_1_year',
          'tax_act_5_years',
          'lpc_7_years',
          'forensic_permanent'
        ]
      },
      default: 'companies_act_10_years',
      required: true
    },

    dataResidency: {
      type: String,
      enum: ['ZA', 'US', 'EU', 'GB', 'AU', 'CA'],
      default: 'ZA',
      required: true
    },

    retentionStart: {
      type: Date,
      default: Date.now,
      required: true
    },

    retentionEnd: {
      type: Date,
      default: function() {
        const endDate = new Date(this.retention.retentionStart);
        switch(this.retention.policy) {
          case 'companies_act_10_years':
            endDate.setFullYear(endDate.getFullYear() + 10);
            break;
          case 'popia_1_year':
            endDate.setFullYear(endDate.getFullYear() + 1);
            break;
          case 'tax_act_5_years':
            endDate.setFullYear(endDate.getFullYear() + 5);
            break;
          case 'lpc_7_years':
            endDate.setFullYear(endDate.getFullYear() + 7);
            break;
          case 'forensic_permanent':
            endDate.setFullYear(endDate.getFullYear() + 100);
            break;
        }
        return endDate;
      }
    },

    archivalDate: Date,
    archivalLocation: String,
    destroyedAt: Date,
    destructionCertificate: String
  },

  /**
   * Forensic Integrity
   */
  forensic: {
    hash: {
      type: String,
      required: true,
      unique: true
    },
    previousHash: {
      type: String,
      default: null,
      index: true
    },
    signature: String,
    signedBy: String,
    signedAt: Date,
    blockchainAnchor: {
      transactionId: String,
      blockNumber: Number,
      network: String,
      timestamp: Date
    }
  },

  /**
   * Notifications
   */
  notifications: [{
    channel: {
      type: String,
      enum: ['email', 'slack', 'webhook', 'sms', 'in_app']
    },
    sent: Boolean,
    sentAt: Date,
    recipients: [String],
    status: String,
    error: String
  }],

  /**
   * Metadata
   */
  metadata: {
    createdAt: {
      type: Date,
      default: Date.now,
      immutable: true,
      index: true
    },
    updatedAt: {
      type: Date,
      default: Date.now
    },
    createdBy: {
      type: String,
      default: 'system'
    },
    version: {
      type: Number,
      default: 1
    },
    tags: [String],
    notes: String,
    environment: {
      type: String,
      enum: ['development', 'staging', 'production'],
      default: process.env.NODE_ENV || 'development'
    }
  }
}, {
  timestamps: true,
  collection: 'audit_events',
  strict: true,
  minimize: false
});

/**
 * Indexes for query performance
 */
auditEventSchema.index({ 'metadata.createdAt': -1 });
auditEventSchema.index({ tenantId: 1, 'metadata.createdAt': -1 });
auditEventSchema.index({ eventCategory: 1, severity: 1, 'metadata.createdAt': -1 });
auditEventSchema.index({ userId: 1, 'metadata.createdAt': -1 });
auditEventSchema.index({ 'target.id': 1, 'target.type': 1 });
auditEventSchema.index({ 'compliance.frameworks.name': 1, 'compliance.frameworks.verified': 1 });
auditEventSchema.index({ 'retention.retentionEnd': 1 }, { expireAfterSeconds: 0 });
auditEventSchema.index({ 'forensic.hash': 1 }, { unique: true });
auditEventSchema.index({ 'forensic.previousHash': 1 });
auditEventSchema.index({ correlationId: 1 });
auditEventSchema.index({ requestId: 1 });

/**
 * Pre-save middleware for forensic hash generation
 */
auditEventSchema.pre('save', async function(next) {
  try {
    this.metadata.updatedAt = new Date();

    // Find the latest audit event for hash chaining
    const lastEvent = await this.constructor.findOne(
      { tenantId: this.tenantId },
      { 'forensic.hash': 1 },
      { sort: { 'metadata.createdAt': -1 } }
    );

    if (lastEvent) {
      this.forensic.previousHash = lastEvent.forensic.hash;
    }

    // Create canonical string for hashing (deterministic order)
    const canonicalData = JSON.stringify({
      eventId: this.eventId,
      timestamp: this.timestamp,
      eventCategory: this.eventCategory,
      eventType: this.eventType,
      severity: this.severity,
      status: this.status,
      tenantId: this.tenantId,
      userId: this.userId,
      requestId: this.requestId,
      target: this.target,
      data: this.data,
      compliance: this.compliance,
      retention: this.retention,
      previousHash: this.forensic.previousHash
    }, Object.keys.sort());

    // Generate SHA256 hash (court-admissible)
    this.forensic.hash = crypto
      .createHash('sha256')
      .update(canonicalData)
      .digest('hex');

    next();
  } catch (error) {
    next(error);
  }
});

/**
 * Pre-update middleware
 */
auditEventSchema.pre('findOneAndUpdate', function() {
  this.set({ 'metadata.updatedAt': new Date() });
});

/**
 * Static method: Get audit trail for a specific entity
 */
auditEventSchema.statics.getEntityAuditTrail = function(
  targetType, 
  targetId, 
  limit = 100,
  fromDate = null
) {
  const query = {
    'target.type': targetType,
    'target.id': targetId
  };

  if (fromDate) {
    query['metadata.createdAt'] = { $gte: fromDate };
  }

  return this.find(query)
    .sort({ 'metadata.createdAt': -1 })
    .limit(limit)
    .lean();
};

/**
 * Static method: Get events by tenant with date range
 */
auditEventSchema.statics.getTenantEvents = function(
  tenantId,
  startDate,
  endDate,
  categories = null,
  limit = 1000
) {
  const query = {
    tenantId,
    'metadata.createdAt': {
      $gte: startDate,
      $lte: endDate
    }
  };

  if (categories) {
    query.eventCategory = { $in: categories };
  }

  return this.find(query)
    .sort({ 'metadata.createdAt': -1 })
    .limit(limit)
    .lean();
};

/**
 * Static method: Get events by user
 */
auditEventSchema.statics.getUserEvents = function(userId, limit = 100) {
  return this.find({ userId })
    .sort({ 'metadata.createdAt': -1 })
    .limit(limit)
    .lean();
};

/**
 * Static method: Get compliance report for date range
 */
auditEventSchema.statics.getComplianceReport = async function(
  tenantId,
  startDate,
  endDate,
  frameworks = null
) {
  const match = {
    tenantId,
    'metadata.createdAt': { $gte: startDate, $lte: endDate }
  };

  if (frameworks) {
    match['compliance.frameworks.name'] = { $in: frameworks };
  }

  const report = await this.aggregate([
    { $match: match },
    { $group: {
      _id: {
        date: { $dateToString: { format: '%Y-%m-%d', date: '$metadata.createdAt' } },
        eventCategory: '$eventCategory',
        severity: '$severity'
      },
      count: { $sum: 1 },
      events: { $push: '$$ROOT' }
    }},
    { $sort: { '_id.date': -1 } }
  ]);

  return report;
};

/**
 * Static method: Verify hash chain integrity
 */
auditEventSchema.statics.verifyHashChain = async function(tenantId, fromDate = null) {
  const query = { tenantId };
  if (fromDate) {
    query['metadata.createdAt'] = { $gte: fromDate };
  }

  const events = await this.find(query)
    .sort({ 'metadata.createdAt': 1 })
    .lean();

  const brokenLinks = [];

  for (let i = 1; i < events.length; i++) {
    const expectedHash = events[i-1].forensic.hash;
    if (events[i].forensic.previousHash !== expectedHash) {
      brokenLinks.push({
        index: i,
        eventId: events[i].eventId,
        timestamp: events[i].timestamp,
        expected: expectedHash,
        actual: events[i].forensic.previousHash
      });
    }
  }

  return {
    verified: brokenLinks.length === 0,
    totalEvents: events.length,
    brokenLinks
  };
};

/**
 * Static method: Get retention summary
 */
auditEventSchema.statics.getRetentionSummary = async function() {
  const now = new Date();

  const summary = await this.aggregate([
    { $match: { 'retention.retentionEnd': { $lt: now } } },
    { $group: {
      _id: '$retention.policy',
      count: { $sum: 1 },
      oldestEvent: { $min: '$metadata.createdAt' },
      newestEvent: { $max: '$metadata.createdAt' }
    }},
    { $sort: { count: -1 } }
  ]);

  return summary;
};

/**
 * Instance method: Get redacted view (remove PII)
 */
auditEventSchema.methods.getRedactedView = function() {
  const redacted = this.toObject();
  
  // Redact PII from data
  if (this.containsPII && this.piiFields) {
    this.piiFields.forEach(pii => {
      if (redacted.data && redacted.data.input && pii.field in redacted.data.input) {
        redacted.data.input[pii.field] = '[REDACTED]';
      }
      if (redacted.data && redacted.data.output && pii.field in redacted.data.output) {
        redacted.data.output[pii.field] = '[REDACTED]';
      }
    });
  }

  // Remove forensic data for external sharing
  delete redacted.forensic;
  delete redacted['$__'];
  delete redacted['$isNew'];

  return redacted;
};

/**
 * Instance method: Generate court-admissible evidence
 */
auditEventSchema.methods.generateEvidence = function() {
  return {
    eventId: this.eventId,
    timestamp: this.timestamp,
    eventCategory: this.eventCategory,
    eventType: this.eventType,
    severity: this.severity,
    tenantId: this.tenantId,
    userId: this.userId,
    requestId: this.requestId,
    source: this.source,
    target: this.target,
    data: this.data,
    forensic: {
      hash: this.forensic.hash,
      previousHash: this.forensic.previousHash,
      blockchainAnchor: this.forensic.blockchainAnchor
    },
    metadata: {
      createdAt: this.metadata.createdAt,
      version: this.metadata.version
    }
  };
};

// Export constants
export const EventCategories = EVENT_CATEGORIES;
export const EventSeverity = EVENT_SEVERITY;
export const EventStatus = EVENT_STATUS;

// Create and export the model
const AuditEventModel = mongoose.model('AuditEvent', auditEventSchema);

export default AuditEventModel;
