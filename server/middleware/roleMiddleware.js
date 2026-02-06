/*
 * File: server/middleware/roleMiddleware.js
 * STATUS: PRODUCTION-READY | HIERARCHICAL SECURITY GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Implements a "Clearance Level" system. Instead of checking for specific roles, 
 * it checks if a user's rank meets the minimum requirement for a resource.
 *
 * HIERARCHY MAP:
 * [0] user      - Basic client access
 * [1] associate - Legal clerks/staff
 * [2] finance   - Billing and Trust account access
 * [3] sheriff   - Field operations and service of process
 * [4] admin     - Firm managers
 * [!] super_admin - Global Platform Operators (God Mode)
 * -----------------------------------------------------------------------------
 */

'use strict';

// --- CONFIGURATION ---
const ROLE_HIERARCHY = ['user', 'associate', 'finance', 'sheriff', 'admin'];

/**
 * MASTER AUTHORIZER
 * @param {...String} requiredRoles - The minimum roles allowed.
 */
const allowRoles = (...requiredRoles) => {
    return async (req, res, next) => {
        // 1. IDENTITY CHECK
        if (!req.user || !req.user.role) {
            return res.status(401).json({
                success: false,
                code: 'ERR_UNAUTHENTICATED',
                message: 'Identity resolution failed.'
            });
        }

        const userRole = req.user.role.toLowerCase();

        // 2. SUPER_ADMIN BYPASS
        // Global operators bypass hierarchy logic for system maintenance.
        if (userRole === 'super_admin') return next();

        // 3. HIERARCHY CALCULATION
        const userRank = ROLE_HIERARCHY.indexOf(userRole);

        // Find the lowest rank among the required roles
        const requiredRanks = requiredRoles.map(r => ROLE_HIERARCHY.indexOf(r.toLowerCase()));
        const minRequiredRank = Math.min(...requiredRanks);

        // 4. AUTHORIZATION DECISION
        // User passes if their rank is equal to or higher than the minimum required rank
        const isAuthorized = userRank >= minRequiredRank && userRank !== -1;

        if (!isAuthorized) {
            // FORENSIC AUDIT: Log the attempted breach
            if (req.logAudit) {
                await req.logAudit('RBAC_INSUFFICIENT_CLEARANCE', {
                    userRole,
                    requiredRoles,
                    path: req.originalUrl
                });
            }

            return res.status(403).json({
                success: false,
                code: 'ERR_INSUFFICIENT_CLEARANCE',
                message: 'Access Forbidden: Your clearance level is insufficient for this resource.',
                meta: {
                    currentLevel: userRole,
                    requiredLevels: requiredRoles
                }
            });
        }

        next();
    };
};

// --- PRE-FABRICATED ENTERPRISE GATES ---
// Use these in your routes for maximum code cleanliness.

const adminOnly = allowRoles('admin');
const sheriffOnly = allowRoles('sheriff'); // Inherits admin
const financeOnly = allowRoles('finance'); // Inherits sheriff, admin
const staffOnly = allowRoles('associate'); // Inherits finance, sheriff, admin

module.exports = {
    allowRoles,
    adminOnly,
    sheriffOnly,
    financeOnly,
    staffOnly
};