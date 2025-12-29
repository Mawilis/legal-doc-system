/**
 * ~/server/models/eventModel.js
 *
 * Enterprise Event Model
 * ----------------------
 * Collaboration-ready, production-grade schema for managing events.
 * - Tracks hearings, deadlines, meetings, and scheduled activities.
 * - Links to cases, documents, courts, and users.
 * - Supports reminders and recurrence rules.
 * - Indexed for performance on status and eventDate.
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
// Event Schema
// ------------------------------------------
const eventSchema = new mongoose.Schema(
    {
        // 1) Identity
        eventCode: { type: String, required: true, unique: true, index: true }, // e.g., "EVT-2025-001"
        title: { type: String, required: true, trim: true },
        description: { type: String, trim: true },

        // 2) Scheduling
        eventDate: { type: Date, required: true },
        endDate: { type: Date, default: null },
        recurrence: {
            type: String,
            enum: ['None', 'Daily', 'Weekly', 'Monthly', 'Yearly'],
            default: 'None'
        },
        reminderMinutesBefore: { type: Number, default: 60 }, // Default reminder 1 hour before

        // 3) Relations
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        document: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
        court: { type: mongoose.Schema.Types.ObjectId, ref: 'Court' },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
        participants: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],

        // 4) Status
        status: {
            type: String,
            enum: ['Scheduled', 'Completed', 'Cancelled', 'Postponed'],
            default: 'Scheduled',
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
eventSchema.index({ status: 1, eventDate: 1 });
eventSchema.index({ case: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Transition event status with audit history.
 */
eventSchema.methods.transitionStatus = function (nextStatus, options = {}) {
    const current = this.status;
    this.status = nextStatus;
    this.history.push({
        action: 'STATUS_CHANGED',
        by: options.by || undefined,
        reason: options.reason || `Status changed from '${current}' to '${nextStatus}'`
    });
    return this.save();
};

/**
 * Add a participant to the event.
 */
eventSchema.methods.addParticipant = function (userId, options = {}) {
    this.participants.push(userId);
    this.history.push({
        action: 'PARTICIPANT_ADDED',
        by: options.by || undefined,
        reason: options.reason || `Participant ${userId} added to event`
    });
    return this.save();
};

// ------------------------------------------
// Model Export
// ------------------------------------------
module.exports = mongoose.model('Event', eventSchema);
