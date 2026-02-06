/*
 * File: server/routes/standardsRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Standards Gateway (Tenant-Scoped). Manages Legal Precedents and Document Templates with variable injection support.
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @legal,@content-ops
 * MIGRATION_NOTES: Migrated to Joi Validation; enforced variable syntax checks.
 * TESTS: mocha@9.x + chai@4.x; tests template variable parsing and storage.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/standards', standardsRoutes);
//
// Functionality:
//   - POST /: Create a new legal precedent/template.
//   - GET /: List available templates (filtered by category).
//   - POST /:id/render: Preview template with dummy data.
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const standardsController = require('../controllers/standardsController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const createStandardSchema = {
    title: Joi.string().min(5).max(200).required(),
    category: Joi.string().valid('CONTRACT', 'NOTICE', 'PLEADING', 'LETTER', 'AFFIDAVIT').required(),
    content: Joi.string().required(), // HTML or Markdown content
    variables: Joi.array().items(Joi.string()).optional(), // e.g., ['clientName', 'address']
    version: Joi.string().pattern(/^\d+\.\d+$/).default('1.0')
};

const renderSchema = {
    data: Joi.object().required() // Key-value pairs matching variables
};

const idSchema = {
    id: Joi.string().required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   POST /api/standards
 * @desc    Create New Legal Standard (Precedent)
 * @access  Admin, Lawyer (Partner)
 */
router.post(
    '/',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer'),
    validate(createStandardSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await standardsController.createStandard(req, res);

            // Audit the Knowledge Asset
            await emitAudit(req, {
                resource: 'legal_standards',
                action: 'CREATE_TEMPLATE',
                severity: 'INFO',
                summary: `New Precedent: ${req.body.title}`,
                metadata: { category: req.body.category, version: req.body.version }
            });

            if (!res.headersSent && result) res.status(201).json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'STD_CREATE_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/standards
 * @desc    List Legal Standards
 * @access  Authenticated Users
 */
router.get(
    '/',
    protect,
    requireSameTenant,
    async (req, res, next) => {
        try {
            const result = await standardsController.listStandards(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'STD_LIST_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/standards/:id
 * @desc    Get Single Standard Details
 * @access  Authenticated Users
 */
router.get(
    '/:id',
    protect,
    requireSameTenant,
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await standardsController.getStandardById(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'STD_GET_FAILED';
            next(err);
        }
    }
);

/**
 * @route   POST /api/standards/:id/render
 * @desc    Render/Preview Template
 * @access  Lawyer, Paralegal
 */
router.post(
    '/:id/render',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer', 'paralegal'),
    validate(idSchema, 'params'),
    validate(renderSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await standardsController.renderStandard(req, res);
            // No audit needed for preview rendering usually
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'STD_RENDER_FAILED';
            next(err);
        }
    }
);

/**
 * @route   PUT /api/standards/:id
 * @desc    Update Standard (New Version)
 * @access  Admin, Lawyer
 */
router.put(
    '/:id',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer'),
    validate(idSchema, 'params'),
    validate(createStandardSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await standardsController.updateStandard(req, res);

            await emitAudit(req, {
                resource: 'legal_standards',
                action: 'UPDATE_TEMPLATE',
                severity: 'INFO',
                summary: `Precedent updated: ${req.body.title}`,
                metadata: { version: req.body.version }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'STD_UPDATE_FAILED';
            next(err);
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const standardsRoutes = require('./server/routes/standardsRoutes');
app.use('/api/standards', standardsRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates template content presence.
3. [ ] Restricts creation/updates to 'lawyer'/'admin'.
4. [ ] Allows all staff to list/view templates.
5. [ ] Emits Audit Events for creating/updating precedents.
*/