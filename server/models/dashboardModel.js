/**
 * ~/server/models/dashboardModel.js
 *
 * Enterprise Dashboard Model
 * --------------------------
 * Collaboration-ready, production-grade schema for dashboards.
 * - Supports flexible widget configuration.
 * - Links to users and roles for personalization.
 * - Includes audit history for compliance.
 * - Indexed for performance on status and type.
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
// Dashboard Schema
// ------------------------------------------
const dashboardSchema = new mongoose.Schema(
    {
        // 1) Identity
        name: { type: String, required: true, trim: true },
        type: { type: String, trim: true, default: 'Custom', index: true },

        // 2) Status
        status: { type: String, default: 'Active', index: true },

        // 3) Relations
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
        assignedToRole: { type: String, trim: true }, // e.g., "Admin", "Lawyer", "Finance"

        // 4) Widgets/Charts Configuration
        widgets: {
            type: [
                {
                    widgetType: { type: String, required: true }, // e.g., "Chart", "Table", "Metric"
                    title: { type: String, trim: true },
                    config: { type: Object, default: {} } // Flexible JSON config
                }
            ],
            default: []
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
dashboardSchema.index({ status: 1, type: 1 });
dashboardSchema.index({ createdBy: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Add a widget to the dashboard.
 */
dashboardSchema.methods.addWidget = function (widget) {
    this.widgets.push(widget);
    this.history.push({
        action: 'WIDGET_ADDED',
        by: widget.by || undefined,
        reason: `Widget '${widget.title}' added`
    });
    return this.save();
};

/**
 * Transition status with audit history.
 */
dashboardSchema.methods.transitionStatus = function (nextStatus, options = {}) {
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
module.exports = mongoose.model('Dashboard', dashboardSchema);
