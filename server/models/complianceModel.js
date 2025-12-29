/**
 * ~/server/models/complianceModel.js
 *
 * Enterprise Compliance Model
 * ---------------------------
 * Collaboration-ready, production-grade schema for managing compliance rules.
 * - Defines regulatory requirements and retention policies.
 * - Links to cases, documents, and users for traceability.
 * - Tracks audit history for compliance enforcement.
 * - Indexed for performance on status and ruleCode.
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
// Compliance Schema
// ------------------------------------------
const complianceSchema = new mongoose.Schema(
    {
        // 1) Identity
        ruleCode: { type: String, required: true, unique: true, index: true }, // e.g., "COMP-RET-001"
        description: { type: String, required: true, trim: true }, // e.g., "Retention of case files for 5 years"

        // 2) Regulatory Context
        jurisdiction: { type: String, trim: true, default: 'South Africa' },
        category: { type: String, trim: true, default: 'Retention', index: true }, // e.g., "Retention", "Audit", "Privacy"

        // 3) Policy Details
        retentionPeriodMonths: { type: Number, default: 60 }, // Default 5 years
        enforcementAction: {
            type: String,
            enum: ['Archive', 'Delete', 'Flag', 'Notify'],
            default: 'Archive'
        },

        // 4) Relations
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        document: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 5) Status
        status: {
            type: String,
            enum: ['Active', 'Inactive', 'Deprecated'],
            default: 'Active',
            index: true
        },

        // 6) Metadata
        meta: { type: Object, default: {} },

        // 7) Audit History
        history: { type: [historySchema], default: [] }
    },
    { timestamps: true }
);

// ------------------------------------------
// Indexes
// ------------------------------------------
complianceSchema.index({ status: 1, category: 1 });
complianceSchema.index({ jurisdiction: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Transition compliance rule status with audit history.
 */
complianceSchema.methods.transitionStatus = function (nextStatus, options = {}) {
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
 * Check if a document is due for enforcement based on retention period.
 */
complianceSchema.methods.isDueForEnforcement = function (docDate) {
    const cutoff = new Date(docDate);
    cutoff.setMonth(cutoff.getMonth() + this.retentionPeriodMonths);
    return new Date() >= cutoff;
};

// ------------------------------------------
// Model Export
// ------------------------------------------
module.exports = mongoose.model('Compliance', complianceSchema);
