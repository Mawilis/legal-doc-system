/**
 * ~/server/models/sheriffModel.js
 *
 * Enterprise Sheriff Model
 * ------------------------
 * Collaboration-ready, production-grade schema for tracking service of process and enforcement actions.
 * - Records service attempts, outcomes, and return details.
 * - Links to cases, documents, courts, and users.
 * - Tracks lifecycle with audit history.
 * - Indexed for performance on status and serviceDate.
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
// Service Attempt Sub-Schema
// ------------------------------------------
const attemptSchema = new mongoose.Schema(
    {
        date: { type: Date, default: Date.now },
        outcome: {
            type: String,
            enum: ['Pending', 'Successful', 'Failed'],
            default: 'Pending'
        },
        notes: { type: String, trim: true },
        servedTo: { type: String, trim: true }, // Person/entity served
        address: { type: String, trim: true }
    },
    { _id: false }
);

// ------------------------------------------
// Sheriff Schema
// ------------------------------------------
const sheriffSchema = new mongoose.Schema(
    {
        // 1) Identity
        sheriffCode: { type: String, required: true, unique: true, index: true }, // e.g., "SHF-2025-001"
        name: { type: String, required: true, trim: true }, // Sheriff officer name
        badgeNumber: { type: String, trim: true },

        // 2) Relations
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        document: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
        court: { type: mongoose.Schema.Types.ObjectId, ref: 'Court' },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 3) Service Attempts
        attempts: { type: [attemptSchema], default: [] },

        // 4) Status
        status: {
            type: String,
            enum: ['Assigned', 'In Progress', 'Completed', 'Failed'],
            default: 'Assigned',
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
sheriffSchema.index({ status: 1, sheriffCode: 1 });
sheriffSchema.index({ case: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Add a service attempt.
 */
sheriffSchema.methods.addAttempt = function (attempt) {
    this.attempts.push(attempt);
    this.history.push({
        action: 'ATTEMPT_ADDED',
        by: attempt.by || undefined,
        reason: attempt.notes || 'Service attempt recorded'
    });
    return this.save();
};

/**
 * Transition sheriff assignment status with audit history.
 */
sheriffSchema.methods.transitionStatus = function (nextStatus, options = {}) {
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
module.exports = mongoose.model('Sheriff', sheriffSchema);
