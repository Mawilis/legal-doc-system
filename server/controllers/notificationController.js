// server/controllers/notificationController.js

const Notification = require('../models/notificationModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

// --- Helper Function for Creating Notifications ---
// This function is not a route handler. It's a utility that can be called from other controllers.
// For example, when a document's status changes, the document controller can call this function.
exports.createNotification = async (recipientId, message, link, type) => {
    try {
        if (!recipientId || !message) {
            logger.warn('Attempted to create a notification with missing recipient or message.');
            return;
        }
        await Notification.create({
            recipient: recipientId,
            message,
            link,
            type,
        });
        logger.info(`Notification created for user: ${recipientId}`);
        // Here you would also typically emit a real-time event via Socket.io
        // io.to(recipientId).emit('new_notification', { message });
    } catch (error) {
        logger.error(`Error creating notification: ${error.message}`);
    }
};


// --- Route Handlers ---

/**
 * @desc    Get all notifications for the logged-in user
 * @route   GET /api/notifications
 * @access  Private
 */
exports.getNotifications = async (req, res, next) => {
    try {
        // Find all notifications for the current user and sort by newest first.
        // We also limit the result to the most recent 50 notifications for performance.
        const notifications = await Notification.find({ recipient: req.user.id })
            .sort({ createdAt: -1 })
            .limit(50);

        res.status(200).json({
            success: true,
            count: notifications.length,
            data: notifications,
        });
    } catch (error) {
        logger.error(`Error fetching notifications: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Mark a single notification as read
 * @route   PUT /api/notifications/:id/read
 * @access  Private
 */
exports.markAsRead = async (req, res, next) => {
    try {
        const notification = await Notification.findById(req.params.id);

        if (!notification) {
            return next(new CustomError(`Notification not found with id of ${req.params.id}`, 404));
        }

        // Authorization: Ensure the user marking the notification is the recipient.
        if (notification.recipient.toString() !== req.user.id) {
            return next(new CustomError('User not authorized to update this notification.', 403));
        }

        notification.isRead = true;
        await notification.save();

        res.status(200).json({
            success: true,
            data: notification,
        });
    } catch (error) {
        logger.error(`Error marking notification as read: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Mark all notifications as read for the logged-in user
 * @route   PUT /api/notifications/readall
 * @access  Private
 */
exports.markAllAsRead = async (req, res, next) => {
    try {
        // Use `updateMany` to efficiently update all documents that match the filter.
        await Notification.updateMany(
            { recipient: req.user.id, isRead: false }, // Filter for unread notifications of the current user
            { $set: { isRead: true } } // The update operation
        );

        logger.info(`All notifications marked as read for user: ${req.user.email}`);

        res.status(200).json({
            success: true,
            message: 'All notifications have been marked as read.',
        });
    } catch (error) {
        logger.error(`Error marking all notifications as read: ${error.message}`);
        next(error);
    }
};
