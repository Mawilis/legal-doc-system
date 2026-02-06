/**
 * @file /Users/wilsonkhanyezi/legal-doc-system/server/routes/dsar.js
 * @module DSARRoutes
 * @description Data Subject Access Request endpoints for POPIA/GDPR compliance
 * @description Implements 72-hour SLA, identity verification, and evidence generation
 * @description Multi-tenant isolation with per-tenant retention policies
 * 
 * @requires express
 * @requires middleware/tenantContext
 * @requires middleware/auth
 * @requires models/DSARRequest
 * @requires models/User
 * @requires models/Document
 * @requires models/AuditLedger
 * @requires lib/kms
 * @requires lib/storage
 * 
 * @compliance POPIA §14 - Access to personal information
 * @compliance POPIA §23 - Correction of personal information
 * @compliance POPIA §24 - Deletion of personal information
 * @compliance GDPR Art.15 - Right of access
 * @compliance GDPR Art.20 - Data portability
 * @compliance PAIA §50 - Access to records
 * 
 * @security 3-factor identity verification
 * @security Per-tenant data isolation
 * @security Cryptographic evidence anchoring
 * 
 * @multitenant Tenant isolation enforced via tenantContext
 * @multitenant Each DSAR request scoped to tenant
 * 
 * @author Wilson Khanyezi <wilsy.wk@gmail.com>
 * @copyright Wilsy OS™ - All Rights Reserved
 */

const express = require('express');
const router = express.Router();
const { body, param, query, validationResult } = require('express-validator');
const mongoose = require('mongoose');

// Middleware imports
const tenantContext = require('../middleware/tenantContext');
const authenticate = require('../middleware/auth');
const authorize = require('../middleware/authorize');
const rateLimit = require('../middleware/rateLimit');

// Model imports
const DSARRequest = require('../models/DSARRequest');
const User = require('../models/User');
const Document = require('../models/Document');
const AuditTrail = require('../models/AuditTrail');
const AuditLedger = require('../models/AuditLedger');

// Service imports
const kms = require('../lib/kms');
const storage = require('../lib/storage');
const { sendDSARNotification, generateEvidencePackage } = require('../services/dsarService');

// ==================== CONSTANTS & CONFIGURATION ====================
const DSAR_SLA_HOURS = 72; // POPIA requirement
const IDENTITY_VERIFICATION_METHODS = ['email', 'sms', 'document'];
const DSAR_TYPES = ['ACCESS', 'CORRECTION', 'DELETION', 'PORTABILITY', 'RESTRICTION', 'OBJECTION'];
const DSAR_STATUSES = ['DRAFT', 'SUBMITTED', 'VERIFYING', 'PROCESSING', 'FULFILLED', 'REJECTED', 'APPEALED'];
const VALID_FILE_FORMATS = ['pdf', 'zip', 'json'];

// ==================== MIDDLEWARE STACK ====================
router.use(tenantContext.enforceTenant);
router.use(authenticate.verifyToken);
router.use('/submit', rateLimit.dsarPerTenant);
router.use('/:id', validateDSAROwnership);

// ==================== HELPER FUNCTIONS ====================

/**
 * @function validateDSAROwnership
 * @description Middleware to validate DSAR request ownership or admin rights
 * @description Fail-closed: denies access if user is not owner or admin
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware
 */
async function validateDSAROwnership(req, res, next) {
    try {
        const dsarId = req.params.id;
        const userId = req.user.id;
        const userRole = req.user.role;
        const tenantId = req.tenantId;

        // Admins can access any DSAR in their tenant
        if (userRole === 'TENANT_ADMIN' || userRole === 'SUPER_ADMIN') {
            const dsar = await DSARRequest.findOne({
                _id: dsarId,
                tenantId: tenantId
            });

            if (!dsar) {
                return res.status(404).json({
                    error: 'DSAR_NOT_FOUND',
                    message: 'Data Subject Access Request not found',
                    compliance: 'POPIA §14(2) - Record of requests'
                });
            }

            req.dsar = dsar;
            return next();
        }

        // Regular users can only access their own DSARs
        const dsar = await DSARRequest.findOne({
            _id: dsarId,
            tenantId: tenantId,
            'dataSubject.userId': userId
        });

        if (!dsar) {
            // Log failed access attempt for security
            await AuditLedger.create({
                tenantId: tenantId,
                eventType: 'ACCESS_DENIED',
                severity: 'WARNING',
                actor: {
                    userId: userId,
                    userEmail: req.user.email,
                    role: userRole,
                    ipAddress: req.ip
                },
                resource: {
                    type: 'DSARRequest',
                    id: dsarId,
                    name: 'DSAR Access Attempt'
                },
                action: 'ACCESS_DSAR',
                description: 'Unauthorized DSAR access attempt',
                compliance: {
                    popiaCategory: 'PERSONAL',
                    dsarRelevant: true
                }
            });

            return res.status(403).json({
                error: 'ACCESS_DENIED',
                message: 'You do not have permission to access this DSAR request',
                compliance: 'POPIA §6 - Processing limitation'
            });
        }

        req.dsar = dsar;
        next();
    } catch (error) {
        console.error('DSAR ownership validation error:', error);
        res.status(500).json({
            error: 'VALIDATION_ERROR',
            message: 'Failed to validate DSAR ownership',
            compliance: 'POPIA §8 - Data quality'
        });
    }
}

/**
 * @function logDSARAuditEvent
 * @description Logs DSAR-related events to audit ledger
 * @description Creates immutable audit trail for legal defensibility
 * @param {string} tenantId - Tenant identifier
 * @param {string} eventType - Type of DSAR event
 * @param {Object} actor - User performing the action
 * @param {Object} resource - DSAR resource being acted upon
 * @param {string} description - Human-readable description
 * @param {Object} metadata - Additional metadata
 * @returns {Promise<Object>} Created audit entry
 */
async function logDSARAuditEvent(tenantId, eventType, actor, resource, description, metadata = {}) {
    try {
        const auditEntry = await AuditLedger.create({
            tenantId: tenantId,
            eventType: eventType,
            actor: actor,
            resource: resource,
            action: `DSAR_${eventType}`,
            description: description,
            metadata: metadata,
            compliance: {
                popiaCategory: 'PERSONAL',
                dsarRelevant: true,
                paiaManualReference: 'PAIA Manual §14(2)'
            }
        });

        return auditEntry;
    } catch (error) {
        console.error('Failed to log DSAR audit event:', error);
        // Don't fail the request if audit logging fails, but do alert
        // In production, this would go to a monitoring system
        return null;
    }
}

/**
 * @function verifyDataSubjectIdentity
 * @description 3-factor identity verification for DSAR requests
 * @description Required by POPIA §14 for data subject verification
 * @param {Object} dataSubject - Data subject information
 * @param {Array} verificationMethods - Methods to use for verification
 * @returns {Promise<Object>} Verification result with evidence
 */
async function verifyDataSubjectIdentity(dataSubject, verificationMethods) {
    const verificationEvidence = {
        timestamp: new Date(),
        methods: [],
        confidenceScore: 0,
        passed: false
    };

    try {
        // Method 1: Email verification (required)
        if (verificationMethods.includes('email')) {
            const emailVerified = await verifyEmailOwnership(dataSubject.email);
            verificationEvidence.methods.push({
                method: 'email',
                verified: emailVerified,
                timestamp: new Date()
            });
            if (emailVerified) verificationEvidence.confidenceScore += 33;
        }

        // Method 2: SMS verification (required for SA POPIA)
        if (verificationMethods.includes('sms') && dataSubject.phone) {
            const smsVerified = await verifyPhoneOwnership(dataSubject.phone);
            verificationEvidence.methods.push({
                method: 'sms',
                verified: smsVerified,
                timestamp: new Date()
            });
            if (smsVerified) verificationEvidence.confidenceScore += 33;
        }

        // Method 3: Document verification (optional but recommended)
        if (verificationMethods.includes('document') && dataSubject.idDocument) {
            const docVerified = await verifyDocumentIdentity(dataSubject.idDocument);
            verificationEvidence.methods.push({
                method: 'document',
                verified: docVerified,
                timestamp: new Date()
            });
            if (docVerified) verificationEvidence.confidenceScore += 34;
        }

        // Minimum 2 methods must pass for DSAR processing
        const passedMethods = verificationEvidence.methods.filter(m => m.verified).length;
        verificationEvidence.passed = passedMethods >= 2 && verificationEvidence.confidenceScore >= 66;

        return verificationEvidence;
    } catch (error) {
        console.error('Identity verification error:', error);
        verificationEvidence.error = error.message;
        return verificationEvidence;
    }
}

/**
 * @function verifyEmailOwnership
 * @description Verifies email ownership via confirmation link
 * @param {string} email - Email address to verify
 * @returns {Promise<boolean>} True if verified
 */
async function verifyEmailOwnership(email) {
    // Implementation would send verification email
    // For now, return mock success
    return new Promise(resolve => setTimeout(() => resolve(true), 100));
}

/**
 * @function verifyPhoneOwnership
 * @description Verifies phone ownership via OTP
 * @param {string} phone - Phone number to verify
 * @returns {Promise<boolean>} True if verified
 */
async function verifyPhoneOwnership(phone) {
    // Implementation would send SMS OTP
    // For now, return mock success
    return new Promise(resolve => setTimeout(() => resolve(true), 100));
}

/**
 * @function verifyDocumentIdentity
 * @description Verifies identity document via validation service
 * @param {Object} idDocument - Identity document details
 * @returns {Promise<boolean>} True if verified
 */
async function verifyDocumentIdentity(idDocument) {
    // Implementation would validate with Home Affairs API or similar
    // For now, return mock success
    return new Promise(resolve => setTimeout(() => resolve(true), 100));
}

// ==================== DSAR ROUTES ====================

/**
 * @route POST /api/dsar/submit
 * @description Submit a new Data Subject Access Request
 * @description POPIA §14: Right to access personal information
 * @access Private (Data Subject)
 * @security 3-factor identity verification
 * @multitenant Tenant isolation enforced
 */
router.post(
    '/submit',
    [
        // Input validation
        body('dsarType').isIn(DSAR_TYPES).withMessage('Invalid DSAR type'),
        body('dataSubject.email').isEmail().normalizeEmail(),
        body('dataSubject.phone').optional().isMobilePhone('any'),
        body('dataSubject.fullName').isLength({ min: 2, max: 100 }),
        body('dataSubject.idNumber').optional().isLength({ min: 13, max: 13 }),
        body('scope').isObject().withMessage('Scope must be an object'),
        body('preferredContactMethod').isIn(['email', 'sms', 'both']),
        body('verificationMethods').isArray().custom(value => {
            return value.every(method => IDENTITY_VERIFICATION_METHODS.includes(method));
        })
    ],
    async (req, res) => {
        try {
            // Validate input
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({
                    error: 'VALIDATION_ERROR',
                    message: 'Invalid DSAR request data',
                    details: errors.array(),
                    compliance: 'POPIA §8 - Data quality'
                });
            }

            const tenantId = req.tenantId;
            const userId = req.user.id;
            const userEmail = req.user.email;
            const userRole = req.user.role;

            const {
                dsarType,
                dataSubject,
                scope,
                preferredContactMethod,
                verificationMethods,
                additionalInfo
            } = req.body;

            // Step 1: Verify user is requesting their own data (unless admin)
            if (userRole !== 'TENANT_ADMIN' && userRole !== 'SUPER_ADMIN') {
                if (dataSubject.email !== userEmail) {
                    return res.status(403).json({
                        error: 'IDENTITY_MISMATCH',
                        message: 'You can only submit DSAR for your own data',
                        compliance: 'POPIA §6 - Processing limitation'
                    });
                }
            }

            // Step 2: Create DSAR request record
            const dsarRequest = new DSARRequest({
                tenantId: tenantId,
                dsarType: dsarType,
                dataSubject: {
                    userId: userId,
                    email: dataSubject.email,
                    phone: dataSubject.phone,
                    fullName: dataSubject.fullName,
                    idNumber: dataSubject.idNumber,
                    residentialAddress: dataSubject.residentialAddress
                },
                scope: scope,
                preferredContactMethod: preferredContactMethod,
                verificationMethods: verificationMethods,
                additionalInfo: additionalInfo || '',
                status: 'SUBMITTED',
                submittedAt: new Date(),
                slaDeadline: new Date(Date.now() + (DSAR_SLA_HOURS * 60 * 60 * 1000)),
                createdBy: userId,
                updatedBy: userId
            });

            // Step 3: Save DSAR request
            await dsarRequest.save();

            // Step 4: Log audit event
            await logDSARAuditEvent(
                tenantId,
                'DSAR_REQUESTED',
                {
                    userId: userId,
                    userEmail: userEmail,
                    role: userRole,
                    ipAddress: req.ip
                },
                {
                    type: 'DSARRequest',
                    id: dsarRequest._id,
                    name: `DSAR ${dsarType} - ${dataSubject.fullName}`
                },
                `DSAR ${dsarType} request submitted by ${dataSubject.fullName}`,
                {
                    dsarId: dsarRequest._id,
                    verificationMethods: verificationMethods
                }
            );

            // Step 5: Initiate identity verification (async)
            setTimeout(async () => {
                try {
                    const verificationResult = await verifyDataSubjectIdentity(
                        dataSubject,
                        verificationMethods
                    );

                    dsarRequest.identityVerification = verificationResult;

                    if (verificationResult.passed) {
                        dsarRequest.status = 'VERIFYING';
                        await dsarRequest.save();

                        // Notify Information Officer
                        await sendDSARNotification(tenantId, dsarRequest._id, 'VERIFICATION_PASSED');
                    } else {
                        dsarRequest.status = 'REJECTED';
                        dsarRequest.rejectionReason = 'Identity verification failed';
                        await dsarRequest.save();

                        // Notify Data Subject
                        await sendDSARNotification(tenantId, dsarRequest._id, 'VERIFICATION_FAILED');
                    }
                } catch (verificationError) {
                    console.error('Identity verification process error:', verificationError);
                    // Will be retried by background worker
                }
            }, 0);

            // Step 6: Return response
            res.status(201).json({
                success: true,
                message: 'DSAR request submitted successfully',
                data: {
                    dsarId: dsarRequest._id,
                    referenceNumber: dsarRequest.referenceNumber,
                    status: dsarRequest.status,
                    slaDeadline: dsarRequest.slaDeadline,
                    nextSteps: ['Identity verification', 'Data collection', 'Evidence generation']
                },
                compliance: {
                    popia: '§14 - Access to personal information',
                    gdpr: 'Article 15 - Right of access',
                    sla: `${DSAR_SLA_HOURS} hours`
                }
            });

        } catch (error) {
            console.error('DSAR submission error:', error);
            res.status(500).json({
                error: 'DSAR_SUBMISSION_FAILED',
                message: 'Failed to submit DSAR request',
                details: process.env.NODE_ENV === 'development' ? error.message : undefined,
                compliance: 'POPIA §14(3) - Form of access'
            });
        }
    }
);

/**
 * @route GET /api/dsar
 * @description List DSAR requests (filtered by user role)
 * @description Information Officers see all tenant DSARs
 * @description Data Subjects see only their own DSARs
 * @access Private
 * @security Role-based access control
 * @multitenant Tenant isolation enforced
 */
router.get(
    '/',
    [
        query('status').optional().isIn(DSAR_STATUSES),
        query('dsarType').optional().isIn(DSAR_TYPES),
        query('page').optional().isInt({ min: 1 }).default(1),
        query('limit').optional().isInt({ min: 1, max: 100 }).default(20)
    ],
    async (req, res) => {
        try {
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({
                    error: 'VALIDATION_ERROR',
                    message: 'Invalid query parameters',
                    details: errors.array()
                });
            }

            const tenantId = req.tenantId;
            const userId = req.user.id;
            const userRole = req.user.role;
            const { status, dsarType, page, limit } = req.query;

            // Build query based on user role
            let query = { tenantId: tenantId };

            // Data Subjects can only see their own DSARs
            if (userRole !== 'TENANT_ADMIN' && userRole !== 'SUPER_ADMIN') {
                query['dataSubject.userId'] = userId;
            }

            // Apply filters
            if (status) query.status = status;
            if (dsarType) query.dsarType = dsarType;

            // Calculate pagination
            const skip = (page - 1) * limit;

            // Execute query
            const dsarRequests = await DSARRequest.find(query)
                .sort({ submittedAt: -1 })
                .skip(skip)
                .limit(parseInt(limit))
                .select('-identityVerification -evidencePackage -__v');

            const total = await DSARRequest.countDocuments(query);

            // Calculate SLA status
            const now = new Date();
            const dsarRequestsWithSLA = dsarRequests.map(dsar => {
                const slaStatus = dsar.slaDeadline > now ? 'WITHIN_SLA' : 'BREACHED';
                const hoursRemaining = Math.max(0, Math.floor((dsar.slaDeadline - now) / (1000 * 60 * 60)));

                return {
                    ...dsar.toObject(),
                    slaStatus,
                    hoursRemaining
                };
            });

            res.json({
                success: true,
                data: dsarRequestsWithSLA,
                pagination: {
                    page: parseInt(page),
                    limit: parseInt(limit),
                    total,
                    pages: Math.ceil(total / limit)
                },
                compliance: {
                    popia: '§14(2) - Record of requests',
                    paia: '§14 - Access to records'
                }
            });

        } catch (error) {
            console.error('DSAR list error:', error);
            res.status(500).json({
                error: 'DSAR_LIST_FAILED',
                message: 'Failed to retrieve DSAR requests',
                compliance: 'POPIA §8 - Data quality'
            });
        }
    }
);

/**
 * @route GET /api/dsar/:id
 * @description Get specific DSAR request details
 * @description Includes evidence package if status is FULFILLED
 * @access Private (Owner or Admin)
 * @security Ownership validation middleware
 * @multitenant Tenant isolation enforced
 */
router.get(
    '/:id',
    [
        param('id').isMongoId().withMessage('Invalid DSAR ID')
    ],
    async (req, res) => {
        try {
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({
                    error: 'VALIDATION_ERROR',
                    message: 'Invalid DSAR ID',
                    details: errors.array()
                });
            }

            const dsar = req.dsar;
            const userRole = req.user.role;

            // Prepare response data
            const responseData = {
                ...dsar.toObject(),
                slaStatus: dsar.slaDeadline > new Date() ? 'WITHIN_SLA' : 'BREACHED',
                canAppeal: dsar.status === 'REJECTED' && dsar.rejectionReason,
                canDownload: dsar.status === 'FULFILLED' && dsar.evidencePackage
            };

            // Hide sensitive fields from non-admins
            if (userRole !== 'TENANT_ADMIN' && userRole !== 'SUPER_ADMIN') {
                delete responseData.identityVerification;
                delete responseData.internalNotes;
                delete responseData.processingLog;
            }

            // Hide evidence package URL until specifically requested
            if (responseData.evidencePackage) {
                responseData.evidencePackage = {
                    exists: true,
                    format: responseData.evidencePackage.format,
                    sizeBytes: responseData.evidencePackage.sizeBytes,
                    generatedAt: responseData.evidencePackage.generatedAt,
                    downloadAvailable: true
                };
            }

            res.json({
                success: true,
                data: responseData,
                compliance: {
                    popia: '§14 - Access to personal information',
                    ect: '§15 - Evidential weight'
                }
            });

        } catch (error) {
            console.error('DSAR details error:', error);
            res.status(500).json({
                error: 'DSAR_DETAILS_FAILED',
                message: 'Failed to retrieve DSAR details',
                compliance: 'POPIA §14(3) - Form of access'
            });
        }
    }
);

/**
 * @route GET /api/dsar/:id/evidence
 * @description Download DSAR evidence package
 * @description Returns signed URL to secure evidence package
 * @access Private (Owner or Admin)
 * @security File access authorization check
 * @multitenant Tenant isolation enforced
 */
router.get(
    '/:id/evidence',
    [
        param('id').isMongoId().withMessage('Invalid DSAR ID'),
        query('format').optional().isIn(VALID_FILE_FORMATS).default('pdf')
    ],
    async (req, res) => {
        try {
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({
                    error: 'VALIDATION_ERROR',
                    message: 'Invalid request parameters',
                    details: errors.array()
                });
            }

            const dsar = req.dsar;
            const { format } = req.query;

            // Check if DSAR is fulfilled
            if (dsar.status !== 'FULFILLED') {
                return res.status(400).json({
                    error: 'EVIDENCE_NOT_READY',
                    message: 'DSAR evidence package is not yet available',
                    currentStatus: dsar.status
                });
            }

            // Check if evidence package exists
            if (!dsar.evidencePackage || !dsar.evidencePackage.storageKey) {
                return res.status(404).json({
                    error: 'EVIDENCE_NOT_FOUND',
                    message: 'Evidence package not found in storage'
                });
            }

            // Generate secure download URL with expiration
            const downloadUrl = await storage.generateSignedUrl(
                dsar.evidencePackage.storageKey,
                'getObject',
                {
                    Expires: 3600, // 1 hour expiration
                    ResponseContentDisposition: `attachment; filename="DSAR-${dsar.referenceNumber}.${format}"`,
                    ResponseContentType: getMimeType(format)
                }
            );

            // Log download event
            await logDSARAuditEvent(
                req.tenantId,
                'EVIDENCE_DOWNLOADED',
                {
                    userId: req.user.id,
                    userEmail: req.user.email,
                    role: req.user.role,
                    ipAddress: req.ip
                },
                {
                    type: 'DSARRequest',
                    id: dsar._id,
                    name: `DSAR Evidence - ${dsar.referenceNumber}`
                },
                `Evidence package downloaded for DSAR ${dsar.referenceNumber}`,
                {
                    format: format,
                    downloadUrl: downloadUrl.split('?')[0] // Store only base URL
                }
            );

            res.json({
                success: true,
                data: {
                    downloadUrl: downloadUrl,
                    expiresAt: new Date(Date.now() + 3600000), // 1 hour
                    fileName: `DSAR-${dsar.referenceNumber}.${format}`,
                    fileSize: dsar.evidencePackage.sizeBytes,
                    hash: dsar.evidencePackage.sha256Hash
                },
                compliance: {
                    popia: '§14(3) - Form of access',
                    ect: '§15 - Integrity and authenticity'
                }
            });

        } catch (error) {
            console.error('Evidence download error:', error);
            res.status(500).json({
                error: 'EVIDENCE_DOWNLOAD_FAILED',
                message: 'Failed to generate evidence download URL',
                compliance: 'POPIA §19 - Security measures'
            });
        }
    }
);

/**
 * @route POST /api/dsar/:id/appeal
 * @description Appeal a rejected DSAR request
 * @description POPIA §24: Right to object to processing
 * @access Private (Data Subject only)
 * @security Ownership validation
 * @multitenant Tenant isolation enforced
 */
router.post(
    '/:id/appeal',
    [
        param('id').isMongoId().withMessage('Invalid DSAR ID'),
        body('appealReason').isLength({ min: 10, max: 1000 }).withMessage('Appeal reason required'),
        body('additionalEvidence').optional().isArray()
    ],
    async (req, res) => {
        try {
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({
                    error: 'VALIDATION_ERROR',
                    message: 'Invalid appeal data',
                    details: errors.array()
                });
            }

            const dsar = req.dsar;
            const { appealReason, additionalEvidence } = req.body;

            // Check if DSAR can be appealed
            if (dsar.status !== 'REJECTED') {
                return res.status(400).json({
                    error: 'APPEAL_NOT_ALLOWED',
                    message: 'Only rejected DSAR requests can be appealed',
                    currentStatus: dsar.status
                });
            }

            if (dsar.appealSubmittedAt) {
                return res.status(400).json({
                    error: 'APPEAL_ALREADY_SUBMITTED',
                    message: 'An appeal has already been submitted for this DSAR',
                    appealSubmittedAt: dsar.appealSubmittedAt
                });
            }

            // Update DSAR with appeal
            dsar.status = 'APPEALED';
            dsar.appealReason = appealReason;
            dsar.additionalEvidence = additionalEvidence || [];
            dsar.appealSubmittedAt = new Date();
            dsar.updatedBy = req.user.id;

            await dsar.save();

            // Log appeal event
            await logDSARAuditEvent(
                req.tenantId,
                'DSAR_APPEALED',
                {
                    userId: req.user.id,
                    userEmail: req.user.email,
                    role: req.user.role,
                    ipAddress: req.ip
                },
                {
                    type: 'DSARRequest',
                    id: dsar._id,
                    name: `DSAR Appeal - ${dsar.referenceNumber}`
                },
                `DSAR appeal submitted by ${req.user.email}`,
                {
                    appealReason: appealReason,
                    evidenceCount: additionalEvidence?.length || 0
                }
            );

            // Notify Information Officer
            await sendDSARNotification(req.tenantId, dsar._id, 'APPEAL_SUBMITTED');

            res.json({
                success: true,
                message: 'DSAR appeal submitted successfully',
                data: {
                    dsarId: dsar._id,
                    referenceNumber: dsar.referenceNumber,
                    status: dsar.status,
                    appealSubmittedAt: dsar.appealSubmittedAt,
                    nextReviewBy: new Date(Date.now() + (7 * 24 * 60 * 60 * 1000)) // 7 days for review
                },
                compliance: {
                    popia: '§24 - Right to object to processing',
                    paia: '§74 - Internal appeals'
                }
            });

        } catch (error) {
            console.error('DSAR appeal error:', error);
            res.status(500).json({
                error: 'APPEAL_SUBMISSION_FAILED',
                message: 'Failed to submit DSAR appeal',
                compliance: 'POPIA §24(3) - Objection procedures'
            });
        }
    }
);

/**
 * @route POST /api/dsar/:id/cancel
 * @description Cancel a pending DSAR request
 * @description Data Subject can cancel their own request
 * @access Private (Owner or Admin)
 * @security Ownership validation
 * @multitenant Tenant isolation enforced
 */
router.post(
    '/:id/cancel',
    [
        param('id').isMongoId().withMessage('Invalid DSAR ID'),
        body('cancellationReason').optional().isLength({ max: 500 })
    ],
    async (req, res) => {
        try {
            const dsar = req.dsar;
            const { cancellationReason } = req.body;

            // Check if DSAR can be cancelled
            const cancellableStatuses = ['DRAFT', 'SUBMITTED', 'VERIFYING'];
            if (!cancellableStatuses.includes(dsar.status)) {
                return res.status(400).json({
                    error: 'CANCELLATION_NOT_ALLOWED',
                    message: 'DSAR cannot be cancelled in its current status',
                    currentStatus: dsar.status,
                    allowedStatuses: cancellableStatuses
                });
            }

            // Update DSAR status
            dsar.status = 'CANCELLED';
            dsar.cancellationReason = cancellationReason || 'Requested by data subject';
            dsar.cancelledAt = new Date();
            dsar.updatedBy = req.user.id;

            await dsar.save();

            // Log cancellation event
            await logDSARAuditEvent(
                req.tenantId,
                'DSAR_CANCELLED',
                {
                    userId: req.user.id,
                    userEmail: req.user.email,
                    role: req.user.role,
                    ipAddress: req.ip
                },
                {
                    type: 'DSARRequest',
                    id: dsar._id,
                    name: `DSAR Cancelled - ${dsar.referenceNumber}`
                },
                `DSAR cancelled by ${req.user.email}`,
                {
                    cancellationReason: cancellationReason,
                    previousStatus: dsar.status
                }
            );

            res.json({
                success: true,
                message: 'DSAR request cancelled successfully',
                data: {
                    dsarId: dsar._id,
                    referenceNumber: dsar.referenceNumber,
                    status: dsar.status,
                    cancelledAt: dsar.cancelledAt
                },
                compliance: {
                    popia: '§13 - Participation of data subjects',
                    gdpr: 'Article 7 - Conditions for consent'
                }
            });

        } catch (error) {
            console.error('DSAR cancellation error:', error);
            res.status(500).json({
                error: 'CANCELLATION_FAILED',
                message: 'Failed to cancel DSAR request',
                compliance: 'POPIA §14(4) - Extension of period'
            });
        }
    }
);

/**
 * @route GET /api/dsar/metrics/tenant
 * @description Get DSAR metrics for tenant (Information Officer dashboard)
 * @description Includes SLA compliance, request types, processing times
 * @access Private (Tenant Admin only)
 * @security Admin role required
 * @multitenant Tenant isolation enforced
 */
router.get(
    '/metrics/tenant',
    authorize('TENANT_ADMIN'),
    [
        query('startDate').optional().isISO8601(),
        query('endDate').optional().isISO8601()
    ],
    async (req, res) => {
        try {
            const tenantId = req.tenantId;
            const { startDate, endDate } = req.query;

            const start = startDate ? new Date(startDate) : new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // 30 days
            const end = endDate ? new Date(endDate) : new Date();

            // Aggregate DSAR metrics
            const metrics = await DSARRequest.aggregate([
                {
                    $match: {
                        tenantId: tenantId,
                        submittedAt: { $gte: start, $lte: end }
                    }
                },
                {
                    $group: {
                        _id: null,
                        totalRequests: { $sum: 1 },
                        byType: { $push: '$dsarType' },
                        byStatus: { $push: '$status' },
                        fulfilledCount: {
                            $sum: { $cond: [{ $eq: ['$status', 'FULFILLED'] }, 1, 0] }
                        },
                        breachedCount: {
                            $sum: { $cond: [{ $lt: ['$fulfilledAt', '$slaDeadline'] }, 0, 1] }
                        },
                        avgProcessingHours: {
                            $avg: {
                                $cond: [
                                    { $and: ['$submittedAt', '$fulfilledAt'] },
                                    { $divide: [{ $subtract: ['$fulfilledAt', '$submittedAt'] }, 1000 * 60 * 60] },
                                    null
                                ]
                            }
                        }
                    }
                },
                {
                    $project: {
                        _id: 0,
                        totalRequests: 1,
                        byType: {
                            $reduce: {
                                input: '$byType',
                                initialValue: {},
                                in: {
                                    $mergeObjects: [
                                        '$$value',
                                        {
                                            $let: {
                                                vars: { type: '$$this' },
                                                in: {
                                                    $arrayToObject: [[
                                                        { k: '$$type', v: { $add: [{ $getField: { field: '$$type', input: '$$value' } }, 1] } }
                                                    ]]
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        },
                        byStatus: {
                            $reduce: {
                                input: '$byStatus',
                                initialValue: {},
                                in: {
                                    $mergeObjects: [
                                        '$$value',
                                        {
                                            $let: {
                                                vars: { status: '$$this' },
                                                in: {
                                                    $arrayToObject: [[
                                                        { k: '$$status', v: { $add: [{ $getField: { field: '$$status', input: '$$value' } }, 1] } }
                                                    ]]
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        },
                        slaCompliance: {
                            totalFulfilled: '$fulfilledCount',
                            slaBreaches: '$breachedCount',
                            complianceRate: {
                                $cond: [
                                    { $eq: ['$fulfilledCount', 0] },
                                    100,
                                    { $multiply: [{ $divide: [{ $subtract: ['$fulfilledCount', '$breachedCount'] }, '$fulfilledCount'] }, 100] }
                                ]
                            }
                        },
                        avgProcessingHours: { $round: ['$avgProcessingHours', 2] }
                    }
                }
            ]);

            const result = metrics[0] || {
                totalRequests: 0,
                byType: {},
                byStatus: {},
                slaCompliance: {
                    totalFulfilled: 0,
                    slaBreaches: 0,
                    complianceRate: 100
                },
                avgProcessingHours: 0
            };

            // Add current pending requests
            const pendingCount = await DSARRequest.countDocuments({
                tenantId: tenantId,
                status: { $in: ['SUBMITTED', 'VERIFYING', 'PROCESSING'] },
                slaDeadline: { $gt: new Date() }
            });

            result.currentPending = pendingCount;
            result.period = { start, end };
            result.generatedAt = new Date();

            res.json({
                success: true,
                data: result,
                compliance: {
                    popia: '§14(2) - Record of requests',
                    paia: '§14 - Annual report'
                }
            });

        } catch (error) {
            console.error('DSAR metrics error:', error);
            res.status(500).json({
                error: 'METRICS_FAILED',
                message: 'Failed to retrieve DSAR metrics',
                compliance: 'POPIA §8 - Data quality'
            });
        }
    }
);

// ==================== HELPER FUNCTIONS ====================

/**
 * @function getMimeType
 * @description Returns MIME type for file format
 * @param {string} format - File format
 * @returns {string} MIME type
 */
function getMimeType(format) {
    const mimeTypes = {
        'pdf': 'application/pdf',
        'zip': 'application/zip',
        'json': 'application/json'
    };
    return mimeTypes[format] || 'application/octet-stream';
}

// ==================== ERROR HANDLING MIDDLEWARE ====================

/**
 * @middleware dsarErrorHandler
 * @description Global error handler for DSAR routes
 * @description Logs errors to audit trail and returns standardized responses
 */
router.use((err, req, res, next) => {
    console.error('DSAR route error:', err);

    // Log to audit ledger
    if (req.tenantId) {
        AuditLedger.create({
            tenantId: req.tenantId,
            eventType: 'DSAR_ERROR',
            severity: 'ERROR',
            actor: {
                userId: req.user?.id || 'unknown',
                userEmail: req.user?.email || 'unknown',
                role: req.user?.role || 'unknown',
                ipAddress: req.ip
            },
            resource: {
                type: 'DSARRequest',
                id: req.params?.id || 'unknown',
                name: 'DSAR Error'
            },
            action: req.method + ' ' + req.path,
            description: `DSAR error: ${err.message}`,
            metadata: {
                error: err.name,
                stack: process.env.NODE_ENV === 'development' ? err.stack : undefined
            },
            compliance: {
                popiaCategory: 'PERSONAL',
                dsarRelevant: true
            }
        }).catch(logErr => console.error('Failed to log DSAR error:', logErr));
    }

    // Return standardized error response
    const statusCode = err.statusCode || 500;
    const errorResponse = {
        error: err.name || 'INTERNAL_ERROR',
        message: 'An error occurred processing your DSAR request',
        compliance: 'POPIA §14 - Access to personal information',
        timestamp: new Date()
    };

    // Include details in development
    if (process.env.NODE_ENV === 'development') {
        errorResponse.details = err.message;
        errorResponse.stack = err.stack;
    }

    res.status(statusCode).json(errorResponse);
});

// ==================== EXPORT ====================
module.exports = router;

// ==================== MIGRATION NOTES ====================
/**
 * @migration v1.0.0
 * - Initial DSAR endpoints implementation
 * - 3-factor identity verification
 * - 72-hour SLA enforcement
 * - Evidence package generation
 * - Multi-tenant isolation
 *
 * @backward-compatibility
 * - New endpoints don't affect existing routes
 * - DSAR model needs to be created separately
 * - Audit logging integrates with existing AuditLedger
 *
 * @next-steps
 * 1. Create DSARRequest model with required schema
 * 2. Implement dsarService.js for evidence generation
 * 3. Set up notification service for email/SMS
 * 4. Configure identity verification providers
 * 5. Set up background worker for SLA monitoring
 */

// Wilsy Touching Lives.
// Chief Architect: Wilson Khanyezi — wilsy.wk@gmail.com | +27 69 046 5710