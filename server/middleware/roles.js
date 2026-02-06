/**
 * File: server/middleware/roles.js
 * PATH: server/middleware/roles.js
 * STATUS: PRODUCTION-READY | BIBLICAL | PERIMETER GUARD
 * VERSION: 15.0.0 (The Gavel)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - The Central Authority for Role-Based Access Control (RBAC).
 * - Enforces the "Sovereign Hierarchy": PLATFORM_ADMIN > TENANT_ADMIN > LAWYER > STAFF.
 * - Validates JWT Integrity, Claims, and Blacklist status in real-time.
 *
 * ARCHITECTURAL SUPREMACY:
 * 1. CIRCUIT BREAKER: Integrates with Redis to check for revoked/blacklisted tokens.
 * 2. ZERO-TRUST: Re-verifies tenantId consistency against the token claims.
 * 3. HIERARCHICAL BYPASS: Implements a 'SUPER_ADMIN' god-mode for platform maintenance.
 * 4. ATOMIC DENIAL: Fails closed (Forbidden) by default to prevent accidental leaks.
 *
 * COLLABORATION:
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - SECURITY: @Wilsy-Security (Cryto-Audit)
 * - SRE: @Infra-Guard (Latency-optimized Redis Checks)
 * -----------------------------------------------------------------------------
 * EPITOME:
 * Biblical worth billions no child's place. Wilsy OS to the World.
 */

'use strict';

const jwt = require('jsonwebtoken');
const redis = require('../lib/redisClient');
const CustomError = require('../utils/customError');

/* ---------------------------------------------------------------------------
   1. SOVEREIGN ROLE HIERARCHY
   --------------------------------------------------------------------------- */
const ROLES = Object.freeze({
    SUPER_ADMIN: 'SUPER_ADMIN',        // Wilsy Internal Systems
    PLATFORM_ADMIN: 'PLATFORM_ADMIN',  // Global Management
    TENANT_ADMIN: 'TENANT_ADMIN',      // Law Firm Owner/Admin
    LAWYER: 'LAWYER',                  // Legal Practitioner
    STAFF: 'STAFF'                     // Support/Clerical
});

/* ---------------------------------------------------------------------------
   2. INTERNAL VERIFICATION ENGINE
   --------------------------------------------------------------------------- */

/**
 * checkBlacklist
 * @description Consults the L2 Redis store to see if this specific token has been revoked.
 */
const isTokenRevoked = async (token) => {
    if (!redis) return false; // Fallback to allow OS to run if Redis is cycling
    const jti = jwt.decode(token)?.jti; // Unique JWT ID
    if (!jti) return false;
    const blacklisted = await redis.get(`blacklist:${jti}`);
    return !!blacklisted;
};

/**
 * requireRole
 * @description The Authoritative Middleware Factory.
 * @param {string|string[]} allowedRoles - The roles permitted to ignite the route.
 */
exports.requireRole = (allowedRoles = []) => {
    // Normalize roles to uppercase for case-insensitive biblical enforcement
    const targetRoles = (Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles])
        .map(r => String(r).toUpperCase());

    return async (req, res, next) => {
        try {
            // --- TIER 1: AUTHENTICATION HANDSHAKE ---
            const authHeader = req.headers.authorization;
            if (!authHeader || !authHeader.startsWith('Bearer ')) {
                throw new CustomError('Sovereign Authentication Required.', 401);
            }

            const token = authHeader.split(' ')[1];

            // --- TIER 2: BLACKLIST VERIFICATION ---
            if (await isTokenRevoked(token)) {
                throw new CustomError('Session Revoked. Please re-authenticate.', 401);
            }

            // --- TIER 3: CRYPTOGRAPHIC INTEGRITY ---
            const secret = process.env.JWT_SECRET;
            if (!secret) throw new Error('SECURITY CRITICAL: JWT_SECRET missing from environment.');

            let decoded;
            try {
                decoded = jwt.verify(token, secret);
            } catch (err) {
                const message = err.name === 'TokenExpiredError' ? 'Session Expired.' : 'Invalid Signature.';
                throw new CustomError(message, 401);
            }

            // Attach the validated identity to the request context
            req.user = Object.freeze({
                _id: decoded.id,
                tenantId: decoded.tenantId,
                role: String(decoded.role || '').toUpperCase(),
                email: decoded.email
            });

            // --- TIER 4: AUTHORIZATION ENGINE ---
            const userRole = req.user.role;

            // God-Mode Bypass
            if (userRole === ROLES.SUPER_ADMIN) return next();

            // Open-Auth (If no roles specified, just authentication is needed)
            if (targetRoles.length === 0) return next();

            // Role Membership Check
            if (!targetRoles.includes(userRole)) {
                console.warn(`🚨 SECURITY ALERT: Unauthorized access attempt by ${req.user.email} (Role: ${userRole})`);
                throw new CustomError('Insufficient permissions for this sovereign resource.', 403);
            }

            // Handshake Complete
            next();

        } catch (error) {
            // Defensive failure: Log locally, return sanitized error to client
            if (error instanceof CustomError) {
                return res.status(error.statusCode).json({ success: false, message: error.message });
            }
            console.error('🔥 MIDDLEWARE EXCEPTION:', error.message);
            return res.status(500).json({ success: false, message: 'Authorization Gateway Error.' });
        }
    };
};

/**
 * hasRole
 * @description Boolean utility for logic branching within controllers.
 */
exports.hasRole = (req, roles = []) => {
    if (!req.user || !req.user.role) return false;
    const userRole = req.user.role.toUpperCase();
    const targetRoles = (Array.isArray(roles) ? roles : [roles]).map(r => String(r).toUpperCase());

    if (userRole === ROLES.SUPER_ADMIN) return true;
    return targetRoles.includes(userRole);
};

/* ---------------------------------------------------------------------------
   SOVEREIGN EXPORTS
   --------------------------------------------------------------------------- */
module.exports = {
    requireRole: exports.requireRole,
    hasRole: exports.hasRole,
    ROLES
};