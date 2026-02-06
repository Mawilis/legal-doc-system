#!/bin/bash
/* eslint-disable no-console, max-len */
/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   █████╗ ██╗   ██╗██████╗ ██╗████████╗    ████████╗██████╗  █████╗ ██╗██╗   ║
║  ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝    ╚══██╔══╝██╔══██╗██╔══██╗██║██║   ║
║  ███████║██║   ██║██║  ██║██║   ██║          ██║   ██████╔╝███████║██║██║   ║
║  ██╔══██║██║   ██║██║  ██║██║   ██║          ██║   ██╔══██╗██╔══██╗██║██║   ║
║  ██║  ██║╚██████╔╝██████╔╝██║   ██║          ██║   ██║  ██║██║  ██║██║██║   ║
║  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝          ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝   ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  FILE: /Users/wilsonkhanyezi/legal-doc-system/server/models/AuditTrail.js   ║
║                                                                              ║
║  PURPOSE: Quantum Audit Trail with Enhanced Document Access Tracking        ║
║           ASCII: [Event]→[Encrypt]→[Hash]→[Tenant]→[Store]→[Chain]         ║
║  COMPLIANCE: Cybercrimes Act/POPIA/ECT/PAIA/FICA/Companies Act             ║
║                                                                              ║
║  CHIEF ARCHITECT: Wilson Khanyezi                                           ║
║  EMAIL: wilsy.wk@gmail.com | CELL: +27 69 046 5710                          ║
║                                                                              ║
║  FILENAME: AuditTrail.js                                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

/**
 * @file Quantum Audit Trail Model with Enhanced Document Access Tracking
 * @module models/AuditTrail
 * @description Immutable forensic ledger capturing all legal transactions with document access tracking
 * @requires mongoose, crypto
 * @version 2.1.0
 * @since Wilsy OS v3.0
 * @author Wilson Khanyezi
 */

const mongoose = require('mongoose');
const crypto = require('crypto');

const { Schema } = mongoose; // Only import what we need

// ==============================================
// SCHEMA DEFINITION: ENHANCED AUDIT TRAIL
// ==============================================

// Document Access Tracking Sub-schema
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
        min: 1
    },
    accessType: {
        type: String,
        enum: ['VIEW', 'DOWNLOAD', 'PRINT', 'COPY', 'SHARE', 'EDIT', 'DELETE', 'RESTORE'],
        required: true
    },
    accessMethod: {
        type: String,
        enum: ['WEB_PORTAL', 'MOBILE_APP', 'API', 'EXPORT', 'SYNC', 'BATCH_PROCESS'],
        default: 'WEB_PORTAL'
    },
    documentMetadata: {
        title: String,
        documentType: String,
        classification: {
            type: String,
            enum: ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED']
        },
        fileSize: Number,
        mimeType: String
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
        purpose: String
    },
    accessDurationMs: {
        type: Number,
        min: 0,
        description: 'Duration of access in milliseconds'
    }
}, { _id: false });

// Main Audit Trail Schema with Enhanced Document Tracking
const AuditTrailSchema = new Schema({
    // ========================
    // IDENTITY & INTEGRITY
    // ========================
    eventId: {
        type: String,
        unique: true,
        required: [true, 'Event ID is required'],
        immutable: true,
        index: true,
        match: [/^AUDIT-[0-9]{13}-[a-f0-9]{12}$/, 'Invalid quantum event ID format']
    },
    eventHash: {
        type: String,
        required: [true, 'Event hash is required'],
        immutable: true,
        match: [/^[a-f0-9]{64}$/, 'Invalid SHA-256 hash format'],
        index: true
    },
    parentHash: {
        type: String,
        match: [/^[a-f0-9]{64}$/, 'Invalid SHA-256 hash format']
    },
    chainIndex: {
        type: Number,
        min: 0,
        description: 'Position in the audit chain for sequential verification'
    },

    // ========================
    // TEMPORAL DATA
    // ========================
    timestamp: {
        type: Date,
        required: [true, 'Timestamp is required'],
        immutable: true,
        index: true,
        default: Date.now
    },
    ingestionTimestamp: {
        type: Date,
        required: [true, 'Ingestion timestamp is required'],
        immutable: true,
        default: Date.now
    },
    timezone: {
        type: String,
        default: 'Africa/Johannesburg',
        description: 'Timezone for accurate temporal reconstruction'
    },

    // ========================
    // ACTOR INFORMATION
    // ========================
    actor: {
        tenantId: {
            type: String,
            required: [true, 'Tenant ID is required for multi-tenant isolation'],
            index: true,
            match: [/^tenant_[a-zA-Z0-9_]{8,32}$/, 'Tenant ID must match pattern: tenant_[8-32 alphanumeric chars]']
        },
        userId: {
            type: Schema.Types.ObjectId,
            ref: 'User',
            required: [true, 'User ID is required'],
            index: true
        },
        userRole: {
            type: String,
            required: [true, 'User role is required'],
            enum: ['SYSTEM_ADMIN', 'COMPLIANCE_OFFICER', 'INFORMATION_OFFICER', 'LEGAL_COUNSEL', 'PARALEGAL', 'CLIENT', 'SYSTEM', 'EXTERNAL_AUDITOR']
        },
        impersonatedBy: {
            type: Schema.Types.ObjectId,
            ref: 'User',
            description: 'If this action was performed by admin on behalf of user'
        },
        sessionId: {
            type: String,
            description: 'Authentication session identifier'
        },
        deviceFingerprint: {
            type: String,
            description: 'Device fingerprint for forensic tracing'
        },
        // Encrypted PII fields for privacy compliance
        encryptedMetadata: {
            ipAddress: {
                type: String,
                required: [true, 'IP address is required for forensic tracing'],
                description: 'AES-256-GCM encrypted IP address'
            },
            userAgent: {
                type: String,
                description: 'AES-256-GCM encrypted user agent string'
            },
            geolocation: {
                country: String,
                region: String,
                city: String,
                latitude: Number,
                longitude: Number
            }
        }
    },

    // ========================
    // ACTION & OPERATION
    // ========================
    action: {
        category: {
            type: String,
            required: [true, 'Action category is required'],
            enum: [
                'AUTHENTICATION',
                'AUTHORIZATION',
                'DOCUMENT_ACCESS',
                'DOCUMENT_MODIFICATION',
                'DOCUMENT_CREATION',
                'DOCUMENT_DELETION',
                'COMPLIANCE_CHECK',
                'USER_MANAGEMENT',
                'SYSTEM_SECURITY',
                'DATA_EXPORT',
                'DATA_IMPORT',
                'API_CALL',
                'LEGAL_WORKFLOW',
                'PAYMENT_PROCESSING',
                'AUDIT_ACCESS',
                'CONFIGURATION_CHANGE'
            ],
            index: true
        },
        method: {
            type: String,
            required: [true, 'HTTP method is required'],
            enum: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'SYSTEM', 'BATCH', 'WEBHOOK']
        },
        resourceType: {
            type: String,
            required: [true, 'Resource type is required'],
            enum: [
                'DOCUMENT',
                'DOCUMENT_VERSION',
                'USER',
                'CLIENT',
                'CASE',
                'COMPLIANCE_RECORD',
                'PAYMENT',
                'CONFIGURATION',
                'API_ENDPOINT',
                'SYSTEM',
                'TENANT',
                'AUDIT_TRAIL',
                'PAIA_REQUEST'
            ],
            index: true
        },
        resourceId: {
            type: Schema.Types.ObjectId,
            description: 'Dynamic reference to affected resource',
            index: true
        },
        resourceIdentifier: {
            type: String,
            description: 'Alternative resource identifier (e.g., case number, email)'
        },
        endpoint: {
            type: String,
            required: [true, 'API endpoint is required'],
            description: 'Specific endpoint invoked'
        },
        description: {
            type: String,
            required: [true, 'Action description is required'],
            maxlength: 1000,
            description: 'Human-readable description of the action'
        },
        // Enhanced document access tracking
        documentAccess: DocumentAccessSchema
    },

    // ========================
    // OUTCOME & RESULTS
    // ========================
    outcome: {
        statusCode: {
            type: Number,
            required: [true, 'Status code is required'],
            min: 100,
            max: 599
        },
        success: {
            type: Boolean,
            required: [true, 'Success flag is required'],
            index: true
        },
        responseTimeMs: {
            type: Number,
            required: [true, 'Response time is required'],
            min: 0
        },
        dataVolume: {
            bytesTransferred: Number,
            recordsAffected: Number,
            description: 'Volume of data involved in the operation'
        },
        errorDetails: {
            errorCode: String,
            errorMessage: String,
            stackTrace: {
                type: String,
                select: false, // Never include in queries by default
                description: 'Full error stack trace for debugging'
            },
            remediationSteps: [String]
        },
        quotaImpact: {
            storageUsed: Number,
            apiCallsUsed: Number,
            description: 'Impact on tenant quotas'
        }
    },

    // ========================
    // LEGAL COMPLIANCE
    // ========================
    compliance: {
        legalBasis: {
            type: String,
            required: [true, 'Legal basis is required'],
            enum: [
                'CYBERCRIMES_ACT_2020',
                'POPIA_2013',
                'ECT_ACT_2002',
                'FICA_2001',
                'COMPANIES_ACT_2008',
                'PAIA_2000',
                'CPA_2008',
                'NATIONAL_ARCHIVES_ACT',
                'LPC_RULES',
                'GDPR_2016'
            ],
            index: true
        },
        specificSection: {
            type: String,
            description: 'Specific legal section (e.g., POPIA Section 14)'
        },
        jurisdiction: {
            type: String,
            required: [true, 'Jurisdiction is required'],
            default: 'ZA',
            enum: ['ZA', 'NA', 'BW', 'LS', 'SZ', 'MZ', 'ZW', 'EU', 'UK', 'GLOBAL'],
            index: true
        },
        regulatorNotificationRequired: {
            type: Boolean,
            default: false
        },
        regulatorNotificationId: String,
        retentionPeriodDays: {
            type: Number,
            required: [true, 'Retention period is required'],
            default: 1095, // 3 years
            min: 1,
            max: 36500 // 100 years max
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
        }
    },

    // ========================
    // SECURITY & INTEGRITY
    // ========================
    security: {
        encryptionVersion: {
            type: String,
            required: [true, 'Encryption version is required'],
            default: 'AES-256-GCM-v2'
        },
        signature: {
            type: String,
            description: 'Digital signature for non-repudiation'
        },
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
            detectionTimestamp: Date,
            originalHash: String,
            tamperType: String,
            forensicReport: String
        },
        blockchainAnchor: {
            txHash: String,
            blockNumber: Number,
            blockchain: {
                type: String,
                enum: ['ETHEREUM', 'BITCOIN', 'SOLANA', 'HEDERA', 'HYPERLEDGER']
            },
            anchoredAt: Date
        }
    },

    // ========================
    // METADATA & CONTEXT
    // ========================
    metadata: {
        serviceName: {
            type: String,
            required: [true, 'Service name is required'],
            default: 'WilsyOS-Core'
        },
        version: {
            type: String,
            required: [true, 'Service version is required'],
            default: '3.0.0'
        },
        correlationId: {
            type: String,
            index: true,
            description: 'Links related events across services'
        },
        requestId: {
            type: String,
            description: 'Original request identifier'
        },
        workflowId: {
            type: String,
            description: 'Workflow instance identifier'
        },
        tags: [{
            type: String,
            description: 'Searchable tags for categorization'
        }],
        notes: {
            type: String,
            maxlength: 2000,
            description: 'Additional context or notes'
        }
    }
}, {
    // Schema Options
    timestamps: {
        createdAt: 'quantumCreationDate',
        updatedAt: 'lastVerificationDate'
    },
    toJSON: {
        virtuals: true,
        transform: (doc, ret) => {
            // Remove encrypted fields from JSON output for security
            delete ret.actor?.encryptedMetadata;
            delete ret.outcome?.errorDetails?.stackTrace;
            return ret;
        }
    },
    toObject: { virtuals: true },
    id: true
});

// ==============================================
// INDEXES: OPTIMIZED FOR FORENSIC QUERIES
// ==============================================

// Primary tenant timeline for DSAR/PAIA requests
AuditTrailSchema.index({
    timestamp: 1,
    'actor.tenantId': 1,
    'action.category': 1
}, {
    name: 'tenant_timeline_idx',
    background: true,
    comment: 'Optimized for tenant timeline reconstruction'
});

// User activity monitoring per POPIA
AuditTrailSchema.index({
    'actor.userId': 1,
    timestamp: -1,
    'action.category': 1
}, {
    name: 'user_activity_idx',
    background: true,
    comment: 'Optimized for user activity audits'
});

// Document access tracking for forensic investigations
AuditTrailSchema.index({
    'action.documentAccess.documentId': 1,
    timestamp: -1,
    'actor.userId': 1
}, {
    name: 'document_access_idx',
    background: true,
    comment: 'Optimized for document access audits'
});

// Compliance reporting by jurisdiction
AuditTrailSchema.index({
    'compliance.jurisdiction': 1,
    'compliance.legalBasis': 1,
    timestamp: 1
}, {
    name: 'compliance_reporting_idx',
    background: true,
    comment: 'Optimized for regulatory reporting'
});

// Resource audit trail
AuditTrailSchema.index({
    'action.resourceType': 1,
    'action.resourceId': 1,
    timestamp: -1
}, {
    name: 'resource_audit_idx',
    background: true,
    comment: 'Optimized for resource history queries'
});

// Failed actions monitoring
AuditTrailSchema.index({
    'outcome.success': 1,
    timestamp: -1,
    'action.category': 1
}, {
    name: 'failed_actions_idx',
    background: true,
    comment: 'Optimized for security incident detection'
});

// TTL index for automatic expiration
AuditTrailSchema.index({
    timestamp: 1
}, {
    name: 'auto_expire_idx',
    background: true,
    expireAfterSeconds: 94608000, // 3 years
    partialFilterExpression: {
        'compliance.retentionPeriodDays': { $lte: 1095 }
    },
    comment: 'Auto-delete after retention period'
});

// ==============================================
// VIRTUAL PROPERTIES
// ==============================================

/**
 * Days until expiration based on retention policy
 */
AuditTrailSchema.virtual('daysUntilExpiration').get(function () {
    if (!this.timestamp) return null;
    const expirationDate = new Date(this.timestamp);
    expirationDate.setDate(expirationDate.getDate() + (this.compliance?.retentionPeriodDays || 1095));
    const diff = expirationDate - new Date();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
});

/**
 * Whether this event requires regulator notification
 */
AuditTrailSchema.virtual('requiresRegulatorNotification').get(function () {
    return this.compliance?.regulatorNotificationRequired ||
        (this.action?.category === 'SYSTEM_SECURITY' && !this.outcome?.success) ||
        (this.compliance?.legalBasis === 'POPIA_2013' &&
            this.action?.category === 'DATA_EXPORT' &&
            this.outcome?.statusCode >= 400) ||
        (this.action?.category === 'DOCUMENT_ACCESS' &&
            this.action?.documentAccess?.accessType === 'SHARE' &&
            this.action?.documentAccess?.documentMetadata?.classification === 'RESTRICTED');
});

/**
 * Check if this is a high-sensitivity audit entry
 */
AuditTrailSchema.virtual('isHighSensitivity').get(function () {
    return this.compliance?.sensitivityLevel === 'RESTRICTED' ||
        this.compliance?.sensitivityLevel === 'SECRET' ||
        this.action?.category === 'SYSTEM_SECURITY' ||
        (this.action?.category === 'DOCUMENT_ACCESS' &&
            this.action?.documentAccess?.documentMetadata?.classification === 'RESTRICTED');
});

// ==============================================
// STATIC METHODS
// ==============================================

/**
 * Log a document access event with enhanced tracking
 * @param {Object} params - Document access parameters
 * @returns {Promise<Object>} Created audit entry
 */
AuditTrailSchema.statics.logDocumentAccess = async function (params) {
    const {
        tenantId,
        userId,
        userRole,
        documentId,
        documentVersion,
        accessType,
        accessMethod = 'WEB_PORTAL',
        documentMetadata = {},
        ipAddress,
        userAgent,
        sessionId,
        success = true,
        statusCode = 200,
        responseTimeMs = 0,
        accessDurationMs = 0
    } = params;

    if (!tenantId || !validateTenantId(tenantId)) {
        throw new Error('Valid tenant ID is required');
    }

    if (!documentId) {
        throw new Error('Document ID is required');
    }

    // Generate event ID
    const timestamp = Date.now();
    const random = crypto.randomBytes(6).toString('hex');
    const eventId = `AUDIT-${timestamp}-${random}`;

    // Create document access details
    const documentAccess = {
        documentId,
        documentVersion: documentVersion || 1,
        accessType,
        accessMethod,
        documentMetadata: {
            title: documentMetadata.title || 'Unknown Document',
            documentType: documentMetadata.documentType || 'UNKNOWN',
            classification: documentMetadata.classification || 'INTERNAL',
            fileSize: documentMetadata.fileSize || 0,
            mimeType: documentMetadata.mimeType || 'application/octet-stream'
        },
        accessDurationMs
    };

    // Create the audit entry
    const auditEntry = new this({
        eventId,
        timestamp: new Date(),
        actor: {
            tenantId,
            userId,
            userRole: userRole || 'CLIENT',
            sessionId,
            encryptedMetadata: {
                ipAddress: encryptField(ipAddress || '0.0.0.0'),
                userAgent: encryptField(userAgent || 'Unknown')
            }
        },
        action: {
            category: 'DOCUMENT_ACCESS',
            method: 'GET',
            resourceType: 'DOCUMENT',
            resourceId: documentId,
            endpoint: `/api/documents/${documentId}/access`,
            description: `Document ${accessType.toLowerCase()} access`,
            documentAccess
        },
        outcome: {
            statusCode,
            success,
            responseTimeMs,
            dataVolume: {
                bytesTransferred: documentMetadata.fileSize || 0
            }
        },
        compliance: {
            legalBasis: 'POPIA_2013',
            jurisdiction: 'ZA',
            retentionPeriodDays: 1825, // 5 years for document access logs
            sensitivityLevel: documentMetadata.classification === 'RESTRICTED' ? 'RESTRICTED' : 'CONFIDENTIAL'
        },
        metadata: {
            serviceName: 'WilsyOS-DocumentService',
            version: '3.0.0',
            tags: ['document-access', accessType.toLowerCase(), 'popia']
        }
    });

    // Generate event hash
    auditEntry.eventHash = generateEventHash(auditEntry);

    try {
        const savedEntry = await auditEntry.save();

        // Update document access statistics
        await updateDocumentAccessStats(documentId, accessType, success);

        return savedEntry;
    } catch (error) {
        console.error('Failed to log document access:', error.message);
        throw error;
    }
};

/**
 * Get document access history for forensic investigations
 * @param {string} documentId - Document identifier
 * @param {Object} options - Query options
 * @returns {Promise<Array>} Document access history
 */
AuditTrailSchema.statics.getDocumentAccessHistory = async function (documentId, options = {}) {
    const {
        tenantId,
        startDate,
        endDate,
        userId,
        accessType,
        limit = 100,
        skip = 0
    } = options;

    const query = {
        'action.resourceType': 'DOCUMENT',
        'action.resourceId': new mongoose.Types.ObjectId(documentId),
        'action.category': 'DOCUMENT_ACCESS'
    };

    // Apply filters
    if (tenantId && validateTenantId(tenantId)) {
        query['actor.tenantId'] = tenantId;
    }

    if (userId) {
        query['actor.userId'] = new mongoose.Types.ObjectId(userId);
    }

    if (accessType) {
        query['action.documentAccess.accessType'] = accessType;
    }

    // Date range filter
    if (startDate || endDate) {
        query.timestamp = {};
        if (startDate) query.timestamp.$gte = new Date(startDate);
        if (endDate) query.timestamp.$lte = new Date(endDate);
    }

    const accessHistory = await this.find(query)
        .sort({ timestamp: -1 })
        .skip(skip)
        .limit(limit)
        .populate('actor.userId', 'name email')
        .populate('action.resourceId', 'title caseNumber')
        .lean();

    return accessHistory.map(entry => ({
        eventId: entry.eventId,
        timestamp: entry.timestamp,
        actor: {
            userId: entry.actor.userId,
            userRole: entry.actor.userRole,
            tenantId: entry.actor.tenantId
        },
        action: {
            accessType: entry.action.documentAccess?.accessType,
            description: entry.action.description,
            documentMetadata: entry.action.documentAccess?.documentMetadata
        },
        outcome: {
            success: entry.outcome.success,
            responseTimeMs: entry.outcome.responseTimeMs
        },
        metadata: {
            serviceName: entry.metadata.serviceName
        }
    }));
};

/**
 * Generate compliance report for regulators
 * @param {Object} params - Report parameters
 * @returns {Promise<Object>} Compliance report
 */
AuditTrailSchema.statics.generateComplianceReport = async function (params = {}) {
    const {
        jurisdiction = 'ZA',
        startDate,
        endDate,
        tenantId,
        legalBasis
    } = params;

    const query = {
        'compliance.jurisdiction': jurisdiction
    };

    // Apply filters
    if (tenantId && validateTenantId(tenantId)) {
        query['actor.tenantId'] = tenantId;
    }

    if (legalBasis) {
        query['compliance.legalBasis'] = legalBasis;
    }

    // Date range
    if (startDate || endDate) {
        query.timestamp = {};
        if (startDate) query.timestamp.$gte = new Date(startDate);
        if (endDate) query.timestamp.$lte = new Date(endDate);
    } else {
        // Default: last 30 days
        query.timestamp = {
            $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
        };
    }

    const events = await this.find(query)
        .sort({ timestamp: -1 })
        .limit(5000)
        .lean();

    // Calculate statistics
    const totalEvents = events.length;
    const successfulEvents = events.filter(e => e.outcome?.success).length;
    const failedEvents = totalEvents - successfulEvents;
    const complianceRate = totalEvents > 0 ? (successfulEvents / totalEvents) * 100 : 100;

    // Document access statistics
    const documentAccessEvents = events.filter(e => e.action?.category === 'DOCUMENT_ACCESS');
    const documentAccessByType = documentAccessEvents.reduce((acc, event) => {
        const type = event.action?.documentAccess?.accessType || 'UNKNOWN';
        acc[type] = (acc[type] || 0) + 1;
        return acc;
    }, {});

    // Identify compliance issues
    const potentialIssues = events.filter(event =>
        event.compliance?.regulatorNotificationRequired ||
        (event.action?.category === 'DOCUMENT_ACCESS' &&
            event.action?.documentAccess?.documentMetadata?.classification === 'RESTRICTED' &&
            !event.outcome?.success) ||
        (event.action?.category === 'SYSTEM_SECURITY' && !event.outcome?.success)
    );

    // Generate report
    return {
        reportMetadata: {
            generatedAt: new Date(),
            jurisdiction,
            period: {
                startDate: query.timestamp?.$gte || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
                endDate: query.timestamp?.$lte || new Date()
            },
            tenantId,
            totalEventsAnalyzed: totalEvents,
            dataSource: 'Wilsy OS Quantum Audit Trail'
        },
        executiveSummary: {
            complianceRate: `${complianceRate.toFixed(2)}%`,
            successfulOperations: successfulEvents,
            failedOperations: failedEvents,
            averageResponseTime: events.reduce((sum, e) => sum + (e.outcome?.responseTimeMs || 0), 0) / totalEvents || 0
        },
        detailedBreakdown: {
            byLegalBasis: events.reduce((acc, event) => {
                const basis = event.compliance?.legalBasis || 'UNKNOWN';
                acc[basis] = (acc[basis] || 0) + 1;
                return acc;
            }, {}),
            byActionCategory: events.reduce((acc, event) => {
                const category = event.action?.category || 'UNKNOWN';
                acc[category] = (acc[category] || 0) + 1;
                return acc;
            }, {}),
            documentAccessBreakdown: documentAccessByType
        },
        securityIncidents: {
            count: potentialIssues.length,
            incidents: potentialIssues.slice(0, 20).map(issue => ({
                eventId: issue.eventId,
                timestamp: issue.timestamp,
                action: issue.action?.description,
                issueType: issue.compliance?.regulatorNotificationRequired ?
                    'Regulator Notification Required' :
                    'Security/Compliance Violation',
                severity: issue.action?.category === 'SYSTEM_SECURITY' ? 'HIGH' : 'MEDIUM'
            }))
        },
        recommendations: generateComplianceRecommendations(events)
    };
};

// ==============================================
// INSTANCE METHODS
// ==============================================

/**
 * Encrypt a field using AES-256-GCM
 * @param {string} plaintext - Text to encrypt
 * @returns {string} Encrypted string
 */
AuditTrailSchema.methods.encryptField = function (plaintext) {
    return encryptField(plaintext);
};

/**
 * Decrypt a field using AES-256-GCM
 * @param {string} encryptedText - Text to decrypt
 * @returns {string} Decrypted string
 */
AuditTrailSchema.methods.decryptField = function (encryptedText) {
    return decryptField(encryptedText);
};

/**
 * Verify the integrity of this audit entry
 * @returns {boolean} Whether the entry is intact
 */
AuditTrailSchema.methods.verifyIntegrity = function () {
    const currentHash = generateEventHash(this);
    return currentHash === this.eventHash;
};

// ==============================================
// MIDDLEWARE
// ==============================================

/**
 * Pre-save hook: Validate and prepare audit entry
 */
AuditTrailSchema.pre('save', async function (next) {
    try {
        // Generate event ID if not present
        if (!this.eventId) {
            const timestamp = Date.now();
            const random = crypto.randomBytes(6).toString('hex');
            this.eventId = `AUDIT-${timestamp}-${random}`;
        }

        // Set ingestion timestamp
        if (!this.ingestionTimestamp) {
            this.ingestionTimestamp = new Date();
        }

        // Encrypt sensitive fields
        if (this.actor?.encryptedMetadata?.ipAddress &&
            !this.actor.encryptedMetadata.ipAddress.includes(':')) {
            this.actor.encryptedMetadata.ipAddress = encryptField(
                this.actor.encryptedMetadata.ipAddress
            );
        }

        if (this.actor?.encryptedMetadata?.userAgent &&
            !this.actor.encryptedMetadata.userAgent.includes(':')) {
            this.actor.encryptedMetadata.userAgent = encryptField(
                this.actor.encryptedMetadata.userAgent
            );
        }

        // Generate event hash
        if (!this.eventHash) {
            this.eventHash = generateEventHash(this);
        }

        // Ensure minimum retention period
        if (this.compliance?.legalBasis) {
            const minRetention = getMinimumRetentionByLaw(this.compliance.legalBasis);
            if (this.compliance.retentionPeriodDays < minRetention) {
                this.compliance.retentionPeriodDays = minRetention;
            }
        }

        next();
    } catch (error) {
        console.error('AuditTrail pre-save validation failed:', error);
        next(error);
    }
});

// ==============================================
// HELPER FUNCTIONS
// ==============================================

/**
 * Validate tenant ID format
 * @param {string} tenantId - Tenant identifier
 * @returns {boolean} Whether tenant ID is valid
 */
function validateTenantId(tenantId) {
    return /^tenant_[a-zA-Z0-9_]{8,32}$/.test(tenantId);
}

/**
 * Encrypt a field using AES-256-GCM
 * @param {string} plaintext - Text to encrypt
 * @returns {string} Encrypted string
 */
function encryptField(plaintext) {
    if (!plaintext) return plaintext;

    const encryptionKey = process.env.AUDIT_ENCRYPTION_KEY ||
        'dev-fallback-key-32-bytes-long-for-testing';

    const algorithm = 'aes-256-gcm';
    const key = crypto.scryptSync(encryptionKey, 'wilsy-audit-salt', 32);
    const iv = crypto.randomBytes(16);

    const cipher = crypto.createCipheriv(algorithm, key, iv);
    let encrypted = cipher.update(plaintext, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    const authTag = cipher.getAuthTag();

    return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`;
}

/**
 * Decrypt a field using AES-256-GCM
 * @param {string} encryptedText - Text to decrypt
 * @returns {string} Decrypted string
 */
function decryptField(encryptedText) {
    if (!encryptedText || !encryptedText.includes(':')) {
        return encryptedText;
    }

    const [ivHex, authTagHex, encryptedHex] = encryptedText.split(':');

    const encryptionKey = process.env.AUDIT_ENCRYPTION_KEY ||
        'dev-fallback-key-32-bytes-long-for-testing';
    const algorithm = 'aes-256-gcm';
    const key = crypto.scryptSync(encryptionKey, 'wilsy-audit-salt', 32);
    const iv = Buffer.from(ivHex, 'hex');
    const authTag = Buffer.from(authTagHex, 'hex');

    const decipher = crypto.createDecipheriv(algorithm, key, iv);
    decipher.setAuthTag(authTag);

    let decrypted = decipher.update(encryptedHex, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
}

/**
 * Generate SHA-256 hash for an audit entry
 * @param {Object} auditEntry - Audit entry object
 * @returns {string} SHA-256 hash
 */
function generateEventHash(auditEntry) {
    const hashData = {
        eventId: auditEntry.eventId,
        timestamp: auditEntry.timestamp?.toISOString(),
        actor: {
            tenantId: auditEntry.actor?.tenantId,
            userId: auditEntry.actor?.userId?.toString()
        },
        action: {
            category: auditEntry.action?.category,
            resourceId: auditEntry.action?.resourceId?.toString()
        },
        outcome: {
            success: auditEntry.outcome?.success,
            statusCode: auditEntry.outcome?.statusCode
        }
    };

    const dataString = JSON.stringify(hashData);
    return crypto.createHash('sha256').update(dataString).digest('hex');
}

/**
 * Get minimum retention period by law
 * @param {string} legalBasis - Legal basis identifier
 * @returns {number} Minimum retention in days
 */
function getMinimumRetentionByLaw(legalBasis) {
    const retentionMap = {
        'CYBERCRIMES_ACT_2020': 3650,  // 10 years
        'POPIA_2013': 1825,            // 5 years
        'FICA_2001': 3650,             // 10 years
        'COMPANIES_ACT_2008': 2555,    // 7 years
        'NATIONAL_ARCHIVES_ACT': 3650, // 10 years
        'PAIA_2000': 1095,             // 3 years
        'ECT_ACT_2002': 1825,          // 5 years
        'CPA_2008': 1095,              // 3 years
        'GDPR_2016': 1825,             // 5 years
        'LPC_RULES': 2555              // 7 years
    };

    return retentionMap[legalBasis] || 1095; // Default 3 years
}

/**
 * Update document access statistics
 * @param {ObjectId} documentId - Document identifier
 * @param {string} accessType - Type of access
 * @param {boolean} success - Whether access was successful
 */
async function updateDocumentAccessStats(documentId, accessType, success) {
    try {
        const Document = mongoose.model('Document');
        await Document.findByIdAndUpdate(documentId, {
            $inc: {
                'metadata.accessStats.totalAccesses': 1,
                [`metadata.accessStats.${accessType.toLowerCase()}Count`]: 1,
                'metadata.accessStats.successfulAccesses': success ? 1 : 0,
                'metadata.accessStats.failedAccesses': success ? 0 : 1
            },
            $set: {
                'metadata.accessStats.lastAccessed': new Date()
            }
        });
    } catch (error) {
        console.error('Failed to update document access stats:', error.message);
    }
}

/**
 * Generate compliance recommendations based on audit data
 * @param {Array} events - Audit events
 * @returns {Array} Recommendations
 */
function generateComplianceRecommendations(events) {
    const recommendations = [];

    // Check for excessive failed document accesses
    const failedDocumentAccesses = events.filter(e =>
        e.action?.category === 'DOCUMENT_ACCESS' && !e.outcome?.success
    );

    if (failedDocumentAccesses.length > 10) {
        recommendations.push({
            priority: 'HIGH',
            title: 'Excessive Failed Document Access Attempts',
            description: `${failedDocumentAccesses.length} failed document access attempts detected. Review access control policies.`,
            action: 'Review and strengthen document access controls'
        });
    }

    // Check for document sharing without proper classification
    const documentShares = events.filter(e =>
        e.action?.category === 'DOCUMENT_ACCESS' &&
        e.action?.documentAccess?.accessType === 'SHARE' &&
        e.action?.documentAccess?.documentMetadata?.classification === 'RESTRICTED'
    );

    if (documentShares.length > 5) {
        recommendations.push({
            priority: 'MEDIUM',
            title: 'High Volume of Restricted Document Shares',
            description: `${documentShares.length} shares of restricted documents detected. Ensure proper authorization.`,
            action: 'Implement stricter sharing controls for restricted documents'
        });
    }

    // Check for system security incidents
    const securityIncidents = events.filter(e =>
        e.action?.category === 'SYSTEM_SECURITY' && !e.outcome?.success
    );

    if (securityIncidents.length > 0) {
        recommendations.push({
            priority: 'CRITICAL',
            title: 'System Security Incidents Detected',
            description: `${securityIncidents.length} system security incidents detected. Immediate review required.`,
            action: 'Conduct security audit and implement remediation measures'
        });
    }

    return recommendations;
}

// ==============================================
// MERMAID DIAGRAM: Audit Trail Flow
// ==============================================

/*
```mermaid
flowchart TD
    A[Event Occurs<br>e.g., Document Access] --> B{Validate & Capture}
    
    B -->|Valid| C[Apply Tenant Context]
    B -->|Invalid| D[Reject Event]
    
    C --> E[Encrypt PII Data]
    E --> F[Generate Event Hash]
    F --> G[Apply Retention Policy]
    
    G --> H[Store in Quantum Ledger]
    H --> I[Update Statistics]
    I --> J[Trigger Notifications]
    
    J --> K{High Sensitivity?}
    K -->|Yes| L[Queue for Blockchain Anchoring]
    K -->|No| M[Standard Storage]
    
    L --> N[Anchor to Blockchain]
    M --> O[Complete]
    N --> O
    
    subgraph "Compliance Features"
        P[POPIA Consent Tracking]
        Q[DSAR Hook Integration]
        R[PAIA Access Logging]
        S[Retention Enforcement]
        T[Multi-tenant Isolation]
    end
    
    E -.-> P
    G -.-> S
    C -.-> T
    H -.-> Q
    H -.-> R
    
    style A fill:#e1f5fe
    style D fill:#ffebee
    style O fill:#e8f5e8
    style L fill:#fff3e0*/