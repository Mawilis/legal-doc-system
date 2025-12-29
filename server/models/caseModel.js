/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/models/caseModel.js
 *
 * Enterprise Case Model (Masterpiece Edition)
 * -------------------------------------------
 * Complete, production-grade schema for managing legal cases.
 * - Identity: case code, title, type, and description.
 * - Relations: clients, courts, documents, events, invoices, payments, alerts.
 * - Governance: status lifecycle, participants, compliance rules, retention policies.
 * - Audit: full history of transitions, assignments, and updates.
 * - Performance: indexed for queries by status, caseCode, and createdAt.
 */

'use strict';

const mongoose = require('mongoose');

// ------------------------------------------
// Audit History Sub-Schema
// ------------------------------------------
const historySchema = new mongoose.Schema(
    {
        action: { type: String, required: true, trim: true }, // e.g., "STATUS_CHANGED", "PARTICIPANT_ADDED"
        by: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
        date: { type: Date, default: Date.now },
        reason: { type: String, trim: true },
        diff: { type: Object, default: {} }
    },
    { _id: false }
);

// ------------------------------------------
// Participant Sub-Schema
// ------------------------------------------
const participantSchema = new mongoose.Schema(
    {
        user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
        role: { type: String, trim: true }, // e.g., "Plaintiff", "Defendant", "Attorney"
        joinedAt: { type: Date, default: Date.now }
    },
    { _id: false }
);

// ------------------------------------------
// Case Schema
// ------------------------------------------
const caseSchema = new mongoose.Schema(
    {
        // 1) Identity
        caseCode: { type: String, required: true, unique: true, index: true }, // e.g., "CASE-2025-001"
        title: { type: String, required: true, trim: true },
        type: { type: String, required: true, trim: true }, // e.g., "Civil", "Criminal", "Family"
        description: { type: String, trim: true },

        // 2) Relations
        client: { type: mongoose.Schema.Types.ObjectId, ref: 'Client' },
        court: { type: mongoose.Schema.Types.ObjectId, ref: 'Court' },
        documents: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Document' }],
        events: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Event' }],
        invoices: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Invoice' }],
        payments: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Payment' }],
        alerts: [{ type: mongoose.Schema.Types.ObjectId, ref: 'AlertLog' }],
        complianceRule: { type: mongoose.Schema.Types.ObjectId, ref: 'Compliance' },
        retentionPolicy: { type: mongoose.Schema.Types.ObjectId, ref: 'Retention' },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 3) Participants
        participants: { type: [participantSchema], default: [] },

        // 4) Status
        status: {
            type: String,
            enum: ['Open', 'In Progress', 'On Hold', 'Closed', 'Archived'],
            default: 'Open',
            index: true
        },
        openedAt: { type: Date, default: Date.now },
        closedAt: { type: Date, default: null },

        // 5) Metadata
        tags: { type: [String], default: [] },
        meta: { type: Object, default: {} },

        // 6) Audit
        history: { type: [historySchema], default: [] }
    },
    { timestamps: true }
);

// ------------------------------------------
// Indexes
// ------------------------------------------
caseSchema.index({ status: 1, caseCode: 1 });
caseSchema.index({ client: 1, createdAt: -1 });
caseSchema.index({ court: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Add a participant to the case.
 */
caseSchema.methods.addParticipant = function (userId, role, actor) {
    this.participants.push({ user: userId, role });
    this.history.push({
        action: 'PARTICIPANT_ADDED',
        by: actor?._id,
        reason: `Participant ${userId} added as ${role}`
    });
    return this.save();
};

/**
 * Transition case status with audit history.
 */
caseSchema.methods.transitionStatus = function (nextStatus, actor, reason) {
    const current = this.status;
    this.status = nextStatus;
    if (nextStatus === 'Closed') this.closedAt = new Date();
    this.history.push({
        action: 'STATUS_CHANGED',
        by: actor?._id,
        reason: reason || `Status changed from '${current}' to '${nextStatus}'`
    });
    return this.save();
};

/**
 * Link a document to the case.
 */
caseSchema.methods.addDocument = function (docId, actor) {
    this.documents.push(docId);
    this.history.push({
        action: 'DOCUMENT_LINKED',
        by: actor?._id,
        reason: `Document ${docId} linked to case`
    });
    return this.save();
};

/**
 * Link an event to the case.
 */
caseSchema.methods.addEvent = function (eventId, actor) {
    this.events.push(eventId);
    this.history.push({
        action: 'EVENT_LINKED',
        by: actor?._id,
        reason: `Event ${eventId} linked to case`
    });
    return this.save();
};

// ------------------------------------------
// Model Export
// ------------------------------------------
module.exports = mongoose.model('Case', caseSchema);
