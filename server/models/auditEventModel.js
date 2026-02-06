/**
 * =============================================================================
 * FILE: server/models/auditEventModel.js
 * PURPOSE: Immutable audit log schema for compliance (POPIA/ECT Act)
 * =============================================================================
 */
const mongoose = require('mongoose'); // FIXED: Removed illegal version tag

const AuditEventSchema = new mongoose.Schema({
    // 1. TIMING & RETENTION
    timestamp: {
        type: Date,
        default: Date.now,
        index: true,
        immutable: true
    },
    
    // 2. TENANT CONTEXT (Multi-tenant Security)
    tenantId: {
        type: String,
        required: true,
        index: true
    },

    // 3. ACTOR (Who did it?)
    actor: {
        userId: { type: String, index: true },
        email: String,
        ipAddress: String,
        userAgent: String,
        role: String
    },

    // 4. ACTION (What happened?)
    action: {
        type: String,
        required: true,
        index: true // e.g., 'CASE_CREATED', 'DOCUMENT_DELETED'
    },
    category: {
        type: String,
        enum: ['AUTH', 'ACCESS', 'MODIFICATION', 'DELETION', 'SECURITY'],
        default: 'ACCESS'
    },
    status: {
        type: String,
        enum: ['SUCCESS', 'FAILURE', 'DENIED'],
        default: 'SUCCESS'
    },

    // 5. RESOURCE (What was touched?)
    resource: {
        entityType: String, // e.g., 'Case', 'Document'
        entityId: String,
        ownerId: String
    },

    // 6. CHANGES (Data delta)
    changes: {
        before: mongoose.Schema.Types.Mixed,
        after: mongoose.Schema.Types.Mixed
    },

    // 7. CRYPTOGRAPHIC PROOF (Non-repudiation)
    integrity: {
        hash: String, // SHA-256 of this event
        previousHash: String // Blockchain-style linking
    }
}, {
    timestamps: true,
    collection: 'audit_events'
});

// Index for compliance reporting (e.g., "Show me all deletions by User X")
AuditEventSchema.index({ tenantId: 1, action: 1, timestamp: -1 });
AuditEventSchema.index({ 'actor.userId': 1, timestamp: -1 });

module.exports = mongoose.model('AuditEvent', AuditEventSchema);
