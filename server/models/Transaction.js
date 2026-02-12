// ====================================================================
// FILE: server/models/Transaction.js
// ====================================================================
/**
 * WILSYS OS - TRANSACTION MODEL
 * LPC Rule 21.1 - Matter Transaction Traceability
 * LPC Rule 86.2 - Trust Account Transaction Recording
 */

const mongoose = require('mongoose');

const transactionSchema = new mongoose.Schema({
    transactionId: {
        type: String,
        required: true,
        unique: true,
        default: () => `TXN-${new mongoose.Types.ObjectId().toString().slice(-12).toUpperCase()}`
    },
    matterId: {
        type: String,
        required: true,
        index: true
    },
    accountNumber: {
        type: String,
        required: false,
        index: true,
        validate: {
            validator: function (v) {
                return !v || /^TRUST-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$/.test(v);
            },
            message: props => `${props.value} is not a valid trust account number! LPC Rule 21.1.3`
        }
    },
    attorneyId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'AttorneyProfile',
        required: true,
        index: true
    },
    attorneyLpcNumber: {
        type: String,
        required: true,
        index: true
    },
    tenantId: {
        type: String,
        required: true,
        index: true
    },
    firmId: {
        type: String,
        required: true,
        index: true
    },
    type: {
        type: String,
        enum: ['CREDIT', 'DEBIT', 'TRANSFER', 'FEE', 'INTEREST', 'REFUND'],
        required: true
    },
    amount: {
        type: Number,
        required: true,
        min: 0.01
    },
    description: {
        type: String,
        required: true,
        trim: true,
        maxlength: 500
    },
    reference: {
        type: String,
        trim: true,
        maxlength: 100
    },
    clientReference: {
        type: String,
        trim: true,
        maxlength: 100
    },
    clientId: {
        type: String,
        index: true
    },
    clientName: String,
    status: {
        type: String,
        enum: ['PENDING', 'COMPLETED', 'FAILED', 'REVERSED', 'RECONCILED'],
        default: 'PENDING'
    },
    reversalOf: {
        type: String,
        ref: 'Transaction'
    },
    reversedBy: {
        type: String
    },
    reversalReason: String,
    reversalDate: Date,
    metadata: {
        source: String,
        sourceIp: String,
        userAgent: String,
        sessionId: String,
        correlationId: String
    },
    compliance: {
        lpc211Verified: {
            type: Boolean,
            default: false
        },
        ficaThresholdExceeded: {
            type: Boolean,
            default: false
        },
        sarReportable: {
            type: Boolean,
            default: false
        },
        verificationTimestamp: Date
    },
    reconciliationStatus: {
        isReconciled: {
            type: Boolean,
            default: false
        },
        reconciledAt: Date,
        reconciledBy: String,
        reconciliationId: String,
        statementReference: String,
        discrepancy: Number
    },
    runningBalance: {
        type: Number,
        default: 0
    },
    processedBy: {
        type: String,
        required: true
    },
    processedAt: {
        type: Date,
        default: Date.now
    },
    transactionHash: {
        type: String,
        unique: true,
        sparse: true
    },
    blockHash: String,
    auditChainIndex: Number,
    retentionExpiry: {
        type: Date,
        default: function () {
            const date = new Date();
            date.setDate(date.getDate() + 3650); // 10 years
            return date;
        }
    },
    deleted: {
        type: Boolean,
        default: false
    },
    deletedAt: Date,
    deletionReason: String
}, {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});

// Indexes for performance
transactionSchema.index({ tenantId: 1, matterId: 1, processedAt: -1 });
transactionSchema.index({ tenantId: 1, accountNumber: 1, processedAt: -1 });
transactionSchema.index({ tenantId: 1, attorneyLpcNumber: 1, processedAt: -1 });
transactionSchema.index({ transactionHash: 1 });
transactionSchema.index({ 'reconciliationStatus.reconciliationId': 1 });

// Virtuals
transactionSchema.virtual('isReversal').get(function () {
    return !!this.reversalOf;
});

transactionSchema.virtual('ageInDays').get(function () {
    return Math.floor((Date.now() - this.processedAt) / (1000 * 60 * 60 * 24));
});

// Pre-save hooks
transactionSchema.pre('save', async function (next) {
    if (this.isNew && !this.transactionHash) {
        const crypto = require('crypto');
        const hash = crypto.createHash('sha3-512')
            .update(`${this.transactionId}:${this.amount}:${this.processedAt.toISOString()}:${this.matterId}`)
            .digest('hex');
        this.transactionHash = hash;
    }
    next();
});

// Static methods
transactionSchema.statics.getComplianceStats = async function (tenantId, firmId = null, days = 30) {
    const query = { tenantId, deleted: false };
    if (firmId) query.firmId = firmId;

    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    const [total, completed, reconciled, suspicious] = await Promise.all([
        this.countDocuments({ ...query, processedAt: { $gte: startDate } }),
        this.countDocuments({ ...query, processedAt: { $gte: startDate }, status: 'COMPLETED' }),
        this.countDocuments({ ...query, processedAt: { $gte: startDate }, 'reconciliationStatus.isReconciled': true }),
        this.countDocuments({ ...query, processedAt: { $gte: startDate }, 'compliance.sarReportable': true })
    ]);

    return {
        total,
        completed,
        reconciliationRate: total > 0 ? (reconciled / total) * 100 : 0,
        suspiciousTransactions: suspicious,
        complianceRate: total > 0 ? (completed / total) * 100 : 0
    };
};

transactionSchema.statics.findByAccount = async function (accountNumber, tenantId, limit = 100) {
    return this.find({
        accountNumber,
        tenantId,
        deleted: false
    })
        .sort({ processedAt: -1 })
        .limit(limit)
        .lean()
        .exec();
};

transactionSchema.statics.findByMatter = async function (matterId, tenantId, accountNumber = null, limit = 1000) {
    const query = { matterId, tenantId, deleted: false };
    if (accountNumber) query.accountNumber = accountNumber;

    return this.find(query)
        .sort({ processedAt: -1 })
        .limit(limit)
        .lean()
        .exec();
};

module.exports = mongoose.model('Transaction', transactionSchema);