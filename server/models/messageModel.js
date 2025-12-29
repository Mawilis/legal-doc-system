/**
 * ~/server/models/messageModel.js
 *
 * Enterprise Message Model
 * ------------------------
 * Collaboration-ready, production-grade schema for managing messages.
 * - Supports direct user-to-user and system-to-user communication.
 * - Links to cases, documents, and workflows for context.
 * - Tracks message lifecycle with audit history.
 * - Indexed for performance on status and participants.
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
// Message Schema
// ------------------------------------------
const messageSchema = new mongoose.Schema(
    {
        // 1) Identity
        messageCode: { type: String, required: true, unique: true, index: true }, // e.g., "MSG-2025-001"
        subject: { type: String, trim: true },
        body: { type: String, required: true, trim: true },

        // 2) Participants
        sender: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
        recipients: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true }],

        // 3) Relations
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        document: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
        workflow: { type: mongoose.Schema.Types.ObjectId, ref: 'Workflow' },

        // 4) Status
        status: {
            type: String,
            enum: ['Sent', 'Delivered', 'Read', 'Archived'],
            default: 'Sent',
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
messageSchema.index({ status: 1, sender: 1 });
messageSchema.index({ recipients: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Mark message as delivered.
 */
messageSchema.methods.markDelivered = function (options = {}) {
    this.status = 'Delivered';
    this.history.push({
        action: 'DELIVERED',
        by: options.by || undefined,
        reason: options.reason || 'Message marked as delivered'
    });
    return this.save();
};

/**
 * Mark message as read.
 */
messageSchema.methods.markRead = function (options = {}) {
    this.status = 'Read';
    this.history.push({
        action: 'READ',
        by: options.by || undefined,
        reason: options.reason || 'Message marked as read'
    });
    return this.save();
};

/**
 * Transition message status with audit history.
 */
messageSchema.methods.transitionStatus = function (nextStatus, options = {}) {
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
module.exports = mongoose.model('Message', messageSchema);
