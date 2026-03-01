#!/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CASE MODEL                                                      ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'crypto';

// Export constants used by tests
export const CASE_STATUSES = {
  PRE_INTAKE: 'PRE_INTAKE',
  ACTIVE: 'ACTIVE',
  PENDING: 'PENDING',
  CLOSED: 'CLOSED',
  ARCHIVED: 'ARCHIVED',
};

export const COURT_TIERS = {
  LOWER: 'LOWER',
  SUPERIOR: 'SUPERIOR',
  APPELLATE: 'APPELLATE',
  SUPREME: 'SUPREME',
};

export const COURT_CATEGORIES = {
  SMALL_CLAIMS: 'SMALL_CLAIMS',
  DISTRICT_MAGISTRATE: 'DISTRICT_MAGISTRATE',
  REGIONAL_MAGISTRATE: 'REGIONAL_MAGISTRATE',
  HIGH_COURT: 'HIGH_COURT',
  SUPREME_COURT_APPEAL: 'SUPREME_COURT_APPEAL',
  CONSTITUTIONAL_COURT: 'CONSTITUTIONAL_COURT',
  LABOUR_COURT: 'LABOUR_COURT',
  LABOUR_APPEAL_COURT: 'LABOUR_APPEAL_COURT',
  LAND_CLAIMS_COURT: 'LAND_CLAIMS_COURT',
};

export const COURT_JURISDICTION = {
  [COURT_CATEGORIES.SMALL_CLAIMS]: {
    name: 'Small Claims Court',
    civilLimit: 20000,
    presidingOfficer: 'Commissioner',
  },
  [COURT_CATEGORIES.DISTRICT_MAGISTRATE]: {
    name: 'District Magistrate Court',
    civilLimit: 200000,
    criminalLimit: 'All except serious',
    presidingOfficer: 'Magistrate',
  },
  [COURT_CATEGORIES.REGIONAL_MAGISTRATE]: {
    name: 'Regional Magistrate Court',
    civilLimit: 400000,
    criminalLimit: 'All except treason',
    presidingOfficer: 'Regional Magistrate',
  },
  [COURT_CATEGORIES.HIGH_COURT]: {
    name: 'High Court',
    civilLimit: null,
    criminalLimit: 'All offences',
    presidingOfficer: 'Judge',
  },
  [COURT_CATEGORIES.SUPREME_COURT_APPEAL]: {
    name: 'Supreme Court of Appeal',
    appellateLevel: true,
    quorum: 5,
    presidingOfficer: 'Justice of Appeal',
  },
  [COURT_CATEGORIES.CONSTITUTIONAL_COURT]: {
    name: 'Constitutional Court',
    appellateLevel: true,
    quorum: 8,
    presidingOfficer: 'Chief Justice',
    appealTo: null,
  },
};

export const PARTY_ROLES = {
  APPLICANT: 'APPLICANT',
  RESPONDENT: 'RESPONDENT',
  PLAINTIFF: 'PLAINTIFF',
  DEFENDANT: 'DEFENDANT',
  ACCUSED: 'ACCUSED',
  CHILD: 'CHILD',
};

export const PAIA_REQUEST_STATUSES = {
  PENDING: 'PENDING',
  IN_REVIEW: 'IN_REVIEW',
  GRANTED: 'GRANTED',
  DENIED: 'DENIED',
  APPEALED: 'APPEALED',
};

const caseSchema = new mongoose.Schema(
  {
    tenantId: {
      type: String,
      required: true,
      index: true,
      validate: {
        validator: function (v) {
          // Accept both formats: tenant_test_12345678 and tenant_[8-32 chars]
          return /^tenant_[a-zA-Z0-9]{8,32}$/.test(v) || /^test-tenant-[a-zA-Z0-9]{8,64}$/.test(v);
        },
        message:
          'Tenant ID must match pattern: tenant_[8-32 alphanumeric chars] or test-tenant-[8-64 chars]',
      },
    },
    caseNumber: {
      type: String,
      required: true,
      unique: true,
    },
    title: {
      type: String,
      required: true,
    },
    court: {
      type: String,
      required: true,
      enum: Object.values(COURT_CATEGORIES),
    },
    client: {
      name: String,
      reference: String,
    },
    status: {
      type: String,
      enum: Object.values(CASE_STATUSES),
      default: CASE_STATUSES.PRE_INTAKE,
    },
    paiaRequests: [
      {
        requestId: String,
        requesterType: String,
        requesterDetails: Object,
        requestedInformation: Array,
        statutoryDeadline: Date,
        status: {
          type: String,
          enum: Object.values(PAIA_REQUEST_STATUSES),
          default: PAIA_REQUEST_STATUSES.PENDING,
        },
        responseDetails: {
          respondedAt: Date,
          responseMethod: String,
          documents: Array,
        },
        audit: {
          createdBy: String,
          createdAt: Date,
        },
      },
    ],
    paiaTracking: {
      totalRequests: { type: Number, default: 0 },
      pendingRequests: { type: Number, default: 0 },
      completedRequests: { type: Number, default: 0 },
      overdueRequests: { type: Number, default: 0 },
    },
    matterDetails: {
      openingDate: Date,
      closingDate: Date,
      description: String,
      value: Number,
      riskLevel: {
        type: String,
        enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
      },
    },
    conflictStatus: {
      checked: { type: Boolean, default: false },
      clearedBy: String,
      clearanceDate: Date,
      foundConflicts: [mongoose.Schema.Types.ObjectId],
      notes: String,
    },
    audit: {
      createdBy: String,
      updatedBy: String,
    },
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
  }
);

// Virtual for court info
caseSchema.virtual('courtInfo').get(function () {
  return COURT_JURISDICTION[this.court] || null;
});

// Virtual for days open
caseSchema.virtual('daysOpen').get(function () {
  if (!this.matterDetails?.openingDate) return 0;
  const start = new Date(this.matterDetails.openingDate);
  const now = new Date();
  return Math.floor((now - start) / (1000 * 60 * 60 * 24));
});

// Virtual for PAIA deadline approaching
caseSchema.virtual('paiaDeadlineApproaching').get(function () {
  if (!this.paiaRequests?.length) return false;
  const now = new Date();
  const threeDaysFromNow = new Date(now.setDate(now.getDate() + 3));
  return this.paiaRequests.some(
    (req) =>
      req.statutoryDeadline &&
      req.statutoryDeadline <= threeDaysFromNow &&
      req.status === PAIA_REQUEST_STATUSES.PENDING
  );
});

// Virtual for has active PAIA requests
caseSchema.virtual('hasActivePaiaRequests').get(function () {
  return (
    this.paiaRequests?.some((req) =>
      [PAIA_REQUEST_STATUSES.PENDING, PAIA_REQUEST_STATUSES.IN_REVIEW].includes(req.status)
    ) || false
  );
});

// Virtual for conflict free
caseSchema.virtual('isConflictFree').get(function () {
  return (
    this.conflictStatus?.checked &&
    (!this.conflictStatus?.foundConflicts || this.conflictStatus.foundConflicts.length === 0)
  );
});

// Virtual for requires manual conflict review
caseSchema.virtual('requiresManualConflictReview').get(function () {
  return this.conflictStatus?.checked && this.conflictStatus?.foundConflicts?.length > 0;
});

// Static method for adding PAIA requests
caseSchema.statics.addPaiaRequest = async function (caseId, paiaRequest) {
  const case_ = await this.findById(caseId);
  if (!case_) throw new Error('Case not found');

  case_.paiaRequests = case_.paiaRequests || [];
  case_.paiaRequests.push({
    ...paiaRequest,
    audit: {
      createdBy: paiaRequest.audit?.createdBy,
      createdAt: new Date(),
    },
  });

  // Update tracking
  case_.paiaTracking.totalRequests = (case_.paiaTracking.totalRequests || 0) + 1;
  case_.paiaTracking.pendingRequests = (case_.paiaTracking.pendingRequests || 0) + 1;

  await case_.save();

  return { success: true, requestId: paiaRequest.requestId };
};

// Static method for finding by tenant
caseSchema.statics.findByTenant = function (tenantId, options = {}) {
  const query = { tenantId };
  if (options.status) query.status = options.status;
  if (options.search) {
    query.$text = { $search: options.search };
  }

  let queryBuilder = this.find(query).sort({ createdAt: -1 });

  if (options.limit) queryBuilder = queryBuilder.limit(options.limit);
  if (options.skip) queryBuilder = queryBuilder.skip(options.skip);

  return queryBuilder;
};

// Static method for finding by court
caseSchema.statics.findByCourt = function (court) {
  return this.find({ court }).sort({ createdAt: -1 });
};

// Static method for getting PAIA stats
caseSchema.statics.getPaiaStats = function (tenantId) {
  return this.aggregate([
    { $match: { tenantId } },
    { $unwind: '$paiaRequests' },
    {
      $group: {
        _id: '$paiaRequests.status',
        count: { $sum: 1 },
      },
    },
  ]);
};

const Case = mongoose.model('Case', caseSchema);

export default Case;
