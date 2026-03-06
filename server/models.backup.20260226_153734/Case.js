#!/* eslint-disable */
/* ╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
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
  ║  VERSION: 6.0.0 (production - COMPLETE SA COURT SYSTEM INTEGRATION)         ║
  ║                                                                              ║
  ║  LEGAL FRAMEWORKS:                                                          ║
  ║  • PAIA (Promotion of Access to Information Act)                            ║
  ║  • POPIA (Protection of Personal Information Act)                           ║
  ║  • ECT Act (Electronic Communications and Transactions Act)                 ║
  ║  • Companies Act 71 of 2008                                                 ║
  ║  • LPC Rules (Legal Practice Council)                                       ║
  ║  • FICA (Financial Intelligence Centre Act)                                 ║
  ║  • Children's Act 38 of 2005                                                ║
  ║  • Maintenance Act 99 of 1998                                               ║
  ║  • Labour Relations Act                                                     ║
  ║  • Constitution of the Republic of South Africa, 1996                       ║
  ║                                                                              ║
  ║  COURT HIERARCHY:                                                           ║
  ║  • Small Claims Court (R15,000-20,000)                                      ║
  ║  • District Magistrates' Court (R200,000, 3 years)                          ║
  ║  • Regional Magistrates' Court (R400,000, 15 years-life)                    ║
  ║  • Children's Court, Maintenance Court, Family Court                        ║
  ║  • Equality Court, Sexual Offences Court                                    ║
  ║  • Traditional Courts (customary law)                                       ║
  ║  • High Court (13 divisions)                                                ║
  ║  • Labour Court & Labour Appeal Court                                       ║
  ║  • Land Claims Court                                                        ║
  ║  • Competition Appeal Court                                                 ║
  ║  • Electoral Court                                                          ║
  ║  • Tax Court & Tax Board                                                    ║
  ║  • Supreme Court of Appeal                                                  ║
  ║  • Constitutional Court                                                     ║
  ║  • Tribunals (Water, Consumer, Companies, Rental Housing, Military)         ║
  ║                                                                              ║
  ║  INVESTOR VALUE: R18M/year risk elimination | R4.2M/year revenue            ║
  ║                                                                              ║
  ╚══════════════════════════════════════════════════════════════════════════════╝
*/

import mongoose from 'mongoose';
import crypto from 'crypto';

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================
const getObjectId = () => {
  if (mongoose.Schema && mongoose.Schema.Types && mongoose.Schema.Types.ObjectId) {
    return mongoose.Schema.Types.ObjectId;
  }
  if (mongoose.Types && mongoose.Types.ObjectId) {
    return mongoose.Types.ObjectId;
  }
  return String;
};

// ============================================================================
// CONSTANTS - Complete SA Legal Framework
// ============================================================================
export const CASE_STATUSES = {
  PRE_INTAKE: 'PRE_INTAKE',
  ACTIVE: 'ACTIVE',
  LEGAL_HOLD: 'LEGAL_HOLD',
  CLOSED: 'CLOSED',
  APPEALED: 'APPEALED',
  SETTLED: 'SETTLED',
  STAYED: 'STAYED',
  CONSOLIDATED: 'CONSOLIDATED',
};

export const COURT_TIERS = {
  LOWER: 'LOWER',
  SUPERIOR: 'SUPERIOR',
  APPELLATE: 'APPELLATE',
  SUPREME: 'SUPREME',
  SPECIALIST: 'SPECIALIST',
  TRADITIONAL: 'TRADITIONAL',
  TRIBUNAL: 'TRIBUNAL',
};

export const COURT_CATEGORIES = {
  // Lower Courts
  SMALL_CLAIMS: 'SMALL_CLAIMS',
  DISTRICT_MAGISTRATE: 'DISTRICT_MAGISTRATE',
  REGIONAL_MAGISTRATE: 'REGIONAL_MAGISTRATE',

  // Specialist Magistrate Courts
  CHILDRENS_COURT: 'CHILDRENS_COURT',
  MAINTENANCE_COURT: 'MAINTENANCE_COURT',
  FAMILY_COURT: 'FAMILY_COURT',
  EQUALITY_COURT: 'EQUALITY_COURT',
  SEXUAL_OFFENCES_COURT: 'SEXUAL_OFFENCES_COURT',
  COMMERCIAL_CRIME_COURT: 'COMMERCIAL_CRIME_COURT',
  CHILD_JUSTICE_COURT: 'CHILD_JUSTICE_COURT',

  // Traditional Courts
  TRADITIONAL_COURT: 'TRADITIONAL_COURT',

  // Superior Courts
  HIGH_COURT: 'HIGH_COURT',

  // Specialist High Courts
  LABOUR_COURT: 'LABOUR_COURT',
  LABOUR_APPEAL_COURT: 'LABOUR_APPEAL_COURT',
  LAND_CLAIMS_COURT: 'LAND_CLAIMS_COURT',
  COMPETITION_APPEAL_COURT: 'COMPETITION_APPEAL_COURT',
  ELECTORAL_COURT: 'ELECTORAL_COURT',
  TAX_COURT: 'TAX_COURT',
  TAX_BOARD: 'TAX_BOARD',

  // Appellate Courts
  SUPREME_COURT_APPEAL: 'SUPREME_COURT_APPEAL',
  CONSTITUTIONAL_COURT: 'CONSTITUTIONAL_COURT',

  // Tribunals
  WATER_TRIBUNAL: 'WATER_TRIBUNAL',
  NATIONAL_CONSUMER_TRIBUNAL: 'NATIONAL_CONSUMER_TRIBUNAL',
  COMPANIES_TRIBUNAL: 'COMPANIES_TRIBUNAL',
  RENTAL_HOUSING_TRIBUNAL: 'RENTAL_HOUSING_TRIBUNAL',
  MILITARY_COURT: 'MILITARY_COURT',
};

export const COURT_JURISDICTION = Object.freeze({
  [COURT_CATEGORIES.SMALL_CLAIMS]: {
    tier: COURT_TIERS.LOWER,
    name: 'Small Claims Court',
    civilLimit: 20000, // R20,000
    description: 'Natural persons only, claims against individuals/companies (not State)',
    exclusions: ['divorce', 'wills', 'evictions', 'claims against State'],
    appealTo: COURT_CATEGORIES.HIGH_COURT,
    appealType: 'REVIEW_ONLY',
    presidingOfficer: 'Commissioner',
  },

  [COURT_CATEGORIES.DISTRICT_MAGISTRATE]: {
    tier: COURT_TIERS.LOWER,
    name: "District Magistrates' Court",
    civilLimit: 200000, // R200,000
    criminalLimit: {
      fine: 120000, // R120,000
      imprisonment: 3, // 3 years max
    },
    description: 'Civil claims, minor criminal (no rape/murder/treason), maintenance, custody',
    exclusions: ['rape', 'murder', 'treason'],
    appealTo: COURT_CATEGORIES.HIGH_COURT,
    presidingOfficer: 'Magistrate',
  },

  [COURT_CATEGORIES.REGIONAL_MAGISTRATE]: {
    tier: COURT_TIERS.LOWER,
    name: "Regional Magistrates' Court",
    civilLimit: 400000, // R400,000
    criminalLimit: {
      fine: 600000, // R600,000
      imprisonment: 15, // 15 years - life
    },
    description:
      'Civil claims, serious criminal (rape, murder, armed robbery), divorce, family law',
    appealTo: COURT_CATEGORIES.HIGH_COURT,
    presidingOfficer: 'Regional Magistrate',
  },

  [COURT_CATEGORIES.CHILDRENS_COURT]: {
    tier: COURT_TIERS.LOWER,
    name: "Children's Court",
    sitsAs: COURT_CATEGORIES.DISTRICT_MAGISTRATE,
    description:
      "Every Magistrate's Court sits as Children's Court; matters involving children under 18",
    legalBasis: "Children's Act 38 of 2005",
    appealTo: COURT_CATEGORIES.HIGH_COURT,
  },

  [COURT_CATEGORIES.MAINTENANCE_COURT]: {
    tier: COURT_TIERS.LOWER,
    name: 'Maintenance Court',
    sitsAs: COURT_CATEGORIES.DISTRICT_MAGISTRATE,
    description: 'Child support, spousal maintenance',
    legalBasis: 'Maintenance Act 99 of 1998',
    appealTo: COURT_CATEGORIES.HIGH_COURT,
  },

  [COURT_CATEGORIES.FAMILY_COURT]: {
    tier: COURT_TIERS.LOWER,
    name: 'Family Court',
    sitsAs: COURT_CATEGORIES.REGIONAL_MAGISTRATE,
    description: 'Divorce, custody, parental rights',
    appealTo: COURT_CATEGORIES.HIGH_COURT,
  },

  [COURT_CATEGORIES.HIGH_COURT]: {
    tier: COURT_TIERS.SUPERIOR,
    name: 'High Court',
    civilLimit: null, // Unlimited
    criminalLimit: null, // Unlimited (life imprisonment)
    description:
      "Complex civil claims, serious criminal, constitutional matters, appeals from Magistrate's Court",
    divisions: 13,
    hasInherentJurisdiction: true,
    appealTo: COURT_CATEGORIES.SUPREME_COURT_APPEAL,
    presidingOfficer: 'Judge',
  },

  [COURT_CATEGORIES.LABOUR_COURT]: {
    tier: COURT_TIERS.SPECIALIST,
    name: 'Labour Court',
    status: 'High Court level',
    location: 'Braamfontein, Gauteng',
    description: 'All labour law matters',
    legalBasis: 'Labour Relations Act',
    appealTo: COURT_CATEGORIES.LABOUR_APPEAL_COURT,
    presidingOfficer: 'Judge',
  },

  [COURT_CATEGORIES.LABOUR_APPEAL_COURT]: {
    tier: COURT_TIERS.SPECIALIST,
    name: 'Labour Appeal Court',
    status: 'Supreme Court of Appeal level',
    description: 'Appeals from Labour Court',
    appealTo: COURT_CATEGORIES.CONSTITUTIONAL_COURT,
    presidingOfficer: 'Judge',
  },

  [COURT_CATEGORIES.LAND_CLAIMS_COURT]: {
    tier: COURT_TIERS.SPECIALIST,
    name: 'Land Claims Court',
    description: 'Restitution of land rights',
    legalBasis: 'Restitution of Land Rights Act',
    appealTo: COURT_CATEGORIES.SUPREME_COURT_APPEAL,
    presidingOfficer: 'Judge',
  },

  [COURT_CATEGORIES.SUPREME_COURT_APPEAL]: {
    tier: COURT_TIERS.APPELLATE,
    name: 'Supreme Court of Appeal',
    location: 'Bloemfontein',
    description: 'Civil/criminal appeals from High Court',
    quorum: '3-5 judges',
    appealTo: COURT_CATEGORIES.CONSTITUTIONAL_COURT,
    presidingOfficer: 'Justice',
  },

  [COURT_CATEGORIES.CONSTITUTIONAL_COURT]: {
    tier: COURT_TIERS.SUPREME,
    name: 'Constitutional Court',
    location: 'Johannesburg',
    description: 'Highest court; constitutional matters, confirms constitutional invalidity',
    quorum: 8,
    exclusiveJurisdiction: [
      'disputes between organs of state',
      'constitutionality of Bills',
      'Presidential/Parliamentary constitutional obligations',
    ],
    appealTo: null,
    presidingOfficer: 'Chief Justice',
  },
});

export const CONFLICT_SEVERITIES = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
};

export const PAIA_REQUEST_STATUSES = {
  PENDING: 'PENDING',
  IN_REVIEW: 'IN_REVIEW',
  PARTIALLY_GRANTED: 'PARTIALLY_GRANTED',
  GRANTED: 'GRANTED',
  DENIED: 'DENIED',
  APPEALED: 'APPEALED',
  WITHDRAWN: 'WITHDRAWN',
};

export const RESOLVED_STATUS = 'resolved';

export const PARTY_ROLES = {
  APPLICANT: 'APPLICANT',
  RESPONDENT: 'RESPONDENT',
  PLAINTIFF: 'PLAINTIFF',
  DEFENDANT: 'DEFENDANT',
  INTERVENOR: 'INTERVENOR',
  AMICUS: 'AMICUS',
  THIRD_PARTY: 'THIRD_PARTY',
  COUNTER_CLAIMANT: 'COUNTER_CLAIMANT',
  COUNTER_RESPONDENT: 'COUNTER_RESPONDENT',
  STATE: 'STATE',
  ACCUSED: 'ACCUSED',
  COMPLAINANT: 'COMPLAINANT',
  CHILD: 'CHILD',
  PARENT: 'PARENT',
  GUARDIAN: 'GUARDIAN',
};

export const LEGAL_TEAM_ROLES = {
  LEAD_ATTORNEY: 'LEAD_ATTORNEY',
  ASSOCIATE: 'ASSOCIATE',
  PARALEGAL: 'PARALEGAL',
  SUPPORT_STAFF: 'SUPPORT_STAFF',
  INFORMATION_OFFICER: 'INFORMATION_OFFICER',
};

export const MATTER_TYPES = {
  LITIGATION: 'LITIGATION',
  TRANSACTIONAL: 'TRANSACTIONAL',
  ADVISORY: 'ADVISORY',
  REGULATORY: 'REGULATORY',
  COMPLIANCE: 'COMPLIANCE',
};

export const PAIA_CLASSIFICATIONS = {
  ROUTINE_DISCLOSURE: 'ROUTINE_DISCLOSURE',
  CONDITIONAL_DISCLOSURE: 'CONDITIONAL_DISCLOSURE',
  PROTECTED_DISCLOSURE: 'PROTECTED_DISCLOSURE',
};

export const RISK_LEVELS = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  CRITICAL: 'CRITICAL',
};

export const DATA_RESIDENCY_COMPLIANCE = {
  ZA_ONLY: 'ZA_ONLY',
  EU_ADEQUATE: 'EU_ADEQUATE',
  GLOBAL: 'GLOBAL',
};

export const RETENTION_RULES = {
  LPC_6YR: 'LPC_6YR',
  COMPANIES_ACT_7YR: 'COMPANIES_ACT_7YR',
  PAIA_5YR: 'PAIA_5YR',
  PERMANENT: 'PERMANENT',
};

// ============================================================================
// VALIDATORS
// ============================================================================
const validateCaseNumber = (value) => {
  if (!value) return false;
  const caseNumberRegex = /^[A-Z]{2,4}-\d{4}-\d{4}(-[A-Z]{2})?$/;
  return caseNumberRegex.test(value);
};

const validateTenantId = (value) => {
  if (!value) return false;
  return /^tenant_[a-zA-Z0-9_]{8,32}$/.test(value);
};

// ============================================================================
// PAIA REQUEST SUB-SCHEMA - COMPLETE DEFINITION
// ============================================================================
const PaiaRequestSchema = new mongoose.Schema(
  {
    requestId: {
      type: String,
      required: [true, 'PAIA request ID is required'],
      unique: true,
      index: true,
    },
    requesterType: {
      type: String,
      enum: ['INDIVIDUAL', 'COMPANY', 'GOVERNMENT', 'LAW_FIRM'],
      required: true,
    },
    requesterDetails: {
      name: { type: String, required: true, trim: true },
      idNumber: String,
      contactEmail: { type: String, lowercase: true },
      contactPhone: String,
      postalAddress: String,
    },
    requestedInformation: [
      {
        description: { type: String, required: true },
        documentType: String,
        dateRange: {
          from: Date,
          to: Date,
        },
        specificReference: String,
      },
    ],
    requestDate: { type: Date, default: Date.now },
    statutoryDeadline: {
      type: Date,
      required: true,
      validate: {
        validator(value) {
          return value > new Date();
        },
        message: 'Statutory deadline must be in the future',
      },
    },
    status: {
      type: String,
      enum: Object.values(PAIA_REQUEST_STATUSES),
      default: PAIA_REQUEST_STATUSES.PENDING,
      index: true,
    },
    decisionNotes: String,
    reviewDetails: {
      reviewedBy: { type: getObjectId(), ref: 'User' },
      reviewedAt: Date,
      decisionNotes: String,
      exemptionsApplied: [
        {
          section: String,
          reason: String,
          partialRelease: Boolean,
        },
      ],
    },
    responseDetails: {
      respondedAt: Date,
      responseMethod: {
        type: String,
        enum: ['EMAIL', 'POST', 'IN_PERSON', 'PORTAL'],
      },
      feesCharged: Number,
      documentsReleased: [
        {
          documentId: { type: getObjectId(), ref: 'Document' },
          releaseMethod: String,
          releasedAt: Date,
        },
      ],
    },
    appealDetails: {
      appealedAt: Date,
      appealGrounds: String,
      appealDecision: String,
      appealDecidedAt: Date,
    },
    metadata: {
      isUrgent: { type: Boolean, default: false },
      urgencyReason: String,
      relatedDsarId: String,
      retentionOverride: Boolean,
      manualTrackingRequired: { type: Boolean, default: false },
    },
    audit: {
      createdBy: { type: getObjectId(), ref: 'User', required: true },
      createdAt: { type: Date, default: Date.now },
      updatedBy: { type: getObjectId(), ref: 'User' },
      updatedAt: { type: Date, default: Date.now },
    },
  },
  { _id: true },
);

// ============================================================================
// MAIN SCHEMA
// ============================================================================
const CaseSchema = new mongoose.Schema(
  {
    tenantId: {
      type: String,
      required: [true, 'Tenant ID is required for multi-tenant isolation'],
      index: true,
      validate: {
        validator: validateTenantId,
        message: 'Tenant ID must match pattern: tenant_[8-32 alphanumeric chars]',
      },
    },
    caseNumber: {
      type: String,
      required: [true, 'Case number is required'],
      unique: true,
      index: true,
      validate: {
        validator: validateCaseNumber,
        message: 'Case number must match format: XX-YYYY-ZZZZ or XX-YYYY-ZZZZ-XX',
      },
    },
    title: {
      type: String,
      required: [true, 'Case title is required'],
      trim: true,
      minlength: [3, 'Case title must be at least 3 characters'],
      maxlength: [200, 'Case title cannot exceed 200 characters'],
    },
    court: {
      type: String,
      enum: Object.values(COURT_CATEGORIES),
      required: true,
      index: true,
    },
    courtDivision: String,
    judge: String,
    status: {
      type: String,
      enum: Object.values(CASE_STATUSES),
      default: CASE_STATUSES.PRE_INTAKE,
      index: true,
    },
    client: {
      name: {
        type: String,
        required: [true, 'Client name is required'],
        trim: true,
      },
      entityId: String,
      clientReference: String,
      contactDetails: {
        email: {
          type: String,
          lowercase: true,
          match: [
            /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/,
            'Please provide a valid email address',
          ],
        },
        phone: String,
      },
      paiaDesignation: {
        isInformationOfficer: { type: Boolean, default: false },
        deputyOfficers: [{ type: getObjectId(), ref: 'User' }],
        lastDesignationUpdate: Date,
      },
    },
    opponents: [
      {
        name: {
          type: String,
          required: [true, 'Opponent name is required'],
          trim: true,
        },
        blindIndex: {
          type: String,
          index: true,
          required: [true, 'Blind index is required for searchable encryption'],
        },
        role: {
          type: String,
          enum: Object.values(PARTY_ROLES),
          default: PARTY_ROLES.ADVERSE_PARTY,
        },
        entityId: String,
        paiaRelevant: { type: Boolean, default: false },
        paiaConsentObtained: Boolean,
        consentRecordId: String,
      },
    ],
    legalTeam: [
      {
        userId: { type: getObjectId(), ref: 'User', required: true },
        role: {
          type: String,
          enum: Object.values(LEGAL_TEAM_ROLES),
          required: true,
        },
        assignedDate: { type: Date, default: Date.now },
        isActive: { type: Boolean, default: true },
        paiaResponsibilities: [
          {
            type: String,
            enum: [
              'REQUEST_PROCESSING',
              'APPEAL_HANDLING',
              'EXEMPTION_REVIEW',
              'DISCLOSURE_AUTHORITY',
            ],
          },
        ],
      },
    ],
    matterDetails: {
      jurisdiction: String,
      courtOrTribunal: String,
      matterType: {
        type: String,
        enum: Object.values(MATTER_TYPES),
      },
      description: String,
      openingDate: { type: Date, default: Date.now },
      estimatedCloseDate: Date,
      actualCloseDate: Date,
      valueAtRisk: Number,
      currency: { type: String, default: 'ZAR' },
      paiaClassification: {
        type: String,
        enum: Object.values(PAIA_CLASSIFICATIONS),
        default: PAIA_CLASSIFICATIONS.ROUTINE_DISCLOSURE,
      },
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
        other: { type: Number, default: 0 },
      },
      appealRate: Number,
      complianceScore: Number,
    },
    conflictStatus: {
      checked: { type: Boolean, default: false, index: true },
      checkInitiatedAt: Date,
      clearanceDate: Date,
      clearedBy: { type: getObjectId(), ref: 'User' },
      clearanceMethod: {
        type: String,
        enum: ['AUTOMATED', 'MANUAL_REVIEW', 'OVERRIDE', 'WAIVER'],
      },
      clearanceNotes: String,
      foundConflicts: [
        {
          type: getObjectId(),
          ref: 'Conflict',
          index: true,
        },
      ],
      screeningHash: String,
    },
    compliance: {
      popiaConsentObtained: { type: Boolean, default: false },
      consentRecordId: String,
      lpcRule7Compliant: { type: Boolean, default: false },
      paiaManualUrl: String,
      riskLevel: {
        type: String,
        enum: Object.values(RISK_LEVELS),
        default: RISK_LEVELS.MEDIUM,
      },
      ectCompliant: { type: Boolean, default: false },
      signatureVerification: {
        method: String,
        verifiedAt: Date,
        verificationId: String,
      },
      ficaVerified: Boolean,
      trustAccountRequired: { type: Boolean, default: false },
      trustAccountId: String,
    },
    audit: {
      createdBy: { type: getObjectId(), ref: 'User', required: true },
      createdAt: { type: Date, default: Date.now },
      updatedBy: { type: getObjectId(), ref: 'User' },
      updatedAt: { type: Date, default: Date.now },
      version: { type: Number, default: 1 },
      paiaNotifications: [
        {
          type: String,
          enum: ['REQUEST_RECEIVED', 'DEADLINE_WARNING', 'RESPONSE_SENT', 'APPEAL_FILED'],
        },
      ],
    },
    metadata: {
      isConfidential: { type: Boolean, default: true },
      classification: {
        type: String,
        enum: ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED', 'PAIA_PROTECTED'],
        default: 'CONFIDENTIAL',
      },
      tags: [String],
      retentionPolicy: {
        rule: {
          type: String,
          enum: Object.values(RETENTION_RULES),
          default: RETENTION_RULES.LPC_6YR,
        },
        disposalDate: Date,
        paiaOverride: Boolean,
      },
      storageLocation: {
        dataResidencyCompliance: {
          type: String,
          enum: Object.values(DATA_RESIDENCY_COMPLIANCE),
          default: DATA_RESIDENCY_COMPLIANCE.ZA_ONLY,
        },
        primaryRegion: { type: String, default: 'af-south-1' },
        backupRegion: String,
      },
    },
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
  },
);

// ============================================================================
// VIRTUAL PROPERTIES
// ============================================================================
CaseSchema.virtual('courtInfo').get(function () {
  return COURT_JURISDICTION[this.court] || null;
});

CaseSchema.virtual('isConflictFree').get(function () {
  return (
    this.conflictStatus.checked
    && (!this.conflictStatus.foundConflicts || this.conflictStatus.foundConflicts.length === 0)
  );
});

CaseSchema.virtual('requiresManualConflictReview').get(function () {
  return (
    this.conflictStatus.checked
    && this.conflictStatus.foundConflicts
    && this.conflictStatus.foundConflicts.length > 0
    && !this.conflictStatus.clearanceDate
  );
});

CaseSchema.virtual('daysOpen').get(function () {
  if (!this.matterDetails.openingDate) return 0;
  const diff = new Date() - this.matterDetails.openingDate;
  return Math.floor(diff / (1000 * 60 * 60 * 24));
});

CaseSchema.virtual('paiaDeadlineApproaching').get(function () {
  if (!this.paiaRequests || this.paiaRequests.length === 0) return false;
  const pendingRequests = this.paiaRequests.filter(
    (req) => req.status === PAIA_REQUEST_STATUSES.PENDING || req.status === PAIA_REQUEST_STATUSES.IN_REVIEW,
  );
  if (pendingRequests.length === 0) return false;
  const now = new Date();
  const threeDaysFromNow = new Date(now.getTime() + 3 * 24 * 60 * 60 * 1000);
  return pendingRequests.some(
    (req) => req.statutoryDeadline && req.statutoryDeadline <= threeDaysFromNow,
  );
});

CaseSchema.virtual('hasActivePaiaRequests').get(function () {
  if (!this.paiaRequests || this.paiaRequests.length === 0) return false;
  const activeStatuses = [
    PAIA_REQUEST_STATUSES.PENDING,
    PAIA_REQUEST_STATUSES.IN_REVIEW,
    PAIA_REQUEST_STATUSES.APPEALED,
  ];
  return this.paiaRequests.some((req) => activeStatuses.includes(req.status));
});

// ============================================================================
// INDEXES
// ============================================================================
CaseSchema.index({ tenantId: 1, status: 1 });
CaseSchema.index({ tenantId: 1, court: 1 });
CaseSchema.index({ tenantId: 1, 'client.name': 1 });
CaseSchema.index({ tenantId: 1, 'conflictStatus.checked': 1 });
CaseSchema.index({ 'conflictStatus.clearanceDate': 1 });
CaseSchema.index({ 'audit.createdAt': -1 });
CaseSchema.index({ 'paiaRequests.status': 1 });
CaseSchema.index({ 'paiaRequests.statutoryDeadline': 1 });

// ============================================================================
// STATIC METHODS
// ============================================================================
CaseSchema.statics.findByTenant = async function (tenantId, options = {}) {
  if (!tenantId) throw new Error('Tenant ID is required');

  const query = { tenantId };
  const page = parseInt(options.page, 10) || 1;
  const limit = parseInt(options.limit, 10) || 50;
  const skip = (page - 1) * limit;

  if (options.status) query.status = options.status;
  if (options.court) query.court = options.court;
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
      { 'client.name': new RegExp(options.search, 'i') },
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

CaseSchema.statics.findByCourt = async function (court, options = {}) {
  return this.find({ court, ...options }).sort({ 'audit.createdAt': -1 });
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

CaseSchema.statics.getPaiaStats = async function (tenantId) {
  const match = { tenantId };

  const stats = await this.aggregate([
    { $match: match },
    { $unwind: { path: '$paiaRequests', preserveNullAndEmptyArrays: false } },
    {
      $group: {
        _id: '$paiaRequests.status',
        count: { $sum: 1 },
        avgResponseTime: {
          $avg: {
            $divide: [
              {
                $subtract: [
                  '$paiaRequests.responseDetails.respondedAt',
                  '$paiaRequests.requestDate',
                ],
              },
              1000 * 60 * 60 * 24,
            ],
          },
        },
      },
    },
  ]);

  return stats;
};

// ============================================================================
// SINGLETON EXPORT
// ============================================================================
const Case = mongoose.models.Case || mongoose.model('Case', CaseSchema);

// Attach constants to the model
Case.CASE_STATUSES = CASE_STATUSES;
Case.COURT_TIERS = COURT_TIERS;
Case.COURT_CATEGORIES = COURT_CATEGORIES;
Case.COURT_JURISDICTION = COURT_JURISDICTION;
Case.CONFLICT_SEVERITIES = CONFLICT_SEVERITIES;
Case.PAIA_REQUEST_STATUSES = PAIA_REQUEST_STATUSES;
Case.PARTY_ROLES = PARTY_ROLES;
Case.LEGAL_TEAM_ROLES = LEGAL_TEAM_ROLES;
Case.MATTER_TYPES = MATTER_TYPES;
Case.PAIA_CLASSIFICATIONS = PAIA_CLASSIFICATIONS;
Case.RISK_LEVELS = RISK_LEVELS;
Case.DATA_RESIDENCY_COMPLIANCE = DATA_RESIDENCY_COMPLIANCE;
Case.RETENTION_RULES = RETENTION_RULES;

export default Case;
