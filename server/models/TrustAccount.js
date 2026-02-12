const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');

const TRANSACTION_TYPES = {
    DEPOSIT: 'DEPOSIT',
    WITHDRAWAL: 'WITHDRAWAL',
    TRANSFER: 'TRANSFER',
    INTEREST: 'INTEREST'
};

const TRANSACTION_STATUS = {
    PENDING: 'PENDING',
    COMPLETED: 'COMPLETED',
    FAILED: 'FAILED',
    REVERSED: 'REVERSED'
};

const trustAccountSchema = new mongoose.Schema({
    accountNumber: {
        type: String,
        required: true,
        unique: true,
        default: () => `TRUST-${uuidv4().toUpperCase()}`
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
    
    bankDetails: {
        bankName: { type: String, required: true },
        branchCode: { type: String, required: true },
        accountHolder: { type: String, required: true },
        accountType: { type: String, enum: ['CHEQUE', 'SAVINGS', 'TRANSMISSION'] }
    },
    
    balances: {
        current: { type: Number, default: 0 },
        available: { type: Number, default: 0 },
        lastUpdated: { type: Date, default: Date.now }
    },
    
    transactions: [{
        transactionId: { type: String, default: () => `TX-${uuidv4()}` },
        transactionType: { type: String, enum: Object.values(TRANSACTION_TYPES), required: true },
        amount: { type: Number, required: true },
        runningBalance: { type: Number, required: true },
        clientId: { type: String, required: true },
        matterReference: { type: String, required: true },
        description: String,
        status: { type: String, enum: Object.values(TRANSACTION_STATUS), default: 'COMPLETED' },
        processedAt: { type: Date, default: Date.now },
        processedBy: { type: String, required: true },
        transactionHash: { type: String, unique: true }
    }],
    
    status: { type: String, enum: ['ACTIVE', 'SUSPENDED', 'CLOSED'], default: 'ACTIVE' },
    openedAt: { type: Date, default: Date.now },
    openedBy: { type: String, required: true },
    deleted: { type: Boolean, default: false }
}, { timestamps: true });

module.exports = mongoose.model('TrustAccount', trustAccountSchema);
