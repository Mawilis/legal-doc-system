/* eslint-disable */
/**
 * 🏛️ WILSYS OS - CPD RECORD MODEL
 * LEGAL PRACTICE COUNCIL · CONTINUING PROFESSIONAL DEVELOPMENT
 * Standard: ES Module (Surgically Standardized)
 * @version 5.0.1
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';
import { v4 as uuidv4 } from 'uuid';

const { Schema } = mongoose;

export const CPD_CATEGORIES = {
    SUBSTANTIVE: 'SUBSTANTIVE', ETHICS: 'ETHICS', PRACTICE_MANAGEMENT: 'PRACTICE_MANAGEMENT',
    PROFESSIONAL_SKILLS: 'PROFESSIONAL_SKILLS', ADVOCACY: 'ADVOCACY', DRAFTING: 'DRAFTING',
    NEGOTIATION: 'NEGOTIATION', MEDIATION: 'MEDIATION', ARBITRATION: 'ARBITRATION',
    TECHNOLOGY: 'TECHNOLOGY', LEGAL_RESEARCH: 'LEGAL_RESEARCH', CLIENT_CARE: 'CLIENT_CARE',
    RISK_MANAGEMENT: 'RISK_MANAGEMENT', FINANCIAL_MANAGEMENT: 'FINANCIAL_MANAGEMENT'
};

export const CPD_STATUS = {
    PENDING_VERIFICATION: 'PENDING_VERIFICATION', VERIFIED: 'VERIFIED', REJECTED: 'REJECTED',
    EXPIRED: 'EXPIRED', CANCELLED: 'CANCELLED', AUTO_VERIFIED: 'AUTO_VERIFIED', UNDER_REVIEW: 'UNDER_REVIEW'
};

export const PROVIDER_TYPES = {
    LPC_ACCREDITED: 'LPC_ACCREDITED', UNIVERSITY: 'UNIVERSITY', LAW_SOCIETY: 'LAW_SOCIETY',
    BAR_COUNCIL: 'BAR_COUNCIL', PRIVATE_PROVIDER: 'PRIVATE_PROVIDER', IN_HOUSE: 'IN_HOUSE',
    INTERNATIONAL: 'INTERNATIONAL', WEBINAR: 'WEBINAR', CONFERENCE: 'CONFERENCE', WORKSHOP: 'WORKSHOP'
};

export const VERIFICATION_METHODS = {
    MANUAL: 'MANUAL', AUTOMATED: 'AUTOMATED', BLOCKCHAIN: 'BLOCKCHAIN',
    LPC_API: 'LPC_API', PROVIDER_API: 'PROVIDER_API', CERTIFICATE_SCAN: 'CERTIFICATE_SCAN', QR_CODE: 'QR_CODE'
};

export const ACCREDITATION_LEVELS = {
    FULL: 'FULL', PROVISIONAL: 'PROVISIONAL', EXPIRED: 'EXPIRED', SUSPENDED: 'SUSPENDED', REVOKED: 'REVOKED'
};

const cpdRecordSchema = new Schema({
    tenantId: {
        type: String,
        required: [true, 'TENANT_ISOLATION_VIOLATION: tenantId is required'],
        index: true, immutable: true,
        validate: { validator: v => /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(v) }
    },
    activityId: { type: String, required: true, unique: true, default: () => `CPD-${uuidv4()}`, immutable: true, index: true },
    attorneyId: { type: Schema.Types.ObjectId, ref: 'AttorneyProfile', required: true, index: true },
    attorneyLpcNumber: { type: String, required: true, index: true, validate: { validator: v => /^(LPC-\d{8}|\d{4}\/\d{4})$/.test(v) } },
    firmId: { type: Schema.Types.ObjectId, ref: 'Firm', required: true, index: true },
    activityName: { type: String, required: true, trim: true, maxlength: 500 },
    activityDescription: { type: String, trim: true, maxlength: 2000 },
    activityDate: { type: Date, required: true, index: true, validate: { validator: v => v.getFullYear() >= 2020 && v.getFullYear() <= new Date().getFullYear() } },
    year: { type: Number, required: true, default: function () { return this.activityDate.getFullYear(); }, index: true, min: 2020, max: new Date().getFullYear() },
    hours: { type: Number, required: true, min: 0.5, max: 8, validate: { validator: v => v % 0.5 === 0 } },
    category: { type: String, required: true, enum: Object.values(CPD_CATEGORIES), index: true },
    subcategory: { type: String, enum: ['PROFESSIONAL_ETHICS', 'PRACTICE_STANDARDS', 'CLIENT_CARE', 'RISK_MANAGEMENT', 'FINANCIAL_MANAGEMENT', 'INFORMATION_TECHNOLOGY', 'COMMUNICATION_SKILLS', 'LEGAL_RESEARCH', 'ADVOCACY_SKILLS', 'DRAFTING_SKILLS', 'ALTERNATIVE_DISPUTE_RESOLUTION', 'SPECIALIST_AREAS', 'LEGISLATIVE_UPDATE', 'CASE_LAW_UPDATE'] },
    provider: {
        name: { type: String, required: true, trim: true, maxlength: 200 },
        type: { type: String, required: true, enum: Object.values(PROVIDER_TYPES) },
        accreditationNumber: { type: String, validate: { validator: v => !v || /^LPC-ACC-\d{6}$|^LPC-\d{4}-\d{4}$/i.test(v) } },
        accreditationLevel: { type: String, enum: Object.values(ACCREDITATION_LEVELS) },
        accreditationExpiry: { type: Date, validate: { validator: v => !v || v > new Date() } },
        website: String, contactEmail: String, contactPhone: String,
        verificationEndpoint: String,
        providerHash: { type: String, default: function () { return crypto.createHash('sha3-512').update(`${this.provider.name}:${this.provider.accreditationNumber || 'N/A'}`).digest('hex').substring(0, 16); } }
    },
    evidence: {
        certificateUrl: { type: String, required: true, validate: { validator: v => /^https?:\/\/.+\..+/.test(v) } },
        certificateHash: { type: String, required: true, validate: { validator: v => /^[a-f0-9]{64}$/i.test(v) } },
        evidenceUrls: [{ url: String, description: String, uploadedAt: { type: Date, default: Date.now } }],
        attendanceProof: String,
        assessmentScore: { type: Number, min: 0, max: 100 },
        assessmentPassed: { type: Boolean, default: function () { return this.assessmentScore >= 70; } },
        completionDate: { type: Date, required: true, validate: { validator: v => v <= new Date() } }
    },
    verificationCode: { type: String, unique: true, sparse: true, default: () => crypto.randomBytes(16).toString('hex').toUpperCase() },
    verificationStatus: { type: String, enum: Object.values(CPD_STATUS), default: 'PENDING_VERIFICATION', index: true },
    verificationMethod: { type: String, enum: Object.values(VERIFICATION_METHODS) },
    verifiedBy: { type: Schema.Types.ObjectId, ref: 'User' },
    verifiedAt: Date, verificationNotes: String, rejectionReason: String,
    accreditation: {
        isLpcAccredited: { type: Boolean, default: false },
        accreditationReference: String,
        qualityAssuranceScore: { type: Number, min: 0, max: 100 },
        peerReviewed: { type: Boolean, default: false },
        reviewerComments: String, reviewedAt: Date, reviewedBy: String
    },
    learningOutcomes: { type: String, maxlength: 2000 },
    keyTakeaways: [{ type: String, maxlength: 500 }],
    practicalApplication: { type: String, maxlength: 2000 },
    relevanceScore: { type: Number, min: 1, max: 5, default: 3 },
    compliance: {
        countsTowardsAnnual: { type: Boolean, default: true },
        countsTowardsEthics: { type: Boolean, default: function () { return this.category === 'ETHICS'; } },
        rolloverEligible: { type: Boolean, default: function () { return this.hours <= 6 && ['VERIFIED', 'AUTO_VERIFIED'].includes(this.verificationStatus) && this.compliance.countsTowardsAnnual === true; } },
        rolloverYear: { type: Number, validate: { validator: v => !v || v > this.year } },
        rolloverHours: { type: Number, min: 0, max: 6, validate: { validator: v => !v || v <= this.hours } },
        appliedToYear: Number
    },
    cost: { amount: { type: Number, min: 0, default: 0, get: v => parseFloat(v.toFixed(2)) }, currency: { type: String, default: 'ZAR', enum: ['ZAR', 'USD', 'EUR', 'GBP'] }, paidBy: { type: String, enum: ['ATTORNEY', 'FIRM', 'SCHOLARSHIP', 'PRO_BONO', 'EMPLOYER'] }, receiptUrl: String, receiptHash: String, taxDeductible: { type: Boolean, default: false } },
    blockchain: { anchorId: { type: String, sparse: true, unique: true }, transactionHash: { type: String, sparse: true }, blockNumber: Number, timestamp: Date, verified: { type: Boolean, default: false }, verificationUrl: String },
    quantumSignature: { type: String, required: true, default: function () { const p = [this.activityId, this.attorneyLpcNumber, this.hours, this.category, this.activityDate.toISOString(), this.verificationCode || 'PENDING', this.evidence.certificateHash].join(':'); return crypto.createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026').update(p).digest('hex'); } },
    forensicHash: { type: String, required: true, unique: true, default: function () { return crypto.createHash('sha3-512').update([this.activityId, this.attorneyLpcNumber, this.hours.toFixed(1), this.category, this.activityDate.toISOString(), this.provider.name, this.evidence.certificateHash, this.verificationCode || 'PENDING', this.year.toString()].join(':')).digest('hex'); } },
    integrityHash: { type: String, unique: true, default: function () { return crypto.createHash('sha3-512').update(`${this._id || this.activityId}:${this.forensicHash}:${Date.now()}`).digest('hex'); } },
    auditTrail: [{ action: { type: String, enum: ['SUBMITTED', 'VERIFIED', 'REJECTED', 'UPDATED', 'EXPIRED', 'ROLLED_OVER', 'CERTIFICATE_GENERATED', 'BLOCKCHAIN_ANCHORED', 'AUTO_VERIFIED'] }, performedBy: String, performedAt: { type: Date, default: Date.now }, ipAddress: String, userAgent: String, changes: Schema.Types.Mixed, previousState: Schema.Types.Mixed, newState: Schema.Types.Mixed, hash: { type: String, default: function () { return crypto.createHash('sha3-512').update(`${this.action}:${this.performedAt.toISOString()}:${this.performedBy}:${JSON.stringify(this.changes)}`).digest('hex'); } } }],
    submissionDate: { type: Date, default: Date.now, immutable: true, index: true },
    submittedBy: { type: String, required: true, immutable: true },
    lastUpdatedBy: String,
    complianceCertificate: { certificateId: { type: String, sparse: true, unique: true }, issuedAt: Date, expiresAt: Date, certificateHash: String, digitalSignature: String, verificationUrl: String, verificationQR: String, pdfUrl: String },
    certificateGenerated: { type: Boolean, default: false },
    certificateGeneratedAt: Date,
    retentionPolicy: { type: String, default: 'companies_act_7_years' },
    retentionStart: { type: Date, default: Date.now, immutable: true },
    retentionExpiry: { type: Date, default: function () { const d = new Date(); d.setFullYear(d.getFullYear() + 7); return d; }, index: true },
    dataResidency: { type: String, default: 'ZA', enum: ['ZA', 'EU', 'US', 'AU', 'UK'] },
    deleted: { type: Boolean, default: false, index: true },
    deletedAt: Date, deletedBy: String, deletionReason: String, deletionAuthorization: String
}, { timestamps: true, toJSON: { virtuals: true, transform: function (doc, ret) { delete ret.__v; delete ret.auditTrail; delete ret.quantumSignature; delete ret.forensicHash; delete ret.integrityHash; delete ret.evidence.certificateUrl; delete ret.blockchain; return ret; } } });

cpdRecordSchema.virtual('daysSinceSubmission').get(function () { return Math.floor((Date.now() - this.submissionDate) / (1000 * 60 * 60 * 24)); });
cpdRecordSchema.virtual('isVerified').get(function () { return ['VERIFIED', 'AUTO_VERIFIED'].includes(this.verificationStatus); });
cpdRecordSchema.virtual('isExpired').get(function () { return this.verificationStatus === 'EXPIRED' || (this.compliance.rolloverYear && this.compliance.rolloverYear < new Date().getFullYear() - 1); });
cpdRecordSchema.virtual('isEthics').get(function () { return this.category === 'ETHICS'; });
cpdRecordSchema.virtual('isSubstantive').get(function () { return this.category === 'SUBSTANTIVE'; });
cpdRecordSchema.virtual('verificationProgress').get(function () { if (this.isVerified) return 100; if (this.verificationStatus === 'REJECTED') return 0; let p = 0; if (this.evidence.certificateHash) p += 25; if (this.verificationCode) p += 25; if (this.provider.accreditationNumber) p += 25; if (this.blockchain?.verified) p += 25; if (this.accreditation.isLpcAccredited) p += 15; return Math.min(100, p); });
cpdRecordSchema.virtual('complianceStatus').get(function () { if (this.isVerified) { if (this.category === 'ETHICS' && this.hours >= 2) return 'ETHICS_COMPLIANT'; return 'HOURS_VERIFIED'; } return 'PENDING_VERIFICATION'; });
cpdRecordSchema.virtual('yearsValidFor').get(function () { return this.compliance.rolloverYear ? this.compliance.rolloverYear - this.year : 1; });

cpdRecordSchema.index({ tenantId: 1, attorneyId: 1, year: -1, activityDate: -1 });
cpdRecordSchema.index({ tenantId: 1, verificationStatus: 1, year: 1 });
cpdRecordSchema.index({ tenantId: 1, category: 1, year: 1 });
cpdRecordSchema.index({ tenantId: 1, 'provider.accreditationNumber': 1 });
cpdRecordSchema.index({ forensicHash: 1 }, { unique: true });
cpdRecordSchema.index({ integrityHash: 1 }, { unique: true });
cpdRecordSchema.index({ verificationCode: 1 }, { unique: true, sparse: true });
cpdRecordSchema.index({ 'blockchain.anchorId': 1 }, { sparse: true });
cpdRecordSchema.index({ 'compliance.rolloverYear': 1, 'compliance.rolloverHours': 1 });
cpdRecordSchema.index({ deleted: 1, retentionExpiry: 1 });
cpdRecordSchema.index({ attorneyLpcNumber: 1, year: 1, verificationStatus: 1 });

cpdRecordSchema.pre('save', async function (next) {
    try {
        if (!this.tenantId) throw new Error('TENANT_ISOLATION_VIOLATION: CPD record requires tenantId');
        if (this.activityDate && !this.year) this.year = this.activityDate.getFullYear();
        if (this.category === 'ETHICS' && this.hours < 1) throw new Error('ETHICS_HOURS_VIOLATION: Ethics CPD must be at least 1 hour');
        if (this.hours > 8) throw new Error('HOURS_LIMIT_VIOLATION: Single CPD activity cannot exceed 8 hours');
        if (this.provider.accreditationNumber && this.provider.accreditationExpiry && this.provider.accreditationExpiry > new Date() && this.verificationStatus === 'PENDING_VERIFICATION') {
            this.verificationStatus = 'AUTO_VERIFIED'; this.verificationMethod = 'AUTOMATED'; this.verifiedAt = new Date(); this.accreditation.isLpcAccredited = true; this.accreditation.accreditationReference = this.provider.accreditationNumber;
        }
        if (!this.forensicHash) this.forensicHash = crypto.createHash('sha3-512').update([this.activityId, this.attorneyLpcNumber, this.hours.toFixed(1), this.category, this.activityDate.toISOString(), this.provider.name, this.evidence.certificateHash, this.verificationCode || 'PENDING', this.year.toString()].join(':')).digest('hex');
        this.integrityHash = crypto.createHash('sha3-512').update(`${this._id || this.activityId}:${this.forensicHash}:${Date.now()}`).digest('hex');
        const payload = [this.activityId, this.attorneyLpcNumber, this.hours, this.category, this.activityDate.toISOString(), this.verificationCode || 'PENDING', this.evidence.certificateHash].join(':');
        this.quantumSignature = crypto.createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026').update(payload).digest('hex');
        if (this.isNew) this.auditTrail.push({ action: 'SUBMITTED', performedBy: this.submittedBy, performedAt: new Date(), changes: { activityName: this.activityName, hours: this.hours, category: this.category, provider: this.provider.name } });
        else this.auditTrail.push({ action: 'UPDATED', performedBy: this.lastUpdatedBy || this.submittedBy, performedAt: new Date() });
        next();
    } catch (error) { next(error); }
});

cpdRecordSchema.statics = {
    async getAttorneySummary(attorneyId, tenantId, year = new Date().getFullYear()) {
        const records = await this.find({ attorneyId, tenantId, year, verificationStatus: { $in: ['VERIFIED', 'AUTO_VERIFIED'] }, 'compliance.countsTowardsAnnual': true, deleted: false });
        const totalHours = records.reduce((s, r) => s + r.hours, 0);
        const ethicsHours = records.filter(r => r.category === 'ETHICS').reduce((s, r) => s + r.hours, 0);
        const prevRecords = await this.find({ attorneyId, tenantId, year: year - 1, verificationStatus: { $in: ['VERIFIED', 'AUTO_VERIFIED'] }, 'compliance.rolloverEligible': true, deleted: false });
        const prevHours = prevRecords.reduce((s, r) => s + r.hours, 0);
        const rolloverHours = Math.min(Math.max(0, prevHours - 12), 6);
        const effectiveHours = totalHours + rolloverHours;
        const isCompliant = effectiveHours >= 12 && ethicsHours >= 2;
        const deadline = new Date(year, 11, 31);
        return {
            attorneyId, tenantId, year,
            summary: { totalHours: parseFloat(totalHours.toFixed(1)), ethicsHours: parseFloat(ethicsHours.toFixed(1)), rolloverHours: parseFloat(rolloverHours.toFixed(1)), effectiveHours: parseFloat(effectiveHours.toFixed(1)), recordsCount: records.length },
            requirements: { hoursRequired: 12, ethicsRequired: 2, hoursRemaining: parseFloat(Math.max(0, 12 - effectiveHours).toFixed(1)), ethicsRemaining: parseFloat(Math.max(0, 2 - ethicsHours).toFixed(1)) },
            compliance: { isCompliant, status: isCompliant ? 'COMPLIANT' : (effectiveHours >= 10 || ethicsHours >= 1 ? 'WARNING' : 'NON_COMPLIANT'), isOverdue: Date.now() > deadline && !isCompliant, deadline: deadline.toISOString(), daysUntilDeadline: Math.ceil((deadline - Date.now()) / (1000 * 60 * 60 * 24)) },
            breakdown: records.map(r => ({ activityId: r.activityId, activityName: r.activityName, activityDate: r.activityDate, hours: r.hours, category: r.category, provider: r.provider.name, verificationStatus: r.verificationStatus, verifiedAt: r.verifiedAt, certificateGenerated: r.certificateGenerated })),
            generatedAt: new Date().toISOString()
        };
    },
    async findNonCompliant(tenantId, year = new Date().getFullYear()) {
        const attorneys = await mongoose.model('AttorneyProfile').find({ tenantId, status: 'ACTIVE', 'cpd.complianceStatus': { $ne: 'COMPLIANT' }, deleted: false }).select('_id lpcNumber practice.name contact.email');
        const nonCompliant = [];
        for (const a of attorneys) { const s = await this.getAttorneySummary(a._id, tenantId, year); if (!s.compliance.isCompliant) nonCompliant.push({ attorneyId: a._id, lpcNumber: a.lpcNumber, practiceName: a.practice?.name, email: a.contact?.email, ...s.summary, ...s.requirements, ...s.compliance }); }
        return nonCompliant;
    },
    async getProviderStats(tenantId, year = new Date().getFullYear()) {
        return this.aggregate([{ $match: { tenantId, year, verificationStatus: { $in: ['VERIFIED', 'AUTO_VERIFIED'] }, deleted: false } }, { $group: { _id: { name: '$provider.name', type: '$provider.type', accreditationNumber: '$provider.accreditationNumber' }, totalHours: { $sum: '$hours' }, totalActivities: { $sum: 1 }, ethicsHours: { $sum: { $cond: [{ $eq: ['$category', 'ETHICS'] }, '$hours', 0] } }, averageHours: { $avg: '$hours' }, verifiedCount: { $sum: 1 }, autoVerifiedCount: { $sum: { $cond: [{ $eq: ['$verificationStatus', 'AUTO_VERIFIED'] }, 1, 0] } }, averageScore: { $avg: '$accreditation.qualityAssuranceScore' } } }, { $project: { providerName: '$_id.name', providerType: '$_id.type', accreditationNumber: '$_id.accreditationNumber', totalHours: { $round: ['$totalHours', 1] }, totalActivities: 1, ethicsHours: { $round: ['$ethicsHours', 1] }, averageHours: { $round: ['$averageHours', 1] }, verifiedCount: 1, autoVerifyRate: { $round: [{ $multiply: [{ $divide: ['$autoVerifiedCount', '$verifiedCount'] }, 100] }, 1] }, averageScore: { $round: ['$averageScore', 0] } } }, { $sort: { totalHours: -1 } }]);
    },
    async getComplianceTrends(attorneyId, tenantId, years = 5) {
        const y = new Date().getFullYear(), t = [];
        for (let i = y - years + 1; i <= y; i++) t.push({ year: i, ...(await this.getAttorneySummary(attorneyId, tenantId, i)).summary, ...(await this.getAttorneySummary(attorneyId, tenantId, i)).compliance });
        return t;
    }
};

cpdRecordSchema.methods = {
    async verify(userId, method = 'MANUAL', notes = '') {
        if (this.isVerified) throw new Error('CPD_ALREADY_VERIFIED');
        this.verificationStatus = 'VERIFIED'; this.verificationMethod = method; this.verifiedBy = userId; this.verifiedAt = new Date(); this.verificationNotes = notes;
        if (!this.certificateGenerated) await this.generateCertificate();
        this.auditTrail.push({ action: 'VERIFIED', performedBy: userId, performedAt: new Date(), changes: { method, notes } });
        await this.save();
        const AttorneyProfile = mongoose.model('AttorneyProfile');
        const attorney = await AttorneyProfile.findById(this.attorneyId);
        if (attorney) { const s = await this.constructor.getAttorneySummary(this.attorneyId, this.tenantId, this.year); attorney.cpd.hoursCompleted = s.summary.totalHours; attorney.cpd.ethicsHours = s.summary.ethicsHours; attorney.cpd.complianceStatus = s.compliance.isCompliant ? 'COMPLIANT' : 'NON_COMPLIANT'; attorney.cpd.lastSubmissionDate = new Date(); attorney.cpd.verifiedAt = new Date(); attorney.cpd.verifiedBy = userId; await attorney.save(); }
        return { success: true, activityId: this.activityId, verifiedAt: this.verifiedAt, verifiedBy: userId, method, certificateGenerated: this.certificateGenerated, certificateId: this.complianceCertificate?.certificateId };
    },
    async reject(userId, reason) {
        if (this.isVerified) throw new Error('CPD_ALREADY_VERIFIED');
        this.verificationStatus = 'REJECTED'; this.rejectionReason = reason; this.verifiedBy = userId; this.verifiedAt = new Date();
        this.auditTrail.push({ action: 'REJECTED', performedBy: userId, performedAt: new Date(), changes: { reason } });
        await this.save();
        return { success: true, activityId: this.activityId, rejectedAt: this.verifiedAt, rejectedBy: userId, reason };
    },
    async generateCertificate() {
        if (this.certificateGenerated) return { success: false, message: 'Certificate already generated', certificateId: this.complianceCertificate?.certificateId };
        if (!this.isVerified) throw new Error('CERTIFICATE_VERIFICATION_REQUIRED');
        const certificateId = `CPD-CERT-${this.year}-LPC-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
        const issuedAt = new Date(), expiresAt = new Date(this.year + 1, 11, 31);
        const certificateHash = crypto.createHash('sha3-512').update([certificateId, this.forensicHash, issuedAt.toISOString(), this.attorneyLpcNumber, this.hours.toString(), this.category].join(':')).digest('hex');
        const digitalSignature = crypto.createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026').update(`${certificateId}:${this.forensicHash}:${issuedAt.toISOString()}`).digest('hex');
        this.complianceCertificate = { certificateId, issuedAt, expiresAt, certificateHash, digitalSignature, verificationUrl: `https://verify.wilsyos.co.za/cpd/${certificateId}`, verificationQR: `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${certificateId}`, pdfUrl: `https://certificates.wilsyos.co.za/cpd/${certificateId}.pdf` };
        this.certificateGenerated = true; this.certificateGeneratedAt = issuedAt;
        this.auditTrail.push({ action: 'CERTIFICATE_GENERATED', performedBy: this.verifiedBy || 'SYSTEM', performedAt: new Date(), changes: { certificateId, expiresAt } });
        await this.save();
        return { success: true, certificateId, certificate: this.complianceCertificate };
    },
    async anchorToBlockchain() {
        if (this.blockchain?.verified) return { success: false, message: 'Already anchored to blockchain', anchorId: this.blockchain.anchorId };
        if (!this.isVerified) throw new Error('BLOCKCHAIN_VERIFICATION_REQUIRED');
        const anchorId = `OTS-${crypto.randomBytes(8).toString('hex').toUpperCase()}`;
        const transactionHash = crypto.createHash('sha3-512').update(`${anchorId}:${this.forensicHash}:${Date.now()}`).digest('hex');
        this.blockchain = { anchorId, transactionHash, blockNumber: Math.floor(Date.now() / 1000), timestamp: new Date(), network: 'PRIVATE', verified: true, verificationUrl: `https://verify.wilsyos.co.za/blockchain/${anchorId}` };
        this.auditTrail.push({ action: 'BLOCKCHAIN_ANCHORED', performedBy: 'SYSTEM', performedAt: new Date(), changes: { anchorId, transactionHash } });
        await this.save();
        return { success: true, anchorId, transactionHash, timestamp: this.blockchain.timestamp, verificationUrl: this.blockchain.verificationUrl };
    },
    async rollover(userId) {
        if (!this.compliance.rolloverEligible) throw new Error('ROLLOVER_INELIGIBLE');
        const excess = this.hours - 12; if (excess <= 0) throw new Error('ROLLOVER_NOT_REQUIRED');
        const rolloverHours = Math.min(excess, 6), rolloverYear = this.year + 1;
        this.compliance.rolloverHours = parseFloat(rolloverHours.toFixed(1)); this.compliance.rolloverYear = rolloverYear; this.compliance.appliedToYear = rolloverYear; this.verificationStatus = 'EXPIRED';
        this.auditTrail.push({ action: 'ROLLED_OVER', performedBy: userId, performedAt: new Date(), changes: { rolloverHours, rolloverYear } });
        await this.save();
        return { success: true, activityId: this.activityId, originalHours: this.hours, rolloverHours, rolloverYear, appliedToYear: rolloverYear };
    },
    async generateAuditReport() {
        const s = await this.constructor.getAttorneySummary(this.attorneyId, this.tenantId, this.year);
        return {
            activityId: this.activityId, attorneyLpcNumber: this.attorneyLpcNumber, activityName: this.activityName, activityDate: this.activityDate, hours: this.hours, category: this.category,
            provider: this.provider.name, providerType: this.provider.type, accreditationNumber: this.provider.accreditationNumber,
            verificationStatus: this.verificationStatus, verificationMethod: this.verificationMethod, verifiedAt: this.verifiedAt, verifiedBy: this.verifiedBy,
            submittedBy: this.submittedBy, submissionDate: this.submissionDate,
            compliance: { countsTowardsAnnual: this.compliance.countsTowardsAnnual, countsTowardsEthics: this.compliance.countsTowardsEthics, rolloverEligible: this.compliance.rolloverEligible, rolloverHours: this.compliance.rolloverHours, rolloverYear: this.compliance.rolloverYear },
            certificate: { generated: this.certificateGenerated, certificateId: this.complianceCertificate?.certificateId, issuedAt: this.complianceCertificate?.issuedAt, expiresAt: this.complianceCertificate?.expiresAt },
            blockchain: { anchored: this.blockchain?.verified || false, anchorId: this.blockchain?.anchorId, timestamp: this.blockchain?.timestamp },
            attorneySummary: s,
            integrity: { forensicHash: this.forensicHash, integrityHash: this.integrityHash, quantumSignature: this.quantumSignature },
            auditTrail: this.auditTrail.slice(-10),
            retention: { policy: this.retentionPolicy, expiryDate: this.retentionExpiry, daysRemaining: Math.ceil((this.retentionExpiry - Date.now()) / (1000 * 60 * 60 * 24)) },
            generatedAt: new Date().toISOString(), generatedBy: 'WilsyOS CPD Forensic Engine v5.0.1'
        };
    },
    async updateVerificationStatus(status, userId, notes = '') {
        const old = this.verificationStatus; this.verificationStatus = status; this.verifiedBy = userId; this.verifiedAt = new Date(); this.verificationNotes = notes;
        this.auditTrail.push({ action: status === 'VERIFIED' ? 'VERIFIED' : 'UPDATED', performedBy: userId, performedAt: new Date(), changes: { oldStatus: old, newStatus: status, notes } });
        await this.save();
        return { success: true, activityId: this.activityId, oldStatus: old, newStatus: status, updatedAt: this.verifiedAt, updatedBy: userId };
    }
};

const CPDRecord = mongoose.model('CPDRecord', cpdRecordSchema);
export default CPDRecord;