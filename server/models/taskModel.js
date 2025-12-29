/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/models/taskModel.js
 *
 * Task Model
 * ----------
 * Tracks background jobs (report generation, email dispatch, compliance checks).
 */

const mongoose = require('mongoose');

const taskSchema = new mongoose.Schema(
    {
        type: { type: String, required: true, trim: true, lowercase: true, index: true }, // e.g., 'report.generate'
        status: {
            type: String,
            required: true,
            enum: ['queued', 'running', 'completed', 'failed', 'cancelled'],
            default: 'queued',
            index: true,
        },
        payload: { type: mongoose.Schema.Types.Mixed, default: {} }, // input params
        result: { type: mongoose.Schema.Types.Mixed, default: {} }, // output or summary
        error: { type: String, trim: true },
        queuedAt: { type: Date, default: Date.now, index: true },
        startedAt: { type: Date },
        completedAt: { type: Date },
        retryCount: { type: Number, default: 0 },
        maxRetries: { type: Number, default: 3 },
        priority: { type: Number, default: 5, index: true }, // 1 highest, 10 lowest
        correlationId: { type: String, trim: true, index: true }, // trace across systems
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    },
    { timestamps: true }
);

taskSchema.index({ type: 1, status: 1, priority: 1 });

module.exports = mongoose.model('Task', taskSchema);
