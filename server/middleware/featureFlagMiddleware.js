/**
 * File: server/middleware/featureFlagMiddleware.js
 * STATUS: PRODUCTION-READY | EPITOME | FEATURE GATEKEEPER
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Route-level middleware to gate endpoints by feature key. Designed for
 * production: fast-path evaluation, caching, admin bypasses, observability,
 * and safe failure modes. Use as:
 *   app.use('/api/new', featureFlag('NEW_DASHBOARD_V2'), newRouter)
 *
 * COLLABORATION COMMENTS:
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - REVIEWERS: @platform, @product, @sre, @security
 * - SECURITY: Admin bypasses must be protected by MFA and audited at the controller level.
 * - TESTING: Add unit tests for bypass flows, cache TTL, and evaluation logic.
 * -----------------------------------------------------------------------------
 */

'use strict';

const featureFlagService = require('../services/featureFlagService');
const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger'); // structured logger expected (info/warn/error)

/**
 * Factory: featureFlag
 * @param {string} key - canonical feature key (case-insensitive)
 * @param {Object} opts - options
 *   - allowRoles: array of roles that bypass the flag (e.g., ['SUPER_ADMIN', 'TENANT_ADMIN'])
 *   - bypassHeader: infra header name that bypasses the flag (default: 'x-wilsy-feature-bypass')
 *   - cacheTTL: ms to cache evaluation per-request (default: 1000)
 *   - hide404: boolean - if true return 404 when disabled (default true)
 *   - metricsClient: optional metrics client with .increment(name, tags)
 */
module.exports = function featureFlag(key, opts = {}) {
    if (!key || typeof key !== 'string') {
        throw new Error('featureFlag middleware requires a feature key string');
    }

    const {
        allowRoles = ['SUPER_ADMIN'],
        bypassHeader = 'x-wilsy-feature-bypass',
        cacheTTL = 1000,
        hide404 = true,
        metricsClient = null
    } = opts;

    // Per-key in-memory short-lived cache to reduce DB hits for high-throughput routes
    const evalCache = {
        value: null,
        ts: 0
    };

    async function evaluate(req) {
        const now = Date.now();
        if (evalCache.value && (now - evalCache.ts) < cacheTTL) {
            return evalCache.value;
        }

        const tenantId = req.context?.tenantId || req.headers['x-tenant-id'] || null;
        const userId = req.user?.id || req.user?._id || null;

        const enabled = await featureFlagService.isFeatureEnabled(key, { tenantId, userId });
        evalCache.value = enabled;
        evalCache.ts = Date.now();
        return enabled;
    }

    // Expose a cache invalidator for admin flows to call after flag updates
    function invalidateCache() {
        evalCache.value = null;
        evalCache.ts = 0;
    }

    // Attach invalidator so callers can clear when flags change
    featureFlag.invalidateCacheFor = featureFlag.invalidateCacheFor || {};
    featureFlag.invalidateCacheFor[key] = invalidateCache;

    return async function (req, res, next) {
        const correlationId = req.headers['x-correlation-id'] || uuidv4();
        res.setHeader('x-correlation-id', correlationId);

        try {
            // 1) Allow explicit infra bypass header (must be protected by infra)
            if (req.headers && req.headers[bypassHeader]) {
                logger.info('featureFlag: bypass header present', { key, correlationId, path: req.path });
                if (metricsClient && typeof metricsClient.increment === 'function') metricsClient.increment('feature.bypass.header', { feature: key });
                return next();
            }

            // 2) Allow roles attached to req.user (auth middleware should run earlier)
            if (req.user && req.user.role) {
                const role = String(req.user.role).toUpperCase();
                if (allowRoles.map(String).map((r) => r.toUpperCase()).includes(role)) {
                    logger.info('featureFlag: bypass via role', { key, role, correlationId, userId: req.user._id || req.user.id });
                    if (metricsClient && typeof metricsClient.increment === 'function') metricsClient.increment('feature.bypass.role', { feature: key, role });
                    return next();
                }
            }

            // 3) Evaluate feature flag (cached)
            const enabled = await evaluate(req);

            if (!enabled) {
                if (metricsClient && typeof metricsClient.increment === 'function') metricsClient.increment('feature.disabled', { feature: key });
                // Hide existence by returning 404 for disabled features (configurable)
                if (hide404) {
                    return res.status(404).json({ status: 'error', message: 'Not found', correlationId });
                }
                return res.status(403).json({ status: 'error', message: 'Feature disabled', correlationId });
            }

            // 4) Allowed: proceed
            if (metricsClient && typeof metricsClient.increment === 'function') metricsClient.increment('feature.enabled', { feature: key });
            return next();
        } catch (err) {
            // On unexpected errors, fail-open to avoid blocking critical flows, but log and emit metric
            logger.error('featureFlag middleware error', { err: err && err.message ? err.message : err, key, correlationId });
            if (metricsClient && typeof metricsClient.increment === 'function') metricsClient.increment('feature.error', { feature: key });
            return next();
        }
    };
};
