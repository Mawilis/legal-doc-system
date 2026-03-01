#!/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - VALIDATION AUDIT MODEL v1.0                                    ║
 * ║ [Production Grade | POPIA §19 | Forensic Validation Trail]                ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 * 
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/ValidationAudit.js
 * VERSION: 1.0.0
 * CREATED: 2026-02-24
 * 
 * INVESTOR VALUE PROPOSITION:
 * • Complete audit trail of all data validations for regulatory compliance
 * • POPIA §19 security safeguards verification
 * • ECT Act §15 data message integrity tracking
 * • Forensic evidence for disputes and litigation
 * • Multi-tenant validation isolation
 * 
 * DEPENDENCIES:
 * • mongoose ^8.2.4 - MongoDB ODM
 * • crypto (built-in) - SHA256 hashing
 * 
 * INTEGRATION MAP:
 * {
 *   "consumers": [
 *     "validators/*.js",
 *     "middleware/validation.js",
 *     "services/complianceService.js",
 *     "controllers/auditController.js"
 *   ],
 *   "providers": [
 *     "./plugins/auditPlugin.js",
 *     "../utils/auditLogger.js"
 *   ]
 * }
 */

import mongoose from "mongoose";
import crypto from "crypto";

/**
 * Validation Types Enum
 */
const VALIDATION_TYPES = {
  SCHEMA: 'schema_validation',
  BUSINESS_RULE: 'business_rule_validation',
  COMPLIANCE: 'compliance_validation',
  DATA_INTEGRITY: 'data_integrity_validation',
  CROSS_FIELD: 'cross_field_validation',
  REGULATORY: 'regulatory_validation',
  POPIA: 'popia_validation',
  FICA: 'fica_validation',
  TAX: 'tax_validation',
  CONSENT: 'consent_validation'
};

/**
 * Validation Status Enum
 */
const VALIDATION_STATUS = {
  PASSED: 'passed',
  FAILED: 'failed',
  WARNING: 'warning',
  SKIPPED: 'skipped',
  PENDING: 'pending'
};

/**
 * Validation Severity Enum
 */
const VALIDATION_SEVERITY = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  CRITICAL: 'critical'
};

/**
 * Validation Audit Schema
 * Tracks all validations performed across the system
 */
const validationAuditSchema = new mongoose.Schema({
  /**
   * Core Fields
   */
  validationId: {
    type: String,
    required: true,
    unique: true,
    index: true,
    default: () => `val-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`
  },

  timestamp: {
    type: Date,
    default: Date.now,
    required: true,
    index: true,
    immutable: true
  },

  validationType: {
    type: String,
    required: true,
    enum: Object.values(VALIDATION_TYPES),
    index: true
  },

  status: {
    type: String,
    required: true,
    enum: Object.values(VALIDATION_STATUS),
    default: VALIDATION_STATUS.PENDING,
    index: true
  },

  severity: {
    type: String,
    required: true,
    enum: Object.values(VALIDATION_SEVERITY),
    default: VALIDATION_SEVERITY.INFO,
    index: true
  },

  /**
   * Context
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

  requestId: {
    type: String,
    required: true,
    index: true,
    validate: {
      validator: (v) => /^[a-f0-9]{16,32}$/i.test(v),
      message: 'requestId must be a valid hexadecimal string'
    }
  },

  /**
   * Validation Target
   */
  targetModel: {
    type: String,
    required: true,
    index: true
  },

  targetId: {
    type: String,
    required: true,
    index: true
  },

  targetVersion: {
    type: Number,
    default: 1
  },

  /**
   * Validation Rules Applied
   */
  rulesApplied: [{
    ruleName: {
      type: String,
      required: true
    },
    ruleVersion: String,
    ruleCategory: String,
    ruleDescription: String,
    parameters: mongoose.Schema.Types.Mixed
  }],

  /**
   * Validation Results
   */
  results: {
    passed: {
      type: Number,
      default: 0
    },
    failed: {
      type: Number,
      default: 0
    },
    warnings: {
      type: Number,
      default: 0
    },
    total: {
      type: Number,
      default: 0
    }
  },

  failures: [{
    ruleName: String,
    field: String,
    value: mongoose.Schema.Types.Mixed,
    expected: mongoose.Schema.Types.Mixed,
    message: String,
    code: String,
    severity: {
      type: String,
      enum: Object.values(VALIDATION_SEVERITY)
    }
  }],

  warnings: [{
    ruleName: String,
    field: String,
    message: String,
    suggestion: String
  }],

  /**
   * Input/Output Data (redacted for PII)
   */
  inputData: {
    type: mongoose.Schema.Types.Mixed,
    required: true,
    validate: {
      validator: function(v) {
        // Ensure input data exists
        return v !== null && v !== undefined;
      },
      message: 'Input data is required'
    }
  },

  outputData: {
    type: mongoose.Schema.Types.Mixed,
    default: null
  },

  /**
   * Redaction Tracking
   */
  piiFields: [{
    field: String,
    redacted: Boolean,
    redactionMethod: String
  }],

  containsPII: {
    type: Boolean,
    default: false
  },

  /**
   * Performance Metrics
   */
  duration: {
    type: Number, // milliseconds
    required: true,
    min: 0
  },

  memoryUsed: Number, // bytes
  cpuTime: Number, // milliseconds

  /**
   * Compliance Tracking
   */
  complianceFrameworks: [{
    framework: {
      type: String,
      enum: ['POPIA', 'ECT', 'COMPANIES_ACT', 'FICA', 'TAX_ACT', 'LPC']
    },
    section: String,
    requirement: String,
    verified: Boolean,
    verifiedAt: Date
  }],

  /**
   * Regulatory Notifications
   */
  requiresNotification: {
    type: Boolean,
    default: false
  },

  notificationSent: {
    type: Boolean,
    default: false
  },

  notificationDetails: {
    sentAt: Date,
    recipient: String,
    reference: String
  },

  /**
   * Data Retention (POPIA §14)
   */
  retentionPolicy: {
    type: String,
    enum: {
      values: [
        'companies_act_10_years',
        'popia_1_year',
        'tax_act_5_years',
        'forensic_permanent'
      ]
    },
    default: 'companies_act_10_years',
    required: true
  },

  dataResidency: {
    type: String,
    enum: ['ZA', 'US', 'EU', 'GB', 'AU'],
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
      const endDate = new Date(this.retentionStart);
      switch(this.retentionPolicy) {
        case 'companies_act_10_years':
          endDate.setFullYear(endDate.getFullYear() + 10);
          break;
        case 'popia_1_year':
          endDate.setFullYear(endDate.getFullYear() + 1);
          break;
        case 'tax_act_5_years':
          endDate.setFullYear(endDate.getFullYear() + 5);
          break;
        case 'forensic_permanent':
          endDate.setFullYear(endDate.getFullYear() + 100);
          break;
      }
      return endDate;
    }
  },

  /**
   * Forensic Integrity
   */
  forensicHash: {
    type: String,
    required: true,
    unique: true
  },

  previousHash: {
    type: String,
    default: null,
    index: true
  },

  /**
   * Metadata
   */
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

  notes: String
}, {
  timestamps: true,
  collection: 'validation_audits',
  strict: true,
  minimize: false
});

/**
 * Indexes for query performance
 */
validationAuditSchema.index({ tenantId: 1, timestamp: -1 });
validationAuditSchema.index({ targetModel: 1, targetId: 1, timestamp: -1 });
validationAuditSchema.index({ validationType: 1, status: 1 });
validationAuditSchema.index({ 'complianceFrameworks.framework': 1, 'complianceFrameworks.verified': 1 });
validationAuditSchema.index({ requiresNotification: 1, notificationSent: 1 });
validationAuditSchema.index({ retentionEnd: 1 }, { expireAfterSeconds: 0 });

/**
 * Pre-save middleware for hash generation
 */
validationAuditSchema.pre('save', async function(next) {
  try {
    this.updatedAt = new Date();

    // Find the latest validation for hash chaining
    const lastValidation = await this.constructor.findOne(
      { tenantId: this.tenantId },
      { forensicHash: 1 },
      { sort: { timestamp: -1 } }
    );

    if (lastValidation) {
      this.previousHash = lastValidation.forensicHash;
    }

    // Create canonical string for hashing
    const canonicalData = JSON.stringify({
      validationId: this.validationId,
      timestamp: this.timestamp,
      validationType: this.validationType,
      status: this.status,
      tenantId: this.tenantId,
      targetModel: this.targetModel,
      targetId: this.targetId,
      rulesApplied: this.rulesApplied,
      results: this.results,
      failures: this.failures,
      previousHash: this.previousHash
    }, Object.keys.sort());

    // Generate SHA256 hash
    this.forensicHash = crypto
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
validationAuditSchema.pre('findOneAndUpdate', function() {
  this.set({ updatedAt: new Date() });
});

/**
 * Static method: Get validation stats for a tenant
 */
validationAuditSchema.statics.getValidationStats = async function(tenantId, days = 30) {
  const since = new Date();
  since.setDate(since.getDate() - days);

  const stats = await this.aggregate([
    { $match: { tenantId, timestamp: { $gte: since } } },
    { $group: {
      _id: {
        validationType: '$validationType',
        status: '$status'
      },
      count: { $sum: 1 },
      avgDuration: { $avg: '$duration' },
      totalFailures: { $sum: '$results.failed' }
    }},
    { $group: {
      _id: '$_id.validationType',
      statuses: {
        $push: {
          status: '$_id.status',
          count: '$count',
          avgDuration: '$avgDuration',
          totalFailures: '$totalFailures'
        }
      },
      total: { $sum: '$count' }
    }},
    { $sort: { total: -1 } }
  ]);

  return stats;
};

/**
 * Static method: Find validations requiring regulatory attention
 */
validationAuditSchema.statics.findRegulatoryIssues = function(tenantId) {
  return this.find({
    tenantId,
    'complianceFrameworks.verified': false,
    severity: { $in: ['error', 'critical'] }
  })
  .sort({ timestamp: -1 })
  .limit(100)
  .lean();
};

/**
 * Static method: Get validation history for a specific record
 */
validationAuditSchema.statics.getRecordValidationHistory = function(targetModel, targetId) {
  return this.find({ targetModel, targetId })
    .sort({ timestamp: -1 })
    .limit(50)
    .lean();
};

/**
 * Static method: Verify hash chain integrity
 */
validationAuditSchema.statics.verifyHashChain = async function(tenantId, fromDate = null) {
  const query = { tenantId };
  if (fromDate) {
    query.timestamp = { $gte: fromDate };
  }

  const validations = await this.find(query)
    .sort({ timestamp: 1 })
    .lean();

  const brokenLinks = [];

  for (let i = 1; i < validations.length; i++) {
    const expectedHash = validations[i-1].forensicHash;
    if (validations[i].previousHash !== expectedHash) {
      brokenLinks.push({
        index: i,
        validationId: validations[i].validationId,
        timestamp: validations[i].timestamp,
        expected: expectedHash,
        actual: validations[i].previousHash
      });
    }
  }

  return {
    verified: brokenLinks.length === 0,
    totalValidations: validations.length,
    brokenLinks
  };
};

/**
 * Instance method: Get redacted view (remove PII)
 */
validationAuditSchema.methods.getRedactedView = function() {
  const redacted = this.toObject();
  
  // Redact PII from input data
  if (this.containsPII && this.piiFields) {
    this.piiFields.forEach(pii => {
      if (redacted.inputData && pii.field in redacted.inputData) {
        redacted.inputData[pii.field] = '[REDACTED]';
      }
    });
  }

  // Remove sensitive fields
  delete redacted.forensicHash;
  delete redacted.previousHash;

  return redacted;
};

/**
 * Instance method: Generate compliance report
 */
validationAuditSchema.methods.generateComplianceReport = function() {
  return {
    validationId: this.validationId,
    timestamp: this.timestamp,
    validationType: this.validationType,
    status: this.status,
    targetModel: this.targetModel,
    targetId: this.targetId,
    complianceFrameworks: this.complianceFrameworks,
    requiresNotification: this.requiresNotification,
    retentionPolicy: this.retentionPolicy,
    retentionEnd: this.retentionEnd,
    dataResidency: this.dataResidency,
    hash: this.forensicHash,
    previousHash: this.previousHash
  };
};

/**
 * Static method: Create validation audit entry
 */
validationAuditSchema.statics.createAudit = async function(data) {
  const audit = new this({
    validationType: data.validationType,
    tenantId: data.tenantId,
    userId: data.userId,
    requestId: data.requestId,
    targetModel: data.targetModel,
    targetId: data.targetId,
    targetVersion: data.targetVersion,
    rulesApplied: data.rulesApplied || [],
    results: data.results || { passed: 0, failed: 0, warnings: 0, total: 0 },
    failures: data.failures || [],
    warnings: data.warnings || [],
    inputData: data.inputData,
    outputData: data.outputData,
    containsPII: data.containsPII || false,
    piiFields: data.piiFields || [],
    duration: data.duration,
    memoryUsed: data.memoryUsed,
    cpuTime: data.cpuTime,
    complianceFrameworks: data.complianceFrameworks || [],
    requiresNotification: data.requiresNotification || false,
    severity: data.severity || VALIDATION_SEVERITY.INFO,
    tags: data.tags || [],
    notes: data.notes
  });

  return audit.save();
};

// Export constants
export const ValidationTypes = VALIDATION_TYPES;
export const ValidationStatus = VALIDATION_STATUS;
export const ValidationSeverity = VALIDATION_SEVERITY;

// Create and export the model
const ValidationAuditModel = mongoose.model('ValidationAudit', validationAuditSchema);

export default ValidationAuditModel;
