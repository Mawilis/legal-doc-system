/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/middleware/ipMetadata.js
 *
 * IP Metadata Capture
 * -------------------
 * Captures IP-related metadata for audit trails and anomaly detection.
 * Extend with geolocation or known-proxy lists as needed.
 */

const ipMetadata = (req, _res, next) => {
    const forwardedFor = req.headers['x-forwarded-for'];
    const ip = req.ip || req.connection?.remoteAddress || 'unknown';

    req.security = req.security || {};
    req.security.ip = {
        ip,
        forwardedFor: typeof forwardedFor === 'string' ? forwardedFor.split(',')[0].trim() : null,
        at: new Date().toISOString(),
    };

    // Optional: add geolocation enrichment here
    next();
};

module.exports = { ipMetadata };
