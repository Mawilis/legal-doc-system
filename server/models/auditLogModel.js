// server/models/auditLogModel.js

const mongoose = require('mongoose');

const auditLogSchema = new mongoose.Schema(
    {
        // The user who performed the action.
        user: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User',
            required: true,
        },
        // The action that was performed (e.g., 'DOCUMENT_UPDATED', 'USER_LOGIN_FAILED').
        action: {
            type: String,
            required: [true, 'An action is required for the audit log.'],
            trim: true,
        },
        // A more detailed description of the event.
        details: {
            type: String,
            trim: true,
        },
        // The IP address from which the action was performed.
        ipAddress: {
            type: String,
        },
        // The status of the action.
        status: {
            type: String,
            enum: ['SUCCESS', 'FAILURE'],
            required: true,
        },
        // Optional: The entity that was affected by the action (e.g., a Document ID).
        entity: {
            id: {
                type: mongoose.Schema.Types.ObjectId,
            },
            type: {
                type: String, // e.g., 'Document', 'User', 'Client'
            }
        }
    },
    {
        timestamps: { createdAt: true, updatedAt: false }, // We only care about when the log was created.
        // Capped collections are high-performance and have a fixed size.
        // They are perfect for logs, as old entries are automatically removed
        // once the collection reaches its maximum size.
        capped: { size: 1024 * 1024 * 50, max: 50000 } // e.g., 50MB or 50,000 documents
    }
);

// Create an index for faster querying of logs by user or action.
auditLogSchema.index({ user: 1, action: 1 });

const AuditLog = mongoose.model('AuditLog', auditLogSchema);

module.exports = AuditLog;
