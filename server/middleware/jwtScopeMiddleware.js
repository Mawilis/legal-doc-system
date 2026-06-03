/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SCOPE GATEKEEPER [V72.1.0-FOUNDER-BYPASS]                                                                                   ║
 * ║ [JWT CLAIM VALIDATION | 403 FRACTURE PREVENTION | FOUNDER ABSOLUTE OVERRIDE | SOVEREIGN MESH ENFORCEMENT]                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 72.1.0-FOUNDER-BYPASS | PRODUCTION READY | TRILLION DOLLAR SPEC                                                               ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/jwtScopeMiddleware.js                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated scope claim validation to prevent 403 fractures.                                     ║
 * ║ • AI Engineering (DeepSeek) – ENHANCED: Added telemetry logging, configurable scope maps, full JSDoc, and forensic audit trail.        ║
 * ║ • AI Engineering (DeepSeek) – FINAL: Added FOUNDER role bypass – absolute override for sovereign founder. [2026-05-29]                 ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import jwt from 'jsonwebtoken';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

// ============================================================================
// 🔥 SCOPE REGISTRY – Defines required scopes for each sovereign resource
// ============================================================================

/**
 * @typedef {Object} ScopeDefinition
 * @property {string[]} read - Scopes required for read operations.
 * @property {string[]} write - Scopes required for write operations.
 * @property {string[]} admin - Scopes required for admin operations.
 */

/**
 * @constant {Object<string, ScopeDefinition>} REQUIRED_SCOPES
 * @description Maps sovereign modules to the required JWT scopes for different operation types.
 *
 * @real-world
 *   Used by `validateScopes` to enforce fine‑grained access control. Scopes are
 *   embedded in the JWT during authentication and must match the endpoint requirements.
 *
 * @example
 * // For compliance read access, token must include 'compliance.read'
 * validateScopes(REQUIRED_SCOPES.compliance.read) // => ['compliance.read']
 */
export const REQUIRED_SCOPES = {
  compliance: {
    read: ['compliance.read', 'compliance.audit'],
    write: ['compliance.write', 'compliance.admin'],
    admin: ['compliance.admin']
  },
  revenue: {
    read: ['revenue.read', 'revenue.ledger'],
    write: ['revenue.write', 'revenue.admin'],
    admin: ['revenue.admin']
  },
  telemetry: {
    write: ['telemetry.write']
  },
  artifact: {
    generate: ['artifact.generate', 'artifact.admin']
  },
  seizure: {
    execute: ['seizure.execute', 'sovereign.admin']
  }
};

// ============================================================================
// 🔥 HELPER: Extract JWT from Authorization header
// ============================================================================

/**
 * Extracts the JWT token from the Authorization header.
 * @param {Object} req - Express request object.
 * @returns {string|null} The token, or null if missing/invalid format.
 * @private
 */
function extractToken(req) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) return null;
  return authHeader.split(' ')[1].replace(/['"]+/g, '');
}

// ============================================================================
// 🔥 CORE MIDDLEWARE – Scope Validation with FOUNDER Override
// ============================================================================

/**
 * Middleware factory that validates JWT scope claims against required scopes.
 * **FOUNDER role bypasses all scope checks** – absolute override.
 *
 * @param {string[]} requiredScopes - Array of scope strings that must be present in the JWT.
 * @returns {Function} Express middleware function (req, res, next).
 *
 * @real-world
 *   Applied to protected routes to ensure the authenticated user has the necessary
 *   permissions. Prevents 403 errors by rejecting the request early with a clear error.
 *   The FOUNDER role is the ultimate sovereign – no scope restrictions apply.
 *
 * @forensic
 *   - Logs every scope validation failure to the Sovereign Mesh via `broadcastTelemetry`.
 *   - Includes user ID (subject), required scopes, and missing scopes in the audit trail.
 *   - Returns standardised 401/403 responses with forensic error codes.
 *   - Founder bypass is logged as a telemetry event for audit.
 *
 * @example
 * // Protect a compliance read endpoint
 * app.get('/compliance/report', validateScopes(REQUIRED_SCOPES.compliance.read), getReport);
 *
 * // Multiple scopes (user must have ALL – unless role === 'FOUNDER')
 * app.post('/revenue/ledger', validateScopes(['revenue.write', 'revenue.admin']), updateLedger);
 */
export function validateScopes(requiredScopes) {
  if (!Array.isArray(requiredScopes) || requiredScopes.length === 0) {
    throw new Error('validateScopes requires a non‑empty array of scope strings');
  }

  return async (req, res, next) => {
    const token = extractToken(req);
    if (!token) {
      // No token – 401, not 403
      return res.status(401).json({
        success: false,
        error: 'UNAUTHORIZED_VOID',
        message: 'No authentication token provided.'
      });
    }

    let decoded;
    try {
      // Decode without verification (we assume authentication middleware already verified)
      decoded = jwt.decode(token);
      if (!decoded || typeof decoded !== 'object') {
        throw new Error('Invalid token structure');
      }
    } catch (err) {
      return res.status(401).json({
        success: false,
        error: 'TOKEN_INTEGRITY_COMPROMISED',
        message: 'Malformed token.'
      });
    }

    const userId = decoded.sub || decoded.id || decoded.userId || 'UNKNOWN';
    const userRole = decoded.role || decoded.roles?.[0] || 'USER';

    // 🔥 SOVEREIGN OVERRIDE: Founder bypasses all scope restrictions
    if (userRole === 'FOUNDER') {
      // Log founder bypass for audit (optional, non‑blocking)
      console.log(`[SCOPE_GATEKEEPER] 👑 FOUNDER bypass for user ${userId} on ${req.method} ${req.originalUrl}`);
      try {
        await broadcastTelemetry(
          decoded.tenantId || 'GLOBAL_ROOT',
          'SCOPE_GATEKEEPER',
          'FOUNDER_BYPASS',
          'jwtScopeMiddleware',
          {
            userId,
            role: userRole,
            path: req.originalUrl,
            method: req.method,
            timestamp: new Date().toISOString()
          }
        );
      } catch (teleErr) {
        console.warn('[SCOPE_GATEKEEPER] Telemetry broadcast failed for founder bypass:', teleErr.message);
      }
      // Attach scope info (even though bypassed) for downstream transparency
      req.userScopes = decoded.scopes || decoded.permissions || [];
      req.requiredScopes = requiredScopes;
      return next();
    }

    // Non‑founder: enforce scope checks
    const userScopes = decoded.scopes || decoded.permissions || [];
    const missingScopes = requiredScopes.filter(scope => !userScopes.includes(scope));
    const hasAllScopes = missingScopes.length === 0;

    if (!hasAllScopes) {
      // 🔍 Forensic audit: log the failure
      console.error(`[AUDIT-FAILURE] Scope mismatch for user ${userId}. Required: ${requiredScopes.join(', ')}. Missing: ${missingScopes.join(', ')}`);

      // Broadcast telemetry for boardroom alerting (if helper exists)
      try {
        await broadcastTelemetry(
          decoded.tenantId || 'GLOBAL_ROOT',
          'SCOPE_GATEKEEPER',
          'SCOPE_VIOLATION',
          'jwtScopeMiddleware',
          {
            userId,
            role: userRole,
            requiredScopes,
            missingScopes,
            path: req.originalUrl,
            method: req.method,
            timestamp: new Date().toISOString()
          }
        );
      } catch (teleErr) {
        console.warn('[SCOPE_GATEKEEPER] Telemetry broadcast failed:', teleErr.message);
      }

      return res.status(403).json({
        success: false,
        error: 'INSUFFICIENT_SOVEREIGN_RIGHTS',
        message: 'Missing required scopes for this operation.',
        required: requiredScopes,
        missing: missingScopes
      });
    }

    // Attach scope info to request for downstream use (optional)
    req.userScopes = userScopes;
    req.requiredScopes = requiredScopes;

    next();
  };
}

// ============================================================================
// 🔥 CONVENIENCE MIDDLEWARES (pre‑configured for common modules)
// ============================================================================

/**
 * Pre‑configured middleware for compliance read operations.
 * @middleware requireComplianceRead
 */
export const requireComplianceRead = validateScopes(REQUIRED_SCOPES.compliance.read);

/**
 * Pre‑configured middleware for compliance write operations.
 * @middleware requireComplianceWrite
 */
export const requireComplianceWrite = validateScopes(REQUIRED_SCOPES.compliance.write);

/**
 * Pre‑configured middleware for compliance admin operations.
 * @middleware requireComplianceAdmin
 */
export const requireComplianceAdmin = validateScopes(REQUIRED_SCOPES.compliance.admin);

/**
 * Pre‑configured middleware for revenue read operations.
 * @middleware requireRevenueRead
 */
export const requireRevenueRead = validateScopes(REQUIRED_SCOPES.revenue.read);

/**
 * Pre‑configured middleware for revenue write operations.
 * @middleware requireRevenueWrite
 */
export const requireRevenueWrite = validateScopes(REQUIRED_SCOPES.revenue.write);

/**
 * Pre‑configured middleware for telemetry write operations.
 * @middleware requireTelemetryWrite
 */
export const requireTelemetryWrite = validateScopes(REQUIRED_SCOPES.telemetry.write);

/**
 * Pre‑configured middleware for artifact generation.
 * @middleware requireArtifactGenerate
 */
export const requireArtifactGenerate = validateScopes(REQUIRED_SCOPES.artifact.generate);

/**
 * Pre‑configured middleware for seizure execution (sovereign admin level).
 * @middleware requireSeizureExecute
 */
export const requireSeizureExecute = validateScopes(REQUIRED_SCOPES.seizure.execute);

// ============================================================================
// 🔥 UTILITY: Check scopes programmatically (for service‑level enforcement)
// ============================================================================

/**
 * Programmatically checks if a user's scope set satisfies required scopes.
 * Useful for service‑level authorisation where middleware is not applicable.
 * Also respects FOUNDER role (returns true for any required scopes).
 *
 * @param {string[]} userScopes - Array of scopes the user possesses.
 * @param {string[]} requiredScopes - Array of scopes required for the operation.
 * @param {string} [userRole] - Optional user role; if 'FOUNDER', bypasses check.
 * @returns {boolean} True if all required scopes are present or user is FOUNDER.
 *
 * @example
 * if (!hasRequiredScopes(req.user.scopes, ['revenue.admin'], req.user.role)) {
 *   throw new Error('Insufficient rights');
 * }
 */
export function hasRequiredScopes(userScopes, requiredScopes, userRole = 'USER') {
  if (userRole === 'FOUNDER') return true;
  if (!Array.isArray(userScopes) || !Array.isArray(requiredScopes)) return false;
  return requiredScopes.every(scope => userScopes.includes(scope));
}

// ============================================================================
// 📤 EXPORTS
// ============================================================================

export default {
  validateScopes,
  REQUIRED_SCOPES,
  requireComplianceRead,
  requireComplianceWrite,
  requireComplianceAdmin,
  requireRevenueRead,
  requireRevenueWrite,
  requireTelemetryWrite,
  requireArtifactGenerate,
  requireSeizureExecute,
  hasRequiredScopes
};
