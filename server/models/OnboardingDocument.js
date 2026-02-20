/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ ONBOARDING DOCUMENT MODEL - INVESTOR-GRADE ● FORENSIC ● PRODUCTION          ║
  ║ FICA Compliant | POPIA Compliant | Chain of Custody | Forensic Tracking    ║
  ║ Version: 4.0.1 - Complete - Static Methods Using .static()                  ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/

'use strict';

const mongoose = require('mongoose');
const crypto = require('crypto');
const { DateTime } = require('luxon');

// =================================================================================================================
// SCHEMA DEFINITION - Complete with all fields
// =================================================================================================================
const onboardingDocumentSchema = new mongoose.Schema({
    // Core Identifiers
    documentId: {
        type: String,
        required: [true, 'Document ID is required'],
        unique: true,
        index: true,
        validate: {
            validator: function(v) {
                return /^DOC_[A-Z]{3}_\d{14}_[A-F0-9]{8}$/.test(v);
            },
            message: props => `${props.value} is not a valid document ID format`
        }
    },
    sessionId: {
        type: String,
        required: [true, 'Session ID is required'],
        index: true,
        validate: {
            validator: function(v) {
                return /^ONB_(IND|BUS|TRU|NPO|PAR)_\d{14}_[A-F0-9]{8}_[a-zA-Z0-9]{4}$/.test(v);
            },
            message: props => `${props.value} is not a valid session ID format`
        }
    },
    tenantId: {
        type: String,
        required: [true, 'Tenant ID is required'],
        index: true
    },
    
    // Document Metadata
    documentType: {
        type: String,
        required: [true, 'Document type is required'],
        enum: {
            values: [
                'ID_COPY', 
                'PROOF_OF_ADDRESS', 
                'PROOF_OF_INCOME', 
                'COMPANY_REGISTRATION', 
                'TAX_CLEARANCE',
                'DIRECTOR_ID_COPIES',
                'FINANCIAL_STATEMENTS',
                'BANK_STATEMENTS',
                'LEGAL_AGREEMENT',
                'POWER_OF_ATTORNEY',
                'TRUST_DEED',
                'CONSTITUTION',
                'NPO_REGISTRATION',
                'PARTNERSHIP_AGREEMENT',
                'OTHER'
            ],
            message: '{VALUE} is not a supported document type'
        },
        index: true
    },
    documentSubType: String,
    fileName: {
        type: String,
        required: [true, 'File name is required'],
        validate: {
            validator: function(v) {
                return v.length > 0 && v.length <= 255;
            },
            message: 'File name must be between 1 and 255 characters'
        }
    },
    fileSize: {
        type: Number,
        required: [true, 'File size is required'],
        min: [1, 'File size must be at least 1 byte'],
        max: [50 * 1024 * 1024, 'File size cannot exceed 50MB']
    },
    mimeType: {
        type: String,
        required: [true, 'MIME type is required'],
        enum: {
            values: [
                'application/pdf',
                'image/jpeg',
                'image/png',
                'image/tiff',
                'image/bmp',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'text/plain',
                'application/rtf'
            ],
            message: '{VALUE} is not a supported file type'
        }
    },
    
    // File Content & Security
    fileData: {
        type: Buffer,
        required: [true, 'File data is required'],
        validate: {
            validator: function(v) {
                return v && v.length > 0;
            },
            message: 'File data cannot be empty'
        }
    },
    fileHash: {
        type: String,
        required: [true, 'File hash is required'],
        index: true,
        validate: {
            validator: function(v) {
                return /^[a-f0-9]{64}$/.test(v);
            },
            message: props => `${props.value} is not a valid SHA-256 hash`
        }
    },
    fileHashAlgorithm: {
        type: String,
        default: 'sha256'
    },
    
    // File Metadata
    fileMetadata: {
        width: Number,
        height: Number,
        pages: Number,
        author: String,
        creationDate: Date,
        modificationDate: Date,
        dpi: Number,
        colorSpace: String,
        compression: String
    },
    
    // Encryption Metadata
    encryptionMetadata: {
        algorithm: {
            type: String,
            enum: ['AES-256-GCM', 'AES-256-CBC'],
            default: 'AES-256-GCM'
        },
        keyId: {
            type: String,
            required: true
        },
        keyVersion: String,
        iv: {
            type: String,
            required: true
        },
        authTag: String,
        encryptedAt: {
            type: Date,
            default: Date.now
        },
        encryptedBy: String,
        encryptionContext: 'Mixed'
    },
    
    // Document Processing Status
    processingStatus: {
        virusScan: {
            status: {
                type: String,
                enum: ['PENDING', 'IN_PROGRESS', 'CLEAN', 'INFECTED', 'ERROR', 'TIMEOUT'],
                default: 'PENDING'
            },
            scannedAt: Date,
            scannerVersion: String,
            scannerName: String,
            threats: [String],
            result: 'Mixed',
            attempts: { type: Number, default: 0 },
            errorMessage: String,
            completedAt: Date
        },
        ocr: {
            status: {
                type: String,
                enum: ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'NOT_APPLICABLE'],
                default: 'PENDING'
            },
            processedAt: Date,
            text: String,
            confidence: Number,
            language: String,
            result: 'Mixed',
            pages: Number,
            wordCount: Number,
            attempts: { type: Number, default: 0 }
        },
        verification: {
            status: {
                type: String,
                enum: ['PENDING', 'IN_PROGRESS', 'VERIFIED', 'REJECTED', 'MANUAL_REVIEW', 'FAILED'],
                default: 'PENDING'
            },
            verifiedAt: Date,
            verifiedBy: String,
            verificationMethod: String,
            confidence: Number,
            flags: [String],
            result: 'Mixed',
            notes: String,
            attempts: { type: Number, default: 0 }
        },
        fraudDetection: {
            status: {
                type: String,
                enum: ['PENDING', 'IN_PROGRESS', 'CLEAN', 'SUSPICIOUS', 'FRAUDULENT', 'ERROR'],
                default: 'PENDING'
            },
            analyzedAt: Date,
            riskScore: Number,
            riskLevel: String,
            flags: [String],
            result: 'Mixed',
            attempts: { type: Number, default: 0 }
        },
        classification: {
            status: {
                type: String,
                enum: ['PENDING', 'IN_PROGRESS', 'CLASSIFIED', 'FAILED'],
                default: 'PENDING'
            },
            classifiedAt: Date,
            category: String,
            subcategory: String,
            confidence: Number,
            result: 'Mixed'
        }
    },
    
    // Chain of Custody
    chainOfCustody: [{
        action: {
            type: String,
            required: true,
            enum: [
                'UPLOADED', 'VIEWED', 'DOWNLOADED', 'VERIFIED', 'REJECTED', 
                'ARCHIVED', 'DELETED', 'RESTORED', 'MODIFIED', 'EXPORTED',
                'PRINTED', 'EMAILED', 'SHARED', 'PROCESSED', 'SCANNED'
            ]
        },
        performedBy: {
            type: String,
            required: true
        },
        ipAddress: String,
        userAgent: String,
        sessionId: String,
        timestamp: {
            type: Date,
            required: true,
            default: Date.now
        },
        reason: String,
        correlationId: String,
        location: String,
        deviceId: String,
        hash: {
            type: String,
            required: true,
            default: function() {
                return crypto
                    .createHash('sha256')
                    .update(`${this.action}|${this.performedBy}|${this.timestamp.getTime()}|${this.reason || ''}|${this.correlationId || ''}`)
                    .digest('hex');
            }
        },
        metadata: 'Mixed'
    }],
    
    // Version Control
    version: {
        number: { type: Number, default: 1 },
        previousVersions: [{
            version: Number,
            documentId: String,
            updatedAt: Date,
            updatedBy: String,
            changes: 'Mixed',
            hash: String
        }],
        isLatest: { type: Boolean, default: true }
    },
    
    // Expiry & Retention
    expiresAt: {
        type: Date,
        required: true,
        default: function() {
            return new Date(Date.now() + 7 * 365 * 24 * 60 * 60 * 1000);
        },
        index: { expireAfterSeconds: 0 }
    },
    retentionPeriod: {
        type: Number,
        min: 365,
        max: 3650,
        default: 2555
    },
    retentionPolicy: String,
    retentionExempt: { type: Boolean, default: false },
    retentionExemptReason: String,
    retentionExemptExpiry: Date,
    
    // Metadata & Tracking
    metadata: {
        createdAt: {
            type: Date,
            required: true,
            default: Date.now
        },
        createdBy: {
            type: String,
            required: true
        },
        createdByIp: String,
        createdByUserAgent: String,
        createdByDevice: String,
        createdByLocation: String,
        
        updatedAt: {
            type: Date,
            required: true,
            default: Date.now
        },
        updatedBy: String,
        updatedByIp: String,
        updatedByUserAgent: String,
        
        version: {
            type: Number,
            default: 1
        },
        
        environment: {
            type: String,
            enum: ['development', 'staging', 'production', 'test'],
            default: process.env.NODE_ENV || 'development'
        },
        
        correlationId: {
            type: String,
            default: () => `corr_${Date.now()}_${crypto.randomBytes(8).toString('hex')}`
        },
        
        sourceSystem: String,
        sourceReference: String,
        
        tags: [String],
        notes: String,
        
        customFields: 'Mixed'
    },
    
    // Legal & Compliance Flags
    compliance: {
        popiaCompliant: { type: Boolean, default: false },
        popiaVerifiedAt: Date,
        popiaVerifiedBy: String,
        
        ficaCompliant: { type: Boolean, default: false },
        ficaVerifiedAt: Date,
        ficaVerifiedBy: String,
        
        gdprCompliant: { type: Boolean, default: false },
        gdprVerifiedAt: Date,
        
        legalHold: {
            active: { type: Boolean, default: false },
            reason: String,
            initiatedBy: String,
            initiatedAt: Date,
            expiresAt: Date,
            caseNumber: String,
            courtOrder: String
        },
        
        retentionExemption: {
            granted: { type: Boolean, default: false },
            reason: String,
            expiresAt: Date,
            grantedBy: String,
            grantedAt: Date
        },
        
        classification: {
            level: {
                type: String,
                enum: ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED', 'TOP_SECRET']
            },
            category: String,
            approvedBy: String,
            approvedAt: Date
        }
    },
    
    // Document Relationships
    relatedDocuments: [{
        documentId: String,
        relationship: {
            type: String,
            enum: ['ATTACHMENT', 'APPENDIX', 'SUPPORTING', 'SUPERSEDED', 'DUPLICATE']
        },
        metadata: 'Mixed'
    }],
    
    // Deletion Tracking
    deletedAt: Date,
    deletedBy: String,
    deletionReason: String,
    deletionAuthorization: String,
    isDeleted: {
        type: Boolean,
        default: false,
        index: true
    },
    
    // Audit Flags
    auditFlags: {
        suspicious: { type: Boolean, default: false },
        flaggedForReview: { type: Boolean, default: false },
        reviewedAt: Date,
        reviewedBy: String,
        reviewNotes: String,
        disputeRaised: { type: Boolean, default: false },
        disputeReference: String,
        disputeResolved: { type: Boolean, default: false }
    },
    
    // System Fields
    systemFields: 'Mixed'
}, {
    timestamps: true,
    collection: 'onboardingdocuments',
    strict: true,
    minimize: false,
    toJSON: {
        transform: function(doc, ret) {
            delete ret.__v;
            delete ret.fileData;
            delete ret.encryptionMetadata;
            return ret;
        },
        virtuals: true
    },
    toObject: {
        transform: function(doc, ret) {
            delete ret.__v;
            delete ret.fileData;
            return ret;
        },
        virtuals: true
    }
});

// =================================================================================================================
// INDEXES
// =================================================================================================================
onboardingDocumentSchema.index({ tenantId: 1, sessionId: 1, documentType: 1 });
onboardingDocumentSchema.index({ tenantId: 1, sessionId: 1, uploadedAt: -1 });
onboardingDocumentSchema.index({ tenantId: 1, documentType: 1, 'processingStatus.verification.status': 1 });
onboardingDocumentSchema.index({ tenantId: 1, fileHash: 1 });
onboardingDocumentSchema.index({ tenantId: 1, 'processingStatus.virusScan.status': 1 });
onboardingDocumentSchema.index({ tenantId: 1, 'processingStatus.fraudDetection.riskLevel': 1 });
onboardingDocumentSchema.index({ tenantId: 1, 'compliance.legalHold.active': 1 });
onboardingDocumentSchema.index({ tenantId: 1, isDeleted: 1, expiresAt: 1 });
onboardingDocumentSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });
onboardingDocumentSchema.index({ 
    fileName: 'text',
    documentId: 'text',
    'metadata.createdBy': 'text',
    'metadata.tags': 'text'
});

// =================================================================================================================
// VIRTUAL PROPERTIES
// =================================================================================================================
onboardingDocumentSchema.virtual('isExpired').get(function() {
    return this.expiresAt && this.expiresAt < new Date();
});

onboardingDocumentSchema.virtual('isProcessed').get(function() {
    return this.processingStatus.virusScan.status === 'CLEAN' &&
           this.processingStatus.verification.status === 'VERIFIED';
});

onboardingDocumentSchema.virtual('needsReview').get(function() {
    return this.processingStatus.verification.status === 'MANUAL_REVIEW' ||
           this.processingStatus.fraudDetection.riskLevel === 'HIGH' ||
           this.processingStatus.fraudDetection.riskLevel === 'CRITICAL' ||
           this.auditFlags.suspicious === true ||
           this.auditFlags.flaggedForReview === true;
});

onboardingDocumentSchema.virtual('fileSizeFormatted').get(function() {
    const bytes = this.fileSize;
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
});

// =================================================================================================================
// STATIC METHODS - Using .static() to ensure proper attachment
// =================================================================================================================

// Find documents by session
onboardingDocumentSchema.static('findBySession', function(sessionId, tenantId, options = {}) {
    const query = this.find({ sessionId, tenantId, isDeleted: false });
    
    if (options.documentType) {
        if (Array.isArray(options.documentType)) {
            query.where('documentType').in(options.documentType);
        } else {
            query.where('documentType').equals(options.documentType);
        }
    }
    
    if (options.verificationStatus) {
        query.where('processingStatus.verification.status').equals(options.verificationStatus);
    }
    
    if (options.virusScanStatus) {
        query.where('processingStatus.virusScan.status').equals(options.virusScanStatus);
    }
    
    if (options.riskLevel) {
        query.where('processingStatus.fraudDetection.riskLevel').equals(options.riskLevel);
    }
    
    if (options.fromDate) {
        query.where('uploadedAt').gte(new Date(options.fromDate));
    }
    
    if (options.toDate) {
        query.where('uploadedAt').lte(new Date(options.toDate));
    }
    
    if (options.sort) {
        query.sort(options.sort);
    } else {
        query.sort({ uploadedAt: -1 });
    }
    
    if (options.limit) query.limit(parseInt(options.limit));
    if (options.skip) query.skip(parseInt(options.skip));
    
    if (options.select) {
        query.select(options.select);
    }
    
    return query;
});

// Get document statistics
onboardingDocumentSchema.static('getStatistics', async function(tenantId, dateRange = {}) {
    const match = { tenantId, isDeleted: false };
    
    if (dateRange.start || dateRange.end) {
        match.uploadedAt = {};
        if (dateRange.start) match.uploadedAt.$gte = new Date(dateRange.start);
        if (dateRange.end) match.uploadedAt.$lte = new Date(dateRange.end);
    }
    
    const results = await this.aggregate([
        { $match: match },
        {
            $facet: {
                documentTypeBreakdown: [
                    { 
                        $group: { 
                            _id: '$documentType', 
                            count: { $sum: 1 }, 
                            totalSize: { $sum: '$fileSize' },
                            avgSize: { $avg: '$fileSize' }
                        } 
                    },
                    { $sort: { count: -1 } }
                ],
                verificationStatusBreakdown: [
                    { 
                        $group: { 
                            _id: '$processingStatus.verification.status', 
                            count: { $sum: 1 } 
                        } 
                    },
                    { $sort: { count: -1 } }
                ],
                virusScanStatusBreakdown: [
                    { 
                        $group: { 
                            _id: '$processingStatus.virusScan.status', 
                            count: { $sum: 1 } 
                        } 
                    },
                    { $sort: { count: -1 } }
                ],
                fraudRiskBreakdown: [
                    { 
                        $group: { 
                            _id: '$processingStatus.fraudDetection.riskLevel', 
                            count: { $sum: 1 } 
                        } 
                    },
                    { $sort: { count: -1 } }
                ],
                dailyStats: [
                    {
                        $group: {
                            _id: { 
                                $dateToString: { 
                                    format: '%Y-%m-%d', 
                                    date: '$uploadedAt' 
                                } 
                            },
                            count: { $sum: 1 },
                            totalSize: { $sum: '$fileSize' }
                        }
                    },
                    { $sort: { '_id': -1 } },
                    { $limit: 30 }
                ],
                totals: [
                    {
                        $group: {
                            _id: null,
                            totalDocuments: { $sum: 1 },
                            totalSize: { $sum: '$fileSize' },
                            avgSize: { $avg: '$fileSize' },
                            minSize: { $min: '$fileSize' },
                            maxSize: { $max: '$fileSize' }
                        }
                    }
                ],
                needsAttention: [
                    {
                        $match: {
                            $or: [
                                { 'processingStatus.verification.status': 'MANUAL_REVIEW' },
                                { 'processingStatus.fraudDetection.riskLevel': { $in: ['HIGH', 'CRITICAL'] } },
                                { 'auditFlags.flaggedForReview': true },
                                { 'auditFlags.suspicious': true },
                                { 'compliance.legalHold.active': true }
                            ]
                        }
                    },
                    { $count: 'count' }
                ]
            }
        }
    ]);
    
    return results[0] || {
        documentTypeBreakdown: [],
        verificationStatusBreakdown: [],
        virusScanStatusBreakdown: [],
        fraudRiskBreakdown: [],
        dailyStats: [],
        totals: {},
        needsAttention: []
    };
});

// Find duplicate documents
onboardingDocumentSchema.static('findDuplicates', async function(fileHash, tenantId) {
    return this.find({
        fileHash,
        tenantId,
        isDeleted: false
    }).populate({
        path: 'sessionId',
        select: 'sessionId clientType clientData'
    });
});

// Bulk soft delete
onboardingDocumentSchema.static('bulkSoftDelete', async function(documentIds, tenantId, deletedBy, reason, authorization = null) {
    return this.updateMany(
        { documentId: { $in: documentIds }, tenantId },
        {
            $set: {
                isDeleted: true,
                deletedAt: new Date(),
                deletedBy,
                deletionReason: reason,
                deletionAuthorization: authorization
            }
        }
    );
});

// Generate document ID
onboardingDocumentSchema.static('generateDocumentId', function(documentType) {
    const type = documentType.substring(0, 3).toUpperCase();
    const timestamp = DateTime.now().toFormat('yyyyMMddHHmmss');
    const random = crypto.randomBytes(4).toString('hex').toUpperCase();
    
    return `DOC_${type}_${timestamp}_${random}`;
});

// Find documents expiring soon
onboardingDocumentSchema.static('findExpiringSoon', function(tenantId, daysThreshold = 30) {
    const threshold = new Date(Date.now() + daysThreshold * 24 * 60 * 60 * 1000);
    
    return this.find({
        tenantId,
        expiresAt: { $lte: threshold },
        isDeleted: false,
        'compliance.retentionExemption.granted': false
    });
});

// Find documents on legal hold
onboardingDocumentSchema.static('findOnLegalHold', function(tenantId) {
    return this.find({
        tenantId,
        'compliance.legalHold.active': true,
        isDeleted: false
    });
});

// =================================================================================================================
// INSTANCE METHODS
// =================================================================================================================

// Update processing status
onboardingDocumentSchema.method('updateProcessingStatus', async function(type, status, result = {}, performedBy = null) {
    if (!this.processingStatus[type]) {
        throw new Error(`Invalid processing type: ${type}`);
    }
    
    this.processingStatus[type].status = status;
    this.processingStatus[type].result = result;
    this.processingStatus[type].attempts = (this.processingStatus[type].attempts || 0) + 1;
    
    switch(type) {
        case 'virusScan':
            this.processingStatus.virusScan.scannedAt = new Date();
            if (result.threats) this.processingStatus.virusScan.threats = result.threats;
            if (status === 'CLEAN' || status === 'INFECTED') {
                this.processingStatus.virusScan.completedAt = new Date();
            }
            break;
        case 'ocr':
            this.processingStatus.ocr.processedAt = new Date();
            if (result.text) this.processingStatus.ocr.text = result.text;
            if (result.confidence) this.processingStatus.ocr.confidence = result.confidence;
            break;
        case 'verification':
            this.processingStatus.verification.verifiedAt = new Date();
            this.processingStatus.verification.verifiedBy = result.verifiedBy || performedBy;
            this.processingStatus.verification.confidence = result.confidence;
            this.processingStatus.verification.flags = result.flags || [];
            break;
        case 'fraudDetection':
            this.processingStatus.fraudDetection.analyzedAt = new Date();
            this.processingStatus.fraudDetection.riskScore = result.score;
            this.processingStatus.fraudDetection.riskLevel = result.level;
            this.processingStatus.fraudDetection.flags = result.flags || [];
            break;
    }
    
    this.metadata.updatedAt = new Date();
    this.metadata.updatedBy = performedBy;
    
    return this.save();
});

// Add to chain of custody
onboardingDocumentSchema.method('addToChainOfCustody', async function(action, performedBy, options = {}) {
    const entry = {
        action,
        performedBy,
        ipAddress: options.ipAddress,
        userAgent: options.userAgent,
        sessionId: options.sessionId,
        reason: options.reason,
        correlationId: options.correlationId || `corr_${Date.now()}_${crypto.randomBytes(8).toString('hex')}`,
        timestamp: new Date()
    };
    
    entry.hash = crypto
        .createHash('sha256')
        .update(`${entry.action}|${entry.performedBy}|${entry.timestamp.getTime()}|${entry.reason || ''}|${entry.correlationId}`)
        .digest('hex');
    
    this.chainOfCustody.push(entry);
    this.metadata.updatedAt = new Date();
    this.metadata.updatedBy = performedBy;
    
    return this.save();
});

// Soft delete
onboardingDocumentSchema.method('softDelete', async function(deletedBy, reason, authorization = null) {
    this.isDeleted = true;
    this.deletedAt = new Date();
    this.deletedBy = deletedBy;
    this.deletionReason = reason;
    this.deletionAuthorization = authorization;
    
    await this.addToChainOfCustody('DELETED', deletedBy, { reason });
    
    return this.save();
});

// Restore document
onboardingDocumentSchema.method('restore', async function(restoredBy, reason = null) {
    this.isDeleted = false;
    this.deletedAt = null;
    this.deletedBy = null;
    this.deletionReason = null;
    
    await this.addToChainOfCustody('RESTORED', restoredBy, { reason });
    
    return this.save();
});

// Place on legal hold
onboardingDocumentSchema.method('placeOnLegalHold', async function(reason, initiatedBy, caseNumber = null) {
    this.compliance.legalHold = {
        active: true,
        reason,
        initiatedBy,
        initiatedAt: new Date(),
        caseNumber
    };
    
    await this.addToChainOfCustody('LEGAL_HOLD_PLACED', initiatedBy, { 
        reason: `Legal hold placed: ${reason}` 
    });
    
    return this.save();
});

// Release legal hold
onboardingDocumentSchema.method('releaseLegalHold', async function(releasedBy, reason) {
    if (this.compliance.legalHold) {
        this.compliance.legalHold.active = false;
        
        await this.addToChainOfCustody('LEGAL_HOLD_RELEASED', releasedBy, { 
            reason: `Legal hold released: ${reason}` 
        });
    }
    return this.save();
});

// Get chain of custody
onboardingDocumentSchema.method('getChainOfCustody', function() {
    return this.chainOfCustody.map(event => ({
        action: event.action,
        performedBy: event.performedBy,
        timestamp: event.timestamp,
        ipAddress: event.ipAddress,
        reason: event.reason,
        hash: event.hash
    }));
});

// Verify integrity
onboardingDocumentSchema.method('verifyIntegrity', function() {
    if (!this.fileData || !this.fileHash) {
        return { valid: false, reason: 'Missing file data or hash' };
    }
    
    const currentHash = crypto
        .createHash('sha256')
        .update(this.fileData)
        .digest('hex');
    
    return {
        valid: currentHash === this.fileHash,
        storedHash: this.fileHash,
        currentHash,
        timestamp: new Date().toISOString()
    };
});

// Get summary
onboardingDocumentSchema.method('getSummary', function() {
    return {
        documentId: this.documentId,
        sessionId: this.sessionId,
        tenantId: this.tenantId,
        documentType: this.documentType,
        fileName: this.fileName,
        fileSize: this.fileSizeFormatted,
        mimeType: this.mimeType,
        uploadedAt: this.uploadedAt,
        verificationStatus: this.processingStatus.verification.status,
        virusScanStatus: this.processingStatus.virusScan.status,
        riskLevel: this.processingStatus.fraudDetection.riskLevel,
        needsReview: this.needsReview,
        isExpired: this.isExpired,
        isDeleted: this.isDeleted
    };
});

// =================================================================================================================
// MIDDLEWARE
// =================================================================================================================

// Pre-save middleware
onboardingDocumentSchema.pre('save', function(next) {
    this.metadata.updatedAt = new Date();
    
    if (!this.documentId) {
        const type = this.documentType.substring(0, 3).toUpperCase();
        const timestamp = DateTime.now().toFormat('yyyyMMddHHmmss');
        const random = crypto.randomBytes(4).toString('hex').toUpperCase();
        this.documentId = `DOC_${type}_${timestamp}_${random}`;
    }
    
    if (!this.fileHash && this.fileData) {
        this.fileHash = crypto
            .createHash('sha256')
            .update(this.fileData)
            .digest('hex');
    }
    
    if (this.isNew) {
        this.chainOfCustody.push({
            action: 'UPLOADED',
            performedBy: this.metadata.createdBy || 'system',
            timestamp: new Date(),
            hash: crypto
                .createHash('sha256')
                .update(`UPLOADED|${this.metadata.createdBy || 'system'}|${Date.now()}`)
                .digest('hex')
        });
    }
    
    next();
});

// Pre-find middleware for soft delete
onboardingDocumentSchema.pre(/^find/, function(next) {
    if (!this.getQuery().includeDeleted) {
        this.where({ isDeleted: { $ne: true } });
    }
    next();
});

// =================================================================================================================
// EXPORT
// =================================================================================================================
module.exports = mongoose.model('OnboardingDocument', onboardingDocumentSchema);
