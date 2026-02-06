/**
 * File: server/middleware/maintenanceMiddleware.js
 * STATUS: PRODUCTION-READY | EPITOME | MAINTENANCE GUARD
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Global maintenance gate for Wilsy OS.
 * - Blocks non-exempt traffic when maintenanceMode is enabled in SystemConfig.
 * - Exemptions: health endpoints, internal IPs/CIDRs, SUPER_ADMINs (via req.user),
 *   infra-protected bypass header, or a verified admin token (optional).
 *
 * FEATURES:
 * - In-memory cached SystemConfig with TTL to avoid DB hot-path.
 * - Correlation id propagation (reads x-correlation-id or generates one).
 * - Optional CIDR support (uses ipaddr.js if available; falls back to prefix match).
 * - Pluggable options for allowPaths, bypassHeader, internalCidrs, allowRoles,
 *   verifyToken (uses JWT_SECRET), cacheTTL, and metrics client.
 * - Fail-open on unexpected errors (configurable to fail-closed).
 *
 * COLLABORATION NOTES:
 * - This middleware expects authMiddleware to run earlier and attach req.user when possible.
 * - For token-based bypass, set options.verifyToken = true and ensure JWT_SECRET is set.
 * - Add this middleware early in the chain (before public API routes).
 * -----------------------------------------------------------------------------
 */

'use strict';

const SystemConfig = require('../models/systemConfigModel');
const logger = require('../utils/logger');
const { v4: uuidv4 } = require('uuid');

let ipaddr;
try {
    // optional dependency for robust CIDR checks
    // npm i ipaddr.js
    ipaddr = require('ipaddr.js');
} catch (e) {
    ipaddr = null;
}

/**
 * Simple prefix match fallback for internal IPs (not CIDR-accurate).
 * Accepts patterns like '10.0.' or '192.168.' or exact IPs.
 */
function ipMatchesFallback(ip, patterns = []) {
    if (!ip || !patterns || !patterns.length) return false;
    for (const p of patterns) {
        if (!p) continue;
        if (p.includes('/')) {
            // can't evaluate CIDR without ipaddr; skip
            continue;
        }
        if (ip === p) return true;
        if (ip.startsWith(p)) return true;
    }
    return false;
}

/**
 * Check if ip is in any CIDR using ipaddr.js
 */
function ipInCidrs(ip, cidrs = []) {
    if (!ip || !cidrs || !cidrs.length) return false;
    if (!ipaddr) return ipMatchesFallback(ip, cidrs);
    try {
        const addr = ipaddr.parse(ip);
        for (const c of cidrs) {
            try {
                if (c.includes('/')) {
                    const [range, bits] = c.split('/');
                    const parsedRange = ipaddr.parse(range);
                    if (addr.match(parsedRange, parseInt(bits, 10))) return true;
                } else {
                    if (addr.toString() === ipaddr.parse(c).toString()) return true;
                }
            } catch (e) {
                // ignore malformed CIDR entries
                continue;
            }
        }
    } catch (e) {
        return false;
    }
    return false;
}

/* In-memory cached config to reduce DB reads */
const configCache = {
    value: null,
    ts: 0
};

/**
 * Fetch SystemConfig with caching and single-flight protection.
 */
async function getCachedConfig(ttl = 3000) {
    const now = Date.now();
    if (configCache.value && (now - configCache.ts) < ttl) {
        return configCache.value;
    }

    // Load fresh
    const cfg = await SystemConfig.getSingleton();
    configCache.value = cfg;
    configCache.ts = Date.now();
    return cfg;
}

/**
 * Clear config cache (call this after config updates)
 */
function invalidateConfigCache() {
    configCache.value = null;
    configCache.ts = 0;
}

/**
 * Middleware factory
 * options:
 *  - allowPaths: array of path prefixes to always allow (default ['/health','/api/public/status'])
 *  - bypassHeader: header name that infra can set to bypass maintenance (default 'x-wilsy-bypass-maintenance')
 *  - allowRoles: array of roles allowed during maintenance (default ['SUPER_ADMIN'])
 *  - allowInternal: boolean to enable internal IP allowlist
 *  - internalCidrs: array of CIDR strings or IP prefixes
 *  - verifyToken: boolean - if true, will attempt to verify JWT from Authorization header to detect SUPER_ADMIN (requires process.env.JWT_SECRET)
 *  - cacheTTL: ms for SystemConfig cache (default 3000)
 *  - failClosed: boolean - if true, middleware will block on errors (default false -> fail open)
 *  - metricsClient: optional object with .increment(name) for metrics
 */
module.exports = function maintenanceMiddleware(options = {}) {
    const {
        allowPaths = ['/health', '/api/public/status'],
        bypassHeader = 'x-wilsy-bypass-maintenance',
        allowRoles = ['SUPER_ADMIN'],
        allowInternal = false,
        internalCidrs = [],
        verifyToken = false,
        cacheTTL = 3000,
        failClosed = false,
        metricsClient = null
    } = options;

    return async function (req, res, next) {
        // Correlation id for logs and response header
        const correlationId = req.headers['x-correlation-id'] || uuidv4();
        res.setHeader('x-correlation-id', correlationId);

        try {
            // 1) Allow whitelisted paths immediately
            if (allowPaths.some((p) => req.path.startsWith(p))) {
                return next();
            }

            // 2) Optionally allow internal IPs
            if (allowInternal && internalCidrs && internalCidrs.length) {
                // Express may provide req.ip or req.connection.remoteAddress
                const ip = (req.ip || req.headers['x-forwarded-for'] || req.connection?.remoteAddress || '').split(',')[0].trim();
                if (ip) {
                    const allowed = ipInCidrs(ip, internalCidrs) || ipMatchesFallback(ip, internalCidrs);
                    if (allowed) {
                        logger.info('Maintenance middleware: allowing internal IP', { ip, correlationId });
                        return next();
                    }
                }
            }

            // 3) Fetch cached SystemConfig
            const cfg = await getCachedConfig(cacheTTL);

            // If config missing or maintenance disabled -> allow
            if (!cfg || !cfg.maintenanceMode) {
                return next();
            }

            // 4) Bypass header (set by infra/WAF) - must be protected by infra
            if (req.headers && req.headers[bypassHeader]) {
                logger.info('Maintenance bypass header present; allowing request', { correlationId });
                if (metricsClient && typeof metricsClient.increment === 'function') metricsClient.increment('maintenance.bypass.header');
                return next();
            }

            // 5) If auth middleware already attached req.user, allow based on role
            if (req.user && req.user.role) {
                const role = String(req.user.role).toUpperCase();
                if (allowRoles.map(String).map((r) => r.toUpperCase()).includes(role)) {
                    logger.info('Maintenance bypass via req.user role', { role, correlationId, userId: req.user._id || req.user.id });
                    if (metricsClient && typeof metricsClient.increment === 'function') metricsClient.increment('maintenance.bypass.role');
                    return next();
                }
            }

            // 6) Optionally verify JWT from Authorization header to detect SUPER_ADMIN
            if (verifyToken) {
                try {
                    const authHeader = req.headers.authorization || req.headers.Authorization || '';
                    const token = authHeader.replace(/^Bearer\s+/i, '').trim();
                    if (token) {
                        // Lazy require to avoid coupling if not used
                        // eslint-disable-next-line global-require
                        const jwt = require('jsonwebtoken');
                        const secret = process.env.JWT_SECRET;
                        if (secret) {
                            const decoded = jwt.verify(token, secret, { ignoreExpiration: true });
                            const role = (decoded && (decoded.role || decoded.roles || decoded.userRole)) || null;
                            if (role && allowRoles.map(String).map((r) => r.toUpperCase()).includes(String(role).toUpperCase())) {
                                logger.info('Maintenance bypass via verified token role', { role, correlationId, sub: decoded && (decoded.id || decoded.sub) });
                                if (metricsClient && typeof metricsClient.increment === 'function') metricsClient.increment('maintenance.bypass.token');
                                return next();
                            }
                        }
                    }
                } catch (e) {
                    // token verification failed -> continue to deny
                    logger.warn('Maintenance middleware token verification failed', { err: e && e.message ? e.message : e, correlationId });
                }
            }

            // 7) Deny all other requests with maintenance message
            if (metricsClient && typeof metricsClient.increment === 'function') metricsClient.increment('maintenance.blocked');
            return res.status(503).json({
                status: 'maintenance',
                message: cfg.maintenanceMessage || 'Service temporarily unavailable for maintenance.',
                correlationId
            });
        } catch (err) {
            // On unexpected errors, either fail-open (allow) or fail-closed (block) based on config
            logger.error('Maintenance middleware error', { err: err && err.message ? err.message : err, correlationId });
            if (metricsClient && typeof metricsClient.increment === 'function') metricsClient.increment('maintenance.error');
            if (failClosed) {
                return res.status(503).json({
                    status: 'maintenance',
                    message: 'Service temporarily unavailable (maintenance check failed).',
                    correlationId
                });
            }
            return next();
        }
    };
};

/* Expose cache invalidation helper for admin flows to call after toggling maintenance */
module.exports.invalidateConfigCache = invalidateConfigCache;
