/*
 * File: server/routes/retentionRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Retention Policy Gateway (Tenant-Scoped). Manages data lifecycle, automated archiving, and destruction policies (POPIA/GDPR Compliance).
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @compliance,@legal,@security
 * MIGRATION_NOTES: Migrated to Joi Validation; enforced strict deletion safeguards.
 * TESTS: mocha@9.x + chai@4.x; tests policy application and soft-delete vs hard-delete logic.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/retention', retentionRoutes);
//
// Functionality:
//   - POST /policies: Define a retention rule (e.g., "Archive Closed Cases after 5 years").
//   - POST /execute: Manually trigger a retention sweep (Admin only).
//   - GET /logs: Audit trail of what data was archived/deleted.
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const retentionController = require('../controllers/retentionController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const policySchema = {
    name: Joi.string().required(),
    resourceType: Joi.string().valid('CASE', 'DOCUMENT', 'INVOICE', 'MESSAGE').required(),
    retentionPeriodDays: Joi.number().min(30).max(3650).required(), // Min 30 days, Max 10 years
    action: Joi.string().valid('ARCHIVE', 'SOFT_DELETE', 'HARD_DELETE', 'ANONYMIZE').required(),
    description: Joi.string().max(500).optional()
};

const executeSchema = {
    policyId: Joi.string().required(),
    dryRun: Joi.boolean().default(true) // Safer default
};

const idSchema = {
    id: Joi.string().required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   GET /api/retention/policies
 * @desc    List Active Retention Policies
 * @access  Admin, Compliance Officer
 */
router.get(
    '/policies',
    protect,
    requireSameTenant,
    restrictTo('admin', 'compliance_officer', 'superadmin'),
    async (req, res, next) => {
        try {
            const result = await retentionController.listPolicies(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'RETENTION_LIST_FAILED';
            next(err);
        }
    }
);

/**
 * @route   POST /api/retention/policies
 * @desc    Create/Update Retention Policy
 * @access  Admin, Compliance Officer
 */
router.post(
    '/policies',
    protect,
    requireSameTenant,
    restrictTo('admin', 'compliance_officer', 'superadmin'),
    validate(policySchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await retentionController.createPolicy(req, res);

            // Audit Governance Change
            await emitAudit(req, {
                resource: 'compliance_engine',
                action: 'DEFINE_RETENTION_POLICY',
                severity: 'WARN',
                summary: `Policy '${req.body.name}' created`,
                metadata: {
                    resource: req.body.resourceType,
                    action: req.body.action,
                    period: req.body.retentionPeriodDays
                }
            });

            if (!res.headersSent && result) res.status(201).json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'RETENTION_CREATE_FAILED';
            next(err);
        }
    }
);

/**
 * @route   POST /api/retention/execute
 * @desc    Trigger Retention Sweep (Manual Override)
 * @access  SuperAdmin Only (Dangerous Operation)
 */
router.post(
    '/execute',
    protect,
    requireSameTenant,
    restrictTo('superadmin'), // Highest privilege only
    validate(executeSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await retentionController.executePolicy(req, res);

            // Critical Audit: Data Destruction/Movement
            await emitAudit(req, {
                resource: 'compliance_engine',
                action: 'EXECUTE_RETENTION',
                severity: req.body.dryRun ? 'INFO' : 'CRITICAL',
                summary: `Retention sweep triggered for Policy ${req.body.policyId}`,
                metadata: { dryRun: req.body.dryRun }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'RETENTION_EXEC_FAILED';
            next(err);
        }
    }
);

/**
 * @route   DELETE /api/retention/policies/:id
 * @desc    Delete Retention Policy
 * @access  Admin, Compliance Officer
 */
router.delete(
    '/policies/:id',
    protect,
    requireSameTenant,
    restrictTo('admin', 'compliance_officer', 'superadmin'),
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await retentionController.deletePolicy(req, res);

            await emitAudit(req, {
                resource: 'compliance_engine',
                action: 'DELETE_RETENTION_POLICY',
                severity: 'WARN',
                metadata: { policyId: req.params.id }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'RETENTION_DELETE_FAILED';
            next(err);
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const retentionRoutes = require('./server/routes/retentionRoutes');
app.use('/api/retention', retentionRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates retention periods (min 30 days, max 10 years).
3. [ ] Restricts execution of sweeps to 'superadmin' only.
4. [ ] Defaults manual execution to 'dryRun: true' for safety.
5. [ ] Emits CRITICAL audit events when data is actually deleted/archived.
*/