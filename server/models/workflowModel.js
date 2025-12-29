/**
 * ~/server/models/workflowModel.js
 *
 * Enterprise Workflow Model
 * --------------------------
 * Collaboration-ready, production-grade schema for managing case/document workflows.
 * - Defines workflow stages and transitions.
 * - Links to cases, documents, and users.
 * - Tracks audit history for compliance.
 * - Indexed for performance on status and workflowName.
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
// Workflow Stage Sub-Schema
// ------------------------------------------
const stageSchema = new mongoose.Schema(
    {
        name: { type: String, required: true, trim: true }, // e.g., "Filed", "Served", "Returned"
        description: { type: String, trim: true },
        order: { type: Number, required: true }, // Stage order in workflow
        status: {
            type: String,
            enum: ['Pending', 'In Progress', 'Completed', 'Failed'],
            default: 'Pending'
        },
        completedAt: { type: Date, default: null }
    },
    { _id: false }
);

// ------------------------------------------
// Workflow Schema
// ------------------------------------------
const workflowSchema = new mongoose.Schema(
    {
        // 1) Identity
        workflowName: { type: String, required: true, trim: true, index: true },
        description: { type: String, trim: true },

        // 2) Relations
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        document: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 3) Stages
        stages: { type: [stageSchema], default: [] },

        // 4) Status
        status: {
            type: String,
            enum: ['Draft', 'Active', 'Completed', 'Cancelled'],
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
workflowSchema.index({ status: 1, workflowName: 1 });
workflowSchema.index({ case: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Add a stage to the workflow.
 */
workflowSchema.methods.addStage = function (stage) {
    this.stages.push(stage);
    this.history.push({
        action: 'STAGE_ADDED',
        by: stage.by || undefined,
        reason: `Stage '${stage.name}' added`
    });
    return this.save();
};

/**
 * Mark a stage as completed.
 */
workflowSchema.methods.completeStage = function (stageName, options = {}) {
    const stage = this.stages.find((s) => s.name === stageName);
    if (!stage) throw new Error(`Stage '${stageName}' not found`);
    stage.status = 'Completed';
    stage.completedAt = new Date();
    this.history.push({
        action: 'STAGE_COMPLETED',
        by: options.by || undefined,
        reason: options.reason || `Stage '${stageName}' marked as completed`
    });
    return this.save();
};

/**
 * Transition workflow status with audit history.
 */
workflowSchema.methods.transitionStatus = function (nextStatus, options = {}) {
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
module.exports = mongoose.model('Workflow', workflowSchema);
