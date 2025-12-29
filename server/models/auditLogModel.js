/**
 * ~/server/models/auditLogModel.js
 *
 * Enterprise Audit Log Model
 * --------------------------
 * Tracks every request and programmatic event for compliance and monitoring.
 * - Links to User for accountability.
 * - Captures method, path, IP, status, statusCode, responseTime.
 * - Allows optional message and meta fields for extended context.
 * - Includes timestamps for createdAt and updatedAt.
 */

'use strict';

const mongoose = require('mongoose');

const auditLogSchema = new mongoose.Schema(
    {
        // 1) Relations
        user: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User',
            default: null
        },
        email: {
            type: String,
            default: 'Guest'
        },

        // 2) Request Context
        method: {
            type: String,
            required: true,
            default: 'UNKNOWN'
        },
        path: {
            type: String,
            required: true,
            default: 'UNKNOWN'
        },
        ip: {
            type: String,
            default: '0.0.0.0'
        },

        // 3) Status & Response
        status: {
            type: String,
            enum: ['PENDING', 'SUCCESS', 'FAILED'],
            default: 'PENDING'
        },
        statusCode: {
            type: Number,
            default: null
        },
        responseTime: {
            type: Number,
            default: null
        },

        // 4) Optional Details
        message: {
            type: String,
            default: null
        },
        meta: {
            type: Object,
            default: null
        }
    },
    {
        timestamps: true // Adds createdAt and updatedAt
    }
);

// ------------------------------------------
// Indexes for performance
// ------------------------------------------
auditLogSchema.index({ status: 1, createdAt: -1 });
auditLogSchema.index({ user: 1, createdAt: -1 });
auditLogSchema.index({ path: 1, method: 1 });

// ------------------------------------------
// Static Methods
// ------------------------------------------
/**
 * Find logs by user email.
 */
auditLogSchema.statics.findByEmail = function (email) {
    return this.find({ email }).sort({ createdAt: -1 });
};

/**
 * Find failed logs in the last N minutes.
 */
auditLogSchema.statics.findRecentFailures = function (minutes = 60) {
    const cutoff = new Date(Date.now() - minutes * 60 * 1000);
    return this.find({ status: 'FAILED', createdAt: { $gte: cutoff } });
};

// ------------------------------------------
// Model Export
// ------------------------------------------
module.exports = mongoose.model('AuditLog', auditLogSchema);
