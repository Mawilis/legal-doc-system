/*
 * File: server/routes/bundleRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Bundle Gateway (Tenant-Scoped). Orchestrates the compilation of multiple documents into a single, indexed PDF Court Bundle.
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @security,@legal,@platform
 * MIGRATION_NOTES: Migrated to Joi Validation; enforced doc array limits to prevent memory overflows.
 * TESTS: mocha@9.x + chai@4.x; tests bundle compilation triggers and permission gates.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/bundles', bundleRoutes);
//
// Functionality:
//   - POST /: Create a new Court Bundle (Async Job Trigger).
//   - GET /:id: Check status / Download final PDF.
//   - POST /:id/regenerate: Re-compile if documents changed.
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const bundleController = require('../controllers/bundleController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const createBundleSchema = {
    caseId: Joi.string().required(), // Link to Legal Matter/Case
    name: Joi.string().min(3).max(200).required(),
    description: Joi.string().max(500).allow('').optional(),
    documents: Joi.array().items(Joi.object({
        documentId: Joi.string().required(),
        order: Joi.number().required(),
        section: Joi.string().valid('A', 'B', 'C', 'D', 'NONE').default('NONE')
    })).min(1).max(200).required(), // Limit 200 docs per bundle to prevent OOM
    options: Joi.object({
        pagination: Joi.boolean().default(true), // Page numbering
        tableOfContents: Joi.boolean().default(true), // Auto-generate index
        watermark: Joi.string().allow('').optional()
    }).default({})
};

const idSchema = {
    id: Joi.string().required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   POST /api/bundles
 * @desc    Initialize Court Bundle Generation (Async)
 * @access  Lawyer, Paralegal, Admin
 */
router.post(
    '/',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer', 'paralegal'),
    validate(createBundleSchema, 'body'),
    async (req, res, next) => {
        try {
            // This usually triggers a BullMQ job
            const result = await bundleController.createBundle(req, res);

            // Audit the Heavy Operation
            await emitAudit(req, {
                resource: 'doc_processor',
                action: 'GENERATE_BUNDLE',
                severity: 'INFO',
                summary: `Bundle '${req.body.name}' queued for compilation`,
                metadata: {
                    caseId: req.body.caseId,
                    docCount: req.body.documents.length
                }
            });

            if (!res.headersSent && result) res.status(201).json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'BUNDLE_CREATE_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/bundles/:id
 * @desc    Get Bundle Metadata & Status
 * @access  Lawyer, Paralegal, Admin
 */
router.get(
    '/:id',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer', 'paralegal', 'client'),
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await bundleController.getBundle(req, res);

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'BUNDLE_GET_FAILED';
            next(err);
        }
    }
);

/**
 * @route   POST /api/bundles/:id/regenerate
 * @desc    Re-compile an existing bundle (e.g., after doc updates)
 * @access  Lawyer, Paralegal, Admin
 */
router.post(
    '/:id/regenerate',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer', 'paralegal'),
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await bundleController.regenerateBundle(req, res);

            await emitAudit(req, {
                resource: 'doc_processor',
                action: 'REGENERATE_BUNDLE',
                severity: 'INFO',
                metadata: { bundleId: req.params.id }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'BUNDLE_REGEN_FAILED';
            next(err);
        }
    }
);

/**
 * @route   DELETE /api/bundles/:id
 * @desc    Archive/Delete a Bundle
 * @access  Admin, Lawyer
 */
router.delete(
    '/:id',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer'),
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await bundleController.deleteBundle(req, res);

            await emitAudit(req, {
                resource: 'doc_repository',
                action: 'DELETE_BUNDLE',
                severity: 'WARN',
                metadata: { bundleId: req.params.id }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'BUNDLE_DELETE_FAILED';
            next(err);
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const bundleRoutes = require('./server/routes/bundleRoutes');
app.use('/api/bundles', bundleRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates document list size (max 200 items) to prevent server overload.
3. [ ] Restricts creation/regeneration to 'lawyer'/'paralegal'/'admin'.
4. [ ] Emits Audit Events for heavy processing tasks (Generate/Regenerate).
5. [ ] Ensures client can read/download but not regenerate/delete.
*/