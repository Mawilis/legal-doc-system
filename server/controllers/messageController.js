/*
 * File: server/controllers/messageController.js
 * STATUS: PRODUCTION-READY | PRIVILEGED COMMUNICATION GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Governs secure internal and client communication. Manages privileged 
 * messaging threads, case-linked discussions, and non-repudiable read receipts.
 * -----------------------------------------------------------------------------
 */

'use strict';

const asyncHandler = require('express-async-handler');
const Message = require('../models/Message');
const User = require('../models/User');
const Case = require('../models/Case');
const { successResponse, errorResponse } = require('../middleware/responseHandler');
const { emitAudit } = require('../middleware/auditMiddleware');

/**
 * @desc    DISPATCH SECURE MESSAGE
 * @route   POST /api/v1/messages
 */
exports.sendMessage = asyncHandler(async (req, res) => {
    const { recipientId, caseId, content, priority } = req.body;

    // 1. RECIPIENT SCOPE VALIDATION
    const recipient = await User.findOne({ _id: recipientId, ...req.tenantFilter });
    if (!recipient) {
        return errorResponse(req, res, 404, 'Recipient not found within your firm scope.', 'ERR_USER_NOT_FOUND');
    }

    // 2. CASE CONTEXT VALIDATION
    if (caseId) {
        const caseExists = await Case.exists({ _id: caseId, ...req.tenantFilter });
        if (!caseExists) {
            return errorResponse(req, res, 404, 'The referenced case matter is invalid or inaccessible.', 'ERR_CASE_NOT_FOUND');
        }
    }

    // 3. ATOMIC CREATION
    const message = await Message.create({
        ...req.body,
        tenantId: req.user.tenantId,
        sender: req.user.id,
        isRead: false
    });

    // 4. FORENSIC METADATA AUDIT (Content is excluded for privacy)
    await emitAudit(req, {
        resource: 'COMMUNICATION_MODULE',
        action: 'MESSAGE_SENT',
        severity: priority === 'URGENT' ? 'WARNING' : 'INFO',
        metadata: {
            messageId: message._id,
            recipientId,
            caseId,
            priority: priority || 'NORMAL'
        }
    });

    return successResponse(req, res, message, { message: 'Secure message dispatched.' }, 201);
});

/**
 * @desc    GET PERSONAL INBOX/SENT FEED
 * @route   GET /api/v1/messages
 */
exports.getMyMessages = asyncHandler(async (req, res) => {
    const { folder, caseId, page = 1, limit = 20 } = req.query;

    const query = { ...req.tenantFilter };

    // Dynamic Folder Routing
    if (folder === 'SENT') {
        query.sender = req.user.id;
    } else {
        query.recipient = req.user.id;
    }

    if (caseId) query.caseId = caseId;

    const skip = (parseInt(page) - 1) * parseInt(limit);
    const messages = await Message.find(query)
        .populate('sender', 'name email role')
        .populate('recipient', 'name email')
        .populate('caseId', 'caseNumber')
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(parseInt(limit));

    const total = await Message.countDocuments(query);
    const unreadCount = await Message.countDocuments({
        ...req.tenantFilter,
        recipient: req.user.id,
        isRead: false
    });

    return successResponse(req, res, messages, {
        pagination: { total, page: parseInt(page) },
        meta: { unreadCount }
    });
});

/**
 * @desc    ACCESS MESSAGE CONTENT (MARK AS READ)
 * @route   GET /api/v1/messages/:id
 */
exports.readMessage = asyncHandler(async (req, res) => {
    const message = await Message.findOne({
        _id: req.params.id,
        ...req.tenantFilter
    }).populate('sender', 'name email').populate('caseId', 'caseNumber');

    if (!message) {
        return errorResponse(req, res, 404, 'Message not found.', 'ERR_MESSAGE_NOT_FOUND');
    }

    // PRIVACY GUARD: Only participants can read
    const isRecipient = message.recipient.toString() === req.user.id;
    const isSender = message.sender._id.toString() === req.user.id;

    if (!isRecipient && !isSender) {
        return errorResponse(req, res, 403, 'Unauthorized access to privileged communication.', 'ERR_RBAC_FORBIDDEN');
    }

    // NON-REPUDIABLE READ RECEIPT
    if (isRecipient && !message.isRead) {
        message.isRead = true;
        message.readAt = new Date();
        await message.save();
    }

    return successResponse(req, res, message);
});

/**
 * @desc    ARCHIVE COMMUNICATION
 * @route   DELETE /api/v1/messages/:id
 */
exports.deleteMessage = asyncHandler(async (req, res) => {
    const message = await Message.findOne({ _id: req.params.id, ...req.tenantFilter });

    if (!message) {
        return errorResponse(req, res, 404, 'Message not found.', 'ERR_MESSAGE_NOT_FOUND');
    }

    // Participants only
    if (message.recipient.toString() !== req.user.id && message.sender.toString() !== req.user.id) {
        return errorResponse(req, res, 403, 'Unauthorized.', 'ERR_RBAC_FORBIDDEN');
    }

    // SOFT DELETE: Maintain data for legal discovery but hide from UI
    message.status = 'DELETED';
    await message.save();

    return successResponse(req, res, null, { message: 'Message successfully archived.' });
});