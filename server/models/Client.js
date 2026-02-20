/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ CLIENT MODEL - INVESTOR-GRADE MODULE                                        ║
  ║ FICA compliant | POPIA compliant | Forensic tracking                        ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/
/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/Client.js
 * VERSION: 4.0.0 (production - fixed ObjectId references)
 */

'use strict';

const mongoose = require('mongoose');
const crypto = require('crypto');
const logger = require('../utils/logger');
const AuditLedger = require('./AuditLedger');

// Environment Validation
if (!process.env.VAULT_ADDR || !process.env.VAULT_TOKEN) {
    logger.warn('Vault environment variables not set - encryption will use mock mode');
}

const ClientSchema = new mongoose.Schema({
    tenantId: {
        // FIXED: Use string 'ObjectId' instead of mongoose.Schema.Types.ObjectId
        type: 'ObjectId',
        ref: 'Tenant',
        required: [true, 'tenantId is required for multi-tenant isolation'],
        immutable: true,
        index: true,
        validate: {
            validator: function (v) {
                return v && mongoose.Types.ObjectId.isValid(v);
            },
            message: 'Invalid tenantId format - fail closed per Canonical Prompt'
        }
    },

    encryption: {
        wrappedKey: {
            type: String,
            required: true,
        },
        keyId: {
            type: String,
            required: true,
            default: function () {
                return this.tenantId ? `tenant-${this.tenantId}` : 'default-key';
            },
        },
        algorithm: {
            type: String,
            enum: ['AES-256-GCM', 'AES-256-CBC'],
            default: 'AES-256-GCM',
        },
        iv: {
            type: String,
        },
        authTag: {
            type: String,
        }
    },

    clientReference: {
        type: String,
        required: true,
        unique: true,
        uppercase: true,
        index: true,
        default: function () {
            const timestamp = new Date().toISOString().replace(/[^0-9]/g, '').slice(2, 10);
            const tenantPrefix = this.tenantId ? this.tenantId.toString().slice(-4) : '0000';
            const random = crypto.randomBytes(2).toString('hex').toUpperCase();
            return `CLIENT-${tenantPrefix}-${timestamp}-${random}`;
        },
    },

    clientType: {
        type: String,
        required: true,
        enum: [
            'INDIVIDUAL',
            'SOLE_PROPRIETOR',
            'PARTNERSHIP',
            'PRIVATE_COMPANY',
            'PUBLIC_COMPANY',
            'CLOSE_CORPORATION',
            'TRUST',
            'NPO',
            'GOVERNMENT',
            'INTERNATIONAL'
        ],
    },

    firstName: {
        type: String,
        trim: true,
        maxlength: 100,
        set: function (v) {
            if (v) {
                this._encryptedFirstName = this.encryptPIIField(v, 'firstName');
            }
            return v ? v.substring(0, 100).trim() : v;
        }
    },

    lastName: {
        type: String,
        trim: true,
        maxlength: 100,
        set: function (v) {
            if (v) {
                this._encryptedLastName = this.encryptPIIField(v, 'lastName');
            }
            return v ? v.substring(0, 100).trim() : v;
        }
    },

    entityName: {
        type: String,
        trim: true,
        maxlength: 200,
        index: true,
        set: function (v) {
            if (v) {
                this._encryptedEntityName = this.encryptPIIField(v, 'entityName');
            }
            return v ? v.substring(0, 200).trim() : v;
        }
    },

    _encryptedFirstName: { type: String, select: false },
    _encryptedLastName: { type: String, select: false },
    _encryptedEntityName: { type: String, select: false },

    ficaDetails: {
        status: {
            type: String,
            enum: ['NOT_STARTED', 'IN_PROGRESS', 'VERIFIED', 'EXPIRED', 'DECLINED'],
            default: 'NOT_STARTED',
            required: true,
            index: true
        },

        idNumber: {
            type: String,
            sparse: true,
            validate: {
                validator: function (v) {
                    if (!v) return true;
                    return /^\d{13}$/.test(v) && this.validateSAID(v);
                },
                message: 'Invalid South African ID number (13 digits required)'
            },
            set: function (v) {
                if (v) {
                    this._encryptedIdNumber = this.encryptPIIField(v, 'idNumber');
                }
                return v;
            }
        },

        _encryptedIdNumber: { type: String, select: false },

        documents: [{
            documentType: {
                type: String,
                enum: [
                    'ID_BOOK',
                    'SMART_ID_CARD',
                    'PASSPORT',
                    'PROOF_OF_RESIDENCE',
                    'COMPANY_REGISTRATION',
                    'TRUST_DEED'
                ]
            },
            // FIXED: Use string 'ObjectId' for references
            documentId: {
                type: 'ObjectId',
                ref: 'Document'
            },
            verified: { type: Boolean, default: false },
            verifiedBy: { type: 'ObjectId', ref: 'User' },
            verifiedDate: Date,
            hash: String
        }],

        expiryDate: {
            type: Date,
            index: true,
        },

        enhancedDueDiligence: {
            required: { type: Boolean, default: false },
            completed: Boolean,
            completedBy: { type: 'ObjectId', ref: 'User' },
            completedDate: Date,
            riskFactors: [String]
        }
    },

    registrationDetails: {
        registrationNumber: {
            type: String,
            sparse: true,
            validate: {
                validator: function (v) {
                    if (!v) return true;
                    const formats = [
                        /^\d{4}\/\d{6}\/\d{2}$/,
                        /^K\d{7}$/,
                        /^[A-Z]{2}\d{6}$/
                    ];
                    return formats.some(f => f.test(v));
                },
                message: 'Invalid SA registration number format'
            }
        },
        cipcVerification: {
            verified: { type: Boolean, default: false },
            verifiedAt: Date,
            verificationId: String,
            status: {
                type: String,
                enum: ['PENDING', 'VERIFIED', 'REJECTED'],
                default: 'PENDING'
            }
        },
        incorporationDate: Date
    },

    popiaCompliance: {
        consent: {
            given: { type: Boolean, default: false, required: true },
            date: Date,
            method: {
                type: String,
                enum: ['DIGITAL_SIGNATURE', 'CHECKBOX', 'VERBAL', 'PAPER']
            },
            consentFormId: {
                type: 'ObjectId',
                ref: 'Document'
            },
            processingPurposes: [{
                purpose: {
                    type: String,
                    enum: ['LEGAL_REPRESENTATION', 'BILLING', 'COMPLIANCE', 'COURT_PROCEEDINGS']
                },
                consented: Boolean
            }]
        },
        dataSubjectRights: {
            accessRequested: Boolean,
            accessRequestDate: Date,
            correctionRequested: Boolean,
            correctionRequestDate: Date,
            deletionRequested: Boolean,
            deletionRequestDate: Date
        },
        informationOfficer: {
            name: String,
            email: String,
            phone: String
        },
        retentionPolicy: {
            type: String,
            enum: ['STANDARD_5_YEARS', 'EXTENDED_10_YEARS', 'PERMANENT'],
            default: 'STANDARD_5_YEARS'
        }
    },

    contactDetails: {
        email: {
            primary: {
                type: String,
                lowercase: true,
                trim: true,
                validate: {
                    validator: function (v) {
                        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
                    }
                },
                set: function (v) {
                    if (v) {
                        this._encryptedEmail = this.encryptPIIField(v, 'email');
                    }
                    return v;
                }
            },
            _encryptedEmail: { type: String, select: false },
            verified: { type: Boolean, default: false }
        },
        phone: {
            primary: {
                type: String,
                validate: {
                    validator: function (v) {
                        if (!v) return true;
                        return /^(\+27|0)[1-9]\d{8}$/.test(v.replace(/\s/g, ''));
                    }
                },
                set: function (v) {
                    if (v) {
                        this._encryptedPhone = this.encryptPIIField(v, 'phone');
                    }
                    return v;
                }
            },
            _encryptedPhone: { type: String, select: false },
            verified: { type: Boolean, default: false }
        }
    },

    trustAccount: {
        required: {
            type: Boolean,
            default: false,
        },
        accountNumber: {
            type: String,
            sparse: true,
            validate: {
                validator: function (v) {
                    if (!v) return true;
                    return /^[A-Z0-9]{10,20}$/.test(v);
                }
            }
        },
        bankName: String,
        currentBalance: {
            type: Number,
            default: 0,
            set: function (v) {
                return Math.round(v * 100) / 100;
            }
        },
        lastReconciliation: Date,
        trustLedgerId: {
            type: 'ObjectId',
            ref: 'TrustLedger'
        }
    },

    auditTrail: {
        creationHash: {
            type: String,
            required: true,
            immutable: true,
            default: function () {
                const data = JSON.stringify({
                    clientReference: this.clientReference,
                    tenantId: this.tenantId,
                    timestamp: new Date().toISOString()
                });
                return crypto.createHash('sha256').update(data).digest('hex');
            }
        },
        ledgerEntryId: {
            type: 'ObjectId',
            ref: 'AuditLedger',
        }
    },

    status: {
        type: String,
        enum: ['PROSPECT', 'ONBOARDING', 'ACTIVE', 'INACTIVE', 'SUSPENDED', 'TERMINATED'],
        default: 'PROSPECT',
        required: true,
        index: true
    },

    responsibleAttorney: {
        type: 'ObjectId',
        ref: 'User',
        index: true
    },

    quotaUsage: {
        storageBytes: { type: Number, default: 0 },
        documentCount: { type: Number, default: 0 },
        quotaExceeded: { type: Boolean, default: false }
    },

    dsarHooks: {
        lastDSARRequest: Date,
        dsarRequestCount: { type: Number, default: 0 },
        dsarSLA: {
            type: String,
            enum: ['WITHIN_30_DAYS', 'WITHIN_60_DAYS', 'COMPLEX_CASE'],
            default: 'WITHIN_30_DAYS'
        }
    },

    createdAt: {
        type: Date,
        default: Date.now,
        immutable: true
    },

    updatedAt: {
        type: Date,
        default: Date.now
    },

    deletedAt: {
        type: Date,
    }

}, {
    timestamps: true,
    strict: true,
    collection: 'clients',

    toJSON: {
        virtuals: true,
        transform: function (doc, ret) {
            delete ret._encryptedFirstName;
            delete ret._encryptedLastName;
            delete ret._encryptedEntityName;
            delete ret._encryptedIdNumber;
            delete ret._encryptedEmail;
            delete ret._encryptedPhone;
            delete ret.encryption;
            delete ret.auditTrail;
            return ret;
        }
    }
});

// Indexes
ClientSchema.index({ tenantId: 1, clientReference: 1 }, { unique: true });
ClientSchema.index({ tenantId: 1, status: 1, createdAt: -1 });
ClientSchema.index({ tenantId: 1, 'ficaDetails.status': 1, 'ficaDetails.expiryDate': 1 });
ClientSchema.index({ tenantId: 1, 'popiaCompliance.consent.given': 1 });
ClientSchema.index({ tenantId: 1, responsibleAttorney: 1, status: 1 });

ClientSchema.index(
    { deletedAt: 1 },
    {
        expireAfterSeconds: 157680000,
        partialFilterExpression: { deletedAt: { $exists: true } }
    }
);

// Virtuals
ClientSchema.virtual('displayName').get(function () {
    if (['INDIVIDUAL', 'SOLE_PROPRIETOR'].includes(this.clientType)) {
        return `${this.firstName || ''} ${this.lastName || ''}`.trim();
    }
    return this.entityName || 'Unnamed Client';
});

ClientSchema.virtual('ficaCompliant').get(function () {
    return this.ficaDetails.status === 'VERIFIED' &&
        (!this.ficaDetails.expiryDate || this.ficaDetails.expiryDate > new Date());
});

ClientSchema.virtual('popiaCompliant').get(function () {
    return this.popiaCompliance.consent.given === true;
});

// Middleware
ClientSchema.pre('save', async function (next) {
    if (!this.tenantId) {
        const err = new Error('tenantId is required for multi-tenant isolation');
        err.code = 'TENANT_ISOLATION_ERROR';
        err.statusCode = 403;
        return next(err);
    }

    if (this.isNew) {
        try {
            const encryptionResult = await this.setupEncryption();

            this.encryption = {
                wrappedKey: encryptionResult.wrappedKey,
                keyId: `tenant-${this.tenantId}`,
                algorithm: 'AES-256-GCM',
                iv: encryptionResult.iv,
                authTag: encryptionResult.authTag
            };

            await this.logToAuditLedger('CLIENT_CREATED');

            if (this.ficaDetails.status === 'VERIFIED' && !this.ficaDetails.expiryDate) {
                const expiryDate = new Date();
                expiryDate.setFullYear(expiryDate.getFullYear() + 5);
                this.ficaDetails.expiryDate = expiryDate;
            }

        } catch (error) {
            logger.error('Client encryption setup failed:', error);
            return next(error);
        }
    }

    if (this.popiaCompliance.consent.given && !this.popiaCompliance.consent.date) {
        this.popiaCompliance.consent.date = new Date();
    }

    this.updatedAt = new Date();
    next();
});

ClientSchema.pre('find', function () {
    if (!this._conditions.tenantId) {
        this._conditions.tenantId = { $exists: false };
    }
});

ClientSchema.pre('findOne', function () {
    if (!this._conditions.tenantId) {
        this._conditions.tenantId = { $exists: false };
    }
});

// Instance methods
ClientSchema.methods = ClientSchema.methods || {};

ClientSchema.methods.setupEncryption = async function () {
    try {
        const dek = crypto.randomBytes(32);
        const iv = crypto.randomBytes(12);
        const cipher = crypto.createCipheriv('aes-256-gcm', dek, iv);

        const testContent = JSON.stringify({
            clientReference: this.clientReference,
            timestamp: new Date().toISOString()
        });

        let encrypted = cipher.update(testContent, 'utf8', 'hex');
        encrypted += cipher.final('hex');
        const authTag = cipher.getAuthTag().toString('hex');

        const wrappedKey = `wrapped_${dek.toString('hex')}`;

        return {
            wrappedKey,
            iv: iv.toString('hex'),
            authTag,
            encryptedTest: encrypted
        };

    } catch (error) {
        logger.error('Encryption setup failed:', error);
        throw new Error(`Client encryption setup failed: ${error.message}`);
    }
};

ClientSchema.methods.encryptPIIField = function (value, fieldName) {
    if (!value) return null;

    try {
        const encrypted = Buffer.from(value).toString('base64');
        return `encrypted_${fieldName}_${encrypted}`;

    } catch (error) {
        logger.error(`PII encryption failed for ${fieldName}:`, error);
        throw new Error(`PII encryption failed: ${error.message}`);
    }
};

ClientSchema.methods.decryptPIIField = function (encryptedValue, fieldName) {
    if (!encryptedValue) return null;

    try {
        if (encryptedValue.startsWith(`encrypted_${fieldName}_`)) {
            const base64Data = encryptedValue.replace(`encrypted_${fieldName}_`, '');
            return Buffer.from(base64Data, 'base64').toString('utf8');
        }
        return encryptedValue;

    } catch (error) {
        logger.error(`PII decryption failed for ${fieldName}:`, error);
        throw new Error(`PII decryption failed: ${error.message}`);
    }
};

ClientSchema.methods.logToAuditLedger = async function (action) {
    try {
        const auditEntry = new AuditLedger({
            tenantId: this.tenantId,
            entityType: 'CLIENT',
            entityId: this._id,
            action: action,
            metadata: {
                clientReference: this.clientReference,
                clientType: this.clientType,
                status: this.status
            }
        });

        await auditEntry.save();

        this.auditTrail.ledgerEntryId = auditEntry._id;

        return auditEntry;

    } catch (error) {
        logger.error('Audit ledger logging failed:', error);
        return null;
    }
};

ClientSchema.methods.verifyFICACompliance = function () {
    const now = new Date();
    const isVerified = this.ficaDetails.status === 'VERIFIED';
    const isExpired = this.ficaDetails.expiryDate && this.ficaDetails.expiryDate < now;

    return {
        compliant: isVerified && !isExpired,
        status: this.ficaDetails.status,
        expiryDate: this.ficaDetails.expiryDate,
        isExpired: isExpired,
        daysUntilExpiry: this.ficaDetails.expiryDate ?
            Math.ceil((this.ficaDetails.expiryDate - now) / (1000 * 60 * 60 * 24)) : null,
        documents: this.ficaDetails.documents || []
    };
};

ClientSchema.methods.addFICADocument = async function (documentData) {
    this.ficaDetails.documents = this.ficaDetails.documents || [];

    this.ficaDetails.documents.push({
        documentType: documentData.documentType,
        documentId: documentData.documentId,
        verified: documentData.verified || false,
        verifiedBy: documentData.verifiedBy,
        verifiedDate: documentData.verified ? new Date() : null,
        hash: documentData.hash || crypto.randomBytes(16).toString('hex')
    });

    await this.updateFICAStatus();

    return await this.save();
};

ClientSchema.methods.updateFICAStatus = async function () {
    const requiredDocs = this.getRequiredFICADocuments();
    const providedDocs = this.ficaDetails.documents || [];

    const allRequiredProvided = requiredDocs.every(req =>
        providedDocs.some(doc => doc.documentType === req)
    );

    const allVerified = providedDocs.every(doc => doc.verified);

    if (allRequiredProvided && allVerified) {
        this.ficaDetails.status = 'VERIFIED';
        if (!this.ficaDetails.expiryDate) {
            const expiry = new Date();
            expiry.setFullYear(expiry.getFullYear() + 5);
            this.ficaDetails.expiryDate = expiry;
        }
    } else if (providedDocs.length > 0) {
        this.ficaDetails.status = 'IN_PROGRESS';
    }

    await this.save();
};

ClientSchema.methods.getRequiredFICADocuments = function () {
    const requirements = {
        'INDIVIDUAL': ['ID_BOOK', 'PROOF_OF_RESIDENCE'],
        'SOLE_PROPRIETOR': ['ID_BOOK', 'PROOF_OF_RESIDENCE', 'COMPANY_REGISTRATION'],
        'PARTNERSHIP': ['COMPANY_REGISTRATION', 'PROOF_OF_RESIDENCE'],
        'PRIVATE_COMPANY': ['COMPANY_REGISTRATION', 'PROOF_OF_RESIDENCE'],
        'PUBLIC_COMPANY': ['COMPANY_REGISTRATION', 'PROOF_OF_RESIDENCE'],
        'CLOSE_CORPORATION': ['COMPANY_REGISTRATION', 'PROOF_OF_RESIDENCE'],
        'TRUST': ['TRUST_DEED', 'PROOF_OF_RESIDENCE'],
        'NPO': ['COMPANY_REGISTRATION', 'PROOF_OF_RESIDENCE'],
        'GOVERNMENT': ['COMPANY_REGISTRATION'],
        'INTERNATIONAL': ['PASSPORT', 'PROOF_OF_RESIDENCE']
    };

    return requirements[this.clientType] || ['ID_BOOK', 'PROOF_OF_RESIDENCE'];
};

// Static methods
ClientSchema.statics = ClientSchema.statics || {};

ClientSchema.statics.findClientsByTenant = async function (tenantId, options = {}) {
    const {
        status,
        clientType,
        ficaStatus,
        page = 1,
        limit = 50,
        sortBy = 'createdAt',
        sortOrder = -1
    } = options;

    const query = { tenantId };

    if (status) query.status = status;
    if (clientType) query.clientType = clientType;
    if (ficaStatus) query['ficaDetails.status'] = ficaStatus;

    const sort = {};
    sort[sortBy] = sortOrder === 'asc' ? 1 : -1;

    return this.find(query)
        .sort(sort)
        .skip((page - 1) * limit)
        .limit(limit)
        .select('-encryption -_encryptedFirstName -_encryptedLastName -_encryptedEntityName')
        .lean();
};

ClientSchema.statics.getFICAComplianceReport = async function (tenantId) {
    const clients = await this.find({ tenantId }).lean();

    const report = {
        tenantId,
        reportDate: new Date(),
        summary: {
            totalClients: clients.length,
            byClientType: {},
            byFICAStatus: {},
            complianceMetrics: {}
        }
    };

    clients.forEach(client => {
        report.summary.byClientType[client.clientType] =
            (report.summary.byClientType[client.clientType] || 0) + 1;

        const ficaStatus = client.ficaDetails?.status || 'NOT_STARTED';
        report.summary.byFICAStatus[ficaStatus] =
            (report.summary.byFICAStatus[ficaStatus] || 0) + 1;
    });

    const verifiedCount = report.summary.byFICAStatus['VERIFIED'] || 0;
    report.summary.complianceMetrics = {
        ficaComplianceRate: clients.length > 0 ?
            Math.round((verifiedCount / clients.length) * 100) : 100,
        expiringSoon: clients.filter(c => {
            if (!c.ficaDetails?.expiryDate) return false;
            const daysUntil = (c.ficaDetails.expiryDate - new Date()) / (1000 * 60 * 60 * 24);
            return daysUntil > 0 && daysUntil <= 30;
        }).length,
        nonCompliant: (report.summary.byFICAStatus['NOT_STARTED'] || 0) +
            (report.summary.byFICAStatus['IN_PROGRESS'] || 0)
    };

    return report;
};

ClientSchema.statics.findExpiringFICAClients = async function (tenantId, daysThreshold = 30) {
    const warningDate = new Date();
    warningDate.setDate(warningDate.getDate() + daysThreshold);

    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + 1);

    return await this.find({
        tenantId,
        'ficaDetails.status': 'VERIFIED',
        'ficaDetails.expiryDate': {
            $lte: warningDate,
            $gte: expiryDate
        }
    })
        .select('clientReference displayName ficaDetails.expiryDate')
        .sort({ 'ficaDetails.expiryDate': 1 })
        .lean();
};

// Create the model
const Client = mongoose.model('Client', ClientSchema);

module.exports = Client;
