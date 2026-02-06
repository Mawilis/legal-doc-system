/*
 * File: server/routes/notificationRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Notification Gateway (Tenant-Scoped). Manages Multi-Channel Alerts (Push, Email, In-App) and User Preferences.
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @ops,@platform,@mobile
 * MIGRATION_NOTES: Migrated to Joi Validation; consolidated preference management.
 * TESTS: mocha@9.x + chai@4.x; tests token registration and preference enforcement.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/notifications', notificationRoutes);
//
// Functionality:
//   - POST /register-token: Register device for Push Notifications (FCM).
//   - GET /: List in-app notifications.
//   - POST /send: Admin broadcast (Emergency/System alerts).
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const notificationController = require('../controllers/notificationController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const registerTokenSchema = {
    token: Joi.string().required(), // FCM/APNS Token
    platform: Joi.string().valid('IOS', 'ANDROID', 'WEB').required(),
    deviceId: Joi.string().optional()
};

const sendBroadcastSchema = {
    title: Joi.string().required(),
    body: Joi.string().required(),
    targetRole: Joi.string().valid('ALL', 'LAWYER', 'CLIENT', 'ADMIN').default('ALL'),
    urgency: Joi.string().valid('NORMAL', 'HIGH').default('NORMAL')
};

const preferencesSchema = {
    email: Joi.boolean().optional(),
    push: Joi.boolean().optional(),
    sms: Joi.boolean().optional(),
    categories: Joi.object({
        marketing: Joi.boolean().optional(),
        legal_updates: Joi.boolean().optional(),
        case_activity: Joi.boolean().optional()
    }).optional()
};

const idSchema = {
    id: Joi.string().required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   POST /api/notifications/register-token
 * @desc    Register Device Token (FCM/APNS)
 * @access  Authenticated Users
 */
router.post(
    '/register-token',
    protect,
    requireSameTenant,
    validate(registerTokenSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await notificationController.registerDevice(req, res);
            if (!res.headersSent && result) res.status(201).json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'NOTIF_TOKEN_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/notifications
 * @desc    Get User's Notification History
 * @access  Authenticated Users
 */
router.get(
    '/',
    protect,
    requireSameTenant,
    async (req, res, next) => {
        try {
            const result = await notificationController.getNotifications(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'NOTIF_LIST_FAILED';
            next(err);
        }
    }
);

/**
 * @route   PATCH /api/notifications/:id/read
 * @desc    Mark Notification as Read
 * @access  Authenticated Users
 */
router.patch(
    '/:id/read',
    protect,
    requireSameTenant,
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await notificationController.markAsRead(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'NOTIF_READ_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/notifications/preferences
 * @desc    Get User Notification Settings
 * @access  Authenticated Users
 */
router.get(
    '/preferences',
    protect,
    requireSameTenant,
    async (req, res, next) => {
        try {
            const result = await notificationController.getPreferences(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'NOTIF_PREF_GET_FAILED';
            next(err);
        }
    }
);

/**
 * @route   PATCH /api/notifications/preferences
 * @desc    Update User Notification Settings
 * @access  Authenticated Users
 */
router.patch(
    '/preferences',
    protect,
    requireSameTenant,
    validate(preferencesSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await notificationController.updatePreferences(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'NOTIF_PREF_UPDATE_FAILED';
            next(err);
        }
    }
);

/**
 * @route   POST /api/notifications/send
 * @desc    Send System Broadcast (Admin Only)
 * @access  Admin, SuperAdmin
 */
router.post(
    '/send',
    protect,
    requireSameTenant,
    restrictTo('admin', 'superadmin'),
    validate(sendBroadcastSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await notificationController.sendBroadcast(req, res);

            await emitAudit(req, {
                resource: 'notification_engine',
                action: 'SEND_BROADCAST',
                severity: 'WARN',
                summary: `Broadcast sent: ${req.body.title}`,
                metadata: { target: req.body.targetRole }
            });

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'NOTIF_BROADCAST_FAILED';
            next(err);
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const notificationRoutes = require('./server/routes/notificationRoutes');
app.use('/api/notifications', notificationRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates device token format and platform type.
3. [ ] Restricts broadcasts to 'admin' roles.
4. [ ] Allows users to toggle email/push preferences.
5. [ ] Emits Audit Events for system-wide broadcasts.
*/