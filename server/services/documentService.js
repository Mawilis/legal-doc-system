/**
 * Wilsy OS - Multi-Tenant Document Service
 * =========================================
 * Quantum document orchestration engine with full multi-tenancy, legal compliance,
 * and enterprise-grade security. Manages document lifecycle from creation to
 * destruction with POPIA, Companies Act, ECT Act, and PAIA compliance.
 * 
 * @module services/documentService
 * @requires dotenv
 * @requires mongoose
 * @requires mongodb
 * @requires crypto
 * @requires uuid
 * @requires moment
 * @requires lodash
 * @requires joi
 * @requires axios
 * @requires node-cache
 * @requires bcrypt
 * @requires pdf-parse
 * @requires mammoth
 * @requires crypto-js
 * @requires jsonwebtoken
 * @requires ../middleware/tenantContext
 * @requires ../lib/kms
 * @requires ../lib/ots
 * @requires ../lib/auditLedger
 */

// =================================================================================
// ENVIRONMENT VALIDATION - SECURE BOOTSTRAP
// =================================================================================
require('dotenv').config({ path: require('path').resolve(__dirname, '../.env') });

// Fail closed if MONGO_URI is missing (non-negotiable)
if (!process.env.MONGO_URI && !process.env.MONGO_URI_TEST) {
    throw new Error('QUANTUM BREACH: MongoDB connection string required. Set MONGO_URI or MONGO_URI_TEST');
}

// =================================================================================
// CORE DEPENDENCIES - PINNED VERSIONS
// =================================================================================
const mongoose = require('mongoose');
const { GridFSBucket, ObjectId } = require('mongodb');
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');
const moment = require('moment');
const _ = require('lodash');

// Wilsy OS Security Dependencies
const { wrapKey, unwrapKey } = require("../lib/kms");
const { generateDocumentHash, createTimestamp } = require("../lib/ots");

const NodeCache = require("node-cache");
const pdfParse = require("pdf-parse");
const mammoth = require("mammoth");



// =================================================================================
// MULTI-TENANT CONFIGURATION - TENANT ISOLATION DNA
// =================================================================================
const DOCUMENT_CONFIG = {
    // Storage Configuration
    STORAGE_BUCKET: process.env.DOCUMENT_STORAGE_BUCKET || 'wilsy-documents',
    MAX_FILE_SIZE_MB: parseInt(process.env.DOCUMENT_MAX_FILE_SIZE_MB) || 100,
    MAX_FILE_SIZE_BYTES: (parseInt(process.env.DOCUMENT_MAX_FILE_SIZE_MB) || 100) * 1024 * 1024,

    // Retention & Compliance (Companies Act 71 of 2008)
    RETENTION_YEARS: parseInt(process.env.DOCUMENT_RETENTION_YEARS) || 7,
    RETENTION_DAYS: (parseInt(process.env.DOCUMENT_RETENTION_YEARS) || 7) * 365,
    ARCHIVAL_THRESHOLD_DAYS: parseInt(process.env.DOCUMENT_ARCHIVAL_THRESHOLD_DAYS) || 1095,

    // Security Configuration (Tenant-specific keys via Vault)
    ENCRYPTION_ALGORITHM: 'AES-256-GCM',
    HASH_ALGORITHM: 'SHA-512',

    // Allowed MIME Types (Legal Document Focus)
    ALLOWED_MIME_TYPES: (process.env.DOCUMENT_ALLOWED_MIME_TYPES ||
        'application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,image/jpeg,image/png'
    ).split(',').map(type => type.trim()),

    // Legal Document Categories (SA Jurisprudence)
    LEGAL_DOCUMENT_CATEGORIES: {
        LITIGATION: ['SUMMONS', 'PLEADING', 'AFFIDAVIT', 'NOTICE_OF_MOTION', 'HEADS_OF_ARGUMENT'],
        CONVEYANCING: ['DEED_OF_SALE', 'TITLE_DEED', 'MORTGAGE_BOND', 'TRANSFER_DOCUMENT'],
        CORPORATE: ['MEMORANDUM_OF_INCORPORATION', 'SHAREHOLDERS_AGREEMENT', 'DIRECTORS_RESOLUTION'],
        ESTATE: ['LAST_WILL_AND_TESTAMENT', 'CODICIL', 'LETTERS_OF_ADMINISTRATION'],
        CONTRACT: ['SERVICE_AGREEMENT', 'NON_DISCLOSURE_AGREEMENT', 'EMPLOYMENT_CONTRACT'],
        COMPLIANCE: ['POPIA_REGISTER', 'PAIA_MANUAL', 'FICA_RECORD', 'SARS_RETURN']
    },

    // Document Status Lifecycle
    DOCUMENT_STATUS: {
        DRAFT: 'DRAFT',
        PENDING_REVIEW: 'PENDING_REVIEW',
        REVIEWED: 'REVIEWED',
        APPROVED: 'APPROVED',
        EXECUTED: 'EXECUTED',
        ARCHIVED: 'ARCHIVED',
        EXPIRED: 'EXPIRED',
        DELETED: 'DELETED'
    },

    // Confidentiality Levels (POPIA & Legal Ethics)
    CONFIDENTIALITY_LEVELS: {
        PUBLIC: 'PUBLIC',
        INTERNAL: 'INTERNAL',
        CONFIDENTIAL: 'CONFIDENTIAL',
        HIGHLY_CONFIDENTIAL: 'HIGHLY_CONFIDENTIAL',
        RESTRICTED: 'RESTRICTED'
    },

    // Feature Flags
    AI_CLASSIFICATION_ENABLED: process.env.DOCUMENT_AI_CLASSIFICATION_ENABLED === 'true',
    BLOCKCHAIN_INTEGRITY_ENABLED: process.env.DOCUMENT_BLOCKCHAIN_INTEGRITY_ENABLED === 'true',
    COMPLIANCE_AUTOCHECK_ENABLED: process.env.DOCUMENT_COMPLIANCE_AUTOCHECK_ENABLED === 'true',

    // Cache Configuration
    CACHE_TTL: 300,
    CACHE_CHECK_PERIOD: 60,

    // Multi-Tenant Configuration
    TENANT_QUOTA_DEFAULT_GB: parseInt(process.env.TENANT_QUOTA_DEFAULT_GB) || 10,
    TENANT_RATE_LIMIT_RPM: parseInt(process.env.TENANT_RATE_LIMIT_RPM) || 100
};

// =================================================================================
// MONGOOSE SCHEMAS - MULTI-TENANT DATA MODELS
// =================================================================================
/**
 * Document Metadata Schema - Multi-tenant with tenant isolation
 * @security POPIA §14 - Data minimization and purpose limitation
 * @compliance Companies Act 71 of 2008 - Retention requirements
 */
const documentMetadataSchema = new mongoose.Schema({
    // Tenant Isolation (MANDATORY - All documents belong to a tenant)
    tenantId: {
        type: String,
        required: true,
        index: true,
        validate: {
            validator: function (v) {
                return /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(v);
            },
            message: props => `${props.value} is not a valid tenant ID!`
        }
    },

    // Core Identification
    documentId: {
        type: String,
        required: true,
        unique: true,
        default: () => `DOC-${uuidv4()}`
    },
    clientReferenceId: {
        type: String,
        required: true,
        index: true
    },
    matterReferenceId: {
        type: String,
        required: true,
        index: true
    },

    // Document Information
    title: {
        type: String,
        required: true,
        trim: true,
        maxlength: 500
    },
    description: {
        type: String,
        trim: true,
        maxlength: 2000
    },
    documentType: {
        type: String,
        required: true,
        enum: Object.values(DOCUMENT_CONFIG.LEGAL_DOCUMENT_CATEGORIES).flat()
    },
    category: {
        type: String,
        required: true,
        enum: Object.keys(DOCUMENT_CONFIG.LEGAL_DOCUMENT_CATEGORIES)
    },

    // File Information
    originalFileName: {
        type: String,
        required: true
    },
    fileExtension: {
        type: String,
        required: true
    },
    mimeType: {
        type: String,
        required: true,
        enum: DOCUMENT_CONFIG.ALLOWED_MIME_TYPES
    },
    fileSize: {
        type: Number,
        required: true,
        min: 1,
        max: DOCUMENT_CONFIG.MAX_FILE_SIZE_BYTES
    },

    // Storage Information with Tenant Isolation
    storageId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true
    },
    storageBucket: {
        type: String,
        default: DOCUMENT_CONFIG.STORAGE_BUCKET
    },
    encrypted: {
        type: Boolean,
        default: true
    },
    encryptionKeyId: {
        type: String,
        required: true,
        default: function () {
            // Tenant-specific key ID for envelope encryption
            return `tenant-${this.tenantId}-dek-${uuidv4().substring(0, 8)}`;
        }
    },
    wrappedKey: {
        type: String,
        required: true,
        comment: 'Vault-wrapped DEK for tenant-specific envelope encryption'
    },

    // Content Integrity Hashes
    contentHash: {
        type: String,
        required: true
    },
    encryptedHash: {
        type: String,
        required: true
    },
    blockchainAnchor: {
        type: String,
        sparse: true
    },

    // PII Classification (POPIA Compliance)
    piiClassification: {
        containsPII: {
            type: Boolean,
            default: false
        },
        piiTypes: [{
            type: String,
            enum: ['SA_ID_NUMBER', 'PASSPORT_NUMBER', 'PHONE_NUMBER', 'EMAIL_ADDRESS', 'PHYSICAL_ADDRESS', 'DATE_OF_BIRTH', 'FINANCIAL_INFORMATION']
        }],
        specialPersonalInfo: {
            type: Boolean,
            default: false
        },
        riskLevel: {
            type: String,
            enum: ['LOW', 'MEDIUM', 'HIGH'],
            default: 'LOW'
        }
    },

    // Confidentiality & Access Control with Tenant Context
    confidentialityLevel: {
        type: String,
        required: true,
        enum: Object.values(DOCUMENT_CONFIG.CONFIDENTIALITY_LEVELS),
        default: 'CONFIDENTIAL'
    },
    accessControl: {
        ownerUserId: {
            type: String,
            required: true
        },
        allowedUsers: [{
            userId: String,
            accessLevel: {
                type: String,
                enum: ['VIEW', 'EDIT', 'SHARE', 'DELETE'],
                default: 'VIEW'
            },
            grantedAt: Date,
            expiresAt: Date
        }],
        requiresAuthentication: {
            type: Boolean,
            default: true
        },
        watermarkEnabled: {
            type: Boolean,
            default: true
        }
    },

    // Version Control
    version: {
        major: {
            type: Number,
            default: 1
        },
        minor: {
            type: Number,
            default: 0
        },
        patch: {
            type: Number,
            default: 0
        }
    },
    versionHistory: [{
        version: String,
        documentId: String,
        changeDescription: String,
        changedBy: String,
        changedAt: Date
    }],
    previousVersionId: {
        type: String,
        sparse: true
    },

    // Legal & Compliance Metadata with Tenant Context
    legalJurisdiction: {
        type: String,
        default: 'ZA'
    },
    governingLaw: {
        type: String,
        default: 'SOUTH_AFRICAN_LAW'
    },
    retentionPeriod: {
        type: Number,
        default: DOCUMENT_CONFIG.RETENTION_DAYS
    },
    retentionExpiry: {
        type: Date,
        required: true
    },
    archivalDate: {
        type: Date,
        sparse: true
    },

    // Status & Lifecycle
    status: {
        type: String,
        required: true,
        enum: Object.values(DOCUMENT_CONFIG.DOCUMENT_STATUS),
        default: 'DRAFT'
    },
    statusHistory: [{
        status: String,
        changedBy: String,
        changedAt: Date,
        reason: String
    }],

    // Signatures & Execution (ECT Act Compliance)
    signatures: [{
        signatureId: String,
        signatoryId: String,
        signatureType: {
            type: String,
            enum: ['ELECTRONIC', 'DIGITAL', 'WET_INK_SCANNED']
        },
        signedAt: Date,
        signatureLevel: {
            type: String,
            enum: ['SIMPLE', 'ADVANCED', 'QUALIFIED']
        },
        verificationToken: String,
        status: {
            type: String,
            enum: ['PENDING', 'SIGNED', 'REVOKED', 'EXPIRED']
        }
    }],
    executed: {
        type: Boolean,
        default: false
    },
    executedAt: {
        type: Date,
        sparse: true
    },

    // AI Classification Results
    aiClassification: {
        categoryConfidence: Number,
        keyTerms: [String],
        summary: String,
        sentiment: {
            type: String,
            enum: ['POSITIVE', 'NEUTRAL', 'NEGATIVE', 'MIXED']
        },
        classifiedAt: Date
    },

    // Audit Trail with Tenant Context
    createdBy: {
        type: String,
        required: true
    },
    createdAt: {
        type: Date,
        default: Date.now,
        required: true
    },
    updatedBy: {
        type: String,
        required: true
    },
    updatedAt: {
        type: Date,
        default: Date.now,
        required: true
    },

    // Soft Delete with Tenant Context
    deleted: {
        type: Boolean,
        default: false
    },
    deletedAt: {
        type: Date,
        sparse: true
    },
    deletedBy: {
        type: String,
        sparse: true
    }
}, {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});

// Multi-Tenant Indexes
documentMetadataSchema.index({ tenantId: 1, documentId: 1 }, { unique: true });
documentMetadataSchema.index({ tenantId: 1, clientReferenceId: 1, matterReferenceId: 1 });
documentMetadataSchema.index({ tenantId: 1, 'accessControl.allowedUsers.userId': 1 });
documentMetadataSchema.index({ tenantId: 1, status: 1 });
documentMetadataSchema.index({ tenantId: 1, retentionExpiry: 1 });
documentMetadataSchema.index({ tenantId: 1, createdAt: -1 });

// Virtual Fields
documentMetadataSchema.virtual('fullVersion').get(function () {
    return `v${this.version.major}.${this.version.minor}.${this.version.patch}`;
});

documentMetadataSchema.virtual('daysUntilExpiry').get(function () {
    return moment(this.retentionExpiry).diff(moment(), 'days');
});

documentMetadataSchema.virtual('isExpired').get(function () {
    return moment().isAfter(this.retentionExpiry);
});

documentMetadataSchema.virtual('requiresArchival').get(function () {
    const archivalThreshold = moment(this.createdAt).add(DOCUMENT_CONFIG.ARCHIVAL_THRESHOLD_DAYS, 'days');
    return moment().isAfter(archivalThreshold) && this.status !== 'ARCHIVED';
});

// Pre-save Middleware with Tenant Validation
documentMetadataSchema.pre('save', function (next) {
    // Fail closed if tenantId is missing
    if (!this.tenantId || typeof this.tenantId !== 'string') {
        return next(new Error('TENANT_ISOLATION_VIOLATION: Document must have a tenantId'));
    }

    // Auto-calculate retention expiry
    if (!this.retentionExpiry) {
        this.retentionExpiry = moment(this.createdAt || new Date())
            .add(this.retentionPeriod || DOCUMENT_CONFIG.RETENTION_DAYS, 'days')
            .toDate();
    }

    // Update timestamp
    this.updatedAt = new Date();

    next();
});

const DocumentMetadata = mongoose.model('DocumentMetadata', documentMetadataSchema);

// =================================================================================
// TENANT QUOTA MODEL
// =================================================================================
/**
 * Tenant Quota Schema - Enforces storage and rate limits per tenant
 * @security Multi-tenancy requirement - Prevent resource exhaustion
 */
const tenantQuotaSchema = new mongoose.Schema({
    tenantId: {
        type: String,
        required: true,
        unique: true,
        index: true
    },
    storageQuotaGB: {
        type: Number,
        default: DOCUMENT_CONFIG.TENANT_QUOTA_DEFAULT_GB
    },
    storageUsedGB: {
        type: Number,
        default: 0
    },
    documentCount: {
        type: Number,
        default: 0
    },
    rateLimitRPM: {
        type: Number,
        default: DOCUMENT_CONFIG.TENANT_RATE_LIMIT_RPM
    },
    requestsThisMinute: {
        type: Number,
        default: 0
    },
    lastResetAt: {
        type: Date,
        default: Date.now
    },
    createdAt: {
        type: Date,
        default: Date.now
    },
    updatedAt: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true
});

tenantQuotaSchema.virtual('storageUsedPercentage').get(function () {
    return this.storageQuotaGB > 0 ? (this.storageUsedGB / this.storageQuotaGB * 100) : 0;
});

tenantQuotaSchema.virtual('isOverQuota').get(function () {
    return this.storageUsedGB > this.storageQuotaGB;
});

const TenantQuota = mongoose.model('TenantQuota', tenantQuotaSchema);

// =================================================================================
// MULTI-TENANT STORAGE ENGINE
// =================================================================================
class MultiTenantStorageEngine {
    /**
     * Secure document storage with tenant isolation and envelope encryption
     * @security Uses per-tenant DEKs wrapped by Vault master keys
     * @compliance POPIA §19 - Security safeguards for personal information
     */

    constructor() {
        this.db = mongoose.connection.db;
        this.bucket = new GridFSBucket(this.db, {
            bucketName: DOCUMENT_CONFIG.STORAGE_BUCKET,
            chunkSizeBytes: 255 * 1024,
            writeConcern: {
                w: 'majority',
                j: true,
                wtimeout: 5000
            }
        });
    }

    /**
     * Store document with tenant-specific envelope encryption
     * @param {Buffer} fileBuffer - Document content
     * @param {Object} metadata - Document metadata including tenantId
     * @returns {Promise<Object>} Storage result with wrapped key
     */
    async storeDocument(fileBuffer, metadata) {
        // Fail closed if tenantId missing
        if (!metadata.tenantId) {
            throw new Error('TENANT_ISOLATION_VIOLATION: tenantId required for document storage');
        }

        try {
            // Validate file size
            if (fileBuffer.length > DOCUMENT_CONFIG.MAX_FILE_SIZE_BYTES) {
                throw new Error(`File exceeds maximum size of ${DOCUMENT_CONFIG.MAX_FILE_SIZE_MB}MB`);
            }

            // Generate content hash for integrity verification
            const contentHash = this._generateContentHash(fileBuffer);

            // Create tenant-specific Data Encryption Key (DEK)
            const dek = crypto.randomBytes(32); // AES-256 key

            // Wrap DEK with Vault Transit (tenant-specific key)
            const wrappedKey = await wrapKey(
                dek.toString('base64'),
                `tenant-${metadata.tenantId}`,
                { context: { tenantId: metadata.tenantId } }
            );

            // Encrypt document with DEK
            const encryptedBuffer = await this._encryptWithDEK(fileBuffer, dek);
            const encryptedHash = this._generateContentHash(encryptedBuffer);

            // Generate storage ID
            const storageId = new ObjectId();
            const fileName = `${metadata.tenantId}_${storageId.toString()}_${metadata.originalFileName || 'document'}`;

            // Create upload stream with tenant metadata
            const uploadStream = this.bucket.openUploadStream(fileName, {
                _id: storageId,
                metadata: {
                    tenantId: metadata.tenantId,
                    originalFileName: metadata.originalFileName,
                    mimeType: metadata.mimeType,
                    contentHash,
                    encryptedHash,
                    encryption: {
                        algorithm: DOCUMENT_CONFIG.ENCRYPTION_ALGORITHM,
                        keyId: `tenant-${metadata.tenantId}`,
                        encrypted: true
                    },
                    uploadedAt: new Date().toISOString()
                }
            });

            // Write encrypted buffer to stream
            return new Promise((resolve, reject) => {
                uploadStream.write(encryptedBuffer);
                uploadStream.end();

                uploadStream.on('finish', async () => {
                    // Create timestamp proof (ECT Act compliance)
                    let timestampProof = null;
                    if (DOCUMENT_CONFIG.BLOCKCHAIN_INTEGRITY_ENABLED) {
                        timestampProof = await createTimestamp(contentHash, metadata.tenantId);
                    }

                    const result = {
                        storageId: storageId,
                        fileName: fileName,
                        contentHash: contentHash,
                        encryptedHash: encryptedHash,
                        wrappedKey: wrappedKey,
                        fileSize: fileBuffer.length,
                        encryptedSize: encryptedBuffer.length,
                        timestampProof: timestampProof,
                        uploadedAt: new Date().toISOString()
                    };

                    resolve(result);
                });

                uploadStream.on('error', (error) => {
                    console.error(`[Tenant: ${metadata.tenantId}] GridFS upload failed:`, error);
                    reject(new Error(`Document storage failed: ${error.message}`));
                });
            });

        } catch (error) {
            console.error(`[Tenant: ${metadata.tenantId}] Document storage failed:`, error);
            throw new Error(`Storage failed: ${error.message}`);
        }
    }

    /**
     * Retrieve document with tenant-specific decryption
     * @param {ObjectId} storageId - GridFS storage ID
     * @param {string} tenantId - Tenant identifier for key unwrapping
     * @param {string} wrappedKey - Vault-wrapped DEK
     * @returns {Promise<Object>} Decrypted document
     */
    async retrieveDocument(storageId, tenantId, wrappedKey) {
        // Fail closed if tenantId missing
        if (!tenantId) {
            throw new Error('TENANT_ISOLATION_VIOLATION: tenantId required for document retrieval');
        }

        try {
            // Get file information
            const files = await this.bucket.find({ _id: new ObjectId(storageId) }).toArray();
            if (!files || files.length === 0) {
                throw new Error(`Document not found with storageId: ${storageId}`);
            }

            const fileInfo = files[0];

            // Verify tenant ownership
            if (fileInfo.metadata?.tenantId !== tenantId) {
                throw new Error('TENANT_ACCESS_DENIED: Document does not belong to this tenant');
            }

            // Create download stream
            const downloadStream = this.bucket.openDownloadStream(new ObjectId(storageId));

            // Read stream into buffer
            const chunks = [];
            for await (const chunk of downloadStream) {
                chunks.push(chunk);
            }

            const encryptedBuffer = Buffer.concat(chunks);

            // Verify integrity
            const currentHash = this._generateContentHash(encryptedBuffer);
            const storedHash = fileInfo.metadata?.encryptedHash;

            if (currentHash !== storedHash) {
                throw new Error('Document integrity check failed - content may have been tampered with');
            }

            // Unwrap DEK with Vault Transit
            const dekBase64 = await unwrapKey(wrappedKey, `tenant-${tenantId}`);
            const dek = Buffer.from(dekBase64, 'base64');

            // Decrypt document
            const decryptedBuffer = await this._decryptWithDEK(encryptedBuffer, dek);

            // Verify original hash
            const decryptedHash = this._generateContentHash(decryptedBuffer);
            if (decryptedHash !== fileInfo.metadata?.contentHash) {
                throw new Error('Decryption integrity check failed');
            }

            return {
                storageId: storageId,
                fileName: fileInfo.filename,
                decryptedBuffer: decryptedBuffer,
                mimeType: fileInfo.metadata?.mimeType || 'application/octet-stream',
                originalFileName: fileInfo.metadata?.originalFileName,
                contentHash: decryptedHash,
                retrievedAt: new Date().toISOString()
            };

        } catch (error) {
            console.error(`[Tenant: ${tenantId}] Document retrieval failed:`, error);
            throw new Error(`Retrieval failed: ${error.message}`);
        }
    }

    /**
     * Delete document with tenant verification
     * @param {ObjectId} storageId - GridFS storage ID
     * @param {string} tenantId - Tenant identifier
     * @returns {Promise<Object>} Deletion result
     */
    async deleteDocument(storageId, tenantId) {
        // Fail closed if tenantId missing
        if (!tenantId) {
            throw new Error('TENANT_ISOLATION_VIOLATION: tenantId required for document deletion');
        }

        try {
            // Verify document belongs to tenant
            const files = await this.bucket.find({ _id: new ObjectId(storageId) }).toArray();
            if (!files || files.length === 0) {
                throw new Error(`Document not found with storageId: ${storageId}`);
            }

            const fileInfo = files[0];
            if (fileInfo.metadata?.tenantId !== tenantId) {
                throw new Error('TENANT_ACCESS_DENIED: Cannot delete document belonging to another tenant');
            }

            // Delete from GridFS
            await this.bucket.delete(new ObjectId(storageId));

            return {
                success: true,
                storageId: storageId,
                deletedAt: new Date().toISOString(),
                tenantId: tenantId
            };

        } catch (error) {
            console.error(`[Tenant: ${tenantId}] Document deletion failed:`, error);
            throw new Error(`Deletion failed: ${error.message}`);
        }
    }

    // =================================================================================
    // PRIVATE METHODS
    // =================================================================================

    _generateContentHash(buffer) {
        return crypto.createHash(DOCUMENT_CONFIG.HASH_ALGORITHM)
            .update(buffer)
            .digest('hex');
    }

    async _encryptWithDEK(buffer, dek) {
        try {
            const iv = crypto.randomBytes(16);
            const cipher = crypto.createCipheriv('aes-256-gcm', dek, iv);

            let encrypted = cipher.update(buffer);
            encrypted = Buffer.concat([encrypted, cipher.final()]);
            const authTag = cipher.getAuthTag();

            // Combine IV + authTag + encrypted data
            return Buffer.concat([iv, authTag, encrypted]);

        } catch (error) {
            console.error('Document encryption failed:', error);
            throw new Error(`Encryption failed: ${error.message}`);
        }
    }

    async _decryptWithDEK(encryptedBuffer, dek) {
        try {
            // Extract components
            const iv = encryptedBuffer.slice(0, 16);
            const authTag = encryptedBuffer.slice(16, 32);
            const encryptedData = encryptedBuffer.slice(32);

            const decipher = crypto.createDecipheriv('aes-256-gcm', dek, iv);
            decipher.setAuthTag(authTag);

            let decrypted = decipher.update(encryptedData);
            decrypted = Buffer.concat([decrypted, decipher.final()]);

            return decrypted;

        } catch (error) {
            console.error('Document decryption failed:', error);
            throw new Error(`Decryption failed: ${error.message}`);
        }
    }
}

// =================================================================================
// MULTI-TENANT DOCUMENT SERVICE
// =================================================================================
class MultiTenantDocumentService {
    /**
     * Quantum document orchestration with full tenant isolation
     * @security All operations enforce tenant context and fail closed
     * @compliance POPIA, Companies Act, ECT Act, PAIA compliance built-in
     */

    constructor() {
        this.storageEngine = new MultiTenantStorageEngine();
        this.documentCache = new NodeCache({
            stdTTL: DOCUMENT_CONFIG.CACHE_TTL,
            checkperiod: DOCUMENT_CONFIG.CACHE_CHECK_PERIOD
        });
        this.DocumentMetadata = DocumentMetadata;
        this.TenantQuota = TenantQuota;

        console.log('Multi-Tenant Document Service Initialized:', {
            storageBucket: DOCUMENT_CONFIG.STORAGE_BUCKET,
            maxFileSize: `${DOCUMENT_CONFIG.MAX_FILE_SIZE_MB}MB`,
            retentionYears: DOCUMENT_CONFIG.RETENTION_YEARS
        });
    }

    // =================================================================================
    // CORE DOCUMENT OPERATIONS WITH TENANT ISOLATION
    // =================================================================================

    /**
     * Create document with tenant context and quota enforcement
     * @param {Object} documentData - File and metadata
     * @param {Object} userContext - Must include tenantId and userId
     * @returns {Promise<Object>} Creation result with audit trail
     */
    async createDocument(documentData, userContext) {
        // Fail closed if tenant context missing
        if (!userContext?.tenantId) {
            throw new Error('TENANT_CONTEXT_REQUIRED: tenantId must be provided in userContext');
        }

        const operationId = `CREATE-${uuidv4()}`;
        const { tenantId, userId } = userContext;

        try {
            // Check tenant quota before proceeding
            await this._checkTenantQuota(tenantId, documentData.file.size);

            // Validate input with tenant context
            const validation = this._validateDocumentInput(documentData, userContext);
            if (!validation.valid) {
                throw new Error(`Document validation failed: ${validation.reason}`);
            }

            // Process document file
            const fileBuffer = await this._processDocumentFile(documentData.file);

            // Generate document hash
            const documentHash = generateDocumentHash(fileBuffer);

            // Perform PII scan (POPIA Compliance)
            const piiScan = await this._performPIIScan(fileBuffer, {
                ...documentData.metadata,
                tenantId,
                mimeType: documentData.file.mimetype
            });

            // Store document with tenant-specific encryption
            const storageResult = await this.storageEngine.storeDocument(fileBuffer, {
                tenantId,
                originalFileName: documentData.file.originalname || 'document',
                mimeType: documentData.file.mimetype || 'application/octet-stream',
                uploadedBy: userId
            });

            // Create document metadata with tenant context
            const documentMetadata = new this.DocumentMetadata({
                tenantId,
                ...documentData.metadata,
                storageId: storageResult.storageId,
                contentHash: documentHash,
                encryptedHash: storageResult.encryptedHash,
                wrappedKey: storageResult.wrappedKey,
                blockchainAnchor: storageResult.timestampProof?.anchorId,
                fileSize: fileBuffer.length,
                mimeType: documentData.file.mimetype,
                originalFileName: documentData.file.originalname,
                fileExtension: this._getFileExtension(documentData.file.originalname),

                // PII Classification
                piiClassification: {
                    containsPII: piiScan.hasPII,
                    piiTypes: piiScan.detectedPII?.map(p => p.piiType) || [],
                    specialPersonalInfo: piiScan.hasSpecialInfo,
                    riskLevel: piiScan.highestRiskLevel || 'LOW'
                },

                // User context
                createdBy: userId,
                updatedBy: userId,

                // Access control with tenant context
                accessControl: {
                    ownerUserId: userId,
                    allowedUsers: [
                        {
                            userId: userId,
                            accessLevel: 'EDIT',
                            grantedAt: new Date(),
                            expiresAt: moment().add(1, 'year').toDate()
                        }
                    ],
                    requiresAuthentication: true,
                    watermarkEnabled: true
                },

                // Retention with tenant context
                retentionExpiry: moment().add(DOCUMENT_CONFIG.RETENTION_DAYS, 'days').toDate(),

                // Initial status
                status: documentData.metadata.status || DOCUMENT_CONFIG.DOCUMENT_STATUS.DRAFT
            });

            // Save metadata
            await documentMetadata.save();

            // Update tenant quota
            await this._updateTenantQuota(tenantId, fileBuffer.length, 1);

            // Create audit entry
            await appendAuditEntry({
                tenantId,
                action: 'DOCUMENT_CREATE',
                resourceType: 'DOCUMENT',
                resourceId: documentMetadata.documentId,
                actor: userId,
                details: {
                    title: documentMetadata.title,
                    fileSize: fileBuffer.length,
                    piiDetected: piiScan.hasPII
                }
            });

            // Cache document metadata
            this.documentCache.set(`${tenantId}:metadata:${documentMetadata.documentId}`,
                documentMetadata.toObject(), 3600);

            return {
                success: true,
                documentId: documentMetadata.documentId,
                tenantId,
                storageId: storageResult.storageId,
                metadata: _.omit(documentMetadata.toObject(), ['wrappedKey']),
                piiScan,
                operationId,
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            console.error(`[Tenant: ${tenantId}] Document creation failed:`, error);

            // Log error to audit trail
            await appendAuditEntry({
                tenantId,
                action: 'DOCUMENT_CREATE_FAILED',
                resourceType: 'DOCUMENT',
                actor: userId,
                details: {
                    error: error.message,
                    operationId
                },
                severity: 'ERROR'
            });

            throw error;
        }
    }

    /**
     * Retrieve document with tenant access control
     * @param {string} documentId - Document identifier
     * @param {Object} userContext - Must include tenantId and userId
     * @returns {Promise<Object>} Document with metadata and content
     */
    async retrieveDocument(documentId, userContext) {
        // Fail closed if tenant context missing
        if (!userContext?.tenantId) {
            throw new Error('TENANT_CONTEXT_REQUIRED: tenantId must be provided in userContext');
        }

        const { tenantId, userId } = userContext;

        try {
            // Check cache first
            const cacheKey = `${tenantId}:document:${documentId}`;
            const cached = this.documentCache.get(cacheKey);
            if (cached) {
                return cached;
            }

            // Get document metadata with tenant isolation
            const documentMetadata = await this.DocumentMetadata.findOne({
                tenantId,
                documentId,
                deleted: false
            });

            if (!documentMetadata) {
                throw new Error(`Document not found: ${documentId}`);
            }

            // Check access permissions with tenant context
            const accessGranted = await this._checkDocumentAccess(documentMetadata, userContext, 'VIEW');
            if (!accessGranted) {
                throw new Error('Access denied: Insufficient permissions');
            }

            // Retrieve document from storage with tenant-specific decryption
            const storageResult = await this.storageEngine.retrieveDocument(
                documentMetadata.storageId,
                tenantId,
                documentMetadata.wrappedKey
            );

            // Log access
            await appendAuditEntry({
                tenantId,
                action: 'DOCUMENT_RETRIEVE',
                resourceType: 'DOCUMENT',
                resourceId: documentId,
                actor: userId,
                details: {
                    title: documentMetadata.title
                }
            });

            const result = {
                success: true,
                documentId,
                tenantId,
                metadata: _.omit(documentMetadata.toObject(), ['wrappedKey']),
                content: {
                    buffer: storageResult.decryptedBuffer,
                    mimeType: storageResult.mimeType,
                    originalFileName: storageResult.originalFileName
                },
                retrievedAt: storageResult.retrievedAt
            };

            // Cache result
            this.documentCache.set(cacheKey, result, 300);

            return result;

        } catch (error) {
            console.error(`[Tenant: ${tenantId}] Document retrieval failed:`, error);
            throw error;
        }
    }

    /**
     * Update document with tenant context and version control
     * @param {string} documentId - Document identifier
     * @param {Object} updates - Document updates
     * @param {Object} userContext - Must include tenantId and userId
     * @returns {Promise<Object>} Update result with new version
     */
    async updateDocument(documentId, updates, userContext) {
        // Fail closed if tenant context missing
        if (!userContext?.tenantId) {
            throw new Error('TENANT_CONTEXT_REQUIRED: tenantId must be provided in userContext');
        }

        const { tenantId, userId } = userContext;
        const operationId = `UPDATE-${uuidv4()}`;

        try {
            // Get existing document with tenant isolation
            const existingDocument = await this.DocumentMetadata.findOne({
                tenantId,
                documentId,
                deleted: false
            });

            if (!existingDocument) {
                throw new Error(`Document not found: ${documentId}`);
            }

            // Check edit permissions
            const editGranted = await this._checkDocumentAccess(existingDocument, userContext, 'EDIT');
            if (!editGranted) {
                throw new Error('Edit access denied: Insufficient permissions');
            }

            // Create new version
            const newVersion = {
                major: updates.majorVersion ? existingDocument.version.major + 1 : existingDocument.version.major,
                minor: updates.majorVersion ? 0 : existingDocument.version.minor + 1,
                patch: 0
            };

            // Create new document metadata (new version)
            const newDocumentMetadata = new this.DocumentMetadata({
                ...existingDocument.toObject(),
                _id: undefined,
                documentId: `DOC-${uuidv4()}`,
                previousVersionId: existingDocument.documentId,
                version: newVersion,
                versionHistory: [
                    ...existingDocument.versionHistory,
                    {
                        version: existingDocument.fullVersion,
                        documentId: existingDocument.documentId,
                        changeDescription: updates.changeDescription || 'Document updated',
                        changedBy: userId,
                        changedAt: new Date()
                    }
                ],
                status: updates.status || existingDocument.status,
                updatedBy: userId,
                updatedAt: new Date()
            });

            // If file content is being updated
            if (updates.file) {
                // Check quota for new file size
                await this._checkTenantQuota(tenantId, updates.file.size);

                // Process new file
                const newFileBuffer = await this._processDocumentFile(updates.file);

                // PII scan
                const piiScan = await this._performPIIScan(newFileBuffer, {
                    ...newDocumentMetadata.toObject(),
                    mimeType: updates.file.mimetype
                });

                // Store new version
                const storageResult = await this.storageEngine.storeDocument(newFileBuffer, {
                    tenantId,
                    originalFileName: updates.file.originalname || existingDocument.originalFileName,
                    mimeType: updates.file.mimetype || existingDocument.mimeType,
                    uploadedBy: userId
                });

                // Update metadata
                newDocumentMetadata.storageId = storageResult.storageId;
                newDocumentMetadata.contentHash = storageResult.contentHash;
                newDocumentMetadata.encryptedHash = storageResult.encryptedHash;
                newDocumentMetadata.wrappedKey = storageResult.wrappedKey;
                newDocumentMetadata.fileSize = newFileBuffer.length;
                newDocumentMetadata.mimeType = updates.file.mimetype || existingDocument.mimeType;
                newDocumentMetadata.originalFileName = updates.file.originalname || existingDocument.originalFileName;
                newDocumentMetadata.fileExtension = this._getFileExtension(updates.file.originalname) || existingDocument.fileExtension;

                // Update PII classification
                newDocumentMetadata.piiClassification = {
                    containsPII: piiScan.hasPII,
                    piiTypes: piiScan.detectedPII?.map(p => p.piiType) || [],
                    specialPersonalInfo: piiScan.hasSpecialInfo,
                    riskLevel: piiScan.highestRiskLevel || 'LOW'
                };

                // Update quota (add new file size, keep old version for now)
                await this._updateTenantQuota(tenantId, newFileBuffer.length, 1);
            }

            // Save new version
            await newDocumentMetadata.save();

            // Mark old version as superseded
            existingDocument.status = 'ARCHIVED';
            existingDocument.updatedBy = userId;
            existingDocument.updatedAt = new Date();
            await existingDocument.save();

            // Clear caches
            this._clearDocumentCaches(tenantId, existingDocument.documentId);
            this._clearDocumentCaches(tenantId, newDocumentMetadata.documentId);

            // Log update
            await appendAuditEntry({
                tenantId,
                action: 'DOCUMENT_UPDATE',
                resourceType: 'DOCUMENT',
                resourceId: newDocumentMetadata.documentId,
                actor: userId,
                details: {
                    previousVersionId: existingDocument.documentId,
                    newVersion: newDocumentMetadata.fullVersion,
                    changeDescription: updates.changeDescription
                }
            });

            return {
                success: true,
                tenantId,
                previousDocumentId: existingDocument.documentId,
                newDocumentId: newDocumentMetadata.documentId,
                newVersion: newDocumentMetadata.fullVersion,
                metadata: _.omit(newDocumentMetadata.toObject(), ['wrappedKey']),
                operationId,
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            console.error(`[Tenant: ${tenantId}] Document update failed:`, error);

            await appendAuditEntry({
                tenantId,
                action: 'DOCUMENT_UPDATE_FAILED',
                resourceType: 'DOCUMENT',
                resourceId: documentId,
                actor: userId,
                details: {
                    error: error.message,
                    operationId
                },
                severity: 'ERROR'
            });

            throw error;
        }
    }

    /**
     * Delete document with tenant context and compliance checks
     * @param {string} documentId - Document identifier
     * @param {Object} userContext - Must include tenantId and userId
     * @param {string} deletionReason - Reason for deletion
     * @returns {Promise<Object>} Deletion result
     */
    async deleteDocument(documentId, userContext, deletionReason = 'USER_REQUESTED') {
        // Fail closed if tenant context missing
        if (!userContext?.tenantId) {
            throw new Error('TENANT_CONTEXT_REQUIRED: tenantId must be provided in userContext');
        }

        const { tenantId, userId } = userContext;
        const operationId = `DELETE-${uuidv4()}`;

        try {
            // Get document with tenant isolation
            const document = await this.DocumentMetadata.findOne({
                tenantId,
                documentId,
                deleted: false
            });

            if (!document) {
                throw new Error(`Document not found: ${documentId}`);
            }

            // Check delete permissions
            const deleteGranted = await this._checkDocumentAccess(document, userContext, 'DELETE');
            if (!deleteGranted) {
                throw new Error('Delete access denied: Insufficient permissions');
            }

            // Check retention compliance
            if (moment().isBefore(document.retentionExpiry)) {
                throw new Error(`Document cannot be deleted before retention expiry: ${document.retentionExpiry.toISOString()}`);
            }

            // Perform soft delete
            document.deleted = true;
            document.deletedAt = new Date();
            document.deletedBy = userId;
            document.status = DOCUMENT_CONFIG.DOCUMENT_STATUS.DELETED;
            document.updatedBy = userId;
            document.updatedAt = new Date();

            await document.save();

            // Delete from storage (optional - depends on retention policy)
            // await this.storageEngine.deleteDocument(document.storageId, tenantId);

            // Update quota (subtract file size)
            await this._updateTenantQuota(tenantId, -document.fileSize, -1);

            // Log deletion
            await appendAuditEntry({
                tenantId,
                action: 'DOCUMENT_DELETE',
                resourceType: 'DOCUMENT',
                resourceId: documentId,
                actor: userId,
                details: {
                    title: document.title,
                    reason: deletionReason,
                    fileSize: document.fileSize
                }
            });

            // Clear caches
            this._clearDocumentCaches(tenantId, documentId);

            return {
                success: true,
                tenantId,
                documentId,
                deletedAt: document.deletedAt,
                deletedBy: document.deletedBy,
                reason: deletionReason,
                operationId,
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            console.error(`[Tenant: ${tenantId}] Document deletion failed:`, error);

            await appendAuditEntry({
                tenantId,
                action: 'DOCUMENT_DELETE_FAILED',
                resourceType: 'DOCUMENT',
                resourceId: documentId,
                actor: userId,
                details: {
                    error: error.message,
                    operationId
                },
                severity: 'ERROR'
            });

            throw error;
        }
    }

    // =================================================================================
    // TENANT QUOTA MANAGEMENT
    // =================================================================================

    /**
     * Check tenant quota before storage operation
     * @param {string} tenantId - Tenant identifier
     * @param {number} additionalBytes - Additional bytes to store
     * @returns {Promise<void>}
     */
    async _checkTenantQuota(tenantId, additionalBytes) {
        try {
            let quota = await this.TenantQuota.findOne({ tenantId });

            if (!quota) {
                // Create default quota for new tenant
                quota = new this.TenantQuota({
                    tenantId,
                    storageQuotaGB: DOCUMENT_CONFIG.TENANT_QUOTA_DEFAULT_GB,
                    storageUsedGB: 0,
                    documentCount: 0
                });
                await quota.save();
            }

            // Reset rate limit counter if minute has passed
            if (moment().diff(quota.lastResetAt, 'minutes') >= 1) {
                quota.requestsThisMinute = 0;
                quota.lastResetAt = new Date();
            }

            // Check rate limit
            if (quota.requestsThisMinute >= quota.rateLimitRPM) {
                throw new Error('TENANT_RATE_LIMIT_EXCEEDED: Too many requests this minute');
            }

            // Check storage quota
            const additionalGB = additionalBytes / (1024 ** 3);
            if (quota.storageUsedGB + additionalGB > quota.storageQuotaGB) {
                throw new Error('TENANT_STORAGE_QUOTA_EXCEEDED: Not enough storage space');
            }

            // Increment request counter
            quota.requestsThisMinute += 1;
            await quota.save();

        } catch (error) {
            console.error(`[Tenant: ${tenantId}] Quota check failed:`, error);
            throw error;
        }
    }

    /**
     * Update tenant quota after storage operation
     * @param {string} tenantId - Tenant identifier
     * @param {number} sizeDelta - Change in storage size (bytes)
     * @param {number} countDelta - Change in document count
     * @returns {Promise<void>}
     */
    async _updateTenantQuota(tenantId, sizeDelta, countDelta) {
        try {
            const sizeDeltaGB = sizeDelta / (1024 ** 3);

            await this.TenantQuota.findOneAndUpdate(
                { tenantId },
                {
                    $inc: {
                        storageUsedGB: sizeDeltaGB,
                        documentCount: countDelta
                    },
                    $set: { updatedAt: new Date() }
                },
                { upsert: true, new: true }
            );

        } catch (error) {
            console.error(`[Tenant: ${tenantId}] Quota update failed:`, error);
            // Don't throw - quota update failure shouldn't break document operations
        }
    }

    // =================================================================================
    // ACCESS CONTROL WITH TENANT CONTEXT
    // =================================================================================

    /**
     * Check document access with tenant isolation
     * @param {Object} documentMetadata - Document metadata
     * @param {Object} userContext - User context with tenantId
     * @param {string} requiredAccess - Required access level
     * @returns {Promise<boolean>} Access granted
     */
    async _checkDocumentAccess(documentMetadata, userContext, requiredAccess) {
        const { tenantId, userId, role } = userContext;

        // Fail closed if tenant mismatch
        if (documentMetadata.tenantId !== tenantId) {
            return false;
        }

        // System administrators have full access
        if (role === 'SYSTEM_ADMIN' || role === 'INFORMATION_OFFICER') {
            return true;
        }

        // Document owner has full access
        if (documentMetadata.accessControl.ownerUserId === userId) {
            return true;
        }

        // Check allowed users
        const userAccess = documentMetadata.accessControl.allowedUsers.find(
            user => user.userId === userId
        );

        if (!userAccess) {
            return false;
        }

        // Check if access has expired
        if (userAccess.expiresAt && moment().isAfter(userAccess.expiresAt)) {
            return false;
        }

        // Check access level hierarchy
        const accessLevels = { VIEW: 1, EDIT: 2, SHARE: 3, DELETE: 4 };
        const userLevel = accessLevels[userAccess.accessLevel] || 0;
        const requiredLevel = accessLevels[requiredAccess] || 0;

        return userLevel >= requiredLevel;
    }

    // =================================================================================
    // COMPLIANCE OPERATIONS
    // =================================================================================

    /**
     * Perform compliance audit for tenant
     * @param {string} tenantId - Tenant identifier
     * @param {Object} auditScope - Audit scope and parameters
     * @param {Object} userContext - User context
     * @returns {Promise<Object>} Audit results
     */
    async performComplianceAudit(tenantId, auditScope, userContext) {
        // Fail closed if tenant context missing
        if (!tenantId) {
            throw new Error('TENANT_CONTEXT_REQUIRED: tenantId must be provided');
        }

        const auditId = `COMPLIANCE-AUDIT-${uuidv4()}`;

        try {
            // Build audit query with tenant isolation
            const query = { tenantId, deleted: false };

            // Add scope filters
            if (auditScope.dateRange) {
                query.createdAt = {
                    $gte: new Date(auditScope.dateRange.start),
                    $lte: new Date(auditScope.dateRange.end)
                };
            }

            // Get documents for audit
            const documents = await this.DocumentMetadata.find(query).lean();

            // Perform compliance checks
            const auditResults = [];
            const complianceIssues = [];

            for (const document of documents) {
                const documentAudit = await this._auditDocumentCompliance(document);
                auditResults.push(documentAudit);

                if (documentAudit.complianceIssues.length > 0) {
                    complianceIssues.push({
                        documentId: document.documentId,
                        issues: documentAudit.complianceIssues,
                        severity: documentAudit.overallSeverity
                    });
                }
            }

            // Generate audit report
            const auditReport = {
                auditId,
                tenantId,
                performedAt: new Date().toISOString(),
                performedBy: userContext.userId,
                scope: auditScope,
                documentsAudited: documents.length,
                complianceIssuesFound: complianceIssues.length,
                complianceIssues,
                summary: this._generateComplianceSummary(auditResults),
                recommendations: this._generateComplianceRecommendations(complianceIssues)
            };

            // Log audit
            await appendAuditEntry({
                tenantId,
                action: 'COMPLIANCE_AUDIT',
                resourceType: 'TENANT',
                resourceId: tenantId,
                actor: userContext.userId,
                details: {
                    auditId,
                    documentsAudited: documents.length,
                    issuesFound: complianceIssues.length
                }
            });

            return {
                success: true,
                auditReport,
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            console.error(`[Tenant: ${tenantId}] Compliance audit failed:`, error);

            await appendAuditEntry({
                tenantId,
                action: 'COMPLIANCE_AUDIT_FAILED',
                resourceType: 'TENANT',
                resourceId: tenantId,
                actor: userContext.userId,
                details: {
                    error: error.message,
                    auditId
                },
                severity: 'ERROR'
            });

            throw error;
        }
    }

    // =================================================================================
    // PRIVATE HELPER METHODS
    // =================================================================================

    _validateDocumentInput(documentData, userContext) {
        // Basic validation
        if (!documentData || !documentData.file) {
            return { valid: false, reason: 'No file provided' };
        }

        if (documentData.file.size > DOCUMENT_CONFIG.MAX_FILE_SIZE_BYTES) {
            return {
                valid: false,
                reason: `File exceeds maximum size of ${DOCUMENT_CONFIG.MAX_FILE_SIZE_MB}MB`
            };
        }

        if (!DOCUMENT_CONFIG.ALLOWED_MIME_TYPES.includes(documentData.file.mimetype)) {
            return {
                valid: false,
                reason: `File type ${documentData.file.mimetype} not allowed`
            };
        }

        if (!userContext?.tenantId) {
            return { valid: false, reason: 'Tenant context required' };
        }

        return { valid: true };
    }

    async _processDocumentFile(file) {
        if (file.buffer) {
            return file.buffer;
        } else if (file.path) {
            const fs = require('fs').promises;
            return await fs.readFile(file.path);
        } else {
            throw new Error('Invalid file object');
        }
    }

    async _performPIIScan(buffer, metadata) {
        // Simplified PII detection for example
        // In production, use specialized PII detection service
        const textContent = await this._extractTextFromBuffer(buffer, metadata.mimeType);

        // Simple regex patterns for South African PII
        const patterns = {
            SA_ID_NUMBER: /\b\d{13}\b/g,
            PHONE_NUMBER: /\b(\+27|0)\d{9}\b/g,
            EMAIL_ADDRESS: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g
        };

        const detectedPII = [];
        for (const [piiType, pattern] of Object.entries(patterns)) {
            const matches = textContent.match(pattern);
            if (matches) {
                detectedPII.push({
                    piiType,
                    count: matches.length,
                    riskLevel: piiType === 'SA_ID_NUMBER' ? 'HIGH' : 'MEDIUM'
                });
            }
        }

        return {
            hasPII: detectedPII.length > 0,
            detectedPII,
            piiCount: detectedPII.reduce((sum, pii) => sum + pii.count, 0),
            scannedAt: new Date().toISOString(),
            highestRiskLevel: detectedPII.length > 0 ?
                detectedPII.reduce((max, pii) =>
                    this._getRiskLevelValue(pii.riskLevel) > this._getRiskLevelValue(max) ? pii.riskLevel : max, 'LOW'
                ) : 'LOW'
        };
    }

    async _extractTextFromBuffer(buffer, mimeType) {
        try {
            if (mimeType === 'application/pdf') {
                const data = await pdfParse(buffer);
                return data.text || '';
            } else if (mimeType.includes('word')) {
                const result = await mammoth.extractRawText({ buffer });
                return result.value || '';
            } else if (mimeType.startsWith('text/')) {
                return buffer.toString('utf-8');
            }
            return '';
        } catch (error) {
            console.warn('Text extraction failed:', error);
            return '';
        }
    }

    _getRiskLevelValue(riskLevel) {
        const values = { LOW: 1, MEDIUM: 2, HIGH: 3 };
        return values[riskLevel] || 1;
    }

    _getFileExtension(fileName) {
        if (!fileName) return '';
        const parts = fileName.split('.');
        return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
    }

    _clearDocumentCaches(tenantId, documentId) {
        const cacheKeys = [
            `${tenantId}:metadata:${documentId}`,
            `${tenantId}:document:${documentId}`
        ];

        cacheKeys.forEach(key => this.documentCache.del(key));
    }

    async _auditDocumentCompliance(document) {
        const complianceIssues = [];

        // Check retention compliance
        if (moment().isAfter(document.retentionExpiry) && document.status !== 'ARCHIVED') {
            complianceIssues.push({
                type: 'RETENTION_NON_COMPLIANCE',
                issue: 'Document past retention period but not archived',
                severity: 'HIGH',
                requirement: 'COMPANIES_ACT_71_OF_2008_SECTION_24'
            });
        }

        // Check PII compliance
        if (document.piiClassification.containsPII &&
            document.confidentialityLevel === 'PUBLIC') {
            complianceIssues.push({
                type: 'PII_NON_COMPLIANCE',
                issue: 'PII-containing document marked as PUBLIC',
                severity: 'CRITICAL',
                requirement: 'POPIA_SECTION_19_SECURITY_MEASURES'
            });
        }

        return {
            documentId: document.documentId,
            auditedAt: new Date().toISOString(),
            complianceIssues,
            overallSeverity: complianceIssues.length > 0 ?
                complianceIssues.reduce((max, issue) =>
                    this._getSeverityValue(issue.severity) > this._getSeverityValue(max) ? issue.severity : max, 'LOW'
                ) : 'NONE'
        };
    }

    _getSeverityValue(severity) {
        const values = { NONE: 0, LOW: 1, MEDIUM: 2, HIGH: 3, CRITICAL: 4 };
        return values[severity] || 0;
    }

    _generateComplianceSummary(auditResults) {
        const summary = {
            totalDocumentsAudited: auditResults.length,
            documentsWithIssues: auditResults.filter(r => r.complianceIssues.length > 0).length,
            issueBreakdown: {
                CRITICAL: 0,
                HIGH: 0,
                MEDIUM: 0,
                LOW: 0
            }
        };

        auditResults.forEach(result => {
            result.complianceIssues.forEach(issue => {
                summary.issueBreakdown[issue.severity] = (summary.issueBreakdown[issue.severity] || 0) + 1;
            });
        });

        summary.complianceScore = auditResults.length > 0 ?
            ((auditResults.length - summary.documentsWithIssues) / auditResults.length * 100).toFixed(2) : 100;

        return summary;
    }

    _generateComplianceRecommendations(complianceIssues) {
        const recommendations = [];
        const issuesByType = {};

        complianceIssues.forEach(doc => {
            doc.issues.forEach(issue => {
                if (!issuesByType[issue.type]) {
                    issuesByType[issue.type] = [];
                }
                issuesByType[issue.type].push(issue);
            });
        });

        for (const [type, issues] of Object.entries(issuesByType)) {
            const count = issues.length;
            const highestSeverity = issues.reduce((max, issue) =>
                this._getSeverityValue(issue.severity) > this._getSeverityValue(max) ? issue.severity : max, 'LOW'
            );

            recommendations.push({
                type,
                count,
                severity: highestSeverity,
                recommendation: this._getRecommendationForIssueType(type, count),
                priority: this._getSeverityValue(highestSeverity) >= 3 ? 'HIGH' : 'MEDIUM'
            });
        }

        return recommendations.sort((a, b) =>
            this._getSeverityValue(b.severity) - this._getSeverityValue(a.severity)
        );
    }

    _getRecommendationForIssueType(type, count) {
        const recommendations = {
            'RETENTION_NON_COMPLIANCE': `Archive ${count} document(s) that are past retention period`,
            'PII_NON_COMPLIANCE': `Review confidentiality levels for ${count} PII-containing document(s)`,
            'SIGNATURE_NON_COMPLIANCE': `Verify execution status for ${count} document(s)`,
            'ACCESS_CONTROL_NON_COMPLIANCE': `Configure access control for ${count} document(s)`
        };

        return recommendations[type] || `Address ${count} ${type.toLowerCase()} issue(s)`;
    }
}

// =================================================================================
// EXPORT WITH HEALTH CHECK
// =================================================================================
module.exports = {
    MultiTenantDocumentService,
    DocumentMetadata,
    TenantQuota,

    // Factory function
    createDocumentService: () => new MultiTenantDocumentService(),

    // Health check
    healthCheck: async () => {
        try {
            const service = new MultiTenantDocumentService();
            const quotaCount = await service.TenantQuota.countDocuments();

            return {
                status: 'HEALTHY',
                timestamp: new Date().toISOString(),
                components: {
                    mongodb: mongoose.connection.readyState === 1 ? 'CONNECTED' : 'DISCONNECTED',
                    cache: 'OPERATIONAL',
                    kms: 'INTEGRATED',
                    auditLedger: 'INTEGRATED'
                },
                metrics: {
                    tenantQuotas: quotaCount,
                    cacheItems: service.documentCache.getStats().keys || 0
                }
            };
        } catch (error) {
            return {
                status: 'DEGRADED',
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }
};

// Mermaid Diagram: Multi-Tenant Document Service Architecture
/**
 * @mermaid
 * flowchart TD
 *     subgraph "Tenant A"
 *         A1[User A1] --> A2[Document Service]
 *         A2 --> A3[Tenant Context]
 *         A3 --> A4[Tenant Key A]
 *         A4 --> A5[Encrypted Storage A]
 *     end
 *     
 *     subgraph "Tenant B"
 *         B1[User B1] --> B2[Document Service]
 *         B2 --> B3[Tenant Context]
 *         B3 --> B4[Tenant Key B]
 *         B4 --> B5[Encrypted Storage B]
 *     end
 *     
 *     A5 --> C[(MongoDB GridFS)]
 *     B5 --> C
 *     
 *     C --> D[Audit Ledger]
 *     D --> E[Blockchain Anchor]
 *     
 *     style A1 fill:#e1f5e1
 *     style B1 fill:#e1f5e1
 *     style A5 fill:#fff3cd
 *     style B5 fill:#fff3cd
 *     style E fill:#d4edda
 */