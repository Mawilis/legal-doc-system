// File: /Users/wilsonkhanyezi/legal-doc-system/server/models/Document.js
// Status: PRODUCTION-READY (Idempotent Fix Applied)
// -----------------------------------------------------------------------------
// COLLABORATION NOTES:
// - This file defines the Document model used across Gateway, Dashboard, and
//   Document routes. It is central to tenant isolation and auditability.
// - The schema includes status, priority, sheriff assignment, financial amount,
//   and embedded history for audit trails.
// - The "Billion Dollar Fix" at the bottom ensures idempotency: if the model
//   has already been compiled by Mongoose, we reuse it instead of redefining.
// - Please keep comments updated when making schema changes so new engineers
//   can understand why fields and indexes exist.
// - When adding new fields, always consider tenant scoping, compliance, and
//   audit requirements. Document changes should be discussed with both backend
//   and frontend collaborators.
// -----------------------------------------------------------------------------

'use strict';

const mongoose = require('mongoose');

// -----------------------------------------------------------------------------
// ENUMS: Shared constants for status and priority.
// These values are referenced in controllers, services, and tests.
// -----------------------------------------------------------------------------
const STATUS = {
    PENDING: 'pending',
    IN_PROGRESS: 'in_progress',
    COMPLETED: 'completed',
    URGENT: 'urgent'
};

const PRIORITY = {
    NORMAL: 'normal',
    HIGH: 'high',
    URGENT: 'urgent'
};

// -----------------------------------------------------------------------------
// SUBDOCUMENT: HistorySchema
// Captures audit trail of changes to a document.
// Each entry records who changed it, what type of change, and a diff snapshot.
// -----------------------------------------------------------------------------
const HistorySchema = new mongoose.Schema({
    changedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: false },
    changeType: { type: String, required: true },
    diff: { type: mongoose.Schema.Types.Mixed },
    ts: { type: Date, default: Date.now }
}, { _id: false });

// -----------------------------------------------------------------------------
// MAIN SCHEMA: DocumentSchema
// Represents a legal document in the system.
// Includes tenant scoping, metadata, audit history, and compliance fields.
// -----------------------------------------------------------------------------
const DocumentSchema = new mongoose.Schema({
    tenantId: { type: mongoose.Schema.Types.ObjectId, index: true, required: true },
    title: { type: String, required: true, trim: true },
    description: { type: String, default: '' },
    status: { type: String, enum: Object.values(STATUS), default: STATUS.PENDING, index: true },
    priority: { type: String, enum: Object.values(PRIORITY), default: PRIORITY.NORMAL, index: true },
    sheriffId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: false },
    amount: { type: Number, default: 0, min: 0 },
    deleted: { type: Boolean, default: false, index: true },
    deletedAt: { type: Date, default: null },
    history: { type: [HistorySchema], default: [] },
    metadata: { type: mongoose.Schema.Types.Mixed, default: {} }
}, {
    timestamps: true,
    toJSON: { virtuals: true, transform: (doc, ret) => { delete ret.__v; return ret; } },
    toObject: { virtuals: true }
});

// -----------------------------------------------------------------------------
// INDEXES: Performance and search optimization.
// - tenantId + status + createdAt: for dashboard queries.
// - tenantId + priority + updatedAt: for prioritization.
// - text index on title/description: for search.
// -----------------------------------------------------------------------------
DocumentSchema.index({ tenantId: 1, status: 1, createdAt: -1 }, { partialFilterExpression: { deleted: false } });
DocumentSchema.index({ tenantId: 1, priority: 1, updatedAt: -1 }, { partialFilterExpression: { deleted: false } });
DocumentSchema.index({ title: 'text', description: 'text' }, { weights: { title: 5, description: 1 }, background: true });

// -----------------------------------------------------------------------------
// BILLION DOLLAR FIX: Idempotent model definition.
// Prevents "Cannot overwrite model once compiled" errors when required multiple times.
// -----------------------------------------------------------------------------
const DocumentModel = mongoose.models.Document || mongoose.model('Document', DocumentSchema);

// -----------------------------------------------------------------------------
// EXPORTS: Model and enums.
// Collaborators: always import STATUS and PRIORITY from here to avoid drift.
// -----------------------------------------------------------------------------
module.exports = DocumentModel;
module.exports.STATUS = STATUS;
module.exports.PRIORITY = PRIORITY;
