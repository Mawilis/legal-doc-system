/*
 * File: server/middleware/metricsMiddleware.js
 * STATUS: PRODUCTION-READY | OBSERVABILITY & SCALE GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Instrumenting the Wilsy API for real-time monitoring. It tracks the "Golden Signals":
 * Latency, Traffic, Errors, and Saturation.
 *
 * KEY FEATURES FOR FUTURE ENGINEERS:
 * 1. Prometheus Integration: Exposes standard metrics for Grafana dashboards.
 * 2. Path Normalization: Prevents high-cardinality issues by masking IDs.
 * 3. Performance Profiling: Uses high-resolution timers (hrtime) for accuracy.
 * 4. Tenant Analytics: Track which firms are consuming the most resources.
 * -----------------------------------------------------------------------------
 */

'use strict';

const client = require('prom-client');

// 1. REGISTRY & DEFAULT METRICS
// Collects Node.js health (CPU, Memory, Event Loop Lag) automatically.
const register = new client.Registry();
client.collectDefaultMetrics({ register, prefix: 'wilsy_' });

// 2. CUSTOM HTTP METRICS
const httpRequestsTotal = new client.Counter({
    name: 'wilsy_api_requests_total',
    help: 'Total number of HTTP requests processed',
    labelNames: ['method', 'route', 'status', 'tenant_id']
});

const httpRequestDuration = new client.Histogram({
    name: 'wilsy_api_request_duration_seconds',
    help: 'Latency of API requests in seconds',
    labelNames: ['method', 'route', 'status', 'tenant_id'],
    buckets: [0.1, 0.3, 0.5, 0.7, 1, 2, 5] // Focused on legal document processing times
});

// 3. PATH NORMALIZATION UTILITY
// Prevents /cases/1 and /cases/2 from becoming two different metric lines.
const normalizePath = (req) => {
    return req.route ? req.route.path : req.originalUrl.split('?')[0];
};

/**
 * METRICS MIDDLEWARE
 */
const metricsMiddleware = (req, res, next) => {
    const start = process.hrtime();

    // The 'finish' event triggers after the response is sent to the client.
    res.on('finish', () => {
        const diff = process.hrtime(start);
        const durationSeconds = diff[0] + diff[1] / 1e9;

        const labels = {
            method: req.method,
            route: normalizePath(req),
            status: res.statusCode,
            tenant_id: req.user?.tenantId || 'anonymous'
        };

        // RECORD METRICS
        httpRequestsTotal.labels(labels).inc();
        httpRequestDuration.labels(labels).observe(durationSeconds);

        // FORENSIC ALERT: Log extremely slow requests to the audit trail
        if (durationSeconds > 5 && req.logAudit) {
            req.logAudit('PERFORMANCE_SLA_VIOLATION', {
                duration: `${durationSeconds.toFixed(2)}s`,
                path: req.originalUrl,
                userId: req.user?._id
            });
        }
    });

    next();
};

/**
 * SCRAPE ENDPOINT
 * This is where Prometheus "calls" your server to get the latest numbers.
 * Protected via internal IP whitelist or basic auth in production.
 */
const metricsEndpoint = async (req, res) => {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
};

module.exports = {
    metricsMiddleware,
    metricsEndpoint
};