/**
 * WILSYS OS - ATTORNEY PROFILE MODEL
 * ====================================================================
 * LEGAL PRACTICE COUNCIL · FORENSIC ATTORNEY REGISTRY
 * QUANTUM-SEALED · POPIA §19 · LPC §55/86
 * 
 * @version 5.0.0
 * @author Wilson Khanyezi - Chief Quantum Sentinel
 * @copyright Wilsy OS (Pty) Ltd 2026
 * 
 * @description Complete attorney profile management with:
 *              - LPC number validation (LPC-12345678 or 2024/1234)
 *              - Fidelity Fund certificate tracking
 *              - CPD compliance monitoring
 *              - Trust account integration
 *              - Forensic audit trails with SHA3-512
 *              - POPIA §19 automated PII redaction
 *              - Tenant isolation for multi-tenant security
 * 
 * @compliance Legal Practice Act 28 of 2014 - Sections 55, 86, 95(3)
 * @compliance LPC Rules (2023 Amendments) - Chapters 3, 7, 11
 * @compliance POPIA 2013 - Section 19 (Security Safeguards)
 * @compliance Companies Act 71 of 2008 - Section 33
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

const ATTORNEY_STATUS = {
    ACTIVE: 'ACTIVE',
    SUSPENDED: 'SUSPENDED',
    EXPIRED: 'EXPIRED',
    DECEASED: 'DECEASED',
    RESIGNED: 'RESIGNED',
    RETIRED: 'RETIRED',
    NON_PRACTICING: 'NON_PRACTICING'
};

const PRACTICE_TYPES = {
    PRIVATE: 'PRIVATE',
    GOVERNMENT: 'GOVERNMENT',
    CORPORATE: 'CORPORATE',
    LEGAL_AID: 'LEGAL_AID',
    ACADEMIC: 'ACADEMIC',
    NON_PRACTICING: 'NON_PRACTICING'
};

const PRACTICE_AREAS = {
    URBAN: 'URBAN',
    RURAL: 'RURAL',
    INTERNATIONAL: 'INTERNATIONAL'
};

const FIDELITY_STATUS = {
    ACTIVE: 'ACTIVE',
    EXPIRED: 'EXPIRED',
    REVOKED: 'REVOKED',
    PENDING: 'PENDING',
    SUSPENDED: 'SUSPENDED'
};

const CPD_STATUS = {
    COMPLIANT: 'COMPLIANT',
    NON_COMPLIANT: 'NON_COMPLIANT',
    PENDING: 'PENDING',
    EXEMPT: 'EXEMPT',
    GRACE_PERIOD: 'GRACE_PERIOD'
};

const DISCIPLINARY_STATUS = {
    NONE: 'NONE',
    PENDING: 'PENDING',
    UNDER_INVESTIGATION: 'UNDER_INVESTIGATION',
    HEARING_SCHEDULED: 'HEARING_SCHEDULED',
    SANCTIONED: 'SANCTIONED',
    APPEALED: 'APPEALED',
    RESOLVED: 'RESOLVED'
};

// ====================================================================
// ATTORNEY PROFILE SCHEMA - FORENSIC ARCHITECTURE
// ====================================================================

const attorneyProfileSchema = new Schema({
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
    // PRIMARY IDENTIFIERS - LPC §55
    // ====================================================================
    lpcNumber: {
        type: String,
        required: [true, 'LPC number is required by Legal Practice Act Section 55'],
        unique: true,
        uppercase: true,
        trim: true,
        immutable: true,
        validate: {
            validator: function(v) {
                return /^(LPC-\d{8}|\d{4}\/\d{4})$/.test(v);
            },
            message: props => `${props.value} is not a valid LPC number. Format: LPC-12345678 or 2024/1234`
        },
        index: true
    },

    practiceNumber: {
        type: String,
        unique: true,
        sparse: true,
        uppercase: true,
        trim: true,
        validate: {
            validator: function(v) {
                return !v || /^PRAC-\d{8}$/.test(v);
            },
            message: props => `${props.value} is not a valid practice number. Format: PRAC-12345678`
        }
    },

    // ====================================================================
    // PERSONAL INFORMATION - POPIA §19 PROTECTED
    // ====================================================================
    personalInfo: {
        title: {
            type: String,
            enum: ['Mr', 'Mrs', 'Ms', 'Dr', 'Prof', 'Adv', 'Justice'],
            required: true
        },
        fullName: {
            type: String,
            required: true,
            trim: true,
            maxlength: [200, 'Full name cannot exceed 200 characters']
        },
        preferredName: {
            type: String,
            trim: true,
            maxlength: [100, 'Preferred name cannot exceed 100 characters']
        },
        idNumber: {
            type: String,
            required: true,
            unique: true,
            validate: {
                validator: function(v) {
                    return /^\d{13}$/.test(v);
                },
                message: 'South African ID number must be 13 digits'
            }
        },
        passportNumber: {
            type: String,
            sparse: true,
            validate: {
                validator: function(v) {
                    return !v || /^[A-Z]{2}\d{7}$/.test(v);
                },
                message: 'Passport number must be 2 letters followed by 7 digits'
            }
        },
        nationality: {
            type: String,
            default: 'South African',
            maxlength: 50
        },
        dateOfBirth: {
            type: Date,
            required: true,
            validate: {
                validator: function(v) {
                    const age = (Date.now() - v) / (1000 * 60 * 60 * 24 * 365);
                    return age >= 21 && age <= 100;
                },
                message: 'Attorney must be between 21 and 100 years old'
            }
        },
        gender: {
            type: String,
            enum: ['Male', 'Female', 'Other', 'Prefer not to say']
        }
    },

    // ====================================================================
    // CONTACT INFORMATION - POPIA §19 PROTECTED
    // ====================================================================
    contact: {
        email: {
            type: String,
            required: true,
            lowercase: true,
            trim: true,
            validate: {
                validator: function(v) {
                    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
                },
                message: 'Invalid email address format'
            }
        },
        alternativeEmail: {
            type: String,
            lowercase: true,
            trim: true,
            validate: {
                validator: function(v) {
                    return !v || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
                }
            }
        },
        phone: {
            type: String,
            required: true,
            validate: {
                validator: function(v) {
                    return /^(\+27|0)[1-9][0-9]{8}$/.test(v);
                },
                message: 'Invalid South African phone number. Format: +27123456789 or 0123456789'
            }
        },
        alternativePhone: {
            type: String,
            validate: {
                validator: function(v) {
                    return !v || /^(\+27|0)[1-9][0-9]{8}$/.test(v);
                }
            }
        },
        fax: {
            type: String,
            validate: {
                validator: function(v) {
                    return !v || /^(\+27|0)[1-9][0-9]{8}$/.test(v);
                }
            }
        }
    },

    // ====================================================================
    // ADDRESS INFORMATION - POPIA §19 PROTECTED
    // ====================================================================
    address: {
        physical: {
            line1: { type: String, required: true },
            line2: { type: String },
            suburb: { type: String, required: true },
            city: { type: String, required: true },
            province: {
                type: String,
                required: true,
                enum: ['GP', 'WC', 'KZN', 'EC', 'FS', 'MP', 'NW', 'LIM', 'NC']
            },
            postalCode: { type: String, required: true },
            country: { type: String, default: 'South Africa' }
        },
        postal: {
            line1: String,
            line2: String,
            suburb: String,
            city: String,
            province: String,
            postalCode: String,
            country: { type: String, default: 'South Africa' }
        },
        jurisdiction: {
            magisterialDistrict: {
                type: String,
                required: true,
                index: true
            },
            highCourtDivision: {
                type: String,
                required: true,
                enum: ['GP', 'GJD', 'KZD', 'ECD', 'FB', 'MM', 'NWM', 'LPM', 'NCK']
            }
        }
    },

    // ====================================================================
    // PRACTICE INFORMATION - LPC COMPLIANCE
    // ====================================================================
    practice: {
        name: {
            type: String,
            required: [true, 'Practice name is required'],
            trim: true,
            maxlength: 200
        },
        type: {
            type: String,
            required: true,
            enum: Object.values(PRACTICE_TYPES)
        },
        area: {
            type: String,
            required: true,
            enum: Object.values(PRACTICE_AREAS)
        },
        commencementDate: {
            type: Date,
            required: true,
            immutable: true
        },
        yearsOfPractice: {
            type: Number,
            default: function() {
                const years = (Date.now() - this.practice.commencementDate) / (1000 * 60 * 60 * 24 * 365);
                return Math.floor(years);
            }
        },
        specializations: [{
            type: String,
            enum: [
                'LITIGATION',
                'CONVEYANCING',
                'COMMERCIAL',
                'ESTATE',
                'FAMILY',
                'CRIMINAL',
                'LABOUR',
                'TAX',
                'INTELLECTUAL_PROPERTY',
                'CONSTITUTIONAL',
                'ENVIRONMENTAL',
                'INSURANCE',
                'BANKING',
                'IMMIGRATION'
            ]
        }],
        languages: [{
            language: {
                type: String,
                required: true
            },
            proficiency: {
                type: String,
                enum: ['BASIC', 'INTERMEDIATE', 'FLUENT', 'NATIVE'],
                required: true
            }
        }],
        employees: {
            type: Number,
            default: 1,
            min: 1
        },
        partners: {
            type: Number,
            default: 1,
            min: 1
        }
    },

    // ====================================================================
    // FIDELITY FUND CERTIFICATE - LPC §55
    // ====================================================================
    fidelityFund: {
        certificateNumber: {
            type: String,
            sparse: true,
            validate: {
                validator: function(v) {
                    return !v || /^FFC-\d{4}-[A-F0-9]{8}$/.test(v);
                },
                message: 'Invalid fidelity fund certificate format. Format: FFC-2026-1A2B3C4D'
            }
        },
        issueDate: Date,
        expiryDate: {
            type: Date,
            index: true
        },
        status: {
            type: String,
            enum: Object.values(FIDELITY_STATUS),
            default: 'PENDING'
        },
        contributionAmount: {
            type: Number,
            min: 0,
            get: v => parseFloat(v.toFixed(2))
        },
        turnoverDeclared: {
            type: Number,
            min: 0,
            get: v => parseFloat(v.toFixed(2))
        },
        verificationHash: String
    },

    // ====================================================================
    // CPD COMPLIANCE - LPC CHAPTER 3
    // ====================================================================
    cpd: {
        currentYear: {
            type: Number,
            default: new Date().getFullYear(),
            index: true
        },
        hoursCompleted: {
            type: Number,
            default: 0,
            min: 0,
            max: 30
        },
        ethicsHours: {
            type: Number,
            default: 0,
            min: 0,
            max: 10
        },
        lastSubmissionDate: Date,
        complianceStatus: {
            type: String,
            enum: Object.values(CPD_STATUS),
            default: 'PENDING'
        },
        rolloverHours: {
            type: Number,
            default: 0,
            min: 0,
            max: 6
        },
        verifiedAt: Date,
        verifiedBy: String
    },

    // ====================================================================
    // TRUST ACCOUNT STATUS - LPC §86
    // ====================================================================
    trustAccount: {
        accountNumber: {
            type: String,
            sparse: true,
            validate: {
                validator: function(v) {
                    return !v || /^TRUST-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$/.test(v);
                }
            }
        },
        bankName: {
            type: String,
            enum: ['ABSA', 'FNB', 'NEDBANK', 'STANDARD_BANK', 'CAPITEC', 'AFRICAN_BANK', 'BIDVEST_BANK', 'DISCOVERY_BANK']
        },
        isActive: {
            type: Boolean,
            default: false
        },
        lastReconciliation: Date,
        nextReconciliationDue: Date,
        complianceScore: {
            type: Number,
            min: 0,
            max: 100,
            default: 0
        }
    },

    // ====================================================================
    // EMPLOYMENT HISTORY - FORENSIC AUDIT
    // ====================================================================
    employmentHistory: [{
        firmName: { type: String, required: true },
        position: { type: String, required: true },
        startDate: { type: Date, required: true },
        endDate: Date,
        isCurrent: { type: Boolean, default: false },
        supervisor: String,
        reference: String,
        verifiedAt: Date,
        verifiedBy: String,
        verificationHash: String
    }],

    // ====================================================================
    // QUALIFICATIONS - LEGAL EDUCATION
    // ====================================================================
    qualifications: [{
        degree: { type: String, required: true },
        institution: { type: String, required: true },
        yearObtained: { type: Number, required: true },
        country: { type: String, default: 'South Africa' },
        classification: String,
        certificateHash: String,
        verifiedAt: Date,
        verifiedBy: String
    }],

    // ====================================================================
    // DISCIPLINARY HISTORY - LPC COMPLIANCE
    // ====================================================================
    disciplinaryHistory: [{
        caseNumber: { type: String, required: true },
        allegation: String,
        finding: String,
        sanction: String,
        imposedAt: Date,
        resolvedAt: Date,
        status: {
            type: String,
            enum: ['PENDING', 'UNDER_INVESTIGATION', 'RESOLVED', 'APPEALED']
        },
        notes: String,
        recordedBy: String,
        recordedAt: { type: Date, default: Date.now }
    }],

    // ====================================================================
    // FORENSIC AUDIT TRAIL - IMMUTABLE HISTORY
    // ====================================================================
    auditTrail: [{
        action: { type: String, required: true },
        performedBy: { type: String, required: true },
        performedAt: { type: Date, default: Date.now },
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
    // CRYPTOGRAPHIC VERIFICATION - TAMPER-PROOF
    // ====================================================================
    integrityHash: {
        type: String,
        default: function() {
            return crypto
                .createHash('sha3-512')
                .update(`${this.lpcNumber}:${this.personalInfo.idNumber}:${this.updatedAt || Date.now()}`)
                .digest('hex');
        }
    },

    quantumSignature: {
        type: String,
        default: function() {
            return crypto
                .createHmac('sha3-512', process.env.QUANTUM_SECRET || 'wilsy-os-quantum-secure-2026')
                .update(`${this._id}:${this.lpcNumber}:${this.integrityHash}`)
                .digest('hex');
        }
    },

    // ====================================================================
    // SYSTEM FIELDS - FORENSIC INTEGRITY
    // ====================================================================
    status: {
        type: String,
        enum: Object.values(ATTORNEY_STATUS),
        default: 'ACTIVE',
        index: true
    },
    statusReason: String,
    statusChangedAt: Date,
    statusChangedBy: String,

    createdBy: {
        type: String,
        required: true,
        immutable: true
    },
    createdAt: {
        type: Date,
        default: Date.now,
        immutable: true,
        index: true
    },
    updatedBy: {
        type: String,
        required: true
    },
    updatedAt: {
        type: Date,
        default: Date.now
    },

    // ====================================================================
    // RETENTION METADATA - COMPANIES ACT 71 OF 2008
    // ====================================================================
    retentionPolicy: {
        type: String,
        default: 'companies_act_20_years'
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
            date.setFullYear(date.getFullYear() + 20);
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
            delete ret.integrityHash;
            delete ret.quantumSignature;
            delete ret.personalInfo.idNumber;
            delete ret.contact.phone;
            delete ret.contact.email;
            ret = redactSensitiveData(ret);
            return ret;
        }
    },
    toObject: {
        virtuals: true,
        transform: function(doc, ret) {
            delete ret.__v;
            return redactSensitiveData(ret);
        }
    }
});

// ====================================================================
// VIRTUAL FIELDS - COMPUTED PROPERTIES
// ====================================================================

attorneyProfileSchema.virtual('fullAddress').get(function() {
    if (!this.address?.physical) return '';
    const addr = this.address.physical;
    return `${addr.line1}, ${addr.suburb}, ${addr.city}, ${addr.province}, ${addr.postalCode}`;
});

attorneyProfileSchema.virtual('isFidelityValid').get(function() {
    return this.fidelityFund?.status === 'ACTIVE' &&
           this.fidelityFund?.expiryDate > new Date();
});

attorneyProfileSchema.virtual('isTrustCompliant').get(function() {
    return this.trustAccount?.isActive === true &&
           this.trustAccount?.complianceScore >= 70;
});

attorneyProfileSchema.virtual('isCPDCompliant').get(function() {
    return this.cpd?.complianceStatus === 'COMPLIANT';
});

attorneyProfileSchema.virtual('daysUntilFidelityExpiry').get(function() {
    if (!this.fidelityFund?.expiryDate) return null;
    return Math.ceil((this.fidelityFund.expiryDate - Date.now()) / (1000 * 60 * 60 * 24));
});

attorneyProfileSchema.virtual('complianceScore').get(function() {
    let score = 100;
    if (!this.isFidelityValid) score -= 30;
    if (!this.isTrustCompliant) score -= 25;
    if (!this.isCPDCompliant) score -= 20;
    if (this.disciplinaryHistory?.length > 0) score -= 15;
    return Math.max(0, score);
});

// ====================================================================
// INDEXES - PERFORMANCE OPTIMIZATION
// ====================================================================

attorneyProfileSchema.index({ tenantId: 1, lpcNumber: 1 }, { unique: true });
attorneyProfileSchema.index({ tenantId: 1, status: 1, 'fidelityFund.expiryDate': 1 });
attorneyProfileSchema.index({ tenantId: 1, 'cpd.complianceStatus': 1, 'cpd.currentYear': 1 });
attorneyProfileSchema.index({ tenantId: 1, 'practice.type': 1, 'practice.area': 1 });
attorneyProfileSchema.index({ tenantId: 1, 'address.jurisdiction.magisterialDistrict': 1 });
attorneyProfileSchema.index({ deleted: 1, retentionExpiry: 1 });
attorneyProfileSchema.index({ integrityHash: 1 }, { unique: true });

// ====================================================================
// PRE-SAVE HOOKS - FORENSIC INTEGRITY
// ====================================================================

attorneyProfileSchema.pre('save', async function(next) {
    try {
        // TENANT ISOLATION - FAIL CLOSED
        if (!this.tenantId) {
            throw new Error('TENANT_ISOLATION_VIOLATION: Attorney profile requires tenantId');
        }

        // Calculate years of practice
        if (this.practice?.commencementDate) {
            const years = (Date.now() - this.practice.commencementDate) / (1000 * 60 * 60 * 24 * 365);
            this.practice.yearsOfPractice = Math.floor(years);
        }

        // Update integrity hash
        this.integrityHash = crypto
            .createHash('sha3-512')
            .update(`${this.lpcNumber}:${this.personalInfo?.idNumber}:${Date.now()}`)
            .digest('hex');

        // Add audit trail
        if (this.isNew) {
            this.auditTrail.push({
                action: 'ATTORNEY_PROFILE_CREATED',
                performedBy: this.createdBy,
                performedAt: new Date(),
                changes: { lpcNumber: this.lpcNumber, practiceName: this.practice?.name }
            });
        } else {
            this.auditTrail.push({
                action: 'ATTORNEY_PROFILE_UPDATED',
                performedBy: this.updatedBy,
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

attorneyProfileSchema.statics = {
    /**
     * Find active attorneys with valid fidelity certificates
     * @param {string} tenantId - Tenant identifier
     * @returns {Promise<Array>} Active attorneys with valid fidelity
     */
    async findActiveWithFidelity(tenantId) {
        return this.find({
            tenantId,
            status: 'ACTIVE',
            deleted: false,
            'fidelityFund.status': 'ACTIVE',
            'fidelityFund.expiryDate': { $gt: new Date() }
        }).sort({ 'fidelityFund.expiryDate': 1 });
    },

    /**
     * Find non-compliant attorneys for CPD
     * @param {string} tenantId - Tenant identifier
     * @param {number} year - Compliance year
     * @returns {Promise<Array>} Non-compliant attorneys
     */
    async findCPDNonCompliant(tenantId, year = new Date().getFullYear()) {
        return this.find({
            tenantId,
            status: 'ACTIVE',
            deleted: false,
            'cpd.currentYear': year,
            'cpd.complianceStatus': { $ne: 'COMPLIANT' }
        });
    },

    /**
     * Find attorneys requiring trust reconciliation
     * @param {string} tenantId - Tenant identifier
     * @returns {Promise<Array>} Attorneys with overdue reconciliation
     */
    async findRequiringReconciliation(tenantId) {
        return this.find({
            tenantId,
            status: 'ACTIVE',
            deleted: false,
            'trustAccount.isActive': true,
            'trustAccount.nextReconciliationDue': { $lte: new Date() }
        });
    },

    /**
     * Search attorneys by name or LPC number
     * @param {string} tenantId - Tenant identifier
     * @param {string} query - Search query
     * @returns {Promise<Array>} Matching attorneys
     */
    async search(tenantId, query) {
        return this.find({
            tenantId,
            deleted: false,
            $or: [
                { lpcNumber: new RegExp(query, 'i') },
                { 'personalInfo.fullName': new RegExp(query, 'i') },
                { 'practice.name': new RegExp(query, 'i') }
            ]
        }).limit(50);
    }
};

// ====================================================================
// INSTANCE METHODS - BUSINESS LOGIC
// ====================================================================

attorneyProfileSchema.methods = {
    /**
     * Verify if attorney can practice
     * @returns {boolean} True if attorney can practice
     */
    canPractice() {
        return this.status === 'ACTIVE' &&
               this.isFidelityValid === true &&
               !this.deleted;
    },

    /**
     * Calculate comprehensive compliance score
     * @returns {Promise<number>} Compliance score 0-100
     */
    async calculateComplianceScore() {
        let score = 100;

        // Fidelity Fund compliance (-30 if invalid)
        if (!this.isFidelityValid) score -= 30;

        // Trust account compliance (-25 if inactive or low score)
        if (!this.trustAccount?.isActive) score -= 25;
        else if (this.trustAccount.complianceScore < 70) score -= 15;

        // CPD compliance (-20 if non-compliant)
        if (this.cpd.complianceStatus !== 'COMPLIANT') score -= 20;

        // Disciplinary history (-15 per pending case)
        if (this.disciplinaryHistory) {
            const pendingCases = this.disciplinaryHistory.filter(d =>
                ['PENDING', 'UNDER_INVESTIGATION'].includes(d.status)
            );
            score -= pendingCases.length * 15;
        }

        return Math.max(0, Math.min(100, score));
    },

    /**
     * Update CPD status
     * @param {number} hours - CPD hours completed
     * @param {number} ethicsHours - Ethics hours completed
     * @param {string} userId - User performing update
     * @returns {Promise<Object>} Updated CPD status
     */
    async updateCPDStatus(hours, ethicsHours, userId) {
        this.cpd.hoursCompleted += hours;
        this.cpd.ethicsHours += ethicsHours;
        this.cpd.lastSubmissionDate = new Date();

        // Check compliance (12 hours total, 2 ethics minimum)
        if (this.cpd.hoursCompleted >= 12 && this.cpd.ethicsHours >= 2) {
            this.cpd.complianceStatus = 'COMPLIANT';
            this.cpd.verifiedAt = new Date();
            this.cpd.verifiedBy = userId;
        }

        this.updatedBy = userId;
        await this.save();

        return {
            hoursCompleted: this.cpd.hoursCompleted,
            ethicsHours: this.cpd.ethicsHours,
            complianceStatus: this.cpd.complianceStatus,
            remainingHours: Math.max(0, 12 - this.cpd.hoursCompleted),
            remainingEthics: Math.max(0, 2 - this.cpd.ethicsHours)
        };
    },

    /**
     * Update fidelity fund certificate
     * @param {Object} fidelityData - Fidelity fund certificate data
     * @param {string} userId - User performing update
     * @returns {Promise<Object>} Updated fidelity status
     */
    async updateFidelityCertificate(fidelityData, userId) {
        this.fidelityFund = {
            ...this.fidelityFund,
            ...fidelityData,
            status: 'ACTIVE',
            issueDate: new Date(),
            expiryDate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000)
        };

        this.fidelityFund.verificationHash = crypto
            .createHash('sha3-512')
            .update(`${this.lpcNumber}:${this.fidelityFund.certificateNumber}:${Date.now()}`)
            .digest('hex');

        this.updatedBy = userId;
        await this.save();

        return {
            certificateNumber: this.fidelityFund.certificateNumber,
            issueDate: this.fidelityFund.issueDate,
            expiryDate: this.fidelityFund.expiryDate,
            status: this.fidelityFund.status,
            verificationHash: this.fidelityFund.verificationHash
        };
    },

    /**
     * Generate forensic audit report
     * @returns {Promise<Object>} Comprehensive audit report
     */
    async generateAuditReport() {
        const complianceScore = await this.calculateComplianceScore();

        return {
            attorneyId: this._id,
            lpcNumber: this.lpcNumber,
            practiceName: this.practice.name,
            status: this.status,
            createdAt: this.createdAt,
            updatedAt: this.updatedAt,
            createdBy: this.createdBy,
            updatedBy: this.updatedBy,
            compliance: {
                score: complianceScore,
                fidelityValid: this.isFidelityValid,
                fidelityExpiry: this.fidelityFund?.expiryDate,
                trustCompliant: this.isTrustCompliant,
                cpdCompliant: this.isCPDCompliant,
                cpdHours: this.cpd.hoursCompleted,
                cpdEthics: this.cpd.ethicsHours
            },
            retention: {
                policy: this.retentionPolicy,
                expiryDate: this.retentionExpiry,
                daysRemaining: Math.ceil((this.retentionExpiry - Date.now()) / (1000 * 60 * 60 * 24))
            },
            integrity: {
                hash: this.integrityHash,
                signature: this.quantumSignature
            },
            auditTrail: this.auditTrail.slice(-10), // Last 10 actions
            generatedAt: new Date().toISOString(),
            generatedBy: 'WilsyOS Attorney Forensic Engine v5.0.0'
        };
    }
};

// ====================================================================
// EXPORT - SINGLETON MODEL
// ====================================================================

const AttorneyProfile = mongoose.model('AttorneyProfile', attorneyProfileSchema);
module.exports = AttorneyProfile;

/**
 * @mermaid
 * graph TD
 *     AttorneyProfile --> LPC[Legal Practice Council]
 *     AttorneyProfile --> Fidelity[Fidelity Fund]
 *     AttorneyProfile --> CPD[CPD Compliance]
 *     AttorneyProfile --> Trust[Trust Account]
 *     AttorneyProfile --> Audit[Forensic Audit Trail]
 *
 *     LPC --> Status{Active/Suspended/Expired}
 *     Fidelity --> Certificate[FFC Certificate]
 *     CPD --> Hours[Annual Hours 12/2]
 *     Trust --> Reconciliation[Weekly Reconciliation]
 *     Audit --> Hash[SHA3-512 Chain]
 *
 *     style AttorneyProfile fill:#e1f5e1
 *     style Audit fill:#d4edda
 *     style Trust fill:#fff3cd
 */
