/**
 * ~/server/models/retentionModel.js
 *
 * Enterprise Retention Model
 * --------------------------
 * Collaboration-ready, production-grade schema for managing document/case retention policies.
 * - Defines retention rules and enforcement actions.
 * - Links to cases, documents, and compliance rules.
 * - Tracks audit history for compliance.
 * - Indexed for performance on status and retentionCode.
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
// Retention Schema
// ------------------------------------------
const retentionSchema = new mongoose.Schema(
    {
        // 1) Identity
        retentionCode: { type: String, required: true, unique: true, index: true }, // e.g., "RET-CASE-001"
        description: { type: String, required: true, trim: true }, // e.g., "Case files retained for 5 years"

        // 2) Policy Details
        retentionPeriodMonths: { type: Number, required: true, default: 60 }, // Default 5 years
        enforcementAction: {
            type: String,
            enum: ['Archive', 'Delete', 'Flag', 'Notify'],
            default: 'Archive'
        },

        // 3) Relations
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        document: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
        complianceRule: { type: mongoose.Schema.Types.ObjectId, ref: 'Compliance' },
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
retentionSchema.index({ status: 1, retentionCode: 1 });
retentionSchema.index({ case: 1, document: 1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Check if a document/case is due for enforcement.
 */
retentionSchema.methods.isDueForEnforcement = function (createdAt) {
    const cutoff = new Date(createdAt);
    cutoff.setMonth(cutoff.getMonth() + this.retentionPeriodMonths);
    return new Date() >= cutoff;
};

/**
 * Transition retention policy status with audit history.
 */
retentionSchema.methods.transitionStatus = function (nextStatus, options = {}) {
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
module.exports = mongoose.model('Retention', retentionSchema);
