/**
 * ~/server/models/auditModel.js
 *
 * Enterprise Audit Model
 * ----------------------
 * Collaboration-ready, production-grade schema for structured compliance audits.
 * - Records audit type, scope, findings, and corrective actions.
 * - Links to cases, documents, invoices, and users.
 * - Tracks audit lifecycle with audit history.
 * - Indexed for performance on status and auditCode.
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
// Audit Finding Sub-Schema
// ------------------------------------------
const findingSchema = new mongoose.Schema(
    {
        description: { type: String, required: true, trim: true },
        severity: {
            type: String,
            enum: ['Low', 'Medium', 'High', 'Critical'],
            default: 'Low'
        },
        correctiveAction: { type: String, trim: true },
        resolved: { type: Boolean, default: false },
        resolvedAt: { type: Date, default: null }
    },
    { _id: false }
);

// ------------------------------------------
// Audit Schema
// ------------------------------------------
const auditSchema = new mongoose.Schema(
    {
        // 1) Identity
        auditCode: { type: String, required: true, unique: true, index: true }, // e.g., "AUD-2025-001"
        auditType: { type: String, required: true, trim: true }, // e.g., "Financial", "Compliance", "Operational"
        description: { type: String, trim: true },

        // 2) Scope & Relations
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        document: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
        invoice: { type: mongoose.Schema.Types.ObjectId, ref: 'Invoice' },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 3) Findings
        findings: { type: [findingSchema], default: [] },

        // 4) Status
        status: {
            type: String,
            enum: ['Planned', 'In Progress', 'Completed', 'Closed'],
            default: 'Planned',
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
auditSchema.index({ status: 1, auditType: 1 });
auditSchema.index({ createdBy: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Add a finding to the audit.
 */
auditSchema.methods.addFinding = function (finding) {
    this.findings.push(finding);
    this.history.push({
        action: 'FINDING_ADDED',
        by: finding.by || undefined,
        reason: `Finding '${finding.description}' added`
    });
    return this.save();
};

/**
 * Resolve a finding.
 */
auditSchema.methods.resolveFinding = function (description, options = {}) {
    const finding = this.findings.find((f) => f.description === description);
    if (!finding) throw new Error(`Finding '${description}' not found`);
    finding.resolved = true;
    finding.resolvedAt = new Date();
    this.history.push({
        action: 'FINDING_RESOLVED',
        by: options.by || undefined,
        reason: options.reason || `Finding '${description}' resolved`
    });
    return this.save();
};

/**
 * Transition audit status with audit history.
 */
auditSchema.methods.transitionStatus = function (nextStatus, options = {}) {
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
module.exports = mongoose.model('Audit', auditSchema);
