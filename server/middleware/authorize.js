/*
 * File: server/middleware/authorize.js
 * STATUS: PRODUCTION-READY | RBAC SECURITY GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * This middleware enforces Role-Based Access Control (RBAC). It ensures that 
 * even authenticated users can only access resources permitted for their role.
 *
 * KEY FEATURES FOR FUTURE ENGINEERS:
 * 1. Role Whitelisting: Define which roles are allowed on a per-route basis.
 * 2. Security Auditing: Logs unauthorized access attempts to the SecurityEvent model.
 * 3. Principle of Least Privilege: Defaults to 'Access Denied' unless explicitly allowed.
 * 4. Flexible Implementation: Can be used on single routes or entire router groups.
 * -----------------------------------------------------------------------------
 */

'use strict';

const SecurityEvent = require('../models/SecurityEvent');

/**
 * AUTHORIZATION MIDDLEWARE:
 * Restricts access to specific user roles.
 * @param {...String} roles - One or more roles allowed to access the route.
 */
const authorize = (...roles) => {
    return async (req, res, next) => {
        // 1. SAFETY CHECK: Ensure user was already authenticated by 'protect' middleware.
        if (!req.user) {
            return res.status(401).json({
                status: 'error',
                message: 'Authorization failed: User identity not found.'
            });
        }

        // 2. ROLE VALIDATION: Check if user's role is in the allowed whitelist.
        if (!roles.includes(req.user.role)) {

            // 3. FORENSIC LOGGING: Track the unauthorized attempt.
            // This is vital for detecting internal threats or account compromises.
            try {
                await SecurityEvent.create({
                    tenantId: req.user.tenantId,
                    eventType: 'UNAUTHORIZED_ACCESS_ATTEMPT',
                    severity: 'HIGH',
                    ipAddress: req.ip,
                    requestPath: req.originalUrl,
                    status: 'BLOCKED',
                    meta: {
                        userId: req.user._id,
                        userRole: req.user.role,
                        requiredRoles: roles,
                        reason: 'User role does not have permission for this resource.'
                    }
                });
            } catch (logErr) {
                console.error('AUTHORIZATION_LOGGING_ERR:', logErr);
            }

            // 4. DENY ACCESS
            return res.status(403).json({
                status: 'error',
                message: `Access Forbidden: Your role (${req.user.role}) does not have permission to perform this action.`
            });
        }

        // 5. SUCCESS: User has the correct role.
        next();
    };
};

/*
 * USAGE FOR ENGINEERS:
 * router.delete('/:id', protect, authorize('admin', 'lawyer'), deleteController);
 */

module.exports = { authorize };