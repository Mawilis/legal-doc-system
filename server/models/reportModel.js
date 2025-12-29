/**
 * ~/server/models/reportModel.js
 *
 * Enterprise Report Model
 * -----------------------
 * Collaboration-ready, production-grade schema for managing reports.
 * - Defines report type, scope, and content.
 * - Links to analytics, audits, dashboards, cases, and users.
 * - Tracks report lifecycle with audit history.
 * - Indexed for performance on status and reportCode.
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
// Report Section Sub-Schema
// ------------------------------------------
const sectionSchema = new mongoose.Schema(
    {
        title: { type: String, required: true, trim: true },
        content: { type: String, trim: true },
        data: { type: Object, default: {} } // Flexible JSON for charts/tables
    },
    { _id: false }
);

// ------------------------------------------
// Report Schema
// ------------------------------------------
const reportSchema = new mongoose.Schema(
    {
        // 1) Identity
        reportCode: { type: String, required: true, unique: true, index: true }, // e.g., "REP-2025-001"
        reportType: { type: String, required: true, trim: true }, // e.g., "Financial", "Compliance", "Operational"
        title: { type: String, required: true, trim: true },
        description: { type: String, trim: true },

        // 2) Scope & Relations
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        audit: { type: mongoose.Schema.Types.ObjectId, ref: 'Audit' },
        analytics: { type: mongoose.Schema.Types.ObjectId, ref: 'Analytics' },
        dashboard: { type: mongoose.Schema.Types.ObjectId, ref: 'Dashboard' },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 3) Content
        sections: { type: [sectionSchema], default: [] },

        // 4) Status
        status: {
            type: String,
            enum: ['Draft', 'Generated', 'Reviewed', 'Published', 'Archived'],
            default: 'Draft',
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
reportSchema.index({ status: 1, reportType: 1 });
reportSchema.index({ createdBy: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Add a section to the report.
 */
reportSchema.methods.addSection = function (section) {
    this.sections.push(section);
    this.history.push({
        action: 'SECTION_ADDED',
        by: section.by || undefined,
        reason: `Section '${section.title}' added`
    });
    return this.save();
};

/**
 * Transition report status with audit history.
 */
reportSchema.methods.transitionStatus = function (nextStatus, options = {}) {
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
module.exports = mongoose.model('Report', reportSchema);
