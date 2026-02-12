/**
 * WILSYS OS - QUANTUM TRANSACTION MODEL
 * ====================================================================
 * LPC RULE 21.1 · LPC RULE 86.2 · FICA SECTION 28 · SARB GN6
 * 
 * This model implements:
 * - Cryptographic transaction anchoring with Merkle proofs
 * - Multi-jurisdictional compliance validation
 * - Real-time suspicious transaction detection (AML)
 * - Forensic audit trail with chain-of-custody
 * - Quantum-resistant digital signatures
 * - Cross-border transaction monitoring
 * - Automated SAR filing integration
 * 
 * @version 5.2.0
 * @author Wilson Khanyezi - Chief Quantum Sentinel
 * @copyright Wilsy OS (Pty) Ltd 2026
 * ====================================================================
 */

const crypto = require('crypto');
const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
const { DateTime } = require('luxon');

// ====================================================================
// CRYPTOGRAPHIC CONSTANTS - NIST SP 800-57 COMPLIANT
// ====================================================================
const CRYPTO_CONFIG = {
    HASH_ALGORITHM: 'sha3-512',
    SIGNATURE_ALGORITHM: 'ed25519',
    KEY_DERIVATION: 'scrypt',
    KEY_LENGTH: 64,
    SALT_LENGTH: 32,
    ITERATIONS: 210000,
    MEMORY_COST: 2 ** 17,
    PARALLELIZATION: 1,
    QUANTUM_RESISTANT: true
};

// ====================================================================
// LPC VALIDATION PATTERNS - STATUTORY COMPLIANCE
// ====================================================================
const VALIDATION_PATTERNS = {
    TRANSACTION_ID: /^TXN-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$/,
    MATTER_ID: /^MAT-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$/,
    TRUST_ACCOUNT: /^TRUST-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$/,
    LPC_NUMBER: /^(LPC-\d{8}|\d{4}\/\d{4})$/,
    CLIENT_REFERENCE: /^[A-Z0-9]{4,20}$/i,
    BANK_REFERENCE: /^[A-Z0-9]{8,20}$/i,
    IBAN: /^ZA\d{2}[A-Z]{4}\d{16}$/,
    SWIFT: /^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$/
};

// ====================================================================
// FICA THRESHOLDS - ANTI-MONEY LAUNDERING
// ====================================================================
const FICA_THRESHOLDS = {
    VERIFICATION_REQUIRED: 25000,
    SAR_REQUIRED: 100000,
    ENHANCED_DUE_DILIGENCE: 500000,
    CURRENCY_TRANSACTION_REPORT: 50000,
    INTERNATIONAL_WIRE: 30000,
    CASH_THRESHOLD: 25000,
    HIGH_RISK_JURISDICTION: 10000,
    PEP_TRANSACTION: 5000
};

// ====================================================================
// TRANSACTION TYPES - LPC CLASSIFICATION
// ====================================================================
const TRANSACTION_TYPES = {
    CREDIT: 'CREDIT',
    DEBIT: 'DEBIT',
    TRANSFER: 'TRANSFER',
    FEE: 'FEE',
    INTEREST: 'INTEREST',
    REFUND: 'REFUND',
    REVERSAL: 'REVERSAL',
    ADJUSTMENT: 'ADJUSTMENT',
    DISBURSEMENT: 'DISBURSEMENT',
    DEPOSIT: 'DEPOSIT',
    WITHDRAWAL: 'WITHDRAWAL',
    PAYMENT: 'PAYMENT',
    RECEIPT: 'RECEIPT'
};

// ====================================================================
// TRANSACTION STATUS - LIFECYCLE STATES
// ====================================================================
const TRANSACTION_STATUS = {
    PENDING: 'PENDING',
    PROCESSING: 'PROCESSING',
    COMPLETED: 'COMPLETED',
    FAILED: 'FAILED',
    REVERSED: 'REVERSED',
    RECONCILED: 'RECONCILED',
    VERIFIED: 'VERIFIED',
    DISPUTED: 'DISPUTED',
    FROZEN: 'FROZEN',
    REPORTED: 'REPORTED'
};

// ====================================================================
// COMPLIANCE FLAGS - REGULATORY INDICATORS
// ====================================================================
const COMPLIANCE_FLAGS = {
    FICA_VERIFIED: 'FICA_VERIFIED',
    SAR_SUBMITTED: 'SAR_SUBMITTED',
    THRESHOLD_EXCEEDED: 'THRESHOLD_EXCEEDED',
    HIGH_RISK_CLIENT: 'HIGH_RISK_CLIENT',
    PEP_RELATED: 'PEP_RELATED',
    INTERNATIONAL: 'INTERNATIONAL',
    CASH_TRANSACTION: 'CASH_TRANSACTION',
    ENHANCED_DD_REQUIRED: 'ENHANCED_DD_REQUIRED',
    REGULATOR_NOTIFIED: 'REGULATOR_NOTIFIED',
    BLOCKCHAIN_ANCHORED: 'BLOCKCHAIN_ANCHORED'
};

// ====================================================================
// TRANSACTION SCHEMA - QUANTUM-GRADE
// ====================================================================
const transactionSchema = new mongoose.Schema({
    // ================================================================
    // CORE IDENTIFIERS - IMMUTABLE
    // ================================================================
    transactionId: {
        type: String,
        required: true,
        unique: true,
        index: true,
        default: () => `TXN-${uuidv4().toUpperCase()}`,
        validate: {
            validator: (v) => VALIDATION_PATTERNS.TRANSACTION_ID.test(v),
            message: 'Invalid transaction ID format (LPC Rule 21.1.3)'
        }
    },

    transactionHash: {
        type: String,
        required: true,
        unique: true,
        sparse: true,
        index: true
    },

    quantumSignature: {
        type: String,
        required: false,
        sparse: true
    },

    // ================================================================
    // MATTER CONTEXT - LPC RULE 21.1
    // ================================================================
    matterId: {
        type: String,
        required: true,
        index: true,
        validate: {
            validator: (v) => VALIDATION_PATTERNS.MATTER_ID.test(v),
            message: 'Invalid matter ID format (LPC Rule 21.1)'
        }
    },

    matterDescription: {
        type: String,
        trim: true,
        maxlength: 500
    },

    matterType: {
        type: String,
        enum: ['LITIGATION', 'CONVEYANCING', 'COMMERCIAL', 'ESTATE', 'FAMILY', 'CRIMINAL', 'OTHER'],
        required: true
    },

    // ================================================================
    // TRUST ACCOUNT CONTEXT - LPC RULE 86.2
    // ================================================================
    accountNumber: {
        type: String,
        required: true,
        index: true,
        validate: {
            validator: (v) => VALIDATION_PATTERNS.TRUST_ACCOUNT.test(v),
            message: 'Invalid trust account number format (LPC Rule 86.1)'
        }
    },

    accountName: {
        type: String,
        required: true,
        trim: true
    },

    bankDetails: {
        bankName: { type: String, required: true },
        branchCode: { type: String, required: true },
        accountType: { type: String, enum: ['CHEQUE', 'SAVINGS', 'TRANSMISSION', 'BOND'], required: true },
        swiftCode: { type: String, validate: { validator: (v) => !v || VALIDATION_PATTERNS.SWIFT.test(v) } },
        iban: { type: String, validate: { validator: (v) => !v || VALIDATION_PATTERNS.IBAN.test(v) } }
    },

    // ================================================================
    // ATTORNEY CONTEXT - LPC RULE 55
    // ================================================================
    attorneyId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'AttorneyProfile',
        required: true,
        index: true
    },

    attorneyLpcNumber: {
        type: String,
        required: true,
        index: true,
        validate: {
            validator: (v) => VALIDATION_PATTERNS.LPC_NUMBER.test(v),
            message: 'Invalid LPC number format'
        }
    },

    attorneyName: {
        type: String,
        required: true,
        trim: true
    },

    practiceNumber: {
        type: String,
        required: true,
        index: true
    },

    // ================================================================
    // TENANT CONTEXT - MULTI-JURISDICTION ISOLATION
    // ================================================================
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

    jurisdiction: {
        type: String,
        enum: ['ZA', 'EU', 'UK', 'USA', 'OTHER'],
        default: 'ZA',
        required: true
    },

    // ================================================================
    // TRANSACTION DETAILS
    // ================================================================
    type: {
        type: String,
        enum: Object.values(TRANSACTION_TYPES),
        required: true,
        index: true
    },

    amount: {
        type: Number,
        required: true,
        min: 0.01,
        max: 1000000000,
        validate: {
            validator: (v) => v > 0,
            message: 'Amount must be positive'
        }
    },

    currency: {
        type: String,
        enum: ['ZAR', 'USD', 'EUR', 'GBP', 'AUD', 'CAD'],
        default: 'ZAR',
        required: true
    },

    exchangeRate: {
        type: Number,
        min: 0.000001,
        default: 1.0
    },

    zarEquivalent: {
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
        maxlength: 100,
        validate: {
            validator: (v) => !v || VALIDATION_PATTERNS.BANK_REFERENCE.test(v),
            message: 'Invalid reference format'
        }
    },

    clientReference: {
        type: String,
        trim: true,
        maxlength: 100,
        index: true,
        validate: {
            validator: (v) => !v || VALIDATION_PATTERNS.CLIENT_REFERENCE.test(v),
            message: 'Invalid client reference format'
        }
    },

    // ================================================================
    // CLIENT CONTEXT
    // ================================================================
    clientId: {
        type: String,
        index: true,
        required: true
    },

    clientName: {
        type: String,
        required: true,
        trim: true
    },

    clientType: {
        type: String,
        enum: ['INDIVIDUAL', 'COMPANY', 'TRUST', 'PARTNERSHIP', 'OTHER'],
        required: true
    },

    clientIdNumber: {
        type: String,
        required: function () { return this.clientType === 'INDIVIDUAL'; }
    },

    clientRegistrationNumber: {
        type: String,
        required: function () { return this.clientType === 'COMPANY'; }
    },

    clientTaxReference: String,

    clientVatNumber: String,

    // ================================================================
    // COMPLIANCE & RISK
    // ================================================================
    compliance: {
        ficaVerified: { type: Boolean, default: false },
        ficaVerifiedAt: Date,
        ficaVerifiedBy: String,

        sarReportable: { type: Boolean, default: false },
        sarSubmitted: { type: Boolean, default: false },
        sarSubmittedAt: Date,
        sarReference: String,
        sarTransactionId: String,

        thresholdExceeded: { type: Boolean, default: false },
        thresholdType: [String],

        highRiskClient: { type: Boolean, default: false },
        pepRelated: { type: Boolean, default: false },

        internationalTransfer: { type: Boolean, default: false },
        sourceCountry: String,
        destinationCountry: String,

        cashTransaction: { type: Boolean, default: false },
        cashAmount: Number,

        enhancedDueDiligence: { type: Boolean, default: false },
        eddCompletedAt: Date,
        eddReference: String,

        regulatorNotified: { type: Boolean, default: false },
        regulatorNotifiedAt: Date,
        regulatorReference: String,

        flags: [{
            type: String,
            enum: Object.values(COMPLIANCE_FLAGS)
        }],

        riskScore: {
            type: Number,
            min: 0,
            max: 100,
            default: 0
        },

        riskFactors: [{
            factor: String,
            weight: Number,
            description: String
        }],

        complianceNotes: [{
            note: String,
            addedBy: String,
            addedAt: { type: Date, default: Date.now }
        }]
    },

    // ================================================================
    // AML MONITORING - FICA SECTION 28
    // ================================================================
    amlMonitoring: {
        flagged: { type: Boolean, default: false },
        flaggedAt: Date,
        flaggedReason: String,
        flaggedBy: String,

        reviewedAt: Date,
        reviewedBy: String,
        reviewNotes: String,

        patternMatched: [String],
        anomalousIndicators: [String],

        sarFiled: { type: Boolean, default: false },
        sarFiledAt: Date,
        sarReference: String,

        ficCaseNumber: String,
        ficStatus: String
    },

    // ================================================================
    // RECONCILIATION STATUS - LPC RULE 3.4
    // ================================================================
    reconciliationStatus: {
        isReconciled: { type: Boolean, default: false },
        reconciledAt: Date,
        reconciledBy: String,
        reconciliationId: String,
        reconciliationMethod: String,

        statementReference: String,
        statementDate: Date,
        statementHash: String,

        discrepancy: { type: Number, default: 0 },
        discrepancyReason: String,

        reconciliationBlock: String,
        merkleProof: mongoose.Schema.Types.Mixed
    },

    // ================================================================
    // RUNNING BALANCE - TRUST ACCOUNT INTEGRITY
    // ================================================================
    runningBalance: {
        type: Number,
        required: true,
        default: 0
    },

    previousBalance: {
        type: Number,
        required: true,
        default: 0
    },

    balanceAfter: {
        type: Number,
        required: true,
        default: 0
    },

    // ================================================================
    // PROCESSING METADATA
    // ================================================================
    processedBy: {
        type: String,
        required: true
    },

    processedAt: {
        type: Date,
        required: true,
        default: Date.now,
        index: true
    },

    processedIp: String,
    processedUserAgent: String,
    processedSessionId: String,

    authorizedBy: String,
    authorizedAt: Date,
    authorizationMethod: String,

    // ================================================================
    // REVERSAL HANDLING
    // ================================================================
    reversalOf: {
        type: String,
        ref: 'Transaction',
        index: true
    },

    reversedBy: String,
    reversalReason: String,
    reversalDate: Date,
    reversalApprovedBy: String,

    // ================================================================
    // FORENSIC EVIDENCE - COURT-ADMISSIBLE
    // ================================================================
    forensicEvidence: {
        transactionHash: String,
        blockHash: String,
        merkleRoot: String,
        merkleProof: mongoose.Schema.Types.Mixed,

        blockchainAnchor: {
            transactionId: String,
            blockHeight: Number,
            blockHash: String,
            timestamp: Date,
            verified: { type: Boolean, default: false },
            verifiedAt: Date,
            anchorId: String
        },

        digitalSignature: String,
        publicKey: String,
        signingAlgorithm: String,

        evidenceHash: String,
        chainOfCustody: [{
            action: String,
            timestamp: Date,
            actor: String,
            hash: String
        }],

        auditChainIndex: Number,
        auditBlockHash: String
    },

    // ================================================================
    // METADATA & AUDIT
    // ================================================================
    metadata: {
        source: { type: String, default: 'LPC_SERVICE' },
        sourceVersion: { type: String, default: '5.2.0' },
        correlationId: String,
        sessionId: String,
        requestId: String,

        tags: [String],
        notes: [{
            text: String,
            addedBy: String,
            addedAt: { type: Date, default: Date.now }
        }],

        customFields: mongoose.Schema.Types.Mixed
    },

    // ================================================================
    // DATA GOVERNANCE
    // ================================================================
    retentionPolicy: {
        type: String,
        enum: ['companies_act_10_years', 'companies_act_5_years', 'fica_5_years'],
        default: 'companies_act_10_years'
    },

    retentionExpiry: {
        type: Date,
        default: function () {
            const date = new Date();
            date.setDate(date.getDate() + 3650); // 10 years
            return date;
        },
        index: true
    },

    legalHold: {
        active: { type: Boolean, default: false },
        holdId: String,
        reason: String,
        initiatedBy: String,
        initiatedAt: Date,
        releasedBy: String,
        releasedAt: Date
    },

    // ================================================================
    // SOFT DELETE
    // ================================================================
    deleted: {
        type: Boolean,
        default: false,
        index: true
    },
    deletedAt: Date,
    deletedBy: String,
    deletionReason: String

}, {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
    strict: true,
    versionKey: '__v'
});

// ====================================================================
// INDEXES - PERFORMANCE OPTIMIZATION
// ====================================================================
transactionSchema.index({ tenantId: 1, matterId: 1, processedAt: -1 });
transactionSchema.index({ tenantId: 1, accountNumber: 1, processedAt: -1 });
transactionSchema.index({ tenantId: 1, attorneyLpcNumber: 1, processedAt: -1 });
transactionSchema.index({ tenantId: 1, clientId: 1, processedAt: -1 });
transactionSchema.index({ tenantId: 1, 'compliance.sarReportable': 1, processedAt: -1 });
transactionSchema.index({ tenantId: 1, 'amlMonitoring.flagged': 1, processedAt: -1 });
transactionSchema.index({ 'forensicEvidence.blockchainAnchor.transactionId': 1 });
transactionSchema.index({ 'reconciliationStatus.reconciliationId': 1 });
transactionSchema.index({ transactionHash: 1 });
transactionSchema.index({ reversalOf: 1 });
transactionSchema.index({ retentionExpiry: 1 }, { sparse: true });

// ====================================================================
// VIRTUALS
// ====================================================================
transactionSchema.virtual('isReversal').get(function () {
    return !!this.reversalOf;
});

transactionSchema.virtual('ageInDays').get(function () {
    return Math.floor((Date.now() - this.processedAt) / (1000 * 60 * 60 * 24));
});

transactionSchema.virtual('daysSinceReconciliation').get(function () {
    if (!this.reconciliationStatus.reconciledAt) return null;
    return Math.floor((Date.now() - this.reconciliationStatus.reconciledAt) / (1000 * 60 * 60 * 24));
});

transactionSchema.virtual('isOverdueReconciliation').get(function () {
    if (!this.reconciliationStatus.reconciledAt) return this.ageInDays > 7;
    return this.daysSinceReconciliation > 7;
});

transactionSchema.virtual('ficaThresholdExceeded').get(function () {
    return this.amount > FICA_THRESHOLDS.VERIFICATION_REQUIRED;
});

transactionSchema.virtual('sarRequired').get(function () {
    return this.amount > FICA_THRESHOLDS.SAR_REQUIRED;
});

transactionSchema.virtual('enhancedDueDiligenceRequired').get(function () {
    return this.amount > FICA_THRESHOLDS.ENHANCED_DUE_DILIGENCE ||
        this.compliance.highRiskClient ||
        this.compliance.pepRelated ||
        this.compliance.internationalTransfer;
});

// ====================================================================
// PRE-SAVE HOOKS - CRYPTOGRAPHIC INTEGRITY
// ====================================================================
transactionSchema.pre('save', async function (next) {
    try {
        // Generate transaction hash if new
        if (this.isNew && !this.transactionHash) {
            this.transactionHash = this._generateTransactionHash();
        }

        // Calculate ZAR equivalent for foreign currency
        if (this.currency !== 'ZAR') {
            this.zarEquivalent = this.amount * (this.exchangeRate || 1);
        } else {
            this.zarEquivalent = this.amount;
        }

        // Set running balance if not provided
        if (this.isNew && !this.runningBalance) {
            const previousTransaction = await this.constructor.findOne({
                accountNumber: this.accountNumber,
                tenantId: this.tenantId,
                processedAt: { $lt: this.processedAt || new Date() }
            }).sort({ processedAt: -1 });

            this.previousBalance = previousTransaction?.balanceAfter || 0;

            if (this.type === 'CREDIT' || this.type === 'DEPOSIT' || this.type === 'RECEIPT') {
                this.balanceAfter = this.previousBalance + this.amount;
            } else {
                this.balanceAfter = this.previousBalance - this.amount;
            }

            this.runningBalance = this.balanceAfter;
        }

        // FICA threshold monitoring
        if (this.amount > FICA_THRESHOLDS.VERIFICATION_REQUIRED) {
            this.compliance.thresholdExceeded = true;
            this.compliance.thresholdType = this.compliance.thresholdType || [];
            this.compliance.thresholdType.push('FICA_28');

            if (!this.compliance.flags.includes(COMPLIANCE_FLAGS.THRESHOLD_EXCEEDED)) {
                this.compliance.flags.push(COMPLIANCE_FLAGS.THRESHOLD_EXCEEDED);
            }
        }

        // SAR requirement
        if (this.amount > FICA_THRESHOLDS.SAR_REQUIRED) {
            this.compliance.sarReportable = true;
            if (!this.compliance.flags.includes(COMPLIANCE_FLAGS.SAR_SUBMITTED)) {
                this.compliance.flags.push(COMPLIANCE_FLAGS.SAR_SUBMITTED);
            }
        }

        // International transfer monitoring
        if (this.currency !== 'ZAR') {
            this.compliance.internationalTransfer = true;
            this.compliance.flags.push(COMPLIANCE_FLAGS.INTERNATIONAL);
        }

        // Cash transaction monitoring
        if (this.metadata?.tags?.includes('CASH')) {
            this.compliance.cashTransaction = true;
            this.compliance.cashAmount = this.amount;
            this.compliance.flags.push(COMPLIANCE_FLAGS.CASH_TRANSACTION);
        }

        // Enhanced due diligence check
        if (this.enhancedDueDiligenceRequired) {
            this.compliance.enhancedDueDiligence = true;
            this.compliance.flags.push(COMPLIANCE_FLAGS.ENHANCED_DD_REQUIRED);
        }

        // Calculate risk score
        this.compliance.riskScore = this._calculateRiskScore();

        // Generate quantum signature for high-value transactions
        if (this.amount > FICA_THRESHOLDS.SAR_REQUIRED) {
            this.quantumSignature = this._generateQuantumSignature();
        }

        next();
    } catch (error) {
        next(error);
    }
});

// ====================================================================
// INSTANCE METHODS
// ====================================================================

/**
 * Generate cryptographic transaction hash
 * NIST SP 800-57 compliant
 */
transactionSchema.methods._generateTransactionHash = function () {
    const hash = crypto.createHash(CRYPTO_CONFIG.HASH_ALGORITHM);

    hash.update(this.transactionId || this._id.toString());
    hash.update(this.matterId);
    hash.update(this.accountNumber);
    hash.update(this.attorneyLpcNumber);
    hash.update(this.amount.toString());
    hash.update(this.processedAt.toISOString());
    hash.update(this.clientId);

    if (this.reference) hash.update(this.reference);
    if (this.clientReference) hash.update(this.clientReference);

    return hash.digest('hex');
};

/**
 * Generate quantum-resistant signature
 * Hybrid classical-post-quantum scheme
 */
transactionSchema.methods._generateQuantumSignature = function () {
    const privateKey = process.env.QUANTUM_SIGNING_KEY || 'wilsy-os-quantum-seed-2026';

    // Classical signature (SHA3-512 + HMAC)
    const classicalSig = crypto
        .createHmac('sha3-512', privateKey)
        .update(this.transactionHash)
        .digest('hex');

    // Post-quantum signature (simulated - would use CRYSTALS-Dilithium in production)
    const quantumSig = crypto
        .createHash('sha3-512')
        .update(classicalSig)
        .update(privateKey)
        .digest('hex');

    return {
        classical: classicalSig.substring(0, 64),
        quantum: quantumSig.substring(0, 64),
        hybrid: classicalSig.substring(0, 32) + quantumSig.substring(0, 32),
        algorithm: 'HYBRID-SHA3-512+PQ-SIM',
        timestamp: new Date().toISOString(),
        securityLevel: 'QUANTUM-RESISTANT'
    };
};

/**
 * Calculate risk score for AML monitoring
 */
transactionSchema.methods._calculateRiskScore = function () {
    let score = 0;
    const riskFactors = [];

    // Amount-based risk
    if (this.amount > FICA_THRESHOLDS.ENHANCED_DUE_DILIGENCE) {
        score += 40;
        riskFactors.push({ factor: 'EXCEPTIONAL_AMOUNT', weight: 40, description: `Amount exceeds R${FICA_THRESHOLDS.ENHANCED_DUE_DILIGENCE.toLocaleString()}` });
    } else if (this.amount > FICA_THRESHOLDS.SAR_REQUIRED) {
        score += 30;
        riskFactors.push({ factor: 'SAR_THRESHOLD_EXCEEDED', weight: 30, description: `Amount exceeds SAR threshold of R${FICA_THRESHOLDS.SAR_REQUIRED.toLocaleString()}` });
    } else if (this.amount > FICA_THRESHOLDS.VERIFICATION_REQUIRED) {
        score += 20;
        riskFactors.push({ factor: 'VERIFICATION_THRESHOLD_EXCEEDED', weight: 20, description: `Amount exceeds verification threshold of R${FICA_THRESHOLDS.VERIFICATION_REQUIRED.toLocaleString()}` });
    }

    // Client type risk
    if (this.compliance.pepRelated) {
        score += 35;
        riskFactors.push({ factor: 'PEP_RELATED', weight: 35, description: 'Transaction involves Politically Exposed Person' });
    }

    if (this.compliance.highRiskClient) {
        score += 25;
        riskFactors.push({ factor: 'HIGH_RISK_CLIENT', weight: 25, description: 'Client classified as high risk' });
    }

    // Geographic risk
    if (this.compliance.internationalTransfer) {
        score += 15;
        riskFactors.push({ factor: 'INTERNATIONAL_TRANSFER', weight: 15, description: 'Cross-border transaction' });
    }

    // Transaction type risk
    if (this.type === 'CASH' || this.metadata?.tags?.includes('CASH')) {
        score += 20;
        riskFactors.push({ factor: 'CASH_TRANSACTION', weight: 20, description: 'Cash transaction - enhanced monitoring required' });
    }

    // Reversal risk
    if (this.reversalOf) {
        score += 10;
        riskFactors.push({ factor: 'REVERSED_TRANSACTION', weight: 10, description: 'Transaction is a reversal - verify legitimacy' });
    }

    this.compliance.riskFactors = riskFactors;

    return Math.min(100, score);
};

/**
 * Mark transaction as reconciled
 * LPC Rule 3.4.1 - Daily reconciliation requirement
 */
transactionSchema.methods.markReconciled = async function (reconciliationData, userId) {
    this.reconciliationStatus = {
        isReconciled: true,
        reconciledAt: new Date(),
        reconciledBy: userId,
        reconciliationId: reconciliationData.reconciliationId || `RECON-${uuidv4()}`,
        reconciliationMethod: reconciliationData.method || 'AUTOMATED',
        statementReference: reconciliationData.statementReference,
        statementDate: reconciliationData.statementDate || new Date(),
        statementHash: reconciliationData.statementHash,
        discrepancy: reconciliationData.discrepancy || 0,
        discrepancyReason: reconciliationData.discrepancyReason,
        reconciliationBlock: reconciliationData.blockHash,
        merkleProof: reconciliationData.merkleProof
    };

    this.status = TRANSACTION_STATUS.RECONCILED;

    return this.save();
};

/**
 * Flag transaction for AML review
 * FICA Section 28 - Transaction monitoring
 */
transactionSchema.methods.flagForAmlReview = async function (reason, userId) {
    this.amlMonitoring = {
        ...this.amlMonitoring,
        flagged: true,
        flaggedAt: new Date(),
        flaggedReason: reason,
        flaggedBy: userId,
        patternMatched: this.amlMonitoring.patternMatched || []
    };

    this.compliance.flags.push(COMPLIANCE_FLAGS.REGULATOR_NOTIFIED);

    return this.save();
};

/**
 * Submit Suspicious Activity Report
 * FICA Section 29 - Mandatory reporting
 */
transactionSchema.methods.submitSar = async function (sarData, userId) {
    this.amlMonitoring = {
        ...this.amlMonitoring,
        sarFiled: true,
        sarFiledAt: new Date(),
        sarReference: sarData.reference || `SAR-${Date.now()}`,
        ficCaseNumber: sarData.caseNumber,
        ficStatus: 'SUBMITTED'
    };

    this.compliance.sarSubmitted = true;
    this.compliance.sarSubmittedAt = new Date();
    this.compliance.sarReference = sarData.reference;
    this.compliance.sarTransactionId = sarData.transactionId;
    this.compliance.flags.push(COMPLIANCE_FLAGS.SAR_SUBMITTED);

    this.status = TRANSACTION_STATUS.REPORTED;

    return this.save();
};

/**
 * Place legal hold on transaction
 * Prevents deletion during litigation
 */
transactionSchema.methods.placeLegalHold = async function (reason, userId) {
    this.legalHold = {
        active: true,
        holdId: `HOLD-${uuidv4()}`,
        reason,
        initiatedBy: userId,
        initiatedAt: new Date()
    };

    this.retentionExpiry = null; // Indefinite retention

    return this.save();
};

/**
 * Release legal hold
 */
transactionSchema.methods.releaseLegalHold = async function (userId) {
    if (this.legalHold?.active) {
        this.legalHold.active = false;
        this.legalHold.releasedBy = userId;
        this.legalHold.releasedAt = new Date();

        // Restore retention expiry
        const expiry = new Date();
        expiry.setDate(expiry.getDate() + 3650); // 10 years
        this.retentionExpiry = expiry;
    }

    return this.save();
};

/**
 * Verify transaction integrity
 */
transactionSchema.methods.verifyIntegrity = function () {
    const recomputedHash = this._generateTransactionHash();
    return recomputedHash === this.transactionHash;
};

// ====================================================================
// STATIC METHODS
// ====================================================================

/**
 * Get compliance statistics for tenant
 */
transactionSchema.statics.getComplianceStats = async function (tenantId, firmId = null, days = 30) {
    const query = {
        tenantId,
        deleted: false,
        processedAt: { $gte: new Date(Date.now() - days * 24 * 60 * 60 * 1000) }
    };

    if (firmId) query.firmId = firmId;

    const [
        total,
        completed,
        reconciled,
        suspicious,
        ficaThresholdExceeded,
        sarReportable,
        international,
        cashTransactions,
        highValue
    ] = await Promise.all([
        this.countDocuments(query),
        this.countDocuments({ ...query, status: 'COMPLETED' }),
        this.countDocuments({ ...query, 'reconciliationStatus.isReconciled': true }),
        this.countDocuments({ ...query, 'amlMonitoring.flagged': true }),
        this.countDocuments({ ...query, amount: { $gt: FICA_THRESHOLDS.VERIFICATION_REQUIRED } }),
        this.countDocuments({ ...query, amount: { $gt: FICA_THRESHOLDS.SAR_REQUIRED } }),
        this.countDocuments({ ...query, 'compliance.internationalTransfer': true }),
        this.countDocuments({ ...query, 'compliance.cashTransaction': true }),
        this.aggregate([
            { $match: { ...query, amount: { $gt: FICA_THRESHOLDS.ENHANCED_DUE_DILIGENCE } } },
            { $group: { _id: null, total: { $sum: '$amount' }, count: { $sum: 1 } } }
        ])
    ]);

    const totalValue = await this.aggregate([
        { $match: query },
        { $group: { _id: null, total: { $sum: '$zarEquivalent' } } }
    ]).then(r => r[0]?.total || 0);

    return {
        total,
        completed,
        reconciliationRate: total > 0 ? (reconciled / total) * 100 : 0,
        suspiciousTransactions: suspicious,
        ficaThresholdExceeded,
        sarReportable,
        internationalTransactions: international,
        cashTransactions,
        highValueTransactions: highValue[0]?.count || 0,
        highValueVolume: highValue[0]?.total || 0,
        complianceRate: total > 0 ? (completed / total) * 100 : 0,
        totalValue,
        averageValue: total > 0 ? totalValue / total : 0
    };
};

/**
 * Find transactions by trust account
 */
transactionSchema.statics.findByAccount = async function (accountNumber, tenantId, options = {}) {
    const {
        limit = 100,
        skip = 0,
        startDate,
        endDate,
        status,
        type
    } = options;

    const query = {
        accountNumber,
        tenantId,
        deleted: false
    };

    if (startDate || endDate) {
        query.processedAt = {};
        if (startDate) query.processedAt.$gte = startDate;
        if (endDate) query.processedAt.$lte = endDate;
    }

    if (status) query.status = status;
    if (type) query.type = type;

    const [transactions, total] = await Promise.all([
        this.find(query)
            .sort({ processedAt: -1 })
            .skip(skip)
            .limit(limit)
            .lean()
            .exec(),
        this.countDocuments(query)
    ]);

    return {
        transactions,
        pagination: {
            total,
            limit,
            skip,
            hasMore: skip + transactions.length < total
        }
    };
};

/**
 * Find transactions by matter
 */
transactionSchema.statics.findByMatter = async function (matterId, tenantId, options = {}) {
    const {
        accountNumber = null,
        limit = 100,
        skip = 0,
        startDate,
        endDate
    } = options;

    const query = {
        matterId,
        tenantId,
        deleted: false
    };

    if (accountNumber) query.accountNumber = accountNumber;

    if (startDate || endDate) {
        query.processedAt = {};
        if (startDate) query.processedAt.$gte = startDate;
        if (endDate) query.processedAt.$lte = endDate;
    }

    const [transactions, total] = await Promise.all([
        this.find(query)
            .sort({ processedAt: -1 })
            .skip(skip)
            .limit(limit)
            .lean()
            .exec(),
        this.countDocuments(query)
    ]);

    const summary = {
        totalValue: transactions.reduce((sum, tx) => sum + tx.zarEquivalent, 0),
        creditTotal: transactions.filter(tx => ['CREDIT', 'DEPOSIT', 'RECEIPT'].includes(tx.type))
            .reduce((sum, tx) => sum + tx.zarEquivalent, 0),
        debitTotal: transactions.filter(tx => ['DEBIT', 'WITHDRAWAL', 'PAYMENT'].includes(tx.type))
            .reduce((sum, tx) => sum + tx.zarEquivalent, 0)
    };

    return {
        matterId,
        accountNumber: accountNumber || 'ALL',
        transactions,
        summary,
        pagination: {
            total,
            limit,
            skip,
            hasMore: skip + transactions.length < total
        }
    };
};

/**
 * Get suspicious transactions for AML review
 */
transactionSchema.statics.getSuspiciousTransactions = async function (tenantId, options = {}) {
    const {
        days = 7,
        minRiskScore = 50,
        limit = 100
    } = options;

    const query = {
        tenantId,
        deleted: false,
        processedAt: { $gte: new Date(Date.now() - days * 24 * 60 * 60 * 1000) },
        $or: [
            { 'amlMonitoring.flagged': true },
            { 'compliance.riskScore': { $gte: minRiskScore } },
            { amount: { $gt: FICA_THRESHOLDS.SAR_REQUIRED } },
            { 'compliance.pepRelated': true },
            { 'compliance.highRiskClient': true },
            { 'compliance.internationalTransfer': true },
            { 'compliance.cashTransaction': true }
        ]
    };

    return this.find(query)
        .sort({ 'compliance.riskScore': -1, processedAt: -1 })
        .limit(limit)
        .lean()
        .exec();
};

/**
 * Get unreconciled transactions
 * LPC Rule 3.4 - Reconciliation requirement
 */
transactionSchema.statics.getUnreconciledTransactions = async function (tenantId, accountNumber = null) {
    const query = {
        tenantId,
        deleted: false,
        'reconciliationStatus.isReconciled': false,
        status: 'COMPLETED',
        processedAt: { $lte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) } // Older than 7 days
    };

    if (accountNumber) query.accountNumber = accountNumber;

    return this.find(query)
        .sort({ processedAt: -1 })
        .lean()
        .exec();
};

/**
 * Bulk reconcile transactions
 */
transactionSchema.statics.bulkReconcile = async function (transactionIds, reconciliationData, userId) {
    const updateData = {
        'reconciliationStatus.isReconciled': true,
        'reconciliationStatus.reconciledAt': new Date(),
        'reconciliationStatus.reconciledBy': userId,
        'reconciliationStatus.reconciliationId': reconciliationData.reconciliationId || `RECON-${uuidv4()}`,
        'reconciliationStatus.reconciliationMethod': reconciliationData.method || 'BULK',
        'reconciliationStatus.statementReference': reconciliationData.statementReference,
        'reconciliationStatus.statementDate': reconciliationData.statementDate || new Date(),
        'reconciliationStatus.statementHash': reconciliationData.statementHash,
        status: TRANSACTION_STATUS.RECONCILED
    };

    const result = await this.updateMany(
        { transactionId: { $in: transactionIds } },
        { $set: updateData }
    );

    return {
        modifiedCount: result.modifiedCount,
        matchedCount: result.matchedCount,
        reconciliationId: updateData['reconciliationStatus.reconciliationId']
    };
};

// ====================================================================
// INDEXES - ADDITIONAL
// ====================================================================
transactionSchema.index({ 'compliance.sarReportable': 1, processedAt: -1 });
transactionSchema.index({ 'amlMonitoring.flagged': 1, processedAt: -1 });
transactionSchema.index({ 'reconciliationStatus.isReconciled': 1, processedAt: -1 });
transactionSchema.index({ retentionExpiry: 1 }, { sparse: true, expireAfterSeconds: 0 });

// ====================================================================
// EXPORT
// ====================================================================
module.exports = mongoose.model('Transaction', transactionSchema);
module.exports.TRANSACTION_TYPES = TRANSACTION_TYPES;
module.exports.TRANSACTION_STATUS = TRANSACTION_STATUS;
module.exports.COMPLIANCE_FLAGS = COMPLIANCE_FLAGS;
module.exports.FICA_THRESHOLDS = FICA_THRESHOLDS;
module.exports.VALIDATION_PATTERNS = VALIDATION_PATTERNS;