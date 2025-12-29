/**
 * ~/server/models/courtModel.js
 *
 * Enterprise Court Model
 * ----------------------
 * Collaboration-ready, production-grade schema for managing courts and divisions.
 * - Defines court identity, jurisdiction, and divisions.
 * - Links to cases, documents, events, and sheriffs.
 * - Tracks lifecycle with audit history.
 * - Indexed for performance on status and courtCode.
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
// Division Sub-Schema
// ------------------------------------------
const divisionSchema = new mongoose.Schema(
    {
        name: { type: String, required: true, trim: true }, // e.g., "Civil Division"
        description: { type: String, trim: true },
        headJudge: { type: String, trim: true }
    },
    { _id: false }
);

// ------------------------------------------
// Court Schema
// ------------------------------------------
const courtSchema = new mongoose.Schema(
    {
        // 1) Identity
        courtCode: { type: String, required: true, unique: true, index: true }, // e.g., "CPT-HIGH-001"
        name: { type: String, required: true, trim: true }, // e.g., "Cape Town High Court"
        jurisdiction: { type: String, required: true, trim: true }, // e.g., "Western Cape"
        address: { type: String, trim: true },

        // 2) Divisions
        divisions: { type: [divisionSchema], default: [] },

        // 3) Relations
        cases: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Case' }],
        documents: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Document' }],
        events: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Event' }],
        sheriffs: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Sheriff' }],
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 4) Status
        status: {
            type: String,
            enum: ['Active', 'Inactive', 'Deprecated'],
            default: 'Active',
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
courtSchema.index({ status: 1, courtCode: 1 });
courtSchema.index({ jurisdiction: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Add a division to the court.
 */
courtSchema.methods.addDivision = function (division) {
    this.divisions.push(division);
    this.history.push({
        action: 'DIVISION_ADDED',
        by: division.by || undefined,
        reason: `Division '${division.name}' added`
    });
    return this.save();
};

/**
 * Transition court status with audit history.
 */
courtSchema.methods.transitionStatus = function (nextStatus, options = {}) {
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
module.exports = mongoose.model('Court', courtSchema);
