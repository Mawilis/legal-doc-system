const logger = require('../utils/logger');

// Fields to redact in body
const SENSITIVE_FIELDS = ['password', 'token', 'authorization'];

const sanitize = (obj) => {
    const clone = { ...obj };
    for (const field of SENSITIVE_FIELDS) {
        if (clone[field]) {
            clone[field] = '[REDACTED]';
        }
    }
    return clone;
};

const requestLogger = (req, res, next) => {
    const method = req.method;
    const url = req.originalUrl;
    const body = sanitize(req.body || {});
    const headers = sanitize(req.headers || {});

    logger.info(`📥 [${method}] ${url} - Body: ${JSON.stringify(body)} - IP: ${req.ip}`);

    next();
};

module.exports = requestLogger;
