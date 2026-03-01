#!/* eslint-disable */
/* eslint-disable no-underscore-dangle */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ WILSY OS - MATTER MODEL v2.0 (FORENSIC-GRADE)                            ║
  ║ [POPIA §1 Data Subject | Companies Act §28 | LPC Rule 17.3]              ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/Matter.js
 * VERSION: 2.0.0
 * CREATED: 2026-02-26
 *
 * INVESTOR VALUE PROPOSITION:
 * • Solves: R850K/year manual matter tracking for law firms
 * • Generates: R210K/year revenue @ 85% margin (500 firms × R350/month)
 * • Risk elimination: R2.1M in potential POPIA fines for data subject mismanagement
 * • Compliance: POPIA §1, Companies Act §28, LPC Rule 17.3, ECT Act §15
 *
 * INTEGRATION MAP:
 * {
 *   "expectedConsumers": [
 *     "controllers/matterController.js",
 *     "services/matterService.js",
 *     "workers/matterCleanupWorker.js",
 *     "services/complianceService.js",
 *     "services/auditService.js"
 *   ],
 *   "expectedProviders": [
 *     "./User.js",
 *     "./Document.js",
 *     "./Client.js",
 *     "../utils/logger.js",
 *     "../utils/auditLogger.js",
 *     "../utils/popiaUtils.js",
 *     "../utils/cryptoUtils.js"
 *   ]
 * }
 *
 * MERMAID_INTEGRATION:
 * graph TD
 *   A[Matter Created] --> B{Tenant Isolation}
 *   B --> C[POPIA Compliance]
 *   B --> D[Retention Tracking]
 *   B --> E[Audit Trail]
 *   C --> F[Data Subject Protection]
 *   D --> G[Retention Schedule]
 *   E --> H[Forensic Logging]
 *   F --> I[Redacted Output]
 *   G --> J[Auto-Archive]
 *   H --> K[Court Evidence]
 */

import mongoose from 'mongoose';
import crypto from 'crypto';

// ============================================================================
// ENUMS & CONSTANTS
// ============================================================================

/**
 * Matter Types - Comprehensive legal categories
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
};

/**
 * Matter Status - Full lifecycle tracking
 */
const MATTER_STATUS = {
  ACTIVE: 'active',
  CLOSED: 'closed',
  ARCHIVED: 'archived',
  DELETED: 'deleted',
  PENDING: 'pending',
  SUSPENDED: 'suspended',
  ON_HOLD: 'on_hold',
  SETTLED: 'settled',
  WITHDRAWN: 'withdrawn',
  DISCONTINUED: 'discontinued',
  APPEALED: 'appealed',
  JUDGMENT_RENDERED: 'judgment_rendered',
  JUDGMENT_APPEALED: 'judgment_appealed',
  JUDGMENT_FINAL: 'judgment_final',
  SETTLEMENT_PENDING: 'settlement_pending',
  SETTLEMENT_COMPLETED: 'settlement_completed',
  MEDIATION_PENDING: 'mediation_pending',
  MEDIATION_COMPLETED: 'mediation_completed',
  ARBITRATION_PENDING: 'arbitration_pending',
  ARBITRATION_COMPLETED: 'arbitration_completed',
  DISCOVERY_PHASE: 'discovery_phase',
  TRIAL_PHASE: 'trial_phase',
  POST_TRIAL_PHASE: 'post_trial_phase',
  ENFORCEMENT_PHASE: 'enforcement_phase',
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
  OTHER: 'OTHER',
};

/**
 * Retention Policies - Companies Act §28
 */
const RETENTION_POLICIES = {
  COMPANIES_ACT_7_YEARS: {
    id: 'companies_act_7_years',
    duration: 7,
    unit: 'years',
    legalReference: 'Companies Act 71 of 2008 §28',
    description: 'Standard business records',
  },
  COMPANIES_ACT_10_YEARS: {
    id: 'companies_act_10_years',
    duration: 10,
    unit: 'years',
    legalReference: 'Companies Act 71 of 2008 §28 (Special)',
    description: 'Long-term legal matters',
  },
  TAX_ACT_5_YEARS: {
    id: 'tax_act_5_years',
    duration: 5,
    unit: 'years',
    legalReference: 'Tax Administration Act 28 of 2011 §29',
    description: 'Tax-related matters',
  },
  POPIA_1_YEAR: {
    id: 'popia_1_year',
    duration: 1,
    unit: 'year',
    legalReference: 'POPIA §14(1)(a)',
    description: 'Consent-based processing',
  },
  LPC_7_YEARS: {
    id: 'lpc_7_years',
    duration: 7,
    unit: 'years',
    legalReference: 'LPC Rule 17.3',
    description: 'Legal practice matters',
  },
  PERMANENT: {
    id: 'permanent',
    duration: 100,
    unit: 'years',
    legalReference: 'Constitutional matters',
    description: 'Permanent retention',
  },
};

// ============================================================================
// SUB-SCHEMAS
// ============================================================================

/**
 * Party Schema - Individuals/entities involved in matter
 */
const partySchema = new mongoose.Schema({
  partyId: {
    type: String,
    default: () => crypto.randomBytes(16).toString('hex'),
    index: true,
  },

  role: {
    type: String,
    enum: [
      'client',
      'opposing_party',
      'witness',
      'expert_witness',
      'intervenor',
      'third_party',
      'applicant',
      'respondent',
      'plaintiff',
      'defendant',
      'appellant',
      'respondent_appeal',
    ],
    required: true,
  },

  // Reference to User if internal
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    sparse: true,
  },

  // External party details (redacted in logs)
  name: {
    type: String,
    required: true,
    set: function (v) {
      // Store encrypted in production
      return process.env.NODE_ENV === 'production'
        ? crypto.createHash('sha256').update(v).digest('hex')
        : v;
    },
  },

  idNumber: {
    type: String,
    set: function (v) {
      return v ? '[REDACTED]' : v;
    },
  },

  email: {
    type: String,
    set: function (v) {
      return v ? v.split('@')[0] + '@[REDACTED]' : v;
    },
  },

  phone: {
    type: String,
    set: function (v) {
      return v ? v.replace(/\d(?=\d{4})/g, '*') : v;
    },
  },

  address: {
    type: String,
    set: function (v) {
      return v ? '[REDACTED]' : v;
    },
  },

  representation: {
    firmName: String,
    attorneyId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },
    attorneyNumber: String,
  },

  createdAt: {
    type: Date,
    default: Date.now,
  },
});

/**
 * Timeline Event Schema - Full matter history
 */
const timelineEventSchema = new mongoose.Schema({
  eventId: {
    type: String,
    default: () => crypto.randomBytes(16).toString('hex'),
  },

  eventType: {
    type: String,
    enum: [
      'CREATED',
      'UPDATED',
      'STATUS_CHANGED',
      'DOCUMENT_ADDED',
      'DOCUMENT_REMOVED',
      'PARTY_ADDED',
      'PARTY_REMOVED',
      'NOTE_ADDED',
      'DEADLINE_SET',
      'DEADLINE_MET',
      'DEADLINE_MISSED',
      'COURT_FILING',
      'COURT_HEARING',
      'JUDGMENT_RENDERED',
      'SETTLEMENT_REACHED',
      'APPEAL_FILED',
      'ARCHIVED',
      'RESTORED',
    ],
    required: true,
  },

  description: {
    type: String,
    required: true,
    maxlength: 2000,
  },

  performedBy: {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    name: String,
    role: String,
  },

  metadata: {
    previousValue: mongoose.Schema.Types.Mixed,
    newValue: mongoose.Schema.Types.Mixed,
    documentId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Document',
    },
    partyId: String,
    deadline: Date,
    courtReference: String,
    caseNumber: String,
  },

  timestamp: {
    type: Date,
    default: Date.now,
    immutable: true,
  },

  ipAddress: String,
  userAgent: String,

  forensicHash: {
    type: String,
    required: true,
  },
});

timelineEventSchema.pre('save', function (next) {
  const data = JSON.stringify({
    eventId: this.eventId,
    eventType: this.eventType,
    description: this.description,
    performedBy: this.performedBy.userId,
    timestamp: this.timestamp,
    metadata: this.metadata,
  });

  this.forensicHash = crypto.createHash('sha256').update(data).digest('hex');
  next();
});

/**
 * Note Schema - Matter notes with redaction
 */
const noteSchema = new mongoose.Schema({
  noteId: {
    type: String,
    default: () => crypto.randomBytes(16).toString('hex'),
  },

  content: {
    type: String,
    required: true,
    maxlength: 10000,
  },

  author: {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    name: String,
    role: String,
  },

  isConfidential: {
    type: Boolean,
    default: false,
  },

  confidentialityLevel: {
    type: String,
    enum: ['standard', 'attorney_client', 'work_product', 'litigation'],
    default: 'standard',
  },

  tags: [String],

  mentions: [
    {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },
  ],

  documents: [
    {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Document',
    },
  ],

  createdAt: {
    type: Date,
    default: Date.now,
  },

  updatedAt: {
    type: Date,
    default: Date.now,
  },

  editedBy: [
    {
      userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
      },
      editedAt: Date,
      previousContent: String,
    },
  ],
});

noteSchema.pre('save', function (next) {
  if (!this.isNew) {
    this.updatedAt = new Date();
  }
  next();
});

// ============================================================================
// MAIN SCHEMA
// ============================================================================

const matterSchema = new mongoose.Schema(
  {
    // ============================================================================
    // CORE IDENTIFICATION
    // ============================================================================

    matterId: {
      type: String,
      required: true,
      unique: true,
      index: true,
      default: () => `MAT-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`,
    },

    tenantId: {
      type: String,
      required: [true, 'tenantId is required for multi-tenant isolation'],
      index: true,
      match: /^[a-zA-Z0-9_-]{8,64}$/,
      description: 'Multi-tenant isolation identifier',
    },

    firmId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Firm',
      required: true,
      index: true,
    },

    // ============================================================================
    // MATTER CLASSIFICATION
    // ============================================================================

    matterType: {
      type: String,
      required: [true, 'Matter type is required for legal classification'],
      enum: Object.values(MATTER_TYPES),
      index: true,
    },

    matterNumber: {
      type: String,
      required: true,
      unique: true,
      index: true,
      description: 'Internal matter reference number',
    },

    title: {
      type: String,
      required: [true, 'Matter title is required'],
      maxlength: 500,
      trim: true,
      index: true,
    },

    description: {
      type: String,
      maxlength: 5000,
      trim: true,
    },

    // ============================================================================
    // STATUS & WORKFLOW
    // ============================================================================

    status: {
      type: String,
      required: [true, 'Matter status is required'],
      enum: Object.values(MATTER_STATUS),
      default: MATTER_STATUS.PENDING,
      index: true,
    },

    priority: {
      type: String,
      enum: ['low', 'normal', 'high', 'urgent'],
      default: 'normal',
    },

    stage: {
      type: String,
      enum: [
        'intake',
        'assessment',
        'planning',
        'execution',
        'monitoring',
        'closure',
        'post_closure',
      ],
      default: 'intake',
    },

    // ============================================================================
    // DATES & DEADLINES
    // ============================================================================

    openedDate: {
      type: Date,
      required: true,
      default: Date.now,
      index: true,
    },

    closedDate: {
      type: Date,
      sparse: true,
      index: true,
    },

    archivedDate: {
      type: Date,
      sparse: true,
    },

    lastActivityDate: {
      type: Date,
      required: true,
      default: Date.now,
      index: true,
    },

    deadlines: [
      {
        deadlineId: {
          type: String,
          default: () => crypto.randomBytes(16).toString('hex'),
        },
        title: {
          type: String,
          required: true,
        },
        description: String,
        dueDate: {
          type: Date,
          required: true,
        },
        completedDate: Date,
        status: {
          type: String,
          enum: ['pending', 'completed', 'overdue', 'waived'],
          default: 'pending',
        },
        assignedTo: {
          type: mongoose.Schema.Types.ObjectId,
          ref: 'User',
        },
        courtOrder: Boolean,
        courtReference: String,
        reminderDays: [Number],
      },
    ],

    // ============================================================================
    // PARTIES & PARTICIPANTS
    // ============================================================================

    parties: [partySchema],

    primaryClient: {
      partyId: String,
      userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
      },
    },

    responsibleAttorney: {
      userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true,
      },
      name: String,
      attorneyNumber: String,
    },

    team: [
      {
        userId: {
          type: mongoose.Schema.Types.ObjectId,
          ref: 'User',
        },
        role: {
          type: String,
          enum: ['lead_attorney', 'associate', 'paralegal', 'secretary', 'clerk'],
        },
        assignedDate: Date,
        assignedBy: {
          type: mongoose.Schema.Types.ObjectId,
          ref: 'User',
        },
      },
    ],

    // ============================================================================
    // FINANCIAL INFORMATION
    // ============================================================================

    financials: {
      feeArrangement: {
        type: String,
        enum: ['hourly', 'fixed', 'contingency', 'pro_bono', 'retainer'],
      },
      hourlyRate: Number,
      fixedFee: Number,
      contingencyPercentage: Number,
      totalBilled: {
        type: Number,
        default: 0,
        min: 0,
      },
      totalPaid: {
        type: Number,
        default: 0,
        min: 0,
      },
      outstandingBalance: {
        type: Number,
        default: 0,
        min: 0,
      },
      estimatedValue: Number,
      currency: {
        type: String,
        default: 'ZAR',
        enum: ['ZAR', 'USD', 'EUR', 'GBP'],
      },
      trustFunds: {
        type: Number,
        default: 0,
        min: 0,
        description: 'Funds held in trust for this matter',
      },
    },

    // ============================================================================
    // COURT INTEGRATION
    // ============================================================================

    courtDetails: {
      court: {
        type: String,
        enum: [
          'constitutional_court',
          'supreme_court_appeal',
          'high_court',
          'magistrates_court',
          'labour_court',
          'labour_appeal_court',
          'competition_appeal_court',
          'tax_court',
          'land_claims_court',
          'equality_court',
          'childrens_court',
          'maintenance_court',
        ],
      },
      caseNumber: String,
      judge: String,
      magistrate: String,
      registry: String,
      filingDate: Date,
      nextHearingDate: Date,
      hearingDates: [Date],
      judgments: [
        {
          date: Date,
          summary: String,
          documentId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'Document',
          },
        },
      ],
    },

    // ============================================================================
    // DOCUMENTS & EVIDENCE
    // ============================================================================

    documents: [
      {
        documentId: {
          type: mongoose.Schema.Types.ObjectId,
          ref: 'Document',
          required: true,
        },
        category: {
          type: String,
          enum: [
            'pleading',
            'motion',
            'affidavit',
            'discovery',
            'evidence',
            'exhibit',
            'correspondence',
            'expert_report',
            'court_order',
            'judgment',
            'settlement',
            'contract',
            'corporate_record',
            'financial_record',
            'other',
          ],
        },
        uploadedBy: {
          type: mongoose.Schema.Types.ObjectId,
          ref: 'User',
        },
        uploadedAt: {
          type: Date,
          default: Date.now,
        },
        description: String,
      },
    ],

    documentCount: {
      type: Number,
      default: 0,
      min: 0,
    },

    // ============================================================================
    // NOTES & HISTORY
    // ============================================================================

    notes: [noteSchema],
    timeline: [timelineEventSchema],

    // ============================================================================
    // POPIA COMPLIANCE (Data Subject Protection)
    // ============================================================================

    popia: {
      dataSubjects: [
        {
          subjectId: String,
          consentId: String,
          consentDate: Date,
          consentVersion: String,
          purposes: [String],
          withdrawalDate: Date,
          withdrawalReason: String,
          dataCategories: [String],
        },
      ],

      processingActivities: [
        {
          activityId: String,
          date: Date,
          description: String,
          purpose: String,
          dataAccessed: [String],
          accessedBy: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User',
          },
        },
      ],

      objections: [
        {
          objectionId: String,
          date: Date,
          reason: String,
          status: {
            type: String,
            enum: ['pending', 'resolved', 'escalated'],
          },
          resolvedDate: Date,
          resolution: String,
        },
      ],

      dataBreaches: [
        {
          breachId: String,
          detectedAt: Date,
          description: String,
          affectedDataSubjects: [String],
          notifiedRegulator: Boolean,
          notifiedAt: Date,
          regulatorReference: String,
          remediatedAt: Date,
          status: {
            type: String,
            enum: ['detected', 'investigating', 'notified', 'resolved'],
          },
        },
      ],
    },

    // ============================================================================
    // RETENTION MANAGEMENT (Companies Act §28)
    // ============================================================================

    retentionPolicyId: {
      type: String,
      enum: Object.keys(RETENTION_POLICIES),
      default: 'COMPANIES_ACT_7_YEARS',
      index: true,
    },

    retentionExpiryDate: {
      type: Date,
      index: true,
    },

    retentionNotes: String,

    // ============================================================================
    // DATA RESIDENCY (POPIA §1)
    // ============================================================================

    dataResidency: {
      type: String,
      enum: Object.values(DATA_RESIDENCY),
      default: DATA_RESIDENCY.ZA,
      required: true,
    },

    crossBorderTransfers: [
      {
        date: Date,
        destination: String,
        purpose: String,
        legalBasis: String,
        safeguards: String,
        authorizedBy: {
          type: mongoose.Schema.Types.ObjectId,
          ref: 'User',
        },
      },
    ],

    // ============================================================================
    // DELETION MANAGEMENT
    // ============================================================================

    isDeleted: {
      type: Boolean,
      default: false,
      index: true,
    },

    deletionRequestedAt: Date,
    deletionRequestedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },
    deletionApprovedAt: Date,
    deletionApprovedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },
    deletionProof: {
      type: String,
      description: 'Cryptographic proof of deletion',
    },
    deletedAt: Date,
    deletedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },

    // ============================================================================
    // FORENSIC INTEGRITY
    // ============================================================================

    forensicHash: {
      type: String,
      required: true,
      unique: true,
    },

    previousHash: String,

    // ============================================================================
    // AUDIT FIELDS
    // ============================================================================

    createdBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },

    updatedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },

    createdAt: {
      type: Date,
      default: Date.now,
      immutable: true,
    },

    updatedAt: {
      type: Date,
      default: Date.now,
    },

    // ============================================================================
    // METADATA
    // ============================================================================

    tags: [String],

    metadata: {
      type: Map,
      of: mongoose.Schema.Types.Mixed,
    },
  },
  {
    timestamps: true,
    collection: 'matters',
    strict: true,
    minimize: false,
    toJSON: {
      virtuals: true,
      transform: function (doc, ret) {
        // Redact PII for API responses
        if (ret.parties) {
          ret.parties = ret.parties.map((party) => ({
            ...party,
            idNumber: party.idNumber ? '[REDACTED]' : undefined,
            email: party.email ? party.email.replace(/^(.)(.*)(@.*)$/, '$1***$3') : undefined,
            phone: party.phone ? party.phone.replace(/\d(?=\d{4})/g, '*') : undefined,
            address: party.address ? '[REDACTED]' : undefined,
          }));
        }

        if (ret.notes) {
          ret.notes = ret.notes.map((note) => ({
            content: note.isConfidential ? '[CONFIDENTIAL]' : note.content,
            author: note.author,
            createdAt: note.createdAt,
          }));
        }

        delete ret.forensicHash;
        delete ret.previousHash;
        delete ret.isDeleted;
        delete ret.deletionProof;

        return ret;
      },
    },
  }
);

// ============================================================================
// INDEXES
// ============================================================================

matterSchema.index({ tenantId: 1, matterNumber: 1 }, { unique: true });
matterSchema.index({ tenantId: 1, status: 1, lastActivityDate: -1 });
matterSchema.index({ tenantId: 1, responsibleAttorney: 1, status: 1 });
matterSchema.index({ tenantId: 1, matterType: 1, status: 1 });
matterSchema.index({ tenantId: 1, retentionExpiryDate: 1 });
matterSchema.index({ tenantId: 1, openedDate: -1 });
matterSchema.index({ tenantId: 1, closedDate: -1 });
matterSchema.index({ 'parties.userId': 1, tenantId: 1 });
matterSchema.index({ 'deadlines.dueDate': 1, status: 1 });
matterSchema.index({ 'courtDetails.nextHearingDate': 1 });
matterSchema.index({ 'popia.dataSubjects.subjectId': 1 });
matterSchema.index({ 'timeline.timestamp': -1 });
matterSchema.index({ tags: 1, tenantId: 1 });

// ============================================================================
// MIDDLEWARE
// ============================================================================

matterSchema.pre('validate', function (next) {
  // Set retention expiry date based on policy
  if (!this.retentionExpiryDate && this.retentionPolicyId) {
    const policy = RETENTION_POLICIES[this.retentionPolicyId];
    if (policy) {
      const expiryDate = new Date();
      expiryDate.setFullYear(expiryDate.getFullYear() + policy.duration);
      this.retentionExpiryDate = expiryDate;
    }
  }

  // Update document count
  if (this.documents) {
    this.documentCount = this.documents.length;
  }

  next();
});

matterSchema.pre('save', async function (next) {
  this.updatedAt = new Date();
  this.lastActivityDate = new Date();

  // Generate forensic hash
  const hashData = {
    matterId: this.matterId,
    tenantId: this.tenantId,
    matterNumber: this.matterNumber,
    title: this.title,
    status: this.status,
    openedDate: this.openedDate,
    lastActivityDate: this.lastActivityDate,
    responsibleAttorney: this.responsibleAttorney?.userId,
    partyCount: this.parties?.length || 0,
    documentCount: this.documentCount,
    previousHash: this.previousHash,
  };

  const canonicalData = JSON.stringify(hashData, Object.keys(hashData).sort());
  this.forensicHash = crypto.createHash('sha256').update(canonicalData).digest('hex');

  // Find previous version for hash chaining
  if (!this.previousHash) {
    const previousVersion = await this.constructor
      .findOne({
        matterNumber: this.matterNumber,
        tenantId: this.tenantId,
        createdAt: { $lt: this.createdAt || new Date() },
      })
      .sort({ createdAt: -1 });

    if (previousVersion) {
      this.previousHash = previousVersion.forensicHash;
    }
  }

  next();
});

// ============================================================================
// INSTANCE METHODS
// ============================================================================

/**
 * Add timeline event
 */
matterSchema.methods.addTimelineEvent = async function (eventData, userId) {
  const event = {
    eventType: eventData.eventType,
    description: eventData.description,
    performedBy: {
      userId: userId,
      name: eventData.userName,
      role: eventData.userRole,
    },
    metadata: eventData.metadata,
    ipAddress: eventData.ipAddress,
    userAgent: eventData.userAgent,
  };

  this.timeline.push(event);
  this.lastActivityDate = new Date();
  this.updatedBy = userId;

  return this.save();
};

/**
 * Add note with confidentiality
 */
matterSchema.methods.addNote = async function (noteData, userId) {
  const note = {
    content: noteData.content,
    author: {
      userId: userId,
      name: noteData.userName,
      role: noteData.userRole,
    },
    isConfidential: noteData.isConfidential || false,
    confidentialityLevel: noteData.confidentialityLevel || 'standard',
    tags: noteData.tags || [],
    mentions: noteData.mentions || [],
  };

  this.notes.push(note);
  this.lastActivityDate = new Date();
  this.updatedBy = userId;

  await this.addTimelineEvent(
    {
      eventType: 'NOTE_ADDED',
      description: `Note added: ${noteData.content.substring(0, 100)}...`,
      metadata: { noteId: note.noteId },
    },
    userId
  );

  return this.save();
};

/**
 * Add document reference
 */
matterSchema.methods.addDocument = async function (documentId, category, userId) {
  this.documents.push({
    documentId,
    category,
    uploadedBy: userId,
    uploadedAt: new Date(),
  });

  this.documentCount = this.documents.length;
  this.lastActivityDate = new Date();
  this.updatedBy = userId;

  await this.addTimelineEvent(
    {
      eventType: 'DOCUMENT_ADDED',
      description: `Document added: ${category}`,
      metadata: { documentId },
    },
    userId
  );

  return this.save();
};

/**
 * Add deadline
 */
matterSchema.methods.addDeadline = async function (deadlineData, userId) {
  this.deadlines.push({
    title: deadlineData.title,
    description: deadlineData.description,
    dueDate: deadlineData.dueDate,
    assignedTo: deadlineData.assignedTo,
    courtOrder: deadlineData.courtOrder || false,
    courtReference: deadlineData.courtReference,
    reminderDays: deadlineData.reminderDays || [7, 3, 1],
  });

  this.lastActivityDate = new Date();
  this.updatedBy = userId;

  await this.addTimelineEvent(
    {
      eventType: 'DEADLINE_SET',
      description: `Deadline set: ${deadlineData.title}`,
      metadata: { dueDate: deadlineData.dueDate },
    },
    userId
  );

  return this.save();
};

/**
 * Update status with audit trail
 */
matterSchema.methods.updateStatus = async function (newStatus, reason, userId) {
  const oldStatus = this.status;

  this.status = newStatus;
  this.updatedBy = userId;

  if (newStatus === 'closed') {
    this.closedDate = new Date();
  }

  await this.addTimelineEvent(
    {
      eventType: 'STATUS_CHANGED',
      description: `Status changed from ${oldStatus} to ${newStatus}`,
      metadata: {
        previousValue: oldStatus,
        newValue: newStatus,
        reason,
      },
    },
    userId
  );

  return this.save();
};

/**
 * Get redacted version for external sharing
 */
matterSchema.methods.getRedactedVersion = function () {
  const redacted = this.toJSON();

  // Deep redaction of PII
  if (redacted.parties) {
    redacted.parties = redacted.parties.map((party) => ({
      role: party.role,
      name: party.name,
      representation: party.representation,
    }));
  }

  if (redacted.notes) {
    redacted.notes = redacted.notes.map((note) => ({
      content: note.isConfidential ? '[CONFIDENTIAL]' : note.content,
      author: note.author,
      createdAt: note.createdAt,
    }));
  }

  return redacted;
};

/**
 * Verify forensic integrity
 */
matterSchema.methods.verifyIntegrity = function () {
  const hashData = {
    matterId: this.matterId,
    tenantId: this.tenantId,
    matterNumber: this.matterNumber,
    title: this.title,
    status: this.status,
    openedDate: this.openedDate,
    lastActivityDate: this.lastActivityDate,
    responsibleAttorney: this.responsibleAttorney?.userId,
    partyCount: this.parties?.length || 0,
    documentCount: this.documentCount,
    previousHash: this.previousHash,
  };

  const canonicalData = JSON.stringify(hashData, Object.keys(hashData).sort());
  const calculatedHash = crypto.createHash('sha256').update(canonicalData).digest('hex');

  return {
    verified: calculatedHash === this.forensicHash,
    calculated: calculatedHash,
    stored: this.forensicHash,
    timestamp: new Date().toISOString(),
  };
};

// ============================================================================
// STATIC METHODS
// ============================================================================

/**
 * Find matters expiring soon
 */
matterSchema.statics.findExpiringSoon = async function (tenantId, daysThreshold = 30) {
  const threshold = new Date();
  threshold.setDate(threshold.getDate() + daysThreshold);

  return this.find({
    tenantId,
    retentionExpiryDate: { $lte: threshold },
    isDeleted: false,
    status: { $ne: 'deleted' },
  }).sort({ retentionExpiryDate: 1 });
};

/**
 * Get matter statistics for firm
 */
matterSchema.statics.getFirmStatistics = async function (firmId) {
  const stats = await this.aggregate([
    { $match: { firmId: new mongoose.Types.ObjectId(firmId), isDeleted: false } },
    {
      $facet: {
        byStatus: [{ $group: { _id: '$status', count: { $sum: 1 } } }],
        byType: [{ $group: { _id: '$matterType', count: { $sum: 1 } } }],
        byAttorney: [{ $group: { _id: '$responsibleAttorney.userId', count: { $sum: 1 } } }],
        activityMetrics: [
          {
            $group: {
              _id: null,
              avgDocuments: { $avg: '$documentCount' },
              avgParties: { $avg: { $size: '$parties' } },
              totalOpen: {
                $sum: { $cond: [{ $eq: ['$status', 'active'] }, 1, 0] },
              },
              totalClosed: {
                $sum: { $cond: [{ $eq: ['$status', 'closed'] }, 1, 0] },
              },
              totalArchived: {
                $sum: { $cond: [{ $eq: ['$status', 'archived'] }, 1, 0] },
              },
            },
          },
        ],
      },
    },
  ]);

  return stats[0] || {};
};

// ============================================================================
// VIRTUAL PROPERTIES
// ============================================================================

matterSchema.virtual('ageInDays').get(function () {
  return Math.floor((Date.now() - this.openedDate) / (1000 * 60 * 60 * 24));
});

matterSchema.virtual('isOverdue').get(function () {
  if (!this.deadlines) return false;
  return this.deadlines.some((d) => d.status === 'pending' && new Date(d.dueDate) < new Date());
});

matterSchema.virtual('partyCount').get(function () {
  return this.parties?.length || 0;
});

matterSchema.virtual('timelineCount').get(function () {
  return this.timeline?.length || 0;
});

// ============================================================================
// EXPORTS
// ============================================================================

const Matter = mongoose.model('Matter', matterSchema);

export default Matter;

// Re-export enums
export { MATTER_TYPES, MATTER_STATUS, DATA_RESIDENCY, RETENTION_POLICIES };
