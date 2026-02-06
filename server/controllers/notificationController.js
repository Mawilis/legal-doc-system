/*
 * File: server/controllers/notificationController.js
 * STATUS: PRODUCTION-READY | REAL-TIME ALERT GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Manages the delivery and lifecycle of user alerts. Handles in-app 
 * notifications, bulk read status updates, and system-triggered events.
 * -----------------------------------------------------------------------------
 */

'use strict';

const asyncHandler = require('express-async-handler');
const Notification = require('../models/Notification');
const { successResponse, errorResponse } = require('../middleware/responseHandler');

/**
 * @desc    GET PERSONAL NOTIFICATION FEED (Paginated)
 * @route   GET /api/v1/notifications
 */
exports.getMyNotifications = asyncHandler(async (req, res) => {
    const { unreadOnly, page = 1, limit = 50 } = req.query;

    const query = {
        userId: req.user.id,
        ...req.tenantFilter // Injected via middleware for strict siloing
    };

    if (unreadOnly === 'true') {
        query.isRead = false;
    }

    const skip = (parseInt(page) - 1) * parseInt(limit);
    const notifications = await Notification.find(query)
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(parseInt(limit))
        .lean(); // Optimized for read-only throughput

    const total = await Notification.countDocuments(query);

    return successResponse(req, res, notifications, {
        pagination: {
            total,
            page: parseInt(page),
            pages: Math.ceil(total / parseInt(limit))
        }
    });
});

/**
 * @desc    ACKNOWLEDGE NOTIFICATION (MARK READ)
 * @route   PATCH /api/v1/notifications/:id/read
 */
exports.markAsRead = asyncHandler(async (req, res) => {
    const notification = await Notification.findOneAndUpdate(
        {
            _id: req.params.id,
            userId: req.user.id,
            ...req.tenantFilter
        },
        { isRead: true, readAt: new Date() },
        { new: true }
    );

    if (!notification) {
        return errorResponse(req, res, 404, 'Notification not found or access denied.', 'ERR_NOTIF_NOT_FOUND');
    }

    return successResponse(req, res, notification);
});

/**
 * @desc    BULK ACKNOWLEDGE (MARK ALL READ)
 * @route   PATCH /api/v1/notifications/read-all
 */
exports.markAllAsRead = asyncHandler(async (req, res) => {
    await Notification.updateMany(
        {
            userId: req.user.id,
            ...req.tenantFilter,
            isRead: false
        },
        { isRead: true, readAt: new Date() }
    );

    return successResponse(req, res, null, { message: 'All pending alerts acknowledged.' });
});

/**
 * @desc    DISMISS NOTIFICATION (DELETE)
 * @route   DELETE /api/v1/notifications/:id
 */
exports.deleteNotification = asyncHandler(async (req, res) => {
    const notification = await Notification.findOneAndDelete({
        _id: req.params.id,
        userId: req.user.id,
        ...req.tenantFilter
    });

    if (!notification) {
        return errorResponse(req, res, 404, 'Notification not found.', 'ERR_NOTIF_NOT_FOUND');
    }

    return successResponse(req, res, null, { message: 'Alert dismissed.' });
});

/**
 * @desc    TRIGGER SYSTEM NOTIFICATION (ADMIN ONLY)
 * @route   POST /api/v1/notifications
 */
exports.createNotification = asyncHandler(async (req, res) => {
    // RBAC: Only high-privilege accounts can push manual alerts
    if (!['admin', 'super_admin'].includes(req.user.role)) {
        return errorResponse(req, res, 403, 'Permission denied: Cannot initiate system alerts.', 'ERR_RBAC_FORBIDDEN');
    }

    const { targetUserId, title, content, type, urgency } = req.body;

    const notification = await Notification.create({
        tenantId: req.user.tenantId,
        userId: targetUserId,
        title,
        content,
        type: type || 'INFO',
        urgency: urgency || 'NORMAL'
    });

    return successResponse(req, res, notification, { message: 'System alert dispatched.' }, 201);
});