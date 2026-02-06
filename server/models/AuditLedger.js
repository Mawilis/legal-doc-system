/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  █████  ██    ██ ██████  ██ ████████     ██       ███████ ██████  ███████  ■
■ ██   ██ ██    ██ ██   ██ ██    ██        ██       ██      ██   ██ ██       ■
■ ███████ ██    ██ ██   ██ ██    ██        ██       █████   ██   ██ ███████  ■
■ ██   ██ ██    ██ ██   ██ ██    ██        ██       ██      ██   ██      ██  ■
■ ██   ██  ██████  ██████  ██    ██        ████████ ███████ ██████  ███████  ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
Purpose: Immutable append-only audit ledger schema with multi-tenant isolation
ASCII Flow: [Audit Event] -> [Schema Validation] -> [Encryption] -> [MongoDB] -> [OTS Anchor]
Compliance: POPIA §18 / ECT §16 / Companies Act §24 / PAIA §14 / FICA §21C
FILENAME: AuditLedger.js
Chief Architect: Wilson Khanyezi (wilsy.wk@gmail.com | +27 69 046 5710)
ROI: Legal defensibility, DSAR compliance, regulatory audit readiness
═══════════════════════════════════════════════════════════════════════════════
*/

/**
 * Wilsy OS - Immutable Audit Ledger Model
 * @module models/AuditLedger
 * @description Mongoose schema for append-only audit trail with cryptographic
 * integrity, multi-tenant isolation, and OpenTimestamps anchoring.
 * @compliance POPIA §18 (accountability), ECT Act §16 (admissibility),
 * Companies Act §24 (7-year retention), PAIA §14 (access logging),
 * FICA §21C (record keeping)
 * @security Tier A - Immutable audit records for legal defensibility
 * @multiTenant Tenant isolation via compound indexes and context validation
 */

var mongoose = require('mongoose');
var Schema = mongoose.Schema;
var crypto = require('crypto');

// ==============================================
// AUDIT LEDGER SCHEMA DEFINITION
// ==============================================

var AuditLedgerSchema = new Schema({
    // === TENANT ISOLATION (FAIL-CLOSED ENFORCEMENT) ===
    tenantId: {
        type: String,
        required: [true, 'AUDIT_LEDGER: Tenant ID required for multi-tenant isolation'],
        index: true,
        validate: {
            validator: function (v) {
                return /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/.test(v) ||
                    /^tenant_[a-zA-Z0-9]{8,32}$/.test(v);
            },
            message: 'AUDIT_LEDGER: Invalid tenant ID format - must be UUID or tenant_ prefix'
        }
    },

    // === USER CONTEXT & ACCOUNTABILITY ===
    userId: {
        type: Schema.Types.ObjectId,
        required: [true, 'AUDIT_LEDGER: User ID required for audit accountability'],
        ref: 'User',
        index: true
    },

    userRole: {
        type: String,
        required: true,
        enum: [
            'super_admin',
            'tenant_admin',
            'legal_practitioner',
            'paralegal',
            'compliance_officer',
            'information_officer',
            'auditor',
            'client',
            'system_auto'
        ],
        default: 'client'
    },

    // === AUDIT ACTION & RESOURCE (COMPLIANCE HOOKS) ===
    action: {
        type: String,
        required: true,
        enum: [
            'CREATE',
            'READ',
            'UPDATE',
            'DELETE',
            'EXPORT',
            'SHARE',
            'SIGN',
            'DSAR_REQUEST',
            'DSAR_FULFILL',
            'CONSENT_GRANT',
            'CONSENT_REVOKE',
            'LOGIN',
            'LOGOUT',
            'FAILED_ACCESS',
            'RETENTION_DISPOSAL',
            'ANCHOR_TO_OTS',
            'PAIA_REQUEST',
            'FICA_VERIFICATION'
        ],
        index: true
    },

    resourceType: {
        type: String,
        required: true,
        enum: [
            'DOCUMENT',
            'USER',
            'TENANT',
            'CONSENT',
            'DSAR_REQUEST',
            'AUDIT_LOG',
            'COMPLIANCE_RULE',
            'WORKFLOW',
            'TEMPLATE',
            'SIGNATURE',
            'PAYMENT',
            'KYC_RECORD',
            'TRUST_ACCOUNT'
        ],
        index: true
    },

    resourceId: {
        type: Schema.Types.ObjectId,
        required: true,
        refPath: 'resourceType',
        index: true
    },

    // === CHANGE DATA (ENCRYPTED FOR POPIA SENSITIVE DATA) ===
    changes: {
        type: Schema.Types.Mixed,
        default: null,
        validate: {
            validator: function (v) {
                // Changes must be null or object with before/after structure
                if (v === null) return true;
                if (typeof v !== 'object' || Array.isArray(v)) return false;

                // Enforce structure for auditability
                var hasBefore = 'before' in v;
                var hasAfter = 'after' in v;
                var hasDelta = 'delta' in v;

                return hasBefore || hasAfter || hasDelta;
            },
            message: 'AUDIT_LEDGER: Changes must be null or object with before/after/delta fields'
        }
    },

    // === ENCRYPTED CHANGES (FOR POPIA PERSONAL INFORMATION) ===
    encryptedChanges: {
        iv: { type: String, default: null },
        encryptedData: { type: String, default: null },
        authTag: { type: String, default: null },
        encryptionKeyId: { type: String, default: null } // Vault key version
    },

    wrappedKey: {
        type: String,
        default: null,
        validate: {
            validator: function (v) {
                // If encryptedChanges exist, wrappedKey must exist
                if (this.encryptedChanges && this.encryptedChanges.encryptedData) {
                    return v !== null && /^vault:v[0-9]+:[a-f0-9]+$/.test(v);
                }
                return true;
            },
            message: 'AUDIT_LEDGER: Wrapped key required when encryptedChanges present (format: vault:v#:hex)'
        }
    },

    // === CRYPTOGRAPHIC INTEGRITY (ECT ACT NON-REPUDIATION) ===
    integrityHash: {
        type: String,
        required: [true, 'AUDIT_LEDGER: Integrity hash required for cryptographic proof'],
        validate: {
            validator: function (v) {
                return /^[a-f0-9]{64}$/.test(v);
            },
            message: 'AUDIT_LEDGER: Integrity hash must be 64-character SHA256 hex'
        },
        index: true
    },

    chainHash: {
        type: String,
        default: null,
        validate: {
            validator: function (v) {
                return v === null || /^[a-f0-9]{64}$/.test(v);
            },
            message: 'AUDIT_LEDGER: Chain hash must be null or 64-character SHA256 hex'
        }
    },

    otsReceipt: {
        type: String,
        default: null,
        validate: {
            validator: function (v) {
                return v === null || /^[A-Za-z0-9+/]+={0,2}$/.test(v);
            },
            message: 'AUDIT_LEDGER: OTS receipt must be base64 encoded'
        }
    },

    anchoredAt: {
        type: Date,
        default: null,
        index: true
    },

    // === COMPLIANCE METADATA (POPIA/PAIA/FICA) ===
    metadata: {
        timestamp: {
            type: Date,
            required: true,
            default: Date.now,
            index: true,
            validate: {
                validator: function (v) {
                    return v <= new Date() && v >= new Date('2020-01-01');
                },
                message: 'AUDIT_LEDGER: Timestamp must be valid date between 2020 and now'
            }
        },

        ipAddress: {
            type: String,
            required: false,
            validate: {
                validator: function (v) {
                    return v === null ||
                        /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(v) ||
                        /^([a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}$/.test(v);
                },
                message: 'AUDIT_LEDGER: Invalid IP address format (IPv4 or IPv6)'
            }
        },

        userAgent: {
            type: String,
            maxlength: [512, 'AUDIT_LEDGER: User agent max length 512 characters'],
            default: null
        },

        geolocation: {
            country: { type: String, default: 'ZA' },
            region: { type: String, default: null },
            city: { type: String, default: null },
            coordinates: {
                type: { type: String, enum: ['Point'], default: null },
                coordinates: { type: [Number], default: null }
            }
        },

        deviceFingerprint: {
            type: String,
            maxlength: [256, 'AUDIT_LEDGER: Device fingerprint max length 256 characters'],
            default: null
        },

        sessionId: {
            type: String,
            validate: {
                validator: function (v) {
                    return v === null || /^[a-f0-9]{32}$/.test(v);
                },
                message: 'AUDIT_LEDGER: Session ID must be 32-character hex string'
            },
            default: null
        },

        correlationId: {
            type: String,
            index: true,
            validate: {
                validator: function (v) {
                    return /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/.test(v);
                },
                message: 'AUDIT_LEDGER: Correlation ID must be UUID v4'
            },
            default: null
        },

        // === POPIA INFORMATION OFFICER METADATA ===
        informationOfficer: {
            name: { type: String, default: null },
            email: { type: String, default: null },
            phone: { type: String, default: null }
        },

        // === PAIA ACCESS REQUEST METADATA ===
        paiaRequestId: {
            type: Schema.Types.ObjectId,
            ref: 'PAIARequest',
            default: null
        },

        // === FICA COMPLIANCE MARKERS ===
        ficaVerified: { type: Boolean, default: false },
        ficaVerificationLevel: {
            type: String,
            enum: ['BASIC', 'ENHANCED', 'ONGOING', null],
            default: null
        }
    },

    // === INDEXED FIELDS FOR PERFORMANCE (MULTI-TENANT OPTIMIZED) ===
    indexedFields: {
        tenantId: {
            type: String,
            required: true,
            index: true
        },
        action: {
            type: String,
            required: true,
            index: true
        },
        resourceType: {
            type: String,
            required: true,
            index: true
        },
        resourceId: {
            type: String,
            required: true,
            index: true
        },
        date: {
            type: String,
            required: true,
            index: true,
            validate: {
                validator: function (v) {
                    return /^\d{4}-\d{2}-\d{2}$/.test(v);
                },
                message: 'AUDIT_LEDGER: Date must be YYYY-MM-DD format'
            }
        },
        hour: {
            type: String,
            required: true,
            index: true,
            validate: {
                validator: function (v) {
                    return /^\d{4}-\d{2}-\d{2}T\d{2}$/.test(v);
                },
                message: 'AUDIT_LEDGER: Hour must be YYYY-MM-DDTHH format'
            }
        }
    },

    // === RETENTION & DISPOSAL (COMPANIES ACT COMPLIANCE) ===
    retentionPolicy: {
        type: String,
        required: true,
        enum: ['STANDARD_7_YEARS', 'CLIENT_DATA_5_YEARS', 'FINANCIAL_10_YEARS', 'PERMANENT', 'DSAR_HOLD'],
        default: 'STANDARD_7_YEARS'
    },

    scheduledDisposalDate: {
        type: Date,
        required: true,
        default: function () {
            var retentionYears = {
                'STANDARD_7_YEARS': 7,
                'CLIENT_DATA_5_YEARS': 5,
                'FINANCIAL_10_YEARS': 10,
                'PERMANENT': 100,
                'DSAR_HOLD': 1
            };
            var years = retentionYears[this.retentionPolicy];
            var date = new Date();
            date.setFullYear(date.getFullYear() + years);
            return date;
        },
        index: true
    },

    disposalCertificate: {
        disposedAt: { type: Date, default: null },
        disposedBy: { type: Schema.Types.ObjectId, ref: 'User', default: null },
        method: {
            type: String,
            enum: ['SECURE_DELETION', 'ANONYMIZATION', 'ARCHIVAL', null],
            default: null
        },
        certificateHash: {
            type: String,
            default: null,
            validate: {
                validator: function (v) {
                    return v === null || /^[a-f0-9]{64}$/.test(v);
                },
                message: 'AUDIT_LEDGER: Certificate hash must be 64-character SHA256 hex'
            }
        },
        verifiedBy: { type: Schema.Types.ObjectId, ref: 'User', default: null },
        verificationTimestamp: { type: Date, default: null }
    },

    // === QUOTA & THROTTLING TRACKING ===
    quotaImpact: {
        storageBytes: { type: Number, default: 0, min: 0 },
        apiCalls: { type: Number, default: 1, min: 0 },
        computeUnits: { type: Number, default: 0.1, min: 0 }
    },

    // === DATA RESIDENCY (POPIA TIER A/B DATA) ===
    dataResidency: {
        country: { type: String, default: 'ZA', required: true },
        region: { type: String, default: 'af-south-1' },
        compliant: { type: Boolean, default: true },
        verifiedAt: { type: Date, default: null }
    }
}, {
    // === SCHEMA OPTIONS ===
    timestamps: {
        createdAt: 'createdAt',
        updatedAt: 'updatedAt'
    },
    collection: 'audit_ledger',
    strict: true,

    // === JSON SERIALIZATION (REMOVE SENSITIVE FIELDS) ===
    toJSON: {
        virtuals: true,
        transform: function (doc, ret) {
            // Remove sensitive/encrypted fields from default JSON output
            delete ret.encryptedChanges;
            delete ret.wrappedKey;
            delete ret.chainHash;
            delete ret.otsReceipt;
            delete ret.quotaImpact;
            delete ret.__v;
            delete ret._id;

            // Convert ObjectId to string
            if (ret.userId && ret.userId._id) ret.userId = ret.userId._id.toString();
            if (ret.resourceId && ret.resourceId._id) ret.resourceId = ret.resourceId._id.toString();

            return ret;
        }
    },

    toObject: {
        virtuals: true,
        transform: function (doc, ret) {
            delete ret.__v;
            return ret;
        }
    }
});

// ==============================================
// VIRTUAL FIELDS & METHODS
// ==============================================

/**
 * Virtual field: Is entry cryptographically anchored?
 * @returns {Boolean} True if OTS receipt exists
 */
AuditLedgerSchema.virtual('isAnchored').get(function () {
    return !!(this.otsReceipt && this.anchoredAt);
});

/**
 * Virtual field: Are changes encrypted?
 * @returns {Boolean} True if encryptedChanges exist
 */
AuditLedgerSchema.virtual('hasEncryptedChanges').get(function () {
    return !!(this.encryptedChanges && this.encryptedChanges.encryptedData);
});

/**
 * Virtual field: Is entry disposed?
 * @returns {Boolean} True if disposal certificate exists
 */
AuditLedgerSchema.virtual('isDisposed').get(function () {
    return !!(this.disposalCertificate && this.disposalCertificate.disposedAt);
});

/**
 * Get human-readable audit description
 * @returns {String} Description of audit event
 */
AuditLedgerSchema.methods.getAuditDescription = function () {
    return this.userRole + ' (' + this.userId + ') ' + this.action + ' on ' + this.resourceType + ' at ' + this.metadata.timestamp.toISOString();
};

/**
 * Check if entry is eligible for disposal
 * @returns {Boolean} True if past scheduled disposal date
 */
AuditLedgerSchema.methods.isEligibleForDisposal = function () {
    if (this.retentionPolicy === 'PERMANENT') return false;
    if (this.isDisposed) return false;
    return this.scheduledDisposalDate <= new Date();
};

/**
 * Generate integrity hash for entry (for verification)
 * @returns {String} SHA256 hash of audit data
 */
AuditLedgerSchema.methods.generateIntegrityHash = function () {
    var hashData = {
        tenantId: this.tenantId,
        userId: this.userId,
        userRole: this.userRole,
        action: this.action,
        resourceType: this.resourceType,
        resourceId: this.resourceId,
        changes: this.changes,
        metadata: this.metadata,
        timestamp: this.metadata.timestamp.getTime()
    };

    return crypto
        .createHash('sha256')
        .update(JSON.stringify(hashData))
        .digest('hex');
};

// ==============================================
// STATIC METHODS (TENANT-ISOLATED QUERIES)
// ==============================================

/**
 * Find all audit entries for a tenant within date range
 * @static
 * @param {String} tenantId - Tenant identifier (required)
 * @param {Date} startDate - Start date (inclusive)
 * @param {Date} endDate - End date (inclusive)
 * @param {Object} options - Pagination options
 * @returns {Query} Mongoose query
 * @throws {Error} If tenantId not provided
 */
AuditLedgerSchema.statics.findByTenantAndDateRange = function (tenantId, startDate, endDate, options) {
    if (!options) options = {};

    if (!tenantId) {
        throw new Error('AUDIT_LEDGER: Tenant ID required for tenant-isolated query');
    }

    var page = options.page || 1;
    var limit = options.limit || 100;
    var startStr = startDate.toISOString().split('T')[0];
    var endStr = endDate.toISOString().split('T')[0];

    return this.find({
        'indexedFields.tenantId': tenantId,
        'indexedFields.date': { $gte: startStr, $lte: endStr }
    })
        .sort({ 'metadata.timestamp': -1 })
        .skip((page - 1) * limit)
        .limit(limit);
};

/**
 * Count audit entries by action for a tenant (for analytics)
 * @static
 * @param {String} tenantId - Tenant identifier
 * @returns {Promise} Aggregation result
 */
AuditLedgerSchema.statics.getActionCounts = function (tenantId) {
    return this.aggregate([
        { $match: { 'indexedFields.tenantId': tenantId } },
        { $group: { _id: '$action', count: { $sum: 1 } } },
        { $sort: { count: -1 } }
    ]);
};

/**
 * Find entries pending OTS anchoring
 * @static
 * @param {String} tenantId - Tenant identifier (optional)
 * @returns {Query} Mongoose query
 */
AuditLedgerSchema.statics.findPendingAnchoring = function (tenantId) {
    var query = { otsReceipt: null, anchoredAt: null };
    if (tenantId) {
        query['indexedFields.tenantId'] = tenantId;
    }
    return this.find(query)
        .limit(100)
        .sort({ 'metadata.timestamp': 1 });
};

/**
 * Get entries eligible for disposal
 * @static
 * @param {String} tenantId - Tenant identifier (optional)
 * @returns {Query} Mongoose query
 */
AuditLedgerSchema.statics.findEligibleForDisposal = function (tenantId) {
    var query = {
        'disposalCertificate.disposedAt': null,
        scheduledDisposalDate: { $lte: new Date() }
    };

    if (tenantId) {
        query['indexedFields.tenantId'] = tenantId;
    }

    return this.find(query)
        .limit(50)
        .sort({ scheduledDisposalDate: 1 });
};

// ==============================================
// MIDDLEWARE (HOOKS) - IMMUTABILITY ENFORCEMENT
// ==============================================

/**
 * Pre-save hook: Ensure immutability and set indexed fields
 */
AuditLedgerSchema.pre('save', function (next) {
    // === FAIL-CLOSED: PREVENT UPDATES TO EXISTING ENTRIES ===
    if (this.isModified() && !this.isNew) {
        var error = new Error('AUDIT_LEDGER: Modification prohibited - audit trail is immutable');
        error.code = 'AUDIT_IMMUTABLE';
        error.statusCode = 403;
        return next(error);
    }

    // === SET INDEXED FIELDS FOR PERFORMANCE ===
    if (this.isNew) {
        var timestamp = this.metadata.timestamp || new Date();
        var dateStr = timestamp.toISOString().split('T')[0];
        var hourStr = dateStr + 'T' + timestamp.getHours().toString().padStart(2, '0');

        this.indexedFields = {
            tenantId: this.tenantId,
            action: this.action,
            resourceType: this.resourceType,
            resourceId: this.resourceId.toString(),
            date: dateStr,
            hour: hourStr
        };

        // === GENERATE INTEGRITY HASH IF NOT PROVIDED ===
        if (!this.integrityHash) {
            this.integrityHash = this.generateIntegrityHash();
        }

        // === SET DATA RESIDENCY (DEFAULT SOUTH AFRICA) ===
        if (!this.dataResidency || !this.dataResidency.country) {
            this.dataResidency = {
                country: 'ZA',
                region: 'af-south-1',
                compliant: true,
                verifiedAt: new Date()
            };
        }
    }

    next();
});

/**
 * Pre-remove hook: Prevent deletion
 */
AuditLedgerSchema.pre('remove', function (next) {
    var error = new Error('AUDIT_LEDGER: Deletion prohibited - audit trail is immutable');
    error.code = 'AUDIT_IMMUTABLE';
    error.statusCode = 403;
    next(error);
});

/**
 * Pre-update hooks: Prevent any modifications
 */
AuditLedgerSchema.pre('findOneAndUpdate', function (next) {
    var error = new Error('AUDIT_LEDGER: Updates prohibited - audit trail is immutable');
    error.code = 'AUDIT_IMMUTABLE';
    error.statusCode = 403;
    next(error);
});

AuditLedgerSchema.pre('updateOne', function (next) {
    var error = new Error('AUDIT_LEDGER: Updates prohibited - audit trail is immutable');
    error.code = 'AUDIT_IMMUTABLE';
    error.statusCode = 403;
    next(error);
});

AuditLedgerSchema.pre('updateMany', function (next) {
    var error = new Error('AUDIT_LEDGER: Updates prohibited - audit trail is immutable');
    error.code = 'AUDIT_IMMUTABLE';
    error.statusCode = 403;
    next(error);
});

// ==============================================
// COMPOUND INDEXES (MULTI-TENANT PERFORMANCE)
// ==============================================

AuditLedgerSchema.index({ tenantId: 1, 'metadata.timestamp': -1 });
AuditLedgerSchema.index({ 'indexedFields.tenantId': 1, 'indexedFields.date': 1 });
AuditLedgerSchema.index({ 'indexedFields.tenantId': 1, 'indexedFields.action': 1 });
AuditLedgerSchema.index({ 'indexedFields.tenantId': 1, 'indexedFields.resourceType': 1 });
AuditLedgerSchema.index({ 'indexedFields.tenantId': 1, 'indexedFields.resourceId': 1 });
AuditLedgerSchema.index({ resourceId: 1, 'metadata.timestamp': -1 });
AuditLedgerSchema.index({ userId: 1, 'metadata.timestamp': -1 });
AuditLedgerSchema.index({ 'metadata.correlationId': 1 });
AuditLedgerSchema.index({ scheduledDisposalDate: 1 });
AuditLedgerSchema.index({ anchoredAt: 1 });
AuditLedgerSchema.index({ 'metadata.geolocation.coordinates': '2dsphere' });
AuditLedgerSchema.index({ 'dataResidency.country': 1, 'metadata.timestamp': -1 });
AuditLedgerSchema.index({ integrityHash: 1 }, { unique: true });

// ==============================================
// MODEL EXPORT
// ==============================================

// Create model with error handling for duplicate model registration
var AuditLedger;
try {
    AuditLedger = mongoose.model('AuditLedger');
} catch (error) {
    AuditLedger = mongoose.model('AuditLedger', AuditLedgerSchema);
}

module.exports = AuditLedger;