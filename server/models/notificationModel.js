/**
 * ~/server/models/notificationModel.js
 *
 * Enterprise Notification Model
 * -----------------------------
 * Collaboration-ready, production-grade schema for managing system notifications.
 * - Supports multiple channels (Email, SMS, In-App).
 * - Links to cases, documents, invoices, and users.
 * - Tracks notification lifecycle with audit history.
 * - Indexed for performance on status and recipient.
 */

'use strict';

const mongoose = require('mongoose');

// ------------------------------------------
// Audit History Sub-Schema
// ------------------------------------------
const historySchema = new mongoose.Schema(
    {
        action: { type: String, required: true, trim: true },
        by: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
        date: { type: Date, default: Date.now },
        reason: { type: String, trim: true }
    },
    { _id: false }
);

// ------------------------------------------
// Notification Schema
// ------------------------------------------
const notificationSchema = new mongoose.Schema(
    {
        // 1) Identity
        notificationCode: { type: String, required: true, unique: true, index: true }, // e.g., "NOTIF-2025-001"
        title: { type: String, required: true, trim: true },
        message: { type: String, required: true, trim: true },

        // 2) Delivery
        channel: {
            type: String,
            enum: ['Email', 'SMS', 'In-App', 'Push'],
            default: 'In-App'
        },
        recipient: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
        recipientEmail: { type: String, trim: true },
        recipientPhone: { type: String, trim: true },

        // 3) Relations
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        document: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
        invoice: { type: mongoose.Schema.Types.ObjectId, ref: 'Invoice' },
        workflow: { type: mongoose.Schema.Types.ObjectId, ref: 'Workflow' },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 4) Status
        status: {
            type: String,
            enum: ['Pending', 'Sent', 'Delivered', 'Failed', 'Read'],
            default: 'Pending',
            index: true
        },

        // 5) Metadata
        meta: { type: Object, default: {} },

        // 6) Audit History
        history: { type: [historySchema], default: [] }
    },
    { timestamps: true }
);

// ------------------------------------------
// Indexes
// ------------------------------------------
notificationSchema.index({ status: 1, recipient: 1 });
notificationSchema.index({ channel: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Mark notification as delivered.
 */
notificationSchema.methods.markDelivered = function (options = {}) {
    this.status = 'Delivered';
    this.history.push({
        action: 'DELIVERED',
        by: options.by || undefined,
        reason: options.reason || 'Notification marked as delivered'
    });
    return this.save();
};

/**
 * Mark notification as read.
 */
notificationSchema.methods.markRead = function (options = {}) {
    this.status = 'Read';
    this.history.push({
        action: 'READ',
        by: options.by || undefined,
        reason: options.reason || 'Notification marked as read'
    });
    return this.save();
};

/**
 * Transition notification status with audit history.
 */
notificationSchema.methods.transitionStatus = function (nextStatus, options = {}) {
    const current = this.status;
    this.status = nextStatus;
    this.history.push({
        action: 'STATUS_CHANGED',
        by: options.by || undefined,
        reason: options.reason || `Status changed from '${current}' to '${nextStatus}'`
    });
    return this.save();
};

// ------------------------------------------
// Model Export
// ------------------------------------------
module.exports = mongoose.model('Notification', notificationSchema);
