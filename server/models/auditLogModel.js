// ~/legal-doc-system/server/models/auditLogModel.js

const mongoose = require('mongoose');

/**
 * Defines the Mongoose schema for an audit log entry.
 * This schema creates a comprehensive and indexed record for every API request,
 * which is essential for security, debugging, and compliance purposes.
 */
const auditLogSchema = new mongoose.Schema({
    // A reference to the user who made the request. Null if the request was unauthenticated.
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User', // This should match the name of your User model
        default: null,
        index: true, // Indexing this field improves query performance when filtering by user.
    },
    // The user's email is stored for quick reference and denormalization.
    // This is useful even if the original user document is deleted.
    email: {
        type: String,
        default: 'Guest',
    },
    // The HTTP method of the request (e.g., GET, POST, PUT, DELETE).
    method: {
        type: String,
        required: true,
    },
    // The API endpoint path that was accessed by the request.
    path: {
        type: String,
        required: true,
    },
    // The final status of the request, updated after the response is sent.
    status: {
        type: String,
        enum: ['PENDING', 'SUCCESS', 'FAILED'], // Ensures only valid statuses can be saved.
        default: 'PENDING',
        index: true, // Indexing status helps in quickly finding failed or successful requests.
    },
    // The IP address of the client making the request, for security tracking.
    ip: {
        type: String,
    },
    // The time in milliseconds it took the server to process and respond to the request.
    responseTime: {
        type: Number,
    },
}, {
    // Mongoose's built-in timestamp option automatically adds `createdAt` and `updatedAt` fields.
    timestamps: true
});

// Compile the schema into a Mongoose model.
const AuditLog = mongoose.model('AuditLog', auditLogSchema);

module.exports = AuditLog;
