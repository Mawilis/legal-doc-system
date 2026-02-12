const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');

const CERTIFICATE_STATUS = {
    ISSUED: 'ISSUED',
    PENDING: 'PENDING',
    RENEWED: 'RENEWED',
    EXPIRED: 'EXPIRED',
    REVOKED: 'REVOKED'
};

const PAYMENT_STATUS = {
    PAID: 'PAID',
    PENDING: 'PENDING',
    OVERDUE: 'OVERDUE'
};

const fidelityFundSchema = new mongoose.Schema({
    certificateId: {
        type: String,
        required: true,
        unique: true,
        default: () => `FFC-${new Date().getFullYear()}-${crypto.randomBytes(4).toString('hex').toUpperCase()}`
    },
    
    attorneyId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'AttorneyProfile',
        required: true
    },
    
    attorneyLpcNumber: { type: String, required: true },
    tenantId: { type: String, required: true, index: true },
    
    contributionAmount: { type: Number, required: true, min: 0 },
    turnoverDeclared: { type: Number, required: true, min: 0 },
    baseContribution: { type: Number, required: true, min: 0 },
    discountAmount: { type: Number, default: 0 },
    discountPercentage: { type: Number, default: 0 },
    
    issueDate: { type: Date, default: Date.now },
    expiryDate: { type: Date, required: true },
    status: { type: String, enum: Object.values(CERTIFICATE_STATUS), default: 'ISSUED' },
    
    payment: {
        amount: { type: Number, required: true },
        status: { type: String, enum: Object.values(PAYMENT_STATUS), default: 'PENDING' },
        paidAt: Date,
        transactionId: String
    },
    
    certificateHash: { type: String, required: true, unique: true },
    verificationUrl: { type: String },
    
    issuedBy: { type: String, required: true },
    issuedAt: { type: Date, default: Date.now },
    
    deleted: { type: Boolean, default: false }
}, { timestamps: true });

module.exports = mongoose.model('FidelityFund', fidelityFundSchema);
