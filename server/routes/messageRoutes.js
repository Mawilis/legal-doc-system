/*
 * File: server/routes/messageRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Secure Messaging Gateway (Tenant-Scoped). Manages encrypted communication between Staff and Clients (Attorney-Client Privilege).
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @security,@legal,@platform
 * MIGRATION_NOTES: Migrated to Joi Validation; enforced thread isolation.
 * TESTS: mocha@9.x + chai@4.x; tests cross-tenant leakage and privilege boundaries.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/messages', messageRoutes);
//
// Functionality:
//   - POST /: Send a secure message (New or Reply).
//   - GET /thread/:id: Retrieve conversation history.
//   - PATCH /:id/read: Mark message as read.
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const messageController = require('../controllers/messageController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const sendMessageSchema = {
    recipientId: Joi.string().required(),
    threadId: Joi.string().optional(), // If replying to existing thread
    caseId: Joi.string().optional(), // Context for new threads
    content: Joi.string().max(5000).required(), // Text content
    attachments: Joi.array().items(Joi.string()).optional() // IDs of uploaded files
};

const idSchema = {
    id: Joi.string().required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   POST /api/messages
 * @desc    Send Secure Message
 * @access  Authenticated Users (Staff & Clients)
 */
router.post(
    '/',
    protect,
    requireSameTenant, // Sender and Recipient must be in same tenant scope
    validate(sendMessageSchema, 'body'),
    async (req, res, next) => {
        try {
            const result = await messageController.sendMessage(req, res);

            // Audit the Communication (Metadata Only)
            await emitAudit(req, {
                resource: 'secure_messenger',
                action: 'SEND_MESSAGE',
                severity: 'INFO',
                summary: `Message sent to ${req.body.recipientId}`,
                metadata: {
                    caseId: req.body.caseId,
                    hasAttachments: !!req.body.attachments
                }
            });

            if (!res.headersSent && result) res.status(201).json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'MSG_SEND_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/messages/thread/:id
 * @desc    Get Conversation History
 * @access  Authenticated Users (Participants Only)
 */
router.get(
    '/thread/:id',
    protect,
    requireSameTenant,
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await messageController.getThread(req, res);

            // Read auditing usually skipped for chat polling unless strict security required

            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'MSG_THREAD_FAILED';
            next(err);
        }
    }
);

/**
 * @route   PATCH /api/messages/:id/read
 * @desc    Mark Message as Read
 * @access  Authenticated Users (Recipient Only)
 */
router.patch(
    '/:id/read',
    protect,
    requireSameTenant,
    validate(idSchema, 'params'),
    async (req, res, next) => {
        try {
            const result = await messageController.markAsRead(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'MSG_READ_FAILED';
            next(err);
        }
    }
);

/**
 * @route   GET /api/messages/unread-count
 * @desc    Get Global Unread Count (For Badge UI)
 * @access  Authenticated Users
 */
router.get(
    '/unread-count',
    protect,
    requireSameTenant,
    async (req, res, next) => {
        try {
            const result = await messageController.getUnreadCount(req, res);
            if (!res.headersSent && result) res.json({ status: 'success', data: result });
        } catch (err) {
            err.code = 'MSG_COUNT_FAILED';
            next(err);
        }
    }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const messageRoutes = require('./server/routes/messageRoutes');
app.use('/api/messages', messageRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates message content length (max 5000 chars).
3. [ ] Restricts thread access to participants (controller logic).
4. [ ] Allows both Clients and Staff to communicate.
5. [ ] Emits Audit Events for sending (Meta-data only, protecting privilege).
*/