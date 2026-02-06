/*
 * File: server/routes/attemptRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Service Attempt Gateway (Tenant-Scoped). Manages the chain of evidence for "Attempts to Serve" legal documents.
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @security,@legal,@sheriff-ops
 * MIGRATION_NOTES: Migrated to Joi Validation; strict geospatial recording enforced.
 * TESTS: mocha@9.x + chai@4.x; validates attempt sequencing (cannot have Attempt 2 without Attempt 1).
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/attempts', attemptRoutes);
//
// Functionality:
//   - POST /:documentId: Log a new attempt to serve (date, location, outcome).
//   - GET /:documentId: Retrieve full attempt history for a specific legal process.
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const attemptController = require('../controllers/attemptController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const logAttemptSchema = {
    attemptNumber: Joi.number().min(1).max(10).required(),
    attemptDate: Joi.date().iso().required(),
    outcome: Joi.string().valid(
        'NO_ANSWER',
        'PREMISES_LOCKED',
        'MOVED',
        'REFUSED_ENTRY',
        'SUCCESSFUL',
        'OTHER'
    ).required(),
    location: Joi.object({
        lat: Joi.number().min(-90).max(90).required(),
        lng: Joi.number().min(-180).max(180).required(),
        address: Joi.string().required()
    }).required(),
    notes: Joi.string().max(500).allow('').optional(),
    photoEvidence: Joi.string().uri().optional() // URL to S3 blob
};

const documentIdSchema = {
    documentId: Joi.string().required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   POST /api/attempts/:documentId
 * @desc    Log a new Service Attempt (Sheriff/Server)
 * @access  Sheriff, Admin
 */
router.post(
    '/:documentId',
    protect,
    requireSameTenant,
    restrictTo('admin', 'sheriff'), // Lawyers read, Sheriffs write
    validate(documentIdSchema, 'params'),
    validate(logAttemptSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await attemptController.logAttempt(req, res);

            // Audit the attempt (Chain of Evidence)
            await emitAudit(req, {
                resource: 'legal_process',
                action: 'LOG_ATTEMPT',
                severity: 'INFO',
                summary: `Service Attempt #${req.body.attemptNumber} logged`,
                metadata: {
                    docId: req.params.documentId,
                    outcome: req.body.outcome,
                    gps: req.body.location
                }
            });

            if (!res.headersSent && result) res.status(201).json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'ATTEMPT_LOG_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/attempts/:documentId
 * @desc    View Attempt History (Chain of Evidence)
 * @access  Admin, Lawyer, Sheriff, Client
 */
router.get(
    '/:documentId',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer', 'sheriff', 'client'),
    validate(documentIdSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await attemptController.getHistory(req, res);

            // Read-only access usually doesn't need heavy auditing unless sensitive
            // We'll skip audit here for performance, or use a lightweight access log if required.

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'ATTEMPT_HISTORY_FAILED';
            next(err);
        }
    }
);

/**
 * @route   DELETE /api/attempts/:id
 * @desc    Strike an erroneous attempt record (Requires Justification)
 * @access  Admin only
 */
router.delete(
    '/:id',
    protect,
    requireSameTenant,
    restrictTo('admin', 'superadmin'),
    async (req, res, next) => {
        try {
            const result = await attemptController.strikeAttempt(req, res);

            // Critical Audit: Altering legal history
            await emitAudit(req, {
                resource: 'legal_process',
                action: 'STRIKE_ATTEMPT',
                severity: 'WARN',
                summary: 'Service attempt record removed',
                metadata: { attemptId: req.params.id }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'ATTEMPT_DELETE_FAILED';
            next(err);
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const attemptRoutes = require('./server/routes/attemptRoutes');
app.use('/api/attempts', attemptRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates GPS coordinates for every attempt (Proof of presence).
3. [ ] Restricts writing attempts to 'sheriff'/'admin' roles only.
4. [ ] Allows 'client' role to read history (Transparency).
5. [ ] Emits Audit Event on creation and deletion of attempts.
*/