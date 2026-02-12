/**
 * WILSYS OS - TRUST ACCOUNT MODEL
 * ====================================================================
 * LEGAL PRACTICE COUNCIL · FORENSIC TRUST ACCOUNTING
 * @version 5.0.2
 * ====================================================================
 */

const mongoose = require('mongoose');
const { Schema } = mongoose;
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');

const TRANSACTION_TYPES = { DEPOSIT: 'DEPOSIT', WITHDRAWAL: 'WITHDRAWAL', TRANSFER: 'TRANSFER', INTEREST: 'INTEREST', REFUND: 'REFUND', FEE: 'FEE', CORRECTION: 'CORRECTION', REVERSAL: 'REVERSAL' };
const TRANSACTION_PURPOSES = { LEGAL_FEES: 'LEGAL_FEES', DISBURSEMENTS: 'DISBURSEMENTS', CLIENT_REFUND: 'CLIENT_REFUND', COURT_FEES: 'COURT_FEES', SHERIFF_FEES: 'SHERIFF_FEES', EXPERT_WITNESS_FEES: 'EXPERT_WITNESS_FEES', MEDIATION_FEES: 'MEDIATION_FEES', ARBITRATION_FEES: 'ARBITRATION_FEES', COUNSEL_FEES: 'COUNSEL_FEES', INVESTIGATION_FEES: 'INVESTIGATION_FEES', SETTLEMENT_FUNDS: 'SETTLEMENT_FUNDS', TRUST_TRANSFER: 'TRUST_TRANSFER' };
const TRANSACTION_STATUS = { PENDING: 'PENDING', COMPLETED: 'COMPLETED', FAILED: 'FAILED', REVERSED: 'REVERSED', CANCELLED: 'CANCELLED', DISPUTED: 'DISPUTED' };
const RECONCILIATION_STATUS = { PENDING: 'PENDING', IN_PROGRESS: 'IN_PROGRESS', COMPLETED: 'COMPLETED', FAILED: 'FAILED', DISPUTED: 'DISPUTED', WAIVED: 'WAIVED' };
const ACCOUNT_STATUS = { ACTIVE: 'ACTIVE', SUSPENDED: 'SUSPENDED', CLOSED: 'CLOSED', PENDING_VERIFICATION: 'PENDING_VERIFICATION', FROZEN: 'FROZEN' };
const BANK_ACCOUNT_TYPES = { CHEQUE: 'CHEQUE', SAVINGS: 'SAVINGS', TRANSMISSION: 'TRANSMISSION', INTEREST_BEARING: 'INTEREST_BEARING' };
const BANKS = { ABSA: 'ABSA', FNB: 'FNB', NEDBANK: 'NEDBANK', STANDARD_BANK: 'STANDARD_BANK', CAPITEC: 'CAPITEC', AFRICAN_BANK: 'AFRICAN_BANK', BIDVEST_BANK: 'BIDVEST_BANK', DISCOVERY_BANK: 'DISCOVERY_BANK', TYMEBANK: 'TYMEBANK', INVESTEC: 'INVESTEC' };

const trustAccountSchema = new Schema({
    tenantId: { 
        type: String, 
        required: [true, 'TENANT_ISOLATION_VIOLATION: tenantId is required'], 
        index: true, 
        immutable: true, 
        validate: { 
            validator: function(v) { 
                return /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(v); 
            },
            message: function(props) { 
                return `${props.value} is not a valid tenant UUID`; 
            }
        } 
    },
    accountNumber: { 
        type: String, 
        required: [true, 'Trust account number is required'], 
        unique: true, 
        immutable: true, 
        default: function() { 
            return `TRUST-${uuidv4().toUpperCase()}`; 
        }, 
        validate: { 
            validator: function(v) { 
                return /^TRUST-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$/.test(v); 
            },
            message: function(props) { 
                return `${props.value} is not a valid trust account number`; 
            }
        }, 
        index: true 
    },
    attorneyId: { type: Schema.Types.ObjectId, ref: 'AttorneyProfile', required: true, index: true },
    attorneyLpcNumber: { 
        type: String, 
        required: true, 
        index: true, 
        validate: { 
            validator: function(v) { 
                return /^(LPC-\d{8}|\d{4}\/\d{4})$/.test(v); 
            },
            message: function(props) { 
                return `${props.value} is not a valid LPC number`; 
            }
        } 
    },
    firmId: { type: Schema.Types.ObjectId, ref: 'Firm', required: true, index: true },
    bankDetails: {
        bankName: { type: String, required: true, enum: Object.values(BANKS) },
        branchCode: { 
            type: String, 
            required: true, 
            validate: { 
                validator: function(v) { 
                    return /^\d{6}$/.test(v); 
                },
                message: function(props) { 
                    return `${props.value} is not a valid branch code`; 
                }
            } 
        },
        accountHolder: { type: String, required: true, trim: true },
        accountNumber: { 
            type: String, 
            required: true, 
            validate: { 
                validator: function(v) { 
                    return /^\d{6,10}$/.test(v); 
                },
                message: function(props) { 
                    return `${props.value} is not a valid account number`; 
                }
            } 
        },
        accountType: { type: String, required: true, enum: Object.values(BANK_ACCOUNT_TYPES) },
        swiftCode: { 
            type: String, 
            validate: { 
                validator: function(v) { 
                    return !v || /^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$/.test(v); 
                } 
            } 
        },
        iban: { type: String, sparse: true },
        encrypted: { type: Boolean, default: true },
        encryptionKeyId: String,
        lastVerifiedAt: Date,
        verifiedBy: String
    },
    balances: {
        current: { 
            type: Number, 
            required: true, 
            default: 0, 
            min: 0, 
            get: function(v) { return parseFloat(v.toFixed(2)); }, 
            set: function(v) { return parseFloat(v.toFixed(2)); } 
        },
        available: { 
            type: Number, 
            required: true, 
            default: 0, 
            min: 0, 
            get: function(v) { return parseFloat(v.toFixed(2)); }, 
            set: function(v) { return parseFloat(v.toFixed(2)); } 
        },
        pending: { 
            type: Number, 
            default: 0, 
            get: function(v) { return parseFloat(v.toFixed(2)); }, 
            set: function(v) { return parseFloat(v.toFixed(2)); } 
        },
        interestEarned: { 
            type: Number, 
            default: 0, 
            get: function(v) { return parseFloat(v.toFixed(2)); } 
        },
        interestPaid: { 
            type: Number, 
            default: 0, 
            get: function(v) { return parseFloat(v.toFixed(2)); } 
        },
        lastUpdated: { type: Date, default: Date.now },
        lastInterestCalculation: Date
    },
    clientBalances: [{
        clientId: { type: String, required: true, index: true },
        clientName: { type: String, required: true, trim: true },
        clientReference: String,
        matterReference: { type: String, required: true, index: true },
        balance: { 
            type: Number, 
            required: true, 
            default: 0, 
            get: function(v) { return parseFloat(v.toFixed(2)); }, 
            set: function(v) { return parseFloat(v.toFixed(2)); } 
        },
        pending: { 
            type: Number, 
            default: 0, 
            get: function(v) { return parseFloat(v.toFixed(2)); } 
        },
        lastTransaction: Date,
        lastTransactionId: String,
        transactionCount: { type: Number, default: 0 },
        status: { type: String, enum: ['ACTIVE', 'INACTIVE', 'CLOSED', 'SUSPENDED'], default: 'ACTIVE' },
        openedAt: { type: Date, default: Date.now },
        closedAt: Date,
        openedBy: String,
        closedBy: String,
        closureReason: String
    }],
    transactions: [{
        transactionId: { 
            type: String, 
            required: true, 
            unique: true, 
            default: function() { 
                return `TX-${uuidv4()}`; 
            }, 
            index: true 
        },
        transactionType: { type: String, required: true, enum: Object.values(TRANSACTION_TYPES) },
        purpose: { type: String, required: true, enum: Object.values(TRANSACTION_PURPOSES) },
        amount: { 
            type: Number, 
            required: true, 
            min: 0.01, 
            get: function(v) { return parseFloat(v.toFixed(2)); }, 
            set: function(v) { return parseFloat(v.toFixed(2)); } 
        },
        runningBalance: { 
            type: Number, 
            required: true, 
            get: function(v) { return parseFloat(v.toFixed(2)); }, 
            set: function(v) { return parseFloat(v.toFixed(2)); } 
        },
        clientId: { type: String, required: true, index: true },
        clientName: { type: String, required: true },
        matterReference: { type: String, required: true, index: true },
        description: { type: String, required: true, trim: true, maxlength: 500 },
        reference: { type: String, required: true, trim: true },
        status: { type: String, enum: Object.values(TRANSACTION_STATUS), default: 'COMPLETED' },
        processedAt: { type: Date, default: Date.now, immutable: true, index: true },
        processedBy: { type: String, required: true },
        ipAddress: String,
        userAgent: String,
        previousHash: { type: String, required: true, default: 'GENESIS' },
        transactionHash: { type: String, required: true, unique: true },
        merkleProof: Schema.Types.Mixed,
        nonce: { 
            type: String, 
            default: function() { 
                return crypto.randomBytes(16).toString('hex'); 
            } 
        },
        reversedBy: String,
        reversedAt: Date,
        reversalReason: String,
        reversalTransactionId: String,
        isReversal: { type: Boolean, default: false },
        originalTransactionId: String
    }],
    reconciliations: [{
        reconciliationId: { 
            type: String, 
            required: true, 
            unique: true, 
            default: function() { 
                return `RECON-${uuidv4()}`; 
            } 
        },
        status: { type: String, enum: Object.values(RECONCILIATION_STATUS), default: 'PENDING' },
        startedAt: { type: Date, default: Date.now },
        completedAt: Date,
        performedBy: String,
        ipAddress: String,
        systemBalance: { 
            type: Number, 
            required: true, 
            get: function(v) { return parseFloat(v.toFixed(2)); } 
        },
        bankBalance: { 
            type: Number, 
            required: true, 
            get: function(v) { return parseFloat(v.toFixed(2)); } 
        },
        discrepancy: { 
            type: Number, 
            default: 0, 
            get: function(v) { return parseFloat(v.toFixed(2)); } 
        },
        isReconciled: { 
            type: Boolean, 
            default: function() { 
                return Math.abs(this.discrepancy) <= 0.01; 
            } 
        },
        transactionCount: { type: Number, default: 0 },
        verifiedTransactions: [String],
        discrepancies: [{
            transactionId: String,
            expectedAmount: Number,
            actualAmount: Number,
            difference: Number,
            reason: String,
            resolved: { type: Boolean, default: false },
            resolvedAt: Date,
            resolvedBy: String
        }],
        statementDate: Date,
        statementReference: String,
        statementHash: { 
            type: String, 
            validate: { 
                validator: function(v) { 
                    return !v || /^[a-f0-9]{64}$/i.test(v); 
                } 
            } 
        },
        statementFile: String,
        verifiedAt: Date,
        verifiedBy: String,
        verificationHash: String,
        notes: String
    }],
    interestSettings: {
        rate: { type: Number, default: 0.025, min: 0, max: 0.1 },
        calculationBasis: { type: String, enum: ['DAILY', 'MONTHLY', 'QUARTERLY'], default: 'DAILY' },
        paymentThreshold: { type: Number, default: 5000, min: 0 },
        minimumInterest: { type: Number, default: 1.00, min: 0 },
        lastCalculatedAt: Date,
        lastPaidAt: Date,
        interestAccount: String
    },
    compliance: {
        lastReconciliationDate: Date,
        nextReconciliationDue: { 
            type: Date, 
            default: function() { 
                const d = new Date(); 
                d.setDate(d.getDate() + 7); 
                return d; 
            }, 
            index: true 
        },
        reconciliationScore: { type: Number, min: 0, max: 100, default: 100 },
        overdueReconciliations: { type: Number, default: 0 },
        consecutiveReconciliations: { type: Number, default: 0 },
        flags: [{
            type: { 
                type: String, 
                enum: ['LOW_BALANCE', 'NEGATIVE_BALANCE', 'UNRECONCILED', 'INTEREST_DUE', 'EXPIRING_CERTIFICATE', 'DISCREPANCY_DETECTED', 'CLIENT_BALANCE_NEGATIVE', 'SUSPICIOUS_ACTIVITY'] 
            },
            severity: { type: String, enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] },
            description: String,
            raisedAt: { type: Date, default: Date.now },
            resolvedAt: Date,
            resolvedBy: String,
            resolution: String
        }]
    },
    auditTrail: [{
        action: { 
            type: String, 
            enum: ['ACCOUNT_CREATED', 'ACCOUNT_UPDATED', 'ACCOUNT_CLOSED', 'ACCOUNT_SUSPENDED', 'ACCOUNT_REACTIVATED', 'TRANSACTION_PROCESSED', 'TRANSACTION_REVERSED', 'RECONCILIATION_COMPLETED', 'RECONCILIATION_FAILED', 'INTEREST_CALCULATED', 'INTEREST_PAID', 'CLIENT_BALANCE_UPDATED', 'BANK_DETAILS_UPDATED', 'COMPLIANCE_FLAG_RAISED', 'COMPLIANCE_FLAG_RESOLVED'] 
        },
        performedBy: String,
        performedAt: { type: Date, default: Date.now },
        ipAddress: String,
        userAgent: String,
        changes: Schema.Types.Mixed,
        previousState: Schema.Types.Mixed,
        newState: Schema.Types.Mixed,
        transactionId: String,
        reconciliationId: String,
        hash: { 
            type: String, 
            default: function() { 
                return crypto.createHash('sha3-512').update(`${this.action}:${this.performedAt.toISOString()}:${this.performedBy}:${JSON.stringify(this.changes)}`).digest('hex'); 
            } 
        }
    }],
    integrityHash: { 
        type: String, 
        unique: true, 
        default: function() { 
            return crypto.createHash('sha3-512').update(`${this.accountNumber}:${this.balances.current}:${this.updatedAt || Date.now()}`).digest('hex'); 
        } 
    },
    quantumSignature: { 
        type: String, 
        default: function() { 
            return crypto.createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026').update(`${this._id}:${this.accountNumber}:${this.integrityHash}`).digest('hex'); 
        } 
    },
    status: { type: String, enum: Object.values(ACCOUNT_STATUS), default: 'PENDING_VERIFICATION', index: true },
    statusReason: String,
    statusChangedAt: Date,
    statusChangedBy: String,
    openedAt: { type: Date, default: Date.now, immutable: true },
    openedBy: { type: String, required: true, immutable: true },
    closedAt: Date,
    closedBy: String,
    closureReason: String,
    retentionPolicy: { type: String, default: 'companies_act_10_years' },
    retentionStart: { type: Date, default: Date.now, immutable: true },
    retentionExpiry: { 
        type: Date, 
        default: function() { 
            const d = new Date(); 
            d.setFullYear(d.getFullYear() + 10); 
            return d; 
        }, 
        index: true 
    },
    dataResidency: { type: String, default: 'ZA', enum: ['ZA', 'EU', 'US', 'AU', 'UK'] },
    metadata: { type: Map, of: Schema.Types.Mixed },
    deleted: { type: Boolean, default: false, index: true },
    deletedAt: Date,
    deletedBy: String,
    deletionReason: String,
    deletionAuthorization: String
}, { 
    timestamps: true, 
    toJSON: { 
        virtuals: true, 
        transform: function(doc, ret) { 
            delete ret.__v; 
            delete ret.auditTrail; 
            delete ret.integrityHash; 
            delete ret.quantumSignature; 
            delete ret.bankDetails.accountNumber; 
            delete ret.bankDetails.swiftCode; 
            delete ret.bankDetails.iban; 
            return ret; 
        } 
    } 
});

// ====================================================================
// VIRTUAL FIELDS
// ====================================================================

trustAccountSchema.virtual('accountAge').get(function() { 
    return Math.floor((Date.now() - this.openedAt) / (1000 * 60 * 60 * 24)); 
});

trustAccountSchema.virtual('daysSinceLastReconciliation').get(function() { 
    return this.compliance.lastReconciliationDate 
        ? Math.floor((Date.now() - this.compliance.lastReconciliationDate) / (1000 * 60 * 60 * 24)) 
        : Infinity; 
});

trustAccountSchema.virtual('isOverdue').get(function() { 
    return this.compliance.nextReconciliationDue < new Date(); 
});

trustAccountSchema.virtual('totalClientCount').get(function() { 
    return this.clientBalances.filter(function(c) { 
        return c.status === 'ACTIVE'; 
    }).length; 
});

trustAccountSchema.virtual('averageClientBalance').get(function() { 
    const active = this.clientBalances.filter(function(c) { 
        return c.status === 'ACTIVE'; 
    }); 
    if (active.length === 0) return 0; 
    const sum = active.reduce(function(s, c) { 
        return s + c.balance; 
    }, 0); 
    return parseFloat((sum / active.length).toFixed(2)); 
});

trustAccountSchema.virtual('hasNegativeBalances').get(function() { 
    return this.clientBalances.some(function(c) { 
        return c.balance < 0; 
    }) || this.balances.current < 0; 
});

// ====================================================================
// INDEXES
// ====================================================================

trustAccountSchema.index({ tenantId: 1, accountNumber: 1 }, { unique: true });
trustAccountSchema.index({ tenantId: 1, attorneyId: 1, status: 1 });
trustAccountSchema.index({ tenantId: 1, 'compliance.nextReconciliationDue': 1 });
trustAccountSchema.index({ 'transactions.transactionId': 1 }, { unique: true, sparse: true });
trustAccountSchema.index({ 'transactions.clientId': 1, 'transactions.processedAt': -1 });
trustAccountSchema.index({ 'transactions.transactionHash': 1 }, { unique: true, sparse: true });
trustAccountSchema.index({ tenantId: 1, status: 1, 'balances.current': 1 });
trustAccountSchema.index({ 'clientBalances.clientId': 1, 'clientBalances.status': 1 });
trustAccountSchema.index({ deleted: 1, retentionExpiry: 1 });
trustAccountSchema.index({ integrityHash: 1 }, { unique: true });

// ====================================================================
// PRE-SAVE HOOKS
// ====================================================================

trustAccountSchema.pre('save', function(next) {
    try {
        if (!this.tenantId) {
            throw new Error('TENANT_ISOLATION_VIOLATION: Trust account requires tenantId');
        }
        if (this.isNew && !this.accountNumber) {
            this.accountNumber = `TRUST-${uuidv4().toUpperCase()}`;
        }
        if (this.compliance.lastReconciliationDate) {
            const nd = new Date(this.compliance.lastReconciliationDate);
            nd.setDate(nd.getDate() + 7);
            this.compliance.nextReconciliationDue = nd;
        }
        if (this.compliance.nextReconciliationDue < new Date()) {
            this.compliance.overdueReconciliations += 1;
        }
        this.integrityHash = crypto.createHash('sha3-512')
            .update(`${this.accountNumber}:${this.balances.current}:${Date.now()}`)
            .digest('hex');
        if (this.isNew) {
            this.auditTrail.push({ 
                action: 'ACCOUNT_CREATED', 
                performedBy: this.openedBy, 
                performedAt: new Date(), 
                changes: { 
                    accountNumber: this.accountNumber, 
                    attorneyId: this.attorneyId 
                } 
            });
        }
        next();
    } catch (error) {
        next(error);
    }
});

// ====================================================================
// STATIC METHODS
// ====================================================================

trustAccountSchema.statics = {
    async findRequiringReconciliation(tenantId) { 
        return this.find({ 
            tenantId, 
            status: 'ACTIVE', 
            deleted: false, 
            'compliance.nextReconciliationDue': { $lte: new Date() } 
        }).populate('attorneyId', 'lpcNumber practice.name contact.email'); 
    },
    
    async findByTransactionHash(hash) { 
        return this.findOne({ 
            'transactions.transactionHash': hash, 
            deleted: false 
        }); 
    },
    
    async getDailySummary(tenantId, date = new Date()) {
        const sd = new Date(date.setHours(0,0,0,0));
        const ed = new Date(date.setHours(23,59,59,999));
        const r = await this.aggregate([
            { $match: { tenantId, deleted: false, status: 'ACTIVE' } },
            { $unwind: '$transactions' },
            { $match: { 
                'transactions.processedAt': { $gte: sd, $lte: ed }, 
                'transactions.status': 'COMPLETED' 
            } },
            { $group: { 
                _id: null, 
                totalTransactions: { $sum: 1 }, 
                totalValue: { $sum: '$transactions.amount' }, 
                averageValue: { $avg: '$transactions.amount' }, 
                deposits: { 
                    $sum: { 
                        $cond: [{ $eq: ['$transactions.transactionType', 'DEPOSIT'] }, '$transactions.amount', 0] 
                    } 
                }, 
                withdrawals: { 
                    $sum: { 
                        $cond: [{ $eq: ['$transactions.transactionType', 'WITHDRAWAL'] }, '$transactions.amount', 0] 
                    } 
                } 
            } }
        ]);
        return r[0] || { 
            totalTransactions: 0, 
            totalValue: 0, 
            averageValue: 0, 
            deposits: 0, 
            withdrawals: 0 
        };
    },
    
    async getComplianceStats(tenantId) {
        const r = await this.aggregate([
            { $match: { tenantId, deleted: false, status: 'ACTIVE' } },
            { $group: { 
                _id: null, 
                totalAccounts: { $sum: 1 }, 
                totalBalance: { $sum: '$balances.current' }, 
                overdueAccounts: { 
                    $sum: { 
                        $cond: [{ $lt: ['$compliance.nextReconciliationDue', new Date()] }, 1, 0] 
                    } 
                }, 
                accountsWithDiscrepancies: { 
                    $sum: { 
                        $cond: [{ 
                            $gt: [{ $size: { $ifNull: ['$reconciliations.discrepancies', []] } }, 0] 
                        }, 1, 0] 
                    } 
                } 
            } }
        ]);
        return r[0] || { 
            totalAccounts: 0, 
            totalBalance: 0, 
            overdueAccounts: 0, 
            accountsWithDiscrepancies: 0 
        };
    }
};

// ====================================================================
// INSTANCE METHODS
// ====================================================================

trustAccountSchema.methods = {
    async processTransaction(tx, ctx) {
        const session = await mongoose.startSession();
        session.startTransaction();
        try {
            if (tx.amount <= 0) throw new Error('TRANSACTION_AMOUNT_INVALID');
            const prev = this.transactions[this.transactions.length - 1];
            const prevHash = prev ? prev.transactionHash : 'GENESIS';
            let nb = this.balances.current;
            const amt = parseFloat(tx.amount.toFixed(2));
            
            switch (tx.transactionType) {
                case 'DEPOSIT':
                case 'INTEREST':
                case 'CORRECTION':
                    nb += amt;
                    break;
                case 'WITHDRAWAL':
                case 'TRANSFER':
                case 'REFUND':
                case 'FEE':
                    if (this.balances.available < amt) throw new Error('INSUFFICIENT_FUNDS');
                    nb -= amt;
                    break;
                default:
                    throw new Error(`INVALID_TRANSACTION_TYPE: ${tx.transactionType}`);
            }
            
            const th = crypto.createHash('sha3-512')
                .update([
                    tx.transactionId || `TX-${uuidv4()}`,
                    tx.transactionType,
                    amt.toFixed(2),
                    tx.clientId,
                    tx.matterReference,
                    prevHash,
                    Date.now().toString(),
                    crypto.randomBytes(16).toString('hex')
                ].join(':')).digest('hex');
            
            const transaction = {
                transactionId: `TX-${uuidv4()}`,
                transactionType: tx.transactionType,
                purpose: tx.purpose,
                amount: amt,
                runningBalance: parseFloat(nb.toFixed(2)),
                clientId: tx.clientId,
                clientName: tx.clientName,
                matterReference: tx.matterReference,
                description: tx.description,
                reference: tx.reference,
                status: 'COMPLETED',
                processedAt: new Date(),
                processedBy: ctx.userId,
                ipAddress: ctx.ipAddress,
                userAgent: ctx.userAgent,
                previousHash: prevHash,
                transactionHash: th,
                nonce: crypto.randomBytes(16).toString('hex')
            };
            
            const ci = this.clientBalances.findIndex(function(c) { 
                return c.clientId === tx.clientId && c.matterReference === tx.matterReference; 
            });
            
            if (ci >= 0) {
                this.clientBalances[ci].balance += ['DEPOSIT', 'INTEREST'].includes(tx.transactionType) ? amt : -amt;
                this.clientBalances[ci].lastTransaction = new Date();
                this.clientBalances[ci].lastTransactionId = transaction.transactionId;
                this.clientBalances[ci].transactionCount += 1;
                if (tx.transactionType === 'DEPOSIT') {
                    this.clientBalances[ci].pending -= amt;
                }
            } else {
                this.clientBalances.push({
                    clientId: tx.clientId,
                    clientName: tx.clientName,
                    matterReference: tx.matterReference,
                    balance: ['DEPOSIT', 'INTEREST'].includes(tx.transactionType) ? amt : -amt,
                    lastTransaction: new Date(),
                    lastTransactionId: transaction.transactionId,
                    transactionCount: 1,
                    status: 'ACTIVE',
                    openedAt: new Date(),
                    openedBy: ctx.userId
                });
            }
            
            this.balances.current = parseFloat(nb.toFixed(2));
            this.balances.available = parseFloat(nb.toFixed(2));
            this.balances.lastUpdated = new Date();
            this.transactions.push(transaction);
            
            this.integrityHash = crypto.createHash('sha3-512')
                .update(`${this.accountNumber}:${this.balances.current}:${Date.now()}`)
                .digest('hex');
            
            this.auditTrail.push({
                action: 'TRANSACTION_PROCESSED',
                performedBy: ctx.userId,
                performedAt: new Date(),
                ipAddress: ctx.ipAddress,
                userAgent: ctx.userAgent,
                changes: {
                    transactionId: transaction.transactionId,
                    transactionType: tx.transactionType,
                    amount: amt,
                    clientId: tx.clientId,
                    matterReference: tx.matterReference
                },
                transactionId: transaction.transactionId,
                previousStateHash: prevHash,
                newStateHash: th
            });
            
            await this.save({ session });
            await session.commitTransaction();
            
            return {
                success: true,
                transactionId: transaction.transactionId,
                transactionHash: th,
                amount: amt,
                runningBalance: this.balances.current,
                processedAt: transaction.processedAt,
                clientBalance: this.clientBalances.find(function(c) { 
                    return c.clientId === tx.clientId && c.matterReference === tx.matterReference; 
                })?.balance || 0
            };
        } catch (e) {
            await session.abortTransaction();
            throw e;
        } finally {
            session.endSession();
        }
    },
    
    async performReconciliation(bankBalance, stmt, ctx) {
        const rid = `RECON-${uuidv4()}`;
        try {
            const sys = this.balances.current;
            const disc = parseFloat((bankBalance - sys).toFixed(2));
            const unreconciled = this.transactions.filter(function(t) { 
                return !this.reconciliations.some(function(r) { 
                    return r.verifiedTransactions?.includes(t.transactionId); 
                }); 
            }.bind(this));
            
            const rec = {
                reconciliationId: rid,
                status: Math.abs(disc) <= 0.01 ? 'COMPLETED' : 'DISPUTED',
                startedAt: new Date(),
                completedAt: new Date(),
                performedBy: ctx.userId,
                ipAddress: ctx.ipAddress,
                systemBalance: sys,
                bankBalance,
                discrepancy: disc,
                isReconciled: Math.abs(disc) <= 0.01,
                transactionCount: unreconciled.length,
                verifiedTransactions: unreconciled.map(function(t) { return t.transactionId; }),
                statementDate: stmt.statementDate,
                statementReference: stmt.statementReference,
                statementHash: stmt.statementHash,
                verifiedAt: new Date(),
                verifiedBy: ctx.userId,
                verificationHash: crypto.createHash('sha3-512')
                    .update(`${rid}:${sys}:${bankBalance}:${Date.now()}`)
                    .digest('hex')
            };
            
            if (Math.abs(disc) > 0.01) {
                rec.discrepancies = [{
                    expectedAmount: sys,
                    actualAmount: bankBalance,
                    difference: disc,
                    reason: 'Unreconciled transactions or bank errors',
                    resolved: false
                }];
                
                this.compliance.flags.push({
                    type: 'DISCREPANCY_DETECTED',
                    severity: Math.abs(disc) > 10000 ? 'CRITICAL' : 'HIGH',
                    description: `Trust reconciliation discrepancy of R${disc.toFixed(2)}`,
                    raisedAt: new Date()
                });
            }
            
            this.reconciliations.push(rec);
            this.compliance.lastReconciliationDate = new Date();
            this.compliance.reconciliationScore = Math.max(0, 100 - (Math.abs(disc) / 100));
            this.compliance.consecutiveReconciliations = Math.abs(disc) <= 0.01 
                ? (this.compliance.consecutiveReconciliations || 0) + 1 
                : 0;
            
            const nd = new Date();
            nd.setDate(nd.getDate() + 7);
            this.compliance.nextReconciliationDue = nd;
            
            this.integrityHash = crypto.createHash('sha3-512')
                .update(`${this.accountNumber}:${this.balances.current}:${Date.now()}`)
                .digest('hex');
            
            this.auditTrail.push({
                action: 'RECONCILIATION_COMPLETED',
                performedBy: ctx.userId,
                performedAt: new Date(),
                ipAddress: ctx.ipAddress,
                userAgent: ctx.userAgent,
                changes: {
                    reconciliationId: rid,
                    systemBalance: sys,
                    bankBalance,
                    discrepancy: disc,
                    isReconciled: Math.abs(disc) <= 0.01
                },
                reconciliationId: rid
            });
            
            await this.save();
            
            return {
                success: true,
                reconciliationId: rid,
                systemBalance: sys,
                bankBalance,
                discrepancy: disc,
                isReconciled: Math.abs(disc) <= 0.01,
                transactionCount: unreconciled.length,
                verifiedAt: rec.verifiedAt
            };
        } catch (e) {
            throw new Error(`RECONCILIATION_FAILED: ${e.message}`);
        }
    },
    
    async calculateInterest() {
        const active = this.clientBalances.filter(function(c) { 
            return c.status === 'ACTIVE' && c.balance > 0; 
        });
        
        let total = 0;
        const calc = [];
        
        for (const c of active) {
            const days = Math.max(30, Math.floor((Date.now() - (c.lastTransaction || Date.now() - 30 * 24 * 60 * 60 * 1000)) / (1000 * 60 * 60 * 24)));
            const years = days / 365;
            const interest = c.balance * this.interestSettings.rate * years;
            
            if (interest >= this.interestSettings.paymentThreshold) {
                const amt = parseFloat(interest.toFixed(2));
                calc.push({
                    clientId: c.clientId,
                    clientName: c.clientName,
                    matterReference: c.matterReference,
                    balance: c.balance,
                    daysHeld: days,
                    yearsHeld: parseFloat(years.toFixed(4)),
                    interestRate: this.interestSettings.rate,
                    interestAmount: amt
                });
                total += amt;
            }
        }
        
        this.balances.interestEarned += total;
        this.interestSettings.lastCalculatedAt = new Date();
        
        this.auditTrail.push({
            action: 'INTEREST_CALCULATED',
            performedBy: 'SYSTEM',
            performedAt: new Date(),
            changes: {
                totalInterest: parseFloat(total.toFixed(2)),
                eligibleClients: calc.length,
                totalClients: active.length,
                rate: this.interestSettings.rate
            }
        });
        
        await this.save();
        
        return {
            accountNumber: this.accountNumber,
            calculationDate: new Date(),
            interestRate: this.interestSettings.rate,
            totalClients: active.length,
            eligibleClients: calc.length,
            totalInterest: parseFloat(total.toFixed(2)),
            calculations: calc
        };
    },
    
    async reverseTransaction(tid, reason, ctx) {
        const tx = this.transactions.find(function(t) { 
            return t.transactionId === tid; 
        });
        
        if (!tx) throw new Error(`TRANSACTION_NOT_FOUND: ${tid}`);
        if (tx.isReversal) throw new Error('CANNOT_REVERSE_REVERSAL');
        if (tx.reversedAt) throw new Error('TRANSACTION_ALREADY_REVERSED');
        
        const rev = await this.processTransaction({
            transactionType: tx.transactionType === 'DEPOSIT' ? 'WITHDRAWAL' : 'DEPOSIT',
            purpose: tx.purpose,
            amount: Math.abs(tx.amount),
            clientId: tx.clientId,
            clientName: tx.clientName,
            matterReference: tx.matterReference,
            description: `REVERSAL: ${tx.description}`,
            reference: `REV-${tx.reference}`,
            isReversal: true,
            originalTransactionId: tid
        }, ctx);
        
        tx.status = 'REVERSED';
        tx.reversedBy = ctx.userId;
        tx.reversedAt = new Date();
        tx.reversalReason = reason;
        tx.reversalTransactionId = rev.transactionId;
        
        await this.save();
        
        return {
            success: true,
            originalTransactionId: tid,
            reversalTransactionId: rev.transactionId,
            reversalAmount: Math.abs(tx.amount),
            reversedAt: tx.reversedAt,
            reversedBy: ctx.userId,
            reason
        };
    },
    
    async generateAuditReport(sd, ed) {
        const txs = this.transactions.filter(function(t) { 
            return t.processedAt >= sd && t.processedAt <= ed; 
        });
        
        const recs = this.reconciliations.filter(function(r) { 
            return r.startedAt >= sd && r.startedAt <= ed; 
        });
        
        let ob = 0;
        this.transactions.filter(function(t) { 
            return t.processedAt < sd; 
        }).forEach(function(t) { 
            ob += ['DEPOSIT', 'INTEREST'].includes(t.transactionType) ? t.amount : -t.amount; 
        });
        
        let chainValid = true;
        let brokenIdx = -1;
        for (let i = 1; i < this.transactions.length; i++) {
            if (this.transactions[i].previousHash !== this.transactions[i-1].transactionHash) {
                chainValid = false;
                brokenIdx = i;
                break;
            }
        }
        
        return {
            accountNumber: this.accountNumber,
            attorneyId: this.attorneyId,
            attorneyLpcNumber: this.attorneyLpcNumber,
            tenantId: this.tenantId,
            reportPeriod: {
                startDate: sd.toISOString(),
                endDate: ed.toISOString()
            },
            summary: {
                openingBalance: parseFloat(ob.toFixed(2)),
                closingBalance: this.balances.current,
                netChange: parseFloat((this.balances.current - ob).toFixed(2)),
                totalTransactions: txs.length,
                totalDeposits: txs.filter(function(t) { 
                    return ['DEPOSIT', 'INTEREST'].includes(t.transactionType); 
                }).reduce(function(s, t) { 
                    return s + t.amount; 
                }, 0),
                totalWithdrawals: txs.filter(function(t) { 
                    return ['WITHDRAWAL', 'TRANSFER', 'FEE'].includes(t.transactionType); 
                }).reduce(function(s, t) { 
                    return s + t.amount; 
                }, 0),
                uniqueClients: new Set(txs.map(function(t) { 
                    return t.clientId; 
                })).size,
                uniqueMatters: new Set(txs.map(function(t) { 
                    return t.matterReference; 
                })).size
            },
            clientBalances: this.clientBalances.filter(function(c) { 
                return c.status === 'ACTIVE'; 
            }).map(function(c) {
                return {
                    clientId: c.clientId,
                    clientName: c.clientName,
                    matterReference: c.matterReference,
                    balance: c.balance,
                    lastTransaction: c.lastTransaction,
                    transactionCount: c.transactionCount
                };
            }),
            reconciliations: recs.map(function(r) {
                return {
                    reconciliationId: r.reconciliationId,
                    date: r.completedAt,
                    status: r.status,
                    systemBalance: r.systemBalance,
                    bankBalance: r.bankBalance,
                    discrepancy: r.discrepancy,
                    isReconciled: r.isReconciled,
                    verifiedBy: r.verifiedBy
                };
            }),
            compliance: {
                reconciliationScore: this.compliance.reconciliationScore,
                overdueReconciliations: this.compliance.overdueReconciliations,
                nextReconciliationDue: this.compliance.nextReconciliationDue,
                flags: this.compliance.flags.filter(function(f) { 
                    return !f.resolvedAt; 
                })
            },
            integrity: {
                chainValid: chainValid,
                brokenIndex: brokenIdx >= 0 ? brokenIdx : undefined,
                transactionCount: this.transactions.length,
                lastTransactionHash: this.transactions[this.transactions.length - 1]?.transactionHash,
                integrityHash: this.integrityHash,
                quantumSignature: this.quantumSignature
            },
            generatedAt: new Date().toISOString(),
            generatedBy: 'WilsyOS Trust Accounting Engine v5.0.2'
        };
    },
    
    verifyTransactionIntegrity(tid) {
        const tx = this.transactions.find(function(t) { 
            return t.transactionId === tid; 
        });
        
        if (!tx) {
            return { 
                valid: false, 
                reason: 'TRANSACTION_NOT_FOUND' 
            };
        }
        
        const recalc = crypto.createHash('sha3-512')
            .update([
                tx.transactionId,
                tx.transactionType,
                tx.amount.toFixed(2),
                tx.clientId,
                tx.matterReference,
                tx.previousHash,
                tx.processedAt.getTime().toString(),
                tx.nonce
            ].join(':')).digest('hex');
        
        const idx = this.transactions.findIndex(function(t) { 
            return t.transactionId === tid; 
        });
        
        let chainValid = true;
        if (idx > 0) {
            chainValid = tx.previousHash === this.transactions[idx-1].transactionHash;
        }
        
        return {
            valid: recalc === tx.transactionHash && chainValid,
            transactionId: tid,
            transactionHash: tx.transactionHash,
            recalculatedHash: recalc,
            hashValid: recalc === tx.transactionHash,
            chainValid: chainValid,
            timestamp: new Date().toISOString()
        };
    },
    
    async closeAccount(reason, ctx) {
        if (this.balances.current !== 0) {
            throw new Error('ACCOUNT_HAS_BALANCE: Account must have zero balance before closing');
        }
        
        if (this.transactions.some(function(t) { 
            return t.status === 'PENDING'; 
        })) {
            throw new Error('PENDING_TRANSACTIONS: Resolve all pending transactions before closing');
        }
        
        this.status = 'CLOSED';
        this.statusReason = reason;
        this.statusChangedAt = new Date();
        this.statusChangedBy = ctx.userId;
        this.closedAt = new Date();
        this.closedBy = ctx.userId;
        this.closureReason = reason;
        
        this.clientBalances.forEach(function(c) {
            c.status = 'CLOSED';
            c.closedAt = new Date();
            c.closedBy = ctx.userId;
            c.closureReason = 'Account closed';
        });
        
        this.auditTrail.push({
            action: 'ACCOUNT_CLOSED',
            performedBy: ctx.userId,
            performedAt: new Date(),
            ipAddress: ctx.ipAddress,
            userAgent: ctx.userAgent,
            changes: { reason }
        });
        
        await this.save();
        
        return {
            success: true,
            accountNumber: this.accountNumber,
            closedAt: this.closedAt,
            closedBy: this.closedBy,
            reason
        };
    }
};

module.exports = mongoose.model('TrustAccount', trustAccountSchema);
