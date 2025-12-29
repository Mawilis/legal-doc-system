/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/services/sessionService.js
 *
 * Session Service
 * ---------------
 * Helpers for issuing, validating, and revoking sessions.
 */

const Session = require('../models/sessionModel');

exports.revokeAllSessionsForUser = async (userId, reason = 'security_password_reset') => {
    const now = new Date();
    await Session.updateMany(
        { userId, valid: true },
        { $set: { valid: false, revokedAt: now, revokedReason: reason } }
    );
};

exports.revokeSessionByHash = async (refreshTokenHash, reason = 'manual_logout') => {
    const now = new Date();
    await Session.updateOne(
        { refreshTokenHash, valid: true },
        { $set: { valid: false, revokedAt: now, revokedReason: reason } }
    );
};

exports.isSessionValid = async (refreshTokenHash) => {
    const s = await Session.findOne({ refreshTokenHash }).lean();
    return !!(s && s.valid && s.expiresAt > new Date());
};
