/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/models/alertLogModel.js
 *
 * Enterprise Alert Log Model (Masterpiece Edition)
 * ------------------------------------------------
 * Complete, production-grade schema for tracking alerts and system warnings.
 * - Identity: alert code, type, severity, and message.
 * - Relations: cases, documents, users, workflows, compliance rules.
 * - Lifecycle: raised → acknowledged → resolved → archived.
 * - Governance: audit history, escalation, and compliance integration.
 * - Performance: indexed for queries by severity, status, and createdAt.
 */

'use strict';

const mongoose = require('mongoose');

// ------------------------------------------
// Audit History Sub-Schema
// ------------------------------------------
const historySchema = new mongoose.Schema(
    {
        action: { type: String, required: true, trim: true }, // e.g., "STATUS_CHANGED", "ACKNOWLEDGED"
        by: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
        date: { type: Date, default: Date.now },
        reason: { type: String, trim: true },
        diff: { type: Object, default: {} }
    },
    { _id: false }
);

// ------------------------------------------
// Alert Log Schema
// ------------------------------------------
const alertLogSchema = new mongoose.Schema(
    {
        // 1) Identity
        alertCode: { type: String, required: true, unique: true, index: true }, // e.g., "ALERT-2025-001"
        type: { type: String, required: true, trim: true }, // e.g., "System", "Compliance", "Security"
        severity: {
            type: String,
            enum: ['Info', 'Warning', 'Error', 'Critical'],
            default: 'Info',
            index: true
        },
        message: { type: String, required: true, trim: true },
        description: { type: String, trim: true },

        // 2) Relations
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        document: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
        workflow: { type: mongoose.Schema.Types.ObjectId, ref: 'Workflow' },
        complianceRule: { type: mongoose.Schema.Types.ObjectId, ref: 'Compliance' },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 3) Lifecycle
        status: {
            type: String,
            enum: ['Raised', 'Acknowledged', 'Resolved', 'Archived'],
            default: 'Raised',
            index: true
        },
        acknowledgedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
        acknowledgedAt: { type: Date, default: null },
        resolvedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
        resolvedAt: { type: Date, default: null },

        // 4) Escalation
        escalationLevel: { type: Number, default: 0 }, // 0=none, 1=team lead, 2=partner, 3=executive
        escalationNote: { type: String, trim: true },

        // 5) Metadata
        meta: { type: Object, default: {} },

        // 6) Audit
        history: { type: [historySchema], default: [] }
    },
    { timestamps: true }
);

// ------------------------------------------
// Indexes
// ------------------------------------------
alertLogSchema.index({ severity: 1, status: 1 });
alertLogSchema.index({ case: 1, createdAt: -1 });
alertLogSchema.index({ workflow: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Acknowledge alert.
 */
alertLogSchema.methods.acknowledge = function (actor, reason) {
    this.status = 'Acknowledged';
    this.acknowledgedBy = actor?._id;
    this.acknowledgedAt = new Date();
    this.history.push({
        action: 'ACKNOWLEDGED',
        by: actor?._id,
        reason: reason || 'Alert acknowledged'
    });
    return this.save();
};

/**
 * Resolve alert.
 */
alertLogSchema.methods.resolve = function (actor, reason) {
    this.status = 'Resolved';
    this.resolvedBy = actor?._id;
    this.resolvedAt = new Date();
    this.history.push({
        action: 'RESOLVED',
        by: actor?._id,
        reason: reason || 'Alert resolved'
    });
    return this.save();
};

/**
 * Escalate alert.
 */
alertLogSchema.methods.escalate = function (level, actor, note) {
    this.escalationLevel = level;
    this.escalationNote = note || '';
    this.history.push({
        action: 'ESCALATED',
        by: actor?._id,
        reason: note || `Escalated to level ${level}`
    });
    return this.save();
};

/**
 * Transition status with audit history.
 */
alertLogSchema.methods.transitionStatus = function (nextStatus, actor, reason) {
    const current = this.status;
    this.status = nextStatus;
    this.history.push({
        action: 'STATUS_CHANGED',
        by: actor?._id,
        reason: reason || `Status changed from '${current}' to '${nextStatus}'`
    });
    return this.save();
};

// ------------------------------------------
// Model Export
// ------------------------------------------
module.exports = mongoose.model('AlertLog', alertLogSchema);
