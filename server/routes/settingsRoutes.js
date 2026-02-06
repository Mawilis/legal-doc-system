/*
 * File: server/routes/settingsRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Settings Gateway (Tenant-Scoped). Manages firm-wide configurations: Branding, Security, Billing defaults, and Notification rules.
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @platform,@security,@design
 * MIGRATION_NOTES: Migrated to Joi Validation; strict typing on configuration objects.
 * TESTS: mocha@9.x + chai@4.x; tests deep-merge updates and audit logging of config changes.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/settings', settingsRoutes);
//
// Functionality:
//   - GET /: Retrieve current tenant configuration.
//   - PATCH /: Update settings (Deep merge).
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const settingsController = require('../controllers/settingsController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const updateSettingsSchema = {
    branding: Joi.object({
        firmName: Joi.string().min(2).optional(),
        primaryColor: Joi.string().pattern(/^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/).optional(), // Hex code
        logoUrl: Joi.string().uri().optional(),
        website: Joi.string().uri().optional()
    }).optional(),

    billing: Joi.object({
        vatNumber: Joi.string().optional(),
        currency: Joi.string().valid('ZAR', 'USD', 'EUR').optional(),
        defaultPaymentTerms: Joi.number().min(0).max(90).optional(), // Days
        bankDetails: Joi.string().max(1000).optional() // Free text for now, or object
    }).optional(),

    notifications: Joi.object({
        emailEnabled: Joi.boolean().optional(),
        smsEnabled: Joi.boolean().optional(),
        dailyDigest: Joi.boolean().optional()
    }).optional(),

    security: Joi.object({
        mfaRequired: Joi.boolean().optional(),
        sessionTimeout: Joi.number().min(5).max(1440).optional(), // Minutes
        passwordExpiryDays: Joi.number().min(0).max(365).optional()
    }).optional()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   GET /api/settings
 * @desc    Get Tenant Configuration
 * @access  Authenticated Users
 */
router.get(
    '/',
    protect,
    requireSameTenant,
    async (req, res, next) => {
        try {
            const result = await settingsController.getSettings(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'SETTINGS_GET_FAILED';
            next(err);
        }
    }
);

/**
 * @route   PATCH /api/settings
 * @desc    Update Tenant Configuration (Deep Merge)
 * @access  Admin, SuperAdmin
 */
router.patch(
    '/',
    protect,
    requireSameTenant,
    restrictTo('admin', 'superadmin'),
    validate(updateSettingsSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await settingsController.updateSettings(req, res);

            // Critical Audit: Configuration Change
            await emitAudit(req, {
                resource: 'tenant_config',
                action: 'UPDATE_SETTINGS',
                severity: 'WARN',
                summary: 'Firm settings updated',
                metadata: {
                    updatedFields: Object.keys(req.body)
                }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'SETTINGS_UPDATE_FAILED';
            next(err);
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const settingsRoutes = require('./server/routes/settingsRoutes');
app.use('/api/settings', settingsRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates Hex color codes for branding.
3. [ ] Restricts updates to 'admin'/'superadmin' only.
4. [ ] Allows granular updates (only changed fields required).
5. [ ] Emits WARN audit events for configuration changes (Security Impact).
*/