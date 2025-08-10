// ~/server/middleware/auditLogger.js

const AuditLog = require('../models/auditLogModel');
const logger = require('../utils/logger');

const auditLogger = async (req, res, next) => {
    const user = req.user;
    const method = req.method;
    const path = req.originalUrl;

    const log = new AuditLog({
        user: user?._id || null,
        email: user?.email || 'Guest',
        method,
        path,
        status: 'PENDING',
        ip: req.ip,
        timestamp: new Date(),
    });

    await log.save();

    const originalSend = res.send;
    res.send = function (body) {
        log.status = res.statusCode < 400 ? 'SUCCESS' : 'FAILED';
        log.responseTime = Date.now() - new Date(log.timestamp);
        log.save().catch((err) => logger.error('Audit log update failed:', err));
        return originalSend.call(this, body);
    };

    next();
};

module.exports = auditLogger;
