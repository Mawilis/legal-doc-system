/*
 * File: server/routes/eventRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Event Gateway (Tenant-Scoped). Manages the Legal Diary (Court Dates, Deadlines, Meetings).
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @legal,@ops,@platform
 * MIGRATION_NOTES: Migrated to Joi Validation; standardized event types.
 * TESTS: mocha@9.x + chai@4.x; tests conflict detection and recurring event logic.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/events', eventRoutes);
//
// Functionality:
//   - POST /: Create a new calendar event (Court Date, Deadline).
//   - GET /: Fetch events for a date range (Month/Week view).
//   - PATCH /:id/reschedule: Move an event (Requires audit trail).
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const eventController = require('../controllers/eventController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const createEventSchema = {
    title: Joi.string().required(),
    type: Joi.string().valid('COURT_DATE', 'DEADLINE', 'MEETING', 'INTERNAL', 'REMINDER').required(),
    caseId: Joi.string().optional(), // Link to legal matter
    start: Joi.date().iso().required(),
    end: Joi.date().iso().min(Joi.ref('start')).required(),
    attendees: Joi.array().items(Joi.string().email()).optional(),
    location: Joi.string().allow('').optional(),
    description: Joi.string().max(1000).allow('').optional(),
    isPrivate: Joi.boolean().default(false)
};

const dateRangeSchema = {
    start: Joi.date().iso().required(),
    end: Joi.date().iso().min(Joi.ref('start')).required(),
    userId: Joi.string().optional() // Filter by user (defaults to self)
};

const rescheduleSchema = {
    newStart: Joi.date().iso().required(),
    newEnd: Joi.date().iso().min(Joi.ref('newStart')).required(),
    reason: Joi.string().required() // Mandatory reason for audit
};

const idSchema = {
    id: Joi.string().required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   POST /api/events
 * @desc    Schedule New Event
 * @access  Lawyer, Paralegal, Admin
 */
router.post(
    '/',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer', 'paralegal'),
    validate(createEventSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await eventController.createEvent(req, res);

            // Audit: Especially important for Court Dates
            await emitAudit(req, {
                resource: 'legal_diary',
                action: 'CREATE_EVENT',
                severity: req.body.type === 'COURT_DATE' ? 'WARN' : 'INFO',
                summary: `Scheduled ${req.body.type}: ${req.body.title}`,
                metadata: { caseId: req.body.caseId, date: req.body.start }
            });

            if (!res.headersSent && result) res.status(201).json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'EVENT_CREATE_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/events
 * @desc    Get Calendar Events (Range)
 * @access  Authenticated Users
 */
router.get(
    '/',
    protect,
    requireSameTenant,
    validate(dateRangeSchema, 'query'),
    async (req, res, next) => {
        try {
            const result = await eventController.getEvents(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'EVENT_LIST_FAILED';
            next(err);
        }
    }
);

/**
 * @route   PATCH /api/events/:id/reschedule
 * @desc    Reschedule Event (Move Date)
 * @access  Lawyer, Admin
 */
router.patch(
    '/:id/reschedule',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer'), // Only pros can move court dates
    validate(idSchema, 'params'),
    validate(rescheduleSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await eventController.rescheduleEvent(req, res);

            // Critical Audit: Moving dates is risky
            await emitAudit(req, {
                resource: 'legal_diary',
                action: 'RESCHEDULE_EVENT',
                severity: 'WARN',
                summary: `Event ${req.params.id} rescheduled`,
                metadata: {
                    newDate: req.body.newStart,
                    reason: req.body.reason
                }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'EVENT_RESCHEDULE_FAILED';
            next(err);
        }
    }
);

/**
 * @route   DELETE /api/events/:id
 * @desc    Cancel Event
 * @access  Lawyer, Admin
 */
router.delete(
    '/:id',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer'),
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await eventController.deleteEvent(req, res);

            await emitAudit(req, {
                resource: 'legal_diary',
                action: 'CANCEL_EVENT',
                severity: 'INFO',
                metadata: { eventId: req.params.id }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'EVENT_DELETE_FAILED';
            next(err);
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const eventRoutes = require('./server/routes/eventRoutes');
app.use('/api/events', eventRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates start/end dates (End must be after Start).
3. [ ] Restricts rescheduling to 'lawyer'/'admin'.
4. [ ] Requires a 'reason' for rescheduling (Audit requirement).
5. [ ] Emits WARN audit event for moving Court Dates.
*/