/*
 * File: server/middleware/requestLogger.js
 * STATUS: PRODUCTION-READY | OPERATIONAL OBSERVABILITY GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Captures the lifecycle of every HTTP transaction. This is the primary data source 
 * for calculating system uptime, performance SLAs, and error rates.
 *
 * KEY FEATURES FOR FUTURE ENGINEERS:
 * 1. High-Resolution Timing: Uses hrtime for micro-second precision.
 * 2. Structured Output: JSON-formatted logs for easy ingestion by ELK/Splunk.
 * 3. Latency Monitoring: Identifies slow database queries or external API calls.
 * 4. Tenant-Aware: Ties every log entry to a specific firm for billing/support.
 * -----------------------------------------------------------------------------
 */

'use strict';

/**
 * REQUEST LOGGER MIDDLEWARE
 */
const requestLogger = (req, res, next) => {
    // 1. START PERFORMANCE CLOCK
    const start = process.hrtime();

    // 2. POST-RESPONSE HOOK
    // We listen for 'finish' to ensure we capture the final status and latency.
    res.on('finish', () => {
        try {
            // Calculate precise duration in milliseconds
            const diff = process.hrtime(start);
            const durationMs = (diff[0] * 1e3 + diff[1] * 1e-6).toFixed(3);

            // Extract context (Populated by earlier middleware like auth/correlation)
            const logEntry = {
                timestamp: new Date().toISOString(),
                correlationId: req.correlationId || 'none',
                tenantId: req.user?.tenantId || req.headers['x-tenant-id'] || 'anonymous',
                userId: req.user?._id || 'anonymous',
                request: {
                    method: req.method,
                    path: req.originalUrl,
                    ip: req.ip,
                    // Track size to monitor bandwidth/S3 costs
                    contentLength: req.headers['content-length'] || 0
                },
                response: {
                    statusCode: res.statusCode,
                    durationMs,
                    // Track response size for egress monitoring
                    contentLength: res.get('Content-Length') || 0
                }
            };

            // 3. SEVERITY CLASSIFICATION
            let severity = 'INFO';
            if (res.statusCode >= 500) severity = 'CRITICAL';
            else if (res.statusCode >= 400) severity = 'WARNING';

            // 4. CONSOLE OUTPUT
            // In Production, this goes to stdout, which is captured by Docker/Kubernetes logs.
            const logString = `[${severity}] ${logEntry.request.method} ${logEntry.request.path} ${logEntry.response.statusCode} (${durationMs}ms)`;

            if (process.env.NODE_ENV === 'development') {
                console.log(logString);
            } else {
                // Structured JSON for production monitoring
                console.log(JSON.stringify({ ...logEntry, severity }));
            }

            // 5. FORENSIC AUDIT EMISSION
            // If the request was unusually slow (> 2s), we escalate it to the Audit Log.
            if (parseFloat(durationMs) > 2000 && req.logAudit) {
                req.logAudit('LATENCY_SLA_WARNING', {
                    duration: `${durationMs}ms`,
                    path: req.originalUrl
                });
            }

        } catch (err) {
            // Silently handle logging errors to avoid interrupting the server process.
            console.error('INTERNAL_LOGGER_FAULT:', err);
        }
    });

    next();
};

module.exports = requestLogger;