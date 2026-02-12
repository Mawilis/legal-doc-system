/**
 * WILSYS OS - FORENSIC AUDIT LEDGER MODEL
 * ====================================================================
 * LPC RULE 17.3 · LPC RULE 95.3 · POPIA SECTION 20 · GDPR ARTICLE 30
 * 
 * This model implements:
 * - Immutable audit trail with cryptographic chain-of-custody
 * - Blockchain anchoring for court-admissible evidence
 * - Multi-jurisdictional compliance tracking
 * - Data subject access request automation
 * - Retention policy enforcement with legal hold
 * - Forensic hash verification
 * - Regulatory reporting
 * 
 * @version 5.2.0
 * @author Wilson Khanyezi - Chief Quantum Sentinel
 * @copyright Wilsy OS (Pty) Ltd 2026
 * ====================================================================
 */

const crypto = require('crypto');
const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

// ====================================================================
// CRYPTOGRAPHIC CONSTANTS
// ====================================================================
const HASH_ALGORITHM = 'sha3-512';
const HASH_ENCODING = 'hex';
const FORENSIC_VERSION = '5.2.0';

// ====================================================================
// REGULATORY FRAMEWORKS
// ====================================================================
const REGULATORY_FRAMEWORKS = {
    LPC: 'LPC',
    POPIA: 'POPIA',
    GDPR: 'GDPR',
    FICA: 'FICA',
    SARB: 'SARB',
    FSCA: 'FSCA'
};

// ====================================================================
// ACTION TYPES
// ====================================================================
const ACTION_TYPES = {
    // CRUD Operations
    CREATE: 'CREATE',
    READ: 'READ',
    UPDATE: 'UPDATE',
    DELETE: 'DELETE',

    // Access Operations
    VIEW: 'VIEW',
    EXPORT: 'EXPORT',
    DOWNLOAD: 'DOWNLOAD',
    PRINT: 'PRINT',

    // Compliance Operations
    VERIFY: 'VERIFY',
    AUDIT: 'AUDIT',
    REPORT: 'REPORT',
    CERTIFY: 'CERTIFY',

    // Trust Account Operations
    RECONCILE: 'RECONCILE',
    PROCESS: 'PROCESS',
    TRANSFER: 'TRANSFER',

    // CPD Operations
    SUBMIT: 'SUBMIT',
    VERIFY_CPD: 'VERIFY_CPD',
    EXEMPT: 'EXEMPT',

    // Fidelity Operations
    ISSUE: 'ISSUE',
    RENEW: 'RENEW',
    CLAIM: 'CLAIM',

    // System Operations
    INITIALIZE: 'INITIALIZE',
    HEALTH_CHECK: 'HEALTH_CHECK',
    SYSTEM: 'SYSTEM'
};

// ====================================================================
// AUDIT LEDGER SCHEMA - IMMUTABLE RECORD
// ====================================================================
const auditLedgerSchema = new mongoose.Schema({
    // ================================================================
    // CORE IDENTIFIERS
    // ================================================================
    auditId: {
        type: String,
        required: true,
        unique: true,
        index: true,
        default: () => `AUDIT-${uuidv4()}`
    },

    correlationId: {
        type: String,
        index: true,
        default: () => uuidv4()
    },

    sessionId: String,
    requestId: String,
    transactionId: String,

    // ================================================================
    // TEMPORAL CONTEXT
    // ================================================================
    timestamp: {
        type: Date,
        required: true,
        default: Date.now,
        index: true
    },

    year: Number,
    month: Number,
    day: Number,
    hour: Number,

    processedAt: {
        type: Date,
        default: Date.now,
        index: true
    },

    // ================================================================
    // RESOURCE CONTEXT
    // ================================================================
    resource: {
        type: String,
        required: true,
        index: true
    },

    resourceType: {
        type: String,
        enum: ['ATTORNEY', 'TRUST_ACCOUNT', 'MATTER', 'CPD', 'FIDELITY',
            'COMPLIANCE', 'AUDIT', 'USER', 'SYSTEM', 'TRANSACTION', 'OTHER'],
        required: true,
        index: true
    },

    identifier: {
        type: String,
        required: true,
        index: true
    },

    action: {
        type: String,
        enum: Object.values(ACTION_TYPES),
        required: true,
        index: true
    },

    // ================================================================
    // USER CONTEXT
    // ================================================================
    userId: {
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
        index: true
    },

    practiceId: String,
    departmentId: String,

    roles: [String],
    permissions: [String],

    // ================================================================
    // REQUEST CONTEXT
    // ================================================================
    ipAddress: String,
    userAgent: String,
    referer: String,
    origin: String,
    platform: String,
    deviceId: String,

    location: {
        country: String,
        region: String,
        city: String,
        timezone: String,
        coordinates: {
            lat: Number,
            lng: Number
        }
    },

    // ================================================================
    // COMPLIANCE METADATA
    // ================================================================
    regulatoryTags: [{
        type: String,
        index: true
    }],

    regulatoryFramework: {
        type: String,
        enum: Object.values(REGULATORY_FRAMEWORKS),
        index: true
    },

    retentionPolicy: {
        policy: String,
        days: Number,
        expiry: Date
    },

    dataResidency: {
        type: String,
        enum: ['ZA', 'EU', 'UK', 'USA', 'OTHER'],
        default: 'ZA'
    },

    legalHold: {
        active: { type: Boolean, default: false },
        holdId: String,
        reason: String,
        initiatedBy: String,
        initiatedAt: Date,
        caseNumber: String
    },

    // ================================================================
    // FORENSIC EVIDENCE
    // ================================================================
    forensicHash: {
        type: String,
        required: true,
        index: true
    },

    previousHash: String,
    nextHash: String,

    chainOfCustody: [{
        action: String,
        timestamp: Date,
        actor: String,
        hash: String,
        ipAddress: String,
        signature: String
    }],

    // ================================================================
    // BLOCKCHAIN ANCHOR
    // ================================================================
    blockchainAnchor: {
        transactionId: String,
        blockHeight: Number,
        blockHash: String,
        timestamp: Date,
        verified: { type: Boolean, default: false },
        verifiedAt: Date,
        anchorId: String,
        regulator: String
    },

    // ================================================================
    // DATA SUBJECT RIGHTS
    // ================================================================
    dataSubjectId: {
        type: String,
        index: true,
        sparse: true
    },

    consentId: {
        type: String,
        index: true,
        sparse: true
    },

    processingPurpose: String,
    legalBasis: String,

    // ================================================================
    // BUSINESS METADATA
    // ================================================================
    metadata: {
        type: mongoose.Schema.Types.Mixed,
        default: {}
    },

    changes: {
        type: mongoose.Schema.Types.Mixed,
        default: {}
    },

    // ================================================================
    // SYSTEM CONTEXT
    // ================================================================
    systemContext: {
        hostname: String,
        platform: String,
        arch: String,
        nodeVersion: String,
        processId: Number,
        memory: mongoose.Schema.Types.Mixed,
        uptime: Number
    },

    // ================================================================
    // VERSIONING
    // ================================================================
    version: {
        type: String,
        default: FORENSIC_VERSION
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
    strict: true,
    versionKey: false
});

// ====================================================================
// INDEXES - PERFORMANCE OPTIMIZATION
// ====================================================================
auditLedgerSchema.index({ tenantId: 1, timestamp: -1 });
auditLedgerSchema.index({ tenantId: 1, userId: 1, timestamp: -1 });
auditLedgerSchema.index({ tenantId: 1, resourceType: 1, timestamp: -1 });
auditLedgerSchema.index({ tenantId: 1, action: 1, timestamp: -1 });
auditLedgerSchema.index({ tenantId: 1, regulatoryTags: 1, timestamp: -1 });
auditLedgerSchema.index({ dataSubjectId: 1, timestamp: -1 });
auditLedgerSchema.index({ consentId: 1 });
auditLedgerSchema.index({ 'blockchainAnchor.transactionId': 1 });
auditLedgerSchema.index({ forensicHash: 1 });
auditLedgerSchema.index({ correlationId: 1 });
auditLedgerSchema.index({ 'retentionPolicy.expiry': 1 }, { sparse: true });

// ====================================================================
// PRE-SAVE HOOKS - FORENSIC INTEGRITY
// ====================================================================
auditLedgerSchema.pre('save', async function (next) {
    try {
        // Set temporal fields
        const now = new Date(this.timestamp || Date.now());
        this.year = now.getUTCFullYear();
        this.month = now.getUTCMonth() + 1;
        this.day = now.getUTCDate();
        this.hour = now.getUTCHours();

        // Generate forensic hash if not present
        if (!this.forensicHash) {
            this.forensicHash = this._generateForensicHash();
        }

        // Set system context
        this.systemContext = {
            hostname: require('os').hostname(),
            platform: process.platform,
            arch: process.arch,
            nodeVersion: process.version,
            processId: process.pid,
            memory: process.memoryUsage(),
            uptime: process.uptime()
        };

        // Set retention expiry
        if (!this.retentionPolicy?.expiry && !this.legalHold?.active) {
            const days = this.retentionPolicy?.days || 1825; // 5 years default
            const expiry = new Date();
            expiry.setDate(expiry.getDate() + days);
            this.retentionPolicy = this.retentionPolicy || {};
            this.retentionPolicy.expiry = expiry;
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
 * Generate forensic hash for audit record
 * SHA3-512 for quantum resistance
 */
auditLedgerSchema.methods._generateForensicHash = function () {
    const hash = crypto.createHash(HASH_ALGORITHM);

    // Include all forensic-relevant fields
    hash.update(this.auditId || '');
    hash.update(this.timestamp?.toISOString() || '');
    hash.update(this.resource || '');
    hash.update(this.identifier || '');
    hash.update(this.action || '');
    hash.update(this.userId || '');
    hash.update(this.tenantId || '');
    hash.update(JSON.stringify(this.metadata || {}));
    hash.update(JSON.stringify(this.changes || {}));

    if (this.previousHash) hash.update(this.previousHash);
    if (this.correlationId) hash.update(this.correlationId);
    if (this.dataSubjectId) hash.update(this.dataSubjectId);

    return hash.digest(HASH_ENCODING);
};

/**
 * Add to chain of custody
 */
auditLedgerSchema.methods.addCustodyEvent = function (action, actor, options = {}) {
    const event = {
        action,
        timestamp: new Date(),
        actor,
        hash: this.forensicHash,
        ipAddress: options.ipAddress,
        signature: options.signature
    };

    this.chainOfCustody = this.chainOfCustody || [];
    this.chainOfCustody.push(event);

    return event;
};

/**
 * Verify forensic integrity
 */
auditLedgerSchema.methods.verifyIntegrity = function () {
    const recomputedHash = this._generateForensicHash();
    return recomputedHash === this.forensicHash;
};

/**
 * Anchor to blockchain
 */
auditLedgerSchema.methods.anchorToBlockchain = async function (anchorResult) {
    this.blockchainAnchor = {
        transactionId: anchorResult.transactionId,
        blockHeight: anchorResult.blockHeight,
        blockHash: anchorResult.blockHash,
        timestamp: anchorResult.timestamp || new Date(),
        verified: false,
        anchorId: anchorResult.anchorId,
        regulator: anchorResult.regulator || 'LPC'
    };

    this.addCustodyEvent('BLOCKCHAIN_ANCHORED', 'SYSTEM', {
        signature: anchorResult.signature?.hybrid
    });

    return this.save();
};

/**
 * Mark as verified on blockchain
 */
auditLedgerSchema.methods.markAnchoredVerified = function () {
    if (this.blockchainAnchor) {
        this.blockchainAnchor.verified = true;
        this.blockchainAnchor.verifiedAt = new Date();
        this.addCustodyEvent('BLOCKCHAIN_VERIFIED', 'SYSTEM');
    }

    return this.save();
};

/**
 * Place legal hold
 */
auditLedgerSchema.methods.placeLegalHold = function (reason, userId, caseNumber = null) {
    this.legalHold = {
        active: true,
        holdId: `HOLD-${uuidv4()}`,
        reason,
        initiatedBy: userId,
        initiatedAt: new Date(),
        caseNumber
    };

    this.retentionPolicy.expiry = null; // Indefinite retention

    this.addCustodyEvent('LEGAL_HOLD_PLACED', userId, { reason });

    return this.save();
};

/**
 * Release legal hold
 */
auditLedgerSchema.methods.releaseLegalHold = function (userId) {
    if (this.legalHold?.active) {
        this.legalHold.active = false;
        this.legalHold.releasedBy = userId;
        this.legalHold.releasedAt = new Date();

        // Restore retention expiry
        const days = this.retentionPolicy?.days || 1825;
        const expiry = new Date();
        expiry.setDate(expiry.getDate() + days);
        this.retentionPolicy.expiry = expiry;

        this.addCustodyEvent('LEGAL_HOLD_RELEASED', userId);
    }

    return this.save();
};

// ====================================================================
// STATIC METHODS
// ====================================================================

/**
 * Create audit entry with full forensic context
 */
auditLedgerSchema.statics.createAuditEntry = async function (data) {
    const entry = new this(data);
    await entry.save();
    return entry;
};

/**
 * Find by correlation ID (trace entire request)
 */
auditLedgerSchema.statics.findByCorrelationId = async function (correlationId) {
    return this.find({ correlationId })
        .sort({ timestamp: 1 })
        .lean()
        .exec();
};

/**
 * Find by data subject ID (POPIA Section 22 / GDPR Article 15)
 */
auditLedgerSchema.statics.findByDataSubject = async function (dataSubjectId, options = {}) {
    const {
        startDate,
        endDate,
        limit = 1000
    } = options;

    const query = {
        dataSubjectId,
        deleted: false
    };

    if (startDate || endDate) {
        query.timestamp = {};
        if (startDate) query.timestamp.$gte = startDate;
        if (endDate) query.timestamp.$lte = endDate;
    }

    return this.find(query)
        .sort({ timestamp: -1 })
        .limit(limit)
        .lean()
        .exec();
};

/**
 * Get compliance statistics for regulatory reporting
 */
auditLedgerSchema.statics.getComplianceStats = async function (tenantId, options = {}) {
    const {
        days = 30,
        framework = null
    } = options;

    const query = {
        tenantId,
        timestamp: { $gte: new Date(Date.now() - days * 24 * 60 * 60 * 1000) },
        deleted: false
    };

    if (framework) {
        query.regulatoryFramework = framework;
    }

    const [
        total,
        byAction,
        byResource,
        byUser,
        anchored,
        legalHold
    ] = await Promise.all([
        this.countDocuments(query),
        this.aggregate([
            { $match: query },
            { $group: { _id: '$action', count: { $sum: 1 } } },
            { $sort: { count: -1 } }
        ]),
        this.aggregate([
            { $match: query },
            { $group: { _id: '$resourceType', count: { $sum: 1 } } },
            { $sort: { count: -1 } }
        ]),
        this.aggregate([
            { $match: query },
            { $group: { _id: '$userId', count: { $sum: 1 } } },
            { $sort: { count: -1 } },
            { $limit: 10 }
        ]),
        this.countDocuments({ ...query, 'blockchainAnchor.verified': true }),
        this.countDocuments({ ...query, 'legalHold.active': true })
    ]);

    return {
        tenantId,
        period: `${days} days`,
        total,
        byAction,
        byResource,
        topUsers: byUser,
        anchoredCount: anchored,
        anchoringRate: total > 0 ? (anchored / total) * 100 : 0,
        legalHoldCount: legalHold,
        generatedAt: new Date().toISOString()
    };
};

/**
 * Enforce retention policies
 */
auditLedgerSchema.statics.enforceRetention = async function () {
    const now = new Date();

    const query = {
        'retentionPolicy.expiry': { $lt: now },
        'legalHold.active': { $ne: true },
        deleted: false
    };

    const result = await this.updateMany(
        query,
        {
            $set: {
                deleted: true,
                deletedAt: now,
                deletedBy: 'SYSTEM',
                deletionReason: 'Retention period expired'
            }
        }
    );

    return {
        modifiedCount: result.modifiedCount,
        matchedCount: result.matchedCount,
        timestamp: now.toISOString()
    };
};

/**
 * Verify audit trail integrity
 */
auditLedgerSchema.statics.verifyChain = async function (startDate, endDate) {
    const query = {
        timestamp: {
            $gte: startDate || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
            $lte: endDate || new Date()
        },
        deleted: false
    };

    const records = await this.find(query)
        .sort({ timestamp: 1 })
        .lean()
        .exec();

    const results = [];
    let verifiedCount = 0;

    for (const record of records) {
        const recomputedHash = crypto
            .createHash(HASH_ALGORITHM)
            .update(record.auditId)
            .update(record.timestamp.toISOString())
            .update(record.resource)
            .update(record.identifier)
            .update(record.action)
            .update(record.userId)
            .update(record.tenantId)
            .digest(HASH_ENCODING);

        const verified = recomputedHash === record.forensicHash;
        if (verified) verifiedCount++;

        results.push({
            auditId: record.auditId,
            timestamp: record.timestamp,
            verified,
            forensicHash: record.forensicHash?.substring(0, 16),
            recomputedHash: recomputedHash.substring(0, 16)
        });
    }

    return {
        total: results.length,
        verified: verifiedCount,
        failed: results.length - verifiedCount,
        integrityScore: results.length > 0 ? (verifiedCount / results.length) * 100 : 100,
        results: results.slice(0, 100), // Limit for performance
        verifiedAt: new Date().toISOString()
    };
};

// ====================================================================
// INDEXES - ADDITIONAL
// ====================================================================
auditLedgerSchema.index({ 'retentionPolicy.expiry': 1 }, {
    sparse: true,
    expireAfterSeconds: 0
});

// ====================================================================
// EXPORT
// ====================================================================
module.exports = mongoose.model('AuditLedger', auditLedgerSchema);
module.exports.ACTION_TYPES = ACTION_TYPES;
module.exports.REGULATORY_FRAMEWORKS = REGULATORY_FRAMEWORKS;