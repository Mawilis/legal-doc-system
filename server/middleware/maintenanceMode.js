/*
 * File: server/middleware/maintenanceMode.js
 * STATUS: PRODUCTION-READY | OPERATIONAL EXCELLENCE GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Provides a controlled "Air Gap" for the system during upgrades. 
 * Prevents data corruption during migrations by pausing all non-essential traffic.
 *
 * KEY FEATURES FOR FUTURE ENGINEERS:
 * 1. 503 Service Unavailable: Correct HTTP semantics for maintenance.
 * 2. Admin Bypass: Allows authorized staff to enter the system while locked.
 * 3. Retry-After Support: Helps load balancers and apps schedule reconnections.
 * 4. Path Whitelisting: Keeps monitoring (Health Checks) alive during downtime.
 * -----------------------------------------------------------------------------
 */

'use strict';

// 1. DYNAMIC CONFIGURATION
// Maintenance can be toggled via ENV or potentially a Redis flag for zero-restarts.
const isMaintenance = process.env.MAINTENANCE_MODE === 'true';

// 2. SAFETY EXEMPTIONS
// Paths that must ALWAYS be accessible (Health checks, Admin login).
const EXEMPT_PATHS = [
    '/api/v1/system/health',
    '/api/v1/system/status',
    '/api/v1/auth/admin-login'
];

/**
 * MAINTENANCE MODE MIDDLEWARE
 */
const maintenanceMode = async (req, res, next) => {
    try {
        // --- BYPASS LOGIC ---
        if (!isMaintenance) return next();

        if (EXEMPT_PATHS.some(path => req.originalUrl.startsWith(path))) {
            return next();
        }

        // --- ADMIN BYPASS LOGIC ---
        // Allows engineers to work on the system while it's "closed."
        const bypassKey = req.headers['x-maintenance-bypass'];
        if (bypassKey && bypassKey === process.env.MAINTENANCE_BYPASS_KEY) {
            return next();
        }

        // --- AUDIT LOGGING ---
        if (req.logAudit) {
            await req.logAudit('MAINTENANCE_BLOCK', {
                path: req.originalUrl,
                ip: req.ip,
                reason: 'System is in maintenance mode'
            });
        }

        // --- PROFESSIONAL RESPONSE ---
        // Set the 'Retry-After' header (Standard: 3600 seconds = 1 hour)
        res.setHeader('Retry-After', process.env.MAINTENANCE_RETRY_AFTER || '3600');

        return res.status(503).json({
            success: false,
            status: 'error',
            code: 'ERR_MAINTENANCE_MODE',
            message: 'Wilsy OS is currently undergoing scheduled performance upgrades.',
            meta: {
                estimatedCompletion: process.env.MAINTENANCE_ESTIMATED_END || 'Unknown',
                supportContact: 'ops@wilsyos.com',
                correlationId: req.correlationId
            }
        });
    } catch (err) {
        // If maintenance logic fails, we prioritize uptime and allow the request.
        console.error('MAINTENANCE_MIDDLEWARE_CRITICAL_FAILURE:', err);
        next();
    }
};

module.exports = maintenanceMode;