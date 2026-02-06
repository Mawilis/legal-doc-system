/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██████╗ ███╗   ██╗███████╗██╗     ███████╗██╗████████╗            ║
║  ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║     ██╔════╝██║╚══██╔══╝            ║
║  ██║     ██║   ██║██╔██╗ ██║█████╗  ██║     █████╗  ██║   ██║               ║
║  ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║     ██╔══╝  ██║   ██║               ║
║  ╚██████╗╚██████╔╝██║ ╚████║██║     ███████╗██║     ██║   ██║               ║
║   ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚══════╝╚═╝     ╚═╝   ╚═╝               ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  FILE: /Users/wilsonkhanyezi/legal-doc-system/server/models/Case.js         ║
║                                                                              ║
║  PURPOSE: Sovereign Case Model with PAIA Tracking & Conflict Screening      ║
║           ASCII: [Case]→[PAIA]→[Conflict]→[Audit]→[Persistence]             ║
║  COMPLIANCE: PAIA/POPIA/LPC Rule 7/Companies Act/ECT Act                   ║
║                                                                              ║
║  CHIEF ARCHITECT: Wilson Khanyezi                                           ║
║  EMAIL: wilsy.wk@gmail.com | CELL: +27 69 046 5710                          ║
║                                                                              ║
║  FILENAME: Case.js                                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

/**
 * @file Sovereign Case Model with PAIA Tracking & Automated Conflict Screening
 * @module models/Case
 * @description Case model with PAIA request tracking, conflict screening, and enhanced compliance
 * @requires mongoose, ./Conflict, ./AuditLedger
 * @version 3.0.0
 * @since Wilsy OS v3.0
 * @author Wilson Khanyezi
 */

const mongoose = require('mongoose');
const crypto = require('crypto');

const { Schema, model } = mongoose;

// Custom validator for case number format
const validateCaseNumber = (value) => {
    const caseNumberRegex = /^[A-Z]{2,4}-\d{4}-\d{4}(-[A-Z]{2})?$/;
    return caseNumberRegex.test(value);
};

// Custom validator for tenant ID format
const validateTenantId = (value) => {
    return /^tenant_[a-zA-Z0-9_]{8,32}$/.test(value);
};

// Enumeration constants
const CASE_STATUSES = {
    PRE_INTAKE: 'PRE_INTAKE',
    ACTIVE: 'ACTIVE',
    LEGAL_HOLD: 'LEGAL_HOLD',
    CLOSED: 'CLOSED'
};

const CONFLICT_SEVERITIES = {
    CRITICAL: 'critical',
    HIGH: 'high',
    MEDIUM: 'medium',
    LOW: 'low'
};

const PAIA_REQUEST_STATUSES = {
    PENDING: 'PENDING',
    IN_REVIEW: 'IN_REVIEW',
    PARTIALLY_GRANTED: 'PARTIALLY_GRANTED',
    GRANTED: 'GRANTED',
    DENIED: 'DENIED',
    APPEALED: 'APPEALED',
    WITHDRAWN: 'WITHDRAWN'
};

const RESOLVED_STATUS = 'resolved';

// PAIA Request Sub-schema for tracking access requests
const PaiaRequestSchema = new Schema({
    requestId: {
        type: String,
        required: [true, 'PAIA request ID is required'],
        unique: true,
        index: true
    },
    requesterType: {
        type: String,
        enum: ['INDIVIDUAL', 'COMPANY', 'GOVERNMENT', 'LAW_FIRM'],
        required: true
    },
    requesterDetails: {
        name: { type: String, required: true, trim: true },
        idNumber: String,
        contactEmail: { type: String, lowercase: true },
        contactPhone: String,
        postalAddress: String
    },
    requestedInformation: [{
        description: { type: String, required: true },
        documentType: String,
        dateRange: {
            from: Date,
            to: Date
        },
        specificReference: String
    }],
    requestDate: { type: Date, default: Date.now },
    statutoryDeadline: { type: Date, required: true },
    status: {
        type: String,
        enum: Object.values(PAIA_REQUEST_STATUSES),
        default: PAIA_REQUEST_STATUSES.PENDING,
        index: true
    },
    reviewDetails: {
        reviewedBy: { type: Schema.Types.ObjectId, ref: 'User' },
        reviewedAt: Date,
        decisionNotes: String,
        exemptionsApplied: [{
            section: String,
            reason: String,
            partialRelease: Boolean
        }]
    },
    responseDetails: {
        respondedAt: Date,
        responseMethod: {
            type: String,
            enum: ['EMAIL', 'POST', 'IN_PERSON', 'PORTAL']
        },
        feesCharged: Number,
        documentsReleased: [{
            documentId: { type: Schema.Types.ObjectId, ref: 'Document' },
            releaseMethod: String,
            releasedAt: Date
        }]
    },
    appealDetails: {
        appealedAt: Date,
        appealGrounds: String,
        appealDecision: String,
        appealDecidedAt: Date
    },
    metadata: {
        isUrgent: { type: Boolean, default: false },
        urgencyReason: String,
        relatedDsarId: String,
        retentionOverride: Boolean,
        manualTrackingRequired: { type: Boolean, default: false }
    },
    audit: {
        createdBy: { type: Schema.Types.ObjectId, ref: 'User', required: true },
        createdAt: { type: Date, default: Date.now },
        updatedBy: { type: Schema.Types.ObjectId, ref: 'User' },
        updatedAt: { type: Date, default: Date.now }
    }
}, { _id: true });

// Main Case Schema
const CaseSchema = new Schema({
    tenantId: {
        type: String,
        required: [true, 'Tenant ID is required for multi-tenant isolation'],
        index: true,
        validate: {
            validator: validateTenantId,
            message: 'Tenant ID must match pattern: tenant_[8-32 alphanumeric chars]'
        }
    },

    caseNumber: {
        type: String,
        required: [true, 'Case number is required'],
        unique: true,
        index: true,
        validate: {
            validator: validateCaseNumber,
            message: 'Case number must match format: XX-YYYY-ZZZZ or XX-YYYY-ZZZZ-XX'
        }
    },

    title: {
        type: String,
        required: [true, 'Case title is required'],
        trim: true,
        minlength: [3, 'Case title must be at least 3 characters'],
        maxlength: [200, 'Case title cannot exceed 200 characters']
    },

    status: {
        type: String,
        enum: {
            values: Object.values(CASE_STATUSES),
            message: 'Status must be one of: PRE_INTAKE, ACTIVE, LEGAL_HOLD, CLOSED'
        },
        default: CASE_STATUSES.PRE_INTAKE,
        index: true
    },

    // Parties involved in the matter
    client: {
        name: {
            type: String,
            required: [true, 'Client name is required'],
            trim: true,
            minlength: [2, 'Client name must be at least 2 characters'],
            maxlength: [100, 'Client name cannot exceed 100 characters']
        },
        entityId: {
            type: String,
            trim: true,
            match: [/^[A-Z0-9_-]{8,20}$/, 'Entity ID must be 8-20 alphanumeric characters']
        },
        clientReference: String,
        contactDetails: {
            email: {
                type: String,
                lowercase: true,
                match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please provide a valid email address']
            },
            phone: String
        },
        // PAIA-specific client fields
        paiaDesignation: {
            isInformationOfficer: { type: Boolean, default: false },
            deputyOfficers: [{ type: Schema.Types.ObjectId, ref: 'User' }],
            lastDesignationUpdate: Date
        }
    },

    opponents: [{
        name: {
            type: String,
            required: [true, 'Opponent name is required'],
            trim: true,
            minlength: [2, 'Opponent name must be at least 2 characters'],
            maxlength: [100, 'Opponent name cannot exceed 100 characters']
        },
        blindIndex: {
            type: String,
            index: true,
            required: [true, 'Blind index is required for searchable encryption']
        },
        role: {
            type: String,
            enum: ['ADVERSE_PARTY', 'THIRD_PARTY', 'WITNESS', 'EXPERT'],
            default: 'ADVERSE_PARTY'
        },
        entityId: String,
        // PAIA tracking for third parties
        paiaRelevant: { type: Boolean, default: false },
        paiaConsentObtained: Boolean,
        consentRecordId: String
    }],

    // Legal team assignment
    legalTeam: [{
        userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
        role: {
            type: String,
            enum: ['LEAD_ATTORNEY', 'ASSOCIATE', 'PARALEGAL', 'SUPPORT_STAFF', 'INFORMATION_OFFICER'],
            required: true
        },
        assignedDate: { type: Date, default: Date.now },
        isActive: { type: Boolean, default: true },
        // PAIA responsibilities
        paiaResponsibilities: [{
            type: String,
            enum: ['REQUEST_PROCESSING', 'APPEAL_HANDLING', 'EXEMPTION_REVIEW', 'DISCLOSURE_AUTHORITY']
        }]
    }],

    // Matter details
    matterDetails: {
        jurisdiction: String,
        courtOrTribunal: String,
        matterType: {
            type: String,
            enum: ['LITIGATION', 'TRANSACTIONAL', 'ADVISORY', 'REGULATORY', 'COMPLIANCE']
        },
        description: String,
        openingDate: { type: Date, default: Date.now },
        estimatedCloseDate: Date,
        actualCloseDate: Date,
        valueAtRisk: Number,
        currency: { type: String, default: 'ZAR' },
        // PAIA matter classification
        paiaClassification: {
            type: String,
            enum: ['ROUTINE_DISCLOSURE', 'CONDITIONAL_DISCLOSURE', 'PROTECTED_DISCLOSURE'],
            default: 'ROUTINE_DISCLOSURE'
        }
    },

    // PAIA Request Tracking
    paiaRequests: [PaiaRequestSchema],

    // PAIA Statistics and Tracking
    paiaTracking: {
        totalRequests: { type: Number, default: 0 },
        pendingRequests: { type: Number, default: 0 },
        avgResponseTimeDays: Number,
        lastRequestDate: Date,
        exemptionUsage: {
            section14: { type: Number, default: 0 }, // Protection of privacy
            section34: { type: Number, default: 0 }, // Commercial information
            section37: { type: Number, default: 0 }, // Legal privilege
            other: { type: Number, default: 0 }
        },
        appealRate: Number,
        complianceScore: Number
    },

    // Conflict Metadata with enhanced tracking
    conflictStatus: {
        checked: {
            type: Boolean,
            default: false,
            index: true
        },
        checkInitiatedAt: Date,
        clearanceDate: Date,
        clearedBy: { type: Schema.Types.ObjectId, ref: 'User' },
        clearanceMethod: {
            type: String,
            enum: ['AUTOMATED', 'MANUAL_REVIEW', 'OVERRIDE', 'WAIVER']
        },
        clearanceNotes: String,
        foundConflicts: [{
            type: Schema.Types.ObjectId,
            ref: 'Conflict',
            index: true
        }],
        screeningHash: String // Hash of screening parameters for audit
    },

    // Compliance metadata
    compliance: {
        popiaConsentObtained: { type: Boolean, default: false },
        consentRecordId: String,
        lpcRule7Compliant: { type: Boolean, default: false },
        paiaManualUrl: String, // Link to PAIA manual for this matter type
        riskLevel: {
            type: String,
            enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
            default: 'MEDIUM'
        },
        // ECT Act compliance
        ectCompliant: { type: Boolean, default: false },
        signatureVerification: {
            method: String,
            verifiedAt: Date,
            verificationId: String
        },
        // FICA/LPC markers
        ficaVerified: Boolean,
        trustAccountRequired: { type: Boolean, default: false },
        trustAccountId: String
    },

    // Audit trail
    audit: {
        createdBy: { type: Schema.Types.ObjectId, ref: 'User', required: true },
        createdAt: { type: Date, default: Date.now },
        updatedBy: { type: Schema.Types.ObjectId, ref: 'User' },
        updatedAt: { type: Date, default: Date.now },
        version: { type: Number, default: 1 },
        // PAIA-specific audit
        paiaNotifications: [{
            type: String,
            enum: ['REQUEST_RECEIVED', 'DEADLINE_WARNING', 'RESPONSE_SENT', 'APPEAL_FILED']
        }]
    },

    // Metadata
    metadata: {
        isConfidential: { type: Boolean, default: true },
        classification: {
            type: String,
            enum: ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED', 'PAIA_PROTECTED'],
            default: 'CONFIDENTIAL'
        },
        tags: [String],
        retentionPolicy: {
            rule: {
                type: String,
                enum: ['LPC_6YR', 'COMPANIES_ACT_7YR', 'PAIA_5YR', 'PERMANENT'],
                default: 'LPC_6YR'
            },
            disposalDate: Date,
            paiaOverride: Boolean // PAIA requests can override normal retention
        },
        // Data residency compliance
        storageLocation: {
            dataResidencyCompliance: {
                type: String,
                enum: ['ZA_ONLY', 'EU_ADEQUATE', 'GLOBAL'],
                default: 'ZA_ONLY'
            },
            primaryRegion: { type: String, default: 'af-south-1' },
            backupRegion: String
        }
    }
}, {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
    id: false
});

// ==============================================
// VIRTUAL PROPERTIES
// ==============================================

CaseSchema.virtual('isConflictFree').get(function () {
    return this.conflictStatus.checked &&
        (!this.conflictStatus.foundConflicts || this.conflictStatus.foundConflicts.length === 0);
});

CaseSchema.virtual('requiresManualConflictReview').get(function () {
    return this.conflictStatus.checked &&
        this.conflictStatus.foundConflicts &&
        this.conflictStatus.foundConflicts.length > 0 &&
        !this.conflictStatus.clearanceDate;
});

CaseSchema.virtual('daysOpen').get(function () {
    if (!this.matterDetails.openingDate) return 0;
    const diff = new Date() - this.matterDetails.openingDate;
    return Math.floor(diff / (1000 * 60 * 60 * 24));
});

CaseSchema.virtual('paiaDeadlineApproaching').get(function () {
    if (!this.paiaRequests || this.paiaRequests.length === 0) return false;

    const pendingRequests = this.paiaRequests.filter(req =>
        req.status === PAIA_REQUEST_STATUSES.PENDING ||
        req.status === PAIA_REQUEST_STATUSES.IN_REVIEW
    );

    if (pendingRequests.length === 0) return false;

    const now = new Date();
    const threeDaysFromNow = new Date(now.getTime() + (3 * 24 * 60 * 60 * 1000));

    return pendingRequests.some(req =>
        req.statutoryDeadline && req.statutoryDeadline <= threeDaysFromNow
    );
});

CaseSchema.virtual('hasActivePaiaRequests').get(function () {
    if (!this.paiaRequests || this.paiaRequests.length === 0) return false;

    const activeStatuses = [
        PAIA_REQUEST_STATUSES.PENDING,
        PAIA_REQUEST_STATUSES.IN_REVIEW,
        PAIA_REQUEST_STATUSES.APPEALED
    ];

    return this.paiaRequests.some(req => activeStatuses.includes(req.status));
});

// ==============================================
// INDEXES
// ==============================================

CaseSchema.index({ tenantId: 1, status: 1 });
CaseSchema.index({ tenantId: 1, 'client.name': 1 });
CaseSchema.index({ tenantId: 1, 'conflictStatus.checked': 1 });
CaseSchema.index({ 'conflictStatus.clearanceDate': 1 });
CaseSchema.index({ 'audit.createdAt': -1 });
CaseSchema.index({ caseNumber: 1 }, { unique: true });
CaseSchema.index({ 'paiaRequests.status': 1 });
CaseSchema.index({ 'paiaRequests.statutoryDeadline': 1 });
CaseSchema.index({ 'metadata.storageLocation.dataResidencyCompliance': 1 });

// ==============================================
// STATIC METHODS
// ==============================================

/**
 * Find cases by tenant with conflict status filter
 * @param {string} tenantId - Tenant identifier
 * @param {Object} options - Query options
 * @returns {Promise<Array>} - Cases matching criteria
 */
CaseSchema.statics.findByTenant = async function (tenantId, options = {}) {
    if (!tenantId || !validateTenantId(tenantId)) {
        throw new Error('Valid tenant ID is required');
    }

    const query = { tenantId };
    const page = parseInt(options.page, 10) || 1;
    const limit = parseInt(options.limit, 10) || 50;
    const skip = (page - 1) * limit;

    // Apply filters
    if (options.status) query.status = options.status;
    if (options.conflictChecked !== undefined) {
        query['conflictStatus.checked'] = options.conflictChecked;
    }
    if (options.hasPaiaRequests !== undefined) {
        if (options.hasPaiaRequests) {
            query['paiaRequests.0'] = { $exists: true };
        } else {
            query.paiaRequests = { $size: 0 };
        }
    }
    if (options.search) {
        query.$or = [
            { caseNumber: new RegExp(options.search, 'i') },
            { title: new RegExp(options.search, 'i') },
            { 'client.name': new RegExp(options.search, 'i') }
        ];
    }

    const cases = await this.find(query)
        .sort({ 'audit.createdAt': -1 })
        .skip(skip)
        .limit(limit)
        .populate('conflictStatus.foundConflicts', 'conflictReference severity status')
        .populate('legalTeam.userId', 'name email role')
        .populate('paiaRequests.reviewDetails.reviewedBy', 'name email')
        .lean();

    return cases;
};

/**
 * Run conflict screening for a case
 * @param {string} caseId - Case identifier
 * @returns {Promise<Object>} - Screening results
 */
CaseSchema.statics.runConflictScreening = async function (caseId) {
    const caseDoc = await this.findById(caseId);
    if (!caseDoc) {
        throw new Error('Case not found');
    }

    return caseDoc.performConflictScreening();
};

/**
 * Add PAIA request to a case
 * @param {string} caseId - Case identifier
 * @param {Object} paiaRequestData - PAIA request data
 * @returns {Promise<Object>} - Updated case with new request
 */
CaseSchema.statics.addPaiaRequest = async function (caseId, paiaRequestData) {
    const caseDoc = await this.findById(caseId);
    if (!caseDoc) {
        throw new Error('Case not found');
    }

    // Generate unique request ID
    const requestId = `PAIA-${caseDoc.caseNumber}-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;

    const paiaRequest = {
        ...paiaRequestData,
        requestId,
        audit: {
            createdBy: paiaRequestData.createdBy || caseDoc.audit.createdBy,
            createdAt: new Date()
        }
    };

    caseDoc.paiaRequests.push(paiaRequest);

    // Update PAIA tracking statistics
    caseDoc.paiaTracking.totalRequests += 1;
    caseDoc.paiaTracking.pendingRequests += 1;
    caseDoc.paiaTracking.lastRequestDate = new Date();

    await caseDoc.save();

    // Log to audit ledger
    try {
        const AuditLedger = mongoose.model('AuditLedger');
        await AuditLedger.log({
            tenantId: caseDoc.tenantId,
            userId: paiaRequestData.createdBy,
            action: 'PAIA_REQUEST_CREATED',
            resourceType: 'Case',
            resourceId: caseDoc._id,
            metadata: {
                requestId,
                caseNumber: caseDoc.caseNumber,
                requesterType: paiaRequest.requesterType
            }
        });
    } catch (error) {
        console.error('Failed to log PAIA request to audit ledger:', error.message);
    }

    return {
        caseId: caseDoc._id,
        caseNumber: caseDoc.caseNumber,
        requestId,
        statutoryDeadline: paiaRequest.statutoryDeadline,
        message: 'PAIA request added successfully'
    };
};

/**
 * Get cases with approaching PAIA deadlines
 * @param {string} tenantId - Tenant identifier
 * @param {number} daysThreshold - Days threshold for deadline warning
 * @returns {Promise<Array>} - Cases with approaching deadlines
 */
CaseSchema.statics.getCasesWithApproachingPaiaDeadlines = async function (tenantId, daysThreshold = 3) {
    const thresholdDate = new Date();
    thresholdDate.setDate(thresholdDate.getDate() + daysThreshold);

    const cases = await this.find({
        tenantId,
        'paiaRequests.status': { $in: ['PENDING', 'IN_REVIEW'] },
        'paiaRequests.statutoryDeadline': { $lte: thresholdDate, $gte: new Date() }
    })
        .select('caseNumber title paiaRequests')
        .populate('paiaRequests', 'requestId status statutoryDeadline requesterDetails.name')
        .lean();

    return cases.map(caseDoc => ({
        caseId: caseDoc._id,
        caseNumber: caseDoc.caseNumber,
        title: caseDoc.title,
        pendingRequests: caseDoc.paiaRequests.filter(req =>
            req.statutoryDeadline <= thresholdDate &&
            (req.status === 'PENDING' || req.status === 'IN_REVIEW')
        )
    }));
};

// ==============================================
// INSTANCE METHODS
// ==============================================

/**
 * Perform comprehensive conflict screening
 * @returns {Promise<Object>} - Screening results
 */
CaseSchema.methods.performConflictScreening = async function () {
    // Check if screening was already performed
    if (this.conflictStatus.checked && !this._forceRescreen) {
        return {
            alreadyScreened: true,
            foundConflicts: this.conflictStatus.foundConflicts,
            clearanceDate: this.conflictStatus.clearanceDate
        };
    }

    // Record screening initiation
    this.conflictStatus.checkInitiatedAt = new Date();

    // Extract party names for screening
    const partyNames = [];
    if (this.client?.name) {
        partyNames.push(this.client.name.trim());
    }

    if (this.opponents?.length) {
        this.opponents.forEach(opponent => {
            if (opponent.name?.trim()) {
                partyNames.push(opponent.name.trim());
            }
        });
    }

    // Extract legal team members for screening
    const involvedUsers = [];
    if (this.legalTeam?.length) {
        this.legalTeam.forEach(member => {
            if (member.userId && member.isActive !== false) {
                involvedUsers.push(member.userId);
            }
        });
    }

    // If no parties to screen, mark as checked
    if (partyNames.length === 0 && involvedUsers.length === 0) {
        this.conflictStatus.checked = true;
        this.conflictStatus.clearanceDate = new Date();
        this.conflictStatus.clearanceMethod = 'AUTOMATED';
        this.conflictStatus.clearanceNotes = 'No parties or legal team members to screen';

        await this.save();
        return {
            screened: true,
            foundConflicts: [],
            message: 'No parties to screen'
        };
    }

    // Generate screening hash for audit
    const screeningData = JSON.stringify({
        partyNames: partyNames.sort(),
        involvedUsers: involvedUsers.sort(),
        timestamp: new Date().toISOString()
    });

    this.conflictStatus.screeningHash = crypto
        .createHash('sha256')
        .update(screeningData)
        .digest('hex')
        .substring(0, 32);

    // Perform screening using Conflict model
    try {
        const Conflict = mongoose.model('Conflict');
        const identifiedConflicts = await Conflict.screenForConflicts(
            this.tenantId,
            {
                partyNames,
                involvedUsers
            }
        );

        const foundConflicts = identifiedConflicts || [];
        const criticalConflicts = [];
        const blockingConflicts = [];

        let result;

        if (foundConflicts.length > 0) {
            // Categorize conflicts by severity
            foundConflicts.forEach(conflict => {
                if (conflict.severity === CONFLICT_SEVERITIES.CRITICAL ||
                    conflict.severity === CONFLICT_SEVERITIES.HIGH) {
                    criticalConflicts.push(conflict);

                    // Check if conflict is blocking (not resolved)
                    if (conflict.status !== RESOLVED_STATUS) {
                        blockingConflicts.push(conflict);
                    }
                }
            });

            // Store found conflicts
            this.conflictStatus.foundConflicts = foundConflicts.map(c => c._id);

            // If there are blocking conflicts, prevent case activation
            if (blockingConflicts.length > 0 && this.status === CASE_STATUSES.PRE_INTAKE) {
                this.status = CASE_STATUSES.LEGAL_HOLD;

                const blockingRefs = blockingConflicts.map(c => c.conflictReference);

                this.conflictStatus.clearanceNotes = `Blocked by unresolved conflicts: ${blockingRefs.join(', ')}`;

                result = {
                    screened: true,
                    foundConflicts: foundConflicts.length,
                    criticalConflicts: criticalConflicts.length,
                    blockingConflicts: blockingConflicts.length,
                    status: 'BLOCKED',
                    blockingReferences: blockingRefs,
                    message: 'Case placed on legal hold due to unresolved high-severity conflicts'
                };
            } else {
                // Non-blocking conflicts found
                this.conflictStatus.checked = true;
                this.conflictStatus.clearanceDate = new Date();
                this.conflictStatus.clearanceMethod = 'AUTOMATED';
                this.conflictStatus.clearanceNotes = 'Conflicts detected but not blocking';

                result = {
                    screened: true,
                    foundConflicts: foundConflicts.length,
                    criticalConflicts: criticalConflicts.length,
                    status: 'CLEARED_WITH_CONFLICTS',
                    message: 'Case cleared with non-blocking conflicts'
                };
            }
        } else {
            // No conflicts found
            this.conflictStatus.checked = true;
            this.conflictStatus.clearanceDate = new Date();
            this.conflictStatus.clearanceMethod = 'AUTOMATED';
            this.conflictStatus.clearanceNotes = 'No conflicts detected';
            this.conflictStatus.foundConflicts = [];

            result = {
                screened: true,
                foundConflicts: 0,
                status: 'CLEARED',
                message: 'No conflicts detected'
            };
        }

        // Save the case with updated conflict status
        await this.save();

        // Populate conflict details in response
        if (foundConflicts.length > 0) {
            const populatedConflicts = await Conflict.find({
                _id: { $in: this.conflictStatus.foundConflicts }
            }).select('conflictReference severity status conflictType description');

            result.conflictDetails = populatedConflicts;
        }

        return result;

    } catch (error) {
        // Log error but don't fail the case creation
        console.error(`Conflict screening error for case ${this.caseNumber}:`, error.message);

        // Mark screening as attempted but failed
        this.conflictStatus.checked = false;
        this.conflictStatus.clearanceNotes = `Screening failed: ${error.message}`;

        await this.save();

        return {
            screened: false,
            error: error.message,
            message: 'Conflict screening failed, manual review required'
        };
    }
};

/**
 * Update PAIA request status
 * @param {string} requestId - PAIA request ID
 * @param {Object} updateData - Update data including status and review details
 * @returns {Promise<Object>} - Update result
 */
CaseSchema.methods.updatePaiaRequestStatus = async function (requestId, updateData) {
    const requestIndex = this.paiaRequests.findIndex(req => req.requestId === requestId);

    if (requestIndex === -1) {
        throw new Error('PAIA request not found');
    }

    const request = this.paiaRequests[requestIndex];
    const previousStatus = request.status;

    // Update request
    Object.assign(request, updateData);
    request.audit.updatedAt = new Date();
    request.audit.updatedBy = updateData.updatedBy;

    // If status is changing from pending/in_review, update counters
    if ((previousStatus === 'PENDING' || previousStatus === 'IN_REVIEW') &&
        !['PENDING', 'IN_REVIEW'].includes(updateData.status)) {
        this.paiaTracking.pendingRequests = Math.max(0, this.paiaTracking.pendingRequests - 1);
    }

    // Update response timestamp if applicable
    if (updateData.status === 'GRANTED' || updateData.status === 'DENIED' ||
        updateData.status === 'PARTIALLY_GRANTED') {
        request.responseDetails = request.responseDetails || {};
        request.responseDetails.respondedAt = new Date();
    }

    await this.save();

    // Log to audit ledger
    try {
        const AuditLedger = mongoose.model('AuditLedger');
        await AuditLedger.log({
            tenantId: this.tenantId,
            userId: updateData.updatedBy,
            action: 'PAIA_REQUEST_UPDATED',
            resourceType: 'Case',
            resourceId: this._id,
            metadata: {
                requestId,
                caseNumber: this.caseNumber,
                previousStatus,
                newStatus: updateData.status,
                decisionNotes: updateData.decisionNotes
            }
        });
    } catch (error) {
        console.error('Failed to log PAIA request update to audit ledger:', error.message);
    }

    return {
        success: true,
        caseId: this._id,
        caseNumber: this.caseNumber,
        requestId,
        previousStatus,
        newStatus: updateData.status,
        updatedAt: request.audit.updatedAt
    };
};

/**
 * Manually clear conflicts for a case
 * @param {Object} clearanceData - Clearance data
 * @returns {Promise<Object>} - Clearance result
 */
CaseSchema.methods.manuallyClearConflicts = async function (clearanceData) {
    if (!clearanceData.clearedBy) {
        throw new Error('Cleared by user ID is required');
    }

    if (!clearanceData.clearanceMethod) {
        throw new Error('Clearance method is required');
    }

    this.conflictStatus.checked = true;
    this.conflictStatus.clearanceDate = new Date();
    this.conflictStatus.clearedBy = clearanceData.clearedBy;
    this.conflictStatus.clearanceMethod = clearanceData.clearanceMethod;
    this.conflictStatus.clearanceNotes = clearanceData.clearanceNotes ||
        `Manually cleared by user: ${clearanceData.clearedBy}`;

    // If case was on legal hold due to conflicts, update status
    if (this.status === CASE_STATUSES.LEGAL_HOLD &&
        this.conflictStatus.foundConflicts &&
        this.conflictStatus.foundConflicts.length > 0) {
        this.status = CASE_STATUSES.PRE_INTAKE;
    }

    await this.save();

    return {
        success: true,
        caseId: this._id,
        caseNumber: this.caseNumber,
        clearedAt: this.conflictStatus.clearanceDate,
        clearedBy: this.conflictStatus.clearedBy,
        clearanceMethod: this.conflictStatus.clearanceMethod,
        previousStatus: clearanceData.previousStatus,
        newStatus: this.status
    };
};

// ==============================================
// MIDDLEWARE: AUTOMATED CONFLICT SCREENING
// ==============================================

CaseSchema.pre('validate', async function (next) {
    // Only screen new cases or cases being activated
    if (!this.isNew && !this.isModified('status')) {
        return next();
    }

    // If case is being closed, skip conflict screening
    if (this.status === CASE_STATUSES.CLOSED) {
        return next();
    }

    // Force rescreen if moving from legal hold to active
    if (this.isModified('status') &&
        this._previousStatus === CASE_STATUSES.LEGAL_HOLD &&
        this.status === CASE_STATUSES.ACTIVE) {
        this._forceRescreen = true;
    }

    // Store previous status for reference
    if (this.isModified('status')) {
        this._previousStatus = this._originalStatus;
    }

    try {
        const screeningResult = await this.performConflictScreening();

        // Handle blocking conflicts
        if (screeningResult.status === 'BLOCKED') {
            const error = new Error('BLOCKING_CONFLICT_DETECTED');
            error.code = 'CONFLICT_BLOCK';
            error.conflicts = screeningResult.blockingReferences;
            error.message = `Case cannot proceed due to unresolved conflicts: ${screeningResult.blockingReferences.join(', ')}`;
            error.severity = 'HIGH';

            // Set case to legal hold
            this.status = CASE_STATUSES.LEGAL_HOLD;
            return next(error);
        }

        // Set case to active if it was in PRE_INTAKE and no blocking conflicts
        if (this.isNew &&
            this.status === CASE_STATUSES.PRE_INTAKE &&
            screeningResult.status !== 'BLOCKED') {
            this.status = CASE_STATUSES.ACTIVE;
        }

        next();
    } catch (error) {
        // Log error but allow case to proceed with manual review flag
        console.error('Pre-validate conflict screening failed:', error.message);

        this.conflictStatus.checked = false;
        this.conflictStatus.clearanceNotes = `Automated screening failed: ${error.message}`;

        // If this is a new case, set to LEGAL_HOLD for manual review
        if (this.isNew && this.status === CASE_STATUSES.PRE_INTAKE) {
            this.status = CASE_STATUSES.LEGAL_HOLD;
        }

        next();
    }
});

CaseSchema.pre('save', function (next) {
    // Update audit trail
    if (this.isNew) {
        this.audit.createdAt = new Date();
    } else {
        this.audit.updatedAt = new Date();
        this.audit.version += 1;
    }

    // Validate legal team has at least one active member
    if (this.status === CASE_STATUSES.ACTIVE &&
        (!this.legalTeam || this.legalTeam.length === 0)) {
        return next(new Error('Active cases must have at least one legal team member assigned'));
    }

    // Validate PAIA statutory deadlines are in the future
    if (this.paiaRequests && this.paiaRequests.length > 0) {
        for (const request of this.paiaRequests) {
            if (request.statutoryDeadline && request.statutoryDeadline < new Date()) {
                return next(new Error(`PAIA request ${request.requestId} has a past statutory deadline`));
            }
        }
    }

    next();
});

// ==============================================
// MERMAID DIAGRAM: Case Lifecycle with PAIA Integration
// ==============================================

/*
```mermaid
flowchart TD
    A[Case Intake] --> B{Conflict Screening}
    B -->|No Conflicts| C[Case Active]
    B -->|Conflicts Found| D[Legal Hold]
    D --> E[Manual Review]
    E -->|Resolved| C
    E -->|Not Resolved| F[Case Rejected]
    
    C --> G[PAIA Request Received]
    G --> H{Request Type}
    H -->|Routine| I[Auto-Process]
    H -->|Complex| J[Manual Review]
    
    I --> K[Generate Response<br>within 30 days]
    J --> L[Legal & Compliance<br>Review]
    L --> M[Apply Exemptions<br>if applicable]
    M --> N[Prepare Response]
    
    K --> O[Response Sent]
    N --> O
    
    O --> P[Update PAIA Tracking]
    P --> Q[Audit Trail Updated]
    Q --> R[Case Continues]
    
    style A fill:#e1f5fe
    style G fill:#f3e5f5
    style O fill:#e8f5e8
    style D fill:#ffebee*/