/*
 * File: server/routes/workflowRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Workflow Gateway (Tenant-Scoped). Manages Business Process Automation (BPA) rules, triggers, and action chains.
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @platform,@product,@automation
 * MIGRATION_NOTES: Migrated to Joi Validation; enforced strict trigger/action typing.
 * TESTS: mocha@9.x + chai@4.x; tests rule execution logic and circular dependency prevention.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/workflows', workflowRoutes);
//
// Functionality:
//   - POST /: Create a new automation rule (e.g., "On Case Close -> Send Email").
//   - POST /:id/trigger: Manually trigger a workflow (Test/Run).
//   - GET /history: View execution logs of automations.
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const workflowController = require('../controllers/workflowController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const createWorkflowSchema = {
    name: Joi.string().min(3).max(100).required(),
    description: Joi.string().max(500).allow('').optional(),
    trigger: Joi.object({
        event: Joi.string().valid('CASE_CREATED', 'CASE_CLOSED', 'INVOICE_OVERDUE', 'DOC_UPLOADED').required(),
        conditions: Joi.object().optional() // JSON Logic filters
    }).required(),
    actions: Joi.array().items(Joi.object({
        type: Joi.string().valid('SEND_EMAIL', 'CREATE_TASK', 'GENERATE_DOC', 'UPDATE_STATUS').required(),
        config: Joi.object().required()
    })).min(1).required(),
    isActive: Joi.boolean().default(true)
};

const idSchema = {
    id: Joi.string().required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   POST /api/workflows
 * @desc    Define New Automation Rule
 * @access  Admin, SuperAdmin
 */
router.post(
    '/',
    protect,
    requireSameTenant,
    restrictTo('admin', 'superadmin'),
    validate(createWorkflowSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await workflowController.createWorkflow(req, res);

            // Audit the Logic Creation
            await emitAudit(req, {
                resource: 'automation_engine',
                action: 'CREATE_WORKFLOW',
                severity: 'WARN', // Automations can have big impacts
                summary: `New Automation: ${req.body.name}`,
                metadata: { trigger: req.body.trigger.event }
            });

            if (!res.headersSent && result) res.status(201).json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'WORKFLOW_CREATE_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/workflows
 * @desc    List Active Workflows
 * @access  Admin, SuperAdmin
 */
router.get(
    '/',
    protect,
    requireSameTenant,
    restrictTo('admin', 'superadmin'),
    async (req, res, next) => {
        try {
            const result = await workflowController.listWorkflows(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'WORKFLOW_LIST_FAILED';
            next(err);
        }
    }
);

/**
 * @route   POST /api/workflows/:id/trigger
 * @desc    Manually Execute Workflow (Testing/Ad-hoc)
 * @access  Admin Only
 */
router.post(
    '/:id/trigger',
    protect,
    requireSameTenant,
    restrictTo('admin', 'superadmin'),
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await workflowController.triggerWorkflow(req, res);

            await emitAudit(req, {
                resource: 'automation_engine',
                action: 'MANUAL_TRIGGER',
                severity: 'INFO',
                summary: `Workflow ${req.params.id} manually triggered`,
                metadata: { workflowId: req.params.id }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'WORKFLOW_TRIGGER_FAILED';
            next(err);
        }
    }
);

/**
 * @route   DELETE /api/workflows/:id
 * @desc    Delete/Archive Workflow
 * @access  Admin
 */
router.delete(
    '/:id',
    protect,
    requireSameTenant,
    restrictTo('admin', 'superadmin'),
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await workflowController.deleteWorkflow(req, res);

            await emitAudit(req, {
                resource: 'automation_engine',
                action: 'DELETE_WORKFLOW',
                severity: 'WARN',
                metadata: { workflowId: req.params.id }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'WORKFLOW_DELETE_FAILED';
            next(err);
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const workflowRoutes = require('./server/routes/workflowRoutes');
app.use('/api/workflows', workflowRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates trigger events and action types against allowed lists.
3. [ ] Restricts automation management to 'admin' roles.
4. [ ] Allows manual triggering for testing purposes.
5. [ ] Emits WARN audit events for creating or deleting automation rules.
*/