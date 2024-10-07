const Notification = require('../models/notificationModel');
const CustomError = require('../utils/customError');

// Get All Notifications
exports.getAllNotifications = async (req, res, next) => {
    try {
        const notifications = await Notification.find({ userId: req.user.id }).sort({ timestamp: -1 });
        res.status(200).json(notifications);
    } catch (error) {
        next(new CustomError('Error fetching notifications', 500));
    }
};

// Create Notification
exports.createNotification = async (req, res, next) => {
    try {
        const { message } = req.body;
        const newNotification = new Notification({
            userId: req.user.id,
            message,
            timestamp: new Date(),
        });
        await newNotification.save();

        // Emit to the frontend for real-time updates
        req.io.emit('new-notification', newNotification);

        res.status(201).json(newNotification);
    } catch (error) {
        next(new CustomError('Error creating notification', 500));
    }
};

// Mark Notification as Read
exports.markAsRead = async (req, res, next) => {
    try {
        const notification = await Notification.findByIdAndUpdate(req.params.notificationId, { read: true });
        if (!notification) return next(new CustomError('Notification not found', 404));

        res.status(200).json(notification);
    } catch (error) {
        next(new CustomError('Error marking notification as read', 500));
    }
};

// Delete Notification
exports.deleteNotification = async (req, res, next) => {
    try {
        const notification = await Notification.findByIdAndDelete(req.params.notificationId);
        if (!notification) return next(new CustomError('Notification not found', 404));

        res.status(200).json({ message: 'Notification deleted successfully' });
    } catch (error) {
        next(new CustomError('Error deleting notification', 500));
    }
};
