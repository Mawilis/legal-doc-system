/*
 * File: server/routes/feeRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Fee Gateway (Tenant-Scoped). Manages billing tariffs, custom fee agreements, and automated cost calculations.
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @finance,@legal,@compliance
 * MIGRATION_NOTES: Migrated to Joi Validation; strict currency formatting enforcement.
 * TESTS: mocha@9.x + chai@4.x; validates tariff application logic and rate overrides.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/fees', feeRoutes);
//
// Functionality:
//   - POST /: Define a new fee structure (Hourly, Fixed, Tariff).
//   - GET /: List available fee structures.
//   - POST /calculate: Estimate costs for a specific task/duration.
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const feeController = require('../controllers/feeController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const feeStructureSchema = {
    name: Joi.string().required(), // e.g., "Senior Partner 2026"
    type: Joi.string().valid('HOURLY', 'FIXED', 'TARIFF', 'CONTINGENCY').required(),
    amount: Joi.number().min(0).required(), // Rate or Fixed Amount
    currency: Joi.string().valid('ZAR', 'USD', 'EUR').default('ZAR'),
    applicableTo: Joi.array().items(Joi.string().valid('CONSULTATION', 'DRAFTING', 'COURT_APPEARANCE', 'TRAVEL', 'ALL')).required(),
    effectiveDate: Joi.date().iso().default(Date.now)
};

const calculateSchema = {
    feeStructureId: Joi.string().required(),
    units: Joi.number().min(0.1).required(), // Hours or Item count
    unitType: Joi.string().valid('HOUR', 'PAGE', 'KM', 'ITEM').required()
};

const idSchema = {
    id: Joi.string().required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   POST /api/fees
 * @desc    Create/Update Fee Structure
 * @access  Admin, Finance
 */
router.post(
    '/',
    protect,
    requireSameTenant,
    restrictTo('admin', 'finance', 'superadmin'),
    validate(feeStructureSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await feeController.createFeeStructure(req, res);

            // Audit the Governance Change
            await emitAudit(req, {
                resource: 'fee_registry',
                action: 'CREATE_FEE_STRUCTURE',
                severity: 'WARN',
                summary: `New Fee Structure: ${req.body.name}`,
                metadata: {
                    type: req.body.type,
                    amount: req.body.amount,
                    currency: req.body.currency
                }
            });

            if (!res.headersSent && result) res.status(201).json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'FEE_CREATE_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/fees
 * @desc    List Fee Structures
 * @access  Authenticated Users
 */
router.get(
    '/',
    protect,
    requireSameTenant,
    async (req, res, next) => {
        try {
            const result = await feeController.listFees(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'FEE_LIST_FAILED';
            next(err);
        }
    }
);

/**
 * @route   POST /api/fees/calculate
 * @desc    Calculate Estimated Cost (Utility)
 * @access  Lawyer, Paralegal, Finance
 */
router.post(
    '/calculate',
    protect,
    requireSameTenant,
    restrictTo('admin', 'lawyer', 'paralegal', 'finance'),
    validate(calculateSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await feeController.calculateCost(req, res);
            // No audit needed for simple calculation utility
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'FEE_CALC_FAILED';
            next(err);
        }
    }
);

/**
 * @route   DELETE /api/fees/:id
 * @desc    Archive Fee Structure
 * @access  Admin Only
 */
router.delete(
    '/:id',
    protect,
    requireSameTenant,
    restrictTo('admin', 'superadmin'),
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await feeController.archiveFeeStructure(req, res);

            await emitAudit(req, {
                resource: 'fee_registry',
                action: 'ARCHIVE_FEE',
                severity: 'WARN',
                metadata: { feeId: req.params.id }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'FEE_DELETE_FAILED';
            next(err);
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const feeRoutes = require('./server/routes/feeRoutes');
app.use('/api/fees', feeRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates currency codes (ISO 4217 standard subset).
3. [ ] Restricts creation/deletion to 'admin'/'finance' roles.
4. [ ] Emits WARN audit events for changing billing rates.
5. [ ] Ensures rate amounts are non-negative.
*/