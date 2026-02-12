/**
 * WILSYS OS - ATTORNEY PROFILE MODEL
 * ====================================================================
 * LEGAL PRACTICE COUNCIL · FORENSIC ATTORNEY REGISTRY
 * @version 5.0.1
 * ====================================================================
 */

const mongoose = require('mongoose');
const { Schema } = mongoose;
const crypto = require('crypto');
const { redactSensitiveData } = require('../utils/popiaRedaction');

const ATTORNEY_STATUS = {
    ACTIVE: 'ACTIVE',
    SUSPENDED: 'SUSPENDED',
    EXPIRED: 'EXPIRED',
    DECEASED: 'DECEASED',
    RESIGNED: 'RESIGNED',
    RETIRED: 'RETIRED',
    NON_PRACTICING: 'NON_PRACTICING'
};

const PRACTICE_TYPES = {
    PRIVATE: 'PRIVATE',
    GOVERNMENT: 'GOVERNMENT',
    CORPORATE: 'CORPORATE',
    LEGAL_AID: 'LEGAL_AID',
    ACADEMIC: 'ACADEMIC',
    NON_PRACTICING: 'NON_PRACTICING'
};

const PRACTICE_AREAS = {
    URBAN: 'URBAN',
    RURAL: 'RURAL',
    INTERNATIONAL: 'INTERNATIONAL'
};

const FIDELITY_STATUS = {
    ACTIVE: 'ACTIVE',
    EXPIRED: 'EXPIRED',
    REVOKED: 'REVOKED',
    PENDING: 'PENDING',
    SUSPENDED: 'SUSPENDED'
};

const CPD_STATUS = {
    COMPLIANT: 'COMPLIANT',
    NON_COMPLIANT: 'NON_COMPLIANT',
    PENDING: 'PENDING',
    EXEMPT: 'EXEMPT',
    GRACE_PERIOD: 'GRACE_PERIOD'
};

const attorneyProfileSchema = new Schema({
    tenantId: {
        type: String,
        required: [true, 'TENANT_ISOLATION_VIOLATION: tenantId is required'],
        index: true,
        immutable: true,
        validate: {
            validator: function(v) {
                return /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(v);
            },
            message: props => `${props.value} is not a valid tenant UUID`
        }
    },

    lpcNumber: {
        type: String,
        required: [true, 'LPC number is required by Legal Practice Act Section 55'],
        unique: true,
        uppercase: true,
        trim: true,
        immutable: true,
        validate: {
            validator: function(v) {
                return /^(LPC-\d{8}|\d{4}\/\d{4})$/.test(v);
            },
            message: props => `${props.value} is not a valid LPC number`
        },
        index: true
    },

    practiceNumber: {
        type: String,
        unique: true,
        sparse: true,
        uppercase: true,
        trim: true,
        validate: {
            validator: function(v) {
                return !v || /^PRAC-\d{8}$/.test(v);
            },
            message: props => `${props.value} is not a valid practice number`
        }
    },

    personalInfo: {
        title: { type: String, enum: ['Mr', 'Mrs', 'Ms', 'Dr', 'Prof', 'Adv', 'Justice'], required: true },
        fullName: { type: String, required: true, trim: true, maxlength: 200 },
        preferredName: { type: String, trim: true, maxlength: 100 },
        idNumber: { type: String, required: true, unique: true, validate: { validator: v => /^\d{13}$/.test(v) } },
        passportNumber: { type: String, sparse: true, validate: { validator: v => !v || /^[A-Z]{2}\d{7}$/.test(v) } },
        nationality: { type: String, default: 'South African', maxlength: 50 },
        dateOfBirth: { type: Date, required: true },
        gender: { type: String, enum: ['Male', 'Female', 'Other', 'Prefer not to say'] }
    },

    contact: {
        email: { type: String, required: true, lowercase: true, trim: true, validate: { validator: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) } },
        alternativeEmail: { type: String, lowercase: true, trim: true },
        phone: { type: String, required: true, validate: { validator: v => /^(\+27|0)[1-9][0-9]{8}$/.test(v) } },
        alternativePhone: { type: String, validate: { validator: v => !v || /^(\+27|0)[1-9][0-9]{8}$/.test(v) } },
        fax: { type: String, validate: { validator: v => !v || /^(\+27|0)[1-9][0-9]{8}$/.test(v) } }
    },

    address: {
        physical: {
            line1: { type: String, required: true },
            line2: String,
            suburb: { type: String, required: true },
            city: { type: String, required: true },
            province: { type: String, required: true, enum: ['GP', 'WC', 'KZN', 'EC', 'FS', 'MP', 'NW', 'LIM', 'NC'] },
            postalCode: { type: String, required: true },
            country: { type: String, default: 'South Africa' }
        },
        postal: {
            line1: String, line2: String, suburb: String, city: String, province: String, postalCode: String, country: { type: String, default: 'South Africa' }
        },
        jurisdiction: {
            magisterialDistrict: { type: String, required: true, index: true },
            highCourtDivision: { type: String, required: true, enum: ['GP', 'GJD', 'KZD', 'ECD', 'FB', 'MM', 'NWM', 'LPM', 'NCK'] }
        }
    },

    practice: {
        name: { type: String, required: true, trim: true, maxlength: 200 },
        type: { type: String, required: true, enum: Object.values(PRACTICE_TYPES) },
        area: { type: String, required: true, enum: Object.values(PRACTICE_AREAS) },
        commencementDate: { type: Date, required: true, immutable: true },
        yearsOfPractice: { type: Number, default: function() { return Math.floor((Date.now() - this.practice.commencementDate) / (1000 * 60 * 60 * 24 * 365)); } },
        specializations: [{ type: String, enum: ['LITIGATION', 'CONVEYANCING', 'COMMERCIAL', 'ESTATE', 'FAMILY', 'CRIMINAL', 'LABOUR', 'TAX', 'INTELLECTUAL_PROPERTY', 'CONSTITUTIONAL', 'ENVIRONMENTAL', 'INSURANCE', 'BANKING', 'IMMIGRATION'] }],
        languages: [{ language: String, proficiency: { type: String, enum: ['BASIC', 'INTERMEDIATE', 'FLUENT', 'NATIVE'] } }],
        employees: { type: Number, default: 1, min: 1 },
        partners: { type: Number, default: 1, min: 1 }
    },

    fidelityFund: {
        certificateNumber: { type: String, sparse: true, validate: { validator: v => !v || /^FFC-\d{4}-[A-F0-9]{8}$/.test(v) } },
        issueDate: Date,
        expiryDate: { type: Date, index: true },
        status: { type: String, enum: Object.values(FIDELITY_STATUS), default: 'PENDING' },
        contributionAmount: { type: Number, min: 0, get: v => parseFloat(v.toFixed(2)) },
        turnoverDeclared: { type: Number, min: 0, get: v => parseFloat(v.toFixed(2)) },
        verificationHash: String
    },

    cpd: {
        currentYear: { type: Number, default: new Date().getFullYear(), index: true },
        hoursCompleted: { type: Number, default: 0, min: 0, max: 30 },
        ethicsHours: { type: Number, default: 0, min: 0, max: 10 },
        lastSubmissionDate: Date,
        complianceStatus: { type: String, enum: Object.values(CPD_STATUS), default: 'PENDING' },
        rolloverHours: { type: Number, default: 0, min: 0, max: 6 },
        verifiedAt: Date,
        verifiedBy: String
    },

    trustAccount: {
        accountNumber: { type: String, sparse: true, validate: { validator: v => !v || /^TRUST-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$/.test(v) } },
        bankName: { type: String, enum: ['ABSA', 'FNB', 'NEDBANK', 'STANDARD_BANK', 'CAPITEC', 'AFRICAN_BANK', 'BIDVEST_BANK', 'DISCOVERY_BANK'] },
        isActive: { type: Boolean, default: false },
        lastReconciliation: Date,
        nextReconciliationDue: Date,
        complianceScore: { type: Number, min: 0, max: 100, default: 0 }
    },

    employmentHistory: [{
        firmName: String, position: String, startDate: Date, endDate: Date, isCurrent: { type: Boolean, default: false },
        supervisor: String, reference: String, verifiedAt: Date, verifiedBy: String, verificationHash: String
    }],

    qualifications: [{
        degree: String, institution: String, yearObtained: Number, country: { type: String, default: 'South Africa' },
        classification: String, certificateHash: String, verifiedAt: Date, verifiedBy: String
    }],

    disciplinaryHistory: [{
        caseNumber: String, allegation: String, finding: String, sanction: String,
        imposedAt: Date, resolvedAt: Date, status: { type: String, enum: ['PENDING', 'UNDER_INVESTIGATION', 'RESOLVED', 'APPEALED'] },
        notes: String, recordedBy: String, recordedAt: { type: Date, default: Date.now }
    }],

    auditTrail: [{
        action: String, performedBy: String, performedAt: { type: Date, default: Date.now },
        ipAddress: String, userAgent: String, changes: Schema.Types.Mixed,
        previousState: Schema.Types.Mixed, newState: Schema.Types.Mixed,
        hash: { type: String, default: function() { return crypto.createHash('sha3-512').update(`${this.action}:${this.performedAt.toISOString()}:${this.performedBy}:${JSON.stringify(this.changes)}`).digest('hex'); } }
    }],

    integrityHash: { type: String, unique: true, default: function() { return crypto.createHash('sha3-512').update(`${this.lpcNumber}:${this.personalInfo.idNumber}:${this.updatedAt || Date.now()}`).digest('hex'); } },
    quantumSignature: { type: String, default: function() { return crypto.createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026').update(`${this._id}:${this.lpcNumber}:${this.integrityHash}`).digest('hex'); } },

    status: { type: String, enum: Object.values(ATTORNEY_STATUS), default: 'ACTIVE', index: true },
    statusReason: String,
    statusChangedAt: Date,
    statusChangedBy: String,

    createdBy: { type: String, required: true, immutable: true },
    createdAt: { type: Date, default: Date.now, immutable: true, index: true },
    updatedBy: { type: String, required: true },
    updatedAt: { type: Date, default: Date.now },

    retentionPolicy: { type: String, default: 'companies_act_20_years' },
    retentionStart: { type: Date, default: Date.now, immutable: true },
    retentionExpiry: { type: Date, default: function() { const d = new Date(); d.setFullYear(d.getFullYear() + 20); return d; }, index: true },
    dataResidency: { type: String, default: 'ZA', enum: ['ZA', 'EU', 'US', 'AU', 'UK'] },

    deleted: { type: Boolean, default: false, index: true },
    deletedAt: Date,
    deletedBy: String,
    deletionReason: String,
    deletionAuthorization: String
}, { timestamps: true, toJSON: { virtuals: true, transform: function(doc, ret) { delete ret.__v; delete ret.auditTrail; delete ret.integrityHash; delete ret.quantumSignature; delete ret.personalInfo.idNumber; delete ret.contact.phone; delete ret.contact.email; return redactSensitiveData(ret); } } });

attorneyProfileSchema.virtual('fullAddress').get(function() { const a = this.address?.physical; return a ? `${a.line1}, ${a.suburb}, ${a.city}, ${a.province}, ${a.postalCode}` : ''; });
attorneyProfileSchema.virtual('isFidelityValid').get(function() { return this.fidelityFund?.status === 'ACTIVE' && this.fidelityFund?.expiryDate > new Date(); });
attorneyProfileSchema.virtual('isTrustCompliant').get(function() { return this.trustAccount?.isActive === true && this.trustAccount?.complianceScore >= 70; });
attorneyProfileSchema.virtual('isCPDCompliant').get(function() { return this.cpd?.complianceStatus === 'COMPLIANT'; });
attorneyProfileSchema.virtual('daysUntilFidelityExpiry').get(function() { return this.fidelityFund?.expiryDate ? Math.ceil((this.fidelityFund.expiryDate - Date.now()) / (1000 * 60 * 60 * 24)) : null; });
attorneyProfileSchema.virtual('complianceScore').get(function() { let s = 100; if (!this.isFidelityValid) s -= 30; if (!this.isTrustCompliant) s -= 25; if (!this.isCPDCompliant) s -= 20; if (this.disciplinaryHistory?.length > 0) s -= 15; return Math.max(0, s); });

attorneyProfileSchema.index({ tenantId: 1, lpcNumber: 1 }, { unique: true });
attorneyProfileSchema.index({ tenantId: 1, status: 1, 'fidelityFund.expiryDate': 1 });
attorneyProfileSchema.index({ tenantId: 1, 'cpd.complianceStatus': 1, 'cpd.currentYear': 1 });
attorneyProfileSchema.index({ tenantId: 1, 'practice.type': 1, 'practice.area': 1 });
attorneyProfileSchema.index({ deleted: 1, retentionExpiry: 1 });
attorneyProfileSchema.index({ integrityHash: 1 }, { unique: true });

attorneyProfileSchema.pre('save', async function(next) {
    try {
        if (!this.tenantId) throw new Error('TENANT_ISOLATION_VIOLATION: Attorney profile requires tenantId');
        if (this.practice?.commencementDate) this.practice.yearsOfPractice = Math.floor((Date.now() - this.practice.commencementDate) / (1000 * 60 * 60 * 24 * 365));
        this.integrityHash = crypto.createHash('sha3-512').update(`${this.lpcNumber}:${this.personalInfo?.idNumber}:${Date.now()}`).digest('hex');
        if (this.isNew) this.auditTrail.push({ action: 'ATTORNEY_PROFILE_CREATED', performedBy: this.createdBy, performedAt: new Date(), changes: { lpcNumber: this.lpcNumber, practiceName: this.practice?.name } });
        else this.auditTrail.push({ action: 'ATTORNEY_PROFILE_UPDATED', performedBy: this.updatedBy, performedAt: new Date() });
        next();
    } catch (error) { next(error); }
});

attorneyProfileSchema.statics = {
    async findActiveWithFidelity(tenantId) { return this.find({ tenantId, status: 'ACTIVE', deleted: false, 'fidelityFund.status': 'ACTIVE', 'fidelityFund.expiryDate': { $gt: new Date() } }).sort({ 'fidelityFund.expiryDate': 1 }); },
    async findCPDNonCompliant(tenantId, y = new Date().getFullYear()) { return this.find({ tenantId, status: 'ACTIVE', deleted: false, 'cpd.currentYear': y, 'cpd.complianceStatus': { $ne: 'COMPLIANT' } }); },
    async findRequiringReconciliation(tenantId) { return this.find({ tenantId, status: 'ACTIVE', deleted: false, 'trustAccount.isActive': true, 'trustAccount.nextReconciliationDue': { $lte: new Date() } }); },
    async search(tenantId, q) { return this.find({ tenantId, deleted: false, $or: [{ lpcNumber: new RegExp(q, 'i') }, { 'personalInfo.fullName': new RegExp(q, 'i') }, { 'practice.name': new RegExp(q, 'i') }] }).limit(50); }
};

attorneyProfileSchema.methods = {
    canPractice() { return this.status === 'ACTIVE' && this.isFidelityValid === true && !this.deleted; },
    async calculateComplianceScore() { let s = 100; if (!this.isFidelityValid) s -= 30; if (!this.trustAccount?.isActive) s -= 25; else if (this.trustAccount.complianceScore < 70) s -= 15; if (this.cpd.complianceStatus !== 'COMPLIANT') s -= 20; if (this.disciplinaryHistory) { s -= this.disciplinaryHistory.filter(d => ['PENDING', 'UNDER_INVESTIGATION'].includes(d.status)).length * 15; } return Math.max(0, Math.min(100, s)); },
    async updateCPDStatus(h, e, uid) { this.cpd.hoursCompleted += h; this.cpd.ethicsHours += e; this.cpd.lastSubmissionDate = new Date(); if (this.cpd.hoursCompleted >= 12 && this.cpd.ethicsHours >= 2) { this.cpd.complianceStatus = 'COMPLIANT'; this.cpd.verifiedAt = new Date(); this.cpd.verifiedBy = uid; } this.updatedBy = uid; await this.save(); return { hoursCompleted: this.cpd.hoursCompleted, ethicsHours: this.cpd.ethicsHours, complianceStatus: this.cpd.complianceStatus, remainingHours: Math.max(0, 12 - this.cpd.hoursCompleted), remainingEthics: Math.max(0, 2 - this.cpd.ethicsHours) }; },
    async updateFidelityCertificate(fd, uid) { this.fidelityFund = { ...this.fidelityFund, ...fd, status: 'ACTIVE', issueDate: new Date(), expiryDate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000) }; this.fidelityFund.verificationHash = crypto.createHash('sha3-512').update(`${this.lpcNumber}:${this.fidelityFund.certificateNumber}:${Date.now()}`).digest('hex'); this.updatedBy = uid; await this.save(); return { certificateNumber: this.fidelityFund.certificateNumber, issueDate: this.fidelityFund.issueDate, expiryDate: this.fidelityFund.expiryDate, status: this.fidelityFund.status, verificationHash: this.fidelityFund.verificationHash }; },
    async generateAuditReport() { const cs = await this.calculateComplianceScore(); return { attorneyId: this._id, lpcNumber: this.lpcNumber, practiceName: this.practice.name, status: this.status, createdAt: this.createdAt, updatedAt: this.updatedAt, createdBy: this.createdBy, updatedBy: this.updatedBy, compliance: { score: cs, fidelityValid: this.isFidelityValid, fidelityExpiry: this.fidelityFund?.expiryDate, trustCompliant: this.isTrustCompliant, cpdCompliant: this.isCPDCompliant, cpdHours: this.cpd.hoursCompleted, cpdEthics: this.cpd.ethicsHours }, retention: { policy: this.retentionPolicy, expiryDate: this.retentionExpiry, daysRemaining: Math.ceil((this.retentionExpiry - Date.now()) / (1000 * 60 * 60 * 24)) }, integrity: { hash: this.integrityHash, signature: this.quantumSignature }, auditTrail: this.auditTrail.slice(-10), generatedAt: new Date().toISOString(), generatedBy: 'WilsyOS Attorney Forensic Engine v5.0.1' }; }
};

module.exports = mongoose.model('AttorneyProfile', attorneyProfileSchema);
