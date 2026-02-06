/*
 * File: server/routes/trackingRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Tracking Gateway (Tenant-Scoped). Collects telemetry and UX metrics (e.g., "User clicked Help button").
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @product,@ux,@privacy
 * MIGRATION_NOTES: Migrated to Joi Validation; batched processing implemented.
 * TESTS: mocha@9.x + chai@4.x; tests event batch ingestion and anonymization.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/tracking', trackingRoutes);
//
// Functionality:
//   - POST /event: Log a single user action (e.g., button click).
//   - POST /batch: Log multiple actions (bulk upload for performance).
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const trackingController = require('../controllers/trackingController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant } = require('../middleware/rbacMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const eventSchema = {
    category: Joi.string().required(), // e.g., 'NAVIGATION', 'FEATURE_USE', 'ERROR'
    action: Joi.string().required(),   // e.g., 'CLICKED_BTN', 'VIEWED_PAGE'
    label: Joi.string().allow('').optional(),
    value: Joi.number().optional(),    // e.g., Duration in ms
    metadata: Joi.object().optional()  // Custom JSON data
};

const batchEventSchema = {
    events: Joi.array().items(eventSchema).min(1).max(100).required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   POST /api/tracking/event
 * @desc    Log Single User Activity
 * @access  Authenticated Users
 */
router.post(
    '/event',
    protect,
    requireSameTenant,
    validate(eventSchema, 'body'),
    async (req, res, next) => {
        try {
            // Fire-and-forget pattern often used here, but we await for reliability in prod
            const result = await trackingController.trackEvent(req, res);

            // Note: Tracking events are NOT audited to prevent infinite loops and log bloat.

            if (!res.headersSent && result) res.status(201).json({ status: 'success' });
        } catch (err) {
            // Tracking failures should generally not break the UI
            console.error('Tracking Error:', err.message);
            res.status(200).json({ status: 'ignored' });
        }
    }
);

/**
 * @route   POST /api/tracking/batch
 * @desc    Log Multiple User Activities (Performance Optimized)
 * @access  Authenticated Users
 */
router.post(
    '/batch',
    protect,
    requireSameTenant,
    validate(batchEventSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await trackingController.trackBatch(req, res);
            if (!res.headersSent && result) res.status(201).json({ status: 'success', count: result.count });
        } catch (err) {
            console.error('Batch Tracking Error:', err.message);
            res.status(200).json({ status: 'ignored' });
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const trackingRoutes = require('./server/routes/trackingRoutes');
app.use('/api/tracking', trackingRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates event categories and structure.
3. [ ] Implements error suppression (res.status(200)) to prevent UI crashes if telemetry fails.
4. [ ] Supports batched events for reduced network overhead.
5. [ ] Does NOT emit audit logs for these events (too noisy).
*/