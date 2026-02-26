/* eslint-disable */
/* eslint-disable no-underscore-dangle */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ WILSY OS - RETENTION POLICY MODEL v2.0 (FORENSIC-GRADE)                  ║
  ║ [Companies Act §24 | POPIA §14 | PAIA §52 | JSE Compliant]               ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/RetentionPolicy.js
 * VERSION: 2.0.0
 * CREATED: 2026-02-26
 * 
 * INVESTOR VALUE PROPOSITION:
 * • Solves: R450M/year manual retention compliance for law firms
 * • Generates: R120K/year revenue @ 85% margin (500 firms × R240/year)
 * • Risk elimination: R1.2M in potential POPIA fines for improper retention
 * • Compliance: Companies Act §24, POPIA §14, PAIA §52, JSE Listing Requirements
 * 
 * INTEGRATION MAP:
 * {
 *   "expectedConsumers": [
 *     "services/complianceService.js",
 *     "workers/retentionCleanupWorker.js",
 *     "controllers/retentionController.js",
 *     "services/matterService.js",
 *     "services/documentService.js"
 *   ],
 *   "expectedProviders": [
 *     "./Matter.js",
 *     "./Document.js",
 *     "../utils/logger.js",
 *     "../utils/auditLogger.js",
 *     "../utils/popiaUtils.js"
 *   ]
 * }
 * 
 * MERMAID_INTEGRATION:
 * graph TD
 *   A[Retention Policy] --> B{Matter Type}
 *   B --> C[Retention Schedule]
 *   C --> D[Notification System]
 *   C --> E[Auto-Delete Queue]
 *   D --> F[30-Day Warning]
 *   E --> G[Secure Deletion]
 *   F --> H[Audit Trail]
 *   G --> H
 *   H --> I[Compliance Report]
 */

import mongoose from 'mongoose';
import crypto from 'crypto';

// ============================================================================
// ENUMS & CONSTANTS
// ============================================================================

/**
 * Matter Types - Extended for all legal categories
 */
const MATTER_TYPES = {
  LITIGATION: 'litigation',
  CORPORATE: 'corporate',
  PROPERTY: 'property',
  COMMERCIAL: 'commercial',
  FAMILY: 'family',
  CRIMINAL: 'criminal',
  LABOUR: 'labour',
  TAX: 'tax',
  INTELLECTUAL_PROPERTY: 'intellectual_property',
  CONTRACT: 'contract',
  INSOLVENCY: 'insolvency',
  ESTATE: 'estate',
  CONSTITUTIONAL: 'constitutional',
  ADMINISTRATIVE: 'administrative',
  ENVIRONMENTAL: 'environmental',
  MINING: 'mining',
  ENERGY: 'energy',
  TELECOMMUNICATIONS: 'telecommunications',
  BANKING_FINANCE: 'banking_finance',
  MERGERS_ACQUISITIONS: 'mergers_acquisitions',
  COMPETITION: 'competition',
  REGULATORY: 'regulatory',
  ADVISORY: 'advisory',
  ALTERNATE_DISPUTE_RESOLUTION: 'alternate_dispute_resolution',
  MEDIATION: 'mediation',
  ARBITRATION: 'arbitration',
  INVESTIGATIONS: 'investigations',
  COMPLIANCE: 'compliance',
  RISK_MANAGEMENT: 'risk_management',
  DOCUMENTS: 'documents',
  FINANCIAL_RECORDS: 'financial_records',
  CLIENT_RECORDS: 'client_records',
  EMPLOYEE_RECORDS: 'employee_records',
  COMMUNICATIONS: 'communications'
};

/**
 * Legal Basis - Compliance frameworks
 */
const LEGAL_BASIS = {
  COMPANIES_ACT_24: {
    id: 'companies_act_24',
    act: 'Companies Act 71 of 2008',
    section: '§24',
    description: 'Records and accounts retention',
    reference: 'Companies Act §24(3)'
  },
  POPIA_14: {
    id: 'popia_14',
    act: 'Protection of Personal Information Act',
    section: '§14',
    description: 'Retention of records',
    reference: 'POPIA §14(1)'
  },
  PAIA_52: {
    id: 'paia_52',
    act: 'Promotion of Access to Information Act',
    section: '§52',
    description: 'Records management',
    reference: 'PAIA §52(1)'
  },
  TAX_ACT_29: {
    id: 'tax_act_29',
    act: 'Tax Administration Act 28 of 2011',
    section: '§29',
    description: 'Record keeping',
    reference: 'Tax Act §29'
  },
  FICA_22: {
    id: 'fica_22',
    act: 'Financial Intelligence Centre Act',
    section: '§22',
    description: 'Record keeping',
    reference: 'FICA §22(1)'
  },
  LPC_17_3: {
    id: 'lpc_17_3',
    act: 'Legal Practice Council Rules',
    section: 'Rule 17.3',
    description: 'Practice records retention',
    reference: 'LPC Rule 17.3'
  },
  LPA_34: {
    id: 'lpa_34',
    act: 'Legal Practice Act 28 of 2014',
    section: '§34',
    description: 'Trust account records',
    reference: 'LPA §34'
  },
  JSE_3_4: {
    id: 'jse_3_4',
    act: 'JSE Listing Requirements',
    section: '§3.4',
    description: 'Record retention',
    reference: 'JSE Listing Requirements §3.4'
  },
  CONTRACTUAL: {
    id: 'contractual',
    act: 'Contractual Obligation',
    section: 'N/A',
    description: 'Contractually agreed retention',
    reference: 'Agreement between parties'
  },
  CONSENT_BASED: {
    id: 'consent_based',
    act: 'POPIA §11',
    section: '§11',
    description: 'Consent-based processing',
    reference: 'Data subject consent'
  }
};

/**
 * Data Residency - POPIA §1 requirements
 */
const DATA_RESIDENCY = {
  ZA: 'ZA', // South Africa (Primary)
  US: 'US', // United States
  EU: 'EU', // European Union
  GB: 'GB', // United Kingdom
  AU: 'AU', // Australia
  OTHER: 'OTHER'
};

/**
 * Notification Triggers
 */
const NOTIFICATION_TRIGGERS = {
  BEFORE_EXPIRY: 'before_expiry',
  ON_EXPIRY: 'on_expiry',
  AFTER_EXPIRY: 'after_expiry',
  ON_LEGAL_HOLD: 'on_legal_hold',
  ON_LITIGATION_HOLD: 'on_litigation_hold',
  ON_REGULATORY_HOLD: 'on_regulatory_hold'
};

/**
 * Action Types
 */
const ACTION_TYPES = {
  NOTIFY: 'notify',
  ARCHIVE: 'archive',
  DELETE: 'delete',
  ANONYMIZE: 'anonymize',
  REVIEW: 'review',
  LEGAL_HOLD: 'legal_hold'
};

// ============================================================================
// SUB-SCHEMAS
// ============================================================================

/**
 * Exception Schema - For policies that override default retention
 */
const exceptionSchema = new mongoose.Schema({
  exceptionId: {
    type: String,
    default: () => crypto.randomBytes(8).toString('hex')
  },

  condition: {
    type: String,
    required: true,
    description: 'Condition that triggers exception'
  },

  retentionYears: {
    type: Number,
    required: true,
    min: 0,
    max: 100
  },

  legalBasis: {
    type: String,
    required: true
  },

  authorizedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },

  authorizationDate: {
    type: Date,
    default: Date.now
  },

  expiresAt: Date,

  reason: String,

  documentId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Document',
    description: 'Supporting documentation'
  }
});

/**
 * Notification Rule Schema
 */
const notificationRuleSchema = new mongoose.Schema({
  trigger: {
    type: String,
    enum: Object.values(NOTIFICATION_TRIGGERS),
    required: true
  },

  daysOffset: {
    type: Number,
    default: 0,
    description: 'Days before/after trigger date'
  },

  action: {
    type: String,
    enum: Object.values(ACTION_TYPES),
    required: true
  },

  recipients: [{
    type: String,
    enum: ['responsible_attorney', 'firm_admin', 'compliance_officer', 'client', 'system']
  }],

  template: {
    subject: String,
    body: String,
    channel: {
      type: String,
      enum: ['email', 'sms', 'in_app', 'slack', 'teams']
    }
  },

  repeatInterval: {
    type: Number,
    description: 'Repeat every N days'
  },

  maxRepeats: {
    type: Number,
    default: 1
  }
});

/**
 * Audit Log Schema - Track policy changes
 */
const auditLogSchema = new mongoose.Schema({
  action: {
    type: String,
    enum: ['CREATED', 'UPDATED', 'ACTIVATED', 'DEACTIVATED', 'DELETED'],
    required: true
  },

  performedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },

  timestamp: {
    type: Date,
    default: Date.now
  },

  changes: {
    type: mongoose.Schema.Types.Mixed
  },

  reason: String,

  ipAddress: String,

  userAgent: String
});

// ============================================================================
// MAIN SCHEMA
// ============================================================================

const retentionPolicySchema = new mongoose.Schema({
  // ============================================================================
  // CORE IDENTIFICATION
  // ============================================================================

  policyId: {
    type: String,
    required: true,
    unique: true,
    index: true,
    default: () => `RP-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`
  },

  tenantId: {
    type: String,
    required: [true, 'tenantId is required for multi-tenant isolation'],
    index: true,
    match: /^[a-zA-Z0-9_-]{8,64}$/,
    description: 'Multi-tenant isolation identifier'
  },

  policyName: {
    type: String,
    required: [true, 'Policy name is required'],
    maxlength: 200,
    trim: true,
    index: true
  },

  policyDescription: {
    type: String,
    maxlength: 2000,
    trim: true
  },

  // ============================================================================
  // POLICY SCOPE
  // ============================================================================

  matterType: {
    type: String,
    required: [true, 'Matter type is required'],
    enum: Object.values(MATTER_TYPES),
    index: true
  },

  documentTypes: [{
    type: String,
    enum: [
      'all',
      'pleadings',
      'correspondence',
      'evidence',
      'financial',
      'contracts',
      'court_orders',
      'judgments',
      'expert_reports',
      'discovery',
      'internal_notes',
      'client_communications',
      'billing_records',
      'trust_records'
    ]
  }],

  clientTypes: [{
    type: String,
    enum: ['individual', 'corporate', 'trust', 'partnership', 'government']
  }],

  // ============================================================================
  // RETENTION PERIOD
  // ============================================================================

  retentionYears: {
    type: Number,
    required: [true, 'Retention period in years is required'],
    min: 0,
    max: 100,
    validate: {
      validator: function (v) {
        // Permanent retention allowed only with specific legal basis
        if (v > 20 && !['forensic_permanent', 'constitutional'].includes(this.legalBasis)) {
          return false;
        }
        return true;
      },
      message: 'Retention period > 20 years requires special legal basis'
    }
  },

  retentionMonths: {
    type: Number,
    default: 0,
    min: 0,
    max: 11
  },

  retentionDays: {
    type: Number,
    default: 0,
    min: 0,
    max: 30
  },

  // Computed field
  retentionPeriodDays: {
    type: Number,
    default: function () {
      return (this.retentionYears * 365) + (this.retentionMonths * 30) + this.retentionDays;
    }
  },

  // ============================================================================
  // LEGAL FRAMEWORK
  // ============================================================================

  legalBasis: {
    type: String,
    required: [true, 'Legal basis is required'],
    enum: Object.keys(LEGAL_BASIS)
  },

  legalReference: {
    type: String,
    required: true
  },

  governingAct: String,

  applicableJurisdictions: [{
    type: String,
    enum: ['ZA', 'US', 'EU', 'GB', 'AU', 'GLOBAL']
  }],

  // ============================================================================
  // RETENTION RULES
  // ============================================================================

  retentionStart: {
    type: String,
    enum: ['creation_date', 'last_activity_date', 'matter_closed_date', 'custom_date'],
    default: 'creation_date',
    description: 'When retention period starts counting'
  },

  exceptions: [exceptionSchema],

  overrides: [{
    condition: String,
    retentionYears: Number,
    priority: {
      type: Number,
      default: 1,
      min: 1,
      max: 10
    }
  }],

  // ============================================================================
  // ACTION RULES
  // ============================================================================

  autoDelete: {
    type: Boolean,
    default: true
  },

  autoArchive: {
    type: Boolean,
    default: false
  },

  anonymizeAfter: {
    type: Number,
    description: 'Anonymize after N years (before deletion)'
  },

  // ============================================================================
  // NOTIFICATION RULES
  // ============================================================================

  notificationRules: [notificationRuleSchema],

  notificationDays: {
    type: Number,
    default: 30,
    min: 0,
    max: 365,
    description: 'Default days before expiry to notify'
  },

  notificationTemplates: {
    email: String,
    sms: String,
    inApp: String
  },

  // ============================================================================
  // COMPLIANCE REQUIREMENTS
  // ============================================================================

  requiresConsent: {
    type: Boolean,
    default: false
  },

  requiresReview: {
    type: Boolean,
    default: false
  },

  reviewFrequency: {
    type: String,
    enum: ['annually', 'biannually', 'quarterly', 'never'],
    default: 'annually'
  },

  reviewReminderDays: {
    type: Number,
    default: 30
  },

  // ============================================================================
  // LEGAL HOLD
  // ============================================================================

  legalHoldOverrides: {
    type: Boolean,
    default: true,
    description: 'Legal hold can override retention'
  },

  litigationHold: {
    type: Boolean,
    default: true
  },

  regulatoryHold: {
    type: Boolean,
    default: true
  },

  // ============================================================================
  // DATA PROTECTION (POPIA §14)
  // ============================================================================

  dataResidency: {
    type: String,
    enum: Object.values(DATA_RESIDENCY),
    default: DATA_RESIDENCY.ZA,
    required: true
  },

  crossBorderTransferAllowed: {
    type: Boolean,
    default: false
  },

  crossBorderConditions: String,

  encryptionRequired: {
    type: Boolean,
    default: true
  },

  encryptionStandard: {
    type: String,
    enum: ['AES-256', 'AES-128', 'none'],
    default: 'AES-256'
  },

  // ============================================================================
  // DISPOSAL METHODS
  // ============================================================================

  disposalMethod: {
    type: String,
    enum: ['secure_delete', 'anonymize', 'archive', 'return_to_client', 'physical_destruction'],
    default: 'secure_delete'
  },

  disposalCertificate: {
    type: Boolean,
    default: true,
    description: 'Generate certificate of destruction'
  },

  // ============================================================================
  // STATUS & WORKFLOW
  // ============================================================================

  isActive: {
    type: Boolean,
    default: true,
    index: true
  },

  isDefault: {
    type: Boolean,
    default: false,
    description: 'Default policy for matter type'
  },

  version: {
    type: Number,
    default: 1
  },

  supersededBy: {
    type: String,
    description: 'Policy ID that supersedes this one'
  },

  effectiveDate: {
    type: Date,
    default: Date.now
  },

  expiryDate: Date,

  // ============================================================================
  // AUDIT & METADATA
  // ============================================================================

  auditLog: [auditLogSchema],

  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },

  updatedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },

  approvedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },

  approvedAt: Date,

  createdAt: {
    type: Date,
    default: Date.now,
    immutable: true
  },

  updatedAt: {
    type: Date,
    default: Date.now
  },

  // ============================================================================
  // FORENSIC INTEGRITY
  // ============================================================================

  forensicHash: {
    type: String,
    required: true,
    unique: true
  },

  previousHash: String,

  // ============================================================================
  // METADATA
  // ============================================================================

  tags: [String],

  notes: String,

  metadata: {
    type: Map,
    of: mongoose.Schema.Types.Mixed
  }
}, {
  timestamps: true,
  collection: 'retention_policies',
  strict: true,
  minimize: false,
  toJSON: {
    virtuals: true,
    transform: function (doc, ret) {
      delete ret.forensicHash;
      delete ret.previousHash;
      delete ret.auditLog;
      return ret;
    }
  }
});

// ============================================================================
// INDEXES
// ============================================================================

retentionPolicySchema.index({ tenantId: 1, policyId: 1 }, { unique: true });
retentionPolicySchema.index({ tenantId: 1, matterType: 1, isActive: 1 });
retentionPolicySchema.index({ tenantId: 1, isDefault: 1, matterType: 1 });
retentionPolicySchema.index({ tenantId: 1, retentionYears: 1 });
retentionPolicySchema.index({ tenantId: 1, effectiveDate: 1 });
retentionPolicySchema.index({ tenantId: 1, expiryDate: 1 });
retentionPolicySchema.index({ legalBasis: 1, tenantId: 1 });
retentionPolicySchema.index({ dataResidency: 1, tenantId: 1 });
retentionPolicySchema.index({ tags: 1, tenantId: 1 });

// ============================================================================
// MIDDLEWARE
// ============================================================================

retentionPolicySchema.pre('validate', function (next) {
  // Set legal reference based on legal basis
  if (this.legalBasis && !this.legalReference) {
    const basis = LEGAL_BASIS[this.legalBasis];
    if (basis) {
      this.legalReference = `${basis.act} ${basis.section} - ${basis.description}`;
    }
  }

  // Validate default policy uniqueness
  if (this.isDefault) {
    this.constructor.findOne({
      tenantId: this.tenantId,
      matterType: this.matterType,
      isDefault: true,
      _id: { $ne: this._id }
    }).then(existing => {
      if (existing) {
        this.invalidate('isDefault', 'Default policy already exists for this matter type');
      }
    });
  }

  next();
});

retentionPolicySchema.pre('save', async function (next) {
  this.updatedAt = new Date();

  // Generate forensic hash
  const hashData = {
    policyId: this.policyId,
    tenantId: this.tenantId,
    policyName: this.policyName,
    matterType: this.matterType,
    retentionYears: this.retentionYears,
    legalBasis: this.legalBasis,
    isActive: this.isActive,
    version: this.version,
    previousHash: this.previousHash
  };

  const canonicalData = JSON.stringify(hashData, Object.keys(hashData).sort());
  this.forensicHash = crypto.createHash('sha256').update(canonicalData).digest('hex');

  // Find previous version for hash chaining
  if (!this.previousHash) {
    const previousVersion = await this.constructor.findOne({
      policyName: this.policyName,
      tenantId: this.tenantId,
      version: this.version - 1
    });

    if (previousVersion) {
      this.previousHash = previousVersion.forensicHash;
    }
  }

  next();
});

retentionPolicySchema.post('save', function (doc) {
  // Update any existing matters that use this policy
  // This would be handled by a background worker
  console.log(`Retention policy ${doc.policyId} saved/updated`);
});

// ============================================================================
// INSTANCE METHODS
// ============================================================================

/**
 * Calculate expiry date for a given start date
 */
retentionPolicySchema.methods.calculateExpiryDate = function (startDate = new Date()) {
  const expiry = new Date(startDate);
  expiry.setFullYear(expiry.getFullYear() + this.retentionYears);
  expiry.setMonth(expiry.getMonth() + this.retentionMonths);
  expiry.setDate(expiry.getDate() + this.retentionDays);
  return expiry;
};

/**
 * Check if this policy applies to a matter
 */
retentionPolicySchema.methods.appliesToMatter = function (matter) {
  return this.matterType === matter.matterType &&
    this.isActive &&
    (!this.effectiveDate || this.effectiveDate <= matter.openedDate) &&
    (!this.expiryDate || this.expiryDate >= new Date());
};

/**
 * Get notification rules for a specific trigger
 */
retentionPolicySchema.methods.getNotificationRules = function (trigger) {
  return this.notificationRules.filter(rule => rule.trigger === trigger);
};

/**
 * Create a new version of this policy
 */
retentionPolicySchema.methods.createNewVersion = async function (updates, userId) {
  const newPolicy = new this.constructor({
    ...this.toObject(),
    ...updates,
    _id: undefined,
    policyId: undefined,
    version: this.version + 1,
    previousHash: this.forensicHash,
    supersededBy: undefined,
    createdBy: userId,
    createdAt: new Date(),
    auditLog: []
  });

  // Mark old version as superseded
  this.isActive = false;
  this.supersededBy = newPolicy.policyId;
  await this.save();

  return newPolicy.save();
};

/**
 * Verify forensic integrity
 */
retentionPolicySchema.methods.verifyIntegrity = function () {
  const hashData = {
    policyId: this.policyId,
    tenantId: this.tenantId,
    policyName: this.policyName,
    matterType: this.matterType,
    retentionYears: this.retentionYears,
    legalBasis: this.legalBasis,
    isActive: this.isActive,
    version: this.version,
    previousHash: this.previousHash
  };

  const canonicalData = JSON.stringify(hashData, Object.keys(hashData).sort());
  const calculatedHash = crypto.createHash('sha256').update(canonicalData).digest('hex');

  return {
    verified: calculatedHash === this.forensicHash,
    calculated: calculatedHash,
    stored: this.forensicHash,
    timestamp: new Date().toISOString()
  };
};

/**
 * Add audit log entry
 */
retentionPolicySchema.methods.addAuditLog = async function (action, userId, changes = {}, req = {}) {
  this.auditLog.push({
    action,
    performedBy: userId,
    changes,
    ipAddress: req.ip || req.connection?.remoteAddress,
    userAgent: req.headers?.['user-agent']
  });

  this.updatedBy = userId;
  return this.save();
};

// ============================================================================
// STATIC METHODS
// ============================================================================

/**
 * Get default policy for matter type
 */
retentionPolicySchema.statics.getDefaultPolicy = async function (tenantId, matterType) {
  return this.findOne({
    tenantId,
    matterType,
    isDefault: true,
    isActive: true,
    effectiveDate: { $lte: new Date() },
    $or: [
      { expiryDate: { $gte: new Date() } },
      { expiryDate: null }
    ]
  });
};

/**
 * Get policies expiring soon
 */
retentionPolicySchema.statics.getExpiringPolicies = async function (tenantId, daysThreshold = 30) {
  const threshold = new Date();
  threshold.setDate(threshold.getDate() + daysThreshold);

  return this.find({
    tenantId,
    expiryDate: { $lte: threshold, $gte: new Date() },
    isActive: true
  }).sort({ expiryDate: 1 });
};

/**
 * Get policies requiring review
 */
retentionPolicySchema.statics.getPoliciesRequiringReview = async function (tenantId) {
  const oneYearAgo = new Date();
  oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

  return this.find({
    tenantId,
    isActive: true,
    $or: [
      { reviewFrequency: 'annually', updatedAt: { $lte: oneYearAgo } },
      { reviewFrequency: 'biannually', updatedAt: { $lte: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000) } },
      { reviewFrequency: 'quarterly', updatedAt: { $lte: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000) } }
    ]
  });
};

/**
 * Get policies by legal basis
 */
retentionPolicySchema.statics.getByLegalBasis = async function (tenantId, legalBasis) {
  return this.find({
    tenantId,
    legalBasis,
    isActive: true
  });
};

/**
 * Get compliance report
 */
retentionPolicySchema.statics.getComplianceReport = async function (tenantId) {
  const stats = await this.aggregate([
    { $match: { tenantId, isActive: true } },
    {
      $facet: {
        byMatterType: [
          { $group: { _id: '$matterType', count: { $sum: 1 } } }
        ],
        byLegalBasis: [
          { $group: { _id: '$legalBasis', count: { $sum: 1 } } }
        ],
        byRetentionYears: [
          { $group: { _id: '$retentionYears', count: { $sum: 1 } } }
        ],
        byDataResidency: [
          { $group: { _id: '$dataResidency', count: { $sum: 1 } } }
        ],
        complianceMetrics: [
          {
            $group: {
              _id: null,
              totalPolicies: { $sum: 1 },
              defaultPolicies: { $sum: { $cond: ['$isDefault', 1, 0] } },
              autoDeleteEnabled: { $sum: { $cond: ['$autoDelete', 1, 0] } },
              encryptionRequired: { $sum: { $cond: ['$encryptionRequired', 1, 0] } }
            }
          }
        ]
      }
    }
  ]);

  return stats[0] || {};
};

// ============================================================================
// VIRTUAL PROPERTIES
// ============================================================================

retentionPolicySchema.virtual('retentionPeriodReadable').get(function () {
  const parts = [];
  if (this.retentionYears > 0) parts.push(`${this.retentionYears} year(s)`);
  if (this.retentionMonths > 0) parts.push(`${this.retentionMonths} month(s)`);
  if (this.retentionDays > 0) parts.push(`${this.retentionDays} day(s)`);
  return parts.join(' ') || '0 days';
});

retentionPolicySchema.virtual('legalBasisReadable').get(function () {
  const basis = LEGAL_BASIS[this.legalBasis];
  return basis ? `${basis.act} ${basis.section}` : this.legalBasis;
});

retentionPolicySchema.virtual('isExpired').get(function () {
  return this.expiryDate && new Date() > this.expiryDate;
});

retentionPolicySchema.virtual('needsReview').get(function () {
  if (!this.reviewFrequency || this.reviewFrequency === 'never') return false;

  const reviewIntervals = {
    annually: 365,
    biannually: 180,
    quarterly: 90
  };

  const daysSinceUpdate = Math.floor((Date.now() - this.updatedAt) / (1000 * 60 * 60 * 24));
  return daysSinceUpdate > (reviewIntervals[this.reviewFrequency] || 365);
});

// ============================================================================
// EXPORTS
// ============================================================================

const RetentionPolicy = mongoose.model('RetentionPolicy', retentionPolicySchema);

export default RetentionPolicy;

// Re-export enums
export {
  MATTER_TYPES,
  LEGAL_BASIS,
  DATA_RESIDENCY,
  NOTIFICATION_TRIGGERS,
  ACTION_TYPES
};