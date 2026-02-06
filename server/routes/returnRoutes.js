/*
 * File: server/routes/returnRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Return of Service Gateway (Tenant-Scoped). Manages the upload, verification, and retrieval of Sheriff Returns (Proof of Service).
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @legal,@sheriff-ops,@platform
 * MIGRATION_NOTES: Migrated to Joi Validation; strict outcome classification.
 * TESTS: mocha@9.x + chai@4.x; tests file association and verification workflows.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/returns', returnRoutes);
//
// Functionality:
//   - POST /: Upload a new Return of Service (PDF).
//   - GET /case/:caseId: List all returns for a specific matter.
//   - PATCH /:id/verify: Admin/Lawyer verification of the return.
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const returnController = require('../controllers/returnController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');
// Note: 'upload' middleware (Multer) is usually injected before validation for multipart forms
// const upload = require('../middleware/uploadMiddleware'); 

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const createReturnSchema = {
    caseId: Joi.string().required(),
    dispatchId: Joi.string().required(), // Link to the instruction
    outcome: Joi.string().valid('PERSONAL_SERVICE', 'DOMICILE_SERVICE', 'NON_SERVICE', 'MOVED').required(),
    serviceDate: Joi.date().iso().required(),
    recipientName: Joi.string().allow('').optional(), // If personal service
    notes: Joi.string().max(1000).allow('').optional()
    // 'file' is handled by multer, validation checks existence in controller
};

const verifyReturnSchema = {
    status: Joi.string().valid('VERIFIED', 'REJECTED').required(),
    rejectionReason: Joi.string().when('status', { is: 'REJECTED', then: Joi.required(), otherwise: Joi.optional() })
};

const idSchema = {
    id: Joi.string().required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   POST /api/returns
 * @desc    Upload Return of Service
 * @access  Sheriff, Admin
 */
router.post(
    '/',
    protect,
    requireSameTenant,
    restrictTo('admin', 'sheriff', 'superadmin'),
    // upload.single('file'), // Uncomment if using Multer here
    validate(createReturnSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await returnController.createReturn(req, res);

            // Audit the Evidence Creation
            await emitAudit(req, {
                resource: 'legal_evidence',
                action: 'UPLOAD_RETURN',
                severity: 'INFO',
                summary: `Return uploaded: ${req.body.outcome}`,
                metadata: {
                    caseId: req.body.caseId,
                    dispatchId: req.body.dispatchId
                }
            });

            if (!res.headersSent && result) res.status(201).json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'RETURN_UPLOAD_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/returns/case/:id
 * @desc    List Returns for a Case
 * @access  Lawyer, Admin, Client, Sheriff
 */
router.get(
    '/case/:id',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer', 'sheriff', 'client'),
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await returnController.getReturnsByCase(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'RETURN_LIST_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/returns/:id
 * @desc    Get Single Return Details (and File URL)
 * @access  Lawyer, Admin, Client
 */
router.get(
    '/:id',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer', 'client'),
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await returnController.getReturnById(req, res);

            // Audit Access to Evidence (Chain of Custody)
            await emitAudit(req, {
                resource: 'legal_evidence',
                action: 'VIEW_RETURN',
                severity: 'INFO',
                metadata: { returnId: req.params.id }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'RETURN_GET_FAILED';
            next(err);
        }
    }
);

/**
 * @route   PATCH /api/returns/:id/verify
 * @desc    Verify Return Quality (Lawyer Approval)
 * @access  Lawyer, Admin
 */
router.patch(
    '/:id/verify',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer'),
    validate(idSchema, 'params'),
    validate(verifyReturnSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await returnController.verifyReturn(req, res);

            // Audit Verification
            await emitAudit(req, {
                resource: 'legal_evidence',
                action: 'VERIFY_RETURN',
                severity: req.body.status === 'REJECTED' ? 'WARN' : 'INFO',
                summary: `Return ${req.body.status}`,
                metadata: { returnId: req.params.id, reason: req.body.rejectionReason }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'RETURN_VERIFY_FAILED';
            next(err);
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const returnRoutes = require('./server/routes/returnRoutes');
app.use('/api/returns', returnRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates outcome types (Personal vs Domicile).
3. [ ] Restricts uploading to 'sheriff'/'admin' roles.
4. [ ] Restricts verification to 'lawyer'/'admin' roles.
5. [ ] Emits Audit Events for upload and verification (Evidence tracking).
*/