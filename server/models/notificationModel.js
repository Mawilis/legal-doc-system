// server/models/notificationModel.js

const mongoose = require('mongoose');

const notificationSchema = new mongoose.Schema(
    {
        // The user who should receive this notification.
        recipient: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User',
            required: true,
        },
        // The main content or message of the notification.
        message: {
            type: String,
            required: [true, 'A notification must have a message.'],
            trim: true,
        },
        // A boolean to track if the recipient has seen the notification.
        // This is essential for UI features like a "new notifications" badge.
        isRead: {
            type: Boolean,
            default: false,
        },
        // An optional link to a specific part of the application.
        // For example, a link to the document that is ready for uplift.
        link: {
            type: String,
            trim: true,
        },
        // The type of notification, which can be used to display different icons or styles on the frontend.
        type: {
            type: String,
            enum: ['document_status', 'new_message', 'system_alert', 'mention'],
            default: 'system_alert',
        }
    },
    {
        // Automatically adds `createdAt` and `updatedAt` timestamps.
        // `createdAt` is essential for displaying notifications in chronological order.
        timestamps: true,
    }
);

// Create an index on the recipient and isRead fields to speed up queries
// for fetching a user's unread notifications.
notificationSchema.index({ recipient: 1, isRead: 1 });

const Notification = mongoose.model('Notification', notificationSchema);

module.exports = Notification;
