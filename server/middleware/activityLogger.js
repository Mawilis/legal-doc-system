/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/middleware/activityLogger.js
 *
 * Activity Logger Middleware
 * --------------------------
 * Emits activity logs for views, downloads, searches, edits.
 */

const ActivityLog = require('../models/activityLogModel');

exports.logActivity = (action, targetType, getTargetId, getMeta = () => ({})) => {
    return async (req, res, next) => {
        try {
            const actorId = req.user?.id || null;
            const actorRole = req.user?.role || null;
            const targetId = typeof getTargetId === 'function' ? getTargetId(req) : getTargetId;
            const ipAddress = req.ip || req.connection?.remoteAddress || 'unknown';
            const userAgent = (req.headers['user-agent'] || '').slice(0, 256);

            await ActivityLog.create({
                actorId,
                actorRole,
                action,
                targetType,
                targetId: String(targetId || ''),
                metadata: getMeta(req),
                ipAddress,
                userAgent,
                occurredAt: new Date(),
            });
        } catch (err) {
            console.warn('Activity log failed:', err.message);
        }
        next();
    };
};
