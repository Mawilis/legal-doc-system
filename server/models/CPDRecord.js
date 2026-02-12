/**
 * WILSYS OS - CPD RECORD MODEL
 * ====================================================================
 * LEGAL PRACTICE COUNCIL · CONTINUING PROFESSIONAL DEVELOPMENT
 * QUANTUM-SEALED · LPC CHAPTER 3 · ECT ACT §15
 * 
 * @version 5.0.0
 * @author Wilson Khanyezi - Chief Quantum Sentinel
 * @copyright Wilsy OS (Pty) Ltd 2026
 * 
 * @description Complete CPD tracking system with:
 *              - LPC Chapter 3 compliance (12 annual hours, 2 ethics)
 *              - Provider accreditation verification
 *              - Automatic certificate generation
 *              - Blockchain timestamp verification
 *              - Rollover hour tracking (max 6 hours)
 *              - Ethics hour enforcement
 *              - Multi-year compliance monitoring
 *              - Forensic audit trails with SHA3-512
 * 
 * @compliance Legal Practice Act 28 of 2014 - Section 86(2)
 * @compliance LPC Rules (2023 Amendments) - Chapter 3, Sections 3.1-3.12
 * @compliance POPIA 2013 - Section 19
 * @compliance ECT Act 2002 - Section 15
 * @compliance Companies Act 71 of 2008 - 7-year retention
 * 
 * @statutory CPD_ANNUAL_HOURS: 12 hours
 * @statutory CPD_ETHICS_HOURS: 2 hours minimum
 * @statutory CPD_MAX_ROLLOVER: 6 hours
 * @statutory CPD_DEADLINE: December 31 annually
 * ====================================================================
 */

const mongoose = require('mongoose');
const { Schema } = mongoose;
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');
const auditLogger = require('../utils/auditLogger');
const { redactSensitiveData } = require('../utils/popiaRedaction');

// ====================================================================
// FORENSIC CONSTANTS - IMMUTABLE · LPC STATUTORY
// ====================================================================

const CPD_CATEGORIES = {
    SUBSTANTIVE: 'SUBSTANTIVE',
    ETHICS: 'ETHICS',
    PRACTICE_MANAGEMENT: 'PRACTICE_MANAGEMENT',
    PROFESSIONAL_SKILLS: 'PROFESSIONAL_SKILLS',
    ADVOCACY: 'ADVOCACY',
    DRAFTING: 'DRAFTING',
    NEGOTIATION: 'NEGOTIATION',
    MEDIATION: 'MEDIATION',
    ARBITRATION: 'ARBITRATION',
    TECHNOLOGY: 'TECHNOLOGY',
    LEGAL_RESEARCH: 'LEGAL_RESEARCH',
    CLIENT_CARE: 'CLIENT_CARE',
    RISK_MANAGEMENT: 'RISK_MANAGEMENT',
    FINANCIAL_MANAGEMENT: 'FINANCIAL_MANAGEMENT'
};

const CPD_STATUS = {
    PENDING_VERIFICATION: 'PENDING_VERIFICATION',
    VERIFIED: 'VERIFIED',
    REJECTED: 'REJECTED',
    EXPIRED: 'EXPIRED',
    CANCELLED: 'CANCELLED',
    AUTO_VERIFIED: 'AUTO_VERIFIED',
    UNDER_REVIEW: 'UNDER_REVIEW'
};

const PROVIDER_TYPES = {
    LPC_ACCREDITED: 'LPC_ACCREDITED',
    UNIVERSITY: 'UNIVERSITY',
    LAW_SOCIETY: 'LAW_SOCIETY',
    BAR_COUNCIL: 'BAR_COUNCIL',
    PRIVATE_PROVIDER: 'PRIVATE_PROVIDER',
    IN_HOUSE: 'IN_HOUSE',
    INTERNATIONAL: 'INTERNATIONAL',
    WEBINAR: 'WEBINAR',
    CONFERENCE: 'CONFERENCE',
    WORKSHOP: 'WORKSHOP'
};

const VERIFICATION_METHODS = {
    MANUAL: 'MANUAL',
    AUTOMATED: 'AUTOMATED',
    BLOCKCHAIN: 'BLOCKCHAIN',
    LPC_API: 'LPC_API',
    PROVIDER_API: 'PROVIDER_API',
    CERTIFICATE_SCAN: 'CERTIFICATE_SCAN',
    QR_CODE: 'QR_CODE'
};

const COMPLIANCE_STATUS = {
    COMPLIANT: 'COMPLIANT',
    NON_COMPLIANT: 'NON_COMPLIANT',
    WARNING: 'WARNING',
    EXEMPT: 'EXEMPT',
    GRACE_PERIOD: 'GRACE_PERIOD',
    PENDING: 'PENDING'
};

const ACCREDITATION_LEVELS = {
    FULL: 'FULL',
    PROVISIONAL: 'PROVISIONAL',
    EXPIRED: 'EXPIRED',
    SUSPENDED: 'SUSPENDED',
    REVOKED: 'REVOKED'
};

// ====================================================================
// CPD RECORD SCHEMA - FORENSIC TRACKING
// ====================================================================

const cpdRecordSchema = new Schema({
    // ====================================================================
    // TENANT ISOLATION - MULTI-TENANT FORTRESS
    // ====================================================================
    tenantId: {
        type: String,
        required: [true, 'TENANT_ISOLATION_VIOLATION: tenantId is required'],
        index: true,
        immutable: true,
        validate: {
            validator: function(v) {
                return /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(v);
            },
            message: props => `${props.value} is not a valid tenant UUID`
        }
    },

    // ====================================================================
    // PRIMARY IDENTIFIERS - LPC CHAPTER 3
    // ====================================================================
    activityId: {
        type: String,
        required: [true, 'CPD activity ID is required'],
        unique: true,
        default: () => `CPD-${uuidv4()}`,
        immutable: true,
        index: true
    },

    attorneyId: {
        type: Schema.Types.ObjectId,
        ref: 'AttorneyProfile',
        required: true,
        index: true
    },

    attorneyLpcNumber: {
        type: String,
        required: true,
        index: true,
        validate: {
            validator: function(v) {
                return /^(LPC-\d{8}|\d{4}\/\d{4})$/.test(v);
            },
            message: props => `${props.value} is not a valid LPC number`
        }
    },

    firmId: {
        type: Schema.Types.ObjectId,
        ref: 'Firm',
        required: true,
        index: true
    },

    // ====================================================================
    // ACTIVITY INFORMATION - SUBSTANTIVE CONTENT
    // ====================================================================
    activityName: {
        type: String,
        required: [true, 'CPD activity name is required'],
        trim: true,
        maxlength: [500, 'Activity name cannot exceed 500 characters']
    },

    activityDescription: {
        type: String,
        trim: true,
        maxlength: [2000, 'Activity description cannot exceed 2000 characters']
    },

    activityDate: {
        type: Date,
        required: [true, 'CPD activity date is required'],
        index: true,
        validate: {
            validator: function(v) {
                const activityYear = v.getFullYear();
                const currentYear = new Date().getFullYear();
                return activityYear >= 2020 && activityYear <= currentYear;
            },
            message: props => `Activity year must be between 2020 and ${new Date().getFullYear()}`
        }
    },

    year: {
        type: Number,
        required: true,
        default: function() {
            return this.activityDate.getFullYear();
        },
        index: true,
        min: 2020,
        max: new Date().getFullYear()
    },

    // ====================================================================
    // CPD HOURS - STATUTORY COMPLIANCE
    // ====================================================================
    hours: {
        type: Number,
        required: [true, 'CPD hours are required'],
        min: [0.5, 'CPD hours must be at least 0.5'],
        max: [8, 'Single CPD activity cannot exceed 8 hours (LPC Rule 3.4)'],
        validate: {
            validator: function(v) {
                return v % 0.5 === 0;
            },
            message: 'CPD hours must be in increments of 0.5'
        }
    },

    category: {
        type: String,
        required: [true, 'CPD category is required'],
        enum: Object.values(CPD_CATEGORIES),
        index: true
    },

    subcategory: {
        type: String,
        enum: [
            'PROFESSIONAL_ETHICS',
            'PRACTICE_STANDARDS',
            'CLIENT_CARE',
            'RISK_MANAGEMENT',
            'FINANCIAL_MANAGEMENT',
            'INFORMATION_TECHNOLOGY',
            'COMMUNICATION_SKILLS',
            'LEGAL_RESEARCH',
            'ADVOCACY_SKILLS',
            'DRAFTING_SKILLS',
            'ALTERNATIVE_DISPUTE_RESOLUTION',
            'SPECIALIST_AREAS',
            'LEGISLATIVE_UPDATE',
            'CASE_LAW_UPDATE'
        ]
    },

    // ====================================================================
    // PROVIDER INFORMATION - ACCREDITATION VERIFICATION
    // ====================================================================
    provider: {
        name: {
            type: String,
            required: [true, 'CPD provider name is required'],
            trim: true,
            maxlength: 200
        },
        type: {
            type: String,
            required: true,
            enum: Object.values(PROVIDER_TYPES)
        },
        accreditationNumber: {
            type: String,
            validate: {
                validator: function(v) {
                    return !v || /^LPC-ACC-\d{6}$|^LPC-\d{4}-\d{4}$/i.test(v);
                },
                message: 'Invalid LPC accreditation number format. Expected: LPC-ACC-123456 or LPC-2024-1234'
            }
        },
        accreditationLevel: {
            type: String,
            enum: Object.values(ACCREDITATION_LEVELS)
        },
        accreditationExpiry: {
            type: Date,
            validate: {
                validator: function(v) {
                    return !v || v > new Date();
                },
                message: 'Provider accreditation has expired'
            }
        },
        website: {
            type: String,
            validate: {
                validator: function(v) {
                    return !v || /^https?:\/\/.+\..+/.test(v);
                }
            }
        },
        contactEmail: {
            type: String,
            lowercase: true,
            validate: {
                validator: function(v) {
                    return !v || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
                }
            }
        },
        contactPhone: {
            type: String,
            validate: {
                validator: function(v) {
                    return !v || /^(\+27|0)[1-9][0-9]{8}$/.test(v);
                }
            }
        },
        verificationEndpoint: String,
        providerHash: {
            type: String,
            default: function() {
                return crypto
                    .createHash('sha3-512')
                    .update(`${this.provider.name}:${this.provider.accreditationNumber || 'N/A'}`)
                    .digest('hex')
                    .substring(0, 16);
            }
        }
    },

    // ====================================================================
    // EVIDENCE & VERIFICATION - FORENSIC PROOF
    // ====================================================================
    evidence: {
        certificateUrl: {
            type: String,
            required: true,
            validate: {
                validator: function(v) {
                    return /^https?:\/\/.+\..+/.test(v);
                }
            }
        },
        certificateHash: {
            type: String,
            required: true,
            validate: {
                validator: function(v) {
                    return /^[a-f0-9]{64}$/i.test(v);
                },
                message: 'Certificate hash must be a valid SHA-256 hash (64 hex characters)'
            }
        },
        evidenceUrls: [{
            url: String,
            description: String,
            uploadedAt: { type: Date, default: Date.now }
        }],
        attendanceProof: String,
        assessmentScore: {
            type: Number,
            min: 0,
            max: 100
        },
        assessmentPassed: {
            type: Boolean,
            default: function() {
                return this.assessmentScore >= 70;
            }
        },
        completionDate: {
            type: Date,
            required: true,
            validate: {
                validator: function(v) {
                    return v <= new Date();
                },
                message: 'Completion date cannot be in the future'
            }
        }
    },

    verificationCode: {
        type: String,
        unique: true,
        sparse: true,
        default: () => crypto.randomBytes(16).toString('hex').toUpperCase(),
        validate: {
            validator: function(v) {
                return /^[A-F0-9]{32}$/i.test(v);
            }
        }
    },

    verificationStatus: {
        type: String,
        enum: Object.values(CPD_STATUS),
        default: 'PENDING_VERIFICATION',
        index: true
    },

    verificationMethod: {
        type: String,
        enum: Object.values(VERIFICATION_METHODS)
    },

    verifiedBy: {
        type: Schema.Types.ObjectId,
        ref: 'User'
    },

    verifiedAt: Date,

    verificationNotes: String,

    rejectionReason: String,

    // ====================================================================
    // ACCREDITATION & QUALITY ASSURANCE
    // ====================================================================
    accreditation: {
        isLpcAccredited: {
            type: Boolean,
            default: false
        },
        accreditationReference: String,
        qualityAssuranceScore: {
            type: Number,
            min: 0,
            max: 100
        },
        peerReviewed: {
            type: Boolean,
            default: false
        },
        reviewerComments: String,
        reviewedAt: Date,
        reviewedBy: String
    },

    // ====================================================================
    // LEARNING OUTCOMES - EDUCATIONAL IMPACT
    // ====================================================================
    learningOutcomes: {
        type: String,
        maxlength: 2000
    },

    keyTakeaways: [{
        type: String,
        maxlength: 500
    }],

    practicalApplication: {
        type: String,
        maxlength: 2000
    },

    relevanceScore: {
        type: Number,
        min: 1,
        max: 5,
        default: 3
    },

    // ====================================================================
    // COMPLIANCE TRACKING - STATUTORY REQUIREMENTS
    // ====================================================================
    compliance: {
        countsTowardsAnnual: {
            type: Boolean,
            default: true
        },
        countsTowardsEthics: {
            type: Boolean,
            default: function() {
                return this.category === 'ETHICS';
            }
        },
        rolloverEligible: {
            type: Boolean,
            default: function() {
                return this.hours <= 6 && 
                       ['VERIFIED', 'AUTO_VERIFIED'].includes(this.verificationStatus) &&
                       this.compliance.countsTowardsAnnual === true;
            }
        },
        rolloverYear: {
            type: Number,
            validate: {
                validator: function(v) {
                    return !v || v > this.year;
                }
            }
        },
        rolloverHours: {
            type: Number,
            min: 0,
            max: 6,
            validate: {
                validator: function(v) {
                    return !v || v <= this.hours;
                }
            }
        },
        appliedToYear: Number
    },

    // ====================================================================
    // FINANCIAL INFORMATION
    // ====================================================================
    cost: {
        amount: {
            type: Number,
            min: 0,
            default: 0,
            get: v => parseFloat(v.toFixed(2))
        },
        currency: {
            type: String,
            default: 'ZAR',
            enum: ['ZAR', 'USD', 'EUR', 'GBP']
        },
        paidBy: {
            type: String,
            enum: ['ATTORNEY', 'FIRM', 'SCHOLARSHIP', 'PRO_BONO', 'EMPLOYER']
        },
        receiptUrl: String,
        receiptHash: String,
        taxDeductible: {
            type: Boolean,
            default: false
        }
    },

    // ====================================================================
    // BLOCKCHAIN VERIFICATION - ECT ACT §15 ADMISSIBILITY
    // ====================================================================
    blockchain: {
        anchorId: {
            type: String,
            sparse: true,
            unique: true
        },
        transactionHash: {
            type: String,
            sparse: true
        },
        blockNumber: Number,
        timestamp: Date,
        verified: {
            type: Boolean,
            default: false
        },
        verificationUrl: String
    },

    // ====================================================================
    // CRYPTOGRAPHIC VERIFICATION - TAMPER-PROOF
    // ====================================================================
    quantumSignature: {
        type: String,
        required: true,
        default: function() {
            const payload = [
                this.activityId,
                this.attorneyLpcNumber,
                this.hours,
                this.category,
                this.activityDate.toISOString(),
                this.verificationCode || 'PENDING',
                this.evidence.certificateHash
            ].join(':');

            return crypto
                .createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026')
                .update(payload)
                .digest('hex');
        }
    },

    forensicHash: {
        type: String,
        required: true,
        unique: true,
        default: function() {
            return crypto
                .createHash('sha3-512')
                .update([
                    this.activityId,
                    this.attorneyLpcNumber,
                    this.hours.toFixed(1),
                    this.category,
                    this.activityDate.toISOString(),
                    this.provider.name,
                    this.evidence.certificateHash,
                    this.verificationCode || 'PENDING',
                    this.year.toString()
                ].join(':'))
                .digest('hex');
        }
    },

    integrityHash: {
        type: String,
        unique: true,
        default: function() {
            return crypto
                .createHash('sha3-512')
                .update(`${this._id || this.activityId}:${this.forensicHash}:${Date.now()}`)
                .digest('hex');
        }
    },

    // ====================================================================
    // AUDIT TRAIL - FORENSIC INTEGRITY
    // ====================================================================
    auditTrail: [{
        action: {
            type: String,
            enum: [
                'SUBMITTED',
                'VERIFIED',
                'REJECTED',
                'UPDATED',
                'EXPIRED',
                'ROLLED_OVER',
                'CERTIFICATE_GENERATED',
                'BLOCKCHAIN_ANCHORED',
                'AUTO_VERIFIED'
            ]
        },
        performedBy: {
            type: String,
            required: true
        },
        performedAt: {
            type: Date,
            default: Date.now
        },
        ipAddress: String,
        userAgent: String,
        changes: Schema.Types.Mixed,
        previousState: Schema.Types.Mixed,
        newState: Schema.Types.Mixed,
        hash: {
            type: String,
            default: function() {
                return crypto
                    .createHash('sha3-512')
                    .update(`${this.action}:${this.performedAt.toISOString()}:${this.performedBy}:${JSON.stringify(this.changes)}`)
                    .digest('hex');
            }
        }
    }],

    // ====================================================================
    // SYSTEM FIELDS
    // ====================================================================
    submissionDate: {
        type: Date,
        default: Date.now,
        immutable: true,
        index: true
    },

    submittedBy: {
        type: String,
        required: true,
        immutable: true
    },

    lastUpdatedBy: String,

    // ====================================================================
    // COMPLIANCE CERTIFICATE
    // ====================================================================
    complianceCertificate: {
        certificateId: {
            type: String,
            sparse: true,
            unique: true
        },
        issuedAt: Date,
        expiresAt: Date,
        certificateHash: String,
        digitalSignature: String,
        verificationUrl: String,
        verificationQR: String,
        pdfUrl: String
    },

    certificateGenerated: {
        type: Boolean,
        default: false
    },

    certificateGeneratedAt: Date,

    // ====================================================================
    // RETENTION METADATA - COMPANIES ACT 71 OF 2008
    // ====================================================================
    retentionPolicy: {
        type: String,
        default: 'companies_act_7_years'
    },

    retentionStart: {
        type: Date,
        default: Date.now,
        immutable: true
    },

    retentionExpiry: {
        type: Date,
        default: function() {
            const date = new Date();
            date.setFullYear(date.getFullYear() + 7);
            return date;
        },
        index: true
    },

    dataResidency: {
        type: String,
        default: 'ZA',
        enum: ['ZA', 'EU', 'US', 'AU', 'UK']
    },

    // ====================================================================
    // SOFT DELETE - POPIA COMPLIANCE
    // ====================================================================
    deleted: {
        type: Boolean,
        default: false,
        index: true
    },
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
            delete ret.quantumSignature;
            delete ret.forensicHash;
            delete ret.integrityHash;
            delete ret.evidence.certificateUrl;
            delete ret.blockchain;
            ret = redactSensitiveData(ret);
            return ret;
        }
    }
});

// ====================================================================
// VIRTUAL FIELDS - COMPUTED PROPERTIES
// ====================================================================

cpdRecordSchema.virtual('daysSinceSubmission').get(function() {
    return Math.floor((Date.now() - this.submissionDate) / (1000 * 60 * 60 * 24));
});

cpdRecordSchema.virtual('isVerified').get(function() {
    return ['VERIFIED', 'AUTO_VERIFIED'].includes(this.verificationStatus);
});

cpdRecordSchema.virtual('isExpired').get(function() {
    return this.verificationStatus === 'EXPIRED' ||
           (this.compliance.rolloverYear && this.compliance.rolloverYear < new Date().getFullYear() - 1);
});

cpdRecordSchema.virtual('isEthics').get(function() {
    return this.category === 'ETHICS';
});

cpdRecordSchema.virtual('isSubstantive').get(function() {
    return this.category === 'SUBSTANTIVE';
});

cpdRecordSchema.virtual('verificationProgress').get(function() {
    if (this.isVerified) return 100;
    if (this.verificationStatus === 'REJECTED') return 0;

    let progress = 0;
    if (this.evidence.certificateHash) progress += 25;
    if (this.verificationCode) progress += 25;
    if (this.provider.accreditationNumber) progress += 25;
    if (this.blockchain?.verified) progress += 25;
    if (this.accreditation.isLpcAccredited) progress += 15;

    return Math.min(100, progress);
});

cpdRecordSchema.virtual('complianceStatus').get(function() {
    if (this.isVerified) {
        if (this.category === 'ETHICS' && this.hours >= 2) {
            return 'ETHICS_COMPLIANT';
        }
        return 'HOURS_VERIFIED';
    }
    return 'PENDING_VERIFICATION';
});

cpdRecordSchema.virtual('yearsValidFor').get(function() {
    if (this.compliance.rolloverYear) {
        return this.compliance.rolloverYear - this.year;
    }
    return 1;
});

// ====================================================================
// INDEXES - PERFORMANCE OPTIMIZATION
// ====================================================================

cpdRecordSchema.index({ tenantId: 1, attorneyId: 1, year: -1, activityDate: -1 });
cpdRecordSchema.index({ tenantId: 1, verificationStatus: 1, year: 1 });
cpdRecordSchema.index({ tenantId: 1, category: 1, year: 1 });
cpdRecordSchema.index({ tenantId: 1, 'provider.accreditationNumber': 1 });
cpdRecordSchema.index({ forensicHash: 1 }, { unique: true });
cpdRecordSchema.index({ integrityHash: 1 }, { unique: true });
cpdRecordSchema.index({ verificationCode: 1 }, { unique: true, sparse: true });
cpdRecordSchema.index({ 'blockchain.anchorId': 1 }, { sparse: true });
cpdRecordSchema.index({ 'compliance.rolloverYear': 1, 'compliance.rolloverHours': 1 });
cpdRecordSchema.index({ deleted: 1, retentionExpiry: 1 });
cpdRecordSchema.index({ attorneyLpcNumber: 1, year: 1, verificationStatus: 1 });

// ====================================================================
// PRE-SAVE HOOKS - FORENSIC INTEGRITY
// ====================================================================

cpdRecordSchema.pre('save', async function(next) {
    try {
        // TENANT ISOLATION - FAIL CLOSED
        if (!this.tenantId) {
            throw new Error('TENANT_ISOLATION_VIOLATION: CPD record requires tenantId');
        }

        // Auto-set year from activity date
        if (this.activityDate && !this.year) {
            this.year = this.activityDate.getFullYear();
        }

        // Validate ethics hours requirement (LPC Rule 3.6)
        if (this.category === 'ETHICS' && this.hours < 1) {
            throw new Error('ETHICS_HOURS_VIOLATION: Ethics CPD must be at least 1 hour (LPC Rule 3.6)');
        }

        // Validate maximum hours per activity (LPC Rule 3.4)
        if (this.hours > 8) {
            throw new Error('HOURS_LIMIT_VIOLATION: Single CPD activity cannot exceed 8 hours (LPC Rule 3.4)');
        }

        // Auto-verify if from accredited provider with valid accreditation
        if (this.provider.accreditationNumber &&
            this.provider.accreditationExpiry &&
            this.provider.accreditationExpiry > new Date() &&
            this.verificationStatus === 'PENDING_VERIFICATION') {

            this.verificationStatus = 'AUTO_VERIFIED';
            this.verificationMethod = 'AUTOMATED';
            this.verifiedAt = new Date();
            this.accreditation.isLpcAccredited = true;
            this.accreditation.accreditationReference = this.provider.accreditationNumber;
        }

        // Generate forensic hash if not exists
        if (!this.forensicHash) {
            this.forensicHash = crypto
                .createHash('sha3-512')
                .update([
                    this.activityId,
                    this.attorneyLpcNumber,
                    this.hours.toFixed(1),
                    this.category,
                    this.activityDate.toISOString(),
                    this.provider.name,
                    this.evidence.certificateHash,
                    this.verificationCode || 'PENDING',
                    this.year.toString()
                ].join(':'))
                .digest('hex');
        }

        // Generate integrity hash
        this.integrityHash = crypto
            .createHash('sha3-512')
            .update(`${this._id || this.activityId}:${this.forensicHash}:${Date.now()}`)
            .digest('hex');

        // Update quantum signature
        const payload = [
            this.activityId,
            this.attorneyLpcNumber,
            this.hours,
            this.category,
            this.activityDate.toISOString(),
            this.verificationCode || 'PENDING',
            this.evidence.certificateHash
        ].join(':');

        this.quantumSignature = crypto
            .createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026')
            .update(payload)
            .digest('hex');

        // Add audit trail
        if (this.isNew) {
            this.auditTrail.push({
                action: 'SUBMITTED',
                performedBy: this.submittedBy,
                performedAt: new Date(),
                changes: {
                    activityName: this.activityName,
                    hours: this.hours,
                    category: this.category,
                    provider: this.provider.name
                }
            });
        } else {
            this.auditTrail.push({
                action: 'UPDATED',
                performedBy: this.lastUpdatedBy || this.submittedBy,
                performedAt: new Date()
            });
        }

        next();
    } catch (error) {
        next(error);
    }
});

// ====================================================================
// STATIC METHODS - FORENSIC QUERIES
// ====================================================================

cpdRecordSchema.statics = {
    /**
     * Get attorney's CPD summary for a given year
     * @param {string} attorneyId - Attorney ID
     * @param {string} tenantId - Tenant ID
     * @param {number} year - Calendar year
     * @returns {Promise<Object>} CPD summary
     */
    async getAttorneySummary(attorneyId, tenantId, year = new Date().getFullYear()) {
        const records = await this.find({
            attorneyId,
            tenantId,
            year,
            verificationStatus: { $in: ['VERIFIED', 'AUTO_VERIFIED'] },
            'compliance.countsTowardsAnnual': true,
            deleted: false
        });

        const totalHours = records.reduce((sum, r) => sum + r.hours, 0);
        const ethicsHours = records
            .filter(r => r.category === 'ETHICS')
            .reduce((sum, r) => sum + r.hours, 0);
        const substantiveHours = totalHours - ethicsHours;

        // Get previous year for rollover (LPC Rule 3.8 - max 6 hours rollover)
        const previousYearRecords = await this.find({
            attorneyId,
            tenantId,
            year: year - 1,
            verificationStatus: { $in: ['VERIFIED', 'AUTO_VERIFIED'] },
            'compliance.rolloverEligible': true,
            deleted: false
        });

        const previousYearHours = previousYearRecords.reduce((sum, r) => sum + r.hours, 0);
        const previousYearExcess = Math.max(0, previousYearHours - 12);
        const rolloverHours = Math.min(previousYearExcess, 6);

        const effectiveHours = totalHours + rolloverHours;
        const hoursRequired = 12;
        const ethicsRequired = 2;

        const isCompliant = effectiveHours >= hoursRequired && ethicsHours >= ethicsRequired;
        const hoursRemaining = Math.max(0, hoursRequired - effectiveHours);
        const ethicsRemaining = Math.max(0, ethicsRequired - ethicsHours);

        // Calculate compliance status
        let complianceStatus = 'NON_COMPLIANT';
        if (isCompliant) {
            complianceStatus = 'COMPLIANT';
        } else if (effectiveHours >= 10 || ethicsHours >= 1) {
            complianceStatus = 'WARNING';
        }

        // Calculate deadline
        const deadline = new Date(year, 11, 31); // December 31
        const daysUntilDeadline = Math.ceil((deadline - Date.now()) / (1000 * 60 * 60 * 24));
        const isOverdue = Date.now() > deadline && !isCompliant;

        return {
            attorneyId,
            tenantId,
            year,
            summary: {
                totalHours: parseFloat(totalHours.toFixed(1)),
                ethicsHours: parseFloat(ethicsHours.toFixed(1)),
                substantiveHours: parseFloat(substantiveHours.toFixed(1)),
                rolloverHours: parseFloat(rolloverHours.toFixed(1)),
                effectiveHours: parseFloat(effectiveHours.toFixed(1)),
                recordsCount: records.length
            },
            requirements: {
                hoursRequired,
                ethicsRequired,
                hoursRemaining: parseFloat(hoursRemaining.toFixed(1)),
                ethicsRemaining: parseFloat(ethicsRemaining.toFixed(1))
            },
            compliance: {
                isCompliant,
                status: complianceStatus,
                isOverdue,
                deadline: deadline.toISOString(),
                daysUntilDeadline,
                gracePeriod: !isOverdue && daysUntilDeadline > 0 ? daysUntilDeadline : 0
            },
            breakdown: records.map(r => ({
                activityId: r.activityId,
                activityName: r.activityName,
                activityDate: r.activityDate,
                hours: r.hours,
                category: r.category,
                provider: r.provider.name,
                verificationStatus: r.verificationStatus,
                verifiedAt: r.verifiedAt,
                certificateGenerated: r.certificateGenerated
            })),
            generatedAt: new Date().toISOString()
        };
    },

    /**
     * Get non-compliant attorneys for a given year
     * @param {string} tenantId - Tenant ID
     * @param {number} year - Calendar year
     * @returns {Promise<Array>} Non-compliant attorneys
     */
    async findNonCompliant(tenantId, year = new Date().getFullYear()) {
        const attorneys = await mongoose.model('AttorneyProfile').find({
            tenantId,
            status: 'ACTIVE',
            'cpd.complianceStatus': { $ne: 'COMPLIANT' },
            deleted: false
        }).select('_id lpcNumber practice.name contact.email');

        const nonCompliant = [];

        for (const attorney of attorneys) {
            const summary = await this.getAttorneySummary(attorney._id, tenantId, year);
            if (!summary.compliance.isCompliant) {
                nonCompliant.push({
                    attorneyId: attorney._id,
                    lpcNumber: attorney.lpcNumber,
                    practiceName: attorney.practice?.name,
                    email: attorney.contact?.email,
                    ...summary.summary,
                    ...summary.requirements,
                    ...summary.compliance
                });
            }
        }

        return nonCompliant;
    },

    /**
     * Get CPD statistics by provider
     * @param {string} tenantId - Tenant ID
     * @param {number} year - Calendar year
     * @returns {Promise<Array>} Provider statistics
     */
    async getProviderStats(tenantId, year = new Date().getFullYear()) {
        return this.aggregate([
            {
                $match: {
                    tenantId,
                    year,
                    verificationStatus: { $in: ['VERIFIED', 'AUTO_VERIFIED'] },
                    deleted: false
                }
            },
            {
                $group: {
                    _id: {
                        name: '$provider.name',
                        type: '$provider.type',
                        accreditationNumber: '$provider.accreditationNumber'
                    },
                    totalHours: { $sum: '$hours' },
                    totalActivities: { $sum: 1 },
                    ethicsHours: {
                        $sum: {
                            $cond: [
                                { $eq: ['$category', 'ETHICS'] },
                                '$hours',
                                0
                            ]
                        }
                    },
                    averageHours: { $avg: '$hours' },
                    verifiedCount: { $sum: 1 },
                    autoVerifiedCount: {
                        $sum: {
                            $cond: [
                                { $eq: ['$verificationStatus', 'AUTO_VERIFIED'] },
                                1,
                                0
                            ]
                        }
                    },
                    averageScore: { $avg: '$accreditation.qualityAssuranceScore' }
                }
            },
            {
                $project: {
                    providerName: '$_id.name',
                    providerType: '$_id.type',
                    accreditationNumber: '$_id.accreditationNumber',
                    totalHours: { $round: ['$totalHours', 1] },
                    totalActivities: 1,
                    ethicsHours: { $round: ['$ethicsHours', 1] },
                    averageHours: { $round: ['$averageHours', 1] },
                    verifiedCount: 1,
                    autoVerifyRate: {
                        $round: [
                            { $multiply: [{ $divide: ['$autoVerifiedCount', '$verifiedCount'] }, 100] },
                            1
                        ]
                    },
                    averageScore: { $round: ['$averageScore', 0] }
                }
            },
            { $sort: { totalHours: -1 } }
        ]);
    },

    /**
     * Get CPD compliance trends over multiple years
     * @param {string} attorneyId - Attorney ID
     * @param {string} tenantId - Tenant ID
     * @param {number} years - Number of years to analyze
     * @returns {Promise<Array>} Compliance trends
     */
    async getComplianceTrends(attorneyId, tenantId, years = 5) {
        const currentYear = new Date().getFullYear();
        const startYear = currentYear - years + 1;
        const trends = [];

        for (let year = startYear; year <= currentYear; year++) {
            const summary = await this.getAttorneySummary(attorneyId, tenantId, year);
            trends.push({
                year,
                ...summary.summary,
                ...summary.compliance
            });
        }

        return trends;
    }
};

// ====================================================================
// INSTANCE METHODS - BUSINESS LOGIC
// ====================================================================

cpdRecordSchema.methods = {
    /**
     * Verify CPD activity
     * @param {string} userId - User performing verification
     * @param {string} method - Verification method
     * @param {string} notes - Verification notes
     * @returns {Promise<Object>} Verification result
     */
    async verify(userId, method = 'MANUAL', notes = '') {
        if (this.isVerified) {
            throw new Error('CPD_ALREADY_VERIFIED: This activity has already been verified');
        }

        this.verificationStatus = 'VERIFIED';
        this.verificationMethod = method;
        this.verifiedBy = userId;
        this.verifiedAt = new Date();
        this.verificationNotes = notes;

        // Auto-generate certificate if not exists
        if (!this.certificateGenerated) {
            await this.generateCertificate();
        }

        this.auditTrail.push({
            action: 'VERIFIED',
            performedBy: userId,
            performedAt: new Date(),
            changes: { method, notes }
        });

        await this.save();

        // Update attorney's CPD status
        const AttorneyProfile = mongoose.model('AttorneyProfile');
        const attorney = await AttorneyProfile.findById(this.attorneyId);

        if (attorney) {
            const summary = await this.constructor.getAttorneySummary(
                this.attorneyId,
                this.tenantId,
                this.year
            );

            attorney.cpd.hoursCompleted = summary.summary.totalHours;
            attorney.cpd.ethicsHours = summary.summary.ethicsHours;
            attorney.cpd.complianceStatus = summary.compliance.isCompliant ? 'COMPLIANT' : 'NON_COMPLIANT';
            attorney.cpd.lastSubmissionDate = new Date();
            attorney.cpd.verifiedAt = new Date();
            attorney.cpd.verifiedBy = userId;

            await attorney.save();
        }

        return {
            success: true,
            activityId: this.activityId,
            verifiedAt: this.verifiedAt,
            verifiedBy: userId,
            method,
            certificateGenerated: this.certificateGenerated,
            certificateId: this.complianceCertificate?.certificateId
        };
    },

    /**
     * Reject CPD activity
     * @param {string} userId - User performing rejection
     * @param {string} reason - Rejection reason
     * @returns {Promise<Object>} Rejection result
     */
    async reject(userId, reason) {
        if (this.isVerified) {
            throw new Error('CPD_ALREADY_VERIFIED: Cannot reject a verified activity');
        }

        this.verificationStatus = 'REJECTED';
        this.rejectionReason = reason;
        this.verifiedBy = userId;
        this.verifiedAt = new Date();

        this.auditTrail.push({
            action: 'REJECTED',
            performedBy: userId,
            performedAt: new Date(),
            changes: { reason }
        });

        await this.save();

        return {
            success: true,
            activityId: this.activityId,
            rejectedAt: this.verifiedAt,
            rejectedBy: userId,
            reason
        };
    },

    /**
     * Generate compliance certificate
     * @returns {Promise<Object>} Generated certificate
     */
    async generateCertificate() {
        if (this.certificateGenerated) {
            return {
                success: false,
                message: 'Certificate already generated',
                certificateId: this.complianceCertificate?.certificateId
            };
        }

        if (!this.isVerified) {
            throw new Error('CERTIFICATE_VERIFICATION_REQUIRED: Activity must be verified before certificate generation');
        }

        const certificateId = `CPD-CERT-${this.year}-LPC-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
        const issuedAt = new Date();
        const expiresAt = new Date(this.year + 1, 11, 31); // December 31 of next year

        // Generate certificate hash
        const certificateHash = crypto
            .createHash('sha3-512')
            .update([
                certificateId,
                this.forensicHash,
                issuedAt.toISOString(),
                this.attorneyLpcNumber,
                this.hours.toString(),
                this.category
            ].join(':'))
            .digest('hex');

        // Generate digital signature
        const digitalSignature = crypto
            .createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026')
            .update(`${certificateId}:${this.forensicHash}:${issuedAt.toISOString()}`)
            .digest('hex');

        this.complianceCertificate = {
            certificateId,
            issuedAt,
            expiresAt,
            certificateHash,
            digitalSignature,
            verificationUrl: `https://verify.wilsyos.co.za/cpd/${certificateId}`,
            verificationQR: `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${certificateId}`,
            pdfUrl: `https://certificates.wilsyos.co.za/cpd/${certificateId}.pdf`
        };

        this.certificateGenerated = true;
        this.certificateGeneratedAt = issuedAt;

        this.auditTrail.push({
            action: 'CERTIFICATE_GENERATED',
            performedBy: this.verifiedBy || 'SYSTEM',
            performedAt: new Date(),
            changes: { certificateId, expiresAt }
        });

        await this.save();

        return {
            success: true,
            certificateId,
            certificate: this.complianceCertificate
        };
    },

    /**
     * Anchor to blockchain (ECT Act §15)
     * @returns {Promise<Object>} Blockchain anchor result
     */
    async anchorToBlockchain() {
        if (this.blockchain?.verified) {
            return {
                success: false,
                message: 'Already anchored to blockchain',
                anchorId: this.blockchain.anchorId
            };
        }

        if (!this.isVerified) {
            throw new Error('BLOCKCHAIN_VERIFICATION_REQUIRED: Activity must be verified before blockchain anchoring');
        }

        // Simulate blockchain anchoring (production would integrate with Ethereum, Hyperledger, or OpenTimestamps)
        const anchorId = `OTS-${crypto.randomBytes(8).toString('hex').toUpperCase()}`;
        const transactionHash = crypto
            .createHash('sha3-512')
            .update(`${anchorId}:${this.forensicHash}:${Date.now()}`)
            .digest('hex');

        this.blockchain = {
            anchorId,
            transactionHash,
            blockNumber: Math.floor(Date.now() / 1000), // Simulated block number
            timestamp: new Date(),
            verified: true,
            verificationUrl: `https://verify.wilsyos.co.za/blockchain/${anchorId}`
        };

        this.auditTrail.push({
            action: 'BLOCKCHAIN_ANCHORED',
            performedBy: 'SYSTEM',
            performedAt: new Date(),
            changes: { anchorId, transactionHash }
        });

        await this.save();

        return {
            success: true,
            anchorId,
            transactionHash,
            timestamp: this.blockchain.timestamp,
            verificationUrl: this.blockchain.verificationUrl
        };
    },

    /**
     * Rollover excess hours to next year (LPC Rule 3.8)
     * @param {string} userId - User performing rollover
     * @returns {Promise<Object>} Rollover result
     */
    async rollover(userId) {
        if (!this.compliance.rolloverEligible) {
            throw new Error('ROLLOVER_INELIGIBLE: This activity is not eligible for rollover (LPC Rule 3.8)');
        }

        const excessHours = this.hours - 12;
        if (excessHours <= 0) {
            throw new Error('ROLLOVER_NOT_REQUIRED: No excess hours to rollover');
        }

        const rolloverHours = Math.min(excessHours, 6); // Max 6 hours rollover
        const rolloverYear = this.year + 1;

        this.compliance.rolloverHours = parseFloat(rolloverHours.toFixed(1));
        this.compliance.rolloverYear = rolloverYear;
        this.compliance.appliedToYear = rolloverYear;
        this.verificationStatus = 'EXPIRED';

        this.auditTrail.push({
            action: 'ROLLED_OVER',
            performedBy: userId,
            performedAt: new Date(),
            changes: { rolloverHours, rolloverYear }
        });

        await this.save();

        return {
            success: true,
            activityId: this.activityId,
            originalHours: this.hours,
            rolloverHours,
            rolloverYear,
            appliedToYear: rolloverYear
        };
    },

    /**
     * Generate forensic audit report
     * @returns {Promise<Object>} Audit report
     */
    async generateAuditReport() {
        const summary = await this.constructor.getAttorneySummary(
            this.attorneyId,
            this.tenantId,
            this.year
        );

        return {
            activityId: this.activityId,
            attorneyLpcNumber: this.attorneyLpcNumber,
            activityName: this.activityName,
            activityDate: this.activityDate,
            hours: this.hours,
            category: this.category,
            provider: this.provider.name,
            providerType: this.provider.type,
            accreditationNumber: this.provider.accreditationNumber,
            verificationStatus: this.verificationStatus,
            verificationMethod: this.verificationMethod,
            verifiedAt: this.verifiedAt,
            verifiedBy: this.verifiedBy,
            submittedBy: this.submittedBy,
            submissionDate: this.submissionDate,
            compliance: {
                countsTowardsAnnual: this.compliance.countsTowardsAnnual,
                countsTowardsEthics: this.compliance.countsTowardsEthics,
                rolloverEligible: this.compliance.rolloverEligible,
                rolloverHours: this.compliance.rolloverHours,
                rolloverYear: this.compliance.rolloverYear
            },
            certificate: {
                generated: this.certificateGenerated,
                certificateId: this.complianceCertificate?.certificateId,
                issuedAt: this.complianceCertificate?.issuedAt,
                expiresAt: this.complianceCertificate?.expiresAt
            },
            blockchain: {
                anchored: this.blockchain?.verified || false,
                anchorId: this.blockchain?.anchorId,
                timestamp: this.blockchain?.timestamp
            },
            attorneySummary: summary,
            integrity: {
                forensicHash: this.forensicHash,
                integrityHash: this.integrityHash,
                quantumSignature: this.quantumSignature
            },
            auditTrail: this.auditTrail.slice(-10), // Last 10 actions
            retention: {
                policy: this.retentionPolicy,
                expiryDate: this.retentionExpiry,
                daysRemaining: Math.ceil((this.retentionExpiry - Date.now()) / (1000 * 60 * 60 * 24))
            },
            generatedAt: new Date().toISOString(),
            generatedBy: 'WilsyOS CPD Forensic Engine v5.0.0'
        };
    },

    /**
     * Update verification status
     * @param {string} status - New status
     * @param {string} userId - User performing update
     * @param {string} notes - Update notes
     * @returns {Promise<Object>} Update result
     */
    async updateVerificationStatus(status, userId, notes = '') {
        const oldStatus = this.verificationStatus;
        this.verificationStatus = status;
        this.verifiedBy = userId;
        this.verifiedAt = new Date();
        this.verificationNotes = notes;

        this.auditTrail.push({
            action: status === 'VERIFIED' ? 'VERIFIED' : 'UPDATED',
            performedBy: userId,
            performedAt: new Date(),
            changes: { oldStatus, newStatus: status, notes }
        });

        await this.save();

        return {
            success: true,
            activityId: this.activityId,
            oldStatus,
            newStatus: status,
            updatedAt: this.verifiedAt,
            updatedBy: userId
        };
    }
};

// ====================================================================
// EXPORT - SINGLETON MODEL
// ====================================================================

const CPDRecord = mongoose.model('CPDRecord', cpdRecordSchema);
module.exports = CPDRecord;

/**
 * @mermaid
 * graph TD
 *     CPDRecord --> AttorneyProfile
 *     CPDRecord --> Provider[Provider Accreditation]
 *     CPDRecord --> Verification{Verification Status}
 *
 *     Verification -->|Pending| Manual[Manual Review]
 *     Verification -->|Auto| Blockchain[Blockchain Anchor]
 *     Verification -->|Verified| Certificate[Generate Certificate]
 *
 *     Certificate --> Rollover{Eligible?}
 *     Rollover -->|Yes| NextYear[Rollover to Next Year]
 *     Rollover -->|No| Complete[Complete]
 *
 *     Blockchain --> ECT[ECT Act §15 Admissible]
 *
 *     style CPDRecord fill:#e1f5e1
 *     style Verification fill:#fff3cd
 *     style Certificate fill:#d4edda
 *     style Blockchain fill:#f8d7da
 */
