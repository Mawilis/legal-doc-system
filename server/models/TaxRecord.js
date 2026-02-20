/**
 * ====================================================================
 * TAX RECORD MODEL - SARS eFILING INTEGRATION
 * ====================================================================
 * 
 * @file server/models/TaxRecord.js
 * @version 6.0.1
 * @author Wilson Khanyezi - Chief Quantum Sentinel
 * @date 2026-02-14
 * 
 * @description
 *   COMPREHENSIVE TAX RECORD MODEL FOR SARS eFILING INTEGRATION
 *   This model provides forensic-grade tracking of all tax filings,
 *   assessments, payments, and compliance flags with multi-tenant isolation.
 * 
 * ====================================================================
 */

const mongoose = require('mongoose');
const crypto = require('crypto');
const { DateTime } = require('luxon');

// ====================================================================
// TAX RECORD SCHEMA DEFINITION
// ====================================================================
const TaxRecordSchema = new mongoose.Schema({
    tenantId: { type: String, required: true, index: true },
    taxpayerId: { type: String, required: true, index: true },
    taxpayerType: { 
        type: String, 
        enum: ['INDIVIDUAL', 'COMPANY', 'TRUST', 'PARTNERSHIP', 'SOLE_PROPRIETOR'],
        default: 'INDIVIDUAL',
        required: true 
    },
    filingType: { 
        type: String, 
        enum: ['ITR12', 'ITR14', 'VAT201', 'PAYE', 'CIT', 'DIVIDENDS', 'PROVISIONAL', 'CAPITAL_GAINS'],
        required: true,
        index: true 
    },
    taxYear: { type: Number, required: true, index: true },
    period: { type: String, enum: ['ANNUAL', 'MONTHLY', 'QUARTERLY', 'BI-ANNUAL'], default: 'ANNUAL' },
    filingDate: { type: Date, default: Date.now, index: true, required: true },
    submissionId: { type: String, sparse: true, unique: true, index: true },
    status: { 
        type: String, 
        enum: ['DRAFT', 'VALIDATING', 'SUBMITTED', 'PROCESSING', 'ACCEPTED', 'REJECTED', 'AMENDED', 'CANCELLED', 'UNDER_AUDIT', 'OBJECTION_FILED', 'APPEAL_FILED'],
        default: 'DRAFT',
        index: true 
    },
    statusHistory: [{
        status: String,
        timestamp: { type: Date, default: Date.now },
        reason: String,
        updatedBy: String,
        metadata: mongoose.Schema.Types.Mixed
    }],
    responseData: mongoose.Schema.Types.Mixed,
    assessmentData: {
        assessmentNumber: String,
        assessmentDate: Date,
        assessmentType: String,
        taxableIncome: Number,
        taxPayable: Number,
        rebates: Number,
        penalties: [{
            type: String,
            amount: Number,
            rate: Number,
            calculationBasis: String,
            imposedDate: Date,
            waivedAmount: Number,
            waiverReason: String
        }],
        interest: {
            amount: Number,
            rate: Number,
            periodMonths: Number,
            calculationBasis: String
        },
        paymentDueDate: Date,
        paymentReference: String,
        rawAssessment: mongoose.Schema.Types.Mixed
    },
    payments: [{
        paymentId: String,
        amount: Number,
        paymentDate: { type: Date, default: Date.now },
        paymentMethod: String,
        paymentReference: String,
        bankAccount: {
            bankName: String,
            branchCode: String,
            accountNumber: { type: String, set: v => v ? `****${v.slice(-4)}` : v }
        },
        confirmationCode: String,
        status: { type: String, enum: ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'REVERSED'], default: 'COMPLETED' },
        metadata: mongoose.Schema.Types.Mixed
    }],
    amountDue: { type: Number, default: 0, min: 0 },
    amountPaid: { type: Number, default: 0, min: 0 },
    documents: [{
        documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
        documentType: String,
        fileName: String,
        fileHash: String,
        sarsReference: String,
        uploadedAt: { type: Date, default: Date.now },
        uploadedBy: String,
        metadata: mongoose.Schema.Types.Mixed
    }],
    complianceFlags: [{
        flag: { type: String, enum: ['RED_FLAG', 'UNDER_AUDIT', 'PENALTY_APPLIED', 'OBJECTION_FILED', 'APPEAL_FILED', 'PAYMENT_OVERDUE', 'FILING_LATE', 'INCONSISTENT_DATA', 'HIGH_RISK', 'MEDIUM_RISK', 'LOW_RISK'] },
        raisedAt: { type: Date, default: Date.now },
        raisedBy: String,
        reason: String,
        resolvedAt: Date,
        resolvedBy: String,
        resolutionNotes: String,
        metadata: mongoose.Schema.Types.Mixed
    }],
    riskScore: { type: Number, min: 0, max: 100, default: 0 },
    retentionPolicy: { type: String, enum: ['tax_act_5_years', 'companies_act_7_years', 'permanent'], default: 'tax_act_5_years', required: true },
    dataResidency: { type: String, enum: ['ZA', 'EU', 'US', 'OTHER'], default: 'ZA', required: true },
    retentionStart: { type: Date, default: Date.now, required: true },
    legalHold: {
        active: { type: Boolean, default: false },
        placedAt: Date,
        placedBy: String,
        reason: String,
        caseReference: String,
        releasedAt: Date,
        releasedBy: String
    },
    auditTrail: [{
        action: { type: String, required: true },
        userId: String,
        tenantId: String,
        timestamp: { type: Date, default: Date.now },
        changes: mongoose.Schema.Types.Mixed,
        ipAddress: String,
        userAgent: String,
        correlationId: String,
        forensicHash: String
    }],
    forensicHash: { type: String, required: true, unique: true },
    metadata: mongoose.Schema.Types.Mixed
}, { timestamps: true });

// ====================================================================
// INDEXES
// ====================================================================
TaxRecordSchema.index({ tenantId: 1, taxpayerId: 1, taxYear: -1 });
TaxRecordSchema.index({ tenantId: 1, status: 1, filingDate: -1 });
TaxRecordSchema.index({ tenantId: 1, filingType: 1, taxYear: -1 });
TaxRecordSchema.index({ submissionId: 1 }, { unique: true, sparse: true });

// ====================================================================
// VIRTUAL PROPERTIES
// ====================================================================
TaxRecordSchema.virtual('balanceDue').get(function() {
    return Math.max(0, this.amountDue - this.amountPaid);
});

TaxRecordSchema.virtual('isOverdue').get(function() {
    if (!this.assessmentData || !this.assessmentData.paymentDueDate) return false;
    return new Date() > new Date(this.assessmentData.paymentDueDate) && this.balanceDue > 0;
});

TaxRecordSchema.virtual('retentionExpiryDate').get(function() {
    const startDate = this.retentionStart || this.createdAt;
    const expiryDate = new Date(startDate);
    if (this.retentionPolicy === 'tax_act_5_years') {
        expiryDate.setFullYear(expiryDate.getFullYear() + 5);
    } else if (this.retentionPolicy === 'companies_act_7_years') {
        expiryDate.setFullYear(expiryDate.getFullYear() + 7);
    }
    return expiryDate;
});

// ====================================================================
// PRE-SAVE MIDDLEWARE
// ====================================================================
TaxRecordSchema.pre('save', function(next) {
    if (this.isNew || this.isModified()) {
        const canonicalData = {
            tenantId: this.tenantId,
            taxpayerId: this.taxpayerId,
            filingType: this.filingType,
            taxYear: this.taxYear,
            submissionId: this.submissionId,
            status: this.status,
            amountDue: this.amountDue,
            amountPaid: this.amountPaid,
            timestamp: new Date().toISOString()
        };
        
        this.forensicHash = crypto
            .createHash('sha256')
            .update(JSON.stringify(canonicalData))
            .digest('hex');
    }
    next();
});

TaxRecordSchema.pre('save', function(next) {
    if (this.isModified('status')) {
        this.statusHistory.push({
            status: this.status,
            timestamp: new Date(),
            reason: `Status updated to ${this.status}`,
            updatedBy: 'system'
        });
    }
    next();
});

// ====================================================================
// INSTANCE METHODS - USING methods OBJECT (STANDARD PATTERN)
// ====================================================================
TaxRecordSchema.methods.updateStatus = async function(status, options = {}) {
    const previousStatus = this.status;
    this.status = status;
    
    this.statusHistory.push({
        status,
        timestamp: new Date(),
        reason: options.reason || `Status updated to ${status}`,
        updatedBy: options.updatedBy || 'system'
    });
    
    this.auditTrail.push({
        action: 'STATUS_UPDATE',
        userId: options.updatedBy || 'system',
        tenantId: this.tenantId,
        timestamp: new Date(),
        changes: { from: previousStatus, to: status },
        correlationId: options.correlationId,
        forensicHash: crypto.createHash('sha256').update(`${this._id}-${Date.now()}`).digest('hex')
    });
    
    return this.save();
};

TaxRecordSchema.methods.recordPayment = async function(paymentData) {
    const paymentId = `PAY-${Date.now()}-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
    
    this.payments.push({
        paymentId,
        amount: paymentData.amount,
        paymentDate: paymentData.paymentDate || new Date(),
        paymentMethod: paymentData.paymentMethod,
        paymentReference: paymentData.paymentReference,
        confirmationCode: paymentData.confirmationCode,
        status: 'COMPLETED'
    });
    
    this.amountPaid += paymentData.amount;
    
    this.auditTrail.push({
        action: 'PAYMENT_RECORDED',
        userId: paymentData.recordedBy || 'system',
        tenantId: this.tenantId,
        timestamp: new Date(),
        changes: { paymentId, amount: paymentData.amount },
        correlationId: paymentData.correlationId
    });
    
    return this.save();
};

TaxRecordSchema.methods.addDocument = async function(documentData) {
    this.documents.push({
        documentId: documentData.documentId,
        documentType: documentData.documentType,
        fileName: documentData.fileName,
        fileHash: documentData.fileHash,
        sarsReference: documentData.sarsReference,
        uploadedAt: new Date(),
        uploadedBy: documentData.uploadedBy || 'system'
    });
    
    this.auditTrail.push({
        action: 'DOCUMENT_ADDED',
        userId: documentData.uploadedBy || 'system',
        tenantId: this.tenantId,
        timestamp: new Date(),
        changes: { documentId: documentData.documentId, documentType: documentData.documentType },
        correlationId: documentData.correlationId
    });
    
    return this.save();
};

TaxRecordSchema.methods.addComplianceFlag = async function(flagData) {
    this.complianceFlags.push({
        flag: flagData.flag,
        raisedAt: new Date(),
        raisedBy: flagData.raisedBy || 'system',
        reason: flagData.reason
    });
    
    return this.save();
};

TaxRecordSchema.methods.calculateRiskScore = async function() {
    let score = 0;
    
    for (const flag of this.complianceFlags) {
        if (!flag.resolvedAt) {
            const scores = {
                'RED_FLAG': 40, 'UNDER_AUDIT': 40,
                'PENALTY_APPLIED': 30, 'OBJECTION_FILED': 30, 'PAYMENT_OVERDUE': 30, 'FILING_LATE': 30,
                'INCONSISTENT_DATA': 20, 'HIGH_RISK': 20,
                'MEDIUM_RISK': 10,
                'LOW_RISK': 5
            };
            score += scores[flag.flag] || 5;
        }
    }
    
    if (this.isOverdue) score += 25;
    
    this.riskScore = Math.min(100, score);
    return this.riskScore;
};

TaxRecordSchema.methods.generateForensicEvidence = function() {
    return {
        recordId: this._id,
        tenantId: this.tenantId,
        taxpayerId: this.taxpayerId,
        filingType: this.filingType,
        taxYear: this.taxYear,
        status: this.status,
        amountDue: this.amountDue,
        amountPaid: this.amountPaid,
        balanceDue: this.balanceDue,
        isOverdue: this.isOverdue,
        riskScore: this.riskScore,
        retentionPolicy: this.retentionPolicy,
        retentionExpiryDate: this.retentionExpiryDate,
        isOnLegalHold: this.legalHold?.active || false,
        createdAt: this.createdAt,
        updatedAt: this.updatedAt,
        forensicHash: this.forensicHash
    };
};

// ====================================================================
// STATIC METHODS - USING statics OBJECT (STANDARD PATTERN)
// ====================================================================
TaxRecordSchema.statics.findByTenant = function(tenantId, options = {}) {
    const query = this.find({ tenantId }).sort(options.sort || { filingDate: -1 });
    if (options.limit) query.limit(options.limit);
    if (options.skip) query.skip(options.skip);
    return query.exec();
};

TaxRecordSchema.statics.findByTaxpayer = function(tenantId, taxpayerId) {
    return this.find({ tenantId, taxpayerId }).sort({ taxYear: -1, filingDate: -1 }).exec();
};

TaxRecordSchema.statics.findOverdue = function(tenantId) {
    return this.find({
        tenantId,
        'assessmentData.paymentDueDate': { $lt: new Date() },
        $expr: { $gt: ['$amountDue', '$amountPaid'] }
    }).exec();
};

TaxRecordSchema.statics.findBySubmissionId = function(submissionId) {
    return this.findOne({ submissionId }).exec();
};

TaxRecordSchema.statics.getEconomicMetrics = async function(tenantId) {
    const result = await this.aggregate([
        { $match: { tenantId } },
        { $group: {
            _id: null,
            totalAmountDue: { $sum: '$amountDue' },
            totalAmountPaid: { $sum: '$amountPaid' },
            totalPenalties: { $sum: { $sum: '$assessmentData.penalties.amount' } },
            avgRiskScore: { $avg: '$riskScore' },
            filingCount: { $sum: 1 }
        }}
    ]);
    
    const stats = result[0] || { totalAmountDue: 0, totalAmountPaid: 0, totalPenalties: 0, avgRiskScore: 0, filingCount: 0 };
    
    return {
        ...stats,
        netOutstanding: stats.totalAmountDue - stats.totalAmountPaid,
        paymentRate: stats.totalAmountDue > 0 ? (stats.totalAmountPaid / stats.totalAmountDue) * 100 : 100
    };
};

// ====================================================================
// EXPORT MODEL
// ====================================================================
const TaxRecord = mongoose.model('TaxRecord', TaxRecordSchema);
module.exports = TaxRecord;
