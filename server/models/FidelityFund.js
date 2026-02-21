/* eslint-disable */
/**
 * 🏛️ WILSYS OS - FIDELITY FUND CERTIFICATE MODEL
 * Standard: ES Module (Surgically Standardized)
 * Forensic-Grade | LPC Rule 55 | $10B Infrastructure
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';

const { Schema } = mongoose;
const CERTIFICATE_STATUS = {
    PENDING: 'PENDING', ISSUED: 'ISSUED', RENEWED: 'RENEWED', EXPIRED: 'EXPIRED',
    REVOKED: 'REVOKED', SUSPENDED: 'SUSPENDED', CANCELLED: 'CANCELLED', REPLACED: 'REPLACED'
};

const PRACTICE_TYPES = {
    PRIVATE: 'PRIVATE', GOVERNMENT: 'GOVERNMENT', CORPORATE: 'CORPORATE',
    LEGAL_AID: 'LEGAL_AID', ACADEMIC: 'ACADEMIC', NON_PRACTICING: 'NON_PRACTICING',
    INTERNATIONAL: 'INTERNATIONAL', PRO_BONO_ONLY: 'PRO_BONO_ONLY'
};

const PRACTICE_AREAS = { URBAN: 'URBAN', RURAL: 'RURAL', PERI_URBAN: 'PERI_URBAN', REMOTE: 'REMOTE' };
const PAYMENT_STATUS = { PENDING: 'PENDING', PAID: 'PAID', OVERDUE: 'OVERDUE', WAIVED: 'WAIVED', REFUNDED: 'REFUNDED', PARTIAL: 'PARTIAL' };
const DISCOUNT_TYPES = {
    JUNIOR_ATTORNEY: 'JUNIOR_ATTORNEY', PRO_BONO: 'PRO_BONO', RURAL_PRACTICE: 'RURAL_PRACTICE',
    REMOTE_RURAL: 'REMOTE_RURAL', GOVERNMENT: 'GOVERNMENT', NON_PRACTICING: 'NON_PRACTICING',
    EARLY_PAYMENT: 'EARLY_PAYMENT', BULK_RENEWAL: 'BULK_RENEWAL', LONG_STANDING: 'LONG_STANDING',
    DISABILITY: 'DISABILITY', RETIRED: 'RETIRED'
};
const EXEMPTION_REASONS = { NON_PRACTICING: 'NON_PRACTICING', GOVERNMENT_EMPLOYEE: 'GOVERNMENT_EMPLOYEE', RETIRED: 'RETIRED', DECEASED: 'DECEASED', DISABILITY: 'DISABILITY', ACADEMIC_ONLY: 'ACADEMIC_ONLY', JUDICIAL_OFFICE: 'JUDICIAL_OFFICE' };
const VERIFICATION_METHODS = { LPC_API: 'LPC_API', BLOCKCHAIN: 'BLOCKCHAIN', QR_SCAN: 'QR_SCAN', MANUAL: 'MANUAL', CERTIFICATE_HASH: 'CERTIFICATE_HASH' };

const fidelityFundSchema = new Schema({
    tenantId: {
        type: String, required: [true, 'TENANT_ISOLATION_VIOLATION: tenantId is required'],
        index: true, immutable: true,
        validate: { validator: v => /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(v) }
    },
    certificateId: {
        type: String, required: true, unique: true, uppercase: true, immutable: true,
        default: () => `FFC-${new Date().getFullYear()}-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
        validate: { validator: v => /^FFC-\d{4}-[A-F0-9]{8}$/.test(v) }, index: true
    },
    attorneyId: { type: Schema.Types.ObjectId, ref: 'AttorneyProfile', required: true, index: true },
    attorneyLpcNumber: { type: String, required: true, index: true, validate: { validator: v => /^(LPC-\d{8}|\d{4}\/\d{4})$/.test(v) } },
    practiceNumber: { type: String, sparse: true, index: true, validate: { validator: v => !v || /^PRAC-\d{8}$/.test(v) } },
    firmId: { type: Schema.Types.ObjectId, ref: 'Firm', required: true, index: true },
    certificateData: { type: Schema.Types.Mixed, required: true, default: { version: '5.0.1', format: 'FFC-2026', issuer: 'Legal Practice Council Fidelity Fund', jurisdiction: 'Republic of South Africa' } },
    issueDate: { type: Date, required: true, default: Date.now, immutable: true, index: true },
    expiryDate: { type: Date, required: true, index: true, validate: { validator: v => v > this.issueDate } },
    status: { type: String, enum: Object.values(CERTIFICATE_STATUS), default: 'PENDING', index: true },
    statusHistory: [{ status: { type: String, enum: Object.values(CERTIFICATE_STATUS) }, changedAt: { type: Date, default: Date.now }, changedBy: String, reason: String, notes: String, authorization: String, ipAddress: String, userAgent: String }],
    contributionAmount: { type: Number, required: true, min: 0, max: 50000, get: v => parseFloat(v.toFixed(2)), set: v => parseFloat(v.toFixed(2)) },
    turnoverDeclared: { type: Number, required: true, min: 0, get: v => parseFloat(v.toFixed(2)) },
    baseContribution: { type: Number, required: true, min: 0, get: v => parseFloat(v.toFixed(2)) },
    discountAmount: { type: Number, default: 0, min: 0, get: v => parseFloat(v.toFixed(2)) },
    discountPercentage: { type: Number, default: 0, min: 0, max: 100 },
    discountReason: String,
    discounts: [{ type: { type: String, enum: Object.values(DISCOUNT_TYPES), required: true }, amount: { type: Number, get: v => parseFloat(v.toFixed(2)) }, percentage: { type: Number, min: 0, max: 100 }, reason: { type: String, required: true }, approvedBy: String, approvedAt: Date, approvalReference: String, expiresAt: Date, documentation: [String], verificationHash: String }],
    isExempt: { type: Boolean, default: false },
    exemptionReason: { type: String, enum: Object.values(EXEMPTION_REASONS) },
    exemptionCertificate: String,
    payment: {
        amount: { type: Number, required: true, get: v => parseFloat(v.toFixed(2)) },
        status: { type: String, enum: Object.values(PAYMENT_STATUS), default: 'PENDING', index: true },
        method: { type: String, enum: ['EFT', 'CREDIT_CARD', 'DEBIT_ORDER', 'CASH', 'CHEQUE', 'BANK_DEPOSIT', 'LPC_PORTAL'] },
        reference: String, paidAt: Date, paidBy: String, receiptNumber: String, receiptUrl: String,
        transactionId: String, bankReference: String, paymentProvider: String, paymentMetadata: Schema.Types.Mixed
    },
    paymentDeadline: { type: Date, required: true, default: () => { const d = new Date(); d.setDate(d.getDate() + 30); return d; }, index: true },
    paymentReminders: [{ sentAt: Date, daysBeforeDeadline: Number, method: { type: String, enum: ['EMAIL', 'SMS', 'PORTAL', 'LETTER'] }, status: String, error: String }],
    practiceType: { type: String, required: true, enum: Object.values(PRACTICE_TYPES) },
    yearsOfPractice: { type: Number, required: true, min: 0, max: 100 },
    practiceArea: { type: String, enum: Object.values(PRACTICE_AREAS), required: true },
    proBonoHours: { type: Number, default: 0, min: 0, max: 5000 },
    employees: { type: Number, default: 1, min: 1 },
    partners: { type: Number, default: 1, min: 1 },
    annualTurnover: { type: Number, required: true, min: 0, get: v => parseFloat(v.toFixed(2)) },
    complianceCheck: {
        cpdCompliant: { type: Boolean, default: false }, trustAccountActive: { type: Boolean, default: false },
        practiceRegistered: { type: Boolean, default: false }, disciplinaryClear: { type: Boolean, default: false },
        taxCompliant: { type: Boolean, default: false }, ficaVerified: { type: Boolean, default: false },
        verifiedAt: Date, verifiedBy: String, verificationReference: String, verificationReport: String
    },
    certificateHash: { type: String, required: true, unique: true, default: function() { return crypto.createHash('sha3-512').update([this.certificateId, this.attorneyLpcNumber, this.issueDate.toISOString(), this.expiryDate.toISOString(), this.contributionAmount.toString(), this.turnoverDeclared.toString()].join(':')).digest('hex'); } },
    digitalSignature: { type: String, required: true, default: function() { return crypto.createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026').update([this.certificateId, this.certificateHash, this.issueDate.toISOString()].join(':')).digest('hex'); } },
    integrityHash: { type: String, unique: true, default: function() { return crypto.createHash('sha3-512').update(`${this.certificateId}:${this.certificateHash}:${Date.now()}`).digest('hex'); } },
    quantumSignature: { type: String, default: function() { return crypto.createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026').update(`${this._id}:${this.certificateId}:${this.integrityHash}`).digest('hex'); } },
    verificationUrl: { type: String, default: function() { return `https://verify.wilsyos.co.za/ffc/${this.certificateId}`; } },
    verificationQR: { type: String, default: function() { return `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${this.certificateId}`; } },
    verificationMethods: [{ method: { type: String, enum: Object.values(VERIFICATION_METHODS) }, verifiedAt: Date, verifiedBy: String, verificationData: Schema.Types.Mixed, successful: Boolean }],
    blockchainAnchor: { anchorId: { type: String, sparse: true, unique: true }, transactionHash: String, blockNumber: Number, timestamp: Date, network: { type: String, enum: ['ETHEREUM', 'HYPERLEDGER', 'BESU', 'PRIVATE'], default: 'PRIVATE' }, verified: { type: Boolean, default: false }, verificationUrl: String },
    renewal: {
        previousCertificateId: { type: String, sparse: true, validate: { validator: v => !v || /^FFC-\d{4}-[A-F0-9]{8}$/.test(v) } },
        nextCertificateId: { type: String, sparse: true, validate: { validator: v => !v || /^FFC-\d{4}-[A-F0-9]{8}$/.test(v) } },
        renewalDate: Date, renewalStatus: { type: String, enum: ['PENDING', 'PROCESSING', 'COMPLETED', 'SKIPPED', 'AUTO_RENEWED'] },
        renewalMethod: { type: String, enum: ['AUTOMATIC', 'MANUAL', 'PORTAL', 'BULK'] },
        renewalReminders: [{ sentAt: Date, daysBeforeExpiry: Number, method: String, status: String }],
        renewalApplication: String, renewalApproval: String
    },
    auditTrail: [{
        action: { type: String, enum: ['CERTIFICATE_ISSUED', 'CERTIFICATE_RENEWED', 'CERTIFICATE_EXPIRED', 'CERTIFICATE_REVOKED', 'CERTIFICATE_SUSPENDED', 'CERTIFICATE_CANCELLED', 'CERTIFICATE_REPLACED', 'PAYMENT_RECEIVED', 'PAYMENT_OVERDUE', 'PAYMENT_REFUNDED', 'DISCOUNT_APPLIED', 'EXEMPTION_GRANTED', 'VERIFIED', 'BLOCKCHAIN_ANCHORED', 'REMINDER_SENT', 'DETAILS_UPDATED'] },
        performedBy: String, performedAt: { type: Date, default: Date.now }, ipAddress: String, userAgent: String,
        changes: Schema.Types.Mixed, previousState: Schema.Types.Mixed, newState: Schema.Types.Mixed,
        reason: String, authorization: String,
        hash: { type: String, default: function() { return crypto.createHash('sha3-512').update(`${this.action}:${this.performedAt.toISOString()}:${this.performedBy}:${JSON.stringify(this.changes)}`).digest('hex'); } }
    }],
    issuedBy: { type: String, required: true, immutable: true },
    issuedAt: { type: Date, default: Date.now, immutable: true },
    lastUpdatedBy: String,
    retentionPolicy: { type: String, default: 'companies_act_5_years' },
    retentionStart: { type: Date, default: Date.now, immutable: true },
    retentionExpiry: { type: Date, default: function() { const d = new Date(); d.setFullYear(d.getFullYear() + 5); return d; }, index: true },
    dataResidency: { type: String, default: 'ZA', enum: ['ZA', 'EU', 'US', 'AU', 'UK'] },
    deleted: { type: Boolean, default: false, index: true },
    deletedAt: Date, deletedBy: String, deletionReason: String, deletionAuthorization: String
}, { timestamps: true, toJSON: { virtuals: true, transform: function(doc, ret) { delete ret.__v; delete ret.auditTrail; delete ret.certificateHash; delete ret.digitalSignature; delete ret.integrityHash; delete ret.quantumSignature; delete ret.blockchainAnchor; delete ret.payment.receiptUrl; delete ret.payment.transactionId; return ret; } } });

fidelityFundSchema.virtual('isValid').get(function() { return this.status === 'ISSUED' && this.expiryDate > new Date() && this.payment.status === 'PAID' && !this.deleted; });
fidelityFundSchema.virtual('isExpiringSoon').get(function() { const d = this.daysUntilExpiry; return d !== null && d <= 30 && d > 0; });
fidelityFundSchema.virtual('isOverdue').get(function() { return this.payment.status === 'PENDING' && this.paymentDeadline < new Date(); });
fidelityFundSchema.virtual('daysUntilExpiry').get(function() { return this.expiryDate ? Math.ceil((this.expiryDate - Date.now()) / (1000 * 60 * 60 * 24)) : null; });
fidelityFundSchema.virtual('daysSinceExpiry').get(function() { return this.expiryDate ? (this.expiryDate > new Date() ? 0 : Math.ceil((Date.now() - this.expiryDate) / (1000 * 60 * 60 * 24))) : null; });
fidelityFundSchema.virtual('daysUntilPaymentDeadline').get(function() { return this.paymentDeadline && this.payment.status !== 'PAID' ? Math.ceil((this.paymentDeadline - Date.now()) / (1000 * 60 * 60 * 24)) : 0; });
fidelityFundSchema.virtual('totalDiscount').get(function() { return parseFloat(this.discounts.reduce((s, d) => s + (d.amount || 0), 0).toFixed(2)); });
fidelityFundSchema.virtual('netContribution').get(function() { return parseFloat(Math.max(0, this.contributionAmount - this.totalDiscount).toFixed(2)); });
fidelityFundSchema.virtual('contributionRate').get(function() { return this.turnoverDeclared === 0 ? 0 : parseFloat(((this.baseContribution / this.turnoverDeclared) * 100).toFixed(3)); });
fidelityFundSchema.virtual('discountEfficiency').get(function() { return this.baseContribution === 0 ? 0 : parseFloat(((this.discountAmount / this.baseContribution) * 100).toFixed(1)); });
fidelityFundSchema.virtual('certificateAge').get(function() { return Math.ceil((Date.now() - this.issueDate) / (1000 * 60 * 60 * 24)); });
fidelityFundSchema.virtual('lifecyclePercentage').get(function() { if (!this.expiryDate) return 0; return Math.min(100, Math.max(0, ((Date.now() - this.issueDate) / (this.expiryDate - this.issueDate)) * 100)); });

fidelityFundSchema.index({ tenantId: 1, attorneyId: 1, issueDate: -1 });
fidelityFundSchema.index({ tenantId: 1, status: 1, expiryDate: 1 });
fidelityFundSchema.index({ tenantId: 1, 'payment.status': 1, paymentDeadline: 1 });
fidelityFundSchema.index({ tenantId: 1, practiceType: 1, practiceArea: 1 });
fidelityFundSchema.index({ tenantId: 1, yearsOfPractice: 1 });
fidelityFundSchema.index({ certificateHash: 1 }, { unique: true });
fidelityFundSchema.index({ integrityHash: 1 }, { unique: true });
fidelityFundSchema.index({ 'blockchainAnchor.anchorId': 1 }, { sparse: true });
fidelityFundSchema.index({ deleted: 1, retentionExpiry: 1 });
fidelityFundSchema.index({ expiryDate: 1, status: 1, 'renewal.renewalStatus': 1 });

fidelityFundSchema.pre('save', async function(next) {
    try {
        if (!this.tenantId) throw new Error('TENANT_ISOLATION_VIOLATION');
        this.contributionAmount = Math.max(0, this.baseContribution - this.discountAmount);
        if (!this.isExempt) this.contributionAmount = Math.max(500, Math.min(50000, this.contributionAmount));
        if (this.isModified('status')) this.statusHistory.push({ status: this.status, changedAt: new Date(), changedBy: this.lastUpdatedBy || this.issuedBy, reason: this.statusReason, notes: this.statusNotes, authorization: this.statusAuthorization, ipAddress: this.ipAddress, userAgent: this.userAgent });
        if (this.expiryDate < new Date() && ['ISSUED', 'RENEWED'].includes(this.status)) {
            this.status = 'EXPIRED';
            this.statusHistory.push({ status: 'EXPIRED', changedAt: new Date(), reason: 'Certificate expired', notes: `Auto-expired on ${new Date().toISOString()}` });
        }
        this.certificateHash = crypto.createHash('sha3-512').update([this.certificateId, this.attorneyLpcNumber, this.issueDate.toISOString(), this.expiryDate.toISOString(), this.contributionAmount.toString(), this.turnoverDeclared.toString()].join(':')).digest('hex');
        this.digitalSignature = crypto.createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026').update([this.certificateId, this.certificateHash, this.issueDate.toISOString()].join(':')).digest('hex');
        this.integrityHash = crypto.createHash('sha3-512').update(`${this.certificateId}:${this.certificateHash}:${Date.now()}`).digest('hex');
        this.quantumSignature = crypto.createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026').update(`${this._id || this.certificateId}:${this.certificateId}:${this.integrityHash}`).digest('hex');
        if (this.isNew) this.auditTrail.push({ action: 'CERTIFICATE_ISSUED', performedBy: this.issuedBy, performedAt: new Date(), changes: { certificateId: this.certificateId, attorneyLpcNumber: this.attorneyLpcNumber, contributionAmount: this.contributionAmount, expiryDate: this.expiryDate } });
        next();
    } catch (error) { next(error); }
});

fidelityFundSchema.statics = {
    calculateContribution(turnover, practiceType = 'PRIVATE', yearsOfPractice = 0, proBonoHours = 0, practiceArea = 'URBAN') {
        if (['NON_PRACTICING', 'GOVERNMENT', 'RETIRED'].includes(practiceType)) {
            return { baseContribution: 0, finalContribution: 0, discountAmount: 0, discountPercentage: 100, isExempt: true, exemptionReason: practiceType, discounts: [], statutoryReference: 'LPC Rule 55(3)', calculationTimestamp: new Date().toISOString() };
        }
        let base = turnover * 0.0025;
        base = Math.max(500, Math.min(50000, Math.round(base * 100) / 100));
        let final = base, discountAmount = 0, discountPct = 0, discounts = [];
        if (yearsOfPractice < 3) { const d = base * 0.5; discountAmount += d; discountPct += 50; discounts.push({ type: 'JUNIOR_ATTORNEY', amount: Math.round(d * 100) / 100, percentage: 50, reason: `Junior attorney discount - Year ${yearsOfPractice + 1} of 3`, statutoryReference: 'LPC Rule 55(6)(a)', expiresAt: new Date(new Date().setFullYear(new Date().getFullYear() + (3 - yearsOfPractice))) }); }
        if (proBonoHours > 50) { const d = base * 0.1; discountAmount += d; discountPct += 10; discounts.push({ type: 'PRO_BONO', amount: Math.round(d * 100) / 100, percentage: 10, reason: `Pro bono service discount - ${proBonoHours} hours provided`, statutoryReference: 'LPC Rule 55(6)(b)', expiresAt: new Date(new Date().setFullYear(new Date().getFullYear() + 1)) }); }
        if (practiceArea === 'RURAL') { const d = base * 0.15; discountAmount += d; discountPct += 15; discounts.push({ type: 'RURAL_PRACTICE', amount: Math.round(d * 100) / 100, percentage: 15, reason: 'Rural practice discount', statutoryReference: 'LPC Rule 55(6)(c)', expiresAt: new Date(new Date().setFullYear(new Date().getFullYear() + 1)) }); }
        if (practiceArea === 'REMOTE') { const d = base * 0.2; discountAmount += d; discountPct += 20; discounts.push({ type: 'REMOTE_RURAL', amount: Math.round(d * 100) / 100, percentage: 20, reason: 'Remote rural practice discount', statutoryReference: 'LPC Rule 55(6)(d)', expiresAt: new Date(new Date().setFullYear(new Date().getFullYear() + 1)) }); }
        if (yearsOfPractice >= 20) { const d = base * 0.15; discountAmount += d; discountPct += 15; discounts.push({ type: 'LONG_STANDING', amount: Math.round(d * 100) / 100, percentage: 15, reason: `Long-standing practice discount - ${yearsOfPractice} years`, statutoryReference: 'LPC Rule 55(6)(e)', expiresAt: null }); }
        if (discountPct > 50) { const r = 50 / discountPct; discountAmount *= r; discountPct = 50; discounts.forEach(d => { d.amount = Math.round(d.amount * r * 100) / 100; d.percentage = Math.round(d.percentage * r); }); }
        final = Math.max(0, Math.round((base - discountAmount) * 100) / 100);
        return { baseContribution: base, finalContribution: final, discountAmount: Math.round(discountAmount * 100) / 100, discountPercentage: discountPct, discounts, isExempt: false, statutoryMinimum: 500, statutoryMaximum: 50000, contributionRate: 0.0025, calculationTimestamp: new Date().toISOString() };
    },
    async findExpiring(tenantId, days = 30) { const t = new Date(); t.setDate(t.getDate() + days); return this.find({ tenantId, status: { $in: ['ISSUED', 'RENEWED'] }, expiryDate: { $lte: t, $gt: new Date() }, deleted: false }).populate('attorneyId', 'lpcNumber practice.name contact.email contact.phone').populate('firmId', 'name contact.email contact.phone').sort({ expiryDate: 1 }); },
    async findOverduePayments(tenantId) { return this.find({ tenantId, 'payment.status': 'PENDING', paymentDeadline: { $lt: new Date() }, status: { $ne: 'CANCELLED' }, deleted: false }).populate('attorneyId', 'lpcNumber practice.name contact.email contact.phone').sort({ paymentDeadline: 1 }); },
    async getRenewalStats(tenantId, year = new Date().getFullYear()) {
        const sd = new Date(year, 0, 1), ed = new Date(year, 11, 31);
        const stats = await this.aggregate([{ $match: { tenantId, issueDate: { $gte: sd, $lte: ed }, deleted: false } }, { $group: { _id: '$status', count: { $sum: 1 }, totalContribution: { $sum: '$contributionAmount' }, averageContribution: { $avg: '$contributionAmount' }, totalTurnover: { $sum: '$turnoverDeclared' }, totalDiscount: { $sum: '$discountAmount' } } }]);
        const totals = await this.aggregate([{ $match: { tenantId, issueDate: { $gte: sd, $lte: ed }, deleted: false } }, { $group: { _id: null, totalCertificates: { $sum: 1 }, totalContributions: { $sum: '$contributionAmount' }, totalTurnover: { $sum: '$turnoverDeclared' }, totalDiscounts: { $sum: '$discountAmount' }, averageContribution: { $avg: '$contributionAmount' } } }]);
        const byPracticeType = await this.aggregate([{ $match: { tenantId, issueDate: { $gte: sd, $lte: ed }, deleted: false } }, { $group: { _id: '$practiceType', count: { $sum: 1 }, totalContribution: { $sum: '$contributionAmount' }, averageContribution: { $avg: '$contributionAmount' } } }]);
        const byDiscountType = await this.aggregate([{ $match: { tenantId, issueDate: { $gte: sd, $lte: ed }, deleted: false } }, { $unwind: '$discounts' }, { $group: { _id: '$discounts.type', count: { $sum: 1 }, totalDiscountAmount: { $sum: '$discounts.amount' }, averageDiscount: { $avg: '$discounts.amount' } } }]);
        return { year, summary: totals[0] || { totalCertificates: 0, totalContributions: 0, totalTurnover: 0, totalDiscounts: 0, averageContribution: 0 }, byStatus: stats, byPracticeType, byDiscountType, generatedAt: new Date().toISOString() };
    },
    async getComplianceStats(tenantId) {
        const total = await this.countDocuments({ tenantId, deleted: false });
        const active = await this.countDocuments({ tenantId, status: { $in: ['ISSUED', 'RENEWED'] }, expiryDate: { $gt: new Date() }, 'payment.status': 'PAID', deleted: false });
        const expiringSoon = await this.countDocuments({ tenantId, status: { $in: ['ISSUED', 'RENEWED'] }, expiryDate: { $gt: new Date(), $lt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) }, deleted: false });
        const expired = await this.countDocuments({ tenantId, status: 'EXPIRED', deleted: false });
        const pendingPayment = await this.countDocuments({ tenantId, 'payment.status': 'PENDING', paymentDeadline: { $gt: new Date() }, deleted: false });
        const overdue = await this.countDocuments({ tenantId, 'payment.status': 'PENDING', paymentDeadline: { $lt: new Date() }, deleted: false });
        const totalContribution = await this.aggregate([{ $match: { tenantId, status: { $in: ['ISSUED', 'RENEWED'] }, deleted: false } }, { $group: { _id: null, total: { $sum: '$contributionAmount' } } }]);
        return { total, active, expiringSoon, expired, pendingPayment, overdue, complianceRate: total > 0 ? Math.round((active / total) * 100) : 0, totalContribution: totalContribution[0]?.total || 0, timestamp: new Date().toISOString() };
    }
};


fidelityFundSchema.methods = {
    async renew(turnover, userContext) {
        if (!['ISSUED', 'EXPIRED'].includes(this.status)) throw new Error(`CERTIFICATE_NOT_RENEWABLE: ${this.status}`);
        const AttorneyProfile = mongoose.model('AttorneyProfile');
        const attorney = await AttorneyProfile.findById(this.attorneyId);
        if (!attorney) throw new Error('ATTORNEY_NOT_FOUND');
        const calc = this.constructor.calculateContribution(turnover, attorney.practice?.type || this.practiceType, (attorney.practice?.yearsOfPractice || this.yearsOfPractice) + 1, attorney.practice?.proBonoHours || this.proBonoHours, attorney.practice?.area || this.practiceArea);
        const cert = new this.constructor({ tenantId: this.tenantId, attorneyId: this.attorneyId, attorneyLpcNumber: this.attorneyLpcNumber, practiceNumber: this.practiceNumber, firmId: this.firmId, ...calc, practiceType: attorney.practice?.type || this.practiceType, yearsOfPractice: (attorney.practice?.yearsOfPractice || this.yearsOfPractice) + 1, practiceArea: attorney.practice?.area || this.practiceArea, proBonoHours: attorney.practice?.proBonoHours || this.proBonoHours, employees: attorney.practice?.employees || this.employees, partners: attorney.practice?.partners || this.partners, annualTurnover: turnover, issuedBy: userContext.userId, issueDate: new Date(), expiryDate: new Date(new Date().setFullYear(new Date().getFullYear() + 1)), payment: { amount: calc.finalContribution, status: 'PENDING' }, renewal: { previousCertificateId: this.certificateId, renewalDate: new Date(), renewalStatus: 'COMPLETED', renewalMethod: 'MANUAL' } });
        await cert.save();
        this.status = 'RENEWED'; this.renewal.nextCertificateId = cert.certificateId; this.renewal.renewalDate = new Date(); this.renewal.renewalStatus = 'COMPLETED'; this.lastUpdatedBy = userContext.userId;
        this.auditTrail.push({ action: 'CERTIFICATE_RENEWED', performedBy: userContext.userId, performedAt: new Date(), changes: { previousCertificateId: this.certificateId, newCertificateId: cert.certificateId, contributionAmount: cert.contributionAmount } });
        await this.save();
        return { success: true, previousCertificateId: this.certificateId, newCertificateId: cert.certificateId, newCertificate: cert, contributionAmount: cert.contributionAmount, expiryDate: cert.expiryDate };
    },
    async revoke(reason, userContext) {
        if (this.status === 'REVOKED') throw new Error('CERTIFICATE_ALREADY_REVOKED');
        const prev = this.status;
        this.status = 'REVOKED'; this.statusReason = reason; this.statusChangedAt = new Date(); this.statusChangedBy = userContext.userId; this.lastUpdatedBy = userContext.userId;
        this.auditTrail.push({ action: 'CERTIFICATE_REVOKED', performedBy: userContext.userId, performedAt: new Date(), changes: { previousStatus: prev, newStatus: 'REVOKED', reason } });
        await this.save();
        return { success: true, certificateId: this.certificateId, revokedAt: new Date(), revokedBy: userContext.userId, reason };
    },
    async recordPayment(paymentData, userContext) {
        if (this.payment.status === 'PAID') throw new Error('PAYMENT_ALREADY_RECORDED');
        const prev = this.payment.status;
        this.payment = { ...this.payment, ...paymentData, status: 'PAID', paidAt: new Date(), paidBy: userContext.userId };
        if (this.status === 'PENDING') { this.status = 'ISSUED'; this.statusHistory.push({ status: 'ISSUED', changedAt: new Date(), changedBy: userContext.userId, reason: 'Payment received' }); }
        this.lastUpdatedBy = userContext.userId;
        this.auditTrail.push({ action: 'PAYMENT_RECEIVED', performedBy: userContext.userId, performedAt: new Date(), changes: { previousStatus: prev, newStatus: 'PAID', amount: this.payment.amount, method: this.payment.method, reference: this.payment.reference } });
        await this.save();
        return { success: true, certificateId: this.certificateId, paidAt: this.payment.paidAt, amount: this.payment.amount, receiptNumber: this.payment.receiptNumber, transactionId: this.payment.transactionId };
    },
    async applyDiscount(discountData, userContext) {
        if (this.discounts.some(d => d.type === discountData.type)) throw new Error(`DISCOUNT_ALREADY_APPLIED: ${discountData.type}`);
        const d = { type: discountData.type, amount: Math.round(discountData.amount * 100) / 100, percentage: discountData.percentage, reason: discountData.reason, approvedBy: userContext.userId, approvedAt: new Date(), approvalReference: discountData.approvalReference, expiresAt: discountData.expiresAt, documentation: discountData.documentation || [] };
        this.discounts.push(d);
        this.discountAmount = this.discounts.reduce((s, x) => s + x.amount, 0);
        this.discountPercentage = Math.min(50, this.discounts.reduce((s, x) => s + (x.percentage || 0), 0));
        this.contributionAmount = Math.max(0, this.baseContribution - this.discountAmount);
        this.lastUpdatedBy = userContext.userId;
        this.auditTrail.push({ action: 'DISCOUNT_APPLIED', performedBy: userContext.userId, performedAt: new Date(), changes: { discountType: d.type, discountAmount: d.amount, discountPercentage: d.percentage, newContribution: this.contributionAmount } });
        await this.save();
        return { success: true, certificateId: this.certificateId, discount: d, newContributionAmount: this.contributionAmount, totalDiscount: this.discountAmount, totalDiscountPercentage: this.discountPercentage };
    },
    async generateVerificationProof() {
        return {
            certificateId: this.certificateId, attorneyLpcNumber: this.attorneyLpcNumber, attorneyName: '[REDACTED]', practiceName: '[REDACTED]',
            issueDate: this.issueDate, expiryDate: this.expiryDate, status: this.status, isValid: this.isValid, contributionAmount: this.contributionAmount,
            verificationTimestamp: new Date().toISOString(), certificateHash: this.certificateHash,
            digitalSignature: crypto.createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026').update(`${this.certificateId}:${Date.now()}`).digest('hex'),
            verificationUrl: `${this.verificationUrl}?t=${Date.now()}`, verifiedBy: 'WilsyOS Fidelity Fund Engine v5.0.1',
            blockchainAnchor: this.blockchainAnchor?.verified ? { anchorId: this.blockchainAnchor.anchorId, transactionHash: this.blockchainAnchor.transactionHash, timestamp: this.blockchainAnchor.timestamp } : null
        };
    },
    async anchorToBlockchain() {
        if (this.blockchainAnchor?.verified) return { success: false, message: 'Already anchored to blockchain', anchorId: this.blockchainAnchor.anchorId };
        const anchorId = `FFC-ANC-${crypto.randomBytes(8).toString('hex').toUpperCase()}`;
        const txHash = crypto.createHash('sha3-512').update(`${anchorId}:${this.certificateHash}:${Date.now()}`).digest('hex');
        this.blockchainAnchor = { anchorId, transactionHash: txHash, blockNumber: Math.floor(Date.now() / 1000), timestamp: new Date(), network: 'PRIVATE', verified: true, verificationUrl: `https://verify.wilsyos.co.za/blockchain/${anchorId}` };
        this.auditTrail.push({ action: 'BLOCKCHAIN_ANCHORED', performedBy: 'SYSTEM', performedAt: new Date(), changes: { anchorId, transactionHash: txHash, timestamp: this.blockchainAnchor.timestamp } });
        await this.save();
        return { success: true, anchorId, transactionHash: txHash, timestamp: this.blockchainAnchor.timestamp, verificationUrl: this.blockchainAnchor.verificationUrl };
    },
    async sendRenewalReminder(method = 'EMAIL', days = 30) {
        if (!this.renewal.renewalReminders) this.renewal.renewalReminders = [];
        this.renewal.renewalReminders.push({ sentAt: new Date(), daysBeforeExpiry: days, method, status: 'SENT' });
        this.auditTrail.push({ action: 'REMINDER_SENT', performedBy: 'SYSTEM', performedAt: new Date(), changes: { method, daysBeforeExpiry: days, expiryDate: this.expiryDate } });
        await this.save();
        return { success: true, certificateId: this.certificateId, reminder: this.renewal.renewalReminders[this.renewal.renewalReminders.length - 1] };
    },
    async generateAuditReport() {
        const stats = await this.constructor.getComplianceStats(this.tenantId);
        return {
            certificateId: this.certificateId, attorneyLpcNumber: this.attorneyLpcNumber, practiceNumber: this.practiceNumber, status: this.status,
            lifecycle: { issuedAt: this.issueDate, issuedBy: this.issuedBy, expiryDate: this.expiryDate, daysUntilExpiry: this.daysUntilExpiry, daysSinceExpiry: this.daysSinceExpiry, certificateAge: this.certificateAge, lifecyclePercentage: this.lifecyclePercentage },
            financial: { turnoverDeclared: this.turnoverDeclared, baseContribution: this.baseContribution, discountAmount: this.discountAmount, discountPercentage: this.discountPercentage, contributionAmount: this.contributionAmount, netContribution: this.netContribution, contributionRate: this.contributionRate, discountEfficiency: this.discountEfficiency },
            discounts: this.discounts.map(d => ({ type: d.type, amount: d.amount, percentage: d.percentage, reason: d.reason, approvedBy: d.approvedBy, approvedAt: d.approvedAt, expiresAt: d.expiresAt })),
            payment: { amount: this.payment.amount, status: this.payment.status, paidAt: this.payment.paidAt, paidBy: this.payment.paidBy, method: this.payment.method, reference: this.payment.reference, daysUntilDeadline: this.daysUntilPaymentDeadline, isOverdue: this.isOverdue },
            compliance: { isExempt: this.isExempt, exemptionReason: this.exemptionReason, complianceCheck: this.complianceCheck, isValid: this.isValid, isExpiringSoon: this.isExpiringSoon },
            integrity: { certificateHash: this.certificateHash, digitalSignature: this.digitalSignature, integrityHash: this.integrityHash, quantumSignature: this.quantumSignature, blockchainVerified: this.blockchainAnchor?.verified || false, blockchainAnchorId: this.blockchainAnchor?.anchorId },
            verification: { verificationUrl: this.verificationUrl, verificationQR: this.verificationQR, verificationMethods: this.verificationMethods },
            renewal: this.renewal, tenantCompliance: stats, auditTrail: this.auditTrail.slice(-10),
            retention: { policy: this.retentionPolicy, expiryDate: this.retentionExpiry, daysRemaining: Math.ceil((this.retentionExpiry - Date.now()) / (1000 * 60 * 60 * 24)) },
            generatedAt: new Date().toISOString(), generatedBy: 'WilsyOS Fidelity Fund Engine v5.0.1'
        };
    }
};


// ============================================================================
// SURGICAL EXPORTS FOR ESM COMPATIBILITY
// ============================================================================
const FidelityFund = mongoose.models.FidelityFund || mongoose.model('FidelityFund', fidelityFundSchema);

export {
    CERTIFICATE_STATUS,
    PRACTICE_TYPES,
    PRACTICE_AREAS,
    PAYMENT_STATUS,
    DISCOUNT_TYPES,
    EXEMPTION_REASONS,
    VERIFICATION_METHODS,
    FidelityFund as default
};
