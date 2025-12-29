/**
 * ~/server/models/storageModel.js
 *
 * Enterprise Storage Model
 * ------------------------
 * Collaboration-ready, production-grade schema for managing storage of documents.
 * - Supports digital and physical storage types.
 * - Links to cases, documents, compliance, and retention policies.
 * - Tracks storage lifecycle with audit history.
 * - Indexed for performance on status and storageCode.
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
// Storage Schema
// ------------------------------------------
const storageSchema = new mongoose.Schema(
    {
        // 1) Identity
        storageCode: { type: String, required: true, unique: true, index: true }, // e.g., "STOR-2025-001"
        name: { type: String, required: true, trim: true }, // e.g., "Digital Archive A"
        description: { type: String, trim: true },

        // 2) Type
        type: {
            type: String,
            enum: ['Digital', 'Physical'],
            required: true,
            index: true
        },

        // 3) Location
        location: { type: String, trim: true }, // e.g., "Server Cluster A" or "Warehouse B"

        // 4) Relations
        case: { type: mongoose.Schema.Types.ObjectId, ref: 'Case' },
        document: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
        complianceRule: { type: mongoose.Schema.Types.ObjectId, ref: 'Compliance' },
        retentionPolicy: { type: mongoose.Schema.Types.ObjectId, ref: 'Retention' },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 5) Status
        status: {
            type: String,
            enum: ['Active', 'Archived', 'Disposed', 'Unavailable'],
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
storageSchema.index({ status: 1, type: 1 });
storageSchema.index({ storageCode: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Transition storage status with audit history.
 */
storageSchema.methods.transitionStatus = function (nextStatus, options = {}) {
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
 * Link a document to storage.
 */
storageSchema.methods.addDocument = function (docId, options = {}) {
    this.document = docId;
    this.history.push({
        action: 'DOCUMENT_LINKED',
        by: options.by || undefined,
        reason: options.reason || `Document ${docId} linked to storage`
    });
    return this.save();
};

// ------------------------------------------
// Model Export
// ------------------------------------------
module.exports = mongoose.model('Storage', storageSchema);
