/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/models/sessionModel.js
 *
 * Session Model
 * -------------
 * Tracks user sessions, refresh tokens, devices, and revocation status.
 */

const mongoose = require('mongoose');

const sessionSchema = new mongoose.Schema(
    {
        userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, index: true },
        refreshTokenHash: { type: String, required: true, unique: true }, // store hash, not raw token
        userAgent: { type: String, trim: true },
        ipAddress: { type: String, trim: true },
        deviceId: { type: String, trim: true, index: true }, // stable device identifier if available
        locationHint: { type: String, trim: true }, // optional geo hint
        valid: { type: Boolean, default: true, index: true },
        issuedAt: { type: Date, default: Date.now },
        expiresAt: { type: Date, required: true, index: true },
        revokedAt: { type: Date },
        revokedReason: { type: String, trim: true },
    },
    { timestamps: true }
);

sessionSchema.index({ userId: 1, valid: 1 });
sessionSchema.index({ expiresAt: 1 });

module.exports = mongoose.model('Session', sessionSchema);
