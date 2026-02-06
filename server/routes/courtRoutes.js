/*
 * File: server/routes/courtRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Court Gateway (Tenant-Scoped). Manages court rolls, filing statuses, and integration with external justice systems (e.g., CaseLines).
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @security,@legal,@integration
 * MIGRATION_NOTES: Migrated to Joi Validation; standardized court types (High/Magistrates).
 * TESTS: mocha@9.x + chai@4.x; validates court date scheduling conflicts and roll lookups.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/courts', courtRoutes);
//
// Functionality:
//   - GET /: List available courts (Master Registry).
//   - POST /filing: Submit document to Court Online/CaseLines (Async).
//   - GET /roll: Fetch daily court roll for a specific jurisdiction.
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const courtController = require('../controllers/courtController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const filingSchema = {
    caseId: Joi.string().required(),
    documentId: Joi.string().required(),
    courtId: Joi.string().required(),
    filingType: Joi.string().valid('PLEA', 'NOTICE', 'AFFIDAVIT', 'SUMMONS', 'URGENT_APP').required()
};

const courtRollSchema = {
    courtId: Joi.string().required(),
    date: Joi.date().iso().required(),
    division: Joi.string().optional() // e.g., "Civil", "Criminal"
};

const idSchema = {
    id: Joi.string().required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   GET /api/courts
 * @desc    List Supported Courts (Registry)
 * @access  Authenticated Users
 */
router.get(
    '/',
    protect,
    // No tenant check needed for public/master registry data usually, 
    // but good practice if you have private court configs.
    async (req, res, next) => {
        try {
            const result = await courtController.listCourts(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            next(err);
        }
    }
);

/**
 * @route   POST /api/courts/filing
 * @desc    Submit Document to External Court System
 * @access  Lawyer, Paralegal, Admin
 */
router.post(
    '/filing',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer', 'paralegal'),
    validate(filingSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await courtController.submitFiling(req, res);

            // Audit the External Integration
            await emitAudit(req, {
                resource: 'court_integration',
                action: 'SUBMIT_FILING',
                severity: 'INFO',
                summary: `Document filed to Court ${req.body.courtId}`,
                metadata: {
                    caseId: req.body.caseId,
                    docId: req.body.documentId,
                    type: req.body.filingType
                }
            });

            if (!res.headersSent && result) res.status(202).json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'COURT_FILING_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/courts/roll
 * @desc    Fetch Court Roll (Daily Schedule)
 * @access  Lawyer, Admin
 */
router.get(
    '/roll',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer'),
    validate(courtRollSchema, 'query'),
    async (req, res, next) => {
        try {
            const result = await courtController.getCourtRoll(req, res);

            // Light audit
            await emitAudit(req, {
                resource: 'court_integration',
                action: 'VIEW_ROLL',
                severity: 'INFO',
                metadata: { courtId: req.query.courtId, date: req.query.date }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'COURT_ROLL_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/courts/filing/:id/status
 * @desc    Check Status of External Filing
 * @access  Lawyer, Paralegal
 */
router.get(
    '/filing/:id/status',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer', 'paralegal'),
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await courtController.getFilingStatus(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'FILING_STATUS_FAILED';
            next(err);
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const courtRoutes = require('./server/routes/courtRoutes');
app.use('/api/courts', courtRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates filing types against allowed court procedures.
3. [ ] Restricts filings to legal staff ('lawyer', 'paralegal').
4. [ ] Emits Audit Events for external submissions (Chain of Evidence).
5. [ ] Returns 202 Accepted for async filing submissions.
*/