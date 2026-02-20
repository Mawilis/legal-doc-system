/*╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██████╗ ███╗   ██╗███████╗██╗     ███████╗██╗████████╗            ║
║  ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║     ██╔════╝██║╚══██╔══╝            ║
║  ██║     ██║   ██║██╔██╗ ██║█████╗  ██║     █████╗  ██║   ██║               ║
║  ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║     ██╔══╝  ██║   ██║               ║
║  ╚██████╗╚██████╔╝██║ ╚████║██║     ███████╗██║     ██║   ██║               ║
║   ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚══════╝╚═╝     ╚═╝   ╚═╝               ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  FILE: /Users/wilsonkhanyezi/legal-doc-system/server/models/Case.js         ║
║  VERSION: 6.0.0 (production - COMPLETE PAIA SCHEMA)                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

'use strict';

const mongoose = require('mongoose');
const crypto = require('crypto');

const getObjectId = () => {
  if (mongoose.Schema && mongoose.Schema.Types && mongoose.Schema.Types.ObjectId) {
    return mongoose.Schema.Types.ObjectId;
  }
  if (mongoose.Types && mongoose.Types.ObjectId) {
    return mongoose.Types.ObjectId;
  }
  return String;
};

// ==============================================
// CONSTANTS
// ==============================================
const CASE_STATUSES = {
  PRE_INTAKE: 'PRE_INTAKE',
  ACTIVE: 'ACTIVE',
  LEGAL_HOLD: 'LEGAL_HOLD',
  CLOSED: 'CLOSED'
};

const CONFLICT_SEVERITIES = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low'
};

const PAIA_REQUEST_STATUSES = {
  PENDING: 'PENDING',
  IN_REVIEW: 'IN_REVIEW',
  PARTIALLY_GRANTED: 'PARTIALLY_GRANTED',
  GRANTED: 'GRANTED',
  DENIED: 'DENIED',
  APPEALED: 'APPEALED',
  WITHDRAWN: 'WITHDRAWN'
};

const RESOLVED_STATUS = 'resolved';

// ==============================================
// VALIDATORS
// ==============================================
const validateCaseNumber = (value) => {
  if (!value) return false;
  const caseNumberRegex = /^[A-Z]{2,4}-\d{4}-\d{4}(-[A-Z]{2})?$/;
  return caseNumberRegex.test(value);
};

const validateTenantId = (value) => {
  if (!value) return false;
  return /^tenant_[a-zA-Z0-9_]{8,32}$/.test(value);
};

// ==============================================
// PAIA REQUEST SUB-SCHEMA - COMPLETE DEFINITION
// ==============================================
const PaiaRequestSchema = new mongoose.Schema({
  requestId: {
    type: String,
    required: [true, 'PAIA request ID is required'],
    unique: true,
    index: true
  },
  requesterType: {
    type: String,
    enum: ['INDIVIDUAL', 'COMPANY', 'GOVERNMENT', 'LAW_FIRM'],
    required: true
  },
  requesterDetails: {
    name: { type: String, required: true, trim: true },
    idNumber: String,
    contactEmail: { type: String, lowercase: true },
    contactPhone: String,
    postalAddress: String
  },
  requestedInformation: [{
    description: { type: String, required: true },
    documentType: String,
    dateRange: {
      from: Date,
      to: Date
    },
    specificReference: String
  }],
  requestDate: { type: Date, default: Date.now },
  statutoryDeadline: {
    type: Date,
    required: true,
    validate: {
      validator: function (value) {
        return value > new Date();
      },
      message: 'Statutory deadline must be in the future'
    }
  },
  status: {
    type: String,
    enum: Object.values(PAIA_REQUEST_STATUSES),
    default: PAIA_REQUEST_STATUSES.PENDING,
    index: true
  },
  decisionNotes: String,
  reviewDetails: {
    reviewedBy: { type: getObjectId(), ref: 'User' },
    reviewedAt: Date,
    decisionNotes: String,
    exemptionsApplied: [{
      section: String,
      reason: String,
      partialRelease: Boolean
    }]
  },
  responseDetails: {
    respondedAt: Date,
    responseMethod: {
      type: String,
      enum: ['EMAIL', 'POST', 'IN_PERSON', 'PORTAL']
    },
    feesCharged: Number,
    documentsReleased: [{
      documentId: { type: getObjectId(), ref: 'Document' },
      releaseMethod: String,
      releasedAt: Date
    }]
  },
  appealDetails: {
    appealedAt: Date,
    appealGrounds: String,
    appealDecision: String,
    appealDecidedAt: Date
  },
  metadata: {
    isUrgent: { type: Boolean, default: false },
    urgencyReason: String,
    relatedDsarId: String,
    retentionOverride: Boolean,
    manualTrackingRequired: { type: Boolean, default: false }
  },
  audit: {
    createdBy: { type: getObjectId(), ref: 'User', required: true },
    createdAt: { type: Date, default: Date.now },
    updatedBy: { type: getObjectId(), ref: 'User' },
    updatedAt: { type: Date, default: Date.now }
  }
}, { _id: true });

// ==============================================
// MAIN SCHEMA
// ==============================================
const CaseSchema = new mongoose.Schema({
  tenantId: {
    type: String,
    required: [true, 'Tenant ID is required for multi-tenant isolation'],
    index: true,
    validate: {
      validator: validateTenantId,
      message: 'Tenant ID must match pattern: tenant_[8-32 alphanumeric chars]'
    }
  },
  caseNumber: {
    type: String,
    required: [true, 'Case number is required'],
    unique: true,
    index: true,
    validate: {
      validator: validateCaseNumber,
      message: 'Case number must match format: XX-YYYY-ZZZZ or XX-YYYY-ZZZZ-XX'
    }
  },
  title: {
    type: String,
    required: [true, 'Case title is required'],
    trim: true,
    minlength: [3, 'Case title must be at least 3 characters'],
    maxlength: [200, 'Case title cannot exceed 200 characters']
  },
  status: {
    type: String,
    enum: Object.values(CASE_STATUSES),
    default: CASE_STATUSES.PRE_INTAKE,
    index: true
  },
  client: {
    name: {
      type: String,
      required: [true, 'Client name is required'],
      trim: true
    },
    entityId: String,
    clientReference: String,
    contactDetails: {
      email: {
        type: String,
        lowercase: true,
        match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please provide a valid email address']
      },
      phone: String
    },
    paiaDesignation: {
      isInformationOfficer: { type: Boolean, default: false },
      deputyOfficers: [{ type: getObjectId(), ref: 'User' }],
      lastDesignationUpdate: Date
    }
  },
  opponents: [{
    name: {
      type: String,
      required: [true, 'Opponent name is required'],
      trim: true
    },
    blindIndex: {
      type: String,
      index: true,
      required: [true, 'Blind index is required for searchable encryption']
    },
    role: {
      type: String,
      enum: ['ADVERSE_PARTY', 'THIRD_PARTY', 'WITNESS', 'EXPERT'],
      default: 'ADVERSE_PARTY'
    },
    entityId: String,
    paiaRelevant: { type: Boolean, default: false },
    paiaConsentObtained: Boolean,
    consentRecordId: String
  }],
  legalTeam: [{
    userId: { type: getObjectId(), ref: 'User', required: true },
    role: {
      type: String,
      enum: ['LEAD_ATTORNEY', 'ASSOCIATE', 'PARALEGAL', 'SUPPORT_STAFF', 'INFORMATION_OFFICER'],
      required: true
    },
    assignedDate: { type: Date, default: Date.now },
    isActive: { type: Boolean, default: true },
    paiaResponsibilities: [{
      type: String,
      enum: ['REQUEST_PROCESSING', 'APPEAL_HANDLING', 'EXEMPTION_REVIEW', 'DISCLOSURE_AUTHORITY']
    }]
  }],
  matterDetails: {
    jurisdiction: String,
    courtOrTribunal: String,
    matterType: {
      type: String,
      enum: ['LITIGATION', 'TRANSACTIONAL', 'ADVISORY', 'REGULATORY', 'COMPLIANCE']
    },
    description: String,
    openingDate: { type: Date, default: Date.now },
    estimatedCloseDate: Date,
    actualCloseDate: Date,
    valueAtRisk: Number,
    currency: { type: String, default: 'ZAR' },
    paiaClassification: {
      type: String,
      enum: ['ROUTINE_DISCLOSURE', 'CONDITIONAL_DISCLOSURE', 'PROTECTED_DISCLOSURE'],
      default: 'ROUTINE_DISCLOSURE'
    }
  },
  paiaRequests: [PaiaRequestSchema],
  paiaTracking: {
    totalRequests: { type: Number, default: 0 },
    pendingRequests: { type: Number, default: 0 },
    avgResponseTimeDays: Number,
    lastRequestDate: Date,
    exemptionUsage: {
      section14: { type: Number, default: 0 },
      section34: { type: Number, default: 0 },
      section37: { type: Number, default: 0 },
      other: { type: Number, default: 0 }
    },
    appealRate: Number,
    complianceScore: Number
  },
  conflictStatus: {
    checked: { type: Boolean, default: false, index: true },
    checkInitiatedAt: Date,
    clearanceDate: Date,
    clearedBy: { type: getObjectId(), ref: 'User' },
    clearanceMethod: {
      type: String,
      enum: ['AUTOMATED', 'MANUAL_REVIEW', 'OVERRIDE', 'WAIVER']
    },
    clearanceNotes: String,
    foundConflicts: [{
      type: getObjectId(),
      ref: 'Conflict',
      index: true
    }],
    screeningHash: String
  },
  compliance: {
    popiaConsentObtained: { type: Boolean, default: false },
    consentRecordId: String,
    lpcRule7Compliant: { type: Boolean, default: false },
    paiaManualUrl: String,
    riskLevel: {
      type: String,
      enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
      default: 'MEDIUM'
    },
    ectCompliant: { type: Boolean, default: false },
    signatureVerification: {
      method: String,
      verifiedAt: Date,
      verificationId: String
    },
    ficaVerified: Boolean,
    trustAccountRequired: { type: Boolean, default: false },
    trustAccountId: String
  },
  audit: {
    createdBy: { type: getObjectId(), ref: 'User', required: true },
    createdAt: { type: Date, default: Date.now },
    updatedBy: { type: getObjectId(), ref: 'User' },
    updatedAt: { type: Date, default: Date.now },
    version: { type: Number, default: 1 },
    paiaNotifications: [{
      type: String,
      enum: ['REQUEST_RECEIVED', 'DEADLINE_WARNING', 'RESPONSE_SENT', 'APPEAL_FILED']
    }]
  },
  metadata: {
    isConfidential: { type: Boolean, default: true },
    classification: {
      type: String,
      enum: ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED', 'PAIA_PROTECTED'],
      default: 'CONFIDENTIAL'
    },
    tags: [String],
    retentionPolicy: {
      rule: {
        type: String,
        enum: ['LPC_6YR', 'COMPANIES_ACT_7YR', 'PAIA_5YR', 'PERMANENT'],
        default: 'LPC_6YR'
      },
      disposalDate: Date,
      paiaOverride: Boolean
    },
    storageLocation: {
      dataResidencyCompliance: {
        type: String,
        enum: ['ZA_ONLY', 'EU_ADEQUATE', 'GLOBAL'],
        default: 'ZA_ONLY'
      },
      primaryRegion: { type: String, default: 'af-south-1' },
      backupRegion: String
    }
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// ==============================================
// VIRTUAL PROPERTIES
// ==============================================
CaseSchema.virtual('isConflictFree').get(function () {
  return this.conflictStatus.checked &&
    (!this.conflictStatus.foundConflicts || this.conflictStatus.foundConflicts.length === 0);
});

CaseSchema.virtual('requiresManualConflictReview').get(function () {
  return this.conflictStatus.checked &&
    this.conflictStatus.foundConflicts &&
    this.conflictStatus.foundConflicts.length > 0 &&
    !this.conflictStatus.clearanceDate;
});

CaseSchema.virtual('daysOpen').get(function () {
  if (!this.matterDetails.openingDate) return 0;
  const diff = new Date() - this.matterDetails.openingDate;
  return Math.floor(diff / (1000 * 60 * 60 * 24));
});

CaseSchema.virtual('paiaDeadlineApproaching').get(function () {
  if (!this.paiaRequests || this.paiaRequests.length === 0) return false;
  const pendingRequests = this.paiaRequests.filter(req =>
    req.status === PAIA_REQUEST_STATUSES.PENDING || req.status === PAIA_REQUEST_STATUSES.IN_REVIEW
  );
  if (pendingRequests.length === 0) return false;
  const now = new Date();
  const threeDaysFromNow = new Date(now.getTime() + (3 * 24 * 60 * 60 * 1000));
  return pendingRequests.some(req => req.statutoryDeadline && req.statutoryDeadline <= threeDaysFromNow);
});

CaseSchema.virtual('hasActivePaiaRequests').get(function () {
  if (!this.paiaRequests || this.paiaRequests.length === 0) return false;
  const activeStatuses = [PAIA_REQUEST_STATUSES.PENDING, PAIA_REQUEST_STATUSES.IN_REVIEW, PAIA_REQUEST_STATUSES.APPEALED];
  return this.paiaRequests.some(req => activeStatuses.includes(req.status));
});

// ==============================================
// INDEXES
// ==============================================
CaseSchema.index({ tenantId: 1, status: 1 });
CaseSchema.index({ tenantId: 1, 'client.name': 1 });
CaseSchema.index({ tenantId: 1, 'conflictStatus.checked': 1 });
CaseSchema.index({ 'conflictStatus.clearanceDate': 1 });
CaseSchema.index({ 'audit.createdAt': -1 });
CaseSchema.index({ 'paiaRequests.status': 1 });
CaseSchema.index({ 'paiaRequests.statutoryDeadline': 1 });

// ==============================================
// STATIC METHODS
// ==============================================
CaseSchema.statics.findByTenant = async function (tenantId, options = {}) {
  if (!tenantId) throw new Error('Tenant ID is required');

  const query = { tenantId };
  const page = parseInt(options.page, 10) || 1;
  const limit = parseInt(options.limit, 10) || 50;
  const skip = (page - 1) * limit;

  if (options.status) query.status = options.status;
  if (options.conflictChecked !== undefined) {
    query['conflictStatus.checked'] = options.conflictChecked;
  }
  if (options.hasPaiaRequests !== undefined) {
    if (options.hasPaiaRequests) {
      query['paiaRequests.0'] = { $exists: true };
    } else {
      query.paiaRequests = { $size: 0 };
    }
  }
  if (options.search) {
    query.$or = [
      { caseNumber: new RegExp(options.search, 'i') },
      { title: new RegExp(options.search, 'i') },
      { 'client.name': new RegExp(options.search, 'i') }
    ];
  }

  return this.find(query)
    .sort({ 'audit.createdAt': -1 })
    .skip(skip)
    .limit(limit)
    .populate('conflictStatus.foundConflicts', 'conflictReference severity status')
    .populate('legalTeam.userId', 'name email role')
    .populate('paiaRequests.reviewDetails.reviewedBy', 'name email');
};

CaseSchema.statics.addPaiaRequest = async function (caseId, paiaRequestData) {
  const caseDoc = await this.findById(caseId);
  if (!caseDoc) throw new Error('Case not found');

  caseDoc.paiaRequests.push(paiaRequestData);
  if (!caseDoc.paiaTracking) caseDoc.paiaTracking = {};
  caseDoc.paiaTracking.totalRequests = (caseDoc.paiaTracking.totalRequests || 0) + 1;
  caseDoc.paiaTracking.pendingRequests = (caseDoc.paiaTracking.pendingRequests || 0) + 1;
  caseDoc.paiaTracking.lastRequestDate = new Date();

  await caseDoc.save();
  return { success: true, caseId, requestId: paiaRequestData.requestId };
};

// ==============================================
// SINGLETON EXPORT
// ==============================================
const Case = mongoose.models.Case || mongoose.model('Case', CaseSchema);

Case.CASE_STATUSES = CASE_STATUSES;
Case.CONFLICT_SEVERITIES = CONFLICT_SEVERITIES;
Case.PAIA_REQUEST_STATUSES = PAIA_REQUEST_STATUSES;

module.exports = Case;
