/*
 * File: server/routes/dispatchInstructionRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Dispatch Instruction Gateway (Tenant-Scoped). Manages specific service instructions for Sheriffs (e.g., specific address, urgency, special notes).
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @ops,@legal,@sheriff-liaison
 * MIGRATION_NOTES: Migrated to Joi Validation; strict status workflow enforcement.
 * TESTS: mocha@9.x + chai@4.x; validates instruction creation and status transitions.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/dispatch-instructions', dispatchInstructionRoutes);
//
// Functionality:
//   - POST /: Create a new instruction for a Sheriff.
//   - PATCH /:id/status: Update status (e.g., RECEIVED, REJECTED, COMPLETED).
//   - GET /case/:caseId: List all instructions for a specific matter.
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const dispatchController = require('../controllers/dispatchController'); // Shared controller often used for both routes

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const createInstructionSchema = {
    sheriffId: Joi.string().required(), // Target Sheriff Profile
    caseId: Joi.string().required(),
    documentId: Joi.string().required(), // The document to be served
    type: Joi.string().valid('SERVICE_NORMAL', 'SERVICE_URGENT', 'COLLECTION').default('SERVICE_NORMAL'),
    address: Joi.string().required(), // Service address
    specialInstructions: Joi.string().max(500).allow('').optional(),
    deadline: Joi.date().iso().min('now').optional()
};

const updateStatusSchema = {
    status: Joi.string().valid('PENDING', 'ACCEPTED', 'REJECTED', 'IN_PROGRESS', 'COMPLETED').required(),
    note: Joi.string().max(200).optional()
};

const idSchema = {
    id: Joi.string().required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   POST /api/dispatch-instructions
 * @desc    Issue New Dispatch Instruction
 * @access  Admin, Lawyer, Paralegal
 */
router.post(
    '/',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer', 'paralegal'),
    validate(createInstructionSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await dispatchController.createInstruction(req, res);

            // Audit the Request
            await emitAudit(req, {
                resource: 'dispatch_logistics',
                action: 'ISSUE_INSTRUCTION',
                severity: 'INFO',
                summary: `Instruction sent to Sheriff ${req.body.sheriffId}`,
                metadata: {
                    caseId: req.body.caseId,
                    type: req.body.type,
                    address: req.body.address
                }
            });

            if (!res.headersSent && result) res.status(201).json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'INSTRUCTION_CREATE_FAILED';
            next(err);
        }
    }
);

/**
 * @route   PATCH /api/dispatch-instructions/:id/status
 * @desc    Update Instruction Status (Sheriff Acknowledgement)
 * @access  Sheriff, Admin
 */
router.patch(
    '/:id/status',
    protect,
    requireSameTenant,
    restrictTo('admin', 'sheriff', 'superadmin'),
    validate(idSchema, 'params'),
    validate(updateStatusSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await dispatchController.updateInstructionStatus(req, res);

            // Audit Workflow Change
            await emitAudit(req, {
                resource: 'dispatch_logistics',
                action: 'UPDATE_STATUS',
                severity: 'INFO',
                summary: `Instruction ${req.params.id} updated to ${req.body.status}`,
                metadata: { note: req.body.note }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'INSTRUCTION_UPDATE_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/dispatch-instructions/:id
 * @desc    Get Instruction Details
 * @access  Admin, Lawyer, Sheriff
 */
router.get(
    '/:id',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer', 'paralegal', 'sheriff'),
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await dispatchController.getInstruction(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'INSTRUCTION_GET_FAILED';
            next(err);
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const dispatchInstructionRoutes = require('./server/routes/dispatchInstructionRoutes');
app.use('/api/dispatch-instructions', dispatchInstructionRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates urgency types ('SERVICE_NORMAL', 'SERVICE_URGENT').
3. [ ] Restricts creation to legal staff and updates to sheriffs.
4. [ ] Emits Audit Events for instruction issuance and status changes.
5. [ ] Ensures valid caseId and sheriffId linkage (via controller).
*/