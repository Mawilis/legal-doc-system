/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/models/activityLogModel.js
 *
 * Activity Log Model
 * ------------------
 * General user activity logs (views, searches, downloads, edits).
 */

const mongoose = require('mongoose');

const activityLogSchema = new mongoose.Schema(
    {
        actorId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', index: true },
        actorRole: { type: String, trim: true, lowercase: true },
        action: { type: String, required: true, trim: true, lowercase: true, index: true }, // e.g., 'document.view'
        targetType: { type: String, required: true, trim: true, lowercase: true, index: true }, // 'document', 'case'
        targetId: { type: String, required: true, trim: true, index: true },
        metadata: { type: Map, of: String, default: {} }, // contextual info (search query, filters)
        ipAddress: { type: String, trim: true },
        userAgent: { type: String, trim: true },
        occurredAt: { type: Date, default: Date.now, index: true },
    },
    { timestamps: true }
);

activityLogSchema.index({ action: 1, occurredAt: -1 });
activityLogSchema.index({ targetType: 1, targetId: 1, occurredAt: -1 });

module.exports = mongoose.model('ActivityLog', activityLogSchema);
