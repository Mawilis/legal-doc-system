/**
 * ~/server/models/analyticsModel.js
 *
 * Enterprise Analytics Model
 * --------------------------
 * Collaboration-ready, production-grade schema for managing analytics data.
 * - Defines analytics type, scope, and metrics.
 * - Links to cases, invoices, workflows, reports, and dashboards.
 * - Tracks lifecycle with audit history.
 * - Indexed for performance on status and analyticsCode.
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
// Metric Sub-Schema
// ------------------------------------------
const metricSchema = new mongoose.Schema(
    {
        name: { type: String, required: true, trim: true }, // e.g., "Revenue", "Case Duration"
        value: { type: Number, required: true },
        unit: { type: String, trim: true }, // e.g., "ZAR", "Days"
        capturedAt: { type: Date, default: Date.now }
    },
    { _id: false }
);

// ------------------------------------------
// Analytics Schema
// ------------------------------------------
const analyticsSchema = new mongoose.Schema(
    {
        // 1) Identity
        analyticsCode: { type: String, required: true, unique: true, index: true }, // e.g., "ANL-2025-001"
        analyticsType: { type: String, required: true, trim: true }, // e.g., "Financial", "Operational", "Compliance"
        description: { type: String, trim: true },

        // 2) Scope & Relations
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        invoice: { type: mongoose.Schema.Types.ObjectId, ref: 'Invoice' },
        workflow: { type: mongoose.Schema.Types.ObjectId, ref: 'Workflow' },
        report: { type: mongoose.Schema.Types.ObjectId, ref: 'Report' },
        dashboard: { type: mongoose.Schema.Types.ObjectId, ref: 'Dashboard' },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 3) Metrics
        metrics: { type: [metricSchema], default: [] },

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
analyticsSchema.index({ status: 1, analyticsType: 1 });
analyticsSchema.index({ createdBy: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Add a metric to the analytics record.
 */
analyticsSchema.methods.addMetric = function (metric) {
    this.metrics.push(metric);
    this.history.push({
        action: 'METRIC_ADDED',
        by: metric.by || undefined,
        reason: `Metric '${metric.name}' recorded`
    });
    return this.save();
};

/**
 * Transition analytics status with audit history.
 */
analyticsSchema.methods.transitionStatus = function (nextStatus, options = {}) {
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
module.exports = mongoose.model('Analytics', analyticsSchema);
