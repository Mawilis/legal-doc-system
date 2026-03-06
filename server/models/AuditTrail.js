/* eslint-disable */
// ============================================================================
// WILSY OS 2050 - QUANTUM AUDIT TRAIL MODEL
// 10TH GENERATION FORENSIC ENGINE | IMMUTABLE LEDGER
// VERSION: 42.0.0 | GENERATION: 10
// COMPLIANCE: Cybercrimes Act/POPIA/ECT/PAIA/FICA/Companies Act
// ============================================================================

import crypto from 'crypto';
import mongoose from 'mongoose';

const { Schema, model } = mongoose;

// ============================================================================
// 🔒 ENCRYPTION CONFIGURATION
// ============================================================================
const ENCRYPTION_ALGORITHM = 'aes-256-gcm';
const ENCRYPTION_KEY = process.env.AUDIT_ENCRYPTION_KEY || crypto.randomBytes(32).toString('hex');
const ENCRYPTION_SALT = 'wilsy-quantum-audit-v1';

// ============================================================================
// 📋 DOCUMENT ACCESS SUB-SCHEMA
// ============================================================================
const DocumentAccessSchema = new Schema({
    documentId: {
        type: Schema.Types.ObjectId,
        ref: 'Document',
        required: true,
        index: true
    },
    documentVersion: {
        type: Number,
        required: true,
        min: 1,
        default: 1
    },
    accessType: {
        type: String,
        enum: ['VIEW', 'DOWNLOAD', 'PRINT', 'COPY', 'SHARE', 'EDIT', 'DELETE', 'RESTORE', 'EXPORT'],
        required: true
    },
    accessMethod: {
        type: String,
        enum: ['WEB_PORTAL', 'MOBILE_APP', 'API', 'EXPORT', 'SYNC', 'BATCH_PROCESS', 'SYSTEM'],
        default: 'WEB_PORTAL'
    },
    documentMetadata: {
        title: String,
        documentType: String,
        classification: {
            type: String,
            enum: ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED', 'SECRET'],
            default: 'INTERNAL'
        },
        fileSize: Number,
        mimeType: String,
        caseNumber: String,
        matterId: Schema.Types.ObjectId
    },
    redactionApplied: {
        type: Boolean,
        default: false
    },
    redactionReason: String,
    watermarkPresent: {
        type: Boolean,
        default: false
    },
    watermarkDetails: {
        userId: String,
        timestamp: Date,
        purpose: String,
        watermarkId: String
    },
    accessDurationMs: {
        type: Number,
        min: 0,
        default: 0
    },
    ipAddress: {
        type: String,
        required: true
    },
    userAgent: String
}, { _id: false });

// ============================================================================
// 🔥 MAIN AUDIT TRAIL SCHEMA
// ============================================================================
const AuditTrailSchema = new Schema({
    // ========================================================================
    // 🔗 IDENTITY & INTEGRITY
    // ========================================================================
    eventId: {
        type: String,
        unique: true,
        required: true,
        immutable: true,
        index: true,
        default: () => `AUDIT-${Date.now()}-${crypto.randomBytes(6).toString('hex')}`
    },
    eventHash: {
        type: String,
        required: true,
        immutable: true,
        index: true,
        match: [/^[a-f0-9]{64}$/, 'Invalid SHA-256 hash format']
    },
    previousHash: {
        type: String,
        match: [/^[a-f0-9]{64}$/, 'Invalid SHA-256 hash format']
    },
    chainIndex: {
        type: Number,
        min: 0,
        index: true
    },

    // ========================================================================
    // ⏰ TEMPORAL DATA
    // ========================================================================
    timestamp: {
        type: Date,
        required: true,
        immutable: true,
        index: true,
        default: Date.now
    },
    ingestionTimestamp: {
        type: Date,
        required: true,
        default: Date.now
    },
    timezone: {
        type: String,
        default: 'Africa/Johannesburg'
    },
    year: {
        type: Number,
        index: true
    },
    month: {
        type: Number,
        index: true
    },
    quarter: {
        type: Number,
        index: true
    },

    // ========================================================================
    // 👤 ACTOR INFORMATION
    // ========================================================================
    actor: {
        tenantId: {
            type: String,
            required: true,
            index: true,
            match: [/^tenant_[a-zA-Z0-9_]{8,32}$/, 'Invalid tenant ID format']
        },
        userId: {
            type: Schema.Types.ObjectId,
            ref: 'User',
            required: true,
            index: true
        },
        userRole: {
            type: String,
            required: true,
            enum: [
                'SYSTEM_ADMIN', 'COMPLIANCE_OFFICER', 'INFORMATION_OFFICER',
                'LEGAL_COUNSEL', 'PARALEGAL', 'CLIENT', 'SYSTEM',
                'EXTERNAL_AUDITOR', 'REGULATOR', 'JUDGE', 'EXPERT_WITNESS'
            ]
        },
        impersonatedBy: {
            type: Schema.Types.ObjectId,
            ref: 'User'
        },
        sessionId: String,
        deviceFingerprint: String,
        ipAddressEncrypted: {
            type: String,
            required: true
        },
        userAgentEncrypted: String,
        geolocation: {
            country: String,
            region: String,
            city: String,
            latitude: Number,
            longitude: Number,
            accuracy: Number
        }
    },

    // ========================================================================
    // 🎯 ACTION & OPERATION
    // ========================================================================
    action: {
        category: {
            type: String,
            required: true,
            enum: [
                'AUTHENTICATION', 'AUTHORIZATION', 'DOCUMENT_ACCESS',
                'DOCUMENT_MODIFICATION', 'DOCUMENT_CREATION', 'DOCUMENT_DELETION',
                'COMPLIANCE_CHECK', 'USER_MANAGEMENT', 'SYSTEM_SECURITY',
                'DATA_EXPORT', 'DATA_IMPORT', 'API_CALL', 'LEGAL_WORKFLOW',
                'PAYMENT_PROCESSING', 'AUDIT_ACCESS', 'CONFIGURATION_CHANGE',
                'BLOCKCHAIN_ANCHOR', 'ENCRYPTION_OPERATION', 'CONSENT_MANAGEMENT',
                'DSAR_REQUEST', 'PAIA_REQUEST', 'FICA_VERIFICATION'
            ],
            index: true
        },
        method: {
            type: String,
            enum: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'SYSTEM', 'BATCH', 'WEBHOOK', 'GRAPHQL']
        },
        resourceType: {
            type: String,
            required: true,
            enum: [
                'DOCUMENT', 'DOCUMENT_VERSION', 'USER', 'CLIENT', 'CASE',
                'COMPLIANCE_RECORD', 'PAYMENT', 'CONFIGURATION', 'API_ENDPOINT',
                'SYSTEM', 'TENANT', 'AUDIT_TRAIL', 'PAIA_REQUEST', 'DSAR_REQUEST',
                'CONSENT', 'BLOCKCHAIN_RECORD', 'ENCRYPTION_KEY'
            ],
            index: true
        },
        resourceId: {
            type: Schema.Types.ObjectId,
            refPath: 'action.resourceType',
            index: true
        },
        resourceIdentifier: String,
        endpoint: String,
        description: {
            type: String,
            required: true,
            maxlength: 2000
        },
        documentAccess: DocumentAccessSchema
    },

    // ========================================================================
    // 📊 OUTCOME & RESULTS
    // ========================================================================
    outcome: {
        statusCode: {
            type: Number,
            required: true,
            min: 100,
            max: 599
        },
        success: {
            type: Boolean,
            required: true,
            index: true
        },
        responseTimeMs: {
            type: Number,
            required: true,
            min: 0
        },
        dataVolume: {
            bytesTransferred: Number,
            recordsAffected: Number,
            apiCallsConsumed: Number
        },
        errorDetails: {
            code: String,
            message: String,
            stackTrace: {
                type: String,
                select: false
            },
            remediationSteps: [String]
        },
        quotaImpact: {
            storageUsed: Number,
            apiCallsUsed: Number,
            documentQuotaUsed: Number
        }
    },

    // ========================================================================
    // ⚖️ LEGAL COMPLIANCE
    // ========================================================================
    compliance: {
        legalBasis: {
            type: String,
            required: true,
            enum: [
                'CYBERCRIMES_ACT_2020', 'POPIA_2013', 'ECT_ACT_2002',
                'FICA_2001', 'COMPANIES_ACT_2008', 'PAIA_2000',
                'CPA_2008', 'NATIONAL_ARCHIVES_ACT', 'LPC_RULES',
                'GDPR_2016', 'CUSTOMARY_LAW', 'COMMON_LAW'
            ],
            index: true
        },
        specificSection: String,
        jurisdiction: {
            type: String,
            required: true,
            enum: ['ZA', 'NA', 'BW', 'LS', 'SZ', 'MZ', 'ZW', 'EU', 'UK', 'GLOBAL'],
            default: 'ZA',
            index: true
        },
        regulatorNotificationRequired: {
            type: Boolean,
            default: false
        },
        regulatorNotificationId: String,
        regulatorNotifiedAt: Date,
        retentionPeriodDays: {
            type: Number,
            required: true,
            min: 1,
            max: 36500,
            default: 2555
        },
        retentionUntil: {
            type: Date,
            index: true
        },
        disposalMethod: {
            type: String,
            enum: ['ARCHIVE', 'ANONYMIZE', 'DELETE', 'PERMANENT'],
            default: 'DELETE'
        },
        sensitivityLevel: {
            type: String,
            enum: ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED', 'SECRET'],
            default: 'INTERNAL'
        },
        popiaConsentId: {
            type: Schema.Types.ObjectId,
            ref: 'Consent'
        },
        ficaVerificationId: String
    },

    // ========================================================================
    // 🔐 SECURITY & INTEGRITY
    // ========================================================================
    security: {
        encryptionVersion: {
            type: String,
            default: 'AES-256-GCM-v2'
        },
        signature: String,
        signatureAlgorithm: {
            type: String,
            enum: ['RSA-SHA256', 'ECDSA-SHA256', 'EdDSA-Ed25519'],
            default: 'RSA-SHA256'
        },
        tamperEvidence: {
            detected: {
                type: Boolean,
                default: false
            },
            detectedAt: Date,
            originalHash: String,
            tamperType: String,
            forensicReport: String
        },
        blockchainAnchor: {
            txHash: String,
            blockNumber: Number,
            blockchain: {
                type: String,
                enum: ['ETHEREUM', 'HYPERLEDGER', 'POLYGON', 'SOLANA', 'HEDERA']
            },
            anchoredAt: Date,
            anchorStatus: {
                type: String,
                enum: ['PENDING', 'CONFIRMED', 'FAILED']
            }
        },
        quantumSignature: String,
        hsmKeyId: String
    },

    // ========================================================================
    // 🏷️ METADATA & CONTEXT
    // ========================================================================
    metadata: {
        serviceName: {
            type: String,
            required: true,
            default: 'WilsyOS-Quantum-Audit'
        },
        serviceVersion: {
            type: String,
            required: true,
            default: '42.0.0'
        },
        correlationId: {
            type: String,
            index: true
        },
        requestId: String,
        workflowId: String,
        workflowStep: String,
        tags: [{
            type: String,
            index: true
        }],
        notes: String,
        environment: {
            type: String,
            enum: ['development', 'staging', 'production', 'disaster-recovery'],
            default: process.env.NODE_ENV || 'development'
        },
        dataCenter: {
            type: String,
            default: 'jhb-01'
        },
        region: {
            type: String,
            default: 'ZA'
        }
    }
}, {
    timestamps: {
        createdAt: 'createdAt',
        updatedAt: 'verifiedAt'
    },
    toJSON: {
        virtuals: true,
        transform: (doc, ret) => {
            delete ret.actor?.ipAddressEncrypted;
            delete ret.actor?.userAgentEncrypted;
            delete ret.outcome?.errorDetails?.stackTrace;
            delete ret.__v;
            return ret;
        }
    },
    toObject: { virtuals: true },
    collection: 'quantum_audit_trail'
});

// ============================================================================
// 🔍 COMPREHENSIVE INDEXES
// ============================================================================

AuditTrailSchema.index({ 'actor.tenantId': 1, timestamp: -1 }, { name: 'tenant_timeline_idx' });
AuditTrailSchema.index({ 'actor.userId': 1, timestamp: -1 }, { name: 'user_activity_idx' });
AuditTrailSchema.index({ 'action.documentAccess.documentId': 1, timestamp: -1 }, { name: 'document_access_idx' });
AuditTrailSchema.index({ 'compliance.jurisdiction': 1, 'compliance.legalBasis': 1, timestamp: -1 }, { name: 'compliance_reporting_idx' });
AuditTrailSchema.index({ 'action.resourceType': 1, 'action.resourceId': 1, timestamp: -1 }, { name: 'resource_audit_idx' });
AuditTrailSchema.index({ 'outcome.success': 1, timestamp: -1 }, { name: 'security_monitoring_idx' });
AuditTrailSchema.index({ 'compliance.retentionUntil': 1 }, { name: 'retention_cleanup_idx', expireAfterSeconds: 0 });
AuditTrailSchema.index({ chainIndex: 1, 'actor.tenantId': 1 }, { name: 'chain_integrity_idx', unique: true, sparse: true });
AuditTrailSchema.index({ 'metadata.correlationId': 1 }, { name: 'correlation_idx', sparse: true });

// ============================================================================
// 🧮 VIRTUAL PROPERTIES
// ============================================================================

AuditTrailSchema.virtual('daysUntilExpiration').get(function() {
    if (!this.compliance?.retentionUntil) return null;
    const diff = this.compliance.retentionUntil - new Date();
    return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
});

AuditTrailSchema.virtual('isExpired').get(function() {
    return this.compliance?.retentionUntil && this.compliance.retentionUntil < new Date();
});

AuditTrailSchema.virtual('requiresNotification').get(function() {
    return this.compliance?.regulatorNotificationRequired ||
        (this.action?.category === 'SYSTEM_SECURITY' && !this.outcome?.success);
});

// ============================================================================
// 🔧 STATIC METHODS
// ============================================================================

AuditTrailSchema.statics.logDocumentAccess = async function(params) {
    const {
        tenantId, userId, userRole, documentId, documentVersion,
        accessType, accessMethod, documentMetadata = {},
        ipAddress, userAgent, sessionId, success = true,
        statusCode = 200, responseTimeMs = 0, accessDurationMs = 0
    } = params;

    const iv = crypto.randomBytes(16);
    const key = crypto.scryptSync(ENCRYPTION_KEY, ENCRYPTION_SALT, 32);
    const cipher = crypto.createCipheriv(ENCRYPTION_ALGORITHM, key, iv);
    let encrypted = cipher.update(ipAddress || '0.0.0.0', 'utf8', 'hex');
    encrypted += cipher.final('hex');
    const authTag = cipher.getAuthTag();
    const ipAddressEncrypted = `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`;

    const retentionDays = documentMetadata.classification === 'SECRET' ? 3650 :
                         documentMetadata.classification === 'RESTRICTED' ? 2555 :
                         documentMetadata.classification === 'CONFIDENTIAL' ? 1825 : 1095;

    const auditEntry = new this({
        actor: {
            tenantId,
            userId,
            userRole,
            sessionId,
            ipAddressEncrypted,
            userAgentEncrypted: userAgent ? ipAddressEncrypted : undefined
        },
        action: {
            category: 'DOCUMENT_ACCESS',
            method: 'GET',
            resourceType: 'DOCUMENT',
            resourceId: documentId,
            endpoint: `/api/documents/${documentId}/access`,
            description: `Document ${accessType.toLowerCase()} by ${userRole}`,
            documentAccess: {
                documentId,
                documentVersion: documentVersion || 1,
                accessType,
                accessMethod: accessMethod || 'WEB_PORTAL',
                documentMetadata,
                accessDurationMs,
                ipAddress,
                userAgent
            }
        },
        outcome: {
            statusCode,
            success,
            responseTimeMs,
            dataVolume: { bytesTransferred: documentMetadata.fileSize || 0 }
        },
        compliance: {
            legalBasis: 'POPIA_2013',
            jurisdiction: 'ZA',
            retentionPeriodDays: retentionDays,
            retentionUntil: new Date(Date.now() + retentionDays * 24 * 60 * 60 * 1000),
            sensitivityLevel: documentMetadata.classification || 'CONFIDENTIAL'
        },
        metadata: { tags: ['document-access', accessType.toLowerCase(), 'popia'] },
        year: new Date().getFullYear(),
        month: new Date().getMonth() + 1,
        quarter: Math.floor(new Date().getMonth() / 3) + 1
    });

    const hashData = {
        eventId: auditEntry.eventId,
        timestamp: auditEntry.timestamp,
        actor: { tenantId, userId: userId?.toString(), userRole },
        action: { category: 'DOCUMENT_ACCESS', resourceId: documentId?.toString() },
        outcome: { success, statusCode },
        compliance: { legalBasis: 'POPIA_2013', jurisdiction: 'ZA' }
    };
    auditEntry.eventHash = crypto.createHash('sha256').update(JSON.stringify(hashData)).digest('hex');

    return auditEntry.save();
};

AuditTrailSchema.statics.getDocumentAccessHistory = async function(documentId, options = {}) {
    const { tenantId, startDate, endDate, userId, accessType, limit = 100, skip = 0 } = options;
    const query = { 'action.documentAccess.documentId': new mongoose.Types.ObjectId(documentId) };
    
    if (tenantId) query['actor.tenantId'] = tenantId;
    if (userId) query['actor.userId'] = new mongoose.Types.ObjectId(userId);
    if (accessType) query['action.documentAccess.accessType'] = accessType;
    if (startDate || endDate) {
        query.timestamp = {};
        if (startDate) query.timestamp.$gte = new Date(startDate);
        if (endDate) query.timestamp.$lte = new Date(endDate);
    }

    return this.find(query)
        .sort({ timestamp: -1 })
        .skip(skip)
        .limit(limit)
        .populate('actor.userId', 'name email')
        .populate('action.resourceId', 'title caseNumber')
        .lean();
};

// ============================================================================
// 🔧 INSTANCE METHODS
// ============================================================================

AuditTrailSchema.methods.verifyIntegrity = function() {
    const hashData = {
        eventId: this.eventId,
        timestamp: this.timestamp,
        actor: { tenantId: this.actor?.tenantId, userId: this.actor?.userId?.toString(), userRole: this.actor?.userRole },
        action: { category: this.action?.category, resourceId: this.action?.resourceId?.toString() },
        outcome: { success: this.outcome?.success, statusCode: this.outcome?.statusCode },
        compliance: { legalBasis: this.compliance?.legalBasis, jurisdiction: this.compliance?.jurisdiction }
    };
    const currentHash = crypto.createHash('sha256').update(JSON.stringify(hashData)).digest('hex');
    return currentHash === this.eventHash;
};

// ============================================================================
// 🔒 MIDDLEWARE
// ============================================================================

AuditTrailSchema.pre('save', function(next) {
    if (!this.year) {
        this.year = this.timestamp?.getFullYear() || new Date().getFullYear();
        this.month = (this.timestamp?.getMonth() || new Date().getMonth()) + 1;
        this.quarter = Math.floor(((this.timestamp?.getMonth() || new Date().getMonth())) / 3) + 1;
    }
    if (!this.compliance?.retentionUntil && this.compliance?.retentionPeriodDays) {
        this.compliance.retentionUntil = new Date(Date.now() + this.compliance.retentionPeriodDays * 24 * 60 * 60 * 1000);
    }
    next();
});

// ============================================================================
// 🚀 CREATE AND EXPORT MODEL
// ============================================================================

const AuditTrail = model('AuditTrail', AuditTrailSchema);

export default AuditTrail;

// ============================================================================
// WILSY OS 2050 - QUANTUM AUDIT TRAIL
// "Law knows no borders. Wilsy OS has no limits."
// 10 Generations of Wealth | R 1,000,000,000,000,000 Target
// Wilson Khanyezi - Supreme Architect
// ============================================================================
