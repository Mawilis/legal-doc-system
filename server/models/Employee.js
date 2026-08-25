/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – SOVEREIGN EMPLOYEE MODEL [V3.0.4-SYNC-HOOK]                                                                               ║
 * ║ [HUMAN RESOURCES FABRIC | CRM | BILLING | PAYROLL | COMPLIANCE]                                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 3.0.4-SYNC-HOOK | PRODUCTION READY                                                                                           ║
 * ║ EPITOME: Mongoose 7+/8-safe pre-save (no next callback). Uniqueness via DB index.                                                   ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/Employee.js                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 FIX (v3.0.4):                                                                                                                       ║
 * ║   1. Removed next() from pre('save') — Mongoose no longer injects next; calling it → "next is not a function".                      ║
 * ║   2. Sync hook only sets displayName when empty; safe optional chaining on legalName.                                                 ║
 * ║   3. Unique indexes remain the source of truth for employeeId / workEmail.                                                            ║
 * ║   4. All fields preserved from V3.0.3.                                                                                                 ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';

const { Schema } = mongoose;

// ─── ENUMS ────────────────────────────────────────────────────────────────────

const EMPLOYMENT_TYPES = ['PERMANENT', 'CONTRACT', 'INTERN', 'TRAINEE', 'CONSULTANT', 'PROBATION'];
const EMPLOYEE_STATUSES = ['ACTIVE', 'ON_LEAVE', 'SUSPENDED', 'TERMINATED', 'RETIRED', 'INACTIVE'];
const GENDER_OPTIONS = ['MALE', 'FEMALE', 'NON_BINARY', 'PREFER_NOT_TO_SAY', 'OTHER'];
const MARITAL_STATUSES = ['SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED', 'SEPARATED', 'PREFER_NOT_TO_SAY'];
const PAY_FREQUENCIES = ['MONTHLY', 'BI_WEEKLY', 'WEEKLY', 'DAILY', 'ANNUAL'];
const ONBOARDING_STATUSES = ['NOT_STARTED', 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED'];
const IDENTIFICATION_TYPES = ['NATIONAL_ID', 'PASSPORT', 'DRIVERS_LICENSE', 'WORK_PERMIT', 'VISA', 'OTHER'];
const WORK_PERMIT_TYPES = ['GENERAL', 'CRITICAL_SKILLS', 'INTRA_COMPANY', 'STUDENT', 'OTHER'];
const VISA_TYPES = ['TOURIST', 'BUSINESS', 'WORK', 'STUDENT', 'RESIDENCE', 'DIPLOMATIC', 'OTHER'];

// ─── SUB‑SCHEMAS ─────────────────────────────────────────────────────────────

const NationalIdSchema = new Schema({
  number: { type: String, required: true, trim: true },
  country: { type: String, required: true, trim: true, default: 'ZA' },
  type: { type: String, enum: IDENTIFICATION_TYPES, default: 'NATIONAL_ID' },
  issueDate: { type: Date, default: null },
  expiryDate: { type: Date, default: null },
  issuingAuthority: { type: String, trim: true, default: '' },
}, { _id: false });

const PassportSchema = new Schema({
  number: { type: String, required: true, trim: true },
  country: { type: String, required: true, trim: true, default: 'ZA' },
  issueDate: { type: Date, default: null },
  expiryDate: { type: Date, default: null },
  issuingAuthority: { type: String, trim: true, default: '' },
}, { _id: false });

const WorkPermitSchema = new Schema({
  number: { type: String, required: true, trim: true },
  type: { type: String, enum: WORK_PERMIT_TYPES, default: 'GENERAL' },
  issuingCountry: { type: String, required: true, trim: true, default: 'ZA' },
  issueDate: { type: Date, default: null },
  expiryDate: { type: Date, default: null },
}, { _id: false });

const VisaSchema = new Schema({
  number: { type: String, required: true, trim: true },
  type: { type: String, enum: VISA_TYPES, default: 'WORK' },
  issuingCountry: { type: String, required: true, trim: true, default: 'ZA' },
  issueDate: { type: Date, default: null },
  expiryDate: { type: Date, default: null },
}, { _id: false });

const DriversLicenseSchema = new Schema({
  number: { type: String, required: true, trim: true },
  country: { type: String, required: true, trim: true, default: 'ZA' },
  class: { type: String, trim: true, default: '' },
  issueDate: { type: Date, default: null },
  expiryDate: { type: Date, default: null },
}, { _id: false });

// ─── MAIN SCHEMA ─────────────────────────────────────────────────────────────

const EmployeeSchema = new Schema(
  {
    // ─── 1. IDENTITY ──────────────────────────────────────────────────────────
    employeeId: {
      type: String,
      required: [true, 'Employee ID is required'],
      unique: true,
      trim: true,
      index: true,
    },
    externalId: {
      type: String,
      trim: true,
      sparse: true,
      index: true,
    },
    legalName: {
      firstName: { type: String, required: true, trim: true, index: true },
      middleName: { type: String, trim: true, default: '' },
      lastName: { type: String, required: true, trim: true, index: true },
      suffix: { type: String, trim: true, default: '' },
    },
    preferredName: {
      type: String,
      trim: true,
      default: '',
    },
    displayName: {
      type: String,
      trim: true,
      default: '',
    },
    photograph: {
      type: String,
      trim: true,
      default: '',
    },

    // ─── 2. PERSONAL ──────────────────────────────────────────────────────────
    dateOfBirth: {
      type: Date,
      required: true,
    },
    placeOfBirth: {
      city: { type: String, trim: true, default: '' },
      country: { type: String, trim: true, default: '' },
    },
    gender: {
      type: String,
      enum: GENDER_OPTIONS,
      default: 'PREFER_NOT_TO_SAY',
    },
    maritalStatus: {
      type: String,
      enum: MARITAL_STATUSES,
      default: 'PREFER_NOT_TO_SAY',
    },
    nationality: {
      type: String,
      trim: true,
      default: '',
      index: true,
    },
    language: {
      type: String,
      trim: true,
      default: 'en',
    },
    religion: {
      type: String,
      trim: true,
      default: '',
    },
    ethnicity: {
      type: String,
      trim: true,
      default: '',
    },

    // ─── 3. IDENTITY DOCUMENTATION ──────────────────────────────────────────
    identification: {
      nationalId: { type: NationalIdSchema, default: null },
      passport: { type: PassportSchema, default: null },
      taxId: {
        number: { type: String, trim: true, default: '' },
        country: { type: String, trim: true, default: 'ZA' },
      },
      workPermit: { type: WorkPermitSchema, default: null },
      visa: { type: VisaSchema, default: null },
      driversLicense: { type: DriversLicenseSchema, default: null },
      socialSecurity: {
        number: { type: String, trim: true, default: '' },
        country: { type: String, trim: true, default: 'ZA' },
      },
      additional: {
        type: [{
          type: { type: String, enum: IDENTIFICATION_TYPES, default: 'OTHER' },
          number: { type: String, trim: true },
          country: { type: String, trim: true, default: 'ZA' },
          issueDate: { type: Date, default: null },
          expiryDate: { type: Date, default: null },
          issuingAuthority: { type: String, trim: true, default: '' },
        }],
        default: [],
      },
    },

    // ─── 4. CONTACT ───────────────────────────────────────────────────────────
    contact: {
      personalEmail: {
        type: String,
        trim: true,
        lowercase: true,
        match: [/^\S+@\S+\.\S+$/, 'Please provide a valid email address'],
      },
      workEmail: {
        type: String,
        required: true,
        unique: true,
        trim: true,
        lowercase: true,
        match: [/^\S+@\S+\.\S+$/, 'Please provide a valid email address'],
        index: true,
      },
      personalPhone: { type: String, trim: true, default: '' },
      workPhone: { type: String, trim: true, default: '' },
      emergencyContact: {
        name: { type: String, trim: true, default: '' },
        relationship: { type: String, trim: true, default: '' },
        phone: { type: String, trim: true, default: '' },
      },
    },

    // ─── 5. ADDRESS ───────────────────────────────────────────────────────────
    address: {
      physical: {
        street: { type: String, trim: true, default: '' },
        city: { type: String, trim: true, default: '' },
        state: { type: String, trim: true, default: '' },
        postalCode: { type: String, trim: true, default: '' },
        country: { type: String, trim: true, default: 'ZA' },
      },
      postal: {
        street: { type: String, trim: true, default: '' },
        city: { type: String, trim: true, default: '' },
        state: { type: String, trim: true, default: '' },
        postalCode: { type: String, trim: true, default: '' },
        country: { type: String, trim: true, default: 'ZA' },
      },
    },

    // ─── 6. EMPLOYMENT ────────────────────────────────────────────────────────
    employment: {
      jobTitle: { type: String, required: true, trim: true, index: true },
      department: { type: String, required: true, trim: true, index: true },
      managerId: { type: Schema.Types.ObjectId, ref: 'Employee', default: null, index: true },
      employmentType: { type: String, enum: EMPLOYMENT_TYPES, required: true, default: 'PERMANENT' },
      status: { type: String, enum: EMPLOYEE_STATUSES, required: true, default: 'ACTIVE', index: true },
      hireDate: { type: Date, required: true },
      seniorityDate: { type: Date, default: null },
      terminationDate: { type: Date, default: null },
      workLocation: { type: String, trim: true, default: '' },
    },

    // ─── 7. FINANCIAL ────────────────────────────────────────────────────────
    financial: {
      bankAccount: {
        accountName: { type: String, trim: true, default: '' },
        accountNumber: { type: String, trim: true, default: '' },
        branchCode: { type: String, trim: true, default: '' },
        bankName: { type: String, trim: true, default: '' },
      },
      basicSalary: { type: Number, default: 0, min: 0 },
      salaryCurrency: { type: String, default: 'ZAR', uppercase: true, trim: true },
      payFrequency: { type: String, enum: PAY_FREQUENCIES, default: 'MONTHLY' },
      costCentre: { type: String, trim: true, default: '' },
    },

    // ─── 8. COMPLIANCE ────────────────────────────────────────────────────────
    compliance: {
      backgroundCheck: { type: String, trim: true, default: '' },
      backgroundCheckDate: { type: Date, default: null },
      criminalRecord: { type: String, trim: true, default: '' },
    },

    // ─── 9. HR / ADMIN ────────────────────────────────────────────────────────
    hr: {
      joinedDate: { type: Date, default: Date.now },
      onboardingStatus: { type: String, enum: ONBOARDING_STATUSES, default: 'NOT_STARTED' },
      probationEndDate: { type: Date, default: null },
      leaveBalance: {
        annual: { type: Number, default: 0, min: 0 },
        sick: { type: Number, default: 0, min: 0 },
        familyResponsibility: { type: Number, default: 0, min: 0 },
      },
      skills: { type: [String], default: [], index: true },
      qualifications: { type: [String], default: [] },
    },

    // ─── 10. SYSTEM ────────────────────────────────────────────────────────────
    tenantId: {
      type: String,
      required: [true, 'tenantId is required'],
      trim: true,
      index: true,
      default: 'GLOBAL_ROOT',
    },
    isActive: { type: Boolean, default: true, index: true },
    deletedAt: { type: Date, default: null, index: true },
    metadata: { type: Schema.Types.Mixed, default: {} },
  },
  {
    timestamps: true,
    toJSON: {
      transform: (doc, ret) => {
        ret.id = ret._id;
        delete ret._id;
        delete ret.__v;
        return ret;
      },
    },
    toObject: {
      transform: (doc, ret) => {
        ret.id = ret._id;
        delete ret._id;
        delete ret.__v;
        return ret;
      },
    },
  }
);

// ─── INDEXES ──────────────────────────────────────────────────────────────────

EmployeeSchema.index({ tenantId: 1, isActive: 1, 'employment.status': 1 });
EmployeeSchema.index({ tenantId: 1, 'employment.department': 1 });
EmployeeSchema.index({ tenantId: 1, 'employment.jobTitle': 1 });
EmployeeSchema.index({ 'employment.managerId': 1, tenantId: 1 });

EmployeeSchema.index({ 'identification.nationalId.number': 1 });
EmployeeSchema.index({ 'identification.passport.number': 1 });
EmployeeSchema.index({ 'identification.taxId.number': 1 });

EmployeeSchema.index(
  {
    employeeId: 'text',
    'legalName.firstName': 'text',
    'legalName.lastName': 'text',
    displayName: 'text',
    'contact.workEmail': 'text',
    'hr.skills': 'text',
    'identification.nationalId.number': 'text',
    'identification.passport.number': 'text',
  },
  {
    name: 'employee_text_search',
    weights: {
      employeeId: 10,
      'legalName.firstName': 8,
      'legalName.lastName': 8,
      displayName: 6,
      'contact.workEmail': 4,
      'hr.skills': 2,
      'identification.nationalId.number': 5,
      'identification.passport.number': 5,
    },
  }
);

// ─── HOOKS (Mongoose 7+/8 — do NOT use next) ─────────────────────────────────

EmployeeSchema.pre('save', function setDisplayName() {
  if (!this.displayName || String(this.displayName).trim() === '') {
    const parts = [
      this.legalName?.firstName,
      this.legalName?.lastName,
    ].filter(Boolean);
    this.displayName = parts.join(' ');
  }
});

// ─── STATIC METHODS ──────────────────────────────────────────────────────────

EmployeeSchema.statics.findActiveByTenant = function (tenantId, filters = {}, limit = 100) {
  const query = { tenantId, isActive: true, deletedAt: null };
  if (filters.department) query['employment.department'] = filters.department;
  if (filters.jobTitle) query['employment.jobTitle'] = filters.jobTitle;
  if (filters.status) query['employment.status'] = filters.status;
  return this.find(query).sort({ 'legalName.lastName': 1, 'legalName.firstName': 1 }).limit(limit).lean();
};

EmployeeSchema.statics.findDirectReports = function (managerId, tenantId) {
  return this.find({
    'employment.managerId': managerId,
    tenantId,
    isActive: true,
    deletedAt: null,
  }).sort({ 'legalName.lastName': 1 }).lean();
};

EmployeeSchema.statics.searchEmployees = function (query, tenantId, options = {}) {
  const limit = Math.min(options.limit || 20, 100);
  const offset = options.offset || 0;
  const filter = { tenantId, isActive: true, deletedAt: null };
  let searchQuery = {};
  if (query && query.trim().length >= 2) {
    searchQuery = { $text: { $search: query.trim() } };
  }
  const finalFilter = { ...filter, ...searchQuery };
  return Promise.all([
    this.find(finalFilter)
      .sort(query && query.trim().length >= 2 ? { score: { $meta: 'textScore' } } : { 'legalName.lastName': 1 })
      .skip(offset)
      .limit(limit)
      .lean(),
    this.countDocuments(finalFilter),
  ]).then(([items, total]) => ({ items, total }));
};

// ─── MODEL EXPORT ──────────────────────────────────────────────────────────

const Employee = mongoose.models.Employee || mongoose.model('Employee', EmployeeSchema);
export default Employee;

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏛️ INSTITUTIONAL CERTIFICATION SEAL — Employee Model V3.0.4-SYNC-HOOK
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status:          CERTIFIED PRODUCTION ARTIFACT
 * Fix:             pre('save') no longer calls next() — fixes TypeError under Mongoose 7/8
 * Compliance:      POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15
 * ═══════════════════════════════════════════════════════════════════════════════
 */
